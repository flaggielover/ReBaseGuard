# K5 PARTIAL closeout protocol: CUSUM K5, m = 5 tail cells 306–309

**Status: FROZEN** by the commit that adds this file. The freeze commit hash is recorded in the freeze review and
in the handover.

After the freeze, neither this file nor `code/closeout_checks.py` is edited. Checker outputs go to `evidence/`
only.

**This protocol authorizes no scientific computation.**
* No Γ is evaluated.
* No target-equivalent proxy, Monte-Carlo science or interval/certificate science is performed.
* No supply is searched and no constant is optimized.
* No floor or adoption limb is created, no cell is adopted, and no coverage map is created or modified.

---

## 0. Authority and supersession

* **What it implements.** This protocol implements the user's authorization "Final K5 PARTIAL Adjudication +
  Publication Closeout" (2026-09-27).
* **What it supersedes.** It supersedes the draft `level4/closure_proofs/p5y_k5_tail_route_audit/protocol/PROPOSED_K5_PARTIAL_CLOSEOUT_DRAFT.md`
  (4a4b1392). That draft stays unedited as history.
* **Authoritative inputs.**
  * Route audit r1: `level4/closure_proofs/p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md` (802be11e).
  * Its independent review: `level4/closure_proofs/p5y_k5_tail_route_audit/review/ROUTE_AUDIT_R1_REVIEW.md`
    (2f36352e, **ROUTE_AUDIT_ACCEPTED**).
* **The route-audit conclusion is fixed.**
  * No prospective K5 scientific expansion under present governance.
  * No new 306, 307, 308 or 309 campaign, and no joint 307–309 campaign.
  * No new floor or adoption limb, and no r6.
* **Deferred research stays deferred.** Deferred research items (§8) are optional research, not prerequisites for
  this closeout. They are neither failed nor completed.

**Repairs carried from the r1 review (N4.1–N4.9 and the other notes):**

