# Cell308 revision 6: independent evidence and harness review

Reviewer: fresh independent evidence/harness subagent, with no authorship of the repair, wrapper or prior reports. Date: 2026-10-15 (Asia/Tokyo).

Immutable input: `875eb95575fa9dc137083667bf30cc4a5a228fe6`; comparison base `1c2ab8f7`. Checkout `/Users/suzhe/.codex/worktrees/cell308-review61/ReBaseGuard`. NS is `level4/closure_proofs/p5y_k5_cell308_research`; DEV is `NS/streams/CLOUD_R1_LINUX_DEV`.

## Current dispositions

- **Static registry and inputs: PASS.** 112 platform plus 22 wrapper test methods give 134 unique test names. There are exactly 79 expected unique low-level mutant IDs: M32/R10/X9/N14/Y3/P5/F6. All sequential edit anchors occur exactly once; every constructed mutant parses. Independently constructed mutation SHA256 values match the authored static record.
- **Strict classifier and orchestration: PASS in synthetic controls.** Of the eight harness functions, only `input_hashes` changes its AST: it now binds `lx_verified.py` and `tests/test_lx_verified.py` alongside the four previous inputs. Nineteen synthetic classifier cases and six mocked-main controls pass. No real unit suite or mutation suite was launched by this reviewer.
- **Record preservation and latest ledger append: PASS.** Eight earlier amendment/owner drafts retain their exact recorded Git blobs and SHA256 values; erratum E1 is unchanged. Eighteen explicitly authorized historical result/review files are byte-identical to `1c2ab8f7`. The latest ledger diff adds exactly one line and removes none; all 18 bindings match immutable Git bytes.
- **Authored selected subset: internally consistent, limited.** The record reports 29 selected Mac tests PASS and three direct F06 assertion failures with zero errors/skips. All six input hashes, both module hashes, all 29 selected names and separately preserved output bytes match. It explicitly says `native_linux_full_suite=UNVERIFIED`; it is not a 134-test Linux result and was not replayed here.
- **Exact-input native Linux baseline: PASS; full mutation evidence condition: NOT MET.** Independently verified completed run 38641842326 at immutable `875eb955`: all 134 baseline tests pass, and all 79 mutant suites execute those same 134 methods. Reclassification gives 78 valid property-related assertion kills, one ERROR (M25), zero survivors/skips/timeouts/unapplied cases, and exact unchanged six-file input hashes. The overall CI result is failure. M25 is not counted as a kill because its intended assertion failure is accompanied by a unittest TypeError.

This report supplies no global code verdict, complete wrapper-coverage claim, amendment acceptance, adoption, owner choice, grant or operational authority.

## Scope, exposure and execution

Read explicit ancestor AGENTS paths: the user-level `/Users/suzhe/.codex/AGENTS.md` is empty; all inspected worktree/namespace/component AGENTS paths are absent. Read the immutable DEV README, source/test/harness bytes, workflow and changed platform/wrapper/test/harness diff. Read only the authorized R5 evidence and summary reports plus `record_checks.json` and `current_adjudication_checks.json`; their historical verdicts do not supply the current runtime verdict. Read current authored R6 subset records and output data. Prior drafts and results, E2 and the continuation plan were read as bytes only when needed for explicit preservation or latest-ledger SHA bindings. The ledger was accessed only through `git diff --unified=0` for the single `CODEX_REVISION6_TRUSTED_BOUNDARY_AND_PROC_PAYLOAD_REPAIR` append; no preceding ledger context was opened. Later read only the supplied R6 Linux artifact `validation.json`, `full-output.json`, `input-commit.txt` and server metadata, and independently queried the named Actions run through read-only `gh run view`.

The first Git changed-name diff returned the permitted revision's changed pathnames, including E2 and the continuation-plan pathname. There was no broad namespace inventory. No forbidden audit/interruption assessment, interruption-review content, exposure-disclosure file, MB-r1 postexecution/target record, or actual Cell309 file/branch/record was opened. Approved reports contain references to historical exposure disclosures; those references were not followed. There was no newly discovered forbidden-content exposure.

