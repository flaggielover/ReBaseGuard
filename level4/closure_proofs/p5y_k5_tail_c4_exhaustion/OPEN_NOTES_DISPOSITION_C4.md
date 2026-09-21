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
