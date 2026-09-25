# C11RD-R1 pre-execution review
READY_TO_QUALIFY

Reviewer: fresh, independent, read-only. Worktree `/Users/suzhe/ReBaseGuard-k5c11rd`, branch
`p5y-k5-tail-c11rd-d1d2-extension`, HEAD = successor freeze commit
`ce5b85959a1693525f9e001e7c191516a4ee7d76` (parent `663f8fe7`, grandparent `71495747`). Date 2026-09-26.
The worktree was clean before and after every check (`git status --porcelain --ignored
--untracked-files=all` printed 0 lines each time).

## Scope and what I ran

I read the following in full:
* the predecessor review `663f8fe7:review/C11RD_PRE_EXECUTION_REVIEW.md` (B-1, N-1..N-12);
* `docs/C11RD_R1_REPAIR.md`, `protocol/C11RD_FREEZE_R1.md` and `.json`;
* `theory/D1_D2_DERIVATION.md` (section 1 with Proposition 1, Lemma 4, Theorem 5);
* all eight code files: `c11rd_runs.py`, `c11rd_compare.py`, `c11rd_certify.py`, `c11rd_kernel.py`
  and `c11rd_model.py` in full; the changed parts of `c11rd_float.py`; `c11rd_validate.py` V01-V29
  in full;
* the rehearsal_r1 and validation_r1 evidence, and the full diff `71495747..ce5b8595`.

I executed:
* the frozen validation, `python3 -I -S -B code/c11rd_validate.py --out <review>/review_validation.json`.
  Result: VALIDATION_CLASS = PASS, 29/29.
* recomputation of the sha256 of the freeze, the 8 code files, the 7 bound documents, the
  calibration file, the committed validation JSON and C7's `c7_gaussian.py`, plus the git blob ids of
  all 8 input bindings at `ce5b8595`, `71495747` and `7375b9cd`;
* a key-by-key diff of the predecessor freeze JSON against the successor, and the byte comparison of
  the two rehearsals;
* a check that V18's 17 hashes equal `value_patterns` of the two disclosed values, and a broader leak
  scan of my own;
* history and scope checks;
* NON-TARGET checks of my own at drift 5/2 or on the non-target block only, plus scratch-repository
  git tests. These are listed under items 3, 4, 7 and 8 and in the command list.

What I did not do:
* compute anything at a drift in [3/2, 5/2) or at any cell 306-309 drift;
* run `c11rd_runs.py` in any mode, run `c11rd_compare.py`'s main, create a grant, or start any C11R
  runner;
* open the C11R quarantine, `C11R_COMPARISON.json`, `REGISTRY_C2.json` or any original cell or
  denominator artifact (I only ran `git rev-parse` on their blob ids).

I wrote only under `scratchpad/c11rd_review_r1/`.

## Findings per item

### 1. The B-1 repair — CLOSED

`theory/D1_D2_DERIVATION.md:49-97` replaces the false lower-closed paragraph. It defines one candidate
on R through `own(x)`:
* band 0 on s in [0, 1];
* band k on s in (k, k + 1] for k = 1, 2, 3, axis points included;
* band 4 on axis points with s in (4, 5].

It then proves Proposition 1 from the partition hypothesis. I checked every step of (b) against the
kernel, which is byte-identical to the predecessor's:
* `c11rd_kernel.state_values` evaluates the box's own band (`cand[bx.band]`, or `('A', axis)` for
  band 4).
* `pieces_tm` (`c11rd_kernel.py:162-183`) produces the middle tag `('M', k-1)`. The middle image lies
  on s' = s - 1, in (k - 1, k] for s in (k, k + 1], so band k - 1 owns it (band 0 owns (0, 1]).
* The partial arm piece `[s-1, k]` uses band k - 1. Its image lies in (k - 1, k] except for one
  measure-zero point.
* The full arm pieces of image band j use `restrict_axis(cand[j])` for j <= 3 and `('A', axis)` for
  j = 4. Owner j holds on (j, j + 1]; the endpoint j has measure zero.
* At s = 1 the middle and the atom window have zero length.
* The atom (s = 0) is band 0's point for every theta, and D_k(a) is band 0's constant coefficient
  (`atom_values`; the monomials are p^i m^j, `c11rd_float.exact_candidate`).
