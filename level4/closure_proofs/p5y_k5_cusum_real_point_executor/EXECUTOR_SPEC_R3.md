# Real point executor r3: specification addendum (written before the repair code)

**Why an r3.**
- The independent static review of the r2 freeze `52769488` (qualification `57b51a6f`, 17/17 gates PASS) returned
  **FAIL** on D1–D4 (`review/EXECUTOR_STATIC_REVIEW_R2.md`, publication `b4f1315f`).
- **Accepted by that review and not reopened:** the mathematics, the R4 certification machinery (C_o0, C_e0, M5,
  transport), the CRAMER compatibility contract, the science preregistration, the qualification/science separation,
  the guard, Q02–Q16, determinism, the cost model, and the stated trust-model limitation.
- r2 stays in history unchanged; this addendum supersedes r2 only where they differ.
- **Nothing scientific changes:** cell, m set, point e = 0, L0/U0, M5, transport, sign gates, K5-B map, precision 256,
  CPU ceilings, C_o0, C_e0, CRAMER contract, R4 mathematics.
- REAL_INPUT_ARITHMETIC_GUARD stays DENY and EXECUTION_AUTHORIZED stays false.

**Root cause shared by D1–D3.** r2 introduced its own authorization object and its own marker files beside the ones
the frozen protocol already defines. r3 removes the parallel models and implements the frozen ones:
`SCIENCE_PREREGISTRATION_R4.authorization_path`, `executor_binding.amendment`, `completion_semantics`,
`retry_policy.slots_and_ledger` and `void_after_arithmetic`.

## R3-1 (D1). In-process prelaunch verification is the authority

Real mode, under guard policy `EXTERNAL_AUTHORIZATION` (the frozen policy stays DENY):

1. **Verifier source.** The executor imports the frozen `prelaunch_verify` and refuses unless
   - the module file resolves to `p5y_k5_cusum_first_real_probe_protocol/code/prelaunch_verify.py`;
   - its bytes hash to the preregistration's `packet_code_sha256` entry (`54b198bc…`) and to the executor pins;
   - `verify` is that module's own function, with its code object compiled from that file.
2. **Authorization object.** The authorization is the verifier's own constant `AUTH_ACTIVE`, which must equal
   `REPO / prereg.authorization_path`. It is the only object the protocol binds, and its identity is its
   **file-bytes sha256** — the verifier's semantics, which the executor adopts.
3. **Call.** The executor calls `prelaunch_verify.verify(AUTH_ACTIVE)` in-process, **with defaults only**, at every
   guard evaluation: before `validate_context`, and again inside the production backend before the first operator
   touch.
4. **Decision on the returned object only.** The returned object is consumed directly. There is **no** input path for
   a report, and a context that carries any operator-supplied authorization material is refused. Q01 requires all of:
   - the report is a dict with schema `…prelaunch-report.v4`;
   - `verdict == LAUNCH_PERMITTED`, `failing_checks == []`, P01–P12 all present and passing, `read_only` true;
   - `authorization_path == AUTH_ACTIVE`;
   - `authorization_sha256` equals the file-bytes hash read by the executor both before and after the call, and again
     at ARITHMETIC_STARTED and at seal, so a change after verification refuses or VOIDs;
   - `science_sha256 == ctx.protocol_sha256`;
   - `head` equals the live `git rev-parse HEAD`;
   - `freeze_commit_derived` and `authorization_commit_derived` are 40-hex commits.
5. **Executor binding.** `sha256(EXECUTION_BINDING_AMENDMENT.json bytes)` must equal three values:
   - `AUTH_ACTIVE.PRODUCER_R4_IDENTITY.executor_binding_sha256`;
   - `ctx.executor_binding_sha256`, which enters every scientific address;
   - the value the verifier's P06 checked.

   The amendment's `executor_sources_sha256` must contain every executor identity file at its live hash, so the running
   bytes are the reviewed bytes.
6. **Countersignature as a second requirement.** The external countersignature
   (`authorization/COUNTERSIGNATURE_ACTIVE.json`, fixed path, committed and unmodified, from template
   `config/EXTERNAL_AUTHORIZATION_TEMPLATE.json` r3) is a second, separately hashed requirement. It must name:
   - `protocol_authorization_sha256`, the same file-bytes hash as in item 4;
   - `execution_binding_amendment_sha256`;
   - the slot;
   - a nonce;
   - an independent countersigner.

   It never replaces or overloads the verifier result.
