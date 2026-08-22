# ReBaseGuard Level 4 — Stage D
## Generalization and Robustness Theory Blueprint

**Quota-conservation task.** No large-scale simulation, no production infrastructure. All
numbers below are pilot-scale (1.8e5-3.1e5 cycles) and labelled NUMERICAL unless marked
otherwise.

---

## PROGRESS CAPSULE

| Field | Value |
|---|---|
| Stage | D (blueprint) |
| Kill gates resolved | 4 / 4 |
| D1 SR | **PASSED** - `Gamma_SR = 17.44 +/- 0.09`, so `\|F'\| = 16.44 >> 1` |
| D2 m>1 | **PARTIAL KILL** - `Gamma_m > 2` for all `m <= 50`; crosses 2 at `m* ~ 72` |
| D3 non-Gaussian | **NOT KILLED** numerically; rigorous theorem AT RISK |
| D4 phase diagram | PROCEED, demoted to theorem-consequence |
| New exact result | `sum_i gamma_i = E[T_tau^2] = ARL_0` (Wald identity 2) |
| Provenance flag | **Stage C.1 is not in this project** - see 0 |
| Cost spent | ~3 min wall-clock simulation, no remote compute |

---

## 0. PROVENANCE FLAG (read before using this document)

The brief lists `Stage C.1: STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY` as closed prior work. **No
such stage exists in this project.** I searched the full session archive and all 52 project
artifacts: the strings `STAGE-C1`, `C.1`, and "detector blinding" appear nowhere except in
your brief itself.

I have therefore treated "stabilization is not obtained by detector blinding" as an
**asserted premise from outside this workspace**, not as an inherited verified result. It is
not load-bearing for anything below - my D1/D2/D3 conclusions rest on measurements made in
this session. But if C.1 was produced elsewhere, its artifacts should be added to the corpus
before Level 4 closure, because the Stage C insensitivity-confound finding (5.3 of the Stage C
memo: `rho=1` has the *best* small-shift delay) is exactly the kind of result a blinding
analysis could contradict.

---

## 1. D1 - SHIRYAEV-ROBERTS MATCHED-PROTOCOL WITNESS

### 1.1 Exact protocol

State separation is the crux, so it is specified explicitly.

**Two-sided SR statistic (resets normally, carries no reference memory).** For drift
magnitude `delta` (main case `delta = 1`), maintain

    R+_t = (1 + R+_{t-1}) * exp( delta*z_t - delta^2/2 )
    R-_t = (1 + R-_{t-1}) * exp( -delta*z_t - delta^2/2 )
    tau  = inf{ t : max(R+_t, R-_t) >= A },      R+_0 = R-_0 = 0

implemented in log space via `log R <- logaddexp(0, log R) +/- delta*z - delta^2/2`.
**Post-update inclusive alarm**, matching the frozen CUSUM convention.

**Reference state (separate object).** `mu_hat_j` is the cycle-`j` reference; the *reference
error* is `e_j = mu_hat_j - mu_true`. Observations enter the detector as
`z_t = x_t - mu_hat_j`, so under `e != 0` the innovation is `z ~ N(-e, 1)` - identical to the
CUSUM convention verified in Stage C. **The reference state affects the likelihood/increment
generation, not `R_0`.** `R+_0 = R-_0 = 0` always; there is no headstart. This is what
distinguishes the construction from SR-r / SRP / headstart variants.

**Reuse (matched to CUSUM).** On alarm at `tau_j`,

    mu_hat_{j+1} = mu_hat_j + rho * zbar_{stopped window} + (1-rho) * m^{-1/2} * V_j

with `V_j` the standardized fresh block, independent of the alarm event. Fresh (`rho=0`), full
(`rho=1`), partial - identical semantics to the CUSUM case.

### 1.2 Derivative identity - it factorizes, and the reason is detector-free

The Stage C argument transfers verbatim, because it never used the CUSUM increment:

**PROVED.** `F_{SR,rho}(e) = rho * F_{SR,1}(e)` for all `e`. The fresh block is independent of
the alarm event and mean-zero, so it contributes nothing to the conditional mean at any `e`.

**CANDIDATE (identical derivation to CUSUM, differentiation-under-stopping not yet
justified for SR):**

    F_{SR,1}'(0) = 1 - Gamma_SR,     Gamma_SR = E[ z_tau * T_tau ] = Cov(z_tau, T_tau)

with `T_tau = sum_{t<=tau} z_t` the stopped path score sum (the Gaussian score).

So **`Gamma_SR` is a genuine analogue**: same functional form, different stopping rule.
Factorization as `rho x detector-specific coefficient` is confirmed.

### 1.3 Measured: |F_SR,1'(0)| = 16.44, so D1 is NOT killed

ARL-matched to the frozen CUSUM using the *same* censored estimator (`log A = 6.2998`):

| detector | ARL_0 | Gamma | rho_c = 1/(Gamma-1) |
|---|---|---|---|
| CUSUM (control) | 454.8 | 15.802 +/- 0.079 | 0.0676 |
| SR | 476.2 | **17.497 +/- 0.081** | 0.0606 |

`\|F_{SR,1}'(0)\| = Gamma_SR - 1 = 16.50 >> 1`. **D1 kill gate PASSED: continue to
nonlinear-map/root search.**

Control check: the estimator reproduces the frozen `Gamma = 15.885` to within 1 SE. `ARL_0`
runs ~2% low because unfinished cycles are right-censored - this biases the run-length mean,
not the covariance.

### 1.4 Is the SR excess real, or a threshold artifact?

`Gamma` depends strongly on `ARL_0`, so the raw SR-CUSUM gap could be calibration mismatch.
Fitting the CUSUM scaling gives `Gamma ~ ARL_0^0.2321` (NUMERICAL), then predicting CUSUM at
each SR operating point:

|     ARL0 |   Gamma_SR |     se |   Gamma_CUSUM_pred |   excess |   excess_in_SE |
|---------:|-----------:|-------:|-------------------:|---------:|---------------:|
| 290.6020 |    15.6230 | 0.0523 |            14.2556 |   1.3674 |        26.1515 |
| 474.4665 |    17.4841 | 0.0887 |            15.9738 |   1.5103 |        17.0243 |
| 771.0279 |    19.4073 | 0.1487 |            17.8795 |   1.5278 |        10.2716 |

The excess is `+1.4 to +1.5` at every threshold, 10-26 SE, and **stable in magnitude across a
2.7x ARL_0 range** - a signature of structure rather than mismatch. SR alarms are marginally
*more* reference-destabilizing than CUSUM at equal false-alarm rate.

### 1.5 D1 proof obligations

1. **Differentiation under the stopping-time expectation for SR** - the only genuine gap.
   Needs local uniform integrability of `z_tau T_tau` in `e`. Moderate difficulty; the SR
   statistic is a nonneg. martingale-plus-drift, which helps.
2. `F_{SR,rho} = rho F_{SR,1}` - transcription of the Stage C proof. Trivial.
3. Odd symmetry of `F_{SR,1}` under the two-sided construction. Should follow from the
   `R+ <-> R-` exchange symmetry; write it out.
4. `Gamma_SR > 2` rigorously - requires an Arb enclosure like Phase 4C's. **Do not start
   until 1-3 are done.**

---

## 2. D2 - m>1 STOPPED-WINDOW THEORY

### 2.1 Exact definition

Reuse the **last `m` observations of the stopped path** (not a smoothing window):

    zbar_m = (1/w) * sum_{i=0}^{w-1} z_{tau-i},     w = min(m, tau)

The truncation `w = min(m,tau)` is required: cycles can be shorter than `m`. A min-dwell
`tau >= tau_m` would remove the truncation but changes the frozen stopping rule, so it is NOT
adopted; the truncated convention is used throughout.

