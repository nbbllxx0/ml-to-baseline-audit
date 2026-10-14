"""Write matlab/infill_logged.m: the repository's infill_topology_optimization.m with logging only.

    python v3/runs/P00183/make_logged.py

Changes: the function name and a fourth output; a timer started at function entry; the load vector preallocated
(repair, REPAIRS.md); at the end of each projection stage (just before 'beta = 2*beta;') one log entry with the elapsed time since the call started,
the design phi, beta and the FE-analysis count. The algorithm is untouched. Diff in matlab/infill_logged.diff.
"""
import difflib
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parents[2] / "v3" / "third_party" / "Theory_Driven_TO" / "CAD code" / "infill_topology_optimization.m"
OUT = HERE / "matlab"

EDITS = [
    ("function [c, y, budget] = infill_topology_optimization(x)",
     "function [c, y, budget, LOG] = infill_logged(x)\n    t_call = tic; LOG = struct('t', {}, 'phi', {}, 'beta', {}, 'budget', {});"),
    ("        beta = 2*beta;\n",
     "        LOG(end+1) = struct('t', toc(t_call), 'phi', phi, 'beta', beta, 'budget', budget);\n        beta = 2*beta;\n"),
    # Repair (REPAIRS.md): F is never preallocated in the released file, so it ends at the load DOF (9,882 entries) and
    # F(freedofs) fails for the 9,922-DOF model. Preallocate it as the repository's calculate_compliance.m does.
    ("    Fx=force*sin(x);\n",
     "    F = sparse(2*(nely+1)*(nelx+1),1);\n    Fx=force*sin(x);\n"),
]


EVAL_SRC = SRC.with_name("calculate_compliance.m")
# Repair (REPAIRS.md): the released evaluator stops at an undefined variable (rho_bar) in its constraint lines, after
# the compliance is computed. The copy returns the compliance only and drops those two lines.
EVAL_EDITS = [
    ("function [c, g, global_density] = calculate_compliance(x, y)", "function c = compliance_eval(x, y)"),
    ("    g = (sum(rho_bar.^p)/nely/nelx)^(1/p) - alpha;\n", ""),
    ("    global_density = rho'*ones(nn,1)/nn-alpha2;\n", ""),
]


def patch(src, edits, out_name):
    orig = src.read_text(encoding="utf-8", errors="strict")
    nl = "\r\n" if "\r\n" in orig else "\n"
    t = orig
    for a, b in edits:
        a2, b2 = a.replace("\n", nl), b.replace("\n", nl)
        n = t.count(a2)
        if n != 1:
            raise SystemExit(f"edit target found {n} times in {src.name}: {a!r}")
        t = t.replace(a2, b2)
    (OUT / out_name).write_text(t, encoding="utf-8", newline="")
    d = difflib.unified_diff(orig.splitlines(True), t.splitlines(True), src.name, out_name)
    (OUT / (pathlib.Path(out_name).stem + ".diff")).write_text("".join(d), encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    patch(EVAL_SRC, EVAL_EDITS, "compliance_eval.m")
    orig = SRC.read_text(encoding="utf-8", errors="strict")
    nl = "\r\n" if "\r\n" in orig else "\n"
    t = orig
    for a, b in EDITS:
        a2, b2 = a.replace("\n", nl), b.replace("\n", nl)
        n = t.count(a2)
        if n != 1:
            raise SystemExit(f"edit target found {n} times: {a!r}")
        t = t.replace(a2, b2)
    OUT.mkdir(exist_ok=True)
    (OUT / "infill_logged.m").write_text(t, encoding="utf-8", newline="")
    d = difflib.unified_diff(orig.splitlines(True), t.splitlines(True), "infill_topology_optimization.m",
                             "infill_logged.m")
    (OUT / "infill_logged.diff").write_text("".join(d), encoding="utf-8")
    print("written")


if __name__ == "__main__":
    main()
