# Proposed supplement: disposition of review 66 on the combined development source

**PROPOSED_NOT_ACCEPTED_NOT_IN_FORCE · DEVELOPMENT ONLY.** This supplement answers review 66
(`reviews/REVIEW_REVIEW65_REPAIR_DELTA.md`, recorded verbatim). Review 66 is a fresh bounded review of `2275b3a0..774f2183`.
This supplement accepts nothing and decides nothing.
* All 21 D-* decisions remain undecided, and `DECIDED` is empty.
* `JOURNAL_READER_REVIEWED = False` and `PIN_POINT_MODULES = None`.
* A1, A2 and A5 remain unmet.

Supplement r65 is not edited. Its §2 is **replaced** by §2 below. The new source is bound by the ledger line of its
commit and by its own native run.

## 1. Findings

| finding (review 66) | disposition on the new source |
|---|---|
| M1 MAJOR: forged changed-path Bloom filters pass fsck and `commit-graph verify` | The isolation adds `-c core.commitGraph=false`, so the commit-graph (parents and Bloom filters) is never read. Test `test_review66_forged_bloom_filter_is_never_read`: the rejection commit's filter is zeroed and the rejection still refuses (HISTORICAL); an honest `--changed-paths` graph is accepted (positive control). Mutant RV43. The earlier forged-CDAT case is now refused by the historical veto, because the graph is unread, rather than by fsck. Its test asserts refusal only. |
| M2 MAJOR: fsck runs a repository-configured `core.fsmonitor` command | The isolation adds `-c core.fsmonitor=false`. Test `test_review66_fsmonitor_command_never_runs`: the repository's own config overrides the fixture's `false`, the attestation is accepted, and no marker is written. Mutant RV44. Other index-time commands were not found in fsck's path. Pagers need a terminal, and the output is captured. **Stated residual:** any process with write access to the repository can change objects between fsck and the reads (time of check vs time of use). |
| M3 MINOR: keys hidden in `include.path` or `config.worktree` | Keys are listed with `git config --includes --name-only --list`, which covers every scope git reads (local, worktree, includes; global and system are nulled by the isolation). Test `test_review66_configuration_in_includes_and_worktree_scope_refuses`; mutant RV48. |
| M4 MINOR: unpinned elements (RY1, RY2, RY3, RY5) | RY1: RV39 is narrowed to the key refusal, and the lazy-fetch block is the separate mutant RV45, with test `test_review66_lazy_fetch_blocked_even_past_the_precondition` (precondition bypassed, no marker). RY3: `test_review66_symlink_attestation_is_refused`; RV46. RY5: `test_review66_unreadable_configuration_listing_refuses`; RV47. RY2: `--strict` is **removed**. It only promotes warnings, such as zero-padded tree modes in old histories, and no hiding construction depends on it. |
| M5 NOTE: newly refused legitimate repositories | §2 below lists them. |
| M6 MINOR: ledger 495 binds an uncommitted file | It stays **uncommitted**, and a ledger line states it as bound-but-omitted. `*.log` is gitignored, and the file is not a job log but a 522-byte failed-download error message containing a signed (since expired) blob-storage URL, which is not committed. The original in the coordinator's scratchpad matches the binding (`fed307d6…`). |
| M7 NOTE: wording | The RV origin label is now "Claude reviews 63–66". `GIT_NO_LAZY_FETCH` is honoured by the local Ubuntu git 2.43.0 (checked) and by git 2.44 and later. The partial-clone test's docstring is narrowed. The ledger now carries the artifact id and digest of run 38725820509: 11969136626, `sha256:3be305c4…`. |

## 2. What the completeness precondition establishes (replaces supplement r65 §2)

`_history_complete` returns True only when all three of these hold, under the isolation:
1. `rev-parse --is-shallow-repository` prints exactly `false`.
2. `git config --includes --name-only --list` lists no `fsck.*` key and no partial-clone or promisor key.
3. `git fsck --full --no-dangling` exits 0.

Any failure, timeout (60 s per git call) or other answer refuses as unavailable evidence. Under the isolation:
* replace refs and grafts are ignored;
* the commit-graph is never read;
* no fsmonitor command runs;
* no missing object is lazily fetched;
* global and system configuration and attributes are not read;
* git sees only an allow-listed environment.

**This establishes** that, at the moment of the check, git's own verification finds the reading repository's object
store complete and consistent, alternates included. It also establishes that the history the scans walk comes from the
commit objects themselves.

**It does not establish:**
* that the history is the one that was reviewed, because a history rewritten consistently has new commit ids;
* that nothing changed between the check and the reads;
* anything about repository-local configuration other than the refused keys and the forced overrides;
* reviewer authority.

The ledger binding (D-HOST-LIFETIME item (i)) and a non-coordinator reviewer (item (ii)) stay carried.

**Legitimate repositories refused (fail-closed; to be listed in the D-HOST-LIFETIME procedure):**
* shallow clones;
* partial clones, and repositories with promisor keys;
* repositories with any `fsck.*` key;
* any `git fsck --full` error in any object, including old history;
* an index whose entries name missing objects, because fsck checks the index;
* any git call exceeding 60 s, for example on large repositories;
* an attestation path spelled other than its exact tree path (e.g. `./att/HOST.json`).

The repository checked out in this session is shallow, so it refuses every attestation.

## 3. Harness

Group RV grows to RV01–RV48, so the registry has 181 mutants.
* RV23, RV31 and RV33 are re-anchored with the same weakening.
* RV39 is narrowed.
* The workflow expects 181 mutants and 182 suites.
