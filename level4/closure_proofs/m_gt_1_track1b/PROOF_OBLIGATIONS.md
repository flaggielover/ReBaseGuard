# Proof and evidence obligations

| ID | Obligation | Status | Evidence |
|---|---|---|---|
| T1B-1 | Track 1 and Track 1A reproduce their historical states | PASS | Track 1 46/46; Track 1A 32/32; expected partial/failed decisions |
| T1B-2 | historical Stage D, Track 1, and Track 1A artifacts immutable | PASS | frozen SHA-256 checks in `tests/test_integrity.py` |
| T1B-3 | protocol frozen before new outcomes | PASS | SHA-256 `c4eca15f…`; commit `253694e…` |
| T1B-4 | Track 1A covariance reconstructed correctly | PASS | compared routes disjoint; covariance zero by design |
| T1B-5 | paired alignment and pathwise decomposition | PASS | maximum path discrepancy `8.53e-14`; maximum batch discrepancy `5.33e-15` |
| T1B-6 | paired covariance formula | PASS | positive covariance, correlation at least `0.999999999`; direct and reconstructed difference variance agree |
| T1B-7 | independent implementation separation | PASS | disjoint source modules and AST import guard |
| T1B-8 | independent-route global cross-check | PASS | Hotelling `p=0.043014 >= 0.01`; maximum relative discrepancy `0.638%` |
| T1B-9 | short-cycle correction nonnegative | HUMAN-PROVED / LEAN-PROVED / NUMERICALLY-CHECKED | `shortCorrection_nonneg`; every generated integrand nonnegative |
| T1B-10 | Stage-A/Stage-D distinction | SECONDARY / MIXED | `m=20,50` historical direction replicated; `m=2` opposite-sign inconsistency preserved |
| T1B-11 | `m=1` reduction | PASS | exact shared-stream structure; `C_1=0`; three Lean reduction lemmas |
| T1B-12 | rho scaling | LEAN-PROVED | `reuseMap_apply`, `reuseMap_zero`, `reuseMap_one` |
| T1B-13 | derivative-map algebra | LEAN-PROVED CONDITIONALLY | `rho_derivative_of_expectation_derivative`; `derivative_spine_of_dominated` |
| T1B-14 | concrete random-window analytic hypotheses | HUMAN-PROVED / NOT INSTANTIATED IN LEAN | measurability, integrability, and domination remain explicit hypotheses |
| T1B-15 | Lean compilation | PASS | pinned Lean/Mathlib compiler, no warnings after cleanup |
| T1B-16 | axiom transparency | PASS | only `propext`, `Classical.choice`, `Quot.sound` |
| T1B-17 | Arb certificate | NOT REQUIRED | no new rigorous numerical inequality claimed |
| T1B-18 | authoritative repository verification | PENDING | run after the Lean closure checkpoint is committed |

The machine-checked claim is deliberately narrower than the human theorem:
Lean checks the stable random-window algebra and the consequence of a general
dominated-differentiation theorem under explicit hypotheses. It does not
construct the frozen CUSUM stopped process or discharge those hypotheses for
`A_m`.
