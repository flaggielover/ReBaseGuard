# Cell-308 brief 61 — independent correctness review of development revision 3

Reviewer: `reviewCLOUD_R1_DELTA2 (fresh independent correctness agent, brief 61)`  
Date: 2026-10-15, Asia/Tokyo  
Reviewed delta: `ff9006ac` → **`d423c7aacc4d1cc15f3c7d77aecb5257a0175392`**  
Checkout: `/Users/suzhe/.codex/worktrees/cell308-review61/ReBaseGuard`  
Copied `lx_platform.py` SHA256: **`6978cba7e10521e00b78428b02c10f6455ab2baa43c90cfa9a4a0b8c8934897c`**

DEV_CODE_R3: NOT_FAIL_CLOSED

This is a code correctness subreview. It neither accepts the amendment nor supplies independent amendment or ledger verdicts. Default whole `preflight()` remains blocked; no whole-preflight PASS was demonstrated. The code verdict concerns the individual evidence-producing APIs required by Q2: valid process snapshots can suppress an unrelated CPU user, malformed identity evidence can return ALIVE/DEAD, malformed assessment records can return CLEAN, and malformed `/proc` evidence can return a complete view.

## Exposure disclosure and limits

Opened only the following repository material, with `NS = level4/closure_proofs/p5y_k5_cell308_research/`:

- `NS/ledger/briefs/61_reviewCLOUD_R1_DELTA2.txt` and `NS/reviews/REVIEW_CLOUD_R1_DELTA_R2.md`.
- `NS/streams/CLOUD_R1_LINUX_DEV/lx_platform.py`, `tests/test_lx_platform.py`, and `tests/run_mutants.py`, in full.
- `NS/streams/CLOUD_R1_LINUX_DEV/lx_inventory.py`, in full, to identify its real memory/preflight call sites.
- Scoped Git diffs of the module and tests from `ff9006ac` to the reviewed HEAD; `git show ff9006ac:<lx_platform path>` solely for a byte comparison of `durable_write`.
- Applicable instruction paths were checked individually, rather than enumerating repository directories. `/Users/suzhe/.codex/AGENTS.md` exists and is empty; no applicable nonempty repository instruction file was found. The system `using-superpowers/SKILL.md` was read; its explicit subagent instruction says to skip that skill.

No prohibited audit, interruption review, exposure disclosure, MB r1 target-run/postexec, or Cell-309 file/branch/record was opened. No candidate source was read or executed by this reviewer. The test module defines a historical-candidate constant reader, but its test was excluded from my executed selection. No science module, cell, drift, certificate, decoy, qualification evaluator, or quarantine guard was executed. No install, persistent system-setting change, Git mutation, or repository write was performed.

All additional scripts, copies, mutants, results, and this review are under `/tmp/cell308-codex-review61/`. Existing selected tests used disposable fixture directories. My base-suite runner sets its TMPDIR to the review's `code/` directory. The mutation runner's unchanged fixture tests used the standard temporary directory and removed their fixtures; no repository output was written.

Final read-only verification observed that another task had advanced the checkout HEAD to validation-control commit `fa70a59155fb685d242004671f1313e8d1c9b720`. I had already read and copied the immutable reviewed d423 source; the repository module still has exactly the reviewed SHA256. I performed no Git mutation. This report remains a review of d423, not a review of that later control commit or future repairs.

**Runtime:** Darwin, Python 3. Native Linux process lifecycle/zombie, initial-PID-namespace, platform/dpkg pin, live host, and full mutation-suite execution are **UNVERIFIED** by this reviewer. Their absence is an environment limitation, not a code defect. The synthetic results below execute platform-independent branches against a byte-equal module copy. They do not assert any native Linux target result.

## Q1 — reviewer-60 dispositions in this subreview's scope

All line references below are relative to `NS/streams/CLOUD_R1_LINUX_DEV/` unless a path is stated.

