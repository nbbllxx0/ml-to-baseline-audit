# Title/abstract screening codes (plan/PROTOCOL.md §3–4)

Each pool record gets exactly one decision and one reason code.

| Decision | Code | Meaning |
|---|---|---|
| include | I-SPEED | ML for TO or architected-material inverse design, and the abstract claims a speed or cost advantage over a classical, non-learned optimization method. Examples: faster, real-time, accelerate, reduces computational cost, without iterative optimization, fewer FE evaluations |
| include | I-QUALITY | Same scope, but the abstract claims only better design quality than a classical method (secondary stratum Q) |
| include | I-UNCLEAR | Same scope; a comparison with a classical method is plausible but not stated in the abstract. The full text decides |
| exclude | E-SCOPE | Not TO or architected-material inverse design, e.g. network "topology", topological data analysis, photonics |
| exclude | E-DOMAIN | TO in an excluded physics domain: fluid flow, acoustics, photonics, electromagnetics |
| exclude | E-NOML | No learned model; classical TO only |
| exclude | E-TYPE | Review, survey, thesis, dataset-only or benchmark-only paper with no method claim, tutorial, perspective |
| exclude | E-FORWARD | ML used only for forward analysis or prediction; no optimization-level comparison |
| exclude | E-MLONLY | Compares only with other ML methods; no classical comparator mentioned. Tallied for C4 |
| exclude | E-NOCLAIM | Proposes an ML-for-TO method but makes no comparative claim of any kind |
| exclude | E-OTHER | Anything else; explain in the rationale |

Extra fields per record:
- `method_family`: one of cnn, gan, vae, diffusion_flow, transformer, gnn, llm_agent, rl, neural_reparam, surrogate_mlp_gp, other.
- `physics`: one of compliance, stress, thermal, compliant_mechanism, multiphysics, metamaterial_homogenization, other.
- `dim`: 2d, 3d, both or unclear.
- `rationale`: one sentence, ≤ 30 words, in the screener's own words (no copying from the abstract).

**When unsure**, prefer I-UNCLEAR over an exclude. The full text is the arbiter, and exclusions at this stage are cheap
to recover later.

# Full-text exclusion codes (coding stage; plan/PROTOCOL.md §11, clarification of 2026-09-24)

An article excluded at full text gets exactly one code from this closed list. When several apply, use the first one in
the table order. Put any explanation in `notes`, not in the `reason` field.

| Order | Code | Meaning |
|---|---|---|
| 1 | FT-DUPLICATE | Another version of an article already in the pool. Code the primary version (version of record if open access, else the latest arXiv version) and name it in `notes` |
| 2 | FT-SCOPE | Not TO or architected-material inverse design |
| 3 | FT-TYPE | Review, survey, thesis, dataset-only or benchmark-only paper with no method claim, tutorial, perspective |
| 4 | FT-DOMAIN | TO in an excluded physics domain: fluid flow, acoustics, photonics, electromagnetics |
| 5 | FT-NOML | No learned model; classical TO only |
| 6 | FT-FORWARD | ML used only for forward analysis or prediction; no optimization-level comparison |
| 7 | FT-MLONLY | Compares only with other ML methods; no classical comparator is run, timed or cited. Tallied for C4 |
| 8 | FT-NOBASELINE | No comparison of any kind with a classical method: the article does not run, time or cite a classical method's cost or result. A qualitative motivation such as "TO is slow" is not a comparison |
| 9 | FT-OTHER | Anything else; explain in `notes` |

Prefills written before this list used free-text labels. `analysis/codes.py` maps them without editing the frozen
prefill files: FT-ML-only → FT-MLONLY; FT-NOCOMPARISON → FT-NOBASELINE. Any other label stops the analysis with an
error, so the record must be recoded.
