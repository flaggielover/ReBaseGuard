#!/bin/sh
for e in 3 1 1/2 1/4 0; do for N in 10 20 40; do for k in whole taboo; do
  t=$(echo $e|tr / _); [ -f "results/point_${t}_N${N}_${k}_P1.json" ] || ./run_capped.sh 1200 "logs/p_${t}_${N}_${k}.txt" point $e $N $k P1
done; done; done
