# P00610 (CNN-Keff) — census result

**Level reached: L2.** Sources: `summary.json` (from `timing/*.json` and `validate/results.csv`), protocol in
`v3/plan/CENSUS_PREREG.md` §9. All timed processes pinned to the performance cores, one thread, 2026-09-25.

**Claim (record P00610).** The CNN predicts k_eff of a 128×128 image in 15 ms (GPU), "3 to 5 orders of magnitude
faster" than the finite-volume (NHT) simulation; Table 1 gives 34.2–371.2 s per image per core.

**Fidelity check (L0).** On 100 of the authors' own images × 4 ratios, the article-era solver reproduces the published
k_eff (median absolute relative difference 0.02–0.33 % for TDMA at the released tolerance). A direct solve of the same
finite-volume system reproduces them to 1.3e-7–4.3e-6 (median), so the discretization is identical. The released
iterative solvers stop early on some images (up to 20 % off); the published values were computed to tighter
convergence than the released default.

| k_s | Published factor (Table 1 CPU ÷ 15 ms GPU) | Article solver (TDMA), s | CNN, 1 CPU thread, s | L1 factor | Direct solve (SuperLU), s | L2 factor at matched quality |
|---|---|---|---|---|---|---|
| 10 | 2,280 | 2.81 | 0.0088 | 320 | 0.0321 | 3.65 |
| 50 | 5,440 | 4.23 | 0.0089 | 477 | 0.0320 | 3.60 |
| 100 | 9,153 | 5.47 | 0.0088 | 622 | 0.0318 | 3.61 |
| 341.7 | 24,747 | 9.82 | 0.0088 | 1,112 | 0.0318 | 3.59 |

Medians over 12 images of the median of 3 repeats. The released Gauss–Seidel solver gives L1 factors of 211–797.

**Quality.** Median error against the published k_eff: CNN 0.14–0.91 % (95th percentile up to 2.35 %); direct solve
below 1e-5. The direct solve is at least as accurate as the CNN at every ratio, so the L2 factor is at matched (or
better) quality.

**Reading.** Most of the published factor comes from the classical side: the same released solver runs 12–38 times
faster here than Table 1 reports (hardware and tolerance differ; the article names no CPU for Table 1), and an
iterative line solver is replaced by a direct solve. Against an efficient solve of the same equations, the CNN keeps a
3.6-fold per-image advantage on one core, before counting its 520,000 training simulations and training.

**Not measured.** The CNN on a GPU (TensorFlow has no GPU support on native Windows); the published 15 ms is kept as
published. A 1-thread CPU CNN (8.8 ms) is faster than the published GPU time, so this does not favour the classical side.
