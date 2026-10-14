# Cell308 revision 4 — fresh independent code review

Reviewed immutable commit: **aef3bead293759e0e4cc1af26e0c01f060bb9abc**. Compared code/tests/harness with **df2f1ea3**. Reviewer: fresh delegated correctness reviewer; authored none of the repairs or earlier reviews. Date: 2026-10-15, Asia/Tokyo.

**CODE VERDICT: NOT_FAIL_CLOSED.** The original targeted examples are repaired, and the default supervisor corroboration is real. Five bounded adjacent input-validation/assessment defects remain: intermediate clock and suspend observations can be ignored, malformed mount metadata and duplicate namespace fields can establish a complete view, and ambiguous snapshot identities can exempt an external child. This verdict concerns these individual evidence-producing APIs. **No whole-preflight false PASS and no native Linux reproduction were demonstrated.** Default preflight remains blocked by open decisions.

**Native Linux runtime: UNVERIFIED / pending.** The parent reported exact-commit CI run `38636549368` pending; no result from that run was received before this report. A later supplement must bind its evidence to its actual source hash. This review does not accept a route/amendment, declare operational readiness, or authorize any official step.

## Exact input bindings and exposure

Workspace: `/Users/suzhe/.codex/worktrees/cell308-review61/ReBaseGuard`. Entry and final verification both observed the exact reviewed HEAD and empty `git status --short`. Copies were byte-equal to both immutable Git blobs and working files.

| Input relative to `NS/streams/CLOUD_R1_LINUX_DEV/` | SHA-256 |
|---|---|
| `lx_platform.py` | `d2ceb74e0eb3fae3a8349efaa18988cb56a9f03d4ff813d656eda5a082a328b5` |
| `lx_inventory.py` | `8ea74ed3621e805066727a4ca3f20253f9a85c90857aca8d8e41e02607cfa597` |
| `tests/test_lx_platform.py` | `e1f2297dab51a87eb2fc3563c7029e27c8b5eea24205829086e79c27f722f784` |
| `tests/run_mutants.py` | `26347426ebb361c4a73232605a62dbb84dea7c45f683e00fedd42cbd5f706919` |

`NS = level4/closure_proofs/p5y_k5_cell308_research`. Repository content opened was limited to:

- `NS/reviews/REVIEW_CLOUD_R1_DELTA_R3_CODEX_CODE.md`, `REVIEW_CLOUD_R1_DELTA_R3_CODEX_AMENDMENT.md`, and `REVIEW_CLOUD_R1_DELTA_R3_CODEX_EVIDENCE.md`. The latter two names have no `CODE` before their suffixes.
- Development `lx_platform.py`, `lx_inventory.py`, `README_DEV_ONLY.md`, `tests/test_lx_platform.py`, and `tests/run_mutants.py`; scoped diffs/statistics and immutable blobs of those code inputs. A development-only filename listing was made, but listed result files were not opened.
- Individually checked applicable ancestor/in-namespace `AGENTS.md` paths. `/Users/suzhe/.codex/AGENTS.md` exists and is empty; no applicable nonempty instructions were found. The system `using-superpowers/SKILL.md` was read and explicitly says delegated subagents skip it.

No forbidden audit/interruption/exposure-disclosure file, MB-r1 postexecution or target record, or Cell309 file/branch/record was opened. References to such material within allowed files were not followed. No candidate, science, decoy, qualification, drift, certificate, cell, scanner or quarantine evaluator was executed. The candidate-constant test was excluded. No repository edits, commits, pushes, installations or host settings changes were performed. Temporary Git fixtures created and committed only disposable synthetic attestation records under the review's `/tmp` test directory; they were not changes to the reviewed repository.

All copies, scripts, fixture outputs and this report are under `/tmp/cell308-codex-review62/`. Execution used macOS 26.5.2 arm64 and Python 3.14.5. `LX_PLATFORM_DIR` pointed to the copied module; bytecode was disabled and `TMPDIR` was within the review's `code/` directory.

## Dispositions of P1–P6 and A2

All code line references below are relative to development `lx_platform.py` at the exact reviewed commit.

