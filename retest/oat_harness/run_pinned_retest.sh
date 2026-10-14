#!/bin/bash
# Pinned re-timing (plan/BASELINE_PREREG.md §9, CPU placement row): every timed process on the performance cores at
# high priority (tools/pin.py). Sequential; nothing else on the GPU. Stage names match run_final_retest.sh and
# run_post_retest.sh, so analysis.oat_retest_summary and analysis.energy parse this log with --log.
#   bash retest/oat_harness/run_pinned_retest.sh > retest/logs/oat_pinned_retest_2026-09-24.log 2>&1
cd "$(dirname "$0")/../.."
source retest/oat_harness/env.sh
export PIN_PCORES=1
T5090=/c/Users/YSL0/anaconda3/envs/torch5090/python.exe
PYT=/c/Users/YSL0/anaconda3/envs/Pytorch/python.exe
K=5
for n in 64 256; do
  for p in P1 P2; do
    echo "=== G2 gpu $p $n ===";     "$T5090" -m retest.baseline.bench --solver gpu     --problem $p --n $n --tag _pinned
    echo "=== G2 pardiso $p $n ==="; "$PYT"   -m retest.baseline.bench --solver pardiso --problem $p --n $n --tag _pinned
  done
done
echo "=== OAT SIMP 256 CG+OC ===";      OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_oat_simp --size 256 --k $K --solvers CG --optimizers OC
echo "=== OAT SIMP 64 CG+OC ===";       OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_oat_simp --size 64 --k $K --solvers CG --optimizers OC
echo "=== OAT SIMP 64 SPSOLVE+OC ===";  OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_oat_simp --size 64 --k $K --solvers SPSOLVE --optimizers OC
echo "=== ours GPU 256 ===";     "$T5090" -m retest.oat_harness.run_ours_on_nito --solver gpu --size 256 --k $K
echo "=== ours GPU 64 ===";      "$T5090" -m retest.oat_harness.run_ours_on_nito --solver gpu --size 64 --k $K
echo "=== ours PARDISO 64 ===";  "$PYT"   -m retest.oat_harness.run_ours_on_nito --solver pardiso --size 64 --k $K
echo "=== ours PARDISO 256 ==="; "$PYT"   -m retest.oat_harness.run_ours_on_nito --solver pardiso --size 256 --k $K
echo "=== OAT inference 256 ==="; "$OAT_PY" -m retest.oat_harness.run_oat_inference --size 256 --k $K
echo "=== OAT inference 64 ===";  "$OAT_PY" -m retest.oat_harness.run_oat_inference --size 64 --k $K
echo "=== ttq run 256 ==="; "$T5090" -m retest.oat_harness.time_to_quality run --size 256 --k $K
echo "=== ttq run 64 ===";  "$T5090" -m retest.oat_harness.time_to_quality run --size 64 --k $K
echo "=== energy ours GPU 256 ==="; "$T5090" -m retest.oat_harness.run_ours_on_nito --solver gpu --size 256 --k $K --power
echo "=== energy ours GPU 64 ===";  "$T5090" -m retest.oat_harness.run_ours_on_nito --solver gpu --size 64 --k $K --power
echo "=== energy OAT inference 256 ==="; "$OAT_PY" -m retest.oat_harness.run_oat_inference --size 256 --k $K --power
echo "=== energy OAT inference 64 ===";  "$OAT_PY" -m retest.oat_harness.run_oat_inference --size 64 --k $K --power
echo "PINNED RETEST DONE"
