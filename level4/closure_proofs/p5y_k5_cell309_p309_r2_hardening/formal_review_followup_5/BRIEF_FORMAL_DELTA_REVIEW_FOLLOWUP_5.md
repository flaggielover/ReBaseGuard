# Brief: formal delta follow-up review 5 of r2 (adoption-candidate corrections)

This brief is committed before it is issued. It follows `FORMAL_DELTA_REVIEW_PACKET.md` (S3) and r2's earlier follow-up
briefs (`governance/BRIEF_R2_DELTA_FOLLOWUP_4.md`). Because the candidate and r2 may not be modified, the record is kept
on branch `claude/p309-r2-hardening-20261005` under
`level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/formal_review_followup_5/`.

## Who and what

**Recipient.** A **fresh** independent reviewer. You wrote none of these:
- the r2 code or its repairs;
- the candidate's corrections, the hardening, the session tooling or the S1–S3 follow-up;
- any earlier review of them.

Earlier reviews and reports are **guides, never evidence**. Re-derive every conclusion from git and from your own
recomputation.

**Boundaries:**
- No git write of any kind to `/home/user/ReBaseGuard`: no commit, checkout, branch change, stash, reset or push. Use
  only `git show`, `diff`, `log`, `ls-tree`, `cat-file`, `rev-parse` and `merge-base`, and file reads.
- NEW Γ309 TARGET EVALUATIONS = 0. Never run or import `p309_driver.py` (in any mode), `p309_qualify.py`,
  `p309_launch.py`, `p309_host.py`, `p309_topology_drill.py` or any evaluator.
- No cell-305–309 values; no cell-307/308 file contents or hashes; no decoy outputs opened; no network; no grants.
- Your own work goes only in a **fresh** workspace,
  `/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t5/review/`:
  - a fresh `git clone --no-local --no-checkout` of the session repository, checked out at the candidate;
  - `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR` pointed there.
- You may run r2's own **cheap static** tools in that clone: `code/p309_static_check.py`,
  `code/p309_scan_pins.py --list`, `tests/test_p309_static_controls.py`, `tests/test_p309_scan_allowance.py`.
  Do **not** re-run the expensive suites (QC11, QC-D5 controls, the rehearsal, the crash matrix) unless the existing
  evidence is insufficient or inconsistent; if you do, say why. Every TEST process you start is yours to kill, and none
  may be left at the end.
- Write your execution ledger (`EXEC_LEDGER.jsonl`, one JSON row per command: utc, command, purpose, rc) and your
  review incrementally.

## What you review

**The delta.** Exactly `101ef2cb17e5eab2892212178278da45b98004ed` (r2, `origin/claude/p5y-k5-cell309-p309-r2`) →
`a119e9789e2a1d42b584fff8a2301946a37f1bcb` (candidate, `origin/claude/p309-r2-adoption-candidate-20261005`), in r2's
namespace `level4/closure_proofs/p5y_k5_cell309_p309_r2/`.
- r2 `101ef2cb` differs from `38842550` (accepted by follow-up 4, `governance/REVIEW_R2_DELTA_FOLLOWUP_4.md` line 2) by
  one ledger row. Confirm this.

**Scope: these five items, nothing else:**
1. `code/p309_qualify.py` durability / exactly-once hardening H1–H5:
   - `xwrite`, `sync_ledgers`, `_ledger_problems`, `prelaunch_state`, `attempt_start` / `ATTEMPT_START.json`;
   - the `attempt_files_sha256` marker key;
   - the `sync_ledgers()` calls in `run_item` and `_qhost_abort`.
2. The restored T14a anchor: `os.mkdir(ATT["dir"])` with the comment exactly `# exclusive`.
3. F-DRILL-ORDER: `make_topology` in `code/p309_topology_drill.py` runs params → manifest → placeholder check.
4. The intentional `make_topology` scanner re-pin (`config/SCANNER_ALLOWANCE_P309.json`) and its additive record
   `governance/R2_REPIN_LIST_SUPPLEMENT_5.json`.
5. The filesystem pre-launch probe: `_oserr`, `fs_probe` and its call sites in `main` and `host_rerun`.

**Evidence you must read and check for consistency.** It is on branch `claude/p309-r2-hardening-20261005` at
`4b3baebd` (read it with `git show 4b3baebd:<path>`), under `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/`:
- `r2_candidate_followup/`, the S1–S3 follow-up at `a119e978`:
  - `FORMAL_DELTA_REVIEW_PACKET.md`, `FILESYSTEM_PRELAUNCH_PROBE_REVIEW.md`, `GOVERNANCE_REPIN_SUPPLEMENT.md`,
    `FINAL_R2_CANDIDATE_REVIEW.md`;
  - `evidence/` (S1/S2 independent review, regression, rehearsal, matrix, fsprobe tests, unit tests, AST, allowance
    diff, anchors, fast checks, integrity), `tools/`, `EVIDENCE_INDEX.json`.
