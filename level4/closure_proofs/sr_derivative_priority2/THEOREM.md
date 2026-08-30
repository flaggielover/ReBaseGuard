# Priority-2 theorem: ordinary-window Shiryaev--Roberts derivative

## 1. Probability law, parameter, and state map

Let `Omega=R^N` with its product Borel sigma-field and canonical coordinates
`Z_t`. For `e` in a neighborhood of zero, `Q_e` is the product law under which
the coordinates are iid `N(-e,1)`. Semantically, `e=R_j-mu` is the current
reference error and `Z_t=X_t-R_j=epsilon_t-e`. The detector is a fixed path
functional; `e` changes the law, not the recurrence.

Let `F_n=sigma(Z_1,...,Z_n)` and

```text
F_tau={B : B intersect {tau<=n} is in F_n for every n}.
```

Fix `A>1`, reset `R_0^+=R_0^-=0`, and define

```text
R_t^+ = (1+R_{t-1}^+) exp(Z_t-1/2),
R_t^- = (1+R_{t-1}^-) exp(-Z_t-1/2),
tau = inf{t>=1:max(R_t^+,R_t^-)>=A}.
```

Both charts update before the inclusive alarm comparison. The alarm-causing
increment is included. There is no head-start. The authoritative repository
instance has `A=520.886133602749` in natural units.

For a positive integer `m`, put

```text
w_m=min(m,tau),
A_m=(1/w_m) sum_{r=0}^{w_m-1} Z_{tau-r},
T_tau=sum_{t=1}^tau Z_t,
GammaTilde_m^SR=E_0[A_m T_tau].
```

Let `U` be an independent centered fresh-reference error. The next physical
reference error is

```text
E_next=rho(e+A_m)+(1-rho)U.
```

Thus the state-to-state conditional-mean map is

```text
F_{rho,m}(e)=E_e[E_next]=rho(e+E_e[A_m]).
```

## 2. Concrete Gaussian SR theorem

For every fixed `A>1`, positive integer `m`, and real `rho`, the reset
symmetric two-chart Gaussian SR process above satisfies, on some neighborhood
of zero:

1. `tau` is positive and finite almost surely, with a uniform geometric tail;
2. `tau`, `A_m`, and `T_tau` are stopped measurable;
3. `A_m` and `A_m T_tau` are integrable under `Q_0`;
4. the stopped likelihood on `F_tau` is
   `L_e=exp(-e T_tau-e^2 tau/2)` and its score at zero is `-T_tau`;
5. the likelihood derivative multiplied by `A_m` has an integrable local
   uniform dominator; and
6. sign reflection exchanges the charts, preserves `tau`, and negates both
   `A_m` and `T_tau`.

Consequently `F_{rho,m}` is differentiable at zero, zero is a fixed point, and

```text
F'_{rho,m}(0)=rho(1-GammaTilde_m^SR).
```

The derivative sign is fixed by `Z_t~N(-e,1)`. In particular,

```text
d/de E_e[A_m] at zero = -E_0[A_m T_tau].
```

## 3. Abstract theorem consumed by the proof spine

The same identity holds for any positive almost-surely finite stopped process
for which `A_m,T_tau` are stopped measurable, `A_m` and `A_mT_tau` are
integrable, `dL_e/de|_0=-T_tau`, and differentiation is justified by an
integrable local dominator. The concrete SR statements above independently
discharge these assumptions; they are not inferred from CUSUM.

## 4. Local dynamical consequence

For the deterministic iteration of the conditional-mean map:

- `|rho(1-GammaTilde_m^SR)|<1` implies local linear attraction;
- `|rho(1-GammaTilde_m^SR)|>1` implies local linear repulsion; and
- equality to one is inconclusive from first-order linearization alone.

This is a local deterministic-map statement, not an operational stochastic
stability theorem.
