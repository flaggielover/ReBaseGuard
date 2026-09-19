# Campaign A, Phase A — lower-front blocker audit (deterministic reuse only)

Start frontier `p5y-postk1-frontier` @ `7cb01e38` (verified on GitHub at session start). Nothing outside this namespace is
modified. No model quantity is computed here.

`LOWER_FRONT_BLOCKER_MAP.json` (built by `code/lower_front_blocker_map.py`, sha256 in `phase_a/SHA256SUMS`) replays the
frozen Theorem K5-B (`k5b_check.k5b_literal`, ddd54dc4) on the sealed, ADOPTED Perron-deflated consumption
(`DEFLATED_CONSUMPTION.json`, 5dcc9b7d) for cells 0–159 and every m, with the adopted T-EXT channel Λ(k) (via the pinned
`text_consume.text_objects`) and the sealed slot-1 L1. The replay reproduces the sealed `via` of every cell 0–159 and the
sealed open set exactly (the script refuses otherwise), and the open sets equal coverage map r3. 122 rows, one per open
lower-front (m, cell) pair.

## What fails, per m (all values FLOAT renderings of exact rationals in the map)

| m | open | H.lo = certified lower end of R'' on the cell | Γ_k (direct test) | R point radius | R'' whole-cell radius | ρ·x·M |
|---|---|---|---|---|---|---|
| 1 | 11–35 (25) | −293 … −252 | +1.2e-4 … +2.8e-3 | 1.9e-3 | 266 – 336 | 4.6e-4 – 2.2e-3 |
| 2 | 11–41 (31) | −223 … −183 | +4.4e-4 … +4.5e-3 | 3.5e-3 | 195 – 265 | 3.4e-4 – 2.2e-3 |
| 3 | 11–42 (32) | −184 … −150 | +2.9e-4 … +4.4e-3 | 3.5e-3 | 160 – 223 | 2.8e-4 – 1.9e-3 |
| 5 | 11–44 (34) | −143 … −113 | +9.1e-5 … +4.3e-3 | 3.4e-3 | 122 – 179 | 2.2e-4 – 1.7e-3 |

The blocker is **the same predicate pair at every open cell, with two sub-cases**:

1. **Cell 11 (every m):** the chain arrives with γ_10 < 0 (m=1: −1.28e-5, m=5: −7.4e-6) but μ_11 = H_11.lo (−32.3,
   −25.5, −21.9, −17.9 for m = 1, 2, 3, 5) because the T-EXT channel is already hugely negative (Λ(10) ≈ −1.9e4 … −1.1e4,
   so ℓ collapses to H.lo). Then U_11 = γ_10 − μ_11·(x_11² − x_10²)/2 > 0. The direct test also fails (Γ_11 > 0).
2. **Cells 12 … K_m:** γ_{k−1} ≥ 0 (the chain is broken at cell 11 and γ_k = min(…, Γ_k) stays positive), and Γ_k > 0.

Why the direct test cannot pass here: |g(e)| ≈ (R'''(0)/3)e³ is 1.3e-4 (m=1, cell 11) … 9e-3 (cell 44), while the
certified point radius of R alone is 1.9e-3 (m=1) / 3.4–3.5e-3 (m ≥ 2). This is the order-0 floor E_a[τ]·‖residual‖ of
Lemma SM(d) (the Perron campaign's §5); no deflation removes it.

Why the chain cannot pass here: the only certified lower bounds on R'' over a lower-front cell are the whole-cell K1
enclosures after theorem AD, whose radius (122–336) is dominated by **ρ-terms of constant-in-e candidates** propagated
through the order-1/2 channel constants: at cell 11 (m=1, r=0) the radius 266 splits as A2·f_F^cell ≈ 169,
2A1·f_D^cell ≈ 95, A0·f_H^cell ≈ 1.7, where f_X^cell = δ_mid + ρ·Env is the whole-cell residual of the e-constant
candidate. The midpoint residuals themselves are small (δ_mid(F_0) = 3.7e-6, δ_mid(dF_0) = 7.9e-5, δ_mid(H_0) = 1.2e-4).

## Margin needed

- **Chain (sufficient uniform rule):** a certified R'' lower bound H.lo ≥ 0 on every cell 11..K_m. Then μ_k ≥ 0 and
  U_k = γ_{k−1} ≤ γ_10 < 0 for all k (γ is non-increasing), so each cell passes; cells ≥ K_m + 1 keep passing because the
  frozen K5-B is monotone under tighter valid enclosures. The per-row field `H_lo_increase_needed_for_uniform_rule` is
  −H.lo (113 … 293).
- **Direct:** Γ_k must drop below 0; needed reductions are listed per row (9e-5 … 4.5e-3), i.e. R point radii below
  |g| — 20–40× better point accuracy at cell 11. Not a realistic target.
- **Order-3 channel (alternative sufficient form):** certified L_k ≥ 0 on cells 1..K_m (T-EXT-style), equivalently a
  sup |R⁽⁵⁾| majorant M5 on [0, x_hi(K_m)] small enough that the ℓ-accumulation stays ≥ 0 (quantified in
  `../phase_b/ROUTE_COMPARISON.md`).

## Information available beyond e = 0

- R'''(0) ∈ [L0, U0]: m=1 [1801.4, 2790.4], m=2 [1461.6, 2410.4], m=3 [1307.1, 2201.0], m=5 [1074.0, 1931.0] (slot-1).
- T-EXT M_n(hull) for n = 2..5, hulls 0..40 (certified): M5 = 1.06e8 (hull 0), 2.8e10 (hull 10), 3.6e19 (hull 40);
  Λ(k) < 0 from cell ≈ 9 on.
- No certified R''' or R⁽⁴⁾/R⁽⁵⁾ information at any e > x_hi(40); no order-3 object at any e ≠ 0.
- NON-CERTIFIED diagnostic (float least squares on the midpoints of the adopted K1 R and R' enclosures, cells 0–159,
  odd polynomial of degree 9–11; no model evaluation): R'''(0) ≈ 2.29e3, R⁽⁵⁾(0) ≈ −1.3e6, R⁽⁷⁾(0) ≈ +1.3e9 (m=1);
  ≈ 1.50e3, −8.4e5, +8.4e8 (m=5). So the true R'' on the lower front is ≈ 13–57 (m=1) and ≈ 9–37 (m=5): the obstacle
  is certification width, not the sign. This diagnostic is never evidence.
