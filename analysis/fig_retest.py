"""Same-machine OAT re-test figure (F3 panel for OAT, F4 time-to-quality, F5 break-even).

    python -m analysis.fig_retest

Reads figures/data/oat_retest_timings.csv (pinned, primary), evidence/oat_eval_n{64,256}.json,
figures/data/ttq_curves_n256_gpu.csv and evidence/breakeven.json. Writes figures/oat_retest.png/.svg and
figures/data/oat_retest_quality.csv.
Palette: dataviz reference categorical slots 1-3 (validated all-pairs, light mode), one hue per family:
ours = blue, OAT's ML model = orange, OAT's own SIMP (pyEDGE) = green. Within a family, marker fill separates
configurations (filled / hollow), and every method is named on the axis, so identity never rests on colour alone.
"""
import csv
import json
import math
import pathlib
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
INK, INK2, SURFACE, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e2dc"
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
# key -> (axis label, colour, filled marker)
METHODS = [("OAT inference", "OAT (inference, no refinement)", ORANGE, True),
           ("ours gpu", "ours: GPU multigrid-PCG", BLUE, True),
           ("ours pardiso", "ours: CPU PARDISO", BLUE, False),
           ("OAT SIMP CG+OC", "OAT's SIMP: pyEDGE CG", GREEN, True),
           ("OAT SIMP SPSOLVE+OC", "OAT's SIMP: pyEDGE SPSOLVE", GREEN, False)]
EVAL_KEYS = {"OAT": "OAT inference", "ours[gpu]": "ours gpu", "ours[pardiso]": "ours pardiso",
             "OAT-SIMP[CG_OC]": "OAT SIMP CG+OC", "OAT-SIMP[SPSOLVE_OC]": "OAT SIMP SPSOLVE+OC"}
T6 = {64: {"SIMP GPU": 9.13, "OAT": 0.508}, 256: {"SIMP GPU": 68.30, "OAT": 0.51}}


def style(ax, grid_axis="x"):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=7.5)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def series_key(r):
    return "OAT SIMP " + r["config"] if r["method"] == "OAT SIMP (pyEDGE)" else r["method"]


def dotrow(ax, y, values, color, filled):
    n = len(values)
    for i, v in enumerate(sorted(values)):
        ax.plot(v, y + (i - (n - 1) / 2) * 0.09, "o", ms=5, mfc=color if filled else SURFACE, mec=color, mew=1.4,
                zorder=3)
    if values:
        m = statistics.median(values)
        ax.vlines(m, y - 0.3, y + 0.3, colors=INK, linewidth=1.3, zorder=4)


