#!/bin/sh
# Phase 8/9 certified driver for the successor children of ONE frozen parent (all 3,994 live patches, midpoint only).
#   run_region.sh launch   PARENT [WORKERS]   -> per-patch midpoint certification, WORKERS detached processes
#   run_region.sh finalize PARENT             -> T3 aggregation (mid + mean-value cell mode), T4, T5 per child
set -eu
N=$(cd "$(dirname "$0")/.." && pwd); CP=$(dirname "$N"); W=$(cd "$CP/../.." && pwd)
MODE=$1; PARENT=$2; WORKERS=${3:-30}
PY=/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python
PP=$N/code:$CP/p5y_k1_sr_o9_curvature_successor/code:$CP/p5y_k1_sr_o9_t345_successor/code:$CP/p5y_k1_sr_o9_t2_closure_successor/code:$CP/p5y_k1_sr_o9_bint_p1_bound_successor/code:$CP/p5y_k1_sr_o9_endpoint_strip_successor/code:$CP/p5y_k1_sr_o9_t2_per_patch_successor/code:$CP/p5y_k1_sr_o9_executor_t1_successor/code
ENV="env -i HOME=/home/ubuntu PATH=/usr/bin:/bin LANG=C.UTF-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PP"
OUT=$N/evidence/certified/parent_$PARENT
CELLS=$($ENV $PY -c "import succ_cells as SC; print(','.join(str(c['index']) for c in SC.cells_of_parent($PARENT)))")
if [ "$MODE" = launch ]; then
  mkdir -p $OUT/chunks
  HEAD=$(git -C $W rev-parse HEAD); DIRTY=$(git -C $W status --porcelain -- level4/closure_proofs | wc -l)
  printf '{"parent":%s,"successor_cells":"%s","git_commit":"%s","dirty_paths":%s,"workers":%s,"launched_utc":"%s","table_sha256":"%s"}\n' \
    "$PARENT" "$CELLS" "$HEAD" "$DIRTY" "$WORKERS" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(sha256sum < $N/config/successor_cells.json | cut -c1-64)" > $OUT/RUN_MANIFEST.json
  split -n l/$WORKERS -d -a 2 $CP/p5y_k1_sr_o9_t345_successor/config/live_patches.txt $OUT/chunks/patches_
  for f in $OUT/chunks/patches_*; do
    k=${f##*_}
    ( setsid $ENV timeout 36000 $PY $N/code/succ_t3.py --cells $CELLS --patches $f --out $OUT/chunks/rec_$k.jsonl > $OUT/chunks/log_$k.txt 2>&1 < /dev/null & )
  done
  echo "launched parent $PARENT cells $CELLS workers $WORKERS"
elif [ "$MODE" = finalize ]; then
  for s in $(echo $CELLS | tr ',' ' '); do
    $ENV $PY $N/code/run_stages.py $s "$OUT/chunks/rec_*.jsonl" $OUT
  done
fi
