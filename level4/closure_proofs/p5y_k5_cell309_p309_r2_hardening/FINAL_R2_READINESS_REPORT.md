# Final r2 readiness report

**Verdict: R2_HARDENING_REQUIRED**

**NEW Γ309 TARGET EVALUATIONS = 0.** No target quantity of cells 306–309 was evaluated. No grant was issued or
consumed. Nothing was adopted and no scientific status changed. r5 is unchanged (`f978eeb6`) and there is no r6. r2
(`101ef2cb`) is unmodified on origin. Cell 309 remains OPEN.

## Starting state (verified, not assumed)

| ref | commit |
|---|---|
| `origin/claude/p5y-k5-cell309-p309-r2` | `101ef2cb` (unchanged at the end) |
| `origin/claude/p309-q11-recovery-20261005` | `290b6c10` (unchanged at the end) |
| `origin/claude/p5y-k5-cell309-p309-r1` / `origin/main` | `c902fe2f` / `1cb45382` (unchanged) |
| protected refs on origin | none, at the start and at the end |

Work branch: `claude/p309-r2-hardening-20261005`, created from `101ef2cb`. It changes one r2 file
(`code/p309_qualify.py`) and adds `.claude/**` (the enforced session guard) and the namespace
`level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/`.

## Deliverables (this namespace)

| # | deliverable | file |
|---|---|---|
| 1 | owner decision aid, OD-R2-0..6 (recommendations only) + proposed OD-R2-H and the F-DRILL-ORDER action | `OWNER_DECISIONS_OD_R2.md` |
| 2 | hardening review | `R2_QUALIFICATION_HARDENING_REVIEW.md` |
| 3 | failure matrix (18 rows, each classification derived from evidence files) | `R2_FAILURE_MATRIX.json` (generator `tests/r2h_make_failure_matrix.py`) |
| 4 | hardening code and tests | `code/p309_qualify.py` in r2's namespace (H1–H5); `code/r2h_validator.py`, `code/r2h_replica.py`, `code/r2h_rehearse.py`; `tests/r2h_crash_matrix.py`, `tests/test_r2h_runtime.py`, `tests/r2h_regression.py`, `tests/r2h_ast_diff.py` |
| 5 | result-free rehearsal design + tool | `FULL_RESULT_FREE_REHEARSAL.md`, `code/r2h_rehearse.py` |
| 6 | durable-host execution packet | `DURABLE_HOST_EXECUTION_PACKET.md` |
| 7 | this report | `FINAL_R2_READINESS_REPORT.md` |

## What r2 as shipped is (from `R2_FAILURE_MATRIX.json`)

**UNSAFE: real defects in the qualification runtime, each reproduced against r2's real runner with crash injection:**
- **R01** non-atomic record and completion-marker writes: torn or empty records, classified CORRUPT;
- **R02 / R03** no fsync on evidence or on directories (0 fsyncs in a full run);
- **R04** ledger appends neither fsynced nor checked;
- **R05** a launch proceeds over a torn ledger;
- **R07** a second run starts over an orphan RUN START;
- **R09** a launch proceeds over a leftover temporary file;
- **R15** F-DRILL-ORDER: the worker-tier drill would refuse at launch.

**Already safe:**
- double launch, stale lock, a crash between artifact and ledger, and a crash between ledger and marker;
- a restart in QC-D5 (fail closed, never resumed);
- host-identity refusal;
- no path mutates preserved evidence;
- every restart after every crash point is refused with bytes unchanged.

## What the hardening achieves, and why it is not yet adoptable

**Achieved** (on `3c191ac2`):
- **Crash matrix:** no crash point yields CORRUPT any more. Launches over a temporary file, a torn ledger or an orphan
  RUN START are refused.
- **fsync ordering:** 25/25 links are preceded by an fsync of their temp file and followed by a directory fsync.
- **Unit tests:** 8/8 pass, and they discriminate: r2 as shipped fails exactly the 6 hardening tests.
- **Pinned functions:** all 9 scanner-pinned runner functions and every gate function are unchanged.
- **r2's own gates are unchanged:** QC11 (112/112), QC12, QC-D5 (controls, backstop, pins all current) and the host
  tests.

**Not yet adoptable:**
- **R17:** the hardened package fails r2's own static control **T14a**. Its anchor contains the comment
  `# exclusive`, which the hardening extended. T14 itself is intact, but r2's suite fails. Required fix: restore the
  comment. It is not applied here: the instruction was to change nothing more once the runs had started, and this
  result is interpretable.
