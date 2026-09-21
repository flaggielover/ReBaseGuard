# Disposition of the C4 pre-result review notes

Review: `review/REVIEW_C4_PRERESULT.md`, fresh context, verdict **READY_TO_EVALUATE_WITH_NOTES**, 0 blocking FAIL.
Every note it asked the campaign to address before adjudication is listed with what was done. Nothing is deferred.

| note | substance | disposition |
|---|---|---|
| (a) | the theorem L proof cited Lemma T for `E[tau] < infinity`, but Lemma T bounds `E_x[tau ^ T_a]`, the **taboo** time — a different, smaller random variable | **Fixed at source.** The proof now derives Wald from Tonelli as an identity in `[0, +infinity]`, so no finiteness hypothesis is needed at all; the correct citation for finiteness (theorem AD §4's whole-kernel supersolution, `E_a[tau] <= W(a) = Abar`) is given alongside, with a note that Lemma T is not it. |
| (a) | "K > 0 makes the two positive parts disjoint, **so** each is at most `V_i`" is a non sequitur | **Fixed at source.** The pathwise step now says what actually implies it (`±z <= |z|` and `x -> (x-K)^+` nondecreasing), and disjointness has been moved to the one place it does work: writing `E[(|z|-K)^+]` as a sum of two one-sided expectations. |
| (b) | the state space was described as the ambient box `[0,H]^2`; the operator acts on the reachable closure `X` | **Fixed at source** in `c4_model_identity.py` and Phase 1 §2, with the `OPERATOR_AUDIT.md` §1 definition and its source cited. Theorem L is unaffected — its argument is pathwise and the chain started at `a` stays in `X`. |
| (b) | cells 308 and 309 were called "disjoint"; they are adjacent closed intervals sharing `e = 1.983910` | **Fixed at source**, and the consequence the campaign had missed is now stated: the number certified for 309 is evaluated at the shared endpoint, so it is simultaneously a valid lower bound on `Lambda_308`. |
| (c) | M05 raised an uncaught `Refusal` and killed the whole Phase 7 run before M06–M12 ran | **Fixed.** The suite catches `Refusal` and records it as `DETECTED_BY_GUARD`. |
| (c) | M06 claimed to test the domain requirement but shifted each cell to its own `e_hi`, which is *inside* the closed cell, and left 309 unperturbed | **Fixed.** M06 now shifts two cells to the left, genuinely outside the closed cell, and the domain guard refuses it. |
| (c) | M02, M03, M04 undetected against the suite's own rule; **M04 is the serious one** — mis-taking the threshold as `C = 11/2` inflates the bound, the unsound direction, and was invisible | **Fixed structurally, not by adding a test.** `c4_certificate.evaluate` now refuses any `(K, H)` with `K + H != C_CUSUM`, tying the pair theorem L consumes back to the frozen producer's own definition; M04 and M05 are both refused by it. M02 is now detected at the decision-rule level, exhibited on the exact input `Gamma = 0` where the two rules differ. M03 is reclassified `VALUE_ONLY` with its magnitude (2.86e-95) and an explicit statement that it is **not** equivalent, merely too small to flip this verdict. |
| (c) | the "shares no function" independence claim was false — the alternative path called the production exp, arctan and sqrt | **Fixed by rewriting it.** `c4_independent.py` uses Bernoulli/AM-GM brackets for exp, Archimedes polygons for pi and the composite midpoint rule for the erf integral: **no series in common**. What remains shared (the interval container, the integer-square-root helper) is named in the evidence. The achieved resolution — ~1e-7 against production's ~1e-95 — is recorded as a cross-check rather than advertised as a reproduction. |
| (d) | three unverified universal self-descriptive claims, plus a Phase 2 sweep that omitted `.md` | **All four fixed.** The README's "each refuses unless its pinned inputs match" is replaced by the actual per-producer list; the AWS clause is restated as a claim about C4's actions, not the estate's state; "no float is used in any value that reaches a certificate" becomes "no float enters any load-bearing comparison", which is true and checkable. The Phase 2 sweep now covers `.md` (56 hits, up from 34); the 22 new hits are 21 × `minorant` and one `subsolution` — the C3 adjudicator recommending this very computation, which asserts no bound. The conclusion is unchanged. |
| (e) | the README and Phase 3 over-claimed ("no operator-level certificate", "`{309}` under any route") | **Fixed at source.** Both are now scoped to the admissible family, and the 308 claim is labelled corroborated-not-proved. |
| (f) | the gate's PARTIAL clause requires a per-cell reason for every non-excluded cell; the producer emitted none | **Fixed.** `reason_not_excluded` now carries the certified reason ("the bound is too weak") separately from the uncertified diagnostic one, and says plainly that C4 certifies no upper bound on `Lambda`. |
| (g) | the monotonicity licence ladder stopped at the certified `A0`, while an admissible `A0` may be arbitrarily larger | **Fixed.** The ladder runs to `10^5 ×` the certified `A0`; `Gamma` is nondecreasing throughout and the intersection stays non-empty, saturating at +0.288317 (308) and +0.374145 (309) — matching the reviewer's independent values. |
| (h) | Phase 0 was not reproducible at a later HEAD: check 10 conflated "zero new-real" with "no path changed outside the C3 namespace", and `git` failures surfaced as tracebacks | **Fixed.** Check 10 is split into `10a_c3_declared_zero_new_real` and `10b_no_path_touched_outside_c3_and_c4`; `--is-ancestor` is tested by return code. Phase 0 now reports **13/13 PASS** at the current HEAD. |
| (i) | the gate discloses midpoint diagnostics where the endpoint value is decision-relevant (1.5 %, not 4.8 %) | **Erratum `ERRATUM_C4_GATE.md` E1.** The gate is frozen and is not amended. |
| (j) | the freeze must be described as binding what the result may mean, not as pre-registering what it would be | **Erratum E2**, and the final report follows it. |
| finding 7 | `monotone_check`'s ladder endpoints were transcribed constants in the one producer whose phase claims nothing is transcribed | **Fixed**; they are derived from `cell_geometry()`. |
| finding 11 | Phase 7 took ~17 minutes | **Fixed** by replacing the alternative implementation; the suite now runs in about a minute. |

## Notes carried forward to a successor

* **C4-N1.** The sharp lower-bound routes are designed and unused. `R1` (invert Lemma T on the committed taboo
  candidate: `tau_a >= w(a)/(1 + sup_X g)`) needs only the **supremum** of the supersolution defect, which the
  frozen certifier already computes in `min_max_on_reachable` and then discards — recording it is a one-line
  change to a re-run of `certify_block`. `R5` (a tight two-sided `tau_a` certificate) is sharper still. Neither
  can change any C4 verdict, so neither was run; a successor that wants a tighter floor should start there.
* **C4-N2.** C4 certifies **no upper bound** on `Lambda`. Everything it says about cell 308 being permanently out
  of reach is corroboration from float diagnostics and the reviewer's Monte-Carlo, not proof. The exact,
  diagnostic-free restatement is in Phase 1 §5: a certified upper bound on `Lambda_308` below 4.375229 would
  itself be an admissible `A0` closing cell 308 under the knockout. The two outcomes are exhaustive.
* **C4-N3.** "Closed under the knockout" is **not** closure. The knockout sets `A1 = A2 = 0`, which no real supply
  achieves. Nothing in C4 licenses the sentence "cell 308 is closable".
* **C4-N4.** `kernel_evaluations: 0`, `operator_certifications_run: 0` and `remote_hosts_contacted: 0` are literal
  constants in the emitters, not instrumented counters. They are true — the reviewer verified it statically and by
  running every producer on a host that has neither numpy nor python-flint — but a reader should treat them as
  assertions, and a successor that wants them to be evidence should instrument them.
* **C4-N5.** `_isqrt(0)` raises `ZeroDivisionError` rather than `Refusal`. Unreachable through `sqrt_iv`, which
  refuses a non-positive interval first. Cosmetic; left as found.

---

# Disposition of the C4 adjudication conditions

Adjudication: `evidence/adjudication/C4_ADJUDICATION.md`, fresh context, verdict
**ACCEPTED_WITH_SCOPE_LIMITATION**, excluded cell set **[309]**, 11 conditions. Every load-bearing figure in it was
reproduced independently before any of this was acted on: 18.2496× at cell 308 under `A0 = 4.311`; `Gamma =
+0.000000008` at `A0 = 4.375229` with `A1 = A2 = 0`; 2.203053× and 1.111966× at cell 307; `B(e0) = 3.191359686`,
0.7117 % **below** cell 309's threshold; `Gamma(B, A1_cert, A2_cert) = +0.064868395` at 309; `Gamma = −0.036197780`
at cell 306's full certified triple.

| # | condition | disposition |
|---|---|---|
| 1 | scope every restatement; `DETERMINISTIC_OPERATOR_ROUTE_EXHAUSTED` may not appear unqualified | **Binding. Adopted verbatim** as the campaign's standing form of words; the token appears nowhere in C4 unqualified, and the final report uses the adjudicator's narrowed sentence. |
| 2 | erratum for the two repairs that did not land in Phase 3 evidence | **Done: `ERRATUM_C4_GATE.md` E4 and E5.** The producer and `C4_ROUTES.json` are deliberately left byte-intact so the adjudicated evidence still reproduces exactly; `phase_3/C4_CANDIDATE_ROUTES.md` carries a banner pointing at the errata. Neither sentence may be quoted as establishing anything. |
| 3 | strike "one of them is progress"; replace with the 18.2× fact | **Done at source**, Phase 1 §5, with the figure reproduced independently (18.2496×) and with the `A0 = 4.375229` impossibility stated alongside. |
| 4 | enforce the licence rather than record it; exercise monotonicity in A1 and A2, not only A0 | **Binding on the successor, not retrofitted.** Both facts hold — the adjudicator verified them structurally and numerically, and so did C4's own ladder for `A0` — but `is_excluded` does not consult `licence`, and the ladder varies `A0` only. Changing `c4_certificate.py` now would regenerate an adjudicated artifact to no numerical effect, so it is carried forward as **C4-N6** instead. |
| 5 | the 2.6 % margin is the certificate's, not the fact's; state the midpoint fragility wherever it is quoted | **Binding. Adopted**, and stated in the final report: true `Lambda_309 ≈ 4.047` exceeds the threshold by 26 %, the route consumes 23 of those points, and the same route at the cell **midpoint** falls 0.7117 % *below* threshold — so the margin exists only by virtue of the sup-over-closed-cell quantifier and the left-endpoint evaluation. |
| 6 | the R-stage premise is not available; guard stays DENY | **Binding, and uncontested.** C4 asserted no R-stage consequence at any point; the certificate emits the gate's PARTIAL `permitted_conclusions` verbatim, including "no R-stage consequence of any kind". |
| 7 | the next successor should cost four mechanisms, in the adjudicator's order | **Recorded as C4-N7** below, in its order, which supersedes C4-N1's ordering. |
| 8 | no coverage map revision; r5 remains authoritative | **Binding, and already satisfied.** No r6 exists; Phase 0 check 5 verifies it; the m = 5 open set is unchanged at {306, 307, 308, 309}. |
| 9 | carry C3's conditions forward unchanged | **Binding.** In particular the K5 tail adoption floor with the C2 adjudicator's N9-lapse condition on F1, the prohibition on citing `C3_BLOCKER_ANALYSIS.md` §3, and C3's N9/N10. None was in C4's scope and none is discharged. |
| 10 | correct erratum E3's framing | **Done: `ERRATUM_C4_GATE.md`, "E3 correction".** The class is `PARTIAL` with or without the carve-out, so it cannot have been outcome-fitting in the decisive sense. |
| 11 | hygiene: the README advertised a non-existent freeze record; check `1_branch_head_clean` does not test cleanliness; the zero-counters are constants | **README fixed** (it now names the gate sha and freeze commit directly, and the empty directory is gone). The check name and the counters are carried forward as **C4-N8** and **C4-N4** rather than retrofitted into adjudicated artifacts. |

## Further notes carried to a successor

* **C4-N6.** `c4_certificate.evaluate` records `licence` but never consults it: a re-run on inputs where the
  TC-T/K5-B intersection went empty at the bound would still emit `excluded: true`. And the monotonicity ladder
  varies `A0` only, so "A1 = A2 = 0 is the most generous setting" is unexercised in C4's own machinery. Both hold
  today. A successor must make the guard refuse rather than report, and must ladder `A1` and `A2` too.
* **C4-N7.** The adjudicator's ordering for the next deterministic successor, which supersedes C4-N1's:
  **(a)** a residual-specific, non-norm-only order-0 bound — `(Ghat|phi|)(a)/D_e` in place of `A0 ||phi||` — the
  only named mechanism that escapes the `E_a[tau]` floor outright, and quantified by no one;
  **(b)** tightening the candidate sup norms feeding the order-3 surrogate `resG`, which the adjudicator's
  sensitivity probe shows is the *dominant* channel at cell 309 — halving them raises the critical `A0` to 4.160,
  above both C4's certified bound and the Monte-Carlo truth, i.e. the cell would become closable under the
  knockout;
  **(c)** cell-width refinement at 309 (halving `rho` raises the critical `A0` to 7.534);
  **(d)** cell 307's target: 2.203053× on `(A1, A2)` with `A0` unchanged, or 1.111966× uniform.
  C4-N1's routes R1 and R5 remain the right starting point for a *sharper floor*, but a sharper floor is no longer
  the highest-value work.
* **C4-N8.** Phase 0's check `1_branch_head_clean` tests the branch name and ancestry but not tree cleanliness,
  and the committed run records `uncommitted_files_at_audit: 12` while returning true. Rename or repair it.
* **C4-N9.** The order-0 atom-constant channel C4 closed at cell 309 is **not** the dominant channel there. The
  adjudicator's single-knob probe: a 10 % cut in the order-0/1/2 residuals moves the critical `A0` by 0.014 %,
  while halving the candidate sup norms moves it by 29 % and halving `rho` moves it by 134 %. Any successor
  reading C4 as "the operator direction is spent at 309" is misreading it.
