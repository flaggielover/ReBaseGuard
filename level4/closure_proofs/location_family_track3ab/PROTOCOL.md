# Frozen protocol — Proof Track 3A/3B

## 1. Scientific target and immutable history

This new campaign asks whether the already human-proved general
location-family stopped-score identity can be independently replicated for
unit-variance Student t3 at adequate precision and, only after a new passing
numerical gate, completed by a reusable conditional Lean spine.

It does not rescue or modify historical Track 3.  The following remain
immutable:

```text
Track 3: LOCATION-FAMILY-THEOREM-PARTIAL
historical numerical gate: FAILED
historical failed predicate: 4.605351% > 3%
historical Lean status: NOT AUTHORIZED / NOT RUN
```

Old Track-3 scientific files may receive navigation links only.  This campaign
will not add such links before its decision.  Historical status and file hashes
are mandatory integrity checks.

## 2. Execution order

The order is fixed:

```text
historical audit
  -> retained-seed variance diagnosis
  -> protocol/source freeze and hash
  -> optional pilot-only sizing (not used; see Section 8)
  -> two fresh confirmatory replications
  -> numerical gate
  -> Lean only on exact PASS
  -> axiom audit
  -> scoped decision
  -> full repository verification
  -> commit/push
```

Arb and a global Level-4 re-audit are out of scope.

## 3. Theorem and sign convention

The frozen physical convention is

```text
e = R_j - mu,
Z_t = epsilon_t - e,
f_e(z) = f(z+e).
```

The conventional location score is `psi=-f'/f`; the parameter score is
`s=f'/f=-psi`.  For actual raw-observation matched `m=1` reuse,

```text
Gamma_f = E_0[Z_tau sum_{t<=tau} psi(Z_t)],
F'_rho(0) = rho (1-Gamma_f).
```

The theorem is conditional on the fixed residual-path functional, stopped
change-of-measure, measurability, a.s. finiteness, integrability, absolute
summability, and domination hypotheses in `PROOF_OBLIGATIONS.md`.  The forensic
audit found no mathematical error, so the estimand and sign may not change
after freeze.

Historical Stage-D terminal-score-only quantities remain different from this
raw terminal-observation gain outside Gaussian specialization.

## 4. Frozen distribution and detector

Only unit-variance Student t3 is confirmatory:

```text
Y ~ StudentT(df=3),
Z = Y / sqrt(3),
Var(Z)=1,
psi(z)=4z/(1+z^2),
|psi(z)|<=2.
```

The detector is the historical raw two-sided CUSUM:

```text
C^+_0=C^-_0=0,
C^+_t=max(0,C^+_{t-1}+Z_t-0.5),
C^-_t=max(0,C^-_{t-1}-Z_t-0.5),
tau=inf{t: C^+_t>=h_A or C^-_t>=h_A},
h_A=6.337011391962933.
```

The threshold is immutable and is not recalibrated.  Route A must reproduce
the historical t3 ARL `465.891191` within 2% in each replication.

Inclusive post-update thresholding is used.  Simultaneous two-chart crossings
and exact ties are recorded; any nonzero count fails the integrity gate.

## 5. Route A — stopped-score prediction

Route A is the frozen raw nonnegative-chart implementation in
`src/rebaseguard_location_family_track3ab/route_a.py`, inherited from the
validated Track-3 algorithm and restricted to t3.

For every path it computes

```text
G = Z_tau sum_{t<=tau} psi(Z_t).
```

The ordinary batch mean estimates `Gamma_f`; the predicted derivative is
`D_A=1-Gamma_f` for `rho=1`.  Primary uncertainty is the sample standard
deviation of independent batch means divided by `sqrt(number of batches)`.
Normal 95% intervals use `mean ± 1.96 SE`.

Median, 10% trimmed batch mean, batch skew, maximum leave-one-batch influence,
path-gain extrema, and top-1% variance concentration are diagnostics only.
They cannot replace the ordinary estimator.

## 6. Route B — independent direct conditional map

Route B is the independently written signed-lower-chart implementation in
`src/rebaseguard_location_family_track3ab/route_b.py`.  It imports no Route-A
code and contains no score or stopped-gain estimator.

For each physical stream and every frozen `e` on the same stream, Route B uses

```text
residual_t(e)=epsilon_t-e,
F(e)=e+E_e[Z_tau],
D_B(h)=[F(h)-F(-h)]/(2h).
```

The error order and geometric ladder are immutable:

```text
errors=(-0.05,+0.05,-0.025,+0.025,-0.0125,+0.0125),
h ladder=(0.05,0.025,0.0125),
primary h=0.0125.
```

Every batch derivative is formed directly from its paired `+h/-h` paths.
Primary uncertainty is the distribution of those paired batch derivatives.
Separate `+h` and `-h` SEs are never combined as if independent.  The complete
ladder, covariance, and CRN correlation are diagnostics; the finest frozen
step alone controls the primary gate.  Observed order and Richardson, if later
reported, remain secondary and cannot rescue or fail a primary result.

## 7. Fresh seed design and checkpointing

The new master seed is

```text
2026082317
```

It is disjoint from historical Track 3 (`2026082307`).  Seed keys are

```text
Route A: [2026082317,10,replication,batch]
Route B: [2026082317,20,replication,batch]
```

with one-based replication indices and zero-based batch indices.  Every key is
pairwise distinct.  Replications share no seed family; routes share no seed
family.

Each completed batch is atomically checkpointed under `results/checkpoints/`.
Checkpoints contain batch summaries, seed keys, counts, hashes, variance
diagnostics, ties, and timings, but no raw path dumps.  A rerun validates and
skips existing checkpoints.

