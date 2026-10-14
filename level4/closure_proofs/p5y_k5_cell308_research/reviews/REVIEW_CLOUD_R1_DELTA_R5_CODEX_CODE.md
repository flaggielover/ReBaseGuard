# Cell308 revision 5 — independent bounded code follow-up

Reviewed immutable SHA: **13047bbebe509c1c04cd25ea90651c853cc61b03**. Narrow code/test/harness/README comparison: **aef3bead293759e0e4cc1af26e0c01f060bb9abc..13047bbebe509c1c04cd25ea90651c853cc61b03**. Reviewer: fresh delegated code reviewer, with no authorship or prior-review involvement. Date: 2026-10-15, Asia/Tokyo.

**CODE VERDICT: NOT_FAIL_CLOSED**, confined to the documented supplied-record helper boundary. The five original F1–F5 examples are repaired. One adjacent MINOR residual permits malformed or multi-PID NSpid payloads to establish a complete proc view. **No native malformed `/proc` record or whole-preflight false PASS was demonstrated.** The empty default decision set continues to block the synthetic favourable preflight control.

**Native/full Linux validation: UNVERIFIED by this reviewer.** At dispatch the parent identified exact-commit GitHub Actions run `38639066841` as pending. No artifact or completed result from that run had been received when this report was written. The selected macOS runs below cannot establish the 111-test native baseline or all 78 full-suite mutation outcomes. Later exact-input Linux evidence can resolve this runtime uncertainty; it cannot erase the reproduced helper result.

## Input binding and exposure

Workspace: `/Users/suzhe/.codex/worktrees/cell308-review61/ReBaseGuard`. Entry and initial-report finalization checks observed the reviewed SHA and an empty `git status --short`. Each copied development input was byte-equal to its immutable Git blob and working file at both checks. Actual imported module hash was recorded in every selected baseline/probe/mutant result. The later supplement records preservation of the reviewed input bytes during disjoint parent work and makes no current global working-tree cleanliness claim.

| Input relative to `NS/streams/CLOUD_R1_LINUX_DEV/` | SHA-256 |
|---|---|
| `lx_platform.py` | `e4f30c816a31a2f36fe7fab88fb4af957457d817b88fc2a8b75324cdb7ef705e` |
| `lx_inventory.py` | `8ea74ed3621e805066727a4ca3f20253f9a85c90857aca8d8e41e02607cfa597` |
| `tests/test_lx_platform.py` | `adf041b57145ae2266fc51b499997721833ee3e6c0e3d62c36496117c9521ea5` |
| `tests/run_mutants.py` | `ddf24e5db7031ed6074b14949497d32561bf0304919d43c4703f19585e4417fa` |
| `README_DEV_ONLY.md` | `4362a1d675a4ce19ee93258faca00b2e750813f5d39cabde9a322d704d0a635d` |

`NS = level4/closure_proofs/p5y_k5_cell308_research`. Repository content read was limited to the preserved R4 code review and R4 amendment review, the proposed R4 erratum E1, development platform source/test/harness/README, and immutable blobs/diffs of those inputs. `lx_inventory.py` was copied and hashed without executing it. Applicable ancestor and scoped `AGENTS.md` paths were individually checked; the only existing file was the empty `/Users/suzhe/.codex/AGENTS.md`. The system `using-superpowers/SKILL.md` was read and explicitly instructs delegated subagents to skip it.

A root `rg --files` search for `AGENTS.md` used exclusions for restricted audit/interruption and Cell309 paths and found none. A pathname/stat-only narrow-commit inventory incidentally listed the research `TARGET_INTEGRITY_LEDGER.jsonl`; no ledger content was opened. No forbidden audit/interruption/exposure-disclosure content, MB-r1 postexecution/target record, or actual Cell309 material was opened. References to restricted material inside permitted reviews were not followed.

No science, candidate, decoy, qualification, drift, certificate, evaluator or target module was executed. The candidate-constant test was excluded; no candidate blob was read. No repository edits, commits, pushes, installations, host settings changes or remote compute operations occurred. All writes and transformed-source execution were under `/tmp/cell308-codex-review63/`. `new_target_evaluations = 0`.

