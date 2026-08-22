# The Stage-D truncated-window derivative theorem

**Status:** `HUMAN-PROVED` before confirmatory numerics
**Protocol:** SHA-256 `27c3cddad3a09520a562b444e9635a3f4155464ac322f01edc79e0fc74c2d9af`

## 1. Definitions

Let `(Z_t)_{t>=1}` be the residual sequence supplied to the frozen two-sided
CUSUM. Under `P_e`, the coordinates are iid `N(-e,1)`. On a common canonical
path space, let

\[
 \tau=\inf\{t\ge1:\max(S_t^+,S_t^-)\ge5\},\qquad
 T_\tau=\sum_{t=1}^{\tau}Z_t,
\]

where `k=1/2`, the alarm boundary is inclusive, and the terminal observation
is included.

For a fixed positive integer `m`, set

\[
 w_m=\min(m,\tau),\qquad
 S_m=\sum_{r=0}^{w_m-1}Z_{\tau-r},\qquad
 A_m=\frac{S_m}{w_m}.
\]

The Stage-D update at reuse fraction `rho in [0,1]` is

\[
 E^+=\rho(e+A_m)+(1-\rho)\bar Y_m,
\]

where `Ybar_m` is independent of the stopped path and has mean zero. Define

\[
 F_{\rho,m}(e)=E_e[E^+\mid E=e],\qquad
 \widetilde\Gamma_m=E_0[A_mT_\tau].
\]

For `r>=0`, also define

\[
 \gamma_r=E_0[\mathbf1_{\{\tau>r\}}Z_{\tau-r}T_\tau]
\]

and

\[
 C_m=E_0\left[\mathbf1_{\{\tau<m\}}
      \left(\frac1\tau-\frac1m\right)T_\tau^2\right].
\]

## 2. Theorem

### General stopped-Gaussian form

Suppose:

1. `tau>=1` is an almost-surely finite stopping time for the coordinate
   filtration;
2. `A_m`, `T_tau`, and `tau` are measurable;
3. `A_m` is square-integrable under `P_0`;
4. for some `p,q>0`, `E_0 exp(p|T_tau|)<infinity` and
   `E_0 exp(q tau)<infinity`;
5. on the stopped sigma-field, the Gaussian location likelihood ratio is
   `L_e=exp(-eT_tau-e^2 tau/2)`.

Then `F_{rho,m}` is differentiable at zero and

