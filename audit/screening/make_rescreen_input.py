"""Blind input for the AI re-screen of the sampled LLM excludes (PROTOCOL §11 screening-check row, 2026-09-24).

    python -m audit.screening.make_rescreen_input

Takes the random 10 % sample of LLM excludes in audit/screening/human_check.csv (llm_decision = exclude; seed 20260924,
drawn by merge_and_pilot.py) and writes, for each record, only the fields the first screeners saw in
audit/screening/llm_screen/input_batch_*.csv: pid, title, date, venue, type, abstract. No first-pass decision, code or
rationale is written. Output: audit/screening/rescreen/input_A.csv and input_B.csv (alternating in pid order).
Refuses to overwrite existing inputs.
"""
import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "audit" / "screening" / "rescreen"
FIELDS = ["pid", "title", "date", "venue", "type", "abstract"]


def main():
    csv.field_size_limit(10 ** 9)
    targets = [OUT / "input_A.csv", OUT / "input_B.csv"]
    if any(t.exists() for t in targets):
        sys.exit("re-screen inputs already exist; refusing to overwrite")
    check = list(csv.DictReader(open(ROOT / "audit/screening/human_check.csv", encoding="utf-8")))
    pids = sorted(r["pid"] for r in check if r["llm_decision"] == "exclude")
    pool = {r["pid"]: r for r in csv.DictReader(open(ROOT / "audit/pool/pool.csv", encoding="utf-8"))}
    missing = [p for p in pids if p not in pool]
    if missing:
        sys.exit(f"pids not in pool.csv: {missing}")
    OUT.mkdir(parents=True, exist_ok=True)
    for k, t in enumerate(targets):
        with open(t, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            for p in pids[k::2]:
                w.writerow({f: pool[p].get(f, "") for f in FIELDS})
    print(f"{len(pids)} sampled excludes -> {', '.join(t.relative_to(ROOT).as_posix() for t in targets)}")


if __name__ == "__main__":
    main()
