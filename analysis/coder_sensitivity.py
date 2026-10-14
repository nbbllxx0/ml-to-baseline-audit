"""Post hoc coder sensitivity of the headline results (not pre-registered; context for C1, G1 and C5).

    python -m analysis.coder_sensitivity

The weak-baseline rules R1 and R2 had the lowest agreement between the two independent AI codings (C5). This script
recomputes the headline quantities under three codings of the same records:
  * first:  the first AI pass (audit/coding/llm_prefill/);
  * second: the blind second AI pass by a different model (audit/coding/second_pass/);
  * final:  the verified records (audit/coding/records/, agreed or adjudicated), as reported.
Quantities: G1 on the decision order (analysis/gates.g1, unchanged rules), and within the analysis sample (positions
1-200) the speed-stratum share with a fail on R1 or R2, with Clopper-Pearson 95 % intervals. A coding that lacks a
record falls back to nothing (records missing from a pass are treated as not coded). Writes
evidence/coder_sensitivity.json; registers N081-N083 (weak share in the sample under each coding).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis import gates  # noqa: E402
from analysis.rules import SAMPLE_POSITIONS, clopper_pearson, sample_pids  # noqa: E402

SOURCES = {"first": "audit/coding/llm_prefill", "second": "audit/coding/second_pass", "final": "audit/coding/records"}


def load(folder, keep):
    out = {}
    for f in (ROOT / folder).glob("P*.json"):
        if f.stem in keep:
            out[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    return out


def main():
    keep = sample_pids(SAMPLE_POSITIONS)
    gates.SCREEN_EXCLUDED = gates.screen_excluded()          # module state that gates.main() sets before g1
    gates.ACCESS, gates.SUPPLIED = gates.access_maps()
    seq = [(pid, f"order {i}") for i, pid in enumerate(gates.pids("pilot_final_order.csv"), 1)]
    out = {"note": "post hoc; the 'final' column is the reported result", "codings": {}}
    for name, folder in SOURCES.items():
        recs = load(folder, keep)
        g = gates.g1(recs, seq)
        speed = [r for r in recs.values() if r["included"]["decision"] == "include"
                 and r["included"].get("stratum") == "speed" and r.get("access") == "full_text"]
        weak = sum(1 for r in speed if "fail" in (r["rules"]["R1"]["verdict"], r["rules"]["R2"]["verdict"]))
        out["codings"][name] = {"records": len(recs), "G1": {k: g[k] for k in ("n_speed_stratum", "complete",
                                                                             "n_fail_R1_or_R2", "share", "ci95",
                                                                             "band", "stopped_at")},
                                "sample_speed_stratum": {"n": len(speed), "weak_R1_or_R2": weak,
                                                         "share": weak / len(speed) if speed else None,
                                                         "ci95": clopper_pearson(weak, len(speed))}}
    (ROOT / "evidence" / "coder_sensitivity.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    from tools.numbers import register
    for nid, name in (("N081", "first"), ("N082", "second"), ("N083", "final")):
        s = out["codings"][name]["sample_speed_stratum"]
        if s["share"] is not None:
            register(nid, s["share"], text=f"{100 * s['share']:.0f} % ({s['weak_R1_or_R2']}/{s['n']})",
                     source="evidence/coder_sensitivity.json", script="analysis/coder_sensitivity.py",
                     note=f"speed-stratum share with a fail on R1 or R2 in the analysis sample, {name} coding (post hoc)")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
