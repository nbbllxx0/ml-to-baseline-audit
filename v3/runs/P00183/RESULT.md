# P00183 (theory-driven one-shot generator) — census result

**Level reached: L2** (the pre-registered L2 gives no gain here). Sources: `summary.json` (from `timing/gen.json`,
`timing/classical_{L1,L2}.mat`), `train.log`, `REPAIRS.md`; protocol `v3/plan/CENSUS_PREREG.md` §9 (P00183 rows).
All runs pinned to the performance cores, 2026-09-25.

**Claim (record P00183).** The trained generator produces a topology in about 10⁻² s (Xeon E5-1620), against 10²–10³ s
for the augmented-Lagrangian TO on the 120×40 mesh; about 10⁴ faster, data acquisition excluded.

**Reproduction (L0).** Two released MATLAB files fail as published and were repaired without changing the algorithm:
the TO function never sizes its load vector, and the evaluator stops at an undefined variable after computing the
compliance (`REPAIRS.md` 2 and 5). The Python/TensorFlow 1 training code was ported with logged changes
(`work/PATCHES.diff`). Retraining took 22.4 min (5 active-learning rounds, 9 training designs from the repository's
pre-solved set, final test error 0.944 against the stopping criterion 1).

| Angle | TO, 1 thread (L1), s | FE analyses | TO compliance | Generator compliance | TO time to match the generator, s | Factor, full TO | Factor, matched quality |
|---|---|---|---|---|---|---|---|
| 16 | 115.1 | 4,741 | 166.4 | 310.8 | 57.8 | 33,615 | 16,869 |
| 62 | 110.7 | 4,635 | 34.2 | 67.0 | 56.2 | 32,331 | 16,412 |
| 75 | 115.8 | 4,711 | 107.6 | 198.7 | 57.1 | 33,829 | 16,666 |

Generator: 3.42 ms per angle (one thread, batch of 5). Times are medians of 3 repeats (spread under 2 %). Compliance
from the repository evaluator (projection β = 16). "Time to match" is the first end of a projection stage at which the TO
design's compliance is at most the generator's; the first stage end (after about 56–58 s) already does so on every angle.

**L2.** MATLAB default threading on the 6 performance cores is slower for this 9,922-DOF problem: 135.5–140.3 s per
run (matched quality 68.1–69.0 s). The TO cost is its about 4,700 FE analyses of a small system, which the census keeps
fixed; a faster solver for the same system was not tested beyond this threading change.

**Reading.** The claim's order of magnitude holds on our machine: 10⁴ at full TO time and about 1.6×10⁴ at matched
quality. The generator's designs have 1.85–1.96 times the TO compliance on these angles; the TO reaches a better design
before its second projection stage. Offline cost (derived): 22.4 min of training plus the 9 pre-solved training designs
(about 9 × 113 s = 17 min of TO) against a saving of about 57 s per design at matched quality, so the generator repays
its offline cost after about 41 designs.
