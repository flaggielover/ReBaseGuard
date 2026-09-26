#!/bin/bash
# usage: cell_k1r6.sh CELL CORE RUNROOT RUNID
CELL=$1; CORE=$2; R=$3; RUN=$4
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
PY=/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python
NS=/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1r6_cusum_bridge_repair
L=$R/logs/CUSUM_$CELL; EV=$R/evidence/cusum_$CELL; TID=K1R6-CUSUM-$CELL-$RUN
cd $NS
taskset -c $CORE $PY driver/k1r6_cusum_entry.py --cell $CELL --evidence-dir $EV --task-id $TID > $L.out 2> $L.err &
P=$!
printf '{"kind":"CUSUM","producer":"K1R6","cell":%s,"core":%s,"pid":%s,"start_utc":"%s","evidence_dir":"%s","task_id":"%s"}\n' $CELL $CORE $P "$(date -u +%Y-%m-%dT%H:%M:%SZ)" $EV $TID > $L.launch.json
wait $P; RC=$?
printf '{"pid":%s,"rc":%s,"end_utc":"%s"}\n' $P $RC "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > $L.exit.json
