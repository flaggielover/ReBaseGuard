# External validation V2 frozen protocol

Status: **FROZEN BEFORE CONFIRMATORY POLICY OUTCOMES**.

This document, `TASK_DEFINITIONS.md`, `METRIC_DEFINITIONS.md`,
`results/protocol.json`, `results/dataset_selection.json`, and
`data_manifest/datasets.json` form the frozen protocol bundle.

## Execution order

1. Verify novelty closure, clean/synchronized Git, authoritative repository
   verifier, and protected tracked-file hashes.
2. Select datasets from metadata/raw structure and projected power only.
3. Freeze this bundle and its hash; checkpoint and push.
4. Acquire/checksum selected archives; deterministically build models and
   residuals; run calibration and actual power/leakage gates.
5. Only after every primary is gated (or the technical backup rule is applied),
   generate confirmatory matched policy outcomes.
6. Preserve every null, unfavorable, contradictory, censored, or unusable
   result without rescue tuning.

## Confirmatory design

- Three primaries: household power, metro traffic, Beijing PM2.5.
- Technical backup: ElectricityLoadDiagrams20112014, usable only before outcomes
  for a primary's non-outcome technical failure.
- Splits: chronological 30/20/50 after frozen preprocessing.
- Detector: two-sided CUSUM, `k=0.5`, `m=20`, shared task threshold.
- Policies: P0=0, P1=1, P2=0.029796; no closure-relevant P3.
- Calibration: fresh policy only; log-threshold bisection; target ARL 60 hours
  (240 observations at 15 minutes; 60 hourly); relative point tolerance 10%;
  target inside 95% moving-block interval; >=20 effective blocks.
- Interventions: STEP 0.5/1.0/2.0 SD, GRADUAL 0->1 over 24 hours, RECURRING
  +1 for 48 hours/off 48 hours. Locations are deterministic and outcome-blind.
- Events: 120; grid central 80% of evaluation after warmup/censoring constraints;
  identical across policies; seed 20261201.
- Bootstrap: 10,000 draws, seed 20261202; weekly natural blocks and six-event
  controlled blocks; floor 20.
- Primary/secondary non-inferiority margins: 0.10 / 0.05.

## Claim boundary

Even a closed campaign supports only: “In a later independently frozen
semi-real validation campaign, the mechanism package was supported in at least
two of three pre-specified sufficiently powered streams.” It never supports
production validated, universally robust, deployment proven,
distribution-free, detector-independent, all real-world streams, or optimal.

No global Level-4 re-audit is part of this protocol.
