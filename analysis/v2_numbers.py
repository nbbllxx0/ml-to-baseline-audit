"""Numbers for the restructured SMO manuscript (manuscript/smo_v2/), registered as N091 onward.

    python -m analysis.v2_numbers          # conda env torch5090

Everything is computed from frozen evidence files, run records and the final coding records; nothing is typed in by
hand except (a) the one post hoc reading of the coded `baseline.solver` field (SOLVER_*, below) and (b) the values of
two worked examples, each asserted against the coded evidence text it paraphrases. N001-N090 are not touched, so the
frozen SMO v1 manuscript still renders identically.

Writes evidence/v2_extras.json and registers N091-N152.
"""
import csv
import glob
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.numbers import register  # noqa: E402

EV = ROOT / "evidence"
REC = ROOT / "audit" / "coding" / "records"
PREFILL = ROOT / "audit" / "coding" / "llm_prefill"
RUNS = ROOT / "retest" / "runs"
OUT = EV / "v2_extras.json"
SCRIPT = "analysis/v2_numbers.py"
SRC = "evidence/v2_extras.json"

# Post hoc reading of the coded `baseline.solver` field of the 28 speed-stratum records (one reader, 2026-09-25).
# The coding instructions say to write "not stated" when a field is absent; 24 records say so at the start of the
# field. Three name no solver type (the field says so in other words); one names its linear solver.
SOLVER_STATED = {"P00610": "iterative line-sweep (TDMA) solver of a finite-volume heat-transfer evaluator"}
SOLVER_TYPE_UNSTATED = {"P00550": "in-house C++/CUDA code; direct vs. iterative not stated",
                        "P00698": "a sparse matrix equation solver, type not stated",
                        "P00808": "PARDISO named for the learned method's FE; the SIMP baseline's solver not stated"}

# Worked examples: value -> substring that must occur in the coded evidence it paraphrases.
EXAMPLE_R1 = ("P00176", "R1", {"ce": "mean compliance error 4.16%", "disc": "4.12% of outputs are disconnected"})
EXAMPLE_R1_NOQ = ("P00755", "R1", {"ml": "40 s ANN-driven optimization", "fe": "about 24 h"})
EXAMPLE_R3 = ("P00176", "R3", {"samples": "80,000 SIMP samples"})


def load(name):
    return json.loads((EV / name).read_text(encoding="utf-8"))


def records():
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(REC.glob("P*.json"))]


def x(v, nd=1):
    return f"{v:.{nd}f}×"


def sci(v):
    """3.456e-09 -> '3.5 × 10⁻⁹' (Unicode superscripts, as in the manuscript)."""
    m, e = f"{v:.1e}".split("e")
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return f"{m} × 10{str(int(e)).translate(sup)}"


