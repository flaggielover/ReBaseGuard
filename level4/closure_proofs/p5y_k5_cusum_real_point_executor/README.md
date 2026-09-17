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
| `TRUST_MODEL.md` | The five separated stages; trusted assumptions; no cryptographic claim |
| `code/executor_core.py` | Guard, context validation, shared stages, enclosure/M5/transport, exact serialization, atomic seal (certificates only) |
| `code/backends.py` | `CusumPointBackend` (production, guarded), `SyntheticCusumSmokeBackend` (real Arb stages, synthetic candidates), `ManufacturedPointBackend` (exact truth) |
| `code/input_adapters.py` | `RealInputAdapter` (metadata only, R1 V01–V10, payload redacted) and `ManufacturedInputAdapter` |
| `code/qualification_gates.py`, `code/consumer.py` | Sign-independent gates; the separate consumer that alone applies the frozen verdict rules |
| `code/smoke.py` | Real-stage smoke that stops before any enclosure |
| `code/exec_fixtures.py`, `code/qualify_executor.py`, `code/make_protocol_executor.py` | Truth, qualification runner (PID/marker completion), protocol builder |
| `config/REAL_INPUT_GUARD.json` | `{"policy": "DENY"}` |
| `config/EXTERNAL_AUTHORIZATION_TEMPLATE.json` | Result-blind authorization for an independent countersigner (INACTIVE) |
| `config/EXECUTOR_QUALIFICATION_PROTOCOL.json`, `config/FIXTURE_LIMITS.json` | Frozen qualification protocol and DEV-calibrated M5 ratio limits |
| `tests/test_executor.py` | Static development tests |
| `evidence/qualification/`, `RESULT.md` | Frozen qualification and result |

```bash
python3 -B tests/test_executor.py
# on rebaseguard-vultr-02, venv /root/work/rbg-cusum-aux5-venv, at the freeze commit:
python -B code/qualify_executor.py run   --outdir evidence/qualification --workers 4
python -B code/qualify_executor.py check --outdir evidence/qualification
```
