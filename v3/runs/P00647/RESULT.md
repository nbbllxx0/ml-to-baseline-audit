# P00647 (DL3DTO, 3D TPMS unit cell) — census result

**Level reached: L1 partial, L2 as a projection; matched quality not possible.** Sources: `summary.json`,
`run_L1.log`, `unit_1thread.log`, `unit_default.log`; protocol `v3/plan/CENSUS_PREREG.md` §9 (P00647 rows, dev17).

**Claim (record P00647).** Once trained, the 3D ResUNet predicts an optimized 32³ gyroid unit cell in 0.001 CPU-hours,
against about 2.4 h per homogenization-based SIMP run on one HPC core: 2,400× (derived). Quality is judged only by voxel
MSE and Dice (rule R4 fail).

**ML side.** No trained weights and no data are released; training took 5.5 GPU-hours plus 2,751 TO runs, beyond the
1 GPU-hour budget. The prediction time stays as published (3.6 s).

**Classical side (L0, L1).** The repository's MATLAB code (`Top3D_maxbulk.m`) runs unchanged. On row 438 of the
released parameter table, one core, it ran from 10:22:08 to 19:16:43 (32,075 s) and was stopped after 253 iterations
by user decision; it had not met its stopping rule (design change below 0.01): the change oscillated between 0.014
and 0.026 over iterations 216–253, and the loop cap is 600. Rows 1696 and 2082 were not run. The long run overlapped
other jobs; a clean 10-iteration run of the same row gives a median of 120.0 s per iteration (iterations 2–10), close
to the long run's average of 126.8 s.

**L2 (projection).** The same code with MATLAB default threading (6 threads) follows the identical trajectory (same
objective values) at a median of 36.5 s per iteration, 3.3× faster than one thread. Over the 253 iterations that
reached, that is about 9,245 s (2.6 h); to the 600-iteration cap, about 21,900 s (6.1 h).

| | Article | Ours |
|---|---|---|
| Classical run, one core | 2.4 h | ≥ 8.9 h (253 iterations, not converged); about 20 h to the cap (projection, 600 × 120.0 s) |
| Classical run, 6 threads | — | about 2.6 h for the same 253 iterations (projection) |
| ML prediction | 0.001 CPU-h (3.6 s) | not reproducible (no weights) |
| Factor | 2,400 | ≥ 8,900 on one core; about 2,570 with 6 threads over 253 iterations (projections, against the published 3.6 s) |

**Reading.** The classical side of this claim is not overstated: on this machine a run of the released code takes
longer than the article's 2.4 h, and threading brings it back to about the article's figure. The claim cannot be
tested at matched quality: the authors release no model, and they score predictions by voxel agreement, not by the
bulk or shear modulus the optimization maximizes. The released code also differs from the article's text (no Heaviside
continuation, a 600-iteration cap; record P00647), which may explain the longer run.
