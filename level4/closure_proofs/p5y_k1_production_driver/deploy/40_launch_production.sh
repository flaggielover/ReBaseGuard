#!/usr/bin/env bash
# Launch sharded production. Requires qualification to have PASSED.
# The frozen worker ceiling is 64; this script refuses to exceed it.
set -euo pipefail
: "${WORKDIR:=$HOME/rebaseguard}"
: "${SHARDS:=64}"
: "${RUN_ID:?set RUN_ID}"
cd "$WORKDIR"
Q=level4/closure_proofs/p5y_k1_production_driver/runs/qualification.json
test -f "$Q" || { echo "run 30_qualify.sh first"; exit 1; }
test "$(jq -r '.ENVIRONMENT_QUALIFICATION' "$Q")" = PASS || { echo "qualification FAILED"; exit 1; }
test "$SHARDS" -le 64 || { echo "SHARDS exceeds the frozen ceiling of 64"; exit 1; }
RUN=level4/closure_proofs/p5y_k1_production_driver/runs/$RUN_ID
mkdir -p "$RUN"
for k in $(seq 0 $((SHARDS-1))); do
  ./level4/.venv/bin/python level4/closure_proofs/p5y_k1_production_driver/k1prod/driver.py \
    --run-dir "$RUN" --shard "$k" --shards "$SHARDS" --phases ABC --execute \
    > "$RUN/shard$k.log" 2>&1 &
done
wait
echo "shards complete; run 50_assemble.sh"
