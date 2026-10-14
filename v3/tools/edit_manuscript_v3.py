"""Apply the census edits to v3/manuscript/manuscript.md (a copy of SMO v2) and the matching build.py table specs.

    python v3/tools/edit_manuscript_v3.py

Each edit replaces text that must occur exactly once; the script stops otherwise, so it cannot be applied twice.
Numbers are registry tokens: N300-N322 from v3/evidence/numbers_v3.json (v3/tools/census_numbers.py), the rest from
evidence/numbers.json. The agreement table becomes Table 5; the census table is Table 4.
"""
import pathlib

V3 = pathlib.Path(__file__).resolve().parents[1]
MD = V3 / "manuscript" / "manuscript.md"
BUILD = V3 / "manuscript" / "build.py"

EDITS = [
    # header note
    ("# SMO v2: restructured Research Paper for Structural and Multidisciplinary Optimization\n",
     "# SMO v3: SMO v2 plus the re-test census\n"),
    ("Status note, not manuscript text:\n",
     "Status note, not manuscript text:\n"
     "- v3 (2026-09-25): v2 (`manuscript/smo_v2/`, unchanged) plus the census of code-linked speed claims: Sect. 2.6 last\n"
     "  paragraph, Sect. 3.7 with Table 4, Online Resource 6, and matching sentences in the abstract, Sects. 1, 2.7, 3.2,\n"
     "  4.3, 4.4 and 5. Census numbers N300-N322 come from `v3/evidence/numbers_v3.json` (`v3/tools/census_numbers.py`).\n"
     "  The agreement table is now Table 5. Edits applied by `v3/tools/edit_manuscript_v3.py`.\n"),
    # abstract
    ("We then re-tested two\npublished methods on one workstation. The authors' own classical code left each speed-up within a factor of\n"
     "[[N093]] of the published value. An efficient implementation of the same classical algorithm reduced it\n"
     "[[N094]]. For a graph-based neural reparameterization (HGTO), this reversed the result: the classical code it was\n"
     "published with, moved to a graphics processor, converged faster than HGTO on the largest mesh. For a diffusion\n"
     "foundation model (OAT), the [[N016]] from its published timings became [[N017]] against the strong baseline and [[N018]] at matched\n"
     "quality on five problems ([[N101]] under the pre-registered rule), and [[N172]] over 25 problems with five samples\n"
     "each.",
     "We then re-tested two\npublished methods on one workstation. An efficient implementation of the same classical algorithm reduced\n"
     "their speed-ups [[N094]]. For a graph-based neural reparameterization (HGTO) this reversed the result. For a diffusion\n"
     "foundation model (OAT), the [[N016]] from its published timings became [[N018]] at matched quality on five problems\n"
     "([[N101]] under the pre-registered rule) and [[N172]] over 25 problems. A census of the [[N301]] speed claims in the\n"
     "sample with public code found the same pattern: at matched quality, a speed-up of thousands fell to [[N305]], another\n"
     "reversed, two held and two could not be compared."),
    # introduction
    ("We audited a random sample of this literature against four rules and re-tested two published methods on one\n"
     "workstation.",
     "We audited a random sample of this literature against four rules, re-tested two published methods on one\n"
     "workstation, and then re-ran every speed claim in the sample whose code is public."),
    ("Against an efficient\nimplementation of the same algorithm, it fell [[N094]], and for HGTO it reversed. Section 2 describes the audit, the\n"
     "baseline and the re-tests.",
     "Against an efficient\nimplementation of the same algorithm, it fell [[N094]], and for HGTO it reversed. The census of code-linked claims\n"
     "shows the same pattern where it can be tested: at matched quality, a speed-up of thousands fell to [[N305]] and\n"
     "another reversed, while two claims held. Section 2 describes the audit, the baseline, the re-tests and the census."),
    # 2.6: candidates, then the census paragraph
    ("[[N211]] further candidates flagged during coding were not\nattempted.",
     "[[N211]] further candidates were flagged during coding; the one with a speed claim\n"
     "[@audP00080] is covered by the census below, and the other two concern quality claims and were not attempted."),
    ("its diagnosis are in Online Resource 5.\n",
     "its diagnosis are in Online Resource 5.\n\n"
     "**Census of code-linked speed claims.** To remove the choice of targets, we then re-tested every speed claim of the\n"
     "analysis sample whose article links public code: [[N300]] claims, one of them the predictor of Halle et al. above.\n"
     "The procedure was pre-registered before the first run (Online Resource 6). Each claim is taken as far as it goes:\n"
     "running the authors' code (L0), the article's own comparison on our machine (L1), and the same classical method\n"
     "with an efficient solver or device at matched quality (L2), judged by the article's own quality measure. Repairs were\n"
     "limited to dependency versions, file paths and removed library calls, each logged with its diff. A missing trained\n"
     "model was retrained with the authors' code only if data generation and training fit in one GPU-hour on our\n"
     "machine; otherwise the learned method keeps its published time. Timed runs were pinned to the performance cores,\n"
     "except for one claim that ran in a container, with a warm-up and three repeats; runs longer than an hour were\n"
     "timed once.\n"),
    # 2.7
    ("Seven changes to the pre-registered protocols are logged with dates in Online Resource 1.\n",
     "Seven changes to the pre-registered protocols are logged with dates in Online Resource 1. The census has its own\n"
     "dated deviation log (Online Resource 6). Its largest change: for one claim we stopped the classical runs after\n"
     "[[N319]] on the first of three pre-registered problems, without convergence, and replaced its multithreaded runs by\n"
     "a per-iteration measurement.\n"),
    # 3.2 forward reference
    ("Deciding R2 needs a re-test, which Sects. 3.3–3.5 report for two\nmethods.",
     "Deciding R2 needs a re-test, which Sects. 3.3–3.5 report for two\nmethods and Sect. 3.7 for the census."),
    # agreement table becomes Table 5 (before the census table is inserted)
    ("the stratum ([[N080]]) (Table 4).", "the stratum ([[N080]]) (Table 5)."),
    ("Every disagreement went to an adjudicator, and Table 4 gives the weak share under each",
     "Every disagreement went to an adjudicator, and Table 5 gives the weak share under each"),
    ("[[N207]] for R2, [[N208]] for R3 and [[N209]] for R4 (Table 4).",
     "[[N207]] for R2, [[N208]] for R3 and [[N209]] for R4 (Table 5)."),
    ("**Table 4** Agreement between the two independent language-model codings",
     "**Table 5** Agreement between the two independent language-model codings"),
    # new 3.7, old 3.7 becomes 3.8
    ("### 3.7 Reporting practices and coder agreement\n",
     "### 3.7 Census of code-linked speed claims\n\n"
     "The authors' code ran for all [[N301]] re-run claims (Table 4); [[N302]] needed repairs first, none of which changed an\n"
     "algorithm. Two MATLAB files released with one article did not run as published: the optimization never sizes its\n"
     "load vector, and the evaluator stops at an undefined variable [@audP00183]. The seventh claim had stopped at its\n"
     "reconstruction check (Sect. 2.6).\n\n"
     "On the articles' own comparisons, the published factors ranged from reproduced to overstated. CNN steps in a\n"
     "phase-field optimization gave [[N316]] against the published [[N315]], with the article's iteration counts and\n"
     "compliances to the last reported digit [@audP00663]. The CNN for effective conductivity kept [[N304]] against the\n"
     "published [[N303]], because the same released solver ran [[N306]] times faster here than the article reports\n"
     "[@audP00610]. For VoroTO both classical times were projections; recomputed from our unit costs they gave [[N308]]\n"
     "instead of [[N307]] [@audP00080].\n\n"
     "At matched quality against an efficient classical method, the conductivity CNN kept a [[N305]] advantage over a\n"
     "direct solve of the same finite-volume equations, which was also more accurate. For VoroTO the comparison reversed:\n"
     "a GPU density-based optimization of the same cantilever reached VoroTO's structural quality in [[N310]], [[N309]]\n"
     "faster than VoroTO's own [[N311]] optimization and without its offline cost; scoring both designs by the same\n"
     "thresholded evaluation, a check we added after the runs, gives the same result. The one-shot generator kept\n"
     "[[N313]] at matched quality, but its designs had [[N314]] times the compliance of the optimized ones [@audP00183].\n"
     "For the other two claims no matched-quality comparison was possible: [@audP00140] states its supports only in a\n"
     "figure and does not describe how the fine-scale designs were evaluated, and [@audP00647] released no trained model.\n"
     "The classical side of the latter is not overstated: one run of its released code took [[N319]] on one core here,\n"
     "without converging, against the 2.4 h the article reports.\n\n"
     "**Table 4** Census of the speed claims in the analysis sample whose code is public. Factors are learned method over\n"
     "classical time. L0: the authors' code runs; L1: the article's comparison on our machine; L2: an efficient classical\n"
     "method at matched quality. Details and deviations in Online Resource 6\n\n"
     "{{TABLE:table4_census}}\n\n"
     "### 3.8 Reporting practices and coder agreement\n"),
    # 4.3 limitations
    ("1. Re-tests: one workstation, two methods. Every re-test number describes our hardware, software and\n"
     "   implementations, and a difference from a published figure is not evidence that the published figure is wrong. A\n"
     "   third re-test failed its reconstruction check (Sect. 2.6). Both re-tests are two-dimensional, while [[N155]] speed\n"
     "   claims involve three-dimensional problems.",
     "1. Re-tests: one workstation; two methods in depth and a census of [[N301]] code-linked claims. Every re-test number\n"
     "   describes our hardware, software and implementations, and a difference from a published figure is not evidence\n"
     "   that the published figure is wrong. A third in-depth re-test failed its reconstruction check (Sect. 2.6). Both\n"
     "   in-depth re-tests are two-dimensional, while [[N155]] speed claims involve three-dimensional problems; the one\n"
     "   three-dimensional claim in the census could not be compared at matched quality.\n"
     "2. Census: two trained models were rebuilt from the released code and may differ from the authors'; one claim ran\n"
     "   in a container that could not be pinned; some runs overlapped and are logged (Online Resource 6)."),
    ("2. Coding: language-model agents coded twice", "3. Coding: language-model agents coded twice"),
    ("3. Access: [[N128]] of the 200 sampled records", "4. Access: [[N128]] of the 200 sampled records"),
    ("4. Screening: one model screened titles", "5. Screening: one model screened titles"),
    ("5. OAT: its refinement step was not run", "6. OAT: its refinement step was not run"),
    # 4.4
    ("6. Release code, data and the timing harness, so that others can re-test on one machine.",
     "6. Release code, data, trained models and the timing harness with a pinned environment, so that others can re-test\n"
     "   on one machine. In our census, [[N302]] of [[N301]] codes needed repairs before they ran, and three released no\n"
     "   trained model."),
    # 5
    ("five OAT samples each, against [[N016]] from its published timings on other hardware.\n",
     "five OAT samples each, against [[N016]] from its published timings on other hardware. A census of every\n"
     "code-linked speed claim in the sample showed the same pattern where it could be tested: at matched quality, one\n"
     "speed-up of thousands fell to [[N305]] and another reversed, while two held.\n"),
    # code availability, online resources, replication
    ("All scripts for search, screening, coding, analysis, the strong baseline and the re-test\nharnesses will be released",
     "All scripts for search, screening, coding, analysis, the strong baseline, the re-test\nharnesses and the census will be released"),
    ("corrections to our reading of the data, the remaining misfit, and scripts.\n",
     "corrections to our reading of the data, the remaining misfit, and scripts.\n\n"
     "**Online Resource 6** Re-test census of code-linked speed claims: the pre-registration with its dated deviation log,\n"
     "the claim frame, and per-claim results and repairs.\n"),
    ("which is why every comparison in this paper is made on one machine.\n",
     "which is why every comparison in this paper is made on one machine. The census also needs MATLAB R2023b, Docker for\n"
     "one claim, and the third-party repositories at the commits listed in Online Resource 6.\n"),
]

