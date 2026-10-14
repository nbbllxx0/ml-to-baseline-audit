"""P00080 timed runs (protocol: v3/plan/CENSUS_PREREG.md §9, row "P00080 protocol").

    PIN_PCORES=1 v3/.venv/census-torch/Scripts/python.exe v3/runs/P00080/timing.py voroto   # ML side + quality
    ...                                                                        homog    # L1 unit: homogenization
    ...                                                                        cpu_iter # L1 unit: top88 iteration
    ...                                                                        gpu      # L2: v2 GPU SIMP

Writes timing/<mode>.json. 'gpu' reads timing/voroto.json for the matched-quality target.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import statistics
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = HERE / "work"
OUT = HERE / "timing"
REPEATS = 3
NELX, NELY, VOLFRAC = 1600, 800, 0.5
RMIN = 1.5 * NELY / 64


def pin():
    spec = importlib.util.spec_from_file_location("pin", ROOT / "tools" / "pin.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.pin_from_env()


def stats(t):
    return {"median_s": statistics.median(t), "min_s": min(t), "max_s": max(t), "repeats_s": t}


def notebook_ns():
    """Namespace of voronoi_TO.ipynb after its definition cells (0-16, 18, 20); cwd = work/notebooks."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.show = lambda *a, **k: plt.close("all")
    nb = json.loads((ROOT / "v3" / "third_party" / "VoroTO" / "notebooks" / "voronoi_TO.ipynb").read_text(encoding="utf-8"))
    cells = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    assert cells[17].lstrip().startswith("density, cell_params, u, convg_history = topopt(")
    os.chdir(WORK / "notebooks")
    sys.path.insert(0, str(WORK))
    ns = {"__name__": "__main__"}
    for i in list(range(17)) + [18, 20]:
        exec(compile(cells[i], f"<voronoi_TO cell {i}>", "exec"), ns)
    return ns, cells


