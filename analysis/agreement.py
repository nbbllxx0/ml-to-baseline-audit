"""Coder agreement (claim C5, Extended Data ED6; N035–N038, N079, N080): first AI pass vs the blind second AI pass.

    python -m analysis.agreement

For every record with both a first-pass coding (audit/coding/llm_prefill/<pid>.json) and a blind second-pass coding by
a different model (audit/coding/second_pass/<pid>.json; PROTOCOL §11, 2026-09-24), items are compared: inclusion
decision, stratum, R1, R2, R3, R4. Reported per item: n, raw agreement and Cohen's kappa with a bootstrap 95 % interval
(2,000 resamples, seed 20260924; plan/PROTOCOL.md §9). A comparison with human-verified records is added only if such
records exist. Writes evidence/agreement.json. Numbers are registered when at least 20 pairs exist.
"""
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ITEMS = {"included": lambda r: r["included"]["decision"], "stratum": lambda r: r["included"].get("stratum"),
         "R1": lambda r: r["rules"]["R1"]["verdict"], "R2": lambda r: r["rules"]["R2"]["verdict"],
         "R3": lambda r: r["rules"]["R3"]["verdict"], "R4": lambda r: r["rules"]["R4"]["verdict"]}
IDS = {"R1": "N035", "R2": "N036", "R3": "N037", "R4": "N038", "included": "N079", "stratum": "N080"}


def kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    cats = sorted(set(a) | set(b), key=str)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return 1.0 if pe == 1.0 else (po - pe) / (1.0 - pe)


def boot(a, b, reps=2000, seed=20260924):
    rng = random.Random(seed)
    n = len(a)
    ks = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        k = kappa([a[i] for i in idx], [b[i] for i in idx])
        if k is not None:
            ks.append(k)
    ks.sort()
    return [ks[int(0.025 * len(ks))], ks[min(len(ks) - 1, int(0.975 * len(ks)))]] if ks else [None, None]


def compare(dir_a, dir_b):
    pairs = []
    for fb in sorted(dir_b.glob("P*.json")):
        fa = dir_a / fb.name
        if fa.exists():
            pairs.append((json.loads(fa.read_text(encoding="utf-8")), json.loads(fb.read_text(encoding="utf-8"))))
    res = {"n_pairs": len(pairs), "items": {}}
    for item, get in ITEMS.items():
        sel = [(get(a), get(b)) for a, b in pairs]
        if item.startswith("R"):          # verdicts only where both coders included the article
            sel = [(x, y) for (x, y), (a, b) in zip(sel, pairs)
                   if a["included"]["decision"] == "include" and b["included"]["decision"] == "include"]
        xa, xb = [x for x, _ in sel], [y for _, y in sel]
        res["items"][item] = {"n": len(sel), "agreement": (sum(x == y for x, y in sel) / len(sel)) if sel else None,
                              "kappa": kappa(xa, xb), "kappa_ci95": boot(xa, xb) if len(sel) >= 5 else [None, None]}
    return res


def main():
    # PROTOCOL §11 (2026-09-24): C5 = agreement between the two independent AI codings (first pass vs the blind second
    # pass by a different model). A human comparison is added only if human-verified records exist.
    out = {"first_vs_second_ai_pass": compare(ROOT / "audit/coding/llm_prefill", ROOT / "audit/coding/second_pass")}
    human = [f for f in (ROOT / "audit/coding/records").glob("P*.json")
             if json.loads(f.read_text(encoding="utf-8")).get("stage") == "human_verified"]
    if human:
        out["llm_vs_human"] = compare(ROOT / "audit/coding/llm_prefill", ROOT / "audit/coding/records")
    (ROOT / "evidence" / "agreement.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    lh = out["first_vs_second_ai_pass"]
    if lh["n_pairs"] >= 20:
        from tools.numbers import register
        for item, nid in IDS.items():
            v = lh["items"][item]
            if v["kappa"] is not None:
                lo, hi = v["kappa_ci95"]
                register(nid, v["kappa"], text=f"κ = {v['kappa']:.2f}" + (f" ({lo:.2f}–{hi:.2f})" if lo is not None else ""),
                         source="evidence/agreement.json", script="analysis/agreement.py",
                         note=f"first AI pass vs blind second AI pass (different model), {item}, n = {v['n']}")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
