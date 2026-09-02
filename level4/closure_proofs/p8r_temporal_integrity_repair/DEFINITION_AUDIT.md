# P8R definition audit — is this the inherited question, and is it narrowed?

Written before any P8R production result existed.

## 1. Where the question comes from

The Priority-8 question is not P8R's invention and not P8's either. It is the
robustness matrix handed over by two upstream artifacts:

* `p7_statistical_consequences/` — the F1–F3 handoff and the scope section,
  which record that P7's operational conclusions were established for the frozen
  Gaussian specialisation and that transfer across innovation family, detector
  and window was left open;
* `p6_safe_rebaselining_predesign/` — exclusion `X5`, which explicitly removed
  model-class robustness from Priority 6's scope.

`p8_model_class_robustness/P8_DEFINITION_AUDIT.md` established that no
historical "P8" protocol, gate file, config or status entry existed anywhere in
the repository before that campaign, and distinguished the priority label from
historical uses of "P8" as a premise label. The independent adjudication
accepted that finding ("I found no scientific-question redefinition after
results") and it is inherited here rather than re-litigated.

## 2. The question P8R asks

Verbatim from `FROZEN_PROTOCOL.md` §1:

> Does the recursive re-baselining structure established for the two frozen
> Gaussian specialisations — the stopped-selection gain `Gamma`, the local
> stability boundary `rho_c`, and the operational monitoring degradation —
> survive outside that specialisation, across innovation-distribution families,
> detector families, reuse windows, reuse conventions and drift patterns, and
> which parts fail to transfer?

The clause **"and which parts fail to transfer"** is doing real work. A campaign
whose only admissible answer were "yes it transfers" would be unfalsifiable;
P8R's resolution semantics (`FROZEN_GATES.md` §3) give every question an
admissible negative outcome.

## 3. Is P8R easier than P8?

This is the audit's central obligation, because narrowing a failed campaign's
question is the cheapest way to fake a repair. Compared cell by cell:

| axis | P8 | P8R | narrower? |
|---|---|---|---|
| innovation families | 6 (`gaussian`, `t10`, `t5`, `t3`, `contam0.05`, `contam0.1`) | the same 6 | no |
| detectors | 2 (frozen two-sided CUSUM `k=1/2`, frozen symmetric two-chart SR) | the same 2 | no |
| windows, gated | `{1,2,3,5}` | the same | no |
| windows, reported only | `{10,20}`, `EXTRAPOLATION_BEYOND_P3` | the same, `S7X = OUT_OF_SCOPE` | no |
| conventions | A (`min(m,tau)`) and B (`m`) | the same | no |
| reuse ladder | P7's, verbatim | P7's, verbatim | no |
| drift patterns | in-control, step `{0.5,1,2}`, ramp `{0.02,0.05}` | the same | no |
| `E1` cycles per cell | 4,096,000 | 4,096,000 | no |
| independent seed family `E5` | yes | yes | no |
| SR calibration search budget | 163,840 cycles × up to 12 iterations, then an added 614,400-cycle phase | 262,144 × 6 then 819,200 × 3, fixed | **larger, and fixed in advance** |
| SR calibration holdout | 1,024,000 cycles, reused after tuning | 1,228,800 cycles, read once; a second pre-reserved holdout for the one frozen retry | **larger and genuinely held out** |
| chain ladder | 2,000 replicates × 70 cycles, burn-in 20 | the same | no |
| drift | 6,000 replicates × 24 cycles, change at 20 | the same | no |
| gate thresholds `S6`–`S13` | `G3`,`G4`,`G4-D`,`G4-F`,`G5`,`G6`,`G7`,`G8`,`G10` | numerically identical | no |

**Conclusion: P8R is not narrower on any factor and is strictly larger on the
calibration budgets.** Where P8R differs it is by removing degrees of freedom
from the *procedure*, not from the science.

## 4. Where P8R is explicitly narrower than P7, and says so

One place, declared here rather than discovered later. P8's `G7` claimed to
apply P7's boundary test "verbatim"; the adjudication found that too strong,
because the implementation covered only `m in {1,5}` and four metrics, omitting
half of P7's `m` coverage and P7's `R_delta` metric.

P8R keeps the same sub-family grid — `detector x m in {1,5}` and the metric set
`{arl, ref_mse, fap100, e_acf1}` — because the chain ladder is what produces
them, but it **does not** call that verbatim P7 coverage. `S10`'s frozen rule
says, in the rule text itself, that it is "P7's criterion applied to a DECLARED
SUBSET of P7's coverage". The subset is frozen here, before results, and cannot
be widened afterwards to rescue the question.

## 5. Estimand identity — the three `Gamma`s

Inherited from P8's cross-priority finding, which the adjudication verified and
which P8R does not re-open:

* `Gamma_A = E[ zbar^A_m * sum psi(z_t) ]` — raw convention-A window against the
  family score sum. **This is the derivative of the frozen raw-mean reference
  map**, and its `m=1` case is P4's `Gamma_f`. Every P8R gate uses this one.
* `Gamma_psipsi = E[ psibar^A_m * sum psi(z_t) ]` — Stage-D D3's `Gamma_psi`, the
  multiplier of a score-transformed reuse rule that no ReBaseGuard artifact
  implements. Recorded, never gated.
* `Gamma_naive = E[ zbar^A_m * sum z_t ]` — Stage-D's
  `gamma_T_naive_DIAGNOSTIC_ONLY`. Recorded, never gated.

The apparent disagreement between P4's and Stage-D's published numbers is
definitional, not a measurement conflict. P8R owns neither artifact and edits
neither.

## 6. Terms fixed before results

| term | frozen meaning |
|---|---|
| *eligible cell* | `(D, f, m)` with `m in {1,2,3,5}` and `f` not in `MOMENT_MARGINAL` |
| `MOMENT_MARGINAL` | `("t3",)` — divergent third absolute moment of the `Gamma` integrand, so no Berry–Esseen rate and an infinite-variance sample variance. Reported in full, never counted in `S6` either way. |
| *attraction* | `Gamma_A < 2`, i.e. `rho_c > 1`: full reuse is locally attracting |
| *repulsion* | `Gamma_A > 2`, i.e. `rho_c < 1` |
| `K(D,f,m)` | `rho_c(D,f,m) / rho_c(D,f,1)`, the window factor whose invariance is the separability law |
| *transfer* | a quantity measured in one detector/family reproducing in another **within its stated interval**; never assumed |
| *resolved* | a question assigned exactly one of `SUPPORTED`, `REJECTED`, `INCONCLUSIVE`, `OUT_OF_SCOPE` by its frozen rule |

## 7. What P8R may not claim

Inherited literally from the P8 adjudication's §16 handoff table, and enforced by
`tests/test_claim_firewall.py`:

* the rejected window-separability law may not be described as "approximately
  holding";
* detector transfer may not be assumed anywhere;
* P7-boundary transfer may not be assumed anywhere;
* `P8R-T1` may not be stated unconditionally;
* nothing here is a certified numerical result;
* no novelty, no priority, no new algorithm.
