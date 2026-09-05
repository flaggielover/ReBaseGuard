#!/bin/bash
# Repair1 regression runner. NOT production; a fixed, small re-certification set.
# One FLINT/BLAS thread per worker, per the frozen no-oversubscription policy.
#
#   usage: run_repair_regression.sh <outdir>
set -u
ROOT=/home/ubuntu/work/ReBaseGuard
OUT=${1:?output directory required}
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PY=$ROOT/level4/.venv/bin/python
Q=$ROOT/level4/closure_proofs/p5y_k1_cover_ledger_repair1/code/repair_qualify.py
mkdir -p "$OUT"
cd "$ROOT" || exit 1

# m=1 representative (cell 221) at the frozen precision plus the 384/512 diagnostic
for b in 256 384 512; do
  "$PY" "$Q" --cell 221 --bits "$b" --scope m1 \
    --out "$OUT/repaired_221_${b}_m1.json" > "$OUT/c221_${b}_m1.log" 2>&1 &
done
# one m>1 representative: the full four-m obligation set on cell 221
"$PY" "$Q" --cell 221 --bits 256 --scope full \
  --out "$OUT/repaired_221_256_full.json" > "$OUT/c221_256_full.log" 2>&1 &
# a second full cell for cross-check (interior, m>1)
"$PY" "$Q" --cell 293 --bits 256 --scope full \
  --out "$OUT/repaired_293_256_full.json" > "$OUT/c293_256_full.log" 2>&1 &
wait
echo DONE > "$OUT/regression.done"