One scratch-placement deviation is disclosed: the initial mocked-main controls used the harness's OS-default TemporaryDirectory location for transient mutant source copies, outside the assigned scratch directory. TemporaryDirectory removed every copy. The same six controls were then rerun with TemporaryDirectory explicitly bound below `/tmp/cell308-codex-review64/evidence`, again with identical expected results, and those transient directories were removed. The final controls record binds their explicit scratch root. No repository or unrelated persistent file was written, and no forbidden content was accessed.

Imported only the stdlib-only mutation harness in scratch. Constructed and parsed mutant strings without importing or executing them. Mocked the real suite function and input-hash function for main-control checks; TemporaryDirectory removes each transient mock-main mutant file. No lx_platform, lx_verified or test module was imported by this reviewer. No host observation, setting change, credential/secret inspection, quarantine CLI, science/candidate/decoy/qualification/drift/certificate/target evaluation occurred. Mocked main inherited normal process environment; only the two explicit harness control values were inspected or recorded. `new_target_evaluations=0`. All durable writes are this reviewer's own explicit scratch files under `/tmp/cell308-codex-review64`; no repository edit, commit or push occurred. All inputs remain bound to immutable Git objects even if the parent later adds reports.

The platform tests include native Linux lifecycle/host observations and two constants read from the historical candidate by CI. They execute no science or target evaluation. Those recorded CI operations are not local execution by this reviewer. Successful synthetic evidence does not establish host survival, power-loss durability, hidden cgroup ancestry, real reviewer/owner authority, all20 decisions, A1/A2 operational acceptance or A5 completion.

## Immutable input bindings

Paths are relative to DEV.

| Input | SHA256 |
|---|---|
| `lx_platform.py` | `e8e33df59f3edd9f187db149cf77d1cca024403ffda5e21eb1c1d66980ec2074` |
| `lx_inventory.py` | `8ea74ed3621e805066727a4ca3f20253f9a85c90857aca8d8e41e02607cfa597` |
| `lx_verified.py` | `ba59aab0ce408c97cfc46f037d525ca16b90a5261129fd75fc2d05a0a487ad65` |
| `tests/test_lx_platform.py` | `03b5b136f0321b64338357f8f1eb6385a13efede32f9eb8fbaefe8fb6113dc8e` |
| `tests/test_lx_verified.py` | `a700e83cdbcfae380b671ed47291bae31100e30c007e6fa71d0b5f9bdcdadc1d` |
| `tests/run_mutants.py` | `e1374423c3137e6f82ee02c2dde7352fb1af40f9f720e4d0b94a958d276ea3a1` |

The immutable development README SHA256 is `818fa016aaff918e1a8123bb4c3a0c431769a6290271c4efcfb7301d38da0d12`. Its wording accurately distinguishes historical R4 103/73 and R5 111/78 evidence from pending R6 134/79 evidence. It calls the new wrapper observation-only and reports all required operational conditions as unresolved. It explicitly says the 79 mutations target low-level code rather than every wrapper behavior.

## Registry, tests and execution controls

The prior 78 IDs and their order are retained. Old mutant tuples are unchanged except P05 and F03, whose removed guards are faithfully reanchored from `.isdigit()/int` checks to the new positive-ASCII regular expressions. F06 restores the precise prior `ln.split()[1:]` payload-dropping behavior. Only the existing malformed-mount test method changes its AST to add Unicode digit cases. The other 110 prior platform test methods are AST-identical; one delimiter/ASCII method and 22 wrapper methods are new.

The wrapper tests use committed temporary Git fixtures with patched observations; canonical attestation/gate logic remains active. They exercise provenance refusal, strict root claims, restricted public inputs, repeated canonical verifier/current-machine calls, independent launch corroboration, mode refusal, empty decisions, UNKNOWN other-campaign state, withheld effective/headroom quantities, and the same platform-module identity under mutation injection. Their 22 methods provide scoped wrapper regression evidence. The harness mutates only `lx_platform.py`; it supplies no independent adversarial mutation coverage for every wrapper behavior.

The strict harness still requires a passing unmodified baseline before mutant execution. It clears inherited `LX_PLATFORM_DIR` for the baseline, sets bytecode suppression and runs `-B -W error::ResourceWarning -m unittest discover -s <tests> -v`. It preserves stdout/stderr, enforces normal exits, one positive test count, one compatible summary, named failures/errors matching the summary, no errors/skips/expected-failure/unexpected-success outcomes, no ResourceWarning/unraisable markers, no timeout/launch error, and exactly the baseline test count. Inputs are checked before and after. A partial registry, survivor, invalid outcome, failed baseline or changed input prevents exit 0.

