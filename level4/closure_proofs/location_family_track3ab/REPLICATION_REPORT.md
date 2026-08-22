# Track-3A variance-aware t3 replication report

## Decision

```text
T3A-NUMERICAL-PASS
NUMERICAL GATE CLOSED — LEAN AUTHORIZED
```

The protocol and numerical implementations were frozen and pushed before the
fresh master seed `2026082317` was used.  The campaign ran exactly two
independent replications with no resizing, seed replacement, threshold change,
h replacement, or tolerance change.

## Fixed design

Each replication used:

```text
Route A: 192 batches × 200,000 paths = 38,400,000 paths
Route B: 192 batches × 25,000 paired streams = 4,800,000 streams
h ladder: 0.05, 0.025, 0.0125
primary h: 0.0125
relative limit: 3%
|z| limit: 3
```

The historical plug-in relative SE target was at most 1%; the selected design
predicted `0.8527%`.  No fresh pilot was needed.

## Replication results

All uncertainty below is computed from independent batch estimates.  Route B
uses the paired batch derivative directly.

| replication | Route-A `Gamma_f` | Route-A derivative | Route-B derivative | relative | `|z|` | result |
|---:|---:|---:|---:|---:|---:|---|
| 1 | `8.6395620 ± 0.0454570` | `-7.6395620 ± 0.0454570` | `-7.7056999 ± 0.0470133` | `0.8620%` | `1.0114` | PASS |
| 2 | `8.6819523 ± 0.0458770` | `-7.6819523 ± 0.0458770` | `-7.6444510 ± 0.0443650` | `0.4894%` | `0.5876` | PASS |

Both replications individually pass the unchanged 3% criterion and the frozen
combined-SE limit.

## Independent-replication agreement

| route | relative discrepancy | `|z|` | result |
|---|---:|---:|---|
| Route A | `0.5533%` | `0.6564` | PASS |
| Route B | `0.7980%` | `0.9475` | PASS |

The historical failure was specifically a Route-B replication discrepancy of
`4.605351% > 3%`.  The new `0.7980%` result is a later independent experiment;
it does not change the old failed decision.

## Pooled primary correspondence

```text
Route-A derivative: -7.6607571455 ± 0.0322677793
Route-B derivative: -7.6750754440 ± 0.0323163590
relative discrepancy: 0.1867299794%
|z|:                  0.3135309498
```

The pooled comparison passes both frozen limits.

## h-ladder diagnostics

| `h` | Route B replication 1 | Route B replication 2 |
|---:|---:|---:|
| `0.05` | `-7.6769487 ± 0.0227770` | `-7.6649617 ± 0.0199686` |
| `0.025` | `-7.7592387 ± 0.0318613` | `-7.6924246 ± 0.0310451` |
| `0.0125` primary | `-7.7056999 ± 0.0470133` | `-7.6444510 ± 0.0443650` |

The ladder is diagnostic only.  The frozen primary step passed without using
Richardson or observed-order arguments.

## Variance, tail, and CRN diagnostics

Route-A batch SEs (`0.0455`, `0.0459`) met the historical sizing prediction.
Its top 1% of absolute path gains accounted for about 38.7% of within-batch
variance, consistent with the pre-outcome t3 tail diagnosis.  Across 192
batches, maximum leave-one-batch influence on `Gamma_f` was only `0.111%` and
`0.097%` of the mean.  Ordinary, median, and 10% trimmed batch estimates were
close; robust summaries remain diagnostic.

At primary `h`, mean Route-B `+h/-h` CRN correlations were `0.96898` and
`0.96889`.  Batch skew was modest.  The paired design retained its intended
variance reduction.

## Operating point and integrity

Route-A ARLs were `465.52035 ± 0.07871` and `465.58838 ± 0.07455`; relative
errors from immutable `465.891191` were `0.0796%` and `0.0650%`, well inside
2%.

All of the following passed:

- protocol and frozen source hashes;
- historical hashes and old Track-3 decision immutability;
- exact t3 score and score bound;
- Gaussian algebraic specialization;
- source-level Route A/B separation;
- seed-family disjointness;
- h ladder and primary-step checks;
- all 768 checkpoint coordinate and seed checks;
- batch map identities (maximum error `9.33e-14`); and
- zero exact ties and zero simultaneous crossings.

`results/numerical_decision.json` is the authoritative machine-readable gate.
`numerics/audit_numerical.py` independently reconstructs the decision from the
retained batch checkpoints.
