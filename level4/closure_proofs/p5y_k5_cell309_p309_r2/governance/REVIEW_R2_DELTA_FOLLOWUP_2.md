# Second focused follow-up review of the r2 delta repairs (repair round 2) of P309-r2 at 5273b908
R2_DELTA_FOLLOWUP_2_ACCEPTED

**Reviewer.** A fresh independent reviewer. I wrote none of the r2 code or its repairs, none of the verifier author's
changes, neither the r2 plan nor its addenda, and no earlier r2 review (`REVIEW_R2_DELTA.md`,
`REVIEW_R2_DELTA_FOLLOWUP_1.md`). I am not the coordinator.

**Brief.** `governance/BRIEF_R2_DELTA_FOLLOWUP_2.md`, committed in `c26fac16` before issue. Sections 1–11 below map to
its items 1–11. `R2_DELTA_RESPONSE_2.md` and `REVIEW_R2_DELTA_FOLLOWUP_1.md` were used as guides only; every statement
below rests on git, the committed evidence, the kept drill clones read with read-only git, or a run in my own scratch
clone.

**State reviewed.**
* Branch `claude/p5y-k5-cell309-p309-r2`, HEAD `5273b9080a00282d22b5d06ad705ff0477a6698a`; working tree clean before this
  file was written.
* Range `ec34b2a3..5273b908`: 6 commits, linear, no merge (`8cb59c0f`, `e3242cbb`, `45fff547`, `8725f8b7`, `c26fac16`,
  `5273b908`). Every path is inside FNS2.
* Code commit `8cb59c0f`. The tree ids of `code`, `config`, `fc2`, `tests` and `verify` are identical at `8cb59c0f`,
  `e3242cbb` (attempt 7's clone base), `8725f8b7` (attempt 8's clone base) and HEAD (`code` `3c345ac3…`, `config`
  `23abf619…`, `fc2` `647d2951…`, `tests` `d01e769f…`, `verify` `d6b4ba88…`). r1's tree is `ecd1c359` at HEAD and at
  `ec34b2a3`.

**NEW Γ309 TARGET EVALUATIONS = 0.** This review ran no `execute`, `seal-only` or `validate-grant`, no QC item and no
drill. It read no target input and opened no decoy output. It created no ref under either production namespace,
anywhere.

## 0. Verdict in brief

**Accepted, with conditions.** FU1 (blocking before owner decisions) is met word by word, and the packet still decides
nothing. FU2 and FU3 are met. I reproduced the evidence:
* QC12 T1–T14 PASS; scanner PASS (36 files, 0 findings; planted controls fire every kind); pins all current.
* Host decision tests 68/68; host controls 35/35 (P02 as root with `setpriv`; K01; A01); static controls 19/19; scanner
  allowance tests 19/19.
* My mutants: T14f–T14h each fail exactly `no_raise_or_exit_after_mkdir`. A01 fails (A01b, A01d) when the abort kills
  nothing.
* My fork-race control: the repaired `kill_own_descendants` left 0 survivors in 24 trials against a tree in which
  every process forks. The pre-repair function left 68–226 survivors in each of 5 trials. A TEST process outside the
  tree was never touched.
* All 13 rows of `R2_REPIN_LIST_SUPPLEMENT_2.json` reproduce. P8 (a)–(d) reproduce; my `P309_FREEZE.json` is
  byte-identical to F′'s.
* Drill attempt 8: report sha256 equals its ledger row; 112 rows equal the clone's ledger extension line for line;
  counters 0; 0 band hits; F2 holds (I reconstructed the report's `refs_sha256` from the repository's refs).
* Attempt 7's coordinator-written record matches its kept clone: 104 rows reproduce, sha256 matches.
* Nothing scientific changed.

**Two new defects need conditions:**
* **SF1. The V5 repair made the worst-case stop gap exceed the limit.** Rows are now timed at the start of their
  sample. So the last gap (last written row to the stop) is the interval plus the duration of the sample in progress
  at the stop. On a virtual clock driving the committed `qhost_monitor` and `monitor_liveness`: 80.2 s normally;
  106.2 s, above the 105 s limit, when a sample hits the `timedatectl` timeout (20 s) and the metadata timeouts (6 s).
  Before the repair, the same cases gave 60.0 s and 85.8 s against 90 s. The response's "worst case about 87 s" holds
  only for gaps between rows. A Q-HOST FAIL at the stop ends the single attempt.
* **SF2. The FU4 procedure cannot be run as written.**
  * Step 2's `p309_host.py gate --config ~/p309_host_config.json` refuses on the §3.1 file ("unknown config keys": the
    six launch settings). The 8c `isolation` and `preflight` commands refuse the same way.
  * Step 4 reads a launch record that the official launch writes only as it starts the unit.

## 1. FU1–FU4 and V1–V10 (brief item 1)

### 1.1 Conditions

