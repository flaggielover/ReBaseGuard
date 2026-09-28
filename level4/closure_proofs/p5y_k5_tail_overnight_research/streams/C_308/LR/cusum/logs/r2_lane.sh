#!/bin/bash
# R2 regeneration lane runner (D16): each job capped at 1200 s (perl alarm), sequential within a lane.
cd /Users/suzhe/ReBaseGuard-k5ov/level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/LR/cusum
lane=$1; shift
while [ $# -gt 0 ]; do
  name=$1; shift; cmd=$1; shift
  start=$(date +%s)
  perl -e 'alarm shift; exec @ARGV' 1200 nice python3 -u -B $cmd > logs/r2_$name.log 2>&1
  rc=$?
  echo "$lane $name rc=$rc secs=$(( $(date +%s) - start )) $(date +%H:%M:%S)" >> logs/r2_queue.status
done
echo "$lane DONE $(date +%H:%M:%S)" >> logs/r2_queue.status
