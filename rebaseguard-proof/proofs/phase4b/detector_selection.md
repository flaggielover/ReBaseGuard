# Phase-4B Detector Selection Memo

**Status:** Approved detector design; implementation pending written-spec review  
**Date:** 2026-08-19  
**Selected detector:** symmetric two-chart Shiryaev-Roberts  
**Frozen design shift:** `delta=1`

## 1. Research boundary

Phase-4B tests whether the detector-independent stopped-score identity produces
a second instability witness for a sequential detector structurally distinct
from the protected two-sided Gaussian CUSUM.

This phase is diagnostic only. It stops after the scalar oracle, ARL
calibration, stopped-score estimate, exact mixed-reuse analysis, modest
multi-cycle sanity check, and witness report. It does not construct a rigorous
second-detector certificate.

The protected CUSUM certificate, historical finite cross-check, corrected
Phase-4A diagnostics, hashes, and theorem are read-only.

## 2. Candidate comparison

| Candidate | Independence | Centering | ARL/MC feasibility | Certification feasibility | Decision |
|---|---|---|---|---|---|
| Symmetric two-chart SR | High: sums likelihood products rather than maximizing reflected log likelihood | Exact reflection | High | Moderate; 2D nonlinear operator | **Selected** |
| Two-sided EWMA | High: linear exponential filter | Exact reflection | Very high | High; 1D operator | Backup if SR is YELLOW |
| Two-sided Shewhart | Very high but memoryless | Exact reflection | Analytic | Essentially analytic | Rejected as scientifically too degenerate for the primary witness |
| Window-limited two-sided GLR | High, but retains changepoint maximization | Exact reflection | Moderate | Low; window-dimensional nonsmooth state | Rejected for this gate |

The one-sided SR rule is not selected because it provides no symmetry argument
ensuring that zero is a reference fixed point. Running positive and negative SR
charts in parallel resolves the centering issue without altering the natural
reuse statistic.

## 3. Exact detector definition

Fix `delta=1` before all calibration and witness computation. For residual
innovations `Z_t`, define

```text
Lambda_t^+ = exp(delta Z_t-delta^2/2),
Lambda_t^- = exp(-delta Z_t-delta^2/2),

R_t^+ = (1+R_(t-1)^+) Lambda_t^+,
R_t^- = (1+R_(t-1)^-) Lambda_t^-,
R_0^+ = R_0^- = 0.
```

For threshold `A>0`,

```text
tau_D = inf{t>=1: max(R_t^+,R_t^-)>=A}.
```

The detector updates both arms using the same `Z_t` and checks the inclusive
alarm boundary after the update. If both arms cross, direction is assigned to
the larger post-update statistic; exact equality is recorded as a symmetric
tie. The detector state resets to `(0,0)` at each new cycle.

The computational representation is

```text
Y^+ = log(1+R^+),
Y^- = log(1+R^-),
```

with softplus updates, to avoid overflow without changing the mathematical
rule.

## 4. Reference parameterization and centering

Let the current reference error be `e`. Under the physical in-control model,

```text
Z_t = X_t-e,  X_t iid N(0,1),
```

so under `Q_e`, `Z_t iid N(-e,1)`. The detector parameters `delta` and `A`
remain fixed as `e` varies, making `tau_D` a parameter-invariant stopping-time
functional.

For full `m=1` reuse,

```text
F_D,1(e)=e+E_e[Z_(tau_D)].
```

Reflection `Z -> -Z` swaps the two SR arms, preserves `tau_D`, and negates the
terminal observation. Hence `E_0[Z_(tau_D)]=0` and `F_D,1(0)=0`.

## 5. Stopped-score functional

Let

```text
T_(tau_D)=sum_(t<=tau_D) Z_t,
Gamma_D=Cov_0(Z_(tau_D),T_(tau_D)).
```

Optional stopping gives `E_0[T_(tau_D)]=0`; reflection gives
`E_0[Z_(tau_D)]=0`. Therefore

```text
Gamma_D=E_0[Z_(tau_D) T_(tau_D)].
```

The stopped Gaussian likelihood ratio is

```text
M_(tau_D)(e)=exp(-e T_(tau_D)-e^2 tau_D/2).
```

The Phase-4A identity therefore gives exactly

```text
F_D,1'(0)=1-Gamma_D.
```

The stopping time has a geometric tail: from every live state, sufficiently
large positive or negative `Z_t` forces an alarm in one step. This supplies the
integrability required by the stopped-score differentiation.

## 6. Precommitted witness interpretation

These categories are frozen before any `Gamma_D` result is observed:

| Diagnostic result | Interpretation |
|---|---|
| `Gamma_D>5` | Strong instability witness; GREEN-A candidate |
| Clearly `Gamma_D>2` but `Gamma_D<=5` | Nontrivial witness; GREEN-B candidate |
| Near `Gamma_D=2` | Near-critical; do not immediately certify |
| `Gamma_D<2` | No instability witness for this detector/configuration |

