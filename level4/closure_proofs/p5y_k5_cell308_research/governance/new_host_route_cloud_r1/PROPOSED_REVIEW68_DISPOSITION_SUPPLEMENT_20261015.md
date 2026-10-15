# Proposed supplement: disposition of review 68 on the combined development source

**PROPOSED_NOT_ACCEPTED_NOT_IN_FORCE · DEVELOPMENT ONLY.** This supplement answers review 68
(`reviews/REVIEW_REVIEW67_REPAIR_DELTA.md`, recorded verbatim). Review 68 is a fresh bounded review of `2f39e9f4..05caa00e`.
This supplement accepts nothing and decides nothing.
* All 21 D-* decisions remain undecided, and `DECIDED` is empty.
* `JOURNAL_READER_REVIEWED = False` and `PIN_POINT_MODULES = None`.
* A1, A2 and A5 remain unmet.

Supplement r67 is not edited. Its §2 is **replaced** by §2 below. Two statements in its N1 row are **withdrawn**:
* that strict fsck "already refuses the warning-class names that make the two views differ";
* "any … warning" refuses.

The new source is bound by the ledger line of its commit and by its own native run.

## 1. Findings

| finding (review 68) | disposition on the new source |
|---|---|
| P1 MINOR: symlinks make a checkout show a rejection at a review path that git's scan never lists; such repositories are ACCEPTED; the r67 rationale is wrong | Option (a), fail closed. `_historical_review_blobs` returns unavailable evidence for any entry under the review directory, in any commit of HEAD's history, that is not a regular file (100644 / 100755): symlinks and gitlinks. HEAD's entries are included, because the commit that introduced them is listed. The new `_review_dir_is_a_directory` reads `<commit>:<path>` for the review directory and each of its ancestors, in every commit of HEAD's history, with one `cat-file --batch-check`. It accepts only "tree" or "missing" answers. Test `test_review68_non_directory_review_paths_refuse` has five subtests: a symlink at HEAD, a symlink in history, a gitlink in history, the review directory as a symlink, and an ancestor (`level4`) as a symlink. Mutants RV59 (history scan) and RV60 (ancestor check). RV26 (review 64 K7) is widened to a combined weakening, because the new scan would otherwise mask it. The K7 test's control is now a fresh repository. **The rule is still defined on git tree paths and blob contents. Checkout-view equivalence is not claimed** (§2). |
| P2 NOTE: INFO-class fsck messages pass `--strict` | Wording only. §2 and the `_history_complete` docstring now say WARN-class messages refuse and INFO-class messages (e.g. `badFilemode`) pass. No INFO-class hiding construction is known. None is pinned. |
| P3 MINOR: the N2 witness covers only the `--find-object` call | The N2 test now signs the acceptance commit as well, which only the `-S` search selects. RA3 is registered as RV55 and is killed by that test. |
| P4 NOTE: `--strict` pinned through one message; `GIT_ATTR_NOSYSTEM` unpinned | Test `test_review68_strict_fsck_and_forced_git_environment`: (a) a zero-padded tree mode (WARN) in history refuses with "history completeness" (RV56 = RA2); (b) `_git_env()` carries every forced key. Part (b) is a direct check of the environment, not an observation of git, because a test cannot write the system attributes file (RV57 = RA4). RA1 is registered as RV58, with a `fsck.fullPathname` subtest in the review-65 configuration test. |
| P5 NOTE: records residue | A ledger line marks ledger 508's statement "the gate ran all three" as coordinator-asserted: no gate output for 2288bec1 is committed. Native run 38783320859 on 05caa00e is recorded by its own ledger line. |

## 2. What the completeness precondition and the history scan do (replaces supplement r67 §2)

`_history_complete` returns True only when all three of these hold, under the isolation:
1. `rev-parse --is-shallow-repository` prints exactly `false`.
2. `git config --includes --name-only --list` lists no `fsck.*` key and no partial-clone or promisor key.
3. `git fsck --full --strict --no-dangling` exits 0. WARN-class messages are errors. INFO-class messages pass.

After it, the history scan refuses as unavailable evidence any history in which an entry under the review directory
is not a regular file, or in which the review directory or one of its ancestors is not a directory, in any commit
of HEAD's history.

Any failure, timeout (60 s per git call) or other answer refuses. Under the isolation:
* replace refs and grafts are ignored;
* the commit-graph is never read;
* no fsmonitor command, lazy fetch or `git log` signature program runs;
* global and system configuration and the global and system attributes files are not read;
* git sees only an allow-listed environment.

**The rule is defined on git tree paths and blob contents.** The check does not establish that a checkout shows the
same files. It refuses the known ways a checkout differs:
* warning-class tree names;
* symlinks and gitlinks under the review directory;
* a non-directory review directory or ancestor.

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
  in any part of the history (e.g. zero-padded tree modes, bad time zones, `nulInCommit`);
* an index whose entries name missing objects, because fsck checks the index;
* a repository owned by another user (git's dubious-ownership check; reported as "attestation not committed at
  HEAD");
* **new:** any history in which a symlink, gitlink or submodule was ever committed under the review directory, or in
  which the review directory or one of its ancestors was ever a symlink, gitlink or file;
* any git call exceeding 60 s, for example on large repositories;
* an attestation path spelled other than its exact tree path (e.g. `./att/HOST.json`).

At HEAD in this session, the real review directory holds 1420 entries, all regular files (mode 100644). This was
checked from the tree only; nothing was called against the real repository. The history is not checked, because
this checkout is shallow, and a shallow clone refuses every attestation anyway.

## 3. Harness

Group RV grows to RV01–RV60, so the registry has 193 mutants.
* RV26 gains a second edit (a combined weakening).
* The workflow expects 193 mutants and 194 suites. The suite has 226 tests.
