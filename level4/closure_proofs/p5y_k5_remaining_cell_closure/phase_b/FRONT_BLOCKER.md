# The CUSUM K5 front: a precisely stated scientific blocker

`FRONT_STATUS = BLOCKED_BY_CERTIFICATION_METHOD`. More compute cannot unblock it. Only a new certified capability
can.

## 1. What must be shown

For each m ∈ {1, 2, 3, 5}, g_m(e) = R_m(e) − e·R_m'(e) < 0 on the front: from x_hi(0) = 5.083e-4 up to x_lo of the
first directly passing cell. That is e ≈ 0.0964 (m = 1), 0.1087 (m = 2), 0.1099 (m = 3) and 0.1135 (m = 5).

Near 0, g_m(e) ≈ −(R'''_m(0)/3)·e³ with R'''_m(0) ∈ [1074, 2790] (slot-1). So |g| is between about 1e-7 (cell 1) and
0.4 (top of the front).

## 2. Why every existing certified route fails there

| route | certified width or penalty on the front | versus signal | verdict |
|---|---|---|---|
| K1 direct bound Γ (order ≤ 2) | point width of g(e0): 0.016 at cell 1 → 0.43 at cell 132 (m = 1), dominated from about cell 5 by e0·width(D); width(D) 3.7–9.1 (m = 1), the D half-width being about the resolvent cross term C²·k₁·res₀ (98% at cell 0); plus ρ·x·M_R2 with M_R2 ≈ 4000–16700 | \|g\| ≈ 3e-7 → 0.42 | fails on every front cell; the point enclosure alone contains 0 on 64–83 cells per m |
| K1 sub-cell points + parent M_R2 | same point width | same | works only on the 25–28 upper cells per m (CURVATURE_SLACK), at about 250 points ≈ 83 CPU-h; cannot touch the rest |
| order-3 at e = 0 + evenness transport (slot-1 / T-EXT) | penalty (e²/2)·M5, M5 ≥ 1.06e8 (m = 1) | L0 ≈ 1074–1801 | reach capped at about cell 9–10 pointwise, about cell 21–23 through the chain |
| order-3 graded point at a ≠ 0, hybrid transport with the 0-anchored M4 (review F8) | graded Neumann condition fails for a ≥ 0.02338 (Phase A §3); amplification 1/det grows to 20 at cell 40; block size unforecast until T-EXT seals M4(η) | R''' ≈ 2e3 | at best cells up to 40, with a new executor mode; nothing beyond |
| order-≤ 1 graded point at a ≠ 0 (review F9 counter-route) | slot-1 certifies R'(0) about 100× sharper than the K1 path, but only because the odd block carries the parity-exact order-0 error at e = 0; at a ≠ 0 the even residual returns (R error ≈ ee·res₀ ≈ 1.9e-3 at cell 20 against \|g\| ≈ 9.7e-4) | — | not a route |
| order-3 scalar (any e) | radius ≥ C·3k₁·ε_H,mid ≈ 1e7 (R1 finding) | R''' ≈ 2e3 | 4 orders of magnitude short |
| K1 whole-cell M3 (Lipschitz R'') | M3 = 9e7 at cell 0 (GammaTilde audit) | — | useless |
| analytic shortcut | none exists (STRATEGY §2) | — | — |

## 3. Root cause

- The certified even-block resolvent constant is C_e0 ≤ 469.77. Its float value is about 466, i.e. essentially sharp.
  It is the Perron mode of the CUSUM kernel at e = 0 (eigenvalue 0.99782, even).
- The scalar constants C_upper (1233 at cell 0; 514–1026 on the scalar-zone cells 41–148) carry the same mode across
  the front.
- Every certified error in orders 0–3 is some residual multiplied by this constant, and at order 3 by
  C·k₁·(lower-order error) cascades.
- The one place it is neutralised is e = 0 exactly, where σ-parity splits the odd block off (C_o0 ≤ 5.36). That is
  why slot-1 worked, and why nothing else does.

## 4. What would unblock it (each is a research-grade successor, with a theorem, a certificate and a qualification)

1. **Perron-deflated resolvent certificate on [0, 0.12].**
   - Needs a certified enclosure of the Perron eigenpair of K_e (eigenvalue gap to 1, eigenprojector) and a
     certified bound on the deflated resolvent. The Perron part of each object is then carried exactly through the
     eigenpair and its e-derivatives.
   - **Float diagnostic (NON-CERTIFIED, operator only, no R value; `PERRON_FLOAT_DIAGNOSTIC.json`).** It uses the frozen
     R2 `e0_operator_estimate.kernel_matrix(drift)`, the same class of diagnostic R2 and R4 ran.
     - Across the whole front, e ∈ {0, 5e-4, 0.0057, 0.0114, 0.0228, 0.05, 0.0964, 0.1135}, the Perron eigenvalue is
       0.99782 → 0.99686 (gap 0.0022–0.0031).
     - The full resolvent sup-norm is 466 → 325.
     - The **Perron-deflated resolvent sup-norm is 11.1–11.3, flat**, with the second eigenvalue |λ₂| ≈ 0.71–0.74.
     - So deflation would cut the dominant constant about 30–40× uniformly on the front. The width cross term scales
       like C², so the possible gain is up to about 10³×. That covers the 18–51× needed at the graded boundary and the
       few × on the upper front, if the Perron component can be certified exactly.
   - This is the most promising lever for the whole front, with a K1-type producer (scalar zone) and possibly an order-3
     producer (graded zone).
2. **A higher-accuracy candidate producer.** The needed width reduction w/|g| is a few × on the upper front, 18–51×
   at cells 40–41 (the graded boundary; m = 1: 18.8/17.6, m = 5: 50.9/47.9), and about 10³× near cell 10, with the
   existing constants.
   - The CUSUM solution has kinks at the clipping boundaries, so it is not known whether polynomial candidates reach
     that.
   - A DEV feasibility study on the residual alone (no enclosure of R) would settle it cheaply. It is still real-model
     arithmetic and needs its own governance ruling.
3. **An order-3 producer at e ≠ 0 without exact parity.** Only useful up to cell 40 even if it works.
   Informativeness is unforecast.

Recommended next step: `RESOLVE_K5_REMAINING_SCIENTIFIC_BLOCKER`, starting with (1). First comes a non-scientific
feasibility memo: can the Perron eigenpair of the CUSUM kernel be enclosed with a certified gap across [0, 0.12], and
what does the deflated constant do to a Γ-type front test? Only after that is a producer design worth freezing.
