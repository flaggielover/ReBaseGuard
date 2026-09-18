# Independent static review of the r3 real point executor (verbatim)

EXECUTOR_STATIC_REVIEW: FAIL

D1 = OPEN
D2 = CLOSED
D3 = CLOSED
D4 = CLOSED

ACCEPTED_R2_SEMANTICS_UNCHANGED = YES
R2_ARTIFACTS_PRESERVED = YES

# Independent static review of the r3 real point executor

## Scope and method

This was a read-only review in `/Users/suzhe/ReBaseGuard-k5r` at HEAD `b2930bb2`. I modified no file, ran nothing on any host, ran no certifier or operator, and did not import or call the executor or the verifier. I used git, sha256 and `json` parsing only. The frozen protocol files (`SCIENCE_PREREGISTRATION_R4.json`, `AUTHORIZATION_TEMPLATE_R4.json`, `prelaunch_verify.py`, `probe_rules.py`) were the authority.

I recomputed these myself rather than taking them from the evidence:

- **Commit chain.**
  - `b2930bb2` changes only the 19 `evidence/qualification_r3/*.json` files relative to `2b9fdf8d`.
  - `a5d63e71` adds only `EXECUTOR_SPEC_R3.md`, and that file is unchanged at HEAD.
  - The order is b4f1315f → a5d63e71 → 2b9fdf8d → b2930bb2, so the spec was written before the code.
- **Executor identity.** Over the 11 `IDENTITY_FILES` it is `f6ac2676…d1d1`. That equals `EXECUTOR_QUALIFICATION_PROTOCOL.json`, the r3 result and `RUN_PROVENANCE.json`.
- **Pins and sources.** All 278 `EXECUTOR_PINS.json` entries and all 21 `executor_sources_sha256` entries match at HEAD. The verifier is pinned at `54b198bc…`, equal to the preregistration's `packet_code_sha256`. `REAL_INPUT_GUARD.json` is still outside the pins and the identity.
- **Science file.** `sha256(SCIENCE_PREREGISTRATION_R4.json) = 9ace6896…780a`. `git diff 852b2d65 HEAD` over the protocol's `protocol/` and `code/` is empty.
- **r3 evidence hashes.**
  - All 15 `part_sha256` values match their files.
  - `sha256(QUALIFICATION_RESULT_EXECUTOR.json) = d06abeda…7598`, which equals `RUN_COMPLETE.result_sha256` and `RUN_PROVENANCE.qualification_result_sha256`.
  - All 21 EG gates are PASS.
  - Every D1, D2 and D3 row is `true`.
  - Mutations: E 16/16, P 4/4, D+A 7/7, L+V 5/5, R 2/2.
- **Predecessors unchanged.**
  - `git diff 57b51a6f HEAD -- evidence/qualification_r2 evidence/qualification` is empty.
  - `git diff b4f1315f HEAD -- review/ RESULT.md` is empty.
  - `EXECUTOR_SPEC.md`, `EXECUTOR_SPEC_R2.md`, `review/EXECUTOR_STATIC_REVIEW_R1.md` and `evidence/qualification/` are unchanged since `6a1adbfe`.

## Accepted r2 semantics: unchanged (YES)

- **Unchanged mathematical sources.** `git diff 52769488 2b9fdf8d` is empty for `backends.py`, `consumer.py`, `input_adapters.py`, `qualification_gates.py`, `smoke.py`, `exec_fixtures.py`, `paths.py`, `FIXTURE_LIMITS.json` and `REAL_INPUT_GUARD.json`.
- **executor_core.py.** The only changes are in the guard/decision, `slot_admission`, `AttemptLog` (attempt_uid), the authorization re-hash, `void_class`, the Q01/Q16 real branch and `seal()`. The following are byte-identical: `run_stages_before_enclosure`, `validate_stage_outputs`, `enclosure_stages` (`certify_graded(parity=True)`, `local_tower`, `tf = x1²/2`, `L1 = L0 − tf·M5`, `U1 = U0 + tf·M5`), `radius_only_cascade`, `serialize_intermediates`, `check_certificate_chain`, the `PR.transport` equality check, `M_SET = [1,2,3,5]` and `PRECISION = 256`.
- **Qualification protocol.** Only the mutation groups, the supervisor tests and the identity/pin/source hashes changed. Fixtures, `cost_model`, `cpu_ceiling`, the E/P/C mutation groups and `inherited_r4_parts` are identical. Pins changed only for executor files; no R1–R4, certificate or protocol pin changed.
- **Empirical confirmation.**
  - The replay payload is `cb28b972…e7e0` twice, identical to r2.
  - The per-fixture scientific hashes in `part_fixtures.json` equal r2's exactly.
  - Fixture verdicts are equal to r2.
  - The CRAMER contract is `b472beac…` and C01 is detected.
  - Smoke formed no enclosure, at 256 bits, with 0 float-containment violations.
  - Projected cost is 6426.4 CPU-s per attempt and 19279.2 for the campaign, within 9000 / 32400.

