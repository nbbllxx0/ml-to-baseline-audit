"""HGTO re-test summary (plan/BASELINE_PREREG.md §9, HGTO re-test row; target P00512).

    python -m analysis.hgto_summary          # run in conda env `hgto` (uses hgto.evaluation for the common scoring)

Per configuration and method (oc2 = HGTO's SIMP-OC as released, 2 threads; oc6 = the same, 6 threads; hgto_gpu = HGTO
as released on the GPU; ours = our GPU port of the same SIMP-OC):
  * timed runs: r1-r3 after a discarded warm-up r0, or r0 alone if it took more than 300 s (pre-registered rule);
    wall_s median, min and max (the target's own timing scope);
  * quality: compliance and volume of each timed design from the target's own independent evaluator
    (hgto.evaluation.evaluate_design: scikit-fem, SuperLU), with the spread over repeats;
  * primary: converged-to-converged wall-time ratios against HGTO on the GPU;
  * secondary (matched quality): per timed repeat of `ours`, the elapsed time at the first final-stage update whose
    compliance is at most HGTO's evaluated compliance with |volume error| <= 1e-7, plus that run's final-evaluation
    time; the median over repeats;
  * the article's own values (benchmarks/reference/linear.csv in the target repository), labelled separately.
Writes evidence/hgto_retest.json and figures/data/hgto_retest.csv; registers N068-N076.
"""
import csv
import json
import math
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RUNS = ROOT / "retest" / "runs" / "hgto"
REF = ROOT / "retest" / "targets" / "HGTO" / "benchmarks" / "reference" / "linear.csv"
CONFIGS = ["cantilever_120x40", "half_mbb", "inclined_cantilever", "cantilever_240x80", "cantilever_480x160",
           "cantilever_960x320"]
METHODS = ["hgto_gpu", "oc2", "oc6", "ours"]
LONG_S = 300.0


def timed_dirs(method, config):
    base = RUNS / method / config
    r0 = json.loads((base / "r0" / "result.json").read_text(encoding="utf-8"))
    if r0["wall_s"] > LONG_S:
        return [base / "r0"]
    return [base / f"r{k}" for k in (1, 2, 3)]


def matched_time(run_dir, c_target):
    res = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    hist = json.loads((run_dir / "history.json").read_text(encoding="utf-8"))
    last_stage = max(h["stage"] for h in hist)
    for h in hist:
        if h["stage"] == last_stage and h["C"] <= c_target and abs(h["volume"] - res["target_volume"]) <= 1e-7:
            return h["elapsed_s"] + res["validation_s"], h["iteration"]
    return None, None


