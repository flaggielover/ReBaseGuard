# ReBaseGuard Level 4 — Stage C
## Stability-Aware Reuse, ARL Mechanism, and the Reuse-Performance Tradeoff

**Role:** scientific/theoretical lead. Production simulation infrastructure is out of scope
(handled independently). This document defines theory, protocol, interpretation rules, and
proof opportunities *before* full Stage C outcomes.

**Posture:** adversarial. Three pre-specified hypotheses are reported below as false or
ill-posed. Stage D is NOT begun.

---

## PROGRESS CAPSULE

| Field | Value |
|---|---|
| Stage | C (theory + protocol) |
| Steps | 8 / 8 |
| Frozen baseline | Levels 1-3 CLOSED; Stage A CLOSED; Stage B CLOSED-RIGOROUS-PERIOD2 |
| Independent solver check | ARL0 = 465.4434, Gamma = 15.8868, F1'(0) = -14.8868 |
| Hypotheses pre-specified | 7 (H1, H2, H3, H3g, H4, H5, H6) |
| Reported false / ill-posed | 3 (H3 false as stated, H4 ill-posed, H5 false at m=1) |
| Unresolved by design | 1 (H6 - data cannot discriminate two scalings) |
| Blocked | prior-art / novelty-risk update (no OpenAlex key) |
| Closure verdict | **STAGE-C-PARTIAL** |

---

## 0. CORRECTION TO MY OWN PRIOR LEDGER (owed before anything else)

My Level-4 design document recorded `Gamma > 2` as **OPEN / REQUIRES-RIGOROUS-CERTIFICATE**.
That row was **wrong**. The corpus carries a certified enclosure

    Gamma(k=0.5, h=5, m=1) in [3.9243, 27.8494]

labelled CERTIFIED COMPUTER-ASSISTED THEOREM. Since `3.9243 > 2`, the antecedent of the
`rho_c` proposition is **closed, not open**. Your Stage C brief states the premise correctly
and my ledger did not. The status table below supersedes that row.

This correction *helps* the project. But it carries an immediate adversarial consequence that
the phrasing `rho_c = 1/(Gamma-1)` conceals - see 1.2.

---

## 1. AUDIT OF THE LOGICAL CHAIN

### 1.1 What follows

The chain is sound, and shorter than it looks:

1. `F_rho(e) = rho * F_1(e)` for **all** `e` - not merely a linearization. The fresh block is
   independent of the alarm event and mean-zero, so it contributes nothing to the conditional
   mean at any `e`. **PROVED.**
2. `F_1'(0) = 1 - Gamma`. **PROVED** (score identity).
3. `Gamma in [3.9243, 27.8494]`, hence `Gamma > 2`, hence `F_1'(0) < -1`.
   **RIGOROUSLY CERTIFIED.**
4. Therefore `|F_rho'(0)| = rho(Gamma-1)` crosses 1 at `rho_c = 1/(Gamma-1) in (0,1)`.
   **PROVED**, with antecedent certified.
5. Stage B: at `rho = 1` there is a certified nonzero symmetric attracting 2-cycle,
   `e* in [1.028724, 1.044724]`, `lambda_2 in [0.108148, 0.832532]`.

Two structural facts are stronger than conjecture and come for free:

- **`lambda_2 = [F_1'(e*)]^2 >= 0` identically.** The multiplier is a perfect square, so it
  can never approach `-1`. A period-doubling cascade off this branch is **structurally
  impossible**, not merely unobserved. This is a proof, not a numerical finding.
- Odd symmetry of `F_rho` is proved, so the 2-cycle condition reduces to the scalar equation
  `g(e*) = 1/rho` with `g(e) = -F_1(e)/e`. The entire `rho`-family collapses onto one curve.

### 1.2 The certificate pins rho_c only to a wide interval

`rho_c = 1/(Gamma-1)` is a *point* only if `Gamma` is a point. It is not - it is a certified
interval of width factor 7.1. Propagating it:

| basis                    |   Gamma |   rho_c |
|:-------------------------|--------:|--------:|
| certified lower endpoint |  3.9243 |  0.3420 |
| MC point estimate        | 15.8743 |  0.0672 |
| solver (this session)    | 15.8868 |  0.0672 |
| certified upper endpoint | 27.8494 |  0.0372 |

