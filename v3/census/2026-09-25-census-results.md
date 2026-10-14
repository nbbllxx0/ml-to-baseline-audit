# Re-test census of code-linked speed claims — results (2026-09-25)

**Bottom line.** Of the 7 speed claims in the analysis sample whose articles link public code, the census re-ran 6 on
one workstation; the 7th (P00150) had already stopped at its pre-registered reconstruction check in v2. The authors'
code ran for all 6; 4 needed logged repairs first. A matched-quality comparison with an efficient classical method was
possible for 4 claims: the factor shrank from thousands to 3.6 (P00610), reversed so that the classical run was 4.7×
faster (P00080), stayed about 10⁴ with designs of about twice the compliance (P00183), and was unchanged at 1.145
against the published 1.16 (P00663). For the other 2 (P00140, P00647) the released material does not allow a
matched-quality comparison; P00647's classical side is not overstated (our one-core run took longer than the
article's).

Sources: per-claim `v3/runs/<PID>/RESULT.md` and `REPAIRS.md`; protocol `v3/plan/CENSUS_PREREG.md` (frozen before the
runs; every later decision in its §9, logged before the run it governs); integrity `v3/evidence/MANIFEST.sha256`.

## 1. Frame and levels

The frame is every speed-stratum record of the analysis sample (adjudicated coding) with public code: 7 claims
(`v3/census/frame.md`). Levels: L0 the article's code runs; L1 the article's own comparison on our machine; L2 the
classical comparator with an efficient solver or device, compared at matched quality.

| PID | Method | Published factor | Level | Result |
|---|---|---|---|---|
| P00610 | CNN for effective conductivity (Keff) | 2,280–24,747 | L2 | L1 320–1,112; **L2 3.6** (direct solve of the same equations, more accurate than the CNN) |
| P00080 | VoroTO multiscale Voronoi TO | 2,200 and 20,775 (both projected) | L2 | projections recomputed 771 and 2,367; **L2 0.21**: GPU SIMP reaches VoroTO's quality 4.7× faster than VoroTO |
| P00183 | Theory-driven one-shot generator | about 10⁴ | L2 (no gain) | 3.2–3.4×10⁴ full, 1.6–1.7×10⁴ at matched quality; generator designs have 1.85–1.96× the TO compliance |
| P00663 | CNN gradient steps in phase-field TO | 1.16 | L2 = L1 | **1.145**; iterations and compliances reproduced to the last reported digit |
| P00140 | CNN de-homogenization | 5–10 (against a comparator that is not public) | L0; L1/L2 time only | CNN times and volume fractions reproduced; GPU SIMP at 1440×720 runs the article's 1,000 iterations in 1,546 s against its 16,000 s projection; quality comparison not possible |
| P00647 | 3D TPMS unit-cell ResUNet (DL3DTO) | 2,400 | L1 partial; L2 projection | classical run ≥ 8.9 h on one core (stopped at 253 iterations, not converged) against the article's 2.4 h; 6 threads 3.3× faster; no model released, so no matched-quality comparison |
| P00150 | Predictor of Halle et al. | 259 | stopped in v2 | reconstruction check failed (57 of 100 within 1 %, 95 required); not re-run |

## 2. P00647

The released MATLAB code runs unchanged. One run on one core (row 438) was stopped by user decision after 253
iterations and 8.9 h without meeting its stopping rule (design change 0.014–0.026 over the last 38 iterations,
threshold 0.01, cap 600); the other two pre-registered rows were not run. A clean 10-iteration measurement gives
120.0 s per iteration on one thread and 36.5 s with six threads (identical iterates). The classical side of the
claim is therefore not overstated: the published 2.4 h is shorter than our one-core run, and threading only brings
the run back to about that figure. The claim cannot be tested at matched quality because no trained model is
released and the article scores predictions by voxel agreement only (`v3/runs/P00647/RESULT.md`).

## 3. What the census shows