def main():
    from hgto.evaluation import evaluate_design
    published = {}
    for r in csv.DictReader(open(REF, encoding="utf-8")):
        published.setdefault(r["case"].split("/")[-1], {})[r["method"]] = {
            "compliance": float(r["compliance"]), "wall_s": float(r["wall_s"]), "termination": r["termination"]}
    out = {"configs": {}, "note": "same machine: RTX 5090, i5-14600KF (6 P-cores), pinned; article: RTX 6000 Ada, "
                                  "Threadripper PRO 5995WX with two threads; published and measured values are never "
                                  "mixed in one ratio"}
    rows = []
    for c in CONFIGS:
        entry = {"published": {"hgto_s": published[c]["HGTO"]["wall_s"], "oc_s": published[c]["SIMP-OC"]["wall_s"],
                               "hgto_C": published[c]["HGTO"]["compliance"], "oc_C": published[c]["SIMP-OC"]["compliance"],
                               "oc_over_hgto": published[c]["SIMP-OC"]["wall_s"] / published[c]["HGTO"]["wall_s"]},
                 "measured": {}}
        for m in METHODS:
            dirs = timed_dirs(m, c)
            res = [json.loads((d / "result.json").read_text(encoding="utf-8")) for d in dirs]
            ev = [evaluate_design(d) for d in dirs]
            walls = [r["wall_s"] for r in res]
            comps = [e["compliance"] for e in ev]
            entry["measured"][m] = {"repeats": len(dirs), "wall_s_median": statistics.median(walls),
                                    "wall_s_min": min(walls), "wall_s_max": max(walls),
                                    "compliance": statistics.median(comps),
                                    "compliance_spread": max(comps) - min(comps),
                                    "volume": statistics.median(e["volume"] for e in ev),
                                    "updates": [r.get("state_evaluations") or r.get("updates") for r in res],
                                    "termination": sorted({str(r.get("termination")) for r in res}),
                                    "runs": [d.relative_to(ROOT).as_posix() for d in dirs]}
        me = entry["measured"]
        h = me["hgto_gpu"]["wall_s_median"]
        entry["ratios_vs_hgto_gpu"] = {m: me[m]["wall_s_median"] / h for m in ("oc2", "oc6", "ours")}
        entry["compliance_hgto_over_ours"] = me["hgto_gpu"]["compliance"] / me["ours"]["compliance"]
        mt = [matched_time(d, me["hgto_gpu"]["compliance"]) for d in timed_dirs("ours", c)]
        times = [t for t, _ in mt if t is not None]
        entry["matched_quality_ours"] = {"target_compliance": me["hgto_gpu"]["compliance"],
                                         "time_s_median": statistics.median(times) if len(times) == len(mt) else None,
                                         "update": [i for _, i in mt],
                                         "ratio_vs_hgto_gpu": (statistics.median(times) / h) if len(times) == len(mt) else None}
        out["configs"][c] = entry
        for m in METHODS:
            rows.append({"config": c, "method": m, "wall_s_median": me[m]["wall_s_median"], "wall_s_min": me[m]["wall_s_min"],
                         "wall_s_max": me[m]["wall_s_max"], "compliance": me[m]["compliance"], "repeats": me[m]["repeats"]})
        rows.append({"config": c, "method": "published_hgto", "wall_s_median": entry["published"]["hgto_s"],
                     "compliance": entry["published"]["hgto_C"]})
        rows.append({"config": c, "method": "published_oc", "wall_s_median": entry["published"]["oc_s"],
                     "compliance": entry["published"]["oc_C"]})
    (ROOT / "evidence" / "hgto_retest.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
    with open(ROOT / "figures" / "data" / "hgto_retest.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["config", "method", "wall_s_median", "wall_s_min", "wall_s_max",
                                           "compliance", "repeats"])
        w.writeheader()
        w.writerows(rows)
    from tools.numbers import register
    src, scr = "evidence/hgto_retest.json", "analysis/hgto_summary.py"
    for nid, c in (("N068", "cantilever_480x160"), ("N069", "cantilever_960x320")):
        e = out["configs"][c]
        register(nid, e["ratios_vs_hgto_gpu"]["oc2"], unit="×", text=f"{e['ratios_vs_hgto_gpu']['oc2']:.1f}×",
                 source=src, script=scr, note=f"HGTO speed-up over its own two-thread SIMP-OC, same machine, {c} "
                                              f"(article: {e['published']['oc_over_hgto']:.1f}×)")
    for nid, c in (("N070", "cantilever_480x160"), ("N071", "cantilever_960x320")):
        e = out["configs"][c]
        register(nid, e["ratios_vs_hgto_gpu"]["oc6"], unit="×", text=f"{e['ratios_vs_hgto_gpu']['oc6']:.1f}×",
                 source=src, script=scr, note=f"six-thread SIMP-OC wall time / HGTO GPU wall time, {c}")
    for nid, c in (("N072", "cantilever_480x160"), ("N073", "cantilever_960x320")):
        e = out["configs"][c]
        v = 1.0 / e["ratios_vs_hgto_gpu"]["ours"]
        register(nid, v, unit="×", text=f"{v:.1f}×", source=src, script=scr,
                 note=f"HGTO GPU wall time / wall time of the GPU port of the same SIMP-OC, {c} (above 1: the port "
                      f"is faster)")
    e = out["configs"]["cantilever_960x320"]
    gap = 100 * (e["compliance_hgto_over_ours"] - 1)
    register("N074", gap, unit="%", text=f"{gap:.1f} %", source=src, script=scr,
             note="HGTO compliance above the GPU SIMP-OC port's, common independent evaluator, cantilever_960x320")
    v = e["matched_quality_ours"]["ratio_vs_hgto_gpu"]
    if v is not None:
        register("N075", 1.0 / v, unit="×", text=f"{1.0 / v:.1f}×", source=src, script=scr,
                 note="HGTO GPU wall time / time of the GPU SIMP-OC port to reach HGTO's compliance, cantilever_960x320")
    gate = json.loads((ROOT / "evidence" / "hgto_gate.json").read_text(encoding="utf-8"))
    worst = max([v["max_relative_difference"] for v in gate["per_update_first_50"].values()]
                + [v["relative_difference"] for v in gate["final"].values()])
    exp = math.ceil(math.log10(worst))
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    register("N076", worst, text=f"10{str(exp).translate(sup)}", source="evidence/hgto_gate.json", script=scr,
             note="largest relative compliance difference between the GPU port and HGTO's SIMP-OC (first 50 updates "
                  "on the 120x40 problems; final compliance on all six); the gate also found equal update counts")
    print(json.dumps({c: {"published_oc_over_hgto": round(e["published"]["oc_over_hgto"], 2),
                          "ratios_vs_hgto_gpu": {k: round(v, 3) for k, v in e["ratios_vs_hgto_gpu"].items()},
                          "C": {m: round(e["measured"][m]["compliance"], 4) for m in METHODS},
                          "matched": e["matched_quality_ours"]["ratio_vs_hgto_gpu"]}
                      for c, e in out["configs"].items()}, indent=1))


if __name__ == "__main__":
    main()
