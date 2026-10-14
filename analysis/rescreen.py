"""Estimated false-exclusion rate of title/abstract screening (PROTOCOL §11 screening-check row, 2026-09-24).

    python -m analysis.rescreen

The random 10 % sample of LLM excludes (audit/screening/human_check.csv, seed 20260924) was re-screened blind by a
different model from the fields in audit/screening/rescreen/input_{A,B}.csv. Each output
audit/screening/rescreen/rescreen_{A,B}.json holds one {pid, decision, code, rationale} per input row.
Reported: the share of sampled excludes that the re-screen includes (the disagreement rate, reported as the estimated
false-exclusion rate), with a Clopper-Pearson 95 % CI; the implied number among all LLM excludes; and code agreement
where both screens exclude. Secondary: how many re-screen includes would also pass the §3.3/§3.4 draw rules. Writes
evidence/rescreen.json; registers N066 and N067.
"""
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.rules import clopper_pearson  # noqa: E402

DIR = ROOT / "audit" / "screening" / "rescreen"
INCLUDE = {"I-SPEED", "I-QUALITY", "I-UNCLEAR"}
EXCLUDE = {"E-SCOPE", "E-DOMAIN", "E-NOML", "E-TYPE", "E-FORWARD", "E-MLONLY", "E-NOCLAIM", "E-OTHER"}


def main():
    csv.field_size_limit(10 ** 9)
    first = {r["pid"]: r for r in csv.DictReader(open(ROOT / "audit/screening/human_check.csv", encoding="utf-8"))
             if r["llm_decision"] == "exclude"}
    second = {}
    for k in "AB":
        wanted = [r["pid"] for r in csv.DictReader(open(DIR / f"input_{k}.csv", encoding="utf-8"))]
        got = json.loads((DIR / f"rescreen_{k}.json").read_text(encoding="utf-8"))
        ids = [g["pid"] for g in got]
        if sorted(ids) != sorted(wanted) or len(set(ids)) != len(ids):
            sys.exit(f"rescreen_{k}.json does not match input_{k}.csv one to one")
        for g in got:
            ok = (g["decision"] == "include" and g["code"] in INCLUDE) or (g["decision"] == "exclude" and g["code"] in EXCLUDE)
            if not ok:
                sys.exit(f"{g['pid']}: invalid decision/code {g['decision']!r}/{g['code']!r}")
            second[g["pid"]] = g
    if sorted(second) != sorted(first):
        sys.exit("re-screened pids differ from the sampled excludes in human_check.csv")
    n = len(second)
    flips = sorted(p for p, g in second.items() if g["decision"] == "include")
    both_ex = [p for p in second if p not in flips]
    same_code = sum(1 for p in both_ex if second[p]["code"] == first[p]["llm_code"])
    scr = list(csv.DictReader(open(ROOT / "audit/screening/screening.csv", encoding="utf-8")))
    n_excl = sum(1 for r in scr if r["llm_decision"] == "exclude")
    rate, ci = len(flips) / n, clopper_pearson(len(flips), n)
    # Secondary: re-screen includes that would also pass the draw rules of audit/screening/draw_final_pilot.py
    # (§3.4 date window; §3.3 type), i.e. that would have entered the decision order. Same logic, restated here.
    pool = {r["pid"]: r for r in csv.DictReader(open(ROOT / "audit/pool/pool.csv", encoding="utf-8"))}
    by_pid = {r["pid"]: r for r in scr}

    def eligible(pid):
        r, p = by_pid[pid], pool[pid]
        only_bib = all(s.startswith("backward:BC3") for s in r["sources"].split(";"))
        pre2017 = bool(r["date"]) and not only_bib and r["date"][:10] < "2017-01-01"
        arx = bool(p["arxiv_id"]) or p["doi"].startswith("10.48550/arxiv") or "arxiv" in p["venue"].lower()
        return not pre2017 and not (p["type"] == "preprint" and not arx)
    flips_eligible = [p for p in flips if eligible(p)]
    out = {"n_sampled_excludes": n, "rescreen_includes": len(flips), "disagreement_rate": rate, "ci95": ci,
           "rescreen_includes_eligible_at_draw": len(flips_eligible),
           "eligible_rate": len(flips_eligible) / n, "eligible_ci95": clopper_pearson(len(flips_eligible), n),
           "all_llm_excludes": n_excl, "implied_false_exclusions": round(rate * n_excl),
           "implied_false_exclusions_ci95": [round(ci[0] * n_excl), round(ci[1] * n_excl)],
           "both_exclude": len(both_ex), "both_exclude_same_code": same_code,
           "rescreen_include_codes": {c: sum(1 for p in flips if second[p]["code"] == c) for c in sorted(INCLUDE)},
           "disagreements": [{"pid": p, "title": first[p]["title"], "first": first[p]["llm_code"],
                              "rescreen": second[p]["code"], "rescreen_rationale": second[p]["rationale"]} for p in flips],
           "note": "disagreement rate = share of sampled LLM excludes that the blind re-screen includes; reported as the "
                   "estimated false-exclusion rate (PROTOCOL §11). Not adjudicated."}
    (ROOT / "evidence" / "rescreen.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    from tools.numbers import register
    register("N066", rate, text=f"{100 * rate:.0f} % ({len(flips)}/{n}; 95 % CI {100 * ci[0]:.0f}–{100 * ci[1]:.0f} %)",
             source="evidence/rescreen.json", script="analysis/rescreen.py",
             note="estimated false-exclusion rate: share of sampled LLM excludes that a blind re-screen by a different model includes")
    register("N067", out["implied_false_exclusions"], text=f"about {out['implied_false_exclusions']} "
             f"(95 % CI {out['implied_false_exclusions_ci95'][0]}–{out['implied_false_exclusions_ci95'][1]})",
             source="evidence/rescreen.json", script="analysis/rescreen.py",
             note=f"implied number of screening false exclusions among all {n_excl} LLM excludes")
    print(json.dumps({k: v for k, v in out.items() if k != "disagreements"}, indent=2))
    for d in out["disagreements"]:
        print(d["pid"], d["first"], "->", d["rescreen"], "|", d["title"][:90])


if __name__ == "__main__":
    main()
