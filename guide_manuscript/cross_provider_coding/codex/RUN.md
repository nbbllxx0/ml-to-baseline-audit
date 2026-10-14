# Blind coding with GPT-6-Sol and GPT-6-Luna (Codex CLI)

This package runs the cross-provider check of `../README.md` with two OpenAI models in the Codex CLI:
`gpt-6-sol` and `gpt-6-luna` (slugs from your Codex model catalog). Per model it holds:
- 20 coding sessions (`q01a` to `q10b`), each with 5 or 6 of the 110 records;
- 1 referral session (the 17 re-screen referrals);
- 1 smoke session, a tool check that uses no study record.

All sessions of one model use the same settings: reasoning effort `high`, live web search, workspace-write sandbox
with network access, and no approvals (`codex_home/config.toml`).

## What was run (2026-09-26)

- **CLI.** The runner uses the Codex CLI bundled with the Codex desktop app (0.158.0-alpha.2.1). The npm CLI
  (0.147.0) failed: the server rejected `gpt-6-sol` from that client with a ChatGPT login.
- **Home.** The runs used `-DefaultHome`: your existing login, with `--ignore-user-config`, every setting of
  `codex_home/config.toml` passed as overrides, memories and 15 other features disabled, and `--ephemeral` (no
  session files). The separate home below needs a fresh ChatGPT sign-in, which only you can give. Your global
  `AGENTS.md` still loads in this mode; it holds no study content, and each session's `AGENTS.md` overrides its
  record-keeping rule.
- **Smoke test.** Both models passed: arXiv page, PDF text and web search. The blindness scan of the smoke logs gave
  0 DISCARD and 0 REVIEW hits.
- **Sandbox facts** (checked with `codex sandbox`): Node downloads work; `curl.exe` (Windows TLS) and Python
  `requests` (a proxy set by the sandbox) fail; writes outside the session folder are blocked; reads are not.

## Blindness on this machine

- **Separate Codex home.** Every session runs with `CODEX_HOME` set to `C:\xprov_runs\codex_home`. That home has no
  memories, no session history, no global `AGENTS.md`, and no plugins, skills, browser or computer use. Your usual
  Codex home ran the GPT audit of this project, and its memory store changed that day, so do not run the sessions from
  it.
- **Sessions outside the project.** The session folders live in `C:\xprov_runs\sessions`, away from the project.
- **Reads are not blocked.** On this machine the unelevated Windows sandbox cannot block reads outside the session
  folder; deny-read needs the elevated backend. Each agent is told to stay in its folder.
- **Discard rule.** `collect_codex.py` scans every event log. A session that touched the project folder, a Claude or
  Codex home, or the Claude scratch folders is discarded and run again in a fresh session.
- **Timing.** Run everything before the public repository release, which publishes the coded records.

## Steps

Run these in PowerShell from this folder (`guide_manuscript\cross_provider_coding\codex_package`).

1. **Set up** the session folders and the separate Codex home:
   ```
   powershell -ExecutionPolicy Bypass -File .\run_codex.ps1 -Action Setup
   ```
2. **Log in once** in the separate home (your ChatGPT sign-in; the runner only starts `codex login`):
   ```
   powershell -ExecutionPolicy Bypass -File .\run_codex.ps1 -Action Login
   ```
3. **Smoke test** (both models): arXiv page and PDF download, PDF text, web search.
   ```
   powershell -ExecutionPolicy Bypass -File .\run_codex.ps1 -Action Smoke
   C:\Users\<user>\anaconda3\python.exe -B ..\collect_codex.py C:\xprov_runs
   ```
   Both models must print `SMOKE OK`. In the collect report, the smoke lines must show 0 DISCARD. If they show many
   REVIEW lines, send me the report before the full run: the scan may need tuning to this Codex version's event
   format. The report lists all coding sessions as incomplete at this point; that is expected.
4. **Run** all sessions, four at a time, with a 180-minute limit per session:
   ```
   powershell -ExecutionPolicy Bypass -File .\run_codex.ps1 -Action Run -Parallel 4
   ```
   - Add `-Models gpt-6-sol` to run one model first.
   - Repeat the same command to resume: finished sessions are skipped, and unfinished ones keep their records.
   - `-Action Status` shows progress at any time.
5. **Collect** the records and check blindness:
   ```
   C:\Users\<user>\anaconda3\python.exe -B ..\collect_codex.py C:\xprov_runs
   ```
   - For a session with a DISCARD hit, delete its `out\` files and run it again:
     `-Action Run -Sessions <name> -Models <model>`.
   - Read the REVIEW lines. Failed turns (for example a usage limit) also appear here.
6. **Analyse** with base Anaconda:
   ```
   C:\Users\<user>\anaconda3\python.exe -B ..\agreement_xprov.py
   ```
   Then send me `..\results\xprov_summary.md`.

Time and usage depend on the model. The smoke test and the first finished sessions show the real figures: the
collect report gives token use per session.
