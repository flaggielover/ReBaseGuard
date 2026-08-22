# ReBaseGuard Level 4 — Stage E Report

## Semi-real / production-style external validation

**Decision: `STAGE-E-PARTIAL`**

Protocol frozen at sha256
`974487019f57c7c319b3bfafcdc20497ab6fca86834ad0d2245a694296ef23cc` before any
monitoring outcome existed; re-verified unchanged after every campaign
(adversarial A1). Adversarial suite **14/14**. **No Stage A / B / C / C.1 / D or
Level 1–3 artifact was modified.**

---

## 1. Headline

Three semi-real streaming tasks were run under one frozen protocol. **The
pre-specified `>= 2 of 3` external-validation closure criterion was not met:
zero tasks satisfied H-E5.** Closure became mathematically unreachable after
Task B, and this was stated before Task C was run rather than after.

The picture is **heterogeneous**, and that is the result rather than a
shortfall in it:

* **Task A** gave decisive evidence that full reuse distorts the monitoring
  reference — and equally decisive evidence that this distortion did **not**
  translate into worse normalised discrimination.
* **Task B** was **LOW-POWER** and could demonstrate nothing about reference
  distortion, though ReBaseGuard was non-inferior to fresh at the primary margin.
* **Task C** produced the only supported discrimination result (H-E4) and the
  strongest apparent reference-distortion signal — but its reference-state and
  alert-burden endpoints fell **below the pre-specified reliability floor**, so
  that signal is not admissible evidence.

---

## 2. Tasks, data, usability

| | Task A | Task B | Task C |
|---|---|---|---|
| Dataset | Electricity / Elec2 | UCI Air Quality | UCI Bike Sharing |
| Source | OpenML id 151 | UCI id 360 | UCI id 275 |
| sha256 (data) | `2d86fbc74c69a5c0…` | `13277ae5d8581e80…` | `e03de4ee4ef4dc37…` |
| n (usable) | 45,312 | 8,991 | 17,379 |
| Split (train/calib/eval) | 13,594 / 9,062 / 22,656 | 2,697 / 1,798 / 4,496 | 5,214 / 3,476 / 8,689 |
| Frozen model | L2 logistic (IRLS) | ridge | ridge |
| Threshold `h` | 36.7136 | 32.1712 | 15.1996 |
| Achieved ARL0 | 256.1 [212.5, 299.7] | 245.6 [201.7, 287.0] | 260.2 [209.8, 325.1] |
| rel. error vs 250 | +0.0243 | −0.0177 | +0.0406 |
| Events `k` | 120 | 24 | 46 |
| **Usability** | **USABLE** | **USABLE, LOW-POWER** | **PARTIALLY USABLE AFTER FREEZE** |
| Effective blocks E1/E4 | 24 / 24 | 5 / 5 | 10 / 10 |
| Effective blocks E2/E3 | 23 / 23 | 5 / 5 | **2 / 2 — below floor** |

Full provenance, including the Elec2 ordering anomaly, is in
`stage_e/notes/DATA_PROVENANCE.md`.

### External-validity character of the streams

These streams are **not** the frozen Gaussian model, and were deliberately not
transformed into it:

| | Task A | Task B | Task C |
|---|---|---|---|
| residual ACF(1) | 0.718 | 0.832 | 0.792 |
| ACF(24) | 0.167 | 0.487 | 0.716 |
| ACF(168) | 0.059 | 0.288 | **0.780** |
| excess kurtosis | −0.71 | **+4.51** | +0.31 |
| calib → eval mean shift | 0.189 → — | 1.452 → — | 0.475 → **0.672** |

Consequences that are part of the result, not defects:

* Thresholds are far above the frozen `h = 5` (15.2–36.7) because serial
  dependence leaves far less independent information per observation.
* Task C's residual retains a strong **weekly** cycle: the frozen feature set
  has hour and month terms but no day-of-week term. This is model
  misspecification, it is frozen, and it stays visible.
* The natural streams already drift, so E3 is reported as an **alert burden**
  and never as a false-alarm rate.

---

## 3. Frozen hypothesis results by task

| | Task A | Task B | Task C |
|---|---|---|---|
| **H-E1** reference distortion | **SUPPORTED** | NOT SUPPORTED *(non-demonstration)* | **UNEVALUABLE** |
| **H-E2** alert burden | NOT SUPPORTED *(non-demonstration)* | NOT SUPPORTED *(non-demonstration)* | **UNEVALUABLE** |
| **H-E3** non-inferiority `eps=0.10` | NOT SUPPORTED *(non-demonstration)* | **SUPPORTED** | **SUPPORTED** |
| **H-E3** secondary `eps=0.05` | NOT SUPPORTED | NOT SUPPORTED | **SUPPORTED** |
| **H-E4** discrimination | NOT SUPPORTED *(**directional contradiction**)* | NOT SUPPORTED *(non-demonstration)* | **SUPPORTED** |
| **H-E5** core mechanism | NOT SUPPORTED | NOT SUPPORTED | NOT MET |
| **Counts toward `>=2/3`** | **No** | **No** | **No** |

