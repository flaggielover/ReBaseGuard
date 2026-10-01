# Focused follow-up review of the r2 delta repairs (repair round 1) of P309-r2 at bbfc24f0
R2_DELTA_FOLLOWUP_1_ACCEPTED

**Reviewer.** A fresh independent reviewer. I wrote none of the r2 code or its repairs, none of the verifier author's
changes, neither the r2 plan nor its addenda, and no earlier r2 review (including `REVIEW_R2_DELTA.md`). I am not the
coordinator.

**Brief.** `governance/BRIEF_R2_DELTA_FOLLOWUP_1.md`, committed in `0484b2b3` before issue. Sections 1–12 below map to
its items 1–12. `R2_DELTA_RESPONSE_1.md` was used as a guide only; every statement below rests on git, the committed
evidence, or a run in my own scratch clone.

**State reviewed.**
* Branch `claude/p5y-k5-cell309-p309-r2`, HEAD `bbfc24f0ec4dde4d676a50f5caac6af63c466a49`; working tree clean before
  this file was written.
* Range `47d2819a..bbfc24f0`: 4 commits, linear, no merge (`4e6a6901`, `38089a64`, `0484b2b3`, `bbfc24f0`).
* The drilled commit is `38089a64`. Between it and HEAD only governance/, evidence/ and ledger/ changed
  (`git diff --stat 38089a64 HEAD`). code, config, fc2, tests and verify are therefore the drilled bytes.

**NEW Γ309 TARGET EVALUATIONS = 0.** This review ran no `execute`, `seal-only` or `validate-grant`, no QC item and no
drill. It read no target input and opened no decoy output. It created no ref in either production namespace, anywhere.

## 0. Verdict in brief

**Accepted, with conditions.** The repair round meets most of C1–C15 and A1–A16 in the bytes, and I reproduced the
evidence:
* QC12 T1–T14 PASS; scanner PASS (36 files, 0 findings, planted controls fire every kind including the two signal
  kinds); pins all current.
* Host decision tests 68/68; host controls 26/26, including P02 run as root with `setpriv`; static controls 16/16.
* T13's 23 constant pins: 22 equal r1's F, and `NS_REL` differs by the relocation only.
* All 48 rows of `R2_REPIN_LIST_SUPPLEMENT_1.json` reproduce.
* P8 (a)–(d) reproduce: 72 outside pins plus the candidate manifest are identical; 12 / 5 / 22 / 9 file classes; 35
  r1-token lines; 44 frozen-parameter differences, exactly the classified set. My regenerated
  `freeze/P309_FREEZE.json` is byte-identical to F′'s.
* The drill attempt 6 evidence is internally consistent (110 rows, completeness, 0 band hits, F2 unchanged).
* Nothing scientific changed.

**But I found four defects that need conditions:**
* **FU1. The owner packet now overstates and understates.** It says "the runner checks them" of the unit limits. The
  runner checks 6 properties, and MemoryMax, OOMScoreAdjust, CPUWeight, IOWeight, SendSIGKILL, TimeoutStopSec and
  InaccessiblePaths are not among them. It also presents OD-R2-5 (i) as a cell-308 risk, although the new
  `unattributable` class makes **any** other non-root user's busy process end the single attempt.
* **FU2. `kill_own_descendants` misses children forked during the stop.** My TEST control left 1–5 SIGTERM-ignoring
  survivors in 6 of 8 trials. The unit's `KillSignal=SIGKILL` limits the damage in both Q-HOST topologies. No committed
  control exercises the runner's abort end to end, and the worker-tier drill as written cannot show C5.
* **FU3. The C13 tree-binding text contradicts itself.** Appending to §E modifies a governance file, which rule 2
  forbids.
* **FU4. The AWS instructions lack the operating procedure** that the unattributable rule needs on a shared host.

## 1. Conditions C1–C15 and advisories A1–A16 (brief item 1)

### 1.1 C1–C15

