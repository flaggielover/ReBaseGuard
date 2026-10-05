# Independent delta review: r2 adoption candidate (qualification-runtime hardening + F-DRILL-ORDER)

* **Reviewer:** an independent subagent. It did not write the change. It verified claims by reading the code and running static checks. Commit-message claims were not trusted.
* **Base:** `101ef2cb17e5eab2892212178278da45b98004ed` (origin/claude/p5y-k5-cell309-p309-r2)
* **Candidate:** `93d550638b8c79ae1c252fc6c2b0194b1a416b49` (claude/p309-r2-adoption-candidate-20261005), tree `3b2f12f54bf9dba2961865f419a46caa19ffecdb`
* **Hardening source compared:** `3c191ac2` (parent `b609549c`, which descends from `101ef2cb`)
* **Namespace:** `level4/closure_proofs/p5y_k5_cell309_p309_r2/` ("r2 namespace" below; paths are relative to it unless they are absolute)
* **Evidence read:** `/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t3/ev/{MATRIX_CANDIDATE,MATRIX_BASELINE,UNIT_CANDIDATE,UNIT_BASELINE,REG_CANDIDATE,F_DRILL_ORDER_DEMO}.json`
* **Reviewer tooling:** helpers under `.../scratchpad/t3/review/` (`pins.py`, `anchors.py`, `ledgers.py`, `matrix.py`). One scratch clone `.../t3/review/cand` was made at the candidate commit and deleted after use. Nothing was run, edited or committed in `/home/user/ReBaseGuard`; it was read only with `git show` / `diff` / `ls-tree` / `rev-parse`. No runner, launcher, host, drill, driver or target evaluator was run or imported by the reviewer.

## Answers

| # | Question | Answer |
|---|---|---|
| 1 | Hardening limited to qualification infrastructure? | **YES** |
| 2 | Scientific algorithms and target logic unchanged? | **YES** |
| 3 | Gate semantics unchanged except durability / exactly-once enforcement? | **PARTLY**: gate logic and verdicts are unchanged. There are also new pre-launch refusals, a new attempt file, a new summary key, and new failure points after RUN START (see Q3) |
| 4 | All pins preserved, or intentionally re-pinned with evidence? | **YES**: one intentional re-pin (`make_topology`). The governance re-pin record is missing (should-fix) |
| 5 | Does T14a pass? | **YES** |
| 6 | Does QC15/A7 pass? | **YES** (computed statically) |
| 7 | F-DRILL-ORDER fixed correctly? | **YES**: correct and sufficient for the manifest check |
| 8 | Does the crash matrix discriminate baseline from candidate? | **YES** for the cases that matter (C04, C05, C12, S04–S06, fsync counts, units T03–T08). C06/C07 are vacuous for the baseline, and the matrix cannot test power loss |
| 9 | Is the branch clean enough to propose for adoption? | **PARTLY**: the commit is clean. Adoption still needs the re-pin record, a formal r2 delta follow-up review, and a filesystem-capability precondition |

## Per-question evidence

### Q1. Is the hardening limited to qualification infrastructure? YES

`git diff --stat 101ef2cb 93d55063` shows exactly three paths, all in the r2 namespace: `code/p309_qualify.py` (+146/−5), `code/p309_topology_drill.py` (+2/−2) and `config/SCANNER_ALLOWANCE_P309.json` (+1/−1). `p309_qualify.py` is the qualification runner. `p309_topology_drill.py` is development-only drill tooling. The allowance change is a single pin.

### Q2. Are scientific algorithms and target logic unchanged? YES

* No other file changed (see Q1). The driver, guard, generators, verifiers, tests, research code and data are byte-identical.
* I diffed the top-level AST of `p309_qualify.py` between the base and the candidate (`review/pins.py`):
  * **Changed:** `xwrite`, `run_item`, `_qhost_abort`, `host_rerun`, `main`.
  * **Added:** `_fsync_dir`, `_fsync_path`, `sync_ledgers`, `_ledger_problems`, `prelaunch_state`, `attempt_start`.
  * **AST-identical:** every gate function (`qc05`, `qc06`, `qc07`, `qc08`, `qc09`, `qc10`, `qc13`, `qc16`, `qc17`, `qc_u2`, `qc_d5`, `qc_formal`, `qc_research_simple`, `research_test`, `decoy_stage1a`, `single_run_since_freeze`, `ledger_append_only`), `items_table` (the gate lambda table), `mirror`, `run`, `git`, `qhost_preflight`, `start_qhost_monitor`, `stop_qhost_monitor`, and all module constants.
