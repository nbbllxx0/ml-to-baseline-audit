#!/bin/bash
# Final same-machine OAT re-test (plan/BASELINE_PREREG.md §7, §9). Sequential; nothing else on the GPU meanwhile.
cd "$(dirname "$0")/../.."
source retest/oat_harness/env.sh
T5090=/c/Users/YSL0/anaconda3/envs/torch5090/python.exe
PYT=/c/Users/YSL0/anaconda3/envs/Pytorch/python.exe
K=5
echo "=== OAT SIMP 256 MultiGrid(5)+OC ==="; OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_oat_simp --size 256 --k $K --solvers MultiGrid --optimizers OC --mg-levels 5
echo "=== OAT SIMP 256 CG+OC ===";           OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_oat_simp --size 256 --k $K --solvers CG --optimizers OC
echo "=== OAT SIMP 64 MultiGrid(3)+OC ===";   OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_oat_simp --size 64 --k $K --solvers MultiGrid --optimizers OC --mg-levels 3
echo "=== OAT SIMP 64 CG+OC ===";             OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_oat_simp --size 64 --k $K --solvers CG --optimizers OC
echo "=== OAT SIMP 64 SPSOLVE+OC ===";        OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_oat_simp --size 64 --k $K --solvers SPSOLVE --optimizers OC
echo "=== ours GPU 256 ===";     "$T5090" -m retest.oat_harness.run_ours_on_nito --solver gpu --size 256 --k $K
echo "=== ours GPU 64 ===";      "$T5090" -m retest.oat_harness.run_ours_on_nito --solver gpu --size 64 --k $K
echo "=== ours PARDISO 64 ===";  "$PYT"   -m retest.oat_harness.run_ours_on_nito --solver pardiso --size 64 --k $K
echo "=== ours PARDISO 256 ==="; "$PYT"   -m retest.oat_harness.run_ours_on_nito --solver pardiso --size 256 --k $K
echo "=== OAT inference 256 ==="; "$OAT_PY" -m retest.oat_harness.run_oat_inference --size 256 --k $K
echo "=== OAT inference 64 ===";  "$OAT_PY" -m retest.oat_harness.run_oat_inference --size 64 --k $K
echo "FINAL RETEST DONE"
