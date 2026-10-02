# Third focused follow-up review of the r2 delta repairs (repair round 3) of P309-r2 at 93ea669a
R2_DELTA_FOLLOWUP_3_ACCEPTED

**Reviewer.** A fresh independent reviewer. I wrote none of the r2 code or its repairs, none of the verifier author's
changes, neither the r2 plan nor its addenda, and no earlier r2 review (`REVIEW_R2_DELTA.md`,
`REVIEW_R2_DELTA_FOLLOWUP_1.md`, `REVIEW_R2_DELTA_FOLLOWUP_2.md`). I am not the coordinator.

**Brief.** `governance/BRIEF_R2_DELTA_FOLLOWUP_3.md`, committed in `ffa11f54` before issue. Sections 1–10 below map to
its items 1–10. `R2_DELTA_RESPONSE_3.md` and `REVIEW_R2_DELTA_FOLLOWUP_2.md` were used as guides only. Every statement
below rests on git, the committed evidence, the kept drill clone read with read-only git, or a run in my own scratch
clone.

**State reviewed.**
* Branch `claude/p5y-k5-cell309-p309-r2`, HEAD `93ea669a1f3b825dbbd6c44b367379749fc10704`; working tree clean before
  this file was written.
* Range `9dcd9d53..93ea669a`: 4 commits, linear, no merge (`8c2aa69f`, `86706ca3`, `ffa11f54`, `93ea669a`). Every path
  is inside FNS2.