| Previous finding | Disposition | Independent basis and limit |
|---|---|---|
| P1, forward PID reuse | **RESOLVED for the original valid-snapshot case; adjacent schema gap F5** | `:667–669` now requires the exact own parent key in the relevant snapshot. Q62A reports the unrelated child at 100%, rather than suppressing it. Relevant existing synthetic tests pass, including the live-child/exited-child and missing-parent cases. A snapshot with two identities for the same parent PID remains accepted (F5). |
| P2, strict stat/boot evidence | **RESOLVED for the reported defect** | `proc_stat :126–145` checks requested PID, recognised state and nonnegative fields. `identity_state :185–234` validates current/recorded boot evidence, namespaces, stat identity/types, and command digests before their comparisons. Selected tests cover malformed current/recorded boots, unknown task states, and malformed records; all pass. Native lifecycle/zombie behavior remains UNVERIFIED here. |
| P3, malformed assessment records | **PARTIALLY RESOLVED** | `:266–299,304–306` reject malformed endpoints/samples, noninteger clocks, bool/negative counters and malformed boot IDs; selected regression tests pass. Recognised intermediate clocks/counters are checked for type but their observed changes can still be ignored (F1/F2). |
| P4, CPU arithmetic | **RESOLVED for the reported cases** | `:643–665,675–677` require finite positive duration, finite nonnegative threshold, strict positive integer frequency, recognised keys/records/ticks, and refuse a stable external counter regression. Selected invalid-duration/threshold/frequency/tick/regression tests pass. No native tick regression was asserted. |
| P5, `/proc` completeness | **PARTIALLY RESOLVED** | `:594–606` refuse the original malformed token, non-proc filesystem/root and duplicate-mount examples; all selected relevant tests pass. The mount metadata fields themselves and uniqueness of the NSpid field remain unchecked (F3/F4). |
| P6, Y01/Y03 coverage | **RESOLVED in source/selected-test scope; full kills UNVERIFIED** | Host-MemTotal and out-of-order-sample assertions are now present and pass. Y01–Y03 are registered. All 73 mutation entries have unique sequential anchors and syntax-valid transformed sources. No full harness was run here; the parent Linux replay must establish intended behavioral kills against a passing baseline. |
| A2, supplied supervisor record | **RESOLVED for the default production preflight path** | `:1060–1062` calls the current live supervisor reader by default and `:1008–1021` corroborates supplied fields against that observation. Q62G records one default observer call and FAIL for a forged favourable supplied record when independent observation is negative. Matching/mismatching synthetic observer regressions pass. An explicitly injected observer remains a documented test seam, to be fixed/restricted by a future trusted wrapper. |

Raw-memory strict `True`, explicit `decided`, checker/reading/observer injection, and caller-supplied fixed-import lists remain the intentionally documented trusted-wrapper integration conditions. They are not newly classified here as operational bypasses, nor are their provenance obligations considered completed. No operational acceptance follows from helper-level PASS/readings.

The harness now runs an unmodified baseline first, clears inherited `LX_PLATFORM_DIR` for that baseline, preserves full output/test counts/provenance, and classifies errors/skips/timeouts as invalid runs. These are substantive E2 repairs in static scope. Fresh full-suite failure attribution remains UNVERIFIED until the parent's Linux evidence arrives.

## New actionable findings

### F1 — MINOR — a transient observed clock divergence can return CLEAN

Location: `:277–289,319–324`. Q62C uses complete records with recognised integer clocks. All records have the same valid boot, suspend count 0, and AC power; journal evidence is an available empty list. Start clocks are `(mono,boot,real)=(0,0,0)s`; end is `(120,120,120)s`; the sole middle record is `(60,60,90)s`. `assess` returns **CLEAN**, `clean=True`, no reasons.

The middle observation supplies a 30-second wall-vs-monotonic divergence; the two adjacent intervals each exceed the existing 2-second tolerance, with opposite signs. Endpoint subtraction cancels that evidence because sample real/boottime fields are only type-checked. This is an assessment-semantic defect on supplied observations, not a demonstrated native pause or whole-preflight bypass.

**Required correction:** apply the existing K'/P clock-difference checks to consecutive records in `[start,*samples,end]`, retaining endpoint checks as appropriate. An observed intermediate divergence must not disappear because the final clock realigns. Add the concrete Q62C case and a middle boottime/monotonic inconsistency, with a fully clean aligned sequence as the control.

### F2 — MINOR — an intermediate suspend counter excursion can return CLEAN

Location: `:292–299`. Q62D has fully aligned clocks at 0, 60 and 120 seconds and otherwise identical clean channels, but suspend counts are `0 → 1 → 0`. It returns **CLEAN**, `clean=True`, no reasons. The recognised middle counter is type-checked while change detection compares only the endpoints.

A changed or subsequently decreasing counter is incompatible with an evidentially clean interval. This supplied sequence establishes inconsistent observations; it does not assert the normal Linux counter resets this way.

**Required correction:** compare suspend counters across the complete sequence. Any observed change must prevent CLEAN; classify a recognised increase as contamination and a decrease/reset as ambiguous or another explicit nonclean state. Add Q62D and the unchanged `0 → 0 → 0` control.

### F3 — MINOR — malformed mount metadata can establish a complete view

Location: `:596–608`. With initial PID namespace and status `NSpid:\t77\n`, Q62E supplies:

```text
garbage garbage garbage / /proc rw,relatime - proc proc rw
```

`proc_view_complete` returns **True**. Replacing the valid mount ID, parent ID and `major:minor` metadata with unrecognised text does not affect its result. The patch checks root/filesystem/separator but has not implemented the requested complete recognised mount-record boundary.

**Required correction:** validate the required mount/parent IDs and device metadata in the accepted record before returning True, rejecting malformed or unrecognised fields. Preserve the valid `23 28 0:22 / /proc rw,relatime - proc proc rw` control and add Q62E. This is malformed supplied-text acceptance; native mountinfo corruption was not exercised.

### F4 — MINOR — conflicting duplicate NSpid fields are ignored

Location: `:589–595`. With initial PID namespace and the valid unrestricted proc mount above, Q62F supplies:

```text
NSpid:\t77
NSpid:\t77 88
```

Here `\t` means a tab. The function returns **True** because `next(...)` selects the first field and never sees the conflicting multi-PID field.

**Required correction:** require exactly one recognised NSpid field and refuse duplicate/ambiguous status evidence before deciding completeness. Test both orders and duplicate identical fields. This supplied malformed-status case is not evidence that native `/proc/self/status` normally emits duplicate fields.

### F5 — MINOR — two identities for one snapshot PID can suppress an external child

Location: `:660–669`. Q62B uses `own={(99,2)}`, duration 5 seconds, `hz=100`, threshold 25, and a complete-view assertion. At t0 the sole row is `(99,2):(1,0,"old_campaign",None)`. At t1:

```python
{
  (99,2): (1,0,"old_campaign",None),
  (99,50): (1,0,"new_parent",None),
  (40,51): (99,500,"external_child",None),
}
```

`busy_processes` returns **[]**. The snapshot asserts two mutually incompatible identities for PID 99. Merely finding the old own key makes the child's parent look owned, despite the competing reused identity. The repair rejects duplicate PIDs in `own` but not in snapshots.

**Required correction:** require each supplied snapshot to contain at most one identity per PID, or otherwise refuse any exemption whose parent identity is ambiguous. Return no reading for Q62B; retain Q62A's valid forward-reuse case, which correctly reports the child. The inspected normal `cpu_ticks` reader naturally emits one key per listed PID; this is a malformed supplied-snapshot boundary defect, not a claimed native duplicate snapshot or full-preflight bypass.

New findings: **BLOCKING 0 · MAJOR 0 · MINOR 5 · NOTE 0**. Each is a bounded correction to the repaired evidence boundaries; no unrestricted seam-hardening requirement is inferred.

## Executed evidence and reproduction

`code/run_selected62.py` ran **87 unchanged selected tests: PASS, 0 failures, 0 errors, 0 skips**, against the byte-equal copy. It excluded native Linux process lifecycle/zombie/detached-child, native boot, candidate-constant read, live assessment/CPU/launcher/preflight, and all platform-pin tests. Attestation preflight tests used a synthetic negative default live-reader mock, with their own nested matching/mismatching observation mocks still exercised. The disposable storage and Git fixture cases were run under the review's TMPDIR. These results do not claim Linux storage/power-loss, host lifecycle, package/pin or namespace-runtime verification.

Seven independent probes were written in `code/probes62.py`; Q62B–F are five new adversarial cases. Their controls/semantic contrasts are explicit: Q62A demonstrates the original valid forward reuse is rejected, aligned clean assessment records are the unchanged selected baseline, the valid single-NSpid/single-proc-mount case passes existing tests, and Q62G demonstrates default supervisor corroboration. New probe outcomes and baseline output are preserved; no full Linux mutant survival/kill count is claimed.

Reproduce from the review's temporary directory:

```sh
TMPDIR=/tmp/cell308-codex-review62/code LX_PLATFORM_DIR=/tmp/cell308-codex-review62/code/base PYTHONDONTWRITEBYTECODE=1 python3 -B -W error::ResourceWarning /tmp/cell308-codex-review62/code/run_selected62.py
LX_PLATFORM_DIR=/tmp/cell308-codex-review62/code/base PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/cell308-codex-review62/code/probes62.py
```

Evidence files:

- `code/input_hashes.json` and `code/final_source_verification.json`: immutable/source/copy bindings, clean exact HEAD, interpreter/platform and 73 static mutation anchor/syntax checks.
- `code/selected_base_result.json` and `code/selected_base.stderr.txt`: exact selected test names and results.
- `code/probes62.py` and `code/probes62_out.json`: independent reproducible inputs and outcomes.

The five adjacent defects must be repaired and reviewed against their resulting immutable revision before upgrading this code verdict. Parent CI evidence for this exact aef revision can resolve native runtime uncertainty, but cannot erase the independently reproduced API outcomes above.
