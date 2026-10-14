"""Screening-flow counts for the flow diagram (F1; N001–N004).

    python -m analysis.prisma

Counts, each read from its own file:
  * records returned per source query and source family (audit/search/raw/, excluding the quarantined FC1 results);
  * unique records after de-duplication (audit/pool/pool.csv);
  * title/abstract screening by LLM code (audit/screening/screening.csv), and the blind AI re-screen of the sampled
    excludes where available (evidence/rescreen.json; PROTOCOL §11 screening-check row);
  * full-text coding: coded, excluded by full-text code, included by stratum (coding records; verified where
    available, otherwise prefills, labelled).
Writes evidence/prisma.json and figures/data/prisma_counts.csv.
"""
import csv
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.codes import ft_code  # noqa: E402
from analysis.rules import VERIFIED_STAGES, load  # noqa: E402

NS = {"a": "http://www.w3.org/2005/Atom"}


def raw_counts():
    out = {}
    raw = ROOT / "audit" / "search" / "raw"
    for page in sorted((raw / "arxiv").glob("*/page_*.xml")):
        n = len(ET.parse(page).getroot().findall("a:entry", NS))
        out[f"arxiv:{page.parent.name}"] = out.get(f"arxiv:{page.parent.name}", 0) + n
    for sub in ("openalex", "forward", "backward"):
        for page in sorted((raw / sub).glob("*/page_*.json")):
            n = len(json.loads(page.read_text(encoding="utf-8")).get("results", []))
            out[f"{sub}:{page.parent.name}"] = out.get(f"{sub}:{page.parent.name}", 0) + n
    for f in sorted((raw / "backward").glob("*/references.json")):        # bibliography parsed from the article
        out[f"backward:{f.parent.name}"] = len(json.loads(f.read_text(encoding="utf-8"))["references"])
    return out


def main():
    csv.field_size_limit(10 ** 9)
    raw = raw_counts()
    fam = {}
    for k, v in raw.items():
        fam[k.split(":")[0]] = fam.get(k.split(":")[0], 0) + v
    pool = list(csv.DictReader(open(ROOT / "audit/pool/pool.csv", encoding="utf-8")))
    scr = list(csv.DictReader(open(ROOT / "audit/screening/screening.csv", encoding="utf-8")))
    llm = {}
    for r in scr:
        llm[r["llm_code"] or "not screened"] = llm.get(r["llm_code"] or "not screened", 0) + 1
    human = [r for r in scr if r.get("human_decision")]
    recs = load(provisional=True)
    verified = sum(1 for r in recs.values() if r.get("stage") in VERIFIED_STAGES)
    ft_ex = {}
    for r in recs.values():
        if r["included"]["decision"] == "exclude":
            c = ft_code(r["included"]["reason"])
            ft_ex[c] = ft_ex.get(c, 0) + 1
    strata = {}
    for r in recs.values():
        if r["included"]["decision"] == "include":
            s = r["included"].get("stratum")
            strata[s] = strata.get(s, 0) + 1
    out = {"records_returned_by_query": raw, "records_returned_by_family": fam,
           "records_returned_total": sum(raw.values()),
           "quarantined_not_counted": "audit/search/raw/_quarantine/ (FC1 wrong anchor, 342 records)",
           "unique_after_dedup": len(pool), "screened_llm": sum(v for k, v in llm.items() if k != "not screened"),
           "not_screened": llm.get("not screened", 0), "llm_codes": llm,
           "llm_includes": sum(v for k, v in llm.items() if k.startswith("I-")),
           "human_confirmed_screening": len(human),
           "full_text_coded": len(recs), "full_text_verified": verified,
           "full_text_excluded_by_code": ft_ex, "included_by_stratum": strata,
           "status": "provisional: coding not yet double-coded and adjudicated" if verified == 0
                     else f"{verified} records verified (AI double-coded)"}
    (ROOT / "evidence" / "prisma.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
    with open(ROOT / "figures" / "data" / "prisma_counts.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["stage", "item", "count"])
        for k, v in raw.items():
            w.writerow(["returned", k, v])
        w.writerow(["dedup", "unique records", len(pool)])
        for k, v in sorted(llm.items()):
            w.writerow(["screening (LLM)", k, v])
        for k, v in sorted(ft_ex.items()):
            w.writerow(["full text excluded", k, v])
        for k, v in sorted(strata.items(), key=lambda kv: str(kv[0])):
            w.writerow(["included", f"stratum {k}", v])
    # Search-level counts are final once all sources have run; screening and inclusion counts wait for verified records.
    # Analysis sample (decision order 1-200; PROTOCOL §11): verified records only.
    from analysis.rules import SAMPLE_POSITIONS, sample_pids
    samp = load(provisional=False, sample=SAMPLE_POSITIONS)
    eligible = len(sample_pids(10 ** 6))
    full = [r for r in samp.values() if r.get("access") == "full_text"]
    inc_full = [r for r in full if r["included"]["decision"] == "include"]
    out_sample = {"decision_order_eligible": eligible, "sample_positions": SAMPLE_POSITIONS,
                  "sample_records_coded": len(samp), "sample_full_text": len(full),
                  "sample_included_full_text": len(inc_full),
                  "sample_speed_stratum": sum(r["included"].get("stratum") == "speed" for r in inc_full),
                  "sample_quality_stratum": sum(r["included"].get("stratum") == "quality" for r in inc_full),
                  "sample_excluded_full_text": sum(r["included"]["decision"] == "exclude" for r in full)}
    out.update(out_sample)
    (ROOT / "evidence" / "prisma.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    from tools.numbers import register
    register("N001", out["records_returned_total"], text=f"{out['records_returned_total']:,}", source="evidence/prisma.json",
             script="analysis/prisma.py", note="records returned by all searches (quarantined FC1 results excluded)")
    register("N002", out["unique_after_dedup"], text=f"{out['unique_after_dedup']:,}", source="evidence/prisma.json",
             script="analysis/prisma.py", note="unique records after de-duplication (audit/pool/pool.csv)")
    if out["sample_records_coded"]:
        for nid, key, note in (("N003", "llm_includes", "records included at title/abstract screening (LLM screen)"),
                               ("N004", "decision_order_eligible", "screening includes eligible for the decision order "
                                                                  "after the §3.3 type and §3.4 date rules"),
                               ("N084", "sample_records_coded", "records in decision-order positions 1-200 not "
                                                                "paywalled per OpenAlex, each coded twice and verified"),
                               ("N085", "sample_full_text", "of those, records whose full text was read"),
                               ("N086", "sample_included_full_text", "of those, included at full text"),
                               ("N087", "sample_speed_stratum", "of those, in the speed stratum")):
            register(nid, out[key], text=f"{out[key]:,}", source="evidence/prisma.json", script="analysis/prisma.py",
                     note=note)
    print(json.dumps({k: v for k, v in out.items() if k != "records_returned_by_query"}, indent=2))


if __name__ == "__main__":
    main()
