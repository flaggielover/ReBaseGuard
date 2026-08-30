# General Stage-D truncated-window derivative theorem

## 1. Semantics and probability model

Let `(Omega,F,(F_t)_{t>=0})` carry one reset monitoring cycle. The scalar

```text
e = R - mu
```

is the entering reference error: active reference `R` minus the in-control
process location `mu`. Under `P_e`, the reference-centered Gaussian
innovations are `Z_t=X_t-R` with law `N(-e,1)` in the frozen specialization.

The detector is updated using `Z_t`; after that update an inclusive threshold
test is made. Let

```text
tau=inf{t>=1: alarm after the update at t}
```

and let

```text
F_tau={B in F: B intersect {tau<=t} is in F_t for every t>=1}
```

be the stopped sigma-field. Expectations `E_e` are taken under the stopped-
path law `P_e` restricted to `F_tau`.

For a fixed positive integer `m`, define

```text
w_m=min(m,tau),
T_tau=sum_{t=1}^tau Z_t,
A_m=(1/w_m) sum_{r=0}^{w_m-1} Z_{tau-r}.
```

The terminal alarm-causing increment is included. The next reference combines
the reused raw reference `R+A_m` with an independent centered fresh reference.
Consequently the conditional mean next-state error is

```text
F_{rho,m}(e)=rho(e+E_e[A_m]).
```

This is a state-to-state mean map, not a sample-path update and not Stage A's
minimum-dwell map.

## 2. Abstract score-at-zero theorem

Fix `m>=1` and real `rho`. Suppose:

1. `tau` is a positive, finite stopping time almost surely;
2. `A_m` and `T_tau` are `F_tau`-measurable;
3. for `e` in an open interval `(-delta,delta)`, `P_e|F_tau` is absolutely
   continuous with respect to `P_0|F_tau`, with likelihood `L_e`;
4. `L_0=1` and `dL_e/de|_0=-T_tau` almost surely;
5. `A_m` and `A_m T_tau` are integrable under `P_0`;
6. `e -> A_m L_e` is almost surely differentiable on that interval and there
   is an integrable `G` such that
   `abs(A_m dL_e/de)<=G` for every `abs(e)<=delta` almost surely;
7. the fresh-reference contribution is independent of the stopped cycle,
   centered for all local `e`, and enters affinely with coefficient `1-rho`.

Define

```text
GammaTilde_m=E_0[A_m T_tau].
```

Then `F_{rho,m}` is differentiable at zero and

```text
F'_{rho,m}(0)=rho(1-GammaTilde_m).                 (T1)
```

If sign-reversal symmetry makes `E_0[A_m]=0`, the origin is a fixed point. For
a continuously differentiable scalar map near zero, it is locally attracting
when

```text
abs(rho(1-GammaTilde_m))<1,
```

and locally repelling when the magnitude exceeds one. Equality gives no
conclusion from linearization alone.

## 3. Frozen Gaussian CUSUM specialization

For iid `X_t~N(mu,1)` and `Z_t=X_t-R`, the stopped likelihood relative to
`e=0` is

```text
L_e=exp(-e T_tau-e^2 tau/2).                       (T2)
```

Its derivative at zero is `-T_tau`. Thus (T1) applies to the ordinary frozen
two-sided CUSUM with `k=1/2`, inclusive threshold `h=5`, reset state, and exact
Stage-D truncated window, provided the stated stopped measurability,
integrability, and local-domination hypotheses hold. A sufficient concrete
condition is a stopped exponential moment strong enough to dominate

```text
abs(A_m)(abs(T_tau)+delta tau)
  exp(delta abs(T_tau)+delta^2 tau/2).
```

The human proof records this sufficient condition. The Lean theorem consumes
the corresponding abstract assumptions; it does not prove this concrete
Gaussian-CUSUM exponential-moment assertion.

## 4. Exact random-denominator decomposition

Define

```text
B_m=(1/m) sum_{r=0}^{min(m,tau)-1} Z_{tau-r},
Q_m=1{tau<m}(1/tau-1/m)T_tau^2.
```

Then pathwise

```text
A_m T_tau=B_m T_tau+Q_m,                            (T3)
Q_m>=0,
```

and, when the terms are integrable,

```text
GammaTilde_m=E_0[B_m T_tau]+E_0[Q_m].               (T4)
```

At `m=1`, `tau<1` is empty, `Q_1=0`, and (T1) reduces to the previously closed
terminal-observation theorem.

## 5. Exact finite-support instantiation

The witness in `certificates/WITNESS.json` has positive rational baseline
weights `p(omega)`, symmetric `T_tau`, and `E_0[T_tau]=0`. Define

```text
M(e)=sum_omega p(omega) exp(-e T_tau(omega)),
P_e(omega)=p(omega) exp(-e T_tau(omega))/M(e).
```

Every term is positive and the finite sum `M(e)` is finite and strictly
positive for every real `e`. Hence `P_e` is a probability law on every
neighborhood of zero, analytically—not merely by numerical normalization.
Finite differentiation gives

```text
d/de log P_e(omega)|_0
  =-T_tau(omega)-M'(0)/M(0)
  =-T_tau(omega)+E_0[T_tau]
  =-T_tau(omega).
```

All domination and interchange requirements are automatic on the finite
space. Therefore the witness is an exact instance of (T1), though not of the
Gaussian likelihood formula (T2). Arb rigorously certifies its numerical
inequalities. Those intervals make no claim about frozen Gaussian CUSUM
`GammaTilde_m` values for `m>1`.
