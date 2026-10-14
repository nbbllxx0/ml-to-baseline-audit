"""Diagnose the P00150 problem mapping: FE of the STORED top88 designs under candidate mappings (untimed)."""
import sys
import numpy as np

sys.path.insert(0, r"E:\AI\ml-to-baseline-audit")
from retest.p00150_harness.problems import load_cases, load_top88, COMPLIANCE_SCALE  # noqa: E402
from retest.p00150_harness.evaluate import Evaluator, SYMMETRIES  # noqa: E402
from retest.baseline.fem2d import Problem, node_id  # noqa: E402

cases = load_cases()[:12]


def prob(case, sx, sy, transpose):
    ix, iy = case["load_node"]
    fx, fy = sx * case["fx"], sy * case["fy"]
    if transpose:                       # node index read row-major: swap the node coordinates, keep the components
        ix, iy = iy, ix
    n = 64
    left = node_id(np.zeros(n + 1, dtype=np.int64), np.arange(n + 1), n)
    fixed = np.sort(np.concatenate([2 * left, 2 * left + 1]))
    f = np.zeros(2 * (n + 1) ** 2)
    k = node_id(8 * ix, 8 * iy, n)
    f[2 * k], f[2 * k + 1] = fx, fy
    return Problem("d", n, n, case["volfrac"], 3.0, fixed, f, penal=3.0, nu=0.3)


results = []
for tname, T in SYMMETRIES.items():
    for sx in (1, -1):
        for sy in (1, -1):
            for tr in (False, True):
                r = []
                for c in cases:
                    t = load_top88(c["k"])
                    ev = Evaluator(prob(c, sx, sy, tr))
                    cc, vol, _ = ev.compliance(T(t["design"]).ravel())
                    r.append(t["compliance"] / (cc * COMPLIANCE_SCALE))
                r = np.array(r)
                results.append((float(np.std(np.log(r))), tname, sx, sy, tr, float(np.median(r)), r))
results.sort(key=lambda x: x[0])
for s, tname, sx, sy, tr, med, r in results[:8]:
    print(f"{tname:22s} sx={sx:+d} sy={sy:+d} transpose={tr!s:5s} sd(log ratio)={s:.4f} median ratio={med:.4f}",
          np.round(r, 3))