Synthetic controls cover KILLED, SURVIVED, failed baseline, short count, errors, missing summary, skips, expected failure, unexpected success, timeout, signal, launch error, ResourceWarning, unraisable marker, missing failure name, duplicate summary/count, and exit/summary disagreement. Mocked main verifies 80 calls for one baseline plus 79 assertions, baseline-only execution for a failed baseline, rejection of one short run or survivor, rejection of changed wrapper bytes, and ValueError for missing F06. These checks prove the classifier/control examples, not native platform behavior or resistance to arbitrary forged logs.

The workflow delta adds `lx_verified.py` to the push path trigger; the tests glob already includes both test files and the harness. It runs the suite/harness from an explicit immutable `github.sha` checkout and uploads complete output even on failure. The completed failed run demonstrates preservation of complete evidence despite failure. Exact GitHub head, artifact commit, source hashes, each full 134-name suite and assertion witnesses are verified below.

## Current authored record and property witness preparation

The preserved Mac record uses CPython 3.14.5 on macOS arm64. Its selected runner loads seven proc-view methods and all 22 wrapper methods. The base source hash matches immutable platform bytes; F06's hash matches independent mutation construction. Both raw reports name exactly those 29 methods. Baseline is Ran 29 / OK / exit 0. F06 is Ran 29 / FAILED(failures=3) / exit 1 with no errors/skips or invalid report reasons.

F06 directly reports `True` where the refusal assertion expects non-True for `NSpid:garbage\t77` and `NSpid:77 88` at immutable test line 756; a valid adjoining `NSpid:77` control instead reports `None` at line 759. The first two assertions establish the intended unsafe payload loss independently of the control failure. The pre-repair records bind the prior platform SHA and accurately separate reproduced old defects from current behavior; they were not replayed.

`evidence/expected_property_witnesses.json` records an independently selected named fixture and intended-property rationale for each of the 79 mutants, together with the exact current fixture source. Current artifact adjudication verifies an assertion section from that method, correct current source line/frame and a result logically linked to the intended weakening. M25 has such an intended assertion but still fails the strict no-error requirement. M06 is proved by the isolated empty power fixture; M16 has direct stale-temp and symlink assertions in addition to its child-exit assertion; M29 directly fails the required-gate presence assertion, with no missing-key runtime error.

## Completed exact-input Linux artifact