| Finding | Disposition | Evidence and precise limit |
|---|---|---|
| N1 | RESOLVED for the identified dev paths | `lx_platform.py:895-920` reads and parses the HEAD attestation, rejects extra caller fields, requires strict accepted/reviewed flags, matches the machine, and checks an exact acceptance line in a HEAD review. `:962-981` keeps both lifetime-dependent gates open under default DECIDED. Selected tests at `tests/test_lx_platform.py:758-809,829-845` pass. `decided` and a custom `attestation_check` are explicit injected configuration seams; integration must bind them to accepted decisions. No arbitrary committed README now passes the normal attestation reader. |
| N2 | RESOLVED | `lx_platform.py:312-319` allows only Discharging or the three known not-discharging statuses. Selected tests `:331-341` refuse Unknown, garbage, lowercase, and NUL-suffixed states. |
| N3 | PARTIALLY RESOLVED / integration condition remains | Strict `is True` at `lx_platform.py:420,433,455,509` closes every truthy non-True example. `:469-499` now reads resource chains, and `:513` records initial cgroup namespace. `:502-506` still documents, rather than enforces, that the boolean comes from a verified attestation; no current normal caller derives an attested True (`lx_inventory.py:76` uses the default False). This is a helper contract, not a demonstrated public-preflight false-PASS: `free_memory_ge_min` is always OPEN_DECISION at `:976`. Bind that derivation in any future campaign wrapper before claiming a code-enforced H6 guarantee. |
| N4 | RESOLVED for the nested-namespace defect, with new P5 | `lx_platform.py:542-546` refuses a noninitial namespace even when NSpid has one entry; `tests/test_lx_platform.py:493-506` covers the original inputs. The malformed/ambiguous mount/status boundary remains incomplete (P5). Native `unshare` reproduction remains UNVERIFIED on Darwin. |
| N5 | PARTIALLY RESOLVED; full runtime UNVERIFIED | X01-X09 are represented in `tests/run_mutants.py:118-137`; source-level anchors and new behavioral tests cover the stated old weaknesses. The committed harness now contains 65 mutants, including N01-N14 at `:138-168` (its opening prose says N01-N12). This reviewer did not run that full harness. New Y01/Y03 survive selected unchanged relevant tests (P6); no full-suite kill count is claimed. |
| N6 | RESOLVED for the preflight gate | `lx_platform.py:977` calls the boot reader's format validation and excludes non-string readings. Selected `tests/test_lx_platform.py:857-861` passes. `identity_state` and `assess` do not use that validation on their record inputs (P2/P3); these are separate boundaries. |
| N7 | PARTIALLY RESOLVED | Exits are reported at `lx_platform.py:608-610`; unreadable still-existing tasks invalidate `cpu_ticks` at `:570-574`; own keys are tuples at `:594-598`. But child exemption still uses only its ppid and an old lower-bound starttime (`:601,609`), so forward PID reuse remains unsafe (P1). The added test at `tests/test_lx_platform.py:471-475` only tests an older child relative to a newer campaign identity. |
| N8 | RESOLVED for the missing-namespace paths | `lx_platform.py:185-189` requires both recorded namespace values to match before ESRCH/starttime/cmdline evidence; selected `tests/test_lx_platform.py:129-136` passes. A valid boot change remains positive evidence. Malformed boot strings separately bypass this at `:179-183` (P2). |
| N11 | PARTIALLY RESOLVED / fixed-list condition remains | Required mapped library families are checked at `lx_platform.py:772-778`; unknown interpreter owner is retained at `:797-815`. `pin_point` at `:818-826` checks all modules of the caller-supplied list but does not bind that list to an immutable accepted list. Caller `pin_point(())` satisfies that helper contract. The frozen list/integration is a condition, not an independently demonstrated normal preflight PASS. Native pin tests are UNVERIFIED on this Mac. |
| N12 | RESOLVED for the requested minimal-record/type repairs, with residual contract NOTE | `lx_platform.py:935-944,983-984` verifies each launch-record field and refuses non-dicts; selected `tests/test_lx_platform.py:873-892` passes. Review 60 allowed the alternative “verify the record's fields”; that alternative is implemented. A fully fabricated record can still pass the individual launch gate (Q13), because `preflight` does not independently call `launched_by_systemd`. The current inventory caller does obtain the live record (`lx_inventory.py:115-116`). Future campaign integration must enforce that provenance; whole-preflight false PASS was not demonstrated. |
| N13 | RESOLVED for the identified test repairs | `tests/test_lx_platform.py:292-296` supplies the journal list; `:556-559` names the apt-dump parser boundary; `:699-707` compares a pin against the recorded kernel. The two host-dependent tests are UNVERIFIED here; source shows the requested semantic changes. |
| C1, code portion | NOT RESOLVED | N7 remains partly unresolved (P1), and native full tests/mutant claims remain UNVERIFIED. Revision 3 should not be cited as a fully verified implementation of an L-* row on this evidence. |
| C2 / N9 / N10 / N14 | OUTSIDE THIS SUBREVIEW | The parent is conducting the independent amendment/records review. No code-only conclusion here resolves those conditions. |

