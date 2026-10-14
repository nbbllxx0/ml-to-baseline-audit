"""Figures for the v4 manuscript, built at final size from frozen evidence files (v2 script, revised for v4:
Fig. 1 shows the type-and-date removal; Fig. 2 uses the GPU solver as the one strong baseline and adds the census
panel; Fig. 3c clips the off-scale start of one curve; Fig. 4 names budgets in iterations; Fig. 6a uses markers and
adds the PARDISO row at 64²).

    python v4/manuscript/figures/make_figures.py

Journal rules (SMO; writing_kit/JOURNAL_REQUIREMENTS.md J13): width 84 mm (one column) or 174 mm (full width);
Arial lettering at 8 pt; lines at least 0.5 pt; no title inside a figure (captions carry the titles); vector PDF with
embedded TrueType fonts. Each figure also gets a PNG preview and a CSV of the plotted values in figures/data/.
Colours: Okabe-Ito (colour-blind safe), always paired with a marker or line style.
"""
import csv
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[3]
EV = ROOT / "evidence"
EV3 = ROOT / "v3" / "evidence"
EV4 = ROOT / "v4" / "evidence"
RUNS3 = ROOT / "v3" / "runs"
RUNS = ROOT / "retest" / "runs"
FD = ROOT / "figures" / "data"
OUT = pathlib.Path(__file__).resolve().parent
DATA = OUT / "data"
DATA.mkdir(exist_ok=True)

MM = 1 / 25.4
W1, W2 = 84 * MM, 174 * MM
C = {"oat": "#D55E00", "gpu": "#0072B2", "cpu": "#56B4E9", "oatsimp": "#009E73", "hgto": "#CC79A7",
     "oc2": "#E69F00", "oc6": "#000000", "grey": "#707070"}
plt.rcParams.update({
    "font.family": "Arial", "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8, "xtick.labelsize": 8,
    "ytick.labelsize": 8, "legend.fontsize": 8, "axes.linewidth": 0.6, "lines.linewidth": 1.0,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.minor.width": 0.5, "ytick.minor.width": 0.5,
    "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "savefig.dpi": 600,
})

# Plain-language labels for the protocol's reason codes (audit/schema/screening_codes.md).
SCREEN = [("E-SCOPE", "outside scope"), ("E-TYPE", "not a method article"), ("E-DOMAIN", "excluded physics"),
          ("E-NOML", "no learned model"), ("E-OTHER", "other"), ("E-FORWARD", "learned forward prediction only"),
          ("E-NOCLAIM", "no comparative claim"), ("E-MLONLY", "learned comparators only")]
FULLTEXT = [("FT-DUPLICATE", "duplicate version"), ("FT-NOBASELINE", "no classical comparison"),
            ("FT-MLONLY", "learned comparators only"), ("FT-DOMAIN", "excluded physics"),
            ("FT-TYPE", "not a method article"), ("FT-SCOPE", "outside scope"), ("FT-NOML", "no learned model"),
            ("FT-OTHER", "other")]


def load(name, folder=EV):
    return json.loads((folder / name).read_text(encoding="utf-8"))


def registry():
    """All registered numbers (v2, v3 census, v4), so figure labels are the manuscript's texts."""
    reg = load("numbers.json")
    reg.update(load("numbers_v3.json", EV3))
    reg.update(load("numbers_v4.json", EV4))
    return reg


def save(fig, name, rows=None, header=None):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=300)
    plt.close(fig)
    if rows is not None:
        with (DATA / f"{name}.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)
    print("wrote", name)


def letter(ax, s, x=-0.02, y=1.02):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=8, fontweight="bold", ha="right", va="bottom")


