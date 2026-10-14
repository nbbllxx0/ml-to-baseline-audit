"""Evaluate designs with OAT's own compliance evaluator (scripts/RunComplianceTest.py logic), in-process.

Run in the CuPy-only process type:
    source retest/oat_harness/env.sh
    OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.eval_designs --orientation-check
    OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.eval_designs --size 256 --ids 12,34 \
        --oat-infer <run dir> --oat-simp <run dir> [--oat-simp ...] --ours <run dir> [--ours <run dir> ...]

The evaluator follows RunComplianceTest.simulate_optimize:
  * StructuredMesh2D(nx, ny, nx/max, ny/max);
  * StructuredFilter2D(mesh, 1.5);
  * SPSOLVE;
  * MinimumCompliance(void=1e-6, heavyside=False);
  * ground truth as desvars = (gt > 0);
  * a candidate as desvars = design variables.
Compliance error is CE = (c - c_gt)/c_gt * 100. Volume fraction is (desvars > 0.5).mean().
It reproduces OAT's metric definitions, including its choice of void = 1e-6 for evaluation.
"""
import argparse
import glob
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.oat_harness.problems import load_split, topology_array  # noqa: E402


def evaluator(row):
    from pyEDGE.CUDA import (StructuredMesh2D, StructuredStiffnessKernel, StructuredFilter2D, FiniteElement,
                             MinimumCompliance, SPSOLVE)
    shape = topology_array(row).shape                 # (H, W), as OAT: image.size[::-1]
    mesh = StructuredMesh2D(shape[0], shape[1], shape[0] / max(shape), shape[1] / max(shape))
    kernel = StructuredStiffnessKernel(mesh)
    filt = StructuredFilter2D(mesh, 1.5)
    FE = FiniteElement(mesh, kernel, SPSOLVE(kernel))
    FE.reset_dirichlet_boundary_conditions()
    FE.reset_forces()
    bc, loads = np.array(row["boundary conditions"]), np.array(row["loads"])
    FE.add_dirichlet_boundary_condition(positions=bc[:, 0:2], dofs=bc[:, 2:])
    FE.add_point_forces(positions=loads[:, 0:2], forces=loads[:, 2:])
    problem = MinimumCompliance(FE, filt, void=1e-6, volume_fraction=[float(row["volume fraction"])],
                                heavyside=False)
    return problem, mesh


def compliance(problem, desvars):
    problem.desvars = np.asarray(desvars, dtype=np.float64).reshape(-1)
    c = problem.FEA()["compliance"]
    return float(c.get()) if hasattr(c, "get") else float(c)


def orientation_check():
    import cupy
    from pyEDGE.CUDA import StructuredMesh2D
    mesh = StructuredMesh2D(4, 3, 1.0, 0.75)
    el = cupy.asnumpy(mesh.elements)
    nodes = cupy.asnumpy(mesh.nodes)
    cent = nodes[el].mean(axis=1)
    print("pyEDGE 4x3 mesh: element centroids in index order (expect x fastest, y from 0 upward):")
    for e in range(min(8, len(cent))):
        print(f"  e={e}: ({cent[e, 0]:.3f}, {cent[e, 1]:.3f})")
    row_major = all(abs(cent[e, 0] - ((e % 4) + 0.5) * 0.25) < 1e-9 and abs(cent[e, 1] - ((e // 4) + 0.5) * 0.25) < 1e-9
                    for e in range(len(cent)))
    col_major = all(abs(cent[e, 0] - ((e // 3) + 0.5) * 0.25) < 1e-9 and abs(cent[e, 1] - ((e % 3) + 0.5) * 0.25) < 1e-9
                    for e in range(len(cent)))
    print("row-major (e = ey*nelx + ex):", row_major, "| column-major (e = ex*nely + ey):", col_major)
    return col_major


def load_candidates(args, pid):
    cands = {}
    if args.oat_infer:
        f = pathlib.Path(args.oat_infer) / f"generated_{pid}.npz"
        if f.exists():
            cands["OAT"] = np.load(f)["x"]
    for d in args.oat_simp or []:
        for f in glob.glob(str(pathlib.Path(d) / f"design_{pid}_*.npz")):
            tag = pathlib.Path(f).stem.replace(f"design_{pid}_", "")
            cands[f"OAT-SIMP[{tag}]"] = np.load(f)["x"]
    for d in args.ours or []:
        f = pathlib.Path(d) / f"design_{pid}.npz"
        if f.exists():
            cands[f"ours[{pathlib.Path(d).name.split('_')[2]}]"] = np.load(f)["x_pyedge"]
    return cands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orientation-check", action="store_true")
    ap.add_argument("--size", type=int)
    ap.add_argument("--ids", default="")
    ap.add_argument("--oat-infer")
    ap.add_argument("--oat-simp", action="append")
    ap.add_argument("--ours", action="append")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    if args.orientation_check:
        orientation_check()
        return
    rows = load_split("NITO_test")
    ids = [int(s) for s in args.ids.split(",") if s]
    report = []
    for pid in ids:
        row = rows[pid]
        problem, _ = evaluator(row)
        gt = topology_array(row)
        c_gt = compliance(problem, (gt > 0).astype(np.float64))
        entry = {"problem_id": pid, "c_gt": c_gt, "vf_target": float(row["volume fraction"]), "candidates": {}}
        for name, x in load_candidates(args, pid).items():
            x = np.asarray(x, dtype=np.float64)
            c = compliance(problem, x)
            entry["candidates"][name] = {"c": c, "CE_pct": (c - c_gt) / c_gt * 100.0,
                                         "vf_thresholded": float((x.reshape(-1) > 0.5).mean()),
                                         "vf_mean": float(x.mean())}
        report.append(entry)
        print(json.dumps(entry, indent=None)[:600], flush=True)
    out = pathlib.Path(args.out) if args.out else ROOT / "evidence" / f"oat_eval_n{args.size}.json"
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
