"""Build Online Resource 6 (re-test census) for the v3 manuscript.

    python v3/tools/build_or6.py

Uses the helpers of manuscript/smo_v2/online_resources/build_or.py (imported read-only; its output folder is redirected
to v3/manuscript/online_resources/). Content, reproduced as written: 1 the census pre-registration with its §9
deviation log (v3/plan/CENSUS_PREREG.md); 2 the claim frame (v3/census/frame.json); 3 per claim, RESULT.md and
REPAIRS.md from v3/runs/<PID>/; 4 the third-party commits (v3/third_party/COMMITS.json).
"""
import importlib.util
import json
import pathlib

V3 = pathlib.Path(__file__).resolve().parents[1]
ROOT = V3.parent
spec = importlib.util.spec_from_file_location("build_or", ROOT / "manuscript" / "smo_v2" / "online_resources" / "build_or.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
B.OUT = V3 / "manuscript" / "online_resources"
B.UNI.update({"°": r"\ensuremath{^\circ}", "θ": r"\ensuremath{\theta}", "π": r"\ensuremath{\pi}"})  # census texts


# The census files were written during the work, where "the user" is the first author giving instructions; in the
# Online Resource the decisions are the authors'. The local download path is dropped. The files themselves are unchanged.
TERMS = [("the user approved the budget rule", "the authors approved the budget rule"),
         ("(user, 2026-09-25)", "(authors' decision, 2026-09-25)"),
         ("files supplied by the user (zip `E:/DL/16902961.zip`)", "files downloaded by the authors from the figshare page (zip `16902961.zip`)"),
         ("user approval 2026-09-25", "authors' approval 2026-09-25"),
         ("stopped by user decision", "stopped by the authors' decision"),
         ("The user downloaded the article's zip (`E:/DL/16902961.zip`,", "The authors downloaded the article's zip (`16902961.zip`,"),
         ("by user\ndecision", "by the authors'\ndecision"), ("by user decision", "by the authors' decision"),
         ("the zip path read `E:/DL` followed by", "the zip path read a local folder name followed by"),
         ("(a shell escape turned `/16` into U+000E", "(a shell escape turned a backslash sequence into U+000E"),
         ("it now reads `E:/DL/16902961.zip`", "it now reads the intended path")]


def md(path):
    """A census markdown file as LaTeX; Windows paths are shown with forward slashes (backslashes break the build)."""
    s = path.read_text(encoding="utf-8").replace("\\", "/")
    for a, b in TERMS:
        s = s.replace(a, b)
    return B.md_to_tex(s, shift=1)

CLAIMS = ["P00610", "P00080", "P00183", "P00663", "P00140", "P00647"]


def main():
    P = [B.inline(
        "This resource documents the census of every speed claim in the analysis sample whose article links public "
        "code (Sect. 2.6 and Sect. 3.7 of the paper). The pre-registration was frozen before the first run; every later "
        "decision is a dated row of its §9, entered before the run it governs. The per-claim results and repairs follow "
        "as written in the census folder, with 'the user' rendered as 'the authors'. The pre-registration was written when the "
        "census was planned for a later revision; it was completed before submission. Integrity: "
        "`v3/evidence/MANIFEST.sha256` in the released repository.")]
    P.append(r"\section*{1. Pre-registration and deviation log}")
    P.append(md(V3 / "plan" / "CENSUS_PREREG.md"))
    P.append(r"\section*{2. Claim frame}")
    frame = json.loads((V3 / "census" / "frame.json").read_text(encoding="utf-8"))
    P.append(B.longtable(["Record", "Year", "Published factor", "R1", "R2", "R3", "R4", "Repository", "Status"],
                         [[r["pid"], r["year"], r["claimed_speedup"], r["rules"].get("R1"), r["rules"].get("R2"),
                           r["rules"].get("R3"), r["rules"].get("R4"), ", ".join(r["repos"]) or "–", r["status"]]
                          for r in frame],
                         widths=[0.07, 0.05, 0.07, 0.05, 0.05, 0.05, 0.05, 0.3, 0.26], size=r"\scriptsize"))
    P.append(r"\section*{3. Results and repairs by claim}")
    for pid in CLAIMS:
        for name in ("RESULT.md", "REPAIRS.md"):
            f = V3 / "runs" / pid / name
            if f.exists():
                P.append(md(f))
    P.append(r"\section*{4. Third-party code}")
    commits = json.loads((V3 / "third_party" / "COMMITS.json").read_text(encoding="utf-8"))
    P.append(B.longtable(["Record", "Repository", "Commit", "Licence"],
                         [[c["pid"], c["repo"], c["commit"][:12], c["licence"]] for c in commits],
                         widths=[0.08, 0.42, 0.14, 0.32], size=r"\scriptsize"))
    P.append(B.inline("P00610 uses Keff-CFD at commit 720be71 (§9 of the pre-registration)."))
    B.write_doc(6, "Re-test census of code-linked speed claims", "\n\n".join(P))


if __name__ == "__main__":
    main()
