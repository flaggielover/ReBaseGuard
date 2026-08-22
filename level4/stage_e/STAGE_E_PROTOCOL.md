# ReBaseGuard Level 4 — Stage E Protocol

**Semi-real / production-style external validation.**
Frozen before any Stage E monitoring outcome was generated. Nothing below may be
edited afterwards; the hash is recorded in `results/protocol_hash.json` and
re-verified by adversarial check A1.

---

## 0. Question

> Does the ReBaseGuard mechanism and its stability-aware mitigation remain
> operationally meaningful on realistic streaming data derived from real
> datasets, rather than only the frozen Gaussian toy model?

Stage E validates the **operational mechanism**, not the Gaussian theorem. The
external data are **not** required to satisfy `F'(0) = 1 − Gamma` or the Stage B
period-2 certificate; those are frozen-model results and are not tested here.
The pattern under test is:

    aggressive post-alarm reuse
      -> reference-state distortion / persistence
      -> degraded repeated-monitoring discrimination or stability

with a conservative ReBaseGuard-style policy reducing that degradation.

Stage E is **semi-real external validation, not deployment**.

---

## 1. Datasets and tasks (exactly three; frozen)

| Task | Dataset | Source | n | Chronology |
|---|---|---|---|---|
| **A** | Electricity / Elec2, `electricity-normalized` | OpenML id 151 (file 2419) | 45,312 | half-hourly, 1996-05-07 → 1998-12-05 |
| **B** | Air Quality | UCI id 360 | 8,991 usable | hourly, 2004-03 → 2005-04 |
| **C** | Bike Sharing (`hour.csv`) | UCI id 275 | 17,379 | hourly, 2011 → 2012 |

Full provenance in `notes/DATA_PROVENANCE.md`. Raw files are **not**
redistributed; only checksums and manifests are committed.

**Ordering.** Task A's `date` column is **not** globally monotone (five backward
jumps, all at day boundaries where `period` wraps). The authoritative order is
**file row order**; the integrity check is that `period` cycles 0..47. Tasks B
and C are verified strictly increasing in their own time index.

**Exclusion rules, fixed now.** Task B: rows where any used sensor channel or
the target equals the dataset's missing code `-200`, or is unparsable, are
dropped. No other rows are excluded from any task. **No outcome-dependent
dropping of rows, tasks, drift conditions or policies is permitted.**

---

## 2. Features, targets, frozen models

Chronological split, identical fractions for all three tasks:

    [ reference / train 30% ] -> [ calibration 20% ] -> [ evaluation 50% ]

| Task | Target | Features | Model |
|---|---|---|---|
| A | `class = UP` (binary) | period, day sin/cos, nswprice, nswdemand, vicprice, vicdemand, transfer | L2 logistic regression, IRLS, `lambda = 1` |
| B | `C6H6(GT)` (reference analyser) | 5 PT08 sensor channels, T, RH | ridge, `lambda = 1` |
| C | `log1p(cnt)` | season, yr, holiday, workingday, weathersit, temp, atemp, hum, windspeed, hour sin/cos, month sin/cos | ridge, `lambda = 1` |

Task C **excludes** `casual` and `registered`: they sum to `cnt` and would leak
the target.

**All model coefficients and all standardisation constants are fitted on the
reference block ONLY.** The model is frozen before the evaluation stream and is
**never refitted**, in particular never after any monitoring outcome is seen.

## 3. Monitored stream

Scalar residual `r_t = y_t − yhat_t` (for Task A the calibration residual
`y_t − phat_t`). The frozen scale `s` is the residual SD **on the reference
block only**. The detector sees

    z_t = (r_t − R_j) / s

where `R_j` is the current reference level. `s` is never recomputed.

## 4. Dependence — preserved, not removed

The residual streams are strongly autocorrelated and are **not** whitened.
Measured on the evaluation blocks before the freeze:

| Task | acf(1) | acf(24) | acf(168) | excess kurtosis (calib) |
|---|---|---|---|---|
| A | 0.718 | 0.167 | 0.059 | −0.71 |
| B | 0.832 | 0.487 | 0.288 | +4.51 |
| C | 0.792 | 0.716 | 0.780 | +0.31 |

Task C carries a strong weekly cycle (`acf(168) = 0.78`); Task B has heavy tails.
**The iid Gaussian theory does not apply to these streams and is not assumed.**
This is precisely why the detector is calibrated empirically per task (§7) and
why uncertainty uses a moving-block bootstrap (§10).

---

## 5. Drift injection

Injections are applied **at the residual level**, `r_t -> r_t + delta_t * s`,
which preserves the real covariate, noise and dependence structure exactly.
Every injection has known timing and magnitude.

