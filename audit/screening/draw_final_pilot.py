"""Fix the decision-pilot order over the complete screened pool (plan/PROTOCOL.md §11, decision pilot row).

    python -m audit.screening.draw_final_pilot

Reads audit/screening/screening.csv (all sources, merged with merge_and_pilot --no-pilot). The LLM includes, sorted by
pid, are shuffled once with random.Random(20260924). Any LLM exclude that the human turned into an include is appended
in a second shuffle (seed 20260925). G1 walks this order (analysis/gates.py). Writes
audit/screening/pilot_final_order.csv; refuses to overwrite an existing order unless the LLM include set is unchanged
(the order must never be redrawn).
"""
import csv
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "audit" / "screening" / "pilot_final_order.csv"
FIELDS = ["order", "pid", "llm_code", "arxiv_id", "doi", "already_coded", "possible_duplicate_of", "title", "part"]


def main():
    csv.field_size_limit(10 ** 9)
    rows = list(csv.DictReader(open(ROOT / "audit/screening/screening.csv", encoding="utf-8")))
    # PROTOCOL §3.4 date window, applied deterministically: arXiv and OpenAlex dates are reliable; dates parsed from
    # a bibliography (source backward:BC3 only) are not, so those records are left to the screener's decision.
    def pre2017(r):
        only_bib = all(s.startswith("backward:BC3") for s in r["sources"].split(";"))
        return bool(r["date"]) and not only_bib and r["date"][:10] < "2017-01-01"
    # PROTOCOL §3.3 type: journal article, conference paper or arXiv preprint. A preprint on another server (Zenodo,
    # SSRN, Research Square, ...) is not eligible; arXiv-ness = arXiv id, an arXiv DOI (10.48550/arxiv.*) or an arXiv venue.
    pool = {r["pid"]: r for r in csv.DictReader(open(ROOT / "audit/pool/pool.csv", encoding="utf-8"))}

    def nonarxiv_preprint(r):
        p = pool[r["pid"]]
        arx = bool(p["arxiv_id"]) or p["doi"].startswith("10.48550/arxiv") or "arxiv" in p["venue"].lower()
        return p["type"] == "preprint" and not arx
    inc = sorted((r for r in rows if r["llm_decision"] == "include" and not pre2017(r) and not nonarxiv_preprint(r)),
                 key=lambda r: r["pid"])
    dropped_by_date = sorted(r["pid"] for r in rows if r["llm_decision"] == "include" and pre2017(r))
    dropped_by_type = sorted(r["pid"] for r in rows if r["llm_decision"] == "include" and not pre2017(r)
                             and nonarxiv_preprint(r))
    flips = sorted((r for r in rows if r["llm_decision"] == "exclude" and r.get("human_decision") == "include"),
                   key=lambda r: r["pid"])
    if OUT.exists():
        old = [r["pid"] for r in csv.DictReader(open(OUT, encoding="utf-8")) if r["part"] == "llm includes"]
        if sorted(old) != [r["pid"] for r in inc]:
            sys.exit("pilot_final_order.csv exists and the LLM include set changed; the order is never redrawn")
    order = list(inc)
    random.Random(20260924).shuffle(order)
    extra = list(flips)
    random.Random(20260925).shuffle(extra)
    coded = {p.stem for p in (ROOT / "audit/coding/llm_prefill").glob("P*.json")}
    dups = {}
    for d in csv.DictReader(open(ROOT / "audit/pool/possible_duplicates.csv", encoding="utf-8")):
        dups.setdefault(d["pid"], []).append(d["possible_duplicate_of"])
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for i, (r, part) in enumerate([(r, "llm includes") for r in order] + [(r, "human-added includes") for r in extra], 1):
            w.writerow({"order": i, "pid": r["pid"], "llm_code": r["llm_code"], "arxiv_id": r["arxiv_id"],
                        "doi": r["doi"], "already_coded": r["pid"] in coded,
                        "possible_duplicate_of": ";".join(dups.get(r["pid"], [])), "title": r["title"], "part": part})
    (ROOT / "audit" / "screening" / "pilot_final_date_excluded.json").write_text(
        json.dumps({"rule_3_4": "PROTOCOL §3.4: date before 2017-01-01", "pids_pre2017": dropped_by_date,
                    "rule_3_3": "PROTOCOL §3.3: preprint not on arXiv", "pids_nonarxiv_preprint": dropped_by_type},
                   indent=1), encoding="utf-8")
    print(json.dumps({"llm_includes": len(order), "llm_includes_dropped_pre2017": len(dropped_by_date),
                      "llm_includes_dropped_nonarxiv_preprint": len(dropped_by_type),
                      "human_added": len(extra),
                      "already_coded_in_first_60": sum(r["pid"] in coded for r in order[:60])}))


if __name__ == "__main__":
    main()
