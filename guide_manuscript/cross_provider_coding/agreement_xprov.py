"""Cross-provider coding check: validate the records coded with kit/ and compare them with every earlier coding.

    python guide_manuscript/cross_provider_coding/agreement_xprov.py              # validate and analyse returned/*
    python guide_manuscript/cross_provider_coding/agreement_xprov.py --selftest   # check the machinery first

Returned records go in returned/<tag>/, one folder per provider model (for example returned/openai-gpt-5.2/):
P#####.json coding records from kit/queues, and optionally referrals.json from kit/REFERRAL_INSTRUCTIONS.md.

Per provider tag the script reports, with the same kappa and bootstrap as analysis/agreement.py (2,000 resamples, seed
20260924; Table 5 of the paper):
  - agreement with the adjudicated records (audit/coding/records), the first pass (llm_prefill), the blind second pass
    (second_pass) and every other provider, for inclusion, stratum and R1-R4 (rules only where both coders include);
  - R1 and R2 against the authors' unblinded review of the 28 speed claims (evidence/human_review.json);
  - the headline counts recomputed with the provider's verdicts, on the 28 adjudicated speed claims and on the
    provider's own speed stratum: R1 fail, R1-or-R2 fail, R1-or-R2 fail-or-partial, and R2 passes by default (marker
    R2-none-established), each with a Clopper-Pearson 95 % interval;
  - for referrals.json: how many of the 17 re-screen referrals are eligible at full text, how many of those also pass
    the draw rules of analysis/rescreen.py, and the implied false-exclusion rate among the 188 sampled excludes.
Validation (schema, stage "cross_provider_pass", closed code lists, the conventions of audit/coding/validate_records.py)
stops the analysis on any invalid record unless --skip-invalid is given; skipped records are listed in the output.
Reads the repository only. Writes results/xprov_agreement.json and results/xprov_summary.md in this folder.
"""
import argparse
import csv
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from analysis.agreement import ITEMS, boot, kappa  # noqa: E402
from analysis.codes import ft_code  # noqa: E402
from analysis.rules import clopper_pearson  # noqa: E402

STAGE = "cross_provider_pass"
VERDICTS = {"pass", "partial", "fail", "na"}
INCLUDE_CODES = {"I-SPEED", "I-QUALITY", "I-UNCLEAR"}
EXCLUDE_CODES = {"E-SCOPE", "E-DOMAIN", "E-NOML", "E-TYPE", "E-FORWARD", "E-MLONLY", "E-NOCLAIM", "E-OTHER"}


def load_dir(d, pids=None):
    recs = {}
    for f in sorted(pathlib.Path(d).glob("P*.json")):
        if pids is None or f.stem in pids:
            recs[f.stem] = json.loads(f.read_text(encoding="utf-8-sig"))   # agents may write a BOM
    return recs


def validate(path, schema, allowed, stage=STAGE):
    """The checks of audit/coding/validate_records.py, with the cross-provider stage and the kit's pid list."""
    try:
        r = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return None, [f"unreadable: {exc}"]
    probs = []
    if r.get("pid") != path.stem:
        probs.append(f"pid {r.get('pid')!r} differs from the file name")
    if path.stem not in allowed:
        probs.append("pid is not in the kit's queues")
    try:
        import jsonschema
        for e in jsonschema.Draft7Validator(schema).iter_errors(r):
            probs.append(f"schema: {'/'.join(map(str, e.path))}: {e.message[:160]}")
    except ImportError:
        for k in schema["required"]:
            if k not in r:
                probs.append(f"missing key {k}")
    if stage and r.get("stage") != stage:
        probs.append(f"stage {r.get('stage')!r}, expected {stage!r}")
    inc, rules = r.get("included") or {}, r.get("rules") or {}
    if inc.get("decision") not in ("include", "exclude"):
        probs.append(f"decision {inc.get('decision')!r}")
    for k in ("R1", "R2", "R3", "R4"):
        if (rules.get(k) or {}).get("verdict") not in VERDICTS:
            probs.append(f"{k} verdict {(rules.get(k) or {}).get('verdict')!r}")
    if inc.get("decision") == "exclude" and r.get("access") == "full_text":
        try:
            ft_code(inc.get("reason", ""))
        except ValueError as exc:
            probs.append(str(exc))
    if inc.get("decision") == "exclude" or r.get("access") != "full_text":
        if inc.get("stratum") not in (None, "none"):
            probs.append(f"stratum {inc.get('stratum')!r} on an excluded or unread record")
        if any((rules.get(k) or {}).get("verdict") != "na" for k in ("R1", "R2", "R3", "R4")):
            probs.append("rule verdicts must be na on an excluded or unread record")
    return r, probs


