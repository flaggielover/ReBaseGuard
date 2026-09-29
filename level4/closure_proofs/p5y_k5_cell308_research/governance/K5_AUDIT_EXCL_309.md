# K5 audit, excluding cell 309 (Phase 14; coordinator; read-only; status statements only)

This audit changes nothing:

* no status is changed, no r6 is created, and nothing is adopted;
* no target computation;
* no tail figure (committed values stay in `history/` and `ledger/`).

**Cell 309 is EXTERNALLY_IN_PROGRESS** in a separate session and is not inspected here.

## 1. Where P5Y stands

| item | status | record |
|---|---|---|
| K1 | CLOSED (successor adjudication) | `7d5cf02b` "close P5Y K1 line by successor adjudication" |
| K2, K3 | CLOSED (independently countersigned) | `df703837` |
| K4 | CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN (K4R1) | `e88a2885`, tag `p5y-k4-successor-closed` |
| K5 | **PARTIAL** | coverage map r5 authoritative (sha `e2197051…`): m1–m3 complete; m5 adopted to 305; **open range [306, 309]**; `K5_COVERAGE_COMPLETE` false |
| P5Y | **not closed**. K5 is its only open item | — |

## 2. The adoption rule in force (floor r2, `a15d083b`, REPLACEMENT_FLOOR_ACCEPTED `3fadb422`)

**Adoption of (m=5, k)** requires all three of:

* scientific closure (Γ < 0 under the frozen K5-B clause on the campaign's chosen **single-implementation** supply);
* **F1′** (two independent operator-constant implementations, N9-comparable, Γ < 0 under **each** supply
  separately) **or F2** (Γ < 0 survives a uniform 1.25 degradation of every atom constant);
* a complete prospective governance chain: freeze before evaluation, qualification, one sealed evaluation,
  independent reviews, an adjudication applying the rule, and the coverage map generated from that adjudication.

**Scope as frozen.** F1′ is available only to a cell with its own two-implementation evidence; at the freeze, only
cell 306. **Cells 307–309 are OUT OF SCOPE**: the floor authorises no work on them, and sets no gate or criterion for
them. The rule "no re-evaluation, parameter change or supply change after a disagreement **in the same campaign**"
(`disagreement.never`) applies.

## 3. Cell by cell

### 306: OPEN

* **History.**
  * I1 closure: the historical C2 record under S_I1.
  * The replacement I2 evaluation (C12-R2) was executed once and sealed (`276f4d41`, EXECUTION_ACCEPTED), with a
    **positive** Γ under S_I2.
  * Floor r2 adjudication: **CELL306_NOT_ADOPTED** (`9c2cbf21`; ADJUDICATION_ACCEPTED `c5324a78`). F1′(d) fails,
    because Γ < 0 does not hold under each supply.
* **No target rerun.** None was made, and none is permitted within that campaign (`disagreement.never`).
* **What remains.** No path exists inside the existing campaigns. Any future attempt needs:
  * a **new, prospectively motivated campaign**, with independent motivation fixed before any new 306 evaluation,
    because a result under S_I2 has been observed;
  * **a user decision**;
  * **either** F2 on a single-implementation chosen supply, **or** a floor decision covering a different kind of
    evidence.

  Nothing is planned tonight.

### 307: CLOSED_UNDER_RLR (scientific closure only; not adopted)

* **History.** `p5y_k5_cell307_rlr_r1`, executed once, sealed. EXECUTION_ACCEPTED and ADJUDICATION_ACCEPTED:
  **CELL307_CLOSED_UNDER_RLR**, closure-only. The marker is consumed and never re-run. r5 is unchanged, and there
  is no r6.
* **Remaining governance: adoption.** Floor r2 declares 307 out of scope. Adopting it therefore requires:
  1. a **separate prospective floor-extension decision** (by the user, with an independent review), defining what
     evidence suffices for an RLR-supply closure. For example:
     * a second independent implementation of the RLR block constants;
     * or an F2-type degradation-survival test fixed in advance;
  2. an adoption campaign under that extension, with its own complete chain. If the extension needs any new
     evaluation of 307, that evaluation needs its own governance. **No re-run of the RLR r1 execution.**
  3. an adjudication applying the extension, then a coverage map generated from it.

### 308: OPEN

* **History.** MB308 r1 (formal `p5y-k5-cell308-mb-r1`):
  * grant `afa93072`, consumed;
  * the run was orphaned by the 23:29 JST Force Quit and ended at the latest by the forced power-button reset at
    00:00:15 JST; nothing was persisted;
  * postexec `21e99cf0`; EXECUTION_ACCEPTED `a40211cc` (adapted sense); adjudication
    **CELL308_EXECUTION_INDETERMINATE** `9ad632c9`; ADJUDICATION_ACCEPTED `e451e634`;
  * TARGET_EVALUATION_COUNT 1. The single authorisation of route MB r1 is exhausted.

  This is **not** a scientific negative.
* **Successor MB-S (prospective):**
  * governance GOVERNANCE_ACCEPTED (research `00a432df` with errata `a7c969e8`), classification
    SUCCESSOR_ALLOWED_WITH_CONDITIONS;
  * route ROUTE_ACCEPTED (research `87d0b2b9`): MB r1's science byte-identical, new infrastructure only;
  * crash-safe build in progress; incident re-rating (S12) in progress.
* **What remains before any 308 target step:**
  1. The build completes, with an independent implementation review and bounded repairs.
  2. S12 is accepted.
  3. **A user decision covering the freeze** (§14 / G2 same-caps question; S16(c)).
  4. The freeze.
  5. The official qualification, on an awake, cool host with automatic updates disabled.
  6. A fresh qualification review.
  7. **The S1 user ruling**, notwithstanding the brief's §21 and mitigation 5, with the C11R-I2/COR-T trade shown.
  8. The grant, then one execution under the durable state machine.
  9. The §10 reviews and adjudication.
* **Adoption, even after a closure,** needs the same kind of floor extension as 307, since 308 is out of floor r2's
  scope.

### 309: EXTERNALLY_IN_PROGRESS (not touched)

What this project will eventually need from the external 309 campaign, for K5 bookkeeping only:

* its final governed status (closure, non-closure or indeterminate) with the complete chain: freeze, qualification,
  independent reviews, grant, execution, adjudication and adjudication review;
* its target-evaluation count and its consumed-marker identity;
* the kind of supply and implementation used, for floor applicability (309 is out of floor r2's scope);
* **a declaration of every drift it evaluated.** This matters for 308's quarantine: any operator evaluation inside
  308's band [6/5, 13/5] or its mirror would be a latent exposure for the 308 successor and must be disclosed before
  the 308 successor's grant. Unlike adjacent-cell work in general, this is a concrete cross-cell requirement;
* whether its campaign read any 308 record, for the same reason.

## 4. Prerequisites for r6, K5 closure and P5Y closure

* **r6.**
  * It is created only from an adjudication that adopts at least one further (5, k) under an accepted floor (r2 for
    306; a future extension for 307–309), with a complete prospective chain.
  * **Never premature.** No r6 exists or is proposed tonight.
  * A scientific closure alone (307 today) does not create r6.
* **K5 closure.** Coverage complete: every open m=5 cell, 306–309, is **adopted** (not merely closed), r_n is
  generated from the adjudications, `K5_COVERAGE_COMPLETE` is true, and the K5 closure adjudication is independently
  reviewed.
  * Today: 306 not adopted (open; no current path); 307 closed but out of the floor's scope; 308 open (successor
    prepared); 309 external.
* **P5Y closure.** K5 closed. With K1–K4 closed, a P5Y-level adjudication would then follow.

## 5. The smallest next user decisions (none taken tonight)

1. **308:** the freeze decision under §14 / G2 (keep MB r1's caps, or re-derive them from decoys under the new
   launcher), and later the S1 ruling.
2. **307 and 308 adoption:** whether to open a prospective floor-extension process for out-of-scope cells.
3. **306:** whether any new prospectively motivated campaign should be considered.
