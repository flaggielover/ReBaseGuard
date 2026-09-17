# Real point executor r2: specification addendum (written before the repair code)

**Why an r2.**
- The independent static review of the r1 executor freeze `8ffcfaff` (qualification `80a3ab2b`, all 12 gates PASS)
  returned **FAIL**.
- **Passed:** the R4 mathematics, certification, guard, separation, serialization, cost and trust statement.
- **Failed:** the executor was not a complete realization of the preregistration's executor obligations. See
  `review/EXECUTOR_STATIC_REVIEW_R1.md`.
- r1 stays in history unchanged, and this addendum supersedes it where they differ.
- Nothing real is computed: REAL_INPUT_ARITHMETIC_GUARD policy stays DENY and EXECUTION_AUTHORIZED stays false.

## R2-1. Preregistered producer-qualification gates evaluated inside the executor

The sealed record carries `producer_qualification = {gates: Q01..Q16 -> bool, evidence}`.
- The consumer decides PASS or VOID only with the frozen `probe_rules.producer_qualification` / `science_usable`
  over these gates, plus the sign-independent structural checks QE01–QE12. QE05, the DENY guard, is no longer a
  consumer condition; it is a qualification-harness check.
- **Real-mode evaluation** (`CusumPointBackend`) follows the table below.
- **Manufactured-mode evaluation** (`ManufacturedPointBackend`) handles the real-only gates as follows:
  - Q01, Q04 and Q14 evaluate the harness analogues: the guard decision is recorded, and the runtime identity is
    checked on the host.
  - Q10 is recorded as `NOT_APPLICABLE_MANUFACTURED`, set to true with that label. The consumer refuses such labels
    in a record whose binding kind is `real`.
  - Q08 compares graded and scalar radii only.

| gate | real-mode evaluation |
|---|---|
| Q01 | a prelaunch report with verdict LAUNCH_PERMITTED, naming this authorization sha256, is supplied in the authorization bundle |
| Q02 | the real input adapter re-validates V01–V10 at seal |
| Q03 | point cell {0} from frozen cell 0; x1 = right |
| Q04 | Aux5 production gates in the 84aaa6a5 pattern at stages initial and final: `manifest_v3.verify()` with no problems, TCB coverage (`tcb5.verify_coverage`) over the committed Aux5 files ∪ the executor pins, `runtime_identity5.require`, `ScipyGuard.require_clean()` around all arithmetic, and the preregistration's host runtime contract |
| Q05 / Q13 | the sha256 of every file in `config/EXECUTOR_PINS.json` (R1–R4, protocol, point certificate, K1 record / manifest / cells, executor sources) is identical at start and at seal |
| Q06 | `odd_block_certificate.verify_artifact` (C_o0, R4) and the R3 `resolvent_certificate.verify_artifact` (C_e0) replay identically |
| Q07 | exact rationals; L0 ≤ U0, M5 ≥ 0, L1 ≤ L0 ≤ U0 ≤ U1; transport equals `probe_rules.transport` |
| Q08 | `radius_only_cascade(inputs)` (the graded point cascade on the inputs with the origin values removed, so no centre and no enclosure): the scalar-mode nodes equal the frozen midpoint DAG (`aux_propagate.cell_dag` + `aux_certifier.midpoint_order3_eps` + the R1 rung formula), relative 2^-200, and graded radius ≤ scalar radius per m |
| Q09 | local-tower trace length 13 (12 iterations); every tower and anchor node has e, o ≤ t, finite; anchors only at orders ≤ 3; M5 = Σ|c|·e of the order-5 tower |
| Q10 | frozen order-2 midpoint path on the same certifier (`aux_propagate.cell_dag`, reviewed `enclosures`, `assembly.assemble`): per m, R(0) and R'(0) intersect the committed 84aaa6a5 RUNG_256 enclosures |
| Q11 | canonical serialization; scientific hash recomputes |
| Q12 | four distinct addresses; no scientific or VOID record for them in the output root |
| Q14 | the guard decision and the authorization validation happen before the first backend method |
| Q15 | CPU and wall at seal are within the soft limits |
| Q16 | ARITHMETIC_STARTED after the authorization UTC (real); event order VALIDATED < ARITHMETIC_STARTED < SEALED |

## R2-2. Attempt events, VOID sealing, CPU limit

- **Attempt log.** The executor appends `ATTEMPT_LOG.jsonl` events (VALIDATED, ARITHMETIC_STARTED, SEALED or VOID)
  with no numbers.
- **VOID sealing.** Any exception after ARITHMETIC_STARTED, including `CPU_RLIMIT` raised by the executor's SIGXCPU
  handler, atomically seals `VOID_RECORD_SEALED.json` (real) or `MANUFACTURED_VOID_RECORD_SEALED.json`. The seal holds
  the failure and the certificates computed so far, and the exception is then re-raised.
- **Supervisor.** `code/supervisor.py` launches `code/executor_cli.py` as a child. It sets RLIMIT_CPU soft 9000 /
  hard 10800 (or a qualification override), runs a wall watchdog, and records the wait status, child CPU seconds and
  boot id. It derives the class with `probe_rules.failure_class` and writes `RUN_STATE`, `RUN_COMPLETE` or
  `RUN_FAILED`.

## R2-3. External authorization without a code change at activation

`guard_decision(bundle)`:
- **policy `DENY`** (the frozen config) denies always;
- **policy `EXTERNAL_AUTHORIZATION`** permits only if `authorization_interface.validate(bundle, context)` accepts a
  countersigned object. That object must carry the template fields, `EXECUTION_AUTHORIZED` true, and the running
  executor identity sha256, qualification result sha256, science sha256, host runtime identity sha256, K1 record
  sha256, cell, m set, precision, CPU ceiling, slot and nonce. A prelaunch report with LAUNCH_PERMITTED naming the
  authorization sha256 is also required.

**What activation changes.** Only the guard policy file and the published countersigned authorization. The executor
sources, which are its identity, are frozen, qualified and reviewed beforehand. The validator is qualified on
synthetic bundles, and it is not a cryptographic authority (`TRUST_MODEL.md`).

## R2-4. Production-stack mutations

**Production stack.** The real-stage smoke (synthetic candidates at the degenerate cell {0}; no R''' / R⁽⁵⁾ / L1 / U1)
now also exercises:
- Q04 (both gate stages, ScipyGuard);
- Q06 certificate replay;
- Q08 radius-only equivalence;
- Q10 order-2 replay. R and R' at e = 0 are the quantities already published by 84aaa6a5; no order-3 or order-5
  object is formed.
- the shared `_CusumStack` methods. Candidate graded suprema must have wrong-parity components of about 0 on the
  parity-pure synthetic payloads. The constants must equal the registry, the hull base the binding x1, and the origin
  values the order-3 W / G payloads at (0,0).

In-process mutants P01–P04 of those methods must be detected.

**Other new mutation groups:**
- **A01–A03:** authorization-validator mutants, detected on synthetic bundles;
- **V01:** VOID sealing dropped, detected by the supervisor CPU-limit test.

**Retained:** E01–E16 with the same intent.
