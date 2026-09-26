# C11RD-R1 comparison review
COMPARISON_ACCEPTED

| item | value |
|---|---|
| reviewer | fresh, independent, read-only comparison reviewer (Claude Opus 5.5 subagent); no stake in the result; the aborted earlier attempt's scratch (scratchpad/c11rd_cmp_review) was neither read nor relied on |
| date | 2026-09-26 |
| worktree | /Users/suzhe/ReBaseGuard-k5c11rd (linked; common dir /Users/suzhe/ReBaseGuard/.git), branch p5y-k5-tail-c11rd-d1d2-extension |
| HEAD | 8e2defab13451654a87a859e1b24fb1b28dc9494 (comparison commit) |
| lineage | 8e2defab -> db1c6118 (execution review) -> 4547bcd4 (seal) -> 4b716d43 (grant G) ... ce5b8595 (freeze R1) |
| NS | level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension |
| scope | comparator provenance, exactly-once, inputs, frozen rule, arithmetic, evidence integrity, out-of-scope absence. N9/K5 are NOT adjudicated here. |
| read-only | `GIT_OPTIONAL_LOCKS=0 git status --porcelain --ignored --untracked-files=all` printed 0 lines before and after every step; nothing was written outside this scratch directory; the comparator was never run as a program and its `main()` was never called |

## Summary

The frozen comparator ran once. Its output is exactly what the frozen rule gives for the recorded inputs.

* The comparator file and all 8 C11RD code files match the freeze's `code_sha256`. C7's `c7_gaussian.py` matches its binding too.
* The artifact is the only file the comparison commit adds. Its committed bytes equal the disk bytes. Its embedded sha256 checks out.
* The artifact appears in exactly one commit (8e2defab) across all refs, all reflogs, the full history and every worktree. No unreachable commit holds it. The frozen U0 (`run_once_problems()`) now refuses on two grounds: the artifact is on disk, and it is in 1 reachable commit.
* Every input is the frozen one:
  * the seal, byte-identical at the seal, at HEAD and on disk;
  * the execution review, with exactly one EXECUTION_ACCEPTED line;
  * the quarantine (blob 219e0122) and C11R's accepted comparison (blob 5269c2aa);
  * the statement table (blob 58b4066f), whose factor is 2.
* Statements come before numbers. D1 and D2 are both EQUIVALENT (domain EQUAL, premises SAME).
* My exact Fraction recomputation of all 4 sub-blocks, done my own way from the freeze's F_derivative_recurrence, reproduces every recorded bound. The frozen `recompute()` returns no problems. The cell values are the maxima over the sub-blocks.
* Both targets are STRONGER under the factor-2 UPPER_BOUND rule (independent <= original, not exactly equal):
  * D1 ratio: exact rational of 152/152 digits, float 0.45362884480385873;
  * D2 ratio: exact rational of 246/247 digits, float 0.0557333083728129.
* The U7 leak check over the 42 files at the freeze commit finds nothing. My own independent value-based scan also finds nothing, as does an extra scan at HEAD.
* The six-class N9 reassembly is C_T AGREES, tau AGREES, Abar STRONGER, D_lo AGREES, D1 STRONGER, D2 STRONGER. The mechanical output is therefore N9_CLOSED, as recorded.
* Nothing is out of scope:
  * no science re-run; the runs directory is unchanged since the seal, and the consumed ref is still G;
  * cells 307-309, r5, r6 and adoption are untouched;
  * the frozen code, protocol and theory are unchanged;
  * local main is c123b9bb and origin/main is 1cb45382, both unchanged.

No blockers.

## Findings per item

