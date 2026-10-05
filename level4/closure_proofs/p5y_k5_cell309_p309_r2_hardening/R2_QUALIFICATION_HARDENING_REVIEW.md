# R2 qualification hardening review

**Scope.** The qualification **runtime** of r2 (`claude/p5y-k5-cell309-p309-r2` @ `101ef2cb`): how it writes, orders,
records and refuses. No scientific algorithm, gate logic or target logic was changed or evaluated.

**Method.**
- r2 was inspected read-only first (a `git archive` export).
- Its **real** runner `main()` was then driven in scratch replicas carrying a synthetic, non-target freeze, with
  synthetic gates and SIGKILL injected at every protocol point (`tests/r2h_crash_matrix.py`).
- Every outcome was judged by an independent validator that imports no r2 code (`code/r2h_validator.py`), and by byte
  hashes before and after three restart requests.

The same matrix was run on r2 as shipped and on the hardened runner. Machine-readable result: `R2_FAILURE_MATRIX.json`.

## 1. Findings on r2 as shipped (`101ef2cb`)

| # | finding | evidence | class |
|---|---|---|---|
| F1 | **Record and completion-marker writes are not atomic.** `xwrite` is `open(O_EXCL)` plus one `os.write`. A crash after open leaves an **empty** record; a crash mid-write leaves a **torn** record or summary under its final name | matrix C04, C05, C12 give CORRUPT; unit T04 fails on baseline | UNSAFE |
| F2 | **No fsync anywhere in the qualification path**: not on records, the summary, directories, ledgers or the Q-HOST monitor file. The only fsyncs in r2 are in the driver's execute path | 0 fsync calls in a full synthetic run (C15); unit T03 fails on baseline | UNSAFE |
| F3 | **Launch does not check existing state beyond `attempt_*` and the summary.** It starts over a leftover temporary file (S04) and over a **torn ledger tail** (S05) | matrix S04, S05: runner not refused | UNSAFE |
| F4 | **Exactly-once gap.** If the attempt directory is lost (its creation was never made durable; or it was removed), a `QUALIFICATION RUN START` row after the freeze no longer stops a launch: **a second run starts**, giving two RUN START rows | matrix S06: runner not refused, 2 start lines | UNSAFE |
| F5 | **F-DRILL-ORDER.** r2's drill topology (`p309_topology_drill.make_topology`) runs `make_freeze_manifest.py` *before* `make_freeze_params.py`. The synthetic F′ manifest therefore lacks the pin of `freeze/P309_FREEZE.json`, and the runner's own precondition `make_freeze_manifest --check` refuses. r1's real F manifest **does** pin that file. The cloud-tier drill never calls `main()`, so this has never been seen; the worker-tier drill (8d) would refuse at launch | first matrix run: all 24 cases refused at that precondition; r1 F manifest pins it | UNSAFE for the drill (rehearsal tooling, not runtime) |
| F6 | **The durability preflight is cloud-specific.** `cloud_metadata_available`, `not_spot`, `not_burstable` and `no_scheduled_maintenance` require an IMDS host and fail closed elsewhere | `code/p309_host.py` `durability_preflight` | SAFE_BUT_UNPROVEN (safe: fails closed; portability blocker) |
| F7 | **No filesystem-durability check** (tmpfs, overlay or network filesystems are not refused) | `durability_preflight` checks no mount type | SAFE_BUT_UNPROVEN |

**Already safe in r2 as shipped** (all confirmed by the matrix):
- the double-launch race (S09: `os.mkdir` decides, one attempt);
- a stale attempt directory blocks every restart (S01, C02);
- a torn record inside a prior attempt is refused (S02), and a stray summary is refused (S03);
- the Q-HOST refusal on a changed host comes before any write (S07); a mismatched commit is refused (S08);
- the real abort path gives ABORTED (C13);
- **every** restart request after **every** crash point is refused with byte-identical attempt and ledger (C02–C15,
  3 requests each);
- nothing in the runner deletes, renames or rewrites evidence.

## 2. The hardening (branch `claude/p309-r2-hardening-20261005`, one r2 file changed)

Only `level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_qualify.py` changed. AST diff against `101ef2cb`
(`evidence/AST_DIFF_RUNNER.json`):

| group | functions |
|---|---|
| added | `_fsync_dir`, `_fsync_path`, `sync_ledgers`, `_ledger_problems`, `prelaunch_state`, `attempt_start` |
| changed | `xwrite`, `run_item`, `main`, `host_rerun`, `_qhost_abort` |
| **unchanged**: all 9 functions r2's scanner pins | `git`, `run`, `qc_formal`, `research_test`, `qc_research_simple`, `mirror`, `start_qhost_monitor`, `stop_qhost_monitor`, `qhost_preflight` |
| **unchanged**: every gate function | `qc05` … `qc_d5`, `qc13`, `items_table` |