| Condition | Definition |
|---|---|
| **IC** in-control | `delta_t = 0` throughout |
| **STEP** | `delta_t = Delta` for `t >= t_0`; `Delta ∈ {0.5, 1.0, 2.0}` |
| **GRAD** gradual | linear ramp `0 -> 1.0` over 200 observations from `t_0`, then held |
| **RECUR** recurring | `Delta = 1.0` on for 300, off for 300, repeating from `t_0` |

Injection onsets `t_0` are a deterministic grid across the evaluation stream:
`K` events spaced evenly, first at 10% and last at 90% of the stream, with
seeded jitter of ±5% of the spacing (seed family `20261101`). The grid is
**identical for every policy** (matched streams, §9).

## 6. Detector

Primary: **frozen-form CUSUM**, `k = 1/2`, two-sided, inclusive post-update
alarm — the Level 1–3 form, with only the threshold recalibrated per task.

Secondary (reported if it costs no extra campaign): Shiryaev–Roberts. **SR is
NOT required for Stage E closure**; Stage D already provides the two-detector
evidence and quota priority here is external validity.

## 7. Calibration

Per task, on the **calibration block only**:

* bisect the CUSUM threshold `h` so the in-control run length on the calibration
  residuals equals **ARL0 target = 250 observations**;
* tolerance `1e-3` in `log h`, at most 40 iterations;
* the **same `h` is used by every policy** within a task (§9);
* `h` is frozen before any evaluation-stream outcome is computed and is
  **never** adjusted afterwards.

Recorded per task: target ARL0, achieved ARL0, its uncertainty, the calibration
block indices, and the iteration trace. No future or evaluation data may be used.

## 8. Reuse policies

All policies differ **only** in post-alarm reference construction. On an alarm
at index `tau_j`:

    mu_reuse = mean of the last w = min(m, cycle length) residuals up to tau_j
    mu_fresh = mean of the m residuals AFTER tau_j   (a settling block)
    R_{j+1}  = rho * mu_reuse + (1 - rho) * mu_fresh

and the next cycle begins at `tau_j + 1 + m`. **Every policy consumes exactly
the same observations**, including the fresh settling block, in every cycle.

`m = 20` for all tasks.

| Policy | `rho` | Role |
|---|---|---|
| **P0 fresh** | 0.0 | control |
| **P1 full reuse** | 1.0 | the failure mode under test |
| **P2 ReBaseGuard** | **0.029796** | certificate-aware, inherited from Stage C (`delta = 0.2`, CONSERVATIVE, from the certified `Gamma` enclosure) |
| **P3 moderate** | 0.3 | **EXPLORATORY ONLY** |

P2 is **fixed before Stage E evaluation** and is not tuned here. It is
conservative at `m = 20`: `rho_c(m=20) = 0.308` from Stage D, and
`0.029796 << 0.308`.

**P3 is EXPLORATORY.** It may not be used for Stage E closure, may not be called
certified-safe, and may not be tuned on Stage E outcomes.

**No sample-efficiency claim (§16).** The mixing convention draws the fresh
block every cycle for every policy, so fresh-sample consumption is *identical*
across policies. Stage E therefore speaks of **reference weighting / reuse
intensity**, never of sample savings, data efficiency, or "X% fewer samples".

---

## 9. Fair comparison

Within a task, all policies share: the same residual stream, the same frozen
model and scale, the same threshold `h`, the same injection grid and magnitudes,
the same `m`, and the same observation availability. Only `rho` differs.

## 10. Endpoints and uncertainty

**Exactly four headline endpoints.**

| # | Endpoint | Definition |
|---|---|---|
| **E1** | baseline-normalised detection response | `R_Delta = mean(tau_Delta) / mean(tau_0)` per policy, `tau_0` from the in-control pass of the **same** policy |
| **E2** | reference-state error | `mean \|R_j − localmean_j\|`, where `localmean_j` is the mean of the injected stream over the 100 observations the cycle actually faces. **Measurement only — never an input to any policy.** |
| **E3** | repeated-monitoring alert burden | alarms per 1000 observations on the **un-injected** evaluation stream |
| **E4** | detection delay | observations from injection onset to the first alarm at or after it |

**E3 naming.** The un-injected stream contains *natural* drift, so E3 is an
**alert burden**, not a pure false-alarm rate. It is never called a false-alarm
rate in any Stage E artifact.

**Uncertainty.** Moving-block bootstrap over the time-ordered sequence of cycles
(E2, E3) or injection events (E1, E4), block length **5**, 10,000 resamples,
percentile intervals. Chosen because the outcome sequences inherit the streams'
serial dependence; a plain iid bootstrap would understate the intervals.

