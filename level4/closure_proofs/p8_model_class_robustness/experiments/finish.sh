#!/usr/bin/env bash
# Finish the remaining P8 production work, then derive every gate.
set -u
P8="$(cd "$(dirname "$0")/.." && pwd)"; cd "$P8"
PY=/Users/suzhe/ReBaseGuard/level4/.venv/bin/python
mkdir -p logs

echo "STAGE wait-for-current-workers"
while pgrep -f "run_gamma_matrix.py" > /dev/null; do sleep 30; done
echo "STAGE E5-remaining-sr-cells"
pids=()
for fam in t3 contam0.05 contam0.1; do
  "$PY" experiments/run_gamma_matrix.py sr "$fam" --tag E5 --batch0 100 \
    > "logs/gamma_E5_sr_${fam}.log" 2>&1 &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done
echo "STAGE E5 cells complete"
"$PY" experiments/aggregate_gamma.py E5 > logs/aggregate_E5.log 2>&1
echo "STAGE E5 aggregated"

echo "STAGE wait-for-E6"
while pgrep -f "run_p4_replication.py [a-z]" > /dev/null; do sleep 30; done
if [ ! -f results/p4_replication_diagnostic.json ]; then
  "$PY" experiments/run_p4_replication.py --merge > logs/p4rep_merge.log 2>&1
fi
echo "STAGE E6 complete"

echo "STAGE derive"
"$PY" experiments/run_cross_priority.py   > logs/cross_priority.log 2>&1
"$PY" experiments/evaluate_posthoc_H2.py  > logs/posthoc_H2.log 2>&1
"$PY" -m pytest tests -q                  > logs/pytest.log 2>&1
"$PY" experiments/derive_closure.py       > logs/derive_closure.log 2>&1
"$PY" experiments/make_result_tables.py   > logs/result_tables.log 2>&1
"$PY" experiments/make_provenance.py      > logs/provenance.log 2>&1
echo "P8 FINISH COMPLETE"
cat logs/derive_closure.log