## 8. Variance-aware sizing decision

No fresh pilot is used.  The exact replay of already-existing historical seeds
in `VARIANCE_DIAGNOSIS.md` supplies the pre-outcome variance estimates:

```text
historical Route-A path SD = 290.7695853130,
historical Route-B primary path SD upper estimate = 98.8310787880,
frozen derivative scale = 7.6337631328.
```

The frozen precision requirement is that the predicted standard error of the
per-replication Route-A/Route-B discrepancy, divided by the historical
derivative scale, be at most 1%.  This rule depends only on pre-existing data,
not on a new point estimate and not on proximity to 3%.

The fixed confirmatory design is, independently for each of two replications:

```text
batches per route = 192,
Route-A paths per batch = 200,000,
Route-A total paths = 38,400,000,
Route-B paired streams per batch = 25,000,
Route-B total paired streams = 4,800,000.
```

The historical plug-in calculation is

```text
SE_A = 290.7695853130/sqrt(38,400,000) = 0.0469227401,
SE_B = 98.8310787880/sqrt(4,800,000)  = 0.0451100094,
combined relative SE = 0.8526542% <= 1%.
```

The sample size is final.  There is no rung climbing, resizing, seed
replacement, threshold retuning, primary-step replacement, or tolerance
change after confirmatory outcomes.

## 9. Two confirmatory replications

There are exactly two mandatory independent replications.  Each uses the same
frozen distribution, threshold, batches, per-route sample sizes, estimators,
h ladder, primary step, uncertainty calculation, and gates.  Each is reported
before pooling.  A failing replication may not be hidden by a pooled result.

## 10. Primary numerical gate

The symmetric relative difference is

```text
rel(x,y)=|x-y| / ((|x|+|y|)/2).
```

The historical 3% threshold is retained unchanged.  Every primary comparison
requires both

```text
rel(x,y) <= 0.03,
|x-y|/sqrt(SE_x^2+SE_y^2) <= 3.
```

All of the following are mandatory:

1. replication 1 Route A versus Route B passes both limits;
2. replication 2 Route A versus Route B passes both limits;
3. Route-A replication 1 versus replication 2 passes both limits;
4. Route-B replication 1 versus replication 2 passes both limits;
5. pooled Route A versus pooled Route B passes both limits;
6. Route-A ARL is within 2% of the immutable historical value in each
   replication;
7. exact t3 score, bounded-score, Gaussian specialization, h-ladder, threshold,
   seed-disjointness, and source-separation checks pass;
8. every stored score/map batch identity recomputes within the frozen numeric
   tolerance;
9. CRN alignment uses one physical stream across all six error conditions; and
10. all exact tie and simultaneous-crossing counts are zero.

The Gaussian control is structural in this t3-only campaign: the exact
identity `psi(z)=z` for a standard Gaussian and the immutable successful
historical Gaussian numerical cell are hash-checked.  No new stochastic
Gaussian outcome is generated.

The decision is exactly one of:

```text
T3A-NUMERICAL-PASS
T3A-NUMERICAL-PARTIAL
T3A-NUMERICAL-FAILED
```

`PASS` requires every mandatory gate.  `PARTIAL` means all implementation and
integrity checks passed but at least one primary statistical comparison
failed.  `FAILED` means an integrity, source, seed, CRN, threshold, batch
identity, ARL, or tie guard failed.  Both non-PASS states stop before Lean.

Only exact PASS permits the literal statement:

```text
NUMERICAL GATE CLOSED — LEAN AUTHORIZED
```

## 11. Conditional Lean spine

If and only if authorized, Track 3B will add declarations for:

1. an abstract stopped-score expectation derivative bridge under an explicit
   hypothesis;
2. parameter-score/conventional-score stopped-sum algebra;
3. exact rho scaling and `F'_rho(0)=rho(1-Gamma_f)`;
4. reflection and oddness under explicit equivariance assumptions;
5. Gaussian score specialization;
6. `Gamma_f>1+1/rho`, `rho>0` implies derivative `<-1`;
7. the `rho=1`, `Gamma_f>2` specialization; and
8. an algebraic distinction between raw-terminal and terminal-score gains
   outside Gaussian equality.

The Lean theorem is a conditional formal proof spine over explicit analytic
hypotheses.  Concrete t3 measurability, a.s. finiteness, integrability, stopped
change of measure, tail, and domination obligations remain human-proved unless
actually instantiated.

Every declaration must compile in the pinned repository environment.  The
axiom audit permits only standard Mathlib foundations such as `propext`,
`Classical.choice`, and `Quot.sound`.  Any `sorry`, `admit`, or project-specific
load-bearing axiom blocks closure.

## 12. Scoped final decision

The campaign ends with exactly one:

```text
LOCATION-FAMILY-TRACK3AB-CLOSED
LOCATION-FAMILY-TRACK3AB-PARTIAL
LOCATION-FAMILY-TRACK3AB-FAILED
```

`CLOSED` requires the new numerical PASS, two passing independent
replications, implementation separation, conditional Lean compilation, clean
axiom audit, complete reproduction, historical immutability, and final
authoritative repository verification.  A clean numerical PASS with an
incomplete Lean/audit/reproducer yields `PARTIAL`; an integrity corruption
yields `FAILED`.  A statistically partial new replication leaves this scoped
campaign `PARTIAL` and keeps Lean unauthorized.

If CLOSED, the Stage-F requirement `general location-family theorem` becomes
`CLOSED` through a later independently frozen variance-aware replication and
Lean completion.  Historical Track 3 itself remains
`LOCATION-FAMILY-THEOREM-PARTIAL` forever.

No global Level-4 decision is made here.