| cond. | status | evidence |
|---|---|---|
| FU1 (a) | met | Packet 189–195: the runner **refuses** unless `Restart`, `KillMode`, `KillSignal`, `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem` have the launcher's values; `MemoryMax`, `OOMScoreAdjust`, `CPUWeight`, `IOWeight`, `SendSIGKILL`, `TimeoutStopSec`, `InaccessiblePaths` are set by the launcher's command and recorded in `UNIT_PROPERTIES.json`, **not checked**. This matches the bytes: `UNIT_REQUIRED` (`p309_qualify.py` 380–381), the check (409–412), the launcher's properties (`p309_launch.py` 127–133). Same facts: AWS instructions 187–190 and 293–296; host requirements 40; amendments G2 (166–170). No residual "checks them" / "are the launcher's" overstatement remains (grep of the five operator texts) |
| FU1 (b) | met | Packet 255–263: `unattributable` covers every non-root uid other than the P309 user's whose cwd P309 cannot read (service accounts, other login sessions, the session's own access user if not the P309 user); above 0.5 of a core, or all together above 1.0 core, ends the attempt. Packet 220–224: windows agreed for the whole host. Packet 242–246 replace "exactly when the right-hand column fires" with the full list: right-hand column, continuity break, monitor death or a gap over 60 s + 45 s, a failed final sample. This matches `monitor_verdict` (`p309_host.py` 621–633), `stop_qhost_monitor` (`p309_qualify.py` 474–494) and `continuity` (`p309_host.py` 272–292). Same facts: host requirements 101–102, 113; amendments G3 (172–174); AWS §4.1 209–211 |
| FU1: decides nothing | met | Packet 3–4, 278 and 322 unchanged. The new text states consequences of option (i) as implemented and points to a procedure; it takes no option. The diff of the packet over the range adds no choice |
| FU2 (a) | met (advisory W1) | `kill_own_descendants` (`p309_host.py` 692–727): every round re-walks the whole tree from the caller through seen pids (707), SIGSTOPs only new ones, ends when a walk finds nothing new; SIGKILL only if the start time is unchanged (719–721). Docstring corrected (693–698). K01 extended (tests 364–385; forkers still forking at the call, 72 and 89). My control (§2) |
| FU2 (b) | met (advisories W6, W7) | A01 (tests 387–430; ABORT 104–137): the runner's own `_qhost_abort`, attempt at a TEST directory, label `host_rerun`, real monitor with a failing baseline, SIGTERM-ignoring forking TEST tree, `QHOST_FAIL.json` and the failed result, exit 3, outside process untouched, nothing in `qualification/`. §3 |
| FU2 (c) | met | Attempt 8 (`evidence/drill/20261001T224858Z`) on `8725f8b7`, whose code trees equal `8cb59c0f`'s. This review covers it (§9) |
| FU3 | met | Amendments G1 (150–164) is mechanical and consistent with §D: the list moves to a new file added at the freeze step; rule 2's `--diff-filter=MDRTCUX` must print nothing; every other added path is listed with its sha256 and review. The file is append-only: its only two versions are `4e6a6901` and `8cb59c0f`, and the first is a byte prefix of the second (§7) |
| FU4 | partly met | §4.1 (AWS 207–227) has the three required elements. But step 2's command refuses on the §3.1 file, and step 4's order cannot be followed for an official launch: **SF2** (§8) |

### 1.2 Advisories

| adv. | status | evidence |
|---|---|---|
| V1 | met, literal scope (W5) | `p309_static_check.py` 686–687, 697. My mutants (§4) |
| V2 | met for whitespace, quotes and backslash (W3) | `p309_launch.py` 100–101, before the record; N05 passes |
| V3 | not met; deferral not in the bytes (W6) | The response defers it to 8d, but `p309_topology_drill.py` has no worker-tier control that reaches these branches; the drill's `main()` exercises only the passing path |
| V4 | met | `p309_launch.py` 176–177; N04d passes (§5) |
| V5 | not met: regressed in the worst case | **SF1** (§6) |
| V6 | met | `process_policy.proc_read_note` declares the register; `exclusion_gate`, `durability_preflight`, `qhost_preflight`, `_start_time`, `in_unit`, `live_with`, `kill_token` registered and pinned, each with a row in supplement 2 |
| V7 | met for SIGKILL (W1) | `p309_host.py` 719–721. SIGSTOP (713) has no such check |
| V8 | met | Packet 270–272 "about 80–90 s". By the code: a process starting just after a sample's first snapshot has no CPU fraction until the next sample (`p309_host.py` 385), which ends about 60 + 20 s later |
| V9 | met | `p309_self_audit.py` IMMUTABLE adds the four files. Each was committed once (`0484b2b3`; `a065aeaa`). `REVIEW_R2_DELTA_FOLLOWUP_1.md` sha256 `c5f5a24a…` equals its record |
| V10 | met as a record | Response 52–59. Two container restarts since make it impossible to verify the kill itself. No `TESTONLY_` process exists now |

