# K5 tail adoption floor r2 — independent review
REPLACEMENT_FLOOR_ACCEPTED

| item | value |
|---|---|
| reviewer | fresh, independent, read-only reviewer (Claude Opus 5.5 subagent). I had no part in C2, C10, C11, C11R, C11RD or floor r2. |
| date | 2026-09-27 |
| worktree | /Users/suzhe/ReBaseGuard-k5c11rd, branch p5y-k5-tail-c11rd-d1d2-extension |
| reviewed commit | a15d083b009868e38a5bd5a808f38f19e6ab4b92 (parent fb237288a7cf481c14cd2f85c18bb363d2ebe44a) |
| subject | level4/closure_proofs/p5y_k5_tail_floor_r2/ (FLOOR_R2_SPECIFICATION.md, config/K5_TAIL_ADOPTION_FLOOR_R2.json, config/CELL306_ADOPTION_GATE_R2.json, code/floor_r2_build.py, code/floor_r2_verify.py, evidence/FLOOR_R2_VERIFY.json) |
| magnitudes | This review contains no D1/D2 value (original or independent), no D1/D2 ratio, and no Γ, atom constant, uniform-A margin or F2 value for any supply containing a C11R or C11RD constant. |

Line references are to the files at a15d083b. "SPEC" = FLOOR_R2_SPECIFICATION.md, "RULE" =
config/K5_TAIL_ADOPTION_FLOOR_R2.json, "GATE" = config/CELL306_ADOPTION_GATE_R2.json, "C2A" =
p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md, "C2N" = p5y_k5_tail_c2_closure/phase_d/CELL_306_ADOPTION.md,
"C10R"/"C10J" = C10 README.md / evidence/phase5/C10_GOVERNANCE.json, "ADJ"/"ADJR" = the C11RD N9 adjudication and its review.

## Commands I ran (all read-only)

* `git status --short`, `git rev-parse HEAD`, `git log --oneline -8`, `git show --stat a15d083b`,
  `git diff --name-only fb237288 a15d083b` (6 paths, all in the namespace).
* `cat -n` / Read of every namespace file; Read/`sed -n` of C2A (lines 1-84, 418-608), C2N (whole), C10R (53-148),
  THEOREM_AD.md §4 and §8, deflated_consume.py (40-109), c2_d5_forecast.py (whole), tail_forecast_r2.py (imports),
  tct_rule.py (`atom_constants_generic`), THEOREM_TCT.md headings, ADJ (text lines excluding the ratio row), ADJR
  (header, item 7, extra judgements, N1-N9), C11RD reviews' verdict lines and scope sections.
* python3.14 -I -S -B one-liners that print only keys, classes, statuses, statements and booleans from:
  C10_GOVERNANCE.json (Q2 sections), C11R_N9_STATEMENTS.json (comparison semantics, DEPENDENCY_FINDING, N9_wording,
  drift_domain, original_certifier, provenance), N9R_GATE_C11R.json (SCOPE, forbidden_conclusions, comparison_rule),
  C11RD_FREEZE_R1.json (F_derivative_recurrence, L_agreement_criterion, FORBIDDEN), C11R_COMPARISON.json (field
  structure, CLASS/direction/status/statement per target), C11RD_COMPARISON.json (field structure, CLASS, and
  booleans only), REGISTRY_C1.json (top-level provenance keys and block key names only), the C11RD validation
  evidence (test names and pass flags), K5_COVERAGE_MAP_R5.json (non-numeric keys).
* Boolean-only checks (no value printed): C11RD `per_target[k].independent_value` == `C11RD_RUNS.json targets[k].value`
  for D1 and D2; C11RD_RUNS sha256 prefix; C11R C_T record lies above the exact supremum A by between 1e-98 and 1e-96;
  C11R's C_T, tau, Abar, D_lo records satisfy the consumer precondition (C >= tau, tau >= 1, Abar >= 1, D_lo > 0).
