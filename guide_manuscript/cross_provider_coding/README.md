# Cross-provider blind coding check

Every coder in the audit so far is a Claude model: the first pass, the blind second pass and the adjudication. Table 5
of the paper says so ("Models were blind to one another but from one provider"). This check has models from other
providers code the same 110 records blind, from the inputs of the second pass. It measures whether the audit labels
depend on the model provider. It also settles the 17 re-screen referrals that were never read at full text.

## What the check can and cannot show

- **It can show** whether another provider's blind coding reproduces the adjudicated labels and the headline counts,
  with the agreement measures of Table 5. The headline counts are: R1 fail 8 of 28 speed claims; R1-or-R2 fail 8 of 28;
  R1-or-R2 fail-or-partial 24 of 28; R2 passed by default ("efficiency could not be determined") 15 of 28.
- **It cannot validate the labels.** Agreement between models is not correctness, and models can share errors. The
  strict review's finding 1 asks for independent expert coding; this check does not replace it. Report it as a
  cross-provider robustness check.

## Interpretation, fixed before any result

- **Provider effect.** Compare "provider vs first pass" and "provider vs second pass" with "first vs second pass" on
  the same records. Similar κ means that the provider adds no detectable shared tendency beyond coder noise. Clearly
  higher Claude–Claude agreement means that the labels are partly provider-specific; the paper must then say so.
- **Agreement with the adjudicated records** is not an accuracy score. The adjudication resolved the first-pass and
  second-pass disagreements, so each Claude pass agrees with it partly by construction. For scale: the blind second
  pass agrees with the adjudicated records at κ 0.52 on R1 and 0.47 on R2 (n = 81; printed by `--selftest`).
- **Headline counts** are reported twice for every provider: with its verdicts on the 28 adjudicated speed claims, and
  on its own speed stratum. Both carry Clopper–Pearson 95 % intervals. Compare them with 8, 24 and 15 of 28 and with
  the authors' review (11 of 28 fail R1 or R2).
- **Referrals.** The paper reports that the blind re-screen referred 9 % of the sampled excludes (17 of 188) for a
  full-text read, and it does not treat them as confirmed errors. The check gives the share of the 188 that is eligible
  at full text and passes the draw rules: a direct estimate of the false-exclusion rate.
- Every provider that returns records is reported, with every item, whatever the result. No record is dropped after
  results are seen. Invalid records are listed as skipped, or returned to the same session for a format repair only.

## Codex runs with GPT-6-Sol and GPT-6-Luna (2026-09-26)

The runs use `codex_package/` (built by `make_codex_package.py`; steps and machine facts in `codex_package/RUN.md`).
Results are collected by `collect_codex.py` into `returned/gpt-6-sol/` and `returned/gpt-6-luna/`.

Fixed before any coding run:
- **Discard rule.** A session whose event log names the project folder, a Claude or Codex home folder or the Claude
  scratch folders is discarded in full and run again in a fresh session. Other outside paths and study keywords in
  the agent's actions are reviewed by hand.
- **Within-provider references.** Sol and Luna are both OpenAI models, so Sol–Luna agreement is the OpenAI
  within-provider reference. The Claude reference is first pass vs second pass. A provider effect shows as
  cross-provider agreement (Sol or Luna vs a Claude pass) clearly below both within-provider values.
- Both models are reported whatever the result. Luna is the provider's "fast and affordable" model, so lower agreement
  for Luna alone would point to model capability, not provider.

## How to run

1. **Timing.** Run the check before the public repository release. The release publishes the coded records
   (Online Resource 3); after that, blindness rests on the agents' instructions alone.
2. **Isolation.** Give each agent a copy of `kit/` in a folder outside this repository, so the agent cannot open the
   coded records. `kit/MANIFEST.sha256` confirms that a copy is unchanged.
