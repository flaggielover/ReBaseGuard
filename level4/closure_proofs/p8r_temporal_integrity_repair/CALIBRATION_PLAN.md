# P8R calibration plan — the single authoritative procedure

**Frozen at the temporal anchor.** Every count below is quoted from
`src/rebaseguard_p8r/config.py`; this document declares no budget of its own.
That is the point: P8's `G14` failed in part because its protocol prose stated
250,000 search cycles and 2,048,000 verification cycles while its executable and
every artifact used 163,840 and 1,024,000, and nothing in the campaign compared
the two. Gate `I13` compares them here, from the stored trace.

## 1. Scope

Calibration applies to **one** thing: the natural threshold `A_f` of the frozen
symmetric two-chart SR detector on the five non-Gaussian families, for which the
repository supplies no value.

* **CUSUM is never calibrated by P8R.** Its family thresholds are Stage-D D3's
  and are read at run time. `S3` re-measures the achieved `ARL_0` and reports the
  residual; that measurement is drawn from `PRODUCTION` addresses and cannot be a
  tuning input, because P8R does not own the thresholds.
* **Gaussian SR is never calibrated.** It keeps the frozen
  `A = 520.886133602749` and is only evaluated once on the holdout, so that the
  Gaussian anchor is measured on the same footing as the others. Its record is
  labelled `FROZEN_NOT_RECALIBRATED`.

Target: `ARL_0 = 465.50394`, read at run time from
`stage_d/results/d3_nongaussian.json`.

## 2. Address classes

| stage | class | batch region |
|---|---|---|
| search stage S1 | `CAL_SEARCH` | `CAL_S1_BATCH0 + 0 .. CAL_S1_ITERATIONS-1` |
| search stage S2 | `CAL_SEARCH` | `CAL_S2_BATCH0 + 0 .. CAL_S2_ITERATIONS-1` |
| frozen retry, stage RETRY_S2 | `CAL_SEARCH` | `CAL_RETRY_BATCH0 + 0 .. CAL_S2_ITERATIONS-1` |
| first acceptance test | `CAL_VERIFY_1` | `CAL_VERIFY_1_BATCH` |
| second acceptance test (retry only) | `CAL_VERIFY_2` | `CAL_VERIFY_2_BATCH` |
| everything scientific | `PRODUCTION` | see `PRODUCTION_PLAN.md` |

The classes are disjoint **by construction**, not by discipline: the class name
is part of the string SHA-256'd into the address's second component, so no two
classes can produce the same address for any value of the remaining components.
`RNG_ADDRESS_PLAN.md` gives the full argument;
`calibrate._search_stage` and `calibrate._verify` each call `require_class`, so a
search that tried to read a verification address raises `PermissionError` rather
than returning a number.

## 3. Search algorithm

Fixed-length, non-adaptive, in two stages.

```
thr <- SR_THRESHOLD_GAUSSIAN                       (the frozen Gaussian value)
prev <- none
stage S1:  exactly CAL_S1_ITERATIONS evaluations,
           CAL_S1_ROW_BLOCKS row blocks each
stage S2:  exactly CAL_S2_ITERATIONS evaluations,
           CAL_S2_ROW_BLOCKS row blocks each
return thr                                         (the last update's output)
```

Each evaluation measures `ARL_0(thr)` at its own `CAL_SEARCH` batch and then
applies the frozen **log-log secant** update:

```
beta    = log(ARL_i / ARL_{i-1}) / log(A_i / A_{i-1})     (beta = 1 initially)
beta    = clip(beta, CAL_BETA_MIN, CAL_BETA_MAX)
p       = 1.0  if  |ARL_i - target|/target > CAL_DAMP_SWITCH
        = CAL_DAMP_EXPONENT  otherwise
A_{i+1} = clip( A_i * (target/ARL_i)^(p/beta),
                A_i / CAL_CLIP_FACTOR,  A_i * CAL_CLIP_FACTOR )
```

