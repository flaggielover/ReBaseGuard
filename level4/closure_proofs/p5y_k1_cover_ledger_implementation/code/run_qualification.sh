#!/bin/bash
# Representative qualification and precision diagnostic runner.
#
# NOT production. It runs a fixed, small representative set only. One FLINT and
# one BLAS thread per worker, per the frozen no-oversubscription policy and so
# that process_time() CPU accounting is not inflated by thread spinning.
#
#   usage: run_qualification.sh <outdir> <full|precision>
set -u
ROOT=/home/ubuntu/work/ReBaseGuard
OUT=${1:?output directory required}
MODE=${2:-full}
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PY=$ROOT/level4/.venv/bin/python
QUALIFY=$ROOT/level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/qualify.py
mkdir -p "$OUT"
cd "$ROOT" || exit 1

if [ "$MODE" = "precision" ]; then
  # Phase 7: m=1 obligation at the frozen 256 bits plus 384 and 512 diagnostics.
  for c in 0 221; do
    for b in 256 384 512; do
      "$PY" "$QUALIFY" --detector CUSUM --cell "$c" --bits "$b" --scope m1 \
        --out "$OUT/CUSUM_${c}_${b}_m1.json" > "$OUT/c${c}_${b}_m1.log" 2>&1 &
    done
  done
else
  # Phase 6: the six frozen representative anchors (27/5 and 11/2 share cell 325).
  for c in 0 136 221 293 325; do
    "$PY" "$QUALIFY" --detector CUSUM --cell "$c" --bits 256 \
      --out "$OUT/CUSUM_${c}_256.json" > "$OUT/c${c}_256.log" 2>&1 &
  done
fi
wait
echo DONE > "$OUT/$MODE.done"
