# C7 — disposition of open notes

## N1 — ψ *is* monotone decreasing. C7 does not use that, and here is the arithmetic for why.

*Producer: `code/c7_psi_monotonicity.py` → `evidence/psi_monotonicity/C7_PSI_MONOTONICITY.json`.
Every figure below is emitted there; none is asserted only in prose. The fresh-context review
reached the same conclusion independently (finding 10) and its `ψ·h ≤ 0.943443` at `u = H` is the
same fact as the `max ψ′ = −0.0566` quoted here.*

C7's theorem deliberately avoids assuming `ψ` is decreasing, and `psi_exact` is used only as a guard.
An independent numerical check established that `ψ` **is** in fact strictly decreasing on `[0,5]`,
with `max ψ′ = −0.0566` — bounded well away from zero, so this is not a floating-point-marginal
conclusion. The campaign's statement that the monotonicity is "not proved" was accurate about C7's
proof but invited the reading that it might be false. It is not false.

**How far it is provable.** Writing `s = K + v`, the density of `V` on `(0,∞)` is proportional to

    f(v) ∝ exp(−(s² + e²)/2)·cosh(s·e),   so   (log f)″ = −1 + e²/cosh²(s·e),

so `f` is log-concave — hence the hazard increases and the mean residual life decreases — exactly
when `cosh(s·e) ≥ e`, i.e. `s ≥ arccosh(e)/e = 0.659111601`, i.e. `v ≥ 0.159111601`. The standard
argument therefore proves `ψ` decreasing on `[0.159112, ∞)` and says nothing on `[0, 0.159112)`. At
the frozen partition `N = 64`, exactly **two** of the 64 knots (`u = 0.078125` and `u = 0.15625`) lie
in the unresolved region.

**What it would buy.** Replacing `ψ_lo` by `ψ_exact` at every knot — which is what the monotonicity
would license — gives:

| | with ψ_lo | with ψ_exact | gain |
|---|---|---|---|
| `E[R]` | 0.438328588 | 0.441387195 | +0.6978 % |
| bound | 3.586306094 | 3.588323092 | **+0.0562 %** |
| margin over the critical A0 | 9.7933 % | 9.8551 % | +0.0617 pp |

**Disposition: NOT TAKEN.** The gain on `E[R]` is 0.70 %, but `E[R]` is only 0.44 of the `H + E[R] =
5.44` that the bound divides, so it dilutes to **+0.056 %** on the reported value. That does not
change any verdict, any band, or any conclusion. Against it stands a delicate argument that fails on
part of its own domain and would need a separate treatment for the first two knots. C7 declines the
trade and records the foregone amount rather than leaving the question open.

This is recorded as a **finding against C7's own presentation**, not as a defect in its result: the
bound is valid either way, and is 0.056 % weaker than it could be.

## N2 — Lorden's inequality is loose here by about 2×

The independent check observed that the true `E[R] ≈ 1.04797`, essentially the asymptotic
stationary-excess mean `E[V²]/(2E[V]) = 1.048343`, while Lorden's certified upper bound is
`E[V²]/E[V] = 2.096687` — looser by very nearly the factor 2 that the asymptotic suggests.

