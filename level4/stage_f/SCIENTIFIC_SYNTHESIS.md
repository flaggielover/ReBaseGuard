# Stage F — cross-stage scientific synthesis

What ReBaseGuard has actually established, layer by layer, with each layer's
evidence type stated and not collapsed into its neighbours.

---

## A. Fully closed inherited foundation — Level 1–3

**Status: `CLOSED`, re-verified in this audit.**

`bash scripts/verify_level_1_3.sh --quick` → **ALL CHECKS PASSED (0 skipped)**:
Lean toolchain `leanprover/lean4:v4.34.0-rc1`, **axiom audit clean and the final
theorem elaborates**, Arb certificate **full replay PASS** with the regenerated
audit report byte-identical to the stored one, and 90 regression tests passing.

What is closed:

| Result | Evidence type |
|---|---|
| `d/de E[Z_tau e^{-eT_tau-(e²/2)tau}]\|₀ = -E[Z_tau T_tau]` | **PROVED / machine-checked in Lean** |
| `Gamma_CUSUM = E₀[Z_tau T_tau] ∈ [3.9243482, 27.8493821]`, hence `> 2` | **RIGOROUS NUMERICAL CERTIFICATE** (outward-rounded Arb) |
| Score identity `F₁'(0) = 1 − Gamma` | **PROVED** |
| Consequently `F₁'(0) < −1` and `rho_c = 1/(Gamma−1) ∈ (0,1)` | **PROVED**, given the certificate |

Scope, as the closure report itself states: this is the frozen two-sided
Gaussian CUSUM at `k = 1/2`, `h = 5`, `m = 1`. Lean proves the differentiation
identity — **not** `Gamma > 2`; that is the Arb certificate's job.

---

## B. Strongest rigorous Level-4 result — Stage B

**`STAGE-B-CLOSED-RIGOROUS-PERIOD2`**, verified from
`level4/stage_b/certificate/period2_certificate.json`.

Precisely what is certified, for the **deterministic conditional-mean map** `F₁`
at `rho = 1`:

| Certified statement | Value |
|---|---|
| a nonzero root of `H(e) = F₁(e) + e` exists in `I` | `I = [1.0287242887184211, 1.0447242887184212]` |
| that root is **unique** in `I` | `H' > 0` on all of `I`; `min H' = 1.32886` |
| `I` **excludes** 0 | `zero_excluded: true` |
| the resulting symmetric period-2 orbit is **locally attracting** | multiplier `lambda_2 ∈ [0.10814763, 0.83253171] ⊂ (−1,1)` |

Requirements R1–R4 all record `ok: true`.

### The distinction that governs everything downstream

**This is a theorem about the deterministic skeleton. It is not a theorem about
the stochastic monitoring chain.** Two independent lines of evidence in this
repository establish that the stronger stochastic reading is false or
unsupported:

1. **`level_4_theory_numerics/rebaseguard_level4_design.md` (2026-08-21 10:48,
   ~3.5 h before the Stage B certificate)** records as **FALSIFIED**:
   * claim 12 — "period-2 describes the stochastic long run" (at `rho = 1`, sign
     alternation is `0.88`, not `1`, and only 25% of mass lies within 25% of `e*`);
   * claim 13 — "stationary mass away from 0 diagnoses reuse" (the fresh control
     exceeds `rho = 0.2`);
   * claim 14 — "reuse is the dominant cause of ARL loss" (subordinate to `m = 1`,
     non-monotone in `rho`).

   Its gate recommendation was **`PROCEED-ALTERNATIVE-DYNAMICS`**, explicitly
   *not* `PROCEED-PERIOD2`, warning that certifying the orbit would certify "a
   feature of a skeleton that does not govern the observable process."

2. **Stage D D2.5** independently reached **`MATHEMATICAL, NOT OPERATIONAL`**:
   across the `Gamma_m = 2` crossing at `m* ≈ 72.19`, **0 of 4** monitoring
   metrics peak and **4 of 4** vary monotonically in `log m`; alarm alternation
   persists *above* the crossing (`−0.456` at `m = 100`, where `Gamma_m = 1.776 < 2`
   and full reuse is locally stable).

**These are not contradictions of Stage B.** Stage B in fact completed items 8
and 9 of that earlier ledger, both of which read "needs certificate". Stage B's
own scope statement is correct throughout the repository: *"It concerns the
deterministic skeleton only; the noisy recursion's invariant law remains OPEN."*

**Safe synthesis:** the deterministic skeleton has rigorously established
nonlinear dynamics, including the certified period-2 result, but this does not
imply that the stochastic monitoring chain exhibits a corresponding sharp
operational phase transition — and the direct measurement says it does not.

