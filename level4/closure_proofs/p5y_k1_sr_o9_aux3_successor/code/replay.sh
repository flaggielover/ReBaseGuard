#!/bin/sh
# Determinism replay: rerun every diagnostic in a clean env (in dependency order) and compare evidence JSON bytes.
set -u
N=$(cd "$(dirname "$0")/.." && pwd); CP=$(dirname "$N")
PY=/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python
PP=$N/code:$CP/p5y_k1_sr_o9_curvature_successor/code:$CP/p5y_k1_sr_o9_t345_successor/code:$CP/p5y_k1_sr_o9_t2_closure_successor/code:$CP/p5y_k1_sr_o9_bint_p1_bound_successor/code:$CP/p5y_k1_sr_o9_endpoint_strip_successor/code:$CP/p5y_k1_sr_o9_t2_per_patch_successor/code:$CP/p5y_k1_sr_o9_executor_t1_successor/code
R=$N/evidence/replay; mkdir -p $R
FILES="phase1_doctrine.json phase2_equations.json phase34_oracle_c313.json phase34_tower_ext_c313.json phase34_consistent_c313.json phase34_consistent_v2_c313.json"
for f in $FILES; do cp $N/evidence/$f $R/$f.orig; done
cd $N/code
for s in phase1_doctrine.py phase2_equations.py aux3_oracle.py aux3_tower_ext.py aux3_consistent.py aux3_consistent_v2.py; do
  env -i HOME=/home/ubuntu PATH=/usr/bin:/bin LANG=C.UTF-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=$PP $PY $s > $R/$s.log 2>&1
done
out=$R/determinism.txt; : > $out
for f in $FILES; do
  a=$(sha256sum < $R/$f.orig | cut -c1-64); b=$(sha256sum < $N/evidence/$f | cut -c1-64)
  if [ "$a" = "$b" ]; then echo "$f IDENTICAL $a" >> $out; else echo "$f DIFFERENT $a $b" >> $out; fi
  rm -v -- $R/$f.orig
done
echo DONE >> $out
