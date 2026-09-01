#!/usr/bin/env bash
# Full P8 replay.  Total wall time is dominated by E1 (the Gamma matrix).
# Run from the repository root.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
P8="$ROOT/level4/closure_proofs/p8_model_class_robustness"
PY="$ROOT/level4/.venv/bin/python"
JOBS="${P8_JOBS:-4}"
cd "$P8"

run_parallel() {   # run_parallel <script> <extra args...> -- <cell specs>
  local script="$1"; shift
  local extra=(); while [ "$1" != "--" ]; do extra+=("$1"); shift; done; shift
  local n=0
  for spec in "$@"; do
    "$PY" "experiments/$script" "${spec%%:*}" "${spec##*:}" "${extra[@]}" \
      > "logs/$(basename "$script" .py)_${spec/:/_}.log" 2>&1 &
    n=$((n+1)); [ $((n % JOBS)) -eq 0 ] && wait
  done
  wait
}

mkdir -p logs results
CELLS_CUSUM="cusum:gaussian cusum:t10 cusum:t5 cusum:t3 cusum:contam0.05 cusum:contam0.1"
CELLS_SR="sr:gaussian sr:t10 sr:t5 sr:t3 sr:contam0.05 sr:contam0.1"

echo "== step 0: family regularity (G1d, G1e) =="
"$PY" experiments/run_regularity.py

echo "== step 1: SR calibration (G2) =="
"$PY" experiments/run_sr_calibration.py

echo "== step 2: E1 Gamma matrix =="
run_parallel run_gamma_matrix.py --tag E1 --batch0 0 -- $CELLS_CUSUM $CELLS_SR
"$PY" experiments/aggregate_gamma.py E1

echo "== step 2b: cross-priority consistency =="
"$PY" experiments/run_cross_priority.py
"$PY" experiments/evaluate_posthoc_H2.py

echo "== step 3: E5 independent seed family =="
run_parallel run_gamma_matrix.py --tag E5 --batch0 100 -- $CELLS_CUSUM $CELLS_SR
"$PY" experiments/aggregate_gamma.py E5

echo "== step 4: E3 chain ladder =="
run_parallel run_chain_ladder.py --tag E3 -- $CELLS_CUSUM $CELLS_SR

echo "== step 5: E4 drift =="
run_parallel run_drift.py --tag E4 -- $CELLS_CUSUM $CELLS_SR

echo "== step 6: E6 P4 replication diagnostic =="
for fam in gaussian t10 t5 t3 contam0.05 contam0.1; do "$PY" experiments/run_p4_replication.py "$fam"; done
"$PY" experiments/run_p4_replication.py --merge

echo "== step 7: tests and gates =="
"$PY" -m pytest tests -q
"$PY" experiments/derive_closure.py
"$PY" experiments/make_result_tables.py
"$PY" experiments/make_provenance.py