Monte Carlo confidence intervals, not point estimates alone, determine whether
a value is “clearly” above two. A result whose uncertainty overlaps the
boundary is near-critical or unresolved.

Neither `delta` nor `A` may be tuned using `Gamma_D`.

## 7. ARL calibration

`delta=1` remains frozen. Only `A` is calibrated, solely against the in-control
target

```text
ARL_0 approximately 465.
```

Calibration uses a dedicated deterministic seed, common random numbers, and a
bracketing/bisection procedure. Every attempted threshold is recorded in
`proofs/phase4b/arl_calibration.json`, including:

- threshold `A`;
- sample size and seed;
- estimated ARL and uncertainty;
- runtime;
- bracketing decision; and
- whether the attempt was pilot, refinement, or final validation.

The selected threshold is independently validated, with sensitivity results
near `0.95A`, `A`, and `1.05A`. Exact equality with 465 is unnecessary.

## 8. Pathwise and Monte Carlo validation

Implementation order is mandatory:

1. scalar log-domain SR oracle;
2. separately structured deterministic path replay;
3. exact fixed-path agreement tests;
4. vectorized Monte Carlo implementation.

Tests cover the initial state, exact/epsilon threshold crossing, large
overshoot, reflection, simultaneous-arm crossing, tie handling, and terminal
reward `Z_tau*T_tau`.

The final stopped-score diagnostic uses precommitted independent seeds `1729`
and `20260818`, initially one million paths per seed. Sampling increases only
when necessary to classify a precommitted regime. Reported quantities include
ARL, `E[T_tau^2]` versus `E[tau]`, terminal means, arm symmetry, `Gamma_D`, its
SE/interval, and `F_D,1'(0)`.

## 9. Protected CUSUM positive control

The protected CUSUM is run once through the same new diagnostic harness as a
positive-control convention check. It must use the frozen configuration
`k=0.5`, `h=5`, `m=1` and must reproduce the known ARL/Gamma scale without
regenerating or modifying any proof artifact.

This control validates common result aggregation, reward indexing, standard
errors, seeds, and reporting conventions. It is diagnostic only and is not a
new proof replay.

## 10. Mixed reuse

For the unchanged affine mixture with an independent mean-zero fresh
component,

```text
F_D,rho'(0)=rho F_D,1'(0)
```

holds exactly. If the diagnostic interval establishes `|F_D,1'(0)|>1`, report

```text
rho_c,D=1/|F_D,1'(0)|=1/(Gamma_D-1)
```

with uncertainty propagated from `Gamma_D`. The scaling identity is analytical;
the constant is diagnostic.

## 11. Multi-cycle sanity check

Only after the local diagnostic, run a modest comparison of:

- fresh post-alarm reference;
- full stopping-selected reuse; and
- if a critical fraction exists, one precommitted `rho` below and one above
  the estimated threshold.

Track reference error, lag-one cycle correlation, alarm direction, reference
distribution, cycle length/ARL, mean error, and dispersion. No period-two or
bimodality result is required or presumed.

## 12. Later certification architecture

For log-state `y=(Y^+,Y^-)`, continuation is

```text
ell(y)<z<u(y),
ell=(Y^- - log(A)-delta^2/2)/delta,
u=(log(A)-Y^+ +delta^2/2)/delta.
```

The affine reduction remains

```text
H(y,x)=a(y)x+b(y),
a=Ka+r_a,
b=Kb+K_z a+r_b.
```

A later proof would be a two-dimensional nonlinear continuum certificate using
Arb bounds for Gaussian tails, exponentials, logarithms, and softplus
transitions. A certified block-survival bound must precede residual propagation.
Main risks are interval wrapping and an unusably loose resolvent bound.

No rigorous certification begins during this diagnostic gate.

## 13. Failure modes and honest outcomes

Possible outcomes include `Gamma_D<2`, a near-critical interval, high reward
variance, ARL sensitivity, convention problems at simultaneous crossings, no
visible multi-cycle feedback, or a diagnostic witness whose nonlinear operator
is impractical to certify. These are reportable scientific outcomes.

If SR yields YELLOW, two-sided EWMA is the next candidate. Parameters, seeds,
and failed settings will not be hidden.

## 14. Why the detector is genuinely distinct

In likelihood-ratio scale, CUSUM retains a maximum over candidate changepoints,
while SR sums their likelihood products:

```text
CUSUM: max_k product_(i=k)^n Lambda_i,
SR:    sum_k product_(i=k)^n Lambda_i.
```

No path-independent monotone transformation converts this maximum to the sum.
The shared `delta=1` increment creates a fair design-shift comparison, not an
equivalent recursion. A positive result would be genuine cross-detector
evidence, but would not justify a universal-instability claim.

## 15. Required outputs and stop gate

The diagnostic phase produces isolated `proofs/phase4b/` artifacts and source
modules under a Phase-4B namespace. Machine-readable files record every
configuration, environment, package version, seed, sample size, runtime, and
hash.

The phase ends with `proofs/phase4b/phase4b_witness_report.md` and a
recommendation about rigorous certification. Work stops before certification
for user review.
