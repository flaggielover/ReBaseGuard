# K5 PARTIAL closeout protocol, successor R2: CUSUM K5, m = 5 tail cells 306–309

**Status: FROZEN** by the unique commit that adds this file; checker I01 finds that commit and enforces blob identity
of every frozen file (§13) before adjudication and before publication.

**No scientific computation is authorized.** No Γ; no target-equivalent proxy; no Monte-Carlo science; no new
interval/certificate; no supply search; no optimization; no floor or limb; no adoption; no coverage map created or
modified.

---

## 0. Rejection history (both preserved, neither rewritten)

| freeze | review | verdict | blocker in one line |
|---|---|---|---|
| 08e9acd176aea4351425c169d2eac723d0a2208b (`level4/closure_proofs/p5y_k5_partial_closeout/`) | 591b43948a07e5fd916de37b3ef4d38830bb7b94 (`level4/closure_proofs/p5y_k5_partial_closeout/review/CLOSEOUT_FREEZE_REVIEW.md`) | **CLOSEOUT_FREEZE_REJECTED** | B1: K1/P5Y read from a remembered commit, not the current ref tip |
| dfcd8f79ee90ffbb5d04ada43eb7ffd10b44013d (`level4/closure_proofs/p5y_k5_partial_closeout_r1/`) | 0d275038fe60252915691df45a31904b27f34c0f (`level4/closure_proofs/p5y_k5_partial_closeout_r1/review/CLOSEOUT_FREEZE_REVIEW_R1.md`) | **CLOSEOUT_FREEZE_REJECTED** | B1: binding re-read keyed to three remembered branch names, no new-ref / ambiguity detection; B2: wording scan weaker than the predecessor |

Each review is authoritative for its freeze. Under neither freeze did an adjudication, a publication closeout or any
scientific computation occur. Both namespaces stay byte-identical to the R2 base (checker H01) with their verdict
tokens pinned (H02). **R2 is a new prospective repair** in `level4/closure_proofs/p5y_k5_partial_closeout_r2/`,
authorized by the user's "K5 PARTIAL Closeout Successor Freeze R2". The route audit r1
(`level4/closure_proofs/p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md`, 802be11e; review 2f36352e ROUTE_AUDIT_ACCEPTED)
remains the fixed foundation: no prospective K5 scientific expansion under present governance.

### R2 repair table — every blocker and note of both reviews

