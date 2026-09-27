# C12-R2 — execution review (cell 306, Gamma(5,306; S_I2))
EXECUTION_ACCEPTED

**Reviewer.** An independent, fresh, read-only execution reviewer. I did not write, freeze, qualify, grant, run or seal
any part of C12-R2.

**Repository.** /Users/suzhe/ReBaseGuard-k5c11rd, branch p5y-k5-tail-c11rd-d1d2-extension.
- git dir: /Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-k5c11rd
- common dir: /Users/suzhe/ReBaseGuard/.git

**Namespace.** level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/ (NS below). D = NS/code/c12r2_cell306.py.

**Summary.**
- 0 blockers and 8 non-blocking notes.
- The chain freeze → qualification → review → grant → seal is exact, linear and unbroken.
- The real Gamma(5, 306; S_I2) was evaluated exactly once, at the grant commit, under the marker. It was sealed from
  memory, by blob id, before the worktree copy was written.
- The sealed record is internally consistent, self-hash verified, and byte-identical in all three places it lives.
- No floor-r2 application and no adoption judgement are made here.

## Reviewed commits

| role | commit | parent | files changed |
|---|---|---|---|
| freeze | 11f91daf50a077999023f733d8e870ad3813923a | 13e06db0 | 6: code/ ×4, protocol/ ×2 |
| qualification | 107a8b362e572eeab5c630e838edbe012cd3ae85 | 11f91daf | 4: evidence/qualification/ only |
| qualification review | e19f4edd06ef2152d8285996db6d60b664c40f7d | 107a8b36 | 1: review/C12R2_QUALIFICATION_REVIEW.md |
| grant | dec92e0983fe39bcf9834e62216daeab09f823a4 | e19f4edd | 1: authorization/C12R2_GRANT.json |
| seal | 276f4d416175086640c982ac4cda7c9cf703fccb | dec92e09 | 1: evidence/execution/C12R2_CELL306_RESULT.json |

- **Unreferenced object from the run:** the trial commit def4e45319711f568125f780b92055c858236217 (parent dec92e09, tree
  = the grant tree). It is the one expected from `check_seal_preconditions`.
- **Baseline:** HEAD 276f4d41 and `git status --porcelain --ignored --untracked-files=all` empty, both at the start of
  this review and at its end.

## Commands run

All git commands ran with `GIT_OPTIONAL_LOCKS=0`, so that `git status` could not rewrite the index. All Python ran as
`python3.14 -I -S -B`. Scratch outputs are in this directory.

1. **Chain.** `git log`, `git show -s`, `git diff-tree -r --name-status` for each chain commit.
   - `git rev-list --parents 13e06db0..HEAD` and `git rev-list --merges`.
   - `git reflog` of HEAD, of the branch and of both refs/c12r2 refs.
   - `git diff --name-status 13e06db0 HEAD`.
2. **Frozen files.** sha256 of the 6 frozen files at the freeze commit, at HEAD and in the worktree (`git show` and
   `shasum`), compared with C12R2_FREEZE.json and the grant.
3. **Refs.**
   - `git for-each-ref` (full listing, snapshotted).
   - Filesystem listing of `<common-dir>/refs/c12r2`, `refs/c12r1` and `refs/c12`.
   - `grep c12 packed-refs`.
   - `find` over `<common-dir>` and `<git-dir>` for `*c12*` and `*emergency*` (objects excluded).
   - `git config --get extensions.refstorage` (unset, so the files backend is in use).
4. **Object store.**
   - Every loose object written after 15:35+09:00 (06:35Z), classified by type with `git cat-file -t` and `-s`.
   - A scan of all 29,612 objects (`cat-file --batch-all-objects`) for C12/C12-R1/C12-R2 result schemas, the
     object-store probe, emergency or POST_MARKER strings, trial commits and C12 subjects. The script
     (scan_objects.py) prints only ids, types and sizes, never content.
   - Blob-to-path mapping with `git rev-list --all --objects`.
5. **Record.** verify_record.py, read-only:
   - O_NOFOLLOW read of the worktree copy, fstat, and a symlink check of every path component;
   - `git cat-file blob` of the pending ref and of HEAD:<result>, and Python SHA-1 of `blob <n>\0` + bytes;
   - the self-hash, and byte-identity of the canonical re-serialization;
   - field checks against the actual commits, the grant bytes, and the frozen pins read from
     `git show 11f91daf:NS/protocol/C12R2_FREEZE.json`;
   - string equality of the control against C2_D5_FORECAST.json `cells["306"]`;
   - the sign of the sealed Gamma strings, read from the leading character and by parsing the sealed string. There
     was no evaluation.
   A separate structure dump (structure.py) printed key paths and leaf types only.
