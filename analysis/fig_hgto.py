"""Extended Data figure for the HGTO re-test (target P00512): ED10.

    python -m analysis.fig_hgto          # after analysis.hgto_summary (reads evidence/hgto_retest.json)

(a) Converged wall time against design elements for the cantilever series (120x40 to 960x320): HGTO on the GPU, the
    authors' SIMP-OC with two and six threads, and our GPU port of the same SIMP-OC (medians of the timed runs; the
    target's own timing scope). The article's times (other hardware) are hollow markers in the same hue, labelled.
(b) Wall time of each SIMP-OC variant divided by HGTO's, same machine; the dashed line marks parity.
Palette: dataviz reference categorical slots 1-4 (adjacent pairlist; slot 4 is direct-labelled per the relief rule).
Writes figures/ed10_hgto.png and .svg, and figures/data/ed10_hgto.csv.
"""
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from analysis.fig_extended import INK, INK2, SURFACE, save, style  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERIES = [("hgto_gpu", "HGTO (GPU)", "#2a78d6", "o"), ("oc2", "SIMP–OC, 2 threads (as released)", "#eb6834", "s"),
          ("oc6", "SIMP–OC, 6 threads", "#1baf7a", "^"), ("ours", "SIMP–OC, GPU port", "#eda100", "D")]
DY = {"oc2": 7, "oc6": -7}                      # end-label offsets (points) that keep close labels apart
SIZES = [("cantilever_120x40", 4800), ("cantilever_240x80", 19200), ("cantilever_480x160", 76800),
         ("cantilever_960x320", 307200)]


def main():
    data = json.loads((ROOT / "evidence" / "hgto_retest.json").read_text(encoding="utf-8"))["configs"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.0, 4.2), facecolor=SURFACE)
    rows = []
    for key, label, color, marker in SERIES:
        xs = [n for _, n in SIZES]
        ys = [data[c]["measured"][key]["wall_s_median"] for c, _ in SIZES]
        a.plot(xs, ys, color=color, marker=marker, markersize=6, linewidth=2, label=label)
        a.annotate(label.split(",")[0] if key == "hgto_gpu" else label.replace("SIMP–OC, ", "OC "),
                   (xs[-1], ys[-1]), xytext=(6, DY.get(key, 0)), textcoords="offset points", va="center", fontsize=7.5,
                   color=INK)
        for (c, n), y in zip(SIZES, ys):
            rows.append({"config": c, "elements": n, "method": key, "wall_s_median": y})
        if key != "hgto_gpu":
            r = [data[c]["measured"][key]["wall_s_median"] / data[c]["measured"]["hgto_gpu"]["wall_s_median"]
                 for c, _ in SIZES]
            b.plot(xs, r, color=color, marker=marker, markersize=6, linewidth=2, label=label)
            b.annotate(label.replace("SIMP–OC, ", "OC "), (xs[-1], r[-1]), xytext=(6, DY.get(key, 0)), textcoords="offset points",
                       va="center", fontsize=7.5, color=INK)
    for key, pub, color, marker in (("hgto_gpu", "hgto_s", "#2a78d6", "o"), ("oc2", "oc_s", "#eb6834", "s")):
        xs = [n for _, n in SIZES]
        ys = [data[c]["published"][pub] for c, _ in SIZES]
        a.plot(xs, ys, linestyle="none", marker=marker, markersize=7, markerfacecolor="none", markeredgecolor=color,
               markeredgewidth=1.4, label=f"article ({'HGTO' if key == 'hgto_gpu' else 'SIMP–OC, 2 threads'}; "
                                          "RTX 6000 Ada, Threadripper)")
    a.set_xscale("log")
    a.set_yscale("log")
    a.set_xlabel("design elements (cantilever, 120×40 to 960×320)", color=INK2, fontsize=8)
    a.set_ylabel("wall time to convergence (s)", color=INK2, fontsize=8)
    a.set_title("a  Converged wall time, same machine", loc="left", fontsize=9, color=INK)
    style(a)
    a.legend(fontsize=6.8, frameon=False, loc="upper left")
    b.axhline(1.0, color=INK2, linestyle="--", linewidth=1)
    b.text(1.5e6, 0.96, "parity with HGTO", fontsize=7, color=INK2, va="top", ha="right")
    b.set_xscale("log")
    b.set_yscale("log")
    b.set_xlabel("design elements", color=INK2, fontsize=8)
    b.set_ylabel("SIMP–OC time ÷ HGTO time", color=INK2, fontsize=8)
    b.set_title("b  HGTO's speed-up depends on the baseline", loc="left", fontsize=9, color=INK)
    style(b)
    for ax in (a, b):
        ax.set_xlim(3000, 1.6e6)
    fig.tight_layout()
    save(fig, "ed10_hgto", rows)


if __name__ == "__main__":
    main()
