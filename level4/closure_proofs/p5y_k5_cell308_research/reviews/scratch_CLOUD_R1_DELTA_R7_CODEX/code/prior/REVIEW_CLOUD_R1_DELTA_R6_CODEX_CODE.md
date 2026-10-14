# Cell308 revision 6 — independent bounded code review

Reviewed immutable commit: **875eb95575fa9dc137083667bf30cc4a5a228fe6**. Delta baseline: **1c2ab8f7**. Workspace: `/Users/suzhe/.codex/worktrees/cell308-review61/ReBaseGuard`. Reviewer: fresh delegated code reviewer, without authorship of the reviewed inputs. Date: 2026-10-15, Asia/Tokyo.

**Disposition: R5-C1 is resolved for its recorded cases and adjacent ASCII/long-token checks. The restricted DEV_ONLY wrapper composition is corroborated within the reviewed source and synthetic boundaries. One actionable MINOR robustness defect remains: malformed attestation or acceptance-record paths escape the canonical verifier as exceptions. No fail-open result, usable memory allowance or operational authority was demonstrated.** An unqualified assertion that all malformed references produce a refusal result is unsupported until R6-C1 is repaired and the resulting immutable input is reviewed.

**Finding counts: BLOCKING 0 · MAJOR 0 · MINOR 1 · NOTE 0.** This is bounded code evidence, not a global fail-closed theorem or completion of an operational integration condition.

**Exact-input Linux evidence: baseline ARTIFACT-CORROBORATED PASS; aggregate mutation validation INCOMPLETE/FAILURE.** This reviewer subsequently inspected the parent-provided artifact from GitHub Actions run `38641842326`. The exact-input baseline runs 134 tests successfully. Of 79 registered low-level mutants, 78 are valid assertion kills and M25 is correctly classified ERROR because its run contains one assertion failure and one TypeError. Therefore there is no 79-valid-kills claim. The parent reported CI FAILURE; this reviewer did not independently query CI or execute a Linux job. Details and limits appear below.

## Input binding and exposure

`NS = level4/closure_proofs/p5y_k5_cell308_research`; `DEV = NS/streams/CLOUD_R1_LINUX_DEV`. The source copies used for all checks were extracted with `git show <immutable-SHA>:<explicit-path>`. Their Git blob IDs, byte counts and SHA-256 values are preserved in `code/input-manifest.json`. Every copied input was compared again with its immutable blob at finalization. All matched. The named worktree inputs also matched at that particular check; no overall clean-worktree requirement or cleanliness claim is made. Later additive reports or repairs do not change this report's immutable binding.

| Input relative to DEV | SHA-256 |
|---|---|
| `lx_platform.py` | `e8e33df59f3edd9f187db149cf77d1cca024403ffda5e21eb1c1d66980ec2074` |
| `lx_verified.py` | `ba59aab0ce408c97cfc46f037d525ca16b90a5261129fd75fc2d05a0a487ad65` |
| `lx_inventory.py` | `8ea74ed3621e805066727a4ca3f20253f9a85c90857aca8d8e41e02607cfa597` |
| `tests/test_lx_platform.py` | `03b5b136f0321b64338357f8f1eb6385a13efede32f9eb8fbaefe8fb6113dc8e` |
| `tests/test_lx_verified.py` | `a700e83cdbcfae380b671ed47291bae31100e30c007e6fa71d0b5f9bdcdadc1d` |
| `tests/run_mutants.py` | `e1374423c3137e6f82ee02c2dde7352fb1af40f9f720e4d0b94a958d276ea3a1` |
| `README_DEV_ONLY.md` | `818fa016aaff918e1a8123bb4c3a0c431769a6290271c4efcfb7301d38da0d12` |

Additional explicit inputs were `.github/workflows/cell308-dev-review.yml` (`86ccc75ef9288d835a854c1508a7cc5be6141a7a6489878d50f66418827a1aa4`), `.github/scripts/cell308_dev_review.py` (`18b8057a914c75804971acf64a6466914822308a5ae8a6373971e04509beadd6`) and the preserved `NS/reviews/REVIEW_CLOUD_R1_DELTA_R5_CODEX_CODE.md` (`525985cf92e458aaf71fabd7db0cf038941c392013a77bfa9a96199e979209a2`). The workflow invokes the development `tests/run_mutants.py`, not the separately preserved `.github/scripts` helper. `lx_inventory.py` was copied and hashed without executing it.

Repository reads were limited to those named immutable inputs, their narrow delta and explicitly checked applicable `AGENTS.md` paths. Only the empty `/Users/suzhe/.codex/AGENTS.md` existed among those checks. The `using-superpowers/SKILL.md` was read; it explicitly tells dispatched subagents to skip the skill. No broad namespace search was performed. The preservation report contains historical references to other material; none was followed.

