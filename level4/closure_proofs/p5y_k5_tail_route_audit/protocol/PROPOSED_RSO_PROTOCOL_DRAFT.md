# PROPOSED CAMPAIGN "RSO": residual-specific order-0 bound, CUSUM m = 5, cells 307–309

# DRAFT ONLY — NOT FROZEN — NOT AUTHORIZED FOR EXECUTION

This file is a proposal written by the route audit (`../ROUTE_AUDIT.md` §10–§11). It has no freeze hash, no campaign
number and no namespace. No code exists for it.

Nothing in it may be executed, and no part of it binds anyone, until:
* the user authorizes a freeze;
* the frozen text passes its own reviews.

On authorization it would receive a campaign number and its own namespace. The name "RSO" is only a label.

---

## 1. Scope

| item | content |
|---|---|
| model | CUSUM, K5, m = 5 only |
| cells | **307, 308, 309**, in the frozen order 307 → 308 → 309 |
| excluded | **cell 306** (governance-final: CELL306_NOT_ADOPTED, ADJUDICATION_ACCEPTED at c5324a78). No RSO quantity may be computed for 306, in any stage. |
| excluded | every other cell and every other m; SR/PS1; any K1 production |
| stages | **Stage 0** (target-free; this draft's first freeze) and **Stage 1** (load-bearing; a separate freeze and a separate authorization, only after Stage 0 passes) |

## 2. Question

C4's adjudication §7 item 1 (e12a09e8) names residual-specific order-0 bounds. It calls them "the sharpest unexcluded
mechanism and the one a successor should cost first". C5-N3 (69bff424) and the C8 adjudication (63a3f825) record
that no one has costed them.

The campaign asks two questions, in order:

1. **Stage 0 (mathematics).** Is there a theorem, a TC-T variant, under which TC-T's order-0 term `A0·‖φ_H‖` may be
   replaced by a certified pointwise residual majorant of the form `(Ĝ|φ_H|)(a) / D_e`, soundly for the frozen K5-B
   clause? And can that majorant be certified from committed code and data?
2. **Stage 1 (science, only if Stage 0 passes).** For each k ∈ {307, 308, 309}, is `T(k) := Γ(5, k; S_RSO(k)) < 0`?
   And does floor r2 hold for k?

Stage 1 exists only to answer question 2 **once** per cell.

## 3. Inputs

**Allowed:**
* Theorem TC-T (`p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md`, 76c37de1).
* The frozen K5-B clause (E02).
* The committed per-cell TC-T inputs `p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_30{7,8,9}.json`. They
  are read in **Stage 1 only**.
* I1's committed operator constants for 307–309 (REGISTRY_C2, the Arb/FLINT lineage), combined by C2's D4 rule over
  Lemma G and Lemma Dv′ r2, exactly as C2 computed its supply for these cells. Read in **Stage 1 only**.
* Candidate polynomials for 307–309, obtained only by the **identity-gated replay** of the committed 13-module chain
  (C6: `REPLAYABLE_EXISTING_ADDRESS`), in **Stage 1 only**.
  * The replay must reproduce every committed scalar bit-identically.
  * If it does not, it refuses.
* For Stage 0: manufactured fixtures only, plus replay identity on **cell 305** (identity pass/fail output only; see
  §7).

**Forbidden:**
* Any 306 datum.
* I2 constants of any cell, and C11/C11R/C11RD outputs. For 307–309 they do not exist; for 306 they are out of scope.
* C11R's quarantine.
* Any original or independent D1/D2 value.
* C8/C9 counterfactual factors used as parameters or thresholds. They may be cited in prose only.
* Calibration on any real cell (§7, L4).
* Mixed-implementation constants.
* Results of any other route.
* AWS SR/PS1, and any host not explicitly authorized.

## 4. Implementations

* **Operator constants:** I1 only (single implementation, floor r2 §3 chosen-supply restriction). No I2 exists for
  307–309, and none is built here.
* **RSO bound: two independent implementations.**
  * **RSO-A** is primary.
  * **RSO-B** is written from the theorem text alone, imports nothing from RSO-A, and uses exact rational
    arithmetic.
  * Per C11's lesson, independence here is of implementation and backend, **not of authorship**, and is described
    as such.
* **Agreement rule:** in Stage 1 both implementations run inside the single sealed evaluation. If they are not
  identical (or, for interval outputs, identical endpoints), the cell is sealed as `IMPLEMENTATION_DISAGREEMENT` and
  cannot be adopted.

## 5. Constants and supply policy

* **S_RSO(k).**
  * Start from I1's committed D4 supply for cell k.
  * TC-T's order-0 term is replaced by `min(RSO-A certified upper bound, committed A0·‖φ_H‖)`.
  * The min of two sound upper bounds from one lineage is sound. It also makes the new term provably no looser than
    the old one (KG2).
* **No free parameter may depend on k.**
  * This covers every grid depth, subdivision count, precision and rounding mode used by the majorant.
  * Each is fixed in Stage 0 by a cell-independent rule, written in the frozen text before any tail datum is read.
  * The verifier checks that the frozen parameter table is one table for all three cells.
* **No supply alternatives.**
  * One supply per cell, frozen.
  * No fallback supply, no second attempt, no componentwise mixing across implementations.

## 6. Governance items to decide before any freeze (open)

* **G-1: the F2 reading for the new term.**
  * Floor r2's F2 degrades "every atom constant of the chosen supply" ×1.25.
  * Proposal: also multiply the RSO term by 1.25. It is not an atom constant, but it replaces an atom-constant term.
    This reading is **at least as strict** as r2's F2.
  * An independent governance review must confirm that it is not a floor change and not a weakening.
  * If the review finds either, Stage 1 may not run (KG7).
* **G-2: the clause.**
  * Default: the **C2 clause**, the one under which C2 published F2 and which the C12-R2 control and the floor-r2
    application consumed.
  * The C5-T clause is valid mathematics (C5 adjudication), but it is **not** selected. Its only effect here is to
    lower the required factors, so choosing it now, in knowledge of C8's per-cell factors, would be a
    favourable-direction choice.
  * The conservative choice is not result-chasing in either direction.
* **G-3: single-implementation restriction.**
  * The certification of `(Ĝ|φ_H|)(a)` must consume only I1-lineage certified objects and exact arithmetic.
  * A review must confirm that S_RSO does not combine implementations in the sense of floor r2 §3.

## 7. Information boundary

### Safe preflight (Stage 0)

These steps are target-free.

* **S1.** Theorem statement and proof. No cell data.
* **S2.** RSO-A and RSO-B, qualified on **manufactured fixtures** with analytic answers:
  * exact agreement between the two implementations;
  * a mutation suite that also covers the classifier and the floor evaluator (C3-N2 lesson).
* **S3.** Structural applicability: the committed chain can deliver φ_H as a function through the identity-gated
  replay. The check reads code and schemas only (presence, hashes, call signatures) and **no tail numeric value**.
* **S4.** Host and toolchain.
  * The host must be authorized.
  * The pin is the one C9 recorded: Python 3.12.3, numpy 2.5.2, python-flint 0.9.0, FLINT 3.6.0.
  * **Replay identity on cell 305** outputs PASS/FAIL against committed scalars only.
  * The replayed 305 candidates are **deleted unread** after the identity check. No RSO code is ever applied to them.
* **S5.** Wall-time and CPU cost of the S4 replay only.
* **S6.** G-1, G-2 and G-3 decided and reviewed.

### Load-bearing (Stage 1 only, exactly once per cell, after the grant)

* **L1.** Any RSO evaluation on 307–309.
* **L2.** Any Γ, Γ sign, margin, factor or closure indicator for 307–309.
* **L3.** Any quantity from which such a Γ could be inferred, including new-term/old-term ratios.
* **L4.** Calibration on **any** real cell, including 305 and the lower front. C2's R-stage design records that
  per-cell ratios transfer as estimates. **Forbidden in every stage**, not just Stage 0.
* **L5.** Any computation on replayed 307–309 candidates beyond the identity gate.

**Rule:** if it is uncertain whether a check leaks target information, it is forbidden.

## 8. Kill gates

All kill gates are evaluated before any L-information exists. None predicts success.

| gate | pass condition | on failure |
|---|---|---|
| KG0 | state: HEAD/branch/refs as frozen; r5 blob `f978eeb6…`; no r6; `refs/c12r2/*` unchanged | STOP |
| KG1 | RSO theorem proved; fresh independent review returns **THEOREM_ACCEPTED** | STOP → final K5 PARTIAL adjudication |
| KG2 | the theorem proves the new term ≤ `A0·‖φ_H‖` (also enforced by the min in §5) | STOP → PARTIAL |
| KG3 | fixtures 100 %; RSO-A ≡ RSO-B; every non-equivalent mutant killed | one repair round, then STOP → PARTIAL |
| KG4 | S3 applicability passes; otherwise `DATA_BLOCKED` | STOP → PARTIAL |
| KG5 | an authorized certifying host exists with the pin, and 305 replay identity PASSES; otherwise `TOOLCHAIN_BLOCKED` | STOP → PARTIAL |
| KG6 | 3 × (measured per-cell cost) ≤ the hard cap (proposed: preferred 3 CPU-h, hard 6 CPU-h, C2's caps) | STOP → PARTIAL |
| KG7 | G-1, G-2, G-3 frozen and accepted by an independent governance review | STOP |

A Stage-0 gates report is committed, followed by an independent **STAGE0_GATES_ACCEPTED / REJECTED** review. Only
then may the user be asked to authorize the Stage-1 freeze.

## 9. Target definition (Stage 1)

For each k ∈ {307, 308, 309}, the target is `T(k) := Γ(5, k; S_RSO(k))` under the frozen K5-B direct clause (G-2),
computed as an outward exact-rational upper bound.

* **Pass:** `T(k).hi < 0`.
* **F2 quantity, in the same sealed run:** `T_deg(k)` = the same with every atom constant of S_RSO(k) degraded ×1.25
  and the RSO term ×1.25 (G-1).
* **Per-cell sealed classes:**

  | class | condition |
  |---|---|
  | `CLOSED_F2_PASS` | T < 0, T_deg < 0 |
  | `CLOSED_F2_FAIL` | T < 0, T_deg ≥ 0 |
  | `NOT_CERTIFIED` | T ≥ 0; non-certification, **not** disproof and **not** an exclusion |
  | `IMPLEMENTATION_DISAGREEMENT` | RSO-A and RSO-B differ |
  | `EXECUTION_FAILED` | the post-marker handler recorded a failure |

## 10. Exactly-once execution (Stage 1)

This inherits the C12-R2 driver pattern, with all 32 pin classes, including:
* identity binding to one worktree, git dir, common dir and branch;
* interpreter flags `-I -S -B`;
* pre-marker `lstat` refusal of guarded paths, and ignored-file awareness;
* a CAS consumed marker **per cell**: `refs/<campaign>/cell{307,308,309}-target-consumed`;
* after each marker: signals ignored, an evaluation-scoped wall cap, and a seal from memory;
  * the seal goes through `hash-object -w --stdin` checked against a local SHA-1, a pending ref, a private index,
    `commit-tree` and a CAS `update-ref`;
  * a second persistence channel is an emergency file in the git dir;
  * `seal-only` never computes;
* post-seal materialization with `O_CREAT|O_EXCL|O_NOFOLLOW` and read-back.

**Run order:**
* One grant, generated by the frozen grant generator and committed alone as the direct child of the
  qualification-review commit.
* One invocation evaluates 307, then 308, then 309, each sealed before the next begins.
* **Every cell is evaluated regardless of earlier cells' results**, so there is no adaptive selection.
* On an **execution** failure (not a Γ sign), the driver seals that failure and stops. Unconsumed cells stay
  unconsumed and need a new authorization.

There are no retries, ever. A consumed cell is never recomputed.

## 11. Qualification (Stage 1)

A frozen verifier runs sandboxes built **at the freeze commit**, never at HEAD. It must demonstrate:
* the freeze-commit sandbox passes;
* qualification, review, grant and consumed-state sandboxes **cannot** evaluate;
* a copied repository, the wrong branch or the wrong worktree cannot consume;
* a planted result cannot cause a second evaluation;
* a seal failure cannot cause a second execution;
* decoy inputs are rejected;
* the value-free leak scan passes (the inherited D1/D2 hash sets);
* the evidence directory contains no RSO output before the seal.

**End-to-end rehearsal uses a synthetic, schema-identical manufactured cell only.** C12-R2 rehearsed on cell 305,
but a real-cell rehearsal here would be L4 calibration.

## 12. Reviews

Each review below is by a fresh context, read-only, with its verdict on line 2. No reviewer output is read before its
completion notification.

| stage | review |
|---|---|
| Stage 0 | theorem (THEOREM_ACCEPTED) |
| Stage 0 | fixture qualification |
| Stage 0 | governance items G-1/G-2/G-3 |
| Stage 0 | gates report (STAGE0_GATES_ACCEPTED) |
| Stage 1 | pre-freeze |
| Stage 1 | qualification (QUALIFICATION_ACCEPTED) |
| Stage 1 | execution (EXECUTION_ACCEPTED) |
| Stage 1 | adjudication (ADJUDICATION_ACCEPTED) |

## 13. Adoption criterion

This is **floor r2, verbatim, as the standing floor** (r2 §9, C2 Condition 1). There is no new limb and no changed
threshold.

* **Base:** `T(k) < 0` under the frozen single-implementation chosen supply S_RSO(k).
* **F1′:** unavailable. No two-implementation certification of 307–309's six operator constants exists, and r2 §9
  does not extend F1′ to them.
* **F2:** `T_deg(k) < 0` (G-1 reading).
* **Complete chain:** a complete prospective chain, and an adjudication that applies r2 mechanically to the sealed
  values.

A cell in `CLOSED_F2_FAIL` is **scientifically closed and not adopted**.

## 14. Stop conditions

The campaign stops on any of the following:
* any KG failure;
* any blocking review verdict;
* any leak-scan hit;
* the cost cap exceeded;
* any need, after a freeze, to change scope, clause, supply, parameters or floor;
* any attempt to read or compute 306 data;
* any contact with AWS SR/PS1 or an unauthorized host;
* an unexpected ref state;
* a post-marker failure (seal-only, then stop).

## 15. Coverage consequence

* A coverage map **r6** is generated only in this case:
  * an adjudication ADOPTS at least one cell under r2;
  * its adjudication review is ACCEPTED;
  * r6 is produced by a frozen generator that consumes only that accepted adjudication and the sealed blobs.
* **r6 changes only the adopted (m = 5, k) entries.** Otherwise r5 stays authoritative.
* No Stage-1 outcome creates or strengthens an exclusion: RSO is closure-only.
* 306's entry is never touched.

## 16. Historical preservation

* No predecessor namespace is edited: C1–C12-R2, floor r2, maps r3/r4/r5, and this route audit once reviewed.
* `refs/c12r2/*`, the C12-R2 seal and the forensic objects (`b83cc6f5`, `def4e453`) are retained.
* A new local branch is created from the reviewed audit commit.
* Nothing is pushed or merged, and main is never synchronized, without explicit instruction.

## 17. Compute

No figure below has been measured.

| stage | item | estimate |
|---|---|---|
| Stage 0 | theory | negligible CPU |
| Stage 0 | fixtures and mutation, exact rational, local `python3 -I -S -B` | minutes |
| Stage 0 | host build | unmeasured; needs the user's permission to download the pinned packages |
| Stage 0 | 305 replay identity | unmeasured |
| Stage 1 | three cells | hours, capped by KG6 |

Stage 1 uses no new real K1 address and no CPU-day.
