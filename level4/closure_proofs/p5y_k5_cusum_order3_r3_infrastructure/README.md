# P5Y K5: R3 infrastructure successor of the CUSUM signed order-3 producer

**Non-scientific, additive; R1 and R2 immutable (pinned file by file).**
- No real CUSUM cell is evaluated and no `R'''` of any `(D,m)` is computed.
- There is no probe. The real-cell authorization registry is frozen **empty**.

| File | Purpose |
|---|---|
| `R3_DESIGN.md` | C_o0 / C_e0 theorems and certification, real graded wiring, He₆ extension, first-cell strategies A and B, R⁽⁵⁾ source audit, forecast method |
| `config/operator_certificates/*.json` | Certified supersolution artifacts (exact payload + recomputable certified numbers) |
| `config/OPERATOR_CERTIFICATES_R3.json` | Certificate registry (sha256 pinned in `code/graded_real.py`) |
| `config/REAL_CELL_AUTHORIZATION_REGISTRY_R3.json` | Empty, sha256 pinned in `code/graded_real.py` |
| `config/PRE_RESULT_GATES_R3.json`, `config/FEASIBILITY_CRITERION_R3.json` | Frozen gates R01–R17, verdict / B1 rules, forecast classes, next-step rule |
| `config/QUALIFICATION_PROTOCOL_R3.json` | Frozen protocol: mutations, fixtures, seeds, R1/R2 pins, bound code |
| `code/resolvent_certificate.py` | Certified σ-odd (`C_o0`) and whole-space (`C_e0`) resolvent bounds at e = 0 |
| `code/hermite6_ext.py` | He₆ roots, `j_5`, `k_6`, `sup|S_0^(5)|` (separate artifact; frozen table unchanged) |
| `code/graded_real.py` | Real CUSUM σ-graded residual/error wiring on the frozen Arb stack; fail-closed gated entry point |
| `code/synthetic_real.py` | Synthetic parity-pure candidates through the real Arb operator path (non-scientific) |
| `code/r5_majorant.py`, `code/first_cell.py` | Strategy B evenness transport, anchored graded R⁽⁵⁾ tower, Strategy A vs B on manufactured odd systems |
| `code/cell0_forecast_r3.py` | Cell-0 forecast from committed magnitudes and certified constants (no R''' value) |
| `code/qualify_r3.py`, `code/make_protocol_r3.py` | Runner and protocol builder |
| `tests/test_r3.py` | Development tests |
| `evidence/qualification_r3/`, `RESULT.md` | Post-freeze qualification |

```bash
python3 -B tests/test_r3.py
# on rebaseguard-vultr-02, venv /root/work/rbg-cusum-aux5-venv, at the freeze commit:
python -B code/qualify_r3.py run   --outdir evidence/qualification_r3 --workers 4
python -B code/qualify_r3.py check --outdir evidence/qualification_r3
```