| source review | item | issue | R2 repair | verification |
|---|---|---|---|---|
| 591b4394 | B1 | stale cross-ref K1/P5Y text; nothing forced a correction | repository-wide, content-based ref discovery (§5); frozen snapshot; mechanical diff with STOP classes before adjudication and before publication | `--snapshot` → `evidence/REF_SNAPSHOT_R2.json`; `--diff` → the pre-adjudication / pre-publication ref-diff files |
| 591b4394 | N1 | judgment-based rule limbs; `K5_CLOSED` vs `K5_DECLARED_CLOSED` | mechanical limbs (§6.2); `K5_CLOSED` defined here as a CUSUM-scoped token, distinct from the K5-wide flag | text; review |
| 591b4394 | N2 | weak SR text search | SR-K5 spellings are part of the carrier regex; `-G` catches in-place edits; exemption only for this closeout's namespaces on this branch | `config/REF_RULES_R2.json`; snapshot |
| 591b4394 | N3 | one SR prerequisite carried | both carried (§11) | H03; snapshot `SR_K5` |
| 591b4394 | N4 | C4 Condition 2 misattribution | attributed per source (§7, 308) | review |
| 591b4394 | N5 | C1 / Campaign B / C11 history omitted | carried (§7) | H02 pins |
| 591b4394 | N6 | thin publication controls | exact allowlist incl. ignored files (P01); frozen public-file edit rules (P02/P03); R2 wording scan (W01/T01); publication-conformance check (§12) | checker |
| 591b4394 | N7 | "verbatim" helpers | "code-identical (AST, docstrings ignored)" | L03 |
| 591b4394 | N8 | role wording | §12 separates reviewers / adjudicator from the publication author | text |
| 591b4394 | N9 | no PARTIAL / INCONCLUSIVE / OPEN mapping | §6.1 | text |
| 0d275038 | **B1** | re-read hard-coded to three branch names; no new-ref search; no snapshot comparison; no ambiguity class | **every ref is enumerated** (branches, remote-tracking refs, annotated tags peeled, tree refs, governance refs); relevance is decided **by content** (status-carrier files from one `git log --all -G` pass, inventoried at every tip); owner records are parsed and the obligation table **computed**; the diff classifies unchanged / moved / new / deleted / renamed-equivalent refs, inspects every commit new since the snapshot, and stops on STOP_AMBIGUOUS_CROSS_REF_STATE, incompatible drift, conflicting live records, missing binding records, positive closure flags or discovery errors | `--diff`; §5.2 |
| 0d275038 | **B2** | wording scan weaker than the predecessor | predecessor phrases restored as an **absolute tier P** (read from the predecessor checker blob, incl. "all routes exhausted"); R1 patterns kept as **tier L** with proposition-local negation; whitespace and hard wraps normalized first; 41 adversarial fixtures incl. the exact R1 false negative; mechanical **no-weakening test** on a 276-sentence corpus (R2 ⊇ predecessor; R2 ⊇ R1) | T01; `config/WORDING_RULES_R2.json`, `config/WORDING_FIXTURES_R2.json` |
| 0d275038 | N1 | no post-freeze immutability | I01: every frozen file byte-identical (freeze blob = HEAD blob = worktree hash) and untouched after the freeze commit | I01 |
| 0d275038 | N2 | drift not mechanical; crash on bad JSON | the diff recomputes the obligation table and compares it with the snapshot; any exception becomes STOP_DISCOVERY_ERROR, with output | `--diff` |
| 0d275038 | N3 | narrow closure-flag search | positive-closure-flag regex widened (`"P5Y": "CLOSED…` prefix, `K5_COVERAGE_COMPLETE` true, `K5_STATUS (CUSUM) = CLOSED`, `K5 = CLOSED`, `K5 CLOSED_BY`) and applied to every carrier blob on every tip; coverage maps found by content (`coverage-map.vN` schema) | snapshot `positive_closure_flags` |
| 0d275038 | N4 | "all refs" meaning | all 134 refs enumerated by namespace; tree refs searched with `git grep` | snapshot `refs` |
| 0d275038 | N5 | scope of "only open P5Y obligation" | stated as "the only open one of K1–K5 as recorded in the P5Y summary" (§8) | text |
| 0d275038 | N6 | stale public K1 text | §14: four stale lines in allowlisted files replaced in place by a frozen correction form; two stale lines in `docs/research_synthesis/PS1_CURRENT_STATUS.md` (not allowlisted) left unchanged and reported | P02, P03, T02 |
| 0d275038 | N7 | K2/K3 bound only by countersignature tokens | K2/K3 computed from `status.K2/K3` together with countersignature PASS | snapshot obligations |
| 0d275038 | N8 | `K5_CLOSED` scope source | §6.2 states that the CUSUM scope is this protocol's own definition | text |
| 0d275038 | N9 | fail-closed false positives | accepted by design (tier P absolute); publication text must avoid tier-P phrases even when negated | T01 fixtures |
| 0d275038 | N10 | P01 counts ignored files repo-wide | kept (fail-closed); the tree must be clean | P01 |
| 0d275038 | N11 | "SR K1 satisfied in substance" | worded as an inference (§11) | text |

**Retained from R1:** OPEN / PARTIAL / K5_INCONCLUSIVE mapping; N4.1–N4.9; mechanical rule limbs; multi-spelling SR
discovery; C4 attribution; negative history; exact allowlist; publication-conformance step; AST helper identity; H3a
non-refutation rule; 306–309 scoped wording; r5 / no-r6; deferred research.

## 1. Scope

The K5 obligation for D = CUSUM, m ∈ {1, 2, 3, 5}, frozen CUSUM K1 cover cells 0–309 meeting (0, 2]
(`level4/closure_proofs/p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md` :89), in particular m = 5
cells 306–309. Out of scope: SR K5 (reported, not adjudicated); K1–K4 and P5Y assembly (reported from the computed
cross-ref state, not adjudicated); AWS SR/PS1.

## 2. Question

> Given the current authoritative evidence and the accepted prospective route audit, what is the correct current
> disposition of CUSUM K5 and of each of cells 306–309?

## 3. Evidence and fact classes (N4.1)

