"""Run a VoroTO notebook's code cells in order, as the notebook would, and time every cell.

    PIN_PCORES=1 v3/.venv/census-torch/Scripts/python.exe v3/runs/P00080/run_notebook.py generate_dataset
    ... train_network | voronoi_TO

A working copy (work/) holds the repository's .py files and settings.yaml at commit d407d15 (copied, not edited),
the torch_sparse_solve stand-in (shim/, REPAIRS.md 1) and data/. Cells run with cwd work/notebooks, so the notebooks'
relative paths ('../settings.yaml', '../data/...') resolve inside the working copy. Plots go to the Agg backend and
plt.show() does nothing. Writes logs/<notebook>.json with per-cell wall times and the cell sources.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPO = ROOT / "v3" / "third_party" / "VoroTO"
WORK = HERE / "work"


def prepare():
    (WORK / "notebooks").mkdir(parents=True, exist_ok=True)
    (WORK / "data").mkdir(exist_ok=True)
    for f in list(REPO.glob("*.py")) + [REPO / "settings.yaml"]:
        shutil.copy2(f, WORK / f.name)
    shutil.copy2(HERE / "shim" / "torch_sparse_solve.py", WORK / "torch_sparse_solve.py")


def main():
    name = sys.argv[1]
    # Load tools/pin.py by path: putting tools/ on sys.path would shadow the standard-library 'numbers' module with
    # the project's tools/numbers.py.
    import importlib.util
    spec = importlib.util.spec_from_file_location("pin", ROOT / "tools" / "pin.py")
    pin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pin)
    pinning = pin.pin_from_env()
    prepare()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.show = lambda *a, **k: plt.close("all")
    nb = json.loads((REPO / "notebooks" / f"{name}.ipynb").read_text(encoding="utf-8"))
    cells = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    os.chdir(WORK / "notebooks")
    sys.path.insert(0, str(WORK))
    ns = {"__name__": "__main__"}
    log = {"notebook": name, "pinning": pinning, "cells": []}
    t_all = time.perf_counter()
    for i, src in enumerate(cells):
        src = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith(("%", "!")))
        t0 = time.perf_counter()
        exec(compile(src, f"<{name} cell {i}>", "exec"), ns)
        dt = time.perf_counter() - t0
        log["cells"].append({"index": i, "seconds": dt, "source": src})
        print(f"[cell {i}] {dt:.2f} s", flush=True)
    log["total_seconds"] = time.perf_counter() - t_all
    (HERE / "logs").mkdir(exist_ok=True)
    (HERE / "logs" / f"{name}.json").write_text(json.dumps(log, indent=1) + "\n", encoding="utf-8")
    print(f"total {log['total_seconds']:.1f} s")


if __name__ == "__main__":
    main()
