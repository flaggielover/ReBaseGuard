# P6 novelty audit

```text
NOVELTY_VERDICT          = PARTIAL / NOT_INDEPENDENTLY_ADJUDICATED
ALGORITHMIC_NOVELTY      = OVERLAPPING  (the weight-adaptation SHAPE has close prior art)
THEORETICAL_NOVELTY      = PLAUSIBLE, NOT ESTABLISHED  (T6-B, T6-C; see section 5)
OPERATIONAL_NOVELTY      = CLAIMED, measured, reproduced -- but in a synthetic frozen model
INTEGRATION_NOVELTY      = CLAIMED (the honest floor)
EXECUTED                 = after Stage 2 screening, BEFORE any Stage 4 confirmation
                           number was read (PREREGISTRATION_OPTIONS.md C9)
TOOL                     = web literature search, September 2026
```

This audit was run before the confirmation results were looked at, exactly so
that its verdict could not be influenced by how good the numbers turned out to
be (`NOVELTY_AUDIT_PLAN.md` section 5). Its most important finding is **negative
for P6's algorithmic novelty**, and it is recorded first.

---

## 1. The headline finding

**The shape of SAW's rule -- adapt a weight to the magnitude of an observed
statistic -- is standard, and the closest prior art is the adaptive-EWMA
literature.** Capizzi & Masarotto's AEWMA (Technometrics 45(3), 2003) makes the
smoothing constant `lambda` a function of the magnitude of the current
prediction error via a Huber or bisquare score, and a very large derivative
literature has followed. Anyone reading "SAW makes the reuse weight a decreasing
function of `|zbar|`" and stopping there is entitled to say P6 has renamed an
AEWMA. **P6 says so explicitly rather than letting a referee say it**, as
`METHOD_NOVELTY_SEPARATION.md` section 3 requires.

What survives that concession is stated in section 4.

## 2. Classes searched, closest prior art, verdicts

Seven comparison dimensions, from `NOVELTY_AUDIT_PLAN.md` section 2:
(1) object controlled, (2) trigger, (3) information used, (4) **the recursion**,
(5) objective, (6) guarantee type, (7) cost accounting.

