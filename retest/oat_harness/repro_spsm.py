"""Standalone reproduction attempt for the pyEDGE MultiGrid crash: CuPy and SciPy only, no OAT code.

    source retest/oat_harness/env.sh
    OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.repro_spsm [--outer 300] [--inner 60]

pyEDGE's MultiGrid coarse solve factors the coarsest matrix with cupyx.scipy.sparse.linalg.splu and calls .solve inside
every V-cycle. The crash surfaces in cuSPARSE spSM_solve after 15-35 optimizer iterations
(retest/logs/debug_mg_*.txt). This script repeats that library pattern on a synthetic SPD matrix of the same
coarsest-grid size: a plane-stress Q4 stiffness on a 16x16 grid (the coarsest level in both crash cases), with a
random SIMP-like density field and a clamped left edge. Each outer loop builds a new matrix and re-factors it; each
inner loop solves with a new right-hand side.
  * If it crashes, the fault lies in the CuPy / cuSPARSE / driver stack on this machine, independent of OAT's code.
  * If it does not crash, the test shows only that this pattern alone does not trigger it; OAT's own matrices or
    call sequence stay implicated, and nothing more is claimed.
Writes retest/logs/repro_spsm_<stamp>.txt.
"""
import argparse
import datetime as dt
import pathlib
import sys
import traceback

import numpy as np
import scipy.sparse as sp

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.baseline.fem2d import element_stiffness, element_dofs  # noqa: E402


def stiffness(nelx, nely, rho, KE):
    edofs = element_dofs(nelx, nely)                       # (n_el, 8), element = ey*nelx + ex
    ndof = 2 * (nelx + 1) * (nely + 1)
    rows = np.repeat(edofs, 8, axis=1).ravel()
    cols = np.tile(edofs, (1, 8)).ravel()
    vals = (KE.ravel()[None, :] * (1e-9 + rho[:, None] ** 3 * (1 - 1e-9))).ravel()
    K = sp.coo_matrix((vals, (rows, cols)), shape=(ndof, ndof)).tocsr()
    fixed = np.array([2 * (iy * (nelx + 1)) + c for iy in range(nely + 1) for c in (0, 1)])   # left edge, ix = 0
    free = np.setdiff1d(np.arange(ndof), fixed)
    return K[free][:, free].tocsc()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outer", type=int, default=300)
    ap.add_argument("--inner", type=int, default=60)
    ap.add_argument("--seed", type=int, default=20260924)
    args = ap.parse_args()
    import cupy as cp
    from cupyx.scipy.sparse import csc_matrix
    from cupyx.scipy.sparse.linalg import splu
    rng = np.random.default_rng(args.seed)
    KE = element_stiffness(1.0 / 3.0)
    nel = 16
    lines = [f"cupy {cp.__version__}; CUDA runtime {cp.cuda.runtime.runtimeGetVersion()}; "
             f"device {cp.cuda.runtime.getDeviceProperties(0)['name'].decode()}"]
    o = -1
    try:
        for o in range(args.outer):
            rho = np.clip(rng.random(nel * nel) ** 2, 0.0, 1.0)
            A = csc_matrix(stiffness(nel, nel, rho, KE))
            lu = splu(A)
            for _ in range(args.inner):
                b = cp.asarray(rng.standard_normal(A.shape[0]))
                x = lu.solve(b)
            cp.cuda.Device().synchronize()
            if o % 50 == 0:
                res = float(cp.linalg.norm(A @ x - b) / cp.linalg.norm(b))
                lines.append(f"outer {o}: n = {A.shape[0]}, relative residual {res:.2e}")
                print(lines[-1], flush=True)
        lines.append(f"completed {args.outer} factorizations x {args.inner} solves without error")
    except Exception:
        lines.append(f"FAILED at outer iteration {o}")
        lines.append(traceback.format_exc())
    text = "\n".join(lines)
    print(text[-3000:])
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "retest" / "logs" / f"repro_spsm_{stamp}.txt"
    out.write_text(text, encoding="utf-8")
    print("wrote", out.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