No forbidden audit/interruption/exposure-disclosure content, MB-r1 postexecution or target record, or Cell309 file/branch/record was opened. No quarantine CLI, science, candidate, decoy, qualification, drift, certificate, evaluator or target module was executed. The candidate-constant test and every native/full-suite macOS case were excluded. No actual candidate blob was read. No remote host operation, configuration/secret inspection, settings change, repository mutation, commit or push occurred. All review writes, synthetic Git fixtures and transformed-source executions were confined to `/tmp/cell308-codex-review64/`; `new_target_evaluations = 0`.

Local execution used CPython **3.14.5**, Darwin arm64. Bytecode was disabled and selected test `TMPDIR` was restricted to `code/`. Git fixture processes explicitly disabled global/system configuration reads. Independent wrapper probes replaced infrastructure readers only, retained the actual canonical verifier and preflight logic, and made any unplanned `_read` native access raise an assertion. The patched repository and current-machine observations are synthetic testing fixtures, not public API seams or evidence of owner/reviewer authority.

## Source and behavioral dispositions

Source line references below refer to the reviewed immutable files.

| Required boundary | Disposition and evidence |
|---|---|
| R5-C1 complete payload parsing | **RESOLVED for recorded examples.** `lx_platform.py:595` partitions at the colon before splitting. Both `NSpid:garbage<TAB>77` and `NSpid:77 88` are refused; valid no-space, space and tab single-PID controls remain True. The first malformed example now returns False because its preserved payload contains two tokens. The contract requires refusal, not one particular refusal state. |
| ASCII numeric fields, conversion errors | **CORROBORATED for selected cases.** Positive PID/mount IDs use ASCII regexes at `:601,609–610`; device metadata uses `[0-9]`. Superscript, fullwidth, Arabic-Indic, mixed Unicode, signs, embedded NUL and zero-only PID fields are refused. Fullwidth/superscript mount and device fields are refused. Selected 5,000-digit positive ASCII PID and mount-ID controls return True without integer-conversion errors; an equally long all-zero PID is refused. This is supplied-text evidence, not a claim about native kernel corruption. |
| Committed/current-host canonical attestation | **CORROBORATED, subject to R6-C1.** `lx_verified.py:26,30–32,45–47` binds the actual canonical verifier to its checkout and omits the low-level machine override. Independent committed fixtures and real Git blob lookup distinguish accepted bytes from uncommitted overlays, absent paths, wrong digests, missing review lines, false reviewed/accepted fields, wrong schema, wrong current machine and lack of hardware binding. `root_cgroup_is_real` must be the exact boolean True; truthy non-booleans yield no root contract. No mechanically accepted fixture establishes real review authority. |
| Restricted public interface | **CORROBORATED.** Signature is `(attestation_ref=None, *, mode='execute') -> 'dict'`; `__all__` contains only `observe`. Fourteen independent reader/checker/observer/decision/machine/repository/raw-root/launch/detector keyword attempts raise TypeError. The internal callback is fixed canonical binding; no caller callback parameter exists. Invalid-mode behavior is covered by the unchanged selected test. This does not assert resilience against arbitrary in-process monkeypatching or import-path tampering. |
| Live launch corroboration | **CORROBORATED synthetically.** The wrapper obtains a default launch observation at `:53` and preserves preflight's canonical default independent observer at `:54–58`. Matching fixtures result in two no-argument reader calls in each mode. A changed invocation or missing second observation yields a FAIL launch gate. No supervisor launch or campaign was performed. |
| Raw memory, decisions, readiness and A5 | **CORROBORATED.** Only the strictly verified root claim reaches `memory_readings`; `:50–51` removes `effective_limit` and `cgroup_min_headroom`. Both remain absent for favorable and missing-memory fixtures. Memory is labelled RAW, not an operational allowance. `_UNDECIDED` is empty, the detector input is None/UNKNOWN and changing the low-level global DECIDED does not override the wrapper's explicit empty set. All three modes remain blocked; development_only is True, operational_ready is False, and A1/A2/A5 remain unmet. |
| Imports and execution authority | **CORROBORATED statically for these modules.** The wrapper imports only `pathlib` and `lx_platform`; the platform imports only stdlib. No science import, dynamic science import, launch/execution method or campaign entry point was added. The mode labels select observation checks and confer no authority. |
| Evidence binding and workflow | **CORROBORATED statically.** `run_mutants.py:335–338` now hashes both wrapper source and its test file alongside platform/inventory/platform-test/harness. Workflow path filtering includes `lx_verified.py`, the snapshot ref is `github.sha`, and the full discovery command uses the snapshot harness. AST counts are 112 platform tests plus 22 wrapper tests = 134. All 79 registry IDs are unique, group sizes match M32/R10/X9/N14/Y3/P5/F6, sequential anchors each occur once, and every transformed platform source parses. Native outcomes are described separately below; the aggregate mutation result is incomplete. |