| # | class | closest prior art found | verdict | the specific difference (dimension) |
|---|---|---|---|---|
| L1 | self-starting / adaptive CUSUM | Hawkins' self-starting CUSUM; self-starting Max-CUSUM on recursive residuals; adaptive self-starting distribution-free CUSUM on sequential ranks | **DISTINCT** | (2) self-starting charts update the estimate at *every* observation from start-up and never reset a cycle; P6 acts only at alarms, with a frozen detector that resets. (4) no stopping-time-selected window enters a self-starting estimate |
| L2 | adaptive reference / parameter updating | **Huberts, Schoonhoven & Does (2019)**, "The effect of continuously updating control chart limits on control chart performance", QREI 35(4):1117-1128 | **OVERLAPPING** | This is the nearest study of P6's *phenomenon*. It measures what continuous updating does to conditional chart performance and warns that out-of-control data may enter the update. (1)/(4): it updates from a growing in-control record, not from the `min(m, tau)` window that *caused* the alarm, and it does not have P6's recursion in which the update's own error selects the next window |
| L3 | EWMA reference adaptation / adaptive centring | **Capizzi & Masarotto (2003)** AEWMA; the large AEWMA derivative literature (score-function, VSS-EWMA, parameter-free AEWMA) | **OVERLAPPING -- the highest-risk class** | (1) AEWMA adapts the *monitoring statistic's* smoothing constant; SAW adapts the *reference reconstruction weight* while the statistic is frozen and reset. (2) AEWMA adapts every observation; SAW only at alarms. (6) AEWMA's `lambda(e)` is a score function chosen for shift-detection performance across a shift range; SAW's `rho` is the exact minimiser of a conditional second moment, with a closed form. **A fixed-`rho` reuse rule really is an EWMA on the reference, and P6 states this in `METHOD.md` rather than leaving it to be discovered** |
| L4 | post-alarm reset / restart / recalibration | repeated-CUSUM restart formulations (Tartakovsky-Nikiforov-Basseville lineage); operational "reset the baseline" features in monitoring products (e.g. Dynatrace baseline reset) | **DISTINCT on mechanism, OVERLAPPING on framing** | the restart literature restarts the *statistic*; it does not model reuse of the pre-alarm window as the new reference, and the operational products offer a reset switch with no analysis |
| L5 | repeated / sequential change detection | Lorden, Pollak, Moustakides; "Quickest change-point detection: a bird's eye view"; multi-stream QCD | **DISTINCT** | (5) the objective is delay under a known or estimated post-change law with a *fixed* reference; the reference-contamination channel is absent |
| L6 | selective data reuse after a stopping time | no direct match found | **NO DIRECT PRIOR ART FOUND** | this is query 6 of the plan, and it returned nothing that reuses a stopping-time-selected window as an estimator and then iterates |
| L7 | post-selection / selective inference after stopping | post-detection inference for sequential changepoint localization (arXiv 2502.06096); optional-stopping bias literature; "there is limited literature on valid estimation or inference for pre- and post-change parameters post-stopping" | **DISTINCT, and this is a real gap in the literature** | the selective-inference work *corrects* an estimate for the selection event; P6 *weights* the contaminated estimate against a clean one to minimise a forward risk, and then iterates the whole thing. Nothing found closes the loop |
| L8 | adaptive sampling / design | adaptive sample allocation in sequential detection | **DISTINCT** | (7) none of it charges for the fresh sample the way `H5` does |
| L9 | VSS / VSI charts | VSS-EWMA, VSSI, risk-based VSI charts; the whole adaptive-sampling-scheme literature | **OVERLAPPING on shape, DISTINCT on object** | VSS adapts the *next sample size* from the current statistic — structurally the nearest analogue to adaptive `m_j`/`k_j`. But (1) it adapts the monitoring sample, not the reference reconstruction, and (5) its objective is ARL over shifts, not reference distortion |
| L10 | robust sequential detection | minimax robust QCD with Wasserstein ambiguity sets; robust AEWMA under contamination | **DISTINCT** | robustness there is to *distributional* contamination; P6's Gaussian core has none, and the pathology is pure selection (`X5` puts contamination in P8) |
| L11 | feedback control of monitoring rules | adaptive threshold computation for CUSUM-type procedures; weighted recursive PCA that re-estimates when the false-alarm rate rises | **OVERLAPPING on framing** | (1) these adapt thresholds or the detection model; P6 freezes both by construction (`I1`) |
| L12 | estimation-effect literature | **Jensen, Jones-Farmer, Champ & Woodall (2006)**, JQT 38:349-364; Phase-I contamination literature; **Capizzi & Masarotto (2020)** "Guaranteed in-control control chart performance with cautious parameter learning", JQT 52(4):385-403 | **OVERLAPPING -- the most important comparison** | See section 3 |
| L13 | inverse-variance / precision weighting; Kalman reference tracking | inverse-variance weighting is textbook (sensor fusion, meta-analysis); shrinkage/variance-adaptive estimation | **DUPLICATE at the level of the formula** | `rho* = (1/k)/(V + 1/k)` **is** inverse-variance weighting and P6 presents it as such. What is not textbook is *what `V` is* here -- the conditional second moment of a stopping-time-selected window mean -- and that it is estimated from observables at 95% `R^2` |
| L14 | bandit / RL formulations of monitoring | online MDPs under bandit feedback; restless bandits; and, in the ML-monitoring literature, **"Self-Poisoning in Adaptive Out-of-Distribution Detection" (arXiv 2607.21673)** | **DISTINCT on method, OVERLAPPING on phenomenon** | the self-poisoning work is the closest *conceptual* analogue found anywhere: a detector that recursively updates from its own accepted data develops a feedback pathology with a sharp threshold, and its fix is a "certified admission gate reading only a frozen reserve". In ReBaseGuard the corresponding fix -- fresh-only -- is **itself unsafe** (`S4`: it loses 65%-83% of nominal ARL), which is exactly why P6 is a weighting problem and not a gating problem |

## 3. The nearest neighbour, in detail: cautious parameter learning

**Capizzi & Masarotto (2020)** is the closest thing in the control-chart
literature to "safe re-baselining". Its mechanism is a **delay**: postpone
updating `mu_0` and `sigma^2` until the probability that out-of-control
observations have entered the estimate is negligible, and design the control
limits by stochastic approximation so that in-control performance is guaranteed.

The differences are structural, not cosmetic:

| dimension | cautious parameter learning | SAW |
|---|---|---|
| what the update is protected from | **contamination by genuinely out-of-control observations** | **stopping-time selection in an entirely in-control process.** P6's pathology needs no change at all: `Delta = 0` everywhere, and the reference still degrades, because the window that entered the estimate is the one that crossed the threshold |
| mechanism | an **inclusion rule** -- delay/exclude suspicious data | a **weight** -- keep the data, downweight it by an estimate of its selection-induced second moment |
| what is guaranteed | in-control performance, by design of the limits | nothing is guaranteed; a one-step conditional dominance is proved and everything else is measured |
| the recursion | the estimate converges as the clean record grows | the reference never converges: each cycle's window is re-selected by the error the previous cycle installed |

P6 carries `B11_conf_gate` (reuse only when `|zbar|` is small, else refresh) as a
baseline precisely because it is the cautious-learning *shape*, so the
comparison is measured rather than argued.

