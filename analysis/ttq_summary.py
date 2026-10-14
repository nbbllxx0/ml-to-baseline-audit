"""Time to matched quality (display item F4; input to C3 break-even).

    python -m analysis.ttq_summary --ttq <ttq run dir> --eval evidence/oat_eval_n256.json

Per problem:
  * CE_OAT and vf_OAT: compliance error and thresholded volume fraction of OAT's generated design (no refinement),
    scored by OAT's own evaluator (retest/oat_harness/eval_designs.py; candidate "OAT");
  * CE_ours(K) and vf_ours(K): the same for our design after K iterations (time_to_quality.py score).
OAT's evaluator binarizes raw design variables at 0.5 without the filter (plan/BASELINE_PREREG.md §9), so two match
rules are reported:
  * primary (volume condition, §9 post-hoc row): CE_ours(K) <= CE_OAT and vf_ours(K) <= max(vf_target, vf_OAT);
  * pre-registered: CE_ours(K) <= CE_OAT only.
The matched time is the smallest setup-inclusive wall time over matching budgets. Each budget is a fresh run, so its
time is a real end-to-end time. A problem with no matching budget is reported as not matched; no time is imputed.
Two summaries per rule:
  * median matched time over matched problems only (as first coded);
  * median per-problem ratio (our matched time / OAT's inference time on that problem), with unmatched problems
    ranked above every matched one (right-censored at our 150-iteration time). The median is reported only when it
    falls on a matched problem; it uses all problems without imputing a time (BASELINE_PREREG §9 row of 2026-09-24).
Writes evidence/ttq_summary.json (keyed "<size>_<solver>") and figures/data/ttq_curves_n<size>_<solver>.csv.
"""
import argparse
import csv
import json
import pathlib
import statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]
RULES = {"primary_ce_and_volume": lambda r, ce, vf_cap: r["CE_pct"] <= ce and r["vf_thresholded"] <= vf_cap,
         "preregistered_ce_only": lambda r, ce, vf_cap: r["CE_pct"] <= ce}


