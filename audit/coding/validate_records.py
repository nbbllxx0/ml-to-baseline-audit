"""Validate coding records against audit/schema/coding_schema.json and the closed code lists.

    python -m audit.coding.validate_records llm_prefill P00001 P00002 ...
    python -m audit.coding.validate_records second_pass --queue audit/coding/queue_wave2.json

Checks per record: valid JSON; `pid` equals the file name; schema validation (jsonschema, if installed; otherwise the
required keys and the stage/access/decision/verdict enums); the stage expected for the folder (llm_prefill ->
"llm_prefill", second_pass -> "ai_second_pass"); a full-text exclusion carries a code from the closed list
(analysis.codes.ft_code); an excluded or unread record has stratum "none" and all rule verdicts "na". Exits non-zero
on any problem and lists every problem found.
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from analysis.codes import ft_code  # noqa: E402

STAGE = {"llm_prefill": "llm_prefill", "second_pass": "ai_second_pass", "records": None}
VERDICTS = {"pass", "partial", "fail", "na"}


def check(path, folder, schema):
    probs = []
    try:
        r = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"unreadable: {exc}"]
    if r.get("pid") != path.stem:
        probs.append(f"pid {r.get('pid')!r} differs from the file name")
    try:
        import jsonschema
        for e in jsonschema.Draft7Validator(schema).iter_errors(r):
            probs.append(f"schema: {'/'.join(map(str, e.path))}: {e.message[:160]}")
    except ImportError:
        for k in schema["required"]:
            if k not in r:
                probs.append(f"missing key {k}")
    want = STAGE[folder]
    if want and r.get("stage") != want:
        probs.append(f"stage {r.get('stage')!r}, expected {want!r}")
    inc = r.get("included") or {}
    rules = r.get("rules") or {}
    for k in ("R1", "R2", "R3", "R4"):
        v = (rules.get(k) or {}).get("verdict")
        if v not in VERDICTS:
            probs.append(f"{k} verdict {v!r}")
    if inc.get("decision") == "exclude" and r.get("access") == "full_text":
        try:
            ft_code(inc.get("reason", ""))
        except ValueError as exc:
            probs.append(str(exc))
    if inc.get("decision") == "exclude" or r.get("access") != "full_text":
        if inc.get("stratum") not in (None, "none"):
            probs.append(f"stratum {inc.get('stratum')!r} on an excluded or unread record")
        if any((rules.get(k) or {}).get("verdict") != "na" for k in ("R1", "R2", "R3", "R4")):
            probs.append("rule verdicts must be na on an excluded or unread record")
    return probs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", choices=sorted(STAGE))
    ap.add_argument("pids", nargs="*")
    ap.add_argument("--queue", help="JSON list of pids")
    args = ap.parse_args()
    pids = list(args.pids) + (json.loads((ROOT / args.queue).read_text(encoding="utf-8")) if args.queue else [])
    if not pids:
        sys.exit("no pids given")
    schema = json.loads((ROOT / "audit/schema/coding_schema.json").read_text(encoding="utf-8"))
    bad = 0
    for pid in pids:
        path = ROOT / "audit" / "coding" / args.folder / f"{pid}.json"
        probs = ["missing file"] if not path.exists() else check(path, args.folder, schema)
        if probs:
            bad += 1
            print(pid, "; ".join(probs))
    print(f"{len(pids) - bad}/{len(pids)} records valid")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