| cond. | status | evidence |
|---|---|---|
| C1 (a) OD-R2-6 | met | Packet lines 268–287. They state the old field's behaviour at `447e0713` and the current behaviour (no host unless `OWNER_OD_R2_6_ANSWER.json` exists). The host re-run is now gated; `execute` and `seal-only` are not gated. Line 275 asks whether the frozen field may name a host before OD-R2-6 is answered |
| C1 (b) OD-R2-5 | met, with an omission | Table at lines 220–232 (0.05 against 0.5 of a core, patterns, aggregate 1.0, one-sample grace). Visibility at lines 234–242 (`foreign_uids`, command line, unattributable). Termination at lines 244–250. Omission: FU1 (b) |
| C1 (c) OD-R2-4 | met, with an inaccuracy | Unit limits at lines 180–185. Polkit only at lines 175–176. World-readable checkout at lines 199–203. Line 188 "the runner checks them" is wrong for most of the listed limits: FU1 (a) |
| C1 (d) OD-R2-0 | met | (A) lines 28–35: message 4 in its own file. (D) lines 41–49: the qualification host is under OD-R2-3/4, no target-execution host is named, and OD-R2-6 is separate |
| C1: decides nothing | met | Lines 3–4, 252 and 296. OD-R2-1 (b) is marked provisional, and option (i) of OD-R2-5 is marked as what the code implements. I found no choice taken outright (§10) |
| C2 | met | `p309_host.py` 350–368 (`foreign_uids`, then pattern or root, then `unattributable` for another non-root uid with an unreadable cwd), 422 (`foreign_uids_configured`), 426–427, 628–631. My P02 run as root: the TEST process under uid 64011 is seen by the gate under uid 64012 as `unattributable`, cpu 0.99; both the gate and the monitor block; with uid 64011 configured it is `foreign`. Consequence for false positives: FU1 (b), FU4 |
| C3 | met | `continuity` 281–285 and 292 are symmetric, and the fallback still needs the same boot id, machine-id and hostname. `qhost_preflight` refuses at 415–417, before the attempt. Tests C09–C11 pass |
| C4 | met | `monitor_liveness` 636–645; `stop_qhost_monitor` 474–495 (alive at the stop, samples present and ordered, no gap over 60 + 30 s). Tests V01–V06 pass. Margin: V5 |
| C5 | partly met | Met: unit `KillSignal=SIGKILL`, `SendSIGKILL=yes`, `TimeoutStopSec=10s` (`p309_launch.py` 121); the abort calls `kill_own_descendants` first (`p309_qualify.py` 430–449); the drill stops on rc 3 or `QHOST_FAIL.json` (`p309_topology_drill.py` 265–266); K01 passes. Not met: the forking-tree defect, and no end-to-end abort control: FU2. The worker-tier evidence is deferred to step 8d by the plan |
| C6 | met | T14 (`p309_static_check.py` 669–700) on `main` and `host_rerun`. Each committed mutant T14a–T14e fails its named sub-check (§4). Gap: refusals by `raise` or `sys.exit` are not seen (V1) |
| C7 | met | Launcher mode `host-rerun` (`p309_launch.py` 51–54). In `host_rerun` (`p309_qualify.py` 539–582), every refusal returns before `os.mkdir` (561) and the HOST RERUN START line (562); the monitor runs, and Q-HOST is part of `pass`. The execute rule is stated in amendments §C and in `make_freeze_params.py` 387–392 |
| C8 | met (P8(e) deferred by plan) | `make_freeze_params.py` 204–215 (named only from the owner's answer file, otherwise `named: false`), 365–369 (Q-HOST and the launcher), 387–392. P8(d) recomputed: §9 |
| C9 | met, two gaps | Redacted record (`p309_launch.py` 155–172; `p309_host.py` 135–140), argv redaction (104–111), file and configuration binding (`p309_qualify.py` 403–408), monitor configuration on standard input (466–471; `p309_host.py` 750–754), start evidence in the attempt (452–471). My N04 record holds the TEST root and the default pattern only as sha256, both in `host_config` and in `argv`. Gaps: the redaction of a quoted path (V2); "are the launcher's" is overstated (FU1 (a)). Worker tier deferred to step 8d |
| C10 | met | `tests/test_p309_static_controls.py`: 16/16 in my clone. Every mutant fails for its named reason (§4) |
| C11 | met | `tests/test_p309_host_controls.py`: 26/26 in my clone (P01, P02, Q01–Q07, N01–N04, S01, K01, B01–B03). Refusal branches inside a unit are untested (V3); the end-to-end abort is untested (FU2) |
| C12 | met | `P309_R2_AMENDMENTS.md` §A (r2 names, provisional) and §B (FC2_SPEC_R2 §6 amended by addition; both namespaces forbidden). The inherited §6 wording is the same text with r1 only |
| C13 | not met as written | §D rules 1, 3 and 4 are mechanical and correct. Rule 2 (line 94: no M in governance/ between D and F) contradicts §E (line 112: entries are appended to this same governance file at the freeze step): FU3 |
| C14 | met | `p309_driver.py` 275–316 and `make_freeze_manifest.py` 102–123 compute the same `runtime_identity`; `check_bindings` compares `RUNTIME_KEYS` and refuses an empty interpreter hash. It is called before the marker (driver 1474; `validate_grant` 695). B01–B03 pass. The T13 closure is unchanged (§7) |
| C15 | met | `R2_BOOTSTRAP.md` 8a uses `foreign_patterns` and `foreign_heavy_patterns`. In my clone, `load_config` accepts those keys, and `load_launch_config` accepts the AWS §3.1 example |

### 1.2 A1–A16

| adv. | status | evidence |
|---|---|---|
| A1 | met | The config reason for the drill's `controls` says `reset --mixed` |
| A2 | met | `p309_topology_drill.py` 312; attempt 6 `R2_M01a.caught: true` |
| A3 | met | Drill 449–454; attempt 6: `run_start_rows: 1`, `missing_scripts: []` |
| A4 | met | Drill 401–404 (`status --porcelain --untracked-files=all -- NS_REL`; a git failure also refuses) |
| A5 | met | The self-audit IMMUTABLE list adds 6 files; all exist; `REVIEW_R2_DELTA.md` sha256 `c04fcf9c…` equals its record |
| A6 | met | `p309_launch.py` 118 |
| A7 | met | Scanner 408–411, 890–904, 936–958; planted control lines added; 5 `signal` registrations. My grep of code/, tests/ and verify/ finds no other sender (§5) |
| A8 | met | `p309_host.py` 630–631; M09/M10 |
| A9 | met | `foreign_stat` 464. It needs both o+r and o+x, which is the right meaning for a directory |
| A10 | met | Reproduced by me (§4) |
| A11 | met | `ledger/CHECKPOINT_PUSHES.jsonl` has one row for each of `4e6a6901` and `0484b2b3`, single refspec |
| A12 | met as a record | `R2_DELTA_RESPONSE_1.md` line 62 |
| A13 | met for the promised functions | 11 functions registered with `proc_read` and pinned. The permit is not enforced by the scanner, and the list is incomplete (V6) |
| A14 | met | `code/p309_placeholder_check.py` is unchanged in the range; `run()` in my clone: PASS, 0 unallowed |
| A15 | met | `p309_qualify.py` 490–491 |
| A16 | met | `p309_launch.py` 86–101 (root, cell-308 uid, owner of a foreign root) and 168–169 (`systemctl_unavailable`); `p309_host.py` 470–473 (overlap refused before any git call) |

## 2. The new host semantics (brief item 2)

**`classify`.**
* An empty command line returns `None`, so kernel threads and zombies are ignored (K05). This test comes before the
  `foreign_uids` test, but no live user process of cell 308 has an empty command line, so that order is harmless.
* `/proc/<pid>` of a non-dumpable process is owned by root. Such a process is never `unattributable`. That is
  acceptable: cell-308 jobs are ordinary processes.

**Fail-open.** Closed for C2's case. Two residual paths remain:
* a cell-308 process whose uid is not listed and whose command line contains `p309` is tagged `p309` and ignored. A
  correct `foreign_uids` removes this, and the gate requires it to be non-empty;
* short-lived processes that start between samples are never judged (the disclosed one-sample grace).

**False positives that consume the single attempt.** The new `unattributable` class covers every non-root uid other
than the caller's whose cwd the P309 user cannot read. That includes:
* service accounts (for example `messagebus`, `syslog`, `systemd-resolve`, `_chrony`, `polkitd`, `man`, `cwagent`);
* any other login session, including the P309 session's own access user if that user is not the P309 user.

In the monitor, any such process above 0.5 of a core over the 20 s window, or the sum of all such processes above 1.0
core, is a Q-HOST FAIL. That ends r2's attempt (OD-R2-5 (i)). The start gate (0.05, and any process new during the
sample) screens this only at the launch. If uid 0 is listed, the same applies to every root job; the documents say so.
FU1 (b) and FU4.

