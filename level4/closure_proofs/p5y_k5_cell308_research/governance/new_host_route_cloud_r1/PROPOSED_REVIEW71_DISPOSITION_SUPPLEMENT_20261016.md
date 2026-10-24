# Proposed supplement: disposition of review 71 on the combined development source

**PROPOSED_NOT_ACCEPTED_NOT_IN_FORCE · DEVELOPMENT ONLY.** This supplement answers review 71
(`reviews/REVIEW_REVIEW70_REPAIR_DELTA.md`, recorded verbatim). Review 71 is a fresh bounded review of
`9f223c91..cc02b9b7`. This supplement accepts nothing and decides nothing.
* All 21 D-* decisions remain undecided, and `DECIDED` is empty.
* `JOURNAL_READER_REVIEWED = False` and `PIN_POINT_MODULES = None`.
* A1, A2 and A5 remain unmet.

Review 71's verdict on the repairs is REPAIRED. Its findings concern the harness and the records. **`lx_platform.py` is
not changed by this repair.** Supplements r69 and r70 are not edited, and their §2 text stands.

## 1. Findings

| finding (review 71) | disposition on the new source |
|---|---|
| U1 MINOR: a root commit's own tree is not pinned (RD1 survives, fail-open) | New test `test_review71_root_commits_duplicates_and_sibling_names`, part (a). An ancestor symlink that exists only in the root commit refuses. So does one that exists only in an unrelated root merged with `-s ours`. RD1 (`--min-parents=1`) is registered as **RV71**. |
| U2 NOTE: same-mode duplicates and the walk's use of a malformed answer are unpinned | The direct `_tree_entry` assertion adds a same-mode duplicate (RD2 = **RV73**). Part (b) of the new test calls `_review_dir_is_a_directory` directly, without the fsck precondition, on a root tree with two `level4` entries; it must answer False (RD3 = **RV74**). Both mutants are equivalent in `attestation_valid`, because strict fsck refuses duplicates first; they pin the walk's own behaviour. |
| U3 NOTE: no positive control for prefix-sharing siblings | Part (c) of the new test is a positive control: a `level4x` symlink, a `reviews-archive` file and a `reviews old` file beside the real directories are accepted. RD5 (prefix match) is registered as **RV72**. |
| U4 NOTE: the sharded record is weaker evidence | Stated. The sharded local record is **not** the single-process evidence. The native workflow run of the unchanged harness is that evidence. Native run 38843066536 on cc02b9b7 covers the 74badebc inputs. The 74badebc sharded record (ledger 531) has no interpreter or kernel field, so its `CPython 3.12.3` is coordinator-asserted. Its run was not resumed: it was started once, after the second restart, and finished without interruption. The rows hold `failed_methods` only. The runner now records the interpreter, executable, platform and git version. It records whether a run resumed, and it keeps each mutant's complete suite record. |
| U5 NOTE: native run on cc02b9b7 pending | Recorded by its own ledger line. |
| U6 NOTE: BRIEF_INDEX "tail-figure scan: 0 hits" not recorded where the index says | A ledger line records the scan, recomputed with `ledger/TAIL_FIGURE_PATTERNS.json`, for briefs 64–71 with their sha256: 0 hits each. For briefs 18–63 the column stays coordinator-asserted. `BRIEF_CHECK.json` is historical and is not edited. |

## 2. Harness

Group RV grows to RV01–RV74, so the registry has 207 mutants.
* The workflow expects 207 mutants and 208 suites. The suite has 230 tests.