The rigorous statement is `rho_c in [0.0372, 0.3420]` - a **ninefold range**. The value
`0.067` is a *numerical* estimate from two independent routes (Monte Carlo and this session's
deterministic solve), not a certified one. **Any Stage C claim locating a threshold "at
rho_c" inherits this ninefold uncertainty unless it uses the point estimate, in which case
it is numerical, not certified.**

### 1.3 What does NOT follow

- **No bifurcation claim at `rho_c`.** Stage B certifies the orbit at `rho = 1` only - a
  single parameter value. There is no continuation argument linking that orbit to `rho_c`,
  and Phase 2B explicitly rejected the normal-form route (boundary layer; no cubic normal
  form). The defensible phrase is "the origin changes local stability at `rho_c`";
  "period-doubling bifurcation at `rho_c`" is **CONJECTURAL** and must not appear in a claim
  sentence.
- **No branch-existence claim for intermediate `rho`.** That the 2-cycle exists for every
  `rho in (rho_c, 1]` requires `g` strictly decreasing. Verified on grids `N = 50/100/200`;
  **unproved**.
- **`F'(0) < -1` alone gives no global dynamics.** It is a statement about an infinitesimal
  neighbourhood of a repelling fixed point. Nothing about attractors, invariant measures, or
  observable behaviour follows from it.
- **No stochastic conclusion whatsoever.** Stage B is a theorem about the deterministic
  conditional-mean skeleton `F_1`. It says nothing about the noisy recursion - see 4.

### 1.4 Theorem-status table

Full table in `stagec_theorem_status.csv`. Status distribution:

| status                                     |   claims |
|:-------------------------------------------|---------:|
| CONDITIONAL IDENTITY                       |        1 |
| CONJECTURAL                                |        2 |
| NUMERICAL                                  |        4 |
| NUMERICAL, regime-restricted               |        1 |
| OPEN                                       |        1 |
| PROVED                                     |        4 |
| PROVED (conditional, antecedent certified) |        1 |
| REFUTED                                    |        1 |
| REFUTED at the frozen point                |        1 |
| RIGOROUSLY CERTIFIED                       |        5 |

---

## 2. THE ARL MECHANISM

Let `A(e)` be the expected in-control run length of a cycle begun with reference error `e`.

### 2.1 Properties established

- **`A(e) = A(-e)`. PROVED** - the same reflection symmetry that makes `F_rho` odd.
- **`A(e) < A(0)` for every `e != 0`, and `A` is strictly decreasing in `|e|`** on the
  computed range `|e| <= 10`. **NUMERICAL** (Richardson-extrapolated, two grids). This is the
  mechanism: reference error is *always* harmful to in-control run length, monotonically.
  `A(0) = 465.4434`.
- **Renewal-reward identity** `ARL_rho = integral of A dpi_rho`. **CONDITIONAL IDENTITY** -
  exact given an invariant law `pi_rho`, whose existence is OPEN (4.3). Verified numerically
  to 4 significant digits at every `rho` tested: at `rho=0.5`, `E_pi[A] = 81.567` vs
  simulated cycle length `81.613`.

### 2.2 The Taylor sign condition - and its very small radius of validity

The brief asks for the symmetric expansion `A(e) ~ A(0) + c_2 e^2` with `c_2 < 0`. The sign
is robust; **the expansion is not**. Fitting `c_2` over shrinking windows:

| window | `c_2` |
|---|---|
| `|e| <= 0.40` | -7303 |
| `|e| <= 0.30` | -10365 |
| `|e| <= 0.20` | -12543 |
| `|e| <= 0.15` | -14407 |
| limit as `e -> 0` (deficit ratio) | **~ -15190** |

The fitted coefficient drifts by a factor of 2 across windows, and the log-log exponent of
the deficit `A(0) - A(e)` is 1.18 at `W=0.5`, 1.45 at `W=0.3`, 1.83 at `W=0.1` - approaching
2 only as `W -> 0`. The clean limit is `c_2 ~ -1.52e4`, confirmed by the deficit ratio
`(A(0)-A(e))/e^2 -> 15188` as `e -> 0.0025`.

