"""Extended Data figures for the strong baseline and the re-test: ED2, ED3, ED9, and the energy panel of F5.

    python -m analysis.fig_extended

ED2  baseline correctness: gating test values against their thresholds; true relative residuals of every accepted
     GPU solve in the pinned benchmark runs.
ED3  strong-baseline scaling, 64² to 1024² (pinned GPU benchmark runs, P1 and P2; PARDISO where run).
ED9  timing sensitivity to CPU placement: default scheduling against pinned, per method and size.
F5b  GPU board energy per design (pinned power runs; instant power over the exact window).
Palette: dataviz reference categorical slots 1-3 (validated all-pairs, light mode).
Writes figures/ed2_baseline_correctness.png, figures/ed3_scaling.png, figures/ed9_scheduling.png,
figures/f5b_energy.png (and .svg), plus their data CSVs under figures/data/.
"""
import csv
import glob
import json
import pathlib
import re
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
INK, INK2, SURFACE, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e2dc"
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"


def style(ax, grid_axis="both"):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=7.5)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def save(fig, name, rows=None):
    out = ROOT / "figures"
    fig.savefig(out / f"{name}.png", dpi=200, facecolor=SURFACE)
    fig.savefig(out / f"{name}.svg", facecolor=SURFACE)
    if rows:
        with open(out / "data" / f"{name}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    plt.close(fig)


def bench_runs(pinned=True):
    runs = {}
    for f in sorted(glob.glob(str(ROOT / "retest" / "runs" / "*" / "summary.json"))):
        d = pathlib.Path(f).parent
        if pinned != d.name.endswith("_pinned"):
            continue
        s = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        if s.get("iters") == 150:
            runs[(s["problem"], s["n"], s["solver"])] = (d, s)      # latest per key
    return runs


def ed2():
    tests = []
    for part in ("gpu", "pardiso"):
        d = json.loads((ROOT / "evidence" / f"baseline_tests_{part}.json").read_text(encoding="utf-8"))
        for t in d["results"]:
            m = re.search(r"([<>]=?)\s*([0-9.eE+-]+)", str(t["threshold"]))
            tests.append({"part": part, "test": t["test"], "value": t["value"], "threshold": t["threshold"],
                          "threshold_value": float(m.group(2)) if m else None,
                          "direction": (m.group(1)[0] if m else ""), "pass": t["pass"], "gating": t["gating"]})
    res = []
    for (prob, n, solver), (d, s) in sorted(bench_runs().items()):
        if solver != "gpu":
            continue
        rec = json.loads((d / "record_rep0.json").read_text(encoding="utf-8"))
        res += [{"problem": prob, "n": n, "true_res": v, "fallback": fb} for v, fb in zip(rec["true_res"], rec["fallback"])]
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 5.2), facecolor=SURFACE, gridspec_kw={"width_ratios": [1.5, 1]})
    gating = [t for t in tests if t["gating"] and isinstance(t["value"], (int, float)) and t["threshold_value"]]
    for i, t in enumerate(gating):
        # distance to failure, < 1 = pass: |value|/threshold for "<" tests, threshold/|value| for ">" tests
        v = abs(t["value"]) or 1e-300
        ratio = (t["threshold_value"] / v) if t["direction"] == ">" else (v / t["threshold_value"])
        a.plot(max(ratio, 1e-18), i, "o", ms=4.5, color=BLUE if t["part"] == "gpu" else ORANGE, zorder=3)
    a.axvline(1.0, color=INK2, linestyle="--", linewidth=0.9)
    a.text(1.1, -0.8, "threshold", fontsize=6.5, color=INK2, va="bottom")
    a.set_xscale("log")
    a.set_yticks(range(len(gating)))
    a.set_yticklabels([t["test"][:70] for t in gating], fontsize=5.3, color=INK)
    a.invert_yaxis()
    a.set_xlabel("distance to the threshold (log; pass if < 1)", fontsize=8, color=INK)
    a.set_title(f"a  Gating correctness tests ({sum(t['pass'] for t in gating)}/{len(gating)} pass)", loc="left",
                fontsize=9, color=INK)
    a.legend([plt.Line2D([], [], ls="", marker="o", color=BLUE), plt.Line2D([], [], ls="", marker="o", color=ORANGE)],
             ["GPU multigrid-PCG tests", "CPU PARDISO tests"], fontsize=6.5, frameon=False, loc="lower right",
             labelcolor=INK)
    style(a, "x")
    vals = [r["true_res"] for r in res if r["true_res"] > 0]
    if vals:
        import math
        bins = [10 ** (x / 4) for x in range(int(4 * math.log10(min(vals))) - 1, int(4 * math.log10(max(vals))) + 2)]
        b.hist(vals, bins=bins, color=BLUE, edgecolor=SURFACE)
        b.set_xscale("log")
        b.axvline(1e-7, color=INK2, linestyle="--", linewidth=0.9)
        b.text(1.1e-7, b.get_ylim()[1] * 0.95, "acceptance 1e-7", fontsize=6.5, color=INK2, va="top")
    b.set_xlabel("true relative residual of each accepted GPU solve (log)", fontsize=8, color=INK)
    b.set_ylabel("solves", fontsize=8, color=INK)
    nfb = sum(1 for r in res if r["fallback"])
    b.set_title(f"b  {len(res)} GPU solves (pinned runs), {nfb} fallbacks", loc="left", fontsize=9, color=INK)
    style(b, "y")
    fig.tight_layout()
    save(fig, "ed2_baseline_correctness", tests)


