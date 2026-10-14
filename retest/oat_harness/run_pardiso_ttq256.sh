#!/bin/bash
# PARDISO time-to-quality at 256² (pinned), for setup-inclusive per-design times (BASELINE_PREREG §9, setup row).
#   bash retest/oat_harness/run_pardiso_ttq256.sh > retest/logs/pardiso_ttq256_2026-09-24.log 2>&1
cd "$(dirname "$0")/../.."
source retest/oat_harness/env.sh
export PIN_PCORES=1
PYT=/c/Users/YSL0/anaconda3/envs/Pytorch/python.exe
P=retest/logs/oat_pinned_retest_2026-09-24.log
stagedir() { awk -v s="=== $2 ===" '$0==s{f=1;next} /^=== /{f=0} f && /^run dir:/{print $3}' "$1" | tail -1 | tr -d '\r'; }
echo "=== ttq run 256 pardiso ==="; "$PYT" -m retest.oat_harness.time_to_quality run --size 256 --k 5 --solver pardiso
TTQP=$(stagedir retest/logs/pardiso_ttq256_2026-09-24.log "ttq run 256 pardiso")
echo "=== ttq rescore 256 pardiso ==="; OAT_CUPY=1 "$OAT_PY" -m retest.oat_harness.ttq_rescore --run "$TTQP" --ref "$(stagedir $P 'ttq run 256')"
echo "PARDISO TTQ256 DONE"