Any committed artifact on this branch, and committed artifacts on other refs **located by content discovery at their
current tips**. Each citation keeps its governance status and evidence type; uncertified evidence may be reported but
never used for an authoritative exclusion or closure. Forbidden: C11R quarantine; D1/D2 values; session transcripts.
**Class A** (frozen local facts): K5 historical evidence, r5, cell dispositions, route audit, both rejected closeouts,
the R2 frozen files. **Class B** (cross-ref facts): everything computed by §5.

## 4. Administrative versus scientific (N4.2)

Allowed: git read operations (`for-each-ref`, `log -G`, `ls-tree`, `grep`, `cat-file`, `rev-list`, `reflog`,
`merge-base`), hashes, blob identity, JSON reads of status records, the value-free leak scan, citation / format /
allowlist / public-edit / stale-line / wording checks, and `docs/research_synthesis/verify_synthesis.py --no-diff-check`
(blob d2411ab805e3bc58ba1d77a6894c3fa67da005fd) in the publication phase. **The only code the closeout runs is
`code/closeout_checks_r2.py` (stdlib + read-only git; reads `config/*.json`; imports no campaign module), that
verifier, and git.** Forbidden: every scientific computation listed at the top.

## 5. Repository-wide relevant-ref discovery (B1)

### 5.1 Method (frozen in `config/REF_RULES_R2.json`)

1. **Enumerate every ref** with `git for-each-ref`: branches, remote-tracking refs, lightweight and annotated tags
   (peeled), tree-valued refs (`refs/codex/…`) and the governance refs.
2. **Find status carriers by content:** one pass `git log --all -G <carrier_regex> --name-only -- level4 docs
   README.md` yields every path whose history ever added or removed K1/K2/K3/K4/K5/P5Y/SR-K5 status text. Branch
   names are never used to decide relevance.
3. **Inventory every commit tip** over those paths (`git ls-tree`), and every tree ref with `git grep`.
4. **Owner records** (the records that own an obligation's state: K1 successor final adjudication; K2/K3 final
   countersignature; K4R1 final verdict; historical K4 execution result; `K5_STATUS.md`; r5) are parsed wherever found.
   For each owner path the live versions across all tips are resolved by lineage: the version whose introducing commit
   descends from every other version's is current, otherwise **conflict**. The historical K4 record is superseded by
   the K4R1 record only when the latter's `HISTORICAL_K4_COMMIT` descends from the commit that introduced the former.
   The P5Y summary is the newest live summary (K2/K3 `status`, historical K4 `p5y_state`, K4R1 `P5Y_STATE`) and must
   agree with the K1–K4 owner records.
5. **The obligation table is computed** from those records, never hard-coded, and every carrier blob is searched for a
   positive closure flag.
6. **Each ref is classified**: binding (carries a current binding owner record), informational (carries status text
   only in superseded, summary or historical form), unrelated (no carrier), or governance.

**At freeze** (`evidence/REF_SNAPSHOT_R2.json`, observation time inside): the table computed from the records is K1
CLOSED, SR K1 CLOSED, K2 CLOSED, K3 CLOSED, K4 CLOSED, K5 OPEN, P5Y NOT_YET_CLOSED, SR K5 NOT STARTED, CUSUM K5
coverage incomplete with union open [[306, 309]]; verdict CONTINUE. The snapshot lists every ref with tip, obligations
represented, owner records present and class, and the current owner-record versions with their live tips and
introducing commits. At the observation, the K1 record is live at `refs/heads/p5y-k1-successor-final-assembly` (and its
origin copy), the K2/K3 record at `p5y-k2-k3-final-closure`, the K4R1 record at `p5y-k4r1-final-closure`, and
`K5_STATUS.md` on every ref that carries it. These locations are **observations**, not the method.

### 5.2 Post-freeze drift algorithm (`--diff`, mandatory before adjudication and before publication)