7. **Failure.** Any exception raised by or around the verifier refuses. Every refusal happens before `VALIDATED`, so
   no arithmetic starts.

**D1 adversarial suite.** Each case below must be refused, and the executor must not reach arithmetic:
- forged operator report;
- stale report (another HEAD);
- report for another authorization;
- authorization changed after verification;
- wrong verifier source;
- verifier returns REFUSED (live, on the host, where `AUTHORIZATION_ACTIVE.json` does not exist);
- verifier raises;
- malformed output;
- correct output with the wrong protocol identity;
- countersignature naming another authorization;
- amendment not binding the running executor.

A synthetic well-formed PERMITTED report is accepted by the pure decision function; this is the positive control. The
production call path is shown structurally: an AST test requires the call `verify(AUTH_ACTIVE)` with no other
arguments and no report parameter. Mutants D01–D04 must be detected.

## R3-2 (D2). The frozen marker lifecycle in `<output_namespace>/slot-N`

**Supervisor (`code/supervisor.py launch`).**
- Creates `slot-N`, refusing if it exists.
- Writes `RUN_STATE.json` atomically, with no overwrite. It holds the supervisor pid, its exact argv, the boot id, the
  start epoch, the authorization sha256 (file bytes of `AUTH_ACTIVE`, or `NOT_APPLICABLE_MANUFACTURED`), the slot, a
  random `attempt_uid`, the protocol sha256 and the executor identity.
- Launches the executor child with that `attempt_uid`.

**Executor output directory.** The executor accepts its slot only if it is empty or holds exactly that RUN_STATE (same
`attempt_uid`, supervisor pid equal to its parent pid); otherwise `STALE_OUTPUT_NAMESPACE`. `ATTEMPT_LOG` events carry
the `attempt_uid`. The sealed record carries it only in the unhashed metadata, since the address holds no attempt id.

**VOID follows `void_after_arithmetic` exactly.** It is sealed only for INTEGRITY_REFUSAL, CPU_RLIMIT or WALL_TIMEOUT.
- A disk-full error (ENOSPC/EDQUOT) after arithmetic seals **nothing**: it is transient, and a transient kill leaves no
  sealed record by construction.
- A scientific and a VOID seal can never coexist, because each refuses to be written while the other exists.

**Exactly one terminal marker per attempt.** It is written atomically with a no-overwrite link, so a second terminal
marker is refused.
- **RUN_COMPLETE:** only if the child exited 0 and a valid scientific seal exists (parses, its scientific hash
  recomputes, the attempt_uid and events match, and no VOID seal exists). Contents: pid, attempt_uid, slot, sealed
  record sha256 (file bytes), scientific hash, the Q01–Q16 gates and the identities.
- **RUN_FAILED:** otherwise. Contents: pid, attempt_uid, slot, arithmetic_started, supervisor_evidence, the failure
  class from the frozen `probe_rules.failure_class`, the VOID seal sha256 if one exists, and a traceback with every
  digit masked (no numbers).
- **Integrity evidence** is set for a refusal before arithmetic (exit 3) and for an integrity failure after it (exit 4,
  not cost or ENOSPC), so the frozen derivation yields INTEGRITY_REFUSAL.

**Ledger (`code/lifecycle.py`).**
- `outcome_entry(slot)` derives the OUTCOME `{event, slot, arithmetic_started, failure_class, run_failed_sha256,
  sealed_record_sha256}` mechanically from the host files.
- `reconcile(slot, ledger_entries)` applies the frozen governing rules (P09 and P11 semantics) and refuses on any
  disagreement.

**D2 test matrix.**
- **Supervisor runs:** normal success; pre-arithmetic refusal; CPU ceiling; wall timeout; external kill; disk failure
  (ENOSPC).
- **Marker faults:** malformed marker; duplicate terminal marker; scientific + VOID conflict; stale marker from another
  attempt; ledger/marker disagreement.
- Mutants L01–L03 must be detected.

