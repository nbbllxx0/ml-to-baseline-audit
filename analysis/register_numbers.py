"""Register the re-test numbers (C2, C3; N016–N026) in evidence/numbers.json from the evidence files.

    python -m analysis.register_numbers

Every value is read from an evidence file at run time, never typed in, except OAT's published values, which carry
their locator in arXiv 2510.23667. Re-running overwrites the same IDs. Status stays "provisional" until the manuscript
freeze. Audit numbers (N001–N015) are registered by the audit analyses once verified records exist.
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.numbers import register  # noqa: E402

OAT = "arXiv 2510.23667"
PUB = "2026-09-24-ml-to-baseline-audit.md#6.2"      # task record section that transcribes OAT's values


def load(rel):
    f = ROOT / rel
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def fmt_x(v):
    return f"{v:.1f}×" if v < 100 else f"{v:.0f}×"


def main():
    st = load("evidence/oat_retest_summary.json")["stages"]
    be = load("evidence/breakeven.json")
    ttq = load("evidence/ttq_summary.json") or {}
    energy = load("evidence/energy.json")
    med = {k: v["time_s_median"] for k, v in st.items()}
    src = "evidence/oat_retest_summary.json"
    scr = "analysis/oat_retest_summary.py"

    register("N016", 68.30 / 0.51, unit="×", text=fmt_x(68.30 / 0.51), source=PUB, script="(published)",
             note=f"{OAT} Table 6: OAT's reported speed-up at 256², SIMP-GPU 68.30 s / OAT 0.51 s (RTX 4090)")
    # Per-design comparisons with OAT use setup-inclusive 150-iteration times (BASELINE_PREREG §9, setup row);
    # loop-only (pre-registered timing) versions are kept as N059-N061.
    tsrc, tscr = "evidence/ttq_summary.json", "analysis/ttq_summary.py"
    t256 = ttq.get("256_gpu")
    if t256 and t256.get("ratio_150_incl_setup_over_oat"):
        v = t256["ratio_150_incl_setup_over_oat"]
        register("N017", v, unit="×", text=fmt_x(v), source=tsrc, script=tscr,
                 note="same machine, pinned, 256²: median of ours GPU 150 its incl. setup / median of OAT inference, 5 NITO problems")
        register("N062", t256["wall_150_incl_setup_median_s"], unit="s", text=f"{t256['wall_150_incl_setup_median_s']:.2f} s",
                 source=tsrc, script=tscr, note="ours GPU, 256², 150 its incl. setup, median of 5 NITO problems")
    fast64 = min((ttq[k] for k in ("64_gpu", "64_pardiso") if ttq.get(k) and ttq[k].get("wall_150_incl_setup_median_s")),
                 key=lambda t: t["wall_150_incl_setup_median_s"], default=None)
    if fast64:
        v = fast64["ratio_150_incl_setup_over_oat"]
        register("N020", v, unit="×", text=fmt_x(v), source=tsrc, script=tscr,
                 note=f"same machine, pinned, 64²: median of ours ({fast64['solver']}, the faster of GPU and PARDISO incl. "
                      f"setup) 150 its / median of OAT inference, 5 NITO problems")
    for key, nid in (("64_pardiso", "N063"), ("64_gpu", "N064"), ("256_pardiso", "N065")):
        t = ttq.get(key)
        if t and t.get("wall_150_incl_setup_median_s") is not None:
            register(nid, t["wall_150_incl_setup_median_s"], unit="s", text=f"{t['wall_150_incl_setup_median_s']:.2f} s",
                     source=tsrc, script=tscr, note=f"ours {t['solver']}, {t['size']}², 150 its incl. setup, median of 5 NITO problems")
    v = med["ours GPU 256"] / med["OAT inference 256"]
    register("N059", v, unit="×", text=fmt_x(v), source=src, script=scr,
             note="loop only (pre-registered timing), pinned, 256²: ours GPU 150 its median / OAT inference median")
    v = med["ours PARDISO 64"] / med["OAT inference 64"]
    register("N060", v, unit="×", text=fmt_x(v), source=src, script=scr,
             note="loop only (pre-registered timing), pinned, 64²: ours PARDISO 150 its median / OAT inference median")
    v = 9.13 / 0.508
    register("N019", v, unit="×", text=fmt_x(v), source=PUB, script="(published)",
             note=f"{OAT} Table 6: OAT's reported speed-up at 64², SIMP-GPU 9.13 s / OAT 0.508 s (RTX 4090)")
    for size, nid in ((256, "N018"), (64, "N039")):
        t = ttq.get(f"{size}_gpu")
        r = t["rules"]["primary_ce_and_volume"] if t else None
        if r and r["ratio_median_censored"] is not None:
            v = r["ratio_median_censored"]
            register(nid, v, unit="×", text=f"{v:.2f}×", source="evidence/ttq_summary.json",
                     script="analysis/ttq_summary.py",
                     note=f"same machine, pinned, {size}²: median over 5 problems of (ours GPU time to OAT's quality, "
                          f"CE and volume condition, setup included) / (OAT inference time); {r['n_matched']}/"
                          f"{t['n_problems']} matched, unmatched ranked slowest. > 1 means OAT is faster")

    register("N021", 2.32e6, unit="uses", text="2.32 million", source=PUB, script="(published)",
             note=f"{OAT} App. G: OAT's stated break-even; with 168 + 16 H100-days it implies a per-design gap of "
                  f"{be['implied_delta_s']:.2f} s")
    rows = be["rows"]

    def row(scenario, size, simp_prefix):
        return next((r for r in rows if r["scenario"] == scenario and r["size"] == size
                     and r["C_SIMP_label"].startswith(simp_prefix)), None)

    r = next(r for r in rows if r["scenario"] == "OAT Table 6 as reported" and r["size"] == 256
             and r["C_SIMP_label"] == "SIMP GPU" and r["C_inf_label"] == "OAT")
    register("N022", r["tau_uses"], unit="uses", text=f"{r['tau_uses'] / 1e6:.2f} million",
             source="evidence/breakeven.json", script="analysis/breakeven.py",
             note="τ from OAT's own Table 6 at 256² (SIMP-GPU 68.30 s vs OAT 0.51 s) with OAT's C_train")
    r = row("same machine, 150 iterations incl. setup", 256, "ours gpu")
    if r:
        t = "never" if math.isinf(r["tau_uses"]) else f"{r['tau_uses'] / 1e6:.2f} million"
        register("N023", r["tau_uses"], unit="uses", text=t, source="evidence/breakeven.json",
                 script="analysis/breakeven.py", note="τ, same machine, pinned, 256², ours GPU 150 its incl. setup vs OAT inference")
    r = row("same machine, 150 iterations, loop only (pre-registered timing)", 256, "ours GPU")
    if r:
        t = "never" if math.isinf(r["tau_uses"]) else f"{r['tau_uses'] / 1e6:.2f} million"
        register("N061", r["tau_uses"], unit="uses", text=t, source="evidence/breakeven.json",
                 script="analysis/breakeven.py", note="τ, same machine, 256², ours GPU 150 its loop only vs OAT inference")
    for size, nid in ((256, "N024"), (64, "N050")):
        r = row("same machine, matched quality (primary, censored median ratio)", size, "ours gpu")
        if r:
            t = "never" if math.isinf(r["tau_uses"]) else f"{r['tau_uses'] / 1e6:.1f} million"
            register(nid, r["tau_uses"] if not math.isinf(r["tau_uses"]) else None, unit="uses", text=t,
                     source="evidence/breakeven.json", script="analysis/breakeven.py",
                     note=f"τ, same machine, pinned, {size}²: C_SIMP = censored median ratio × OAT's median inference "
                          f"time ({r['C_SIMP_s']:.3f} s) vs OAT inference ({r['C_inf_s']:.3f} s); 'never' = C_SIMP ≤ C_inf")
    g2 = load("evidence/g2_provisional.json")
    for prob, nid in (("P1_cantilever", "N040"), ("P2_mbb", "N041")):
        p = g2["per_problem"].get(prob)
        if p:
            register(nid, p["strong_baseline_s"], unit="s", text=f"{p['strong_baseline_s']:.2f} s",
                     source="evidence/g2_provisional.json", script="analysis/baseline_summary.py",
                     note=f"G2: {prob} 256², {p['solver']}, 150 its, median of 3, CPU pinned = {p['cpu_pinned']}; "
                          f"OAT Table 6 SIMP-GPU 68.30 s is {p['ratio_oat_over_ours']:.1f}× longer (cross-hardware)")
    for stage, nid in (("OAT inference 256", "N042"), ("ours GPU 256", "N043"), ("OAT SIMP 256 CG+OC", "N044"),
                       ("OAT inference 64", "N045"), ("ours PARDISO 64", "N046"), ("ours PARDISO 256", "N047"),
                       ("ours GPU 64", "N048"), ("OAT SIMP 64 CG+OC", "N049")):
        s = st.get(stage)
        if s and s["time_s_median"] is not None:
            register(nid, s["time_s_median"], unit="s", text=f"{s['time_s_median']:.2f} s", source=src, script=scr,
                     note=f"same machine, pinned: {stage}, median over 5 NITO problems "
                          f"(range {s['time_s_min']:.3f}–{s['time_s_max']:.3f} s)")
    wins, total = 0, 0
    for size in (256, 64):
        ev = load(f"evidence/oat_eval_n{size}.json") or []
        for e in ev:
            c = e["candidates"]
            if "OAT" in c and "ours[gpu]" in c:
                total += 1
                wins += c["ours[gpu]"]["CE_pct"] < c["OAT"]["CE_pct"]
    if total:
        register("N051", wins, text=f"{wins} of {total}", source="evidence/oat_eval_n256.json", script="retest/oat_harness/eval_designs.py",
                 note="problems (both sizes) where our 150-iteration GPU design has lower compliance error than OAT's "
                      "output under OAT's evaluator; also evidence/oat_eval_n64.json")
    for size, nid in ((256, "N052"), (64, "N053")):
        t = ttq.get(f"{size}_gpu")
        if t:
            r = t["rules"]["primary_ce_and_volume"]
            register(nid, r["n_matched"], text=f"{r['n_matched']} of {t['n_problems']}", source="evidence/ttq_summary.json",
                     script="analysis/ttq_summary.py",
                     note=f"{size}²: problems where our GPU run reached OAT's quality within 150 iterations (primary rule)")
    ed9 = ROOT / "figures" / "data" / "ed9_scheduling.csv"
    if ed9.exists():
        import csv
        rows9 = list(csv.DictReader(open(ed9, encoding="utf-8")))
        worst = max(rows9, key=lambda r: float(r["default_s"]) / float(r["pinned_s"]))
        v = float(worst["default_s"]) / float(worst["pinned_s"])
        register("N056", v, unit="×", text=f"{v:.1f}×", source="figures/data/ed9_scheduling.csv",
                 script="analysis/fig_extended.py",
                 note=f"largest ratio of default-scheduling to pinned median time ({worst['item']}); ED9")
    p1 = (g2 or {}).get("per_problem", {}).get("P1_cantilever")
    if p1:
        register("N054", p1["ratio_oat_over_ours"], unit="×", text=f"{p1['ratio_oat_over_ours']:.1f}×",
                 source="evidence/g2_provisional.json", script="analysis/baseline_summary.py",
                 note="OAT's reported SIMP-GPU time at 256² (68.30 s, RTX 4090) / our pinned GPU time for P1 (cross-hardware)")
    if energy and energy.get("by_stage"):
        for stage, nid in (("energy ours GPU 256", "N025"), ("energy OAT inference 256", "N026")):
            s = energy["by_stage"].get(stage)
            if s:
                register(nid, s["board_j_per_design_median"], unit="J", text=f"{s['board_j_per_design_median']:.0f} J",
                         source="evidence/energy.json", script="analysis/energy.py",
                         note=f"{stage}: GPU board energy per design (median over problems; instant power, exact window); "
                              f"above idle: {s['above_idle_j_per_design_median']:.0f} J")
    print(json.dumps(load("evidence/numbers.json"), indent=1, ensure_ascii=False)[:4000])


if __name__ == "__main__":
    main()
