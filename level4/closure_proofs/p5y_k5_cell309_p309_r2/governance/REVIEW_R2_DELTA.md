# Independent r2 delta review (gate step 6) of P309-r2 at 447e0713
R2_DELTA_ACCEPTED

**Reviewer.** A fresh independent reviewer. I wrote none of the r2 code, the verifier author's changes, the plan, its
addenda or any earlier review, and I am not the coordinator.

**Brief.** `governance/BRIEF_R2_DELTA_REVIEW.md` (sha256 `cc583fb0…`), committed in `447e0713` before issue. I followed
it item by item (sections 2–12 below map to its items 1–10).

**State reviewed.**
* Branch `claude/p5y-k5-cell309-p309-r2`, HEAD `447e0713e5e34970570f47136e20412022a150bb`, working tree clean, range
  `c902fe2f..447e0713` (18 commits, linear).
* r1: branch `claude/p5y-k5-cell309-p309-r1` = `c902fe2f` (local and remote-tracking; the remote was not queried).
* The repository is a shallow clone; `eb9a9c22` and F `4c754a73` are reachable.

**NEW Γ309 TARGET EVALUATIONS = 0.** This review evaluated nothing, ran no `execute`, `seal-only` or `validate-grant`,
ran no QC item, created no ref in either production namespace (or anywhere in the real repository), and read no target
input.

## 1. Verdict in brief

**Accepted, with conditions.** The parts of r2 that decide whether r1's failure class is repaired, and whether the
scientific object is untouched, hold up under recomputation:
* **QC11 repair.** The sandbox base rule, the 0-record precondition, the per-mode postcondition and the
  refusal-detail table are correct, and the passing drill (`evidence/drill/20261001T171235Z`) shows QC11 passing in a
  real post-freeze topology, with both R2-M01 mutants caught for the right reason.
* **Equivalence.** I reproduced P8(a)–(d) myself: 73/73 outside-namespace pins unchanged (by git, by construction);
  12 unchanged, 7 relocation-only (reverse substitution equals F byte for byte), 20 beyond the map, 7 new; 34 remaining
  r1 tokens, exactly the listed ones; 39 frozen-parameter differences, exactly the classified ones. The exactly-once
  sites, the A38 backstop and the 13 production-read-path functions hash identically to r1's F on CPython 3.11.15.
* **Namespaces and r1.** r1's tree is `ecd1c359` at every r2 commit; no path outside FNS2 changed; no ref exists under
  `refs/p5y-k5-cell309*` or `refs/p309-test*`; both namespaces are refused everywhere the plan required.
* **Scanner, QC12, pins.** Scan PASS (34 files, 0 findings, planted controls fire), QC12 T1–T13 PASS, pins all
  current, and all 51 re-pin rows reproduce.

**But the host package (Q-HOST, gate, monitor, launcher) does not yet meet P9 and P10, and the owner decision packet
is incomplete on points that bear directly on OD-R2-4, OD-R2-5 and OD-R2-6.** None of these is exercised before the
worker steps, so none blocks acceptance of the delta. But several are real defects, each shown by a reviewer control:
* under the mandatory separate Unix user (P12), the gate and the in-run monitor are blind to a busy foreign process
  whose command line does not match a pattern (fail-open; P9 not met);
* one IMDS timeout at the runner's own preflight makes Q-HOST fail at the first later sample, consuming r2's single
  attempt, which is exactly the failure that repair 2 of `61731123` was meant to remove;
* the abort does not stop the heavy jobs "at once" (they ignore SIGTERM by design; in the worker-tier drill they are
  orphaned and keep running);
* `--host-rerun` runs QC10-class heavy work with no exclusion gate, and the runner is frozen at F, so "listed rather
  than changed now" is not an option;
* the unchanged `make_freeze_params.py` would freeze `proposed_execution_host` = the freeze host, described as "this
  isolated cloud environment", so a freeze on the AWS worker would implicitly propose it as the execution host
  (OD-R2-6).

The packet must be corrected **before** it goes to the owner (C1). The code conditions (C2–C11, C14) must be met
**before the worker-tier drill (step 8d)**, followed by a cloud-tier re-drill and a focused delta follow-up review
(P13). Everything else is before-freeze or advisory.

## 2. Integrity and r1 immutability (brief item 4)

| check | result |
|---|---|
| r1 namespace tree at each of the 18 commits `da754b8f…447e0713` | `ecd1c359ef0c3e0c9911b014b884376a10f6ed5b` at every one |
| paths outside FNS2 changed in any r2 commit | 0 (per-commit `diff-tree`); `git diff F HEAD` outside both namespaces: 0 |
| r1 branch | `c902fe2f` (local and `origin/…` tracking ref) |
| refs under `refs/p5y-k5-cell309*`, `refs/p309-test*` | 0 |
| step 3a baseline `e07e3ee8` | subtree ids of code, config, fc2, tests, verify, start_state equal F's; the 15 r1 governance files equal F's blobs at `e07e3ee8` and still at HEAD |
| r1's reviews inherited by r1 path | `make_freeze_params.INHERITED_REVIEWS` reads 12 reviews at `p5y_k5_cell309_p309_r1/reviews/…`; regeneration succeeded in my clone |
| r1-tree check in tooling | checkpoint `7d_r1_namespace_unchanged` (line 112), QC13 `r1_namespace_unchanged` (lines 287–289), self-audit A7 (`R1_TREE`), drill `host.r1_tree_unchanged` |
| preserved r2 records | `REVIEW_R2_PLAN.md` `cddfd0d0…` and `REVIEW_R2_PLAN_FOLLOWUP_1.md` `9b2ad293…` equal their `.sha256` files; both review ledgers match; only `R2_REPIN_LIST.json` was ever modified in governance/ after first add |
| official FNS2 ledger | 14 rows, all counters 0; one GOVERNANCE row per drill attempt (5) |