Execution used macOS 26.5.2 arm64, Python 3.14.5. `LX_PLATFORM_DIR` selected copied or transformed source, bytecode was disabled, and selected test `TMPDIR` was confined to the review's `code/` directory. The selected baseline retained the original test methods; an explicitly negative synthetic outer mock replaced the default live launcher reader, while nested matching/mismatching test mocks remained effective. No native/full Linux suite was attempted on macOS.

## F1–F5 and README dispositions

Source line references are for `lx_platform.py` at the reviewed SHA.

| Item | Disposition | Independent evidence and limit |
|---|---|---|
| F1: intermediate clock divergence | **RESOLVED for original examples and targeted semantics** | `:277–293` checks all adjacent pairs and independently start/end, with unchanged strict 2 s tolerance. The original REALTIME excursion becomes AMBIGUOUS; the analogous BOOTTIME excursion becomes CONTAMINATED. Exact 2 s is CLEAN; 2 s plus 1 ns is AMBIGUOUS. Two 1.5 s adjacent BOOTTIME discrepancies accumulate to 3 s at endpoints and remain CONTAMINATED, demonstrating retention of the endpoint check. |
| F2: intermediate suspend counter excursion | **RESOLVED for original example and targeted precedence** | `:296–305` considers all sequence members, rejects malformed/bool counters, gives any decrease/reset S′ AMBIGUOUS precedence, and otherwise classifies an increase CONTAMINATED. Original `0 → 1 → 0` is AMBIGUOUS with no S′ contamination reason; `0 → 1 → 1` is CONTAMINATED; `5 → 4 → 5` stays S′ AMBIGUOUS. Independent positive K′ contamination still makes the aggregate CONTAMINATED when S′ is ambiguous. |
| F3: mount metadata | **RESOLVED for original example and targeted numeric boundary** | `:609–611` refuses the original three-garbage header and isolated malformed/zero IDs and negative device components. The valid single unrestricted proc-mount control returns True. All 16 committed malformed-metadata subcases pass. This establishes supplied-text behavior, not native mountinfo provenance or corruption behavior. |
| F4: duplicate NSpid fields | **RESOLVED for original duplicate examples; PARTIAL at the adjacent payload boundary** | `:595–597` refuses conflicting duplicates in either order and identical duplicates. The first valid single field control passes. The retained whitespace-token parser can still drop an unrecognised or additional PID payload adjoining the colon, producing the R5-C1 false completeness below. |
| F5: duplicate PID identities within either snapshot | **RESOLVED for original example and targeted ambiguity** | `:676–677` refuses repeated PIDs in either snapshot before ownership exemptions. Original conflicting end-parent identities return None; duplicate start identities and unrelated noncampaign duplicates also return None. Valid forward reuse reports the external child at 100%; the valid observed campaign-parent control still exempts its child. Native `cpu_ticks` snapshot production was not exercised. |
| README R4-D1 stale contract reference | **RESOLVED** | The current platform row now names amendment r4 §3 and erratum E1. Revision-5 descriptions and AST-confirmed source counts (111 test methods, 78 registered mutants) agree. Historical R4 outcomes remain separately described, and current native validation/independent review is marked pending. This code review does not independently validate the historical R4 CI claim. |

Erratum E1 accurately requires all adjacent and endpoint clock comparisons, unchanged thresholds, counter precedence, numeric metadata, exactly one recognised namespace field/token and unique PID per snapshot. The original repair outcomes match those requirements. R5-C1 remains inconsistent with its requirement that malformed/unrecognised namespace evidence cannot establish completeness.

## New actionable finding

### R5-C1 — MINOR — a payload adjoining `NSpid:` is discarded and can falsely establish a complete view

Location: **`lx_platform.py:595`** (selected token extraction), with the favourable decision at `:598–602,618`.

With `pidns=L.INIT_PID_NS` and the valid unrestricted mount:

```text
23 28 0:22 / /proc rw,relatime - proc proc rw
```

the independent D01 probes supply either status text:

```text
NSpid:garbage<TAB>77
NSpid:77 88
```

`<TAB>` denotes a real tab; these are separate probe records. **Both return True.** The control `NSpid:<TAB>77` also returns True.

`ln.startswith("NSpid:")` recognises the field, but `ln.split()[1:]` discards the entire first whitespace token. In the first case that discarded token includes the unrecognised `garbage` value; in the second it includes PID 77, so the two-value payload is reduced to the single favourable token 88. Uniqueness of the field therefore does not establish validity or uniqueness of its PID payload.

