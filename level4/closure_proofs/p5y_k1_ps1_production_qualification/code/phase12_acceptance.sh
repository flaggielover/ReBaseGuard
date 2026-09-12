#!/bin/sh
# Phase 12 clean-checkout acceptance. Usage: phase12_acceptance.sh OPS_CLONE PROD_CLONE OUTDIR
# Runs every focused suite from CLEAN clones (no working-tree state of the development worktree is used), records
# each suite's exit status and output. Result-free: creates no genuine production cell; starts nothing.
set -u
OPS=$1; PROD=$2; OUT=$3; mkdir -p $OUT
PY=/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python
CPo=$OPS/level4/closure_proofs; CPp=$PROD/level4/closure_proofs
pp() { R=$1; echo "$R/level4/closure_proofs/p5y_k1_ps1_production_qualification/code:$R/level4/closure_proofs/p5y_k1_sr_o9_partition_successor/code:$R/level4/closure_proofs/p5y_k1_sr_o9_curvature_successor/code:$R/level4/closure_proofs/p5y_k1_sr_o9_t345_successor/code:$R/level4/closure_proofs/p5y_k1_sr_o9_t2_closure_successor/code:$R/level4/closure_proofs/p5y_k1_sr_o9_bint_p1_bound_successor/code:$R/level4/closure_proofs/p5y_k1_sr_o9_endpoint_strip_successor/code:$R/level4/closure_proofs/p5y_k1_sr_o9_t2_per_patch_successor/code:$R/level4/closure_proofs/p5y_k1_sr_o9_executor_t1_successor/code"; }
ENV="env -i HOME=/home/ubuntu PATH=/usr/bin:/bin LANG=C.UTF-8 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1"
run() { name=$1; shift; echo "== $name" >> $OUT/summary.txt; ( "$@" ) > $OUT/$name.log 2>&1; rc=$?; echo "$name rc=$rc" >> $OUT/summary.txt; }
: > $OUT/summary.txt
echo "ops_clone_head $(git -C $OPS rev-parse HEAD)" >> $OUT/summary.txt
echo "prod_clone_head $(git -C $PROD rev-parse HEAD)" >> $OUT/summary.txt
echo "ops_clone_dirty $(git -C $OPS status --porcelain | wc -l) prod_clone_dirty $(git -C $PROD status --porcelain | wc -l)" >> $OUT/summary.txt
# 1 PS1 partition generator + historical regression (cell 150 T4/T5) + stage generation
run partition_and_historical_regression $ENV PYTHONPATH=$(pp $OPS) $PY $CPo/p5y_k1_sr_o9_partition_successor/tests/test_successor.py
# 2 PS1 production namespace (identity, shards, precision, pool/serialization, accounting, sealing gate, controls, firewall, handoff)
run ps1_production $ENV PYTHONPATH=$(pp $PROD) $PY $CPp/p5y_k1_ps1_production/tests/test_ps1_production.py
# 3 PS1 lifecycle adapter: byte identity, contract, render, release sites, synthetic supervised campaigns
run ps1_lifecycle_adapter $ENV $PY -m pytest -q $CPo/p5y_k1_ps1_lifecycle_adapter/tests/test_adapter.py
# 4 the ORIGINAL audited lifecycle suite, unchanged
run original_lifecycle_suite $ENV $PY -m pytest -q -k "not live" $CPo/p5y_k1_sr_production_lifecycle_successor/tests
# 5 deterministic fresh-process replay of Phase-4 production-path records
run deterministic_replay $ENV PYTHONPATH=$(pp $OPS) $PY $CPo/p5y_k1_ps1_production_qualification/code/replay_qual.py $OUT/replay
# 6 lifecycle readiness against the REAL PS1 contract (no start): install policy, render, status, verify.
# install-runtime-policy writes ONLY the governed block into $PROD/.git/info/exclude (git metadata; idempotent;
# not a start and not a production mutation), so the acceptance is self-contained from fresh clones.
run install_runtime_policy $ENV $PY $CPo/p5y_k1_ps1_lifecycle_adapter/ops/prodctl.py install-runtime-policy --role AWS
run prodctl_render $ENV $PY -c "import sys; sys.path.insert(0,'$CPo/p5y_k1_ps1_lifecycle_adapter/ops'); import opscommon as OC, prodctl as PC; c=OC.load_contract(); print(' '.join(PC.render_start(c,'AWS','20260101T000000Z-00000000')))"
run prodctl_status $ENV $PY $CPo/p5y_k1_ps1_lifecycle_adapter/ops/prodctl.py status --role AWS
run prodctl_verify $ENV $PY $CPo/p5y_k1_ps1_lifecycle_adapter/ops/prodctl.py verify --role AWS
echo DONE >> $OUT/summary.txt