def compare(a, b):
    """analysis/agreement.py compare(), over two {pid: record} maps (pairs = pids coded in both)."""
    pids = sorted(set(a) & set(b))
    pairs = [(a[p], b[p]) for p in pids]
    res = {"n_pairs": len(pairs), "items": {}}
    for item, get in ITEMS.items():
        sel = [(get(x), get(y)) for x, y in pairs]
        if item.startswith("R"):
            sel = [(u, v) for (u, v), (x, y) in zip(sel, pairs)
                   if x["included"]["decision"] == "include" and y["included"]["decision"] == "include"]
        xa, xb = [u for u, _ in sel], [v for _, v in sel]
        res["items"][item] = {"n": len(sel), "agreement": (sum(u == v for u, v in sel) / len(sel)) if sel else None,
                              "kappa": kappa(xa, xb), "kappa_ci95": boot(xa, xb) if len(sel) >= 5 else [None, None],
                              "one_category": len(set(xa) | set(xb)) < 2}
    return res


def is_speed(r):
    return (r["included"]["decision"] == "include" and r["included"].get("stratum") == "speed"
            and r.get("access") == "full_text")


def headline(recs, pids):
    """Headline counts over `pids` with the verdicts in `recs`; pids not coded as full-text speed claims are listed."""
    coded = [p for p in pids if p in recs and is_speed(recs[p])]
    v = {p: {k: recs[p]["rules"][k]["verdict"] for k in ("R1", "R2")} for p in coded}
    m2 = {p: str(recs[p]["rules"]["R2"].get("marker", "")).lower() for p in coded}

    def share(k):
        return {"k": k, "n": len(coded), "ci95": clopper_pearson(k, len(coded))}
    return {
        "n_pids": len(pids), "n_speed_full_text": len(coded),
        "not_speed": {p: ("missing" if p not in recs else
                          f"{recs[p]['included']['decision']}/{recs[p]['included'].get('stratum')}/{recs[p].get('access')}")
                      for p in pids if p not in coded},
        "R1_fail": share(sum(v[p]["R1"] == "fail" for p in coded)),
        "R1_or_R2_fail": share(sum("fail" in (v[p]["R1"], v[p]["R2"]) for p in coded)),
        "R1_or_R2_fail_or_partial": share(sum(bool({"fail", "partial"} & {v[p]["R1"], v[p]["R2"]}) for p in coded)),
        "R2_default_pass": share(sum(v[p]["R2"] == "pass" and "none-established" in m2[p] for p in coded)),
    }


def authors_review(adjudicated, speed):
    """The authors' reviewed verdicts: the adjudicated verdicts with the changes in evidence/human_review.json."""
    hr = json.loads((ROOT / "evidence/human_review.json").read_text(encoding="utf-8"))
    out = {p: json.loads(json.dumps(adjudicated[p])) for p in speed}
    for c in hr["changes"]:
        out[c["pid"]]["rules"][c["rule"]]["verdict"] = c["reviewed"]
    return out, hr