def ed3():
    runs = bench_runs()
    rows = []
    for (prob, n, solver), (d, s) in sorted(runs.items()):
        rows.append({"problem": prob, "n": n, "solver": solver, "dofs": 2 * (n + 1) * (n + 1) if prob.startswith("P1") else "",
                     "per_iter_s_median": s["per_iter_s_median"], "total_s_median": s["total_s_median"],
                     "pcg_its_median": s.get("pcg_its_median", ""), "run": d.name})
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4), facecolor=SURFACE)
    for prob, mk in (("P1_cantilever", "o"), ("P2_mbb", "s")):
        for solver, col, filled in (("gpu", BLUE, True), ("pardiso", BLUE, False)):
            pts = sorted((r["n"], r["per_iter_s_median"] * 1000) for r in rows if r["problem"] == prob and r["solver"] == solver)
            if pts:
                a.plot([p[0] for p in pts], [p[1] for p in pts], marker=mk, ms=5, color=col, mfc=col if filled else SURFACE,
                       linewidth=1.4, linestyle="-" if filled else "--",
                       label=f"{'cantilever' if prob.startswith('P1') else 'MBB'}, {'GPU multigrid-PCG' if solver == 'gpu' else 'CPU PARDISO'}")
        pts = sorted((r["n"], r["pcg_its_median"]) for r in rows if r["problem"] == prob and r["solver"] == "gpu" and r["pcg_its_median"] != "")
        if pts:
            b.plot([p[0] for p in pts], [p[1] for p in pts], marker=mk, ms=5, color=BLUE, linewidth=1.4,
                   label="cantilever" if prob.startswith("P1") else "MBB")
    for ax in (a, b):
        ax.set_xscale("log", base=2)
        ax.set_xticks([64, 128, 256, 512, 1024])
        ax.set_xticklabels(["64²", "128²", "256²", "512²", "1024²"])
        ax.set_xlabel("mesh (elements)", fontsize=8, color=INK)
        style(ax)
    a.set_yscale("log")
    a.set_ylabel("time per SIMP iteration (ms, log; median)", fontsize=8, color=INK)
    a.set_title("a  Cost per iteration, CPU pinned", loc="left", fontsize=9, color=INK)
    a.legend(fontsize=6.5, frameon=False, labelcolor=INK)
    b.set_ylabel("PCG iterations per solve (median over 150 iterations)", fontsize=8, color=INK)
    b.set_ylim(0, None)
    b.set_title("b  Multigrid-PCG iterations stay flat with mesh size", loc="left", fontsize=9, color=INK)
    b.legend(fontsize=6.5, frameon=False, labelcolor=INK)
    fig.tight_layout()
    save(fig, "ed3_scaling", rows)


