# Pilot and top-up coding — human verification sheet

**Superseded (PROTOCOL §11, 2026-09-24):** records are verified by a blind second AI pass and AI adjudication
(`analysis/compare_passes.py`). This sheet is kept for the record and is not used.

For each article: open the link, check the pre-filled primary outcome and rule verdicts against the protocol (`plan/PROTOCOL.md` §5), then fill your row in `audit/coding/human_verification.csv`. Blank cells accept the prefill. Unsure → pass (template convention).

Rules that the prefills did not all apply (`plan/PROTOCOL.md` §11):
- **No baseline.** An article that does not run, time or cite a classical method's cost or result makes no comparison. Exclude it: human_include = `exclude`, human_reason = `FT-NOBASELINE`; `apply` then sets stratum and R1–R4 to `na`. Records flagged as candidates are marked below.
- **Exclusion codes.** Use one code from the closed list in `audit/schema/screening_codes.md` (second table), first applicable in its order.
- **G1 set.** The decision G1 walks the decision order (records marked "decision order k", listed first) and uses the first 20 speed-stratum includes. The provisional arXiv pilot and its top-ups follow. `python -m analysis.gates` shows the current sets. Verify in the listed order.
- **Conflicts of interest.** Leave flagged records for the second coder.
- **Browser caveat.** Some pilot prefills were read through a browser tab that several coders shared. Check each locator against the article.

## P02328 (decision order 1) — Two-scale data-driven design for heat manipulation (2023)

- **FLAG — exclusion check: Coded FT-NOML: the 'data-driven' method is a nearest-neighbour database lookup. If that counts as a learned model, the code becomes FT-NOBASELINE.**
- Link: https://arxiv.org/abs/2304.00747
- Access: full_text; inclusion: **exclude** (FT-NOML; prefill label: FT-NOML); stratum: **none**
- Primary outcome (Abstract; Sec. 3 (database), Sec. 5 (examples), Sec. 6 (extraction), Sec. 7): Not coded (excluded). Headline: gradient-based optimization of the two homogenized conductivity components per macro element achieves thermal cloaking, concentration, rotation and their combinations; nearest-neighbour substitution from an 8282-RVE database matches the optimized properties (MSE down to 9.3e-6, R2 up to 0.9998).
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded at full text). No runtime, iteration count or hardware is reported anywhere in the article.)

- **R1 = na** [] — excluded at full text
- **R2 = na** [] — excluded at full text
- **R3 = na** [] — excluded at full text
- **R4 = na** [] — excluded at full text

- Baseline: {}

## P00647 (decision order 4) — Designing a TPMS metamaterial via deep learning and topology optimization (2024)

