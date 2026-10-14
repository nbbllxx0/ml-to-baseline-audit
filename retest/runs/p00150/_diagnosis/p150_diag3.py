import sys
import numpy as np
sys.path.insert(0, r"E:\AI\ml-to-baseline-audit")
from retest.p00150_harness.problems import load_cases, load_top88, COMPLIANCE_SCALE
from retest.p00150_harness.evaluate import Evaluator
from retest.baseline.fem2d import Problem, node_id

def prob(case, dx=0, dy=0):
    ix, iy = case["load_node"]
    n = 64
    left = node_id(np.zeros(n + 1, dtype=np.int64), np.arange(n + 1), n)
    fixed = np.sort(np.concatenate([2 * left, 2 * left + 1]))
    f = np.zeros(2 * (n + 1) ** 2)
    k = node_id(min(64, 8 * ix + dx), min(64, max(0, 8 * iy + dy)), n)
    f[2 * k], f[2 * k + 1] = case["fx"], -case["fy"]
    return Problem("d", n, n, case["volfrac"], 3.0, fixed, f, penal=3.0, nu=0.3)

for c in load_cases()[:16]:
    t = load_top88(c["k"])
    d = t["design"]
    cc, _, _ = Evaluator(prob(c)).compliance(d.ravel())
    ix, iy = c["load_node"]
    # material density around the load node in the stored image (row = ey, col = ex in fem2d order)
    ex, ey = min(63, 8 * ix), min(63, 8 * iy)
    around = d[max(0, ey - 1):ey + 1, max(0, ex - 1):ex + 1].mean()
    print(c["k"], "load", (int(ix), int(iy)), "F", (round(c["fx"], 2), round(-c["fy"], 2)), "vf", round(c["volfrac"], 2),
          "ratio", round(t["compliance"] / (cc * COMPLIANCE_SCALE), 3), "density at load", round(float(around), 2))
