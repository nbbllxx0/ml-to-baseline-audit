"""Fig. 5: three OAT test problems at 256², with each problem's supports and load drawn on the dataset reference design.

    python v6/smo/make_fig5.py

Evidence (read-only): OAT's evaluator scores (evidence/oat_eval_n256.json), our time-to-quality curves
(figures/data/ttq_curves_n256_gpu.csv) and designs, OAT's stored samples (retest/runs/), and the NITO_test rows
(retest/targets/hf/OpenTO_data/NITO_test_cache.json: supports, loads, reference design). House style comes from
v4/manuscript/figures/make_figures.py, which is imported without writing into v4/.
Writes fig5_designs.pdf into smo/figures/ and arxiv/figures/.
"""
import base64
import csv
import io
import json
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "v4" / "manuscript" / "figures"))
import make_figures as mf  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

OUTS = [HERE / "figures" / "fig5_designs.pdf", HERE.parent / "arxiv" / "figures" / "fig5_designs.pdf"]
BLUE, VERM = "#0072B2", "#D55E00"
N = 256
PROBS = [(1961, "Matched after 15 iterations"),
         (1015, "Matched only under the\npre-registered rule"),
         (1676, "Not matched within\n150 iterations")]
HEADS = ["Problem and\nreference design", "OAT sample", "Classical: first budget\nwith CE at most OAT's",
         "Classical:\n150 iterations"]


def draw_problem(ax, row):
    """Supports (filled square: both directions fixed; open circle: one direction) and the point load (arrow with
    its head on the loaded node). A node at normalised (x, y) sits at image (row, col) = (x, y) * N - 0.5."""
    many = len(row["boundary conditions"]) > 20      # an edge support: draw it thin
    for x, y, fx, fy in row["boundary conditions"]:
        r, c = x * N - 0.5, y * N - 0.5
        both = fx > 0.5 and fy > 0.5
        size = 1.2 if (many and not both) else (3.2 if both else 2.6)
        ax.plot(c, r, marker="s" if both else "o", ms=size, mfc=BLUE if both else "white", mec=BLUE, mew=0.8,
                clip_on=False, zorder=4)
    for x, y, fx, fy in row["loads"]:
        r, c, L = x * N - 0.5, y * N - 0.5, 55.0
        ax.annotate("", xy=(c, r), xytext=(c - L * fy, r - L * fx), zorder=5, annotation_clip=False,
                    arrowprops=dict(arrowstyle="-|>", color=VERM, lw=1.2, mutation_scale=7))


def main():
    rows_ds = json.loads((ROOT / "retest/targets/hf/OpenTO_data/NITO_test_cache.json").read_text(encoding="utf-8"))
    ev = {p["problem_id"]: p for p in mf.load("oat_eval_n256.json")}
    curves = list(csv.DictReader((mf.FD / "ttq_curves_n256_gpu.csv").open(encoding="utf-8")))
    oat_dir = mf.RUNS / "20260924T170945Z_oat_infer_n256"
    ttq_dir = mf.RUNS / "20260924T171052Z_ttq_gpu_n256"
    fig, axes = plt.subplots(len(PROBS), 4, figsize=(mf.W2, 138 * mf.MM))
    fig.subplots_adjust(left=0.14, right=0.99, bottom=0.05, top=0.92, wspace=0.10, hspace=0.34)
    for i, (pid, outcome) in enumerate(PROBS):
        e, ds = ev[pid], rows_ds[pid]
        ref = np.array(Image.open(io.BytesIO(base64.b64decode(ds["topology"]["b64"])))).astype(float) > 0.5
        rr = sorted((r for r in curves if int(r["problem_id"]) == pid), key=lambda r: int(r["iters"]))
        ce_oat = e["candidates"]["OAT"]["CE_pct"]
        cap = max(e["vf_target"], e["candidates"]["OAT"]["vf_thresholded"])
        first = next((r for r in rr if float(r["CE_pct"]) <= ce_oat), None)
        cells = [("ref", ref, None, ref.mean(), ""),
                 ("des", np.load(oat_dir / f"generated_{pid}.npz")["x"], ce_oat,
                  e["candidates"]["OAT"]["vf_thresholded"], ""),
                 None,
                 ("des", np.load(ttq_dir / f"design_{pid}_it150.npz")["x_pyedge"].reshape(N, N),
                  e["candidates"]["ours[gpu]"]["CE_pct"], e["candidates"]["ours[gpu]"]["vf_thresholded"], "")]
        if first is not None:
            k, vf = int(first["iters"]), float(first["vf_thresholded"])
            note = f"{k} iterations" + ("" if vf <= cap else "; volume above limit")
            cells[2] = ("des", np.load(ttq_dir / f"design_{pid}_it{k:03d}.npz")["x_pyedge"].reshape(N, N),
                        float(first["CE_pct"]), vf, note)
        for j, cell in enumerate(cells):
            ax = axes[i, j]
            ax.set_xticks([])
            ax.set_yticks([])
            for s in ax.spines.values():
                s.set_visible(True)
                s.set_linewidth(0.5)
            ax.set_xlim(-0.5, N - 0.5)
            ax.set_ylim(N - 0.5, -0.5)
            ax.set_aspect("equal")
            if i == 0:
                ax.set_title(HEADS[j], fontsize=8, pad=4)
            if cell is None:
                ax.set_facecolor("#F2F2F2")
                ax.text(0.5, 0.5, "no budget reached\nOAT's CE", ha="center", va="center", fontsize=8,
                        transform=ax.transAxes)
                continue
            kind, img, ce, vf, note = cell
            if kind == "ref":
                ax.imshow(np.asarray(img), cmap="Greys", vmin=0, vmax=2.6, interpolation="nearest")
                ax.set_xlim(-0.5, N - 0.5)
                ax.set_ylim(N - 0.5, -0.5)
                draw_problem(ax, ds)
                ax.set_xlabel(f"reference, volume {vf:.3f}", fontsize=8, labelpad=2)
            else:
                ax.imshow(np.asarray(img) > 0.5, cmap="Greys", interpolation="nearest", vmin=0, vmax=1)
                lab = f"CE {ce:+.2f} %, volume {vf:.3f}".replace("-", "−") + (f"\n{note}" if note else "")
                ax.set_xlabel(lab, fontsize=8, labelpad=2)
        axes[i, 0].set_ylabel(f"{outcome}\n(problem {pid}, target {e['vf_target']:.2f})", fontsize=8, labelpad=12)
    for out in OUTS:
        fig.savefig(out)
        print("wrote", out)
    plt.close(fig)


if __name__ == "__main__":
    main()
