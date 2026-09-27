# PROPOSED: final K5 PARTIAL adjudication and publication closeout, CUSUM m = 5 tail (cells 306–309)

# DRAFT ONLY — NOT FROZEN — NOT AUTHORIZED FOR EXECUTION

This file is the protocol draft for the route recommended by `../ROUTE_AUDIT_R1.md` §10 (architecture D). It has no
freeze hash, no namespace and no code. Nothing in it runs, and nothing binds, until:
* the user authorizes it;
* the frozen text passes its own review.

The closeout is a **governance and documentation** chain. It evaluates **no** scientific quantity.

---

## 1. Scope

| item | content |
|---|---|
| object | the K5 record for CUSUM, and in particular the disposition of m = 5 cells 306–309 |
| cells | 306, 307, 308, 309 (dispositions); every other CUSUM (m, cell) is carried verbatim from r5 |
| out of scope | SR K5; K1; K4; AWS SR/PS1; any computation |
| SR K5 | carried verbatim from the latest committed status: NOT STARTED at `K5_STATUS.md` :52, a3547b9b. The adjudicator must re-check it against HEAD and must not decide it. |

## 2. Question

The adjudicator decides whether, on committed evidence only, all of the following hold:
* the K5 CUSUM record is correctly **PARTIAL**;
* r5 (blob `f978eeb6b41188eabaf3c6d590c9178d711f1ce6`) is correctly the final coverage map;
* each of 306–309 has the disposition, blocker map and scope statements below, exactly supported by the evidence and
  no stronger.

The K5 specification pre-specifies the outcome class for unresolved cells as `K5_INCONCLUSIVE`
(`p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md` :91).

**Proposed dispositions**, to be confirmed or corrected by the adjudicator:

| cell | disposition | scope statement that must accompany it |
|---|---|---|
| 306 | **OPEN — NOT ADOPTED** | Closed under I1's supply; not certified under I2's (+0.005159101140006536, sealed once); floor r2 NOT_MET (F1′(d), F2). Non-certification under I2 is not disproof. |
| 307 | **OPEN** | Not closed by any committed certified supply. Blocker is (A1, A2), not A0. No certified route evaluated. |
| 308 | **OPEN** | "Operator-level route not excluded" (C4 wording; C4 Condition 2 forbids stronger). |
| 309 | **OPEN — REFUTED WITHIN SCOPE** | Scope per C4 Condition 1 with C7's bound: "uniform-A0 atom-constant family, cell 309, m = 5, against the frozen measurement inputs and the frozen TC-T / K5-B consumer". Not a statement that 309 is unclosable (C4 :503). |

## 3. Inputs

**Allowed:**
* committed artifacts only: E01–E30 of the route audit r1;
* r5;
* the accepted route audit r1 and its accepted review.

**Forbidden:**
* any computation of Γ, margin, factor, bisection, knockout, Λ bound, replay or calibration for any cell;
* any campaign code, producer, certifier, verifier or driver execution;
* C11R's quarantine;
* any D1/D2 value;
* session transcripts;
* AWS and Vultr;
* push, merge and main synchronization.

## 4. Implementations, constants and supply policy

None. No supply is chosen, evaluated or compared.

## 5. Target definition

**None.** There is no scientific target. The only "result" is the adjudicator's verdict on the record.

## 6. Safe preflight

Every preflight check below is document-only.

* **P1. State.**
  * HEAD and branch as frozen;
  * r5 blob `f978eeb6…`;
  * no r6 anywhere;
  * `refs/c12r2/cell306-target-consumed → dec92e09`;
  * `refs/c12r2/cell306-pending-result → 0ac46b3d`;
  * forensic objects present;
  * tree clean, including ignored files.
* **P2.** Every artifact the closeout cites exists at its cited commit with the cited text. This uses `git show` and
  `git cat-file` only.
* **P3.** No K5 tail namespace has changed since the route-audit-r1 review commit (`git log`).
* **P4.** The value-free leak scan (the inherited D1/D2 hash sets) passes on every closeout file.

## 7. Kill gates

| gate | pass condition | on failure |
|---|---|---|
| KG0 | P1 passes | STOP |
| KG1 | route audit r1 carries an ACCEPTED independent review | STOP |
| KG2 | P3 passes (no new K5 evidence since the audit) | STOP; re-audit first |
| KG3 | P2 and P4 pass | STOP |

## 8. Load-bearing boundary

There is no load-bearing target information in this chain.

If the adjudicator concludes that a disposition cannot be decided without computing any tail quantity, the closeout
**STOPS** and reports this. It does not compute.

## 9. Exactly-once

Nothing is computed, so there is nothing to consume. The adjudication verdict is issued once, and its commit is the
record. A rejection is preserved verbatim, and any repair is a successor document.

## 10. Qualification

No code is involved. Instead there is a frozen document checklist: P1–P4 plus the disposition table above. The
adjudicator must tick each item with the file and line it checked.

## 11. Reviews

Each review is by a fresh context, read-only, with its verdict on line 2.

1. **Independent final adjudication:** `K5_PARTIAL_CONFIRMED` / `K5_PARTIAL_REJECTED`, with per-cell dispositions and
   scope statements.
2. **Independent adjudication review:** `ADJUDICATION_ACCEPTED` / `ADJUDICATION_REJECTED`.

No reviewer output is read before its completion notification.

## 12. Adoption criterion

**None.** The closeout adopts nothing and changes no coverage.

## 13. Stop conditions

The closeout stops on any of the following:
* a KG failure;
* a blocking review;
* any need to compute;
* any need to modify a predecessor namespace, r5, the refs or the forensic objects;
* a leak-scan hit;
* any contact with AWS or Vultr.

## 14. Coverage consequence

* r5 remains the final authoritative map, and no r6 is created.
* K5 CUSUM is **PARTIAL**, with unresolved cells in the outcome class `K5_INCONCLUSIVE`: m = 5 cells 306–309.
* SR K5 is carried verbatim.
* PARTIAL is **not** a claim that any open cell is unclosable.

## 15. Publication closeout

A single status document is committed in a new local namespace. It carries:
* the adjudicated dispositions;
* the blocker map (route audit r1 §4, §6);
* the structural finding (r1 §6);
* the user-level prerequisites U1–U3:
  * U1: host provisioning;
  * U2: P3 admissibility;
  * U3: a floor extension for closure-only routes;
* the ranked open research items:
  * the RSO lemma;
  * R-asm;
  * R4 after N1, N5 and N7;
  * B1 with a new provenance chain;
* the reopening rule (§16).

Nothing is pushed or merged, and main is never synchronized, without explicit user instruction. LOCAL_MAIN_REF and
REMOTE_MAIN_REF stay as they are.

## 16. Reopening rule, recorded but not exercised

Cells 307–309 may be reopened only under a fresh user authorization of a prospective campaign. Any theorem, floor
extension or admissibility ruling it needs must be frozen and reviewed **before** any tail recomputation (C2
Condition 1). Cell 306 may not be touched by such a campaign without its own separate authorization.

## 17. Historical preservation

Nothing is edited in:
* C1–C12-R2;
* floor r2;
* maps r3, r4 and r5;
* route audit r0 and r1, their drafts and their reviews.

The following are retained:
* `refs/c12r2/*`;
* the C12-R2 seal;
* `b83cc6f5`;
* `def4e453`.

## 18. Compute

None.
