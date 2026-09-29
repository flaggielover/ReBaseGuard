# MB308 execution interruption: erratum E1 to addendum A1 (coordinator)

**Why.** Repairs R1 and R2 of the delta review `reviews/REVIEW_EXECUTION_INTERRUPTION_DELTA.md` (research
`0b9020af`, sha256 `3c48babf…b5a220`, DELTA_REJECTED).

**Status of the earlier files.** Addendum A1 (`audit/EXECUTION_INTERRUPTION_ASSESSMENT_ADDENDUM_A1.md`, research
`e681d16f`) and the original assessment (research `8b64d989`) stay byte-unchanged. E1 replaces exactly two sentences
of A1 and nothing else. A1, as corrected by E1, prevails over the original assessment.

## R1: in A1 (a), the sentence on signals and survival

**Replaced sentence:**

> A SIGTERM-class termination of the app's subprocesses therefore killed `caffeinate` and left the driver and the
> workers running.

**Replacement (the reviewer's wording):**

> If the app's subprocesses received a SIGTERM-class signal (not logged), that would kill `caffeinate` and leave the
> driver and the workers running. The continued pool load shows that the workers kept running; that the driver
> survived is most probable, not proven.

## R2: in A1 (e), the post-reboot object sentence

**Replaced sentence:**

> **After the reboot:** the only objects written are those of the research commit `8b64d989` that carried the
> assessment (12 objects; type- and size-accounted by the review). None of them is a result object.

**Replacement (the reviewer's wording):**

> After the reboot, the only objects written are those of the research-branch commits made since (`8b64d989`,
> `ef29bc2b`, `e681d16f`, and any later research commit). All of them are accounted for by id and type; none is a
> result object.

No fixed count is given, since later commits would falsify it. The statement "no object was written between the
marker and the reboot" is unchanged.

## Unchanged

Everything else in A1 stands as the delta review accepted it:

* answers A–E and the frozen outcome **CELL308_EXECUTION_INDETERMINATE**;
* TARGET_EVALUATION_COUNT 1;
* the status lines: cell 308 OPEN; r5, K5 and P5Y unchanged; no r6;
* the C3 ledger line.
