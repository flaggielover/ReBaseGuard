# C11RD N9 adjudication review
ADJUDICATION_ACCEPTED

| item | value |
|---|---|
| reviewer | fresh, independent, read-only adjudication reviewer (Claude Opus 5.5 subagent). I had no part in C11, C11R or C11RD. |
| date | 2026-09-26 |
| worktree | /Users/suzhe/ReBaseGuard-k5c11rd (linked; common dir /Users/suzhe/ReBaseGuard/.git), branch p5y-k5-tail-c11rd-d1d2-extension |
| HEAD | 7d67989d3da6595180ca3c01d34f2bdf4543ae73 (the adjudication commit, which adds only `adjudication/ADJUDICATION_C11RD_N9.md`) |
| subject | `level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/adjudication/ADJUDICATION_C11RD_N9.md`, verdict line `N9_CLOSED` |
| read-only | `GIT_OPTIONAL_LOCKS=0 git status --porcelain --ignored --untracked-files=all` printed 0 lines before and after every step. I wrote nothing except this directory. No runner, launcher, comparator main, qualification or authorization tool, or C11/C11R producer was run. No frozen module was imported. |
| magnitudes | This review states classes, statuses, ratios and hashes only. It contains no D1/D2 magnitude, independent or original. |

## Summary

I rebuilt the frozen N9 definition and its closure conditions from the frozen records, without relying on the adjudication:

* the C2 adjudication, line 501 and section K;
* the C11R gate `config/N9R_GATE_C11R.json`: SCOPE, target, precedence and forbidden_conclusions;
* the C11R statement table, blob 58b4066f: N9_wording, DEPENDENCY_FINDING, original_statements and comparison_semantics_frozen_before_results;
* the C11RD freeze `protocol/C11RD_FREEZE_R1.json`: sections A, B, C, D, F, L, Q, R, S, T, U, FORBIDDEN and governance_at_freeze.

I then checked every condition against the evidence. Where a recomputation was possible, I did it with pure Fraction code that I wrote myself.

**Result.** Every frozen condition for N9 closure holds:

* all six constants for cell 306 are covered, on the frozen block [680769/400000, 17885921/10000000];
* each statement is EQUIVALENT or STRONGER than the original;
* each class is AGREES or STRONGER under the factor-2 rule, which was frozen before any result;
* there is no independence violation, no DISAGREES and no INVALID;
* each execution and each comparison happened exactly once, and each was accepted by its review.

**What the adjudication gets right.**

* It identifies the missing requirement after C11R correctly: an independent, statement-equivalent D1/D2.
* It shows that C11RD supplied exactly that requirement and changed nothing else about N9.
* It keeps the historical C11 and C11R verdicts intact.
* It separates the five layers.
* It reaches its verdict from the frozen conditions, not from the comparator's token.
* Its K5 section does not claim K5 closure, adoption, a floor replacement or an applied F1 lapse.
* It contains no D1/D2 magnitude.

The verdict N9_CLOSED is correct and properly grounded. I found no blocker. The non-blocking notes below are points of precision or completeness only.

## Reconstruction of the frozen N9 definition (independent of the adjudication)

* **Wording.** Source: C2_ADJUDICATION.md:501. *"a second, independently written certifier reproducing the six operator constants for cell 306 (closing N9)"*. C11R's statement table (blob 58b4066f) freezes it verbatim, with `constant_count` 6 and `target_cell` 306. The six constants are C_T, tau, Abar, D_lo, D1 and D2 (C2 Condition 3; gate `target.constants`).
* **Closure criterion.** C11R gate `SCOPE.N9_closure_requires`: *"all six constants for cell 306 classified AGREES or STRONGER, each with an EQUIVALENT or STRONGER statement"*. The gate adds that if D1 and D2 are not independently certified, N9 remains OPEN. Its `SCOPE.D1_D2` says *"a later prospective derivative-system extension would be needed"*.
* **Agreement rule.** From the statement table, frozen before any result:
  * factor 2;
  * UPPER_BOUND: STRONGER if independent <= original; AGREES if original < independent <= 2·original; otherwise INSUFFICIENT;
  * LOWER_BOUND: the mirror image;
  * *"SAME STATEMENT BEFORE SAME NUMBER"*.

  C11RD freeze L restates this rule as UNCHANGED. It also makes an independent value exactly equal to the original INVALID.
