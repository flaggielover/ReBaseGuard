# ReBaseGuard Level 4 — Stage C

## Stability-Aware Reuse, Monitoring Consequences, and the Reuse–Performance Tradeoff

**Decision: `STAGE-C-PARTIAL`**

> **Scope.** Stage B's rigorous theorem concerns the **deterministic**
> conditional-mean map `F_1`, *not* the noisy recursion
> `E_{j+1} = F_1(E_j) + noise`. Nothing in Stage C upgrades it. Every
> stationary shape below is an empirical, numerical description; no
> bimodality, ergodicity or stochastic period-2 claim is made anywhere.

---

## 1. Scientific question

Not *does reuse cause instability* — Stage A and Stage B settled that.
The Stage C question is whether the **certified local stability**
boundary can be used to *control* reuse: keep some alarm-triggering data,
avoid recursive reference instability, and not wreck monitoring.

---

## 2. Frozen theoretical inputs

| Input | Value | Status |
|---|---|---|
| `F_rho = rho F_1`, `F_1'(0) = 1 - Gamma` | exact | FROZEN-PROVED (Level 2C) |
| `Gamma` enclosure | `[3.9243482, 27.8493821]` | FROZEN-CERTIFIED (Arb) |
| `Gamma` point estimate | `15.885729 ± 0.020165` | NEW-NUMERICAL (Stage A) |
| `rho_c = 1/(Gamma-1)` | point `0.067178`; certified `[0.037245, 0.341957]` | derived |
| Stage B period-2 orbit at `rho=1` | `e* ∈ [1.028724, 1.044724]`, `lambda_2 ∈ [0.1081, 0.8325]` | RIGOROUS-CERTIFIED, deterministic map |

---

## 3. The ReBaseGuard policy

Require `|F'_rho(0)| <= 1 - delta`. Since `|F'_rho(0)| = rho (Gamma - 1)`:

```text
rho_safe(delta) = clip( (1 - delta) / (Gamma - 1), 0, 1 )
```

| Variant | `Gamma` used | Guarantee | Evidence class |
|---|---|---|---|
| POINT | `15.885729` | holds *if* the Monte Carlo estimate is exact | heuristic, **NOT certified** |
| **CONSERVATIVE** | `27.849382` | holds for the **true** `Gamma` | **certified**, local linear stability, deterministic map only |

| `delta` | POINT `rho` | CONSERVATIVE `rho` |
|---|---|---|
| 0.05 | 0.063820 | 0.035383 |
| 0.1 | 0.060461 | 0.033520 |
| **0.2** | **0.053743** | **0.029796** |
| 0.5 | 0.033589 | 0.018622 |

**Headline: `delta = 0.2`, CONSERVATIVE, `rho = 0.029796`.** Fixed in
the protocol before the campaign. `delta = 0.2` was chosen as a
conventional 20% margin, not for performance.

The distinction between the two variants is not cosmetic. At the
certified upper end of `Gamma`, the POINT variant's reuse fraction gives
`|F'_rho(0)| = 1.443 > 1` — i.e. it
would sit on the *unstable* side of the boundary. That is why only the
conservative variant carries a guarantee.

---

## 4. Pre-specified protocol

`level4/stage_c/STAGE_C_PROTOCOL.md`, frozen before the campaign, fixes
the endpoints, grids, sample sizes, tolerances, the policy and the
success criteria. Section 12 of that protocol pre-registers the
possibility that a fixed `rho` dominates the policy — see §12 below.

---

## 5. Experimental design

* **In-control:** the FROZEN Stage A multi-cycle simulator, 100 replicates × 10,000 retained cycles, burn-in 1,000, master seed `20260821`. 23 `rho` cells.
* **Detection:** 4,000 independent change events per cell. `tau` is heavy-tailed (in control at `rho=0`: mean ≈ 78, median 16, sd ≈ 173), so 100 events would give ~22% relative error — far too coarse for criterion C6.
* **Statistical unit:** the replicate. All intervals are 95% percentile
  bootstrap over replicates, never over cycles.
