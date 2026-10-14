"""P00150 reconstruction check (plan/BASELINE_PREREG.md §9, P00150 row item 3; mapping v2 after the diagnosis row).

    python -m retest.p00150_harness.check

Reads the untimed SuperLU scan (retest/runs/p00150/superlu/scan.json): our top88 port run to top88's stopping point
on each of the 100 validation problems. Pass condition: our compliance at the stopping point, in the article's units,
within 1 % of the stored top88 compliance on at least 95 of the 100 cases. The GPU scan is reported beside it.
Writes evidence/p00150_check.json; registers N077 (cases within 1 %) and N078 (largest shortfall of the stored value).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.p00150_harness.problems import COMPLIANCE_SCALE, load_top88  # noqa: E402


def ratios(solver):
    f = ROOT / "retest" / "runs" / "p00150" / solver / "scan.json"
    if not f.exists():
        return None
    out = []
    for c in json.loads(f.read_text(encoding="utf-8"))["cases"]:
        stored = load_top88(c["case"])["compliance"]
        ours = c["c_at_stop"] * COMPLIANCE_SCALE if c["c_at_stop"] is not None else None
        out.append({"case": c["case"], "stop_k": c["stop_k"], "stored": stored, "ours": ours,
                    "ratio": stored / ours if ours else None})
    return out


def main():
    res = {}
    for solver in ("superlu", "gpu"):
        rows = ratios(solver)
        if rows is None:
            continue
        r = [x["ratio"] for x in rows if x["ratio"] is not None]
        res[solver] = {"n": len(rows), "no_stop": sum(x["ratio"] is None for x in rows),
                       "within_1pct": sum(abs(v - 1) <= 0.01 for v in r),
                       "min_ratio": min(r), "max_ratio": max(r), "cases": rows}
    s = res["superlu"]
    out = {"pass_condition": ">= 95 of 100 within 1 % (SuperLU port, stopping point)",
           "passed": s["within_1pct"] >= 95 and s["no_stop"] == 0, "mapping": "v2", **res}
    (ROOT / "evidence" / "p00150_check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    from tools.numbers import register
    register("N077", s["within_1pct"], text=f"{s['within_1pct']} of {s['n']}", source="evidence/p00150_check.json",
             script="retest/p00150_harness/check.py",
             note="P00150 reconstruction check: cases where our top88 port matches the stored compliance within 1 % "
                  "(pre-registered pass: at least 95)")
    short = 1 - s["min_ratio"]
    register("N078", short, unit="%", text=f"{100 * short:.0f} %", source="evidence/p00150_check.json",
             script="retest/p00150_harness/check.py",
             note="largest amount by which a stored top88 compliance falls below our reproduction")
    print(json.dumps({k: v for k, v in out.items() if k not in ("superlu", "gpu")}, indent=1))
    for solver, v in res.items():
        print(solver, {k: v[k] for k in ("n", "no_stop", "within_1pct", "min_ratio", "max_ratio")})


if __name__ == "__main__":
    main()
