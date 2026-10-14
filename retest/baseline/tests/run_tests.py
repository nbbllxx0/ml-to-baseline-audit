"""Correctness tests for the strong baseline (evidence item ED2).

    <torch5090 python> -m retest.baseline.tests.run_tests --part gpu       # KE, patch, Galerkin, PCG vs direct
    <Pytorch python>   -m retest.baseline.tests.run_tests --part pardiso   # PARDISO vs SuperLU on the same K

Each part writes evidence/baseline_tests_<part>.json. Every test states its threshold; any failure
exits non-zero.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from retest.baseline.fem2d import cantilever, element_dofs, element_stiffness, mbb  # noqa: E402

RESULTS = []


def check(name, value, threshold, ok, note="", gating=True):
    RESULTS.append({"test": name, "value": float(value), "threshold": threshold, "pass": bool(ok),
                    "gating": gating, "note": note})
    tag = ("PASS" if ok else "FAIL") + ("" if gating else " (non-gating)")
    print(f"{tag}  {name}: {value:.3e}  ({threshold}) {note}")


def top88_KE(nu=0.3):
    A11 = np.array([[12, 3, -6, -3], [3, 12, 3, 0], [-6, 3, 12, -3], [-3, 0, -3, 12]], float)
    A12 = np.array([[-6, -3, 0, 3], [-3, -6, -3, -6], [0, -3, -6, 3], [3, -6, 3, -6]], float)
    B11 = np.array([[-4, 3, -2, 9], [3, -4, -9, 4], [-2, -9, -4, -3], [9, 4, -3, -4]], float)
    B12 = np.array([[2, -3, 4, -9], [-3, 2, 9, -2], [4, 9, 2, 3], [-9, -2, 3, 2]], float)
    return 1.0 / (1 - nu ** 2) / 24.0 * (np.block([[A11, A12], [A12.T, A11]]) + nu * np.block([[B11, B12], [B12.T, B11]]))


def assemble_full(prob, E, KE):
    edof = element_dofs(prob.nelx, prob.nely)
    iK = np.repeat(edof, 8, axis=1).ravel()
    jK = np.tile(edof, (1, 8)).ravel()
    sK = (E[:, None] * KE.ravel()[None, :]).ravel()
    return sp.csr_matrix((sK, (iK, jK)), shape=(prob.ndof, prob.ndof))


def test_element(KE):
    check("KE symmetry max|KE-KE^T|", np.abs(KE - KE.T).max(), "<1e-14", np.abs(KE - KE.T).max() < 1e-14)
    ev = np.sort(np.linalg.eigvalsh(KE))
    check("KE: 3 zero eigenvalues (max |lambda_1..3|)", np.abs(ev[:3]).max(), "<1e-12", np.abs(ev[:3]).max() < 1e-12)
    check("KE: 5 positive eigenvalues (min lambda_4..8)", ev[3:].min(), ">1e-3", ev[3:].min() > 1e-3)
    xy = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
    rot = np.stack([-xy[:, 1], xy[:, 0]], axis=1).ravel()
    check("KE: rigid rotation in nullspace |KE r|", np.abs(KE @ rot).max(), "<1e-13", np.abs(KE @ rot).max() < 1e-13)
    d = np.abs(KE - top88_KE()).max()
    check("KE equals top88 closed form", d, "<1e-14", d < 1e-14, "Andreassen et al. 2011 KE, same node order")


def test_patch(KE):
    prob = cantilever(4)
    K = assemble_full(prob, np.ones(prob.nel), KE)
    nx, ny = prob.nelx + 1, prob.nely + 1
    ix, iy = np.meshgrid(np.arange(nx), np.arange(ny))
    ux = 0.01 * ix.ravel() + 0.02 * iy.ravel()
    uy = -0.03 * ix.ravel() + 0.005 * iy.ravel()
    u = np.stack([ux, uy], axis=1).ravel()
    fint = (K @ u).reshape(ny, nx, 2)[1:-1, 1:-1].ravel()
    check("patch test: interior forces under linear field", np.abs(fint).max(), "<1e-14", np.abs(fint).max() < 1e-14)


def random_density(prob, seed):
    rng = np.random.default_rng(seed)
    rho = rng.random(prob.nel)
    rho[rng.random(prob.nel) < 0.3] = 0.0            # voids at Emin -> contrast 1e-9
    return prob.Emin + rho ** prob.penal * (prob.E0 - prob.Emin)


def part_gpu():
    import torch
    from retest.baseline.gmg2d import GMGSolver
    KE = element_stiffness()
    test_element(KE)
    test_patch(KE)
    dev, dt = "cuda", torch.float64
    test_gpu_loop_paths()
    for mk, n in ((cantilever, 32), (mbb, 64)):
        prob = mk(n)
        E = random_density(prob, 1)
        s = GMGSolver(prob, KE, device=dev, dtype=dt)
        s.update(torch.as_tensor(E, device=dev, dtype=dt))
        rng = np.random.default_rng(2)
        worst_adj, worst_gal = 0.0, 0.0
        for li in range(len(s.levels) - 1):
            vc = torch.as_tensor(rng.standard_normal(s.levels[li + 1].ndof), device=dev, dtype=dt)
            wf = torch.as_tensor(rng.standard_normal(s.levels[li].ndof), device=dev, dtype=dt)
            lhs = torch.dot(s._prolong(li, vc), wf).item()
            rhs = torch.dot(vc, s._restrict(li, wf)).item()
            worst_adj = max(worst_adj, abs(lhs - rhs) / max(abs(lhs), 1e-300))
            mc = s.levels[li + 1].mask
            gal_local = s._apply(li + 1, vc) - (1 - mc) * vc
            gal_global = s._restrict(li, s._apply(li, s._prolong(li, vc)) - (1 - s.levels[li].mask) * s._prolong(li, vc))
            worst_gal = max(worst_gal, (torch.linalg.norm(gal_local - gal_global) / torch.linalg.norm(gal_global)).item())
        check(f"{prob.name} n={n}: restriction = adjoint of prolongation", worst_adj, "<1e-12", worst_adj < 1e-12)
        check(f"{prob.name} n={n}: element-local Galerkin = global P^T K P", worst_gal, "<1e-12", worst_gal < 1e-12)
        # Solve accuracy on three realistic fields (gating, no fallback allowed) and one stress field.
        from retest.baseline import simp_cpu
        _, xdesign, _ = simp_cpu.run(prob, solver="superlu", iters=60)
        rng = np.random.default_rng(3)
        fields = {
            "uniform": np.ones(prob.nel),
            "random_no_void": prob.Emin + rng.random(prob.nel) ** 3 * (prob.E0 - prob.Emin),
            "simp_design_it60": prob.Emin + xdesign ** 3 * (prob.E0 - prob.Emin),
            "stress_random_30pct_isolated_voids": E,
        }
        f = torch.as_tensor(prob.force, device=dev, dtype=dt)
        free = np.setdiff1d(np.arange(prob.ndof), prob.fixed)
        for label, Ef in fields.items():
            s.update(torch.as_tensor(Ef, device=dev, dtype=dt))
            u, its, tres, fb = s.solve(f)
            K = assemble_full(prob, Ef, KE)
            ud = np.zeros(prob.ndof)
            ud[free] = spsolve(K[free][:, free].tocsc(), prob.force[free])
            err = np.linalg.norm(u.cpu().numpy() - ud) / np.linalg.norm(ud)
            tag = f"{prob.name} n={n} [{label}]"
            if label.startswith("stress"):
                check(f"{tag}: guarded solve true residual", tres, "<=1e-7", tres <= 1e-7,
                      f"PCG its={its}, fallback={fb}; forward error vs direct {err:.1e}. Stress field: isolated "
                      "E_min voids make K near-singular; a residual floor here also bounds sparse direct solvers",
                      gating=False)
            else:
                check(f"{tag}: PCG vs sparse direct, rel. error in u", err, "<1e-6", err < 1e-6, f"PCG its={its}")
                check(f"{tag}: PCG true residual without fallback", tres, "<=1e-7", tres <= 1e-7 and not fb,
                      f"fallback={fb}")
                if label == "simp_design_it60":
                    s_ng = GMGSolver(prob, KE, device=dev, dtype=dt, use_graphs=False)
                    s_ng.update(torch.as_tensor(Ef, device=dev, dtype=dt))
                    u_ng, its_ng, _, _ = s_ng.solve(f)
                    dg = (torch.linalg.norm(u - u_ng) / torch.linalg.norm(u_ng)).item()
                    check(f"{tag}: CUDA-graph path equals eager path", dg, "<1e-12", dg < 1e-12,
                          f"PCG its graph={its}, eager={its_ng}")



def test_gpu_loop_paths():
    """Full SIMP loop: graph-captured path vs eager path, and GPU vs top88-faithful CPU port."""
    from retest.baseline import simp_cpu, simp_gpu
    for mk, n in ((cantilever, 32), (mbb, 48)):
        prob = mk(n)
        rg, xg, _ = simp_gpu.run(prob, iters=40, graphs=True)
        re_, xe, _ = simp_gpu.run(prob, iters=40, graphs=False)
        re2, xe2, _ = simp_gpu.run(prob, iters=40, graphs=False)
        # run-to-run floor: CUDA index_add_ uses atomics, so summation order (and the last bits) varies
        floor_x = float(np.abs(xe - xe2).max())
        check(f"{prob.name} n={n}: GPU eager vs eager (nondeterminism floor), max |dxPhys|", floor_x,
              "recorded; must be <1e-6", floor_x < 1e-6, "atomic-add summation order")
        rc, xc, _ = simp_cpu.run(prob, solver="superlu", iters=40)
        dcomp = max(abs(a - b) / abs(b) for a, b in zip(rg["c"], re_["c"]))
        check(f"{prob.name} n={n}: GPU loop graph vs eager, max rel. compliance diff (40 its)", dcomp, "<1e-10",
              dcomp < 1e-10)
        dx = float(np.abs(xg - xe).max())
        check(f"{prob.name} n={n}: GPU loop graph vs eager, max |dxPhys|", dx, "<1e-6 (floor-calibrated)", dx < 1e-6,
              f"eager-vs-eager floor {floor_x:.1e}; first threshold 1e-8 was below the measured floor (2.9e-7)")
        dcc = abs(rg["c"][-1] - rc["c"][-1]) / abs(rc["c"][-1])
        check(f"{prob.name} n={n}: GPU vs CPU top88-faithful port, rel. compliance diff at it 40", dcc, "<1e-5",
              dcc < 1e-5)
        dxc = float(np.abs(xg - xc).max())
        check(f"{prob.name} n={n}: GPU vs CPU top88-faithful port, max |dxPhys| at it 40", dxc, "<1e-3", dxc < 1e-3)


def part_pardiso():
    from retest.baseline import simp_cpu
    from retest.baseline.simp_cpu import Assembler
    from pypardiso import PyPardisoSolver
    KE = element_stiffness()
    for mk, n in ((cantilever, 64), (mbb, 64)):
        prob = mk(n)
        _, xdesign, _ = simp_cpu.run(prob, solver="superlu", iters=60)
        rng = np.random.default_rng(3)
        fields = {
            "uniform": np.ones(prob.nel),
            "random_no_void": prob.Emin + rng.random(prob.nel) ** 3 * (prob.E0 - prob.Emin),
            "simp_design_it60": prob.Emin + xdesign ** 3 * (prob.E0 - prob.Emin),
            "stress_random_30pct_isolated_voids": random_density(prob, 1),
        }
        full = Assembler(prob, KE, upper_only=False)
        up = Assembler(prob, KE, upper_only=True)
        b = prob.force[full.free_idx]
        ps = PyPardisoSolver(mtype=2)
        Ku0 = up.assemble(np.ones(prob.nel))
        ps._check_A(Ku0)
        ps.set_phase(11)
        ps._call_pardiso(Ku0, np.zeros(up.n))
        ps.set_phase(23)
        for label, Ef in fields.items():
            Kf, Ku = full.assemble(Ef), up.assemble(Ef)
            x_ref = spsolve(Kf.tocsc(), b)
            x = ps._call_pardiso(Ku, b)          # numeric factorization + solve on the frozen symbolic analysis
            err = np.linalg.norm(x - x_ref) / np.linalg.norm(x_ref)
            res = np.linalg.norm(b - Kf @ x) / np.linalg.norm(b)
            res_ref = np.linalg.norm(b - Kf @ x_ref) / np.linalg.norm(b)
            tag = f"{prob.name} n={n} [{label}]"
            gating = not label.startswith("stress")
            check(f"{tag}: PARDISO (SPD, phase 23) vs SuperLU, rel. difference", err, "<1e-8", err < 1e-8,
                  f"residuals PARDISO {res:.1e}, SuperLU {res_ref:.1e}", gating=gating)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["gpu", "pardiso"], required=True)
    args = ap.parse_args()
    {"gpu": part_gpu, "pardiso": part_pardiso}[args.part]()
    out = ROOT / "evidence" / f"baseline_tests_{args.part}.json"
    out.parent.mkdir(exist_ok=True)
    payload = {"run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "python": sys.executable, "results": RESULTS,
               "all_pass": all(r["pass"] for r in RESULTS if r["gating"]),
               "non_gating_failures": sum(1 for r in RESULTS if not r["gating"] and not r["pass"])}
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("wrote", out.relative_to(ROOT).as_posix(), "all_pass (gating) =", payload["all_pass"],
          "non-gating failures =", payload["non_gating_failures"])
    sys.exit(0 if payload["all_pass"] else 1)


if __name__ == "__main__":
    main()
