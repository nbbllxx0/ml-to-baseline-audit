"""Register the numbers added in the v4 revision and write the v4 tables and figure inputs. Every value is recomputed
from files already in the project (read-only); nothing outside v4/ is written.

    python v4/tools/v4_numbers.py

Writes v4/evidence/numbers_v4.json (tokens N400-N449, same fields as tools/numbers.py), three evidence files and
three manuscript tables:
  v4/evidence/decomposition_v4.json   Fig. 2 values with our GPU solver as the one strong baseline (below)
  v4/evidence/coder_paired.json       weak share under each coding on the same 28 speed-stratum records
  v4/evidence/oat_bestof5.json        best-of-5 OAT sensitivity from the post hoc extension's stored runs
  v4/manuscript/tables/table4_census.md, table5_agreement.md, table6_minimum_report.md

What is new relative to v3 (all post hoc, reported as such in the manuscript):
  1. One strong baseline. v3 reported "the faster of our two solvers", chosen after the runs; that choice differed
     from the GPU solver only for the fixed-150-iteration comparison at 64², where PARDISO was faster. v4 names the
     GPU solver as the strong baseline everywhere and reports PARDISO beside it. Only the OAT 64² fixed-iteration
     ratio and its Fig. 2 point change (tokens N400-N402); every matched-quality value was already the GPU solver's.
  2. Coder sensitivity on one denominator: v3 gave each coding's weak share on the records that coding placed in the
     speed stratum (26, 38 and 28 records). v4 fixes the 28 adjudicated speed-stratum records and reports, for each
     coding, how many it coded as speed claims and how many of those fail R1 or R2 (N413-N421).
  3. Best-of-5 OAT: OAT's authors propose drawing several samples per problem and keeping the best. From the stored
     extension runs (5 samples per problem, all baseline budgets scored), the best sample (lowest CE) is matched as
     before; OAT's time is bounded by one sampling call (batching free) and by five sequential calls (N422-N429).
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import math
import pathlib
import statistics
import sys

V4 = pathlib.Path(__file__).resolve().parents[1]
ROOT = V4.parent
EV = ROOT / "evidence"
OUT = V4 / "evidence" / "numbers_v4.json"
TAB = V4 / "manuscript" / "tables"
SCRIPT = "v4/tools/v4_numbers.py"
sys.path.insert(0, str(ROOT))
from analysis.rules import SAMPLE_POSITIONS, clopper_pearson, sample_pids  # noqa: E402

REG: dict = {}
STAMP = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def j(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def add(nid, value, text, source, note="", unit=""):
    if nid in REG:
        raise SystemExit(f"duplicate token {nid}")
    REG[nid] = {"value": value, "unit": unit, "text": text, "source": source, "script": SCRIPT, "note": note,
                "status": "provisional", "registered_utc": STAMP}


def pct(k, n):
    lo, hi = clopper_pearson(k, n)
    return f"{100 * k / n:.0f} % ({k}/{n}; 95 % CI {100 * lo:.0f}–{100 * hi:.0f} %)"


def strict(o):
    """JSON-safe copy: an infinite ratio (unmatched within 150 iterations) becomes null."""
    if isinstance(o, float) and math.isinf(o):
        return None
    if isinstance(o, dict):
        return {k: strict(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [strict(v) for v in o]
    return o


def median_censored(vals):
    """Median with right-censored values (inf sorts last), as analysis/oat_extended.py computes it."""
    s = sorted(vals)
    n = len(s)
    if n % 2:
        return s[n // 2]
    a, b = s[n // 2 - 1], s[n // 2]
    return math.inf if math.isinf(b) else (a + b) / 2


# ---------------------------------------------------------------------------------------------------------------
def one_strong_baseline():
    tt, oat, x2 = j(EV / "ttq_summary.json"), j(EV / "oat_retest_summary.json"), j(EV / "v2_extras.json")
    st = oat["stages"]
    t_oat = {int(k): v["time_s"] for k, v in st["OAT inference 64"]["per_problem"].items()}
    pp = {p["problem_id"]: p["wall_150_incl_setup_s"] / t_oat[p["problem_id"]] for p in tt["64_gpu"]["per_problem"]}
    r64 = tt["64_gpu"]["ratio_150_incl_setup_over_oat"]
    # same definition as N017/N020: median setup-inclusive 150-iteration time / median OAT inference time
    assert abs(r64 - tt["64_gpu"]["wall_150_incl_setup_median_s"] / tt["64_gpu"]["oat_inference_median_s"]) < 1e-12
    add("N400", r64, f"{r64:.1f}×", "evidence/ttq_summary.json",
        "OAT 64², 150 iterations incl. setup: median of our GPU baseline / median OAT inference (GPU is the one strong "
        "baseline in v4; v3's N020 used PARDISO, the faster solver at this size)", "×")
    add("N401", [min(pp.values()), max(pp.values())], f"{min(pp.values()):.1f}× to {max(pp.values()):.1f}×",
        "evidence/ttq_summary.json; evidence/oat_retest_summary.json", "OAT 64²: per-problem range of N400")
    dec = json.loads(json.dumps(x2["decomposition"]))
    d = dec["OAT 64"]
    d["strong"] = r64
    d["baseline_factor"] = d["own_code"] / r64
    bf = [v["own_code"] / v["strong"] for v in dec.values()]
    for v in dec.values():
        assert abs(v["baseline_factor"] - v["own_code"] / v["strong"]) < 1e-9
    add("N402", [min(bf), max(bf)], f"{min(bf):.1f}- to {max(bf):.0f}-fold", "v4/evidence/decomposition_v4.json",
        "range over the 4 re-test cases of (speed-up over the authors' classical code on our machine) / (speed-up over "
        "our GPU strong baseline), same machine; replaces v3's N094, whose OAT 64² case used PARDISO")
    (V4 / "evidence" / "decomposition_v4.json").write_text(json.dumps(
        {"note": "Fig. 2 inputs: v2_extras.json decomposition with OAT 64² 'strong' = our GPU baseline (N400)",
         "decomposition": dec, "preregistered_ratio_256": x2["oat_rules"]["preregistered_ratio_256"]}, indent=1),
        encoding="utf-8")
    # Eq. (5): S_matched = S_published * H * I * Q, shown for OAT at 256²
    o = dec["OAT 256"]
    H, I, Q = o["own_code"] / o["reported"], o["strong"] / o["own_code"], o["matched"] / o["strong"]
    assert abs(o["reported"] * H * I * Q - o["matched"]) < 1e-9
    add("N407", H, f"{H:.2f}", "evidence/v2_extras.json", "OAT 256²: machine factor H = own-code speed-up / reported")
    add("N408", I, f"{I:.2f}", "evidence/v2_extras.json", "OAT 256²: implementation factor I = strong / own code")
    add("N409", Q, f"{Q:.2f}", "evidence/v2_extras.json", "OAT 256²: quality factor Q = matched / strong")
    # PARDISO beside the GPU solver: 64² matched-quality break-even with PARDISO as the classical time
    b = j(EV / "breakeven.json")
    hit = [r for r in b["rows"] if r["size"] == 64 and "pardiso" in r["C_SIMP_label"].lower()
           and r["scenario"].startswith("same machine, matched quality (primary, censored")]
    assert len(hit) == 1
    tau = hit[0]["tau_uses"]
    add("N404", tau, f"{tau / 1e6:.0f} million", "evidence/breakeven.json",
        "τ at 64², matched quality (post hoc rule), PARDISO as the classical time (ratio 1.91×)")
    # the OAT matched-quality range quoted in the abstract: both rules, five and 25 problems, 256²
    ext = j(EV / "oat_extended.json")["256"]["rules"]
    vals = [tt["256_gpu"]["rules"]["primary_ce_and_volume"]["ratio_median_censored"],
            tt["256_gpu"]["rules"]["preregistered_ce_only"]["ratio_median_censored"],
            ext["primary_ce_and_volume"]["median_ratio_over_problems"],
            ext["preregistered_ce_only"]["median_ratio_over_problems"]]
    reg = j(EV / "numbers.json")
    for v, k in zip(vals, ("N018", "N101", "N172", "N176")):   # the four registered texts these values carry
        assert reg[k]["text"].rstrip("×") in (f"{v:.2f}", f"{v:.3g}"), (k, v, reg[k]["text"])
    add("N405", [min(vals), max(vals)], f"{min(vals):.1f}× to {max(vals):.1f}×",
        "evidence/ttq_summary.json; evidence/oat_extended.json",
        "OAT 256² at matched quality: range over both matching rules and both problem sets (N018, N101, N172, N176)")
    return dec


# ---------------------------------------------------------------------------------------------------------------
def hgto_position():
    rows = list(csv.DictReader((ROOT / "audit" / "screening" / "pilot_final_order.csv").open(encoding="utf-8")))
    pos = [int(r["order"]) for r in rows if r["pid"] == "P00512"]
    assert len(pos) == 1 and pos[0] > SAMPLE_POSITIONS
    assert (ROOT / "audit" / "coding" / "llm_prefill" / "P00512.json").exists()
    add("N406", pos[0], str(pos[0]), "audit/screening/pilot_final_order.csv",
        "decision-order position of HGTO (P00512), coded in the pilot wave before the random sample was fixed")


# ---------------------------------------------------------------------------------------------------------------
def coder_paired():
    keep = sample_pids(SAMPLE_POSITIONS)

    def load(folder):
        return {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in (ROOT / folder).glob("P*.json")
                if f.stem in keep}

    def speed(r):
        return (r["included"]["decision"] == "include" and r["included"].get("stratum") == "speed"
                and r.get("access") == "full_text")

    final, first, second = load("audit/coding/records"), load("audit/coding/llm_prefill"), load(
        "audit/coding/second_pass")
    ids = sorted(p for p, r in final.items() if speed(r))
    assert len(ids) == 28
    out = {"records": ids, "codings": {}}
    for name, recs in (("first", first), ("second", second), ("adjudicated", final)):
        avail = [p for p in ids if p in recs and speed(recs[p])]
        weak = [p for p in avail if "fail" in (recs[p]["rules"]["R1"]["verdict"], recs[p]["rules"]["R2"]["verdict"])]
        tally = {rule: {v: sum(1 for p in avail if recs[p]["rules"][rule]["verdict"] == v)
                        for v in ("fail", "partial", "pass")} for rule in ("R1", "R2")}
        out["codings"][name] = {"coded_as_speed": len(avail), "weak": len(weak), "weak_pids": weak, "tally": tally}
    # the authors' review: reviewed verdicts from the checklist (one row per record and rule)
    ck = ROOT / "manuscript" / "smo_v2" / "online_resources" / "review" / "speed_stratum_checklist.csv"
    rev = {}
    for r in csv.DictReader(ck.open(encoding="utf-8-sig")):
        rev.setdefault(r["pid"], {})[r["rule"]] = (r["reviewer_verdict"] or r["verdict"]).strip()
    assert sorted(rev) == ids
    weak_h = [p for p in ids if "fail" in (rev[p]["R1"], rev[p]["R2"])]
    out["codings"]["authors_review"] = {"coded_as_speed": 28, "weak": len(weak_h), "weak_pids": weak_h,
                                        "tally": {rule: {v: sum(1 for p in ids if rev[p][rule] == v)
                                                         for v in ("fail", "partial", "pass")} for rule in ("R1", "R2")}}
    hr = j(EV / "human_review.json")
    assert len(weak_h) == 11 and hr["per_rule"]["R1"]["n"] == 28
    added = sorted(set(weak_h) - set(out["codings"]["adjudicated"]["weak_pids"]))
    removed = sorted(set(out["codings"]["adjudicated"]["weak_pids"]) - set(weak_h))
    out["authors_review_added"], out["authors_review_removed"] = added, removed
    (V4 / "evidence" / "coder_paired.json").write_text(json.dumps(out, indent=1, allow_nan=False), encoding="utf-8")
    c = out["codings"]
    add("N411", c["adjudicated"]["weak"], f"{c['adjudicated']['weak']} ({100 * c['adjudicated']['weak'] / 28:.0f} %)",
        "v4/evidence/coder_paired.json", "short form of N083 for the abstract")
    add("N412", c["authors_review"]["weak"], f"{c['authors_review']['weak']} ({100 * c['authors_review']['weak'] / 28:.0f} %)",
        "v4/evidence/coder_paired.json", "short form of N205 for the abstract")
    add("N410", c["authors_review"]["weak"] / 28, pct(c["authors_review"]["weak"], 28), "v4/evidence/coder_paired.json",
        "weak share under the authors' review, with Clopper-Pearson interval")
    add("N434", c["adjudicated"]["weak"], str(c["adjudicated"]["weak"]), "v4/evidence/coder_paired.json",
        "count of speed claims failing R1 or R2 after adjudication (count only, for the abstract and cover letter)")
    add("N435", c["authors_review"]["weak"], str(c["authors_review"]["weak"]), "v4/evidence/coder_paired.json",
        "count of speed claims failing R1 or R2 under the authors' unblinded review (count only)")
    nid = 413
    for name in ("first", "second"):
        s = c[name]
        add(f"N{nid}", s["coded_as_speed"], f"{s['coded_as_speed']} of 28", "v4/evidence/coder_paired.json",
            f"of the 28 adjudicated speed claims, records the {name} coding also coded as speed claims")
        add(f"N{nid + 1}", s["weak"], f"{s['weak']} of {s['coded_as_speed']}", "v4/evidence/coder_paired.json",
            f"of those, records failing R1 or R2 under the {name} coding")
        nid += 2
    add("N417", len(added), str(len(added)), "v4/evidence/coder_paired.json",
        "records the authors' review adds to the adjudicated weak set: " + ", ".join(added))
    add("N418", len(removed), str(len(removed)), "v4/evidence/coder_paired.json",
        "records the authors' review removes from the adjudicated weak set")
    # table 5 (v4): agreement rows as in v3, then the paired weak shares
    t4 = (ROOT / "v3" / "manuscript" / "tables" / "table4_agreement.md").read_text(encoding="utf-8").splitlines()
    keep_rows = [ln.replace(", human vs adjudicated", ", authors' review vs adjudicated")
                 for ln in t4 if not ln.startswith("| Weak share")]
    rows = []
    for name, lab in (("first", "first coding"), ("second", "second coding"), ("adjudicated", "adjudicated coding"),
                      ("authors_review", "authors' review")):
        s = c[name]
        cp = clopper_pearson(s["weak"], s["coded_as_speed"])
        rows.append(f"| Weak share, {lab} | {s['coded_as_speed']} | {100 * s['weak'] / s['coded_as_speed']:.0f} % "
                    f"({s['weak']}/{s['coded_as_speed']}; {100 * cp[0]:.0f}–{100 * cp[1]:.0f}) | – |")
    (TAB / "table5_agreement.md").write_text("\n".join(keep_rows + rows) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------------------------------------------------------
RULES = {"post hoc rule": lambda o, ce, cap: o["CE_pct"] <= ce and o["vf_thresholded"] <= cap,
         "pre-registered rule": lambda o, ce, cap: o["CE_pct"] <= ce}


def bestof5():
    reg = j(EV / "numbers.json")
    out = {}
    nid = 422
    for n in (256, 64):
        d = ROOT / j(EV / "oat_extended.json")[str(n)]["run"]
        sc = j(d / "scores.json")
        t_inf = {(r["problem_id"], r["seed"]): r["time_s"] for r in j(d / "infer.json")["results"]}
        wall = {(r["problem_id"], r["iters"]): r["wall_incl_setup_s"] for r in j(d / "ttq_runs.json")["runs"]}
        res = {}
        for rule, ok in RULES.items():
            free, seq, best_ce_gain, per = [], [], [], []
            for e in sc:
                pid = e["problem_id"]
                seed, o = min(e["oat"].items(), key=lambda kv: kv[1]["CE_pct"])
                cap = max(e["vf_target"], o["vf_thresholded"])
                K = next((int(k) for k, v in sorted(e["ours"].items(), key=lambda kv: int(kv[0]))
                          if ok(v, o["CE_pct"], cap)), None)
                times = [t_inf[(pid, int(s))] for s in e["oat"]]
                t_one, t_five = statistics.median(times), sum(times)
                w = wall[(pid, K)] if K is not None else math.inf
                free.append(w / t_one)
                seq.append(w / t_five)
                best_ce_gain.append(statistics.median(v["CE_pct"] for v in e["oat"].values()) - o["CE_pct"])
                per.append({"problem_id": pid, "best_seed": seed, "best_CE_pct": o["CE_pct"], "matched_iters": K,
                            "ratio_batching_free": free[-1], "ratio_five_calls": seq[-1]})
            res[rule] = {"median_ratio_batching_free": median_censored(free),
                         "median_ratio_five_calls": median_censored(seq),
                         "matched": sum(1 for p in per if p["matched_iters"] is not None), "problems": len(per),
                         "median_ce_gain_pp": statistics.median(best_ce_gain), "per_problem": per}
        out[str(n)] = res
        for rule in RULES:
            r = res[rule]
            lo, hi = r["median_ratio_five_calls"], r["median_ratio_batching_free"]
            txt = f"{lo:.2f}× to {hi:.2f}×" if math.isfinite(hi) else "unmatched on the median problem"
            add(f"N{nid}", strict([lo, hi]), txt, "v4/evidence/oat_bestof5.json",
                f"{n}², best of 5 OAT samples, {rule}: median over 25 problems of (our time to the best sample's "
                "quality) / (OAT sampling time), from five sequential calls to one call; oracle selection, the "
                "evaluation of the five samples is not timed (inference-only)")
            add(f"N{nid + 1}", r["matched"], f"{r['matched']} of {r['problems']}", "v4/evidence/oat_bestof5.json",
                f"{n}², best of 5, {rule}: problems our baseline matched within 150 iterations")
            nid += 2
        add(f"N{nid}", res["post hoc rule"]["median_ce_gain_pp"],
            f"{res['post hoc rule']['median_ce_gain_pp']:.1f} percentage points", "v4/evidence/oat_bestof5.json",
            f"{n}²: median over problems of (median-sample CE − best-sample CE)")
        nid += 1
    out = {"note": "Oracle-selected, inference-only sensitivity: the best of five OAT samples (lowest CE) is chosen "
                   "with the finite-element evaluation of every sample, whose time is not counted. OAT time is one "
                   "sampling call (batching free) or five sequential calls. null ratio = unmatched within 150 "
                   "iterations (right-censored, counted as slower for our baseline).", **out}
    (V4 / "evidence" / "oat_bestof5.json").write_text(json.dumps(strict(out), indent=1, allow_nan=False),
                                                     encoding="utf-8")
    assert reg["N172"]["value"]  # the extension summary this analysis extends
    return out


# ---------------------------------------------------------------------------------------------------------------
def census_table():
    s = j(ROOT / "v3" / "runs" / "P00183" / "summary.json")
    fe = [a["fe_analyses"] for a in s["L1"].values()]
    add("N432", [min(fe), max(fe)], f"{min(fe):,}–{max(fe):,}", "v3/runs/P00183/summary.json",
        "finite-element analyses in one full run of the article's augmented-Lagrangian TO (three load angles)")
    nelx, nely = 120, 40                                     # the article's mesh (v3/runs/P00183/RESULT.md)
    ndof = 2 * (nelx + 1) * (nely + 1)
    assert "9,922-DOF" in (ROOT / "v3" / "runs" / "P00183" / "RESULT.md").read_text(encoding="utf-8")
    add("N433", ndof, f"{ndof:,}", "v3/runs/P00183/RESULT.md", "degrees of freedom of the 120×40 bilinear mesh")
    v3 = j(ROOT / "v3" / "evidence" / "numbers_v3.json")
    T = lambda n: v3[n]["text"]
    rows = [
        ("[@audP00610]", "CNN for effective conductivity", T("N303"), T("N304"),
         f"{T('N305')} (direct solve of the same equations; more accurate)", "L2"),
        ("[@audP00080]", "Voronoi multiscale TO with a surrogate", f"{T('N307')} (projected)", f"{T('N308')} (projected)",
         f"classical {T('N309')} faster (single-scale GPU SIMP, {T('N310')} against {T('N311')}; compliance only)", "L2"),
        ("[@audP00183]", "One-shot generator", "about 10⁴", T("N312"),
         f"no faster solver found (threading was slower); against the article's own code, {T('N313')}; generator "
         f"designs {T('N314')}× the converged TO compliance", "L1 at matched quality"),
        ("[@audP00663]", "CNN steps in phase-field TO", T("N315"), T("N316"),
         "same as L1 (sparse direct solver already)", "L2 = L1"),
        ("[@audP00140]", "CNN de-homogenization", "5–10× (comparator not public)", f"CNN {T('N317')}, as published",
         "not possible (supports and quality evaluation not stated)", "L0"),
        ("[@audP00647]", "3D unit-cell ResUNet", "2,400×", f"one-core run over {T('N319')}, not converged (article 2.4 h)",
         "not possible (no model released)", "L1, partial"),
        ("[@audP00150]", "Unsupervised predictor", "259×", f"reconstruction check failed ({T('N322')} within 1 %)",
         "not attempted", "stopped"),
    ]
    lines = ["| Article | Learned method | Published factor | Article's comparison on our machine | "
             "Matched-quality comparison | Level |", "|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    (TAB / "table4_census.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def minimum_report_table():
    rows = [
        ("Classical method", "Algorithm, implementation, linear solver and stopping rule", "Sect. 2.4"),
        ("Hardware", "CPU or GPU model, threads and precision, for each method", "Sect. 2.5"),
        ("Timing protocol", "What is timed, whether setup is included, warm-up, repeats and the statistic", "Sect. 2.5"),
        ("Quality at the compared point", "Finite-element objective of the returned designs, thresholded, with "
         "constraint violations and failures", "Sects. 2.6 and 3.4"),
        ("Offline cost", "Data generation, training and their hardware, with the break-even number of uses",
         "Sect. 3.6"),
        ("Artifacts", "Code, trained model, timing harness and a pinned environment", "Code availability"),
    ]
    lines = ["| Item | State | In this paper |", "|---|---|---|"] + ["| " + " | ".join(r) + " |" for r in rows]
    (TAB / "table6_minimum_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    (V4 / "evidence").mkdir(exist_ok=True)
    one_strong_baseline()
    hgto_position()
    coder_paired()
    bestof5()
    census_table()
    minimum_report_table()
    OUT.write_text(json.dumps(strict(dict(sorted(REG.items()))), indent=2, ensure_ascii=False, allow_nan=False),
                   encoding="utf-8")
    for k, v in sorted(REG.items()):
        print(k, v["text"], "|", v["note"][:90])


if __name__ == "__main__":
    main()
