# P7 evidence boundary

P7 uses P3's evidence hierarchy verbatim so the two campaigns can be read
together. No P7 result is rank 1--3.

| rank | class | where it occurs in P7 |
|---:|---|---|
| 1 | `EXACT_SYMBOLIC` | none |
| 2 | `INTERVAL_CERTIFIED` | none |
| 3 | `THEOREM_PLUS_CERTIFIED_INPUT` | none |
| 4 | `THEOREM_PLUS_EMPIRICAL_ESTIMATE` | P7-A evaluated with Monte Carlo response/reference laws; conditional P7-B identity evaluated empirically |
| 5 | `EMPIRICAL_ONLY` | every simulated ARL, FAP, delay, MSE, ACF1 and finite-cycle curve; `A(x)`, `g_m(x)`, `h_m(x)` |
| 6 | `INCONCLUSIVE` | every cell whose effect interval straddles zero |

`THEOREM P7-A` (sufficiency of the reference error) is exact and needs no
numerical input; it is the one structural statement P7 contributes, and it is
proved from the frozen semantics, not measured. Its *use* is rank 4 because the
functions it is evaluated at are estimated.

## What P7 does NOT establish

* **No rigorous enclosure of anything.** There is no Arb layer, no interval
  arithmetic and no Lean spine in P7. The campaign is a statistical-consequence
  study built on two closed theorems, not a new certification layer.
* **No existence or uniqueness of the stationary law `pi`.** P7-B, P7-C and P7-D
  are conditional on a stationary law with finite fourth moment. The chains mix
  within ~3 cycles empirically (`STATISTICAL_CONSEQUENCES.md` §5), but that is
  evidence, not proof. Burn-in is 12 cycles.
* **No closed-form map from `lambda` to stationary dispersion.** Conditional
  P7-C/D use an empirically checked sign condition and Monte Carlo point inputs;
  their tabulated values are plug-in diagnostics, not certified bounds.
* **No first-order monitoring-functional transfer theorem.** Candidate P7-E
  was rejected in independent adjudication: the derivative of `E[e_1]` does not
  determine the derivative of `E[M(e_1)]` when `e_1` remains random.
* **Nothing outside the two frozen Gaussian specialisations**, `m in {1,2,3,5}`,
  `rho in [0,1]`, `k=1/2, h=5` (CUSUM) and `A=520.886133602749` (SR).
* **No claim of novelty.** The absolute ARL cost of re-baselining from `m`
  observations is a matched-information effect, not a P7 discovery; P7 quantifies
  it only to separate it from the reuse-attributable effect.

## Inherited estimates P7 did not re-certify

`rho_c(D,m)` is read from P3's `boundary_table.json`, and P3 labels those gains
`EMPIRICAL_ONLY`. P7 independently re-measured `GammaTilde` at `n = 4x10^5`
(`STATISTICAL_CONSEQUENCES.md` §8) as a correspondence check only; where the two
disagree by more than their stated standard errors this is reported in
`ADVERSARIAL_REVIEW.md` and **not** resolved by P7, which does not own those
numbers.

## Relation to Stage-D D2.5

Stage-D D2.5 tested the `GammaTilde_m = 2` crossing at fixed `rho = 1` along `m`
and returned `MATHEMATICAL, NOT OPERATIONAL`. P7 tests a *different* crossing —
along `rho` at fixed small `m`, where P3's `rho_c` lies in `[0.061, 0.109]`.
Conditional P7-C provides a compatible mass-escape interpretation, not a proof
that either crossing must be featureless. P7 does not supersede D2.5 and does
not reopen it.
