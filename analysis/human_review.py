"""Authors' review of the 28 speed-stratum verdicts (SMO v2, Sect. 2.3): agreement with the adjudicated verdicts.

    python -m analysis.human_review [path/to/filled_checklist.csv]

Input: manuscript/smo_v2/online_resources/review/speed_stratum_checklist.csv after the authors filled, per row,
`reviewer_agrees_y_n` (y or n) and, when n, `reviewer_verdict` (pass, partial, fail or na) and a note. A row with y
keeps the adjudicated verdict; a row with n must give a different verdict. The script stops on a missing or invalid
entry, so a half-filled file cannot be reported. It does not change any coding record.

Output: evidence/human_review.json (per-rule agreement, Cohen's kappa, every change with its note) and numbers
N200 onward. If any verdict changed, the headline rates must be recomputed from the reviewed verdicts and the change
reported as a deviation; the script prints the changes and the reviewed weak-baseline count to make that step explicit.
"""
import collections
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.numbers import register  # noqa: E402

CSV = ROOT / "manuscript" / "smo_v2" / "online_resources" / "review" / "speed_stratum_checklist.csv"
OUT = ROOT / "evidence" / "human_review.json"
VERDICTS = {"pass", "partial", "fail", "na"}


from analysis.agreement import boot, kappa  # noqa: E402  (same κ and bootstrap as the coder agreement)

LOG = ROOT / "manuscript" / "smo_v2" / "online_resources" / "review" / "review_log.json"


def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else CSV
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    if len(rows) != 112:
        raise SystemExit(f"expected 112 rows (28 records x 4 rules), found {len(rows)}")
    reviewed, problems = [], []
    for r in rows:
        agree = r["reviewer_agrees_y_n"].strip().lower()
        rv = r["reviewer_verdict"].strip().lower()
        if agree == "y":
            final = r["verdict"]
            if rv and rv != r["verdict"]:
                problems.append(f"{r['pid']} {r['rule']}: agrees = y but reviewer verdict {rv!r} differs")
        elif agree == "n":
            if rv not in VERDICTS or rv == r["verdict"]:
                problems.append(f"{r['pid']} {r['rule']}: agrees = n needs a different verdict in {sorted(VERDICTS)}")
            final = rv
        else:
            problems.append(f"{r['pid']} {r['rule']}: reviewer_agrees_y_n is empty or not y/n")
            final = None
        reviewed.append({**r, "reviewed": final})
    if problems:
        raise SystemExit("checklist not complete:\n  " + "\n  ".join(problems))
    per_rule, changes = {}, []
    for rule in ("R1", "R2", "R3", "R4"):
        rr = [r for r in reviewed if r["rule"] == rule]
        a, b = [r["verdict"] for r in rr], [r["reviewed"] for r in rr]
        agree = sum(x == y for x, y in zip(a, b))
        per_rule[rule] = {"n": len(rr), "agree": agree, "kappa": kappa(a, b), "kappa_ci95": boot(a, b)}
        changes += [{"pid": r["pid"], "rule": rule, "adjudicated": r["verdict"], "reviewed": r["reviewed"],
                     "note": r["reviewer_note"]} for r in rr if r["verdict"] != r["reviewed"]]
    by_pid = collections.defaultdict(dict)
    for r in reviewed:
        by_pid[r["pid"]][r["rule"]] = r["reviewed"]
    weak = sum(1 for v in by_pid.values() if v["R1"] == "fail" or v["R2"] == "fail")
    out = {"source": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), "per_rule": per_rule,
           "changes": changes, "n_changed": len(changes), "weak_R1_or_R2_reviewed": weak, "n_records": len(by_pid)}
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    src, script = "evidence/human_review.json", "analysis/human_review.py"
    nid = 200
    for rule, v in per_rule.items():
        register(f"N{nid}", v["agree"], text=f"{v['agree']} of {v['n']}", source=src, script=script,
                 note=f"authors' review agrees with the adjudicated {rule} verdict")
        nid += 1
    register(f"N{nid}", len(changes), text=str(len(changes)), source=src, script=script,
             note="speed-stratum verdicts changed by the authors' review (of 112)")
    register(f"N{nid + 1}", weak, text=f"{100 * weak / len(by_pid):.0f} % ({weak}/{len(by_pid)})", source=src,
             script=script, note="speed claims failing R1 or R2 under the authors' review (reported rates stay adjudicated)")
    nid += 2
    for rule, v in per_rule.items():
        lo, hi = v["kappa_ci95"]
        text = f"{v['kappa']:.2f}" if lo == hi == 1.0 else f"{v['kappa']:.2f} (95 % CI {lo:.2f}–{hi:.2f})"
        register(f"N{nid}", v["kappa"], text=text, source=src, script=script,
                 note=f"Cohen's κ, authors' review vs adjudicated {rule} verdicts (28 speed-stratum records; bootstrap "
                      "2,000 resamples, seed 20260924)")
        nid += 1
    to_r1_fail = sum(1 for c in changes if c["rule"] == "R1" and c["reviewed"] == "fail")
    register(f"N{nid}", to_r1_fail, text=str(to_r1_fail), source=src, script=script,
             note="changed verdicts that became R1 fails (each adds a weak-baseline record)")
    # Cross-check against the review log written with the review.
    if LOG.exists():
        log = json.loads(LOG.read_text(encoding="utf-8"))
        for rule, v in per_rule.items():
            x = log["human_vs_adjudicated"][rule]
            if x["n_agree"] != v["agree"] or abs(x["kappa"] - v["kappa"]) > 1e-12 or \
                    any(abs(p - q) > 1e-12 for p, q in zip(x["kappa_ci95"], v["kappa_ci95"])):
                raise SystemExit(f"{rule}: this computation disagrees with review_log.json")
        if log["n_changed"] != len(changes) or log["weak_R1_or_R2"]["human"] != f"{weak}/{len(by_pid)}":
            raise SystemExit("changed count or weak share disagrees with review_log.json")
        print("cross-check with review_log.json: identical")
    for rule, v in per_rule.items():
        print(f"{rule}: {v['agree']} of {v['n']} agree, kappa {v['kappa']:.2f}")
    print(f"changed: {len(changes)}; weak baseline after review: {weak} of {len(by_pid)} (adjudicated: 8 of 28)")
    for c in changes:
        print(f"  {c['pid']} {c['rule']}: {c['adjudicated']} -> {c['reviewed']} | {c['note']}")


if __name__ == "__main__":
    main()
