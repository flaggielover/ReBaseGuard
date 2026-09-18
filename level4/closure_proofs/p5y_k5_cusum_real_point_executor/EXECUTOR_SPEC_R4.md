# Real point executor r4: specification addendum (written before the repair code)

**Why an r4.**
- The independent review of the r3 freeze `2b9fdf8d` (qualification `b2930bb2`, 21/21 gates, publication
  `34bb9b0b`) ruled **D1 = OPEN** (N1–N3) and **D2 = D3 = D4 = CLOSED**.
- r4 repairs exactly N1–N3. The r3 items that review accepted are not reopened: the in-process frozen verifier, no
  authority for operator reports, the file-bytes authorization binding, the D2 lifecycle and ledger, D3 recovery, D4
  provenance, and the mathematics, certification, replay, cost and runtime.
- **Nothing scientific changes.** REAL_INPUT_ARITHMETIC_GUARD stays DENY and EXECUTION_AUTHORIZED stays false.

## R4-1. Exactly one authoritative pre-arithmetic launch decision (N1)

`supervisor.py launch` for the governed modes (`real`, and the qualification mode `governed_manufactured`):

1. **Resolve the launch inputs.** These are the slot `<prereg.output_namespace>/slot-N`, which must not exist and must
   lie in the preregistered namespace; the binding; the executor binding, i.e. the sha256 of
   `EXECUTION_BINDING_AMENDMENT.json`; and the protocol sha256.
2. **Check the guard policy.** DENY gives `PRELAUNCH_REFUSED` with no verification, no slot and no state.
3. **Verify.** `authorization_interface.validate(ctx)` makes the single call to the frozen
   `prelaunch_verify.verify(AUTH_ACTIVE)`: in process, with defaults, the returned object consumed directly. Every r3
   check applies.
4. **On REFUSED, or any verifier exception:** return `PRELAUNCH_REFUSED`. **No slot, no RUN_STATE and no VOID** are
   created, and no scientific address is consumed.
5. **On PASS:** the decision record includes:
   - the verdict and the full frozen prelaunch report (so an adjudicator can read P01–P12);
   - the authorization, amendment and countersignature file-bytes sha256;
   - HEAD, the protocol sha256 and the executor identity;
   - the slot, the namespace, the attempt parameters and the verification time.

   It is bound as `prelaunch_decision` plus `prelaunch_decision_sha256` into a new `RUN_STATE`, and only then is
   `slot-N` allocated and RUN_STATE written atomically.
6. **Launch.** The child is launched with `--attempt-uid` and `--decision-sha256`.

The only production call site of the verifier is `supervisor.py`. `executor_core`, `backends` and `executor_cli` never
reference it (an AST fence).

## R4-2. No full verifier after launch; a pure bound-decision re-check (N2)

**The guard in the child.** Under EXTERNAL_AUTHORIZATION, `executor_core.decide` calls
`authorization_interface.bound_decision_problems(ctx)`. This is a pure local check with no git, no network, no ledger
scan, no slot creation and no new verdict. It asks one question: does this running child still match the decision
that authorized this exact attempt? It requires:
- the slot holds exactly RUN_STATE, whose `attempt_uid` equals `--attempt-uid`;
- RUN_STATE's supervisor pid is the child's parent, and its argv equals `/proc/<ppid>/cmdline`;
- `sha256(canonical(prelaunch_decision))` equals RUN_STATE's digest and equals `--decision-sha256`;
- the decision verdict is LAUNCH_PERMITTED;
- the authorization file bytes still hash to the decision's value;
- the live executor identity, protocol sha256, executor binding, slot, namespace, K1 record identity, m set, point,
  cell and precision all equal the decision.

**Where the re-check runs.** `CusumPointBackend.prepare_point`'s defence-in-depth `enforce_guard` is therefore pure. On
a mismatch the attempt fails closed before arithmetic.

**Post-start fence.** `executor_core` latches `arithmetic_started()` immediately before `ARITHMETIC_STARTED`. From then
on `authorization_interface.validate_with` raises `PostStartVerifierCall` **before any verifier code runs**. That
exception is an executor defect: `void_class` returns None for it, so it is **never sealed as VOID**. A qualification
row and mutants N02 and N05 prove the fence.

## R4-3. The supervisor is required in real mode (N3)

- For real and governed attempts, `slot_admission` refuses a missing slot or a missing or mismatching RUN_STATE. An
  unsupervised real launch is refused.
- `enforce_guard` requires permission for any `real_input` or `governed` backend.
- The non-governed qualification modes (`manufactured`, `burn`, `diskfull`) keep their r3 definitions.

## R4-4. A permitted synthetic governed launch, end to end (load-bearing)

`code/qualify_governed.py` builds a **synthetic** full clone S of the repository at the tree under test, containing:
- a SYNTHETIC review;
- an amendment binding S's executor bytes and the frozen adapter pins;
- `AUTHORIZATION_ACTIVE.json` (activation fields only);
- a countersignature;
- a ledger LAUNCH_NOTICE for slot-1;
- the guard policy EXTERNAL_AUTHORIZATION.

All of these are committed only in S, in the order the preregistration fixes. S is never pushed.

**Two hermetic test doubles, and nothing else:**
- the verifier's network `git ls-remote origin` (the GitHub publication anchor) is answered from a local synthetic
  bare repository by a `git` shim on `PATH`. The origin URL stays the allow-listed GitHub URL, and every other git
  operation is real;
- the preregistered output namespace `/root/work/k5-first-real-probe` is virtualised by running the whole scenario in
  a private mount namespace with a copy-on-write overlay over `/root/work`. The real namespace is never created.

The unmodified frozen verifier (S's byte-identical copy, pinned by `packet_code_sha256`) runs with its defaults.

**Positive path:** frozen verifier PASS → slot allocation → RUN_STATE → child launch → child pure re-check → synthetic
arithmetic (ManufacturedPointBackend, governed) → valid seal → RUN_COMPLETE → ledger reconciliation
(`lifecycle.outcome_entry` / `reconcile`).

**Negatives:**
- verifier REFUSED → no slot;
- verifier exception → no slot;
- unsupervised real mode → refused;
- changed decision digest → refused;
- changed attempt_uid → refused;
- missing RUN_STATE → refused;
- stale RUN_STATE → refused;
- wrong supervisor identity (pid or argv) → refused;
- post-start verifier call → fenced, no VOID.

**Mutants.** Each mutant is built into its own S, whose amendment binds the mutant bytes, so detection comes from
behaviour and not from identity drift:
- N01: slot created before verification;
- N02: the child guard runs the full verifier;
- N03: missing slot admitted;
- N04: decision digest not checked;
- N05: post-start fence removed.

## Gates

- **EG22:** the governed-launch suite (positive end to end, negatives, N01–N05).
- **Regressions:** EG01–EG21 stay as in r3, including the D1–D4 suites.
- **RUN_STATE:** gains `prelaunch_decision` and `prelaunch_decision_sha256`, null for the non-governed modes. This is
  the only lifecycle contract change; D2 and D3 are re-run as regressions.
