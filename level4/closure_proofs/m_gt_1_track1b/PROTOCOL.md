# Frozen protocol — Proof Track 1B

**Campaign:** Correlation-Aware Decomposition Replication + Lean Completion  
**Freeze date:** 2026-08-22  
**Track 1B outcomes generated before this text:** none  
**Historical Track 1A `m=20`:** `3.130 > 3`, `FAILED`, immutable

This protocol replaces no historical gate and does not reinterpret Track 1A.

## 1. Frozen mathematical objects

Under `P_0`, residuals `Z_t` are iid standard normal. The two-sided CUSUM uses
`k=1/2`, inclusive threshold `h=5`, reset initial state, and includes the
terminal observation.

For ordinary alarm time `tau`, stopped sum `T_tau`, fixed positive integer
`m`, and `w=min(m,tau)`, define

`S_m = sum_{r=0}^{w-1} Z_{tau-r}`,

`Gdirect_m = (S_m/w) T_tau`,

`Gfixed_m = (1/m) sum_{r=0}^{m-1} 1{tau>r} Z_{tau-r} T_tau`,

`Q_m = 1{tau<m}(1/tau-1/m)T_tau^2`.

The theorem's decomposition is `Gdirect_m=Gfixed_m+Q_m` pathwise and

`GammaTilde_m=E[Gdirect_m]=E[Gfixed_m]+C_m`, where `C_m=E[Q_m]`.

## 2. Grid and fresh seeds

The confirmatory grid is `m={1,2,5,10,20,50}`. Master seed `2026082219` is
absent from every repository science run at freeze.

All streams use NumPy `SeedSequence` and PCG64:

- paired Route P: `[2026082219,1,batch]`;
- independent Route I direct: `[2026082219,2,batch]`;
- independent Route I reconstruction: `[2026082219,3,batch]`;
- secondary Stage A: `[2026082219,4,m_index,batch]`;
- structural controls use route identifiers at least 90.

No Track 1B stream shares a seed family with Stage D, Track 1, or Track 1A.

## 3. Batch unit and sample size

Routes P, I-direct, and I-reconstruction each use 64 independent batches of
25,000 paths: 1,600,000 stopped paths per route. Sixty-four batches exceed ten
times the six-dimensional grid size, permitting a stable empirical covariance
matrix without a pilot-selected ridge or pseudoinverse. The 25,000-path batch
mean is the statistical unit for every covariance-aware test.

The secondary Stage-A calculation uses 40 independent 25,000-path batches per
`m`, one million paths per cell. These sizes were selected before outcomes for
batch-level covariance stability and CLT precision, not to attain a desired z.
No pilot or adaptive resizing is permitted.

## 4. Implementation separation

The simulator returns only stopped primitives: `tau`, `T_tau`, and newest-
first lags.

The direct implementation must compute `Gdirect` from `w=min(m,tau)` and the
truncated suffix without importing the reconstruction implementation.

The reconstruction implementation must accumulate fixed-lag contributions
and `Q_m` directly from `tau`, `T_tau`, and lag masks without importing the
direct implementation or a shared theorem-encoding helper.

AST/source guards must enforce this separation. Both may depend on the raw
primitive data type and NumPy only.

## 5. Route P — paired primary test

For each batch and `m`, the same stopped paths feed both independent
implementations. Record batch means `X_b`, `Y_b`, and

`D_b=X_b-Y_b`.

From the 64 aligned batch pairs, compute sample variances `s_X^2`, `s_Y^2`,
sample covariance `s_XY`, and

`s_D^2=s_X^2+s_Y^2-2s_XY`.

Report the paired SE `s_D/sqrt(64)`, the naive independence SE
`sqrt((s_X^2+s_Y^2)/64)`, covariance, correlation, and their ratio.

Route P passes only if, for every `m`:

1. batch IDs, seed keys, and path counts align exactly;
2. maximum pathwise absolute discrepancy is at most `1e-10`;
3. maximum absolute batch-mean discrepancy is at most `1e-10`;
4. absolute overall paired mean discrepancy is at most `1e-12`;
5. the covariance identity for `s_D^2` agrees with the directly computed
   variance of `D_b` to absolute tolerance `1e-12` times
   `max(1,s_X^2+s_Y^2)`;
6. covariance is positive and correlation is at least `0.999999999`; and
7. every correction integrand is at least `-1e-14`.

These are algebra, alignment, and numerical-roundoff gates—not a z target.

## 6. Route I — independent implementation cross-check