1. **The code runs, mostly not as released.** Four of the 6 needed repairs before they ran on current software:
   dependency renames (scikit-image, TensorFlow 1, a KLU extension), stale notebook names, a C++ OpenMP keyword, and
   in P00183 two MATLAB files that fail as published (an unsized load vector and an undefined variable in the
   evaluator). P00663 ran unchanged once its environment was rebuilt (the released environment file is a macOS export
   and the FEniCS image can no longer be pulled); P00647's MATLAB code ran unchanged. None of the repairs changed an
   algorithm (`REPAIRS.md` per claim). Three claims had released weights; two were retrained within the 1 GPU-hour
   budget (P00080 in 14.3 min, P00183 in 22.4 min); for P00647 neither weights nor data were released.
2. **Where the published factors come from.** In three of the four claims with factors above 1,000 the size rests on
   the classical side or on unequal quality: projections instead of runs (both P00080 comparators), classical
   timings far slower than the same released code on our machine (P00610: 12–38×), and designs of
   different quality (P00183's generator designs have about twice the TO compliance). P00647 is the exception: its
   classical run takes longer here than the article reports.
3. **What an efficient classical baseline changes.** Where the classical side is an inefficient solver of the same
   equations (P00610) or a projection of an unrun computation (P00080), an efficient implementation removes most or
   all of the advantage. Where the classical side is already a sparse direct solve (P00663) or is bound by an
   algorithm with thousands of small solves (P00183), it does not.
4. **Claims that hold.** P00663's modest 1.16× holds (1.145). P00183's order of magnitude holds on time, with a
   quality gap that the article's own metric leaves visible.

## 4. Limits

1. One workstation (i5-14600KF, RTX 5090); P00663 ran in Docker and could not be pinned to the performance cores.
2. Some runs overlapped: the single-threaded P00647 MATLAB run ran alongside the P00140 and P00663 runs, and the
   P00140 GPU runs alongside P00663. Overlaps can slow either side; all are logged (`v3/runs/P00647/CONCURRENT.log`,
   §9). P00610, P00080 and P00183 ran with nothing else on the machine.
3. Retrained models (P00080, P00183) may differ from the authors'; both met the released stopping criteria.
4. P00140's supports and quality evaluation are not stated in the article text; P00647's ML side is published only.
5. The census covers 7 claims; it describes those claims and estimates no rate.

## 5. Draft text (superseded)

The census is now integrated into the v3 manuscript (`v3/manuscript/`, Sects. 2.6 and 3.7, Table 4, Online
Resource 6), which is the version to submit. The drafts below were the starting point; the manuscript text governs.

**Methods (after Sect. 2.6).** To remove the choice of re-test targets, we re-tested every speed claim in the analysis
sample whose article links public code (7 claims). The procedure was pre-registered before the first run: each claim
is taken as far as it goes, from running the authors' code (L0), to the article's own comparison on our machine (L1),
to the same classical method with an efficient solver or device at matched quality (L2). Repairs were limited to
dependency versions, file paths and removed library calls; missing trained models were retrained only within one
GPU-hour; every deviation is logged with its date in Online Resource 6.

**Results (new subsection).** The authors' code ran for all six claims; four needed repairs first, none of which
changed an algorithm, and two released MATLAB files did not run as published. The seventh had stopped at its
reconstruction check (Sect. 2.6). On the article's own comparison, the published factors ranged from reproduced (1.145 against 1.16) to
overstated through projected or slow classical timings (320–1,112 against 2,280–24,747; 771 and 2,367 against 2,200
and 20,775). At matched quality against an efficient classical method, the factor fell to 3.6 in one claim and
reversed in another (the classical run was 4.7× faster), stayed about 10⁴ in a third whose designs had about twice
the compliance, and was unchanged in the fourth. In two claims the released material did not allow a matched-quality
comparison; in one of them the classical run took longer on our machine than the article reports.
