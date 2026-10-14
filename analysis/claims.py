"""Distribution of claimed speed-ups among included speed-stratum articles (Introduction I-1; N013–N015).

    python -m analysis.claims                 # verified records only (decision-grade)
    python -m analysis.claims --provisional   # also unverified LLM prefills (labelled provisional)

`claim.claimed_speedup` is the factor stated in, or derivable from, the article (classical time / ML time), with its
basis recorded by the coder. Writes evidence/claims[_provisional].json and figures/data/claimed_speedups[_provisional].csv.
Numbers are registered only in verified mode (AI double-coded records, agreed or adjudicated).
"""
import argparse
import csv
import json
import math
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.rules import SAMPLE_POSITIONS, VERIFIED_STAGES, load  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provisional", action="store_true")
    args = ap.parse_args()
    recs = load(args.provisional, SAMPLE_POSITIONS)
    speed = [r for r in recs.values() if r["included"]["decision"] == "include" and r["included"].get("stratum") == "speed"]
    rows = []
    for r in speed:
        cl = r.get("claim", {})
        v = cl.get("claimed_speedup")
        rows.append({"pid": r["pid"], "year": r["citation"].get("year"), "method_family": r["included"].get("method_family"),
                     "claimed_speedup": v, "basis": (cl.get("claimed_speedup_basis") or "")[:200],
                     "direction": cl.get("direction"), "stage": r.get("stage")})
    vals = sorted(float(x["claimed_speedup"]) for x in rows if isinstance(x["claimed_speedup"], (int, float)))
    q = lambda p: vals[min(len(vals) - 1, max(0, int(math.ceil(p * len(vals))) - 1))] if vals else None  # noqa: E731
    out = {"mode": "provisional" if args.provisional else "verified only (AI double-coded and agreed or adjudicated)", "n_speed_stratum": len(speed),
           "n_with_numeric_claim": len(vals),
           "median": statistics.median(vals) if vals else None, "q25": q(0.25), "q75": q(0.75),
           "min": vals[0] if vals else None, "max": vals[-1] if vals else None,
           "direction_counts": {d: sum(1 for x in rows if x["direction"] == d)
                                for d in ("outperform", "underperform", "similar_or_mixed", None)},
           "n_below_1": sum(1 for v in vals if v < 1.0),
           "verified": sum(1 for r in speed if r.get("stage") in VERIFIED_STAGES)}
    sfx = "_provisional" if args.provisional else ""
    (ROOT / "evidence" / f"claims{sfx}.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    if rows:
        (ROOT / "figures" / "data").mkdir(parents=True, exist_ok=True)
        with open(ROOT / "figures" / "data" / f"claimed_speedups{sfx}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    if not args.provisional and vals:
        from tools.numbers import register
        register("N013", out["median"], unit="×", text=f"{out['median']:.0f}×", source="evidence/claims.json",
                 script="analysis/claims.py", note="median claimed speed-up, verified speed-stratum records")
        def fx(v):                                     # 1.2×, 24×, 300,000× (no exponent notation in prose)
            return f"{v:,.0f}×" if v >= 100 else f"{v:.2g}×"
        register("N014", [out["min"], out["max"]], unit="×", text=f"{fx(out['min'])} to {fx(out['max'])}",
                 source="evidence/claims.json", script="analysis/claims.py", note="range of claimed speed-ups")
        register("N015", out["n_with_numeric_claim"], text=f"{out['n_with_numeric_claim']} of {len(speed)}",
                 source="evidence/claims.json", script="analysis/claims.py",
                 note="speed-stratum records with a numeric claimed speed-up")
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