* **Independence.**
  * Gate G9: nothing may import or replay the original's load-bearing graph or its backend.
  * DEPENDENCY_FINDING: D_lo, D1 and D2 are conditional on C_T and tau. The independent line must certify its own C_T and tau via Khat_e and propagate with those, never with the original's.
  * The gate forbids "the original's C_T or tau as a premise".
* **Precedence.** INDEPENDENCE_VIOLATION > SCIENTIFIC_DISAGREEMENT > EXECUTION_INVALID > N9_CLOSED > AGREEMENT_INSUFFICIENT. The gate's `N9_classification_precedence` and C11RD freeze L.n9 give the same order, and so does the comparison artifact's `precedence` (checked by equality).
* **Reassembly.** C11RD freeze `L_agreement_criterion.n9`, frozen at ce5b8595 before any target magnitude:
  * N9_CLOSED iff all six are AGREES or STRONGER;
  * C_T, tau, Abar and D_lo are read from C11R's accepted comparison and not recomputed;
  * D1 and D2 come from C11RD.

  FORBIDDEN includes "recomputing or replacing C_T, tau, Abar or D_lo".

## Findings per item

### 1. Why N9 stayed OPEN after C11 and after C11R — CONFIRMED
* **C11.** Sources: `evidence/n9/C11_N9_RESULT.json` (schema /2, `N9_VERDICT` EXECUTION_INVALID, `N9_STATUS_AFTER_C11` OPEN), `WHAT_BLOCKS_CLOSURE` and `verdict_reasons`. Two reasons:
  1. STATEMENT: the certifier used a scalar drift, while the original's statement is block-uniform.
  2. SCOPE: it covered cell 307 and one constant (Abar), where N9 is worded about cell 306 and six constants, and it had no Khat_e.

  `review/ADJUDICATION_C11.md` adds the first-draft defects: the wrong comparator constant and the abandoned blinded comparison.
* **C11R.**
  * The comparison (blob 5269c2aa) gives C_T AGREES/EQUIVALENT, tau AGREES/EQUIVALENT, Abar STRONGER/EQUIVALENT, D_lo AGREES with a STRONGER statement (premises FEWER), and D1 and D2 INSUFFICIENT with NO_INDEPENDENT_STATEMENT (NOT_IMPLEMENTED).
  * The frozen class is AGREEMENT_INSUFFICIENT. The adjudication (118008f5) gives N9_REMAINS_OPEN, citing the gate clause on D1/D2.
  * The review at 7375b9cd ends `VERDICT: COMPARISON_ACCEPTED` and agrees with N9_REMAINS_OPEN.
  * So the single missing requirement after C11R was an independent, statement-equivalent D1 and D2 for cell 306 on the frozen block, agreeing under the factor-2 rule.
* The adjudication states both reasons correctly in section 3, item 1. See note N4 on its layer-A wording.

### 2. C11RD addresses exactly that requirement and changes nothing in N9 — CONFIRMED
* **Target.**
  * Freeze Q_target is "cell 306 only". The grant scope is "cell 306, D1 and D2 only". The runs artifact has cell 306 and targets D1 and D2 only.
  * The four sub-blocks tile [680769/400000, 17885921/10000000] exactly. I checked this with Fractions, and it equals freeze D and C11R's `drift_domain`.
* **Statements.**
  * Freeze A/B `record` equals C11R's `original_statements.D1/D2` on all seven exact fields: constant, quantity, kernel, convention, direction, state_set and proposition. The runs artifact's target statements also equal both, field by field (my own script).
  * Direction is UPPER_BOUND in the table, the freeze and the artifact.
  * Constant count: SIX = C11R's six.
  * Factor: read from C11R's table, and equal to 2.
  * Precedence: identical, as above.
* **Unchanged records.**
  * The C11R gate (blob 5fb8fb26), statement table (58b4066f), schema (0526426c), quarantine (219e0122) and comparison (5269c2aa) are identical at 2c24a989, 118008f5, 7375b9cd and HEAD.
  * `git diff 7375b9cd HEAD` touches no file outside the C11RD namespace.
