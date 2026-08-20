# ReBaseGuard Phase-4B Second-Detector Witness Report

**Date:** 2026-08-19

**Detector:** symmetric two-chart Shiryaev-Roberts

**Frozen design shift:** `delta=1`

**ARL-calibrated threshold:** `A=520.3125`

**Gate status:** diagnostic work complete; rigorous certification not started

## Executive verdict

Yes. The symmetric two-chart SR detector provides a genuine, structurally
distinct second-detector instability witness at the precommitted diagnostic
standard.

The pooled two-million-path result is

```text
Gamma_D = 17.2720847004
Monte Carlo SE = 0.0280269524
diagnostic 95% interval = [17.2171528831, 17.3270165178].
```

The whole interval exceeds `5`, so the precommitted interpretation is
**strong instability witness / GREEN-A candidate**. It implies the diagnostic
local slope

```text
F_D,1'(0) = 1-Gamma_D = -16.2720847004
```

and a diagnostic critical reuse fraction

```text
rho_c,D = 1/(Gamma_D-1) = 0.06145494068,
95% transformed interval [0.06124817715, 0.06166310494].
```

These numerical intervals are Monte Carlo intervals, not continuum
certificates. The recommended Level-4 route verdict is **GREEN-A candidate:
advance SR to a separate rigorous-certification design gate**, subject to user
approval. This phase stops here as required.

## Gate 1 — detector and convention validation

The exact recursion, inclusive post-update alarm boundary, common observation
for both charts, tie convention, reset convention, and `m=1` terminal reuse are
frozen in [detector_definition.md](detector_definition.md).

The scalar log-domain oracle and a separately coded raw-state replay agree on
fixed positive, negative, overshoot, reflected, and exact/epsilon-boundary
paths. Eleven initial oracle tests and subsequent simulation/multi-cycle tests
cover:

- initial state and frozen `delta`;
- exact and epsilon crossing;
- both-chart updates from the same residual;
- large overshoot;
- simultaneous crossing and exact tie handling;
- reflection with reward preservation;
- terminal sum including the firing increment; and
- seed reproducibility and common-random-number path addressability.

The persisted replay is [pathwise_replay.json](pathwise_replay.json), whose
`all_checks_pass` field is true.

## Gate 2 — ARL-only calibration

Threshold calibration used seed `314159` and never inspected `Gamma_D`.
All 12 attempts, including coarse, bisection, and sensitivity settings, are
preserved in [arl_calibration.json](arl_calibration.json). No attempted setting
failed or returned null.

The selected calibration estimate was

```text
A = 520.3125
ARL = 464.9636667
SE = 1.3178603
target = 465.
```

The higher-sample sensitivity triplet was:

| Threshold | Relative setting | ARL | SE |
|---:|---:|---:|---:|
| 494.296875 | `0.95 A` | 442.2465 | 1.0203 |
| 520.312500 | `1.00 A` | 465.5122 | 1.0745 |
| 546.328125 | `1.05 A` | 488.7385 | 1.1297 |

The later independent witness samples gave pooled ARL `464.4071` with SE
`0.3221`, confirming the intended operating scale without retuning.

## Gate 3 — stopped-score witness

The precommitted seeds and results were:

| Seed | Paths | ARL (SE) | `Gamma_D` (SE) | 95% interval |
|---:|---:|---:|---:|---:|
| 1729 | 1,000,000 | 464.5321 (0.4553) | 17.2221 (0.0397) | [17.1443, 17.2999] |
| 20260818 | 1,000,000 | 464.2822 (0.4558) | 17.3221 (0.0396) | [17.2445, 17.3996] |
| pooled | 2,000,000 | 464.4071 (0.3221) | 17.2721 (0.0280) | [17.2172, 17.3270] |

Convention diagnostics are internally consistent:

- pooled arm fractions are `0.4996925` plus and `0.5003075` minus;
- no exact floating-point tie occurred;
- `E[Z_tau]` is `-0.00135` and `E[T_tau]` is `0.01177`;
- `E[T_tau^2]-E[tau]=0.260`, small relative to the ARL scale; and
- both independent seeds separately fall in the GREEN-A regime.

The machine-readable campaign, including all seeds, settings, runtimes,
environment versions, protected hashes, and empty failed/null ledger, is
[diagnostic_runs.json](diagnostic_runs.json).

## Gate 4 — protected CUSUM positive control

The protected `k=0.5`, `h=5`, `m=1` CUSUM was passed through the same new
summary harness without modifying the protected simulator or any proof
artifact. With one million paths and seed `1729`, it returned

```text
ARL = 465.363379
Gamma = 15.8429362
SE = 0.0402915
95% interval = [15.7639662, 15.9219062].
```