def problem(rmin: float = RMIN):
    """VoroTO's MID_CANT_BEAM on the fine mesh: left edge clamped, unit downward load at the right-edge midpoint."""
    sys.path.insert(0, str(ROOT))
    from retest.baseline.fem2d import Problem, node_id
    left = node_id(np.zeros(NELY + 1, dtype=np.int64), np.arange(NELY + 1), NELX)
    fixed = np.sort(np.concatenate([2 * left, 2 * left + 1]))
    f = np.zeros(2 * (NELX + 1) * (NELY + 1))
    f[2 * node_id(NELX, NELY // 2, NELX) + 1] = -1.0
    return Problem("P00080_mid_cantilever", NELX, NELY, VOLFRAC, rmin, fixed, f)


def fine_compliance(rho_x_y: np.ndarray) -> dict:
    """Compliance of a (1600, 800) [x, y] density image, thresholded at 0.5, E_min 1e-9, on the v2 GPU solver."""
    import torch
    sys.path.insert(0, str(ROOT))
    from retest.baseline.fem2d import element_stiffness
    from retest.baseline.gmg2d import GMGSolver
    prob = problem()
    solid = (rho_x_y.T >= 0.5).astype(np.float64)          # (nely, nelx), row-major e = ey*nelx + ex, y up
    E = prob.Emin + solid.reshape(-1) * (prob.E0 - prob.Emin)
    solver = GMGSolver(prob, element_stiffness(prob.nu), device="cuda", dtype=torch.float64)
    solver.update(torch.as_tensor(E, device="cuda"))
    f = torch.as_tensor(prob.force, device="cuda", dtype=torch.float64)
    u, its, tres, fb = solver.solve(f, tol=1e-8, true_tol=1e-7, maxit=2000)
    return {"compliance": float(torch.dot(f, u)), "volume_fraction": float(solid.mean()), "pcg_its": its,
            "true_res": tres, "fallback": bool(fb)}


def voroto():
    import torch
    ns, cells = notebook_ns()
    runs = []
    for rep in range(REPEATS + 1):
        t0 = time.perf_counter()
        density, cell_params, u, hist = ns["topopt"](fe=ns["fe"], desired_vol_frac=ns["to_cfg"]["vol_frac"],
                                                     max_iter=ns["to_cfg"]["num_epochs"],
                                                     loss_params=ns["loss_params"], lr=ns["to_cfg"]["lr"])
        t_opt = time.perf_counter() - t0
        ns["cell_params"] = cell_params
        t1 = time.perf_counter()
        exec(compile(cells[19], "<cell 19>", "exec"), ns)
        exec(compile(cells[21], "<cell 21>", "exec"), ns)
        t_dehom = time.perf_counter() - t1
        img = np.asarray(ns["composite_img"])
        ev = fine_compliance(img)
        runs.append({"warmup": rep == 0, "t_topopt_s": t_opt, "t_dehomogenize_s": t_dehom,
                     "J_final": hist["obj"][-1], "vc_final": hist["vol_cons"][-1],
                     "homog_volume_fraction": float(torch.mean(density).item()), "image_shape": list(img.shape), **ev})
        print(runs[-1], flush=True)
    timed = [r for r in runs if not r["warmup"]]
    return {"runs": runs, "topopt": stats([r["t_topopt_s"] for r in timed]),
            "dehomogenize": stats([r["t_dehomogenize_s"] for r in timed]),
            "fine_compliance_median": statistics.median(r["compliance"] for r in timed),
            "J_median": statistics.median(r["J_final"] for r in timed)}


def homog():
    sys.path.insert(0, str(WORK))
    import homogenize
    import material
    mstr = np.load(WORK / "data" / "mstr_imgs_aniso_raw.npy", mmap_mode="r")
    H = homogenize.Homogenization(lx=1., ly=1., nelx=mstr.shape[1], nely=mstr.shape[2], phiInDeg=90.,
                                  matProp=material.MaterialConstants(youngs_modulus=1., poissons_ratio=0.3), penal=3.)
    per = []
    for rep in range(REPEATS + 1):
        t0 = time.perf_counter()
        for s in range(20):
            H.homogenize(np.array(mstr[s]))
        dt = (time.perf_counter() - t0) / 20
        if rep:
            per.append(dt)
    unit = statistics.median(per)
    return {"micro_mesh": list(mstr.shape[1:]), "unit": stats(per),
            "projection_concurrent_min": unit * 800 * 300 / 60, "article_unit_s": 0.132, "article_projection_min": 528}


def cpu_iter():
    sys.path.insert(0, str(ROOT))
    from retest.baseline import simp_cpu
    per = []
    for rep in range(REPEATS + 1):
        # rmin 1.5: CENSUS_PREREG §9 (the explicit filter at rmin 18.75 does not fit in memory)
        rec, _, _ = simp_cpu.run(problem(rmin=1.5), solver="superlu", iters=1)
        if rep:
            per.append(rec["t_total"] if "t_total" in rec else float(np.sum(rec["t_iter"])))
        print("cpu iter", per[-1] if rep else "warm-up", flush=True)
    unit = statistics.median(per)
    return {"unit": stats(per), "projection_bruteforce_min": unit * 300 / 60, "article_unit_min": 16.62,
            "article_projection_min": 4986}


def gpu():
    sys.path.insert(0, str(ROOT))
    from retest.baseline import simp_gpu
    target = json.loads((OUT / "voroto.json").read_text(encoding="utf-8"))["fine_compliance_median"]
    runs = []
    for rep in range(REPEATS + 1):
        rec, xPhys, _ = simp_gpu.run(problem(), iters=300)
        cum = np.cumsum(rec["t_iter"])
        hit = next((i for i, c in enumerate(rec["c"]) if c <= target), None)
        runs.append({"warmup": rep == 0, "t_setup_s": rec["t_setup"], "t_300_s": float(cum[-1]),
                     "c_final": rec["c"][-1], "vol_final": rec["vol"][-1],
                     "first_iter_at_target": hit, "t_to_target_s": float(cum[hit]) if hit is not None else None,
                     "fallbacks": int(sum(rec["fallback"]))})
        print(runs[-1], flush=True)
    timed = [r for r in runs if not r["warmup"]]
    out = {"target_compliance": target, "runs": runs, "t_300": stats([r["t_300_s"] for r in timed])}
    if all(r["t_to_target_s"] is not None for r in timed):
        out["t_to_target"] = stats([r["t_to_target_s"] for r in timed])
    return out


def main():
    mode = sys.argv[1]
    OUT.mkdir(exist_ok=True)
    meta = {"mode": mode, "pinning": pin(), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    res = {"voroto": voroto, "homog": homog, "cpu_iter": cpu_iter, "gpu": gpu}[mode]()
    meta["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (OUT / f"{mode}.json").write_text(json.dumps({"meta": meta, **res}, indent=1) + "\n", encoding="utf-8")
    print("wrote", OUT / f"{mode}.json")


if __name__ == "__main__":
    main()
