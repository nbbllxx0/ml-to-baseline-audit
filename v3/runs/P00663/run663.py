"""P00663 one run inside the census-p00663:3 container (FEniCS 2019.1, PyTorch 1.8 CPU).

    docker run --rm -v <repo>:/repo:ro -v <this folder>:/out -v <cache>:/root/.cache -w /repo census-p00663:3 \
        python /out/run663.py classic|cnn <run-tag>

Experiment 3.1.3 of the repository notebook with setting = 0 (nominal load g = (0, -5000), the load of the article's
Table 1 and the first row of Table 4): 'classic' calls LE_optimzation(...) exactly as the notebook does, 'cnn' calls
run_CNN_optimization on a fresh LEProblem(bridge2D()). The timed interval is that call, as the notebook's tic()/tac()
brackets it. One run per process, so every run starts from the module-level objects the notebook starts from.
Writes /out/results/<run-tag>.json.
"""
import json
import os
import sys
import time

os.environ.setdefault("MPLBACKEND", "Agg")
sys.path.insert(0, "/repo")


def main():
    alg, tag = sys.argv[1], sys.argv[2]
    if alg == "classic":
        import optimizer as O
        O.tic()                      # the notebook calls tic() before LE_optimzation; the loop's tac() needs it
        t0 = time.perf_counter()
        res = O.LE_optimzation(problem=O.LEP, tau_adapter=O.tau_adapter, maxIteration=750, plot_parameters=True,
                               plot_steps=False, stoch=False, plot_every=100)
        dt = time.perf_counter() - t0
        Js, problem = res[6], res[9]
        out = {"alg": alg, "seconds": dt, "iterations": len(Js), "J": float(Js[-1]),
               "compliance": float(O.compliance(problem)), "vertices": int(problem.mesh.num_vertices())}
    elif alg == "cnn":
        import CNN_optimizer as C
        lep = C.LEProblem(C.bridge2D())
        t0 = time.perf_counter()
        Js = C.run_CNN_optimization(lep)
        dt = time.perf_counter() - t0
        out = {"alg": alg, "seconds": dt, "iterations": len(Js), "J": float(Js[-1]),
               "compliance": float(C.compliance(lep)), "vertices": int(lep.mesh.num_vertices())}
    else:
        raise SystemExit("alg: classic | cnn")
    os.makedirs("/out/results", exist_ok=True)
    with open(f"/out/results/{tag}.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("RESULT", json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