**Required bounded correction:** parse the recognised field/value delimiter before splitting the value, preserve the whole payload after `NSpid:`, and validate exactly one recognised positive integer token. Refuse the two concrete records above. Preserve valid tab/space-separated single-PID controls and all existing duplicate-field refusals. Add an assertion regression and a corresponding weakening mutant or equivalent evidence of detection.

This is a malformed injected-record acceptance, **not a claim that the Linux kernel normally emits either record**, nor a demonstration of host-exclusivity or full-preflight PASS. It is actionable because the current public supplied-text helper and erratum promise to refuse malformed/unrecognised proc evidence. No unrestricted seam hardening is requested.

New findings: **BLOCKING 0 · MAJOR 0 · MINOR 1 · NOTE 0**. No other actionable defect was established within this bounded follow-up.

## Executed evidence

- **51 unchanged selected synthetic tests: PASS**, zero failures, errors or skips. Selection and complete output are preserved in `code/selected_base_result.json` and `code/selected_base.stderr.txt`. Selected classes cover assessment, supplied snapshots/proc view, two raw-memory controls, and seven synthetic preflight/launcher cases. Candidate/native lifecycle/native boot/live assessment/live CPU/live launch/live preflight/platform-pin tests were excluded; this is not a full-suite result.
- **27 independent probes** in `code/probes63.py`: all five original F1–F5 examples, four controls, 16 adjacent refusal/semantic cases met expectations; the two D01 false-completeness cases form the single new finding. Exact records, results and actual imported hash are in `code/probes63_out.json`.
- **Whole-registry static checks:** 111 `test_*` methods, 78 unique registered mutants with expected groups M32/R10/X9/N14/Y3/P5/F5. Every sequential mutation anchor occurs exactly once and every transformed source parses. See `code/harness_checks63.json`.
- **Selected behavioral mutation checks:** F01–F05 and revised Y03 each run the same passing 51-test selection and produce intended assertion failures, zero errors/skips. F01 is detected by both middle-clock cases; F02 by the middle reset/invalid counter cases; F03 by malformed metadata; F04 by duplicate fields; F05 by either-snapshot duplicate PID tests; Y03 by the out-of-order sample test. Complete per-mutant output and imported transformed hashes are under `code/mutants/`. These are selected synthetic assertion kills, not the full Linux 78-mutant claim.
- `code/input_hashes.json` and `code/final_source_verification.json` bind inputs, interpreter/platform and clean immutable HEAD. Preserved R4 code-review SHA-256 is `0940ed8f9c6d581b4cfc0a6707239bf25dec420cd98d187e21c2c6c2c52d8fa3`; R4 amendment-review SHA-256 is `5761dbf7c4debff496640d01b5d1ebc5b1b878b7a28a39c2c457e19856becc27`; proposed erratum E1 SHA-256 is `b73ecabf0dbf7fe2dda650b6f8c98808b03137faaa4cc69d8e1a4c35bc237e84`.

Reproduce from the temporary copied-source tree:

```sh
TMPDIR=/tmp/cell308-codex-review63/code LX_PLATFORM_DIR=/tmp/cell308-codex-review63/code/base PYTHONDONTWRITEBYTECODE=1 python3 -B -W error::ResourceWarning /tmp/cell308-codex-review63/code/run_selected63.py
LX_PLATFORM_DIR=/tmp/cell308-codex-review63/code/base PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/cell308-codex-review63/code/probes63.py
PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/cell308-codex-review63/code/check_harness63.py
```

## Continuing scope conditions

The verdict explicitly carries the trusted-wrapper conditions from R4 and E1: raw-memory `root_cgroup_is_real is True` must derive from verified, committed, current-host attestation; caller-provided decisions, checker/reading/observer seams and configuration need independently reviewed restrictions; the complete fixed science-import list and wrapper must be pinned and reviewed at the pin point in every computing mode. Synthetic injection is evidence for the documented helper boundary, not proof that those provenance/integration conditions have been completed.

No route/amendment acceptance, owner choice, operational readiness, global fail-closed theorem, native lifecycle/hardware/storage/provider guarantee, designation, qualification, freeze, grant, S1 ruling or target authority follows from this report. All open decisions and governing sequence conditions remain open. Repair R5-C1 and independently review the resulting immutable input before upgrading this helper-level code verdict.

