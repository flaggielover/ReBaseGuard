# Exact finite-support SR witness certificate

## Certified construction

At SR threshold `A=2`, Arb at 128-bit precision certifies first alarms at
`tau=1,1,6,6` for the frozen paths `[2]`, `[-2]`,
`[0,0,0,0,0,2]`, and its reflection. Every long-path state through time five
is strictly below the inclusive boundary, and the terminal update crosses.

The normalized tilt

```text
P_e(omega)=p(omega)exp(-eT_tau(omega))/M(e)
```

is analytically a probability family: finite positive weights give a finite,
strictly positive normalizer, and normalized weights sum exactly to one. Sign
symmetry gives `E_0[T_tau]=0`; differentiating the finite sum proves the score
at zero is exactly `-T_tau`, independently of numerical normalization.

## Exact and interval results

| `m` | `GammaTilde_m^SR` | fixed-denominator part | short correction | derivative at `rho=1/4` | derivative at `rho=1` |
|---:|---:|---:|---:|---:|---:|
| 2 | 3 | 2 | 1 | -1/2 | -2 |
| 3 | 8/3 | 4/3 | 4/3 | -5/12 | -5/3 |
| 5 | 12/5 | 4/5 | 8/5 | -7/20 | -7/5 |

Arb encloses all exact values, proves each correction nonnegative, certifies
attraction for `rho=1/4`, repulsion for `rho=1`, and verifies strictly
decreasing finite-difference error over steps `1/4,1/8,1/16,1/32`.

All required checks in `certificates/certificate.json` pass.

## Evidence boundary

This rigorous certificate validates only the exact finite-support
SR-compatible witness. It is not an interval certificate for frozen
infinite-horizon Gaussian SR values at `m=2,3,5`.
