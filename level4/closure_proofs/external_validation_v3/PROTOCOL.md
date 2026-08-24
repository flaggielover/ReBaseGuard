# External validation V3 frozen protocol

Status: **FROZEN BEFORE ALL CONFIRMATORY P0/P1/P2 OUTCOMES**.

This file, `TASK_DEFINITIONS.md`, `METRIC_DEFINITIONS.md`,
`results/protocol.json`, `results/dataset_selection.json`, and
`manifests/datasets.json` form the hashed protocol bundle.

## Scope and execution order

1. Protect every historical artifact and preserve Stage E and V2 exactly.
2. Diagnose V2 from persisted results only.
3. Audit twelve new datasets without running reuse-policy comparisons.
4. Freeze two primaries, checksums, models, splits, metrics, power, hypotheses,
   aggregation, taxonomy, and stop rules; checkpoint and push.
5. Build each residual stream and run P0-only calibration, leakage, and actual
   power gates. Do not generate confirmatory policy results until both tasks
   pass, or record a technically unusable task without replacement.
6. Generate every frozen outcome and preserve null, unfavorable, and
   contradictory results.
7. Stop after these two tasks. No V4 is authorized.

## Confirmatory architecture

- Primaries: MetroPT-3 industrial compressor and Online Retail II demand.
- Backup: none. Neither scientific failure nor low support permits replacement.
- Splits: chronological 30/20/50 after frozen causal feature construction.
- Detector: inclusive two-sided CUSUM, `k=0.5`, `m=20`, with one task threshold
  calibrated under P0 and shared by all policies.
- P0 fresh: rho 0. P1 full alarm-selected reuse: rho 1. P2 authoritative
  ReBaseGuard: rho 0.029796. P3 is absent; any later P3 is exploratory only.
- Target ARL: MetroPT 32 observations; Retail 24 observations.
- Calibration: log-threshold bisection; relative point tolerance 10%; target
  inside a dependence-aware 95% interval; at least 40 effective blocks.
- Interventions: STEP 0.5/1.0/2.0 SD, GRADUAL 0 to 1 SD over 24 hours, and
  RECURRING +1 SD for 48 hours then off for 48 hours.
- Events: 240 deterministic outcome-blind locations in the central 80% of
  evaluation subject to warmup/censoring; identical across policies.
- Event cap: four target ARLs; warmup: two target ARLs.
- Inference: 10,000 deterministic moving-block bootstrap draws. Natural blocks
  are task-specific physical/observation-time units in `TASK_DEFINITIONS.md`;
  event blocks contain six adjacent events.
- Effective-block floor: 40 for calibration and every closure endpoint.
- Primary/secondary simultaneous non-inferiority margins: 0.10 / 0.05.
- Multiplicity: the five H3-3 conditions use simultaneous one-sided 99%
  intervals. H3-1 and the two prespecified H3-2 routes use paired one-sided
  97.5% bounds; no additional route may be invented.

## Task and campaign taxonomy

A task is `V3-TASK-SUPPORTED` iff its data, leakage, calibration, and actual
power gates pass and H3-1, H3-2, and H3-3 all pass mechanically. A usable task
missing any hypothesis is `V3-TASK-NOT-SUPPORTED`. A failed pre-outcome gate is
`V3-TASK-UNUSABLE`.

The campaign is:

- `EXTERNAL-VALIDATION-V3-CLOSED` iff at least one new V3 task is supported,
  the frozen cross-campaign rule closes L4R-15, no V3 strong contradiction
  exists, and integrity/reproduction gates pass;
- `EXTERNAL-VALIDATION-V3-PARTIAL` iff the usable evidence is informative but
  L4R-15 is not closed and no failure condition applies;
- `EXTERNAL-VALIDATION-V3-FAILED` for a strong P2 contradiction, protocol or
  historical-integrity failure, or two unusable primaries.

## Frozen cross-campaign aggregation rule

The original substantive L4R-15 semi-real external-validation requirement is
`CLOSED` when at least two independently frozen, sufficiently powered tasks
across post-Stage-E campaigns each support their campaign's full mechanism
package, provided they use independent datasets and domains, each passed its
pre-outcome gates, no strong P2 contradiction exists in the V3 confirmatory
campaign used for closure, and every historical negative task remains visible.

V2 Household contributes exactly one success. V2 itself remains 1/3 and
`EXTERNAL-VALIDATION-V2-PARTIAL`. One new V3 success in either selected domain
would raise the cross-campaign count to two. No statistics are pooled, Stage E
is not relabeled, and this rule changes only the later evidentiary status of
L4R-15. This is compatible with the repository's established convention that
later isolated campaigns may close an original requirement without changing
its failed historical stage.

## Claim and stop boundary

Even a V3 closure is evidence for the frozen mechanism on two independent
tasks, not production validation, deployment readiness, universal robustness,
distribution-free validity, detector independence, or optimality. V3 performs
no global Level-4 re-audit. After V3, stop: the next action is either a final
global re-audit if L4R-15 closes, or a human global scientific decision if it
does not.
