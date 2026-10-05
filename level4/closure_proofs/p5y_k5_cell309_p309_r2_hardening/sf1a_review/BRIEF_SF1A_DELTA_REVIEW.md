# Brief: scoped delta review of SF1-A (ledger appendability in the r2 pre-launch probe)

This brief is committed before it is issued. It is written so that it can be filed verbatim in r2's `governance/` later.

## Who and what

**Recipient.** A **fresh** independent reviewer. You wrote none of:
- the r2 code, its hardening, the S1 probe or this SF1-A change;
- the session tooling;
- any earlier review of them.

Earlier reports are guides, never evidence: verify from git and from your own recomputation.

**Authority.** The owner chose SF1-A in `governance/OWNER_DECISIONS_R2_MSG5_VERBATIM.md` (r2 `b66a45f0`), quoted
verbatim:

> "SF1
> SELECT SF1-A.
> Resolve ledger appendability by extending the pre-launch probe under a narrowly scoped reviewed delta before the
> worker-tier drill.
> This authorization is limited to the minimal SF1 probe extension and its required tests/review.
> It does not authorize unrelated hardening."

SF1 itself is the formal delta follow-up review 5's should-fix SF1 and condition C2 (before-freeze), in
`governance/REVIEW_R2_DELTA_FOLLOWUP_5.md` and `governance/R2_DELTA_FOLLOWUP_5_RECORD.md` (r2 `b66a45f0`).

**Boundaries:**
- **No git write** to `/home/user/ReBaseGuard`. Use only `git show`, `diff`, `log`, `ls-tree`, `cat-file`,
  `rev-parse` and `merge-base`.
- **NEW Γ309 TARGET EVALUATIONS = 0.** Never run or import `p309_driver.py`, the runner, the launcher, the host tool,
  the drill or any evaluator.
- **No** cell values, decoy outputs, network or grants.
- **Fresh workspace only:**
  `/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t7/sf1a_review/work/`.
  Use a fresh no-local clone checked out at the SF1-A commit, with `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and
  `TMPDIR` pointed there.
- **Tools you may run:** r2's cheap static tools only (`code/p309_static_check.py`, `code/p309_scan_pins.py --list`,
  `tests/test_p309_static_controls.py`, `tests/test_p309_scan_allowance.py`).
- **Ledger:** write an execution ledger (one JSON row per command) incrementally.

## What you review

**The delta.** Exactly `b66a45f097989764176075802c953df4b72c2aef` (r2's head: the accepted candidate `a119e978`, plus
one governance-only commit) → `716946e8d9a6744d0b49de6acc802605b6eb1bf8` (branch
`origin/claude/p309-r2-sf1a-20261005`), in `level4/closure_proofs/p5y_k5_cell309_p309_r2/`.

The change is three lines in `fs_probe`, in `code/p309_qualify.py`. After `sync_ledgers()`, both ledgers must exist
and open `O_WRONLY|O_APPEND|O_NOFOLLOW`, with nothing written, or the probe reports a problem naming the ledger, the
step and the errno.

**Evidence.** This is on branch `claude/p309-r2-hardening-20261005`, under
`level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/sf1a_review/evidence/` once committed; until then it is in
`/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t7/ev/`. Check every result's
binding to the commit and the runner bytes.
- `FSPROBE_TESTS_716946e8_s1a.json`: all of F01–F15 and M01–M06 pass.
- `FSPROBE_TESTS_b66a45f0_pre_s1a.json`: on the runner without SF1-A, F14, F15 and M06 fail. M06 records the attempt
  being consumed.
- `MATRIX_716946e8.json`: the crash matrix.
- `UNIT_716946e8.json`.
- `AST_RUNNER_b66a45f0_VS_716946e8.json`.
- `FAST_CHECKS_716946e8.json`: QC12, static controls, pins, scan-allowance, the unresolved-marker check (`code/p309_placeholder_check.py`), manifest and QC15.
- `REG_716946e8.json`: QC11, QC12, QC-D5, host tests, static controls.
- The light rehearsal of `716946e8`.

The test tool is `tests/test_r2h_fsprobe.py` (hardening namespace). Its earlier version is the one the formal review
read.

## Questions you must answer (YES / NO / PARTLY, each with your own evidence)

1. Is the delta exactly the SF1-A probe extension, and nothing else (one file; only `fs_probe` changes)?
2. Does it check the capability SF1 names: the ledgers exist and can be opened for appending, before Q-HOST, the
   attempt directory and RUN START (and HOST RERUN START), in both `main` and `host_rerun`?
3. Is it fail-closed and precise? Consider:
   - a missing ledger, a read-only or unappendable ledger, and a ledger that is a symbolic link (`O_NOFOLLOW`);
   - an exception that escapes;
   - an open that succeeds while a later append would still fail. If any such case remains, say so and judge it.
4. Does it write or persist anything? Consider ledger bytes, mtime, and probe leftovers.
5. Are scientific logic, target logic and gate semantics unchanged? Are all scanner pins current and the 9 pinned
   runner functions byte-identical? Do T14a and the static controls pass?
6. Do QC11, QC12, QC-D5, the host tests and QC15 / A7 pass? Judge by content, bound to `716946e8`.
7. Does the crash matrix still discriminate baseline r2 (`101ef2cb`) from this runner, unchanged from `a119e978`?
8. Do the new tests (F14, F15, M06) discriminate? Is M06's fault model (`os.open` and the ledger writer's
   `Path.open`) a faithful stand-in for an unappendable ledger?
9. Does SF1-A **resolve SF1** as condition C2 requires? Rule exactly `SF1: RESOLVED` or `SF1: NOT_RESOLVED`.
10. Are there unauthorized changes (scope creep beyond the minimal extension), or any namespace change outside r2?

## Output

Write `REVIEW_SF1A_DELTA.md` in your workspace. Line 1 is the title. **Line 2 is exactly one of:**
- `SF1A_DELTA_REVIEW_ACCEPTED`
- `SF1A_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS`
- `SF1A_DELTA_REVIEW_REJECTED`
- `SF1A_DELTA_REVIEW_BLOCKED`

Include:
- the exact commits and ancestry;
- the diff scope;
- the evidence reviewed, with hashes;
- the answers to 1–10;
- `## Blockers`, `## Should-fix` and `## Conditions` (each condition marked **blocking-before-incorporation**,
  **before-freeze** or **advisory**);
- the SF1 ruling;
- whether the change may be incorporated into r2. Incorporation itself is a separate owner decision that has not yet
  been taken; do not decide it.

Avoid the words that `code/p309_placeholder_check.py` flags. Read its marker list in the code; do not quote it.
