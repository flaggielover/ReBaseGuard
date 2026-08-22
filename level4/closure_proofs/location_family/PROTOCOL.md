# Frozen protocol — Proof Track 3

**Campaign:** general location-family stopped-score derivative theorem  
**Freeze date:** 2026-08-23  
**Confirmatory Track-3 outcomes generated before this text:** none  
**Historical results:** immutable

## 1. Closure target

The target is a general stopped-score derivative theorem for a specified class
of regular one-dimensional location families under explicit stopping-time
differentiation hypotheses, plus its actual `m=1` ReBaseGuard specialization.

The target is not distribution-free ReBaseGuard, detector independence, a
general robustness theorem, an instability certificate for every family, or a
global Level-4 re-audit.

## 2. Frozen theorem and sign convention

The physical/residual convention is

```text
e=R_j-mu,
Z_t=epsilon_t-e,
f_e(z)=f(z+e).
```

The parameter score and conventional location score are

```text
s(z)=f'(z)/f(z),
psi(z)=-f'(z)/f(z),
S_tau=sum s(Z_t)=-sum psi(Z_t).
```

Under the explicit hypotheses in `THEOREM.md`,

```text
d/de E_e[H_tau]|_0=E_0[H_tau S_tau].
```

For actual raw-observation `m=1` reuse, freeze

```text
Gamma_f=E_0[Z_tau sum_{t<=tau} psi(Z_t)],
F'_rho(0)=rho(1-Gamma_f).
```

The Gaussian reduction must be exactly
`Gamma_f=E[Z_tau T_tau]`.  Any sign or reduction failure stops the track.

## 3. Frozen detector

Every regular-family numerical cell uses the same two-sided CUSUM form:

```text
C_0^+=C_0^-=0,
C_t^+=max(0,C_{t-1}^+ + Z_t - 1/2),
C_t^-=max(0,C_{t-1}^- - Z_t - 1/2),
tau=inf{t>=1:max(C_t^+,C_t^-)>=h_f}.
```

Both charts update before an inclusive alarm test.  The terminal residual and
terminal score are included.  There is no minimum dwell.  Exact simultaneous
crossings are recorded; the implementation classifies them as ties and never
silently assigns a direction.

The family-specific thresholds are copied exactly from the frozen Stage-D D3
operating points and are never recalibrated in Track 3:

| family | `h_f` |
|---|---:|
| Gaussian | 5.0 |
| unit-variance t10 | 5.234517732360302 |
| unit-variance t5 | 5.669498491821448 |
| unit-variance t3 | 6.337011391962933 |
| 5% `N(0,3^2)` contamination | 7.671712168173407 |
| 10% `N(0,3^2)` contamination | 9.381983052368211 |

The Stage-D measured ARLs are historical comparators only.  No Track-3
threshold may be substituted into Stage D.

## 4. Frozen regular families

The confirmatory regular grid is:

1. standard Gaussian control;
2. Student-t with `nu=10`, rescaled to variance one;
3. Student-t with `nu=5`, rescaled to variance one;
4. Student-t with `nu=3`, rescaled to variance one;
5. `(0.95)N(0,1)+(0.05)N(0,3^2)`; and
6. `(0.90)N(0,1)+(0.10)N(0,3^2)`.

All are symmetric, positive, smooth densities.  The t3 cell is the mandatory
discriminator because Stage D's two historical candidate estimands lie on
opposite sides of 2 there.

## 5. Irregular edge diagnostic

The centered variance-one uniform family is frozen as an analytic negative
control with deterministic `tau=1`, `H=Z_1`.  Its translated support moves.
The interior a.e. log-density derivative is zero, which would falsely predict
`dE_e[Z_1]/de=0`; the actual derivative is `-1`.

This diagnostic is required to demonstrate the common-support/absolute-
continuity assumption.  It is not a theorem confirmation and does not control
the regular-family numerical verdict unless the implementation fails to
reproduce the exact mismatch.

