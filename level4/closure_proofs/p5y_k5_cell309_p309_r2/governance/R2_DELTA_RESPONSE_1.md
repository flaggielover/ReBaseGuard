# P309-r2: response to the delta review (conditions C1–C15, advisories A1–A16)

**The review.** `governance/REVIEW_R2_DELTA.md` (R2_DELTA_ACCEPTED with conditions; sha256 in
`REVIEW_R2_DELTA.sha256`).

**This record.**
* It is written by the coordinator and covers the repair round of 2026-10-01.
* It states what was changed for each condition, where, and what shows it.
* It decides no owner question. Conditions that need the owner, or the AWS worker, are marked so and left open.
* It is committed together with the repairs, **before** the cloud-tier re-drill. The re-drill's evidence directory
  and its independent validation are recorded in the follow-up review brief (`BRIEF_R2_DELTA_FOLLOWUP_1.md`) and in
  the overnight report. The review itself said the re-drill follows C2–C11 and C14.

**How the changes were checked before commit.** In a scratch clone of the branch, with the changed files copied in:
* QC12 T1–T14;
* the scanner and the pins;
* `tests/test_p309_host.py` (68 cases), `tests/test_p309_host_controls.py` (26) and
  `tests/test_p309_static_controls.py` (16);
* `tests/test_p309_scan_allowance.py`, the D5 control suite and `code/p309_placeholder_check.py`.

Their ledger rows stayed in that clone. They are development runs and are not evidence. The committed evidence is the
re-drill, which runs every one of them again in its own clone and ledgers each.

NEW Γ309 TARGET EVALUATIONS = 0. No production-namespace ref was created. r1 is unchanged (`c902fe2f`, tree
`ecd1c359`). Cell 308 was not touched.

## Conditions