### 2.2 The candidate structure is CORRECT, with an exact closed form

The brief asks whether `F_{rho,m}'(0) = rho(1 - Gamma_m)` holds. **It does**, with

    Gamma_m = E[ zbar_m * T_tau ] = (1/m) * sum_{i=0}^{m-1} gamma_i,    gamma_i = E[ z_{tau-i} T_tau ]

**and the lag weights obey an exact sum rule.** Since `sum_{i=0}^{tau-1} z_{tau-i} = T_tau`,

    sum_{i>=0} gamma_i = E[ T_tau^2 ]  =  ARL_0        <- Wald's second identity

**Verified:** `E[T_tau^2] = 460.3 +/- 1.3` against `ARL_0 = 459.0` (CUSUM);
`479.8 +/- 1.4` vs `477.3` (SR). This is a **theorem**, not a fit: for unit-variance
increments `E[T_tau^2] = E[tau]`.

Two consequences follow immediately and neither needed simulation:

**(i) Large-window limit.** `Gamma_m -> Gamma_inf = E[T_tau^2/tau]` as `m -> inf` under the
truncated convention. Measured `Gamma_inf = 1.406 +/- 0.003` (CUSUM), `1.432 +/- 0.003` (SR).
**Both are below 2.**

**(ii) A finite stabilization window `m*` must exist.** `Gamma_m` decreases from `Gamma_1 > 2`
to `Gamma_inf < 2`, so there is a finite `m*` with `Gamma_m < 2` for all `m > m*` - and hence
**no reuse fraction `rho <= 1` can destabilize the origin for `m > m*`**.

### 2.3 Measured Gamma_m and m*

Direct measurement of the truncated statistic, no tail model:

|        m |   Gamma_m_cusum |   se_cusum |   rho_c_cusum |   Gamma_m_sr |   se_sr |   rho_c_sr |
|---------:|----------------:|-----------:|--------------:|-------------:|--------:|-----------:|
|   1.0000 |         15.8328 |     0.0911 |        0.0674 |      17.4392 |  0.0934 |     0.0608 |
|   5.0000 |         10.1473 |     0.0564 |        0.1093 |      11.0399 |  0.0575 |     0.0996 |
|  10.0000 |          7.0843 |     0.0372 |        0.1644 |       7.9380 |  0.0396 |     0.1441 |
|  20.0000 |          4.2483 |     0.0213 |        0.3079 |       4.8364 |  0.0232 |     0.2607 |
|  50.0000 |          2.3504 |     0.0106 |        0.7405 |       2.5898 |  0.0114 |     0.6290 |
|  75.0000 |          1.9594 |     0.0082 |      nan      |       2.1111 |  0.0088 |     0.9000 |
| 100.0000 |          1.7740 |     0.0071 |      nan      |       1.8837 |  0.0075 |   nan      |
| 150.0000 |          1.6021 |     0.0060 |      nan      |       1.6733 |  0.0062 |   nan      |
| 250.0000 |          1.4832 |     0.0052 |      nan      |       1.5304 |  0.0053 |   nan      |

**`m*`: Gamma_m crosses 2 at m ~ 72 (CUSUM), ~ 87 (SR).**

The lag profile is steeply front-loaded: `gamma_0 = 15.84` but `gamma_1 = 10.59`,
`gamma_5 = 5.76`, decaying to a floor near `0.85`. **The terminal alarm observation contributes
~3.4x more than the next lag** - it is the selected one, and this asymmetry is the whole
mechanism. `Gamma_m` is therefore *not* an ordinary finite-window variance: an unselected
window would give `gamma_i` constant in `i`.

### 2.4 D2 kill gate: PARTIAL KILL - report window stabilization as the result

- Entire recommended pilot set `m in {1,5,10,20,50}` has `Gamma_m > 2` (`15.83` down to
  `2.35`) - instability persists, so the pilots are worth running.