**`gate_checks`.** `foreign_uids_configured` (422) fails closed when `foreign_uids` is empty or holds the caller's uid.
It does not refuse uid 0, which is documented as allowed.

**`monitor_verdict`.** The aggregate rule (630–631) marks every foreign or unattributable pid with a positive CPU
fraction when the sum exceeds `monitor_aggregate_cpu_fraction`. It is correct and fails closed.

**`monitor_liveness`.** Correct, and as pure as stated. Margin, from reading `qhost_monitor`: a sample takes about
20 s; in the worst case it takes 20 s plus 20 s (the `timedatectl` timeout) plus about 6 s (IMDS timeouts). The
largest gap between consecutive `t` values is then about 86–87 s, against a limit of 90 s. The rows use wall-clock
time (V5).

**Symmetric `continuity`.** Not fail-open: when one side lacks the instance id, `same_instance` still requires the same
boot id, machine-id and hostname, and `instance_unverified` is reported.

**`kill_own_descendants` (686–712).**
* It walks only the `/proc` ppid tree below `os.getpid()`. In 8 of 8 trials of my control, a TEST sleeper outside the
  caller's tree stayed untouched (state `S`). So it signals only the caller's descendants, apart from the theoretical
  case of pid reuse (V7).
* **Defect.** A later round pushes only new pids onto its stack (695–698), so it never descends below an
  already-stopped pid. A child forked by such a pid between round 1's `/proc` scan and that pid's SIGSTOP is never
  found.