## 2. `kill_own_descendants` (brief item 2)

**Traversal.** Complete against a descendant that forks during the call, up to the asynchrony noted in W1.
* Each round rebuilds the ppid map (`_children_map`, 676–684) and walks from the caller through every descendant,
  seen or not (707). The FU1 defect, never descending below a stopped pid, is gone.
* My control (`ctl/forkrace3.py`): a TEST driver forks a tree in which **every** process keeps forking (3 children
  each, 1 ms apart, depth 5; up to 364 processes), all ignoring SIGTERM. It calls the committed function after 5–150
  ms, while the tree grows.

  | function | trials | trials with survivors | survivors per trial | outside TEST process |
  |---|---|---|---|---|
  | HEAD | 24 | 0 | 0 (45–364 killed) | untouched in all |
  | `bbfc24f0` (pre-repair) | 5 | 5 | 68–226, state `S`, most reparented to pid 1 | untouched in all |

* Committed K01 passed in my run (killed 50, so the forkers were still forking at the call; no token process left;
  outside untouched).

**Start-time check.** It prevents a SIGKILL to a reused pid (719–721). It does not guard the SIGSTOP (713), which
goes out in the same round as the discovery. That window is at most one `/proc` scan; the SIGKILL's is microseconds.
A reuse inside them needs a pid wrap-around (`pid_max` 32768 here). While a descendant's parent is stopped, its zombie
cannot be reaped, so its pid cannot be reused. The residual is theoretical (W1).

**Asynchrony.** "A stopped process cannot fork" is true, but `kill()` returns before the target has stopped. A child
forked by a descendant whose SIGSTOP arrived mid-`fork()` becomes visible only when `copy_process` links it. If the
next round's `listdir("/proc")` runs before that, and nothing else is new, the loop ends without it. I did not observe
this in 24 trials; it is W1.

**Signals outside the caller's tree.** None observed: K01b, A01d and my outside sleeper in 29 trials. The walk starts at
`os.getpid()` and never yields the caller (705). The only new signal sender in the range is `kill_token` in the
tests: it SIGKILLs live processes whose argv holds the run's random 12-hex token as an exact element (tests 342–361).

**Related, outside the function.** `qhost_monitor` checks `os.getppid() != parent` at the top of each loop (659) and
sends SIGTERM to `parent` about 20 s later (671). If the runner has died in between, the pid could in theory name
another process. In the units, `KillMode=control-group` ends the monitor with its runner (W2).

## 3. The end-to-end abort control A01 (brief item 3)

* **Nothing in `qualification/`.** `ATT` is the TEST directory and the label is `host_rerun` (tests 110), so
  `_qhost_abort` writes `QC10_HOST_RERUN.json` there (`p309_qualify.py` 439–441), never `P309_QUALIFICATION.json`. A01e
  compares the listing before and after. My run: pass.
* **Row order.** The explanatory row is logged (tests 395–398) before the ledger snapshot (399). A01c requires exactly
  one new row, starting `HOST_RERUN ABORTED BY Q-HOST`, from `code/p309_qualify.py`, with 0 evaluations. In attempt 8
  the pair is rows 108 and 109 (1-based) of the 112 drill rows, 1 s apart; the validation record's "107/108" counts
  from 0.
* **Why the ledger is not redirected.** It holds. `p309_env.py` 24–25 set `Q.EXEC_LEDGER` by module attribute. QC12 T7
  flags any module-attribute store in tests, including in `python -c` strings (`p309_static_check.py` 268–270). There
  is no environment override. No ledger consumer reads "ABORTED BY Q-HOST" rows (grep of code/tests/verify).
* **The control fails if the abort does not kill.** My mutant (scratch copy; `kill_own_descendants` returns `[]` at
  once): A01a passes, **A01b fails** (`descendants_killed` 0), **A01d fails** (84 TEST processes alive), A01c and A01e
  pass. The test's own cleanup then killed them; none was left.
* **Forking at the abort.** In my run, `descendants_killed` was 84: 2 forkers, their 80 children, 1 leaf and the exited
  monitor. The forkers had finished before the monitor's first sample, so A01 shows the abort on a tree that forked,
  not on one forking during the abort. K01 covers the latter (W7).
* **C5 for the worker-tier drill.** Partly. The drill runs the host controls in both tiers (`p309_topology_drill.py`
  358–359), so A01 will run inside the drill unit as the P309 user. It then shows the runner's abort inside a unit.
  It does not show the unit's `KillMode=control-group` / `KillSignal=SIGKILL` backstop. It does not show the drill's
  stop on rc 3 or `QHOST_FAIL.json` (265). Both remain unexercised, because the drill's own runner passes Q-HOST
  (W7).

## 4. QC12 T14's V1 extension (brief item 4)