* **CRN:** the same master seed across `rho`, so every between-`rho`
  comparison is a **paired** replicate contrast. Naive independent-point
  standard errors are never used for such comparisons.
* **Grid:** all 21 protocol points retained; 2 points added (the two
  policy values) and recorded as additions; 4 further points added near
  `rho_c` by the adversarial refinement check. Nothing was deleted.

---

## 6. Stability results

| `rho` | regime | ref. MSE | 95% CI | cycle ARL | 95% CI | alternation | ACF₁ |
|---|---|---|---|---|---|---|---|
| 0 | certified-stable | 1.00034 | [0.99723, 1.00347] | 83.309 | [82.946, 83.673] | 0.5004 | -0.0020 |
| 0.01 | certified-stable | 0.98069 | [0.97764, 0.98376] | 84.087 | [83.744, 84.435] | 0.5059 | -0.0099 |
| 0.02 | certified-stable | 0.96172 | [0.95870, 0.96472] | 84.782 | [84.426, 85.142] | 0.5108 | -0.0180 |
| 0.029796 **←RBG** | certified-stable | 0.94369 | [0.94074, 0.94664] | 85.230 | [84.829, 85.630] | 0.5162 | -0.0262 |
| 0.03 | certified-stable | 0.94333 | [0.94039, 0.94630] | 85.344 | [84.942, 85.753] | 0.5163 | -0.0264 |
| 0.04 | undetermined-by-certificate | 0.92574 | [0.92288, 0.92865] | 85.855 | [85.451, 86.253] | 0.5218 | -0.0350 |
| 0.05 | undetermined-by-certificate | 0.90857 | [0.90576, 0.91142] | 86.653 | [86.259, 87.048] | 0.5276 | -0.0438 |
| 0.053743 ←RBG-pt | undetermined-by-certificate | 0.90242 | [0.89959, 0.90526] | 86.856 | [86.451, 87.270] | 0.5296 | -0.0471 |
| 0.06 | undetermined-by-certificate | 0.89249 | [0.88973, 0.89528] | 87.374 | [87.006, 87.747] | 0.5332 | -0.0527 |
| 0.065 | undetermined-by-certificate | 0.88460 | [0.88185, 0.88737] | 87.722 | [87.373, 88.082] | 0.5361 | -0.0574 |
| 0.067 | undetermined-by-certificate | 0.88144 | [0.87871, 0.88414] | 87.889 | [87.521, 88.262] | 0.5372 | -0.0593 |
| 0.07 | undetermined-by-certificate | 0.87684 | [0.87411, 0.87960] | 87.981 | [87.595, 88.375] | 0.5391 | -0.0621 |
| 0.075 | undetermined-by-certificate | 0.86924 | [0.86654, 0.87198] | 88.493 | [88.125, 88.881] | 0.5421 | -0.0667 |
| 0.08 | undetermined-by-certificate | 0.86180 | [0.85907, 0.86455] | 88.856 | [88.524, 89.193] | 0.5448 | -0.0717 |
| 0.1 | undetermined-by-certificate | 0.83390 | [0.83134, 0.83648] | 89.844 | [89.428, 90.264] | 0.5571 | -0.0913 |
| 0.15 | undetermined-by-certificate | 0.77638 | [0.77410, 0.77871] | 93.047 | [92.636, 93.473] | 0.5910 | -0.1430 |
| 0.2 | undetermined-by-certificate | 0.73644 | [0.73431, 0.73860] | 94.929 | [94.533, 95.343] | 0.6272 | -0.1976 |
| 0.25 | undetermined-by-certificate | 0.71396 | [0.71188, 0.71602] | 95.800 | [95.442, 96.166] | 0.6650 | -0.2525 |
| 0.3 ←ORACLE | undetermined-by-certificate | 0.70864 | [0.70684, 0.71050] | 95.435 | [95.022, 95.836] | 0.7040 | -0.3054 |
| 0.4 | certified-unstable | 0.74117 | [0.73955, 0.74280] | 90.622 | [90.212, 91.015] | 0.7785 | -0.3980 |
| 0.5 | certified-unstable | 0.82427 | [0.82258, 0.82592] | 81.724 | [81.396, 82.047] | 0.8393 | -0.4702 |
| 0.75 | certified-unstable | 1.21634 | [1.21413, 1.21847] | 59.652 | [59.348, 59.961] | 0.9080 | -0.5373 |
| 1 | certified-unstable | 1.87731 | [1.87384, 1.88081] | 50.018 | [49.744, 50.287] | 0.8951 | -0.4971 |