* My reviewer control (`ctl/forkrace2.py`; driver → TEST forker that forks every ~2 ms; the committed function called
  from the driver) left survivors as follows:

  | delay (s) | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.8 | 1.0 | 1.2 |
  |---|---|---|---|---|---|---|---|---|
  | survivors | 1 | 2 | 2 | 2 | 3 | 5 | 0 | 0 |

  At 1.0 and 1.2 s the forker had already reached its cap of 400 children and was no longer forking. The survivors were
  alive, in state `S`, and reparented to pid 1.
* The docstring's "repeated until no new descendant appears, so none can fork away" is therefore false.
* In the official run and the host re-run, the runner exits at once and the unit's SIGKILL stops the survivors. In the
  worker-tier drill, they run until the drill has written its report and deleted its root. FU2.

**`unit_properties` and its redaction (721–745).** `InaccessiblePaths` is hashed element by element, and the
`P309_FOREIGN_ROOTS=` entry of `Environment` is hashed. If `systemctl show` quotes an environment entry (a path with
whitespace), the entry no longer starts with `P309_FOREIGN_ROOTS=` and is recorded in clear. My simulation of lines
739–744 on TEST strings shows this (V2).

**`redacted_config`, `config_sha256`, `load_launch_config`.** These are consistent between the launcher and the
runner:
* both call `load_launch_config` with `require_empty = mode != "drill"`;
* the runner substitutes the record's `p309_repo` before hashing (`p309_qualify.py` 407), which makes the drill
  clone's binding work;
* redaction covers `foreign_roots`, `foreign_patterns` and `foreign_heavy_patterns`.

**The `isolation` order.** The overlap refusal comes before any git call (470–473), as A16 asked.

## 3. The launcher and the runner (brief item 3)

**Launcher.**
* Modes `drill`, `official` and `host-rerun`, each with a fixed unit name (L05).
* Kill properties at line 121.
* A16 refusals at step 0, before the record exists.
* Redacted record and argv. `P309_HOST_CONFIG` is passed (line 120) and bound by `host_config_file_sha256`.
* Blocked launches still write the record (`open(..., "x")`) and start nothing.
* Nothing checks that the launcher's own uid is the unit user's (V4).

**Runner.**
* `qhost_preflight(modes)` refuses in this order: scratch root; record present; record and scratch under the launch
  root; blockers or mode; mode fits the repository; inside the unit; configuration file sha256; configuration hash;
  six unit properties (`UNIT_REQUIRED`, 380–381); instance-id rule; continuity.
* The start evidence (`LAUNCH_RECORD.json`, `UNIT_PROPERTIES.json`, `QHOST_BASELINE.json` with both sha256 values) is
  written right after the start line.
* `_qhost_abort` kills its own tree before writing.
* `stop_qhost_monitor` ignores SIGTERM first, then judges liveness, every row and a final continuity sample.
* `host_rerun` follows the same pattern.

**Every refusal before the attempt directory and the start line?** Yes, for every refusal written as a `return`: by
reading `main()` (596–619), `host_rerun()` (546–558) and T14. `qhost_preflight` raises `HostError`, which both callers
turn into `return 2` before the mkdir. T14 does not see a refusal written as `raise` or `sys.exit` after the mkdir; my
two mutants of that kind pass T14 (V1).

**Exercised nowhere so far.** The configuration, unit-property and instance-id refusal branches (they lie behind the
in-unit check; V3), the real `systemctl show`, `start_qhost_monitor`, `stop_qhost_monitor` and `_qhost_abort`. The
worker tier will exercise the passing path only (FU2).

## 4. QC12 (brief item 4)

**T13.** I took r1's `code/p309_driver.py` and `code/p309_guard.py` from `4c754a73` and ran the committed
`production_read_closure` and `production_read_constants` on r1's F and on HEAD:
* the 13 function pins are equal at r1's F, at HEAD and in the config;
* there are 23 constants in each, with the same members;
* 22 equal r1's F, and `equals_r1_F` is accurate in every entry;
* r1's `NS_REL = CP + "p5y_k5_cell309_p309_r1"` with the map applied hashes to the pinned `3567c9fd…`.

**T14** is as described in its docstring. Each committed mutant fails exactly its named check:

| mutant | fails |
|---|---|
| T11a | `qc11_new_sandbox_uses_sandbox_base` (and the real-head read) |
| T11b | `guard_new_sandbox_uses_sandbox_base` |
| T11c | `verifier_sandbox_uses_sandbox_base_commit` |
| T12a | `guard_forbidden_namespaces_is_both` |
| T12b | `qc13_checks_both` |
| T12c | `production_tokens_hold_both` (r1 token removed) |
| T13a | `same_hashes` |
| T13b | `same_constant_hashes` |
| T13c | `same_constant_members` |
| T14a | `preflight_before_mkdir`, `start_logged_right_after_mkdir`, `refusal_returns_before_mkdir` |
| T14b | `refusal_returns_before_mkdir` |
| T14c | `monitor_starts_before_work` |
| T14d, T14e | `host_rerun.one_preflight_with_modes` |

