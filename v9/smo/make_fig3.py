"""Fig. 3: speed-up at the comparison levels of Fig. 2, for OAT and HGTO (a) and the census claims (b).

    python v6/smo/make_fig3.py

Evidence (read-only): v4/evidence/decomposition_v4.json, the registered numbers (evidence/numbers.json,
v3/evidence/numbers_v3.json, v4/evidence/numbers_v4.json) and the census summaries in v3/runs/P00610 and P00183.
Drawn as fig2_decomposition in v4/manuscript/figures/make_figures.py, which is imported for its house style and
loaders without writing into v4/. Changes from v4: the level names and hardware labels are those of Fig. 2, panel b
draws the census methods in black and grey (blue, vermilion and green keep one meaning across the paper), and both
axes label powers of ten. Since 2026-09-29 the OAT 256² pre-registered match has its own solid segment and legend
entry, like the post hoc volume-condition match. The plotted values are checked against v4's
figures/data/fig2_decomposition.csv.
Writes fig3_decomposition.pdf into smo/figures/ and arxiv/figures/.
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

OUTS = [HERE / "figures" / "fig3_decomposition.pdf", HERE.parent / "arxiv" / "figures" / "fig3_decomposition.pdf"]
C, BLACK = mf.C, "#000000"
plt.rcParams.update({"mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic"})


def same_as_v4(rows, header, name):
    """The plotted values must equal the ones v4 wrote, so the redraw cannot move a mark."""
    buf = io.StringIO(newline="")
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    legacy = (mf.DATA / f"{name}.csv").read_bytes().decode("utf-8").replace('Phase-field CNN steps', 'Phase-field CNN')
    if buf.getvalue() != legacy:
        raise SystemExit(f"plotted values differ from v4 figures/data/{name}.csv")
    data = HERE / 'figures' / 'data'
    data.mkdir(exist_ok=True)
    (data / 'fig3_decomposition.csv').write_bytes(buf.getvalue().encode('utf-8'))


def log_axis(ax, ticks):
    ax.set_yticks(ticks)
    ax.yaxis.set_major_formatter(mticker.LogFormatterSciNotation())
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())


def main():
    x4 = mf.load("decomposition_v4.json", mf.EV4)
    reg = mf.registry()
    d = x4["decomposition"]
    pre = x4["preregistered_ratio_256"]
    fig = plt.figure(figsize=(mf.W2, 92 * mf.MM))
    gs = fig.add_gridspec(1, 2, left=0.085, right=0.985, bottom=0.36, top=0.86, wspace=0.32, width_ratios=[1, 0.92])
    ax = fig.add_subplot(gs[0, 0])
    style = {"OAT 256": (C["oat"], "o", "OAT, 256², volume-condition rule"), "OAT 64": (C["oat"], "s", "OAT, 64²"),
             "HGTO 480x160": (C["hgto"], "v", "HGTO, 480×160"), "HGTO 960x320": (C["hgto"], "^", "HGTO, 960×320")}
    # Texts are the registered ones, so the figure and the manuscript cannot drift apart.
    left_txt = {"OAT 256": reg["N016"]["text"], "OAT 64": reg["N019"]["text"], "HGTO 480x160": reg["N095"]["text"],
                "HGTO 960x320": reg["N096"]["text"]}
    right_txt = {"OAT 256": reg["N018"]["text"], "OAT 64": reg["N039"]["text"], "HGTO 480x160": reg["N099"]["text"],
                 "HGTO 960x320": reg["N100"]["text"]}
    xs = [0, 1, 2, 3]
    rows = []
    for k, (col, mk, lab) in style.items():
        v = d[k]
        ys = [v["reported"], v["own_code"], v["strong"], v["matched"]]
        ax.plot(xs[:2], ys[:2], ls=(0, (2, 2)), color=col, lw=0.9)
        ax.plot(xs[1:], ys[1:], ls="-", color=col, lw=1.1)
        ax.plot(xs, ys, ls="none", marker=mk, ms=4.2, mfc=col, mec="white", mew=0.5, color=col,
                label=f"{lab} ({left_txt[k]} → {right_txt[k]})")
        rows.append([k] + ys)
    # The pre-registered match gets the same solid segment from the efficient solve as the post hoc rule (2026-09-29
    # review: equal visual status for the two matching rules); only the open marker tells them apart.
    ax.plot([2, 3], [d["OAT 256"]["strong"], pre], ls="-", color=C["oat"], lw=1.1)
    ax.plot([3], [pre], marker="o", ms=4.2, mfc="white", mec=C["oat"], mew=0.9, ls="none",
            label=f"OAT, 256², pre-registered rule ({left_txt['OAT 256']} → {reg['N101']['text']})")
    rows.append(["OAT 256 pre-registered rule", "", "", "", pre])
    ax.axhline(1, color=C["grey"], lw=0.6, ls=(0, (1, 1.5)))
    ax.text(-0.3, 1.1, "equal speed", fontsize=8, color=C["grey"], ha="left", va="bottom")
    ax.set_yscale("log")
    ax.set_ylim(0.1, 300)
    ax.set_xlim(-0.35, 3.25)
    ax.set_xticks(xs)
    # Symbol first, then the name, as in Fig. 2
    ax.set_xticklabels([r"$S_{\mathrm{pub}}$" + "\nPublished", r"$S_1$" + "\nAuthors'\ncode",
                        r"$S_2$" + "\nEfficient\nsolve", r"$S_3$" + "\nMatched\nquality"], fontsize=8)
    ax.annotate("", xy=(0.75, 480), xytext=(3.2, 480), xycoords="data", annotation_clip=False,
                arrowprops=dict(arrowstyle="-", lw=0.6, color="black"))
    ax.text(1.97, 520, "our workstation", fontsize=8, ha="center", va="bottom", clip_on=False)
    ax.text(0, 520, "article's hardware", fontsize=8, ha="center", va="bottom", clip_on=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.255), ncol=1, handletextpad=0.4, borderaxespad=0.0)
    ax.set_ylabel("Learning-based speed-up (×)")
    log_axis(ax, [0.1, 1, 10, 100])
    ax.tick_params(axis="x", length=0)
    mf.letter(ax, "a", x=-0.13, y=1.06)

    # b: census quality checks; phase-field uses convergence endpoints with lower learned compliance.
    ax = fig.add_subplot(gs[0, 1])
    s610 = mf.load("summary.json", mf.RUNS3 / "P00610")["per_ratio"].values()
    s183 = mf.load("summary.json", mf.RUNS3 / "P00183")["L1"].values()
    census = [
        ("Conductivity CNN", BLACK, "o", True,
         [v["published_factor_cpu_nht_vs_gpu_cnn"] for v in s610], [v["L1_factor_tdma_over_cnn"] for v in s610],
         [v["L2_factor_direct_over_cnn"] for v in s610]),
        ("VoroTO", C["grey"], "s", True, reg["N307"]["value"], reg["N308"]["value"], [1 / reg["N309"]["value"]]),
        ("One-shot generator", C["grey"], "D", False, [1e4], [a["factor_full"] for a in s183],
         [a["factor_matched"] for a in s183]),
        ("Phase-field CNN", BLACK, "^", True, [reg["N315"]["value"]], [reg["N316"]["value"]],
         [reg["N316"]["value"]]),
    ]
    for k, (lab, col, mk, filled, *cols) in enumerate(census):
        med = [float(np.exp(np.median(np.log(v)))) for v in cols]   # median on the log scale
        dx = (k - 1.5) * 0.07
        ax.plot(np.arange(3) + dx, med, color=col, lw=1.0, ls="-" if filled else (0, (3, 1.5)))
        for x, v in enumerate(cols):
            ax.plot([x + dx] * len(v), v, ls="none", marker=mk, ms=3.4, mfc=col if filled else "white", mec=col,
                    mew=0.8, alpha=0.9)
            rows += [["b", lab, x, f"{t:.6g}", ""] for t in v]
        ax.plot([], [], color=col, marker=mk, ms=3.4, mfc=col if filled else "white", mec=col,
                ls="-" if filled else (0, (3, 1.5)), label=lab + ("" if filled else " (article's own code)"))
    ax.axhline(1, color=C["grey"], lw=0.6, ls=(0, (1, 1.5)))
    ax.set_yscale("log")
    ax.set_ylim(0.1, 1e5)
    ax.set_xlim(-0.35, 2.35)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["Published", "Authors'\ncode", "Quality\nchecked"], fontsize=8)
    log_axis(ax, [0.1, 1, 10, 100, 1e3, 1e4, 1e5])
    ax.set_ylabel("Speed-up (×)")
    ax.tick_params(axis="x", length=0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.255), ncol=1, handletextpad=0.4, borderaxespad=0.0)
    mf.letter(ax, "b", x=-0.13, y=1.06)
    same_as_v4(rows, ["case", "reported_or_x", "own_code_or_case", "strong", "matched"], "fig2_decomposition")
    for out in OUTS:
        fig.savefig(out, metadata={"CreationDate": None})
        print("wrote", out)
    plt.close(fig)


if __name__ == "__main__":
    main()