6. **Driver.** I read D in full. An AST scan of the transitive local call closure of `run_seal_only` found none of
   load_consumer, control, prepare_target, evaluate_target, evaluate, supply, atoms, cell_inputs, i1_sets, i2_set,
   after_marker, exec_module, decide or lemma_g_independent. D has no top-level statements other than definitions,
   constants and the main guard.
7. **Probes, each run once from NS/code.** A full state snapshot was taken before and after them.
   - `python3.14 -I -S -B c12r2_cell306.py execute` → `C12R2 REFUSED CONSUMED: a ref exists under refs/c12r2/`,
     exit 2 (07:03:09Z).
   - `python3.14 -I -S -B c12r2_cell306.py seal-only` →
     `C12R2 SEALED 276f4d416175086640c982ac4cda7c9cf703fccb (seal-only; status TARGET_EVALUATED; nothing computed)`,
     exit 0 (07:03:21Z–07:03:22Z).
   - The snapshot covered:
     - HEAD;
     - a digest of the full `for-each-ref`;
     - refs/c12r2, refs/c12r1 and refs/c12;
     - the status line count and digest (with `--ignored`);
     - a digest of the git-dir listing;
     - a digest of the common refs/c12r2 listing;
     - the index mtime, size and sha256;
     - the loose-object count;
     - the result file's inode, nlink, size and mtime;
     - the execution-directory listing;
     - whether an emergency file exists;
     - the last three HEAD reflog entries.
   - Result: the snapshots before and after are **identical**. No loose object and no `__pycache__` was created.
8. **History.**
   - `git log --all` for every prior-result path and for the authorization/ and evidence/execution directories of C12,
     C12-R1 and C12-R2.
   - Per-file commit history for every review, adjudication and status file of C12, C12-R1, floor r2, C11, C11R,
     C11RD and C2.
   - r5's blob in HEAD and in the worktree.
   - K5_COVERAGE_MAP_R6 in the tree, in all history, in all reachable objects and on disk.
9. **Timing.** Sub-second mtimes of the probe blob, trial commit, marker, result blob, pending ref, seal tree, seal
   commit, branch ref, execution directory, worktree copy and index.
10. **Operator material, read only:**
    - scratchpad/c12r2/EXECUTE.log;
    - dryrun.sh, dry2.log and official.log;
    - a listing of scratchpad/c12r2/dry (refs and result files only).

## Findings

### 1. Chain freeze → qualification → review → grant → seal: EXACT

- **Parents.**
  - The grant's parent is exactly e19f4edd.
  - **NB10:** the seal's parent is exactly the grant commit, dec92e09.
  - Every link has a single parent. There are no merges in 13e06db0..HEAD, which holds exactly 5 commits.
- **File sets.**
  - The grant commit adds only authorization/C12R2_GRANT.json.
  - The seal commit adds only evidence/execution/C12R2_CELL306_RESULT.json.
  - The review commit adds only the review file. None of the qualification reviewer's probe files were committed, which
    satisfies NB12's operational constraint.
- **NB12: no intervening or unrelated commits.**
  - The HEAD and branch reflogs run …13e06db0 → 11f91daf → 107a8b36 → e19f4edd → dec92e09 → 276f4d41, with no other
    entry. The seal entry has an empty message, from `update-ref`.
  - `git diff --name-only 13e06db0 HEAD` touches only NS: 13 files, 0 outside.
- **Frozen code and protocol.**
  - The sha256 of D, grant.py, r6 generator, verify.py, PROTOCOL.md and FREEZE.json is identical at 11f91daf, at HEAD
    and in the worktree:

    | file | sha256 prefix |
    |---|---|
    | D | 5c45b4de |
    | grant.py | 83ec10cc |
    | r6 generator | 23a831c9 |
    | verify.py | 3c748f11 |
    | PROTOCOL.md | 874a5610 |
    | FREEZE.json | 23deb827 |

  - The last commit touching code/ and protocol/ is 11f91daf, which is what D's `freeze_commit()` derives.
