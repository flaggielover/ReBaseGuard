# ReBaseGuard Level 4 — Stage D Report

**Decision: `STAGE-D-PARTIAL`**

Stage D asked whether the stopped-selection mechanism established for the frozen
CUSUM at `m = 1` survives three generalisations: a second detector (D1), longer
stopped windows (D2), and non-Gaussian innovations (D3). It does so **in part**.
Two pre-specified criteria did not hold — one estimator-level failure and one
substantive negative result — and both are reported as failures rather than
repaired.

* Protocol frozen at sha256 `925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e`
  before any confirmatory data existed; re-verified unchanged after every
  campaign (adversarial A12).
* Confirmatory seed family `20261001`; independent replication family
  `20261002`. Neither appears anywhere in prior work.
* Adversarial suite: **12/12** (A11 failed on first run; diagnosed and fixed —
  see below).
* **No frozen Stage A / B / C / C.1 or Level 1–3 artifact was modified.**

---

## 1. Four levels of evidence

Stage D produced nothing rigorous. The separation below is load-bearing and is
maintained everywhere in this report.

### 1.1 RIGOROUS-CERTIFIED — inherited, not produced here

| Result | Source | Used in Stage D as |
|---|---|---|
| `F_1'(0) = 1 − Gamma` (score identity) | Level 2C, Lean-checked, `FROZEN-PROVED` | the identity D2.3 tests at `m > 1` |
| `Gamma_CUSUM ∈ [3.9243482, 27.8493821]` | Level 1–3 Arb certificate | adversarial A10 consistency check |
| unique root of `F_1(e)+e` in `[1.028724, 1.044724]`, multiplier in `[0.1081, 0.8325]` | Stage B, `RIGOROUS-CERTIFIED` | the enclosure D1.4's CUSUM arm is checked against |

**Stage D adds nothing to any of these and extends none of them.** In
particular the Stage B certificate is **not** transferred to the SR detector.

### 1.2 CONFIRMATORY-NUMERICAL — produced here, Monte Carlo

| Result | Value | Gate |
|---|---|---|
| SR ARL0-matched to the frozen CUSUM | `A = 520.886134`, ARL0 `465.294 ± 0.360` vs `465.504 ± 0.726` | D1.1 |
| `Gamma_SR` at `m = 1` | `17.3198 ± 0.0280` | D1.2 |
| SR excess over CUSUM at matched ARL0 | `+1.4746 ± 0.0400` | D1.3 |
| `Gamma_m` crossing bracket | `m* ∈ [50, 75]`, ends at `+108.6` / `−14.5` SE | D2.2 |
| Wald's second identity | `E[T_tau^2] / ARL0 = 0.99960` | D2.1 |
| `Gamma_infinity = E[T_tau^2/tau]` | `1.4037 ± 0.0013` | D2.4 |
| `Gamma_psi > 2`, six families, ARL0-matched | 6/6 under the frozen estimand | D3.2 |

### 1.3 CANDIDATE — Monte Carlo, not certified

| Result | Value |
|---|---|
| SR symmetric period-2 candidate | `e* = 1.036719 ± 0.001496` |
| CUSUM candidate (replication of Stage B by simulation) | `e* = 1.036719 ± 0.001496`, interval inside the certified enclosure |

The two roots are numerically identical **because bisection landed in the same
cell**, not because two independent estimates coincided. The reported
uncertainty is resolution-limited: the bisection cell (`0.001562`) is wider than
the Monte Carlo `2σ` (`0.001302`).

### 1.4 FAILED / AMBIGUOUS / DIAGNOSTIC-ONLY

| Item | Status |
|---|---|
| **D2.3** derivative correspondence | **FAILED**, 0/8 at the primary step |
| **D2.5** operational consequence of the crossing | **MATHEMATICAL, NOT OPERATIONAL** — a negative result |
| **D3 t3** under the two estimands | **AMBIGUOUS** |
| naive Gaussian-form `Gamma_T` | **DIAGNOSTIC ONLY**, never evidence |
| assumptions A1, A4 | **UNPROVED** |
| D4 stability map | **NOT RUN** — gate not met |

---

## 2. Every frozen criterion

