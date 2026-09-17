# P5Y K5: R4 tightening successor of the CUSUM signed order-3 producer

**Non-scientific, additive; R1, R2 and R3 immutable (pinned file by file).**
- No real CUSUM cell is evaluated and no `R'''` or `R⁽⁵⁾` value of any `(D,m)` is computed.
- There is no probe. The real-cell authorization registry is frozen **empty**.

| File | Purpose |
|---|---|
| `R4_DESIGN.md` | B01 test-power fixtures, C_o0 architecture comparison and exact odd-block theorem, R⁽⁵⁾ routes and local anchoring lemma, forecast / grid / blocker rules, qualification, real-cell policy |
| `config/operator_certificates/C_o0_odd_block_certificate.json` | Exact odd-block supersolution artifact (payload + recomputable certified numbers) |
| `config/OPERATOR_CERTIFICATES_R4.json` | C_o0 (R4) and C_e0 (R3 artifact), sha256 pinned in `code/constants_r4.py` |
| `config/REAL_CELL_AUTHORIZATION_REGISTRY_R4.json` | Empty, sha256 pinned |
| `config/PRE_RESULT_GATES_R4.json`, `config/FEASIBILITY_CRITERION_R4.json` | Frozen gates G01–G17, verdict / B1 / next-step rules, classes, grid, blocker rule |
| `config/QUALIFICATION_PROTOCOL_R4.json` | Frozen protocol: fixtures, mutations, controls, seeds, R1/R2/R3 pins, bound code and config |
| `code/odd_block_certificate.py`, `code/odd_block_crosscheck.py`, `code/operator_audit.py` | Certified C_o0, independent float cross-check, architecture audit (non-evidence) |
| `code/local_r5.py`, `code/first_cell_r4.py`, `code/m5_crosscheck.py` | Local first-cell R⁽⁵⁾ majorant, manufactured Strategy B against exact truth, independent Cauchy/acb derivatives |
| `code/constants_r4.py`, `code/forecast_r4.py` | Certified constant loading with fail-closed real entry; cell-0 forecast and sensitivity grid |
| `code/qualify_r4.py`, `code/make_protocol_r4.py` | Runner (PID/marker completion) and protocol builder |
| `tests/test_r4.py` | Development tests |
| `evidence/qualification_r4/`, `RESULT.md` | Post-freeze qualification |

```bash
python3 -B tests/test_r4.py
# on rebaseguard-vultr-02, venv /root/work/rbg-cusum-aux5-venv, at the freeze commit:
python -B code/qualify_r4.py run   --outdir evidence/qualification_r4 --workers 4
python -B code/qualify_r4.py check --outdir evidence/qualification_r4
```
