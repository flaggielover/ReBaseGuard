# Track-3 failure diagnoses

## F1 — t3 independent-replication relative gate

**Frozen result:** `FAILED`.

At `h=0.0125`, the two independent direct-map replications were

```text
replication 1: -7.4579823 ± 0.1891541,
replication 2: -7.8095439 ± 0.1880057.
```

Their difference is statistically ordinary (`|z|=1.318`) but is `4.605%` of
their mean absolute magnitude.  The protocol required both `|z|<=3` and
relative discrepancy at most 3%.  Therefore the t3 family fails and the
all-family numerical gate fails.

This is an evidentiary precision/replication failure, not a sign
contradiction:

- pooled Route B versus Route A: `|z|=0.158`, `0.995%`;
- both direct replications are negative and close to the predicted value;
- t3 ARL reproduction error is `0.015%`;
- every source, score, reflection, tie, and seed check passes; and
- no other family fails.

The t3 terminal residual is heavy-tailed and Route A has the largest gain SE
in the grid (`0.4632`).  That is a plausible explanation for the observed
finite-sample spread, not permission to loosen the frozen criterion.

No sample-size increase, alternative seed, family removal, coarser primary
step, Richardson substitution, or tolerance change is permitted.  The result
remains failed.

## F2 — observed order and Richardson

t3 replication 1 had noisy negative observed order; replication 2 had no real
log-ratio order estimate.  The two Richardson diagnostics were approximately
`-7.4224` and `-7.8246`.  The protocol declares both order and Richardson
secondary.  They neither worsen nor rescue F1.

## F3 — Lean gate

The numerical decision is exactly

```text
LOCATION-FAMILY-NUMERICAL-FAILED
NUMERICAL GATE FAILED — LEAN NOT AUTHORIZED
```

Phase 6 is therefore not run.  The repository must contain no Track-3 Lean
artifact, no axiom audit claiming Track-3 formal closure, and no description of
the human theorem as machine-checked.

## F4 — scope of the surviving theorem

The human stopped-score theorem remains mathematically valid under its explicit
hypotheses, and five family cells plus the pooled t3 comparison support it
numerically.  The campaign nevertheless cannot satisfy its predeclared closure
definition without the complete all-family correspondence gate and Lean spine.
The final Track-3 status is therefore partial, not closed.

Historical Stage D/F and Proof Tracks 1--2 are unaffected.