---

## C. Practical / sensitivity result — Stages C and C.1

Both statuses stand; neither erases the other.

**`STAGE-C-PARTIAL`.** The stability-aware policy
`rho_safe(delta) = (1−delta)/(Gamma−1)` is well-defined and safe, and at
`delta = 0.2` (conservative, from the certified enclosure) gives
`rho = 0.029796`. **Criterion C6 failed and was left failed.** A fixed `rho`
well above the stability boundary (oracle `rho = 0.3`, MSE `0.70864`) dominates
the policy (`0.94369`) on in-control performance — recorded as
`dominates: true`.

**`STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`.** A separate confirmatory stage,
preregistered and hashed before any data, on new seeds, with a
baseline-normalised metric. It found the certificate-aware policy **non-inferior
to fresh at every tested shift** (`epsilon = 0.05`): `Delta = 0.25` upper95
`+0.01358`; `0.5` `+0.01410`; `1.0` `−0.00059`; `1.5` `−0.00920`.

**What C.1 established:** that the earlier apparent sensitivity loss was an
artifact of comparing *raw* delays across policies whose in-control run lengths
differed by 1.7×. Under a baseline-normalised metric, no sensitivity penalty is
detectable.

**What C.1 did NOT establish, and must not be read as establishing:** it does
**not** make C6 pass; C6 remains failed. It does **not** remove the oracle-`rho`
domination finding. It makes **no sample-efficiency claim**. Its scope is
sensitivity only.

---

## D. Detector replication / generalization — Stage D

**`STAGE-D-PARTIAL`.** Retained in full:

| Gate | Result | Status |
|---|---|---|
| D1.1 | SR ARL0-matched, `A = 520.886134`, rel err `−0.00045 ± 0.00174` | **PASS** |
| D1.2 | `Gamma_SR = 17.3198 ± 0.0280`, lower bound `17.2649 > 2` | **PASS** |
| D1.3 | `Gamma_SR − Gamma_CUSUM = +1.4746 ± 0.0400`, CI excludes 0 | **PASS** |
| D1.4 | SR period-2 candidate `e* = 1.036719 ± 0.001496` | **CANDIDATE** |
| D2.2 | crossing bracket `m* ∈ [50, 75]`, `+108.6 / −14.5` SE | **PASS** |
| **D2.3** | derivative correspondence at `m > 1` | **FAIL** — 0/8 at the frozen step |
| D2.4 | `Gamma_inf = 1.4037 ± 0.0013 < 2` | numerical only |
| **D2.5** | operational consequence of the crossing | **MATHEMATICAL, NOT OPERATIONAL** |
| D3.2 | `Gamma_psi > 2`, six ARL0-matched families | **PASS** 6/6 frozen; 5/6 normalised |
| **D3.2-t3** | `t3` under the two estimands | **AMBIGUOUS** |
| **D4** | `m`–`rho` phase map | **NOT RUN** — gate required D2 to survive |

**D2.3's failure is diagnosed but not repaired.** The discrepancy is one-signed,
shrinks at observed order `p = 1.938` against the exact central-difference value
2, and Richardson extrapolation matches `1 − Gamma_m` within `0.40` SE at every
`m`. That diagnosis was written and hashed **before** the run
(`7b7a54c6…`). Re-running at a smaller step would be re-tuning after seeing a
`Gamma`, forbidden by the frozen protocol §8. The identity therefore remains
**unconfirmed at `m > 1`** — consistent with, but not established by, this evidence.

**The `t3` ambiguity is preserved, not resolved.** The frozen estimand gives
`Gamma_psi = 2.5980` (lower bound `2.5449 > 2`, **PASS**); the
stability-relevant normalisation gives `Gamma_psi/E[psi'] = 1.2990` (lower bound
`1.2725 < 2`, **FAIL**). Assumption A5 predicted this disagreement, and that the
normalisation would move the t-families and the contaminated families in
*opposite* directions — which it did. Neither estimand is selected for
convenience.

