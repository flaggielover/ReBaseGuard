#!/bin/bash
# usage: cell.sh KIND CELL CORE RUNROOT RUNID
KIND=$1; CELL=$2; CORE=$3; R=$4; RUN=$5
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
PY=/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python
CP=/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs
L=$R/logs/${KIND}_${CELL}
if [ "$KIND" = SR ]; then
  EV=$R/evidence/sr_$CELL; TID=K1R4-SR-$CELL-$RUN
  cd $CP/p5y_k1r4_bridge_successor/driver
  taskset -c $CORE $PY -c "import sys,json; sys.path.insert(0,'.'); import k1r4_bridge_worker as W; r=W.run_cell($CELL,'$EV','$TID'); print(json.dumps(r,sort_keys=True,default=str))" > $L.out 2> $L.err &
else
  EV=$R/evidence/cusum_$CELL; TID=K1R5-CUSUM-$CELL-$RUN
  cd $CP/p5y_k1r5_cusum_entry
  taskset -c $CORE $PY driver/k1r5_cusum_entry.py --cell $CELL --evidence-dir $EV --task-id $TID > $L.out 2> $L.err &
fi
P=$!
printf '{"kind":"%s","cell":%s,"core":%s,"pid":%s,"start_utc":"%s","evidence_dir":"%s","task_id":"%s"}\n' $KIND $CELL $CORE $P "$(date -u +%Y-%m-%dT%H:%M:%SZ)" $EV $TID > $L.launch.json
wait $P; RC=$?
printf '{"pid":%s,"rc":%s,"end_utc":"%s"}\n' $P $RC "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > $L.exit.json
