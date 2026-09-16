# P5Y K5: R2 repair successor of the real CUSUM signed order-3 producer

**Non-scientific, additive; R1 immutable.**
- No real CUSUM cell is evaluated and no `R'''` of any `(D,m)` is computed.
- There is no probe and no authorization: the real-cell and operator-certificate registries are frozen **empty**.

| File | Purpose |
|---|---|
| `R2_DESIGN.md` | R05 repair, cell-0 autopsy and exact budget, e = 0 structural audit, alternatives, graded method with proofs, unbuilt real wiring, point vs whole cell and K5-B, freeze discipline |
| `config/PRE_RESULT_GATES_R2.json`, `config/FEASIBILITY_CRITERION.json` | Frozen gates, verdict rule, feasibility categories and next-step rule |
| `config/QUALIFICATION_PROTOCOL_R2.json` | Frozen protocol: R1 retained verbatim, T25 R05 fixture, σ-fixtures, graded mutations, R1 byte pins, bound code |
| `config/ORDER3_PRODUCER_MANIFEST_R2.json` | R2 method trusted inputs |
| `config/REAL_CELL_AUTHORIZATION_REGISTRY.json`, `config/OPERATOR_CERTIFICATE_REGISTRY.json` | Empty, sha256 pinned in `code/cusum_graded.py` |
| `code/graded_dag.py` | Selected method: σ-graded certified error propagation (orders 0–3, midpoint and whole cell) |
| `code/sigma_systems.py` | Manufactured σ-symmetric chain systems, exact graded residuals and truth checks |
| `code/r05_fixture.py` | R05 isolating fixture and ablations |
| `code/cusum_graded.py` | Real graded range primitive and gated real front-end (wiring explicitly unbuilt) |
| `code/operator_parity_integration.py` | CUSUM Arb kernels at e = 0 on synthetic polynomials: parity structure |
| `code/e0_operator_estimate.py`, `evidence/e0_operator_estimate/` | NON-CERTIFIED float K₀ parity resolvent estimate (forecast input) |
| `code/cell0_forecast.py` | Cell-0 radius forecast and exact budget from committed K1 magnitudes |
| `code/qualify_r2.py`, `make_protocol_r2.py`, `make_manifest_r2.py` | Runner, protocol and manifest builders |
| `tests/test_r2.py` | Development tests |
| `evidence/qualification_r2/`, `RESULT.md` | Post-freeze qualification |

```bash
python3 -B tests/test_r2.py
# on rebaseguard-vultr-02, venv /root/work/rbg-cusum-aux5-venv, at the freeze commit:
python -B code/qualify_r2.py run   --outdir evidence/qualification_r2 --workers 4
python -B code/qualify_r2.py check --outdir evidence/qualification_r2
```