* C11RD's route `independent_derivative_propagation` was already frozen in C11R's own schema (`ROUTE_REQUIRED_DEPENDENCIES` = {C_T_independent, tau_independent}; `ROUTE_CAN_PRODUCE` ⊇ {D1, D2}). C11RD is therefore the "later prospective derivative-system extension" the gate names. It is not a redefinition.

### 3. C11R's C_T, tau, Abar and D_lo evidence is still valid, unchanged and in scope — CONFIRMED
* **Blobs.**
  * C11R comparison: 5269c2aa.
  * Sealed runs: a5351603, equal at the seal 5ff4cc5b, at 7375b9cd and at HEAD.
  * Each file has exactly one introducing commit in all history: 2c24a989 and 5ff4cc5b.
* **Reviews.**
  * REVIEW_C11R_EXECUTION.md ends `VERDICT: EXECUTION_ACCEPTED` (22537709).
  * REVIEW_C11R_COMPARISON.md ends `VERDICT: COMPARISON_ACCEPTED` (7375b9cd), with no blockers.
* **No later change.** The C11R, C11, C2 and C10 namespaces each have 0 changed files since 7375b9cd.
* **Scope.**
  * All four statements are single whole-block certificates on the EQUAL domain. The comparison recorded no independence violation, no refusal and no opposite-direction pair.
  * C11RD's comparator reads these classes blob-bound (`classes_source`) and does not recompute them. This is what freeze L.n9 and FORBIDDEN require.

### 4. D1/D2 statements are EQUIVALENT before any number is compared — CONFIRMED
* I reimplemented C11R's frozen semantics myself:
  * `c11r_equiv.compare` / `check_internal`, using the `c11r_schema` constants, which I read in source;
  * exact-field equality;
  * the drift domain as exact rationals;
  * premises normalised by the `_independent` suffix.
* Result, for both D1 and D2: no field mismatch, domain EQUAL, and premises SAME ({C_T_independent, tau_independent} → {C_T, tau}).
* The internal checks all pass:
  * kernel Khat_e with the atom_removed convention;
  * aggregation max_over_sub_blocks, which is valid for UPPER_BOUND;
  * an independent route;
  * producer `c11rd_runs.py`, with its file_sha256 equal to the freeze's;
  * the route can produce D1 and D2;
  * the required dependencies are present;
  * no original constant is a dependency.
* The status is therefore EQUIVALENT, which equals the artifact's `statement` entries.
* The aggregation differs from the original's (4 sub-blocks against 9, both max). C11R's semantics treat aggregation as non-propositional, in the same way C11R accepted whole-block certificates against the 9-sub-block originals.
* Ordering: the comparator runs U4 (statements) before U5 (the originals are loaded). The comparison review confirmed the frozen `compare_statement` output and a separate implementation.

### 5. The factor-2 rule for D1 and D2 — CONFIRMED by my own recomputation
* **Blob check first.** The quarantine is blob 219e0122a7febf4347ce9205e5e5ed9f18b20ffb, by `git hash-object` on disk and at HEAD. Its last change is dbd6cd89 (C11R pre-result), before the C11R run.
* **Originals.** `original_value` equals the quarantine `magnitudes.D1/D2.value` exactly as Fractions, for both. The quarantine float fields are consistent.
* **Recomputed classification**, with Fractions:

  | target | positive | independent vs original | not equal | class | ratio (exact equals artifact; float bit-identical) |
  |---|---|---|---|---|---|
  | D1 | yes | ≤ | yes | STRONGER | 0.45362884480385873 |
  | D2 | yes | ≤ | yes | STRONGER | 0.0557333083728129 |

  Both classes match the artifact's `CLASS` and `numeric.class`.
* **Consistency with the sealed runs.** The independent value equals `targets.Dk.value`, `execution.Dk` and the maximum over the four sub-block `Dk` fields of the sealed runs artifact, which is status CERTIFIED.
* **DISAGREES.** Not reachable for a same-direction UPPER_BOUND pair, as freeze L states.

### 6. All six constants meet the frozen N9 criterion — CONFIRMED
My own reassembly script reads C11R's per-target records and C11RD's per-target records:

| constant | class | statement |
|---|---|---|
| C_T | AGREES | EQUIVALENT |
| tau | AGREES | EQUIVALENT |
| Abar | STRONGER | EQUIVALENT |
| D_lo | AGREES | STRONGER |
| D1 | STRONGER | EQUIVALENT |
| D2 | STRONGER | EQUIVALENT |