def draw_eligible():
    """analysis/rescreen.py eligible(), restated: the §3.4 date window and §3.3 record type of the draw."""
    csv.field_size_limit(10 ** 9)
    scr = {r["pid"]: r for r in csv.DictReader(open(ROOT / "audit/screening/screening.csv", encoding="utf-8"))}
    pool = {r["pid"]: r for r in csv.DictReader(open(ROOT / "audit/pool/pool.csv", encoding="utf-8"))}

    def eligible(pid):
        r, p = scr[pid], pool[pid]
        only_bib = all(s.startswith("backward:BC3") for s in r["sources"].split(";"))
        pre2017 = bool(r["date"]) and not only_bib and r["date"][:10] < "2017-01-01"
        arx = bool(p["arxiv_id"]) or p["doi"].startswith("10.48550/arxiv") or "arxiv" in p["venue"].lower()
        return not pre2017 and not (p["type"] == "preprint" and not arx)
    return eligible, sum(1 for r in scr.values() if r["llm_decision"] == "exclude")


def referrals(path, rescreen):
    want = sorted(d["pid"] for d in rescreen["disagreements"])
    try:
        got = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return None, [f"referrals.json unreadable: {exc}"]
    probs = []
    ids = [g.get("pid") for g in got]
    if sorted(ids) != want or len(set(ids)) != len(ids):
        probs.append("referrals.json does not hold the 17 referral pids exactly once")
    for g in got:
        d, c, acc = g.get("decision"), str(g.get("code", "")), g.get("access")
        if acc not in ("full_text", "abstract_only", "no_access"):
            probs.append(f"{g.get('pid')}: access {acc!r}")
        if d == "include":
            ok = c in ({"I-SPEED", "I-QUALITY"} if acc == "full_text" else INCLUDE_CODES)
        elif d == "exclude":
            ok = c in EXCLUDE_CODES if acc != "full_text" else c.startswith("FT-")
            if ok and acc == "full_text":
                try:
                    ft_code(c)
                except ValueError:
                    ok = False
        else:
            ok = False
        if not ok:
            probs.append(f"{g.get('pid')}: decision/code {d!r}/{c!r} with access {acc!r}")
    if probs:
        return None, probs
    eligible, n_excl = draw_eligible()
    n = rescreen["n_sampled_excludes"]
    inc = sorted(g["pid"] for g in got if g["decision"] == "include")
    inc_ft = sorted(g["pid"] for g in got if g["decision"] == "include" and g["access"] == "full_text")
    inc_draw = [p for p in inc_ft if eligible(p)]
    ci = clopper_pearson(len(inc_draw), n)
    return {"n_referrals": len(got), "include": inc, "include_full_text": inc_ft, "include_full_text_and_draw": inc_draw,
            "codes": {g["pid"]: g["code"] for g in got}, "access": {g["pid"]: g["access"] for g in got},
            "false_exclusion_rate": len(inc_draw) / n, "false_exclusion_ci95": ci, "n_sampled_excludes": n,
            "implied_false_exclusions": round(len(inc_draw) / n * n_excl),
            "implied_ci95": [round(ci[0] * n_excl), round(ci[1] * n_excl)], "all_llm_excludes": n_excl}, []


def fmt_items(res):
    rows = []
    for item, v in res["items"].items():
        if not v["n"]:
            rows.append(f"{item} n=0")
            continue
        k = "undefined (one category)" if v["one_category"] else (
            f"{v['kappa']:.2f}" + (f" ({v['kappa_ci95'][0]:.2f}–{v['kappa_ci95'][1]:.2f})"
                                   if v["kappa_ci95"][0] is not None else ""))
        rows.append(f"{item} n={v['n']} agree={100 * v['agreement']:.0f} % κ={k}")
    return "; ".join(rows)


