# Phase A — why every remaining CUSUM K5 cell is open

**Descriptive; no new scientific arithmetic.** The map `OPEN_CELL_MAP.json` (sha256 `9579f3ad…`) was built on
rebaseguard-vultr-02 with `code/open_cell_map.py build` from a clean GitHub clone of `p5y-postk1-frontier` at `84299314`.
It re-runs only frozen code on frozen or sealed inputs:

- the accepted E6 adapter's loading path (`fbad7d33`): frozen loader `k5_minimality` (`3a54f0fb`), frozen
  `k5b_check.k5b_literal` (`ddd54dc4`), manifest `29ad1f9b` and cover `341eb5e9`;
- the adopted slot-1 L1 values from the sealed record `cf90f1ea…`;
- the certified operator constants (registry `a645a157`: C_e0 ≤ 469.7697, C_o0 ≤ 5.3601) and the frozen He₆ hull
  norm table. These are used only to classify zones (§3). No value of R or of any derivative of R is computed.

The builder refuses to emit a map unless its pass sets equal the adopted E6 output: canonical sha256 `89017388…`,
per-m pass ranges identical.

## 1. Initial open sets (verified)

| m | passes (frozen K5-B, L₁ from slot-1, L_k = None for k ≥ 2) | open | count |
|---|---|---|---:|
| 1 | 0, 133–309 | 1–132 | 132 |
| 2 | 0, 145–309 | 1–144 | 144 |
| 3 | 0, 146–309 | 1–145 | 145 |
| 5 | 0, 149–304 | 1–148, 305–309 | 153 |
| union | | 1–148, 305–309 | 153 |

## 2. The mechanism, exactly

Theorem K5-B passes cell k ≥ 2 either by the direct bound `Γ_k = hi(R_k − e0·D_k) + ρ_k·x_k·M_k < 0`, or by the
chain, `U_k = max(γ_{k−1}, γ_{k−1} − μ_k·Δ_k) < 0`, with `μ_k = max(H_k.lo, ℓ_{k−1} + min(0, 2ρ_k·L_k))`.

- **No order-3 channel after cell 0.** L_k = None for k ≥ 2, so μ_k = H_k.lo and ℓ_k = H_k.lo.
- **H_BOUND.** Every open cell, for every m, has H_k.lo ≤ 0. The K1 R'' enclosures are wide: H ≈ [−16669, +16670] on
  cell 0 (m = 1) and ≈ [−3892, +4090] on cell 132. So one cell without L already adds `|H_k.lo|·Δ_k` ≫ |g| to γ,
  and the chain cannot carry.
- **Direct bound fails** on every open cell (Γ_k ≥ 0), for one of two reasons:
  - **MIDPOINT_G_INDETERMINATE**: `hi(R_k − e0·D_k) ≥ 0`. The K1 midpoint enclosure of g(e0) already contains 0.
    From about cell 5 on its width is dominated by `e0·width(D_k)` (at cell 1, width(R) is larger), with width(D)
    3.74–9.08 across cells 1–148 for m = 1 (3.49–16.9 across all m), against |g| ≈ (R'''(0)/3)·e³.
  - **CURVATURE_SLACK**: `hi(R_k − e0·D_k) < 0 ≤ Γ_k`. g(e0) is certified negative, but the first-order penalty
    `ρ_k·x_k·M_R2` exceeds its margin.

## 3. Zones (certified operator constants only)

The graded parity method of R2–R5 (`graded_dag.resolvent_block`) is admissible on a hull [0, η] (or at a point with
|e0| = η) only if the 2×2 Neumann condition holds:

```text
(1 − C_e0·a)(1 − C_o0·a) − C_e0·C_o0·b² > 0,   a = η²·k2(η)/2,  b = η·k1(η)
```

Evaluated exactly with the certified constants and the frozen hull norms, it holds up to η = x_hi(40) = 0.0227656 and
fails from cell 41 (η ≥ 0.0233762; determinant −0.0014). Past that point, every graded rule falls back to the scalar
resolvent bound C_upper ∈ [587, 1233].

- **GRADED zone:** cells 1–40.
- **SCALAR_ONLY zone:** cells 41 and above.

Even inside the graded zone the even–even resolvent entry reaches the scalar cap C = 1232.8 by about cell 33.

## 4. Classification of every open cell

| m | FRONT, GRADED, MIDPOINT_G_INDETERMINATE | FRONT, SCALAR_ONLY, MIDPOINT_G_INDETERMINATE | FRONT, SCALAR_ONLY, CURVATURE_SLACK | TAIL, CURVATURE_SLACK | TAIL, + THEOREM_DOMAIN |
|---|---|---|---|---|---|
| 1 | 1–40 (40) | 41–104 (64) | 105–132 (28) | — | — |
| 2 | 1–40 (40) | 41–119 (79) | 120–144 (25) | — | — |
| 3 | 1–40 (40) | 41–120 (80) | 121–145 (25) | — | — |
| 5 | 1–40 (40) | 41–123 (83) | 124–148 (25) | 305–308 (4) | 309 (1) |

The primary categories use the vocabulary of the campaign:

- **FRONT = MISSING_ORDER3_EVIDENCE**, with H_BOUND and INTERVAL_WIDTH as the mechanism;
- **TAIL = INTERVAL_WIDTH** (curvature slack). Cell 309 also has THEOREM_DOMAIN: it extends to 2.0923 > 2, and the
  frozen K5-B is cell-granular, so it must pass beyond e = 2.

No open cell is blocked by GAMMA: GammaTilde > 1 is certified for every m (`84aaa6a5`; m = 1 by CORE-C1). None is
blocked by DERIVATIVE_SIGN either: no certified negative sign exists anywhere.

## 5. What the numbers say (diagnostics, floats rounded from the exact rows)

| m = 1 cell | e0 | g centre | g width | ρ·x·M_R2 | Γ |
|---:|---:|---:|---:|---:|---:|
| 1 | 7.6e-4 | −3.4e-7 | 0.016 | 0.0043 | +0.012 |
| 20 | 0.0109 | −9.7e-4 | 0.094 | 0.041 | +0.087 |
| 50 | 0.0287 | −0.017 | 0.196 | 0.089 | +0.170 |
| 100 | 0.0654 | −0.170 | 0.379 | 0.179 | +0.199 |
| 132 | 0.0958 | −0.420 | 0.435 | 0.210 | +0.007 |
| 133 (passes) | 0.0969 | −0.430 | 0.435 | 0.211 | −0.002 |

| m = 5 cell | e0 | g centre | g width | ρ·x·M_R2 | Γ |
|---:|---:|---:|---:|---:|---:|
| 305 | 1.661 | −0.341 | 0.0074 | 0.379 | +0.042 |
| 306 | 1.745 | −0.307 | 0.0080 | 0.421 | +0.118 |
| 307 | 1.836 | −0.276 | 0.0082 | 0.471 | +0.200 |
| 308 | 1.933 | −0.249 | 0.0080 | 0.533 | +0.288 |
| 309 | 2.038 | −0.227 | 0.0075 | 0.598 | +0.374 |

- **The front is a precision problem.** The K1 centre follows g ≈ −(R'''(0)/3)e³ closely, but the certified width
  of g(e0) is up to about 1000 times |g| near e = 0. Near the top of the front it is about equal to |g|.
- **The tail is a curvature-slack problem only.** The midpoint enclosures are about 1/40 of |g|, and the whole
  failure is ρ·x·M_R2 with M_R2 ≈ 5.3–5.5.