[Actions run 38641842326](https://github.com/flaggielover/ReBaseGuard/actions/runs/38641842326) is completed with conclusion failure, workflow **Cell-308 development review**, head exactly `875eb95575fa9dc137083667bf30cc4a5a228fe6`. These fields were independently queried through read-only `gh run view`; the input-commit file agrees. The immutable snapshot step and final artifact-preservation step succeeded; the mutation step failed. Artifact path: `/tmp/cell308-codex-review61/linux-r6-38641842326`.

| Artifact file | SHA256 |
|---|---|
| `validation.json` | `a3bf42d336c689c4cdf8d57064af617632a3416a1c015b8323cc7fbe3a351501` |
| `full-output.json` | `a3bf42d336c689c4cdf8d57064af617632a3416a1c015b8323cc7fbe3a351501` |
| `input-commit.txt` | `f595124d6588db9fe560c4eacf6a97a77492ab0f2eed419149261a8f0bf65992` |

The two JSON files are byte-identical. The record is development-only SYNTHETIC_VALIDATION on Linux x86_64, kernel `6.17.0-1022-azure`, CPython 3.12.3 (`/usr/bin/python3`, real `/usr/bin/python3.12`, GCC 13.3.0), timestamp `2026-10-14T21:43:54Z`, with new_target_evaluations=0. Its six before/after hashes equal one another and independently recomputed Git-blob SHA256 values at immutable 875eb955. All 79 properties, IDs, order, anchor arrays and mutated-source hashes match independent construction.

All 80 raw suite reports name exactly the 134 current unique methods. Every suite uses the complete strict discovery command and unchanged snapshot cwd. Baseline LX_PLATFORM_DIR is absent and bytecode suppression is set; each mutant uses its temporary platform copy. The baseline reports Ran 134 / OK / exit 0, zero failures/errors/skips/invalid reasons, no timeout/launch error. Every mutant likewise reports Ran 134 and exit 1, no skips/timeouts/launch errors. Independent reconstruction of every `_suite_record` field matches the artifact. The 78 valid kills have only assertion outcomes and zero unittest errors/invalid reasons. M25 alone reports one unittest error and one assertion failure.

| Group | Valid assertion kills | ERROR |
|---|---:|---:|
| M | 31 | 1 |
| R | 10 | 0 |
| X | 9 | 0 |
| N | 14 | 0 |
| Y | 3 | 0 |
| P | 5 | 0 |
| F | 6 | 0 |
| Total | 78 | 1 |

Every valid kill has a direct intended-property witness in the exact current fixture. The complete 79-case observations, fixture excerpts, full chosen assertion sections and strict status records are in `evidence/current_adjudication_checks.json`. All 194 test-source traceback frames, including the M25 wrapper helper frame, match the immutable line/statement and containing function. The direct observations were read and evaluated against the intended edits; they are not inferred from return code alone.

**M25: ERROR, not a valid kill.** Removing the digest guard still makes the original digest-mismatch fixture accept the wrong committed record: `test_reference_digest_must_match_the_committed_file` fails `assertIsNone(rec)` at current platform-test line 1076. But the new wrapper `test_uncommitted_fixture_withholds_root_contract` at line 136 also enters `assert_no_root` at line 94, `observe` at wrapper line 45 and `_committed_attestation` at line 32; `_git_blob` returns None for the uncommitted fixture, the weakened digest guard no longer refuses it, and `json.loads(data)` raises TypeError at mutated platform line 990. The summary is `FAILED (failures=1, errors=1)` and independent classification is ERROR with `UNITTEST_ERRORS`. The assertion cannot override that error. This is evidence of a nonqualifying mutant run; the unmodified baseline handles the supplied uncommitted fixture and passes. No global unmodified-code verdict follows.

M16 records a secondary child FileExistsError→StaleTmp traceback and child exit 1 before SIGKILL when its target-in-place weakening conflicts with the pre-existing target. This secondary child exception is disclosed and is not the property proof. Its separate `StaleTmp not raised` (test line 914) and `OSError not raised` for the stale .tmp symlink (line 921) directly establish the intended unsafe write weakening. It has zero unittest errors and a complete 134-method assertion report, so it remains a valid assertion kill. The report therefore says zero **unittest** errors for the 78 valid cases, not an absence of all child-process exceptions.

F06's native Linux record independently reproduces both unsafe payload acceptances at test line 756 and the valid adjoining-PID refusal at line 759, with three assertions and no errors. P05 and F03 retain direct invalid-token/mount-metadata witnesses under their faithful reanchors. The new wrapper regressions contribute to the complete count and specifically reveal the M25 error; their presence does not establish exhaustive wrapper behavior coverage.

**Final evidence disposition: baseline 134 PASS; mutation evidence 78 VALID ASSERTION KILLS / 1 ERROR; the all-79-valid-kill condition is unmet.** A source or harness repair and a fresh run bound to those changed exact inputs would be needed to satisfy that condition. A later report or run cannot retroactively change this immutable result. The development README and ledger's pending wording are preserved pre-validation statements; this report supplies the later failing result without rewriting them. No current 79/79 PASS claim is supportable for 875eb955.

## Supporting scratch outputs

`evidence/static_checks.json`, `harness_controls.json`, `record_checks.json`, `authored_subset_checks.json`, `expected_property_witnesses.json`, `current_adjudication_checks.json`, `ci_metadata.json`, `property_observations.txt`, `immutable_manifest.json`, `latest_ledger_zero_context.diff`, and three reproduction scripts preserve this review's independent checks. Copied immutable inputs and authorized authored/historical records are under `evidence/immutable` and `evidence/authored_or_historical`; the native validation record is copied once under `evidence/linux_artifact` because full-output was verified identical. The final output manifest enumerates only this reviewer's explicit outputs and binds this report's final SHA256.
