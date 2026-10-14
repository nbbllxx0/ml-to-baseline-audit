"""Score a time-to-quality run, reusing scores from an earlier run where the design mask is identical.

    OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.ttq_rescore --run <new ttq run dir> --ref <scored ttq run dir>

OAT's evaluator scores only the design binarized at 0.5 (pyEDGE MinimumCompliance.FEA, thresshold=True; see
plan/BASELINE_PREREG.md §9), so two designs with the same mask have the same compliance. For each (problem, budget):
if the new design's mask equals the reference design's mask, the reference CE and volume are reused, and the record
says so; otherwise the design is scored with OAT's evaluator (retest/oat_harness/eval_designs.py). Timings always
come from the new run. Output: <run dir>/ttq.json, in the format of time_to_quality.py score, plus provenance fields.
"""
import argparse
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.oat_harness.problems import load_split, topology_array  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--ref", required=True)
    args = ap.parse_args()
    d, ref = ROOT / args.run, ROOT / args.ref
    meta = json.loads((d / "ttq_runs.json").read_text(encoding="utf-8"))
    ref_scores = {(r["problem_id"], r["iters"]): r for r in json.loads((ref / "ttq.json").read_text(encoding="utf-8"))}
    rows = load_split("NITO_test")
    out, n_reused, n_scored = [], 0, 0
    problems = {}
    for r in meta["runs"]:
        pid, k = r["problem_id"], r["iters"]
        x = np.load(d / f"design_{pid}_it{k:03d}.npz")["x_pyedge"]
        x_ref = np.load(ref / f"design_{pid}_it{k:03d}.npz")["x_pyedge"]
        flips = int(np.count_nonzero((x > 0.5) != (x_ref > 0.5)))
        rs = ref_scores.get((pid, k))
        if flips == 0 and rs is not None:
            out.append({**r, "c_gt": rs["c_gt"], "c_oat_eval": rs["c_oat_eval"], "CE_pct": rs["CE_pct"],
                        "vf_thresholded": float((x > 0.5).mean()), "score_source": f"reused from {args.ref}",
                        "mask_flips_vs_ref": 0, "max_abs_dx_vs_ref": float(np.abs(x - x_ref).max())})
            n_reused += 1
        else:
            from retest.oat_harness.eval_designs import evaluator, compliance
            if pid not in problems:
                problem, _ = evaluator(rows[pid])
                problems[pid] = (problem, compliance(problem, (topology_array(rows[pid]) > 0).astype(np.float64)))
            problem, c_gt = problems[pid]
            c = compliance(problem, x)
            out.append({**r, "c_gt": c_gt, "c_oat_eval": c, "CE_pct": (c - c_gt) / c_gt * 100.0,
                        "vf_thresholded": float((x > 0.5).mean()), "score_source": "scored",
                        "mask_flips_vs_ref": flips, "max_abs_dx_vs_ref": float(np.abs(x - x_ref).max())})
            n_scored += 1
        print(f"problem {pid} K={k:3d}: CE {out[-1]['CE_pct']:7.2f}%  ({out[-1]['score_source'][:6]}, flips {flips})",
              flush=True)
    (d / "ttq.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"reused {n_reused}, scored {n_scored}; wrote {(d / 'ttq.json').relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
