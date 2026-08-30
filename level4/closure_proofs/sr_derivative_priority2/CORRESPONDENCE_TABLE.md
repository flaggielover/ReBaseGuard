# Cross-representation correspondence

| Feature | Human theorem/proof | Authoritative Stage D | Independent Python | Lean | Arb witness | Historical SR / Priority 1 |
|---|---|---|---|---|---|---|
| Initialization | `R_0^+=R_0^-=0` | zero log states | raw/log zeros | `reset` | exact zeros | matches historical SR |
| Recurrence | `(1+R)exp(+-Z-1/2)` | `_sr_update` log form | independently raw and log | `srStep` | interval raw recurrence | historical SR regression only |
| Likelihood sign | `Z~N(-e,1)`, score `-T_tau` | residual is `raw-e` | focused density-ratio test | score consumed as derivative hypothesis | exact normalized tilt score | not inferred from CUSUM |
| Threshold | natural `A`, inclusive | takes `log(A)` once | natural `520.886...` | predicate `A<=max` | exact `A=2` witness | old `520.3125` non-authoritative |
| Timing/index | update then test, `t>=1` | same | same | finite first alarm | certified `1` and `6` | matches protected SR |
| Terminal increment | included | total/buffer updated first | included by both routes | stopped record carries terminal | included | `m=1` anchor |
| Stopped sum | `sum_{1..tau}Z_t` | `T` | raw score route | abstract `T`/record total | exact rational | same convention |
| Window | `w=min(m,tau)` | convention A | both routes compute suffix | `windowLength` | exact suffix | Priority 1 generic identity |
| Denominator | random `w` | `gamma_m("A")` | direct suffix divided by `w` | `directTerm` | exact correction | not fixed to `m` on short paths |
| `tau<m` | whole stopped path | supported | observed/fixtures | short branch | `tau=1` | detector-independent identity reused explicitly |
| `tau=m` | full path, zero correction | supported | fixture | full branch | algebraic | distinct from Stage-A dwell |
| `tau>m` | last `m` residuals | supported | observed/fixtures | full branch | `tau=6` | ordinary Stage-D object |
| `rho` | outer affine multiplier | mixed reference convention | exact scaling after estimates | derivative/stability algebra | `1/4`, `1` | no new stochastic simulation |
| Evidence | analytical theorem | frozen definition | empirical Gaussian | conditional formal spine | rigorous finite support only | prior evidence, not substitute |

All representations use the ordinary Stage-D stop. No representation equates
it with a minimum-dwell Stage-A stopping time for `m>1`.
