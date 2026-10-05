# S1: filesystem pre-launch probe — review

| | |
|---|---|
| finding addressed | independent delta review of `93d55063`, **S1**: "new failure points after RUN START that depend on the filesystem" |
| commit | `a119e9789e2a1d42b584fff8a2301946a37f1bcb` on `claude/p309-r2-adoption-candidate-20261005` (parent `93d55063`) |
| file | `level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_qualify.py` (+97 lines; `_oserr` l.147, `fs_probe` l.151; calls at l.836 in `main`, l.753 in `host_rerun`) |
| scope | fail-fast check only. No gate, gate logic, pinned function, module-level statement, retry or resume path was added or changed |

All work was result-free. Nothing was evaluated, frozen or qualified.

## 1. The hazard it removes (demonstrated, not assumed)

The candidate's hardening makes the single attempt depend on two filesystem features, **right after RUN START**:
- **`os.link`** (hard links): `xwrite` links a fully written and fsynced temporary file to the final record name.
- **`fsync` on a directory fd**: `_fsync_dir`, via `xwrite` and `sync_ledgers`.

On a filesystem that lacks either one, the pre-S1 runner had already passed Q-HOST, created `attempt_1` and logged
RUN START when it crashed at its first durable write. Under R4 B8 (no retry) that **consumes the single attempt**.

This was reproduced with `tests/test_r2h_fsprobe.py`, which drives the real `main()` / `host_rerun()` in a replica of
`93d55063`, with the missing capability injected at the `os` boundary
(`evidence/FSPROBE_TESTS_93d55063_pre_s1.json`):

| case | pre-S1 runner `93d55063` | S1 runner `a119e978` |
|---|---|---|
| M02 hard links unsupported (EPERM) | rc 1. Q-HOST preflight called, `attempt_1` created, **RUN START written** (1 line), then `PermissionError` at the first `xwrite` | rc 2: `QUALIFICATION REFUSED: filesystem probe (S1): same-directory hard link: PermissionError (errno 1: …)`. No preflight, no `attempt_1`, 0 RUN START, ledger bytes unchanged, `qualification/` empty |
| M03 directory fsync unsupported (EINVAL) | rc 1. `attempt_1` created, **RUN START written**, then `OSError [Errno 22]` | rc 2: `… filesystem probe (S1): directory fsync: OSError (errno 22: …)`. Same "nothing happened" checks |
| M05 host re-run, hard links unsupported | rc 1. Preflight called, `host_rerun/<id>/` created, **HOST RERUN START written**, then `PermissionError` | rc 2: `HOST RERUN REFUSED: filesystem probe (S1): same-directory hard link: …`. No preflight, no `host_rerun/`, ledger unchanged |

## 2. What the probe checks: exactly the capabilities the candidate uses