- **Grant hashes.** Every hash in the grant equals the frozen value: driver, verifier, r6 generator, grant generator,
  protocol and freeze record.
- **Timestamps.**

  | event | time (Z) |
  |---|---|
  | grant commit | 06:40:36 |
  | execute start (record) | 06:41:48.398872 |
  | seal commit | 06:41:50 |

### 2. Explicit user authorization, as recorded in the grant: PRESENT (see NOTE 1)

- `authorization.source` records "a SEPARATE explicit user authorization for the C12-R2 grant / exactly-once execution
  phase, given after QUALIFICATION_ACCEPTED was preserved".
- `authorizes` is exactly one `execute` at HEAD = the grant commit, in the qualified worktree.
- `target` is cell 306, m 5, Gamma(5, 306; S_I2), with 1 evaluation.
- `not_authorized` includes a second execute, moving or deleting the marker, cells 307–309, modifying r5, r6 outside
  the generator, and changing frozen code, inputs or thresholds.
- The grant fields also bind:
  - `exactly_once` true;
  - the schema grant.v1;
  - the freeze, qualification and review commits;
  - the review verdict;
  - the qualified identity.
- The caller relays that the user authorized, in chat: the grant, one real evaluation, sealing, and this review and its
  preservation. The grant is consistent with that scope: it authorizes execution only, not floor application,
  adoption or r6.

### 3. Exactly-once marker semantics: HOLD

- **Markers.**
  - `refs/c12r2/cell306-target-consumed` = dec92e0983fe39bcf9834e62216daeab09f823a4, a commit, which is the grant commit.
  - `refs/c12r2/cell306-pending-result` = 0ac46b3d2abe497084ddf7631d894bb819e6ddc6, a blob, which is the result blob.
- **Nothing else.** `for-each-ref refs/c12r2 refs/c12r1 refs/c12` lists exactly these two.
- **NB1: no junk.**
  - `<common-dir>/refs/c12r2` holds exactly two regular files, each 41 bytes with nlink 1, and no subdirectory.
  - `<common-dir>/refs/c12r1` and `<common-dir>/refs/c12` do not exist.
  - packed-refs has no c12 entry. Its only "c12" matches are the hash prefix c123b9bb of main and origin/main.
  - There are no per-worktree refs under the git dir.
  - There are no reflogs for refs/c12r2.
  - The ref backend is files, since `extensions.refstorage` is unset.
- **Creation order.** Both refs have mtimes inside the run (see 5). The marker was created by a CAS from the zero oid
  (D:875), so it cannot have pre-existed. Otherwise execute would have refused.

### 4. Real evaluation count = 1; no pre-grant evaluation: CONFIRMED

- **The record.** It says `target_evaluations` 1 and `target_evaluated` true, with a single `target` block.
- **The object store** holds all 29,612 objects, including unreachable ones.
  - **Exactly one** blob carries the C12-R2 result schema: 0ac46b3d, 19,937 bytes. The only other blob containing that
    string is the driver source itself, fab98a27.
  - **Exactly one** "c12r2 trial commit object" exists: def4e453, parent dec92e09, committed in the same second as the
    seal.
    - The trial commit is created in `check_seal_preconditions`, which runs only after `check_grant` passes, that is
      with HEAD = the grant.
    - So exactly one execute invocation ever passed the grant check, and it did so at the grant commit.
  - No C12 or C12-R1 result record exists. The blobs matching those schema strings are their driver sources,
    3dab30b6 and 836209ba.
  - No emergency or POST_MARKER record blob exists. The matches are the verifier, the qualification JSON, the review
    and FREEZE.json.
- **History.**
  - `git log --all` for the C12-R2 result path gives only 276f4d41.
  - The C12-R1 and C12 result paths, and their evidence/execution and authorization/ directories, have no history.
  - The grant path gives only dec92e09.
- **Before the grant.**
  - The grant generator ran `check_not_evaluated` at e19f4edd before committing. That check refuses on any ref under
    the three prefixes, any prior result in the tree, on disk or in any history, and any emergency file.
  - The qualification report at 107a8b36 records:
    - `real_target_evaluations` 0;
    - `markers_and_pending_refs` [];
    - `result_path_objects` [];
    - `grant_exists` false;
    - `seal_exists` false.
