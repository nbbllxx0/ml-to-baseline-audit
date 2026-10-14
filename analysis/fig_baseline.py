"""Strong-baseline figures (preview of F4 / ED3): wall-clock per 150-iteration run, and time per iteration.

    python -m analysis.fig_baseline

Reads figures/data/baseline_timings.csv (from analysis.baseline_summary) and the per-iteration records.
Writes figures/baseline_timing.png/.svg and figures/data/baseline_per_iteration_P1_256.csv.
Palette: dataviz reference categorical slots 1-3 (validated all-pairs, light mode); slot 3 is below 3:1
contrast, so every series carries a direct label.
"""
import csv
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
INK, INK2, SURFACE, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e2dc"
COLORS = {"gpu": "#2a78d6", "pardiso": "#eb6834", "superlu": "#1baf7a"}
LABELS = {"gpu": "GPU multigrid-PCG (strong)", "pardiso": "CPU PARDISO (strong)", "superlu": "CPU SuperLU, top88-faithful port"}
OAT = {64: {"SIMP GPU": 9.13, "SIMP CPU": 3.45}, 256: {"SIMP GPU": 68.30, "SIMP CPU": 69.45}}


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def main():
    rows = list(csv.DictReader(open(ROOT / "figures/data/baseline_timings.csv", encoding="utf-8")))
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 4.0), facecolor=SURFACE, gridspec_kw={"width_ratios": [1.15, 1]})
    # (a) grouped bars: problem x size, bars per solver, log scale
    groups = [(p, n) for n in (64, 256) for p in ("P1_cantilever", "P2_mbb")]
    solvers = ["gpu", "pardiso", "superlu"]
    w = 0.26
    for gi, (p, n) in enumerate(groups):
        for si, s in enumerate(solvers):
            r = next((r for r in rows if r["problem"] == p and int(r["n"]) == n and r["solver"] == s), None)
            if r is None:
                continue
            t = float(r["total_s_median"])
            x = gi + (si - 1) * w
            a.bar(x, t, width=w - 0.03, color=COLORS[s], edgecolor=SURFACE, linewidth=1.0)
            a.text(x, t * 1.12, f"{t:.1f}" if t >= 1 else f"{t:.2f}", ha="center", va="bottom", fontsize=6.5, color=INK)
        for lab, ls in (("SIMP GPU", "--"), ("SIMP CPU", ":")):
            v = OAT[n][lab]
            a.hlines(v, gi - 1.5 * w, gi + 1.5 * w, colors=INK2, linestyles=ls, linewidth=1.0)
    a.set_yscale("log")
    a.set_xticks(range(len(groups)))
    a.set_xticklabels([f"{'cantilever' if p.startswith('P1') else 'MBB'}\n{n}×{n}" for p, n in groups], fontsize=8, color=INK)
    a.set_ylabel("wall-clock, 150 SIMP iterations (s, log)", fontsize=8, color=INK)
    a.set_title("a  Strong baselines vs a typical port (this machine)", loc="left", fontsize=9, color=INK)
    style(a)
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[s]) for s in solvers]
    handles += [plt.Line2D([], [], color=INK2, ls="--"), plt.Line2D([], [], color=INK2, ls=":")]
    a.legend(handles, [LABELS[s] for s in solvers] + ["OAT Table 6 SIMP-GPU (RTX 4090)", "OAT Table 6 SIMP-CPU (i9-14900K)"],
             fontsize=6.5, frameon=False, loc="upper left", labelcolor=INK)

    # (b) time per iteration along the run, P1 256
    series = []
    for s in solvers:
        r = next((r for r in rows if r["problem"] == "P1_cantilever" and int(r["n"]) == 256 and r["solver"] == s), None)
        if r is None:
            continue
        rec = json.loads((ROOT / r["run_dir"] / "record_rep0.json").read_text(encoding="utf-8"))
        t_ms = [1000 * v for v in rec["t_iter"]]
        b.plot(range(1, len(t_ms) + 1), t_ms, color=COLORS[s], linewidth=2.0)
        b.text(len(t_ms) + 2, t_ms[-1], LABELS[s].split(" (")[0].replace(", top88-faithful port", ""), color=INK,
               fontsize=7, va="center")
        series.append((s, t_ms, rec.get("pcg_its")))
    b.set_yscale("log")
    b.set_xlim(0, 190)
    b.set_xlabel("design iteration", fontsize=8, color=INK)
    b.set_ylabel("time per iteration (ms, log)", fontsize=8, color=INK)
    b.set_title("b  Cantilever 256×256: cost per iteration", loc="left", fontsize=9, color=INK)
    style(b)
    fig.tight_layout()
    out = ROOT / "figures"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "baseline_timing.png", dpi=200, facecolor=SURFACE)
    fig.savefig(out / "baseline_timing.svg", facecolor=SURFACE)
    with open(out / "data" / "baseline_per_iteration_P1_256.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["iteration"] + [f"{s}_ms" for s, _, _ in series] + ["gpu_pcg_its"])
        n_it = max(len(t) for _, t, _ in series)
        pcg = next((p for s, _, p in series if s == "gpu"), None)
        for i in range(n_it):
            wr.writerow([i + 1] + [f"{t[i]:.3f}" if i < len(t) else "" for _, t, _ in series] + [pcg[i] if pcg else ""])
    print("wrote figures/baseline_timing.png/.svg and figure data CSV")


if __name__ == "__main__":
    main()
