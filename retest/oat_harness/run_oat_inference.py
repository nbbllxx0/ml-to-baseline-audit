"""Time OAT inference on NITO_test problems on this machine and save the generated designs.

Run in the torch-only process type (no CuPy):
    source retest/oat_harness/env.sh
    "$OAT_PY" -m retest.oat_harness.run_oat_inference --size 256 --k 5

It mirrors OAT's scripts/GenerateSolutions.py:
  * the same dataset wrapper and collators;
  * NFAE and CTOPUNet loaded in bfloat16;
  * the OATPipeline;
  * 20 sampling steps;
  * classifier-free guidance 1.0.
Timing follows OAT Table 6: one sample per problem, DDIM (ddpm=False), averaged over repeats.
Checkpoints load from the verified local copies (retest/targets/hf, SHA-256 in hf_manifest.json), fully
offline. torch.compile is optional (--compile), because OAT compiles modules; failures are recorded.
Output: retest/runs/<stamp>_oat_infer_n<size>/ with timings.json and generated_<id>.npz.
--power (a separate energy run, not a timing run): a 5 s idle trace, then nvidia-smi board power sampled every 100 ms
around each problem's timed repeats; energy per design = window integral / repeats (plan/BASELINE_PREREG.md §5).
"""
import contextlib
import argparse
import datetime as dt
import json
import pathlib
import sys
import time
import traceback

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retest.oat_harness.problems import load_split, select  # noqa: E402

HF = ROOT / "retest" / "targets" / "hf"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, required=True)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--repeats", type=int, default=10, help="OAT Table 6: 10-run average")
    ap.add_argument("--compile", action="store_true")
    ap.add_argument("--seed", type=int, default=20260924)
    ap.add_argument("--power", action="store_true", help="sample GPU board power (energy run)")
    args = ap.parse_args()
    from tools.pin import pin_from_env
    args.cpu_pinning = pin_from_env()          # PIN_PCORES=1: performance cores, high priority (BASELINE_PREREG §9)

    import torch
    from datasets import Dataset
    from datasets import Image as HFImage
    from OAT.Models import NFAE, CTOPUNet
    from OAT.Pipelines import OATPipeline, DDIMPipeline
    from OAT.DataUtils import OpenTO, NFAECollator, DiffusionCollator
    torch.set_float32_matmul_precision("high")

    rows = load_split("NITO_test")
    ids = select(rows, args.size, args.size, args.k)
    sub = []
    for i in ids:
        r = dict(rows[i])
        r["topology"] = {"bytes": r["topology"]["bytes"], "path": None}
        sub.append(r)
    data = Dataset.from_list(sub).cast_column("topology", HFImage())   # decode as load_dataset("parquet") would
    dataset = OpenTO(data, full_sampling=True)
    collator = DiffusionCollator(unconditional_prob=0.0, inference=True,
                                 inference_collator=NFAECollator(zero_centering=False, full_sampling=True,
                                                                 coords_only=True))
    AE = NFAE.from_pretrained(str(HF / "NFAE")).to(torch.bfloat16).cuda().eval()
    LDM = CTOPUNet.from_pretrained(str(HF / "LDM")).to(torch.bfloat16).cuda().eval()
    compile_note = "not requested"
    if args.compile:
        try:
            AE.decoder.compile()
            for name, module in LDM.named_modules():
                if "problem_encoder" not in name and len(list(module.children())) == 0:
                    module.compile()
            compile_note = "compiled (OAT's per-module compile)"
        except Exception as exc:
            compile_note = f"compile failed: {type(exc).__name__}: {exc}"
    pipe = OATPipeline(diffusion_model=LDM, nfae=AE, DDIM=DDIMPipeline())

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "retest" / "runs" / (f"{stamp}_oat_infer_n{args.size}{'_compiled' if args.compile else ''}"
                                      f"{'_power' if args.power else ''}")
    out.mkdir(parents=True)
    idle_w = None
    if args.power:
        from tools.energy import PowerSampler, idle_power
        idle_w = idle_power(5.0, out / "idle_power.csv")
    timings = []
    for j, pid in enumerate(ids):
        conditions, ae_batch = collator([dataset[j]])
        conditions, ae_batch = conditions.to("cuda"), ae_batch.to("cuda")
        rec = {"problem_id": pid}
        try:
            def once(seed):
                with torch.no_grad(), torch.amp.autocast(device_type="cuda", dtype=torch.bfloat16):
                    return pipe.inference(neural_field_inputs=ae_batch, conditions=conditions, verbose=False,
                                          n_samples=1, num_sampling_steps=args.steps, classifier_free_guidance=1.0,
                                          ddpm=False, clamp_latents=False, remap_latents=False, random_seed=seed)
            once(args.seed)                              # warm-up (and compile, if requested)
            torch.cuda.synchronize()
            ts = []
            gen = None
            with (PowerSampler(out / f"power_{pid}.csv") if args.power else contextlib.nullcontext()) as ps:
                for r in range(args.repeats):
                    torch.cuda.synchronize()
                    t0 = time.perf_counter()
                    gen = once(args.seed + r)
                    torch.cuda.synchronize()
                    ts.append(time.perf_counter() - t0)
            if args.power:
                rec["energy"] = {"idle_w": idle_w, "repeats": args.repeats, "window_s": ps.t_stop - ps.t_start,
                                 "board_j_per_design": ps.energy_j() / args.repeats,
                                 "above_idle_j_per_design": ps.energy_j(subtract_w=idle_w) / args.repeats}
            sample = gen[0][0]
            while isinstance(sample, (list, tuple)):          # OATPipeline returns nested lists of tensors
                sample = sample[0]
            arr = sample.float().cpu().numpy().squeeze()
            struct = type(gen).__name__ + "/" + type(gen[0]).__name__ + "/" + type(gen[0][0]).__name__
            np.savez_compressed(out / f"generated_{pid}.npz", x=arr)
            rec.update({"times_s": ts, "median_s": float(np.median(ts)), "mean_s": float(np.mean(ts)),
                        "shape": list(arr.shape), "output_structure": struct,
                        "value_range": [float(arr.min()), float(arr.max())]})
            print(f"problem {pid}: median {np.median(ts):.3f} s  mean {np.mean(ts):.3f} s  shape {arr.shape}", flush=True)
        except Exception as exc:
            rec["error"] = f"{type(exc).__name__}: {exc}"
            rec["traceback"] = traceback.format_exc()[-3000:]
            print(f"problem {pid}: ERROR {rec['error'][:200]}", flush=True)
        timings.append(rec)
        (out / "timings.json").write_text(json.dumps({"config": {**vars(args), "problem_ids": ids,
                                                                 "compile": compile_note,
                                                                 "torch": torch.__version__,
                                                                 "device": torch.cuda.get_device_name(0)},
                                                      "results": timings}, indent=1), encoding="utf-8")
    print("run dir:", out.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
