# ReBaseGuard Level 4 — Gate 4.2 Report

## Conditional nonlinear map estimator

**Decision: `PROCEED-RIGOROUS-PERIOD2`**

> **Proof role.** Monte Carlo throughout. Roots located here are
> *candidates*, never proved objects. The frozen Level 1–3 results are
> quoted unchanged and are only ever checked against.

---

## 1. What is estimated, and how

`F_rho(e) = E[E_{j+1} | E_j = e]`, estimated **without** the stationary
multi-cycle chain. For each grid point `e`, independently and repeatedly:
initialise a fresh monitoring cycle under the frozen model with reference
offset exactly `e` (detector reset to `(0,0)`, residuals `Z_t = X_t - e`,
`X_t ~ N(0,1)`); simulate to the exact frozen alarm rule; apply the
re-baselining rule; record `E_{j+1}`. Gate 4.2 never reads Gate 4.1's
output, so the two gates are genuinely independent estimators.

Two further estimators serve as **independent cross-checks**:

* **Score / change of measure.** On the stopped sigma-field,
  `dP_{-e}/dP_0 = exp(-e T_tau - (e^2/2) tau)`, so
  `F_1(e) = e + (1/m) E_0[W_{tau,m} L_e]` and
  `F_1'(0) = 1 - Gamma(m)` with `Gamma(m) = (1/m) E_0[W_{tau,m} T_tau]`.
  At `m = 1` this is *exactly* the frozen Level 1–3 target
  `Gamma = E_0[Z_tau T_tau]`. The whole estimate runs at `e = 0`.
* **Importance-sampled map.** The same change of measure evaluated on a
  grid, with an effective-sample-size diagnostic; trusted only near zero.

**Common random numbers.** The primary near-zero grid shares one seed key
across grid points. For each fixed `e` the draws are still i.i.d.
`N(0,1)`, so every pointwise estimate stays unbiased and the target
expectation is unchanged; only the joint law across the grid is altered,
which is what makes differences of the estimated map far less noisy.
Every CRN result below is replicated with independent seeds and CRN off.

**Statistical unit.** Unlike Gate 4.1, paths here are genuinely i.i.d.,
so the *path* is the unit and the ordinary i.i.d. standard error is
correct. Batch means are retained for independent-seed replication.

| Field | Value |
|---|---|
| detector | frozen two-sided CUSUM, `k = 1/2`, `h = 5` |
| `m` | 1 |
| master seed | `20260820` |
| score-route paths | 2,000,000 × 2 seed replicates |
| coarse-grid paths per point | 300,000 |
| near-zero paths per point | 1,000,000 (×2 runs) |
| root-refinement paths per point | 800,000 |
| git commit | `9077c9b66e837f9f687d6dc117306da3f4417efb` |
| working tree | **dirty** |
| Python / NumPy | 3.14.5 / 2.5.2 |
| code digest | `b6a67c99e7e46982…` |
| total runtime | 28.9 min |

---

## 2. The estimated map

`F_1(e)` on the coarse grid (positive half; the map is odd):

| `e` | `F_1(e)` | s.e. | `H_1(e) = F_1(e)+e` | mean `tau` |
|---|---|---|---|---|
| 0.0000 | -0.0019 | 0.0037 | -0.0019 | 465.0 |
| 0.0125 | -0.1784 | 0.0037 | -0.1659 | 463.1 |
| 0.0250 | -0.3657 | 0.0036 | -0.3407 | 454.5 |
| 0.0500 | -0.6977 | 0.0034 | -0.6477 | 430.2 |
| 0.0750 | -0.9774 | 0.0031 | -0.9024 | 392.4 |
| 0.1000 | -1.1866 | 0.0028 | -1.0866 | 348.0 |
| 0.1500 | -1.4489 | 0.0022 | -1.2989 | 261.8 |
| 0.2000 | -1.5531 | 0.0018 | -1.3531 | 191.4 |
| 0.2500 | -1.5743 | 0.0015 | -1.3243 | 139.1 |
| 0.3000 | -1.5608 | 0.0014 | -1.2608 | 102.9 |
| 0.3500 | -1.5326 | 0.0013 | -1.1826 | 77.5 |
| 0.4000 | -1.4934 | 0.0013 | -1.0934 | 59.8 |
| 0.5000 | -1.4122 | 0.0013 | -0.9122 | 38.0 |
| 0.6000 | -1.3343 | 0.0013 | -0.7343 | 26.2 |
| 0.7500 | -1.2224 | 0.0013 | -0.4724 | 17.1 |
| 1.0000 | -1.0600 | 0.0013 | -0.0600 | 10.4 |
| 1.2500 | -0.9159 | 0.0014 | 0.3341 | 7.4 |
| 1.5000 | -0.8016 | 0.0014 | 0.6984 | 5.7 |
| 2.0000 | -0.6171 | 0.0015 | 1.3829 | 4.0 |
| 2.5000 | -0.4900 | 0.0016 | 2.0100 | 3.1 |
| 3.0000 | -0.3876 | 0.0017 | 2.6124 | 2.6 |

