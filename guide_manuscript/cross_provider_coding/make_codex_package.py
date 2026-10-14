"""Build codex_package/: the blind coding sessions for GPT-6-Sol and GPT-6-Luna in the Codex CLI.

    python guide_manuscript/cross_provider_coding/make_codex_package.py [--force]

Reads kit/ (checked against kit/MANIFEST.sha256 first) and the sources in codex/. Writes, per model:
  sessions/<model>/q01a ... q10b   20 coding sessions; each holds one half of a kit queue as queue.txt (the kit's
                                   lines, unchanged), the kit's instructions, protocol, schema and codes (byte
                                   copies), fetch.js and an AGENTS.md naming the model and the number of records
  sessions/<model>/referrals       the 17 referrals with REFERRAL_INSTRUCTIONS.md
  sessions/<model>/smoke           a tool check that uses no study record
and codex_home/config.toml, run_codex.ps1, RUN.md and MANIFEST.sha256 (LF, for `sha256sum -c`).
Halving the queues keeps each session to 5 or 6 articles, well inside one context window. Reads the repository only;
writes only codex_package/. Refuses to replace an existing package without --force.
"""
import argparse
import hashlib
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
KIT, SRC, PKG = HERE / "kit", HERE / "codex", HERE / "codex_package"
MODELS = ("gpt-6-sol", "gpt-6-luna")          # slugs from the local Codex model catalog (~/.codex/models_cache.json)
CODING_FILES = ("AGENT_INSTRUCTIONS.md", "PROTOCOL_masked.md", "coding_schema.json", "screening_codes.md")
REFERRAL_FILES = ("AGENT_INSTRUCTIONS.md", "REFERRAL_INSTRUCTIONS.md", "PROTOCOL_masked.md", "screening_codes.md",
                  "referrals.csv")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fill(template, model, n=None):
    text = (SRC / template).read_text(encoding="utf-8").replace("{model}", model)
    return text.replace("{n_records}", str(n)) if n is not None else text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    for line in (KIT / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        if sha(KIT / rel) != digest:
            sys.exit(f"kit file changed since its manifest was written: {rel}")
    if PKG.exists():
        if not args.force:
            sys.exit("codex_package/ exists; use --force to rebuild it")
        shutil.rmtree(PKG)
    for model in MODELS:
        base = PKG / "sessions" / model
        for q in sorted((KIT / "queues").glob("queue_*.txt")):
            lines = q.read_bytes().splitlines(keepends=True)
            half = (len(lines) + 1) // 2
            for tag, part in (("a", lines[:half]), ("b", lines[half:])):
                d = base / f"q{q.stem[-2:]}{tag}"
                d.mkdir(parents=True)
                (d / "queue.txt").write_bytes(b"".join(part))
                (d / "AGENTS.md").write_bytes(fill("AGENTS_coding.md.tmpl", model, len(part)).encode("utf-8"))
                for f in CODING_FILES:
                    shutil.copyfile(KIT / f, d / f)
                shutil.copyfile(SRC / "fetch.js", d / "fetch.js")
        d = base / "referrals"
        d.mkdir(parents=True)
        (d / "AGENTS.md").write_bytes(fill("AGENTS_referrals.md.tmpl", model).encode("utf-8"))
        for f in REFERRAL_FILES:
            shutil.copyfile(KIT / f, d / f)
        shutil.copyfile(SRC / "fetch.js", d / "fetch.js")
        d = base / "smoke"
        d.mkdir(parents=True)
        (d / "AGENTS.md").write_bytes(fill("AGENTS_smoke.md.tmpl", model).encode("utf-8"))
        shutil.copyfile(SRC / "fetch.js", d / "fetch.js")
    (PKG / "codex_home").mkdir()
    shutil.copyfile(SRC / "config.toml", PKG / "codex_home" / "config.toml")
    shutil.copyfile(SRC / "run_codex.ps1", PKG / "run_codex.ps1")
    shutil.copyfile(SRC / "RUN.md", PKG / "RUN.md")

    # every queue line appears exactly once per model, unchanged
    kit_lines = sorted(l for q in (KIT / "queues").glob("queue_*.txt") for l in q.read_bytes().splitlines())
    for model in MODELS:
        got = sorted(l for q in (PKG / "sessions" / model).glob("q*/queue.txt") for l in q.read_bytes().splitlines())
        if got != kit_lines:
            sys.exit(f"{model}: session queues differ from the kit queues")
    files = sorted(f for f in PKG.rglob("*") if f.is_file() and f.name != "MANIFEST.sha256")
    with open(PKG / "MANIFEST.sha256", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(f"{sha(f)}  {f.relative_to(PKG).as_posix()}\n" for f in files))
    n_sessions = {m: len([d for d in (PKG / "sessions" / m).iterdir() if d.is_dir()]) for m in MODELS}
    print(f"codex_package/: {len(files)} files; sessions per model {n_sessions}; {len(kit_lines)} queue lines per model")


if __name__ == "__main__":
    main()
