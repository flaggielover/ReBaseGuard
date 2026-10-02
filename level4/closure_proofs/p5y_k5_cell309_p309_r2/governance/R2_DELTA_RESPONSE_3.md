# P309-r2: response to the second follow-up review (repair round 3; SF1–SF2, W1–W8)

**The review.** `governance/REVIEW_R2_DELTA_FOLLOWUP_2.md`: R2_DELTA_FOLLOWUP_2_ACCEPTED with conditions SF1 and SF2
and advisories W1–W8, read at `5273b908`. It is preserved verbatim in `1f5e7771`, with its sha256 in
`REVIEW_R2_DELTA_FOLLOWUP_2.sha256`.

**This record.**
* It is written by the coordinator and covers repair round 3, on 2026-10-02.
* It is committed with the repairs, **before** the cloud-tier re-drill that SF1 requires.
* It decides no owner question.

**Development checks before commit.** They ran in a scratch clone of the branch with the changes copied in, so their
ledger rows stayed in that clone:
* QC12 T1–T14, the scanner and the pins;
* `tests/test_p309_host.py` 73/73;
* `tests/test_p309_host_controls.py` 37/37, plus K01 repeated 6 times and A01 repeated 3 times, all passing, with no
  TEST process left afterwards;
* `tests/test_p309_static_controls.py` 22/22;
* `tests/test_p309_scan_allowance.py` 19/19;
* `code/p309_placeholder_check.py`: no unallowed hit.

The re-drill runs all of them, plus the long suites. NEW Γ309 TARGET EVALUATIONS = 0.

**A correction to `R2_DELTA_RESPONSE_2.md`.** Under V5, that record said "the worst case is about 87 s" against a 105 s
limit. The reviewer showed that this was wrong. Timing each row at its sample's start put up to a whole sample (about
47 s at worst) into the gap at the stop, so the worst case was about 107 s, over the limit. Response 2 stays as written;
this paragraph corrects it.

## Conditions

| id | label | what was done | where | shown by |
|---|---|---|---|---|
| SF1 | before freeze; before 8d | Each sample now writes a **start-of-sample row** and a **result row**, both carrying a CLOCK_MONOTONIC time `m`. The runner takes its own start and stop on the same clock, which is system-wide on Linux, and passes **every** event's time to `monitor_liveness`. Q-HOST passes only if at least one sample completed and every completed sample passed. While samples last under 60 s, every gap is at most max(sample duration, 60 s), whatever the stop's timing. A wall-clock step can no longer open a false gap. The tolerance stays 45 s (limit 105 s), now a margin of 45 s over 60 s. The monitor loop's world (clock, sampling, parent check, signal, output) is one object, `MonitorIO`, so that a test can drive the committed loop on a virtual clock | `code/p309_host.py` (`MonitorIO`, `qhost_monitor`, `monitor_liveness` docstring); `code/p309_qualify.py` (`start_qhost_monitor`, `stop_qhost_monitor`) | `tests/test_p309_host.py` MV01–MV05. The committed loop runs on a virtual clock and `monitor_liveness` is applied at every stop time from 100 s to 1100 s in 0.5 s steps. **MV01:** with 47 s samples, the largest gap is 47 s and every stop passes. **MV02:** mixed durations, the same. **MV03:** round 2's scheme on the same run reaches 106.5 s and fails, so the control tells the two apart. **MV04:** a sample stuck for 120 s fails. **MV05:** a failed sample signals the parent once and stops. S01 and A01 now also check the two event kinds. The texts are revised in the same commit: AWS §3.1, host requirements §6, packet OD-R2-5, amendments §H1 |
| SF2 | before freeze; before 8d | The checks that need the §3.1 file now use the launcher's `--print-only` in a fresh check directory that is never a run's scratch root. It reads the file through `load_launch_config`, runs the preflight, the gate and the isolation check, and writes one redacted record. This covers the 8c checks (AWS §3), §4.1 step 2 (the gate rows) and §4.1 step 4 (a separate check directory as `--mode official`, then the launch with another empty scratch root). The text also says that `p309_host.py --config` reads a configuration without the six launch settings | `R2_AWS_SESSION_INSTRUCTIONS.md` §3, §4.1; `R2_BOOTSTRAP.md` 8c | text only, as the reviewer stated |

