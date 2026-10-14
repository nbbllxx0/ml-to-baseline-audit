import math, sys
import numpy as np
sys.path.insert(0, r"E:\AI\ml-to-baseline-audit")
from retest.p00150_harness.problems import load_cases, load_top88, COMPLIANCE_SCALE
from retest.p00150_harness import evaluate as ev_mod
from retest.baseline.fem2d import Problem, node_id

def ke(nu, strain):
    if strain:
        D = 1.0 / ((1 + nu) * (1 - 2 * nu)) * np.array([[1 - nu, nu, 0], [nu, 1 - nu, 0], [0, 0, (1 - 2 * nu) / 2]])
    else:
        D = 1.0 / (1 - nu * nu) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    xi_n = np.array([-1.0, 1.0, 1.0, -1.0]); eta_n = np.array([-1.0, -1.0, 1.0, 1.0]); g = 1 / math.sqrt(3)
    K = np.zeros((8, 8))
    for xi in (-g, g):
        for eta in (-g, g):
            dx = 2 * 0.25 * xi_n * (1 + eta * eta_n); dy = 2 * 0.25 * eta_n * (1 + xi * xi_n)
            B = np.zeros((3, 8)); B[0, 0::2] = dx; B[1, 1::2] = dy; B[2, 0::2] = dy; B[2, 1::2] = dx
            K += B.T @ D @ B * 0.25
    return K

def prob(case):
    ix, iy = case["load_node"]; n = 64
    ys = np.arange(0, n + 1, 8)
    left = node_id(np.zeros(len(ys), dtype=np.int64), ys, n)
    fixed = np.sort(np.concatenate([2 * left, 2 * left + 1]))
    f = np.zeros(2 * (n + 1) ** 2); k = node_id(8 * ix, 8 * iy, n)
    f[2 * k], f[2 * k + 1] = case["fx"], -case["fy"]
    return Problem("d", n, n, case["volfrac"], 3.0, fixed, f, penal=3.0, nu=0.3)

cases = load_cases()
for label, strain in (("plane stress", False), ("plane strain", True)):
    r = []
    for c in cases:
        t = load_top88(c["k"])
        e = ev_mod.Evaluator(prob(c)); e.KE = ke(0.3, strain)
        cc, _, _ = e.compliance(t["design"].ravel())
        r.append(t["compliance"] / (cc * COMPLIANCE_SCALE))
    r = np.array(r)
    print(f"{label:12s} n={len(r)} median {np.median(r):.5f} sd(log) {np.std(np.log(r)):.5f} range {r.min():.4f}-{r.max():.4f}"
          f" within 1%: {int(np.sum(np.abs(r - 1) <= 0.01))}")
