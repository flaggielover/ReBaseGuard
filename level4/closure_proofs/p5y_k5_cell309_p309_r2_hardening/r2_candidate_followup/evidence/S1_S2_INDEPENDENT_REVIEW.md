# Independent review of the S1+S2 delta (p309 r2 adoption candidate)

- **Reviewer:** an independent subagent. It did not write this change and did not trust commit messages or code comments.
- **Delta:** `93d550638b8c79ae1c252fc6c2b0194b1a416b49 .. a119e9789e2a1d42b584fff8a2301946a37f1bcb` on branch `claude/p309-r2-adoption-candidate-20261005`, in namespace `level4/closure_proofs/p5y_k5_cell309_p309_r2/`.
- **Files changed (`git diff --stat`):** `code/p309_qualify.py` (+89 lines in `fs_probe`/`_oserr`, plus 4 lines each in `main` and `host_rerun`; 170 insertions in total, no deletions) and `governance/R2_REPIN_LIST_SUPPLEMENT_5.json` (new file).
- **Inputs read:**
  - `git show`/`git diff` of 101ef2cb, 38842550, 93d55063 and a119e978
  - `config/SCANNER_ALLOWANCE_P309.json`
  - `code/p309_static_check.py`, `code/p309_env.py`, `q309_guard.log_execution`, `tests/test_p309_host_controls.py`, `code/p309_topology_drill.py`
  - the hardening branch evidence `r2_candidate/evidence/SCAN_PINS_*.txt`
  - `.../scratchpad/t3/htools/.../tests/test_r2h_fsprobe.py` (sha256 b597ed8b…, which matches `tool_sha256` in both result files)
  - `.../scratchpad/t4/ev/FSPROBE_TESTS_a119e978.json` (label s1) and `FSPROBE_TESTS_93d55063_pre_s1.json` (label pre_s1)
- **Checks run by the reviewer:**
  - In a fresh `--no-local` clone at a119e978 (since deleted), with `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR` set under `scratchpad/t4/review/`: `code/p309_static_check.py`, `code/p309_scan.py`, `code/p309_scan_pins.py --list` and `tests/test_p309_static_controls.py`.
  - `review/ast_cmp.py` and `review/claims.py`: AST and hash recomputation from `git show` bytes; nothing was imported.
  - `review/ph_grep.py`: a static placeholder grep using the exact regexes from `p309_placeholder_check.py`.
- **Not done:** the runner, launcher, host, drill and driver were not run or imported, and `test_r2h_fsprobe.py` was not run. The work repo was not modified (HEAD is still a119e978 and nothing is tracked as modified).

## Answers

| | Question | Answer |
|---|---|---|
| A | Probe strictly before Q-HOST, the attempt directory and RUN START in main and host_rerun; no path to RUN START without it | **YES** |
| B | Tests exactly the capabilities that xwrite, sync_ledgers and attempt creation rely on | **PARTLY**: it covers xwrite and sync_ledgers fully and the attempt directory/monitor file through the same filesystem. Small gaps: ledger append writability, and mkdir refusing an existing name. Two checks are slightly stricter than needed but harmless. |
| C | Fails closed and gives a precise reason | **YES**, with two minor notes: an `iterdir` PermissionError escapes as a traceback (still before the start line), and fsync durability cannot be proven (inherent) |
| D | No persistent qualification evidence; ordering with H3 | **YES**, no ordering problem |
| E | Only main/host_rerun changed and 2 functions added; no gate, pinned or module-level change | **YES** |
| F | QC12 (T14), scanner and pins accept it; placeholder-clean | **YES** |
| G | S2 is additive, its hashes are correct and its claims accurate | **YES**, with stylistic extras only |
| H | Tests are meaningful and discriminate | **PARTLY**: they are meaningful against S1, but the pre_s1 discrimination of F01–F13 is trivial (AttributeError) and a few branches are untested |

## Evidence

### A. Order (YES)

`p309_qualify.py` at a119e978:

- **main**, in this order:
  1. 831: `QDIR.mkdir(exist_ok=True)`
  2. 832–835: the "attempt already exists" check
  3. **836–839: `fs_probe(QDIR)`**, which returns 2 on any problem
  4. 840: `prelaunch_state` (H3)
  5. 845: `qhost_preflight`
  6. 850: `os.mkdir(attempt_1)`
  7. 851: `E.log(RUN_START…)`
