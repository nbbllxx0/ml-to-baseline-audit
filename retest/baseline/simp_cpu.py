"""CPU SIMP loops (numpy/scipy), pre-registered in plan/BASELINE_PREREG.md §3.

  solver="superlu"  : top88-faithful port - filter applied inside the OC bisection, scipy spsolve (SuperLU).
                      Reference for "a typical Python port"; not the strong baseline.
  solver="pardiso"  : strong CPU baseline - volume in the bisection via precomputed weights (identical in
                      exact arithmetic), MKL PARDISO for SPD matrices (mtype=2) with the symbolic analysis
                      done once and numeric factorization + solve (phase 23) every iteration.
Both use the same formulation (fem2d.py), so designs agree up to floating-point differences.
"""
import time

import numpy as np
import scipy.sparse as sp

from .fem2d import element_dofs, element_stiffness, filter_matrix


class Assembler:
    """K_ff = S @ E as one sparse mat-vec (S precomputed from KE and the fixed free-DOF pattern)."""

    def __init__(self, prob, KE, upper_only):
        edof = element_dofs(prob.nelx, prob.nely)
        nel = prob.nel
        iK = np.repeat(edof, 8, axis=1).ravel()
        jK = np.tile(edof, (1, 8)).ravel()
        el = np.repeat(np.arange(nel), 64)
        kv = np.tile(KE.ravel(), nel)
        free = np.ones(prob.ndof, dtype=bool)
        free[prob.fixed] = False
        self.free_idx = np.flatnonzero(free)
        n = self.free_idx.size
        remap = -np.ones(prob.ndof, dtype=np.int64)
        remap[self.free_idx] = np.arange(n)
        keep = free[iK] & free[jK]
        ri, rj, el, kv = remap[iK[keep]], remap[jK[keep]], el[keep], kv[keep]
        if upper_only:
            up = rj >= ri
            ri, rj, el, kv = ri[up], rj[up], el[up], kv[up]
        key = ri * n + rj
        uniq, pos = np.unique(key, return_inverse=True)
        rows, cols = uniq // n, uniq % n
        self.indptr = np.zeros(n + 1, dtype=np.int64)
        np.add.at(self.indptr, rows + 1, 1)
        self.indptr = np.cumsum(self.indptr)
        self.indices = cols
        self.n, self.nnz = n, uniq.size
        self.S = sp.csr_matrix((kv, (pos, el)), shape=(self.nnz, nel))

    def assemble(self, E):
        return sp.csr_matrix((self.S @ E, self.indices, self.indptr), shape=(self.n, self.n))


def run(prob, solver="pardiso", iters=150, log=None, return_x=False):
    """Run `iters` SIMP iterations; return (record dict, final xPhys, final u)."""
    t_setup = time.perf_counter()
    KE = element_stiffness(prob.nu)
    edof = element_dofs(prob.nelx, prob.nely)
    H, Hs = filter_matrix(prob.nelx, prob.nely, prob.rmin)
    asm = Assembler(prob, KE, upper_only=(solver == "pardiso"))
    f_free = prob.force[asm.free_idx]
    dv = H @ (1.0 / Hs)                       # filtered dv; also the volume weights of xnew
    nel, vtarget = prob.nel, prob.volfrac * prob.nel
    x = np.full(nel, prob.volfrac)
    xPhys = x.copy()
    u = np.zeros(prob.ndof)
    if solver == "pardiso":
        from pypardiso import PyPardisoSolver
        ps = PyPardisoSolver(mtype=2)
        K0 = asm.assemble(np.ones(nel))
        ps._check_A(K0)
        ps.set_phase(11)
        ps._call_pardiso(K0, np.zeros(asm.n))
    else:
        from scipy.sparse.linalg import spsolve
    t_setup = time.perf_counter() - t_setup

    rec = {k: [] for k in ("c", "vol", "change", "t_iter", "t_solve", "t_assemble", "true_res")}
    for it in range(iters):
        t0 = time.perf_counter()
        E = prob.Emin + xPhys ** prob.penal * (prob.E0 - prob.Emin)
        K = asm.assemble(E)
        t1 = time.perf_counter()
        if solver == "pardiso":
            ps.set_phase(23)
            uf = ps._call_pardiso(K, f_free)
        else:
            uf = spsolve(K, f_free)
        t2 = time.perf_counter()
        u[asm.free_idx] = uf
        Ue = u[edof]
        ce = np.einsum("ij,jk,ik->i", Ue, KE, Ue)
        c = float(E @ ce)
        dc = -prob.penal * (prob.E0 - prob.Emin) * xPhys ** (prob.penal - 1) * ce
        # Clamp at 0: a rounding-level positive sensitivity would make sqrt(-dc/dv/lmid) NaN (OpenTO problem 1974,
        # 256²). A no-op whenever all sensitivities are <= 0 (2026-09-25 fix).
        dc = np.minimum(H @ (dc / Hs), 0.0)
        l1, l2, move = 0.0, 1e9, 0.2
        while (l2 - l1) / (l1 + l2) > 1e-3:
            lmid = 0.5 * (l2 + l1)
            xnew = np.maximum(0.0, np.maximum(x - move, np.minimum(1.0, np.minimum(x + move, x * np.sqrt(-dc / dv / lmid)))))
            if solver == "superlu":
                xPhys_try = (H @ xnew) / Hs
                vol = xPhys_try.sum()
            else:
                vol = dv @ xnew
            if vol > vtarget:
                l1 = lmid
            else:
                l2 = lmid
        xPhys_new = xPhys_try if solver == "superlu" else (H @ xnew) / Hs
        change = float(np.abs(xnew - x).max())
        x, xPhys = xnew, xPhys_new
        t3 = time.perf_counter()
        if solver == "pardiso":
            # true residual of the accepted solve (W20 admissibility principle), outside the timed region
            res = np.linalg.norm(f_free - (K @ uf + K.T @ uf - K.diagonal() * uf)) / np.linalg.norm(f_free)
        else:
            res = np.linalg.norm(f_free - K @ uf) / np.linalg.norm(f_free)
        rec["c"].append(c)
        rec["vol"].append(float(xPhys.mean()))
        rec["change"].append(change)
        rec["t_iter"].append(t3 - t0)
        rec["t_solve"].append(t2 - t1)
        rec["t_assemble"].append(t1 - t0)
        rec["true_res"].append(float(res))
        if log:
            log(it, c, change, t3 - t0)
    rec["t_setup"] = t_setup
    rec["t_total"] = float(np.sum(rec["t_iter"]))
    if return_x:
        return rec, xPhys, u, x
    return rec, xPhys, u
