# Independent static review of the r4 real point executor (verbatim)

EXECUTOR_STATIC_REVIEW: FAIL

N1 = CLOSED
N2 = CLOSED
N3 = CLOSED
D1 = CLOSED
D2 = CLOSED
D3 = CLOSED
D4 = CLOSED

ACCEPTED_R3_SEMANTICS_UNCHANGED = YES
PREDECESSOR_ARTIFACTS_PRESERVED = YES

**The one blocking item** is a new load-bearing defect, X1, which r4 exposes by making the governed path reachable. The supervisor does not tie the launch slot to the slot the frozen verifier approved. N1–N3 and D1–D4 are closed. The fix is small and is a consistency check against accidents, not an on-host anti-tamper measure (see §5).

---

# Independent static review of the r4 real point executor

## Scope and method

- **What I did.** A read-only review in `/Users/suzhe/ReBaseGuard-k5r` at HEAD `d64bcd10`. I modified no file and ran nothing on any host. I did not import or call the executor or the verifier. I used only git, sha256 and `json` parsing.
- **Authority.** The frozen protocol files: `SCIENCE_PREREGISTRATION_R4.json`, `AUTHORIZATION_TEMPLATE_R4.json`, `prelaunch_verify.py` and `probe_rules.py`.

I recomputed the following myself rather than taking them from the evidence:

- **Commit chain.**
  - `b0e3f6c6` (15:49 +0900) adds only `EXECUTOR_SPEC_R4.md`.
  - `77afd942` (17:51) touches only the 14 files in the executor namespace.
  - `d64bcd10` (18:39) adds only the 20 files under `evidence/qualification_r4/`.
  - `git diff --name-only 34bb9b0b d64bcd10` touches nothing outside `p5y_k5_cusum_real_point_executor/`.
  - The spec was therefore committed before the repair code.
- **Executor identity.**
  - Over the 11 `IDENTITY_FILES` it is `47f3557b…b8d2`. This equals `EXECUTOR_QUALIFICATION_PROTOCOL.json` (status FROZEN_PRE_QUALIFICATION), the r4 result and `RUN_PROVENANCE.json`.
  - All 279 `EXECUTOR_PINS.json` entries match at HEAD. The verifier is pinned at `54b198bc…`, equal to `packet_code_sha256`.
  - `REAL_INPUT_GUARD.json` is DENY and stays outside the identity and the pins.
- **Evidence hashes.**
  - All 16 `part_sha256` values match their files.
  - `sha256(QUALIFICATION_RESULT_EXECUTOR.json) = d8982c74…185e`. This equals both `RUN_COMPLETE.result_sha256` and `RUN_PROVENANCE.qualification_result_sha256`.
  - The protocol sha is `1a62e5d1…`. The pins sha is `be558082…`, which equals the provenance value.
  - All 25 `qualification_sources_sha256` entries match both the `77afd942` blobs and the working tree. Before-run and after-run porcelain were both empty. `git_commit` and `git_commit_at_end` are both `77afd942`.
- **Gates.**
  - EG01–EG22 are all PASS, with 0 runner failures.
  - The governed rows pass 17/17 and N01–N05 are detected 5/5.
  - D2 passes 36/36 rows, with L01–L04 and V01 detected.
  - D3 passes, with R01–R02 detected.
- **Science file.**
  - `sha256(SCIENCE_PREREGISTRATION_R4.json) = 9ace6896d70b…3780a`, with one commit only (`852b2d65`).
  - Since `852b2d65`, the protocol's `protocol/` and `code/` changed only through `FREEZE_RECORD_R4.json` (`cf09d6fc`), which P03 requires.

## 1. N1: one authoritative pre-arithmetic decision, taken before slot-N exists (CLOSED)

**Order of operations** (`code/supervisor.py:113-137`):

1. `SLOT_EXISTS` is refused (117-118).
2. For `mode in GOVERNED`, `governed_prelaunch` runs (120-126).
3. Only afterwards come `slot.parent.mkdir`, `slot.mkdir()` (127-128) and `LC.write_new(slot, RUN_STATE, state)` (137).

The static test `tests/test_executor.py` (`test_r4_single_verifier_call_site`) asserts that `governed_prelaunch(` comes before `slot.mkdir()` in `supervise`.

**The decision itself:**
- `governed_prelaunch` (`supervisor.py:96-110`) checks, in order:
  1. that the slot parent is the preregistered `output_namespace`;
  2. that the guard policy is EXTERNAL_AUTHORIZATION (otherwise it returns without verifying);
  3. then `AI.prelaunch_decision(ctx)`, the only production call site.