`no_raise_or_exit_after_mkdir` (697) fails if any top-level statement at or after the attempt `mkdir` contains an
`ast.Raise` or a call whose function unparses to `sys.exit`, `os._exit`, `exit`, `quit` or `os.abort` (686–687). HEAD
passes. My scratch mutants (`ctl/t14_mutants.py`, calling the committed `t14` on mutated copies):

| mutant | fails |
|---|---|
| T14f shape (`raise SystemExit(2)` in `main`) | `main.no_raise_or_exit_after_mkdir` only |
| T14g shape (`sys.exit(2)` in `main`) | `main.no_raise_or_exit_after_mkdir` only |
| T14h shape (`os._exit(2)` in `host_rerun`) | `host_rerun.no_raise_or_exit_after_mkdir` only |
| `assert qh` | nothing |
| `from sys import exit as bye; bye(2)` | nothing |
| `import sys as s_; s_.exit(2)` | nothing |
| `os.kill(os.getpid(), 9)` (also exempt in the scanner) | nothing |
| `signal.raise_signal(9)` | nothing |
| a helper that raises | nothing |

The committed static controls (19/19) check only that T14 fails, not which sub-check. The check is literal (W5). The
code trees are bound at F (§D rule 1), so this matters only for a future edit.

## 5. The launcher's V2 refusal and V4 blocker (brief item 5)

**V2.**
* `unit_user_check` refuses a foreign root matching `[\s'"\\]` (`p309_launch.py` 100–101). It runs at step 0, before
  the record (155), so a refused launch writes nothing. N05 passes.
