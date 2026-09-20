# Campaign B, Phase B — route comparison and costed plan (m = 5 tail, cells 305–309)

Classes follow `config/FEASIBILITY_GATES_B.json`, frozen before these forecasts. Requirement (Phase A): certify the
whole-cell R'' of cells 305–309 to within **4.62, 3.69, 2.91, 2.31, 1.87** respectively (then the frozen K5-B direct
test passes), or certify μ_k ≥ ≈ −0.29 for the chain.

| route | mechanism | new real addresses | forecast | class |
|---|---|---|---|---|
| **T0** adopted state | K1 whole-cell refinement (already applied) | 0 | M = 5.27–5.50; needs 1.12–2.67× | — (the open state) |
| **T1** theorem-AD tightening at the tail (the adopted Perron rule, domain extended) | Corollary T with A0, A1, A2 from an extended operator registry, applied to the recorded whole-cell residuals | 0 (registry is operator-only) | the AD rule consumes the ρ-dominated whole-cell residuals: with the tail's own C_upper-class constants the radius is A0·f_H^cell + 2A1·f_D^cell + A2·f_F^cell ≈ 7.7·0.05 + 2·48·0.09 + 649·0.055 ≈ 45 per r, i.e. **worse** than the adopted refined 1.8–8.5. Even with perfect atom constants (A0 ≈ 2.5, A1 ≈ 8, A2 ≈ 40) it is ≈ 4 per r, no better than the adopted value | **INFEASIBLE** |
| **T2** theorem TC at cells 305–309 (the Campaign-A successor's theorem, new addresses) | Taylor candidate F̂ + tD̂ + t²Ĥ/2 + t³Ĝ/6 with the frozen order-3 producer; generic valid constants A0 = C_upper, A1 = C_upper²κ₁, A2 = 2C_upper³κ₁² + C_upper²κ₂ (no registry needed at the tail), radius = A0·p2 + 2A1·p1 + A2·p0 with p2 = f_H^mid + ρ f_G + ρ²Env4/2 | 5 cells (midpoint, r = 0..4), ≈ 2.2 CPU-h | NOMINAL (sG ≈ 10, sH ≈ 5, δ_G ≈ 1e-3): radius ≈ 0.6–0.9 per r ⇒ M ≈ 0.7–1.2 ⇒ **5/5 closed** with margin 1.6× (cell 309) to 6× (cell 305). CONSERVATIVE (×4 on the unmeasured sG, sH, δ_G): radius ≈ 2.4–3.6 ⇒ cells 305–307 close, 308–309 marginal ⇒ **3/5** | **USEFUL** |
| **T3** K5-B-T sub-cell direct test (`p5y_k5_remaining_cell_closure/tail_design`) | new theorem (sub-cell direct test with the parent M), 11 certified point evaluations at sub-cell midpoints, new executor binding (`point_core.point_cell` refuses any cell but CUSUM cell 0) | 11 points, ≈ 3.6 CPU-h + 1.6 CPU-h qualification replay | the design's own forecast: penalties 0.085–0.21 against \|g\| 0.22–0.34, ratio ≤ 0.74 ⇒ 5/5 under NOMINAL; the margin is thinner than T2's and the engineering is a new theorem plus a new executor | **USEFUL** |
| **T4** finer cover | re-cover the tail with narrower K1 cells and re-run K1 there | ≈ 10–20 cells of full K1 work (≈ 6–12 CPU-h) and a new cover, which the frozen K5-B binds by `cells.json` | changing the frozen cover invalidates the adopted map's cell indexing | **INFEASIBLE** (governance) |

## Selection and cost

**T2 (theorem TC at the tail)** is selected on the frozen rule: highest class, fewest new addresses (5 vs 11), least new
mathematics (the theorem, rule, cross-check, fixtures and mutants are already frozen, qualified and adjudicated in
`p5y_k5_lower_front_order3`), and the smallest new-code surface. What is genuinely new:

1. a new namespace with its own protocol pre-registering exactly cells 305–309 and its own producer binding (the frozen
   `tc_producer` is address- and namespace-bound by design, so it cannot be re-pointed; the new producer imports the
   frozen `tc_rule`, `tc_crosscheck`, `extract`/`identity_gate` by pin);
2. the constant supply: generic C_upper-based A0, A1, A2 (valid by positivity and the frozen norms) instead of the
   registry-r1 atom constants, since registry r1 covers e ∈ [0, 0.12] only — with an optional, operator-only registry
   extension to e ∈ [1.6, 2.1] as a tightening (no new real address);
3. a consumer that composes the adopted state (map r4) with the tail enclosures and re-runs the frozen K5-B.

Forecast new real compute: 5 cells × ≈ 1575 CPU-s ≈ **2.2 CPU-h** (+ 2 reproduction cells ≈ 0.9 CPU-h). Campaign A spent
14.203, so the campaign total stays ≈ 17.3 CPU-h against the preferred 20 and the hard 40.

Forecast wall time for the full governed lifecycle (build, three fresh-context reviews, qualification, authorization,
run, seal, two consumptions, adjudication, coverage map r5): **5–7 h**, of which ≈ 1 h is compute.

## Status

`TAIL_ROUTE_SELECTED = T2 (theorem TC at cells 305-309)`, `TAIL_FEASIBILITY_GATE = USEFUL`,
`TAIL_EXECUTION = NOT_STARTED` (the overnight window ended before the lifecycle could be built; no address of this
campaign has been evaluated, no protocol frozen, guard DENY). K5 therefore stays **PARTIAL**.