* `git rev-parse <rev>:<path>` for every bound blob at HEAD and at fb237288 (all equal; REGISTRY_C2.json and
  C2_D5_FORECAST.json were checked by blob id only and never opened); `git show HEAD:<REGISTRY_C1> | shasum -a 256`
  and `git show HEAD:<deflated_consume.py> | shasum -a 256` (equal to c2_d5_forecast's pins `C1_REG_SHA` and `DC_SHA`).
* `git merge-base --is-ancestor` and `git log -1 --format=%s` for the 16 cited commits; `git for-each-ref`, `git reflog`
  (no rewritten commits; only this branch contains fb237288); `git ls-tree -r --name-only HEAD` and
  `git log --all -- '*K5_COVERAGE_MAP_R6*'` (no r6); `git rev-parse refs/c11rd/r1-execution-consumed` (= 4b716d43...).
* An AST scan of the module-level statements of c11rd_runs.py, c11rd_launch.py, c11rd_validate.py and c11rd_compare.py
  (imported by the verifier) to confirm no import-time side effect beyond a read-only flag barrier.
* The verifier, as instructed:
  `cd level4/closure_proofs/p5y_k5_tail_floor_r2/code && python3.14 -I -S -B floor_r2_verify.py --out <scratch>/floor_r2_review/VERIFY_RERUN.json`
  -> `FLOOR_R2_VERIFY PASS (19/19)`, exit 0. The rerun's `checks` and `information` are identical to the committed
  evidence; its HEAD is a15d083b (the committed evidence records fb237288, see note N12); verifier sha256 fc17bd99... equal.
* The build script imported (not run as `__main__`) with python3.14 -I -S -B; `json.dumps(sealed(RULE|GATE))`
  is byte-identical to both committed JSONs, and both self-hashes verify.
* `git status --porcelain --ignored --untracked-files=all` before and after every executing step: 0 lines; no
  `__pycache__` anywhere in the worktree.
* A κ sanity check with floats: sqrt(2/π) < 0.7978846 and 4φ(1) < 0.9678830 (both true).
* A final leak scan of this review file with the frozen C11RD machinery (`_broad_hashed_scan` against
  `ORIGINAL_PATTERN_SHA256` and an in-memory independent-value hash set, built exactly as floor_r2_verify.py builds it,
  never printed): 0 hits for both sets.

I did not run c2_d5_forecast.py, deflated_consume, tct_rule, tail_forecast_r2, any certifier, runner, comparator,
launcher or qualification main, and did not open C11R's quarantine, REGISTRY_C2.json or C2_D5_FORECAST.json.

## Q1 — Audit accuracy

All sixteen italic quotations in SPEC were extracted and located independently of the verifier, each piece in its
attributed source (my own per-source lookup, not the verifier's union lookup):

* **(a) Old floor and F1.** SPEC:21 quotes the base clause, F1 and F2 of r1. Source C2A:427-436 — verbatim (F1 elided
  after "Lemma G", correctly marked). RULE:87 and RULE:99 restate the base and F2; F2 is verbatim.
* **(b) Lapse condition.** SPEC:22 = C2A:432-433 verbatim ("This limb is available for as long as **N9** (no second,
  independently written certifier of the operator constants) remains open, and lapses when N9 is closed."). RULE:59
  uses the same sentence with a correct ellipsis.
* **(c) What N9 closure unlocks.** SPEC:23 = C2A:501-503 verbatim, correctly placed as the first of three discharge
  routes for cell 306 (C2A:499-506), and correctly characterised as *corroborating* with Condition 1 primary
  (C10R:63-75; C10J Q2_ANSWER line 2, `corroborating_only_306_replacement_bullet`). This also matches ADJR note N5.
* **(d) Freeze before recomputation.** SPEC:24 quotes C2 Condition 1 (C2A:536-537) verbatim, and C10R:81-82 verbatim
  ("may freeze a different prospective adoption rule without retroactively altering C2"; "may not ... re-adjudicate
  305 or 306 under a new rule, or apply its own rule to an adoption already made").
* **(e) Two-implementation agreement.** SPEC:25 quotes C2A:465-468 ("The open risk is N9 ... What does protect against
  it is a second, structurally independent route", ellipsis correct), C10J:178 ("answer IMPLEMENTATION INDEPENDENCE,
  not merely add margin") and C2N:23-24 ("re-execution with different inputs, not an independent check"). All verbatim.
* The consumer quotations are also exact: THEOREM_AD §4 Lemma Dv′ r2 (THEOREM_AD.md:86, SPEC:29), the D4 docstring
  (c2_d5_forecast.py:71, SPEC:30), the C10 retroactivity sentence (C10J:155, SPEC:45-46), "YES, prospectively"
  (C10J:53, SPEC:47) and the deferred-cell sentence (C2A:509-510, SPEC:48-49).
* The JSON's single-quoted quotations (RULE:23, RULE:59) are not machine-checked, but I checked each by hand: all
  verbatim up to marked ellipses.
* **Old F1 status.** SPEC:35-43 and RULE:58-64 state F1 LAPSED as a whole limb, not retroactively. Correct:
  * The lapse clause (C2A:432-433) has no cell qualifier. N9 is CLOSED (ADJ line 2; ADJR line 2 ADJUDICATION_ACCEPTED).
  * Lapse removes an adoption route and adds none. It therefore fails safe for every cell. For 307-309 it also removes
    the registry-free route. That is the literal consequence of C2's text, and it can only delay an adoption.
  * The ADJ (§5, lines 146-153) itself declined to apply the lapse. ADJR N5 records that the lapse condition is
    "textually met" and that the C2 floor remains the standard until a replacement is frozen. SPEC:40-42 is consistent.
  * Non-retroactivity matches C2A:422-423, C10R:81-83 and C10J Q2_phase6 (B "NOT RETROACTIVELY").

**Answer: accurate.** Only minor attribution imprecisions exist (notes N7, N8).

## Q2 — Prospective, frozen before recomputation, not fitted

* **What the commit contains.** a15d083b adds only the six namespace files (`git show --stat`). No file outside the
  namespace changed since fb237288.
* **No computation.** floor_r2_build.py imports hashlib/json/pathlib only and writes constant text. floor_r2_verify.py
  reads sources as text via `git show`. It loads C11RD_RUNS D1/D2 into memory only to build a hash set for the leak
  scan, and prints no value. Neither imports or executes any consumer module. No commit, ref or reflog entry after
  fb237288 exists other than a15d083b.
* **No fitted parameter.**
  * The rule's only numbers are the inherited factor 2 (N9 rule) and ×1.25 (r1 F2). Verified: no JSON number and only
    two decimal tokens, 1.25 and the disclosed 3.7e-97 offset.
  * The adoption criterion is sign-only (RULE:55).
  * Every discretionary design choice cuts against adoption or is neutral:
    * mixing across implementations is forbidden, which removes the componentwise best of both;
    * the C_T record chosen for I2 is the larger, outward-rounded one;
    * the D′ mixed supply is excluded;
    * the chosen supply for 306 is fixed to the historical S_I1;
    * the F2 route for 306 is locked to C2's published classification.
  * None of these could have been tuned toward adoption after seeing a value.
* **The no-inspection statement.** It is present and explicit: SPEC:250-261 and RULE:146 and RULE:148-152. It is
  consistent with the package. The designer's disclosed exposure (pre-N9 C2/C10 figures; N9 classes and ratios) is
  listed. The statement that REGISTRY_C2.json and C2_D5_FORECAST.json were not opened is consistent with the verifier,
  which touches them only through `git rev-parse`.
* **Limits.** What happened outside the repository is an attestation that I cannot verify (note N13). The rule has
  no free parameter that such knowledge could have tuned.

**Answer: yes.**

## Q3 — Completeness of the comparison design

Each required element is present:

| element | where |
|---|---|
| both implementations | SPEC:62-69 (F1′ (a)-(d)), SPEC:137-141, RULE:112-138 |
| compared quantity: exact rational Γ(5, k; S) from the frozen consumer path, strict sign | SPEC:87-89, RULE:76-77 |
| supplies S_I (componentwise min over Lemma G and Lemma Dv′ r2 of I's own sets) | SPEC:90-94, RULE:80 |
| consumer validation | SPEC:97-98; matches c2_d5_forecast.py:62-63 and deflated_consume.py:88-89, 100-101 |
| κ | SPEC:95-96; deflated_consume.py:55-56 and THEOREM_AD.md:24 (analytic Gaussian moments) |
| statement/domain compatibility | SPEC:112-120, RULE:154-158 |
| numerical threshold (factor 2 per constant; no ratio threshold for adoption) | SPEC:101-108, SPEC:121-122, RULE:54-57 |
| STRONGER policy: agreement only, never substitutes, not soundness evidence | SPEC:123-127, RULE:7-11 |
| asymmetric bounds (D_lo the only lower bound; enters its own supply's denominators; lower-bound rule applied) | SPEC:128-133, RULE:17-21; matches C11R_N9_STATEMENTS.json:57 and the D_lo denominators at c2_d5_forecast.py:64-65 |
| fail-closed | SPEC:178-186, RULE:40-46 |
| independence | SPEC:151-166, RULE:47-52 |
| disagreement (per-constant, closure, contradiction, no re-evaluation) | SPEC:170-177, RULE:34-39 |

For cell 306, the per-constant precondition is satisfied as bound. I checked the field structure and classes only:

* C11R C_T, tau and D_lo are AGREES and Abar is STRONGER.
* The statements are EQUIVALENT for C_T, tau and Abar and STRONGER for D_lo, all on domain EQUAL.
* C11RD D1 and D2 are STRONGER, with EQUIVALENT statements (ADJ; C11RD_COMPARISON.json).
* The whole block in G05 (GATE:25) equals C11R_N9_STATEMENTS.json:257-259.

**Answer: yes.** See N3 for one fail-closed wording inconsistency.

## Q4 — No reliance on STRONGER; soundness evidence per implementation

* **No reliance on STRONGER.** SPEC:125-127 and RULE:10 say STRONGER is not soundness evidence. F1′(d) requires each
  supply to close on its own. The rule nowhere uses I2's STRONGER D1/D2 to improve S_I1.
* **Per-implementation evidence** is stated separately (SPEC:137-141, RULE:112-136). I checked each claim.
* **I1.**
  * C2's two-pass re-certification of cell 306's 18 artifacts matches C2N:63-68 (18/18 bit-identical at 256 bits;
    45/45 valid at 384 bits).
  * The C2 adjudicator re-certified five artifacts with an independent python-flint venv and re-derived Γ exactly
    (C2A:41-47, C2A:71, C2A:583-587).
  * REGISTRY_C1 records `taboo_certify` sha256 ced9422c..., which equals C11R's `original_certifier` sha256. So both
    I1 registries come from the same certifier bytes.
  * Residuals: N10 open (C2N:40-53) and never independently re-implemented (C2N:98-99).
* **I2.**
  * C11R chain, confirmed by `git log`:
    * eight pre-freeze and pre-qualification reviews (6d7cd546 … 5890511b READY_TO_QUALIFY);
    * QUALIFICATION_ACCEPTED 445fd84e;
    * AUTHORIZATION_ACCEPTED 9bd17be5;
    * EXECUTION_ACCEPTED 22537709;
    * COMPARISON_ACCEPTED 7375b9cd.
  * C11RD chain:
    * READY_TO_QUALIFY 3c1eff11 (C11RD_R1_PRE_EXECUTION_REVIEW.md line 2);
    * validation 29/29 at evidence/validation_r1/C11RD_VALIDATION.json, where v04, v13, v15, v22, v24 and v25 are all
      present and pass;
    * non-target rehearsals (evidence/rehearsal_r1);
    * QUALIFICATION_ACCEPTED e27c2ffd, EXECUTION_ACCEPTED db1c6118 and COMPARISON_ACCEPTED 90265349;
    * the comparison review's own exact Fraction recomputation of all sub-blocks (C11RD_COMPARISON_REVIEW.md:28);
    * ADJUDICATION_ACCEPTED fb237288.
  * All 16 commits I checked are ancestors of a15d083b and carry the stated role.
  * The C11RD dependency on C11R's F_H certificate is correctly described (C11RD_FREEZE_R1.json:147-150).
* **Imprecisions (non-blocking).**
  * I1's evidence list includes "six-constant agreement with I2". That is at most conditional corroboration, and the
    same RULE object says comparison classes are not soundness evidence (note N1).
  * The theory citation for 3c1eff11 is compressed (note N9).

**Answer: yes, with notes.**

## Q5 — The N9 adjudication review's notes

* **N1 (C_T exact supremum vs outward-rounded record).** Addressed at SPEC:141 and SPEC:145-146, and at RULE:3 and
  RULE:134. I confirmed by boolean check that the C11R C_T record exceeds the exact supremum A by between 1e-98 and
  1e-96, consistent with the stated ~3.7e-97. The rule uses the record in S_I2. That is conservative, because Lemma
  Dv′ is increasing in C. Combining the record with D1/D2 propagated from A is valid, because each constant is
  separately a true bound.
* **N2 (STRONGER does not prove soundness).** Addressed at SPEC:126-127 and SPEC:141, RULE:10 and RULE:132.
* **N3 (implementation-only independence, not authorship).** Addressed at SPEC:151-163 and RULE:48 and RULE:133.
* **Exposure of the original values.** Disclosed at SPEC:162 and RULE:48, with the correct source
  (docs/C11RD_INDEPENDENCE_AUDIT.md:20-21). The floor designer's own exposure is disclosed at SPEC:256-258.

**Answer: yes, all four are addressed.**

## Q6 — Is F1′ a sound replacement for F1?

* **It answers implementation independence, not margin.**
  * F1′(d) requires Γ < 0 under each implementation's own supply, separately.
  * If I1 is faulty and I2 is sound, Γ(S_I2) < 0 is a valid closure certificate. If I2 is faulty and I1 is sound,
    Γ(S_I1) < 0 is.
  * An F1′ adoption is therefore correct whenever at least one implementation is sound. That is single-fault
    tolerance, which is exactly what C2A:464-468 and C10J Q2_phase9 require of an F1 substitute.
  * It adds no margin threshold (SPEC:121-122).
* **No mixing of the chosen supply.**
  * SPEC:57-60 and SPEC:79-83, RULE:88 and GATE G08 forbid any cross-implementation combination in the base/F2 supply
    and in F1′.
  * This closes the obvious loophole: a componentwise-best S_I1 ∪ S_I2 would be valid only if both implementations
    were sound.
  * The S_I definition (RULE:80) and G08 ("S_I1 contains no I2 constant; S_I2 contains no I1 constant") are consistent.
* **Common-mode residuals** are disclosed (SPEC:164-166, RULE:49):
  * the shared frozen model, kernel definition and derivative theory (THEOREM_AD);
  * Lemma G (the K1 C_upper and norms);
  * the consumer (tct_rule, the K5-B direct clause, the K1 stack);
  * κ₁ and κ₂, which are analytic Gaussian moments. They are shared but trivially verifiable, and the C11RD
    derivation uses its own enclosure of the same moments (C11RD_FREEZE_R1.json F_derivative_recurrence.kappa).
* **Loophole search.**
  * I found no path by which an F1′ adoption rests on one implementation alone.
  * F2 remains a single-implementation limb (inherited from r1, where F2 alone also permitted a registry-only adoption
    by design: C2A:448-450; C10J Q2_phase9 "F2 protects against numerical fragility"). r2 does not widen it.
  * For 306, F2 is dead by construction: SPEC:224-226 and G12 require a re-evaluation to reproduce C2's published FAIL
    or stop.
  * The chosen supply for 306 is pinned to S_I1 (SPEC:216-217, G08).
  * Closure disagreement between supplies fails F1′ (SPEC:172-174).
  * No re-evaluation is allowed after a disagreement (SPEC:177).
  * The S_I2 evaluation is exactly once and sealed before interpretation (G11).
* **Validation cannot silently void F1′ for 306.** I confirmed by boolean check that I2's C11R records pass the
  consumer precondition, so the one S_I2 evaluation is not guaranteed to fail closed.

**Answer: sound, within the disclosed common-mode scope.**

## Q7 — Scope and the future cell-306 criterion

* **306 is the only operative target:** SPEC:193-195, RULE:108.
* **307-309 are out of scope:** no work, no gate or criterion, no F1′ extension and no statement on closure or
  adoptability (SPEC:196-203, RULE:107, G14). Note N4 covers the interaction with "standing floor".
* **Adoption is separated from closure and from N9:** SPEC:204-212, RULE:12-16. This matches C10J Q2_phase6
  (concepts C and D) and ADJ §5.
* **No re-adjudication of C2's 305/306 verdicts:** SPEC:41-50 and RULE:23, RULE:61. The support is sound:
  * C10J:155 and C10R:81-83 forbid rewriting a past verdict;
  * C10J:53 and C10R:104-106 permit a prospective campaign targeting 306;
  * C2A:508-510 and C2N:117-119 expressly contemplate 306 closing "under a floor frozen in advance".
* **The future criterion is unambiguous** (SPEC:216-231, RULE:29-33, GATE G00-G14):
  * the chosen supply is fixed to S_I1;
  * control: the exact string reproduction of `cells['306'].Gamma_exact` of C2_D5_FORECAST.json (blob a191557f), before
    S_I2 is evaluated (G10);
  * exactly one sealed Γ(S_I2) evaluation (G11);
  * the decision table (G12);
  * independent review and adjudication, and only that chain may create r6 (G13).
* **S_I1 really equals C2's adopted supply.** In c2_d5_forecast.py:
  * lines 194-205 build `sup = {"G": T.atom_constants_generic(...), "C1": DC.atom_constants_r2(C1 block), "C2":
    DC.atom_constants_r2(C2 block)}`;
  * line 204 applies `combine(sup)`, the componentwise minimum over A0, A1, A2 (lines 70-76);
  * κ is DC's default K1_BOUND/K2_BOUND (deflated_consume.py:55-56, 97), cross-checked against the local copy
    (c2_d5_forecast.py:40-41, 201).

  This is exactly SPEC:90-94 with I = I1 = {REGISTRY_C1, REGISTRY_C2} blocks for 306. The REGISTRY_C1 content hash
  equals the pin `C1_REG_SHA` (c2_d5_forecast.py:36), and deflated_consume.py blob a0a836fa hashes to `DC_SHA` (line
  37). C2A:59-61 records per-field provenance "C2 on every field of every cell".

**Answer: yes.** Notes N5 and N6 cover gate-execution details that the future campaign's own freeze must settle.

## Q8 — Machine-readable consistency and the verifier

* **The JSONs match the spec.** Section by section, RULE and GATE match SPEC:
  * rule, quantity, supplies, thresholds, STRONGER, asymmetry, soundness, independence, disagreement, scope and the
    306 criterion;
  * the G00-G14 list at SPEC:233-248 matches GATE:3-63.

  The one wording inconsistency is N3.
* **Build and self-hashes.** floor_r2_build.py reproduces both files byte-for-byte. Both `sha256` fields verify
  (ba988b9e..., db7806fc...).
* **Verifier rerun.** PASS 19/19, exit 0. Output is identical to the committed evidence except HEAD. No
  `__pycache__` was created, and none needed removal.
* **Are the checks meaningful?** Each is capable of failing:
  * The blob checks use `rev-parse` prefix matching. A missing path yields non-hex output, so the check fails.
  * The C11RD at-commit check requires equal and non-empty ids.
  * The quote list is 23 raw-substring checks against the attributed sources.
  * The spec-quotation check covers all 16 italic quotations.
  * The JSON checks are: no number, only two decimal tokens, and self-hash.
  * The governance checks are: lineage, exactly one verdict line each, no r6 filename, the consumed ref at G, and
    `git diff` plus pending status for foreign changes.
  * The leak scans use the frozen original hash set and an in-memory independent hash set. They cover decimal,
    scientific and rational renderings at several scales (c11rd_qualify.py:1281-1303).
  * Five negative controls fire.
* **Weaknesses (non-blocking, note N11).**
  * The spec-quotation check looks pieces up in the union of nine sources. It does not check the attributed source
    or the order of elided pieces. I checked attribution myself: all correct.
  * RULE's single-quoted quotations are not checked. I checked them by hand.
  * There are no negative controls for blob mismatch, self-hash tamper, foreign-change detection or r6 detection.
  * The self-hash detects accidental edits only. Governance integrity rests on G00's commit binding.

**Answer: consistent, and the checks are meaningful.**

## Q9 — Governance state unchanged

* **N9 CLOSED.** ADJ line 2 is `N9_CLOSED`. ADJR line 2 is `ADJUDICATION_ACCEPTED`. Both are unchanged since fb237288.
* **Cell 306 not adopted; K5 PARTIAL.** r5 K5_COVERAGE_MAP_R5.json is blob f978eeb6b411… at both fb237288 and
  a15d083b (byte-identical). Its `union_open_ranges` is [[306, 309]] and `K5_COVERAGE_COMPLETE` is false. So K5 is
  PARTIAL, and 306-309 are open at m = 5.
* **307-309 untouched.** No file of theirs changed. `git diff --name-only fb237288 a15d083b` lists only the six
  namespace files.
* **No r6.** There is none in the HEAD tree and none in any ref's history.
* **Other state.** The consumed ref still points at G (4b716d43). No branch other than this one contains fb237288.

**Answer: unchanged.**

## BLOCKERS

none

## NON-BLOCKING NOTES

* **N1 — I1's evidence list includes the comparison it elsewhere disclaims.**
  * RULE:117 and SPEC:140 list "six-constant agreement with I2 (N9 CLOSED)" as soundness evidence for I1. RULE:137
    says "The comparison classes are not soundness evidence", and SPEC:125-127 says the same of STRONGER.
  * At most, the agreement is *conditional* corroboration. If I2 is sound, I1's Abar, D1 and D2 are implied valid
    (I2 ≤ I1 for these upper bounds). For C_T, tau and D_lo the AGREES class gives no soundness implication.
  * No operational effect: F1′'s correctness rests on (d), not on (c).
  * A future adjudication should read this item in that restricted sense.
* **N2 — "the two sets" in F1′(b).**
  * I1 contributes two six-constant sets to S_I1 at 306: the REGISTRY_C1 and REGISTRY_C2 blocks, both produced by
    taboo_certify ced9422c. Only the REGISTRY_C2 block was compared under N9 (C11R_N9_STATEMENTS.json `provenance.inputs`).
  * This is harmless. The comparison is a precondition, not the soundness argument. C2A:59-61 records that the C2 block
    supplies every field of S_I1.
  * The wording should be read as "the compared set of I1 is the REGISTRY_C2 block".
* **N3 — fail-closed wording differs between SPEC and RULE.**
  * SPEC:186 says every listed case means "DO NOT ADOPT, and the cell stays OPEN".
  * RULE:41 says an unbound or unreviewed input makes only F1′ "unavailable", and RULE:43 says "stop, nothing is decided".
  * For cell 306 GATE:2 governs: any failure stops without a decision, and F2 is dead. For other cells the stricter
    SPEC reading should prevail.
* **N4 — 307-309 "no criterion" vs "standing floor".**
  * SPEC:191-192 makes r2 the standing floor for all K5 m = 5 tail adoptions frozen after it is in force.
  * SPEC:198 says r2 "sets no gate or criterion" for 307-309. That is reconcilable as "no cell-specific gate or
    criterion".
  * A future 307-309 campaign is governed by r2 (base + F2, F1′ unavailable without its own two-implementation
    evidence) unless it freezes a further replacement first. SPEC:202-203 says so.
* **N5 — consumer-path binding is incomplete in the gate.**
  * RULE:76 calls tct_rule.py a "pinned dependency". c2_d5_forecast.py actually sha-pins only deflated_consume
    (`DC_SHA`) and the C1 registry. It loads tail_forecast_r2.py unpinned (c2_d5_forecast.py:144), and that module does
    a plain `import tct_rule` (tail_forecast_r2.py:41).
  * tail_forecast_r2.py (blob edec817e…) and the non-supply inputs appear in neither RULE nor G04. Those inputs are
    TCT_INPUTS_306, ADOPTED_TAIL_INPUTS, cells.json and the K1 record manifest.
  * The adoption quantity is still well defined ("the frozen consumer path that produced C2's committed Γ_exact", i.e.
    the chain at 5a94568a), G03 obliges the campaign to freeze "the consumer path and its hashes", and G10's exact
    control is an end-to-end check.
  * The future freeze should bind all of these explicitly.
* **N6 — executing G10 as literally worded.**
  * `c2_d5_forecast.main()` loops over all tail cells 305-309 (line 194). It computes Γ and the uniform-A requirement for
    each. It also requires the off-host K1 record store (`--records`, `FC.adopted_state`).
  * Running it as-is for the control would evaluate 307-309, which contradicts G14's "not evaluated", although only on
    historical S_I1 values. It also needs remote data.
  * The future campaign should freeze a cell-306-only driver that reuses the frozen functions (`direct`, `combine`,
    `atom_constants_r2`, `atom_constants_generic`). It should not compute any margin or `requirement()` on S_I2.
* **N7 — attribution of "exactly equal is INVALID".** SPEC:107 and RULE:78 attribute the per-constant rule to the C11R
  statement table. The table's UPPER_BOUND STRONGER includes equality (C11R_N9_STATEMENTS.json:44-58). The
  exact-equality INVALID rule comes from C11R's comparator (c11r_compare.py:495) and the C11RD freeze's
  `L_agreement_criterion.copied` (C11RD_FREEZE_R1.json:218). The substance is right; the source is merged.
* **N8 — C11R's `forbidden_conclusions` do not bind r2.**
  * N9R_GATE_C11R.json:48-52 forbids the C11R/C11RD evidence chain from concluding "that F1 has lapsed" and "that the
    C2 adoption floor may be replaced". ADJR confirms the N9 adjudication respected that.
  * r2 is the separate governance step that ADJ §5 (lines 146-151) and C2 Condition 1 contemplate, so drawing those
    conclusions here is proper.
  * It would help if the spec said so explicitly.
* **N9 — theory citation compressed.** SPEC:140 credits 3c1eff11 (READY_TO_QUALIFY) with "Proposition 1, Lemmas 0–4
  and 6, Theorem 5".
  * That review read Proposition 1, Lemma 4 and Theorem 5 plus the full diff 71495747..ce5b8595.
  * Lemmas 0-3 and 6 were examined by the predecessor review 663f8fe7 (NOT_READY).
  * The verdict covers the frozen theory as a whole, so the claim is right in substance.
* **N10 — κ provenance.** "Outputs of neither implementation" (SPEC:95-96) is true of the operator-constant
  certifiers. κ₁ and κ₂ are rational upper bounds of analytic Gaussian moments (THEOREM_AD.md:24). deflated_consume.py
  :53-54 notes they were proved in Arb by a Perron-deflation gate. They are common-mode but trivially checkable.
* **N11 — verifier limitations** (see Q8): union-of-sources quote lookup; unchecked single-quoted JSON quotations; no
  negative controls for blob mismatch, self-hash tamper or foreign-change and r6 detection.
* **N12 — the committed evidence predates the commit.** evidence/FLOOR_R2_VERIFY.json records HEAD fb237288. It was
  generated with the namespace files pending, and the foreign-change check includes pending paths, so this is
  expected. My rerun at a15d083b reproduces every check and information field exactly.
* **N13 — the no-inspection statement is an attestation.** Nothing in the repository contradicts it. What happened
  outside the repository cannot be verified. The rule's lack of free parameters limits what such knowledge could
  have changed.

## Confirmation

* I modified nothing in the repository. I ran no git write command. `git status --porcelain --ignored
  --untracked-files=all` printed 0 lines before and after every executing step, and no `__pycache__` exists in the
  worktree. I wrote only inside
  /private/tmp/claude-501/-Users-suzhe-ReBaseGuard/ea6191ae-93b1-4f9c-b9ba-6cd0430d32ee/scratchpad/floor_r2_review/
  (VERIFY_RERUN.json and this file).
* I computed, estimated or inspected no Γ, atom constant, uniform-A margin or F2 value for any supply containing a
  C11R or C11RD constant. I computed no post-N9 adoption magnitude of any kind.
* I printed, wrote and quoted no D1/D2 value, original or independent. Operator-constant values from C11R/C11RD were
  touched only inside boolean predicates.
* I did not open REGISTRY_C2.json, C2_D5_FORECAST.json or C11R's quarantine. I ran no consumer, certifier, runner,
  comparator or launcher. I used no AWS/Vultr tool, no network and no session transcript.