| id | label (review) | what was done | where | shown by |
|---|---|---|---|---|
| C1 | blocking before owner decisions | (a) OD-R2-6: the frozen field's behaviour before and after C8; host re-run gating (C7); execute not gated, with the amendments §C rule; the proposal tool's host field. (b) OD-R2-5: the two definitions of "heavy" in a table, the one-sample grace, the separate-user visibility limit and `foreign_uids`, the detection and termination times. (c) OD-R2-4: the unit limits and kill settings; polkit only (no sudo in the code); a world-readable cell-308 checkout fails `isolation` and would need a §6 amendment. (d) OD-R2-0: message 4 recorded in its own file; the proposed authorization separates the qualification host from the execution host | `governance/OWNER_DECISION_PACKET_R2.md` | the packet text |
| C2 | before freeze; before 8d | `foreign_uids` (required non-empty, not the P309 user's uid: gate check `foreign_uids_configured`). A process of another non-root user whose cwd cannot be read is `unattributable`: it blocks the start like a foreign process and counts in the monitor. Kernel threads and zombies are not classified | `code/p309_host.py` (`classify`, `_snapshot`, `gate_checks`, `monitor_verdict`) | `tests/test_p309_host.py` G15–G18, K01–K06, M08; `tests/test_p309_host_controls.py` P02 (the reviewer's setup: a TEST busy process under one TEST uid, cwd in a mode-700 TEST root, a non-matching command line, observed by the gate under another TEST uid; it is unattributable and blocks the gate and the monitor; with its uid configured it is foreign) |
| C3 | before freeze; before 8d | `continuity` is symmetric: a missing instance id on either side falls back to boot, machine-id and hostname, and is reported as `instance_unverified`. `qhost_preflight` refuses before the attempt if the launch read an instance id and the baseline could not | `code/p309_host.py` `continuity`; `code/p309_qualify.py` `qhost_preflight` | `tests/test_p309_host.py` C09–C11 |
| C4 | before freeze; before 8d | `monitor_liveness`: Q-HOST fails if the monitor is dead at the stop, wrote no sample, or any gap between the start, the samples and the stop exceeds the interval (60 s) plus `monitor_gap_tolerance_s` (30 s). Monitor rows carry an epoch time | `code/p309_host.py`; `code/p309_qualify.py` `stop_qhost_monitor` | `tests/test_p309_host.py` V01–V06 |
| C5 | before freeze; before 8d | The unit has `KillSignal=SIGKILL`, `SendSIGKILL=yes` and `TimeoutStopSec=10s`. On a Q-HOST abort, the runner first calls `kill_own_descendants()` (SIGSTOP the whole own tree until no new pid appears, then SIGKILL every pid), then records the failure and exits 3. The worker-tier drill stops at once when the runner aborts | `code/p309_launch.py`; `code/p309_host.py`; `code/p309_qualify.py` `_qhost_abort`; `code/p309_topology_drill.py` `run_items` | `tests/test_p309_host_controls.py` K01 (a three-deep TEST tree ignoring SIGTERM is dead at once; the caller survives). **Worker-tier evidence is still needed**: only the AWS worker has systemd units; that is step 8d |
| C6 | before freeze | QC12 **T14**: in `main()` and `host_rerun()`, there is exactly one `qhost_preflight` call with the modes each needs. It and every refusal return come before the single `os.mkdir` of the attempt. The start line is logged right after that mkdir. The monitor starts before any work and stops after it | `code/p309_static_check.py` | QC12 T14 PASS; negative controls T14a–T14e in `tests/test_p309_static_controls.py` |
| C7 | before freeze | `--host-rerun` runs only under the launcher's new `host-rerun` mode (unit `p309-r2-hostrerun-<utc>`, empty scratch root), with Q-HOST before the attempt, the monitor, liveness and the final sample. Its result fails if Q-HOST fails. How execute would be gated on a shared host is settled as a rule: only after a reviewed amendment | `code/p309_launch.py`; `code/p309_qualify.py` `host_rerun`; `governance/P309_R2_AMENDMENTS.md` §C | T14 (host_rerun); host test L05 |
| C8 | before freeze | `qualification_rule` names Q-HOST and the launcher. `proposed_execution_host` names a host only from the owner's own OD-R2-6 answer file (`governance/OWNER_OD_R2_6_ANSWER.json`, which does not exist); otherwise `{"named": false, …}`. The execution-host derivation text states the host-re-run and execute rules. P8(d) is recomputed with these three differences classified. P8(e) (runtime and host differences) is produced at the worker freeze | `code/make_freeze_params.py` | P8 round 2 (after the re-drill) |
| C9 | before freeze; before 8d | The launch record (schema `P309_R2_LAUNCH/2`) is redacted. Foreign roots and patterns appear only as sha256, in `host_config` and in `argv`. It binds the configuration file (`host_config_file_sha256`) and the full configuration (`host_config_sha256`). The unit gets `P309_HOST_CONFIG`, and the runner reads that file and checks both. The monitor gets its configuration on standard input. The attempt keeps `LAUNCH_RECORD.json` (a copy) and `UNIT_PROPERTIES.json` (`systemctl show` of its own unit, redacted), with their sha256 in `QHOST_BASELINE.json`. The runner refuses unless the unit's effective properties are the launcher's. The worker-tier drill embeds the record and the properties | `code/p309_host.py` (`redacted_config`, `config_sha256`, `load_launch_config`, `unit_properties`); `code/p309_launch.py`; `code/p309_qualify.py`; `code/p309_topology_drill.py` | `tests/test_p309_host.py` R01, R02, L06; `tests/test_p309_host_controls.py` N04 (a `--print-only` record holds the TEST foreign root only as its sha256, and binds the file) |
| C10 | before freeze | Negative controls for T11–T14, run in a scratch copy: 15 mutants plus the unmutated and restored copies | `tests/test_p309_static_controls.py` | 16/16; run by the drill |
| C11 | before freeze; before 8d | The P9–P11 controls as committed tests with a ledger row: a TEST busy process through the real /proc (P01); the cross-uid case (P02); the runner's Q-HOST refusals in child processes, with nothing written in qualification/ (Q01–Q07); the launcher's refusals and `--print-only` blocked (N01–N04); the monitor FAIL → one SIGTERM to its parent (S01); `kill_own_descendants` (K01); the C14 binding (B01–B03) | `tests/test_p309_host_controls.py` | 26/26; run by the drill |
| C12 | before freeze | The amendments record: r2's production names (provisional OD-R2-1 (b)); the FC2_SPEC_R2 §6 forbidden-names rule amended by addition (both namespaces forbidden); how r2 reads FC2_SPEC_R2's r1 names | `governance/P309_R2_AMENDMENTS.md` §A, §B | the file |
| C13 | before freeze | The tree binding stated as git commands: the code, config, fc2, tests and verify tree ids at F equal the drilled commit's; governance/ differs only by additions listed in §E; freeze/ holds only the generated files; nothing is added to a frozen directory after F; post-freeze reviews go to `reviews/` | `governance/P309_R2_AMENDMENTS.md` §D, §E | the file |
| C14 | before freeze | The manifest's runtime gains `glibc` and `interpreter_sha256` (`make_freeze_manifest.runtime_identity`). The driver's `check_bindings` compares python, implementation, glibc and the interpreter binary's sha256 (`runtime_identity`, `RUNTIME_KEYS`), and refuses `RUNTIME` on any difference | `code/make_freeze_manifest.py`; `code/p309_driver.py` | `tests/test_p309_host_controls.py` B01–B03. `check_bindings` is outside the T13 closure, so T13's pins are unchanged |
| C15 | before freeze; before 8a | 8a uses `foreign_patterns` and `foreign_heavy_patterns`; the refused key is named | `governance/R2_BOOTSTRAP.md` | the file |

