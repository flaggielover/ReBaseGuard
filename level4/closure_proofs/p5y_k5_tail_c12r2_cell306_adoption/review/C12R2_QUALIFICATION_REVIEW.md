# C12-R2 — qualification review (cell 306 under floor r2)
QUALIFICATION_ACCEPTED

**Reviewer.** An independent, fresh, read-only qualification reviewer. I replace a reviewer that stalled; it left no
files. I did not write any part of C12-R2.

**Repository.** /Users/suzhe/ReBaseGuard-k5c11rd, branch p5y-k5-tail-c11rd-d1d2-extension.

**Abbreviations.** All of these are under level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/:
- D = code/c12r2_cell306.py
- V = code/c12r2_verify.py
- GR = code/c12r2_grant.py
- R6 = code/c12r2_r6_from_adjudication.py
- P = protocol/C12R2_PROTOCOL.md

`D:n` means D line n.

**Summary.** There are 0 blockers and 12 non-blocking notes. The C12-R1 blocker is demonstrably closed.

## Reviewed commits

- **Freeze:** 11f91daf50a077999023f733d8e870ad3813923a. It changes code/ and protocol/ only (6 files).
- **Qualification:** 107a8b362e572eeab5c630e838edbe012cd3ae85, which was HEAD throughout. It changes
  evidence/qualification/ only (4 files). Its parent is the freeze commit.
- The sha256 of each of the five frozen files matches C12R2_FREEZE.json `frozen_files_sha256`:

  | file | sha256 prefix |
  |---|---|
  | D | 5c45b4de |
  | V | 3c748f11 |
  | GR | 83ec10cc |
  | R6 | 23a831c9 |
  | P | 874a5610 |

- The committed qualification report says: pass true; 181/181; review_mode false; freeze_commit = HEAD = 11f91daf;
  real_target_evaluations 0.

## State confirmed before and after every step

- HEAD = 107a8b36.
- `git status --porcelain --ignored --untracked-files=all` was empty (0 lines) at the start and after every step.
- `git for-each-ref refs/c12r2 refs/c12r1 refs/c12` was empty.
- The digest of the full `git for-each-ref` listing was the same before and after my probes.
- There was no emergency file in /Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-k5c11rd.
- There was no grant, no result and no seal.
  - The real Γ(5, 306; S_I2) has been evaluated **0** times.
  - My VERIFY_REVIEW.json reports `real_target_evaluations` 0, `markers_and_pending_refs` [], `result_path_objects` [],
    `grant_exists` false and `seal_exists` false.
- r5 at HEAD is blob f978eeb6b41188eabaf3c6d590c9178d711f1ce6. No K5_COVERAGE_MAP_R6 exists in the index, the
  worktree or any history.

## Commands run

All outputs are in …/scratchpad/c12r2_qual_review2/.

1. `python3.14 -I -S -B c12r2_verify.py --review --out …/VERIFY_REVIEW.json`, at HEAD 107a8b36.
   - Result: `C12R2 QUALIFICATION PASS (181/181)`, exit 0, 139 s. The state was "qualification".
   - Sandbox A and the parent of sandbox B are both 11f91daf.
   - `B_contains_no_real_I2_file` true; `review_tmp_removed` true.
   - No c12r2rev* or c12r2q* directory was left in $TMPDIR.
2. `c12r2_cell306.py preflight --out …/PREFLIGHT.json` → `C12R2 PREFLIGHT PASS`, exit 0.
3. `c12r2_cell306.py rehearse --cell 306 --out …/REHEARSE_306.json` → reproduces C2 exactly = True, exit 0.
   - All seven field matches are True, including the per-supply records for G, C1 and C2.
