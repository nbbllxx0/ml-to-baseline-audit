# Fair-comparison checklist for ML-for-TO speed and quality claims (draft)

Draft from the protocol rules (`plan/PROTOCOL.md` §5, R1–R4) and from what the OAT re-test needed
(`plan/BASELINE_PREREG.md` §9). The manuscript's recommendation section uses it (evidence map §5). Each item says what
to report and why. The "Seen in this study" lines point to evidence, not to any author's intent.

## A. The classical baseline (R2)

1. **Use a strong, current classical method.** A sparse direct solver such as PARDISO or CHOLMOD, or a multigrid-
   preconditioned iterative solver. Run it on a GPU when the ML method runs on a GPU. A straight port of an
   educational MATLAB code is not a strong baseline.
   - Seen in this study: at 256², a matrix-free multigrid PCG on the GPU ran 150 SIMP iterations in 4.3–4.5 s. OAT's
     paper reports 68.30 s for its GPU SIMP (evidence `g2_provisional.json`).
2. **Name the configuration.** Solver, preconditioner, tolerance, optimizer, filter and iteration count, so a reader can
   rerun it.
   - Seen in this study: pyEDGE's CG option with default tolerance gave visibly worse designs than an exact solve
     (compliance error +10.8 % against −8.2 % on problem 1015).
3. **Check that the baseline's solves are accurate.** Report the true residual, not only the solver's own estimate.

## B. Timing (R1, R2)

4. **Same machine, or hardware stated per method.** Give the GPU, the CPU, library versions and the power mode.
5. **Timing protocol.** Warm-up excluded and reported; repeats; median and spread; whether setup is inside the timed
   interval.
6. **Control CPU placement on hybrid CPUs.** Pin every timed process to the same cores.
   - Seen in this study: on a 6+8-core CPU, the same inference took 0.44 s pinned and 1.02 s unpinned, minutes apart.
     A CPU sparse solver took 13.6 s pinned and 50 s unpinned (BASELINE_PREREG §9).
7. **Compare at matched quality, not at a fixed iteration count.** Report the classical method's time to reach the ML
   output's quality, under the same evaluator and without more material.
   - Seen in this study: OAT's median advantage was 17.9× at a fixed 150 iterations and 3.5× at matched quality (256²).
     At 64² the classical baseline was faster at matched quality.

## C. Cost accounting (R3)

8. **Report the offline cost.** Data generation and training, in device-hours with the hardware named.
9. **Report the break-even number of uses**, τ = C_train / (C_SIMP − C_inference). Use the stated inputs and C_SIMP
   from the strong baseline at matched quality.
   - Seen in this study: with OAT's formula and training cost, τ moved from 0.23 million uses (its own Table 6) to 13.7
     million (same machine, matched quality, 256²). At 64² there was no break-even.
10. **Measure energy the right way.** On recent NVIDIA GPUs, nvidia-smi `power.draw` is a 1 s average. Integrate
    instantaneous power over the exact timed window.

## D. Verifying the outputs (R4)

11. **Re-verify every reported design with an independent FE solve.** Do not rely on a surrogate or image metric.
12. **State the evaluator exactly.** Thresholding, filtering, void stiffness, volume handling.
    - Seen in this study: OAT's evaluator binarizes the raw design variables at 0.5 without the filter. That rewards
      extra material, so volume must be checked beside compliance error.
13. **Report volume-fraction error beside compliance error**, and flag designs that exceed the volume target.
14. **Report failure rates.** Designs that are disconnected, infeasible or above a compliance-error cutoff, and how
    they enter the means.

## E. Scope and transparency

15. **Out-of-distribution tests**: resolutions, load cases, aspect ratios or boundary conditions outside the training
    set.
16. **Seeds and variance** for stochastic methods.
17. **Runtimes for all cases**, not a selected subset.
18. **Code, data and trained weights available**, with a licence that allows re-testing.
