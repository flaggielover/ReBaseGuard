# Formal delta follow-up review 5 of P309-r2 (adoption-candidate corrections) 101ef2cb -> a119e978
FORMAL_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS

- **Reviewer:** a fresh independent reviewer. I wrote none of the r2 code, the candidate's corrections, the hardening,
  the session tooling, the S1-S3 follow-up or any earlier review. Earlier reports were read as guides only; every
  conclusion below is re-derived from git bytes or from my own recomputation.
- **Brief:** `5a0d444a:level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/formal_review_followup_5/BRIEF_FORMAL_DELTA_REVIEW_FOLLOWUP_5.md`,
  sha256 `632828707336345fb00c08cc5b921ab1ad0ebba0f5e9c34bd4dc899f3ed595a0` (recomputed: matches).
- **Workspace:** `/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t5/review/`
  (fresh `git clone --no-local --no-checkout`, checked out at the candidate, deleted at the end). Execution ledger:
  `EXEC_LEDGER.jsonl`; helpers: `led.py`, `check_index.py`, `delta_check.py`, `rehearsal_check.py`,
  `matrix_check.py`, `peek.py`.
- **Boundaries kept:** no git write to `/home/user/ReBaseGuard` (only `show`, `diff`, `log`, `ls-tree`, `cat-file`,
  `rev-parse`, `merge-base`, `for-each-ref`). The runner, the launcher, the host tool, the drill, the driver and every
  evaluator were neither run nor imported. NEW Γ309 TARGET EVALUATIONS = 0. No grant, no network. No expensive suite
  was re-run: the committed evidence was sufficient and consistent (see Q9, Q10). No TEST process is left.

## 1. Commits and ancestry (recomputed)

| item | value | how |
|---|---|---|
| base (r2) | `101ef2cb17e5eab2892212178278da45b98004ed` = `origin/claude/p5y-k5-cell309-p309-r2` | `git rev-parse` |
| candidate | `a119e9789e2a1d42b584fff8a2301946a37f1bcb` = `origin/claude/p309-r2-adoption-candidate-20261005`, tree `684d8540…` | `git rev-parse` |
| ancestry | `101ef2cb` is an ancestor of `a119e978` (rc 0); `101ef2cb..a119e978` = `93d55063`, `a119e978` (2 commits, linear) | `merge-base --is-ancestor`, `log` |
| r2 vs last accepted | `38842550..101ef2cb` = 1 commit, `ledger/CHECKPOINT_PUSHES.jsonl` +1 row (the pre-push record of the `38842550` push). **Confirmed.** | `git diff --stat` |
| follow-up 4 | `REVIEW_R2_DELTA_FOLLOWUP_4.md` line 2 = `R2_DELTA_FOLLOWUP_4_ACCEPTED`. The review is titled "at e96ed380"; `38842550` = `e96ed380` + the 3 files that preserve that review. So the reviewed content is `e96ed380`, and `38842550` adds only the review record | `git show`, `git log e96ed380..38842550` |
| evidence branch | `4b3baebd` is an ancestor of `origin/claude/p309-r2-hardening-20261005` (`5a0d444a`), which adds only the brief | `merge-base`, `diff --stat` |

## 2. Exact diff scope

`git diff --name-status 101ef2cb a119e978` (whole repository) gives exactly 4 paths, all in
`level4/closure_proofs/p5y_k5_cell309_p309_r2/`; 315 insertions, 7 deletions:

| path | status | commit |
|---|---|---|
| `code/p309_qualify.py` | M (+243/-5) | `93d55063` (H1-H5, T14a anchor), `a119e978` (S1 `_oserr`, `fs_probe` and 2 call sites) |
| `code/p309_topology_drill.py` | M (2 lines swapped) | `93d55063` |
| `config/SCANNER_ALLOWANCE_P309.json` | M (1 value) | `93d55063` |
| `governance/R2_REPIN_LIST_SUPPLEMENT_5.json` | A (73 lines) | `a119e978` |

These map one-to-one onto the brief's five in-scope items. No other file in the repository changed.

