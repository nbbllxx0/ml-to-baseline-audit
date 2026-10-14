# P00080 (VoroTO) — census result

**Level reached: L2.** Sources: `timing/{voroto,homog,cpu_iter,gpu,posthoc_threshold}.json`; protocol
`v3/plan/CENSUS_PREREG.md` §9 (P00080 rows). All runs pinned to the performance cores, 2026-09-25.

**Claim (record P00080).** On the 40×20 mid-cantilever, VoroTO optimizes in 0.24 min after a one-time 28.4 min of data
generation and training, against a projected 528 min for concurrent homogenization-based multiscale TO (2,200×) and a
projected 4,986 min for brute-force fine-scale TO at 1600×800 (20,775×). Both classical times are projections from unit
costs × 300 iterations; neither was run.

**ML side (L0).** The surrogate was retrained with the released notebooks (repair: `REPAIRS.md`): data generation
736.5 s and training 122.7 s, 14.3 min in total (article: 28.4 min). VoroTO `topopt()`: median 11.48 s (3 repeats,
11.38–11.49 s; article 0.24 min). Dehomogenization to a 1600×800 image: median 20.5 s more. Fine-scale compliance of the
thresholded images: median 88.98 at volume fraction 0.552–0.559 (homogenized J 78.74 at 0.51).

| Comparator | Article | Ours | Factor vs VoroTO 11.48 s |
|---|---|---|---|
| Concurrent homogenization, projected (unit × 800 × 300) | 0.132 s unit → 528 min | 0.0369 s unit (40×40 micro-mesh, as in data generation) → 147 min | 771 (projection) |
| Brute-force fine-scale TO, projected (one iteration × 300) | 16.62 min/iteration → 4,986 min | 90.5 s/iteration (top88-faithful CPU, SuperLU, rmin 1.5) → 453 min | 2,367 (projection) |
| **L2:** v2 GPU SIMP at 1600×800, volume fraction 0.5, rmin 18.75, to VoroTO's fine-scale compliance (pre-registered) | not run | 2.45 s (iteration 9) | **0.21** (the classical run is 4.7× faster) |
| v2 GPU SIMP, full 300 iterations | — | 67.7 s, compliance 67.2 (penalized) | 5.9 |

**Post hoc check (not pre-registered).** The pre-registered rule compares SIMP's penalized compliance with VoroTO's
thresholded one. Scoring the SIMP designs the same way (threshold 0.5, fine-scale evaluator): after 9 iterations
(2.2 s) 79.1 at volume fraction 0.477; after 20 iterations (5.0 s) 65.7 at 0.495; after 300 iterations 63.0 at 0.501.
Each is stiffer than VoroTO's 89.0 while using less material, so the match holds under the stricter scoring.

**Reading.** Run instead of projected, the classical comparators take 3.6× (homogenization) and 11× (fine-scale)
less time than the article's projections on this machine. An efficient fine-scale SIMP reaches VoroTO's structural
quality in about 2.5 s, before VoroTO finishes its own optimization and without its 14.3 min offline cost; after 67.7 s its
thresholded design has 29 % lower compliance (63.0 against 89.0) with less material. VoroTO's designs are Voronoi multiscale structures, a design
space that single-scale SIMP does not produce; the comparison is on the structural objective the article reports.
