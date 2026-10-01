# P309-r2: response to the follow-up review (repair round 2; FU1–FU4, V1–V10)

**The review.** `governance/REVIEW_R2_DELTA_FOLLOWUP_1.md`: R2_DELTA_FOLLOWUP_1_ACCEPTED with conditions FU1–FU4 and
advisories V1–V10, read at `bbfc24f0`. It is preserved verbatim in `a065aeaa`, with sha256 in
`REVIEW_R2_DELTA_FOLLOWUP_1.sha256`.

**This record.**
* It is written by the coordinator for the repair round of 2026-10-01 and 2026-10-02.
* It is committed with the repairs, **before** the cloud-tier re-drill that FU2 (c) requires.
* That drill's evidence and its independent validation are named in the next follow-up brief.
* It decides no owner question.

**Development checks before commit.** These ran in a scratch clone of the branch with the changes copied in, so their
ledger rows stayed in that clone:
* QC12 T1–T14, the scanner and the pins;
* `tests/test_p309_host.py` 68/68;
* `tests/test_p309_host_controls.py` 35/35;
* `tests/test_p309_static_controls.py` 19/19;
* `tests/test_p309_scan_allowance.py` 19/19;
* `code/p309_placeholder_check.py`, with no unallowed hit.

The D5 suite and QC16 were not re-run in development: the scanner's code is unchanged in this round. The re-drill runs
both. NEW Γ309 TARGET EVALUATIONS = 0.

## Conditions

| id | label | what was done | where | shown by |
|---|---|---|---|---|
| FU1 (a) | blocking before owner decisions | The packet, the AWS instructions, the host requirements and the amendments state the facts. The runner refuses unless Restart, KillMode, KillSignal, NoNewPrivileges, PrivateTmp and ProtectSystem have the launcher's values. MemoryMax, OOMScoreAdjust, CPUWeight, IOWeight, SendSIGKILL, TimeoutStopSec and InaccessiblePaths are set by the launcher's command and recorded in `UNIT_PROPERTIES.json`, but not checked. The code is unchanged here: these systemd output formats cannot be verified without a systemd host | `OWNER_DECISION_PACKET_R2.md` (OD-R2-4); `R2_AWS_SESSION_INSTRUCTIONS.md` §4 and §8; `R2_HOST_REQUIREMENTS.md` §2; `P309_R2_AMENDMENTS.md` G2 | the texts |
| FU1 (b) | blocking before owner decisions | OD-R2-5 states that `unattributable` covers every other non-root uid that P309 cannot attribute: service accounts, other sessions, an access user other than the P309 user. The windows are agreed for the whole host. "Exactly when the right-hand column fires" is replaced by the full list of what ends the attempt: the right-hand column, a continuity break, the monitor's death or a gap over 60 s + 45 s, and a failed final sample. V8's detection time is corrected | `OWNER_DECISION_PACKET_R2.md` (OD-R2-5); `R2_HOST_REQUIREMENTS.md` §6; `P309_R2_AMENDMENTS.md` G3 | the texts |
| FU2 (a) | before freeze; before 8d | `kill_own_descendants` rewritten. Each round walks the whole tree below the caller again, **through** descendants already stopped, and SIGSTOPs every one not yet seen. The rounds end when a full walk finds nothing new; a stopped process cannot fork. Every pid is then SIGKILLed only if its start time (`/proc/<pid>/stat` field 22) is still the one recorded when it was found (V7). The docstring is corrected | `code/p309_host.py` | K01, extended: a three-deep TEST tree plus two descendants that keep starting TEST children during the call, all ignoring SIGTERM, must be dead at once, the caller alive, and a TEST process outside the tree untouched. **Mutation check** (development, scratch copy): the previous function failed K01 in 5 of 8 runs, with 1–3 survivors; the new one passed every run |
| FU2 (b) | before freeze; before 8d | A01, an end-to-end abort control. A child process installs the runner's own `_qhost_abort`, with the attempt pointed at a TEST directory and the `host_rerun` label, so nothing is written in qualification/. It starts a SIGTERM-ignoring TEST tree that keeps starting children, then a real monitor with a failing baseline. The monitor signals the child; the abort kills the tree, writes `QHOST_FAIL.json` and the failed `QC10_HOST_RERUN.json`, logs its row, and exits 3. An outside TEST process is untouched. A test may not redirect the guard's ledger (QC12 T7, MODULE_ATTRIBUTE_STORE), so the abort's own row goes to the namespace ledger. A01 first logs a row saying that the next row comes from this TEST control and that no host re-run ran, and it checks that exactly one abort row was added. The drill runs A01 in both tiers | `tests/test_p309_host_controls.py` | A01a–A01e |
| FU2 (c) | before freeze; before 8d | a re-drill on these bytes, after this commit; the next follow-up review covers it | evidence/drill (next attempt) | the next brief |
| FU3 | before freeze | `P309_R2_AMENDMENTS.md` is append-only, so section **G1** is appended. The list of governance additions after D lives in a separate file added at the freeze step (`governance/R2_GOVERNANCE_ADDITIONS_AFTER_D.json`), which rule 2 allows as an addition. The amendments file and every other governance file are not modified between D and F. §E is superseded | `P309_R2_AMENDMENTS.md` §G | the text |
| FU4 | before freeze; before 8d | `R2_AWS_SESSION_INSTRUCTIONS.md` §4.1 sets the procedure: (1) every P309 process runs as the P309 user; (2) the gate is run and preserved as the P309 user after 8c; (3) each non-root uid in its rows is identified, and the window is agreed with every workload shown; (4) before an official launch, the launch record's gate rows are checked against that agreement | `R2_AWS_SESSION_INSTRUCTIONS.md` §4.1 | the text |

