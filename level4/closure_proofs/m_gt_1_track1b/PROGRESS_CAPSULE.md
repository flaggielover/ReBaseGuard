# Progress capsules

## PROGRESS CAPSULE — #1

| Field | Value |
|---|---|
| Step | 1 / 8 |
| Gate | Track 1A covariance and dependency audit |
| Protocol frozen? | NO |
| Historical Track 1A preserved? | YES |
| Covariance audit | complete — compared routes independent; relevant covariance zero |
| Paired replication | NOT STARTED |
| Independent replication | NOT STARTED |
| m=1 control | historical control reproduced |
| Lean | NOT STARTED |
| Axiom audit | NOT STARTED |
| Tests | Track 1 46/46; Track 1A 32/32 |
| Historical artifacts modified? | NO |
| Blockers | none |
| Remaining | freeze correlation-aware Track 1B protocol before data |

## PROGRESS CAPSULE — #2

| Field | Value |
|---|---|
| Step | 2 / 8 |
| Gate | pre-data protocol freeze |
| Protocol frozen? | YES — `c4eca15f8e72059a8d7cb3f0a5dc8fe7922183b90594b4a9574ded4e94c775c6` |
| Historical Track 1A preserved? | YES |
| Covariance audit | complete |
| Paired replication | NOT STARTED |
| Independent replication | NOT STARTED |
| m=1 control | NOT STARTED for Track 1B |
| Lean | NOT STARTED |
| Axiom audit | NOT STARTED |
| Tests | protocol hash, scope, and fresh-seed prechecks pass |
| Historical artifacts modified? | NO |
| Blockers | none |
| Remaining | commit/push protocol; then implement frozen routes |

## PROGRESS CAPSULE — #3

| Field | Value |
|---|---|
| Step | 3 / 8 |
| Gate | covariance diagnosis |
| Protocol frozen? | YES |
| Historical Track 1A preserved? | YES — `3.130 > 3` remains failed |
| Covariance audit | CLOSED — old routes independent; old quadrature SE valid; paired covariance positive/maximal |
| Paired replication | implementation ready; outcomes not yet evaluated at this capsule |
| Independent replication | implementation ready |
| m=1 control | structural tests pass |
| Lean | NOT STARTED |
| Axiom audit | NOT STARTED |
| Tests | 17/17 pre-outcome tests |
| Historical artifacts modified? | NO |
| Blockers | none |
| Remaining | execute frozen 64-batch routes |

## PROGRESS CAPSULE — #4

| Field | Value |
|---|---|
| Step | 4 / 8 |
| Gate | confirmatory replication complete |
| Protocol frozen? | YES |
| Historical Track 1A preserved? | YES |
| Covariance audit | complete |
| Paired replication | PASS — path error `8.53e-14`; batch error `5.33e-15` |
| Independent replication | PASS — Hotelling p `0.0430`; max relative discrepancy `0.638%` |
| m=1 control | PASS |
| Lean | NOT STARTED pending explicit gate declaration |
| Axiom audit | NOT STARTED |
| Tests | result tests pending |
| Historical artifacts modified? | NO |
| Blockers | none |
| Remaining | freeze numerical decision and authorize Lean |

## PROGRESS CAPSULE — #5

| Field | Value |
|---|---|
| Step | 5 / 8 |
| Gate | `NUMERICAL GATE CLOSED — LEAN AUTHORIZED` |
| Protocol frozen? | YES |
| Historical Track 1A preserved? | YES |
| Covariance audit | complete |
| Paired replication | PASS |
| Independent replication | PASS |
| m=1 control | PASS |
| Lean | AUTHORIZED, not yet started |
| Axiom audit | NOT STARTED |
| Tests | pre-outcome 17/17; confirmatory result checks pending |
| Historical artifacts modified? | NO |
| Blockers | none |
| Remaining | commit green numerical checkpoint; formalize Lean spine |

## PROGRESS CAPSULE — #6

| Field | Value |
|---|---|
| Step | 6 / 8 |
| Gate | Lean stable-spine compilation and analytic-assumption audit |
| Protocol frozen? | YES |
| Historical Track 1A preserved? | YES |
| Covariance audit | complete |
| Paired replication | PASS |
| Independent replication | PASS |
| m=1 control | PASS |
| Lean | PASS — stable spine compiles |
| Axiom audit | PASS — `propext`, `Classical.choice`, `Quot.sound` only |
| Tests | 26/26 numerical/source tests; Lean-hook tests being added |
| Historical artifacts modified? | NO |
| Blockers | none |
| Remaining | commit/push Lean closure checkpoint; reproduce history and run full verifier |

## PROGRESS CAPSULE — #7

| Field | Value |
|---|---|
| Step | 7 / 8 |
| Gate | clean reproduction and authoritative verification |
| Protocol frozen? | YES |
| Historical Track 1A preserved? | YES — expected failed decision reproduced |
| Covariance audit | complete |
| Paired replication | PASS |
| Independent replication | PASS |
| m=1 control | PASS |
| Lean | PASS |
| Axiom audit | PASS |
| Tests | Track 1 46/46; Track 1A 32/32; Track 1B 31/31 before final-decision test; authoritative 695/695 |
| Historical artifacts modified? | NO — clean tree after reproducer |
| Blockers | none |
| Remaining | freeze final decision/report; run final scoped test; commit/push |

## PROGRESS CAPSULE — #8

| Field | Value |
|---|---|
| Step | 8 / 8 |
| Gate | `MGT1-TRACK1B-CLOSED` |
| Protocol frozen? | YES |
| Historical Track 1A preserved? | YES |
| Covariance audit | complete — old independence SE valid |
| Paired replication | PASS |
| Independent replication | PASS |
| m=1 control | PASS |
| Lean | PASS — conditional stable spine, not full concrete instantiation |
| Axiom audit | PASS — standard axioms only |
| Tests | 805/805 combined after final scoped decision guard |
| Historical artifacts modified? | NO |
| Blockers | none |
| Remaining | none; do not start next proof track |