`0 / 3` tasks support H-E5; `2` were required.

### Key numbers

**Task A — E2 reference-state error** (the one decisive mechanism result):
P1 full reuse `0.3330` vs P2 `0.2564` vs P0 `0.2447`.
`P1 − P2 = +0.0766 [+0.0369, +0.1135]`, `P1 − P0 = +0.0883 [+0.0498, +0.1326]`,
both excluding 0; `P2 − P0 = +0.0117 [−0.0273, +0.0610]`, not excluding 0.

**Task C — H-E4 discrimination**: `R(P1) − R(P2) = +0.0470 [+0.0062, +0.1266]`,
excluding 0. The only supported discrimination result in Stage E.

**Task C — H-E3**: `R(P2)/R(P0)` between `0.987` and `1.008` at all five
conditions, upper-95% excess `<= +0.0263` — ReBaseGuard tracks fresh almost
exactly on this stream.

---

## 4. Negative, null and contradictory results — all retained

1. **Reference distortion does not imply worse discrimination.** Task A is the
   clean case: full reuse degrades the reference decisively (H-E1), yet
   normalised discrimination is unchanged, and H-E4's point estimate is
   `−0.0141`, i.e. the **opposite sign** to the hypothesis. This is a
   **directional contradiction**, not merely a wide interval, and it is the
   single most important negative finding in Stage E.
2. **H-E4's sign is not stable across streams**: `−0.0141` (A), `+0.0528` (B),
   `+0.0470` (C, significant). The mechanism's discrimination consequence is
   stream-dependent.
3. **E4 raw delays reverse between tasks.** Full reuse detected *faster* than
   fresh throughout Task A (STEP 1.0: 116.6 vs 122.2) and *slower* in Tasks B
   and C (78.8 vs 63.0; 57.5 vs 26.3). A short raw delay is not better
   discrimination when the same policy also alarms rapidly without drift.
4. **Task A fails H-E3 while every point estimate favours P2.** The excess is
   negative at all five conditions; only interval width causes the failure.
   This is **failure to demonstrate non-inferiority, not demonstrated
   inferiority**, and it remains recorded as FAILED.
5. **Task B is LOW-POWER**; its three failures are all statistical
   non-demonstration with the predicted sign. At this power a non-significant
   result is not evidence of no effect — and the frozen criteria stay failed.
6. **Task C's strongest-looking signal is inadmissible.** Its E2 point
   estimates (P1 `0.4315` vs P0 `0.2397`) and alert burden (P1 `1.97` vs P0
   `1.05` per 1000) are the largest apparent mechanism effects observed
   anywhere in Stage E, and they are **UNRELIABLE** — 2–3 effective blocks
   against a floor of 5. They are excluded from every hypothesis. The
   reliability gate was applied against the most favourable-looking data in the
   stage.
7. **Natural nonstationarity can dominate the injected effect.** Task C's
   in-control cycles ran to 932.7 observations against a calibrated ARL0 of
   260, because the evaluation block is a different regime from the calibration
   block.