## 4. What is actually left, separated by kind

`METHOD_NOVELTY_SEPARATION.md` section 1's four kinds:

| kind | claim | strength |
|---|---|---|
| **algorithmic** | **NOT CLAIMED.** Weight-as-a-function-of-observed-magnitude is AEWMA-shaped (L3); the formula is inverse-variance weighting (L13); gating on a statistic is cautious learning (L12) | none |
| **theoretical** | **CLAIMED, unadjudicated.** (a) T6-C's identity that the entire advantage of an adaptive reuse weight over the best fixed one is the **Jensen gap of `Q*(V) = nu V/(V+nu)` against the dispersion of the selection intensity**, with the exact plug-in criterion `E[(V+nu)(rho_hat - rho*)^2] < Gap`; (b) T6-B's closed-loop Doeblin argument for a *policy-dependent* kernel, whose new content is that the raw-mean identity makes the minorising event's decision independent of the state. No prior art for either was found, but absence of a search hit is weak evidence | plausible; needs adjudication |
| **operational** | **CLAIMED.** A measured, cost-matched, two-detector, multi-`m`, independent-seed improvement over the *best fixed reuse weight* -- not over full reuse | real, but inside one frozen synthetic model |
| **integration** | **CLAIMED (the honest floor).** The problem formulation with an explicit fresh-sample cost model; the observability audit with its two positive results and one negative; the oracle ceiling; and the finding that the incumbent method is the zero-information member of the proposed family | modest and honest |

Two further items that the audit found **no** prior art for, and which are
P6-owned rather than SAW-owned:

* **The selection effect is also a sensor.** `E[zbar | e] = R(e) - e`, so the
  observable window mean reads the latent reference error with gain
  `-GammaTilde in [-17.3, -11.8]` near the origin: the mechanism that causes the
  damage is a 12x-17x amplifier for measuring it. Measured here at `R^2 = 0.95`.
* **Increment observability.** `e_{j+1} - e_j = mu_{j+1} - mu_j` exactly, so the
  filtering problem is one-dimensional in the single unknown `e_0` — together
  with the finding that this channel *leaks* whenever `e_0` is known
  (`OBSERVABILITY_AUDIT.md` section 4a). SAW does not use this channel, so it is
  reported as an audit result, not as part of the method.

## 5. Honest limits of this audit

* It is a **web literature search**, not a systematic review with database
  coverage, and it was run in one sitting. Negative findings (L6, L7, and the
  two theoretical claims) are **weak evidence of absence**.
* The control-chart literature is large, old and partly paywalled; several of
  the closest items were read from abstracts and secondary summaries rather than
  from the full papers.
* No independent adjudication of this audit has happened. Per
  `NOVELTY_AUDIT_PLAN.md` section 4 step 5 that is required, and it is listed in
  `CODEX_HANDOFF.md` as an attack target.
* Consequently the repository status line stays at
  `NOVELTY = PARTIAL / NOT_INDEPENDENTLY_ADJUDICATED`, and no P6 document claims
  a novel algorithm.

## 6. Queries executed

```text
1  data reuse after stopping time bias sequential change detection reference update control chart
2  self-starting CUSUM control chart estimated parameters recursive reference update ARL degradation
3  adaptive reuse weight inverse variance shrinkage baseline update after alarm SPC selection bias
4  conditional distribution last m observations before stopping time CUSUM overshoot selected window mean
5  variable sample size control chart adaptive sample size VSS VSI post-alarm recalibration policy
6  post-alarm restart rule repeated change detection re-baselining reference data contaminated by alarm
7  selective inference conditional on stopping event estimation of change magnitude after CUSUM alarm
8  EWMA adaptive centerline reference update control chart equivalence exponential smoothing baseline drift
9  Capizzi Masarotto adaptive EWMA score function smoothing constant magnitude of error
10 "inverse variance" weighting combine reused historical estimate with fresh sample sequential monitoring
11 effect of parameter estimation control chart Phase I recursive contamination Jensen Jones-Farmer review
12 Huberts effect of continuously updating control chart limits on chart performance 2019
13 "cautious parameter learning" control chart guaranteed in-control performance Capizzi Masarotto
14 stopping time selection bias inflates variance of terminal window sample mean sequential detection
15 bandit stochastic approximation adaptive control of monitoring reset policy MDP quality control restart
16 detection delay tail quantile worst case delay control chart conditional performance right tail run length
17 recursive baseline update anomaly detection feedback loop self-poisoning reference drift monitoring
```

Queries 6, 7 and 14 are the plan's three aimed at P6's actual mechanism. **None
returned a match**, which is the basis for the `NO DIRECT PRIOR ART FOUND`
verdict on L6 and the "real gap" note on L7 — and, per section 5, is weak
evidence.