**The adversarial point:** `c_2 ~ -1.5e4` against `A(0) ~ 465` means the quadratic term
consumes the entire run length by `|e| ~ 0.175`. The expansion is valid only for
`|e| <~ 0.02`, and **the stationary law puts only 1.6% of its mass there** (measured
`P(|e| < 0.02) = 0.0159` at `rho=0`, `0.0087` at `rho=1`). A second-order ARL argument is
mathematically correct and **practically vacuous at this operating point** - it describes a
regime the process almost never occupies. Any Stage C narrative resting on the quadratic
expansion must say so.

---

## 3. STABILITY-AWARE REUSE

### 3.1 The rule, and which certificate endpoint is admissible

Target `|F_rho'(0)| <= 1 - delta`, giving `rho_safe(delta) = (1-delta)/(Gamma-1)`.

**Which `Gamma` may be substituted is a correctness question, not a taste question.** The
guarantee must hold for the unknown true `Gamma`. Since `rho_safe` is *decreasing* in
`Gamma`, only the **upper** endpoint `Gamma = 27.8494` yields a valid guarantee. Using the
lower endpoint `3.9243` gives `rho_safe` five times too large and is **invalid** - it is the
direction that silently breaks the guarantee.

|   delta |   certified_lower_INVALID |   certified_upper_VALID |   point_estimate |
|--------:|--------------------------:|------------------------:|-----------------:|
|  0.0500 |                    0.3249 |                  0.0354 |           0.0639 |
|  0.1000 |                    0.3078 |                  0.0335 |           0.0605 |
|  0.2000 |                    0.2736 |                  0.0298 |           0.0538 |
|  0.5000 |                    0.1710 |                  0.0186 |           0.0336 |

**Cost of rigour:** the conservatism factor is `(Gamma_hi-1)/(Gamma_pt-1) = 1.805`. A
certificate-aware rule permits 1.81x less reuse than a point-estimate rule. That is a
*modest* price - notably better than the 7.1x enclosure width, because the map
`Gamma -> 1/(Gamma-1)` compresses. This is a genuinely favourable finding for the method.

**Estimated variant.** With `Gamma_hat` from data one may use
`rho_safe_hat = (1-delta)/(Gamma_hat_upper - 1)` with `Gamma_hat_upper` an upper confidence
limit. Statistical confidence is **not** mathematical certification: the resulting statement
is "valid with probability >= 1-alpha" and must never be reported in the same register as the
Arb enclosure.

### 3.2 At delta = 0.1 the certificate-aware rule permits rho = 0.0335

This is 3.4% reuse. **The stability-aware rule, applied honestly, is nearly indistinguishable
from fresh-only re-baselining.** Whatever Stage C claims about the benefit of reuse, it
cannot claim that a *stability-guaranteed* reuse fraction is practically substantial at this
operating point. The interesting values `rho = 0.2, 0.5` all violate the guarantee.

---

## 4. STOCHASTIC LAYER - MINIMAL ASSUMPTIONS AND WHAT IS ACTUALLY TRUE

### 4.1 The irreducible noise obstruction (structural, and it bounds the whole programme)

Write `E_{j+1} = rho(E_j + Z_tau_j) + (1-rho) m^(-1/2) V_j`. Increasing `m` shrinks the fresh
block's variance as `1/m` - but `Z_tau`, the reused terminal statistic, is **itself random and
its variance does not shrink with `m` at all**. Measured conditional variance of `Z_tau`
given `e`:

|      e |   E_ztau |   Var_ztau_cond |     sd |
|-------:|---------:|----------------:|-------:|
| 0.0000 |   0.0005 |          4.0641 | 2.0160 |
| 0.2500 |  -1.8248 |          0.6931 | 0.8325 |
| 0.5000 |  -1.9125 |          0.4780 | 0.6914 |
| 1.0000 |  -2.0568 |          0.5271 | 0.7260 |
| 1.0400 |  -2.0739 |          0.5338 | 0.7306 |
| 1.5000 |  -2.2991 |          0.6178 | 0.7860 |
| 2.0000 |  -2.6200 |          0.7096 | 0.8424 |

At the orbit amplitude `e* ~ 1.0367` the per-cycle noise SD is 0.731 - **70.5% of the orbit
amplitude** - and this floor is independent of `m`. Confirmed: `Var(Z_tau) = 5.638` at
`rho=1` for every `m` in `{1,4,16,64,256}` (`noise_floor.csv`).