**Secondary diagnostics** (never used to rescue a failed primary criterion):
lag-1 reference ACF, alarm-direction alternation, reference-error persistence,
cycle-length distribution, recovery time, cumulative alerts, drift-response curve.

---

## 11. Hypotheses (frozen)

| ID | Hypothesis | Decision criterion |
|---|---|---|
| **H-E1** | full reuse creates larger persistent reference distortion than fresh or ReBaseGuard | E2(P1) > E2(P2) and E2(P1) > E2(P0), bootstrap CI of the difference excluding 0, in **>= 2 of 3** tasks |
| **H-E2** | ReBaseGuard reduces repeated-monitoring alert burden relative to full reuse | E3(P2) < E3(P1), CI of the difference excluding 0, in **>= 2 of 3** tasks |
| **H-E3** | ReBaseGuard is non-inferior to fresh in normalised detection responsiveness | `R_Delta(P2) / R_Delta(P0) − 1 <= epsilon` with **`epsilon = 0.10`**, upper 95% bootstrap bound, at **every** pre-specified `Delta`, in **>= 2 of 3** tasks |
| **H-E4** | full reuse discriminates in-control from shifted regimes worse than ReBaseGuard | `R_Delta(P1) > R_Delta(P2)` at `Delta = 1.0`, CI excluding 0, in **>= 2 of 3** tasks |
| **H-E5** | the qualitative Stage A/C mechanism appears in semi-real streams | H-E1 and (H-E2 or H-E4) both hold in the **same** task, in **>= 2 of 3** tasks |

**`epsilon = 0.10`, and why it differs from Stage C.1's 0.05.** Stage C.1 tested
an iid Gaussian synthetic stream. These streams are strongly autocorrelated
(`acf(1)` up to 0.83), heavy-tailed (Task B), and seasonal (Task C), so
replicate-level variability is materially larger. The margin is set once, here,
before any outcome. **The Stage C.1 margin `epsilon = 0.05` is also reported as a
secondary result at every task and `Delta`,** so the effect of this choice is
visible rather than hidden.

---

## 12. Decision rule (exactly three statuses; no fourth may be invented)

**`STAGE-E-CLOSED-EXTERNAL-VALIDATION`** if all hold:
1. `>= 2 of 3` tasks support the core mechanism (H-E5);
2. ReBaseGuard improves or preserves stability relative to full reuse (H-E1 and H-E2);
3. ReBaseGuard does not materially blind the detector (H-E3);
4. no major implementation or adversarial check fails;
5. all negative results retained.

**`STAGE-E-PARTIAL`** if: only one task strongly supports the mechanism; or task
conclusions conflict materially; or sensitivity is preserved but reference
stabilisation is inconsistent; or a task becomes unusable after the freeze.

**`STAGE-E-FAILED`** if: full reuse is not meaningfully worse in any task; or
ReBaseGuard systematically degrades detection; or the mechanism is
indistinguishable from ordinary calibration noise; or reproducibility /
adversarial checks fail.

---

## 13. Seeds

| Purpose | Root entropy |
|---|---|
| injection grid jitter | `20261101` |
| bootstrap resampling | `20261102` |
| adversarial rerun | `20261103` |

None appears in Level 1–3 or Stages A–D (prior seeds: `1234, 1729, 2024, 2026,
4242, 5150, 8080, 31337, 90210, 20260820-22, 20260901-02, 20260931, 20261001-02,
20261031`). Asserted by test.

## 14. Adversarial suite

A1 protocol hash unchanged · A2 seed/data split integrity · A3 no future-data
leakage · A4 fresh-control sanity · A5 detector calibration sanity · A6
full-reuse reproduction under rerun seed · A7 ReBaseGuard policy outcome-blind ·
A8 matched-stream comparison · A9 replicate-count sensitivity · A10 burn-in /
warm-up sensitivity · A11 drift-location sensitivity · A12 alternative valid
residual scaling · A13 dataset loader reproducibility · A14 figure/table
regeneration from machine-readable data.

Every check is reported pass or fail. **Any failure stays visible** and is
diagnosed in `notes/FAILURE_DIAGNOSES.md`. Tolerances are never widened after a
result is seen.

## 15. Execution order (quota conservation)

E0 audit + freeze → E1 Task A pilot → E2 Task B pilot → E3 Task C pilot →
full confirmatory runs only after all three pipelines pass sanity checks.
Smoke first, estimate runtime, freeze replicate counts, checkpoint, resumable.
If quota tightens: **all three tasks at moderate precision** beats one task at
extreme precision.

## 16. Forbidden

production-proven · industry-proven · universally robust · distribution-free ·
detector-independent · optimal · real-world deployment validated · any claim of
sample savings or data efficiency · promoting P3 to a closure result · calling
E3 a false-alarm rate · reopening Stage D theory absent a concrete contradiction.