8. **P3 (EXPLORATORY) does not replicate.** Best on E2 and burden in Task A,
   worst at STEP 1.0 in Task B (`R = 0.301` vs P2's `0.153`). It is excluded
   from every closure statement and is not proposed as a method.

---

## 5. Adversarial suite — 14/14

| ID | Check | Result |
|---|---|---|
| A1 | protocol hash unchanged | PASS |
| A2 | seed families disjoint; splits contiguous | PASS |
| A3 | no future-data leakage | PASS |
| A4 | fresh-control sanity | PASS |
| A5 | calibration sanity (calibration block only, within 5%) | PASS |
| A6 | full reuse reproduces on an independent grid seed (20261103) | PASS |
| A7 | P2 `rho` is the frozen Stage C constant; no outcome hard-coded | PASS |
| A8 | matched streams: only `rho` differs | PASS |
| A9 | replicate-count sensitivity (halved) | PASS |
| A10 | warm-up sensitivity (750 → 400) | PASS |
| A11 | drift-location sensitivity (early vs late) | PASS |
| A12 | alternative valid residual scaling (MAD vs SD) | PASS |
| A13 | loader reproducibility and checksums | PASS |
| A14 | figures regenerate from results JSON only | PASS |

A6 matters most: Task A's corrected pilot ran at the full confirmatory design,
so its confirmatory run reproduces bit-identically and is **not statistically
independent of its pilot**. A6's independent grid seed supplies the replication
that comparison cannot.

---

## 6. Protocol deviations

**Deviations from the frozen protocol: none.** No hypothesis, endpoint, policy,
drift grid, margin or closure rule was changed at any point. Recorded in
`stage_e/notes/PROTOCOL_DEVIATIONS.md`:

* **C1** — calibration policy ambiguity resolved explicitly to the fresh
  control `rho = 0` (the frozen text fixed the target but not the policy).
* **C2** — warm-up fixed at 750 observations = 3 cycles at the frozen ARL0
  target; A10 tests sensitivity.
* **C3** — **implementation defect corrected at the Task A pilot gate**: the E1
  denominator was length-biased (mean residual wait `240.7` vs mean cycle
  length `174.0`), inflating every `R_Delta` by ~38% and producing impossible
  `R_Delta > 1` values. Replaced by a matched in-control wait at identical grid
  points; the length-biased quantity is retained in every result file as
  `E1_R_delta_cyclelen_denominator` for audit.
* **C4** — `k` sized per task so the bootstrap's block of 5 spans the warm-up
  dependence range (`5 x spacing >= 750`).
* **C5** — bootstrap validity is reported, never assumed; block length was
  never tuned.

---

## 7. Strongest defensible claim

> Across three semi-real streaming tasks, the external-validation picture was
> heterogeneous. Aggressive post-alarm reuse produced clear and statistically
> decisive reference-state distortion in one task (Electricity), directional
> but low-power evidence in another (Air Quality), and its strongest apparent
> effect in a third (Bike Sharing) on endpoints that fell below the
> pre-specified reliability floor and were therefore excluded. Normalised
> discrimination effects varied by stream: full reuse was significantly worse
> than the certificate-aware policy in one task, indistinguishable in another,
> and marginally better in a third. The certificate-aware ReBaseGuard policy
> was non-inferior to fresh re-baselining at the pre-specified practical margin
> in two of three tasks and was never shown to degrade detection. **The
> pre-specified `>= 2 of 3` external-validation closure criterion was not met.**

## 8. Claims explicitly ruled out

* ❌ external validation succeeded across `>= 2` tasks — it did not; 0 of 3.
* ❌ production validation, real-world deployment validation — Stage E is
  semi-real offline evaluation.
* ❌ universally robust, distribution-free, detector-independent, optimal.
* ❌ full reuse universally degrades discrimination — Task A contradicts this
  directionally.
* ❌ ReBaseGuard is externally validated in general.
* ❌ any sample-efficiency, sample-savings or data-efficiency claim: every
  policy consumes the fresh settling block every cycle, so fresh-sample
  consumption is **identical** across policies by construction.
* ❌ E3 described as a false-alarm rate.
* ❌ `epsilon = 0.10` read as a continuation or relaxation of Stage C.1's
  `epsilon = 0.05`; it is an independent Stage E practical margin, and the
  `0.05` secondary is reported unchanged at every task and condition.

## 9. Open questions

1. Whether reference distortion produces a discrimination penalty under any
   stream regime — Task A says no, Task C says yes, and nothing here separates
   the conditions.
2. Why full reuse detects faster on one stream and slower on two others.
3. Whether an evaluation design exists that supplies adequate cycle counts for
   E2/E3 on short streams without violating the dependence-coverage rule.
4. Whether the ReBaseGuard advantage would appear at reuse intensities between
   `rho = 0.0298` and `rho = 1` — untested here by design.
5. Whether Task C's weekly residual structure, an artifact of a frozen and
   misspecified feature set, drives its distinctive behaviour.

---

## 10. Summary table

| Task | Full reuse | ReBaseGuard | Fresh | Core mechanism supported? |
|---|---|---|---|---|
| **A — Electricity** | worst reference error (`0.3330`), highest alert burden (`5.55`), fastest raw delay | reference error `0.2564`, indistinguishable from fresh | reference error `0.2447`, lowest burden (`5.15`) | **No** — H-E1 supported, but H-E4 directionally contradicted |
| **B — Air Quality** | largest reference error (`1.1349`) and burden (`5.70`), slowest delay — none significant | non-inferior to fresh at `eps=0.10` at all five conditions | reference error `1.0201` | **No** — LOW-POWER; nothing demonstrable |
| **C — Bike Sharing** | significantly worse normalised response (H-E4 met); largest apparent E2/E3 but **UNRELIABLE** | tracks fresh almost exactly; non-inferior at both margins | reference error `0.2397` *(unreliable)* | **No** — H-E1/H-E2 UNEVALUABLE |

**`0 / 3` tasks supported H-E5; `2` were required. Stage E: `STAGE-E-PARTIAL`.**