## 6. Fresh seeds

The master seed is `2026082307`, verified absent from the repository at freeze.
NumPy `SeedSequence` with PCG64 uses disjoint keys:

- Route A: `[2026082307,1,family_index,batch]`;
- Route B replication 1: `[2026082307,2,family_index,batch]`;
- Route B replication 2: `[2026082307,3,family_index,batch]`; and
- structural diagnostics: route component at least 90.

No stream is shared with Stage D or Proof Tracks 1--2.

## 7. Frozen sample sizes

For every regular family:

- Route A: 48 independent batches of 10,000 paths (`480,000` total);
- Route B replication 1: 48 independent batches of 5,000 paired path streams;
- Route B replication 2: the same size on disjoint seeds; and
- each Route-B path stream is reused across every signed step in the frozen
  ladder.

The batch is the statistical unit.  No sample-size increase is allowed after
outcomes.

## 8. Route A — stopped-score prediction

Route A is an independently written raw two-chart CUSUM implementation.  At
`e=0`, each path records

```text
tau,
Z_tau,
Psi_tau=sum_{t<=tau} psi(Z_t),
G_f=Z_tau Psi_tau.
```

Per family it estimates

```text
Gamma_f=E[G_f],
d_A=1-Gamma_f.
```

The SE is the sample standard deviation of the 48 batch means divided by
`sqrt(48)`.  Route A must not compute a finite difference or import Route B.

It also records ARL, mean terminal residual, mean stopped score, chart
direction, ties, and batch summaries.  For symmetric cells the two means must
be statistically consistent with zero, but those diagnostics do not replace
the pathwise reflection test.

## 9. Route B — direct conditional-map derivative

Route B is independently written and uses a signed lower-chart representation:

```text
U_t=max(0,U_{t-1}+Z_t-1/2),
L_t=min(0,L_{t-1}+Z_t+1/2),
alarm iff U_t>=h_f or L_t<=-h_f.
```

It must not import Route A, its score formulas, or its stopped-gain estimator.
It estimates only

```text
F_1(e)=e+E_e[Z_tau].
```

The frozen geometric step ladder is

```text
h in {0.05,0.025,0.0125}.
```

For each batch and `h`, the same underlying physical innovation stream drives
the `+h` and `-h` residual paths.  The batch derivative is formed directly:

```text
D_b(h)=[F_b(h)-F_b(-h)]/(2h).
```

SE is computed from the distribution of these paired batch derivatives, not
from separate sign SEs.  The primary step is `h=0.0125`.  Observed order and
Richardson extrapolation are diagnostics only and cannot fail or rescue the
primary decision.

## 10. Structural and historical controls

Before evaluating numerical correspondence, all must pass:

1. Gaussian score reduces pointwise to `psi(z)=z`.
2. Each family score agrees with `-d/dz log f` on a frozen deterministic grid.
3. Route-A path reflection swaps charts, preserves `tau`, negates `Z_tau` and
   `Psi_tau`, and preserves their product.
4. Route-B path reflection swaps its upper/lower alarm states and negates the
   terminal residual.
5. Affine rho scaling is exact pathwise at `rho in {0,0.25,0.5,1}`.
6. Every regular-family tie count is zero.  Any observed exact tie or any
   nonzero simultaneous-crossing count is a numerical-defect stop.
7. Source guards prove that neither route imports the other and Route B
   contains no score/gain estimator.
8. The frozen protocol and historical manifest hashes match exactly.
9. Stage D/F and Proof Track 1/1A/1B/2 decisions remain unchanged.
10. At each fixed threshold, Route-A ARL must be within 2% of the corresponding
    historical Stage-D measured ARL.  This is an operating-point reproduction
    check, not recalibration.

## 11. Frozen numerical pass/fail rule

For every one of the six regular families, all primary conditions must pass:

1. Route A and pooled Route B primary derivatives have
   `|z|<=3`, using `sqrt(SE_A^2+SE_B^2)`.
