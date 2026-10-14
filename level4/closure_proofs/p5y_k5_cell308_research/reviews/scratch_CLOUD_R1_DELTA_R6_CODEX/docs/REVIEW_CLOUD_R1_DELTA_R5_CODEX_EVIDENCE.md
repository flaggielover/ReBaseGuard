# Cell308 revision 5: independent evidence, harness and record review

Reviewer: fresh independent final evidence/harness subagent; no authorship of the revision-5 repair or prior reports. Date: 2026-10-15 (Asia/Tokyo).

Immutable reviewed HEAD: `13047bbebe509c1c04cd25ea90651c853cc61b03`. Checkout: `/Users/suzhe/.codex/worktrees/cell308-review61/ReBaseGuard`. Namespace: `level4/closure_proofs/p5y_k5_cell308_research` (NS). Development stream: `NS/streams/CLOUD_R1_LINUX_DEV` (DEV).

## Dispositions

- **Static current harness: PASS.** 111 unique test methods, 78 unique and exact expected mutant IDs (M32/R10/X9/N14/Y3/P5/F5), sequential anchors each occurring exactly once, and every constructed mutant parses.
- **Strict classification and orchestration controls: PASS in synthetic checks.** All eight harness function ASTs and the complete bytes from `def _text` through the file end are unchanged from revision 4 at `aef3bead293759e0e4cc1af26e0c01f060bb9abc`. Strict core SHA256: `e1102a904234ceee8233e8614561878dcf4432c59fd53077299ef21a0e1cd426`. Baseline-first, clean environment, invalid-run rejection, exact registry, unchanged-input and fail-on-partial-run behavior are retained.
- **Record preservation and latest append: PASS.** Eight prior amendment/owner-draft files preserve their Git blobs from aef3bead. Every previously present development result blob is unchanged from d423c7 (3 paths), aef3bead (6 paths), and review-preservation commit 64c0909d (8 paths). The latest revision-5 ledger delta adds one line and removes zero; all eight referenced SHA256 values match current bytes.
- **Current exact-commit native Linux runtime: PASS in the recorded test scope.** Independently verified completed run 38639066841 at immutable 13047bbebe509c1c04cd25ea90651c853cc61b03: clean 111-test baseline, all 78 complete valid property-related assertion kills, zero errors/skips/timeouts/unapplied cases, and unchanged exact input hashes. This does not establish coverage of untested inputs or a global fail-closed code verdict.
- **AMENDMENT_DRAFT_R4_PLUS_ERRATUM_E1: FIT_WITH_CONDITIONS.** Documentary readiness is scoped to the proposed contract and continuing conditions. It accepts no amendment, selects no owner option, grants no authority, and supplies no code-wide fail-closed verdict. A separate code review owns the code verdict.

## Scope, exposure and execution

Read the preserved R4 evidence report, the R4 summary and amendment review, active root README and development README, current development platform source and test/harness as text, R4 amendment and owner brief and R4 erratum E1. Read and hashed the narrowly specified latest repair ledger append. Parsed the authored 42-test subset and static-check result records; used the corresponding stderr only as preserved data. Read lx_inventory bytes only for hashing. Later read the supplied revision-5 Linux artifact validation.json/input-commit.txt/full-output.json and queried GitHub Actions run metadata through read-only `gh run view` for 38639066841. Used Git metadata and explicitly named historical source/test/harness blobs for immutable-input and preservation checks; no historical candidate module was opened or executed.

Two bounded exposure deviations are disclosed: an initial narrow filename inventory over reviews/ledger returned the unrelated brief pathname `NS/ledger/briefs/25_reviewINTERRUPTION_DELTA.txt`; its contents were never opened. An initial default-context Git diff of the permitted latest ledger append displayed three immediately preceding development-review lines (CODEX_REVIEW61_TAKEOVER, CODEX_REVISION4_REPAIR_AND_BASELINE_REPLAY, CODEX_REVIEW62_AND_LINUX_REVISION4). The independent latest-append verification thereafter used `--unified=0`; earlier ledger context supplied no current-result verdict. The references contained in those lines were not followed. A final output-manifest pass also hash-read the bytes of unrelated target-free collaborator outputs `CODE_REVIEW.md` and `NEXT_WORK.md` in the shared `/tmp/cell308-codex-review63` directory; their contents were not displayed, interpreted, or used for any verdict. The corrected manifest lists only this reviewer’s explicit outputs.

