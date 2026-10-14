"""Run our strong baseline (S-GPU or S-PARDISO) on the same NITO_test problems used for the OAT re-test.

    <torch5090 python> -m retest.oat_harness.run_ours_on_nito --solver gpu --size 256 --k 5
    <Pytorch python>   -m retest.oat_harness.run_ours_on_nito --solver pardiso --size 256 --k 5

Formulation parameters come from OAT, per plan/BASELINE_PREREG.md §1 and §9: nu = 1/3 (pyEDGE default
material), E_min = 1e-9 (OAT paper, data generation), filter radius 1.5 elements (OAT evaluator), p = 3.
Update rule: top88 OC, as pre-registered. Timing: one warm-up run (10 iterations), then `repeats` runs of
`iters` iterations, per problem.
Output: retest/runs/<stamp>_ours_<solver>_nito_n<size>/ with results.json and design_<id>.npz.
--power (GPU only; a separate energy run, not a timing run): a 5 s idle trace, then nvidia-smi board power sampled
every 100 ms around each problem's timed repeats. The window covers setup and loop of every repeat; energy per design
is the window integral divided by the number of repeats (plan/BASELINE_PREREG.md §5).
"""
import contextlib
import argparse
import datetime as dt
import json
import pathlib
import statistics
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.oat_harness.problems import load_split, select, to_fem2d  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solver", choices=["gpu", "pardiso", "superlu"], required=True)
    ap.add_argument("--size", type=int, required=True)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--iters", type=int, default=150)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--power", action="store_true", help="sample GPU board power (energy run; GPU solver only)")
    args = ap.parse_args()
    from tools.pin import pin_from_env
    args.cpu_pinning = pin_from_env()          # PIN_PCORES=1: performance cores, high priority (BASELINE_PREREG §9)
    if args.power and args.solver != "gpu":
        ap.error("--power measures GPU board energy; use it with --solver gpu")
    if args.solver == "gpu":
        from retest.baseline import simp_gpu as mod
        run = lambda p, it: mod.run(p, iters=it, return_x=True)  # noqa: E731
    else:
        from retest.baseline import simp_cpu as mod
        run = lambda p, it: mod.run(p, solver=args.solver, iters=it, return_x=True)  # noqa: E731
    rows = load_split("NITO_test")
    ids = select(rows, args.size, args.size, args.k)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "retest" / "runs" / f"{stamp}_ours_{args.solver}_nito_n{args.size}{'_power' if args.power else ''}"
    out.mkdir(parents=True)
    idle_w = None
    if args.power:
        from tools.energy import PowerSampler, idle_power
        idle_w = idle_power(5.0, out / "idle_power.csv")
    results = []
    for pid in ids:
        prob = to_fem2d(rows[pid])
        run(prob, 10)                                                    # warm-up
        totals, last = [], None
        with (PowerSampler(out / f"power_{pid}.csv") if args.power else contextlib.nullcontext()) as ps:
            for _ in range(args.repeats):
                rec, xphys, _, xdes = run(prob, args.iters)
                totals.append(rec["t_total"])
                last = (rec, xphys, xdes)
        rec, xphys, xdes = last
        g_x = xdes.reshape(prob.nely, prob.nelx)
        np.savez_compressed(out / f"design_{pid}.npz", xPhys=xphys.reshape(prob.nely, prob.nelx), x=g_x,
                            x_pyedge=g_x.T.reshape(-1))           # pyEDGE element order (column-major)
        r = {"problem_id": pid, "nelx": prob.nelx, "nely": prob.nely, "volfrac": prob.volfrac,
             "n_fixed_dofs": int(len(prob.fixed)), "total_s_all": totals, "total_s_median": statistics.median(totals),
             "per_iter_s_median": statistics.median(rec["t_iter"]), "c_last": rec["c"][-1], "compliance": rec["c"],
             "true_res_max": max(rec["true_res"])}
        if args.power:
            r["energy"] = {"idle_w": idle_w, "repeats": args.repeats, "window_s": ps.t_stop - ps.t_start,
                           "board_j_per_design": ps.energy_j() / args.repeats,
                           "above_idle_j_per_design": ps.energy_j(subtract_w=idle_w) / args.repeats}
        if args.solver == "gpu":
            r.update({"pcg_its_median": statistics.median(rec["pcg_its"]), "pcg_its_max": max(rec["pcg_its"]),
                      "fallbacks": int(sum(rec["fallback"]))})
        results.append(r)
        print(f"problem {pid}: median {r['total_s_median']:.3f} s  c_last {r['c_last']:.6g}"
              + (f"  pcg med {r['pcg_its_median']} max {r['pcg_its_max']} fb {r['fallbacks']}" if args.solver == "gpu" else ""),
              flush=True)
        (out / "results.json").write_text(json.dumps({"config": {**vars(args), "problem_ids": ids,
                                                                 "formulation": "nu=1/3, Emin=1e-9, rmin=1.5, p=3, top88 OC"},
                                                      "results": results}, indent=1), encoding="utf-8")
    print("run dir:", out.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