- **Qualification ran decoys only.**
  - Sandbox B holds only decoy I2 inputs (`B_contains_no_real_I2_file` true).
  - Both sandboxes are `--shared` clones in $TMPDIR built from 11f91daf. Their refs and objects are their own, and no
    sandbox marker or trial commit appears in the real store.
  - In the real worktree only these ran:
    - preflight;
    - I1-only rehearsals for 305 and 306;
    - an execute refused GRANT_MISSING.
  - The qualification review (§10) independently confirms that no verifier path computes Gamma under the real S_I2.
- **The operator's pre-freeze dry runs.** These are scratchpad/c12r2/dryrun.sh and dry/, at 14:07–14:42+09:00. They
  ran in a `--shared` scratch clone at 13e06db0 with a stand-in freeze. That clone has no c12r2 refs and no result
  file, and its CLI execute would be refused by identity. See NOTE 5.

### 5. Result persistence and blob identity: EXACT; seal integrity HOLDS

- **One blob everywhere.** These are all equal to 0ac46b3d2abe497084ddf7631d894bb819e6ddc6:
  - the pending blob;
  - HEAD:<result> (`ls-tree`: `100644 blob 0ac46b3d…`);
  - the index entry (`100644 0ac46b3d… 0`);
  - `git hash-object` of the worktree copy;
  - the Python SHA-1 of `blob 19937\0` + the bytes.
- **The bytes.**
  - The worktree bytes, the pending blob and the HEAD blob are byte-identical.
  - They are 19,937 bytes, with sha256 bbe31d0a2b3f4966b3961a94ee5644b97ad48ca5ba8ae15b1264c6cf33e325ea.
- **Self-hash.** The record's `sha256`, recomputed over the body without it using `json.dumps(sort_keys=True)`,
  verifies. The canonical `indent=1, sort_keys=True` re-serialization plus a newline is byte-identical to the file.
- **Seal message.** The commit says "SEAL … (TARGET_EVALUATED)" and "Committed by … from the in-memory bytes". It does
  not say "sealed by seal-only".
- **Order of writes** (sub-second mtimes, Z), exactly the R3 order:

  | time (Z) | write |
  |---|---|
  | 06:41:50.269155 | probe blob |
  | 06:41:50.324641 | trial commit |
  | 06:41:50.379607 | marker |
  | 06:41:50.383202 | record `finished_utc` |
  | 06:41:50.392474 | result blob |
  | 06:41:50.401219 | pending ref |
  | 06:41:50.467887 | seal tree |
  | 06:41:50.481559 | seal commit |
  | 06:41:50.490855 | branch ref |
  | 06:41:50.520468 | evidence/execution directory |
  | 06:41:50.520802 | worktree copy |

  The worktree file was written only after the seal.

### 6. Pending/fallback paths: primary channel only; no recovery path used

- There is no `c12r2-cell306-emergency-result.json` in /Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-k5c11rd.
  `find` over the common dir for `*emergency*` finds nothing either.
- The operator log shows the normal path, with no UNSEALED, CONSUMED_UNRECORDED or exit-7 line:
  - `start_utc 2026-09-27T06:41:48Z`;
  - `C12R2 SEALED 276f4d41… (status TARGET_EVALUATED; one target evaluation; result not printed)`;
  - `driver_exit=0`;
  - `end_utc 2026-09-27T06:41:50Z`.
- The seal was made by `execute` itself: the commit message and the time order above show it.
- The later `seal-only` runs, the operator's and mine, found the HEAD entry equal to the pending blob and the worktree
  copy equal to the bytes. So they neither sealed nor materialized.

### 7. No-follow, exclusive, no external redirection: HOLDS

- The worktree copy is a regular file with nlink 1, mode 0644 and inode 27068837. It was read with O_NOFOLLOW.
- No path component is a symlink. Every component from /Users through `evidence/execution` is a real directory
  (lstat), and the worktree root's realpath equals itself.
- NS contains 0 symlinks and 0 objects other than regular files and directories.
- `evidence/execution` contains only C12R2_CELL306_RESULT.json. `ls -A` shows no hidden entries.
- The execution directory was created 0.3 ms before the file (see 5), consistent with materialize's fresh `mkdir` and
  O_EXCL create.
- A copy outside the tree would need a second link or a redirect. nlink 1 and the absence of symlinks exclude both.

### 8. Retry refusal; seal-only computes nothing: CONFIRMED

