# General stopped-score derivative theorem for regular location families

## 1. Abstract theorem

Let `Q_e` be the iid law on residual paths with one-coordinate density
`f_e(z)=f(z+e)` for `|e|<delta`.  Let `tau` be a positive-integer-valued
stopping time and let `H_tau` be a real stopped functional.  Assume:

### Path-functional hypotheses

1. For every `n`, `{tau=n}` is measurable with respect to the first `n`
   residual coordinates.
2. On `{tau=n}`, `H_tau=H_n(Z_1,...,Z_n)` for a Borel `H_n`.
3. The events, functions `H_n`, detector recursion, stopping boundary, and
   tie convention do not depend on `e` in residual coordinates.

### Distributional hypotheses

4. `f` is a probability density, positive almost everywhere on a common
   support that is stable under translations in `(-delta,delta)`.
5. `f` is absolutely continuous and `f'/f` exists almost everywhere.  Put
   `s=f'/f` and assume `s` is measurable.
6. For almost every finite prefix,

   ```text
   prod f(z_t+e)/f(z_t) -> 1
   ```

   as `e->0`, and its difference quotient converges to
   `sum s(z_t)`.  A sufficient condition is positive `C1` density on all of
   `R`.

### Stopped-time and differentiation hypotheses

7. `tau<infinity` almost surely under every `Q_e` in the neighborhood.
8. With

   ```text
   L_tau(e)=prod_{t=1}^tau f(Z_t+e)/f(Z_t),
   ```

   the event-sliced change-of-measure series is absolutely summable:

   ```text
   sum_n E_0[|H_n| 1{tau=n} L_n(e)] < infinity.
   ```

9. `H_tau` is integrable under `Q_0`, and there is an integrable `G` such that
   for all sufficiently small nonzero `e`,

   ```text
   |H_tau (L_tau(e)-1)/e| <= G                     (1.1)
   ```

   almost surely.

Then, with

```text
S_tau=sum_{t=1}^tau s(Z_t),
```

the map `e -> E_e[H_tau]` is differentiable at zero and

```text
d/de E_e[H_tau]|_0 = E_0[H_tau S_tau].             (1.2)
```

This theorem is detector-agnostic only in the narrow sense that no recursion
appears after hypotheses 1--3.  It is not detector-independent: every concrete
detector must separately satisfy measurability, finiteness, and the analytic
hypotheses 7--9.

## 2. Proof

On `{tau=n}`, iid change of measure gives

```text
E_e[H_n 1{tau=n}]
  =E_0[H_n 1{tau=n} L_n(e)].                        (2.1)
```

Hypothesis 8 permits summation over `n`, so

```text
E_e[H_tau]=E_0[H_tau L_tau(e)].                     (2.2)
```

For every finite stopped record, hypotheses 5--6 and the finite product rule
give

```text
(L_tau(e)-1)/e -> S_tau.                            (2.3)
```

Subtract the `e=0` value in (2.2), divide by `e`, and apply dominated
convergence using (1.1).  The limit is

```text
E_0[H_tau S_tau],
```

which proves (1.2).  The proof uses neither reflection nor a centered score
covariance identity.

## 3. Equivalent derivative-dominator hypothesis

For a positive `C1` density define

```text
ell'(x)=f'(x)/f(x).
```

The pathwise derivative is

```text
d/de L_tau(e)
  =L_tau(e) sum_{t=1}^tau ell'(Z_t+e).              (3.1)
```

Thus hypothesis 9 may be replaced by the explicit sufficient condition that
some integrable `D` satisfies

```text
|H_tau| L_tau(e)
  sum_{t=1}^tau |ell'(Z_t+e)| <= D                 (3.2)
```

for every `|e|<=delta0`, almost surely.  The mean-value theorem then supplies
(1.1).  This formulation cleanly separates density regularity from stopped
domination.

## 4. Bounded-score sufficient condition

Suppose additionally that

```text
sup_x |f'(x)/f(x)| <= M < infinity.                 (4.1)
```

Then

```text
L_tau(e) <= exp(M|e|tau)
```

