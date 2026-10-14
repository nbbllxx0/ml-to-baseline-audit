#!/bin/bash
# Untimed scoring of the pinned re-timing designs with OAT's evaluator, then the CuPy-only crash repro.
#   bash retest/oat_harness/run_pinned_scoring.sh > retest/logs/oat_pinned_scoring_2026-09-24.log 2>&1
cd "$(dirname "$0")/../.."
source retest/oat_harness/env.sh
P=retest/logs/oat_pinned_retest_2026-09-24.log
POST=retest/logs/oat_post_retest_2026-09-24.log
stagedir() { awk -v s="=== $2 ===" '$0==s{f=1;next} /^=== /{f=0} f && /^run dir:/{print $3}' "$1" | tail -1 | tr -d '\r'; }
echo "=== eval 256 ==="
OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.eval_designs --size 256 --ids 1015,1676,1839,1935,1961 \
  --oat-infer "$(stagedir $P 'OAT inference 256')" --oat-simp "$(stagedir $P 'OAT SIMP 256 CG+OC')" \
  --ours "$(stagedir $P 'ours GPU 256')" --ours "$(stagedir $P 'ours PARDISO 256')"
echo "=== eval 64 ==="
OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.eval_designs --size 64 --ids 15,676,839,935,961 \
  --oat-infer "$(stagedir $P 'OAT inference 64')" --oat-simp "$(stagedir $P 'OAT SIMP 64 CG+OC')" \
  --oat-simp "$(stagedir $P 'OAT SIMP 64 SPSOLVE+OC')" \
  --ours "$(stagedir $P 'ours GPU 64')" --ours "$(stagedir $P 'ours PARDISO 64')"
echo "=== ttq rescore 256 ==="; OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.ttq_rescore --run "$(stagedir $P 'ttq run 256')" --ref "$(stagedir $POST 'ttq run 256')"
echo "=== ttq rescore 64 ===";  OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.ttq_rescore --run "$(stagedir $P 'ttq run 64')" --ref "$(stagedir $POST 'ttq run 64')"
echo "=== repro spSM ===";      OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.repro_spsm
echo "PINNED SCORING DONE"
