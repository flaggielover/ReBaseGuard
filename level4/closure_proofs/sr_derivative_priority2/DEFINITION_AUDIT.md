# Authoritative SR definition audit

| Object | Authoritative source | Exact Priority-2 meaning | Classification |
|---|---|---|---|
| Reference error and residual | `level4/stage_d/src/stopped.py::simulate_stopped` | `e=R_j-mu`, `Z=epsilon-e~N(-e,1)` | authoritative, frozen |
| SR initialization | `stopped.py` | `R_0^+=R_0^-=0`; stored log states `Y_0^+=Y_0^-=0`; no head-start | authoritative, frozen |
| Raw recurrence | `stopped.py::_sr_update`; historical `PROTOCOL.md` | `(1+R)exp(+-Z-1/2)` on both charts | authoritative, frozen |
| Log recurrence | `stopped.py::_sr_update` | `ell^+=Y^++Z-1/2`, `ell^-=Y^--Z-1/2`, `Y'=logaddexp(0,ell)` | authoritative stable representation |
| Threshold | Stage-D SR results and historical protocol | natural `A=520.886133602749`; code takes `log` once | authoritative; `520.3125` is obsolete here |
| Alarm timing | `_sr_update`, then `simulate_stopped` crossing handling | inclusive `>=`, after both updates | authoritative, frozen |
| Stopping time | `simulate_stopped` | ordinary `tau=inf{t>=1:alarm after update}` | authoritative, frozen |
| Terminal inclusion | `simulate_stopped` | buffer and total updated before crossed paths finalize | authoritative, frozen |
| Stopped sum | `simulate_stopped` | `T_tau=sum_{t=1}^tau Z_t` | authoritative, frozen |
| Stage-D window | `level4/stage_d/STAGE_D_PROTOCOL.md`; `stopped.py` | `w_m=min(m,tau)`, suffix divided by `w_m` | authoritative, frozen |
| Stage-A dwell | `level4/src/rebaseguard_level4/conditional.py` | alarm eligibility delayed until `t>=m`; distinct for `m>1` | historical distinct object |
| Reference update | `level4/stage_d/src/chain.py` convention | conditional mean `rho(e+E_e[A_m])`; fresh term centered | authoritative generic convention |
| Historical SR theorem | `level4/closure_proofs/sr_derivative/` | protected `m=1` theorem and later certificate | immutable prior evidence |
| Priority-2 theorem | this namespace | same SR stop with ordinary truncated Stage-D window for all positive `m` | newly proved |

## Window branches

- `tau<m`: the suffix is the whole path, `w_m=tau`, and `A_m=T_tau/tau`.
- `tau=m`: the whole path is retained and both denominators equal `m`.
- `tau>m`: exactly the last `m` residuals are retained and divided by `m`.

Because `tau>=1`, the denominator is never singular. It is random and
correlated with the suffix and stopped sum, so it cannot be replaced by `m` on
short cycles.

## Correspondence conclusion

The frozen recurrence and Priority-2 recurrence agree in initialization,
likelihood increments, natural threshold units, inclusive post-update timing,
ordinary stopping index, and terminal inclusion. No CUSUM state, CUSUM stopping
assumption, head-start, or finite-horizon approximation enters the theorem.