- **My execute probe** was refused `CONSUMED: a ref exists under refs/c12r2/` with exit 2.
  - D's `run_execute` reaches `check_not_evaluated` right after `check_flags` and `check_identity`.
  - That is before `check_seal_preconditions`, the only pre-marker writer, so nothing is written.
- **My seal-only probe** printed `nothing computed` with exit 0.
- **State.** The pre- and post-probe snapshots are identical:
  - HEAD 276f4d41;
  - the full refs digest df240ed5…;
  - the two c12r2 refs;
  - status 0 lines (with `--ignored` and `--untracked-files=all`);
  - the git-dir listing;
  - the common refs/c12r2 listing;
  - the index mtime and sha256;
  - the loose-object count 5640;
  - the result inode, nlink and mtime;
  - no emergency file.
  No loose object and no `__pycache__` appeared after the probes.
- **Static.** The transitive local call closure of `run_seal_only` is:
  - check_flags;
  - check_identity;
  - git;
  - git_blob_id;
  - git_dir;
  - materialize (only if the worktree copy is absent);
  - persist_pending (only if there is an emergency file and no pending ref);
  - seal_blob (only if HEAD has no entry);
  - seal_message.

  No consumer, control, preparation, evaluation, supply or atom function is reachable. At this state, all three
  conditional writers are skipped.
- **The operator's reported probes** (a second execute refused CONSUMED, exit 2; seal-only "nothing computed", exit 0)
  are consistent with this. HEAD and branch reflogs have no entry after 06:41:50Z. See NOTE 3 for the index.

### 9. Content of the sealed record (read-only): CONSISTENT

- **Top-level fields.**
  - schema: `rebaseguard.p5y.k5.tail-c12r2.cell306-result.v1`;
  - status: TARGET_EVALUATED;
  - cell 306, m 5;
  - `target_evaluated` true;
  - `target_evaluations` 1;
  - `consumed_ref`: refs/c12r2/cell306-target-consumed;
  - floor: "r2 (rule a15d083b, review 3fadb422)";
  - python 3.14.5.
- **Run metrics.**
  - started 2026-09-27T06:41:48.398872Z;
  - finished 06:41:50.383202Z;
  - wall 1.984 s;
  - cpu 0.215 s;
  - peak RSS 38,371,328.
- **Grant block.** All fields equal the actual commits:
  - grant_commit dec92e09…;
  - freeze_commit 11f91daf…;
  - qualification_commit 107a8b36…;
  - qualification_review_commit e19f4edd….

  `grant_sha256` ef59ad21… equals the sha256 of the grant file at dec92e09. `seal_preconditions.branch_head` is dec92e09.
- **Identity block.** It is exactly the qualified worktree, git dir, common dir and branch.
- **`driver_sha256`** equals the frozen driver hash, 5c45b4de….
- **`input_sha256`** has 32 keys, identical to the frozen `input_pins_sha256` keys, and all 32 values equal the pins.
  All 32 pinned inputs still have those sha256 values in the worktree, and their HEAD blobs match the frozen blob
  prefixes.
- **`governance_state_before`.** r5 union open ranges [[306, 309]], r6 absent.
- **Control** (cell 306, supply "S_I1 = min{G, C1, C2}").
  - `reproduces_C2_exactly` true, and all 7 `field_matches` are true.
  - My own string comparison with C2_D5_FORECAST.json `cells["306"]` agrees on Gamma_exact, A_exact, H_exact,
    M_after_exact, pass and provenance.
  - Provenance is A0/A1/A2 = C2.
- **Target block** (cell 306, supply "S_I2 = min{G, I2}", provenance A0/A1/A2 = I2).
  - The Gamma_exact string has 1,484 characters and sha256 8ef2815c…. Its leading character is a digit, not '-', and
    parsing the sealed string confirms the sign is positive.
  - The float is 0.005159101140006536, with the same sign.
  - `pass` is false, which agrees with the sign of Gamma_exact: the consumer defines pass as Gamma < 0.
- **Advisory `floor_r2_table`.** It is internally consistent with the two pass flags, control true and target false:
  - base_clause_Gamma_S_I1_lt_0: true;
  - F1_prime_d_both_supplies_lt_0: false;
  - F1_prime: false;
  - floor_r2_satisfied_mechanically: false;
  - scientific_closure: {S_I1: true, S_I2: false};
  - F2: NOT_SATISFIED (not re-evaluated).
