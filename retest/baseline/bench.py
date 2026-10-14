"""Timing harness for the strong baseline (plan/BASELINE_PREREG.md §4-5, §8).

    <torch5090 python> -m retest.baseline.bench --solver gpu     --problem P1 --n 256
    <Pytorch python>   -m retest.baseline.bench --solver pardiso --problem P1 --n 256
    <torch5090 python> -m retest.baseline.bench --solver superlu --problem P1 --n 256

Writes retest/runs/<UTC stamp>_<solver>_<problem>_n<n>/ with config.json, record_rep<k>.json,
design_rep<k>.npz, power_rep<k>.csv (GPU runs) and summary.json.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import platform
import statistics
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.baseline.fem2d import PROBLEMS  # noqa: E402
from tools.energy import PowerSampler, idle_power  # noqa: E402


def manifest_digest():
    m = ROOT / "evidence" / "MANIFEST.sha256"
    return hashlib.sha256(m.read_bytes()).hexdigest() if m.exists() else None


def first_below(changes, thr=0.01):
    for i, c in enumerate(changes):
        if c < thr:
            return i + 1
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solver", choices=["gpu", "pardiso", "superlu"], required=True)
    ap.add_argument("--problem", choices=sorted(PROBLEMS), required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--iters", type=int, default=150)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--warmup", type=int, default=10)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    from tools.pin import pin_from_env
    args.cpu_pinning = pin_from_env()          # PIN_PCORES=1: performance cores, high priority (BASELINE_PREREG §9)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = ROOT / "retest" / "runs" / f"{stamp}_{args.solver}_{args.problem}_n{args.n}{args.tag}"
    run_dir.mkdir(parents=True)
    prob = PROBLEMS[args.problem](args.n)
    if args.solver == "gpu":
        import torch
        from retest.baseline import simp_gpu as mod
        runner = lambda iters: mod.run(prob, iters=iters)  # noqa: E731
        extra = {"torch": torch.__version__, "cuda": torch.version.cuda, "device": torch.cuda.get_device_name(0)}
    else:
        from retest.baseline import simp_cpu as mod
        runner = lambda iters: mod.run(prob, solver=args.solver, iters=iters)  # noqa: E731
        extra = {}
    import scipy
    config = {
        "args": vars(args), "problem": {"name": prob.name, "nelx": prob.nelx, "nely": prob.nely,
                                        "volfrac": prob.volfrac, "rmin": prob.rmin, "penal": prob.penal,
                                        "Emin": prob.Emin, "nu": prob.nu},
        "python": sys.version.split()[0], "executable": sys.executable, "numpy": np.__version__,
        "scipy": scipy.__version__, "platform": platform.platform(), "manifest_sha256": manifest_digest(),
        "started_utc": stamp, **extra,
    }
    (run_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    t = time.perf_counter()
    runner(args.warmup)                                   # warm-up, discarded
    warm_s = time.perf_counter() - t
    idle_w = idle_power(5.0, run_dir / "idle_power.csv") if args.solver == "gpu" else None

    totals, energies, energies_above = [], [], []
    for rep in range(args.repeats):
        if args.solver == "gpu":
            with PowerSampler(run_dir / f"power_rep{rep}.csv") as ps:
                rec, xphys, _ = runner(args.iters)
            energies.append(ps.energy_j())
            energies_above.append(ps.energy_j(subtract_w=idle_w))
        else:
            rec, xphys, _ = runner(args.iters)
        totals.append(rec["t_total"])
        (run_dir / f"record_rep{rep}.json").write_text(json.dumps(rec), encoding="utf-8")
        np.savez_compressed(run_dir / f"design_rep{rep}.npz", xPhys=xphys)
        print(f"rep {rep}: total {rec['t_total']:.3f} s  c_last {rec['c'][-1]:.6f}", flush=True)

    last = json.loads((run_dir / f"record_rep{args.repeats - 1}.json").read_text(encoding="utf-8"))
    summary = {
        "solver": args.solver, "problem": prob.name, "n": args.n, "iters": args.iters,
        "total_s_median": statistics.median(totals), "total_s_min": min(totals), "total_s_max": max(totals),
        "total_s_all": totals, "setup_s": last["t_setup"], "warmup_s": warm_s,
        "per_iter_s_median": statistics.median(last["t_iter"]),
        "solve_s_median": statistics.median(last["t_solve"]),
        "c_last": last["c"][-1], "vol_last": last["vol"][-1],
        "first_iter_change_below_0.01": first_below(last["change"]),
        "true_res_max": max(last["true_res"]),
    }
    if args.solver == "gpu":
        summary.update({"pcg_its_median": statistics.median(last["pcg_its"]), "pcg_its_max": max(last["pcg_its"]),
                        "fallbacks": int(sum(last["fallback"])), "idle_power_w": idle_w,
                        "energy_j_median": statistics.median(energies),
                        "energy_above_idle_j_median": statistics.median(energies_above)})
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("run dir:", run_dir.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