My own mutant that drops `stop_qhost_monitor` from `host_rerun` is caught (`monitor_stopped_after_work`). The `raise`
and `sys.exit` mutants are not (V1).

## 5. The scanner's signal rule (A7) (brief item 5)

**Coverage.**
* `os.kill`, `os.killpg`, `posix.*` and `signal.pthread_kill` / `pidfd_send_signal`, through the resolved module alias.
* Any `.send_signal()`, `.terminate()` or `.kill()` method call.
* Import or value binding of these names (SIGNAL_ALIAS).
* `os.kill(os.getpid(), …)` is exempt only when written literally.
* `getattr`-style access and other modules (`ctypes`) fall under the existing INTROSPECTION and IMPORT rules.
* The planted control has `os.kill(1, 15)` and `KILL = os.killpg`, and the scan reports that both fire.

**Registrations with the permit `signal`.** `qhost_monitor` (one SIGTERM to its parent), `kill_own_descendants`,
`stop_qhost_monitor`, the host controls' `stop`, and `verify_cert` (`pool.terminate()`; the verifier is unchanged).
Each has an accurate reason.

**Other new registrations.**
* `process`: `unit_properties`, `case_p02`, `launcher`, `case_q`, `case_k01`.
* `proc_read`: 11 functions.

**Unregistered senders.** My grep of every signal-sending construct finds none outside these. The only implicit
senders are the standard library's own kill of its child on a `subprocess.run` timeout, which is always the caller's
own child.

## 6. The committed controls (brief item 6)

I re-ran them in my scratch clone, as root, with `setpriv` available:

| control | result |
|---|---|
| `tests/test_p309_host.py` | 68/68 |
| `tests/test_p309_host_controls.py` | 26/26 |

**What the cases show.**
* **P02** shows what the response claims; the rows are quoted in §1.1, C2.
* **S01**: rc 1, signals `[15]` exactly once, one failed row with `same_boot` false.
* **K01**: the three-deep SIGTERM-ignoring tree is killed and the caller survives. K01 has no forking descendant and
  no non-descendant check. My control adds both (§2).
* **N04**: blockers `preflight`, `gate`, `isolation` and `systemctl_unavailable`. The record contains neither the TEST
  root nor the default pattern in clear; both appear as sha256.

## 7. C14 (brief item 7)

**Driver diff from r1's F after relocation** (my `diff` of r1's driver with the map applied against HEAD's) has three
parts:
* `check_bindings` lines 291–293;
* the new `RUNTIME_KEYS` and `runtime_identity` (297–316);
* the seal label.

**Since `447e0713`**, only `p309_driver.py` changed among driver, guard and verify (27 lines).

**Unchanged:** the T13 closure (13 equal pins); `exactly_once_sites` and `backstop_pins` in the config equal r1's F;
T4 and T8 pass.

**Consequence.** It is disclosed in packet lines 284–287 and in `R2_HOST_REQUIREMENTS.md` line 38: the execution host
needs a byte-identical interpreter and the same glibc. `make_freeze_manifest.py --check` now also compares these at
the start of qualification. That refusal comes before the attempt.

## 8. C8 (brief item 8)

`qualification_rule` names Q-HOST and `--mode official`.

`proposed_execution_host()` behaves as follows:
* It never defaults to the freeze host.
* It names a host only from `governance/OWNER_OD_R2_6_ANSWER.json`, with its sha256. The file is absent, so my
  regeneration gives `named: false`.
* A malformed answer file fails loudly (`KeyError`).

The execution-host derivation now keys the host re-run to "the host of the qualification attempt". r1's text keyed it
to the proposed host, which r1 set to the freeze and qualification host. It is equivalent in r1's situation, and it is
classified in P8(d).

## 9. The re-drill, P8 and the re-pin supplement (brief item 9)

**Drill attempt 6** (`evidence/drill/20261001T202159Z`, clone base `38089a64`):
* The report's sha256 is `3b596f88…`. It equals the official ledger row's.
* **F4.** 110 rows; the exported file equals the report's rows line for line; the report's `sha256` is
  sha256("\n".join(rows)), and it reproduces. The exposure ledger is empty.
* **Counters and band.** Counters 0; no `cells_touched`; 60 drift entries with 0 band hits (I used the drill's own
  `meets_band`; the band was not printed).
