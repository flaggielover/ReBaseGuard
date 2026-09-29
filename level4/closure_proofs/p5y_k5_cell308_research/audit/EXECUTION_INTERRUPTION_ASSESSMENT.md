# MB308 execution interrupted by a host hard reset: recovery assessment (coordinator; not independent)

Everything below was determined read-only after the reboot. It is measured against the frozen bytes: protocol r3 at
freeze `c46434a3`, the grant `afa93072`, the driver `411252b2…`, and the qualification review `47bb37c7`'s E1–E8.
No target value exists, and none was read, inferred or reconstructed. No `execute`, no `seal-only`, no ref change and
no process signal was used.

## 1. Timeline (JST, +0900; UTC in brackets)

| time | event | source |
|---|---|---|
| 2026-09-29 20:57:58 (11:57:58Z) | the one-shot launcher records the host readings and runs `execute` once: thermal-pressure level 0 on three consecutive reads, AC, lid open, lowpowermode 0, load 1.76, HEAD `afa93072` | launcher record (lost with /private/tmp at the reboot; quoted in the session transcript) |
| 20:57:59 | driver process starts | `ps` lstart seen at 23:10 |
| 20:58:00 | pre-marker seal-precondition probes written: blob `a1995184…` (31 B, the fixed probe text, id verified from the frozen bytes) and trial commit `501388e2…` (253 B, never referenced) | object-store mtimes; `check_seal_preconditions` |
| 20:58:01 | marker `refs/p5y-k5-cell308-mb-r1/target-consumed` → `afa930727d08…` created by CAS: **target consumed** | ref-file mtime |
| 23:10 (14:10Z) | read-only audit: the same process tree alive, driver `56681` with 5 spawned workers computing; no pending ref, no emergency file, no result, no seal; no sleep since launch | session audit |
| 23:41:09 (14:41:09Z) | the last entry in the unified log; the power log's last entries are at 23:38:46 | `log show`, `pmset -g log` |
| 23:41 – 00:00 | no log entry of any process: the host was unresponsive, or not logging | `log show` |
| 2026-09-30 00:00:15 (15:00:15Z) | boot. The PMU fault log reads `rst btn_rst,btn_seq_reset`: a forced power-button reset. There is no orderly Sleep, Shutdown or Restart entry | `kern.boottime`; kernel boot log |

The execution had been running for about 2 h 43 min at the last log entry, and about 3 h 02 min at the reset. The
projected Stage-1 wall is 17 546 s (about 4.9 h) and EVAL_CAP is 8 h. The run was therefore mid-Stage-1, and the
EVAL_CAP had not been reached.

## 2. State after the reboot (read-only)

* **No MB308 process exists.** The driver, workers, resource tracker, caffeinate and launcher are all gone.
* **Refs.**
  * `refs/p5y-k5-cell308-mb-r1/target-consumed` = `afa930727d084a5b70e6b85d30ca8f34c0e8ae74`, the grant.
  * `refs/p5y-k5-cell308-mb-r1/pending-result`: **absent**. No other ref exists under the prefix.
* **Git dir** `/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-c308mb`: **no** `mb308-cell308-emergency-result.json`.
* **Result path.** `evidence/` does not exist, so neither does `evidence/execution/MB308_CELL308_RESULT.json`.
* **Formal worktree.** HEAD is `afa93072` on `refs/heads/p5y-k5-cell308-mb-r1`, and the namespace is clean including
  ignored files.
* **Object store.** The only objects written after launch are the two pre-marker probes of 20:58:00. **No object was
  written after the marker**, so no persisted result blob, commit or pack exists.
* **Logs.** The launcher log, the execution log and the host-readings file were in the session's /private/tmp
  scratchpad, which the reboot erased. The driver prints nothing before the seal, and the execution log was empty at
  23:10.

## 3. The frozen semantics that apply

* **§4, execution failures.** "MemoryError, OSError, worker death, a cap hit, a guard refusal and signals are
  execution failures (INDETERMINATE)". A host reset kills the driver and every worker.
* **§7, exactly-once mechanics.** "after the marker nothing escapes; seal from memory (object store, pending ref …)".
  The evaluation state lives only in memory until `after_marker` persists it after the evaluation (pending ref, else
  emergency file), then seals and materializes.
* **§8, frozen outcome table.** "INDEPENDENT_CHECK_FAILED, INCONSISTENT, C6 refusal, TARGET_EVALUATION_FAILED,
  POST_MARKER_RECORDING_FAILED, unsealable | any post-marker failure | **CELL308_EXECUTION_INDETERMINATE** (target
  consumed; no rerun)".
* **The driver's exit-code semantics** (docstring): "6 CONSUMED_UNRECORDED (never rerun)", meaning "the marker exists
  and no evidence channel worked. NEVER run execute again."
