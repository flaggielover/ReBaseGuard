# Scoped delta review of SF1-A (ledger appendability in the r2 pre-launch probe), P309-r2, Cell 309
SF1A_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS

**Reviewer.** A fresh independent reviewer. I wrote none of the r2 code, its hardening, the S1 probe, this SF1-A change,
the session tooling or any earlier review. An earlier reviewer attempt was cut off; I did not read or reuse its
workspace. Earlier reports were used only as guides; every answer below rests on git objects and my own
recomputation.

**Brief.** `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/sf1a_review/BRIEF_SF1A_DELTA_REVIEW.md` at
`dc446519`, sha256 `59c2544d85c2c1f10a2219566c5840479f9fe9868a2e04b6a8462c662db40c66` (verified).

**Workspace.** `/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t7/sf1a_review/work2/`.
The brief names `.../sf1a_review/work/`; that directory holds the interrupted earlier attempt, so this review used
the sibling `work2/` as a fresh workspace (deviation in path only, made so as not to reuse the earlier attempt).
`EXEC_LEDGER.jsonl` there records every command (utc, command, purpose, rc).

**Boundaries kept.** No git write to `/home/user/ReBaseGuard` (status clean at the end). NEW Γ309 TARGET EVALUATIONS = 0.
No runner, driver, launcher, host tool, drill or evaluator was run or imported; `test_r2h_fsprobe.py`, the crash
matrix and the rehearsal were not run by me. No network, grants or cell values. The only tools run were r2's four
cheap static tools, in a fresh `--no-local` clone at `716946e8` with `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and
`TMPDIR` under `work2/`; the clone was deleted afterwards.

## 1. Commits and ancestry

| Role | Commit | Tree |
|---|---|---|
| r2 head (base of the delta) | `b66a45f097989764176075802c953df4b72c2aef` | `9aeb2d87a252b771d4703b6e1f4730b248176fb4` |
| SF1-A (head of the delta) = `origin/claude/p309-r2-sf1a-20261005` | `716946e8d9a6744d0b49de6acc802605b6eb1bf8` | `3afb045cea6b78c708686ecc9108abd6a2d46100` |
| accepted candidate | `a119e9789e2a1d42b584fff8a2301946a37f1bcb` | |
| baseline r2 | `101ef2cb17e5eab2892212178278da45b98004ed` | |
| evidence (hardening branch) | `b6efec425102b7f0523188182083af525423671f` (parent `dc446519`, which holds the brief) | |

Ancestry (git log): `101ef2cb` → `93d55063` → `a119e978` → `b66a45f0` (governance only) → `716946e8`. The delta
`b66a45f0..716946e8` is exactly one commit, whose sole parent is `b66a45f0`.

## 2. Diff scope

`git diff --stat b66a45f0 716946e8`: one file, `level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_qualify.py`,
3 insertions, 0 deletions, one hunk inside `fs_probe`, directly after `sync_ledgers()` and inside the existing
`try / except OSError / finally`:

```python
        for led in (E.Q.EXEC_LEDGER, E.Q.EXPOSURE_LEDGER):  # SF1-A: RUN START's append must not fail after the mkdir
            step = f"ledger appendability ({Path(led).name}: must exist and open for appending; nothing is written)"
            os.close(os.open(str(led), os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW))
