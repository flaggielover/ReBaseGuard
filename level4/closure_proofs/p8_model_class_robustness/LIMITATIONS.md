# P8 limitations

Written to be read by someone trying to break the campaign. Ordered by how much
damage the limitation does if it turns out to matter. Nothing inherited from
P4, P5, P6 or P7 is softened here; §6 restates the inherited limitations that
still bind P8.

---

## 1. Scope limitations that no P8 result escapes

| # | limitation | consequence |
|---|---|---|
| `L1` | **P8 widens the model class along four named axes and no others.** Six innovation families, two detector families, six windows, two window conventions, two drift patterns. Everything else is unchanged: iid innovations, a location shift, full detector reset at every alarm, a single frozen ARL match, no autocorrelation, no scale change, no multivariate structure, no real data | "outside the frozen Gaussian specialisation" is **not** the same as "outside simulation". No P8 number is evidence about a real process |
| `L2` | **The innovation families are a designed set, not a sample of anything.** They are Stage-D's six, chosen there for regularity and analytic tractability. They are all *symmetric* and all *unimodal* | P8 says nothing about skewed, discrete, bounded or multimodal innovations. A skewed family is the single most obvious untested case, and it is untested because no frozen ReBaseGuard artifact defines one |
| `L3` | **The detector families are the only two the repository closes.** P8 deliberately declined to add a third (`P8_DEFINITION_AUDIT.md` §6 `O1`) because no closed derivative theorem would stand behind it | Any statement of the form "this holds for detectors" means **these two**. CUSUM and SR are also close relatives — both are likelihood-ratio-based two-chart schemes with the same Gaussian design — so agreement between them is weaker evidence of generality than two arbitrary detectors would be |
| `L4` | **The detector statistic is frozen at its Gaussian design in every family; only the threshold is recalibrated.** That is the Stage-D convention and the operationally realistic one | P8 therefore measures the robustness of *a Gaussian-designed chart run on non-Gaussian data*, **not** the robustness of the re-baselining phenomenon to a family-optimal chart. A score-based chart for `t3` is a different detector and is untested |
| `L5` | **The contaminated families do not have unit variance** (`1.4` and `1.8`), by Stage-D's frozen construction. So `k = 1/2` is not "half a standard deviation" there | Cross-family comparisons at fixed `k` mix a distribution-shape effect with a scale effect. The ARL match removes the first-order consequence; it does not remove the confound |
| `L6` | **`P8-T1` rests on a `PARTIAL` premise.** It is P4's abstract stopped-score theorem applied to a new stopped functional. P4's status is `PARTIAL` and P8 does not change it | Every `rho_c` in P8 is `THEOREM_CONDITIONAL_ON_PARTIAL_PREMISE`, not a closed result |
| `L7` | **No stationarity theorem exists outside the Gaussian core.** P5's `T7` is Gaussian-scoped (`p5/LIMITATIONS.md` §1) | **Every** non-Gaussian chain quantity in P8 is a finite-horizon average after a declared burn-in of 20 cycles. None is a stationary quantity, and P8 does not claim ergodicity, uniqueness of an invariant law, or convergence anywhere |

## 2. Theory limitations

| # | limitation |
|---|---|
| `T1` | **`P8-T1`'s analytic hypotheses (P4's 7–9) are assumed, not verified, per family.** P8 verifies hypotheses 1–3 (measurability of the truncated-window functional) by proof, and 4–6 by quadrature on the density; hypotheses 7–9 — almost-sure finiteness of `tau` locally in `e`, absolute summability of the event-sliced change of measure, and integrable domination of the stopped likelihood difference quotient — are **stated as assumptions**. Establishing them for the two-sided CUSUM and SR recursions is open |
| `T2` | **`H1` is not a theorem and has no proof sketch that survives inspection.** `P8-L1(c)` reduces it to invariance of the normalised lag profile, which is a restatement, not an explanation. Why stopping-time selection should distribute over recent lags in a detector- and distribution-free way is **unexplained** |
| `T3` | **`P8-T2` is exact and operationally empty on its own.** `A_f` has no closed form in any family; the theorem licenses the experiment design and nothing else |
| `T4` | **No enclosure, no formal proof.** There is no Arb interval layer and no Lean declaration in P8, deliberately (`P8_DEFINITION_AUDIT.md` §4 `O4`). Every P8 number is `EMPIRICAL` in P3's evidence hierarchy, rank 4 at best where a theorem is evaluated at measured inputs |
| `T5` | **`X6` binds throughout.** Nothing in P8 infers an operational consequence from `Gamma` or `rho_c`; the relationship between them is measured and is reported as an association, never as a mechanism |