The shape is the one the mechanism predicts: a steep negative slope
through the origin, a minimum, then a bend back toward zero as large
`|e|` makes the alarm fire almost immediately and the selected
observation reverts to an ordinary `N(0,1)` draw.

### Symmetry diagnostics

Oddness (`F(-e) = -F(e)`) is a *proved* symmetry of the model, so it is a
test of the estimator, not of the model. Over the
12 symmetric pairs on the dense near-zero grid:

* max standardised asymmetry `|z| = 2.78`
* mean `z = 0.511`
* chi-square per pair = 1.37

---

## 3. Local derivative correspondence — the critical test

This is the check the mission designates a **BLOCKER** if it fails.

### 3.1 Why a plain finite difference is the wrong estimator here

A central difference of an estimated map carries an `O(delta^2)`
truncation bias, `D(delta) = F'(0) + a3 delta^2 + O(delta^4)`. For this
map `a3` is large — the fit below gives `a3 ≈ 380` —
so at `delta = 0.05` the bias is of order 0.7, which is many Monte Carlo
standard errors. Reporting that as a disagreement with Level 1–3 would be
a numerical artefact dressed as a scientific finding. The measured scan:

| `delta` | `D(delta)` | s.e. | `D(delta) - (1-Gamma)` | ratio to `delta^2` |
|---|---|---|---|---|
| 0.1500 | -9.6769 | 0.0057 | 5.2088 | 231.5 |
| 0.1000 | -11.9258 | 0.0109 | 2.9599 | 296.0 |
| 0.0750 | -13.0376 | 0.0162 | 1.8481 | 328.5 |
| 0.0500 | -13.9785 | 0.0264 | 0.9073 | 362.9 |
| 0.0250 | -14.7614 | 0.0559 | 0.1243 | 198.9 |
| 0.0125 | -14.7100 | 0.1133 | 0.1757 | 1124.4 |

The ratio column is approximately constant, which identifies the gap as
truncation rather than model disagreement, and its value matches the
independently fitted cubic coefficient. The primary estimator is
therefore a weighted least-squares fit of the **odd** polynomial
`a1 e + a3 e^3 + a5 e^5` over the dense symmetric near-zero window, with
`a1 = F'(0)`.

### 3.2 Three routes to `F_1'(0)`

| Route | `F_1'(0)` | s.e. | independence |
|---|---|---|---|
| direct conditional simulator (odd-polynomial fit) | -14.9073 | 0.0251 | simulates cycles at each `e`; never uses `Gamma` |
| same, independent seeds and CRN off | -14.8516 | 0.0307 | disjoint random streams |
| score / change of measure at `e = 0` | -14.8857 | 0.0202 | never simulates at `e != 0` |
| **frozen Arb certificate** `Gamma ∈ [3.9243, 27.8494]` | enclosure `[-26.849, -2.924]` | — | outward-rounded interval arithmetic, immutable |

* Direct minus score: **-0.0215** (`0.67` sigma) → **CONSISTENT**.
* Direct estimate inside the certified enclosure: **True**.
* Score-route `Gamma = 15.8857 ± 0.0202` against the frozen diagnostic
  `15.8429`; two independent seeds differ by 0.39 sigma.