### 1. Provenance — PASS
* **Code hashes.** The on-disk sha256 of all 8 code files equals the freeze's `code_sha256`, and `c11rd_compare.py` = e299186a…c2b41d. C7 `c7_gaussian.py` sha256 = bd73b5b4…a9815 and blob = be492720, both as bound.
* **Unchanged trees.** The code tree is 1c2ec31f at the freeze ce5b8595, at G, at the seal and at HEAD. The protocol tree (1102720d) and theory tree (0d4bce62) are identical at the freeze, at G and at HEAD. The freeze file is blob 770b378d at the freeze commit, at HEAD and on disk.
* **Documents.** All 8 `document_sha256` entries match on disk.
* **Artifact commits.** `seal_commit` = 4547bcd4…, `execution_review_commit` = db1c6118…, `freeze_commit` = ce5b8595…. The schema is `c11rd.comparison.v1` and the key set is exactly the one the comparator writes.
* **Comparison commit.** 8e2defab has the single parent db1c6118. `git diff-tree` shows exactly one path: `A …/evidence/comparison/C11RD_COMPARISON.json`. The whole-tree diff from db1c6118 to HEAD is that one file.
* **Committed bytes = disk bytes.** Blob 7151f57a matches at HEAD and on disk, `cmp` confirms byte equality, and the file sha256 is 8a9637b6…391b06.
* **Embedded sha256.** sha256(json.dumps(body without "sha256", sort_keys=True)) = f69c2bf0…665bae0, equal to the embedded field. Re-serialising the parsed artifact with `indent=1, sort_keys=True` plus a newline reproduces the file bytes exactly, which is consistent with the comparator's own write path.

### 2. Exactly once — PASS
* **Full-history search.** I ran `git rev-list --all --reflog --full-history` over the artifact path, over the whole comparison directory, and over any path matching `*C11RD_COMPARISON*`, with replace objects and the commit-graph disabled. All three return only 8e2defab.
* **Refs and reflogs.** The only ref containing 8e2defab (or db1c6118) is the campaign branch. The branch reflog and the worktree HEAD reflog each show one comparison commit. The stash is empty.
* **Repository integrity.** The repository is not shallow, and there is no grafts file, no shallow file and no replace ref.
* **Unreachable commits.** `git fsck --unreachable` lists 10 unreachable commits. All date from 2026-09-13 or 2026-09-16 (old stashes and one review commit), and none holds the comparison path.
* **Every worktree.** Across all 34 registered worktrees, the only file named `*C11RD_COMPARISON*` on disk is the one at HEAD.
* **U0 now refuses.** I imported the frozen module read-only (-I -S -B, barrier passed) and called the pure `c11rd_compare.run_once_problems()`. It returns `['a comparison artifact exists on disk', 'a comparison artifact was in reachable history (1 commits, e.g. 8e2defab1345)']`, so the comparator would now refuse.
* **Invocation record.** It shows `invocation: 1` with the stated cwd, command and sanitised environment. The output line is `N9_VERDICT = N9_CLOSED; D1 STRONGER, D2 STRONGER`, the exit code is 0, and the run spans 12:33:37.02Z to 12:33:38Z. The artifact mtime (21:33:38 +0900, i.e. 12:33:38Z) falls inside that window, and the commit follows at 12:34:39Z. No other `*COMPARATOR_INVOCATION*` file exists under /private/tmp/claude-501 (task outputs excluded). No comparator or runner process is running.
* **Nothing else written by the run.**
  * Worktree: after the execution review commit time, the only new file is the artifact (plus its directory).
  * Common dir: after the seal, only the campaign branch ref, its reflog and this worktree's HEAD log changed, all from the commits.
  * Refs sorted by committer date: only the campaign branch is newer than G.

### 3. Correct inputs — PASS
* **Seal.**
  * `evidence/runs/C11RD_RUNS.json` is byte-identical at 4547bcd4, at HEAD and on disk (sha256 c28a8cea…709cc0).
  * Its `freeze_commit` = ce5b8595, its `code_sha256` equals the freeze's, and its status is CERTIFIED (execution and both targets).
  * mode = real, cell = 306, head = `authorization_review_commit` = G.
  * All four runs files (lock, log, journal, runs) have the same blob at the seal, at HEAD and on disk.
  * Ancestry holds: freeze ⊂ G ⊂ seal ⊂ review ⊂ 8e2defab ⊆ HEAD.
* **Execution review.** At db1c6118, `review/C11RD_EXECUTION_REVIEW.md` has exactly one whole-line verdict: EXECUTION_ACCEPTED on line 2, with no rejection line. Commit db1c6118 adds only that file, and its blob 7037189f is unchanged at HEAD and on disk.
* **Quarantine.**
  * The blob is 219e0122a7febf4347ce9205e5e5ed9f18b20ffb on disk, at HEAD, at C11R's final head 7375b9cd and at the C11R branch tip. It equals both the comparator's constant and the freeze's binding.
  * I verified this before loading the file.
  * The artifact's `original_value` strings equal `str(Fraction(quarantine value))` for D1 and D2 exactly.
