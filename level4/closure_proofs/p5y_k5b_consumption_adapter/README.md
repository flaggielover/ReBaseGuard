# K5-B consumption adapter (authorization prerequisite E6)

This namespace closes authorization prerequisite **E6** of
`p5y_k5_cusum_first_real_probe_protocol/protocol/EXECUTION_BINDING_R4.json`: implement the K5-B consumption adapter and
pass its frozen acceptance test (reproduce the CUSUM_MINIMALITY_R1 pass sets with L = None).

It is additive and composes two frozen components without editing either:
- the readiness loader `k5_minimality.py` (`3a54f0fb…`);
- the countersigned theorem checker `k5b_check.k5b_literal` (`ddd54dc4…`).

Nothing here is authorized to execute, and no real R''' or R^(5) is read or formed.

| file | role |
|---|---|
| `E6_SPEC.md` | specification, committed before any adapter code |
| `config/E6_ACCEPTANCE_PROTOCOL.json` | frozen acceptance protocol, with the expected pass sets, pins and gates |
| `code/consumption_adapter.py` | the adapter: frozen loader → frozen `k5b_literal`, per m; fail-closed |
| `code/crosscheck.py` | independent cross-check: frozen scan reproduction (X-A), plus manifest-addressed records with the frozen readiness variant (X-B) |
| `code/acceptance.py` | frozen acceptance run and read-only `check` (gates G01–G09, mutants M01–M14) |
| `evidence/acceptance_r1/`, `RESULT.md` | frozen acceptance run (ACCEPTED, 9/9 gates, 14/14 mutants) and result |
| `tests/test_adapter.py` | local synthetic tests (no K1 record is read) |

```bash
python3 -B tests/test_adapter.py
# on rebaseguard-vultr-02, at a clean checkout of the implementation commit:
python3 -B code/acceptance.py run   --outdir evidence/acceptance_r1
python3 -B code/acceptance.py check --outdir evidence/acceptance_r1
```
