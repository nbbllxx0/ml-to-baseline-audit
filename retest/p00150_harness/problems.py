"""The 100 validation problems of P00150 (Halle et al., Appl. Sci. 2021; Mendeley data, CC BY 4.0) as fem2d Problems.

Each row of inputrows_8x8.npz (float32, 325 values) is the predictor's input on the 8x8 coarse grid (9x9 nodes):
  * R_k (0..161): support flags, first 81 = x DOFs, next 81 = y DOFs; node index i = 9*ix + iy (column-major);
  * R_s (162..323): load components in the same layout (one unit load per case);
  * M_tar (324): target volume fraction.
All 100 cases clamp the nine left-edge nodes of the coarse grid and apply one unit point load (checked in
load_cases). On the 64x64 design grid a coarse node (ix, iy) is fine node (8*ix, 8*iy); fem2d numbers nodes with y
upwards. Mapping v2 (reconstruction diagnosis, plan/BASELINE_PREREG.md §9, P00150 rows; scripts and logs in
retest/runs/p00150/_diagnosis/):
  * supports: only the 9 fine nodes that coincide with the clamped coarse nodes are fixed (both DOFs), not the
    whole left edge; the full-edge reading (mapping v1) left stored-to-reproduced compliance ratios of 0.9-1.4;
  * loads: the input's y component is negated (the source frame has y pointing down); with v1's sign the ratios of
    the same stored designs ranged over a factor of about 30;
  * images: the stored 64x64 designs are in fem2d element order (row = ey) under this mapping.
Article settings (Table 2): p = 3, r_min = 3, nu = 0.3, E = 195,000 N/mm^2, force 100 N. The fem2d problems use E = 1
and a unit load; COMPLIANCE_SCALE converts to the article's units (c scales with F^2 / E).
"""
import io
import pathlib
import zipfile

import numpy as np

from retest.baseline.fem2d import Problem, node_id

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "retest" / "targets" / "P00150_mendeley" / "Validation Data.zip"
N, COARSE = 64, 8
RMIN, PENAL, NU = 3.0, 3.0, 0.3
COMPLIANCE_SCALE = 100.0 ** 2 / 195000.0


def load_inputs():
    with zipfile.ZipFile(DATA) as zf:
        return np.load(io.BytesIO(zf.read("inputrows_8x8.npz")))["arr_0"]


def load_top88(k):
    """Stored top88 result of case k: design (64x64), compliance (article units) and time (s)."""
    with zipfile.ZipFile(DATA) as zf:
        d = np.load(io.BytesIO(zf.read(f"outputrows_{k}_64x64.npz")))
        return {"design": d["min_Material"], "compliance": float(d["Nachgiebigkeit"]), "time_s": float(d["time_fe"]),
                "material_deviation": float(d["Materialabweichung"]), "grayness": float(d["Unbestimmtheit"])}


def load_cases():
    X = load_inputs().astype(np.float64)
    cases = []
    for k, row in enumerate(X):
        rk, rs, m = row[:162], row[162:324], float(row[324])
        fixed_nodes = [(i // 9, i % 9) for i in np.flatnonzero(rk[:81])]
        if sorted(fixed_nodes) != [(0, j) for j in range(9)] or not np.array_equal(rk[:81], rk[81:]):
            raise ValueError(f"case {k}: support is not the clamped left edge")
        loaded = sorted(set(np.flatnonzero(rs[:81])) | set(np.flatnonzero(rs[81:])))
        if len(loaded) != 1:
            raise ValueError(f"case {k}: expected one loaded node, found {len(loaded)}")
        i = loaded[0]
        fx, fy = rs[i], rs[81 + i]
        if abs(np.hypot(fx, fy) - 1.0) > 1e-5:
            raise ValueError(f"case {k}: load is not a unit vector")
        cases.append({"k": k, "load_node": (i // 9, i % 9), "fx": float(fx), "fy": float(fy), "volfrac": m})
    return cases


def problem(case, flip_y=False):
    """fem2d Problem for one case (mapping v2); flip_y reflects the whole case (iy -> 8 - iy with the y load negated),
    which leaves the compliance unchanged and mirrors the design image."""
    nel = N
    ix, iy = case["load_node"]
    fy = case["fy"]
    if flip_y:
        iy, fy = COARSE - iy, -fy
    ys = np.arange(0, nel + 1, 8)                    # the 9 fine nodes that coincide with the clamped coarse nodes
    left = node_id(np.zeros(len(ys), dtype=np.int64), ys, nel)
    fixed = np.sort(np.concatenate([2 * left, 2 * left + 1]))
    f = np.zeros(2 * (nel + 1) * (nel + 1))
    n = node_id(8 * ix, 8 * iy, nel)
    f[2 * n] = case["fx"]
    f[2 * n + 1] = -fy                                  # source frame: y points down
    return Problem(f"P00150_case{case['k']:03d}", nel, nel, case["volfrac"], RMIN, fixed, f, penal=PENAL, nu=NU,
                   meta={"case": case["k"], "flip_y": flip_y})
