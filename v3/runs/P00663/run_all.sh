#!/usr/bin/env bash
# P00663 run sequence (CENSUS_PREREG §9, P00663 row): one warm-up per algorithm, then 3 timed runs alternating
# classic / cnn. One container per run; the repository is mounted read-only; the FEniCS JIT cache persists in cache/.
set -u
HERE="E:/AI/ml-to-baseline-audit/v3/runs/P00663"
REPO="E:/AI/ml-to-baseline-audit/v3/third_party/DeepNNforTopoOptisation"
LOG="E:/AI/ml-to-baseline-audit/v3/runs/P00647/CONCURRENT.log"
mkdir -p "$HERE/cache" "$HERE/results"
run() {
  echo "$(date +%T) P00663 $2 start" >> "$LOG"
  MSYS_NO_PATHCONV=1 docker run --rm -v "$REPO:/repo:ro" -v "$HERE:/out" -v "$HERE/cache:/root/.cache" -w /repo \
    census-p00663:3 python /out/run663.py "$1" "$2" > "$HERE/results/$2.log" 2>&1
  echo "$(date +%T) P00663 $2 end (exit $?)" >> "$LOG"
  grep RESULT "$HERE/results/$2.log" || tail -5 "$HERE/results/$2.log"
}
run classic warmup_classic
run cnn warmup_cnn
for i in 1 2 3; do
  run classic "classic_$i"
  run cnn "cnn_$i"
done
