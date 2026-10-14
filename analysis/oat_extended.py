"""Summary of the post hoc OAT extension (retest/oat_harness/extended.py): 25 problems per size, 5 OAT seeds each.

    python -m analysis.oat_extended            # after retest/oat_harness/run_extended.sh

For every problem and OAT seed, our baseline's first budget that matches that OAT sample is found under both rules of
analysis/ttq_summary.py (primary: CE and volume; pre-registered: CE only). The ratio is our setup-inclusive wall time
at that budget divided by the OAT sample's inference time. An unmatched sample is right-censored (ratio = inf, i.e.
our baseline counted as slower). Per problem, the median over the 5 seeds is taken; across problems we report the
median, the share of problems where our baseline is faster (ratio < 1), and a two-sided exact sign test of
H0: P(ratio < 1) = 0.5. Censoring only ever counts against our baseline, so the test is conservative for it.
Writes evidence/oat_extended.json and registers N163 onward.
"""
import glob
import json
import math
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.numbers import register  # noqa: E402

OUT = ROOT / "evidence" / "oat_extended.json"
SCRIPT, SRC = "analysis/oat_extended.py", "evidence/oat_extended.json"
RULES = {"primary_ce_and_volume": lambda o, ce, cap: o["CE_pct"] <= ce and o["vf_thresholded"] <= cap,
         "preregistered_ce_only": lambda o, ce, cap: o["CE_pct"] <= ce}


def binom_two_sided(k, n):
    """Exact two-sided sign-test p-value for k successes of n at p = 0.5."""
    pk = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-15))


