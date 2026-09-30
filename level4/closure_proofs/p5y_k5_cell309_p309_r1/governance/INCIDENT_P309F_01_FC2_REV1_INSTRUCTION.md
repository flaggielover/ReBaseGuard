# Incident P309F-01: the FC2(b) rev-1 brief instructed in-band synthetic tests and the REAL names in a sandbox

**Recorded because of:** delta review condition D4 (`reviews/REVIEW_DELTA_INCIDENT_P309.md` §7, commit e53a678c).
**Recorded:** append-only, before the freeze.
**Liability:** **NONE**.
**Responsible party:** the coordinator (author of P309; target-exposed), who wrote the brief.

## What was instructed

The brief is item 23 of `governance/briefs_recovered/AGENT_BRIEFS_TRANSCRIPT.jsonl`, "Build grant-scoped verifier
variant (FC2b)". It was sent to the verifier author at **2026-09-30T01:49:53.487Z** and has sha256 37fc8c14b9786f93….

It instructed two things:
1. **An in-band synthetic test band.** It asked for h = 3 certificates "at a test cell inside [3/2, 7/4]" to exercise the
   admission path. That interval lies inside the geometry-blind quarantined band [6/5, 13/5]. The research quarantine
   in force at the time already forbade in-band drift computation for any geometry. Had it been executed, it would have
   been an in-band computation. It would not have been a target evaluation: the geometry is synthetic and the cell is
   not 309.
2. **The REAL names in a sandbox.** It asked for sandbox admission tests using the **REAL** production marker name
   and a sandbox marker. Owner rulings 2 later classified any ref with the real marker name, even in a sandbox, as
   marker creation, and forbade it before the final grant (`governance/OWNER_RULINGS_2_P309_VERBATIM.md`).

## What happened

**Nothing was executed.**
* The verifier author's first attempt was stopped by a permission denial before any run.
* The partial rev-1 file was removed at the time.
* The record is `ledger/ZERO_TARGET_LEDGER.jsonl` lines 7 and 8: the author's start-of-work read-only inspections and
  the coordinator's retrospective record. Formal erratum FE-6 notes that both lines describe the same attempt.

No certificate, kernel run or admission check was made for any in-band drift. No ref with the production marker name
was created in any repository, sandbox or namespace.

## Withdrawal

The instruction was withdrawn and replaced by:
* `fc2/FC2_SPEC_R2.md` (commit 78bd6a98): the test band is the declared h = 3 decoy-cell hull [341/1024, 201/512],
  disjoint from the quarantined band, and only the synthetic TEST names are used;
* owner rulings 2 (FC2 test band; sandbox marker).

The rev-2 brief (item 25) and follow-up 1 superseded item 23.

## Why the liability is NONE

* No computation or ref creation happened, so no information about the target or the band was produced or seen.
* The delta review found that it "carries no information" (§4).
* The incident is recorded for completeness of the instruction record, not because any exposure occurred.

It is disclosed in the freeze parameters and in the proposed grant (delta review D3).
