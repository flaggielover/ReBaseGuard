# K5 global bridge theorem (proof before any compute)

**Target (binding, `p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md`): H3a.** For each frozen `(D,m)`, `s(e) = −R(e)/e` is continuous and strictly decreasing on `(0,2]`, with `s(0+) = Γ̃ − 1` and `s(2) < 1`.

## Setting

- Fix `(D,m)` and the frozen K1 cover cells `C_k = [x_{k−1}, x_k]`, `k = 1..N`, with `x_0 = 0` exactly, contiguous, and `x_N ≥ 2` (SR PS1 cells 0–294; CUSUM cells 0–309). Let `ρ_k = (x_k − x_{k−1})/2` and `e0_k` be the midpoint.
- K1 certified objects on `C_k` (outward exact rationals):
  - `R_k ∋ R(e0_k)` and `D_k ∋ R'(e0_k)` (midpoint enclosures);
  - `H_k ⊇ R''(C_k)` (`R2_interval`, the cell enclosure whose magnitude is `M_k = M_R2`).
- New object: a certified lower bound `L_k ≤ inf_{C_k} R'''`. If absent, `L_k := −∞`.
- Premises:
  - `R` is odd (P5-T3) and real-analytic (P5X L5), hence C³ with `R''(0) = 0`;
  - `R'(0) = 1 − Γ̃` exactly (local derivative correspondence);
  - K1's `sup|R| < 2` certificate on the cell containing 2.
- Let `g(e) := R(e) − e·R'(e)`. Then `g(0) = 0`, `g'(e) = −e·R''(e)`, and `s'(e) = g(e)/e²` for `e > 0`.

## Theorem K5-B (sufficient bridge)

Define exact-rational recurrences with `ℓ_0 := 0`:

```text
k = 1:  ℓ_1 := max(H_1.lo, 2ρ_1·L_1),        γ_1 := −L_1·x_1³/3            (valid when L_1 finite)
k ≥ 2:  μ_k := max(H_k.lo, ℓ_{k−1} + min(0, 2ρ_k·L_k))
        ℓ_k := max(H_k.lo, ℓ_{k−1} + 2ρ_k·L_k)
        γ_k := min( γ_{k−1} − μ_k·(x_k² − x_{k−1}²)/2 ,  Γ_k )
        Γ_k := hi( R_k − e0_k·D_k ) + ρ_k·x_k·M_k                               (K1-only direct bound)
```

A cell `C_k` **passes** if either:
- `k = 1` and `L_1 > 0`; or
- `k ≥ 2` and `U_k < 0`, where `U_k := max(γ_{k−1}, γ_{k−1} − μ_k·(x_k² − x_{k−1}²)/2)`; or
- `Γ_k < 0` (the direct test, for any `k`).

If every cell meeting `(0,2]` passes, H3a holds for that `(D,m)`.

**Proof.**
1. *Lower bounds for `R''`.*
   - `R''(0) = 0 = ℓ_0`.
   - On `C_k`, by the mean value theorem for `R''`: `R''(t) ≥ R''(x_{k−1}) + L_k(t − x_{k−1}) ≥ ℓ_{k−1} + min(0, 2ρ_k L_k)` and `R''(t) ≥ H_k.lo`. So `R'' ≥ μ_k` on `C_k`.
   - At `x_k`: `R''(x_k) ≥ max(H_k.lo, ℓ_{k−1} + 2ρ_k L_k) = ℓ_k`. By induction each `ℓ_k` is a valid lower bound.
2. *Upper bounds for `g`.* `g(e) = g(x_{k−1}) − ∫_{x_{k−1}}^{e} t·R''(t)dt`. Since `t ≥ 0` and `R'' ≥ μ_k` on `C_k`, `∫ t R'' ≥ μ_k (e² − x_{k−1}²)/2` whatever the sign of `μ_k`.
   - So `g(e) ≤ γ_{k−1} − μ_k(e² − x_{k−1}²)/2`, which is monotone in `e` on `C_k`. Its supremum is `U_k`, and `g(x_k) ≤ γ_{k−1} − μ_k(x_k² − x_{k−1}²)/2`.
   - Independently, by the mean value theorem for `g` about `e0_k`: `|g(e) − g(e0_k)| ≤ ρ_k·sup_{C_k}|t·R''(t)| ≤ ρ_k·x_k·M_k`, and `g(e0_k) ∈ R_k − e0_k·D_k`. So `g ≤ Γ_k` on `C_k`, and `γ_k` is a valid bound for `g(x_k)`.
   - For `k = 1`: `R''(t) ≥ L_1·t` on `C_1` (since `R''(0) = 0`), so `g(e) ≤ −L_1 e³/3`, which is `< 0` for `e > 0` when `L_1 > 0`.
3. *Conclusion.* If every cell passes, `g < 0` on `(0,2]`. So `s' < 0` there and `s` is strictly decreasing.
   - Continuity of `s` follows from continuity of `R`.
   - `s(0+) = −R'(0) = Γ̃ − 1`.
   - `s(2) < 1` ⇔ `R(2) > −2`, which K1 certifies.

   This is H3a. `∎`

## What the theorem does and does not say

- **Sound and exact:** the recurrences use only outward rational endpoints and certified objects. They involve no tolerance, no refinement and no tuning.
- **Near zero, third order is necessary.** `H_1` contains `R''(0) = 0`, so `μ_1 ≤ 0`. The first cell can pass only through `L_1 > 0`, or through `Γ_1 < 0`, which is structurally hopeless because `|g| = O(e³)` there. With `R(e) = a1 e + a3 e³ + …`, `L_1 > 0` requires `a3 = R'''(0)/6 > 0`. A certified `sup_{C_1} R''' < 0` would certify that `s` increases near 0, i.e. H3a false.
- **Not complete.** Passing depends on realised widths. If H3a holds only degenerately (`a3 = 0`, or `g` touching 0 inside `(0,2]`), no interval method certifies it. The bridge cannot guarantee that the widths are narrow enough before results exist.
- **`R'''` is needed only where the chain requires it.** Setting `L_k = −∞` on a cell falls back to `H_k.lo` and `Γ_k`. Which cells need it depends on the results, so no cell subset is predeclared as sufficient.

```text
K5_GLOBAL_BRIDGE_THEOREM = PASS   (sufficient-condition theorem with exact recurrences; completeness not claimed)
```
