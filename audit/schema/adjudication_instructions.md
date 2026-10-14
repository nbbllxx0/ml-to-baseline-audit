# Adjudication instructions (AI verification; plan/PROTOCOL.md §11, 2026-09-24)

An adjudicator settles every item on which the two independent codings of one article disagree. The inputs are:
- the first coding, `audit/coding/llm_prefill/<pid>.json`;
- the blind second coding by a different model, `audit/coding/second_pass/<pid>.json`;
- the list of disagreeing items, `audit/coding/adjudication_queue.json`, written by `analysis/compare_passes.py`.

The compared items are: access, inclusion decision, full-text exclusion code, stratum, R1–R4 verdicts, and the claimed
speed-up (the two values agree when both are absent, or when they are within 10 % relative).

## Procedure

1. **Read the article yourself.** Follow the access rules below. Neither coding is the default. Decide each disputed
   item from the article text, `plan/PROTOCOL.md` §3–6 and §11, `audit/schema/coding_instructions.md` and
   `audit/schema/screening_codes.md`.
2. **Access disputes.** If either coder reached the full text, try the same legal route. If you reach the full text,
   the final record is a full-text coding. Start from the coding that used the full text, and settle its other items
   as usual. If no legal full text is reachable, the final record has `access = "abstract_only"` (or `"no_access"`)
   and all rule verdicts `na`.
3. **Build the final record.**
   - Start from the coding that you judge closer to the article.
   - Set every disputed item to your decision.
   - Update the locator and evidence text of every field you change, marking inferences "[inferred]".
   - Keep the other fields unless they contradict your decisions. For example, an exclusion needs stratum `none`
     and all verdicts `na`.
4. **Record the adjudication.** Add a top-level `adjudication` object with these fields:
   - `adjudicator_model` and `date`;
   - `based_on`: `"first"` or `"second"`;
   - `items`: one entry per disputed item. Each entry holds `first` (value), `second` (value), `decision` (value) and
     `reason` (one or two sentences, with a locator).
5. **Write** `audit/coding/records/<pid>.json` with `stage = "ai_adjudicated"` (Write tool, valid JSON). Never
   change the two input codings.
6. **Validate** with `python -m audit.coding.validate_records records <pid> ...`, run from the project root with
   base Anaconda, which has jsonschema.

## Rules that decide frequent disputes

- **No full text, no full-text exclusion.** An article whose full text no coder could read legally keeps its
  screening decision: include, reason "I-UNCLEAR (no accessible full text)", stratum `none`, all verdicts `na`.
- **Unsure means pass** for R1–R4, which is the template convention. Use `partial` only for the partial cases that
  §5.3 lists.
- **Primary outcome** (§5.1): the first quantitative comparison with a classical method, in this order: abstract,
  then conclusion, then introduction, then main text. Otherwise, the first qualitative comparison. The stratum
  follows the primary outcome: `speed` if it compares speed, cost or a proxy for them; `quality` if it compares
  design quality only.
- **Full-text exclusions** use the closed list in `screening_codes.md`. When several apply, use the first in table
  order.
- **FT-DUPLICATE** marks the non-primary version. The primary version is the version of record if it is open access;
  otherwise it is the latest arXiv version. Name the other pool id in `notes`.
- **Stratum Q (quality-only primary outcome)** (PROTOCOL §11, 2026-09-24): R3 is `na`; R2 is `na` unless criterion
  (b) applies (the abstract reports a weaker baseline than the results or appendix); R1 and R4 apply as written.

## Access rules

- Use legal copies only: arXiv, the publisher's open-access version (including its own file host), institutional or
  funder repositories, and author pages.
- Never bypass a CAPTCHA, a bot check, a login or a paywall.
- Send no personal data: use a generic User-Agent, and no email, `mailto`, Unpaywall, API keys or logins.
- Keep downloads in a scratch folder outside the project, and delete them afterwards.

## Duplicate tie-break (PROTOCOL §11, 2026-09-24)

When two pool records hold the same version of one article, the record earlier in the decision order
(`audit/screening/pilot_final_order.csv`; a record outside the order counts as later) carries the coding, and the
other is FT-DUPLICATE. Records of different versions keep the primary-version rule.
