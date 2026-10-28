# Audit protocol — pre-registered

**Version:** 1.0 · **Written:** 2026-09-24 · **Freeze rule:** this file is hashed into `evidence/MANIFEST.sha256`
before the first coding record or timing run exists. Any later change goes into §11, the deviations log, with date and
reason. Nothing is edited silently.

The design follows McGreivy & Hakim (*Nat. Mach. Intell.* 2024, doi 10.1038/s42256-024-00897-5; arXiv 2407.07218).
Their Methods were read on 2026-09-24. Two differences matter:
- **They excluded solid mechanics and metamaterials.** Their exclusion list reads "solid mechanics … meta-materials,
  hyper-elasticity". This audit covers that excluded domain.
- **Their break-even calculation was a recommendation (Rec. 3); here it is a rule (R3).** In TO the training data are
  produced by the very optimizer the model replaces.

---

## 1. Questions

- **C1.** Among articles that use machine learning (ML) for topology optimization (TO) and claim to outperform a
  classical method, what share of primary outcomes violate at least one fairness rule (R1–R4)?
- **C2.** How much do re-tested speed-up claims shrink against a strong classical baseline at matched design quality,
  on one machine?
- **C3.** How does counting data generation and training change the break-even number of uses?
- **C4.** How common are reporting practices that hide negative results?
- **C5 (secondary).** How well does an LLM pre-extraction agree with the human-verified verdicts?

## 2. Sources and search

All searches are recorded with date, query string, endpoint and raw response in `audit/search/`. The query list is
frozen in `audit/search/queries.json` before any screening.

1. **Keyword queries.**
   - arXiv API: title and abstract fields.
   - OpenAlex: the `title_and_abstract.search` filter, publication date ≥ 2017-01-01.
   - Queries cover "topology optimization" and "topology optimisation" crossed with: deep learning, neural network,
     machine learning, generative, GAN, diffusion, variational autoencoder, flow matching, reinforcement learning,
     large language model, agent, neural reparameterization, implicit neural, physics-informed, surrogate.
   - They also cover metamaterial, microstructure and architected material crossed with inverse design and ML
     (restricted to TO or homogenization comparators).
2. **Forward citations** (OpenAlex `cites:` filter) of these anchor articles:
   - Sosnovik & Oseledets 2017 (neural networks for TO);
   - Banga et al. 2018 (3D TO with CNNs);
   - Nie et al. 2021 (TopologyGAN, doi 10.1115/1.4049533);
   - Chandrasekhar & Suresh 2021 (TOuNN);
   - Woldseth et al. 2022 (doi 10.1007/s00158-022-03347-1);
   - Mazé & Ahmed 2023 (TopoDiff, arXiv 2208.09591).
   Each anchor's identifier is resolved and recorded before use. An anchor that cannot be resolved is logged in §11 and
   dropped.
3. **Backward citations**: reference lists of Woldseth et al. 2022, Sanu et al. 2025 and OAT (arXiv 2510.23667),
   matched by title.

**Search end date.** The date the queries are frozen is recorded in `queries.json`. Only articles available on or
before that date are included.

## 3. Inclusion criteria (all must hold)

1. **Method.** A learned model is used to produce, accelerate or replace iterative TO. Learned models include neural
   networks, Gaussian processes, reinforcement learning, diffusion or flow models, GANs, VAEs, transformers and LLMs.
   - TO covers density-based methods (SIMP, RAMP), level-set, moving morphable components/voids, and ESO/BESO.
   - Physics covers linear or nonlinear elasticity (compliance, stress, displacement), heat conduction, and compliant
     mechanisms.
   - Also included: inverse design of architected materials or metamaterials, where the classical comparator is TO or
     homogenization-based optimization.
2. **Comparison.** The article's **primary outcome** (§5.1) compares the ML method with a classical, non-learned
   optimization method on **speed or computational cost, or a proxy for them**. Examples: "N× faster", "real-time",
   "fewer FE evaluations", "without iterative optimization". This matches the template's speed-based inclusion.
   - Articles whose primary outcome compares only design quality with a classical method are coded too. They are
     analysed as a **secondary stratum (Q)** and are not pooled into the headline C1 rate.