**Consequence.** The `m -> infinity` limit of the recursion is *not* the deterministic
skeleton; it is `E_{j+1} = rho(E_j + Z_tau)`, still stochastic with O(1) noise. **No amount of
re-baselining data recovers the Stage B skeleton.** This is the sharpest structural statement
in Stage C, and it is not a numerical artifact - it follows from the model definition.

### 4.2 Skeleton instability does not imply bimodality - the dissociation persists in m

Measured bimodality onset (central-dip `z`) against `rho_c`:

|        m |   onset_rho |   dip_at_onset |
|---------:|------------:|---------------:|
|   1.0000 |      0.5500 |        -0.4109 |
|   2.0000 |      0.4500 |        -1.5612 |
|   4.0000 |      0.3500 |        -1.0074 |
|   8.0000 |      0.2750 |        -2.0513 |
|  16.0000 |      0.2250 |        -4.1584 |
|  32.0000 |      0.2000 |       -14.3218 |
|  64.0000 |      0.1750 |       -18.2814 |
| 128.0000 |      0.1500 |       -14.1117 |

Onset falls with `m` - consistent with 4.1's noise shrinking partially - but the ratio
`onset/rho_c` only falls from 8.19 to 2.23 over `m = 1 -> 128`. Two scalings fit:

- pure power law `rho_onset = 0.519 m^(-0.270)` -> limit **0**, would eventually reach
  `rho_c`;
- plateau `rho_onset = 0.094 + 0.460 m^(-0.430)` -> limit **0.094 > rho_c = 0.067** (lower
  SSR).

**These cannot be separated by the present data, and 4.1 supplies a mechanism for a nonzero
plateau.** H6 is therefore **UNRESOLVED** and I decline to claim convergence in either
direction. Discriminating requires `m >= 512` with replicate seeds - recommended for Stage D,
not asserted here.

On `rho in (rho_c, 0.55)` at `m=1` the skeleton has an attracting 2-cycle while the invariant
law is significantly **unimodal at zero**. That dissociation is, in my judgement, the most
publishable result in the Level-4 programme: a clean negative result about when deterministic
skeleton analysis fails to describe a noisy monitoring scheme.

### 4.3 Minimal assumptions for the invariant-law programme (roadmap, not results)

| Target | Route | Feasibility |
|---|---|---|
| Existence of `pi_rho` | Feller + tightness. Fold-back of `F_1` (`A` decreasing, `F_1` bounded on compacts) gives a drift bound `E[V(E')] <= gamma V(E) + b`, `V(e)=e^2`, `gamma<1` for `rho` bounded away from 1. | **Stage-C feasible** |
| Uniqueness / Harris recurrence | psi-irreducibility from the absolutely continuous fresh block (`rho<1` gives a Gaussian component of full support, so a minorization on compacts is immediate). | **Stage-C feasible for `rho<1`; `rho=1` genuinely harder** (no fresh component - irreducibility must come from the law of `Z_tau`) |
| Geometric ergodicity | Foster-Lyapunov with the same `V`. | **Stretch** |
| Rigorous bimodality | Requires quantitative control of the density of `pi_rho`, far beyond a Lyapunov argument. | **Level 4+ / abandon** |

**Recommendation: do not attempt rigorous bimodality in Stage C.** Its difficulty is out of
proportion to its contribution, and 4.1 suggests the honest result is a *regime restriction*
rather than a theorem.

---

## 5. THE REUSE-PERFORMANCE TRADEOFF, WITH THE INSENSITIVITY GUARD

### 5.1 H4 (sample efficiency) is ill-posed under the frozen mixing convention

Under the frozen recursion a fresh block of size `m` is drawn **every cycle for every
`rho < 1`**; the reuse fraction weights the blocks but does not reduce how many fresh
observations are consumed. Fresh observations per cycle is `m` for all `rho<1` and `0` only
at exactly `rho=1` - a discontinuity, not a trend.

