"""Fig. 6: HGTO and SIMP-OC on the same workstation: time against mesh size (a), time ratios (b) and the final
960x320 designs (c).

    python v6/smo/make_fig6.py

Evidence (read-only): evidence/hgto_retest.json and the designs in retest/runs/hgto/. Drawn as fig5_hgto in
v4/manuscript/figures/make_figures.py, which is imported for its house style and loaders without writing into v4/.
Changes from v4: panel b labels 0.1 to 10 and keys its filled (full run) and open (matched quality) diamonds, and the two designs in panel c sit
side by side across the full width. The plotted values are checked against v4's figures/data/fig5_hgto.csv.
Writes fig6_hgto.pdf into smo/figures/ and arxiv/figures/.
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

OUTS = [HERE / "figures" / "fig6_hgto.pdf", HERE.parent / "arxiv" / "figures" / "fig6_hgto.pdf"]
C = mf.C
XLIM_B = (0.1, 15)


def same_as_v4(rows, header, name):
    """The plotted values must equal the ones v4 wrote, so the redraw cannot move a mark."""
    buf = io.StringIO(newline="")
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    if buf.getvalue() != (mf.DATA / f"{name}.csv").read_bytes().decode("utf-8"):
        raise SystemExit(f"plotted values differ from v4 figures/data/{name}.csv")


def main():
    h = mf.load("hgto_retest.json")["configs"]
    fig = plt.figure(figsize=(mf.W2, 96 * mf.MM))
    # panels a and b keep v4's geometry; panel c gets its own row across the full width
    gs = fig.add_gridspec(1, 2, left=0.075, right=0.985, bottom=0.486, top=0.965, wspace=0.56)
    row_c = fig.add_gridspec(1, 2, left=0.075, right=0.985, bottom=0.06, top=0.345, wspace=0.08)
    cant = ["cantilever_120x40", "cantilever_240x80", "cantilever_480x160", "cantilever_960x320"]
    ne = [4800, 19200, 76800, 307200]
    meth = [("hgto_gpu", "HGTO (GPU)", C["hgto"], "o", "-"), ("oc2", "SIMP–OC, 2 threads", C["oc2"], "s", "-"),
            ("oc6", "SIMP–OC, 6 threads", C["oc6"], "^", (0, (3, 1.5))), ("ours", "SIMP–OC, GPU port", C["gpu"], "D", "-")]
    ax = fig.add_subplot(gs[0, 0])
    rows = []
    for key, lab, col, mk, ls in meth:
        v = [h[c]["measured"][key]["wall_s_median"] for c in cant]
        ax.plot(ne, v, ls=ls, marker=mk, ms=3.6, color=col, label=lab, lw=1.0)
        rows += [["a", c, key, f"{t:.4f}"] for c, t in zip(cant, v)]
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Design elements (cantilever, 120×40 to 960×320)")
    ax.set_ylabel("Wall time to convergence (s)")
    ax.legend(loc="upper left", handlelength=2.4)
    mf.letter(ax, "a", x=-0.12)
    ax = fig.add_subplot(gs[0, 1])
    order = ["cantilever_120x40", "half_mbb", "inclined_cantilever", "cantilever_240x80", "cantilever_480x160",
             "cantilever_960x320"]
    names = ["Cantilever 120×40", "Half MBB 120×40", "Inclined load 120×40", "Cantilever 240×80",
             "Cantilever 480×160", "Cantilever 960×320"]
    shown = []
    for i, cfg in enumerate(order):
        y = len(order) - 1 - i
        for dy, (key, lab, col, mk, ls) in zip((0.22, 0.0, -0.22), meth[1:]):
            r = h[cfg]["ratios_vs_hgto_gpu"][key]
            ax.plot([r], [y + dy], marker=mk, ms=3.8, color=col, ls="none")
            rows.append(["b", cfg, key, f"{r:.4f}"])
            shown.append(r)
        rq = h[cfg]["matched_quality_ours"]["ratio_vs_hgto_gpu"]
        ax.plot([rq], [y - 0.22], marker="D", ms=3.8, mfc="white", mec=C["gpu"], mew=0.8, ls="none")
        rows.append(["b", cfg, "ours_matched_quality", f"{rq:.4f}"])
        shown.append(rq)
    if not (XLIM_B[0] < min(shown) and max(shown) < XLIM_B[1]):
        raise SystemExit(f"panel b range {min(shown):.3g}-{max(shown):.3g} falls outside the axis {XLIM_B}")
    ax.axvline(1, color=C["grey"], lw=0.6, ls=(0, (1, 1.5)))
    ax.set_xscale("log")
    ax.set_xlim(*XLIM_B)
    xt = [0.1, 0.2, 0.5, 1, 2, 5, 10]
    ax.set_xticks(xt)
    ax.set_xticklabels([f"{v:g}" for v in xt])
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(names[::-1])
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.set_xlabel("Baseline time ÷ HGTO time")
    # key for the GPU port's two ratios; the other markers are keyed in panel a
    ax.plot([], [], ls="none", marker="D", ms=3.8, color=C["gpu"], label="full run")
    ax.plot([], [], ls="none", marker="D", ms=3.8, mfc="white", mec=C["gpu"], mew=0.8, label="matched quality")
    ax.legend(loc="upper right", handlelength=1.0, handletextpad=0.4, borderaxespad=0.2)
    mf.letter(ax, "b", x=-0.55)
    # c: the two designs side by side
    for j, (key, lab) in enumerate((("hgto_gpu", "HGTO"), ("ours", "Our GPU port"))):
        ax = fig.add_subplot(row_c[0, j])
        rho = np.load(mf.RUNS / "hgto" / key / "cantilever_960x320" / "r1" / "rho.npy").reshape(320, 960)
        ax.imshow(rho, cmap="Greys", vmin=0, vmax=1, interpolation="nearest")
        ax.set_xticks([])
        ax.set_yticks([])
        comp = h["cantilever_960x320"]["measured"][key]["compliance"]
        ax.set_xlabel(f"{lab}: compliance {comp:.2f}", fontsize=8, labelpad=2)
        rows.append(["c", "cantilever_960x320", key, f"{comp:.6f}"])
        if j == 0:
            mf.letter(ax, "c", x=-0.02)
    same_as_v4(rows, ["panel", "config", "method", "value"], "fig5_hgto")
    for out in OUTS:
        fig.savefig(out, metadata={"CreationDate": None})
        print("wrote", out)
    plt.close(fig)


if __name__ == "__main__":
    main()
