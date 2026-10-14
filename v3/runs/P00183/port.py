"""Make the working copy of P00183's case-1 code (Theory_Driven_TO @ 02de10e, "CAD code/") runnable under Python 3.11
and TensorFlow 2.21, with the smallest changes. Every change is listed in PATCHES and written to work/PATCHES.diff.

    v3/.venv/census-tf/python.exe v3/runs/P00183/port.py

Changes (permitted repairs, pre-registration §6.2; REPAIRS.md):
1. TensorFlow 1 API -> tf.compat.v1 with v2 behaviour disabled (documented equivalent for tf.placeholder,
   tf.Session, tf.train.*).
2. Python 2 integer division in tensor shapes and loop counts -> floor division (the Python 2 meaning).
3. Seeds for random, numpy and TensorFlow (20260925): the original draws the initial training set without a seed.
4. MATLAB engine: change the engine's folder to the working copy before calling cal_c_1D, so the relative paths in
   cal_c_1D.m ('experiment_result/...') resolve as they would when started from this folder.
"""
from __future__ import annotations

import difflib
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parents[2] / "v3" / "third_party" / "Theory_Driven_TO" / "CAD code"
WORK = HERE / "work"

PATCHES = [
    ("import tensorflow as tf\n", "import tensorflow.compat.v1 as tf\ntf.disable_v2_behavior()\n"),
    ("import matlab.engine\n",
     "import matlab.engine\nrandom.seed(20260925); np.random.seed(20260925); tf.set_random_seed(20260925)\n"),
    ("[batch_size, width/8, height/8, 1]", "[batch_size, width//8, height//8, 1]"),
    ("output_shape=[batch_size, width/8, height/8, deconv2_1_features]",
     "output_shape=[batch_size, width//8, height//8, deconv2_1_features]"),
    ("output_shape=[batch_size, width/4, height/4, deconv2_2_features]",
     "output_shape=[batch_size, width//4, height//4, deconv2_2_features]"),
    ("output_shape=[batch_size, width/4, height/4, deconv3_1_features]",
     "output_shape=[batch_size, width//4, height//4, deconv3_1_features]"),
    ("output_shape=[batch_size, width/2, height/2, deconv3_2_features]",
     "output_shape=[batch_size, width//2, height//2, deconv3_2_features]"),
    ("output_shape=[batch_size, width/2, height/2, deconv4_1_features]",
     "output_shape=[batch_size, width//2, height//2, deconv4_1_features]"),
    ("output_shape=[batch_size, width/1, height/1, deconv4_2_features]",
     "output_shape=[batch_size, width//1, height//1, deconv4_2_features]"),
    ("output_shape=[batch_size, width/1, height/1, 1]", "output_shape=[batch_size, width//1, height//1, 1]"),
    ("h_dim = width/8*height/8", "h_dim = width//8*height//8"),
    ("    ratio=testing_num/batch_size\n    final_error=0", "    ratio=testing_num//batch_size\n    final_error=0"),
    ("    ratio=testing_num/batch_size\n    phi_store=[]", "    ratio=testing_num//batch_size\n    phi_store=[]"),
    ("    eng = matlab.engine.start_matlab()\n    eng.cal_c_1D(nargout=0)",
     "    eng = matlab.engine.start_matlab()\n    eng.cd(os.getcwd(), nargout=0)\n    eng.cal_c_1D(nargout=0)"),
]


def main():
    if WORK.exists():
        shutil.rmtree(WORK)
    shutil.copytree(SRC, WORK)
    p = WORK / "main_1D.py"
    orig = p.read_text(encoding="utf-8")
    t = orig
    for a, b in PATCHES:
        n = t.count(a)
        if n != 1:
            raise SystemExit(f"patch target found {n} times: {a!r}")
        t = t.replace(a, b)
    p.write_text(t, encoding="utf-8")
    diff = difflib.unified_diff(orig.splitlines(True), t.splitlines(True), "a/CAD code/main_1D.py", "b/main_1D.py")
    (WORK / "PATCHES.diff").write_text("".join(diff), encoding="utf-8")
    print(f"{len(PATCHES)} patches applied")


if __name__ == "__main__":
    main()
