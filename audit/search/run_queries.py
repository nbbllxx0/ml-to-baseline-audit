"""Run the frozen literature queries (plan/PROTOCOL.md §2) and save every raw response.

    python -m audit.search.run_queries            # all sources
    python -m audit.search.run_queries --only arxiv

Raw responses go to audit/search/raw/<source>/<query id>/page_<k>.(xml|json) with a request log
(audit/search/raw/requests.jsonl: UTC time, URL, HTTP status, bytes). Network access uses curl (the
Inkscape-bundled Python on PATH fails TLS verification; curl does not). Standard library only.

Privacy: no personal data is sent. The User-Agent is generic. OpenAlex's "polite pool" `mailto` parameter is sent
only if the user sets OPENALEX_MAILTO themselves; by default it is omitted. (Until 2026-09-24 ~20:00 UTC this script
put an institutional address in the User-Agent; the 6 arXiv requests of 14:31 UTC carried it. Removed; see the task
record.)
"""
import os
import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "audit" / "search" / "raw"
MAILTO = os.environ.get("OPENALEX_MAILTO")   # opt-in only; never set by this project
NS = {"a": "http://www.w3.org/2005/Atom", "os": "http://a9.com/-/spec/opensearch/1.1/"}


def mail():
    return {"mailto": MAILTO} if MAILTO else {}


def fetch(url, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    res = subprocess.run(["curl", "-sL", "-A", "ml-to-baseline-audit/1.0",
                          "-w", "%{http_code}", "-o", str(out_path), url], capture_output=True, text=True, timeout=180)
    code = res.stdout.strip()[-3:]
    size = out_path.stat().st_size if out_path.exists() else 0
    with open(RAW / "requests.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                             "url": url, "http": code, "bytes": size, "file": out_path.relative_to(ROOT).as_posix()}) + "\n")
    return code


def run_arxiv(q, page_size=500, pause=3.5):
    start, page = 0, 0
    while True:
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            {"search_query": q["query"], "start": start, "max_results": page_size,
             "sortBy": "submittedDate", "sortOrder": "descending"})
        out = RAW / "arxiv" / q["id"] / f"page_{page:03d}.xml"
        code = fetch(url, out)
        if code != "200":
            print(f"  {q['id']} page {page}: HTTP {code}", file=sys.stderr)
            break
        root = ET.parse(out).getroot()
        total = int(root.find("os:totalResults", NS).text)
        n = len(root.findall("a:entry", NS))
        print(f"  {q['id']} page {page}: {n} entries (total {total})")
        start += page_size
        page += 1
        if n == 0 or start >= total:
            break
        time.sleep(pause)


def run_openalex_filter(qid, flt, sub="openalex", pause=0.3):
    cursor, page = "*", 0
    while cursor:
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
            {"filter": flt, "per-page": 200, "cursor": cursor, **mail(),
             "select": "id,doi,title,publication_year,publication_date,type,primary_location,ids,cited_by_count,"
                       "abstract_inverted_index,authorships,referenced_works_count"})
        out = RAW / sub / qid / f"page_{page:03d}.json"
        code = fetch(url, out)
        if code != "200":
            print(f"  {qid} page {page}: HTTP {code}", file=sys.stderr)
            break
        data = json.loads(out.read_text(encoding="utf-8"))
        n = len(data.get("results", []))
        print(f"  {qid} page {page}: {n} results (count {data.get('meta', {}).get('count')})")
        cursor = data.get("meta", {}).get("next_cursor") if n else None
        page += 1
        time.sleep(pause)


def resolve_work(anchor):
    """OpenAlex work id for an anchor given by DOI or exact title."""
    if "doi" in anchor:
        url = f"https://api.openalex.org/works/https://doi.org/{anchor['doi']}?" + urllib.parse.urlencode(
            {**mail(), "select": "id,title,doi"})
    else:
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
            {"filter": f"title.search:{anchor['title']}", "per-page": 25, **mail(),
             "select": "id,title,doi,publication_year,cited_by_count", "sort": "cited_by_count:desc"})
    out = RAW / "anchors" / f"{anchor['id']}.json"
    fetch(url, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    if "results" in data:
        exact = [w for w in data["results"] if (w.get("title") or "").strip().lower() == anchor["title"].strip().lower()]
        return exact[0] if exact else None          # exact title only; a non-exact fallback picked a wrong work once
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["arxiv", "openalex", "forward", "backward"])
    args = ap.parse_args()
    spec = json.loads((ROOT / "audit" / "search" / "queries.json").read_text(encoding="utf-8"))
    RAW.mkdir(parents=True, exist_ok=True)
    if args.only in (None, "arxiv"):
        for q in spec["arxiv"]:
            run_arxiv(q)
    if args.only in (None, "openalex"):
        for q in spec["openalex"]:
            run_openalex_filter(q["id"], q["filter"])
    if args.only in (None, "forward"):
        resolved = {}
        for a in spec["forward_citation_anchors"]:
            w = resolve_work(a)
            resolved[a["id"]] = w
            if w and w.get("id"):
                wid = w["id"].rsplit("/", 1)[-1]
                print(f"  {a['id']} -> {wid} {w.get('title')}")
                run_openalex_filter(a["id"], f"cites:{wid}", sub="forward")
            else:
                print(f"  {a['id']}: anchor not resolved -> logged, dropped", file=sys.stderr)
        (RAW / "anchors" / "resolved.json").write_text(json.dumps(resolved, indent=2), encoding="utf-8")
    if args.only in (None, "backward"):
        for b in spec["backward_citation_sources"]:
            url = f"https://api.openalex.org/works/https://doi.org/{b['doi']}?" + urllib.parse.urlencode(
                {**mail(), "select": "id,title,referenced_works"})
            out = RAW / "backward" / b["id"] / "source.json"
            fetch(url, out)
            refs = json.loads(out.read_text(encoding="utf-8")).get("referenced_works", [])
            print(f"  {b['id']}: {len(refs)} referenced works")
            for k in range(0, len(refs), 50):
                ids = "|".join(r.rsplit("/", 1)[-1] for r in refs[k:k + 50])
                run_openalex_filter(f"{b['id']}_chunk{k // 50:02d}", f"openalex:{ids}", sub="backward")


if __name__ == "__main__":
    main()