and the left side of (3.2) is at most

```text
M |H_tau| tau exp(M delta0 tau).                   (4.2)
```

Consequently a sufficient stopped-time condition is

```text
E_0[|H_tau| tau exp(M delta0 tau)] < infinity.      (4.3)
```

This is useful for the unit-variance Student-t families in the frozen
numerical protocol: their densities are positive and smooth and their scores
are bounded.  It does not remove the need to establish (4.3) for the concrete
detector.

For the two-sided CUSUM with threshold `h` and reference allowance `k`,
`|Z_t|>=h+k` forces an alarm from every live state.  A positive forcing
probability uniform over a compact error neighborhood yields a geometric tail
for `tau`.  Combined with any innovation moment of order strictly above one,
Hölder's inequality makes (4.3) finite after shrinking `delta0`.  In
particular, this supplies a direct human route for `H_tau=Z_tau` for the
Student-t families with degrees of freedom 3, 5, and 10.

Gaussian and contaminated-normal scores are unbounded but at most linear in
the tails, while those innovation families have Gaussian exponential moments.
They can instead discharge (3.2) by the same forcing-tail decomposition and a
Gaussian exponential-moment bound.  Track 3 keeps this concrete analytic step
human-proved; Lean will expose it as a hypothesis rather than call it an
end-to-end formalization.

## 5. ReBaseGuard specialization

Take `H_tau=Z_tau`.  Under the frozen convention, the parameter score and the
conventional location score are

```text
s(z)=f'(z)/f(z),
psi(z)=-f'(z)/f(z),
S_tau=-sum_{t=1}^tau psi(Z_t).
```

Define

```text
Gamma_f=E_0[Z_tau sum_{t=1}^tau psi(Z_t)]
       =-E_0[Z_tau S_tau].                          (5.1)
```

The theorem gives

```text
d/de E_e[Z_tau]|_0=-Gamma_f.                       (5.2)
```

For independent centered fresh-reference error `U` and affine reuse fraction
`rho`,

```text
F_rho(e)
 =E_e[rho(e+Z_tau)+(1-rho)U]
 =rho(e+E_e[Z_tau]),                                (5.3)
```

so

```text
F'_rho(0)=rho(1-Gamma_f).                           (5.4)
```

No `E[psi']` normalization appears because the reused reference is the raw
terminal observation, not an M-estimator influence-function update.

## 6. Symmetry theorem

Assume separately that `f` is even and that path reflection `Jz=-z` satisfies

```text
tau(Jz)=tau(z),
H_tau(Jz)=-H_tau(z).
```

The pushforward of `Q_e` by `J` is `Q_{-e}`.  Hence

```text
E_{-e}[H_tau]=-E_e[H_tau].                          (6.1)
```

For `H_tau=Z_tau`, (5.3) is odd and `F_rho(0)=0`.  Symmetry is used here, not
in the stopped-score derivative proof.  Reflection equivariance is a detector
assumption, not a property of the innovation density alone.

## 7. Local instability consequence

If zero is a fixed point and

```text
rho |1-Gamma_f|>1,                                  (7.1)
```

then zero is locally linearly repelling for the deterministic conditional-mean
map.  In the sign-reversing regime `Gamma_f>1`, condition (7.1) is

```text
Gamma_f>1+1/rho.                                    (7.2)
```

At `rho=1`, this is `Gamma_f>2`.  The scalar inequality and the fixed-point
condition are additional premises; the derivative theorem alone certifies
neither.

## 8. Gaussian specialization

For the standard Gaussian density, `s(z)=-z`, `psi(z)=z`, and
`S_tau=-T_tau`.  Therefore

```text
Gamma_f=E_0[Z_tau T_tau],
F'_rho(0)=rho(1-Gamma_f),
```

exactly reproducing the existing Gaussian theorem.

## 9. Scope boundary

The proved result is a stopped-score derivative theorem for regular
one-dimensional location families under explicit path-functional,
change-of-measure, integrability, and domination hypotheses.  It is not
distribution-free, universal, detector-independent, or an end-to-end theorem
for every location density and stopping rule.

