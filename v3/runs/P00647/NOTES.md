# P00647 — run notes

- Smoke test 2026-09-25 (`smoke/smoke.m`, row 1 of `vfrmin.mat`: vf 0.25, rmin 1.2; `maxNumCompThreads(1)`; not
  pinned, not timed): the repository's `Top3D_maxbulk.m` runs unchanged under MATLAB R2023b. Iteration 1 printed
  "Obj. -2.1437, Micro_Vol. 0.470" within the 420 s window, which includes MATLAB start-up and filter setup. L0 for
  the classical side: reached. ML side: published (no weights, no data; pre-registration §7).
- Sample for L1/L2: rows 438, 1696, 2082 (pre-registration §9).
