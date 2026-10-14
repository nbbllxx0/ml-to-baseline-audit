"""Open-access status of the first records in the decision order (who can the coders read?).

    python -m audit.coding.oa_lookup --first 120

For each record: an arXiv id in the pool means accessible. Otherwise the DOI is looked up in OpenAlex (anonymous,
generic User-Agent, no personal data): `open_access.oa_status`, the best open location, and any arXiv or repository
location. Writes audit/coding/access_final_order.csv. Raw responses go to audit/search/raw/oa_lookup/.
A record marked not accessible is skipped by G1 (PROTOCOL §11 decision-pilot row) unless the user supplies the full
text, which then makes it accessible.
"""
import argparse
import csv
import json
import pathlib
import subprocess
import time
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "audit" / "search" / "raw" / "oa_lookup"


def fetch(doi):
    RAW.mkdir(parents=True, exist_ok=True)
    out = RAW / (doi.replace("/", "_") + ".json")
    if not out.exists():
        url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi)}?" + urllib.parse.urlencode(
            {"select": "id,doi,open_access,best_oa_location,locations"})
        subprocess.run(["curl", "-sL", "-A", "ml-to-baseline-audit/1.0", "-o", str(out), url], check=False, timeout=120)
        time.sleep(0.2)
    try:
        return json.loads(out.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first", type=int, default=120)
    args = ap.parse_args()
    csv.field_size_limit(10 ** 9)
    order = list(csv.DictReader(open(ROOT / "audit/screening/pilot_final_order.csv", encoding="utf-8")))[:args.first]
    rows = []
    for r in order:
        rec = {"order": r["order"], "pid": r["pid"], "doi": r["doi"], "arxiv_id": r["arxiv_id"],
               "already_coded": r["already_coded"], "oa_status": "", "oa_url": "", "arxiv_location": "",
               "accessible": "", "title": r["title"][:120]}
        if r["arxiv_id"]:
            rec.update(accessible="yes", arxiv_location=f"https://arxiv.org/abs/{r['arxiv_id']}", oa_status="arXiv")
        elif r["doi"]:
            w = fetch(r["doi"])
            if w and "open_access" in w:
                oa = w.get("open_access") or {}
                best = w.get("best_oa_location") or {}
                rec["oa_status"] = oa.get("oa_status", "")
                rec["oa_url"] = best.get("pdf_url") or best.get("landing_page_url") or oa.get("oa_url") or ""
                for loc in w.get("locations") or []:
                    src = ((loc or {}).get("source") or {}).get("display_name") or ""
                    if "arxiv" in src.lower() and loc.get("landing_page_url"):
                        rec["arxiv_location"] = loc["landing_page_url"]
                rec["accessible"] = "yes" if (oa.get("is_oa") or rec["arxiv_location"]) else "no (paywalled per OpenAlex)"
            else:
                rec["accessible"] = "unknown (lookup failed)"
        else:
            rec["accessible"] = "unknown (no DOI, no arXiv id)"
        rows.append(rec)
    out = ROOT / "audit" / "coding" / "access_final_order.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r["accessible"]] = counts.get(r["accessible"], 0) + 1
    print(json.dumps(counts, indent=1))


if __name__ == "__main__":
    main()
