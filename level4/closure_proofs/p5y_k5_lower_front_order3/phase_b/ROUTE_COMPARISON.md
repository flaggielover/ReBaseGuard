# Campaign A, Phase B — mechanism search and route comparison

All numbers are FORECASTS (`evidence/forecast_r1/ROUTE_FORECAST.json`, built by `code/route_forecast.py` from adopted
evidence only; no model evaluation). Classes follow the gates frozen and published at `e89b33f2`
(`config/FEASIBILITY_GATES_A.json`) before any forecast: a pair (m, cell) counts as closed only if the frozen K5-B passes it.

## What any route must deliver (from Phase A)

The frozen K5-B chain carries from γ_10 < 0 through the whole lower front as soon as every cell 11..K_m has a certified
lower bound μ_k ≥ 0 for R'' on the cell. Equivalently (T-EXT form) a certified order-3 channel L_k with ℓ_k ≥ 0. The
direct test is out of reach (order-0 floor, Phase A).

## Routes investigated

| route | mechanism | ruled out before forecasting? |
|---|---|---|
| A | direct R''' transport with R'''' bounds: R'''(e) ≥ R'''(0) − e·M4 | dominated by B (M4 ≈ e·M5 carries one order less of smallness); T-EXT R4 already rejected it at cell 0 (DEV budget 8.9e3 vs 6.1e2) |
| B / C / D | evenness (Taylor) transport from e = 0 with an R⁽⁵⁾ majorant; graded odd/even tower (R4 local_r5); atom-deflated tower | forecast as **D** |
| E / F | recurrence-level / interval-ODE propagation in e | no finite closed system exists for R at the atom: every e-derivative of ν_e(S_e)/D_e brings a new operator derivative; any propagation reduces to norm towers of F⁽ⁿ⁾, i.e. to D |
| G | deterministic reuse: theorem AD at the **midpoint** for R'' (records' δ_mid) + best certified M3 | forecast as **G** |
| H | sparse positive-e R''' anchors + local M4 transport | forecast as **H** |
| I (TC) | Taylor-in-e candidate within each cell + theorem AD, with one new order-3 midpoint candidate per (cell, r) | forecast as **TC** |

Also considered and rejected with a quantitative reason (not a class): a complex-drift Cauchy estimate of R⁽⁵⁾ or of the
Taylor remainder of R'' on [0, 0.025]. The pole of 1/D_e near e ≈ ±0.17i limits the radius to ≈ 0.12–0.15, and even
the TRUE max|R| on such circles (≈ 2–4) gives a remainder bound 5–9× the true one, which fails for m = 5 before any
certification loss (it would also need new complex-drift real evaluations).

## Quantitative comparison

