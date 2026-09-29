# MB308 execution interruption: addendum A1 (coordinator; not independent)

**Why.** Condition C1 of the independent review `reviews/REVIEW_EXECUTION_INTERRUPTION.md` (research `ef29bc2b`,
sha256 `e82c4524…3bfc3`, RECOVERY_ASSESSMENT_REJECTED as submitted).

**Status of the original.** The assessment `audit/EXECUTION_INTERRUPTION_ASSESSMENT.md` (research `8b64d989`) is kept
byte-unchanged. This addendum prevails where they differ.

**Scope.** A1 changes none of the answers A–E, the frozen outcome or the status lines.

**Method.**
* Read-only, from the system logs.
* The coordinator re-verified the entries quoted verbatim in (a) and (b).
* The pool-load fact in (a) rests on the review's powerlog reading (§4b). It is quoted qualitatively only.

## (a) The timeline gains the Force Quit at 23:29:00 JST (14:29:00Z)

* **23:29:00.047.** `loginwindow`: `-[ProcessPanel serverOptionsSheetDidEnd:returnCode:] | Forcequit confirmed,
  quitting app(s)`, then `-[Application terminateAppAndSubprocesses] | enter`.
* **23:29:00.050.** `Claude [97329] force quit (caller responsible for termination)`. This is the user's Force Quit
  dialog acting on the Claude desktop app. That app hosted the Claude Code session which had started the one-shot
  launcher.
* **23:29:00.275.** `launchd`: `removing child: pid/97329`. The review reports the app exited on SIGTERM sent by
  `loginwindow[402]`.
* **The power log, same second, shows both caffeinate processes of the run gone.**
  * `PID 56680(caffeinate) ClientDied PreventUserIdleSystemSleep … 02:31:01`. This is the launcher's `caffeinate -i`
    wrapper, created 20:57:59.
  * `PID 56814(caffeinate) ClientDied PreventUserIdleSystemSleep / PreventSystemSleep / PreventDiskIdle …
    02:30:59`. This is the driver's own `keep_awake()` (`caffeinate -i -m -s -w <driver pid>`), created 20:58:00.
* **From 23:29:00 the run had no sleep prevention, and its launcher and parent session were gone:** it was
  orphaned.
* **The computation continued after the Force Quit.** The review (§4b) reports that the Stage-1 pool load kept running
  at more than 4 cores until at least 23:40:48, and that the thermal-pressure context stayed at level 2 until the
  reboot. This is consistent with the frozen code. After the marker, the driver and every worker ignore SIGINT,
  SIGTERM, SIGHUP and SIGQUIT (`run_execute`, `_worker_init`). A SIGTERM-class termination of the app's subprocesses
  therefore killed `caffeinate` and left the driver and the workers running.

## (b) The power log's last entry before the boot is 23:40:35, not 23:38:46

23:40:35 is `cloudd Released SystemIsActive`. 23:38:46 was only the last periodic `Summary` block. The last
unified-log entry is 23:41:09.965, as stated.

## (c) The unknowns, restated

The Force Quit and its effects are established, so "What happened between 23:10 and 23:41 … is not established"
(original §6) is withdrawn. What remains unknown is exactly two things:

* **The exact moment the driver died.** Most probably after 23:29:00, since the pool load continued to at least
  23:40:48. At the latest, 00:00:15 (the boot).
* **The cause of the host's unresponsiveness after 23:41:09.**

Recorded only, and **not** claimed as causes:
* a `ReportMemoryException` (about 23:27:44–23:28:48, subject unidentified);
* a system memory-pressure warning (23:33:31);
* heavy Bluetooth and audio-accessory activity starting at 23:40;
* the PMU line `o2ws: 34 00 (gcb_wakeup auto_wakeup gcb_crash_wakeup)`, which is not interpreted.

There is no panic, watchdog or jetsam report.

## (d) The title and §1, restated

The one granted evaluation was **orphaned at 23:29:00 JST** by the user's Force Quit of the hosting Claude desktop
app. That quit ended its launcher, its parent session and both of its caffeinate processes. Stage-1 load continued
at least until 23:40:48. The host stopped logging at 23:41:09 and was **force-reset by the power button** at 00:00:15
(PMU `btn_rst,btn_seq_reset`), which ended the run at the latest. No evidence was ever persisted.

## (e) The object-store sentence, qualified (review N1)

* **Between the marker (20:58:01) and the reboot:** no object was written.
* **After the reboot:** the only objects written are those of the research commit `8b64d989` that carried the
  assessment (12 objects; type- and size-accounted by the review). None of them is a result object.

## (f) CONSUMED_UNRECORDED is a state label, not an exit code (review N3)

The driver never returned, so no exit code exists. The execution's state is the one that exit code 6 names, "the
marker exists and no evidence channel holds anything"; call it "state equivalent to CONSUMED_UNRECORDED; the driver
never returned". No exit code is recorded.

## (g) The launcher readings are coordinator-reported

The launch-time host readings were in /private/tmp and were erased by the reboot. They exist only in the
coordinator's session transcript:
* thermal-pressure level 0 on three consecutive reads;
* AC;
* lid open;
* lowpowermode 0;
* load 1.76;
* HEAD `afa93072`.

They are **coordinator-reported and unverifiable** now.

Independently of them, the marker proves that every pre-marker check passed, including `require_ac`, `check_clean`,
the grant chain, the pins, the governance state, the seal preconditions and both controls. The review adds that the
OS thermal-pressure context was 0 from 20:53:58 until 20:58:03.

## Unchanged

* **A:** no complete result was persisted.
* **B:** no pending or emergency state exists; `seal-only` is not applicable.
* **C:** the run ended before the persistence boundary, as confirmed by the continued pool load (review N4).
* **D:** no recovery other than `seal-only` is permitted, and `seal-only` has nothing to seal.
* **E:** the frozen outcome is **CELL308_EXECUTION_INDETERMINATE** (target consumed; no rerun).
* **TARGET_EVALUATION_COUNT** is 1.
* **Status:** cell 308 OPEN; r5 authoritative and unchanged; no r6; K5 PARTIAL; P5Y unchanged; route MB r1's single
  authorization exhausted.
* **The standing prohibitions (review C6)** remain in force.