- **R18:** QC15's A7 fails on the branch as packaged. Adoption must be the **single file** onto r2, never a merge of
  this branch.
- r2's governance requires a **delta review** of any change before the freeze, and a re-drill.
- The power-loss durability of the hardened writes is **SAFE_BUT_UNPROVEN** (it depends on the filesystem; host
  packet §2).

## F-DRILL-ORDER

**Intentionally left for owner action, and still blocking for r2's worker-tier (8d) drill.**
- It is not fixed on this branch: the drill tool is outside the runtime-hardening write-set.
- It does not affect the qualification runtime or a real freeze, and the result-free rehearsal tool uses the correct
  order.
- The one-line fix is in `R2_QUALIFICATION_HARDENING_REVIEW.md` §5. The recommendation is to review it together with
  OD-R2-H.

## Why this verdict and not another

- **Not R2_READY_FOR_DURABLE_HOST_QUALIFICATION:** owner decisions OD-R2-0 (D) and OD-R2-3..5 are open; P0.2–P0.5
  of the host packet are open; and the package to qualify is not settled.
- **Not R2_READY_FOR_OWNER_DECISIONS:** the owner could decide OD-R2-0 (A)–(C), -1, -2, -5 and -6's deferral now.
  But the decision that matters, OD-R2-0 (D) (authorize the single attempt), should not be taken on r2 as shipped,
  which has the UNSAFE defects above. The hardening that removes them still needs the T14a comment fix and r2's
  delta review. Calling r2 "ready" would overstate it.
- **Not R2_BLOCKED:** nothing prevents progress. Every remaining item has a concrete, small, known path:
  - the comment fix;
  - the single-file delta and its review;
  - the drill-order fix;
  - the owner decisions;
  - a durable host (with IMDS, or a reviewed portability change).
- **Therefore R2_HARDENING_REQUIRED.** r2 needs its qualification runtime hardened before any durable-host
  qualification. The hardening is implemented and verified here, and it needs one comment-level correction plus
  r2's own review route before adoption.

## Integrity confirmation (independent of this report's author)

- **origin:** r2 `101ef2cb`, recovery `290b6c10`, r1 `c902fe2f` and main `1cb45382` are unchanged, with 0 protected
  refs.
- **this branch vs r2:** only `.claude/**` (8), the hardening namespace, and `p309_qualify.py` changed. No r2
  evidence, ledger, governance, test or other code changed. r5 is unchanged; there are 0 r6 files and 0 grant or
  result files added.
- **scratch:** 424 repositories scanned. The only protected refs are the frozen harness's own F23 TEST fixture
  (`refs/rlr-tail/x`, 4 sandboxes). 24,829 ledger rows were scanned, with 0 nonzero target counters. There are no
  grant files outside TEST sandboxes.
- **session audit** (`audit/SESSION_AUDIT_SNAPSHOT.json`, from the hook logs): target evaluations 0; the guard
  refused 15 calls by rule (canaries, conservative refusals of commands naming refused tools, history and remote
  rules).
- **One tripwire event, disclosed:** at 05:21:33Z my own policy edit made the tripwire report "HEAD is on the recovery
  branch, not the hardening branch". This was the moment between re-scoping the guard and creating the branch. No
  protected state changed.

## Next permitted actions (none of them is a target evaluation)

1. **Engineering (any session, result-free):** prepare the single-file delta onto r2 (`code/p309_qualify.py` from
   `3c191ac2` with `# exclusive` restored) together with the F-DRILL-ORDER one-line fix, re-run
   `tests/r2h_regression.py` (expect `test_p309_static_controls.py` rc 0) and the crash matrix, and write r2's
   delta-review brief.
2. **Owner:**
   - answer OD-R2-0 (A)–(C), OD-R2-1, OD-R2-2 and OD-R2-5;
   - approve the OD-R2-3 audit access;
   - request the cell-308 operator's data (OD-R2-4);
   - decide OD-R2-H and the F-DRILL-ORDER action, which means commissioning the delta review;
   - defer OD-R2-6's host.
3. **Only after those:** the 8a audit on the chosen host, a `--gates all --require-durable-host` rehearsal, the
   worker-tier drill, and then, with OD-R2-0 (D), the freeze and the single official attempt
   (`DURABLE_HOST_EXECUTION_PACKET.md`).

**Stop.** No formal qualification, no freeze and no Γ309 evaluation was started.
