"""Diagnose the pyEDGE MultiGrid crash (cudaErrorIllegalAddress) seen at 256^2 on this machine.

    source retest/oat_harness/env.sh
    CUDA_LAUNCH_BLOCKING=1 OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.debug_mg --pid 1015 --levels 5 --iters 150

With CUDA_LAUNCH_BLOCKING=1 every kernel launch is synchronous, so the traceback points at the kernel that
actually faults rather than at the next API call. The script prints the iteration reached and the full
traceback, then writes retest/logs/debug_mg_<pid>_L<levels>.txt. Diagnostic only; nothing here is timed.
"""
import argparse
import pathlib
import sys
import traceback

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.oat_harness.problems import load_split  # noqa: E402
from retest.oat_harness.time_oat_simp import build  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pid", type=int, default=1015)
    ap.add_argument("--levels", type=int, default=5)
    ap.add_argument("--iters", type=int, default=150)
    ap.add_argument("--optimizer", default="OC")
    ap.add_argument("--coarse", default="splu")
    args = ap.parse_args()
    from pyEDGE.CUDA import OC, PGD
    rows = load_split("NITO_test")
    problem, cupy = build(rows[args.pid], "MultiGrid", 1e-9, False, args.levels, args.coarse)
    opt = {"OC": OC, "PGD": PGD}[args.optimizer](problem)
    it = -1
    lines = []
    try:
        for it in range(args.iters):
            opt.iter()
            if it % 10 == 0:
                lines.append(f"iter {it}: c = {float(problem.f().get()) if hasattr(problem.f(), 'get') else float(problem.f()):.6g}")
                print(lines[-1], flush=True)
        lines.append(f"completed {args.iters} iterations without error")
    except Exception:
        lines.append(f"FAILED at iteration {it}")
        lines.append(traceback.format_exc())
    text = "\n".join(lines)
    print(text[-4000:])
    out = ROOT / "retest" / "logs" / f"debug_mg_{args.pid}_L{args.levels}_{args.optimizer}_{args.coarse}.txt"
    out.write_text(text, encoding="utf-8")
    print("wrote", out.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