* `run_item` (`p309_qualify.py:625-637`): the only change is one `sync_ledgers()` call after the record `xwrite`. The result dict, the exception-to-FAIL handling and the record content are unchanged.
* `p309_topology_drill.py`: only `make_topology` changed. The change swaps two list elements (lines 218-219).
* The candidate runner is AST-identical to `3c191ac2`. It differs in bytes only on line 753: the comment `# exclusive: of two racing runners exactly one passes` becomes `# exclusive` (`git diff 3c191ac2 93d55063`).

### Q3. Are gate semantics unchanged except for durability / exactly-once enforcement? PARTLY

Gate pass/fail logic is unchanged: `items_table`, every gate function, the `gates` dict and the `pass` formula in `main` are unchanged. The behaviour changes beyond plain durability are:

1. **New pre-launch refusal H3 in `main`** (`:743-746`). It runs after the "attempt already exists" check and after `QDIR.mkdir(exist_ok=True)`. It runs **before** `qhost_preflight`, the `os.mkdir(attempt_1)` and RUN START. It refuses on:
   * any entry in `qualification/` (allowed set `()`);
   * a torn or unparseable ledger row, or a ledger without a trailing newline;
   * a **nonzero target counter** in either ledger. This is new and goes beyond exactly-once, but it is still a refusal before launch;
   * a `QUALIFICATION RUN START` row at or after the freeze-record commit time (an orphan RUN START).

   The orphan rule matches `single_run_since_freeze` (QC13, `:407`). A run in that state would fail QC13 anyway, so refusing up front only avoids an attempt that is bound to fail.
2. **New pre-launch refusal H3 in `host_rerun`** (`:664-673`). It runs before `qhost_preflight`, the mkdir and HOST RERUN START. It refuses on dot entries in `qualification/` and `qualification/host_rerun/`, on ledger problems, and on a prior `HOST RERUN START <host16>` row after the freeze record.
3. **Placement:** every new `return 2` is before the attempt mkdir. QC12 T14 on the candidate gives, for both `main` and `host_rerun`, `refusal_returns_before_mkdir`, `start_logged_right_after_mkdir`, `no_raise_or_exit_after_mkdir`, `preflight_before_mkdir` and `monitor_starts_before_work` all **true** (`p309_static_check.py`, run in the scratch clone, exit 0).
4. **New statements after RUN START that can raise** (not refusals, but new crash points):
   * `_fsync_dir(QDIR)`, `sync_ledgers()`, `xwrite(ATTEMPT_START.json)` (which needs `os.link`), and `_fsync_dir(attempt_1)` at `:758-762`;
   * the matching statements in `host_rerun` (`:685-689`);
   * `sync_ledgers()` in `run_item`, outside its try.

   On a filesystem without hard-link support, or where `fsync` on an `O_DIRECTORY` fd fails, the single qualification attempt would be used up right after RUN START. See finding S1.
5. **New evidence file** `attempt_1/ATTEMPT_START.json`: boot_id, pid, runner sha256, unit, mode and the launch-record sha256. The driver's `walk_chain` admits it because the qualification commit is checked by the `qualification/` prefix only (`p309_driver.py:553-556`).
6. **New key in the completion marker:** `attempt_files_sha256` (`:780-781`), with the schema label still `P309_QUALIFICATION/2`. The driver reads only `pass` and `freeze_commit` (`p309_driver.py:558-560`), and no other code, test or verifier consumer exists (grep).
7. **Refusal text change:** the "attempt already exists" message gains "classify it read-only with the status validator". No test matches that text (grep). The status validator is not in the r2 tree (finding N3).
8. **`_qhost_abort`:** one added `sync_ledgers()` inside the `try`, so `os._exit(3)` in the `finally` still runs. Abort classification is unchanged (matrix C13 gives ABORTED in both).
9. **`xwrite`** keeps "never overwrite": O_EXCL on the temporary file, and `os.link` fails with FileExistsError if the final name exists. It now also fsyncs the file and the directory and loops on short writes. The pinned callers (`start_qhost_monitor`) are AST-unchanged, but the writes they make are now durable.

