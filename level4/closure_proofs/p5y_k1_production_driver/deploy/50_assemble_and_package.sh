#!/usr/bin/env bash
# Phases D/E/F on the collected shard records, then package the artifacts.
set -euo pipefail
: "${WORKDIR:=$HOME/rebaseguard}"
: "${RUN_ID:?set RUN_ID}"
cd "$WORKDIR"
RUN=level4/closure_proofs/p5y_k1_production_driver/runs/$RUN_ID
./level4/.venv/bin/python level4/closure_proofs/p5y_k1_production_driver/k1prod/driver.py \
  --run-dir "$RUN" --shard 0 --shards 1 --phases DEF | tee "$RUN/assembly.json"
tar -czf "$RUN.tar.gz" -C "$(dirname "$RUN")" "$(basename "$RUN")"
sha256sum "$RUN.tar.gz"
