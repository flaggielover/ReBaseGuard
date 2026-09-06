#!/bin/bash
# CUSUM completion successor certification runner. NOT production.
# The qualifier re-execs itself with a pinned single-thread contract, so the
# certified content is deterministic regardless of how it is invoked.
#
#   usage: run_successor.sh <outdir> <cell> [<cell> ...]
set -u
ROOT=/home/ubuntu/work/ReBaseGuard
OUT=${1:?output directory required}; shift
export PYTHONDONTWRITEBYTECODE=1
PY=$ROOT/level4/.venv/bin/python
Q=$ROOT/level4/closure_proofs/p5y_k1_cusum_completion_successor/code/successor_qualify.py
mkdir -p "$OUT"
cd "$ROOT" || exit 1
for c in "$@"; do
  "$PY" "$Q" --cell "$c" --bits 256 \
    --out "$OUT/succ_CUSUM_${c}_256.json" > "$OUT/c${c}.log" 2>&1 &
done
wait
echo DONE > "$OUT/run.done"
