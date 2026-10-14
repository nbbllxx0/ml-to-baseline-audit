"""Summarize the final same-machine OAT re-test (plan/BASELINE_PREREG.md §7, §9) from its driver log.

    python -m analysis.oat_retest_summary --log retest/logs/oat_pinned_retest_2026-09-24.log            # primary
    python -m analysis.oat_retest_summary --log retest/logs/oat_final_retest_2026-09-24.log --tag default_sched

The driver log (retest/oat_harness/run_final_retest.sh) prints one "=== <stage> ===" header per stage and one
"run dir: <path>" line per completed stage, so each run folder is tied to its stage without hand-picking folders.
Writes evidence/oat_retest_summary[_<tag>].json and figures/data/oat_retest_timings[_<tag>].csv (one row per problem
and method). The untagged files are the primary (pinned) timings that the other analyses read.

Times are wall-clock seconds for one design:
  * OAT SIMP (pyEDGE): the full 150-iteration loop (time_oat_simp.py);
  * ours: the median over repeats of the 150-iteration loop, warm-up excluded (run_ours_on_nito.py);
  * OAT inference: the median over 10 sampling runs, warm-up excluded (run_oat_inference.py).
"""
import argparse
import csv
import json
import pathlib
import re
import statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]


def stages(log):
    out, current = {}, None
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^=== (.+) ===$", line.strip())
        if m:
            current = m.group(1)
        m = re.match(r"^run dir: (\S+)", line.strip())
        if m and current:
            out[current] = ROOT / m.group(1)
    return out


def rows_for(stage, run):
    rows = []
    if (run / "timings.json").exists():                                   # OAT inference
        d = json.loads((run / "timings.json").read_text(encoding="utf-8"))
        for r in d["results"]:
            rows.append({"stage": stage, "method": "OAT inference", "config": f"{d['config']['steps']} DDIM steps, "
                         f"{d['config']['compile']}", "problem_id": r["problem_id"], "time_s": r.get("median_s"),
                         "c_last": None, "status": "ok" if "median_s" in r else r.get("error", "error")[:120]})
        return rows
    d = json.loads((run / "results.json").read_text(encoding="utf-8"))
    if isinstance(d, dict):                                               # ours (run_ours_on_nito.py)
        cfg = d["config"]
        for r in d["results"]:
            rows.append({"stage": stage, "method": f"ours {cfg['solver']}", "config": cfg.get("formulation", ""),
                         "problem_id": r["problem_id"], "time_s": r["total_s_median"], "c_last": r["c_last"],
                         "status": "ok" if not r.get("fallbacks") else f"ok, {r['fallbacks']} direct fallbacks",
                         "pcg_its_median": r.get("pcg_its_median"), "pcg_its_max": r.get("pcg_its_max")})
        return rows
    cfg = json.loads((run / "config.json").read_text(encoding="utf-8"))   # OAT SIMP (time_oat_simp.py)
    for r in d:
        label = r["solver"] + (f"({cfg['mg_levels']})" if r["solver"] == "MultiGrid" else "") + "+" + r["optimizer"]
        rows.append({"stage": stage, "method": "OAT SIMP (pyEDGE)", "config": label, "problem_id": r["problem_id"],
                     "time_s": r.get("wall_s"), "c_last": r.get("c_last"),
                     "status": "ok" if "error" not in r else r["error"][:120]})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="retest/logs/oat_pinned_retest_2026-09-24.log")
    ap.add_argument("--tag", default="", help="suffix for the output files; empty = primary")
    args = ap.parse_args()
    sfx = f"_{args.tag}" if args.tag else ""
    # timing stages only; the pinned log also holds G2, time-to-quality and energy stages, analysed elsewhere
    st = {k: v for k, v in stages(ROOT / args.log).items() if k.startswith(("OAT SIMP", "ours ", "OAT inference"))}
    rows = []
    for stage, run in st.items():
        size = int(re.search(r"_n(\d+)", run.name).group(1))
        for r in rows_for(stage, run):
            rows.append({"size": size, "run": run.relative_to(ROOT).as_posix(), **r})
    summary = {"log": args.log, "stages": {}}
    for stage, run in st.items():
        sel = [r for r in rows if r["stage"] == stage]
        ok = [r["time_s"] for r in sel if r["status"].startswith("ok")]
        summary["stages"][stage] = {
            "run": run.relative_to(ROOT).as_posix(), "size": sel[0]["size"] if sel else None,
            "n_problems": len(sel), "n_ok": len(ok),
            "time_s_median": statistics.median(ok) if ok else None,
            "time_s_min": min(ok) if ok else None, "time_s_max": max(ok) if ok else None,
            "per_problem": {str(r["problem_id"]): {"time_s": r["time_s"], "c_last": r["c_last"], "status": r["status"]}
                            for r in sel}}
    (ROOT / "evidence" / f"oat_retest_summary{sfx}.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
    fields = ["size", "stage", "method", "config", "problem_id", "time_s", "c_last", "status", "pcg_its_median",
              "pcg_its_max", "run"]
    with open(ROOT / "figures" / "data" / f"oat_retest_timings{sfx}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})
    for stage, s in summary["stages"].items():
        med = f"{s['time_s_median']:.3f}" if s["time_s_median"] is not None else "n/a"
        print(f"{stage:32s} n{s['size']:<4} ok {s['n_ok']}/{s['n_problems']}  median {med} s")


if __name__ == "__main__":
    main()
