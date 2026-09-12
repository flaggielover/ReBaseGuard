#!/bin/sh
# Optimised-core benchmarks: (1) concurrency W = 1,8,16,24,32 identical workloads (SMT pricing);
# (2) batch-size series b1..b16, each size in its own process, all concurrently (<= 5 processes on 16 cores).
PY=/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python
PP=/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_ps1_production_qualification/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_partition_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_curvature_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_t345_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_t2_closure_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_bint_p1_bound_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_endpoint_strip_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_t2_per_patch_successor/code:/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_sr_o9_executor_t1_successor/code
E="env -i HOME=/home/ubuntu PATH=/usr/bin:/bin LANG=C.UTF-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PP"
O=/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_ps1_production_qualification/evidence/bench_opt
for Wk in 1 8 16 24 32; do
  mkdir -p $O/conc_W$Wk; s=$(date +%s.%N)
  k=0; while [ $k -lt $Wk ]; do $E $PY /home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_ps1_production_qualification/code/bench_opt.py 150 "51,63;38,26;0,0" $O/conc_W$Wk/w$k.json > /dev/null 2>&1 & k=$((k+1)); done; wait
  echo "W=$Wk wall=$(echo "$(date +%s.%N) - $s" | bc)" >> $O/conc.log
done
for spec in "b1:360" "b2:360,150" "b4:360,150,10,368" "b8:360,150,10,368,60,210,300,361" "b16:360,150,10,368,60,210,300,361,0,40,100,180,240,275,330,363"; do
  name=${spec%%:*}; cells=${spec#*:}
  $E $PY /home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_ps1_production_qualification/code/bench_opt.py "$cells" "51,63;18,62;38,26;8,36;0,0;0,0" $O/series_$name.json >> $O/series.log 2>&1 &
done; wait
echo OPT_BENCH_DONE >> $O/series.log
