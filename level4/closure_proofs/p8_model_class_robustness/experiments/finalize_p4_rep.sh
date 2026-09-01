#!/usr/bin/env bash
set -u
P8="$(cd "$(dirname "$0")/.." && pwd)"; cd "$P8"
PY=/Users/suzhe/ReBaseGuard/level4/.venv/bin/python
REMAIN="t10 t5 contam0.05"
for fam in $REMAIN; do
  while [ "$(pgrep -cf 'run_p4_replication.py [a-z]')" -ge 3 ]; do sleep 30; done
  nohup "$PY" experiments/run_p4_replication.py "$fam" > "logs/p4rep_$fam.log" 2>&1 &
  sleep 5
done
while pgrep -f "run_p4_replication.py [a-z]" > /dev/null; do sleep 30; done
"$PY" experiments/run_p4_replication.py --merge