* Score-route `ARL_0 = 465.55` against the
  frozen diagnostic `465.4`.
* Selected fit: window `|e| <= 0.15`, 4 odd terms, 25 grid points, 20 independent batches; pooled chi-square per d.o.f. = 1.27.

**The correspondence test passes.** An estimator built from scratch in
the Level 4 namespace, run at nonzero reference offsets, reproduces a
derivative that the frozen Level 1–3 chain derives analytically and
encloses by certified interval arithmetic. That is the strongest
available evidence that the Level 4 simulator is simulating the same
model.

---

## 4. The reuse transition

`F'_rho(0)` was fitted separately for each `rho` from the dense
near-zero grid, at the window and order selected once for `F_1`:

| `rho` | fitted `F'_rho(0)` | s.e. | `rho * F_1'(0)` |
|---|---|---|---|
| 0 | 0.0000 | 0.0000 | -0.0000 |
| 0.02 | -0.2981 | 0.0005 | -0.2981 |
| 0.05 | -0.7454 | 0.0013 | -0.7454 |
| 0.1 | -1.4907 | 0.0025 | -1.4907 |
| 0.25 | -3.7268 | 0.0063 | -3.7268 |
| 0.5 | -7.4536 | 0.0125 | -7.4536 |
| 1 | -14.9073 | 0.0251 | -14.9073 |

> **This table is not evidence for `F_rho = rho F_1`, and must not be
> read as such.** The two right-hand columns agree to every printed
> digit, and they agree *exactly*, for an algebraic reason rather than a
> scientific one. Each path contributes
> `rho*mu_reuse + (1-rho)*mu_fresh`; the fit is linear in the data; and
> `mu_fresh` does not depend on `e`, so on a symmetric grid the **odd**
> polynomial basis annihilates it identically. The fresh term therefore
> contributes exactly zero to `a1` whatever the data happen to be, and a
> difference column here would report an identity, not a measurement.
> The row for `rho = 1` carries the only independent information in the
> table; the rest is that row multiplied by `rho`.

What the estimator *can* be asked is whether the assumption underneath
the Level-2 identity holds in the simulated data: that `mu_fresh` has
mean zero and is independent of the stopping event. The `rho = 0` policy
is exactly `E[mu_fresh]`, estimated separately at every grid point:

* across 25 grid points, the largest standardised
  departure of `E[mu_fresh]` from zero is **0.52 sigma**
  (at `e = -0.1500`, estimate -0.000522 ± 0.001001);
* `mu_fresh` is drawn from a stream that is never touched by the
  monitoring loop, and `test_fresh_policy_ignores_the_stopping_selected_data` asserts that under `rho = 0` the next reference error
  is bit-identical to `mu_fresh`;
* `test_fresh_statistic_is_mean_zero_and_uncorrelated_with_selection`
  measures the correlation between `mu_fresh` and the
  stopping-selected `mu_reuse` directly.

### Critical reuse fraction

| Source | `rho_c` | interval |
|---|---|---|
| direct conditional simulator | 0.06708 | [0.06686, 0.06730] (95%) |
| score route | 0.06718 | [0.06700, 0.06736] (95%) |
| **frozen certificate**, `rho_c = 1/(Gamma-1)` | — | [0.03724, 0.34196] (enclosure) |

The measured `rho_c` lies inside the certified enclosure: **True**.
The certified enclosure is wide because it must hold `Gamma` rigorously;
the Monte Carlo interval is narrow but is only Monte Carlo. They are
different kinds of statement and are reported as such.

> **Scope.** `rho_c` is the threshold for **local linear stability of the
> deterministic linearisation at `e = 0`**. It is not a bifurcation
> theorem, and — as Gate 4.1 shows directly — it is *not* where the cycle
> ARL or the stationary dispersion turns around. Crossing `rho_c` and
> "the system changes qualitatively" are different claims.

---

## 5. `H_rho` roots and period-2 candidates

