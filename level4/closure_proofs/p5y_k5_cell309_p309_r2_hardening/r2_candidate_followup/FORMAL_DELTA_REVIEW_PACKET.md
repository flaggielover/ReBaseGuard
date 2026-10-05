# Formal delta follow-up review packet: r2 → adoption candidate (S3)

This packet is everything r2's formal delta follow-up review needs: the exact range, the exact scope, the brief to
issue, the mandatory checks with the commands and evidence for each, and the required output form. It does **not**
perform that review.

r2's convention is that a brief "is committed before it is issued". §3 is therefore ready to be committed, as written,
as `level4/closure_proofs/p5y_k5_cell309_p309_r2/governance/BRIEF_R2_DELTA_FOLLOWUP_5.md` by whoever commissions the
review. It is not committed here, so the candidate keeps only the corrections and their record.

## 1. Range and identity

| | |
|---|---|
| last formally accepted state | `38842550` (`REVIEW_R2_DELTA_FOLLOWUP_4.md`, line 2 `R2_DELTA_FOLLOWUP_4_ACCEPTED`). r2's head `101ef2cb` adds only one ledger row (`ledger/CHECKPOINT_PUSHES.jsonl`) |
| base of the delta | r2 `101ef2cb17e5eab2892212178278da45b98004ed` (`origin/claude/p5y-k5-cell309-p309-r2`, unchanged) |
| candidate | `a119e9789e2a1d42b584fff8a2301946a37f1bcb` (`origin/claude/p309-r2-adoption-candidate-20261005`) |
| commits | `93d55063` (the hardening, T14a anchor, F-DRILL-ORDER, re-pin) and `a119e978` (S1 probe, S2 supplement) |
| files (`git diff --stat 101ef2cb a119e978`; 4 files, 315 insertions, 7 deletions) | `code/p309_qualify.py`, `code/p309_topology_drill.py`, `config/SCANNER_ALLOWANCE_P309.json`, `governance/R2_REPIN_LIST_SUPPLEMENT_5.json` (new) |

## 2. Scope: these five items and nothing else

1. `code/p309_qualify.py` durability / exactly-once hardening H1–H5:
   - `xwrite` (temp + fsync + link + directory fsync);
   - `sync_ledgers`;
   - `_ledger_problems` and `prelaunch_state` (pre-launch refusals);
   - `attempt_start` / `ATTEMPT_START.json`;
   - the `attempt_files_sha256` key of the completion marker;
   - the added `sync_ledgers()` calls in `run_item` and `_qhost_abort`.
2. The restored T14a anchor: `os.mkdir(ATT["dir"])` with the comment exactly `# exclusive` in `main`.
3. F-DRILL-ORDER: `make_topology` in `code/p309_topology_drill.py` runs params → manifest → placeholder check.
4. The one intentional scanner re-pin: `ref_mutation_functions[20]` `make_topology`, `9b59c12f…` → `8af1bb78…`,
   recorded in `governance/R2_REPIN_LIST_SUPPLEMENT_5.json`.
5. The filesystem pre-launch probe from S1: `_oserr`, `fs_probe` and its two call sites (`main`, `host_rerun`).

**Out of scope:**
- every other r2 file;
- owner decisions OD-R2-0..6;
- host selection;
- the worker-tier drill and the freeze.

These are named only so the reviewer can confirm they are untouched.

## 3. The brief (to be committed verbatim as `governance/BRIEF_R2_DELTA_FOLLOWUP_5.md`, then issued)

---

# Brief: fifth focused follow-up of the r2 delta review (adoption-candidate corrections)

This brief is committed before it is issued.

## Who and what

**Recipient.** A **fresh** independent reviewer. You wrote none of these:
- the r2 code, its repairs, or these corrections;
- the hardening, the session tooling, or any review of them;
- any earlier r2 review.

**Boundaries.** As in the earlier briefs:
- no git write of any kind;
- NEW Γ309 TARGET EVALUATIONS = 0: never run `p309_driver.py execute`, `seal-only` or `validate-grant`, nor anything
  that could read a target input;
- no cell-305–309 values;
- no cell-307/308 file contents or hashes;
- no decoy outputs opened;
- no network;
- scratch runs only under your own scratchpad, with `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR` pointed
  there;
- every TEST process you start carries a random token, is killed by you, and none is left at the end.

Do not run the runner's `main()` with real gates, the launcher, or the drill. Write your execution ledger and your
review file incrementally.

