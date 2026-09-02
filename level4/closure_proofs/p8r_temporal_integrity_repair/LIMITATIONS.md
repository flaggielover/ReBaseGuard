# P8R limitations

Written to be read by someone trying to break the campaign. Nothing inherited
from P3, P4, P5, P6, P7 or P8 is softened here.

**The most important limitation is at the top: a repaired procedure does not
make the science broader.** P8R re-establishes that the model-class robustness
question was asked under a leakage-free, pre-anchored protocol. It does not
widen the model class, does not discharge any analytic hypothesis, and does not
turn any `EMPIRICAL` result into a certified one.

---

## 1. Scope limitations that no P8R result escapes

| # | limitation | consequence |
|---|---|---|
| `L1` | P8R widens the model class along four named axes and no others: six innovation families, two detector families, six windows, two window conventions, two drift patterns. Everything else is unchanged — iid innovations, a location shift, full detector reset at every alarm, a single frozen ARL match, no autocorrelation, no scale change, no multivariate structure, **no real data**. | "outside the frozen Gaussian specialisation" is not "outside simulation". No P8R number is evidence about a real process. |
| `L2` | The six families are a designed set, not a sample of anything. They are Stage-D's six, chosen there for regularity and tractability, and they are all **symmetric and unimodal**. | P8R says nothing about skewed, discrete, bounded or multimodal innovations. A skewed family is the most obvious untested case, and it is untested because no frozen ReBaseGuard artifact defines one. |
| `L3` | The two detector families are the only two the repository closes, and they are close relatives — both likelihood-ratio-based two-chart schemes with the same Gaussian design. | Agreement between them is weaker evidence of generality than two arbitrary detectors would be; disagreement between them is correspondingly stronger evidence of non-transfer. |
| `L4` | The detector statistic is frozen at its Gaussian design in every family; only the threshold is recalibrated. | P8R measures the robustness of *a Gaussian-designed chart run on non-Gaussian data*, not the robustness of the phenomenon to a family-optimal chart. A score-based chart for `t3` is a different detector and is untested. |
| `L5` | The contaminated families do not have unit variance (`1.4` and `1.8`), by Stage-D's frozen construction, so `k = 1/2` is not "half a standard deviation" there. | Cross-family comparisons at fixed `k` mix a shape effect with a scale effect. The ARL match removes the first-order consequence, not the confound. |
| `L6` | No stationarity theorem exists outside the Gaussian core (P5's `T7` is Gaussian-scoped). | Every non-Gaussian chain quantity here is a finite-horizon average after a declared burn-in. None is a stationary quantity, and P8R claims no ergodicity, no uniqueness of an invariant law and no convergence. |
| `L7` | The chain and drift experiments use `m in {1,5}` only, and the drift experiment observes four post-change cycles. | The `Gamma` grid and the drift grid are **not** fully crossed, and the ramp conclusion is confined to the first post-change cycle. Four cycles do not establish long-run ramp accumulation. |

## 2. Theory limitations

| # | limitation |
|---|---|
| `T1` | **`P8R-T1` is a `CONDITIONAL_THEOREM` and stays one.** It inherits P4's differentiation-under-expectation, score-integrability and stopping-time-integrability hypotheses, which are *assumed*, not verified, per family. Simulation agreement is not a discharge of an analytic hypothesis. The case is most acute for heavy-tailed `t3`. |
| `T2` | `H1` (window separability) has no proof and no surviving proof sketch. Reducing it to invariance of the normalised lag profile is a restatement, not an explanation. Why stopping-time selection should distribute over recent lags in a detector- and distribution-free way remains unexplained — and P8R's `S7` result does not explain it either. |
| `T3` | The exact algebraic identities (`P8R-L0`, `P8R-L1`, the reset decomposition, the convention-A/B truncation decomposition) are exact **under their stated iid/reset model** and are separate claims from `P8R-T1`. They must not be cited as evidence for the conditional theorem's hypotheses. |
| `T4` | No enclosure layer, no interval arithmetic, no formal proof. Every P8R number is `EMPIRICAL` in P3's evidence hierarchy. **P8R creates no certified numerical result**, exactly as P8 created none. |
| `T5` | Nothing here infers an operational consequence from `Gamma` or `rho_c`. The relationship between them is measured and reported as an association, never as a mechanism. |

## 3. Statistical limitations

| # | limitation |
|---|---|
| `S1` | `t3` is on the third-moment boundary for the `Gamma` integrand: the CLT applies but no Berry–Esseen rate does, and the sample variance itself has infinite variance. **`t3`'s reported standard error is not trustworthy.** Declared before production; `t3` is excluded from `S6`'s count in both directions and reported separately everywhere. |
| `S2` | `t5` is on the fourth-moment boundary for the variance of its variance. Its SE is finite and usable but converges slowly; treat its interval as indicative. |
| `S3` | The window law is tested on `m in {1,2,3,5}` with `{10,20}` as declared extrapolation. Whether `K(m)` behaves the same for larger `m`, or changes form as `m` approaches the ARL, is untested — and the `t3`/`m=20` cell of interest lies **inside** that untested region. |
| `S4` | At millions of cycles per cell, a 1% heterogeneity is highly significant. Every invariance question is a practical-equivalence question with a pre-declared margin, and the formal homogeneity statistic (Cochran's `Q`) is `DESCRIPTIVE_ONLY`. A reader who reads `p`-values as the result will draw the wrong conclusion. |
| `S5` | Multiplicity protection is reproduction — across detectors, windows, an independent seed family and an independent reimplementation — not an adjustment. The one BH companion is `DESCRIPTIVE_ONLY` and changes no resolution. |
| `S6` | P7's boundary criterion is a bare `max` over brackets **with no uncertainty margin**, and P8R applies it at half P7's resolving power (4 sub-families per family, not 8). It can flip on Monte Carlo noise. `S10` reports the literal result; the uncertainty companion is reported beside it and never inside it. |
| `S7` | The drift study is under-powered in the tail at large `Delta`. Cells with fewer than 200 tail events are labelled `INSUFFICIENT_TAIL_EVENTS`, and the label is not decoration. |
| `S8` | CRN pairing is across detector, window, convention and `rho` — **not** across families. Family comparisons are unpaired and carry the full independent variance. |
| `S9` | The SR calibration is P8R's own. Its residual ARL error propagates into every SR non-Gaussian number, and a residual of a few tenths of a percent is not nothing when `Gamma` differences of a few percent are being compared. |
| `S10` | `S15`'s three-way rule is deliberately conservative and is also **under-powered by construction**: the independent reimplementation runs far fewer cycles per cell than production, so its interval is the widest of the three and will usually be the binding one. `S15 = INCONCLUSIVE` therefore means "not established", never "refuted". |
| `S11` | P8R inherits the unresolved upstream P3/P7 discrepancy on the Gaussian SR gain. Every P8R SR quantity is anchored on a number that downstream campaigns now measure differently from the priority that owns it. P8R measures it a third time and **does not resolve it**. |

## 4. Procedural limitations — specific to this repair

| # | limitation |
|---|---|
| `P1` | **The pre-anchor runtime pilot is a real degree of freedom, disclosed.** Throughput was measured and the calibration update rule's convergence was checked on a scratch copy before the anchor. That pilot did not fix any verdict, gate threshold or estimand, and it used addresses no P8R result uses — but it is the one place where information flowed from simulation into the frozen protocol, and an adjudicator should treat it as such. `REPAIR_RATIONALE.md` §5 and `TEMPORAL_ANCHOR.md` §7 record it. |
| `P2` | **The gates were written by the same agent that ran the experiments**, before production but with full knowledge of P8's outcomes. Knowing that `G4` failed at 10% is not the same as choosing 10% afresh; the mitigation is that the thresholds are *numerically identical to P8's*, so the comparison to P8 is like-for-like. Where P8R's rule differs in form (`S8`, `S15`, `S17`), the difference is argued in the frozen prose and fixed at the anchor. |
| `P3` | **`TEMPORAL_ANCHOR.md` is written after the commit it names.** It has to be. Nothing in the campaign trusts it: `I1`, `I6` and `I7` read git. But a reader who takes the hash on trust has learned nothing. |
| `P4` | **The scratch tree that hosted the pilot was deleted rather than committed.** That is the right disposition for throwaway output at reduced budgets, but it means the pilot's numbers are not independently re-checkable from the repository. Only the two conclusions drawn from it are recorded. |
| `P5` | **P8R re-measures quantities owned by P4, Stage-D, P3 and P7 and adjudicates none of them.** Where a P8R number and a historical number differ, both are reported and nothing is edited. |
| `P6` | **Novelty is not adjudicated.** `NOVELTY_STATUS = NOT_ESTABLISHED`, permanently for this campaign. |
| `P7` | **The claim-class firewall is a blunt substring check, and it fires on negated mentions too.** `tests/test_claim_firewall.py` rejected an earlier draft of §6 of this file: two of its disclaimers were phrased as "Not that X ..., approximately ..., or ...", which put the affirmative collocation for the window-separability law and for detector transfer into the text even though both sentences *denied* the claim. The disclaimers were rephrased; no claim changed. The bluntness is deliberate (a firewall that parsed negation could be talked around), but a reader should know that its passing means "no forbidden collocation appears", not "no overclaim was made". Judging overclaim is the adjudicator's job, not the regex's. |

## 5. Implementation limitations found in this campaign

| # | limitation |
|---|---|
| `I1` | **The calibration-failure exclusion path is implemented but was not exercised.** `experiments/thresholds.py` raises rather than substituting a threshold, and the cell drivers write `EXCLUDED_CALIBRATION_FAILED` artifacts — but in this run no family ended `CALIBRATION_FAILED`, so that path carried no production data. Worse, `experiments/aggregate_gamma.py` writes excluded cells without a `per_m` block and `experiments/derive_resolution.py` indexes `per_m` unconditionally for `S6`, `S7`, `S7D`, `S7F`, `S13` and `S15`; had a family failed, those questions would have raised `KeyError` rather than resolving. **This is a latent defect in anchored source.** It is disclosed rather than patched, because patching source after the anchor is exactly what `I3` and `I7` exist to prevent, and because no production result depended on it. A future campaign that expects an exclusion must fix it *before* its own anchor. |

## 6. What P8R explicitly does not claim

* Not that `P8 = FAIL` is wrong, revisable, or softened. It is authoritative and
  P8R leaves it exactly where it stands.
* No claim that `H1`, the window-separability law, is true in any form — not
  exactly, not approximately, not up to a scale factor, not for most cells.
  `S7`, `S7D` and `S7F` all resolved `REJECTED`.
* No claim of transfer between the two detectors, and no claim that the measured
  absence of it is a permanent or universal non-equivalence: it is absent in the
  tested cells, and that is the whole of it.
* No claim that P7's operational boundary conclusion carries across families.
* Not that `P8R-T1` holds unconditionally for any family, and least of all for
  `t3`.
* Not that local attraction occurs at `t3`/`m=20`.
* Not that any P8R number is a certified numerical result.
* Not that anything here is novel.
* Not that a `CLOSED_CANDIDATE` verdict is a `CLOSED` status. It is a candidate
  awaiting independent adjudication.