## Q2 — adversarial evidence and actionable new findings

All probe outputs below are from the unchanged copied revision 3 in `code/probes61.py`, recorded in `code/probes61_out.json`. Source line references support each trigger. “Caller boundary” means that the function accepts a supplied record; it does not imply the normal live reader emits such a record.

### P1 — MAJOR — a reused campaign PID exempts the new unrelated process's children

**Location:** `lx_platform.py:598-602,608-610`; test blind spot `tests/test_lx_platform.py:471-475`.

**Valid synthetic inputs (Q01):** at t0 the campaign key is `(99,2)`; at t1 PID 99 is instead `(99,50)`, with zero new CPU ticks, and unrelated child `(40,51)` has ppid 99 and 500 ticks. With `own={(99,2)}`, `dt=5`, `hz=100`, and threshold 25, `busy_processes` returns `[]`. The child's 100% usage should be reported. The old campaign's exit is exempt because its exact old key is own; the new parent is not busy; the new child is exempt because `51 >= 2`. Thus the entire conflict disappears.

**Required correction:** resolve a child's actual parent identity from the relevant snapshot, and exempt it only when that exact `(ppid,parent_starttime)` is verified as own. If the parent identity is missing/reused/ambiguous, report or return no reading. Do not derive ownership from a PID plus a lower-bound timestamp alone. Add a forward-reuse/new-child test, including an idle reused parent and a busy child.

### P2 — MINOR — identity inputs can turn unrecognised evidence into ALIVE or DEAD

**Location:** `lx_platform.py:179-183,199-210`; parser `:133-136`.

**Q02/Q03:** a complete identity with a valid boot and namespaces, matching starttime/cmdline, and supplied `state="?"` returns ALIVE. The same record with supplied `current_boot="garbage"` returns DEAD immediately as a “boot change”. Neither value is recognised evidence. `proc_stat` accepts any first state token.

**Boundary limit:** unmodified `boot_id()` validates live boot text, so Q03 requires malformed supplied/persisted boot evidence. Q02 uses the same accepted stat-dict path as the normal reader, but no native corrupted `/proc` case was exercised. This is not a preflight boot-gate regression; that gate is fixed.

**Required correction:** validate supplied and recorded boot identifiers before comparing them; malformed evidence must yield UNKNOWN. Validate supported task state and stat identity fields before ALIVE/death comparison, retaining UNKNOWN for zombie/dead states and ALIVE for known valid live states. Add malformed-current-boot, malformed-recorded-boot, and unknown-state tests.

### P3 — MINOR — malformed interval records can be classified CLEAN

**Location:** `lx_platform.py:239-285`, especially `:242-255,257-258,265-269,278-283`.

**Q04-Q06:** otherwise clean interval records whose boot IDs are all the identical string `"garbage"` return CLEAN; records with all end clocks set to float NaN return CLEAN; a boolean False used as every suspend-success counter also returns CLEAN. NaN comparisons make each rejection predicate false. Python treats bool as int at the count check. Merely being non-None makes every identical malformed boot identifier acceptable.

**Boundary limit:** `snapshot()`/`clocks()` normally supplies integer clocks and a validated-or-None boot ID. These probes exercise the public assessment's accepted-record boundary; they do not show the native clock reader emitting NaN.

**Required correction:** validate the complete start/end/sample record schema before classification: integer nanosecond clocks excluding bool, nonnegative integer suspend counts excluding bool, and valid boot identifiers. Nonfinite/nonrecognised/missing values must add AMBIGUOUS evidence. Validate intermediate sample channels as well as endpoint differences. Add the three independent tests above.

### P4 — MINOR — invalid CPU arithmetic can produce an empty conflict list

**Location:** `lx_platform.py:592-607`.

**Q07-Q09:** a busy external process returns `[]` when `dt_s` is NaN or threshold is NaN; the same identity with decreasing CPU ticks also returns `[]`. The first predicate accepts NaN (`dt_s <= 0` is false), and the threshold comparison then never fires; negative used ticks are silently treated as nonbusy.

