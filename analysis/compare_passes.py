"""Compare the first-pass and the blind second-pass AI codings; finalize agreements; queue disagreements.

    python -m analysis.compare_passes

For every record in the analysis sample (decision order 1-200; PROTOCOL §11) that has both
audit/coding/llm_prefill/<pid>.json (first pass) and audit/coding/second_pass/<pid>.json (blind second pass):
  * items compared: access (full text or not), inclusion decision, full-text exclusion code, stratum, R1-R4 verdicts,
    and the claimed speed-up (agreement = both absent, or within 10 % relative);
  * full agreement -> audit/coding/records/<pid>.json = first-pass record with stage "ai_agreed", after the mechanical
    PROTOCOL §11 clarifications that adjudicators also apply (apply_clarifications; changes are recorded);
  * any disagreement -> audit/coding/adjudication_queue.json for the adjudicator agents, which write
    audit/coding/records/<pid>.json with stage "ai_adjudicated".
An existing adjudicated record is never overwritten. Writes evidence/pass_comparison.json.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.codes import ft_code  # noqa: E402
from analysis.rules import SAMPLE_POSITIONS, sample_pids  # noqa: E402

FIRST, SECOND, RECORDS = (ROOT / "audit/coding/llm_prefill", ROOT / "audit/coding/second_pass", ROOT / "audit/coding/records")


def items(r):
    inc = r["included"]
    full = r.get("access") == "full_text"
    out = {"access": "full_text" if full else "not_full_text", "decision": inc["decision"]}
    if not full:
        return out
    if inc["decision"] == "exclude":
        out["ft_code"] = ft_code(inc["reason"])
        return out
    out["stratum"] = inc.get("stratum")
    for k in ("R1", "R2", "R3", "R4"):
        out[k] = r["rules"][k]["verdict"]
    out["claimed_speedup"] = (r.get("claim") or {}).get("claimed_speedup")
    return out


def apply_clarifications(r):
    """Mechanical PROTOCOL §11 clarifications (2026-09-24) that adjudicators apply, applied to agreed records too.

    Stratum Q: R3 is na; R2 is na unless it fails through criterion (b). No full text: no full-text exclusion (except
    FT-DUPLICATE, which rests on identity) - the record keeps include / I-UNCLEAR with stratum none and verdicts na.
    Returns {item: [before, after]} for every change."""
    ch = {}
    inc = r["included"]
    if r.get("access") != "full_text" and inc["decision"] == "exclude" and ft_code(inc["reason"]) != "FT-DUPLICATE":
        ch["decision"] = [f"exclude ({inc['reason']})", "include (I-UNCLEAR (no accessible full text))"]
        inc["decision"], inc["reason"], inc["stratum"] = "include", "I-UNCLEAR (no accessible full text)", "none"
    if inc["decision"] == "include" and inc.get("stratum") == "quality":
        if r["rules"]["R3"]["verdict"] != "na":
            ch["R3"] = [r["rules"]["R3"]["verdict"], "na"]
            r["rules"]["R3"]["verdict"] = "na"
        r2 = r["rules"]["R2"]
        if r2["verdict"] != "na" and not (r2["verdict"] == "fail" and "(b)" in str(r2.get("marker") or "")):
            ch["R2"] = [r2["verdict"], "na"]
            r2["verdict"] = "na"
    return ch


def same(key, a, b):
    if key == "claimed_speedup":
        if a is None or b is None:
            return a is None and b is None
        try:
            a, b = float(a), float(b)
        except (TypeError, ValueError):
            return str(a) == str(b)
        return abs(a - b) <= 0.10 * max(abs(a), abs(b), 1e-12)
    return a == b


def main():
    RECORDS.mkdir(parents=True, exist_ok=True)
    keep = sample_pids(SAMPLE_POSITIONS)
    rows, queue, agreed = [], [], 0
    for f2 in sorted(SECOND.glob("P*.json")):
        pid = f2.stem
        f1 = FIRST / f2.name
        if pid not in keep or not f1.exists():
            continue
        r1, r2 = json.loads(f1.read_text(encoding="utf-8")), json.loads(f2.read_text(encoding="utf-8"))
        a, b = items(r1), items(r2)
        keys = sorted(set(a) | set(b))
        diff = {k: [a.get(k), b.get(k)] for k in keys if not same(k, a.get(k), b.get(k))}
        rows.append({"pid": pid, "first": a, "second": b, "disagreements": diff})
        out = RECORDS / f"{pid}.json"
        if out.exists() and json.loads(out.read_text(encoding="utf-8")).get("stage") == "ai_adjudicated":
            continue
        if diff:
            queue.append({"pid": pid, "disagreements": diff})
        else:
            r = json.loads(json.dumps(r1))
            r["stage"] = "ai_agreed"
            r["verification"] = {"second_pass": f"audit/coding/second_pass/{pid}.json", "result": "full agreement"}
            ch = apply_clarifications(r)
            if ch:
                r["verification"]["protocol_clarifications_applied"] = ch
            out.write_text(json.dumps(r, indent=1), encoding="utf-8")
            agreed += 1
    (ROOT / "audit/coding/adjudication_queue.json").write_text(json.dumps(queue, indent=1), encoding="utf-8")
    (ROOT / "evidence/pass_comparison.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print(f"compared {len(rows)}; full agreement {agreed} (written as ai_agreed); queued for adjudication {len(queue)}")


if __name__ == "__main__":
    main()
