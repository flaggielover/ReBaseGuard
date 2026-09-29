# Cell-308 successor governance, addendum A1: erratum E1 (coordinator; governance delta review D1 to D3)

**Why.** The delta review `reviews/REVIEW_SUCCESSOR_GOVERNANCE_308_DELTA.md` (research `00a432df`, sha256
`ac58383c…321360266`) returned DELTA_ACCEPTED: the determination as amended is **GOVERNANCE_ACCEPTED**. Conditions
D1–D3 must be met before the S1 ruling and the freeze.

**Status of the earlier files.** A1 (`ce145e51`) and the original determination (`e5871aa6`) stay byte-unchanged.

## D1: the brief's exactly-once passages, and the S1 content

The brief's §20 ("exactly one target execution"), §21 ("execute cell 308 exactly once."; "The consumed marker must
make any second execution refuse.") and §23 ("No rerun on rejection.") are now recorded verbatim in
`ledger/USER_TEXTS_SUCCESSOR_308.md` §3.

**Reconciliation.**
* These passages bind MB308 r1's grant, execution and marker. MB r1's marker is consumed for ever, and MB r1 is never
  re-run.
* A successor is a **second** execution of cell 308. The user's own words ask for exactly one. The successor
  therefore needs the user's ruling expressly **notwithstanding** §21 and mitigation 5.

**S1 content, A1 §3 items 1–2, now read:**

1. authorise a **second consumed evaluation** of cell 308 (count 2) under the successor MB-S only, **notwithstanding
   the brief's §21 ("execute cell 308 exactly once") and mitigation 5**;
2. **lift mitigation 5 for the successor, and confirm that the brief's §20–§21 and §23 continue to bind MB r1
   unchanged** (MB r1 is never re-run; its marker stays consumed).

The brief put to the user for S1 shows §20, §21 and §23 verbatim, next to O1–O5. It also states the C11R-I2 / COR-T
deferral trade (route erratum E1, DR1).

## D2: time correction (exposure addendum E1″)

The successor builder was instructed about GC-6 at **2026-09-29 18:39:04Z**, not "~20:40Z". The same applies to A1
§4 S13 ("2026-09-29 ~20:40Z").

The coordinator's approximate "~HH:MMZ" annotations written this night (brief-index rows 24–34 and their erratum, E1″)
were not taken from a clock and are unreliable. **The UTC timestamps of the research-ledger lines are authoritative**
for every launch and instruction time.

## D3: holders of the MB r1 run observations (exposure addendum E1″)

The holder list is extended by:

* **reviewGOV**, the successor-governance reviewer, who read REVIEW_EXECUTION_INTERRUPTION §4b's per-coalition CPU
  figures;
* **the step-8 adjudication reviewer** (reviewADJ), who reads the recovery chain and the execution review.

Neither may take a successor route, implementation or caps role (S13).

## Note (delta review)

A1's "decisive argument" is **conditional on completion**. Byte-identical science makes the successor's certified
value equal to the value the lost run would have produced, **if** the successor completes (and, per route erratum E1,
if the platform pin holds at every resume).