- `prelaunch_decision` → `validate` → `validate_with(ctx, PV, COUNTERSIGNATURE_FILE)` (`authorization_interface.py:226-282`). This keeps the accepted r3 path unchanged:
  - `verifier_source_problems`: path, bytes against `packet_code_sha256` and the pins, and the `verify` code object;
  - `run_verifier(module.verify, module.AUTH_ACTIVE)`, which uses the defaults and consumes the returned object;
  - `decide_from_report` (P01–P12 all pass, HEAD and authorization bytes before and after), then `binding_problems`, then `countersignature_problems`.

**Why P11 now passes** (`prelaunch_verify.py:454-502`):
- With slot-N absent, P11 requires exactly one LAUNCH_NOTICE, and nothing else, for `slot_dir(len(entries)+1)`.
- It also requires `(root/slot).exists()` to be false.
- Both hold before the `mkdir`, so the verifier's own rules now admit the launch. This is the root cause of N1, and it is removed.

**A refusal or exception leaves nothing behind:**
- REFUSED returns `PRELAUNCH_REFUSED` with `slot_created: slot.exists()` and no RUN_STATE (`supervisor.py:122-125`).
- Any verifier exception is converted to a refusal by `run_verifier` (`authorization_interface.py:102-107`).
- Any other exception inside `validate_with` or the adapter propagates out of `supervise` before line 127.
- In every case there is no slot, no RUN_STATE, no VOID, no ATTEMPT_LOG and no address.

**Genuine frozen-verifier output** (`part_governed.json`):
- `verifier_exception_creates_no_slot`: the unmodified verifier raised FileNotFoundError before `AUTHORIZATION_ACTIVE.json` existed. The row requires `not ns_root.exists()`.
- `verifier_refused_creates_no_slot`: authorized, but with no LAUNCH_NOTICE, it returned `verdict 'REFUSED'`.
- `permitted_synthetic_end_to_end`:
  - RUN_STATE carries `prelaunch_report` with verdict LAUNCH_PERMITTED, 12 checks all passing and `failing_checks == []`;
  - the events are `[VALIDATED, ARITHMETIC_STARTED, SEALED]`;
  - the terminal marker is RUN_COMPLETE;
  - the file set is exact.

**The decision is bound into RUN_STATE:**
- `lifecycle.build_run_state` (`lifecycle.py:148-156`) stores `prelaunch_decision` and `prelaunch_decision_sha256 = sha(canonical(decision))`. `STATE_KEYS` gains exactly these two keys (`lifecycle.py:34-35`).
- The decision record (`authorization_interface.py:270-282`) holds:
  - the verdict and the full report with its digest;
  - the authorization path and bytes sha, the amendment sha and the countersignature sha;
  - HEAD, the verification time, the protocol sha, the executor identity and the executor binding;
  - the slot, the namespace, and the attempt: K1 record sha, kind, right endpoint, m set, point, cell and precision.
- The positive row recomputes the digest from the stored decision and finds it equal.

## 2. N2: the full verifier is unreachable from the child and backend, and a post-start call is never VOID (CLOSED)

**Static reachability:**
- `executor_core.decide` (80-98) now calls only `AI.bound_decision_problems(ctx)`.
- `grep` finds no `validate(`, `validate_with(`, `run_verifier(`, `prelaunch_decision(` or `PV.verify(` in `executor_core.py`, `backends.py`, `executor_cli.py` or `input_adapters.py`.
- The only remaining `prelaunch_verify` uses in the child are `PV.live_host_facts()` (`executor_core.py:239-240`, the runtime contract) and `PV.AUTH_ACTIVE` as a path (`authorization_interface.py:340-343`). Neither runs `verify`.
- The AST fence is `test_r4_single_verifier_call_site` plus the `static_single_verifier_call_site` qualification row, which counts `AI.prelaunch_decision(ctx)` in `supervisor.py` exactly once.

**The re-check is pure:**
- `bound_decision_problems` (`authorization_interface.py:294-337`) reads only:
  - the slot and RUN_STATE;
  - `/proc/<ppid>/cmdline`;
  - the authorization file bytes;
  - the executor identity file bytes.
- It compares these against the decision. It runs no git, no network, no ledger read, creates no slot and issues no verdict.
- `CusumPointBackend.prepare_point`'s defence-in-depth `EC.enforce_guard(self, ctx)` (`backends.py:383-384`) therefore reaches only this pure function.