def fmt_head(h):
    def one(x):
        lo, hi = x["ci95"]
        return f"{x['k']}/{x['n']}" + (f" ({100 * lo:.0f}–{100 * hi:.0f} %)" if lo is not None else "")
    return (f"R1 fail {one(h['R1_fail'])}; R1-or-R2 fail {one(h['R1_or_R2_fail'])}; R1-or-R2 fail-or-partial "
            f"{one(h['R1_or_R2_fail_or_partial'])}; R2 default pass {one(h['R2_default_pass'])}; "
            f"not coded as full-text speed claims: {len(h['not_speed'])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="reproduce the paper's agreement and headline values")
    ap.add_argument("--skip-invalid", action="store_true", help="analyse the valid records and list the invalid ones")
    args = ap.parse_args()
    kit_pids = {line.split()[1] for q in sorted((HERE / "kit/queues").glob("queue_*.txt"))
                for line in q.read_text(encoding="utf-8").splitlines() if line.startswith("- P")}
    adjudicated = load_dir(ROOT / "audit/coding/records", kit_pids)
    first = load_dir(ROOT / "audit/coding/llm_prefill", kit_pids)
    second = load_dir(ROOT / "audit/coding/second_pass", kit_pids)
    speed = sorted(p for p, r in adjudicated.items() if is_speed(r))
    authors, hr = authors_review(adjudicated, speed)
    rescreen = json.loads((ROOT / "evidence/rescreen.json").read_text(encoding="utf-8"))

    if args.selftest:
        ok = True
        print(f"kit pids {len(kit_pids)}; adjudicated {len(adjudicated)}; first {len(first)}; second {len(second)}; "
              f"speed claims {len(speed)}")
        ref = json.loads((ROOT / "evidence/agreement.json").read_text(encoding="utf-8"))["first_vs_second_ai_pass"]
        mine = compare(first, second)
        for item, v in ref["items"].items():
            m = mine["items"][item]
            same = (m["n"] == v["n"] and abs(m["agreement"] - v["agreement"]) < 1e-12 and abs(m["kappa"] - v["kappa"]) < 1e-12
                    and all(abs(x - y) < 1e-12 for x, y in zip(m["kappa_ci95"], v["kappa_ci95"])))
            ok &= same
            print(f"  Table 5 {item:8s} n={m['n']:3d} agree={m['agreement']:.3f} kappa={m['kappa']:.2f} "
                  f"({m['kappa_ci95'][0]:.2f}-{m['kappa_ci95'][1]:.2f}) | evidence/agreement.json {'same' if same else 'DIFFERS'}")
        h = headline(adjudicated, speed)
        want = {"R1_fail": 8, "R1_or_R2_fail": 8, "R1_or_R2_fail_or_partial": 24, "R2_default_pass": 15}
        for k, w in want.items():
            ok &= h[k]["k"] == w and h[k]["n"] == 28
            print(f"  headline {k:25s} {h[k]['k']}/{h[k]['n']} (paper {w}/28)")
        for rule in ("R1", "R2", "R3", "R4"):
            agree = sum(authors[p]["rules"][rule]["verdict"] == adjudicated[p]["rules"][rule]["verdict"] for p in speed)
            ok &= agree == hr["per_rule"][rule]["agree"]
            print(f"  authors' review {rule}: agree {agree}/28 (evidence/human_review.json {hr['per_rule'][rule]['agree']})")
        ha = headline(authors, speed)
        ok &= ha["R1_or_R2_fail"]["k"] == hr["weak_R1_or_R2_reviewed"]
        print(f"  authors' review R1-or-R2 fail {ha['R1_or_R2_fail']['k']}/28 (paper {hr['weak_R1_or_R2_reviewed']}/28)")
        print("  second pass as a stand-in provider, against the adjudicated records:", fmt_items(compare(second, adjudicated)))
        print("SELFTEST", "PASSED" if ok else "FAILED")
        sys.exit(0 if ok else 1)

    schema = json.loads((HERE / "kit/coding_schema.json").read_text(encoding="utf-8"))
    tags = sorted(d for d in (HERE / "returned").glob("*") if d.is_dir()) if (HERE / "returned").exists() else []
    if not tags:
        sys.exit("no returned/<tag>/ folders yet")
    provider, invalid, refs = {}, {}, {}
    for d in tags:
        recs = {}
        for f in sorted(d.glob("P*.json")):
            r, probs = validate(f, schema, kit_pids)
            if probs:
                invalid.setdefault(d.name, {})[f.stem] = probs
            else:
                recs[f.stem] = r
        provider[d.name] = recs
        if (d / "referrals.json").exists():
            res, probs = referrals(d / "referrals.json", rescreen)
            if probs:
                invalid.setdefault(d.name, {})["referrals.json"] = probs
            else:
                refs[d.name] = res
    if invalid:
        for tag, bad in invalid.items():
            for pid, probs in bad.items():
                print(f"INVALID {tag}/{pid}: " + "; ".join(probs))
        if not args.skip_invalid:
            sys.exit("invalid records; fix them or rerun with --skip-invalid")

    out = {"reference": {"adjudicated_headline": headline(adjudicated, speed),
                         "authors_review_headline": headline(authors, speed),
                         "first_vs_second": compare(first, second)},
           "providers": {}, "between_providers": {}, "invalid": invalid}
    lines = ["# Cross-provider coding check", "",
             f"Reference (adjudicated, 28 speed claims): {fmt_head(out['reference']['adjudicated_headline'])}",
             f"First vs blind second pass (Table 5): {fmt_items(out['reference']['first_vs_second'])}", ""]
    for tag, recs in provider.items():
        own = sorted(p for p, r in recs.items() if is_speed(r))
        res = {"n_records": len(recs), "coverage_of_kit": f"{len(recs)}/{len(kit_pids)}",
               "models": sorted({r["coder"].get("llm_model", "?") for r in recs.values()}),
               "vs_adjudicated": compare(recs, adjudicated), "vs_first_pass": compare(recs, first),
               "vs_second_pass": compare(recs, second),
               "vs_authors_review_R1_R2": {k: v for k, v in compare({p: recs[p] for p in recs if p in authors},
                                                                    authors)["items"].items() if k in ("R1", "R2")},
               "headline_on_adjudicated_28": headline(recs, speed),
               "headline_on_own_speed_stratum": headline(recs, own),
               "first_vs_second_on_same_records": compare({p: first[p] for p in recs if p in first},
                                                          {p: second[p] for p in recs if p in second}),
               "referrals": refs.get(tag)}
        out["providers"][tag] = res
        lines += [f"## {tag}", "", f"Records: {res['coverage_of_kit']}; models: {', '.join(res['models'])}", "",
                  f"- vs adjudicated: {fmt_items(res['vs_adjudicated'])}",
                  f"- vs first pass: {fmt_items(res['vs_first_pass'])}",
                  f"- vs blind second pass: {fmt_items(res['vs_second_pass'])}",
                  f"- first vs second pass on the same records: {fmt_items(res['first_vs_second_on_same_records'])}",
                  f"- headline on the 28 adjudicated speed claims: {fmt_head(res['headline_on_adjudicated_28'])}",
                  f"- headline on its own speed stratum: {fmt_head(res['headline_on_own_speed_stratum'])}"]
        if res["referrals"]:
            rf = res["referrals"]
            lo, hi = rf["false_exclusion_ci95"]
            lines.append(f"- referrals: {len(rf['include'])} of 17 include ({len(rf['include_full_text'])} at full text, "
                         f"{len(rf['include_full_text_and_draw'])} also pass the draw rules); false-exclusion rate "
                         f"{100 * rf['false_exclusion_rate']:.1f} % (95 % CI {100 * lo:.1f}–{100 * hi:.1f} %), implied "
                         f"{rf['implied_false_exclusions']} of {rf['all_llm_excludes']} excludes "
                         f"({rf['implied_ci95'][0]}–{rf['implied_ci95'][1]})")
        lines.append("")
    names = list(provider)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            res = compare(provider[a], provider[b])
            out["between_providers"][f"{a} vs {b}"] = res
            lines.append(f"- {a} vs {b}: {fmt_items(res)}")
    if invalid:
        lines += ["", "Invalid and skipped: " + "; ".join(f"{t}/{p}" for t, bad in invalid.items() for p in bad)]
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/xprov_agreement.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (HERE / "results/xprov_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