* Boxes of a non-owning band contain x only at their lower band edge, or at s = 4 on an axis for band
  4. They add extra values to the maximum, which can only enlarge lam_k.

Hence sup_R |r_k| <= lam_k with ONE single-valued bounded candidate, which is exactly Theorem 5's
hypothesis. The predecessor's counterexample (interior (2, 2), s = 4) is now owned by band 3. V24
row "interior s=4 on" shows that the band-3 box encloses the exact upper-closed Khat of the jump
candidate there. `c11rd_float.py` now describes fitting only, and the dead lower-closed `band_of` is
gone. The convention is also stated in freeze E.band_ownership, and "any change of the
band-ownership convention" is added to the forbidden list.

### 2. Exact upper-closed ownership in production code — PASS

`c11rd_certify.owner_band` (`c11rd_certify.py:33-45`):
* returns 0 for s <= 1, else `ceil(s) - 1`, using exact `Fraction` arithmetic;
* refuses points outside R (`MD.in_R`).

This is exactly [0, 1] -> 0, (k, k + 1] -> k, and axis (4, 5] -> 4. Band 4 is reachable only on the
axes because interior points of R have s <= 4. Checks:
* My spot checks give (0,0)->0, (1/2,1/2)->0, (1,1)->1, (2,2)->3, (4,0)->3, (0,9/2)->4 and (5,0)->4.
  (3, 3/2) is refused.
* V24 compares `owner_band` with an independently written `frozen_convention_owner` on 49 points:
  below, on and above every line s = 1..4, interior (two directions) and both axes, the atom and the
  s = 5 ends. All are equal.
* Replacing production `owner_band` by the lower-closed reading makes V24 FAIL (my mutation M2,
  item 4).

`box_contains` treats boxes as closed, including edges and the atom.

### 3. Completeness of the closed-box cover; per-box formula = candidate residual — PASS

`verify_cover` (`c11rd_certify.py:70-101`) is an exact check, with no sampling:
* for each band k = 0..3, the s-rows partition [k, k + 1] (sorted, abutting, non-degenerate);
* in every row, the theta-cells partition [-1, 1];
* on each axis, the band-4 segments partition [4, 5].

That is Proposition 1's hypothesis for the grid initial cover. Refinement keeps the partition
(`Box.split` bisects; V22).

Runner guard R6 (`c11rd_runs.py:411-418`) calls it before the grant, R3 and the lock.

My negative controls on the non-target block (duplicate box; overlapping extra box; dropped band-0
theta cell; dropped band-4 m-segment; a gap in the band-1 s-rows) are all refused. The frozen
168-box cover passes.

On a rational grid of step 1/32 (8,449 points of R, including every band line and both axes), every
point has an owning box (`owning_boxes`).

The per-box formula equals the candidate's residual: see item 1. There is no gap, and no double value:
the candidate is defined once by `own`, and other boxes only add further maxima. See N-13 on R6
checking the whole-block box list rather than the per-sub-block lists (equivalent here).

### 4. V24 jump-at-band-line control — PASS (it can fail; the negative controls are real)

V24 (`c11rd_validate.py:1234-1285`) runs production `initial_boxes`, `owner_band`, `owning_boxes`,
`verify_cover`, `verify_ownership`, `Box`, `state_values` and `kernel_box`. Its candidate is 1, 10,
100, 1000 and 10000 on bands 0-4, so it jumps at every line. It compares against an exact reference,
`khat_reference`, that does not use the kernel: C7 Phi on the window split at every kink and integer
crossing, with the owner taken at each piece midpoint.

Negative controls:
* production `verify_ownership` with the reversed owner FAILS on interior s = 4, at (2,2) and
  (8/3,4/3);
* removing one band-3 box FAILS `verify_cover`.

My mutations of production code, applied in memory at e = 5/2 only:

| mutation | V24 result |
|---|---|
| M1: middle uses band k instead of k - 1 | FAIL, 36 points |
| M2: lower-closed `owner_band` | FAIL, 16 points, plus the per-line exclusion check |
| M3: partial arm uses band k | FAIL, 26 points |
| M4: only band-3 boxes' middle switched | FAIL, 12 points |