\[
 \boxed{F'_{\rho,m}(0)=\rho(1-\widetilde\Gamma_m)}. \tag{T1}
\]

Moreover,

\[
 \boxed{\widetilde\Gamma_m
   =\frac1m\sum_{r=0}^{m-1}\gamma_r+C_m}. \tag{T2}
\]

### Frozen Stage-D CUSUM corollary

All five assumptions hold for the frozen Gaussian CUSUM. Therefore (T1) and
(T2) hold for every fixed positive integer `m` and every `rho in [0,1]` for
the actual Stage-D truncated-window reuse map.

## 3. Lemmas

### Lemma 1 — stopped-window measurability

For fixed `r`, define the lag-selected coordinate on `{tau>r}` by

\[
 V_r=\mathbf1_{\{\tau>r\}}Z_{\tau-r}
    =\sum_{n=r+1}^{\infty}\mathbf1_{\{\tau=n\}}Z_{n-r}.
\]

Each slice is measurable and the events are disjoint, so `V_r` is measurable.
The integer-valued variables `w_m=min(m,tau)` and `1/w_m` are measurable, and

\[
 A_m=\frac1{w_m}\sum_{r=0}^{m-1}V_r
\]

is a finite combination of measurable functions. This also handles `tau<m`;
no undefined lag is evaluated outside its indicator.

### Lemma 2 — finite-lag square integrability

The existing frozen-CUSUM alarm-time result supplies an exponential moment:
for some `q>0`, `K=E_0[e^{q tau}]<infinity`. Hence

\[
 P_0(\tau=n)\le Ke^{-qn}.
\]

For fixed `r`, Cauchy–Schwarz on each stopping slice and the standard-Gaussian
fourth moment give

\[
\begin{aligned}
 E_0[V_r^2]
 &=\sum_{n=r+1}^{\infty}E_0[\mathbf1_{\{\tau=n\}}Z_{n-r}^2]\\
 &\le\sum_{n=r+1}^{\infty}
       (E_0 Z_{n-r}^4)^{1/2}P_0(\tau=n)^{1/2}\\
 &\le\sqrt{3K}\sum_{n=r+1}^{\infty}e^{-qn/2}<\infty.
\end{aligned}
\]

No independence between `{tau=n}` and `Z_{n-r}` is assumed.

By Jensen's inequality for the random finite average,

\[
 |A_m|^2\le\frac1{w_m}\sum_{r=0}^{w_m-1}Z_{\tau-r}^2
       \le\sum_{r=0}^{m-1}V_r^2.
\]

The sum is finite because `m` is fixed. Thus `A_m` is square-integrable.

### Lemma 3 — stopped change of measure

On `{tau=n}`, the ordinary `n`-coordinate Gaussian location likelihood ratio
is

\[
 L_{e,n}=\exp\left(-e\sum_{t=1}^nZ_t-\frac{e^2n}{2}\right).
\]

Since `{tau=n}` belongs to the `n`th sigma-field, summing the deterministic-time
change-of-measure identity over the disjoint stopping slices gives, for every
integrable stopped functional `H`,

\[
 E_e[H]=E_0[H L_e],\qquad
 L_e=\exp(-eT_\tau-e^2\tau/2).
\]

Absolute convergence near zero follows from Lemma 4 below. This slice argument
accounts for the dependence of `tau`, `w_m`, and the terminal/lagged
observations on `e`; no pathwise derivative of `tau` is taken.

### Lemma 4 — domination for differentiation under stopping

Pointwise,

\[
 \frac{d}{de}(A_mL_e)
   =-A_m(T_\tau+e\tau)L_e.
\]

For `|e|<=delta`, because the quadratic term in the likelihood exponent is
nonpositive,

\[
 \left|\frac{d}{de}(A_mL_e)\right|
 \le |A_m|(|T_\tau|+\delta\tau)e^{\delta|T_\tau|}. \tag{D}
\]

Choose `0<delta<p/4`. By Cauchy–Schwarz, the expectation of the right-hand
side is bounded by `||A_m||_2` times the square root of

\[
 E_0[(|T_\tau|+\delta\tau)^2e^{2\delta|T_\tau|}].
\]

The `T_tau` term is finite because a polynomial is absorbed by
`exp(p|T_tau|)` when `2delta<p`. For the mixed alarm-time term,

\[
 E_0[\tau^2e^{2\delta|T_\tau|}]
 \le (E_0\tau^4)^{1/2}(E_0e^{4\delta|T_\tau|})^{1/2}<\infty.
\]

The first factor follows from the exponential moment of `tau`; the second from
`4delta<p`. Thus (D) is an integrable uniform dominator. Dominated
differentiation is justified.

### Lemma 5 — exact rho scaling

Independence is stronger than necessary here; zero conditional mean suffices:

\[
\begin{aligned}
 F_{\rho,m}(e)
 &=\rho(e+E_eA_m)+(1-\rho)E\bar Y_m\\
 &=\rho F_{1,m}(e).
\end{aligned}
\]

Therefore `F'_{rho,m}(0)=rho F'_{1,m}(0)` exactly.

### Lemma 6 — exact short-cycle correction

Let

\[
 B_m=\frac1m\sum_{r=0}^{m-1}\mathbf1_{\{\tau>r\}}Z_{\tau-r}
     =\frac{S_m}{m}.
\]

Pointwise,

\[
 (A_m-B_m)T_\tau
 =\left(\frac1{w_m}-\frac1m\right)S_mT_\tau.
\]

On `{tau>=m}`, `w_m=m` and this is zero. On `{tau<m}`, `w_m=tau` and the
window is the whole stopped path, so `S_m=T_tau`. Hence

\[
 (A_m-B_m)T_\tau
 =\mathbf1_{\{\tau<m\}}
   \left(\frac1\tau-\frac1m\right)T_\tau^2.
\]

Taking expectations gives
`widetilde Gamma_m=E_0[B_mT_tau]+C_m`. Finite-sum linearity gives

\[
 E_0[B_mT_\tau]=\frac1m\sum_{r=0}^{m-1}\gamma_r,
\]

which proves (T2). It also proves `C_m>=0`.

## 4. Proof of the theorem

By Lemma 3 with `H=A_m`,

\[
 F_{\rho,m}(e)=\rho\{e+E_0[A_mL_e]\}.
\]

Lemmas 1, 2, and 4 justify differentiating the expectation at zero. Since

\[
 \left.\frac{dL_e}{de}\right|_{e=0}=-T_\tau,
\]

we obtain

\[
 F'_{\rho,m}(0)
 =\rho\{1-E_0[A_mT_\tau]\}
 =\rho(1-\widetilde\Gamma_m),
\]

proving (T1). Lemma 6 proves (T2).

For the frozen CUSUM, stopping-time measurability and exponential moments of
`tau` and `T_tau` are already established in the Level 1–3 Lean/human proof
chain. Lemma 2 extends the existing terminal-coordinate slice argument to the
finitely many required lags. Thus the assumptions of the general form are
discharged and the frozen Stage-D corollary follows.

## 5. Reductions and edge cases

### `m=1`

Here `w_1=1`, `A_1=Z_tau`, `C_1=0`, and

\[
 \widetilde\Gamma_1=E_0[Z_\tau T_\tau].
\]

Thus (T1) becomes the established identity

\[
 F'_{\rho,1}(0)=\rho(1-\Gamma).
\]

### `rho=0`

The next reference is fresh and has mean zero, so `F_{0,m}` is identically
zero and its derivative is zero. Formula (T1) gives the same result.

### `rho=1`

Full reuse gives `F'_{1,m}(0)=1-widetilde Gamma_m`.

### `tau<m`

The denominator is `tau`, the stopped window is the whole stopped path, and
`A_m=T_tau/tau`. These cycles contribute exactly `C_m` beyond the historical
fixed-denominator lag average. They do not create an extra term beyond
`widetilde Gamma_m`; they explain why the historical lag formula did not equal
the Stage-D convention-A scalar.

## 6. Where assumptions enter

- **Gaussianity:** the explicit likelihood ratio and standard-Gaussian moment
  bound in Lemma 2. The rho and short-cycle algebra do not use Gaussianity.
- **Stopping-time integrability:** the geometric slice sum, polynomial moments
  of `tau`, and the uniform domination in Lemma 4.
- **Random `tau` and `w_m`:** encoded inside the stopped functional and handled
  by the likelihood-ratio/slice argument, not differentiated pathwise.
- **Symmetry:** not required for the derivative identity. It implies `F(0)=0`
  for the two-sided symmetric detector, but the proof above does not depend on
  it.

## 7. Historical formula assessment

The historical Stage-D convention-A scalar

\[
 E_0\left[\frac1{\min(m,\tau)}
   \sum_{r<\min(m,\tau)}Z_{\tau-r}T_\tau\right]
\]

is the correct scalar in the derivative theorem. The historical claim that the
same scalar equals `(1/m)sum_{r<m}gamma_r` is wrong for the truncated
denominator; it omits `C_m`. Historical D2.3 remains `FAILED`. A successful new
correspondence result would be a later closure-proof result, never a retroactive
Stage-D pass.
