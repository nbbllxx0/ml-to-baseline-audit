"""P00610 timed runs (protocol: v3/plan/CENSUS_PREREG.md §9, row "P00610 timing protocol").

    PIN_PCORES=1 v3/.venv/census-torch/Scripts/python.exe v3/runs/P00610/timing.py classical   # both released solvers
    PIN_PCORES=1 v3/.venv/census-torch/Scripts/python.exe v3/runs/P00610/timing.py direct      # L2, SuperLU
    PIN_PCORES=1 v3/.venv/census-tf/python.exe            v3/runs/P00610/timing.py cnn         # released CNN, CPU

Each mode times the 12 protocol images at 4 ratios: one warm-up and 3 timed repeats, median, minimum and maximum.
"direct" and "cnn" also score all 100 sampled images against the published k_eff (quality). Writes
timing/<mode>.json.
"""
from __future__ import annotations

import csv
import json
import os
import pathlib
import platform
import statistics
import subprocess
import sys
import tempfile
import time

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from pin import pin_from_env  # noqa: E402

OUT = HERE / "timing"
IMAGES = ["CirclePack/00089.jpg", "CirclePack/00454.jpg", "CirclePack/00471.jpg", "EllipsePack/00446.jpg",
          "EllipsePack/00459.jpg", "EllipsePack/00999.jpg", "QuadrilateralPack/00047.jpg", "QuadrilateralPack/00118.jpg",
          "QuadrilateralPack/00290.jpg", "QSGS/00063.jpg", "QSGS/00379.jpg", "QSGS/00897.jpg"]
RATIOS = {10.0: ("Keff_130k_10p.csv", "r10"), 50.0: ("Keff_130k_50p.csv", "r50"), 100.0: ("Keff_130k_100p.csv", "r100"),
          341.7: ("Keff_130k_Al.csv", "r341")}
OFFSET = {"CirclePack": 0, "EllipsePack": 40000, "QuadrilateralPack": 80000, "QSGS": 120000}
REPEATS = 3


def gray(rel: str) -> np.ndarray:
    return np.asarray(Image.open(HERE / "data" / "images" / rel).convert("L"))


def published() -> dict[float, list[float]]:
    out = {}
    for ks, (name, _) in RATIOS.items():
        rows = list(csv.reader(open(HERE / "data" / "cfd" / name, encoding="utf-8")))
        out[ks] = [float(r[0]) for r in rows if r and r[0] not in ("k_eff", "keff")]
    return out


def pub_value(pub, rel: str, ks: float) -> float:
    folder, name = rel.split("/")
    return pub[ks][OFFSET[folder] + int(pathlib.Path(name).stem)]


def summarize(times: list[float]) -> dict:
    return {"median_s": statistics.median(times), "min_s": min(times), "max_s": max(times), "repeats_s": times}


def classical():
    from validate import INPUT  # same input file as the agreement check
    res = []
    for solver in ("tdma", "gs"):
        for rel in IMAGES:
            for ks in RATIOS:
                with tempfile.TemporaryDirectory(dir=OUT) as d:
                    d = pathlib.Path(d)
                    Image.fromarray(gray(rel)).save(d / "img.png")
                    (d / "input.txt").write_text(INPUT.format(ks=ks), encoding="ascii")
                    times, walls = [], []
                    for rep in range(REPEATS + 1):
                        t0 = time.perf_counter()
                        subprocess.run([str(HERE / "build" / f"keff2D_{solver}.exe")], cwd=d, check=True,
                                       capture_output=True)
                        wall = time.perf_counter() - t0
                        row = next(csv.reader(open(d / "out.csv")))
                        if rep:
                            times.append(float(row[14]))
                            walls.append(wall)
                        (d / "out.csv").unlink()
                res.append({"solver": solver, "image": rel, "ks": ks, "keff": float(row[0]), "iter": int(row[3]),
                            **summarize(times), "wall_median_s": statistics.median(walls)})
                print(solver, rel, ks, res[-1]["median_s"], flush=True)
    return res


def direct():
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    from strong import keff_direct
    pub = published()
    res = []
    for rel in IMAGES:
        img = gray(rel)
        for ks in RATIOS:
            times = []
            for rep in range(REPEATS + 1):
                t0 = time.perf_counter()
                k = keff_direct(img, ks)
                if rep:
                    times.append(time.perf_counter() - t0)
            res.append({"image": rel, "ks": ks, "keff": k, "keff_published": pub_value(pub, rel, ks), **summarize(times)})
            print("direct", rel, ks, res[-1]["median_s"], flush=True)
    quality = []
    for p in sorted((HERE / "data" / "images").glob("*/*.jpg")):
        rel = f"{p.parent.name}/{p.name}"
        img = gray(rel)
        for ks in RATIOS:
            k = keff_direct(img, ks)
            quality.append({"image": rel, "ks": ks, "keff": k, "keff_published": pub_value(pub, rel, ks)})
    return res, quality


def cnn():
    import tensorflow as tf
    tf.config.threading.set_intra_op_parallelism_threads(1)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.set_visible_devices([], "GPU")
    import tf_keras as k3
    pub = published()
    models = {ks: k3.models.load_model(str(ROOT / "v3" / "third_party" / "CNN-Keff" / d)) for ks, (_, d) in RATIOS.items()}
    # Released example (load_and_predict.py): grayscale, pixel < 150 -> 0, else 1, shape (1, 128, 128).
    binar = lambda img: (img >= 150).astype(np.float32)[None]
    res = []
    calls = 50
    for rel in IMAGES:
        x = tf.constant(binar(gray(rel)))
        for ks, m in models.items():
            times = []
            for rep in range(REPEATS + 1):
                t0 = time.perf_counter()
                for _ in range(calls):
                    y = m(x, training=False)
                dt = (time.perf_counter() - t0) / calls
                if rep:
                    times.append(dt)
            res.append({"image": rel, "ks": ks, "keff": float(np.asarray(y)[0, 0]),
                        "keff_published": pub_value(pub, rel, ks), "calls_per_repeat": calls, **summarize(times)})
            print("cnn", rel, ks, res[-1]["median_s"], flush=True)
    quality = []
    for p in sorted((HERE / "data" / "images").glob("*/*.jpg")):
        rel = f"{p.parent.name}/{p.name}"
        x = tf.constant(binar(gray(rel)))
        for ks, m in models.items():
            quality.append({"image": rel, "ks": ks, "keff": float(np.asarray(m(x, training=False))[0, 0]),
                            "keff_published": pub_value(pub, rel, ks)})
    return res, quality, {"tensorflow": tf.__version__, "tf_keras": k3.__version__}


def main():
    mode = sys.argv[1]
    OUT.mkdir(exist_ok=True)
    sys.path.insert(0, str(HERE))
    pinning = pin_from_env()
    meta = {"mode": mode, "python": platform.python_version(), "pinning": pinning, "numpy": np.__version__,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if mode == "classical":
        out = {"timing": classical()}
    elif mode == "direct":
        import scipy
        meta["scipy"] = scipy.__version__
        t, q = direct()
        out = {"timing": t, "quality": q}
    elif mode == "cnn":
        t, q, v = cnn()
        meta.update(v)
        out = {"timing": t, "quality": q}
    else:
        raise SystemExit("mode: classical | direct | cnn")
    meta["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (OUT / f"{mode}.json").write_text(json.dumps({"meta": meta, **out}, indent=1) + "\n", encoding="utf-8")
    print("wrote", OUT / f"{mode}.json")


if __name__ == "__main__":
    main()
