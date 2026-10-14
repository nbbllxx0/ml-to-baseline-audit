"""Fig. 8: model-coded availability and reporting indicators, with 95 % confidence intervals.

    python v6/smo/make_fig8.py

Evidence (read-only): evidence/reporting.json. Drawn as fig7_reporting in v4/manuscript/figures/make_figures.py,
which is imported for its house style and loaders without writing into v4/. Change from v4: the two strata are drawn
in black and grey, so blue and vermilion keep one meaning (our solver, OAT) across the paper. The plotted values are
checked against v4's figures/data/fig7_reporting.csv.
Writes fig8_reporting.pdf into smo/figures/ and arxiv/figures/.
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

OUTS = [HERE / "figures" / "fig8_reporting.pdf", HERE.parent / "arxiv" / "figures" / "fig8_reporting.pdf"]
ALL, SPEED = "#000000", mf.C["grey"]     # strata: all 57 included articles; the 28 speed claims


def same_as_v4(rows, header, name):
    """The plotted values must equal the ones v4 wrote, so the redraw cannot move a mark."""
    buf = io.StringIO(newline="")
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    if buf.getvalue() != (mf.DATA / f"{name}.csv").read_bytes().decode("utf-8"):
        raise SystemExit(f"plotted values differ from v4 figures/data/{name}.csv")


def main():
    rep = mf.load("reporting.json")["indicators"]
    items = [("code_available", "Code linked"), ("data_available", "Data linked"),
             ("seeds_or_variance", "Seeds or variance"), ("failure_rate_reported", "Failure rate"),
             ("ood_test", "Out-of-distribution test"), ("hardware_per_method_stated", "Hardware per method"),
             ("runtimes_all_cases", "Only selected runtimes"), ("timing_protocol_stated", "Full timing protocol")]
    fig, ax = plt.subplots(figsize=(mf.W1, 70 * mf.MM))
    fig.subplots_adjust(left=0.4, right=0.84, bottom=0.27, top=0.97)
    rows = []
    for i, (k, lab) in enumerate(items):
        d = rep[k]
        y = len(items) - 1 - i
        col = ALL if d["n"] == 57 else SPEED
        mk = "o" if d["n"] == 57 else "s"
        ax.plot([d["ci95"][0], d["ci95"][1]], [y, y], color=col, lw=1.0)
        ax.plot([d["share"]], [y], marker=mk, ms=4, color=col, clip_on=False)   # a share of 0 stays whole
        ax.text(1.03, y, f"{d['k']}/{d['n']}", va="center", fontsize=8, transform=ax.get_yaxis_transform())
        rows.append([lab, d["k"], d["n"], f"{d['share']:.4f}", f"{d['ci95'][0]:.4f}", f"{d['ci95'][1]:.4f}"])
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, len(items) - 0.4)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([i[1] for i in items][::-1])
    ax.set_xlabel("Share of articles (95 % CI)")
    ax.set_xticks([0, 0.5, 1])
    ax.set_xticklabels(["0", "0.5", "1"])
    ax.plot([], [], marker="o", ms=3.5, ls="-", color=ALL, label="of 57 included")
    ax.plot([], [], marker="s", ms=3.5, ls="-", color=SPEED, label="of 28 speed claims")
    ax.legend(loc="upper center", bbox_to_anchor=(0.3, -0.24), ncol=2, handlelength=1.4, columnspacing=1.0)
    same_as_v4(rows, ["indicator", "k", "n", "share", "ci_low", "ci_high"], "fig7_reporting")
    for out in OUTS:
        fig.savefig(out, metadata={"CreationDate": None})
        print("wrote", out)
    plt.close(fig)


if __name__ == "__main__":
    main()
