"""Register the census numbers for the v3 manuscript and write its census table, recomputed from the run outputs.

    python v3/tools/census_numbers.py

Writes v3/evidence/numbers_v3.json (tokens N300-N339, same fields as tools/numbers.py) and
v3/manuscript/tables/table4_census.md. Every value is read from the per-claim outputs in v3/runs/ (or, for P00150, from
evidence/p00150_check.json) at run time; published values are the records' own figures (audit/coding/records).
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import statistics

V3 = pathlib.Path(__file__).resolve().parents[1]
ROOT = V3.parent
R = V3 / "runs"
OUT = V3 / "evidence" / "numbers_v3.json"
TAB = V3 / "manuscript" / "tables" / "table4_census.md"
SCRIPT = "v3/tools/census_numbers.py"


def j(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def f0(x):
    return f"{x:,.0f}"


def main():
    reg = {}
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    def add(nid, value, text, source, note="", unit=""):
        reg[nid] = {"value": value, "unit": unit, "text": text, "source": source, "script": SCRIPT, "note": note,
                    "status": "provisional", "registered_utc": stamp}

    frame = j(V3 / "census" / "frame.json")
    rerun = [r for r in frame if r["status"] == "to re-test in v3"]
    repaired = ["P00610", "P00080", "P00183", "P00140"]           # REPAIRS.md with code or dependency changes
    words = {2: "two", 4: "four", 6: "six", 7: "seven"}
    add("N300", len(frame), words[len(frame)], "v3/census/frame.json", "speed claims in the sample with public code")
    add("N301", len(rerun), words[len(rerun)], "v3/census/frame.json", "claims re-run in the census")
    add("N302", len(repaired), words[len(repaired)], "v3/runs/*/REPAIRS.md", "claims needing code or dependency repairs")

    # P00610
    s = j(R / "P00610" / "summary.json")["per_ratio"]
    pub = [v["published_factor_cpu_nht_vs_gpu_cnn"] for v in s.values()]
    l1 = [v["L1_factor_tdma_over_cnn"] for v in s.values()]
    l2 = [v["L2_factor_direct_over_cnn"] for v in s.values()]
    slow = [v["ours_s"]["tdma_article_method"] for v in s.values()]
    pubs = {"10.0": 34.2, "50.0": 81.6, "100.0": 137.3, "341.7": 371.2}
    ratio_slow = [pubs[k] / v["ours_s"]["tdma_article_method"] for k, v in s.items()]
    add("N303", [min(pub), max(pub)], f"{f0(min(pub))}–{f0(max(pub))}×", "v3/runs/P00610/summary.json")
    add("N304", [min(l1), max(l1)], f"{f0(min(l1))}–{f0(max(l1))}×", "v3/runs/P00610/summary.json")
    add("N305", [min(l2), max(l2)], f"{statistics.median(l2):.1f}×", "v3/runs/P00610/summary.json",
        f"median over the four ratios; range {min(l2):.2f}-{max(l2):.2f}")
    add("N306", [min(ratio_slow), max(ratio_slow)], f"{min(ratio_slow):.0f}–{max(ratio_slow):.0f}", "v3/runs/P00610/summary.json",
        "article Table 1 time / our time for the same released solver")

    # P00080
    v = j(R / "P00080" / "timing" / "voroto.json")
    h = j(R / "P00080" / "timing" / "homog.json")
    c = j(R / "P00080" / "timing" / "cpu_iter.json")
    g = j(R / "P00080" / "timing" / "gpu.json")
    t_vor = v["topopt"]["median_s"]
    p1, p2 = h["projection_concurrent_min"] * 60 / t_vor, c["projection_bruteforce_min"] * 60 / t_vor
    t_match = g["t_to_target"]["median_s"]
    add("N307", [2200, 20775], "2,200× and 20,775×", "audit/coding/records/P00080.json", "528 min / 0.24 min; 4,986 min / 0.24 min")
    add("N308", [p1, p2], f"{f0(p1)}× and {f0(p2)}×", "v3/runs/P00080/timing/homog.json; cpu_iter.json; voroto.json")
    add("N309", t_vor / t_match, f"{t_vor / t_match:.1f}×", "v3/runs/P00080/timing/gpu.json; voroto.json",
        "VoroTO time / classical time to VoroTO's fine-scale compliance")
    add("N310", t_match, f"{t_match:.2f} s", "v3/runs/P00080/timing/gpu.json")
    add("N311", t_vor, f"{t_vor:.1f} s", "v3/runs/P00080/timing/voroto.json")

    # P00183
    s = j(R / "P00183" / "summary.json")
    L1 = s["L1"]
    ff = [a["factor_full"] for a in L1.values()]
    fm = [a["factor_matched"] for a in L1.values()]
    cr = [a["c_generator"] / a["c_final_TO"] for a in L1.values()]
    add("N312", [min(ff), max(ff)], f"{min(ff) / 1e4:.1f}–{max(ff) / 1e4:.1f} × 10⁴", "v3/runs/P00183/summary.json")
    add("N313", [min(fm), max(fm)], f"{min(fm) / 1e4:.1f}–{max(fm) / 1e4:.1f} × 10⁴", "v3/runs/P00183/summary.json")
    add("N314", [min(cr), max(cr)], f"{min(cr):.2f}–{max(cr):.2f}", "v3/runs/P00183/summary.json",
        "generator compliance / TO compliance, repository evaluator")

    # P00663
    s = j(R / "P00663" / "summary.json")
    add("N315", s["article"]["ratio"], f"{s['article']['ratio']:.2f}×", "v3/runs/P00663/summary.json", "283 s / 245 s")
    add("N316", s["ratio"], f"{s['ratio']:.3f}×", "v3/runs/P00663/summary.json", "median classical / median CNN, 3 runs each")

    # P00140
    d = j(R / "P00140" / "timing" / "dehom.json")["runs"]
    t = [r["median_s"] for r in d]
    c14 = j(R / "P00140" / "timing" / "classical_1440.json")
    add("N317", [min(t), max(t)], f"{min(t):.1f}–{max(t):.1f} s", "v3/runs/P00140/timing/dehom.json")
    add("N318", c14["gpu_1440x720"]["t_1000_median_s"], f"{f0(c14['gpu_1440x720']['t_1000_median_s'])} s",
        "v3/runs/P00140/timing/classical_1440.json")

    # P00647
    s = j(R / "P00647" / "summary.json")
    add("N319", s["L1_stopped"]["elapsed_s"] / 3600, f"{s['L1_stopped']['elapsed_s'] / 3600:.1f} h",
        "v3/runs/P00647/summary.json", "one-core run, stopped, not converged")
    add("N320", s["L1_stopped"]["iterations"], str(s["L1_stopped"]["iterations"]), "v3/runs/P00647/summary.json")
    add("N321", s["derived"]["threading_speedup"], f"{s['derived']['threading_speedup']:.1f}×", "v3/runs/P00647/summary.json")

    # P00150 (v2)
    p = j(ROOT / "evidence" / "p00150_check.json")
    add("N322", p["superlu"]["within_1pct"], f"{p['superlu']['within_1pct']} of {p['superlu']['n']}",
        "evidence/p00150_check.json")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dict(sorted(reg.items())), indent=2, ensure_ascii=False), encoding="utf-8")

    T = lambda n: reg[n]["text"]
    rows = [
        ("[@audP00610]", "CNN for effective conductivity", T("N303"), f"{T('N304')}", f"{T('N305')} (direct solve of the same equations; more accurate)", "L2"),
        ("[@audP00080]", "Voronoi multiscale TO with a surrogate", f"{T('N307')} (projected)", f"{T('N308')} (projected)", f"classical {T('N309')} faster (GPU SIMP, {T('N310')} against {T('N311')})", "L2"),
        ("[@audP00183]", "One-shot generator", "about 10⁴", T("N312"), f"{T('N313')}; generator designs {T('N314')}× the TO compliance", "L2"),
        ("[@audP00663]", "CNN steps in phase-field TO", T("N315"), T("N316"), "same as L1 (sparse direct solver already)", "L2 = L1"),
        ("[@audP00140]", "CNN de-homogenization", "5–10× (comparator not public)", f"CNN {T('N317')}, as published", "not possible (supports and quality evaluation not stated)", "L0"),
        ("[@audP00647]", "3D unit-cell ResUNet", "2,400×", f"one-core run over {T('N319')}, not converged (article 2.4 h)", "not possible (no model released)", "L1, partial"),
        ("[@audP00150]", "Unsupervised predictor", "259×", f"reconstruction check failed ({T('N322')} within 1 %)", "not attempted", "stopped"),
    ]
    lines = ["| Article | Learned method | Published factor | Article's comparison on our machine | Efficient classical method, matched quality | Level |",
             "|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    TAB.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for k, v in sorted(reg.items()):
        print(k, v["text"])


if __name__ == "__main__":
    main()
