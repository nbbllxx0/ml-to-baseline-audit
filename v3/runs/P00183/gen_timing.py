"""P00183 ML side: time the retrained generator and write its designs for all 100 test angles.

    PIN_PCORES=1 v3/.venv/census-tf/python.exe v3/runs/P00183/gen_timing.py

Builds the generator graph from the patched working copy (work/main_1D.py, the code above its 'sess = tf.Session()'
line), opens a session with one intra-op and one inter-op thread, restores the last checkpoint saved by training
(work/model_save/), and times one forward pass of the fixed batch of 5 angles: warm-up + 3 repeats of 50 calls; time
per angle = batch time / 5. Writes timing/gen.json and timing/phi_gen_100.mat (the designs for linspace(0, pi, 100),
in the row order main_1D.py uses).
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import statistics
import time

import numpy as np
import scipy.io as sio

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = HERE / "work"
OUT = HERE / "timing"


def main():
    spec = importlib.util.spec_from_file_location("pin", ROOT / "tools" / "pin.py")
    pin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pin)
    pinning = pin.pin_from_env()
    src = (WORK / "main_1D.py").read_text(encoding="utf-8")
    head = src[:src.index("sess = tf.Session()")]
    head = head.replace("import matlab.engine\n", "")
    os.chdir(WORK)
    ns = {"__name__": "gen_timing"}
    exec(compile(head, "main_1D.py (graph part)", "exec"), ns)
    tf = ns["tf"]
    sess = tf.Session(config=tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1))
    ckpt = tf.train.latest_checkpoint(str(WORK / "model_save"))
    if ckpt is None:
        ckpts = sorted((WORK / "model_save").glob("*.index"), key=lambda p: p.stat().st_mtime)
        ckpt = str(ckpts[-1].with_suffix(""))
    tf.train.Saver().restore(sess, ckpt)
    P_output, F_input, bs = ns["P_output"], ns["F_input"], ns["batch_size"]
    theta = np.linspace(0.0, np.pi, 100)
    F = theta[:, None]
    per = []
    for rep in range(4):
        t0 = time.perf_counter()
        for _ in range(50):
            sess.run(P_output, feed_dict={F_input: F[:bs]})
        dt = (time.perf_counter() - t0) / 50 / bs
        if rep:
            per.append(dt)
    phi = np.concatenate([sess.run(P_output, feed_dict={F_input: F[i:i + bs]}).reshape(bs, -1)
                          for i in range(0, 100, bs)], axis=0)
    # main_1D.py flattens the (batch, width=nely, height=nelx) output with tf.reshape to (batch, nn) and transposes;
    # the stored phi rows follow the same flattening, as phi_true_1D.mat does.
    OUT.mkdir(exist_ok=True)
    sio.savemat(OUT / "phi_gen_100.mat", {"phi_gen": phi, "theta": theta})
    res = {"meta": {"pinning": pinning, "tensorflow": tf.__version__, "checkpoint": pathlib.Path(ckpt).name,
                    "threads": 1},
           "per_angle": {"median_s": statistics.median(per), "min_s": min(per), "max_s": max(per), "repeats_s": per},
           "batch_size": bs}
    (OUT / "gen.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