- **host_rerun**, in this order:
  1. 750: "re-run exists" check
  2. **753–756: `fs_probe(QDIR)`**
  3. 759–766: H3
  4. 768: `qhost_preflight`
  5. 773/775: mkdir
  6. 776: `HOST_START` log

Both functions run straight through with no branch around the probe. `RUN_START` and `HOST_START` are logged only in main and host_rerun (`git grep`). The one other writer is the topology drill's development-only `ITEM_CODE` (`p309_topology_drill.py`, around line 106), which logs `RUN_START … attempt_drill` in the drill clone without the probe. That bypass existed before this delta and is not a production path. The drill's full-runner path goes through main and therefore through the probe.

QC12 T14 in the clone gives `main` and `host_rerun` all true, including `refusal_returns_before_mkdir`, `start_logged_right_after_mkdir` and `preflight_before_mkdir`. The pre_s1 test run shows what used to happen when a capability was missing: M02, M03 and M05 at 93d55063 wrote the start line and created `attempt_1` (`run_start_lines` 1, `qualification_entries ['attempt_1']`). At a119e978 they are refused with `preflight_called` false and 0 start lines.

### B. Coverage (PARTLY)

**What the runner relies on, and how the probe covers it:**

- **xwrite:**
  - O_EXCL\|O_NOFOLLOW temp create: probe lines 177–178.
  - Full write loop and file fsync: 180–185.
  - `os.link` to the final name, which must refuse an existing name: 194–195 and 202–207.
  - unlink: in the cleanup at 216–222.
  - Directory fsync: 208–210 (both the new subdirectory and QDIR).
- **sync_ledgers:** the probe calls the real function (211–212).
- **Exclusive attempt:** the probe's own `os.mkdir`.
- **Q-HOST monitor file (O_EXCL in the attempt directory):** the same O_EXCL capability on the same filesystem.

**Where the probe runs:** inside `QDIR/.p309-fsprobe-<pid>/`. This is the same filesystem as `attempt_1/`, `attempt_1/evidence/` and `qualification/host_rerun/<id>/`, which are all created later under QDIR and cannot be separate mount points (they do not exist yet). The one exception would be a pre-existing `host_rerun/` symlink or mount, which is theoretical. The ledger directory `FNS/ledger/` is a sibling directory, and its fsync is exercised by `sync_ledgers()`.

**Not covered:**

1. **Ledger append writability.** `q309_guard.log_execution` appends with `EXEC_LEDGER.open("a")` (q309_guard.py:119/128). The probe's `sync_ledgers` opens the ledgers O_RDONLY only, and `_fsync_path` skips a missing file silently (lines 103–111). The first append is the RUN START line itself, made right after `os.mkdir(attempt_1)` (850–851). A non-writable ledger file therefore still consumes the single attempt, leaving an attempt directory without a start line. The mount itself is writable through the launcher's `ReadWritePaths=<repo>` (p309_launch.py:132), so only per-file permissions or attributes are exposed. Risk is low. → **SF1**
2. **mkdir refusing an existing name.** The probe proves `mkdir` of a new name but not that `mkdir` refuses an existing one, although the docstring claims "the exclusive attempt". The existing-attempt check comes first and EEXIST is universal POSIX, so this is a note (N1).

**Checked but stricter than needed (conservative and harmless):**

- Any non-EEXIST error on the second O_EXCL or the second link refuses the launch. xwrite would also fail safely in that case.
- `st_nlink >= 2` is required.
- The bytes are read back through the new name.

Nothing is checked that the runner does not need.

### C. Fail-closed and precise (YES, with notes)

- **Every OSError inside the probe** goes to the step-tagged `except OSError` (213–214), which uses `_oserr` → `"<step>: <Type> (errno N: msg)"`. That covers EIO on fsync, ENOSPC on write, EPERM on link, EINVAL on directory fsync, and errors from `os.close` in the inner `finally`.
- **mkdir failure** (EROFS, EACCES, or EEXIST from a race) returns immediately and never removes a directory that is not the probe's own (170–174).
- **Cleanup errors:**
  - unlink errors other than ENOENT are reported (221–222).
  - rmdir failure is reported with "blocks every launch until removed by hand" (223–227).
  - fsync of QDIR after the rmdir is reported (229–232).
