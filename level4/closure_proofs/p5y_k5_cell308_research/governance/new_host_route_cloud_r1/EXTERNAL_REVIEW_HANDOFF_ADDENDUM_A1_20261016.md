# External review handoff, addendum A1 (Cell-308 Cloud route r1): after B1's report

**Status: PREPARED HANDOFF · NOTHING LAUNCHED BY THE COORDINATOR SIDE · NO REVIEWER APPOINTED BY IT.** This addendum adds
to `EXTERNAL_REVIEW_HANDOFF_20261016.md` (`842463b3…a3b1`), which is preserved unchanged. Where they differ, this
addendum governs. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. State of each handoff

| id | state | brief (sha256) | pin | runs after |
|---|---|---|---|---|
| **B1** | **Report recorded** (`reviews/external/REVIEW_EXTERNAL_B1_CONFORMANCE.md`, `cf1a4b18…8e41`). Bounded corrections made at `f9b28704eff7df76ed0240ca3b7149d0e161040d`. **One correction confirmation** is pending | the correction package, committed after this file, which pins this file's commit (§2) | this addendum's commit | the owner forwards the package |
| **B2** | **unchanged.** It may proceed independently | `ledger/briefs/B2_EXTERNAL_INCIDENT_REVIEW_READING_CLOUD_R1.txt` (`e7b9ca96…c210`) | `f814fe84053bf8df61149e3d07bbc00aea50846c` | statement 1 |
| **B3** | **revision r2** replaces r1 (r1 preserved). L-DET erratum E3, L-DET erratum E2 and procedure erratum E1 are added; matrix R4 replaces matrix R3 (B1 X6) | `ledger/briefs/B3_EXTERNAL_PROVENANCE_CHECK_CLOUD_R1_R2.txt` (sha256 in this commit's ledger line) | `f9b28704eff7df76ed0240ca3b7149d0e161040d` | B2's released output, with its digest verified |
| **S12X** | **new**, CONDITIONAL. It is launched only if the owner's statement 1A requires re-commissioning (Q8-7) or a rating with standing beyond advice (Q8-8) | `ledger/briefs/S12X_EXTERNAL_RISK_RATING_CLOUD_R1.txt` (sha256 in this commit's ledger line) | `f9b28704eff7df76ed0240ca3b7149d0e161040d` | statement 1A; B2's output and B3's output are optional additional inputs |

**Distinct persons or sessions.**
* B2's reader takes no later role.
* B3 is not B2.
* S12X is none of B1, B2, B3, reviewerS12, reviewerFR1, reviewerFR2 or any coordinator session.
* B1's confirmation goes to the **same** B1 reviewer. There is no replacement B1.

## 2. B1's single correction confirmation

The owner forwards the correction package `ledger/briefs/B1_CORRECTION_CONFIRMATION_CLOUD_R1.txt` to the same reviewer,
B1-External (Codex). The package is committed after this file, and its sha256 is given in its own ledger line and to
the owner.
* It pins one commit: the commit of **this** addendum. That commit holds the corrected files (from
  `f9b28704eff7df76ed0240ca3b7149d0e161040d`, unchanged) and the briefs S12X and B3 r2.
* It asks only whether X1–X6 are corrected, and whether any correction introduced a new defect, weakened an accepted
  text or presented a proposal as accepted.
* The reviewer reports to the owner directly. The owner releases the output to branch `owner-review/cell308-B1` as
  `reviews/external/REVIEW_EXTERNAL_B1_CORRECTION_CONFIRMATION.md`, or hands it over.
* There is no further round.

## 3. How the owner launches B3 r2 and S12X

As handoff §2, with these differences:
* **Reviewer choice:** a human; or a Claude session under an account other than the coordinator's; or, if the owner's
  appointment expressly permits it, an agent on another platform launched by the owner outside the coordinator's
  access and control (the owner's B1 precedent).
* **B3 r2:** give the reviewer the r2 brief and B2's released output with its sha256. If B3 was already launched under
  r1, follow the substitution note at the top of r2.
* **S12X:** only after statement 1A requires it (owner package R4 §3). Record the appointment, identity, brief sha256
  and date in the owner's own record.

## 4. What the coordinator side does on release

As handoff §3, and also:
* **B1 confirmation:**
  * record it verbatim;
  * mark an X-item's corrections "confirmed (text)" in the register only where B1 confirms them;
  * record VC only where the owner accepts B1's standing for that item.
* **S12X:** record verbatim. One bounded correction round, then one confirmation by the same rater. The rating stays
  advice unless the owner adopts it with the standing Q8 describes.
