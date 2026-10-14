"""Human verification of LLM-prefilled coding records (plan/PROTOCOL.md §7).

Superseded (PROTOCOL §11, 2026-09-24): records are verified by a blind second AI pass and AI adjudication
(analysis/compare_passes.py). This tool is kept for the record and is not part of the pipeline.

    python -m audit.coding.review_tools sheet      # writes audit/coding/REVIEW_pilot.md and human_verification.csv
    python -m audit.coding.review_tools apply      # applies filled rows of human_verification.csv -> audit/coding/records/

The sheet covers the pilot and every coded top-up, in the pre-registered order. Rows already in the CSV are never
rewritten; `sheet` only appends rows for newly coded records.

The human fills one CSV row per article:
- confirm or override `included`, `stratum` and each rule verdict (pass / partial / fail / na);
- for an exclusion, give `human_reason`: one code from audit/schema/screening_codes.md (second table);
- add initials and date; leave a cell blank to accept the prefill value.
`apply` writes audit/coding/records/<pid>.json with stage = "human_verified". An excluded record gets stratum "none"
and all verdicts "na". Every change from the prefill is kept in `human_changes`, so C5 (LLM-human agreement) can be
computed later. Prefill files are never modified.
"""
import csv
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from analysis.codes import ft_code  # noqa: E402

PREFILL = ROOT / "audit" / "coding" / "llm_prefill"
RECORDS = ROOT / "audit" / "coding" / "records"
CSV = ROOT / "audit" / "coding" / "human_verification.csv"
FIELDS = ["pid", "arxiv_or_doi", "prefill_include", "prefill_stratum", "prefill_R1", "prefill_R2", "prefill_R3",
          "prefill_R4", "human_include", "human_reason", "human_stratum", "human_R1", "human_R2", "human_R3",
          "human_R4", "human_initials", "human_date", "human_notes"]


