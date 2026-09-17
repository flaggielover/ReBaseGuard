# P5Y K5 CUSUM: first governed real-cell probe (preregistration packet)

**Frozen pre-result. NOT authorized. NOT executed.** No real cell was evaluated and no `R'''` / `R⁽⁵⁾` value exists.

| File | Purpose |
|---|---|
| `PROTOCOL.md` | Human-readable preregistration: cell selection, object, hypothesis, verdicts, qualification, ladder, retry, address, K5-B map, cost, host, completion, authorization, executor status |
| `protocol/SCIENCE_PREREGISTRATION_R4.json` | **Authoritative** frozen protocol r4 (PROTOCOL_SHA256) |
| `protocol/EXECUTION_BINDING_R4.json`, `protocol/AUTHORIZATION_TEMPLATE_R4.json`, `protocol/FREEZE_RECORD_R4.json` | r4 executor binding (PENDING), authorization template (`EXECUTION_AUTHORIZED = false`), freeze record (published after the freeze) |
| `protocol/R3_SUPERSEDED.json` | r3 superseded before authorization (review FAIL on governance) |
| `protocol/SCIENCE_PREREGISTRATION_R3.json` | r3 (superseded, history only) |
| `protocol/EXECUTION_BINDING_R3.json`, `protocol/AUTHORIZATION_TEMPLATE_R3.json`, `protocol/FREEZE_RECORD_R3.json` | r3 (superseded, history only) |
| `protocol/R2_SUPERSEDED.json` | r2 superseded before authorization (review FAIL on governance) |
| `protocol/SCIENCE_PREREGISTRATION_R2.json` | r2 (superseded, history only) |
| `protocol/EXECUTION_BINDING_R2.json`, `protocol/AUTHORIZATION_TEMPLATE_R2.json` | r2 (superseded, history only) |
| `protocol/R1_SUPERSEDED.json` | r1 superseded before authorization (review FAIL on governance) |
| `protocol/SCIENCE_PREREGISTRATION.json` | r1 (superseded, history only) |
| `protocol/EXECUTION_BINDING.json`, `protocol/AUTHORIZATION_TEMPLATE.json`, `protocol/PACKET_MANIFEST.json` | r1 (superseded, history only) |
| `code/probe_rules.py` | Frozen pure rules: transport, three-way verdict, point sign, consequences, aggregate, K5-B map, address, qualification, retry, ladder |
| `code/prelaunch_verify.py` | Read-only fail-closed prelaunch verifier r4 (P01–P12, pinned publication anchor) |
| `tests/test_probe_protocol.py` | Unit tests on hypothetical inputs only |
| `review/` | r1–r3 static reviews (FAIL, governance) with host refusal reports; r4 host refusal report and static review (added after the r4 freeze) |
| `ledger/` | append-only attempt ledger (absent until a launch notice) |

```bash
python3 -B tests/test_probe_protocol.py
python3 -B code/prelaunch_verify.py        # expected: REFUSED, primary reason P01 EXECUTION_NOT_AUTHORIZED
```