4. `c12r2_cell306.py rehearse --cell 305 --out …/REHEARSE_305.json` → reproduces C2 exactly = True, exit 0.
   - The outputs of commands 2-4 are identical to the committed evidence/qualification/*.json, apart from
     utc, wall and rss.
5. `python3.14 -I -S -B c12r2_cell306.py execute` in the real worktree, as a refusal probe only.
   - Result: `C12R2 REFUSED GRANT_MISSING`, exit 2.
   - `check_grant` (D:847) precedes the object-store probe (D:850), so nothing was written.
   - Afterwards refs/c12r2 was empty, `status --ignored` was empty and there was no emergency file.
6. A throwaway git repository in scratch, since deleted:
   - a broken ref at `refs/c12r2/cell306-pending-result/junk` does not appear on `for-each-ref` stdout (it only warns on
     stderr);
   - it makes `update-ref refs/c12r2/cell306-pending-result <oid> 0000…` fail with exit 128.
7. `probe/c12r2_probe.py --out probe/PROBE.json`, three probes on decoys only.
   - **Sandbox.** My own sandbox, built by V's `make_decoy_sandbox`/`build_state` from 11f91daf and deleted afterwards.
     Its I2 supply files, C11R_RUNS.json and I2 soundness documents are V's decoys, and the script asserts `DECOY`
     before it drives anything.
   - **Driving.** The driver was driven in-process with its identity pointed at the sandbox and PINS/BLOBS set to the
     decoy hashes, exactly as V's X/T/P flows do.
   - **Real repository.** It was unchanged: the same HEAD, status, refs digest and emergency-file count before and
     after.

## Findings on the ten points

### 1. The C12-R1 .tmp/symlink blocker: CLOSED (demonstrably)

**The root cause is removed.**
- No filesystem write of the result precedes the seal.
  - The record is serialized in memory (D:807).
  - It is persisted with `git hash-object -w --stdin`, and the blob id is checked against a locally computed SHA-1
    (D:668-676).
  - It is committed through a private index with `--cacheinfo` (D:694-724).
- There is no temporary file, rename or replacement anywhere in D.
- The only worktree write is `materialize` (D:727-762). It runs only after the seal and is exclusive and no-follow.
- A planted object therefore cannot divert or corrupt the sealed record.

**Before the marker, a planted object at any guarded path is refused and cannot survive into the evaluation.**
- This covers the result, `.tmp`, `.json.tmp`, `.partial` and `evidence/execution` itself (D:81-82).
- It is enforced in three layers:
  - `check_not_evaluated` uses `lexists` on the result (D:315);
  - `check_result_paths` uses `lstat` of everything, plus a plain-directory check on every component (D:322-341);
  - R2, the ignored-aware status check (D:348).
- Every child path is covered because `evidence/execution` must not exist at all.

**Decoy tests.** V's T1-T9 pass in my re-run, including the two C12-R1 reproductions:
- T1: a directory at `.tmp`;
- T2: a symlink at `.tmp` pointing outside, with the outside sentinel's bytes and mtime unchanged.
The `status_blind` assertion (V:724-728) proves that the default `git status` could not see the planted objects.

**After the marker (TOCTOU),** a planted object makes `materialize` fail. The result is then exit 7: the result is
sealed, and nothing is written through the link. This is shown by P10, P11 and P11b.

**Residual.** A planted object inside the *git dir* at the pending-ref path is not caught before the marker. It
neither diverts nor corrupts anything, and the second channel records the evidence. See note NB1.

### 2. Ignored-file cleanliness (R2): HOLDS

- D:348 requires `git status --porcelain --ignored --untracked-files=all -- <namespace>` to be empty. The repository-wide
  tracked and untracked check is kept (D:346). `.gitignore` is unchanged.
- **R2 is independently live.** T5b plants `code/stray.tmp`, which R1 would not catch, and is refused IGNORED_OBJECT.
- **R1 fires before R2.** T1, T3, T5, T6 and T7 are refused RESULT_PATH_OCCUPIED. Both layers are therefore
  non-vacuous.
- **Scope.** R2 covers the namespace only. Outside it, every input is pinned by sha256 and blob. The worktree bytes are
  also compared with the HEAD blob through `git hash-object` (D:391-396).
- **Stale .pyc.** Every consumer module on the evaluation path is compiled from pinned bytes:
  - D:263-268;
  - tail_forecast_r2 `module()`;
  - consumption_adapter `load_frozen`.
  So a stale .pyc outside the namespace cannot reach the evaluation. `tct_rule` is pre-registered in `sys.modules`
  (D:434-437).
- In the real worktree there are zero ignored paths now.

### 3. Pre-marker path barriers (R1): HOLD

- **Object kinds.** `lstat` never follows the final component. Any non-ENOENT result refuses. Other errors such as
  EACCES or ENOTDIR also refuse (D:326-332).
  - Files, directories, symlinks, broken symlinks, FIFOs and sockets are covered by T1-T7 and T4-T4d.
  - Devices fall under the same `lstat` rule. They are not testable without root.
- **Symlinked parent components.** D:333-341 checks level4, closure_proofs, the namespace and evidence. T8 (the
  execution directory) and T9 (a symlinked `evidence/`) are refused.
- **TOCTOU.** The check is repeated immediately before the marker (D:871). Correctness does not depend on it, because
  the only later worktree write (D:734-762) guards itself:
  - it opens each component with `O_NOFOLLOW` from a directory fd;
  - it runs `mkdir("execution")`, which must create the directory;
  - it creates the file with `O_CREAT|O_EXCL|O_NOFOLLOW`;
  - it reads the file back and checks for a regular file with link count 1.
  P10 and P11 plant a directory or a symlink after the marker, and both give exit 7 with nothing written outside.
- **seal-only's read-only comparison branch** follows an intermediate symlink. See note NB3.

### 4. Exclusive, no-follow result creation (R3): HOLDS; the sealed bytes are exactly the produced bytes

- **Blob.** `hash-object -w --stdin` implies no filters. The blob id is compared with `sha1("blob <n>\0"+data)` (D:670-673).
- **Pending ref.** Created by CAS from the zero oid (D:674).
- **Commit.** A private index is built from HEAD, then `update-index --cacheinfo 100644,<blob>,<path>`, `write-tree`,
  `commit-tree`, and a CAS `update-ref` of the branch (D:700-718). Then the committed entry is checked by `ls-tree` to
  be `100644 blob <blob>` (D:719-721).
- **Worktree copy.** `materialize` re-reads the blob, re-verifies its id, writes it `O_EXCL|O_NOFOLLOW` via directory
  fds and reads it back (D:730-759).
- **Test evidence.** X05 passes: the pending blob, the HEAD blob and the blob id of the worktree copy are all equal, the
  mode is 100644, the self-hash verifies, and the evaluation count is 1.
- **Replace objects** are disabled twice (D:96-97, D:240/244).
- **Pre-marker probes.** The object-store write probe and a trial `commit-tree` (for gpgSign and identity) run before
  the marker (D:360-374, N4).

### 5. Post-marker failure sealing (R4): HOLDS, with residuals that fail safe

**Signals and the wall cap.**
- INT, TERM, HUP and QUIT are set to SIG_IGN before the marker (D:872-873).
- The invocation wall-cap alarm is cancelled before the marker (D:874), so no internal SIGALRM can land in the window.
  - A SIGALRM that trips just before `alarm(0)` is handled at the next eval-breaker. That is before the `update-ref`
    subprocess starts, so it is still before the marker.
- Inside `after_marker` the cap is re-armed for the evaluation only (D:790, 795-800).

**Everything after the marker is recorded.**
- An evaluation exception, SystemExit, KeyboardInterrupt or the cap → TARGET_EVALUATION_FAILED (D:799-801).
- A serialization or recording failure → POST_MARKER_RECORDING_FAILED (D:808-809).
- Persistence: the pending ref is tried first, then an `O_EXCL|O_NOFOLLOW` file in the git dir (D:811-819).
- A seal failure → 4; a materialization failure → 7 (D:823-832).
- P01-P11 all pass: exactly one decoy evaluation each, a persisting consumed state, the retry refused, and a recovery
  that never recomputes.

**The window between `update-ref` and `after_marker`** holds only trivial statements (D:875-877, then D:787-792). Only an externally
sent SIGALRM can make anything escape there. My probe 2 shows the result:
- the marker is set, 0 evaluations, Refusal WALL_CAP escapes, and the CLI would exit 2;
- execute is refused afterwards, and seal-only refuses.
This fails safe and equals a SIGKILL. See note NB2.

**Other residuals, all without recomputation or evidence loss:** print() failures after the marker (NB4), a
600-second race (NB5) and short writes (NB6).

### 6. Retry and recovery: HOLD. seal-only never computes

- seal-only calls `check_flags`, then `check_identity`, then ignores signals (D:882-885). It never touches the consumer,
  which V's static check confirms.
- P01-P11 and X06b keep the evaluation count at 1.
- Retry after any post-marker outcome is refused CONSUMED (X06, and every P test). Probes 1-3 confirm this.
- The exit codes match the FREEZE table in normal operation, with these exceptions:
  - 2 can also follow an evaluation, for seal-only refusals such as P07;
  - 2 appears after the marker in the external-SIGALRM case;
  - 1 (a traceback) appears when stdout fails (NB4), and when seal-only meets the git-dir obstruction of NB1.
  None of these ever means "safe to rerun": execute refuses on any ref under refs/c12r2/.

### 7. Exactly-once semantics: HOLD

**The four barriers.**
- **Marker.** A CAS create at the grant commit (D:875).
- **Prior-evaluation evidence.** Any ref under refs/c12r2/, refs/c12r1/ or refs/c12/, any prior result in the tree,
  on disk or in any history, or the emergency file refuses before anything runs (D:307-319; X08, X08b, X08c, A07*).
- **Identity barrier.** It runs first after the interpreter flags (D:842-843; X01-X03, B05). ENV strips GIT_DIR and
  similar variables (D:96-97).
- **Grant chain.** It is derived exactly as freeze → qualification (evidence/qualification only, including QUAL_REL,
  an official non-review PASS at the freeze) → review (the review file only, line 2 accepted) → grant (the grant file
  only, HEAD = the grant commit) (D:624-658; X12*, X12b-e).

**CONTROL_FAILED** creates no marker, but seals a pending ref that spends the campaign (X11).

**Marker deletion alone does not re-enable execute:** the pending ref and the history check remain (an improvement on
C12-R1 N5).

### 8. The original C12 B1 barriers: INTACT

- **Sandboxes are built from the freeze commit.**
  - Sandbox A = 11f91daf. Sandbox B is 11f91daf plus one decoy commit.
  - `both_from_the_freeze_commit` is true in my run (V:1121-1129).
- **The verifier refuses at later states** (V:122-149):
  - HEAD must be the freeze commit, or with `--review` the qualification commit directly on it;
  - review/, authorization/, adjudication/, evidence/execution and evidence/coverage must not exist on disk or in any
    history;
  - there must be no ref under the three prefixes, no prior result, no occupied result path, a tree clean including
    ignored files, and code/ and protocol/ equal to the freeze.
  - B02v, B03v, B04v, B06v and B07v-B12v pass.
- **Decoy-only governance.**
  - Every grant, review, marker and post-marker flow runs in sandbox B, on decoys.
  - Sandbox A never receives a grant or review, and its CLI execute is refused REPO_NOT_QUALIFIED (A20) or
    INTERPRETER_FLAGS (A21).
- **Driver identity first.** `check_flags` then `check_identity` open both `execute` (D:842-843) and `seal-only`
  (D:882-883). The static order check passes.

### 9. N1-N13 of the C12-R1 review: 12 correct, 1 misclassified

| note | classification | assessment |
|---|---|---|
| N1 | "repaired" | **Misclassified: only partially repaired** (NB7). |
| N2 | repaired | Correct. B06v is relabelled, and B10v plants this campaign's own result at the freeze state. |
| N3 | repaired | Correct. V:145-148 requires a tree clean including ignored files, and code/ and protocol/ equal to the freeze (B12v). |
| N4 | repaired | Correct for internally generated signals. INT, TERM, HUP and QUIT are ignored and `alarm(0)` precedes the marker. Non-Refusal sealer errors are handled (P08). The object store and commit-tree are probed (D:363-374). The only residual is an external SIGALRM (NB2). |
| N5 | inherent, mitigated | Correct. |
| N6 | repaired | Correct. X12 names the wrong qualification or review commit; X12e changes code after the freeze; G17 has the result not at HEAD. |
| N7 | repaired | Correct. R6:88-95 and R6:110-117 cover it (G11-G16). |
| N8 | repaired | Correct. D:288-291 (A21). |
| N9 | repaired | Correct. GR:46 requires QUAL_REL, and GR:88-89 commits through `D.git` with its sanitized env, `core.hooksPath=/dev/null` and `--no-verify`. The check is static only (V:215-217), but `check_grant` re-verifies everything downstream. |
| N10 | repaired | Correct. D:162-172 and D:185-187 pin five documents by sha256 and blob. |
| N11 | "repaired to the precision the evidence permits" | Correct. D:458-460 (`A0=C`, `A1=k1·C²`, `A2=k2·C²+2k1²C³`) matches Lemma G, which I re-derived from the K1 DAG rules in tct_rule.py:65-76. It is live (F08b). A_exact and provenance are compared exactly with C2. |
| N12 | not applicable (by design) | Correct. Every I2 check must precede the marker, and the atoms are never output. |
| N13 | repaired | Correct. V:1108 and V:1144-1146; my run left nothing in $TMPDIR. |

**N1 in detail.**
- The sandbox-B half is repaired: the decoys now cover C11R_RUNS.json and the soundness documents, and the run logs are
  removed.
- The predecessor half is not. P:93-96 and V:4-6 still claim that the verifier refuses when "a qualification review,
  grant, adjudication, execution or coverage output" exists for C12-R1 or C12.
- Both predecessor qualification reviews exist at HEAD, and V runs:
  - p5y_k5_tail_c12_cell306_adoption/review/C12_QUALIFICATION_REVIEW.md;
  - p5y_k5_tail_c12r1_cell306_adoption/review/C12R1_QUALIFICATION_REVIEW.md.
- For C12-R1 and C12, V checks only refs/c12r1/, refs/c12/ and their result paths.

### 10. No path computes the real target; floor-r2 fidelity

**Verifier paths.** No verifier path can compute Γ or atoms under real S_I2:
- In the real repository, V runs:
  - the CLI `execute`, refused GRANT_MISSING before `prepare`;
  - preflight and rehearse, which evaluate I1 only;
  - `function_controls`:
    - `supply` is called only with synthetic sets, and refuses mixing before any atoms;
    - `i2_set` is called only with mutated copies, and each one refuses before returning;
    - the I1 control and Lemma G;
  - `leak_scans`, which hash patterns only;
  - `r6` G01, which is refused.
- Sandbox A, which holds the real inputs, only runs the CLI, whose execute is refused by identity or flags.
- All in-process driving uses sandbox B, which holds decoys.
- The static check confirms that `prepare_target` and `evaluate_target` are referenced only by `run_execute`
  (V:194-196).

**Reviewer paths.** preflight and rehearse evaluate I1 only (D:966-987). GR evaluates nothing. R6 reads a sealed record
and computes nothing.

**S_I1 is C2's adopted supply.** Compare D:463-486, 497-504, 547-572 with c2_d5_forecast.py:194-205:
- Lemma G comes from `atom_constants_generic(C_upper, k1, k2)`;
- Dv′ r2 is `deflated_consume.atom_constants_r2` on the REGISTRY_C1 and REGISTRY_C2 blocks of the cell, cross-checked
  against `_atom_independent`;
- the combination is C2's `combine`, the componentwise minimum;
- the evaluation is C2's `direct` with the adopted m=5 record, cover cell and loader.
The rehearsal reproduces C2's record exactly at 305 and 306.

**No mixing, and S_I2 is as the floor defines it.**
- `supply()` refuses any set whose implementation tag differs, and any duplicate name (D:556-565; F01, F01b, F01c).
- S_I2 = min{G, Dv′(I2 set)}, as the floor rule's `S_I` defines it (D:600).
- The I2 set's sources are the ones the floor rule names:
  - C11R `per_target.independent_value` for C_T, tau, Abar and D_lo, with directions checked;
  - C11RD for D1 and D2, bound to the sealed runs' values;
  - statements must be EQUIVALENT or STRONGER, and domains EQUAL or SUPERSET;
  - the C11R drift domain must equal cell 306's cover cell;
  - there must be no independence violations.
  See D:507-544 and F03-F04c.

**The decision table matches the floor-r2 limbs (D:609-620).**
- base = Γ(S_I1) < 0, strict.
- F1′(d) = base AND Γ(S_I2) < 0.
- F2 is NOT_SATISFIED and is not re-evaluated.
- floor = base AND F1′.
- Adoption is left to G13.

**Pins and scope.**
- There are 32 inputs, each pinned by sha256, blob prefix and worktree == HEAD blob, plus the lineage and verdict
  lines (D:387-412).
- Only cell 306 can be targeted: TARGET_CELL is fixed, `cell_inputs` refuses cells other than 305 and 306, and
  execute refuses `--cell` (A02, A02b, F06, F06b).
- r5 is read only.

**The r6 generator** moves only (5, 306). It requires:
- the sealed result at HEAD, with a verifying self-hash;
- cell 306 and TARGET_EVALUATED with exactly one evaluation;
- control pass and target pass;
- the marker at the result's grant commit;
- the pending ref equal to the committed blob;
- line 2 exactly right in all three reviews and the adjudication, with the adopted set exactly [306];
- `--out` confined to evidence/coverage/K5_COVERAGE_MAP_R6.json.
See R6:83-186 and G02-G17.

## Is the C12-R1 blocker demonstrably closed?

**Yes.**
- No planted object at a result, temporary or execution-directory path can survive into the evaluation. They are
  refused before the marker by R1 and R2: T1-T9, re-run by me, all pass.
- None can divert or corrupt the sealed result:
  - the seal is made from memory by blob id, with no worktree read (D:694-724);
  - the worktree copy is written only afterwards, exclusively and without following links, and is read back;
  - a planting after the marker yields exit 7 with nothing written outside (P10, P11, P11b).
- The C12-R1 failure mode "the one evaluation unsealable" is replaced by recorded evidence in every tested
  post-marker failure (P01-P11).

## BLOCKERS

None.

## NON-BLOCKING NOTES

**NB1 — The pending-ref path in the git dir is not probed before the marker.**
- **Mechanism.** A broken ref planted at `<common-dir>/refs/c12r2/cell306-pending-result/junk` is invisible on
  `for-each-ref` stdout, so `check_not_evaluated` passes (D:310-312). After the marker, `update-ref` of the pending ref
  fails with a directory/file conflict (D:674).
- **What happens.**
  - The emergency channel records the full TARGET_EVALUATED record, and execute exits 4.
  - seal-only then raises an **uncaught OSError** from `persist_pending` (D:899, which is not in a try) and exits 1 with
    a traceback.
  - It seals normally, with no recomputation, only after the junk is removed by hand.
- **Reproduction:** probe/c12r2_probe.py, probe 1, recorded in probe/PROBE.json.
- **Why it is not a blocker.**
  - It needs a deliberate write inside .git/refs/.
  - Nothing is lost, diverted or corrupted.
  - Exactly-once holds: the retry is refused CONSUMED.
- A `reference-transaction` hook rejecting that update would have the same effect. None is configured today.
- **Suggestions for a successor:**
  - make seal-only turn this OSError into a clean refusal;
  - probe the pending-ref and marker creations before the marker with a
    `git update-ref --stdin` start/create/prepare/abort transaction.
  - Operators should check that `<common-dir>/refs/c12r2` does not exist before `execute`.

**NB2 — An externally sent SIGALRM between the marker and `after_marker`'s `try` escapes as Refusal WALL_CAP.**
- The SIGALRM handler is still `main`'s wall_cap until D:790.
- The CLI would then print `REFUSED WALL_CAP` and exit 2, which the FREEZE table glosses as "refused before the marker".
- The marker is set and there are 0 evaluations. Retry and seal-only refuse. Reproduction: probe 2.
- This fails safe, equals a SIGKILL, and requires `kill -ALRM` by hand. The internal alarm is cancelled at D:874.

**NB3 — seal-only's already-materialized branch reads through an intermediate symlink.**
- The branch is D:931-945: `lstat` and `open(O_NOFOLLOW)` on the full path.
- If `evidence/execution` is a symlink out of the repository to a copy of the sealed bytes, seal-only prints SEALED and
  returns 0 while the tree is dirty.
- It only reads, and the sealed record is unaffected. Reproduction: probe 3.
- It also does not check the link count, unlike `materialize`.

**NB4 — The print() calls in `after_marker` are outside any try.**
- They are at D:818, 821, 826, 831 and 833. V's static check whitelists top-level `If` and `print`.
- An EIO or EPIPE on stdout after the marker gives exit 1 with a traceback instead of 4, 5, 6 or 7.
- The persisted, sealed or materialized state is already correct at each print, so this affects only the exit code.

**NB5 — An evaluation cap race.**
- If SIGALRM fires between the evaluator returning and `signal.alarm(0)` (D:796-797), a completed evaluation is
  recorded as TARGET_EVALUATION_FAILED and its value is discarded.
- This needs completion within microseconds of 600 s, against about 0.04 s measured, so it is negligible.

**NB6 — `persist_emergency` ignores `os.write`'s count and has no read-back (D:683-686).**
- seal-only's emergency path does not verify the self-hash before sealing (D:889-912).
- A short write would therefore be sealed as a truncated UNPARSEABLE_EVIDENCE record. R6 would refuse it on the
  self-hash.
- This only matters under near-full-disk conditions in which the primary channel has already failed.

**NB7 — N1 is only partially repaired.**
- P:93-96 and V:4-6 still overstate what V checks for C12-R1 and C12; see point 9.
- The actual cross-campaign barriers are sound and tested (A07c, A07c2, A07e, A07f, B09v, X07b, X07c):
  refs/c12r1/, refs/c12/ and their result paths.

**NB8 — Protocol wording.**
- P §6 says "900 s per invocation", but after the marker the invocation cap is cancelled (D:874). Persistence, seal and
  materialization are uncapped; only the evaluation is capped, at 600 s.
- P §1 R4 and D:17-20 say the evidence is "persisted through two channels". The fallback file is written only if the
  pending ref fails (D:811-816).

**NB9 — `check_grant` and GR read the review verdict and the grant from the worktree (D:634, D:655; GR:43), not from
the commit.**
- `check_clean` makes this equivalent in practice.
- The exception is an assume-unchanged or skip-worktree bit, which `git status` does not report.
- Reading `git show <review_c>:<QREVIEW_REL>` would bind the committed bytes.

**NB10 — The seal does not check that HEAD is still the grant commit.**
- `seal_blob` re-reads HEAD on each attempt and seals on top of it (D:700).
- R6 checks the marker against the result's grant commit, but not the seal's parent.
- The execution review should confirm that the seal commit's parent is the grant commit.

**NB11 — The main-index alignment's return code is ignored (D:722).**
- If it fails, for example through a concurrent index.lock, the tree looks dirty after `materialize`.
- R6's clean-tree check would then refuse until the index is refreshed.

**NB12 — Operational constraint for preserving this review and granting.**
- `check_grant` (D:645-646) and GR:41 require the review commit to change **only**
  `review/C12R2_QUALIFICATION_REVIEW.md`, and HEAD to be exactly the grant commit when execute runs (D:630-633).
- So this review's probe files (probe/, PROBE.json, VERIFY_REVIEW.json and so on) must **not** be committed with the
  review. The C12-R1 review commit e89402c1 did carry a probe directory.
- Nothing may be committed between the review and the grant, or between the grant and execute.
- Otherwise the grant is refused GRANT_INVALID. That fails closed, but it would spend the protocol.

## Confirmation

- **I modified nothing.**
  - I ran no git write command in /Users/suzhe/ReBaseGuard-k5c11rd and created no file or ref there.
  - HEAD is still 107a8b36. `git status --porcelain --ignored --untracked-files=all` is empty. refs/c12r2, refs/c12r1
    and refs/c12 are empty. There is no emergency file. r5 is blob f978eeb6, and no r6 exists.
- **What I ran.**
  - `execute` only once, as the permitted refusal probe (GRANT_MISSING). I never ran seal-only in the real worktree.
  - V `--review` once. Its sandboxes were in $TMPDIR and were removed.
- **Where I wrote.** Only under …/scratchpad/c12r2_qual_review2/, which includes my own decoy sandbox. I deleted that
  sandbox and a throwaway git repository afterwards.
- **I computed nothing under a real S_I2.**
  - I did not compute, estimate or inspect any Γ, atom constant or margin under a supply containing a real C11R or
    C11RD constant.
  - I did not call `prepare_target` or `evaluate_target` on real inputs, and did not reconstruct them.
  - Every Γ that I caused to be evaluated was either the historical I1 control (305, 306) or a synthetic decoy in my
    sandbox.
- **No D1/D2 values.** I printed, wrote and quoted no D1 or D2 value, original or independent. I did not open C11R's
  quarantine. I used no AWS or Vultr tool, no network and no session transcript.
