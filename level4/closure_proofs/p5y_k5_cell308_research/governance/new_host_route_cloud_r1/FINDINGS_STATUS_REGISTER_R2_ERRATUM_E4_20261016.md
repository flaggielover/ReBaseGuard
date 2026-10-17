# Erratum E4 to findings status register r2 (Cell-308 Cloud route r1): external B3 findings

**Status: CURRENT STATE RECORD.** This erratum amends `FINDINGS_STATUS_REGISTER_R2_20261016.md` together with errata
E1–E3 (`FINDINGS_STATUS_REGISTER_R2_ERRATUM_E3_20261016.md`, `9154d02c…b62b`). All are preserved unchanged. Where they
differ, this erratum governs.

**Still true:** no finding has reached VC, OD, IT or AX. `new_target_evaluations = 0` · `cell309_activity = none`.

## E4.1 — B3 (`reviews/external/REVIEW_EXTERNAL_B3_PROVENANCE.md`, `16188ffd…e96a`)

| id | sev | cover | correction (PC) in | VC route | OD | IT / OPS |
|---|---|---|---|---|---|---|
| Y1 | MAJOR | PC | recommendations erratum E1.1, E1.4 | B3's single confirmation (A9c) | req (A17) | OPS-10 |
| Y2 | MAJOR | PC | recommendations erratum E1.2–E1.3, with the recorded source retrieval (not independent) | A9c | req (A17) | OPS-5 |
| Y3 | MAJOR | PC | package erratum E2 | A9c | req (A17) | B4 readings |
| Y4 | MAJOR | PC | `PROVENANCE_DISPOSITION_RECORD_B3_20261016.md` | A9c | req (A17) | — |
| Y5 | **BLOCKING** | **PC (the claim is corrected and guarded); transfer NOT established** | T6 disposition §2–§5; owner package R4 erratum E1 | A9c (whether the correction is accurate) | req (A14, scoped) | C1-M3 if adopted |
| Y6 | MAJOR | PC | the provenance record §6; matrix erratum E4 (B9-T) | A9c | req | B9-T; C1 |
| Y7 | NOTE | **recorded**; it remains an author proposal | T6 disposition §6 | none appointed | req (A15) | B8 / B9 |
| Y8 | NOTE | **recorded**; it remains UNVERIFIED | T6 disposition §6; ER-T6 lists B3 as R6 | ER-T6 (register part only) | — | — |

## E4.2 — Rows updated

| id / item | cover | change |
|---|---|---|
| S5 (N1) | PC | N1's choices are now stated (recommendations E1.1). No response capacity is evidenced |
| S8 (non-holder trace; T6) | **PP** (unchanged) | The route-level textual trace is done by B3 and corrected in this round (PC). The code-level trace is placed at B9-T. **T6 transfer: UNMET**; the scoped ruling is pending (A14) |
| S13 (N2) | PC | N2 is discretionary (recommendations E1.2). The source retrieval is recorded and is not independent |
| T6 conditions: satisfaction and transfer | **UNMET** (was PENDING) | per B3. Not carried forward by any record. M3 is placed at C1-M3 only as a possible new safeguard |
| role-holder status (R1–R6) | **UNVERIFIED** | ER-T6 (A14a), prepared and not commissioned |
