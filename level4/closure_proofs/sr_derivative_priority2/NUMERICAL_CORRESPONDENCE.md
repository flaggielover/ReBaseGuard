# Independent frozen-Gaussian SR numerical correspondence

## Result

All twelve preregistered `(m,rho)` cells passed the direct-map versus stopped
score gate, Richardson diagnostic, step-ladder check, fixed sample-escalation
precision rule, finiteness rule, and exact-tie rule.

The raw-state score route and log-state direct route are separately written,
import neither Stage D nor the protected SR package, and use disjoint seed
families. The direct route uses common random numbers only between its own
`+h/-h` conditions.

| `m` | `GammaTilde_m^SR` | batch SE | `P` sample count with `tau<m` | score multiplier `1-GammaTilde` |
|---:|---:|---:|---:|---:|
| 1 | 17.453571 | 0.065881 | 0 | -16.453571 |
| 2 | 14.500510 | 0.056725 | 0 | -13.500510 |
| 3 | 12.972655 | 0.049011 | 1 | -11.972655 |
| 5 | 11.048526 | 0.041047 | 37 | -10.048526 |

The final score route used 48 batches of 5,000 paths. Its mean stopping time
was `465.798125`. Pilot and final routes recorded zero exact ties and the final
routes recorded zero simultaneous crossings.

At the smallest step `h=0.0125`, absolute direct-versus-score differences over
all cells ranged from `0.00982` to `0.08275`, within their frozen limits. At
`rho=0.1`, the direct derivatives for `m=1,2,3,5` were respectively
`-1.61226`, `-1.32404`, `-1.17347`, and `-0.98522`, versus score predictions
`-1.64536`, `-1.35005`, `-1.19727`, and `-1.00485`.

Complete batch values, SEs, step diagnostics, thresholds, seeds, and gate
margins are in `results/numerical_correspondence.json`.

## Evidence boundary

This is empirical correspondence for the authoritative frozen infinite-horizon
Gaussian SR detector. It is not an Arb or interval-certified evaluation of
those `m>1` values.