This reproduces the established `15.87` diagnostic scale and is a positive
control for reward indexing, the terminal increment, stopped-sum inclusion,
seed handling, and standard errors. The side-by-side conventions are recorded
in [convention_matrix.md](convention_matrix.md).

## Gate 5 — does the score identity survive removal of CUSUM structure?

Yes. The identity is a stopped-likelihood-score result, not a reflected-CUSUM
recursion result. For residuals distributed as `N(-e,1)`, the stopped
likelihood ratio is

```text
exp(-e T_tau - e^2 tau/2).
```

The frozen SR stopping rule is parameter-invariant in residual coordinates and
has a geometric tail because an extreme observation forces an alarm uniformly
from every live state. Reflection supplies the centered fixed point. Therefore
the already audited Gaussian stopped-score argument specializes to SR as

```text
F_D,1'(0)=1-E_0[Z_tau T_tau]=1-Gamma_D.
```

The proof of the identity and its required detector-specific checks are in
[score_derivation.md](score_derivation.md). What remains detector-specific is
the numerical value of `Gamma_D`; Phase-4B estimates it but does not certify it.

## Gate 6 — exact mixed-reuse analysis

For an independent mean-zero fresh component,

```text
F_D,rho(e)=rho F_D,1(e),
F_D,rho'(0)=rho(1-Gamma_D).
```

This equality is exact. Only the inserted estimate of `Gamma_D` is
non-rigorous. Delta-method propagation gives SE `0.00010585` for the estimated
`rho_c,D`; direct monotone transformation of the Gamma interval gives the
reported interval.

## Gate 7 — modest multi-cycle sanity check

The precommitted policies used 512 independent chains, 30 burn-in cycles and
120 retained cycles per chain (61,440 retained cycles per policy):

| Policy | `rho` | Error SD | lag-1 error corr. | direction alternation | mean cycle length |
|---|---:|---:|---:|---:|---:|
| fresh | 0 | 0.9995 | -0.0106 | 0.5029 | 80.04 |
| below threshold | `0.8 rho_c=0.0491640` | 0.9508 | -0.0390 | 0.5267 | 83.80 |
| above threshold | `1.2 rho_c=0.0737459` | 0.9346 | -0.0630 | 0.5403 | 84.00 |
| full reuse | 1 | 1.3701 | -0.4983 | 0.8948 | 48.70 |

The full-reuse chain displays clear alternating feedback and increased
reference dispersion. The near-threshold policies differ only modestly under
the injected fresh noise and nonlinear stationary dynamics; this sanity check
is not a bifurcation proof and was not used to select any parameter. Complete
results and all policy seeds (`41001`–`41004`) are in
[multicyle_diagnostic.json](multicyle_diagnostic.json).

## Independence from CUSUM

The witness is genuinely cross-detector evidence. In likelihood-ratio scale,
CUSUM retains a maximum over candidate changepoints, whereas SR sums the
corresponding likelihood products:

```text
CUSUM: max_k product_(i=k)^n Lambda_i,
SR:    sum_k product_(i=k)^n Lambda_i.
```

There is no path-independent monotone transformation from the maximum to the
sum. Shared Gaussian observations and `delta=1` make the comparison fair; they
do not make the detectors equivalent.

## Protection, reproducibility, and stop gate

The historical finite Arb solver, corrected Phase-4A diagnostic solver,
continuum certificate, and all Level-3 artifacts remained untouched. Their
SHA-256 values are embedded in the machine artifacts and rechecked by the
Phase-4B audit. The pinned environment is Python `3.14.5`, NumPy `2.5.2`, SciPy
`1.18.0`, python-flint `0.9.0`, and FLINT `3.6.0`; the project metadata and
`requirements.lock` retain the complete pinned dependency set.

Final regression status is: 64 tests passed; the prior Phase-4A pre-gate audit
passed; the protected continuum audit passed a full Arb replay of the model,
block contraction, residual, resolvent propagation, hashes, and independent
Bellman cross-check; and the independent Phase-4B artifact audit passed every
check. The protected certified interval remains
`Gamma in [3.9243482,27.8493821]`, with its lower endpoint strictly above two.

Reproduction commands are:

```text
.venv/bin/python scripts/run_phase4b_pathwise.py
.venv/bin/python scripts/calibrate_phase4b_sr.py
.venv/bin/python scripts/run_phase4b_diagnostics.py --samples 1000000
.venv/bin/python scripts/run_phase4b_multicycle.py
.venv/bin/python scripts/audit_phase4b.py
```

Phase-4B is now stopped before rigorous second-detector certification. The
recommended next gate, if separately approved, is a feasibility study for a
two-dimensional nonlinear SR continuum operator with Arb interval arithmetic,
a globally certified block-survival contraction, and a residual/resolvent
certificate. No part of that certification has been started here.
