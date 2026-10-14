"""Working copy of deep-dehom's package (commit 73529a9) with one renamed keyword, so it runs with scikit-image 0.26.

    python v3/runs/P00140/port.py

scikit-image renamed the structuring-element keyword 'selem' to 'footprint' (deprecated in 0.19, removed later); the
repository pins 0.18.3, which has no wheels for Python 3.12. Every 'selem=' in deepdehom/*.py becomes 'footprint='
(same argument, documented replacement). Writes work/deepdehom/ and work/PATCHES.diff.
"""
import difflib
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parents[2] / "v3" / "third_party" / "deep-dehom" / "deepdehom"
WORK = HERE / "work"


def main():
    if WORK.exists():
        shutil.rmtree(WORK)
    shutil.copytree(SRC, WORK / "deepdehom")
    diffs, n = [], 0
    for p in sorted((WORK / "deepdehom").glob("*.py")):
        t = p.read_text(encoding="utf-8")
        k = t.count("selem=")
        if k:
            new = t.replace("selem=", "footprint=")
            p.write_text(new, encoding="utf-8")
            diffs += difflib.unified_diff(t.splitlines(True), new.splitlines(True), f"a/deepdehom/{p.name}",
                                          f"b/deepdehom/{p.name}")
            n += k
    (WORK / "PATCHES.diff").write_text("".join(diffs), encoding="utf-8")
    print(f"{n} keyword replacements")


if __name__ == "__main__":
    main()
