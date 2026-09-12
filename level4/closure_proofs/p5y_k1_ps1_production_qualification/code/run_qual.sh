#!/bin/sh
# Phase 4: wait for the optimised benchmark to finish, then run the real-cost qualification on 16 workers pinned to
# the 16 PHYSICAL cores (logical cpus 0-15; SMT siblings 16-31 unused), then aggregate/T4/T5 every cell.
O=/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_ps1_production_qualification/evidence/qual
while ! grep -q OPT_BENCH_DONE /home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_ps1_production_qualification/evidence/bench_opt/series.log 2>/dev/null; do sleep 20; done
PY=/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python
PP=/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_ps1_production_qualification/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_partition_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_curvature_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_t345_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_t2_closure_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_bint_p1_bound_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_endpoint_strip_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_t2_per_patch_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_executor_t1_successor/code
E="env -i HOME=/home/ubuntu PATH=/usr/bin:/bin LANG=C.UTF-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PP"
GROUPS="0,1,2,3;148,149,150,151;360,361,362,363;368"; CELLS=0,1,2,3,148,149,150,151,360,361,362,363,368
mkdir -p $O/chunks; split -n l/16 -d -a 2 /home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_t345_successor/config/live_patches.txt $O/chunks/p_
date -u +%s > $O/start_epoch
k=0; for f in $O/chunks/p_*; do taskset -c $k $E $PY /home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_ps1_production_qualification/code/qual_producer.py "$GROUPS" $f $O/chunks > $O/chunks/log_$k.txt 2>&1 & k=$((k+1)); done; wait
date -u +%s > $O/end_epoch
for s in $(echo $CELLS | tr ',' ' '); do $E $PY /home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_partition_successor/code/run_stages.py $s "$O/chunks/rec_s${s}_*.jsonl" $O/stages >> $O/stages.log 2>&1; done
echo QUAL_DONE >> $O/stages.log