**Paired contrasts** (replicate-level, CRN-aware):

* `MSE(rho=1) - MSE(RBG)` = **0.9336** [0.9292, 0.9380]
* `MSE(rho=1) / MSE(RBG)` = **1.9893** [1.9825, 1.9962]
* `MSE(fresh) - MSE(RBG)` = 0.0567 [0.0564, 0.0569]

### The `rho_c` null finding

**Crossing the certified local stability boundary produces no visible
signature in either headline endpoint.** Reference MSE and cycle ARL both
vary smoothly through `rho_c ≈ 0.067` with no kink, no discontinuity and
no change of slope that the grid can resolve — the four extra points added
at `rho ∈ {0.055, 0.062, 0.068, 0.072}` confirm it.

This is a genuine null result and it matters for interpretation: the
local boundary is a statement about the linearisation of `F_1` at `e = 0`,
and the strong nonlinearity of `F_1` caps the resulting instability long
before it reaches a stationary summary. A practitioner cannot find
`rho_c` by looking at MSE or ARL curves; it has to come from the theory.

---

## 7. ARL mechanism

`A(e) = E[tau | E_j = e]` was estimated on 221 grid
points spanning `|e| <= 5`, 200,000 paths each, with
**independent seeds per grid point** (no CRN): `A` is consumed by an
integral, so independent errors average down, whereas CRN would make them
systematic.

* `A(0) = 464.833 ± 1.026` against the frozen in-control `ARL_0 ≈ 465.4`
* **symmetry:** 110 mirror pairs, max `|z| = 2.83`, mean `z = -0.075` — consistent with the proved arm-swap involution
* **monotonicity in `|e|`: TESTED, not assumed.** 0/110 intervals increase, 0 of them by more than 3σ. Verdict: `True`

So the mechanism is confirmed in the expected direction: **reference
displacement shortens the in-control stopping time**, i.e. raises the
false-alarm hazard.

### Decomposition check

`ARL_rho = E_pi[A(e)]` was evaluated by averaging an interpolated `A` over
the observed `e_prev` sample — no binning of `pi`. Because both routes use
the *same* cycles, the contrast is naturally **paired**:

| `rho` | direct `mean(tau)` | decomposition `E_pi[A]` | paired gap | 95% CI |
|---|---|---|---|---|
| 0 | 83.309 | 82.856 | +0.453 | [+0.160, +0.757] |
| 0.01 | 84.087 | 83.581 | +0.505 | [+0.244, +0.777] |
| 0.02 | 84.782 | 84.307 | +0.475 | [+0.213, +0.746] |
| 0.029796 | 85.230 | 85.053 | +0.177 | [-0.103, +0.474] |
| 0.03 | 85.344 | 85.067 | +0.277 | [-0.018, +0.583] |
| 0.04 | 85.855 | 85.722 | +0.133 | [-0.174, +0.449] |
| 0.05 | 86.653 | 86.467 | +0.186 | [-0.124, +0.501] |
| 0.053743 | 86.856 | 86.688 | +0.168 | [-0.138, +0.465] |
| 0.06 | 87.374 | 87.177 | +0.197 | [-0.080, +0.473] |
| 0.065 | 87.722 | 87.531 | +0.192 | [-0.062, +0.448] |
| 0.067 | 87.889 | 87.662 | +0.226 | [-0.048, +0.511] |
| 0.07 | 87.981 | 87.717 | +0.264 | [-0.030, +0.558] |
| 0.075 | 88.493 | 88.220 | +0.272 | [+0.003, +0.548] |
| 0.08 | 88.856 | 88.495 | +0.361 | [+0.120, +0.611] |
| 0.1 | 89.844 | 89.706 | +0.138 | [-0.171, +0.450] |
| 0.15 | 93.047 | 92.587 | +0.460 | [+0.180, +0.743] |
| 0.2 | 94.929 | 94.629 | +0.300 | [-0.001, +0.607] |
| 0.25 | 95.800 | 95.409 | +0.391 | [+0.115, +0.674] |
| 0.3 | 95.435 | 95.152 | +0.284 | [-0.033, +0.610] |
| 0.4 | 90.622 | 90.309 | +0.313 | [+0.034, +0.599] |
| 0.5 | 81.724 | 81.385 | +0.338 | [+0.046, +0.626] |
| 0.75 | 59.652 | 59.537 | +0.115 | [-0.112, +0.348] |
| 1 | 50.018 | 49.974 | +0.044 | [-0.173, +0.269] |

Pre-specified tolerance was 3σ combining the paired bootstrap SE with
`A`'s own Monte Carlo error. Result: **max |z| = 2.12 under the protocol formula (threshold 3). Without the pre-specified bias_interp term it would be 3.70; with a sharper Richardson bias estimate 3.34 and 2/23 points would exceed 3. Raw agreement is better than 0.60% at every rho. C7 is the weakest criterion and its verdict does not change the Stage C decision, since C6 already fails.** → `PASS`.

---

## 8. Detection-delay results

Mean detection delay (observations) for a mean shift applied at a
cycle boundary. `Delta = 0` is the in-control control arm.

| `rho` | in control | $\Delta$=0.25 | $\Delta$=0.5 | $\Delta$=1 | $\Delta$=1.5 |
|---|---|---|---|---|---|
| 0 | 80.79 | 74.42 | 72.34 | 55.05 | 35.01 |
| 0.029796 **←RBG** | 83.35 | 77.68 | 74.10 | 52.00 | 33.73 |
| 0.053743 | 87.18 | 80.50 | 73.17 | 55.47 | 34.54 |
| 0.25 | 97.45 | 87.66 | 78.41 | 55.11 | 25.77 |
| 0.3 | 92.09 | 89.13 | 81.78 | 56.77 | 26.90 |
| 1 | 50.54 | 51.91 | 50.28 | 53.19 | 44.37 |

**Paired contrasts against full reuse** (criterion C6):

| `Delta` | delay(RBG) | delay(rho=1) | paired difference | 95% CI | C6 threshold | verdict |
|---|---|---|---|---|---|---|
| 0.25 | 77.676 | 51.910 | +25.767 | [+18.389, +33.019] | < +12.977 | **FAIL** |
| 0.5 | 74.105 | 50.282 | +23.823 | [+16.692, +30.903] | < +12.570 | **FAIL** |
| 1 | 51.997 | 53.189 | -1.192 | [-7.522, +5.364] | < +13.297 | PASS |
| 1.5 | 33.727 | 44.367 | -10.640 | [-16.389, -4.776] | < +11.092 | PASS |

**C6 therefore FAILS**, and it is left failed: the criterion was not
rewritten, and the Stage C decision reflects the failure.

### Why C6 failed, and what the data actually show

C6 compares **raw** delays between two policies whose in-control cycle
ARLs differ by a factor of 1.7 (RBG 85.2, full reuse 50.0). A detector
that alarms constantly always posts short "delays", change or no
change. That is not like-for-like — a hazard flagged in §9 of the
protocol, which I then failed to build the criterion around.

Normalising each policy by its own in-control delay removes the
baseline alarm rate and measures sensitivity as such:

| `rho` | $\Delta$=0.25 | $\Delta$=0.5 | $\Delta$=1 | $\Delta$=1.5 |
|---|---|---|---|---|
| 0 (fresh) | 0.921 | 0.895 | 0.681 | 0.433 |
| **0.0298 (RBG)** | 0.932 | 0.889 | 0.624 | 0.405 |
| **1.0 (full reuse)** | 1.027 | 0.995 | 1.052 | 0.878 |

Full reuse sits at **≈1.0 at every shift**: its detection delay is
almost identical whether or not a change occurred. Its alarms are
driven by its own reference instability, not by the data — that is the
*absence* of sensitivity, not its presence. ReBaseGuard's ratios fall
from 0.93 to 0.41, and at `Delta = 1.5` it is **absolutely faster**
than full reuse (33.7 vs 44.4) despite a 1.7x longer in-control run.

So the scientific concern C6 was written to capture — *is the stability
gain bought by blinding the detector?* — is answered decisively **no**,
in the opposite direction from the criterion's verdict.

The ratio is reported as a **secondary diagnostic only**. It is not a
gate, it was not pre-specified as one, and it does not rescue C6. Full
analysis: `level4/stage_c/notes/CRITERION_C6_DIAGNOSIS.md`.

**Detection delay must never be read alone.** The honest object is the
pair (in-control ARL, delay), which §10 plots. Because `h` is frozen,
the baselines cannot be re-tuned to a common `ARL_0`, so no
single-number delay comparison is like-for-like.

---

## 9. Sample-efficiency results

Definitions match the implemented protocol exactly:

| ID | Quantity | At `rho = 0` | At RBG | At `rho = 1` |
|---|---|---|---|---|
| D1 | retained alarm-data weight = `rho` | 0 | **0.029796** | 1 |
| D2 | fresh observations per cycle | 1 | 1 | 0 |
| D3 | fresh observations per monitored observation | 0.01200 | 0.01173 | 0 |

**Stated limitation, pre-registered in the protocol.** At `m = 1` the
fresh-sample *count* (D2) is a step function of `rho`: the protocol always
draws one fresh variate and weights it by `1-rho`. The continuous
efficiency story therefore lives in the weight D1 and in the amortised D3,
not in D2. No percentage is quoted here that is not one of D1–D3.

The practical consequence is blunt: **at `m = 1`, ReBaseGuard does not
reduce the number of fresh observations collected.** It changes how much
weight the reference places on stopping-selected data. A protocol in which
the fresh draw could be *skipped* — pre-allocated thinning or sample
splitting — would make D2 continuous, but both change the frozen
re-baselining rule and are therefore out of scope (`SC-OPEN2`).

---

## 10. Pareto analysis

* `Delta = 0.25`: Pareto front (high ARL, low delay) at `rho ∈ {0, 0.05, 0.067, 0.07, 0.075, 0.1, 0.15, 0.2, 0.25, 0.75, 1}`; ReBaseGuard on front: **False**; oracle on front: False
* `Delta = 0.5`: Pareto front (high ARL, low delay) at `rho ∈ {0.075, 0.08, 0.1, 0.25, 0.75, 1}`; ReBaseGuard on front: **False**; oracle on front: False
* `Delta = 1.0`: Pareto front (high ARL, low delay) at `rho ∈ {0.15, 0.25}`; ReBaseGuard on front: **False**; oracle on front: False
* `Delta = 1.5`: Pareto front (high ARL, low delay) at `rho ∈ {0.25}`; ReBaseGuard on front: **False**; oracle on front: False

Regimes, using the certified `rho_c` enclosure rather than the point
estimate alone — the enclosure is wide, so a whole band of `rho` is
genuinely **undetermined by the certificate**:

| Regime | `rho` range | interpretation |
|---|---|---|
| certified-stable | `rho < 0.0372` | local stability holds for every `Gamma` the certificate admits |
| undetermined | `0.0372 <= rho <= 0.3420` | the certificate cannot decide; the point estimate places `rho_c` at 0.0672 |
| certified-unstable | `rho > 0.3420` | the fixed point is locally unstable for every admissible `Gamma` |

