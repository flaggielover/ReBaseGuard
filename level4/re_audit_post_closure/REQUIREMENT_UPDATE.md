# Post-closure requirement update

This table mirrors the canonical 18-row source in `requirements.json`. Counts
and the verdict are generated; this document contains no independent status
assertions.

| ID | Requirement | Class | Stage-F status | Later evidence | Current | Reason |
|---|---|---|---|---|---|---|
| L4R-01 | Level 1-3 closure foundation | MANDATORY | PASS | None that changes this row | **PASS** | The Level 1-3 Lean and Arb foundation remains closed and reproduced. |
| L4R-02 | Multi-cycle oracle, reproducible | MANDATORY | PASS | None that changes this row | **PASS** | No later campaign changes the closed Stage-A oracle requirement. |
| L4R-03 | Conditional map and derivative correspondence at m=1 | MANDATORY | PASS | None that changes this row | **PASS** | The three-route m=1 correspondence remains closed. |
| L4R-04 | Gamma_CUSUM > 2 rigorously | MANDATORY | PASS | None that changes this row | **PASS** | The outward-rounded Arb enclosure still has lower endpoint above two. |
| L4R-05 | Rigorous period-2 for the deterministic skeleton | MANDATORY | PASS | None that changes this row | **PASS** | Stage B remains closed for the deterministic conditional-mean skeleton only. |
| L4R-06 | Stability-aware reuse policy with monitoring consequences | MANDATORY | PARTIAL | None that changes this row | **PARTIAL** | Stage C remains partial; C6 remains failed and later theorem work does not change the policy outcome. |
| L4R-07 | Confirmatory sensitivity of the stability-aware policy | MANDATORY | PASS (narrow scope) | None that changes this row | **PASS** | Stage C.1 remains closed within its frozen sensitivity scope. |
| L4R-08 | SR Monte Carlo derivative | MANDATORY | PASS | None that changes this row | **PASS** | The matched-ARL SR numerical derivative remains confirmatory numerical evidence. |
| L4R-09 | m>1 derivative theorem | MANDATORY | FAIL | MGT1-TRACK1B-CLOSED | **PASS** | Track 1B independently closed the scoped theorem requirement; historical D2.3 and Track 1A remain failed. |
| L4R-10 | SR derivative theorem (proved) | MANDATORY | OPEN | SR-DERIVATIVE-CLOSED | **PASS** | Track 2 closes the derivative theorem; the separate rigorous SR local-instability certificate remains open. |
| L4R-11 | m-rho phase map (D4) | MANDATORY | FAIL (not run) | None that changes this row | **FAIL** | D4 remains not run and no later closure campaign supplies the phase map. |
| L4R-12 | Operational consequence of the Gamma_m crossing | MANDATORY | NEGATIVE RESULT | None that changes this row | **PARTIAL** | The crossing remains mathematical, not operational; later theorem closure does not change the negative experiment. |
| L4R-13 | Non-Gaussian robustness | STRONG_EXTENSION | PARTIAL | None that changes this row | **PARTIAL** | The six-family numerical evidence remains bounded by the historical t3 estimand ambiguity. |
| L4R-14 | General location-family theorem | STRETCH | OPEN | LOCATION-FAMILY-TRACK3AB-CLOSED | **PASS** | Track 3A/3B closes the regular location-family stopped-score theorem under explicit assumptions; historical Track 3 remains partial. |
| L4R-15 | Semi-real external validation | MANDATORY | FAIL vs its own rule | None that changes this row | **FAIL** | Stage E remains 0/3 for H-E5 and no later external-validation campaign was performed. |
| L4R-16 | Prior-art and novelty verification | MANDATORY | OPEN / provenance gap | None that changes this row | **OPEN** | The external review artifact is still not persisted, so the original hygiene requirement remains open. |
| L4R-17 | Reproducibility of every stage | MANDATORY | PASS | None that changes this row | **PASS** | All historical stages and later scoped campaigns retain documented reproduction entry points. |
| L4R-18 | Protocol integrity | MANDATORY | PASS | None that changes this row | **PASS** | Frozen protocol, precommitment, Stage-F, and closure-track hashes remain unchanged. |

## Requirements closed since Stage F

- m>1 derivative theorem — MGT1-TRACK1B-CLOSED
- SR derivative theorem (proved) — SR-DERIVATIVE-CLOSED
- General location-family theorem — LOCATION-FAMILY-TRACK3AB-CLOSED

The Stage-F verdict remains historical `LEVEL-4-PARTIAL`. Closing a later
scoped requirement does not rewrite its Stage-F row or its originating stage
decision.
