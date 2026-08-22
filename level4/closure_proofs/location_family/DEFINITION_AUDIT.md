# General location-family definition audit

## 1. Residual parameterization

Let the physical observations be `X_t=mu+epsilon_t`, where the innovations are
iid with Lebesgue density `f`.  At the beginning of a monitoring cycle the
reference error is

```text
e = R_j-mu.
```

The detector receives only residuals

```text
Z_t = X_t-R_j = epsilon_t-e.
```

Thus, if `epsilon_t` has density `f`, then under reference error `e`,

```text
f_e(z)=f(z+e).                                      (1.1)
```

The parameter changes the law of the residual path.  It does not change a
detector written solely as a function of that path.

## 2. Fixed detector/path functional

Let `tau` be an almost surely finite positive-integer-valued stopping time on
the residual coordinates.  On `{tau=n}`, let the stopped quantity be a Borel
function `H_n(z_1,...,z_n)`.  Define `H_tau=H_n` on that event.

Both `{tau=n}` and `H_n` are fixed as `e` varies.  This is the load-bearing
condition

```text
path functional fixed, law varies.
```

If `e` enters the detector recursion, threshold, or terminal functional after
residual parameterization, the likelihood term below is not the entire
derivative.  An explicit functional derivative must then be added, and the
present theorem does not apply as stated.

## 3. One-observation likelihood ratio and score

Assume locally that the translated law is absolutely continuous with respect
to the zero-error law and that `f>0` on the relevant common support.  The
one-observation likelihood ratio is

```text
r_e(z)=f(z+e)/f(z).                                 (3.1)
```

At points where `f` is differentiable,

```text
s(z) = d/de log r_e(z)|_0
     = f'(z)/f(z).                                  (3.2)
```

This `s` is the score for the ReBaseGuard error parameter `e`.  It has the
opposite sign from the conventional location score

```text
psi(z)=-f'(z)/f(z),
s(z)=-psi(z).                                       (3.3)
```

The sign follows from `Z=epsilon-e`; it is not imported from the Gaussian
formula.

## 4. Stopped likelihood ratio and score

For a deterministic prefix of length `n`, independence gives

```text
L_n(e)=prod_{t=1}^n f(Z_t+e)/f(Z_t).                (4.1)
```

On `{tau=n}`, put `L_tau(e)=L_n(e)`.  Its logarithmic derivative at zero is

```text
S_tau = sum_{t=1}^tau s(Z_t)
      = -sum_{t=1}^tau psi(Z_t).                    (4.2)
```

Under the absolute-summability hypotheses in `THEOREM.md`, event-by-event
change of measure yields

```text
E_e[H_tau]=E_0[H_tau L_tau(e)].                     (4.3)
```

No optional-stopping assertion for an unbounded likelihood martingale is
needed.

## 5. Stopped derivative

If the stopped difference quotients are dominated by one integrable random
variable, then

```text
d/de E_e[H_tau]|_0
  = E_0[H_tau S_tau]
  = -E_0[H_tau sum_{t=1}^tau psi(Z_t)].             (5.1)
```

The domination, integrability, measurability, and almost-sure finiteness
conditions are separate analytic hypotheses, not hidden under "standard
regularity conditions."

## 6. Specialization to the terminal residual

For matched reuse length `m=1`, the reused physical observation is

```text
X_tau=R_j+Z_tau.
```

Its error relative to `mu` is exactly `e+Z_tau`.  With independent centered
fresh-reference error `U` and reuse fraction `rho`, the frozen affine rule is

```text
E_next = rho(e+Z_tau)+(1-rho)U,
F_rho(e)=E_e[E_next]
        =rho(e+E_e[Z_tau]).                         (6.1)
```

Define the actual ReBaseGuard location-family stopped gain by

```text
Gamma_f
  := -E_0[Z_tau S_tau]
   =  E_0[Z_tau sum_{t=1}^tau psi(Z_t)].             (6.2)
```

Equations (5.1)--(6.2) give

```text
F'_rho(0)=rho(1+E_0[Z_tau S_tau])
         =rho(1-Gamma_f).                           (6.3)
```

Rho scaling is exact algebra and requires neither symmetry nor a numerical
gain estimate.

## 7. Stage-D estimands

For `m=1`, Stage D froze

```text
Gamma_psi^D
  =E_0[psi(Z_tau) sum_{t=1}^tau psi(Z_t)].           (7.1)
```

This is not (6.2) unless `psi(Z_tau)=Z_tau`.  The normalized quantity

```text
Gamma_psi^D/E[psi']                                 (7.2)
```

belongs to the different terminal update
`H_tau=psi(Z_tau)/E[psi']`, the first-order influence-function update for a
score-defined M-estimator.  Actual ReBaseGuard `m=1` uses `H_tau=Z_tau`.

Therefore the theorem-relevant quantity is **neither** historical candidate
for a non-Gaussian family.  The historical t3 classification remains
`AMBIGUOUS`; Track 3 does not rewrite that frozen decision.  It resolves only
which quantity belongs to the newly specified raw-observation theorem.

## 8. Symmetry, fixed points, and oddness

Symmetry is not needed for (5.1), (6.1), or (6.3).  It is needed for the
structural fixed-point statement unless centering is assumed separately.

If `f` is even and the detector/terminal pair is reflection-equivariant,

```text
tau(-z)=tau(z),
H_tau(-z)=-H_tau(z),
```

then reflection sends the `e` residual law to the `-e` law.  Hence

```text
E_{-e}[H_tau]=-E_e[H_tau],
F_rho(-e)=-F_rho(e),
F_rho(0)=0.                                          (8.1)
```

Detector reflection is required for oddness.  Evenness of `f` alone is not.
Conversely, the local derivative theorem remains valid for asymmetric
families, but zero need not be a fixed point.

## 9. Local instability assumptions

At a fixed point zero, local linear instability of the deterministic mean map
requires

```text
|F'_rho(0)|=rho|1-Gamma_f|>1.                       (9.1)
```

If `Gamma_f>1`, this is equivalent to

```text
Gamma_f>1+1/rho.                                    (9.2)
```

For full reuse, `rho=1`, (9.2) reduces to `Gamma_f>2`.  The inequality is an
additional scalar premise.  It is not part of the derivative theorem and is
not supplied by symmetry.

## 10. Gaussian reduction

For `f(z)=phi(z)`,

```text
f'(z)/f(z)=-z,
s(z)=-z,
psi(z)=z,
S_tau=-T_tau.
```

Therefore

```text
Gamma_f=E_0[Z_tau T_tau],
F'_rho(0)=rho(1-Gamma_f),
```

exactly the already closed Gaussian formula.  A failure of this reduction is
a sign or parameterization error and stops Track 3.

## 11. Irregular-support warning

For a translated uniform density, the support moves with `e`; the translated
law is not locally mutually absolutely continuous with the zero-error law.
The interior a.e. logarithmic derivative is zero, but boundary mass produces
the actual derivative.  Treating that zero as a valid score gives a false
identity.  Uniform innovations are therefore an edge diagnostic, never a
confirmation of the regular-family theorem.