`H_rho(e) = F_rho(e) + e`. A nonzero root `e*` satisfies `F_rho(e*) = -e*`,
and since `F_rho` is odd, `F_rho(F_rho(e*)) = e*` — so `{e*, -e*}` is a
2-cycle **of the deterministic map**. Its multiplier is
`F'(e*) F'(-e*) = [F'(e*)]^2`, because `F'` is even.

> The actual recursion is `E_{j+1} = F_rho(E_j) + noise`. A deterministic
> 2-cycle is neither necessary nor sufficient for bimodality of the
> invariant law of the noisy recursion. Nothing below claims otherwise.

**Screening.** Near `e = 0`, `H_rho(e) ≈ (1 - rho|F_1'(0)|) e`, which is
tiny for small `rho`, so Monte Carlo noise alone manufactures sign
changes there. A crossing is accepted only if the grid carries points of
the matching sign at ≥ 3 standard errors from zero on **both** sides.
Rejected crossings are reported, not dropped.

| `rho` | classification | `e*` | s.e. | `F'(e*)` | 2-cycle multiplier | `H(e*)` residual |
|---|---|---|---|---|---|---|
| 0 | **NO-CANDIDATE** | — | — | — | — | — |
| 0.02 | **NO-CANDIDATE** | — | — | — | — | — |
| 0.05 | **NO-CANDIDATE** | — | — | — | — | — |
| 0.1 | **STRONG-CANDIDATE** | 0.14413 | 0.00107 | -0.3761 | 0.1415 ± 0.0193 | 0.00114 (1.1σ) |
| 0.25 | **STRONG-CANDIDATE** | 0.37860 | 0.00047 | 0.1819 | 0.0331 ± 0.0079 | 0.00134 (1.6σ) |
| 0.5 | **STRONG-CANDIDATE** | 0.64953 | 0.00045 | 0.3731 | 0.1392 ± 0.0043 | 0.00059 (0.9σ) |
| 1 | **STRONG-CANDIDATE** | 1.03695 | 0.00037 | 0.5954 | 0.3545 ± 0.0049 | 0.00035 (0.4σ) |

### Screened-out crossings

None: no sub-threshold sign change appeared on the coarse grid.

### Robustness of each candidate

Each sensitivity varies exactly one thing. `e*` is relocated from: a grid
with every second point removed; the first half of the batches (same
seeds, half the paths); and a fully independent-seed run with CRN off.
A separate confirmation simulation is then run **at** `e = ±e*`, because
the interpolated residual is zero by construction and proves nothing.

**`rho = 0.1` — STRONG-CANDIDATE**

| check | value |
|---|---|
| `e*` (95% CI) | 0.14413 [0.14203, 0.14623] |
| CI width | 0.00421 |
| grid halved → shift in `e*` | 0.00001 |
| sample size halved → shift | -0.00144 |
| independent seeds → shift | -0.00273 |
| direct `H(e*)` at `e*` | 0.00114 ± 0.00102 |
| odd-symmetry gap `F(e*)+F(-e*)` | -0.00013 (-0.09σ) |
| `F'(e*)` | -0.3761 ± 0.0256 |
| 2-cycle multiplier `[F'(e*)]²` | 0.1415 ± 0.0193 |

  - direct H(e*) residual z = 1.12
  - symmetry |z| = 0.09
  - grid shift in e* = +0.00001 (CI width 0.00421)
  - Monte Carlo sample shift in e* = -0.00144 (CI width 0.00421)
  - independent seed shift in e* = -0.00273 (CI width 0.00421)

**`rho = 0.25` — STRONG-CANDIDATE**

| check | value |
|---|---|
| `e*` (95% CI) | 0.37860 [0.37767, 0.37952] |
| CI width | 0.00186 |
| grid halved → shift in `e*` | 0.00023 |
| sample size halved → shift | -0.00087 |
| independent seeds → shift | -0.00080 |
| direct `H(e*)` at `e*` | 0.00134 ± 0.00086 |
| odd-symmetry gap `F(e*)+F(-e*)` | 0.00015 (0.12σ) |
| `F'(e*)` | 0.1819 ± 0.0217 |
| 2-cycle multiplier `[F'(e*)]²` | 0.0331 ± 0.0079 |

  - direct H(e*) residual z = 1.55
  - symmetry |z| = 0.12
  - grid shift in e* = +0.00023 (CI width 0.00186)
  - Monte Carlo sample shift in e* = -0.00087 (CI width 0.00186)
  - independent seed shift in e* = -0.00080 (CI width 0.00186)

