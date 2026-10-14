"""HGTO re-test campaign (plan/BASELINE_PREREG.md §9, HGTO re-test row). Each run is a fresh process.

    python -m retest.hgto_harness.campaign reference   # (b) HGTO's SIMP-OC as released, 2 threads, timed
    python -m retest.hgto_harness.campaign validate    # (c) our GPU port in --validate mode, untimed
    python -m retest.hgto_harness.campaign gate        # equivalence gate; exits 1 on failure
    python -m retest.hgto_harness.campaign timed       # (c) timed, (a) HGTO on the GPU, (b) SIMP-OC with 6 threads

Timed runs: PIN_PCORES=1; the first run of a method-configuration pair is a discarded warm-up followed by three timed
repeats, unless it takes longer than 300 s, in which case it is the single timed run. Run folders:
retest/runs/hgto/<method>/<config>/r<k> with the run's stdout and stderr in r<k>.log. Existing folders are skipped,
so an interrupted campaign resumes where it stopped.
"""
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PY = r"C:\Users\YSL0\anaconda3\envs\hgto\python.exe"
CFG = ROOT / "retest" / "targets" / "HGTO" / "configs" / "linear2d"
CONFIGS = ["cantilever_120x40", "half_mbb", "inclined_cantilever", "cantilever_240x80", "cantilever_480x160",
           "cantilever_960x320"]
RUNS = ROOT / "retest" / "runs" / "hgto"
LONG_S = 300.0


def command(method, config, out):
    cfg = str(CFG / f"{config}.yaml")
    if method == "ours":
        return [PY, "-m", "retest.hgto_harness.run_ours", "--config", cfg, "--output", str(out)]
    if method == "ours_validate":
        return [PY, "-m", "retest.hgto_harness.run_ours", "--config", cfg, "--output", str(out), "--validate"]
    if method == "hgto_gpu":
        return [PY, "-m", "retest.hgto_harness.run_hgto_pinned", "run", "--config", cfg, "--output", str(out)]
    threads = {"oc2": "2", "oc6": "6"}[method]
    return [PY, "-m", "retest.hgto_harness.run_hgto_pinned", "run", "--config", cfg, "--output", str(out),
            "--method", "oc", "--threads", threads]


def run_once(method, config, k):
    out = RUNS / method / config / f"r{k}"
    if (out / "result.json").exists():
        return json.loads((out / "result.json").read_text(encoding="utf-8"))
    if out.exists():
        raise SystemExit(f"incomplete run folder {out}; inspect and remove it before resuming")
    out.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PIN_PCORES="1", PYTHONIOENCODING="utf-8")
    with open(out.parent / f"r{k}.log", "w", encoding="utf-8") as log:
        p = subprocess.run(command(method, config, out), cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                           timeout=4 * 3600)
    if p.returncode != 0 or not (out / "result.json").exists():
        raise SystemExit(f"{method} {config} r{k} failed (exit {p.returncode}); see {out.parent / f'r{k}.log'}")
    r = json.loads((out / "result.json").read_text(encoding="utf-8"))
    print(f"{method:14s} {config:22s} r{k} wall {r['wall_s']:9.2f} s  C {r['C_raw']:.10g}  {r.get('termination')}",
          flush=True)
    return r


def series(method, config):
    first = run_once(method, config, 0)
    if first["wall_s"] > LONG_S:
        return
    for k in (1, 2, 3):
        run_once(method, config, k)


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "reference":
        for c in CONFIGS:
            series("oc2", c)
    elif phase == "validate":
        for c in CONFIGS:
            run_once("ours_validate", c, 0)
    elif phase == "gate":
        from retest.hgto_harness.gate import main as gate
        sys.exit(gate())
    elif phase == "timed":
        for c in CONFIGS:
            for m in ("ours", "hgto_gpu", "oc6"):
                series(m, c)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
