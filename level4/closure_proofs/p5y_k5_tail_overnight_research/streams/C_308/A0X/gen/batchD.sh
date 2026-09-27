#!/bin/sh
# waits for batch A (truth), then truth grids, robust ARL, controls
while pgrep -f batchA.sh > /dev/null; do sleep 20; done
for e0 in 1/2 1 3; do ./run_capped.sh 1200 "logs/tg_$(echo $e0|tr / _).txt" truthgrid $e0 1/10 4; done
for e0 in 3 1 1/2; do t=$(echo $e0|tr / _)
  for w in 1/20 1/10; do ./run_capped.sh 1200 "logs/r_${t}_$(echo $w|tr / _)_20.txt" robust $e0 $w 20; done
done
for e0 in 3 1; do t=$(echo $e0|tr / _)
  for w in 1/40 1/20 1/10; do ./run_capped.sh 1200 "logs/r_${t}_$(echo $w|tr / _)_40.txt" robust $e0 $w 40; done
done
./run_capped.sh 1200 logs/r_1_2_1_40_40.txt robust 1/2 1/40 40
nice perl -e 'alarm shift; exec @ARGV' 1200 python3 c2b_controls.py 1 20 > logs/controls_1.txt 2>&1
nice perl -e 'alarm shift; exec @ARGV' 1200 python3 c2b_controls.py 1/2 20 > logs/controls_1_2.txt 2>&1