- `r2_candidate/`, task 3 at `93d55063`: the delta, validation, F-DRILL-ORDER review, the first independent delta
  review, and evidence including the baseline r2 matrix and unit tests.
- Task 2's records: `R2_FAILURE_MATRIX.json` (the reproduced baseline defects), `R2_QUALIFICATION_HARDENING_REVIEW.md`
  and `OWNER_DECISIONS_OD_R2.md`.
- Check that the `EVIDENCE_INDEX.json` sha256 values match the committed files.

## Questions you must answer explicitly

Answer each with **YES / NO / PARTLY** and your own evidence (file:line, command and output, hashes):

1. Is scientific logic unchanged?
2. Is target logic unchanged? (The driver, guard, evaluators, mirror and decoys are byte-identical. Do the added marker
   key and `ATTEMPT_START.json` leave what the grant check reads, in `p309_driver.py`, unaffected?)
3. Are gate semantics unchanged except for fail-fast, durability and exactly-once enforcement? (Check `items_table`,
   every gate function, the `gates` dict and the `pass` formula. Does every new refusal precede Q-HOST, the attempt
   directory and RUN START / HOST RERUN START?)
4. Is the runtime hardening technically justified by reproduced baseline defects? (Does the baseline matrix evidence
   show CORRUPT outcomes, missing fsyncs and launches over a temp file, a torn ledger or an orphan RUN START, for the
   real r2 runner bytes?)
5. Is the filesystem pre-launch probe correctly scoped and fail-closed? (Does it check exactly the hardening's
   capabilities? Does it leave no persistent evidence? Does it refuse a leftover precisely and never remove one?)
6. Is F-DRILL-ORDER corrected to match the intended freeze sequence? (Read `make_freeze_manifest.build`,
   `FROZEN_DIRS` / `EXCLUDE` and `make_freeze_params`, and r1's recorded F manifest.)
7. Is the `make_topology` re-pin correctly and additively governed? (Recompute both hashes. Is exactly one allowance
   leaf changed? Are `R2_REPIN_LIST.json` and supplements 1–4 byte-identical? Is supplement 5 accurate?)
8. Do T14a and all static controls pass?
9. Do QC11, QC12, QC-D5, the host tests and QC15 / A7 pass? (Check the content of the results, not only exit codes,
   and check that each result is bound to `a119e978`'s bytes.)
10. Does the crash matrix still discriminate baseline r2 from the candidate?
11. Are all scanner pins current?
12. Are there any unauthorized namespace changes? (Since `c902fe2f`, and within `101ef2cb..a119e978`.)
13. **SF1 ruling.** The probe does not test ledger appendability. RUN START, r2's pre-existing first ledger append,
    follows the attempt mkdir, so an unwritable ledger would fail immediately after the attempt is created. Rule
    exactly **BLOCKING** or **NON_BLOCKING**, with reasons. Do not fix it.
14. Is the candidate acceptable for incorporation into r2?

Also look for:
- a fail-open path;
- a refusal after the attempt directory;
- anything that could consume the single attempt;
- a probe leftover that could be removed silently;
- an implicit owner decision;
- any inconsistency between the reports and the bytes.

## Output

Write `REVIEW_FORMAL_DELTA_FOLLOWUP_5.md` in your workspace. Line 1 is the title. **Line 2 is exactly one of:**
- `FORMAL_DELTA_REVIEW_ACCEPTED`
- `FORMAL_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS`
- `FORMAL_DELTA_REVIEW_REJECTED`
- `FORMAL_DELTA_REVIEW_BLOCKED`

It must contain:
- the exact base and candidate commits, with ancestry recomputed;
- the exact diff scope;
- the evidence reviewed, with its hashes;
- answers 1–14 with evidence;
- findings;
- a section headed exactly `## Blockers` (may be empty);
- a section headed exactly `## Should-fix` (may be empty);
- the SF1 ruling (`SF1: BLOCKING` or `SF1: NON_BLOCKING`);
- the re-pin ruling (`RE-PIN: ACCEPTED` or `RE-PIN: REJECTED`);
- a section headed exactly `## Conditions`, with each condition marked **blocking-before-incorporation**,
  **blocking-before-owner-decisions**, **before-freeze** or **advisory**;
- the final disposition.

**If accepted, state explicitly:**
- whether the candidate may be incorporated into r2;
- which non-blocking follow-ups remain;
- which owner decisions still gate the official qualification. Read `OWNER_DECISIONS_OD_R2.md`; name them, but do not
  decide them.

Avoid the words that `code/p309_placeholder_check.py` flags (TBD, TODO, FIXME, XXX, "placeholder", "to be decided",
"open question", "undecided", "owner decides", "may be chosen", "depending on the result").