## Advisories

| id | done | note |
|---|---|---|
| A1 | yes | the `ref_mutation_functions` reason for the drill's `controls` says `reset --mixed` |
| A2 | yes | R2-M01a counts as caught only with the uncaught `\np309_driver.Refusal: FREEZE_RECORD: ` line |
| A3 | yes | the drill's ledger verdict requires exactly one RUN START row and a row from each of nine required scripts (`completeness` in the report) |
| A4 | yes | the drill refuses unless the P309 namespace's working tree is clean |
| A5 | yes | self-audit A3's IMMUTABLE list adds the delta brief, the delta review with its ledger, and the three `.sha256` records |
| A6 | yes | the unit environment sets `GIT_CONFIG_GLOBAL=/dev/null` |
| A7 | yes, as a rule | The scanner has two new kinds. **SIGNAL_UNLISTED**: `os.kill`, `os.killpg`, `signal.pthread_kill`, `signal.pidfd_send_signal`, or a `.send_signal`/`.terminate`/`.kill` call, outside a reviewed function with the permit `signal`. A self-signal `os.kill(os.getpid(), …)` is not counted. **SIGNAL_ALIAS**: importing or binding these names. The planted control fires both. Registered with the `signal` permit: `qhost_monitor`, `kill_own_descendants`, `stop_qhost_monitor`, the host controls' `stop`, and the verifier's `verify_cert` (its pool's `terminate`; the verifier file is unchanged) |
| A8 | yes | `monitor_aggregate_cpu_fraction` (1.0 core) over foreign and unattributable processes |
| A9 | yes | `foreign_stat` records `world_readable` |
| A10 | yes | T13 also pins the 23 module constants the closure reads (`production_read_path_constant_pins`). 22 equal r1's F; `NS_REL` differs by the relocation only |
| A11 | yes | this round is pushed with `code/checkpoint_push_p309.py` |
| A12 | recorded | the verifier author's step-3 tests ran only in a scratch clone, against addendum 2 step 3a; disclosed by the author, recorded in the overnight report |
| A13 | yes | the /proc-reading functions are registered with the permit `proc_read` (pinned): `proc_access`, `_own_tree`, `_snapshot`, `processes`, `provenance`, `mem_available_gb`, `_children_map`, `audit`, plus `unit_properties`, `qhost_monitor` and `kill_own_descendants` |
| A14 | n/a | noted: the new governance texts were written to pass `code/p309_placeholder_check.py` without new allowlist entries |
| A15 | yes | `stop_qhost_monitor` takes a final provenance sample and requires continuity |
| A16 | yes | the launcher refuses a root unit user, one that owns a foreign root, or one listed as a cell-308 uid. `isolation` refuses before any git call if a P309 root overlaps a foreign root. A failing `systemctl` is a blocker (`systemctl_unavailable`) |

## Other changes in this round

* **Two bugs found while building the controls:**
  * `redact_argv` crashed when the interpreter is unset. It now passes `None` through, and the launch is blocked by
    the preflight as before.
  * A local variable in `kill_own_descendants` whose name is one of the unresolved-marker words tripped
    `code/p309_placeholder_check.py`. It was renamed `stack`.
* **Re-pins:** `governance/R2_REPIN_LIST_SUPPLEMENT_1.json` lists every pinned-list row changed or added, against the
  reviewed commit `447e0713`. The exactly-once sites, the backstop pins, the 13 T13 function pins and the production
  tokens are unchanged.

## What stays open (not the coordinator's to close here)

* **Owner decisions:** OD-R2-0 … OD-R2-6, with the packet as corrected under C1.
* **AWS worker steps:**
  * the C5 worker-tier evidence;
  * P8(e) at the worker freeze;
  * steps 8a–8d. HOST_SUITABILITY = PENDING.
* **A focused follow-up review** of this round (the review's own requirement after C2–C11 and C14).
