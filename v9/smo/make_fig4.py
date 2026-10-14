"""Fig. 4: OAT same-machine timing (a), compliance error (b) and time to OAT's quality (c).

    python v6/smo/make_fig4.py

Evidence (read-only): evidence/ttq_summary.json, oat_retest_summary.json, oat_eval_n256.json, oat_eval_n64.json and
figures/data/ttq_curves_n{64,256}_gpu.csv. Drawn as fig3_oat in v4/manuscript/figures/make_figures.py, which is
imported for its house style and loaders without writing into v4/. Changes from v4: panel a labels 0.3, 1, 3, 10 and
30 s, panel b spells out "150 iterations", and panel c numbers each curve by its problem, as in Online Resource 2.
The plotted values are checked against v4's figures/data/fig3_oat.csv.
Writes fig4_oat.pdf into smo/figures/ and arxiv/figures/.
"""
import csv
import io
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "v4" / "manuscript" / "figures"))
import make_figures as mf  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import numpy as np  # noqa: E402

OUTS = [HERE / "figures" / "fig4_oat.pdf", HERE.parent / "arxiv" / "figures" / "fig4_oat.pdf"]
C = mf.C
# panel c problem labels: (x offset pt, y offset pt, ha, va); the default sits right of the curve's last budget
LABEL_AT = {676: (0, 2, "right", "bottom"), 1935: (2, -1.5, "left", "top"), 1961: (2, -1.5, "left", "top")}


def same_as_v4(rows, header, name):
    """The plotted values must equal the ones v4 wrote, so the redraw cannot move a mark."""
    buf = io.StringIO(newline="")
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    if buf.getvalue() != (mf.DATA / f"{name}.csv").read_bytes().decode("utf-8"):
        raise SystemExit(f"plotted values differ from v4 figures/data/{name}.csv")