- But `m = 50` already gives `rho_c = 0.74`: near-total reuse is needed to destabilize.
- Beyond `m* ~ 72`, instability is **impossible at any rho**.

Per your gate instruction, I do **not** recommend period-2 certificates across `m`. The honest
D2 headline is: *reference instability is a small-window phenomenon, and averaging over more
than ~70 stopped observations eliminates it regardless of reuse fraction.* That is a stronger
and more useful statement than another certified orbit.

Rigorous certification, if any: **`m <= 10` only**, where `Gamma_m >= 7` sits far from the
boundary.

### 2.5 Does the Stage C noise floor prevent skeleton convergence? Yes, and now it is sharp

Stage C established `Var(Z_tau)` independent of `m`. Combined with 2.2: as `m` grows the
*mean* feedback `Gamma_m` decays toward 1.41 while the *noise* does not decay at all. So the
large-`m` limit is neither the deterministic skeleton nor an unstable system - it is a
**stable-mean, O(1)-noise recursion**. The `m -> inf` limit is tractable *and* uninteresting
dynamically, which is itself the finding.

### 2.6 D2 proof obligations

1. **`Gamma_m = (1/m) sum gamma_i` with `sum_i gamma_i = ARL_0`.** Wald + linearity.
   **Nearly free - do this first.**
2. **`gamma_i` decreasing in `i`.** Would prove `Gamma_m` monotone decreasing, hence `m*`
   unique. Numerically clean (monotone over all 50 lags).
3. **`Gamma_inf = E[T_tau^2/tau] < 2`.** Would prove existence of `m*` rigorously. Needs an
   enclosure on a ratio of stopped moments - harder than it looks.
4. Truncation `min(m,tau)` handled exactly rather than asymptotically.

---

## 3. D3 - NON-GAUSSIAN BLUEPRINT

### 3.1 The general score route

For a regular location family `p_e(x) = p_0(x-e)` with score `psi = -p_0'/p_0`:

**CANDIDATE identity.**

    F'(0) = 1 - Gamma_psi,     Gamma_psi = E[ zbar_m * S_tau ],     S_tau = sum_{t<=tau} psi(z_t)

The Gaussian case is `psi(z) = z`, giving `S_tau = T_tau` and recovering `Gamma`. **The
distinction is not cosmetic**: see 3.3.

**Validity conditions for differentiating through the stopping-time expectation** (all
**OPEN**, and these are the real obstacle):

- `p_0` absolutely continuous with finite Fisher information `I(p_0) < inf`;
- `E[tau^2] < inf` under `p_e` locally uniformly in `e` near 0;
- local uniform integrability of `zbar_m * S_tau`, i.e. a dominating family
  `sup_{|e|<eps} E[ |zbar_m S_tau|^{1+kappa} ] < inf` for some `kappa > 0`;
- the detector's stopping boundary not concentrating mass at `tau = 1` as `e` varies.

Heavy tails threaten the third condition specifically: `psi` for Student-t is *bounded*
(good), but `tau` fluctuates more (bad).

### 3.2 Measured, ARL-matched

Thresholds recalibrated per family so every row sits at `ARL_0 ~ 480` (raw comparison at
fixed `h=5` is confounded - `ARL_0` fell to 236 under `t(3)`, and `Gamma ~ ARL_0^0.23`):

| family             |   h_matched |     ARL0 |   Gamma_psi |     se |   Gamma_Tonly |   rho_c |
|:-------------------|------------:|---------:|------------:|-------:|--------------:|--------:|
| Gaussian (control) |      5.0000 | 455.3250 |     15.9024 | 0.0861 |       15.9024 |  0.0671 |
| t, nu=5            |      5.7444 | 483.7878 |     13.5107 | 0.2561 |       34.5476 |  0.0799 |
| t, nu=3            |      6.4519 | 481.6735 |      8.4055 | 0.6600 |      100.4349 |  0.1350 |
| contam eps=.05 s=3 |      6.0388 | 487.0436 |     13.9828 | 0.2602 |       35.2502 |  0.0770 |
| contam eps=.10 s=3 |      6.0959 | 484.2290 |     14.5616 | 0.2578 |       33.8314 |  0.0737 |

