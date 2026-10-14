"""P00150 predictor (model_predictor_64x64, Mendeley data, CC BY 4.0) on the 100 validation inputs, timed per design.

    python -m retest.p00150_harness.run_pen          # conda env tf_p00150 (TensorFlow on the CPU; see §9)

Loads the Keras SavedModel unchanged from the downloaded archive (extracted to a temporary folder outside the
project). Per case, batch size 1: inputs R_k (162), R_s (162) and M_tar (1) from inputrows_8x8.npz; the 64x64 output
is kept. Timing: a tf.function with a fixed input signature (graph mode, the fastest single-design call), after 20
warm-up calls; per case the median of 5 timed calls; model.predict is timed once per case for reference. Pinned
when PIN_PCORES=1. Writes retest/runs/p00150/pen/pen.json and designs.npz.
"""
import json
import pathlib
import sys
import tempfile
import time
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
MODEL_ZIP = ROOT / "retest" / "targets" / "P00150_mendeley" / "model_predictor_64x64.zip"
OUT = ROOT / "retest" / "runs" / "p00150" / "pen"


def main():
    from tools.pin import pin_from_env
    pinning = pin_from_env()
    import numpy as np
    import tensorflow as tf
    from retest.p00150_harness.problems import load_inputs
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "pen.json").exists():
        raise SystemExit("pen.json exists")
    X = load_inputs().astype(np.float32)
    with tempfile.TemporaryDirectory() as tmp:
        zipfile.ZipFile(MODEL_ZIP).extractall(tmp)
        model = tf.keras.models.load_model(str(pathlib.Path(tmp) / "model_predictor_64x64"), compile=False)
    names = [t.name.split(":")[0] for t in model.inputs]
    outs = [o.name for o in model.outputs]
    i64 = [k for k, o in enumerate(model.outputs) if o.shape[-1] == 4096]
    if len(i64) != 1:
        raise SystemExit(f"cannot identify the 64x64 output among {[o.shape for o in model.outputs]}")
    i64 = i64[0]
    spec = [tf.TensorSpec((1, 162), tf.float32), tf.TensorSpec((1, 162), tf.float32), tf.TensorSpec((1, 1), tf.float32)]

    @tf.function(input_signature=spec)
    def infer(rk, rs, m):
        return model([rk, rs, m], training=False)[i64]

    def split(k):
        row = X[k:k + 1]
        return tf.constant(row[:, :162]), tf.constant(row[:, 162:324]), tf.constant(row[:, 324:325])

    for _ in range(20):
        infer(*split(0)).numpy()
    res, designs = [], {}
    for k in range(len(X)):
        a = split(k)
        ts = []
        for _ in range(5):
            t0 = time.perf_counter()
            y = infer(*a).numpy()
            ts.append(time.perf_counter() - t0)
        t0 = time.perf_counter()
        yp = model.predict(list(a), verbose=0)[i64]
        t_predict = time.perf_counter() - t0
        if not np.allclose(y, yp, atol=1e-5):
            raise SystemExit(f"case {k}: tf.function and predict outputs differ")
        designs[f"case{k:03d}"] = y.reshape(64, 64)
        ts.sort()
        res.append({"case": k, "t_median_s": ts[2], "t_min_s": ts[0], "t_max_s": ts[-1], "t_predict_s": t_predict})
    np.savez_compressed(OUT / "designs.npz", **designs)
    meta = {"tensorflow": tf.__version__, "inputs": names, "outputs": outs, "output_64x64_index": i64,
            "devices": [d.name for d in tf.config.list_physical_devices()], "cpu_pinning": pinning,
            "timing": "tf.function with fixed signature, batch 1; median of 5 calls per case after 20 warm-up calls",
            "cases": res}
    (OUT / "pen.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    t = sorted(r["t_median_s"] for r in res)
    print(f"median per-design inference {1e3 * t[len(t) // 2]:.3f} ms; predict median "
          f"{1e3 * sorted(r['t_predict_s'] for r in res)[len(res) // 2]:.3f} ms")


if __name__ == "__main__":
    main()
