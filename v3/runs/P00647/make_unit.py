"""Write Top3D_maxbulk_unit.m: the repository's Top3D_maxbulk.m with the loop cap set to 10 and a per-iteration timer.

    python v3/runs/P00647/make_unit.py

Changes (CENSUS_PREREG §9, dev17): function name; 'maxloop = 600' -> 'maxloop = 10'; a timer started at the top of
each iteration and printed with the iteration line. The iteration itself is unchanged. Diff in Top3D_maxbulk_unit.diff.
"""
import difflib
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parents[2] / "v3" / "third_party" / "DL3DTO-Deep-Learning-for-3D-Topology-Optimization" / "Top3D_maxbulk.m"
EDITS = [
    ("function [xPhys,DH,loop]=Top3D_maxbulk(Micro_struct,voxel, volfrac, penal, rmin,ft)",
     "function [xPhys,DH,loop]=Top3D_maxbulk_unit(Micro_struct,voxel, volfrac, penal, rmin,ft)"),
    ("maxloop = 600;", "maxloop = 10;"),
    ("    loop = loop+1; \n", "    loop = loop+1; t_it = tic;\n"),
    ("    fprintf(' It.:%5i Obj.:%11.4f Micro_Vol.:%7.3f Micro_ch.:%7.3f\\n',...\n        loop,c,mean(xPhys(:)),Micro.change);",
     "    fprintf(' It.:%5i Obj.:%11.4f Micro_Vol.:%7.3f Micro_ch.:%7.3f seconds:%9.3f\\n',...\n"
     "        loop,c,mean(xPhys(:)),Micro.change,toc(t_it));"),
]


def main():
    orig = SRC.read_text(encoding="utf-8")
    nl = "\r\n" if "\r\n" in orig else "\n"
    t = orig
    for a, b in EDITS:
        a2, b2 = a.replace("\n", nl), b.replace("\n", nl)
        n = t.count(a2)
        if n != 1:
            raise SystemExit(f"edit target found {n} times: {a!r}")
        t = t.replace(a2, b2)
    (HERE / "Top3D_maxbulk_unit.m").write_text(t, encoding="utf-8", newline="")
    d = difflib.unified_diff(orig.splitlines(True), t.splitlines(True), "Top3D_maxbulk.m", "Top3D_maxbulk_unit.m")
    (HERE / "Top3D_maxbulk_unit.diff").write_text("".join(d), encoding="utf-8")
    print("written")


if __name__ == "__main__":
    main()
