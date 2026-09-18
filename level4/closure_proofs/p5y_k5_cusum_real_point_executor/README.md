# P5Y K5 CUSUM: real point executor (build and qualify; not authorized)

**Scope.**
- **Objective:** BUILD_AND_QUALIFY_REAL_POINT_EXECUTOR. It repairs blocker E of the first real-probe protocol, whose
  science preregistration is preserved byte for byte.
- **Nothing real is computed:** REAL_INPUT_ARITHMETIC_GUARD = DENY, EXECUTION_AUTHORIZED = false, no real K1 cell is
  executed, and no real R''', R⁽⁵⁾, L1 or U1 is formed.
- **Trust:** the local host is not a trust root (`TRUST_MODEL.md`).

| File | Purpose |
|---|---|
| `EXECUTOR_SPEC.md` | Interface and pipeline, committed before implementation (`ac555bf2`) |
| `EXECUTOR_SPEC_R2.md` | r2 addendum after the r1 static review FAIL (`6a1adbfe`), committed before the repair code |
| `review/EXECUTOR_STATIC_REVIEW_R1.md` | r1 review (FAIL), preserved |
| `review/EXECUTOR_STATIC_REVIEW_R2.md` | r2 review (FAIL: D1–D4), preserved |
| `EXECUTOR_SPEC_R3.md` | r3 addendum repairing D1–D4 (`a5d63e71`), committed before the repair code |
| `EXECUTOR_SPEC_R4.md` | r4 addendum repairing N1–N3 (`b0e3f6c6`), committed before the repair code |
| `EXECUTOR_SPEC_R5.md` | r5 addendum closing X1: one canonical launch slot (`59bd3268`), committed before the repair code |
| `code/qualify_governed.py` | r4 synthetic governed launch end to end (frozen verifier PASS -> slot -> RUN_STATE -> child re-check -> seal -> RUN_COMPLETE -> ledger), in a private mount namespace |
| `TRUST_MODEL.md` | The five separated stages; trusted assumptions; no cryptographic claim |
| `code/executor_core.py` | Guard (DENY / EXTERNAL_AUTHORIZATION), context validation, shared stages, enclosure/M5/transport, preregistered Q01–Q16 gates, attempt events, VOID sealing, SIGXCPU, exact serialization, atomic seal (certificates only) |
| `code/authorization_interface.py` | Real-mode authorization (prepared, inactive): the frozen `prelaunch_verify.verify` called in process, the executor binding and a countersignature as a second requirement (not a cryptographic authority) |
| `code/supervisor.py`, `code/executor_cli.py` | Attempt supervisor in `<output_namespace>/slot-N` (RLIMIT_CPU, wall watchdog, frozen `failure_class`, exactly one terminal marker) with its reboot-recovery mode, and the executor child process |
| `code/lifecycle.py` | The frozen slot marker contract: atomic no-overwrite writes, A–E slot classification, OUTCOME derivation, ledger reconciliation |
| `code/qualify_d1d4.py` | r3 qualification suites for D1 (in-process prelaunch), D2 (lifecycle and ledger), D3 (recovery) and D4 (provenance) |
| `code/backends.py` | `CusumPointBackend` (production, guarded), `SyntheticCusumSmokeBackend` (real Arb stages, synthetic candidates), `ManufacturedPointBackend` (exact truth); shared Q-gate helpers (Aux5 production gate, certificate replay, graded/scalar consistency, order-2 cross replay) |
| `code/input_adapters.py` | `RealInputAdapter` (metadata only, R1 V01–V10, payload redacted) and `ManufacturedInputAdapter` |
| `code/qualification_gates.py`, `code/consumer.py` | Sign-independent gates; the separate consumer that alone applies the frozen verdict rules |
| `code/smoke.py` | Real-stage smoke that stops before any enclosure; Q04/Q06/Q08/Q10 on the real stack; production-stack mutants P01–P04; order-2 reference replay |
| `code/exec_fixtures.py`, `code/qualify_executor.py`, `code/make_protocol_executor.py` | Truth, qualification runner (PID/marker completion), protocol builder |
| `config/REAL_INPUT_GUARD.json` | `{"policy": "DENY"}` (the only file activation changes; outside the executor identity and pins) |
| `config/EXECUTOR_PINS.json` | sha256 of every byte the real path and its gates depend on (Q05 / Q13) |
| `config/EXTERNAL_AUTHORIZATION_TEMPLATE.json` | Result-blind authorization for an independent countersigner (INACTIVE) |
| `config/EXECUTOR_QUALIFICATION_PROTOCOL.json`, `config/FIXTURE_LIMITS.json` | Frozen qualification protocol and DEV-calibrated M5 ratio limits |
| `tests/test_executor.py` | Static development tests |
| `evidence/qualification/` | r1 frozen qualification (preserved) |
| `evidence/qualification_r2/` | r2 frozen qualification (preserved) |
| `RESULT.md` | r2 result (preserved) |
| `review/EXECUTOR_STATIC_REVIEW_R3.md` | r3 review (FAIL: D1 open; D2–D4 closed) |
| `evidence/qualification_r3/`, `RESULT_R3.md` | r3 frozen qualification (with `RUN_PROVENANCE.json`) and result |
| `review/EXECUTOR_STATIC_REVIEW_R4.md` | r4 review (FAIL on new X1; N1–N3 and D1–D4 closed) |
| `evidence/qualification_r4/`, `RESULT_R4.md` | r4 frozen qualification and result |
| `evidence/qualification_r5/`, `RESULT_R5.md` | r5 frozen qualification and result |
| `review/EXECUTOR_STATIC_REVIEW_R5.md` | r5 review (PASS_WITH_SCOPE_LIMITATION; X1, N1–N3 and D1–D4 closed) |

```bash
python3 -B tests/test_executor.py
# on rebaseguard-vultr-02, venv /root/work/rbg-cusum-aux5-venv, at the freeze commit:
python -B code/qualify_executor.py run   --outdir evidence/qualification_r5 --workers 4
python -B code/qualify_executor.py check --outdir evidence/qualification_r5
```
