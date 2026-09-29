# Firewalled reader B: governance and formal-campaign conventions (verbatim hand-back, condensed layout)

Reader: firewalled subagent. Read-only, and it ran no repository code. Its report contains no 305–309 numbers; its
own exposures are ledgered in `ledger/EXPOSURE_LEDGER.jsonl`. Repository state it saw: 52e00290 → 1f6b724a. There is
no committed cell-308 formal namespace and no 308 ref, locally or on origin.

## 1. Floor r2

* **Status.** Proposed at a15d083b. In force since REPLACEMENT_FLOOR_ACCEPTED at 3fadb422.
* **Base clause** (FLOOR_R2_SPECIFICATION.md:54-55): the frozen K5-B certifies it with "Γ < 0 under the campaign's
  own frozen closure rule, evaluated on the campaign's chosen supply", plus F1′ or F2.
* **Chosen supply** (:57-60): a single-implementation supply, the componentwise minimum (C2's D4 rule) over Lemma G and
  Lemma Dv′ r2 from one operator-constant implementation. It is never mixed and is frozen before any evaluation.
* **F1′** (:62-69): two independent implementations of the six constants; a frozen N9 comparison with AGREES/STRONGER
  or EQUIVALENT/STRONGER outcomes, independently accepted; soundness evidence for each; and Γ < 0 for each separately.
  It is UNAVAILABLE at 309 (ROUTE_AUDIT_R1.md:308-309).
* **F2** (:71-72): Γ < 0 survives the r1 uniform unfavourable degradation of all atom constants.
* **Adoption quantity** (JSON line 76): the exact rational from C2's frozen consumer path. The pinned pieces are
  c2_d5_forecast 18403dbe, deflated_consume a0a836fa and tct_rule 98f6eee4, together with the k5b_literal direct clause.
  Only S is substituted. The sign is strict; Γ = 0 or an incomplete evaluation fails. The K1 stack, the Lemma G
  inputs, the TC-T premises and cells.json are fixed.
* **Closure vs adoption** (:204-212):
  * scientific closure is Γ < 0 under the frozen K5-B clause;
  * adoption is closure, plus F1′ or F2, plus the full governed chain.
* **Closure-only routes** (ROUTE_AUDIT_R1:328-332): a route that changes the consumer or other inputs is closure-only
  (RSO, R-asm, R4, R5, B1).
* **Fail-closed** (:168-186): any failure means DO NOT ADOPT, and the cell stays OPEN.
* **U3 requirements:**
  * C2 Condition 1: freeze any replacement floor before recomputing any magnitude;
  * C10: a successor MAY freeze a different prospective adoption rule, and it must answer IMPLEMENTATION INDEPENDENCE;
  * KG-U3: the extension is user-instructed, frozen and reviewed before Stage 1;
  * "Floor-307"-style fitted floors are REJECTED (HIGH result-chasing).
* **Consequence for 309:** every route that could close 309 is closure-only, and adoption needs U3.
* **Driver precedent.** Floor-r2 review N6: freeze a single-cell driver that reuses `direct`, `combine`,
  `atom_constants_r2` and `atom_constants_generic`, as the 307 campaign did. Review N5: `tail_forecast_r2` is loaded
  unpinned by c2_d5_forecast, so pin it.

## 2. Pending user decisions: none decided

| decision | content | source |
|---|---|---|
| U1 | host provisioning (C6 Condition 7). No certifying host is in scope, and the vultr-02 record is unreconciled. Local exact-arithmetic routes need no U1 | review N2a |
| U2 | admissibility of new quantities derived from P3 tail records (C6 Condition 10: "No P3 object may be adopted as new scientific evidence"). A ruling is needed before any Stage-1 freeze (KG-U2) | — |
| U3 | a floor extension for closure-only routes | — |

Other items that need a user decision:
* acknowledgement of the incident disclosures (01–03 and 309R1-01/02);
* the TPT-at-309 decision (309R1-01);
* the cell set;
* a separate grant after QUALIFICATION_ACCEPTED;
* any new real computation (guard DENY; N1/N5/N7);
* push and merge.

## 3. Formal-campaign anatomy (p5y_k5_cell307_rlr_r1)

1. Start-state verification (20/20). Reviewer F5 says to widen the detectors (content-based, all refs).
2. Provenance timeline, ordered by commit.
3. Coordinator incident audit, which is not independent.
4. Independent incident review, INCIDENT_AUDIT_ACCEPTED with C1–C6.
5. Addendum, latent-proxy amendment, and briefs committed or hashed.
6. Theorem document: the soundness claim with its one assumption (§3), and the limits (§4).
7. Freeze manifest: caps, certifier pins, consumer/input pins, driver sha, exactly-once names, frozen files, governance
   anchors, outcome table, route, scope, Stage-1 rules, Stage-2 criterion.
8. Qualification cases, all non-target:
   * committed-block reproduction and decoy Stage 1;
   * determinism, including cross-run;
   * independent Monte Carlo;
   * two-sided assembly mutants, κ, guard/arming, cell-305 reproduction, S construction;
   * 39 exactly-once sandbox flows;
   * AST static structure, leak scan, temporal state.
9. Gates Q1–Q12, with none waivable. The verifier has an official mode and a review mode.
10. Independent qualification review: QUALIFICATION_ACCEPTED with G1–G3 and E1–E5. If it is REJECTED, STOP; no
    same-round repair.
11. Grant JSON, committed alone as the child of the review. `check_grant` enforces the chain
    freeze → qualification → review → grant.
12. Exactly-once refs:
    * marker `refs/<ns>/target-consumed` → grant (CAS from zero OID);
    * `refs/<ns>/pending-result`;
    * an emergency O_EXCL file.
13. Driver modes: preflight, rehearse, decoy-stage1, execute, seal-only. Exit codes 0 and 2–7. A historical control
    runs post-grant and pre-marker.
14. Seal-from-memory (C12-R2 design): serialize in memory; hash-object -w; pending ref by CAS; commit with a private
    index and --cacheinfo; only then materialize the worktree copy with O_EXCL|O_NOFOLLOW; signals ignored after the
    marker.
15. Post-execution checks: result blob = pending ref; the seal changes only the result; parent = grant; one execution;
    a second execute is refused; seal-only is read-only; r5 unchanged, no r6; no other cell evaluated.
16. Execution review: 11 checks.
17. Adjudication: the frozen §8 table verbatim.
    * CLOSED_UNDER_<route> for pass true, Γ < 0 exact;
    * NOT_CLOSED for Γ ≥ 0 or CERTIFICATION_FAILED;
    * EXECUTION_INDETERMINATE after any post-marker failure;
    * CONTROL_FAILED means no conclusion, not consumed, STOP.
18. Adjudication review.
19. Handover.

**Ledger.** Pre-grant classes are START_STATE_READ, HISTORICAL_READ, NONTARGET_DECOY, SYNTHETIC, GOVERNANCE and
DISCLOSURE. TARGET_EXECUTION is appended after the seal.

**Failure and recovery.**
* REJECTED means STOP.
* A consumed marker is never rerun.
* Lost information means no recompute without new governance.
* Resolve the E4 literal conflict about the post-exec refusal probe.

## 4. Incidents (as they bear on 309)

* **Incident 01** is TPT tail use: BLOCKED (PROXY_EXPOSURE). Any future use must carry it as a disclosed liability and
  obtain U3 knowing it.
* **FREEZE_DESIGN_TPT_TAIL** is design only:
  * user sees incident 01, then U3 or explicit CLOSURE_ONLY, then a fixed cell set;
  * the reproduction gates G-R1…G-R4 run inside the sealed execution;
  * decoy-only qualification;
  * result-chasing risk MEDIUM–HIGH.
  * Its cell set is stale: 307 is closed and 308 is live.
* **Incident 02** is a cross-cell re-attribution of a committed 309 certificate at the 308/309 shared endpoint. It is
  forbidden (amendment 2 R2.4). 309 work must never produce or relabel quantities toward 308.
* **Incident 03** is a C2b brief scale derived from 308 figures. It bears on 309 only if the C2b A0 certifier is used.

## 5. Incident-independence conditions C1–C6 (307 review)

* **C2, C3, C5 and C6 generalize directly.** These cover decoy latent proxies, latent-proxy additions, a review check
  of campaign decisions for target dependence, and one sealed evaluation with no retry and no tuning, with the
  criterion frozen before the grant.
* **C1 and C4 generalize in form.** A 309 campaign needs its own coordinator audit plus an independent review, and its
  briefs hashed or committed.
* **Wording:** "temporal and parametric independence only".

## 6. Rejected closeout freezes

All three were administrative:
* r0: stale state;
* r1: hard-coded branch keying and a weak wording scan;
* r2: a lossy drift classifier and a weak carrier regex.

**Constraints on 309:**
* The accepted scoped wording is "OPEN; refuted within scope only"; C4:503 says "not unclosable".
* C5 Condition 2: no successor may restate the 309 exclusion without re-deriving it under its own clause, or E2 (done
  by C7).

## 7. Closure-only closure under a different consumer

* **For adoption:** the direct clause.
* **For scientific statements:** C5-T is the adopted authoritative transport where x_lo > 0 (C5_ADJUDICATION:561-565).
* **Scientific closure under a sharpened sound transport** (TPT, etc.) is permitted, labelled closure-only. Its
  validity rests on the campaign's own theorem plus reviews.
* **Caveat:** TPT r2 was never re-reviewed after REVIEW_TPT_R1 NOT_READY, and no second global review was run.