# ---------------------------------------------------------------------------------------------------------------
def fig1_flow():
    p, c1, x2 = load("prisma.json"), load("c1_rules.json"), load("v2_extras.json")
    acc = x2["access"]
    fam = p["records_returned_by_family"]
    scr = ", ".join(f"{lab} {p['llm_codes'][k]:,}" for k, lab in SCREEN)
    ft = ", ".join(f"{lab} {c1['excluded_by_code'].get(k, 0)}" for k, lab in FULLTEXT)
    main = [
        f"Records returned: {p['records_returned_total']:,} (arXiv {fam['arxiv']:,}; OpenAlex {fam['openalex']:,};\n"
        f"forward citations {fam['forward']:,}; reference lists {fam['backward']:,})",
        f"Unique after de-duplication: {p['unique_after_dedup']:,}",
        f"Title and abstract screening by a\nlanguage model: {p['llm_includes']:,} included",
        f"Eligible after type and date rules: {p['decision_order_eligible']:,}\nfixed in one seeded random order",
        f"Analysis sample: positions 1–{p['sample_positions']}",
        f"Coded twice, disagreements adjudicated: {p['sample_records_coded']}",
        f"Full text read: {p['sample_full_text']}",
        f"Included: {p['sample_included_full_text']}\nspeed stratum {p['sample_speed_stratum']}; "
        f"quality stratum {p['sample_quality_stratum']}",
    ]
    excl_scr = p["screened_llm"] - p["llm_includes"]
    removed = p["llm_includes"] - p["decision_order_eligible"]
    side = {
        2: f"Excluded: {excl_scr:,} ({scr})\nBlind re-screen of 188 excluded: 17 flagged for full text",
        3: f"Removed by the type and date rules: {removed}",
        4: f"Skipped as paywalled (OpenAlex): {acc['paywalled_skipped']}",
        5: f"No readable full text: {acc['abstract_only'] + acc['no_access']} "
           f"(abstract only {acc['abstract_only']}; blocked {acc['no_access']})",
        6: f"Excluded at full text: {p['sample_excluded_full_text']} ({ft})",
    }
    re_ = load("rescreen.json")
    assert re_["n_sampled_excludes"] == 188 and re_["rescreen_includes"] == 17
    import textwrap
    fig = plt.figure(figsize=(W2, 100 * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 174)
    ax.set_ylim(0, 100)
    ax.axis("off")
    bw, bh, gap, top, x0 = 80, 8.6, 3.4, 98.5, 1
    rows = []
    for i, t in enumerate(main):
        y = top - i * (bh + gap) - bh
        ax.add_patch(FancyBboxPatch((x0, y), bw, bh, boxstyle="round,pad=0,rounding_size=1.2", lw=0.6,
                                    ec="black", fc="#F2F2F2"))
        ax.text(x0 + bw / 2, y + bh / 2, t, ha="center", va="center", fontsize=8, linespacing=1.15)
        if i < len(main) - 1:
            ax.annotate("", xy=(x0 + bw / 2, y - gap + 0.2), xytext=(x0 + bw / 2, y - 0.2),
                        arrowprops=dict(arrowstyle="-|>", lw=0.6, color="black", mutation_scale=6))
        rows.append(["main", i, t.replace("\n", " | ")])
        if i in side:
            ax.annotate("", xy=(x0 + bw + 3.5, y + bh / 2), xytext=(x0 + bw, y + bh / 2),
                        arrowprops=dict(arrowstyle="-|>", lw=0.6, color="black", mutation_scale=6))
            txt = "\n".join(textwrap.fill(par, 60) for par in side[i].split("\n"))
            ax.text(x0 + bw + 4.5, y + bh / 2, txt, ha="left", va="center", fontsize=8, linespacing=1.15)
            rows.append(["side", i, side[i].replace("\n", " | ")])
    save(fig, "fig1_flow", rows, ["kind", "box", "text"])


# ---------------------------------------------------------------------------------------------------------------
def fig2_decomposition():
    x4 = load("decomposition_v4.json", EV4)
    reg = registry()
    d = x4["decomposition"]
    pre = x4["preregistered_ratio_256"]
    fig = plt.figure(figsize=(W2, 92 * MM))
    gs = fig.add_gridspec(1, 2, left=0.085, right=0.985, bottom=0.36, top=0.86, wspace=0.32, width_ratios=[1, 0.92])
    ax = fig.add_subplot(gs[0, 0])
    style = {"OAT 256": (C["oat"], "o", "OAT, 256²"), "OAT 64": (C["oat"], "s", "OAT, 64²"),
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
    ax.plot([3], [pre], marker="o", ms=4.2, mfc="white", mec=C["oat"], mew=0.9, ls="none",
            label=f"OAT, 256², pre-registered matching rule ({reg['N101']['text']})")
    rows.append(["OAT 256 pre-registered rule", "", "", "", pre])
    ax.axhline(1, color=C["grey"], lw=0.6, ls=(0, (1, 1.5)))
    ax.text(-0.3, 1.1, "equal speed", fontsize=8, color=C["grey"], ha="left", va="bottom")
    ax.set_yscale("log")
    ax.set_ylim(0.1, 300)
    ax.set_xlim(-0.35, 3.25)
    ax.set_xticks(xs)
    ax.set_xticklabels(["Reported", "Authors'\ncode", "Strong\nbaseline", "Matched\nquality"], fontsize=8)
    ax.annotate("", xy=(0.75, 480), xytext=(3.2, 480), xycoords="data", annotation_clip=False,
                arrowprops=dict(arrowstyle="-", lw=0.6, color="black"))
    ax.text(1.97, 520, "on our machine", fontsize=8, ha="center", va="bottom", clip_on=False)
    ax.text(0, 520, "authors' hardware", fontsize=8, ha="center", va="bottom", clip_on=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=1, handletextpad=0.4, borderaxespad=0.0)
    ax.set_ylabel("Speed-up of the learned method (×)")
    ax.set_yticks([0.1, 1, 10, 100])
    ax.set_yticklabels(["0.1", "1", "10", "100"])
    ax.tick_params(axis="x", length=0)
    letter(ax, "a", x=-0.13, y=1.06)

    # b: census claims with a matched-quality comparison; dots are the article's cases, lines join their medians
    ax = fig.add_subplot(gs[0, 1])
    s610 = load("summary.json", RUNS3 / "P00610")["per_ratio"].values()
    s183 = load("summary.json", RUNS3 / "P00183")["L1"].values()
    census = [
        ("Conductivity CNN", C["gpu"], "o", True,
         [v["published_factor_cpu_nht_vs_gpu_cnn"] for v in s610], [v["L1_factor_tdma_over_cnn"] for v in s610],
         [v["L2_factor_direct_over_cnn"] for v in s610]),
        ("VoroTO", C["oatsimp"], "s", True, reg["N307"]["value"], reg["N308"]["value"], [1 / reg["N309"]["value"]]),
        ("One-shot generator", C["oc2"], "D", False, [1e4], [a["factor_full"] for a in s183],
         [a["factor_matched"] for a in s183]),
        ("Phase-field CNN steps", C["oc6"], "^", True, [reg["N315"]["value"]], [reg["N316"]["value"]],
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
    ax.set_xticklabels(["Published", "Article's\ncomparison,\nour machine", "Matched\nquality"], fontsize=8)
    ax.set_yticks([0.1, 1, 10, 100, 1e3, 1e4, 1e5])
    ax.set_yticklabels(["0.1", "1", "10", "100", "10³", "10⁴", "10⁵"])
    ax.set_ylabel("Speed-up (×)")
    ax.tick_params(axis="x", length=0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=1, handletextpad=0.4, borderaxespad=0.0)
    letter(ax, "b", x=-0.13, y=1.06)
    save(fig, "fig2_decomposition", rows, ["case", "reported_or_x", "own_code_or_case", "strong", "matched"])


# ---------------------------------------------------------------------------------------------------------------
def fig3_oat():
    tt, oat = load("ttq_summary.json"), load("oat_retest_summary.json")
    e256, e64 = load("oat_eval_n256.json"), load("oat_eval_n64.json")
    st = oat["stages"]
    fig = plt.figure(figsize=(W2, 122 * MM))
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
            names.append(f"{lab}, {n}²")
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
        rows_c = list(csv.DictReader((FD / f"ttq_curves_n{n}_gpu.csv").open(encoding="utf-8")))
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
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
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
    save(fig, "fig3_oat", rows, ["panel", "series_or_problem", "value_or_iters", "time_s", "delta_ce", "volume_ok"])


# ---------------------------------------------------------------------------------------------------------------
def fig4_designs():
    ev = {p["problem_id"]: p for p in load("oat_eval_n256.json")}
    rows_c = list(csv.DictReader((FD / "ttq_curves_n256_gpu.csv").open(encoding="utf-8")))
    oat_dir, ttq_dir, simp_dir = RUNS / "20260924T170945Z_oat_infer_n256", RUNS / "20260924T171052Z_ttq_gpu_n256", \
        RUNS / "20260924T165342Z_oat_simp_n256"
    probs = [1961, 1015, 1676]
    fig, axes = plt.subplots(len(probs), 4, figsize=(W2, 142 * MM))
    fig.subplots_adjust(left=0.1, right=0.99, bottom=0.05, top=0.94, wspace=0.08, hspace=0.3)
    heads = ["OAT output", "Ours: first budget with\nCE at most OAT's", "Ours: 150 iterations", "OAT's SIMP (CG):\n150 iterations"]
    rows = []
    for i, pid in enumerate(probs):
        e = ev[pid]
        rr = sorted((r for r in rows_c if int(r["problem_id"]) == pid), key=lambda r: int(r["iters"]))
        ce_oat = e["candidates"]["OAT"]["CE_pct"]
        cap = max(e["vf_target"], e["candidates"]["OAT"]["vf_thresholded"])
        first = next((r for r in rr if float(r["CE_pct"]) <= ce_oat), None)
        cells = [
            (np.load(oat_dir / f"generated_{pid}.npz")["x"], ce_oat, e["candidates"]["OAT"]["vf_thresholded"], ""),
            None,
            (np.load(ttq_dir / f"design_{pid}_it150.npz")["x_pyedge"].reshape(256, 256),
             e["candidates"]["ours[gpu]"]["CE_pct"], e["candidates"]["ours[gpu]"]["vf_thresholded"], ""),
            (np.load(simp_dir / f"design_{pid}_CG_OC.npz")["x"].reshape(256, 256),
             e["candidates"]["OAT-SIMP[CG_OC]"]["CE_pct"], e["candidates"]["OAT-SIMP[CG_OC]"]["vf_thresholded"], ""),
        ]
        if first is not None:
            k = int(first["iters"])
            vf = float(first["vf_thresholded"])
            note = f"{k} iterations" + ("" if vf <= cap else "; volume too high")
            cells[1] = (np.load(ttq_dir / f"design_{pid}_it{k:03d}.npz")["x_pyedge"].reshape(256, 256),
                        float(first["CE_pct"]), vf, note)
        for j, cell in enumerate(cells):
            ax = axes[i, j]
            ax.set_xticks([])
            ax.set_yticks([])
            for s in ax.spines.values():
                s.set_visible(True)
                s.set_linewidth(0.5)
            if i == 0:
                ax.set_title(heads[j], fontsize=8, pad=4)
            if cell is None:
                ax.text(0.5, 0.5, "CE never at or below\nOAT's within 150\niterations", ha="center", va="center",
                        fontsize=8, transform=ax.transAxes)
                ax.set_facecolor("#F2F2F2")
                rows.append([pid, j, "", "", "none"])
                continue
            img, ce, vf, note = cell
            ax.imshow(np.asarray(img) > 0.5, cmap="Greys", interpolation="nearest", vmin=0, vmax=1)
            lab = f"CE {ce:+.2f} %, volume {vf:.3f}".replace("-", "−") + (f"\n{note}" if note else "")
            ax.set_xlabel(lab, fontsize=8, labelpad=2)
            rows.append([pid, j, f"{ce:.4f}", f"{vf:.4f}", note])
        axes[i, 0].set_ylabel(f"Problem {pid}\ntarget volume {e['vf_target']:.2f}", fontsize=8)
    save(fig, "fig4_designs", rows, ["problem", "column", "CE_pct", "volume_thresholded", "note"])


# ---------------------------------------------------------------------------------------------------------------
def fig5_hgto():
    h = load("hgto_retest.json")["configs"]
    fig = plt.figure(figsize=(W2, 96 * MM))
    gs = fig.add_gridspec(2, 2, left=0.075, right=0.985, bottom=0.07, top=0.965, hspace=0.3, wspace=0.56,
                          height_ratios=[1.6, 1])
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
    letter(ax, "a", x=-0.12)
    ax = fig.add_subplot(gs[0, 1])
    order = ["cantilever_120x40", "half_mbb", "inclined_cantilever", "cantilever_240x80", "cantilever_480x160",
             "cantilever_960x320"]
    names = ["Cantilever 120×40", "Half MBB 120×40", "Inclined load 120×40", "Cantilever 240×80",
             "Cantilever 480×160", "Cantilever 960×320"]
    for i, cfg in enumerate(order):
        y = len(order) - 1 - i
        for dy, (key, lab, col, mk, ls) in zip((0.22, 0.0, -0.22), meth[1:]):
            r = h[cfg]["ratios_vs_hgto_gpu"][key]
            ax.plot([r], [y + dy], marker=mk, ms=3.8, color=col, ls="none")
            rows.append(["b", cfg, key, f"{r:.4f}"])
        rq = h[cfg]["matched_quality_ours"]["ratio_vs_hgto_gpu"]
        ax.plot([rq], [y - 0.22], marker="D", ms=3.8, mfc="white", mec=C["gpu"], mew=0.8, ls="none")
        rows.append(["b", cfg, "ours_matched_quality", f"{rq:.4f}"])
    ax.axvline(1, color=C["grey"], lw=0.6, ls=(0, (1, 1.5)))
    ax.set_xscale("log")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(names[::-1])
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.set_xlabel("Baseline time ÷ HGTO time")
    letter(ax, "b", x=-0.55)
    for j, (key, lab) in enumerate((("hgto_gpu", "HGTO"), ("ours", "Our GPU port"))):
        ax = fig.add_subplot(gs[1, j])
        rho = np.load(RUNS / "hgto" / key / "cantilever_960x320" / "r1" / "rho.npy").reshape(320, 960)
        ax.imshow(rho, cmap="Greys", vmin=0, vmax=1, interpolation="nearest")
        ax.set_xticks([])
        ax.set_yticks([])
        comp = h["cantilever_960x320"]["measured"][key]["compliance"]
        ax.set_xlabel(f"{lab}: compliance {comp:.2f}", fontsize=8, labelpad=2)
        rows.append(["c", "cantilever_960x320", key, f"{comp:.6f}"])
        if j == 0:
            letter(ax, "c", x=-0.02)
    save(fig, "fig5_hgto", rows, ["panel", "config", "method", "value"])


# ---------------------------------------------------------------------------------------------------------------
def fig6_breakeven_energy():
    b, en, x2, reg = load("breakeven.json"), load("energy.json"), load("v2_extras.json"), registry()
    fig = plt.figure(figsize=(W2, 72 * MM))
    gs = fig.add_gridspec(1, 2, left=0.33, right=0.97, bottom=0.18, top=0.94, wspace=0.75, width_ratios=[1.35, 1])

    def row(scen, size):
        # one GPU and one PARDISO row share a scenario label; our GPU baseline is the one plotted
        hits = [r for r in b["rows"] if r["size"] == size and r["scenario"].startswith(scen)
                and ("gpu" in r["C_SIMP_label"].lower() or scen.startswith("OAT Table 6"))]
        hits = [r for r in hits if not scen.startswith("OAT Table 6") or (r["C_SIMP_label"] == "SIMP GPU" and r["C_inf_label"] == "OAT")]
        assert len(hits) == 1, (scen, size, len(hits))
        return hits[0]
    # value labels are the registered texts (N021, N022, N023, N024, N103, N050, N404); open markers: pre-registered
    # matching rule or the PARDISO baseline
    pard64 = [r for r in b["rows"] if r["size"] == 64 and "pardiso" in r["C_SIMP_label"].lower()
              and r["scenario"].startswith("same machine, matched quality (primary, censored")]
    assert len(pard64) == 1 and abs(pard64[0]["tau_uses"] - reg["N404"]["value"]) < 1
    items = [("Stated in OAT's paper", b["oat_tau_stated"], C["grey"], "N021", True),
             ("OAT's own timing table, 256²", row("OAT Table 6 as reported", 256)["tau_uses"], C["grey"], "N022", True),
             ("Our machine, 150 iterations, 256²", row("same machine, 150 iterations incl. setup", 256)["tau_uses"], C["gpu"], "N023", True),
             ("Our machine, matched quality, 256²", row("same machine, matched quality (primary, censored", 256)["tau_uses"], C["gpu"], "N024", True),
             ("Same, pre-registered matching rule", x2["oat_rules"]["tau_preregistered_256"], C["gpu"], "N103", False),
             ("Our machine, matched quality, 64²", row("same machine, matched quality (primary, censored", 64)["tau_uses"], C["gpu"], "N050", True),
             ("Same, PARDISO as the baseline", pard64[0]["tau_uses"], C["cpu"], "N404", False)]
    ax = fig.add_subplot(gs[0, 0])
    rows = []
    for i, (lab, tau, col, nid, filled) in enumerate(items):
        y = len(items) - 1 - i
        if tau is None or not np.isfinite(tau):
            ax.text(1.25e5, y, f"{reg[nid]['text']}: our baseline is faster", va="center", fontsize=8)
            rows.append(["a", lab, "never"])
            continue
        ax.plot([1e5, tau], [y, y], color=col, lw=0.8)
        ax.plot([tau], [y], ls="none", marker="D" if col == C["cpu"] else "o", ms=4.2, mfc=col if filled else "white",
                mec=col, mew=0.9)
        ax.text(tau * 1.35, y, reg[nid]["text"], va="center", fontsize=8)
        rows.append(["a", lab, f"{tau:.0f}"])
    ax.set_xscale("log")
    ax.set_xlim(1e5, 1e9)
    ax.set_ylim(-0.6, len(items) - 0.4)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([i[0] for i in items][::-1])
    ax.set_xlabel("Break-even number of uses τ")
    fig.text(0.01, 0.97, "a", fontsize=8, fontweight="bold", va="top")
    ax = fig.add_subplot(gs[0, 1])
    groups = [("energy OAT inference 64", "OAT, 64²", C["oat"], "o"), ("energy ours GPU 64", "Ours, 64²", C["gpu"], "o"),
              ("energy OAT inference 256", "OAT, 256²", C["oat"], "s"), ("energy ours GPU 256", "Ours, 256²", C["gpu"], "s")]
    for i, (stage, lab, col, mk) in enumerate(groups):
        v = np.array([r["board_j_per_design"] for r in en["rows"] if r["stage"] == stage])
        y = len(groups) - 1 - i
        ax.plot(v, y + np.linspace(-0.15, 0.15, len(v)), ls="none", marker=mk, ms=3.6, color=col)
        ax.plot([np.median(v)] * 2, [y - 0.3, y + 0.3], color="black", lw=1.1)
        rows += [["b", lab, f"{t:.2f}"] for t in v]
    ax.set_xscale("log")
    ax.set_ylim(-0.6, len(groups) - 0.4)
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([g[1] for g in groups][::-1])
    ax.set_xlabel("GPU board energy per design (J)")
    letter(ax, "b", x=-0.3)
    save(fig, "fig6_breakeven_energy", rows, ["panel", "item", "value"])


# ---------------------------------------------------------------------------------------------------------------
def fig7_reporting():
    rep = load("reporting.json")["indicators"]
    items = [("code_available", "Code linked"), ("data_available", "Data linked"),
             ("seeds_or_variance", "Seeds or variance"), ("failure_rate_reported", "Failure rate"),
             ("ood_test", "Out-of-distribution test"), ("hardware_per_method_stated", "Hardware per method"),
             ("runtimes_all_cases", "Only selected runtimes"), ("timing_protocol_stated", "Full timing protocol")]
    fig, ax = plt.subplots(figsize=(W1, 70 * MM))
    fig.subplots_adjust(left=0.4, right=0.84, bottom=0.27, top=0.97)
    rows = []
    for i, (k, lab) in enumerate(items):
        d = rep[k]
        y = len(items) - 1 - i
        col = C["gpu"] if d["n"] == 57 else C["oat"]
        mk = "o" if d["n"] == 57 else "s"
        ax.plot([d["ci95"][0], d["ci95"][1]], [y, y], color=col, lw=1.0)
        ax.plot([d["share"]], [y], marker=mk, ms=4, color=col)
        ax.text(1.03, y, f"{d['k']}/{d['n']}", va="center", fontsize=8, transform=ax.get_yaxis_transform())
        rows.append([lab, d["k"], d["n"], f"{d['share']:.4f}", f"{d['ci95'][0]:.4f}", f"{d['ci95'][1]:.4f}"])
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, len(items) - 0.4)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([i[1] for i in items][::-1])
    ax.set_xlabel("Share of articles (95 % CI)")
    ax.set_xticks([0, 0.5, 1])
    ax.set_xticklabels(["0", "0.5", "1"])
    ax.plot([], [], marker="o", ms=3.5, ls="-", color=C["gpu"], label="of 57 included")
    ax.plot([], [], marker="s", ms=3.5, ls="-", color=C["oat"], label="of 28 speed claims")
    ax.legend(loc="upper center", bbox_to_anchor=(0.3, -0.24), ncol=2, handlelength=1.4, columnspacing=1.0)
    save(fig, "fig7_reporting", rows, ["indicator", "k", "n", "share", "ci_low", "ci_high"])


if __name__ == "__main__":
    fig1_flow()
    fig2_decomposition()
    fig3_oat()
    fig4_designs()
    fig5_hgto()
    fig6_breakeven_energy()
    fig7_reporting()
