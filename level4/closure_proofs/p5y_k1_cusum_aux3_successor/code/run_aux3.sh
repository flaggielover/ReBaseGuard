#!/bin/bash
# aux3 successor certification runner. NOT production.
set -u
ROOT=/home/ubuntu/work/ReBaseGuard
OUT=${1:?output directory required}; shift
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export K1_THREADS_PINNED=1
PY=$ROOT/level4/.venv/bin/python
Q=$ROOT/level4/closure_proofs/p5y_k1_cusum_aux3_successor/code/aux_qualify.py
mkdir -p "$OUT"; cd "$ROOT" || exit 1
for c in "$@"; do
  "$PY" "$Q" --cell "$c" --bits 256 --out "$OUT/aux3_CUSUM_${c}_256.json" \
      > "$OUT/c${c}.log" 2>&1 &
done
wait
echo DONE > "$OUT/run.done"
