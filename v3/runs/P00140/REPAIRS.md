# P00140 — repairs and choices (census pre-registration §6.2)

1. **Weights.** figshare answers scripted downloads with a bot check (HTTP 202, empty body), which the census does
   not try to get around. The user downloaded the article's zip (`E:\DL\16902961.zip`, 8,699,051 bytes, four files);
   the extracted files match the figshare record's MD5 sums (`weights/PROVENANCE.json`).
2. **Stale notebook names.** `lam_width_projection.ipynb` imports `RBF_Upsampler` and `DotLoss` from modules that no
   longer define them. `dehom.py` uses `DehomNet` (same layers; the released weights load with matching keys and
   shapes) and `DotLoss` from `deepdehom/main.py`.
3. **Encoder folder.** `HomogenizationData` refuses an empty folder but uses the data only for training; the encoder is
   built on a folder with one placeholder file. The notebook's hard-coded path to the authors' training data is
   therefore not needed.
4. **scikit-image keyword.** `selem=` became `footprint=` (1 occurrence, `work/PATCHES.diff`, made by `port.py`); the
   pinned scikit-image 0.18.3 has no wheels for Python 3.12.
5. **Display only.** `verbose` and `enable_plot` are off in `lam.forward`; they print and plot.
6. **Seed.** The encoder adds Gaussian noise of 1° (notebook setting); numpy is seeded (20260925) before each run.
