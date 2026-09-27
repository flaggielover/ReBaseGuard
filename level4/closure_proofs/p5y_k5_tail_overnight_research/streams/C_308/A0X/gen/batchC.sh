#!/bin/sh
# waits for batch B (pointwise) to finish, then runs blocks + F0 comparator
while pgrep -f batchB.sh > /dev/null; do sleep 20; done
for e0 in 1/2 1 3; do t=$(echo $e0|tr / _)
  for w in 1/40 1/20 1/10; do ./run_capped.sh 1200 "logs/b_${t}_$(echo $w|tr / _)_40.txt" block $e0 $(python3 -c "from fractions import Fraction as F;print(F('$e0')+F('$w'))") 40 whole; done
  for w in 1/20 1/10; do ./run_capped.sh 1200 "logs/b_${t}_$(echo $w|tr / _)_20.txt" block $e0 $(python3 -c "from fractions import Fraction as F;print(F('$e0')+F('$w'))") 20 whole; done
  ./run_capped.sh 1200 "logs/bt_${t}_1_20_40.txt" block $e0 $(python3 -c "from fractions import Fraction as F;print(F('$e0')+F(1,20))") 40 taboo
done
for e in 3 1 1/2 1/4 0; do t=$(echo $e|tr / _); for k in whole taboo; do ./run_capped.sh 1200 "logs/f0_${t}_${k}.txt" point $e 20 $k F0_affine_m; done; done