## 3. The binding conditions (brief item 1)

### 3.1 P1–P23 (`REVIEW_R2_PLAN.md`)

| cond. | status | evidence / gap |
|---|---|---|
| P1 authority | met | Fenced-body sha256 reproduced: msg 1 `86065859…` (12 360 B), msg 2 `77e344d7…` (1 017), msg 3 `78cd27da…` (2 038), msg 4 `de3c8e44…` (14 621), F10 convention. Carry-over completed in addendum 2 F6 and the packet. Packet wording defect: C1(d) |
| P2 literal table | met | Table + supplement (bound by sha256 `8c6e1e9a…`); P8(b)/(c) reproduce (§10). Anchors split as required. The seal-message label "formal r1" (outside the table's patterns) was renamed in `2f09500f` and disclosed in its message |
| P3 classification | met | Bindings in packet OD-R2-1b; §4.6/§4.7 rules are QC12 T11/T13 |
| P4 host package location | met, one gap | `code/p309_host.py`, `code/p309_launch.py`, all FNS2 files mode 100644, no `.sh`; docs in governance/; T7 scope extended. Addendum 1's promise to register **/proc-reading** functions (`proc_access`, `_snapshot`, `processes`, `provenance`) was not kept (A13) |
| P5 drill tool | met | No runner mode; guards (`guard_clone`); distinct name; ref-moving calls registered; confinement per call; 1 GOVERNANCE row per attempt. Stale reason text (A1) |
| P6(a) history-based base; manifest from F | met | `sandbox_base()` uses `git log HEAD -- FREEZE_RECORD_REL`; `manifest_bytes()` reads `F:` post-freeze |
| P6(b) pre/postcondition | met | 0-record precondition in `sandbox_base`; per-mode postcondition in `build_chain` (`ok`/`wrong` 1, `late_change` 2, else 0); the verifier helper has its own (construction, `build_valid`, exit) |
| P6(c) refusal detail | met | `FREEZE_RECORD_DETAIL` for F14, F16, A23, A24, A25; strings equal the driver's (lines 339, 346, 349, 351); a missing entry fails |
| P6(d) two mutants outside FNS2 | met | Built only in the drill clone, then deleted. Attempt 5: M01a rc 1 with uncaught `p309_driver.Refusal: FREEZE_RECORD: the freeze record was changed after it was made`; M01b rc 1 with `RuntimeError: QC11 harness: 2 freeze-record commits in the sandbox chain, expected 1`. Criterion weak: A2 |
| P6(e) same rule in guard and verifier helper; static ban | met | `X.sandbox_base()` in the guard harness; `sandbox_base_commit()` in `Sandbox.__init__`; T11. My mutants reverting either harness to `rev-parse HEAD` fail T11 |
| P6(f) call-closure pins | met | 13 members, every hash equal at r1 F, HEAD and config (my own closure). Constants are not pinned (A10) |
| P6(g) re-pin list on 3.11 | met | 51 rows; every `r1_at_F` and `r2` value reproduced on CPython 3.11.15; no changed config entry missing from the list |
| P7 scratch root | met | §6 |
| P8 equivalence | (a)–(d) met; (e) open | §10; P8(e) belongs to the worker freeze: C8 |
| P9 gate and isolation | **partly met** | Met: listing/hidepid/zero-visible refusals, own-cgroup exclusion, hashed recording in gate/audit/monitor rows, no git in foreign roots, unit properties set. **Not met:** refusal on an unreadable foreign /proc entry (fail-open, §7.1, C2); `systemctl show` evidence (C9); the launch record holds foreign roots and heavy patterns in clear (C9); the "TEST-named fake heavy process" control is not preserved (C11) |
| P10 Q-HOST and preflight | **partly met** | Met: refusals before attempt dir and RUN START (read and reproduced), ≤ 60 s sampling, start provenance values, argv[0] unaltered. **Not met:** static order check (C6); "at once" termination (C5); monitor liveness (C4); instance rule asymmetric (C3) |
| P11 persistence | met, one substitution | System transient unit, `--uid/--gid`, Restart=no, KillMode=control-group, MemoryMax, OOMScoreAdjust, CPU/IO weight, hermetic env, no fallback. `GIT_CONFIG_GLOBAL=/dev/null` replaced by an empty `HOME` (A6). Drill topology differs in kill behaviour (C5) |
| P12 separation | met in documents | `R2_HOST_REQUIREMENTS.md` §5, AWS instructions 8c; `isolation` checks credential, alternates, single branch. Not enforced in the launcher (A16). Feasibility gap: C1(c) |
| P13 gate order | order met; binding not satisfiable as worded | 3a → brief (`2183b8f2`) → verifier (`030b7025`) → coordinator → drills → this review. The tree-id binding conflicts with governance/ being a frozen dir: C13 |
| P14 worker drill decisive | deferred (plan) | — |
| P15 runtime pins | deferred; needs code | The manifest's `runtime` still holds python, implementation, platform, host_id only; glibc and the interpreter sha256 are not pinned at the freeze. That is a frozen-code change, so it needs a delta review and a re-drill (C14) |
| P16 allowlist | deferred (pre-freeze reviewer) | At HEAD the checker finds 0 unallowed and 80 allowed hits; the five r2 entries are file-scoped |
| P17–P22 owner decisions | in the packet | Corrections required: C1 |
| P23 governance text | met | Adopted in addendum 1 and in the frozen-parameter liabilities; the runner refuses any second attempt |

### 3.2 F1–F11 (`REVIEW_R2_PLAN_FOLLOWUP_1.md`)

| cond. | status | evidence / gap |
|---|---|---|
| F1 no production-namespace ref anywhere | met in code; spec text open | TEST-only `refs/p5y-k5-cell309-TEST-ONLY-prior/x` refused as CONSUMED (attempt 5). T12 checks both prefixes against `PRIOR_MARKER_PATTERNS[0]` and both namespaces in TestContext, the variant, the helper, QC13 and `production_tokens`. My mutants (TestContext r2-only; QC13 r2-only; narrowed pattern) each fail T12. With the r2 `TOKEN` line removed, the planted control still fires MARKER_TOKEN via `TOKEN_R1`. The governance text that adds r2's namespace to the forbidden-names rule does not exist: C12 |
| F2 subprocess only; witness; repo unchanged | met | `run_py` env: no PYTHONPATH, only INHERIT keys; `REPO == clone` asserted in each `-c` program. Witness all true in attempt 5. HEAD, refs and status sha256 unchanged in attempts 1, 3, 4, 5; attempt 2 tripped on status (coordinator write, disclosed). Dirty-tree start: A4 |
| F3 cloud-tier scope | met | 15 items (all but QC06/08/09/10), `recorded_freeze`, `mirror(F′)`, r1-tree check, provenance ×2 + continuity, preflight FAIL as expected (rc 1), 41 host tests |
| F4 rows in full | met for attempts 4, 5 | 107 and 108 rows; files equal the report's rows; sha256 `305582b5…` recomputed; counters 0; my band check: 60 drift entries, 0 hits. Attempts 2–3 hold 1 row each (disclosed). Verdict vacuity: A3 |
| F5 wording, confinement, unit names, T7 | met | Docstring wording; `confined()` per call; `p309-r2-drill-`/`p309-r2-qualify-` with `unit_name()` refusal (test L01–L03); T7 scope |
| F6 carry-over | met | Addendum 2 and packet rows complete; wording defects in C1(d) |
| F7 owner texts | mostly met | §6, §3, §8 quoted; OD-R2-1 provisional and its cost stated. Missing: unit limits and the real privilege mechanism (C1(c)); the r2 amendment of the forbidden-names rule (C12) |
| F8 step 8 order | met in documents | 8a–8d in both documents. `R2_BOOTSTRAP.md` 8a command uses the key `cell308_patterns`, which `load_config` refuses ("unknown config keys"): C15. `p309_host.py` parses with `ast.parse(feature_version=(3,6))` |
| F9 table accuracy | met | Supplement: 72 commit refs, freeze/ rule, reason corrections, 4 cross-references |
| F10 hash convention | met | Stated in addendum 2; all four hashes reproduce under it |
| F11 verifier author | met | Brief `2183b8f2` before `030b7025`. No coordinator commit touched `verify/` or `tests/test_verify_scoped.py` afterwards. Report sha256 `1ed43352…` equals its `.sha256`. Authorship is self-declared ("r1's independent verifier author"); I cannot verify it. Brief versus addendum 2 on step-3 tests: A12 |

## 4. The QC11 repair after the freeze (brief item 2)

**Base rule.** The rule is right. `sandbox_base()` (`tests/test_p309_exactly_once.py`):
* decides by history;
* takes F from the **unmodified** `D.recorded_freeze(REPO, "HEAD")`, whose refusal becomes a loud
  `RuntimeError("QC11 harness: …")`;
* refuses a base whose own history holds a record commit.

The guard harness imports the same function. The verifier author's `sandbox_base_commit()` is independent and stricter:
* it requires exactly one record commit, with a single parent, touching only the record, whose `freeze_commit` equals
  that parent;
* it then applies the 0-record precondition;
* it re-checks the record count at construction, after `build_valid` and on exit.

**Production path unchanged.** `recorded_freeze`, `check_grant`, `walk_chain`, `check_not_evaluated` and their closure
are AST-identical to r1's F (§9). The driver diff from F is three lines:
* `NS_REL`;
* `SCHEMA`;
* the seal message label.

**In the post-freeze topology** (attempt 5):
* F′ `fa65b761`, FR′ `1819aff3`, plus a checkpoint-style commit;
* witnesses: `recorded_freeze_is_F`, `one_record_commit`, `F_history_holds_no_record`; the QC11 sandbox
  `F02_grant_not_at_head` holds 1 record commit and descends from F′;
* QC11 PASS in 183 s, QC_D5 in 2 704 s, QC16 in 679 s.

**The mutants show what they must.**
* M01a, r1's base without the conditions, reproduces r1's class: an uncaught FREEZE_RECORD refusal from
  `recorded_freeze`, which r1's own QC11 record at `c902fe2f` also shows as an uncaught traceback out of
  `validate_flows`.
* M01b, r1's base with the conditions, raises the harness's own error.

## 5. Namespace prohibitions (brief item 3)

No ref under `refs/p5y-k5-cell309-p309-r1/` or `-r2/` was created anywhere I can see:
* the real repository holds none;
* the drill clone's control `no_production_namespace_ref` is true in all attempts;
* the QC11 harness's `Z_no_production_ref_anywhere` checks both namespaces in every sandbox and in the repository.

| component | how both namespaces are refused |
|---|---|
| guard `TestContext` | one `for-each-ref` over both |
| variant | `FORBIDDEN_REF_NAMESPACES` loop |
| helper | `_FORBIDDEN_REF_PREFIX` tuple in `_assert_ref` and `assert_no_production_refs` |
| QC13 | `startswith(D.G._FORBIDDEN_NAMESPACES)` |
| scanner | both tokens in `production_tokens` |
| planted control | `TOKEN` and `TOKEN_R1` |
| QC12 | T12 |

The prefix refusal in `check_not_evaluated` is shown dynamically with the TEST-only ref only, as F1 required.

## 6. Scratch-root portability (brief item 5, P7)

With `P309_SCRATCH_ROOT` unset, relative, equal to the repository or missing, every consumer refuses at import with
`HostError` or `ScratchRootError`:
* `p309_qualify`;
* `test_p309_exactly_once`, `test_p309_guard` and `test_p309_d5_exception`;
* `scoped_sandbox.scratch_sandbox_base()`.

`test_p309_site_backstop` refuses through its import of `test_p309_exactly_once`. I ran these imports in my scratch
clone.

Other P7 points:
* a set-but-empty `P309_FOREIGN_ROOTS` is refused (S06);
* an official launch requires an empty root (S08 and `launch.py` line 112);
* the launcher and the drill set `TMPDIR` under the root;
* no session path remains in code, tests or `verify/*.py` (grep).

## 7. Host package, Q-HOST, launcher (brief item 6)

### 7.1 Exclusion gate and monitor versus owner message 3

**The start gate.** `gate_checks` refuses on any of these:
* a foreign process above 0.05 of a core, newly appeared, or matching a heavy pattern;
* any other ReBaseGuard process above 0.05;
* load above the baseline plus 0.5;
* low RAM or disk;
* unreadable /proc, `hidepid`, or no visible foreign process.

That is a faithful strict reading of message 3 §4.

**The in-run monitor.** `monitor_verdict` fails only on:
* a broken continuity check;
* a foreign or other-ReBaseGuard process above `monitor_heavy_cpu_fraction` (0.5), per process, not aggregated;
* a configured heavy pattern.

A newly seen process is judged one sample later. As a reading of §3 ("a cell-308 heavy job") this is defensible, but
the threshold, the per-process rule and the one-sample grace together define when OD-R2-5 (i) consumes r2's attempt.
The packet does not state them (C1(b)). Several cell-308 workers each below 0.5 of a core are invisible to it (A8).

**Fail-open under the mandatory separate user (P9, P12).**
* `_snapshot` reads `/proc/<pid>/cwd` and silently uses `""` when the readlink fails (`p309_host.py` lines 302–305).
  For another user's process it always fails without privilege.
* `classify` then sees the command line only (lines 311–319). A non-matching process is dropped entirely: it is
  neither foreign nor counted.
* **Reviewer control** (`ctl/control_p9*.py`). Two TEST busy processes, with cwd in a mode-700 TEST "foreign root":
  * as root, both are tagged `foreign` (one through its cwd);
  * as uid 65534 (via `setpriv`), the one whose `argv[0]` does not match the pattern is **untagged**, so it is invisible
    to `gate_checks` and to `monitor_verdict`;
  * `proc_access` still reports `readable: true`, so P9's "refuse on an unreadable /proc entry of a foreign process"
    never fires.
* At the start the load-average check is a backstop. During the run there is none.
* Mid-run detection of cell-308 heavy work therefore depends entirely on `foreign_heavy_patterns` supplied by the
  cell-308 operator (default `[]`) or on matching command-line text (C2).

**Recording.**
* Gate, audit and monitor rows hold only pid, uid, tag, CPU fraction, command-line sha256 and a heavy flag.
* The foreign root is only `stat()`ed and `access()`ed, hashed with mode, uid and gid.
* git runs only in the P309 repository. In `isolation()`, however, the git reads run before the
  disjointness check, so a misconfigured `p309_repo` pointing at a foreign root would get git run there first (A16).
* **The launch record, however, stores `host_config` in clear** (`launch.py` line 118): the foreign root paths and
  `foreign_heavy_patterns`. Its `argv` repeats the paths (`InaccessiblePaths=-…`, `--setenv=P309_FOREIGN_ROOTS=…`).
  This contradicts `R2_AWS_SESSION_INSTRUCTIONS.md` §3.1 ("matched in memory only and never recorded") and P9.
* Conversely, the start-gate, isolation and preflight results live only in that record under the scratch root. The
  attempt keeps just its path (`QHOST_BASELINE.json`), so the plan's "the gate's JSON output is preserved with the
  run" is not met for the official run (C9).

**The only signal.** In the host package, the one signal is `os.kill(parent, SIGTERM)` (line 597). A reviewer control
(`ctl/control_monitor.py`) shows one FAIL row, exactly one SIGTERM to the parent, and no signal to the busy process.

The runner also terminates and kills its own monitor child (`p309_qualify.py` lines 433–437). That is P309-internal.
The scanner does not flag `os.kill` or `killpg` at all, so this property rests on review (A7).

### 7.2 Q-HOST continuity: the instance-unverified rule is asymmetric (C3)

`continuity()` (lines 243–246) passes a sample **without** an instance id if boot, machine-id and hostname are
unchanged. That was repair 2 of `61731123`, tested by C05.

But `qhost_preflight` takes the run's baseline from a fresh `provenance()` (line 389). The run's preflight check is
against the launch record, and that check passes through the same fallback. So if IMDS times out at that moment:
* the baseline has no instance id;
* every later sample that reads IMDS successfully fails `same_instance`, because `None == "<id>"` is false and the
  fallback requires the **sample** to lack the id.

Reviewer computation with the committed function: `continuity(base without id, sample with id)` → `pass: False`. In
the official run, that means a SIGTERM at the first monitor sample after RUN START, and a consumed attempt.

### 7.3 Termination: not "at once" (P10, C5)

On Q-HOST FAIL, `_qhost_abort` writes `QHOST_FAIL.json` and the failed summary, then calls `os._exit(3)` (line 413).
It does not touch its children. The heavy decoy jobs are started by `_spawn_job` with SIGINT, SIGTERM, SIGHUP and
SIGQUIT **ignored** (driver line 960).
* **Official run.** The runner is the unit's main process. When it exits, systemd sends SIGTERM (ignored) and SIGKILL
  only after `TimeoutStopSec`, which defaults to 90 s; the unit sets neither that nor `KillSignal`.
* **Worker-tier drill.** The unit's main process is the drill. The runner is its child (`run_py`), so on abort the
  runner's job tree is orphaned and keeps running while the drill goes on to the witness, the host functions and the
  controls (two more QC11 runs). Only when the drill exits does the unit stop.

Both contradict P10's "terminates its own heavy process tree at once" and message 3 §3.

### 7.4 Monitor liveness (C4)

`stop_qhost_monitor` passes Q-HOST if at least one row exists and every row passed (line 439). It does not check that
the monitor was still alive, nor the gaps between samples. `qhost_monitor` has no exception handling, so a monitor
that dies after its first sample leaves a silent gap and a PASS.

### 7.5 Runner ordering and refusals

**Order, from reading `main()`.**
1. `recorded_freeze`.
2. Manifest `--check`.
3. Dirty-tree check.
4. `QDIR.mkdir`, which creates no attempt directory.
5. Attempt-exists check.
6. `qhost_preflight` (line 543).
7. `os.mkdir(attempt_1)` (line 548), then RUN START (line 549).

**Reviewer controls.** I called the committed `qhost_preflight` in my clone with each of these, and each was refused
with no attempt directory created:
* no launch record;
* a record with blockers;
* a drill record outside a drill clone;
* a valid official record outside a systemd unit.

**But no static check asserts this order**, which P10 and addendum 1 require (C6).

**`--host-rerun`** (`host_rerun`, line 485) has no launcher, gate, isolation, preflight or monitor, and runs two
Stage-1a decoys. The runner is frozen at F, so this cannot wait for "the later grant window" (implementation report
§6) (C7).

### 7.6 Launcher

**What holds.**
* Unit names are fixed by mode and refused across modes.
* The properties are set as listed in P11 (and P9: `ProtectSystem=strict`, `ReadWritePaths` = repository and scratch,
  `PrivateTmp`, `NoNewPrivileges`, `InaccessiblePaths`).
* The environment is hermetic.
* The record is written exclusively before the start.
* There is a single `systemd-run`, never retried.
* A loaded `p309-r2-*` unit blocks a new launch. Without `--collect`, a failed unit also blocks a re-launch until it
  is cleared, which errs on the safe side.

**Privilege.** `main()` calls `systemd-run` itself, not through `sudo`. So:
* only a polkit rule for the P309 user works;
* run as root, `isolation`'s `foreign_roots_unreadable` uses root's `access()` and fails;
* `isolation` runs in the launcher, outside the unit, so `InaccessiblePaths` cannot make a world-readable cell-308
  checkout "unreadable".

The documents offer "sudo or polkit", and OD-R2-4 does not mention the second point (C1(c)).

### 7.7 Frozen texts that r2 left unchanged but that are now wrong (C8)

* `make_freeze_params.py` line 349: `qualification_rule` = "… gates Q01-Q17, Q-U2, Q-D5". It omits Q-HOST, which the
  runner adds as a gate.
* Line 361: `proposed_execution_host` = {"this isolated cloud environment (rev. 2c A14)", `G.host_id()` of the freeze
  host}.
  * P8(d) shows no difference only because the drill ran in the same cloud container as r1's freeze: my
    regeneration at HEAD gives the identical `host_id_sha256`.
  * At the worker freeze, both the host id and the truth of the text change.
  * The field would name the shared worker as the proposed execution host. Message 4 says that must not follow
    automatically from qualification-host approval.

## 8. The drill and its evidence (brief items 6 and 9)

| attempt | clone base | outcome in the report | diagnosis and fix (verified against the evidence) |
|---|---|---|---|
| 1 `132113Z` | `e362c3de` | FAIL before F′ | The checker refused marker words in r2's own governance texts (error text in the report). Fix `4abc7073`: five file-scoped allowlist entries (P16 reviewer to confirm) |
| 2 `132325Z` | `4abc7073` | FAIL (items) | QC16 FAIL: `-I` dropped tests/ from `sys.path`. All items "not confined": a parse bug, re-checked clean (not re-checkable now; later attempts confined). Status sha changed: the coordinator wrote `R2_REPIN_LIST.json` mid-drill (disclosed). Fixes `a39ec7c3` |
| 3 `143415Z` | `a39ec7c3` | PASS, but defective | Ledger export holds 1 row: the second-record control's `reset --hard` discarded them. The drill's own ledger verdict still passed (A3). Fix `93b41bd9`: `reset --mixed`, record restore, survival control |
| 4 `160409Z` | `93b41bd9` | PASS | 107 rows; survival control true |
| 5 `171235Z` | `61731123` | PASS | 108 rows; 41 host tests; every control caught; P309 state unchanged |

**Integrity of the evidence.**
* Each report's sha256 equals the one in its official ledger row.
* Each evidence file was added once and never modified.
* Message 4 was recorded after attempt 4 ended (17:07:39 → `7ed74347` at 17:09:09).
* `61731123` (17:12:27) preceded attempt 5 (17:12:35).
* Nothing was written to the repository during attempts 4 and 5 (status sha unchanged).

**Final bytes.** `447e0713` changes only governance/, evidence/ and the ledger relative to the drilled `61731123`.
Code, config, tests and verify are identical.

**Never run anywhere.** The worker tier: the runner's `main()` with Q-HOST, the monitor inside a unit, and the
launcher's start path. This is disclosed. The development controls that the report cites for P9, P10 and P11 are not
preserved in the ledger or evidence (C11):
* the planted busy fake cell-308 process;
* the three preflight refusals;
* `--print-only` in a container.

## 9. Scanner, QC12, pins (brief item 7)

**Scanner, in my clone at HEAD.**
* `p309_scan.py`: PASS, 34 files scanned (every FNS2 `.py`, including the 4 new), 0 findings, 73 listed suppressions.
* Planted controls fire all kinds.
* `p309_scan_pins.py --list`: all current.

**New registrations, each with a reason.**
* git runners: `p309_host.git_read`, the drill's `git` and `run_py`.
* reviewed functions: 9.
* ref-mutation functions: 4. `system_reads` is one only because `version` is not a read verb.
* verb options: `reset --mixed`, `clone -q --single-branch --branch`, `version`.
* imports: `p309_host`, `urllib`, `urllib.request`, `p309_qualify` for the drill's `-c` programs only; tests
  `p309_host`, `p309_launch`.

One reason is stale (A1).

**QC12.** T1–T13 PASS.

**Negative controls.** None is committed for T11–T13 (C10). My scratch mutants were each caught:
* QC11 harness to `HEAD`: T11 FAIL;
* guard harness to `HEAD`: T11 FAIL;
* TestContext r2-only: T12 FAIL;
* QC13 r2-only: T12 FAIL;
* `PRIOR_MARKER_PATTERNS[0]` narrowed: T12 FAIL;
* `_only` body changed: T13 FAIL.

A changed guard function is (correctly) outside the closure, which has no guard members.

**`R2_REPIN_LIST.json`, row by row.** All 51 rows reproduce with `sha256(ast.dump(node))` on CPython 3.11.15, against
r1's config at F and r2's at HEAD:
* 25 re-pinned: 10 ref-mutation, 7 reviewed, 7 t7 and 1 module exemption (`r1_at_F` = my F value; `r2` = my HEAD
  value = config);
* 26 new: 13 read-path, 9 reviewed and 4 ref-mutation.

The exactly-once sites (`1ee764b7…`, `13ee3ec3…`) and the backstop pins (`c8a2fb51…`, `80d206ad…`, `23f3021d…`,
`696a6102…`) are equal at F, at HEAD and in both configs.

**`production_read_path_pins`.** My independent closure from the four starts gives the same 13 members at F and at
HEAD, every hash equal to the config. The members are:
* `ExecContext` and `Refusal`;
* `_chain_kind` and `_only`;
* `check_grant`, `check_not_evaluated` and `freeze_commit`;
* `git`, `git_dir` and `sha`;
* `recorded_freeze`, `verdict_ok` and `walk_chain`.

Of the 19 module-level constants they read, only `NS_REL` differs, by the relocation.

## 10. Equivalence P8(a)–(d) and the scientific object (brief item 8)

* **(a)** I did not run the manifest generator. It hashes four cell-307 campaign files and the C_308 stream files,
  which my brief forbids.
  * By construction instead: the generator's out-of-namespace pin list is literal and unchanged (only `NS_REL`
    differs); the candidate manifest is unchanged.
  * For each of the 73 outside pin paths, `git diff --quiet F 447e0713 -- <path>` succeeds, so the pins equal F's.
