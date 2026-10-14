"""Registry values and the Online Resource 4 section for the post hoc cross-provider coding check (v6).

    py -3.12 v9/smo/make_xprov_numbers.py

Reads guide_manuscript/cross_provider_coding/results/xprov_agreement.json (written by agreement_xprov.py from the GPT-6-Sol and
GPT-6-Luna records) and writes:
  numbers_xprov.json                  N510-N525, read by make_numbers.py with the other registries
  submission/ESM_4_xprov_section.tex  section 9 of Online Resource 4, input by ESM_4.tex
N510-N515  kappa (95 % CI), GPT-6-Sol vs GPT-6-Luna: inclusion, stratum, R1-R4 (Table 5)
N516-N521  kappa range over the four OpenAI-model/Claude-pass pairs, same items (Table 5)
N522       R1 kappa range over all six coder pairs (Claude pair, OpenAI pair, four cross pairs)
N523-N524  R1 fail share among each OpenAI model's own speed claims (GPT-6-Sol; GPT-6-Luna)
N525       re-screen referrals eligible at full text and under the draw rules (lowest and highest model)
The script asserts the statements printed beside these values.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
RES = PROJECT / "guide_manuscript" / "cross_provider_coding" / "results" / "xprov_agreement.json"
ITEMS = [("included", "Inclusion"), ("stratum", "Stratum"), ("R1", "R1"), ("R2", "R2"), ("R3", "R3"), ("R4", "R4")]
SOL, LUNA = "gpt-6-sol", "gpt-6-luna"

d = json.loads(RES.read_text(encoding="utf-8"))
P = d["providers"]
claude = d["reference"]["first_vs_second"]["items"]
openai = d["between_providers"][f"{LUNA} vs {SOL}"]["items"]
cross = {i: [P[m][f"vs_{p}_pass"]["items"][i] for m in (SOL, LUNA) for p in ("first", "second")] for i, _ in ITEMS}


def k2(x):
    return f"{x:.2f}"


def kci(v):
    lo, hi = v["kappa_ci95"]
    return f"{k2(v['kappa'])} ({k2(lo)}–{k2(hi)})"


reg = {}
for n, (i, _) in enumerate(ITEMS):
    reg[f"N{510 + n}"] = {"value": openai[i]["kappa"], "text": kci(openai[i]),
                          "note": f"kappa (95 % CI), GPT-6-Sol vs GPT-6-Luna, {i}, n = {openai[i]['n']} (post hoc)"}
    ks = [c["kappa"] for c in cross[i]]
    reg[f"N{516 + n}"] = {"value": [min(ks), max(ks)], "text": f"{k2(min(ks))}–{k2(max(ks))}",
                          "note": f"kappa range, four OpenAI-model/Claude-pass pairs, {i} (post hoc)"}
r1 = [claude["R1"]["kappa"], openai["R1"]["kappa"]] + [c["kappa"] for c in cross["R1"]]
assert max(r1) == claude["R1"]["kappa"]                      # "low for every pair"; the Claude pair is the highest
reg["N522"] = {"value": [min(r1), max(r1)], "text": f"κ = {k2(min(r1))}–{k2(max(r1))}",
               "note": "R1 kappa range over all six coder pairs (post hoc)"}
for key, m in (("N523", SOL), ("N524", LUNA)):
    h = P[m]["headline_on_own_speed_stratum"]["R1_fail"]
    lo, hi = h["ci95"]
    reg[key] = {"value": h["k"] / h["n"], "text": f"{100 * h['k'] / h['n']:.0f} % ({h['k']}/{h['n']}; 95 % CI "
                f"{100 * lo:.0f}–{100 * hi:.0f} %)", "note": f"R1 fail share among {m}'s own speed claims (post hoc)"}
elig = sorted(len(P[m]["referrals"]["include_full_text_and_draw"]) for m in (SOL, LUNA))
reg["N525"] = {"value": elig, "text": f"{elig[0]} or {elig[1]}" if elig[0] != elig[1] else str(elig[0]),
               "note": "re-screen referrals eligible at full text and under the draw rules, by model (post hoc)"}
assert P[SOL]["headline_on_own_speed_stratum"]["R1_fail"]["k"] / P[SOL]["headline_on_own_speed_stratum"]["R1_fail"]["n"] > 8 / 28
assert P[LUNA]["headline_on_own_speed_stratum"]["R1_fail"]["k"] / P[LUNA]["headline_on_own_speed_stratum"]["R1_fail"]["n"] > 8 / 28
(HERE / "numbers_xprov.json").write_text(json.dumps(reg, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

# Online Resource 4, section 9
rows = []
pairs = [("Claude first vs second pass", claude)] + [
    (f"{name} vs Claude {p} pass", P[m][f"vs_{p}_pass"]["items"]) for m, name in ((SOL, "GPT-6-Sol"), (LUNA, "GPT-6-Luna"))
    for p in ("first", "second")] + [("GPT-6-Sol vs GPT-6-Luna", openai)]
for label, items in pairs:
    for i, name in ITEMS:
        v = items[i]
        lo, hi = v["kappa_ci95"]
        rows.append(f"{label} & {name} & {v['n']} & {100 * v['agreement']:.0f} \\% & {k2(v['kappa'])} & "
                    f"{k2(lo)} to {k2(hi)} \\\\")
head = []
for m, name in ((SOL, "GPT-6-Sol"), (LUNA, "GPT-6-Luna")):
    h = P[m]["headline_on_own_speed_stratum"]
    cells = []
    for k in ("R1_fail", "R1_or_R2_fail", "R1_or_R2_fail_or_partial", "R2_default_pass"):
        x = h[k]
        cells.append(f"{x['k']}/{x['n']} ({100 * x['k'] / x['n']:.0f} \\%)")
    head.append(f"{name} (own speed claims) & " + " & ".join(cells) + " \\\\")
ref = []
for m, name in ((SOL, "GPT-6-Sol"), (LUNA, "GPT-6-Luna")):
    r = P[m]["referrals"]
    lo, hi = r["false_exclusion_ci95"]
    ref.append(f"{name} & {len(r['include'])} & {len(r['include_full_text'])} & {len(r['include_full_text_and_draw'])} & "
               f"{100 * r['false_exclusion_rate']:.1f} \\% ({100 * lo:.1f} to {100 * hi:.1f} \\%) \\\\")
tex = r"""\section*{9. Post hoc cross-provider coding check}

