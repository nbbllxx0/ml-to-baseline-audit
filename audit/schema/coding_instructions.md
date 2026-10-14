# Full-text coding instructions (first AI pass; a blind second AI pass and AI adjudication follow)

Apply `plan/PROTOCOL.md` §3–6 to one included article. Fill one record that follows `audit/schema/coding_schema.json`,
with `stage = "llm_prefill"` and `coder.human_initials = null`.

## Steps

1. **Access.** Read the full text: arXiv HTML (`https://arxiv.org/html/<id>`) or the PDF (`https://arxiv.org/pdf/<id>`),
   or the version of record if it is open access.
   - Record `access` and `citation.version_coded`.
   - If only the abstract is reachable, set `access = "abstract_only"` and do not assign rule verdicts; use
     `verdict = "na"` with evidence "no full text".
2. **Full-text inclusion.** Confirm §3 and §4. If the article fails them, set `included.decision = "exclude"` with
   `reason = FT-<short reason>`, and stop after the citation and the reason.
3. **Primary outcome** (§5.1), in this order:
   1. the first quantitative comparison with a **classical** method in the abstract;
   2. otherwise in the conclusion, then the introduction, then the main text;
   3. otherwise the first qualitative comparison, in the order abstract → conclusion → introduction.
   - Write `claim.primary_outcome_paraphrase` in your own words.
   - Give its `location`. Give at most one verbatim `key_phrase` (< 15 words).
   - Record other candidates in `claim.alternatives`.
   - Set `included.stratum`: `speed` if the primary outcome compares speed, cost or a proxy for them; `quality` if it
     compares design quality only.
4. **Baseline facts.** Fill every `baseline` field the article states. Write "not stated" when absent. Never guess.
   - Report numbers exactly as printed, with units.
   - If a speed-up factor is stated, or can be derived as classical time ÷ ML time from printed numbers, put it in
     `claimed_speedup` and say how it was derived in `claimed_speedup_basis`.
5. **Rules R1–R4** (§5.3). Set a verdict for each and name the protocol `marker` that applies, e.g. `R2(c)`,
   `R1-unmatched`, `R3-no-data-cost`, `R4-image-metric`.
   - `evidence` = locator + paraphrase.
   - **Unsure means pass** (template convention). Use `partial` only for the partial cases the protocol lists.
   - R2 markers (a) and (e) need our re-test or a per-iteration time. Without them, use (b), (c) or (d) only when the
     article's own text establishes them. Otherwise R2 is `pass` or `partial`.
6. **Reporting indicators** (§6). Fill every field.
7. **retest_candidate.** true only if public code exists, the article's benchmark can be run, and nothing forbids
   running it.

## Style and limits

- Paraphrase. At most one verbatim phrase per article, under 15 words.
- No inferences stated as facts. Mark inferences "[inferred]" inside the evidence text.
- Numbers must be traceable: every numeric field gets a locator.
- Output valid JSON only, one file per article: `audit/coding/llm_prefill/<pid>.json`.