* **C11R accepted comparison.** Blob 5269c2aa is identical on disk, at HEAD and at 7375b9cd. Its review, REVIEW_C11R_COMPARISON.md (preserved at 7375b9cd), carries a comparison-accepted verdict. The comparison records C_T AGREES, tau AGREES, Abar STRONGER, D_lo AGREES; `per_target` and `classes` agree.
* **Statement table.** Blob 58b4066f is identical on disk and at HEAD. It declares CONTAINS_NO_ORIGINAL_MAGNITUDE = true and carries no D1/D2 value field. `comparison_semantics_frozen_before_results` has factor 2 and the UPPER_BOUND rule "STRONGER: independent <= original; AGREES: original < independent <= 2*original; INSUFFICIENT: independent > 2*original".
* **Other bound inputs.**
  * C11R schema blob 0526426c, C11R runs blob a5351603 and C11R equiv blob 6531eb8d are all unchanged.
  * The whole C11R namespace is unchanged since the entry head 7375b9cd.
  * The premise from the frozen loader `c11rd_model.c11r_fh_premise()` (C_T = tau) equals the freeze's F.premise and the runs record.
  * The kappa values from `kernel_norms()` equal the runs record.
  * My 1200-digit Decimal check shows that kappa_1 >= 2·phi(0) and kappa_2 >= 4·phi(1) (slack about 8e-97 each), so both are sound upper ends.
  * `cell_block()` equals the freeze's C_drift_block.

### 4. The frozen rule — PASS
* **Statement before number.**
  * The frozen `compare_statement(table.original_statements[k], runs.targets[k].statement)` returns `{'STATUS': 'EQUIVALENT', 'domain': 'EQUAL', 'premises': 'SAME'}` for D1 and for D2. This equals the artifact's `statement` entries.
  * My own implementation, built on C11R's frozen schema constants, also returns EQUIVALENT: exact fields equal, drift domain equal as exact rationals, and premise sets {C_T_independent, tau_independent} normalising to {C_T, tau}.
  * The independent records also equal the freeze's A/B statement records field by field, including route `independent_derivative_propagation`.
  * The producer is `c11rd_runs.py`, whose file_sha256 is the freeze's.
  * There is no independence violation (`independence_violations` = []).
* **Factor-2 UPPER_BOUND rule.** The direction is UPPER_BOUND in both the table and the artifact. For D1 and D2 alike, independent <= original holds, so the class is STRONGER. The frozen `classify_numeric` and my own rule agree, and the artifact's `numeric.class` and `factor` = 2 match.
* **U6 exact equality.** Independent ≠ original for both targets, so there is no INVALID from copying.
* **N9 precedence.** The artifact's precedence list equals the freeze's L.n9 order. My own reassembly gives N9_CLOSED: no violation, no DISAGREES, no INVALID, all six AGREES or STRONGER. This equals `n9_verdict(classes, [])` and the artifact's `N9_VERDICT`.

### 5. Arithmetic — PASS
* **U3 (frozen).** `c11rd_compare.recompute(runs, premise, kappa, block)`, called with the frozen loaders, returns [] (no problems).
* **U3 (independent).** I wrote my own Fraction code from the freeze's F_derivative_recurrence text, using C_T and tau as frozen and kappa as recorded and verified:
  * n0 = C_T·lam0 and n1 = C_T·(lam1 + kappa_1·n0);
  * D1_j = |D1(a)| + |D2(a)|·de + |D3(a)|·de²/2 + tau·(lam1 + kappa_1·n0);
  * D2_j = |D2(a)| + |D3(a)|·de + tau·(lam2 + 2·kappa_1·n1 + kappa_2·n0).

  For each of the 4 sub-blocks, the recorded D1_j and D2_j, the recorded propagation (n0, n1, err_D1, err_D2) and the recorded atom bounds all equal my recomputation exactly. The recorded atom values equal the band-0 constant terms of the candidates' exact monomial (p^i m^j) polynomials, which are their values at a = (0,0). All lam are >= 0.
* **Partition.** The sub-blocks equal the freeze's D_sub_block_partition and tile the cell block in 4 equal widths exactly.
* **Aggregation.** The cell values `targets.D1.value` / `targets.D2.value` (and `execution.D1/D2`) equal the maxima over the 4 sub-blocks. The argmax is sub-block 0 for both. The artifact's `independent_value` strings equal the runs values verbatim.
* **Ratios.** Exact v/o:
  * D1: numerator 152 digits, denominator 152 digits, float 0.45362884480385873;
  * D2: numerator 246 digits, denominator 247 digits, float 0.0557333083728129.

  Both equal the artifact's `ratio` strings exactly and its `ratio_float` bit for bit.