* Code commit `8c2aa69f`. The tree ids of `code` (`0ef04141`), `config` (`f6b877f3`), `fc2` (`647d2951`), `tests`
  (`b6800930`), `verify` (`d6b4ba88`) and `start_state` (`716666f2`) are identical at `8c2aa69f`, at `86706ca3`
  (attempt 9's clone base), at `ffa11f54` and at HEAD. At `9dcd9d53` they were `3c345ac3`, `23abf619`, `647d2951`,
  `d01e769f`, `d6b4ba88` and `716666f2`. r1's tree is `ecd1c359` at HEAD.

**NEW Γ309 TARGET EVALUATIONS = 0.** This review ran no `execute`, `seal-only` or `validate-grant`, no QC item and no
drill. It read no target input and opened no decoy output. It created no ref under either production namespace,
anywhere; the repository has none.

## 0. Verdict in brief

**Accepted. Every condition below is advisory.** SF1 and SF2 are met in the bytes. The packet still decides nothing and
now states the gap rule. Nothing scientific changed.

**What I reproduced:**
* QC12 T1–T14 PASS; scanner PASS (36 files, 0 findings); pins all current.
* Host package tests 73/73, MV01–MV05 included. Host controls 37/37: P02 as root with `setpriv`, K01, A01, N06, U00.
  Static controls 22/22.
* My T14 mutants: the T14i–k shapes each fail exactly `main.no_raise_or_exit_after_mkdir`.
* SF1, on a virtual clock driving the committed `qhost_monitor` and `monitor_liveness`:
  * every stop passes for every constant sample duration up to 105 s;
  * 60 000 random stops over mixed 20–47 s samples all pass, with a worst gap of 47.4 s;
  * the committed runner `start_qhost_monitor` / `stop_qhost_monitor`, with a real monitor child, passes on the real
    monotonic clock (§2).
* SF2: the §3 `--print-only` command runs as written on a §3.1-shaped TEST file, in both modes. A check directory
  reused as an official scratch root is refused (§3).
* All 10 rows of `R2_REPIN_LIST_SUPPLEMENT_3.json` reproduce. P8 (a)–(d) reproduce, and my `P309_FREEZE.json` is
  byte-identical to F′'s.
* Drill attempt 9:
  * the report's sha256 equals its ledger row;
  * the 112 rows equal the kept clone's ledger extension;
  * counters are 0, with 0 band hits;
  * F2 holds: I reconstructed `refs_sha256` from the repository.

**New findings, all advisory** (§10 and `## Conditions`):
* **X1.** The order check alone can fail Q-HOST at the stop. The cause is the 1 ms rounding of `m`. The chance is about
  4.5 × 10⁻⁶ per stop: rare, but it would end the single attempt.
* **X2.** `kill_own_descendants` can still end one walk too early. In my slow-fork control (1 GB TEST forkers), 8 of 20
  trials left live descendants that were born during the call. A one-line reordering, tested in scratch, left 0 of 20.
  The unit's backstop covers the official run (§4).
* **X3–X7.** Smaller points:
  * MV coverage of the runner's own selection;
  * A01's unbounded forkers on a failure path;
  * U01's clear-text copy of the host configuration;
  * T14's docstring;
  * the 8c, working-directory and W8 operator texts.

## 1. SF1–SF2 and W1–W8 (brief item 1)

| id | status | evidence |
|---|---|---|
| SF1 | **met** | `p309_host.py`: `MonitorIO` 651–676; the start-of-sample row with `m` 692–693; the result row with `m` taken after the sample 697–701. `p309_qualify.py`: `started` 466 and `stopped` 481, both on `time.monotonic()`; every JSON row's `m` goes to `monitor_liveness` 488–491; at least one completed sample, and all of them passing, 489 and 494. Committed control MV01–MV05 (`tests/test_p309_host.py` 132–193). Texts revised in the same commit: AWS 138–145, packet 248–251, host requirements 113, amendments H1 (178–185). The "87 s" correction is in response 3. My controls are in §2 |
| SF2 | **met** | AWS §3 149–165, §4.1 step 2 229–238, step 4 245–253; bootstrap 67–69. Every command runs as written on the §3.1 file, and the check directory is kept apart from every run's scratch root (§3) |
| W1 | **partly met** | The start time is checked before SIGSTOP (750–751) and before SIGKILL (763–764), and the loop waits for the stops to take effect (756–760). But it can end on a walk made before the last stop took effect: X2 (§4) |
| W2 | met | `MonitorIO.signal_parent` (668–672) re-checks `os.getppid() == parent` immediately before `os.kill` |
| W3 | met | `p309_launch.py` 101–102 accept only `/[A-Za-z0-9._/+@,=~-]*`; docstring 8–11; N05 and N06 pass; amendments H2. As I read systemd's shell-quoting set (whitespace, `"`, `\`, `` ` ``, `$`, `*`, `?`, `[`, `'`, `(`, `)`, `<`, `>`, `\|`, `&`, `;`, `!`), no allowed character is quoted. I could not run `systemctl show` here |
| W4 | met | The reasons of `case_a01` and `case_k01` no longer name `P309_TEST_LEAF` / `P309_TEST_FORKER`. `case_a01`'s reason states that the abort's row goes to the namespace ledger. Supplement 3 rows 8–9 |
| W5 | met | The T14 docstring (65–71) states the syntactic scope. `assert` and from-import aliases are rejected (671–684, 700–701). Mutants T14i–k are added (static controls 75–80). The residual is X6 (§5) |
| W6 | partly met, with the deferral now in the bytes | U01–U03 (`tests/test_p309_host_controls.py` 270–292) reach three in-unit refusals on the worker tier (§6). The unit-property and instance-id branches are recorded as exercised nowhere: amendments H3 (191–196), AWS 257–263, test docstring 27–31 |
| W7 | met | A01's forkers keep forking until the abort (tests 125–127). AWS 257–263 requires the 8d report to state that the unit backstop and the drill's rc-3 stop remain unexercised. Failure-path note: X4 |
| W8 | met in part | AWS 229–244 add read-only listings of timers and system cron files and a request to the administrator for per-user crontabs. The listings do not show the account a job runs under: X7 |

## 2. SF1 in depth (brief item 2)

**The bound, from the bytes.** A sample of duration D runs between its start row and its result row.
* The gap from the start row to the result row is D.
* The gap from the result row to the next start row is max(0, 60 − D) plus the sleep's overshoot (705).
* At a stop during a sample, the last gap is at most D. At a stop during the sleep, it is at most 60 − D.
* The first gap runs from the runner's start (466, taken before `Popen`) to the monitor's first start row. That is the
  child's start-up: 0.06 s and 0.09 s in my runs.

So every gap is at most max(D, 60 − D) + ε. That is at most 60 s for D ≤ 60, and exactly D above 60. The limit is
60 + 45 = 105 s, so only a sample longer than 105 s (or a monitor start-up over 105 s) fails liveness. The interval is
fixed at 60 (`QHOST_INTERVAL`, 427). D is at least 20 s (the process sample) and about 47 s with every timeout; the code
sets no upper bound, so a hanging sample fails, as the texts say.

**Controls on the committed functions** (`ctl/sf1_sim.py`). `qhost_monitor` runs with its `MonitorIO` replaced by a
virtual clock; the sleep overshoots by 1.1 ms and a row is written 30 µs after its `m` is read. The runner's own rule
is then applied to the rows written before each stop: every JSON row's `m`, then `monitor_liveness`, and at least one
completed sample.

| case | stops | result |
|---|---|---|
| constant D = 20, 22.5, … 110 s | every 0.25 s over 30 min | worst gap max(D, 60 − D): 40 s at D = 20, 47 s at D = 47, D above 60. All stops pass up to D = 105.0 s; the first failing D in the grid is 107.5 s |
| mixed durations 20.2–47.4 s, 200 runs | 60 000 random | 0 failures; worst gap 47.4 s |
| five 20.3 s samples, then one that hangs 104 s | 103.9 s into it | pass; max gap 103.9 s; 143.6 s from the last completed result row to the stop |

**On the real clock** (`ctl/runner_qhost.py`). This drives the committed `start_qhost_monitor` and
`stop_qhost_monitor` with a real `p309_host.py qhost-monitor` child:
* the attempt is a TEST directory, with the label `host_rerun`;
* TEST thresholds let every sample pass;
* the run is in a network namespace with no network.

| stop after | result |
|---|---|
| 47 s | pass; 1 sample; max gap 26.9 s |
| 95 s | pass; 2 samples; max gap 40.0 s |

In both runs the first start row came 0.06–0.09 s after the runner's start. The monitor was terminated (rc −15), and
the final continuity passed.

**The shared clock.** Both sides call `time.monotonic()`, which is CLOCK_MONOTONIC on Linux.
* The monitor is a direct `Popen` child (467–469), with no `unshare` or `setns`, so it shares the runner's time
  namespace. A systemd unit creates no time namespace.
* A wall-clock step no longer moves either side.
* A suspend does not advance CLOCK_MONOTONIC. The continuity check (`no_suspend`, `p309_host.py` 288–289) catches it.
* My real-clock runs agree: every `m` lies between the runner's start and its stop.

**MV01–MV05.** They subclass `MonitorIO` (tests 132–158) and call the committed `qhost_monitor` and
`monitor_liveness`. I ran the committed `tests/test_p309_host.py` against mutated copies of the loop
(`ctl/mv_mutants.py`, in the scratch clone, restored afterwards).

| mutant | caught by |
|---|---|
| no start row | MV02 and MV05. MV01 alone passes, because its gap is exactly 60 |
| start row written after the sample | MV02 and MV03 |
| result row timed at the sample's start | MV03 only, incidentally. Its liveness is still sound in reality: the start rows bound every gap by 60 s |
| sleep a full interval after each sample (cadence lost) | nothing (73/73 pass) |

MV04 catches a liveness that ignores gaps, and MV03 tells round 2's scheme from round 3's (106.5 s).

**What MV01–MV05 do not cover.**
* **The runner's selection.** They re-implement `stop_qhost_monitor`'s selection, choosing rows by their `m`
  (`e["m"] <= stop`, tests 170–177) rather than by when they were written. So:
  * a change of 490 to result rows only would pass them;
  * that change would also pass every cloud-tier control, because the cloud tier never runs the runner's start or
    stop: the drill runs `main()` only on the worker tier (`p309_topology_drill.py` 256–266);
  * they cannot show X1 (below).
* **The cadence,** as in the last row of the table.

Both are X3.

**Is Q-HOST weaker than before?**
* **A monitor that writes start rows but no result rows** is impossible in the committed loop (689–705). Each start
  row is followed by its sample, then its result row, then the sleep:
  * a sample that raises ends the monitor, so `alive_at_stop` is false and the run fails;
  * a sample that hangs writes nothing more, and fails after 105 s.
* **A sample whose result row never arrives** happens only for the sample in progress at the stop. Its start row
  counts for liveness and its result is lost, as in round 2, where the in-progress row was never written either.
  * The consequence: the end of the run is now judged like the middle. A last sample that hangs up to 105 s passes,
    and the span without a completed observation can then reach about 144 s (my third case).
  * The same span already passed mid-run in round 2: a hanging sample followed by the next one.
  * The final provenance at the stop (492–493) still checks continuity.
  * I do not count this as a weakening.
* **A new way to fail wrongly (X1).** `samples_in_order` requires every gap to be ≥ 0 (`p309_host.py` 646). The
  monitor rounds `m` to 1 ms (693, 697); the runner's `stopped` (481) is not rounded. A gap goes negative, and Q-HOST
  FAILs, in two cases:
  * a row written less than 0.5 ms before the stop whose `m` rounds up past `stopped`;
  * a row written between `stopped` (481) and `terminate()` (483).

  With the committed functions: a row written at 2047.000730 carries `m` 2047.001; a stop at 2047.000830 gives
  `samples_in_order: false`, `pass: false`.

  My Monte Carlo over real-valued clocks puts the exposure at about 0.14 ms per stop. Rows arrive at 2 per 60 s, so the
  chance is about **4.5 × 10⁻⁶ per stop**. There is one stop per official attempt and one per host re-run.

  Round 2 had no such exposure: its rows carried their sample's start time and were written at least 20 s later.
  * The same parse (488) would also raise on a torn last line, after the attempt directory exists. A write of a
    ~400-byte line to a regular file is practically atomic, and round 2 parsed the same way. I note it only with X1.

## 3. SF2 (brief item 3)

**§3 / bootstrap 8c (AWS 155–157; bootstrap 67–69).** The command is `P309_SCRATCH_ROOT=<dir>
P309_FOREIGN_ROOTS=<paths> python3.11 -B code/p309_launch.py --mode drill --host-config ~/p309_host_config.json
--print-only`.
* The launcher reads the file through `load_launch_config` (`p309_launch.py` 155; `p309_host.py` 143–153), which
  removes the six launch keys before `load_config`.
* **My run.** A TEST file with exactly §3.1's keys (`sample_s` 3), `python3.11`, a fresh check directory, network
  namespace:
  * rc 1, no refusal at load;
  * one record `launch_<utc>.json`;
  * blockers `preflight`, `gate`, `isolation`, `systemctl_unavailable`, `launcher_not_unit_user`, all expected here:
    no systemd, a root launcher, unit user `nobody`;
  * the TEST foreign root and the TEST heavy pattern are absent in clear.

**§4.1 step 4 (AWS 245–253).** The same command with `--mode official`, in a second fresh directory:
* the same result, with `require_empty_scratch: true` in the record;
* that check directory, reused as an official launch's root, is refused with `{"launched": false, "refused":
  "P309_SCRATCH_ROOT is not empty"}` (rc 2; `p309_host.py` 515–516).

**§4.1 step 2 (AWS 229–238).** The §3 check, `systemctl list-timers --all --no-pager` and `ls -l /etc/cron.d
/etc/crontab /etc/cron.hourly /etc/cron.daily`. All are read-only and run as written. Here there is no systemd, and the
`ls` exits 2 for the absent paths but lists the rest.

**The note at AWS 162–165.** `p309_host.py preflight|gate --config <copy without the six keys>` runs. `isolation` with
the added `--config-json '{"p309_repo": …}'` also runs; here it fails only `foreign_roots_unreadable`, because I ran as
root. The full §3.1 file is refused, as the note says.

**The check directory is kept apart from every run's scratch root:**
* by the texts (AWS 159–160 and 250–251; bootstrap 69);
* for an official run or a host re-run, by the empty-root refusal.

A drill root is not required to be empty in code; the text requires a fresh one (AWS 171).

**Notes (X7).**
* **8c is tighter than before.** At 8c, "must report no blocker" now includes the exclusion gate: a 60 s sample with no
  foreign or unattributable activity, and the load at baseline. Before, 8c required only isolation and the preflight.
  This fails closed, but the text should say so.
* **The working directory.** "From the clone" with `code/p309_launch.py` means the namespace directory, not the clone
  root. The 8d command uses the same convention. From the clone root the command fails at once.

## 4. `kill_own_descendants` (brief item 4; W1)

**The bytes** (`p309_host.py` 729–770). Each round:
1. walks the whole tree below `os.getpid()` (740–748);
2. SIGSTOPs each new pid whose start time is unchanged (749–755);
3. computes `settled`: every seen pid is stopped, a zombie, gone or reused (756).

The loop ends when the round found nothing new and `settled` holds (757–758). If nothing was new but `settled` does not
hold, it sleeps 5 ms (759–760). The SIGKILL pass then checks the start time again (761–770).

**Termination.** The loop is bounded at 2000 rounds (739). A seen pid that never reaches `T` makes it run every round
(a long `D` state, a SIGCONT from elsewhere, or EPERM; NoNewPrivileges rules out set-uid descendants in the unit). That
is at least 2000 × 5 ms plus the walks, then the SIGKILL pass. The loop cannot fail to end. In my 42 completed
slow-fork trials the call took 0.018–0.168 s.

**Confinement.**
* The walk is rooted at the caller and never yields the caller (743–744).
* Only pids found below the caller are signalled, each after a start-time check.
* An escaped descendant reparented to pid 1 is never signalled later, because it was never seen.
* The outside TEST process stayed untouched in K01, in A01 and in all 42 completed slow-fork trials.

**The remaining race (X2).** `settled` is computed *after* the round's walk. Take a pid whose SIGSTOP went out in the
previous round but has not yet taken effect, for example one inside a slow `fork()`:
1. the walk runs and finds nothing new;
2. the pid links a child and only then stops;
3. the settled check now passes, so the loop ends without that child.

My control (`ctl/kod_slowfork.py`):
* two SIGTERM-ignoring TEST forkers, each with 1 GB resident memory, fork continuously;
* the driver calls the function after 0.2–1.0 s and checks 2 s later, discounting processes with SIGKILL pending.

| function | trials | trials with survivors | survivors | per trial |
|---|---|---|---|---|
| HEAD | 20 | **8** | 9, all state `S`, reparented to pid 1, born during the call, never signalled | 38–175 killed; call 0.018–0.124 s |
| scratch variant: break only when a walk *begun after* a settled observation finds nothing new | 20 | 0 | — | 67–168 killed; call ≤ 0.17 s |

The scratch variant's change is: `if not new and settled_before: break`, then
`settled_before = all(...)`, then sleep if not settled.

**Impact.**
* **In the official run and a host re-run:** the runner exits at once (`os._exit(3)`, `p309_qualify.py` 449). The
  unit's `KillMode=control-group` with `KillSignal=SIGKILL` then stops anything left, so an escapee lives a few
  milliseconds longer.
* **On the worker tier:** the drill unit gives the same backstop.
* **A01:** its forkers are small Python processes that fork quickly. It passed here (37/37) and in attempt 9.

So this is advisory. Every survivor of my runs was killed by token, and none remains.

## 5. T14 (brief item 5; W5)

**The bytes** (`p309_static_check.py`):
* docstring 65–71;
* `T14_EXITS` 671 and `_exit_like` 674–678;
* `exit_names`, the from-import aliases anywhere in the file, 683–684;
* `i_x2` 700–701, which counts any `Raise`, any `Assert` or an exit-like call.

**My mutants** (`ctl/t14_mutants.py`, the committed `t14` on scratch copies):

| mutant | fails |
|---|---|
| T14i shape (`assert qh`) | `main.no_raise_or_exit_after_mkdir` only |
| T14j shape (`from sys import exit as _leave; _leave(2)`) | `main.no_raise_or_exit_after_mkdir` only |
| T14k shape (`os.kill(os.getpid(), 9)`) | `main.no_raise_or_exit_after_mkdir` only |
| `import sys as s_; s_.exit(2)` | `main.no_raise_or_exit_after_mkdir` (the attribute is caught) |
| `assert qh` in `host_rerun` | `host_rerun.no_raise_or_exit_after_mkdir` |
| `bye = sys.exit; bye(2)` | nothing |
| `getattr(sys, "exit")(2)` | nothing |
| `signal.pthread_kill(threading.get_ident(), 9)` | nothing |
| `os.execv(PY, [...])` | nothing |
| `signal.alarm(1)` | nothing |
| a helper that raises | nothing (declared out of scope) |
| `QHOST['monitor'].kill()` before `host_rerun`'s stop | `host_rerun.no_raise_or_exit_after_mkdir`: any `.kill` attribute counts, so the check fails closed |

* The docstring says the check is syntactic and does not follow calls (71). That holds.
* Its phrase "by any name or attribute" (69) overstates: a name bound by assignment is not caught (X6).
* The code trees are bound at F (§D rule 1), so this matters only for a future edit, and that edit would be reviewed.

## 6. The in-unit controls U01–U03 (brief item 6; W6)

**When they run.** Only with `INVOCATION_ID`, `P309_LAUNCH_RECORD` and `P309_HOST_CONFIG` set and a `.service` cgroup
(272–274). Otherwise U00 records "not applicable": my run, and attempt 9's 37 lines.

**How they run.** Each case runs `Q_CODE` (143–152), which calls `qhost_preflight(("official", "drill"))` in a child.
The child gets the unit's environment plus `P309_TEST_CODE` and the altered paths (288). It inherits `INVOCATION_ID`
and the unit cgroup. Inside a correct worker-tier drill unit, the record's mode is `drill`, it has no blockers, and the
clone lies under the launch's root, so the checks before 403 pass.

**Each case reaches the refusal it names:**
* **U01.** The real record, with a configuration copy that has one extra newline (279): the same JSON, other bytes.
  404–405 refuse with "the host configuration file is missing or differs from the one the launch record binds". That
  contains "configuration file" and not "configuration differs".
* **U02.** A record copy with `host_config_sha256` set to 64 zeros (281), and the real configuration.
  * 404 passes, because the copy keeps `host_config_file_sha256`.
  * 406–408 refuse with "the host configuration differs from the one the launcher used".
* **U03.** A record copy whose `preflight.provenance.boot_id` differs (283–284).
  * The file and hash checks pass.
  * The unit properties (409–412) pass in a correct unit.
  * The instance-id check (415–417) passes when the launch and now both read IMDS, or neither does.
  * Continuity (418–420) fails `same_boot`, giving "the host changed since the launch: …". "host changed" lies within
    the first 200 characters.

**Fail-closed.** A case passes only with rc 0 and its own substring (292), so an earlier or different refusal fails it.

**Confinement.**
* The copies go to `E.scratch_dir("host_controls")/U_records` (275–276; `p309_env.py` 47–54), under
  `P309_SCRATCH_ROOT`. The launcher sets that to the launch's scratch root (`p309_launch.py` 124).
* `qhost_preflight` itself refuses a record outside that root (393–394), so a misplaced copy would fail U02 or U03.
* The unit's `ReadWritePaths` cover that root (132).

**X5.** U01's copy is the whole host configuration file. It holds the foreign roots and the cell-308 patterns in clear.
`write_text` creates it with the default mode (0644 under umask 022), in the launch's scratch root on the shared host,
and it stays there until that root is removed. It is a TEST input, not a record, and it is not exported. Everywhere
else P309 keeps these values only as sha256.

## 7. The re-drill and the evidence (brief item 7)

### 7.1 Attempt 9 (`evidence/drill/20261002T025624Z`, cloud tier, PASS)

* **Report and window.**
  * The report's sha256 is `7317fa74…`. It equals the official ledger row added in `ffa11f54`.
  * `clone_base` is `86706ca3`; the window is 02:56:24Z–04:14:39Z.
  * All 15 cloud items pass, confined, with head unchanged (QC_D5 3404.4 s, QC16 738.2 s).
* **Ledger rows in full (F4).**
  * There are 112 rows. The exported file equals the report's rows line for line.
  * The report's sha256 is sha256("\n".join(rows)), and it reproduces. The exposure extension is empty.
  * In the kept clone, the working ledger (129 lines) is `86706ca3`'s committed 17 lines plus exactly the 112 exported
    rows. The exposure ledger equals its base.
  * The rows are UTC-ordered, with one RUN START row and no required script missing. Counters are 0, with no
    `cells_touched`. There are 60 drift entries and 0 band hits, computed with the drill's own `meets_band`; no band
    value was printed.
  * Rows 108–109 (1-based) are the A01 pair: the control's explanatory row (`tests/test_p309_host_controls.py`), then
    the abort's row (`code/p309_qualify.py`).
* **Controls.** All 9 were caught.
* **Host.** Package tests rc 0 (73). Host controls rc 0, with 37 pass lines, equal to my 37 cases. Static controls rc 0
  (22). The preflight failed as expected in the cloud tier; continuity passed; the r1 tree was unchanged.
* **F2.** `p309_before` equals `p309_after`: head `86706ca3`, `refs_sha256` `f2f3007d…`, and the status sha256 is that
  of the empty string.
  * I rebuilt `refs_sha256` from the repository's current `for-each-ref`, with the r2 branch **and** its
    remote-tracking ref set to `86706ca3`, and it is equal. With the branch alone it is not equal.
  * So the push of `86706ca3` preceded the drill, and no other ref existed then. In particular there was no
    production-namespace ref.
* **The kept clone** (read-only git):
  * F′ `2d8849c9` has parent `86706ca3` and touches the freeze files, the freeze ledger row and
    `evidence/freeze/PLACEHOLDER_CHECK.json`;
  * FR′ `e582ab00` touches only `ledger/FREEZE_RECORD.json`;
  * the tip `4298b9f9` touches only `CHECKPOINT_PUSHES.jsonl`;
  * there is no remote and no `remote.pushDefault`. The refs are the branch and 7 inherited research tags, with no
    production-namespace ref.
* **The validation record** (44/44). Every claim of it that I re-derived agrees.
* **No restart.** This container's boot was at about 02:03Z (uptime 2 h 20 min at 04:23:41Z). That is before the
  attempt's start, which matches the record's "no container restart during this attempt".

### 7.2 `R2_REPIN_LIST_SUPPLEMENT_3.json`

All 10 rows reproduce (`ctl/verify_repin3.py`). For each row I checked:
* the `5273b908` configuration value, and its currency against `5273b908`'s own file;
* the HEAD configuration value and the HEAD AST sha256;
* the permits and the reason;
* the kind.

Between `5273b908` and HEAD:
* only `process_policy.reviewed_functions` differs: 10 entries changed or added, 0 removed, every one with a row;
* the seven lists claimed unchanged are unchanged, and so is the import policy;
* none of the 10 entries exists in r1's configuration at F, so `r1_at_F: null` is right;
* `kill_own_descendants`' permits are only reordered, and its reason changed, as declared.

### 7.3 `R2_EQUIVALENCE_P8_ROUND4.json`, recomputed

* **(a) Outside pins.**
  * F′'s manifest (kept clone) against r1's F: 72 outside pins with equal paths and records, plus the equal
    candidate-manifest record, make 73.
  * `git diff --quiet 4c754a73 HEAD -- <path>` succeeds for the 68 outside paths that are not cell-305–309 campaign
    paths. The other 4 name another cell campaign (305–308). For those I only compared their recorded pin records in
    memory.
  * The runtime gains `glibc` and `interpreter_sha256`; `verifier_settings` are equal.
* **(b) Classes.** Over code, config, fc2, tests, verify and start_state: r2 has 48 files and r1 has 39; 0 were
  removed.
  * 12 unchanged.
  * 5 relocation-only: 4 by my reverse substitution (`p309_r2`→`p309_r1`, `p309-r2`→`p309-r1`), plus
    `config/FORMAL_QUARANTINE_P309.json`. I did not read that file; it is unchanged since `bbfc24f0` and `5273b908`.
  * 22 beyond the map: 21 plus `verify/VERIFY_RESULTS_SCOPED.json`, also not read and also unchanged.
  * 9 new.

  These are the identical lists, with no moves.
* **(c) Tokens.** 35 occurrences, the same (file, line) set. The scanner configuration's note is now at line 1912.
* **(d) Parameters.** My `make_freeze_params.py` output at HEAD is byte-identical to F′'s `P309_FREEZE.json`. Its key
  diff against r1's F has 44 differences, equal in paths and kinds to the classified set: 0 unexpected, 0 missing.

## 8. No scientific change (brief item 8)

* **What changed.** `code/` changed only in:
  * `p309_host.py` (Q-HOST monitor, `kill_own_descendants`, `_state`);
  * `p309_launch.py` (W3);
  * `p309_qualify.py` (the monotonic start and stop, and liveness over every event);
  * `p309_self_audit.py` (IMMUTABLE adds the second follow-up's four files);
  * `p309_static_check.py` (T14).

  `config/` changed only in `SCANNER_ALLOWANCE_P309.json` (`reviewed_functions`). `tests/` changed only in
  `test_p309_host.py`, `test_p309_host_controls.py` and `test_p309_static_controls.py`.
* **The IMMUTABLE additions.** Each of the four files was committed once (`c26fac16`; `1f5e7771`). The two sha256
  values in `REVIEW_R2_DELTA_FOLLOWUP_2.sha256` match the files.
* **What did not change.** These are byte-unchanged over the range (`git diff --stat` is empty):
  * the driver and the guard;
  * `verify/`;
  * the generators (`make_freeze_manifest.py`, `make_freeze_params.py`);
  * the scanner (`p309_scan.py`, `p309_scan_pins.py`);
  * `fc2/` and `start_state/`.
* **The regenerated parameters.** `route`, `cell`, `detector`, `m`, `closure_criterion`, `scope`, `outcome_table`,
  `stage1a`, `stage1b`, `stage2`, `u2`, `efficacy` and `independence_statement` equal r1's F.
  `post_grant_derivations` differs only in `execution_host`, and `proposed_execution_host.named` is false.
* **The pins.** The exactly-once sites, backstop pins, T13 pins and production tokens are unchanged.

## 9. The governance texts (brief item 9)

* **`OWNER_DECISION_PACKET_R2.md`.** The diff has 9 insertions and 3 deletions: the revision notes (16–19) and the gap
  rule (248–251).
  * **It decides nothing.** Lines 3–4 and "The coordinator does not choose." (284, 328) are unchanged, and no option
    is taken.
  * **The rule is stated exactly.** "Gaps are measured on the monotonic clock between the runner's start, every
    monitor event (a start-of-sample row and a result row per sample) and the stop", against 60 s + 45 s. That matches
    `p309_qualify.py` 488–491 and `p309_host.py` 636–648.
  * **Its consequence sentence is right in substance but not exhaustive.** The sentence is "only a monitor that dies,
    or a sample that hangs for more than 105 s, ends the attempt this way". It omits:
    * a monitor start-up over 105 s;
    * X1's order check;
    * the separate "no completed sample" rule (494). H1 states that rule; the packet's list does not.

    For the owner's choice under OD-R2-5 these are immaterial, so they are advisory (with X1).
* **`P309_R2_AMENDMENTS.md` §H.**
  * It is append-only: its three versions (`4e6a6901`, `8cb59c0f`, `8c2aa69f`) are each a byte prefix of the next.
  * H1 matches the bytes, including "if no sample completed".
  * H2 matches the launcher, and H3 matches the tests.
* **AWS instructions.**
  * 138–145 are corrected.
  * §3 (149–165) and §4.1 (229–253) are executable (§3 above).
  * 257–263 state what 8d does not show.
* **Host requirements** 113 and **bootstrap** 67–69 agree with the bytes.
* **The response's correction.** Response 3 corrects response 2's "about 87 s", which stays as written.

## 10. Anything new (brief item 10)

* **Fail-open path.** None found.
  * A JSON row without `m` gives 0, which makes a negative gap and so a FAIL.
  * A row that is not `kind: sample` cannot pass as a sample.
  * The refusals added for W3 and T14 fail closed.
* **False positive that would consume the single attempt.**
  * X1: about 4.5 × 10⁻⁶ per stop.
  * X2 is not one: it is a missed descendant, and the unit stops it.
  * The 8c gate tightening (X7) costs a check, not an attempt.
* **Signal to a process the caller does not own.** None.
  * W2 closed the monitor's window.
  * SIGSTOP and SIGKILL each check the start time.
  * Escaped descendants are never signalled.
  * `kill_token` in the tests signals only argv carrying that run's 12-hex token.
* **Leaking record.** None among the records: the SF2 check records are redacted (§3). X5 concerns a TEST input file,
  not a record.
* **Refusal after the attempt directory.** None added; T14 passes. On the stop's parse, see X1.
* **Implicit owner decision.** None.
  * The packet's change states the rule.
  * The SF2 procedure decides nothing for the owner.
  * Agreeing windows "for the whole host" was already in the packet as a consequence of option (i).

## Conditions

None is blocking-before-owner-decisions, and none is before-freeze. All are **advisory**. I recommend folding X1, X2,
X3 and X6 into any code change made before D.

* **X1 — advisory. The Q-HOST order check at the stop.**
  * Judge the last gap as max(0, stop − m), or stop rounding `m` (`p309_host.py` 693, 697). Alternatively, take the
    stop time only after the monitor is reaped and ignore rows after it.
  * Parse the monitor file line by line, tolerating a torn last line.
  * Add a virtual-clock case where a row's rounded `m` exceeds the stop.
  * Until then, the packet's sentence at 250–251 should name the order check and the "no completed sample" rule.
* **X2 — advisory. `kill_own_descendants`.**
  * End the loop only when a walk that began after a settled observation finds nothing new. My scratch variant does
    this: `if not new and settled_before: break`, then recompute `settled_before`.
  * Add a slow-fork case to K01 (large resident memory, continuous `fork`).
* **X3 — advisory. MV coverage.**
  * Add a cloud-tier control that runs the committed `start_qhost_monitor` / `stop_qhost_monitor` with a real
    monitor, as my `ctl/runner_qhost.py` does.
  * Let the MV harness select rows by the time they were written, not by their `m`.
  * Assert the cadence: start rows 60 s apart while D < 60.
* **X4 — advisory. A01's forkers.** Bound them, for example with a deadline or a count. Today, if the abort never
  fires, the forkers start about 20 TEST processes per second each for the 120 s of the ABORT child's sleep, and the
  one-pass `kill_token` can miss leaves started during its scan. The unit's limits cap this on the worker tier; the
  cloud tier has no such cap.
* **X5 — advisory. U01's copy.** Write it with mode 0600 and remove `U_records` at the end of the case. Or write a copy
  whose foreign values are replaced by TEST values: the refusal at 404 needs only other bytes.
* **X6 — advisory. T14's docstring.** Replace "by any name" with "by these names, as an attribute, or through a
  from-import alias". Also list what is not covered: assignment aliases, `getattr`, `exec*`, `pthread_kill` and
  `alarm`.
* **X7 — advisory. The operator texts.**
  * State that the 8c check's "no blocker" includes the gate, so 8c needs an agreed quiet moment.
  * State the working directory (the namespace directory) for `code/...` commands.
  * For W8, show the account for each job: the `User=` of each timer's service (`systemctl show -p User,DynamicUser
    <service>`), and the user field of `/etc/crontab` and `/etc/cron.d/*`.
  * Note that the gate record keeps at most 80 process rows (`p309_host.py` 453).

## Disclosure (reads, runs, writes)

**Execution ledger.**
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r2_followup3_review/LEDGER.jsonl`
holds one JSON row per command or command group, each with `target_evaluations: 0`.

**Reads.**
* **Briefs and guides:** the brief; `REVIEW_R2_DELTA_FOLLOWUP_2.md`; `R2_DELTA_RESPONSE_3.md`.
* **The range:** the full diff of every code, config and test file in the range, and of the changed governance texts.
* **Governance texts in the cited parts:** the packet; amendments §H; AWS §3–§8; the host requirements; bootstrap 8c;
  the literal disposition.
* **Code in the cited parts:**
  * `p309_host.py`, `p309_launch.py`, `p309_qualify.py`, `p309_static_check.py`, `p309_env.py`,
    `p309_topology_drill.py`;
  * `make_freeze_params.py`, `p309_scan_pins.py`, `p309_placeholder_check.py`;
  * the host-control, host and static-control tests.
* **Evidence:** the drill attempt 9 evidence; the validation record; supplement 3; the P8 round 3 and round 4 records;
  the official ledgers.
* **The kept attempt-9 clone,** through read-only git only, with `GIT_OPTIONAL_LOCKS=0`:
  * `log`, `rev-parse`, `diff-tree --name-only`, `for-each-ref`, `remote -v`, `config --get`, `status --porcelain`;
  * `show` of the base ledgers, the F′ manifest and `P309_FREEZE.json`.

  Its two ledger files were read as files.
* **r1 at `4c754a73`,** through `git show`: the freeze manifest (pin records compared in memory, no hash printed),
  `P309_FREEZE.json` (key paths compared, values not printed), the scanner configuration, and the files of (b), compared
  as bytes in memory.
* **Never read:** `config/FORMAL_QUARANTINE_P309.json` and `verify/VERIFY_RESULTS_SCOPED.json`, in r1 or r2.
* **Disclosed incidentally.** Four of the 72 outside pins are paths of another cell campaign (cell-305–308, by
  name; their names were not printed).
  * Their already-recorded pin records were compared for equality in memory.
  * I did not open, read, hash or `git diff` those files, and printed no hash.

**Runs.**
* **In the real repository, read-only git only,** always with `GIT_OPTIONAL_LOCKS=0`: `rev-parse`, `log`, `diff`
  (including `diff --quiet`), `diff-tree`, `show`, `ls-tree`, `for-each-ref`, `rev-list`, `branch --show-current`,
  `check-ignore` and `status --porcelain`.
  * A `__pycache__` directory under `code/` predates this review (2026-10-01 19:06Z) and is git-ignored. It is not
    mine.
* **One scratch clone** (`--no-local --single-branch`, origin removed, the 7 inherited tags deleted in the clone). Its
  settings were:
  * `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR` in my scratchpad;
  * `PYTHONDONTWRITEBYTECODE=1`;
  * every run inside `unshare --net` (no network, including the link-local metadata address).

  In it I ran:
  * `p309_static_check.py`, `p309_scan.py`, `p309_scan_pins.py --list`;
  * `tests/test_p309_host.py`, `tests/test_p309_host_controls.py` (as root; TEST uids 64011/64012) and
    `tests/test_p309_static_controls.py`;
  * `make_freeze_params.py`;
  * the SF2 commands of §3 on TEST configurations in fresh TEST check directories, plus one official launch without
    `--print-only` that was refused at once.
* **My scratch scripts:**
  * `ctl/sf1_sim.py`, `ctl/runner_qhost.py`, `ctl/mv_mutants.py`, `ctl/t14_mutants.py`, `ctl/verify_repin3.py`,
    `ctl/verify_drill9.py`, `ctl/p8a.py`, `ctl/p8bcd.py`, `ctl/p8d2.py`;
  * `ctl/mv_mutants.py` edited `code/p309_host.py` in the scratch clone only and restored it (`git diff --quiet` in the
    clone);
  * `ctl/kod_slowfork.py`, run against HEAD's function and against a patched scratch copy (`ctl/patched/p309_host.py`);
  * `ctl/scan_left.py`.
* **TEST processes.**
  * Every process my scripts started carried my random token in argv. The runner-control's monitor child had the
    token appended (its CLI ignores trailing arguments). The committed tests' children carry their own nonces, and my
    token is in their environment (`REVIEW_TOKEN`).
  * The first slow-fork run stopped itself at its third trial. A genuine survivor of the committed function, a TEST
    child, held the driver's output pipe, so the driver's 300 s timeout fired and the controller exited before its
    cleanup.
    * That trial's leftovers, the survivor and the outside sleeper, both carried my token. Each ended with its own
      600 s sleep; I did not signal them, and my next scan found none.
    * I then gave the forkers `/dev/null` for their output and ran 20 + 20 trials. Those are the numbers in §4.
  * The controls killed survivors only by my token.
  * After every run, a scan of `/proc` argv and environments found no live process with my token or a committed TEST
    token.
  * I signalled no process I did not start.
* **Not run:** the manifest generator, any QC item, any drill, `execute`, `seal-only`, `validate-grant`. No network.

**Writes.**
* This file, not added or committed.
* My scratchpad: the ledger, scripts, outputs, scratch roots and the clone. I deleted the clone by its literal path at
  the end.
* The tools I ran wrote ledger rows and evidence only inside the scratch clone or my scratch directories.
* Nothing was written to the kept drill clone.
* No git write of any kind in `/home/user/ReBaseGuard`.

**Firewall.**
* No cell-305–309 value was read.
* No cell-307/308 campaign file was opened or hashed.
* No decoy output was opened.
* No ref under `refs/p5y-k5-cell309-p309-r1/` or `-r2/` was created anywhere, and the repository has none
  (`for-each-ref`).