Route I-direct and Route I-reconstruction use disjoint seeds and stopped
paths. Batch index only aligns two independent batch means into an iid
difference vector; it creates no CRN.

Let `D_b` be the six-dimensional vector of direct-minus-reconstruction batch
means. Estimate its sample covariance matrix `S`. With `B=64`, `p=6`, compute

`T2 = B mean(D)' S^{-1} mean(D)`

and

`F = ((B-p)/(p(B-1))) T2`, compared with `F_{p,B-p}`.

No ridge, pseudoinverse, cell dropping, or covariance retuning is allowed. The
matrix must be positive definite with condition number at most `1e12`.

Route I passes only if:

1. the global Hotelling p-value is at least `0.01`;
2. every absolute relative discrepancy is at most `0.02`, using denominator
   `(|X|+|Y|)/2`;
3. all 64 direct keys are disjoint from all 64 reconstruction keys; and
4. both implementations separately satisfy their internal pathwise
   primitive checks.

Per-cell z-values and Bonferroni intervals are retained as secondary
diagnostics only and do not drive the verdict. This is a multivariate batch-
level cross-check, not a post-hoc relaxation of Track 1A's criterion.

## 7. Short-cycle replication

Use Route I-reconstruction primitives to estimate `P(tau<m)`, `C_m`, and
`SE(C_m)` from the 64 independent batch means/counts. Wilson intervals are
reported for probabilities. Track 1A values are external comparators only and
are never pooled with Track 1B.

`m=2` may contain zero observed short cycles; this is not an implementation
failure. Correction integrands must remain nonnegative.

## 8. Stage-A / Stage-D secondary consistency check

Stage A uses `tau_m=inf{t>=m:alarm}` and a fixed full `m` window. Stage D uses
ordinary `tau` and `min(m,tau)`. Report gains, derivatives, raw differences,
batch-based SE/95% CI, standardized effects, direction, and relation to
`P(tau<m)`.

This is a secondary diagnostic with no significance threshold. The historical
Track 1A distinction `PASS` remains unchanged.

## 9. Mandatory `m=1` control

On a shared structural-control stream, Stage A and Stage D must have identical
`tau`, `T_tau`, terminal windows, and gain integrands. Route P must have
`Q_1=0` exactly. The human and Lean theorem must reduce to

`F'_{rho,1}(0)=rho(1-E[Z_tau T_tau])`.

Any `m=1` structural failure stops the campaign.

## 10. Numerical gate

The primary numerical gate closes only if:

- every Route P criterion passes;
- every Route I criterion passes;
- the `m=1` control passes;
- correction nonnegativity passes;
- seed/source/batch integrity tests pass; and
- no frozen historical artifact changes.

Secondary Stage-A/Stage-D and historical-comparator differences are reported
but do not control the gate.

If any primary item fails, stop before Lean and return `MGT1-TRACK1B-PARTIAL`
for an evidentiary/implementation limitation or `MGT1-TRACK1B-FAILED` for a
theorem, sign, alignment, or `m=1` contradiction.

If all pass, record exactly:

`NUMERICAL GATE CLOSED — LEAN AUTHORIZED`.

## 11. Lean gate and targets

Only after numerical authorization, create the Lean source and compile it
against the pinned project. Formalize:

1. `w=min m tau` and the short/long partition;
2. the short-cycle whole-path statistic;
3. pointwise and expectation-level decomposition;
4. correction nonnegativity;
5. `m=1` reduction;
6. rho scaling; and
7. derivative-map algebra using the existing abstract stopped-integral
   differentiation interface.

The axiom audit must list `#print axioms` output. Explicit analytic hypotheses
are allowed but must be identified as remaining assumptions. The result may
not be described as a fully instantiated frozen-CUSUM theorem unless the
random-window measurability and moment obligations are actually discharged.

## 12. Arb

`NOT REQUIRED`. Track 1B claims no new rigorously certified scalar inequality.

## 13. Final decision

Allowed states are `MGT1-TRACK1B-CLOSED`, `MGT1-TRACK1B-PARTIAL`, and
`MGT1-TRACK1B-FAILED`.

`CLOSED` requires historical reproduction, frozen protocol integrity, both
numerical routes passing, `m=1` passing, compiled Lean spine, transparent
axioms/assumptions, authoritative full-suite success, and unchanged history.

If closed, the scoped `m>1 derivative theorem` requirement becomes `CLOSED`.
No overall Level-4 re-audit is performed.