**`rho = 0.5` — STRONG-CANDIDATE**

| check | value |
|---|---|
| `e*` (95% CI) | 0.64953 [0.64865, 0.65041] |
| CI width | 0.00176 |
| grid halved → shift in `e*` | -0.00056 |
| sample size halved → shift | -0.00097 |
| independent seeds → shift | -0.00050 |
| direct `H(e*)` at `e*` | 0.00059 ± 0.00068 |
| odd-symmetry gap `F(e*)+F(-e*)` | -0.00088 (-0.91σ) |
| `F'(e*)` | 0.3731 ± 0.0057 |
| 2-cycle multiplier `[F'(e*)]²` | 0.1392 ± 0.0043 |

  - direct H(e*) residual z = 0.87
  - symmetry |z| = 0.91
  - grid shift in e* = -0.00056 (CI width 0.00176)
  - Monte Carlo sample shift in e* = -0.00097 (CI width 0.00176)
  - independent seed shift in e* = -0.00050 (CI width 0.00176)

**`rho = 1` — STRONG-CANDIDATE**

| check | value |
|---|---|
| `e*` (95% CI) | 1.03695 [1.03622, 1.03768] |
| CI width | 0.00146 |
| grid halved → shift in `e*` | 0.00000 |
| sample size halved → shift | -0.00058 |
| independent seeds → shift | -0.00020 |
| direct `H(e*)` at `e*` | 0.00035 ± 0.00082 |
| odd-symmetry gap `F(e*)+F(-e*)` | -0.00209 (-1.81σ) |
| `F'(e*)` | 0.5954 ± 0.0041 |
| 2-cycle multiplier `[F'(e*)]²` | 0.3545 ± 0.0049 |

  - direct H(e*) residual z = 0.43
  - symmetry |z| = 1.81
  - grid shift in e* = +0.00000 (CI width 0.00146)
  - Monte Carlo sample shift in e* = -0.00058 (CI width 0.00146)
  - independent seed shift in e* = -0.00020 (CI width 0.00146)

---

## 6. Decision

### `PROCEED-RIGOROUS-PERIOD2`

| # | criterion | result | detail |
|---|---|---|---|
| 1 | direct and score routes to F1'(0) agree within 3 sigma | PASS | gap -0.0215 = 0.67 sigma |
| 2 | direct F1'(0) lies inside the certified Gamma enclosure | PASS | -14.9073 in [-26.849, -2.924] |
| 3 | score route reproduces the certified Gamma enclosure | PASS | Gamma = 15.8857 |
| 4 | estimated map respects the proved odd symmetry | PASS | max |z| = 2.78 |
| 5 | independent-seed replication of the score route agrees | PASS | 0.39 sigma |

Candidates: **4 STRONG**, 0 WEAK, 0 NUMERICALLY-INCONSISTENT, 3 NO-CANDIDATE.

**Reason.** 4 reuse fraction(s) carry a STRONG-CANDIDATE nonzero root of H_rho that survived grid, sample-size and independent-seed perturbation, and the model correspondence check passed.

### What this decision does not assert

* Not that a period-2 orbit of the *noisy* recursion exists. Every root
  here belongs to the deterministic map `F_rho`.
* Not that the invariant law is bimodal. That was not measured to a
  standard that would support the claim, and it is not claimed.
* Not that `F'_rho(0) < -1` implies period-2. Local instability of a
  fixed point is not existence of a 2-cycle; the two are reported
  separately and the roots are found by locating zeros of `H_rho`, not
  inferred from the slope.
* Nothing about `m > 1`, other `(k,h)`, or non-Gaussian innovations.
* Nothing with the force of a proof. This is Monte Carlo.
