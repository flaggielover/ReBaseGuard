# Campaign B forecast r2 — measurement-anchored route scoring under the frozen gates

Generator `code/tail_forecast_r2.py`; output `TAIL_FORECAST_R2.json` (sha256 `82afcbba…`, two generations
byte-identical). Classes and scenarios are `config/FEASIBILITY_GATES_B.json`, frozen at `7ee92476` before any
Campaign-B forecast and unmodified; they are applied mechanically by `classify()`.

Every route is scored by running the **frozen K5-B** (`k5b_check.k5b_literal`, pin `ddd54dc4…`) on the full adopted
post-Campaign-A state over cells 0–309, so the chain route is included, not only the direct test. The state is
rebuilt from the pinned E6 adapter, the frozen loader, the adopted Perron consumer with certified registry r1 on
[0, 148], the adopted T-EXT C1/C2 channel and the **sealed** Campaign-A theorem-TC enclosures on cells 11–44. Replay
gate: with no tail route applied the pass ranges must equal the sealed Campaign-A consumption `1fa8d8de…` — they do,
for all four m.

| route | order-3 inputs | new real addresses | NOMINAL | CONSERVATIVE | class |
|---|---|---|---|---|---|
| `T2_AUDIT` | the frozen route comparison's own: s_G = 10, s_H = 5, δ_G = 10⁻³ | 5 | 3/5 (305–307) | 1/5 | MARGINAL |
| `T2_AUDIT_MEAS` | the same, on the measured adopted suprema | 5 | 3/5 (305–307) | 1/5 | MARGINAL |
| `T2_EVIDENCE` | s_G = max adopted s_G/s_H × measured s_H; \|Ĝ(a)\| = 0.681 s_G; δ_G = max adopted | 5 | 0/5 | 0/5 | INFEASIBLE |
| `TCT0` | **none — Ĝ := 0** (theorem TC-T) | **0** | 1/5 (305) | 1/5 (nothing estimated) | MARGINAL |

Selection under the frozen rules: every route is MARGINAL or INFEASIBLE ⇒
`verdict = STOP_AND_WRITE_COSTED_CONTINUATION_PLAN`. See `phase_c/EXECUTION_DECISION.md`.

The frozen route comparison recorded, for T2, "NOMINAL … 5/5 closed" and "CONSERVATIVE … 3/5 ⇒ USEFUL". Recomputed
exactly at its **own** stated inputs the numbers are 3/5 and 1/5, i.e. class MARGINAL. The defect is therefore in the
arithmetic of the forecast, not in the choice of estimate, and it is load-bearing: `selection_rule` forbids executing
below USEFUL.

`critical_sup_G_over_sup_H_ratio` (exact bisection): 60.18, 43.23, 27.13, 14.24, **5.47** for cells 305…309 — the
largest tail order-3 candidate supremum, as a multiple of the measured order-2 supremum, at which T2 still closes each
cell. The adopted lower-front value of that ratio is 34.8–80.5.

`ATOM_CONSTANT_REQUIREMENT.json`: with Ĝ := 0 the same cells close once the atom constants A0, A1, A2 fall uniformly
by 1.00×, 1.053×, 1.335×, 1.731×, 2.195× (or A0 alone by 1.00×, 1.068×, 1.462×, 2.132×, 3.153×). This is the input to
continuation route C1 (an operator-only certified registry extension to the tail, zero new real addresses).