Why a secant and not the plain proportional step P8 used: `ARL_0` is **not**
linear in the SR natural threshold `A` over the range the contaminated families
need. Measured on the pre-anchor scratch tree it behaves locally like `A^beta`
with `beta` near 0.47, so a proportional step undershoots by more than a factor
of two per iteration and would not reach the operating point within any
reasonable fixed iteration count. This is a statement about the shape of the
`ARL_0(A)` curve, established at scratch addresses no P8R result uses; it fixes
no verdict, no threshold and no estimand. It is disclosed in
`REPAIR_RATIONALE.md` §5.

Guards, all frozen: `beta` is clipped so a noise-driven slope cannot produce a
wild step; the whole multiplier is clipped again; and the damping exponent takes
over once the residual falls to the evaluation's own noise floor
(`CAL_DAMP_SWITCH`), where a full step would chase noise.

### What the search deliberately does not do

* **No early stop.** Both stages run their full iteration count regardless of
  what they see. A data-dependent stopping rule lets search noise decide when to
  stop, and an added phase is exactly what P8's amendment `A2` was.
* **No best-of selection.** The returned threshold is the iterate produced by
  the last update, not the iterate with the smallest observed residual.
  Selecting the best-observed evaluation would fit the search noise.
* **No look at any verification address.** Enforced at the call site.

`tests/test_calibration_protocol.py` asserts the first two by inspecting the
function body for `break`, `min` and `argmin`.

## 4. Acceptance

One evaluation on `CAL_VERIFY_1`, `CAL_VERIFY_ROW_BLOCKS` row blocks, at
`CAL_VERIFY_1_BATCH`. Accepted iff

```
|ARL_0(verify) - target| / target  <=  CAL_TOLERANCE
```

`CAL_TOLERANCE = 0.005` is numerically identical to P8's `G2` bound, so the
acceptance criterion is not weakened by the repair.

**Once `CAL_VERIFY_1` has been read for a family, that address is never read
again for that family, under any circumstances.** That is the specific thing P8
did and P8R does not.

## 5. The frozen retry ladder

Declared here, before results. If `CAL_VERIFY_1` rejects a family:

1. Stage `RETRY_S2` runs exactly `CAL_S2_ITERATIONS` further evaluations, from
   the rejected threshold, on the **pre-reserved** `CAL_RETRY_BATCH0` region of
   `CAL_SEARCH`. These are fresh addresses; no search address is reused either.
2. The result is accepted or rejected **once**, on `CAL_VERIFY_2` — a distinct
   address class reserved for exactly this purpose and never touched otherwise.
3. If `CAL_VERIFY_2` also rejects, the family's outcome is
   **`CALIBRATION_FAILED`**. There is no third attempt.

There are therefore exactly four admissible calibration outcomes:
`FROZEN_NOT_RECALIBRATED` (Gaussian), `ACCEPTED_VERIFY_1`, `ACCEPTED_VERIFY_2`,
`CALIBRATION_FAILED`.

## 6. What a `CALIBRATION_FAILED` family means

It is a **negative procedural outcome, reported as such**, not a cell to be
retuned until it passes.

* `experiments/thresholds.py` raises `CalibrationFailed` rather than
  substituting any value, so a failed calibration cannot leak into a production
  cell even by accident.
* Every SR production cell for that family is written with
  `status = "EXCLUDED_CALIBRATION_FAILED"` and its reason, so the exclusion is
  visible in the artifact rather than being an absence.
* `S5` resolves to `REJECTED` if any family ends `CALIBRATION_FAILED`.
* The affected cells are excluded from the questions that presuppose a
  calibrated threshold, and `RESULTS.md` states which questions those are and how
  many cells each lost.

## 7. What `I13` checks

`calibrate.executed_budget` re-derives, from the stored trace alone:

* the number of S1, S2 and retry evaluations actually run;
* the cycle count of each;
* the verification cycle count and the number of acceptance evaluations;
* the set of search batches and the set of verification batches;
* the set of address classes each stage touched.

`I13` fails if any of these disagrees with `calibrate.declared_budget`, which
reads `config` directly. A P8-style declared/executed divergence is therefore a
gate failure, not a footnote discovered by an adjudicator.
