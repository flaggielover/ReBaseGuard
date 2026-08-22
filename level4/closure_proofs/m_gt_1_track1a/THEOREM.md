# Human theorem package

**Human status:** proved in the prior track and re-audited here  
**Track 1A Lean status:** not started because the frozen numerical stop gate failed

## 1. Stage-D definition

Under `P_e`, the residuals are iid `N(-e,1)`. Let `tau` be the ordinary
two-sided-CUSUM alarm time, let

`T_tau = sum_{t=1}^tau Z_t`, `w_m=min(m,tau)`, and

`A_m^D = (1/w_m) sum_{r=0}^{w_m-1} Z_{tau-r}`.

For reuse fraction `rho`, the zero-mean fresh term drops from the conditional
mean, so

`F_{rho,m}(e) = rho (e + E_e[A_m^D])`.

Define

`GammaTilde_m = E_0[A_m^D T_tau]`.

## 2. Derivative identity

On the stopped sigma-field, the Gaussian location likelihood ratio relative
to `P_0` is

`L_e = exp(-e T_tau - e^2 tau/2)`.

Thus

`F_{rho,m}(e) = rho (e + E_0[A_m^D L_e])`.

The prior track proved stopped measurability, square integrability of each
fixed finite window, exponential stopped moments, and a uniform integrable
dominator. Differentiation under the expectation is therefore valid at zero.
Since `L'_0=-T_tau`,

`F'_{rho,m}(0) = rho (1 - E_0[A_m^D T_tau])`.

Hence

`F'_{rho,m}(0) = rho (1-GammaTilde_m)`.

Rho scaling is exact, not asymptotic: the fresh statistic has zero mean and
the update is affine.

## 3. Short-cycle decomposition

Let

`B_m^D = (1/m) sum_{r=0}^{min(m,tau)-1} Z_{tau-r}`

and

`C_m = E_0[1{tau<m}(1/tau-1/m)T_tau^2]`.

If `m<=tau`, both denominators equal `m`. If `tau<m`, the stopped suffix is the
entire path, its sum is `T_tau`, and

`(A_m^D-B_m^D)T_tau = (1/tau-1/m)T_tau^2`.

Therefore, pointwise and then in expectation,

`GammaTilde_m = E_0[B_m^D T_tau] + C_m`

and

`GammaTilde_m = (1/m) sum_{r=0}^{m-1} gamma_r + C_m`,

where

`gamma_r = E_0[1{tau>r}Z_{tau-r}T_tau]`.

The correction is nonnegative because `tau<m` implies `1/tau-1/m>0` and
`T_tau^2>=0`. The historical fixed-denominator lag average alone is therefore
incomplete under the actual Stage-D truncated-window convention.

## 4. Stage A is a different stopped object

Stage A uses

`tau_m = inf {t>=m : alarm at t}`

and

`A_m^A = (1/m) sum_{r=0}^{m-1} Z_{tau_m-r}`.

There is no `tau_m<m` branch. Relative to Stage A, Stage D changes two things:

1. the stop from `tau_m` to the ordinary `tau`; and
2. on ordinary short cycles, the denominator from fixed `m` to `tau`.

Writing `Gamma_A=E[A_m^A T_{tau_m}]` and
`Gamma_B=E[B_m^D T_tau]` separates the gain difference exactly:

`Gamma_D-Gamma_A = (Gamma_B-Gamma_A)+C_m`.

The first parenthesis is the stopping-time contribution; `C_m` is the
denominator/window contribution. No sign theorem is asserted for the first.

## 5. `m=1`

At `m=1`, `tau_1=tau`, `w_1=1`, `A_1^A=A_1^D=Z_tau`, and `C_1=0`. The theorem
reduces exactly to the established identity

`F'_{rho,1}(0)=rho(1-E_0[Z_tau T_tau])`.

Track 1A's shared-stream control verified these equalities bit-for-bit on
20,000 paths. Its independent estimates also agreed within `0.991` combined
SE, and its four-route pooled gain agreed with the prior independent estimate
within `0.146` combined SE.

## 6. Evidentiary boundary

This document is a human proof. The prior Level 1–3 Lean infrastructure
machine-checks a generic stopped-likelihood differentiation interface, but
Track 1A did not instantiate that interface for `A_m^D`: the frozen numerical
protocol stopped before Lean. No Track 1A machine-checked theorem is claimed.