def summarize(runs_all, pid, ce_oat, vf_cap, rule):
    runs = sorted((r for r in runs_all if r["problem_id"] == pid), key=lambda r: r["iters"])
    match = next((r for r in runs if ce_oat is not None and RULES[rule](r, ce_oat, vf_cap)), None)
    return {"matched": match is not None, "matched_iters": match["iters"] if match else None,
            "matched_wall_incl_setup_s": match["wall_incl_setup_s"] if match else None,
            "matched_loop_s": match["loop_s"] if match else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ttq", required=True, help="time-to-quality run dir (holds ttq.json)")
    ap.add_argument("--eval", required=True, help="evidence/oat_eval_n<size>.json")
    args = ap.parse_args()
    ttq_dir = ROOT / args.ttq
    ttq = json.loads((ttq_dir / "ttq.json").read_text(encoding="utf-8"))
    meta = json.loads((ttq_dir / "ttq_runs.json").read_text(encoding="utf-8"))
    solver = meta.get("solver", "gpu")
    ev = {e["problem_id"]: e for e in json.loads((ROOT / args.eval).read_text(encoding="utf-8"))}
    summ = json.loads((ROOT / "evidence" / "oat_retest_summary.json").read_text(encoding="utf-8"))["stages"]
    size = meta["size"]
    inf_median = summ[f"OAT inference {size}"]["time_s_median"]
    per_problem, curves = [], []
    for pid in meta["problem_ids"]:
        cands = ev[pid]["candidates"]
        oat = cands.get("OAT")
        ce_oat = oat["CE_pct"] if oat else None
        vf_cap = max(ev[pid]["vf_target"], oat["vf_thresholded"]) if oat else None
        runs = sorted((r for r in ttq if r["problem_id"] == pid), key=lambda r: r["iters"])
        for r in runs:
            curves.append({"size": size, "solver": solver, "problem_id": pid, "iters": r["iters"],
                           "wall_incl_setup_s": r["wall_incl_setup_s"], "loop_s": r["loop_s"], "CE_pct": r["CE_pct"],
                           "vf_thresholded": r["vf_thresholded"], "CE_OAT_pct": ce_oat,
                           "vf_OAT": oat["vf_thresholded"] if oat else None, "vf_target": ev[pid]["vf_target"]})
        per_problem.append({"problem_id": pid, "CE_OAT_pct": ce_oat, "vf_OAT": oat["vf_thresholded"] if oat else None,
                            "vf_target": ev[pid]["vf_target"], "vf_cap": vf_cap,
                            "CE_OAT_SIMP_pct": {k: v["CE_pct"] for k, v in cands.items() if k.startswith("OAT-SIMP")},
                            "CE_ours_150_pct": runs[-1]["CE_pct"] if runs else None,
                            "wall_150_incl_setup_s": runs[-1]["wall_incl_setup_s"] if runs else None,
                            **{rule: summarize(ttq, pid, ce_oat, vf_cap, rule) for rule in RULES}})
    w150 = [p["wall_150_incl_setup_s"] for p in per_problem if p["wall_150_incl_setup_s"] is not None]
    w150_med = statistics.median(w150) if w150 else None
    out = {"size": size, "solver": solver, "ttq_run": args.ttq, "eval": args.eval, "n_problems": len(per_problem),
           "oat_inference_median_s": inf_median, "per_problem": per_problem, "rules": {}, "breakeven_inputs": [],
           "wall_150_incl_setup_median_s": w150_med,
           "wall_150_incl_setup_range_s": [min(w150), max(w150)] if w150 else None,
           "ratio_150_incl_setup_over_oat": (w150_med / inf_median) if w150_med else None,
           "note_150": "fresh 150-iteration run per problem, setup included (BASELINE_PREREG §9, setup row); "
                       "ratio = median of ours / median of OAT inference"}
    if w150_med is not None:
        out["breakeven_inputs"].append({
            "scenario": "same machine, 150 iterations incl. setup", "size": size,
            "C_SIMP_label": f"ours {solver}, 150 its incl. setup (median of {len(w150)})", "C_SIMP_s": w150_med,
            "C_inf_label": "OAT inference, no Ref (median of 5)", "C_inf_s": inf_median,
            "hardware": "RTX 5090 / i5-14600KF (this study)"})
    inf_by_pid = {int(k): v["time_s"] for k, v in summ[f"OAT inference {size}"]["per_problem"].items()}
    for rule in RULES:
        matched = [p[rule] for p in per_problem if p[rule]["matched"]]
        med = statistics.median(m["matched_wall_incl_setup_s"] for m in matched) if matched else None
        ratios = sorted((p[rule]["matched_wall_incl_setup_s"] / inf_by_pid[p["problem_id"]]) if p[rule]["matched"]
                        else float("inf") for p in per_problem)
        n = len(ratios)
        mid = [ratios[n // 2]] if n % 2 else [ratios[n // 2 - 1], ratios[n // 2]]
        ratio_med = sum(mid) / len(mid) if all(m != float("inf") for m in mid) else None
        out["rules"][rule] = {"n_matched": len(matched), "matched_time_median_s": med,
                              "median_note": ("all problems matched" if len(matched) == len(per_problem)
                                              else f"median over the {len(matched)} matched problems only"),
                              "ratio_ours_over_oat_sorted": [None if r == float("inf") else r for r in ratios],
                              "ratio_median_censored": ratio_med,
                              "ratio_note": "unmatched problems ranked as slowest (None in the sorted list); "
                                            "median undefined (null) if it falls on an unmatched problem"}
        tag = "primary" if rule.startswith("primary") else "pre-registered rule"
        if ratio_med is not None:           # conservative: C_SIMP = censored median ratio x OAT's median time
            out["breakeven_inputs"].append({
                "scenario": f"same machine, matched quality ({tag}, censored median ratio)", "size": size,
                "C_SIMP_label": f"ours {solver}: median ratio {ratio_med:.3f} x OAT time ({len(matched)}/{len(per_problem)} matched)",
                "C_SIMP_s": ratio_med * inf_median, "C_inf_label": "OAT inference, no Ref (median of 5)",
                "C_inf_s": inf_median, "hardware": "RTX 5090 / i5-14600KF (this study)"})
        if med is not None:
            out["breakeven_inputs"].append({
                "scenario": f"same machine, matched quality ({tag}, matched problems only)", "size": size,
                "C_SIMP_label": f"ours {solver}, median over {len(matched)}/{len(per_problem)} matched problems",
                "C_SIMP_s": med, "C_inf_label": "OAT inference, no Ref (median of 5)", "C_inf_s": inf_median,
                "hardware": "RTX 5090 / i5-14600KF (this study)"})
    out_file = ROOT / "evidence" / "ttq_summary.json"
    prev = json.loads(out_file.read_text(encoding="utf-8")) if out_file.exists() else {}
    prev = {k: v for k, v in prev.items() if k != "breakeven_inputs" and "_" in k}      # drop keys of older layouts
    prev[f"{size}_{solver}"] = out
    prev["breakeven_inputs"] = [b for k, v in prev.items() if k != "breakeven_inputs" for b in v["breakeven_inputs"]]
    out_file.write_text(json.dumps(prev, indent=1), encoding="utf-8")
    (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
    with open(ROOT / "figures" / "data" / f"ttq_curves_n{size}_{solver}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(curves[0]))
        w.writeheader()
        w.writerows(curves)
    for p in per_problem:
        parts = []
        for rule in RULES:
            m = p[rule]
            parts.append(f"{rule.split('_')[0]}: " + (f"K={m['matched_iters']} {m['matched_wall_incl_setup_s']:.3f} s"
                                                      if m["matched"] else "not matched"))
        print(f"problem {p['problem_id']}: CE_OAT {p['CE_OAT_pct']:.2f} % (vf {p['vf_OAT']:.3f}, cap {p['vf_cap']:.3f}), "
              f"ours@150 {p['CE_ours_150_pct']:.2f} %; " + "; ".join(parts))
    for rule, r in out["rules"].items():
        print(f"n{size} {solver} {rule}: matched {r['n_matched']}/{len(per_problem)}; median time {r['matched_time_median_s']}; "
              f"OAT inference {inf_median}; ratio median (censored) {r['ratio_median_censored']}; "
              f"sorted ratios {[None if x is None else round(x, 3) for x in r['ratio_ours_over_oat_sorted']]}")


if __name__ == "__main__":
    main()