So V24 would fail if either the ownership or the kernel's band choice were reversed. It is not
vacuous.

One weakness (N-2): its "reversed value excluded" assertion can be met by the state value alone. My
check shows the Khat enclosure itself also excludes the reversed exact Khat at all 12 on-line points
of s = 2, 3, 4 (gaps of 1e-2 to 7e2). At s = 1 the two conventions give the same Khat: the middle has
zero length and the arm endpoints have measure zero. So only the state value can distinguish that
line, and V24 does check it.

### 5. Lemma 4 endpoint repair and V25 — PASS

I re-derived each step:
* (a) w >= 1 + Khat w and Khat w >= 0 give w >= 1. With w <= C_T this gives Khat w <= (1 - 1/C_T) w,
  so ||Khat^N|| <= q^N C_T.
* (b) ||Khat_f|| <= 1. Telescoping gives ||Khat_f^N - Khat_e0^N|| <= N kappa_1 rho = 1/4, so
  ||Khat_f^N|| <= 3/4. The Neumann series converges with norm <= 4N on the open set U = E + (-rho, rho).
  It is the same series that defines d.
* (c) The resolvent identity with the uniform bound, plus the kappa_2 (and kappa_3) Taylor bounds,
  gives operator-norm C^2 on U, so the endpoints of E carry two-sided derivatives.
* (d) The closed sub-blocks, u_e = +-1 inside the closed TM domain, F_H on the closed block, and
  Theorem 5 applied pointwise cover every endpoint. At shared endpoints the maximum still holds.

This closes the predecessor's N-1.

V25 passes all 72 endpoint checks, the exact drift-coordinate check (`ec +- de` = the endpoints) and
the atom-bound check. Its numerical containment has little discriminating power (N-3). The exact
structural check and the proof carry the weight.

### 6. Production-path V15 — PASS

V15 builds synthetic runs records and judges them only through `c11rd_compare.recompute` (U3). The
validation-local `verify_claim` is gone (`"verify_claim" not in globals()`). The honest record is
accepted. Each of the following is refused through the production path:
* the sign-flipped D1 candidate (its lam1 rises from 2.7e-5 to 2.1e-3 on the band-1 box);
* the flipped h_1' sign;
* zero kappa;
* D1 and D2 claims one unit in the 12th place too low.

U3 cannot detect an under-reported lam, which is inherent: lam is run evidence, examined at the
execution review. That was already so before this round.

### 7. Host / worktree / freeze / qualification / authorization binding — PASS (notes N-4, N-5, N-6, N-8, N-11)

`grant_problems` (`c11rd_runs.py:220-276`) binds the following:
* ALLOW, campaign C11RD, target {306, block, [D1, D2]}, `max_executions == 1`;
* code and input hashes;
* host {hostname, IOPlatformUUID via `/usr/sbin/ioreg`, platform, Python};
* worktree {realpath toplevel, realpath git common dir}. The canonical path must also equal the
  resolved repo and contain the resolved code dir. `MD.REPO` comes from `Path(__file__).resolve()`,
  so a symlink alias resolves to the checkout it names.
* the freeze commit is an ancestor of HEAD, the freeze file is byte-identical there, and its sha256 is
  bound;
* the qualification commit, its artifact blob (the same at HEAD) and a review with exactly one
  QUALIFICATION_ACCEPTED line and no REJECTED line;
* `--authorization-review-commit` with exactly one AUTHORIZATION_ACCEPTED line and the byte-identical
  grant;
* the lineage via 40-hex `merge-base --is-ancestor`, so an empty or missing id fails;
* no shallow repository.

The grant path is fixed and may not be a symlink. R3 then forces it to be committed.

Every linked worktree of this repository shares the common dir, so the path check is what refuses
them.

V26 passes 26 checks: 21 single-deviation refusals, two positive controls, the production identity
functions, and "an alias resolves to the bound checkout".

My fail-closed checks:
* a missing ioreg gives REFUSE R2;
* a non-git directory gives REFUSE R2;
* an empty grant gives 10 distinct problems;
* no grant file gives REFUSE R2.