No forbidden audit/interruption assessment, interruption review content, coordinator exposure disclosure, MB-r1 postexecution/target record, or actual Cell309 file/branch/record was read. No full namespace scan or scanner CLI ran. No science, candidate, decoy, qualification, drift, certificate or target evaluation executed; new_target_evaluations=0.

This subagent imported only the target-free stdlib mutation harness, without invoking its real suite. Synthetic reports and mocked `run_suite`/`input_hashes` exercised classification and main exit logic; generated mutations were parsed, never imported or executed. No lx_platform or test module was imported and no Mac or Linux unit suite was launched here. Ephemeral mutant source copies created by mocked-main controls were removed by TemporaryDirectory; durable outputs are under `/tmp/cell308-codex-review63`. No repository edits, commits or pushes occurred. Tracked/staged diff checks before the parent began subsequent disjoint work were clean. The parent later reported additive new files/continuation-plan work; no overall final-clean-worktree claim is made. This assessment remains bound to immutable 13047bbebe509c1c04cd25ea90651c853cc61b03, and all four reviewed inputs were reverified against its Git blobs during artifact adjudication. No later wrapper or repair file forms part of this verdict.

## Input bindings

Paths in the first table are relative to DEV.

| Input | Current SHA256 |
|---|---|
| `lx_platform.py` | `e4f30c816a31a2f36fe7fab88fb4af957457d817b88fc2a8b75324cdb7ef705e` |
| `lx_inventory.py` | `8ea74ed3621e805066727a4ca3f20253f9a85c90857aca8d8e41e02607cfa597` |
| `tests/test_lx_platform.py` | `adf041b57145ae2266fc51b499997721833ee3e6c0e3d62c36496117c9521ea5` |
| `tests/run_mutants.py` | `ddf24e5db7031ed6074b14949497d32561bf0304919d43c4703f19585e4417fa` |

| Document | Current SHA256 |
|---|---|
| `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4.md` | `0a9d720f2b715cda0f247d1500a807613a2e6f2a1265578fdada0ab2d85baa9b` |
| `OWNER_DECISION_BRIEF_CLOUD_R1_R4.md` | `7dc0322dd341477f008cbd5f7957eae7e3ee1fbc2d8d28c99ebc485602715c4c` |
| `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4_ERRATUM_E1.md` | `b73ecabf0dbf7fe2dda650b6f8c98808b03137faaa4cc69d8e1a4c35bc237e84` |
| `README_DEV_ONLY.md` | `4362a1d675a4ce19ee93258faca00b2e750813f5d39cabde9a322d704d0a635d` |

Full exact prior draft/result blob identities and all eight latest-ledger SHA bindings are in `record_checks.json`. The current artifact also matches these four input hashes recomputed directly from Git blobs at immutable 13047bbebe509c1c04cd25ea90651c853cc61b03, independently of later working-tree additions. R4/owner-r4 bytes are unchanged, so their accepted quotations and governance provisions are preserved without reopening restricted underlying source material. This review does not independently re-adjudicate primary accepted quotations.

## Mutation and test delta

All 103 prior test methods are AST-identical. The eight additions are intermediate REALTIME excursion, intermediate BOOTTIME excursion, intermediate counter reset, nondecreasing counter increase, duplicate PID identities in start snapshot, duplicate PID identities in end snapshot, duplicate NSpid fields, and malformed mount metadata. Only the platform functions `assess`, `proc_view_complete` and `busy_processes` change their ASTs.

All 73 old mutant IDs and their order are retained. Every old mutant tuple is unchanged except X04 and Y03:

- **X04 reanchor: faithful.** Only indentation changes to follow the new adjacent-pair loop; whitespace-normalized removed source is identical, and the same monotonic-ahead-of-boottime channel is removed from every checked pair.
- **Y03 combined weakening: faithful, explicitly described.** Its original sample-order edit is unchanged. A second edit removes the newly independent `dm <= 0 or db <= 0` rejection route, so an out-of-order sample can reach CLEAN. Both edits concern the same ordering property; sample-gap coverage and other K/P, power, boot, counter and journal checks remain. This is an intentional combined bypass of two rejection routes, not a syntax shortcut or a general clock-channel deletion.

F01 returns clock comparisons to endpoints, F02 returns counter comparisons/schema validation to endpoints, F03 removes numeric mount-header checks, F04 trusts the first of duplicate NSpid fields, and F05 removes per-snapshot unique-PID enforcement. Their source anchors and tests directly correspond to the bounded repair contracts. Complete runtime property attribution is verified below and preserved for all 78 cases in `current_adjudication_checks.json`.