**Boundary limit:** supplied window duration/threshold and snapshot records are public function inputs. No native Linux tick regression was asserted. The function documents malformed/unsafe inputs as no reading but currently validates only own-key shape and view completeness.

**Required correction:** require finite positive duration/hz, finite nonnegative threshold, and recognised nonnegative integer tick counts. If a stable identity's counter decreases, invalidate the interval rather than suppressing the process. Add each case independently so NaN behavior cannot mask counter behavior.

### P5 — MINOR — `/proc` completeness accepts unrecognised or ambiguous mount/status evidence

**Location:** `lx_platform.py:547-556`; tests `tests/test_lx_platform.py:493-506`.

**Q10-Q12/Q14:** with the initial PID namespace, an empty NSpid field, a single `garbage` NSpid token, or a `/proc` mount row whose filesystem is tmpfs returns True. Two `/proc` rows, the first unrestricted and a later row with hidepid=2, also return True: the loop returns on the first matching mountpoint, never considering later conflicting evidence.

**Boundary limit:** status/mount text is supplied synthetically. Native overmount topology reproduction is UNVERIFIED; the exact accepted-text behavior is confirmed. This is distinct from N4's fixed nested-namespace test.

**Required correction:** require exactly one valid positive integer NSpid token and parse a complete mountinfo record with recognised proc filesystem/root. Resolve which mount actually provides the view; conservatively reject multiple/ambiguous `/proc` mount candidates or any restrictive candidate instead of taking the first. Add malformed-token/filesystem and duplicate-mount cases.

### P6 — NOTE — two new semantic weakenings survive the unchanged relevant tests

**Location:** `tests/test_lx_platform.py:361-449` (host cap); `:228-290` (sample order).

Y01 and Y03 below survive all unchanged synthetic tests relevant to their modified functions. Both are behaviorally inequivalent. This is a confirmed gap in the selected test coverage; **full Linux suite survival is UNVERIFIED**, so this finding does not claim an additional full-harness survivor count.

**Required correction:** add a MemTotal-smaller-than-every-cgroup-limit case and an out-of-order sample case, add these independent mutants to the harness, and verify against a passing unmutated Linux baseline. Attribute kills to relevant behavioral assertions, not to unrelated host failures.

## Public paths and caller contracts

- **Host root:** `memory_readings(root_attested=True)` can produce numbers because True is its documented verified-attestation-derived input. The API itself does not prove that derivation. The only inspected normal caller uses False, and no preflight gate consumes the number. Report this as the N3 integration condition, not an observed normal gate PASS.
- **Launch:** Q13 forges every requested field without any live supervisor observation; `launch_record_ok` returns True and normal `preflight` assigns `launched_by_systemd=PASS`, while the whole preflight remains false. This satisfies the original field-validation alternative but still requires a trusted wrapper/live record. It should not be described as independent systemd verification by `preflight`.
- **Pin point:** its module list is a caller argument and its return is a reading, not a PASS gate. Required mapped members are enforced, but an accepted immutable science import list must be configured by the future wrapper. Calling `pin_point(())` is not proof that science imports were frozen.
- **Decisions/test seams:** a supplied `decided` set and custom attestation checker can open lifetime gates; they are explicit injected configuration, and default DECIDED remains empty. They must not become user assertions in an operational wrapper.

These distinctions avoid treating every documented helper/test seam as a newly discovered production bypass. P1 instead uses valid snapshots and an otherwise legitimate own record; it is wrong even under its stated caller contract.

## Q3 — regressions and deliberate stricter choices