- **FLAG — duplicate: Its arXiv preprint is P00826 (not yet coded); P00826 should become FT-DUPLICATE of P00647. The paper calls itself educational: FT-TYPE is possible.**
- Link: https://arxiv.org/abs/2303.10007 (preprint version, pool P00826)
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (Sec. 3.2 (p. 8) and Table 2 (p. 10): the first quantitative ML-vs-classical comparison. The abstract and conclusion compare only qualitatively; the introduction (p. 2) gives the classical cost alone (about 67 s per iteration at 32³, 200-800 iterations)): Once trained, the 3D ResUNet predicts an optimized 32³ gyroid unit cell in 0.001 CPU-hours, versus about 2.4 h per homogenization-based SIMP run on one HPC core; accuracy is judged only by voxel MSE and Dice.
- Key phrase: instantaneously predict the optimized unit cell geometry for any topology parameters
- Claimed speed-up: 2400 (Derived, no factor is stated: 2.4 h per TO data point on one HPC core (Sec. 3.2, p. 8) ÷ 0.001 CPU-hours for DL prediction (Table 2, p. 10) = 2,400. Whether 0.001 CPU-h is per prediction or for the whole test set, and on which CPU, is not stated. With the introduction's workstation figure (67 s per iteration × 200-800 iterations = 13,400-53,600 s, p. 2) the ratio would be about 3,700-14,900 [derived]. Data generation and training (Table 2) are reported separately and are not in the ratio.)

- **R1 = partial** [R1-loose] — Sec. 3.2, Table 2, Sec. 5: DL prediction (0.001 CPU-h) is set against full TO runs (about 2.4 h each), and its outputs are compared with the TO ground truth only by voxel MSE (0.0079), Dice (about 95%) and volume deviation (0.24% mean). The bulk or shear modulus of a predicted cell is never computed, so objective-level matching cannot be checked; the authors note poorly learned discontinuous designs at low filter radius (p. 11). A stricter reading (speed claim with no design-quality comparison) gives fail (R1-no-quality).
- **R2 = partial** [R2-hardware-unjustified; R2(e) re-test pointer] — Sec. 3.2 and Table 2: the classical time comes from single-core runs of a modified educational MATLAB code (chosen for parallel data generation), while the prediction hardware is not stated. (c) does not apply: the timed prediction is on CPU and the problem has about 9.8×10⁴ DOFs [derived]. (b) not observed (no figure in the abstract). (d) not established (convergence-based stopping, 1,000-iteration cap). For (e), a per-iteration time is stated: about 67 s at 32³ with 6 load cases on a workstation (p. 2); it needs a same-size strong-baseline measurement. Unsure between pass and partial [judgment].
- **R3 = pass** [R3-costs-reported; per-query framing] — Table 2 (p. 10) and Sec. 3.2 (p. 8) report data generation (24 h on 226 cores; about 2.4 h per run) and training (5.5 GPU-h) next to the prediction time. The abstract names the many costly TO runs as the model's major disadvantage and frames the gain as reuse after training. No break-even is given [derived for C3: about 2,750 uses = 6,600 core-h ÷ 2.4 h, before training]. A stricter reading (costs with no amortization) gives partial (R3-no-amortization).
- **R4 = fail** [R4-image-metric] — Sec. 3.3 and Sec. 5, Figs. 13-16: quality rests on voxel MSE and Dice against the TO ground truth and on volume deviation. No FE or homogenization analysis of any predicted cell is reported, and no failure count (e.g. disconnected or hollow predictions) is given; Figs. 14-16 show selected slices.

- Baseline: {"classical_method": "Energy-based homogenization TO (SIMP, OC update, density/sensitivity filter, penalty 5) maximizing the bulk or shear modulus of a periodic 32³ unit cell, started from a voxelized gyroid; Vf 25-45%, rmin 1.2-2.5; the text adds a Heaviside projection with beta doubled from 1 to 512 (Sec. 2.2, pp. 4-5; Sec. 3.1, pp. 5-6)", "implementation": "MATLAB, modified from the educational code of Gao et al. 2018 (Top3D_maxbulk.m / Top3D_maxshear.m; Sec. 2.2 and 3.1). Public repository read 2026-09-24: the Heaviside continuation is commented out and the loop cap is 600 iterations, which differs from the text", "solver": "not stated in the article; the public code solves the reduced periodic system for 6 load cases with MATLAB backslash (sparse direct) [observed in the repository code]", "hardware_classical": "Data generation: one TO run per core on HPC nodes (iForge Intel Skylake

## P00170 (decision order 5; provisional top-up 61) — Machine Learning based parameter tuning strategy for MMC based topology optimization (2019)

- Link: https://arxiv.org/abs/1910.07227
- Access: full_text; inclusion: **exclude** (FT-MLONLY; prefill label: FT-MLONLY); stratum: **none**
- Primary outcome (n/a): None: the article reports no comparison with a classical method. Its only comparison ranks the Extra-Trees feasibility classifier against three other ML classifiers on classification metrics (Tables 4 and 7).
- Key phrase: 
- Claimed speed-up: None (not applicable (excluded at full text); no run time, iteration cost or tuning cost of any method is reported)

- **R1 = na** [excluded] — excluded at full text
- **R2 = na** [excluded] — excluded at full text
- **R3 = na** [excluded] — excluded at full text
- **R4 = na** [excluded] — excluded at full text

- Baseline: {}

## P00183 (decision order 8; provisional pilot 10) — One-Shot Generation of Near-Optimal Topology through Theory-Driven Machine Learning (2019)

- Link: https://arxiv.org/abs/1807.10787
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (Section 5.4, paragraph on solution generation speed, p. 13 (abstract and conclusion hold only qualitative ML-vs-classical claims; their quantitative claims are ML-vs-ML)): The trained one-shot generator produces a topology in the order of 10⁻² s per problem on a Xeon E5-1620 CPU, versus 10² to 10³ s per problem for the TO solver; the authors exclude data-acquisition cost from this comparison.
- Key phrase: computation time required for generating solutions through the learned model is negligible
- Claimed speed-up: 10000 (Derived from order-of-magnitude times in Section 5.4 (p. 13): 10²–10³ s ÷ 10⁻² s = 10⁴–10⁵; the lower bound 10⁴ is entered. Not stated as a factor. Excludes data acquisition and training, as the authors note.)

- **R1 = fail** [R1-unmatched] — Section 5.4 p. 13: generator time (about 10⁻² s) is compared with full TO solves (10²–10³ s) run to the AL tolerances (Alg. 2). The generated designs are measurably worse: Case 2 median compliance gap 5.2 with std 0.6 over 10 runs and failure rate 0.16% (Table 1); Case 1 mean gap 6.2 (Fig. 3b), 3.5–16.7% on the Fig. 4 examples [derived]. Mean global volume violation is 8.76% vs 4.89% for ground truth in Case 1 (1.6% vs 3.0% in Case 2) (p. 12). No classical run is matched to the generator's quality or time.
- **R2 = partial** [R2-inefficient-impl] — Section 3.2 p. 6: the AL solver needs about 5000 FE analyses on average for a 4800-element 2D problem; Alg. 2 uses gradient steps with a 10⁻³ learning rate, step clipping and β-continuation. Typical OC/MMA runs on such problems need far fewer FE solves [recalled, not verified in-session]. Linear solver and TO-solver hardware are not stated. (a) and (e) need a re-test (per-FE-analysis time ≈0.02–0.2 s is derivable); (b)–(d) are not established.
- **R3 = partial** [R3-no-training-cost] — Section 5.4 p. 13: the authors state that generator run time excludes data acquisition and that the comparison holds only when the expected TO workload far exceeds the training cost (an explicit per-query limitation). Data cost is given as an FE-analysis budget (Case 2 equals 7000 TO solves, p. 11), but NN training time is not reported and no break-even is computed; Section 6.4 discusses the trade-off only qualitatively.
- **R4 = pass** [R4-FE-verified] — Eq. (8), Figs. 3–6, Table 1: compliance of every generated test design is computed by FE analysis and compared with the AL ground truth over 100 (Case 1) and 1000 (Case 2) test inputs, 10 runs each. Global and local volume-constraint violations are reported (p. 12), and failed designs (gap > 1000) are counted for Case 2 (Table 1). Case 1 failure counts and the number of volume-violating designs are not given.

- Baseline: {"classical_method": "Density TO with filter, projection, global and local (p-norm) volume constraints, solved by a custom augmented Lagrangian (AL) gradient method (Section 3.2; Appendix, Alg. 2); ground truth for all learning mechanisms", "implementation": "not stated in the article; the public repository holds MATLAB TO scripts and Python learning scripts [checked repository file listing]", "solver": "not stated (Ku = s solves; linear solver type not given)", "hardware_classical": "not stated (the hardware in Section 5.4 is given for the generator only)", "hardware_ml": "Intel Xeon CPU E5-1620 @ 3.50GHz for generation (Section 5.4, p. 13); training hardware not stated", "problem_size": "40×120 mesh, N = 4800 elements (Sections 3.2, 5.2) [inferred ≈10⁴ DOFs]", "classical_iterations": "stopping rule: AL tolerances ε_al = 1 and ε_opt = 10⁻³ with β-continuation (Alg. 2); about 5000 FE ana

## P01960 (decision order 10) — Reinforcement learning-based topology optimization for generative designed lightweight structures (2025)

- **FLAG — stratum check: The body runs neither SIMP nor level-set; the 40 % weight gain is against a 'traditional hub'. If that is not a classical comparison, the Fig. 12 timing (8.8x derived) makes it speed stratum.**
- Link: https://doi.org/10.1016/j.mex.2025.103539
- Access: full_text; inclusion: **include** (I-QUALITY (screening code confirmed at full text; the abstract's quantitative classical comparison is a weight-reduction claim)); stratum: **quality**
- Primary outcome (Abstract (first quantitative comparison with a classical method, §5.1 rule 1). The number reappears in the closing summary paragraph of 'Method validation' (the article has no separate Conclusion section) and in the wheel-hub case study (Fig. 13, weight bar chart)): The abstract says the PPO-based design method beats conventional SIMP and level-set approaches on the ToD benchmark, with up to 40% lower weight at maintained compliance. In the body, the 40% is measured against a traditional hub design, not against SIMP or level-set.
- Key phrase: achieving up to 40 % weight reduction while maintaining compliance
- Claimed speed-up: None (Not applicable to the quality-stratum primary outcome. Alternative, 'Method validation' text and Fig. 12 (inference-time bar chart): PPO-RL about 2.1 s vs SIMP about 18.4 s, so 18.4 / 2.1 = 8.8 [derived]. The text attributes the SIMP time to ref. [36] (Halle et al., Appl. Sci. 2021); whether the authors measured it or took it from [36], and on which problem size and hardware, is not stated. RL training time is not included.)

- **R1 = fail** [R1-unmatched (no classical design result; quality stratum)] — Abstract vs body: the claimed advantage over SIMP and level-set has no classical counterpart in the article. No SIMP or level-set design, volume or compliance is reported (full text read; Table 6 compares only with ML references [36]-[38]). The 40% figure compares the optimized hub with a traditional hub of unstated origin (Fig. 13), not with a classical optimizer at matched volume or compliance, and the compliance of neither hub is quantified. Alternative: na, if R1 is read as applying to speed comparisons only.
- **R2 = na** [R2-na-quality-stratum] — Quality stratum, and no classical design is run, so the competence of a comparator cannot be judged. For the Fig. 12 speed alternative: the SIMP time (about 18.4 s) is attributed to ref. [36], with no implementation, solver, iteration count, problem size or hardware for either method, so (a)-(e) cannot be established; partial (R2-hardware-unjustified) would be the likely code under that reading [inferred].
- **R3 = na** [R3-na-quality-stratum] — Primary outcome is quality only. For C3: the PPO agent's training (100 episodes of FEA-in-the-loop interaction, Table 4, 'Method validation') has no reported time or hardware, and the 2.1 s inference time in Fig. 12 excludes it; no break-even is given.
- **R4 = partial** [R4-no-failure-rate] — Step 4 and Table 5: the final ToD design is said to be checked by FEniCS FEA; volume fraction 0.32 and constraint values (0.49 mm, 298 MPa) are reported. The returned binary grid has disconnected and floating elements ('Method validation', Fig. 7), which the authors say SDF smoothing removes, but they are not counted, and Table 5 does not say whether it describes the design before or after smoothing. One design per case, so no failure rate. The 40% hub figure has no FE-computed compliance for either hub.

- Baseline: {"classical_method": "SIMP and level-set are named as the outperformed conventional approaches (Abstract), but no SIMP or level-set design is run or reported anywhere in the article. The only classical number is a SIMP time of about 18.4 s, attributed to ref. [36] ('Method validation', Fig. 12). The comparator of the 40% weight figure is a traditional hub design (Fig. 13 bar chart), whose origin is not described", "implementation": "not stated", "solver": "not stated (the proposed method uses FEniCS for its FEA, Step 4)", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "ToD case: 60 x 40 grid (2400 elements), 2D cantilever, left edge clamped, 1000 N point load on the right edge, aluminium E = 70 GPa, nu = 0.33 (Step 1, Table 1). Wheel hub: cylindrical domain, 5000 N radial load and 1000 Nm torque, 5 mm minimum wall; mesh not stated (Application case study

## P00786 (decision order 11) — Multi-scale topology optimization of multi-material heterogeneous microstructures based on deep learning (2025)

- **FLAG — stratum check: Speed stratum rests on a per-evaluation cost proxy (500x per homogenization call), as in P00149. No classical TO is run; if the proxy is rejected, FT-NOBASELINE.**
- **FLAG — access route: The PDF came from the publisher's own PDF server via the link on the OUP page; no challenge was solved.**
- Link: https://arxiv.org/abs/none found (arXiv title search returned no match)
- Access: full_text; inclusion: **include** (I-SPEED (screening code kept at full text; the only measured classical comparison is per property evaluation, a cost proxy as in P00149)); stratum: **speed**
- Primary outcome (Sec. 2.3, p. 134, and Table 2, p. 135 (first quantitative comparison with a classical method, in the main text; the abstract, introduction and conclusions state the cost saving only qualitatively)): The MLP surrogate returns a microstructure's homogenized elasticity tensor and volume fraction about 500× faster than numerical homogenization (≈6×10⁻⁴ s vs ≈0.32-0.34 s on five example microstructures), with MAE below 0.01.
- Key phrase: approximately 500 times faster than the homogenization theory
- Claimed speed-up: 500 (Stated in Sec. 2.3 as approximately 500×, per microstructure evaluation. Per-example ratios stated as 510, 557, 549, 570 and 486× for microstructures (6)-(10); they match Table 2 (e.g. 0.3190 s ÷ 6.251×10⁻⁴ s = 510 [derived]); mean of the five ratios 534 [derived]. Not an optimization-level speed-up: no classical multiscale TO is run or timed. Data generation and training are excluded.)

- **R1 = partial** [R1-loose] — Sec. 2.3 and Table 2: time and accuracy are reported for the same five microstructures, and the surrogate outputs sit within their reported error (MAE < 0.01) of HC. Matching is loose: the claim is per property evaluation; no classical multiscale TO is run, so neither design quality nor total optimization time is matched; the five examples are illustrative picks from Fig. 3B, and whether they lie in the training set is not stated. Coded as in P00149.
- **R2 = pass** [R2-none-established] — Sec. 2.3, Table 2: HC implementation, solver and timing hardware are not stated; both methods ran on a CPU workstation [inferred], so (c) does not apply, and the problem has ≈2×10⁴ DOFs [derived], below 10⁵. The abstract gives no baseline figure (b); no iteration count applies (d); no per-iteration classical time exists (e). 0.32-0.34 s for one 100×100 homogenization shows no evident inefficiency. Unsure, so pass.
- **R3 = partial** [R3-no-data-cost] — Sec. 2.3: training time is reported (131 min, final model; hyperparameter search not timed), but the cost of homogenizing the 156,000 training microstructures is not [inferred ≈14 h at 0.327 s each]. No break-even is given; the introduction argues only qualitatively that the one-off data and training cost is repaid by reuse. C3 [derived]: (51,000 s + 7,860 s) ÷ (0.327 − 0.0006) s ≈ 1.8×10⁵ property evaluations, i.e. ≈350 iterations at 32×16 cells or ≈8 runs of the 40×4, 135-iteration shape-matching example.
- **R4 = partial** [R4-no-failure-rate] — Table 2: surrogate outputs are checked against FE homogenization, but only for five illustrative microstructures; no held-out error is reported beyond the 2.2×10⁻³ loss value (Sec. 2.3). Design objectives (e.g. J = 16.676, Sec. 4.1.2; 19.455, 21.687, 17.580, Sec. 4.1.4) come from the macroscale FE with surrogate-predicted properties; the reconstructed structures are not re-analysed [inferred]. Volume is a soft penalty and final fractions are only plotted (Fig. 12A). One unreasonable design is noted qualitatively (Fig. 14(6)); no failure counts. A stricter reading (surrogate-predicted, selected examples) gives fail.

- Baseline: {"classical_method": "Numerical homogenization (HC) of each 100×100-pixel microstructure, i.e. the online homogenization step that classical multiscale TO would repeat per cell and iteration (Sec. 2.3, Table 2; refs Guedes & Kikuchi 1990, Andreassen & Andreasen 2014, Dong et al. 2019). No classical optimizer is run", "implementation": "not stated for HC; the surrogate is built in Python/PyTorch (Sec. 2.3, 3.5)", "solver": "not stated", "hardware_classical": "not stated for the Table 2 timing [inferred: the same i9-13900K workstation used for training, Sec. 2.3]", "hardware_ml": "13th Gen Intel Core i9-13900K 3.00 GHz workstation, 64 GB memory, for surrogate training (Sec. 2.3) and all numerical examples (Sec. 4); no GPU mentioned", "problem_size": "Microstructure 100×100 pixels (Sec. 2.3) [≈2×10⁴ DOFs, derived]; macroscale meshes 16×8 to 56×28 (Table 3), mostly 32×16 (Sec. 4.1), 40×4 and

## P01268 (decision order 14) — Application of a Machine Learning-Based Topology Optimization Method on an Automotive B-Pillar for Crashworthy Lightweight Design (2026)

- Link: https://doi.org/10.1051/matecconf/202642203010
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (abstract only): Not coded (no full text). The abstract reports voidML cut the B-pillar patch mass from 2.413 to 2.141 kg (11.3%) in 48 iterations and 191 crash analyses, with force-intrusion curves close to the reference; no classical comparator is named.
- Key phrase: 
- Claimed speed-up: None (not coded (no full text); the abstract states no time or speed comparison with a classical method)

- **R1 = na** [no-full-text] — no full text
- **R2 = na** [no-full-text] — no full text
- **R3 = na** [no-full-text] — no full text
- **R4 = na** [no-full-text] — no full text

- Baseline: {}

## P00165 (decision order 15; provisional top-up 94) — Topology optimization of 2D structures with nonlinearities using deep learning (2020)

- **FLAG — duplicate: P01152 (coded FT-DUPLICATE) and P00867 (not yet coded) are older titles of the same arXiv preprint.**
- Link: https://arxiv.org/abs/2002.01896
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-SPEED; the ML inference time is never quantified, so the speed claim stays qualitative, and the first quantitative classical comparison is test-set Dice similarity against the TO designs, §5.1 rule 2)); stratum: **quality**
- Primary outcome (Sec. 5, pp. 29-30 (linear model; first quantitative comparison with classical TO results); neo-Hookean pp. 32-33; stress-constrained p. 34. The abstract, introduction and conclusion compare with TO only qualitatively): On held-out test sets, ResUnet predictions thresholded at 0.5 reproduce the TO ground-truth designs with mean Dice similarity 0.958 (linear elastic, 32×32); 0.964 (neo-Hookean) and 0.984 (stress-constrained), both 50×50.
- Key phrase: the ground-truth and predicted designs are almost identical
- Claimed speed-up: None (Not derivable: the ML inference time is never given (called negligible in the abstract and instant in Sec. 5, p. 34, and Sec. 6). Classical side only: about 25 min per linear 32×32 optimization and about 90 min per neo-Hookean 50×50 optimization on a Core i5 vPro PC (Sec. 3.1, Fig. 4).)

- **R1 = partial** [R1-loose] — Sec. 3 and 5: predictions and TO designs share the same inputs (load position, angle and magnitude, volume target, filter radius), so the comparison is at matched problem settings. Matching is loose: agreement is measured only by DSC on thresholded images; the volume fraction and compliance of the predicted designs are not reported; the TO stopping rules are not stated; no time or FE budget is matched.
- **R2 = partial** [R2-inefficient-impl] — Sec. 2.1 and 3.1: the linear and neo-Hookean reference designs come from ABAQUS/TOSCA, a general-purpose commercial TO module (a listed partial case). The reported cost, about 25 min per 32×32 linear optimization on a Core i5 PC (about 2,200 DOFs [derived]), looks slow for the size [inferred]; no direct comparison is possible because iteration counts are not stated. (c) does not apply: problems have at most about 5×10³ DOFs [derived]. (b), (d) and (e) are not established. Alternative: na, since the primary outcome compares quality only.
- **R3 = na** [R3-na-quality-stratum] — Primary outcome is quality only. For C3: the qualitative speed claim concerns inference time only (abstract). Training 1.25 h and 1.5 h on one V100 (Sec. 5, p. 26); data 15,000 and 18,000 samples at 0.31 and 3.2 min per data point on ten parallel iForge tasks (Sec. 3.1) [derived: 77.5 h and 960 h]; stress model: neither cost stated; no break-even. [derived] Because the data are TO runs, the linear model breaks even only after about 15,000 uses at PC rates (15,000 × 25 min of data vs 25 min saved per use), plus about 3 uses for training.
- **R4 = fail** [R4-image-metric] — Sec. 4.2 and 5: design quality rests only on the Dice similarity of thresholded images (0.958, 0.964, 0.984) and on randomly picked visual examples (Figs. 10, 11, 13). No FE analysis of any predicted design is reported: no compliance, no volume check and no stress-constraint check for the stress model. Disconnections are said not to occur for the linear model (p. 32), without a count.

- Baseline: {"classical_method": "Density-based SIMP (penalty 3) compliance minimization with a volume constraint, solved by MMA: ABAQUS with TOSCA (sensitivity-based solver) for the linear elastic and neo-Hookean datasets (Sec. 2.1, 3.1); an in-house MATLAB MMA code with a q-norm stress constraint (q = 10) for the stress-constrained dataset (Sec. 2.2, 3.2)", "implementation": "Commercial general-purpose TO module (ABAQUS/TOSCA) driven by Python scripts for two datasets; in-house MATLAB code for the stress dataset (Sec. 2.1-3.2)", "solver": "not stated", "hardware_classical": "iForge HPC cluster (Intel Skylake nodes, 40 cores, 192 GB RAM), ten optimizations run simultaneously; also a personal computer with an Intel Core i5 vPro (Sec. 3.1)", "hardware_ml": "Training on one NVIDIA V100 (32 GB) on iForge; a CPU-only iForge node was used for a training-time comparison (Sec. 5, p. 26). Inference hardware

## P00019 (decision order 18; provisional top-up 26) — Multi-material Multi-physics Topology Optimization with Physics-informed Gaussian Process Priors (2026)

- Link: https://arxiv.org/abs/2602.17783
- Access: full_text; inclusion: **include** (I-QUALITY); stratum: **quality**
- Primary outcome (Section 4.1, Table 4 (first quantitative classical comparison; the abstract, introduction and conclusion compare with the open-source codes and COMSOL only qualitatively)): With a mass constraint on four 2D multi-material compliance benchmarks, PIGP's median compliance over 10 runs is slightly above ordered SIMP's and PolyMat's (e.g., MBB 1.049 vs 0.982 and 0.987); with a cost-only constraint it matches PolyMat.
- Key phrase: achieves compliance values that are slightly higher yet comparable
- Claimed speed-up: None (No runtime of any method is reported anywhere. Only hardware and budgets are given: SIMP, PolyMat and COMSOL on an Intel i7-11700K CPU; PIGP in Python on an NVIDIA A100 GPU for up to 10,000 Adam epochs, 20,000 for the thermo-mechanical cases (Sec. 4, 4.4). The conclusion states qualitatively that PIGP costs more to train than SIMP and that COMSOL is slower than the open-source codes and PIGP. Not derivable.)

- **R1 = partial** [R1-loose] — Sec. 4, 4.1, Tables 2-4: every method is scored by FEM at the same mass or cost target, and achieved values are reported (e.g., MBB mass 6006.3 PIGP, 5990.8 ordered SIMP, 5988.0 PolyMat; target 6000 [derived]). Matching is loose: discretizations differ (Table 3), length-scale control differs (filter radius 6 and 2 mm vs the PGCAN resolution, which Sec. 4.2 links to feature complexity), and PIGP runs up to 10,000 epochs while the iteration counts and stopping rules of ordered SIMP and PolyMat are not stated. No runtimes are compared.
- **R2 = pass** [R2-none-established] — Quality stratum, competence of the comparator. Sec. 4-4.1: the 2D comparators are published open-source codes with stated filter radii, and projection was switched off in PIGP to match them. No speed claim exists, so markers (a)-(e) do not bear. Ordered SIMP's weak cost-only result (MBB 0.991 vs 0.652 for PolyMat) is attributed by the authors to its interpolation scheme, a property of the method rather than a weak run [inferred]. For the alternative COMSOL comparison, the conclusion says COMSOL needs fine-tuning to be competitive and Sec. 4.4 reports that a multi-material COMSOL setup could not be made to work, so that comparator may be under-tuned [inferred]; it is not the primary outcome. Unsure, so pass.
- **R3 = na** [R3-na-quality-stratum] — Quality stratum with per-problem physics-informed training and no offline data (Sec. 3); no speed claim. For C3: no runtime, training time or GPU-hours are reported for any method; the conclusion says only that PIGP costs more to train than SIMP.
- **R4 = partial** [R4-no-failure-rate] — Sec. 4 opening and the captions of Tables 4, 5, 8, 11 and 15: the objectives of the final topologies of all methods are evaluated by FEM (ABAQUS after binarization in Sec. 4.4), achieved mass and cost values are reported, and statistics cover all 10 runs (medians in Table 4). Defective designs are not counted: gray areas (Sec. 4.3) and thin or disconnected features (Sec. 4.4) are described only qualitatively, and whether the Table 4 designs were binarized before the FEM evaluation is not stated.

- Baseline: {"classical_method": "2D: ordered SIMP for multi-material TO (ref. [14], Da Silveira and Palma 2022) and PolyMat (ref. [43], Sanders et al. 2018); 3D: single-material SIMP 3D code (ref. [33], Liu and Tovar 2014); thermo-mechanical: COMSOL with a nested MMA workflow (Sec. 4, 4.1, 4.4)", "implementation": "Published open-source codes (refs. [14], [33], [43]; the titles of [33] and [43] name MATLAB); ordered SIMP filter radius 6, PolyMat density filter radius 2 mm, no projection in these codes (Sec. 4, 4.1). COMSOL (commercial) with a Helmholtz filter of radius 5 um and projection continuation beta = 8, 12, 16 (Sec. 4.4)", "solver": "not stated for any classical code", "hardware_classical": "Intel Core i7-11700K CPU for SIMP, PolyMat and COMSOL (Sec. 4)", "hardware_ml": "NVIDIA A100 GPU; Python implementation (Sec. 4)", "problem_size": "Primary (2D compliance): ordered SIMP 301x151 FE nodes

## P00140 (decision order 19; provisional top-up 80) — De-homogenization using Convolutional Neural Networks (2021)

- **FLAG — stratum check: The quantitative part of the abstract claim is a quality gap; speed stratum is a judgment call. R1 could be partial instead of fail.**
- Link: https://arxiv.org/abs/2105.04232
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (Abstract (first quantitative comparison with a classical method; §5.1 rule 1). The cost part is qualitative in the abstract and is quantified in Sec. 4.2.1 (p. 18) and the Conclusions (p. 22) as a factor of 5 to 10 over state-of-the-art de-homogenization): A CNN replaces the least-squares step of classical de-homogenization. The resulting single-scale designs come within 7-25% of the homogenization-based reference performance, at a small fraction of the cost. The body quantifies the saving as about 5-10x over least-squares de-homogenization.
- Key phrase: within 7−25% of the homogenization-based solution at a fraction of the computational cost
- Claimed speed-up: 5 (Stated as a factor of 5 to 10 (Sec. 4.2.1, p. 18; Conclusions, p. 22); the lower bound is entered. It is a cross-paper estimate. Groen et al. [16] report about 10 s for 80x40 -> 1600x800 on another laptop. This work needs about 1.3 s for 60x30 -> 1440x720 and about 2.2 s for 60x30 -> 2400x1200 on a single Intel Core i7 2.6 GHz CPU. Ratios: 10/1.3 = 7.7 and 10/2.2 = 4.5 [derived]. Training (about 1 h on a Titan X GPU) and the homogenization-based optimization that supplies the input are not counted.)

- **R1 = fail** [R1-unmatched; R1-no-quality (vs the timed comparator)] — Abstract, Sec. 4.2.1 and Conclusions: the 5-10x saving over least-squares de-homogenization [16] rests on a cited time. The quality of [16]'s designs is not reported. The CNN designs are 6.8-52.6% worse than the homogenization reference (Tables 2-5 [derived]), and no matching is attempted; the authors present this as a trade-off (p. 19). The top88 alternative is also unmatched: no top88 design exists, similar quality is asserted, and the input's homogenization-TO time is excluded. Alternative: partial (R1-loose) if the reference comparison is accepted.
- **R2 = pass** [R2-none-established] — Sec. 4.1 and 4.2.1: both sides are timed on laptop CPUs (CNN on a single Intel Core i7 2.6 GHz CPU; [16] on a laptop of unstated model), so (c) does not apply. The abstract gives no baseline figure (b). No iteration count exists for [16], so (d) and (e) cannot be derived. The authors flag that the cross-paper times are not directly comparable. Unsure, so pass. Pointer for the top88 alternative: 16 s and 87 s per iteration at about 2.1 and 5.8 million DOFs [derived] can be checked for (e) with the project's baseline at the same size; the 1000 iterations are assumed, not run.
- **R3 = partial** [R3-no-data-cost; R3-no-amortization] — Sec. 4.1: training time (about 1 h on a Titan X for 15 epochs) is reported. The cost of generating the 20,000 synthetic orientation fields is not stated (it needs no TO runs; small [inferred]). No break-even or amortization is given, and the claim is not explicitly limited to per-query use. For C3 [derived, cross-hardware, rough]: 3,600 s of training over a saving of about 8.7 s per use vs [16] gives about 400 uses; vs the top88 alternative, fewer than one use.
- **R4 = partial** [R4-no-failure-rate] — Tables 2-5 and App. A Table 1: compliance and volume fraction are reported for the post-processed design in every case (all 30 cases, no selection); FE evaluation is inferred, as the method is not described. Volume overshoot is visible per case and discussed (Sec. 4.2-4.3). Non-load-carrying boundary artefacts appear in many designs (Sec. 4.2, p. 16) but are not counted, and no disconnection or failure count is given.

- Baseline: {"classical_method": "Primary: least-squares de-homogenization of homogenization-based TO results (Groen and Sigmund 2018 [16]); its time is cited, not run (Sec. 4.2.1). Quality reference for every case: the rank-2 homogenization-based TO solution that supplies the CNN input (Sec. 2.1, eq. 1; code by J. P. Groen per the Acknowledgements). Alternative speed comparator: SIMP with the top88 MATLAB code at the fine resolution, per-iteration time measured, iteration count assumed (Sec. 4.2.1)", "implementation": "Least-squares de-homogenization: not described (cited result from [16]). top88: the public 88-line MATLAB code (footnote 1, p. 18). Homogenization TO: in-house code (Acknowledgements). Proposed: fully convolutional network with post-processing (skeletonize, distance transform) (Sec. 2.2-2.3, App. B)", "solver": "not stated for any classical method (top88 as published uses a sparse di

## P01971 (decision order 22) — Reinforcement Learning Guided Engineering Design: from Topology Optimization to Advanced Modelling (2025)

- **FLAG — stratum check: No conclusion section. If the Discussion counts, the RL-vs-brute-force operation count becomes primary (speed stratum).**
- Link: https://arxiv.org/abs/none found (arXiv author search for Tskhondia returned no records)
- Access: full_text; inclusion: **include** (I-QUALITY (screening code confirmed at full text)); stratum: **quality**
- Primary outcome (Sec. 3, pp. 9-10 (first quantitative comparison with a non-learned method; the abstract states the GA comparison only qualitatively, the introduction has none, and there is no conclusion section: the closing Discussion restates the GA claim qualitatively)): On a 10×10 cantilever grid, refining a genetic-algorithm layout (about 1 min) with PPO (about 32 min) lowers the compliance metric from 19.3654 to 18.2786; the author states GA alone does worse for the same wall-clock time.
- Key phrase: GA pre-training + RL refinement was better than GA alone
- Claimed speed-up: None (No speed-up over a classical method is claimed; the Discussion (p. 13) concedes that traditional TO is almost always faster in wall-clock time. Appendix, 5×5 grid: SIMP (topopt_cholmod.py) about 1 s vs PPO about 18 min (ML about 1,080× slower [derived]); brute force about 5.8 h (PPO about 19× faster [derived]).)

- **R1 = partial** [R1-loose] — Sec. 3, pp. 9-10: the printed numbers compare the GA output after about 1 min with GA+RL after about 1 + 32 min, so the budgets are unequal. The equal-wall-clock GA-alone result is asserted but not printed. GA generations, population and stopping rule are not stated, and the material volume of neither design is reported.
- **R2 = pass** [R2-none-established] — Sec. 3: the GA and the RL refinement run on the same Apple M1 Pro with the same FE code [23]; the grid has ≈242 DOFs [derived], so (c) does not apply; the abstract gives no baseline figure (b); the GA ran shorter, not longer, than needed (d); no per-iteration time exists (e). A GA is a weak TO method compared with gradient TO (the appendix SIMP run takes about 1 s), but no R2 marker covers the choice of method. Unsure, so pass.
- **R3 = na** [R3-na-per-problem] — No speed claim against a classical method is primary, and the RL agents are trained per problem (the PPO refinement of the 10×10 case is itself the 32 min run), which is R3's n/a case. For C3: PPO 1M steps about 80 min on an i5 (Sec. 3); HRL hyperparameter search time not stated.
- **R4 = partial** [R4-no-constraint-report] — Sec. 3: both designs are scored by the FE code of [23] in the same environment [inferred], one run each. Material volume, failed runs and seeds are not reported, and the metric is not defined. Removal-only refinement (Sec. 3, step 2) lowering compliance at a fixed load is inconsistent with pure compliance [inferred], so the metric may include a volume term. Fig. 3(c) (HRL, not the primary outcome) is labelled cherry-picked. A stricter reading gives fail.

- Baseline: {"classical_method": "Genetic algorithm (DEAP) placing elements on the binary 10×10 grid, run for about 1 min (Sec. 3). Appendix only: SIMP via topopt_cholmod.py (Python version of the 88-line code [11]) and brute-force enumeration on a 5×5 grid", "implementation": "DEAP GA with the FE code of Greydanus's structural-optimization tutorial [23] (Sec. 2.5, 3); topopt_cholmod.py for the appendix SIMP run", "solver": "not stated", "hardware_classical": "Apple M1 Pro for the GA+RL experiment, GA included (Sec. 3, p. 9); not stated for the appendix runs", "hardware_ml": "PPO (6×6, 5×5): 2.9 GHz dual-core Intel Core i5, 1M steps in about 80 min; HRL (4×4): Apple M1 Pro, 5000 steps; GA+RL (10×10): Apple M1 Pro (Sec. 3, pp. 7 and 9)", "problem_size": "10×10 element grid for the primary comparison [≈242 DOFs, derived]; 6×6 and 5×5 (PPO), 4×4 (HRL); cantilever with load at the bottom right corner (S

## P00918 (decision order 24) — Accelerating cell topology optimisation by leveraging similarity in the parametric input space (2025)

- Link: https://doi.org/10.1016/j.cma.2025.118044
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (abstract only): Not coded (no full text). The abstract says an instance-based model, using vector- or energy-based similarity of input parameters, warm-starts SIMP cell optimisation in a two-level framework and reduces computation time; no number is given.
- Key phrase: 
- Claimed speed-up: None (not coded (no full text); the abstract gives no time or speed-up figure)

- **R1 = na** [no-full-text] — no full text
- **R2 = na** [no-full-text] — no full text
- **R3 = na** [no-full-text] — no full text
- **R4 = na** [no-full-text] — no full text

- Baseline: {}

## P00610 (decision order 26) — Effective thermal conductivity estimation using a convolutional neural network and its application in topology optimization (2023)

- Link: https://doi.org/10.1016/j.egyai.2023.100310
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (Abstract (the only text read)): Not coded (no accessible full text). Abstract only: a VGG-style CNN predicts effective thermal conductivity of a 128×128 binary image in 15 ms, stated as 3-5 orders of magnitude faster than a finite volume simulation.
- Key phrase: 
- Claimed speed-up: None (Not coded. The abstract states a range of 3 to 5 orders of magnitude for one CNN prediction (15 ms, 128×128 image) against one finite volume simulation; this is a per-evaluation forward comparison, and no optimization-level time is given in the abstract.)

- **R1 = na** [] — no full text
- **R2 = na** [] — no full text
- **R3 = na** [] — no full text
- **R4 = na** [] — no full text

- Baseline: {}

## P01870 (decision order 29) — Exploring VAE-driven implicit parametric unit cells for multiscale topology optimization (2024)

- Link: https://doi.org/10.1016/j.matdes.2024.113087
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (abstract only): Not coded (no full text). The abstract describes a VAE with a property regressor, trained on a unit-cell database built by an AAPO topology-optimization method plus a distortion filter, for multiscale thermo-mechanical metamaterial design. Efficiency is asserted, with no classical comparison named.
- Key phrase: 
- Claimed speed-up: None (not coded (no full text); the abstract gives no time, cost or speed-up figure)

- **R1 = na** [no-full-text] — no full text
- **R2 = na** [no-full-text] — no full text
- **R3 = na** [no-full-text] — no full text
- **R4 = na** [no-full-text] — no full text

- Baseline: {}

## P01214 (decision order 30) — Deep learning-based topology optimization design method for bridge structures guided by aesthetics (2025)

- Link: https://arxiv.org/abs/none found
- Access: full_text; inclusion: **exclude** (FT-MLONLY; prefill label: FT-MLONLY); stratum: **none**
- Primary outcome (Abstract; Sec. 2.2 (classifier), Sec. 3 (TO network), Sec. 4, Sec. 5): Not coded (excluded). Headline: an ImageNet-pretrained ShuffleNet-V2 classifier of pylon aesthetics (validation accuracy 92.59%) screens pylon layouts generated by the authors' two-stage TO network; results are shown as selected figures only.
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded at full text). No runtime, iteration count or hardware is reported for any method.)

- **R1 = na** [] — excluded at full text
- **R2 = na** [] — excluded at full text
- **R3 = na** [] — excluded at full text
- **R4 = na** [] — excluded at full text

- Baseline: {}

## P02042 (decision order 31) — DQN-Based Pre-Optimization for Dual-Scale Collaborative Topology Optimization of Anisotropic Materials (2026)

- **FLAG — access route: PDF taken from mdpi-res.com (MDPI's own file host, CC BY) because www.mdpi.com returned 403. Confirm this route is acceptable. Same for P00663 and P00698.**
- Link: https://doi.org/10.3390/app16094080
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-SPEED; the abstract's only quantitative classical comparison is compliance)); stratum: **quality**
- Primary outcome (Abstract (quantitative comparison with the traditional method); values in Sec. 5.1 (p. 17) and the Introduction (p. 2)): On the MBB beam, running the dual-scale thermo-mechanical optimization from a DQN pre-optimized start gave final compliance 0.5754 versus 0.7421 for the same framework without DQN pre-optimization, 22.463% lower.
- Key phrase: achieves a 22.463% reduction in structural compliance
- Claimed speed-up: None (No runtime is reported for any method, and the baseline's iteration count is not stated. The abstract's faster-convergence claim is qualitative; Table 3 (p. 12) lists 60-180 iterations for the eight DQN runs only. Not derivable.)

- **R1 = partial** [R1-loose] — Sec. 5.1 (pp. 16-17), Table 4, Figs. 7-8: both designs share the mesh, loads and nominal volume fraction 0.4. Matching is loose: the baseline's penalty value, filter, iteration count and stopping rule are not stated; it ends with many intermediate densities (Fig. 7a), so a penalized grey field is compared with a near-binary design [inferred]; achieved volumes are not reported; which of the eight DQN runs (Table 3) gives 0.5754 is not stated; no compute budget is compared.
- **R2 = partial** [R2-weak-comparator [judgment]] — Quality stratum, competence of the comparator. Sec. 5.1: the baseline is the authors' own run without DQN, with an unstated fixed ('empirical') penalty and a uniform 0.5 start. Its grey final layout (Fig. 7a) suggests an under-penalized or unconverged run [inferred], while the DQN runs end with penalties 2.4-5.0 (Table 3). No classical run with a standard penalty or continuation schedule is tried, so the 22.463% gain may reflect the penalty choice rather than the DQN [judgment]. Markers (a)-(e) do not bear on a quality claim; unsure between pass and partial.
- **R3 = na** [R3-na-quality-stratum] — Quality stratum with per-problem online DQN training and no offline dataset (Sec. 3.4); no speed claim is quantified. For C3: no DQN training time, pre-optimization time or TO time is reported.
- **R4 = partial** [R4-no-constraint-report] — Sec. 5.1-5.5: the compliance values are the optimizer's FE results for the returned designs [inferred]. Achieved volume fractions are not reported for any design, and failed or non-converged runs are not counted. Eight seeds are reported for the DQN method (Table 3), while the baseline is a single run. The 3D extrusions (Fig. 12) are not analysed (Sec. 5.6).

- Baseline: {"classical_method": "The same dual-scale thermo-mechanical optimization without DQN pre-optimization: SIMP-type interpolation of modulus, conductivity and thermal-stress coefficient with a fixed empirical penalty factor (value not stated), OC update with move limit, uniform initial density 0.5 (Sec. 2.4, 4, 5.1, pp. 5-17). The article calls the optimizer BESO, but the stated update is the OC rule (Eq. 23)", "implementation": "not stated; the TO runs in a numerical-analysis environment and the DQN in PyTorch 2.6.0, CPU version (Sec. 3.3-3.4, pp. 7-8)", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "CPU (PyTorch 2.6.0 CPU version, Sec. 3.4, p. 8); processor not stated", "problem_size": "Macro 150 × 80 elements, volume fraction 0.4; micro unit cell 50 × 50 elements, volume fraction 0.5 (Table 4, p. 16). Sec. 5.4 also uses 300 × 100 (MBB) and 150 × 100 (cantilev

## P00375 (decision order 34; provisional top-up 13) — Diffusing the Optimal Topology: A Generative Optimization Approach (2023)

- **FLAG — stratum check: Screening said speed; the prefill puts it in quality (Table 5: 4.16 % compliance error against SIMP references). Alternative primary outcome: Table 9, SIMP stopped after 5 or 10 iterations.**
- Link: https://arxiv.org/abs/2303.09760
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-SPEED; full text reports no SIMP runtime, and the first quantitative classical comparison is compliance error against SIMP-optimized designs)); stratum: **quality**
- Primary outcome (Sec. 5.1, Table 5, p. 9 (first quantitative comparison with a classical method; the Abstract, Sec. 7 Conclusion and Introduction hold no quantitative classical comparison, and the Introduction's 53.93%, 23.81% and 25.64% figures are against ML baselines)): On in-distribution test constraints (task-1, 64×64), diffusion designs conditioned on the cheap kernel and refined by 10 SIMP iterations have 4.16% mean compliance error relative to the SIMP-optimized references, with 1.16% volume-fraction error and 5.61% floating material.
- Key phrase: has the lowest values for compliance error, volume fraction error, and floating material
- Claimed speed-up: None (No SIMP runtime is reported anywhere. Inference times (TopoDiff-FF + SIMP(10): sampling 2.23, processing 0.32, inference 2.55, in seconds per the Fig. 9 legend; Table 5) are compared only with ML baselines (TopoDiff 5.54, TopoDiff-GUIDED 5.87; TopologyGAN in Fig. 8). Not derivable.)

- **R1 = partial** [R1-loose] — Table 5 and Sec. 5 Evaluation: generated designs are compared with SIMP references at the same prescribed volume fraction, but volume is only approximately matched (VFE 1.16%). Samples with compliance > 100 are removed before averaging, with no count reported. Budgets are not matched or stated: the ML side spends 2.55 s of sampling, processing and 10 SIMP iterations; the SIMP reference runs have no stated iteration count or time.
- **R2 = pass** [R2-none-established] — The SIMP references come from the TopoDiff dataset [13]; this article states none of their settings (iterations, continuation, solver). Unsure, so pass. For the Table 9 alternative, SIMP is deliberately stopped at 5 or 10 iterations from an unstated initial design, which is an equal-iteration comparison rather than a converged classical baseline.
- **R3 = na** [R3-na-no-speed-claim] — No speed or cost claim against a classical method. For C3: training is 200k steps on 30,000 SIMP-optimized topologies (Sec. 5 Setup); training time, data-generation cost and hardware are not reported.
- **R4 = partial** [R4-filtered-outliers] — Compliance of generated designs is compared with SIMP compliance for the test configurations, presumably by FE analysis [inferred; the evaluation procedure is not described]. VFE, floating-material rate and load disrespect are reported (Tables 5-7). But Tables 5-6, including the primary outcome, drop samples with compliance > 100 and do not report how many; only task-3 (Table 7) is unfiltered. Figs. 11-12 show selected bad and good examples without a stated selection rule.

- Baseline: {"classical_method": "SIMP-optimized reference topologies from the TopoDiff dataset [13], used as ground truth for compliance error (Sec. 5 Dataset; CE definition p. 7). Table 9 also runs SIMP for only 5 or 10 iterations as a comparator.", "implementation": "not stated in this article (reference designs taken from [13])", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "64×64 domain (Sec. 3; Sec. 5 Setup) [inferred ≈8.4×10³ DOFs]; 30,000 optimized training topologies; number of test configurations per task not stated", "classical_iterations": "not stated for the SIMP references; Table 9 SIMP comparator runs 5 or 10 iterations; the refinement step is SIMP(10)", "classical_time": "not stated", "ml_time": "TopoDiff-FF + SIMP(10): sampling 2.23, processing 0.32, total inference 2.55 (seconds per Fig. 9 legend; Table 5); 100 sampling st

## P00875 (decision order 35) — Learning topology optimization process via convolutional long‐short‐term memory autoencoder‐decoder (2023)

- Link: https://doi.org/10.1002/nme.7221
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (Abstract (the only text read)): Not coded (no accessible full text). Abstract only: a ConvLSTM encoder-decoder, fed the first SIMP iterations, predicts the rest of the optimization path, claiming a large computation-cost reduction for a small loss in design performance.
- Key phrase: 
- Claimed speed-up: None (Not coded; the abstract gives no numbers.)

- **R1 = na** [] — no full text
- **R2 = na** [] — no full text
- **R3 = na** [] — no full text
- **R4 = na** [] — no full text

- Baseline: {}

## P00042 (decision order 38; provisional top-up 73) — Variational Quantum Latent Encoding for Topology Optimization (2025)

- Link: https://arxiv.org/abs/2506.17487
- Access: full_text; inclusion: **exclude** (FT-MLONLY; prefill label: FT-MLONLY); stratum: **none**
- Primary outcome (Abstract; Sec. 5, Tables 1-3; Sec. 6 Conclusion): Not coded (excluded). Headline: over 10 runs each on three 60x30 benchmarks, quantum-circuit latents give compliance and design diversity close to Gaussian latents in the same neural-field pipeline, with small differences in both directions (e.g. compliance 90.83 vs 92.60 with 5 qubits, Table 1).
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded at full text). No run time of any method is reported; the comparison of loss-based regularization with density filtering plus Heaviside projection is in iterations only (about 200 vs up to 500; Sec. 5.2).)

- **R1 = na** [excluded] — excluded at full text (FT-MLONLY)
- **R2 = na** [excluded] — excluded at full text (FT-MLONLY)
- **R3 = na** [excluded] — excluded at full text (FT-MLONLY)
- **R4 = na** [excluded] — excluded at full text (FT-MLONLY)

- Baseline: {}

## P00550 (decision order 40) — Machine learning for topology optimization: Physics-based learning through an independent training strategy (2022)

- Link: https://arxiv.org/abs/none found
- Access: no_access; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (not available): Not coded: no accessible full text.
- Key phrase: 
- Claimed speed-up: None (no full text)

- **R1 = na** [] — no full text
- **R2 = na** [] — no full text
- **R3 = na** [] — no full text
- **R4 = na** [] — no full text

- Baseline: {}

## P00983 (decision order 42) — A function online learning and prediction method for accelerating structural topology optimization and its application to pneumatic soft actuator (2025)

- Link: https://doi.org/10.1016/j.tws.2025.112942
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (abstract only): Not coded (no full text). The abstract claims that FoLap, a one-hidden-layer network that learns and predicts design-function updates online, saves up to 65.1% of total computing time for a soft-actuator cell design versus level-set and moving-isosurface-threshold TO.
- Key phrase: 
- Claimed speed-up: None (not coded (no full text). The abstract states a total time saving of up to 65.1% against the selected level-set and moving isosurface threshold methods [≈2.9× derived as 1 ÷ (1 − 0.651); not checked against the article])

- **R1 = na** [no-full-text] — no full text
- **R2 = na** [no-full-text] — no full text
- **R3 = na** [no-full-text] — no full text
- **R4 = na** [no-full-text] — no full text

- Baseline: {}

## P00605 (decision order 43) — Fast topology optimization of phononic crystal‐based metastructures for vibration isolation by deep learning (2023)

- Link: https://doi.org/10.1111/mice.13100
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (Abstract (the only text read)): Not coded (no accessible full text). Abstract only: the deep-learning-based optimization (DLBO) reaches bandgap results similar to or better than a genetic algorithm while needing 0.01% of the GA's time.
- Key phrase: 
- Claimed speed-up: None (Not coded. Would-be value from the abstract: 0.01% of the GA time corresponds to a factor of 10,000 [derived: 1 ÷ 0.0001]; the GA and DLBO times themselves are not in the abstract.)

- **R1 = na** [] — no full text
- **R2 = na** [] — no full text
- **R3 = na** [] — no full text
- **R4 = na** [] — no full text

- Baseline: {}

## P01151 (decision order 44) — Two-scale topology optimization of multiscale structures and materials via deep neural networks for local and global buckling (2026)

- Link: https://doi.org/10.1016/j.cma.2026.119038
- Access: no_access; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (title only): Not coded (no full text and no abstract available). Only the title is known: deep neural networks are used in two-scale topology optimization of structures and their materials under local and global buckling.
- Key phrase: 
- Claimed speed-up: None (not coded (no full text))

- **R1 = na** [no-full-text] — no full text
- **R2 = na** [no-full-text] — no full text
- **R3 = na** [no-full-text] — no full text
- **R4 = na** [no-full-text] — no full text

- Baseline: {}

## P00808 (decision order 45) — A Geometric-Enhanced Neural Network Method for Scalable and High-Resolution Topology Optimization (2026)

- Link: https://arxiv.org/abs/none found
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (Abstract (Crossref metadata)): Not coded (abstract only). The abstract claims better computational efficiency than traditional and other neural-network TO methods, and a 256 m bridge with millions of DOFs optimized in under ten minutes on a standard PC; no comparison numbers are given.
- Key phrase: 
- Claimed speed-up: None (no full text)

- **R1 = na** [] — no full text
- **R2 = na** [] — no full text
- **R3 = na** [] — no full text
- **R4 = na** [] — no full text

- Baseline: {}

## P00143 (decision order 46; provisional top-up 4) — Improving Solar Cell Metallization Designs using Convolutional Neural Networks (2021)

- Link: https://arxiv.org/abs/2104.04017
- Access: full_text; inclusion: **exclude** (FT-DOMAIN; prefill label: FT-DOMAIN (electrical conduction in solar-cell metallization; outside the §3.1 physics list)); stratum: **none**
- Primary outcome (Section 4 Results, Figs. 2-3 (abstract, introduction and conclusion hold only qualitative comparisons)): Not coded (excluded: physics out of scope). Would-be primary outcome: on square cells with four busbar layouts, SolarNet designs reached higher efficiency than density-based TO, by up to 0.42 percentage points (3.5% relative); triangular cell 12.67% vs 12.31%.
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded at full text); no runtime of either method is reported anywhere in the article.)

- **R1 = na** [] — excluded at full text
- **R2 = na** [] — excluded at full text
- **R3 = na** [] — excluded at full text
- **R4 = na** [] — excluded at full text

- Baseline: {}

## P00663 (decision order 47) — Topology Optimisation under Uncertainties with Neural Networks (2022)

- Link: https://doi.org/10.3390/a15070241
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (Sec. 4.1.3, Table 1 (p. 22): first quantitative comparison with the classical optimizer (iterations, J, compliance); the matching times are in Table 4 (p. 28). The abstract, conclusion and introduction compare only qualitatively): Deterministic 2D bridge, nominal load: inserting CNN-predicted gradient steps every 55 iterations cut convergence from 538 to 441 iterations, with lower compliance (1148.66 vs 1173.22) and run time 4 min 05 s vs 4 min 43 s.
- Key phrase: the NN prediction of the gradient step clearly outperforms the classical optimisation method
- Claimed speed-up: 1.16 (Derived, no factor is stated: Table 4 (p. 28), nominal load, 4 min 43 s (283 s, classical Algorithm A1) ÷ 4 min 05 s (245 s, CNN Algorithm 1) = 1.155; times are averages of 10 runs (Sec. 4.1.3, p. 21). Iteration ratio 538 ÷ 441 = 1.22 (Table 1). Over the five loads in Table 4 the CNN time ratio is 1.03-1.16 [derived]. Data generation and training are not in the times and are not reported.)

- **R1 = pass** [R1-matched] — Tables 1 and 4: both optimizers solve the same problem with the same volume constraint (m = 0.4) and the same convergence criterion (Eq. A1), and the CNN-assisted design has lower J and compliance at the nominal load, so the time gain (4 min 05 s vs 4 min 43 s) does not come with worse quality. Achieved volumes are not reported. For two of five loads (Table 4) the CNN design is about 0.6% worse in compliance [derived] while faster; a verifier who weighs those cases may choose partial.
- **R2 = pass** [R2-none-established] — Sec. 4 and App. B: the baseline is the authors' own phase-field optimizer (refs [1,2]) in the same FEniCS code, and the NN steps are inserted into the same loop, so implementation and hardware are shared [inferred]; hardware and linear solver are not stated. The mesh has up to about 15,000 vertices [≈3×10⁴ DOFs, derived], so (c) does not apply; (b) not observed (no figure in the abstract); (d) not applicable (convergence-based stopping). A per-iteration time is derivable (283 s ÷ 538 ≈ 0.53 s, adaptive mesh [derived]), but the phase-field gradient flow differs from a SIMP strong baseline, so (e) is hard to apply. Unsure, so pass.
- **R3 = fail** [R3-no-cost] — Sec. 4.1.1 and 4.2.1: the networks are trained on sample paths of the classical optimizer (S runs with random load rotations, up to 500 iterations each), but S, the data-generation time and the training time are not reported, and no break-even is given. The claim is not limited to per-query use. For C3: the saving is about 38 s per run at the nominal load (Table 4) [derived], so each training path (about one classical run [inferred]) needs roughly 7 uses to pay back [derived].
- **R4 = partial** [R4-no-failure-rate] — Tables 1-4: J and compliance come from the FE state solve of the converged designs, which continue with classical steps after each NN step [inferred]. Achieved volume is not reported. Topology collapse for an unsuitable insertion interval c_m or for loads far from the training data is described only qualitatively (Sec. 4.1.4, 4.4), with no counts. The extra loads are a hand-picked selection of extreme cases (three in Sec. 4.1.4 and Table 3; a fourth appears only in Table 4).

- Baseline: {"classical_method": "Phase-field TO: Allen-Cahn gradient flow with a Ginzburg-Landau interface penalty, adaptive step size and adaptive mesh refinement (Algorithm A1, the authors' refs [1,2]); risk-averse CVaR variant with 224 Monte Carlo samples per iteration (Algorithm A2) (Sec. 2, App. A-B)", "implementation": "Authors' Python code on FEniCS with first-order triangles; the NN steps are inserted into the same optimization loop (Sec. 4, App. B). Public repository (FEniCS 2019.1 and PyTorch per its requirements file)", "solver": "not stated", "hardware_classical": "not stated (WIAS IT infrastructure acknowledged)", "hardware_ml": "not stated", "problem_size": "2D bridge on D = [-1,1] × [0,1], adaptive triangular mesh refined up to about 15,000 vertices (Sec. 4.1.3, p. 20); NN reference grid 201 × 101 nodes (Example 1, p. 11) [derived: up to about 3×10⁴ DOFs]", "classical_iterations": "R

## P01517 (decision order 49) — A Multi-Grid, Single-Mesh Online Learning Framework for Stress-Constrained Topology Optimization Based on Isogeometric Formulation (2025)

- Link: https://doi.org/10.32604/cmes.2025.072447
- Access: full_text; inclusion: **include** (I-SPEED (screened I-UNCLEAR; the first quantitative classical comparison reports total run times against the same isogeometric TO without the surrogate, Sec. 5.1, Table 1)); stratum: **speed**
- Primary outcome (Sec. 5.1 and Table 1 (first quantitative comparison with the classical TO-IGA run; the abstract and conclusion compare only qualitatively, and the introduction cites other studies' results only). Sec. 5.2.4 states the Table 1 speed-up as 1.23): On two 2D stress-constrained L-bracket problems (103×52 control points), FNO online learning cut IGA evaluations from 210 to 150 and total time by about 20% (2540.44 to 2062.78 s; 2429.20 to 2058.63 s) at matching volume and maximum stress.
- Key phrase: reducing the total computational time by about 20%
- Claimed speed-up: 1.23 (Stated in Sec. 5.2.4 as the speed-up of Table 1. Derived from Table 1: case (a) 2540.44 s ÷ 2062.78 s = 1.23; case (b) 2429.20 s ÷ 2058.63 s = 1.18. Both totals are wall-clock times on the same machine and code; the online-learning total is taken to include FNO training [inferred: Sec. 5.1 reports the whole run time].)

- **R1 = pass** [R1-matched] — Sec. 5.1, Table 1 and Fig. 10: both methods run the same code, formulation and stopping rule (210 iterations or mean design change below 1e-3) on one machine, and the online-learning designs match the baseline (volume 0.1489 vs 0.1500 and 0.1464 vs 0.1465; max stress 24.9176 vs 25.2465 and 24.9528 vs 24.9757 against a 25 Pa limit). The time comparison is therefore made at matched design quality. No post-processing is applied to either design.
- **R2 = partial** [R2-inefficient-impl] — Sec. 5, Table 1: the baseline is the authors' in-house MATLAB isogeometric TO code, the same code the online framework calls. It takes about 12.1 s per iteration at 10,712 DOFs [derived: 2540.44 s ÷ 210], and Sec. 4 names the stress-sensitivity step as the most time-consuming step. This looks slow for the size [inferred]; the article itself cites efficiency-oriented MATLAB IGA-TO implementations ([18], [19]), but no direct comparison is possible. A faster baseline would shrink the saving, because the FNO overhead stays fixed [inferred]. (c) does not apply (at most 4.2×10⁴ DOFs [derived]); (b) and (d) are not observed (no abstract figure; both methods share the 210-iteration cap, and Fig. 10 shows the volume still falling until about iteration 170 [read from plot]). Unsure alternative: pass.
- **R3 = na** [R3-na-per-problem-learning] — Sec. 4 and 5.1: the FNO is trained online on data from the same optimization run (warm-up n0 = 20 IGA iterations, then n1 = 10 IGA and n2 = 5 FNO iterations per block, 150 epochs per training), with no offline dataset or pretraining. Its cost sits inside the total times compared under R1 [inferred: Sec. 5.1 reports the whole run time].
- **R4 = pass** [R4-FE-verified] — Tables 1, 2, 4 and 5: volume fraction and maximum von Mises stress are reported for every returned design, with stress plots at the Gauss points; they come from IGA analysis of the final design [inferred from Sec. 4, where the design at the last iteration is evaluated]. Constraint satisfaction is visible for each case, including small overshoots of the stress limit by both methods (e.g. online learning 40.4327 vs 40 Pa, Table 2). All runs are shown; failed runs are neither reported nor discussed, and each case is a single run. Unsure, so pass.

- Baseline: {"classical_method": "The same isogeometric density-based TO without the surrogate, which the authors treat as the ground truth: quadratic NURBS, volume minimization under a p-norm (p = 8) von Mises stress constraint, Shepard filter, tanh projection, adjoint sensitivities, MMA (Sec. 3, 5)", "implementation": "In-house MATLAB 2020b code; the online-learning part runs in Python 3.8 with PyTorch 1.10.2 (Sec. 5)", "solver": "not stated", "hardware_classical": "One workstation for all runs: Intel i7-11700 CPU, 16 GB RAM, NVIDIA RTX 3060 (12 GB), Windows 10 Pro (Sec. 5); the device used by the MATLAB IGA code is not stated [CPU inferred]", "hardware_ml": "Same workstation (Sec. 5); FNO on the RTX 3060 [inferred; not stated per method]", "problem_size": "L-bracket 103×52 control points, padded to 104×52 for the FNO (Sec. 5.1) [derived: 10,712 DOFs]; extra cases 63×48 and 207×102 control points 

## P00141 (decision order 51; provisional top-up 31) — GANTL: Towards Practical and Real-Time Topology Optimization with Conditional GANs and Transfer Learning (2021)

- Link: https://arxiv.org/abs/2105.03045
- Access: full_text; inclusion: **include** (I-QUALITY); stratum: **quality**
- Primary outcome (Sec. 4.2 para 3 and Table 2 (first quantitative comparison with a classical method; the abstract, conclusion and introduction hold none)): For seen boundary conditions with one random load, GANTL predictions at six resolutions (40×80 to 200×400) differ from the SIMP designs by 1.00% average compliance error (std 2.5%), 2.12% MSE and 96.72% binary accuracy.
- Key phrase: with a 1% average compliance error and a 2.5% standard deviation
- Claimed speed-up: None (Not derivable. No GANTL inference, training or data-generation time is reported anywhere (full text read). The only classical timing is cited, not measured: the SIMP code of [4] needs 1.85 s per iteration and hundreds of iterations for a 300×100 MBB beam (Sec. 1 para 1).)

- **R1 = partial** [R1-loose] — Tables 2-5, Sec. 3.4-3.5, 4.2: predictions are compared with SIMP designs for the same loads, BCs and prescribed volume fraction 0.5, but the achieved volume fraction of the predictions is not reported, the SIMP penalty value and stopping rule are not stated, and no run time exists on either side, so no budget is matched. No speed claim is quantified. [judgment] na is the alternative if R1 is read as applying only to speed comparisons (precedent: P00182, P00358).
- **R2 = pass** [R2-none-established] — Sec. 3.4, 4.1: the SIMP references come from the public 88-line MATLAB code [4] with volume fraction 0.5 and filter radius 1.5; penalty, stopping rule, linear solver and hardware per method are not stated. Nothing indicates an unconverged or weakened SIMP reference. Quality stratum; unsure, so pass. The cited 1.85 s per iteration (Sec. 1) is not used in any comparison.
- **R3 = na** [R3-na-quality-stratum] — No quantified speed claim against a classical method. For C3: 11,000 + 1,500 SIMP training cases (Sec. 3.4, 4.1); no data-generation, training or inference time is reported; the conclusion refers the data-generation cost to [5] (Sec. 5).
- **R4 = partial** [R4-no-constraint-report] — Tables 2-5: compliance error against SIMP is reported for every test set (250-7,473 cases per row), with MSE and binary accuracy; compliance of predictions presumably from FE analysis [inferred; method not stated]. The volume fraction of predictions is not reported, and disconnected predictions are acknowledged (Sec. 4.3) but not counted. The topology-loss improvement (Fig. 11) rests on examples shown without a stated selection rule.

- Baseline: {"classical_method": "SIMP compliance minimization with the 88-line MATLAB code [4] (Andreassen et al. 2011), modified to automate data generation; volume fraction 0.5, filter radius 1.5; one point load with components sampled uniformly in [-100, 100] N; BCs of Fig. 5(a)-(b) for training. The SIMP designs are the ground truth for training and testing (Sec. 3.4, 4.1)", "implementation": "MATLAB 88-line educational code [4], modified for batch generation (Sec. 3.4, 4.1); initial-domain stress and strain-energy input channels computed with SolidsPy in Python (Sec. 3.4)", "solver": "not stated", "hardware_classical": "not stated per method; all experiments ran on the UConn HPC cluster (RHEL7), with no CPU or GPU given (Sec. 3.5)", "hardware_ml": "not stated per method; same cluster (Sec. 3.5)", "problem_size": "2D rectangular domains: source network 40×80; target networks 80×160, 120×160, 12

## P00092 (decision order 58; provisional top-up 90) — Topology optimization with text-guided stylization (2023)

- Link: https://arxiv.org/abs/2310.15506
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-UNCLEAR; the only quantitative classical comparison is compliance and volume against SIMP, with no SIMP runtime, §5.1 rule 2)); stratum: **quality**
- Primary outcome (Sec. 4.1 'Mechanical performance', p. 10, and Fig. 6 (first quantitative classical comparison; the abstract, conclusion and introduction hold no quantitative classical comparison, §5.1 rule 2)): With only the mechanical loss active, the hash-encoded neural field reaches nearly the same compliance as SIMP on three 2D benchmarks at matched volume. Bridge: 181.08 vs 181.06; MBB: 40.80 vs 39.48; L-bracket: 177.23 vs 169.80.
- Key phrase: our method shares a similar topology optimization performance to SIMP
- Claimed speed-up: None (Not applicable: no SIMP runtime is reported. Only the proposed method is timed: 0.587 s per iteration, 58.66 s for 100 iterations, for a 256x256 bridge on a laptop RTX 4080 GPU (Sec. 4.1 'Computational cost', Fig. 11). Sec. 5 states qualitatively that its convergence speed is below that of traditional explicit methods.)

- **R1 = partial** [R1-loose] — Sec. 4.1, p. 10: SIMP uses the same penalty (p = 2.0), the filter radius was tuned, and the achieved volumes match within 0.002. Matching is loose: SIMP's iteration count, stopping rule and FE resolution are not stated, while the proposed method stopped at 100 iterations. The target volume fraction of each task is not given, and one run per method and task is compared, although the method varies by about ±3% across random initializations (Sec. 4).
- **R2 = pass** [R2-none-established] — Quality stratum, competence of the comparator: SIMP is the public DTU Python code with a tuned filter radius, and it gives the lower compliance in all three tasks (Sec. 4.1), so nothing points to an under-converged comparator. Its solver, hardware and iterations are not stated. No runtime is compared, so markers (a)-(e) do not bear. Unsure, so pass.
- **R3 = na** [R3-na-quality-stratum] — Primary outcome is quality only, and the method learns per problem with no offline training or dataset (Sec. 4, 'Gradients computation'). For C3: 0.587 s per iteration at 256x256 on an RTX 4080 laptop GPU (Sec. 4.1, Fig. 11); 100-500 iterations per design.
- **R4 = pass** [R4-FE-verified] — Sec. 4.1 and Fig. 6: compliance and volume are reported for SIMP and both variants of the method on all three tasks, from FE analysis (the method's own FE on the pooled 64x64 field [inferred]). The volumes of the Lmech-only designs match SIMP's within 0.002, so the volume constraint is met as closely as SIMP's (targets not stated). For the full-loss variant, the connectivity loss removes disconnected parts and stays at zero after about 100 iterations (Fig. 6; Sec. 4.1); no disconnection check is reported for the Lmech-only variant, which has no such loss. The three tasks are standard benchmarks, not selected outputs, with one run each. Unsure whether compliance is evaluated after thresholding; pass.

- Baseline: {"classical_method": "SIMP compliance minimization with the 165-line Python code by Aage and Johansen (cited as Andreassen et al. 2011); penalty p = 2.0 to match the proposed method; sensitivity filter radius tuned to 1.5 (Sec. 4.1, pp. 9-10)", "implementation": "public DTU 165-line Python SIMP code (Sec. 4.1); the proposed method uses PyTorch with an algebraic multigrid solver (PyAMG cited) for its FE solves (Sec. 4, 'Experiment environment')", "solver": "not stated for SIMP; algebraic multigrid for the proposed method (Sec. 4)", "hardware_classical": "not stated [same laptop inferred]", "hardware_ml": "laptop PC, Intel Core i9-13900HX CPU and NVIDIA RTX 4080 GPU, Windows 11, Python 3.9; most computation on the GPU (Sec. 4)", "problem_size": "FE analysis at 64x64 after 4x4 average pooling of the 256x256 design field; stylization at 256x256 (Sec. 4.1); SIMP resolution not stated [64x64 i

## P00139 (decision order 61; provisional pilot 5) — DNN-Based Topology Optimisation: Spatial Invariance and Neural Tangent Kernel (2021)

- Link: https://arxiv.org/abs/2106.05710
- Access: full_text; inclusion: **exclude** (FT-MLONLY; prefill label: FT-ML-only); stratum: **none**
- Primary outcome (n/a): None: the article reports no speed or quality comparison with a classical method. Its experiments compare DNN density parameterizations with and without the proposed coordinate embeddings (Figs. 4, 8-9).
- Key phrase: 
- Claimed speed-up: None (not applicable (excluded at full text))

- **R1 = na** [excluded] — excluded at full text
- **R2 = na** [excluded] — excluded at full text
- **R3 = na** [excluded] — excluded at full text
- **R4 = na** [excluded] — excluded at full text

- Baseline: {}

## P02074 (decision order 64) — UDHF-SMERO: a unified deep hybrid framework for co-evolutionary smart material design and energy-adaptive structural optimizations (2026)

- **FLAG — exclusion check: Comparator numbers cannot be traced to any described experiment (BESO bridge, smart grid, antenna studies). FT-OTHER or FT-SCOPE possible.**
- Link: https://arxiv.org/abs/none found
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-UNCLEAR; the first quantitative comparison including a classical method is prediction accuracy, Table 2)); stratum: **quality**
- Primary outcome (Sec. 5 Conclusion (first quantitative comparison: superiority with average R² 0.96, citing Table 2); Table 2, p. 11. The abstract reports only the method's own metrics; the introduction has no comparison of this method): The framework's topology-to-performance mapping reaches an average R² of 0.96 over three load scenarios, versus 0.82, 0.84 and 0.86 for Method [3] (a cited BESO bridge study), Method [8] and Method [25] (Table 2).
- Key phrase: the framework was demonstrated to be superior based on multiple evaluation metrics
- Claimed speed-up: None (No speed-up is claimed. Sec. 4.4 states that the whole pipeline takes about 0.82 s per sample on an RTX-class GPU versus 0.34 s for unnamed traditional TO models, i.e. 2.4× slower (stated); no method, size or hardware is given for the 0.34 s.)

- **R1 = partial** [R1-loose] — Sec. 4, p. 11 and Table 2: the comparison is said to use the same conditions and data split. No implementation, budget, stopping rule or hardware is given for Methods [3], [8] or [25]. A BESO run [3] has no performance-prediction R² [inferred], so the matching cannot be checked.
- **R2 = pass** [R2-none-established] — The comparators are cited, not described: no implementation, solver or hardware (Sec. 4). (b) not observed: the abstract has no comparator figure. (c) cannot be established: the ML runs on RTX-class GPUs, the problem has ≈2.2×10⁵ DOFs [derived], but the comparator hardware is not stated. (d) and (e) are not derivable. Unsure, so pass.
- **R3 = na** [R3-na-no-speed-claim] — The primary outcome is prediction accuracy, and Sec. 4.4 concedes a slower pipeline (0.82 s vs 0.34 s per sample). For C3: no training time or data-generation cost is reported; only epoch counts and a 35% training-time reduction from mixed precision (Sec. 4, 4.4).
- **R4 = fail** [R4-similarity-metric] — Table 2 and Sec. 5: quality rests on agreement scores, i.e. R² between predicted and FEM performance and reconstruction accuracy (%) in Tables 2 and 4. No FE-computed objective, volume or constraint satisfaction of returned designs is reported, and no failed designs are counted. The case study (Sec. 4.7) gives only agreement percentages.

- Baseline: {"classical_method": "Method [3] = Lai et al. 2024, BESO design of a pedestrian bridge: the only named classical TO comparator. Methods [8] (Wang 2023, evolutionary optimization for smart-grid nanoparticle analysis) and [25] (Ghali et al. 2024, conformal antenna design optimization) complete the comparator set; the article says the three align with conventional TO, inverse design and structural simulation (Sec. 4, p. 11). How any of them was applied to this dataset is not described", "implementation": "not stated", "solver": "not stated (FEM is used as ground truth; solver unspecified)", "hardware_classical": "not stated", "hardware_ml": "NVIDIA RTX-class GPUs with mixed precision; model not stated (Sec. 4, p. 11; Sec. 4.4)", "problem_size": "64×64×16 voxel design tensor with six material features (Sec. 4, 4.6, 4.7) [≈2.2×10⁵ nodal DOFs for 3D elasticity, derived]; extended dataset of mo

## P00893 (decision order 68) — Deep learning-aided topology design of metasurfaces for Rayleigh waves (2024)

- Link: https://doi.org/10.1093/jcde/qwae037
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (abstract only): Not coded (no full text). The abstract says a VAE latent space plus a conditional tandem network designs Rayleigh-wave-isolating metasurfaces for target frequency ranges, validated by 100 tests with determination coefficients above 0.99; no classical comparator is named.
- Key phrase: 
- Claimed speed-up: None (not coded (no full text); the abstract claims improved design efficiency without a number or a named classical comparator)

- **R1 = na** [no-full-text] — no full text
- **R2 = na** [no-full-text] — no full text
- **R3 = na** [no-full-text] — no full text
- **R4 = na** [no-full-text] — no full text

- Baseline: {}

## P00860 (decision order 69) — AI-Based Topology Optimization of Freehand Sketches (2021)

- Link: https://doi.org/10.1016/j.procir.2021.11.221
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (Abstract (the only text read)): Not coded (no accessible full text). Abstract only: a neural network reads photographed design sketches and generates lightweight structures matching the sketched load cases; the abstract states no comparison with a classical method.
- Key phrase: 
- Claimed speed-up: None (Not coded; the abstract gives no numbers and no comparison.)

- **R1 = na** [] — no full text
- **R2 = na** [] — no full text
- **R3 = na** [] — no full text
- **R4 = na** [] — no full text

- Baseline: {}

## P01994 (decision order 73) — Practical topology optimization with deep reinforcement learning (2025)

- **FLAG — exclusion check: Registered as a ResearchGate preprint (fails PROTOCOL 3.3, FT-OTHER); may also be an earlier version of P01997 (FT-DUPLICATE). Not readable by the coder.**
- Link: https://doi.org/10.13140/rg.2.2.16548.95369
- Access: no_access; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (title only): Not coded (no full text and no abstract available). Only the title is known: deep reinforcement learning applied to topology optimization with a practical focus.
- Key phrase: 
- Claimed speed-up: None (not coded (no full text))

- **R1 = na** [no-full-text] — no full text
- **R2 = na** [no-full-text] — no full text
- **R3 = na** [no-full-text] — no full text
- **R4 = na** [no-full-text] — no full text

- Baseline: {}

## P02361 (decision order 74) — Distributed design optimization of multi-component systems using meta models and topology optimization (2024)

- Link: https://arxiv.org/abs/none found
- Access: full_text; inclusion: **include** (I-QUALITY (screening code confirmed at full text)); stratum: **quality**
- Primary outcome (Abstract (quantitative comparison with a classical method); numbers in Table 5, p. 16 (P2, 12.9%) and Table 3, pp. 12-13 (P1, 3.87-8.18%); restated in Sec. 8): Designs from the meta-model-based decoupled architecture (system optimization with learned feasibility and mass estimators, then independent component TO) are feasible but up to 12.9% heavier than monolithic TO of the whole system.
- Key phrase: at most 12.9% heavier than those of a monolithic optimization
- Claimed speed-up: None (No runtime is reported for either approach; Sec. 7 states that time was not investigated and that meta-model training is not counted. The conclusion says only that computation time may be significantly reduced (qualitative).)

- **R1 = partial** [R1-loose] — Tables 3 and 5: both approaches solve the same problems with the same design domains, P1 mesh, material and 1 mm displacement limit, and both designs are feasible, so mass is compared at matched constraints. The stopping rules of the monolithic run and the component runs are not stated, which the protocol lists as loose matching. The comparison disfavors the ML approach; pass is defensible if the shared setup is given more weight.
- **R2 = na** [R2-na-quality-only] — No runtime of either approach is reported (Sec. 7), and no speed claim is quantified, so the efficiency criteria (a)-(e) do not apply. The monolithic baseline is the authors' own MATLAB SIMP formulation on the same model.
- **R3 = na** [R3-na-no-speed-claim] — No quantified speed claim. For C3: neither sampling (component TO runs) nor meta-model training cost is reported; Sec. 7 calls the offline database computationally expensive and says training is excluded from the time argument.
- **R4 = pass** [R4-FE-verified] — Tables 3 and 5: mass and end-effector displacement are reported for the returned component designs of both approaches. The displacement is computed from the condensed FE stiffness of the detailed designs [inferred from Sec. 3.2]. Constraint satisfaction is reported for every case (0.99-1.00 of the limit), and all final designs are feasible (Sec. 5.4, 6.4). A failed temporary classifier during sampling is disclosed (Sec. 6.2).

- Baseline: {"classical_method": "Monolithic SIMP-based topology optimization of all components together: minimum mass subject to the end-effector displacement requirement for every load case (approach A, Eq. 4). The component optimizations use SIMP (p = 3, sensitivity filter r = 2) with MMA (Sec. 3.2); the optimizer used for A is not stated [same tools inferred]", "implementation": "MATLAB (replication statement); custom code, not released", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "P1: two components, each a 30×30×100 mm box meshed with 20×8×8 brick elements (Sec. 5.1) [1,280 elements per component, derived]; P2: four components 30×30 mm in section, lengths 150/100/50/50 mm, 100 load cases (Sec. 6.1); P2 mesh not stated", "classical_iterations": "not stated", "classical_time": "not reported (Sec. 7)", "ml_time": "not reported (Sec. 7)

## P00335 (decision order 76; provisional top-up 35) — Constructing Boundary-identical Microstructures via Guided Diffusion for Fast Multiscale Topology Optimization (2024)

- Link: https://arxiv.org/abs/2406.16066
- Access: full_text; inclusion: **exclude** (FT-NOBASELINE; prefill label: FT-NOBASELINE); stratum: **none**
- Primary outcome (Abstract; Sec. 1 (contributions); Sec. 4.5.3 and Fig. 20; Sec. 5): Not coded (excluded). Headline: a guided diffusion model builds 16 boundary-identical microstructure datasets; each multiscale design (e.g., a 30×30 mechanical cloak) then finishes in under one minute; no classical method is run, timed or cited.
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded at full text). Only the proposed pipeline is timed (Fig. 20, PDF p. 24): 35.49-39.55 s for the Fig. 15 designs, 34.23-40.80 s for the Fig. 16 designs, 16.54 s and 28.22 s for the Fig. 19 designs. The acceleration over unnamed state-of-the-art methods (Sec. 1) and the time burden of the data-driven approach [30] (Sec. 4.5.3) are not quantified.)

- **R1 = na** [excluded] — excluded at full text (FT-NOBASELINE)
- **R2 = na** [excluded] — excluded at full text (FT-NOBASELINE)
- **R3 = na** [excluded] — excluded at full text (FT-NOBASELINE)
- **R4 = na** [excluded] — excluded at full text (FT-NOBASELINE)

- Baseline: {}

## P00150 (decision order 81; provisional top-up 12) — An Artificial Intelligence–Assisted Design Method for Topology Optimization without Pre-Optimized Training Data (2021)

- **FLAG — R2 check: Timing hardware not stated (R2 pass or partial). The journal version's numbers differ from arXiv v2 (259x against 225x).**
- Link: https://arxiv.org/abs/2012.06384
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (Sec. 3.2 Results and Discussion, p. 16, Fig. 14a (first quantitative comparison with a classical method; Abstract, Conclusions and Introduction hold only qualitative comparisons)): On 100 random 64×64 validation cases, the trained PEN predictor returns a design in about 7.3 ms on average versus 1.9 s for top88 SIMP, roughly 259 times faster, with compliance described as almost the same.
- Key phrase: requires, on average, 1.9 s (and is, therefore, roughly 259 times slower)
- Claimed speed-up: 259 (Stated in Sec. 3.2, p. 16: top88 1.9 s vs PEN 7.3 ms on average over the 100 validation cases, 'roughly 259 times'. The printed rounded times give 1.9/0.0073 = 260.3 [derived]. arXiv v2 states 8.4 ms and roughly 225 times for the same comparison.)

- **R1 = partial** [R1-loose] — Sec. 3.2, Fig. 14, Table 3, Fig. 15: PEN inference time is compared with complete top88 runs whose stopping rule is not stated. Quality is reported: FE compliance for all 100 cases (scatter only) and six printed pairs, in which PEN is 1.8-5.6% worse in five and 10.2% better in one [derived]. Volume is matched only approximately (ΔM up to 0.010 in the six printed cases; the constraint is a penalty, Sec. 3.2). No attempt is made to match top88 time or iterations to PEN quality.
- **R2 = partial** [R2-hardware-unjustified] — Neither the top88 timing hardware nor the PEN inference hardware is stated; Table 1 describes the GPU training machine only. PEN inference probably ran on the GPU and top88 on the CPU [inferred], but the problem is 64×64 (≈8.4×10³ DOFs [inferred]), so R2(c) does not apply. top88 is the vectorized efficient educational code, so no inefficiency is evident; solver and iteration count are not stated, so (d) and (e) cannot be judged; the abstract gives no baseline figure (b). Unsure between pass and partial; partial because the hardware choice is unstated and unjustified.
- **R3 = pass** [R3-full-accounting] — Sec. 3.3, Table 5, p. 19: training time T_P = 3.25 h is reported and folded into a break-even count e_BEP = 6226 predictions. There is no separate data-generation cost, because training uses random inputs evaluated by FE inside the training loop (Secs. 1, 2.8). Not included: the cost of the hyperparameter grid search that compared predictions with conventional TO results (Sec. 3.1).
- **R4 = partial** [R4-no-failure-rate] — Compliance of the returned PEN designs is computed by FE analysis (compliance evaluator, Sec. 2.3; Fig. 14b for all 100 cases). No post-processing is applied. Volume deviation ΔM is printed only for the six Fig. 15 examples (Table 3). No failure or infeasibility count is given, although the authors note that some geometries lack details (Sec. 3.2, Fig. 15 columns four and five).

- Baseline: {"classical_method": "SIMP compliance minimization with density filter, 88-line code (top88, Andreassen et al. [29]); p = 3, filter radius r_min = 3, Poisson's ratio 0.3, E = 195,000 N/mm², force 100 N (Table 2, p. 15; Sec. 3.2)", "implementation": "top88; the version of record cites only the MATLAB 88-line paper [29]. arXiv v2 says the validation designs came from the DTU TopOpt Python codes (v2 ref. [30]) [so probably a Python port; not stated in the version of record]", "solver": "not stated", "hardware_classical": "not stated (Table 1 gives the configuration used for training only)", "hardware_ml": "Training: Nvidia Titan RTX (24 GB), AMD Ryzen Threadripper 2950X 16-core, 128 GB RAM, TensorFlow 2.5.0, Python 3.7.3, Windows 10 (Table 1, p. 12). Hardware for the 7.3 ms inference timing not stated.", "problem_size": "64×64 elements (Table 5 caption, p. 19; Sec. 4) [inferred ≈8.4×10³ DOF

## P00842 (decision order 82) — Topology Optimization via Frequency Tuning of Neural Design Representations (2021)

- Link: https://doi.org/10.1145/3485114.3485124
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (abstract only): Not coded (no full text). The abstract says coordinate networks with Fourier feature mapping reach state-of-the-art compliance designs and allow frequency control of the design, mesh-independent results and sub-pixel filtering; the comparator is not named.
- Key phrase: 
- Claimed speed-up: None (not coded (no full text); the abstract makes no speed claim)

- **R1 = na** [no-full-text] — no full text
- **R2 = na** [no-full-text] — no full text
- **R3 = na** [no-full-text] — no full text
- **R4 = na** [no-full-text] — no full text

- Baseline: {}

## P00755 (decision order 83) — Artificial neural network supported design of a lattice-based artificial spinal disc for restoring patient-specific anisotropic behaviors (2023)

- **FLAG — FT-NOBASELINE candidate: The classical time (about 24 h) is an unexplained estimate, not a run. If an estimate does not count as timing, the record is FT-NOBASELINE.**
- Link: https://doi.org/10.1016/j.compbiomed.2022.106475
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text; the only classical comparison is an estimated run time of the same GA with FE fitness evaluation, Sec. 5.2)); stratum: **speed**
- Primary outcome (Sec. 5.2, p. 10 (first quantitative comparison with a classical method; the abstract, introduction and conclusion claim efficiency only qualitatively)): With the ANN replacing beam FE analysis as the GA fitness evaluator, one lattice-disc topology optimization finishes in about 40 s, versus an estimated 24 h for the same optimization driven by FE analysis.
- Key phrase: significantly more efficient compared to a FE-analysis-based optimization process
- Claimed speed-up: 2160 (Derived, not stated: about 24 h (86,400 s) ÷ about 40 s = 2,160 (Sec. 5.2, p. 10). The 24 h is an expected time, stated in the future tense; no FE-based optimization run is reported, and its basis (evaluations, time per FE analysis) is not stated. Data generation and training are excluded.)

- **R1 = fail** [R1-no-quality] — Sec. 5.2, p. 10: the 40 s ANN-driven optimization is set against an expected 24 h for the FE-driven optimization, which is not reported as run, so no classical design or objective exists to compare with. The ANN designs are checked by FE against the target stiffnesses only (Figs. 9, 12), not against an FE-driven GA result at matched quality or budget.
- **R2 = pass** [R2-none-established] — Sec. 3 and 5.2: both methods would use the same GA settings [inferred] and the same laptop-class CPU (i7-8550U), and no GPU is used, so (c) does not apply; (b) is not observed (no abstract figure). The 24 h estimate has no stated basis: if it assumes all 25,000 evaluations of Table 2 [derived], it implies about 3.5 s per six-load-case beam analysis [inferred], and Fig. 8 suggests that 100-150 of the 500 generations would suffice [read from plot]. But the same generation count applies to the 40 s run, so the ratio does not depend on it, and (d) is not established. The beam-model size is not stated, so efficiency cannot be judged. Unsure, so pass.
- **R3 = partial** [R3-no-data-cost] — Training times are reported (about 17 and 23 min per library, Sec. 4.2-4.3), but the cost of the 600,000 FE-analysed training designs per library (Sec. 3.1.4) is not, and no break-even is given; Sec. 5.3 only argues that data generation is a one-time cost. [derived] One library's 600,000 FE analyses equal 24 times the at most 25,000 fitness evaluations of one GA run (population 50 × 500 generations, Table 2), so break-even needs at least about 24 designs per library, before training time.
- **R4 = pass** [R4-FE-verified] — Sec. 3.3 and Figs. 9, 12, 14: every optimized design is re-analysed with the FE beam model and plotted next to the ANN prediction; all runs are shown, including the Library A designs that miss the torsional targets (Fig. 9). The problem has no volume constraint; member sizes are checked against the printer resolution (Sec. 5.1). Whether the post-sizing stiffnesses of Fig. 13 come from FE or from the uniform scaling rule is not stated. Unsure, so pass.

- Baseline: {"classical_method": "The same genetic-algorithm topology optimization of the unit-cell distribution with FE analysis as the fitness evaluator (Sec. 3.3, 5.2); referred to only as an expected time, with no run reported [inferred from the future-tense wording]", "implementation": "In-house MATLAB script for the FE analysis (1D Euler beam elements, linear elastic PEEK, six rotational load cases; Sec. 3.1.4); GA via the open-source Python library PyGAD (Sec. 3.3)", "solver": "not stated", "hardware_classical": "Intel Core i7-8550U CPU, 16 GB RAM, the machine for all computational tasks (Sec. 3, p. 3)", "hardware_ml": "Same machine for training and optimization (Sec. 3, p. 3)", "problem_size": "Grid of 15×3×2 = 90 grid-units (design variables), three unit-cell types per library (Sec. 3.1, Table 2); number of beam elements and DOFs not stated; a denser 25×4×2 grid is also tested (Sec. 5.1)", 

## P00149 (decision order 84; provisional pilot 6) — Data-driven topology optimization of spinodoid metamaterials with seamlessly tunable anisotropy (2021)

- Link: https://arxiv.org/abs/2012.15744
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text; comparator is FE homogenization inside FE²-type two-scale TO)); stratum: **speed**
- Primary outcome (Section 4.1, p. 11 (first comparison with a classical method in the main text; abstract, conclusion and introduction hold only qualitative claims); numbers in Appendix B, Table B.1, p. 23): The trained DNN surrogate returns a spinodoid RVE's homogenized stiffness in about 0.001 s per sample, versus roughly 5 min for FE homogenization, so stiffness evaluations inside the two-scale optimization become orders of magnitude cheaper.
- Key phrase: accurate stiffness predictions instantly compared to several minutes for FEM-based homogenization
- Claimed speed-up: 300000 (Derived by coder, not stated: Table B.1 FE homogenization 5 min (300 s, 16 MPI cores) ÷ DNN prediction 0.001 s (one sample, one CPU, no parallelization) = 300,000 per stiffness evaluation. The paper gives only an orders-of-magnitude statement and calls the runtimes a qualitative measure (Appendix B). This is not an optimization-level speed-up: no classical FE² or SIMP optimization runtime is reported.)

- **R1 = partial** [R1-loose] — Section 5.1, Figs. 5–6: surrogate accuracy vs FEM is reported (R² ≥ 0.996 stiffness, ≥ 0.999 sensitivities, 2,130 held-out samples), so quality is reported at the level of the speed claim. Matching is loose: the speed claim is per stiffness evaluation (Section 4.1; Table B.1); no FE²-type optimization was run to compare optimized designs or total time; the FE homogenization mesh and accuracy are not stated here; the authors call the runtimes only a qualitative measure (Appendix B).
- **R2 = pass** [R2-none-established] — Table B.1: FE homogenization uses an in-house C++ FEM code on 16 MPI cores (Euler IV), while the DNN runs on one CPU without parallelization. No GPU is used, so (c) does not apply; the abstract gives no baseline figure (b); no fixed iteration count applies (d). Solver type and RVE mesh are not stated; no inefficiency is evident. Unsure → pass.
- **R3 = partial** [R3-no-amortization] — Table B.1: DNN training 10 min; FE homogenization about 5 min per sample. Section 5.1: 19,170 training + 2,130 test samples. The total data-generation cost is never stated [inferred ≈1,775 h of 16-core time], and data and training were reused from Kumar et al. 2020a. No break-even is given. Appendix B frames the gain per prediction, but the conclusion's speed-up statement is not limited to per-query use.
- **R4 = partial** [R4-surrogate-predicted] — Surrogate outputs are checked against FEM on 2,130 held-out samples (Section 5.1). The optimized compliances of the returned designs (Figs. 7c, 10c, 12c, 14c) are computed with DNN-predicted stiffness; no FE homogenization or fully resolved FE re-check of the final design parameters is reported [inferred from Sections 3–5 and Appendix A], and the achieved relative density is not reported. Partial because the macroscale FE is real and the surrogate is independently validated; a stricter reading (design performance rests on the surrogate) gives fail.

- Baseline: {"classical_method": "FE computational homogenization of each spinodoid RVE (the step FE²-type concurrent two-scale TO repeats per element and iteration); single-scale SIMP (p = 4) as design-quality reference (Section 5.2)", "implementation": "Homogenization: in-house C++ FEM code (Table B.1). SIMP reference: not stated. ML side: PyTorch in Python; TO in Python with IPOPT (Section 3.1, Table B.1)", "solver": "not stated (homogenization and macroscale FE); optimizer IPOPT interior-point (Section 3.1)", "hardware_classical": "Euler IV cluster (ETH Zürich), two 18-core 2.7 GHz Intel Xeon Gold 6150, 192 GB; 16 MPI cores for FE homogenization (Table B.1, footnote c)", "hardware_ml": "DNN prediction and training: four 12-core 2.2 GHz Intel Xeon E5-2650, 256 GB, CPU without parallelization (Table B.1, footnote b); TO benchmarks: Euler IV CPU without parallelization (footnote c)", "problem_size"

## P00925 (decision order 85) — Generative Design by Reinforcement Learning: Maximizing Diversity of Topology Optimized Designs (2020)

- Link: https://arxiv.org/abs/2008.07119
- Access: full_text; inclusion: **exclude** (FT-DUPLICATE; prefill label: FT-DUPLICATE); stratum: **none**
- Primary outcome (Conclusion, p. 17 (the abstract compares only qualitatively with the earlier CPU approach); the same pairing opens Sec. 3 (10 min vs under 10 ms)): Not coded (excluded as an earlier version of P00158). Would-be primary outcome in this version: TopOpNet, a CNN stand-in for the wheel TO algorithm, answers in milliseconds, whereas the CPU algorithm needs on the order of 10 min.
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded as a duplicate). Would-be values as in P00158: about 10 min vs milliseconds (Conclusion) or under 10 ms (Sec. 3 opening), i.e. at least 6x10^4 [derived]; Sec. 3 end gives seconds for simple inputs vs under 1 ms on a GTX 1080 Ti.)

- **R1 = na** [excluded] — excluded at full text (FT-DUPLICATE of P00158)
- **R2 = na** [excluded] — excluded at full text (FT-DUPLICATE of P00158)
- **R3 = na** [excluded] — excluded at full text (FT-DUPLICATE of P00158)
- **R4 = na** [excluded] — excluded at full text (FT-DUPLICATE of P00158)

- Baseline: {}

## P00549 (decision order 88) — Deep learning aided topology optimization of phononic crystals (2023)

- **FLAG — scope check: Elastic-wave phononic design: decide whether this is excluded 'acoustic' TO (FT-DOMAIN). Same question for P00605 and P00893. Speed via a per-evaluation proxy.**
- Link: https://arxiv.org/abs/none found
- Access: full_text; inclusion: **include** (I-SPEED (screening code kept at full text; the only measured classical comparison is per dispersion-diagram evaluation, a cost proxy as in P00149)); stratum: **speed**
- Primary outcome (Sec. 4 Conclusions, pp. 12-13 (first quantitative classical comparison; the abstract and introduction are qualitative); supporting timing example in Sec. 2.1, p. 4 (about 47 min for one 134,040-DOF FEM run)): A CNN surrogate predicts a phononic unit cell's full dispersion diagram in under 100 ms, versus roughly 0.5-1 h for an FEM (COMSOL) calculation, so a genetic algorithm can use it inside the topology optimization loop.
- Key phrase: capable of predicting dispersion curves in less than 100 ms
- Claimed speed-up: 18000 (Derived lower bound: 0.5 h (1,800 s) ÷ 0.1 s = 18,000 (36,000 at 1 h; 28,200 for the 47 min example [derived]); the article gives no factor. Per evaluation, not per optimization; no GA+FEM run is timed. Against the ≈288 s per sample implied by the dataset generation (about one month for 9,000 samples) [derived], the ratio would be about 2,900 [derived].)

- **R1 = partial** [R1-loose] — Sec. 2.3, 2.6 and 4: surrogate accuracy is reported against FEM on all 300 test samples (Table 2), so quality is reported at the level of the claim. Matching is loose. The quoted 0.5-1 h (and the 47 min example) concern FEM runs that appear finer or slower than the simplified-geometry FEM that produced the training labels: the dataset works out to ≈288 s per sample [derived]. The article itself says the cavity geometry was simplified to cut COMSOL time. No optimization-level comparison exists.
- **R2 = partial** [R2-inefficient-impl] — Sec. 2.1, 2.3: the classical cost comes from general-purpose commercial FE (COMSOL via MATLAB LiveLink) on an 8-core CPU. The quoted per-evaluation time is 6-12× the ≈288 s implied by the authors' own dataset pipeline [derived], and the surrogate's hardware is not stated. (c) cannot be established: the example has 134,040 DOFs, but whether the surrogate ran on a GPU is not stated. (b) not observed: the abstract has no figure. (d) and (e) not applicable.
- **R3 = partial** [R3-no-training-cost] — Sec. 2.3: data generation is reported (about one month for 9,000 samples); training time is not, and no break-even is given. Sec. 1 notes qualitatively that the speed comes at the cost of supervised training. C3 [derived]: at ≈288 s per FEM sample, the data cost equals 9,000 FEM evaluations; at the quoted 0.5-1 h, 720-1,440 evaluations. One GA run allows up to 20,000 evaluations (400 × 50), so the data cost is repaid within about one run, training excluded.
- **R4 = partial** [R4-no-failure-rate] — Table 2: surrogate outputs are FE-checked on every test sample. Optimized cells are re-analysed with FEM, but only as curve overlays (Figs. 8-11); the Table 3 values are surrogate predictions. Wall-thickness feasibility is discussed (Sec. 3.2, Fig. 12); one surrogate misprediction is disclosed (Fig. 9) without a rate. A stricter reading gives fail: the two runs shown per objective were picked from several GA runs, with no stated selection rule (Sec. 3.2).

- Baseline: {"classical_method": "FEM computation of the dispersion diagram (Bloch-Floquet eigenvalue problem over Γ-X-M) in COMSOL Multiphysics: the forward solver a classical GA-based phononic TO would call for every candidate (Sec. 2.1, 4). No classical optimization run is timed or compared", "implementation": "COMSOL Multiphysics (commercial, general-purpose FE) driven by MATLAB LiveLink with GMSH meshes (Sec. 2.3)", "solver": "not stated (COMSOL eigenvalue solver)", "hardware_classical": "AMD Ryzen 7 1800X 8-core 3.8 GHz, 64 GB RAM for the 47 min example (Sec. 2.1); an unspecified desktop computer for the dataset (Sec. 2.3)", "hardware_ml": "not stated (Keras model imported into MATLAB, Sec. 3)", "problem_size": "3D aluminium unit cell, 8 mm × 8 mm × 3 mm, with one through-cavity (Sec. 2.2); timing example mesh 14,072 tetrahedra, 134,040 DOFs, 24 eigenmodes (Sec. 2.1); dataset mesh size not sta

## P02084 (decision order 89) — Hierarchical thermal design for battery packs using phase change materials (2026)

- Link: https://doi.org/10.1016/j.ijheatmasstransfer.2026.129081
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (abstract only): Not coded (no full text). The abstract says a generative latent-space fin design needs over 95% fewer design variables than pixel-wise TO, and claims gains in thermal performance and computational efficiency; no time comparison is given.
- Key phrase: 
- Claimed speed-up: None (not coded (no full text); the abstract's only quantitative comparison with pixel-wise TO is a design-variable reduction of over 95%, which is not a time ratio)

- **R1 = na** [no-full-text] — no full text
- **R2 = na** [no-full-text] — no full text
- **R3 = na** [no-full-text] — no full text
- **R4 = na** [no-full-text] — no full text

- Baseline: {}

## P01827 (decision order 91) — TPMS-Optimized Cement Geometries for Carbon-Efficient Structural Performance (2026)

- Link: https://doi.org/10.70671/dq9am588
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (Abstract (the only text read)): Not coded (no accessible full text). Abstract only: ML surrogates predict the performance of swept TPMS cement geometries (R² 0.987-0.999), and generated hybrid topologies reach 104% of the best classical TPMS compressive performance.
- Key phrase: 
- Claimed speed-up: None (Not coded; the abstract states no run time or cost for any method.)

- **R1 = na** [] — no full text
- **R2 = na** [] — no full text
- **R3 = na** [] — no full text
- **R4 = na** [] — no full text

- Baseline: {}

## P01152 (decision order 92) — Deep learning accelerated topology optimization of linear and nonlinear structures (2020)

- Link: https://arxiv.org/abs/2002.01896
- Access: full_text; inclusion: **exclude** (FT-DUPLICATE; prefill label: FT-DUPLICATE); stratum: **none**
- Primary outcome (Abstract (qualitative: no iterative scheme, negligible time); data generation and test results in the main text): Not coded (excluded as an earlier version of P00165). This version reports the same results as v4: CNN predictions reach mean Dice similarity 0.958 (linear), 0.964 (neo-Hookean) and 0.984 (stress-constrained) against the TO designs, and each optimization takes about 25 min on a PC.
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded as a duplicate). As in P00165, the ML inference time is not quantified, so no speed ratio is derivable; the only classical times are data-generation costs (0.31 and 3.2 min per data point with ten tasks in parallel; about 25 and 90 min per task on a Core i5 vPro PC).)

- **R1 = na** [excluded] — excluded at full text (FT-DUPLICATE of P00165)
- **R2 = na** [excluded] — excluded at full text (FT-DUPLICATE of P00165)
- **R3 = na** [excluded] — excluded at full text (FT-DUPLICATE of P00165)
- **R4 = na** [excluded] — excluded at full text (FT-DUPLICATE of P00165)

- Baseline: {}

## P00533 (decision order 95) — A complete Physics-Informed Neural Network-based framework for structural topology optimization (2023)

- Link: https://arxiv.org/abs/none found
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (Abstract (pool record, from OpenAlex)): Not coded (abstract only). The abstract states that CPINNTO, a deep-energy-method PINN for analysis plus a sensitivity PINN, reaches optimal topologies without labelled data or FEA, with compliance comparable to density-based TO designs (no numbers).
- Key phrase: 
- Claimed speed-up: None (no full text)

- **R1 = na** [] — no full text
- **R2 = na** [] — no full text
- **R3 = na** [] — no full text
- **R4 = na** [] — no full text

- Baseline: {}

## P00178 (decision order 96; provisional pilot 8) — A Novel Topology Optimization Approach using Conditional Deep Learning (2019)

- Link: https://arxiv.org/abs/1901.04859
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (Results and Discussions, Table 1 and the paragraph after it, p. 6 (abstract, conclusion and introduction hold only qualitative claims)): After training, the CWGAN produces a 120×120 cantilever design in about 0.34–0.35 s versus about 71–115 s for MATLAB SIMP (e.g. 0.350 s vs 83.914 s), roughly two orders of magnitude faster, claimed without loss of optimality.
- Key phrase: remarkable reductions in the computational time of an order of 10²
- Claimed speed-up: 239.75 (Derived from printed times for the example the text cites: 83.914 s (SIMP, target volume fraction 0.3) ÷ 0.350 s (CWGAN) = 239.75 (Table 1, p. 6). Other targets: 212.3× (0.4), 210.8× (0.5), 324.8× (0.6), 241.0× (0.7) [derived]. The text states about two orders of magnitude.)

- **R1 = fail** [R1-unmatched] — Results p. 6, Table 1: the speed claim (0.350 s vs 83.914 s at target volume fraction 0.3) compares CWGAN inference with completed SIMP runs, while the authors report that generated designs stay near volume fraction 0.4 whatever the target, so the cited 0.3 output misses its constraint. No compliance of any CWGAN design is computed and no matching is attempted. Whether the post-processing (0.5 threshold plus Gaussian filter, p. 5) is inside the 0.350 s is not stated.
- **R2 = partial** [R2-hardware-unjustified; R2-inefficient-impl [inferred]] — Dataset p. 5: SIMP runs in MATLAB, and the article cites the 99-line and 88-line educational codes (refs 27, 28) [inferred as the code base]. Hardware, linear solver and iteration counts are not stated for either method. The problem is 120×120 (below 10⁵ DOFs), so (c) does not apply; (b) and (d) are not established by the text.
- **R3 = fail** [R3-no-cost] — The speed claim (p. 6) reports neither training time nor data-generation cost. Only the dataset size is given (3024 SIMP samples, Dataset p. 5); at the Table 1 SIMP times this is about 60–96 h of generation [inferred: 3024 × 71.461–114.635 s]. No break-even and no per-query limitation.
- **R4 = fail** [R4-selected-examples] — Table 1 and Figs. 5–6: quality is judged visually on one generated design per target, chosen without a stated rule. No FE analysis of any generated design, no compliance and no measured volume fraction. The conclusion (p. 7) notes that GANs lack a proper evaluation metric.

- Baseline: {"classical_method": "SIMP compliance minimization, cantilever loaded at the mid-point of the free end (Problem Statement; Dataset, p. 5)", "implementation": "MATLAB SIMP code (Dataset, p. 5); the article cites the 99-line and 88-line educational codes (refs 27, 28); exact code not stated", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated (Keras with TensorFlow backend, Python 3.5, p. 4; Ohio Supercomputer Center acknowledged, p. 8)", "problem_size": "120×120 (Dataset, p. 5) [inferred ≈2.9×10⁴ DOFs]", "classical_iterations": "not stated", "classical_time": "83.914 s (target 0.3), 72.318 s (0.4), 71.461 s (0.5), 114.635 s (0.6), 83.613 s (0.7) (Table 1, p. 6)", "ml_time": "0.350 s, 0.34070 s, 0.339 s, 0.353 s, 0.347 s for the same targets (Table 1, p. 6); whether post-processing time is included is not stated", "training_time": "not stated", "data_gen

## P00373 (decision order 97; provisional top-up 56) — Neural Level Set Topology Optimization Using Unfitted Finite Elements (2023)

- Link: https://arxiv.org/abs/2303.13672
- Access: full_text; inclusion: **include** (I-QUALITY (screening code confirmed at full text)); stratum: **quality**
- Primary outcome (Sec. 7.1.2, Fig. 7 (p. 15): the first quantitative comparison with classical methods. The abstract, introduction and conclusion compare only qualitatively): Fig. 7: with the same mesh, volume fraction and unfitted evaluator, the NN-LS design had the lowest heat-conduction objective (pixel SIMP 15.7% and pixel LS 20.3% worse) but was 2.6% worse than pixel SIMP on the MBB beam.
- Key phrase: similar, in some cases better, performance compared to the well-known SIMP method
- Claimed speed-up: None (No runtime is reported for any method. Convergence is shown only as objective vs objective-function calls (Fig. 8, p. 16), and the conclusion (p. 17) states that the method converges more slowly than SIMP. Not derivable.)

- **R1 = partial** [R1-loose] — Sec. 3 (p. 7), Sec. 7.1, Figs. 7-8: same meshes, volume fraction 0.4 and a common unfitted evaluator. Budget is not matched: NN-LS reports the best of 100 random seeds, while seeding for the pixel baselines is not stated [inferred: single runs]; the optimizers differ (ADAM vs MMA); stopping rules and times are not stated. The heat-conduction gain may partly reflect the best-of-100 selection [judgment].
- **R2 = pass** [R2-none-established] — Quality stratum, competence of the comparator. Sec. 7.1: pixel SIMP (penalization 3) and pixel LS use MMA, the usual optimizer for these parameterizations, on the same meshes, and pixel SIMP gives the best MBB design (Fig. 7). The SIMP filter, continuation and stopping rule are not stated, but nothing in the text establishes a weak run. Markers (a)-(e) do not bear on a quality claim. Unsure, so pass.
- **R3 = na** [R3-na-per-problem] — Per-problem neural reparameterization with no dataset and no offline training (Sec. 2-3); no speed claim. For C3: no runtimes are reported; the method needs a similar or larger number of function calls than SIMP (Fig. 8), and 100 random seeds per problem (Sec. 3, p. 7).
- **R4 = partial** [R4-no-constraint-report] — Sec. 7.1.2 and Fig. 7: every design, including SIMP after 0.5 iso-surface conversion, is re-evaluated with the same unfitted FE solver. The LS volume is enforced exactly by the translation step (Sec. 4.4), but the volume of the converted SIMP designs is not reported, and the spread or failures over the 100 NN seeds are not reported; only the best design is shown (selection rule stated: lowest objective).

- Baseline: {"classical_method": "Pixel-LS: the same unfitted level-set method with the nodal LS values as design variables, optimized with MMA. Pixel-SIMP: nodal-density SIMP with penalization 3, optimized with MMA (Sec. 7.1, p. 13). SIMP designs are converted at the 0.5 iso-surface and re-evaluated with the unfitted solver (Sec. 7.1.2, p. 14)", "implementation": "Authors' Julia code (Gridap for FE, Flux for the U-Net) for all methods (Sec. 1, p. 4); public repository (Sec. 9, p. 18)", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "Heat conduction: 95 × 95 mesh, volume fraction 0.4; MBB half-beam: 287 × 95 mesh, volume fraction 0.4 (Sec. 7.1.1, pp. 13-14) [derived: about 9.2×10³ and 5.5×10⁴ DOFs]", "classical_iterations": "not stated; the convergence plots run to about 1,000 objective-function calls for all methods (Fig. 8, p. 16)", "classi

## P00698 (decision order 98) — Novel Artificial Neural Network Aided Structural Topology Optimization (2024)

- **FLAG — stratum check: Speed stratum rests on shares of run time spent in FE; the abstract's 40 % matches no FE share in Fig. 14.**
- Link: https://doi.org/10.3390/app142311416
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text; cost proxy = share of run time spent in FE analysis, SIMP vs the network-aided method, stated in the abstract)); stratum: **speed**
- Primary outcome (Abstract (§5.1 rule 1: quantitative comparison with SIMP); data in Sec. 5.4, Figs. 13-14, pp. 18-19): FE analysis takes over 90% of SIMP run time, but a smaller share in the partitioned-network method: 40% per the abstract, 17-65% across 60×60 to 480×480 meshes in Fig. 14. No absolute run times are reported.
- Key phrase: takes more than 90% of the total operation time of the SIMP method
- Claimed speed-up: None (Not derivable: only shares of run time are given, never absolute times for either method (Sec. 5.4, Figs. 13-14). SIMP FE share 90%, 96%, 99%, 99% at 60×60, 120×120, 240×240, 480×480 (Fig. 13); network method FE 17%, 27%, 61%, 65%, network inference 43%, 38%, 20%, 8%, other 40%, 35%, 19%, 27% (Fig. 14). The abstract's 40% matches no FE share in Fig. 14 (their mean is 42.5% [derived]); 40% is the share of the other modules at 60×60.)

- **R1 = partial** [R1-loose] — Sec. 4-5: the cost claim rests on shares of run time (Figs. 13-14) with no absolute times, and the timed runs are not linked to a stated design case [the 3×3-partition L-beams of Table 1 inferred]. Quality is reported separately as unlabelled objective values within about ±9% of SIMP (Tables 1-3 [derived]); volume fractions are not reported, and SIMP stops after a fixed 20 iterations. Matching is therefore loose. A stricter reading (no measured speed at all) gives fail.
- **R2 = pass** [R2-none-established] — Sec. 2.1, 4 and 5.4: the SIMP implementation, solver type and hardware are not stated, and no absolute time exists, so (a), (b), (c) and (e) cannot be derived. (d) is not established: SIMP uses 20 iterations while most examples converge within 10 to 20 steps (Sec. 5.1), and both methods share the budget. An FE share of 90-99% is typical of SIMP codes whose cost is dominated by the linear solve, so no inefficiency is evident [inferred]. Unsure, so pass.
- **R3 = partial** [R3-no-amortization] — The network is trained offline on random SIMP runs and reused across examples (Sec. 3.2; Conclusion) [reuse inferred]. Training time, dataset size and break-even are not reported; the only cost figure is about 30 min for a process of generating randomly partitioned TO iterations (Sec. 3.3), which may be the data-generation cost [inferred]. The efficiency claim covers the whole design process (abstract), not per-query inference. If the 30 min is not read as a data cost, R3 = fail (R3-no-cost).
- **R4 = partial** [R4-no-failure-rate] — Tables 1-6: an objective value is given for every network and SIMP design, presumably from FE analysis of the returned design [inferred; the quantity and its computation are not stated]. Volume fractions and constraint satisfaction of the network designs are not reported, and disconnections or failed runs are not counted; the 25 Appendix A cases show images only.

- Baseline: {"classical_method": "SIMP compliance minimization (penalty 3) with the optimality-criteria update and a density filter (Sec. 2.1); the network method replaces the fine-scale FE sensitivity computation with a partitioned CNN plus fully connected network fed by coarse-scale FE displacements and densities (Sec. 2-3)", "implementation": "not stated (own SIMP code [inferred])", "solver": "a sparse matrix equation solver, type not stated (Sec. 5.4)", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "Timing study: 60×60, 120×120, 240×240 and 480×480 meshes, 3×3 partitions (Figs. 13-14) [derived: 7,442 to 462,722 nodal DOFs]; examples 60×60 to 240×960 (Sec. 4, Tables 1-6)", "classical_iterations": "20 optimization iterations for every example (Sec. 4.1-4.5); Figs. 11-12 plot 50 iterations; Sec. 5.1 says most examples converge within 10 to 20 steps", "classical_ti

## P01016 (decision order 99) — Designing Porous Structure with Optimized Topology using Machine Learning (2024)

- Link: https://doi.org/10.1016/j.procir.2024.08.033
- Access: abstract_only; inclusion: **include** (I-UNCLEAR (no accessible full text)); stratum: **none**
- Primary outcome (abstract only): Not coded (no full text). The abstract says machine-learning models performing topology optimization for porous biomedical structures give a large cut in computation time, with performance comparable to conventional methods; no numbers are given.
- Key phrase: 
- Claimed speed-up: None (not coded (no full text); the abstract gives no time or speed-up figure)

- **R1 = na** [no-full-text] — no full text
- **R2 = na** [no-full-text] — no full text
- **R3 = na** [no-full-text] — no full text
- **R4 = na** [no-full-text] — no full text

- Baseline: {}

## P00034 (decision order 100; provisional top-up 3) — Transformer-based Topology Optimization (2025)

- **FLAG — duplicate: Earlier version of P00235 (arXiv 2604.03522). P00235 is the primary record.**
- Link: https://arxiv.org/abs/2509.05800
- Access: full_text; inclusion: **exclude** (FT-DUPLICATE; prefill label: FT-DUPLICATE (earlier version of P00235 = arXiv 2604.03522; version of record doi 10.1007/s00158-026-04342-6)); stratum: **none**
- Primary outcome (Section 5, last paragraph (abstract, introduction and conclusion hold only qualitative classical comparisons)): Not coded (excluded as an earlier version of P00235). Would-be primary outcome in this version: static 64×64 designs in about 2 s vs 66 s average for the original topology-optimization runs (33×) at a 1.88% mean compliance error.
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded as a duplicate). Would-be values, both stated in Section 5: static 66 s ÷ about 2 s = 33; dynamic 8900 s ÷ 2 s = 4,450.)

- **R1 = na** [] — excluded at full text
- **R2 = na** [] — excluded at full text
- **R3 = na** [] — excluded at full text
- **R4 = na** [] — excluded at full text

- Baseline: {}

## P00051 (decision order 102; provisional top-up 97) — Diverse Topology Optimization using Modulated Neural Fields (2025)

- **FLAG — note: Re-test candidate: MIT-licensed code and configs (GINNs repository). The alternative primary outcome (9.1x and 4.2x vs a deflated barrier method) has 12-19 % worse compliance.**
- Link: https://arxiv.org/abs/2502.13174
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-UNCLEAR; the emphasized classical comparison is near-optimal compliance; speed vs the deflated barrier method is an alternative)); stratum: **quality**
- Primary outcome (Sec. 4.4 and Table 1, p. 9: first quantitative classical comparison. Abstract, introduction and conclusion are qualitative. Chosen by §5.1 rule 4: near-optimality is claimed in the abstract and introduction, and the conclusion stresses adherence to mechanical requirements, while the speed claim appears only in the introduction and one results heading): TOM's sampled designs come close to, but average above, classical compliance: 0.75±0.03 vs 0.68 (SIMP) and 0.67 (deflated barrier) on MBB, 0.69±0.13 vs 0.59/0.58 on the cantilever, and 1.31 vs 0.99 (×10⁻³, SIMP) on the 3D bracket.
- Key phrase: generates more diverse solutions than any previous method, all while maintaining near-optimality
- Claimed speed-up: None (Quality-stratum primary. Speed alternative (Table 1): the deflated barrier method (DB) takes 55.5 min vs TOM 6.1 min on MBB (9.1× [derived]) and 123 vs 29 min on the cantilever (4.2× [derived]). Against SIMP (FeniTop), TOM is slower in 2D (2 vs 6.1 min; 4 vs 29 min) and faster on the bracket (187 vs 47 min) with a 64× coarser FEM mesh [derived from Table 2].)

- **R1 = partial** [R1-loose] — Sec. 4.3 and Tables 1-2: all designs are scored on the same high-resolution mesh. Budgets and outputs differ: TOM uses 9,000-25,000 solver calls vs 400 (FeniTop) and 3,190-4,922 (DB), and samples a continuous family vs one or two designs. On MBB, TOM's mean volume exceeds the 53.5% target (55.08%) while its compliance is still higher. The FeniTop stopping rule is a fixed 400 iterations; DB's is not stated.
- **R2 = pass** [R2-none-established] — The classical baselines are established open implementations (FeniTop; DB's public code) on the same node [inferred]. (b) not observed: no numbers in the abstract. (c) does not apply: FEM runs on CPUs for all methods. (d) not established: FeniTop's 400 iterations are not compared with a convergence need. Sec. 4.4 attributes part of DB's run time to its public implementation's mesh refinement, which bears on the speed alternative, not on compliance. Unsure, so pass.
- **R3 = na** [R3-na-per-problem] — TOM is data-free and trains one network per problem with the solver in the loop (Sec. 3.1), so its cost sits inside R1/R2; the reported TOM times include that training (Table 1).
- **R4 = partial** [R4-floaters-not-counted] — Sec. 4.3 and Table 1: compliance and volume of the returned designs come from a FEniCSx analysis on a common mesh. Load-violating designs are counted and filtered (TOM 8% on the cantilever). Floaters (disconnected pieces) are acknowledged only qualitatively (Sec. 4.4; post-processing shown in App. D.3 but not used for Table 1 [inferred]). The number of TOM samples behind the statistics is not stated.

- Baseline: {"classical_method": "SIMP via FeniTop (Python wrapper of FEniCSx/DOLFINx; one design per problem) and the deflated barrier method (DB, Papadopoulos et al. 2021; public implementation with adaptive mesh refinement; two designs) (Sec. 4.2, App. A.4). DB omitted for the 3D bracket", "implementation": "FeniTop (Jia et al. 2024) for SIMP; DB public code; TOM code is in the GINNs repository, which includes its own FeniTop copy", "solver": "not stated (FEniCSx/DOLFINx FEM). TOM runs its FEM calls in parallel on CPU cores, one process per shape (Sec. 3.1)", "hardware_classical": "not stated per method; all experiments ran on one node: NVIDIA Titan V GPU (printed 'Titan V12'), Xeon Gold 6150 (36 cores, 2.70 GHz), 384 GB RAM (App. A.3) [same node inferred for the baselines]", "hardware_ml": "Same node; network and diversity loss on the GPU (under 2 GB memory), FEM on CPU cores (Sec. 3.1, App. A.3

## P00181 (decision order 104; provisional top-up 88) — 3D Topology Optimization using Convolutional Neural Networks (2018)

- Link: https://arxiv.org/abs/1808.07440
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (Abstract (quantitative comparison with the conventional solver alone); restated in Sec. 5.4 (p. 13, 40-45%) and the Conclusion (pp. 13-14, 40%)): Stopping 3D SIMP (TopOpt) at iteration 20 and letting a 3D CNN predict the final design cut computation time by about 40% versus solving to convergence, with 96.2% binary and 79.7% RMS voxel accuracy on 1,000 test problems.
- Key phrase: about 40% reduction in overall computation time
- Claimed speed-up: 1.67 (Derived from the stated 40% time reduction (abstract; conclusion): 1 ÷ (1 − 0.40) = 1.67; Sec. 5.4 states 40-45%, i.e. 1.67-1.82 [derived]. No absolute times are printed anywhere, so the ratio cannot be checked. Stopping at iteration 20 of the 70-100 iterations each run needs (Sec. 4.1) would suggest 71-80% fewer solver iterations [derived]; the article does not say how the time reduction was measured.)

- **R1 = partial** [R1-loose] — Abstract, Sec. 5, Conclusion: the roughly 40% time saving is measured against running TopOpt to convergence, while the CNN outputs are compared with the converged designs only by voxel accuracy (96.2% binary, 79.7% RMS). No compliance or volume of any predicted design is computed, and SIMP is not stopped at matched accuracy; per Fig. 6, raw SIMP iterates already exceed 90% binary accuracy early, so the CNN's gain over early stopping is untested. A stricter reading (speed claim with no design-quality comparison) gives fail.
- **R2 = pass** [R2-none-established] — Sec. 4-4.1: the baseline is the public PETSc TopOpt code (ref. [31]), run to convergence (70-100 iterations); its default solver is multigrid-preconditioned FGMRES, the protocol's efficient class [observed in the public code; settings used here not stated]. Hardware is not stated. The problem has about 1.3×10⁴ DOFs [derived], so (c) does not apply; (b) not observed (the abstract and results use the same comparator); (d) not established (convergence-based stopping); (e) not derivable (no times). Unsure, so pass.
- **R3 = fail** [R3-no-cost] — Sec. 1 notes qualitatively that the approach trades a large offline data corpus for run-time speed, but neither the cost of the 6,000 TopOpt runs (Sec. 4.1) nor the training time (App. A: 30 epochs) is reported, and no break-even is given. For C3: with about 6,000 full solves of data and a saving of about 40% of one solve per use, break-even is about 15,000 uses before training [derived: 6,000 ÷ 0.4].
- **R4 = fail** [R4-image-metric] — Sec. 5 and Tables 3-7: quality rests only on voxel binary and RMS accuracy against the solver output. No FE analysis of any predicted design, no volume check and no count of disconnected designs are reported; the conclusion lists avoiding islands and controlling volume fraction as future work (Sec. 6). Table 7 and App. C show selected examples.

- Baseline: {"classical_method": "3D SIMP compliance minimization with a density filter, run to convergence with the open-source PETSc code 'TopOpt' of Aage et al. (ref. [31]); four MBB-type support cases, 1-10 sampled loads, volume fraction sampled around 0.28 (Sec. 3-4.1)", "implementation": "TopOpt, the parallel PETSc framework of Aage, Andreassen and Lazarov 2014 (ref. [31]) (Sec. 4, 4.1)", "solver": "not stated in the article; the public TopOpt_in_PETSc code defaults to FGMRES with a geometric multigrid preconditioner (4 levels) [observed in the repository's LinearElasticity.cc, 2026-09-24; the article's own settings are not stated]", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "24 × 12 × 12 = 3,456 elements on a 2 m × 1 m × 1 m beam (Sec. 4.1, p. 5) [derived: about 1.3×10⁴ DOFs]", "classical_iterations": "Run to convergence; each sample needed about 70-100 

## P00358 (decision order 113; provisional pilot 17) — Latent Diffusion Models for Structural Component Design (2024)

- Link: https://arxiv.org/abs/2309.11601
- Access: full_text; inclusion: **include** (I-QUALITY); stratum: **quality**
- Primary outcome (Sec. 6.2 Strain Energy Analysis, Fig. 8 (first quantitative performance comparison with SIMP); the Abstract and Conclusions give only the qualitative near-optimality claim): For 100 test conditions (2,000 generated 3D designs), the distribution of surrogate-predicted strain energy shows no marked aggregate difference from the 100 matching SIMP designs. On this basis the paper presents the generated designs as near-optimal.
- Key phrase: there is no substantial difference in performance
- Claimed speed-up: None (No speed claim. No SIMP time and no LDM inference time are reported; Sec. 6.4 gives training times only.)

- **R1 = na** [R1-na-no-speed-claim] — No speed or cost comparison with SIMP appears anywhere; there are no SIMP times and no LDM inference times (Sec. 5, 6.4). Note for the verifier: the quality comparison is not volume-matched (volume-fraction MAE 0.0989, Sec. 6.2).
- **R2 = na** [R2-na-no-speed-claim] — The primary outcome is quality only. SIMP (ANSYS Mechanical APDL v19.2, Sec. 5) supplies the reference designs, and its run time is never compared.
- **R3 = na** [R3-na-no-speed-claim] — There is no speed claim. For reference, training times are reported per epoch or per sample (Sec. 6.4); SIMP data-generation time is not stated; voxelization takes about 15 minutes per geometry (Sec. 5).
- **R4 = fail** [R4-surrogate] — Sec. 6.2, Fig. 8: strain energy of the generated designs is predicted by a surrogate CNN whose accuracy is not reported. No FE analysis of any generated design is reported. Generated volume fractions deviate from the SIMP designs (MAE 0.0989). Floating or disconnected designs are not counted; floating artifacts are mentioned only for a rejected encoder variant (Sec. 4.1).

- Baseline: {"classical_method": "SIMP topology optimization in ANSYS Mechanical APDL v19.2 (Sec. 5)", "implementation": "Commercial: ANSYS Mechanical APDL v19.2 (Sec. 5)", "solver": "not stated", "hardware_classical": "not stated (Sec. 5 mentions a cluster only for voxelization)", "hardware_ml": "not stated", "problem_size": "SIMP mesh of a 1 m cube with 31093 nodes and 154,677 elements (Sec. 5). Designs voxelized to 32^3, 64^3 and 128^3 (Sec. 5). All quality analyses are at 32^3 (Sec. 6.4).", "classical_iterations": "Not stated for the dataset. The subset saved for surrogate training averages 13 iterations per initial strain energy (Sec. 6.2).", "classical_time": "not stated", "ml_time": "Generation/inference time not stated", "training_time": "VAE: about 2 min 20 s per epoch (32^3) and about 24 min per epoch (64^3). 128^3 with multi-grid training: under 2 hours, versus over 10 hours from scratch.

## P00081 (decision order 124; provisional top-up 22) — PyTOaCNN: Topology optimization using an adaptive convolutional neural network in Python (2024)

- Link: https://arxiv.org/abs/2404.12244
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-SPEED; no classical runtime appears anywhere, and the first quantitative classical comparison is volume and objective error against the MATLAB TO codes, §5.1 rule 2)); stratum: **quality**
- Primary outcome (Section 7.1.1 and Table 1 (first quantitative classical comparison, in the main text; the Abstract, Section 8 and Introduction compare only qualitatively)): For the mid-load beam on a 100×100 grid, CNN designs at seven prescribed volume fractions differ from top88 SIMP designs by 0.053–5.4% in volume and 0.041–2.66% in compliance (Table 1); the authors call such errors negligible.
- Key phrase: negligible performance and volume fraction errors
- Claimed speed-up: None (No classical runtime is reported anywhere. The trained CNN is said to return a design instantly (Abstract) or in under a second (Sec. 7.1.1-7.1.3), with no number, hardware or MATLAB time. Not derivable.)

- **R1 = partial** [R1-loose] — Sec. 7 and Table 1: CNN and MATLAB designs share the problem, the grid and the prescribed volume fraction, and the CNN output is scored in the same MATLAB code. Matching is loose: the CNN's own volume misses the target by up to 5.4% (Table 1; up to 14.4% in Table 4), and the objective error is not corrected for that volume difference. The stopping rule of top88 and topX is not stated in the article (TOPress: maxit 100), and no compute budget is compared.
- **R2 = pass** [R2-none-established] — Sec. 4-5: the classical designs come from standard public MATLAB codes (top88, TOPress, topX) with standard settings, and they are also the CNN's training targets. Nothing in the text points to an under-converged or weak comparator. No runtime is reported, so markers (a)-(e) cannot apply; the problems have about 2×10^4 DOFs [derived], below the (c) threshold. Unsure, so pass.
- **R3 = na** [R3-na-no-speed-claim] — Quality stratum: no quantified speed claim against a classical method. For C3: data = 95 MATLAB TO runs per problem (68 for topX) and training = 2000 epochs; neither time nor hardware is reported (Sec. 5, 6.5).
- **R4 = partial** [R4-no-failure-rate] — Sec. 7: the returned grayscale CNN field is evaluated in the same MATLAB code, so the objective is FE-computed, and the volume error is reported for every case (Tables 1-7). No failed or disconnected outputs are counted. The authors say they picked the 5-7 volume fractions per table arbitrarily (Sec. 7.1.2); in Tables 1, 2, 5, 6 and 7 all of them lie inside the training sets [Tables 5-7 derived from the training ranges in Sec. 5, 7.1.3, 7.1.4 and 7.2]. A verifier who reads the arbitrary pick as selection without a stated rule may choose fail (R4-selected-examples).

- Baseline: {"classical_method": "SIMP compliance minimization (modified SIMP, p = 3) with the top88 MATLAB code for the constant-load beams; TOPress MATLAB code for the design-dependent pressure-loaded arch; topX MATLAB code for bulk-modulus microstructure design (Sec. 4-5). The update scheme is not described in the article", "implementation": "Public educational MATLAB codes, called open-source in the article: top88 (Andreassen et al. 2011) and topX (Xia and Breitkopf 2015) with penal 3, rmin 2.4, ft 1; TOPress (Kumar 2023) with penal 3, rmin 2.4, etaf 0.2, betaf 8, lst 1, maxit 100 (Sec. 5)", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated (TensorFlow/Keras in a Jupyter Notebook, Sec. 6)", "problem_size": "100×100 bilinear quadrilateral elements for every problem (Sec. 4-5) [derived: about 2.0×10^4 nodal DOFs]", "classical_iterations": "not stated for top88 

## P00309 (decision order 127; provisional pilot 15) — Evolutionary de-homogenization using a generative model for optimizing solid-porous infill structures considering the stress concentration issue (2024)

- Link: https://arxiv.org/abs/2412.19154
- Access: full_text; inclusion: **include** (I-QUALITY); stratum: **quality**
- Primary outcome (Section 4.2.3, Figs. 20-21 (no quantitative classical comparison in abstract, conclusion or introduction)): On the symmetric tension beam, the VAE-driven evolutionary stage (MFTD) cut maximum von Mises stress by 13%, 15.6% and 18.2% versus classical low-fidelity stress-TO designs at similar mass ratios; hypervolume rose 35.5% over 200 iterations.
- Key phrase: achieving a 13% reduction in maximum stress with a smaller volume fraction
- Claimed speed-up: None (No runtimes or computational costs are reported for any method; not derivable.)

- **R1 = partial** [R1-loose] — Sec. 4.2.3, Fig. 21: stress comparisons at approximately matched mass ratio (10.27 vs 10.33%, 12.41 vs 12.3%, 17.1 vs 16.7%); by the printed values MFTD uses more material in two of the three pairs, although the text reports weight reductions [inferred]. No computational budget is reported: MFTD ran 200 iterations with high-fidelity FEA of candidates, and the stopping rule of the classical low-fidelity runs is not stated.
- **R2 = na** [R2-na-quality-only] — Primary outcome compares design quality only; no runtimes are reported for any method, so the efficiency criteria (a)-(e) do not apply.
- **R3 = na** [R3-na-per-problem-learning] — No speed or cost claim. The VAE is retrained at every iteration inside one design run, with no offline training (Sec. 3.2.4), so its cost sits inside R1/R2.
- **R4 = partial** [R4-no-failure-rate] — Quality = maximum von Mises stress from COMSOL adaptive-mesh FEA of the de-homogenized geometry, with a mesh-independence study (Sec. 2.2.3, 4.1.2); mass ratio reported for each design. Anomalous candidates are discarded without a reported count (Sec. 3.2.2), and the three per-design pairs use chosen mass ratios without a stated selection rule; the hypervolume comparison covers all Rank-1 designs.

- Baseline: {"classical_method": "Low-fidelity optimization: gradient-based two-field multi-material maximum-stress (P-norm) TO updated with MMA, mapped to a full-scale geometry by de-homogenization (Sec. 2.1.4, 2.2). Also traditional single-material stress-based TO (Stress-TO) (Sec. 4.2.2)", "implementation": "MATLAB 2022b for the low-fidelity optimization and most of MFTD; COMSOL Multiphysics 6.2 for CAD realization and FEA; VAE in TensorFlow (version printed as 3.6) (Sec. 4)", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "L-bracket: 60×60 elements of 1 mm × 1 mm, m = 100 designs (Sec. 4.1.1, Table 1). Tension beam: 52×80 elements, m = 160 (Sec. 4.2.1, Table 5; Table 5 lists 3200 elements per low-fidelity datum). High-fidelity adaptive meshes of 18,669-154,325 elements in the mesh study (Table 4)", "classical_iterations": "not stated for 

## P00176 (decision order 138; provisional top-up 7) — A deep Convolutional Neural Network for topology optimization with strong generalization ability (2019)

- Link: https://arxiv.org/abs/1901.07761
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (Sec. 5, p. 7, and Table 1 (first quantitative classical comparison; the abstract, conclusion and introduction make only qualitative claims)): On 8000 held-out 40×80 cantilever problems, the U-Net predicts a layout in 0.001 s on average versus 3.913 s for SIMP (88-line code), with mean compliance error 4.16% after excluding the 4.12% of outputs that are disconnected.
- Key phrase: a significant reduction in computation cost was achieved with little sacrifice on the performance
- Claimed speed-up: 3913 (Derived: 3.913 s (SIMP) ÷ 0.001 s (CNN), average times over the test set (Sec. 5, p. 7) = 3913; Table 1 states 99.97% calculation time saved. The authors exclude dataset generation and training. Whether the FE solve that builds each input tensor (Sec. 4.1) is inside the 0.001 s is not stated.)

- **R1 = fail** [R1-unmatched] — Sec. 5 p. 7 and Table 1: mean CNN inference time (0.001 s) is compared with mean SIMP time (3.913 s) on the same test problems, while the CNN designs are measurably worse than the SIMP designs they imitate: mean compliance error 4.16%, and 4.12% of outputs are disconnected with huge compliance errors and are excluded from all averages. No matching is attempted (e.g., SIMP stopped at equal compliance); the SIMP stopping rule is not stated.
- **R2 = pass** [R2-none-established] — Sec. 4.1 and 5: SIMP is the 88-line MATLAB code, run on a PC with an i7-8700K CPU and a GTX 1080 Ti GPU; the device for each method is not stated. The problem has about 6.6×10³ DOFs [derived], below 10⁵, so (c) does not apply. The abstract gives no baseline figure (b). No iteration count or stopping rule is given, so (d) and (e) cannot be derived. The 88-line code is a vectorized educational code [recalled, not verified in-session]; no inefficiency is evident. Unsure, so pass.
- **R3 = fail** [R3-no-cost] — Sec. 5 p. 7: the authors state that the considerable dataset-generation and training times are not included and argue that they become negligible over many uses; neither is quantified and no break-even is given. Dataset: 80,000 SIMP samples (Sec. 4.1) [inferred ≈87 h at the 3.913 s mean], plus one FE solve per sample for the input tensor; training time not stated.
- **R4 = pass** [R4-FE-verified] — Table 1 and Sec. 5: compliance, pixel and volume-fraction errors are computed for all 8000 test designs against SIMP (compliance by FE analysis [inferred]; error definitions not given). Volume-fraction error (0.13%) is reported, and disconnected outputs are counted (4.12%; 13.64% and 11.50% for the OOD sets, Table 2), although they are excluded from the averages. Figures show examples, but the numbers cover the full test sets.

- Baseline: {"classical_method": "SIMP compliance minimization with the 88-line MATLAB code (Andreassen et al. 2011); cantilever, penalty 3, filter radius 1.5, volume fraction 0.2-0.8, 1-10 point loads in X+, X-, Y+ or Y- (Sec. 4.1)", "implementation": "MATLAB 88-line educational code (Sec. 4.1); the timed conventional method in Sec. 5 is taken to be the same code [inferred]", "solver": "not stated (the published 88-line code uses a sparse direct solve [recalled, not verified in-session])", "hardware_classical": "one PC with an Intel Core i7-8700K CPU and an NVIDIA GTX 1080 Ti GPU for all calculations (Sec. 5, p. 7); the device used by SIMP is not stated [CPU inferred]", "hardware_ml": "same PC (i7-8700K + GTX 1080 Ti), Keras (p. 5 and Sec. 5); the device per method is not stated", "problem_size": "40×80 elements; input tensor 41×81×6 (Sec. 4.1) [derived: 6,642 nodal DOFs]", "classical_iterations": 

## P00238 (decision order 159; provisional pilot 12) — AutoMS: Multi-Agent Evolutionary Search for Cross-Physics Inverse Microstructure Design (2026)

- Link: https://arxiv.org/abs/2603.27195
- Access: full_text; inclusion: **exclude** (FT-MLONLY; prefill label: FT-MLONLY); stratum: **none**
- Primary outcome (Abstract; Section 1 contributions; Section 5.1, Table 1): Not coded (excluded). Headline: 83.8% success rate on 17 cross-physics tasks versus NSGA-II 43.7%, CMA-ES 66.7% and BayesOpt 65.0%, all baselines searching the inputs of the same learned MIND generator.
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded at full text).)

- **R1 = na** [] — excluded at full text
- **R2 = na** [] — excluded at full text
- **R3 = na** [] — excluded at full text
- **R4 = na** [] — excluded at full text

- Baseline: {}

## P00519 (decision order 182; provisional pilot 20) — Toward Signed Distance Function based Metamaterial Design: Neural Operator Transformer for Forward Prediction and Diffusion Model for Inverse Design (2025)

- **FLAG — FT-NOBASELINE candidate: Listed in the clarification. Efficiency claim against gradient-based TO; no classical optimizer is run or timed.**
- Link: https://arxiv.org/abs/2504.01195
- Access: full_text; inclusion: **include** (I-SPEED); stratum: **speed**
- Primary outcome (Abstract (qualitative; the classical comparator is named earlier in the Abstract as gradient-based optimization). The contrast with TO is explicit in Sec. 1 Introduction and Sec. 4 Conclusions. No quantitative comparison with a classical method exists anywhere, so protocol Sec. 5.1 rule 3 applies.): The paper presents its SDF-conditioned diffusion model as an efficient one-shot route to inverse design. It contrasts this with iterative gradient-based TO, which it calls computationally intensive and prone to local minima. No classical optimizer is run or timed.
- Key phrase: enabling efficient one-shot design synthesis
- Claimed speed-up: None (No classical optimizer time is reported. Table S7 (Supplementary S5) gives a forward FE simulation time of 2.3 min/sample on 1 CPU and an inverse-design time of 0.46 s/solution. The FE figure is a forward analysis, not a classical optimization, so no speed-up versus a classical method can be derived.)

- **R1 = fail** [R1-no-quality] — Abstract, Sec. 1 and Sec. 4: the paper asserts efficiency relative to iterative gradient-based TO, but runs no classical optimizer and makes no design-quality comparison with any TO or other classical result. Table S7 lists only ML times and forward-FE times.
- **R2 = na** [R2-na-no-baseline-run] — No classical optimization baseline is implemented or timed anywhere in the main text or Supplementary S0-S5, so there is no baseline whose efficiency can be judged. Markers (b)-(d) cannot apply.
- **R3 = partial** [R3-no-amortization] — Supplementary S5, Table S7 reports the data-generation cost (2.3 min/sample on 1 CPU, about 10,000 simulations per Sec. 2.1) and the training cost (16, 96 and 47 s/epoch for 500, 300 and 300 epochs per Tables S4, S6). No break-even count is given, and the efficiency claim is not explicitly limited to per-query inference.
- **R4 = partial** [R4-no-failure-rate] — Sec. 2.3, Figs. 6 and 9: for each target, the model generates 200 or 500 SDFs; the 4 with the lowest surrogate (NOT) L2 error are shown and checked with Abaqus FE (Figs. 6(b), 9(b)). Samples with islands are filtered out (Sec. 3.5). The number filtered and the share of generated designs that meet the target are not reported.

- Baseline: {"classical_method": "None run. Gradient-based topology optimization and genetic algorithms are named only as traditional alternatives (Sec. 1, Sec. 4).", "implementation": "not applicable (no classical optimizer implemented)", "solver": "not applicable. The data-generation FE uses the Abaqus 2024 implicit dynamic solver (Sec. 3.2).", "hardware_classical": "not applicable. FE data generation ran on CPUs of the NCSA Delta machine (Sec. 3.2; Supplementary S5).", "hardware_ml": "Training: one NVIDIA H100 GPU with 90GB memory (DeltaAI, NCSA; Sec. 3.4). Inference: one NVIDIA A100 GPU (Delta, NCSA; Sec. 3.5).", "problem_size": "2D unit cell on a [0, 1 mm]^2 domain. Geometry from a 64x64 Gaussian random field; SDF on a 120x120 grid (Sec. 2.1, 3.1). FE global mesh size 0.04 mm, 51 load steps to 0.2 compressive strain (Sec. 3.2).", "classical_iterations": "not applicable. The diffusion model uses

## P00313 (decision order 184; provisional top-up 10) — Populating cellular metamaterials on the extrema of attainable elasticity through neuroevolution (2025)

- **FLAG — FT-NOBASELINE candidate: No TO run, runtime or FE-count comparison. Only a qualitative remark that the Pareto fronts agree with a TO reference (Sec. 3.3). Decide whether that counts as citing a classical result.**
- Link: https://arxiv.org/abs/2412.11112
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text; qualitative primary outcome, no classical method run)); stratum: **speed**
- Primary outcome (Abstract (§5.1 rule 3: no quantitative classical comparison anywhere); related qualitative statements in Sec. 3.3 and 3.5): Qualitative: gradient-based TO is said to be inefficient for surveying the metamaterial design space and unable to reveal attainable property bounds, whereas CPPN neuroevolution efficiently finds Pareto-front designs; no TO is run and no cost is compared.
- Key phrase: they are not efficient tools for surveying the vast design space of metamaterials
- Claimed speed-up: None (Not derivable: no runtime, no FE-evaluation count comparison and no classical run are reported. The method evolves a population of 500 for 800 generations per study on 256 CPU processors (Sec. 3); its runtime is not stated.)

- **R1 = fail** [R1-no-quality-comparison] — Abstract, Sec. 3.3 and 3.5: the efficiency claim against gradient-based TO is backed by no TO run, runtime, FE-evaluation count or matched-quality comparison. The only link to TO results is the qualitative statement that the orthotropic Pareto fronts are consistent with Ref. [5] and denser than TO-driven results (Sec. 3.3); Fig. 11 shows no Ref. [5] data [checked PDF p. 31].
- **R2 = pass** [R2-none-established] — No classical optimization is run (Sec. 3), so the comparator's implementation, solver and hardware cannot be assessed; the claim about TO rests on the literature (Introduction; Ref. [5] in Sec. 3.3). Unsure, so pass.
- **R3 = na** [R3-na-per-problem] — CPPNs are evolved per study from random initial networks without prior data or offline training (Sec. 1 aim; Sec. 2; Conclusion), so there is no training or data cost to amortize; the evolutionary cost (population 500, 800 generations, Sec. 3; runtime not reported) belongs under R1/R2.
- **R4 = partial** [R4-no-failure-rate] — Sec. 2 (Fig. 1b, Alg. 1) and App. A: every candidate's properties come from FE homogenization of the meshed design. Designs with interior or exterior discontinuity stay in the population and are ranked by a constraint-violation measure (Sec. 2.2.3, Fig. 6), but the share of infeasible designs in the final Pareto sets and in the 486,852-design database (Sec. 2.1.1) is not reported. No mesh-convergence check is reported for the 35×35 point-cloud meshes. Representative designs are chosen as distinct extreme combinations (Sec. 3.2).

- Baseline: {"classical_method": "Gradient-based TO for metamaterial design (density-based, level-set and phase-field methods named in the Introduction); not run. Sec. 3.3 compares qualitatively with results reported in Ref. [5]", "implementation": "not applicable (no classical run). ML side: custom NEAT-style CPPN neuroevolution with RVEA reference-vector selection and constraint-violation ranking; FE homogenization on Delaunay triangle meshes (Sec. 2, App. A); software not stated", "solver": "not stated", "hardware_classical": "not applicable (no classical run)", "hardware_ml": "Alibaba Cloud machines with AMD EPYC 7H12 64-core processors, 256 processors in total, 2.60 GHz, 503 GiB RAM; no GPU (Sec. 3)", "problem_size": "2D periodic unit cells: a 35×35 point cloud on the symmetry patch, mapped by symmetry and meshed with Delaunay triangles (Sec. 2.1.3, 3); FE element count not stated", "classical_

## P00254 (decision order 207; provisional pilot 14) — Rank Reduction AutoEncoders for Mechanical Design: Advancing Novel and Efficient Data-Driven Topology Optimization (2026)

- Link: https://arxiv.org/abs/2601.23269
- Access: full_text; inclusion: **exclude** (FT-NOBASELINE; prefill label: FT-NOCOMPARISON); stratum: **none**
- Primary outcome (Abstract; Sections 5.1-5.3; Section 6): Not coded (excluded). Headline: RRAE-plus-MLP surrogates give accurate, efficient forward stress prediction and inverse geometry recovery on a SIMP half-MBB dataset; accuracy is measured only against SIMP/FE ground truth, with no runtime comparison.
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded at full text); no runtimes are reported anywhere in the article.)

- **R1 = na** [] — excluded at full text
- **R2 = na** [] — excluded at full text
- **R3 = na** [] — excluded at full text
- **R4 = na** [] — excluded at full text

- Baseline: {}

## P00374 (decision order 217; provisional pilot 18) — NSTO: Neural Synthesizing Topology Optimization for Modulated Structure Generation (2022)

- Link: https://arxiv.org/abs/2303.11757
- Access: full_text; inclusion: **include** (I-SPEED); stratum: **speed**
- Primary outcome (Introduction, first contribution bullet (headline claim); quantitative support in Sec. 4.2, the Daruma timing table (third table, unnumbered in the arXiv HTML). If the Introduction phrase is judged non-quantitative, the primary outcome is that Sec. 4.2 table; stratum and verdicts do not change.): NSTO optimizes on a coarse grid and super-resolves the result, cutting high-resolution TO time to seconds; in the Daruma task NSTO took 15.51 s versus SIMP's 120.37 s and 475.56 s at 2x and 3x resolution.
- Key phrase: shortening computation from hours/minutes to seconds
- Claimed speed-up: 30.7 (No factor is stated. Derived from the Sec. 4.2 Daruma timing table: SIMP at 55x46x53, 475.56 s / NSTO at 18x15x17, 15.51 s = 30.7. SIMP at 36x30x35 gives 120.37/15.51 = 7.8. SIMP at the same 18x15x17 grid gives 16.03/15.51 = 1.03. The two methods run at different resolutions. The NSTO time does not include the super-resolution step; the text calls that step negligible but gives no time for it.)

- **R1 = fail** [R1-no-quality] — Sec. 4.2 Daruma table: the speed-up exists only against SIMP runs at 2x and 3x resolution (120.37 s, 475.56 s) versus NSTO at 18x15x17 (15.51 s). No compliance or volume is reported for those SIMP runs, and no FE evaluation of the 10x super-resolved Daruma design is reported (Sec. 4.3). At equal resolution the times are similar (16.03 vs 15.51 s). Table 1 compares quality only at equal resolution and has no times. The super-resolution FEA check (1-5x per axis, benchmarks only, Sec. 4.2) includes no SIMP comparison at those resolutions.
- **R2 = pass** [R2-pass (multigrid solver, same PC)] — Sec. 4.2: SIMP uses the same AMG FEA solver in the same environment as NSTO (i9-10900KF plus RTX2080S, Sec. 4.1), with the filter radius tuned. Multigrid is in the protocol's efficient class. Markers (b), (c) and (d) are not established by the text. There is one ambiguity: SIMP's solver is cited as PyAMG [BOS22] while NSTO cites GPU AMGX [NAC*15], so the SIMP device is unclear, but the text asserts the same solver and environment. Markers (a) and (e) need the re-test.
- **R3 = na** [R3-na-per-problem] — Sec. 1 and 3: per-problem, self-supervised neural reparameterization with no dataset and no offline training. The network training is the optimization and is counted in the reported total time (Table 2).
- **R4 = partial** [R4-no-failure-rate] — Table 1: compliance comes from FEA of the optimized designs, and volumes are reported (NSTO 0.00-0.02 above delta). Sec. 4.2: FEA of the super-resolved benchmark designs showed stable compliance for 1-5x per axis; the values appear only in Fig. 3(d). No failure or infeasibility counts are given. No FE evaluation of the 10x super-resolved and smoothed Daruma output is reported (Sec. 4.3).

- Baseline: {"classical_method": "SIMP benchmark following Ferrari and Sigmund 2020 [FS20]; Sec. 4.2 attributes SIMP's initialization to its optimality-criteria update; density filter radius tuned (Sec. 4.2)", "implementation": "Not fully stated. SIMP after [FS20] (the 99-line code family), run with the same algebraic multigrid FEA solver and in the same environment as NSTO (Sec. 4.2). The language of the SIMP port is not stated. NSTO itself uses Python 3.6 and PyTorch (Sec. 3.2, 4.1).", "solver": "Multigrid. NSTO: GPU AMGX [NAC*15] with a multi-level V-cycle hierarchy and Jacobi smoother, tolerance 1e-8, at most 100 iterations (Sec. 3.1). SIMP: stated to use the same AMG solver, but the citation given is PyAMG [BOS22] (Sec. 4.2). Whether SIMP ran on CPU or GPU is not explicit; the text says SIMP at higher resolution might exceed GPU memory, which suggests GPU use [inferred].", "hardware_classical":

## P00130 (decision order 234; provisional top-up 16) — Enhancing Data-driven Multiscale Topology Optimization with Generalized De-homogenization (2021)

- Link: https://arxiv.org/abs/2112.02506
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (Sec. 5 case studies, subsection printed as '4.1 Pinned beam', pp. 21-24 (first quantitative comparison with a classical method; the abstract, introduction and conclusion compare only qualitatively). Chosen under §5.1 rule 4: the section's closing efficiency statement is the only stated speed-up and matches the abstract's high-efficiency claim against macroscale-only optimization): Pinned beam: the NN-surrogate multiscale pipeline (664.50 s [derived]) is claimed more than 5700× faster than SIMP on the same 1800×400 mesh (one iteration timed, ~1000 assumed), and scores 0.0637 vs 0.0705 m·Hz against coarse macroscale SIMP.
- Key phrase: over 5700 times faster than TO on the fine mesh
- Claimed speed-up: 5700 (Stated on p. 24 as a factor above 5700 relative to fine-mesh TO. Not reproducible from the printed numbers: fine-mesh SIMP 3712.12 s for one iteration × ~1000 assumed iterations = 3,712,120 s; proposed method 314.54 s (300 iterations) + 349.96 s de-homogenization = 664.50 s; ratio 5,586 [derived]. With the article's own 300-iteration cap the ratio would be 1,676 [derived]. Against the coarse 90×20 macroscale SIMP (332.51 s) the proposed method is slower: 332.51 ÷ 664.50 = 0.50 [derived]. Database generation and NN training are excluded from all times.)

- **R1 = fail** [R1-no-quality] — pp. 23-24: the 5700× figure sets the pipeline time against an extrapolated SIMP run on the 1800×400 mesh (one timed iteration × ~1000 assumed). No fine-mesh SIMP design or objective is produced, so the speed claim has no quality comparison with its comparator. The only quality comparison (0.0637 vs 0.0705 m·Hz, p. 22) is against coarse 90×20 SIMP, where the pipeline is about 2× slower. Alternative: if the verifier takes the coarse comparison as primary, R1 = pass.
- **R2 = fail** [R2(d)] — pp. 20-24: the fine-mesh SIMP cost assumes about 1000 iterations (citing ref. [28]), while the article's own stopping rule for all its examples stops at 300 iterations at most (Sec. 5 intro), and the proposed method's 314.54 s covers 300 iterations. 1000 ≥ 2 × 300, so the classical estimate uses at least 3.3× the iteration budget of the article's own criterion [derived]; at 300 iterations the claimed ratio falls to about 1,676 [derived]. Both methods ran on a single CPU of the same platform, so (c) does not apply; (b) is not observed (no abstract figure). Pointer for (e): 3712.12 s per fine-mesh iteration with 21 frequency points (≈177 s per frequency point [derived]) needs a frequency-response strong baseline to judge. Alternative: partial (R2-inefficient-impl [inferred]) if (d) is read as applying only to executed runs.
- **R3 = fail** [R3-no-cost] — Sec. 2 and p. 23: the speed statements count only online optimization and de-homogenization (664.50 s [derived]). The offline cost of homogenizing 38,416 microstructures on 100×100 pixels and training the MLP is not reported, and no break-even is given. One surrogate serves all three case studies [inferred], so amortization is plausible but not quantified.
- **R4 = partial** [R4-no-failure-rate] — pp. 21-24, Figs. 10-12: the objective and frequency response of the returned de-homogenized fine-mesh structure are reported (FE analysis inferred from the dynamic simulations on the 4-node mesh mentioned in Sec. '4.3'), and its volume is reported (50.25% vs 50% target). The SIMP design's volume is not reported. Defects from de-homogenization are repaired with morphological operators (Sec. 4.3) without counts, and no failed runs are reported; orientation singularities are outside the study's scope (Sec. 6).

- Baseline: {"classical_method": "Single-scale (macroscale) SIMP frequency-response minimization under the same loads and volume: (i) run on the coarse 90×20 mesh and projected to the 1800×400 fine mesh for evaluation; (ii) on the 1800×400 fine mesh only one iteration was timed and the total extrapolated (pp. 22-24). The proposed pipeline itself uses MMA with a sensitivity filter and a PDE filter (Sec. 3.3)", "implementation": "not stated for SIMP. The de-homogenization uses MATLAB morphological operators (Sec. 4.3); the NN is trained with scaled conjugate gradient (Sec. 2) [MATLAB inferred]", "solver": "not stated", "hardware_classical": "stated to be the platform used for the proposed method, a single CPU; model not stated (p. 23)", "hardware_ml": "a single CPU; model not stated (p. 23)", "problem_size": "Coarse 90×20 = 1,800 elements; fine 1800×400 = 720,000 elements [≈1.44×10^6 nodal DOFs, deriv

## P00166 (decision order 241; provisional top-up 9) — Convolutional Neural Network-based Topology Optimization (CNN-TO) By Estimating Sensitivity of Compliance from Material Distribution (2019)

- Link: https://arxiv.org/abs/2001.00635
- Access: full_text; inclusion: **include** (I-SPEED (screened I-QUALITY; the first quantitative classical comparison in the full text is a computation-time comparison, §5.1 rule 2)); stratum: **speed**
- Primary outcome (Sec. 5.2.1 and Table 2, p. 7 (first quantitative comparison with the classical method; the abstract, conclusion and introduction are qualitative, so §5.1 rule 2 applies)): For 40 density updates on a 16×32 cantilever, CNN-TO took 33.5 s on a Xeon PC with four GPUs, versus 7.28 s for FEM-based SIMP on a 1.60 GHz Core i5 PC; the ML method is about 4.6× slower [derived].
- Key phrase: the proposed method requires more computation time than the previous method
- Claimed speed-up: 0.217 (Derived: 7.28 s (SIMP, 40 updates) ÷ 33.5 s (CNN-TO, 40 updates) = 0.217 (Table 2), i.e. CNN-TO is about 4.6× slower; per update 0.182 s vs 0.84 s [derived]. Different machines: SIMP on a Core i5-4500U PC without GPU, CNN-TO on a Xeon Silver 4112 PC with 4× GTX 1080 Ti (Sec. 4).)

- **R1 = pass** [R1-matched-iterations] — Table 2 and Sec. 5.2.1: both methods are timed for the same 40 density updates, and the filtered final compliances are nearly equal (1,294 vs 1,287, Table 3). Matching is not exact: different post-processing filters (Appendix 1), a SIMP threshold set only to give a volume close to CNN-TO's (Sec. 2.3), unreported final volumes, and no statement on whether filtering time is in Table 2. Unsure, so pass; a stricter reading gives partial (R1-loose).
- **R2 = partial** [R2-hardware-unjustified; R2-inefficient-impl [inferred]] — Sec. 4: SIMP ran on a PC with a Core i5-4500U @ 1.60 GHz and 8 GB RAM, without GPU; CNN-TO ran on a 128 GB Xeon Silver 4112 PC with four GTX 1080 Ti GPUs; the choice is not justified. SIMP needs 0.182 s per update at 16×32 [derived: 7.28 s ÷ 40], which suggests an unoptimized implementation (NumPy/SciPy [inferred]; solver not stated); this is an R2(e) candidate that needs our per-iteration timing at this size. (c) does not apply (about 1.1×10³ DOFs [derived]); (b) and (d) are not established. The asymmetry penalizes the classical side, so it cannot explain the ML method's slower time.
- **R3 = fail** [R3-no-cost] — Sec. 3.2.1-3.2.2 and 4: neither the CNN training time nor the cost of generating the bar-system training structures and their FEM sensitivities is reported (sample count not stated), and no break-even is given; Table 2 covers only the 40 updates. The omission favours the ML side, which is still slower.
- **R4 = partial** [R4-no-constraint-report] — Table 3 and Fig. 11: the compliance of the filtered final designs is reported for both methods (FE analysis [inferred]). Final volumes are not reported, although the authors note that hole filling can break the mass constraint (Sec. 3.2.4). Raw CNN-TO outputs contain disconnected parts that the filter removes (Fig. 7). One example only; no failure count.

- Baseline: {"classical_method": "SIMP compliance minimization (p = 3, volume limit 50%) with optimality-criteria updates from FEM sensitivities, uniform initial density, followed by threshold filtering and floating-island removal (Sec. 2.2-2.4, 4)", "implementation": "not stated for SIMP specifically; the article lists Python with TensorFlow for the CNN and NumPy/SciPy for other calculations (Sec. 4) [SIMP inferred to use NumPy/SciPy]", "solver": "not stated", "hardware_classical": "PC with 8 GB RAM and an Intel Core i5-4500U @ 1.60 GHz, no GPU (Sec. 4)", "hardware_ml": "128 GB PC with an Intel Xeon Silver 4112 @ 2.60 GHz; CNN run in parallel on 4× NVIDIA GTX 1080 Ti (Sec. 4)", "problem_size": "16×32 elements, cantilever (Sec. 4) [derived: 1,122 nodal DOFs]", "classical_iterations": "fixed 40 density updates for both methods in the comparison (Table 2; Fig. 11 caption); Sec. 2.4 describes a change-

## P00047 (decision order 243; provisional pilot 3) — Mechanostat-type effective density correction for Carter-Hayes growth applied to topology optimization and its efficient interpolation for a target strain energy and volume fraction (2025)

- Link: https://arxiv.org/abs/2503.21456
- Access: full_text; inclusion: **include** (I-SPEED); stratum: **speed**
- Primary outcome (abstract, paragraph 3; the speed-up factor is stated in Sec. 7 (discussion of Fig. 18)): A small physics-loss network (D2NN), trained for 500 epochs on 20 topology images, gives designs said to resemble 2,000 iterations of the authors' non-learned logarithmic SIMP scheme; once trained, a roughly 25-fold speed-up is claimed.
- Key phrase: similar results to 2,000 steps worth of vanilla iteration within 500 training epochs
- Claimed speed-up: 25 (Stated in Sec. 7 for the trained D2NN versus the vanilla scheme. No times are printed for either method, so the factor cannot be re-derived. The abstract's 2,000 iterations versus 500 training epochs compares effort in different units and is not a time ratio.)

- **R1 = partial** [R1-loose-matching] — Sec. 7, Fig. 18: quality parity with the 2,000-iteration reference rests on visual similarity of stress maps. No compliance or volume values are given for D2NN outputs. The reference uses a fixed iteration count with no stated convergence check, and the authors concede the match is inexact.
- **R2 = partial** [R2-hardware-unjustified] — Sec. 6.1, Sec. 7: hardware is given only for one classical run (single core, i7 1.8 GHz) and not for the D2NN or the Sec. 7 comparison; the baseline builds on the educational top88.m code. Markers (b)-(d) are not established: the article shows no convergence evidence for the 600x200 reference. R2(e) is not decidable yet: the derivable per-iteration time of the 1000x200 run (about 5.4 s [derived]) needs a same-size single-core strong-baseline measurement, and it belongs to a different problem than the primary outcome.
- **R3 = partial** [R3-no-data-cost] — Abstract, Sec. 7: training is counted only as 500 epochs, with no time. The cost of producing the 20 training topologies with the vanilla scheme itself is not reported, and no break-even is given.
- **R4 = partial** [R4-no-constraint-report] — Sec. 7, Fig. 18: D2NN outputs are analysed in FEBio (stress maps), but no compliance, volume or constraint values and no failure count are reported. Only 4 target points plus the full block are shown.

- Baseline: {"classical_method": "The authors' own non-learned scheme, termed the vanilla iteration: SIMP compliance minimization built on top88.m, with the mechanostat-type logarithmic volume update (Eq. 15) and the twigcutter erosion filter (Sec. 2-3, Algorithm 1)", "implementation": "MATLAB top88.m, the 88-line educational code (ref. [1]), plus the authors' twigcutter.m (Sec. 3); D2NN framework not stated", "solver": "not stated [inferred: top88.m solves with MATLAB sparse backslash, a direct solver; recalled from the public top88 code, not stated in the article]", "hardware_classical": "single-core i7 1.8 GHz, 16 GB RAM (Sec. 6.1); stated for the filtered Fig. 8 cantilever run, not for the Sec. 7 comparison", "hardware_ml": "not stated", "problem_size": "D2NN comparison: 600x200 cantilever (Sec. 7); timed classical run: the Fig. 8 cantilever, which the Fig. 2 caption identifies as the 1000x200 c

## P00074 (decision order 262; provisional top-up 29) — Neural topology optimization: the good, the bad, and the ugly (2024)

- Link: https://arxiv.org/abs/2407.13954
- Access: full_text; inclusion: **include** (I-SPEED); stratum: **speed**
- Primary outcome (Sec. 2, optimizer trajectories and Fig. 4 (first measured comparison with the classical baseline), quantified in Sec. 4 (Fig. 6) and SI Sec. E.4, Tables 4-5; the abstract, introduction and discussion compare only qualitatively): Neural reparameterizations (MLP, SIREN, CNN) reach compliance close to the SIMP+MMA baseline but usually need more iterations to converge; over 18 compliance problems with MMA, median iteration ratios to the baseline are 1.69-16.56 (SIREN), 0.93-13.04 (MLP), 0.34-3.12 (CNN).
- Key phrase: neural TO usually requires more iterations to converge as compared to the baseline method
- Claimed speed-up: None (No speed-up is claimed; neural TO is mostly slower, and no wall-clock time is reported. SI Tables 4-5 give iterations to convergence scaled to the baseline (ML/classical; each cell lists median, best and worst over six initializations [order inferred from SI E.4]). Median over the 18 problems of the per-problem medians [derived]: MMA - CNN 1.20, SIREN 5.21, MLP 4.80; Adam - CNN 1.46, SIREN 3.54, MLP 2.08, i.e., classical/ML about 0.19-0.83. Medians below 1 (network faster) [derived]: with MMA, CNN 8 of 18, MLP 3, SIREN 0; with Adam, CNN 8, MLP 6, SIREN 0.)

- **R1 = pass** [R1-matched] — Sec. 4 and SI E.4: all methods use the same FE model and volume constraint, the objective is compared at an equal budget of 200 function evaluations, and iteration counts are reported together with objective and thresholded compliance for all 18 problems (SI Tables 4-5). The speed finding goes against the ML method, so no inflated speed claim needs quality matching. For the alternative best-of-six CNN+MMA claim (Sec. 4), the ML side gets six initializations against one deterministic baseline run [inferred].
- **R2 = pass** [R2-none-established] — Sec. 6 and SI E: the baseline is SIMP with MMA from the 88-line formulation, in the same JAX code and FE model (direct LU solver) as the networks, with its MMA hyperparameters tuned per case like theirs (SI E.3) and no continuation for either. The metric is an iteration count, so hardware does not bear. (b) the abstract gives no numbers; (c) no timing; (d) the convergence iteration is measured per run, not fixed. Nothing suggests a weak baseline.
- **R3 = na** [R3-na-per-problem] — Per-problem neural reparameterization with no offline data (Sec. 6); the uniform-density pretraining (300 Adam iterations, no FE analysis) is described as negligible (SI E.1). For C3: Optuna hyperparameter tuning (25 outer iterations per case at 64x32, SI E.3) is not costed for either method.
- **R4 = partial** [R4-no-failure-rate] — Sec. 4 and SI E.2, E.4: objective and thresholded compliance come from the FE model for every run, and volume is enforced by MMA, by the shifted sigmoid (Adam) or by thresholding to the target volume. Failures are not quantified: SI Tables 4-5 contain cross entries that the captions do not define [failed runs inferred], MMA is said to struggle with the volume constraint for the networks (SI C.2), and thresholded compliance is rescaled by a volume ratio when the thresholded volume deviates slightly (SI E.2).

- Baseline: {"classical_method": "Density-based SIMP (p = 3, density filter, no continuation) with MMA, re-implemented from the 88-line code (Sec. 6; SI B, E)", "implementation": "Authors' in-house JAX TO library with a Python MMA implementation (ref. [47]); the baseline's MMA move limit and asymptote initialization were tuned per case with Optuna (TPE, 25 outer iterations) at 64x32 and reused at higher resolution, as for the networks (SI E.3)", "solver": "direct LU solver (SI E)", "hardware_classical": "not stated", "hardware_ml": "not stated (GPU training is mentioned only for the expressivity study, Sec. 3 footnote)", "problem_size": "576x288 elements for the 18-problem benchmark (Fig. 6 caption); 64x32 for the landscape and trajectory study (SI D); 544x272 and 544x544 for the SI E.5 problems", "classical_iterations": "Objective metric: best value within a fixed budget of 200 function evaluations

## P00152 (decision order 264; provisional pilot 7) — Scalable Deep-Learning-Accelerated Topology Optimization for Additively Manufactured Materials (2020)

- Link: https://arxiv.org/abs/2011.14177
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (abstract (also introduction and conclusion); quantified in Section 3 and Fig. 6b, p. 6): On a 1024×1024 two-material heat-conduction design run for 200 iterations, SDL-TO on 128 Summit nodes reaches a design close to sequential MMA-based TO on one CPU, with about 8.6× shorter time-to-solution.
- Key phrase: a speed up of around 8.6x over the standard TO implementation
- Claimed speed-up: 8.6 (Stated: abstract and Fig. 6b give 8.6× (label 8.60× at 128 Summit nodes vs the single-CPU sequential TO, heat conduction 1024×1024, 200 iterations). Absolute times are shown only as bars.)

- **R1 = partial** [R1-loose] — Section 3, Figs. 5–6: both methods run a fixed 200 iterations on the 1024×1024 problem. Quality is shown only as objective histories and design images, with no printed final objective (Fig. 6a inset suggests SDL-TO slightly higher [read from plot]). Matching is at equal iteration count, not at equal quality, wall-clock or FE-evaluation budget (SDL-TO adds parallel local-sample FE runs at 12 learning steps; sample count not stated). Bridge objectives agree within 0.15–0.23% (Fig. 3), but bridge timing is only in bars (Fig. 4d).
- **R2 = fail** [R2(c)] — Section 2: the baseline is the authors' NumPy MMA code on a single CPU; SDL-TO uses up to 128 Summit nodes with 6 NVIDIA V100 GPUs each (distributed GPU training) plus parallel CPU simulations. The 8.6× (Fig. 6b) is at 128 nodes on a 1024×1024 mesh (≈1.05×10⁶ nodal DOFs [inferred], above 10⁵). The only rationale is that parallel solvers and physics are outside the study's scope (Section 2), which does not justify the hardware asymmetry; at 16 nodes the gain is 1.08× (Fig. 6b).
- **R3 = na** [R3-per-problem] — Section 2, Figs. 1–2: the gradient surrogate is trained online on local samples from the same optimization run; there is no offline dataset or pre-training. Its cost sits inside the reported time-to-solution [inferred; not broken out], so it is judged under R1/R2.
- **R4 = partial** [R4-no-constraint-report] — Figs. 3, 4a–c, 6a: objectives of the returned designs are reported (bridge numerically, heat conduction as curves). FE evaluation of the final SDL-TO designs is not described but is needed to compute these objectives [inferred]. Volume-constraint satisfaction and any failed runs are not reported; the heat-conduction final objective is not given as a number.

- Baseline: {"classical_method": "Modified SIMP density TO with adjoint gradients and MMA, run sequentially (Seq-TO) (Section 2)", "implementation": "Authors' own NumPy implementation on a single CPU (Section 2, TO baseline method paragraph)", "solver": "not stated (FEM solve of the state equation; linear solver type not given)", "hardware_classical": "a single CPU; model not stated (Section 2)", "hardware_ml": "ORNL OLCF Summit, 16/32/64/128 nodes, each 2 IBM Power9 CPUs + 6 NVIDIA V100 GPUs with NVLink; mpi4py for parallel simulations, Horovod for distributed GPU training (Section 2)", "problem_size": "Heat conduction 1024×1024 mesh (Section 3, Fig. 5); bridge 480×160 and 960×320 (Fig. 3)", "classical_iterations": "fixed 200 iterations for heat conduction (Section 3); bridge histories shown to 200 iterations (Fig. 4a)", "classical_time": "not printed; Fig. 6b bar about 6×10³ s for Seq-TO heat cond

## P00428 (decision order 282; provisional top-up 8) — IH-GAN: A Conditional Generative Model for Implicit Surface-Based Inverse Design of Cellular Structures (2022)

- **FLAG — conflict of interest: Co-authored by the user's PhD advisor. The second coder verifies this record; disclose in the manuscript.**
- Link: https://arxiv.org/abs/2103.02588
- Access: full_text; inclusion: **include** (I-QUALITY (screening code confirmed at full text)); stratum: **quality**
- Primary outcome (Abstract (also Sec. 1 contribution 5 and the Conclusion); numbers in Table 2 and Sec. 8.4.1): In the minimum-compliance cantilever at 45% density, the IH-GAN multi-type graded cellular beam had 79.7% lower peak von Mises stress (10,302.0 vs 50,800.8 MPa) and 3.03% lower maximum displacement than the variable-density single-type TPMS beam.
- Key phrase: improve the optimized structural performance over the conventional variable-density single-type structure
- Claimed speed-up: None (Quality-only primary outcome; no classical runtime is reported. IH-GAN training takes 38 s and inference under 1 s (Sec. 7.2); the 93 h quoted for Zhu et al.'s level-set gamut construction (Sec. 2.1.2) is a literature figure for a different pipeline, not a measured comparison. Not derivable.)

- **R1 = partial** [R1-loose] — Table 2 and Sec. 8.4.1: all three structures carry the same 100 N load at the same 45% density, so volume is matched. Matching is loose: no iteration count, stopping rule or compute budget is stated for the modified SIMP (IH-GAN side) or for the [23] variable-density optimization; the headline gain is in peak von Mises stress (10,302.0 vs 50,800.8 MPa), which is not the optimization objective and which the authors call mesh-sensitive (Sec. 9.1), while compliance differs by 0.38% [derived]; the target-deformation comparison drops the mass constraint and reports no density for either design (Sec. 6.2, Table 3).
- **R2 = partial** [R2(b) [judgment call]] — Abstract vs Sec. 9.1 and Fig. 18: the abstract reports gains only against the variable-density single-type D-surface structure, while Sec. 9.1 reports a SIMP solid-material design at the same 45% volume that beats the IH-GAN design on max displacement (0.1326 vs 0.1630 mm), compliance (7.1227 vs 7.3876 N·mm) and max stress (7,630.4 vs 10,302.0 MPa). The authors treat the solid design as a different design class and argue for porous designs' other benefits. A strict reading of (b) gives fail; a same-class scope reading gives pass. The [23] comparator's implementation, solver and iteration count are not stated (Sec. 8.4).
- **R3 = na** [R3-na-no-speed-claim] — The primary outcome is design quality only; no classical runtime is compared. For C3: IH-GAN training 38 s on a GTX TITAN X and inference under 1 s (Sec. 7.2); the cost of homogenizing the 924 training unit cells is not reported (Sec. 7.1); the 93 h figure (Sec. 2.1.2) is quoted from Zhu et al. [22], not measured here.
- **R4 = partial** [R4-no-constraint-report] — Sec. 8.4 and footnote 5: the assembled IH-GAN and comparator structures are meshed (650,000+ tetrahedra) and analysed in ABAQUS, so quality rests on FE analysis of the returned designs. Table 2 lists the prescribed 45% density; the achieved density of the assembled structures is not reported, although generated cells carry volume-fraction errors (most means within -2% to 3%, Fig. 11), and the target-deformation designs have no reported density. Connectivity is reported as mean interface overlap 96.43% with a minimum of 30.0% (Sec. 8.3), but the number of weak interfaces and whether blending was applied before the FE runs are not stated; the rule for choosing the best candidates among GAN samples (Fig. 2c) is not given.

- Baseline: {"classical_method": "Variable-density single-type D-surface TPMS cellular structure whose unit-cell densities are optimized by the method of Li et al. [23] (J. Mech. Des. 141(7)); uniform D-surface structure without optimization; in Sec. 9.1, a SIMP solid-material design at the same volume fraction (Sec. 8.4, 9.1)", "implementation": "not stated for the [23] optimization or the SIMP solid design. IH-GAN side: modified SIMP over E, ν and ρ maps with a property-space distance constraint (Sec. 6). FE validation of all assembled designs with iso2mesh and ABAQUS 2017 (footnote 5)", "solver": "not stated for the TO runs; FE validation in ABAQUS 2017, solver settings not stated (footnote 5)", "hardware_classical": "not stated for TO; meshing and FE validation on a PC with a 2.9 GHz Intel Core i9-8950HK CPU and 32 GB RAM (footnote 5)", "hardware_ml": "IH-GAN training on a GeForce GTX TITAN X (S

## P00501 (decision order 286; provisional top-up 28) — Large Language Models as Optimization Controllers: Adaptive Continuation for SIMP Topology Optimization (2026)

- **FLAG — conflict of interest (unconfirmed): Corresponding author is a Jun Wang (Santa Clara University), per the coding agent. Confirm whether this is the user's PhD advisor; if so, the second coder verifies this record.**
- Link: https://arxiv.org/abs/2603.25099
- Access: full_text; inclusion: **include** (I-QUALITY); stratum: **quality**
- Primary outcome (Abstract (quantitative classical comparison); values in Table 5 (2D, Sec. 4.1) and Table 7 (3D, Sec. 4.4)): On three 2D (120x60) and two 3D (40x20x10) compliance benchmarks with 300 main iterations, LLM-controlled SIMP gives the lowest mean final compliance, 5.7% to 18.1% below the fixed no-continuation SIMP baseline, with binary designs.
- Key phrase: The LLM agent achieves the lowest final compliance on every benchmark
- Claimed speed-up: None (No speed claim; the LLM agent is mostly slower. Wall-clock (Tables 5 and 7): LLM agent 445.2 s, 562.4 s, 150.1 s (2D cantilever, MBB, L-bracket) and 1198 s, 1685 s (3D cantilever, MBB) vs fixed 384.9, 425.3, 343.3, 1044, 1014 s and three-field continuation 337.4, 396.4, 268.5, 994, 1059 s. Classical/ML time vs fixed: 0.86, 0.76, 2.29, 0.87, 0.60 [derived]. Sec. 5.3 states a 32-42% overhead vs three-field continuation on the 2D cantilever and MBB beam.)

- **R1 = partial** [R1-loose] — Sec. 3.4-3.5, Tables 5 and 7: all controllers share the mesh, volume fraction 0.40 and 300 main-loop iterations. The headline comparator is not matched: the fixed controller gets no 40-iteration sharpening tail while the LLM run does, and it ends gray (G up to 0.260) while the LLM design is binary, so compliance is compared between a penalized gray field and a binary one [inferred]. Wall-clock is not matched (the LLM agent is slower than the fixed controller on 4 of 5 benchmarks), achieved volume is not reported, and the agent's hyperparameters were meta-tuned on the same three 2D problems with the fast preset (Sec. 3.3; Table 4 caption), while the classical schedules were set by hand.
- **R2 = fail** [R2(b)] — Abstract vs Tables 5 and 7 and Sec. 4.1: the abstract quantifies the gain only against the fixed no-continuation controller (-5.7% to -18.1%), while the results contain stronger classical comparators, standard three-field continuation and an expert heuristic, against which the margins are 0.09-1.92% in 2D (Sec. 4.1) and 0.22-0.43% in 3D [derived from Table 7]. The abstract names these baselines but gives numbers only for the weakest. [judgment call: a verifier who reads the abstract's claim of lowest compliance on every benchmark as reporting the stronger baselines may code partial or pass]
- **R3 = na** [R3-na-quality-stratum] — Quality stratum; no speed claim; zero-shot LLM with no training data. For C3: API cost is called negligible without a figure; about 900 inner-loop calls for the 2D comparison, about 60 for 3D and about 24 for the meta-loop (Sec. 5.3).
- **R4 = partial** [R4-no-failure-rate] — Tables 5 and 7: compliance of every returned design (after the tail) comes from the solver's FE analysis, and grayness is reported for all controllers over 5 seeds. Achieved volume fractions are not reported. When the API was unavailable or returned an invalid answer, the agent fell back to a deterministic ramp; these fallbacks were logged and excluded from the primary results, and the number of affected runs or calls is not reported (Sec. 3.2). The fixed controller's failure to produce a valid snapshot on the 3D MBB beam is disclosed (Table 7 footnote).

- Baseline: {"classical_method": "Three-field SIMP (density filter, Heaviside projection) with OC updates under four non-learned controllers (Sec. 3.4): fixed (p = 3, beta = 1, r_min = 1.5, move limit 0.2, no continuation, no tail); standard three-field continuation (p ramp 1 to 4.5 over 30 iterations, beta doubled every 10); expert heuristic; schedule-only ablation. The primary outcome uses the fixed controller.", "implementation": "Authors' own three-field SIMP solver using SciPy and pyamg [Python inferred from the libraries]; source code promised upon acceptance (Data and Code Availability)", "solver": "direct sparse factorization (SciPy) in 2D; AMG-preconditioned conjugate gradient (pyamg) in 3D, hierarchy rebuilt when element stiffness changes by more than 15% (Sec. 3.5)", "hardware_classical": "not stated", "hardware_ml": "not stated; LLM is gemini-3.1-flash-lite-preview via the Gemini API at 

## P00054 (decision order 349; provisional top-up 2) — Meta-neural Topology Optimization: Knowledge Infusion with Meta-learning (2025)

- Link: https://arxiv.org/abs/2502.01830
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text; cost proxy = iterations, i.e. FE evaluations, to convergence)); stratum: **speed**
- Primary outcome (Abstract; quantified in Sections 4.1 and 4.3, Fig. 6(a),(c) and Table 2): Across 1000 in-distribution (64×64) and 1000 cross-resolution (256×256) compliance tasks, meta-neural TO reached the shared stopping rule in the fewest iterations in 57.6% and 74.1% of tasks (standard GCMMA TO: 42.3%, 25.7%), with thresholded compliance called competitive.
- Key phrase: converges in fewer iterations in 57.6% of in-distribution and 74.1% of cross-resolution tasks
- Claimed speed-up: 1.07 (Proxy (iterations to convergence; one FE solve per iteration), derived from Table 2 means: standard TO 111.26 ÷ meta-neural TO 103.65 = 1.07 (in-distribution); 130.03 ÷ 100.90 = 1.29 (cross-resolution); 110.89 ÷ 126.57 = 0.88 (out-of-distribution, standard TO faster). No factor is stated. Wall-clock [derived from Table 3 per-iteration times × Table 2 means]: 64×64 standard 111.26 × 46.11 ms ≈ 5.13 s vs meta-neural 103.65 × 62.49 ms ≈ 6.48 s, i.e. 0.79 (meta-neural slower); 256×256 130.03 × 723.13 ms ≈ 94.0 s vs 100.90 × 672.90 ms ≈ 67.9 s, i.e. 1.38. The per-iteration times come from three separate benchmark tasks, so these wall-clock ratios are approximate.)

- **R1 = partial** [R1-loose] — Sections 3.3-4.3, Fig. 6, Tables 2-3: all methods share one stopping rule (relative loss change < 10⁻⁵, 10-200 iterations) and the same volume (exact volume enforcement and volume-preserving thresholding), and quality is reported for every task. The iteration comparison is not made at matched quality or matched budget: in-distribution, standard TO gives the best thresholded design in 63.1% of tasks vs 20.3% for meta-neural TO (83.9% vs 80.9% within 5%). The iteration counts also ignore the per-iteration cost gap that Table 3 reports (62.49 vs 46.11 ms at 64×64).
- **R2 = partial** [R2-inefficient-impl (untuned default GCMMA)] — Section 4: standard TO uses GCMMA with default NLopt settings and no tuning, while neural TO was tuned on a validation set and reported as the best of three seeds, and meta-neural TO was grid-searched (Appendix A). Section 4.1 attributes standard TO's slow early loss reduction to these default GCMMA parameters; Section 4.6 says the implementations are not fully optimized. The linear solver is a sparse direct Cholesky (CHOLMOD) shared by all methods [public repository, checked], so the solver class is efficient. (b), (c) and (d) are not established: the abstract gives no baseline figure, the hardware and stopping rule are the same for all methods. (e) needs a re-test with the article's update; per-iteration times are 46.11 ms (64×64) and 723.13 ms (256×256) (Table 3).
- **R3 = partial** [R3-no-amortization] — Table 3 and Section 4.6: the meta-training cost (3 h 35 min, one A100) is reported and expressed as about 1500 full 64×64 optimizations that amortize over later problems, but no break-even is computed. Data cost is one FE analysis per task (Section 3.4), time not stated [small, inferred]; the hyperparameter grid search reran meta-training for 8 configurations (Appendix A), not counted [inferred]. From Tables 2-3 [derived]: at 64×64 meta-neural TO averages ≈6.48 s per task vs ≈5.13 s for standard TO, so there is no saving to amortize; at 256×256, ≈67.9 s vs ≈94.0 s gives break-even after ≈494 tasks.
- **R4 = partial** [R4-no-failure-rate] — Fig. 6 d-f and Sections 3.2-3.3: the compliance of each thresholded returned design is computed with the FE model for all 1000 tasks per test set. Volume is enforced by construction (bisection for the neural methods, the GCMMA constraint for standard TO, then volume-preserving thresholding), but achieved volumes are not reported. A failure share is given only for the compound-shift set (Appendix F.2: thresholded designs at least 10× worse than the best in 9.2%, 5.8% and 3.1% of tasks for standard, neural and meta-neural TO). Appendix B drops tasks with more than 50% thresholding degradation without giving a count.

- Baseline: {"classical_method": "Standard density-based TO (modified SIMP, p = 3, Emin = 10⁻⁹, ν = 0.3) solved with GCMMA using default NLopt settings and no hyperparameter tuning; uniform initial design; volume-preserving thresholding of final designs (Sections 3.1, 3.3, 4). The filter for standard TO is not stated in the article [the repository applies the same density filter, radius 1/32 of the domain]", "implementation": "Authors' JAX code; gradients by implicit differentiation through the linear solve (Section 3.1); the authors say the implementations are not fully optimized (Section 4.6). Repository [checked 2026-09-24]: FE solve by cvxopt CHOLMOD through a JAX callback (metatopia/solver/fem_cvxopt.py); standard TO = nlopt.LD_MMA with ftol_abs = ftol_rel = tol and maxeval 201 (experiments/meta_neural_to/mma.py)", "solver": "direct (sparse Cholesky, CHOLMOD via cvxopt), shared by all methods, 

## P00133 (decision order 362; provisional top-up 20) — Length Scale Control in Topology Optimization using Fourier Enhanced Neural Networks (2021)

- Link: https://arxiv.org/abs/2109.01861
- Access: full_text; inclusion: **include** (I-SPEED (screened I-UNCLEAR; the first quantitative classical comparison lists FE-iteration counts beside compliance and adds a run-time parity statement)); stratum: **speed**
- Primary outcome (Sec. 5.1 and Fig. 9 (first quantitative comparison with a classical method; the abstract, introduction and conclusion make no comparison with a classical method)): On four 60×30 benchmarks, Fourier-TOuNN reached 10.4-18.1% lower compliance than the 88-line SIMP code [derived] while using 151 versus 92-131 FE iterations; its 4-6 s run time is described as comparable to mesh-based codes.
- Key phrase: the compliance values are lower (better) than both SIMP and TOuNN
- Claimed speed-up: 0.79 (No speed-up is claimed and no SIMP run time is printed. Proxy from the FE-iteration counts in Fig. 9, SIMP ÷ Fourier-TOuNN: 119/151 = 0.79, 92/151 = 0.61, 119/151 = 0.79, 131/151 = 0.87; median 0.79 [derived], i.e. Fourier-TOuNN needs more FE solves. Sec. 5.1 gives 4-6 s per example and says this matches mesh-based codes like the 88-line code.)

- **R1 = pass** [R1-no-speed-advantage-claimed] — Sec. 5.1 and Fig. 9: compliance and FE-iteration counts are printed side by side for all four cases on the same mesh and volume targets. Fourier-TOuNN needs more FE iterations (151 vs 92-131) and the text claims only run-time parity, so no speed claim needs quality matching. The quality comparison itself is loose (see R4): attained volume is not reported and the penalization probably differs; a verifier who weighs this may choose partial (R1-loose).
- **R2 = pass** [R2-none-established] — Sec. 5 and 5.1: the baseline is the published 88-line SIMP code with filter radius 1.4, and all experiments ran on the same i7-6700 CPU. (b) is not observed (no classical figure in the abstract); (c) does not apply (CPU only; ≈3.8×10³ DOFs [derived]); (d) is not established (SIMP stops by its own criterion after 92-131 iterations); (e) is not derivable (no SIMP time). A stronger baseline would only widen Fourier-TOuNN's iteration disadvantage.
- **R3 = na** [R3-na-per-problem] — Sec. 3-4, Algorithm 1: the network weights are optimized per problem from a Glorot initialization with no dataset or offline training; the cost sits inside the 4-6 s run time.
- **R4 = partial** [R4-no-constraint-report] — Fig. 9 and Sec. 3.2-3.3: the printed compliance comes from the FE model on the 60×30 mesh [inferred final-iteration objective], but the attained volume fraction of the Fourier-TOuNN designs is never reported although the volume constraint is only a growing penalty (about 30 at iteration 151 [derived from Table 1]). The two methods are probably not scored at the same penalization: the SIMP penalty for Fig. 9 is not stated (the 88-line default is p = 3 [recalled]) and its designs are partly gray, while Fourier-TOuNN's continuation reaches p ≈ 4.0 by iteration 151 [derived from Table 1] on near-binary designs. The displayed high-resolution extraction (15×15 samples per element) is not re-analysed, and disconnected designs (Sec. 5.5) are described without counts.

- Baseline: {"classical_method": "SIMP minimum compliance with the 88-line code (ref. [50]), filter radius 1.4, no extra length-scale control (Sec. 5.1, Fig. 9); published classical length-scale methods compared visually or by reported compliance in Sec. 5.2 (refs. [17], [53])", "implementation": "88-line MATLAB educational code (ref. [50]); Fourier-TOuNN in Python and PyTorch with a CVXOPT Cholesky FE solve (Sec. 3.2, 5). The public repository also holds a Python SIMP port (topopt99.py, crediting the Aage-Johansen Python code) [file list and header checked 2026-09-24]; the article names only ref. [50] for the Fig. 9 SIMP column", "solver": "Fourier-TOuNN: sparse Cholesky via CVXOPT (Sec. 3.2). SIMP: not stated (the 88-line code uses a sparse direct solve [recalled, not verified in-session])", "hardware_classical": "Intel i7-6700 CPU at 2.6 GHz with 16 GB RAM, stated for all experiments (Sec. 5)", "

## P00326 (decision order 378; provisional top-up 30) — Data-driven multifidelity topology design with multi-channel variational auto-encoder for concurrent optimization of multiple design variable fields (2024)

- Link: https://arxiv.org/abs/2409.04692
- Access: full_text; inclusion: **include** (I-QUALITY); stratum: **quality**
- Primary outcome (Sec. 5.2.1, Figs. 9-10 (first quantitative classical comparison; the abstract and conclusion state superiority over the reference solutions only qualitatively)): In stiffness maximization of a rib-reinforced cone shell, the MC-VAE framework's designs beat 100 reference designs from classical TO extruded to uniformly sampled heights at low volume; at equal volume 0.015 strain energy is 24% lower (9.9x10^3 vs 1.3x10^4).
- Key phrase: leading to a 24% lower strain energy than that of the reference model
- Claimed speed-up: None (No runtime, hardware or evaluation count is reported for any method. The conclusion claims, without numbers, that the framework reduces computational demand by replacing parametric studies over HF parameters with a single run. Not derivable.)

- **R1 = partial** [R1-loose] — Sec. 5.2.1, Figs. 9-10: both sets are scored by the same high-fidelity FE model and compared at equal volume (0.015 in Fig. 10; Pareto sets in Fig. 9). The budget is not matched: the reference set is 100 designs with randomly sampled heights, while the framework runs 24 iterations of 256 MC-VAE samples plus mutants [over 6,000 HF evaluations inferred from Table 1 and Algorithm 1], and neither side reports evaluation counts or times.
- **R2 = partial** [R2-weak-comparator [judgment]] — Quality stratum, competence of the comparator. Sec. 4.1, 5.2.1, Table 2: the reference designs come from standard SIMP/MMA runs in a general-purpose commercial code (COMSOL), capped at 50 MMA iterations with fixed projection beta = 4, and their rib heights are sampled uniformly rather than optimized, although height is exactly the variable the framework adds. No classical run that also optimizes the height (e.g., as a sizing variable) is tried. None of markers (a)-(e) applies; unsure whether a stronger classical comparator would close the gap.
- **R3 = na** [R3-na-quality-stratum] — Quality stratum; the VAE is retrained inside each design run with no offline training data (Sec. 2.2, 4.2), and no speed claim is quantified. For C3: no low-fidelity TO, HF evaluation or VAE training times are reported; the conclusion's cost-reduction claim has no numbers.
- **R4 = partial** [R4-no-failure-rate] — Sec. 4.3, 5.2.1: every candidate, including the reference designs, is binarized, extruded and analysed with the high-fidelity solid FE model, and the volume of each design is reported as the second objective (Figs. 9-10). Infeasible candidates are discarded before selection (Algorithm 1, line 12), and samples violating the volume constraint after smoothing were removed from the initial dataset (Sec. 5.2.1), with no counts. Fig. 10 shows one chosen pair at equal volume; Fig. 9 shows the full sets.

- Baseline: {"classical_method": "100 reference solutions: low-fidelity stiffness-maximization TO (SIMP with density filter and Heaviside projection, MMA, discrete adjoint in COMSOL) over a range of maximum-volume constraints [inferred; the reference volumes are not listed], each extruded to a rib height sampled uniformly from the framework's HF-parameter range and evaluated with the same high-fidelity solid FE model (Sec. 3.1, 4.1, 5.2.1)", "implementation": "COMSOL Multiphysics 6.1 controlled by MATLAB 2023a scripts (Sec. 4)", "solver": "not stated (COMSOL)", "hardware_classical": "not stated", "hardware_ml": "not stated (TensorFlow 2.12.0 MC-VAE; HF evaluations run in parallel, Sec. 4)", "problem_size": "Low fidelity: 64x64 shell elements on a cone surface (Table 2); high fidelity: extruded solid models with boundary-refined P1 tetrahedral meshes, size not stated (Sec. 4.3, 5.1)", "classical_iter

## P00214 (decision order 386; provisional pilot 11) — Steering topology distributions for unified generative design of architected metamaterials (2026)

- Link: https://arxiv.org/abs/2607.24777
- Access: full_text; inclusion: **include** (I-QUALITY); stratum: **quality**
- Primary outcome (Section 2.1 and Fig. 2g (main text); numbers in Supplementary Table 3 (Appendix E.1)): On thermal-conductivity extremization of a 256×256 periodic cell at 0.4 volume fraction, GenTO matched classical density-based TO for maximization (best 0.2498 vs 0.2493) and gave the best valid minimization design (0.0323) where TO's design failed feasibility.
- Key phrase: GenTO significantly outperforms both TO and GA
- Claimed speed-up: None (No speed or runtime comparison with a classical method anywhere. Efficiency is discussed only as evaluation budgets (Supp. F.1, Tables 7-8), and the TO budget is given only as one trajectory, without an iteration count. Not derivable.)

- **R1 = partial** [R1-loose] — Supp. E.1, Table 3: all designs at volume fraction 0.4, same FFT evaluator and feasibility checks, so volume and constraints are matched. Budget is not matched against TO: GenTO uses ~1.3×10^4 evaluated candidates per objective (Supp. Table 8) plus unreported sampling and fine-tuning cost, while TO is one run whose iteration count and stopping rule are not stated; the Discussion says TO was handled outside the equal-budget comparison. Against TO, the minimization advantage consists of TO's single run returning an infeasible design.
- **R2 = na** [R2-na-quality-only] — Primary outcome compares design quality only; no classical runtime or speed claim is made, so the efficiency criteria (a)-(e) do not bear on it. For the record: TO mesh, FE solver, penalty exponent value, filter radius and iteration count are not stated (Supp. D.3).
- **R3 = na** [R3-na-no-speed-claim] — No speed or cost claim against TO. For C3: pretraining, sampling and fine-tuning costs are not reported (Supp. F.1); the pretraining data are procedurally generated, not TO outputs (Supp. B.1).
- **R4 = pass** [R4-verified] — Supp. C.1 and E.1: returned binary designs of every method are re-scored by the same FFT homogenization solver at fixed volume fraction 0.4, with connectivity and minimum-feature checks; the infeasible TO minimization design is reported as a failure (Supp. Table 3). Not reported: the share of GenTO samples rejected by screening during steering.

- Baseline: {"classical_method": "Density-based TO with SIMP-type penalized interpolation, sensitivity filtering and an optimality-criteria-type update for maximization tasks, one optimization trajectory (Supp. D.3). Other baselines: Best in training sets, Best in Prior, generator-seeded GA (Supp. D.1, D.2, D.4)", "implementation": "not stated in the article; the public repository (MIT licence) has top-level Training/ and Generation/ folders and no TO or GA baseline code was seen (README checked 2026-09-24)", "solver": "TO: FE analysis, solver type not stated (Supp. D.3). Final scoring of all methods: FFT-based Lippmann-Schwinger homogenization, 256×256 grid, 500 fixed-point steps per loading direction (Supp. C.1)", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "2D periodic unit cell, 256×256 binary grid, volume fraction 0.4 (Supp. C.1)", "classical_iterations": "n

## P00174 (decision order 400; provisional top-up 25) — Deep Generative Design: Integration of Topology Optimization and Generative Models (2019)

- Link: https://arxiv.org/abs/1903.01548
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-UNCLEAR; the only classical comparison is a qualitative diversity comparison with TO-only exploration, Sec. 7.1, Figs. 13-14; no runtime of any method is compared)); stratum: **quality**
- Primary outcome (Abstract (qualitative; §5.1 rule 3, because no quantitative comparison of the learned model with a classical method exists anywhere); supporting classical runs in Section 7.1, Figs. 13-14 (pp. 16-17)): The TO-plus-GAN framework is claimed to yield more aesthetic, diverse and robust wheel designs than earlier generative-design methods; the supporting classical runs are qualitative: TO without reference designs gives near-identical or unconverged results (Sec. 7.1).
- Key phrase: better aesthetics, diversity, and robustness of generated designs than previous generative design methods
- Claimed speed-up: None (No runtime of TO or of the GAN is compared. Only BEGAN training time is given (about 3 h on four GTX 1080 GPUs, Sec. 6.1.2). Not derivable.)

- **R1 = partial** [R1-loose] — Sec. 7.1, Figs. 13-14, Sec. 4.2 and Table 3: the diversity comparison is qualitative and not budget-matched. The framework runs TO for 658 market references × 25 condition pairs [derived: up to 16,450 runs] and 128 GAN references × 25 [derived: up to 3,200 runs], plus about 3 h of BEGAN training (Sec. 6.1.2). The TO-only baseline shows 5 runs without references (Fig. 13) and 12 selected results from 4 TO references (Fig. 14) [counted from the figure]; the number of baseline runs and the stopping tolerance used are not stated. No diversity metric is computed for the baseline.
- **R2 = pass** [R2-none-established] — Sec. 4.1-4.2 and 7.1: the classical engine is the authors' three-field SIMP code (OC, density filter, Heaviside projection) built on the 99- and 88-line MATLAB codes, the same engine used inside the framework, on 128×128 elements. The TO-only baseline varies only the force ratio (5 levels) from a uniform start; the authors report that it does not converge for two force ratios (Fig. 13a-b) and that reusing TO outputs as references gives similar designs (Fig. 14). A broader classical exploration (varying supports, volume fraction or initial designs) is not tried [inferred]. No runtimes exist, so markers (a)-(e) cannot apply. Unsure, so pass.
- **R3 = na** [R3-na-no-speed-claim] — Quality stratum; no speed or cost claim against TO. For C3: BEGAN training about 3 h on four GTX 1080 GPUs (Sec. 6.1.2); TO run counts as derived under R1; TO run times are not reported.
- **R4 = partial** [R4-no-failure-rate] — All final designs are TO outputs, so their compliance and cost come from FE-based optimization (Fig. 11 for 2,004 designs; Table 2). But the claimed advantage (aesthetics, diversity) is judged from images: pixel-wise L1 filtering (threshold 10^3, Sec. 3) and visual examples (Figs. 7, 10, 13-14); aesthetics is assumed from market designs, not measured (Sec. 3, Stage 2). Rejection counts are not reported: neither the number of GAN samples before Stage-6 filtering nor any non-converged TO runs inside the framework. Fig. 14 states its selection rule (the most different results); Fig. 10 does not. A strict reading (image metric only) gives fail.

- Baseline: {"classical_method": "Three-field SIMP compliance minimization with OC updates, density filter and Heaviside projection (Sec. 4.1). Classical baseline for the claim: TO without reference designs at 5 force ratios (Fig. 13) and iterative TO-only exploration that reuses TO results as references (Fig. 14)", "implementation": "authors' MATLAB code built on the 99- and 88-line educational codes (Sec. 4.1.1, 4.2)", "solver": "not stated", "hardware_classical": "not stated (TO runs executed in parallel, Sec. 6.1.1)", "hardware_ml": "four GTX 1080 GPUs for BEGAN training (Sec. 6.1.2)", "problem_size": "128×128 elements; 2D wheel with a non-design rim and a fixed hub (Sec. 4.2)", "classical_iterations": "not stated; convergence when the design change falls below a tolerance described as typically 0.01 (Eq. 7); the value used is not stated", "classical_time": "not stated", "ml_time": "not stated",

## P00235 (decision order 416; provisional top-up 19) — Physics-Informed Transformer for Real-Time High-Fidelity Topology Optimization (2026)

- Link: https://arxiv.org/abs/2604.03522
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text; primary record of the study; the earlier version P00034 = arXiv 2509.05800 is the duplicate)); stratum: **speed**
- Primary outcome (Conclusion (Sec. 6, para. 2), quantified only in Sec. 5.5 (paragraph after Table 7) for the dynamic case, with accuracy in Table 7. The abstract is qualitative. If the verifier reads the conclusion as qualitative, §5.1 rule 4 selects the same Sec. 5.5 comparison over the Sec. 5.1 static compliance-error tables, because the abstract and conclusion stress real-time generation and cost reduction): Once trained, the transformer generates a dynamic-load design in about 1.26 s (0.36 s preloaded) versus about 8900 s for classical SIMP-based dynamic TO (more than 1000×), with 4.81% mean compliance error and 48.0% floating material.
- Key phrase: reducing inference time by multiple orders of magnitude compared to classical methods
- Claimed speed-up: 7063 (Stated in Sec. 5.5 as more than three orders of magnitude. Derived: 8900 s ÷ 1.26 s (full pipeline: model loading, initial FEA, forward pass) = 7,063; with the model preloaded 8900 ÷ 0.36 = 24,722. The classical time is an approximate figure; neither side's hardware is stated. No static-case timing appears in this version.)

- **R1 = fail** [R1-unmatched] — Sec. 5.5 and Table 7: about 1.26 s of inference is set against complete SIMP-based dynamic optimizations (about 8900 s), while the dynamic outputs are measurably worse: mean CE 4.81% (samples above 100% excluded, count not given), 16.6% of samples above 30% CE, VFE 4.38%, load discrepancy 9.20%, floating material 48.0%. No matching at equal quality or equal time is attempted, and the classical stopping rule and settings are not stated. Alternative: partial if the 4.81% is read as the method's reported error.
- **R2 = partial** [R2-hardware-unjustified; R2-inefficient-impl [inferred]] — Secs. 2.2, 4.4, 5.5: implementation, solver, time integration, time-step and iteration counts, stopping rule and hardware are stated for neither the classical dynamic TO nor the transformer, and the classical time is approximate. (b) is not observed (no baseline figure in the abstract); (c) does not apply (64×64, ≈8.5×10³ DOFs [derived]); (d) and (e) are not derivable. The earlier version of this study (P00034, arXiv 2509.05800 v2 Sec. 5) timed its static SIMP at 66 s per 64×64 run; the project's provisional 150-iteration 64² CPU runs took 0.73-13.4 s (figures/data/baseline_timings.csv; cross-hardware), so the authors' classical code looks slow [inferred]. That static figure is absent from this version. Alternative: pass (R2-none-established) if only this version's text is weighed (unsure → pass).
- **R3 = fail** [R3-no-cost] — Sec. 5 and 5.5: neither training cost (800,000 iterations per model, plus fine-tuning) nor data-generation cost (30,000 static and about 6,000 dynamic SIMP runs, Sec. 4.1, 4.4) is reported, and no break-even is given. The dynamic data alone imply about 5.34×10^7 s of classical optimization at the stated 8900 s per run [derived].
- **R4 = pass** [R4-verified [FE inferred]] — Sec. 5: compliance error is computed for the predicted topologies against the ground truth on a fixed 500-sample validation subset, which requires an FE analysis of each prediction [inferred; the evaluator is not described]. Volume error, load discrepancy and floating-material share are reported, and failures are counted as the share above 30% CE (Tables 3, 4, 7). Caveat: the mean CE excludes samples above 100% without giving their number; a verifier who weighs this may choose partial (R4-filtered-outliers).

- Baseline: {"classical_method": "SIMP-based dynamic topology optimization with time-domain dynamic compliance and MMA (Sec. 2.2), the generator of the dynamic dataset (Sec. 4.4); static data from SIMP (Sec. 4.1). Time integrator, time-step count, damping values, filter, penalty and stopping rule are not stated", "implementation": "not stated (the 88-line MATLAB paper is listed in the references but not cited in the text [inferred from the missing backlink in the HTML reference list])", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "64×64 elements (Sec. 4.1) [≈8.5×10³ DOFs, derived]; the dynamic grid is not stated separately [64×64 inferred from the model input]", "classical_iterations": "not stated", "classical_time": "about 8900 s per dynamic optimization, given as an approximate figure (Sec. 5.5); no static SIMP time in this version", "ml

## P00239 (decision order 424; provisional pilot 13) — TopoCtrl: Post-Optimization Topology Editing Toward Target Structural Characteristics (2026)

- Link: https://arxiv.org/abs/2603.26926
- Access: full_text; inclusion: **include** (I-QUALITY); stratum: **quality**
- Primary outcome (Section 4.2, Table 2 (first quantitative classical comparison; abstract, conclusion and introduction compare only qualitatively)): Across 100 OAT test topologies, best-of-64 TopoCtrl edits reached 83.84–99.50% of the target characteristic ranges, versus 16.94–56.00% for re-running topology optimization with seven filter radii (Table 2).
- Key phrase: broader reachable characteristic coverage than the benchmark based on varying the filter radius
- Claimed speed-up: None (No classical runtime is reported. Only TopoCtrl inference (about 0.5 s per sample) and regressor training (about 3 min per characteristic) are given (Sec. 4). Not derivable.)

- **R1 = partial** [R1-loose] — Table 2 and Sec. 4.2: TopoCtrl best-of-N (N = 2-64 samples per topology-target pair, 16 target settings) vs 7 TO reruns per topology with filter radius 1.5-12. Volume is matched (VFE 0.03-0.10% vs 0.21% at best-of-64). Structural performance is not matched: TopoCtrl failure rates (compliance above 2× the original) are 4.67-16.00% at best-of-64, the BM failure rate is not reported, and compliance values are not tabulated. Neither the compute budget nor the TO stopping rule is stated.
- **R2 = na** [R2-na-quality-only] — Primary outcome is controllability coverage only; no classical runtime is reported and no speed claim is quantified, so the efficiency criteria (a)-(e) do not apply.
- **R3 = na** [R3-na-no-speed-claim] — No quantified speed claim against a classical method. For C3: regressor training (about 3 min per characteristic) and inference (about 0.5 s per sample) are reported (Sec. 4); OAT pretraining and OAT dataset-generation costs are not reported.
- **R4 = pass** [R4-verified] — Sec. 4.2 and Table 2: characteristics are recomputed on the decoded topologies with the same medial-axis evaluator (not the regressor); failure rate (compliance above 2× ground truth, following the OAT protocol; FE-based [inferred]) and VFE are reported for every N; the best-of-N selection rule is stated. Qualitative figures show selected examples, but the quantitative results cover all 100 test topologies.

- Baseline: {"classical_method": "Re-running the conventional TO solver that generated the OAT dataset on each test problem with the filter radius varied from 1.5 to 12, 7 reruns per topology (Sec. 4.2, Fig. 6); the TO formulation is not described in this article", "implementation": "not stated", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "PC with an RTX Pro 6000 GPU, 96 GB VRAM (Sec. 4)", "problem_size": "OAT test-set problems of varying domain size and aspect ratio; grid resolution not stated in this article; 100 test topologies (Sec. 4)", "classical_iterations": "not stated", "classical_time": "not stated", "ml_time": "about 0.5 s per sample on average; 64 samples per topology-target pair (Sec. 4)", "training_time": "about 3 min per characteristic regressor (Sec. 4); OAT pretraining cost not stated", "data_generation_cost": "not stated; regressors trained on a 150K

## P00002 (decision order 432; provisional pilot 1) — Machine-learning-assisted multiscale topology optimization of functionally graded superimposed lattice structures (2026)

- **FLAG — FT-NOBASELINE candidate: Listed in the PROTOCOL §11 no-baseline clarification. Cost claim against online homogenization; no classical run or timing.**
- Link: https://arxiv.org/abs/2608.28513
- Access: full_text; inclusion: **include** (I-SPEED); stratum: **speed**
- Primary outcome (abstract, sentences 1 and 10; restated in Sec. 4.4 para 1 and Sec. 5 para 2): Two offline-trained networks, one for stiffness and one for density, stand in for unit-cell homogenization at every MMA lattice iteration, framed as removing the homogenization cost that limits graded-lattice multiscale TO; nothing is timed or run classically.
- Key phrase: The trained stiffness and density surrogates replace repeated online homogenization
- Claimed speed-up: None (No times, FE-solve counts or speed-up factors are reported anywhere (full text read, incl. Appendix A).)

- **R1 = fail** [R1-no-quality-comparison] — Abstract, Sec. 4.4, Sec. 5: the cost-avoidance claim against online homogenization has no design-quality comparison with any classical multiscale result. Sec. 4.4 leaves for future work any check of the final design by direct homogenization.
- **R2 = na** [R2-no-classical-run] — Full text: no classical baseline is executed or timed. The comparator appears only as the avoided cost (abstract sentence 1; Sec. 1 para 3), so solver efficiency and hardware cannot be judged. [judgment] pass would also be defensible.
- **R3 = partial** [R3-no-amortization] — Sec. 2.3-2.4, Table 1: offline effort is given only as counts (1,926 stiffness and 1,500 density samples; 50,000 and 500 epochs). No data-generation or training time and no break-even against the online homogenizations avoided. [judgment] fail is arguable if counts are not accepted as cost.
- **R4 = fail** [R4-surrogate-predicted] — Sec. 4.2-4.4, Figs. 13-14: compliance and relative density of the returned lattice design come from the NN surrogates inside the FE model. No direct homogenization, Monte Carlo density check or full-lattice FE of the final design. Sec. 4.4 calls the fields approximate (relative L2 error of the stiffness factors 9.2 %, and 13.0 % for G33; Sec. 2.3).

- Baseline: {"classical_method": "Implicit comparator only: multiscale lattice optimization with repeated online computational homogenization, never run. The pipeline itself uses SIMP with OC and a sensitivity filter for the macroscale stage (Sec. 3, Table 2) and MMA with the NN surrogates for the lattice stage (Sec. 4.2).", "implementation": "No classical baseline implementation. Surrogates in Julia/Flux (Sec. 2.3); training data from an in-house homogenization code with Gmsh meshes and Abaqus cubic Euler-Bernoulli beam elements (Sec. 2.2); MMA from an open-source implementation, ref. [40] (Sec. 4.2).", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "3D MBB beam, domain 20 × 5 × 5, 60 × 15 × 15 = 13,500 first-order hexahedral elements (Sec. 4.1)", "classical_iterations": "No classical run. Pipeline stopping rules: SIMP stage stops on windowe

## P00125 (decision order 440; provisional top-up 32) — An Adaptive and Scalable ANN-based Model-Order-Reduction Method for Large-Scale TO Designs (2022)

- Link: https://arxiv.org/abs/2203.10515
- Access: full_text; inclusion: **include** (I-SPEED); stratum: **speed**
- Primary outcome (Sec. 4.2, Table 5 and Fig. 17 (pp. 18-19); first quantitative classical comparison, since the abstract, conclusion and introduction are qualitative): For the 512×512 BESO cantilever, one MapNet-based iteration (coarse 32×32 FE plus fine-field mapping) takes about 2 s versus about 600 s for fine-mesh FEM-based TO, a 300-fold per-iteration cut, with equal final compliance (0.026).
- Key phrase: a 300-times reduction in the computational time is achieved
- Claimed speed-up: 300 (Stated per iteration (Sec. 4.2) and derivable from Table 5: ~600 s (FEM-TO, 512×512) ÷ ~2 s (MapNet-TO: 0.13 s coarse FEM + 0.92 s MapNet with fragmentation and defragmentation + ~1 s rest of the optimization) = 300. Excludes data generation (first 60 FEM-TO iterations) and MapNet training. Bridge (Table 6): ~750 s vs ~3 s per iteration (~250×) and 1.5×10^5 s vs 6×10^2 s per run, both assuming 200 iterations.)

- **R1 = partial** [R1-loose] — Table 5 and Fig. 17: the per-iteration comparison is paired with equal final compliance (0.026 vs 0.026) under the same volume constraint 0.4, but achieved volumes are not reported, the BESO convergence criterion is not stated, the MapNet-TO iteration count is not reported (Table 6 assumes 200 for both), and it is not stated whether the MapNet-TO compliance was re-evaluated on the fine mesh. [judgment] pass is the lenient reading, since the printed compliances match.
- **R2 = partial** [R2-inefficient-implementation [inferred]; R2(e) re-test candidate] — Sec. 4.2, Table 5: fine-mesh BESO at 512×512 (~5.3×10^5 DOFs [derived]) spends ~600 s per iteration in the FE solve with a SciPy sparse solver on a 16-core Xeon E5-2687W v2. Both methods ran on that CPU, so (c) does not apply; (b) and (d) are not established. The per-iteration time is derivable, but (e) needs a strong-baseline time at 512×512 on a comparable CPU, which the article cannot supply. About 600 s for one 2D solve of this size looks slow for a sparse direct solver [inferred], so partial.
- **R3 = partial** [R3-no-training-cost] — Sec. 4.1.1, 4.2: data generation is given as the first 60 fine-mesh FEM-TO iterations [derived ≈3.6×10^4 s at ~600 s each], and the text argues that the saving already pays off within one TO run; training time is not reported (1000 ADAM steps only) and no break-even is computed. New MapNets are trained for the SIMP and thermal problems (Sec. 4.4-4.5).
- **R4 = partial** [R4-no-constraint-report] — Figs. 17-24: one design per problem, all problems shown, with final compliance for both methods. Whether the MapNet-TO compliance comes from a fine-mesh FE re-analysis is not stated [if it is the MapNet-predicted value, R4 = fail, R4-surrogate-predicted]. Achieved volume fractions are not reported and no failure cases are discussed.

- Baseline: {"classical_method": "Conventional FEM-based BESO compliance minimization on the 512×512 fine mesh, volume fraction 0.4, square cantilever with a distributed load at the upper right (Sec. 2, 4.1-4.2); SIMP structural and thermal variants (Sec. 4.4-4.5) are compared without timing", "implementation": "Python; FE solved with a SciPy sparse linear solver (Sec. 4.2); the BESO and SIMP codes are not published (code on request, Data Availability)", "solver": "SciPy sparse linear solver (Sec. 4.2); direct or iterative not stated [SciPy's default spsolve is a direct SuperLU solver; recalled, not verified in-session]", "hardware_classical": "Intel Xeon E5-2687W v2 CPU (3.40 GHz), 16 cores; the Table 5 times were measured on it (Sec. 4.2)", "hardware_ml": "same CPU (Sec. 4.2); no GPU mentioned", "problem_size": "512×512 fine mesh and 32×32 coarse mesh (Sec. 4.1-4.2) [derived: 526,338 fine-mesh DOF

## P00100 (decision order 467; provisional pilot 4) — DMF-TONN: Direct Mesh-free Topology Optimization using Neural Networks (2023)

- **FLAG — note: Reports the ML method about 4x slower than SIMP: a negative-direction record, relevant to C4.**
- Link: https://arxiv.org/abs/2305.04107
- Access: full_text; inclusion: **include** (I-QUALITY); stratum: **speed**
- Primary outcome (Sec. 4.1, Table 1: the first quantitative comparison with a classical method; the abstract, introduction and conclusion compare only qualitatively): On a 2D cantilever at volume fraction 0.5, DMF-TONN reaches lower FE-evaluated compliance than the 88-line SIMP code (binary 2.52×10^-4 vs 2.66×10^-4) but needs 277 s versus 69 s on the same machine.
- Key phrase: though our method is slower than SIMP
- Claimed speed-up: 0.249 (Derived from Table 1: SIMP 69 s ÷ DMF-TONN 277 s = 0.249, so the ML method is about 4.0 times slower. The article claims no speed-up over SIMP.)

- **R1 = pass** [none] — Sec. 4.1, Table 1: run time and FE-evaluated compliance are reported side by side at equal volume fraction (0.50). The ML method is slower and claims no speed advantage over SIMP, so no speed claim needs quality matching. Its compliance advantage comes with about 4 times the SIMP run time.
- **R2 = pass** [none] — Sec. 3.3, 4.1: SIMP uses the published 88-line code at its default stopping rule on the same machine. No marker is established: the 2D grid size and the device per method are not stated, and the largest 3D case has 97,200 DOF, below 10^5. A stronger baseline would only widen the reported slow-down.
- **R3 = na** [R3-per-problem] — Sec. 3: per-problem neural reparameterization with a PINN; no offline data or training. Its cost sits inside the reported run times.
- **R4 = partial** [R4-no-failure-rate] — Sec. 4 intro, Tables 1-3: the compliance of every returned design is recomputed by FEA, and the volume fraction is reported. Failures are not counted: non-convergence below volume fraction 0.2 (Sec. 5) and a dangling feature (Fig. 14c, Sec. 4.6) are described only qualitatively.

- Baseline: {"classical_method": "SIMP. 2D: the 88-line code of Andreassen et al. 2011 (ref. [34]) at its default convergence criterion, density filter radius 1.5 elements (Sec. 4, 4.1). 3D: Top3D of Liu and Tovar 2014 (ref. [35]).", "implementation": "MATLAB educational codes (88-line 2D code; Top3D for 3D), per the titles of refs. [34] and [35]; DMF-TONN in TensorFlow (Sec. 3.2.2)", "solver": "not stated", "hardware_classical": "not stated per method; all experiments ran on one machine: Intel Core i7-12700 2.10 GHz, 16 GB RAM, Nvidia GeForce RTX 3060 (Sec. 3.3)", "hardware_ml": "the same single machine (Sec. 3.3); the device used by each method is not stated", "problem_size": "2D cantilever: grid not stated in the text (Tables 1-2). 3D: 40x20x8 grid with 19,200 DOF (Sec. 4.2); 60x20x8 with 28,800 DOF and 90x30x12 with 97,200 DOF (Table 3). DMF-TONN: batch of 6,000 points, 4,096 trainable weights p

## P00518 (decision order 468; provisional top-up 21) — Machine learning-enabled inverse design of bimaterial thermoelastic lattice metamaterials (2026)

- Link: https://arxiv.org/abs/2602.20173
- Access: full_text; inclusion: **exclude** (FT-NOBASELINE; prefill label: FT-NOBASELINE); stratum: **none**
- Primary outcome (Abstract; Sections 3.3-3.7, Tables 3-6 and S.2-S.3; Section 4): Not coded (excluded). Headline: fully connected forward and inverse ANNs trained on 10^5 FE-homogenized hybrid-honeycomb designs return lattice parameters whose properties match targets within 0.15-6.5% relative error in the worked examples; no classical optimizer is run or timed.
- Key phrase: 
- Claimed speed-up: None (Not coded (excluded at full text). No runtime of any method is reported; efficiency is asserted without timing (Abstract; Sections 3.5 and 3.7; Section 4).)

- **R1 = na** [excluded] — excluded at full text (FT-NOBASELINE)
- **R2 = na** [excluded] — excluded at full text (FT-NOBASELINE)
- **R3 = na** [excluded] — excluded at full text (FT-NOBASELINE)
- **R4 = na** [excluded] — excluded at full text (FT-NOBASELINE)

- Baseline: {}

## P00327 (decision order 475; provisional pilot 16) — Data-driven topology design based on principal component analysis for 3D structural design problems (2025)

- Link: https://arxiv.org/abs/2409.01607
- Access: full_text; inclusion: **exclude** (FT-MLONLY; prefill label: FT-ML-only); stratum: **none**
- Primary outcome (Sec. 4.2 Comparison (Figs. 5-7); Sec. 5 Conclusions; Abstract): Excluded at full text. The only method-versus-method comparison is PCA-based DDTD against non-PCA DDTD, an ML baseline. The other results compare DDTD outputs with the method's own initial designs. No classical optimizer is run on the target problems.
- Key phrase: 
- Claimed speed-up: None (No speed claim against a classical method. The version of record adds DDTD-only per-iteration times.)

- **R1 = na** [na] — excluded at full text
- **R2 = na** [na] — excluded at full text
- **R3 = na** [na] — excluded at full text
- **R4 = na** [na] — excluded at full text

- Baseline: {}

## P00371 (decision order 478; provisional top-up 33) — Aligning Optimization Trajectories with Diffusion Models for Constrained Design Generation (2023)

- Link: https://arxiv.org/abs/2305.18470
- Access: full_text; inclusion: **include** (I-QUALITY); stratum: **quality**
- Primary outcome (Sec. 4 (Evaluation; In-Distribution Constraints), Table 3, p. 9 (first quantitative comparison with a classical method; the abstract, conclusion and introduction compare quantitatively only with deep generative models)): On the in-distribution 64×64 test set, DOM with trajectory alignment (100 sampling steps) yields designs with 4.44% mean (0.74% median) compliance error versus the SIMP-optimized designs, 1.52% volume-fraction error and 6.72% floating material.
- Key phrase: as measured by compliance error (CE) wrt the optimized SIMP solution
- Claimed speed-up: None (Primary outcome is quality only. Derivable for the alternative in App. B.2, Table 8 (100 steps or iterations each): SIMP 18.12 s vs DOM 2.35 s at 64×64 [derived 7.7×] and 316.02 s vs 8.09 s at 256×256 [derived 39.1×]; SIMP ran on CPU and the diffusion models on GPU (caption); the 256×256 models were trained for only 10k steps (App. B.2).)

- **R1 = partial** [R1-loose] — Table 3 and Sec. 4 Evaluation: generated designs are compared with SIMP-optimized designs for the same loads, BCs and prescribed volume fraction, but volume is only approximately matched (VFE 1.52%), generated configurations with high compliance are filtered out before averaging (threshold and count not stated), and budgets are not matched: DOM uses 100 sampling steps (2.35 s), while the iteration count and time of the SIMP reference runs are not stated.
- **R2 = pass** [R2-none-established] — Sec. 4 Dataset: the SIMP references come from an existing dataset whose SIMP settings are not stated in this article; nothing indicates a weakened classical reference. Quality stratum; unsure, so pass. For the Table 8 alternative, SIMP runs on CPU and the diffusion models on GPU at 256×256 [derived ≈1.3×10^5 DOFs]; the caption notes the device difference but does not justify it, so R2(c) would apply if Table 8 were primary.
- **R3 = na** [R3-na-quality-stratum] — Quality-stratum primary outcome. For C3: 200k training steps on 30k optimized 64×64 topologies plus 150K intermediate SIMP iterates (Sec. 4 Setup; Table 11); training time, hardware and data-generation cost are not reported.
- **R4 = partial** [R4-filtered-outliers] — Sec. 4 Evaluation, Tables 3-5: compliance error against the SIMP optimum, volume-fraction error and floating material are reported, and Table 4 adds unsolvable and load-disrespect rates; compliance of generated designs presumably from FE analysis [inferred; procedure not described]. High-compliance samples are filtered out before averaging with no threshold or count, and Fig. 12 shows examples labelled as good performers without a selection rule.

- Baseline: {"classical_method": "SIMP-optimized reference topologies from the dataset attributed to [66, 62] (TopoDiff), used as ground truth for compliance error (Sec. 4 Dataset and Evaluation); App. B.2 also runs SIMP for 100 iterations at 64×64 and 256×256 for timing (Table 8); SIMP is also used for 5 or 10 refinement steps (Table 5)", "implementation": "not stated (neither for the reference designs nor for the Table 8 timing run)", "solver": "not stated", "hardware_classical": "CPU, model not stated (Table 8 caption)", "hardware_ml": "GPU, model not stated (Table 8 caption)", "problem_size": "64×64 for all main results (Sec. 4 Setup) [derived ≈8.5×10^3 DOFs]; 256×256 only in Table 8 [derived ≈1.3×10^5 DOFs]; both assume 4-node elements", "classical_iterations": "not stated for the reference designs; 100 iterations in Table 8; 5 or 10 SIMP refinement steps in Table 5", "classical_time": "18.12 s

## P00182 (decision order 495; provisional pilot 9) — A novel topology design approach using an integrated deep learning network architecture (2018)

- Link: https://arxiv.org/abs/1808.02334
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-UNCLEAR; full text holds only a qualitative, quality-only comparison with SIMP and no timing)); stratum: **quality**
- Primary outcome (conclusion (Section 5, p. 13); supporting comparison in Section 4, p. 11 and Table 1, p. 12. No quantitative comparison exists anywhere, so rule 5.1(3) applies): The authors conclude that GAN-generated cantilever structures, mapped to settings by a CNN, agree well with SIMP structures computed at those settings, so the GAN can produce sub-optimal topologies after training on 3024 samples.
- Key phrase: With the good agreement of the GAN results against the conventional algorithm
- Claimed speed-up: None (No timing is reported for either method anywhere in the article (full text checked).)

- **R1 = na** [R1-na-quality-stratum] — The primary outcome is a qualitative, quality-only comparison (Conclusion p. 13; Section 4 p. 11). No run time of either method appears anywhere in the article, so there is no speed comparison to match.
- **R2 = na** [R2-na-quality-stratum] — No speed comparison. For the record: SIMP implementation, solver, iteration count and hardware are not stated (Sections 2–3).
- **R3 = na** [R3-na-no-speed-claim] — No quantified speed claim. For the record: the 3024-sample SIMP dataset (augmented to 6048 for the CNN) has no stated generation or training cost (Section 3, pp. 5, 9).
- **R4 = fail** [R4-selected-examples] — Section 4 p. 11 and Table 1 p. 12: four post-processed GAN structures (0.5 threshold plus Gaussian filter) are compared by eye with SIMP structures run at the CNN-predicted settings; the selection rule is not stated. No FE analysis, compliance or measured volume fraction of any GAN output is reported.

- Baseline: {"classical_method": "SIMP compliance minimization, cantilever loaded at the mid-point of the free end (Sections 2–3)", "implementation": "not stated (a conventional SIMP code; Section 2 cites the 99-line and 88-line MATLAB papers, refs 14, 15)", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated (Keras with TensorFlow backend, Python 3.5; Section 3)", "problem_size": "120×120 (Section 3, Dataset, p. 9)", "classical_iterations": "not stated", "classical_time": "not stated", "ml_time": "not stated", "training_time": "not stated", "data_generation_cost": "not stated; 3024 SIMP samples over volume fraction 0.3–0.8, penalty 2–4, filter radius 1.5–3, augmented with noise to 6048 for the CNN (Section 3, pp. 5, 9)", "quality_metric": "visual comparison of post-processed GAN structures with SIMP structures at CNN-predicted settings (Section 4, Table 1)", "qual

## P00020 (decision order 499; provisional top-up 34) — Learning Gradient Flow: Using Equation Discovery to Accelerate Engineering Optimization (2026)

- Link: https://arxiv.org/abs/2602.13513
- Access: full_text; inclusion: **include** (I-SPEED); stratum: **speed**
- Primary outcome (Conclusion (Sec. 5 para 1) and Table 6 (first quantitative comparison; the abstract is qualitative); TO details in Sec. 4.2, Table 2 and Figs. 4-5): In the 3D compliance TO example, the learned gradient-flow surrogate replaces 50 of every 70 gradient-descent steps (250% acceleration, 3.5× fewer objective/gradient evaluations) over 900 epochs, and the design is shown to agree with plain gradient descent.
- Key phrase: reduced the number of gradient evaluations by factors ranging from 33% up to 250%
- Claimed speed-up: 3.5 (Evaluation-count ratio, not time. Acceleration is defined as 100×(M/K−1) (Sec. 4.1, Table 6); for TO, K = 20 and M = 70 give 250%, i.e. 70/20 = 3.5× fewer objective/gradient evaluations than gradient descent over the same 900 epochs [derived] (Sec. 4.2). No wall-clock time or hardware is reported; the cost of the rank-2 truncated SVD, the least-squares fit and the dopri5 integration is argued to be minor but not measured (Sec. 4.2).)

- **R1 = pass** [R1-matched] — Sec. 4.2, Figs. 4-5: surrogate-accelerated and plain gradient descent run the same number of epochs from the same start; the objective curves overlap and the densities agree (2.0×10^-4 relative difference at 500 epochs for the 100% case; graphical agreement for the 250% case), so the evaluation saving is claimed at matched design. [judgment] partial is defensible because the 250% case has no numeric quality check, volume is not reported, and the surrogate overhead is outside the evaluation-count proxy.
- **R2 = partial** [R2-inefficient-baseline-optimizer [judgment]] — Sec. 4.2, Table 2, Fig. 5: the classical comparator is fixed-step plain gradient descent on a tanh-parametrized, penalty-constrained formulation, not a standard TO optimizer such as OC or MMA. The authors note that this parametrization strongly delays convergence to 0/1 densities, and Fig. 5 still shows intermediate densities after 900 epochs. Solver and hardware are not stated. Markers (a)-(e) are not established; whether a 3.5× evaluation saving would hold against OC or MMA is untested [inferred risk].
- **R3 = na** [R3-na-per-problem-learning] — The surrogate is fitted online from the current run's own iterates, with no offline training or dataset (Sec. 3.1, 3.4); per protocol its cost sits inside R1/R2. The refit cost (truncated SVD and least squares every 70 epochs) is described but not timed (Sec. 4.2).
- **R4 = partial** [R4-no-constraint-report] — Figs. 4-5: the objective of the accelerated run is plotted over all epochs and overlaps gradient descent, presumably from FE evaluation of the returned densities [inferred]; the density difference itself is a field-similarity metric. The volume (enforced only through a penalty) and the compliance of the final design are not reported. One run per setting; no failure cases for TO.

- Baseline: {"classical_method": "Plain gradient descent with a fixed learning rate of 1 on an unconstrained SIMP compliance formulation: tanh density parametrization, quadratic volume penalty (V0 = 0.3), penalty exponent p = 4, no density filter mentioned (Sec. 4.2, Eqs. 22-29, Table 2); the same optimizer with and without the learned surrogate", "implementation": "PyTorch-based LGF optimizer (Sec. 1 contributions); the FE code is not described beyond solving the sparse equilibrium system and assembling element sensitivities (Sec. 4.2)", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "3D: quarter of a unit cube by symmetry, 13,824 8-node hexahedra (24 per side of the computational domain), 46,875 DOFs before boundary conditions (Sec. 4.2)", "classical_iterations": "fixed epoch counts, no convergence criterion: 500 epochs for the 100% case (T

## P00015 (decision order 500; provisional pilot 2) — Multiscale topology optimization of compressible and nearly incompressible anisotropic hyperelastic structures using physics-augmented neural networks (2026)

- **FLAG — FT-NOBASELINE candidate: Listed in the clarification. FE2 cost claim; no FE2 run, timing or cost figure.**
- Link: https://arxiv.org/abs/2604.06519
- Access: full_text; inclusion: **include** (I-SPEED); stratum: **speed**
- Primary outcome (abstract, penultimate sentence (AM p. 2); restated in Sec. 6 para 3 (AM p. 56)): Using physics-augmented neural-network constitutive surrogates in place of microscale RVE solves is said to cut computational cost markedly relative to classical FE2 concurrent multiscale TO; no FE2 run, timing or cost figure is reported.
- Key phrase: significantly reducing computational cost compared to classical FE2 approaches
- Claimed speed-up: None (No times, solve counts or speed-up factors are reported (arXiv v1 read in full; AM searched for timing and hardware terms).)

- **R1 = fail** [R1-no-quality-comparison] — Abstract (AM p. 2) and Sec. 6 (AM p. 56): the FE2 cost claim has no design-quality comparison with FE2 or with any directly homogenized design. App. B compares single-scale synthetic cases, qualitatively only.
- **R2 = na** [R2-no-classical-run] — Full text: FE2 is never run or timed; its cost appears only as a description (Sec. 1, AM p. 3; Sec. 3), so baseline efficiency and hardware cannot be judged. [judgment] pass would also be defensible.
- **R3 = partial** [R3-no-data-cost] — Sec. 3 (AM p. 20): training is given only as a 10^5-epoch budget. Data-generation effort is sized for one of three surrogates, and only per phi level (Sec. 5.1.2). No times, no break-even. [judgment] fail is arguable because no cost is given in time or compute units.
- **R4 = fail** [R4-surrogate-predicted] — Sec. 5, Figs. 3-9: every multiscale compliance value comes from FE with the PANN surrogate as the material law. The returned designs get no FE2 or direct-homogenization check, and volume and inclusion-mass constraint values are not reported. App. B.2 (AM p. 67) attributes small compliance-history differences to surrogate error building up during optimization. [judgment] partial is the lenient reading if FE with a learned material law counts as FE-verified.

- Baseline: {"classical_method": "Implicit comparator only: classical FE2 concurrent multiscale TO, never run. The optimization itself is density-based SIMP with a linear filter, Heaviside projection and continuation, solved with MMA (Sec. 4, 4.3.2, 5).", "implementation": "No FE2 baseline implemented. ISNN surrogates in PyTorch (Sec. 3, AM p. 20); the TO code is not named.", "solver": "No classical baseline. The method's Newton linear systems use a direct sparse solver (Sec. 5, AM p. 40).", "hardware_classical": "not stated", "hardware_ml": "not stated; TACC is acknowledged for computing resources (Acknowledgments)", "problem_size": "Simply supported beam: 50 × 3 × 15 mesh (Sec. 5.1.1, AM p. 43); 3D cantilever with cubic RVE: 40 × 20 × 20 mesh (Sec. 5.1.2, AM p. 50); nearly incompressible cantilever: 60 × 15 × 15 mesh (Sec. 5.2, AM p. 53); mesh of the Sec. 5.1.1 cantilever not stated", "classical_i

## P00244 (decision order 513; provisional top-up 1) — Sketch2Topo: Diffusion-Model-Based Topology Optimization Using Hand-Drawn Inputs as Condition Constraints (2026)

- Link: https://arxiv.org/abs/2603.18960
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-UNCLEAR; the only quantitative classical comparison is on design quality)); stratum: **quality**
- Primary outcome (Section 4.1, Table 1 (first quantitative classical comparison; abstract, introduction and conclusion hold none)): On a single load case with a 0.2 volume-fraction target, Sketch2Topo's three generation modes (10 samples each) gave higher mean compliance than the SIMP result (67.96-96.49 vs 63.40) and overshot the volume target (21.90-26.34% vs 20%).
- Key phrase: the structures generated by Sketch2Topo exhibit higher minimum compliance
- Claimed speed-up: None (No runtime of any method is reported anywhere in the article. The speed argument is only motivation: the abstract says classical TO has significant computational and time costs, and Section 1 says classical runs can take hours (citing Aage et al. 2017). Not derivable.)

- **R1 = partial** [R1-loose] — Section 4.1, Table 1: all groups share the load case, material, penalty and filter settings and a 0.2 volume target, so the comparison is on design quality only. Volume is not matched: Sketch2Topo outputs hold 21.90-26.34% material vs 20% for SIMP, which favours their compliance [inferred]. The design domains probably differ too [inferred]: the authors attribute the compliance gap to regional constraints imposed by the sketches. Ten generations per mode are compared with one SIMP run; the SIMP stopping rule and any compute budget are not stated.
- **R2 = pass** [R2-none-established] — Sections 3.2 and 4.1: the SIMP settings are given (r_min = 2.0, p = 3.0, ν = 0.3, E0 = 1, Emin = 10⁻⁹, volume fraction 0.2), but the implementation, solver, iteration count and stopping rule are not. SIMP gives the lowest compliance in Table 1 (63.40), so nothing indicates an under-converged comparator [inferred]. No runtimes exist, so markers (a)-(e) cannot apply. Unsure → pass.
- **R3 = na** [R3-na-no-speed-claim] — No speed claim: no runtime of any method is reported. For C3: the pretrained TopoDiff model is used without retraining or fine-tuning (Sections 3.1-3.2); its data-generation and training costs are not reported in this article.
- **R4 = partial** [R4-no-failure-rate] — Table 1: compliance and volume fraction are reported as mean ± std over all 10 generations per mode, and the volume overshoot is disclosed (Section 4.1). How the compliance of the generated designs was computed is not stated [FE with the listed SIMP parameters inferred]. Disconnected, floating-material or otherwise failed generations are not counted.

- Baseline: {"classical_method": "SIMP compliance minimization: the FEA group in Table 1, which the Fig. 1a caption describes as SIMP-based finite element analysis; vertical load at (0.98, 0.96), supports at (0.26, 0.0) and (0.0, 0.62), volume fraction 0.2 (Section 4.1)", "implementation": "not stated", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "not stated (coordinates are given in normalized units, Section 4.1)", "classical_iterations": "not stated", "classical_time": "not stated", "ml_time": "not stated", "training_time": "none for this work: the pretrained open-source TopoDiff model is used without retraining or fine-tuning (Sections 3.1-3.2); TopoDiff's own training cost not stated", "data_generation_cost": "none for this work; the base model's training-data cost is not stated", "quality_metric": "minimum compliance and volume fracti

## P00385 (decision order 544; provisional top-up 24) — Conceptual Design of Cellular Auxetic Systems with Passive Adaptation to Loading (2022)

- Link: https://arxiv.org/abs/2210.01659
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-SPEED; the abstract's computational-efficiency claim is qualitative and never measured, while its quantitative classical comparison, the fourfold reaction force, concerns quality only; §5.1 rule 1)); stratum: **quality**
- Primary outcome (Abstract (quantitative classical comparison, §5.1 rule 1); numbers in Section 4, Table 6): In a gripper case study, the Bayesian-optimized auxetic-cell design gives 1.65 N contact reaction force versus 0.41 N for an ANSYS compliance-minimizing TO design of equal mass (8%) and 0.85 N at 25% volume (Table 6).
- Key phrase: four times better in terms of exhibited contact reaction force
- Claimed speed-up: None (No runtime of either method is reported. The Abstract and Sec. 1.1 call the parametric-cell approach computationally efficient and TO costly, without numbers. Not derivable.)

- **R1 = partial** [R1-loose] — Table 6 and Sec. 3: the 8% TO design has the same mass as the auxetic design (Table 6 footnote), and all three designs pass through the same ANSYS validation FEM (Table 4). Matching is loose: TO minimizes compliance on the initial envelope, while the Bayesian optimization maximizes a jaw displacement ratio (Eq. 1) and may change the outer envelope through the edge offset and cell sizes (Sec. 3) [inferred: design domains may differ; Sec. 2.2 says the outer geometry is fixed, so the article is inconsistent]. The TO outputs were manually post-processed on the outer contour before validation (Sec. 4). The Bayesian optimization was stopped at 80 of 100 planned iterations (Sec. 4), and no compute budget is compared.
- **R2 = partial** [R2-inefficient-impl (general-purpose commercial TO module); comparator objective mismatch [judgment]] — Sec. 5 and Table 5: the classical comparator is ANSYS's standard TO module, a general-purpose commercial TO module (a listed partial case), minimizing compliance (at most 100 iterations, 0.1% convergence accuracy, converged in 27). Its objective differs from the gripping-force metric used in the comparison (Table 6) and from the Bayesian-optimization objective (jaw displacement ratio, Eq. 1). No mechanism-type TO formulation targeting jaw force or displacement is run [inferred to be the competent classical comparator for a gripper]. The authors note that the TO result could change with added constraints (Sec. 4). (b) does not apply: the abstract uses the equal-mass 8% design, which is the fair one; the 25% design uses about three times the material. No runtimes exist, so (a) and (c)-(e) cannot apply. A verifier who weighs the objective mismatch as decisive may choose fail.
- **R3 = na** [R3-na-no-speed-claim] — Quality stratum; the Abstract's efficiency claim is not quantified. For C3: the Bayesian optimization used 500 initial samples and was stopped after 80 one-sample iterations (Table 3, Sec. 4) [inferred: about 580 FEniCS evaluations], while TO converged in 27 iterations (Table 5); no times or hardware are reported.
- **R4 = pass** [R4-FE-verified] — Sec. 3 and 5, Tables 4 and 6: the returned auxetic design is re-analysed with a separate, higher-fidelity ANSYS validation FEM, and reaction force and peak von Mises stress are reported for all three designs, with mass fractions stated (8%, 8%, 25%). One returned design, so no failure rate applies. Satisfaction of the rib-overlap constraint g1 is not reported; unsure, so pass.

- Baseline: {"classical_method": "ANSYS standard topology optimization minimizing compliance, run at 8% (same mass as the auxetic design) and at 25% volume fraction on the initial gripper envelope, with the envelope edges and the payload as exclusion zones and a symmetry constraint (Sec. 3, Table 5, Sec. 5)", "implementation": "commercial general-purpose TO module (ANSYS, Sec. 5)", "solver": "not stated", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "not stated (2D plane-stress gripper; FEniCS with Gmsh first-order triangles for the optimization, ANSYS 8-node-dominant quadrilaterals for validation; Sec. 2.2, Table 4)", "classical_iterations": "at most 100, convergence accuracy 0.1%, converged after 27 iterations (Table 5)", "classical_time": "not stated", "ml_time": "not stated; Bayesian optimization with 500 initial samples and one new sample per iteration, 100 i

## P00512 (decision order 558; provisional top-up 14) — HGTO: A Unified Graph-Based Physics-Informed Formulation for Structural Topology Optimization (2026)

- **FLAG — R2 check: If the ~4x and ~10x high-resolution claims are taken as primary, R2(c) becomes fail: GPU against a 2-thread CPU.**
- Link: https://arxiv.org/abs/2609.15001
- Access: full_text; inclusion: **include** (I-SPEED (screened I-UNCLEAR; the first quantitative classical comparison reports run times against SIMP–OC)); stratum: **speed**
- Primary outcome (Sec. 3.2 and Table 1, pp. 10-11 (first quantitative comparison with a classical method; the Abstract and Sec. 5 compare with SIMP–OC only qualitatively, and their cost statements are against the neural baseline NTopo)): On three 120×40 planar benchmarks at volume fraction 0.5, HGTO reaches compliance within about 0.6–2.1% [derived] of SIMP–OC (all slightly higher) in 7.4–8.5 s versus 9.0–26.9 s, which the authors describe as cost of the same order.
- Key phrase: at a total cost of the same order as SIMP–OC on these small problems
- Claimed speed-up: 1.22 (Derived, not claimed: the authors state cost of the same order. Table 1 SIMP–OC ÷ HGTO time: cantilever 9.0/8.3 = 1.08, half-MBB 9.0/7.4 = 1.22, inclined load 26.9/8.5 = 3.16 (the SIMP–OC run hit its 1,000-update limit); the median, 1.22, is entered. The article's explicit speed-up claims against SIMP–OC are in the alternatives.)

- **R1 = pass** [R1-matched] — Sec. 3.1, S1.3, S2, Table 1: both methods use the same filter, projection, continuation and stopping rule, satisfy the volume constraint within 1e-7, and are scored by the same independent FE evaluator. HGTO compliance is 0.6-2.1% higher [derived], while its times are similar (8.3 vs 9.0 s and 7.4 vs 9.0 s), so the comparison sits near equal wall-clock and the authors claim only cost of the same order. The inclined-load SIMP–OC run stopped at the update limit, and its time (26.9 s) is flagged in Table 1.
- **R2 = partial** [R2-hardware-unjustified] — Sec. 3.1, S5: HGTO runs on an RTX 6000 Ada GPU while SIMP–OC is restricted to two CPU threads of a Threadripper PRO 5995WX, with no stated reason. For the primary cases (≈9.9×10³ DOFs [inferred]) R2(c) does not apply. SIMP–OC uses a sparse direct solver (S5; PARDISO per the repository docs), which is in the efficient class; (b) and (d) are not observed. Per-update SIMP–OC time is derivable only for the inclined case: 26.9 s over 1,000 updates ≈ 0.027 s per update including setup [derived], an input for an R2(e) re-test. If the verifier takes the Sec. 3.3 fourfold and tenfold claims as primary (about 1.5×10^5 and 6.2×10^5 DOFs [inferred]), R2(c) gives fail.
- **R3 = na** [R3-na-per-problem] — Sec. 3.1 and S1.3: each design is optimized from a uniform density without labeled data or offline training. S5: HGTO timings include network setup and optimization, so learning cost sits inside R1/R2.
- **R4 = pass** [R4-verified] — Sec. 3.1 and S2: the optimized physical densities of every method are passed to a common independent scikit-fem evaluator (p = 3, full quadrature). S1.3: HGTO and SIMP–OC meet the volume constraint within 1e-7, and Table S1 lists achieved NTopo volumes. Every run's convergence status is reported (all HGTO runs converge; the SIMP–OC update-limit and stagnation cases and the NTopo nonlinear failures are flagged). No post-processing is applied.

- Baseline: {"classical_method": "SIMP with optimality-criteria updates (SIMP–OC), same density filter, projection and (p, β) continuation as HGTO, move limit 0.2/max(1, β) (Sec. 3.1; S1.3)", "implementation": "Authors' own Python implementation (repository src/hgto/reference); article states only CPU mechanics with two threads (Sec. 3.1; S5). Repository docs say linear OC configurations use pypardiso-spd and nonlinear OC uses CPU SciPy mechanics (docs/reproduction.md, read 2026-09-24).", "solver": "SIMP–OC: sparse direct (article S5, for the nonlinear cases; repository docs: PARDISO for linear OC). HGTO: preconditioned CG with geometric multigrid, or smoothed-aggregation AMG with GPU V-cycles on the perforated mesh (Sec. 2.4; S5); nonlinear HGTO uses cuDSS sparse LU on the GPU (S5).", "hardware_classical": "Two CPU threads on an AMD Ryzen Threadripper PRO 5995WX (Sec. 3.1; S5)", "hardware_ml": "NVI

## P00059 (decision order 562; provisional top-up 18) — A dual physics-informed neural network for topology optimization (2024)

- Link: https://arxiv.org/abs/2410.14342
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text)); stratum: **speed**
- Primary outcome (Sec. 4.1.1, Table 1 and Fig. 7 (compliance and iterations also in Fig. 4); the first quantitative comparison with a classical method. The abstract, introduction and conclusion compare only qualitatively): On four 200×100 benchmarks, DPNN-TO took 126-164 s versus 167-251 s for 88-line SIMP with Heaviside projection (1.02-1.81× faster [derived]) and had lower compliance in 3 of 4 cases, but was slower than standard SIMP (68-113 s).
- Key phrase: better computational efficiency compared to the SIMP with the Heaviside projection filter method
- Claimed speed-up: 1.4 (Not stated as a factor. Derived from the Fig. 7 data labels (total time, s): SIMP+Heaviside ÷ DPNN-TO = 188/126 = 1.49, 167/164 = 1.02, 251/139 = 1.81, 183/139 = 1.32; median 1.40. Against standard 88-line SIMP: 79/126 = 0.63, 80/164 = 0.49, 113/139 = 0.81, 68/139 = 0.49; median 0.56, i.e. DPNN-TO is slower in all four cases. Iteration proxy (Table 1): DPNN-TO needs 38-48 density epochs vs 222-340 (SIMP) and 498-660 (SIMP+Heaviside) iterations, but each density epoch also retrains the displacement network (120 epochs after 500 initial ones per Sec. 4.1; Sec. 3.3 describes progressively fewer), so the proxy overstates the saving.)

- **R1 = partial** [R1-loose] — Table 1, Figs. 4 and 7: each method runs to its own stopping rule, and compliance is reported beside time for all four cases, but nothing is matched. DPNN-TO has lower compliance in 3 of 4 cases, yet in case (2) it is 15.7% worse than SIMP+Heaviside [derived] while only 1.02× faster (164 vs 167 s). DPNN-TO volume fractions are not reported and its compliance-evaluation method for Table 1 is not stated, so equal volume cannot be confirmed.
- **R2 = fail** [R2(b)] — Abstract vs Sec. 4.1.1 and Fig. 7: the abstract says DPNN-TO beats conventional methods in computational efficiency, but the results show standard 88-line SIMP is faster than DPNN-TO in all four cases (68-113 s vs 126-164 s); the efficiency advantage holds only against SIMP with Heaviside projection, the slower of the two classical baselines (2.1-2.7× slower than standard SIMP [derived]). The abstract's claim thus rests on the weaker baseline in the results. Other markers: (c) does not apply (about 4.1×10^4 DOFs [derived]); (d) not established; (e) pointer: 0.30-0.38 s per SIMP iteration at 200×100 [derived] needs a same-size re-test. Alternative: pass (R2-none-established) if the verifier reads (b) as requiring a named or quantified baseline in the abstract.
- **R3 = na** [R3-na-per-problem] — Sec. 3.3 and Algorithm 1: both networks are trained per problem from scratch with no dataset or offline training; their cost sits inside the reported run times (Fig. 7).
- **R4 = partial** [R4-no-constraint-report] — Table 1 and Fig. 4: compliance of the returned designs is reported, apparently from an FE re-analysis with the 88-line code [inferred from Sec. 4.3; the Table 1 procedure is not stated]. Attained volume fractions of the 2D DPNN-TO designs are not reported although the volume constraint is only a penalty, and no failed runs are counted. The L-bracket design ends at 1.67 MPa against a 1.5 MPa stress constraint, a violation the text does not flag [derived, Sec. 4.3]. If the Table 1 values come from the displacement network's energy rather than FE, the verdict becomes fail (R4-surrogate-predicted).

- Baseline: {"classical_method": "SIMP compliance minimization with the 88-line MATLAB code (ref. [56]), standard and with Heaviside projection, penalization p = 3 (Sec. 4.1, Table 1)", "implementation": "MATLAB 88-line educational code (Sec. 4.1); DPNN-TO in PyTorch (Sec. 4)", "solver": "SIMP: not stated (the published 88-line code uses a sparse direct solve [recalled, not verified in-session]). DPNN-TO has no FE solver: a displacement network minimizes the potential energy with Adam (Sec. 3.2.1, 3.3)", "hardware_classical": "not stated", "hardware_ml": "one Nvidia Quadro P2200 GPU (5 GB VRAM), stated for all numerical simulations (Sec. 4)", "problem_size": "2 m × 1 m domain, 200×100 collocation points (Sec. 4.1); the SIMP mesh is not stated [assumed 200×100 elements, ≈4.1×10^4 DOFs, derived]. Other examples: L-bracket 200×80 points, multi-load 100×100, 3D 200×100×50", "classical_iterations": "SIMP

## P00073 (decision order 590; provisional top-up 23) — An Uncertainty-aware Deep Learning Framework-based Robust Design Optimization of Metamaterial Units (2024)

- Link: https://arxiv.org/abs/2407.20251
- Access: full_text; inclusion: **include** (I-QUALITY (screening code confirmed at full text)); stratum: **quality**
- Primary outcome (Section 4.2.1, Table 5 (first quantitative classical comparison; the Abstract, Section 5 conclusion and Introduction compare only qualitatively)): For bulk-modulus maximization at volume fraction 0.3, the robust VAE–MDN design re-analysed by FEA on the 26×26×26 domain gives 5954.8 MPa (volume fraction 0.302) versus 5577.8 MPa for a literature TO design (0.3) (Table 5).
- Key phrase: yielded designs with a higher normalized bulk modulus
- Claimed speed-up: None (No runtime of TO or of design inference is reported. Sec. 4.2.1 states only qualitatively that design inference is fast after training while TO needs costly iterations. Only training costs are given (Table 1). Not derivable.)

- **R1 = partial** [R1-loose] — Sec. 4.2.1, Table 5: one robust design (volume fraction 0.302) is compared with one literature TO design (0.3) [77]; both are analysed with 8-node bricks on the 26×26×26 domain of [77] after the robust design is resized from 48³. The robust design carries 0.67% more material [derived] and lies outside the ±0.001 volume tolerance of Eq. 18 after resizing [derived]. The TO design is not re-run: its stopping rule, material properties and the way its geometry was reproduced are not stated. No compute budget is compared.
- **R2 = pass** [R2-none-established] — The classical comparator is a published 2011 TO result for maximum bulk modulus [77] at 26³ resolution, re-analysed with the authors' FEA [inferred from the Table 5 caption]. The article gives no information on its settings or convergence, so its competence cannot be judged from the text. No runtimes exist, so markers (a)-(e) cannot apply. Unsure, so pass.
- **R3 = na** [R3-na-no-speed-claim] — Quality stratum; the only speed statement is qualitative (Sec. 4.2.1). For C3: training about 442.1 min with progressive transfer learning vs about 234.6 min from scratch (Table 1; hardware not stated); 46,840 ABAQUS unit-cell simulations for the dataset (Sec. 3), cost not stated; the cost of the NSGA-II latent search with 80 latent samples per evaluation (App. B) is not stated.
- **R4 = pass** [R4-FE-verified] — Sec. 4.2.1, Tables 4-5: the returned designs are decoded to voxels and re-analysed by FEA (FEA bulk modulus for all six β values; Table 5 for the resized design), and the volume fraction of every design is reported. Floating material is disclosed for β = 0.5 and 1, whose FEA values fall well below the predictions (6347.29 vs 7422.34 MPa and 4554.07 vs 7321.25 MPa, Table 4). The choice of β = 5 follows a stated rule (Sec. 4.2.1). Case 2 designs are also checked by simulation (Table 6).

- Baseline: {"classical_method": "A published TO design for maximum bulk modulus at volume fraction 0.3 from ref. [77] (Huang, Radman, Xie 2011, Computational Materials Science 50(6) 1861-1870, per the reference list); the TO algorithm is not named in this article and the design is not re-run (Sec. 4.2.1)", "implementation": "literature result [77]; how its geometry was reproduced for the FEA, and which material properties it was given, are not stated", "solver": "not stated (dataset FEA in ABAQUS with a user subroutine and periodic boundary conditions, Sec. 3; the Table 5 FEA uses 8-node bricks, software not stated)", "hardware_classical": "not stated", "hardware_ml": "not stated", "problem_size": "ML: 48×48×48-voxel unit cells, with the 24×24×24 octant as network input (Sec. 3, 4.1.1); comparison on the 26×26×26 domain of [77] after resizing the ML design (Sec. 4.2.1)", "classical_iterations": "no

## P00425 (decision order 594; provisional pilot 19) — Speeding up Computational Morphogenesis with Online Neural Synthetic Gradients (2021)

- Link: https://arxiv.org/abs/2104.12282
- Access: full_text; inclusion: **include** (I-SPEED); stratum: **speed**
- Primary outcome (Abstract (last sentence); supported in Sec. IV-D and Fig. 6(b) (MBB Mesh 4, block size N_B = 4)): ONSG replaces most exact adjoint gradients with gradients from a network trained online. It runs up to 7.5x faster than the standard OC optimizer on a 3D MBB problem with about 1.4 million design variables, at comparable final compliance.
- Key phrase: our method achieves up to 7.5x speedup while producing optimized designs with comparable objectives
- Claimed speed-up: 7.5 (Stated in the abstract and in Sec. IV-D: wall-clock ratio of the standard optimizer to ONSG on MBB Mesh 4 (1.4M design variables) with N_B = 4. The bar-chart wall-clock times appear only in Fig. 6; the text gives the ratio labels only.)

- **R1 = pass** [R1-matched] — Sec. IV, Table II and Fig. 6: each speed-up is a wall-clock ratio for runs with the same total iteration count (K = 200 for all experiments [inferred to include the standard optimizer]) on identical resources. Final compliance is within -0.46% to +0.06% of the standard result. Both methods use the same volume fraction (12%) and filter radius. Final volumes are not reported; OC enforces the volume constraint [inferred].
- **R2 = partial** [R2-partial-inefficient-solver (Jacobi-PCG)] — Sec. IV, Competitor method: the baseline solves with Jacobi-preconditioned CG in MATLAB on the GPU. That solver is neither sparse direct nor multigrid-preconditioned, so it is outside the protocol's efficient class. Marker (c) does not apply, because both methods run on the same GPU machine. Marker (b) is not observed. Marker (d) cannot be judged: both methods run a fixed K = 200, and the convergence curves exist only as plots (Fig. 5). Markers (a) and (e) need the re-test, and per-iteration times are not printed.
- **R3 = na** [R3-na-online-per-problem] — Sec. III-B and Algorithm 1: the network is trained online from the run's own exact-gradient iterations. There is no pre-collected data and no offline training. The training time sits inside ONSG's reported wall-clock time [inferred from Algorithm 1 and Sec. IV-C].
- **R4 = partial** [R4-no-constraint-report] — Table II reports final compliance objectives for all 6 runs [inferred to be FE-computed, since the objective needs the state solve]. Designs are shown in Figs. 3-4. Final volume fractions and any failed runs are not reported.

- Baseline: {"classical_method": "Standard density-based compliance minimization with a density filter and optimality-criteria (OC) update, using exact adjoint gradients at every iteration (Sec. III-D; Sec. IV, Competitor method)", "implementation": "MATLAB, using MATLAB's built-in GPU implementation of PCG (Sec. IV, Competitor method)", "solver": "Iterative: PCG with a Jacobi preconditioner on the GPU (Sec. IV, Competitor method). It is not multigrid-preconditioned. The article describes this choice as the most efficient available, citing [44].", "hardware_classical": "Same machine and same resources as ONSG: Nvidia Titan Xp (12GB), Intel Xeon Silver 4116 at 2.10GHz, 256GB RAM (Sec. IV, Experimental settings)", "hardware_ml": "Nvidia Titan Xp (12GB), Intel Xeon Silver 4116 at 2.10GHz, 256GB RAM (Sec. IV, Experimental settings)", "problem_size": "3D. Cantilever Mesh 1, 2, 3: 86K, 250K, 1.5M design v

## P00064 (decision order 599; provisional top-up 15) — Consistent machine learning for topology optimization with microstructure-dependent neural network material models (2025)

- **FLAG — stratum check: The abstract frames ML as cheaper than computational homogenization but never measures it. Under the no-baseline clarification that framing is not a comparison, so the quality comparison stays primary. Confirm.**
- Link: https://arxiv.org/abs/2408.13843
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-SPEED; the cost advantage over computational homogenization is framing only and never measured; the only classical comparison executed is design parity)); stratum: **quality**
- Primary outcome (Sec. 5.4, Figs. 6-9, pp. 14-17 (first optimization-level comparison with a classical method; figure-based: objective histories and difference plots, with no per-model final values printed); App. D.1 and D.3 repeat it for the portal frame and the 3D beam. The Abstract, Sec. 6 Conclusions and Introduction hold no quantitative classical comparison.): In single-scale finite-deformation TO (T-bracket, cantilever, portal frame, 3D beam), designs and objective histories obtained with the consistent ML material model nearly coincide with those obtained with the ground-truth phenomenological Arruda–Boyce model.
- Key phrase: demonstrating nearly identical designs in a setting with directly comparable conventional results
- Claimed speed-up: None (No runtime, cost or iteration time is reported for any method (full text searched). The cost advantage over computational homogenization or FE2 is stated only as motivation (Abstract; Sec. 1). Not derivable.)

- **R1 = pass** [R1-matched] — Sec. 5.4 and Table 3: both runs use the same mesh, volume bound (g_max 0.5 T-bracket, 0.6 cantilever), filter, projection, continuation, MMA settings and stopping rules, and the objective histories and continuation steps overlap (Figs. 7, 9). The comparison isolates the material model. Final objective values and achieved volumes are not printed, but nothing suggests a mismatch. Unsure, so pass.
- **R2 = pass** [R2-none-established] — The classical comparator is the authors' own TO run with identical settings (Sec. 5.4; Table 3), so it is run as competently as the ML variant, with the full continuation schedule and the same step-stopping rules. No runtimes exist, so markers (a)-(e) do not bear on a speed claim. Linear solver and hardware are not stated.
- **R3 = na** [R3-na-no-speed-claim] — No speed or cost claim is quantified. For C3: training and data-generation costs are not reported; the Dm dataset needed 5 × 2^10 ABAQUS RVE simulations (Sec. 5.1), and training ran on an RTX 3050 Ti desktop (footnote 2, p. 12).
- **R4 = partial** [R4-surrogate-predicted] — Objectives come from a real nonlinear FE analysis, but each design is scored under its own material model: the ML-designed structures are not re-evaluated with the ground-truth Arruda–Boyce model (Sec. 5.4; Figs. 7, 9) [inferred: no cross-evaluation is described]. The Ms surrogate is very accurate (test 1-R2 3.22e-8, Table 2), and the difference plots compare the returned designs directly. Achieved volume fractions are not reported, and instabilities are discussed only qualitatively (cantilever, Sec. 5.4.2). Multiscale designs have no ground truth at all (Sec. 5.5).

- Baseline: {"classical_method": "The same density-based TO (filter, Heaviside projection, SIMP energy interpolation of Wang et al. 2014, generalized displacement control, MMA, continuation) run with the analytical Arruda–Boyce hyperelastic model instead of the ML model (Secs. 3, 5.4). FE2 or computational homogenization is named as the classical route for the multiscale case but not run (Sec. 1).", "implementation": "not stated for the TO code; ML workflow in JAX with Equinox and Optax (footnote 2, p. 12); RVE data generated in ABAQUS through the f3dasm framework (Sec. 5.1)", "solver": "Newton-Raphson with relative tolerance 1e-6 and 8 load steps (15 for the 3D example) (Algorithm 1; Table 3; App. D.3); linear solver not stated", "hardware_classical": "not stated", "hardware_ml": "ML training on a standard desktop with an NVIDIA RTX 3050 Ti GPU (footnote 2, p. 12); TO hardware not stated", "problem

## P00208 (decision order 628; provisional top-up 17) — HPG-Diff: Hierarchical physics-guided diffusion with differentiable connectivity constraints for topology optimization (2026)

- Link: https://arxiv.org/abs/2607.07233
- Access: full_text; inclusion: **include** (I-QUALITY (screened I-UNCLEAR; the abstract's quantitative classical comparison is compliance error against SIMP reference designs; a SIMP timing appears only in the Sec. 4.7.2 discussion)); stratum: **quality**
- Primary outcome (Abstract (sentence 7); numbers in Sec. 4.4.2-4.4.3, Tables 2-3. §5.1 rule 1: the abstract's only quantitative comparison involving the classical method is compliance error against the SIMP references (the same convention as P00375)): Against SIMP-optimized reference designs, HPG-Diff outputs have mean compliance error of 0.87% on 1,800 in-distribution and 5.29% on 1,000 out-of-distribution test problems, with floating material in 2.90% and 2.44% of samples.
- Key phrase: achieves average compliance errors of 0.87% (in-distribution) and 5.29% (out-of-distribution)
- Claimed speed-up: None (Not applicable to the quality-stratum primary outcome. Alternative (Table 8, Sec. 4.7.2): SIMP 23.93 s on a multi-core CPU vs HPG-Diff 10.74 s on a single GPU at 64×64 gives 2.23 [derived]; the text calls HPG-Diff about twice as fast as SIMP.)

- **R1 = partial** [R1-loose] — Sec. 4.1-4.2, Tables 2-3: each binarized output is compared with the SIMP reference for the same boundary conditions and prescribed volume fraction, but volume is only approximately matched (mean VFE 1.38% in-distribution and 1.45% out-of-distribution). The references' SIMP settings and stopping rule are not stated in this article (dataset of ref. [31]). No compute budget is matched; the quality claim does not rely on one.
- **R2 = pass** [R2-none-established] — Quality stratum: judged on the competence of the SIMP references. Their settings are not stated (ref. [31]); median CE of 0.16% (Table 2) shows the references are usually slightly better than the generated designs, and the few case-study designs that beat SIMP by 0.8-2.0% [derived] (Sec. 4.6) are consistent with local optima, not an incompetent baseline [inferred]. Unsure, so pass.
- **R3 = na** [R3-na-quality-stratum] — Primary outcome is quality only. For C3: training time is not reported (about 200 epochs on one A100, Sec. 4.3); the cost of the 30,000 SIMP training samples, the added displacement and principal-stress-line fields, and the 1,000-sample LoRA set is not reported (Sec. 4.1, 4.6); no break-even.
- **R4 = pass** [R4-verified] — Sec. 4.2: all metrics are computed on binarized outputs with a standard FEA solver over all 1,800 and 1,000 test samples (Tables 2-3). Volume error and floating-material share are reported; App. E counts failures (2.70% of Test 2 samples above 30% CE, maximum 791.07%), which shows the averages include outliers [inferred]; App. D repeats inference over five seeds. Case-study figures show selected designs, but the quantitative results cover full test sets.

- Baseline: {"classical_method": "SIMP minimum-compliance optimization: reference designs of the TopoDiff dataset of Mazé et al. [31] (Sec. 4.1); SIMP also timed in Table 8 and used for the case-study ground truths (Sec. 4.6); 5- or 10-step SIMP post-processing inside the DOM baseline (Table 4)", "implementation": "not stated (dataset taken from ref. [31]; the SIMP code behind Table 8 and the case studies is not named)", "solver": "not stated", "hardware_classical": "a multi-core CPU, model not stated (Table 8 caption)", "hardware_ml": "one NVIDIA A100 for training and inference (Sec. 4.3); Table 8 ML timings on a single GPU", "problem_size": "64×64 elements (Table 8 caption; Sec. 4.7.3) [≈8.5×10³ DOFs, derived]; LoRA adaptation at 60×20 (Sec. 4.6)", "classical_iterations": "not stated for the reference dataset. The Table 8 caption says 100 steps without saying whether this counts SIMP iterations or

## P00252 (decision order 633; provisional top-up 6) — TopoEdit: Fast Post-Optimization Editing of Topology Optimized Structures (2026)

- **FLAG — FT-NOBASELINE candidate: Re-running TO is the named slow alternative but is never run, timed or evaluated. The quantitative comparisons are with direct density-space edits, which are not optimization methods (prefill notes).**
- Link: https://arxiv.org/abs/2602.22430
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text; qualitative primary outcome)); stratum: **speed**
- Primary outcome (Abstract (the same contrast recurs in Sec. 1, the last paragraph of Sec. 4.1 and Sec. 4.3); only the ML time is quantified (Sec. 4.1). No quantitative comparison with a classical optimization method exists anywhere, so §5.1 rule 3 applies): Qualitative: TopoEdit edits an optimized topology with sub-second diffusion sampling per candidate, whereas re-running topology optimization is described as slow and prone to drift; no re-optimization time or design is reported.
- Key phrase: re-running optimization is slow and may drift toward a qualitatively different design
- Claimed speed-up: None (Not derivable: no re-optimization time is reported. ML side only: about 0.58 s per diffusion sample on an RTX Pro 6000 GPU, plus 1.13 s for 10 SIMP post-processing steps on a CPU for warps (Sec. 4.1).)

- **R1 = fail** [R1-no-quality-comparison] — Abstract, Sec. 1, Sec. 4.1 (last paragraph) and Sec. 4.3: the speed claim is against re-running optimization, which is never run, timed or compared on design quality; all quantitative quality comparisons (Tables 2-4) are against direct density-space edits. The headline time covers one diffusion sample (about 0.58 s, Sec. 4.1), while the reported quality uses best-of-64 selection (64 samples plus compliance evaluations, time not stated) and, for warps, 10 SIMP steps (1.13 s, reported separately in Sec. 4.1).
- **R2 = pass** [R2-none-established] — No classical re-optimization is run, so the comparator's implementation, solver, iterations and hardware are unknown (Sec. 4). The only classical component is the 10-step SIMP OC post-processing on an unspecified CPU (1.13 s; Sec. 3.4, 4.1), shared by both edit pipelines. Problem sizes are not stated, so (c) cannot be established; (b), (d) and (e) are not derivable. Unsure, so pass.
- **R3 = fail** [R3-no-cost] — TopoEdit runs on frozen pretrained OAT weights (Fig. 1); OAT is trained on 2.2 million optimized structures (Sec. 2). The article reports neither OAT's training cost nor the cost of generating those structures, and gives no break-even; the speed claim is framed per sample (abstract). TopoEdit itself adds no training.
- **R4 = pass** [R4-verified] — Sec. 4.1-4.3 and Tables 2-4: compliance of every returned edit is computed under the original loads and boundary conditions (FE-based [inferred]); volume-fraction error, no-design violation ratio and failure rates are reported for every N and for the direct baselines; the best-of-N rule is stated (minimum sum of compliance and distance errors, Sec. 4.1). Figs. 4, 8 and 10 show selected examples, but the tables cover all test edits. Fig. 6 drops cases above 1000% compliance, which Table 2 counts as failures.

- Baseline: {"classical_method": "Re-running topology optimization from scratch (named as the slow alternative in the abstract, Sec. 1, 4.1 and 4.3; never run). The quantitative comparators are non-learned direct density-space edits (direct warp, direct lattice swap, direct hole); for warps, both direct and latent results get the same 10 SIMP OC post-processing steps (Sec. 3.4, 4.1-4.3)", "implementation": "not stated (re-optimization not run). SIMP post-processing: density SIMP with p = 3 and optimality-criteria updates, warm-started from the edited design, warps only (Sec. 3.4); code not stated", "solver": "not stated", "hardware_classical": "not stated for re-optimization (not run); SIMP post-processing on 'the CPU', model not stated (Sec. 4.1)", "hardware_ml": "PC with an RTX Pro 6000 GPU, 96 GB VRAM (Sec. 4)", "problem_size": "not stated in this article; reference topologies come from the OAT t

## P00158 (decision order 638; provisional top-up 27) — Generative Design by Reinforcement Learning: Enhancing the Diversity of Topology Optimization Designs (2020)

- Link: https://arxiv.org/abs/2008.07119
- Access: full_text; inclusion: **include** (I-SPEED); stratum: **speed**
- Primary outcome (Sec. 5 Conclusion, second paragraph, p. 22 (first quantitative classical comparison in the conclusion; the abstract compares with the earlier CPU-based approach only qualitatively). The same comparison opens Sec. 3 (p. 8: about 10 min vs under 10 ms)): TopOpNet, a CNN that stands in for the wheel TO algorithm, returns a design within milliseconds of GPU inference, whereas the CPU-based TO algorithm is said to need on the order of ten minutes per run.
- Key phrase: the algorithm requires an order of 10 min in general
- Claimed speed-up: 60000 (Derived, order of magnitude only; no factor is stated. Sec. 3 opening (p. 8): TO on the order of 10 min vs TopOpNet under 10 ms, so 600 s / 0.01 s = 6x10^4, a lower bound on the ML side. The conclusion (p. 22) pairs about 10 min with milliseconds (6x10^5 if 1 ms). Sec. 3.5 (p. 13) instead gives seconds for simple inputs vs under 1 ms on a GTX 1080 Ti, about 10^3 [derived]. No averaged timing, iteration count or CPU model is given for the TO runs, and dataset generation and training are not counted.)

- **R1 = partial** [R1-loose] — Conclusion p. 22 and Sec. 3 p. 8: TopOpNet inference (milliseconds) is set against full TO runs (about 10 min). Quality is reported (Table 1: compliance MAPE 0.8851 +/- 0.2341, median-based), but matching is loose: the median hides the large-error outliers the authors mention (p. 13), no volume error is given, the TO stopping rule and iteration count are not stated, and the times are orders of magnitude that differ between sections (10 min vs seconds; 10 ms vs 1 ms). MAPE is an absolute error, so the text does not establish that TopOpNet designs are worse; R1-unmatched is therefore not established. A verifier who treats any reported compliance deviation as measurably worse would code fail.
- **R2 = partial** [R2-inefficient-impl; R2-hardware-unjustified] — Sec. 3.5 (p. 13), abstract and conclusion: the TO algorithm runs on an unnamed CPU and is described as computing inverse matrices and determinants with exception handling, which suggests an inefficient implementation [inferred]; TopOpNet runs on a GTX 1080 Ti GPU, and the CPU-to-GPU shift is presented as a benefit without justification. (c) is not established because the FE size is not stated [about 3.3x10^4 DOFs if 128 x 128, inferred, below 10^5]. (b) does not apply: the abstract gives no numbers. (d) and (e) cannot be derived: no iteration count or per-iteration time.
- **R3 = fail** [R3-no-cost] — Sec. 3.2-3.4: neither the 77,319 TO runs [derived] that produce the training data nor the TopOpNet training time is quantified, and no break-even is given; the data-generation burden is acknowledged only qualitatively (Sec. 1). For C3 [derived, order of magnitude]: at about 10 min per TO run the data alone need about 77,320 uses to break even, before training cost.
- **R4 = partial** [R4-no-failure-rate] — Table 1, p. 13: compliance of TopOpNet outputs is compared with the TO outputs for the full validation set (FE analysis inferred; the method is not described), alongside image metrics (IoU, pixel difference, cross-entropy). The compliance statistic is a median because outliers give very large errors; the number of such outliers, failed designs and volume-constraint satisfaction are not reported. Figs. 8-9 show examples chosen without a stated rule, but Table 1 covers all validation cases.

- Baseline: {"classical_method": "Wheel TO algorithm of Oh et al. (2019): compliance minimization plus an L1 similarity term to a reference design, with a volume equality constraint (Eq. 1, Sec. 3.1); run on an 11 x 11 grid of similarity weight (0.0005-5.0, log scale) and force ratio (0.0-0.4) per reference image (Sec. 3.2)", "implementation": "not described in this article (taken from Oh et al. 2019); Sec. 3.5 (p. 13) says the algorithm performs many matrix manipulations, including inverse matrices and determinants, with exception handling when these fail", "solver": "not stated", "hardware_classical": "CPU (Sec. 3.5, abstract, conclusion); model not stated. A PC with an Intel i7 CPU and a GTX 1080 Ti GPU is named only for the exhaustive search (p. 20)", "hardware_ml": "NVIDIA GeForce GTX 1080 Ti GPU (Sec. 3.5, p. 13)", "problem_size": "128 x 128 single-channel images for TopOpNet (Sec. 3.3); FE me

## P00156 (decision order 649; provisional top-up 5) — Accelerating gradient-based topology optimization design with dual-model neural networks (2020)

- Link: https://arxiv.org/abs/2009.06245
- Access: full_text; inclusion: **include** (I-SPEED (screening code confirmed at full text; cost proxy = per-evaluation surrogate cost vs FE inside SIMP)); stratum: **speed**
- Primary outcome (Abstract; numbers in Section 4.3, Table 7 (pp. 26-27)): On the 64×64 metamaterial cell, the trained dual-model network computed the forward quantity 137× faster and its sensitivities 74× faster than FEM (0.0035 vs 0.48 s; 0.0066 vs 0.49 s per structure, same Xeon CPU); no whole-optimization runtime is compared.
- Key phrase: 137 times in forward calculation and 74 times in sensitivity analysis
- Claimed speed-up: 137 (Stated (abstract; Table 7): FEM 0.48 s ÷ NN 0.0035 s = 137 for the forward calculation of the 64×64 metamaterial cell; sensitivity 0.49 s ÷ 0.0066 s = 74; cantilever 36×36: 54 (0.21 ÷ 0.0039) and 24 (0.21 ÷ 0.0088). Proxy: per-evaluation surrogate cost vs FE, not an optimization-level speed-up. No total design time of NN-accelerated or FEM-based SIMP is reported, and the iteration counts of NN-accelerated runs are not stated.)

- **R1 = partial** [R1-loose] — Section 4.3, Table 7 vs Figs. 10-13: the speed claim is per evaluation (NN vs FEM forward and sensitivity calculation), and the NN accuracy is reported: about 94% average prediction accuracy and up to about 95% design accuracy with augmented data (Sections 4.1-4.2). No optimization-level runtime of NN-accelerated vs FEM-based SIMP is given, the iteration counts of NN-accelerated runs are not stated, and the per-evaluation speed-up is not tied to matched design quality or budget.
- **R2 = partial** [R2-inefficient-impl [inferred]] — Table 7 and Section 4.3: FEM takes 0.21 s per forward or sensitivity calculation on a 36×36 cantilever and 0.48-0.49 s on the 64×64 metamaterial cell, on one Intel Xeon E5-2687W v2 CPU; the NN runs on the same CPU, so (c) does not apply. The FEM code and linear solver are not stated. These per-solve times look slow for 2D meshes of about 2.7×10³ to 8×10³ DOFs [inferred]; (e) needs a same-size re-test. (b) no: the abstract figures equal Table 7. (d) no: SIMP runs to convergence (average 150 and about 200 iterations, Sections 4.1-4.2).
- **R3 = fail** [R3-no-cost] — Abstract and Section 4.3: the 137×/74× claim comes with no training time and no data-generation time, although the abstract says the data methods save training time. Only counts are given: 1929 and 2030 training samples (610 and 677 augmented) from 18 and 13 FEM-based SIMP runs. No break-even and no per-query limitation. [Inferred at the Table 7 FEM times: roughly 0.2-0.4 h and 0.4-0.9 h of FEM time for data; training time unknown.]
- **R4 = partial** [R4-no-constraint-report] — Eq. 19 and Sections 4.1-4.2: the design error uses the FEM-computed compliance (or FEM-validated Poisson's ratio) of each returned design against the FEM-based SIMP benchmark, averaged over 126 and 120 test cases (Figs. 10-13). Achieved volume fractions of the NN-accelerated designs are not reported. Disconnected or failed designs are described only in words (some barely connected without augmentation; almost all connected with it), with no count. Tables 2, 3, 5 and 6 show a few cases without a stated selection rule, but the averages cover all test cases.

- Baseline: {"classical_method": "SIMP with FEM forward analysis and adjoint sensitivities, sensitivity filter radius 4 pixels, gradient-descent update, density projection with growing sharpness and threshold 0.5 (Section 2); cantilever compliance with a Lagrange-multiplier volume term (Eq. 5) and inverse-homogenization design of negative-Poisson's-ratio cells with weighted penalty terms (Eq. 9)", "implementation": "not stated (the FEM code is not described). The linked repository holds only two TensorFlow NN training scripts [checked 2026-09-24]", "solver": "not stated", "hardware_classical": "Intel Xeon CPU E5-2687W v2, 3.40 GHz (Section 4.3)", "hardware_ml": "same computer: all calculations on the Xeon E5-2687W v2 (Section 4.3); training hardware not stated separately", "problem_size": "cantilever 36×36 elements (Section 4.1); metamaterial cell 64×64, quarter domain designed by symmetry (Section 

## P00041 (decision order 655; provisional top-up 11) — Data-driven topology optimization for multiscale biomimetic spinodal design (2026)

- **FLAG — FT-NOBASELINE candidate: The cost claim against homogenization-in-the-loop TO is never measured. Decide whether the single-scale tensile-bar run counts as a classical comparator (prefill notes list three options).**
- Link: https://arxiv.org/abs/2506.23420
- Access: full_text; inclusion: **include** (I-SPEED (screening code kept at full text; the cost claim is qualitative and never measured, so inclusion is borderline)); stratum: **speed**
- Primary outcome (Abstract (qualitative); restated in Sec. 5 Conclusion, para. 2 (arXiv v2 p. 21) as the approach's primary strength. No quantitative comparison of this framework with a clearly classical method exists (see alternatives 1-2), so protocol 5.1 rule 3 applies.): The framework's Gaussian-process surrogate replaces repeated computational homogenization inside multiscale spinodoid TO, which the authors present as a cost and scalability advantage over homogenization-in-the-loop TO; no runtime of any method is reported.
- Key phrase: eliminating the need for repeated computational homogenization
- Claimed speed-up: None (Not derivable: no runtime, iteration time or cost is reported for any method (full text searched). Sec. 5 cites 'up to four orders of magnitude' cost reduction for constitutive surrogates versus FE2-type direct simulation from the authors' earlier works (Deng et al. 2024, 2022a, 2023; arXiv v2 refs [18], [61], [62]). That figure concerns other models and forward simulation, not this framework, so it is not entered.)

- **R1 = partial** [R1-loose] — Sec. 3.4, Fig. 13: the surrogate that carries the cost claim is checked against FE homogenization (test RRMSE 2.59e-3 to 8.05e-3), so some quality evidence exists. No speed comparison is run at all: no classical homogenization-in-the-loop TO, no timing, and no design-level matching. A stricter reading (speed claim with no design-quality comparison) gives fail, as in P00519.
- **R2 = na** [R2-na-no-baseline-run] — No classical optimization baseline is implemented or timed for the cost claim, so markers (a)-(e) cannot apply. If the verifier moves the record to stratum Q via the single-scale comparison, R2 would be pass (unsure): that run's optimizer and solver are not stated and it used the same 100 iterations as the neural runs (Fig. 16).
- **R3 = fail** [R3-no-cost] — The GPs are trained offline on 3 × 500 samples drawn from 1,800 reconstructed and FE-homogenized microstructures (Sec. 3.4; Algorithm 1 initialization). Neither the homogenization time nor the GP training time is reported, no break-even is given, and the claim is not limited to per-query use. The neural reparameterization itself is per-problem, but the offline GP makes R3 applicable.
- **R4 = partial** [R4-surrogate-predicted] — Design compliances (e.g. 4.85e3, 7.67e3, 7.86e3 N·m, Sec. 4.1) come from a real macroscale FE analysis but with GP-predicted effective moduli. The returned post-processed designs (interface interpolation and amplification, Sec. 3.2; Algorithm 1 postprocess) are never re-analysed; the smoothing effect was checked on four sample microstructures only (Table 1, RRMSE 0.0092-0.0370). Volume is a soft penalty constraint; its history is plotted for the tensile bar only (Fig. 16(b)-(c)) with no final values; no failure counts (e.g. loss of bi-continuity). A stricter reading gives fail.

- Baseline: {"classical_method": "Named but never run for the cost claim: repeated computational (FE) homogenization inside multiscale TO loops (Abstract; Sec. 1; Sec. 5). The only other comparator is a 'classic single-scale structural TO' of the tensile bar with the solid modulus penalized to its 70% value (Sec. 4.1, Fig. 15(b)); its optimizer is not stated.", "implementation": "Not applicable to the cost claim (no homogenization-in-the-loop TO implemented). Framework: spinodoid reconstruction and data repository in MATLAB; NN-reparameterized TO in JAX (Sec. 4, p. 14). Single-scale run: not stated; Fig. 16 plots it on the same 100-iteration axis, with a decaying volume-violation history like the neural runs [inferred: same framework].", "solver": "not stated (macroscale FE and RVE homogenization FE)", "hardware_classical": "not applicable (no classical baseline timed); all numerical experiments ran