* **(b)** Reverse substitution of the declared map over code, config, fc2, tests, verify and start_state gives
  12 / 7 / 20 / 7 / 0 removed. That is the identical file lists to `R2_EQUIVALENCE_P8_FINAL.json`.
* **(c)** My scan for `p309[_-]r1|cell309-p309-r1|<r1 branch>` finds 34 occurrences, the same (file, line) set.
* **(d)** I regenerated `P309_FREEZE.json` at HEAD bytes in my clone and diffed it key by key against F's. There are
  39 differences, the same set as the classified list.
  * These are equal to r1: `route`, `cell`, `detector`, `m`, `closure_criterion`, `scope`, `outcome_table`, `stage1a`,
    `stage1b`, `stage2`, `u2`, `efficacy`, `independence_statement`, `qualification_rule` and
    `post_grant_derivations`.
  * The two problems with "equal" texts are in §7.7 and C8.

**No scientific behaviour or parameter changed.**
* The driver changes only `NS_REL`, `SCHEMA` and the seal message label. The guard changes only the names and the
  TestContext refusal. The research namespace is unchanged since `eb9a9c22`.
* The SRK route, supplies, closure criterion, Γ309, the cell interval (a post-grant derivation, unchanged), budgets,
  workers (`WORKERS = 4`; the launcher fixes `--workers 4`), the outcome table and Stage 1a, 1b and 2 are equal.