There are no independence violations in either comparison, no DISAGREES and no INVALID. By the frozen precedence the result is N9_CLOSED. This equals the artifact's `classes` and its `N9_VERDICT`, but I derived it from the frozen conditions, not from those fields.

### 7. Independence — CONFIRMED (see notes N1 and N3)
* **C11R.** No original load-bearing graph, and certificate premises are empty (C11R adjudication Q1; comparison review item 19).
* **C11RD production path.**
  * By static import scan, the modules are c11rd_runs → c11rd_certify, c11rd_float, c11rd_kernel, c11rd_model and c11rd_tm, plus C7's `c7_gaussian`. `c7_gaussian` imports only `fractions`; its sha256 is bd73b5b4…, equal to the binding.
  * There are no imports of taboo_certify, resolvent_certificate, opnorms, ra_certifier, fast_range, intervals, rebaseguard_certify, rung3_engine, spec, numpy or flint.
  * No production module names REGISTRY_C2, the quarantine, the C11R comparison or the original namespace.
  * `c11_certifier` is imported only inside `c11rd_validate.py` (V03).
* **Premise.**
  * D1/D2 are propagated from C11R's F_H certificate: sealed blob a5351603; input digest 913fa6aa equal to C11R's F_H; Khat_e; atom_removed; whole block; no premises.
  * The frozen loader `c11rd_model.c11r_fh_premise` checks certified, Khat_e, the block, A > 0, B >= 0 and a positive margin. It sets C_T = tau = A = sup_R w. The runs records declare `DEPENDENCY_ON_ACCEPTED_C11R_CERTIFICATE`.
  * The original's C_T/tau are never used. This is exactly what DEPENDENCY_FINDING requires. See note N1 on the exact C_T value.
* **Disclosed prior knowledge.** The author had seen the two original D1/D2 values (C11R Phase 15; `docs/C11RD_INDEPENDENCE_AUDIT.md`), and read REGISTRY_C2 for structural facts. This compromises nothing that N9 or the frozen rule tests:
  * No design choice references the values. Calibration used only the non-target blocks NT = [5/2, …] and LOW = [1, …]. The rehearsals run in `nontarget` mode on [5/2, 3233337/1250000].
  * Everything load-bearing was frozen before the target run: the rule, the partition, the tolerances and the aggregation.
  * The values appear in no pre-comparison file: V18, U7 with 42 files and 0 hits, and the pre-execution, qualification and comparison reviewers' own scans.
  * A certified upper bound's truth does not depend on its author's knowledge.
  * Both classes sit far from any threshold, so there is no borderline to steer toward.

  The pre-execution reviews (N-8) and the qualification review (N-10) examined the disclosure and found it honest.

### 8. Exactly once — CONFIRMED
* **Execution.**
  * One consumed ref: `refs/c11rd/r1-execution-consumed` → 4b716d43 (G).
  * The launch journal has 5 events: preflight_pass, consumed, runner_starting, runner_exited with exit 0, and seal_attempt 1 with COMPLETED_CERTIFIED.
  * There is one lock. The runner log shows one start and the artifact being written.
  * The runs file, grant, lock and comparison each appear in exactly one commit across `git log --all --reflog`: 4547bcd4, 4b716d43, 4547bcd4 and 8e2defab respectively.
* **Comparison.**
  * Commit 8e2defab adds only the artifact. File sha256 8a9637b6…; embedded body sha256 f69c2bf0….
  * The comparison review verified exclusive create, U0 now refusing, and one invocation. Note N7 covers the invocation record.

### 9. Reviews — CONFIRMED
Each C11RD review has exactly one whole-line verdict, on line 2, and each is preserved in its own commit:

| review | verdict | commit |
|---|---|---|
| R1 pre-execution | READY_TO_QUALIFY | 3c1eff11 |
| R1Q-R1 qualification | QUALIFICATION_ACCEPTED | e27c2ffd |
| authorization | AUTHORIZATION_ACCEPTED | e320d8f5 |
| execution | EXECUTION_ACCEPTED | db1c6118 |
| comparison | COMPARISON_ACCEPTED | 90265349 |