## Advisories

| id | done | note |
|---|---|---|
| V1 | yes | T14 also requires that no `raise`, `sys.exit`, `os._exit`, `exit`, `quit` or `os.abort` occurs between the attempt's mkdir and the final return. New mutants T14f (raise), T14g (sys.exit) and T14h (os._exit) are caught; the static controls are 19/19 |
| V2 | yes | The launcher refuses a foreign root containing whitespace, a quote or a backslash (control N05) |
| V3 | deferred | The in-unit refusal branches of `qhost_preflight` (configuration file, configuration hash, unit properties, instance id) need a systemd unit. They are to be exercised at the worker-tier drill (8d); no test seam was added to the runner |
| V4 | yes, as a blocker | The launcher records the blocker `launcher_not_unit_user` unless its own uid is the unit user's. It is a blocker rather than a refusal, so the record (with its redaction) is still written and reviewable (control N04d) |
| V5 | yes | Each monitor row is timed at the start of its sample, and the default `monitor_gap_tolerance_s` is now 45 s (limit 105 s; the worst case is about 87 s). The AWS configuration example is updated |
| V6 | yes | `proc_read` is declared a register in `process_policy.proc_read_note` (the scanner does not enforce it). The list adds `exclusion_gate`, `durability_preflight`, `qhost_preflight`, `_start_time` and the controls' /proc readers |
| V7 | yes | the start-time check in `kill_own_descendants` (FU2 (a)) |
| V8 | yes | detection time stated as about 80–90 s |
| V9 | yes | self-audit A3's IMMUTABLE list adds the follow-up brief, the review, its ledger and its sha256 record |
| V10 | done | See below |

**V10.** The delta reviewer, a subagent of this session, left two TEST busy loops running: pids 19667 and 19669, from
18:32Z. The follow-up reviewer found them; the delta review stays verbatim. The coordinator then:
* confirmed their command lines (`TESTONLY_unmatched_job …`, `TESTONLY_fake_cell308_job …`);
* confirmed their working directory (the delta reviewer's scratch TEST root);
* SIGKILLed them on 2026-10-01 after 21:40Z.

They ran through drill attempt 6 and competed for CPU (QC16 took 913 s, against 679 s in attempt 5). No verdict
depends on them.

## Re-pins

`governance/R2_REPIN_LIST_SUPPLEMENT_2.json` has 13 rows against `bbfc24f0`:
* re-pinned: `kill_own_descendants`, `_children_map`, `qhost_monitor`, the launcher's `main`, the K01 case;
* new: the A01 case, the cleanup `kill_token`, the /proc register entries.

The exactly-once sites, the backstop pins, the T13 pins (functions and constants) and the production tokens are
unchanged. The scanner code is unchanged in this round.

## Changes to the code a reviewer should know

* `code/p309_host.py`: `kill_own_descendants`, `_children_map`, `_start_time`; the monitor's row time; the default
  `monitor_gap_tolerance_s`.
* `code/p309_launch.py`: the V2 refusal and the V4 blocker.
* `code/p309_static_check.py`: T14's V1 check.
* `code/p309_self_audit.py`: the V9 IMMUTABLE additions.

Nothing in the driver, guard, verifier, generators or scanner code changed in this round.
