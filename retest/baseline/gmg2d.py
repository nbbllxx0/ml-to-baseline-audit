"""Matrix-free Galerkin geometric multigrid + PCG for 2D SIMP (torch, float64, GPU).

Pre-registered in plan/BASELINE_PREREG.md §3 (S-GPU).
  * fine operator: gather u_e -> E_e * KE u_e -> scatter-add
  * coarse operators: element-local Galerkin  K_c = sum_k Pk~^T K_child Pk~, where Pk is the bilinear
    interpolation from a parent element's 8 DOFs to child k's 8 DOFs and Pk~ masks fixed DOFs on both
    sides. This equals the global product P~^T K P~ (checked in tests/run_tests.py).
  * smoother: damped Jacobi; coarsest level: dense Cholesky
  * PCG accepts a solve only when the recomputed true residual ||f - K u|| / ||f|| <= true_tol.
"""
import numpy as np
import torch

from .fem2d import element_dofs


def child_interpolation():
    """(4, 8, 8) array: P[k] maps parent-element DOFs to child-k DOFs, k = cy*2 + cx."""
    corners = [(0, 0), (1, 0), (1, 1), (0, 1)]  # BL, BR, TR, TL

    def shape(xi, eta):
        return [(1 - xi) * (1 - eta), xi * (1 - eta), xi * eta, (1 - xi) * eta]

    mats = []
    for cy in (0, 1):
        for cx in (0, 1):
            Nk = np.array([shape((cx + a) / 2.0, (cy + b) / 2.0) for (a, b) in corners])
            mats.append(np.kron(Nk, np.eye(2)))
    return np.stack(mats)


class Level:
    def __init__(self, nelx, nely, mask, device, dtype):
        self.nelx, self.nely = nelx, nely
        self.ndof = 2 * (nelx + 1) * (nely + 1)
        self.edof = torch.as_tensor(element_dofs(nelx, nely), device=device)
        self.edof_flat = self.edof.reshape(-1)
        self.mask = mask                      # (ndof,) 1 = free, 0 = fixed
        self.Ke = None                        # (nel, 8, 8), coarse levels only
        self.diag = None