* **`run_seal_only`.** It needs a pending ref or an emergency file, else `Refusal("SEAL_ONLY", "no persisted evidence
  (no pending ref, no emergency file)")`. It never computes.
* **Qualification review E7.** "Never `execute` again; recovery goes through `seal-only` only … Lost result
  information is never recomputed without a new independent governance process."
* **E3.** Host provenance never changes the status, the outcome or exactly-once; no rerun and no reinterpretation on
  host grounds.
* **§10.** Execute once; a REJECTED review ⇒ STOP, no rerun.

## 4. Answers

* **A. Was a complete target result durably persisted before the reboot?** **No.** No pending ref, no emergency file,
  no result file, and no object written after the marker. An evaluation value, if one was ever formed in memory,
  was lost with the process. Given the projected wall and the run's age, the evaluation most probably never
  finished Stage 1.
* **B. Does any protocol-authorized pending or emergency state exist that permits `seal-only`?** **No.** The only
  channels `seal-only` accepts are the pending ref and the emergency file, and both are absent. `seal-only` would
  refuse with "no persisted evidence"; it cannot seal anything. It is not run.
* **C. Did the reboot come before the protocol's result-persistence boundary?** **Yes.** The boundary is
  `after_marker`'s `persist_pending`, reached only after `evaluator()` returns or fails. No persisted object exists,
  so the process died before that boundary.
* **D. Does the consumed exactly-once authorization permit any recovery other than `seal-only`?** **No.** The frozen
  rules allow no re-execution, no resumption, no reconstruction from partial state and no new evaluation under this
  grant (§8 "no rerun", driver "NEVER run execute again", E7). Recovering lost result information would need "a new
  independent governance process" (E7) and a new user decision. None is proposed here.
* **E. The execution verdict when no recoverable complete result exists.** Frozen outcome
  **CELL308_EXECUTION_INDETERMINATE**: target consumed, no rerun. The driver state is CONSUMED_UNRECORDED; the §8 row
  is "any post-marker failure … unsealable". **No seal exists, and none can be made.**

## 5. Report fields

| field | value |
|---|---|
| TARGET_EVALUATION_COUNT | **1** (the one granted evaluation, consumed at 20:58:01 JST; unrecorded) |
| target-consumed ref / hash | `refs/p5y-k5-cell308-mb-r1/target-consumed` → `afa930727d084a5b70e6b85d30ca8f34c0e8ae74` (the grant) |
| complete target value exists | **no** |
| pending-result exists | **no** (nor an emergency file, a result file or a post-marker object) |
| seal-only authorized | **not applicable**: no persisted evidence, and it would refuse |
| re-execution authorized | **no**, never under this grant |
| execution verdict | **CELL308_EXECUTION_INDETERMINATE** (CONSUMED_UNRECORDED; host hard reset, `btn_rst,btn_seq_reset`) |
| scientific cell-308 status | **unchanged: OPEN.** Not closed under MB. No scientific positive or negative conclusion: INDETERMINATE is not NOT_CLOSED, and no Γ value exists |
| effect on r5 | **none** (r5 authoritative; no r6; 308 never adopted) |
| effect on K5 / P5Y | **none**: K5 PARTIAL, P5Y unchanged |
| route MB r1 | its one exactly-once authorization is **exhausted**; the protocol is spent |

## 6. What is not done, and why

* **Not done:** no `execute`; no `seal-only` (nothing to seal); no marker change; no new grant; no reconstruction or
  proxy of any target quantity.
* **The prohibitions of §8, E3 and E7:** no reinterpretation on host grounds, and no change to r5, K5, P5Y or cell
  308's status.
* **The E2 host conditions** held at launch and at the 23:10 audit (AC, lid open; thermal pressure 2 during the run,
  recorded only). What happened between 23:10 and 23:41, and why the host became unresponsive, is not established.
  The forced reset is recorded by the PMU. By E3 this changes nothing in the verdict.

## 7. Proposed additive formal record (for the independent reviewer to rule on)

Following the cell-307 precedent (`postexec/`), commit on the formal branch, after the grant, only an additive
`postexec/` record. It would hold:

* the launch time;
* the post-reboot state of §2;
* this assessment's reference;
* the frozen outcome CELL308_EXECUTION_INDETERMINATE (CONSUMED_UNRECORDED).

No target value would be included, and no seal would be claimed. The research ledger gains one line:

* class INCIDENT (the research quarantine has no TARGET_EXECUTION class);
* `new_target_evaluations` 1, the consumed, unrecorded granted evaluation;
* the automatic LEAK_FLAG, explained in the notes.

Whether the protocol's §10 steps 6–8 (execution review, §8 adjudication, adjudication review) should then run on
this record, or whether the reviewed assessment suffices, is left to the reviewer and the user. §8 already fixes the
conclusion.
