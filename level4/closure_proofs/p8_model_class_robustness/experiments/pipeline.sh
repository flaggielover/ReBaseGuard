#!/usr/bin/env bash
# Sequential P8 production pipeline with bounded parallelism (bash 3.2 safe).
set -u
P8="$(cd "$(dirname "$0")/.." && pwd)"
PY=/Users/suzhe/ReBaseGuard/level4/.venv/bin/python
JOBS=${P8_JOBS:-4}
cd "$P8"; mkdir -p logs

par() {  # par <logprefix> <script> <extra...> :: <specs...>
  local pref="$1"; shift
  local script="$1"; shift
  local extra=()
  while [ "$1" != "::" ]; do extra+=("$1"); shift; done; shift
  local pids=() n=0
  for spec in "$@"; do
    "$PY" "experiments/$script" "${spec%%:*}" "${spec##*:}" "${extra[@]}" \
      > "logs/${pref}_${spec%%:*}_${spec##*:}.log" 2>&1 &
    pids+=($!); n=$((n+1))
    if [ ${#pids[@]} -ge "$JOBS" ]; then wait "${pids[0]}"; pids=("${pids[@]:1}"); fi
  done
  wait
}

CU="cusum:gaussian cusum:t10 cusum:t5 cusum:t3 cusum:contam0.05 cusum:contam0.1"
SR="sr:gaussian sr:t10 sr:t5 sr:t3 sr:contam0.05 sr:contam0.1"
SRNG="sr:t10 sr:t5 sr:t3 sr:contam0.05 sr:contam0.1"

echo "STAGE wait-for-wave1-and-calibration"
while [ ! -f results/sr_calibration.json ] || \
      [ "$(ls results/gamma/E1_cusum_*.json 2>/dev/null | wc -l | tr -d ' ')" -lt 6 ] || \
      [ ! -f results/gamma/E1_sr_gaussian.json ]; do sleep 20; done
echo "STAGE wave1 complete"

echo "STAGE E1-sr-nongaussian"
par gamma_E1 run_gamma_matrix.py --tag E1 --batch0 0 :: $SRNG
"$PY" experiments/aggregate_gamma.py E1 > logs/aggregate_E1.log 2>&1
echo "STAGE E1 aggregated"

echo "STAGE E3-chain"
par chain_E3 run_chain_ladder.py --tag E3 :: $CU $SR
echo "STAGE E3 complete"

echo "STAGE E4-drift"
par drift_E4 run_drift.py --tag E4 :: $CU $SR
echo "STAGE E4 complete"

echo "STAGE E6-p4-replication"
"$PY" experiments/run_p4_replication.py > logs/p4_replication.log 2>&1
echo "STAGE E6 complete"

echo "STAGE E5-seed-family"
par gamma_E5 run_gamma_matrix.py --tag E5 --batch0 100 :: $CU $SR
"$PY" experiments/aggregate_gamma.py E5 > logs/aggregate_E5.log 2>&1
echo "STAGE E5 complete"

echo "STAGE derive-closure"
"$PY" experiments/derive_closure.py > logs/derive_closure.log 2>&1
echo "PIPELINE COMPLETE"