| ID | Criterion | Status | Value |
|---|---|---|---|
| D1.1 | SR ARL0-matched, `\|ratio−1\| <= 0.01` | **PASS** | rel err `−0.00045 ± 0.00174` |
| D1.2 | lower 95% bound of `Gamma_SR` > 2 | **PASS** | `17.2649` |
| D1.3 | CI for `Gamma_SR − Gamma_CUSUM` excludes 0 | **PASS** | `+1.4746` CI `[+1.3963, +1.5529]` |
| D1.4 | SR period-2 candidate or NO-CANDIDATE | **CANDIDATE** | `e* = 1.036719 ± 0.001496` |
| D2.1 | `gamma_i` decay (descriptive) | **DESCRIPTIVE** | `gamma_0 = 15.8544`; Wald ratio `0.99960` |
| D2.2 | crossing bracket, both ends > 3 SE | **PASS** | `[50, 75]`, `+108.6` / `−14.5` SE |
| D2.3 | FD of the **actual** induced map = `1 − Gamma_m` within 3 combined SE | **FAIL** | 0/8 at `h = 0.05` |
| D2.4 | `Gamma_m -> Gamma_inf < 2` (numerical) | **NUMERICAL** | `1.4037 ± 0.0013` |
| D2.5 | crossing predicts an operational change | **MATHEMATICAL, NOT OPERATIONAL** | 0/4 metrics peak at `m*`; 4/4 monotone |
| D3.1 | assumptions written and labelled before simulation | **PASS** | A1, A4 marked UNPROVED |
| D3.2 | per family, lower bound of `Gamma_psi` vs 2 | **PASS** | 6/6 frozen; 5/6 normalised |
| D3.2-t3 | t3 under the two estimands | **AMBIGUOUS** | `2.5980` PASS vs `1.2990` FAIL |
| D3.3 | naive `Gamma_T` diagnostic only | **PASS** | never used as evidence |
| D4 | stability map | **NOT RUN** | gate requires D2 to survive |

---

## 3. D2.3 — the failure, and why it stays a failure

`0/8` grid points agreed within 3 combined SE at the pre-committed primary step
`h = 0.05`. Discrepancies ran from `+0.798` (17.0 SE) at `m = 1` to `+0.033`
(7.3 SE) at `m = 100`.

**Diagnosis (predicted in advance, `7b7a54c6…`).** The discrepancy is one-signed
and shrinks at observed order **`p = 1.938`** against the exact central-difference
value 2; Richardson extrapolation matches `1 − Gamma_m` within **0.40 SE at every
`m`**. This is `O(h^2)` truncation of a steep map (`F'(0) ≈ −14.9` at `m = 1`),
not a refutation of the identity.

**It remains FAILED.** Re-running at a smaller step and presenting that as the
primary result would be re-tuning an estimator after seeing a `Gamma`, forbidden
by protocol §8. The identity `F'_{rho,m}(0) = rho(1 − Gamma_m)` is therefore
**unconfirmed at Stage D for `m > 1`** — consistent with, but not established by,
this evidence. Richardson agreement is numerical extrapolation and is not
promoted to a result.

A separate consistency check at `m = 1` did measure the map slope directly:
`F'(0) = −16.23 ± 0.11` (SR) and `−14.91 ± 0.11` (CUSUM), each matching its own
`1 − Gamma` within `0.86` and `0.60` SE, with slope separation `+1.315 ± 0.150`
against the `Gamma` gap `+1.475 ± 0.040`. This is reported as a consistency
check, **not** as a substitute for D2.3.

---

## 4. D2.5 — the negative result

**The `Gamma_m = 2` crossing has no observable operational counterpart.**

At `rho = 1`, 20,000 replicates, `m*` interpolated at `72.19`:

| m | side | ARL | MSE | eACF1 | dirACF1 | R_0.5 | R_1.0 |
|---|---|---|---|---|---|---|---|
| 10 | below | 100.41 | 0.2936 | −0.585 | −0.879 | 1.169 | 0.394 |
| 20 | below | 156.35 | 0.1461 | −0.554 | −0.817 | 0.727 | 0.119 |
| 50 | below | 261.27 | 0.0692 | −0.398 | −0.610 | 0.256 | 0.053 |
| 65 | below | 286.95 | 0.0592 | −0.352 | −0.547 | 0.213 | 0.048 |
| **75** | **above** | 299.13 | 0.0551 | −0.335 | −0.516 | 0.185 | 0.046 |
| 90 | above | 314.12 | 0.0512 | −0.308 | −0.478 | 0.178 | 0.044 |
| 100 | above | 322.05 | 0.0492 | −0.297 | −0.456 | 0.172 | 0.042 |

**0 of 4** metrics show their steepest change across `m*`; **4 of 4** are
monotone in `log m`. The steepest change is always elsewhere — in `[10,20]`,
`[20,50]` or `[50,65]`.

**Alarm alternation persists above the crossing.** At `m = 100`, where
`Gamma_m = 1.776 < 2` and full reuse is locally *stable* at `e = 0`, the lag-1
alarm-direction ACF is still `−0.456`.