- **O_EXCL not honoured:** the second open succeeds and the probe appends a problem (188–193). There is no O_TRUNC, so the data survives.
- **Link produces a copy:** caught by the (st_dev, st_ino) and nlink checks (196–199).
- **Link replaces an existing name:** reported (202–205).
- **Second link raising something other than FileExistsError:** caught as OSError, step "hard link over an existing name". This fails closed.
- **Partial writes:** the memoryview loop handles them. As in xwrite, a `write` returning 0 would loop forever; this is theoretical for regular files (N4).
- **Interrupted probe:**
  - SIGKILL or default SIGTERM leaves `.p309-fsprobe-<pid>`. The next launch refuses it by name and does not remove it (163–166; test F11/M04).
  - SIGINT runs the `finally` cleanup and then propagates. That is a traceback before the start line, so it fails closed.
- **PID reuse:** any `.p309-fsprobe-*` entry is refused before mkdir, so a reused PID can never pick up an old directory. A same-name collision can only come from a concurrent race; it fails at `os.mkdir` with a precise refusal, and the other process's directory is left alone.
- **Exceptions that escape:**
  - `where.iterdir()` (163) is outside the try. A PermissionError there escapes as a traceback (rc 1) before H3, Q-HOST and the start line. This fails closed but is not a problem-list message. In main, line 832 already iterates QDIR, so it is unreachable there; it is reachable in host_rerun (N3).
  - Non-OSError exceptions cannot normally arise in the try body.
- **Returns `[]` although a capability is missing:** only where the capability cannot be observed. A volatile filesystem (tmpfs/ramfs) or an fsync-suppressing layer such as eatmydata passes, because the probe proves that the calls succeed, not that data is durable (N2). The same applies to the missing-ledger skip (SF1).
- **host_rerun with no `qualification/`:** now refused ("qualification/ does not exist (nothing to probe)"). Before S1 such a re-run proceeded and was bound to fail `same(x, q08)` against a missing attempt_1, so this is an improvement.

### D. No persistent evidence; H3 ordering (YES)

- After a successful probe only the probe's own directory has been created and removed, plus fsyncs. QDIR's entries are unchanged; only directory timestamps move, and git does not track them.
- Supporting tests:
  - F01: the directory is empty after the probe.
  - M01: `probe_left []`, and the run completes with 1 RUN START line.
  - M02 and M03: `qualification_entries []`, `ledger_unchanged true`.
- **H3 interplay:**
  - In main, H3 (`allowed=()`) runs after the probe, which has already removed its directory or refused.
  - In host_rerun, `names` is computed after the probe (759), and dot-entries are not allowed, so a concurrent probe directory is refused.
  - A leftover gets the probe's specific message rather than H3's generic one. At pre_s1, H3 already refused the M04 leftover, generically.
- **Design note (N5):** the probe runs before H3 and Q-HOST, as specified. A manual run outside the launched unit therefore creates and removes a probe directory before Q-HOST refuses it. Before S1, nothing beyond `QDIR.mkdir` was written in that case. This is harmless. The alternative order (H3 → Q-HOST → probe → mkdir) would also satisfy T14.
- **Existing tests:** none is broken. `test_p309_host_controls` Q01–Q07, R01 and A01 call `qhost_preflight`/`start_qhost_monitor` directly, not main.

### E. Gate semantics (YES)

`review/AST_CMP.json` (comparing 93d55063 with a119e978):

- `runner_added ["_oserr","fs_probe"]`, `runner_removed []`, `runner_changed ["host_rerun","main"]`, 37 unchanged.
- `module_level_statements_identical true` (34/34), and the definition order of shared functions is the same.
- All 9 `process_policy.reviewed_functions` for p309_qualify.py match their pinned hashes at a119e978: `git`, `run`, `qc_formal`, `research_test`, `qc_research_simple`, `mirror`, `start_qhost_monitor`, `stop_qhost_monitor`, `qhost_preflight`.
- `items_table`, `run_item` and every `qc*` gate function are unchanged.
- The text diff of main/host_rerun is additions only: the 4-line probe block in each.

### F. Static rules (YES)

Run in the clone at a119e978:

- **`p309_static_check.py`:** rc 0, T1–T14 all PASS. T14 detail: every key is true for main and host_rerun.
- **`p309_scan.py`:** rc 0, `"verdict": "PASS"`, `formal_controls_fire_all_kinds true`, `allowance_config_sha256 f1780a91…`.
- **`p309_scan_pins.py --list`:** rc 0, "P309 SCAN PINS: all current".
- **`tests/test_p309_static_controls.py`:** rc 0. S00, T11a–c, T12a–c, T13a–c, T14a–k and S99 all PASS, so the T14 mutation anchors still match after the insertion.
- **Placeholder grep** (the exact MARKERS and CHOICE regexes): 0 hits in p309_qualify.py at both revisions, 0 hits in SUPPLEMENT_5.json, and 0 hits in the 170 added lines.

