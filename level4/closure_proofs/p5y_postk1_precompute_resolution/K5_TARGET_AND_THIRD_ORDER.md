# K5: binding target and minimal near-zero third-order route (pre-compute; nothing run)

## 1. Adjudicating the two frozen formulations

| date (commit) | record | formulation | status |
|---|---|---|---|
| 2026-08-31 (`bb03c0ea`) | `p5_nonlinear_dynamics/THEOREM.md` (H3a) | **A**: `s(e) = −R(e)/e` continuous and **strictly decreasing** on `(0,2]`, `s(0+) = Γ̃ − 1 = 1/ρ_c`, `s(2) < 1` | hypothesis of P5 T9/T10 |
| 2026-09-02 (`db0781ed`, P5X anchor) | P5X `FROZEN_THEOREM.md` §8 P5X-T7(2); `FEASIBILITY_AUDIT.md` §8 | **B**: continuous, `s(0+) = Γ̃ − 1`, "each level `L ≥ 1` attained exactly once on `(0,E]`"; the audit calls it a *weakening* of H3a | P5X secondary target; claims it discharges H3a |
| 2026-09-05 01:54 (`8e888255`) | P5Y K1 binding `CHECKPOINT.md` §1 | "`K5` (`H3a`)" | **binding P5Y label** |
| 2026-09-05 11:45 (`17eb58b2`) | `FORWARD_AUDIT.md` | "H3a is strict monotonicity … adopting [level attainment] as the target would substitute the theorem and needs an explicit pre-registered decision" | P5Y audit |
| 2026-09-05 11:54 (`45a82473`) | `THEOREM_ADJUDICATION.json` (binding) | K5_H3a proof path "`s'(e) < 0` cellwise" (form A) | **binding** |

**Ruling (temporal and governance precedence).**
- K5 is a P5Y obligation. Every binding P5Y record, all later than the P5X anchor, names **H3a** (form A).
- No P5Y record adopts form B, and the one P5Y record that discusses B requires an explicit pre-registered decision before B could substitute for A. No such decision exists.
- The substitution is therefore **not made**, silently or otherwise.
- **B as literally frozen is defective**: it is false for `L > sup s`. Corrected, B reads: `s < s(0+)` on `(0,2]`, each `L ∈ [1, s(0+))` attained exactly once, and `s(2) < 1`. **A implies corrected B**, so discharging A also discharges corrected B.

```text
K5_BINDING_TARGET = H3a (P5 THEOREM.md, verbatim): for each frozen (D,m), s(e) := -R_{D,m}(e)/e is continuous and
                    strictly decreasing on (0,2], with s(0+) = GammaTilde_{D,m} - 1 = 1/rho_c(D,m) and s(2) < 1
```

The non-local parts are already covered:
- continuity: from `R` continuous (H1/P5-T3; P5X `L5` analyticity);
- `s(0+) = −R'(0) = Γ̃ − 1`: exact local derivative correspondence;
- `s(2) < 1` ⇔ `R(2) > −2`: K1's target gate on the cell containing 2.

## 2. Expansion near zero

- By P5-T3, `R` is odd. By P5X `L5`, `R` is real-analytic. Hence

  ```text
  R(e) = a1 e + a3 e³ + a5 e⁵ + O(e⁷),   a1 = R'(0) = 1 − Γ̃ < 0,   a3 = R'''(0)/6,   a5 = R⁽⁵⁾(0)/120.
  ```

- Dividing by `e`:

  ```text
  s(e)  = −a1 − a3 e² − a5 e⁴ + O(e⁶)        ⇒ s(0+) = −a1 = Γ̃ − 1
  s'(e) = −2 a3 e − 4 a5 e³ + O(e⁵)
  ```

- Consequences:
  - `a3 > 0` (⇔ `R'''(0) > 0`) ⇒ `s` is strictly decreasing, with `s < s(0+)`, on some `(0, δ]`. This is the only generic way H3a can hold at 0.
  - `a3 < 0` ⇒ `s` is strictly increasing near 0 ⇒ **H3a is false**. A certified `R'''(0) < 0` is a mathematical counterexample.
  - `a3 = 0` ⇒ third order cannot decide; `a5` is needed.
- **Why second order cannot work.** `R''` is odd, so `R''(0) = 0`. Every `R''` enclosure over a cell containing 0 contains 0. A bound `|R''| ≤ M` gives `|s'| ≤ M/2`, which carries no sign.

**Lemma K5-L (non-asymptotic, needs only C³).** Let `R` be odd and C³ on `[0,δ]`. Then:
- If `R'''(t) ≥ c > 0` for `t ∈ [0,δ]`, then for `0 < e ≤ δ`: `s'(e) ≤ −c·e/3 < 0` and `s(e) < s(0+)`.
- If instead `R''' ≤ −c < 0`, then `s' ≥ c·e/3 > 0` there, which contradicts H3a.

*Proof.* `R''(0) = 0`, so `R''(t) = ∫₀ᵗ R''' ≥ ct`. Let `g(e) = R(e) − eR'(e)`. Then `g(0) = 0` and `g' = −eR''`, so `g(e) = −∫₀ᵉ tR''(t)dt ≤ −c e³/3`. Since `s'(e) = g(e)/e²`, `s'(e) ≤ −ce/3`. Integrating gives `s(e) − s(0+) < 0`. `∎`