## R3-3 (D3). Reboot recovery (`code/supervisor.py recover --namespace ROOT`)

Recovery classifies each `slot-N` from persisted evidence only. It never launches the executor and never recomputes
anything.

| class | meaning |
|---|---|
| **A** | no attempt started (no ARITHMETIC_STARTED, no seal) |
| **B** | ARITHMETIC_STARTED, no seal |
| **C** | a valid scientific seal |
| **D** | a valid VOID seal |
| **E** | inconsistent or torn state (see below) |

**Class E conditions:**
- malformed or unparseable marker or log line (except a final partial log line after a crash, which is recorded);
- both seals;
- a seal whose hash does not recompute or whose attempt_uid differs;
- a terminal marker for another attempt;
- RUN_COMPLETE without a valid scientific seal;
- both terminal markers;
- events out of order.

**Liveness is never inferred from absence alone.** A slot without a terminal marker whose supervisor pid is alive on
the same boot, with exact `/proc` argv equal to RUN_STATE, is **LIVE**: recovery does nothing. A boot-id change is
evidence of interruption.

**Frozen actions for a slot without a terminal marker and not LIVE:**
- **A:** write RUN_FAILED (`arithmetic_started` false, evidence `boot_id_changed` or `supervisor_lost`). The slot is
  consumed; a new launch needs a new slot, a new LAUNCH_NOTICE and a permitted prelaunch verification.
- **B:** write RUN_FAILED (`arithmetic_started` true) with the supervisor evidence reconstructed from persisted facts.
  - A boot change gives HOST_REBOOT_OR_BOOT_ID_CHANGE, transient, so a retry is possible only under
    `retry_decision`.
  - A lost supervisor on the same boot gives UNKNOWN_FAILURE, non-transient, so there is no retry.
- **C:** consume the existing record and **never rerun**. If RUN_COMPLETE is missing, write it from the sealed bytes,
  flagged `recovered: true`.
- **D:** VOID semantics apply and block further attempts. If RUN_FAILED is missing, write it with the recovered
  evidence and the VOID seal hash.
- **E:** write nothing and report `ADJUDICATION_REQUIRED` (fail closed).

**Crash-boundary suite.** Manufactured states at each boundary:
- before RUN_STATE;
- after RUN_STATE;
- during ATTEMPT_LOG (partial line);
- before the scientific seal (tmp only);
- immediately after the scientific seal;
- before RUN_COMPLETE;
- after the VOID seal;
- during the terminal-marker write (tmp only, and a truncated final file).

The states are taken from real manufactured runs and cut at the boundary. They are tested both with the recorded boot
id and with a changed boot id, plus one live crash (SIGKILL of supervisor and child mid-arithmetic, then recover).
Recovery must reach the frozen decision, must never mark a C slot retryable, and must be idempotent (a second pass
changes nothing). Mutants R01–R02 must be detected.

## R3-4 (D4). `RUN_PROVENANCE.json` in the qualification evidence

The runner writes `RUN_PROVENANCE.json` when it finishes. It binds:
- the git commit, the porcelain before and after the run, the executor identity, the protocol sha256 and the science
  sha256;
- the runtime identity and live host facts, python, python-flint, the FLINT version (Arb is part of FLINT 3), glibc and
  libc;
- the pins and sources manifests;
- the mode (`FROZEN_QUALIFICATION` or `DEV`), the guard policy and the authorization state;
- the supervisor identity (sha256 of `supervisor.py`), the runner pid and argv;
- the start and end timestamps and the qualification result sha256.

The result does not reference the provenance, so there is no cycle; `check` validates the provenance against HEAD, the
protocol and the result. Runtime fields never enter any scientific hash.

## New gates and mutation groups

- **EG18:** D1 in-process prelaunch and authorization binding.
- **EG19:** D2 marker lifecycle and ledger reconciliation.
- **EG20:** D3 recovery and crash boundaries.
- **EG21:** D4 provenance (and `check`).
- **Mutation groups:** D01–D04, L01–L03 and R01–R02, in addition to the inherited E01–E16, P01–P04, A01–A03, V01 and
  C01.
- **Revised in place:** the A-group validator mutants (the countersignature validator) and the supervisor marker tests,
  because they now target the frozen objects.
