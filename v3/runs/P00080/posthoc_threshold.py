"""P00080 post hoc check (not pre-registered; labelled so in RESULT.md): score the v2 GPU SIMP designs the way the
VoroTO designs were scored, i.e. thresholded at 0.5 and evaluated at fine scale (timing.fine_compliance).

    v3/.venv/census-torch/Scripts/python.exe v3/runs/P00080/posthoc_threshold.py

The pre-registered matched-quality rule compares SIMP's own (penalized, grey) compliance with VoroTO's thresholded
fine-scale compliance. A grey design early in the run is not a buildable structure, so this check reports, at fixed
checkpoints, the thresholded design's compliance and volume fraction. Checkpoints: 9 (the pre-registered match), 20,
30, 50, 100, 150, 300 iterations; one untimed run per checkpoint. Writes timing/posthoc_threshold.json.
"""
from __future__ import annotations

import json
import sys

import numpy as np

import timing as T

CHECKPOINTS = [9, 20, 30, 50, 100, 150, 300]


def main():
    sys.path.insert(0, str(T.ROOT))
    from retest.baseline import simp_gpu
    target = json.loads((T.OUT / "voroto.json").read_text(encoding="utf-8"))
    out = {"voroto_fine_compliance_median": target["fine_compliance_median"],
           "voroto_fine_volume_fraction": [r["volume_fraction"] for r in target["runs"] if not r["warmup"]],
           "checkpoints": []}
    for k in CHECKPOINTS:
        rec, xPhys, _ = simp_gpu.run(T.problem(), iters=k)
        img = xPhys.reshape(T.NELY, T.NELX).T                 # (nelx, nely) [x, y], as the VoroTO image
        ev = T.fine_compliance(img)
        out["checkpoints"].append({"iterations": k, "t_iterations_s": float(np.sum(rec["t_iter"])),
                                   "penalized_compliance": rec["c"][-1], **ev})
        print(out["checkpoints"][-1], flush=True)
    (T.OUT / "posthoc_threshold.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
