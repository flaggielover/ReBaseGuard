# Stage E — protocol clarifications, corrections and deviations

`STAGE_E_PROTOCOL.md` is frozen at sha256
`974487019f57c7c319b3bfafcdc20497ab6fca86834ad0d2245a694296ef23cc`. It has not
been edited and will not be.

**Deviations from the frozen protocol: none.** No hypothesis, endpoint, policy
definition, drift grid, margin or closure criterion has been changed. The items
below are (a) resolutions of genuine ambiguities in the frozen text and (b) one
implementation defect corrected at the pilot gate. All were settled **before any
confirmatory outcome existed**, and all are recorded here rather than made
silently.

---

## C1 — Which policy the calibration chain runs under (ambiguity resolved)

**The gap.** §7 fixes the calibration target (in-control run length = 250
observations on the calibration block), the procedure (bisection on `log h`) and
that the same `h` is shared by all policies. It does **not** name the reuse
policy the calibration chain itself runs under.

**Resolution.** Calibration runs under the **fresh control, `rho = 0`** — the
policy with no reuse feedback. A calibration that ran under a reuse policy would
make the shared threshold depend on the very thing being compared.

**Status:** a clarification, not a change. Recorded in `src/calibrate_e.py`.

## C2 — Warm-up length before an injection onset (parameter not frozen)

`WARMUP = 750` observations, i.e. **3 cycles at the calibration target ARL0 of
250**. Derived from the frozen calibration target, not from any observed
outcome. Adversarial check A10 tests sensitivity to it.

## C3 — E1 denominator: **implementation defect found and corrected at the pilot gate**

**The defect.** §10 defines `R_Delta = mean(tau_Delta) / mean(tau_0)` with
"`tau_0` from the in-control pass of the same policy". The first implementation
used the numerator = *delay from a mid-cycle injection onset to the next alarm*
and the denominator = *full in-control cycle length*. **These are different
quantities**, and their ratio is length-biased: the mean residual waiting time
from an arbitrary point exceeds the mean cycle length whenever cycle lengths are
over-dispersed.

**Evidence it is a defect, not an inconvenient result.** On the Task A pilot:

| quantity | value |
|---|---|
| mean in-control cycle length `E[L]` | 174.0 |
| `E[L^2] / (2 E[L])` (mean residual wait under a renewal model) | 217.8 |
| directly measured matched in-control wait at the same grid points | **240.7** |

The bias inflated every `R_Delta` by ~38% and produced the impossible-looking
`R_Delta > 1` for small steps — detection under a real shift appearing *slower*
than the no-shift baseline:

| condition | matched denominator | cycle-length denominator |
|---|---|---|
| STEP 0.5 | 0.951 | 1.316 |
| STEP 1.0 | 0.508 | 0.702 |
| STEP 2.0 | 0.157 | 0.217 |

**Correction.** The primary denominator is now the **identical measurement
procedure with magnitude 0 at the identical grid points** — a matched
in-control wait. This is within the frozen text ("from the in-control pass of
the same policy") and is the statistically matched reading of it.

**Both are reported.** The length-biased cycle-length version is retained in
every result file as `E1_R_delta_cyclelen_denominator`, so the correction can be
audited rather than taken on trust.

**Implementation correction, not scientific retuning.** It fixes a mismatch
between two measurement procedures. It was made before any confirmatory run, it
applies identically to every policy, and it cannot favour one policy over
another: all four policies are measured with the same corrected procedure.

## C4 — Number of injection events `k` (sizing, not frozen)

`k` is chosen per task so that the bootstrap's **block of 5 spans the
warm-up-induced dependence range**: consecutive injection passes share history
over `WARMUP = 750` observations, so `5 x spacing >= 750` is required for block
resampling to break that dependence.

| task | evaluation length | `k` | spacing | `5 x spacing` | covers warm-up |
|---|---|---|---|---|---|
| A electricity | 22,656 | 120 | 152.3 | 761 | **yes** |
| B air_quality | 4,496 | (set at its pilot) | — | — | — |
| C bike_sharing | 8,689 | (set at its pilot) | — | — | — |

This is a precision/validity decision driven by the dependence structure, not by
any observed effect. A9 tests replicate-count sensitivity.

## C5 — Bootstrap validity is reported, never assumed

Every interval carries `n_blocks_effective` and a `reliable` flag
(`n_blocks_effective >= 5`). Intervals below that threshold are emitted with an
explicit `UNRELIABLE` note and **must not be treated as calibrated**. Block
length is fixed at 5 by the protocol and is **not** tuned; where the design
cannot support a valid interval, that is reported as a methodological limitation
rather than repaired by enlarging the block until an interval looks acceptable.

---

## Standing constraints reaffirmed

* **No sample-efficiency claim.** The mixing convention draws the fresh block
  every cycle for every policy, so fresh-sample consumption is *identical*
  across policies. Stage E speaks of reference weighting / reuse intensity only.
* **"Alert burden", never "false-alarm rate"** — the un-injected streams contain
  real concept drift and are not stationary in-control processes.
* **`epsilon = 0.10` is an independently pre-specified Stage E practical
  margin**, justified by the measured serial dependence of these streams. It is
  **not** a continuation or relaxation of Stage C.1's `epsilon = 0.05`, which
  remains exactly as frozen in Stage C.1 and is reported here as a secondary
  analysis at every task and `Delta`.
* Pilot results live in `task_*_pilot.json` with `evidence_status: PILOT` and are
  never pooled with confirmatory results.
