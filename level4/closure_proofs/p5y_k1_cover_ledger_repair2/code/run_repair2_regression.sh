#!/bin/bash
# Repair2 regression runner. NOT production; the minimum representative set
# needed to prove the provenance wiring end-to-end.
#
# One FLINT/BLAS thread per worker, per the frozen no-oversubscription policy.
#
#   usage: run_repair2_regression.sh <outdir>
set -u
ROOT=/home/ubuntu/work/ReBaseGuard
OUT=${1:?output directory required}
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PY=$ROOT/level4/.venv/bin/python
Q=$ROOT/level4/closure_proofs/p5y_k1_cover_ledger_repair2/code/repair2_qualify.py
mkdir -p "$OUT"
cd "$ROOT" || exit 1

# Representative cell 221, all four m: leaves, a non-leaf chain, an m=1
# assembly and m>1 assemblies, all with a full frozen dependency graph.
"$PY" "$Q" --cell 221 --bits 256 --scope full \
  --out "$OUT/repair2_221_256_full.json" > "$OUT/c221_full.log" 2>&1 &

# The m=1 SCOPED diagnostic, which must issue NO certificate.
"$PY" "$Q" --cell 221 --bits 256 --scope m1 \
  --out "$OUT/repair2_221_256_m1.json" > "$OUT/c221_m1.log" 2>&1 &

wait
echo DONE > "$OUT/regression.done"
