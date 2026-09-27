# Idea note (timestamped before any evaluation): atom-direct likelihood-ratio Taylor enclosure (ADLR)

Written 2026-09-27 ~18:30Z, overnight. It uses no cell data. It was passed to stream B (order-3) for evaluation.

## Identity

For the killed CUSUM kernel, the drift enters only through φ(z + e). For a fixed f, the likelihood-ratio identity
(`streams/C_308/IDEA_LR_SCORE_CONSTANTS.md`) is:

    (∂_e^j R_e f)(a) = E_a[ Σ_{n<τ} f(X_n) · H_j(M_n, n) ],   M_n = Σ_{k≤n} S_k,  S_k = −(Z_k + e) ~ N(0,1),
    H_0 = 1, H_1 = M, H_2 = M² − n, H_3 = M³ − 3nM, H_4 = M⁴ − 6nM² + 3n²   (the Hermite-type LR weights).

Since F_r(e) = R_e S_r(e), Leibniz gives, **at the atom**,

    |F_r^{(k)}(e)(a)| ≤ Σ_{j=0..k} C(k,j) · Λ_j(e) · ‖S_r^{(k−j)}(e)‖,     Λ_j(e) := E_a[ Σ_{n<τ} |H_j(M_n, n)| ],  Λ_0 = Λ.

## Enclosure

    F_r''(t)(a) ∈ Ĥ_r(a) ± [ rad_TC(0) + s·B3_r + (s²/2)·B4_r ],    s = |t − e0|,

where:
* `rad_TC(0) = A0 f_H + 2A1 f_D + A2 f_F` is theorem AD's midpoint bound;
* `B3_r ≥ |F_r'''(e0)(a)|`;
* `B4_r ≥ sup_cell |F_r''''(u)(a)|`, both from the formula above, with source-derivative sups σ_n(r). These are
  committed tower inputs.

**Candidate payloads are not needed for orders 3–4.** The approach is a structurally different alternative to TC-T's
s-dependent radius, `A0·f_G + …`. It avoids the product of the atom-functional norm A0 with the whole-function sups
`‖F''‖, ‖F'‖, ‖F‖` in f_G.

It combines with TPT: the profile has the same (constant, s, s²) shape.

## Status

* THEORY_ONLY.
* Its validity needs Λ_j certified uniformly over the cell, and σ_n(r) valid on the cell for n = 4 and at e0 for
  n = 3.
* It is closure-only under floor r2, because it changes the consumer.
* It must never be evaluated on cells 305–309 or at drifts in [1.2, 2.6].