- **Not applied.** I did not apply floor r2 and made no adoption determination.

### 10. NB7 preserved: CONFIRMED

- The qualification review is the only file e19f4edd changes. Its blob, 79af9392, is identical at e19f4edd, at HEAD
  and in the worktree.
- Its NB7 text is intact: C12-R1's N1 is "only partially repaired"; P:93-96 and V:4-6 overstate; the actual
  cross-campaign barriers are sound.
- PROTOCOL.md and c12r2_verify.py are unchanged since the freeze, so the overstatement NB7 refers to is preserved
  rather than silently edited.
- C12R1_QUALIFICATION_REVIEW.md has a single commit, e89402c1.
- No document was edited after the review. The only later commits are the grant and the seal, one new file each.

### 11. r5, r6, cells 307–309, historical verdicts: UNCHANGED

- **r5.** K5_COVERAGE_MAP_R5.json is blob f978eeb6b41188eabaf3c6d590c9178d711f1ce6 in HEAD and in the worktree. Its only
  commit is ae4cbc2c.
- **r6.** No K5_COVERAGE_MAP_R6 exists in the HEAD tree, in `git log --all`, among the reachable objects or on disk.
- **Cells 307–309.** Nothing outside NS changed since 13e06db0, so they are untouched. The driver refuses cells
  other than 305 and 306, and the record is cell 306 only.
- **Historical verdict files.** Each has exactly one commit, its preservation commit, and no commit since 13e06db0
  touches these namespaces:

  | campaign | file | commit |
  |---|---|---|
  | C12 | C12 review | 2cdfa467 |
  | C12 | C12 status | eba56027 |
  | C12-R1 | C12-R1 review and its probe files | e89402c1 |
  | C12-R1 | C12-R1 status | 13e06db0 |
  | floor r2 | FLOOR_R2_REVIEW.md | 3fadb422 |
  | N9 | adjudication | 7d67989d |
  | N9 | adjudication review | fb237288 |
  | C11RD | authorization review | e320d8f5 |
  | C11RD | execution review | db1c6118 |
  | C11RD | comparison review | 90265349 |
  | C11RD | qualification and pre-execution reviews | 89330534, e27c2ffd, 663f8fe7, 3c1eff11 |
  | C11R | adjudication | 118008f5 |
  | C11R | authorization review | 9bd17be5 |
  | C11R | execution review | 22537709 |
  | C11R | comparison review | 7375b9cd |
  | C11R | qualification review | 445fd84e |
  | C11R | pre-freeze reviews R1-R8 | one commit each |
  | C11 | ADJUDICATION_C11.md | 25475205 |
  | C2 | C2_ADJUDICATION.md | ae4cbc2c |
  | C2 | pre-freeze reviews | one commit each |

  C11R_STATUS.json has 7 commits, the last at ee1a6a8a on 2026-09-25. It is a status file, not a verdict, and is
  unchanged since then.

## BLOCKERS

None.

## NON-BLOCKING NOTES

**NOTE 1 — The grant records the user authorization only as generator boilerplate.**
- `authorization.source` is fixed text from the frozen c12r2_grant.py. The user's actual words, the time and the
  narrower chat scope are not in the repository. That scope excludes floor-r2 application, adoption, r6 and 307–309.
- The grant is consistent with that scope: it authorizes only the one execute. But it does not itself exclude the
  adoption adjudication, which the protocol (§4) lists as a later step.
- That step still needs its own explicit authorization, as the caller states.

**NOTE 2 — The post-seal probes are outside the grant's literal wording.**
- `not_authorized` lists "any second execute", and `authorizes` allows seal-only "only after an UNSEALED exit".
- The operator ran one extra `execute` and one `seal-only` after exit 0. This review ran one of each, as its
  instructions permit.
- Each extra execute was refused CONSUMED before any write or evaluation. Each seal-only was a read-only verification.
  I confirmed both by the state diff and by the static call closure.
- None of them is an evaluation, so exactly-once is unaffected. The record of this phase should describe them as
  refusal and verification probes, not executions.

**NOTE 3 — The worktree index was rewritten at 06:42:47.834852Z, about 57 s after the seal.**
- The driver's own alignment of the index was at 06:41:50. This later write is consistent with a plain `git status`
  refreshing stat data, run without `GIT_OPTIONAL_LOCKS=0`.
