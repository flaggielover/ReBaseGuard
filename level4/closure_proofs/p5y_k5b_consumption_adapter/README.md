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
