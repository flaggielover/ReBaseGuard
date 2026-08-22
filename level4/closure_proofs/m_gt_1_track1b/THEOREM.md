# Human theorem package

**Human status:** proved

**Lean status:** stable algebraic spine compiled; frozen-CUSUM analytic
instantiation remains outside Lean

## 1. Stage-D object

Under `P_e`, let the ordinary two-sided-CUSUM alarm time be `tau`, let

`T_tau = sum_{t=1}^tau Z_t`, `w_m=min(m,tau)`, and

`A_m = (1/w_m) sum_{r=0}^{w_m-1} Z_{tau-r}`.

For reuse fraction `rho`, the centered fresh-reference contribution has mean
zero and the update is affine, so

`F_{rho,m}(e)=rho(e+E_e[A_m])`.

Define `GammaTilde_m=E_0[A_m T_tau]`.

## 2. Stopped-likelihood derivative

On the stopped sigma-field, the Gaussian location likelihood ratio relative
to `P_0` is

`L_e=exp(-e T_tau-e^2 tau/2)`.

Thus

`F_{rho,m}(e)=rho(e+E_0[A_m L_e])`.

The stopped random variable `A_m` is measurable. For fixed finite `m`, it is
a finite stopped-window average, so the stopped-moment estimates established
in the earlier theorem track supply integrability and a uniform integrable
dominator in a neighborhood of zero. Differentiation under the expectation
then gives

`d/de E_0[A_m L_e]|_{e=0}=-E_0[A_m T_tau]`.

Consequently,

`F'_{rho,m}(0)=rho(1-GammaTilde_m)`.

This analytic application is a human proof. Lean proves the generic
dominated-differentiation bridge and its algebraic consequence under explicit
measurability, integrability, and domination hypotheses; it does not encode
and discharge those hypotheses for the concrete random-window CUSUM object.

## 3. Exact decomposition

Write

`B_m=(1/m) sum_{r=0}^{min(m,tau)-1} Z_{tau-r}`

and

`Q_m=1{tau<m}(1/tau-1/m)T_tau^2`.

If `m<=tau`, then `w_m=m`, so `A_m=B_m` and `Q_m=0`. If `tau<m`, the retained
suffix is the whole stopped path. Its sum is `T_tau`, hence

`(A_m-B_m)T_tau=(1/tau-1/m)T_tau^2=Q_m`.

Therefore the following identity holds pathwise:

`A_m T_tau=B_m T_tau+Q_m`.

Taking expectations yields

`GammaTilde_m=(1/m) sum_{r=0}^{m-1} gamma_r+C_m`,

where

`gamma_r=E_0[1{tau>r}Z_{tau-r}T_tau]`

and

`C_m=E_0[Q_m]`.

On `tau<m`, positivity of `tau` and `m` gives `1/tau-1/m>0`; since
`T_tau^2>=0`, `Q_m>=0` and therefore `C_m>=0`.

## 4. `m=1`

Because `tau>=1`, `min(1,tau)=1`, the short-cycle event `tau<1` is empty, and
`C_1=0`. The result reduces to the already established terminal-observation
identity

`F'_{rho,1}(0)=rho(1-E_0[Z_tau T_tau])`.

## 5. Evidentiary boundary

The decomposition, sign, `m=1`, rho-scaling, and derivative-map algebra are
machine-checked in the Track 1B Lean spine. The generic stopped-integral
differentiation theorem it invokes is also proved in the existing Lean
project, but only under explicit analytic hypotheses.

The following concrete-CUSUM obligations are justified by the human theorem
and prior stopped-moment work, not instantiated in Track 1B Lean:

1. the exact random-window construction of `A_m` on stopped paths;
2. its a.e. strong measurability and integrability;
3. measurability of `T_tau` and real-valued `tau`; and
4. an integrable function uniformly dominating the likelihood-integrand
   derivative near zero.

Accordingly, Track 1B claims a compiled Lean proof spine and a combined human,
formal, and numerical closure. It does not claim that the entire concrete
frozen-CUSUM derivative theorem is machine-checked end to end.