**What `m*` actually is.** `Gamma_m = 2` is exactly `rho_c = 1`: the point at
which full reuse ceases to be locally unstable **at the fixed point `e = 0` of
the deterministic conditional-mean skeleton**. It is a local-stability boundary
of that skeleton. Nothing in the frozen protocol asserts that such a boundary
must produce a discontinuity in the stationary behaviour of the noisy chain, and
the data show it does not. This is stated as a limitation of what the boundary
means, not as a defect of the measurement, and **no phase-transition narrative
is constructed from monotone curves.**

This contradicts an operational reading of the pilot's `m* ≈ 72` headline. The
contradiction is the result.

---

## 5. D3 — non-Gaussian

All six families ARL0-matched to the frozen Gaussian CUSUM before any `Gamma`
was computed.

| family | h | ARL0 | `Gamma_psi` | frozen | `E[psi']` | `Gamma_psi/E[psi']` | normalised | naive `Gamma_T` |
|---|---|---|---|---|---|---|---|---|
| gaussian | 5.0000 | 465.60 | `15.8671 ± 0.0403` | PASS | 1.0000 | 15.8671 | PASS | 15.8671 |
| t10 | 5.2345 | 466.57 | `11.9938 ± 0.0360` | PASS | 1.0577 | 11.3396 | PASS | 19.9203 |
| t5 | 5.6695 | 464.87 | `7.1890 ± 0.0320` | PASS | 1.2500 | 5.7512 | PASS | 33.8362 |
| **t3** | 6.3370 | 465.89 | `2.5980 ± 0.0271` | PASS | 2.0000 | **1.2990** | **FAIL** | 99.5586 |
| contam0.05 | 7.6717 | 465.74 | `5.7572 ± 0.0246` | PASS | 0.8833 | 6.5182 | PASS | 46.8949 |
| contam0.1 | 9.3820 | 464.36 | `5.0474 ± 0.0204` | PASS | 0.7961 | 6.3405 | PASS | 59.2507 |

**The t3 ambiguity is preserved, not resolved.** The protocol froze
`Gamma_psi` without the `E[psi']` normalisation. If the reference is
re-estimated from the stopped window by the M-estimator with score `psi` — the
natural generalisation of the Gaussian sample mean — its influence function is
`psi / E[psi']`, so the stability boundary is `Gamma_psi / E[psi'] = 2`. The two
coincide **only for the Gaussian**. At `t3` they disagree across the threshold:
frozen criterion **PASS** (`2.5980`, lower bound `2.5449`), stability-normalised
**FAIL** (`1.2990`, lower bound `1.2725`). This was recorded as assumption A5
before any D3 data existed, including the prediction that normalisation would
move the t-families and the contaminated families in **opposite** directions —
which it did. **t3 is classified AMBIGUOUS.** Neither estimand is selected for
being more convenient.

**D3.3 — the naive statistic is a warning, and an informative one.** The naive
Gaussian-form `Gamma_T` reads `99.5586` at t3 where the correct score-based
value is `2.5980` — a factor of 38. This is direct evidence that **the Gaussian
stopped-sum identity cannot simply be exported to heavy-tailed families**: using
`T_tau` in place of the score sum does not merely lose efficiency, it produces a
number with no bearing on the stability question. `Gamma_T` is never used as
evidence for any claim.

**Scope.** D3 establishes **numerical robustness across six tested families**
and nothing wider. Assumption A1 (differentiation under the expectation) is
**UNPROVED for every non-Gaussian family**, and A4 is UNPROVED with a check too
low-powered to speak either way. **No general location-family theorem is
claimed; its proof obligations are not closed.**

---

## 6. Adversarial suite — 12/12

| ID | Check | Result |
|---|---|---|
| A1 | independent seed family `20261002` reproduces `Gamma_m` | PASS |
| A2 | CRN on/off: SR−CUSUM excess keeps sign and magnitude | PASS |
| A3 | batch bootstrap and normal CI agree at every `m` | PASS |
| A4 | FD discrepancy shrinks at `O(h^2)` (the D2.3 *diagnosis*) | PASS |
| A5 | `Gamma_SR` stable under threshold recalibration uncertainty | PASS |
| A6 | `m*` insensitive to interpolation method | PASS |
| A7 | convention B equals the lag decomposition; convention A does not | PASS |
| A8 | `tau < m` edge cases handled and drive the A/B divergence | PASS |
| A9 | 4M-cycle run agrees with the 2M primary | PASS |
| A10 | `Gamma` at `m = 1` inside the Stage B certified enclosure | PASS |
| A11 | no measured outcome hard-coded in executable source | **FAILED first run**, fixed, PASS |
| A12 | frozen protocol hash still matches | PASS |