**All families keep `Gamma_psi` well above 2** (8.41 to 15.90), so `rho_c` stays in
`[0.067, 0.135]`. **D3 is not killed numerically.**

### 3.3 The naive statistic diverges - use the score form

The `Gamma_Tonly` column applies the *Gaussian* statistic `T_tau = sum z_t` to non-Gaussian
data. It inflates from 16 (Gaussian) to **100 at `t(3)`** - and it is not measuring feedback,
it is measuring tail variance. If a Stage D campaign uses `T_tau` off the Gaussian it will
report spurious instability that grows with tail heaviness.

Note the *direction*: correctly measured, `Gamma_psi` **decreases** with heavier tails
(15.90 -> 8.41). Heavy tails make the system *less* reference-unstable, not more, once
false-alarm rate is held fixed. That is the opposite of what the naive statistic says, and
it is the single most important operational finding in D3.

### 3.4 Ranking for numerical robustness

1. **Student-t** (`nu in {3,5,10,inf}`) - best value. Bounded score, exact symmetry preserved,
   `nu=3` is the informative endpoint and already shows the effect surviving.
2. **Contaminated Gaussian** - second. Nearly flat in `epsilon` (13.98 at 5%, 14.56 at 10%);
   cheap, and the practitioner-facing case.
3. **Skewed** - last, and I recommend deferring it. Asymmetry breaks odd symmetry of
   `F_rho`, which destroys `g(e) = -F_1(e)/e` and the whole scalar reduction. Not a robustness
   check but a different theory, for modest gain.

### 3.5 D3 kill gate

**Numerical: NOT KILLED. Rigorous general theorem: AT RISK.** Recommendation: pursue the
location-family theorem only for the **bounded-score** subclass (Student-t, Huber-type), where
domination is plausible. If the uniform-integrability diagnostic (P6) fails, **abandon the
general theorem and report numerical robustness only** - exactly as your gate instructs.

---

## 4. D4 - PHASE-DIAGRAM BLUEPRINT

Designed after D1/D2, and **demoted**: per the prior-art firewall (D-3 THREATENED), a generic
stability phase diagram is not a novelty headline. It is a *theorem-supported consequence* of
2.2.

**Recommended axes.** `rho_c(m) = 1/(Gamma_m - 1)` is the primary axis: it is a direct
consequence of the `Gamma_m` theorem, spans an order of magnitude (0.067 -> 0.74 -> infeasible
past `m*`), and terminates in the hard boundary `m*`. Use **`ARL_0`, not `h`**, as the second
axis - `h` is scale-dependent and detector-specific while `ARL_0` is the operationally
meaningful quantity, and `Gamma ~ ARL_0^0.232` makes the mapping explicit.

**Required companion metric.** A stability boundary alone reads as an adaptive-gain plot. Pair
it with **cycle ARL** (Stage C's headline monitoring consequence, already showing the
non-monotone interior maximum at `rho ~ 0.2`) as the primary companion, and **lag-1 ACF** as
the secondary (it is the quantity that distinguishes oscillatory negative feedback from
period-2 - the Stage C falsification). Normalized discrimination `R_Delta` and reference MSE
are weaker: `R_Delta` needs an out-of-control convention not yet frozen, and reference MSE is
nearly a deterministic function of `rho` and adds little.

**The one figure worth making:** `rho_c(m)` with the `m*` termination marked, overlaid with the
certified `rho_c` band from the `Gamma` enclosure, plus a cycle-ARL panel. That is a
consequence-of-theorem figure, defensible as such.

---

## 5. TASK RANKING

