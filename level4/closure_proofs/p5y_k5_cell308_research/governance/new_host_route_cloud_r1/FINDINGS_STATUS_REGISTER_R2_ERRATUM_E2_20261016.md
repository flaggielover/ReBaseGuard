# Erratum E2 to findings status register r2 (Cell-308 Cloud route r1): B2's reading

**Status: CURRENT STATE RECORD.** This erratum amends `FINDINGS_STATUS_REGISTER_R2_20261016.md` (`550eb831…3061`)
together with its erratum E1 (`FINDINGS_STATUS_REGISTER_R2_ERRATUM_E1_20261016.md`, `37875b92…155c`). Both are preserved
unchanged. Where they differ, this erratum governs.

**Still true after this erratum:** no finding has reached VC, OD, IT or AX. `new_target_evaluations = 0` ·
`cell309_activity = none`.

**Source.** The B2 reading (`reviews/external/READING_EXTERNAL_B2_INCIDENT_REVIEW.md`, `201aa5af…f9b2`). B2's results
are recorded as evidence from an owner-appointed external reader. B2's isolation is not certified, by B2 (report line
30) or by the owner.

## E2.1 — Rows updated

| id | cover (updated) | evidence | remaining |
|---|---|---|---|
| **G38** (incident-review quotations UNVERIFIED) | **PC** (was NC) | B2 quotes N1–N4 and T1–T6 verbatim. The amendment r5 §6 quotations are **MATCH** (B2 lines 109–118) | the owner's use of the reading (OD) |
| **S6** (floor basis; verbatim N1–N4 / T1–T6; whether T1 fires) | **PC** (was PP) | The floor is restated on trigger-independent text (amdE2.3). The verbatim reading is recorded (B2 lines 36–89). **`T1_ON_PLATFORM_CHANGE: CANNOT_TELL`** (line 122) is recorded as it stands: neither fired nor unfired | VC (text) and OD. The floor stays not lower than HIGH; nothing lowers it |
| **S17** (T2 / T5 unknown; label collision with governance S9's T1–T4) | **PP** (was NC) | T1–T6 are listed verbatim (B2 lines 63–89) | The disambiguation from governance S9's "T1–T4" is not made by B2. It must be stated in the S1 brief (owner package R4 §6) |
| **S8** (non-holder trace; T6 M1–M6 transfer) | **PP** (unchanged) | The trace requirement and its order: PC. **M1–M6 definitions: MISSING** (B2 lines 91–95) | B2's supplement (matrix A5s), then B3 with task item 3 assessed on the actual M1–M6 |

## E2.2 — Other open items

| item | state |
|---|---|
| M1–M6 definitions | **MISSING.** Lead: the T6 supplement (blob `d3d1ef53…438a`, metadata only; not read by the coordinator side). Awaits B2's owner-released supplement |
| T6 transfer ruling prerequisite | **not discharged** (matrix R4 erratum E2, row A14) |

Every other row of register r2 and erratum E1 stands.