### Q4. Are all pins preserved, or intentionally re-pinned with evidence? YES (one intentional re-pin; governance record missing)

* **Allowance JSON:** 1228 leaves in both versions. One leaf differs: `/ref_mutation_functions[20]/ast_sha256` changes from `9b59c12f…` to `8af1bb7836674141f69a53175b094eb31092d55462bfb1b9ba2c27a0dc8dc575` (file `code/p309_topology_drill.py`, function `make_topology`). Allowance sha256 changes from `57cc9a22…` to `f1780a91…`.
* **Pins on the changed files**, recomputed at the candidate as sha256(ast.dump) of the unique outermost function, the same rule as `p309_scan_pins.owner_hash`:

| list | file | function | pin | candidate | base | state |
|---|---|---|---|---|---|---|
| reviewed_functions | p309_qualify.py | git | cd913a267901… | = | = | MATCH, unchanged |
| reviewed_functions | p309_qualify.py | run | c83462542707… | = | = | MATCH, unchanged |
| reviewed_functions | p309_qualify.py | qc_formal | 8bc184214aea… | = | = | MATCH, unchanged |
| reviewed_functions | p309_qualify.py | research_test | 01fae563f3b5… | = | = | MATCH, unchanged |
| reviewed_functions | p309_qualify.py | qc_research_simple | 675ccfbd330a… | = | = | MATCH, unchanged |
| reviewed_functions | p309_qualify.py | mirror | 98254406862c… | = | = | MATCH, unchanged |
| reviewed_functions | p309_qualify.py | start_qhost_monitor | 489721f2de82… | = | = | MATCH, unchanged |
| reviewed_functions | p309_qualify.py | stop_qhost_monitor | d033e684902d… | = | = | MATCH, unchanged |
| reviewed_functions | p309_qualify.py | qhost_preflight | fa14832aa691… | = | = | MATCH, unchanged |
| reviewed_functions | p309_topology_drill.py | git / run_py / controls | 9bc80915… / ef699389… / 5930c65d… | = | = | MATCH, unchanged |
| ref_mutation_functions | p309_topology_drill.py | main / controls | 9db8d792… / 5930c65d… | = | = | MATCH, unchanged |
| ref_mutation_functions | p309_topology_drill.py | make_topology | 8af1bb783667… | 8af1bb783667… | 9b59c12fa22f… | MATCH, **re-pinned** |

* All nine scanner-pinned runner functions (`process_policy.reviewed_functions` for `code/p309_qualify.py`) are unchanged. The exactly-once sites, backstop pins, production read-path pins and constant pins are untouched (all in `p309_driver.py`). `p309_scan_pins.py --list` in the scratch clone reports `P309 SCAN PINS: all current`.
* **Gap (S2):** r2 records every re-pin in `governance/R2_REPIN_LIST*.json`. `governance/R2_REPIN_LIST.json:314-320` still lists `make_topology` with `9b59c12f…`, and no supplement records `8af1bb78…`. No code reads these files, so nothing fails, but the governance trail is incomplete.

### Q5. Does T14a pass? YES

