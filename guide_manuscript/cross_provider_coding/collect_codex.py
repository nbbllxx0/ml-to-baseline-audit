"""Collect the Codex runs into returned/<model>/ and check every session for blindness and completeness.

    python guide_manuscript/cross_provider_coding/collect_codex.py C:\\xprov_runs [--models gpt-6-sol gpt-6-luna] [--force]

Reads <run-root>/sessions/<model>/<session>/ (queue.txt or referrals.csv, and out/) and every event log
<run-root>/logs/<model>/<session>/events-*.jsonl that `codex exec --json` wrote for an attempt of the session.

Blindness scan (the rule fixed in README.md before any run):
  DISCARD  any event names the project folder, a Claude or Codex home folder or the Claude scratch folders. The
           session's records are not copied; delete its out/ files and run it again in a fresh session.
  REVIEW   an agent action (command, file change, search query, tool call or code; not tool output) names another
           absolute path outside the session folder (system and tool folders excepted), another drive, this run's
           Codex home, a study keyword or the paper's title. Read the lines and decide; these sessions are copied.
Completeness: every pid of queue.txt has out/<pid>.json and no other pid is there; referrals.json holds the 17 pids.
Also reported: failed turns and errors (for example a usage limit), and token use per session.
Copies the records of sessions without a DISCARD hit into returned/<model>/, referrals.json into
returned/<model>/referrals.json and each RUN_LOG.md into returned/<model>/logs/<session>.md, and writes
returned/<model>/COLLECT_REPORT.md. Refuses to overwrite a returned file whose content differs unless --force.
Exit status 1 when a session is discarded or incomplete. Standard library only.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PASSIVE = {"agent_message", "reasoning", "todo_list", "plan", "plan_update"}
OUTPUT_KEYS = {"aggregated_output", "output", "stdout", "stderr", "result", "formatted_output"}
KEYWORDS = re.compile(r"llm_prefill|second_pass|adjudicat|audit[\\/]+coding|numbers_review|ESM_\d|online resource|"
                      r"classical baseline shapes", re.I)
PID_LINE = re.compile(r"^- (P\d{5}) ")
ABS_PATH = re.compile(r"(?<![\w/])([A-Za-z]):[\\/][^\s\"'`<>|*?;,)]*")
BARE_DRIVE = re.compile(r"(?<![\w:/\\'\"{,])([A-Z]):(?![\\/\w])")   # e.g. "cd /d E:"; not "{a: 1}" in code


def path_rx(p):
    """Regex for a Windows path written with either slash, any case."""
    parts = [re.escape(x) for x in re.split(r"[\\/]+", str(p).rstrip("\\/")) if x]
    return r"[\\/]+".join(parts)


def strings(x, skip_outputs, key=None):
    if isinstance(x, dict):
        for k, v in x.items():
            if skip_outputs and k in OUTPUT_KEYS:
                continue
            yield from strings(v, skip_outputs, k)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v, skip_outputs, key)
    elif isinstance(x, str):
        yield x


def allowed_prefixes(session_dir):
    env = os.environ
    pre = [session_dir, env.get("SystemRoot", r"C:\Windows"), env.get("ProgramFiles", r"C:\Program Files"),
           env.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), env.get("TEMP", ""),
           os.path.join(env.get("LOCALAPPDATA", ""), "Programs")]
    for tool in ("node", "pdftotext", "python"):
        found = shutil.which(tool)
        if found:
            pre.append(str(pathlib.Path(found).parent.parent))
    return [p.lower().replace("/", "\\").rstrip("\\") for p in pre if p]


def scan_session(log_dir, session_dir, run_root):
    discard_rx = re.compile("|".join([path_rx(ROOT), r"ml-to-baseline", r"[\\/]\.claude(?![\w-])", r"[\\/]\.codex(?![\w-])",
                                      r"appdata[\\/]+local[\\/]+temp[\\/]+claude"]), re.I)
    home_rx = re.compile(path_rx(pathlib.Path(run_root) / "codex_home"), re.I)
    allow = allowed_prefixes(str(session_dir))
    run_drive = str(run_root)[0].lower()
    hits = {"discard": [], "review": []}
    stats = {"attempts": 0, "events": 0, "bad_lines": 0, "failed_turns": 0, "errors": [], "input_tokens": 0,
             "output_tokens": 0}
    for f in sorted(pathlib.Path(log_dir).glob("events-*.jsonl")) if pathlib.Path(log_dir).exists() else []:
        stats["attempts"] += 1
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not line.strip():
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                stats["bad_lines"] += 1
                continue
            stats["events"] += 1
            where = f"{f.name}:{n}"
            etype = ev.get("type", "")
            if etype == "turn.failed" or etype == "error":
                stats["failed_turns"] += etype == "turn.failed"
                stats["errors"].append(f"{where} {json.dumps(ev)[:200]}")
            usage = ev.get("usage") or {}
            stats["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
            stats["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
            for s in strings(ev, skip_outputs=False):
                m = discard_rx.search(s)
                if m:
                    hits["discard"].append(f"{where} [{etype}] ...{s[max(0, m.start() - 60):m.end() + 60]}...")
            item = ev.get("item") or {}
            if not item or item.get("type") in PASSIVE:
                continue
            for s in strings(item, skip_outputs=True):
                for m in ABS_PATH.finditer(s):
                    p = re.sub(r"[\\/]+", r"\\", m.group(0).lower()).rstrip("\\.")   # commands carry doubled backslashes
                    if not any(p == a or p.startswith(a + "\\") for a in allow):
                        hits["review"].append(f"{where} [{item.get('type')}] outside path: {m.group(0)[:160]}")
                for m in BARE_DRIVE.finditer(s):
                    if m.group(1).lower() != run_drive:
                        hits["review"].append(f"{where} [{item.get('type')}] other drive: ...{s[max(0, m.start() - 40):m.end() + 40]}...")
                for rx, label in ((home_rx, "run Codex home"), (KEYWORDS, "study keyword or title")):
                    m = rx.search(s)
                    if m:
                        hits["review"].append(f"{where} [{item.get('type')}] {label}: ...{s[max(0, m.start() - 60):m.end() + 60]}...")
    for k in hits:                                   # the same hit can repeat across started/updated/completed events
        hits[k] = list(dict.fromkeys(hits[k]))
    return hits, stats


def copy_file(src, dst, force):
    if dst.exists() and dst.read_bytes() != src.read_bytes() and not force:
        raise SystemExit(f"{dst} exists with different content; rerun with --force to replace it")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_root")
    ap.add_argument("--models", nargs="+", default=["gpt-6-sol", "gpt-6-luna"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # run logs may hold a BOM; the console may be GBK
    run_root = pathlib.Path(args.run_root).resolve()
    bad = False
    for model in args.models:
        sroot = run_root / "sessions" / model
        if not sroot.exists():
            print(f"{model}: no sessions under {sroot}")
            bad = True
            continue
        dest = HERE / "returned" / model
        report = [f"# Collect report: {model}", "", f"Run root: `{run_root}`", "",
                  "| Session | Expected | Done | Missing | Extra | Attempts | Failed turns | Tokens in/out | DISCARD | REVIEW | Copied |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        details, copied_pids = [], {}
        for sdir in sorted(d for d in sroot.iterdir() if d.is_dir()):
            name = sdir.name
            out = sdir / "out"
            hits, st = scan_session(run_root / "logs" / model / name, sdir, run_root)
            if name == "smoke":
                ok = (out / "smoke.json").exists()
                details.append(f"- smoke: out/smoke.json {'present' if ok else 'missing'}; {len(hits['discard'])} DISCARD, "
                               f"{len(hits['review'])} REVIEW")
                continue
            if name == "referrals":
                want = [line.split(",")[0] for line in (sdir / "referrals.csv").read_text(encoding="utf-8").splitlines()[1:]
                        if re.match(r"P\d{5},", line)]
                got = []
                if (out / "referrals.json").exists():
                    try:
                        got = [g.get("pid") for g in json.loads((out / "referrals.json").read_text(encoding="utf-8-sig"))]
                    except ValueError:
                        got = []
            else:
                want = [m.group(1) for line in (sdir / "queue.txt").read_text(encoding="utf-8").splitlines()
                        for m in [PID_LINE.match(line)] if m]
                got = [f.stem for f in out.glob("P*.json")] if out.exists() else []
            missing = sorted(set(want) - set(got))
            extra = sorted(set(got) - set(want))
            discard = bool(hits["discard"])
            copied = 0
            if not discard:
                if name == "referrals":
                    if got:
                        copy_file(out / "referrals.json", dest / "referrals.json", args.force)
                        copied = len(set(got) & set(want))
                else:
                    for pid in sorted(set(got) & set(want)):
                        if pid in copied_pids:
                            raise SystemExit(f"{model}: {pid} is coded in both {copied_pids[pid]} and {name}")
                        copied_pids[pid] = name
                        copy_file(out / f"{pid}.json", dest / f"{pid}.json", args.force)
                        copied += 1
                if (out / "RUN_LOG.md").exists():
                    copy_file(out / "RUN_LOG.md", dest / "logs" / f"{name}.md", args.force)
            bad |= discard or bool(missing) or bool(extra)
            report.append(f"| {name} | {len(want)} | {len(set(got) & set(want))} | {len(missing)} | {len(extra)} | "
                          f"{st['attempts']} | {st['failed_turns']} | {st['input_tokens']:,}/{st['output_tokens']:,} | "
                          f"{len(hits['discard'])} | {len(hits['review'])} | {copied} |")
            if missing:
                details.append(f"- {name}: missing {', '.join(missing)}")
            if extra:
                details.append(f"- {name}: pids outside its queue {', '.join(extra)} (not copied)")
            for k in ("discard", "review"):
                for h in hits[k][:25]:
                    details.append(f"- {name} {k.upper()}: {h}")
                if len(hits[k]) > 25:
                    details.append(f"- {name} {k.upper()}: {len(hits[k]) - 25} more")
            for e in st["errors"][:5]:
                details.append(f"- {name} error: {e}")
            log = out / "RUN_LOG.md"
            if log.exists():
                for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
                    if re.search(r"accident|blind|outside this folder|study's", line, re.I):
                        details.append(f"- {name} RUN_LOG: {line.strip()[:200]}")
        report += ["", "## Details", ""] + (details or ["None."]) + [
            "", "Sessions with a DISCARD hit were not copied. Delete their out/ files, then run them again with "
                "`run_codex.ps1 -Action Run -Sessions <name>`.", ""]
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "COLLECT_REPORT.md").write_text("\n".join(report), encoding="utf-8")
        print("\n".join(report))
    print("Next: C:\\Users\\<user>\\anaconda3\\python.exe -B guide_manuscript/cross_provider_coding/agreement_xprov.py")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
