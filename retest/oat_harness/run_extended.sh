#!/bin/bash
# Post hoc OAT extension (retest/oat_harness/extended.py): 5 primary + 20 new problems per size, 5 OAT seeds each.
# Every timed process pinned to the performance cores at high priority, as run_pinned_retest.sh. Sequential.
#   bash retest/oat_harness/run_extended.sh > retest/logs/oat_extended_2026-09-25.log 2>&1
cd "$(dirname "$0")/../.."
source retest/oat_harness/env.sh
export PIN_PCORES=1
T5090=/c/Users/YSL0/anaconda3/envs/torch5090/python.exe
set -e
for n in 64 256; do
  echo "=== ids $n ==="
  RUN=$("$OAT_PY" -m retest.oat_harness.extended ids --size $n | tail -1)
  echo "run dir: $RUN"
  echo "=== OAT inference $n ===";  "$OAT_PY" -m retest.oat_harness.extended infer --run "$RUN"
  echo "=== ours GPU ttq $n ===";   "$T5090" -m retest.oat_harness.extended ttq --run "$RUN"
  echo "=== score $n ===";          OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.extended score --run "$RUN"
done
echo "EXTENDED DONE"
