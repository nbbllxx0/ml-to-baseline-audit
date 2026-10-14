"""Format-only repair of invalid returned records (README: "returned to the same session for a format repair only").

    python guide_manuscript/cross_provider_coding/repair_codex.py prepare C:\\xprov_runs gpt-6-luna
    (run the repair sessions: run_codex.ps1 -Action Repair -Models gpt-6-luna -DefaultHome)
    python guide_manuscript/cross_provider_coding/repair_codex.py verify C:\\xprov_runs gpt-6-luna

prepare  validates every out/P*.json of the model's sessions (same checks as agreement_xprov.py), backs up each
         invalid record to <run-root>/repair_backup/<model>/<session>/, and writes REPAIR.md into each affected
         session folder: the record files, their exact schema errors and the allowed values.
verify   compares each repaired record with its backup. The repair is accepted only if the analysed fields are
         unchanged (access, included.decision, included.stratum, rules R1-R4 verdicts) and the record now validates;
         otherwise the backup is restored and the record stays invalid (skipped by the analysis). Removes REPAIR.md.
"""
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import agreement_xprov as ax  # noqa: E402

SCHEMA = json.loads((HERE / "kit/coding_schema.json").read_text(encoding="utf-8"))
KIT_PIDS = {line.split()[1] for q in (HERE / "kit/queues").glob("queue_*.txt")
            for line in q.read_text(encoding="utf-8").splitlines() if line.startswith("- P")}


def analysed(r):
    inc = r.get("included") or {}
    return (r.get("access"), inc.get("decision"), inc.get("stratum"),
            tuple((r.get("rules") or {}).get(k, {}).get("verdict") for k in ("R1", "R2", "R3", "R4")))


def allowed_values():
    rep = SCHEMA["properties"]["reporting"]["properties"]
    return "\n".join(f"- `reporting.{k}`: {', '.join(repr(v) for v in d['enum'])}" for k, d in rep.items() if "enum" in d)


def main():
    mode, run_root, model = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
    sessions = sorted(d for d in (run_root / "sessions" / model).glob("q*") if d.is_dir())
    backup_root = run_root / "repair_backup" / model
    n_bad = n_ok = n_rejected = 0
    for s in sessions:
        if mode == "prepare":
            bad = {}
            for f in sorted((s / "out").glob("P*.json")):
                r, probs = ax.validate(f, SCHEMA, KIT_PIDS)
                if probs:
                    bad[f.name] = probs
            if not bad:
                continue
            (backup_root / s.name).mkdir(parents=True, exist_ok=True)
            for name in bad:
                shutil.copyfile(s / "out" / name, backup_root / s.name / name)
            lines = ["# Format repair", "",
                     "Some records in `out/` do not validate against `coding_schema.json`. Repair only the problems "
                     "listed below.", "",
                     "- Do not read any article again and do not use the web.",
                     "- Do not change `access`, `included` (decision, reason, stratum) or any rule verdict, marker or "
                     "evidence. Change only the fields named in the problems.",
                     "- For a reporting field, choose the allowed value that your record's own evidence supports. "
                     "Put any qualification in `notes`, not in the field.",
                     "- A missing `stage` is `\"cross_provider_pass\"`. A missing `claim` or `reporting` object on an "
                     "excluded or unread record is added with the fields the record supports.",
                     "- Write each repaired record back to the same file as UTF-8 JSON without a byte-order mark.",
                     "- Stay in this folder. Reply with one line: the files repaired.", "",
                     "Allowed values:", allowed_values(), "", "Problems:"]
            for name, probs in bad.items():
                lines.append(f"- `out/{name}`: " + "; ".join(probs))
            (s / "REPAIR.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            n_bad += len(bad)
            print(f"{s.name}: {len(bad)} record(s) to repair")
        else:
            bdir = backup_root / s.name
            if not bdir.exists():
                continue
            for b in sorted(bdir.glob("P*.json")):
                f = s / "out" / b.name
                old = json.loads(b.read_text(encoding="utf-8-sig"))
                new, probs = ax.validate(f, SCHEMA, KIT_PIDS)
                if new is not None and not probs and analysed(new) == analysed(old):
                    n_ok += 1
                else:
                    shutil.copyfile(b, f)
                    n_rejected += 1
                    why = probs if probs else [f"analysed fields changed: {analysed(old)} -> {analysed(new) if new else None}"]
                    print(f"{s.name}/{b.name}: repair rejected, original restored ({'; '.join(why)[:200]})")
            (s / "REPAIR.md").unlink(missing_ok=True)
    if mode == "prepare":
        print(f"{n_bad} invalid record(s); backups in {backup_root}")
    else:
        print(f"accepted {n_ok}, rejected {n_rejected}")


if __name__ == "__main__":
    main()
