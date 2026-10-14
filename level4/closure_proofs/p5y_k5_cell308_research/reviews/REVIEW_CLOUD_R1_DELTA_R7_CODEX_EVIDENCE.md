# Cell308 revision 7: independent evidence and harness review

Fresh independent evidence/harness reviewer, with no authorship of the repair, wrapper or previous review. Date: 2026-10-15, Asia/Tokyo. Immutable input: `7eb3ba4d03f3b7898109073c83eb9b08f4589354`; comparison base: `af55168c`. Checkout: `/Users/suzhe/.codex/worktrees/cell308-review61/ReBaseGuard`. NS is `level4/closure_proofs/p5y_k5_cell308_research`; DEV is `NS/streams/CLOUD_R1_LINUX_DEV`.

## Evidence disposition

**Exact-input native Linux evidence: PASS.** Independently queried completed [Actions run 38644122257](https://github.com/flaggielover/ReBaseGuard/actions/runs/38644122257): head exactly `7eb3ba4d`, workflow **Cell-308 development review**, server conclusion success. The immutable snapshot, mutation and evidence-preservation steps succeeded. The baseline passes all 136 current methods; all 80 low-level mutant runs execute the same 136 unique methods in the same order and qualify as valid assertion kills. There are zero unittest errors, skips, survivors, timeouts, launch failures or unapplied cases. Every kill has a direct assertion witness logically tied to its intended weakening, and all six before/after input hashes match independently hashed immutable Git blobs.

**Registry, classifier and provenance: PASS within scope.** There are 112 platform plus 24 wrapper methods and exactly 80 unique expected IDs, M32/R10/X9/N14/Y3/P5/F7. Every sequential edit anchor occurs once and every independently constructed mutant parses. All eight harness function ASTs, including classifier/orchestration/input hashing, are identical to the base. The original 79 mutant tuples and the 112 platform plus 22 earlier wrapper method ASTs are retained. Forty-two isolated synthetic harness controls pass. The authored Mac record is internally consistent but establishes only its selected 32-method baseline and M25/F06/F07 assertion runs.

**Historical preservation: PASS.** Thirty-six explicitly identified historical draft/erratum/result/review inputs are byte-identical to the comparison base. In particular, R6 remains its failed immutable 134-test PASS baseline / 78 valid kills / M25 ERROR record, with one digest assertion and one unittest TypeError. R7 does not retroactively turn that R6 ERROR into a kill. The latest ledger adds one line, removes none, and all 16 bindings match current immutable Git bytes.

This evidence review supplies no global unmodified-code verdict, exhaustive wrapper mutation-coverage claim, amendment acceptance, adoption, owner decision, grant, operational acceptance or target authority.

## Immutable inputs

Paths below are relative to DEV.

| Input | SHA256 |
|---|---|
| `lx_platform.py` | `92c7dbcd9f71e30736a799e54842c433daac2258b7a15d719587e47cfd66705e` |
| `lx_inventory.py` | `8ea74ed3621e805066727a4ca3f20253f9a85c90857aca8d8e41e02607cfa597` |
| `lx_verified.py` | `ba59aab0ce408c97cfc46f037d525ca16b90a5261129fd75fc2d05a0a487ad65` |
| `tests/test_lx_platform.py` | `03b5b136f0321b64338357f8f1eb6385a13efede32f9eb8fbaefe8fb6113dc8e` |
| `tests/test_lx_verified.py` | `c8f388659f41d7bec237bfeaeaaf36dd4bafbaae20ef601be4bce1744d9463e4` |
| `tests/run_mutants.py` | `6fe09b9f1bd6f437bf561ed69290a154867618265338cfb9ec3b3fda7e89af74` |


README `README_DEV_ONLY.md` has SHA256 `3ce8d14f746c40e28543238114cea87421f9fa48d225b9d30d792316ced97524`. The root workflow `.github/workflows/cell308-dev-review.yml` has SHA256 `86ccc75ef9288d835a854c1508a7cc5be6141a7a6489878d50f66418827a1aa4`. The README accurately preserves the R6 failure, labels R7 validation/review as pending at authorship, describes observation-only composition and unresolved A1/A2/A5 conditions, and explicitly scopes the 80 mutations to low-level code. This later report resolves the runtime pending state for the pinned input without rewriting that earlier statement. The workflow directly invokes the immutable snapshot's harness and uploads full output even on failure; the separately preserved forensic script is not the active runner.

## Harness and authored checks

The harness first runs a clean unmodified baseline, with inherited `LX_PLATFORM_DIR` removed. Suites use `-B -W error::ResourceWarning -m unittest discover -s <tests> -v` and bytecode suppression. Its unchanged classifier requires one positive count, one compatible summary, matching named failures/errors, normal exit, complete baseline test count, no unittest errors or nonassertion outcomes, and no timeout/launch/resource-warning/unraisable condition. Unchanged input hashes, a complete expected registry and valid kills for every row are required for exit 0.

A narrow delegated reviewer read only the two pinned harness blobs and produced 29 classifier controls, four subprocess-mocked `run_suite` controls, one six-input fixture hashing control and eight fully mocked `main` controls: all 42 pass. These cover passing/failing baselines; valid assertion kills and survivors; short/extra/zero counts; missing/repeated/malformed summaries; unmatched outcome names; errors/skips/expected failures/unexpected successes; timeout/launch/signal/exit mismatches; ResourceWarning/unraisable text; complete output preservation; registry mismatch; source snapshot mismatch; and changed after-hashes. Source reads, suites, mutations, environment, metadata and time in mocked main were fixtures. They prove these examples rather than resistance to arbitrary forged logs. Their report, controls and independently verified 14-file manifest are under `evidence/harness-controls`.

The R7 authored runner selects seven proc-view methods, all 24 wrapper methods and the original M25 digest-mismatch method. Its 32 selected names are exact in each raw report. CPython 3.14.5/macOS arm64 records baseline Ran 32 / OK / exit 0, M25 one assertion, F06 three assertions and F07 four assertions; each mutant exits 1 with zero errors/skips/invalid reasons. Module hashes match independent transformation, all six record input hashes match Git, separate stdout/stderr files equal the embedded reports, and source traceback frames match current immutable fixtures. `native_linux_full_suite=UNVERIFIED` is accurately preserved. No authored run was replayed locally.

## Native Linux artifact adjudication

Artifact supplied at `/tmp/cell308-codex-review61/linux-r7-38644122257`:

| File | SHA256 |
|---|---|
| `validation.json` | `b73a9472ceff3498d8a2ec761a6c36b6f649e7e5815c1f2e6a8e41a13061564e` |
| `full-output.json` | `b73a9472ceff3498d8a2ec761a6c36b6f649e7e5815c1f2e6a8e41a13061564e` |
| `input-commit.txt` | `44b3c4abb2d49c31392d538fadb612d907acf099b6e9c50af0da7b9d81c82ad8` |

The two JSON files are byte-identical, 2,161,619 bytes each. The commit file names the complete pinned hash. Record class is development-only SYNTHETIC_VALIDATION on Linux x86_64, kernel `6.17.0-1022-azure`, CPython 3.12.3 (`/usr/bin/python3`, real `/usr/bin/python3.12`, GCC 13.3.0), timestamp `2026-10-14T22:02:16Z`, `new_target_evaluations=0`.

All 81 suite records are reconstructed from complete stdout/stderr and explicit controls using the pinned unchanged parser, with every field matching. Baseline is Ran 136 / OK / exit 0, zero failures/errors/skips and no invalid reasons. Every mutant is Ran 136 / FAILED with only assertion outcomes / exit 1, exactly the current baseline names and order. Their commands/cwd bind the immutable snapshot; mutant module directories are temporary and the baseline module override is absent. All 80 IDs, properties, order, anchor arrays and transformed platform hashes match independent string construction and AST parsing. Before/after maps equal the exact six Git hashes above.

| Group | Valid assertion kills | ERROR |
|---|---:|---:|
| M | 32 | 0 |
| R | 10 | 0 |
| X | 9 | 0 |
| N | 14 | 0 |
| Y | 3 | 0 |
| P | 5 | 0 |
| F | 7 | 0 |
| Total | 80 | 0 |

All 80 intended properties were assessed against the current fixture, intended edit and direct assertion observation, not return code alone. `current_adjudication_checks.json` preserves each full chosen failure section, fixture source, rationale, strict status, anchors/hash and verified source frames. All 208 test traceback frames and 18 product traceback frames match the immutable test/wrapper source or independently transformed platform source, including the containing function.

M25 now has only the original digest-mismatch assertion at platform-test line 1076: the weakened verifier returns a committed record when the reference names a different accepted digest. The uncommitted wrapper fixture reports OK in the same complete suite. The new absent-blob refusal occurs before the unchanged digest guard, so it prevents the old TypeError without removing or weakening the intended digest counterexample.

F07 restores the former exception boundary. Its four named subtest assertions cover NUL and surrogate paths in both references and committed acceptance records. The escaping ValueError/UnicodeEncodeError is caught by the fixture and converted into an explicit property assertion at wrapper-test lines 146/158. This tests refusal without escaping argument exceptions; it does not relax classifier rules or credit a unittest ERROR.

M16 retains a secondary child FileExistsError→StaleTmp traceback and child exit 1 when target-in-place writing conflicts with an existing target. That secondary exception is disclosed and is not the property proof. Separate direct assertions are `StaleTmp not raised` for a stale `.tmp` at line 914 and `OSError not raised` for a stale `.tmp` symlink at line 921. Its complete suite has three assertions and zero unittest errors. The result therefore says zero **unittest** errors, not absence of all child-process exceptions. M06 uses the isolated empty power tree; M29 directly tests required launch-gate presence; F06 directly rejects both unsafe payload losses at line 756 and separately fails its valid adjoining-PID control at line 759.

## Preservation, exposure and output scope

Read only explicit root/user AGENTS paths: the user file `/Users/suzhe/.codex/AGENTS.md` is empty and the worktree root file is absent. Read immutable development source/test/harness bytes, relevant fixture/helper source, README, workflow and bounded development delta. Read the explicitly authorized R6 evidence report and only its needed `record_checks.json`, `expected_property_witnesses.json` and `current_adjudication_checks.json`. Older drafts, errata and result/review records were accessed as bytes solely for explicit hash/identity preservation. The latest ledger was read only through `git diff --unified=0 af55168c..7eb3ba4d` on its exact path, showing the single `CODEX_REVISION7_MALFORMED_PATH_AND_ABSENT_BLOB_REFUSAL` append; no neighboring old ledger content was opened. Sixteen latest bindings match immutable bytes, including the continuation plan accessed only for hashing.

A bounded changed-name diff of DEV returned current revision filenames. There was no broad namespace inventory. Approved historical evidence includes references to forbidden exposure/interruption documents; these references were not followed. No forbidden audit/interruption assessment/review/exposure-disclosure content, MB-r1 postexecution/target record or actual Cell309 file/branch/record was opened. No newly discovered forbidden-content exposure occurred. The startup skill was read and explicitly exempts delegated subagents.

Imported only a copied stdlib-only mutation harness for pure record reconstruction; no platform, inventory, wrapper or test module was imported or executed. Constructed and parsed mutant strings without execution. The delegated controls fully mocked suite and mutation application, patched environment with synthetic controls and restored it, mocked metadata/host functions and confined every transient directory to its assigned scratch. No native Mac full suite or real local mutation suite was launched. Read-only `gh run view` queried only the named R7 run; no credentials, secrets, settings or host observations were inspected. No quarantine CLI, science/candidate/decoy/qualification/drift/certificate/target execution or import occurred. Recorded native CI fixture processes and two candidate constants read by its tests are CI activity, not local execution by this reviewer.

One collateral scratch-byte read is disclosed: the initial output-manifest generator traversed the shared `/tmp/cell308-codex-review65` root and hashed 51 sibling code-review outputs as bytes. Their text was not displayed or semantically evaluated, and the independent evidence conclusions had already been established. The initial root-level manifest was removed. The final manifest, saved inside `evidence`, is restricted to this reviewer's evidence directory and report. `collateral_manifest_hash_exposure.json` records the exact accidental hash inventory; it supplies no review evidence. No forbidden content was exposed.

Every durable write by this reviewer or its delegated helper stays under `/tmp/cell308-codex-review65`; no repository edit, commit or push occurred. Input bindings remain pinned to the immutable Git objects even if later records are added. Static and runtime results establish this development evidence condition, while host survival, power-loss durability, hidden cgroup ancestry, real owner/reviewer authority, all20 decisions, A1/A2 operational acceptance and A5 completion remain outside the evidence.

Supporting outputs include `static_checks.json`, `authored_subset_checks.json`, `record_checks.json`, `expected_property_witnesses.json`, `current_adjudication_checks.json`, `property_observations.txt`, `ci_metadata.json`, `immutable_manifest.json`, `latest_ledger_zero_context.diff`, copied immutable inputs/authorized records, the single complete native validation copy and reproduction scripts. `evidence/output_manifest.json` enumerates the explicit scratch outputs and binds this report's final SHA256.
