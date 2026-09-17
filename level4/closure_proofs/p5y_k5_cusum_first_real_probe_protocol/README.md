# P5Y K5 CUSUM: first governed real-cell probe (preregistration packet)

**Frozen pre-result. NOT authorized. NOT executed.** No real cell was evaluated and no `R'''` / `R⁽⁵⁾` value exists.

| File | Purpose |
|---|---|
| `PROTOCOL.md` | Human-readable preregistration: cell selection, object, hypothesis, verdicts, qualification, ladder, retry, address, K5-B map, cost, host, completion, authorization, executor status |
| `protocol/SCIENCE_PREREGISTRATION.json` | Authoritative frozen protocol (PROTOCOL_SHA256) |
| `protocol/EXECUTION_BINDING.json` | Executor binding: PENDING (no qualified real Strategy-B executor exists yet) |
| `protocol/AUTHORIZATION_TEMPLATE.json` | Authorization object template, `EXECUTION_AUTHORIZED = false` |
| `protocol/PACKET_MANIFEST.json` | sha256 of every packet file (checked by prelaunch P04) |
| `code/probe_rules.py` | Frozen pure rules: transport, three-way verdict, point sign, consequences, aggregate, K5-B map, address, qualification, retry, ladder |
| `code/prelaunch_verify.py` | Read-only fail-closed prelaunch verifier (P01–P11) |
| `tests/test_probe_protocol.py` | Unit tests on hypothetical inputs only |
| `review/` | Prelaunch refusal evidence and independent static review (added after the freeze commit) |

```bash
python3 -B tests/test_probe_protocol.py
python3 -B code/prelaunch_verify.py        # expected: REFUSED, primary reason P01 EXECUTION_NOT_AUTHORIZED
```