| | D (deflated order-5 tower) | G (midpoint R'' + M3) | H (sparse anchors) | TC (Taylor-cell, order-3 candidates) |
|---|---|---|---|---|
| theorem | R'''(e) ≥ L0 − ∫(e−t)R⁽⁵⁾ (T-EXT corollary) with a new M5 | R''(e) ≥ R''(e0) − ρ·M3; R''(e0) by theorem AD at e0 | R'''(e) ≥ R'''(e_a) − \|e − e_a\|·M4 | theorem TC (`../theorem/THEOREM_TC.md`): AD applied to the Taylor residual φ(e) of F̃ = F̂ + tD̂ + t²Ĥ/2 + t³Ĝ/6 |
| regularity | R ∈ C⁵ (P5X L5, R real-analytic) | R ∈ C³ | R ∈ C⁴ | e ↦ K_e, S_r(e) analytic into B(X) (Lemma K; sources closed form or J_e h_r); R ∈ C² suffices for K5-B |
| derivative order | 5 (sup) | 3 (sup) | 4 (sup) + 3 (point) | 2 (whole cell) + 3 (midpoint candidate only) + 4 (norm envelope × ρ²) |
| certified constants | a new tower (does not exist) | A0, A1, A2 (registry r1), T-EXT M3 | T-EXT M4; an order-3 point executor at e ≠ 0 (does not exist) | A0, A1, A2 (registry r1, adopted); drift-aware k_i, j_i (frozen K1); candidate sups (Bernstein) |
| reused evidence | slot-1, T-EXT | K1 records, registry r1, T-EXT | slot-1, T-EXT | registry r1, adopted deflated consumption, frozen K1/Aux3/order-3 producers |
| new real addresses | 0 | 0 | ≥ 1 per cell | 34 cell midpoints (cells 11–44), orders ≤ 3, r = 0..4 |
| forecast new-real CPU-h | 0 | 0 | not forecastable (no producer) | 9.0 (+0.5 for a 2-cell reproduction) |
| forecast wall time | — | — | — | ≈ 1.5–2 h on 7 vultr-02 workers |
| closed pairs NOMINAL / CONSERVATIVE | 42 / 5 of 122 | 0 / 0 | 0 / 0 | **122 / 122** |
| dominant error | M5 itself: the required uniform M5 is 4.2e7 (m1), 2.5e7 (m2), 2.1e7 (m3), 1.6e7 (m5); the best certified M5 anywhere (hull 0, η = 5e-4) is 1.06e8 / 9.2e7 / 8.4e7 / 7.3e7, i.e. 2.5–4.7× too large **with zero hull growth**; the certified value at the needed hull is 1.7e8 … 8e11× too large | ρ·M3 = 113 … 5e8 against R'' ≈ 9–50 | anchor radius 1e-5 … 3e-13 against cell half-width 2.7e-4 (25 anchors per cell at cell 11) | A2·f_F^mid + 2A1·f_D^mid (theorem-AD order-2 point error ≈ 3.4–5), all from adopted K1 residuals |
| safety margin | — | — | — | min H.lo: NOMINAL 9.5 / 6.2 / 5.3 / 4.0; CONSERVATIVE 7.3 / 4.3 / 3.6 / 2.5 (m = 1, 2, 3, 5; always at cell 11) |
| expected failure mode | the one C_e0 factor of the anchored tower is already sharp (C_e0 ≈ E_a[τ]); deflation removes products of channels, not this floor, and the norm bounds of K_i on channel-shaped functions keep the 50–80× gap to the true R⁽⁵⁾ ≈ 1.3e6 | M3 explodes past hull 6 | no certified M4 at e ≠ 0 | a runtime that does not reproduce the adopted K1 candidates (caught by the identity gate); a much larger G residual or candidate sup than estimated (CONSERVATIVE already allows ×4) |
| **class (frozen rule)** | **MARGINAL** | **INFEASIBLE** | **INFEASIBLE** | **STRONG** |

Why D's NOMINAL is generous: it assumes a deflated tower whose M5 on [0, 0.025] equals the certified hull-0 value (no
growth at all over a hull 50× wider). Even so it closes only 42/122 pairs; with the ×4 CONSERVATIVE allowance, 5.

## Selection (frozen rule)

TC is the only route at or above USEFUL, so it is selected. It needs new real addresses, so the section-5 lifecycle
applies in full: deterministic reuse is shown insufficient above (routes D, G at zero new real addresses close 0 pairs
under the certified inputs they would actually use); addresses, producer, runtime, dependencies, fields, outputs,
acceptance, budget and stopping rule are pre-registered in the protocol; freeze → qualification at the freeze commit →
fresh-context authorization review → guard ALLOW for exactly the 34 addresses → execution → guard DENY → seal →
consumption → independent adjudication.

`LOWER_FRONT_SELECTED_ROUTE = TC (Taylor-cell atom-deflated whole-cell R'' enclosure)`,
`LOWER_FRONT_FEASIBILITY_GATE = STRONG` (forecast), new-real forecast 9.0 CPU-h (preferred budget 20, hard 40).
