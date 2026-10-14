"""Reporting indicators (claim C4; plan/PROTOCOL.md §6; N027–N034).

    python -m analysis.reporting                 # verified records only (decision-grade)
    python -m analysis.reporting --provisional   # also unverified LLM prefills (labelled provisional)

Per indicator: counts of each recorded value among included articles (both strata; speed stratum separately for the
runtime indicators), with Clopper-Pearson 95 % CIs for the headline share. Also the direction split (outperform /
underperform / mixed) and the ML-only tallies (screening E-MLONLY; full text FT-MLONLY).
Writes evidence/reporting[_provisional].json and figures/data/reporting[_provisional].csv. Numbers are registered only
in verified mode.
"""
import argparse
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.codes import ft_code  # noqa: E402
from analysis.rules import SAMPLE_POSITIONS, clopper_pearson, load  # noqa: E402

# indicator -> (value counted as the headline share, strata it applies to, registry id)
INDICATORS = {"ood_test": ("yes", ("speed", "quality"), "N031"),
              "seeds_or_variance": ("yes", ("speed", "quality"), "N030"),
              "failure_rate_reported": ("yes", ("speed", "quality"), "N029"),
              "timing_protocol_stated": ("yes", ("speed",), None),
              "runtimes_all_cases": ("selective", ("speed",), "N028"),
              "code_available": ("yes", ("speed", "quality"), "N032"),
              "data_available": ("yes", ("speed", "quality"), "N033"),
              "hardware_per_method_stated": ("yes", ("speed",), "N034")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provisional", action="store_true")
    args = ap.parse_args()
    recs = load(args.provisional, SAMPLE_POSITIONS)
    inc = [r for r in recs.values() if r["included"]["decision"] == "include"]
    out = {"mode": "provisional" if args.provisional else "verified only (AI double-coded and agreed or adjudicated)", "n_included": len(inc),
           "indicators": {}, "direction": {}, "ml_only": {}}
    rows = []
    for key, (hit, strata, _) in INDICATORS.items():
        sel = [r for r in inc if r["included"].get("stratum") in strata]
        vals = [(r.get("reporting") or {}).get(key) for r in sel]
        counts = {}
        for v in vals:
            counts[str(v)] = counts.get(str(v), 0) + 1
        k = sum(1 for v in vals if v == hit)
        out["indicators"][key] = {"strata": list(strata), "n": len(sel), "counts": counts, "headline_value": hit,
                                  "k": k, "share": k / len(sel) if sel else None, "ci95": clopper_pearson(k, len(sel))}
        rows.append({"indicator": key, "strata": "+".join(strata), "n": len(sel), "headline_value": hit, "k": k,
                     "share": k / len(sel) if sel else ""})
    dirs = [(r.get("claim") or {}).get("direction") for r in inc]
    for d in ("outperform", "underperform", "similar_or_mixed"):
        out["direction"][d] = sum(1 for x in dirs if x == d)
    n_dir = sum(out["direction"].values())
    out["direction"]["share_outperform"] = out["direction"]["outperform"] / n_dir if n_dir else None
    out["direction"]["ci95_outperform"] = clopper_pearson(out["direction"]["outperform"], n_dir)
    ft = [ft_code(r["included"]["reason"]) for r in recs.values() if r["included"]["decision"] == "exclude"]
    out["ml_only"]["full_text_FT_MLONLY"] = ft.count("FT-MLONLY")
    scr = ROOT / "audit" / "screening" / "screening.csv"
    if scr.exists():
        csv.field_size_limit(10 ** 9)
        out["ml_only"]["screening_E_MLONLY_llm"] = sum(1 for r in csv.DictReader(open(scr, encoding="utf-8"))
                                                      if r["llm_code"] == "E-MLONLY")
    sfx = "_provisional" if args.provisional else ""
    (ROOT / "evidence" / f"reporting{sfx}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
    with open(ROOT / "figures" / "data" / f"reporting{sfx}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    if not args.provisional and inc:
        from tools.numbers import register
        s = out["direction"]["share_outperform"]
        register("N027", s, text=f"{100 * s:.0f} %", source="evidence/reporting.json", script="analysis/reporting.py",
                 note="share of included articles whose primary outcome claims to outperform")
        for key, (_, _, nid) in INDICATORS.items():
            v = out["indicators"][key]
            if nid and v["share"] is not None:
                register(nid, v["share"], text=f"{100 * v['share']:.0f} % ({v['k']}/{v['n']})",
                         source="evidence/reporting.json", script="analysis/reporting.py",
                         note=f"{key} = {v['headline_value']} among included ({'+'.join(v['strata'])})")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
