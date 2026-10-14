# P00610 — repairs and choices (census pre-registration §6.2)

1. **Code version.** Keff-CFD commit `720be71` (2023-07-22), checked out as `v3/third_party/Keff-CFD@720be71`. It is
   the last commit before the article's Crossref record was created (2023-10-19); the 2D solver has no later change
   before 2023-11-09. HEAD (`48700a8`, 2025) is a later version with a residual-based stopping rule. Logged as a
   deviation in `v3/plan/CENSUS_PREREG.md` §9 (COMMITS.json lists HEAD).
2. **Compiler.** The code targets GCC. With MSVC 2022 (`/openmp:llvm`), `schedule(auto)` is rejected. The build copy
   `build/src/` replaces `schedule(auto)` with `schedule(static)` in 10 setup loops of `keff2D.cpp` (cell centres and
   array initialisation). Loop scheduling does not change results. `/FIstring` supplies the `<string>` header that
   GCC includes implicitly.
3. **Solver variant.** At `720be71` the single-image path calls `ParallelGS` (Gauss–Seidel). The article describes
   an iterative TDMA line sweep. `build/src_tdma/` switches the single-image call to the `TDMAscanner` function that
   the same file defines (the call is present, commented out). Both executables are kept: `keff2D_gs.exe` (code as
   released) and `keff2D_tdma.exe` (solver the article describes).

Smoke test (2026-09-25, `smoke/`, image `00009.jpg` from the repository, k_s = 10, one core, not pinned, not a timed
run): Gauss–Seidel 0.99 s, 12,800 iterations, keff 5.2974; TDMA 1.49 s, 7,300 iterations, keff 5.2990. Article Table 1
for k_s = 10: 34.2 s and 32,903 iterations per image (the images differ).
4. **Image input.** 75 of the 100 sampled dataset JPEGs (CirclePack, EllipsePack, QuadrilateralPack) are stored as
   3-channel RGB with identical channels (maximum channel difference 0); the solver rejects images with more than one
   channel. They are converted to 8-bit grayscale (exact for equal channels) and saved as PNG, so no second JPEG
   compression occurs. QSGS images are already one-channel. Same conversion for the CNN input.
