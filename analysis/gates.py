"""Compute gate G1 from coding records (plan/PROTOCOL.md §8) and collect G2 into evidence/gates.json.

    python -m analysis.gates                  # uses verified records; falls back to prefills as provisional

G1 = share of pilot primary outcomes (speed stratum) with a fail on R1 or R2, with a Clopper-Pearson 95 % CI.
Primary ("G1"): walk the decision order over the complete screened pool (audit/screening/pilot_final_order.csv;
PROTOCOL §11 decision-pilot row) and use the first 20 speed-stratum includes; records excluded at a screening check
(legacy human_decision column), excluded at full text, or in the quality stratum are skipped; an uncoded record stops
the walk.
Also reported: the provisional arXiv pilot plus its pre-registered top-ups (audit/screening/pilot_provisional.csv,
pilot_topup_order.csv), and planning variants that drop unverified FT-NOBASELINE candidates (never a gate decision).
A verified record (stage in VERIFIED_STAGES: AI double-coded and agreed or adjudicated) replaces its prefill; unverified
prefills yield a *provisional* G1 only.
"""
import csv
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.codes import ft_code  # noqa: E402
from analysis.rules import VERIFIED_STAGES  # noqa: E402

N_TARGET = 20


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return (float("nan"), float("nan"))
    from scipy.stats import beta
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return (float(lo), float(hi))


def band_g1(share):
    if math.isnan(share):
        return "undetermined"
    return "NMI framing" if share >= 0.40 else ("ACME/SMO framing" if share >= 0.20 else "stop audit")


def load_records():
    recs = {}
    for sub in ("llm_prefill", "records"):
        for f in (ROOT / "audit" / "coding" / sub).glob("P*.json"):
            r = json.loads(f.read_text(encoding="utf-8"))
            if sub == "records" or r["pid"] not in recs:
                recs[r["pid"]] = r
    return recs


def pids(name):
    path = ROOT / "audit" / "screening" / name
    return [r["pid"] for r in csv.DictReader(open(path, encoding="utf-8"))] if path.exists() else []


def screen_excluded():
    f = ROOT / "audit" / "screening" / "screening.csv"
    if not f.exists():
        return set()
    csv.field_size_limit(10 ** 9)
    return {r["pid"] for r in csv.DictReader(open(f, encoding="utf-8")) if r.get("human_decision") == "exclude"}


SCREEN_EXCLUDED = set()
ACCESS, SUPPLIED = {}, set()


def access_maps():
    acc, sup = {}, set()
    f = ROOT / "audit" / "coding" / "access_final_order.csv"
    if f.exists():
        acc = {r["pid"]: r["accessible"] for r in csv.DictReader(open(f, encoding="utf-8"))}
    f = ROOT / "audit" / "coding" / "user_supplied_fulltext.csv"
    if f.exists():
        sup = {r["pid"] for r in csv.DictReader(open(f, encoding="utf-8"))}
    return acc, sup


