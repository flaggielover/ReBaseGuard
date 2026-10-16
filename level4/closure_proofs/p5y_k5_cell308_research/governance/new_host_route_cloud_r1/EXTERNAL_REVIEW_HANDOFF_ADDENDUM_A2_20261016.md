# External review handoff, addendum A2 (Cell-308 Cloud route r1): after B2's reading

**Status: HANDOFF METADATA · NOTHING LAUNCHED OR APPOINTED BY THE COORDINATOR SIDE.** This addendum adds to
`EXTERNAL_REVIEW_HANDOFF_20261016.md` and addendum A1 (`EXTERNAL_REVIEW_HANDOFF_ADDENDUM_A1_20261016.md`,
`a09c22fb…136a`). Both are preserved unchanged. Where they differ, this addendum governs. `new_target_evaluations = 0` ·
`cell309_activity = none`.

## 1. State of each handoff

| id | state |
|---|---|
| **B1** | Finished. The confirmation was received as an owner-supplied excerpt (`10af3d09…5011`); the full report is not received. No further round |
| **B2** | **Report recorded**: `reviews/external/READING_EXTERNAL_B2_INCIDENT_REVIEW.md`, sha256 `201aa5af49da3c0d3a9b4a13bc4b356fb4f42c59fde86c780d123b0d3930f9b2` (receipt `OWNER_RELEASE_B2_20261016.md`). Tail-figure check: 0 hits. Gap: **M1–M6 not extractable** from its four sources |
| **B2 supplement** | **Owner-authorized, to the original B2 reader only.** It reads exactly one added source, the T6 supplement at pin `f814fe84` (blob `d3d1ef53…438a`, 8745 bytes), to extract M1–M6. The coordinator side neither authorizes nor contacts the reader. It waits for the owner's release of `READING_EXTERNAL_B2_T6_MITIGATIONS_SUPPLEMENT.md` with its sha256 |
| **B3** | Brief r2, unchanged. It may be launched now with B2's released report as its "additional input". **Task item 3 (T6 transfer) needs the M1–M6 definitions** (§2) |
| **S12X** | Unchanged; conditional on statement 1A |

## 2. Note for the owner to give B3 with brief r2 (no change to the pinned brief)

> B2's released report (`201aa5af…f9b2`) quotes T6 (its lines 87–89) but records M1–M6 as NOT EXTRACTABLE (lines
> 91–95). Do not substitute MBS-1…MBS-6, S12's numbered mitigations or S12's summaries for M1–M6.
> * **Task items 1, 1a and 2** (the provenance trace) do not depend on M1–M6. Do them as briefed.
> * **Task item 3:** if B2's sanitised T6 supplement has been released to you with its sha256, use only its quoted
>   M1–M6 definitions. Otherwise do not give a T6_TRANSFER verdict. Write instead:
>   "T6_TRANSFER: NOT ASSESSED — M1–M6 definitions not available".
>
> That line is not a T6 finding, and does not discharge the prerequisite for D-* adoption. You must not read the
> incident review or its T6 supplement yourself, and you must not be B2.

If B3 reports NOT ASSESSED, then once the supplement is released a bounded follow-up on task item 3 is needed. It
can go to the same B3, through the owner, using only the supplement's quotations, before the T6 ruling. That is the
owner's decision.

## 3. What the coordinator side does when the supplement is released

1. Verify its sha256 against the owner's digest, then run the tail-figure check by process only. Any hit sends it back
   to the owner unrecorded.
2. Record it verbatim beside the B2 report. The B2 report stays immutable.
3. Update the register and matrix: the M1–M6 status, S8, and the T6 ruling's prerequisite.