## Synthetic controls

Nineteen independently constructed cases cover complete assertion failure (KILLED), complete passing suite (SURVIVED), failed baseline, unittest error, absent summary, short count, skips, expected failures, unexpected success, timeout, signal exit, subprocess launch error, ResourceWarning, unraisable marker, missing named failure, multiple summaries, multiple run-count lines, zero exit with failures, and nonzero exit with OK. Every invalid case is ERROR.

Mocked main with 78 complete assertion outcomes exits 0 and requests exactly 79 suite calls, baseline first. One short run, one survivor, failed baseline, or before/after hash mismatch exits 1. Failed baseline requests only one suite call and marks all mutant cases ERROR. Removing F05 from the registry raises ValueError. Deliberately inherited `/SYNTHETIC_POISONED_DIR` LX_PLATFORM_DIR is absent from baseline environment and PYTHONDONTWRITEBYTECODE=1 is set. These are classifier/control checks, not native platform evidence.

## Authored subset evidence

The preserved authored subset record names 42 current test methods, has source/test hashes equal to the current commit, and its stderr ends with Ran 42 / OK. It records Mac arm64 CPython 3.14.5, an injected temporary LX_PLATFORM_DIR, and `native_linux_full_suite=UNVERIFIED`. Its static record identifies the pre-commit HEAD 64c0909d with current repair-byte hashes. The ledger accurately labels 111 tests and 78 mutants as static counts and native Linux / independent review as pending. The authored subset was not replayed by this reviewer and is not treated as independent or full native evidence.

## Documentary scope and remaining conditions

Active README now names revision 5, correctly says 111 tests / 78 mutants, links r4 §3 **and** erratum E1, and keeps revision-3 records explicitly historical. Its revision-4 103/73 statement names the historical input scope; it explicitly says revision-5 native validation and fresh independent review are pending. R4 and its owner brief preserve their historical pending wording; E1 explains that exact revision-5 validation is pending and makes no passed-run claim. No false current 111-test PASS claim was found.

Erratum E1 requires recognised integer clocks on every adjacent interval plus endpoint interval with unchanged 2 s tolerance, counter malformed/decrease/increase precedence, accumulation of independent channel reasons, numeric mount metadata, exactly one positive NSpid token, and one PID identity per individual CPU snapshot. Those described seams match the changed source and focused test inputs statically. This does not assert the complete implementation is fail closed for every untested input.

All 20 D-* rows remain unchanged from the preserved R4 blob, their IDs/order match R3, and the source's default DECIDED remains empty. R4's sole prior R3-to-R4 D-HOST-LIFETIME wording correction to OPEN_DECISION is preserved; revision 5 makes no further decision change. SLEEP_GAP_TOL_NS, MAX_SAMPLE_GAP_S, MIN_FREE_DISK and OPEN_DECISIONS assignment ASTs are unchanged from R4.

FIT_WITH_CONDITIONS carries: verified current-host attestation provenance for raw memory; independently reviewed restrictions on launcher/checker/readings/decision/configuration seams; a complete pinned static science import list and wrapper reaching the pin point in every computing mode; non-holder reference records and strip/serializer digests in the formally accepted text before OD-3; applicable owner decisions, route/governance acceptance, fresh S12 and implementation evidence before any official operation. No host choice, repeat or host-shopping permission, operational wrapper proof or formal authority follows from this review.

Current scoped evidence/record findings: BLOCKING 0; MAJOR 0; MINOR 0. Exposure deviations above are recorded rather than hidden. The parent separately reports DEV_CODE_R5 NOT_FAIL_CLOSED because of a newly reviewed R5-C1 delimiter defect; that code finding is not independently adjudicated in this role and is not discharged by the 78-kill registry. The code verdict remains separate from evidence and document readiness.

## Current Linux artifact assessment