## 3. Evidence reviewed and its hashes

**Integrity of the evidence set.**
- I exported all 177 committed files under `4b3baebd:level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/` with
  `git show`.
- I recomputed every entry of `r2_candidate_followup/EVIDENCE_INDEX.json` (sha256 `7caac485…`): **58/58 sha256 and
  byte counts match**. The only committed file not indexed is the index itself.
- I also recomputed `r2_candidate/R2_CANDIDATE_EVIDENCE_MANIFEST.json` (`6db7614e…`): **64/64 match**.
- The 7 `evidence_sha256` values in `R2_FAILURE_MATRIX.json` (`a229f850…`) all match.

**Files read** (sha256 of the committed bytes):

| file | sha256 |
|---|---|
| `r2_candidate_followup/FORMAL_DELTA_REVIEW_PACKET.md` | `a379d6f7…c267` |
| `r2_candidate_followup/FILESYSTEM_PRELAUNCH_PROBE_REVIEW.md` | `3021839f…dffe` |
| `r2_candidate_followup/GOVERNANCE_REPIN_SUPPLEMENT.md` | `82585c7f…61b5` |
| `r2_candidate_followup/FINAL_R2_CANDIDATE_REVIEW.md` | `c8e1a6db…26b9` |
| `r2_candidate_followup/evidence/S1_S2_INDEPENDENT_REVIEW.md` | `e6020f07…2ed` |
| `r2_candidate_followup/evidence/REG_a119e978.json` | `d0626837…66e8` |
| `r2_candidate_followup/evidence/MATRIX_a119e978.json` / `_run2.json` | `fd5e77d3…c924` / `a849bb87…0809` |
| `r2_candidate/evidence/matrix/MATRIX_BASELINE.json` (task 3) | `d99778bf…72fe` |
| `r2_candidate_followup/evidence/FSPROBE_TESTS_a119e978.json` / `_93d55063_pre_s1.json` | `636296eb…143d7c` / `2700c60b…a533` |
| `r2_candidate_followup/evidence/UNIT_a119e978.json`, `FSYNC_ORDER_a119e978.json` | `ec90f211…40df`, `0da00e84…d459` |
| `r2_candidate_followup/evidence/rehearsal/PROVENANCE.json`, `attempt/QC15.json` | `a79826b3…8783`, `d76fdd76…e994` |
| `r2_candidate/INDEPENDENT_DELTA_REVIEW.md` | `efa43b7f…bf13` |
| `R2_FAILURE_MATRIX.json`, `R2_QUALIFICATION_HARDENING_REVIEW.md`, `OWNER_DECISIONS_OD_R2.md` | `a229f850…4f5c`, `3d2a4253…d5a1`, `c7840611…d4d5` |

**My own outputs** (`out/` and the workspace):
- `scan_pins_list.txt` `8a3de7fc…`;
- `static_check.txt` `a24362b6…`;
- `static_controls.txt` `694643a1…`;
- `scan_allowance.txt` `42044e93…`;
- `matrix_compare.txt` `50250811…`;
- `DELTA_CHECK_OUT.json` `7eb2e470…`.

**Byte identities used below:**

| file | `101ef2cb` | `93d55063` | `a119e978` |
|---|---|---|---|
| `code/p309_qualify.py` sha256 | `e9eba86f…ab8e` | `c60624b3…b024` | `36e428fb…be1d` |
| `code/p309_topology_drill.py` sha256 | `135b5e14…aef` | `ef4ce1bf…f0c1` | `ef4ce1bf…f0c1` |

## 4. Answers

### Q1. Is scientific logic unchanged? **YES**
- Only the 4 paths in §2 changed; no evaluator, verifier, generator, research module, data, test or ledger file is among them.
- The runner and the drill hold no scientific computation in the changed nodes. My own top-level AST comparison
  (`delta_check.py`) of the runner, r2 → candidate:
  - **added (8):** `_fsync_dir`, `_fsync_path`, `sync_ledgers`, `_oserr`, `fs_probe`, `_ledger_problems`,
    `prelaunch_state`, `attempt_start`;
  - **changed (5):** `xwrite`, `_qhost_abort`, `run_item`, `host_rerun`, `main`;
  - nothing removed; relative order unchanged; 62 nodes identical.
