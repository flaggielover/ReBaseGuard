# Frozen protocol — D4 theorem-supported `(m,rho)` phase map

**Campaign:** isolated closure of `L4R-11`, the D4 `m-rho` phase map  
**Freeze date:** 2026-08-24  
**Pre-freeze numerical outcomes from this campaign:** none  
**Historical information used for design:** Stage-D crossing bracket `[50,75]`
and Track-1B theorem/correspondence, both already public in the repository

This file is immutable after its SHA-256 is recorded. No grid, seed, sample
size, interpolation rule, validation cell, threshold, or decision criterion
may change after D4 numerical outcomes are inspected.

## 1. Scope and selected design

The approved design is theorem-first:

1. estimate the exact Track-1B `GammaTilde_m` on a frozen grid;
2. derive `lambda=rho(1-GammaTilde_m)` and `rho_c` mechanically;
3. audit selected cells with a separately implemented direct finite
   difference;
4. show a small consequence-only operational overlay.

Rejected designs are a brute-force heatmap that discovers a boundary without
the theorem, and a replay-only artifact that adds no new frozen-grid
uncertainty. The chosen design isolates the theorem boundary from the
operational measurements and keeps historical Stage D immutable.

This campaign does not address external validation, novelty, SR Arb,
location-family theory, invariant laws, stochastic period-2 behavior, or the
global Level-4 verdict.

## 2. Frozen mathematical object and detector

Residuals are iid `N(-e,1)`. The reset symmetric two-sided CUSUM uses
`k=1/2`, inclusive `h=5`, and includes the terminal observation. There is no
minimum dwell.

With ordinary alarm time `tau`, `T_tau=sum_{t<=tau}Z_t`,
`w=min(m,tau)`, and

`A_m=(1/w)sum_{r=0}^{w-1}Z_{tau-r}`,

the primary scalar is

`GammaTilde_m=E_0[A_m T_tau]`.

The correction audit uses

`C_m=E_0[1{tau<m}(1/tau-1/m)T_tau^2]`.

The primary boundary is generated only from

`lambda(m,rho)=rho(1-GammaTilde_m)`.

## 3. Frozen grids

The `m` grid is

`{1,2,5,10,20,35,50,60,65,70,72,75,80,90,100,150,250}`.

It contains the required historical points, a deliberately modest refinement
around the historical `[50,75]` crossing, and large-window stable controls.

The visualization/classification `rho` grid is

`{0,0.029796,0.05,0.10,0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90,0.95,1.00}`.

`0.029796` is the Stage-C conservative `rho_safe(delta=0.2)`. The theorem
curve itself is continuous and is not discovered from this display grid.

## 4. Gamma estimator, seeds, and checkpoints

Master seed `2026082404` was searched across tracked repository sources before
freeze and was absent. NumPy `SeedSequence` with PCG64 is used throughout.

- Gamma batches: `[2026082404,1,batch]`.
- Direct-map plus/minus branches: `[2026082404,2,cell,step,rep,sign,batch]`.
- Direct-map fresh-reference draws: route component `3` with the same remaining
  key fields; the identical fresh batch is used at `+epsilon` and `-epsilon`
  so its centered contribution cancels in the finite difference.
- Operational overlay: `[2026082404,4,cell,batch]`.
- Smoke tests use route components `90` and above and never enter results.

The Gamma run has 64 independent batches of 25,000 stopped cycles, for
1,600,000 cycles total. The batch mean is the statistical unit. For every `m`,
the checkpoint records the mean, batch SE, normal 95% CI, direct
fixed-plus-correction reconstruction, `C_m`, its batch SE/CI,
`P(tau<m)`, and a Wilson 95% interval. No raw paths are written.

The Gamma checkpoint is valid only if all 64 seed keys are unique; every
summary is finite; every Gamma SE is positive; direct and reconstructed
integrands agree to at most `1e-10` pathwise; batch means agree to at most
`1e-10`; and every correction integrand is at least `-1e-14`. `m=1` must have
zero correction and zero short-cycle probability exactly.

## 5. Boundary derivation and interpolation

For every `m`, the finalizer computes `lambda` and `rho_c` using the algebra in
`THEOREM_BRIDGE.md`. It never fits a boundary to rho-grid outcomes.

Between sampled `m` values, figures use piecewise linear interpolation in
`log(m)` of the point estimates of `GammaTilde_m`; no spline, isotonic repair,
or outcome-selected smoother is permitted. Every adjacent `GammaTilde_m=2`
crossing is reported. The primary crossing bracket is the pair of adjacent
frozen grid points straddling two; the secondary point estimate is linear in
`log(m)`. If there is no crossing, or more than one, that fact is reported
without changing the grid.

## 6. Frozen direct-map correspondence audit

The six validation cells are fixed before outcomes:

| cell | `m` | `rho` | intended coverage from historical evidence |
|---|---:|---:|---|
| V1 | 1 | 0.20 | small-window, strongly unstable |
| V2 | 20 | 0.20 | clearly stable |
| V3 | 20 | 0.40 | unstable side at the same `m` |
| V4 | 50 | 0.70 | near-boundary, lower side |
| V5 | 50 | 0.80 | near-boundary, upper side |
| V6 | 100 | 1.00 | large-window, full-reuse stable |

The perturbation ladder is `epsilon={0.025,0.0125,0.00625}`. Detector threshold
`h=5` is unchanged; `epsilon` is never called a detector threshold.

For each cell, epsilon, and each of two independent replications, simulate
20 batches of 12,500 cycles at each sign (250,000 per sign per replication).
The direct-map implementation imports only the frozen CUSUM update and does
not import the Gamma accumulator, boundary finalizer, or theorem helper. The
plus and minus stopped paths use disjoint seeds. Fresh centered draws are
generated separately from stopped paths and paired across signs.

The primary derivative is the second-order Richardson value formed from the
`epsilon=0.0125` and `0.00625` central differences. The `0.025` result is a
required truncation diagnostic. Route replications are inverse-variance
pooled only after each is reported.

Every cell passes correspondence only if:

1. the pooled Richardson estimate differs from theorem `lambda` by at most
   four combined SE;
2. when `|lambda|<0.5`, the absolute discrepancy is at most `0.10`; when
   `|lambda|>=0.5`, the relative discrepancy is at most 10%;
3. the two independent Richardson replications agree within four combined SE;
4. all seed/source separation checks pass; and
5. all ladder values and all cells remain present.

No tolerance may widen after inspection. A failed cell makes D4.4 fail.

## 7. Frozen operational overlay

The consequence-only cells are

`{(20,0.20),(20,0.40),(50,0.60),(50,0.90),(100,1.00)}`.

They cover both sides of accessible theorem boundaries and a large-window
full-reuse stable control. Each cell uses 20 independent batches of 250
replicates. Each replicate runs 60 repeated cycles with the first 20 discarded
as burn-in. The statistical unit is the replicate.

Report batch-based mean, SE, and 95% CI for in-control cycle ARL, reference
MSE, reference-state ACF1, and alarm-direction ACF1. No operational metric is a
closure threshold and no discontinuity is required. Outcomes A through D in
the campaign brief are all admissible. The report must explicitly retain
Stage-D D2.5 as `MATHEMATICAL, NOT OPERATIONAL`.

## 8. Figures and data provenance

The primary figure has horizontal `m`, vertical `rho`, and theorem-derived
local class. It overlays the continuous `rho_c(m)` curve, `rho=1`, and Stage-C
`rho_safe=0.029796`. Its title contains “Local deterministic reference-map
stability”.

A secondary Gamma/rho-boundary figure and an operational-overlay figure may be
generated. Every committed figure is generated from final JSON only. Figure
code may not read checkpoints or historical raw results directly.

## 9. Frozen D4 criteria

- D4.1 exact Track-1B theorem correspondence reconstructed.
- D4.2 Gamma estimated on the complete frozen grid with valid uncertainty.
- D4.3 rho_c mechanically derived from Gamma.
- D4.4 all six direct-map cells pass the frozen correspondence rules.
- D4.5 map classification and figure provenance agree with theorem JSON.
- D4.6 Stage-A/Stage-D semantic guard passes.
- D4.7 operational overlay is complete and makes no unsupported transition
  claim.
- D4.8 historical D2.5 negative result is preserved.
- D4.9 all fourteen adversarial checks pass.
- D4.10 authoritative repository verification passes.

The final state is exactly one of `D4-PHASE-MAP-CLOSED`,
`D4-PHASE-MAP-PARTIAL`, or `D4-PHASE-MAP-FAILED`.

`CLOSED` requires D4.1 through D4.10. A theorem/sign/semantic contradiction,
historical mutation, invalid primary estimator, or source coupling returns
`FAILED`. A complete, honestly reported campaign with an evidentiary or
precision gate failure returns `PARTIAL`.

## 10. Adversarial checks

The final suite contains exactly A1–A14 from the campaign brief: protocol
hash; D2.3 preservation; D2.5 preservation; Track-1A failure; Track-1B
closure; Stage-A exclusion; frozen grid; frozen interpolation; direct-route
separation; no operational overclaim; no universal wording; final-JSON-only
figures; no hidden raw dependency; and full-verifier evidence.

## 11. Reproduction and failure states

The default reproducer verifies hashes, replays committed checkpoint summaries
through the deterministic finalizer, regenerates figures, runs focused tests
and A1–A14, runs the authoritative repository verifier, and confirms historical
hashes and a clean tree. `--recompute` reruns expensive Gamma, direct-map, and
operational simulations from the frozen seeds before the same checks.

Generated JSON excludes wall-clock time, absolute paths, and mutable commit
identifiers. Replaying summaries must be byte-stable. Missing batches,
duplicate seeds, non-finite values, changed protocol/hash, changed history,
source coupling, omitted cells, or altered figures are hard failures.
