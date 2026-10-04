#!/usr/bin/env bash
# Targeted QC11 / QC-D5 rehearsals in the scratch replica iso_r1 (sequential: the frozen tests share hard-coded
# scratch directories).  Each run needs a clean replica: the replica ledger lines a run appends are saved as a diff
# next to the run, then the replica ledger is restored.  Detached by the caller (setsid nohup): no tool time limit.
set -u
SP=/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad
ISO=$SP/iso_r1
NS=/home/user/ReBaseGuard/level4/closure_proofs/p5y_k5_cell309_q11_recovery
LEDGER=level4/closure_proofs/p5y_k5_cell309_p309_r1/ledger
RUN() {  # name gates harness [harness-file]
  local name=$1 gates=$2 harness=$3 hf=${4:-}
  echo "=== $name start $(date -u +%FT%TZ)"
  if [ -n "$hf" ]; then
    python3 $NS/code/p309_rehearsal.py --iso $ISO --out $SP/runs/$name --gates $gates --harness $harness --harness-file $hf
  else
    python3 $NS/code/p309_rehearsal.py --iso $ISO --out $SP/runs/$name --gates $gates --harness $harness
  fi
  echo "=== $name end rc=$? $(date -u +%FT%TZ)"
  git -C $ISO diff -- $LEDGER > $SP/runs/$name.replica_ledger.diff
  git -C $ISO checkout -q -- $LEDGER
}
# the interrupted Run A's replica ledger lines are kept before the first restore
git -C $ISO diff -- $LEDGER > $SP/runs/A_frozen_QC11_QCD5.replica_ledger.diff
git -C $ISO checkout -q -- $LEDGER
RUN A2_frozen_QC11_QCD5 QC11,QC_D5 frozen
RUN A3_repaired_QC11_QCD5 QC11,QC_D5 repaired
for m in M1_BASE_HEAD M2_BASE_HEAD_NO_POST M3_DETAIL_SWAP M4_MANIFEST_FROM_TREE; do
  RUN MUT_$m QC11 mutant $NS/repair/mutants/$m.py.txt
done
echo "=== ALL DONE $(date -u +%FT%TZ)"
