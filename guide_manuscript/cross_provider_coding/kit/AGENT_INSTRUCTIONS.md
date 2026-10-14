# Blind coding pass: instructions for the coding agent

You are one independent coder in a blind coding pass of a pre-registered audit. The audit covers articles that use
machine learning for topology optimization. For each article in your queue file you read the full text and fill one
record, following the protocol in this folder. Your records are compared with other coders' records only after all
coding is finished.

## Files in this folder

| File | Use |
|---|---|
| `PROTOCOL_masked.md` | The pre-registered protocol. Apply §3–6. The §11 deviations log is part of the protocol: its clarifications apply. Pool ids inside the protocol are masked as `P#####`. |
| `coding_schema.json` | The record format. One JSON record per article. |
| `screening_codes.md` | Closed code lists. The second table gives the full-text exclusion codes. |
| `queues/queue_NN.txt` | Your articles, one line each: pool id, decision-order position, title, DOI, arXiv id, an open-copy link if one is known, and the result of an earlier automated access check. |

The user tells you which queue file is yours.

## Blindness rules

1. Use only the files in this folder and the articles' own texts.
2. Do not open, search for or read anything that reports how this study coded or judged these articles:
   - other coding records or other agents' output;
   - any manuscript, preprint, supplement, online resource or code repository of this study, for example a preprint
     titled "How the Classical Baseline Shapes Machine-Learning Speed Claims in Topology Optimization".
   If you meet such material by accident, stop reading it, do not use it, and report it in the run log.
3. Do not share your records with anyone until the user collects them.

## Access rules (protocol §7 and §11)

- Read the full text only from a legitimate open source:
  - arXiv: `https://arxiv.org/html/<id>` or `https://arxiv.org/pdf/<id>`;
  - the open-copy link in the queue line;
  - an open-access version of record, including a copy on the publisher's own file host;
  - an institutional or author repository copy.
- Never bypass a paywall, a login, a CAPTCHA or a bot check. Never use a shadow library.
- Do not save article PDFs in this folder. Records hold identifiers, locators, paraphrases and at most one short
  verbatim phrase.

## Steps for each article

1. **Access.** Record `access` and `citation.version_coded`. If no full text is reachable under the access rules:
   - set `access` to `"abstract_only"` (the abstract is readable) or `"no_access"`;
   - set `included.decision` to `"include"`, and `included.reason` to the title/abstract code that fits the abstract
     (`I-SPEED`, `I-QUALITY` or `I-UNCLEAR`, see `screening_codes.md`) followed by `(no accessible full text)`;
   - set `included.stratum` to `"none"` and every rule verdict to `"na"` with evidence `"no full text"`;
   - stop there for this article.
2. **Full-text inclusion.** Check the article against protocol §3 and §4. If it fails them:
   - set `included.decision` to `"exclude"` and `included.reason` to exactly one code from the full-text exclusion
     table (for example `FT-FORWARD`); when several apply, use the first in the table order;
   - set `included.stratum` to `"none"` and every rule verdict to `"na"`;
   - put any explanation in `notes`, then stop for this article.
3. **Primary outcome** (protocol §5.1), in this order:
   1. the first quantitative comparison with a **classical** method in the abstract;
   2. otherwise in the conclusion, then the introduction, then the main text;
   3. otherwise the first qualitative comparison, in the order abstract, conclusion, introduction.
   - Write `claim.primary_outcome_paraphrase` in your own words and give its `location`.
   - Give at most one verbatim `key_phrase`, shorter than 15 words.
   - Record other candidates in `claim.alternatives`.
   - Set `included.stratum` to `"speed"` if the primary outcome compares speed, cost or a proxy for them, or to
     `"quality"` if it compares design quality only.
4. **Baseline facts.** Fill every `baseline` field the article states. Write `"not stated"` when a fact is absent;
   never guess.
   - Report numbers exactly as printed, with units.
   - If a speed-up factor is stated, or can be derived as classical time ÷ ML time from printed numbers, put it in
     `claim.claimed_speedup` and explain the derivation in `claim.claimed_speedup_basis`.
5. **Rules R1–R4** (protocol §5.3). Give each rule a verdict (`pass`, `partial`, `fail` or `na`) and name the
   protocol marker that applies, for example `R2(c)`, `R1-unmatched`, `R3-no-data-cost` or `R4-image-metric`.
   - `evidence` is a locator plus a paraphrase.
   - **Unsure means pass** (template convention). Use `partial` only for the partial cases the protocol lists.
   - R2 markers (a) and (e) need a re-test or a per-iteration time. Without them, use (b), (c) or (d) only when the
     article's own text establishes them. Otherwise R2 is `pass` or `partial`.
   - When no R2 criterion can be established from the text, R2 is `pass` with the marker `R2-none-established`.
6. **Reporting indicators** (protocol §6). Fill every field.
7. **`retest_candidate`.** `true` only if public code exists, the article's benchmark can be run, and nothing
   forbids running it.

Set these fields in every record:
- `stage`: `"cross_provider_pass"`;
- `coder.llm_model`: the exact model name and version that your provider shows;
- `coder.llm_date`: today's date as `YYYY-MM-DD`;
- `coder.human_initials` and `coder.human_date`: `null`.

## Style and limits

- Paraphrase. Use at most one verbatim phrase per article, shorter than 15 words.
- Do not state an inference as a fact. Mark inferences `[inferred]` inside the evidence text.
- Give every numeric field a locator (section, table, figure or page).

## Output

- One file per article: `out/<pid>.json`, for example `out/P99999.json` for a record with pid `P99999`. The file
  holds one JSON object that is valid against `coding_schema.json`, and its `pid` equals the file name.
- One run log: `out/RUN_LOG.md`. Give the model name and version, the date, and the queue file. Then give one line per
  article: pid, the source you read (URL), and any problem, such as an unreachable text or an unclear rule. Report
  any accidental contact with material covered by the blindness rules.
- Code every line of your queue. If you must stop early, keep the records you finished and list the rest in the run
  log as not coded.
