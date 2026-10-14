"""F3 (claimed vs re-tested speed-up) and F5 (break-even against resolution; energy per design), from evidence files.

    python -m analysis.fig3_f5

F3: for each re-tested article and size, a line from the speed-up the article reports (its own hardware) to the
    same-machine speed-up against a strong baseline under the article's own protocol (OAT: 150 iterations, setup
    included; HGTO: each method to its own convergence rule) and then at matched quality. Values below 1 mean the
    classical baseline is faster. Articles: OAT (64², 256²) and HGTO (480x160, 960x320).
F5: (a) τ = C_train / (C_SIMP − C_inference) against resolution for OAT's reported times, the same-machine 150-iteration
    times and the matched-quality times; "never" is drawn at the top edge. (b) GPU board energy per design.
Writes figures/f3_speedup.png/.svg, figures/f5_breakeven_energy.png/.svg and figures/data/f3_speedup.csv.
"""
import csv
import json
import math
import pathlib
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


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def f3():
    num = load("evidence/numbers.json")
    ttq = load("evidence/ttq_summary.json")
    rows = [{"article": "OAT", "size": "256²", "claimed": num["N016"]["value"],
             "same_machine_strong_baseline": num["N017"]["value"], "matched_quality": num["N018"]["value"]},
            {"article": "OAT", "size": "64²", "claimed": num["N019"]["value"],
             "same_machine_strong_baseline": num["N020"]["value"], "matched_quality": num["N039"]["value"]}]
    hg = load("evidence/hgto_retest.json")["configs"]
    for cfg, size in (("cantilever_960x320", "960×320"), ("cantilever_480x160", "480×160")):
        e = hg[cfg]
        rows.append({"article": "HGTO", "size": size, "claimed": e["published"]["oc_over_hgto"],
                     "same_machine_strong_baseline": e["ratios_vs_hgto_gpu"]["ours"],
                     "matched_quality": e["matched_quality_ours"]["ratio_vs_hgto_gpu"]})
    # All values are t_SIMP / t_ML (the ML model's speed-up); N018 and N039 are "ours / OAT" time ratios, the same
    # quantity. Values below 1 mean the classical baseline is faster.
    assert abs(num["N039"]["value"] - ttq["64_gpu"]["rules"]["primary_ce_and_volume"]["ratio_median_censored"]) < 1e-12
    fig, ax = plt.subplots(figsize=(7.0, 4.8), facecolor=SURFACE)
    colors = [BLUE, GREEN, ORANGE, "#eda100"]
    for i, r in enumerate(rows):
        x = [0, 1, 2]
        y = [r["claimed"], r["same_machine_strong_baseline"], r["matched_quality"]]
        col = colors[i]
        ax.plot(x, y, color=col, linewidth=1.6, marker="o", ms=6, zorder=3)
        for xi, yi in zip(x, y):
            ax.text(xi + 0.06, yi, f"{yi:.2f}×" if yi < 10 else (f"{yi:.1f}×" if yi < 100 else f"{yi:.0f}×"), fontsize=7, color=INK, va="center")
        ax.text(-0.08, y[0], f"{r['article']} {r['size']}", fontsize=7.5, color=INK, ha="right", va="center")
    ax.axhline(1.0, color=INK2, linestyle="--", linewidth=0.9)
    ax.text(2.35, 1.05, "equal speed", fontsize=6.5, color=INK2, va="bottom", ha="right")
    ax.set_yscale("log")
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["reported\n(paper's hardware)", "same machine, strong\nbaseline, paper's protocol",
                        "same machine,\nmatched quality"], fontsize=7.5, color=INK)
    ax.set_xlim(-0.9, 2.5)
    ax.set_ylabel("speed-up of the ML model over SIMP (log)", fontsize=8, color=INK)
    ax.set_title("F3  Reported and re-tested speed-up (one line per article and size)", loc="left", fontsize=9,
                 color=INK)
    style(ax, "y")
    fig.tight_layout()
    fig.savefig(ROOT / "figures" / "f3_speedup.png", dpi=200, facecolor=SURFACE)
    fig.savefig(ROOT / "figures" / "f3_speedup.svg", facecolor=SURFACE)
    plt.close(fig)
    with open(ROOT / "figures" / "data" / "f3_speedup.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def f5():
    be = load("evidence/breakeven.json")["rows"]
    series = [("OAT's reported times (Table 6)", "OAT Table 6 as reported", "SIMP GPU", ORANGE),
              ("same machine, ours GPU, 150 iterations with setup", "same machine, 150 iterations incl. setup", "ours gpu", BLUE),
              ("same machine, ours GPU, matched quality", "same machine, matched quality (primary, censored median ratio)", "ours gpu", GREEN)]
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2), facecolor=SURFACE)
    top = 5e8
    for label, scen, prefix, col in series:
        pts = []
        for size in (64, 256):
            r = next((r for r in be if r["scenario"] == scen and r["size"] == size and r["C_SIMP_label"].startswith(prefix)
                      and (scen != "OAT Table 6 as reported" or r["C_inf_label"] == "OAT")), None)
            if r:
                pts.append((size, top if math.isinf(r["tau_uses"]) else r["tau_uses"], math.isinf(r["tau_uses"])))
        a.plot([p[0] for p in pts], [p[1] for p in pts], color=col, marker="o", ms=6, linewidth=1.6, label=label)
        for s, v, never in pts:
            a.text(s * 1.06, v, "never" if never else (f"{v / 1e6:.2f} M" if v < 1e7 else f"{v / 1e6:.1f} M"), fontsize=6.5,
                   color=INK, va="center")
    a.axhline(2.32e6, color=INK2, linestyle=":", linewidth=0.9)
    a.text(66, 2.32e6 * 1.1, "OAT's stated 2.32 M", fontsize=6.5, color=INK2)
    a.set_xscale("log", base=2)
    a.set_xticks([64, 256])
    a.set_xticklabels(["64²", "256²"])
    a.set_xlim(50, 400)
    a.set_yscale("log")
    a.set_ylim(1e5, top * 1.5)
    a.set_xlabel("resolution", fontsize=8, color=INK)
    a.set_ylabel("break-even uses τ (log; top edge = never)", fontsize=8, color=INK)
    a.set_title("a  Break-even with OAT's formula and 184 H100-days", loc="left", fontsize=9, color=INK)
    a.legend(fontsize=6.5, frameon=False, loc="lower left", labelcolor=INK)
    style(a)
    e = load("evidence/energy.json")["rows"]
    order = [("energy OAT inference 64", "OAT inference, 64²", ORANGE), ("energy ours GPU 64", "ours GPU, 150 its, 64²", BLUE),
             ("energy OAT inference 256", "OAT inference, 256²", ORANGE), ("energy ours GPU 256", "ours GPU, 150 its, 256²", BLUE)]
    for i, (stage, label, col) in enumerate(order):
        v = [r["board_j_per_design"] for r in e if r["stage"] == stage]
        b.plot(v, [i] * len(v), "o", ms=5, color=col, zorder=3)
        if v:
            m = statistics.median(v)
            b.vlines(m, i - 0.3, i + 0.3, colors=INK, linewidth=1.3, zorder=4)
            b.text(max(v) * 1.15, i, f"median {m:.0f} J", fontsize=6.5, color=INK, va="center")
    b.set_yticks(range(len(order)))
    b.set_yticklabels([o[1] for o in order], fontsize=7.5, color=INK)
    b.invert_yaxis()
    b.set_xscale("log")
    b.set_xlim(50, 1e4)
    b.set_xlabel("GPU board energy per design (J, log)", fontsize=8, color=INK)
    b.set_title("b  Energy per design, one RTX 5090 (dots = problems)", loc="left", fontsize=9, color=INK)
    style(b, "x")
    fig.tight_layout()
    fig.savefig(ROOT / "figures" / "f5_breakeven_energy.png", dpi=200, facecolor=SURFACE)
    fig.savefig(ROOT / "figures" / "f5_breakeven_energy.svg", facecolor=SURFACE)
    plt.close(fig)


def main():
    f3()
    f5()
    print("wrote figures/f3_speedup.png and figures/f5_breakeven_energy.png")


if __name__ == "__main__":
    main()
