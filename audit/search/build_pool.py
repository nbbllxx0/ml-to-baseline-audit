"""Parse raw search responses into one de-duplicated candidate pool (audit/pool/pool.csv).

De-duplication key, in order: DOI (lower-case), arXiv id (without version), normalised title.
Each pool row keeps every source query id it came from.
"""
import csv
import html
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "audit" / "search" / "raw"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def norm_title(t):
    t = html.unescape(t or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def arxiv_records():
    for page in sorted((RAW / "arxiv").glob("*/page_*.xml")):
        qid = page.parent.name
        root = ET.parse(page).getroot()
        for e in root.findall("a:entry", NS):
            aid = e.find("a:id", NS).text.rsplit("/abs/", 1)[-1]
            aid_nov = re.sub(r"v\d+$", "", aid)
            doi_el = e.find("arxiv:doi", NS)
            jref = e.find("arxiv:journal_ref", NS)
            yield {
                "source": f"arxiv:{qid}",
                "arxiv_id": aid_nov,
                "doi": (doi_el.text.strip().lower() if doi_el is not None else ""),
                "title": " ".join(e.find("a:title", NS).text.split()),
                "abstract": " ".join(e.find("a:summary", NS).text.split()),
                "date": e.find("a:published", NS).text[:10],
                "authors": "; ".join(a.find("a:name", NS).text for a in e.findall("a:author", NS)),
                "venue": (jref.text.strip() if jref is not None else ""),
                "type": "preprint",
                "cited_by": "",
            }


def openalex_records(sub):
    base = RAW / sub
    if not base.exists():
        return
    for page in sorted(base.glob("*/page_*.json")):
        qid = page.parent.name
        data = json.loads(page.read_text(encoding="utf-8"))
        for w in data.get("results", []):
            inv = w.get("abstract_inverted_index") or {}
            pos = {}
            for word, idxs in inv.items():
                for i in idxs:
                    pos[i] = word
            ids = w.get("ids") or {}
            arx = ""
            for v in ids.values():
                m = re.search(r"arxiv\.org/abs/([0-9.]+)", str(v))
                if m:
                    arx = m.group(1)
            src = ((w.get("primary_location") or {}).get("source") or {}) or {}
            yield {
                "source": f"{sub}:{qid}",
                "arxiv_id": arx,
                "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower(),
                "title": " ".join((w.get("title") or "").split()),
                "abstract": " ".join(pos[i] for i in sorted(pos)),
                "date": w.get("publication_date") or "",
                "authors": "; ".join(a["author"]["display_name"] for a in (w.get("authorships") or [])[:12]),
                "venue": src.get("display_name") or "",
                "type": w.get("type") or "",
                "cited_by": w.get("cited_by_count", ""),
                "openalex_id": w.get("id", ""),
            }


def bibliography_records():
    """Reference lists parsed from an article's own bibliography (no OpenAlex record of the list), matched by title."""
    for f in sorted((RAW / "backward").glob("*/references.json")):
        qid = f.parent.name
        for r in json.loads(f.read_text(encoding="utf-8"))["references"]:
            yield {"source": f"backward:{qid}", "arxiv_id": "", "doi": "", "title": " ".join(r["title"].split()),
                   "abstract": "", "date": r.get("year", ""), "authors": r.get("authors", ""),
                   "venue": r.get("venue", ""), "type": "reference-list entry", "cited_by": ""}


def main():
    pool, keymap = [], {}
    gens = [arxiv_records()] + [openalex_records(s) for s in ("openalex", "forward", "backward")] + [bibliography_records()]
    for gen in gens:
        for r in gen or []:
            keys = [k for k in (("doi:" + r["doi"]) if r["doi"] else None,
                                ("arxiv:" + r["arxiv_id"]) if r["arxiv_id"] else None,
                                "title:" + norm_title(r["title"])) if k]
            hit = next((keymap[k] for k in keys if k in keymap), None)
            if hit is None:
                r["sources"] = r.pop("source")
                pool.append(r)
                hit = len(pool) - 1
            else:
                cur = pool[hit]
                cur["sources"] = ";".join(sorted(set(cur["sources"].split(";")) | {r["source"]}))
                for f in ("doi", "arxiv_id", "venue", "abstract", "cited_by", "openalex_id"):
                    if not cur.get(f) and r.get(f):
                        cur[f] = r[f]
            for k in keys:
                keymap.setdefault(k, hit)
    fields = ["pid", "title", "date", "authors", "venue", "type", "doi", "arxiv_id", "openalex_id", "cited_by",
              "sources", "abstract"]
    for i, r in enumerate(pool):
        r["pid"] = f"P{i + 1:05d}"
    out = ROOT / "audit" / "pool" / "pool.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in pool:
            w.writerow({f: r.get(f, "") for f in fields})
    print(f"pool: {len(pool)} unique records -> {out.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