**Runtime fence:**
- `_mark_arithmetic_started()` is latched immediately before `log.emit("ARITHMETIC_STARTED")` (`executor_core.py:413-414`).
- `validate_with` raises `PostStartVerifierCall` as its first statement (`authorization_interface.py:237-238`), before any operator-material or verifier code. It is a `BaseException`, so the `except Exception` inside `run_verifier` cannot swallow it.
- `void_class` returns None for it (`executor_core.py:476-477`), so `execute` seals no VOID (`executor_core.py:458`).
- `test_r4_fence_first_in_validate_with` pins its position.
- **Caveat on the qualification row.** `post_start_full_verifier_unreachable` checks the fence and `void_class` directly. Its `decide(...)` "pure after start" half uses a ctx without `attempt_uid`, so it exercises only the early-return branch. See X6.

**The r3 N2 mechanism is gone.** `prepare_point` can no longer reach P11, `git ls-remote` or any other network or ledger read, so a transient publication-read failure can no longer turn into a permanent VOID.

**Residual behaviours** (not load-bearing): X3 and X4 below.

## 3. N3: real mode needs a supervised slot and a matching RUN_STATE (CLOSED)

**Two independent layers refuse an unsupervised launch:**
- *Guard first.* `execute` calls `enforce_guard` before anything else (`executor_core.py:396`).
  - `enforce_guard` requires permission for `real_input` or `governed` backends (125-130).
  - Under DENY, `decide` denies.
  - Under EXTERNAL_AUTHORIZATION, `bound_decision_problems` refuses on each of these:
    - a missing `attempt_uid` or decision digest;
    - a missing slot or a symlinked slot;
    - a missing or malformed RUN_STATE (`set(state) != STATE_KEYS`);
    - a different `attempt_uid`;
    - `state.pid != getppid()` or `state.argv != /proc/<ppid>/cmdline`;
    - a digest mismatch against RUN_STATE or against `--decision-sha256`;
    - a verdict other than LAUNCH_PERMITTED;
    - changed authorization bytes;
    - a different executor identity, protocol, binding, slot, namespace or attempt parameters.
- *Slot admission second.* `slot_admission(..., require_supervisor=True)` (`executor_core.py:243-268`) refuses a missing slot (`SUPERVISOR_REQUIRED`), an empty slot, or a RUN_STATE belonging to another attempt or pid.

**CLI.** `executor_cli.py:72-81` passes `--decision-sha256` into the context. Without it the guard refuses with "not a supervised governed attempt".

**Evidence:**
- `unsupervised_real_mode_refused` and `unsupervised_governed_mode_refused` are refused by the guard with "no supervised slot", and the slot is not created.
- The negatives for a changed digest, attempt_uid, missing RUN_STATE, stale RUN_STATE, wrong pid and wrong argv are each refused by `UNAUTHORIZED_REAL_ARITHMETIC` for their stated reason, with no ARITHMETIC_STARTED and no seal. The recorded error strings match these reasons.

**Accepted limitation.** `child_coherent_binding_runs` shows that a hand-written RUN_STATE carrying a copied decision, written by the process that launches the child, is accepted. The re-check is a consistency check, not an authenticator. This is the accepted host-trust limitation (§6). A slot created this way has no ledger OUTCOME, so the frozen P11/P09 would refuse every later launch, and adjudication would see it.

## 4. End-to-end test (`code/qualify_governed.py`, `part_governed.json`)

**The permitted path uses the unmodified frozen verifier:**
- The synthetic clone S is checked out at the host HEAD (`77afd942` in the frozen run). Only the executor namespace is rsynced from the (clean) working tree (`:84-89`), so the protocol namespace and `prelaunch_verify.py` are the frozen blobs.
- `verifier_source_problems` (path, bytes against `packet_code_sha256` and pins, code object) and the verifier's own P03 (packet code byte-equal to the freeze blobs) both passed. The verifier ran with its defaults.
- The governance commits are made in the preregistered order:
  1. review;
  2. amendment (then published);
  3. authorization, with `sleep(1.1)` for strict ordering;
  4. countersignature (published);
  5. LAUNCH_NOTICE (published).
- The run goes: supervisor → verifier PASS (P01–P12) → slot → RUN_STATE → child pure re-check → manufactured arithmetic → seal → RUN_COMPLETE → `LC.outcome_entry` / `LC.reconcile` == [].

