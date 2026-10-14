"""Energy per design from the power-sampled runs (claim C3, N025–N026; plan/BASELINE_PREREG.md §5).

    python -m analysis.energy [--log retest/logs/oat_post_retest_2026-09-24.log]

The post-re-test driver (retest/oat_harness/run_post_retest.sh) runs our GPU baseline and OAT inference once more with
`--power`: nvidia-smi samples GPU board power every 100 ms, a 5 s idle trace comes first, and energy is the trapezoidal
integral over the repeats of each problem divided by the number of repeats. These runs exist for energy only; their
times are not used as timing results, because sampling adds load. CPU package energy is not measured.
Writes evidence/energy.json and figures/data/energy.csv.
"""
import argparse
import csv
import json
import pathlib
import re
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.oat_retest_summary import stages  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="retest/logs/oat_post_retest_2026-09-24.log")
    args = ap.parse_args()
    rows = []
    for stage, run in stages(ROOT / args.log).items():
        if not stage.startswith("energy"):
            continue
        f = run / ("timings.json" if (run / "timings.json").exists() else "results.json")
        d = json.loads(f.read_text(encoding="utf-8"))
        method = "OAT inference" if f.name == "timings.json" else f"ours {d['config']['solver']}"
        for r in d["results"]:
            e = r.get("energy")
            if not e:
                continue
            rows.append({"stage": stage, "method": method, "size": int(re.search(r"_n(\d+)", run.name).group(1)),
                         "problem_id": r["problem_id"], "board_j_per_design": e["board_j_per_design"],
                         "above_idle_j_per_design": e["above_idle_j_per_design"], "idle_w": e["idle_w"],
                         "window_s": e["window_s"], "repeats": e["repeats"], "run": run.relative_to(ROOT).as_posix()})
    out = {"log": args.log, "method": "nvidia-smi board power, 100 ms, trapezoid; idle from a 5 s trace",
           "by_stage": {}}
    for stage in sorted({r["stage"] for r in rows}):
        sel = [r for r in rows if r["stage"] == stage]
        out["by_stage"][stage] = {
            "n_problems": len(sel),
            "board_j_per_design_median": statistics.median(r["board_j_per_design"] for r in sel),
            "above_idle_j_per_design_median": statistics.median(r["above_idle_j_per_design"] for r in sel)}
    out["rows"] = rows
    (ROOT / "evidence" / "energy.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    if rows:
        (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
        with open(ROOT / "figures" / "data" / "energy.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    for stage, s in out["by_stage"].items():
        print(f"{stage:32s} n={s['n_problems']}  board {s['board_j_per_design_median']:.1f} J/design  "
              f"above idle {s['above_idle_j_per_design_median']:.1f} J/design")


if __name__ == "__main__":
    main()
