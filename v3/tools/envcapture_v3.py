"""The project's environment capture (tools/envcapture.py) for the census environments, writing to v3/env/.

    python v3/tools/envcapture_v3.py

Probes v3/.venv/census-tf and v3/.venv/census-torch. TensorFlow and other packages outside envcapture's list are
recorded by each timing script in its own output.
"""
import pathlib
import sys

V3 = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V3.parent / "tools"))
import envcapture  # noqa: E402

envcapture.ROOT = V3
envcapture.CONDA_ENVS = V3 / ".venv"
envcapture.PROJECT_ENVS = ["census-tf", "census-torch/Scripts"]

if __name__ == "__main__":
    envcapture.main()
