# Proposed supplement: disposition of review 65 on the combined development source

**PROPOSED_NOT_ACCEPTED_NOT_IN_FORCE · DEVELOPMENT ONLY.** This supplement answers review 65
(`reviews/REVIEW_REVIEW64_REPAIR_DELTA.md`, recorded verbatim). Review 65 is a fresh bounded review of `5e8e3d9c..2275b3a0`,
covering the review-64 repairs and the restored history-completeness guard. This supplement accepts nothing and
decides nothing.
* All 21 D-* decisions remain undecided, and `DECIDED` is empty.
* `JOURNAL_READER_REVIEWED = False` and `PIN_POINT_MODULES = None`.
* A1, A2 and A5 remain unmet.

The review-64 supplement and its erratum E1 are not edited. Where they differ from this text, this text describes the
new source. The new source is bound by the ledger line of its commit and by its own native run. Until that run passes,
nothing here is validated.

## 1. Findings

| finding (review 65) | disposition on the new source |
|---|---|
| L1 MAJOR: a forged commit-graph or a rewritten loose object hides a deleted rejection without a shallow marker | `_history_complete` now also requires a clean `git fsck --full --strict --no-dangling`, run under the same isolation. That fsck checks every object, alternates included, and the commit-graph. Measured on git 2.43: a forged graph gives rc 16, a rewritten blob rc 3, an honest repository rc 0, and replace and graft cuts rc 0 (those are handled by the isolation; see L2). Test `test_review65_forged_graph_and_rewritten_object_refuse`: the reviewer's forged-graph construction and a rewritten blob, each refused; an honest commit-graph is accepted (positive control). Mutant RV31. |
| L2 MAJOR: isolation and K9 repairs under-pinned (RX1–RX6) | Test `test_review65_replace_refs_and_grafts_are_ignored` covers a replace-graft cut, an `info/grafts` cut, and a replace graft that places a pre-blob acceptance after the blob; mutants RV33, RV34, RV35. An upper-case glued sha (RV36) and an `EIO` `OSError` (RV37) are added to the existing tests. Test `test_review65_short_exact_listing_refuses`; RV38. |
| L3 MINOR: inherited `GIT_*` variables | `_git_env` builds the environment from an allow-list (`PATH`, `HOME`, `LANG`, `LC_ALL`, `LC_CTYPE`, `TMPDIR`, `TZ`) plus the forced keys, so no inherited `GIT_*` reaches git. Test `test_review65_caller_git_environment_is_ignored` (`GIT_DIR`, `GIT_OBJECT_DIRECTORY`); RV40. |
| L4 MINOR: Q01 over-weakens (gitlinks) | Q01 drops direct-child **trees** only. Its description says so. |
| L5 MINOR: a failed native run unrecorded | Run 38709761027 on `b23ee7dd` is recorded by a new ledger line (160/161, Q01 ERROR). It was one of two push-event runs created one second apart for the same commit. The coordinator triggered neither separately, and the cause of the duplicate is unknown. |
| L6 NOTE: repository-configured commands run during the check | `_history_complete` refuses when the repository's own configuration names a partial clone or promisor (`extensions.partialclone`, `remote.*.promisor`, `remote.*.partialclonefilter`). The environment sets `GIT_NO_LAZY_FETCH=1`, which git 2.44 and later honour. Test `test_review65_partial_clone_runs_no_configured_command`: a blob:none clone whose configured upload-pack would write a marker is refused, and no marker is written. Mutant RV39 removes both the partial-clone refusal and the lazy-fetch block. |
| L7 NOTE: (a) `_ordered` resolved the blob by `rev-parse HEAD:<path>`; (b) deep JSON raised | (a) The blob id now comes from the exact-path listing, and only regular files count. (b) `RecursionError` is refused as "nested too deeply". Test `test_review65_range_like_attestation_path_and_deep_json`; RV41, RV42. |

## 2. What the completeness precondition establishes (replaces erratum E1.3's "positive evidence" wording)

`_history_complete` returns True only when all three of these hold, in the reading repository under the isolation:
1. `rev-parse --is-shallow-repository` prints exactly `false`.
2. The repository's own configuration names no `fsck.*` key and no partial-clone or promisor key.
3. `git fsck --full --strict --no-dangling` exits 0.

Any failure, timeout (60 s per git call) or other answer refuses as unavailable evidence.

**This establishes** that the reading repository's object store, including alternates, is internally consistent and
complete as git verifies it. It also establishes that git's own parent data (commit-graph, shallow marker) agrees with
it, and that no replace ref or graft is used.

**It does not establish:**
* that the history is the history that was reviewed, because a history rewritten consistently has new commit ids;
* anything about a repository whose local configuration git honours in other ways (the review-64 K1 residual);
* reviewer authority.

The ledger binding (D-HOST-LIFETIME item (i)) and a non-coordinator reviewer (item (ii)) stay carried. Large real
repositories may exceed the 60 s fsck limit, which refuses. The repository checked out in this session is a shallow
clone, so it would refuse every attestation. An actual-host procedure must use a full clone, and the host review must
fix the time limit.

## 3. Harness

Group RV grows to RV01–RV42, so the registry has 175 mutants.
* RV30 is re-anchored to the shallow line of the new `_history_complete`, with the same weakening: an unreadable answer
  counts as complete.
* Q01 is narrowed (L4).
* The workflow expects 175 mutants and 176 suites.