## Advisories

| id | done | note |
|---|---|---|
| W1 | yes | `kill_own_descendants` now checks a pid's start time before its SIGSTOP as well as before its SIGKILL. A walk ends only when it finds nothing new **and** every descendant seen is stopped (`T`/`t`) or gone; otherwise it waits 5 ms and walks again. That catches a child linked just before an asynchronous SIGSTOP took effect |
| W2 | yes | `MonitorIO.signal_parent` re-checks `os.getppid() == parent` immediately before `os.kill(parent, SIGTERM)` |
| W3 | yes | The launcher refuses a foreign root that is not an absolute path of `[A-Za-z0-9._/+@,=~-]`, so `:`, `$`, `;`, `(` and the like are refused. Controls N05 and N06. Amendments §H2 |
| W4 | yes | The registered reasons of `case_a01` and `case_k01` are corrected in this configuration change, with the re-pin |
| W5 | yes | T14 also rejects an `assert`, and a call of `exit`, `_exit`, `abort`, `quit`, `kill`, `killpg` or `raise_signal` by any name or attribute, including a name bound by `from … import … as …` anywhere in the file. The docstring states that the check is syntactic. New mutants T14i (assert), T14j (aliased exit) and T14k (self-signal) are caught; the static controls are 22/22 |
| W6 | partly | `tests/test_p309_host_controls.py` U01–U03 reach three in-unit refusals from inside the launched unit: an altered configuration file, an altered configuration hash, and another boot. They run on the worker tier only; the cloud tier records `U00 not applicable`. The unit-property and instance-id branches cannot be forced from inside a correct unit and are exercised nowhere. That is recorded in amendments §H3, AWS §4 and here |
| W7 | yes | A01's TEST forkers now keep forking until the abort (`while True`, every 50 ms). AWS §4 states that 8d does not exercise the unit's KillMode/SIGKILL backstop after an abort, nor the drill's stop on exit status 3, and that its report must say so |
| W8 | yes | AWS §4.1 step 2 adds read-only listings of timers (`systemctl list-timers --all`) and system cron files. It asks the administrator for per-user crontabs, which the P309 user cannot read. Step 3 includes them in the window's agreement |

## Re-pins

`governance/R2_REPIN_LIST_SUPPLEMENT_3.json` lists 10 rows against `5273b908`:
* new: `MonitorIO.sample`, `MonitorIO.signal_parent`, `_state` and the U case;
* re-pinned: `kill_own_descendants`, `qhost_monitor`, `start_qhost_monitor`, `stop_qhost_monitor` and the A01 case;
* reason only: the K01 case.

The exactly-once sites, the backstop pins, the T13 pins and the production tokens are unchanged.

## Changes to the code a reviewer should know

* `code/p309_host.py`: `MonitorIO`, `qhost_monitor`, `kill_own_descendants`, `_state`.
* `code/p309_qualify.py`: the monotonic start and stop; liveness over all events; completed samples only.
* `code/p309_launch.py`: the W3 character set.
* `code/p309_static_check.py`: the W5 extension of T14.
* `code/p309_self_audit.py`: IMMUTABLE adds the second follow-up's brief, review, ledger and sha256 record.

Nothing in the driver, guard, verifier, generators or scanner code changed in this round.

## Environment

Two container restarts happened in round 2:
* the first interrupted drill attempt 7, preserved as `20261001T222108Z_INTERRUPTED`;
* the second came after attempt 8 had written its evidence.

Both are in the attempt 8 validation record.
