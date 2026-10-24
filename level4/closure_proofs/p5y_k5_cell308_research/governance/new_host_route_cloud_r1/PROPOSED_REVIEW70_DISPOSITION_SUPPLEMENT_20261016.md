# Proposed supplement: disposition of review 70 on the combined development source

**PROPOSED_NOT_ACCEPTED_NOT_IN_FORCE · DEVELOPMENT ONLY.** This supplement answers review 70
(`reviews/REVIEW_REVIEW69_REPAIR_DELTA.md`, recorded verbatim). Review 70 is a fresh bounded review of `dad3c948..9f223c91`.
This supplement accepts nothing and decides nothing.
* All 21 D-* decisions remain undecided, and `DECIDED` is empty.
* `JOURNAL_READER_REVIEWED = False` and `PIN_POINT_MODULES = None`.
* A1, A2 and A5 remain unmet.

Supplement r69 is not edited. Its §2 is **amended** by §2 below; everything not restated there stands. Its S2 row's
statements that RB5 and RB6 are "equivalent" are **withdrawn** (T1). The new source is bound by the ledger line of its
commit and by its own native run.

## 1. Findings

| finding (review 70) | disposition on the new source |
|---|---|
| T1 MINOR: RB5 and RB6 are stated equivalent; neither is | Withdrawn. RC1 (the review directory's own entry not read by mode) is registered as **RV64**. Its witness is the `review_dir_regular_file` subtest of the new test `test_review70_review_dir_file_evil_merge_and_odd_mode_refuse`: the review directory is a regular file in one commit; the history scan accepts that entry as a regular file, and only the walk refuses it. RC2 (the batch reads without `_git_env()`) is registered as **RV65**. It is killed **indirectly**, through `test_review65_caller_git_environment_is_ignored`, whose expected reason changes. The reviewer's forged-object-directory construction is not added as a direct witness. |
| T2 MINOR: merge commits' own trees are not pinned | The `evil_merge` subtest adds a merge whose own tree alone holds `level4 -> alt` with a rejection under `alt/…`. The history scan does not list that merge; the walk refuses it. RC3 (`--no-merges`) is registered as **RV66**. |
| T3 NOTE: sha256 width and directory-like odd modes are not pinned | `test_review70_sha256_repository_and_walk_parsing` accepts a legitimate sha256 repository (RC5, fixed 20-byte width, is **RV67**). The `odd_dir_mode` subtest puts a `40755` directory at `level4` in history; it refuses (RC4 is **RV68**). |
| T4 NOTE: S4 and the walk's integrity assumptions are unpinned and unstated | The new test calls `_cat_file_batch` directly: a missing object id gives None, with and without contents (RC7 is **RV70**). The `_review_dir_is_a_directory` docstring and §2 now state that `cat-file --batch` does not verify object hashes, so the walk relies on the strict fsck precondition over the same object store and on the isolated environment. The helper's own exception clause has no mutant (stated). |
| T5 NOTE: `_tree_entry` takes the last of duplicate entries | `_tree_entry` returns False (malformed) on a second entry with the same name. This is defence in depth, because strict fsck refuses duplicates first. The new test asserts it directly on raw tree bytes: **RV69** removes the check. |
| T6 NOTE: §2's checkout alternative is incomplete | The "or use a case-sensitive, non-normalising checkout" alternative is withdrawn. The D-HOST-LIFETIME procedure must read git tree paths and blob contents only (§2). |
| T7 NOTE: native run on 9f223c91 pending | Recorded by its own ledger line. |

## 2. Amendments to supplement r69 §2

* **Walk scope.** The ancestor walk covers every commit of HEAD's history, merges included (each merge's own tree).
  It reads the review directory's own entry by mode as well as its ancestors'.
* **Integrity.** `cat-file --batch` returns object contents without verifying their hashes. The history scan and the
  walk are only as trustworthy as the strict fsck that ran first over the same object store, together with the
  isolated environment (`_git_env()`, `_GIT_ISOLATION`). A change to the object store between the fsck and the reads
  is not detected (the check-to-read race already stated).
* **Duplicate tree entries** are refused by strict fsck. `_tree_entry` also treats them as malformed.
* **Checkout.** Replaces "The D-HOST-LIFETIME procedure must read tree paths only, or use a case-sensitive,
  non-normalising checkout". The D-HOST-LIFETIME procedure must read git tree paths and blob contents only, never a
  checkout. A checkout can differ from them in ways this check does not see:
  * case-insensitive or normalising file systems;
  * smudge/clean filters and `eol` / `core.autocrlf`, `ident` or `working-tree-encoding` attributes;
  * sparse checkout or skip-worktree;
  * untracked or modified working-tree files;
  * a checkout of a commit other than HEAD.
* **Performance.** The figure "1.8 s on a synthetic 30 000-commit linear history" was measured here on one
  construction (git 2.43). Review 70 measured 1.58 s and 2.43 s on two 30 000-commit constructions and 12.87 s at
  150 000 commits, roughly linear. Each git call has a 60 s limit, so much longer histories refuse.

## 3. Harness

Group RV grows to RV01–RV70, so the registry has 203 mutants.
* RV65 is witnessed indirectly (T1).
* The workflow expects 203 mutants and 204 suites. The suite has 229 tests.
