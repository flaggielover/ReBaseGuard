# Frozen protocol — L4R-06 stability-aware policy closure

**Campaign:** isolated same-requirement closure of original mandatory L4R-06

**Freeze date:** 2026-08-24

**Confirmatory monitoring outcomes inspected before freeze:** none

**Historical inputs used for design:** Stage C/C.1, Track 1B, D4, and final
global re-audit artifacts listed in `REQUIREMENT_AUDIT.md`

This file is immutable after its SHA-256 is recorded. No policy, regime,
margin, seed, sample size, shift, endpoint, interval method, safety guard, or
decision criterion may change after confirmatory outcomes are generated.

## 1. Scope and historical firewall

The target is exactly:

`L4R-06 — Stability-aware reuse policy with monitoring consequences`.

Stage C remains `STAGE-C-PARTIAL`; C6 remains failed at `Delta=0.25` and
`0.5`; Stage C.1 remains independently closed; the final global audit remains
`LEVEL-4-PARTIAL`; and L4R-12 is untouched. This campaign performs no global
re-audit, semi-real validation, D4 reinterpretation, or new theorem campaign.

## 2. Primary policy and baselines

Let `rho_c,L95(m)` be the lower endpoint of the frozen D4 95% confidence
interval for the unconstrained local stability boundary. Freeze

`rho_P3(m)=min(1,0.8*rho_c,L95(m))`.

The factor `0.8` is a fixed 20% safety margin selected before outcomes. It may
not be tuned. The D4 point-estimate policy is excluded from closure and is not
run. Policies are:

- P0 fresh: `rho=0`.
- P1 full reuse: `rho=1`.
- P2 historical fixed comparison: `rho=0.0297958439`.
- P3 primary uncertainty-aware policy: formula above.

P3 must be reconstructed from the protected D4 JSON; hard-coded display values
alone are insufficient.

## 3. Frozen regimes and P3 actions

`m in {1,20,70,100}` with exact P3 values

`{1:0.05364218801989182, 20:0.24541780396034488,
  70:0.7819935545467208, 100:1.0}`.

Display values are `{0.053642,0.245418,0.781994,1.000000}`. At `m=100`, the
unit value follows from the general cap because `0.8*rho_c,L95>1`; it is not a
special-case override. Active clipping regimes are `{1,20,70}`. `m=100` is the
pre-specified clearly stable saturation control.

## 4. Frozen detector and simulator semantics

Residuals follow the frozen Gaussian primary model. The symmetric two-sided
CUSUM uses `k=1/2`, inclusive `h=5`, detector reset each cycle, minimum dwell
`tau>=m`, and alarm-selected mean over the terminal window. Re-baselining uses

`e_next=rho*mu_reuse+(1-rho)*mu_fresh`.

A shift at a cycle boundary changes reference error by `e <- e-Delta` and does
not inform the detector. The campaign simulator must import the frozen CUSUM
update, streams, scale, direction, and re-baselining primitives. For every
frozen `m` and policy, its `Delta=0` output must match the existing multi-cycle
oracle bit-for-bit on protocol-independent test configurations.

## 5. Frozen numerical allocation

- confirmatory seed `2026082406`;
- bootstrap seed `2026082407`;
- adversarial independent seed `2026082408`;
- 200 replicate clusters per cell;
- 200 events per replicate;
- 300 burn-in cycles;
- 15 in-control spacing cycles between events;
- positive shifts `{0.25,0.5,1.0,1.5}` plus the `Delta=0` denominator arm;
- 10,000 joint replicate-cluster bootstrap resamples;
- 95% familywise simultaneous intervals;
- identical allocation for all policies, regimes, and arms.

These seeds were absent from tracked repository sources before this document
was created. Replication never increases after outcomes. Checkpoints are
resumable and exclude absolute paths, wall-clock fields from generated science,
and raw cycle arrays; per-replicate summaries are retained for paired inference.

## 6. Frozen endpoints

Primary reference endpoint:

`MSE_e(P,m)=mean_r mean_cycles(e_prev^2)`.

Primary operational endpoint:

`ARL_0(P,m)=mean_r mean_in_control_cycles(tau)`.

Primary normalized detection response:

`R_Delta(P,m)=mean_r(delay_Delta)/mean_r(delay_0)`

using ratios of means and paired replicate clusters. Absolute guard:

`Q_Delta(m)=mean_r(delay_Delta|P3)/mean_r(delay_Delta|P0)`.

Reference bias/SD/ACF1, direction ACF1, raw delays, all P2 outcomes, and
`epsilon=0.05` response non-inferiority are secondary and cannot control
closure.

## 7. Simultaneous inference

Every bootstrap draw resamples the same replicate indices jointly across all
policies, regimes, and arms. Within each frozen family, simultaneous bounds use
the 95th percentile of the maximum centered bootstrap deviation. No marginal
interval may substitute for a simultaneous gate.

Families are:

1. three `MSE(P1)-MSE(P3)` active-regime contrasts;
2. three `ARL_0(P3)-ARL_0(P1)` active-regime contrasts;
3. sixteen `R_Delta(P3)-R_Delta(P0)` contrasts;
4. sixteen `Q_Delta` ratios.

