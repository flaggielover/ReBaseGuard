#!/bin/sh
# Determinism replay: rerun both diagnostics in a clean env and compare evidence JSON bytes.
set -u
N=$(cd "$(dirname "$0")/.." && pwd); CP=$(dirname "$N")
PY=/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python
PP=$N/code:$CP/p5y_k1_sr_o9_curvature_successor/code:$CP/p5y_k1_sr_o9_t345_successor/code:$CP/p5y_k1_sr_o9_t2_closure_successor/code:$CP/p5y_k1_sr_o9_bint_p1_bound_successor/code:$CP/p5y_k1_sr_o9_endpoint_strip_successor/code:$CP/p5y_k1_sr_o9_t2_per_patch_successor/code:$CP/p5y_k1_sr_o9_executor_t1_successor/code
R=$N/evidence/replay; mkdir -p $R
for f in phase23_oracle_c313.json phase3_next_blocker_c313.json; do cp $N/evidence/$f $R/$f.orig; done
cd $N/code
for s in oracle_norms.py next_blocker.py; do
  env -i HOME=/home/ubuntu PATH=/usr/bin:/bin LANG=C.UTF-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=$PP $PY $s 313 > $R/$s.log 2>&1
done
out=$R/determinism.txt; : > $out
for f in phase23_oracle_c313.json phase3_next_blocker_c313.json; do
  a=$(sha256sum < $R/$f.orig | cut -c1-64); b=$(sha256sum < $N/evidence/$f | cut -c1-64)
  if [ "$a" = "$b" ]; then echo "$f IDENTICAL $a" >> $out; else echo "$f DIFFERENT $a $b" >> $out; fi
  rm -v -- $R/$f.orig
done
echo DONE >> $out