* **Completeness.** Exactly one RUN START row; all nine required scripts present.
* **Controls.** All caught, including M01a by the uncaught refusal line.
* **Witnesses.** All true.
* **F2.** `p309_before` equals `p309_after` (HEAD `38089a64`, refs sha `38482e5d…`, status sha256 of the empty string).
* **Timing.** Attempt 6 ended at 21:32:51Z, before the evidence commit `0484b2b3` at 21:33:46Z.
* **Kept clone** (read-only git): F′ `ffee89ab` (parent `38089a64`), FR′ `19cdcbf7` (touches only `FREEZE_RECORD.json`),
  tip `54d91ea3` (touches only `CHECKPOINT_PUSHES.jsonl`). No origin, no pushDefault, no production-namespace ref.
* **The coordinator's validation:** 43/43 true.

**P8, recomputed:**
* **(a)** 72 outside pins plus the candidate manifest make the 73.
  * The path sets are equal.
  * `git diff --quiet 4c754a73 HEAD -- <path>` succeeds for all 72.
  * The pin records compare equal in memory. No hash was printed (disclosed below).
  * The runtime gains `glibc` and `interpreter_sha256` (F′: CPython 3.11.15, glibc 2.39).
* **(b)** Over code, config, fc2, tests, verify and start_state: 12 unchanged, 5 relocation-only, 22 beyond the map,
  9 new, 0 removed. These are the identical lists.
* **(c)** 35 lines, the same (file, line) set. The new one is the `NS_REL` note at config line 1803.
* **(d)** My `make_freeze_params.py` output at HEAD is byte-identical to F′'s `P309_FREEZE.json`. Its key-path diff
  against r1's F (values not printed) gives 44 differences, equal to the classified set; 0 unexpected. Every new
  difference (5: `qualification_rule`, `proposed_execution_host.{description,host_id_sha256,named}`,
  `post_grant_derivations.execution_host`) is correctly classified as C7/C8.

**`R2_REPIN_LIST_SUPPLEMENT_1.json`.** All 48 rows reproduce: 23 constant pins, 22 reviewed functions, 2 ref-mutation
functions and 1 t7 exemption. For each row I checked the 447e0713 config value and its currency there, the HEAD AST
sha256, the HEAD config value and the r1 config value. No config entry changed without a row. No permit or reason
changed on an existing reviewed entry. No module-level exemption changed.

## 10. No scientific change (brief item 10)

These top-level keys of the frozen parameters are equal to r1's F: `route`, `cell`, `detector`, `m`,
`closure_criterion`, `scope`, `outcome_table`, `stage1a`, `stage1b`, `stage2`, `u2`, `efficacy` and
`independence_statement`.

`post_grant_derivations` differs only in `execution_host`. `cell_interval`, `drift_hull_Ew` and `not_after_utc` are
unchanged.

**Also unchanged:**
* the driver except for C14 (§7);
* guard and verify;
* no path outside FNS2 in any commit of the range; r1's tree is `ecd1c359` at every commit;
* `WORKERS` and the launcher's fixed `--workers 4`;
* the exactly-once sites and the A38 backstop.

**Implicit owner decisions.** I found none taken outright:
* the default `named: false` is the conservative reading and is put to the owner (packet line 275);
* amendments §C defers shared-host execute to a reviewed amendment and is presented as one OD-R2-6 option;
* the thresholds (0.05 / 0.5 / 1.0, tolerance 30 s) are configuration values shown to the owner.

The breadth of `unattributable` does widen who can end the attempt, beyond message 3's "a cell-308 heavy job". It must
be stated (FU1 (b)).

## 11. The new governance texts (brief item 11)

**`P309_R2_AMENDMENTS.md`.**
* §A and §B are accurate.
* §C is mechanical (a sequence of amendment, code, delta review, re-drill) and names no host.
* §D rules 1, 3 and 4 are git commands with the right paths.
* Rule 2 cannot hold together with §E as written: FU3.

**AWS instructions and bootstrap.**
* C15 is met.
* The §8 launch-record table matches `p309_launch.py` field for field.
* The §3.1 example parses.
* Lines 186 and 268 say "the unit's effective properties are the launcher's", which overstates the six-property check:
  FU1 (a).
* `R2_HOST_REQUIREMENTS.md` line 40 attributes SendSIGKILL and TimeoutStopSec to `qhost_preflight`, which does not
  check them: FU1 (a).

## 12. Disclosures (brief item 12)

* **Development runs in a scratch clone.** Accepted. They are not evidence, and the drill re-ran every suite and
  ledgered it.
* **The two bugs.**
  * `redact_argv` now passes a non-string through (`p309_launch.py` 109).
  * The renamed local is `stack` (`p309_host.py` 693).
  * Neither added an allowlist entry.