* The residual is W3. `unit_properties` redacts `Environment` by prefix (`p309_host.py` 757–759). systemd prints
  string-array properties through its shell quoting. That quoting is triggered by more characters than the refusal
  covers: `` ` ``, `$`, `*`, `?`, `[`, `(`, `)`, `<`, `>`, `|`, `&`, `;`, `!`.
* Such an entry would begin with `"` and be recorded in clear, in `UNIT_PROPERTIES.json` in the attempt and in a
  worker-tier `DRILL_REPORT.json`. I could not run `systemctl show` here (no running manager); the statement rests on
  systemd's printing code.

**V4.**
* The launcher appends `launcher_not_unit_user` when its uid differs from the unit user's (176–177). It writes the
  record exclusively (179–180) and refuses to start (185–186). N04d passes; in my run the blockers were `preflight`,
  `gate`, `isolation`, `systemctl_unavailable`, `launcher_not_unit_user`.
* **Why a blocker.** The gate and isolation are evaluated as the launcher's user. A blocker keeps that evidence in a
  redacted record for review, and nothing starts. A step-0 refusal would leave no record. Either way no attempt
  exists. The only cost is that the official scratch root is no longer empty, so the next official launch needs a
  fresh root.
* I agree with the choice.

## 6. The monitor's V5 timing and the 45 s default (brief item 6)

The bytes:
* `t0 = time.time()` at the start of each loop (`p309_host.py` 661), written as the row's `t` (666);
* a sample = `provenance` (`timedatectl` timeout 20 s at 197; IMDS 1 s timeouts at 226 and 233) + `processes`
  (sleeps 20 s at 376, plus two `/proc` snapshots);
* the next loop starts 60 s after `t0` (673);
* `stop_qhost_monitor` takes `stopped` before it terminates the monitor (480); the row of a sample in progress is
  never written; liveness uses `[started] + t + [stopped]` (488–489; `monitor_liveness` 636–645), limit 60 + 45 = 105
  s (the default at 58).

So gaps between rows are about 60 s, but the **last** gap is up to 60 s plus the duration of the sample in progress.
My virtual-clock run of the committed functions (`ctl/v5_sim.py`; `provenance` and `processes` stubbed to take the
stated time, every stop time in 0.25 s steps):

| sample (provenance + 20.3 s) | HEAD worst gap / limit | `bbfc24f0` worst gap / limit |
|---|---|---|
| normal (0.2 s) | 80.2 / 105 | 60.0 / 90 |
| one sample in five with IMDS timeouts (6 s) | 86.2 / 105 | 65.8 / 90 |
| one sample in five with the `timedatectl` timeout (20 s) | 100.2 / 105 | 79.8 / 90 |
| one sample in five with both (26 s) | **106.2 / 105: FAIL** | 85.8 / 90 |

* The repair removed the gap between rows, but moved the full sample duration into the stop gap.
* The typical margin fell from 30 s to about 25 s. The worst-case margin fell from +4.2 s to −1.2 s.
* The AWS text (138–140, "the default of 45 s leaves a margin") and the response's "worst case about 87 s" are true
  only for gaps between rows.
* A slow final sample is a false positive that ends the single attempt: **SF1**.

## 7. FU3 (brief item 7)

* **Mechanical.** G1.1 names one new file, `governance/R2_GOVERNANCE_ADDITIONS_AFTER_D.json`, added at the freeze step.
  It holds D and F by commit id. Every other path printed by `git diff --name-only --diff-filter=A D F -- FNS2/governance`
  must be listed in it with its sha256 and the review that read it. G1.3 keeps rule 2's
  `--diff-filter=MDRTCUX` (empty) unchanged. G1.2 freezes this file between D and F.
* **Consistent with §D.** Rule 2's list now lives in an added path, which rule 2 allows. G1 states that it supersedes
  §E, whose text stays as written.
* **Append-only.** `git log` of `P309_R2_AMENDMENTS.md` shows exactly `4e6a6901` and `8cb59c0f`. The first version's
  bytes are a prefix of the second's.

## 8. FU4 (brief item 8)

**Present.** §4.1 (AWS 207–227) has all three required elements:
* every P309 process runs as the P309 user;
* the gate is recorded after 8c;
* the uids in its rows are identified, and the window is agreed with every workload, and recorded.

**What it asks of cell 308.** Nothing beyond read-only facts (its uids, from the rows) and agreement on the window. It
asks nothing to be stopped, changed or listed beyond the gate's own rows.

**Defects (SF2).**
* **Step 2's command refuses.** `load_config` rejects unknown keys (`p309_host.py` 124–126). The §3.1 file holds the six
  launch keys, which only `load_launch_config` removes (143–154). My run in the scratch clone, on a TEST configuration
  shaped like §3.1: `gate`, `isolation` and `preflight --config <file>` each print `{"refused": "unknown config keys:
  ['cpu_weight', 'io_weight', 'memory_max', 'oom_score_adjust', 'unit_group', 'unit_user']", "pass": false}`, rc 1.
  The same applies to the 8c commands at AWS 147–148. Those predate this round, and `isolation` would also lack
  `p309_repo`.
* **Step 4's order.** "Read the launch record before an official launch … If either fails, do not launch."
  * The official launcher writes the record and then, with no blocker, starts the unit at once (179–193).
  * The only record readable before a start comes from `--print-only`. That writes `launch_<utc>.json` into the
    scratch root, which an official launch then refuses as non-empty (`p309_host.py` 515–516).
  * The procedure names neither step. The gap fails closed, but an operator who improvises on a shared host is
    exactly what FU4 meant to prevent.

**Safe otherwise.** Every command in §4.1 is read-only; a refusal costs no attempt.

## 9. The re-drill and the evidence (brief item 9)

### 9.1 Attempt 8 (`evidence/drill/20261001T224858Z`, cloud tier, PASS)

* **Report.** sha256 `286bde88…` equals the official ledger row's (`c26fac16`). `clone_base` `8725f8b7`; window
  22:48:58Z–23:59:16Z; all 15 cloud items pass, confined, head unchanged (QC_D5 2956.8 s, QC16 719.6 s).
* **Ledger rows in full (F4).**
  * 112 rows. The exported file equals the report's rows line for line, and the report's `sha256` is
    sha256("\n".join(rows)). Both reproduce.
  * Recomputed from the kept clone: the working ledger (128 lines) extends `8725f8b7`'s committed ledger (16), and the
    112-row extension equals the exported file. The exposure ledger is empty in both.
  * UTC-ordered; one RUN START row (row 2); no required script missing.
  * Counters 0; no `cells_touched`; 60 drift entries, 0 band hits (computed with the drill's own `meets_band`).
  * The A01 pair is rows 108–109 (§3).
* **Controls.** All caught, including M01a (`FREEZE_RECORD`), M01b, second freeze record, TEST-only prior ref, push URL,
  P309 repository refused, no production ref, ledger rows kept across the reset.
* **Host.** Host package tests rc 0 (68), host controls rc 0 (35 pass lines), static controls rc 0 (19), preflight
  failing as expected in the cloud tier, continuity pass, r1 tree unchanged.
* **F2.** `p309_before` equals `p309_after` (head `8725f8b7`, `refs_sha256` `4ca09511…`, status sha256 of the empty
  string). I reconstructed `refs_sha256` from the repository's current `for-each-ref` with the r2 branch and its
  remote-tracking ref set to `8725f8b7`: it gives `4ca09511…`. So no other ref, and no production-namespace ref,
  existed then.
* **Kept clone** (read-only git):
  * F′ `ed89357f` (parent `8725f8b7`; freeze files, the freeze ledger row, `evidence/freeze/PLACEHOLDER_CHECK.json`);
  * FR′ `c9579c0d` (touches only `ledger/FREEZE_RECORD.json`);
  * tip `e5a1b8d0` (touches only `CHECKPOINT_PUSHES.jsonl`);
  * no remote, no `remote.pushDefault`, no production-namespace ref.
* **Validation record.** 44/44 true. Its first-run defect is disclosed and correctly described: the explanatory row
  quotes the abort phrase. The fix to a prefix match is right.
* **The restarts.** `R2_DRILL_ATTEMPT8_VALIDATION.json` names two: during attempt 7, and about 02:03Z. This
  container's boot time is 02:03:27Z, and the report and ledger row were committed afterwards with their sha256 intact.

### 9.2 Attempt 7 and the coordinator-written record

`evidence/drill/20261001T222108Z_INTERRUPTED/INTERRUPTED.json` (sha256 `ba3edec5…`, equal to its ledger row in
`45fff547`) states that the coordinator wrote it, not the drill. Against the kept attempt-7 root (read-only):
* code commit `e3242cbb`; F `a75d5808`, FR `7ddda9fe`, tip `8acb6fee` match the clone's history, with the same touched
  paths as in attempt 8;
* the 104 rows equal the clone's ledger extension beyond `e3242cbb`'s 15 committed lines. Their sha256 `820101db…`
  reproduces. Counters 0, 0 cells, 54 drifts with 0 band hits;
* the three host-control scripts are absent from the rows, consistent with an interruption during items;
* the 14 listed items equal `r2_drill_cloud_7.log`;
* the record names itself INCOMPLETE, with no verdict, superseded and preserved.

The official ledger row's `script` ("coordinator (interruption record)") is not a path. QC13 and QC15 passed in
attempt 8 on a base that contains it, and no code consumes `evidence/drill/`. Handling it as a preserved, unverdicted
attempt followed by a full re-run on identical code bytes is correct.

### 9.3 `R2_REPIN_LIST_SUPPLEMENT_2.json`

All 13 rows reproduce (`ctl/verify_repin2.py`). For each row I checked:
* its `bbfc24f0` config value, and that value's currency at `bbfc24f0`;
* the HEAD config value and the HEAD AST sha256;
* permits and reason;
* kind.

Every reviewed-function entry that changed or was added has a row. No entry was removed. Among existing entries, only
`case_k01` changed its reason (declared). Only `process_policy` differs at top level (`reviewed_functions` and the new
`proc_read_note`). The seven lists claimed unchanged are unchanged, and so are the constant pins.

**Defect in two registered reasons (W4).** The reasons of `case_a01` and `case_k01` say the test passes
`P309_TEST_LEAF` and `P309_TEST_FORKER`; the code passes neither (tests 369, 402). The reason of `case_a01` says
`_qhost_abort` runs "with the attempt and the ledger pointed at that TEST directory". The abort's row goes to the
namespace ledger by design (§3).

### 9.4 `R2_EQUIVALENCE_P8_ROUND3.json`, recomputed

* **(a)** F′'s manifest (kept clone) against r1's F: 72 outside pins with equal paths and records, plus the equal
  candidate-manifest record, make 73. `git diff --quiet 4c754a73 HEAD -- <path>` succeeds for all 72. The runtime
  gains `glibc` and `interpreter_sha256`; `verifier_settings` are equal. Records were compared in memory; no hash was
  printed.
* **(b)** 12 unchanged, 5 relocation-only, 22 beyond the map, 9 new, 0 removed: the identical lists.
  * I recomputed by reverse substitution for every file but two. `config/FORMAL_QUARANTINE_P309.json` and
    `verify/VERIFY_RESULTS_SCOPED.json` I did not read; their blobs are unchanged since `bbfc24f0`, where the previous
    reviewer reproduced their classes.
  * The 7 files changed in this round are all in "beyond the map" or "new", so no file moved class.
* **(c)** 35 lines with the record's token forms, the same (file, line) set. The scanner configuration's note moved
  from line 1803 to 1877 because entries were added.
* **(d)** My `make_freeze_params.py` output at HEAD is byte-identical to F′'s `P309_FREEZE.json`. Its key-path diff
  against r1's F (values not printed): 44 differences, equal to the classified set; 0 unexpected, 0 missing.

## 10. No scientific change (brief item 10)

* In the range, `code/` changed only in `p309_host.py`, `p309_launch.py`, `p309_self_audit.py` (IMMUTABLE list) and
  `p309_static_check.py` (T14). `config/` changed only in `SCANNER_ALLOWANCE_P309.json` (`process_policy` only), and
  `tests/` only in the two control files.
* The driver, guard, verifier, generators (`make_freeze_manifest.py`, `make_freeze_params.py`) and scanner
  (`p309_scan.py`, `p309_scan_pins.py`) are byte-unchanged.
* In my regenerated parameters, `route`, `cell`, `detector`, `m`, `closure_criterion`, `scope`, `outcome_table`,
  `stage1a`, `stage1b`, `stage2`, `u2`, `efficacy` and `independence_statement` equal r1's F.
* `post_grant_derivations` differs only in `execution_host`, and `proposed_execution_host.named` is false.
* The exactly-once sites, backstop pins, T13 pins and production tokens are unchanged.

## 11. Anything new (brief item 11)

* **Fail-open path.** None found in the changed code. The V2 refusal, the V4 blocker and T14 all fail closed.
  `kill_own_descendants` fails closed toward foreign processes; its residual (W1) is a missed descendant, which the
  unit's `KillMode=control-group` / SIGKILL stops in the official run and the host re-run.
* **False positive that consumes the single attempt.**
  * SF1: a slow final sample.
  * Also periodic jobs. §4.1 relies on one gate sample, so a timer or cron job under a non-root account (Ubuntu's
    `man-db` runs `mandb` as `man`; `fwupd-refresh` has its own user) is invisible unless it happens to run then. Under
    option (i) it can end a run if it exceeds the thresholds (W8).
* **Signal to a process not owned by the caller.** None observed. Theoretical pid-reuse windows: W1 (SIGSTOP) and W2
  (the monitor's SIGTERM).
* **Leaking record.**
  * W3: a foreign root with a shell-special character other than those refused.
  * No foreign root or cell-308 pattern appears in clear in any record of my runs. N04b: only the sha256 of the TEST
    root.
* **Refusal after the attempt directory or start line.** None added. Every refusal in `main()` and `host_rerun()` still
  returns before the `mkdir`, and T14 now also covers `raise` and the listed exits.
* **Implicit owner decision.** None.
  * The packet presents option (i) as what the code implements and asks for whole-host agreement as its consequence.
  * The 45 s tolerance is a host-configuration value shown in the packet.
  * The V3 deferral and the A01 design decide nothing for the owner.

## Conditions

**SF1 — before-freeze; before step 8d. The Q-HOST stop gap.**
* Make the liveness rule hold for the worst-case sample duration that the code allows. With the code as it stands,
  that is about 47 s (20 s sleep, 20 s `timedatectl` timeout, 6 s metadata, plus `/proc` and hashing). Keep a stated
  margin. Possible ways:
  * time each row at its start and also write a start-of-sample row that liveness uses;
  * raise `monitor_gap_tolerance_s` (default and the §3.1 example) to at least 60 s;
  * bound the sample's duration.
* Show the bound with a committed control that drives the committed `qhost_monitor` and `monitor_liveness` (a virtual
  clock is enough).
* Correct AWS 138–140. Correct the response's "worst case about 87 s" in the next response.
* If the tolerance or the rule changes, revise packet 245 and host requirements 113 in the same commit, so that the
  packet stays exact for the owner's decision.
* A code change is re-drilled and covered by the next review of the r2 delta.

**SF2 — before-freeze; before step 8d. The FU4 commands.**
* Replace §4.1 step 2's command with one that runs on the §3.1 file. For example, the launcher's `--print-only` in a
  separate fresh scratch root records the gate through `load_launch_config` in a redacted record. Fix the 8c commands
  at AWS 147–148 the same way.
* Make step 4 executable. The pre-launch check reads a `--print-only` record made in a separate scratch root, and the
  official launch then uses another empty one; or move the uid check to the launch record after a blocked launch.
* Text only. No re-drill is needed for it.

**Advisory:**
* **W1.** In `kill_own_descendants`:
  * wait until every seen pid is stopped (`/proc/<pid>/stat` state `T`) or gone, then walk once more before the SIGKILL
    pass, so that a child linked after an asynchronous SIGSTOP is still found;
  * check the start time before the SIGSTOP as well, or open pidfds at discovery.
* **W2.** In `qhost_monitor`, re-check `os.getppid() == parent` immediately before `os.kill(parent, SIGTERM)`.
* **W3.** Refuse foreign roots outside a positive character class (for example `[A-Za-z0-9._/+@,=~-]`, with `:` also
  refused because it separates `P309_FOREIGN_ROOTS`), or redact `Environment` by substring.
* **W4.** Correct the registered reasons of `case_a01` and `case_k01` (no `P309_TEST_LEAF` / `P309_TEST_FORKER`; the
  abort's row goes to the namespace ledger) at the next configuration change before D, with the re-pin.
* **W5.** T14 is literal. Either state that scope in its docstring, or also reject `assert` and aliased exits after the
  `mkdir`.
* **W6.** V3: add worker-tier controls that reach the configuration-file, configuration-hash, unit-property and
  instance-id refusals before D; or record that these branches are exercised nowhere.
* **W7.** Lengthen A01's forkers so that they are still forking at the abort. In the 8d evidence, state that the unit
  backstop and the drill's rc-3 stop remain unexercised.
* **W8.** In §4.1, add a read-only listing of timers and cron jobs that run under non-root accounts (`systemctl
  list-timers --all`), and include them in the window's agreement.

## Disclosure (reads, runs, writes)

**Execution ledger.** `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r2_followup2_review/LEDGER.jsonl`:
one JSON row per command or command group, each with `target_evaluations: 0`. Some read-only groups were logged in
batches right after they ran.

**Reads.**
* The brief; `REVIEW_R2_DELTA_FOLLOWUP_1.md`; `R2_DELTA_RESPONSE_2.md`.
* The full diff of every code, config and test file in the range, and the changed governance texts. The packet,
  amendments §D–§G, AWS instructions §3–§8 and the host requirements in the cited parts. The cited parts of
  `p309_host.py`, `p309_launch.py`, `p309_qualify.py`, `p309_static_check.py`, `p309_topology_drill.py`, `p309_env.py`,
  `make_freeze_params.py`, `p309_placeholder_check.py` and the host-control tests.
* The drill attempt 7 and 8 evidence; the validation record; supplement 2; the P8 round 2 and 3 records; the official
  ledgers.
* `r2_drill_cloud_7.log`, `r2_drill_cloud_8.log` and their `.head` files.
* The kept clones of attempts 7 and 8, through read-only git only (`log`, `rev-list`, `diff-tree --name-only`,
  `for-each-ref`, `remote -v`, `config --get`/`--get-regexp`, `show` of the F′ manifest and parameters and of the base
  ledgers, with `GIT_OPTIONAL_LOCKS=0`), and their working ledger files read as files.
* r1 at `4c754a73` through `git show`: the freeze manifest (pin records compared in memory, no hash printed) and
  `P309_FREEZE.json` (key paths compared, values not printed).
* **Disclosed incidentally.**
  * A `grep` of `p309_topology_drill.py`'s imports printed its line 93, the quarantine band literal. It is a code
    constant, not a cell value, and I used it only through the drill's `meets_band`.
  * Four of the 72 outside pins are cell-307 campaign paths. Their already-recorded pin records were compared in
    memory, and `git diff --quiet` compared their tree entries. I did not open, read or hash those files and printed
    no hash.

**Runs.**
* **In the real repository, read-only git only:** `rev-parse`, `log`, `diff`, `diff-tree`, `show`, `ls-tree`,
  `cat-file`, `for-each-ref`, `rev-list`, `branch --show-current`. `git status` ran twice without `GIT_OPTIONAL_LOCKS=0`
  (at the start and before writing). git may refresh its index stat cache during `status`; no content, ref or config
  changed.
* **One scratch clone** (`--no-local --single-branch`; origin removed; the 7 inherited research tags deleted in the
  clone, leaving only the r2 branch ref). `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR` were in my scratchpad,
  with `PYTHONDONTWRITEBYTECODE=1`. In it I ran:
  * `p309_static_check.py`, `p309_scan.py` and `p309_scan_pins.py --list`;
  * `tests/test_p309_host.py`, `tests/test_p309_host_controls.py` (as root; TEST uids 64011/64012),
    `tests/test_p309_static_controls.py` and `tests/test_p309_scan_allowance.py`;
  * `make_freeze_params.py`;
  * `p309_host.py gate|isolation|preflight --config` on a TEST configuration (each refused at load);
  * `p309_placeholder_check.run()` as a function, with a copy of this file in the clone's `governance/`: PASS, 0
    unallowed hits.
* **A second scratch copy** (`clone_mut`) with the no-kill mutant, running only `case_a01`.
* **My scratch scripts:** `ctl/t14_mutants.py`, `ctl/forkrace3.py` (HEAD, and `bbfc24f0`'s `p309_host.py` from
  `git show`), `ctl/v5_sim.py`, `ctl/verify_repin2.py`, `ctl/p8a.py`, `ctl/p8bc.py`, `ctl/p8d.py` and the drill's
  `meets_band` through import.
* **TEST processes.**
  * Every TEST process I started carried my random token: in argv for my own scripts, their trees and the committed
    tests' top-level processes, and in the environment (`REVIEW_TOKEN`) for the committed tests' children, which also
    carry the tests' own nonces. The exception is the N cases' launcher subprocesses, which the test gives a minimal
    environment and runs to completion.
  * The pre-repair fork-race run held each trial's survivors until they exited by themselves. After 5 of 12 trials I
    stopped it by SIGKILLing every process whose argv carried my token: 11 processes, all started by me (the
    controller and its wrappers, the outside sleeper, and the current trial's remaining TEST processes).
  * After every run, a scan of `/proc` argv and environments found no process with my token or a committed TEST
    token.
  * I signalled no process I did not start.
* **Not run:** the manifest generator, any QC item, any drill, `execute`, `seal-only`, `validate-grant`. No network.

**Writes.**
* This file, not added or committed.
* My scratchpad: the ledger, scripts, outputs, scratch roots, and the two clones, which I deleted by literal path at
  the end.
* The tools I ran wrote ledger rows and evidence only inside those clones or my scratch evidence directories.
* Nothing was written to the kept drill clones or the attempt-7 root.
* No git write of any kind in `/home/user/ReBaseGuard`.

**Firewall.**
* No cell-305–309 value was read.
* No cell-307/308 campaign file was opened or hashed.
* No decoy output was opened.
* No ref under `refs/p5y-k5-cell309-p309-r1/` or `-r2/` was created anywhere; the repository has none (`for-each-ref`).