**Strongest safe detector statement: two-detector replication of strong
stopped-selection feedback under a matched reuse protocol.** Not
detector-independence — two detectors is replication, and the 2026-08-21 ledger
independently classified detector-generality as **OPEN** ("two Gaussian `m = 1`
witnesses only"). The naive Gaussian-form `Gamma_T` reading `99.5586` at `t3`
against a correct `2.5980` is positive evidence that the Gaussian stopped-sum
identity must **not** be exported to heavy-tailed families without the correct score.

---

## E. Semi-real external stress test — Stage E

**`STAGE-E-PARTIAL`. `0 / 3` tasks satisfied H-E5; `2` were required.** Closure
became mathematically unreachable after Task B and was declared so **before**
Task C was run.

| | Task A — Elec2 | Task B — Air Quality | Task C — Bike Sharing |
|---|---|---|---|
| usability | USABLE | USABLE, **LOW-POWER** | **PARTIALLY USABLE AFTER FREEZE** |
| H-E1 | **SUPPORTED** | NOT SUPPORTED *(non-demo)* | **UNEVALUABLE** |
| H-E4 | NOT SUPPORTED — **directional contradiction** (`−0.0141`) | NOT SUPPORTED *(non-demo)* | **SUPPORTED** (`+0.0470 [+0.0062,+0.1266]`) |
| H-E5 | NOT SUPPORTED | NOT SUPPORTED | NOT MET |

**This is not successful external validation and is not described as such.**
What it does teach:

1. **Reference distortion does not imply worse normalised discrimination.**
   Task A is decisive on distortion (`P1 − P2 = +0.0766 [+0.0369, +0.1135]`) yet
   shows no discrimination penalty, with the point estimate in the *opposite*
   direction. Full reuse buys responsiveness by running a distorted reference:
   it shortens in-control *and* post-drift waiting times roughly proportionally,
   so the normalisation largely cancels the effect.
2. **The effect's sign is stream-dependent.** H-E4: `−0.0141` (A), `+0.0528` (B),
   `+0.0470` (C). Raw delays reverse too — full reuse detects faster in A, slower
   in B and C.
3. **Real streams are not the frozen model.** Residual ACF(1) `0.718 / 0.832 /
   0.792`; Task C carries a weekly cycle (`ACF(168) = 0.780`); Task B is
   heavy-tailed (excess kurtosis `+4.51`). Calibrated thresholds land at
   `15.2–36.7` versus the frozen `h = 5`.
4. **Short streams cannot support the analysis.** Task C's reference-state and
   alert-burden endpoints fell below the pre-specified reliability floor (2–3
   effective blocks against 5) — and those were the **largest apparent mechanism
   effects anywhere in Stage E**. The gate was applied against the most
   favourable-looking data in the stage, and they were excluded.

---

## F. The central scientific story

**What survived every stage.** The stopped-selection identity and its
consequences for the frozen Gaussian CUSUM at `m = 1`: the Lean-checked
differentiation identity, the Arb-certified `Gamma > 2`, `F₁'(0) = 1 − Gamma < −1`,
and an interior `rho_c`. Wald's second identity `sum_i gamma_i = E[T_tau²] = ARL₀`
reproduced at ratio `0.99960`.

**What was rigorously established but failed to become operationally sharp.**
The deterministic period-2 structure (Stage B) and the `Gamma_m = 2` crossing at
`m* ∈ [50, 75]`. Both are real and certified/measured; neither produces a
discontinuity in the stochastic chain (D2.5), and the stochastic reading was
already falsified in 2026-08-21.

**What did not survive generalization.** The `m > 1` derivative theorem (D2.3
FAILED), the `m`–`rho` phase map (D4 NOT RUN), the SR derivative theorem (never
proved), and the general location-family theorem (A1 UNPROVED for every
non-Gaussian family).

**What remained numerically suggestive but unproved.** `Gamma_SR = 17.3198` and
the SR excess `+1.4746`; the SR period-2 candidate `e* = 1.036719`;
`Gamma_inf = 1.4037 < 2`; non-Gaussian robustness across six families.

**What failed.** D2.3; Stage C's C6; Stage E's `≥2/3` H-E5 rule (0/3); and the
three 2026-08-21 stochastic claims (12, 13, 14).

**What became ambiguous.** The `t3` estimand disagreement, and — at the
meta-level — whether `staged_task_ranking.csv`'s MANDATORY labels are Level-4
closure requirements or Stage-D priorities.

### Verified structural summary

**CORE.** Alarm-conditioned reuse induces a cross-cycle reference-state feedback
mechanism, and in the frozen Gaussian CUSUM setting (`k = 1/2`, `h = 5`, `m = 1`)
that mechanism admits rigorous local and nonlinear analysis, including a
certified period-2 structure **of the deterministic conditional-mean skeleton**.

**GENERALIZATION.** A structurally distinct Shiryaev–Roberts detector reproduces
the strong local stopped-selection feedback numerically at matched `ARL₀`
(`Gamma_SR = 17.3198 ± 0.0280`), but the broader `m`-dependent theorem and
phase-map program did not close: D2.3 failed and D4 was never run.

**EXTERNAL VALIDITY.** Semi-real streams behave heterogeneously: reference
distortion can occur without normalised discrimination degradation, and the
stochastic operational behaviour does not mirror the deterministic skeleton.