def main():
    tt, oat = mf.load("ttq_summary.json"), mf.load("oat_retest_summary.json")
    e256, e64 = mf.load("oat_eval_n256.json"), mf.load("oat_eval_n64.json")
    st = oat["stages"]
    fig = plt.figure(figsize=(mf.W2, 122 * mf.MM))
    gs = fig.add_gridspec(2, 3, left=0.2, right=0.845, bottom=0.085, top=0.975, wspace=0.18, hspace=0.36)
    rows = []
    cats = [("OAT inference", C["oat"], "o", True), ("Ours, GPU (multigrid)", C["gpu"], "o", True),
            ("Ours, CPU (PARDISO)", C["cpu"], "D", False), ("OAT's SIMP, CG", C["oatsimp"], "s", True),
            ("OAT's SIMP, direct", C["oatsimp"], "s", False)]
    for j, n in enumerate((64, 256)):
        ax = fig.add_subplot(gs[0, j])
        series = {
            "OAT inference": [v["time_s"] for v in st[f"OAT inference {n}"]["per_problem"].values()],
            "Ours, GPU (multigrid)": [q["wall_150_incl_setup_s"] for q in tt[f"{n}_gpu"]["per_problem"]],
            "Ours, CPU (PARDISO)": [q["wall_150_incl_setup_s"] for q in tt[f"{n}_pardiso"]["per_problem"]],
            "OAT's SIMP, CG": [v["time_s"] for v in st[f"OAT SIMP {n} CG+OC"]["per_problem"].values()],
        }
        if n == 64:
            series["OAT's SIMP, direct"] = [v["time_s"] for v in st["OAT SIMP 64 SPSOLVE+OC"]["per_problem"].values()]
        for i, (lab, col, mk, filled) in enumerate(cats):
            yy = len(cats) - 1 - i
            if lab not in series:
                ax.text(1.0, yy, "not timed", fontsize=8, color=C["grey"], va="center", ha="left")
                continue
            v = np.array(series[lab])
            jit = np.linspace(-0.18, 0.18, len(v))
            ax.plot(v, yy + jit, ls="none", marker=mk, ms=3.6, mfc=col if filled else "white", mec=col, mew=0.8)
            ax.plot([np.median(v)] * 2, [yy - 0.3, yy + 0.3], color="black", lw=1.1)
            rows += [[f"a {n}", lab, f"{t:.4f}"] for t in v]
        ax.set_xscale("log")
        ax.set_xlim(0.2, 80)
        xt = [0.3, 1, 3, 10, 30]
        ax.set_xticks(xt)
        ax.set_xticklabels([f"{v:g}" for v in xt])
        ax.xaxis.set_minor_formatter(mticker.NullFormatter())
        ax.set_yticks(range(len(cats)))
        ax.set_yticklabels([c[0] for c in cats][::-1] if j == 0 else [])
        ax.set_xlabel("Time per design (s)")
        ax.set_ylim(-0.6, len(cats) - 0.4)
        ax.text(0.97, 0.97, f"{n}²", transform=ax.transAxes, ha="right", va="top", fontsize=8, fontweight="bold")
    fig.text(0.01, 0.975, "a", fontsize=8, fontweight="bold", va="top")
    # b: compliance error under OAT's evaluator (tick labels on the right, clear of panel a)
    ax = fig.add_subplot(gs[0, 2])
    ax.yaxis.tick_right()
    ax.spines["right"].set_visible(True)
    ax.spines["left"].set_visible(False)
    lab_b = [("OAT", "OAT", C["oat"], "o", True), ("Ours, 150 it.", "ours[gpu]", C["gpu"], "o", True),
             ("OAT's SIMP", "OAT-SIMP[CG_OC]", C["oatsimp"], "s", True)]
    ticks, names = [], []
    yy = 0
    for n, ev in ((256, e256), (64, e64)):
        for lab, key, col, mk, filled in lab_b[::-1]:
            v = np.array([p["candidates"][key]["CE_pct"] for p in ev])
            jit = np.linspace(-0.18, 0.18, len(v))
            ax.plot(v, yy + jit, ls="none", marker=mk, ms=3.6, mfc=col, mec=col)
            ax.plot([np.median(v)] * 2, [yy - 0.3, yy + 0.3], color="black", lw=1.1)
            ticks.append(yy)
            names.append(f"Ours, {n}²\n(150 iterations)" if key == "ours[gpu]" else f"{lab}, {n}²")
            rows += [[f"b {n}", lab, f"{t:.4f}"] for t in v]
            yy += 1
        yy += 0.6
    ax.axvline(0, color=C["grey"], lw=0.6)
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xlim(-12, 30)
    ax.set_xticks([-10, -1, 0, 1, 10])
    ax.set_xticklabels(["−10", "−1", "0", "1", "10"])
    ax.set_yticks(ticks)
    ax.set_yticklabels(names)
    ax.set_xlabel("Compliance error (%)")
    fig.text(ax.get_position().x0 - 0.01, 0.975, "b", fontsize=8, fontweight="bold", va="top", ha="right")
    # c: time to OAT's quality. The axis stops at +100 percentage points; the few earlier budgets above it (one curve
    # at 64²) are drawn at the edge as open triangles, so the match region around zero keeps its height.
    ytop = 100.0
    for j, n in enumerate((64, 256)):
        ax = fig.add_subplot(gs[1, j])
        rows_c = list(csv.DictReader((mf.FD / f"ttq_curves_n{n}_gpu.csv").open(encoding="utf-8")))
        pids = sorted({int(r["problem_id"]) for r in rows_c})
        t_oat = np.median([v["time_s"] for v in st[f"OAT inference {n}"]["per_problem"].values()])
        for pid in pids:
            rr = sorted((r for r in rows_c if int(r["problem_id"]) == pid), key=lambda r: int(r["iters"]))
            t = np.array([float(r["wall_incl_setup_s"]) for r in rr])
            dce = np.array([float(r["CE_pct"]) - float(r["CE_OAT_pct"]) for r in rr])
            cap = max(float(rr[0]["vf_target"]), float(rr[0]["vf_OAT"]))
            ok = np.array([float(r["vf_thresholded"]) <= cap for r in rr])
            off = dce > ytop
            dcl = np.minimum(dce, ytop)
            ax.plot(t, dcl, color=C["gpu"], lw=0.8)
            ax.plot(t[ok & ~off], dcl[ok & ~off], ls="none", marker="o", ms=3.2, mfc=C["gpu"], mec=C["gpu"])
            ax.plot(t[~ok & ~off], dcl[~ok & ~off], ls="none", marker="o", ms=3.2, mfc="white", mec=C["gpu"], mew=0.8)
            ax.plot(t[off], dcl[off], ls="none", marker="^", ms=3.6, mfc="white", mec=C["gpu"], mew=0.8, clip_on=False)
            # problem number at the curve's last budget, as listed per problem in Online Resource 2; three labels move
            # off the zero line or away from a neighbouring curve's end
            dx, dy, ha, va = LABEL_AT.get(pid, (3, 0, "left", "center"))
            ax.annotate(str(pid), (t[-1], dcl[-1]), xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                        fontsize=6, color="0.3", annotation_clip=False)
            rows += [[f"c {n}", pid, r["iters"], r["wall_incl_setup_s"], f"{dd:.4f}", int(o)] for r, dd, o in zip(rr, dce, ok)]
        ax.axhline(0, color=C["grey"], lw=0.6)
        ax.axvline(t_oat, color=C["oat"], lw=0.9, ls=(0, (3, 1.5)))
        ax.set_xscale("log")
        ax.set_yscale("symlog", linthresh=1)
        ax.set_ylim(-20, ytop)
        yt = [-10, -1, 0, 1, 10, 100]
        ax.set_yticks(yt)
        ax.set_yticklabels([f"{v:g}".replace("-", "−") for v in yt] if j == 0 else [])
        lo, hi = ax.get_xlim()
        xt = [v for v in (0.1, 0.2, 0.5, 1, 2, 5, 10, 20) if lo <= v <= hi]
        ax.set_xticks(xt)
        ax.set_xticklabels([f"{v:g}" for v in xt])
        ax.xaxis.set_minor_formatter(mticker.NullFormatter())
        ax.set_xlabel("Our time incl. setup (s)")
        ax.text(0.97, 0.97, f"{n}²", transform=ax.transAxes, ha="right", va="top", fontsize=8, fontweight="bold")
        if j == 0:
            ax.set_ylabel("Our CE minus OAT's CE\n(percentage points)")
    fig.text(0.01, 0.47, "c", fontsize=8, fontweight="bold", va="top")
    ax = fig.add_subplot(gs[1, 2])
    ax.axis("off")
    ax.plot([], [], ls="-", marker="o", ms=3.2, color=C["gpu"], label="budget meets the\nvolume condition")
    ax.plot([], [], ls="-", marker="o", ms=3.2, mfc="white", mec=C["gpu"], color=C["gpu"],
            label="budget uses more\nmaterial than OAT\nor the target")
    ax.plot([], [], ls="none", marker="^", ms=3.6, mfc="white", mec=C["gpu"], mew=0.8,
            label="above 100 points,\ndrawn at the edge")
    ax.plot([], [], ls=(0, (3, 1.5)), color=C["oat"], label="OAT inference\ntime (median of 5)")
    ax.legend(loc="center left", handlelength=2.2, labelspacing=1.0, bbox_to_anchor=(0.02, 0.5))
    same_as_v4(rows, ["panel", "series_or_problem", "value_or_iters", "time_s", "delta_ce", "volume_ok"], "fig3_oat")
    for out in OUTS:
        fig.savefig(out, metadata={"CreationDate": None})
        print("wrote", out)
    plt.close(fig)


if __name__ == "__main__":
    main()