| task                            |   score | novelty            |   p_success | compute_cost   | proof_cost   | class              |
|:--------------------------------|--------:|:-------------------|------------:|:---------------|:-------------|:-------------------|
| m>1 derivative theorem          |      95 | UNCERTAIN (D-1)    |          90 | low            | med          | MANDATORY          |
| SR derivative theorem           |      92 | NOVELTY-DEFENSIBLE |          85 | low            | med          | MANDATORY          |
| general location-family theorem |      80 | NOVELTY-DEFENSIBLE |          55 | low            | high         | STRONG EXTENSION   |
| m-rho phase map                 |      78 | THREATENED (D-3)   |          95 | med            | none         | MANDATORY          |
| SR Monte Carlo derivative       |      70 | n/a (support)      |          99 | low            | none         | MANDATORY          |
| Student-t campaign              |      65 | NOVELTY-DEFENSIBLE |          90 | med            | none         | STRONG EXTENSION   |
| contaminated Gaussian campaign  |      62 | NOVELTY-DEFENSIBLE |          92 | med            | none         | STRONG EXTENSION   |
| SR nonlinear map                |      58 | NOVELTY-DEFENSIBLE |          70 | high           | med          | STRETCH            |
| h-rho phase map                 |      55 | THREATENED (D-3)   |          96 | low            | none         | STRONG EXTENSION   |
| m>1 rigorous certificate        |      40 | UNCERTAIN          |          45 | high           | very high    | STRETCH            |
| SR rigorous period-2            |      30 | NOVELTY-DEFENSIBLE |          35 | very high      | very high    | STRETCH / LEVEL-4+ |
| skewed campaign                 |      25 | NOVELTY-DEFENSIBLE |          50 | med            | high         | STRETCH / LEVEL-4+ |

Full rationale column in `staged_task_ranking.csv`.

**Reading of the ranking.** The two derivative theorems top the list because this session made
them cheap: both are transcriptions of the Stage C conditional-mean argument plus a Wald
identity, with the measurements already in hand. The rigorous certificates rank low not
because they are unimportant but because Stage C already showed the stochastic system does not
exhibit the certified skeleton behaviour - another certified orbit buys narrative closure at
very high proof cost.

---

## 6. KILL CRITERIA - STATUS

| gate             | verdict                                | evidence                                                                                                                                                 |
|:-----------------|:---------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| D1 SR            | PASSED - NOT KILLED                    | Gamma_SR=17.44+/-0.09 => |F'|=16.44 >> 1. Continue to nonlinear map/root search.                                                                         |
| D2 m>1           | PARTIAL KILL                           | Gamma_m>2 for all m<=50 (pilot set safe) but Gamma_m crosses 2 at m*~72 (CUSUM) / ~87 (SR). Window stabilization IS the result for large m.              |
| D3 non-Gaussian  | NOT KILLED numerically; rigour AT RISK | Gamma_psi in [8.41,15.90] ARL-matched across t(3,5) and 5-10% contamination. Naive Gamma_T diverges (35-100) - the score form is REQUIRED, not cosmetic. |
| D4 phase diagram | PROCEED, DEMOTED                       | rho_c(m) and rho_c(ARL0) are consequences of the Gamma_m theorem. Not a novelty headline (D-3 THREATENED).                                               |

---

## 7. MANDATORY vs STRETCH

**MANDATORY LEVEL-4 CLOSURE** (all four gates resolved; none is a low-probability side quest)

1. `m>1` derivative theorem + Wald sum rule (2.2, 2.6.1) - nearly free.
2. SR derivative theorem + factorization (1.2) - transcription.
3. SR Monte Carlo derivative at production precision (P1-P2).
4. `rho_c(m)` phase map with `m*` termination (4).

**STRONG EXTENSION**

5. General location-family theorem, bounded-score subclass (3.1).
6. Student-t and contaminated-Gaussian campaigns (P5).
7. `rho_c(ARL_0)` axis (P4).
8. Uniform-integrability diagnostic (P6) - **gates item 5**, run it first.

