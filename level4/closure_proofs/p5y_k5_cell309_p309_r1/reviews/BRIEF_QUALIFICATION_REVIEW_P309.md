# Brief: independent qualification review (formal campaign p5y_k5_cell309_p309_r1; after qualification, before the grant)

This brief is committed **before the freeze**, and so before it is issued (condition C5; rev. 2c A23/A24: nothing but
checkpoint records may be committed between the qualification commit and the review commit).

**Reviewer.** A new independent reviewer who wrote none of the reviewed code. The reviewer is not R1, R2, R3 or R4, not
the incident-independence reviewer, not the verifier's author, and not the coordinator. The basis is research
`protocol_prep/P309_REVIEW_BRIEFS.md` §2, with the formal campaign's rev. 2c amendments.

## Authority and boundaries (read first)

**Owner documents:**
* `governance/OWNER_DECISIONS_P309_VERBATIM.md`;
* `governance/OWNER_RULINGS_2_P309_VERBATIM.md`;
* `governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md`.

No grant exists. **NEW Γ309 TARGET EVALUATIONS must stay 0.** Never create, arm or consume any ref under
`refs/p5y-k5-cell309-p309-r1/`, anywhere. Never run `execute` or `seal-only`, and never write the grant path. Nothing
you run may read a target input or compute in the band.

**Common firewall** (research `P309_REVIEW_BRIEFS.md`):
* no 305–309 value;
* consumer code only through `code/code_skeleton.py` (numbers masked);
* no cell-307/308 campaign file beyond git metadata;
* no git writes;
* write only your output file;
* ledger every run through `code/p309_env.py`, with notes prefixed "QR reviewer:";
* send tool evidence to a scratch `P309_EVIDENCE_DIR`, never to `qualification/`.

## What to review

The chain is: the freeze commit F, named by `ledger/FREEZE_RECORD.json` and added by F's only child FR; then the
qualification commit Q, holding `qualification/attempt_1/` and `qualification/P309_QUALIFICATION.json`; and the HEAD
you are given.

Read:
* the frozen package: rev. 2b plus `governance/P309_REV2C_AMENDMENTS.md` (A1–A30, the D2 corrections);
* the FC2 spec rev. 2 and erratum 1;
* the errata FE-1..FE-9 (and any later ones);
* `freeze/P309_FREEZE.json` and `freeze/P309_FREEZE_MANIFEST.json`;
* every review in `reviews/`: incident independence, U2 check, delta, delta 2, R4 and the R4 follow-up.

## Checklist

Give each item PASS or FAIL, with evidence.
1. **Freeze contents and pins.** The freeze commit contains exactly the frozen files. Every pin verifies (blob and
   sha256), including the interpreter and platform string. The freeze record is valid: `D.recorded_freeze()`, and
   QC13's check.
2. **Protocol integrity.** The frozen protocol documents are the reviewed rev. 2b blobs plus the append-only rev. 2c
   amendments. Nothing else changed after the reviews that accepted them.
3. **Qualification timing.** Q01–Q17, Q-U2 and Q-D5 all ran after the freeze, on the frozen code, with non-target
   inputs only (ledger check).
4. **One attempt.** Every gate passed, and none was waived. There is exactly one attempt (`attempt_1`), with no
   retry, rerun or overwrite (A27).
5. **The verifier variant.**
   * Its independence (README; subagent separation; declared sources).
   * It was written and hashed before the freeze.
   * QC16 passed: I1 on the full decoy battery, the tests, the guard tests (with reasons), and the scanner allowance
     controls.
   * The review mode works on the driver's sealed record: QC11 I01/I02.
6. **The controls are genuine.** Each mutant has a single defect and a reason-specific expectation. No control is
   vacuous: guard N-tests assert reasons; the D5 controls include positive controls.
7. **Per-rung serialization and the gate** (QC08).
8. **Determinism.** Byte identity across runs and on this host (QC10). A14/D7: if the owner names another host,
   QC10's host re-run (`--host-rerun`) must be repeated there before `execute`.
9. **Reproduction.** The adapter reproduces the pinned `tct_rule` (QC05), and S matches the independent
   reconstruction (QC17).
10. **Exactly-once (QC11).** Every failure mapping of protocol §2.5, §3 and §5, plus the rev. 2c flows: admission
    A01–A26, seal-only D5 gates F40–F42, stage flows S13–S16, and integration flows I01–I03.
11. **Static check (QC12) T1–T7.** In particular T6 (the marker is dominated by the grant) and T7 (no production
    execution from tests or qualification).
12. **Historical control.** It is in the driver, runs before the marker, and a control exception is CONTROL_FAILED.
    QC14′, the rehearsal on manufactured inputs (A1), passes.
13. **Budgets and job ends.** Budgets are declared as frozen: Stage 1a 48 CPU-h with 12 CPU-h per job; Stage 1b
    21 600 s with 21 600 s per job; ≤ 4 workers. The job-end mapping is A22.
