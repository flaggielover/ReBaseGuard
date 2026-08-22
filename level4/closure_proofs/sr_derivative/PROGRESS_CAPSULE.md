# Progress capsules

## PROGRESS CAPSULE — #1

| Field | Value |
|---|---|
| Step | 1 / 9 |
| Gate | repository and definition audit |
| Authoritative SR threshold | `A = 520.886133602749` |
| Protocol frozen? | NO |
| Historical artifacts preserved? | YES |
| Definition/code correspondence | complete |
| Forcing bound | re-derived from the raw recursion |
| Human theorem | NOT STARTED |
| Confirmatory numerics | NOT STARTED |
| Lean | NOT STARTED |
| Arb | NOT STARTED — non-blocking and post-Lean only |
| Baseline verification | 695 / 695 passed |
| Blockers | none |
| Remaining | freeze/hash the approved protocol before outcomes |

## PROGRESS CAPSULE — #2

| Field | Value |
|---|---|
| Step | 2 / 9 |
| Gate | pre-outcome protocol freeze |
| Authoritative SR threshold | `A = 520.886133602749` |
| Protocol frozen? | YES — `e9b66ff8ffbf0d8138598b1d4dc19dcc1e44d8b4f33f5b462b5b82f341d5f762` |
| Historical artifacts preserved? | YES — 139-file manifest passes |
| Definition/code correspondence | PASS |
| Forcing bound | PASS — derived from authoritative raw recursion |
| Human theorem | NOT STARTED |
| Confirmatory numerics | NOT STARTED; no outcome file existed at freeze |
| Lean | NOT STARTED |
| Arb | NOT STARTED — non-blocking and post-Lean only |
| Tests | 10 / 10 pre-freeze checks passed before hash record |
| Blockers | none |
| Remaining | commit/push freeze; prove human theorem; implement frozen numerical routes |

## PROGRESS CAPSULE — #3

| Field | Value |
|---|---|
| Step | 3 / 9 |
| Gate | human theorem and analytic obligations |
| Protocol frozen? | YES — unchanged |
| Definition/code correspondence | PASS |
| Human theorem | CLOSED — stopped-score proof with SR-specific tail argument |
| Concrete analytic obligations | CLOSED (human) — measurability, tail, moments, stopped likelihood, domination |
| Symmetry and rho scaling | CLOSED structurally in the human proof |
| Confirmatory numerics | NOT STARTED |
| Lean | NOT AUTHORIZED pending numerical gate |
| Arb | NOT STARTED — non-blocking and post-Lean only |
| Historical artifacts preserved? | YES |
| Blockers | none |
| Remaining | implement and test the frozen numerical routes; then generate outcomes |

## PROGRESS CAPSULE — #4

| Field | Value |
|---|---|
| Step | 4 / 9 |
| Gate | pre-outcome numerical implementation |
| Protocol frozen? | YES — unchanged |
| Human theorem | CLOSED |
| Route A | raw-state implementation ready; no confirmatory outcome yet |
| Route B | independently written log-state implementation ready; no confirmatory outcome yet |
| Paired uncertainty | batch derivative is the statistical unit |
| Structural controls | PASS — correspondence, reflection, rho, ties, source/seed separation |
| Confirmatory numerics | NOT STARTED |
| Lean | NOT AUTHORIZED |
| Arb | NOT STARTED |
| Tests | 35 / 35 scoped pre-outcome tests passed |
| Historical artifacts preserved? | YES |
| Blockers | none |
| Remaining | commit/push implementation; execute the immutable confirmatory protocol |

## PROGRESS CAPSULE — #5

| Field | Value |
|---|---|
| Step | 5 / 9 |
| Gate | `NUMERICAL GATE CLOSED — LEAN AUTHORIZED` |
| Protocol frozen? | YES — unchanged |
| Calibration reproduction | PASS — candidate error `0.333%` |
| Fixed operating point | PASS — ARL ratio error `0.162%` |
| Route A | PASS — `Gamma=17.29132 ± 0.02757`, historical `z=-0.726` |
| Route B | PASS — primary `-16.19501 ± 0.03906`, pooled `|z|=2.015` |
| Independent replication | PASS — agreement `|z|=0.741` |
| Exact ties | 0 |
| Gamma above two | CONFIRMATORY NUMERICAL ONLY |
| Lean | AUTHORIZED, not yet started at this capsule |
| Arb | NOT STARTED — non-blocking and post-Lean only |
| Historical artifacts preserved? | YES |
| Blockers | none |
| Remaining | freeze numerical report; formalize and audit conditional Lean spine |

## PROGRESS CAPSULE — #6

| Field | Value |
|---|---|
| Step | 6 / 9 |
| Gate | conditional Lean proof spine and axiom audit |
| Protocol frozen? | YES — unchanged |
| Human theorem | CLOSED |
| Numerical correspondence | PASS |
| Lean | PASS — finite SR reflection, stopped record, rho/derivative algebra, instability implication |
| Analytic boundary | explicit — concrete infinite SR obligations remain human-proved |
| Axiom audit | PASS — `propext`, `Classical.choice`, `Quot.sound` only |
| Forbidden placeholders | none |
| Gamma above two | CONFIRMATORY NUMERICAL ONLY |
| Arb | AUTHORIZED NEXT — non-blocking rigor upgrade |
| Historical artifacts preserved? | YES |
| Blockers | none |
| Remaining | commit Lean checkpoint; attempt authoritative-threshold Arb upgrade |

## PROGRESS CAPSULE — #7

| Field | Value |
|---|---|
| Step | 7 / 9 |
| Gate | non-blocking authoritative-threshold Arb attempt |
| Protocol frozen? | YES — unchanged |
| Derivative theorem | human, numerical, and Lean gates PASS |
| Arb threshold | exact runtime rational for `A=520.886133602749` |
| Fresh candidate | recomputed — midpoint `17.29084`, not a Gamma enclosure |
| Outward-rounded geometry | PASS |
| Representative residual cells | completed; raw-box dependency loss persists |
| Global cover/residual propagation | INCOMPLETE |
| Independent OPEN-status audit | PASS |
| Gamma above two | CONFIRMATORY NUMERICAL ONLY |
| Rigorous SR local-instability certificate | OPEN — non-blocking |
| `SR-GAMMA-CERTIFIED` | NOT AWARDED |
| Historical artifacts preserved? | YES |
| Blockers | none for derivative closure |
| Remaining | final reproducer, full repository verification, reports and decision |
