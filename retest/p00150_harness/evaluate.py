"""P00150 re-test scoring: image orientation, reconstruction check, compliance of every design by one evaluator.

    python -m retest.p00150_harness.evaluate      # conda env torch5090 (numpy, scipy)

1. Orientation: the stored top88 designs (min_Material, 64x64 images) are compared with our top88 designs (superlu
   timed run; fem2d element order reshaped to (nely, nelx)) under the 8 symmetries of the square. The symmetry with
   the smallest mean absolute difference over the 100 cases maps the article's images to fem2d order.
2. Reconstruction check (pre-registered): our superlu port's compliance at top88's stopping point, times
   COMPLIANCE_SCALE, lies within 1 % of the stored compliance on at least 95 of the 100 cases.
3. One evaluator for all designs: fem2d plane stress, E0 = 1, E_min = 1e-9, p = 3, unit load, SuperLU. It scores the
   stored top88 designs, the predictor's designs (continuous output, as the article evaluates them) and ours.
   Volume fraction = mean density.
Writes evidence/p00150_eval.json.
"""
import json
import pathlib
import sys

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.baseline.fem2d import element_dofs, element_stiffness  # noqa: E402
from retest.p00150_harness.problems import COMPLIANCE_SCALE, load_cases, load_top88, problem  # noqa: E402

RUNS = ROOT / "retest" / "runs" / "p00150"
SYMMETRIES = {
    "identity": lambda a: a, "flip_rows": lambda a: a[::-1, :], "flip_cols": lambda a: a[:, ::-1],
    "rot180": lambda a: a[::-1, ::-1], "transpose": lambda a: a.T, "transpose_flip_rows": lambda a: a.T[::-1, :],
    "transpose_flip_cols": lambda a: a.T[:, ::-1], "transpose_rot180": lambda a: a.T[::-1, ::-1]}


class Evaluator:
    def __init__(self, prob):
        self.prob = prob
        self.KE = element_stiffness(prob.nu)
        self.edof = element_dofs(prob.nelx, prob.nely)
        self.iK = np.repeat(self.edof, 8, axis=1).ravel()
        self.jK = np.tile(self.edof, (1, 8)).ravel()
        free = np.ones(prob.ndof, dtype=bool)
        free[prob.fixed] = False
        self.free = np.flatnonzero(free)

    def compliance(self, rho):
        p = self.prob
        rho = np.clip(np.asarray(rho, dtype=float).ravel(), 0.0, 1.0)
        E = p.Emin + rho ** p.penal * (p.E0 - p.Emin)
        K = sp.csr_matrix(((E[:, None] * self.KE.ravel()[None, :]).ravel(), (self.iK, self.jK)),
                          shape=(p.ndof, p.ndof))
        Kf = K[self.free][:, self.free].tocsc()
        u = np.zeros(p.ndof)
        u[self.free] = spsolve(Kf, p.force[self.free])
        res = np.linalg.norm(Kf @ u[self.free] - p.force[self.free]) / np.linalg.norm(p.force[self.free])
        return float(p.force @ u), float(rho.mean()), float(res)


def main():
    cases = load_cases()
    top = [load_top88(c["k"]) for c in cases]
    ours = np.load(RUNS / "superlu" / "designs.npz")
    ours_img = {c["k"]: ours[f"case{c['k']:03d}"].reshape(64, 64) for c in cases}
    err = {name: float(np.mean([np.abs(T(t["design"]) - ours_img[c["k"]]).mean() for c, t in zip(cases, top)]))
           for name, T in SYMMETRIES.items()}
    best = min(err, key=err.get)
    T = SYMMETRIES[best]
    scan = {r["case"]: r for r in json.loads((RUNS / "superlu" / "scan.json").read_text(encoding="utf-8"))["cases"]}
    pen = np.load(RUNS / "pen" / "designs.npz")
    gpu = np.load(RUNS / "gpu" / "designs.npz")
    rows, within = [], 0
    for c, t in zip(cases, top):
        ev = Evaluator(problem(c))
        k = c["k"]
        c_stop = scan[k]["c_at_stop"]
        rel = abs(c_stop * COMPLIANCE_SCALE - t["compliance"]) / t["compliance"] if c_stop is not None else None
        within += int(rel is not None and rel <= 0.01)
        c_top, v_top, _ = ev.compliance(T(t["design"]).ravel())
        c_pen, v_pen, r_pen = ev.compliance(T(pen[f"case{k:03d}"]).ravel())
        c_our, v_our, _ = ev.compliance(ours[f"case{k:03d}"])
        c_gpu, v_gpu, _ = ev.compliance(gpu[f"case{k:03d}"])
        rows.append({"case": k, "volfrac": c["volfrac"], "stored_compliance": t["compliance"],
                     "superlu_c_at_stop_scaled": c_stop * COMPLIANCE_SCALE if c_stop is not None else None,
                     "reconstruction_relative_error": rel,
                     "eval_stored_top88": {"c": c_top, "vol": v_top}, "eval_pen": {"c": c_pen, "vol": v_pen, "res": r_pen},
                     "eval_ours_superlu": {"c": c_our, "vol": v_our}, "eval_ours_gpu": {"c": c_gpu, "vol": v_gpu},
                     "stored_top88_time_s": t["time_s"]})
    out = {"orientation": {"best": best, "mean_abs_difference": err},
           "reconstruction_check": {"within_1pct": within, "n": len(cases), "pass": within >= 95},
           "evaluator": "fem2d plane stress, E0 = 1, E_min = 1e-9, p = 3, unit load, SuperLU; c in unit-load units "
                        f"(multiply by {COMPLIANCE_SCALE:.6g} for the article's units)",
           "cases": rows}
    (ROOT / "evidence" / "p00150_eval.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("orientation", "reconstruction_check")}, indent=1))
    g = [r["eval_pen"]["c"] / r["eval_ours_gpu"]["c"] for r in rows]
    print("PEN / ours (GPU) compliance: median", float(np.median(g)), "range", float(min(g)), float(max(g)))


if __name__ == "__main__":
    main()