[GitHub Actions run 38639066841](https://github.com/flaggielover/ReBaseGuard/actions/runs/38639066841), workflow **Cell-308 development review**, was independently queried through read-only `gh run view`: status completed, conclusion success, headSha exactly `13047bbebe509c1c04cd25ea90651c853cc61b03`. Artifact directory: `/tmp/cell308-codex-review61/linux-r5-38639066841`. input-commit.txt independently names that same immutable commit. validation.json and full-output.json are byte-identical and parse to the same complete record.

| Artifact file | SHA256 |
|---|---|
| `validation.json` | `d46587398f7807b8e11c2dce7c68b889fa3d2a8a29daac5947092d80a29b349a` |
| `input-commit.txt` | `e607a27a71d9da071f0df44dcf66fb53df69b673c340bc0a3144b9cf936836b9` |
| `full-output.json` | `d46587398f7807b8e11c2dce7c68b889fa3d2a8a29daac5947092d80a29b349a` |

The record is SYNTHETIC_VALIDATION/dev_only on Linux x86_64, kernel 6.17.0-1022-azure, CPython 3.12.3 (`/usr/bin/python3`, real `/usr/bin/python3.12`, GCC 13.3.0), timestamp 2026-10-14T21:22:43Z, new_target_evaluations=0. It records the complete command and cwd. The baseline uses `/usr/bin/python3 -B -W error::ResourceWarning -m unittest discover -s <snapshot DEV>/tests -v`, LX_PLATFORM_DIR=null and PYTHONDONTWRITEBYTECODE=1. Its raw output names exactly the 111 current unique test methods and reports Ran 111 / OK, normal returncode=0, no errors/skips/failures/invalid reasons or timeout/launch error.

Every mutant uses the same command/cwd with its temporary LX_PLATFORM_DIR. Its raw verbose output likewise names exactly all 111 current methods, reports Ran 111, normal returncode=1, one or more named assertion failures, and zero errors/skips/invalid reasons, timeouts or launch failures. Independent reconstruction of every suite record from stdout/stderr/exit metadata exactly matches the reported fields. Reclassification gives **78 KILLED, 0 SURVIVED, 0 ERROR, 0 NOT_APPLIED**. IDs, properties, subgroup counts and record totals match the expected full registry. All 78 mutated-source hashes and sequential anchor-count arrays match independent local construction at the immutable input. Before/after input hashes equal each other and the four Git-blob SHA256 values in the input table; inputs_unchanged is verified.

Property adjudication examined each full assertion section, the current named test fixture and the intended source weakening. All 161 recorded traceback test frames match the exact immutable test line and source statement. Every case has a direct intended-property assertion witness, not merely a failed process or unrelated exception. The complete 78-case witness/observation/frame record is in `current_adjudication_checks.json`.

M06 has the isolated empty temporary power-supply fixture in `test_power_classes`: AC rather than ABSENT. M16's child may exit before SIGKILL because target-in-place writing hits the exclusive-open path; that secondary child-exit assertion is not the sole property proof. Its direct stale-temp and symlink assertions report StaleTmp/OSError not raised and independently demonstrate the intended unsafe write weakening. M29 now fails directly at `assertIn("launched_by_systemd", g)` (immutable test line 1150): the execute/resume gate is omitted. It is a strict assertion kill, with no required-key error adjudicated as a current automatic kill.

| Changed/new case | Direct relevant witness and observation |
|---|---|
| X04 | `test_monotonic_ahead_of_boottime_and_absent_samples`: CLEAN rather than AMBIGUOUS after removal of the negative K′ divergence channel |
| Y03 | `test_samples_out_of_order_never_clean`: CLEAN rather than AMBIGUOUS for a sample after end, with both ordering rejection routes deliberately weakened |
| F01 | intermediate BOOTTIME excursion returns CLEAN rather than CONTAMINATED; intermediate REALTIME excursion returns CLEAN rather than AMBIGUOUS in their respective new fixtures |
| F02 | `test_intermediate_suspend_counter_reset_is_ambiguous`: CLEAN rather than AMBIGUOUS for 0→1→0; malformed middle counters likewise wrongly return CLEAN |
| F03 | `test_proc_view_rejects_malformed_mount_metadata`: True for each malformed mount/parent/device fixture rather than a refused/unavailable view |
| F04 | `test_proc_view_rejects_duplicate_nspid_fields`: True for single-then-nested and identical duplicated status fields |
| F05 | end duplicate-PID fixture returns [] rather than None; start duplicate-PID fixture likewise returns a reading rather than None |

**Final evidence verdict: all 78 are VALID ASSERTION KILLS in this exact 111-test recorded scope.** This resolves the pending native-runtime evidence condition for revision 5 and retains the strict no-error rule. It does not resolve the separately reported code delimiter finding, establish global fail-closed behavior, accept the proposed amendment, or discharge operational/governance prerequisites. The immutable R4/E1 pending wording remains a preserved pre-validation statement; this separately bound review supplies the later evidence without rewriting history.

Supporting outputs: `static_checks.json`, `harness_controls.json`, `record_checks.json`, `delta_checks.json`, `expected_property_witnesses.json`, and `current_adjudication_checks.json` beside this report.
