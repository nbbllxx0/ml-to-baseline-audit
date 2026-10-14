"""P00140 classical side (protocol: v3/plan/CENSUS_PREREG.md §9, P00140 row).

    PIN_PCORES=1 v3/.venv/census-torch/Scripts/python.exe v3/runs/P00140/classical.py cpu_iter
    PIN_PCORES=1 v3/.venv/census-torch/Scripts/python.exe v3/runs/P00140/classical.py gpu

Meshes 1440×720 and 2400×1200 (the article's fine meshes), rmin 1.5, volume fraction 0.4. The load case only has to
be representative for the cost per iteration: left edge clamped, unit downward load at the right-edge midpoint.
cpu_iter: one iteration of the top88-faithful CPU SIMP (SuperLU), warm-up + 3 repeats; projection = unit × 1000
(the article's iteration count). gpu: v2 GPU SIMP, a 20-iteration warm-up, then 3 timed runs of 1000 iterations.
Writes timing/classical_<mode>.json.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import statistics
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MESHES = [(1440, 720), (2400, 1200)]
ARTICLE_S_PER_ITER = {"1440x720": 16.0, "2400x1200": 87.0}


def pin():
    spec = importlib.util.spec_from_file_location("pin", ROOT / "tools" / "pin.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.pin_from_env()


def problem(nelx, nely):
    sys.path.insert(0, str(ROOT))
    from retest.baseline.fem2d import Problem, node_id
    left = node_id(np.zeros(nely + 1, dtype=np.int64), np.arange(nely + 1), nelx)
    fixed = np.sort(np.concatenate([2 * left, 2 * left + 1]))
    f = np.zeros(2 * (nelx + 1) * (nely + 1))
    f[2 * node_id(nelx, nely // 2, nelx) + 1] = -1.0
    return Problem(f"P00140_cantilever_{nelx}x{nely}", nelx, nely, 0.4, 1.5, fixed, f)


def stats(t):
    return {"median_s": statistics.median(t), "min_s": min(t), "max_s": max(t), "repeats_s": t}


def cpu_iter():
    from retest.baseline import simp_cpu
    out = {}
    for nelx, nely in MESHES:
        per = []
        for rep in range(4):
            rec, _, _ = simp_cpu.run(problem(nelx, nely), solver="superlu", iters=1)
            if rep:
                per.append(float(np.sum(rec["t_iter"])))
            print(nelx, nely, "cpu iter", rec["t_iter"], flush=True)
        key = f"{nelx}x{nely}"
        out[key] = {"unit": stats(per), "projection_1000_s": statistics.median(per) * 1000,
                    "article_unit_s": ARTICLE_S_PER_ITER[key], "article_projection_s": ARTICLE_S_PER_ITER[key] * 1000}
    return out


def gpu():
    from retest.baseline import simp_gpu
    out = {}
    for nelx, nely in MESHES:
        simp_gpu.run(problem(nelx, nely), iters=20)                  # warm-up
        runs = []
        for rep in range(3):
            rec, _, _ = simp_gpu.run(problem(nelx, nely), iters=1000)
            runs.append({"t_setup_s": rec["t_setup"], "t_1000_s": rec["t_total"], "c_final": rec["c"][-1],
                         "change_final": rec["change"][-1], "fallbacks": int(sum(rec["fallback"])),
                         "first_iter_change_below_0.01": next((i for i, c in enumerate(rec["change"]) if c < 0.01), None)})
            print(nelx, nely, runs[-1], flush=True)
        key = f"{nelx}x{nely}"
        out[key] = {"runs": runs, "t_1000": stats([r["t_1000_s"] for r in runs]),
                    "per_iteration_median_s": statistics.median(r["t_1000_s"] for r in runs) / 1000,
                    "article_projection_s": ARTICLE_S_PER_ITER[key] * 1000}
    return out


def gpu_unit():
    """CENSUS_PREREG §9 (dev15): 2400×1200 unit cost in a fresh process, 100 iterations, no warm-up in the process;
    projection = median time of iterations 11-100 × 1000. Peak GPU memory recorded."""
    import torch
    from retest.baseline import simp_gpu
    rec, _, _ = simp_gpu.run(problem(2400, 1200), iters=100)
    t = rec["t_iter"][10:]
    return {"2400x1200": {"iterations": 100, "t_setup_s": rec["t_setup"], "t_iter_all_s": rec["t_iter"],
                          "per_iteration_median_s": statistics.median(t), "projection_1000_s": statistics.median(t) * 1000,
                          "max_memory_allocated_GiB": torch.cuda.max_memory_allocated() / 2**30,
                          "max_memory_reserved_GiB": torch.cuda.max_memory_reserved() / 2**30,
                          "fallbacks": int(sum(rec["fallback"])), "article_projection_s": 87000.0}}


def main():
    mode = sys.argv[1]
    meta = {"mode": mode, "pinning": pin(), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "concurrent": "P00647 L1 MATLAB run (one thread) active; see runs/P00647/CONCURRENT.log"}
    sys.path.insert(0, str(ROOT))
    res = {"cpu_iter": cpu_iter, "gpu": gpu, "gpu_unit": gpu_unit}[mode]()
    meta["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (HERE / "timing").mkdir(exist_ok=True)
    (HERE / "timing" / f"classical_{mode}.json").write_text(json.dumps({"meta": meta, **res}, indent=1) + "\n",
                                                             encoding="utf-8")
    print("written")


if __name__ == "__main__":
    main()
