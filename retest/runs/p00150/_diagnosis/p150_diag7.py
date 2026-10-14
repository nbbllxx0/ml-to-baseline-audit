"""P00150 diagnosis step 7: per-direction support extent (untimed; stored designs evaluated)."""
import sys
import numpy as np
sys.path.insert(0, r"E:\AI\ml-to-baseline-audit")
from retest.p00150_harness.problems import load_cases, load_top88, COMPLIANCE_SCALE
from retest.p00150_harness.evaluate import Evaluator
from retest.baseline.fem2d import Problem, node_id

def prob(case, x_full, y_full):
    ix, iy = case["load_node"]; n = 64
    allys, coarse = np.arange(n + 1), np.arange(0, n + 1, 8)
    lx = node_id(np.zeros(len(allys if x_full else coarse), dtype=np.int64), allys if x_full else coarse, n)
    ly = node_id(np.zeros(len(allys if y_full else coarse), dtype=np.int64), allys if y_full else coarse, n)
    fixed = np.sort(np.concatenate([2 * lx, 2 * ly + 1]))
    f = np.zeros(2 * (n + 1) ** 2); k = node_id(8 * ix, 8 * iy, n)
    f[2 * k], f[2 * k + 1] = case["fx"], -case["fy"]
    return Problem("d", n, n, case["volfrac"], 3.0, fixed, f, penal=3.0, nu=0.3)

cases = load_cases()
for x_full, y_full in ((False, False), (True, False), (False, True), (True, True)):
    r = []
    for c in cases:
        t = load_top88(c["k"])
        cc, _, _ = Evaluator(prob(c, x_full, y_full)).compliance(t["design"].ravel())
        r.append(t["compliance"] / (cc * COMPLIANCE_SCALE))
    r = np.array(r)
    print(f"x full edge={x_full!s:5s} y full edge={y_full!s:5s} within 1%: {int(np.sum(abs(r - 1) <= 0.01)):3d} "
          f"median {np.median(r):.4f} range {r.min():.3f}-{r.max():.3f}")
