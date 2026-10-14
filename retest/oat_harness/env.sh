# Source before running OAT code:  source retest/oat_harness/env.sh
export CUDA_PATH="C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0"
export PYTHONPATH="$(cygpath -w "$(pwd)/retest/oat_harness/shims");$(cygpath -w "$(pwd)/retest/targets/OptimizeAnyTopology")"
export OAT_PY=/c/Users/<user>/anaconda3/envs/oat/python.exe
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