**The two test doubles are honest, minimal and disclosed** (module docstring, spec R4-4, DEV_CALIBRATION):
- *(a) git shim* (`:46-57`). It rewrites only the argument following `ls-remote` when that argument is `origin`, and execs `/usr/bin/git` for everything else.
  - `git remote get-url origin` still returns the allow-listed GitHub URL.
  - Publication is simulated by pushing to a local bare repository and updating the local remote-tracking ref (`:118-123`), which is what a real push and fetch would do.
  - This remote-tracking update is not listed as a separate double, but it is the natural effect of the simulated push.
- *(b) mount namespace.* `unshare --mount --propagation private` with an overlay over `/root/work` (`:387-390, 409-410`).
  - The driver refuses to run if `/root/work/k5-first-real-probe` exists on the host.
  - The part reports `real_namespace_untouched: true`.
  - The overlay hides nothing the verifier needs, because the namespace does not exist on the host. It only prevents the namespace from being created.

**Synthetic commits cannot leak:**
- They exist only in S under `/var/tmp/k5gov`, removed in `finally`.
- The only push is `push --force <local bare path>` (`:121`).
- The source repository lives under the overlay, so any write to it lands in the discarded upper layer.
- No code path pushes to `origin`.
- Residual: S's origin URL is set to the real GitHub URL (`:122`). A future edit adding `push origin` would reach GitHub. This is not load-bearing today.

**The negatives are load-bearing:**
- `refused_by_guard` requires exit code 3, `UNAUTHORIZED_REAL_ARITHMETIC`, the specific reason string, and no ARITHMETIC_STARTED or seal (`:298-305`).
- The negatives run before the coherent crafted run, so FINALIZED_ADDRESS_EXISTS cannot stand in for them. This fixes the vacuity recorded in DEV finding 1.
- The recorded errors show the intended reasons.
- `verifier_refused_creates_no_slot` checks only "verifier verdict", not which P-check failed. The next step (adding only the LAUNCH_NOTICE yields PASS) shows it was P11.

**Mutants.** Each mutant is built into its own S whose amendment binds the mutant bytes, so detection comes from behaviour. A crash counts as not detected, and a clean control is required.

| Mutant | Detected? | How |
|---|---|---|
| N01 (slot before verification) | Yes, behaviourally | P11 refuses because of the pre-created slot, so there is no permitted decision; rows 1–2 also fail on `slot1.exists()`. |
| N02 (child runs the full verifier) | Yes, behaviourally | The child's verify hits the r3 N1 P11 refusal and the negatives lose their stated reasons. This reproduces the r3 defect exactly. |
| N03 (missing slot admitted) | Only by the unit row `slot_admission_requires_supervisor` | End to end, the guard independently refuses "no supervised slot" (defence in depth). |
| N04 (digest check off) | Yes, behaviourally | The digest-changed child runs and seals. |
| N05 (fence removed) | Yes | Detected by the in-driver fence row. |

The evidence lists only the first 6 failing rows alphabetically, so the N01/N02 records do not show the positive-row reason. See X6.

## 5. D2 / D3 / D4 regressions and the D2 adaptation

**Regression evidence:**
- D2 passes 36/36 rows, with L01–L04 and V01 detected.
- D3 passes 33/33 rows, with R01–R02 detected.
- EG21 (D4 provenance) passes, and I recomputed its hashes (see Scope).

**The RUN_STATE change is additive.** Two keys are null for the non-governed modes. `write_new`, the terminal markers, `classify`, `recovery_action`, `outcome_entry` and `reconcile` are unchanged. **D2, D3 and D4 remain CLOSED.**

**The adaptation** (`qualify_d1d4.py:322-326, 358-369`):
- The post-slot, pre-arithmetic refusal is now a second manufactured attempt of an already sealed fixture. It is refused with FINALIZED_ADDRESS_EXISTS and yields RUN_FAILED with INTEGRITY_REFUSAL, `arithmetic_started` false, exactly `[RUN_FAILED, RUN_STATE]`, and ledger reconciliation.
- This exercises the same `finish()` refusal path (exit 3 plus an `EXECUTOR_REFUSAL:` line) that the r3 case exercised, so the lifecycle contract is still covered faithfully.
- **Defect in the adaptation (X2).** The new row `real_launch_prelaunch_refused_no_slot` was refused because the slot is outside the preregistered namespace (recorded problem: `slot outside the preregistered output namespace`), not because of DENY.
  - DEV_CALIBRATION item 3 describes it as a DENY refusal.
  - The supervisor's DENY short-circuit (`supervisor.py:104-106`) is exercised by no row.
  - This is not load-bearing: DENY is enforced independently by the child guard (the EG03 refusals rows) and by the verifier.

