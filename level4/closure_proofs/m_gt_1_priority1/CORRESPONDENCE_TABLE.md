# Cross-representation correspondence table

| Concept | Mathematical prose | Independent Python | Lean | Arb witness | Frozen sources / finding |
|---|---|---|---|---|---|
| Index start | `t=1` | loop `range(1,...)` | positive `tau` hypothesis | path arrays begin at first increment | Stage D and frozen model start at 1 |
| Stop timing | alarm after detector update | update states, then test | abstract stopping input | stopping record is frozen data | Stage D uses post-update stop |
| Threshold | inclusive `max(S+,S-)>=5` | literal `>=H`, `H=5` | outside algebraic spine | not a CUSUM fixture | matches frozen primitive |
| Terminal increment | included in `T_tau` and `A_m` | total and buffer updated before stop | whole-suffix hypothesis | included in every frozen path | matches Stage D |
| Nominal window | positive integer `m` | `int64` grid, positivity guard | natural number | `{2,3,5}` | matches Stage D |
| Realized window | `w_m=min(m,tau)` | `np.minimum(m,tau)` | `windowLength=min` | exact integer minimum | Stage D convention A |
| Denominator | random `w_m` | suffix divided pathwise by `w` | `directTerm` | exact rational `1/w` | not Stage A fixed denominator |
| `tau<m` | whole path, denominator `tau` | forced fixture plus observed counts | short branch and correction | `tau=1` pair | Stage A excludes these alarms |
| `tau=m` | whole path, equal denominators | forced fixture and counts | full branch via `m<=tau` | not needed for witness certificate | regression-tested separately |
| `tau>m` | terminal suffix of length `m` | reversed ring-buffer suffix | full branch | `tau=6` pair | matches Stage D |
| Stopped sum | `T_tau=sum_{1}^tau Z_t` | accumulated before stop | abstract `T` | exact rational sum | terminal included |
| Reference error | `e=R-mu` | simulate `Z=X-e` | real parameter | exponential-tilt parameter | Stage D sign convention |
| State map | `rho(e+E_e[A_m])` | `rho` scales estimated base map | affine derivative theorem | exact tilted expectation | Stage D chain uses `e+zbar` |
| Likelihood score | `-T_tau` at zero | score route estimates `E[A_mT]` | Gaussian integral bridge | exact normalized-tilt score | same local score; different families away from zero |
| Derivative sign | `rho(1-GammaTilde_m)` | central FD and independent score | compiled theorem | exact `-13/20`, `-13/8` | matches Track 1B prior evidence |
| Stage A relation | distinct for `m>1`; same at `m=1` | forced/regression tests | `m=1` reduction only | no Stage A claim | minimum dwell changes stopping law |
| Evidence type | theorem under stated assumptions | Monte Carlo | conditional proof spine | rigorous finite-support intervals | no frozen-Gaussian `m>1` interval claim |

## Track 1B relation

Track 1B uses the same ordinary-stop random-window mathematical convention and
is a useful regression anchor. This campaign independently supplies every
required document, numerical run, Lean declaration, interval witness, and gate.
No Track 1B file is imported as a closure result or modified.