* The historical NOT_READY (663f8fe7, first freeze 71495747) and QUALIFICATION_REJECTED (89330534) were repaired prospectively, before any execution: the successor freeze ce5b8595 and qualification e627d4ec.
* The execution, comparison, authorization and qualification reviews each report "none" under BLOCKERS.
* C11R's execution and comparison reviews are accepted (item 3).

### 10. Temporal integrity, provenance, freeze, authorization, sealing, leakage and scope — CONFIRMED, no violation
* **Temporal.**
  * History is linear from 7375b9cd to HEAD, each commit the single parent of the next.
  * The freeze ce5b8595 (2026-09-25 16:41Z) declares `FROZEN_BEFORE_ANY_TARGET_MAGNITUDE`, and `governance_at_freeze` has target_D1/D2_computed false.
  * Grant G at 11:17:27Z → runner 11:29:21–11:55:01Z → seal 11:55:02Z → execution review 12:28Z → comparison 12:34Z → comparison review 13:21Z → adjudication 13:39Z (all 2026-09-26).
* **Freeze and provenance.**
  * `git diff ce5b8595 HEAD` shows only additions (A). No code, protocol or theory file changed.
  * All 8 code files on disk match the freeze and the runs `code_sha256`. All 8 `document_sha256` entries match.
  * All 8 `input_bindings` blobs at HEAD equal the freeze.
* **Authorization.** A 6bab71b9 → R e320d8f5 → G 4b716d43 (the grant adds only `config/C11RD_GRANT.json`, decision ALLOW, scope cell 306 D1/D2) → the launch at HEAD == G, per the journal and lock.
* **Sealing.** The seal adds exactly the four `evidence/runs/` files on top of G.
* **Leakage.** V18, U7 and the post-write scans are clean. My own scan of the adjudication document found none of either value's renderings (3–30 significant digits, truncated and rounded, including scientific notation) and no exact rational or numerator. Its only decimal tokens are the two ratios.
* **Scope.** Nothing outside the C11RD namespace has changed since 7375b9cd. local main c123b9bb and origin/main 1cb45382 are unchanged.

### 11. Cells 307–309 — CONFIRMED never executed
* The grant, lock, runs artifact and journal name cell 306 and its block only.
* No file outside the C11RD namespace changed. No changed path concerns 307, 308 or 309.
* Freeze R and FORBIDDEN prohibit it.

### 12. No adoption and no r6 — CONFIRMED
* `p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json` is blob f978eeb6 at 7375b9cd, ce5b8595, 4547bcd4, 8e2defab and HEAD. Its last change is ae4cbc2c (C2).
* There is no K5 coverage map r6 anywhere in history. The only "r6" paths belong to the unrelated p5x `compute_optimization_r6`.
* No adoption or coverage file has changed since 7375b9cd.

### 13. Historical verdicts are immutable — CONFIRMED
* The C11 namespace is identical to C11's final tip 440bcd91, which is an ancestor of HEAD. `C11_N9_RESULT.json` still says EXECUTION_INVALID, N9 OPEN.
* C11R's comparison (AGREEMENT_INSUFFICIENT) and adjudication (N9_REMAINS_OPEN) are byte-identical since 7375b9cd.
* The adjudication commit adds one new file and edits none.

### 14. No retroactive change — CONFIRMED
* The adjudication attributes closure to the LATER successor evidence, combined with C11R's four classes exactly as C11RD's freeze prescribed before any target magnitude.
* It states that neither C11 nor C11R closed N9 on its own evidence, and it re-labels neither.
* C11R's gate lists "that C11 is rewritten as success" as a forbidden conclusion. That remains respected.

### Extra judgements
* **Five layers.** The section 2 table separates the historical C11 record, the historical C11R record, the C11RD evidence, the mechanical comparator result (8e2defab / 90265349) and the authoritative adjudication. The content of each row matches the records.
* **Verdict grounding.** Section 4 derives N9_CLOSED from the frozen conditions: six constants, statements, classes, independence, precedence, exactly-once and acceptance. It says expressly that it does not copy the comparator's `N9_VERDICT`. My reconstruction reaches the same verdict without using that field.
* **K5 section.**
  * It states that K5 remains PARTIAL, that r5 remains authoritative, that there is no r6 and no adoption, and that cells 306–309 remain open in r5.
  * It states that N9 is a trust condition and not a cell-closure criterion.
  * It declines to apply F1's lapse to any cell and declines to freeze, replace or apply any floor.
  * It quotes C2's F1 lapse sentence verbatim, with a correct ellipsis, and names the freeze-before-recompute replacement route (C2 Condition 1) that C10 described as gated on N9.
  * It asserts none of the conclusions in C11R's `forbidden_conclusions`: no cell closed or adopted, no "F1 has lapsed", no "floor may be replaced", no r6.
  * The content is accurate. Note N5 covers a citation imprecision.
