"""Time OAT's own SIMP code (pyEDGE, CUDA backend) on NITO_test problems, on this machine.

Run in the CuPy-only process type:
    source retest/oat_harness/env.sh
    OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_oat_simp --size 256 --k 5 --iters 150

For each problem and each pyEDGE configuration (solver in SPSOLVE / CG / MultiGrid, optimizer in OC / PGD),
it runs one warm-up of 5 iterations, then `iters` timed iterations. It records wall-clock, per-iteration
compliance and the final design. Configurations that raise an error are recorded with the error text. The
problem set comes from problems.select (seed 20260924). Output: retest/runs/<stamp>_oat_simp_n<size>/.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys
import time
import traceback

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.oat_harness.problems import load_split, select, topology_array  # noqa: E402


def build(row, solver_name, void, heavyside, mg_levels=3, mg_coarse='splu'):
    import cupy
    from pyEDGE.CUDA import (StructuredMesh2D, StructuredStiffnessKernel, StructuredFilter2D, FiniteElement,
                             MinimumCompliance, SPSOLVE, CG, MultiGrid)
    shape = topology_array(row).shape                 # (H, W), as OAT: image.size[::-1]
    mesh = StructuredMesh2D(shape[0], shape[1], shape[0] / max(shape), shape[1] / max(shape))
    kernel = StructuredStiffnessKernel(mesh)
    filt = StructuredFilter2D(mesh, 1.5)
    solver = (MultiGrid(mesh, kernel, n_level=mg_levels, coarse_solver=mg_coarse) if solver_name == "MultiGrid"
              else {"SPSOLVE": SPSOLVE, "CG": CG}[solver_name](kernel))
    FE = FiniteElement(mesh, kernel, solver)
    FE.reset_dirichlet_boundary_conditions()
    FE.reset_forces()
    bc = np.array(row["boundary conditions"])
    loads = np.array(row["loads"])
    FE.add_dirichlet_boundary_condition(positions=bc[:, 0:2], dofs=bc[:, 2:])
    FE.add_point_forces(positions=loads[:, 0:2], forces=loads[:, 2:])
    problem = MinimumCompliance(FE, filt, void=void, volume_fraction=[float(row["volume fraction"])],
                                heavyside=heavyside)
    return problem, cupy


def run_config(row, solver_name, opt_name, iters, void, heavyside, mg_levels=3, mg_coarse='splu'):
    from pyEDGE.CUDA import OC, PGD
    problem, cupy = build(row, solver_name, void, heavyside, mg_levels, mg_coarse)
    opt = {"OC": OC, "PGD": PGD}[opt_name](problem)
    for _ in range(5):                                   # warm-up (kernel compilation, allocations)
        opt.iter()
    cupy.cuda.Device().synchronize()
    problem, cupy = build(row, solver_name, void, heavyside, mg_levels, mg_coarse)
    opt = {"OC": OC, "PGD": PGD}[opt_name](problem)
    comps = []
    cupy.cuda.Device().synchronize()
    t0 = time.perf_counter()
    for _ in range(iters):
        opt.iter()
        comps.append(float(problem.f()) if not hasattr(problem.f(), "get") else float(problem.f().get()))
    cupy.cuda.Device().synchronize()
    wall = time.perf_counter() - t0
    x = problem.get_desvars()
    x = x.get() if hasattr(x, "get") else np.asarray(x)
    return wall, comps, x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, required=True, help="64 or 256 (square NITO_test problems)")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--iters", type=int, default=150)
    ap.add_argument("--solvers", default="SPSOLVE,CG,MultiGrid")
    ap.add_argument("--optimizers", default="OC,PGD")
    ap.add_argument("--void", type=float, default=1e-9, help="OAT paper: E_min = 1e-9 in data generation")
    ap.add_argument("--heavyside", action="store_true")
    ap.add_argument("--mg-levels", type=int, default=3,
                    help="pyEDGE MultiGrid n_level (default 3). At 256^2 use 5 (coarse 16^2, as 64^2 with 3): "
                         "the default 64^2 coarse splu crashes in cuSPARSE spSM on this machine (deviation log)")
    ap.add_argument("--mg-coarse", default="splu", choices=["splu", "cg", "spsolve"],
                    help="pyEDGE MultiGrid coarse_solver (default splu). 'cg' avoids the cuSPARSE spSM crash")
    args = ap.parse_args()
    from tools.pin import pin_from_env
    args.cpu_pinning = pin_from_env()          # PIN_PCORES=1: performance cores, high priority (BASELINE_PREREG §9)
    rows = load_split("NITO_test")
    ids = select(rows, args.size, args.size, args.k)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "retest" / "runs" / f"{stamp}_oat_simp_n{args.size}"
    out.mkdir(parents=True)
    (out / "config.json").write_text(json.dumps({**vars(args), "problem_ids": ids, "split": "NITO_test",
                                                 "oat_commit": "dc5e817497eb7d5517f93b7c79ea463ab2761082"},
                                                indent=2), encoding="utf-8")
    results = []
    for pid in ids:
        for s in args.solvers.split(","):
            for o in args.optimizers.split(","):
                rec = {"problem_id": pid, "solver": s, "optimizer": o}
                try:
                    wall, comps, x = run_config(rows[pid], s, o, args.iters, args.void, args.heavyside, args.mg_levels, args.mg_coarse)
                    rec.update({"wall_s": wall, "per_iter_s": wall / args.iters, "c_first": comps[0],
                                "c_last": comps[-1], "compliance": comps})
                    np.savez_compressed(out / f"design_{pid}_{s}_{o}.npz", x=x)
                    print(f"problem {pid} {s:9s} {o:3s}: {wall:8.2f} s  c_last {comps[-1]:.6g}", flush=True)
                except Exception as exc:
                    rec["error"] = f"{type(exc).__name__}: {exc}"
                    rec["traceback"] = traceback.format_exc()[-2000:]
                    print(f"problem {pid} {s:9s} {o:3s}: ERROR {rec['error'][:160]}", flush=True)
                results.append(rec)
                (out / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("run dir:", out.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