| r1-review item | where implemented |
|---|---|
| N4.1 allowed evidence | §3 |
| N4.2 administrative checks vs scientific computation | §4 |
| N4.3 K5-level vocabulary | §5 |
| N4.4 P5Y consequence and H3a rule | §7 |
| N4.5 307 wording | §6 (307) |
| N4.6 308 and C4 Condition 3 | §6 (308) |
| N4.7 deferred research list (with R4 risk HIGH) | §8 |
| N4.8 "current", not "final" | §11 |
| N4.9 SR K5 across refs | §10 |
| N1 (information gain vs preservation; D's cost; U3 not tainted) | §8, §12 |
| N2 (R-I2-alone needs no host), N3 (R4 risk), N5 (clause), N6 (U2 open, erratum E1, K4 ref) | §8, §14 |

## 1. Scope

* **Object.** The K5 obligation for the CUSUM detector: D = CUSUM, m ∈ {1, 2, 3, 5}, on the frozen CUSUM K1 cover
  cells 0–309 meeting (0, 2] (`level4/closure_proofs/p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md`
  :89).
* **Focus.** The current disposition of m = 5 cells 306–309, the only open cells in the current authoritative map.
* **Every other CUSUM (m, cell)** is carried as the current authoritative coverage map records it, and is not
  re-adjudicated.
* **Out of scope:**
  * SR K5, which is carried over unchanged and not adjudicated (§10);
  * K1, K4 and P5Y assembly, which are not adjudicated (only the consequence in §7 is stated);
  * AWS SR/PS1.

## 2. Question

> Given the current authoritative evidence and the accepted prospective route audit, what is the correct current
> disposition of CUSUM K5, and of each of cells 306–309?

The question is **not** "can K5 somehow be closed?". The answer records the state and does not improve it.

## 3. Allowed evidence (N4.1)

**Allowed.**
* Any artifact committed on branch `p5y-k5-tail-c11rd-d1d2-extension` at or before the freeze commit that bears on
  the K5 state.
* Committed artifacts on other refs, cited by ref and commit, where the SR K5 or P5Y status requires it (§7, §10).

**Rules on use.**
* Every citation carries its artifact's historical governance status:
  * ACCEPTED / REJECTED / INVALID / PARTIAL / CLOSED / STOPPED, as committed;
  * whether the evidence is certified (CI/EX), diagnostic (NE) or uncertified (e.g. Monte-Carlo).
* No new scientific evidence may be generated.
* No uncommitted artifact may be load-bearing.
* Uncertified evidence (Monte-Carlo, COUNTERFACTUAL_ONLY sweeps, projections) may be **reported**. It may never
  support an authoritative exclusion or closure.

**Forbidden.**
* Anything under a C11R quarantine directory.
* Any original or independent D1/D2 value.
* Session transcripts.

## 4. Administrative checks versus scientific computation (N4.2)

### Allowed administrative / mechanical verification

* git ancestry, `rev-parse`, `cat-file`, `diff`, `log` (including pickaxe), `for-each-ref`, `status`;
* blob and file identity, and hashes;
* grep and `sed -n` reads;
* the value-free hashed leak scan;
* JSON structure checks (e.g. r5's `per_m.*.open_ranges`, `K5_COVERAGE_COMPLETE`);
* citation-existence checks;
* review-format checks;
* additive-only diff checks;
* the research-synthesis document verifier (`docs/research_synthesis/verify_synthesis.py --no-diff-check`,
  blob `d2411ab805e3bc58ba1d77a6894c3fa67da005fd`), in the publication phase only.

**The only code this closeout runs** is:
* `code/closeout_checks.py` (frozen here, stdlib and git only);
* that document verifier;
* git.

**Properties of the checker:**
* It imports no campaign module. Its hashed-scan helpers are verbatim stdlib copies with sources cited in its
  docstring.
* It reads the original-value hash set by AST literal parsing.
* It prints only counts and file names, never a value.

**Who may run it:**
* reviewers and the adjudicator, with `--out` pointing outside the repository;
* the closeout itself, with outputs committed under `evidence/`.

### Forbidden scientific computation

* any Γ evaluation, for any cell or supply;
* any target-equivalent proxy (margins, factors, bisections, knockouts, Λ bounds, replays, calibrations);
* any new interval or certificate calculation;
* supply search and constant optimization;
* Monte-Carlo science;
* theorem or proof computation producing new K5 evidence;
* running any campaign producer, certifier, verifier or driver.

## 5. Vocabulary and the prospective decision rule (N4.3)

### K5-level verdict tokens

These are repository vocabulary: the E01 decision rule (`K5_TARGET_AND_THIRD_ORDER.md` :91) and the
`K5_DECLARED_CLOSED` flag used across P5Y records.

| token | meaning |
|---|---|
| `K5_CLOSED` | the K5 obligation is established (the repository records it as `K5_DECLARED_CLOSED = YES`) |
| `K5_FAIL_MATHEMATICAL` | E01 :91: a certified `R'''_cell.hi < 0` on a cell containing 0, i.e. a certified counterexample to H3a |
| `K5_INCONCLUSIVE` | E01 :91: "otherwise unresolved cells ⇒ `K5_INCONCLUSIVE`" |

No other K5-level token is used, and no "failed" verdict is invented.

### Rule

The rule is applied to the CUSUM K5 object of §1, mechanically, in this order.

1. **`K5_FAIL_MATHEMATICAL`** if committed, accepted evidence contains either:
   * a certified `R'''_cell.hi < 0` on a CUSUM cell containing 0, for some m; or
   * any other independently proved counterexample to H3a for (CUSUM, m), as
     `level4/closure_proofs/p5y_k5b_independent_countersignature/README.md` :236–238 requires for refutation.
2. **Otherwise `K5_CLOSED`**, if both of the following hold:
   * the current authoritative coverage map records `K5_COVERAGE_COMPLETE = true`, i.e. every m ∈ {1, 2, 3, 5} and
     cells 0–309 passing;
   * an accepted adjudication has established the remaining K5-B premises (countersignature README §10).
3. **Otherwise `K5_INCONCLUSIVE`.**

### What `K5_INCONCLUSIVE` means in this closeout

* **(a)** The currently required K5 closure/adoption conditions have not been established for all required cells.
* **(b)** The open cells are **not** thereby scientifically refuted.
* **(c)** Under the accepted route audit r1, no currently justified prospective campaign is required before
  publication closeout.
* **(d)** The current authoritative coverage map remains r5.

### Per-cell states

* Cells keep their own states: OPEN, NOT ADOPTED, not certified, refuted within a stated scope.
* `K5_INCONCLUSIVE` is **not** applied to individual cells. No authoritative protocol defines per-cell semantics
  for it.

### P5Y-wide K5 (SR ∪ CUSUM)

* It receives **no** verdict here.
* The only statement made is a mechanical one: it cannot currently be `K5_CLOSED` while its CUSUM component is not.
* Nothing is inferred about SR K5.

### Pre-freeze reconstruction

This is recorded for the adjudicator. It is not binding on them; they must independently confirm or refute it.

* **Rule 1 does not fire.** The only certified R''' evidence on the CUSUM cell containing 0 is
  `level4/closure_proofs/p5y_k5_cusum_first_real_probe_result/RESULT.md` (`FIRST_CELL_SUPPORTED_ALL_M`: certified
  lower bounds on R'''(0) positive for every m). No certified counterexample to H3a exists in committed evidence.
* **Rule 2 does not fire.** r5 records `K5_COVERAGE_COMPLETE = false`, with m = 5 open [[306, 309]].
* **So the rule yields `K5_INCONCLUSIVE`.**

## 6. Cell dispositions (reconstructed pre-freeze from committed evidence; the adjudicator confirms or corrects)

### Cell 306

Several facts **coexist**, and none may be collapsed into a single verdict word.

* **Scientific: closes under I1's supply.**
  * Value: Γ(5, 306; S_I1) = −0.030469257709306738 under the C2 clause.
  * Source: `level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md` :47, CI/EX,
    C2 PARTIALLY_ADOPTED [305] ae4cbc2c.
  * It was reproduced exactly by the C12-R2 control.
* **Scientific: closure is not certified under I2's own supply.**
  * Value: Γ(5, 306; S_I2) = +0.005159101140006536, sealed once (276f4d41).
  * Review: `level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/review/C12R2_EXECUTION_REVIEW.md`,
    EXECUTION_ACCEPTED (1173670f).
  * This is **non-certification, not disproof**.
* **Trust condition: N9 is CLOSED.**
  * `level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/adjudication/ADJUDICATION_C11RD_N9.md` (7d67989d).
  * `level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md`,
    ADJUDICATION_ACCEPTED (fb237288).
  * N9 is a trust condition, not closure or adoption.
* **Governance: the floor r2 adoption criterion is not met.**
  * Base clause: TRUE.
  * F1′: (a)–(c) TRUE, (d) FALSE (closure disagreement between I1 and I2).
  * F2: FALSE, as published by C2 §K: Γ at ×1.25 = +0.029163293, uniform-A margin 1.1277 (C2 adjudication
    :65, :474–478).
  * Decided by `level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/adjudication/C12R2_ADOPTION_ADJUDICATION.md`,
    **CELL306_NOT_ADOPTED** (9c2cbf21).
  * Its review: `level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/review/C12R2_ADJUDICATION_REVIEW.md`,
    **ADJUDICATION_ACCEPTED** (c5324a78).
* **Authoritative disposition: OPEN, NOT ADOPTED.**

### Cell 307

* **Wording (N4.5): "No route that closes 307 has been certified."**
* **Evidence.** Committed certified supplies were evaluated at 307 and did not close it:
  * the C2 D4 supply: Γ positive (C2 adjudication :48);
  * the C3 D′ mixed supply: Γ positive (`level4/closure_proofs/p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md`
    :349; C3 REJECTED as a campaign).
* **Blocker structure.**
  * The second- and third-order terms (A1, A2) are material. With A1 = A2 = 0, 307 closes at the certified A0,
    so A0 is not its blocker (C3 :349; `level4/closure_proofs/p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md`
    :288–290).
  * No committed closing supply exists.
  * The two-implementation limb F1′ is **unavailable**: no second-implementation certification exists for 307
    (floor r2 spec :193).
* **Reported, not load-bearing.**
  * C9's α projection (1.098807×–1.137406×) is a COUNTERFACTUAL projection. It was never certified; C9 is
    EXECUTION_BLOCKED_ON_RUNTIME_AND_AUTHORIZATION.
  * C8's factors are COUNTERFACTUAL_ONLY, under the C5-T clause.
* **UNKNOWN:** every route not certified. **No impossibility is claimed.**
* **Authoritative disposition: OPEN.**

### Cell 308

**Ruled out (certified, EX):**
* Improving the second- and third-order terms alone does not suffice at the certified A0.
* Evidence: knockout A1 = A2 = 0 still leaves Γ = +0.039568 (C3 adjudication :350; C3 OND C3-N4).

**C4 Condition 3, carried verbatim** (C4 adjudication :534–537):
> at `A0 = 4.311`, the Monte-Carlo value of `Λ₃₀₈`, closing cell 308 still requires an **18.2× reduction of
> `(A1, A2)`**; at `A0 = 4.375229` it is impossible at any `(A1, A2)`. C4-N3 stands and is binding: nothing licenses
> "cell 308 is closable".

**C4's status wording** (C4 adjudication :510–512): "operator-level route not excluded". C4 Condition 2 (:527–533)
forbids quoting "none can" / "cannot be excluded" as establishing anything.

**Uncertified evidence, reported and NOT authoritative:** 2,000,000-path Monte-Carlo evidence at ~65 standard errors
suggests no lower-bound route will exclude 308. It is not an exclusion. No certified upper bound on Λ₃₀₈ exists.

**UNKNOWN:** everything not ruled out above. Nothing licenses "308 is closable", and nothing establishes "308 is not
closable".

**Authoritative disposition: OPEN.**

### Cell 309

**Refuted within scope only** (CI + EX), in C4 Condition 1's wording (C4 adjudication :522–524): "for the uniform-A0
atom-constant family, at cell 309, at m = 5, against the frozen measurement inputs and the frozen TC-T / K5-B
consumer".

**Strengthened by C7.** The certified Λ₃₀₉ ≥ 3.586306094
(`level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309/README.md`, ACCEPTED_WITH_CONDITIONS) exceeds the C5-T-clause
ceiling 3.266416 by 9.79 % (C8 adjudication, ACCEPTED_WITH_CONDITIONS).

**Not generalized.** C4 :503 says this is not a statement that 309 is unclosable.

**UNKNOWN outside the scope:**
* sup-norm routes;
* finer cover;
* real order-3;
* assembly / clause tightening;
* residual-specific routes;
* other independently justified future theory.

**Authoritative disposition: OPEN.**

### Other cells

CUSUM m ∈ {1, 2, 3} cells 0–309 and m = 5 cells 0–305 are carried as r5 records them (passing). They are not
re-adjudicated.

## 7. H3a and the P5Y consequence (N4.4)

### H3a

* **The rule.** A failed or unresolved K5 cell is **not**, by itself, evidence against H3a.
  * Source: `level4/closure_proofs/p5y_k5b_independent_countersignature/README.md` :236–238 (countersignature
    d7d3c08b): a failed recurrence, `K5_INCONCLUSIVE` or a failed cell, "including cell 309 or the m = 5 tail",
    may not be claimed as evidence against H3a. Refutation needs an independently proved counterexample, such as a
    certified sup R''' < 0.
  * Theorem K5-B is **sufficient-only** (`level4/closure_proofs/p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md`).
* **The distinction preserved.**
  * *Evidence against a scientific hypothesis* would be a certified counterexample, and none exists in committed
    evidence.
  * *Inability to certify a sufficient condition* is what the open cells are.
* **No overclaim of support.**
  * This closeout asserts H3a for **no** (D, m).
  * r5 records every CUSUM cell passing for m ∈ {1, 2, 3}. But no accepted artifact assembles the full K5-B premise
    list (countersignature README §10) into an H3a claim for any (D, m).
  * Making such a claim would need a separate authorization and adjudication.

### P5Y consequence

* **Recorded P5Y state.** `level4/closure_proofs/p5y_k5_remaining_cell_closure/K5_STATUS.md` :45–58 (2026-09-19)
  records:
  * "P5Y final assembly waits on SR K1, SR K5 and CUSUM K5";
  * `P5Y_STATUS = NOT_CLOSED`.
* **Superseded detail.** That file's CUSUM K5 row (front 11–K_m open) is superseded in detail by maps r3–r5
  (front closed). Its P5Y dependency structure is not superseded.
* **Consequence of this closeout:**
  * The CUSUM K5 input to any P5Y assembly is the verdict of §5 (expected `K5_INCONCLUSIVE`), with m = 5 cells
    306–309 unresolved, on the current authoritative map r5.
  * Through K5, P5Y cannot record H3a as established for (CUSUM, m = 5), and so cannot record the K5 obligation as
    closed.
  * `P5Y_STATUS` remains **NOT_CLOSED**. This closeout changes no other P5Y obligation: K1, K4 and SR K5 are carried
    as last recorded.

## 8. Deferred research (N4.7)

**These are optional future research directions.**
* They are not required for this closeout's validity, not unfinished K5 work, and not failed or completed.
* They can be reopened only under fresh, separately authorized, prospective protocols. Any theorem, floor extension
  or admissibility ruling must be frozen before any tail recomputation (C2 Condition 1).

The ratings below are from route audit r1 §6/§9, with the r1 review's corrections.

| direction | cells | r1 label | prerequisites | scientific risk |
|---|---|---|---|---|
| RSO theory (residual-specific order-0 majorant, at most the `A0·f_H` part of `A0·p2`) | 307–309 | DEFER (research item) | theorem; U1 host, U2 admissibility, U3 floor extension for any adoption | HIGH |
| assembly / clause tightening (σ₃, σ₄, env4, f_G) | 307–309 | DEFER (research item) | theorem(s); U3 for any adoption | HIGH |
| real order-3 R stage (R-a / R-b) | 307–309 | DEFER | N1, N3, N5, N7; guard DENY; new real addresses; host | **HIGH** (r1-review N3: C2 R-stage §2 models a realistic reach of 307 only; Campaign B's T2 closed 0/5 INFEASIBLE) |
| sup-norm tightening (R5) | 307–309 | DEFER | replay plus a new sup routine; U1; U2 | HIGH |
| cover refinement (B1) | 309 (+) | DEFER | new K1 addresses; new provenance chain | MEDIUM |
| general operator-tuple search (R-E1g) | 307, 308 | INSUFFICIENT_EVIDENCE | a cell-independent certifier strategy; U1 | HIGH |
| two-implementation limb (R-F1′) | 307 | DEFER | I2 six-constant certification for 307 plus an I1 that closes | HIGH |

**Route status unchanged.** r1 REJECTED four routes as next actions: R-α, R-I2-alone, Floor-307 and X308. That
status is carried unchanged, with r1's reasons. The rejections are of *routes as actions*, not scientific failures.

**Corrections carried from the r1 review:**
* **R-I2-alone** needs no provisioned host, since I2 is exact-rational and ran locally (r1 review N2a). Its REJECT
  rests on result-chasing and evidence grounds.
* **Clauses differ.** C8's per-cell factors are under the C5-T clause, whereas floor r2's adoption quantity uses C2's
  consumer path. Every "not adoptable" statement holds even more strongly under r2's own quantity (r1 review N5).
* **U2 is an open admissibility question** requiring a governance ruling (C6 Condition 10), not a settled bar (r1
  review N6).
* **U3 (floor extension) is r2's ordinary prospective path for 307–309** (floor r2 spec :202–203), not a
  temporal-integrity defect (r1 review N1c).
* **C8 rule 1.** C8's erratum E1 records that rule 1 embeds a false premise. 306-e remains barred by the fixed fact
  "no new 306 supply" (r1 review N6).
* **Stopping preserves; it does not gain.** On information gain alone, a theory-only stage would have been narrowly
  ahead (r1 review N1a). Stopping preserves what is known; it adds no new information. The closeout was chosen on
  governance simplicity, temporal integrity and compute, and because the research can follow it without loss.

## 9. Coverage: no adoption, no mutation

* No cell may be newly adopted.
* r5 (`level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json`, blob
  `f978eeb6b41188eabaf3c6d590c9178d711f1ce6`) remains the **current authoritative coverage map**.
* No r6 is created, and no coverage entry is rewritten.
* This closeout records the state; it does not improve it.
* **If any step would mutate coverage, STOP.** That needs a different authorization.

## 10. SR K5 (N4.9)

**Verified before freeze** (`evidence/SR_K5_REFS.json`, from `code/closeout_checks.py --sr-refs`):
* A pickaxe (`git log --all -S 'SR K5'`) over every branch, remote and tag ref finds that the text was added or
  removed only by a3547b9b (2026-09-19) and by the route-audit commits on this branch.
* `K5_STATUS.md` :52 records "SR K5 | NOT STARTED".
* The latest SR K1 artifact on another ref, da79fe1f (ref `p5y-k1-successor-final-assembly`), states "READY for
  independent adjudication; K1 not decided".
* The recorded SR K5 rationale ("needs SR K1 records") may be stale in detail: SR K1 records now exist, unadjudicated.
  Its conclusion is uncontradicted.

**This adjudication concerns the CUSUM K5 disposition only.**
* SR K5 is carried over unchanged as NOT STARTED.
* SR K5 is **not** adjudicated here.
* No inference is made from CUSUM K5 to SR K5.

**If any ref shows a contradictory SR K5 state at adjudication time, STOP.**

## 11. Current-versus-final language (N4.8)

Use "current authoritative state" and "current authoritative coverage map". This closeout finalizes the **current
project phase under current governance**. It does not finalize mathematics and does not bar future, separately
authorized research.

Publication text may not contain the phrases the checker bans (`BANNED_PUBLICATION_PHRASES`, check W01). These are
overclaims of finality, impossibility, exhaustion, refutation or support of H3a, "306 failed" and "no route
exists".

## 12. Chain, roles and gates

Every role below is a fresh, independent context, distinct from every other role and from the author. Each works
read-only on the repository (git, grep, `sed -n` and the frozen checker with `--out` outside the repository). Each
puts its verdict on line 2 exactly. No reviewer output is read before its completion notification.

1. **Freeze.** One narrow commit adds:
   * this protocol;
   * `code/closeout_checks.py`;
   * `README.md` (namespace index);
   * `evidence/PREFREEZE_CHECKS.json` (all checks PASS);
   * `evidence/SR_K5_REFS.json` (PASS).
2. **Freeze review.** File `review/CLOSEOUT_FREEZE_REVIEW.md`.
   * Line 2: `CLOSEOUT_FREEZE_ACCEPTED` or `CLOSEOUT_FREEZE_REJECTED`.
   * It checks at least the 15 points of the authorization §7.
   * It is committed verbatim, alone.
   * **If REJECTED: preserve it and STOP.** There is no repair in this round.
3. **Final adjudication.** File `adjudication/K5_CUSUM_FINAL_ADJUDICATION.md`.
   * Line 2: exactly one of `K5_CLOSED`, `K5_FAIL_MATHEMATICAL`, `K5_INCONCLUSIVE`, derived mechanically by §5.
   * It must independently determine each cell's disposition (§6) with evidence.
   * It must explicitly separate four things: scientific non-certification, scientific falsification, governance
     non-adoption, and unresolved future research.
   * It must include a findings table with rows for cells 306, 307, 308 and 309, r5, r6, SR K5, CUSUM K5 and H3a,
     and columns *item | authoritative finding | evidence | consequence*.
   * If it cannot decide without computation, it STOPS and says so.
   * It is committed verbatim, alone.
4. **Adjudication review.** File `review/K5_ADJUDICATION_REVIEW.md`.
   * Line 2: `K5_ADJUDICATION_ACCEPTED` or `K5_ADJUDICATION_REJECTED`.
   * It checks at least the 16 points of the authorization §10.
   * It is committed verbatim, alone.
   * **If REJECTED: preserve it and STOP.** There is no publication.
5. **Publication**, only if step 4 is ACCEPTED. Performed by the closeout author, from the accepted adjudication
   only. The adjudication governs any disagreement.
   * Only the artifacts in §13.
   * `code/closeout_checks.py --phase publication` must PASS (including P01, P02, W01, V01), with its output
     committed as `evidence/PUBLICATION_CHECKS.json`.

## 13. Permitted publication artifacts (exhaustive)

| id | path | permitted change |
|---|---|---|
| P-A | `level4/closure_proofs/p5y_k5_partial_closeout/publication/K5_CUSUM_CLOSEOUT_STATUS.md` | new file. K5 summary and status brief, coverage explanation, limitations, research outlook, evidence/provenance table, reproducibility index |
| P-B | `README.md` (repository root) | one additive subsection "Current K5 status (CUSUM, updated 2026-09-27)", after the existing PS1 status block and before "## Limitations and negative results". Zero deleted or modified lines |
| P-C | `docs/research_synthesis/README.md` | one additive section "Current K5 successor status (additive update)", appended. Zero deleted lines |
| P-D | `docs/research_synthesis/LIMITATIONS_AND_OPEN_ITEMS.md` | one additive section "P5Y successor: CUSUM K5 open items (additive, 2026-09-27)", appended. Zero deleted lines |
| P-E | `level4/closure_proofs/p5y_k5_partial_closeout/README.md` | index update listing the chain |

No other file may change. No historical artifact is edited, and no earlier verdict is rewritten.

**Required publication wording** (authorization §12):
* **(A)** The accepted K5-level verdict, exactly. If it is `K5_INCONCLUSIVE`, publication states that this is a
  certification/adoption conclusion under the current framework, not proof that the mathematical statements are
  false.
* **(B)** Cell 306:
  * closure was certified under I1;
  * adoption failed under floor r2, because I2's own supply did not certify closure, and F2 had already failed.
* **(C)** Cells 307–309 in the scoped wording of §6, with the negative historical evidence visible.
* **(D)** Deferred research as optional, not as required K5 work.
* **(E)** H3a: failed or unresolved K5 cells are not by themselves evidence against H3a. No claim of support beyond
  committed evidence.

## 14. Historical and forensic preservation

**Historical namespaces.** They stay byte-identical to the base 2f36352e (checker H01). Pinned verdict tokens stay
present (checker H02). They cover:
* C1 and Campaign B;
* C2 through C12-R2, including C11, C11R, C11RD and N9;
* floor r2;
* the cell-306 adjudication;
* route-audit r0, its review, r1 and its review.

**Governance refs and forensic objects**, retained (checker G01, G02):
* `refs/c11rd/r1-execution-consumed`;
* `refs/c12r2/cell306-target-consumed`;
* `refs/c12r2/cell306-pending-result`;
* seal 276f4d41;
* probe blob b83cc6f5;
* trial commit def4e453.

Nothing is garbage-collected.

**External observation, not attributed to this closeout.** The ref `p5y-k4r1-nearzero-successor` moved
`5d33363c → 93d82c87` (a K4 commit, "P5Y-K4R1: candidate r5 … no target evaluated"). It is shared-repository
activity. Route audit r1 §14 recorded the earlier value.

## 15. Stop conditions

The closeout stops on any of the following:
* the starting state differs from the authorization §0;
* any checker check fails;
* the freeze review is REJECTED;
* the adjudication needs computation, or its verdict does not follow mechanically from §5;
* the adjudication review is REJECTED;
* any proposed coverage mutation or adoption;
* a contradictory SR K5 state;
* a leak-scan hit;
* any change to a historical namespace;
* any need to push, merge or synchronize main;
* any AWS or Vultr contact;
* any nonzero entry in §16.

## 16. Computation declaration (reported at every checkpoint)

| quantity | count |
|---|---|
| new Γ evaluations, cell 306 | 0 |
| new Γ evaluations, cell 307 | 0 |
| new Γ evaluations, cell 308 | 0 |
| new Γ evaluations, cell 309 | 0 |
| target-equivalent proxy evaluations | 0 |
| new scientific Monte-Carlo runs | 0 |
| new load-bearing scientific calculations | 0 |

**If any entry is nonzero: STOP and report the contamination.**