## Post-report supplement — exact-input Linux artifact

This supplement **supersedes the pending native/full-suite evidence status above only**. The original findings, exposure statement for repository material, continuing conditions and **NOT_FAIL_CLOSED** verdict remain unchanged. The parent subsequently supplied downloaded outputs from GitHub Actions run `38639066841` and reported its final status as SUCCESS. This reviewer inspected those local artifacts; the CI status was not independently queried and no Linux job was re-executed.

Artifact directory: `/tmp/cell308-codex-review61/linux-r5-38639066841/`.

| Artifact | SHA-256 |
|---|---|
| `input-commit.txt` | `e607a27a71d9da071f0df44dcf66fb53df69b673c340bc0a3144b9cf936836b9` |
| `validation.json` | `d46587398f7807b8e11c2dce7c68b889fa3d2a8a29daac5947092d80a29b349a` |
| `full-output.json` | `d46587398f7807b8e11c2dce7c68b889fa3d2a8a29daac5947092d80a29b349a` |

The commit file names the exact reviewed SHA. `validation.json` and `full-output.json` are byte-identical copies of the same record, not two independent runs. The four platform/inventory/test/harness input hashes before and after the run equal this review's immutable/copy hashes. The baseline has inherited `LX_PLATFORM_DIR` cleared; bytecode is disabled. Its recorded command uses `/usr/bin/python3 -B -W error::ResourceWarning -m unittest discover` against the snapshot's development test directory. Recorded environment: CPython 3.12.3, Linux kernel `6.17.0-1022-azure`, x86_64; UTC record `2026-10-14T21:22:43Z`.

Independent parsing of the preserved complete stderr agrees with the summaries: **baseline 111 tests PASS**, exit 0, zero assertion failures, errors or skips. All **78 unique registered mutants** run the same 111 tests, exit 1 and report assertion failures, with zero errors/skips, no timeout/launch error/invalid-run reason or ResourceWarning/unraisable indicator. For every mutant this reviewer independently reconstructed the transformed source from the copied exact-input registry, checked its sequential unique anchor counts and confirmed the recorded transformed-source SHA-256. The registered IDs and complete outcome-name tallies agree; the artifact reports `new_target_evaluations = 0`.

F01's two middle-clock tests, F02's reset/malformed intermediate-counter tests, F03's 16 metadata subcases, F04's conflicting/identical duplicate-field cases, F05's start/end duplicate-PID cases and Y03's out-of-order-sample case supply the intended behavioural attribution in the full Linux outputs, consistent with the separate selected synthetic replay. Thus the pending full Linux test/mutation evidence is now **ARTIFACT-CORROBORATED PASS for these exact inputs and recorded environment**. This is inspection of execution evidence, not an independent remote reproduction or hardware/provider/storage guarantee.

The committed suite and registered F04 mutant do not test either new R5-C1 payload. A clean 111-test baseline and 78 valid mutation kills therefore coexist with the independent false-completeness results. This supplement does not upgrade the helper-level code verdict or claim a native malformed NSpid record, whole-preflight false PASS, completed trusted wrapper or operational/governance acceptance.

After the parent reported disjoint plan/wrapper work in the shared checkout, this reviewer reverified only the five reviewed development inputs against immutable `13047bbebe509c1c04cd25ea90651c853cc61b03` blobs and the preserved copies. All remain byte-equal. HEAD still identifies that reviewed SHA. No new plan/wrapper file was read or reviewed, and no claim of current overall working-tree cleanliness is made. This final review is bound to the immutable revision-5 input and its exact CI artifact, not to later disjoint authored files. See `code/supplement_source_verification63.json`.

The detailed independent artifact checks are saved in `code/linux_artifact_assessment63.json`. Preserve the following scratch evidence with this report: `code/probes63.py` and `probes63_out.json`; `run_selected63.py`, selected baseline result/stdout/stderr; `check_harness63.py`, `harness_checks63.json` and `mutants/` full selected outputs; exact `base/` source copies; `input_hashes.json`, `final_source_verification.json`, `supplement_source_verification63.json` and `linux_artifact_assessment63.json`; plus the three original downloaded Linux artifact files above. The probes and their input/output records are the essential independently reproducible evidence for R5-C1.
