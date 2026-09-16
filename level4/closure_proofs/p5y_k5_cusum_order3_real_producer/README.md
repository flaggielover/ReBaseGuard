# P5Y K5: real CUSUM signed order-3 producer, implementation and non-scientific qualification

**Not a K5 probe, not a production run, not an authorization.**
- No real CUSUM cell is evaluated and no `R'''` of any `(D,m)` is computed.
- K1 records, the CUSUM closure, K5-B, its countersignature, the premise-binding audit and the order-3 design are
  unchanged.
- SR is out of scope (B2).

| File | Purpose |
|---|---|
| `DESIGN_REAL.md` | Identity audit, real derivation chain, Aux3 autopsy, implementation, whole-cell soundness proof, K1 inputs, cell-0 width forecast, governance |
| `config/PRE_RESULT_GATES.json` | G01–G16 and the verdict rule, frozen before any qualification result |
| `config/QUALIFICATION_PROTOCOL.json` | Frozen protocol (fixtures, mutations, precision, cross-check, fail-closed, fences, bound code sha256) |
| `config/ORDER3_PRODUCER_MANIFEST.json` | Order-3 producer trusted inputs by exact path |
| `config/REAL_CELL_AUTHORIZATION_REGISTRY.json` | Frozen **empty**; pinned in `cusum_order3.py` |
| `code/rung3_engine.py`, `code/rung3_residual.py` | Arb engine and new-rung residual |
| `code/cusum_order3.py` | Real CUSUM front-end (gated; never entered here) |
| `code/k1_inputs.py` | Fail-closed K1 record validation (V01–V10, target gate for every m) |
| `code/manufactured_chain.py`, `fixtures.py`, `soundness.py`, `run_fixture.py` | Manufactured chain systems with exact truth |
| `code/reference_differential.py` | Arb engine vs the frozen exact-rational reference kernel |
| `code/independent_crosscheck.py` | Independent rational-function whole-cell enclosure |
| `code/real_operator_integration.py` | CUSUM Arb kernels on synthetic polynomials vs float quadrature |
| `code/qualify_order3.py`, `make_protocol.py`, `make_manifest.py` | Runner, protocol and manifest builders |
| `tests/test_order3_producer.py` | Development unit tests |
| `evidence/qualification_r1/`, `RESULT.md` | Post-freeze qualification evidence |

```bash
python3 -B tests/test_order3_producer.py
# on rebaseguard-vultr-02, venv /root/work/rbg-cusum-aux5-venv, at the freeze commit:
python -B code/qualify_order3.py run   --outdir evidence/qualification_r1 --workers 4
python -B code/qualify_order3.py check --outdir evidence/qualification_r1
```
