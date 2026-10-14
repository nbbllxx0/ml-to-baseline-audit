"""Equivalence gate of the HGTO re-test (plan/BASELINE_PREREG.md §9, HGTO re-test row, item 4).

    python -m retest.hgto_harness.campaign gate

(i) On the three 120x40 configurations, the per-update compliance of the GPU port (validate run) matches HGTO's
SIMP-OC with two threads (first run) within 1e-5 relative over the first 50 updates.
(ii) On all six configurations, the port's final compliance, from the common independent evaluator (C_raw after the
final scikit-fem evaluation in both runners), lies within 1 % of SIMP-OC's, with the same termination status.
Writes evidence/hgto_gate.json; returns 0 if both hold, else 1.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNS = ROOT / "retest" / "runs" / "hgto"
SMALL = ["cantilever_120x40", "half_mbb", "inclined_cantilever"]
ALL = SMALL + ["cantilever_240x80", "cantilever_480x160", "cantilever_960x320"]


def load(method, config):
    d = RUNS / method / config / "r0"
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    hist = json.loads((d / "history.json").read_text(encoding="utf-8"))
    return res, hist


def main():
    out = {"per_update_first_50": {}, "final": {}}
    ok = True
    for c in ALL:
        ref, rh = load("oc2", c)
        ours, oh = load("ours_validate", c)
        if c in SMALL:
            n = min(50, len(rh), len(oh))
            worst = max(abs(a["C"] - b["C"]) / abs(a["C"]) for a, b in zip(rh[:n], oh[:n]))
            passed = n == 50 and worst <= 1e-5
            out["per_update_first_50"][c] = {"updates_compared": n, "max_relative_difference": worst, "pass": passed}
            ok &= passed
        rel = abs(ours["C_raw"] - ref["C_raw"]) / ref["C_raw"]
        passed = rel <= 0.01 and ours["termination"] == ref["termination"]
        out["final"][c] = {"C_oc2": ref["C_raw"], "C_port": ours["C_raw"], "relative_difference": rel,
                           "termination_oc2": ref["termination"], "termination_port": ours["termination"],
                           "updates_oc2": ref["state_evaluations"], "updates_port": ours["state_evaluations"],
                           "pass": passed}
        ok &= passed
    out["gate_pass"] = bool(ok)
    (ROOT / "evidence" / "hgto_gate.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