So "reuse improves sample efficiency" cannot be tested as stated: at fixed `m`, fresh cost
per unit time varies **only** through cycle length, which is H3. **H4 must be rejected or
reformulated**; I recommend rejecting it and folding its content into H3. Reporting a
sample-efficiency benefit under this convention would be an artifact of the parameterization,
not a finding. If Stage D wants a genuine efficiency axis, the *model* must change (e.g. `m`
allowed to depend on `rho`) - and that is a modification of the frozen baseline requiring
explicit approval.

### 5.2 In-control cycle length is non-monotone in rho

|    rho |   cycle_len_sim |   cycle_len_se |   E_pi_A |   frac_gt_half |   frac_in_taylor_window |
|-------:|----------------:|---------------:|---------:|---------------:|------------------------:|
| 0.0000 |         82.7225 |         0.1455 |  82.9282 |         0.6170 |                  0.0159 |
| 0.0340 |         85.1117 |         0.1498 |  85.2596 |         0.6061 |                  0.0163 |
| 0.0605 |         87.3918 |         0.1538 |  87.3453 |         0.5962 |                  0.0168 |
| 0.1000 |         89.9868 |         0.1584 |  89.9813 |         0.5841 |                  0.0175 |
| 0.2000 |         94.8570 |         0.1665 |  94.8644 |         0.5605 |                  0.0186 |
| 0.5000 |         81.6129 |         0.1427 |  81.5670 |         0.6203 |                  0.0152 |
| 0.8000 |         56.7424 |         0.0981 |  56.8631 |         0.7390 |                  0.0098 |
| 1.0000 |         50.0695 |         0.0875 |  50.0407 |         0.7749 |                  0.0087 |

Cycle length **rises** from 82.7 (fresh) to a maximum near `rho ~ 0.2` (94.9) before falling
to 50.1 at `rho=1`. H3 as stated ("reuse shortens cycles") is **FALSE**; the true statement
is non-monotone with an interior maximum. `E_pi[A]` tracks simulated cycle length to 4 digits
throughout - the renewal identity is doing real work.

### 5.3 The insensitivity guard - and it bites

A longer in-control cycle is worthless if bought by insensitivity, so cycle length is
evaluated **jointly** with out-of-control delay. Because the solver's innovation is
`z ~ N(-e,1)`, a true shift `mu` enters as `A(|e-mu|)`; delay was computed by direct
simulation from the stationary reference-error law (5 independent seeds):

|    rho |     cyc |   cyc_se |   dly0.5 |   dly0.5_se |   dly1.0 |   dly1.0_se |   dly2.0 |   dly2.0_se |
|-------:|--------:|---------:|---------:|------------:|---------:|------------:|---------:|------------:|
| 0.0000 | 83.2650 |   0.1547 |  74.1347 |      0.1824 |  53.5506 |      0.4846 |  16.2670 |      0.0880 |
| 0.0605 | 86.9756 |   0.1605 |  77.5829 |      0.1603 |  53.8166 |      0.1995 |  14.6302 |      0.1033 |
| 0.2000 | 94.9323 |   0.2139 |  81.8990 |      0.2664 |  52.8182 |      0.2007 |  11.8680 |      0.1146 |
| 0.5000 | 81.5777 |   0.2387 |  77.2628 |      0.3047 |  58.5433 |      0.1793 |  12.5395 |      0.1051 |
| 0.8000 | 57.0036 |   0.1867 |  62.0456 |      0.2659 |  60.0894 |      0.2116 |  22.3196 |      0.2645 |
| 1.0000 | 50.1190 |   0.1845 |  52.9064 |      0.6125 |  52.6745 |      0.2416 |  28.6063 |      0.2756 |

Read adversarially:

- **`rho = 0.2` Pareto-dominates fresh on two axes at once**: longer in-control cycle
  (94.93 +/- 0.21 vs 83.27 +/- 0.15) *and* shorter delay at `mu=2` (11.87 +/- 0.11 vs
  16.27 +/- 0.09). Both gaps are tens of standard errors. A real, reproducible, non-obvious
  result.
- **The dominance is not uniform in `mu`.** At `mu = 0.5`, `rho=0.2` is *worse* than fresh
  (81.90 vs 74.13). The honest claim is "Pareto-dominant for moderate-to-large shifts,
  dominated for small shifts" - never an unqualified "better".
