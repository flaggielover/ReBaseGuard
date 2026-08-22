# Progress capsules

## PROGRESS CAPSULE — #1

| Field | Value |
|---|---|
| Step | 1 / 7 |
| Gate | pre-data audit complete |
| Previous theorem reproduced? | YES |
| New protocol frozen? | NO |
| Replication | NOT STARTED |
| Decomposition | NOT STARTED |
| Lean | NOT STARTED |
| Axiom audit | NOT STARTED |
| Tests | prior 46/46; authoritative 695/695 |
| Historical artifacts modified? | NO |
| Blockers | none |
| Remaining | freeze and hash Track 1A protocol before generating data |

## PROGRESS CAPSULE — #2

| Field | Value |
|---|---|
| Step | 2 / 7 |
| Gate | protocol frozen before confirmatory data |
| Previous theorem reproduced? | YES |
| New protocol frozen? | YES — `76a5d40b4165758afb72a12dd93f302dd03cbf7db78184ef248156962cc9a79f` |
| Replication | NOT STARTED |
| Decomposition | NOT STARTED |
| Lean | NOT STARTED |
| Axiom audit | NOT STARTED |
| Tests | protocol hash and seed-family prechecks pass |
| Historical artifacts modified? | NO |
| Blockers | none |
| Remaining | commit protocol checkpoint, then implement and run confirmatory replication |

## PROGRESS CAPSULE — #3

| Field | Value |
|---|---|
| Step | 3 / 7 |
| Gate | independent Stage-A / Stage-D distinction |
| Previous theorem reproduced? | YES |
| New protocol frozen? | YES |
| Replication | PASS — preselected `m=20,50` effects positive in both replications and pooled 95% CIs |
| Decomposition | evaluation complete; one pooled cell failed |
| Lean | NOT STARTED |
| Axiom audit | NOT STARTED |
| Tests | simulation smoke controls passed |
| Historical artifacts modified? | NO |
| Blockers | independent decomposition pooled bound at `m=20` |
| Remaining | preserve results and diagnose decomposition gate |

## PROGRESS CAPSULE — #4

| Field | Value |
|---|---|
| Step | 4 / 7 |
| Gate | independent decomposition correspondence |
| Previous theorem reproduced? | YES |
| New protocol frozen? | YES |
| Replication | distinction PASS |
| Decomposition | FAIL — `m=20`: discrepancy `0.02955`, SE `0.00944`, abs z `3.130` > 3 |
| Lean | STOPPED BEFORE START |
| Axiom audit | NOT STARTED |
| Tests | pathwise identity and correction-sign checks pass |
| Historical artifacts modified? | NO |
| Blockers | frozen decomposition criterion failed |
| Remaining | document failure; do not add paths, tune rule, or begin Lean |

## PROGRESS CAPSULE — #5

| Field | Value |
|---|---|
| Step | 5 / 7 |
| Gate | Lean authorization after numerical gate |
| Previous theorem reproduced? | YES |
| New protocol frozen? | YES |
| Replication | distinction PASS |
| Decomposition | FAIL |
| Lean | NOT STARTED — mandatory stop rule |
| Axiom audit | NOT RUN; no Track 1A axiom introduced |
| Tests | pending final package verification |
| Historical artifacts modified? | NO |
| Blockers | numerical stop gate prevents Lean phase |
| Remaining | finalize failure-first package and run non-scientific verification |

## PROGRESS CAPSULE — #6

| Field | Value |
|---|---|
| Step | 6 / 7 |
| Gate | final verification |
| Previous theorem reproduced? | YES |
| New protocol frozen? | YES |
| Replication | distinction PASS |
| Decomposition | FAIL |
| Lean | NOT STARTED — mandatory stop |
| Axiom audit | NOT RUN; no new axiom |
| Tests | Track 1A 32/32; prior track 46/46; authoritative 695/695; combined 773 |
| Historical artifacts modified? | NO |
| Blockers | frozen decomposition failure remains dispositive |
| Remaining | issue exact Track 1A verdict and scoped requirement status |

## PROGRESS CAPSULE — #7

| Field | Value |
|---|---|
| Step | 7 / 7 |
| Gate | final decision |
| Previous theorem reproduced? | YES |
| New protocol frozen? | YES |
| Replication | Stage-A / Stage-D distinction PASS |
| Decomposition | independent criterion FAIL at pooled `m=20`; pathwise identity PASS |
| Lean | NOT STARTED |
| Axiom audit | NOT RUN; no Track 1A Lean axiom exists |
| Tests | ALL GREEN — 773 combined |
| Historical artifacts modified? | NO |
| Blockers | `m=20` independent decomposition `3.130 > 3` SE; Lean unopened |
| Remaining | none within Track 1A; verdict `MGT1-TRACK1A-FAILED` |
