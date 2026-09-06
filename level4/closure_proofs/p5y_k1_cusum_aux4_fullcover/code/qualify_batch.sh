#!/bin/bash
# Aux4 batch launcher. NOT production.
#   qualify_batch.sh OUTDIR WORKERS CELL [CELL...]
# Resumable: a cell already certified under the current producer identity is
# skipped. Records are written atomically by the runner itself.
set -u
ROOT=/home/ubuntu/work/ReBaseGuard
OUT=$1; shift
WORKERS=$1; shift
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export K1_THREADS_PINNED=1
PY=$ROOT/level4/.venv/bin/python
Q=$ROOT/level4/closure_proofs/p5y_k1_cusum_aux4_fullcover/code/qualify4.py
mkdir -p "$OUT/logs"
cd "$ROOT" || exit 1
rm -f "$OUT/run.done"
run_one() {
  c=$1
  "$PY" "$Q" --cell "$c" --bits 256 --skip-if-current \
      --out "$OUT/aux4_CUSUM_${c}_256.json" > "$OUT/logs/c${c}.log" 2>&1
  if [ $? -ne 0 ]; then
    echo "FAILED cell $c" >> "$OUT/failures.txt"
  fi
}
export -f run_one 2>/dev/null || true
i=0
for c in "$@"; do
  run_one "$c" &
  i=$((i + 1))
  if [ "$i" -ge "$WORKERS" ]; then
    wait -n 2>/dev/null || wait
    i=$((i - 1))
  fi
done
wait
date -u +%FT%TZ > "$OUT/run.done"