* **Further departures I found.**
  * **(a) Two orphaned TEST processes.** pids 19667 and 19669, argv[0] `TESTONLY_unmatched_job` and
    `TESTONLY_fake_cell308_job`, cwd `…/scratchpad/r2_delta_review/ctl/foreign_TEST_root`, ppid 1, started 18:32:11Z,
    about 100 % CPU each. They are still running in this container.
    * The delta review's ledger row 14 says "processes killed". The coordinator did not notice them.
    * They held 2 of the 4 cores throughout drill attempt 6 (timings only). They make any gate run in this container
      block: the second matches `cell[_-]?308`, and the first's cwd contains "ReBaseGuard".
    * Under my brief I did not signal them.
  * **(b) `R2_HOST_REQUIREMENTS.md` changed after the drilled commit.** This is a governance text only. It is not in
    the parameter generator's DOCS, since F′ regenerates identically, and it is allowed before D.
  * **(c) The response overstates C9.** `R2_DELTA_RESPONSE_1.md` line 39 says "The runner refuses unless the unit's
    effective properties are the launcher's". The check covers six properties (FU1 (a)).

## Conditions

**FU1 — blocking-before-owner-decisions.** Correct the owner packet, and the operator texts with it. The packet must
still decide nothing.
* **(a) The unit-property check.** Replace the packet's line 188, "the runner checks them against `systemctl show`",
  with the facts:
  * the runner refuses unless Restart, KillMode, KillSignal, NoNewPrivileges, PrivateTmp and ProtectSystem have the
    launcher's values;
  * MemoryMax, OOMScoreAdjust, CPUWeight, IOWeight, SendSIGKILL, TimeoutStopSec and InaccessiblePaths are set by the
    launcher's argv and recorded in `UNIT_PROPERTIES.json`, but not checked.

  Alternatively, extend `UNIT_REQUIRED` to all of them. That is a code change: then also before step 8d, with a
  re-drill. Apply the same correction to `R2_HOST_REQUIREMENTS.md` line 40 and `R2_AWS_SESSION_INSTRUCTIONS.md`
  lines 186 and 268.
* **(b) OD-R2-5.** State that `unattributable` covers every other non-root uid whose cwd the P309 user cannot read:
  service accounts, other login sessions, and the P309 session's own access user if that is not the P309 user. So under
  option (i), any such process above 0.5 of a core, or all of them above 1.0 core together, ends the single attempt.
  The windows must therefore be agreed for the whole host, not only with the cell-308 operator (lines 213–215).
  Replace "exactly when the right-hand column fires" (line 231): Q-HOST also fails on a monitor death or a gap over
  90 s, on a continuity break, and on a failed final sample.

**FU2 — before-freeze; before step 8d.** Repair and exercise the abort.
* **(a)** Make `kill_own_descendants` traverse through already-seen pids in every round, so that a child forked by a
  stopped descendant is found, and stop only when a full traversal finds nothing new. Correct its docstring. Extend
  K01 with a descendant that keeps forking during the call, and with a TEST process outside the caller's tree that must
  stay untouched (my `forkrace2.py` shows the shape).
* **(b)** Commit a control that runs the runner's abort end to end, in the cloud tier and in the worker-tier drill:
  * a real monitor with a failing baseline;
  * SIGTERM to a child that has installed `_qhost_abort`, with `ATT` pointed at a TEST directory and the `host_rerun`
    label so that nothing is written in `qualification/`;
  * a SIGTERM-ignoring, forking TEST tree killed;
  * `QHOST_FAIL.json` and the failed result written;
  * exit status 3.

  Without it, the worker-tier drill, which passes Q-HOST, cannot show C5.
* **(c)** Re-drill on the changed bytes, and have the next review of the r2 delta cover them.

**FU3 — before-freeze.** Make `P309_R2_AMENDMENTS.md` §D rule 2 consistent with §E. One way is to keep §E's list in a
new governance file added after D, which rule 2 allows as an addition. The other is to exempt appends to §E explicitly,
with a mechanical check that the diff of this file between D and F only appends lines under §E. Apply the same rule to
any other governance file that must change between D and F.

**FU4 — before-freeze; before step 8d.** Add to `R2_AWS_SESSION_INSTRUCTIONS.md` the procedure the unattributable rule
needs:
* run every process the P309 session starts during a window as the P309 user, whose own processes are never
  classified;
* after 8c, run `p309_host.py gate` read-only as the P309 user and preserve it, so that the uids of `unattributable`
  and `foreign` rows are known;
* before an official launch, read those rows in the launch record, and agree the window with every non-root workload
  they show.

**Advisory:**
* **V1.** T14 counts only `return` as a refusal. Also reject `raise`, `sys.exit` and `os._exit` statements between the
  attempt mkdir and the final return, and add a mutant for each.
* **V2.** Refuse foreign roots containing whitespace or quoting characters in the launcher, or redact `Environment` by
  substring rather than by prefix.
* **V3.** Exercise the in-unit refusal branches of `qhost_preflight` (configuration file, configuration hash, unit
  properties, the instance-id rule). Use an injectable test seam, or worker-tier drill controls.
