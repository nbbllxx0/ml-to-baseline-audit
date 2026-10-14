"""Summarise strong-baseline runs: cross-solver equivalence (BASELINE_PREREG §3) and provisional G2.

    python -m analysis.baseline_summary

Reads retest/runs/*/summary.json and design_rep*.npz. Writes evidence/baseline_equivalence.json,
evidence/g2_provisional.json and figures/data/baseline_timings.csv. The latest run per (problem, n, solver) wins, so
the pinned re-timing (plan/BASELINE_PREREG.md §9, CPU placement row) replaces the earlier GPU and PARDISO runs; each
row records whether its run was pinned. Numbers are registered by analysis/register_numbers.py.
"""
import csv
import glob
import json
import pathlib
import statistics

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
OAT_SIMP_GPU_256 = 68.30      # arXiv 2510.23667v1 Table 6, SIMP GPU, 256x256, 150 steps, RTX 4090
OAT_SIMP_CPU_256 = 69.45      # same table, SIMP on Intel i9-14900K
OAT_SIMP_CPU_64 = 3.45
OAT_SIMP_GPU_64 = 9.13
G2_HEADLINE = OAT_SIMP_GPU_256 / 5.0


def pinned(d):
    cfg = json.loads((d / "config.json").read_text(encoding="utf-8")) if (d / "config.json").exists() else {}
    return bool(cfg.get("args", {}).get("cpu_pinning", {}).get("pinned", False))


def load_runs():
    runs = {}
    for f in sorted(glob.glob(str(ROOT / "retest" / "runs" / "*" / "summary.json"))):
        d = pathlib.Path(f).parent
        s = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        if s.get("iters") != 150:
            continue
        key = (s["problem"], s["n"], s["solver"])
        runs[key] = (d, s)            # latest run per key wins (sorted by UTC stamp)
    return runs


def main():
    runs = load_runs()
    eq = []
    for (prob, n) in sorted({(k[0], k[1]) for k in runs}):
        have = {k[2]: runs[k] for k in runs if k[0] == prob and k[1] == n}
        ref = have.get("superlu") or have.get("pardiso")
        if ref is None:
            continue
        xr = np.load(ref[0] / "design_rep0.npz")["xPhys"]
        for solver, (d, s) in have.items():
            x = np.load(d / "design_rep0.npz")["xPhys"]
            dc = abs(s["c_last"] - ref[1]["c_last"]) / abs(ref[1]["c_last"])
            dx = float(np.abs(x - xr).max())
            eq.append({"problem": prob, "n": n, "solver": solver, "ref": ref[1]["solver"],
                       "rel_dc_last": dc, "max_abs_dxphys": dx, "pass": dc <= 1e-5 and dx <= 1e-3})
    (ROOT / "evidence").mkdir(exist_ok=True)
    (ROOT / "evidence" / "baseline_equivalence.json").write_text(json.dumps(eq, indent=2), encoding="utf-8")

    rows = []
    for (prob, n, solver), (d, s) in sorted(runs.items()):
        rows.append({"problem": prob, "n": n, "solver": solver, "total_s_median": s["total_s_median"],
                     "total_s_min": s["total_s_min"], "total_s_max": s["total_s_max"],
                     "per_iter_s_median": s["per_iter_s_median"], "solve_s_median": s["solve_s_median"],
                     "c_last": s["c_last"], "pcg_its_median": s.get("pcg_its_median", ""),
                     "fallbacks": s.get("fallbacks", ""), "energy_above_idle_j": s.get("energy_above_idle_j_median", ""),
                     "cpu_pinned": pinned(d), "run_dir": d.relative_to(ROOT).as_posix()})
    out = ROOT / "figures" / "data"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "baseline_timings.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    g2 = {}
    for prob in ("P1_cantilever", "P2_mbb"):
        best = [(s["total_s_median"], solver) for (p, n, solver), (d, s) in runs.items() if p == prob and n == 256
                and solver in ("gpu", "pardiso")]
        if best:
            t, solver = min(best)
            d_best = runs[(prob, 256, solver)][0]
            g2[prob] = {"strong_baseline_s": t, "solver": solver, "cpu_pinned": pinned(d_best),
                        "run_dir": d_best.relative_to(ROOT).as_posix(), "vs_oat_simp_gpu_256_s": OAT_SIMP_GPU_256,
                        "ratio_oat_over_ours": OAT_SIMP_GPU_256 / t,
                        "band": "headline" if t <= G2_HEADLINE else ("moderate" if t < OAT_SIMP_GPU_256 else "fair")}
    payload = {"status": "provisional (standard formulation P1/P2; final G2 uses OAT generator settings)",
               "threshold_headline_s": G2_HEADLINE, "per_problem": g2,
               "equivalence_all_pass": all(e["pass"] for e in eq), "note":
               "Cross-hardware: our RTX 5090 / i5-14600KF vs OAT's RTX 4090 / i9-14900K. Not a same-machine comparison."}
    (ROOT / "evidence" / "g2_provisional.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    for e in eq:
        print(e)


if __name__ == "__main__":
    main()
