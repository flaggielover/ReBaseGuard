#!/usr/bin/env bash
# NON-RESULT-BEARING environment qualification. Produces no K1 evidence.
set -euo pipefail
: "${WORKDIR:=$HOME/rebaseguard}"
: "${WORKERS:=64}"
cd "$WORKDIR"
OUT=level4/closure_proofs/p5y_k1_production_driver/runs/qualification.json
./level4/.venv/bin/python level4/closure_proofs/p5y_k1_production_driver/k1prod/qualify.py "$WORKERS" | tee "$OUT"
jq -r '.ENVIRONMENT_QUALIFICATION' "$OUT"
./level4/.venv/bin/python level4/closure_proofs/p5y_k1_production_driver/k1prod/smoke.py \
  | tee level4/closure_proofs/p5y_k1_production_driver/runs/scaling_smoke.json | jq -r '.flags'
