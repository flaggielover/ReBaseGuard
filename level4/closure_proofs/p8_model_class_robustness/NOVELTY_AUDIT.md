# P8 novelty audit

`X10` of the P6 pre-design records that **novelty is not adjudicated anywhere in
ReBaseGuard**. P4's own audit is open, P5's and P6's are
`NOVELTY-NOT-ADJUDICATED` / `NOT_INDEPENDENTLY_ADJUDICATED`. P8 inherits that
posture: nothing here is claimed novel, and the labels below are deliberately
conservative.

**Method.** One sitting of web literature search (September 2026), reading
titles, abstracts and, where reachable, method sections. This is **not** a
systematic review; several of the closest items were read from abstracts only.
Its negative findings are weak evidence of absence, exactly as
`p6/LIMITATIONS.md` `V2` says of P6's audit. It has **not** been independently
adjudicated.

---

## 1. What P8 might be claiming

| # | candidate | kind |
|---|---|---|
| `C1` | the *phenomenon*: reusing alarm-selected observations to rebuild a monitoring reference creates a recursive feedback whose local multiplier is a stopped-score covariance | phenomenon |
| `C2` | `P8-T1`: the convention-A stopped-selection gain identity for a general regular location family and every window `m` | theorem |
| `C3` | `P8-T2`: the reset decomposition `E[tau_j] = E[A_f(e_j)]` for a general innovation family | theorem |
| `C4` | ~~`H1` / `G4`: the window scaling of the critical reuse fraction as a quantity invariant across detector and innovation family~~ **`H1` was measured and REJECTED** (gate `G4` FAIL, spread `22.7%`–`49.3%` against a `10%` margin). There is no law to claim novelty for. What remains is `C4'` | — |
| `C4'` | the measured `K` surface itself, and its decomposition into a near-invariant detector axis (residual `<= 3.63%`) and a strongly varying distribution axis (`22%`–`49%`) | empirical finding, not a law |
| `C8` | the reconciliation of P4's `Gamma_f` with Stage-D's `Gamma_psi` as two different estimands, and the magnitude of the wrong-score error (up to `11.7x`) | experimental synthesis / diagnosis |
| `C5` | the detector x distribution x window x convention x drift robustness matrix itself | experimental synthesis |
| `C6` | the moment-boundary diagnosis of the `t3` estimator | statistical diagnosis |
| `C7` | any algorithm | — (P8 contains none) |

## 2. Closest prior art found

| # | line of work | representative work | relation to P8 |
|---|---|---|---|
| `L1` | **effect of parameter estimation on control-chart performance** | Jensen, Jones-Farmer, Champ & Woodall, *Effects of parameter estimation on control chart properties: a literature review* (2006); Saleh et al. on conditional performance | **Closest neighbour to `C1`.** It studies a chart whose limits use a *fixed Phase-I estimate*, and shows the conditional in-control ARL is highly variable. It does **not** study a reference rebuilt repeatedly from observations selected by the alarm, has no recursion, and derives no multiplier |
| `L2` | **self-starting charts with sequentially updated estimates** | Hawkins, *Self-starting CUSUM charts for location and scale* (1987); Keefe, Woodall & Jones-Farmer (2015) on its in-control behaviour; predictive-ratio CUSUM (2023) | **Closest neighbour to the recursion in `C1`.** Estimates *are* updated every observation and the dependence between the standardised values is recognised. But the update uses **all** past observations, not an alarm-selected terminal window, and the chart is **not** restarted at an alarm; there is no stopping-time selection, so no stopped-score object and no reuse fraction to be critical in |
| `L3` | **run-length behaviour of CUSUM / SR with estimated parameters** | Hawkins & Olwell; Capizzi & Masarotto; "CUSUM ARL — conditional or unconditional?" (2019) | quantifies the same *damage*; the mechanism studied is estimation error, not selection through a stopping event |
| `L4` | **robustness of CUSUM / SR to non-Gaussian and contaminated data at matched ARL** | numerous; e.g. numerical CUSUM-vs-SR comparisons (Polunchenko & Tartakovsky), heavy-tail and contamination robustness studies | **Directly overlaps `C5`'s axes** for a *single-cycle, fixed-reference* chart. What is not in that literature is the same matrix for a **recursively re-baselined** chart, which is what P8 measures |
| `L5` | **change detection under model misspecification / robust QCD** | minimax robust QCD with ambiguity sets; robust AEWMA under contamination; score-based drift charts | robustness *of the detector design* to distributional uncertainty. P8 keeps the detector frozen at its Gaussian design (`THEORY.md` §0) and asks a different question |
| `L6` | **stopped-score / change-of-measure differentiation of stopping functionals** | classical: Wald identities, likelihood-ratio differentiation, score functions of stopped experiments; Rubinstein/Glynn score-function IPA | `C2`'s *machinery* is textbook. What is not textbook is its application to this estimand; and P4 already owns the `m = 1` case inside ReBaseGuard, so `C2` is at best an incremental extension of a `PARTIAL` in-repository result |
| `L7` | **sample-mean estimators with divergent third moments** | classical: Berry-Esseen conditions, stable-law limits, infinite-variance variance estimates | `C6` is a textbook diagnosis applied to a specific artifact. Nothing novel |
| `L8` | **separability / factorisation laws in run-length or influence profiles** | searched for; nothing found linking a *window-length scaling of a stability boundary* to detector- and distribution-invariance | no prior art located for `C4`. **This is a negative search result, not a demonstration of absence** |

