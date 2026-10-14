#!/bin/bash
# Extra pinned runs (plan/BASELINE_PREREG.md §9 CPU placement row): ED3 GPU scaling of the strong baseline
# (P1, P2 at 128², 512², 1024²; 64² and 256² exist from the pinned re-timing) and CPU PARDISO time-to-quality at 64²,
# where PARDISO is the faster baseline. PARDISO is not run above 256²: the pre-registered filter radius scales with
# n (1.5 n/64), and the CPU filter matrix at 1024² would hold about 1.7e9 nonzeros.
#   bash retest/oat_harness/run_extra_runs.sh > retest/logs/extra_runs_2026-09-24.log 2>&1
cd "$(dirname "$0")/../.."
source retest/oat_harness/env.sh
export PIN_PCORES=1
T5090=/c/Users/YSL0/anaconda3/envs/torch5090/python.exe
PYT=/c/Users/YSL0/anaconda3/envs/Pytorch/python.exe
P=retest/logs/oat_pinned_retest_2026-09-24.log
stagedir() { awk -v s="=== $2 ===" '$0==s{f=1;next} /^=== /{f=0} f && /^run dir:/{print $3}' "$1" | tail -1 | tr -d '\r'; }
for n in 128 512 1024; do
  for p in P1 P2; do
    echo "=== ED3 gpu $p $n ==="; "$T5090" -m retest.baseline.bench --solver gpu --problem $p --n $n --tag _pinned
  done
done
echo "=== ttq run 64 pardiso ==="; "$PYT" -m retest.oat_harness.time_to_quality run --size 64 --k 5 --solver pardiso
TTQP=$(stagedir retest/logs/extra_runs_2026-09-24.log "ttq run 64 pardiso")
echo "=== ttq rescore 64 pardiso ==="; OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.ttq_rescore --run "$TTQP" --ref "$(stagedir $P 'ttq run 64')"
echo "EXTRA RUNS DONE"