I found no way to evade the binding through a symlink or alias, or through a second checkout. What
remains needs deliberate acts: environment or PATH manipulation of the governance git calls (N-5),
deleting the worktree-local lock before sealing (N-6), or editing the on-disk freeze to steer a
nontarget rehearsal (N-4). None of these is a path a legitimate operator could take by accident.

### 8. Comparison run-once history protection — PASS (note N-7)

`c11rd_model.history_commits` (`c11rd_model.py:75-98`) is used by both U0 and R4. It:
* runs with a sanitised environment (`PATH=/usr/bin:/bin`, `GIT_NO_REPLACE_OBJECTS=1`);
* uses `--no-replace-objects` and `core.commitGraph=false`;
* refuses shallow repositories (both the rev-parse check and the `shallow` file), an `info/grafts`
  file, and any git error;
* runs `rev-list --all --reflog --full-history -- <paths>`.

V27 passes 13 cases:
* on disk;
* committed then deleted;
* reverted;
* merged, including `-s ours`;
* on an unmerged branch;
* behind a replace ref;
* in a stash;
* shallow and grafts (both fail closed);
* R4 on a shallow repository;
* the real repository is clean.

My extra scratch-repository tests (git 2.50.1):
* an artifact committed only in a DETACHED linked worktree is found;
* a `stash -u` untracked parent is found;
* `GIT_DIR` pointing at another repository is ignored by the sanitised reader;
* a commit made unreachable (branch deleted and reflogs expired) is NOT found. This is inherent to
  "reachable history", which is what the freeze states.

`run_once_problems` is the first action of `main` (`c11rd_compare.py:382`).

### 9. Replacement-worker memory monitoring — PASS (note N-11)

`process_tree_rss_kb` sums RSS over the root and all live descendants from one `ps -A -o
pid=,ppid=,rss=` snapshot. It returns None, which becomes RESOURCE_ACCOUNTING_FAILED, when:
* `ps` is missing or returns non-zero;
* any line is malformed;
* the root is missing.

`parallel_cover` samples at pool start and then every 30 to 60 s, before `it.next(timeout=30)`. Any
non-OK status terminates the pool and gives NOT_CERTIFIED. R7 runs before the lock.

V28 passes 9 checks on a real spawn tree whose workers replace each other: replacement PIDs are
seen, concurrent memory is counted, a low cap is reported, and unreadable, malformed and missing-root
tables all fail closed.

The rehearsal_r1 records 11-12 samples per sub-block and 18-19 distinct PIDs. That count includes the
per-sample `ps` child, which confirms that late children are counted.

### 10. Scientific identity against 71495747 — PASS (confirmed independently of V29)

**Freeze JSON.** My key-by-key diff shows these fields identical:

A_D1_statement, B_D2_statement, C, D, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, FORBIDDEN,
frozen_parameters, resource_caps, target, nontarget_rehearsal_block, input_bindings,
governance_at_freeze, entry_head, branch, V.

V29's `IDENTITY_FIELDS` omits A and B; I checked those two myself. The changed fields are:
* E, which only gains `band_ownership` (`initial_boxes` and `refinement` are unchanged);
* U, which gains U0, the token normalisation and the module path;
* campaign, schema, code/document hashes, runner_guards, and the validation and rehearsal evidence
  paths;
* new bookkeeping keys.

**Code.**
* `c11rd_tm.py` and `c11rd_kernel.py` are byte-identical to the predecessor (empty diff).
* The diffs of `c11rd_float.py`, `c11rd_model.py` and `c11rd_certify.py` are only docstrings,
  additions and the removal of the dead `Basis.band_of`. V29 confirms this with 128 predecessor
  definitions compared by AST: none changed, only `band_of` removed, and `band_of` had no call site.
* `certify_block` differs only by the added `resource_accounting` key.
* `parallel_cover` changes only in its monitoring. It still uses the same `initial_boxes`,
  `refine_box` and `merge`.