2. Their absolute relative discrepancy is at most 3%, using the mean absolute
   magnitude as denominator.
3. The two independent Route-B replications agree within `|z|<=3` and 3%
   relative discrepancy.
4. Route B uses the paired-batch SE and the frozen primary step.
5. All structural, tie, source, seed, ARL, and historical-integrity controls
   pass.

The Gaussian Route-A `Gamma_f` must additionally agree with the historical
Stage-D Gaussian `Gamma_psi=15.867139929316513` within 3 combined batch SE and
2% relative discrepancy.  It must also reduce to the existing Gaussian score
formula at source and theorem level.

The t3 report must compare the new `Gamma_f` against both historical Stage-D
quantities, but neither historical quantity controls the new gate.

No family may be removed, no threshold or estimand changed, no `h` replaced,
and no `N` increased after outcomes.  A failure is preserved.

## 12. Numerical verdicts and Lean authorization

Allowed numerical statuses are:

```text
LOCATION-FAMILY-NUMERICAL-PASS
LOCATION-FAMILY-NUMERICAL-FAILED
LOCATION-FAMILY-THEOREM-PARTIAL
```

If every primary criterion passes, record exactly:

```text
NUMERICAL GATE CLOSED — LEAN AUTHORIZED
```

If a theorem/sign/Gaussian-reduction or regular-family correspondence check
fails, return `LOCATION-FAMILY-NUMERICAL-FAILED` and stop before Lean.  If the
limitation is implementation, integrability evidence, or reproducibility
rather than a contradiction of the identity, return
`LOCATION-FAMILY-THEOREM-PARTIAL` and stop before Lean.

## 13. Conditional Lean scope

Lean is authorized only by the exact pass declaration above.  If authorized,
formalize:

1. finite-product likelihood derivative/score algebra;
2. a general expectation derivative consequence under explicit hypotheses;
3. the sign conversion `s=-psi`;
4. `Gamma_f=-E[Z_tau S_tau]` and rho derivative algebra;
5. reflection/oddness under explicit involution hypotheses;
6. Gaussian score specialization; and
7. `Gamma_f>1+1/rho -> |F'_rho(0)|>1`, including `rho=1`.

The formal theorem remains conditional over analytic hypotheses.  Concrete
infinite-process measurability, almost-sure finiteness, stopped change of
measure, integrability, and domination may remain human-proved and must be
listed as such.  No `sorry`, `admit`, or project-specific axiom is allowed.
Every headline declaration receives a `#print axioms` audit; the allowlist is
`propext`, `Classical.choice`, and `Quot.sound` only.

## 14. Final Track-3 statuses

Allowed final statuses are:

```text
LOCATION-FAMILY-DERIVATIVE-CLOSED
LOCATION-FAMILY-THEOREM-PARTIAL
LOCATION-FAMILY-THEOREM-OPEN
```

`CLOSED` requires the human theorem under explicit assumptions, frozen
definition/code correspondence, all regular-family numerical gates, compiled
conditional Lean spine, transparent axiom audit, historical integrity, and
full repository verification.

`CLOSED` does not assert `Gamma_f>2` for a class, distribution-free behavior,
or concrete local instability unless the relevant scalar inequality is
separately established at the stated evidential level.

## 15. Reproducibility and stop rules

Persist batch summaries sufficient to recompute all means, SEs, paired
derivatives, and gates.  Raw paths are not committed.  The final reproducer
must verify historical and protocol hashes, replay retained numerical
decisions, compile Lean if authorized, audit axioms, run Track-3 tests, run the
authoritative repository verifier, and confirm historical decisions unchanged.

After this file is hashed, it is immutable.  Any required scientific change
creates a new protocol/version and leaves this one intact.  Routine code fixes
are allowed only before confirmatory execution and must remain consistent with
this text.  Do not begin confirmatory simulation until source and integrity
tests pass.

