# ReBaseGuard Level-4 Closure Proof Campaign

## Proof Track 1 — General `m > 1` Derivative Theorem

This namespace contains a new closure-proof result for the Stage-D
truncated-window reuse protocol. It does not revise any historical stage.

Historical status is immutable:

- Level 1–3: `CLOSED`
- Stage B: rigorous deterministic period-2 result
- Stage C: `PARTIAL`
- Stage C.1: `CLOSED-CONFIRMED-SENSITIVITY`
- Stage D: `PARTIAL`
- historical Stage D D2.3: `FAILED`
- Stage E: `PARTIAL`
- Stage F: `LEVEL-4-PARTIAL`

The campaign order is definition audit, human theorem, proof obligations,
independent numerical correspondence, Lean proof spine, then interval
certification only if a new rigorous numerical inequality is claimed.

## PROGRESS CAPSULE — #1

| Field | Value |
|---|---|
| Step | 1 / 8 |
| Gate | repository audit complete |
| Historical artifacts modified? | NO |
| Protocol frozen? | NO |
| Theorem status | candidate |
| Proof obligations | 0 / 13 |
| Numerical correspondence | not started |
| Lean | not started |
| Arb | not started |
| Tests | authoritative baseline: 695 passed |
| Blockers | none |
| Runtime | baseline verifier 228 s |
| Remaining | definition audit and protocol freeze |

## PROGRESS CAPSULE — #2

| Field | Value |
|---|---|
| Step | 3 / 8 |
| Gate | protocol frozen; human theorem next |
| Historical artifacts modified? | NO |
| Protocol frozen? | YES — `27c3cdda…d2d9af` |
| Theorem status | candidate |
| Proof obligations | 4 / 13 |
| Numerical correspondence | not started |
| Lean | not started |
| Arb | not started |
| Tests | authoritative baseline: 695 passed |
| Blockers | none |
| Runtime | baseline verifier 228 s |
| Remaining | prove theorem before numerical exposure |

## PROGRESS CAPSULE — #3

| Field | Value |
|---|---|
| Step | 4 / 8 |
| Gate | human theorem proved; numerical correspondence authorized |
| Historical artifacts modified? | NO |
| Protocol frozen? | YES — `27c3cdda…d2d9af` |
| Theorem status | proved |
| Proof obligations | 10 / 13 human-closed |
| Numerical correspondence | not started |
| Lean | gated on correspondence |
| Arb | not required unless a new inequality is claimed |
| Tests | authoritative baseline: 695 passed |
| Blockers | none |
| Runtime | baseline verifier 228 s |
| Remaining | implement and run frozen correspondence design |

## PROGRESS CAPSULE — #4

| Field | Value |
|---|---|
| Step | 5 / 8 |
| Gate | complete numerical gate failed; stop before Lean |
| Historical artifacts modified? | NO |
| Protocol frozen? | YES — unchanged |
| Theorem status | human-proved; primary correspondence passed |
| Proof obligations | 10 human-proved; M11 FAILED |
| Numerical correspondence | primary PASS; overall FAIL |
| Lean | prohibited by stop gate |
| Arb | not reached |
| Tests | 34 campaign tests passed before full run |
| Blockers | per-cell Stage-A/Stage-D distinction at `m=20` |
| Runtime | full correspondence 133.8 s |
| Remaining | failure diagnosis and partial decision |

## PROGRESS CAPSULE — #5

| Field | Value |
|---|---|
| Step | 6 / 8 |
| Gate | Lean gate not reached |
| Historical artifacts modified? | NO |
| Protocol frozen? | YES — unchanged |
| Theorem status | human-proved |
| Proof obligations | M12 OPEN |
| Numerical correspondence | overall FAIL preserved |
| Lean | NOT STARTED |
| Arb | not reached |
| Tests | campaign result guards added |
| Blockers | numerical stop rule |
| Runtime | no Lean runtime |
| Remaining | certificate scope and final verification |

## PROGRESS CAPSULE — #6

| Field | Value |
|---|---|
| Step | 7 / 8 |
| Gate | certificate scope assessed |
| Historical artifacts modified? | NO |
| Protocol frozen? | YES — unchanged |
| Theorem status | human-proved |
| Proof obligations | M13 not applicable under frozen scope |
| Numerical correspondence | overall FAIL preserved |
| Lean | NOT STARTED |
| Arb | NOT STARTED / no new inequality claimed |
| Tests | final verification pending |
| Blockers | numerical stop rule; Lean open |
| Runtime | no certificate runtime |
| Remaining | full verification and final decision |

## PROGRESS CAPSULE — #7

| Field | Value |
|---|---|
| Step | 8 / 8 |
| Gate | full verification complete |
| Historical artifacts modified? | NO |
| Protocol frozen? | YES — hash matches |
| Theorem status | human-proved, track partial |
| Proof obligations | 10 human-proved / M11 failed / M12 open / M13 N/A |
| Numerical correspondence | primary PASS; complete gate FAIL |
| Lean | NOT STARTED |
| Arb | NOT STARTED / not required |
| Tests | 46 new + 695 historical = 741 passed |
| Blockers | map-distinction replication; Lean gate |
| Runtime | final authoritative verifier 244 s |
| Remaining | final decision and Git checkpoint |

## PROGRESS CAPSULE — #8

| Field | Value |
|---|---|
| Step | final |
| Gate | proof track concluded |
| Historical artifacts modified? | NO |
| Protocol frozen? | YES — `27c3cdda…d2d9af` |
| Theorem status | HUMAN-PROVED; `MGT1-THEOREM-PARTIAL` |
| Proof obligations | M11 FAILED; M12 OPEN |
| Numerical correspondence | central theorem PASS; complete gate FAIL |
| Lean | NOT STARTED by protocol stop |
| Arb | NOT STARTED / no new inequality |
| Tests | 741 passed |
| Blockers | new independent distinction replication required |
| Runtime | correspondence 133.8 s; verification 244 s |
| Remaining | Proof Track 1A (not started) |