* **Static check** (`review/anchors.py`, the MUTANTS list taken from the test's AST): at the candidate, every one of the 18 MUTANTS anchors occurs **exactly once**, including `T14a_main_preflight_after_the_attempt` (count 1) and `T14c` (`MAIN_MON + MAIN_MIRROR`). At `3c191ac2` the T14a anchor occurs **0** times, so restoring the comment fixes the defect it was meant to fix. At the base, all counts are 1.
* **Run** in the scratch clone: `python3 -B tests/test_p309_static_controls.py` exited 0, with all 22 controls PASS (S00, T11a–c, T12a–c, T13a–c, T14a–k, S99) in 8.6 s. Also run there:
  * `code/p309_static_check.py`: T1–T14 all PASS, T5 formal scan PASS, exit 0;
  * `tests/test_p309_scan_allowance.py`: all PASS, exit 0.

### Q6. Does QC15/A7 pass? YES (statically computed)

At the candidate:

* `git diff --name-only c902fe2f 93d55063` lists 156 paths, **0** outside the r2 namespace. `c902fe2f` is an ancestor of the candidate.
* `git diff --name-only eb9a9c22 93d55063 -- …/p5y_k5_cell309_research_r1/` lists 0 paths.
* `git rev-parse 93d55063:…/p5y_k5_cell309_p309_r1` gives `ecd1c359ef0c3e0c9911b014b884376a10f6ed5b`, which equals `R1_TREE`.

So A7 holds. As a bonus, A6 also holds: the R5 blob is `f978eeb6…` and there are no COVERAGE_MAP_R6 paths. None of the three changed files is in the self-audit's `IMMUTABLE` lists.

### Q7. Is F-DRILL-ORDER fixed correctly? YES

* `make_freeze_manifest.build()` pins every tracked **or untracked** (non-ignored) file under the namespace whose first directory is in `FROZEN_DIRS = (code, config, fc2, freeze, tests, verify, governance)`. It excludes only `freeze/P309_FREEZE_MANIFEST.json`. So `freeze/P309_FREEZE.json` is pinned only if it exists when the manifest is built.
* `make_freeze_params.build()` reads governance docs, reviews, the driver bytes and the allowance. It never reads the manifest or anything under `freeze/`, and its output is deterministic. Running params first therefore has no circular dependency.
* `--check` rebuilds and compares, ignoring `built_utc` and `built_at_head`. In the drill, by the time the runner checks, F' has committed `P309_FREEZE.json`, so the old order (manifest first) always gives `MANIFEST DIFFERS`.
* **Reproduced in the scratch clone:**
  * old order (manifest, params, `--check`): `MANIFEST DIFFERS`, rc 1, 0 pins of `freeze/P309_FREEZE.json`, 182 code pins;
  * new order (params, manifest, `--check`): `MANIFEST IDENTICAL`, rc 0, 1 pin, 183 code pins; `make_freeze_params --check` gives IDENTICAL.

  This matches `F_DRILL_ORDER_DEMO.json`.
* **This is the real-freeze order.** r1's real freeze manifest at `4c754a73` pins `…p309_r1/freeze/P309_FREEZE.json` (`P309_FREEZE_MANIFEST.json:122`).
* **Sufficient:** the later drill commits (FR' and the checkpoint record) touch only `ledger/`, which is not a frozen directory, and the placeholder check writes to `evidence/`. Nothing else in the drill depends on the generator order. The `generators` rc list in the report changes order, but nothing reads it (grep).

### Q8. Does the crash matrix discriminate baseline r2 from the candidate? YES (with caveats)

* **Provenance checked:**
  * MATRIX_CANDIDATE `runner_sha256` `c60624b3…` equals the sha256 of the candidate `p309_qualify.py`;
  * the baseline's `e9eba86f…` equals the base runner;
  * the candidate replica tree `3b2f12f5…` equals the candidate tree;
  * the tool `fc174335…` and validator `3ec03346…` hashes equal `3c191ac2:…p309_r2_hardening/{tests/r2h_crash_matrix.py, code/r2h_validator.py}`.

  The harness runs the real `main()`. It stubs the gates, the Q-HOST preflight and the monitor, and wraps `os` to log fsync/link and to inject SIGKILL.
* **Discriminating cases:**
  * **C04, C05** (empty or partial QC05 record): the baseline is **CORRUPT** (`QC05.json: empty file` / `unparseable … torn write`); the candidate is **INTERRUPTED** (leftover `.QC05.json.tmp-<pid>`, with no torn record under the final name).
  * **C12** (partial summary): the baseline is **CORRUPT** (`P309_QUALIFICATION.json unparseable`); the candidate is **INTERRUPTED** (leftover `.P309_QUALIFICATION.json.tmp-<pid>`).
  * **fsync/link ops:** the baseline has 0/0 in every case. The candidate has, for example, C03 14/4, C10 122/22 and C15 137/25. The fsynced names include the record temporary files, `attempt_1`, `qualification`, `ledger` and both ledgers.
  * **S04** (leftover tmp), **S05** (torn ledger tail), **S06** (orphan RUN START): the candidate refuses with the H3 text and writes no new RUN START (run_start_lines 0 / 0 / 1, where the 1 is the planted fixture). The baseline **launches and completes** (COMPLETE_PASS output; run_start_lines 1 / 1 / 2).
  * **Units:** the candidate passes T01–T08. On the baseline, T03–T08 fail (no fsync, torn record, missing functions) and T01–T02 pass, so the tests discriminate.
* **Same in both, as expected:**
  * C02, C03, C08–C11, C13 (ABORTED) and C14 give the same classification;
  * S01–S03, S07 and S08 are refused in both;
  * S09 (race) gives rcs [0, 1] and one RUN START in both.

  Exactly-once holds in both versions. The candidate's improvement is durability, plus the pre-launch refusals in S04–S06.
* **Caveats:**
  * **C06/C07** (`before_link` / `after_link`) are **vacuous for the baseline**: it never calls `os.link`, so no fault is injected and it reports COMPLETE_PASS (rc 0). These two cases test the candidate only.
  * **C01:** `restart.ok=false` and `no_trace=false` in both are tool artefacts. `ok` requires every restart to be refused, but a fresh start is correct here (`fresh_start_allowed_after=true`). `no_trace` is computed **after** the restart probe has run a full run.
  * **S05/S06 `unchanged=false` on the candidate** comes from `QDIR.mkdir(exist_ok=True)` creating an empty `qualification/` before the H3 refusal. The `<absent>` and empty-directory hashes differ; the ledger is unchanged. This is baseline behaviour, not a regression.
  * **SIGKILL is not power loss.** The matrix shows the fsync and link *calls* and the atomic-rename protocol, but it cannot show that data survives a power cut. Partial writes are simulated by splitting `write()`.

### Q9. Is the branch clean enough to propose for adoption? PARTLY

* **Clean:**
  * a single commit `93d55063` whose only parent is `101ef2cb` (`git cat-file -p`);
  * the branch ref resolves to `93d55063`;
  * 3 paths, all in the r2 namespace;
  * no `.claude/**`, evidence, docs, ledger, governance, test or qualification paths (0 `.claude/` paths changed or tracked);
  * the commit is signed.
* **Before adoption:**
  * (a) the re-pin governance record (S2);
  * (b) r2's practice of a formal delta follow-up review. The runner changed after `REVIEW_R2_DELTA_FOLLOWUP_4` accepted `38842550`, and this independent review does not replace r2's brief/review/sha256 records (S3);
  * (c) a filesystem-capability precondition (S1);
  * (d) the r2 namespace contains no regression test for H1–H5. The tests and validator live in `p5y_k5_cell309_p309_r2_hardening` (which A7 forbids on r2) or in scratch (N2);
  * (e) drill and P8 records made under the old order are stale. The next worker-tier drill and P8 round must be re-run with 183 code pins (N5).

## Findings

### Blocker
* None found in the code delta.

### Should-fix
* **S1. New failure points after RUN START that depend on the filesystem.**
  * **Problem:** `xwrite` needs `os.link` (hard links), and `_fsync_dir` needs `fsync` on an `O_DIRECTORY` fd. Both run right after RUN START (`p309_qualify.py:758-762`, `:685-689`) and in every gate record. Some filesystems refuse hard links (some FUSE, vfat, some network or overlay setups) or return EINVAL on directory fsync. On such a filesystem the single attempt (R4 B8: no retry) would end INTERRUPTED at its first write.
  * **Why the drill doesn't cover it:** the worker-tier drill runs in a clone under `P309_SCRATCH_ROOT`, which may be a different filesystem from the real repository.
  * **Fix:** add a pre-launch probe that does link and directory fsync on the repository filesystem, kept out of `qualification/` (for example in `ledger/`'s parent or the namespace root). Alternatively, state the requirement in `R2_HOST_REQUIREMENTS.md` and check it on the execution host before launch.
  * **Note:** power-loss durability is filesystem-dependent in any case (ext4/xfs give the intended semantics; NFS and some overlay setups may not).
* **S2. The re-pin is not recorded in r2's governance trail.** `R2_REPIN_LIST.json` still records `make_topology = 9b59c12f…`. Add `R2_REPIN_LIST_SUPPLEMENT_5.json` (or equivalent) with before `9b59c12f…`, after `8af1bb78…`, and the reason "F-DRILL-ORDER: params before manifest". Report the unchanged lists the way supplement 4 does.
* **S3. Delta-review requirement.** The runner was accepted by follow-up review 4 (`38842550`), and the candidate changes it (5 changed and 6 new top-level functions) and the drill. r2's process calls for a formal delta follow-up (brief, review, exec ledger, sha256) before the freeze. That review should explicitly accept the new H3 refusal paths, ATTEMPT_START.json, and the `attempt_files_sha256` key under an unchanged schema label.

### Note
* **N1. Partial durability coverage.**
  * Files written by subprocesses (decoy outputs `QC08_DECOY_STAGE1A.json`, `QC09_DECOY_STAGE1B_*.json`, `QC14_REHEARSE.json`, and everything under `attempt_1/evidence/`) are never fsynced. H5 binds only top-level attempt files by hash, not the `evidence/` subtree.
  * The `host_rerun/` directory entry inside `qualification/`, and the `qualification/` entry inside the namespace directory, are not parent-fsynced. The orphan-start check covers a lost entry, so exactly-once is unaffected; only evidence could be lost.
* **N2. No in-namespace tests for H1–H5.** The units T01–T08, the crash matrix and the validator sit outside r2 (`p5y_k5_cell309_p309_r2_hardening` at `3c191ac2`, and scratch), so no QC gate exercises the new code. `tests/test_p309_host_controls.py` (A01 abort harness, which now reaches `sync_ledgers`) was not run by me (it runs `p309_host.py`) and is not in the supplied regression evidence. Matrix C13 covers the abort path synthetically.
* **N3. Dangling references.** The refusal text "classify it read-only with the status validator" (`:741`) and the `xwrite` docstring's "status classifier" (`:119`) point to a validator that is not in the r2 tree. Name its location, or adopt it under an A7-compatible arrangement.
* **N4. Schema label unchanged.** The completion-marker schema is still `P309_QUALIFICATION/2` despite the new key. This is harmless to the driver (it reads `pass` and `freeze_commit` only), but a reviewer may want a note in the delta brief.
* **N5. Stale records.** The F' manifest under the new order has one more code pin (183 vs 182). Earlier drill validations and P8 records (`R2_DRILL_ATTEMPT*_VALIDATION.json`, `R2_EQUIVALENCE_P8_ROUND5.json`, source F' `170074cc`) were made under the old order and must be regenerated by the next drill. This is expected, not a defect.
* **N6. Crash-matrix tool artefacts** (outside the candidate): C01 `ok`/`no_trace`, C06/C07 vacuous for the baseline, and S05/S06 `unchanged=false` caused by `QDIR.mkdir`. See Q8.
* **N7. Clean-crash edge cases in `prelaunch_state`.** A non-object JSON ledger row (`row.get` raises AttributeError) or a timezone-naive `utc` (aware/naive comparison raises TypeError) would crash instead of refusing. Both happen before the mkdir and RUN START, so nothing is lost. The current ledgers have neither: 19 + 1 rows, all objects with Z timestamps, no counters, no start lines (`review/ledgers.py`).
* **N8. Stricter refusal in `main`.** With the allowed set `()`, `main` would now refuse if `qualification/host_rerun/` existed before the main run. The runner's own flow (the host re-run reads `attempt_1/QC08_DECOY_STAGE1A.json` from HEAD) makes that order impossible in practice.
* **N9. Unchanged pre-existing hazard.** `E.log` inside the `_qhost_abort` signal handler can interleave with an interrupted `E.log` in `main`. This was already present in the baseline. H3 would now refuse a later launch over the resulting torn row, but no later launch is allowed anyway.

## Overall recommendation

**Propose after listed fixes.** The code delta is correct and minimal:

* the scanner pins hold;
* T14a, QC12 T1–T14 and A7 pass;
* F-DRILL-ORDER is fixed in the right direction (it matches r1's real freeze);
* the hardening discriminates in the matrix and changes no target, gate or driver logic.

Before adoption: add the re-pin governance record (S2), get the formal r2 delta follow-up review (S3), and address or explicitly accept the filesystem precondition (S1), ideally with a pre-launch link + directory-fsync probe on the repository filesystem. N1–N9 can be handled in the review brief.
