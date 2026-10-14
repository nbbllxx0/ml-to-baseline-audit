"""Registry of the values added in response to the strict review (2026-09-26), computed from the saved run data.

    python v6/smo/make_review_numbers.py

Writes numbers_review.json next to this script; make_numbers.py reads it with the other registries.

N501-N503  Break-even over the five-problem workload: tau = C_train / mean paired saving, where the saving is
           classical time to match minus OAT inference time on the same problem. An unmatched problem's classical
           time is at least its 150-iteration time, so the mean saving is a lower bound and tau an upper bound.
N504-N505  Largest coefficient of variation in the CPU-pinned three-repeat runs of the time-to-quality problems (GPU;
           PARDISO), the timing noise that the single-timed time-to-quality sweeps rely on. The script checks that
           these runs cover the same problems and sizes as the sweeps.
N506       Largest amount by which an OAT sample's thresholded volume exceeds the problem's target volume.
The script also checks the claims printed next to these values: a strict volume rule (volume <= target) changes no
match, and OAT's samples exceed the target on two of five problems at each size.
"""
import csv
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
C_TRAIN = (168 + 16) * 86400.0            # OAT App. G: H100-days of data generation and training, in seconds


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


tt, oat = load("evidence/ttq_summary.json"), load("evidence/oat_retest_summary.json")["stages"]


def tau_upper(size, rule):
    s = tt[f"{size}_gpu"]
    inf = {int(k): v["time_s"] for k, v in oat[f"OAT inference {size}"]["per_problem"].items()}
    savings = []
    for p in s["per_problem"]:
        m = p[rule]
        t = m["matched_wall_incl_setup_s"] if m["matched"] else p["wall_150_incl_setup_s"]
        savings.append(t - inf[p["problem_id"]])
    mean = statistics.mean(savings)
    assert mean > 0, (size, rule, mean)
    return C_TRAIN / mean


reg = {}
t256p, t256r = tau_upper(256, "primary_ce_and_volume"), tau_upper(256, "preregistered_ce_only")
t64p, t64r = tau_upper(64, "primary_ce_and_volume"), tau_upper(64, "preregistered_ce_only")
assert abs(t64p - t64r) < 1.0, (t64p, t64r)                  # the text gives one 64^2 value for both rules
for key, v, note in (("N501", t256p, "256^2 GPU, volume-condition rule"), ("N502", t256r, "256^2 GPU, pre-registered rule"),
                     ("N503", t64p, "64^2 GPU, both rules")):
    reg[key] = {"value": v, "text": f"{v / 1e6:.1f} million",
                "note": f"upper bound on break-even uses from the five-problem mean saving; {note}"}

swept = {}                                                      # (solver, size) -> problems of the time-to-quality sweep
for key in ("256_gpu", "64_gpu", "256_pardiso", "64_pardiso"):
    j = load(tt[key]["ttq_run"] + "/ttq_runs.json")
    assert j["cpu_pinning"]["pinned"], key
    swept[(j["solver"], j["size"])] = sorted(j["problem_ids"])
cv = {"gpu": [], "pardiso": []}
for d in sorted((ROOT / "retest" / "runs").glob("*_ours_*_nito_n*")):
    j = json.loads((d / "results.json").read_text(encoding="utf-8"))
    if not (j["config"].get("cpu_pinning") or {}).get("pinned"):
        continue
    size = int(d.name.split("_nito_n")[1].split("_")[0])
    assert sorted(r["problem_id"] for r in j["results"]) == swept[(j["config"]["solver"], size)], d.name  # "the same problems"
    for r in j["results"]:
        t = r["total_s_all"]
        assert len(t) == 3, d.name
        cv[j["config"]["solver"]].append(100 * statistics.pstdev(t) / statistics.mean(t))
assert len(cv["gpu"]) == 20 and len(cv["pardiso"]) == 10, {k: len(v) for k, v in cv.items()}
reg["N504"] = {"value": max(cv["gpu"]), "text": f"{max(cv['gpu']):.1f} %",
               "note": "largest coefficient of variation, CPU-pinned GPU three-repeat runs of the time-to-quality problems "
                       f"(median {statistics.median(cv['gpu']):.2f} %)"}
reg["N505"] = {"value": max(cv["pardiso"]), "text": f"{max(cv['pardiso']):.1f} %",
               "note": "largest coefficient of variation, CPU-pinned PARDISO three-repeat runs of the time-to-quality problems "
                       f"(median {statistics.median(cv['pardiso']):.2f} %)"}

excess = []
for size in (256, 64):
    rows = list(csv.DictReader((ROOT / "figures" / "data" / f"ttq_curves_n{size}_gpu.csv").open(encoding="utf-8")))
    pids = sorted({int(r["problem_id"]) for r in rows})
    first = {p: next(r for r in rows if int(r["problem_id"]) == p) for p in pids}
    over = [float(first[p]["vf_OAT"]) - float(first[p]["vf_target"]) for p in pids
            if float(first[p]["vf_OAT"]) > float(first[p]["vf_target"])]
    assert len(over) == 2 and len(pids) == 5, (size, over)       # "two of five problems at each size"
    excess += over

    def matches(curves, strict):
        out = {}
        for p in pids:
            rr = sorted((r for r in curves if int(r["problem_id"]) == p), key=lambda r: int(r["iters"]))
            cap = float(rr[0]["vf_target"]) if strict else max(float(rr[0]["vf_target"]), float(rr[0]["vf_OAT"]))
            hit = next((int(r["iters"]) for r in rr if float(r["CE_pct"]) <= float(r["CE_OAT_pct"])
                        and float(r["vf_thresholded"]) <= cap), None)
            out[p] = hit
        return out
    for solver in ("gpu", "pardiso"):                            # "the volume-condition allowance changed no match"
        curves = list(csv.DictReader((ROOT / "figures" / "data" / f"ttq_curves_n{size}_{solver}.csv").open(encoding="utf-8")))
        assert matches(curves, True) == matches(curves, False), (size, solver)
reg["N506"] = {"value": max(excess), "text": f"{max(excess):.3f}",
               "note": "largest excess of an OAT sample's thresholded volume over the target volume (256^2 and 64^2)"}

(HERE / "numbers_review.json").write_text(json.dumps(reg, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
for k, v in reg.items():
    print(k, v["text"], "|", v["note"])
