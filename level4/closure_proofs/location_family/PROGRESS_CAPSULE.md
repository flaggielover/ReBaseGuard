# Track-3 progress capsule

## Capsule 1 — forensic baseline

| Field | Value |
|---|---|
| Phase | 0 / 8 |
| Gate | forensic audit |
| Protocol frozen? | NO |
| New outcomes generated? | NO |
| Baseline HEAD | `a2d1ebce9ce13346ebc0b8af3c8fa25f631a56fe` |
| Baseline authoritative tests | 695 / 695 passed |
| Historical integrity | PASS; worktree initially clean |
| Stage D/F | unchanged: `STAGE-D-PARTIAL`, `LEVEL-4-PARTIAL` |
| Track 1/1A/1B/2 | unchanged |
| Blocker | none |
| Estimated remaining runtime | several hours, dominated by frozen Monte Carlo and Lean |
| Git checkpoint | `a2d1ebc` |

## Capsule 2 — definition and human theorem

| Field | Value |
|---|---|
| Phase | 2 / 8 |
| Gate | human theorem design |
| Protocol frozen? | NO |
| New outcomes generated? | NO |
| Parameter score | `s=f'/f=-psi` |
| Actual reuse gain | `Gamma_f=E[Z_tau sum psi(Z_t)]` |
| Stage-D ambiguity | mathematically neither candidate for raw reuse; historical `AMBIGUOUS` preserved |
| Gaussian reduction | exact |
| Human theorem | written under explicit path, density, stopped-change-of-measure, integrability, and domination hypotheses |
| Lean status | NOT STARTED; numerical authorization required |
| Historical integrity | PASS |
| Blocker | none |
| Estimated remaining runtime | several hours |
| Git checkpoint | pending protocol-freeze commit |

## Capsule 3 — protocol freeze

| Field | Value |
|---|---|
| Phase | 3 / 8 |
| Gate | protocol frozen before outcomes |
| Protocol frozen? | YES — SHA-256 `52a27f178f91b88abfc78c28c327084eedafa61e6e91b24354a9faf1b3ed55f6` |
| New outcomes generated? | NO |
| Families | Gaussian, t10, t5, t3, contaminated-normal 5% and 10% |
| Edge case | translated uniform, analytic negative control only |
| Master seed | `2026082307`, absent before freeze |
| Primary finite-difference step | `0.0125` |
| Lean status | NOT STARTED; numerical gate required |
| Historical integrity | dependency manifest frozen |
| Blocker | none |
| Estimated remaining runtime | several hours |
| Git checkpoint | pending freeze commit |

## Capsule 4 — numerical gate

| Field | Value |
|---|---|
| Phase | 5 / 8 |
| Gate | `LOCATION-FAMILY-NUMERICAL-FAILED` |
| Protocol frozen? | YES — unchanged |
| New outcomes generated? | YES — one frozen campaign |
| Regular family verdicts | 5 PASS, t3 FAIL |
| t3 pooled correspondence | PASS: `|z|=0.158`, 0.995% |
| t3 replication criterion | FAIL: `|z|=1.318`, 4.605% > 3% |
| Gaussian control | PASS |
| Structural/tie/source controls | PASS; zero ties |
| Lean status | NOT AUTHORIZED; will not start |
| Historical integrity | PASS |
| Blocker | frozen t3 replication-relative gate |
| Estimated remaining runtime | under one hour for audit, reports, and verification |
| Git checkpoint | pending numerical-gate commit |

## Capsule 5 — final partial closeout

| Field | Value |
|---|---|
| Phase | 8 / 8 |
| Gate | `LOCATION-FAMILY-THEOREM-PARTIAL` |
| Protocol frozen? | YES — unchanged |
| New outcomes generated? | YES — no rerun or resizing |
| Human theorem | PROVED under explicit hypotheses |
| Numerical gate | FAILED, exact t3 predicate preserved |
| Lean / axiom audit | NOT AUTHORIZED / NOT RUN |
| Retained numerical audit | PASS |
| Track-3 tests | target 37 / 37 |
| Full verification | pending clean closing-commit replay |
| Historical integrity | PASS; no global re-audit |
| Blocker | all-family numerical gate prevents closure |
| Estimated remaining runtime | final clean verification only |
| Git checkpoint | pending final commit |
