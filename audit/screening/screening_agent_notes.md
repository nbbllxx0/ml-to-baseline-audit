# Notes from the LLM screening agents (batches 5–13), for the screening check

These notes summarize what the screening agents reported in their final messages on 2026-09-24. They are prompts for
the screening check (`audit/screening/human_check_priority.csv`), not decisions. Every pid below is an LLM screening
result. Since 2026-09-24 the check is a blind AI re-screen of the sampled excludes (PROTOCOL §11).

## Conventions that differ between batches (exclusions only; includes are unaffected)

- **Off-topic reviews, theses and conference abstracts.** Batches 6, 7 and 10 coded them E-TYPE; batches 1 and 8 used
  E-SCOPE or E-DOMAIN for some. Both are exclusions. The flow diagram (F1) should report them together or after
  recoding to one convention.
- **Non-English dissertations.** Coded E-TYPE, not E-OTHER, in batches 7, 9, 10 and 11 (for example P01185, P01187,
  P01632, P01656, P01769, P01784, P01847, P02007, P02060, P02194). Also exclusions either way.
- **Pre-2017 records.** Batch 12 coded 67 of them E-OTHER with the rationale "Pre-2017 (YYYY)". The decision order
  also applies the §3.4 date window mechanically (PROTOCOL §11 row).
- **Preprints on servers other than arXiv** (Zenodo, SSRN, Research Square, Preprints.org). Several batches screened
  them on content. The decision order drops them under §3.3 (54 records; `audit/screening/pilot_final_date_excluded.json`).
- **Elastic-wave, phononic and seismic metamaterials.** Kept in scope in every batch, following batches 2–4.
  Airborne sound was excluded as acoustic (for example P00653, P00680, P00708, P00720, P00723, P00733). PROTOCOL §11
  (2026-09-24) settles this: "acoustic" means sound in fluids, and elastic-wave problems are in scope.

## Likely duplicates the automatic flags missed (check at screening or full text)

- P01842 / P01843 (same abstract); P01900 / P01929; P01907 / P01938; P01905 / P01942 (P01942 is a code repository).
- P02095 / P02096; P02250 / P02282; P02281 / P02289.
- P00665 / P00712 (both "DL-Scale"); P00647 / P00767 (3D CNN on gyroid cells).
- P00994 appears to be the conference version of P00830.
- P01394 may be the journal version of P00035 (inferred by the agent, not verified).
- P01149 / P01271 (journal and SSRN versions).
- P01559 / P01744 (both excluded anyway).
- P01633–P01641: nine chapter or paratext records from one dissertation (all excluded).
- Flags that look like false positives (different papers by the same authors): P00524 (TOuNN vs GM-TOuNN), P00526,
  P00592, P00638, P02509→P02437, P02538→P02438.

## Borderline includes to check first

- **Vague auto-generated Zenodo "topology" preprints:** P01049, P01051, P01143, P01307, P01309, P01321, P01353,
  P01365, P01391, P01499, P01523, P01665, P01692, P01703, P01754. Most are also dropped from the decision order as
  non-arXiv preprints.
- **Physics possibly outside the protocol's list:** P00699 (ion transport), P00554 (flexoelectric), P01101
  (piezoelectric), P01268 (crash), P00688, P01890, P01901, P01998, P02084 (possible fluid flow), P00781, P00904,
  P00920, P00948 (cooling plates and heat sinks without abstracts), P01980 (elastic-wave).
- **Learned model's role unclear:** P00629, P00598, P00811, P00918, P00862, P01956, P01966, P02296, P02487, P02481.
- **ML-only comparisons with a speed framing:** P00664, P00684, P01542 (coded I-SPEED or I-UNCLEAR). E-MLONLY is the
  alternative.
- **Title does not name TO:** P00694, P00739, P00751, P00689, P00600, P02221, P02229, P02240, P02287, P02293, P02572.
- **Results against the ML method (keep; they matter for C4):** P01247 (classical TO faster and stiffer); P01314
  (mixed cost-benefit study).
- **Other:** P01827 (the comparator is a parameter sweep), P01828 (may not be TO), P01869, P01887, P01916 (GAN
  joints), P02001 (may be a review), P01457 and P01788 (possibly talk-only records), P01674 (linkage synthesis, scope),
  P02107 (typed as a data-files record, but the abstract is the paper's own; kept as I-QUALITY).

## Borderline excludes to check

- P01872 and P01959 (assumed fluid flow, E-DOMAIN).
- P01926 (E-MLONLY).
- P01899 and P01945 (VAE for interpretation only, E-OTHER).
- P02553 (GAN inverse design of graphene/h-BN, E-SCOPE).
- P02317 (graded porous structures, E-NOML from the title only).
- P02297 (deep-learning layout of reinforced-concrete buildings, E-SCOPE).
- P01317 (benchmark of five TO methods, E-TYPE).
- P01397 (German title, English abstract with a speed claim, E-OTHER non-English).
- P01041 (reads like a review, E-TYPE, inferred from the title).

## Related-work lead

- P02589: GPU-accelerated classical TO codes (CMAME 2023), excluded as E-NOML. It is a strong-baseline reference for
  the Discussion.
