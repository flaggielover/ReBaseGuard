# MB308 r1: authoritative recovery record of the one granted evaluation

This record is additive and made after the grant (`afa93072`). Per review C4 it contains no target, job-level, seal,
exit-code or causal-hang content. It is the formal-branch summary of the reviewed research recovery chain (§5 below).

## 1. Status

| field | value |
|---|---|
| MB308 r1 target evaluations | **1** (the one granted evaluation) |
| target-consumed | `refs/p5y-k5-cell308-mb-r1/target-consumed` → `afa930727d084a5b70e6b85d30ca8f34c0e8ae74` (the grant). This ref is never changed or deleted |
| complete durable target result | **none** |
| pending-result | **none** |
| emergency recoverable result | **none** |
| seal | **none**, and none can be made (`seal-only` would refuse: "no persisted evidence") |
| same-grant re-execution | **forbidden**, and mechanically refused by `check_not_evaluated` (CONSUMED) |
| execution status | **CELL308_EXECUTION_INDETERMINATE**; state equivalent to CONSUMED_UNRECORDED; the driver never returned |
| cell 308 scientific status | **OPEN**. No scientific positive or negative conclusion; no Γ value exists |
| r5 | unchanged, authoritative |
| r6 | none |
| K5 | unchanged: PARTIAL |
| P5Y | unchanged |

The frozen protocol §8 row applies verbatim:

| sealed status | condition | conclusion |
|---|---|---|
| INDEPENDENT_CHECK_FAILED, INCONSISTENT, C6 refusal, TARGET_EVALUATION_FAILED, POST_MARKER_RECORDING_FAILED, unsealable | any post-marker failure | **CELL308_EXECUTION_INDETERMINATE** (target consumed; no rerun) |

## 2. Corrected chronology (JST, +0900)

| time | event | strength |
|---|---|---|
| 2026-09-29 20:57:58 | the one-shot launcher runs `execute` once, after recording host readings: thermal-pressure level 0 on three reads, AC, lid open, lowpowermode 0 | the readings are **coordinator-reported**; the launcher record was lost with /private/tmp |
| 20:58:00 | pre-marker seal-precondition probes: blob `a1995184…` (31 B), trial commit `501388e2…` (253 B) | object store; ids recomputed from the frozen bytes |
| 20:58:01 | marker created (**target consumed**) | ref-file mtime. The marker proves every pre-marker check passed, both controls included |
| 23:29:00 | the user's Force Quit of the hosting Claude desktop app (`loginwindow` "Forcequit confirmed", `terminateAppAndSubprocesses`). Both caffeinate processes of the run died (the launcher's 56680 and the driver's `keep_awake` 56814), and the run was orphaned | system logs |
| 23:29:00–23:40:48 | Stage-1 pool load continued | review §4b (powerlog, qualitative) |
| 23:40:35 / 23:41:09 | last power-log / unified-log entries | system logs |
| 2026-09-30 00:00:15 | boot after a forced power-button reset (PMU `rst btn_rst,btn_seq_reset`); no orderly sleep, shutdown or restart entry | `kern.boottime`, kernel boot log |

**Driver death:** most probably after 23:29:00, at the latest 00:00:15. It is most probable, not proven, that the
driver survived the Force Quit. The cause of the host's unresponsiveness after 23:41:09 is **unknown**.

**Object store:**
* Between the marker and the reboot, no object was written.
* After the reboot, the only objects written are those of the research-branch commits made since (`8b64d989`,
  `ef29bc2b`, `e681d16f`, and any later research commit). All of them are accounted for by id and type; none is a
  result object.

## 3. Lost records

The launcher log, the execution log and the host-readings file were in the session's /private/tmp, which the reboot
erased. The driver prints nothing before the seal.

## 4. Standing prohibitions (review C6)

* No `execute`, and no `seal-only` (there is nothing to seal).
* No change to, and never a deletion of, any ref under `refs/p5y-k5-cell308-mb-r1/`.
* No new grant, rerun, resumption or recomputation for cell 308 under route MB r1 (E7). Lost information is recomputed
  only through a new independent governance process and a new user decision.
* No proxy or reconstruction of any target quantity.
* r5 stays authoritative, with no r6.

## 5. The reviewed recovery chain (research branch `p5y-k5-cell308-research`)

| document | commit | verdict |
|---|---|---|
| `audit/EXECUTION_INTERRUPTION_ASSESSMENT.md` | `8b64d989` | (assessment) |
| `reviews/REVIEW_EXECUTION_INTERRUPTION.md` | `ef29bc2b` | RECOVERY_ASSESSMENT_REJECTED as submitted (C1–C6) |
| `audit/EXECUTION_INTERRUPTION_ASSESSMENT_ADDENDUM_A1.md` | `e681d16f` | (addendum; with the C3 ledger line) |
| `reviews/REVIEW_EXECUTION_INTERRUPTION_DELTA.md` | `0b9020af` | DELTA_REJECTED (R1, R2) |
| `audit/EXECUTION_INTERRUPTION_ASSESSMENT_ADDENDUM_A1_ERRATUM_E1.md` | `c5f7c857` | (erratum) |
| `reviews/REVIEW_EXECUTION_INTERRUPTION_R3.md` | `98118e22` (sha256 `46be90b6…7b84`) | DELTA_ACCEPTED: the assessment as corrected by A1 and E1 is **RECOVERY_ASSESSMENT_ACCEPTED** |

Research ledger lines: 2026-09-29T15:22:45Z (INCIDENT, count 1) and its supplementary correction (INCIDENT, count 0).
