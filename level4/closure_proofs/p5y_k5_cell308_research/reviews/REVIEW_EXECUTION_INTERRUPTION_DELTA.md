# Delta review of addendum A1 to the MB308 execution-interruption assessment (reviewer reviewINT, resumed; condition C2)
DELTA_REJECTED

**Verdict.** DELTA_REJECTED, on two sentences only.

**What is accepted.** Everything else in A1 is correct, complete and not overstated. I accept it, together with the
C3 ledger line.

**What must change.**
* **(a)** A1 turns the review's "most probable, not proven" survival of the driver into a past-tense fact. That
  contradicts A1's own (c).
* **(e)** A1's object-store sentence was already false when A1 was written: two later research commits also wrote
  objects after the reboot.

**Remedy.** An erratum with the two replacements R1 and R2, followed by a re-check limited to them. Nothing about the
outcome, the count or the status changes.

## 0. Basis

**What I read.**
* A1 `audit/EXECUTION_INTERRUPTION_ASSESSMENT_ADDENDUM_A1.md`, research commit `e681d16f`.
* The research ledger at `8b64d989`, `ef29bc2b`, `e681d16f` and the worktree.
* My review `reviews/REVIEW_EXECUTION_INTERRUPTION.md`.

**What I did.**
* The work was read-only. Git reads in the formal worktree ran with `GIT_OPTIONAL_LOCKS=0`. Nothing was written in
  `/Users/suzhe/ReBaseGuard-c308mb`.
* No driver mode was run, and no ref, index or object was written.
* I read no content of any post-marker object. The objects of the research commits appear by id, type and count only.
* I computed nothing for cells 305–309 and evaluated no drift.
* I re-queried the log facts A1 quotes live, with `/usr/bin/log show` and `pmset -g log`.

## 1. Provenance: PASS

* The original assessment is byte-unchanged.
  * Its blob is `7e9a0a82…` at `8b64d989`, at `ef29bc2b` and at `e681d16f`, and it equals the worktree file.
  * Its sha256 is `a46e3e22…061d`.
  * The only commit touching it is `8b64d989`.
* A1 cites my review as research `ef29bc2b`, sha256 `e82c4524…3bfc3`. That matches the committed bytes and the
  worktree bytes.

## 2. A1 against C1(a)–(g)

| item | result | evidence |
|---|---|---|
| (a) Force Quit, caffeinate deaths, pool load | **FAIL, one sentence (R1)** | See the details below. |
| (b) power-log end | PASS | The last entry before boot is `23:40:35 … cloudd Released SystemIsActive`. The unified log ends at 23:41:09.965. |
| (c) unknowns | PASS WITH NOTE | See the details below. |
| (d) title and §1 restated | PASS | It matches the review's honest description. The reset is "at the latest", the unknowns are kept, and there is no causal claim about the hang. |
| (e) object-store sentence | **FAIL (R2)** | See the details below. |
| (f) CONSUMED_UNRECORDED as a state | PASS | "State equivalent to CONSUMED_UNRECORDED; the driver never returned"; no exit code is recorded. |
| (g) launcher readings | PASS | All six readings are labelled "coordinator-reported and unverifiable". What the marker proves is stated separately and correctly. The thermal context of 0 from 20:53:58 to 20:58:03 is attributed to the review. |

**(a) in detail.**
* Every verbatim fact re-verified:
  * `loginwindow … Forcequit confirmed, quitting app(s)` and `terminateAppAndSubprocesses | enter` at 23:29:00.047;
  * `Claude [97329] force quit (caller responsible for termination)` at .050;
  * `launchd … removing child: pid/97329` at 23:29:00.275463;
  * `exited due to SIGTERM | sent by loginwindow[402]` at .211;
  * the four power-log `ClientDied` entries: caffeinate 56680 with 02:31:01, and 56814 ×3 with 02:30:59.
* The pool-load fact is qualitative and attributed to review §4b. "More than 4 cores" is the review's own phrase;
  see N2.
* **The defect.** The sentence "A SIGTERM-class termination of the app's subprocesses therefore killed `caffeinate`
  and left the driver and the workers running" goes beyond the evidence.
  * The signal delivered to the subprocesses is not logged.
  * The driver's survival is "most probable, not proven" (review §4b). A1's own (c) says "most probably".
  * The review wrote this as a present-tense account of the mechanism, beside an explicit "not proven". A1's past
    tense turns it into an assertion of fact.

**(c) in detail.**
* The unknowns are exactly the two named: the moment of the driver's death ("most probably after 23:29:00 … at the
  latest 00:00:15") and the cause of the unresponsiveness after 23:41:09.
* The four recorded-only items are marked "not claimed as causes".
* See N1.

**(e) in detail.**
* A1 says: "After the reboot: the only objects written are those of the research commit `8b64d989` … (12 objects)".
* In fact the object store holds **33** objects written after the boot. They are exactly
  `git rev-list --objects c6c7cbe4..e681d16f`:
  * `8b64d989`, 12 objects;
  * `ef29bc2b`, 9 objects (my review, which A1 itself cites);
  * `e681d16f`, 12 objects (A1 itself).