BUILD_EDITS = [
    ('        4: (False, r">{\\raggedright\\arraybackslash}p{0.33\\columnwidth}>{\\centering\\arraybackslash}p{0.06\\columnwidth}"',
     '        4: (True, r">{\\raggedright\\arraybackslash}p{0.13\\textwidth}>{\\raggedright\\arraybackslash}p{0.15\\textwidth}"\n'
     '                  r">{\\raggedright\\arraybackslash}p{0.13\\textwidth}>{\\raggedright\\arraybackslash}p{0.2\\textwidth}"\n'
     '                  r">{\\raggedright\\arraybackslash}p{0.24\\textwidth}>{\\raggedright\\arraybackslash}p{0.07\\textwidth}", r"\\footnotesize"),\n'
     '        5: (False, r">{\\raggedright\\arraybackslash}p{0.33\\columnwidth}>{\\centering\\arraybackslash}p{0.06\\columnwidth}"'),
]


def apply(path, edits):
    t = path.read_text(encoding="utf-8")
    for a, b in edits:
        n = t.count(a)
        if n != 1:
            raise SystemExit(f"{path.name}: target found {n} times: {a[:80]!r}")
        t = t.replace(a, b)
    path.write_text(t, encoding="utf-8")


if __name__ == "__main__":
    apply(MD, EDITS)
    apply(BUILD, BUILD_EDITS)
    print("applied", len(EDITS), "manuscript edits and", len(BUILD_EDITS), "build edit")
