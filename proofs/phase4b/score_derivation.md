# Symmetric-SR Stopped-Score and Mixed-Reuse Derivation

Let `Q_e` denote the law under which the residuals are iid `N(-e,1)`. The
frozen SR rule is the same measurable functional of the residual path for every
`e`. Relative to `Q_0`, the likelihood ratio through a deterministic time `n`
is

```text
M_n(e) = exp(-e T_n - e^2 n/2),   T_n=sum_(t<=n) Z_t.
```

Stopping at `tau_D` gives the same expression with `n=tau_D`. The SR stopping
time has a geometric tail: from any live state, either
`Z_t >= log(A)+1/2` or `Z_t <= -log(A)-1/2` forces an alarm in one step, and
this event has a fixed positive Gaussian probability. Consequently the moment
conditions used by the already audited Gaussian stopped-score theorem apply.

For full `m=1` reuse,

```text
F_D,1(e) = e + E_e[Z_(tau_D)].
```

Differentiating at zero in residual coordinates yields

```text
F_D,1'(0)
  = 1 + E_0[Z_(tau_D) * (-T_(tau_D))]
  = 1 - Gamma_D,

Gamma_D = Cov_0(Z_(tau_D),T_(tau_D)).
```

Reflection of the residual path swaps the two SR charts while preserving
`tau_D`, and negates both `Z_tau` and `T_tau`. Hence
`E_0[Z_tau]=0`. Optional stopping gives `E_0[T_tau]=0`, so the covariance is
the raw product used by the diagnostic:

```text
Gamma_D = E_0[Z_(tau_D) T_(tau_D)].
```

For an independent mean-zero fresh reference,

```text
F_D,rho(e)
  = E_e[rho(e+Z_tau)+(1-rho)X_fresh]
  = rho F_D,1(e),

F_D,rho'(0) = rho(1-Gamma_D).
```

This scaling is exact and detector-independent under the stated independence
and centering assumptions. It does not depend on CUSUM structure. When
`Gamma_D>2`, the local critical fraction is

```text
rho_c,D = 1/(Gamma_D-1).
```

The two-million-path SR diagnostic gives `Gamma_D=17.2720847004` with Monte
Carlo SE `0.0280269524`; therefore the non-rigorous point estimate is
`rho_c,D=0.06145494068`, with transformed 95% diagnostic interval
`[0.06124817715, 0.06166310494]`.

The identity in this note is analytical. The numerical value of `Gamma_D` and
the resulting numerical critical fraction remain Monte Carlo diagnostics, not
certified bounds.