* **Classes.** D1 STRONGER, D2 STRONGER. With C11R's C_T, tau, Abar and D_lo classes, the six-class reassembly is N9_CLOSED.
* **U7.**
  * I re-ran the frozen `leak_hits` over `git ls-tree -r` of the NS at the freeze commit, with originals rendered as `format(float(v), '.9f')`. It covers 42 files and returns {}, matching the artifact's `leak_check` = {files: 42, hits: {}}.
  * My own value-based scan of the same 42 files also returns no hits. It covers decimal, integer and scientific tokens, normalised by value, matched against 4-30-significant-digit truncations and half-even/half-up roundings of the exact originals.
  * Extra scan, not a frozen gate: the NS at HEAD, 74 files with the artifact excluded. Both the frozen function and my scan return no hits.

### 6. Evidence integrity and out-of-scope absence — PASS
* **No science re-run.**
  * The runs directory (lock, log, journal, runs) is unchanged since the seal.
  * The journal records one launch: preflight_pass, consumed, runner_starting, runner_exited 0, and one seal attempt ending COMPLETED_CERTIFIED.
  * `refs/c11rd/r1-execution-consumed` = 4b716d43 (G).
  * The only changes G..HEAD are the 4 seal files, the execution review and the comparison artifact.
* **Nothing touched outside the namespace.** `git diff 7375b9cd HEAD` outside the C11RD NS is empty. So cells 307-309, the C2 coverage map and C11R are all untouched, and no changed path matches 307/308/309.
* **r5, r6, adoption.** r5 `K5_COVERAGE_MAP_R5.json` is blob f978eeb6 at the entry and at HEAD (sha256 e2197051…). No r6 file and no adoption file exist.
* **Main refs.** refs/heads/main = c123b9bb8f15d17650545b3fce4aca8a6b61093b and refs/remotes/origin/main = 1cb453826313c189f0bdafd5b84120c1edb74da9, both unchanged.
* **Frozen code, protocol, theory.** Unchanged (see item 1).

## BLOCKERS
none

## NON-BLOCKING NOTES
1. **Route tables are a restricted mirror of C11R's schema.** `c11rd_compare`'s ROUTE_REQUIRED_DEPENDENCIES and ROUTE_CAN_PRODUCE copy C11R's frozen `c11r_schema` tables but keep only the one route this campaign uses, `independent_derivative_propagation`. Its entries are identical to C11R's. All other mirrored constants (EXACT_FIELDS, STATEMENT_FIELDS, CONVENTION, VALID_AGGREGATION, INDEPENDENT_ROUTES, FORBIDDEN_PRODUCERS, SIX) are equal in full. Any other route would fail closed as "cannot produce", so the result is unaffected. My full-equality probe flagged this as an informational difference, and the check restricted to the used route passes.
2. **A toy fixture shares the artifact's name.** A 3-byte `{}` file named `C11RD_COMPARISON.json` exists in a separate toy git repository at `scratchpad/c11rd_review_r1/histtest/envother/…`, created 2026-09-26 02:45 +0900. The pre-execution reviewer made it to test U0's history detection. It is not in the ReBaseGuard repository or its history and is not a comparator output. The authorization reviewer's simulation copy (`scratchpad/c11rd_auth_review/sim`) holds the comparator source but no comparison artifact.
3. **The environment is attested only by the log.** The invocation environment and cwd rest on the invocation log alone, which lives outside the repository and is not hash-bound. The artifact's bytes, mtime and exact re-serialisation, and the U0 state, all agree with a single run of the frozen code path.
4. **The consumed ref has no reflog.** `refs/c11rd/r1-execution-consumed` has no reflog, so only its current value (G) can be checked.
5. **Scope of this verdict.** The comparator's `N9_VERDICT` = N9_CLOSED is its mechanical output under the frozen rule. This review does not adjudicate N9 or K5. The four non-D classes are read from C11R's accepted comparison, not re-derived.
6. **Extra leak scan, beyond the frozen gate.** The frozen U7 covers the NS at the freeze commit only. My extra scan of the NS at HEAD, with the comparison artifact excluded, also found no rendering of either original.

