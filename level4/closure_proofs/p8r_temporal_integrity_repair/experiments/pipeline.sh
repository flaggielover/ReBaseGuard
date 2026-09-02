#!/usr/bin/env bash
# The frozen P8R production pipeline, in the order PRODUCTION_PLAN.md declares.
#
# Every command here also appears verbatim in COMMAND_MANIFEST.json, which is
# committed at the temporal anchor.  Nothing in this script chooses a budget,
# a threshold or a cell: all of those live in src/rebaseguard_p8r/config.py.
#
# Usage:  P8R_JOBS=3 experiments/pipeline.sh
set -u
P8R="$(cd "$(dirname "$0")/.." && pwd)"
PY="${P8R_PYTHON:-/Users/suzhe/ReBaseGuard/level4/.venv/bin/python}"
JOBS="${P8R_JOBS:-3}"
cd "$P8R"
mkdir -p logs

CELLS="cusum:gaussian cusum:t10 cusum:t5 cusum:t3 cusum:contam0.05 cusum:contam0.1 \
sr:gaussian sr:t10 sr:t5 sr:t3 sr:contam0.05 sr:contam0.1"
FAMILIES="gaussian t10 t5 t3 contam0.05 contam0.1"

# run "$script" "$det" "$fam" [extra...] over CELLS, at most JOBS at a time
par_cells() {
  local pref="$1" script="$2"; shift 2
  local pids=()
  local spec det fam
  for spec in $CELLS; do
    det="${spec%%:*}"; fam="${spec##*:}"
    "$PY" "experiments/$script" "$det" "$fam" "$@" \
      > "logs/${pref}_${det}_${fam}.log" 2>&1 &
    pids+=($!)
    if [ "${#pids[@]}" -ge "$JOBS" ]; then wait "${pids[0]}"; pids=("${pids[@]:1}"); fi
  done
  wait
}

echo "== 1 regularity"
"$PY" experiments/run_regularity.py > logs/regularity.log 2>&1

echo "== 2 calibration (CAL_SEARCH / CAL_VERIFY_1 / CAL_VERIFY_2)"
pids=()
for f in $FAMILIES; do
  "$PY" experiments/run_calibration.py "$f" > "logs/cal_${f}.log" 2>&1 &
  pids+=($!)
  if [ "${#pids[@]}" -ge "$JOBS" ]; then wait "${pids[0]}"; pids=("${pids[@]:1}"); fi
done
wait

echo "== 3 calibration merge (freezes the accepted thresholds)"
"$PY" experiments/run_calibration.py --merge > logs/cal_merge.log 2>&1

echo "== 4 E1 gamma matrix"
par_cells gamma_E1 run_gamma_matrix.py --tag E1
echo "== 5 aggregate E1"
"$PY" experiments/aggregate_gamma.py E1 > logs/aggregate_E1.log 2>&1

echo "== 6 E5 gamma matrix (independent seed family)"
par_cells gamma_E5 run_gamma_matrix.py --tag E5
echo "== 7 aggregate E5"
"$PY" experiments/aggregate_gamma.py E5 > logs/aggregate_E5.log 2>&1

echo "== 8 in-control ARL re-measurement"
"$PY" experiments/run_arl0_check.py > logs/arl0_check.log 2>&1

echo "== 9 independent reimplementation"
"$PY" experiments/run_independent_repro.py > logs/independent_repro.log 2>&1

echo "== 10 E3 chain ladder"
par_cells chain_E3 run_chain_ladder.py
echo "== 11 E4 drift"
par_cells drift_E4 run_drift.py

echo "== 12 scientific resolution"
"$PY" experiments/derive_resolution.py > logs/derive_resolution.log 2>&1
echo "PIPELINE COMPLETE"