ReBaseGuard sits at `rho = 0.029796`, inside **certified-stable**, which
is exactly what it was designed to guarantee.

---

## 11. Adversarial checks

| Check | Question | Result | Note |
|---|---|---|---|
| `independent_seeds` | do the headline endpoints reproduce under a disjoint seed family? | PASS | max |z| = 2.37 over 8 comparisons (threshold 3) |
| `run_length` | does halving or doubling the run change the answer? | PASS | max |z| = 0.74 (threshold 3.5) |
| `burn_in` | is the stationary estimate sensitive to burn-in length? | PASS | max |z| = 0.66 (threshold 3.5) |
| `stationary_window` | is the retained window actually stationary (first vs second half)? | PASS | paired CI for the half-to-half MSE difference contains 0 at every probed rho |
| `a_grid_refinement` | does halving the A(e) grid move the decomposition? | PASS | max relative shift 2.43e-03 (threshold 1%) |
| `rho_refinement_near_rho_c` | does refining rho near rho_c reveal any structure the grid missed? | PASS | 4 added points, MSE monotone decreasing through rho_c; no discontinuity |
| `arl_decomposition` | do direct ARL and the stationary decomposition agree? | PASS | max |z| = 2.12 under the protocol formula (threshold 3). Without the pre-specified bias_interp term it would be 3.70; with a sharper Richardson bias estimate 3.34 and 2/23 points would exceed 3. Raw agreement is better than 0.60% at every rho. C7 is the weakest criterion and its verdict does not change the Stage C decision, since C6 already fails. |
| `policy_variants` | does the conservative variant hold across the whole certified Gamma? | PASS | conservative holds at every delta; the POINT variant would violate |F'|<=1 for 3/4 deltas if Gamma were at its certified upper end -- which is exactly why it is labelled heuristic |
| `fresh_baseline_sanity` | does rho = 0 behave exactly as its own definition requires? | PASS | sd = 1/sqrt(m), alternation 0.5, ACF 0, MSE 1 |
| `stage_a_reproduction` | does Stage C reproduce the Stage A Gate 4.1 numbers? | PASS | max relative gap 4.57e-03 (threshold 2%); note Stage A reported sd on e_next, Stage C on e_prev |
| `no_stage_b_leak` | can any Stage B outcome reach the policy definition? | PASS | no Stage B root or multiplier value appears in policy.py |

**11/11** passed.

---

## 12. Negative and null findings

Kept prominent, not buried.

1. **`rho_c` is invisible in the endpoints.** Reference MSE and ARL pass
   through the certified local stability boundary with no kink. The
   boundary is real and certified, but it is not an observable transition
   in stationary summaries (`SC-NULL1`).
2. **ReBaseGuard is not performance-optimal, as pre-registered.** A fixed
   `rho = 0.3` attains reference MSE 0.70864 against **0.94369** for the policy;
   the paired difference is +0.23505 [+0.23307, +0.23697], so the domination is
   statistically clear. This was written into §12 of the protocol
   **before** the campaign, precisely so it could not later be presented
   as a discovery or quietly dropped. The policy buys a *certified local
   stability guarantee*, not optimality — and that is the price.
3. **At `m = 1` no fresh observations are saved** (§9). The efficiency
   gain is in reference weight, not in sample count.
4. **The POINT policy variant is not safe** at the certified upper end of
   `Gamma`; it is reported only for contrast (`SC-M3`).

---

## 13. Limitations

* The certified guarantee is **local linear stability of the deterministic
  map at `e = 0`** — nothing more. It is not a statement about the noisy
  recursion, its invariant law, or its stationary dispersion.
* Stage B's period-2 theorem is about the deterministic map `F_1`. Stage C
  neither uses nor extends it; the policy provably cannot see it.
* Only `m = 1`, `k = 1/2`, `h = 5`, Gaussian innovations, shifts at a cycle
  boundary, non-adaptive `rho`.
