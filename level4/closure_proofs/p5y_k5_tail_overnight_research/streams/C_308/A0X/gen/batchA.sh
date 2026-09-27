#!/bin/sh
for e in 3 1 1/2 1/4 0; do ./run_capped.sh 1200 "logs/truth_$(echo $e|tr / _).txt" truth $e 10,20,40; done
./run_capped.sh 1200 logs/truth80_3.txt truth 3 80
./run_capped.sh 1200 logs/truth80_1.txt truth 1 80
