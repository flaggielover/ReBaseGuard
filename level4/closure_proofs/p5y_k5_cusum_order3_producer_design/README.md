# P5Y K5: CUSUM signed order-3 producer, design and non-scientific qualification

**Not a producer run, not a K5 probe, not an authorization.** Nothing here computes `R'''` for any `(D,m)`, reads
any K1 record, or uses any host. The authoritative K5 state stays `e8680998` (`NOT_READY`).

| File | Purpose |
|---|---|
| `DESIGN.md` | Objects, certified rules with proofs, export schema, qualification ladder L0–L5, open owner decisions, risk |
| `config/QUALIFICATION_PROTOCOL.json` | QN1–QN6, `FROZEN_PRE_RESULT`; trials first executed after the freeze commit |
| `code/order3_algebra.py` | Exact-rational reference kernel for DESIGN §3 |
| `code/manufactured.py` | Manufactured analytic systems with exact derivatives |
| `code/qualify_nonscientific.py` | Runs and replays the protocol |
| `tests/test_order3_algebra.py` | Development unit tests (seeds disjoint from the protocol) |
| `evidence/qualification_r1/` | Written only by the post-freeze run |

```bash
python3 -B tests/test_order3_algebra.py
python3 -B code/qualify_nonscientific.py run   --out      evidence/qualification_r1/QUALIFICATION_RESULT.json
python3 -B code/qualify_nonscientific.py check --evidence evidence/qualification_r1/QUALIFICATION_RESULT.json
```
