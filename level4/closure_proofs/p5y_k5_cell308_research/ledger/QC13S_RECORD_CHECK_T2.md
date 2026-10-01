# QC13-S governance records checked against the real repository (reviewQ6 R1; status only)

Run by the coordinator (editorR3C1, a holder, so a program may open the MBS-2 files on its behalf) on 2026-10-01 with
the verifier's own `check_record` from an export of successor 555f4cbf (config revision r2). Only the status and, for
a verdict mismatch, the expected token and the file's line 2 (a public verdict label) are recorded.

| record id | kind | commit | status |
|---|---|---|---|
| GOVERNANCE_ACCEPTED | verdict | 00a432df | VERDICT_MISMATCH: expected `GOVERNANCE_ACCEPTED`, line 2 is `DELTA_ACCEPTED` |
| ROUTE_ACCEPTED | verdict | 87d0b2b9 | VERDICT_MISMATCH: expected `ROUTE_ACCEPTED`, line 2 is `DELTA_ACCEPTED` |
| INCIDENT_RERATING_ACCEPTED | verdict | b7e62dec | OK |
| T6_RULING | verdict | ff2280e9 | OK |
| M4_USER_RULING_OPTION_B | jsonl_line | 5e7b8cdc | OK |
| S14_MBR1_EXECUTION_REVIEW | verdict | a40211cc | OK |
| S14_MBR1_ADJUDICATION | presence | 9ad632c9 | OK |
| S14_MBR1_ADJUDICATION_REVIEW | verdict | e451e634 | OK |
| CONSTANTS_RATIFICATION | verdict | 3c2a7854 | OK |
| LIVENESS_DELTA_ACCEPTED | verdict | 2308651e | OK |
| IMPLEMENTATION_REVIEW_ACCEPTED | verdict | (none) | PENDING_RECORD |
| USER_FREEZE_DECISION | presence | (none) | PENDING_RECORD |

Two records carry a status name where the named file's line 2 is the delta review's own token. The correction is the
repair builder's (R1); this file only reports what the verifier sees. To be re-run on the final bytes before the freeze.