## 8. Frozen hypotheses

### H6-1 — stability control

For all four regimes, P3 must equal the formula reconstructed from protected
D4 data and satisfy `rho_P3<=0.8*rho_c,L95`; when capped at one, the uncapped
allowance must be at least one. The implied uncertainty-aware multiplier bound
is at most 0.8. Passes by construction only if all arithmetic/source checks do.

### H6-2 — reference improvement

For every active clipping regime `{1,20,70}`, the simultaneous lower 95% bound
for `MSE(P1)-MSE(P3)` must be strictly positive. The saturated `m=100` P3/P1
identity is reported exactly and is not counted as improvement.

### H6-3 — operational consequence

For every active clipping regime `{1,20,70}`, the simultaneous lower 95% bound
for `ARL_0(P3)-ARL_0(P1)` must be strictly positive, demonstrating reduced
false-alert burden relative to full reuse. This is not sufficient without
H6-4 and the absolute safety guard.

### H6-4 — normalized-response non-inferiority

For all 16 `(m,Delta)` conditions, the simultaneous upper 95% bound for

`R_Delta(P3)-R_Delta(P0)`

must be strictly below primary `epsilon=0.10`. `epsilon=0.05` is reported as a
secondary sensitivity only and cannot replace the primary rule.

### Absolute-delay safety guard

For all 16 conditions, the simultaneous upper 95% bound for `Q_Delta` must be
strictly below `1.25`. A failed guard is a strong safety contradiction and
prevents closure even if H6-1 through H6-4 otherwise pass.

### H6-5 — joint policy success

H6-1, H6-2, H6-3, H6-4, and the absolute-delay safety guard must all pass. No
qualitative override, favorable subset, or secondary metric can rescue a fail.

## 9. Frozen closure criteria

- C06.1 original L4R-06 reconstructed exactly.
- C06.2 P3 is mechanically stability-aware.
- C06.3 policy, regimes, endpoints, inference, and thresholds frozen before outcomes.
- C06.4 H6-2 reference improvement passes.
- C06.5 H6-3 operational consequence passes.
- C06.6 H6-4 normalized-response non-inferiority passes.
- C06.7 absolute-delay safety guard and simulator semantic guards pass.
- C06.8 D4 remains local/deterministic and historical D2.5 remains
  `MATHEMATICAL, NOT OPERATIONAL`.
- C06.9 historical Stage C and C6 remain unchanged.
- C06.10 all A1–A23 adversarial checks pass.
- C06.11 focused tests, byte-stable reproduction, and authoritative repository
  verification pass.

The scoped verdict is exactly one of:

- `L4R06-POLICY-CLOSED`: C06.1–C06.11 all pass.
- `L4R06-POLICY-PARTIAL`: history/integrity are valid but one or more
  scientific/evidentiary criteria fail.
- `L4R06-POLICY-FAILED`: protocol, history, simulator semantics, required data,
  or reproducibility integrity is invalid.

Original L4R-06 maps to `PASS` only when the scoped verdict is CLOSED,
`same_requirement_mapping=true`, and `historical_C6_preserved=true`.

## 10. Negative-result handling

Every policy/regime/shift remains present. P3 reference-only improvement,
operational failure, detection degradation, near-fresh collapse, P2 dominance,
stable-control disagreement, or any unfavorable condition is reported. No
regime, shift, sample, threshold, or margin changes after outcomes.

## 11. Adversarial suite

The suite contains exactly:

- A1 Stage C unchanged.
- A2 historical C6 failure preserved.
- A3 D4 unchanged.
- A4 L4R-12 untouched.
- A5 P3 rule frozen before outcomes.
- A6 no outcome-driven rho tuning.
- A7 no regime deletion.
- A8 no sample-size increase after outcomes.
- A9 stability-awareness is mechanical.
- A10 operational consequence pre-specified.
- A11 reference-only improvement cannot close the requirement.
- A12 no operational-phase-transition wording.
- A13 no universal safety claim.
- A14 fresh comparator preserved.
- A15 full-reuse comparator preserved.
- A16 simultaneous non-inferiority valid.
- A17 negative outcomes retained.
- A18 same-requirement mapping explicit.
- A19 figures read final JSON only.
- A20 protected hashes unchanged.
- A21 focused tests green.
- A22 full verifier green.
- A23 reproducer byte-stable.

The first run is preserved exactly. Only implementation/reporting defects may
be repaired; no scientific gate may weaken.

## 12. Figures, reproduction, and verification

Final JSON alone generates: policy rho/margin, reference distortion,
operational alert consequence, P3-vs-fresh non-inferiority, and joint criteria.

The default reproducer verifies hashes, reconstructs policy actions, replays
committed per-replicate summaries through analysis, regenerates figures, runs
focused tests and A1–A23, runs `scripts/verify_level_4.sh`, and confirms Stage C
and C6 history. An explicit `--recompute` mode may rerun the expensive frozen
simulation from the same seeds before identical checks.