## 3. Is a third-order certificate plus K1 records enough globally?

Decision chain per `(D,m)` on `(0,2]`:
- **Z1** (new): contiguous cells from 0 with `R'''_cell.lo > 0` ⇒ `R'' > 0`, `g < 0`, `s' < 0` on `(0, z₁]`.
- **Z2** (K1 records, signed `R2_interval`, admissibility per K4_FREEZE_AUDIT): following contiguous cells with `R2_interval.lo > 0`. Since `R'' > 0` there, `g` keeps decreasing from a negative value.
- **Z3** (K1 records): any cell with `g_cell.hi < 0`, where `g_cell ⊂ (R_interval − e0·D_interval) + [−ρ·e_hi·M_R2, ρ·e_hi·M_R2]`.

The chain is logically sufficient. Whether Z2 and Z3 close the remainder depends on the **realised** K1 widths against `|g| ≈ 2a3e³` and `R'' ≈ 6a3e` near 0. The frozen K1 budgets structurally allow much more width than that near 0:
- `R_interval` radius up to `B_candidate + B_kernel + B_interval + B_rounding + B_other = 0.14` absolute;
- curvature `ρ²M_R2/2 ≤ 1/20`, so `M_R2` up to about `1.5·10⁶` on SR cell 0 (`ρ = 1299/5000000`).

So how far Z1 must extend cannot be decided without inspecting results.

```text
K5_THIRD_ORDER_CERTIFICATE_SUFFICIENT = UNRESOLVED
   (exactly sufficient on the region where it certifies R''' > 0; global sufficiency with K1 records
    depends on unobserved K1 widths, which are structurally unable to resolve g or R'' near 0)
```

## 4. Minimal new computation (design only; NOT run)

**Feasibility risk, measured and immutable.**
- The SR O9 "Aux3-style third-derivative evidence" is `AUX3_SR_FEASIBILITY_FAIL`. Whole-cell fourth-order remainders exploded through the resolvent self-consistency factor `q_N = C Σ C(N,i) k_i ρ^i/i!` at `C·ρ ≈ 0.31` (cell 313).
- Near zero, the K1 SR cells run at the **same** `C·ρ`: cell 0 has `C_upper ≈ 1206` and `ρ = 2.6e-4`. That is by construction, since the frozen cover step depends on `C`.
- The K5 test is a **sign** test (`R'''(e0) − ρ·T[R,4] > 0`), not the `1/20` cover budget that failed, so feasibility is not settled. It is, however, at risk.
- A single coarse near-zero cell (e.g. `[0, 2/25]`) is excluded: `C·ρ` would be about 50.

**Design:**

| item | exact content |
|---|---|
| object | certified cell enclosure of `R'''_{D,m}(e)`: order-3 rung `F_r:k3` (r = 0..4) with order-3 sources `S_r:3`, `W:3`, `h_j:3`, all-m assembly at order 3, whole-cell remainder `ρ·T[R,4]` from the fourth-order norm tower (Aux3 governance Q3–Q7 pattern) |
| precision / records | 256 bits; outward exact-rational `{lo, hi}` records in the K1 schema, bound to a new producer identity |
| cells | the frozen K1 cover cells meeting `(0,2]`: SR PS1 cells 0–294 (295) and CUSUM cells 0–309 (310), for m ∈ {1,2,3,5}. This is the smallest scope that is **result-independent**: a strip (e.g. `left < 1/4`: SR 208 and CUSUM 222 cells) saves only ~30% and needs a result-triggered fallback. |
| mandatory gate before any cell | predeclared, non-result-bearing feasibility oracle (Aux3 Phase-4 pattern, float/oracle values, kill rule fixed in advance) on SR cells {0, 207, 294} and CUSUM cells {0, 221, 309} |
| decision rule | Z1 → Z2 → Z3 as §3; `R'''_cell.hi < 0` on a cell containing 0 ⇒ `K5_FAIL_MATHEMATICAL`; otherwise unresolved cells ⇒ `K5_INCONCLUSIVE` |
| CUSUM coupling | Aux4 already computes order-3 **source** objects (`auxiliary_third_derivative_evidence_v1`: S_r:3, W:3, h_j:3) but not `F_r:3`. Keep K5 **out of** the K1 CUSUM successor, so K1 is not hostage to K5; run it as its own governed successor on the same bound runtime |
| cost (unmeasured estimate) | SR: +33% candidates / +63% contracts per cell (Aux3 census) over PS1's 15.43 CPU-h/cell, giving ≈ 5.1–9.7 CPU-h/cell × 295 ≈ **1,500–2,870 CPU-h**. CUSUM: ≲ 0.4 CPU-h/cell × 310 ≈ **≲ 124 CPU-h**. Requalified by the oracle before any cap. |

```text
K5_MINIMAL_NEW_COMPUTE = certified R'''_{D,m} cell enclosures (order-3 rung + 4th-order remainder), m in {1,2,3,5},
                         256 bits, on frozen K1 cover cells meeting (0,2]: SR 0-294, CUSUM 0-309; preceded by a
                         predeclared feasibility oracle on SR {0,207,294} and CUSUM {0,221,309}; est. SR 1,500-2,870 CPU-h,
                         CUSUM <= ~124 CPU-h (unmeasured)
```
