"""One-time setup of the v3 manuscript (SMO v2 + the re-test census) in v3/manuscript/. v2 files are read, not written.

    python v3/tools/setup_manuscript.py

Copies from manuscript/smo_v2/: manuscript.md, build.py, references_audited.bib, figures/, tables/, the Online
Resources 1-5 (out/*.pdf, the records CSV) and the cover-letter source; from manuscript/: package_submission.py.
Path changes (each asserted to occur once):
  build.py: numbers from evidence/numbers.json merged with v3/evidence/numbers_v3.json; the arXiv build writes to
            v3/manuscript/arxiv/ instead of manuscript/arxiv/.
  package_submission.py: every input and output folder inside v3/manuscript/; six Online Resources.
Refuses to run if v3/manuscript/manuscript.md exists, so later edits are never overwritten.
"""
import pathlib
import shutil

V3 = pathlib.Path(__file__).resolve().parents[1]
ROOT = V3.parent
SRC = ROOT / "manuscript" / "smo_v2"
DST = V3 / "manuscript"


def patch(path: pathlib.Path, edits):
    t = path.read_text(encoding="utf-8")
    for a, b in edits:
        if t.count(a) != 1:
            raise SystemExit(f"{path.name}: target found {t.count(a)} times: {a!r}")
        t = t.replace(a, b)
    path.write_text(t, encoding="utf-8")


def main():
    if (DST / "manuscript.md").exists():
        raise SystemExit("v3/manuscript already set up")
    DST.mkdir(parents=True, exist_ok=True)
    for f in ("manuscript.md", "build.py", "references_audited.bib"):
        shutil.copy2(SRC / f, DST / f)
    for d in ("figures", "tables"):
        shutil.copytree(SRC / d, DST / d)
    (DST / "online_resources").mkdir()
    for f in sorted((SRC / "online_resources" / "out").glob("Online_Resource_*")):
        shutil.copy2(f, DST / "online_resources" / f.name)
    (DST / "submission").mkdir()
    shutil.copy2(SRC / "submission" / "cover_letter_src.md", DST / "submission" / "cover_letter_src.md")
    shutil.copy2(ROOT / "manuscript" / "package_submission.py", DST / "package_submission.py")
    patch(DST / "build.py", [
        ('NUM = ROOT / "evidence" / "numbers.json"\n',
         'NUM = ROOT / "evidence" / "numbers.json"\nNUM_V3 = ROOT / "v3" / "evidence" / "numbers_v3.json"  # census numbers (v3)\n'),
        ('    reg = json.loads(NUM.read_text(encoding="utf-8"))\n',
         '    reg = json.loads(NUM.read_text(encoding="utf-8"))\n'
         '    reg.update(json.loads(NUM_V3.read_text(encoding="utf-8")))\n'),
        ('        OUT = ROOT / "manuscript" / "arxiv"\n', '        OUT = HERE / "arxiv"\n'),
    ])
    patch(DST / "package_submission.py", [
        ('ROOT = pathlib.Path(__file__).resolve().parents[1]\n', 'ROOT = pathlib.Path(__file__).resolve().parents[2]\n'),
        ('SMO = ROOT / "manuscript" / "smo_v2" / "latex"\n', 'SMO = ROOT / "v3" / "manuscript" / "latex"\n'),
        ('ARX = ROOT / "manuscript" / "arxiv"\n', 'ARX = ROOT / "v3" / "manuscript" / "arxiv"\n'),
        ('ORS = ROOT / "manuscript" / "smo_v2" / "online_resources" / "out"\n',
         'ORS = ROOT / "v3" / "manuscript" / "online_resources"\n'),
        ('SUB = ROOT / "manuscript" / "smo_v2" / "submission"\n', 'SUB = ROOT / "v3" / "manuscript" / "submission"\n'),
        ('    for n in range(1, 6):\n', '    for n in range(1, 7):\n'),
    ])
    print("v3/manuscript set up")


if __name__ == "__main__":
    main()
