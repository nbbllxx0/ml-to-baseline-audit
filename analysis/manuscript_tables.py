"""Main-text tables for the SMO manuscript, generated from frozen evidence files (no number typed by hand).

    python -m analysis.manuscript_tables

Table 2  audit verdicts by rule and stratum (evidence/c1_rules.json, c1_rules_sensitivity.json, gates.json)
Table 3  re-test summary: reported vs same-machine speed-ups (evidence/numbers.json for OAT; evidence/hgto_retest.json)
Table 4  agreement between the two independent AI codings, and the weak share under each coding
         (evidence/agreement.json, evidence/coder_sensitivity.json)
Writes manuscript/tables/table{2,3,4}_*.csv and .md. Table 1 (rules and verdict criteria) is text in the draft.
"""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript" / "tables"


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def pct(k, n, ci):
    if not n:
        return "–"
    return f"{100 * k / n:.0f} % ({k}/{n}; {100 * ci[0]:.0f}–{100 * ci[1]:.0f})"


def write(name, header, rows, caption):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    md = [f"**{caption}**", "", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    md += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    (OUT / f"{name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def table2():
    c1, sens, g = load("evidence/c1_rules.json"), load("evidence/c1_rules_sensitivity.json"), load("evidence/gates.json")
    rows = []
    for stratum in ("speed", "quality"):
        s, t = c1["strata"][stratum], sens["strata"][stratum]
        for k in ("R1", "R2", "R3", "R4"):
            a, b = s[k], t[k]
            rows.append([stratum, k, a["n_applicable"], pct(a["n_fail"], a["n_applicable"], a["ci95"]),
                         pct(b["n_fail"], b["n_applicable"], b["ci95"])])
        w, ws = s["weak_R1_or_R2"], t["weak_R1_or_R2"]
        rows.append([stratum, "R1 or R2 (weak baseline)", s["n"], pct(w["k"], s["n"], w["ci95"]),
                     pct(ws["k"], s["n"], ws["ci95"])])
        a, as_ = s["any_rule"], t["any_rule"]
        rows.append([stratum, "any rule", s["n"], pct(a["k"], s["n"], a["ci95"]), pct(as_["k"], s["n"], as_["ci95"])])
    G = g["G1"]
    rows.append(["speed (decision order)", "G1: R1 or R2, first 20", G["n_speed_stratum"],
                 pct(G["n_fail_R1_or_R2"], G["n_speed_stratum"], G["ci95"]), "–"])
    write("table2_audit_rates", ["Stratum", "Rule", "n (rule applies)", "Fail, % (k/n; 95 % CI)",
                                 "Fail or partial, % (k/n; 95 % CI)"], rows,
          "Table 2 Rule verdicts in the analysis sample (decision order 1–200; verified records)")


def table3():
    num, hg = load("evidence/numbers.json"), load("evidence/hgto_retest.json")["configs"]

    def v(nid):
        return num[nid]["value"]
    rows = [["OAT", "256²", f"{v('N016'):.0f}× (RTX 4090)", f"{v('N017'):.1f}× (150 iterations, setup incl.)",
             f"{v('N018'):.2f}×"],
            ["OAT", "64²", f"{v('N019'):.1f}× (RTX 4090)", f"{v('N020'):.1f}× (150 iterations, setup incl.)",
             f"{v('N039'):.2f}×"]]
    for cfg, size in (("cantilever_480x160", "480×160"), ("cantilever_960x320", "960×320")):
        e = hg[cfg]
        rows.append(["HGTO", size, f"{e['published']['oc_over_hgto']:.1f}× (RTX 6000 Ada; 2 CPU threads)",
                     f"{e['ratios_vs_hgto_gpu']['ours']:.2f}× (converged; GPU port)",
                     f"{e['matched_quality_ours']['ratio_vs_hgto_gpu']:.2f}×"])
    write("table3_retests", ["Method", "Size", "Reported speed-up (paper's hardware)",
                             "Same machine, strong baseline", "Same machine, matched quality"], rows,
          "Table 3 Speed-up of each learned method over SIMP: reported and re-tested on one workstation "
          "(values below 1: the classical baseline is faster)")


def table4():
    ag, cs = load("evidence/agreement.json")["first_vs_second_ai_pass"], load("evidence/coder_sensitivity.json")
    rows = []
    for item, label in (("included", "Inclusion"), ("stratum", "Stratum"), ("R1", "R1"), ("R2", "R2"), ("R3", "R3"),
                        ("R4", "R4")):
        s = ag["items"][item]
        lo, hi = s["kappa_ci95"]
        rows.append([label, s["n"], f"{100 * s['agreement']:.0f} %", f"{s['kappa']:.2f} ({lo:.2f}–{hi:.2f})"])
    for name, label in (("first", "first coder only"), ("second", "second coder only"), ("final", "adjudicated")):
        s = cs["codings"][name]["sample_speed_stratum"]
        rows.append([f"Weak share (R1 or R2), {label}", s["n"], pct(s["weak_R1_or_R2"], s["n"], s["ci95"]), "–"])
    write("table4_agreement", ["Item", "n", "Raw agreement / share", "Cohen's κ (95 % CI)"], rows,
          "Table 4 Agreement between two independent AI codings (first pass vs blind second pass), and the weak "
          "share under each coding (post hoc)")


def main():
    table2()
    table3()
    table4()
    for f in sorted(OUT.glob("*.md")):
        print(f.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