def g1(recs, sequence, drop=frozenset()):
    """G1 over the pilot-then-top-up sequence. `drop` = unverified pids treated as excluded (planning variant)."""
    used, fails, verified = [], 0, 0
    detail, stopped = [], None
    for pid, role in sequence:
        if not role.startswith("pilot") and len(used) >= N_TARGET:
            break
        if pid in SCREEN_EXCLUDED:
            detail.append({"pid": pid, "role": role, "status": "excluded at a screening check"})
            continue
        r = recs.get(pid)
        if r is None:
            if role.startswith("order") and ACCESS.get(pid, "").startswith("no") and pid not in SUPPLIED:
                detail.append({"pid": pid, "role": role, "status": "skipped: no accessible full text "
                               "(paywalled per OpenAlex; not supplied by the user)"})
                continue
            detail.append({"pid": pid, "role": role, "status": "not coded"})
            if not role.startswith("pilot"):
                stopped = f"{role} ({pid}) not yet coded"
                break
            continue
        if r.get("access") in ("abstract_only", "no_access"):
            detail.append({"pid": pid, "role": role, "status": f"skipped: full text not accessible ({r.get('access')})"})
            continue
        inc = r.get("included", {})
        if pid in drop and r.get("stage") not in VERIFIED_STAGES:
            detail.append({"pid": pid, "role": role, "status": "dropped in planning variant (flagged FT-NOBASELINE candidate)"})
            continue
        if inc.get("decision") != "include" or inc.get("stratum") != "speed":
            status = (ft_code(inc.get("reason")) if inc.get("decision") == "exclude"
                      else f"{inc.get('decision')}/{inc.get('stratum')}")
            detail.append({"pid": pid, "role": role, "status": f"not in speed stratum ({status})",
                           "stage": r.get("stage")})
            continue
        v1 = r["rules"]["R1"]["verdict"]
        v2 = r["rules"]["R2"]["verdict"]
        fail = v1 == "fail" or v2 == "fail"
        used.append(pid)
        fails += int(fail)
        verified += int(r.get("stage") in VERIFIED_STAGES)
        detail.append({"pid": pid, "role": role, "R1": v1, "R2": v2, "R3": r["rules"]["R3"]["verdict"],
                       "R4": r["rules"]["R4"]["verdict"], "weak": fail, "stage": r.get("stage")})
    n = len(used)
    share = fails / n if n else float("nan")
    lo, hi = clopper_pearson(fails, n)
    complete = n == N_TARGET
    return {"n_speed_stratum": n, "n_target": N_TARGET, "complete": complete, "stopped_at": stopped,
            "n_fail_R1_or_R2": fails, "share": share, "ci95": [lo, hi], "band": band_g1(share),
            "verified_records": verified,
            "status": ("decision-grade" if complete and verified == n
                       else "provisional (incomplete set, LLM prefill or partial verification)"),
            "detail": detail}


def main():
    global SCREEN_EXCLUDED, ACCESS, SUPPLIED
    SCREEN_EXCLUDED = screen_excluded()
    ACCESS, SUPPLIED = access_maps()
    recs = load_records()
    arxiv_seq = [(pid, f"pilot {i}") for i, pid in enumerate(pids("pilot_provisional.csv"), 1)]
    arxiv_seq += [(pid, f"top-up {i}") for i, pid in enumerate(pids("pilot_topup_order.csv"), 1)]
    final_seq = [(pid, f"order {i}") for i, pid in enumerate(pids("pilot_final_order.csv"), 1)]
    flags_file = ROOT / "audit" / "coding" / "verifier_flags.csv"
    flagged = {f["pid"] for f in csv.DictReader(open(flags_file, encoding="utf-8"))
               if f["flag"] == "FT-NOBASELINE candidate"} if flags_file.exists() else set()
    plan_note = ("planning variant only: unverified records flagged as FT-NOBASELINE candidates "
                 "(audit/coding/verifier_flags.csv) are treated as excluded; never a gate decision")
    gates = {}
    if final_seq:
        gates["G1"] = {**g1(recs, final_seq), "pilot_note": "decision order over the complete screened pool "
                       "(PROTOCOL §11 decision-pilot row); inclusion is decided at full text (PROTOCOL §11 screening-check row)"}
        gates["G1_planning_flags_excluded"] = {**g1(recs, final_seq, frozenset(flagged)), "note": plan_note}
    gates["G1_provisional_arxiv_pilot"] = {**g1(recs, arxiv_seq), "pilot_note":
                                           "provisional arXiv-stratum pilot plus pre-registered top-ups"}
    gates["G1_provisional_arxiv_pilot_planning"] = {**g1(recs, arxiv_seq, frozenset(flagged)), "note": plan_note}
    g2_file = ROOT / "evidence" / "g2_provisional.json"
    gates["G2"] = json.loads(g2_file.read_text(encoding="utf-8")) if g2_file.exists() else None
    (ROOT / "evidence" / "gates.json").write_text(json.dumps(gates, indent=2), encoding="utf-8")
    g = gates.get("G1")
    if g and g["status"] == "decision-grade":
        from tools.numbers import register
        register("N011", g["share"], text=f"{100 * g['share']:.0f} % ({g['n_fail_R1_or_R2']}/{g['n_speed_stratum']}; "
                                          f"95 % CI {100 * g['ci95'][0]:.0f}–{100 * g['ci95'][1]:.0f} %)",
                 source="evidence/gates.json", script="analysis/gates.py",
                 note=f"G1: share of the first 20 verified speed-stratum records in the decision order failing R1 or "
                      f"R2; band: {g['band']}")
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "detail"} if k.startswith("G1") else v)
                      for k, v in gates.items()}, indent=2))


if __name__ == "__main__":
    main()
