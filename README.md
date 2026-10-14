# ml-to-baseline-audit

Code and data for:

> Shaoliang Yang and Jun Wang (2026). *How the Classical Baseline Shapes Machine-Learning Speed Claims in Topology
> Optimization.* arXiv:2610.16051. https://doi.org/10.48550/arXiv.2610.16051

The study re-runs released code for eight machine-learning topology-optimization methods on one workstation, two of
them in depth (Optimize Any Topology and HGTO) and six from a census of code-linked claims, and audits a random sample
of published speed comparisons with language-model coding. This repository holds the audit records, the analysis and
re-test scripts, the run summaries behind every reported number, the figure data and the six Online Resources.

## Layout

Paths keep the layout of the working project, so scripts resolve their inputs relative to the repository root.

| Folder | Contents |
|---|---|
| `online_resources/` | Online Resources 1–6 (`ESM_1.pdf` … `ESM_6.pdf`) and the machine-readable table of Online Resource 3 (`ESM_3.csv`) |
| `plan/` | Audit protocol and baseline pre-registration with dated deviation logs (`PROTOCOL.md`, `BASELINE_PREREG.md`), checklist and evidence map |
| `audit/search/` | Search queries and the scripts that ran them and built the record pool |
| `audit/pool/` | Pooled, de-duplicated records (2,591 unique records); abstracts removed, identifiers kept |
| `audit/screening/` | Language-model screening batches, screening table, blind re-screen and sampling order |
| `audit/coding/` | Coding records (one JSON per accessible article), second-pass and adjudication batches, access lists, schema validation |
| `audit/schema/` | Coding schema and the instructions given to the coding and adjudicating models |
| `guide_manuscript/cross_provider_coding/` | Post hoc blind coding by models from another provider: kit, instructions, returned codings and agreement results |
| `analysis/` | Scripts that turn the records and runs into the evidence files, tables and figure data |
| `evidence/` | Evidence files behind the reported numbers, the number registry (`numbers.json`) and the append-only hash log (`MANIFEST.sha256`) |
| `retest/` | Re-test harnesses for the classical baselines, OAT, HGTO and the stopped Halle et al. reconstruction, with run summaries and logs |
| `v3/` | Census of code-linked claims: frame, pre-registration (`v3/plan/CENSUS_PREREG.md`), per-claim run records, evidence and recorded upstream commits |
| `v4/` | Coder-comparison evidence (model passes, adjudication and the authors' review) and its number registry |
| `v9/smo/` | Scripts that draw the paper's figures and write its number file, with figure data |
| `figures/` | Figure data (CSV) and working figures from the analysis scripts |
| `tools/`, `env/` | Shared helpers (hash pinning, number registry, energy sampling) and the captured software environment |

## What is not included

- **Article texts.** Audited articles are listed with DOIs and locators in Online Resource 3; their texts are not
  redistributed. Coding records quote short phrases as locators only.
- **Abstracts.** The pooled records keep titles, authors, venues and identifiers; the abstract column is empty.
  The raw API responses of the search are not included.
- **Third-party code, data and weights,** including OAT, whose repository has no licence file. `THIRD_PARTY.md` lists
  every source with the commit used. Scripts that call this code expect it in `retest/targets/` or `v3/third_party/`.
- **Bulky run arrays** (design snapshots and density fields in `.npz`, `.npy` and `.pt` files). Run summaries,
  timings and logs are included; the arrays (about 0.5 GB) are left out for size.

## Checking the records

- The pre-registrations were fixed before the runs they govern. `evidence/MANIFEST.sha256` (and
  `v3/evidence/MANIFEST.sha256` for the census) records a SHA-256 hash of each plan version with its date; the plan
  files here match their latest recorded hashes. Some rows of the logs refer to files that are not released: working
  drafts, and in the census log the patched upstream files listed in `THIRD_PARTY.md`.
- Files listed in a hash log are released byte-identical, so a few of them still show local Windows paths. In other
  files, the local user folder is written as `C:\Users\<user>`.
- The manuscript's result macros resolve through `v9/smo/numbers.tex` to registered values with notes on their source:
  `evidence/numbers.json`, `v3/evidence/numbers_v3.json`, `v4/evidence/numbers_v4.json` and
  `v9/smo/numbers_*.json`.
- The hardware and software of the timed runs are in `env/2026-09-24_env.json` and Online Resource 2.

## Licences

Code: MIT (`LICENSE`). Records, evidence, run summaries, figure data and the Online Resources: CC BY 4.0
(`LICENSE-DATA.md`). A few files contain MIT-licensed upstream code; they are listed in `THIRD_PARTY.md`, with the
upstream licence texts in `licenses/`. Other third-party material is excluded.

## Citation

Please cite the paper (see `CITATION.cff`).
