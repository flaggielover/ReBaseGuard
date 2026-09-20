# Campaign B forecast r2 — measurement-anchored route scoring under the frozen gates

Generator `code/tail_forecast_r2.py`; output `TAIL_FORECAST_R2.json` (sha256 `0903715d…`). Classes and scenarios are
`config/FEASIBILITY_GATES_B.json`, frozen at `7ee92476` before any Campaign-B forecast and unmodified; they are
applied mechanically by `classify()`.

Every route is scored by running the **frozen K5-B** (`k5b_check.k5b_literal`, pin `ddd54dc4…`) on the full adopted
post-Campaign-A state over cells 0–309, so the chain route is included, not only the direct test. The state is
rebuilt from the pinned E6 adapter, the frozen loader, the adopted Perron consumer with certified registry r1 on
[0, 148], the adopted T-EXT C1/C2 channel and the **sealed** Campaign-A theorem-TC enclosures on cells 11–44. Replay
gate: with no tail route applied the pass ranges must equal the sealed Campaign-A consumption `1fa8d8de…` — they do,
for all four m.

**One premise supply for every route.** Since review r1 note N4, all four routes go through
`tct_rule.tail_enclosure` with the Lemma-G atom constants and the (P3′) σ₃/σ₄. (P3′) is a statement about the
*source* and is independent of the choice of Ĝ, so a route with a real order-3 candidate is entitled to it too;
scoring T2 on the unrefined tower while TCT0 had the refined one understated T2 by one cell.

| route | order-3 inputs | new real addresses | NOMINAL | CONSERVATIVE | class |
|---|---|---|---|---|---|
| `T2_AUDIT` | the frozen route comparison's own: s_G = \|Ĝ(a)\| = 10, s_H = 5, s_D = 2, s_F = 1, δ_G = 10⁻³ | 5 | 3/5 (305–307) | 0/5 | MARGINAL |
| `T2_AUDIT_MEAS` | the same order-3 inputs, on the measured adopted suprema | 5 | 4/5 (305–308) | 1/5 | MARGINAL |
| `T2_EVIDENCE` | s_G = max adopted s_G/s_H × measured s_H; \|Ĝ(a)\| = 0.681 s_G; δ_G = max adopted | 5 | 0/5 | 0/5 | INFEASIBLE |
| `TCT0` | **none — Ĝ := 0** (theorem TC-T) | **0** | 1/5 (305) | 1/5 (nothing estimated) | MARGINAL |

`T2_AUDIT` is a reconstruction of what the frozen route comparison forecast, **not a certified bound**: its assumed
s_F = 1 is below the measured candidate supremum for two objects (cells 305 and 306 at r = 0), so those rows would
not be valid enclosures (review r1 note N8). `T2_AUDIT_MEAS`, whose suprema are all measured, is the one to read for
the size of the effect. CONSERVATIVE multiplies every input the route does not measure by 4 in the unfavourable
direction, as the frozen gates define it — for `T2_AUDIT` that includes s_F, s_D and s_H, which are assumed there;
scoring only the order-3 inputs (as review-r1 r1 did) would give 1/5 instead of 0/5, i.e. would flatter the route
being refuted (note N3).

Selection under the frozen rules: every route is MARGINAL or INFEASIBLE ⇒
`verdict = STOP_AND_WRITE_COSTED_CONTINUATION_PLAN`. See `phase_c/EXECUTION_DECISION.md`.

The frozen route comparison recorded, for T2, "NOMINAL … 5/5 closed" and "CONSERVATIVE … 3/5 ⇒ USEFUL". Recomputed
at its own stated inputs the numbers are 3/5 and 0/5; with every supremum measured they are 4/5 and 1/5. USEFUL needs
NOMINAL = 5/5 or CONSERVATIVE ≥ 3/5, so **no reading reaches it**. The defect is in the arithmetic of the forecast,
not in the choice of estimate, and it is load-bearing: `selection_rule` forbids executing below USEFUL.

`critical_sup_G_over_sup_H_ratio` (exact bisection): 64.72, 47.99, 32.03, 19.20, **10.55** for cells 305…309 — the
largest tail order-3 candidate supremum, as a multiple of the measured order-2 supremum, at which T2 still closes
each cell. The adopted lower-front value of that ratio is 34.8–80.5, i.e. cell 309 needs the tail ratio to be 3.3–7.6×
smaller than anything the campaign has measured.

`atom_constant_requirement` / `ATOM_CONSTANT_REQUIREMENT.json`: with Ĝ := 0 the same cells close once the atom
constants fall uniformly by 1.000×, 1.071×, 1.362×, 1.771×, **2.253×** (or A0 alone by 1.000×, 1.091×, 1.502×,
2.206×, **3.294×**). This is the input to continuation route C1.
