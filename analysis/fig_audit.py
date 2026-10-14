"""Audit display items: F1 screening flow, F2 rule verdicts by year, F6 reporting indicators, ED1 per-paper table,
ED4 scale sensitivity, ED5 LLM-agent stratum.

    python -m analysis.fig_audit                  # verified records only (decision-grade)
    python -m analysis.fig_audit --provisional    # also unverified LLM prefills; every output is labelled provisional

Inputs: evidence/prisma.json, coding records (audit/coding/records/ or llm_prefill/), evidence/reporting*.json.
Writes figures/f1_flow[_provisional].png/.svg, f2_rules_by_year[...], f6_reporting[...],
figures/data/ed1_verdicts[...].csv and evidence/ed4_sensitivity[...].json, evidence/ed5_llm_stratum[...].json.
Palette: dataviz reference categorical slots (validated all-pairs, light mode); verdicts use a fixed order.
"""
import argparse
import csv
import json
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.codes import ft_code  # noqa: E402
from analysis.rules import SAMPLE_POSITIONS, clopper_pearson, load  # noqa: E402

INK, INK2, SURFACE, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e2dc"
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
VERDICT_COLOR = {"pass": GREEN, "partial": BLUE, "fail": ORANGE, "na": GRID}


def style(ax, grid_axis="x"):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=7.5)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(ROOT / "figures" / f"{name}.png", dpi=200, facecolor=SURFACE)
    fig.savefig(ROOT / "figures" / f"{name}.svg", facecolor=SURFACE)
    plt.close(fig)


def f1(sfx, recs, label):
    pr = json.loads((ROOT / "evidence" / "prisma.json").read_text(encoding="utf-8"))
    inc = [r for r in recs.values() if r["included"]["decision"] == "include"]
    ex = {}
    for r in recs.values():
        if r["included"]["decision"] == "exclude":
            c = ft_code(r["included"]["reason"])
            ex[c] = ex.get(c, 0) + 1
    speed = sum(1 for r in inc if r["included"].get("stratum") == "speed")
    qual = sum(1 for r in inc if r["included"].get("stratum") == "quality")
    rs_file = ROOT / "evidence" / "rescreen.json"
    rs = json.loads(rs_file.read_text(encoding="utf-8")) if rs_file.exists() else None
    n_full = sum(1 for r in recs.values() if r.get("access") == "full_text")
    boxes = [(f"Records returned\n{pr['records_returned_total']:,}\n(arXiv {pr['records_returned_by_family'].get('arxiv', 0)}, "
              f"OpenAlex {pr['records_returned_by_family'].get('openalex', 0)},\nforward {pr['records_returned_by_family'].get('forward', 0)}, "
              f"backward {pr['records_returned_by_family'].get('backward', 0)})"),
             f"Unique after de-duplication\n{pr['unique_after_dedup']:,}",
             f"Title/abstract screening (LLM)\n{pr['llm_includes']} includes" + (
                 f"\nblind re-screen of {rs['n_sampled_excludes']} sampled excludes:\n"
                 f"{rs['rescreen_includes']} would include" if rs else ""),
             f"Decision order (seeded random order)\n{pr.get('decision_order_eligible', '?')} eligible "
             f"after the type and date rules;\nanalysis sample = positions 1–{pr.get('sample_positions', 200)}",
             f"Coded twice and verified: {len(recs)}\n(paywalled records skipped)\n{n_full} full text; "
             f"{len(recs) - n_full} abstract only or no access",
             f"Included at full text: {speed + qual}\nspeed stratum {speed}, quality stratum {qual}"]
    fig, ax = plt.subplots(figsize=(7.5, 7.4), facecolor=SURFACE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis("off")
    ys = [11.0, 9.1, 7.2, 5.3, 3.4, 1.5]
    for y, text in zip(ys, boxes):
        ax.add_patch(plt.Rectangle((0.6, y - 0.75), 5.2, 1.5, facecolor=SURFACE, edgecolor=INK2, linewidth=1.0))
        ax.text(3.2, y, text, ha="center", va="center", fontsize=7.5, color=INK)
    for y0, y1 in zip(ys, ys[1:]):
        ax.annotate("", xy=(3.2, y1 + 0.78), xytext=(3.2, y0 - 0.78), arrowprops=dict(arrowstyle="->", color=INK2))
    exl = ", ".join(f"{k.replace('FT-', '')} {v}" for k, v in sorted(ex.items(), key=lambda kv: -kv[1]))
    scr_ex = sorted(((k, v) for k, v in pr["llm_codes"].items() if k.startswith("E-")), key=lambda kv: -kv[1])
    ax.text(6.2, 7.2, "Excluded at screening:\n" + "\n".join(f"{k} {v}" for k, v in scr_ex), fontsize=6.5, color=INK2,
            va="center")
    ax.text(6.2, 3.4, "Excluded at full text:\n" + (exl.replace(", ", "\n") or "none"), fontsize=6.5,
            color=INK2, va="center")
    ax.set_title(f"F1  Screening flow ({label})", loc="left", fontsize=9, color=INK)
    save(fig, f"f1_flow{sfx}")


def f2(sfx, recs, label):
    speed = [r for r in recs.values() if r["included"]["decision"] == "include" and r["included"].get("stratum") == "speed"]
    years = sorted({r["citation"].get("year") for r in speed if r["citation"].get("year")})
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.6), facecolor=SURFACE, sharey=True)
    for ax, rule in zip(axes, ("R1", "R2", "R3", "R4")):
        for i, y in enumerate(years):
            vs = [r["rules"][rule]["verdict"] for r in speed if r["citation"].get("year") == y]
            left = 0
            for v in ("fail", "partial", "pass", "na"):
                n = vs.count(v)
                if n:
                    ax.barh(i, n, left=left, color=VERDICT_COLOR[v], edgecolor=SURFACE, height=0.7)
                    left += n
        ax.set_yticks(range(len(years)))
        ax.set_yticklabels([str(y) for y in years], fontsize=7, color=INK)
        ax.set_title(rule, loc="left", fontsize=9, color=INK)
        ax.set_xlabel("articles", fontsize=7.5, color=INK)
        style(ax)
    axes[0].legend([plt.Rectangle((0, 0), 1, 1, color=VERDICT_COLOR[v]) for v in ("fail", "partial", "pass", "na")],
                   ["fail", "partial", "pass", "n/a"], fontsize=6.5, frameon=False, loc="lower right", labelcolor=INK)
    fig.suptitle(f"F2  Rule verdicts by publication year, speed stratum ({label}; n = {len(speed)})", x=0.01, ha="left",
                 fontsize=9, color=INK)
    fig.tight_layout()
    save(fig, f"f2_rules_by_year{sfx}")


