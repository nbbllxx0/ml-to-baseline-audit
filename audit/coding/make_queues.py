"""Coding queues for agents, from the decision order and the access lookup.

    python -m audit.coding.make_queues wave3 --first 162 --last 200 --agents 2 --prefix E
    python -m audit.coding.make_queues second --last 200 --agents 9 --prefix S --tag a --skip audit/coding/queue_wave3.json
    python -m audit.coding.make_queues second --last 200 --agents 2 --prefix T --tag b --only audit/coding/queue_wave3.json

wave3:  uncoded records at decision-order positions first..last whose access check is "yes" or "unknown"
        (paywalled records are skipped under the pre-registered rule unless the user supplies them).
second: every record at positions first..last that has a first-pass coding (audit/coding/llm_prefill/), for the blind
        second pass (PROTOCOL §11, 2026-09-24). The queue lines carry bibliographic data only, never first-pass results.
--only / --skip restrict the selection to, or remove from it, the pids of a queue json.
Writes audit/coding/queue_<name>[_<tag>].json (all pids, position order) and queue_<prefix><k>.txt, one per agent,
interleaved by position so every agent gets early and late records. Refuses to overwrite existing queue files.
"""
import argparse
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CODING = ROOT / "audit" / "coding"


def line(r):
    return (f"- {r['pid']} (decision order {r['order']}): \"{r['title']}\" | DOI {r['doi'] or 'none'} | "
            f"arXiv {r['arxiv_id'] or 'none'} | open copy per OpenAlex: {r['oa_url'] or '(find by title)'} | "
            f"access check: {r['accessible']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", choices=("wave3", "second"))
    ap.add_argument("--first", type=int, default=1)
    ap.add_argument("--last", type=int, default=200)
    ap.add_argument("--agents", type=int, required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--tag", default="", help="suffix of the queue json name")
    ap.add_argument("--only", help="queue json: keep only these pids")
    ap.add_argument("--skip", help="queue json: drop these pids")
    args = ap.parse_args()
    csv.field_size_limit(10 ** 9)
    rows = sorted(csv.DictReader(open(CODING / "access_final_order.csv", encoding="utf-8")), key=lambda r: int(r["order"]))
    rows = [r for r in rows if args.first <= int(r["order"]) <= args.last]
    if args.only:
        keep = set(json.loads((ROOT / args.only).read_text(encoding="utf-8")))
        rows = [r for r in rows if r["pid"] in keep]
    if args.skip:
        drop = set(json.loads((ROOT / args.skip).read_text(encoding="utf-8")))
        rows = [r for r in rows if r["pid"] not in drop]
    coded = {p.stem for p in (CODING / "llm_prefill").glob("P*.json")}
    if args.name == "wave3":
        sel = [r for r in rows if r["pid"] not in coded and not r["accessible"].startswith("no")]
    else:
        sel = [r for r in rows if r["pid"] in coded]
    name = f"queue_{args.name}" + (f"_{args.tag}" if args.tag else "") + ".json"
    outs = [CODING / name] + [CODING / f"queue_{args.prefix}{k}.txt" for k in range(1, args.agents + 1)]
    if any(o.exists() for o in outs):
        sys.exit("queue files exist already; refusing to overwrite")
    outs[0].write_text(json.dumps([r["pid"] for r in sel]), encoding="utf-8")
    for k in range(args.agents):
        part = sel[k::args.agents]
        outs[k + 1].write_text("\n".join(line(r) for r in part) + "\n", encoding="utf-8")
        print(outs[k + 1].name, len(part), " ".join(r["pid"] for r in part))
    print(f"{len(sel)} records -> {outs[0].name}")


if __name__ == "__main__":
    main()
