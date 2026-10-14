import sys
import numpy as np
sys.path.insert(0, r"E:\AI\ml-to-baseline-audit")
from retest.p00150_harness.problems import load_cases, load_top88, COMPLIANCE_SCALE
from retest.p00150_harness.evaluate import Evaluator
from retest.baseline.fem2d import Problem, node_id

def prob(case, support):
    ix, iy = case["load_node"]
    n = 64
    ys = np.arange(0, n + 1, 8) if support == "coarse nodes only" else np.arange(n + 1)
    left = node_id(np.zeros(len(ys), dtype=np.int64), ys, n)
    fixed = np.sort(np.concatenate([2 * left, 2 * left + 1]))
    f = np.zeros(2 * (n + 1) ** 2)
    k = node_id(8 * ix, 8 * iy, n)
    f[2 * k], f[2 * k + 1] = case["fx"], -case["fy"]
    return Problem("d", n, n, case["volfrac"], 3.0, fixed, f, penal=3.0, nu=0.3)

cases = load_cases()[:30]
for support in ("full left edge", "coarse nodes only"):
    r = []
    for c in cases:
        t = load_top88(c["k"])
        cc, _, _ = Evaluator(prob(c, support)).compliance(t["design"].ravel())
        r.append(t["compliance"] / (cc * COMPLIANCE_SCALE))
    r = np.array(r)
    print(f"{support:18s} median {np.median(r):.4f} sd(log) {np.std(np.log(r)):.4f} range {r.min():.3f}-{r.max():.3f}")
    print("   ", np.round(r[:16], 3))