**What you review.** The committed bytes on branch `claude/p309-r2-adoption-candidate-20261005` over the range
`101ef2cb..a119e978` (= `38842550..a119e978` minus one ledger row), in r2's namespace only. Guides, never evidence:
- the reports and evidence under `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/r2_candidate/` and
  `…/r2_candidate_followup/` on branch `claude/p309-r2-hardening-20261005`;
- the earlier independent delta review there (`INDEPENDENT_DELTA_REVIEW.md`), whose findings S1–S3 these corrections
  answer.

Verify from git and by recomputation.

## The five items in scope (nothing else)

1. the `p309_qualify.py` durability / exactly-once hardening (H1–H5);
2. the restored T14a anchor `# exclusive`;
3. F-DRILL-ORDER in `make_topology`;
4. the one intentional scanner re-pin (`make_topology`), with `governance/R2_REPIN_LIST_SUPPLEMENT_5.json`;
5. the filesystem pre-launch probe (`fs_probe`).

## What to verify (every item, each with your own evidence)

1. **Scientific logic unchanged.** No file outside the four in the range changed, and none of them holds scientific
   computation.
2. **Target logic unchanged.**
   - The driver, guard, evaluators, mirror, decoys and the grant chain are byte-identical.
   - The completion marker's added key and `ATTEMPT_START.json` do not alter what the grant check reads
     (`p309_driver.py`: `pass`, `freeze_commit`, the `qualification/` prefix).
3. **Gate semantics unchanged except fail-fast / durability enforcement.**
   - `items_table`, every gate function, the `gates` dict and the `pass` formula are unchanged.
   - Every new refusal comes before Q-HOST, the attempt directory and RUN START (or HOST RERUN START).
   - Every new statement after RUN START is a durability step whose capabilities `fs_probe` proves first.
4. **Scanner pins valid.**
   - `code/p309_scan_pins.py --list` reports "all current".
   - The allowance differs from `101ef2cb` in exactly one leaf; recompute `sha256(ast.dump(make_topology))` yourself.
   - The 9 reviewed runner functions are byte-identical.
   - `R2_REPIN_LIST.json` and supplements 1–4 are byte-identical; supplement 5 is additive and accurate.
5. **T14a PASS.** `tests/test_p309_static_controls.py` gives 22/22, with T14a detected.
6. **QC15 / A7 PASS.** `code/p309_self_audit.py QUALIFICATION` on a synthetic-freeze replica gives A1–A10 true. A7:
   0 paths outside r2's namespace since `c902fe2f`, r1 tree `ecd1c359`, research unchanged since `eb9a9c22`.
7. **QC11 / QC12 / QC-D5 PASS.** QC11 112/112; QC12 incl. T5 and T14; QC-D5 controls, backstop and pins.
8. **The crash matrix still discriminates** baseline r2 from the candidate:
   - r2 is CORRUPT at C04/C05/C12, makes 0 fsyncs, and launches over S04–S06;
   - the candidate never ends CORRUPT, refuses S04–S06, and orders its record links;
   - the S1 tests show the pre-S1 runner consuming the attempt on an unsupported filesystem, while the candidate refuses.
9. **No unauthorized namespace changes.** Exactly the four paths above, all in r2's namespace. No `.claude/**`,
   hardening, recovery, evidence, ledger or test path. No other governance file changed.
10. **No target evaluation or grant.**
    - The candidate and every ledger row carry 0 target counters.
    - There is no grant or result file and no protected ref.
    - r5 is unchanged (`f978eeb6…`) and there is no r6.

Look also for: a fail-open path; a refusal after the attempt directory; a probe leftover that could block or be
removed silently; anything that would consume the single attempt; an implicit owner decision.

## Output

**`governance/REVIEW_R2_DELTA_FOLLOWUP_5.md`.** Line 2 is exactly one of:
- `R2_DELTA_FOLLOWUP_5_ACCEPTED`, with a section headed exactly `## Conditions` (it may be empty);
- `R2_DELTA_FOLLOWUP_5_REJECTED`, with reasons.

Mark each condition **blocking-before-owner-decisions**, **before-freeze**, or **advisory**. Avoid the words that
`code/p309_placeholder_check.py` flags.