def f6(sfx, label):
    f = ROOT / "evidence" / f"reporting{sfx}.json"
    if not f.exists():
        return
    rep = json.loads(f.read_text(encoding="utf-8"))
    items = list(rep["indicators"].items())
    fig, ax = plt.subplots(figsize=(7.5, 3.6), facecolor=SURFACE)
    for i, (k, v) in enumerate(items):
        if v["share"] is None:
            continue
        lo, hi = v["ci95"]
        ax.plot([lo, hi], [i, i], color=INK2, linewidth=1.2)
        ax.plot(v["share"], i, "o", color=BLUE, ms=6)
        ax.text(1.02, i, f"{v['k']}/{v['n']}", fontsize=6.5, color=INK, va="center", transform=ax.get_yaxis_transform())
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([f"{k.replace('_', ' ')} = {v['headline_value']}" for k, v in items], fontsize=7, color=INK)
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of included articles (95 % CI)", fontsize=8, color=INK)
    ax.set_title(f"F6  Reporting indicators ({label})", loc="left", fontsize=9, color=INK)
    style(ax)
    fig.tight_layout()
    save(fig, f"f6_reporting{sfx}")


def ed1(sfx, recs):
    rows = []
    for r in sorted(recs.values(), key=lambda r: r["pid"]):
        if r["included"]["decision"] != "include":
            continue
        c, cl = r["citation"], r.get("claim", {})
        rows.append({"pid": r["pid"], "title": c.get("title", ""), "year": c.get("year"), "venue": c.get("venue", ""),
                     "stratum": r["included"].get("stratum"), "method_family": r["included"].get("method_family"),
                     **{k: r["rules"][k]["verdict"] for k in ("R1", "R2", "R3", "R4")},
                     **{f"{k}_marker": r["rules"][k].get("marker", "") for k in ("R1", "R2", "R3", "R4")},
                     "primary_outcome_location": cl.get("location", ""), "key_phrase": cl.get("key_phrase", ""),
                     "claimed_speedup": cl.get("claimed_speedup"), "stage": r.get("stage")})
    if rows:
        with open(ROOT / "figures" / "data" / f"ed1_verdicts{sfx}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    return len(rows)


def ed4(sfx, recs):
    speed = [r for r in recs.values() if r["included"]["decision"] == "include" and r["included"].get("stratum") == "speed"]
    out = {}
    for name, bad in (("fail only (headline)", {"fail"}), ("fail or partial (sensitivity)", {"fail", "partial"})):
        k = sum(any(r["rules"][x]["verdict"] in bad for x in ("R1", "R2")) for r in speed)
        out[name] = {"k": k, "n": len(speed), "share": k / len(speed) if speed else None,
                     "ci95": clopper_pearson(k, len(speed))}
    (ROOT / "evidence" / f"ed4_sensitivity{sfx}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def ed5(sfx, recs):
    llm = [r for r in recs.values() if r["included"].get("method_family") == "llm_agent"]
    out = {"n_coded": len(llm), "records": [{"pid": r["pid"], "decision": r["included"]["decision"],
                                             "stratum": r["included"].get("stratum"),
                                             **{k: r["rules"][k]["verdict"] for k in ("R1", "R2", "R3", "R4")}}
                                            for r in llm],
           "note": "rates are reported only when n >= 5 (evidence map, R-1)"}
    (ROOT / "evidence" / f"ed5_llm_stratum{sfx}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provisional", action="store_true")
    args = ap.parse_args()
    sfx = "_provisional" if args.provisional else ""
    label = ("provisional: first-pass AI coding, not yet double-coded" if args.provisional
             else "verified: AI double-coded and adjudicated")
    recs = load(args.provisional, SAMPLE_POSITIONS)
    (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
    f1(sfx, recs, label)
    f2(sfx, recs, label)
    f6(sfx, label)
    n1 = ed1(sfx, recs)
    s4 = ed4(sfx, recs)
    s5 = ed5(sfx, recs)
    print(json.dumps({"records": len(recs), "ed1_rows": n1, "ed4": s4, "ed5_n": s5["n_coded"]}, indent=1))


if __name__ == "__main__":
    main()