**Rehearsal.** In `evidence/rehearsal_r1/C11RD_REHEARSAL_NT.json` against
`evidence/rehearsal/C11RD_REHEARSAL_NT.json`:
* status, D1 and D2 are equal;
* every per-sub-block key is equal (e_lo, e_hi, D1, D2, the atom bounds and values, lam, propagation,
  cover, float_proposal and candidates), except the added `resource_accounting`.

The freeze file the rehearsal used (the author's scratch copy) is byte-identical (`cmp`) to the
committed R1 freeze. The rehearsal's JSON and log sha256 equal its manifest.

No scientific parameter, computation or cover geometry changed.

### 11. Target leak scan — PASS (note N-10)

* **V18 hashes.** `value_patterns` of the two disclosed values, hashed, is exactly V18's 17-element
  set.
* **V18 rerun.** It scanned all 42 namespace files with 0 hits. It now normalises bare-point and
  scientific renderings, and both controls pass. The committed run scanned 38 files; the 4
  evidence files written after it are covered by `POST_WRITE_LEAK_SCAN.json` (41 files plus itself,
  clean) and by my rerun.
* **My broader scan** covered all 42 files at `ce5b8595`:
  * decimal tokens with any 4-9-digit rendering prefix: 0 hits;
  * scientific notation with an integer mantissa within 1e-3: 0 hits;
  * all 7,605 rational strings, checked for values within 1e-4 relative of either original: 0 hits;
  * leading significant-digit substrings of 5 or more digits anywhere: the only hits sit in the
    middle of 13-digit dyadic numerators of the non-target candidates, identical in both rehearsals.
    These are coincidences, not renderings. The 4-digit hits are coincidental too.
  * Positive controls fired.

### 12. Independence — PASS

* V16 passes:
  * no forbidden import, statically or at runtime (94 modules, fresh `-I -S -B` interpreter,
    return code 0);
  * no forbidden data reference;
  * the negative controls, including the new runner-review controls, fire.
* V17 passes (allowlisted literals, planted-magnitude control).
* The refined runner rule is sound:
  * The science modules name no review at all.
  * The runner reads only the freeze, the grant, the statement table and the F_H runs (both
    blob-bound), and git objects: the freeze at the freeze commit, the qualification and
    authorization review lines, the grant at the review commit, and the qualification artifact's blob
    id only. I checked this with a grep of every file read.
  * These are PRE-RESULT governance files. No target value exists before execution, so reading them
    cannot leak one.
  * The runner names no execution, comparison or C11R review.
* C7's `c7_gaussian.py` is unchanged (sha256 and blob equal the freeze).

### 13. Validation — PASS, 29/29 reproduced

My rerun equals the committed `evidence/validation_r1/C11RD_VALIDATION.json` test by test, except for:
* timings;
* V18 `files_scanned` (42 vs 38; see item 11);
* V28's sample count and peak RSS, which depend on timing.

The committed JSON sha256 equals the manifest's `output_sha256`. The manifest's freeze and code hashes
equal the committed ones.

### 14. Historical immutability — PASS

* `git diff --name-only 7375b9cd ce5b8595` has 0 paths outside the namespace, so C11R, C11, C7, C2
  and r5 are untouched.
* `protocol/C11RD_FREEZE.json` and `.md` show no diff `71495747..ce5b8595`; the predecessor freeze
  sha256 is 4e3bd6c0..., equal to `successor_of`.
* The predecessor review has the same blob (`dbf1dd03`) at `663f8fe7` and `ce5b8595`.
* `663f8fe7` only added that review.
* The only commits touching the namespace on any ref or reflog are `71495747`, `663f8fe7` and
  `ce5b8595`.
* There is no coverage-map r6 file (the only r5 file is `K5_COVERAGE_MAP_R5.json` in the C2
  namespace, unchanged).
* main = `c123b9bb` and origin/main = `1cb45382`, as recorded.
* All 8 input blobs are identical at `ce5b8595`, `71495747` and `7375b9cd`. The F_H runs blob equals
  the seal `5ff4cc5b`.

### 15. Absence of target computation — PASS

* There is no `evidence/runs`, `evidence/comparison`, lock or `config/` directory on disk.
* No commit on any ref or reflog ever touched those paths.
* The rehearsal_r1 ran on the non-target block [5/2, 3233337/1250000]. Its log shows counters and
  timings only.
* The author's scratch directory holds no script that computes at a cell 306-309 drift. The only
  target-block strings there are inside code-patch text and freeze generators.
* R6 builds `Box` objects on cell 306's block in both modes. This is geometry plus trivial affine
  drift TMs only: no candidate, no kernel, no residual and no magnitude (see N-4).

### Disposition table (docs/C11RD_R1_REPAIR.md section 3) — accurate

| note | my judgement |
|---|---|
| N-1 | Correctly repaired. |
| N-2 | Correctly repaired. |
| N-3 | Correctly repaired, and V24 is real. |
| N-4 | Correct for the float module. An analogous lower-closed helper survives in validation (my N-1). |
| N-5 | Repaired. |
| N-6 | Repaired, with the residuals N-4, N-5, N-6 and N-8 below. |
| N-7 | Legitimately ACCEPTED_LIMITATION: it touches tightness and the cost of a NOT_CERTIFIED outcome only. |
| N-8 | Legitimately ACCEPTED_LIMITATION: disclosed, and the certifier never reads it. |
| N-9 | Repaired for decimal, bare-point and point-mantissa scientific renderings. The rational and integer-mantissa residual is accepted, and my scan shows it clean at this freeze (N-10). |
| N-10 | Repaired. |
| N-11 | Repaired. |
| N-12 | Repaired. |

## BLOCKERS

none

## NON-BLOCKING NOTES

**N-1. A validation helper still uses the lower-closed reading.** `code/c11rd_validate.py:62-82`
(`point_box`, line 67 `k = 0 if s < 1 else min(4, int(math.floor(s)))`).
* Its docstring says "the band that owns (p, m)", but it implements the lower-closed reading.
* For an interior point with s = 4 it would build a band-4 m-axis box at (0, 4).
* No sample state reaches that case, and V02-V04, V10-V12 and V14 use globally continuous candidates,
  so no outcome depends on it.
* Align it with `owner_band` or `owning_boxes` in a later round.

**N-2. V24's exclusion check is weaker than it could be.** `code/c11rd_validate.py:1260-1265`.
* The "reversed value excluded" condition can be met by the state value alone.
* Consider asserting kernel-level exclusion on the s = 2, 3, 4 lines. It holds today (item 4).
* V24 also exercises only order-0 Khat, though all orders share `pieces_tm`.

**N-3. V25's numerical containment has little discriminating power.** `code/c11rd_validate.py:1304-1326`.
* Its order-4 enclosures at u_e = +-1 are about 1e-4 (r0) to 1e-3 (r2) wide, while the float
  residuals are about 1e-7 to 1e-5, so containment is nearly automatic.
* The exact check `ec +- de == endpoints` and the proof carry the endpoint claim. Do not cite V25 as a
  sharp numerical test.

**N-4. Nontarget mode trusts the on-disk freeze.** `code/c11rd_runs.py:155-159, 490-506`.
* It does not check the freeze's integrity: `load_freeze` checks only the schema, and R1 compares the
  code against the same on-disk file.
* The rehearsal-block guard only requires disjointness from cell 306's block.
* So a deliberately edited, uncommitted freeze could make a rehearsal compute next to cell 306's
  block, or on cells 307-309, with no grant and no lock. This requires tampering with a frozen file,
  which is no easier than calling the library directly, so it is not a failure of the governed path.
* Cheap hardening:
  * in nontarget mode, require the freeze to equal HEAD's committed blob;
  * refuse rehearsal blocks that meet [3/2, 5/2).

**N-5. Governance git calls inherit the caller's environment.** `code/c11rd_runs.py:111-116` (`git_run`)
and `code/c11rd_compare.py:123-125`.
* These calls inherit PATH and any `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` or `GIT_CONFIG_*`
  variables. Only `MD.history_commits` sanitises the environment.
* A stray `GIT_DIR` changes the worktree identity, so the run is refused: fail closed. Only a
  deliberate forgery could get past it.
* Use `GIT_ENV` and an absolute `/usr/bin/git` for every governance git call.

**N-6. The lock is still local to the worktree.** `code/c11rd_runs.py:297-310`.
* Between a run and its seal, a second run becomes possible if someone deletes the untracked lock and
  artifact, or removes and re-adds the worktree at the same path, which keeps the same path and
  common dir. That is deliberate only.
* Seal immediately after the run.
* Optionally also create a create-only ref, which R4's `--all` would see.

**N-7. The history reader sees only reachable history.** `code/c11rd_model.py:75-98`.
* A commit made unreachable (branch deleted and reflogs expired) is not found; I confirmed this in a
  scratch repository.
* This is inherent, and the freeze correctly says "reachable history".

**N-8. Some qualification fields are supplied by the grant.** `code/c11rd_runs.py:248-267`.
* The qualification `artifact_path` and `review_path` come from the grant; they are not fixed paths.
* `freeze_commit` may be any ancestor commit whose freeze file is byte-identical, not necessarily
  `ce5b8595`.
* The authorization review must check all three. Consider fixing the qualification review path, as
  was done for `AUTH_REVIEW_REL`.

**N-9. Some documents are stale.**
* `docs/C11RD_ARCHITECTURE.md:17` and `:94` still say "R0–R6"; R7 now also precedes the lock.
* The freeze's `K_success_failure` copies "R0-R6"; R7 is covered separately by
  `K_r1_additional_not_certified_reason`.
* `protocol/C11RD_FREEZE_R1.json:4` gives `entry_head` as the campaign entry `7375b9cd`, while
  `docs/C11RD_R1_REPAIR.md:3` gives the R1 entry as `663f8fe7`. `successor_of` binds `663f8fe7`
  explicitly, so nothing is ambiguous.

**N-10. The U7 tokeniser needs a decimal point.** `code/c11rd_compare.py:260`.
* Scientific notation with an integer mantissa, and exact rationals, are not value-scanned. This is
  the accepted residual of the predecessor's N-9.
* My rational-proximity and integer-mantissa scans show the namespace clean at this freeze.

**N-11. Fail-closed accounting can consume the execution.**
* A single transient `ps` failure mid-run ends the run NOT_CERTIFIED and consumes the execution
  (`code/c11rd_runs.py:382-387`).
* A hostname change under macOS network changes refuses before the lock (`:179`), which is harmless.
* The authorization should pin the host name and require an otherwise idle host with
  `caffeinate -i` (the predecessor's N-7).

**N-12. V26 omits a few single-field deviations.** It does not test platform-only, `input_bindings`,
or `git_common_dir`-only deviations, a QUALIFICATION_REJECTED review, or an ancestor freeze commit
with a different freeze file. The code handles all of these through the same equality checks, which
I read.

**N-13. R6 checks a different box list than the pool receives.** `code/c11rd_runs.py:411-418`.
* R6 verifies `initial_boxes` over the whole block, not the lists `parallel_cover` builds per
  sub-block (`:374`).
* The function, splits and geometry are the same and do not depend on the drift interval, so this is
  equivalent.
* Checking the exact list handed to the pool would be tighter.

## Commands I ran

All commands were read-only in the worktree. Outputs went only to `scratchpad/c11rd_review_r1`. The
two disclosed values are REDACTED below.

```
cd /Users/suzhe/ReBaseGuard-k5c11rd && git status && git log --oneline -8 && git rev-parse HEAD
find <ns> -type f | xargs wc -c ; git diff --stat 71495747 ce5b8595
cat review/C11RD_PRE_EXECUTION_REVIEW.md docs/C11RD_R1_REPAIR.md protocol/C11RD_FREEZE_R1.md protocol/C11RD_FREEZE_R1.json theory/D1_D2_DERIVATION.md
cat -n code/c11rd_certify.py code/c11rd_kernel.py code/c11rd_model.py code/c11rd_runs.py code/c11rd_compare.py ; Read c11rd_validate.py 1-1785
git diff 71495747 ce5b8595 -- code/c11rd_float.py code/c11rd_model.py code/c11rd_certify.py code/c11rd_runs.py code/c11rd_compare.py code/c11rd_validate.py docs/C11RD_ARCHITECTURE.md docs/C11RD_INDEPENDENCE_AUDIT.md theory/D1_D2_DERIVATION.md
git diff --stat 71495747 ce5b8595 -- code/c11rd_tm.py code/c11rd_kernel.py        (empty)
cd code && python3 -I -S -B c11rd_validate.py --out <review>/review_validation.json   (29/29 PASS)
python3 -I -S -B -  <compare review_validation.json with evidence/validation_r1/C11RD_VALIDATION.json modulo timings>
shasum -a 256 protocol/*.json code/*.py docs/*.md theory/*.md protocol/C11RD_FREEZE_R1.md evidence/calibration/C11RD_CALIBRATION.json evidence/validation_r1/C11RD_VALIDATION.json ../p5y_k5_tail_c7_e2_lambda309/code/c7_gaussian.py
git rev-parse {ce5b8595,71495747,7375b9cd}:<each input_bindings path> ; git rev-parse 5ff4cc5b:<C11R_RUNS.json>
git diff --name-only 7375b9cd ce5b8595 | grep -v '^<ns>/' | wc -l ; git diff --stat 71495747 ce5b8595 -- protocol/C11RD_FREEZE.json protocol/C11RD_FREEZE.md
git rev-parse 663f8fe7:<review> ce5b8595:<review> ; git diff --name-status 71495747 663f8fe7 ; git rev-list --parents -n 3 ce5b8595
git --no-replace-objects -c core.commitGraph=false rev-list --all --reflog --full-history -- <ns> ; ... -- <ns>/evidence/runs <ns>/evidence/comparison <ns>/config | wc -l
git rev-parse main origin/main HEAD ; git worktree list ; git ls-tree -r --name-only ce5b8595 | grep -iE 'coverage.?map' ; git --version
python3 -I -S -B - <key-by-key diff of 71495747:protocol/C11RD_FREEZE.json vs protocol/C11RD_FREEZE_R1.json>
python3 -I -S -B - <rehearsal vs rehearsal_r1: status, D1, D2 and per-sub-block key comparison>
shasum -a 256 evidence/rehearsal_r1/* ; cmp scratchpad/c11rd/freeze_r1_used_by_rehearsal.json protocol/C11RD_FREEZE_R1.json
cd code && python3 -I -S -B - <<EOF  <V18 hash check: value_patterns('<D1 REDACTED>') | value_patterns('<D2 REDACTED>') hashed == V.ORIGINAL_PATTERN_SHA256;
   broad leak scan of all 42 files at ce5b8595 (decimal prefixes, 5+-digit substrings, rationals within 1e-4, integer-mantissa sci-notation; positive controls); prints counts and masked contexts only>  EOF
python3 -I -S -B - <locate the containing digit run of each substring hit in rehearsal_r1 (masked)>
ls scratchpad/c11rd ; grep -lE '<target-block rationals and 1.70-1.78 decimals>' scratchpad/c11rd/{*.py,*.sh,*.log,*.txt} (USER_INSTRUCTION.txt excluded, not opened); grep -nE on r1_patch_*.py, finish_r1.py, make_freeze_r1.py
python3 -I -S -B scratchpad/c11rd_review_r1/v24_mutations.py     (V24 honest + mutations M1-M4 at e = 5/2; on-line kernel exclusion)
python3 -I -S -B scratchpad/c11rd_review_r1/cover_v25_check.py   (verify_cover negative controls; owner_band spot checks; 1/32 grid ownership; V25 enclosure widths on the NT sub-block)
python3 -I -S -B scratchpad/c11rd_review_r1/hist_check.py        (scratch repos: detached linked worktree, stash -u, purged branch, GIT_DIR in env)
python3 -I -S -B scratchpad/c11rd_review_r1/failclosed.py        (host_identity with missing ioreg, worktree_identity on non-git dir, empty grant, missing grant)
grep -nE 'read_text|read_bytes|open\(|"show"|_load_bound' code/c11rd_{runs,model,certify,kernel,float,tm}.py
grep -rnE 'half-open|lower-closed|...' code docs theory protocol/C11RD_FREEZE_R1.* ; grep -rn 'R0–R6|R0-R6' <ns>
cd <repo> && git status --porcelain --ignored --untracked-files=all | wc -l      (0, before and after every step)
```