3. **Type.** Journal article, conference paper, or arXiv preprint (latest version). English.
4. **Date.** 2017-01-01 to the search end date.

## 4. Exclusion criteria

- Reviews, surveys, theses, dissertations, presentations, technical reports, patents, abstracts-only records.
- Articles with no comparison to a classical method. Articles that compare only with ML baselines are tallied as
  **ML-only** (reported under C4) and not coded for R1–R4.
- ML used only for forward analysis, with no optimization-level comparison.
- Fluid-flow TO (the template's domain overlaps it), acoustic, photonic and electromagnetic TO.
- Full text not accessible to the coders (tallied separately; a stated limitation).
- Duplicates. Code the version of record when accessible, otherwise the most complete preprint; record both IDs.

## 5. Primary outcome and fairness rules

### 5.1 Primary outcome (template rule, verbatim in substance)

1. If the abstract contains a quantitative comparison with a classical method, that is the primary outcome.
2. Otherwise, take the first quantitative comparison in the conclusion, then the introduction, then the main text.
3. If no quantitative comparison exists anywhere, take a qualitative one ("significantly faster", "outperforms"), in
   the order abstract → conclusion → introduction.
4. If there are several candidates, the coder picks the one the article emphasises most, and records the alternatives.

### 5.2 Scale (template convention)

- ✓ **pass** — the rule is satisfied, **or the coder is unsure**.
- ! **partial** — partly satisfied; or likely not satisfied without enough evidence to be sure.
- ✖ **fail** — not satisfied.
- **n/a** — the rule does not apply.

The headline counts ✖ only. Extended Data ED4 reports the sensitivity with ! counted as ✖.

### 5.3 Rules

**R1 — matched quality or matched time.** (Template rule 1, adapted to design quality.)
- ✓ The speed comparison is made at equal design quality: same volume fraction on the physical field, and compliance
  or the objective within the ML method's reported error of the classical result. Or it is made at equal wall-clock or
  equal FE-evaluation budget.
- ✖ Any of:
  - ML inference time is compared with a classical run to full convergence, while the ML output is measurably worse
    (outside the reported error) and no matching is attempted;
  - a speed claim is made with no quality comparison;
  - post-processing (e.g. SIMP refinement steps) is used for the quality result but not counted in the reported time.
- ! Quality is reported but matching is loose; for example, the classical stopping rule is unstated.

**R2 — efficient classical baseline.** (Template rule 2, adapted.) The state equation in TO is elliptic. Following the
template's elliptic-PDE criterion, efficient means a sparse direct solver (Cholesky/LDLᵀ class) or a
multigrid-preconditioned Krylov solver, on hardware comparable to the ML method.
- ✖ Any of:
  - **(a)** Our re-implementation of the paper's classical method reaches its primary-outcome result significantly
    faster: ≥ 3× on the same hardware class at the same size (after the re-test).
  - **(b)** The abstract reports a weaker baseline than the results or appendix.
  - **(c)** A GPU ML method is compared with a CPU-only classical run on problems of ≥ 10⁵ degrees of freedom, with no
    justification. This is template Rec. 2, made concrete.
  - **(d)** The classical run uses a fixed iteration count at least 2× what the article's own convergence criterion or
    convergence plot needs.
  - **(e)** The reported per-iteration time of the classical method is ≥ 10× our strong baseline's at the same size on
    the same hardware class. Per-iteration time must be derivable from the article.
- ! Any of:
  - the implementation looks inefficient (e.g. an unvectorized educational code, or a general-purpose commercial TO
    module), but no direct comparison is possible;
  - the hardware choice is not justified.

**R3 — full cost accounting.** (TO-specific; template Rec. 3 made a rule.)
- ✓ A speed claim reports both data-generation cost and training cost, and either gives the break-even number of uses
  or explicitly limits the claim to per-query inference.
- ! Training cost is reported but data-generation cost is missing, or costs are reported with no amortization.
- ✖ A speed claim with no training or data cost at all.
- n/a Per-problem learning with no offline training (e.g. neural reparameterization): its cost sits inside R1/R2.

**R4 — verified outputs.** (TO-specific.)
- ✓ Quality is computed by an FE analysis of the **returned** design, including post-processing when used. Volume or
  constraint satisfaction is reported, and infeasible or failed designs (disconnected, floating material, volume
  violation) are counted.
- ! FE-verified, but constraint violations or failure rates are not reported.
- ✖ Quality rests only on image-similarity metrics (MSE, pixel accuracy, IoU), on surrogate-predicted performance, or
  on examples selected without a stated rule.

**Fair** = no ✖ on any applicable rule. **Weak baseline (template-comparable)** = ✖ on R1 or R2.

## 6. Reporting indicators (C4)

Each is recorded as yes, no or unclear, with a locator:
- claim direction (positive, negative, mixed);
- number of test cases;
- out-of-distribution test present;
- seeds or variance reported;
- failure or infeasibility rate reported;
- timing protocol stated (hardware, warm-up, iteration count);
- runtimes reported for all cases or selectively;
- code available;
- data available;
- hardware for each method stated.

Two field-level counts are also kept: the share of included articles claiming to outperform versus to underperform
(the template's publication-bias signal), and the ML-only tally from §4.

## 7. Coding procedure

1. **LLM pre-extraction.** An LLM reads the accessible full text and fills the record schema
   (`audit/schema/coding_schema.json`), with a locator for each field (section, table, figure or page) and at most one
   short key phrase (< 15 words) per article.
   - The prefill is saved to `audit/coding/llm_prefill/` and hashed **before** human verification.
   - Model name and date are recorded.
2. **Human verification.** The human coder checks every field against the article and sets the final verdict and their
   initials in `audit/coding/records/`. **A record without verifier initials does not count** in any reported rate.
3. **Second coder.** A second human codes a random 20 % subset independently. Cohen's κ is reported per rule.
4. **Copyright and storage.** No third-party PDFs are stored in the project. Records hold identifiers, URLs,
   locators, paraphrases and short key phrases only.

## 8. Gates

| Gate | Measurement | ≥ upper | between | < lower |
|---|---|---|---|---|
| **G1** | Share of the 20 pilot primary outcomes with ✖ on R1 or R2 (human-verified; speed stratum) | ≥ 40 % → full audit, *Nat. Mach. Intell.* framing | ≥ 20 % and < 40 % → full audit, ACME/SMO framing | < 20 % → stop the audit; publish the strong baseline as a short benchmark note, or switch to the runner-up (dataset admissibility) |
| **G2** | Strong-baseline wall-clock for a 150-iteration SIMP run at 256×256 on this machine, against OAT's reported 68.30 s (arXiv 2510.23667 Table 6, SIMP-GPU) | ≤ 13.66 s → re-test headline | > 13.66 s and < 68.30 s → moderate | ≥ 68.30 s → OAT's baseline was fair |

- **The pilot sample** is 20 articles drawn uniformly at random, seed **20260924**, from the included set with
  accessible full text, after title/abstract screening is complete.
- **A provisional G1** may be computed from LLM prefills, labelled provisional. The decision uses human-verified
  records only.
- **A provisional G2** uses the pre-registered standard formulation (`plan/BASELINE_PREREG.md`). The final G2 uses
  OAT's own generator settings once its code may be downloaded.

## 9. Statistics

- Proportions with exact Clopper–Pearson 95 % intervals.
- Cohen's κ with bootstrap 95 % intervals (2,000 resamples, seed 20260924).
- Speed-up ratios as medians with interquartile ranges. No pooling across hardware classes.
- No hypothesis test is used to decide a gate. Gates are threshold rules on point estimates, as stated.

## 10. What this audit does not claim

- It does not claim that ML has no value for TO. Design diversity, differentiable priors, out-of-distribution
  exploration and access for users without solvers are outside the rules.
- It does not judge any author's intent.
- It does not re-test every article. Re-tests cover the articles whose code can be run and whose licences allow
  running it.

## 11. Deviations log

| Date | Section | Change | Reason |
|---|---|---|---|
| 2026-09-24 | §2 sources | The OpenAlex queries, forward-citation and backward-citation searches run when the OpenAlex daily budget resets. The arXiv queries ran on 2026-09-24 (523 unique records). Semantic Scholar is also rate-limited (HTTP 429). | The shared free OpenAlex budget for this network was exhausted on 2026-09-24. Recorded in `audit/search/raw/requests.jsonl` |
| 2026-09-24 | §2–4 screening method (clarification before any screening) | Title/abstract screening is pre-screened by an LLM (Claude subagents) against the §3–4 criteria, with a reason code per record. The human coder confirms every include and a random 10 % of excludes (seed 20260924) before full-text coding. Records without human confirmation count only in provisional numbers | Feasibility at pool sizes of hundreds to thousands. This mirrors the §7 prefill-then-verify design |
| 2026-09-24 | §8 pilot | While the pool is arXiv-only, a **provisional** pilot is drawn from the arXiv stratum (same seed and size). The pilot for the G1 decision is redrawn from the complete included set once all sources have run | Keeps coding moving without letting a partial pool decide G1 |
| 2026-09-24 | §8 pilot size (clarification, written before any full-text coding) | G1 needs 20 *speed-stratum* primary outcomes. If fewer of the 20 drawn pilot papers end up in the speed stratum after full-text coding (excluded, or quality-only), add papers from the remaining arXiv-stratum includes in a fixed order until 20 speed-stratum outcomes exist. The order is a shuffle with `random.Random(20260925)`, stored in `audit/screening/pilot_topup_order.csv` | The 20 drawn papers mix I-SPEED, I-UNCLEAR and I-QUALITY screening codes, so some will leave the speed stratum at full text. Fixing the top-up order now keeps it independent of coding results |
| 2026-09-24 | §3.2 / §4 no-baseline articles (clarification after the first 20 LLM prefills; before any human verification) | "Comparison with a classical method" means the article runs, times or cites a classical method's cost or result. A purely qualitative motivation with no classical run and no timing is **no comparison** and is excluded as `FT-NOBASELINE`. This mirrors the template, which excluded articles that compare to no baselines. Human verification applies this rule. Affected prefills: P00002, P00015, P00519 (coded as includes with R1 = fail) | The LLM coders read the rule inconsistently. Applying it as written *lowers* the weak-baseline count, so the clarification works against the audit's hypothesis. It is recorded now, before any verified record exists |
| 2026-09-24 | §4 full-text exclusion reasons (clarification before any human verification) | Full-text exclusions use one code from a closed list, first applicable in this order: FT-DUPLICATE, FT-SCOPE, FT-TYPE, FT-DOMAIN, FT-NOML, FT-FORWARD, FT-MLONLY, FT-NOBASELINE, FT-OTHER (definitions: `audit/schema/screening_codes.md`, second table). Earlier prefills used free-text labels; `analysis/codes.py` maps them without editing the frozen prefills (FT-ML-only → FT-MLONLY, FT-NOCOMPARISON → FT-NOBASELINE) and stops on any other label. Three later prefills (P00252, P00313, P00041) are also flagged as FT-NOBASELINE candidates for the verifier (`audit/coding/verifier_flags.csv`) | The flow diagram (ED1) and the C4 tally need one count per reason. Free-text labels split the counts |
| 2026-09-24 | §2 searches run; anchor FC1 (after the searches, before any screening of their results) | OpenAlex OA1–OA3, forward citations FC1–FC6 and backward citations BC1–BC2 ran at about 20:00 UTC, anonymously: generic User-Agent, no `mailto`. The budget reset was not needed: 918 of 1,000 daily credits were free. FC1 ("Neural networks for topology optimization") first resolved to a wrong work (W2964971928, a graph-neural-network paper), because the title-search fallback took the most-cited non-exact hit. Its 342 results are quarantined in `audit/search/raw/_quarantine/` and excluded. The resolver now accepts exact titles only. `queries.json` v1.1 adds FC1's DOI, 10.1515/rnam-2019-0018 (W2757408183; confirmed by OpenAlex and Crossref). FC1 then returned 30 citing works; OpenAlex has no separate record of the arXiv preprint | A wrong anchor would have added hundreds of off-topic records. The fix changes only how the anchor is found, not what is searched |
| 2026-09-24 | §8 decision pilot (written while the new records are being pre-screened, before any of their screening results are seen) | After LLM pre-screening of the complete pool (all sources), one random order is fixed over all LLM includes: the includes sorted by pid, shuffled with `random.Random(20260924)`, stored in `audit/screening/pilot_final_order.csv`. G1 walks this order and uses the first 20 records that are, at full text, speed-stratum includes. Records that human screening excludes, full-text exclusions (including FT-DUPLICATE), quality-stratum records and records without accessible full text are skipped, not redrawn. An LLM exclude that the human turns into an include is appended in a second shuffle (seed 20260925). Already-coded records keep their frozen prefills. The provisional arXiv pilot and its top-up list stay as recorded and are reported as the provisional G1 | A seeded shuffle, then the first eligible records, is a uniform random draw from the eligible set. Fixing the order now, before the screening results, keeps G1 independent of coding results and robust to later human confirmation |
| 2026-09-24 | §2.3 backward citations: OAT's reference list (found while drafting Methods; before any screening of its records) | §2.3 names three backward sources, but `queries.json` v1.0–1.1 listed only two (Woldseth et al. 2022, Sanu et al. 2025); OAT (arXiv 2510.23667) was omitted in error. OpenAlex holds OAT (W7197034560) without a reference list, so its 64 references were parsed from the arXiv HTML bibliography, as §2.3 specifies ("matched by title"), and stored as titles, authors, venue and year (`audit/search/raw/backward/BC3/references.json`). `queries.json` v1.2 adds BC3. The pool gained 46 records (P02546–P02591); 17 references matched existing records. Existing pids are unchanged (checked) | Brings the search in line with the pre-registered source list |
| 2026-09-24 | §3.4 date window in the decision order (clarification, before the draw) | The decision order covers LLM includes that satisfy §3.4's date window (published 2017-01-01 or later). arXiv and OpenAlex dates decide deterministically; LLM includes dated earlier are listed in `audit/screening/pilot_final_date_excluded.json`. Records known only from OAT's parsed bibliography keep the screener's decision, because their parsed years are unreliable | Screening batches applied the date criterion inconsistently: one coded 67 pre-2017 records E-OTHER, others screened on content. The protocol's own criterion, applied mechanically, removes the inconsistency |
| 2026-09-24 | §3.3 record type in the decision order (clarification, before the draw) | Also applied mechanically at the draw: §3.3 admits journal articles, conference papers and arXiv preprints, so an LLM include that is a preprint on another server (Zenodo, SSRN, Research Square and similar; pool type "preprint" without an arXiv id, arXiv DOI or arXiv venue) is not eligible. It is listed in `audit/screening/pilot_final_date_excluded.json` | One screening batch included about 16 such preprints on content; the protocol's type criterion excludes them |
| 2026-09-24 | §7 verification (major change; the author's decision, recorded before any verification) | Human verification is replaced by independent AI verification. (1) Every coded record in the analysis sample is coded a second time, **blind to the first coding**, by a different model (Claude Sonnet 5; the first pass used the session's default model). (2) Scripts compare the two codings item by item (inclusion, exclusion code, stratum, R1–R4, claimed speed-up) and recheck derived arithmetic. (3) An adjudicator agent settles every disagreement from the article text, with locators. Final records carry stage `ai_agreed` or `ai_adjudicated` and count in reported rates. (4) C5 becomes the agreement between the two independent AI codings (Cohen's κ per item); the human second coder of §7.3 is dropped. Every final record is published with its locators, so any verdict can be checked | The author judged human verification unnecessary and wants a self-contained pipeline with minimal human intervention. First-pass AI coders applied some rules inconsistently in this project, so one AI pass is never used alone: two independent codings plus adjudication replace the human check |
| 2026-09-24 | §2–4 and §8 analysis sample (the author's decision; recorded before any second-pass coding or adjudication) | No census. C1 and C4 are estimated on the records at **positions 1–200 of the decision order**, which is a seeded random permutation of eligible includes, coded wherever a legal full text is accessible. G1 stays the first 20 speed-stratum records of the same order. The provisional arXiv pilot and its top-ups are reported only as a secondary sample | A prefix of a seeded random order is a simple random sample of the eligible includes, so the estimates stay unbiased for the accessible literature. Position 200 balances precision against cost |
| 2026-09-24 | §3.1 and §4 physics scope: elastic waves (clarification before any verification) | Elastic-wave, phononic and seismic metamaterial design in solids is elasticity (elastodynamics) and in scope. "Acoustic" in §4 means sound in fluids. Every screening batch already applied this reading, so no record changes | Consistent with the elasticity scope of §3.1 and with the existing screening |
| 2026-09-24 | §7 access routes and conflicts of interest (the author's decisions) | An open-access copy served from the publisher's own file host (for example mdpi-res.com, or a publisher PDF server linked from the article page) counts as accessible. No CAPTCHA or bot check is ever bypassed. Conflicts of interest confirmed by the author: P00428 and P00501 are co-authored by the author's PhD advisor, and P00497 is the author's own paper. They are coded like all other records and disclosed in the manuscript | Recorded as instructed |
| 2026-09-24 | §2–4 screening check (follows the verification decision above) | The human confirmation of title/abstract screening is replaced by AI. (1) For records in the analysis sample, full-text coding (first pass, blind second pass, adjudication) decides inclusion, as the protocol already makes the full text the arbiter. (2) The random 10 % sample of LLM excludes (seed 20260924, `audit/screening/human_check.csv`, 188 records) is re-screened blind by a different model, and the disagreement rate is reported as the estimated false-exclusion rate | Same author decision: self-contained, with minimal human intervention |
| 2026-09-24 | §5.3 rule applicability in the secondary stratum Q (clarification before any adjudication; both blind passes coded without it) | When the primary outcome compares design quality only (stratum Q): R3 is n/a, because it concerns speed claims; R2 applies only through criterion (b), a weaker baseline in the abstract than in the results or appendix, and is otherwise n/a, because its other criteria concern the cost of the classical run; R1 and R4 apply as written. Adjudicators apply this reading | The two blind passes read R2's applicability to quality claims differently (n/a against pass). Stratum Q is secondary and outside the headline rate, so the reading cannot move G1 or the headline C1 |
| 2026-09-24 | §7 full-text coding without full text (clarification during the second pass) | An article whose full text no coder can read legally keeps its screening decision (include, "I-UNCLEAR (no accessible full text)", stratum none, all verdicts n/a); full-text exclusion codes need the full text. Sent to the running second-pass agents and included in later prompts; adjudicators apply it | One second-pass coder excluded an article from its abstract. Coding instructions step 2 presupposes the full text |
| 2026-09-24 | FT-DUPLICATE tie-break for identical records (clarification before any adjudication) | When two pool records hold the same version of one article (same arXiv identifier or DOI, or the same version under two records), the record earlier in the decision order (`audit/screening/pilot_final_order.csv`; a record outside the order counts as later) carries the coding and the other is FT-DUPLICATE. Records of different versions keep the primary-version rule of `screening_codes.md` | The primary-version rule cannot choose between two records of the same version (for example P00676 and P00133, P01468 and P00141), and the coders chose differently |
| 2026-09-25 | §7 speed-stratum author review (after adjudication; Springer Nature AI policy) | The authors scored all 112 speed-stratum verdicts from the locators. Seven differ from the adjudicated coding (P00181 R1, P00647 R1 and P00827 R1 partial→fail; P00178 R2 and P01974 R2 partial→pass; P00149 R4 and P00786 R4 partial→fail). Human–adjudicated κ is 0.83, 0.85, 1.00 and 0.88 for R1–R4. The weak share would be 11/28 under the human scores and stays 8/28 in the reported rates, which remain the adjudicated records. Log: `manuscript/smo_v2/online_resources/review/` | The adjudicator used the first coder's model. The review is the human check Sect. 2.3 states. Adjudicated records are not rewritten |
| 2026-10-28 | §8 G1 framing (post hoc venue change, decided after G1) | The G1 band 20–40 % names "ACME/SMO framing". The manuscript is submitted to *Results in Engineering*, which covers all areas of engineering. The framing stays that of a specialist topology-optimization paper; claims and analyses are unchanged | The journal accepts papers that are "scientifically sound, technically correct and provide valuable new knowledge to the engineering community". The change of venue does not strengthen the framing |