- The drill: only `make_topology` changed (52 of 53 nodes identical).
- This agrees with `AST_RUNNER_R2_VS_a119e978.json` (34/34 module-level statements identical, `intended_untouched` empty).

### Q2. Is target logic unchanged? **YES**
- The driver, guard, evaluators, mirror and decoys are byte-identical: they are outside the 4-path diff.
- The grant check reads, in `p309_driver.py` l.553-562:
  - the qualification commit may touch only the `qualification/` prefix and the two ledgers, and must contain
    `qualification/P309_QUALIFICATION.json`;
  - from that file it reads only `pass is True` and `freeze_commit == fz`.
- `ATTEMPT_START.json` lies under `qualification/attempt_1/` (or `qualification/host_rerun/<id>/`), so the prefix
  admits it.
- The `attempt_files_sha256` key is not read by the driver, by any r2 code, or by any r2 test (grep over r2 for
  `P309_QUALIFICATION`, `ATTEMPT_START` and `attempt_files_sha256` finds only the runner and the drill's existence
  check, `p309_topology_drill.py:261`).
- `pass`, `freeze_commit` and `gates` are computed exactly as in r2 (`main` l.870-873).

### Q3. Are gate semantics unchanged except fail-fast, durability and exactly-once enforcement? **YES**

**Gates.** These are AST-identical r2 → candidate (my recomputation): `items_table` and every function it reaches:
- `qc05` … `qc10`, `qc13`, `qc16`, `qc17`, `qc_u2`, `qc_d5`;
- `qc_formal`, `qc_research_simple`, `research_test`, `decoy_stage1a`;
- `ledger_append_only`, `single_run_since_freeze`, `run`, `git`, `mirror`;
- `qhost_preflight`, `start_qhost_monitor`, `stop_qhost_monitor`.

The `gates` dict and the `pass` formula (l.870-873) are unchanged. `run_item` differs only by `sync_ledgers()`
after the record (l.723), and `_qhost_abort` only by `sync_ledgers()` inside its `try` before `os._exit(3)` (l.631).

**Ordering in `main`.** Every new refusal precedes Q-HOST, the attempt directory and RUN START:

| step | line |
|---|---|
| existing-attempt check | l.832 |
| **S1** `fs_probe` | l.836 |
| **H3** `prelaunch_state` | l.840 |
| `qhost_preflight` | l.845 |
| `os.mkdir` | l.850 |
| RUN START | l.851 |

**Ordering in `host_rerun`.** The same holds:

| step | line |
|---|---|
| existing re-run check | l.750 |
| S1 | l.753 |
| H3 | l.759-766 |
| preflight | l.768 |
| mkdir | l.775 |
| HOST RERUN START | l.776 |

**After the start line.** The new statements are:
- `_fsync_dir`, `sync_ledgers` and `xwrite(ATTEMPT_START.json)`, then `mkdir evidence`, then `_fsync_dir`;
- later, `_fsync_path(QHOST file)` and `sync_ledgers`.

None is a `return`, `raise`, `assert` or exit. Their only failure mode is an `OSError` from a capability that S1
probes first.

**Static enforcement.** r2's own static check T14 enforces this ordering (`p309_static_check.py:682-717`: preflight
before mkdir, start line right after mkdir, no return / raise / exit after mkdir). It passes in my run.

**What changed in behaviour.** H3 and S1 are new pre-launch refusals; both are fail-fast. One consequence is
stricter but not a gate change: a stray `qualification/host_rerun/` before the official run. In r2 that state would
launch and fail QC13; it is now refused before anything starts.

### Q4. Is the runtime hardening justified by reproduced baseline defects? **YES**