| id | change | closes |
|---|---|---|
| H1 | `xwrite`: temp file (O_EXCL) → full write → `fsync` → `os.link` to the final name (fails if it exists, so a record is never overwritten) → unlink the temp → `fsync` the directory | F1, F2 |
| H2 | `sync_ledgers()`: fsync both ledgers and their directory after the RUN START line, after every gate record, after a Q-HOST abort's line and before the summary; fsync the monitor file after the monitor is reaped | F2 (ledger and monitor) |
| H3 | `prelaunch_state()`: before Q-HOST, the attempt and the start line, refuse on any entry in `qualification/` (a prior attempt, a stray summary, a temporary file), on any ledger row that is torn, unparseable or carries a nonzero target counter, or on a start line logged at or after the freeze record (a prior run whose attempt is missing). It runs for the host re-run too. Nothing is repaired or resumed | F3, F4 |
| H4 | After the RUN START line (QC12 T14 requires it **immediately** after the attempt `mkdir`): fsync the qualification directory, sync the ledgers, then write a durable `ATTEMPT_START.json` (boot id, pid, runner sha256, launch-record sha256, retry rule) | F4 (the attempt's existence is durable); attribution of interruptions |
| H5 | The summary binds the sha256 of **every** attempt file (`attempt_files_sha256`) | crash-safe completion marker |

**Not changed, deliberately:**
- no retry, no resume, no automatic cleanup (message 1 §5B; A27; P23);
- the research ledger writer (`q309_guard.log_execution`, read-only research namespace) still appends with one
  buffered write per row. H2 makes its rows durable after the fact, and H3 refuses any torn row;
- F5 lives in drill tooling outside this branch's write-set. The proposed one-line fix is §5;
- F6 and F7 need host-level decisions (OD-R2-3/6) and are documented in `DURABLE_HOST_EXECUTION_PACKET.md` §0 and §2.

### A first version failed r2's own static check, and was fixed (disclosed)

v1 (`b609549c`) changed `stop_qhost_monitor` (one fsync line). Its AST hash then no longer matched the scanner's pin,
and the pinned `.terminate()` / `.kill()` sites became `SIGNAL_UNLISTED` (QC12 T5). v1 also placed work between the
attempt `mkdir` and the RUN START line, which QC12 T14 forbids.

v2 (`3c191ac2`) leaves `stop_qhost_monitor` byte-identical and moves the monitor fsync to its call sites. It logs RUN
START immediately after the `mkdir` and makes it durable after. It uses the registered `git()` runner. The v1 matrix
is kept as `evidence/matrix/MATRIX_HARDENED_v1_b609549c_superseded.json`.

## 3. Verification of the hardening (v2, `3c191ac2`)

| check | result | evidence |
|---|---|---|
| crash matrix (24 cases) | no crash point gives CORRUPT; torn and empty writes give INTERRUPTED (a leftover temp file only); C10 (restart in QC-D5) gives INTERRUPTED; C13 gives ABORTED; C14 gives INTERRUPTED; C15 gives COMPLETE_PASS; S04, S05 and S06 are now refused, each naming its reason; every restart is refused with bytes unchanged | `evidence/matrix/MATRIX_HARDENED_3c191ac2.json` |
| fsync ordering | in a full run: 25/25 links preceded by an fsync of their temp file and followed by a directory fsync; 42 ledger fsyncs (verified on v1 and again on v2) | matrix C15 fsync log (`matrix_hardened_v2/C15.fsync.jsonl`) |
| unit tests (positive / negative) | hardened 8/8; r2 as shipped fails exactly the 6 hardening tests and passes the 2 common ones, so the tests discriminate (T03 "the record bytes were not fsynced: []"; T04 "a torn record exists under its final name") | `evidence/unit/` |
| r2's own gates on the hardened package (post-synthetic-freeze) | see §3a | `evidence/regression/` |
| pinned functions | 9/9 unchanged | `evidence/AST_DIFF_RUNNER.json` |

### 3a. Regression against r2's own gates

Filled from `evidence/regression/REGRESSION_*.json` (the section is appended when the runs finish).

## 4. Residual risks after hardening

- **Power-loss durability is SAFE_BUT_UNPROVEN.** It relies on the filesystem honouring `fsync(file)` +
  `fsync(dir)`. No power-cut test is possible here. Mitigation: the filesystem rules in the host packet §2.
- **The attempt is still lost on any interruption.** This is by design: no resume (A27 / P23). The only mitigation
  is a durable host and an adequate window, especially for the 60–85 min QC-D5 at the end.
- **The launcher's own double-launch check** (no loaded `p309-r2-*` unit, empty scratch root) is untested here: there
  is no systemd. The runner-level race is proven safe.
- **A ledger row torn at power loss *during* an attempt** is not repaired. It makes the attempt CORRUPT on validation
  (fail closed) and blocks any later launch (H3) until the owner decides.

## 5. Proposed fix for F5 (not applied; outside the write-set; needs r2's review route)

In `code/p309_topology_drill.py`, `make_topology`, swap the first two generator calls, so that the parameters are
generated before the manifest (as in a real freeze; r1's F manifest pins `freeze/P309_FREEZE.json`):

```diff
-    gen = [run_py([sys.executable, "-B", str(code / "make_freeze_manifest.py")], clone, scratch),
-           run_py([sys.executable, "-B", str(code / "make_freeze_params.py")], clone, scratch),
+    gen = [run_py([sys.executable, "-B", str(code / "make_freeze_params.py")], clone, scratch),
+           run_py([sys.executable, "-B", str(code / "make_freeze_manifest.py")], clone, scratch),
            run_py([sys.executable, "-B", str(code / "p309_placeholder_check.py")], clone, scratch)]
```

`code/r2h_replica.py` uses this order, and with it the runner's real `make_freeze_manifest --check` passes in every
replica of this review.
