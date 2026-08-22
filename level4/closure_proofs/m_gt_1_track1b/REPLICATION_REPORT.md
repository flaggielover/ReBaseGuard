# Correlation-aware replication report

**Numerical decision:** `PASS`  
**Lean gate:** `NUMERICAL GATE CLOSED — LEAN AUTHORIZED`  
**Protocol:** `c4eca15f8e72059a8d7cb3f0a5dc8fe7922183b90594b4a9574ded4e94c775c6`

## 1. Track 1A uncertainty diagnosis

Track 1A's direct and reconstruction estimators used disjoint seed families
and disjoint stopped paths. Their covariance was zero by design, so
`sqrt(SE_X^2+SE_Y^2)` was valid. The old `3.130` result is not explained by a
missing covariance term and remains a frozen failure.

Track 1B deliberately paired both calculations on the same paths. The paired
covariance is positive and essentially maximal, so it must be subtracted in
`Var(X-Y)`.

## 2. Route P — paired same-path result

| `m` | mean direct−reconstruction | paired SE | naive independence SE | batch covariance | correlation |
|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0.044419 | 0.063138 | 1.000000000 |
| 2 | +2.22e-16 | 2.29e-16 | 0.037331 | 0.044595 | 1.000000000 |
| 5 | -3.33e-16 | 1.93e-16 | 0.028174 | 0.025402 | 1.000000000 |
| 10 | +1.11e-16 | 1.58e-16 | 0.017856 | 0.010202 | 1.000000000 |
| 20 | -6.94e-17 | 8.91e-17 | 0.010500 | 0.003528 | 1.000000000 |
| 50 | -2.78e-17 | 4.73e-17 | 0.005611 | 0.001008 | 1.000000000 |

The maximum pathwise discrepancy was `8.53e-14`; the maximum absolute batch-
mean discrepancy was `5.33e-15`. All alignment, covariance-identity,
correlation, primitive, source-separation, and correction-sign gates passed.

The table shows why a same-path calculation must retain covariance: the naive
independence SE is many orders of magnitude too large. This observation does
not apply retroactively to Track 1A's disjoint routes.

## 3. Route I — disjoint-seed multivariate cross-check

| `m` | direct | reconstruction | difference ± batch SE | marginal z | relative discrepancy |
|---:|---:|---:|---:|---:|---:|
| 1 | 15.84199 | 15.92487 | -0.08288 ± 0.04377 | -1.894 | 0.522% |
| 2 | 13.21139 | 13.27364 | -0.06225 ± 0.03735 | -1.667 | 0.470% |
| 5 | 10.15878 | 10.20356 | -0.04478 ± 0.02717 | -1.648 | 0.440% |
| 10 | 7.06623 | 7.10949 | -0.04326 ± 0.01624 | -2.664 | 0.610% |
| 20 | 4.24120 | 4.26833 | -0.02713 ± 0.00956 | -2.837 | 0.638% |
| 50 | 2.35172 | 2.36321 | -0.01149 ± 0.00465 | -2.469 | 0.487% |

The full six-dimensional batch-difference covariance gave Hotelling
`T²=15.2599`, condition number `774.8`, and `p=0.043014`. The frozen gate was
`p>=0.01`; every relative discrepancy was below the separate 2% guard.

Per-cell z-values are diagnostics only. No cellwise Track 1A threshold was
reused or reinterpreted.

**Independent route: PASS.**

## 4. Short-cycle correction replication

Track 1B values use Route I-reconstruction only and are not pooled with Track
1A.

| `m` | `P(tau<m)` | `C_m ± batch SE` | Track 1A comparator |
|---:|---:|---:|---:|
| 1 | 0 | 0 exactly | 0 |
| 2 | 0 observed | 0 observed | `7.59e-6` from one event |
| 5 | 0.0007194 | 0.00273995 ± 0.00009062 | 0.00251193 |
| 10 | 0.0074238 | 0.02316266 ± 0.00029840 | 0.02256694 |
| 20 | 0.0277331 | 0.07834101 ± 0.00055082 | 0.07757686 |
| 50 | 0.0896331 | 0.20263707 ± 0.00088520 | 0.20146107 |

Every correction integrand was nonnegative. Zero observed `m=2` short cycles
is permitted by the protocol and is consistent with the extremely rare
`tau=1` event.

## 5. Secondary Stage-A / Stage-D distinction

`Delta=Gamma_D-Gamma_A`; this check does not control the numerical gate.

| `m` | `Delta ± SE` | 95% CI | standardized effect | direction |
|---:|---:|---:|---:|---:|
| 1 | -0.04010 ± 0.04943 | [-0.13698,+0.05679] | -0.00099 | negative |
| 2 | -0.09218 ± 0.04444 | [-0.17927,-0.00508] | -0.00275 | negative |
| 5 | -0.01412 ± 0.03591 | [-0.08451,+0.05627] | -0.00056 | negative |
| 10 | +0.01130 ± 0.02351 | [-0.03477,+0.05737] | +0.00068 | positive |
| 20 | +0.05058 ± 0.01206 | [+0.02694,+0.07421] | +0.00534 | positive |
| 50 | +0.13340 ± 0.00608 | [+0.12148,+0.14532] | +0.02824 | positive |

The preselected effect-bearing `m=20,50` directions replicate Track 1A. The
`m=2` estimate has the opposite sign and excludes zero; this secondary
inconsistency is preserved, not turned into a new gate. With effectively no
short cycles at `m=2`, its distinction is attributable to the stopping-time
difference rather than the denominator correction.

## 6. `m=1` control

On a shared 20,000-path stream, Stage A and Stage D had identical `tau`,
`T_tau`, lags, and gain integrands. Direct and reconstructed Stage-D
integrands agreed exactly, and `C_1=0` exactly.

**`m=1`: PASS.**

## 7. Numerical gate

Every frozen primary criterion passed. Track 1A's failure remains unchanged.

`NUMERICAL GATE CLOSED — LEAN AUTHORIZED`.

