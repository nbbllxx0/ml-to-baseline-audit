"""P00183 census summary from timing/gen.json and timing/classical_{L1,L2}.mat.

    v3/.venv/census-tf/python.exe v3/runs/P00183/summarize.py

Per angle (16, 62, 75): median full TO time over the timed repeats; compliance of the final TO design and of the
generator design (repository evaluator, repaired: compliance_eval.m); matched quality = the elapsed time at the first
stage-end TO design whose compliance is at most the generator's (median over repeats); the generator time per angle.
The generator compliance for all 100 test angles is kept for reference. Writes summary.json.
"""
from __future__ import annotations

import json
import pathlib
import statistics

import numpy as np
import scipy.io as sio

HERE = pathlib.Path(__file__).resolve().parent
T = HERE / "timing"


def load_mat(tag):
    m = sio.loadmat(T / f"classical_{tag}.mat", squeeze_me=True, struct_as_record=False)
    runs = np.atleast_1d(m["runs"])
    return runs, np.atleast_1d(m["gen_c"]), [int(i) for i in np.atleast_1d(m["idx"])]


def per_angle(runs, gen_c, idx):
    out = {}
    for i in idx:
        timed = [r for r in runs if int(r.angle_index) == i and int(r.repeat) >= 1]
        if not timed:
            timed = [r for r in runs if int(r.angle_index) == i]
        g = float(gen_c[i - 1])
        hits = []
        for r in timed:
            sc, st = np.atleast_1d(r.stage_c), np.atleast_1d(r.stage_t)
            k = next((j for j, c in enumerate(sc) if c <= g), None)
            hits.append(float(st[k]) if k is not None else float(r.seconds))
        out[str(i)] = {"repeats": len(timed), "t_full_median_s": statistics.median(float(r.seconds) for r in timed),
                       "fe_analyses": int(timed[0].budget), "c_final_TO": float(timed[0].c_final_eval),
                       "stage_c_TO": [float(c) for c in np.atleast_1d(timed[0].stage_c)],
                       "stage_t_TO_s": [float(t) for t in np.atleast_1d(timed[0].stage_t)],
                       "c_generator": g, "t_matched_median_s": statistics.median(hits)}
    return out


def main():
    gen = json.loads((T / "gen.json").read_text(encoding="utf-8"))
    t_gen = gen["per_angle"]["median_s"]
    out = {"generator_s_per_angle": t_gen, "published": {"generator_s": 1e-2, "TO_s": [1e2, 1e3]}}
    for tag in ("L1", "L2"):
        f = T / f"classical_{tag}.mat"
        if not f.exists():
            continue
        runs, gen_c, idx = load_mat(tag)
        pa = per_angle(runs, gen_c, idx)
        for v in pa.values():
            v["factor_full"] = v["t_full_median_s"] / t_gen
            v["factor_matched"] = v["t_matched_median_s"] / t_gen
        out[tag] = pa
        out["generator_c_all_100"] = [float(c) for c in gen_c]
    (HERE / "summary.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "generator_c_all_100"}, indent=1))


if __name__ == "__main__":
    main()