def main():
    e = {}
    tt, br, hg, rep, cl = load("ttq_summary.json"), load("breakeven.json"), load("hgto_retest.json"), \
        load("reporting.json"), load("claims.json")
    oat, g2eq = load("oat_retest_summary.json"), load("baseline_equivalence.json")
    reg = load("numbers.json")

    # --- same-machine decomposition -------------------------------------------------------------------------
    st = oat["stages"]
    own256 = st["OAT SIMP 256 CG+OC"]["time_s_median"] / st["OAT inference 256"]["time_s_median"]
    own64 = st["OAT SIMP 64 CG+OC"]["time_s_median"] / st["OAT inference 64"]["time_s_median"]
    rep256, rep64 = reg["N016"]["value"], reg["N019"]["value"]
    c480, c960 = hg["configs"]["cantilever_480x160"], hg["configs"]["cantilever_960x320"]
    pub480, pub960 = c480["published"]["oc_over_hgto"], c960["published"]["oc_over_hgto"]
    oc480, oc960 = c480["ratios_vs_hgto_gpu"]["oc2"], c960["ratios_vs_hgto_gpu"]["oc2"]
    port480, port960 = c480["ratios_vs_hgto_gpu"]["ours"], c960["ratios_vs_hgto_gpu"]["ours"]
    mq480 = c480["matched_quality_ours"]["ratio_vs_hgto_gpu"]
    mq960 = c960["matched_quality_ours"]["ratio_vs_hgto_gpu"]
    strong256 = tt["256_gpu"]["ratio_150_incl_setup_over_oat"]
    strong64 = tt["64_pardiso"]["ratio_150_incl_setup_over_oat"]
    cases = {
        "OAT 256": {"reported": rep256, "own_code": own256, "strong": strong256,
                    "matched": tt["256_gpu"]["rules"]["primary_ce_and_volume"]["ratio_median_censored"]},
        "OAT 64": {"reported": rep64, "own_code": own64, "strong": strong64,
                   "matched": tt["64_gpu"]["rules"]["primary_ce_and_volume"]["ratio_median_censored"]},
        "HGTO 480x160": {"reported": pub480, "own_code": oc480, "strong": port480, "matched": mq480},
        "HGTO 960x320": {"reported": pub960, "own_code": oc960, "strong": port960, "matched": mq960},
    }
    for c in cases.values():
        c["machine_factor"] = max(c["own_code"] / c["reported"], c["reported"] / c["own_code"])
        c["baseline_factor"] = c["own_code"] / c["strong"]
    e["decomposition"] = cases
    mf = max(c["machine_factor"] for c in cases.values())
    bf = [c["baseline_factor"] for c in cases.values()]

    # --- OAT: per-problem spread, matching rules, final G2 -----------------------------------------------------
    def per_problem_ratios(key, stage):
        t_oat = {int(k): v["time_s"] for k, v in st[stage]["per_problem"].items()}
        return {p["problem_id"]: p["wall_150_incl_setup_s"] / t_oat[p["problem_id"]] for p in tt[key]["per_problem"]}
    pp256 = per_problem_ratios("256_gpu", "OAT inference 256")
    pp64 = per_problem_ratios("64_pardiso", "OAT inference 64")
    e["oat_per_problem_150"] = {"256_gpu": pp256, "64_pardiso": pp64}
    pre = tt["256_gpu"]["rules"]["preregistered_ce_only"]
    # breakeven.json holds one GPU and one PARDISO row per scenario at 256²; select the GPU row by its label
    tau_rows = [r for r in br["rows"] if r["size"] == 256 and "gpu" in r["C_SIMP_label"]
                and r["scenario"].startswith("same machine, matched quality (pre-registered rule, censored")]
    assert len(tau_rows) == 1, tau_rows
    tau_pre = tau_rows[0]["tau_uses"]
    g2_final = reg["N043"]["value"]
    e["oat_rules"] = {"preregistered_ratio_256": pre["ratio_median_censored"], "preregistered_matched_256": pre["n_matched"],
                      "tau_preregistered_256": tau_pre,
                      "pardiso_64_matched_ratio": tt["64_pardiso"]["rules"]["primary_ce_and_volume"]["ratio_median_censored"],
                      "g2_final_s": g2_final, "g2_final_ratio": 68.30 / g2_final}

    # --- HGTO: all six problems ---------------------------------------------------------------------------------
    six = {}
    for name, c in hg["configs"].items():
        m = c["measured"]
        six[name] = {"hgto_over_port": 1 / c["ratios_vs_hgto_gpu"]["ours"],
                     "hgto_over_port_matched": 1 / c["matched_quality_ours"]["ratio_vs_hgto_gpu"],
                     "port_termination": m["ours"]["termination"][0], "port_updates": m["ours"]["updates"][0],
                     "hgto_termination": m["hgto_gpu"]["termination"][0], "hgto_updates": m["hgto_gpu"]["updates"][0]}
    e["hgto_six"] = six
    faster = {k: v for k, v in six.items() if v["hgto_over_port"] > 1}
    slower = {k: v for k, v in six.items() if v["hgto_over_port"] <= 1}
    assert list(slower) == ["inclined_cantilever"], slower
    incl = six["inclined_cantilever"]
    assert incl["port_termination"] == "max_stage_steps" and incl["hgto_termination"] == "converged"

    # --- audit texture from the final coding records ------------------------------------------------------------
    recs = records()
    inc = [r for r in recs if r["included"]["decision"] == "include" and r["included"].get("stratum") in ("speed", "quality")]
    speed = [r for r in inc if r["included"]["stratum"] == "speed"]
    assert len(speed) == 28 and len(inc) == 57

    def markers(rule, verdict):
        return [r["rules"][rule].get("marker", "") for r in speed if r["rules"][rule]["verdict"] == verdict]
    r1_fail = markers("R1", "fail")
    r2_pass = markers("R2", "pass")
    e["markers"] = {rule: {v: markers(rule, v) for v in ("fail", "partial", "pass", "na")} for rule in ("R1", "R2", "R3", "R4")}
    r2_default = sum(1 for m in r2_pass if m.startswith("R2-none-established"))
    r1_unmatched = sum(1 for m in r1_fail if "R1-unmatched" in m)
    r4_nofail = sum(1 for m in markers("R4", "partial") if "R4-no-failure-rate" in m)

    speed_ids = {r["pid"] for r in speed}
    assert set(SOLVER_STATED) | set(SOLVER_TYPE_UNSTATED) <= speed_ids
    for r in speed:
        if r["pid"] in SOLVER_STATED or r["pid"] in SOLVER_TYPE_UNSTATED:
            continue
        assert r["baseline"]["solver"].strip().lower().startswith("not stated"), r["pid"]
    e["solver_stated"] = {"stated": SOLVER_STATED, "type_unstated": SOLVER_TYPE_UNSTATED,
                          "not_stated": sorted(speed_ids - set(SOLVER_STATED) - set(SOLVER_TYPE_UNSTATED))}

    def count(field, recs_):
        out = {}
        for r in recs_:
            k = r["included"].get(field)
            out[k] = out.get(k, 0) + 1
        return out
    years = [int(r["citation"]["year"]) for r in inc]
    e["sample"] = {f: {"speed": count(f, speed), "quality": count(f, [r for r in inc if r not in speed])}
                   for f in ("method_family", "physics", "dim")}
    e["sample"]["year_range"] = [min(years), max(years)]
    e["sample"]["year_median"] = statistics.median(years)

    acc = {}
    for r in recs:
        acc[r["access"]] = acc.get(r["access"], 0) + 1
    with (ROOT / "audit" / "coding" / "access_final_order.csv").open(encoding="utf-8", newline="") as fh:
        order = list(csv.DictReader(fh))
    paywalled = sum(1 for o in order if int(o["order"]) <= 200 and "paywalled per OpenAlex" in o["accessible"])
    e["access"] = {"paywalled_skipped": paywalled, **acc}
    assert paywalled + len(recs) == 200

    models = {}
    for r in recs:
        p = PREFILL / f"{r['pid']}.json"
        m = json.loads(p.read_text(encoding="utf-8"))["coder"]["llm_model"]
        models[m] = models.get(m, 0) + 1
    e["first_pass_models"] = models

    tp = rep["indicators"]["timing_protocol_stated"]["counts"]
    e["timing_protocol"] = tp

    # --- solver fallbacks in the logged timed GPU runs ------------------------------------------------------------
    fb_runs, fb = 0, 0
    for f in glob.glob(str(RUNS / "*_gpu_P?_n*_pinned" / "record_rep*.json")):
        fb += sum(bool(v) for v in json.loads(pathlib.Path(f).read_text(encoding="utf-8"))["fallback"])
        fb_runs += 1
    for f in (RUNS / "20260924T170236Z_ours_gpu_nito_n256" / "results.json", RUNS / "20260924T170436Z_ours_gpu_nito_n64" / "results.json"):
        for p in json.loads(f.read_text(encoding="utf-8"))["results"]:
            fb += int(p["fallbacks"])
            fb_runs += 1
    for f in glob.glob(str(RUNS / "hgto" / "ours" / "*" / "r*" / "result.json")):
        fb += int(json.loads(pathlib.Path(f).read_text(encoding="utf-8"))["pcg_fallbacks"])
        fb_runs += 1
    e["fallbacks"] = {"runs": fb_runs, "fallbacks": fb,
                      "scope": "pinned benchmark runs (record_rep*.json), the pinned 150-iteration runs on OAT's problems "
                               "(results.json) and every HGTO port run (result.json); the time-to-quality runs do not log it"}

    eq_c = max(r["rel_dc_last"] for r in g2eq if r["solver"] != "superlu")
    eq_x = max(r["max_abs_dxphys"] for r in g2eq if r["solver"] != "superlu")
    e["equivalence"] = {"max_rel_compliance": eq_c, "max_abs_density": eq_x}

    ex = {}
    for pid, rule, vals in (EXAMPLE_R1, EXAMPLE_R1_NOQ, EXAMPLE_R3):
        ev = json.loads((REC / f"{pid}.json").read_text(encoding="utf-8"))["rules"][rule]["evidence"]
        for k, s in vals.items():
            assert s in ev, (pid, rule, s)
        ex[f"{pid}_{rule}"] = vals
    claim176 = json.loads((REC / "P00176.json").read_text(encoding="utf-8"))["claim"]["claimed_speedup"]
    e["examples"] = ex
    e["claims"] = {"median": cl["median"], "q25": cl["q25"], "q75": cl["q75"]}

    OUT.write_text(json.dumps(e, indent=1, default=str), encoding="utf-8")

    # --- registration -----------------------------------------------------------------------------------------------
    def r(nid, value, text, note, unit="", source=SRC):
        register(nid, value, unit=unit, text=text, source=source, script=SCRIPT, note=note)

    r("N091", own256, x(own256), "OAT 256²: speed-up over OAT's own SIMP code on our machine (pyEDGE CG+OC, loop only, "
      "median 37.04 s) / OAT inference median; decomposition stage 2", "×")
    r("N092", own64, x(own64), "OAT 64²: same as N091 (pyEDGE CG+OC 14.64 s)", "×")
    r("N093", mf, f"{mf:.2f}", "largest factor between a reported speed-up and the same method's speed-up over its "
      "authors' classical code on our machine (4 cases: OAT 256², 64²; HGTO 480×160, 960×320)")
    r("N094", [min(bf), max(bf)], f"{min(bf):.1f}- to {max(bf):.0f}-fold",
      "range over the 4 cases of (speed-up over the authors' classical code on our machine) / (speed-up over our "
      "strong baseline); OAT 256² " + f"{bf[0]:.2f}, OAT 64² {bf[1]:.2f}, HGTO 480×160 {bf[2]:.2f}, HGTO 960×320 {bf[3]:.2f}")
    r("N095", pub480, x(pub480), "HGTO article: two-thread SIMP-OC time / HGTO time, 480×160 (article's hardware)", "×")
    r("N096", pub960, x(pub960), "HGTO article: same, 960×320", "×")
    r("N097", port480, f"{port480:.2f}×", "same machine: port time / HGTO time, 480×160 (HGTO's speed-up over the port)", "×")
    r("N098", port960, f"{port960:.2f}×", "same machine: port time / HGTO time, 960×320", "×")
    r("N099", mq480, f"{mq480:.2f}×", "same machine, matched quality: port time to HGTO's compliance / HGTO time, 480×160", "×")
    r("N100", mq960, f"{mq960:.2f}×", "same machine, matched quality: same, 960×320", "×")
    r("N101", pre["ratio_median_censored"], x(pre["ratio_median_censored"], 2),
      "OAT 256², pre-registered matching rule (CE only): censored median ratio ours/OAT", "×", "evidence/ttq_summary.json")
    r("N102", pre["n_matched"], f"{pre['n_matched']} of 5", "OAT 256²: problems matched under the pre-registered rule",
      source="evidence/ttq_summary.json")
    r("N103", tau_pre, f"{tau_pre / 1e6:.1f} million", "break-even τ at 256² under the pre-registered matching rule",
      source="evidence/breakeven.json")
    r("N104", 68.30 / g2_final, x(68.30 / g2_final), "final G2: OAT's reported SIMP-GPU 68.30 s / our GPU baseline on "
      "OAT's problems at 256², 150 iterations, loop only (N043, median of 5); cross-hardware", "×")
    pr = e["oat_rules"]["pardiso_64_matched_ratio"]
    r("N105", pr, x(pr, 2), "OAT 64², PARDISO baseline at matched quality: censored median ratio ours/OAT", "×",
      "evidence/ttq_summary.json")
    r("N106", [min(pp256.values()), max(pp256.values())], f"{min(pp256.values()):.1f}× to {max(pp256.values()):.1f}×",
      "OAT 256²: range over the 5 problems of (our GPU 150 iterations incl. setup) / (OAT inference), per problem")
    r("N107", [min(pp64.values()), max(pp64.values())], f"{min(pp64.values()):.1f}× to {max(pp64.values()):.1f}×",
      "OAT 64²: same with our PARDISO baseline")
    r("N108", len(faster), f"{len(faster)} of 6", "HGTO: problems where the GPU port converged faster than HGTO")
    lo, hi = min(v["hgto_over_port"] for v in faster.values()), max(v["hgto_over_port"] for v in faster.values())
    r("N109", [lo, hi], f"{lo:.1f}× to {hi:.1f}×", "HGTO time / port time over those problems", "×")
    r("N110", 1 / incl["hgto_over_port"], x(1 / incl["hgto_over_port"]),
      "inclined load: port time / HGTO time (port stops at the 1000-update cap; HGTO converges)", "×")
    r("N111", incl["hgto_updates"], f"{incl['hgto_updates']}", "inclined load: HGTO updates to convergence")
    mlo = min(v["hgto_over_port_matched"] for v in six.values())
    mhi = max(v["hgto_over_port_matched"] for v in six.values())
    r("N112", [mlo, mhi], f"{mlo:.1f}× to {mhi:.1f}×", "matched quality, all six problems: HGTO time / port time to "
      "HGTO's final compliance", "×")
    r("N113", r2_default, f"{r2_default} of 28", "speed claims whose R2 pass was a default (marker R2-none-established: "
      "no R2 criterion could be established from the text; unsure scores pass)")
    n_r2p = len(e["markers"]["R2"]["partial"])
    r("N114", n_r2p, f"{n_r2p} of 28", "speed claims with R2 partial")
    r("N115", r1_unmatched, f"{r1_unmatched} of {len(r1_fail)}", "R1 fails of the unmatched kind (ML inference vs a "
      "converged classical run while the ML output is measurably worse)")
    n_r1p = len(e["markers"]["R1"]["partial"])
    r("N116", n_r1p, f"{n_r1p} of 28", "speed claims with R1 partial (quality reported, matching loose)")
    r("N117", r4_nofail, f"{r4_nofail} of 28", "speed claims with R4 partial because no failure rate is reported")
    n_r3p = len(e["markers"]["R3"]["partial"])
    r("N118", n_r3p, f"{n_r3p} of 25", "speed claims with R3 partial (some but not all offline costs)")
    r("N119", len(SOLVER_STATED), f"{len(SOLVER_STATED)} of 28", "speed claims that name the linear solver of the "
      "classical baseline (post hoc reading of the coded baseline.solver field)")
    r("N120", tp.get("yes", 0), f"{tp.get('yes', 0)} of 28", "speed claims that fully state a timing protocol",
      source="evidence/reporting.json")
    r("N121", tp.get("partial", 0), f"{tp.get('partial', 0)}", "speed claims that state a timing protocol in part",
      source="evidence/reporting.json")
    r("N122", [cl["q25"], cl["q75"]], f"{cl['q25']:.1f}× to {cl['q75']:,.0f}×", "interquartile range of the claimed "
      "speed-ups (26 numeric claims)", "×", "evidence/claims.json")
    r("N123", cl["median"], f"{cl['median']:.1f}×", "median claimed speed-up (26 numeric claims)", "×", "evidence/claims.json")
    fam, phy, dim = e["sample"]["method_family"]["speed"], e["sample"]["physics"]["speed"], e["sample"]["dim"]["speed"]
    r("N124", fam.get("cnn", 0), f"{fam.get('cnn', 0)} of 28", "speed claims from convolutional networks")
    r("N125", phy.get("compliance", 0), f"{phy.get('compliance', 0)} of 28", "speed claims on compliance problems")
    r("N126", dim.get("2d", 0), f"{dim.get('2d', 0)} of 28", "speed claims on two-dimensional problems only")
    r("N127", e["sample"]["year_range"], f"{e['sample']['year_range'][0]}–{e['sample']['year_range'][1]}",
      "publication years of the 57 included articles")
    r("N128", paywalled, f"{paywalled}", "records at positions 1-200 skipped as paywalled per OpenAlex",
      source="audit/coding/access_final_order.csv")
    r("N129", acc.get("abstract_only", 0), f"{acc.get('abstract_only', 0)}", "coded records with an abstract only")
    r("N130", acc.get("no_access", 0), f"{acc.get('no_access', 0)}", "coded records blocked by a publisher bot check")
    nft = acc.get("abstract_only", 0) + acc.get("no_access", 0)
    r("N131", nft, f"{nft}", "coded records without a readable full text (enter no rate)")
    opus = sum(v for k, v in models.items() if "Opus" in k)
    r("N132", opus, f"{opus} of 110", "first-pass records that name the model (Claude Opus 5.5)",
      source="audit/coding/llm_prefill")
    r("N133", 110 - opus, f"{110 - opus}", "first-pass records that record only 'Claude subagent'",
      source="audit/coding/llm_prefill")
    r("N134", fb, "none" if fb == 0 else f"{fb}", "solves that fell back to the direct solver in the logged timed GPU runs")
    r("N135", fb_runs, f"{fb_runs}", "logged timed GPU runs checked for fallbacks (" + e["fallbacks"]["scope"] + ")")
    r("N136", eq_c, sci(eq_c), "largest relative final-compliance difference to SuperLU after 150 iterations (GPU and "
      "PARDISO; P1, P2; 64², 256²)", source="evidence/baseline_equivalence.json")
    r("N137", eq_x, sci(eq_x), "largest physical-density difference to SuperLU after 150 iterations",
      source="evidence/baseline_equivalence.json")
    r("N138", claim176, f"{claim176:,.0f}×", "worked example (record P00176): claimed speed-up", "×",
      "audit/coding/records/P00176.json")
    r("N139", 4.16, "4.16 %", "worked example (record P00176): mean compliance error of the network's designs",
      source="audit/coding/records/P00176.json")
    r("N140", 4.12, "4.12 %", "worked example (record P00176): share of outputs disconnected and left out of the averages",
      source="audit/coding/records/P00176.json")
    r("N141", 80000, "80,000", "worked example (record P00176): SIMP samples generated for training, cost not reported",
      source="audit/coding/records/P00176.json")
    r("N142", 40, "40 s", "worked example (record P00755): learned-model optimization time",
      source="audit/coding/records/P00755.json")
    r("N143", 24, "about 24 h", "worked example (record P00755): estimated, never-run classical optimization time",
      source="audit/coding/records/P00755.json")
    out38 = rep["direction"]["outperform"]
    r("N144", out38, f"{out38} of 57 (67 %)", "included articles whose primary outcome claims to outperform",
      source="evidence/reporting.json")
    r("N145", len(r1_fail), f"{len(r1_fail)}", "speed claims failing R1")
    ip = len([r_ for r_ in speed if r_["rules"]["R2"]["verdict"] == "pass"]) - r2_default
    r("N146", ip, f"{ip}", "speed claims whose R2 pass rests on stated evidence")
    q_ = sum(v["hgto_over_port_matched"] > 1 for v in six.values())
    r("N147", q_, f"{q_} of 6", "HGTO: problems where the port reached HGTO's final compliance before HGTO finished")
    # published values (external), with the locator of the in-session check
    br_note = json.loads((EV / "breakeven.json").read_text(encoding="utf-8"))["C_train_note"]
    assert br_note.startswith("168 + 16 H100-days")
    r("N148", 168, "168 H100-days", "OAT App. G: data-generation cost (arXiv 2510.23667; checked in-session 2026-09-24)",
      source="2026-09-24-ml-to-baseline-audit.md#6.2")
    r("N149", 16, "16", "OAT App. G: final training cost in H100-days", source="2026-09-24-ml-to-baseline-audit.md#6.2")
    r("N150", 9, "nine of the ten", "McGreivy & Hakim re-tests: articles where the stronger baseline was at least two "
      "orders of magnitude faster than the article's baseline (arXiv 2407.07218 HTML, fetched 2026-09-24)",
      source="manuscript/2026-09-24-latex-manuscript-audit.md")
    pr_ = load("prisma.json")
    r("N151", pr_["sample_quality_stratum"], f"{pr_['sample_quality_stratum']}", "analysis sample: quality stratum",
      source="evidence/prisma.json")
    k1961 = next(p["primary_ce_and_volume"]["matched_iters"] for p in tt["256_gpu"]["per_problem"] if p["problem_id"] == 1961)
    r("N152", k1961, f"{k1961}", "OAT 256², problem 1961: first budget (iterations) at which our GPU baseline matched OAT "
      "(both rules)", source="evidence/ttq_summary.json")
    print(f"wrote {OUT}; registered N091-N152")


if __name__ == "__main__":
    main()