```

Runner bytes: `b66a45f0` sha256 `36e428fb…abe1d` (identical to `a119e978`'s runner as recorded in the a119 matrix);
`716946e8` sha256 `540df055…f9a3af`. Recomputed by me from `git show`.

## 3. Evidence reviewed (committed at `b6efec42`, `.../sf1a_review/evidence/`)

| File | sha256 | Binding checked |
|---|---|---|
| `FSPROBE_TESTS_716946e8_s1a.json` | `8703ad2737f211e43d0d50301aa888dee8556ea3833e0790796bbe5ed0620487` | commit `716946e8`, tree `3afb045c` (= recomputed), runner `540df055` (= recomputed), tool `74bc5186` (= sha256 of `tests/test_r2h_fsprobe.py` at `b6efec42`, recomputed) |
| `FSPROBE_TESTS_b66a45f0_pre_s1a.json` | `24250e3e39b05026d399f925c2485dd2e048da7d99a1662cff098dd89feeab12` | commit `b66a45f0`, tree `9aeb2d87` (= recomputed), runner `36e428fb` (= recomputed), same tool sha256 |
| `MATRIX_716946e8.json` | `720eae625990242dfd65a9f12038b47153189882c160073337cf0796feb18136` | package/replica commit `716946e8`, parent `b66a45f0`, tree `3afb045c`, runner `540df055`; tool `fc174335` and validator `3ec03346` identical to the a119 and baseline matrices |
| `UNIT_716946e8.json` | `d71258f4a7e65f266d7a563221ff56b0ec4e048d23360055e6b99faae3f00fb7` | names only a replica path (`t7/matrix_sf1a/replica/...`), which `MATRIX_716946e8.json` binds to `716946e8` / `540df055`; no sha256 field of its own (see C-A4) |
| `AST_RUNNER_b66a45f0_VS_716946e8.json` | `6348454b8de042582b1cd332aa39956e383600a5eb373d8e24c2a2b8175140b9` | old/new sha256 = recomputed runner hashes |
| `FAST_CHECKS_716946e8.json` | `4927a8d9032e640fcb0bb306a37948cc27346b029af8328b51dfad46772857c0` | commit `716946e8`; four of its steps re-run by me (§5) |
| `REG_716946e8.json` | `53d296ce7ada4aa4396ee2044b5a212b3453675a386c235e61aa80e273de8f5b` | runner `540df055`; replica head `0f5a5afd` = the matrix's synthetic-freeze tip over `716946e8` |
| `STATIC_CONTROLS_716946e8.json` | `28693c5bc21d83a6e54cedbaeaf6d080b35f21131b804836a58bff379c2f1241` | 22 controls, all pass; re-run by me |
| `SF1A_RUNS_VALIDATION.json` | `2c55d8d1e4144438904d0be5fc4a082f4edd6566c0547bc624eed13342474aab` | commit `716946e8`, tree `3afb045c` |
| `REHEARSAL_716946e8_REVALIDATION.json` | `13c24990cdd424ec0fdee9c56ccd4b37ae91defd6440a6044438e30248b9497e` | verdict PASS, no reasons |
| `rehearsal/PROVENANCE.json` | `562e5704147c10b2bf9e77d554df3d752a559f23d8f1fafeb3c4f1d4968406a0` | commit `716946e8`, tree `3afb045c`, parent `b66a45f0`; DEVELOPMENT_ONLY, synthetic freeze |
| `rehearsal/VALIDATION.json` | `167a90a61c32ee6f2712159525c8223e295a9b29e3f1fe6bd3bc515a8885d834` | |
| `rehearsal/REHEARSAL_SUMMARY.json` | `4e49cb60f08ac7813523edcdd5c902f24a0344bb57ed461796b36ee5c16a40a6` | |
| `rehearsal/GATE_LEDGER.jsonl` | `b70b9d49e921a26bfd9b1b6c325d87641dac3a27dcbfdcef1d5db9e2eeb4cd22` | |
| `GUARD_TESTS_sf1a_phase.json` | `05e391cce90c4c590d75dc9248a596e6f59bce2bb691fc350972c347a8d615a6` | session tooling; not relied on |

Also read: the a119 matrices (`r2_candidate_followup/evidence/MATRIX_a119e978.json`, `..._run2.json`), the baseline
matrix (`evidence/matrix/MATRIX_BASELINE_r2_101ef2cb.json`), formal review 5 and its record at `b66a45f0`, and
`q309_guard.log_execution` / `log_exposure` (the ledger writers; research namespace unchanged by the delta).

## 4. Answers

### Q1. Is the delta exactly the SF1-A probe extension and nothing else? **YES**
- One commit, one file, one hunk of 3 added lines, all inside `fs_probe` (diff above).
- The AST evidence agrees and I agree from the diff: 41/41 defs on both sides, only `fs_probe` changed, module-level
  statements byte-identical, no def added or removed.

### Q2. Does it check the capability SF1 names, before Q-HOST, the attempt directory and RUN START / HOST RERUN START, in both `main` and `host_rerun`? **YES**
- SF1 (formal review 5, Should-fix) names the remedy: "both ledgers must exist and open `O_WRONLY|O_APPEND`, no write".
  The delta opens exactly the two ledger paths the writers use (`E.Q.EXEC_LEDGER`, `E.Q.EXPOSURE_LEDGER`, redirected by
  `p309_env` to r2's `ledger/ZERO_TARGET_LEDGER.jsonl` and `ledger/EXPOSURE_LEDGER.jsonl`) with
  `O_WRONLY|O_APPEND`, plus `O_NOFOLLOW`, without `O_CREAT`, and writes nothing.
- Order in `main` (716946e8 l.839-855): `fs_probe(QDIR)` → refusal rc 2 → H3 `prelaunch_state` → `qhost_preflight` →
  `os.mkdir(attempt_1)` → `E.log(RUN START)`. Order in `host_rerun` (l.756-779): `fs_probe(QDIR)` → H3 →
  `qhost_preflight(("host-rerun",))` → `os.mkdir(target)` → `E.log(HOST RERUN START)`. Both call sites are unchanged
  bytes; the new check runs inside them.
- The RUN START / HOST RERUN START append is `q309_guard.log_execution` → `EXEC_LEDGER.open("a")`; the exposure ledger
  is appended by `log_exposure` the same way. The probe exercises the same kernel open-for-write permission check as
  those writers, under the same process credentials.

### Q3. Is it fail-closed and precise? **YES** (with residual cases stated and judged non-blocking)
Independent OS-level check (`h_semantics.py`, scratch files only, no p309 module imported) of the exact call:
- **Missing ledger:** `FileNotFoundError` errno 2; nothing created (no `O_CREAT`). Stricter than the writer, which
  would create it. Before SF1-A, `sync_ledgers` silently tolerated a missing ledger (`_fsync_path` returns on
  `FileNotFoundError`); F15 shows this was a real gap and is now refused.
- **Read-only / unappendable ledger:** the open-for-write permission check is the writer's own, so EACCES / EPERM /
  EROFS surface at the probe exactly when they would at RUN START. As root, mode 0444 passes both probe and writer
  (consistent; the host tests refuse a root unit user, L07).
- **Symbolic link (including dangling):** `ELOOP` (errno 40) from `O_NOFOLLOW`; stricter than the writer, which would
  follow it. A directory in the ledger's place: `EISDIR`, as for the writer.
- **Precision:** the `except OSError` records `"{step}: {type} (errno N: …)"` where `step` names the ledger file and
  the step; `main` prints it as `QUALIFICATION REFUSED: filesystem probe (S1): ledger appendability
  (ZERO_TARGET_LEDGER.jsonl: …): PermissionError (errno 13: …)` (M06 evidence). The first failing ledger stops the
  loop; one named problem suffices to refuse.
- **Escaping exception:** `os.open` / `os.close` raise only `OSError` subclasses for any realistic input (the path is
  a module constant). Any other exception would still run the `finally` cleanup and propagate out of `main` before
  `os.mkdir(attempt_1)`, so no attempt is consumed. This behaviour is pre-existing for every probe step.
- **Open succeeds, later append still fails (residual):** a write-free probe cannot detect ENOSPC / EDQUOT on the
  ledger filesystem, `RLIMIT_FSIZE` / EFBIG, EIO at write time, or a change between the probe and the start line
  (H3 and the Q-HOST preflight run in between). A FIFO in the ledger's place blocks the open (no reader), so the
  probe would hang rather than refuse; the writer would hang identically, and no attempt directory exists at that
  point. These are outside what SF1 asked for and outside what a no-write probe can establish; formal review 5
  already lists full-disk and mount-change cases as pre-existing. Judged **non-blocking** (C-A1).

### Q4. Does it write or persist anything? **NO**
- No `O_CREAT`, no `O_TRUNC`, no `write`; the fd is closed at once. Independent check: after the identical open/close
  the file's bytes, size, mtime and ctime were unchanged and no directory entry was added.
- No new probe leftovers: the added lines create no file; the existing `finally` still removes `probe.a`, `probe.b`
  and the probe directory. M06 and F14/F15 record `probe_left: []`; F15 asserts the missing ledger is not created;
  M06 records `ledger_unchanged: true` and `qualification_entries: []`.

### Q5. Are scientific logic, target logic and gate semantics unchanged; all scanner pins current; the 9 pinned runner functions byte-identical; T14a and the static controls passing? **YES**
- Only `fs_probe` changes (Q1). The 9 pinned functions (`git`, `mirror`, `qc_formal`, `qc_research_simple`,
  `qhost_preflight`, `research_test`, `run`, `start_qhost_monitor`, `stop_qhost_monitor`) are byte-identical (AST
  evidence; the diff touches none of them).
- My own runs at `716946e8` (fresh clone): `p309_scan_pins.py --list` rc 0, "P309 SCAN PINS: all current", 130
  `current` rows including all 9 `code/p309_qualify.py` reviewed functions; `test_p309_static_controls.py` rc 0,
  22/22 PASS including `T14a_main_preflight_after_the_attempt`; `p309_static_check.py` (QC12) rc 0, T1-T14 PASS;
  `test_p309_scan_allowance.py` rc 0, 19/19 PASS.

### Q6. Do QC11, QC12, QC-D5, the host tests and QC15 / A7 pass, by content, bound to `716946e8`? **YES**
- `REG_716946e8.json` (runner sha256 `540df055` = recomputed `716946e8` bytes): QC11 rc 0, table 112 flows / 0 failed;
  QC12 14 PASS; QC-D5 backstop 27 PASS, controls 109 PASS, pins all current; `test_p309_host.py` 77 PASS;
  `test_p309_host_controls.py` 41 PASS; static controls 22 PASS; no `[FAIL]` line in any tail.
- `FAST_CHECKS_716946e8.json` (commit `716946e8`): QC15 self-audit `ok: true` with A1-A10 all true, including
  `A7_formal_namespace_only_research_unchanged`; manifest identical; the unresolved-marker check passes; QC12, static
  controls, pins and scan-allowance rc 0 (the last four re-run by me with the same result).
- Light rehearsal of `716946e8` (DEVELOPMENT_ONLY, synthetic freeze): 15/15 gates present and PASS, QC15 PASS,
  re-validation verdict PASS with no reasons, provenance bound to commit `716946e8` / tree `3afb045c`.

### Q7. Does the crash matrix still discriminate baseline r2 (`101ef2cb`) from this runner, unchanged from `a119e978`? **YES**
Recomputed from the committed matrices (`h_matrix2.py`, `h_matrix3.py`):
- Same 24 case ids, same tool `fc174335` and validator `3ec03346` across `716946e8`, `a119e978` and `101ef2cb`.
- `716946e8` equals `a119e978` in every case after normalizing pids, paths and timestamps, except S09.
- S09 (two runners race; mkdir decides) differs only in the loser's rc (`[0,1]` vs `[0,2]`) and loser text; both runs
  keep exactly one RUN START line and COMPLETE_PASS. `a119e978`'s own two runs differ the same way, and the baseline
  shows `[0,1]`, so this is race nondeterminism, not a change.
- Classifications that separate the hardened runners from the baseline are the same set for both: C04, C05, C12
  (baseline CORRUPT → INTERRUPTED), C06, C07 (baseline COMPLETE_PASS → INTERRUPTED). Fsync counts are identical to
  `a119e978` in every case (0 in the baseline).

### Q8. Do F14, F15 and M06 discriminate, and is M06's fault model faithful? **YES**
- On `716946e8` (s1a) all of F01-F15 and M01-M06 pass. On `b66a45f0` (pre_s1a) F01-F13 and M01-M05 pass and F14, F15,
  M06 fail: F14 "an unsupported capability was accepted", F15 returns no problem for a missing ledger, and M06
  records the attempt being consumed: rc 1, `preflight_called: true`, `attempt_dir: true`,
  `qualification_entries: ["attempt_1"]`, `run_start_lines: 0`, traceback from the injected EACCES at the writer.
  That is exactly the SF1 defect, reproduced, then refused at `716946e8` (rc 2, no preflight, no attempt directory,
  no start line, ledger unchanged).
- Fault model: the runner's `os` proxy raises EACCES for an `os.open` of a `.jsonl` path with `O_APPEND` and a write
  mode; `pathlib.Path.open` raises EACCES for `ledger/*.jsonl` in an `a`/`w`/`+` mode. A real unappendable ledger fails
  both opens at the same kernel check, with the same errno family, so injecting at both boundaries is a faithful
  stand-in. Its limit: it is injection, not a real permission state; the independent OS check (Q3) covers the real
  flag semantics. I read the tool's diff (`4b3baebd` → `dc446519`): it adds F14, F15, M06 and the s1a / pre_s1a
  labels and leaves the S1 tests' logic intact.

### Q9. Does SF1-A resolve SF1 as condition C2 requires? **YES**
C2 (before-freeze): "Resolve SF1, either by the probe extension under its own delta review, or by a recorded
host-preparation check". The owner selected SF1-A (message 5). The delta is the probe extension SF1 describes (both
ledgers must exist and open `O_WRONLY|O_APPEND`, no write), slightly stricter (`O_NOFOLLOW`), placed before Q-HOST, the
attempt directory and both start lines, fail-closed and precise, and this is its own delta review. The residual
cases in Q3 are of the kind formal review 5 already called pre-existing and are not part of SF1.

**SF1: RESOLVED**

Effective upon incorporation of `716946e8` into r2; C2 is then satisfied by this probe extension.

### Q10. Are there unauthorized changes or namespace changes outside r2? **NO**
- The delta touches only `level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_qualify.py`; the research namespace
  (`p5y_k5_cell309_research_r1`) is byte-identical across the delta; QC15 A7 is true.
- No scope creep: SF2 (docstring and the two traceback-to-refusal changes) is **not** included, consistent with the
  owner's limit ("does not authorize unrelated hardening"). The new tests live in the hardening namespace on a
  separate branch and are not part of the r2 delta.

## Blockers

None.

## Should-fix

None that blocks or that must be done before the freeze. Advisory follow-ups are listed as conditions C-A1 to C-A5.

## Conditions

| Id | Class | Condition |
|---|---|---|
| C-B1 | **blocking-before-incorporation** | Incorporate exactly `716946e8` on top of `b66a45f0` (a fast-forward, or the same single-path bytes: `p309_qualify.py` sha256 `540df0552bfc31512289e30eaf1ead57bf82a4ac806f38080439c05c43f9a3af`). No hardening-branch file, tool, test or evidence enters r2 in the same step (R18; QC15 A7). The incorporation itself is a separate owner decision not taken here |
| C-F1 | **before-freeze** | The remaining before-freeze conditions of formal review 5 (C3: the worker-tier drill on the incorporated bytes) still apply; the drill should run on bytes that include SF1-A, so the probe's ledger check is exercised by the host's real unit user and real ledgers |
| C-A1 | advisory | Residual cases a write-free probe cannot detect (ENOSPC / EDQUOT / EFBIG / EIO at append time; change between probe and start line; a FIFO in a ledger's place blocks rather than refuses). Record them as accepted limits, alongside formal review 5's power-loss caveat |
| C-A2 | advisory | Add tests for a symlinked ledger (expect ELOOP) and a success-path assertion that both ledgers' bytes and mtime are unchanged by the probe (F01 does not check the ledgers). Both were verified here only by the independent OS-level check |
| C-A3 | advisory | The `fs_probe` docstring does not mention ledger appendability; fold this into SF2 when it is taken up, under its own reviewed delta |
| C-A4 | advisory | `UNIT_716946e8.json` carries no commit / runner sha256 field of its own; its binding is indirect, through the replica path that `MATRIX_716946e8.json` binds. Future unit evidence should record both |
| C-A5 | advisory | Matrix case S09's loser rc is nondeterministic (1 or 2) across runs; a comparison tool should normalize it rather than treat it as a difference |

## SF1 ruling

**SF1: RESOLVED**

## May the change be incorporated into r2?

**Technically, yes**, subject to C-B1. No blocker was found; the delta is the minimal, authorized SF1-A extension, it is
fail-closed, writes nothing, leaves scientific, target and gate logic and all pins unchanged, and its tests
discriminate. Incorporation itself is a separate owner decision that has not been taken; this review does not take it.