* The certified `rho_c` enclosure `[0.0372, 0.3420]` is wide because the
  frozen `Gamma` enclosure is wide. A tighter `Gamma` certificate would
  immediately allow a less conservative certified policy — currently the
  conservative variant is 1.80x more
  restrictive than the point-estimate variant.
* Stationary shapes are empirical. No bimodality, ergodicity or stochastic
  period-2 claim is made.

---

## 14. Claim ledger

Stage A and Stage B ledgers are untouched. Stage C entries are in
`level4/reports/STAGE_C_LEDGER.md`.

---

## 15. Final Stage C decision

### `STAGE-C-PARTIAL`

| # | Criterion | Result | Detail |
|---|---|---|---|
| C1 | policy mathematically well-defined | PASS | closed form rho_safe(delta) = (1-delta)/(Gamma-1), clipped to [0,1]; 21 unit tests |
| C2 | stability rule follows from frozen theory | PASS | derived from F'_rho(0) = rho(1-Gamma) (Level 2C, FROZEN-PROVED) and the frozen certified Gamma enclosure |
| C3 | full reuse substantially worse reference stability than the stable policy | PASS | MSE(rho=1)/MSE(RBG) = 1.9893 [1.9825, 1.9962] (paired); threshold 1.5 |
| C4 | ReBaseGuard preserves nonzero alarm data | PASS | rho = 0.029796 > 0; retained alarm-data weight D1 = 0.029796 |
| C5 | ReBaseGuard improves stability over full reuse | PASS | MSE(rho=1) - MSE(RBG) = 0.9336 [0.9292, 0.9380] (paired) |
| C6 | improvement not bought by destroying detection | **FAIL** | Delta=0.25: RBG-full = +25.767 [+18.389, +33.019] vs threshold +12.977; Delta=0.5: RBG-full = +23.823 [+16.692, +30.903] vs threshold +12.570; Delta=1: RBG-full = -1.192 [-7.522, +5.364] vs threshold +13.297; Delta=1.5: RBG-full = -10.640 [-16.389, -4.776] vs threshold +11.092 |
| C7 | direct and decomposition ARL agree | PASS | max \|z\| = 2.12 under the protocol formula (threshold 3). Without the pre-specified bias_interp term it would be 3.70; with a sharper Richardson bias estimate 3.34 and 2/23 points would exceed 3. Raw agreement is better than 0.60% at every rho. C7 is the weakest criterion and its verdict does not change the Stage C decision, since C6 already fails. |
| C8 | reproduces under independent seeds | PASS | max \|z\| = 2.37 over 8 comparisons (threshold 3) |
| C9 | no frozen Stage A/B claim regresses | PASS | 474 tests passed, 0 failed across the frozen Level 1-3, Stage A, Stage B and Stage C suites; Stage B certificate unchanged (db8ea712dc0abb34...); Stage A Gate 4.1 ARL reproduced to 7.35e-03 |
| C10 | negative/null findings retained | PASS | all 23 grid cells reported; adversarial checks recorded pass or fail; the domination finding is a headline limitation |

Failed criteria: C6.

### Reproduction

```bash
bash level4/stage_c/reproduce.sh
```

Every campaign cell is checkpointed by config hash, so a rerun reuses
completed cells and an interrupted run resumes.

### Figures

* `level4/stage_c/figures/fig01_mse_vs_rho.png`
* `level4/stage_c/figures/fig02_arl_vs_rho.png`
* `level4/stage_c/figures/fig03_detection_delay.png`
* `level4/stage_c/figures/fig04_sample_efficiency.png`
* `level4/stage_c/figures/fig05_pareto.png`
* `level4/stage_c/figures/fig06_stationary_densities.png`
* `level4/stage_c/figures/fig07_a_curve.png`
* `level4/stage_c/figures/fig08_arl_decomposition.png`
* `level4/stage_c/figures/fig09_stability_boundary.png`