## 3. Conservative labels

| candidate | novelty of phenomenon | novelty of theorem | novelty of experimental synthesis | novelty of algorithm | novelty of application |
|---|---|---|---|---|---|
| `C1` phenomenon | `NOT_ESTABLISHED` — owned by P1–P3, not by P8, and `L1`/`L2` are close enough that P8 makes no claim | `NOT_APPLICABLE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` |
| `C2` `P8-T1` | `NOT_APPLICABLE` | `NOT_ESTABLISHED` — an application of P4's `PARTIAL` abstract theorem to a different stopped functional; the machinery is standard (`L6`) | `NOT_APPLICABLE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` |
| `C3` `P8-T2` | `NOT_APPLICABLE` | `NOT_ESTABLISHED` — a one-line generalisation of P7's `THEOREM P7-A` | `NOT_APPLICABLE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` |
| `C4` `H1` window law | `NOT_APPLICABLE` — **the hypothesis was rejected.** A falsified hypothesis is not a novel result | `NOT_APPLICABLE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` |
| `C4'` measured `K` surface | `NOT_ESTABLISHED` — a measurement of a known object (`rho_c`) on a wider model class; the cross-detector near-invariance is a `3.63%`-residual observation on two closely related detectors, not a phenomenon | `NOT_APPLICABLE` | `PLAUSIBLE_BUT_NOT_ADJUDICATED` — no prior art located for a window-scaling decomposition of a re-baselining stability boundary, on a non-systematic search | `NOT_APPLICABLE` | `NOT_APPLICABLE` |
| `C8` estimand reconciliation | `NOT_APPLICABLE` | `NOT_APPLICABLE` | `NOT_ESTABLISHED` — it is a definitional clarification internal to this repository, not a contribution to any literature | `NOT_APPLICABLE` | `NOT_APPLICABLE` |
| `C5` the matrix | `NOT_APPLICABLE` | `NOT_APPLICABLE` | `PLAUSIBLE_BUT_NOT_ADJUDICATED` — the axes are individually standard (`L4`), their combination for a *recursively re-baselined* chart was not located | `NOT_APPLICABLE` | `NOT_ESTABLISHED` |
| `C6` `t3` diagnosis | `NOT_ESTABLISHED` — textbook (`L7`) | `NOT_APPLICABLE` | `NOT_ESTABLISHED` | `NOT_APPLICABLE` | `NOT_APPLICABLE` |
| `C7` algorithm | `NOT_APPLICABLE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` | `NOT_APPLICABLE` — **P8 contains no algorithm.** A matrix, a plot and a law are not an algorithm | `NOT_APPLICABLE` |

**Overall P8 novelty status: `NOVELTY = NOT_INDEPENDENTLY_ADJUDICATED`.**

After the results are in, the position is *weaker* than it looked before them.
The item that was the campaign's best novelty candidate — the window-separability
law `H1` — was **measured and rejected**, so it is not a candidate at all. The
only items still carrying `PLAUSIBLE_BUT_NOT_ADJUDICATED` are the experimental
syntheses `C4'` and `C5`, and both are combinations of individually standard
axes. **P8 claims no novel phenomenon, no novel theorem, and no novel
algorithm.**

## 4. What would move a label

* `C4` cannot move: the hypothesis is falsified.
* `C4'`/`C5` → `ESTABLISHED` would need (i) a systematic review of the SPC and
  sequential-analysis literature on run-length influence profiles, (ii) the
  finding to survive detector families outside `{CUSUM, SR}` and model classes
  outside the location family, and (iii) independent adjudication. P8 supplies
  none of the three.
* Any `NOT_ESTABLISHED` above would move only on evidence that the prior art
  named in §2 does **not** in fact cover the item. P8 did not find such
  evidence and did not look for it exhaustively.

## 5. Honest statement of the search's weakness

Three named weaknesses, following `p6/LIMITATIONS.md` `V2`–`V3`:

1. one sitting, general web search, no database-systematic protocol, no
   citation chasing;
2. several closest items read from abstract only, so a method-section detail
   could overturn a "distinct" judgement;
3. no independent adjudication, which is a stated requirement everywhere else in
   this repository for a novelty claim.
