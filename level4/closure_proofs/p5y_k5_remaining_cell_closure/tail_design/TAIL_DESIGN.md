# m = 5 tail (K1 cells 305–309): closure design

**Status: DESIGN_ON_RECORD.**
- No preregistration has been frozen for execution and no authorization is requested.
- No tail point has been evaluated.

Why the execution packet is deferred: the m = 5 tail cannot change K5's status while every front (m = 1, 2, 3, 5) is
blocked (`../phase_b/STRATEGY.md` §8). Spending 11 or more real scientific addresses now would buy no closure. Qualifying
the executor now would also age before use: host facts drift once unattended-upgrades runs, and the K1 midpoint replay
would have to be repeated. The packet should be built right after the front has a qualified route.

## 1. Theorem K5-B-T (tail sub-cell direct test; an additive successor to K5-B, which it does not modify)

**Setting.** K1 cell C_k = [a, b] of the frozen CUSUM cover, with parent curvature bound M_k = M_R2(k), which bounds
sup_{C_k} |R''|. Take a partition a = y₀ < y₁ < … < y_s = min(b, 2), with sub-cell midpoints p_j and radii r_j.

**Claim.** If for every j

```text
hi( R(p_j) − p_j·R'(p_j) ) + r_j · y_j · M_k  <  0
```

with certified point enclosures of R(p_j) and R'(p_j), then g = R − eR' < 0 on [a, min(b, 2)].

**Proof.** g' = −eR'', so on sub-cell j, |g(e) − g(p_j)| ≤ r_j·sup |tR''(t)| ≤ r_j·y_j·M_k. This holds because the
sub-cell lies in C_k and M_k bounds |R''| on all of C_k. ∎

**Assembly with K5-B.**
- A K5-B pass of cell C certifies g < 0 on C unconditionally. The ℓ/γ quantities are valid bounds whether or not other
  cells passed.
- So H3a on (0, 2] follows once every point of (0, 2] lies in a K5-B-passed cell or a K5-B-T-certified sub-cell,
  together with continuity, s(0+) = Γ̃ − 1 and s(2) < 1.
- s(2) < 1 ⇔ R(2) > −2 comes from the cell-309 target gate. Per PB6 the closure does not enforce the gate values
  (margins 1.37–1.84), so the tail consumer must check them per m itself. The E6 adapter does not.
- The restriction to (0, 2] is exactly the H3a domain. It removes the frozen K5-B requirement that cell 309 pass
  beyond e = 2 (THEOREM_DOMAIN).

## 2. Address plan (forecast from the committed K1 values; to be frozen only when the packet is built)

Equal splits: s = 2, 2, 3, 3 on cells 305–308, plus one sub-cell [x_hi(308), 2] for cell 309. That is 11 points,
listed exactly in `TAIL_POINTS_DRAFT.json`.

Forecast penalties r_j·y_j·M_k are 0.085–0.21, against |g| ≈ 0.22–0.34 (ratio ≤ 0.74) with point widths ≈ 0.008.

**Failure path** (to be frozen with the packet, before any result; review F12): no adaptive refinement. If any
sub-cell fails, the result is TAIL_NOT_CLOSED for the affected parent cell. A new partition would need a new
preregistration.

## 3. Executor and cost

- **Executor:** `p5y_gammatilde_point_certificate/code/point_eval.py`, the frozen K1 CUSUM midpoint path called
  unedited on a degenerate cell {p}, with C_upper of the containing frozen cell. That C_upper is valid for every e in
  the cell.
  - Classification: REQUIRES_NEW_CODE_AND_QUALIFICATION. `point_core.point_cell` refuses any cell but CUSUM cell 0
    (review F12), so a containing-cell binding is new code. The midpoint arithmetic itself is the frozen K1 path,
    unedited.
  - The qualification would be an exact replay of the K1 midpoints of cells 305–309 (the existing R_interval and
    D_interval must be reproduced), the same pattern as the point certificate's Q2.
- **Cost:** about 1,180 CPU-s per point, all m in one run (from the point certificate's evidence).
  - 11 points ≈ 3.6 CPU-h, about 1 wall-h on 4 workers.
  - Qualification replay: 5 × 1,180 CPU-s ≈ 1.6 CPU-h.
- **Governance:** new real scientific addresses, so the full external-authorization packet of the first real probe
  applies: frozen protocol, qualified executor binding, independent review, execution-binding amendment, external
  authorization and countersignature, LAUNCH_NOTICE, sealed ledger, adjudication.