- **`rho = 1` is the worst configuration on the in-control axis but the best on delay at
  `mu=0.5` (52.91).** Large reference-error dispersion makes the chart trigger-happy, which
  *helps* small-shift delay and *hurts* everything else. This is exactly the confound the
  guard exists to catch: **cycle length and delay must never be aggregated into one score.**

### 5.4 Dead-time accounting

At `m=1` the fresh-observation duty cycle is ~1-2% of wall-clock time for all `rho<1`,
dropping to 0 at `rho=1`; at `m=20` it is 17-26%. Dead time matters at large `m` and is
essentially free at `m=1`, reinforcing 5.1: the frozen convention gives reuse no efficiency
lever at the frozen operating point.

---

## 6. PRE-SPECIFIED HYPOTHESES

Full table with endpoints, uncertainty measures, and failure rules in
`stagec_hypotheses.csv`. Uncertainty is reported as replicate-seed standard errors and
interval enclosures - **not p-values**; nothing here is a significance test against a null of
no effect.

| id   | hypothesis                                            | stage_c_status                                                                           |
|:-----|:------------------------------------------------------|:-----------------------------------------------------------------------------------------|
| H1   | Origin loses local stability at rho_c=1/(Gamma-1)     | Skeleton only. TRUE by proof, antecedent certified.                                      |
| H2   | Deterministic 2-cycle exists for all rho in (rho_c,1] | Supported numerically; certified only at rho=1.                                          |
| H3   | Reuse shortens in-control cycle length                | FALSE as stated: non-monotone. rho=0.2 gives 94.9 > fresh 83.3.                          |
| H3g  | Cycle-length gain is not bought by insensitivity      | PASSES at rho=0.2 for mu=1,2; FAILS at mu=0.5.                                           |
| H4   | Stability-aware reuse improves sample efficiency      | ILL-POSED under the frozen convention: m fresh obs drawn every cycle for every rho<1.    |
| H5   | Bimodality onset coincides with rho_c                 | FALSE at m=1 (onset 0.55 vs rho_c 0.067); gap narrows with m but does not close.         |
| H6   | Larger m recovers the skeleton prediction             | UNRESOLVED: power-law fit -> 0, plateau fit -> 0.094 > rho_c. Data cannot separate them. |

Three of seven are false or ill-posed. That is the correct outcome of pre-specification: had
these been formulated after seeing the data, all three would have been quietly reshaped into
confirmations.

---

## 7. PROOF OBLIGATIONS (ranked by payoff per unit effort)

1. **`g(e) = -F_1(e)/e` is strictly decreasing on `(0, infinity)`.** Yields existence *and*
   uniqueness *and* attraction of the 2-cycle for the **entire** `rho`-family - strictly more
   general than the certified single point at `rho=1`. Uses the Fredholm/Arb machinery already
   scoped in Phase 4C. **Highest payoff; recommended as the Stage C/D theorem target.**
2. **`A(e)` strictly decreasing in `|e|`.** Currently numerical; this is the ARL mechanism
   itself and deserves a proof. Monotone-likelihood-ratio or coupling argument on the CUSUM
   hitting time.
3. **Existence + uniqueness of `pi_rho` for `rho<1`** via the drift/minorization pair in 4.3.
   Modest effort, closes an OPEN row, and *retroactively upgrades the renewal identity* from
   conditional to unconditional - which every ARL statement in the programme depends on.
4. **`Var(Z_tau)` bounded below uniformly in `m`** - formalizes 4.1 and turns the noise
   obstruction from a measurement into a theorem. Small effort, high narrative value.
5. Tighten the `Gamma` enclosure. Purely computational; would narrow `rho_c` from a ninefold
   range and reduce the 3.1 conservatism factor below 1.81.

---

## 8. CLAIM-LANGUAGE GUIDE

Full table in `claim_language_guide.csv`. Load-bearing entries:

- **"optimal" - FORBIDDEN.** No optimization theorem over any admissible class exists.
  `rho ~ 0.2` is an interior maximum of a simulated curve over six grid points. Permitted:
  "Pareto-dominant among the `rho` values tested".
- **"first" - FORBIDDEN.** The prior-art search never ran (10). No defensible search basis.
- **"bifurcation at `rho_c`" - FORBIDDEN.** No continuation argument (1.3). Permitted: "local
  stability change of the origin".