## 3. Statistical limitations

| # | limitation |
|---|---|
| `S1` | **`t3` is on the third-moment boundary.** The `Gamma_A` integrand inherits the innovation tail index, so for `nu = 3` the CLT applies but no Berry–Esseen rate does, and the sample variance itself has infinite variance. `t3`'s reported standard error is **not trustworthy**, is declared so before production, and `t3` is excluded from the primary invariance gate and reported separately everywhere |
| `S2` | **`t5` is on the fourth-moment boundary for the *variance of the variance*.** Its SE is finite and usable but converges slowly; treat its interval as indicative |
| `S3` | **The window law is tested on a finite `m` grid** `{1,2,3,5}` plus `{10,20}` as declared extrapolation. Whether `K(m)` continues to behave the same way for larger `m`, or has a different form as `m` approaches the ARL, is untested. The one cell where the phenomenon disappears entirely (`Gamma_A < 2`, CUSUM `t3` at `m = 20`) is **inside** that untested extrapolation region, so P8 cannot say whether it is the start of a trend or an isolated crossing |
| `S4` | **Large-`n` significance.** At `4.1e6` cycles a `1%` heterogeneity is highly significant. Every invariance gate is a practical-equivalence gate with a pre-declared margin, and the formal homogeneity statistic is reported as *descriptive only*. A reader who reads the `p`-values as the result will draw the wrong conclusion |
| `S5` | **Multiplicity.** One primary hypothesis at one primary statistic; secondary families use BH at `q = 0.10`. The real protection is reproduction across detectors, families, windows and an independent seed family, not the adjustment |
| `S5b` | **`E4` runs only 4 post-change cycles.** The change lands at cycle 20 of 24 and the delay metric is the first post-change cycle. That is the right metric for a step and the wrong one for a ramp, whose whole question is accumulation over many cycles. P8's ramp conclusion is confined to the first post-change cycle plus an exact `rho = 0` argument, and does not measure ramp accumulation at `rho > 0` |
| `S6` | **The chain grid is coarse in `rho` and short in `m`.** Chain experiments use `m in {1,5}` and 13 reuse fractions. Anything about `m in {2,3}` operationally, or about `rho` between ladder rungs, is not measured |
| `S7` | **The drift study is under-powered in the tail at large `Delta`,** exactly as P6's `S8` records for its own campaign. Every cell with fewer than 200 tail events is labelled `INSUFFICIENT_TAIL_EVENTS`, and the label is not decoration |
| `S8` | **CRN pairing is across detector, window, convention and `rho`, not across families.** Family comparisons are unpaired and their differences carry the full independent variance |
| `S9` | **The SR calibration is P8's own.** Its residual ARL error propagates into every SR non-Gaussian number; a `0.5%` ARL mismatch is not nothing when `Gamma` differences of a few percent are being compared. Measured residuals are `0.01%`–`0.44%`, the worst at `t3`, whose SR operating point is therefore the least well matched in the matrix |
| `S10` | **P7's boundary criterion has no uncertainty margin, and P8 applies it at half P7's resolving power.** It is a bare `max` over brackets; P7 had 8 `(detector, m)` sub-families per test, P8 has 4 per innovation family. Two of the six families flip to `OPERATIONAL_BOUNDARY` on differences that the uncertainty companion puts at well under 1 standard error (`contam0.05`) or that do not survive BH correction across the 96 comparisons (`t3`'s `arl`). Gate `G7` fails on the literal criterion and P8 reports it failed; the companion analysis is `DESCRIPTIVE_ONLY` and changes no gate |
| `S10b` | **P8 inherits an unresolved upstream discrepancy.** P8's Gaussian SR gain is `0.70%`–`0.80%` below P3's at every window (`z = -1.75..-2.07`), agreeing instead with P7's independent re-measurement. Every P8 SR quantity is therefore anchored on a number that two downstream campaigns now measure differently from the priority that owns it. The effect is under `1%` and no P8 conclusion depends on it, but every P8 SR `rho_c` inherits it |
| `S11` | **The one boundary signal that survives multiplicity does not corroborate across detectors.** `t3`, CUSUM, `m = 5`, `fap100`, `+3.11` SE, `p = 9.4e-4` of 96 tests — but the same cell under SR is at `+0.92` SE. One detector, one window, one metric, one family. It is a lead for a follow-up, not a result |

## 4. Procedural limitations

| # | limitation |
|---|---|
| `P1` | **No P8 gate existed before this campaign.** They are all `P8_ORIGINAL`, written by the same agent that ran the experiments, before the production runs but after a pilot that had already reproduced P3 and P4. The pilot's influence on the gate thresholds is recorded in `results/pilot_notes.json`; a reader should check that record rather than take the claim on trust |
| `P2` | **The `G4` margin of 10% was chosen from P3's cross-detector spread and Stage-D's cross-family spread of a *different* estimand.** It is a judgement, not a derivation |
| `P3` | **`t3`'s exclusion from `G4` is a pre-declared exclusion with a mathematical justification, but it is still an exclusion.** If `t3` had been included, `G4`'s outcome could differ. Both readings are reported |
| `P4` | **P8's re-measurements bear on P4 and Stage-D artifacts that P8 does not own.** Where P8's number and a historical number differ, P8 reports both and edits nothing. It does not adjudicate, and its report is not a re-opening of either priority |
| `P5` | **Novelty is not adjudicated** (`NOVELTY_AUDIT.md` §5) |

## 5. What P8 explicitly does not claim

* No claim that the phenomenon is distribution-free, universal, or
  detector-independent. `location_family/FINAL_REPORT.md` §A forbids that
  reading of P4 and P8 does not earn it either.
* No claim about any detector family outside `{CUSUM, SR}`.
* No claim about any innovation family outside the six.
* No claim that `rho_c` is operationally meaningful in **any** family.
* No claim of stationarity, ergodicity or convergence outside the Gaussian core.
* **No claim that the window-separability law holds.** `H1` was preregistered and
  is **rejected** across innovation families. The surviving statement is the
  measured cross-detector residual (`<= 3.63%`) beside the cross-distribution
  spread (`22%`–`49%`), and even that misses its own `3%` sub-gate in one of
  fifteen comparisons.
* **No replacement law.** All three post-hoc hypotheses `H2a`–`H2c` were
  rejected on the held-out cells.
* No algorithm, no policy, no recommendation, no design constant.
* No novelty.

## 6. Inherited limitations that still bind

Restated, not softened:

* **P4 is `PARTIAL`.** Its numerical gate failed on the `t3` replication
  criterion; its Lean was `NOT AUTHORIZED` and `NOT RUN`; the location-family
  result "is not distribution-free, universal, detector-independent, or a
  class-wide instability certificate".
* **P5 is `PARTIAL`.** `T1`–`T5`, `T7`, `T11` hold only within their stated
  Gaussian, convention-A, `Delta = 0`, `rho in [0,1]`, `m in {1,2,3,5}` scope.
  `T8`–`T10` are conditional. Its numerics are not design constants (`X9`).
* **P6 is `CLOSED` with its limitations intact**: calibration converged in 6 of
  8 cells; `cusum_m2` and `sr_m3` remain nonconverged; sparse/fallback `s1`
  evidence remains; the final refit is not a verified fixed point; sensitivity
  does not prove convergence; `Delta = 0.5` is inconclusive; `Delta = 2` tail
  evidence is under-powered; detector transfer without recalibration is not
  established; finite-reference evidence is post-burn-in; scope is one frozen
  Gaussian convention-A model; novelty is **not** established. P8 uses none of
  P6's numerics as premises, so none of these propagate into a P8 result — but
  none of them is retracted either.
* **P7 is `CLOSED`** with no rank 1–3 evidence, no stationary-law theorem, and
  the rejected candidate `P7-E`, which forbids first-order transfer from
  `d E[e_1]` to `d E[M(e_1)]`.
* **Stage D is `STAGE-D-PARTIAL`.** Its thresholds are adopted as frozen
  operating-point conventions; its `Gamma_psi` values are a different estimand
  and are not premises.
