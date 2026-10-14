"""Post hoc agreement breakdown (not pre-registered; reported as descriptive context for C5).

    python -m analysis.agreement_posthoc

Cohen's kappa for R1-R4 between the first AI pass and the blind second AI pass, restricted to pairs where both
coders placed the article in the speed stratum. Rationale: the headline rates and G1 use the speed stratum, and part
of the all-pairs disagreement on R2 comes from its applicability to quality-only outcomes, which the protocol
settled only before adjudication (PROTOCOL §11, stratum-Q row). Writes evidence/agreement_posthoc.json. Registers
nothing.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.agreement import boot, kappa  # noqa: E402


def main():
    first, second = ROOT / "audit/coding/llm_prefill", ROOT / "audit/coding/second_pass"
    pairs = []
    for fb in sorted(second.glob("P*.json")):
        fa = first / fb.name
        if fa.exists():
            a, b = (json.loads(f.read_text(encoding="utf-8")) for f in (fa, fb))
            if all(r["included"]["decision"] == "include" and r["included"].get("stratum") == "speed" for r in (a, b)):
                pairs.append((a, b))
    out = {"subset": "both coders: include, speed stratum", "n_pairs": len(pairs), "items": {},
           "note": "post hoc; descriptive only; C5 as pre-registered is evidence/agreement.json"}
    for k in ("R1", "R2", "R3", "R4"):
        xa = [a["rules"][k]["verdict"] for a, _ in pairs]
        xb = [b["rules"][k]["verdict"] for _, b in pairs]
        out["items"][k] = {"n": len(pairs), "agreement": sum(x == y for x, y in zip(xa, xb)) / len(pairs) if pairs else None,
                           "kappa": kappa(xa, xb), "kappa_ci95": boot(xa, xb) if len(pairs) >= 5 else [None, None]}
    (ROOT / "evidence" / "agreement_posthoc.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