14. **The quarantine is intact.** Self-audit A1–A11 (QC15), and the formal scan with its D5 whitelist current (Q-D5).
15. **Temporal order.** Freeze → record → qualification → review. r5 unchanged, no r6 (QC13).
16. **No qualification artifact touches the target or the real band.** QC16 uses the TEST band only, and the decoys
    are declared.
17. **Scope.** The outcome table and the grant schema are CLOSURE_ONLY (U3). The proposal tool's grant rules match
    the driver's pre-marker checks (A20, A21).

## Output

`reviews/REVIEW_QUALIFICATION_P309.md`, with line 2 exactly one of:
* `QUALIFICATION_ACCEPTED`, with conditions G… and notes E…;
* `QUALIFICATION_REJECTED`, with the reasons.

`QUALIFICATION_ACCEPTED` must appear exactly once in the file, on line 2.

Also include:
* a disclosure section listing your reads and runs, with ledger timestamps;
* a statement that NEW Γ309 TARGET EVALUATIONS = 0 as far as you can verify.

## Addendum (before issue; delta-2 review conditions E2–E9)

* **Checklist 4 (one attempt).** Verify it from the committed execution ledger, anchored at the freeze record's commit
  time. Exactly one line reading `QUALIFICATION RUN START`, and no `HOST RERUN START` before the review. QC13 checks
  this as `single_qualification_run_since_the_freeze_record`. Lines labelled "qualification:" or "dry run" dated before
  the freeze record belong to the coordinator's pre-freeze dry run (development).
* **Checklist 13 (job ends).** It includes E2: a SIGXCPU below the CPU limit (tolerance 0.05 s) is JOB_EXCEPTION
  (QC11 S17).
* **Checklist 10.** QC11 I03 uses manufactured Stage-1b records (E4). No campaign results file and no cover-cell entry
  is read.
* **Latent proxies.** QC09's Stage-1b decoy outputs (cover cells 297 and 316) are latent-proxy class (E5). Check that
  they are labelled and never displayed in summaries.

## Addendum 2 (before issue; R4 follow-up, rev. 2c third delta A31–A36)

* **Checklist 4 (one attempt), R4F NF2.** Check the attempt tree and the committed execution ledger together. An attempt
  directory deleted before the Q commit leaves no trace in the tree, only its `QUALIFICATION RUN START` ledger line.
  Exactly one such line after the freeze record, and exactly one attempt directory, `attempt_1`.
* **Checklist 11 (static check).** QC12 now has T1–T8. T8 is the runtime backstop's structure (A31). T7 is the
  hardened form (A33); its `t7_exemptions` are rule-specific and bound to each file's AST hash.
* **Checklist 14 (quarantine), and Q-D5.** Scanner schema 4 allowlists process execution (A32). Check that:
  * every `process_policy.reviewed_functions` entry, `git_runners` entry and `ref_mutation_functions` entry has a true
    reason and a current hash;
  * the two sites keep the owner-ratified hashes;
  * Q-D5 ran the D5 controls, including R4's M01–M15, and the backstop controls `tests/test_p309_site_backstop.py`.
* **Checklist 10 (QC11).** QC11 also contains:
  * A27 (an authority quoting the owner is admitted);
  * A28 (a missing worktree is refused);
  * V01–V09 (`validate-grant`).
* **Checklist 17 (scope).** Check that the proposal carries the `grant_validation` step: run validate-grant before
  the grant commit, and a refused grant commit is terminal without a new owner decision.

## Addendum 3 (before issue; delta-3 review conditions G5, G6)

* **Checklist 3 and 4 (timing, one attempt), G6 and FE-11.** The execution-ledger rows after `77991be1` have not been
  reviewed by any independence review. They include the coordinator's second pre-freeze dry run (from
  2026-09-30 06:53:35Z) and R4 follow-up 2's runs. Review them.
* **Pre-freeze lines.** The research-test lines of both pre-freeze dry runs read "qualification: …" (FE-11). They are
  development because they are dated before the freeze record. After the freeze record there must be exactly one
  `QUALIFICATION RUN START` line and no other QC-runner line outside the single run.

## Addendum 4 (before issue; R4 follow-up 2 and the fourth delta, A37–A42)

* **Checklist 4 (one attempt), R4 NF4.** QC13 now also checks `execution_ledger_append_only_since_the_freeze`: every
  committed version of the execution ledger from the freeze to HEAD, and the working copy, is a byte prefix of the
  next. Confirm it independently from git.
* **Checklist 11 (static check).** QC12 has T1–T9:
  * T8 is an equality check of the pinned backstop (A38);
  * T9 checks validate-grant's pre-checks (A39).
* **Checklist 14 (quarantine).** The scanner is schema 5 (A37). Check that each of these allowlists is exactly what
  the tree uses:
  * the import allowlists and the two module-level `multiprocessing` exemptions;
  * the `introspection` and `import:importlib.util` permits;
  * the `env_keys`;
  * the per-verb option lists.
* **Checklist 17 (scope).** The proposal carries `host_git` (A40). The execution host's repository config must pass
  `check_host_git`, and the owner should know this before choosing the host.