C_o0, C_e0, M5, L0/U0, L1/U1, the sign gates, the K5-B map and the R4 mathematics are untouched.

## Per-defect findings

### D1 — in-process prelaunch obligation: OPEN

The specific r2 sub-defects are repaired:

- **The production call is `prelaunch_verify.verify(AUTH_ACTIVE)`, in process, defaults only.**
  - `authorization_interface.py:215-219` (`validate` → `validate_with(ctx, PV, …)`).
  - `:232` calls `run_verifier(module.verify, module.AUTH_ACTIVE)`, and `:91-96` calls `verify_fn(auth_path)` with no keyword, so `allowed_origin_urls` stays at its default.
  - `executor_core.py:80-93` routes `EXTERNAL_AUTHORIZATION` only through it.
  - `:348` is the first statement of `execute`.
  - AST test: `test_executor.py` `test_d1_validate_calls_frozen_verifier_in_process_only`.
- **The returned object is what Q01 consumes.** `decide_from_report` (`:118-145`) works on `report`. The binding records `prelaunch_verdict` and `prelaunch_report_sha256` from it (`:240-244`). Q01 in `executor_core.py:465-468` reads only `decision["binding"]` and `verified_utc_epoch`.
- **No operator material.**
  - `:225-227` refuses a ctx carrying `authorization_bundle`, `prelaunch_report` or `verifier_report` before any verifier code runs.
  - `executor_cli.py:64-70` offers no authorization or report option.
  - `ExecutionContext` no longer has `authorization_bundle`.
