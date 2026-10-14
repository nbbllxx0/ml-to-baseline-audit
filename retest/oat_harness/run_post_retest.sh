#!/bin/bash
# Steps after the final same-machine OAT re-test (plan/BASELINE_PREREG.md §5, §7, §9). Sequential; nothing else on the GPU.
# Order: timed work first (time-to-quality, then power-sampled energy runs), then untimed scoring and diagnostics.
# Invoke with its log, which the script reads back for run folders:
#   bash retest/oat_harness/run_post_retest.sh > retest/logs/oat_post_retest_2026-09-24.log 2>&1
cd "$(dirname "$0")/../.."
POSTLOG=retest/logs/oat_post_retest_2026-09-24.log
source retest/oat_harness/env.sh
T5090=/c/Users/YSL0/anaconda3/envs/torch5090/python.exe
FINAL=retest/logs/oat_final_retest_2026-09-24.log
# Last "run dir:" printed under a "=== <stage> ===" header of a driver log.
stagedir() { awk -v s="=== $2 ===" '$0==s{f=1;next} /^=== /{f=0} f && /^run dir:/{print $3}' "$1" | tail -1 | tr -d '\r'; }
K=5
echo "=== ttq run 256 ==="; "$T5090" -m retest.oat_harness.time_to_quality run --size 256 --k $K
echo "=== ttq run 64 ===";  "$T5090" -m retest.oat_harness.time_to_quality run --size 64 --k $K
echo "=== energy ours GPU 256 ==="; "$T5090" -m retest.oat_harness.run_ours_on_nito --solver gpu --size 256 --k $K --power
echo "=== energy ours GPU 64 ===";  "$T5090" -m retest.oat_harness.run_ours_on_nito --solver gpu --size 64 --k $K --power
echo "=== energy OAT inference 256 ==="; "$OAT_PY" -m retest.oat_harness.run_oat_inference --size 256 --k $K --power
echo "=== energy OAT inference 64 ===";  "$OAT_PY" -m retest.oat_harness.run_oat_inference --size 64 --k $K --power
TTQ256=$(stagedir "$POSTLOG" "ttq run 256")
TTQ64=$(stagedir "$POSTLOG" "ttq run 64")
echo "=== eval 256 ==="
OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.eval_designs --size 256 --ids 1015,1676,1839,1935,1961 \
  --oat-infer "$(stagedir "$FINAL" 'OAT inference 256')" --oat-simp "$(stagedir "$FINAL" 'OAT SIMP 256 CG+OC')" \
  --ours "$(stagedir "$FINAL" 'ours GPU 256')" --ours "$(stagedir "$FINAL" 'ours PARDISO 256')"
echo "=== eval 64 ==="
OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.eval_designs --size 64 --ids 15,676,839,935,961 \
  --oat-infer "$(stagedir "$FINAL" 'OAT inference 64')" --oat-simp "$(stagedir "$FINAL" 'OAT SIMP 64 CG+OC')" \
  --oat-simp "$(stagedir "$FINAL" 'OAT SIMP 64 SPSOLVE+OC')" \
  --ours "$(stagedir "$FINAL" 'ours GPU 64')" --ours "$(stagedir "$FINAL" 'ours PARDISO 64')"
echo "=== ttq score 256 ==="; OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_to_quality score --run "$TTQ256"
echo "=== ttq score 64 ===";  OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.time_to_quality score --run "$TTQ64"
echo "=== debug MultiGrid 256 L5 ==="; CUDA_LAUNCH_BLOCKING=1 OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.debug_mg --pid 1015 --levels 5 --iters 150
echo "=== debug MultiGrid 64 L3 ===";  CUDA_LAUNCH_BLOCKING=1 OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.debug_mg --pid 15 --levels 3 --iters 150
echo "POST RETEST DONE"
