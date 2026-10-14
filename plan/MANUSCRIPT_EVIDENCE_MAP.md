# Manuscript–evidence map (pair plan)

Every manuscript element on the left is paired with the evidence that must exist before that element is written. An
element may be drafted only when its evidence row shows **ready**.
- Every number in the manuscript is registered in `evidence/numbers.json`, with its source file and producing script.
- `python tools/numbers.py check <draft>` fails if a manuscript `[[Nxxx]]` token is unregistered or its source file is
  missing. Numbers are registered by the analyses (`analysis/register_numbers.py` for the re-test).

Target format: *Nature Machine Intelligence* Analysis.
- Main text ≤ 3,500 words; abstract 100–150 words, unreferenced.
- ≤ 6 display items; about 50 references.
- Structure: Introduction (no heading), Results, Discussion, Methods.

Fallback: *Nat. Comput. Sci.* or *Nat. Commun.*, then ACME long form. The ACME version adds a full per-paper narrative
and needs no new evidence.

**Status keys:** `todo` · `running` · `ready` (evidence exists and passed its check) · `frozen` (hash in
`evidence/MANIFEST.sha256`) · `blocked:<reason>`.
**Gates** (defined in `plan/PROTOCOL.md` §8): **G1** decides the framing; **G2** decides whether the re-test is a
headline.

---

## 1. Identifiers

| Kind | IDs | Where they live |
|---|---|---|
| Claims | C1 audit share · C2 re-test deflation · C3 break-even and energy · C4 reporting biases · C5 (secondary) agreement between two independent AI codings · S-LLM (stratum) LLM-agent TO papers | this map; `plan/PROTOCOL.md` |
| Numbers | N001… | `evidence/numbers.json` |
| Display items | F1–F6 (main) · ED1–ED10 (Extended Data) · T1 (rules table, inside Methods) | `figures/`, `analysis/` |
| Evidence artefacts | paths below | `audit/`, `retest/`, `env/`, `evidence/` |

## 2. Front matter

| Manuscript element | Content | Evidence required | Producing step | Check | Status |
|---|---|---|---|---|---|
| Title | Neutral title before G1 and G2; the conditional title applies only if C1 and C2 hold (drafts in the scan report §6.5) | G1, G2 outcomes | `analysis/gates.py` → `evidence/gates.json` | The title's claim matches the gate outcomes | ready: G1 decided ([[N011]], ACME/SMO band under every coding); neutral title kept; target SMO |
| Abstract | N screened and included; share failing ≥ 1 rule with 95 % CI; K re-tests; median speed-up before and after; break-even before and after | N001–N012 | `analysis/*` | `tools/numbers.py check` | ready: drafted from registered numbers (verified records; HGTO and OAT re-tests) |

## 3. Introduction (no heading, about 450 words)

| Para | Claim made | Evidence required | Source | Status |
|---|---|---|---|---|
| I-1 | ML is reported to accelerate structural TO, often by large factors | Distribution of **claimed** speed-ups across included papers (median, range), N013–N015 | `audit/coding/records/*.json` (AI double-coded, agreed or adjudicated) → `analysis/claims.py` | ready: N013–N015 from verified records |
| I-2 | Speed claims are only as good as the baseline; the fluid-PDE audit found 79 % (60/76) weak baselines | Citation to McGreivy & Hakim (quoted numbers verified 2026-09-24) | the task record §6.1 | ready |
| I-3 | TO adds two issues the fluid rules miss: offline data-generation cost (R3) and verification of the returned design (R4) | Rule definitions; the OAT break-even example (168 + 16 H100-days → 2.32 M uses) | `plan/PROTOCOL.md` §5; task record §6.2 | ready |
| I-4 | What we did, and the headline numbers | N001–N012 | as in the abstract | ready: N009, N010 and the re-test outcomes |

## 4. Results

### R-1 "Most ML-for-TO speed and quality claims rest on weak comparisons" → C1