def median_censored(vals):
    s = sorted(vals)                      # inf sorts last
    m = statistics.median(s) if all(math.isfinite(v) for v in s) else s[(len(s) - 1) // 2] if len(s) % 2 else \
        (s[len(s) // 2 - 1] + s[len(s) // 2]) / 2
    return m


def summarize(run):
    d = pathlib.Path(run)
    meta = json.loads((d / "ids.json").read_text(encoding="utf-8"))
    inf = json.loads((d / "infer.json").read_text(encoding="utf-8"))["results"]
    ttq = json.loads((d / "ttq_runs.json").read_text(encoding="utf-8"))["runs"]
    sc = {e["problem_id"]: e for e in json.loads((d / "scores.json").read_text(encoding="utf-8"))}
    t_inf = {(r["problem_id"], r["seed"]): r["time_s"] for r in inf}
    wall = {(r["problem_id"], r["iters"]): r["wall_incl_setup_s"] for r in ttq}
    res = {"size": meta["size"], "n_problems": len(sc), "n_seeds": len(meta["oat_seeds"]), "rules": {}}
    ce_spread = []
    for pid, e in sc.items():
        ces = [v["CE_pct"] for v in e["oat"].values()]
        ce_spread.append(max(ces) - min(ces))
    res["oat_ce_range_median_pp"] = statistics.median(ce_spread)
    res["oat_ce_median_pct"] = statistics.median(v["CE_pct"] for e in sc.values() for v in e["oat"].values())
    ti = list(t_inf.values())
    res["oat_time_s"] = {"median": statistics.median(ti), "min": min(ti), "max": max(ti)}
    for rule, ok in RULES.items():
        per_problem, n_samples, n_matched = [], 0, 0
        for pid, e in sc.items():
            ratios = []
            for s, o in e["oat"].items():
                cap = max(e["vf_target"], o["vf_thresholded"])
                n_samples += 1
                K = next((int(k) for k, v in sorted(e["ours"].items(), key=lambda kv: int(kv[0]))
                          if ok(v, o["CE_pct"], cap)), None)
                if K is None:
                    ratios.append(math.inf)
                else:
                    n_matched += 1
                    ratios.append(wall[(pid, K)] / t_inf[(pid, int(s))])
            per_problem.append({"problem_id": pid, "primary": e["primary"], "median_ratio": median_censored(ratios),
                                "ratios": ratios})
        meds = [p["median_ratio"] for p in per_problem]
        faster = sum(1 for m in meds if m < 1)
        res["rules"][rule] = {"samples": n_samples, "samples_matched": n_matched,
                              "median_ratio_over_problems": median_censored(meds),
                              "problems_baseline_faster": faster, "problems": len(meds),
                              "sign_test_p": binom_two_sided(faster, len(meds)),
                              "primary_five_median": median_censored([p["median_ratio"] for p in per_problem if p["primary"]]),
                              "new_twenty_median": median_censored([p["median_ratio"] for p in per_problem if not p["primary"]]),
                              "per_problem": per_problem}
    return res


def fmt_ratio(v):
    return "unmatched" if not math.isfinite(v) else f"{v:.2f}×"


def main():
    out = {}
    for n in (64, 256):
        runs = sorted(glob.glob(str(ROOT / "retest" / "runs" / f"*_oat_extended_n{n}")))
        if not runs:
            raise SystemExit(f"no extended run for n={n}")
        out[str(n)] = {"run": pathlib.Path(runs[-1]).relative_to(ROOT).as_posix(), **summarize(runs[-1])}
    OUT.write_text(json.dumps(out, indent=1, default=lambda x: None if x == math.inf else x), encoding="utf-8")
    nid = 163
    for n in ("64", "256"):
        s = out[n]
        for rule, lab in (("primary_ce_and_volume", "post hoc rule"), ("preregistered_ce_only", "pre-registered rule")):
            r = s["rules"][rule]
            items = [(fmt_ratio(r["median_ratio_over_problems"]), f"{n}²: median over {r['problems']} problems of the per-problem median ratio (ours ÷ OAT) at matched quality, {lab}"),
                     (f"{r['problems_baseline_faster']} of {r['problems']}", f"{n}²: problems where our baseline matched OAT faster (median over seeds), {lab}"),
                     (f"p = {r['sign_test_p']:.2g}" if r["sign_test_p"] >= 1e-3 else f"p = {r['sign_test_p']:.1e}", f"{n}²: exact two-sided sign test, {lab}"),
                     (f"{r['samples_matched']} of {r['samples']}", f"{n}²: OAT samples matched within 150 iterations, {lab}")]
            for text, note in items:
                register(f"N{nid}", text, text=text, source=SRC, script=SCRIPT, note=note)
                print(f"N{nid}", text, "|", note)
                nid += 1
        register(f"N{nid}", s["oat_ce_range_median_pp"], text=f"{s['oat_ce_range_median_pp']:.1f} percentage points",
                 source=SRC, script=SCRIPT, note=f"{n}²: median over problems of the range of OAT's CE across 5 seeds")
        print(f"N{nid}", f"{s['oat_ce_range_median_pp']:.1f} pp")
        nid += 1
    # Break-even at 256² from the extension, as analysis/breakeven.py forms it for the primary five: the learned
    # method's time is OAT's median inference time; the classical time is the median ratio times that time.
    be = json.loads((ROOT / "evidence" / "breakeven.json").read_text(encoding="utf-8"))
    s = out["256"]
    for rule, lab in (("primary_ce_and_volume", "post hoc rule"), ("preregistered_ce_only", "pre-registered rule")):
        ratio, t_oat = s["rules"][rule]["median_ratio_over_problems"], s["oat_time_s"]["median"]
        tau = be["C_train_H100_s"] / (ratio * t_oat - t_oat)
        s["rules"][rule]["tau_uses"] = tau
        register(f"N{nid}", tau, text=f"{tau / 1e6:.0f} million", source=SRC, script=SCRIPT,
                 note=f"256²: break-even uses from the extension, {lab} (C_train / (ratio*t_OAT - t_OAT))")
        print(f"N{nid}", f"{tau / 1e6:.0f} million", lab)
        nid += 1
    OUT.write_text(json.dumps(out, indent=1, default=lambda x: None if x == math.inf else x), encoding="utf-8")


if __name__ == "__main__":
    main()