* So are the exactly-once sites and the A38 backstop.
* The variant's diff is confined to the name constants and `_validated_sandbox`. Its `verifier_id` changes with its
  sha256 (`e82d6812…`), as classified.
* I did not open `VERIFY_RESULTS_SCOPED.json`. For "verdicts identical" I rely on the verifier author's report.

## 11. Disclosures (brief item 9)

| disclosure | assessment |
|---|---|
| Mid-drill write (attempt 2) | Confirmed by the report's status sha change; HEAD and refs equal |
| Pushes not through the checkpoint tool | Consistent: no `ledger/CHECKPOINT_PUSHES.jsonl` exists; namespace-only holds by my check (A11) |
| Seal-message label | Changed in `2f09500f` and disclosed in its message; outside the table's patterns |
| Self-audit A3 put message 4 in its own file | Correct consequence of A3's IMMUTABLE list. The packet's "appended later" is wrong (C1(d)) |
| Open items in the report | Worker tier untested: accepted, as it is gated at 8d. Linear history: accepted under P13. QC_D5 duration: accepted. "`--host-rerun` … listed rather than changed now" is **not** acceptable, because the runner is frozen at F (C7) |

## 12. Implicit owner decisions (brief item 10)

Beyond the disclosed provisional OD-R2-1(b), I found **no decision taken outright**. Three choices in the bytes would
pre-empt or shape owner decisions unless disclosed and corrected:
* **OD-R2-6.** The frozen `proposed_execution_host` follows the freeze host by default (§7.7). Neither `execute` nor
  `--host-rerun` has any cross-campaign gate or launcher mode. The packet discloses neither.
