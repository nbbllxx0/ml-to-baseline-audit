"""Numbers added in the pre-submission revision of the SMO v2 manuscript (reviewer-style audit, 2026-09-25).

    python -m analysis.v2_revision_numbers

All values are computed from the coding records, the pool, the decision order and frozen evidence files; N001-N152
are not touched. Writes evidence/v2_revision_extras.json and registers N153-N162.
"""
import collections
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.numbers import register  # noqa: E402

EV = ROOT / "evidence"
OUT = EV / "v2_revision_extras.json"
SCRIPT = "analysis/v2_revision_numbers.py"
SRC = "evidence/v2_revision_extras.json"


def records():
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "audit" / "coding" / "records").glob("P*.json"))]


# Journal or proceedings versions that the coded records do not name as "Version of record" but that existed before
# the search ended (24 Sep 2026). Found by the pre-submission reference audit (2026-09-25), confirmed on Crossref:
#   P00029: Computational Mechanics 78(1) 101-126, online 2026-02-05, same title and authors.
#   P00176: retitled version with a partly different author list, Engineering Optimization 54(6) 973-988 (2021);
#           its own record names it. Counted as a journal version.
KNOWN_VERSIONS = {"P00029": "10.1007/s00466-026-02749-y", "P00176": "10.1080/0305215X.2021.1902998"}


def arxiv_only(r):
    """No journal or proceedings version by the end of the search: coded as an arXiv preprint, no version of record
    named in the record, and none listed in KNOWN_VERSIONS."""
    v = r["citation"].get("venue") or ""
    return (v.lower().startswith("arxiv") and not re.search(r"Version of record", v, re.I)
            and r["pid"] not in KNOWN_VERSIONS)


def weak(r):
    return r["rules"]["R1"]["verdict"] == "fail" or r["rules"]["R2"]["verdict"] == "fail"


def main():
    recs = records()
    speed = [r for r in recs if (r.get("included") or {}).get("stratum") == "speed"]
    assert len(speed) == 28
    pre = [r for r in speed if arxiv_only(r)]
    pub = [r for r in speed if not arxiv_only(r)]
    three_d = [r for r in speed if r["included"].get("dim") in ("3d", "both")]

    coded = {r["pid"] for r in recs}
    order = list(csv.DictReader((ROOT / "audit" / "screening" / "pilot_final_order.csv").open(encoding="utf-8")))
    pool = {r["pid"]: r for r in csv.DictReader((ROOT / "audit" / "pool" / "pool.csv").open(encoding="utf-8"))}
    skipped = [r["pid"] for r in order if int(r["order"]) <= 200 and r["pid"] not in coded]
    assert len(skipped) == 90
    venues = collections.Counter((pool[p].get("venue") or "").strip() for p in skipped)

    be = json.loads((EV / "breakeven.json").read_text(encoding="utf-8"))
    ref256 = [r for r in be["rows"] if r["scenario"].startswith("OAT Table 6") and r["size"] == 256
              and r["C_SIMP_label"] == "SIMP GPU" and r["C_inf_label"] == "OAT w/ Ref"]
    assert len(ref256) == 1
    ref = ref256[0]

    extras = {"preprint_split": {"arxiv_only": {"n": len(pre), "weak": sum(map(weak, pre)), "pids": [r["pid"] for r in pre]},
                                 "with_version_of_record": {"n": len(pub), "weak": sum(map(weak, pub))}},
              "three_d": {"n": len(three_d), "pids": [r["pid"] for r in three_d]},
              "paywalled_skipped": {"n": len(skipped), "venues": dict(venues.most_common()), "pids": skipped},
              "oat_refinement_256": {"C_SIMP_s": ref["C_SIMP_s"], "C_inf_s": ref["C_inf_s"],
                                     "speedup": ref["C_SIMP_s"] / ref["C_inf_s"], "source": ref["source"]}}
    OUT.write_text(json.dumps(extras, indent=1, ensure_ascii=False), encoding="utf-8")

    reg = [("N153", extras["preprint_split"]["arxiv_only"]["weak"], "", f"{extras['preprint_split']['arxiv_only']['weak']} of {len(pre)}",
            "speed claims available only as arXiv preprints that fail R1 or R2"),
           ("N154", extras["preprint_split"]["with_version_of_record"]["weak"], "",
            f"{extras['preprint_split']['with_version_of_record']['weak']} of {len(pub)}",
            "speed claims with a journal or proceedings version that fail R1 or R2"),
           ("N155", len(three_d), "", f"{len(three_d)} of 28", "speed claims on 3D problems (coded dim 3d or both)"),
           ("N156", venues["Computer Methods in Applied Mechanics and Engineering"], "", str(venues["Computer Methods in Applied Mechanics and Engineering"]),
            "paywalled, skipped records (positions 1-200) with venue CMAME (pool venue field)"),
           ("N157", venues["Journal of Mechanical Design"], "", str(venues["Journal of Mechanical Design"]),
            "paywalled, skipped records with venue Journal of Mechanical Design"),
           ("N158", venues["Structural and Multidisciplinary Optimization"], "", str(venues["Structural and Multidisciplinary Optimization"]),
            "paywalled, skipped records with venue Structural and Multidisciplinary Optimization"),
           ("N159", venues["Engineering Applications of Artificial Intelligence"], "", str(venues["Engineering Applications of Artificial Intelligence"]),
            "paywalled, skipped records with venue Engineering Applications of Artificial Intelligence"),
           ("N160", venues[""], "", str(venues[""]), "paywalled, skipped records with no venue in the pool record"),
           ("N161", ref["C_inf_s"], "s", f"{ref['C_inf_s']:.2f} s", "OAT with refinement at 256², its own Table 6 (published)"),
           ("N162", extras["oat_refinement_256"]["speedup"], "×", f"{extras['oat_refinement_256']['speedup']:.1f}×",
            "speed-up over SIMP-GPU with refinement at 256², from OAT Table 6 (published)")]
    # Re-test candidates flagged in the final coding records (retest_candidate = true) and not attempted.
    flagged = sorted(r["pid"] for r in recs if r.get("retest_candidate") is True)
    attempted = {"P00150"}                      # the predictor of Halle et al.; HGTO (P00512) lies outside the sample
    not_attempted = [p for p in flagged if p not in attempted]
    extras["retest_candidates"] = {"flagged_in_sample": flagged, "attempted": sorted(attempted),
                                   "not_attempted": not_attempted}
    OUT.write_text(json.dumps(extras, indent=1, ensure_ascii=False), encoding="utf-8")
    reg.append(("N211", len(not_attempted), "", {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}.get(
        len(not_attempted), str(len(not_attempted))),
        "re-test candidates flagged in the final coding records of the sample and not attempted (sentence-initial)"))
    for nid, val, unit, text, note in reg:
        register(nid, val, unit=unit, text=text, source=SRC, script=SCRIPT, note=note)
        print(nid, text, "|", note)


if __name__ == "__main__":
    main()