This affects only the `U` used by the L3 Lorden variant, and `U` enters the bound weakly: the spread
between `U = 4.679910` (Lorden) and `U = 5.937205` (C7's own elementary lemma) moves the reported
bound from 3.600338 to 3.586306, i.e. **0.39 %** for a 27 % change in `U`. So the looseness of
Lorden is not a material constraint on C7's result, and sharpening it is not a route worth pursuing
inside this campaign.

**Disposition: RECORDED, NO ACTION.** It is relevant to a successor only if a much tighter `U` became
available, and even then it is worth at most a few tenths of a percent.

## N3 — the true `E[τ′] ≈ 3.98842`, so C7's bound is ~10 % conservative

Monte Carlo puts `E[τ′]` at 3.98842 ± 0.00050. C7's PRIMARY certified bound is 3.586306, so the
bound is about **10.1 %** below the true value of `E[τ′]` — and `E[τ]` is larger still, since `τ ≥ τ′`
pathwise. The remaining conservatism is the LP's, and the E2-family ceiling of 4.679910 shows how far
the family could in principle be pushed.

**Disposition: RECORDED.** This is a lower bound doing its job, not a defect. It is noted so that a
successor does not mistake 3.586306 for an estimate of `Λ_309`.

**The Monte Carlo is a cross-check and is not evidence.** It is not certified, it is not committed as
a producer, and no C7 conclusion rests on it. It appears here only because it independently confirmed
that every certified bound holds and that Wald's identity is satisfied by an independently coded
simulator.

## N4 — the phase-ordering deviation

The plan put a fresh-context review before the final evaluation; it happened after. The gate freeze,
which was the load-bearing requirement, did precede the evaluation, and
`evidence/governance/HANDOVER_FACT_VERIFICATION.json` reports the ordering of every artifact against
the gate truthfully, including that the ledger landed in the same commit as the gate and was in fact
produced before it.

**Disposition: DISCLOSED, REPAIRED IN SUBSTANCE.** The review was given the certificate as a draft
required to survive it, with instructions not to soften findings because an artifact already existed.

## N5 — the pre-publication review returned NOT_READY, and what that changed

`review/REVIEW_C7_PREPUBLICATION.md`: 17 findings, 2 CRITICAL, 7 MAJOR, 3 MINOR, 5 OBSERVATION.

**The numbers were never in doubt.** Item J — the check this programme has failed at least five
times — came back completely clean: all four bounds, all three `U` values and every `E_R_lower`
reproduce as exact rationals identical to the certificate and the ledger; every README figure, the
10.37× multiple, the ceiling and the headroom all reproduce; C4/C5 baselines match their sources; the
certificate, gate and model shas all verify. Items A–E were verified correct by hand, including the
non-obvious rounding direction in `U_elementary`'s mixed endpoints.

**The mechanisms were.** Both CRITICALs were live exploits of the campaign's own API, not hypotheses:
a forged `a_grid` and an out-of-cell `e`, each yielding a kill-gate-clean bound above the published
PRIMARY. Both are closed (`ERRATUM_C7_GATE.md` E1, E2) and regression-tested (M16, M17, M18).

Repairs made in response, all re-run and re-verified:

| finding | repair |
|---|---|
| 1, 2 CRITICAL | `a > 0` enforced; frozen grid bound in code; cell membership enforced; M16–M18 added |
| 3 | Lemma C7-U step 0 now executes and its result rides in every `U` certificate (E3) |
| 4 | the false "below the 2^-320 grid" class replaced; M01–M04 now reported as **surviving** |
| 5 | M11 drives the real floor guard instead of a copy it wrote for itself |
| 6 | the coverage gap quantified: **+1.0985 %**, and the range widened to the registry `U` |
| 7, 16 | B0 made re-runnable by ancestry, all 9 modules walked, `__import__`/`eval` escapes closed, `re` allowlisted |
| 8, 9 | README's surface-independence and C4-margin claims narrowed to what is true |
| 11 | `code/c7_primitives_test.py` commits known-value tests for `G.Phi` / `G.phi` |
| 12 | M07 and M13 reordered so each reaches its own guard |
| 13 | the accidental `and` fixed; dead code **partly** removed — see N7, the adjudication found `lambda_lower_tier2` still present, public and unguarded |
| 14 | the Monte Carlo breach disclosed and declared in the certificate (E4, E5) |
| 15 | fact-check regex widened to 4 decimals; scope and blind spots stated in the artifact |
| 17 | the ψ wording corrected in the README and backed by a producer |

**Finding 4 is the one worth restating.** The suite's four rounding-direction mutants — the
mutants testing its own stated organising principle — **survive**. They are now reported as
surviving rather than folded into `undetected = []` under a justification that was numerically false
by up to 405×. The suite supplies *no* positive evidence on rounding direction; that was established
by hand in the review instead, and the record now says so.

**Disposition: ALL FINDINGS ADDRESSED.** The published bounds are unchanged — 3.586306094 before the
repairs and after them — which is the expected outcome, since every defect was in a mechanism or a
claim rather than in the committed evaluation path.

## N6 — what a successor should inherit

1. **Freeze values in code, not in prose.** The a-grid was "frozen" as a gate string and bound
   nothing. A frozen constant that no code compares against is decoration.
2. **Enforce side-conditions at the entry point.** `e ∈ cell` and `a > 0` were both stated correctly
   in prose — in the gate and in the lemma's own docstring — and enforced nowhere.
3. **A mutation suite must drive the real path.** M11 tested a rule it had written for itself; the
   guard it named was never exercised by anything.
4. **State what a passing check cannot see.** `FACT_CHECK_CLASS: PASS` was true and reached none of
   findings 3, 4 or 6, because no numeral-comparing check can reach a behavioural claim.

## N7 — the independent adjudication: ACCEPTED_WITH_CONDITIONS

`review/ADJUDICATION_C7.md`. **15 findings LANDED, 2 PARTIAL, 0 NOT_LANDED.** Both CRITICAL exploits
were re-run by the adjudicator out of tree and confirmed closed *by the specific guard*, not
incidentally — it ran eight variants to establish that the forged-grid refusal and the
re-derivation-mismatch refusal are distinct guards. Lemma C7-U step 0 was verified by instrumentation
to execute twice on the PRIMARY path and zero times on tier-1, which is correct. All four bounds,
three `U`s, three `E_R`s, the ceiling, the PRIMARY selection and the verdict class were recomputed
from the repaired modules and are **identical as exact rationals**.

It also found **nine defects neither the review nor the campaign had found**. Four needed errata
(E6–E9); all nine are repaired:

| # | defect | repair |
|---|---|---|
| N1 | README layout block stale in four places | corrected; the fact-checker cannot see integers, by its own declared blind spot |
| N2 | `lambda_lower_tier2` dead, **public and unguarded** — `e = 1.90, U = 0.1` returned 4.219038180 | function removed (E7); the disposition's "dead code removed" was false of it |
| N3 | **`K` and `H` unchecked at every real entry point** — `H = 6` gives 4.250984509, above PRIMARY, and KG5 does not fire | `_require_frozen_model` at every entry point (E9); M19/M20 drive the real path |
| N4 | a B0 check named a property it did not test; another's condition was the literal `True` | both now test real properties |
| N5 | five kill gates enforced that the frozen gate does not enumerate | KG10/KG10b declared and kept; **KG11 removed** — it gated on an analysis the theorem does not use (E8) |
| N6 | `MONTE_CARLO_RUNS` and `mirror_equivalence_asserted` were literals, the latter making its own gate vacuous | mirror equivalence now carries both values and is compared; the MC count is marked declared-not-measured |
| N7 | within-commit ordering unverifiable | recorded as a limitation, below |
| N8 | `finiteness` bound inside the loop, so step 0 reported the *last* source not the PRIMARY | bound explicitly from `"elementary"` and the source is named in the artifact |
| N9 | the ledger predated the repairs | regenerated |

**The one that should have been caught here, not there.** N3 is C4's own documented
threshold-confusion failure mode — the error whose repair C4 made structural, and which this
campaign's gate lists as KG7. C7 inherited the check into `c7_certificate.py`, where it tested that
module's own constants, and into the mutation suite's *mirror*. The real entry points accepted any
`K`, `H` at all, at a larger inflation (+18.5 %) than either exploit the review found. Three
successive rounds of adversarial attention were needed to find a defect the programme had already
documented once.

**The one that is pure governance.** E6: `MUTATION_CLASS` read `PASS` while the artifact's own prose
said four required mutants survive, and the frozen KG8 says any such survivor means REFUSE. The
campaign had narrowed a frozen kill gate in its own favour and mentioned it nowhere. It is now
reported as `PASS_WITH_SURVIVORS`, with the frozen text and a `KG8_literal_status` of **NOT
SATISFIED** carried in the artifact.

**Acknowledged limitation (adjudication N7).** The certificate gates on the mutation, primitives, ψ
and B0 artifacts, and all were committed together, so commit-granular ordering cannot establish that
the certificate was produced *after* the artifacts it consumes. Stated rather than inferred either
way. What can be established: the certificate re-reads each artifact at run time and fires its kill
gates on their contents, and the full chain has been re-run end to end in dependency order.

**Disposition: ALL CONDITIONS ADDRESSED.** The published bounds are unchanged through both rounds —
**3.586306094**, before the review, after the review, and after the adjudication. Every one of the 26
findings across the two rounds was in a mechanism, a claim, or a presentation, and none in the
committed evaluation path.