def load_prefills(pids=None):
    recs = {}
    for f in sorted(PREFILL.glob("P*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        if pids is None or r["pid"] in pids:
            recs[r["pid"]] = r
    return recs


def sheet():
    pilot = [r["pid"] for r in csv.DictReader(open(ROOT / "audit/screening/pilot_provisional.csv", encoding="utf-8"))]
    topup = [r["pid"] for r in csv.DictReader(open(ROOT / "audit/screening/pilot_topup_order.csv", encoding="utf-8"))]
    final_file = ROOT / "audit/screening/pilot_final_order.csv"
    final = [r["pid"] for r in csv.DictReader(open(final_file, encoding="utf-8"))] if final_file.exists() else []
    recs = load_prefills(set(pilot) | set(topup) | set(final))
    flags = {}
    for f in csv.DictReader(open(ROOT / "audit/coding/verifier_flags.csv", encoding="utf-8")):
        flags.setdefault(f["pid"], []).append(f"{f['flag']}: {f['note']}")
    # Decision order first (G1 walks it; PROTOCOL §11 decision-pilot row), then the provisional arXiv pilot and top-ups.
    roles = {}
    for i, pid in enumerate(final, 1):
        if pid in recs:
            roles.setdefault(pid, []).append(f"decision order {i}")
    for i, pid in enumerate(pilot, 1):
        roles.setdefault(pid, []).append(f"provisional pilot {i}")
    for i, pid in enumerate(topup, 1):
        if pid in recs:
            roles.setdefault(pid, []).append(f"provisional top-up {i}")
    sequence = [(pid, "; ".join(r)) for pid, r in roles.items()]
    lines = ["# Pilot and top-up coding — human verification sheet", "",
             "For each article: open the link, check the pre-filled primary outcome and rule verdicts against the "
             "protocol (`plan/PROTOCOL.md` §5), then fill your row in `audit/coding/human_verification.csv`. "
             "Blank cells accept the prefill. Unsure → pass (template convention).", "",
             "Rules that the prefills did not all apply (`plan/PROTOCOL.md` §11):",
             "- **No baseline.** An article that does not run, time or cite a classical method's cost or result makes "
             "no comparison. Exclude it: human_include = `exclude`, human_reason = `FT-NOBASELINE`; `apply` then sets "
             "stratum and R1–R4 to `na`. Records flagged as candidates are marked below.",
             "- **Exclusion codes.** Use one code from the closed list in `audit/schema/screening_codes.md` (second "
             "table), first applicable in its order.",
             "- **G1 set.** The decision G1 walks the decision order (records marked \"decision order k\", listed "
             "first) and uses the first 20 speed-stratum includes. The provisional arXiv pilot and its top-ups follow. "
             "`python -m analysis.gates` shows the current sets. Verify in the listed order.",
             "- **Conflicts of interest.** Leave flagged records for the second coder.",
             "- **Browser caveat.** Some pilot prefills were read through a browser tab that several coders shared. "
             "Check each locator against the article.", ""]
    rows = []
    for pid, role in sequence:
        r = recs.get(pid)
        if r is None:
            lines += [f"## {pid} ({role}) — NOT YET CODED", ""]
            continue
        c = r.get("citation", {})
        link = f"https://arxiv.org/abs/{c.get('arxiv_id')}" if c.get("arxiv_id") else (f"https://doi.org/{c.get('doi')}" if c.get("doi") else "")
        inc, cl, rl = r.get("included", {}), r.get("claim", {}), r.get("rules", {})
        reason = inc.get("reason")
        if inc.get("decision") == "exclude":
            reason = f"{ft_code(reason)}; prefill label: {reason}"
        lines += [f"## {pid} ({role}) — {c.get('title', '')} ({c.get('year', '')})", ""]
        lines += [f"- **FLAG — {f}**" for f in flags.get(pid, [])]
        lines += [f"- Link: {link}", f"- Access: {r.get('access')}; inclusion: **{inc.get('decision')}** "
                  f"({reason}); stratum: **{inc.get('stratum')}**",
                  f"- Primary outcome ({cl.get('location', '')}): {cl.get('primary_outcome_paraphrase', '')}",
                  f"- Key phrase: {cl.get('key_phrase', '')}",
                  f"- Claimed speed-up: {cl.get('claimed_speedup')} ({cl.get('claimed_speedup_basis', '')})", ""]
        for k in ("R1", "R2", "R3", "R4"):
            v = rl.get(k, {})
            lines.append(f"- **{k} = {v.get('verdict')}** [{v.get('marker', '')}] — {v.get('evidence', '')}")
        lines += ["", f"- Baseline: {json.dumps(r.get('baseline', {}), ensure_ascii=False)[:900]}", ""]
        rows.append({"pid": pid, "arxiv_or_doi": c.get("arxiv_id") or c.get("doi") or "",
                     "prefill_include": inc.get("decision"), "prefill_stratum": inc.get("stratum"),
                     "prefill_R1": rl.get("R1", {}).get("verdict"), "prefill_R2": rl.get("R2", {}).get("verdict"),
                     "prefill_R3": rl.get("R3", {}).get("verdict"), "prefill_R4": rl.get("R4", {}).get("verdict")})
    (ROOT / "audit" / "coding" / "REVIEW_pilot.md").write_text("\n".join(lines), encoding="utf-8")
    # Existing rows (and anything the human typed in them) are never rewritten; new records are appended.
    have = {r["pid"] for r in csv.DictReader(open(CSV, encoding="utf-8"))} if CSV.exists() else set()
    new = [row for row in rows if row["pid"] not in have]
    with open(CSV, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if not have:
            w.writeheader()
        for row in new:
            w.writerow({k: row.get(k, "") for k in FIELDS})
    print(f"wrote REVIEW_pilot.md ({len(rows)} records); appended {len(new)} rows to {CSV.name}")


def apply():
    RECORDS.mkdir(parents=True, exist_ok=True)
    recs = load_prefills()
    n = 0
    for row in csv.DictReader(open(CSV, encoding="utf-8")):
        if not row.get("human_initials"):
            continue
        pid = row["pid"]
        r = json.loads(json.dumps(recs[pid]))
        changes = {}
        if row.get("human_include"):
            if row["human_include"] not in ("include", "exclude"):
                sys.exit(f"{pid}: bad human_include {row['human_include']!r}")
            if row["human_include"] != r["included"]["decision"]:
                changes["included"] = [r["included"]["decision"], row["human_include"]]
            r["included"]["decision"] = row["human_include"]
        if row.get("human_reason"):
            if row["human_reason"] != r["included"].get("reason"):
                changes["reason"] = [r["included"].get("reason"), row["human_reason"]]
            r["included"]["reason"] = row["human_reason"]
        if row.get("human_stratum"):
            if row["human_stratum"] != r["included"].get("stratum"):
                changes["stratum"] = [r["included"].get("stratum"), row["human_stratum"]]
            r["included"]["stratum"] = row["human_stratum"]
        for k in ("R1", "R2", "R3", "R4"):
            v = row.get(f"human_{k}")
            if v:
                if v not in ("pass", "partial", "fail", "na"):
                    sys.exit(f"{pid} {k}: bad verdict {v!r}")
                if v != r["rules"][k]["verdict"]:
                    changes[k] = [r["rules"][k]["verdict"], v]
                r["rules"][k]["verdict"] = v
        if r["included"]["decision"] == "exclude":
            try:
                ft_code(r["included"]["reason"])
            except ValueError as exc:
                sys.exit(f"{pid}: an exclusion needs human_reason from the FT list ({exc})")
            if r["included"].get("stratum") != "none":
                changes["stratum"] = [r["included"].get("stratum"), "none"]
            r["included"]["stratum"] = "none"
            for k in ("R1", "R2", "R3", "R4"):
                if r["rules"][k]["verdict"] != "na":
                    changes[k] = [r["rules"][k]["verdict"], "na"]
                r["rules"][k]["verdict"] = "na"
        r["stage"] = "human_verified"
        r["coder"]["human_initials"] = row["human_initials"]
        r["coder"]["human_date"] = row.get("human_date") or dt.date.today().isoformat()
        r["human_changes"] = changes
        r["human_notes"] = row.get("human_notes", "")
        (RECORDS / f"{pid}.json").write_text(json.dumps(r, indent=1), encoding="utf-8")
        n += 1
    print(f"applied {n} human-verified records -> {RECORDS.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    {"sheet": sheet, "apply": apply}[sys.argv[1]]()