* **OD-R2-5.** Option (i) is implemented, as the packet says. But the operational meaning of "heavy" is not presented:
  * 0.5 of a core per process;
  * one-sample grace;
  * visibility limited to command lines under a separate user;
  * up to 90 s or more of continued heavy work after a trigger.
* **OD-R2-4.** The launcher's privilege model (polkit, not sudo) and the dependence of `isolation` on the cell-308
  checkout being non-world-readable decide part of what the owner and the cell-308 operator would be consenting to.
  "The unit limits" (P20) are missing from the packet's list.

## Conditions

**C1 — blocking-before-owner-decisions.** Correct `OWNER_DECISION_PACKET_R2.md` before it is put to the owner:
* **(a) OD-R2-6.** State that, as the bytes stand:
  * the frozen `proposed_execution_host` is "this isolated cloud environment (rev. 2c A14)" with the freeze host's id,
    so a freeze on the AWS worker would propose that worker;
  * `execute` and `--host-rerun` have no exclusion gate, launcher mode or Q-HOST.

  Put OD-R2-6 to the owner with these consequences stated. That includes whether the frozen field may name any host
  before OD-R2-6 is answered.
* **(b) OD-R2-5.** State the start-gate and in-run definitions of "heavy" (0.05 versus 0.5 of a core per process,
  patterns, one-sample grace). State the separate-user visibility limit (cell-308 processes recognisable only by
  command line, so the cell-308 operator must supply job patterns). State the termination latency (§7.3).