def ed9():
    pinned = json.loads((ROOT / "evidence" / "oat_retest_summary.json").read_text(encoding="utf-8"))["stages"]
    default = json.loads((ROOT / "evidence" / "oat_retest_summary_default_sched.json").read_text(encoding="utf-8"))["stages"]
    rows = []
    for stage in pinned:
        if stage in default and pinned[stage]["time_s_median"] and default[stage]["time_s_median"]:
            rows.append({"item": stage, "default_s": default[stage]["time_s_median"], "pinned_s": pinned[stage]["time_s_median"]})
    up, pp = bench_runs(pinned=False), bench_runs(pinned=True)
    for key in sorted(set(up) & set(pp)):
        rows.append({"item": f"G2 {key[2]} {key[0].split('_')[0]} {key[1]}", "default_s": up[key][1]["total_s_median"],
                     "pinned_s": pp[key][1]["total_s_median"]})
    fig, ax = plt.subplots(figsize=(8.5, 0.32 * len(rows) + 1.2), facecolor=SURFACE)
    for i, r in enumerate(rows):
        ax.plot([r["default_s"], r["pinned_s"]], [i, i], color=GRID, linewidth=2.2, zorder=1)
        ax.plot(r["default_s"], i, "o", ms=5, mfc=SURFACE, mec=INK2, mew=1.2, zorder=2)
        ax.plot(r["pinned_s"], i, "o", ms=5, color=BLUE, zorder=3)
        ax.text(max(r["default_s"], r["pinned_s"]) * 1.12, i, f"{r['default_s'] / r['pinned_s']:.2f}×", fontsize=6.5,
                color=INK, va="center")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r["item"] for r in rows], fontsize=7, color=INK)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlabel("median seconds per design or run (log)", fontsize=8, color=INK)
    ax.legend([plt.Line2D([], [], ls="", marker="o", mfc=SURFACE, mec=INK2), plt.Line2D([], [], ls="", marker="o", color=BLUE)],
              ["default Windows scheduling", "pinned to performance cores, high priority"], fontsize=6.5, frameon=False,
              loc="lower left", labelcolor=INK)
    ax.set_title("ED9  Timing sensitivity to CPU placement (label = default / pinned)", loc="left", fontsize=9, color=INK)
    style(ax, "x")
    fig.tight_layout()
    save(fig, "ed9_scheduling", rows)


def energy():
    e = json.loads((ROOT / "evidence" / "energy.json").read_text(encoding="utf-8"))
    rows = [{"stage": r["stage"], "size": r["size"], "problem_id": r["problem_id"], "board_j": r["board_j_per_design"]}
            for r in e["rows"]]
    fig, ax = plt.subplots(figsize=(6.5, 3.0), facecolor=SURFACE)
    order = [("energy OAT inference 64", "OAT inference, 64²", ORANGE), ("energy ours GPU 64", "ours GPU, 150 its, 64²", BLUE),
             ("energy OAT inference 256", "OAT inference, 256²", ORANGE), ("energy ours GPU 256", "ours GPU, 150 its, 256²", BLUE)]
    for i, (stage, label, col) in enumerate(order):
        v = [r["board_j"] for r in rows if r["stage"] == stage]
        ax.plot(v, [i] * len(v), "o", ms=5, color=col, alpha=0.9, zorder=3)
        if v:
            m = statistics.median(v)
            ax.vlines(m, i - 0.3, i + 0.3, colors=INK, linewidth=1.3, zorder=4)
            ax.text(max(v) * 1.15, i, f"median {m:.0f} J", fontsize=6.5, color=INK, va="center")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([o[1] for o in order], fontsize=7.5, color=INK)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(50, 1e4)
    ax.set_xlabel("GPU board energy per design (J, log)", fontsize=8, color=INK)
    ax.set_title("F5b  Energy per design, one RTX 5090 (dots = problems)", loc="left", fontsize=9, color=INK)
    style(ax, "x")
    fig.tight_layout()
    save(fig, "f5b_energy", rows)


def main():
    (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
    for f in (ed2, ed3, ed9, energy):
        f()
        print("wrote", f.__name__)


if __name__ == "__main__":
    main()
