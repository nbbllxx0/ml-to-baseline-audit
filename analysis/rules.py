"""C1 and C4 from coding records: rule verdict rates with Clopper-Pearson 95 % CIs, by stratum.

    python -m analysis.rules                    # verified records only (decision-grade)
    python -m analysis.rules --provisional      # also LLM prefills not yet verified (labelled provisional)
    python -m analysis.rules --sensitivity      # ED4: count "partial" as fail

Writes evidence/c1_rules[_provisional].json and figures/data/rule_verdicts.csv.
"""
import argparse
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFIED_STAGES = ("human_verified", "ai_agreed", "ai_adjudicated")   # PROTOCOL §11: AI double coding replaces human checks
SAMPLE_POSITIONS = 200                                   # PROTOCOL §11: analysis sample = decision order 1-200


def sample_pids(n=SAMPLE_POSITIONS):
    f = ROOT / "audit" / "screening" / "pilot_final_order.csv"
    return {r["pid"] for r in csv.DictReader(open(f, encoding="utf-8")) if int(r["order"]) <= n} if f.exists() else set()
sys.path.insert(0, str(ROOT))

from analysis.codes import FT_CODES, ft_code  # noqa: E402


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return [None, None]
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [lo, hi]


def load(provisional, sample=None):
    """Verified records (audit/coding/records/), plus unverified prefills when provisional. `sample` = decision-order
    positions to keep (None = all coded records)."""
    recs = {}
    for f in (ROOT / "audit/coding/records").glob("P*.json"):
        r = json.loads(f.read_text(encoding="utf-8"))
        recs[r["pid"]] = r
    if provisional:
        for f in (ROOT / "audit/coding/llm_prefill").glob("P*.json"):
            r = json.loads(f.read_text(encoding="utf-8"))
            recs.setdefault(r["pid"], r)
    if sample:
        keep = sample_pids(sample)
        recs = {k: v for k, v in recs.items() if k in keep}
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provisional", action="store_true")
    ap.add_argument("--sensitivity", action="store_true")
    ap.add_argument("--all-coded", action="store_true", help="use every coded record, not only the analysis sample")
    args = ap.parse_args()
    recs = load(args.provisional, None if args.all_coded else SAMPLE_POSITIONS)
    bad = {"fail", "partial"} if args.sensitivity else {"fail"}
    out = {"n_records": len(recs), "mode": ("provisional" if args.provisional else "verified only (AI double-coded and agreed or adjudicated)"),
           "fail_set": sorted(bad), "strata": {}}
    rows = []
    for stratum in ("speed", "quality"):
        sel = [r for r in recs.values() if r["included"]["decision"] == "include" and r["included"].get("stratum") == stratum]
        n = len(sel)
        s = {"n": n}
        for k in ("R1", "R2", "R3", "R4"):
            applicable = [r for r in sel if r["rules"][k]["verdict"] != "na"]
            kk = sum(r["rules"][k]["verdict"] in bad for r in applicable)
            s[k] = {"n_applicable": len(applicable), "n_fail": kk,
                    "share": kk / len(applicable) if applicable else None,
                    "ci95": clopper_pearson(kk, len(applicable))}
        weak = sum(any(r["rules"][k]["verdict"] in bad for k in ("R1", "R2")) for r in sel)
        anyrule = sum(any(r["rules"][k]["verdict"] in bad for k in ("R1", "R2", "R3", "R4")) for r in sel)
        s["weak_R1_or_R2"] = {"k": weak, "share": weak / n if n else None, "ci95": clopper_pearson(weak, n)}
        s["any_rule"] = {"k": anyrule, "share": anyrule / n if n else None, "ci95": clopper_pearson(anyrule, n)}
        s["verified"] = sum(r.get("stage") in VERIFIED_STAGES for r in sel)
        out["strata"][stratum] = s
        for r in sel:
            rows.append({"pid": r["pid"], "stratum": stratum, "year": r["citation"].get("year"),
                         "method_family": r["included"].get("method_family"), "stage": r.get("stage"),
                         **{k: r["rules"][k]["verdict"] for k in ("R1", "R2", "R3", "R4")},
                         "claimed_speedup": r.get("claim", {}).get("claimed_speedup")})
    excluded = [ft_code(r["included"]["reason"]) for r in recs.values() if r["included"]["decision"] == "exclude"]
    out["excluded_at_full_text"] = len(excluded)
    out["excluded_by_code"] = {c: excluded.count(c) for c in FT_CODES if c in excluded}
    suffix = ("_provisional" if args.provisional else "") + ("_sensitivity" if args.sensitivity else "")
    (ROOT / "evidence" / f"c1_rules{suffix}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    if rows:
        (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
        with open(ROOT / "figures" / "data" / f"rule_verdicts{suffix}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    if not args.provisional and not args.all_coded:
        from tools.numbers import register
        sp = out["strata"]["speed"]
        def pct(d):
            return (f"{100 * d['share']:.0f} % ({d.get('k', d.get('n_fail'))}/{d.get('n_applicable', sp['n'])}; "
                    f"95 % CI {100 * d['ci95'][0]:.0f}–{100 * d['ci95'][1]:.0f} %)")
        src, scr = f"evidence/c1_rules{suffix}.json", "analysis/rules.py"
        if args.sensitivity:
            register("N012", sp["weak_R1_or_R2"]["share"], text=pct(sp["weak_R1_or_R2"]), source=src, script=scr,
                     note="speed stratum, analysis sample: share with fail or partial on R1 or R2 (ED4 sensitivity)")
        else:
            for nid, k in (("N005", "R1"), ("N006", "R2"), ("N007", "R3"), ("N008", "R4")):
                register(nid, sp[k]["share"], text=pct(sp[k]), source=src, script=scr,
                         note=f"speed stratum, analysis sample: share failing {k} among records where it applies")
            register("N009", sp["any_rule"]["share"], text=pct(sp["any_rule"]), source=src, script=scr,
                     note="speed stratum, analysis sample: share failing at least one of R1-R4")
            register("N010", sp["weak_R1_or_R2"]["share"], text=pct(sp["weak_R1_or_R2"]), source=src, script=scr,
                     note="speed stratum, analysis sample: share failing R1 or R2 (weak baseline, template-comparable)")
            w, r3 = sp["weak_R1_or_R2"], sp["R3"]         # short forms for the abstract (no interval)
            register("N088", w["share"], text=f"{w['k']} of {sp['n']} ({100 * w['share']:.0f} %)", source=src,
                     script=scr, note="short form of N010 for the abstract")
            register("N089", r3["share"], text=f"{r3['n_fail']} of {r3['n_applicable']} ({100 * r3['share']:.0f} %)",
                     source=src, script=scr, note="short form of N007 for the abstract")
        if args.sensitivity:
            w = sp["weak_R1_or_R2"]
            register("N090", w["share"], text=f"{w['k']} of {sp['n']} ({100 * w['share']:.0f} %)", source=src,
                     script=scr, note="short form of N012 for the abstract")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
