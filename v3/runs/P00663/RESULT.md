# P00663 (CNN gradient steps in phase-field TO) — census result

**Level reached: L2 = L1.** Sources: `summary.json`, `results/*.json`; protocol `v3/plan/CENSUS_PREREG.md` §9 (P00663
rows). Runs in Docker (`census-p00663:3`), 2026-09-25; not pinned to the performance cores (see §9).

**Claim (record P00663).** On the deterministic 2D bridge under the nominal load, inserting CNN-predicted gradient
steps every 55 iterations cut convergence from 538 to 441 iterations, with lower compliance (1148.66 against
1173.22), in 4 min 05 s against 4 min 43 s (averages of 10 runs): 1.16× (derived).

**Reproduction (L0).** The FEniCS 2019.1 code and the released CNN weights run unchanged in a Linux environment built
from the repository's package versions (`env/`). Both runs reproduce the article to the last reported digit: classical
538 iterations, compliance 1173.23; CNN-assisted 441 iterations, compliance 1148.66.

| | Article (Table 1, Table 4) | Ours (median of 3; repeats) |
|---|---|---|
| Classical loop (Algorithm A1) | 538 iterations, 283 s | 538 iterations, 48.97 s (48.87, 49.39, 48.97) |
| CNN-assisted loop (Algorithm 1) | 441 iterations, 245 s | 441 iterations, 42.76 s (42.76, 43.25, 42.42) |
| Ratio | 1.155 | **1.145** |

**L2.** The classical loop solves every system with UMFPACK, a sparse direct solver, which rule R2 counts as efficient;
no stronger solver is substituted, so L2 equals L1.

**Reading.** The claim holds: the CNN steps save 18 % of the iterations and 13 % of the time, and the design has 2 %
lower compliance. The absolute times are 5.8 and 5.7 times shorter than the article's on this machine; the comparison is between
two variants of the same code on the same machine, so the ratio carries over. Data generation and training are not
reported by the article and are not counted here.
