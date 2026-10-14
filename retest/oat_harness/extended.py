"""Post hoc extension of the OAT re-test: more problems and several OAT sampling seeds (reviewer-style audit, 2026-09-25).

The pre-registered re-test (five seeded problems per size, one OAT sample each) stays the primary result. This
extension adds 20 problems per size, drawn with a new seed and disjoint from the primary five, and scores every
problem (primary five and new twenty) with 5 OAT sampling seeds. It reuses the harness functions unchanged:
OAT inference as in run_oat_inference.py, the strong baseline at the fixed budgets of time_to_quality.py, and OAT's
own evaluator from eval_designs.py. Every timed step runs with PIN_PCORES=1 (tools/pin.py).

    source retest/oat_harness/env.sh; export PIN_PCORES=1
    python -m retest.oat_harness.extended ids   --size 256                       # any env; writes the run dir
    "$OAT_PY" -m retest.oat_harness.extended infer --run <dir>                  # oat env, torch-only process
    <torch5090> -m retest.oat_harness.extended ttq   --run <dir>                 # strong baseline, GPU
    OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.extended score --run <dir>       # oat env, CuPy process

Output in retest/runs/<stamp>_oat_extended_n<size>/: ids.json, infer.json (+ generated_<pid>_s<seed>.npz),
ttq_runs.json (+ design_<pid>_it<K>.npz), scores.json.
"""
import argparse
import datetime as dt
import json
import pathlib
import random
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.oat_harness.problems import SEED, load_split, select  # noqa: E402

EXT_SEED = 20260925          # new problem draw, disjoint from the primary five (drawn with SEED)
N_NEW = 20
OAT_SEEDS = [20260924 + 1000 * i for i in range(1, 6)]
BUDGETS = [5, 10, 15, 20, 30, 40, 50, 75, 100, 150]      # as time_to_quality.py
HF = ROOT / "retest" / "targets" / "hf"


def ids(args):
    from PIL import Image
    import io
    rows = load_split("NITO_test")
    primary = select(rows, args.size, args.size, 5, seed=SEED)
    pool = [i for i, r in enumerate(rows)
            if Image.open(io.BytesIO(r["topology"]["bytes"])).size == (args.size, args.size) and i not in primary]
    new = sorted(random.Random(EXT_SEED).sample(pool, N_NEW))
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "retest" / "runs" / f"{stamp}_oat_extended_n{args.size}"
    out.mkdir(parents=True)
    (out / "ids.json").write_text(json.dumps({"size": args.size, "primary": primary, "new": new,
                                              "problem_seed": EXT_SEED, "pool_size": len(pool) + len(primary),
                                              "oat_seeds": OAT_SEEDS, "budgets": BUDGETS}, indent=1), encoding="utf-8")
    print(out.relative_to(ROOT).as_posix())


def load_ids(run):
    meta = json.loads((pathlib.Path(run) / "ids.json").read_text(encoding="utf-8"))
    return meta, meta["primary"] + meta["new"]


def infer(args):
    from tools.pin import pin_from_env
    pinning = pin_from_env()
    import torch
    from datasets import Dataset
    from datasets import Image as HFImage
    from OAT.Models import NFAE, CTOPUNet
    from OAT.Pipelines import OATPipeline, DDIMPipeline
    from OAT.DataUtils import OpenTO, NFAECollator, DiffusionCollator
    torch.set_float32_matmul_precision("high")
    d = pathlib.Path(args.run)
    meta, pids = load_ids(d)
    rows = load_split("NITO_test")
    sub = []
    for i in pids:
        r = dict(rows[i])
        r["topology"] = {"bytes": r["topology"]["bytes"], "path": None}
        sub.append(r)
    dataset = OpenTO(Dataset.from_list(sub).cast_column("topology", HFImage()), full_sampling=True)
    collator = DiffusionCollator(unconditional_prob=0.0, inference=True,
                                 inference_collator=NFAECollator(zero_centering=False, full_sampling=True,
                                                                 coords_only=True))
    AE = NFAE.from_pretrained(str(HF / "NFAE")).to(torch.bfloat16).cuda().eval()
    LDM = CTOPUNet.from_pretrained(str(HF / "LDM")).to(torch.bfloat16).cuda().eval()
    pipe = OATPipeline(diffusion_model=LDM, nfae=AE, DDIM=DDIMPipeline())
    out = []
    for j, pid in enumerate(pids):
        conditions, ae_batch = collator([dataset[j]])
        conditions, ae_batch = conditions.to("cuda"), ae_batch.to("cuda")

        def once(seed):
            with torch.no_grad(), torch.amp.autocast(device_type="cuda", dtype=torch.bfloat16):
                return pipe.inference(neural_field_inputs=ae_batch, conditions=conditions, verbose=False,
                                      n_samples=1, num_sampling_steps=20, classifier_free_guidance=1.0,
                                      ddpm=False, clamp_latents=False, remap_latents=False, random_seed=seed)
        once(OAT_SEEDS[0])                                   # warm-up per problem, as run_oat_inference.py
        torch.cuda.synchronize()
        for s in OAT_SEEDS:
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            gen = once(s)
            torch.cuda.synchronize()
            t = time.perf_counter() - t0
            sample = gen[0][0]
            while isinstance(sample, (list, tuple)):
                sample = sample[0]
            np.savez_compressed(d / f"generated_{pid}_s{s}.npz", x=sample.float().cpu().numpy().squeeze())
            out.append({"problem_id": pid, "seed": s, "time_s": t, "primary": pid in meta["primary"]})
            print(f"problem {pid} seed {s}: {t:.3f} s", flush=True)
    (d / "infer.json").write_text(json.dumps({"cpu_pinning": pinning, "torch": torch.__version__,
                                              "device": torch.cuda.get_device_name(0), "results": out}, indent=1),
                                  encoding="utf-8")


