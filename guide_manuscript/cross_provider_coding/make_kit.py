"""Build the blinded cross-provider coding kit in kit/ from the inputs of the original blind second pass.

    python guide_manuscript/cross_provider_coding/make_kit.py [--agents 10] [--force]

The kit repeats the second pass (PROTOCOL §11, 2026-09-24) with coders from other model providers. It holds only what
the second-pass coders saw: the pid-masked protocol, the coding schema, the screening and full-text exclusion codes, and
queue lines with bibliographic data. No coding result of any pass enters the kit.

Written into kit/ (the two instruction files there are hand-written and are not touched):
  PROTOCOL_masked.md    byte copy of audit/coding/second_pass/_inputs/PROTOCOL_pids_masked.md
  coding_schema.json    audit/schema/coding_schema.json with "cross_provider_pass" added to the stage values
  screening_codes.md    byte copy of audit/schema/screening_codes.md
  queues/queue_NN.txt   the 110 coded records of the analysis sample, interleaved by decision order over the agents,
                        in the second pass's line format (audit/coding/make_queues.py)
  referrals.csv         the 17 records that the blind title/abstract re-screen referred for a full-text read
                        (evidence/rescreen.json), with the fields the screeners saw plus DOI and arXiv id
  MANIFEST.sha256       SHA-256 of every kit file, to confirm that a copy handed to an agent is unchanged
Reads the repository only; writes only inside this folder. Refuses to overwrite generated files without --force.
"""
import argparse
import csv
import hashlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KIT = HERE / "kit"
HAND_WRITTEN = ("AGENT_INSTRUCTIONS.md", "REFERRAL_INSTRUCTIONS.md")
STAGE = "cross_provider_pass"


def queue_line(r):
    """Identical to audit/coding/make_queues.py line(), so the coders see what the second-pass coders saw."""
    return (f"- {r['pid']} (decision order {r['order']}): \"{r['title']}\" | DOI {r['doi'] or 'none'} | "
            f"arXiv {r['arxiv_id'] or 'none'} | open copy per OpenAlex: {r['oa_url'] or '(find by title)'} | "
            f"access check: {r['accessible']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", type=int, default=10, help="number of queue files")
    ap.add_argument("--force", action="store_true", help="rebuild generated files that exist already")
    args = ap.parse_args()
    csv.field_size_limit(10 ** 9)
    generated = [KIT / "PROTOCOL_masked.md", KIT / "coding_schema.json", KIT / "screening_codes.md",
                 KIT / "referrals.csv", KIT / "MANIFEST.sha256", KIT / "queues"]
    if any(p.exists() for p in generated) and not args.force:
        sys.exit("kit files exist already; use --force to rebuild them")
    for name in HAND_WRITTEN:
        if not (KIT / name).is_file():
            sys.exit(f"missing hand-written kit file {KIT / name}")
    if (KIT / "queues").exists():
        shutil.rmtree(KIT / "queues")
    (KIT / "queues").mkdir(parents=True)

    shutil.copyfile(ROOT / "audit/coding/second_pass/_inputs/PROTOCOL_pids_masked.md", KIT / "PROTOCOL_masked.md")
    shutil.copyfile(ROOT / "audit/schema/screening_codes.md", KIT / "screening_codes.md")
    schema = json.loads((ROOT / "audit/schema/coding_schema.json").read_text(encoding="utf-8"))
    stage = schema["properties"]["stage"]
    stage["enum"] = stage["enum"] + [STAGE]
    stage["description"] += f"; {STAGE} = blind coding pass by a model from another provider (cross-provider check)"
    (KIT / "coding_schema.json").write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # the 110 coded records of the analysis sample; only their pids are read from the final records
    pids = {p.stem for p in (ROOT / "audit/coding/records").glob("P*.json")}
    order = {r["pid"]: r for r in csv.DictReader(open(ROOT / "audit/coding/access_final_order.csv", encoding="utf-8"))}
    missing = sorted(pids - set(order))
    if missing:
        sys.exit(f"coded records missing from access_final_order.csv: {missing}")
    rows = sorted((order[p] for p in pids), key=lambda r: int(r["order"]))
    if len(rows) != 110:
        sys.exit(f"expected 110 coded records, found {len(rows)}")
    for k in range(args.agents):
        part = rows[k::args.agents]
        (KIT / "queues" / f"queue_{k + 1:02d}.txt").write_text("\n".join(queue_line(r) for r in part) + "\n",
                                                               encoding="utf-8")
    print(f"{len(rows)} records in {args.agents} queues")

    # the 17 re-screen referrals, with the screening fields and identifiers only (no decision, code or rationale)
    ref = [d["pid"] for d in json.loads((ROOT / "evidence/rescreen.json").read_text(encoding="utf-8"))["disagreements"]]
    seen = {}
    for k in "AB":
        for r in csv.DictReader(open(ROOT / f"audit/screening/rescreen/input_{k}.csv", encoding="utf-8")):
            seen[r["pid"]] = r
    pool = {r["pid"]: r for r in csv.DictReader(open(ROOT / "audit/pool/pool.csv", encoding="utf-8"))}
    if len(ref) != 17 or any(p not in seen or p not in pool for p in ref):
        sys.exit("referral pids do not match the re-screen inputs and the pool")
    with open(KIT / "referrals.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pid", "title", "date", "venue", "type", "doi", "arxiv_id", "abstract"])
        for p in sorted(ref):
            s, q = seen[p], pool[p]
            w.writerow([p, s["title"], s["date"], s["venue"], s["type"], q["doi"], q["arxiv_id"], s["abstract"]])
    print(f"{len(ref)} referrals")

    files = sorted(f for f in KIT.rglob("*") if f.is_file() and f.name != "MANIFEST.sha256")
    lines = [f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(KIT).as_posix()}" for f in files]
    with open(KIT / "MANIFEST.sha256", "w", encoding="utf-8", newline="\n") as fh:   # LF, so `sha256sum -c` reads it
        fh.write("\n".join(lines) + "\n")
    print(f"MANIFEST.sha256: {len(lines)} files")


if __name__ == "__main__":
    main()
