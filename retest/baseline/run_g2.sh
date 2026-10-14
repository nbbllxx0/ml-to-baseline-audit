#!/bin/bash
# Provisional G2 benchmark (plan/BASELINE_PREREG.md §2-5): P1, P2 x n in {64, 256} x 3 solvers, 150 its, 3 repeats.
cd "$(dirname "$0")/../.."
T5090=/c/Users/<user>/anaconda3/envs/torch5090/python.exe
PYT=/c/Users/<user>/anaconda3/envs/Pytorch/python.exe
for n in 64 256; do
  for p in P1 P2; do
    "$T5090" -m retest.baseline.bench --solver gpu     --problem $p --n $n
    "$PYT"   -m retest.baseline.bench --solver pardiso --problem $p --n $n
    "$T5090" -m retest.baseline.bench --solver superlu --problem $p --n $n
  done
done
echo "G2 BENCHMARK DONE"
