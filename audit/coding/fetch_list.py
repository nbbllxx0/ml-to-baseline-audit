"""Write audit/coding/FETCH_LIST.md: records in the decision order whose full text the coding agents could not read.

    python -m audit.coding.fetch_list --upto 161

Two groups, both up to the given decision-order position:
  * open access per OpenAlex, but blocked for automated agents (CAPTCHA or bot check) -> free to read in a browser;
  * paywalled per OpenAlex -> needs library access.
G1 skips both groups under the pre-registered rule unless the user supplies the full text
(audit/coding/user_supplied_fulltext.csv). Third-party PDFs are never stored in the project (PROTOCOL §7.4).
"""
import argparse
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upto", type=int, default=161)
    args = ap.parse_args()
    rows = [r for r in csv.DictReader(open(ROOT / "audit/coding/access_final_order.csv", encoding="utf-8"))
            if int(r["order"]) <= args.upto]
    access = {}
    for f in (ROOT / "audit/coding/llm_prefill").glob("P*.json"):
        r = json.loads(f.read_text(encoding="utf-8"))
        access[r["pid"]] = r.get("access")
    blocked = [r for r in rows if access.get(r["pid"]) in ("abstract_only", "no_access")]
    paywalled = [r for r in rows if r["accessible"].startswith("no") and r["pid"] not in access]
    lines = ["# Papers to fetch (optional): records in the decision order the coding agents could not read", "",
             "**Why.** G1 walks the decision order (`audit/screening/pilot_final_order.csv`). The pre-registered rule "
             "skips a record whose full text the coders cannot read, which biases the pilot toward papers that "
             "automated agents can reach. Supplying a PDF makes the record count.",
             "",
             "**How to supply a paper.**",
             "1. Save the PDF outside the project (third-party PDFs are never stored in the project; PROTOCOL §7.4), for "
             "example in a private folder next to it named `ml-to-baseline-audit-private`, as `<pid>.pdf`.",
             "2. Add a row to `audit/coding/user_supplied_fulltext.csv` with columns `pid,file,date` (create the file with "
             "that header if it does not exist).",
             "3. Tell me; the supplied records get coded and re-enter the G1 walk at their positions.",
             "",
             f"Positions up to {args.upto} (the span coded so far). Earlier positions matter most.",
             "",
             f"## A. Free to read in a browser, but blocked for automated agents ({len(blocked)})", "",
             "| Order | pid | Title | Link |", "|---|---|---|---|"]
    for r in blocked:
        link = f"https://doi.org/{r['doi']}" if r["doi"] else (r["oa_url"] or "search by title")
        lines.append(f"| {r['order']} | {r['pid']} | {r['title'].replace('|', '/')} | {link} |")
    lines += ["", f"## B. Paywalled per OpenAlex ({len(paywalled)})", "", "| Order | pid | Title | DOI |", "|---|---|---|---|"]
    for r in paywalled:
        lines.append(f"| {r['order']} | {r['pid']} | {r['title'].replace('|', '/')} | https://doi.org/{r['doi']} |")
    (ROOT / "audit/coding/FETCH_LIST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"blocked {len(blocked)}, paywalled {len(paywalled)} (positions <= {args.upto})")


if __name__ == "__main__":
    main()