### G. S2 supplement (YES)

- **Prior files unchanged:** `R2_REPIN_LIST.json` and SUPPLEMENT_1..4 are byte-identical at 101ef2cb, 93d55063 and a119e978. Their row counts are 51/48/13/10/8, as the record claims.
- **make_topology hashes** (sha256 of `ast.dump`, CPython 3.11.15, the same as `p309_scan.ast_sha`):

  | Commit | Hash |
  |---|---|
  | 101ef2cb | 9b59c12f…92e8 |
  | 38842550 | 9b59c12f…92e8 |
  | 93d55063 | 8af1bb78…c575 |
  | a119e978 | 8af1bb78…c575 |

  These match `reviewed_38842550` and `now`. The allowance entry at index 20 holds 9b59… at 101ef2cb and 8af1… at 93d55063.
- **Allowance:**
  - Byte-identical between 93d55063 and a119e978.
  - sha256 57cc9a22… at 101ef2cb and 38842550, f1780a91… at a119e978. These match `allowance_sha256_before`/`after`.
  - Leaf count 1228/1228. The only changed leaf is `/ref_mutation_functions[20]/ast_sha256`; the only changed top-level key is `ref_mutation_functions`. So every list in `unchanged_lists`, including process_policy, t7_exemptions and import_policy, is in fact unchanged.
- **Other claims:**
  - `reason_unchanged` is true.
  - `r1_at_F: null` is correct: r1's allowance at 4c754a73 has no make_topology entry.
  - The drill diff 101→93d is exactly a swap of two list elements in `make_topology`; it is the only changed drill function, and module level is identical.
  - `paths_changed_by_the_candidate_commit` matches `git diff --name-only 101ef2cb 93d55063`.
  - The cited hardening-branch evidence exists and says what the record claims: BEFORE_REPIN shows "make_topology: STALE HASH … 1 NOT CURRENT", REFRESH shows "refreshed: ref_mutation_functions code/p309_topology_drill.py make_topology", and AFTER shows "all current".
  - "Every gate function and items_table unchanged" holds for 101→93d. Changed runner functions there are the durability helpers, `run_item`, `_qhost_abort`, `attempt_start`, `prelaunch_state`, main and host_rerun; no `qc*` function or `items_table` changed.
- **Schema/style:** the same schema string and the same core keys as SUPPLEMENT_4 (`schema`, `supplements`, `round`, `hash`, `compared`, `unchanged_lists`, `import_allowlist_additions`, `rows` with `list`/`file`/`name`/`reviewed_<commit>`/`now`/`r1_at_F`/`kind`/`reason_now`). Additions:
  - top-level keys `proof`, `validation_of_this_repin` and `statement`
  - row keys `change`, `how_repinned` and `reason_unchanged`
  - no `permits_now`, which is correct because `ref_mutation_functions` entries have no permits

  These are additive and informational. SUPPLEMENT_1 already introduced an extra key, so there is precedent. The file is valid JSON, ends with a newline, and no code consumes `REPIN_LIST*` (`git grep`).

### H. Tests (PARTLY)

- **Provenance:** the result files bind the runner bytes. s1 has `runner_sha256` 36e428fb… (equal to the git blob at a119e978); pre_s1 has c60624b3… (equal to the blob at 93d55063). Both have `meets_expectation true`.
- **Positive tests:**
  - F01: clean result, nothing left.
  - F02: the exact operation sequence: file fsync, two links to probe.b, directory fsyncs of the probe directory and QDIR, fsync of both ledgers and the ledger directory.
  - M01: a full synthetic run through the real main, with 1 RUN START line and no leftover.
- **Negative tests:** each injects one fault at the `os` boundary and asserts the step name, the errno where relevant, and an empty directory afterwards:
  - F03 EPERM link
  - F04 link replaces
  - F05 link copies
  - F06 O_EXCL ignored
  - F07 EIO fsync
  - F08 EINVAL directory fsync
  - F09 ledger fsync
  - F13 ENOSPC
  - F10 rmdir failure leaves a directory that is refused by name and not removed
  - F11 SIGKILL mid-probe leaves a leftover that is refused and left byte-identical
  - F12 missing directory
  - M02–M05: the real main/host_rerun refuse before preflight, the attempt directory and the start line, with the ledger unchanged