Added after a strict pre-submission review, when no independent human coder was available. Two OpenAI models,
GPT-6-Sol (\texttt{gpt-6-sol}) and GPT-6-Luna (\texttt{gpt-6-luna}), coded the same 110 records from the inputs of
the blind second pass: the protocol with masked record identifiers, the coding schema, the code lists and the
bibliographic queue lines. They ran in the Codex command-line tool (0.158.0) with reasoning effort high, live web
search, a workspace-write sandbox with network access, and memories, plugins, browser use and subagents switched
off. Each session held five or six records in a folder outside the project; the models saw no earlier coding and
not each other's records. A scan of every session's event log found no access to project, adjudication or
earlier-coding files, and every session log reported no contact with study material. Full texts came from
legitimate open sources (the download helper refused shadow libraries), and the session logs report no bypassed bot
check. Thirty-nine GPT-6-Luna records failed schema validation
(values outside the allowed reporting codes, a missing stage field, two missing objects on excluded records); new
sessions of the same model repaired the format only, and a check confirmed that access, inclusion, stratum and all rule verdicts
were unchanged. Both models also judged the 17 re-screen referrals of section 5 at full text.

Agreement uses the same Cohen's $\kappa$ and bootstrap as section 3 (2,000 resamples, seed 20260924); rule items
count records that both coders included.

{\footnotesize\setlength{\tabcolsep}{3pt}
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.30\textwidth}>{\raggedright\arraybackslash}p{0.10\textwidth}>{\raggedright\arraybackslash}p{0.08\textwidth}>{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}p{0.08\textwidth}>{\raggedright\arraybackslash}p{0.16\textwidth}@{}}
\toprule
\textbf{Pair} & \textbf{Item} & \textbf{Pairs} & \textbf{Raw agreement} & \textbf{κ} & \textbf{95 \% CI} \\
\midrule
\endhead
\bottomrule
\endfoot
""" + "\n".join(rows) + r"""
\end{longtable}}

Headline counts with each model's own inclusion, stratum and verdicts (adjudicated: 8/28 (29 \%), 8/28 (29 \%),
24/28 (86 \%) and 15/28 (54 \%)).

{\footnotesize\setlength{\tabcolsep}{3pt}
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.24\textwidth}>{\raggedright\arraybackslash}p{0.15\textwidth}>{\raggedright\arraybackslash}p{0.15\textwidth}>{\raggedright\arraybackslash}p{0.2\textwidth}>{\raggedright\arraybackslash}p{0.16\textwidth}@{}}
\toprule
\textbf{Coder} & \textbf{R1 fail} & \textbf{R1-or-R2 fail} & \textbf{R1-or-R2 fail or partial} & \textbf{R2 pass by default} \\
\midrule
\endhead
\bottomrule
\endfoot
""" + "\n".join(head) + r"""
\end{longtable}}

Re-screen referrals at full text (17 records). Eligible records are those included at full text that also pass the
draw rules; the false-exclusion rate divides them by the 188 re-screened exclusions.

{\footnotesize\setlength{\tabcolsep}{3pt}
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.2\textwidth}>{\raggedright\arraybackslash}p{0.12\textwidth}>{\raggedright\arraybackslash}p{0.16\textwidth}>{\raggedright\arraybackslash}p{0.14\textwidth}>{\raggedright\arraybackslash}p{0.26\textwidth}@{}}
\toprule
\textbf{Coder} & \textbf{Included} & \textbf{At full text} & \textbf{Eligible} & \textbf{False-exclusion rate (95 \% CI)} \\
\midrule
\endhead
\bottomrule
\endfoot
""" + "\n".join(ref) + r"""
\end{longtable}}
"""
(HERE / "submission" / "ESM_4_xprov_section.tex").write_text(tex, encoding="utf-8")
for k, v in reg.items():
    print(k, v["text"])