* **No magnitude.** Confirmed by the scan in item 10.

## BLOCKERS

none

## NON-BLOCKING NOTES

* **N1 — the exact C_T used in the propagation.**
  * C11RD uses C_T = tau = A = 3429/500. This is the exact supremum on R of the F_H weight w = A − B·m, with B ≥ 0 and m ≥ 0. The frozen loader checks it, and freeze F.premise and theory Lemma 3 state it before any target run.
  * C11R's accepted target record for C_T is an outward-rounded upper bound. It exceeds A by about 3.7e-97.
  * The value used is therefore the mathematically exact bound implied by the same accepted certificate. It is not C11R's C_T target field verbatim.
  * This is sound and prospectively frozen, and the effect is negligible: it cannot move either class at ratios 0.4536 and 0.0557.
  * The adjudication's "propagated from C11R's independently certified C_T = tau" is accurate at the certificate level. It could have said that C_T is taken as sup_R w of F_H.
* **N2 — what the comparison cannot detect in the STRONGER direction.**
  * For UPPER_BOUND pairs, an unsound independent certifier would also show up as STRONGER. D2's ratio of about 0.056 is a large gap.
  * The adjudication's item 5 remark ("a markedly stronger independent upper bound implies the original's statement") is true under soundness, but it is one-sided.
  * Soundness rests on other evidence, not on the comparison: the R1 pre-execution review of the theory and code (B-1 repair, Proposition 1, Theorem 5), validation 29/29, and the reviewers' exact recomputation of the propagation from the recorded residual bounds.
  * The frozen rule deliberately counts STRONGER as agreement, so this is not an unmet condition.
* **N3 — authorship independence is not restated.**
  * The C11 adjudication and C11R comparison review N2 both recorded that "independently written" is met in the frozen C11R sense (a disjoint load-bearing graph and no consumed original outputs), not as organisational or authorship independence.
  * C11RD has the same author lineage, and that author had seen the original values.
  * The adjudication scopes its disclosure conclusion to "independence of implementation or the certificates", which is correct, but it does not repeat this standing qualification.
* **N4 — layer-A wording.** Layer A lists "wrong constant" and "no blinded comparison" among the reasons C11's comparison was void.
  * C11's final record (C11_N9_RESULT/2) says N6 is satisfied once the comparator is corrected, and that the verdict does not lean on C11-N10. It rests on STATEMENT (scalar drift) and SCOPE (cell 307, one constant, no Khat_e).
  * Those two items are defects that the C11 adjudication found in the first draft.
  * Section 3 item 1 states the reason precisely, so nothing turns on this.
* **N5 — citation merge in section 5.**
  * The phrase "a replacement floor requiring agreement between two independent certifier implementations" comes from C2 section K (the "What will:" list at line ~501–502).
  * C2 Condition 1 supplies the freeze-before-recompute precondition.
  * C10 treats the two-certifier sentence as corroborating, one of three routes for cell 306, with Condition 1 as the primary authority.
  * The parenthetical "(C2 verdict Condition 1; C10)" merges these sources. The substance is accurate.
  * The section also leaves the floor's current state implicit: the C2 floor remains the standard until a replacement is frozen, and C2's stated F1 lapse condition is textually met. The adjudication rightly leaves every application to the separate governance step. This is conservative and not an overstep.
* **N6 — the chain summary omits the first freeze.** It does not mention the predecessor freeze 71495747 or its NOT_READY review 663f8fe7. Both are historical, recorded in freeze R1 `successor_of`, and repaired before qualification.
* **N7 — "one comparator invocation" partly rests on an external log.** The git-level exactly-once is verified: one commit in all refs and reflogs, and U0 now refuses. The invocation count itself partly rests on an invocation log outside the repository (comparison review note 3).
* **N8 — self-adjudication.** The adjudicator is the campaign author, as in C11R. This review supplies the independent check.
* **N9 — inferable magnitudes.** The adjudication's ratios, combined with the originals published in the historical C11R adjudication, would let a reader infer the independent magnitudes. Ratios are expressly permitted, and the comparison artifact holds the values anyway. This does not breach the no-magnitude rule.