- Its content is correct: the status is empty, and the entry for the result is 100644 0ac46b3d.
- It has no effect on the seal. It is noted for the record, since it did not come from the driver.

**NOTE 4 — Unrelated activity in the shared common dir during this review.**
- `refs/heads/p5y-k4-frozen-execution-r1` moved from 5289b6ce to bc4ba08e. `refs/heads/p5y-k4r1-nearzero-successor` and
  `refs/remotes/origin/p5y-k4-frozen-execution-r1` appeared.
- The objects of the K4 commit bc4ba08e were written at 06:44:32Z.
- All of this came from another worktree. It is not on this branch, not in NS, and did not touch refs/c12r2 or this
  branch. It happened before my probe snapshots, which are identical.
- It is noted because the exactly-once phase shares its object store and refs with concurrent sessions.

**NOTE 5 — The operator ran pre-freeze dry runs outside the repository.**
- scratchpad/c12r2/dryrun.sh, dry/ and dry2.log: FAIL 179/181, identity-related, as expected in a scratch clone.
- The clone is `--shared` at 13e06db0. It has no c12r2 refs and no result files, and cannot pass the identity check.
- pre.json, r305.json and r306.json (14:07+09:00) are I1-only preflight and rehearsal outputs.
- None of this evaluates the target. It is noted for completeness.

**NOTE 6 — The latent residuals of the qualification review did not trigger.**
- The run took the normal path: exit 0, pending-ref channel, sealed, materialized. So NB2, NB3, NB4, NB5, NB6 and NB11
  never came into play.
- NB1, NB10 and NB12 are confirmed clean (findings 1 and 3).
- NB9 is moot: the committed review blob equals the worktree copy (79af9392).
- NB8 is consistent: only the primary channel was written, and there is no emergency file.

**NOTE 7 — The seal's reflog entry has an empty message.**
- `update-ref` was run without `-m` (D:716). This is cosmetic.

**NOTE 8 — Loose objects from the pre-marker probe remain in the object store, as designed.**
- These are the probe blob b83cc6f5 and the trial commit def4e453. No ref points at either.
- They are harmless, and useful: the single trial commit is independent forensic evidence of one invocation past the
  grant check.
- They should not be pruned before the adjudication.

## Sealed result as recorded (no adoption judgement)

**Target: Gamma(5, 306; S_I2), supply min{G, I2}, provenance I2 for A0/A1/A2.**
- The sign of Gamma_exact is **positive**.
- The float is **0.005159101140006536**.
- `pass` is **false**.
- The exact string has 1,484 characters, with sha256 8ef2815cd478b43b05605e0ddefebd318568446194090327ffabc0e50b59e194.

**Control: Gamma(5, 306; S_I1), supply min{G, C1, C2}, provenance C2.**
- The sign of Gamma_exact is **negative**.
- The float is **-0.030469257709306738**.
- `pass` is **true**.
- It reproduces C2's published cell-306 record exactly, all 7 fields.

**Advisory table as sealed** (not applied by this review):
- base true;
- F1′(d) false;
- F1′ false;
- floor_r2_satisfied_mechanically false;
- F2 NOT_SATISFIED.

## Confirmation

- **I modified nothing.**
  - I ran no git write command in /Users/suzhe/ReBaseGuard-k5c11rd and created or modified no file or ref there.
  - Every git command ran with `GIT_OPTIONAL_LOCKS=0`.
  - The only driver invocations were the two single probes in finding 8. The state snapshot is identical before and
    after them.
  - At the end: HEAD is 276f4d41, the refs are unchanged, status is empty, and there is no emergency file.
- **I recomputed nothing.**
  - I evaluated no Gamma and no atom constant under any supply, real or synthetic.
  - I did not call prepare_target, evaluate_target, control, direct or supply.
  - I did not run the verifier or rehearse.
  - The sealed signs were read from the sealed strings.
- **No D1/D2 values.** I printed, wrote and quoted no numeric value of D1 or D2, original or independent. The sealed
  record contains no D1/D2 field. I did not open C11R's quarantine.
- **Nothing else.** I used no AWS or Vultr tool, no network and no session transcript.
- **Where I wrote.** Only in …/scratchpad/c12r2_exec_review/: this file, the snapshots, the probe logs and three
  read-only helper scripts.