def main():
    rows = [r for r in csv.DictReader(open(ROOT / "figures/data/oat_retest_timings.csv", encoding="utf-8"))
            if r["status"].startswith("ok")]
    fig = plt.figure(figsize=(12.5, 8.2), facecolor=SURFACE)
    gs = GridSpec(2, 4, figure=fig, height_ratios=[1, 1.15], hspace=0.42, wspace=0.12,
                  left=0.16, right=0.985, top=0.93, bottom=0.08)
    ys = {k: len(METHODS) - 1 - i for i, (k, *_rest) in enumerate(METHODS)}

    # (a) time per design, one axis per size. Ours: fresh 150-iteration runs with setup included (time-to-quality
    # series, BASELINE_PREREG §9 setup row); OAT inference: its own timing; OAT's SIMP: loop only (setup excluded).
    def ours_incl_setup(size, solver):
        f = ROOT / "figures" / "data" / f"ttq_curves_n{size}_{solver}.csv"
        if not f.exists():
            return None
        return [float(r["wall_incl_setup_s"]) for r in csv.DictReader(open(f, encoding="utf-8")) if int(r["iters"]) == 150]

    for j, size in enumerate((64, 256)):
        ax = fig.add_subplot(gs[0, j])
        for key, label, color, filled in METHODS:
            vals = [float(r["time_s"]) for r in rows if int(r["size"]) == size and series_key(r) == key]
            if key.startswith("ours "):
                incl = ours_incl_setup(size, key.split()[1])
                vals = incl if incl else vals
            dotrow(ax, ys[key], vals, color, filled)
        for lab, ls, txt in (("SIMP GPU", "--", "OAT Table 6\nSIMP-GPU"), ("OAT", ":", "OAT Table 6\nOAT")):
            ax.axvline(T6[size][lab], color=INK2, linestyle=ls, linewidth=0.9, zorder=1)
            ax.text(T6[size][lab], len(METHODS) - 0.35, txt, fontsize=6, color=INK2, ha="center", va="bottom")
        ax.set_xscale("log")
        ax.set_ylim(-0.6, len(METHODS) - 0.1)
        ax.set_yticks([ys[k] for k, *_ in METHODS])
        ax.set_yticklabels([m[1] for m in METHODS] if j == 0 else [], fontsize=7.5, color=INK)
        ax.set_xlabel(f"seconds per design, {size}² (log)", fontsize=8, color=INK)
        if j == 1:
            ax.text(1.0, -0.2, "ours: setup included; OAT's SIMP: loop only", transform=ax.transAxes, ha="right",
                    fontsize=6, color=INK2)
        style(ax)
        if j == 0:
            ax.set_title("a  Time per design, one RTX 5090, CPU pinned (dots = 5 problems, bar = median)",
                         loc="left", fontsize=9, color=INK, x=0.0, pad=16)

    # (b) compliance error under OAT's evaluator, one axis per size
    qrows = []
    for j, size in enumerate((64, 256)):
        ax = fig.add_subplot(gs[0, 2 + j])
        ev = json.loads((ROOT / "evidence" / f"oat_eval_n{size}.json").read_text(encoding="utf-8"))
        for ek, key in EVAL_KEYS.items():
            label, color, filled = next((m[1], m[2], m[3]) for m in METHODS if m[0] == key)
            vals = []
            for e in ev:
                cand = e["candidates"].get(ek)
                if cand:
                    vals.append(cand["CE_pct"])
                    qrows.append({"size": size, "problem_id": e["problem_id"], "series": key,
                                  "CE_pct": cand["CE_pct"], "vf_thresholded": cand["vf_thresholded"],
                                  "vf_mean": cand["vf_mean"], "vf_target": e["vf_target"]})
            dotrow(ax, ys[key], vals, color, filled)
        ax.axvline(0, color=INK2, linewidth=0.8, zorder=1)
        ax.set_xscale("symlog", linthresh=1.0)
        ax.set_ylim(-0.6, len(METHODS) - 0.1)
        ax.set_yticks([ys[k] for k, *_ in METHODS])
        ax.set_yticklabels([], fontsize=7.5)
        lo, hi = ax.get_xlim()
        ax.set_xlim(lo, hi * 1.6)
        ax.set_xlabel(f"CE vs dataset design, {size}² (%, symlog)", fontsize=8, color=INK)
        style(ax)
        if j == 0:
            ax.set_title("b  Quality under OAT's own evaluator (lower is better)", loc="left", fontsize=9, color=INK,
                         pad=16)

    # (c) time to quality at 256²: our compliance error minus OAT's, per problem
    ax = fig.add_subplot(gs[1, 0:2])
    tq = list(csv.DictReader(open(ROOT / "figures/data/ttq_curves_n256_gpu.csv", encoding="utf-8")))
    inf = {int(r["problem_id"]): float(r["time_s"]) for r in rows if int(r["size"]) == 256 and r["method"] == "OAT inference"}
    for pid in sorted({int(r["problem_id"]) for r in tq}):
        pr = sorted((r for r in tq if int(r["problem_id"]) == pid), key=lambda r: int(r["iters"]))
        cap = max(float(pr[0]["vf_target"]), float(pr[0]["vf_OAT"]))
        ts = [float(r["wall_incl_setup_s"]) for r in pr]
        d = [float(r["CE_pct"]) - float(r["CE_OAT_pct"]) for r in pr]
        ax.plot(ts, d, color=BLUE, linewidth=1.5, zorder=2)
        for t, v, r in zip(ts, d, pr):          # hollow = more material than OAT or the target: no match
            ok = float(r["vf_thresholded"]) <= cap
            ax.plot(t, v, "o", ms=3.8, mfc=BLUE if ok else SURFACE, mec=BLUE, mew=1.0, zorder=3)
        ax.text(ts[-1] * 1.06, d[-1], f"problem {pid}", fontsize=6.5, color=INK, va="center")
        ax.plot(inf[pid], 0, "D", ms=6, mfc=ORANGE, mec=SURFACE, mew=1.2, zorder=4)
    ax.axhline(0, color=INK2, linewidth=0.9, zorder=1)
    ax.set_xscale("log")
    ax.set_yscale("symlog", linthresh=1.0)
    ax.set_xlim(0.18, 25)
    ax.set_xlabel("wall-clock incl. setup, 256² (s, log)", fontsize=8, color=INK)
    ax.set_ylabel("our CE minus OAT's CE (pp, symlog)", fontsize=8, color=INK)
    ax.legend([plt.Line2D([], [], color=BLUE, marker="o", ms=3.8),
               plt.Line2D([], [], color=BLUE, marker="o", ms=3.8, mfc=SURFACE, ls=""),
               plt.Line2D([], [], marker="D", ms=6, mfc=ORANGE, mec=SURFACE, ls="")],
              ["ours, GPU: fresh runs at 5 … 150 iterations", "uses more material than OAT or the target",
               "OAT inference time (at 0 by definition)"],
              fontsize=6.5, frameon=False, loc="upper right", labelcolor=INK)
    ax.set_title("c  Time to OAT's quality, 256²: matched where a filled dot reaches 0 or below",
                 loc="left", fontsize=9, color=INK)
    style(ax, "both")

    # (d) break-even uses with OAT's formula and training cost
    ax = fig.add_subplot(gs[1, 2:4])
    be = json.loads((ROOT / "evidence" / "breakeven.json").read_text(encoding="utf-8"))
    rows_be = be["rows"]

    def pick(scenario, size, simp_prefix, inf_label=None):
        return next(r for r in rows_be if r["scenario"] == scenario and r["size"] == size
                    and r["C_SIMP_label"].startswith(simp_prefix) and (inf_label is None or r["C_inf_label"] == inf_label))

    bars = [("OAT, stated (App. G)", be["oat_tau_stated"], INK2),
            ("OAT Table 6 numbers, 256²", pick("OAT Table 6 as reported", 256, "SIMP GPU", "OAT")["tau_uses"], ORANGE),
            ("same machine, 150 iterations incl. setup, 256²",
             pick("same machine, 150 iterations incl. setup", 256, "ours gpu")["tau_uses"], BLUE),
            ("same machine, matched quality, 256²",
             pick("same machine, matched quality (primary, censored median ratio)", 256, "ours gpu")["tau_uses"], BLUE),
            ("same machine, matched quality, 64²",
             pick("same machine, matched quality (primary, censored median ratio)", 64, "ours gpu")["tau_uses"], BLUE)]
    yb = list(range(len(bars)))[::-1]
    for y, (name, v, col) in zip(yb, bars):
        ax.text(1.08e5, y + 0.33, name, fontsize=7.5, color=INK, va="bottom")          # label above its bar
        if math.isinf(v):
            ax.text(1.08e5, y, "never: our matched-quality time is below OAT's inference time", va="center",
                    fontsize=7, color=INK)
        else:
            ax.barh(y, v, height=0.42, color=col, edgecolor=SURFACE, linewidth=1.0)
            ax.text(v * 1.1, y, f"{v / 1e6:.2f} M" if v < 1e7 else f"{v / 1e6:.1f} M", va="center", fontsize=7,
                    color=INK)
    ax.set_yticks([])
    ax.set_ylim(-0.6, len(bars) - 0.1)
    ax.set_xscale("log")
    ax.set_xlim(1e5, 1e8)
    ax.set_xlabel("break-even uses τ = C_train / (C_SIMP − C_inference) (log)", fontsize=8, color=INK)
    ax.set_title("d  Break-even with OAT's formula (184 H100-days)", loc="left", fontsize=9, color=INK)
    style(ax, "x")

    out = ROOT / "figures"
    fig.savefig(out / "oat_retest.png", dpi=200, facecolor=SURFACE)
    fig.savefig(out / "oat_retest.svg", facecolor=SURFACE)
    with open(out / "data" / "oat_retest_quality.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(qrows[0]))
        w.writeheader()
        w.writerows(qrows)
    print("wrote figures/oat_retest.png/.svg")


if __name__ == "__main__":
    main()