- **"stochastic period-2" - FORBIDDEN at `m=1`.** Refuted. Permitted: "oscillatory negative
  feedback", quantified by lag-1 autocorrelation.
- **"improves sample efficiency" - FORBIDDEN.** Ill-posed under the frozen convention (5.1).

---

## 9. CLOSURE VERDICT

| verdict                              | criterion                                                                                                                                                                              | assessment                                                                       |
|:-------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------|
| STAGE-C-CLOSED-MECHANISM-ESTABLISHED | A(e) even + globally decreasing in |e| VERIFIED; renewal identity matches simulation to 4 digits at every rho tested; a Pareto-dominant rho region identified on >=2 of 3 shift sizes. | MET (with the mu=0.5 exception recorded)                                         |
| STAGE-C-PARTIAL                      | Mechanism verified but the reuse-performance tradeoff has no monotone or dominant structure; >=1 pre-specified hypothesis ill-posed.                                                   | ALSO MET: H4 ill-posed, H3/H5 false as stated                                    |
| STAGE-C-BLOCKED                      | The frozen model or an inherited certificate is internally inconsistent.                                                                                                               | NOT met: baseline is consistent; one ledger row of mine was wrong, now corrected |

### **STAGE-C-PARTIAL**

Justification. The mechanism criterion is met: `A` is even and globally decreasing in `|e|`,
the renewal identity reproduces simulated cycle length to four digits at every `rho`, and a
Pareto-dominant reuse region exists at `rho ~ 0.2` for moderate-to-large shifts. Had that
been all, the verdict would be STAGE-C-CLOSED-MECHANISM-ESTABLISHED.

It is not all. Three pre-specified hypotheses failed - H4 is **ill-posed by construction**
under the frozen mixing convention, H3 is **false as stated** (non-monotone), H5 is **false
at `m=1`** (onset 8x above `rho_c`) - and H6 is unresolvable with the present data. A stage in
which the central sample-efficiency hypothesis turns out not to be testable under its own
model convention has not closed. PARTIAL is the honest label, and it is not a failure: the
falsifications are themselves the transferable results.

**BLOCKED is explicitly *not* warranted.** The frozen model is internally consistent; the one
inconsistency found was in **my own** prior ledger (0), not in the baseline.

---

## 10. STAGE D RECOMMENDATIONS (recommendations only - Stage D is NOT begun)

1. **Prove `g' < 0`** (obligation 1). One lemma, whole-family payoff.
2. **Reformulate or drop the efficiency axis.** A genuine sample-cost lever requires changing
   the frozen mixing convention - which needs explicit approval and must not be done silently.
3. **Push `m` to >= 512 with replicate seeds** to settle H6 (plateau vs power law). This is
   the one measurement that decides whether skeleton analysis is ever predictive here.
4. **Report the dissociation as the headline**, not the period-2 orbit. "Certified skeleton
   period-2 that the stochastic system does not exhibit" is stronger and more transferable
   than a fragile positive claim.
5. **Second witness, non-Gaussian.** Per the Phase-4D audit, an exponential-family witness
   adds more generality per unit effort than a third Gaussian detector.
6. **Close the prior-art gap before drafting.** Novelty risk now exceeds mathematical risk in
   this project and has been unquantified for two stages.

---

## 11. BLOCKED ITEM - NOVELTY-RISK UPDATE

The brief requests a novelty-risk update. **It cannot be produced.** The scholarly connector
requires an OpenAlex API key on every request and none is configured; the credential request
issued in the previous session was never answered. I have not substituted recalled citations,
because fabricated references in a novelty assessment are worse than an acknowledged gap.

Required searches, once a key is available: post-alarm restart in repeated sequential change
detection; self-starting and adaptive control charts with estimated or recursively-updated
reference parameters; iterated random functions and invariant measures; multi-cyclic quickest
detection; computer-assisted periodic-orbit proofs via interval arithmetic; noisy
one-dimensional maps with bimodal stationary laws.

---

*All numerical values above were recomputed in this session and read back from the saved
CSVs. Solver validation: ARL0 = 465.4434 and Gamma = 15.8868 against the frozen baseline's
465.4 and 15.885. The protected Level 1-3 certificate is untouched; no Monte Carlo result is
labelled as a theorem anywhere above.*
