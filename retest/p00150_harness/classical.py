"""Classical top88-formulation runs on the 100 P00150 validation problems (plan/BASELINE_PREREG.md §9, P00150 row).

    python -m retest.p00150_harness.classical scan  --solver superlu|pardiso|gpu
    python -m retest.p00150_harness.classical timed --solver superlu|pardiso|gpu

scan:  every case once with a 1,000-iteration budget. Records compliance and design change per iteration. stop_k is
       the first iteration whose design change is <= 0.01; top88's loop ends after that update. Writes
       retest/runs/p00150/<solver>/scan.json.
timed: pinned when PIN_PCORES=1; one discarded 10-iteration warm-up; then, per case, three fresh runs with budget
       stop_k + 1 (top88's loop up to its stopping point), timed setup-inclusive (setup + loop), with per-iteration
       times kept for the matched-quality analysis. Saves the final design of the first repeat. Writes
       retest/runs/p00150/<solver>/timed.json and designs.npz.
Environments: gpu and superlu in conda torch5090; pardiso in conda Pytorch (plan/BASELINE_PREREG.md §3).
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "retest" / "runs" / "p00150"
MAX_ITERS = 1000
STOP_CHANGE = 0.01


def runner(solver):
    if solver == "gpu":
        from retest.baseline import simp_gpu

        def run(prob, iters):
            rec, xphys, _ = simp_gpu.run(prob, iters=iters)
            return rec, xphys
    else:
        from retest.baseline import simp_cpu

        def run(prob, iters):
            rec, xphys, _ = simp_cpu.run(prob, solver=solver, iters=iters)
            return rec, xphys
    return run


def stop_index(change):
    for i, ch in enumerate(change):
        if ch <= STOP_CHANGE:
            return i
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=("scan", "timed"))
    ap.add_argument("--solver", required=True, choices=("gpu", "pardiso", "superlu"))
    args = ap.parse_args()
    from tools.pin import pin_from_env
    pinning = pin_from_env() if args.phase == "timed" else {"pinned": False}
    import numpy as np
    from retest.p00150_harness.problems import load_cases, problem
    run = runner(args.solver)
    out = OUT / args.solver
    out.mkdir(parents=True, exist_ok=True)
    cases = load_cases()
    if args.phase == "scan":
        target = out / "scan.json"
        if target.exists():
            raise SystemExit(f"{target} exists")
        res = []
        for c in cases:
            rec, _ = run(problem(c), MAX_ITERS)
            s = stop_index(rec["change"])
            res.append({"case": c["k"], "stop_k": s, "c": rec["c"], "change": rec["change"],
                        "c_at_stop": rec["c"][s] if s is not None else None, "vol_final": rec["vol"][-1]})
            print(c["k"], s, rec["c"][s] if s is not None else None, flush=True)
        target.write_text(json.dumps({"solver": args.solver, "max_iters": MAX_ITERS, "stop_change": STOP_CHANGE,
                                      "cases": res}), encoding="utf-8")
        return
    target = out / "timed.json"
    if target.exists():
        raise SystemExit(f"{target} exists")
    scan = {r["case"]: r for r in json.loads((out / "scan.json").read_text(encoding="utf-8"))["cases"]}
    run(problem(cases[0]), 10)                                  # warm-up, discarded
    res, designs = [], {}
    for c in cases:
        s = scan[c["k"]]["stop_k"]
        budget = (s + 1) if s is not None else MAX_ITERS
        reps = []
        for r in range(3):
            rec, xphys = run(problem(c), budget)
            reps.append({"t_setup": rec["t_setup"], "t_iter": rec["t_iter"], "c": rec["c"],
                         "wall_s": rec["t_setup"] + float(np.sum(rec["t_iter"]))})
            if r == 0:
                designs[f"case{c['k']:03d}"] = np.asarray(xphys)
        walls = sorted(x["wall_s"] for x in reps)
        res.append({"case": c["k"], "budget": budget, "converged": s is not None, "wall_s_median": walls[1],
                    "wall_s_min": walls[0], "wall_s_max": walls[2], "c_final_iter": reps[0]["c"][-1], "repeats": reps})
        print(c["k"], budget, f"{walls[1]:.4f}", flush=True)
    np.savez_compressed(out / "designs.npz", **designs)
    target.write_text(json.dumps({"solver": args.solver, "cpu_pinning": pinning, "cases": res}), encoding="utf-8")


if __name__ == "__main__":
    main()