* Re-enumerate all refs; classify each as unchanged, moved, new, deleted, or renamed-equivalent (a new name whose
  object equals a deleted ref's frozen object).
* List every commit reachable from a current ref but not from any frozen tip that touches a status carrier (by `-G` or
  by path).
  * A file inside this closeout's own namespaces, on this branch, is exempt.
  * In the publication phase the three allowlisted public files are also exempt.
  * A touched **owner record** is re-parsed and recompared.
  * **Any other touched carrier ⇒ STOP_AMBIGUOUS_CROSS_REF_STATE.**
* A new or changed tree ref is grepped; a carrier blob not in the snapshot ⇒ STOP_AMBIGUOUS_CROSS_REF_STATE.
* Recompute the owner-record resolution and the obligation table over the current tips:
  * conflicting live versions ⇒ **STOP_CONFLICTING_LIVE_RECORDS**;
  * a binding owner record with no live version ⇒ **STOP_MISSING_BINDING_RECORD**;
  * an obligation table different from the snapshot ⇒ **STOP_INCOMPATIBLE_BINDING_DRIFT**;
  * a new positive closure flag ⇒ **STOP_POSITIVE_CLOSURE_FLAG**;
  * any exception ⇒ **STOP_DISCOVERY_ERROR**.
* Moved or renamed refs, and changed live-tip sets of binding records, whose recomputed table is identical and which
  raised no stop are **COMPATIBLE_DRIFT**. They are recorded in the diff file and carried into the adjudication table.
* **Fail-closed rule (mechanical):** any unexplained new relevant ref or carrier, incompatible movement of a binding
  ref, or unresolved conflict among live relevant records gives a verdict other than CONTINUE, and the closeout stops
  before adjudication (or before publication).

### 5.3 Drift self-test (frozen evidence)

`code/drift_selftest_r2.py` (administrative) builds a throwaway `git clone --shared --no-checkout` of this repository in
a temporary directory **outside** the repository, takes an R2 snapshot there, injects one scenario at a time into the
clone's refs only, runs `--diff`, and restores the clone. The real repository's refs are never written; the clone is
deleted afterwards. Required outcomes (recorded in `evidence/DRIFT_SELFTEST_R2.json`):

| scenario | expected |
|---|---|
| S0 no change | CONTINUE |
| S1 new ref with an unknown status carrier | STOP_AMBIGUOUS_CROSS_REF_STATE |
| S2 binding ref moved to a commit that changes the K4 verdict | STOP_INCOMPATIBLE_BINDING_DRIFT / STOP_CONFLICTING_LIVE_RECORDS |
| S3 binding ref moved to a commit that touches no carrier | CONTINUE (COMPATIBLE_DRIFT) |
| S4 every ref carrying the K1 record deleted (branches and tags) | STOP_MISSING_BINDING_RECORD |
| S5 the K1 record's refs replaced by a renamed branch at the same commit | CONTINUE (renamed-equivalent) |
| S6 a divergent second version of the K1 record on a new ref | STOP_CONFLICTING_LIVE_RECORDS |
| S7 a new tag at an already-frozen commit | CONTINUE |
| S8 a new tree ref containing an unknown status carrier | STOP_AMBIGUOUS_CROSS_REF_STATE |
| S9 a known historical carrier edited to a positive closure flag | STOP_AMBIGUOUS_CROSS_REF_STATE / STOP_POSITIVE_CLOSURE_FLAG |

## 6. Vocabulary and decision rule

### 6.1 OPEN / PARTIAL / K5_INCONCLUSIVE (repository definitions first)

| term | level | repository source | meaning here |
|---|---|---|---|
| OPEN | cell; P5Y obligation | r5 `per_m.<m>.open_ranges`; P5Y summaries (`"K5": "OPEN"`) | a cell is OPEN iff it lies in r5's `open_ranges`; an obligation is OPEN iff not recorded closed |
| PARTIAL | coverage status of CUSUM K5 | `level4/closure_proofs/p5y_k5_remaining_cell_closure/K5_STATUS.md` :4–5; r5 `K5_COVERAGE_COMPLETE` false | only a subset of the required (m, cell) pairs is established; a coverage description, not a verdict |
| K5_INCONCLUSIVE | adjudicated CUSUM-K5 verdict | E01 :91 ("otherwise unresolved cells ⇒ `K5_INCONCLUSIVE`") | the framework does not establish the required closure for all required cells, and unresolved cells are not read as mathematical refutation |

Relation: coverage PARTIAL (cells OPEN) with no certified counterexample ⇒ the §6.2 rule yields `K5_INCONCLUSIVE`; the
P5Y obligation K5 then remains OPEN. The three terms are not interchangeable and are never applied at another term's
level.

### 6.2 Rule (CUSUM K5, mechanical, in order)

1. **`K5_FAIL_MATHEMATICAL`** iff a committed artifact whose own recorded verdict is accepted records either a
   certified `R'''_cell.hi < 0` on a CUSUM cell containing 0 (E01 :91), or a declared refutation of H3a for
   (CUSUM, m) (the standard of `level4/closure_proofs/p5y_k5b_independent_countersignature/README.md` :236–238).
2. **else `K5_CLOSED`** iff r5 records `K5_COVERAGE_COMPLETE = true` **and** a committed accepted adjudication records
   CUSUM K5 closed.
3. **else `K5_INCONCLUSIVE`.**

`K5_CLOSED` is a CUSUM-scoped token **defined by this protocol**. The repository uses the token without scoping it
(e.g. `level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment/adjudication/ADJUDICATION_C11R_N9.md` :144). It is
not the K5-wide flag `K5_DECLARED_CLOSED`, which this closeout never sets. `K5_INCONCLUSIVE` is never applied to a cell.

**Pre-freeze reconstruction (non-binding):**
* limb 1 does not fire: `level4/closure_proofs/p5y_k5_cusum_first_real_probe_result/RESULT.md` records
  `FIRST_CELL_SUPPORTED_ALL_M`, and no committed artifact refutes H3a;
* limb 2 does not fire: r5 records `K5_COVERAGE_COMPLETE = false`;
* hence `K5_INCONCLUSIVE`.

## 7. Cell dispositions (Class A; the adjudicator confirms or corrects)

**306 — OPEN, NOT ADOPTED.** These facts coexist:
* Closes under I1's supply: Γ(5, 306; S_I1) = −0.030469257709306738
  (`level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md` :47).
* Not certified under I2's own supply: Γ(5, 306; S_I2) = +0.005159101140006536, sealed once at 276f4d41;
  EXECUTION_ACCEPTED at 1173670f. This is non-certification, not disproof.
* N9 CLOSED (7d67989d; ADJUDICATION_ACCEPTED fb237288) is a trust condition only.
* Floor r2 not met:
  * base TRUE;
  * F1′ (a)–(c) TRUE, (d) FALSE;
  * F2 FALSE (C2 §K: ×1.25 → +0.029163293, margin 1.1277; C2 adjudication :65, :474–478).
* `level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/adjudication/C12R2_ADOPTION_ADJUDICATION.md` records
  CELL306_NOT_ADOPTED (9c2cbf21), with ADJUDICATION_ACCEPTED (c5324a78).

**307 — OPEN. "No route that closes 307 has been certified."**
* Certified supplies evaluated at 307 did not close it:
  * C2 D4 (C2 adjudication :48);
  * C3 D′ (`level4/closure_proofs/p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md` :349).
* Earlier failed attempts: C1 MARGINAL; Campaign B MARGINAL / INFEASIBLE; C11 EXECUTION_INVALID (a failed
  corroboration).
* Blocker structure:
  * (A1, A2) is material and A0 is not the blocker (C3 :349;
    `level4/closure_proofs/p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md` :288–290);
  * no committed closing supply;
  * F1′ is unavailable (floor r2 spec :193).
* Reported, not load-bearing: the C9 α projection (uncertified) and the C8 factors (COUNTERFACTUAL_ONLY, C5-T clause).
* UNKNOWN: every uncertified route.

**308 — OPEN.**
* Ruled out (certified): improving only (A1, A2) at the certified A0 (knockout Γ = +0.039568, C3 :350).
* C4 Condition 3, verbatim (C4 adjudication :534–537):

  > at `A0 = 4.311`, the Monte-Carlo value of `Λ₃₀₈`, closing cell 308 still requires an **18.2× reduction of
  > `(A1, A2)`**; at `A0 = 4.375229` it is impossible at any `(A1, A2)`. C4-N3 stands and is binding: nothing licenses
  > "cell 308 is closable".

* C4's status wording (verdict :510–512) is "operator-level route not excluded". C4 Condition 2 (:527–533) bars the
  Phase-3 sentence "the honest answer is that none can" and the Lemma T citation.
* Uncertified Monte-Carlo evidence (2,000,000 paths, ~65 SE) suggests no lower-bound route excludes 308. It is reported,
  **not** an exclusion. No certified upper bound on Λ₃₀₈ exists.
* UNKNOWN: everything not ruled out.

**309 — OPEN.**
* Refuted only within C4 Condition 1's scope: the uniform-A0 atom-constant family, cell 309, m = 5, the frozen
  measurement inputs and the frozen TC-T / K5-B consumer (C4 :522–524).
* Strengthened by C7's certified Λ₃₀₉ ≥ 3.586306094 (`level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309/README.md`),
  which exceeds the C5-T-clause ceiling 3.266416 by 9.79 %.
* C4 :503: the exclusion does not show cell 309 to be unclosable.
* UNKNOWN outside the scope: sup-norm routes, finer cover, real order-3, assembly / clause tightening,
  residual-specific routes, other independent theory.

**Other cells:** as r5 records them.

## 8. H3a and P5Y consequence

* **H3a:**
  * Failed or unresolved K5 cells are not, by themselves, evidence against H3a (countersignature README :236–238).
  * K5-B is sufficient-only (`level4/closure_proofs/p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md`).
  * Evidence against a hypothesis (a certified counterexample, none committed) is distinct from the inability to
    certify a sufficient condition.
  * No support is claimed: this closeout asserts H3a for no (D, m).
* **P5Y:**
  * Computed from the owner records and the newest live P5Y summary at the re-read (§5).
  * If the re-read table equals the snapshot's (K1, K2, K3, K4 closed; K5 OPEN; P5Y NOT_YET_CLOSED), then K5 is the
    only open one of K1–K5 as recorded in the P5Y summary.
  * `K5_INCONCLUSIVE` does not close K5, and SR K5 is NOT STARTED on its own record.
  * The recorded vocabulary therefore stays **K5 OPEN, P5Y NOT_YET_CLOSED**.
  * K5 is upstream of T9/T10 and Level-4 closure in `level4/closure_proofs/p5y_postk1_frontier/P5Y_POST_K1_DAG.md`
    (:60, :75, :97–102).
  * No P5Y verdict is issued, and no P5Y assembly rule is invoked beyond these records.

## 9. Deferred research

These directions are optional, not required for this closeout, and neither failed nor completed.

| direction | status |
|---|---|
| RSO theory | DEFER |
| assembly / clause tightening | DEFER |
| real order-3 R stage | DEFER; **scientific risk HIGH**; N1, N3, N5, N7; guard DENY |
| sup-norm tightening | DEFER |
| cover refinement | DEFER |
| general operator-tuple search | INSUFFICIENT_EVIDENCE |
| two-implementation limb | DEFER |

Each is reopenable only under fresh prospective authorization, which freezes any theorem, floor extension or
admissibility ruling before recomputation (C2 Condition 1). Route audit r1 rejected R-α, R-I2-alone, Floor-307 and
X308 as actions; these are not scientific failures.

## 10. Coverage

* No adoption.
* r5 (blob `f978eeb6b41188eabaf3c6d590c9178d711f1ce6`) remains the **current authoritative coverage map**.
* No r6, and no coverage entry is rewritten.
* Any step that would mutate coverage ⇒ STOP.

## 11. SR K5

* **State: NOT STARTED** (`level4/closure_proofs/p5y_k5_remaining_cell_closure/K5_STATUS.md` :52; computed as `SR_K5`
  in the snapshot).
* **Recorded prerequisites:**
  * (i) SR K1 records — **by inference** now met in substance, since the K1 successor adjudication covers SR
    (`sr_successor_science` PASS);
  * (ii) an SR order-3 producer — **still missing**
    (`level4/closure_proofs/p5y_k1_sr_o9_aux3_successor/config/AUX3_SR_RECORD.json`, `AUX3_SR_FEASIBILITY_FAIL`).
* **Handling:** SR K5 is carried unchanged, not adjudicated, not counted as a CUSUM K5 blocker, and not declared
  complete. Nothing is inferred from CUSUM K5 to SR K5.

## 12. Chain, roles and gates

**Roles.**
* Four distinct fresh contexts, none of them the author: the freeze reviewer, the adjudicator, the adjudication
  reviewer and the publication-conformance checker. Each is read-only and puts its verdict on line 2.
* The publication author is the closeout author, writing only from the accepted adjudication.
* No reviewer output is read before its completion notification.

**Steps.**
1. **Freeze** — one commit adding exactly the frozen files (§13).
2. **Freeze review** → `review/CLOSEOUT_FREEZE_REVIEW_R2.md` (`CLOSEOUT_FREEZE_ACCEPTED` / `CLOSEOUT_FREEZE_REJECTED`),
   committed verbatim alone. **REJECTED ⇒ preserve and STOP: no same-round repair, no adjudication, no publication.**
3. **Pre-adjudication gate:**
   * `--phase adjudication` (incl. I01 identity) → `evidence/PREADJUDICATION_CHECKS_R2.json`;
   * `--diff evidence/REF_SNAPSHOT_R2.json --diff-phase adjudication` → `evidence/PREADJUDICATION_REF_DIFF_R2.json`.

   Any failure, or a diff verdict other than CONTINUE ⇒ STOP.
4. **Final adjudication** → `adjudication/K5_CUSUM_FINAL_ADJUDICATION_R2.md`.
   * Line 2 is exactly `K5_CLOSED`, `K5_FAIL_MATHEMATICAL` or `K5_INCONCLUSIVE`, per §6.2.
   * It separates scientific non-certification, scientific falsification, governance non-adoption and unresolved
     future research.
   * It has a findings table (*item | authoritative finding | evidence | consequence*) with rows 306, 307, 308, 309,
     r5, r6, K1, K2/K3, K4, P5Y, SR K5, CUSUM K5 and H3a. The cross-ref rows come from the step-3 diff, recording any
     COMPATIBLE_DRIFT.
   * If computation would be needed, it STOPS.
   * Committed verbatim with the step-3 files.
5. **Adjudication review** → `review/K5_ADJUDICATION_REVIEW_R2.md` (`K5_ADJUDICATION_ACCEPTED` /
   `K5_ADJUDICATION_REJECTED`), committed alone. **REJECTED ⇒ preserve and STOP.**
6. **Pre-publication gate:** `--diff … --diff-phase publication` → `evidence/PREPUBLICATION_REF_DIFF_R2.json`. A
   verdict other than CONTINUE ⇒ STOP.
7. **Publication** (only after step 5 ACCEPTED):
   * the author writes the §14 artifacts;
   * `--phase publication` must pass;
   * a fresh **publication-conformance check** reads the uncommitted diff → `review/PUBLICATION_CONFORMANCE_R2.md`
     (`PUBLICATION_CONFORMANT` / `PUBLICATION_NONCONFORMANT`).

   CONFORMANT ⇒ commit, with `evidence/PUBLICATION_CHECKS_R2.json`. NONCONFORMANT ⇒ commit only the conformance review,
   leave the publication files unchanged, and STOP.

## 13. Frozen files, exact allowlist, identity

**Frozen files (I01):**
* `README.md` (the namespace README; may change again only in the publication phase);
* `protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL_R2.md`;
* `code/closeout_checks_r2.py`;
* `code/drift_selftest_r2.py`;
* `config/REF_RULES_R2.json`;
* `config/WORDING_RULES_R2.json`;
* `config/WORDING_FIXTURES_R2.json`;
* `config/PUBLICATION_ALLOWLIST_R2.json`;
* `evidence/REF_SNAPSHOT_R2.json`;
* `evidence/PREFREEZE_CHECKS_R2.json`;
* `evidence/DRIFT_SELFTEST_R2.json`.

**Exact allowlist:** `config/PUBLICATION_ALLOWLIST_R2.json` lists every path that may differ from the base 0d275038
(tracked, untracked and ignored), per phase. Its `namespace_files` are keyed by phase, and its three `public_files`
are allowed only in the publication phase. Anything else fails P01.

## 14. Publication artifacts, stale public K1 text, required wording

| id | path | permitted change |
|---|---|---|
| P-A | `level4/closure_proofs/p5y_k5_partial_closeout_r2/publication/K5_CUSUM_CLOSEOUT_STATUS.md` | new status brief (verdict, dispositions, coverage, K1/K2/K3/K4/K5/P5Y, SR K5, H3a, research outlook, evidence/provenance table, reproducibility index) |
| P-B | `README.md` | one block starting `### Current K5 status (CUSUM, updated 2026-09-27)` between `## Current successor status (PS1)` and `## Limitations and negative results`, plus the stale-line corrections below |
| P-C | `docs/research_synthesis/README.md` | one block starting `## Current K5 successor status (additive update)`, appended, plus the stale-line corrections below |
| P-D | `docs/research_synthesis/LIMITATIONS_AND_OPEN_ITEMS.md` | one block starting `## P5Y successor: CUSUM K5 open items (additive, 2026-09-27)`, appended |
| P-E | `level4/closure_proofs/p5y_k5_partial_closeout_r2/README.md` | index update |

**Stale current-facing K1 text.** The frozen list is `stale_lines` in `config/PUBLICATION_ALLOWLIST_R2.json`:

| file | line | text | recorded |
|---|---|---|---|
| README.md | :134 | "- **NOT_CLOSED.**" (the PS1/SR bullet) | 2026-09-13 |
| README.md | :137 | "K1 and P5Y remain NOT CLOSED" | 2026-09-16 |
| synthesis README | :158 | PS1/SR "… NOT_CLOSED" | 2026-09-13 |
| synthesis README | :160 | "K1 is NOT_CLOSED" | 2026-09-16 |

* Each is **replaced in place** by one line of the frozen correction form, keeping the historical claim and its date
  (P02, P03):

  > Historical status (as recorded <date>): <claim>. Superseded (2026-09-27) … by K1_SUCCESSOR_CLOSED
  > (CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN), `level4/closure_proofs/p5y_k1_successor_final_adjudication/evidence/FINAL_ADJUDICATION.json`
  > at ref `p5y-k1-successor-final-assembly` (<tip>) …

* No other existing line changes.
* `docs/research_synthesis/PS1_CURRENT_STATUS.md` :8 and :42 are stale but **not allowlisted**. They stay unchanged
  here (H01), are reported, and are named as superseded in blocks P-B and P-C. Editing them needs a separate
  authorization.
* Historical campaign records are never edited.

**Required content:**
* **(A)** The accepted CUSUM K5 verdict exactly. If it is `K5_INCONCLUSIVE`, say that it is a certification/adoption
  conclusion under the current framework, not proof that a mathematical statement is false.
* **(B)** 306: closure certified under I1; adoption not reached under floor r2, because I2's own supply did not certify
  closure and F2 had already failed.
* **(C)** 307–309 in §7's scoped wording, with the negative history visible.
* **(D)** r5 is the current authoritative map; no r6.
* **(E)** K1, K2/K3, K4 and P5Y as computed at the re-read; SR K5 separate.
* **(F)** H3a is not refuted by unresolved cells; no support claimed.
* **(G)** Deferred research is optional and reopenable.

All publication-facing text must pass W01. Tier-P phrases are rejected even when negated.

## 15. Preservation

* **Byte-identical to 0d275038 (H01):** the historical namespaces — C1, Campaign B, C2–C12-R2 (incl. C11, C11R,
  C11RD and N9), floor r2, the cell-306 adjudication, route audit r0/r1 and their reviews, both rejected closeouts —
  and `docs/research_synthesis/PS1_CURRENT_STATUS.md`.
* **Verdict tokens pinned (H02).**
* **Retained (G01, G02):**
  * `refs/c11rd/r1-execution-consumed`;
  * `refs/c12r2/cell306-target-consumed`;
  * `refs/c12r2/cell306-pending-result`;
  * seal 276f4d41;
  * blob b83cc6f5;
  * commit def4e453.
* External ref movements appear in the snapshot and diff as observations, not attributed.

## 16. Stop conditions

The closeout stops on any of the following:
* the starting state differs;
* any checker check fails;
* the freeze review is REJECTED;
* I01 fails;
* the diff verdict is not CONTINUE;
* the adjudication needs computation, or its verdict does not follow from §6.2;
* the adjudication review is REJECTED;
* the publication check is NONCONFORMANT;
* any adoption or coverage mutation;
* a leak-scan hit;
* a historical namespace changed;
* a push, merge or main sync would be needed;
* any AWS or Vultr contact;
* any nonzero entry in §17.

## 17. Computation declaration

| item | count |
|---|---|
| new Γ evaluations, 306 | **0** |
| new Γ evaluations, 307 | **0** |
| new Γ evaluations, 308 | **0** |
| new Γ evaluations, 309 | **0** |
| target-equivalent proxies | **0** |
| scientific Monte-Carlo | **0** |
| new load-bearing intervals / certificates | **0** |