* There is no pack, and still **no object between the marker and the reboot**.
* The sentence was already false when A1 was written. It is the very statement that N1 asked to qualify.

## 3. A–E, the outcome and the status: PASS

**The answers.**
* A, B, D and E are restated with unchanged substance.
* C is reworded from "the reboot came before the boundary" to "the run ended before the persistence boundary, as
  confirmed by the continued pool load (review N4)". The answer is unchanged. The new wording is the correct one
  after the orphaning, and it matches N4: no persisted evidence, and pool load until 23:40:48.

**Unchanged figures and status.**
* TARGET_EVALUATION_COUNT is 1.
* The frozen outcome is CELL308_EXECUTION_INDETERMINATE (target consumed; no rerun).
* Cell 308 OPEN; r5 unchanged; no r6; K5 PARTIAL; P5Y unchanged; route MB r1 exhausted.
* The C6 prohibitions are kept.

## 4. The C3 ledger line: PASS

**Append-only.**
* The ledger is strictly append-only across `8b64d989` (218 lines) → `ef29bc2b` (220) → `e681d16f` (221) → worktree
  (identical to `e681d16f`).
* The 2026-09-29T15:22:45Z line is byte-identical in every version.
* The sum of `new_target_evaluations` over the whole ledger is 1.

**The new line (utc 2026-09-29T17:40:48Z).**
* It is class INCIDENT, with `new_target_evaluations` 0, `cells_touched` [] and no LEAK_FLAG.
* Its purpose cross-references the 15:22:45Z line as "not edited".
* Its account matches A1 (d): orphaned at 23:29:00; the pool load continued at least until 23:40:48; stopped logging
  at 23:41:09; forced reset at 00:00:15; nothing persisted.
* Its two unknowns carry "most probably".
* Its notes are correct: the count stays 1, the outcome is unchanged, and the state is equivalent to
  CONSUMED_UNRECORDED.
* It contains neither of A1's two defects.

## 5. Required repairs (an erratum to A1, e.g. `audit/…_ADDENDUM_A1_ERRATUM_E1.md`; A1 itself stays byte-unchanged)

* **R1.** In (a), replace the sentence "A SIGTERM-class termination … therefore killed `caffeinate` and left the
  driver and the workers running" with the following text:

  > If the app's subprocesses received a SIGTERM-class signal (not logged), that would kill `caffeinate` and leave
  > the driver and the workers running. The continued pool load shows that the workers kept running; that the
  > driver survived is most probable, not proven.
* **R2.** In (e), replace the post-reboot sentence with the following text:

  > After the reboot, the only objects written are those of the research-branch commits made since (`8b64d989`,
  > `ef29bc2b`, `e681d16f`, and any later research commit). All of them are accounted for by id and type; none is a
  > result object.

  Do not give a fixed count that later commits would falsify.
* **R3.** A re-check of R1 and R2 only, by this reviewer resumed or a fresh one. It confirms that the erratum
  changes nothing else. Line 2 must read DELTA_ACCEPTED or DELTA_REJECTED.

## 6. Conditions that continue to bind (review C4–C6, restated)

**C4. The formal `postexec/` record.** It is made only after R3 returns DELTA_ACCEPTED, and only as review §8a
allows.
* **Form.** One additive commit under `NSF/postexec/`, a direct child of `afa93072`. It never touches
  `refs/p5y-k5-cell308-mb-r1/*` and never creates `evidence/` or any `GUARDED_PATHS` name.
* **Required statements.** It must use:
  * R2's form of the object-store statement;
  * the qualitative pool-load fact;
  * "driver death most probably after 23:29:00, at the latest 00:00:15";
  * "state equivalent to CONSUMED_UNRECORDED; the driver never returned";
  * the launcher readings labelled coordinator-reported.
* **Exclusions.** It contains no target, job-level, seal or exit-code content, and no causal claim about the hang.

**C5. §10 steps 6–8.** An execution review of the postexec record, the §8 adjudication applied verbatim, and an
adjudication review, each by a fresh reviewer, unless the user records otherwise before the adjudication. Whatever
their verdicts, there is no rerun.

**C6. Standing prohibitions.**
* No `execute`, and no `seal-only` (there is nothing to seal).
* No change to, and never a deletion of, any ref under `refs/p5y-k5-cell308-mb-r1/`.
* No new grant, rerun, resumption or recomputation for cell 308 under route MB r1 (E7).
* No proxy or reconstruction of any target quantity.
* r5 stays authoritative, with no r6.
* Read-only audits of the formal worktree use `GIT_OPTIONAL_LOCKS=0`.

## NOTES

* **N1** (c). "There is no panic, watchdog or jetsam report" should read "for the incident window". A
  `JetsamEvent-2026-09-27-114155.ips` exists but is unrelated. This is a wording note, not a repair.
* **N2** (a). "More than 4 cores" repeats the review's summary phrase. Two short intervals (2.9 and 4.0 cores, at
  23:33:30 and 23:34:50) sit at or below 4. For the postexec record, "Stage-1 pool load continued" is enough.
* **N3.** The formal state was re-verified during this delta:
  * the marker still points to `afa93072`;
  * no object was written between the marker and the reboot;
  * there is no pending ref, no emergency file and no `evidence/`.