**Also:** `governance/REVIEW_R2_DELTA_FOLLOWUP_5.sha256` (the review's sha256) and your execution ledger, kept with
the review as in follow-ups 1–4.

---

## 4. How each mandatory check can be reproduced (commands and existing evidence)

Every command runs in a **scratch clone** of `a119e978` with `P309_SCRATCH_ROOT` / `P309_EVIDENCE_DIR` / `TMPDIR` in
scratch. Evidence paths are on the hardening branch: `r2_candidate/` (task 3, at `93d55063`) and
`r2_candidate_followup/` (task 4, at `a119e978`).

| # | check | command | existing evidence (at `a119e978` unless noted) |
|---|---|---|---|
| 1, 2 | scientific / target logic unchanged | `git diff --name-only 101ef2cb a119e978`; AST comparison of every top-level node | `evidence/AST_RUNNER_R2_VS_a119e978.json`, `evidence/AST_RUNNER_93d55063_VS_a119e978.json`, `r2_candidate/evidence/AST_DRILL_R2_VS_CANDIDATE.json` |
| 3 | gate semantics; refusals before the attempt | `python3 -B code/p309_static_check.py` (T14) | `evidence/FAST_CHECKS_a119e978.json`; `FILESYSTEM_PRELAUNCH_PROBE_REVIEW.md` §3 |
| 4 | scanner pins | `python3 -B code/p309_scan_pins.py --list`; `tests/test_p309_scan_allowance.py` | `evidence/FAST_CHECKS_a119e978.json`, `evidence/ALLOWANCE_DIFF_R2_VS_a119e978.json`, `GOVERNANCE_REPIN_SUPPLEMENT.md` |
| 5 | T14a | `python3 -B tests/test_p309_static_controls.py` | `evidence/FAST_CHECKS_a119e978.json`, `evidence/ANCHORS_a119e978.json`, regression |
| 6 | QC15 / A7 | rehearsal QC15 record | `evidence/rehearsal/attempt/QC15.json` |
| 7 | QC11 / QC12 / QC-D5 | `r2h_regression.py` (r2's own tests, as the runner defines them) | `evidence/REG_a119e978.json` |
| 8 | crash matrix + S1 discrimination | `tests/r2h_crash_matrix.py run` (candidate and baseline); `tests/test_r2h_fsprobe.py run --label s1 / pre_s1` | `evidence/MATRIX_a119e978.json` (+ `_run2`), `r2_candidate/evidence/matrix/MATRIX_BASELINE.json`, `evidence/FSPROBE_TESTS_*.json`, `evidence/FSYNC_ORDER_a119e978.json`, `evidence/UNIT_a119e978.json` |
| 9 | namespaces | `git diff --name-only c902fe2f a119e978` (0 outside r2) | `FINAL_R2_CANDIDATE_REVIEW.md` §integrity |
| 10 | no target evaluation / grant | counters over every ledger row and repository | `evidence/integrity/INTEGRITY_COUNT.json`, `evidence/integrity/SESSION_AUDIT_SNAPSHOT.json` |

## 5. Known items the reviewer should rule on (disclosed in advance)

These come from the task-3 review's notes. None is a correction in this range; the reviewer decides whether any becomes
a condition.

| id | item |
|---|---|
| N1 | subprocess-written evidence (decoy outputs, `attempt_1/evidence/`) is not fsynced by the runner |
| N2 | the H1–H5 and S1 tests live outside r2 (hardening namespace), so no QC gate runs them |
| N3 | the refusal text names a "status validator" that lives outside r2 |
| N4 | the completion-marker schema label stays `P309_QUALIFICATION/2` despite the added key |
| N5 | the earlier drill and P8 records predate F-DRILL-ORDER; the next worker-tier drill regenerates them (F′ now has 184 code pins) |
| N7 | a non-object ledger row makes `prelaunch_state` raise (before launch) instead of refusing |
| power loss | durability across a power cut depends on the filesystem (ext4 / xfs host requirement); no probe can prove it |
| S1-SF1 | (independent S1/S2 check, non-blocking) `fs_probe` does not prove the ledgers are **appendable**. RUN START, r2's pre-existing first append, follows the attempt mkdir, so an unwritable ledger would still consume the attempt. Proposed fix if the review wants it: about 3 lines in `fs_probe` requiring both ledgers to exist and open `O_WRONLY|O_APPEND` (no write) |
| S1-N1 | the exclusive `os.mkdir` of the attempt is not exercised by the probe (POSIX-exclusive; relied on since before the hardening); the docstring overstates this |
| S1-N3 | an unreadable `qualification/` makes the probe's listing raise (a traceback before the start line) instead of a formatted refusal |
| S1-N6 | probe paths without a test: unlink failure, probe-directory mkdir EROFS/EACCES, a leftover in `host_rerun`, non-EEXIST errors on the second create/link |
