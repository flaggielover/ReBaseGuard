# Frozen Gaussian CUSUM numerical correspondence

**Evidence class:** empirical Monte Carlo, not interval certification.

## Protocol

The hash-pinned `numerics/PROTOCOL.json` was frozen before the final run. The
new implementation restates the CUSUM recurrence and window accumulation and
imports no Stage D, Track 1A, or Track 1B scientific evaluator. Separate seed
families drive the score route, pilot finite differences, and final finite
differences.

The final route used 48 independent batches of 10,000 paths at each `e`, with
`h={0.1,0.05,0.025}`. The independent score route used another 480,000 paths.
The grid was `m={1,2,3,5}` and `rho={0.05,0.1,0.25}`.

## Results before rho scaling

| `m` | `GammaTilde_m` | score slope `1-GammaTilde_m` (SE) | FD `h=.025` (SE) | Richardson (SE) |
|---:|---:|---:|---:|---:|
| 1 | 15.91654 | -14.91654 (0.05991) | -14.57807 (0.07491) | -14.77394 (0.10121) |
| 2 | 13.26482 | -12.26482 (0.05015) | -11.98094 (0.06333) | -12.14202 (0.08470) |
| 3 | 11.95708 | -10.95708 (0.04316) | -10.66598 (0.05893) | -10.81309 (0.07828) |
| 5 | 10.22636 | -9.22636 (0.03524) | -8.97228 (0.04998) | -9.10250 (0.06673) |

All 12 preregistered `(m,rho)` cells passed smallest-step agreement,
Richardson agreement, convergence, precision escalation, and finite-value
gates. Scaling by `rho` was applied only after estimating the full-reuse
slopes, as required by the affine theorem.

## Short and full windows

On the score route, the observed `(tau<m, tau=m, tau>m)` counts were:

| `m` | short | equal | long |
|---:|---:|---:|---:|
| 1 | 0 | 0 | 480000 |
| 2 | 0 | 11 | 479989 |
| 3 | 11 | 88 | 479901 |
| 5 | 310 | 424 | 479266 |

Zero observed short cycles at `m=2` is consistent with their rarity and is not
treated as proof that the event is empty. Forced deterministic fixtures test
`tau<m`, `tau=m`, and `tau>m` for every relevant denominator branch.

## Evidence boundary

This experiment is independent numerical correspondence for the frozen
infinite-horizon Gaussian CUSUM. Its confidence calculations are statistical,
not rigorous intervals. The Arb certificate applies only to the separately
frozen finite-support witness and does not certify any Gaussian CUSUM value in
this table.
