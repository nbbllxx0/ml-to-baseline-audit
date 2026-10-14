"""Merge LLM screening batches into one sheet and draw the (provisional) pilot sample.

    python -m audit.screening.merge_and_pilot            # merge + validate + draw pilot
    python -m audit.screening.merge_and_pilot --no-pilot

Outputs:
  audit/screening/screening.csv       one row per pool record: LLM decision, code, fields, blank human columns
  audit/screening/human_check.csv     every include plus a random 10 % of excludes (seed 20260924) for human confirmation
  audit/screening/pilot_provisional.csv   20 includes drawn uniformly at random (seed 20260924), arXiv stratum
Validation: every pool pid screened exactly once; codes from the allowed list.
"""
import argparse
import csv
import glob
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEED = 20260924
ALLOWED = {"I-SPEED", "I-QUALITY", "I-UNCLEAR", "E-SCOPE", "E-DOMAIN", "E-NOML", "E-TYPE", "E-FORWARD",
           "E-MLONLY", "E-NOCLAIM", "E-OTHER"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pilot", action="store_true")
    ap.add_argument("--pilot-size", type=int, default=20)
    args = ap.parse_args()
    pool = {r["pid"]: r for r in csv.DictReader(open(ROOT / "audit/pool/pool.csv", encoding="utf-8"))}
    decisions = {}
    for f in sorted(glob.glob(str(ROOT / "audit/screening/llm_screen/batch_*.json"))):
        for d in json.loads(pathlib.Path(f).read_text(encoding="utf-8")):
            if d["pid"] in decisions:
                sys.exit(f"duplicate pid {d['pid']} in {f}")
            if d["code"] not in ALLOWED:
                sys.exit(f"bad code {d['code']} for {d['pid']}")
            if (d["decision"] == "include") != d["code"].startswith("I-"):
                sys.exit(f"decision/code mismatch for {d['pid']}")
            d["batch"] = pathlib.Path(f).stem
            decisions[d["pid"]] = d
    missing = sorted(set(pool) - set(decisions))
    extra = sorted(set(decisions) - set(pool))
    if extra:
        sys.exit(f"screened pids not in pool: {extra[:5]}")
    print(f"pool {len(pool)} | screened {len(decisions)} | missing {len(missing)}")
    fields = ["pid", "title", "date", "venue", "doi", "arxiv_id", "sources", "llm_decision", "llm_code",
              "method_family", "physics", "dim", "llm_rationale", "llm_batch", "human_decision", "human_code",
              "human_initials", "human_date"]
    rows = []
    for pid, p in pool.items():
        d = decisions.get(pid, {})
        rows.append({"pid": pid, "title": p["title"], "date": p["date"], "venue": p["venue"], "doi": p["doi"],
                     "arxiv_id": p["arxiv_id"], "sources": p["sources"], "llm_decision": d.get("decision", ""),
                     "llm_code": d.get("code", ""), "method_family": d.get("method_family", ""),
                     "physics": d.get("physics", ""), "dim": d.get("dim", ""), "llm_rationale": d.get("rationale", ""),
                     "llm_batch": d.get("batch", ""), "human_decision": "", "human_code": "", "human_initials": "",
                     "human_date": ""})
    with open(ROOT / "audit/screening/screening.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r["llm_code"]] = counts.get(r["llm_code"], 0) + 1
    print("codes:", dict(sorted(counts.items())))

    rng = random.Random(SEED)
    inc = [r for r in rows if r["llm_decision"] == "include"]
    exc = [r for r in rows if r["llm_decision"] == "exclude"]
    exc_sample = rng.sample(exc, k=max(1, round(0.10 * len(exc)))) if exc else []
    with open(ROOT / "audit/screening/human_check.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields + ["check_reason"])
        w.writeheader()
        for r in inc:
            w.writerow({**r, "check_reason": "all includes"})
        for r in exc_sample:
            w.writerow({**r, "check_reason": "10% exclude sample"})
    print(f"human check list: {len(inc)} includes + {len(exc_sample)} sampled excludes")

    if not args.no_pilot:
        eligible = sorted([r for r in inc if r["arxiv_id"]], key=lambda r: r["pid"])
        pilot = random.Random(SEED).sample(eligible, k=min(args.pilot_size, len(eligible)))
        with open(ROOT / "audit/screening/pilot_provisional.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(sorted(pilot, key=lambda r: r["pid"]))
        print(f"provisional pilot: {len(pilot)} of {len(eligible)} arXiv-stratum includes (seed {SEED})")


if __name__ == "__main__":
    main()
