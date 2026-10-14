"""OpenTO / NITO_test problems -> both codes' inputs (no torch, no cupy imports here).

A NITO_test row holds: topology (PNG, the SIMP ground truth), loads [[x, y, fx, fy], ...],
boundary conditions [[x, y, fix_x, fix_y], ...] in normalised coordinates, volume fraction.
OAT's evaluator does shape = image.size[::-1] = (H, W) and StructuredMesh2D(H, W, H/max, W/max), so the mesh
has nelx = H (image rows) and nely = W (image columns). pyEDGE numbers elements column-major,
e = ex*nely + ey (verified 2026-09-24, eval_designs --orientation-check), so the flattened image (row-major
over (H, W)) is exactly pyEDGE's element order. A node sits at (i*h, j*h) with h = 1/max(H, W), and the same
positions map onto fem2d nodes (ix, iy) = (round(x/h), round(y/h)). fem2d numbers elements row-major
(e = ey*nelx + ex); convert a fem2d design grid g (nely, nelx) to pyEDGE order with g.T.reshape(-1).
Sample selection is seeded and recorded so every re-test uses the same problem ids.
"""
import io
import pathlib
import random

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "retest" / "targets" / "hf" / "OpenTO_data"
SEED = 20260924


PARQUET = {"NITO_test": "NITO_test-00000-of-00001", "test": "test-00000-of-00001",
           "test_clean": "test_clean-00000-of-00001"}


def load_split(split="NITO_test"):
    """Rows of an OpenTO split. Uses pyarrow when available (oat env); otherwise the JSON cache written by
    `python -m retest.oat_harness.problems export` (same rows, same order; PNG bytes base64-encoded)."""
    try:
        import pyarrow.parquet as pq
        return pq.read_table(DATA / f"{PARQUET[split]}.parquet").to_pylist()
    except ModuleNotFoundError:
        import base64
        import json
        cache = DATA / f"{split}_cache.json"
        rows = json.loads(cache.read_text(encoding="utf-8"))
        for r in rows:
            r["topology"] = {"bytes": base64.b64decode(r["topology"]["b64"])}
        return rows


def export_cache(split="NITO_test"):
    import base64
    import json
    import pyarrow.parquet as pq
    rows = pq.read_table(DATA / f"{PARQUET[split]}.parquet").to_pylist()
    for r in rows:
        r["topology"] = {"b64": base64.b64encode(r["topology"]["bytes"]).decode("ascii")}
    out = DATA / f"{split}_cache.json"
    out.write_text(json.dumps(rows), encoding="utf-8")
    print(f"wrote {out} ({len(rows)} rows)")


def topology_array(row):
    from PIL import Image
    im = Image.open(io.BytesIO(row["topology"]["bytes"]))
    return np.array(im).astype(np.float64)


def select(rows, nx, ny, k, seed=SEED):
    """k problem indices of size nx x ny (image width x height), uniformly at random with a fixed seed."""
    from PIL import Image
    idx = [i for i, r in enumerate(rows)
           if Image.open(io.BytesIO(r["topology"]["bytes"])).size == (nx, ny)]
    rng = random.Random(seed)
    return sorted(rng.sample(idx, k)) if k < len(idx) else idx


def to_fem2d(row, nu=1.0 / 3.0, Emin=1e-9, rmin=1.5, penal=3.0):
    """Build a fem2d.Problem for our strong baseline from an OpenTO row (same physical positions)."""
    import sys
    sys.path.insert(0, str(ROOT))
    from retest.baseline.fem2d import Problem, node_id
    nx, ny = topology_array(row).shape                 # image (H, W) -> nelx = H, nely = W (OAT convention)
    h = 1.0 / max(nx, ny)
    ndof = 2 * (nx + 1) * (ny + 1)
    fixed = []
    for x, y, fx_, fy_ in row["boundary conditions"]:
        ix, iy = int(round(x / h)), int(round(y / h))
        n = node_id(ix, iy, nx)
        if fx_ > 0.5:
            fixed.append(2 * n)
        if fy_ > 0.5:
            fixed.append(2 * n + 1)
    f = np.zeros(ndof)
    for x, y, fx_, fy_ in row["loads"]:
        ix, iy = int(round(x / h)), int(round(y / h))
        n = node_id(ix, iy, nx)
        f[2 * n] += fx_
        f[2 * n + 1] += fy_
    return Problem(name="OpenTO", nelx=nx, nely=ny, volfrac=float(row["volume fraction"]), rmin=rmin,
                   fixed=np.unique(np.array(fixed, dtype=np.int64)), force=f, penal=penal, E0=1.0,
                   Emin=Emin, nu=nu, meta={"h": h})


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        export_cache(sys.argv[2] if len(sys.argv) > 2 else "NITO_test")
