# P9 experiment protocol — and an honest temporal-integrity disclosure

## 0. Temporal integrity — read this first

P9 has **no** frozen preregistration, because P9 has no frozen definition
(`P9_DEFINITION_AUDIT.md` §2). The protocol below therefore records what was
actually pre-committed and what was not. Getting this wrong is exactly the
defect P3 was flagged for (`P3-LIM1`) and P6R was flagged for, so P9 states it
plainly rather than presenting a protocol as if it had been frozen first.

| item | pre-committed? | evidence |
|---|---|---|
| scope of P9 (`P9_DEFINITION_AUDIT.md` §7) | **YES** — written before any computation | it is the first artifact in the namespace; its §7.1 declares the theorem target *provisionally*, before the audit |
| theorem-target decision | **YES, provisionally** | §7.1 explicitly allows `THEORY.md` to withdraw it |
| A1–A3 tolerances (`1e-9`, `1e-12`) | **YES** | hard-coded in `experiments/reproduce_anchors.py` before execution |
| seed derivation rule | **YES** | `seed_for()` is deterministic SHA-256 over label fields; no seed was chosen by hand at any point |
| A4–A6 comparisons | **NO threshold pre-set** | reported as **descriptive** comparisons against published P7 values, with standard errors. No pass/fail line was drawn in advance, so none is drawn now. |
| `CLOSURE_GATES.md` | **NO** — written **after** the anchors ran | disclosed here and in that file |

**Consequence, stated so it cannot be quietly dropped:** A4, A5 and A6 are
*descriptive reproductions*, not tests against preregistered thresholds. P9's
closure gates (`CLOSURE_GATES.md`) are consequently written to be
**verifiable-by-inspection artifact properties** (schema validity, acyclicity,
quarantine, protected tree) rather than post-hoc numerical thresholds that P9
could have tuned to its own results. Gates of the second kind would be
worthless here and are deliberately absent.

## 1. What P9 computed, and why each anchor was chosen

P9 ran **no discovery experiment**. Every computation is a reproduction or a
consistency check of an existing claim.

| anchor | claim exercised | why this one |
|---|---|---|
| A1 | `P3-X1` | exact, so any deviation is a coding error, not noise — a clean correctness probe of the boundary algebra |
| A2 | `P3-N1`, `P3-N2` | validates the P1/P2 → P3 edge without re-running P1/P2's `10^6`-path campaigns |
| A3 | `P5-T1` | the single most load-bearing exact claim; everything downstream (`P5-T7`, `P5-MECH`, `P7-A`, `P9-T2`) rests on it |
| A4 | `P7-E1`, `P7-E2` | the operational headline; the one an external reader is most likely to check |
| A5 | `P9-N1` (new) | arose from investigating an A4 cell rather than accepting a mismatch |
| A6 | `P9-T2`, `P7-A` premise | the only computation supporting a P9-owned theorem, plus a direct test of a premise P7 assumed |

## 2. Model, factors, sizes

Frozen model exactly as in `CROSS_PRIORITY_REPRODUCTION.md`. Factors:
detector `{CUSUM, SR}` × `m in {1,5}` (A3 adds `m=2`) × `rho in {0,1}`
(A3 adds `0.25`).

| anchor | paths | replication unit |
|---|---:|---|
| A1, A2 | — | exact arithmetic |
| A3 | 4000 × 18 cells | per-path algebraic residual |
| A4 | 12000 paths × 12 cycles | **per path**, averaged over cycles 2–12 |
| A5 | 12000 paths × 20 cycles | per path, by cycle index |
| A6 | 2500 paths × 81 grid nodes × 4 cells | per path within a node |

## 3. Estimands and uncertainty

* **Replicate-level uncertainty.** A4's standard errors are computed **across
  paths** on the per-path cycle mean, not across pooled cycles. Cycles within a
  path are dependent (that is the entire phenomenon), so pooling cycles as if
  independent would understate the SE. This is the one statistical choice that
  materially affects the reported intervals.
* **A6** SEs are across paths within a grid node; the mixture's own quadrature
  error is **not** quantified, which is why A6 is reported as *agreement*, not
  as an identity check.
* **No multiple-comparison correction is applied**, because no hypothesis test
  is performed. A4/A5/A6 report point estimates with SEs and are interpreted
  descriptively. Reporting a corrected p-value for a reproduction would imply a
  testing frame that does not exist here.

## 4. Amendment policy

Any change to `experiments/*.py` after this file was written must be recorded
in `RESULTS.md` with its motivation. One such change occurred and is recorded:
the A6 quadrature was changed from 21-node Gauss-Hermite to an 81-point
half-grid **after** the first attempt returned `134.19` against a measured
`82.08`. The motivation was diagnosed and is reported in
`CROSS_PRIORITY_REPRODUCTION.md` §A6 and `STATISTICAL_AUDIT.md`: `A(e)` falls
from `468` to `10.35` within one standard deviation and 21 nodes cannot resolve
it. The discarded first attempt is reported rather than deleted.

## 5. Negative-result interpretation

If a reproduction had failed, P9's rule — fixed before A4 ran, and exercised in
practice at A4 and A6 — is: **investigate the mechanism, report both numbers,
and classify in `DISCREPANCY_REGISTER.md`.** Do not adjust the reproduction
until it matches. Both `D-11` and `D-12` were handled this way, and the A6
quadrature failure was retained in the record.
