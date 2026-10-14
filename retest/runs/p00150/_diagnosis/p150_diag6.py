import sys
import numpy as np
sys.path.insert(0, r"E:\AI\ml-to-baseline-audit")
from retest.p00150_harness.problems import load_cases, load_top88, COMPLIANCE_SCALE
from retest.p00150_harness.evaluate import Evaluator
from retest.baseline.fem2d import Problem, node_id, filter_matrix
H, Hs = filter_matrix(64, 64, 3.0)

def prob(case, emin=1e-9):
    ix, iy = case["load_node"]; n = 64
    ys = np.arange(0, n + 1, 8)
    left = node_id(np.zeros(len(ys), dtype=np.int64), ys, n)
    fixed = np.sort(np.concatenate([2 * left, 2 * left + 1]))
    f = np.zeros(2 * (n + 1) ** 2); k = node_id(8 * ix, 8 * iy, n)
    f[2 * k], f[2 * k + 1] = case["fx"], -case["fy"]
    return Problem("d", n, n, case["volfrac"], 3.0, fixed, f, penal=3.0, nu=0.3, Emin=emin)

rows = []
for c in load_cases():
    t = load_top88(c["k"]); d = t["design"].ravel()
    base = Evaluator(prob(c)).compliance(d)[0]
    filt = Evaluator(prob(c)).compliance((H @ d) / Hs)[0]
    e3 = Evaluator(prob(c, 1e-3)).compliance(d)[0]
    rows.append((t["compliance"] / (base * COMPLIANCE_SCALE), t["compliance"] / (filt * COMPLIANCE_SCALE),
                 t["compliance"] / (e3 * COMPLIANCE_SCALE), c, t))
rows.sort(key=lambda r: r[0])
for r0, rf, re3, c, t in rows[:12]:
    print(c["k"], "ratio", round(r0, 4), "filtered", round(rf, 4), "Emin1e-3", round(re3, 4), "load", tuple(int(v) for v in c["load_node"]),
          "F", (round(c["fx"], 2), round(-c["fy"], 2)), "vf", round(c["volfrac"], 2), "gray", round(t["grayness"], 3),
          "Filter", round(t["material_deviation"], 4))
r = np.array([x[0] for x in rows]); rfv = np.array([x[1] for x in rows]); r3 = np.array([x[2] for x in rows])
print("within 1%: base", int(np.sum(abs(r - 1) <= .01)), "filtered", int(np.sum(abs(rfv - 1) <= .01)), "Emin 1e-3", int(np.sum(abs(r3 - 1) <= .01)))