* **(c) OD-R2-4.** Add:
  * the unit limits (MemoryMax, OOMScoreAdjust, CPUWeight, IOWeight; P20);
  * that the launcher needs a polkit rule for the P309 user (a sudo rule is not used by the code);
  * that `isolation` requires the cell-308 checkout to be unreadable by permissions outside the unit, so a
    world-readable checkout would need the §6 amendment.
* **(d) OD-R2-0.** (A): message 4 is in its own file, not appended. (D): separate the freeze/qualification host
  (OD-R2-3/4) from the execution host (OD-R2-6) in the proposed authorization text.

**C2 — before-freeze; before step 8d.** P9 fail-open. A foreign-uid process whose cwd cannot be read must not be
silently dropped. Classify by a configured cell-308 uid, refuse at the gate and count it in the monitor, or otherwise
make it visible. Commit a control reproducing mine: a TEST busy process, cwd under a TEST foreign root, non-matching
command line, observed from another uid. It must block both the gate and the monitor.

**C3 — before-freeze; before step 8d.** Make the instance rule symmetric. `qhost_preflight` must refuse, before the
attempt directory, if its baseline lacks an instance id that the launch record had, or the monitor must compare
against the launch record's id. Add the test "baseline without id, sample with id".

**C4 — before-freeze; before step 8d.** Q-HOST must FAIL if the monitor exited before `stop_qhost_monitor`, or if any
gap between start, samples and stop exceeds the interval plus a stated tolerance. Add tests.

