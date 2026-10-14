"""P00610 census summary from timing/{classical,direct,cnn}.json.

    v3/.venv/census-torch/Scripts/python.exe v3/runs/P00610/summarize.py

Per ratio k_s: median over the 12 protocol images of each method's median time; speed factors of the CNN against
the article's solver (L1, TDMA, the method the article describes; Gauss-Seidel as released also reported) and
against the direct solve (L2). Quality on the 100 sampled images: median and 95th-percentile absolute relative error
against the published k_eff, for the CNN, the direct solve and the TDMA solver at the released tolerance (from
validate/results.csv). Published factors: record P00610 (claimed_speedup_basis). Writes summary.json.
"""
from __future__ import annotations

import csv
import json
import pathlib
import statistics

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
RATIOS = [10.0, 50.0, 100.0, 341.7]
# Article Table 1 (record P00610): NHT time per image per core, s; published 15 ms GPU CNN.
PUBLISHED_NHT_S = {10.0: 34.2, 50.0: 81.6, 100.0: 137.3, 341.7: 371.2}
PUBLISHED_CNN_GPU_S = 0.015
PUBLISHED_CNN_CPU_S = 0.020


def load(name):
    return json.loads((HERE / "timing" / f"{name}.json").read_text(encoding="utf-8"))


def med_by_ks(rows, key="median_s", **flt):
    out = {}
    for ks in RATIOS:
        sel = [r[key] for r in rows if r["ks"] == ks and all(r.get(k) == v for k, v in flt.items())]
        out[ks] = statistics.median(sel) if sel else None
    return out


def err(rows):
    e = np.array([abs(r["keff"] - r["keff_published"]) / r["keff_published"] for r in rows])
    return {"n": int(e.size), "median": float(np.median(e)), "p95": float(np.percentile(e, 95)), "max": float(e.max())}


def main():
    cl, di, cn = load("classical"), load("direct"), load("cnn")
    t_tdma = med_by_ks(cl["timing"], solver="tdma")
    t_gs = med_by_ks(cl["timing"], solver="gs")
    it_tdma = med_by_ks(cl["timing"], key="iter", solver="tdma")
    t_dir = med_by_ks(di["timing"])
    t_cnn = med_by_ks(cn["timing"])
    val = list(csv.DictReader(open(HERE / "validate" / "results.csv", encoding="utf-8")))
    per_ks = {}
    for ks in RATIOS:
        tdma_q = [{"keff": float(r["keff"]), "keff_published": float(r["keff_published"])} for r in val
                  if r["solver"] == "tdma" and float(r["ks"]) == ks]
        per_ks[str(ks)] = {
            "published_factor_cpu_nht_vs_gpu_cnn": PUBLISHED_NHT_S[ks] / PUBLISHED_CNN_GPU_S,
            "published_factor_cpu_nht_vs_cpu_cnn": PUBLISHED_NHT_S[ks] / PUBLISHED_CNN_CPU_S,
            "ours_s": {"tdma_article_method": t_tdma[ks], "gs_released": t_gs[ks], "direct_superlu": t_dir[ks],
                       "cnn_cpu_1thread": t_cnn[ks]},
            "tdma_median_iterations": it_tdma[ks],
            "L1_factor_tdma_over_cnn": t_tdma[ks] / t_cnn[ks],
            "L1_factor_gs_over_cnn": t_gs[ks] / t_cnn[ks],
            "L2_factor_direct_over_cnn": t_dir[ks] / t_cnn[ks],
            "quality_abs_rel_error_vs_published": {
                "cnn": err([q for q in cn["quality"] if q["ks"] == ks]),
                "direct": err([q for q in di["quality"] if q["ks"] == ks]),
                "tdma_released_tolerance": err(tdma_q)}}
    out = {"per_ratio": per_ks, "meta": {"classical": cl["meta"], "direct": di["meta"], "cnn": cn["meta"]}}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    for ks, v in per_ks.items():
        q = v["quality_abs_rel_error_vs_published"]
        print(f"k_s {ks}: published {v['published_factor_cpu_nht_vs_gpu_cnn']:.0f}x; L1 {v['L1_factor_tdma_over_cnn']:.0f}x "
              f"(GS {v['L1_factor_gs_over_cnn']:.0f}x); L2 {v['L2_factor_direct_over_cnn']:.2f}x; "
              f"error median CNN {q['cnn']['median']:.4f}, direct {q['direct']['median']:.1e}, "
              f"TDMA {q['tdma_released_tolerance']['median']:.4f}")


if __name__ == "__main__":
    main()
