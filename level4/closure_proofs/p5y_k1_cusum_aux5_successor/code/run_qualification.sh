#!/bin/bash
# Aux5 qualification launcher. NON-PRODUCTION. Frozen protocol: config/QUALIFICATION_PROTOCOL.json
#   run_qualification.sh ROOT OUTDIR
# Cells 318 and 323, two repeats each, four fresh env -i interpreters run concurrently on distinct physical
# cores (logical 0,2,4,6). No resume: every run recomputes from scratch.
set -u
ROOT=$1
OUT=$2
PY=/root/work/rbg-cusum-aux5-venv/bin/python
Q=$ROOT/level4/closure_proofs/p5y_k1_cusum_aux5_successor/code/qualify5.py
mkdir -p "$OUT"
cd "$ROOT" || exit 1
date -u +%FT%TZ > "$OUT/run.started"
for spec in 318:A:0 318:B:2 323:A:4 323:B:6; do
  IFS=: read -r cell rep core <<< "$spec"
  d="$OUT/c${cell}_${rep}"
  mkdir -p "$d"
  (
    env -i PATH=/usr/bin:/bin HOME=/root LANG=C.UTF-8 \
      OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
      K1_THREADS_PINNED=1 PYTHONDONTWRITEBYTECODE=1 \
      taskset -c "$core" "$PY" "$Q" --cell "$cell" --bits 256 --out "$d/aux5_CUSUM_${cell}_256.json" \
      > "$d/run.log" 2>&1
    echo $? > "$d/rc"
  ) &
done
wait
date -u +%FT%TZ > "$OUT/run.done"