* **V4.** The launcher should refuse unless its own uid is the unit user's, since the gate and isolation are evaluated
  as the launcher's user.
* **V5.** Take each monitor row's `t` at the start of the sample, or use `CLOCK_MONOTONIC`, or raise the tolerance. The
  worst-case gap is about 86–87 s against 90 s.
* **V6.** `proc_read` is informational, because the scanner does not enforce it. Either enforce it, or complete the
  list (`exclusion_gate`, `durability_preflight`, `qhost_preflight`, the drill's `/proc` reads) and say it is a register.
* **V7.** In `kill_own_descendants`, check each pid's start time (or use pidfds) before SIGKILL, against pid reuse.
* **V8.** The packet's "about 140 s" for detection is conservative. By the code's timing it is about 80 s plus
  sampling overhead.
* **V9.** When preserved, add `BRIEF_R2_DELTA_FOLLOWUP_1.md` and this review, with its sha256 record and ledger, to
  self-audit A3's IMMUTABLE list.
* **V10.** Have the session that owns pids 19667 and 19669 kill them before the next run in this container, and record
  the departure with the next response (the delta review itself stays verbatim).

## Disclosure (reads, runs, writes)

**Execution ledger.** `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r2_followup_review/LEDGER.jsonl`
holds one JSON row per command or command group, each with `target_evaluations: 0`. The early read-only groups were
logged in batches shortly after they ran.

**Reads.**
* The brief; `REVIEW_R2_DELTA.md`; `R2_DELTA_RESPONSE_1.md`; the owner packet; `P309_R2_AMENDMENTS.md`; the AWS
  instructions, the bootstrap and the host requirements; FC2_SPEC_R2 §6.
* The full diff of every code, config and test file in the range, and the changed files in full or in the cited
  sections.
* The drill attempt 6 report and ledgers, the validation JSON, the P8 round 2 and supplement JSONs, the official
  ledgers, and the delta review's execution ledger (for its control rows).
* r1 at `4c754a73` through `git show`: driver, guard, config, `P309_FREEZE.json` (key paths compared, values not
  printed) and the manifest (paths printed; pin records compared in memory, no hash printed).
* The kept drill clone through read-only git only: `log`, `for-each-ref`, `remote -v`, `config --get`, `show --stat`,
  and `show` of F′'s two freeze files.
* `/proc` of pids 19667 and 19669: the first three argv elements, cwd, status lines and cgroup.

**Runs.**
* In the real repository, read-only git only: `rev-parse`, `log`, `diff`, `diff-tree`, `show`, `ls-tree`, `cat-file`,
  `for-each-ref`, `status`, `rev-list`. Also `ps`.
* One scratch clone (`--no-local --no-tags --single-branch`, origin removed, only `refs/heads/<r2 branch>`), with
  `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR` in my scratchpad and `PYTHONDONTWRITEBYTECODE=1`. In it I ran:
  * `p309_static_check.py`, `p309_scan.py` and `p309_scan_pins.py --list`;
  * `tests/test_p309_host.py`, `tests/test_p309_host_controls.py` (as root; TEST uids 64011/64012) and
    `tests/test_p309_static_controls.py`;
  * `make_freeze_params.py`, which reads FNS2 docs, r1 reviews and research protocol documents, and no cell-307/308
    file;
  * `p309_placeholder_check.run()`, as a function only;
  * my scratch scripts: `verify_repin.py`, a static-mutant script on a scratch copy, a band count through the drill's
    `meets_band`, a redaction simulation on TEST strings, and `ctl/forkrace.py` and `ctl/forkrace2.py`.
* The fork-race controls started TEST processes only. Their cleanup SIGKILLed processes whose argv carried the run's
  random nonce. In the first run, that match included my own `timeout` wrapper process, which carried the nonce in its
  argv; it was mine, and no other process was signalled. After each run, no process carrying the nonce remained.
* I sent no signal to any process I did not start, including pids 19667 and 19669.
* Not run: the manifest generator, any QC item, any drill, `execute`, `seal-only`, `validate-grant`. No network.

**Writes.**
* This file. It is not added or committed.
* My scratchpad: the ledger, scripts, outputs, the scratch root, and a clone that I then deleted by its literal path.
* The tools I ran wrote ledger rows and evidence only inside that clone or the scratch evidence directory.
* No git write of any kind in `/home/user/ReBaseGuard`. HEAD is `bbfc24f0` and the status was clean before this file.
* Nothing was written to the kept drill clone.

**Firewall.**
* No cell-305–309 value was read.
* No cell-307/308 campaign file was opened or hashed. Outside pins were compared by `git diff --quiet` and by
  in-memory equality of the already-recorded pin records, without printing them.
* No decoy output was opened.
* No ref under `refs/p5y-k5-cell309-p309-r1/` or `-r2/` was created anywhere.
