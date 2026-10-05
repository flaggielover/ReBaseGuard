# r2 adoption candidate: the delta

*Deliverable 1. The required name was `ADOPTION_CANDIDATE_DELTA.md`. The session guard refuses every path containing
"adoption" (rule R2_GRANT), and relaxing that rule was not permitted, so the file carries this neutral name.*

| | |
|---|---|
| base | r2 `101ef2cb17e5eab2892212178278da45b98004ed` (`origin/claude/p5y-k5-cell309-p309-r2`, unchanged) |
| candidate | `93d550638b8c79ae1c252fc6c2b0194b1a416b49` on `claude/p309-r2-adoption-candidate-20261005` (pushed; one commit; parent `101ef2cb`) |
| status | **candidate only**: not merged into r2, not frozen, not qualified, not adopted. No target evaluation. |

## 1. Exactly what changed

`git diff --stat 101ef2cb 93d55063` (3 files, 145 insertions, 7 deletions), all in r2's namespace
`level4/closure_proofs/p5y_k5_cell309_p309_r2/`:

| file | change | why |
|---|---|---|
| `code/p309_qualify.py` | +144 / −5 | qualification-runtime hardening H1–H5, ported mechanically from the reviewed hardening commit `3c191ac2` |
| `code/p309_topology_drill.py` | +2 / −2 | F-DRILL-ORDER: `make_topology` runs `make_freeze_params` before `make_freeze_manifest` |
| `config/SCANNER_ALLOWANCE_P309.json` | +1 / −1 | the one AST pin of `make_topology`, which the drill fix makes stale, re-pinned with r2's own `p309_scan_pins.py --refresh` |

**Not carried over** (verified: `git diff --name-only 101ef2cb 93d55063` lists only the 3 files above):
- `.claude/**`: the session guard is present in the working tree only, untracked; the guard itself refuses to commit
  it on this branch (`COMMIT_ALLOW`);
- the hardening evidence namespace `p5y_k5_cell309_p309_r2_hardening/`;
- the recovery evidence `p5y_k5_cell309_q11_recovery/`;
- session tooling, documentation and rehearsal artefacts.

These six deliverables live on the hardening branch, not on the candidate.

## 2. How the runner was ported (mechanical, not rewritten)

1. `git restore --source=3c191ac2 -- level4/…/code/p309_qualify.py`. The resulting blob `4549f70b` is identical to
   the file at `3c191ac2` and at the hardening head `ae7db324`; no r2-namespace file changed between those two
   commits.
2. One exact one-line edit restores r2's T14a anchor comment:
   ```
   -    os.mkdir(ATT["dir"])                                      # exclusive: of two racing runners exactly one passes
   +    os.mkdir(ATT["dir"])                                      # exclusive
   ```
   `git diff 3c191ac2 93d55063 -- code/p309_qualify.py` is exactly this one line.

## 3. Identity checks (by AST and by bytes; `tools/ast_full.py`)

**Runner, r2 → candidate** (`evidence/AST_RUNNER_R2_VS_CANDIDATE.json`):
- 33 → 39 top-level functions.
- **Added (6):** `_fsync_dir`, `_fsync_path`, `sync_ledgers`, `_ledger_problems`, `prelaunch_state`,
  `attempt_start`.
- **Changed (5):** `xwrite`, `run_item`, `main`, `host_rerun`, `_qhost_abort`.
- Removed: none. Changed by bytes only: none.
- Unintended changes: **none**. Every touched function is in the intended set, and every intended function was touched.
- The other 22 functions, including `items_table` and every gate function, are **byte-identical**.
- All 34 module-level statements are **byte-identical**.
- **All 9 scanner-pinned runner functions** (`process_policy.reviewed_functions` for `code/p309_qualify.py`) are
  byte-identical to r2: `git`, `run`, `qc_formal`, `research_test`, `qc_research_simple`, `mirror`,
  `start_qhost_monitor`, `stop_qhost_monitor`, `qhost_preflight`.

**Runner, hardened `3c191ac2` → candidate** (`evidence/AST_RUNNER_HARDENED_V2_VS_CANDIDATE.json`):
- 0 AST changes;
- `main` differs in bytes only (the comment);
- everything else is byte-identical.

The candidate is therefore exactly the runner that Task 2 reviewed and tested.

**Drill, r2 → candidate** (`evidence/AST_DRILL_R2_VS_CANDIDATE.json`):
- 17 → 17 functions; only `make_topology` changed;
- every other function and module-level statement is byte-identical;
- the drill's pinned `git`, `run_py`, `controls` and `main` are byte-identical.

**Allowance, r2 → candidate** (`evidence/ALLOWANCE_DIFF.json`):
- 1 228 leaves before and after;
- exactly one leaf changed: `/ref_mutation_functions[20]/ast_sha256` (`make_topology`), `9b59c12f…` → `8af1bb78…`.
  This equals `sha256(ast.dump(make_topology))` at the candidate, recomputed independently.
- `exactly_once_sites` (owner-ratified) and all other pins are unchanged.

**T14a anchors** (`evidence/ANCHORS_CANDIDATE_WT.json`): every one of the 18 mutant anchors of r2's
`tests/test_p309_static_controls.py` occurs exactly once in the candidate, including T14a's `MAIN_PRE` with
`# exclusive`.

## 4. What the runtime hardening does (H1–H5; unchanged from the Task 2 review)

| id | what | where | ordering relative to the attempt |
|---|---|---|---|
| H1 | `xwrite`: temp file (O_EXCL) → complete write → `fsync` → `os.link` to the final name (never overwrites) → unlink temp → directory `fsync` | every record and the completion marker | n/a |
| H2 | `sync_ledgers()`: fsync of both ledgers and their directory after each start line, gate record, abort and before the marker; `_fsync_path` of the Q-HOST file | `run_item`, `main`, `host_rerun`, `_qhost_abort` | after |
| H3 | `prelaunch_state()`: refuse when the qualification directory holds anything (a prior attempt, a stray summary, a temporary file), when a ledger has a torn or unparseable row or a nonzero counter, or when a RUN START line exists after the freeze record | `main`, `host_rerun` | **before** Q-HOST, the attempt directory and RUN START (refusal leaves no trace) |
| H4 | durable start: directory fsync and ledger sync after the RUN START line (keeping QC12 T14: the start line directly after the mkdir), then `ATTEMPT_START.json` (boot id, pid, runner sha256, launch-record sha256; nothing reads it to resume) | `main`, `host_rerun` | after RUN START |
| H5 | the completion marker additionally binds `attempt_files_sha256` (every attempt file) | `main` | at the end |

**What did not change:**
- no gate, gate lambda or `items_table` entry;
- no evaluator, driver, guard, generator, test, ledger or evidence;
- no retry or resume path is introduced (refusal only; msg1 §5B).

The added summary field and file are invisible to the grant check. `p309_driver.py` (lines 553–561) reads only `pass`
and `freeze_commit` from `P309_QUALIFICATION.json`, and it admits any file under the `qualification/` prefix in the
qualification commit, where `ATTEMPT_START.json` lies.

## 5. F-DRILL-ORDER

The two lines are swapped, plus the one re-pin. The full analysis and demonstration are in `F_DRILL_ORDER_REVIEW.md`.