3. **Coding.** For each provider, use one model version. For each of the ten files `kit/queues/queue_01.txt` to
   `queue_10.txt` (11 records each), start a fresh agent session with web access and give it this prompt:
   > Read AGENT_INSTRUCTIONS.md and code every record in queues/queue_NN.txt.
4. **Referrals.** One more session per provider:
   > Read AGENT_INSTRUCTIONS.md and REFERRAL_INSTRUCTIONS.md, and check every record in referrals.csv.
5. **Collect.** Per provider, choose a tag such as `openai-gpt-5.2`. Copy every `out/P*.json` into
   `returned/<tag>/`, the referral output into `returned/<tag>/referrals.json`, and the run logs into
   `returned/<tag>/logs/`.
6. **Analyse** with base Anaconda (it has `jsonschema`; the project environment does not, and the script then checks
   only the required keys and closed values):
   ```
   C:\Users\<user>\anaconda3\python.exe -B guide_manuscript/cross_provider_coding/agreement_xprov.py
   ```
   Output: `results/xprov_summary.md` and `results/xprov_agreement.json`.

The manuscript changes only after the results exist and you decide to report them. They would add one Table 5 row per
provider and text in Sect. 2.3 and 4.3, with the new numbers entered through a registry script like
`smo/make_review_numbers.py`.

## Contents

| File | Role |
|---|---|
| `make_kit.py` | Builds the generated kit files from the repository (read-only); refuses to overwrite without `--force` |
| `kit/AGENT_INSTRUCTIONS.md` | Prompt for a coding agent: blindness and access rules, the steps of `audit/schema/coding_instructions.md`, output format |
| `kit/REFERRAL_INSTRUCTIONS.md` | Prompt for the full-text eligibility check of the 17 referrals |
| `kit/PROTOCOL_masked.md` | Byte copy of the pid-masked protocol that the second-pass coders used |
| `kit/coding_schema.json` | The coding schema, with the stage value `cross_provider_pass` added |
| `kit/screening_codes.md` | Byte copy of the screening and full-text exclusion codes |
| `kit/queues/queue_NN.txt` | The 110 records, interleaved by decision order, in the second pass's line format (bibliographic data only) |
| `kit/referrals.csv` | The 17 referrals: the fields the screeners saw, plus DOI and arXiv id; no earlier decision |
| `kit/MANIFEST.sha256` | SHA-256 of every kit file |
| `agreement_xprov.py` | Validation and analysis; `--selftest` checks the machinery against the saved passes |

## Differences from the second pass

- The stage value `cross_provider_pass` (schema copy only).
- The instructions spell out the convention that every pass applied to unreadable texts: keep the article included
  with its abstract-level code plus "(no accessible full text)", stratum `none`, all verdicts `na`.
- The instructions name the marker `R2-none-established` for an R2 pass with no establishable criterion. The first
  pass used this label; the second pass did not. It makes the "15 of 28" count recountable. The verdict rule itself
  ("unsure means pass") is unchanged.
- The blindness and access rules are written out, because the agents run outside this project.
- The referral check is new; no earlier pass read these 17 articles at full text.

## Verification (2026-09-26)

- `--selftest` (project environment and base Anaconda) reproduces exactly:
  - Table 5, first vs second pass, for all six items (n, raw agreement, κ and its bootstrap interval), from
    `evidence/agreement.json`;
  - the headline counts 8, 8, 24 and 15 of 28 from the final records;
  - the authors' review: agreement per rule (25, 26, 28 and 26 of 28) and 11 of 28 failing R1 or R2, from
    `evidence/human_review.json`.
- An end-to-end run on simulated returns (copies of the saved passes with the new stage) exercised validation,
  `--skip-invalid`, every comparison, both headline versions and the referral analysis. The simulated files were
  deleted afterwards.
- The repository validator (`audit/coding/validate_records.py`) accepts all 110 final records. In the saved second
  pass it flags two of 110: P00605 and P00983 are coded as unread (abstract only) with stratum "speed". The paper's
  agreement analysis does not validate records, so Table 5 includes both as coded.
