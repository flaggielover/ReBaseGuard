# Proposed supplement: disposition of review 69 on the combined development source

**PROPOSED_NOT_ACCEPTED_NOT_IN_FORCE · DEVELOPMENT ONLY.** This supplement answers review 69
(`reviews/REVIEW_REVIEW68_REPAIR_DELTA.md`, recorded verbatim). Review 69 is a fresh bounded review of `05caa00e..dad3c948`.
This supplement accepts nothing and decides nothing.
* All 21 D-* decisions remain undecided, and `DECIDED` is empty.
* `JOURNAL_READER_REVIEWED = False` and `PIN_POINT_MODULES = None`.
* A1, A2 and A5 remain unmet.

Supplement r68 is not edited. Its §2 is **replaced** by §2 below. Its statement that "it refuses the known ways a
checkout differs" is **withdrawn**. At dad3c948 its statement that an ancestor "ever a … gitlink" is refused was true
only when the gitlink's commit object was present (S1). The new source is bound by the ledger line of its commit and
by its own native run.

## 1. Findings

| finding (review 69) | disposition on the new source |
|---|---|
| S1 MINOR: a gitlink (submodule) at an ancestor of the review directory is ACCEPTED when its commit is absent; a gitlink-mode entry naming a tree passes too | `_review_dir_is_a_directory` now reads tree entries **by mode**. It takes every commit's root tree (`<commit>^{tree}`, which must answer `tree`), then walks down the components of the review directory. Each depth uses one `cat-file --batch` call over the distinct trees at that depth. An entry for the next component must be absent or have mode `40000`. Anything else refuses: a symlink, gitlink, file or odd mode, or a missing or malformed object. Test `test_review69_ancestor_entries_are_read_by_mode` has three gitlink subtests at `level4`: absent commit, present commit, and gitlink mode naming a tree. Mutant RV63 (RB4) reads a gitlink as a directory. |
| S2 MINOR: the ancestor check is pinned only through a top-level symlink on a linear history | The same test adds a symlink at a middle ancestor (RV61 = RB1), an ancestor symlink reachable only through an `-s ours` merge (RV62 = RB2), and an ancestor symlink checked under a caller `GIT_DIR`. RB6 (the batch call without `_git_env()`) is now **equivalent**, not registered: with a foreign `GIT_DIR`, the commits are missing in that repository, and a missing answer refuses (S4). RB5 (leaf omitted) stays equivalent, because the history scan refuses a non-directory review directory. It is not registered. |
| S3 NOTE: the widened RV26 no longer witnesses K7; the K7 mode check is unreachable | Stated. The P1 history scan refuses any symlink at HEAD under the directory before the K7 check, which is kept as unreachable defence in depth (code comment). RV26 is re-described as a K7 / P1 symlink witness, alongside RV59. The K7 test's docstring says so. |
| S4 NOTE: `<commit>:<path> missing` accepted when the commit is unreadable | The new `_cat_file_batch` refuses any `missing` answer. Paths are no longer looked up by name, so `missing` cannot stand for an absent path. |
| S5 NOTE: "refuses the known ways a checkout differs" overstated | Withdrawn. §2 lists the differences that are refused and those that are not: directory names that differ only by case or Unicode normalisation or ignorables, which a case-insensitive or normalising file system would merge. |
| S6 NOTE: records residue | The 1420-entry count is attributed to 9250f473. At f52e123f, the base of this repair, there are 1455 entries, all `100644` (tree read only). Native run 38812337420 on dad3c948 is recorded by its own ledger line. Ledger 518's `worktree_clean_after` is marked coordinator-asserted: `git status --short` in the worktree printed nothing after the run, and that output is not committed. |

## 2. What the completeness precondition and the history scan do (replaces supplement r68 §2)

`_history_complete` returns True only when all three of these hold, under the isolation:
1. `rev-parse --is-shallow-repository` prints exactly `false`.
2. `git config --includes --name-only --list` lists no `fsck.*` key and no partial-clone or promisor key.
3. `git fsck --full --strict --no-dangling` exits 0. WARN-class messages are errors; INFO-class messages pass.

After it, the history scan refuses as unavailable evidence, for any commit of HEAD's history:
* an entry under the review directory that is not a regular file (100644 / 100755);
* a review directory, or an ancestor of it, whose tree entry is not a directory (mode `40000`), read from the raw
  trees.

Any failure, timeout (60 s per git call), missing object or other answer refuses. Under the isolation:
* replace refs and grafts are ignored;
* the commit-graph is never read;
* no fsmonitor command, lazy fetch or `git log` signature program runs;
* global and system configuration and attributes files are not read;
* git sees only an allow-listed environment.

**The rule is defined on git tree paths and blob contents.** These known differences between a checkout and the
tree paths are refused:
* warning-class tree names;
* symlinks and gitlinks under the review directory;
* a review directory or ancestor that is not a directory entry, including submodules.

**Not refused:** directory names that differ from the review directory only by case, by Unicode normalisation or by
ignorable characters (e.g. `Level4/…`, `…/Reviews`). A case-insensitive or normalising file system would show their
files at the review path. They are distinct tree paths, so under the rule as written their files are not reviews. The
D-HOST-LIFETIME procedure must read tree paths only, or use a case-sensitive, non-normalising checkout.

**It is defence in depth, not a closure (review 67 N7).** It does not establish:
* that the history is the one that was reviewed (a consistent rewrite has new commit ids);
* that nothing changed between the check and the reads;
* that no other repository-configured behaviour affects the reads;
* reviewer authority.

These rest on D-HOST-LIFETIME items (i) (the ledger binding) and (ii) (a non-coordinator reviewer), which stay carried
and undecided.

**Legitimate repositories refused (fail-closed; to be listed in the D-HOST-LIFETIME procedure):**
* shallow clones;
* partial clones, and repositories with promisor keys;
* repositories with any `fsck.*` key;
* any `git fsck --full --strict` error, including any WARN-class message, in any object, ref or worktree metadata,
  anywhere in the history (e.g. zero-padded tree modes, bad time zones, `nulInCommit`);
* an index whose entries name missing objects;
* a repository owned by another user (git's dubious-ownership check; reported as "attestation not committed at
  HEAD");
* any history in which a symlink, gitlink or submodule was ever committed under the review directory, or in which the
  review directory or one of its ancestors was ever a symlink, gitlink, submodule, file or odd-mode entry;
* any git call exceeding 60 s (review 69 measured the old batch check at 1.8 s on a 30 000-commit history; the new
  walk took 1.8 s on a synthetic 30 000-commit linear history here, git 2.43);
* an attestation path spelled other than its exact tree path (e.g. `./att/HOST.json`).

## 3. Harness

Group RV grows to RV01–RV63, so the registry has 196 mutants.
* CDEX15 is re-anchored to `_git`'s exception clause, which the new batch helper repeats, with the same weakening.
* RV26 is re-described (S3).
* The workflow expects 196 mutants and 197 suites. The suite has 227 tests.