**Ruling on retry_policy.attempt_start** ("A refusal before it … still consumes a launch slot (max_slots) and requires a new LAUNCH_NOTICE and a permitted prelaunch verification before relaunch"):
- That sentence defines when an *arithmetic attempt* starts. It governs refusals inside a launch, where "relaunch" requires "a permitted prelaunch verification". So a failed prelaunch verification is a precondition failure, not a launch.
- The frozen P11 admits exactly this reading. A ledger slot absent from the namespace is allowed only as the next slot, and a slot directory requires a LAUNCH_NOTICE, an OUTCOME and RUN_FAILED. Creating slot-N before or at verification is what reproduced N1.
- r4 is consistent with this:
  - a pre-slot PRELAUNCH_REFUSED consumes no slot and reuses the same committed LAUNCH_NOTICE;
  - a refusal after the slot exists (child guard, FINALIZED_ADDRESS_EXISTS, context refusal) writes RUN_FAILED with `arithmetic_started` false, consumes the slot, and requires an OUTCOME plus a new notice.
- There is a literal-wording tension only if "refusal before ARITHMETIC_STARTED" is read to include verifier REFUSED. It is **not load-bearing**: no arithmetic runs, nothing is sealed, the next launch still needs a PASS, and the ledger contract holds.
- Residual: a pre-slot refusal leaves no host or ledger trace. The operator procedure should record refused prelaunch attempts (a documentation matter).

## 6. Accepted r3 semantics and predecessors

**Mathematics unchanged:**
- `git diff 2b9fdf8d 77afd942` is empty for `backends.py`, `input_adapters.py`, `consumer.py`, `qualification_gates.py`, `paths.py`, `smoke.py` and `exec_fixtures.py`.
- In `executor_core.py`, the changes touch only:
  - the guard (`decide`, `bound_decision`, the latch, `enforce_guard`);
  - `standard_context`, `amendment_binding` and `guard_policy`;
  - `slot_admission`;
  - the latch call;
  - `void_class`;
  - a governed HARNESS_ANALOGUE branch in `producer_gates` for Q01/Q14/Q16, which is not taken for `real_input`.
- The enclosure, M5, transport, serialization, addresses, Q-gate mathematics, CRAMER contract and certificate replay are untouched.
- The replay payload is `cb28b972…e7e0` twice, with 0 scientific leaf differences, identical in r2, r3 and r4.

**Predecessors unchanged:**
- `git diff b2930bb2 d64bcd10` over `evidence/qualification`, `qualification_r2` and `qualification_r3` is empty.
- `git diff 34bb9b0b d64bcd10` over `review/`, `RESULT.md`, `RESULT_R3.md`, `EXECUTOR_SPEC.md`, `EXECUTOR_SPEC_R2.md` and `EXECUTOR_SPEC_R3.md` is empty.
- The science preregistration bytes are unchanged, sha256 `9ace6896…`.

## 7. New defects, ranked

**X1. MEDIUM, LOAD-BEARING. The launch slot is not bound to the slot the verifier approved.**

*The mismatch:*
- P11 approves launching only `slot_dir(len(entries)+1)` and checks the LAUNCH_NOTICE only for that slot (`prelaunch_verify.py:490-500`).
- `supervise` launches the CLI's `--slot N` (`supervisor.py:284`).
- `governed_prelaunch` checks only the namespace (`:102`).
- The only slot binding is the countersignature's `attempt_slot` (`authorization_interface.py:209-216`). The countersignature never reads the ledger, and the verifier never reads the countersignature.