- **Discrimination:**
  - M02, M03 and M05 discriminate in a meaningful way: pre_s1 consumes the attempt.
  - F01–F13 at pre_s1 fail only because `fs_probe` does not exist (AttributeError), so the test run does not show that each assertion would catch a defective probe. For example, the inode check or the second-link check could be removed without that run noticing. Read against the S1 code, though, each fault targets a distinct branch with a step-specific assertion. A small mutation run would close this gap (N6).
  - M04 at pre_s1 was already refused by H3. It discriminates only the wording, not safety.
- **Untested branches (N6):**
  - unlink failure during cleanup
  - probe-directory mkdir failure (EROFS/EACCES), the most realistic unsupported case
  - a mkdir name collision that leaves the other directory alone
  - a leftover in host_rerun (M04 covers main only)
  - the second O_EXCL or second link raising an error other than EEXIST
  - the `iterdir` PermissionError path
  - an unwritable ledger (see SF1)

## Findings by severity

**Blocker:** none.

**Should-fix (non-blocking):**

- **SF1. Ledger append not probed.** The RUN START line is the first ledger append, made right after the attempt mkdir (p309_qualify.py:850–851) by `open("a")` in `q309_guard.log_execution`. The probe's `sync_ledgers()` opens the ledgers O_RDONLY and skips missing files, so a ledger file without write permission, or a missing ledger, still consumes the single attempt. This is exactly the failure class S1 exists to prevent. Suggested fix, about 3 lines in `fs_probe`, with no other code touched:
  - require both ledger files to exist, and
  - require `os.access(p, os.W_OK)`, or open them `O_WRONLY|O_APPEND` without writing and close.

  Exposure is low, because the launcher grants `ReadWritePaths=<repo>` and the ledgers are tracked files.

**Notes:**

- **N1.** The docstring says the probe covers "the exclusive attempt", but `os.mkdir` refusing an existing name is not exercised. EEXIST is universal POSIX and the existing-attempt check comes first.
- **N2.** fsync success does not prove durability: a tmpfs or ramfs mount, or an fsync-suppressing preload, passes. This is inherent. An optional `/proc/self/mountinfo` filesystem-type check (p309_host.py already reads mountinfo) could refuse volatile filesystems for the official mode.
- **N3.** `where.iterdir()` (line 163) is outside the try. A PermissionError raises a traceback rather than a problem list. It still fails closed before the start line, and in main it is unreachable because of line 832.
- **N4.** The write loop would spin if `os.write` returned 0. xwrite has the same pattern, and this is theoretical for regular files.
- **N5.** The probe runs before H3 and Q-HOST, as specified, so an invocation outside the launched unit creates and removes a transient probe directory before Q-HOST refuses it. This is acceptable. Running it after Q-HOST would also satisfy T14.
- **N6.** The test gaps and the weak pre_s1 discrimination listed under H.
- **N7.** Nothing in QC12 or T14 requires `fs_probe` to stay present and in order. A later edit that removed it would still pass the static check, because main and host_rerun are not hash-pinned. A T14 key for this would be optional.
- **N8.** Pre-existing and out of scope: the drill's `ITEM_CODE` logs `RUN_START … attempt_drill` without the probe or H3, in the drill clone only.
- **N9.** SUPPLEMENT_5 adds informational keys beyond the SUPPLEMENT_4 shape (`proof`, `validation_of_this_repin`, `statement`, `change`, `how_repinned`, `reason_unchanged`). It is consistent with the schema, and SUPPLEMENT_1 set a precedent for extra keys.

## Recommendation

**ACCEPT the S1+S2 delta.**

- No blocker was found.
- S1 meets every stated requirement:
  - it runs before H3, Q-HOST, the attempt directory and the start line on both paths
  - it leaves no persistent entry
  - it fails closed with step and errno
  - it checks only needed capabilities
  - it refuses leftovers by name and never removes them
- The gates and pinned functions are untouched, and QC12, the scanner and the pins are green.
- S2 is additive and its hashes and claims check out.

SF1 (probing ledger appendability) is recommended as a small follow-up. If the owner wants the probe to cover every pre-start dependency, make SF1 a condition, which turns this into "accept after SF1". The notes are optional.
