# Standalone proof

## 1. SR stopping and measurability

For a finite prefix, each SR state is a continuous function of that prefix.
Hence `{tau=n}` is the Borel event that every earlier post-update state is
strictly below `A` and the state at `n` reaches `A`. Thus `tau` is a stopping
time. On `{tau=n}`, `T_tau`, `w_m`, the terminal suffix sum, and `A_m` are
finite-coordinate Borel functions. Their countable stopped definitions are
therefore `F_tau`-measurable.

Put `b_A=log(A)+1/2`. Every live raw state is nonnegative. If `Z_t>=b_A`,

```text
R_t^+=(1+R_{t-1}^+)exp(Z_t-1/2)>=A.
```

If `Z_t<=-b_A`, the same argument forces the minus chart. On any compact
`|e|<=e_0`, continuity and positivity of Gaussian tail probabilities give

```text
p_* = inf_{|e|<=e_0} Q_e(|Z_1|>=b_A)>0.
```

Independence of the next innovation from the live state yields

```text
sup_{|e|<=e_0} Q_e(tau>n) <= (1-p_*)^n.
```

Therefore `tau` is almost surely finite and has a uniform small exponential
moment: `sup E_e[exp(c tau)]<infinity` whenever
`exp(c)(1-p_*)<1`.

## 2. Stopped moments

A nonterminal innovation cannot satisfy the forcing inequality. Consequently,
pathwise,

```text
S_tau:=sum_{t=1}^tau |Z_t| <= b_A(tau-1)+|Z_tau|,
|T_tau|<=S_tau,
|A_m|<=S_tau.
```

For `a>=0`, independence at the final trial gives the uniform bound

```text
E_e[exp(a|Z_tau|+c tau)]
 <= sup_{|u|<=e_0} E_u[exp(a|Z_1|)]
    sum_{n>=1} exp(cn)(1-p_*)^(n-1),
```

which is finite for sufficiently small `c>0`. Combining this with the
pathwise bound proves a small exponential moment of `S_tau`. Polynomial
moments of `S_tau` and `tau` follow. In particular `A_m` and
`A_m T_tau` are integrable for every fixed `m`.

## 3. Stopped likelihood and its sign

The density of `N(-e,1)` at residual `z` is `phi(z+e)`. For a deterministic
prefix of length `n`,

```text
product phi(z_t+e)/phi(z_t)
 = exp(-e sum z_t-e^2n/2).
```

Decompose an `F_tau` expectation over `{tau=n}` and apply this finite-prefix
identity on every term. The almost-sure finiteness and integrability above
justify summation, giving on `F_tau`

```text
L_e=dQ_e/dQ_0=exp(-eT_tau-e^2tau/2).
```

Therefore

```text
dL_e/de=-(T_tau+e tau)L_e,
dL_e/de at e=0=-T_tau.
```

This minus sign is a direct consequence of `Z=epsilon-e`.

## 4. Local domination and differentiation

For `|e|<=delta`,

```text
|A_m dL_e/de|
 <= |A_m|(|T_tau|+delta tau)
    exp(delta|T_tau|+delta^2 tau/2).
```

Use `|A_m|,|T_tau|<=S_tau`. Choose `delta>0` small enough that the exponential
rate in `S_tau` and `tau`, after absorbing the polynomial prefactor into a
slightly larger exponential, remains below the stopped exponential-moment
margin from Section 2. The resulting right-hand side is an integrable uniform
dominator. Dominated differentiation now gives

```text
d/de E_e[A_m] at zero
 = E_0[A_m dL_e/de|_0]
 = -E_0[A_mT_tau]
 = -GammaTilde_m^SR.
```

The identity term in `F_{rho,m}` has derivative one and the centered fresh
term has derivative zero, hence

```text
F'_{rho,m}(0)=rho(1-GammaTilde_m^SR).
```

## 5. Exact random-denominator decomposition

Define

```text
B_m=(1/m)sum_{r=0}^{min(m,tau)-1}Z_{tau-r},
Q_m=1{tau<m}(1/tau-1/m)T_tau^2.
```

On `{tau>=m}`, `w_m=m`, so `A_m=B_m` and `Q_m=0`. On `{tau<m}`, the retained
suffix is the whole stopped path, so its sum is `T_tau` and

```text
(A_m-B_m)T_tau=(1/tau-1/m)T_tau^2=Q_m.
```

This also covers the boundary `tau=m`, where both denominators equal `m` and
the correction is zero. Therefore, pathwise and then in expectation,

```text
A_mT_tau=B_mT_tau+Q_m,
GammaTilde_m^SR=E_0[B_mT_tau]+E_0[Q_m].
```

Since `0<tau<m` on the short event, `Q_m>=0`. The random denominator is never
replaced by `m` on a short cycle.

## 6. Reflection and centering

Reflect a residual path by `z_t -> -z_t`. Induction in the two recurrences
exchanges `R_t^+` and `R_t^-` at every step. Thus the inclusive first alarm
time is preserved, while `T_tau` and every terminal suffix average `A_m` are
negated. Under `Q_0` the path law is reflection invariant, so
`E_0[A_m]=0` and `F_{rho,m}(0)=0`. More generally reflection sends `Q_e` to
`Q_{-e}`, making `e+E_e[A_m]` odd.

## 7. Stability and the `m=1` anchor

The multiplier at the fixed point is exactly
`rho(1-GammaTilde_m^SR)`. The standard one-dimensional differentiable-map
criterion gives attraction below unit magnitude and repulsion above it; at
unit magnitude the linear term alone decides nothing.

For `m=1`, positivity of `tau` gives `w_1=1`, `A_1=Z_tau`, and an empty short
event. The theorem reduces to the immutable historical SR `m=1` identity, used
only as a regression anchor.