class GMGSolver:
    def __init__(self, prob, KE, device="cuda", dtype=torch.float64,
                 omega=0.6, nu_pre=2, nu_post=2, coarsest_min=8, use_graphs=True):
        self.dev, self.dt = device, dtype
        # CUDA graphs remove kernel-launch overhead of the V-cycle and operator apply. Same arithmetic;
        # checked against the non-graph path in tests/run_tests.py.
        self.use_graphs = use_graphs and device == "cuda"
        self.g_prec = self.g_apply = None
        self.omega, self.nu_pre, self.nu_post = omega, nu_pre, nu_post
        self.KE = torch.as_tensor(KE, device=device, dtype=dtype)
        m0 = torch.ones(prob.ndof, device=device, dtype=dtype)
        m0[torch.as_tensor(prob.fixed, device=device)] = 0.0
        self.levels = [Level(prob.nelx, prob.nely, m0, device, dtype)]
        P = torch.as_tensor(child_interpolation(), device=device, dtype=dtype)
        self.transfer = []  # per coarse level: (child_ids (nel_c,4), Pt (nel_c,4,8,8))
        nx, ny = prob.nelx, prob.nely
        while nx % 2 == 0 and ny % 2 == 0 and min(nx, ny) > coarsest_min:
            fine = self.levels[-1]
            ncx, ncy = nx // 2, ny // 2
            # coarse mask by injection: coarse node (IX, IY) <-> fine node (2IX, 2IY)
            mf = fine.mask.view(ny + 1, nx + 1, 2)
            mc = mf[::2, ::2, :].contiguous().view(-1)
            coarse = Level(ncx, ncy, mc, device, dtype)
            X, Y = np.meshgrid(np.arange(ncx), np.arange(ncy))
            X, Y = X.ravel(), Y.ravel()
            kids = np.stack([(2 * Y + cy) * nx + (2 * X + cx) for cy in (0, 1) for cx in (0, 1)], axis=1)
            kids = torch.as_tensor(kids, device=device)
            m_child = fine.mask[fine.edof[kids]]                 # (nel_c, 4, 8)
            m_par = coarse.mask[coarse.edof]                      # (nel_c, 8)
            Pt = m_child[..., :, None] * P[None, :, :, :] * m_par[:, None, None, :]
            self.transfer.append((kids, Pt))
            self.levels.append(coarse)
            nx, ny = ncx, ncy
        self.E = None
        self.cinv = None

    # ---------------------------------------------------------------- operators
    def _apply(self, li, u):
        lv = self.levels[li]
        um = u * lv.mask
        ue = um[lv.edof]                                          # (nel, 8)
        if li == 0:
            fe = self.E[:, None] * (ue @ self.KE)                 # KE symmetric
        else:
            fe = torch.bmm(lv.Ke, ue.unsqueeze(-1)).squeeze(-1)
        y = torch.zeros(lv.ndof, device=self.dev, dtype=self.dt)
        y.index_add_(0, lv.edof_flat, fe.reshape(-1))
        return lv.mask * y + (1.0 - lv.mask) * u

    def _prolong(self, li, uc):
        """coarse level li+1 -> fine level li (masked on both sides)."""
        f, c = self.levels[li], self.levels[li + 1]
        cg = (uc * c.mask).view(c.nely + 1, c.nelx + 1, 2)
        fg = torch.zeros(f.nely + 1, f.nelx + 1, 2, device=self.dev, dtype=self.dt)
        fg[::2, ::2] = cg
        fg[::2, 1::2] = 0.5 * (cg[:, :-1] + cg[:, 1:])
        fg[1::2, ::2] = 0.5 * (cg[:-1, :] + cg[1:, :])
        fg[1::2, 1::2] = 0.25 * (cg[:-1, :-1] + cg[:-1, 1:] + cg[1:, :-1] + cg[1:, 1:])
        return fg.reshape(-1) * f.mask

    def _restrict(self, li, rf):
        """fine level li -> coarse level li+1; exact adjoint of _prolong."""
        f, c = self.levels[li], self.levels[li + 1]
        g = (rf * f.mask).view(f.nely + 1, f.nelx + 1, 2)
        cg = g[::2, ::2].clone()
        e = 0.5 * g[::2, 1::2]
        cg[:, :-1] += e
        cg[:, 1:] += e
        e = 0.5 * g[1::2, ::2]
        cg[:-1, :] += e
        cg[1:, :] += e
        e = 0.25 * g[1::2, 1::2]
        cg[:-1, :-1] += e
        cg[:-1, 1:] += e
        cg[1:, :-1] += e
        cg[1:, 1:] += e
        return cg.reshape(-1) * c.mask

    # ---------------------------------------------------------------- setup per design
    @staticmethod
    def _store(obj, name, value):
        """Assign on first use, then copy in place so captured CUDA graphs keep valid pointers."""
        cur = getattr(obj, name)
        if cur is None:
            setattr(obj, name, value.clone())
        else:
            cur.copy_(value)

    def update(self, E):
        """Rebuild the hierarchy for element moduli E (nel,) on the device. Included in timings."""
        self._store(self, "E", E)
        E = self.E
        lv0 = self.levels[0]
        dK = torch.diagonal(self.KE)
        d0 = torch.zeros(lv0.ndof, device=self.dev, dtype=self.dt)
        d0.index_add_(0, lv0.edof_flat, (E[:, None] * dK[None, :]).reshape(-1))
        self._store(lv0, "diag", lv0.mask * d0 + (1.0 - lv0.mask))
        for li, (kids, Pt) in enumerate(self.transfer):
            fine, coarse = self.levels[li], self.levels[li + 1]
            if li == 0:
                T = torch.matmul(self.KE, Pt)                     # (nel_c, 4, 8, 8)
                T = T * E[kids][..., None, None]
            else:
                T = torch.matmul(fine.Ke[kids], Pt)
            self._store(coarse, "Ke", torch.matmul(Pt.transpose(-1, -2), T).sum(dim=1))
            dc = torch.zeros(coarse.ndof, device=self.dev, dtype=self.dt)
            dc.index_add_(0, coarse.edof_flat, torch.diagonal(coarse.Ke, dim1=1, dim2=2).reshape(-1))
            self._store(coarse, "diag", coarse.mask * dc + (1.0 - coarse.mask))
        # coarsest level: dense matrix, Cholesky, explicit inverse (small; graph-safe to apply)
        lc = self.levels[-1]
        Kel = self.E[:, None, None] * self.KE[None] if len(self.levels) == 1 else lc.Ke
        rows = lc.edof[:, :, None].expand(-1, 8, 8).reshape(-1)
        cols = lc.edof[:, None, :].expand(-1, 8, 8).reshape(-1)
        Kd = torch.zeros(lc.ndof, lc.ndof, device=self.dev, dtype=self.dt)
        Kd.index_put_((rows, cols), Kel.reshape(-1), accumulate=True)
        m = lc.mask
        Kd = m[:, None] * Kd * m[None, :] + torch.diag(1.0 - m)
        L, _info = torch.linalg.cholesky_ex(Kd)          # no host sync (graph-capturable); SPD by construction
        self._store(self, "cinv", torch.cholesky_inverse(L))
        if self.use_graphs and self.g_prec is None:
            self._capture()

    def _capture(self):
        n0 = self.levels[0].ndof
        z = lambda: torch.zeros(n0, device=self.dev, dtype=self.dt)  # noqa: E731
        self.r_s, self.z_s, self.p_s, self.Ap_s = z(), z(), z(), z()
        side = torch.cuda.Stream()
        side.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(side):
            for _ in range(2):
                self.z_s.copy_(self._vcycle(0, self.r_s))
                self.Ap_s.copy_(self._apply(0, self.p_s))
        torch.cuda.current_stream().wait_stream(side)
        self.g_prec = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.g_prec):
            self.z_s.copy_(self._vcycle(0, self.r_s))
        self.g_apply = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.g_apply):
            self.Ap_s.copy_(self._apply(0, self.p_s))

    # ---------------------------------------------------------------- cycle and PCG
    def _vcycle(self, li, r):
        if li == len(self.levels) - 1:
            return self.cinv @ r
        lv, w = self.levels[li], self.omega
        x = w * r / lv.diag
        for _ in range(self.nu_pre - 1):
            x = x + w * (r - self._apply(li, x)) / lv.diag
        rc = self._restrict(li, r - self._apply(li, x))
        x = x + self._prolong(li, self._vcycle(li + 1, rc))
        for _ in range(self.nu_post):
            x = x + w * (r - self._apply(li, x)) / lv.diag
        return x

    def apply_A(self, u):
        if self.g_apply is not None:
            self.p_s.copy_(u)
            self.g_apply.replay()
            return self.Ap_s
        return self._apply(0, u)

    def precondition(self, r):
        if self.g_prec is not None:
            self.r_s.copy_(r)
            self.g_prec.replay()
            return self.z_s
        return self._vcycle(0, r)

    def solve(self, f, x0=None, tol=1e-8, true_tol=1e-7, maxit=500):
        m = self.levels[0].mask
        f = f * m
        x = torch.zeros_like(f) if x0 is None else x0 * m
        nf = torch.linalg.norm(f)
        its = 0
        true_res = float("nan")
        while its < maxit:
            r = f - self.apply_A(x)
            z = self.precondition(r)
            p = z.clone()
            rz = torch.dot(r, z)
            while its < maxit:
                Ap = self.apply_A(p)
                alpha = rz / torch.dot(p, Ap)
                x = x + alpha * p
                r = r - alpha * Ap                      # Ap is consumed before the next graph replay
                its += 1
                if (torch.linalg.norm(r) / nf).item() <= tol:
                    break
                z = self.precondition(r)
                rz_new = torch.dot(r, z)
                p = z + (rz_new / rz) * p
                rz = rz_new
            true_res = (torch.linalg.norm(f - self.apply_A(x)) / nf).item()
            if true_res <= true_tol:
                break
        fallback = False
        if not true_res <= true_tol:
            # Deviation 2026-09-24 (BASELINE_PREREG §9): PCG could not certify the solve; fall back to a
            # sparse direct solve on the CPU and report it. Counted in every run record.
            x = self._direct_solve(f)
            true_res = (torch.linalg.norm(f - self.apply_A(x)) / nf).item()
            fallback = True
        return x, its, true_res, fallback

    def _direct_solve(self, f):
        import scipy.sparse as sp
        from scipy.sparse.linalg import spsolve
        lv = self.levels[0]
        edof = lv.edof.cpu().numpy()
        KE = self.KE.cpu().numpy()
        E = self.E.cpu().numpy()
        iK = np.repeat(edof, 8, axis=1).ravel()
        jK = np.tile(edof, (1, 8)).ravel()
        K = sp.csr_matrix(((E[:, None] * KE.ravel()[None, :]).ravel(), (iK, jK)), shape=(lv.ndof, lv.ndof))
        free = np.flatnonzero(lv.mask.cpu().numpy() > 0.5)
        xf = spsolve(K[free][:, free].tocsc(), f.cpu().numpy()[free])
        x = np.zeros(lv.ndof)
        x[free] = xf
        return torch.as_tensor(x, device=self.dev, dtype=self.dt)
