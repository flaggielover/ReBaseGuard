# Adversarial audit

The first run is preserved at **19/22 FAIL**.
A19 was an over-broad checker match; A21 and A22 correctly preceded their final
records. The final run is **22/22 PASS**.

| ID | Check | First | Final | Final evidence |
|---|---|---|---|---|
| A1 | Stage E historical decision unchanged | PASS | PASS | historical Stage E remains PARTIAL with 0/3 H-E5 |
| A2 | no old Stage-E data pooled | PASS | PASS | V2 primaries are independent of historical Stage-E tasks |
| A3 | dataset selection preceded confirmatory policy outcomes | PASS | PASS | protocol c80d5d47 precedes outcomes ['00ee0f3a'] |
| A4 | no task replacement after unfavorable outcome | PASS | PASS | all three frozen primaries retained; backup inactive |
| A5 | power floor frozen | PASS | PASS | 20-block floor is inside frozen protocol bundle |
| A6 | calibration frozen before evaluation outcomes | PASS | PASS | gate 671eef94 precedes outcome checkpoint; thresholds identical |
| A7 | no future leakage | PASS | PASS | train/calibration/evaluation and source guards all pass |
| A8 | matched streams | PASS | PASS | each task has one residual hash, threshold, and 120-point grid shared by policies |
| A9 | rho outcome-blind | PASS | PASS | rho fixed at execution checkpoint ade95663 |
| A10 | drift conditions outcome-blind | PASS | PASS | five conditions match frozen protocol exactly |
| A11 | matched-wait denominator | PASS | PASS | E1 arrays contain only event delay and matched in-control wait |
| A12 | dependence-aware inference | PASS | PASS | two-week natural and six-event moving blocks used |
| A13 | effective block floor enforced | PASS | PASS | every closure endpoint/task meets floor 20 |
| A14 | unreliable endpoints excluded | PASS | PASS | no unreliable endpoint enters H2-4 |
| A15 | P3 exploratory only | PASS | PASS | P3 is absent from the confirmatory policy set |
| A16 | no sample-efficiency claim unless consumption differs | PASS | PASS | current result reports contain no sample-efficiency claim |
| A17 | alert burden not called false-alarm rate | PASS | PASS | current result reports use alert burden only |
| A18 | no production-validation wording | PASS | PASS | forbidden phrases appear only inside an explicit does-not-support boundary |
| A19 | figures from final JSON only | FAIL | PASS | four figures read only results/summary.json |
| A20 | historical hashes unchanged | PASS | PASS | all protected tracked roots match |
| A21 | full verifier green | FAIL | PASS | recorded status=PASS checks=1028 |
| A22 | reproducer byte-stable | FAIL | PASS | recorded status=PASS byte_stable=True |

No scientific threshold, hypothesis, result, or closure rule was weakened
between runs.