| capability | used by (after RUN START) | probe step (name in the refusal) |
|---|---|---|
| exclusive create (`O_CREAT|O_EXCL|O_NOFOLLOW`) | `xwrite`'s temp file; `start_qhost_monitor`'s monitor file | `exclusive create (O_EXCL)` |
| O_EXCL refuses an existing name | the same (no overwrite) | `exclusive create over an existing name` |
| complete write | `xwrite` (loop over short writes) | `write` |
| file fsync | `xwrite` (the record bytes) | `file fsync` |
| same-directory hard link that is a **second name of the same file** (same `st_dev`/`st_ino`, link count ≥ 2, bytes read back) | `xwrite` (temp → final name) | `same-directory hard link` |
| hard link **refuses an existing name** (FileExistsError) | `xwrite` ("a record is never replaced") | `hard link over an existing name` |
| directory fsync | `_fsync_dir` in `xwrite`, H4, `sync_ledgers` | `directory fsync` (the probe's directory and `qualification/`) |
| ledger fsync + ledger-directory fsync | `sync_ledgers` | `ledger and ledger-directory fsync (sync_ledgers)`: the probe **calls `sync_ledgers()` itself** |

**Where it probes:**
- **`qualification/` (QDIR) itself.** The attempt directories (`attempt_1/`, `host_rerun/<id>/`) are created inside it.
- **The ledgers:** `sync_ledgers` is the very function used later.
- **Not covered:** a mount point *inside* `qualification/` is not covered. The runner never creates one, and the
  durable-host packet keeps the whole namespace on one ext4 / xfs volume.

**Not checked (because the candidate does not need it):**
- `rename` and `O_DIRECT`;
- power-loss behaviour, which cannot be tested by a probe: a probe shows the calls succeed, not that the device honours
  them. That remains a host requirement (ext4 / xfs; durable-host packet §2) and is still SAFE_BUT_UNPROVEN.

## 3. Ordering, fail-closed and cleanup

**Ordering:**
- **`main`** (l.836): after the existing-attempt refusal, and **before**:
  - H3 `prelaunch_state` (l.840);
  - `qhost_preflight` (l.845);
  - `os.mkdir(attempt_1)` (l.850);
  - RUN START (l.851).
- **`host_rerun`** (l.753): after the "re-run already exists" refusal, and before:
  - H3 (l.760);
  - `qhost_preflight` (l.768);
  - the mkdir (l.775);
  - HOST RERUN START (l.776).
- r2's own QC12 T14 check ("Q-HOST refusals before the attempt") passes on `a119e978`.

**Why before H3:**
- A leftover probe directory then gets the probe's precise message, not H3's generic "exists (a prior or partial run)".
- The probe only touches its own new directory, so running it before H3 changes nothing H3 inspects.
- H3 still runs afterwards and still refuses every other trace.

**Fail closed.** Every `OSError` in a step becomes a problem string naming the step, the exception type and the errno.
Any non-empty list causes a refusal with exit 2. A non-OSError exception propagates and the runner exits before
RUN START. In both cases no attempt is started. There is no retry.

**No persistent qualification evidence:**
- The probe works only in its own new directory, `qualification/.p309-fsprobe-<pid>/`, using the files `probe.a` and
  `probe.b`.
- It unlinks both files, removes the directory and fsyncs `qualification/` again.
- After a supported run, `qualification/` has no new entry (F01; M01: no `.p309-fsprobe-*` anywhere in the namespace).

**Refusal of leftovers:**
- If cleanup fails (F10) or the probe is killed (F11, a real SIGKILL in a child process), the directory remains.
- The next launch is refused, naming it: `qualification/.p309-fsprobe-<pid> is left by an interrupted filesystem probe
  (no attempt was started; it holds only probe files): remove it by hand, then launch again`.
- The probe **never removes** a leftover (r2's rule: nothing is repaired). F11 checks that the leftover's tree is
  unchanged after the refusal; M04 checks that `qualification/` and the ledger are byte-identical.

## 4. Tests (`tests/test_r2h_fsprobe.py`, hardening namespace; positive and negative)

Faults are injected through a proxy of the runner's `os` module, because no filesystem lacking these features is
available in this container. M01–M05 run the real `main()` / `host_rerun()`, with the gates, mirror and Q-HOST as test
doubles.

| id | case | `a119e978` (S1) | `93d55063` (pre-S1) |
|---|---|---|---|
| F01 | supported directory → `[]`, nothing left | PASS | FAIL (no `fs_probe`) |
| F02 | operations performed: file fsync, link + refused link, dir fsyncs, both ledgers and their directory | PASS | FAIL |
| F03 | `os.link` EPERM → "same-directory hard link … errno 1", nothing left | PASS | FAIL |
| F04 | link replaces an existing name → "did not refuse an existing name" | PASS | FAIL |
| F05 | link makes a copy (different inode) → "not a second name of the same file" | PASS | FAIL |
| F06 | O_EXCL not honoured → "O_EXCL did not refuse" | PASS | FAIL |
| F07 | file fsync EIO → "file fsync … errno 5" | PASS | FAIL |
| F08 | directory fsync EINVAL → "directory fsync … errno 22" | PASS | FAIL |
| F09 | ledger fsync EIO → "sync_ledgers … errno 5" | PASS | FAIL |
| F10 | rmdir fails → "blocks every launch"; the next probe refuses the leftover by name; not removed | PASS | FAIL |
| F11 | probe SIGKILLed mid-way (real child) → leftover refused by name, tree unchanged | PASS | FAIL |
| F12 | directory missing → "does not exist" | PASS | FAIL |
| F13 | write ENOSPC → "write … errno 28" | PASS | FAIL |
| M01 | supported: the full synthetic run completes (rc 0, one RUN START, `ATTEMPT_START.json`, summary pass), no probe leftover | PASS | PASS |
| M02 | hard links unsupported → refused before preflight / attempt / RUN START | PASS | FAIL (attempt consumed, §1) |
| M03 | directory fsync unsupported → the same | PASS | FAIL (attempt consumed) |
| M04 | planted leftover → precise refusal, nothing changed | PASS | FAIL (H3's generic refusal) |
| M05 | host re-run, hard links unsupported → refused before HOST RERUN START | PASS | FAIL (re-run consumed) |

**Results:** 18/18 on the S1 runner. On the pre-S1 runner, F01–F13 and M02–M05 fail while M01 passes, so the tests
discriminate. Evidence: `evidence/FSPROBE_TESTS_a119e978.json`, `evidence/FSPROBE_TESTS_93d55063_pre_s1.json`.

## 5. Identity and static checks

**AST/byte comparison `93d55063` → `a119e978`** (`evidence/AST_RUNNER_93d55063_VS_a119e978.json`):
- added: `_oserr`, `fs_probe`; changed: `main`, `host_rerun` (the call and its refusal only);
- nothing else touched, and nothing unintended;
- all 34 module-level statements are byte-identical;
- all 9 scanner-pinned runner functions are byte-identical to r2.

**r2's own checks on a clean clone of `a119e978`** (`evidence/FAST_CHECKS_a119e978.json`):
- QC12 static check PASS, including T14 "Q-HOST refusals before the attempt";
- static controls 22/22, T14a PASS;
- scan pins "all current";
- scan-allowance test PASS;
- placeholder check: 0 unallowed;
- manifest `--check` IDENTICAL.

**No scanner allowance change.** `fs_probe` makes no process or git call. Its file operations (`mkdir`, `link`,
`unlink`, `rmdir`) name only `qualification/.p309-fsprobe-*`, never a ref path.

## 6. Independent check of S1 and S2

A fresh independent reviewer examined exactly `93d55063..a119e978` (report: `evidence/S1_S2_INDEPENDENT_REVIEW.md`).
It read the code and ran r2's static check, scanner, scan pins and static controls in its own clone.

**Recommendation: ACCEPT.** No blocker.

**Answers:**
- **YES** on A (ordering), C (fail-closed / precise), D (no persistence), E (gate semantics / pins), F (static rules)
  and G (supplement).
- **PARTLY** on B (coverage) and H (tests).

**Its should-fix and notes, with how each is handled here:**

| id | finding | handling |
|---|---|---|
| SF1 (non-blocking, "not a condition") | Ledger **appendability** is not probed. RUN START, r2's existing first ledger append, comes right after the attempt mkdir. An unwritable ledger would still consume the attempt (low exposure: the launcher grants `ReadWritePaths=<repo>`) | **Not changed here.** It concerns r2's pre-existing ledger write, not a capability the hardening introduced, which is S1's mandate. Changing the probe now would reopen the whole validation. Put to the formal review as an item to rule on (`FORMAL_DELTA_REVIEW_PACKET.md` §5) |
| N1 | `os.mkdir` refusing an existing name (the exclusive attempt) is not exercised. The docstring's "the exclusive attempt rely on" overstates the coverage | Disclosed. POSIX `mkdir` is exclusive, and r2 relied on it before the hardening. Put to the formal review |
| N2 | fsync on tmpfs / eatmydata "succeeds": the probe proves the calls work, not durability | As stated in §2 (host requirement) |
| N3 | a `PermissionError` from listing `qualification/` escapes as a traceback (still before the start line) | Fail-closed, but not a formatted refusal. Put to the formal review |
| N4 | the write loop would spin if `os.write` returned 0 (same as `xwrite`); theoretical | Disclosed |
| N5 | a manual run outside the unit creates and removes the probe directory before Q-HOST refuses | Harmless; disclosed |
| N6 | untested paths: unlink failure, probe mkdir EROFS/EACCES, a leftover in `host_rerun`, non-EEXIST second-create/link errors, an unwritable ledger. The pre-S1 failures of F01–F13 are AttributeErrors (no per-assertion mutants) | Disclosed. No new mutants were added (scope) |
| N7 | no static rule keeps `fs_probe` present; `main` / `host_rerun` are not hash-pinned | As for all of r2's unpinned runner code; disclosed |
| N8 | the drill's development `ITEM_CODE` start line bypasses the probe | Development-only and pre-existing |
| N9 | supplement 5 carries informational keys beyond supplement 4's schema | Intended (proof and validation fields) |

## 7. Residual notes (disclosed; none blocks)

- **One unknown filesystem behaviour is still possible:** a filesystem that accepts these calls but loses data on power
  failure. Only the host requirement (ext4 / xfs, durable-host packet) covers that.
- **Timing gap.** The probe runs seconds before the attempt. A filesystem change between the probe and RUN START
  (a remount) is outside its reach. The exclusion gate and Q-HOST continuity cover the host during the attempt.
- **M03 refusal text.** The refusal lists two problems: the failed directory fsync, and the same failure during
  cleanup's directory fsync. Both are accurate.