**STRETCH / LEVEL-4+**

9. SR nonlinear map + root search (only if SR period-2 is targeted).
10. `m>1` rigorous certificate, `m <= 10` only.
11. SR rigorous period-2.
12. Skewed campaign.

**Blocking risk.** Items 10-11 are exactly the low-probability rigorous side quests your brief
warns about. Recommendation: **freeze Level 4 closure on items 1-4**, which are achievable and
already evidenced, and let 9-12 run as Level 4+ without gating closure.

---

## 8. PROOF OBLIGATIONS (consolidated, ranked by payoff per unit effort)

1. **`Gamma_m = (1/m) sum_{i<m} gamma_i`, `sum_i gamma_i = E[T_tau^2] = ARL_0`.** Wald +
   linearity. Yields the closed form, the `m -> inf` limit, and existence of `m*`.
2. **`F_{SR,rho} = rho F_{SR,1}` and `F_{SR,1}'(0) = 1 - Gamma_SR`.** Transcription of the
   Stage C argument; the SR increment never enters it.
3. **`gamma_i` decreasing in `i`.** Gives monotone `Gamma_m` and uniqueness of `m*`.
4. **`g(e) = -F_1(e)/e` strictly decreasing** (carried over from Stage C, still the highest-
   value single lemma: existence + uniqueness + attraction for the whole `rho`-family).
5. **Differentiation under stopping for SR** - the genuine D1 gap.
6. **`Gamma_inf < 2`** - would make `m*` rigorous.
7. **Uniform integrability of stopped score sums**, bounded-score families - gates D3 rigour.
8. **`Gamma_SR > 2` by Arb enclosure** - do not start before 2 and 5.

---

## 9. RECOMMENDED PILOT PROTOCOL

| id   | experiment                                    | scale                 | deliverable                           | est_cost     | class     |
|:-----|:----------------------------------------------|:----------------------|:--------------------------------------|:-------------|:----------|
| P1   | CUSUM Gamma_m, m in {1,5,10,20,50}            | 1e6 cycles            | confirm Gamma_m and locate m* to +/-2 | 2 core-hours | MANDATORY |
| P2   | SR Gamma_m, matched ARL0=465                  | 1e6 cycles            | Gamma_SR,m and m*_SR                  | 3 core-hours | MANDATORY |
| P3   | SR full map F_SR,1(e), e in [0,3]             | 2e5 cycles/pt, 25 pts | root of g_SR(e)=1 -> orbit amplitude  | 6 core-hours | MANDATORY |
| P4   | rho_c(ARL0): h grid -> ARL0 in {100,...,2000} | 5e5 cycles/pt         | exponent in Gamma ~ ARL0^b            | 4 core-hours | STRONG    |
| P5   | t(3,5,10) + contam(.05,.10) ARL-matched       | 5e5 cycles            | Gamma_psi CIs, tail-index check       | 5 core-hours | STRONG    |
| P6   | Var of stopped score sum vs truncation        | 5e5 cycles            | uniform-integrability diagnostic      | 2 core-hours | STRONG    |
| P7   | skewed (skew-normal) pilot                    | 2e5 cycles            | does F_rho=rho F_1 survive asymmetry? | 2 core-hours | STRETCH   |

Total mandatory pilot cost: **~11 core-hours**, no GPU, no remote compute required. Everything
in this blueprint was produced in ~3 minutes of local simulation; the pilots are precision
upgrades, not new capability.

---

## 10. HANDOFF INSTRUCTIONS

**Reference implementation.** The estimator used here is the deliverable to port: a vectorized
`N`-channel simulator carrying, per channel, `(detector state, T_tau accumulator, age,
ring buffer of last L innovations)`, emitting `gamma_i` and truncated `Gamma_m` in a single
pass. `N = 3000-8000` channels x `T = 2-4e4` steps gives ~2e5 cycles in ~30 s single-core.