**A4 validates the D2.3 diagnosis; it does not convert D2.3 into a pass.**

**A11** initially failed because the checker matched its own list of values to
search for. The literal list was replaced by values **derived from the results
files**, and the checker exempted from its own scan; the rewritten guard scans
more values than before, so it is stricter. No threshold moved. Both runs are
recorded in `notes/FAILURE_DIAGNOSES.md`.

---

## 7. The window-convention audit

Stage A's simulator applies a **minimum dwell** (`if m > 1 and step < m:
continue`), so its stopping rule is `tau_m = inf{t >= m}` and its reuse window
always holds exactly `m` observations. The Stage D blueprint explicitly rejected
the dwell because it changes the frozen stopping rule, and Stage D follows the
blueprint: frozen `tau`, truncated window `w = min(m, tau)` (convention A).

**Consequence:** Stage A and Stage D define **different maps for `m > 1`** and
their `m > 1` numbers are not comparable. They agree exactly at `m = 1`, so the
cross-stage checks at `m = 1` remain valid.

The blueprint's closed form `Gamma_m = (1/m) sum_i gamma_i` is **FALSE** under
convention A (refuted at 152 SE at `m = 250`) and true **by construction** for
convention B. The blueprint is internally inconsistent here: it asserts both
that form and `Gamma_m -> E[T^2/tau] = 1.406`, which cannot both hold since
`sum_i gamma_i = E[T_tau^2] = ARL0` is finite. `sum_i gamma_i = E[T_tau^2] =
ARL0` itself **reproduces** (ratio `0.99960`).

---

## 8. Strongest defensible claims

1. Under a matched reuse protocol and matched `ARL0`, a **second detector**
   (symmetric two-chart Shiryaev–Roberts) exhibits the same strong
   stopped-selection feedback as the frozen CUSUM, with a **larger** stopped
   gain: `Gamma_SR = 17.3198 ± 0.0280` against `15.8452 ± 0.0285`, difference
   `+1.4746 ± 0.0400`. This is **two-detector replication**, not
   detector-independence.
2. The stopped gain **decreases monotonically in the window length `m`** and
   crosses the `rho_c = 1` boundary inside a tightly bracketed interval,
   `m* ∈ [50, 75]`, with both ends significant at `+108.6` and `−14.5` SE.
3. `sum_i gamma_i = E[T_tau^2] = ARL0` **reproduces** (ratio `0.99960`), and
   `Gamma_m -> E[T_tau^2/tau] = 1.4037 ± 0.0013 < 2` numerically.
4. Across six ARL0-matched innovation families the score-based stopped gain
   exceeds 2 under the frozen estimand (6/6), and under the stability-normalised
   estimand in 5 of 6 — **numerical robustness, not distribution-free theory**.
5. The naive Gaussian-form statistic **fails badly** off-Gaussian (`99.56` vs
   `2.60` at t3), which is positive evidence that the Gaussian stopped-sum
   identity must not be exported to heavy-tailed families without the correct
   score.

## 9. Claims explicitly ruled out

* ❌ "detector-independent" — two detectors is replication.
* ❌ "distribution-free", "universal", "robust in general" — six families is not
  a class of distributions.
* ❌ Any Stage D result described as "certified" or "proved" — all Monte Carlo.
* ❌ `m*` as an **operational** phase transition — D2.5 refutes this directly.
* ❌ `F'_{rho,m}(0) = rho(1 − Gamma_m)` as **confirmed** at `m > 1` — D2.3 failed.
* ❌ A general location-family theorem — A1 is UNPROVED for every non-Gaussian
  family.
* ❌ Transfer of the Stage B certificate to SR.
* ❌ Any claim resting on `Gamma_T`.
* ❌ "first stability boundary", "repeated SR is novel" (novelty firewall).

## 10. OPEN questions

1. **A1** — differentiation under the expectation for non-Gaussian location
   families; the binding obstacle to any general theorem.
2. **D2.3 at `m > 1`** — confirming `F'_{rho,m}(0) = rho(1 − Gamma_m)` with an
   estimator that does not suffer `O(h^2)` truncation (e.g. a score-based
   derivative estimator, which needs its own pre-registration).
3. **The t3 estimand question** — which of `Gamma_psi` and `Gamma_psi/E[psi']`
   is the right boundary object, a modelling question the protocol did not fix.
4. **Why alternation persists above `m*`** — what governs the stochastic chain's
   alternation, given it is not the skeleton's local stability.
5. **A rigorous SR certificate** — would require an Arb enclosure like Stage B's;
   not started, and D1.4 does not substitute for it.
6. **The noisy recursion's invariant law** — `OPEN` since Stage B.
7. **A4** — square-integrability of the stopped score sum.