**C5 — before-freeze; before step 8d.** Make termination immediate in both topologies, for example:
* `TimeoutStopSec`/`KillSignal` on the unit, since the jobs ignore SIGTERM;
* in the worker-tier drill, killing the runner's process tree (or stopping the drill) on a runner abort.

Show it in the worker-tier drill evidence.

**C6 — before-freeze.** Add the P10 static check: in `main()`, `qhost_preflight` and every refusal return precede
`os.mkdir(attempt_1)` and the RUN START log. Add a negative control.

**C7 — before-freeze.** Put `--host-rerun` under the launcher, the exclusion gate and Q-HOST, or make it refuse
outside a valid launch record. Settle in the frozen tree how `execute` would be gated on a shared host, if OD-R2-6
names one.

**C8 — before-freeze.**
* `qualification_rule` must name Q-HOST.
* `proposed_execution_host` must follow the owner's OD-R2-6 answer, with accurate text.
* Refresh P8(d)'s expected-difference list for the worker freeze, and produce P8(e) (runtime and host differences)
  there.

**C9 — before-freeze; before step 8d.** The official run must preserve its start evidence in the attempt: gate,
isolation, preflight, the host configuration, and `systemctl show` of the effective unit properties (P9), hash-bound.
Foreign root paths and `foreign_heavy_patterns` may appear only as sha256 in any record, including the launch record.

**C10 — before-freeze.** Commit negative controls for QC12 T11–T13, as the D5 tests do for T4/T6/T7/T8.

**C11 — before-freeze; before step 8d.** Commit, as reproducible tests with ledger rows, the P9/P10/P11 controls the
implementation report cites:
* a TEST-named busy process through the real `/proc` path;
* the preflight refusals;
* the launcher's refusals (including `--print-only` blocked without systemd);
* the monitor FAIL → SIGTERM path.

**C12 — before-freeze.** Create the r2 amendments record that `R2_LITERAL_DISPOSITION.json` cites
(`P309_R2_AMENDMENTS`) and that addendum 2 F7 requires. It must name r2's production names and add r2's namespace to
the FC2 forbidden-names rule, keeping r1's. The inherited `fc2/FC2_SPEC_R2.md` names only r1's.

**C13 — before-freeze.** Restate P13's tree binding mechanically, since governance/ is a frozen directory:
* the code, config, fc2, tests and verify tree ids at F equal those drilled and reviewed;
* governance/ may differ only by listed, reviewed additions.

Today the reviewed tree (`447e0713`) already differs from the drilled one (`61731123`) in governance/. Nothing may be
added to any frozen directory after F; post-freeze reviews go to `reviews/` (`QREVIEW_PREFIX`).

**C14 — before-freeze.** P15 needs code: pin glibc and the interpreter's sha256 in the freeze manifest's runtime, and
check them where the runtime is checked. This is a frozen-code change, so it needs a delta review and a re-drill.