- **Verifier source is bound.** `verifier_source_problems` (`:65-88`) checks the resolved path equals `VERIFIER_REL`, bytes equal the preregistration's `packet_code_sha256` and the executor pins, and `verify.__module__` and `co_filename` resolve to that file.
- **Authorization identity is file bytes (the verifier's semantics).**
  - `live_facts` (`:100-114`) hashes `AUTH_ACTIVE`, which must resolve to `prereg.authorization_path`.
  - It is re-hashed after the call (`:233`, compared at `:135-137`), before `ARITHMETIC_STARTED` (`executor_core.py:363-364`), before the seal (`:398-399`) and in Q16 (`:469-470`).
  - The report must have schema v4, `LAUNCH_PERMITTED`, `failing_checks == []`, P01–P12 all present and passing, `read_only`, the same path and sha, `science_sha256 == ctx.protocol_sha256`, `head ==` live `git rev-parse HEAD`, and 40-hex derived commits.
- **The executor binding chain holds** (`binding_problems`, `:148-163`, plus the verifier's P06 at `prelaunch_verify.py:347`). `sha256(EXECUTION_BINDING_AMENDMENT.json)` must equal `AUTH.PRODUCER_R4_IDENTITY.executor_binding_sha256`, which must equal `ctx.executor_binding_sha256` (computed from the same file bytes in `executor_cli.py:59-61` and entering every address). Every live identity file must appear in the amendment's `executor_sources_sha256` at its live hash.
- **The adversarial suite is load-bearing for the refusal paths.** It covers:
  - a forged report through a fake verifier (asserting the fake is never executed);
  - wrong source (a modified copy and an unmodified copy elsewhere);
  - the verifier raising;
  - a genuine REFUSED object;
  - malformed output (a list or None);
  - a stale HEAD;
  - another authorization (by sha and by path);
  - an authorization changed after verification;
  - a wrong protocol identity in the report and in the context;
  - binding and countersignature variants.

  Each of D01–D04 and A01–A03 removes exactly the check a specific row depends on, the control is all-pass, and a crash does not count as detected (`qualify_d1d4.py:263-277`).

**Why D1 is still OPEN.** The obligation is "refuses in-process unless the result is LAUNCH_PERMITTED for the same HEAD and authorization". As built, the frozen verifier cannot return LAUNCH_PERMITTED in any launch configuration the executor accepts, so the refusal is certain rather than conditional. This is the same failure the r2 review called the FAIL: Q01 cannot be satisfied by the genuine frozen verifier's output in the prescribed launch. Only the mechanism differs. See N1–N3 below.

The suite could not detect this. Its only accepting case is a synthetic report passed to the pure `decide_from_report` (`qualify_d1d4.py:158`), and the live call runs only on a host with no `AUTHORIZATION_ACTIVE.json` (`:118-125`). No test runs `verify` → LAUNCH_PERMITTED → `execute` through the supervisor, even on a synthetic git repository.

### D2 — completion_semantics marker contract: CLOSED

- **One marker model, in `slot-N`.** `supervisor.py:88-99` refuses an existing slot, creates `slot-N` and writes RUN_STATE through `LC.write_new`. RUN_STATE holds pid, argv, boot id, start epoch, authorization sha256 (file bytes or `NOT_APPLICABLE_MANUFACTURED`), slot, attempt_uid, protocol sha and executor identity. It is a superset of the frozen fields (`lifecycle.py:148-152`), and the pid and argv are the supervisor's exact kernel cmdline (`:66-71`), which is what the waiter compares. Child diagnostics go to a temporary directory outside the namespace (`:109-111`), so the namespace root holds only `slot-N` directories (P11).
- **Atomic, no-overwrite writes.** Each write is tmp + fsync + `os.link` + directory fsync (`lifecycle.py:70-85`). This also closes r2 D8.
- **Exactly one terminal marker.** `write_terminal` (`:88-97`) refuses a second one. If both appear anyway, the slot classifies as E.
- **No RUN_COMPLETE without a valid seal.** RUN_COMPLETE requires exit 0, a valid scientific seal (the hash recomputes, the attempt_uid matches), no VOID seal and events exactly `[VALIDATED, ARITHMETIC_STARTED, SEALED]`. Otherwise `integrity_refusal` is set and RUN_FAILED is written (`supervisor.py:151-158`); mutant L01 is detected.
- **Marker contents.** RUN_COMPLETE carries pid, attempt_uid, slot, identities, `sealed_record_sha256` (file bytes), `scientific_hash` and the Q01–Q16 gates. RUN_FAILED carries pid, `arithmetic_started`, `supervisor_evidence`, `failure_class = PR.failure_class(evidence)` (the frozen function only), the VOID sha and a digit-masked traceback (`:156-173`).
- **No scientific and VOID seal together.** `seal()` refuses if any seal exists (`executor_core.py:540-546`, L02 detected), and the VOID branch re-checks (`:409`).
- **VOID only for the preregistered classes.** `void_class` (`:420-432`) returns None for ENOSPC/EDQUOT and KeyboardInterrupt (L03 detected). SIGTERM and SIGKILL keep their default action, so they leave no seal. Evidence: CPU → CPU_RLIMIT + VOID; wall (SIGUSR1) → WALL_TIMEOUT + VOID; external SIGKILL → PROCESS_KILLED_BY_EXTERNAL_SIGNAL, no seal, `RETRY_PERMITTED`; ENOSPC → DISK_FULL_BEFORE_SEAL, no seal.
- **Ledger.** `outcome_entry` (`:247-262`) produces exactly the frozen `OUTCOME_KEYS`. `reconcile` (`:265-300`) reproduces P11 (one LAUNCH_NOTICE and one well-formed OUTCOME; the `run_failed_sha256` hash; `arithmetic_started` compared with `is`; the class derived by `PR.failure_class`) and P09 (a ledger seal is a seal even if the host file is gone), and adds a LAUNCH_NOTICE ↔ RUN_STATE authorization check. L04 is detected.

Residual notes N4, N5 and N6 do not reopen D2.

### D3 — reboot recovery: CLOSED

- **Recovery only classifies and writes markers.** `supervisor.py recover` (`:179-221`) never launches the executor and never recomputes anything. It classifies each `slot-*` directory with `LC.classify` (`lifecycle.py:160-231`).
- **Class E (torn) conditions:** a malformed or unreadable marker; a torn log other than a final partial line; events from another attempt or out of order; both seals; a seal/mode mismatch; a seal that does not recompute or has another attempt_uid; a seal without RUN_STATE; a stale terminal marker; both terminals; RUN_COMPLETE without a scientific seal or naming another seal; RUN_FAILED beside a scientific seal.
- **Frozen actions** (`recovery_action`, `:234-243`):
  - A: RUN_FAILED, not started.
  - B: RUN_FAILED, interrupted. A changed boot id gives HOST_REBOOT_OR_BOOT_ID_CHANGE (transient); a lost supervisor on the same boot gives UNKNOWN_FAILURE (no retry).
  - C: consume the seal and write RUN_COMPLETE with `recovered: true`; never retryable (R01 detected).
  - D: RUN_FAILED with the VOID sha.
  - E: `ADJUDICATION_REQUIRED`, write nothing (R02 detected).
- **Liveness.** A slot counts as LIVE only when it has no terminal marker, its RUN_STATE boot equals the current boot and the supervisor pid matches the exact `/proc` argv (`:228-230`, `supervisor.py:57-63`). Completion is never inferred from absence.
- **Evidence.** All nine boundaries pass on both the same and a changed boot. Idempotence holds (tree hash unchanged on a second pass). LIVE is left alone. A sealed address is refused again (`FINALIZED_ADDRESS_EXISTS`). A live crash (SIGKILL of supervisor and child mid-arithmetic) is recovered as B / UNKNOWN_FAILURE with no seal.

Residual note N4 does not reopen D3.

### D4 — RUN_PROVENANCE.json: CLOSED

- **Contents.** `evidence/qualification_r3/RUN_PROVENANCE.json` records:
  - commit `2b9fdf8d`, the same at the end, with empty porcelain before and after;
  - `FROZEN_QUALIFICATION`, identity `f6ac2676…`, protocol `390c2a68…`, science `9ace6896…`, runtime identity `1d49bd4e…` with 0 contract differences;
  - host facts including the libc sha, python 3.12.3, python-flint 0.9.0, FLINT 3.6.0 and glibc 2.41-12+deb13u4;
  - the pins sha `c6ddb65b…` and the sources manifest;
  - guard DENY and every authorization file absent;
  - the supervisor and lifecycle sha256, the runner pid and argv, start and end times, and the result sha.
- **No cycle.** The result does not reference the provenance.
- **No contamination.** Provenance is a separate file, so no runtime field enters a scientific hash; the identical `cb28b972…` payload confirms it.
- **Validation.** EG21 checks it at assembly, and `cmd_check` (`qualify_executor.py:730-735`) checks it with `final=True` (the result sha, HEAD unmoved, a clean worktree after the run).
- Minor gap N11 below.

## New defects, by severity

### N1 — the in-process verifier always refuses a supervised launch. CRITICAL, LOAD-BEARING (it keeps D1 open)

1. **The launch order puts the slot on disk before verification.** `supervisor.supervise` creates `<ROOT>/slot-N` and writes RUN_STATE (`supervisor.py:88-99`) before it starts the child (`:114`). The child's first act is `enforce_guard`, which calls `verify(AUTH_ACTIVE)` (`executor_core.py:348`).
2. **The frozen P11 then refuses.** P11 (`prelaunch_verify.py:461-477`) requires every namespace entry to have exactly one LAUNCH_NOTICE and one OUTCOME. The current slot has no OUTCOME yet, which returns False. P11 also requires the next slot, `slot-(N+1)`, to be free and to have its own LAUNCH_NOTICE (`:488-501`).
3. **Moving the namespace does not help.** The countersignature check pins `ctx.output_dir` to `prereg.output_namespace/slot-N` (`authorization_interface.py:203-205`). Any launch the countersignature accepts is therefore one P11 refuses.

The consequences:

- Every real launch the TRUST_MODEL procedure prescribes (`supervisor.py launch --mode real`) ends in `UNAUTHORIZED_REAL_ARITHMETIC` before VALIDATED.
- Each refusal still consumes a launch slot and needs a new LAUNCH_NOTICE (`retry_policy.attempt_start`), and there are at most 9 slots.
- Q01 cannot be satisfied by genuine frozen-verifier output. The r2 FAIL stands in a new form.

It is fail-closed, so no wrong science can result, but the frozen prelaunch contract cannot be met.

### N2 — the second verifier call inside the production backend seals a permanent VOID. CRITICAL, LOAD-BEARING

- **Where it runs.** `CusumPointBackend.prepare_point` calls `EC.enforce_guard` again (`backends.py:384`; the file is unchanged from r2). In r2 that call was a pure validation. In r3 it runs the full verifier, and it runs after `ARITHMETIC_STARTED` (`executor_core.py:365-366`).
- **Why it always refuses.** By that point the slot always exists: at the latest, `AttemptLog.emit("VALIDATED")` creates it (`:266`). So P11 refuses exactly as in N1.
- **What that triggers.** `ExecutorRefusal("UNAUTHORIZED_REAL_ARITHMETIC")` → `void_class` → INTEGRITY_REFUSAL → `VOID_RECORD_SEALED.json` (`:407-416`). Under `void_after_arithmetic` and P09, that VOID blocks every further attempt under this protocol.
- **It survives an ordering fix.** Any repair that only moves the first verification ahead of slot creation still hits this call and seals the VOID.
- **It turns transient failures into permanent VOIDs.** The verifier calls `git ls-remote origin` with no timeout (P03/P04 publication checks). A transient network failure here would also become a permanent protocol VOID, where r2's pure re-check could not fail this way.

### N3 — real mode runs without the supervisor. HIGH, LOAD-BEARING

- **The admission rule.** `slot_admission` returns `[]` whenever the output directory does not exist (`executor_core.py:206-207`), even when an `--attempt-uid` is given. `executor_cli.py real --output-dir …/slot-N --attempt-uid <anything>` is therefore admitted with no supervisor.
- **What is lost.** No RLIMIT_CPU, no wall watchdog, no RUN_STATE and no terminal marker. This breaks obligation 1 and `completion_semantics`.
- **It is the only path that passes the first verifier call.** Because of N1, this unsupervised path is the only one where verification #1 can pass (the slot is absent and the LAUNCH_NOTICE present). It then deterministically reaches N2 and seals a VOID. In real mode, a missing slot must be refused unless a supervised RUN_STATE is present.

**Repair (small, local, no science change).**

- Perform the single in-process verification before `slot-N` exists: for example, the child verifies first, and RUN_STATE and the slot are created afterwards, with the executor then admitting only that RUN_STATE.
- Replace the verifier call in `prepare_point` with a pure re-check of the bound decision: the guard policy plus the authorization re-hash.
- Require RUN_STATE in real mode.
- Add one end-to-end qualification row on a synthetic git repository and namespace that drives supervisor → `verify` → LAUNCH_PERMITTED → `ARITHMETIC_STARTED` with a manufactured backend. This is a fidelity test, not anti-tamper machinery.

### N4 — an orphaned executor child is not covered by liveness. MEDIUM, not load-bearing (fails closed)

Recovery checks only the supervisor pid (`lifecycle.py:228-230`). If the supervisor dies on the same boot while the child keeps running:

- recovery writes RUN_FAILED (B, UNKNOWN_FAILURE);
- the child continues with no wall watchdog;
- a later seal turns the slot into class E beside a ledger OUTCOME that says "no seal".

P09 and E-adjudication keep this fail-closed. Tying the child to the supervisor (a parent-death signal or a process group), or recording and probing the child pid, would remove it.

### N5 — partial seal bytes can be left on disk. LOW, not load-bearing

`write_new` leaves `.NAME.pid.tmp` in place if the write or fsync raises, for example ENOSPC during the scientific seal (`lifecycle.py:76-79`), or on SIGKILL mid-write. That tmp can hold record numbers from a transient, retryable attempt, which conflicts with `transient_kills` ("never persisted"). Recovery does not remove it. Unlinking on failure, and quarantining or deleting tmp files in class B, would close it.

### N6 — OOM classification. LOW, not load-bearing

- The supervisor hard-codes `kernel_oom_record: False` (`supervisor.py:149`), so a kernel OOM is labelled PROCESS_KILLED_BY_EXTERNAL_SIGNAL. The retry outcome is the same (both are transient), but the label is wrong.
- A Python `MemoryError` after arithmetic becomes INTEGRITY_REFUSAL plus VOID, where an OOM-class treatment is arguable. This should be a stated policy rather than an accident.

### N7 — countersignature ordering and publication. LOW, governance

`is_ancestor(authorization_commit, intro)` (`authorization_interface.py:188`) also accepts the authorization commit itself, although the template says "after". Publication of the countersignature commit on the pinned ref is not checked.

### N8 — the prelaunch report is not persisted. LOW

Only `prelaunch_report_sha256` is sealed (`authorization_interface.py:242`, inside `scientific.guard`). An adjudicator cannot read the P01–P12 details. It should be stored in the unhashed metadata.

### N9 — documentation drift. LOW

- `RESULT.md` is still the r2 result, but `README.md` lists it as the r3 result.
- `TRUST_MODEL.md` still says "science content unchanged since `dbbd405a`" (r2 D11, unfixed) and cites `evidence/qualification/`.
- The `rule` string in `REAL_INPUT_GUARD.json` still describes the r2 bundle and report model.
- `EXECUTOR_SPEC_R3.md` says L01–L03; L04 was added (disclosed in `DEV_CALIBRATION.md`).

### N10 — P08 cannot see the r3 executor. LOW, informational

The frozen P08 basenames (`first_real_probe_executor.py`, `first_real_probe_supervisor.py`) do not match `executor_cli.py` / `supervisor.py`, so P08 cannot see a concurrent r3 run. P11 covers concurrency inside the namespace. Separately, the amendment must not pin `REAL_INPUT_GUARD.json`, or activation will fail P06.

### N11 — provenance check gaps. LOW

`provenance_problems` does not check that `git_commit` is the source freeze or an ancestor of HEAD. `qualification_mode` is derived from the config's constant `status` rather than from how the run was actually invoked. I verified the commit chain independently above.

### N12 — informational

A recovered D-class RUN_FAILED derives HOST_REBOOT or UNKNOWN_FAILURE from reconstructed evidence even though a VOID seal exists. P09 still blocks, so there is no consequence.

## Scope limitations accepted

1. **The execution host is not an independent trust root.** The guard, the in-process verifier and the countersignature are consistency and fail-closed mechanisms (`TRUST_MODEL.md`), and that is stated honestly. I do not fail the review for it and do not ask for on-host anti-tamper work. The following are within that accepted limitation: sys.modules/pyc substitution, `GIT_*` environment variables, and time-of-check/time-of-use on the amendment or countersignature after verification.
2. **The real-mode assembly (Q01/Q14/Q16 REAL branch, `CusumPointBackend`) cannot be run end-to-end under DENY.** It is judged statically, which is exactly how N1–N3 were found.
3. **Reviews are not proofs.** Arb correctness and the inherited 53-bit CRAMER construction remain stated assumptions.
4. **The r2 accepted findings stand** as the r2 review recorded them: Q1–Q4 and Q6–Q8, plus the order-2 re-derivation outside the guard on already-published values.

## Disposition

r3 genuinely repairs the r2 sub-defects:

- The frozen verifier is now the authority, called in process with defaults, and its returned object is what is consumed.
- The authorization is identified by file bytes, and the amendment → authorization → address → running-bytes binding holds.
- The `slot-N` marker model, ledger reconciliation, reboot recovery and provenance are faithful to the frozen protocol.
- Every accepted scientific semantic is byte-preserved, and all predecessors are intact.

It fails because the integrated launch path cannot work:

- A supervised real launch is always refused by the frozen verifier's own P11 (N1).
- The second, post-`ARITHMETIC_STARTED` verifier call converts any launch that gets past the first call into a permanent protocol VOID (N2).
- The only launch that gets past the first call is an unsupervised one (N3).

All three are local fixes: move the one verification before slot creation, make the backend re-check pure, and require RUN_STATE in real mode. They should be followed by one end-to-end positive-path qualification row on a synthetic repository. No science changes.
