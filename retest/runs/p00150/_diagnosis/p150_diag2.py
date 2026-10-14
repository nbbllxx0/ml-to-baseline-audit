"""P00150 mapping diagnosis, step 2: is the stored design x (unfiltered) or xPhys? Emin sensitivity. Untimed."""
import sys
import numpy as np

sys.path.insert(0, r"E:\AI\ml-to-baseline-audit")
from retest.p00150_harness.problems import load_cases, load_top88, COMPLIANCE_SCALE  # noqa: E402
from retest.p00150_harness.evaluate import Evaluator  # noqa: E402
from retest.baseline.fem2d import Problem, node_id, filter_matrix  # noqa: E402

cases = load_cases()[:20]
H, Hs = filter_matrix(64, 64, 3.0)


def prob(case, emin=1e-9):
    ix, iy = case["load_node"]
    n = 64
    left = node_id(np.zeros(n + 1, dtype=np.int64), np.arange(n + 1), n)
    fixed = np.sort(np.concatenate([2 * left, 2 * left + 1]))
    f = np.zeros(2 * (n + 1) ** 2)
    k = node_id(8 * ix, 8 * iy, n)
    f[2 * k], f[2 * k + 1] = case["fx"], -case["fy"]
    return Problem("d", n, n, case["volfrac"], 3.0, fixed, f, penal=3.0, nu=0.3, Emin=emin)


for label, filt, emin in (("stored as xPhys, Emin 1e-9", False, 1e-9), ("filtered (H x/Hs), Emin 1e-9", True, 1e-9),
                          ("stored as xPhys, Emin 1e-3", False, 1e-3), ("filtered, Emin 1e-3", True, 1e-3)):
    r, vols = [], []
    for c in cases:
        t = load_top88(c["k"])
        d = t["design"].ravel()
        if filt:
            d = (H @ d) / Hs
        cc, vol, _ = Evaluator(prob(c, emin)).compliance(d)
        r.append(t["compliance"] / (cc * COMPLIANCE_SCALE))
        vols.append(vol - c["volfrac"])
    r = np.array(r)
    print(f"{label:30s} median {np.median(r):.4f} sd(log) {np.std(np.log(r)):.4f} range {r.min():.3f}-{r.max():.3f}"
          f" | vol - target: median {np.median(vols):+.4f}")