def ttq(args):
    from tools.pin import pin_from_env
    pinning = pin_from_env()
    import torch
    from retest.baseline import simp_gpu
    from retest.oat_harness.problems import to_fem2d
    d = pathlib.Path(args.run)
    meta, pids = load_ids(d)
    rows = load_split("NITO_test")
    recs = []
    for pid in pids:
        prob = to_fem2d(rows[pid])
        simp_gpu.run(prob, iters=10, return_x=True)             # warm-up, as time_to_quality.py
        for K in BUDGETS:
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            rec, _, _, x = simp_gpu.run(prob, iters=K, return_x=True)
            torch.cuda.synchronize()
            wall = time.perf_counter() - t0
            np.savez_compressed(d / f"design_{pid}_it{K:03d}.npz", x_pyedge=x.reshape(prob.nely, prob.nelx).T.reshape(-1))
            recs.append({"problem_id": pid, "iters": K, "loop_s": rec["t_total"], "wall_incl_setup_s": wall})
            print(f"problem {pid} K={K:3d}: wall {wall:.3f} s", flush=True)
    (d / "ttq_runs.json").write_text(json.dumps({"cpu_pinning": pinning, "solver": "gpu", "runs": recs}, indent=1),
                                     encoding="utf-8")


def score(args):
    from retest.oat_harness.eval_designs import evaluator, compliance
    from retest.oat_harness.problems import topology_array
    d = pathlib.Path(args.run)
    meta, pids = load_ids(d)
    rows = load_split("NITO_test")
    out = []
    for pid in pids:
        problem, _ = evaluator(rows[pid])
        c_gt = compliance(problem, (topology_array(rows[pid]) > 0).astype(np.float64))
        entry = {"problem_id": pid, "primary": pid in meta["primary"], "c_gt": c_gt,
                 "vf_target": float(rows[pid]["volume fraction"]), "oat": {}, "ours": {}}
        for s in meta["oat_seeds"]:
            x = np.asarray(np.load(d / f"generated_{pid}_s{s}.npz")["x"], dtype=np.float64)
            c = compliance(problem, x)
            entry["oat"][str(s)] = {"CE_pct": (c - c_gt) / c_gt * 100.0, "vf_thresholded": float((x.reshape(-1) > 0.5).mean())}
        for K in meta["budgets"]:
            x = np.load(d / f"design_{pid}_it{K:03d}.npz")["x_pyedge"]
            c = compliance(problem, x)
            entry["ours"][str(K)] = {"CE_pct": (c - c_gt) / c_gt * 100.0, "vf_thresholded": float((x > 0.5).mean())}
        out.append(entry)
        print(f"problem {pid}: OAT CE {[round(v['CE_pct'], 2) for v in entry['oat'].values()]}", flush=True)
    (d / "scores.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["ids", "infer", "ttq", "score"])
    ap.add_argument("--size", type=int)
    ap.add_argument("--run")
    args = ap.parse_args()
    {"ids": ids, "infer": infer, "ttq": ttq, "score": score}[args.mode](args)


if __name__ == "__main__":
    main()
