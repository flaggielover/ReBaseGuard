# Reconfirmed location-family stopped-score theorem

## Convention and estimand

Track 3A/3B retains the historical convention

```text
e = R_j - mu,
Z_t = epsilon_t - e,
f_e(z) = f(z + e).
```

For a positive differentiable density on locally common support, the
parameter score and conventional location score are

```text
s(z)   = d/de log f(z+e)|_0 = f'(z)/f(z),
psi(z) = -f'(z)/f(z),
s(z)   = -psi(z).
```

For a fixed residual-path stopping/terminal functional,

```text
S_tau = sum_{t<=tau} s(Z_t)
      = -sum_{t<=tau} psi(Z_t).
```

Under the explicit stopped change-of-measure, measurability, a.s. finiteness,
integrability, and domination hypotheses recorded in `PROOF_OBLIGATIONS.md`,

```text
d/de E_e[H_tau]|_0 = E_0[H_tau S_tau].
```

For actual matched raw-observation `m=1` reuse, `H_tau=Z_tau`.  Define

```text
Gamma_f = E_0[Z_tau sum_{t<=tau} psi(Z_t)]
        = -E_0[Z_tau S_tau].
```

Then

```text
d/de E_e[Z_tau]|_0 = -Gamma_f,
F_rho(e) = rho (e + E_e[Z_tau]),
F'_rho(0) = rho (1 - Gamma_f).
```

The forensic audit found no mathematical error in this theorem.  Track 3A
therefore replicates it rather than changing its estimand or sign.

## Reconfirmed structural consequences

- Rho scaling is exact algebra and does not require symmetry.
- If the base density is even, the detector is reflection-equivariant, and
  the terminal functional is odd, then `F_rho` is odd and zero is a fixed
  point.
- If zero is a fixed point, local linear repulsion requires
  `rho * |1-Gamma_f| > 1`.
- For `rho > 0` and `Gamma_f > 1`, the sufficient sign-reversing condition is
  `Gamma_f > 1 + 1/rho`.
- At `rho=1`, `Gamma_f > 2` implies `F'_1(0) < -1`.

## Gaussian reduction

For the standard Gaussian density,

```text
s(z)=-z,  psi(z)=z,  S_tau=-T_tau,
Gamma_f=E_0[Z_tau T_tau].
```

The theorem reduces exactly to the already-closed Gaussian identity

```text
F'_rho(0)=rho(1-E_0[Z_tau T_tau]).
```

## Historical Stage-D estimands

The theorem-relevant raw-reuse gain uses terminal functional `Z_tau`.  Stage
D's non-Gaussian quantities used terminal functional `psi(Z_tau)`, with or
without `E[psi']` normalization.  Outside Gaussian simplification, neither is
the raw-reuse `Gamma_f`.  Stage-D t3 remains historically `AMBIGUOUS`.

## Scope

This is a conditional regular-location-family theorem.  It is not
distribution-free, universal, detector-independent, or valid for moving
support without additional boundary terms.  The translated-uniform negative
control from Track 3 remains excluded.
