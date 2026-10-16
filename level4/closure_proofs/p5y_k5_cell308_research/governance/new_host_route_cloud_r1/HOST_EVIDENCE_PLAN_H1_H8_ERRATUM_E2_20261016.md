# Erratum E2 to the H1–H8 host evidence plan (Cell-308 Cloud route r1) — after FR2 and S12

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** This erratum corrects the plan (`901a05d7…4ec8`) and erratum E1
(`HOST_EVIDENCE_PLAN_H1_H8_ERRATUM_E1_20261016.md`, `f871b9a2…adde`). Both are preserved unchanged.

Its sources:
* FR2 (`1ad769bb…8cac`): K4, K22;
* S12 (`9d549eb2…b55c`): S3, S7, S12.

`new_target_evaluations = 0` · `cell309_activity = none`.

* **K22.** Erratum E1's "reviewed host-selection criteria" means criteria **classed by FR1 against accepted text, not
  accepted**. The minimum M1–M8 are classed; the means and preferences are proposals.
* **K4.** H4 belongs to acceptance part P1 as the owner's exclusivity arrangement. Its measured part stays the live gate
  `host_exclusive` at every step (procedure r3 §4).
* **S7.** M8 requires a readable DMI `product_uuid`. There is no owner-attestation substitute (package r2 erratum E1).
* **S3 — OD-1 record hygiene.** The owner's OD-1 record:
  * names one machine and its architecture;
  * cites only the criteria M1–M8 and the decided preferences;
  * states in writing that no MB r1 target-run observation informed the choice;
  * discloses the decider's E1″ status by name only, never a value.

  Any machine property chosen beyond those criteria carries a written, target-free reason, which a non-holder checks.
* **S12 — attempts.** Every machine inventoried for this route is recorded in the ledger and disclosed in every later
  brief, including candidates dropped before L-DET.
* **Order (§3), corrected.** The steps run in this order:
  1. owner decisions MBS-6 / MBS-7 / MBS-8 and all 21 D-* items, plus the window-bound and response-time numbers;
  2. OD-1;
  3. inventory;
  4. the owner's H3 actions;
  5. attestation, then acceptance part P1, ledger line and anchor;
  6. reviewed build and implementation review;
  7. the L-DET interpreter build (anchored);
  8. acceptance part P2;
  9. OD-3.
