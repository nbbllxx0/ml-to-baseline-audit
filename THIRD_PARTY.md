# Third-party code, data and weights

None of the following is redistributed here. Obtain each item from its source at the recorded commit.
Code without a licence file is used locally only; scripts in this repository that depend on it expect it in
the folder shown (`retest/targets/<name>` for re-tests, `v3/third_party/<name>` for the census).

| Use | Folder | Source | Commit | Licence |
|---|---|---|---|---|
| re-test | `HGTO` | https://github.com/Liukz233/HGTO | `d9828ef06ed6a75329ecb97158271e94bbaa08f2` | MIT |
| re-test | `Fourier-TOuNN` | https://github.com/UW-ERSL/Fourier-TOuNN | `fce3b8a43fa426e16be16d5a05bdb81b71a773b0` | MIT |
| re-test | `OptimizeAnyTopology` | https://github.com/ahnobari/OptimizeAnyTopology | `dc5e817497eb7d5517f93b7c79ea463ab2761082` | none (no licence file) |
| census P00080 | `VoroTO` | https://github.com/UW-ERSL/VoroTO | `d407d15d9c876338f1b47e54cb41ff9dc9dcb381` | MIT |
| census P00140 | `deep-dehom` | https://github.com/elingaard/deep-dehom | `73529a9340287a4e14a5e80250dc46fb213a866c` | none (no licence file; local use only, not redistributed) |
| census P00183 | `Theory_Driven_TO` | https://github.com/DesignInformaticsLab/Theory_Driven_TO | `02de10e0a04c334c809084a0ba4743438f7afb95` | none (no licence file; local use only, not redistributed) |
| census P00610 | `Keff-CFD` | https://github.com/adama-wzr/Keff-CFD | `48700a842afaaceef247572ddd17668d0d376548` | MIT |
| census P00610 | `CNN-Keff` | https://github.com/adama-wzr/CNN-Keff | `46ec2b6553567bc3c02092ec8022a0a51d5740b7` | none (no licence file; local use only, not redistributed) |
| census P00647 | `DL3DTO-Deep-Learning-for-3D-Topology-Optimization` | https://github.com/AshaV17/DL3DTO-Deep-Learning-for-3D-Topology-Optimization | `d9db8b2dc285ca169f15e7c0d0a77cb0c4f81ef5` | none (no licence file; local use only, not redistributed) |
| census P00663 | `DeepNNforTopoOptisation` | https://github.com/MarvinHaa/DeepNNforTopoOptisation | `6c042e57b289a29fd4703ccd35472c703266f5c1` | none (no licence file; local use only, not redistributed) |

Also not redistributed: OAT's released checkpoints https://huggingface.co/OpenTO/NFAE and
https://huggingface.co/OpenTO/LDM and the dataset https://huggingface.co/datasets/OpenTO/OpenTO (linked from the OAT
README), expected in `retest/targets/hf/NFAE`, `hf/LDM` and `hf/OpenTO_data`; and the trained predictor and validation data
of Halle et al. (2021) from the article's Mendeley deposit, expected in `retest/targets/P00150_mendeley/` (see
`plan/BASELINE_PREREG.md`, deviation log, and Online Resource 5). `retest/targets/hf_manifest.json` records the
Hugging Face revisions and file hashes used.

## Files here that contain MIT-licensed upstream code

These files include code adapted from MIT-licensed repositories; the upstream licence texts are in `licenses/`.

| File | Upstream | Licence text |
|---|---|---|
| `retest/hgto_harness/oc_gpu.py`, `retest/hgto_harness/run_ours.py`, `retest/runs/hgto/**/config.yaml` | HGTO, Kangzheng Liu, commit `d9828ef` | `licenses/HGTO-LICENSE.txt` |
| `v3/runs/P00610/strong.py`, `v3/runs/P00610/smoke/input.txt`, `v3/runs/P00610/smoke/00009.jpg` | Keff-CFD, Andre Adam, commit `48700a8` | `licenses/Keff-CFD-LICENSE.txt` |
| `v3/runs/P00080/logs/generate_dataset.json`, `v3/runs/P00080/logs/train_network.json` (notebook cells recorded in the run logs) | VoroTO, commit `d407d15` | `licenses/VoroTO-LICENSE.txt` |

## Other notes

- `retest/oat_harness/eval_designs.py`, `time_oat_simp.py` and `run_oat_inference.py` call OAT's pyEDGE and model
  API in the same order and with the same arguments as OAT's `scripts/RunComplianceTest.py` and
  `scripts/GenerateSolutions.py`, so that scores and timings match OAT's own protocol. No OAT source file is included.
- `v3/runs/P00140/dehom.py`, `v3/runs/P00183/make_logged.py`, `v3/runs/P00183/port.py` and `v3/runs/P00647/make_unit.py`
  locate the lines they patch in the upstream clones by one- or two-line anchors. The patched upstream files
  themselves (`P00183/matlab/infill_logged.m`, `compliance_eval.m`, `P00647/Top3D_maxbulk_unit.m` and their diffs)
  are not included; run these generators against the clones to rebuild them before `run_classical.m` or `unit_rows.m`.
- The classical SIMP baselines in `retest/baseline/` (`simp_cpu.py`, `simp_gpu.py`, `fem2d.py`) follow the formulation
  of the 88-line MATLAB code of Andreassen et al. (2011), https://doi.org/10.1007/s00158-010-0594-7.
- Pretrained weights and data used by the census (`v3/runs/P00140/weights/`, `v3/runs/P00610/data/`) are not
  included; each folder keeps a `PROVENANCE.json` with the source DOI and checksums.
