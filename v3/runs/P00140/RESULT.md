# P00140 (CNN de-homogenization) — census result

**Level reached: L0; L1 and L2 partial (time only, 1440×720 only).** Sources: `timing/dehom.json`,
`timing/classical_1440.json`; protocol `v3/plan/CENSUS_PREREG.md` §9 (P00140 rows, dev10, dev15, dev16).

**Claim (record P00140).** CNN de-homogenization of a 60×30 homogenization result takes about 1.3 s (to 1440×720) and
2.2 s (to 2400×1200) on one Intel Core i7 CPU, against about 10 s for least-squares de-homogenization (a cross-paper
figure, 80×40 to 1600×800): 5–10× (derived). The article also projects top88 at the fine meshes: 16 s and 87 s per
iteration × about 1,000 iterations = 16,000 s and 87,000 s.

**Reproduction (L0).** The released pipeline with the released weights (repairs: `REPAIRS.md`) on the 8 released
60×30 Michell inputs produces 2400×1200 designs in 1.69–1.94 s (period 10) and 2.05–2.10 s (period 20), medians of 3
(article: 2.16–2.23 s at 2400×1200). Volume fractions match Table 2 within 0.006 (period 20: 0.2693 against 0.2695 for
μ_min 0.05, 0.4375 against 0.4389 for μ_min 0.20).

**L1.** The least-squares de-homogenization is not public; its 10 s is a figure from another paper and is not re-run.
One iteration of our top88-faithful CPU port (SuperLU) at 1440×720 takes 75.9 s (median of 3), slower than the article's
16 s for top88, so it does not reduce the article's projection.

**L2 (time only).** The v2 GPU SIMP runs 1,000 iterations at 1440×720 in 1,546 s (median of 3; 1,536–1,566 s), against
the article's projected 16,000 s. At 2400×1200 neither classical measurement fits this machine (the SuperLU run exited during
setup, memory suspected but not confirmed; the GPU run exceeded 18 s per iteration, consistent with memory above 32 GB), so the 87,000 s projection is not re-checked.

**Matched quality: not reached.** The supports of the test problems are given only in a figure, and the article does
not describe how the fine-scale compliance of a design is evaluated; the census does not reconstruct either.

**Reading.** The article's headline factor (5–10× against least-squares de-homogenization) cannot be re-tested because
that comparator is not public. The CNN pipeline reproduces its reported times and volume fractions. Against fine-scale
SIMP, an efficient GPU run cuts the article's top88 projection at 1440×720 by about 10×, but the CNN (1.28 s at 1440×720 in the
article; 1.7–2.1 s at 2400×1200 here) remains about three orders of magnitude faster in time; whether the designs are of comparable quality is not measured.
The coarse homogenization-based optimization that feeds the CNN is not public and is not counted on either side.