## Commands run (all read-only; Python always `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -I -S -B`, run from the scratch directory or with inline `-c`)
* `GIT_OPTIONAL_LOCKS=0 git status --porcelain --ignored --untracked-files=all | wc -l` (0 before and after every step)
* `git rev-parse HEAD HEAD~1 HEAD~2 HEAD~3`, `git log --format='%H %P %ad %s' -5`, `git show --stat HEAD`
* `ls -la` of the NS directories; python `-c` printing freeze sections L, U, V, input_bindings, code_sha256, A, B, C, D, F, J, K, P, R, S, T, FORBIDDEN, frozen_parameters, target, successor_of, governance_at_freeze, document_sha256
* Read `code/c11rd_compare.py`, `code/c11rd_model.py`, `code/c11rd_certify.py`, and grepped `c11rd_tm.py`, `c11rd_float.py`, `c11rd_kernel.py` for import-time side effects
* `cat evidence/comparison/C11RD_COMPARISON.json`
* `shasum -a 256 code/*.py`; `git rev-parse <commit>:<path>` for the freeze file and the code/protocol/theory trees at ce5b8595, G, the seal and HEAD; `git hash-object --no-filters` on disk files; `shasum`/`git hash-object` on C7 `c7_gaussian.py`
* `git diff-tree --no-commit-id -r --root --name-status 8e2defab`; `git rev-list --parents -n1 8e2defab`; `git cat-file -p HEAD:<artifact> | cmp - <artifact>`; `git diff --stat db1c6118 HEAD`; `git diff --name-status` for seal..review and G..seal
* `cat` of the invocation log; `ls` of scratchpad/r1qr1
* `git worktree list --porcelain`; `git rev-parse --is-shallow-repository`; grafts/shallow/replace-ref checks; `git --no-replace-objects -c core.commitGraph=false rev-list --all --reflog --full-history -- <artifact path>` (also over the comparison dir); `git log --all --reflog --full-history --name-only -- '*C11RD_COMPARISON*'`
* `git for-each-ref --contains 8e2defab` and `--contains db1c6118`; `git reflog show` for the branch and HEAD; `git stash list`; disk scan of every worktree for the comparison directory and `*C11RD_COMPARISON*`
* `git fsck --unreachable --no-progress` (commits listed to scratch), then `git log -1` and `git ls-tree` of each unreachable commit
* `git for-each-ref` (non-branch refs, c11rd refs); `git rev-parse refs/heads/main refs/remotes/origin/main`
* `git show db1c6118:<review>` verdict-line extraction; review blob at db1c6118, HEAD and on disk; runs-dir blobs at the seal, HEAD and on disk; `cat` of the lock and launch journal; grep of the execution log
* C11R input blobs at HEAD, 7375b9cd, on disk and at the branch tip; `git diff 7375b9cd HEAD` outside the NS; C11R comparison review verdict grep; python `-c` summarising the C11R comparison classes
* grep of `c11r_equiv.py` and `c11r_schema.py` APIs and constants; grep of `c11rd_float.exact_candidate` (monomial basis)
* `verify.py` (sha256 00cb0f75…a651) in this scratch directory, run under `env -i PATH=/usr/bin:/bin HOME=/var/empty LANG=C GIT_NO_REPLACE_OBJECTS=1 GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_OPTIONAL_LOCKS=0`. It imports the frozen modules read-only and calls only the pure `run_once_problems`, `recompute`, `compare_statement`, `classify_numeric`, `n9_verdict` and `leak_hits` plus the frozen `c11rd_model` loaders, then does my own recomputation, statement comparison, classification, reassembly and leak scan. Output is in `verify_out2.txt` (sha256 91715414…ef8c): 57 PASS; the one informational full-equality probe is explained in note 1.
* `diag.py` (constant-mirror diff; kappa slack at 1200 digits)
* `find -newermt` on the worktree, the NS and the common-dir refs/logs; `git for-each-ref --sort=-committerdate --count=6`
* `grep -rl` of /private/tmp/claude-501 (excluding *.jsonl, tasks/ and the review scratch directories) for comparator invocations; `find` for `*COMPARATOR_INVOCATION*` and `*C11RD_COMPARISON*` in scratch; `ls`/`stat`/`head -c` of the histtest fixture and the auth-review sim copy; `ps` for comparator/runner processes
* python `-c` checking `document_sha256` on disk; `git ls-tree` checks for r5/r6/adoption; r5 blob at the entry and HEAD and its sha256; `git diff --name-status G HEAD`
