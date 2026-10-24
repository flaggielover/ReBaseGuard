# Erratum E6 to findings status register r2 (Cell-308 Cloud route r1): the ER-T6 lookup result

**Status: CURRENT STATE RECORD.** This erratum amends `FINDINGS_STATUS_REGISTER_R2_20261016.md` together with errata
E1–E5 (`FINDINGS_STATUS_REGISTER_R2_ERRATUM_E5_20261017.md`, `772360df…02cc`). All are preserved unchanged. Where they
differ, this erratum governs.

**Still true:** no finding has reached VC, OD, IT or AX. `new_target_evaluations = 0` · `cell309_activity = none`.

## E6.1 — Findings touched by the ER-T6 result

| id | cover | change | what remains |
|---|---|---|---|
| YC2 | PC; **lookup done** | ER-T6 r2's bounded lookup was performed and recorded (`e2bcb406…dcbc4`). Results are per individual row. There are no NOT_LISTED results, so none could have been used as a clearance | **open** until the owner's A14b determination exists. That determination is now blocked on the criterion (MA1–MA4), not on the lookup |
| Y8 | recorded; PARTLY | R6b (B3) returned CANNOT_TELL ([N], [K]). The owner-released thread id is not in the register | B3's full non-holder status and its isolation remain uncertified |

## E6.2 — Other rows

| item | state |
|---|---|
| role-holder status | **UNVERIFIED**. The ER-T6 register coverage (Q3) is supplied for all 24 rows, all CANNOT_TELL. Q1, Q2, Q4 and Q5 are open (A14b table §4) |
| established byte-scan events | reviewerFR2 (R5b) and reviewerS12 (R5c), per search-eligibility r2 §3, unchanged. Their significance under the register's conduct-defined classes depends on **MA1** (owner) |
| T6 transfer | **UNMET** |
| T6 applicability | **undecided** |
| historical M1–M8 | none satisfied, and none shown to have definitely failed |
| S8 | **PP** (unchanged) |