**The baseline matrix runs the real r2 bytes.** `MATRIX_BASELINE.json` (task 3) and
`evidence/matrix/MATRIX_BASELINE_r2_101ef2cb.json` (task 2) both bind:
- package `101ef2cb`;
- runner sha256 `e9eba86f…` (= r2's `p309_qualify.py`, recomputed);
- replica tree `db04dfc9…` (= `101ef2cb^{tree}`, recomputed).

The two baseline copies agree case by case (`out/matrix_compare.txt`).

| defect | baseline evidence |
|---|---|
| CORRUPT outcomes | C04, C05, C12 classify **CORRUPT** |
| missing fsyncs | `fsync_ops` = 0 in every case, including the C15 full run. Independently, r2's runner source contains the string `fsync` 0 times |
| launch over a temporary file | S04 `runner_refused=false`, run_start_lines 1 |
| torn ledger | S05 `runner_refused=false` |
| orphan RUN START | S06 `runner_refused=false`, **2** start lines |

`R2_FAILURE_MATRIX.json` rows R01-R05, R07 and R09 cite exactly these cases. The baseline unit run fails T03-T08,
while the hardened run passes them.

### Q5. Is the filesystem pre-launch probe correctly scoped and fail-closed? **YES** (advisory notes A2, A3, A5)

**Scope.** `fs_probe` (l.151-233) exercises exactly what the hardening adds after the start line, inside
`qualification/` (the parent of every attempt directory):
- exclusive create with `O_EXCL|O_NOFOLLOW`, and its refusal of an existing name;
- a complete write (loop) and a file fsync;
- `os.link` giving a second name of the same inode (dev/ino, nlink ≥ 2, bytes read back), and its refusal of an
  existing name;
- directory fsync of the probe directory and of `qualification/`;
- `sync_ledgers()` itself, which covers both ledgers and `ledger/`.

It does not test two things the hardening did not introduce:
- the exclusive `os.mkdir` (r2's pre-existing primitive; the docstring overstates this, see A2);
- ledger appendability (SF1).

**No persistent evidence.**
- It works only in `qualification/.p309-fsprobe-<pid>/`.
- The `finally` (l.215-232) unlinks `probe.b` and `probe.a`, removes the directory and fsyncs `qualification/`.
- Cleanup failures become problems, so they are refused.
- Matrix C02 lists the probe's fsyncs, and F01 / M01 show that nothing is left.

**Leftovers.** A `.p309-fsprobe-*` entry is refused by name before the probe's `mkdir` (l.163-166). The probe only
ever removes its own just-created pid directory, so a leftover is **never removed**. No other code path removes it:
- `prelaunch_state` only lists;
- the dirty-tree check ignores `/qualification/` lines.

**Fail-closed.**
- Every `OSError` in a step becomes a problem string with the step name and errno, and any problem returns 2 before
  H3.
- A non-`OSError` exception propagates out of `main` before the preflight, so no attempt exists.
- I found no path that returns `[]` while a probed call failed. Only the inherent case remains (an fsync that
  "succeeds" on a volatile filesystem: the host requirement).

### Q6. Is F-DRILL-ORDER corrected to match the intended freeze sequence? **YES**
- **What the manifest pins.** `make_freeze_manifest.build` (l.74-105) pins every tracked or untracked file of the
  namespace under `FROZEN_DIRS = ("code","config","fc2","freeze","tests","verify","governance")`. It excludes only
  its own output `freeze/P309_FREEZE_MANIFEST.json`.
- **What the parameters write.** `make_freeze_params.py` writes `freeze/P309_FREEZE.json` (l.28, 406).
- **Why the order matters.** The manifest must be built after the parameters, or it cannot pin them and
  `--check` later differs. r2 has no committed `freeze/` (`ls-tree` is empty), so in a drill clone the order decides.
- **r1's recorded F agrees.** r1's F (`4c754a73`, "FREEZE F") has 114 code pins, and they include
  `p5y_k5_cell309_p309_r1/freeze/P309_FREEZE.json` with sha256 `b9b0f510…`. That equals the bytes of r1's
  `P309_FREEZE.json` at F (recomputed).
- **The fix.** The candidate's `make_topology` now runs params → manifest → the marker-word check (diff: two list
  elements swapped, nothing else).
- **Side effect.** One more governance file means 184 code pins at `a119e978`, against 183 at `93d55063`; both
  numbers are consistent with supplement 5's addition.

### Q7. Is the `make_topology` re-pin correctly and additively governed? **YES**
- **Both hashes recomputed** with `sha256(ast.dump(node))`, the scanner's own definition (`p309_scan.ast_sha`),
  on CPython 3.11.15 (the same version the supplement names):
  - r2: `9b59c12fa22f27226590d870315370d72bae18a57ef0b70c63217205152b92e8`;
  - candidate: `8af1bb7836674141f69a53175b094eb31092d55462bfb1b9ba2c27a0dc8dc575`.
- **Allowance file.** `57cc9a22…` → `f1780a91…`; 1228 leaves both sides; exactly **one** changed leaf,
  `/ref_mutation_functions[20]/ast_sha256`. The allowance at `101ef2cb` is byte-identical to `38842550`'s.
- **Earlier lists.** `R2_REPIN_LIST.json` (51 rows) and supplements 1-4 (48/13/10/8 rows) are byte-identical at
  `38842550`, `101ef2cb` and `a119e978`.
- **Supplement 5 is accurate.** Its rows, hashes, before/after allowance sha256, leaf counts, changed-leaf path, row
  counts of the earlier lists and `paths_changed_by_the_candidate_commit` (for `93d55063`) all match my
  recomputation. It is additive (a new file). No r2 code reads the re-pin lists (grep over `code/`, `tests/` and
  `verify/` finds no match).
- **Ruling:** **RE-PIN: ACCEPTED**.

### Q8. Do T14a and all static controls pass? **YES** (own runs at `a119e978`)

| check | result |
|---|---|
| `python3 -I -S -B code/p309_static_check.py` | rc 0; T1-T14 all PASS, including T5 formal scan and T14 Q-HOST refusals before the attempt |
| `python3 -B tests/test_p309_static_controls.py` | rc 0; **22 PASS / 0 FAIL**, including `T14a_main_preflight_after_the_attempt` |
| `python3 -B tests/test_p309_scan_allowance.py` | rc 0; 19 PASS / 0 FAIL |

**The T14a anchor.** It is `os.mkdir(ATT["dir"])` followed by the exact `# exclusive` comment (control
`MAIN_PRE`, `tests/test_p309_static_controls.py:28-34`). It occurs exactly once in the candidate (l.850). The
control fails on a missing anchor (l.110-111). The line is byte-identical to r2's l.625, so it is "restored"
relative to the hardening source `3c191ac2`, and unchanged relative to r2.

### Q9. Do QC11, QC12, QC-D5, the host tests and QC15 / A7 pass? **YES** (judged by content)

**`REG_a119e978.json`.** Bound to runner sha256 `36e428fb…` (= the candidate's runner).

| run | result |
|---|---|
| QC11 | rc 0, `qc11_table` 112 flows `all_pass` true, `failed` [] |
| QC12 | rc 0, T1-T14 PASS |
| QC-D5 controls / backstop / pins | rc 0 / rc 0 / rc 0, `pins_all_current` true |
| `test_p309_host.py`, `test_p309_host_controls.py` | rc 0, no FAIL lines |

**Rehearsal.** Bound to commit `a119e978` and tree `684d8540…` (= `a119e978^{tree}`) in `PROVENANCE.json`, whose
sha256 matches the summary's `provenance_sha256`.
- All 15 record hashes match `REHEARSAL_SUMMARY.json`.
- Every record names the synthetic freeze `1a3a6862…`, its own gate, and `pass: true`.
- QC11 PASS; QC12 PASS with T5 and T14; QC-D5 parts all true with pins all current.
- **QC15 PASS with A1-A10 all true, including `A7_formal_namespace_only_research_unchanged`.**
- The gate ledger has 17 rows, 0 with nonzero target counters.

**Binding caveat.** REG binds only the runner hash. That is sufficient here: `93d55063` → `a119e978` changes only
the runner and a governance JSON. The tree-bound rehearsal repeats QC11 / QC12 / QC-D5 / QC15, and my own QC12 /
static-control runs are on the candidate bytes.

**A7 confirmed from git.**
- 0 paths outside r2's namespace in `c902fe2f..a119e978`;
- r1 tree = `ecd1c359…`;
- 0 research changes since `eb9a9c22`;
- r5 blob `f978eeb6…`; no r6.

**Interruption.** One interrupted first run is disclosed (`REG_a119e978_ATTEMPT1_INTERRUPTED_partial.json`, the
rehearsal's `ATTEMPT1_STATUS.json` INTERRUPTED). The results used are from complete re-runs. That is consistent.

### Q10. Does the crash matrix still discriminate baseline r2 from the candidate? **YES**
- **Candidate, two runs.** Both runs on `a119e978` (runner `36e428fb…`, tree `684d8540…`) are identical case by
  case:
  - C04, C05 and C12 classify **INTERRUPTED** (never CORRUPT);
  - C15 makes 145 fsyncs and 27 links;
  - S04-S06 are **refused** (0 / 0 / 1 start lines, the 1 being the planted fixture);
  - S01-S08 are refused, and S09 has one winner.
- **Fsync ordering.** `FSYNC_ORDER_a119e978.json`: 25/25 record links ordered, and the 4 probe operations come
  before the first record link.
- **Baseline.** CORRUPT at C04 / C05 / C12, 0 fsyncs, launches over S04-S06.
- **S1 discrimination.** On `93d55063` (tree `3b2f12f5…`), M02, M03 and M05 consume the attempt; on `a119e978` they
  are refused before preflight. M01 passes on both.
- **Tool artefacts** (disclosed in task 3): C06 and C07 are vacuous for the baseline. S05 / S06 `unchanged=false`
  comes from r2's pre-existing `QDIR.mkdir(exist_ok=True)` creating an empty `qualification/`; I verified this in
  the harness, where `sha_tree` hashes `<absent>` against an empty directory.

### Q11. Are all scanner pins current? **YES**
- My run: `p309_scan_pins.py --list` gives rc 0, "P309 SCAN PINS: all current", and 0 STALE / NOT LISTED / missing
  lines.
- Every allowance pin that names a drill function (`main`, `make_topology`, `controls`) recomputes to its listed
  hash.

### Q12. Are there any unauthorized namespace changes? **NO**
- **Since `c902fe2f`:** 157 paths, all additions, 0 outside `p5y_k5_cell309_p309_r2/`.
- **Within `101ef2cb..a119e978`:** exactly the 4 in-scope paths. There is no `.claude/**`, hardening, recovery,
  evidence, ledger or test path, and no other governance file.
- **Refs:** no ref under the production namespace exists (`for-each-ref` shows only the remote-tracking branches).
- **Ledgers:** at `a119e978` the ledgers (19 / 1 / 13 rows) carry 0 nonzero target counters and end with a newline.

### Q13. SF1 ruling. **SF1: NON_BLOCKING**

**The gap is real.** I confirmed it:
- `sync_ledgers` opens the ledgers `O_RDONLY` (l.103-111, 137-144);
- no pre-mkdir step appends to the execution ledger (`make_freeze_manifest.py` does not log);
- RUN START is the first `open("a")` (`q309_guard.log_execution`, l.118-120), right after `os.mkdir(attempt_1)`
  (l.850-851).

So a ledger file the unit user cannot append to would leave `attempt_1/` without a start line. That state classifies
INTERRUPTED and, under r2 P23, ends r2.

It is **not blocking** for these reasons:
1. **It is not new.** The failure point is r2's own first post-mkdir statement, byte-identical to the state accepted
   by follow-up 4. The candidate neither introduces it nor widens it. Every failure point the candidate *adds* after
   the start line is probed, so the candidate strictly reduces the ways the single attempt can be consumed (M02,
   M03, M05).
2. **It is fail-closed.** No target is evaluated, and no PASS or grant can follow. The attempt is preserved and
   classified; nothing is retried or resumed.
3. **The exposure is narrow.**
   - The unit's `ReadWritePaths` is the whole repository (`p309_launch.py:132`). The ledgers sit next to
     `qualification/` in the same namespace, and that directory is proven writable by the probe and by
     `QDIR.mkdir`.
   - Only a per-file permission or attribute, or a nearly full volume, remains. A host-preparation step can rule
     these out.
4. **The fix is outside this delta's scope.** Fixing it here would change the probe, which needs its own
   validation.

It still deserves follow-up: see Should-fix SF1 and condition C2.

### Q14. Is the candidate acceptable for incorporation into r2? **YES**
- The candidate is technically acceptable, subject to the conditions below. No blocker was found.
- The review rules on the bytes; the adoption itself is the owner's step (C1).

## 5. Findings

**Looked for and not found:**
- a fail-open path;
- a refusal after the attempt directory;
- a silent removal of a probe leftover;
- a scientific or target change;
- an unauthorized path.

**Anything that could consume the single attempt.** Only pre-existing points remain (SF1, plus an `OSError` from an
unprobed condition such as a full disk mid-run, or a mount change between the probe and the start line).

**Implicit owner decisions.** The code embeds none:
- the probe's "remove it by hand, then launch again" concerns a pre-attempt state, where nothing was started, as for
  every Q-HOST refusal;
- supplement 5 is a record.

Incorporation itself, however, corresponds to the proposed OD-R2-H (see C1).

**Advisory notes** (none blocks; each is listed under Conditions where relevant):
- **A1. Report / bytes inconsistencies** (reports only; the bytes are correct):
  - `FINAL_R2_CANDIDATE_REVIEW.md` says "every restart refused with bytes unchanged". In fact C01 correctly allows a
    fresh start after a pre-attempt crash (the tool reports `restart.unchanged=false`), and S05 / S06 report
    `unchanged=false` (the `QDIR.mkdir` artefact above). "No CORRUPT" is true of the C cases only: S02, S03, S05 and
    S06 classify their planted states CORRUPT, by design.
  - The packet's draft brief places this review under r2's `governance/`, while the issued brief places it on the
    hardening branch. Harmless.
- **A2.** The `fs_probe` docstring says it covers what "the exclusive attempt rely on". The exclusive `os.mkdir`
  is not exercised (S1-N1).
- **A3.** An unreadable `qualification/` makes `iterdir` raise a traceback rather than a formatted refusal (S1-N3).
  The same is true of a non-object ledger row (N7). In `prelaunch_state`, a row whose `utc` has no timezone would
  raise a `TypeError` at `when >= t0` (l.280). All of these are before the attempt, so fail-closed.
- **A4.** In `prelaunch_state`'s start-line scan, a parseable row whose `utc` does not parse is skipped (l.276-279).
  Rows are written only by `log_execution`, which always stamps `utc`, and torn rows are refused separately. So
  this is theoretical, but it is the one place H3 is lenient.
- **A5.** S1-N6 untested probe branches (unlink failure, probe-mkdir EROFS / EACCES, a leftover seen by
  `host_rerun`, non-EEXIST second create / link errors).
- **A6.** N1: decoy outputs and `attempt_1/evidence/` written by subprocesses are not fsynced by the runner (H5 does
  bind the attempt's top-level files by hash). N4: the summary schema stays `P309_QUALIFICATION/2` with an added key.
  N3: the refusal text names a status validator that lives outside r2.
- **A7.** N2: the H1-H5 and S1 tests (`test_r2h_runtime.py`, `test_r2h_fsprobe.py`) live outside r2, so no r2 QC gate
  regresses the hardening. N5: earlier drill and P8 records predate F-DRILL-ORDER.

## Blockers

None.

## Should-fix

- **SF1 (non-blocking): ledger appendability is not probed.**
  - The defect: an unwritable or unappendable ledger is discovered only at RUN START, after `attempt_1/` exists.
  - Remedy (either one): the about-3-line probe extension proposed in `FORMAL_DELTA_REVIEW_PACKET.md` §5 (both
    ledgers must exist and open `O_WRONLY|O_APPEND`, no write), under its own delta review; **or** a recorded
    host-preparation check that the unit's user can append to both ledgers.
  - See condition C2.
- **SF2 (non-blocking): correct the fs_probe docstring (A2), and replace the two pre-launch tracebacks with formatted
  refusals (A3).** Do this in the same follow-up as SF1 if code is touched; otherwise advisory.

## Conditions

- **C1 — blocking-before-incorporation.**
  - Incorporate exactly the two reviewed commits, as a fast-forward of r2 from `101ef2cb` to `a119e978` (or the same
    4-path bytes). Nothing else may enter in the same step: in particular no hardening-branch file, tool or test
    (R18; QC15 A7).
  - The adoption is the owner's step. OD-R2-H is a *proposed* decision, and no answer to it is recorded in r2. This
    review supplies the technical acceptance only and does not answer OD-R2-H.
- **C2 — before-freeze.** Resolve SF1, either by the probe extension under its own delta review, or by a recorded
  host-preparation check, before the freeze. This review does not choose between the two.
- **C3 — before-freeze.** Run the worker-tier drill (8d) on the incorporated bytes so that F-DRILL-ORDER is
  exercised end to end. It regenerates the drill and P8 records that predate the fix (N5).
- **C4 — advisory.** SF2; A1 wording corrections in any future report; A4; A6 (N1, N3, N4); A7 (consider moving the
  hardening's unit and probe tests into r2 by a later reviewed delta).
- **C5 — advisory.** Power-loss durability remains SAFE_BUT_UNPROVEN. It depends on the host filesystem honouring
  fsync (ext4 / xfs; durable-host packet), which no probe can prove.

## Re-pin ruling

**RE-PIN: ACCEPTED.** It is exactly one leaf, both hashes are recomputed, the change is intended (F-DRILL-ORDER), and
it is recorded additively in `R2_REPIN_LIST_SUPPLEMENT_5.json` while supplements 1-4 stay byte-identical.

## SF1 ruling

**SF1: NON_BLOCKING** (reasons in Q13; follow-up in C2).

## Final disposition

**FORMAL_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS**

**May the candidate be incorporated into r2?** Yes, technically, as the fast-forward described in C1. The adoption
step itself rests with the owner (proposed OD-R2-H).

**Remaining non-blocking follow-ups:**
- SF1, before the freeze (C2);
- SF2 (docstring; formatted refusals);
- A1 report-wording inconsistencies;
- A4 (lenient `utc` skip in H3);
- A5 (untested probe branches);
- A6 (N1 subprocess-output fsync, N3 refusal text, N4 schema label);
- A7 (hardening tests outside r2; drill records predating the fix, regenerated by C3);
- the power-loss caveat (C5).

**Owner decisions that still gate the official qualification.** These are named from `OWNER_DECISIONS_OD_R2.md`;
none is decided here, and that document records no owner answers in r2.

| decision | subject |
|---|---|
| OD-R2-0 | (A)-(C) the record, carry-over and liabilities; **(D)** authorization of r2's freeze, its single official qualification, the qualification review and the grant-package preparation |
| OD-R2-1 / OD-R2-1b | the production namespace and its four bindings |
| OD-R2-2 | the marker and pending-result names, and the D5 extension to r2's two exactly-once sites |
| OD-R2-3 | the qualification host's access path, session and windows (8a audit / 8b verdict, then the windows) |
| OD-R2-4 | host mutations 1-5 and the unit limits, with the cell-308 operator's consent for mutation 4 |
| OD-R2-5 | the interference policy during the single attempt |
| OD-R2-6 | the target-execution host, the QC10 host re-run before any grant, and whether the freeze may name a host |
| OD-R2-H (proposed, not in the packet) | adoption of this runtime hardening into r2 |
| F-DRILL-ORDER owner action (proposed) | technically addressed by this candidate; its adoption follows OD-R2-H |

NEW Γ309 TARGET EVALUATIONS = 0. No grant. Nothing was merged, frozen or qualified by this review. Cell 309 remains OPEN.