*Example:*
1. The namespace is empty and the ledger has a LAUNCH_NOTICE for slot-1.
2. The countersignature names slot 2 and the operator runs `--slot 2`.
3. The verifier PASSes on "next slot slot-1", and slot-2 is created.
4. The child re-check passes (the decision's slot is slot-2), and real arithmetic runs in a slot with no LAUNCH_NOTICE. This violates `retry_policy.slots_and_ledger`.
5. The sealed record becomes final (P09), and P11 then refuses forever (the namespace is not contiguous).

*Why it is in scope:* it takes two consistent human errors in external inputs, but preventing exactly such accidents is the executor's stated purpose. r3 could not reach this state because N1 blocked every launch; r4 exposes it.

*Fix:* in `governed_prelaunch`, before verifying, refuse unless `slot.name == PR.slot_dir(<number of existing slot-* dirs> + 1)` and the committed ledger holds exactly one LAUNCH_NOTICE naming `slot.name` with this authorization's sha. Both are pure reads in the supervisor. Add a qualification negative (countersignature and CLI naming slot 2, ledger naming slot 1: expect PRELAUNCH_REFUSED, no slot).

**X2. LOW, not load-bearing.** Covered in §5: `real_launch_prelaunch_refused_no_slot` is refused by the namespace check, not by DENY. The supervisor's DENY branch is unexercised, and DEV_CALIBRATION item 3 misdescribes the row.

**X3. LOW, not load-bearing.** A `PostStartVerifierCall` exits with code 4 and an `EXECUTOR_REFUSAL:` line (`executor_cli.py:91-96`).
- `finish` then derives INTEGRITY_REFUSAL with `arithmetic_started` true and **no** VOID (`supervisor.py:182-190`; `probe_rules.failure_class`).
- This literally conflicts with `void_after_arithmetic`, which says INTEGRITY_REFUSAL after arithmetic means VOID.
- It fails closed: P11 treats the class as non-transient.
- The static fence and the runtime fence make it unreachable in the frozen code.

**X4. LOW, not load-bearing.** `prepare_point`'s re-check runs after ARITHMETIC_STARTED (`executor_core.py:413-415` → `backends.py:384`). EXECUTOR_SPEC_R4 R4-2 says a mismatch "fails closed before arithmetic"; in fact a mismatch there seals VOID with INTEGRITY_REFUSAL.
- For genuine integrity drift (changed authorization or executor bytes within milliseconds), this is the frozen behaviour.
- The re-check also compares ppid and argv. If the supervisor were killed in that millisecond window, the result would be VOID rather than a transient class. This is theoretical.

**X5. LOW, documentation.** Several texts still describe the r3 design, where the child called the verifier:
- `TRUST_MODEL.md:55` ("The executor then calls the frozen verifier itself");
- `authorization_interface.py:9-14`;
- `executor_core.py:12-14`;
- the `rule` text in `REAL_INPUT_GUARD.json`.

**X6. LOW, evidence granularity.**
- The governed mutant records keep `failing[:6]` in alphabetical order, so the N01/N02 records do not show the positive-row reason.
- N03 is detected only by a unit row.
- The `decide` half of the post-start row uses an incomplete ctx.
- `verifier_refused_creates_no_slot` does not name the failing P-check.

**X7. LOW, not load-bearing.** The child re-check does not re-read HEAD, although the obligation is "for the same HEAD". The authorization bytes, executor identity, protocol and K1 binding are all re-hashed, so HEAD drift alone cannot change what runs.

**X8. LOW, not load-bearing (operator-error class).** `governed_manufactured` is a production supervisor/CLI mode that must run in the preregistered namespace.
- Under a live activation, `--mode governed_manufactured` would pass the verifier and spend the authorized slot on a MANUFACTURED record ending in RUN_COMPLETE.
- The frozen P11 would then block the campaign, because it expects RUN_FAILED.
- This is the same class as the pre-existing `manufactured` mode pointed at the namespace. TRUST_MODEL should forbid non-`real` modes on the execution host after activation.

## 8. Scope limitations accepted

- **The host is not a trust root.** The execution host is not an independent trust root. The supervisor, the RUN_STATE decision binding and the child re-check are consistency and fail-closed mechanisms against accidents. An on-host operator can forge a coherent RUN_STATE (shown by `child_coherent_binding_runs`) or bypass the guard. This belongs to external authorization, the published ledger and independent adjudication. I recommend no further on-host anti-tamper work.
- **Publication read.** The positive path's publication read is simulated by a local bare repository. The real `git ls-remote` against GitHub has not been exercised end to end. This is accepted: it is a frozen-verifier behaviour, and the verifier is unmodified.
- **Manufactured input only.** The end-to-end positive path uses manufactured input (`governed_manufactured`), so `CusumPointBackend.prepare_point`'s pure re-check, the real-mode `authorization_still_bound` re-hash and the real Q01/Q14 gates are covered statically and by unit rows, not by a governed real run. This is accepted, because no real arithmetic may run before authorization.
- **Real input remains denied.** REAL_INPUT_ARITHMETIC_GUARD = DENY and EXECUTION_AUTHORIZED = false throughout. No real K1 cell was executed and no real R''' was formed.
