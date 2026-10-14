"""P00140 L0/L1 (ML side): the released CNN de-homogenization on the released 60×30 Michell-cantilever inputs.

    PIN_PCORES=1 v3/.venv/census-torch/Scripts/python.exe v3/runs/P00140/dehom.py

Follows the repository notebook lam_width_projection.ipynb cell by cell (commit 73529a9), with name-level repairs
(REPAIRS.md; package from port.py): RBF_Upsampler -> DehomNet (same layers; the released weights load into it), DotLoss imported from
deepdehom/main.py, the RBF encoder built from a folder holding one placeholder file, plots and verbose output off.
Weights: the figshare step-2 files for lamination periods 10 and 20 (CC BY 4.0, MD5-checked, weights/).
For each input file and period: the timed interval runs from the RBF encoding to the final fine-scale design (the
notebook's cells from 'npad = 2' to lam_proj.forward), warm-up + 3 repeats, CPU, PyTorch default threads.
Reported: time, fine-mesh shape, volume fraction V_f (mean density), homogenization V_ref and C_ref from the input.
Writes timing/dehom.json.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import statistics
import sys
import tempfile
import time

import numpy as np
import torch

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPO = ROOT / "v3" / "third_party" / "deep-dehom"
PKG = HERE / "work"                                  # port.py: deepdehom/ with selem= -> footprint=
OUT = HERE / "timing"
FILES = sorted(p.name for p in (REPO / "Output_TO").glob("michellCantileverSym_*_60_15_*.mat"))


def pin():
    spec = importlib.util.spec_from_file_location("pin", ROOT / "tools" / "pin.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.pin_from_env()


def main():
    pinning = pin()
    sys.path.insert(0, str(PKG))
    sys.path.insert(0, str(PKG / "deepdehom"))        # main.py imports 'models' and 'dataset' as top-level modules
    from deepdehom.models import DehomNet, get_net_dict
    from deepdehom.dataset import HomogenizationData
    from deepdehom.utils import LaminationWidthProjection, load_homogenization_file, get_hist_periodicity, \
        get_homogenization_volfrac
    from main import DotLoss
    device = torch.device("cpu")
    dot_loss = DotLoss()
    placeholder = tempfile.mkdtemp(dir=HERE)
    (pathlib.Path(placeholder) / "placeholder.npy").write_bytes(b"")
    datagen = HomogenizationData(placeholder, n_rbf_bins=24, std_factor=2, noise_mag=np.deg2rad(1), hvflip=False)
    results = []
    for period in (10, 20):
        model = DehomNet(get_net_dict(model_size="medium", input_dim=24), out_kernel_size=3).to(device)
        model.load_state_dict(torch.load(HERE / "weights" / f"DehomNet_step2_period{period}.pth", map_location="cpu",
                                         weights_only=True))
        model = model.eval()
        for fname in FILES:
            N1x, N1y, N2x, N2y, mu1, mu2, ref_comp = load_homogenization_file(str(REPO / "Output_TO" / fname))
            min_mu = float(fname.split("_")[-4])
            times = []
            for rep in range(4):
                np.random.seed(20260925)                # noise_mag adds Gaussian noise inside the RBF encoding
                t0 = time.perf_counter()
                npad = 2
                p = lambda a: np.pad(a, pad_width=npad, mode="edge")
                N1xp, N1yp, N2xp, N2yp = p(N1x), p(N1y), p(N2x), p(N2y)
                H1 = datagen.rbf_encoding(N1xp, N1yp).astype(np.float32)
                ex1, ey1 = N1xp.copy().astype(np.float32), N1yp.copy().astype(np.float32)
                H1, ex1, ey1 = datagen.transform(H1, ex1, ey1)
                H2 = datagen.rbf_encoding(N2xp, N2yp).astype(np.float32)
                ex2, ey2 = N2xp.copy().astype(np.float32), N2yp.copy().astype(np.float32)
                H2, ex2, ey2 = datagen.transform(H2, ex2, ey2)
                with torch.no_grad():
                    r1 = model(H1.unsqueeze(0).to(device))
                    d1_loss, d1_surf, _ = dot_loss(r1, ex1.unsqueeze(0).to(device), ey1.unsqueeze(0).to(device))
                    r2 = model(H2.unsqueeze(0).to(device))
                    d2_loss, d2_surf, _ = dot_loss(r2, ex2.unsqueeze(0).to(device), ey2.unsqueeze(0).to(device))
                r1n, r2n = r1.numpy().squeeze(0).squeeze(0), r2.numpy().squeeze(0).squeeze(0)
                s1n, s2n = d1_surf.numpy().squeeze(0).squeeze(0), d2_surf.numpy().squeeze(0).squeeze(0)
                per = get_hist_periodicity(r1n, r2n)
                lam = LaminationWidthProjection(per, hmin=3, wmin=min_mu, nn_usr=8, field_usr=5, input_pad=npad)
                rho_hr, _, _ = lam.forward((r1n, r2n), (s1n, s2n), (mu1, mu2), wmin_thres=True, refine_period=True,
                                           verbose=False, enable_plot=False)
                dt = time.perf_counter() - t0
                if rep:
                    times.append(dt)
            rho_hr = np.asarray(rho_hr)
            results.append({"file": fname, "period": period, "min_mu": min_mu, "V_ref": float(get_homogenization_volfrac(mu1, mu2)),
                            "C_ref": float(np.asarray(ref_comp).squeeze()), "fine_shape": list(rho_hr.shape),
                            "V_f": float(rho_hr.mean()), "V_f_thresholded": float((rho_hr >= 0.5).mean()),
                            "median_s": statistics.median(times), "min_s": min(times), "max_s": max(times),
                            "repeats_s": times})
            np.save(OUT / f"rho_hr_p{period}_{pathlib.Path(fname).stem[-60:]}.npy", rho_hr.astype(np.float32))
            print(json.dumps(results[-1]), flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "dehom.json").write_text(json.dumps({"meta": {"pinning": pinning, "torch": torch.__version__,
                                                         "threads": torch.get_num_threads()}, "runs": results},
                                               indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    main()