| Element | Evidence | Producing step | Check | Status |
|---|---|---|---|---|
| Counts: records found, screened, full-text, included, claiming to outperform (N001–N004) | `audit/search/raw/*.json`, `audit/screening/screening.csv`, PRISMA counts | `audit/search/run_queries.py`, LLM pre-screen + `audit/screening/merge_and_pilot.py`, `analysis/prisma.py` (not yet written) | The counts add up; every exclusion has a code (screening: `audit/schema/screening_codes.md`; full text: closed FT list) | ready: N001–N004 and N084–N087 (`evidence/prisma.json`); blind re-screen N066, N067 |
| Share failing R1, R2, R3, R4 and ≥ 1 rule, with Clopper–Pearson 95 % CI (N005–N009) | `audit/coding/records/*.json` (AI double-coded, agreed or adjudicated; sample = decision order 1–200) | `analysis/rules.py` | Every verdict has a locator and a verifier initial | ready: N005–N010 (`evidence/c1_rules.json`, 110 verified records: 44 agreed, 66 adjudicated); G1 N011; scale sensitivity N012; per-coder range N081–N083 (post hoc) |
| **F1** Screening flow plus Sankey (baseline type → verdict) | as above | `analysis/fig_audit.py` (flow; Sankey after verification) | Figure data CSV saved next to the figure | ready: flow in `figures/f1_flow.png` (verified); Sankey not made |
| **F2** Rule verdicts by year and by venue tier | as above | `analysis/fig_audit.py` (by year; venue tier after verification) | same | ready: by year, `figures/f2_rules_by_year.png`; venue tier not made |
| S-LLM stratum: the same rates for LLM-agent TO papers | coding records with `method_family = llm_agent` | `analysis/rules.py --stratum llm` | n reported; no CI if n < 5 | ready: `evidence/ed5_llm_stratum.json` (small n; descriptive) |

### R-2 "Strong classical baselines shrink reported speed-ups" → C2

