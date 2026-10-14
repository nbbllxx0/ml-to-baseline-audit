# Census status (updated by hand; results live in v3/runs/<PID>/RESULT.md; summary: 2026-09-25-census-results.md)

| PID | Level reached | Published factor | Our result | State |
|---|---|---|---|---|
| P00610 CNN-Keff | L2 | 2,280–24,747 | L1 320–1,112; L2 3.6 at matched quality | done |
| P00080 VoroTO | L2 | 2,200 and 20,775 (projections) | projections recomputed 771 and 2,367; L2 0.21 (the classical run is 4.7× faster at matched quality) | done |
| P00183 Theory-driven TO | L2 (no gain) | about 10⁴ | L1 3.2–3.4×10⁴ full, 1.6–1.7×10⁴ at matched quality; generator designs 1.85–1.96× the TO compliance | done |
| P00663 DeepNN phase-field | L2 = L1 | 1.16 | 1.145, iterations and compliance reproduced exactly | done |
| P00140 deep-dehom | L0; L1/L2 time only at 1440×720 | 5–10 (cross-paper) | CNN reproduces times and V_f; least-squares comparator not public; GPU SIMP 1,000 iterations at 1440×720 in 1,546 s vs article projection 16,000 s; 2400×1200 does not fit this machine; matched quality blocked | done |
| P00150 Halle et al. (predictor) | stopped in v2 | 259 | reconstruction check failed (57 of 100 within 1 %, 95 required); not re-run | done (v2) |
| P00647 DL3DTO | L1 partial; L2 projection | 2,400 | one-core run stopped at 253 iterations after 8.9 h (not converged; article 2.4 h); 120.0 s vs 36.5 s per iteration on 1 vs 6 threads; no model released, matched quality impossible | done (stopped by user decision, §9 dev17) |
