"""Run the GPU port of HGTO's SIMP-OC on one HGTO linear2d configuration, timed over HGTO's own wall_s scope.

    python -m retest.hgto_harness.run_ours --config <HGTO configs/linear2d/*.yaml> --output <new dir> [--validate]

Pre-registered in plan/BASELINE_PREREG.md §9 (HGTO re-test row). The timed interval copies hgto.linear.run: t0 after
imports and a CUDA synchronize; case construction (hgto.linear.problem_from_settings, as HGTO's own runs do); setup
and optimization (retest/hgto_harness/oc_gpu.py); the final independent scikit-fem evaluation of the returned density
with the same reference call and checks as hgto.linear.run; wall_s ends after that evaluation. Imports and file output
are outside the interval. CPU threads for the evaluation are set like HGTO's command line (--threads, default 2).
The process is pinned to the performance cores when PIN_PCORES=1 (tools/pin.py).
Output, in HGTO's layout so `hgto evaluate <dir>` scores it like HGTO's own designs: rho.npy, geometry.npz,
result.json, history.json. --validate repeats HGTO's own PhysicalStopping at every update on host copies of the
density and requires identical stopping decisions; it is never used for timed runs.
"""
import argparse
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, type=pathlib.Path)
    ap.add_argument("--output", required=True, type=pathlib.Path)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--no-graphs", action="store_true")
    args = ap.parse_args()
    for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        os.environ[name] = str(args.threads)
    from tools.pin import pin_from_env
    pinning = pin_from_env()
    import json
    import time

    import numpy as np
    import torch
    from hgto.cli import load_settings
    from hgto.linear import problem_from_settings
    from hgto.reference import ScikitFEMElasticity
    from hgto.reference.oc import OCConfig
    from hgto.stopping import PhysicalStopping, StopConfig
    from retest.hgto_harness.oc_gpu import optimize, to_problem

    settings = load_settings(args.config, method="oc")
    if settings.get("category", "linear2d") != "linear2d":
        raise SystemExit("linear2d configurations only")
    cfg = OCConfig(**settings["oc"])
    if cfg.stopping_rule != "physical" or cfg.continuation_stage_cap is None:
        raise SystemExit("the port implements the physical stopping rule with a continuation-stage cap only")
    if args.output.exists():
        raise SystemExit(f"choose a new output directory: {args.output}")
    args.output.mkdir(parents=True)
    torch.set_num_threads(args.threads)
    ref_stop = (PhysicalStopping(StopConfig(objective_tolerance=cfg.compliance_tolerance,
                                            density_tolerance=cfg.change_tolerance, patience=cfg.stable_steps))
                if args.validate else None)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    _, problem, _, geometry, _ = problem_from_settings(settings, args.config.resolve().parent)
    prob = to_problem(problem)
    rho, history, summary = optimize(prob, cfg.betas, cfg.penalties, max_stage_steps=cfg.max_stage_steps,
                                     continuation_stage_cap=cfg.continuation_stage_cap, stable_steps=cfg.stable_steps,
                                     change_tolerance=cfg.change_tolerance,
                                     compliance_tolerance=cfg.compliance_tolerance, rho_min=cfg.rho_min, move=cfg.move,
                                     graphs=not args.no_graphs, reference_stopping=ref_stop, started_at=t0)
    optimizer_end = time.perf_counter()
    reference = ScikitFEMElasticity.from_problem(problem)
    c, _, _ = reference.evaluate(rho)
    relative = abs(c - summary["C_raw"]) / c
    if relative > 1e-6:
        raise RuntimeError(f"common-library final compliance mismatch {relative}")
    v = reference.element_volumes
    achieved = float(v @ rho / v.sum())
    if abs(achieved - problem.volume_fraction) > 1e-7:
        raise RuntimeError("final physical volume is infeasible")
    independent = reference.metadata()
    reference.close()
    torch.cuda.synchronize()
    wall = time.perf_counter() - t0
    summary.update(case=problem.name, C_raw=c, volume=achieved, wall_s=wall, optimization_end_s=optimizer_end - t0,
                   validation_s=wall - (optimizer_end - t0), independent_relative_C_error=relative,
                   independent_fem=independent, cpu_threads=args.threads, cpu_pinning=pinning,
                   hardware=torch.cuda.get_device_name(0), validate_mode=args.validate,
                   config=str(args.config), oc_config={k: (list(v) if isinstance(v, tuple) else v)
                                                       for k, v in cfg.__dict__.items()},
                   timing_scope="as hgto.linear.run: case construction, setup, optimization and the final independent "
                                "scikit-fem evaluation; imports and file output excluded")
    np.save(args.output / "rho.npy", rho)
    np.savez_compressed(args.output / "geometry.npz", **geometry)
    (args.output / "result.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    (args.output / "history.json").write_text(json.dumps(history, default=float), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("case", "C_raw", "volume", "termination", "state_evaluations", "wall_s",
                                              "setup_s", "pcg_iterations_total", "pcg_fallbacks")}, indent=2))


if __name__ == "__main__":
    main()
