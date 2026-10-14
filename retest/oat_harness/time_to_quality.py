"""Time-to-quality for the strong baseline (evidence for display item F4; plan/BASELINE_PREREG.md §7).

Step 1 (torch5090 env): run S-GPU on the seeded NITO_test problems at fixed iteration budgets. Each budget is a
fresh run, so the design at budget K equals the K-th iterate of a longer run up to GPU atomic-add noise. Wall-clock
and the design in pyEDGE element order are recorded:
    python -m retest.oat_harness.time_to_quality run --size 256 --k 5

Step 2 (oat env, CuPy process): score every saved design with OAT's own evaluator (eval_designs.evaluator):
    OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_to_quality score --run <run dir>

Output: <run dir>/ttq.json with per problem and budget: wall_s, c_ours, CE_pct (OAT metric), vf_thresholded.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.oat_harness.problems import load_split, select, to_fem2d  # noqa: E402

BUDGETS = [5, 10, 15, 20, 30, 40, 50, 75, 100, 150]


def run(args):
    if args.solver == "gpu":                    # torch5090 env
        import torch
        from retest.baseline import simp_gpu
        sync = torch.cuda.synchronize
        solve = lambda prob, K: simp_gpu.run(prob, iters=K, return_x=True)  # noqa: E731
    else:                                       # Pytorch env (pypardiso)
        from retest.baseline import simp_cpu
        sync = lambda: None  # noqa: E731
        solve = lambda prob, K: simp_cpu.run(prob, solver=args.solver, iters=K, return_x=True)  # noqa: E731
    rows = load_split("NITO_test")
    ids = select(rows, args.size, args.size, args.k)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "retest" / "runs" / f"{stamp}_ttq_{args.solver}_n{args.size}"
    out.mkdir(parents=True)
    recs = []
    for pid in ids:
        prob = to_fem2d(rows[pid])
        solve(prob, 10)                                               # warm-up
        for K in BUDGETS:
            sync()
            t0 = time.perf_counter()
            rec, xphys, _, x = solve(prob, K)
            sync()
            wall_incl_setup = time.perf_counter() - t0
            g = x.reshape(prob.nely, prob.nelx)
            np.savez_compressed(out / f"design_{pid}_it{K:03d}.npz", x_pyedge=g.T.reshape(-1))
            recs.append({"problem_id": pid, "iters": K, "loop_s": rec["t_total"], "wall_incl_setup_s": wall_incl_setup,
                         "c_ours_last": rec["c"][-1]})
            print(f"problem {pid} K={K:3d}: loop {rec['t_total']:.3f} s (with setup {wall_incl_setup:.3f} s)", flush=True)
    (out / "ttq_runs.json").write_text(json.dumps({"size": args.size, "problem_ids": ids, "budgets": BUDGETS,
                                                   "solver": args.solver, "cpu_pinning": args.cpu_pinning,
                                                   "runs": recs}, indent=1), encoding="utf-8")
    print("run dir:", out.relative_to(ROOT).as_posix())


def score(args):
    from retest.oat_harness.eval_designs import evaluator, compliance
    from retest.oat_harness.problems import topology_array
    d = pathlib.Path(args.run)
    meta = json.loads((d / "ttq_runs.json").read_text(encoding="utf-8"))
    rows = load_split("NITO_test")
    out = []
    for pid in meta["problem_ids"]:
        problem, _ = evaluator(rows[pid])
        c_gt = compliance(problem, (topology_array(rows[pid]) > 0).astype(np.float64))
        for r in [r for r in meta["runs"] if r["problem_id"] == pid]:
            x = np.load(d / f"design_{pid}_it{r['iters']:03d}.npz")["x_pyedge"]
            c = compliance(problem, x)
            out.append({**r, "c_gt": c_gt, "c_oat_eval": c, "CE_pct": (c - c_gt) / c_gt * 100.0,
                        "vf_thresholded": float((x > 0.5).mean())})
            print(f"problem {pid} K={r['iters']:3d}: CE {out[-1]['CE_pct']:7.2f}%  loop {r['loop_s']:.3f} s", flush=True)
    (d / "ttq.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote", (d / "ttq.json").relative_to(ROOT).as_posix())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "score"])
    ap.add_argument("--size", type=int)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--run")
    ap.add_argument("--solver", choices=["gpu", "pardiso"], default="gpu")
    args = ap.parse_args()
    from tools.pin import pin_from_env
    args.cpu_pinning = pin_from_env()          # PIN_PCORES=1: performance cores, high priority (BASELINE_PREREG §9)
    run(args) if args.mode == "run" else score(args)


if __name__ == "__main__":
    main()
