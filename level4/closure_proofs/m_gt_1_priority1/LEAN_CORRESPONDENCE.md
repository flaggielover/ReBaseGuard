# Lean correspondence

**Source:** `lean/MGtOneClosure.lean`

**Namespace:** `RebaseguardLean.Level4Priority1`

## Compiled theorem map

| Lean declaration | Human result |
|---|---|
| `windowLength_eq_tau_of_short` | `w_m=tau` on `tau<m` |
| `windowLength_eq_m_of_full` | `w_m=m` on `m<=tau` |
| `directTerm_short` | whole-path suffix algebra on a short cycle |
| `directTerm_full` | direct and fixed denominators coincide on a full window |
| `direct_eq_fixed_add_short` | pointwise equation (T3) |
| `shortCorrection_nonneg` | `Q_m>=0` |
| `windowLength_one`, `directTerm_one`, `shortCorrection_one` | `m=1` reduction |
| `integral_direct_eq_fixed_add_short` | expectation decomposition (T4) |
| `rho_derivative_of_expectation_derivative` | affine rho scaling |
| `derivative_spine_of_dominated` | Gaussian stopped-likelihood derivative under explicit abstract assumptions |
| `attraction_from_derivative_bound` | multiplier magnitude below one criterion |
| `repulsion_from_derivative_bound` | multiplier magnitude above one criterion |
| `multiplier_abs_of_nonneg_of_one_le` | threshold algebra for nonnegative rho and `Gamma>=1` |

## What Lean assumes and consumes

`derivative_spine_of_dominated` explicitly consumes a.e. strong measurability
of `A`, `T`, and real-valued `tau`; integrability of `A`; a positive local
radius; an integrable dominating function; and an almost-everywhere uniform
bound on the parameterized derivative. These are abstract hypotheses in the
theorem signature. The generic differentiation theorem they feed is imported
from the frozen Level 1--3 `RebaseguardLean.IntegralBridge` module.

## What remains outside Lean

The new file does not construct the concrete two-sided CUSUM probability
space, its stopping time, or its rolling stopped window. It does not prove
their measurability, almost-sure finiteness, stopped exponential moments, or
the concrete local domination inequality. Those Gaussian-CUSUM obligations
are stated and discharged at the human-theorem level under the explicit
stopped exponential-moment hypothesis. They are not described as
machine-checked.

The Lean file imports no Track 1B source. Its axiom audit reports only the
standard Mathlib foundations `propext`, `Classical.choice`, and `Quot.sound`;
there is no `sorry`, `admit`, or scientific axiom.