- `durable_write`'s entire section is byte-identical to `ff9006ac`. All six unchanged synthetic durable-write tests pass against the copy, including stale tmp, no-follow symlink, fsync ordering, read-back corruption, and crash stages. This establishes no power-loss/host-reclaim durability guarantee; native Linux storage behavior is UNVERIFIED.
- Zombie/dead state Z/X still returns UNKNOWN, and the known live states remain ALIVE in selected identity tests. Native multithreaded zombie leader reproduction is UNVERIFIED here.
- The original R01-R10 weakenings remain represented in the committed harness with reanchored source substitutions; fresh native R01-R10 kill claims are UNVERIFIED by this reviewer.
- Requiring the initial PID namespace deliberately refuses a legitimate container's partial host view. That strict choice is documented. The live `TestBusy.test_live_snapshot` nevertheless unconditionally expects a list (`:516-521`) and thus assumes an initial, complete host view; running that assertion in a nested namespace can fail the baseline without exposing a fail-open code path. Such a baseline failure must not be counted as killing mutants.
- Unknown interpreter package ownership deliberately prevents pin matching; a non-dpkg-managed interpreter is therefore unsupported by a complete pin. The live pin comparison tests require a host on which those readings are available. Mac `/proc`, glibc, CLOCK_BOOTTIME, and dpkg limitations are not rev3 defects.
- Raw `cgroup_resources` output intentionally changed from a single v2 row to leaf-to-root rows. The inspected inventory records the object directly; its relevant call sites were updated to the new preflight attestation-reference signature. No campaign/scientific consumer was read or run.
- `host_lifetime_attested`/provider update gates now deliberately stay OPEN_DECISION; no default full preflight can pass, but this does not establish the individual evidence APIs' correctness.

## Executed tests, new mutants, and reproducibility

`code/run_selected_base61.py` ran **59 unchanged selected tests, all OK**, against `code/base/lx_platform.py`, with bytecode disabled. This excludes the native Linux lifecycle tests, native boot test, candidate-constant test, live assessment, live CPU snapshot, live launcher, all platform-pin tests, and live preflight. No full native suite was run.

`code/new_mutants61.py --run-selected` created three new mutants in `code/mutants/Y01`, `Y02`, `Y03`, ran all **nine** unchanged TestMemory tests for Y01/Y02 and the eight selected unchanged synthetic TestAssess tests for Y03. `code/mutant_semantics61.py` separately proved each changed a defined outcome.

| Mutant | Source diff | Selected result | Independent semantic contrast | Full Linux suite |
|---|---|---|---|---|
| Y01 | `:438`: remove MemTotal from effective-limit minimum | SURVIVED_SELECTED_TESTS (9 TestMemory tests) | MemTotal=1000, limited cgroup=3000: base 1000 → mutant 3000 | UNVERIFIED |
| Y02 | `:466`: `min(hs)` → `max(hs)` | KILLED_BY_SELECTED_TESTS (`test_v2_root_and_memory_high`) | headrooms 10 and 7980: base 10 → mutant 7980 | UNVERIFIED |
| Y03 | `:280`: remove negative sample-step test | SURVIVED_SELECTED_TESTS (8 TestAssess tests) | interval 0→120s with sample at 150s: base AMBIGUOUS → mutant CLEAN | UNVERIFIED |

Exact new diffs, also saved separately beside each mutant:

```diff
--- base/lx_platform.py
+++ Y01/lx_platform.py
@@ -435,7 +435,7 @@
     vals = _chain_values(chain_rec, root_attested=True)
     if vals is None:
         return None
-    return min([mem["MemTotal"], *[v for v in vals[0] if isinstance(v, int)]])
+    return min([v for v in vals[0] if isinstance(v, int)], default=mem["MemTotal"])

--- base/lx_platform.py
+++ Y02/lx_platform.py
@@ -463,7 +463,7 @@
             if not isinstance(use, int):
                 return None
             hs.append(lim - use)
-    return min(hs) if hs else None
+    return max(hs) if hs else None

--- base/lx_platform.py
+++ Y03/lx_platform.py
@@ -277,7 +277,7 @@
     try:
         ts = [x["clocks"]["monotonic_ns"] for x in seq]
         steps = [b - a for a, b in zip(ts, ts[1:])]
-        if any(d < 0 for d in steps):
+        if False:
             reasons.append("AMBIGUOUS: samples out of order")
```

Primary evidence files:

- `code/probes61.py` / `code/probes61_out.json` — unchanged-base adversarial probes.
- `code/run_selected_base61.py` / `code/selected_base.stderr.txt` / `code/selected_base_result.json` — 59-test baseline.
- `code/new_mutants61.py` / `code/new_mutants61_result.json` — mutation creation and selected results; per-mutant stdout/stderr and exact diff preserved.
- `code/mutant_semantics61.py` / `code/mutant_semantics61_out.json` — inequivalence checks.

Counts of new findings: **BLOCKING 0 · MAJOR 1 · MINOR 4 · NOTE 1**. Q4/Q5 amendment/records conclusions and native Linux runtime remain outside this independent code subreview; where not exercised, they are explicitly UNVERIFIED.
