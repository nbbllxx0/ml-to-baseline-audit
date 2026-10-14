# Full-text eligibility check: instructions for the agent

`referrals.csv` lists 17 records from the literature pool of a pre-registered audit. The audit covers articles that
use machine learning for topology optimization. For each record, decide at full text whether the article meets the
audit's eligibility criteria. The blindness rules and access rules of `AGENT_INSTRUCTIONS.md` apply here unchanged.

## Criteria

Apply protocol §3 (inclusion) and §4 (exclusion) in `PROTOCOL_masked.md`, with the clarifications in its §11
deviations log. Use the code lists in `screening_codes.md`.

## Steps for each record

1. **Access.** Read the full text through a legitimate open source (see `AGENT_INSTRUCTIONS.md`). Use the DOI, the
   arXiv id or the title to find it.
2. **Decision.**
   - The article meets §3 and §4: `decision` is `"include"`, and `code` is `I-SPEED` if its first comparison with a
     classical method (protocol §5.1) concerns speed, cost or a proxy for them, or `I-QUALITY` if it concerns design
     quality only.
   - The article fails §3 or §4: `decision` is `"exclude"`, and `code` is exactly one full-text exclusion code
     (`FT-...`); when several apply, use the first in the table order.
   - No full text is reachable: decide from the abstract with the title/abstract codes (`I-...` or `E-...`), and
     set `access` to `"abstract_only"`.
3. **Rationale.** One or two sentences in your own words, with a locator (section, figure or page). No quotation
   longer than 15 words.

## Output

One file, `out/referrals.json`: a JSON list with one object per record, in this form (`P99999` is a placeholder, not
a record of the list):

```json
{"pid": "P99999", "access": "full_text", "decision": "<include or exclude>", "code": "<one code>",
 "rationale": "<locator>: <one or two sentences in your own words>",
 "llm_model": "<exact model name and version>", "llm_date": "YYYY-MM-DD"}
```

`access` is `"full_text"`, `"abstract_only"` or `"no_access"`. Give all 17 records. Add the source you read for each
record to `out/RUN_LOG.md`, with any problem.
