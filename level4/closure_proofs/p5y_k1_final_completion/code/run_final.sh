#!/bin/bash
# Final-completion re-certification runner. NOT production.
# One FLINT/BLAS thread per worker, per the frozen no-oversubscription policy.
#   usage: run_final.sh <outdir> <cell> [<cell> ...]
set -u
ROOT=/home/ubuntu/work/ReBaseGuard
OUT=${1:?output directory required}; shift
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PY=$ROOT/level4/.venv/bin/python
Q=$ROOT/level4/closure_proofs/p5y_k1_final_completion/code/final_qualify.py
mkdir -p "$OUT"
cd "$ROOT" || exit 1
for c in "$@"; do
  "$PY" "$Q" --cell "$c" --bits 256 \
    --out "$OUT/sharp_CUSUM_${c}_256.json" > "$OUT/c${c}.log" 2>&1 &
done
wait
echo DONE > "$OUT/final.done"
