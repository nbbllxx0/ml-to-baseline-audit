"""Break-even number of uses for OAT (claim C3; plan/MANUSCRIPT_EVIDENCE_MAP.md R-3).

    python -m analysis.breakeven

Formula as published in OAT (arXiv 2510.23667, App. G): tau = C_train / (C_SIMP - C_inference). The paper
takes C_train = 168 H100-days (data generation) + 16 H100-days (final training) and states tau = 2.32 million uses.
It does not state which C_SIMP and C_inference produce 2.32 million, so the implied difference is reported.
Like the paper, this keeps C_train in H100-seconds and the per-design times in seconds on the GPU that measured
them (RTX 4090 in OAT; RTX 5090 here). No hardware conversion is applied; every row names its hardware.
If C_SIMP <= C_inference the method never breaks even (tau = inf).

Inputs: evidence/oat_retest_summary.json (same-machine medians); evidence/ttq_summary.json when present
(time-to-matched-quality). Writes evidence/breakeven.json and figures/data/breakeven.csv.
"""
import csv
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

DAY_S = 86400.0
C_TRAIN_H100_S = (168 + 16) * DAY_S                 # OAT App. G
OAT_TAU_STATED = 2.32e6                              # OAT App. G
# OAT Table 6 (150 SIMP steps; RTX 4090 / i9-14900K), seconds per design
T6 = {64: {"SIMP (CPU)": 3.45, "SIMP GPU": 9.13, "OAT": 0.508, "OAT w/ Ref": 0.637},
      256: {"SIMP (CPU)": 69.45, "SIMP GPU": 68.30, "OAT": 0.51, "OAT w/ Ref": 3.28}}


def tau(c_simp, c_inf):
    d = c_simp - c_inf
    return (C_TRAIN_H100_S / d if d > 0 else math.inf), d


def main():
    rows = []

    def add(scenario, size, simp_label, c_simp, inf_label, c_inf, hardware, source):
        t, d = tau(c_simp, c_inf)
        rows.append({"scenario": scenario, "size": size, "C_SIMP_label": simp_label, "C_SIMP_s": c_simp,
                     "C_inf_label": inf_label, "C_inf_s": c_inf, "delta_s": d, "tau_uses": t,
                     "tau_vs_stated": t / OAT_TAU_STATED, "hardware": hardware, "source": source})

    for size, t6 in T6.items():
        for simp in ("SIMP GPU", "SIMP (CPU)"):
            for inf in ("OAT", "OAT w/ Ref"):
                add("OAT Table 6 as reported", size, simp, t6[simp], inf, t6[inf], "RTX 4090 / i9-14900K (OAT)",
                    "arXiv 2510.23667 Table 6")
    summ_file = ROOT / "evidence" / "oat_retest_summary.json"
    if summ_file.exists():
        st = json.loads(summ_file.read_text(encoding="utf-8"))["stages"]
        for size in (64, 256):
            ours = st.get(f"ours GPU {size}", {}).get("time_s_median")
            ours_cpu = st.get(f"ours PARDISO {size}", {}).get("time_s_median")
            inf = st.get(f"OAT inference {size}", {}).get("time_s_median")
            if ours is not None and inf is not None:
                add("same machine, 150 iterations, loop only (pre-registered timing)", size, "ours GPU (median of 5)",
                    ours, "OAT inference, no Ref (median of 5)", inf, "RTX 5090 / i5-14600KF (this study)",
                    "evidence/oat_retest_summary.json")
            if ours_cpu is not None and inf is not None:
                add("same machine, 150 iterations, loop only (pre-registered timing)", size,
                    "ours PARDISO CPU (median of 5)", ours_cpu, "OAT inference, no Ref (median of 5)", inf,
                    "RTX 5090 / i5-14600KF (this study)", "evidence/oat_retest_summary.json")
            if ours is not None:
                add("ours vs OAT w/ Ref as reported (mixed hardware)", size, "ours GPU (median of 5)", ours,
                    "OAT w/ Ref (Table 6)", T6[size]["OAT w/ Ref"], "ours: RTX 5090; OAT: RTX 4090",
                    "oat_retest_summary.json + Table 6")
    ttq_file = ROOT / "evidence" / "ttq_summary.json"
    if ttq_file.exists():
        for r in json.loads(ttq_file.read_text(encoding="utf-8")).get("breakeven_inputs", []):
            add(r["scenario"], r["size"], r["C_SIMP_label"], r["C_SIMP_s"], r["C_inf_label"], r["C_inf_s"],
                r["hardware"], "evidence/ttq_summary.json")
    out = {"formula": "tau = C_train / (C_SIMP - C_inference) (OAT App. G)",
           "C_train_H100_s": C_TRAIN_H100_S, "C_train_note": "168 + 16 H100-days, as stated in OAT App. G",
           "oat_tau_stated": OAT_TAU_STATED, "implied_delta_s": C_TRAIN_H100_S / OAT_TAU_STATED,
           "rows": rows}
    (ROOT / "evidence" / "breakeven.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
    with open(ROOT / "figures" / "data" / "breakeven.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"implied delta for the stated 2.32 M uses: {out['implied_delta_s']:.3f} s")
    for r in rows:
        t = "never" if math.isinf(r["tau_uses"]) else f"{r['tau_uses'] / 1e6:8.3f} M"
        print(f"{r['scenario'][:44]:44s} n{r['size']:<4} {r['C_SIMP_label'][:26]:26s} {r['C_SIMP_s']:8.3f} s  "
              f"{r['C_inf_label'][:30]:30s} {r['C_inf_s']:6.3f} s  tau {t}")


if __name__ == "__main__":
    main()