## R6-C1 — MINOR — malformed subprocess paths escape the canonical refusal boundary

Locations: **`lx_platform.py:963–968`**, called from `attestation_valid` at `:986` and `:1002`, and from the new public `lx_verified.observe` at **`:45`**.

The parser accepts any Python string as a reference path after checking the key set and digest format. `_git_blob` catches `OSError` and `subprocess.SubprocessError`, but `subprocess.run` rejects malformed argv strings before launching Git with exceptions outside that catch.

Independent minimal public reference witnesses are:

```python
observe({"path": "\x00", "sha256": "0" * 64})
# ValueError: embedded null byte

observe({"path": "\ud800", "sha256": "0" * 64})
# UnicodeEncodeError: ... surrogates not allowed
```

The recorded probes used synthetically committed fixtures and their valid digests, with the same outcomes. In each case the exception escapes the first verifier call and no DEV_ONLY observation/refusal result is returned. The four complete exception traces are preserved in `code/probes_result.json`.

The same two strings in the `acceptance_record` field of an otherwise schema-correct, strictly reviewed/accepted, matching-machine committed fixture cause the same exceptions when the canonical verifier reads the review file. JSON validly represents both values. These are two entry points and four witnesses for **one missing malformed-path handling defect**.

**Required bounded repair:** reject unsupported path strings, or handle their argv validation/encoding exceptions inside canonical `_git_blob` and return None so the existing verifier records refusal reasons. Cover both public reference paths and committed acceptance-record paths with NUL and surrogate regressions. Preserve valid committed/current-host controls and add a targeted weakening with explicit assertion witnesses. Do not turn this repair into a favorable-reader or caller-verifier seam.

This is a refusal-result/robustness defect. It produces **no returned root flag, memory allowance, preflight PASS or operational_ready=True**. No native malformed kernel input, campaign behavior or whole-preflight false PASS is claimed. The selected authored suite lacks these path cases; its passing baseline and the limited mutation outcomes coexist with this independent witness.

## Executed evidence

- **29 unchanged selected tests: PASS**, zero failures/errors/skips. Seven supplied-proc-view methods plus all 22 wrapper methods; complete output and actual imported source hashes are in `code/selected.stderr.txt` and `code/selected_result.json`. Native lifecycle/host/assessment/CPU/preflight/pin cases and the candidate-constant method were not selected locally. Later Linux artifact inspection is a separate evidence set.
- **85 independent probe cases:** 81 meet their expected outcomes; four record the R6-C1 path exceptions. These include the delimiter/ASCII/5,000-digit controls; committed/worktree/current-machine/root-type provenance cases; 14 public seam refusals; all modes; UNKNOWN detector and empty decisions; withheld quantities; fresh launch mismatch/missing observations; and a committed deeply nested non-schema JSON fixture refused by this interpreter. The first exploration expected None for the two-token garbage payload, but its actual False is a correct refusal; that over-specific expectation was corrected before the final record. No source change was made. Scripts, final outputs and complete captured exception traces are in `code/probes.py`, `probes_result.json` and `probes.stdout.txt`.
- **F06 selected replay: intended assertion kill**, same 29 tests, three assertion failures, zero errors/skips. Both original R5-C1 payloads return True under the restored payload-dropping parser and fail the refusal assertions. Its no-space single-PID control also fails, consistent with that parser's dropped sole token. Actual transformed platform hash: `0531b5c69ff6c040d2a7d92c40154cc4076e5743031fe9f52d3e5c5940ddaeb8`. See `code/F06_result.json`, stdout/stderr and `code/platform-mutants/F06/`.
- **Nine independent wrapper-only weakening checks W01–W09:** all yield intended assertion failures on the same passing 29-test selection, each with zero errors/skips and normal exit 1. They weaken canonical verification, strict root boolean, withheld fields, empty policy, unavailable detector, fresh launch observation, ready=False, A5 unmet, and public machine-seam refusal. Complete transformations, hashes and failure names are in `code/wrapper_mutants.py`, `wrapper_mutants_result.json` and `code/wrapper-mutants/`. These are a separate, limited synthetic stress set, not exhaustive wrapper mutation coverage.
- **Whole-registry static checks:** 134 test methods, 79 unique low-level mutants, correct groups, unique sequential anchors and parsable transformed source; hash coverage agrees with immutable inputs. See `code/check_harness.py` and `harness_static.json`. Static application is not execution of all mutants.

The registered **79 mutations target `lx_platform.py`**. Running wrapper tests alongside them does **not** establish mutation coverage of the wrapper. Neither the limited W01–W09 stress set nor F06 selected replay establishes full native Linux validation. No mutation-result count combines these distinct evidence sets.

Reproduction uses the preserved scratch copies only:

```sh
GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null TMPDIR=/tmp/cell308-codex-review64/code PYTHONDONTWRITEBYTECODE=1 python3 -B -W error::ResourceWarning /tmp/cell308-codex-review64/code/run_selected.py
GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null TMPDIR=/tmp/cell308-codex-review64/code PYTHONDONTWRITEBYTECODE=1 python3 -B -W error::ResourceWarning /tmp/cell308-codex-review64/code/probes.py
PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/cell308-codex-review64/code/check_harness.py
GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null TMPDIR=/tmp/cell308-codex-review64/code PYTHONDONTWRITEBYTECODE=1 python3 -B -W error::ResourceWarning /tmp/cell308-codex-review64/code/wrapper_mutants.py
```

## Exact-input Linux artifact inspection

Artifact directory: `/tmp/cell308-codex-review61/linux-r6-38641842326/`. Parent-provided files were read after the initial source/probe findings and before report finalization.

| Artifact | SHA-256 |
|---|---|
| `input-commit.txt` | `f595124d6588db9fe560c4eacf6a97a77492ab0f2eed419149261a8f0bf65992` |
| `validation.json` | `a3bf42d336c689c4cdf8d57064af617632a3416a1c015b8323cc7fbe3a351501` |
| `full-output.json` | `a3bf42d336c689c4cdf8d57064af617632a3416a1c015b8323cc7fbe3a351501` |

The commit file identifies **875eb95575fa9dc137083667bf30cc4a5a228fe6**. The two JSON files are byte-identical copies of one execution record, not independent runs. All six recorded input hashes, both before and after execution, equal the immutable/copy hashes above. Recorded environment: CPython 3.12.3, Linux `6.17.0-1022-azure`, x86_64, UTC `2026-10-14T21:43:54Z`; inherited LX_PLATFORM_DIR cleared for the baseline, bytecode disabled, ResourceWarning treated as an error.

Independent parsing of the complete baseline stderr corroborates **134 tests, OK, exit 0, zero failures/errors/skips**, no invalid-run or resource/unraisable indicator. All 79 unique registered IDs and sequential anchor counts agree with the immutable registry. Every recorded transformed-platform hash was independently compared with the transformation reconstructed by this review's static checker and matches.

The artifact records **78 KILLED · 0 SURVIVED · 1 ERROR · 0 NOT_APPLIED**. For all 78 credited kills, complete stderr independently contains 134 tests and named assertion failures, no error headings or resource/unraisable indicator. This supports those **78 exact-input low-level assertion kills**; it does not support a complete 79-mutant validation pass.

**M25 is an invalid mixed-outcome run.** Its recorded transformed source hash is `3e769677d48329d62c174a62af332c14a30ffaba3f7cbd14d3a671052117d247`. The mutant removes the attestation digest rejection. The intended different-valid-blob mismatch assertion fails in `test_reference_digest_must_match_the_committed_file`, but the wrapper's uncommitted-fixture case also errors: `_git_blob` returns None, the removed digest guard no longer rejects it, and `json.loads(None)` raises TypeError. The run summary is `FAILED (failures=1, errors=1)`, 134 tests, exit 1; reason `UNITTEST_ERRORS`. The strict harness correctly rejects this run as ERROR. The error is induced by the weakening, not a demonstrated unmodified-baseline defect, and it must not be reclassified as a kill or discounted because the intended assertion also exists.

A bounded correction can refuse absent blob data independently before digest/JSON processing while retaining M25's genuine different-valid-blob digest weakness and its assertion witness. That change is a proposed future repair, not reviewed code at 875eb955. No harness-classification relaxation is justified by this artifact.

The parent reported GitHub Actions run **38641842326: FAILURE**, consistent with the artifact's aggregate condition. This reviewer inspected evidence only; no CI status query or remote reproduction occurred. `code/linux_artifact_assessment.json` preserves the independent hash/anchor/report checks and M25's complete recorded suite/error trace. The native baseline and 78 valid low-level kills coexist with the new R6-C1 witnesses, which are absent from the committed suite. No operational/governance acceptance or global theorem follows.

## Continuing limits

The report preserves the R5 review's bounded helper interpretation and unresolved integration conditions. A successful synthetic record, reader composition or CI run cannot establish route/amendment acceptance, owner choice, hardware/provider/storage durability, operational readiness, completed A1/A2/A5, fixed science-import/pin-point completion, computing-mode execution authority, campaign status, designation, qualification, freeze, grant, S1 ruling or target authority. Every governance and D-* decision remains open.

This report is bound to **875eb955** and its named inputs. Any subsequent repair requires its own immutable input verification and bounded follow-up. The exact-input Linux artifact resolves the earlier pending runtime-evidence status only to the baseline PASS and 78 valid kills/one ERROR documented above. It does not erase R6-C1, complete the mutation campaign, or upgrade the limited synthetic checks into a global theorem.