| Element | Evidence | Producing step | Check | Status |
|---|---|---|---|---|
| Strong-baseline correctness | `retest/baseline/tests/` report: element stiffness spectrum, patch test, CPU–GPU agreement, true residual | `retest/baseline/tests/run_tests.py` → `evidence/baseline_tests_gpu.json`, `evidence/baseline_tests_pardiso.json` | All gating tests pass | ready (the isolated-void stress test is non-gating and recorded) |
| Strong-baseline timing (G2) | `retest/runs/<run_id>/record.json` with per-iteration timings, CG counts, true residuals, energy trace | `retest/baseline/bench.py` (pinned runs `retest/runs/*_pinned/`) → `analysis/baseline_summary.py` → `evidence/g2_provisional.json` | Warm-up excluded and reported; three repeats; median and spread; CPU pinning recorded | ready (provisional G2, headline band) |
| Per-target re-test: the target's own method and our strong baseline on the same problems, same machine | OAT (target 1, approved): `evidence/oat_retest_summary.json` (pinned, primary), `*_default_sched.json` (sensitivity), `evidence/oat_eval_n{64,256}.json` | `retest/oat_harness/run_pinned_retest.sh`, `run_pinned_scoring.sh` | Same NITO_test problems, boundary conditions, volume fraction and resolution; OAT commit dc5e817 recorded; OAT's own evaluator | ready for OAT; targets 2–3 not approved |
| Claimed vs re-tested speed-up per paper (N016–N020) | re-test records plus coding records | `analysis/register_numbers.py` (OAT); `analysis/speedups.py` (not yet written) | Claimed values carry locators; re-tested values carry run IDs | partial: OAT only (N016–N020, N039) |
| Re-test target 2: HGTO (P00512), six linear 2D configurations, same machine | Runs `retest/runs/hgto/<method>/<config>/r<k>`; equivalence gate `evidence/hgto_gate.json` (port vs authors' SIMP–OC: within 1e-10, equal update counts); summary `evidence/hgto_retest.json` | `retest/hgto_harness/campaign.py` (pre-registered in BASELINE_PREREG §9) → `analysis/hgto_summary.py` (N068–N076) | Every design scored by HGTO's own independent evaluator; published values kept separate | ready: HGTO 4.9× / 10.8× faster than its two-thread SIMP–OC (article 4.2× / 9.6×); the GPU port of the same SIMP–OC converges faster than HGTO (HGTO takes 2.6× / 1.9× as long) with stiffer designs; draft C2 subsection written |
| Re-test target 3: P00150 predictor, 100 validation problems | `evidence/p00150_check.json`; diagnosis in `retest/runs/p00150/_diagnosis/` | `retest/p00150_harness/` (pre-registered in BASELINE_PREREG §9) | Reconstruction check: stored top88 compliance within 1 % on ≥ 95 of 100 cases | not reconstructed: check failed ([[N077]] within 1 %, needed 95; stored values up to [[N078]] lower); no re-test reported, as pre-registered |
| **F3** Claimed vs re-tested speed-up (log–log, arrows) | as above | `analysis/fig3_f5.py` | data CSV `figures/data/f3_speedup.csv` | partial: OAT only, `figures/f3_speedup.png` |
| **F4** Time-to-quality curves at 64² and 256² | fresh runs at fixed budgets (`retest/oat_harness/time_to_quality.py`), scored by OAT's evaluator; `evidence/ttq_summary.json` | `analysis/ttq_summary.py`; `analysis/fig_retest.py` panel c | Every design scored by the same FE evaluator as OAT's output; volume condition applied (BASELINE_PREREG §9) | ready for OAT at 64² and 256² (N018, N039) |

### R-3 "Counting data generation moves the break-even" → C3

| Element | Evidence | Producing step | Check | Status |
|---|---|---|---|---|
| Break-even τ recomputed from the papers' own cost statements and measured C_SIMP, C_inference (N021–N024) | coding records (R3 fields with locators); re-test timings; `evidence/breakeven.json` | `analysis/breakeven.py` | Formula τ = C_train/(C_SIMP − C_inf) as published (OAT App. G); no hardware conversion, hardware named per row | ready for OAT (N021–N024, N050); other papers need coded R3 fields |
| Energy per design, GPU board power (N025–N026) | `retest/runs/*_power/power_*.csv` + `.window.json`; `evidence/energy.json` | `tools/energy.py` + `analysis/energy.py` | `power.draw.instant` every 100 ms, trapezoid over the exact window (BASELINE_PREREG §9); board energy primary | ready for OAT (N025–N026); CPU energy not measured |
| **F5** τ against resolution; energy per design | as above | `analysis/fig3_f5.py` | data from `evidence/breakeven.json`, `evidence/energy.json` | ready for OAT: `figures/f5_breakeven_energy.png` |

### R-4 "Reporting practices hide negative results" → C4

| Element | Evidence | Producing step | Check | Status |
|---|---|---|---|---|
| Positive-claim share; selective runtime reporting; failure-rate reporting; seeds; out-of-distribution tests; code and data availability (N027–N034) | coding records, reporting block | `analysis/reporting.py` | Definitions in the protocol, §6 | ready: N027–N034 (`evidence/reporting.json`) |
| **F6** Reporting panel plus fair-comparison checklist | as above plus `plan/CHECKLIST.md` (drafted) | `analysis/reporting.py` + `analysis/fig_audit.py` | — | ready: `figures/f6_reporting.png`; checklist in the draft |

### R-5 (secondary, Extended Data) "An LLM can pre-code the audit but not replace the coder" → C5

| Element | Evidence | Producing step | Check | Status |
|---|---|---|---|---|
| Agreement between the first AI coding and the blind second AI coding (different model), per rule, as Cohen's κ (N035–N038) | `audit/coding/llm_prefill/*.json` against `audit/coding/second_pass/*.json` | `analysis/agreement.py` | Each first-pass coding is frozen (hash) before the blind second pass runs | ready: N035–N038, N079, N080 (`evidence/agreement.json`); post hoc speed-stratum κ (`evidence/agreement_posthoc.json`) |
| (dropped) Human second coder | — | — | replaced by the blind AI second pass (PROTOCOL §11, 2026-09-24) | n/a |

## 5. Discussion (about 600 words; no new numbers)

| Point | Evidence | Status |
|---|---|---|
| What the audit does not claim: it does not claim ML-for-TO has no value (diversity, differentiable priors, out-of-distribution design, democratization as argued in OAT App. G) | citations; the OAT App. G argument | ready |
| Recommendations: the fair-comparison checklist | `plan/CHECKLIST.md` (draft after coding) | ready: drafted in the Discussion |
| Limitations: English only; full-text-available bias; one machine; single primary coder; rules need judgment | protocol, deviations log | ready: drafted (coding reliability, R2 needs re-tests, re-tests outside the sample) |

## 6. Methods (online; no word limit in practice)

| Section | Evidence | Status |
|---|---|---|
| M-1 Search: sources, queries, dates | `audit/search/queries.json` v1.2 (frozen), `audit/search/raw/`, PROTOCOL §11 rows (FC1 anchor fix, BC3 bibliography) | evidence ready; drafted in `manuscript/draft_v0.md` |
| M-2 Screening and inclusion | `plan/PROTOCOL.md` §3–4; `audit/screening/screening.csv` | frozen once hashed |
| M-3 Primary outcome and rules R1–R4 (Table T1) | `plan/PROTOCOL.md` §5 | frozen once hashed |
| M-4 Coding procedure, LLM pre-extraction, verification, reliability | `plan/PROTOCOL.md` §6–7 | frozen once hashed |
| M-5 Strong baseline: formulation, solvers, stopping rules, pre-registration | `plan/BASELINE_PREREG.md`; `retest/baseline/` | frozen once hashed |
| M-6 Re-test protocol: hardware, timing, CPU pinning, energy, matched quality, evaluator definition, MultiGrid environment fault | `env/2026-09-24_env.json`; `retest/baseline/bench.py`; `tools/pin.py`; `tools/energy.py`; `plan/BASELINE_PREREG.md` §9 | evidence ready; text todo |
| M-7 Statistics | `analysis/stats.py` | ready: Clopper–Pearson and bootstrap κ in `analysis/rules.py`, `analysis/agreement.py` |
| M-8 Data and code availability | `evidence/MANIFEST.sha256`; the release plan (public only with user approval) | ready: drafted; release once the arXiv version is online (user, 2026-09-25); details later |

## 7. Extended Data

| ID | Content | Evidence | Status |
|---|---|---|---|
| ED1 | Per-paper verdict table: rule verdicts, locators, one short key phrase each | coding records | ready: `figures/data/ed1_verdicts.csv` (verified) |
| ED2 | Baseline correctness: stiffness spectrum, patch test, CPU–GPU agreement, true-residual histogram | `evidence/baseline_tests_gpu.json`, `evidence/baseline_tests_pardiso.json`, `evidence/baseline_equivalence.json`; `figures/ed2_baseline_correctness.png` | ready |
| ED3 | Strong-baseline scaling from 64² to 1024²: time per iteration, CG iterations | pinned bench runs; `figures/ed3_scaling.png` | ready (GPU; PARDISO to 256² only, see `run_extra_runs.sh`) |
| ED4 | Sensitivity of the rule verdicts to the three-point-scale convention (unsure counted as pass or as fail) | `analysis/fig_audit.py` → `evidence/ed4_sensitivity*.json` | ready: `evidence/ed4_sensitivity.json`; N012 |
| ED5 | S-LLM stratum details | `analysis/fig_audit.py` → `evidence/ed5_llm_stratum*.json` | ready: `evidence/ed5_llm_stratum.json` (descriptive) |
| ED6 | Agreement between two independent AI codings (C5) | `analysis/agreement.py`, `evidence/pass_comparison.json` | ready: κ table (`evidence/agreement.json`) and per-coder range (`evidence/coder_sensitivity.json`) |
| ED7 | OAT arithmetic note, stated neutrally: (i) Table 6 times SIMP at 150 steps, §4.4 mentions 200–500 iterations for a full run; (ii) the App. G formula applied to Table 6 times gives τ = 0.23 M at 256², against the 2.32 M the paper states without listing its inputs. Both values are reported; neither is called an error. No author contact (author decision, 2026-09-24) | task record §6.2; `evidence/breakeven.json` | ready (wording in `manuscript/draft_v0.md`, C3) |
| ED8 | Environment: GPU, driver, CPU, library versions | `env/2026-09-24_env.json`; BASELINE_PREREG §9 (OAT env) | evidence ready |
| ED9 | Timing sensitivity to CPU placement: pinned (primary) against default scheduling | `evidence/*_default_sched.json`; `retest/runs/_probes/scheduling_2026-09-24/`; `figures/ed9_scheduling.png` | ready |
| ED10 | HGTO re-test: converged wall time against mesh size for HGTO, the authors' SIMP–OC (2 and 6 threads) and the GPU port; ratios to HGTO; article values hollow | `analysis/fig_hgto.py` → `figures/ed10_hgto.png`, `figures/data/ed10_hgto.csv` | ready |

## 8. Presentation extras (not in the journal page limit)

| Item | Evidence | Status |
|---|---|---|
| Interactive, sortable audit table (companion web page) | `evidence/audit_table.json` | todo; publishing needs user confirmation |
| Strong-baseline code release (MIT or BSD-3, the user's choice) | `retest/baseline/` | todo; release needs user confirmation |

## 9. Gate log

| Gate | Definition (frozen in the protocol) | Provisional value | Final value | Date |
|---|---|---|---|---|
| G1 | Share of 20 pilot primary outcomes failing R1 or R2: ≥ 40 % → NMI framing; ≥ 20 % and < 40 % → ACME/SMO framing; < 20 % → stop the audit | Provisional arXiv pilot plus top-ups, LLM prefills, none verified: 10/20 = 0.50 (95 % CI 0.27–0.73) as coded; 8/20 = 0.40 (0.19–0.64) with the flagged no-baseline candidates dropped. Both in the NMI band; the second sits on the threshold | 25 % (5/20; 95 % CI 9–49 %) on the first 20 speed-stratum records of the decision order, coded twice by language models and agreed or adjudicated (N011, `evidence/gates.json`): ACME/SMO band. Cell closed 2026-09-25 UTC, recording the value already reported | 2026-09-25 |
| G2 | Strong-baseline time for a 150-iteration SIMP run at 256², against OAT's reported 68.30 s: ≤ 13.66 s → headline; > 13.66 s and < 68.30 s → moderate; ≥ 68.30 s → fair case | P1 4.34 s, P2 4.51 s (GPU, pinned; standard formulation; cross-hardware): headline | 8.45 s on OAT's own problems (NITO test split, GPU, pinned, 150 iterations, loop only, median of 5; N043): ≤ 13.66 s → headline. OAT's 68.30 s is 8.1× longer (N104; cross-hardware). Cell closed 2026-09-25 UTC for SMO v2 | 2026-09-25 |

**Provisional G2** uses the pre-registered standard formulation. **Final G2** uses OAT's own generator settings, after
the download is approved.
