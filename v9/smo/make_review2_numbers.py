"""Registry of the values added in response to the second strict review (2026-09-29), computed from the saved run data.

    python v6/smo/make_review2_numbers.py

Writes numbers_review2.json next to this script; make_numbers.py reads it with the other registries.

N530       Largest implementation cut over all eight measured in-depth cases: the authors' classical time divided by
           the efficient classical time on the same machine (OAT: decomposition baseline factor; HGTO: two-thread
           SIMP-OC median over our GPU port median). N402 (4.2- to 20-fold) is the range of the four Fig. 3a cases.
N531       The same cut for HGTO at 240x80.
N532       The range of the same cut on the three 120x40 HGTO configurations (cantilever, half MBB, inclined load).
N533       OAT extension samples (25 problems x 5 seeds, both sizes) whose thresholded volume exceeds the target.
N534       Largest such excess, in percentage points of volume fraction.
N535-N536  Extension samples matched when the classical design must meet the original target (256^2; 64^2).
N537-N538  Extension median factor (classical / OAT) under that strict classical cap (256^2; 64^2).
The script also checks the claims printed next to these values: the strict cap leaves the 256^2 sign test below 0.05
with the baseline faster on 7 of 25 problems, and leaves the 64^2 sign test far from significance.
"""
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
from analysis.oat_extended import binom_two_sided, median_censored  # noqa: E402


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8-sig"))


reg = {}

# Implementation cut, all eight in-depth cases
dec = load("v4/evidence/decomposition_v4.json")["decomposition"]
hg = load("evidence/hgto_retest.json")["configs"]
cut = {"OAT 256": dec["OAT 256"]["baseline_factor"], "OAT 64": dec["OAT 64"]["baseline_factor"]}
for k, c in hg.items():
    m = c["measured"]
    cut[k] = m["oc2"]["wall_s_median"] / m["ours"]["wall_s_median"]
for k in ("480x160", "960x320"):                     # the HGTO ratio is the one Fig. 3a plots
    assert abs(cut[f"cantilever_{k}"] - dec[f"HGTO {k}"]["baseline_factor"]) < 1e-9, k
fig3a = [cut["OAT 256"], cut["OAT 64"], cut["cantilever_480x160"], cut["cantilever_960x320"]]
assert f"{min(fig3a):.1f}" == "4.2" and round(max(fig3a)) == 20          # N402 = "4.2- to 20-fold"
assert max(cut.values()) == max(fig3a)
small = [cut["cantilever_120x40"], cut["half_mbb"], cut["inclined_cantilever"]]
reg["N530"] = {"value": max(cut.values()), "text": f"{round(max(cut.values()))}-fold",
               "note": "largest implementation cut over the eight in-depth cases (HGTO 960x320)"}
reg["N531"] = {"value": cut["cantilever_240x80"], "text": f"{cut['cantilever_240x80']:.1f}-fold",
               "note": "implementation cut, HGTO cantilever 240x80"}
reg["N532"] = {"value": [min(small), max(small)], "text": f"{min(small):.1f}- to {max(small):.1f}-fold",
               "note": "implementation cut, the three 120x40 HGTO configurations"}

# OAT extension: volume excess and a strict classical cap
meta = load("evidence/oat_extended.json")
excess, strict = [], {}
for n in ("64", "256"):
    d = ROOT / meta[n]["run"]
    sc = json.loads((d / "scores.json").read_text(encoding="utf-8"))
    inf = {(r["problem_id"], r["seed"]): r["time_s"]
           for r in json.loads((d / "infer.json").read_text(encoding="utf-8"))["results"]}
    wall = {(r["problem_id"], r["iters"]): r["wall_incl_setup_s"]
            for r in json.loads((d / "ttq_runs.json").read_text(encoding="utf-8"))["runs"]}
    excess += [o["vf_thresholded"] - e["vf_target"] for e in sc for o in e["oat"].values()]
    out = {}
    for capmode in ("paper", "strict"):
        meds, matched, samples = [], 0, 0
        for e in sc:
            ratios = []
            for s, o in e["oat"].items():
                samples += 1
                cap = e["vf_target"] if capmode == "strict" else max(e["vf_target"], o["vf_thresholded"])
                K = next((int(k) for k, v in sorted(e["ours"].items(), key=lambda kv: int(kv[0]))
                          if v["CE_pct"] <= o["CE_pct"] and v["vf_thresholded"] <= cap), None)
                if K is None:
                    ratios.append(math.inf)
                else:
                    matched += 1
                    ratios.append(wall[(e["problem_id"], K)] / inf[(e["problem_id"], int(s))])
            meds.append(median_censored(ratios))
        faster = sum(m < 1 for m in meds)
        out[capmode] = {"matched": matched, "samples": samples, "median": median_censored(meds), "faster": faster,
                        "p": binom_two_sided(faster, len(meds))}
    # the paper's rule must reproduce the registered extension values
    assert out["paper"]["median"] == meta[n]["rules"]["primary_ce_and_volume"]["median_ratio_over_problems"], n
    strict[n] = out["strict"]
assert strict["256"]["median"] > 1 and strict["256"]["faster"] == 7 and strict["256"]["p"] < 0.05
assert strict["64"]["p"] > 0.5
reg["N533"] = {"value": sum(x > 0 for x in excess), "text": f"{sum(x > 0 for x in excess)} of {len(excess)}",
               "note": "OAT extension samples above the original target volume (both sizes)"}
reg["N534"] = {"value": max(excess) * 100, "text": f"{max(excess) * 100:.1f} percentage points",
               "note": "largest excess of an OAT extension sample's thresholded volume over the target"}
for key, n in (("N535", "256"), ("N536", "64")):
    reg[key] = {"value": strict[n]["matched"], "text": f"{strict[n]['matched']} of {strict[n]['samples']}",
                "note": f"{n}^2 extension samples matched with classical volume <= original target"}
for key, n in (("N537", "256"), ("N538", "64")):
    reg[key] = {"value": strict[n]["median"], "text": f"{strict[n]['median']:.2f}×",
                "note": f"{n}^2 extension median factor (classical / OAT), classical volume <= original target"}

(HERE / "numbers_review2.json").write_text(json.dumps(reg, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
for k, v in reg.items():
    print(k, v["text"], "|", v["note"])