**C15 — before-freeze; before step 8a.** Fix `R2_BOOTSTRAP.md` 8a: `cell308_patterns` is refused by `load_config`. Use
`foreign_patterns` / `foreign_heavy_patterns`, as in the AWS instructions.

**After C2–C11 and C14:** a cloud-tier re-drill and a focused follow-up of this review before step 8d (P13).

**Advisory:**
* **A1.** The `ref_mutation_functions` reason for the drill's `controls` still says "reset --hard back"; the code uses
  `--mixed`.
* **A2.** Tighten R2-M01a's "caught" test from the substring `FREEZE_RECORD` plus a nonzero rc to the uncaught
  `p309_driver.Refusal: FREEZE_RECORD` line, or the failing flow names.
* **A3.** The drill's ledger verdict should check completeness (a RUN START row, and rows from each item script).
  Attempt 3 passed with 1 row.
* **A4.** The drill should refuse a dirty P309 working tree; it imports `p309_host` and `p309_env` from it.
* **A5.** Add `BRIEF_R2_DELTA_REVIEW.md`, the `.sha256` files and this review (with its ledger) to self-audit A3's
  IMMUTABLE list.
* **A6.** Set `GIT_CONFIG_GLOBAL=/dev/null` explicitly, as P11 says.
* **A7.** The scanner does not flag `os.kill`, `killpg` or `send_signal`. Pin or register `qhost_monitor` and
  `stop_qhost_monitor`.
* **A8.** Consider an aggregate foreign-CPU criterion in the monitor.
* **A9.** Record in the 8a audit whether the cell-308 checkout is world-readable (a boolean), not only inside
  `meta_sha256`.
* **A10.** T13 pins functions, not the module constants they read. All 19 equal r1's except `NS_REL`.
* **A11.** Push through `code/checkpoint_push_p309.py` from now on.
* **A12.** The verifier brief directed step-3 tests, against addendum 2 step 3a. The author ran them only in a scratch
  clone and disclosed it. Record the deviation.
* **A13.** Register the /proc-reading functions, as addendum 1 P4 promised.
* **A14.** governance/ is scanned by `code/p309_placeholder_check.py` at the freeze. This review avoids its marker and
  choice phrases, so that it adds no allowlist entry.
* **A15.** Take a final provenance sample at stop, so the end values are recorded rather than implied.
* **A16.** The launcher should refuse `unit_user` = root and check it against the foreign roots' owners. `isolation()`
  should refuse before any git call if `p309_repo` overlaps a foreign root. `loaded_p309_units` should treat a failing
  `systemctl` as a blocker.

## Disclosure (reads, runs, writes)

**Execution ledger.** `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r2_delta_review/LEDGER.jsonl`,
one JSON row per command or command group. Rows marked `retrospective` record read-only command groups that I logged
after running them. Every row has `target_evaluations: 0`.

**Reads.**
* FNS2 governance in full:
  * the brief, the plan, both addenda and both reviews;
  * owner messages 1–4, the implementation report, the packet;
  * the AWS instructions, `R2_BOOTSTRAP.md`, `R2_HOST_REQUIREMENTS.md`.
* JSON summaries of the re-pin list, the P8 file and the literal supplement.
* FNS2 code, tests and verify, in full or in the cited sections. Diffs of every operative file against r1 at F.
* The verifier author's report (first 120 lines).
* All five drill reports and drill ledgers, as committed evidence.
* r1 at `F`/`c902fe2f`, through `git show`:
  * the config;
  * `P309_FREEZE.json`;
  * the manifest's structure and pin **paths** (no pin hash printed);
  * `qualification/attempt_1/QC11.json`, the harness output;
  * names under `reviews/`.

**Runs.**
* Read-only git in the real repository only: `log`, `show`, `diff`, `diff-tree`, `rev-parse`, `ls-tree`,
  `for-each-ref`, `merge-base`, `cat-file -e`, `grep`, `status`. Also `sha256sum`.
* One scratch clone (`--single-branch`, origin removed, only `refs/heads/<r2 branch>` plus tags; deleted by its
  literal path at the end). With `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR` in my scratchpad and
  `PYTHONDONTWRITEBYTECODE=1`, I ran there:
  * `p309_static_check.py`, `p309_scan.py` and `p309_scan_pins.py --list`;
  * `tests/test_p309_host.py`;
  * `p309_placeholder_check.run()`, as a function only;
  * `make_freeze_params.py`, which reads FNS2 docs, r1 reviews and research protocol docs, and no cell-307/308 file;
  * import-refusal checks;
  * `qhost_preflight` and `continuity` calls;
  * a scanner run on a copy with the r2 planted token removed.
* My scratch scripts (`recompute_pins.py`, `recompute_p8bc.py`, `negctl.py`, `ctl/*.py`). The controls started TEST
  busy python processes with cwd under a TEST directory, and ran the committed host code as root and as uid 65534
  (`setpriv`); the processes were then killed.
* No manifest generator, no QC item, no drill, no `execute`, `seal-only` or `validate-grant`, no network.

**Writes.**
* This file (not committed).
* My scratchpad: the ledger, scripts, outputs, test launch records, and a clone that has since been deleted.
* The tools I ran appended ledger rows and evidence only inside the scratch clone or the scratch evidence directory.
* No git write of any kind in `/home/user/ReBaseGuard`. Its HEAD is still `447e0713` and its status was clean before
  this file was written.

**Firewall.**
* No cell-305–309 value was read.
* No cell-307 or cell-308 campaign file was opened or hashed. I saw their pin paths by name only, and compared them by
  `git diff --quiet` only.
* No decoy output was opened, including `VERIFY_RESULTS_SCOPED.json`.
* No ref under either production namespace was created, armed or consumed.
* The retired worker was not contacted.