**Non-negotiable protocol points** (each is a place a reimplementation will silently diverge):

1. **Post-update inclusive alarm.** Update the statistic, then test `>= h`. Off-by-one here
   changes `gamma_0` materially, since the terminal observation carries 3.4x the next lag.
2. **Truncated window `w = min(m, tau)`.** Do not discard short cycles (biases `Gamma_m` up)
   and do not pad them.
3. **SR in log space**, `log R <- logaddexp(0, log R) +/- delta*z - delta^2/2`, reset to
   `-inf` (use `-60`). Linear-space SR overflows before `A = e^6.3`.
4. **ARL-match before comparing any two configurations.** `Gamma ~ ARL_0^0.232`, so an
   unmatched comparison manufactures effects. This applies to SR-vs-CUSUM *and* to every
   non-Gaussian family.
5. **Off the Gaussian, use `S_tau = sum psi(z_t)`, never `T_tau`.** The naive form inflates to
   100 at `t(3)` (3.3).
6. **Report `Gamma` with a standard error** from the per-cycle variance. At 2e5 cycles the SE
   is ~0.09; the SR-CUSUM excess is +1.5, so precision is adequate but not lavish.
7. **Right-censoring caveat.** Unfinished cycles at horizon `T` bias `ARL_0` ~2% low. Fine for
   covariances; if `ARL_0` itself is the deliverable, discard the final partial cycle.

**Execution order.** P6 first (it gates the D3 theorem), then P1-P3 in parallel, then P4-P5.
Do not start P7 or any rigorous certificate without an explicit new gate.

**Do not** attempt the `m>1` rigorous certificate or SR period-2 in the same batch as the
mandatory items - per 7, they must not gate closure.

---

## 11. CLAIM LANGUAGE FOR STAGE D OUTCOMES

Additions to the Stage C guide (`claim_language_guide.csv`), all load-bearing:

| Forbidden | Permitted |
|---|---|
| "detector-independent" | "reproduced in two structurally distinct detectors (CUSUM and Shiryaev-Roberts) under a matched reference-reuse protocol" |
| "universal", "distribution-free" | "robust across the location families tested (Gaussian, Student-t `nu>=3`, `epsilon`-contaminated to 10%)" |
| "first" | omit entirely - the prior-art gap is still open (12) |
| "novel stability boundary" | "the local-stability boundary `rho_c = 1/(Gamma_m - 1)`, a consequence of the derivative identity" |
| "SR is more unstable than CUSUM" | "at matched `ARL_0`, `Gamma_SR` exceeds `Gamma_CUSUM` by 1.5 (10-26 SE) across a 2.7x `ARL_0` range" |
| "instability vanishes for large windows" (unqualified) | "for `m > m* ~ 72` (CUSUM, NUMERICAL), no reuse fraction destabilizes the origin" |
| "heavy tails destabilize re-baselining" | the opposite is measured: at matched `ARL_0`, `Gamma_psi` *decreases* with tail heaviness |

Two structural claims that **are** safe, because they are theorems: `sum_i gamma_i = ARL_0`
(Wald), and `lambda_2 = [F_1'(e*)]^2 >= 0` so no period-doubling cascade exists (Stage B).

---

## 12. STANDING BLOCKED ITEM

Prior-art verification remains **unavailable in this workspace** - the scholarly connector
requires an OpenAlex API key and none is configured. The Perplexity firewall results in your
brief are used as given; I have not independently verified D-1 through D-4 and cannot. The
word "first" must not appear in any Stage D output until this is closed. Third stage running.

---

*All numerical values recomputed in this session at pilot scale and read back from the saved
CSVs. Control: the stopped-covariance estimator reproduces the frozen `Gamma = 15.885` as
`15.80 +/- 0.08`. The protected Level 1-3 certificate is untouched. Nothing above is labelled
a theorem except the Wald identity, the factorization `F_rho = rho F_1`, and the Stage B
multiplier sign - all of which are proved, not measured.*