## Commands I ran (all read-only)

Python was always `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -I -S -B`, run from the scratch directory `/private/tmp/claude-501/-Users-suzhe-ReBaseGuard/ea6191ae-93b1-4f9c-b9ba-6cd0430d32ee/scratchpad/c11rd_adj_review`. No frozen module was imported.

**Git state and history**
* `GIT_OPTIONAL_LOCKS=0 git status --porcelain --ignored --untracked-files=all | wc -l`: 0 at the start, in between and at the end.
* `git rev-parse HEAD`; `git branch --show-current`; `git log --oneline -25`.
* `git log --reverse --format='%H %P %ad %s' 7375b9cd..HEAD`, plus `git show --name-status` for each commit in the C11RD lineage.
* Change checks:
  * `git diff --name-only 7375b9cd HEAD` for the C11R, C11, C2 and C10 namespaces and for everything outside the C11RD namespace;
  * `git diff --name-only ce5b8595 HEAD` for code, protocol, theory and docs, and `--name-status ce5b8595 HEAD`;
  * `git diff --name-only 440bcd91 HEAD` for C11, and `git merge-base --is-ancestor 440bcd91 HEAD`.
* Blob checks with `git rev-parse <commit>:<path>`:
  * C11R comparison, runs, quarantine, table and gate at 2c24a989, 7375b9cd, 118008f5 and HEAD;
  * the runs file at 5ff4cc5b;
  * r5 at 7375b9cd, ce5b8595, 4547bcd4, 8e2defab and HEAD.
* `git hash-object` of the quarantine on disk.
* `git log --all [--reflog] --format=... -- <path>` for the key C11R files and for the C11RD comparison, runs, grant, lock and adjudication.
* `git for-each-ref` (c11rd refs); `git worktree list`; `git rev-parse refs/heads/main refs/remotes/origin/main`; `git ls-tree -r HEAD --name-only | grep COVERAGE_MAP`; `git log --all --name-only | grep -i R6`.

**Reading**
* `cat` / `sed` / `grep` of:
  * the adjudication;
  * the C2 adjudication (lines 395–608) and OPEN_NOTES_DISPOSITION_C2 (N9);
  * the C10 README (Q2 and Consequences);
  * the C11 README and review/ADJUDICATION_C11.md;
  * the C11R adjudication and the C11R review verdict lines;
  * REVIEW_C11R_COMPARISON.md (the conclusion);
  * C11RD reviews: the verdict lines of all seven, the comparison review in full, and the execution review summary, blockers and notes;
  * the R1 pre-execution review head and its independence item;
  * the R1Q-R1 qualification review notes;
  * `docs/C11RD_INDEPENDENCE_AUDIT.md` and qualification doc section 8;
  * `c11rd_compare.py` lines 1–230 and `c11rd_model.c11r_fh_premise` / `kernel_norms`;
  * `c11r_equiv.py` lines 60–162 and `c11r_schema.py` lines 40–100;
  * the C11RD launch journal, lock and execution log, with value masking.
* Import and name scans (`grep`) of all C11RD code modules and C7 `c7_gaussian.py`; `shasum -a 256` of `c7_gaussian.py` and the comparison artifact.

**My own scripts** (pure Fraction/Decimal on recorded strings; no numbers printed except classes, ratios, booleans and hashes)
* `walk.py` / `mwalk.py`: structure dumps with value masking.
* `reclass.py`: the factor-2 reclassification, originals against the quarantine, and exact ratio equality.
* `agg.py`: the block tiling and max-aggregation identities.
* `stmt.py`: field-by-field statement equivalence.
* `n9.py`: the six-constant reassembly under the frozen precedence.
* `leak.py`: a magnitude-rendering scan of the adjudication.
* Inline `-c` checks for the C11R F_H certificate against the C11RD premise, C11 `verdict_reasons`, freeze sections, input bindings at HEAD, and code and document hashes.
