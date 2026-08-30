# Proof of the general Stage-D theorem

## 1. The two window events

Fix a sample path with positive finite `tau`.

On `{tau>=m}`, `w_m=min(m,tau)=m`. Therefore `A_m=B_m` and the indicator in
`Q_m` vanishes. Equation (T3) follows on this event.

On `{tau<m}`, `w_m=tau`. The last `tau` observations are the whole stopped
path, including the terminal increment, so

```text
sum_{r=0}^{tau-1} Z_{tau-r}=sum_{t=1}^tau Z_t=T_tau.
```

It follows that

```text
A_m T_tau=(T_tau/tau)T_tau=T_tau^2/tau,
B_m T_tau=(T_tau/m)T_tau=T_tau^2/m,
```

and their difference is exactly

```text
(1/tau-1/m)T_tau^2=Q_m.
```

The events partition the sample space, proving (T3). On the short event,
`0<tau<m` implies `1/tau-1/m>0`; a square is nonnegative. On the long event
`Q_m=0`. Thus `Q_m>=0` everywhere. Integrability and linearity of expectation
give (T4).

This is why the random denominator cannot be replaced by `m`: doing so deletes
`Q_m`, precisely on short cycles.

## 2. Differentiation of the stopped expectation

Absolute continuity on `F_tau` gives

```text
E_e[A_m]=E_0[A_m L_e].
```

By assumption, `A_m L_e` is differentiable almost surely near zero and its
derivative is dominated by an integrable random variable. The dominated
differentiation theorem therefore yields

```text
d/de E_0[A_m L_e]|_0
 =E_0[A_m dL_e/de|_0]
 =-E_0[A_m T_tau]
 =-GammaTilde_m.
```

The identity map `e -> e` has derivative one. The fresh-reference contribution
has local mean zero by assumption. Differentiating the affine state map gives

```text
F'_{rho,m}(0)=rho(1-GammaTilde_m),
```

which proves (T1) and exact scaling in `rho`.

## 3. Gaussian stopped likelihood and domination

For a deterministic horizon `n`, the density ratio of `n` iid `N(-e,1)`
increments to iid `N(0,1)` increments is

```text
exp(-e T_n-e^2 n/2).
```

Stopping and restricting to `F_tau` gives (T2) by the standard stopped-
likelihood identity. Direct differentiation gives

```text
dL_e/de=-(T_tau+e tau)L_e,
dL_e/de|_0=-T_tau.
```

For `abs(e)<=delta`,

```text
abs(A_m dL_e/de)
 <=abs(A_m)(abs(T_tau)+delta tau)
   exp(delta abs(T_tau)+delta^2 tau/2).
```

The stopped exponential-moment hypothesis makes the right side integrable and
therefore discharges the domination requirement. Because `1<=w_m<=m`, the
random reciprocal is bounded by one and introduces neither a singularity nor
an extra derivative. It remains correlated with the path, which is handled by
retaining `A_m` intact inside the expectation.

## 4. Symmetry and the fixed point

At `e=0`, sign reversal exchanges the upper and lower arms of the symmetric
two-sided CUSUM, preserves `tau`, and maps `A_m` to `-A_m`. Hence
`E_0[A_m]=0` whenever it is integrable. The centered fresh term also has mean
zero, so `F_{rho,m}(0)=0`.

For a continuously differentiable scalar map fixing zero, the usual local
contraction argument gives attraction when `abs(F'(0))<1`; the inverse local
expansion argument gives repulsion when `abs(F'(0))>1`. Substitution of (T1)
gives the stated criteria. At magnitude one, the derivative does not control
higher-order terms, so no conclusion is claimed.

## 5. `m=1` reduction and Stage A boundary

Positive `tau` implies `w_1=1` and makes `{tau<1}` empty. Thus `A_1=Z_tau`,
`Q_1=0`, and

```text
F'_{rho,1}(0)=rho(1-E_0[Z_tau T_tau]).
```

Stage A's dwell condition is also vacuous at `m=1`, providing a valid
regression anchor. For `m>1`, Stage A changes the stopping time and is outside
this proof.

## 6. Finite-support witness

The witness has finitely many positive baseline masses. Hence `M(e)` is a
finite sum of positive finite exponentials and is strictly positive and
analytic for every real `e`. Division by `M(e)` defines positive masses that
sum algebraically to one.

Moreover,

```text
M'(0)=-sum_omega p(omega)T_tau(omega)=-E_0[T_tau]=0
```

by the frozen sign symmetry. Consequently the likelihood score is exactly
`-T_tau`, as shown in `THEOREM.md`. All functions on a finite space are
measurable and all finite-valued functions are integrable; finite sums may be
differentiated termwise. The general theorem therefore applies without any
unproved analytic obligation. The Arb layer encloses the resulting values and
inequalities using the pre-frozen exact rational construction.
