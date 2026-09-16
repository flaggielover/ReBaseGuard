# R2 repair successor: R05 test power, cell-0 conditioning autopsy, sigma-graded error propagation

**Non-scientific, additive.**
- R1 (`p5y_k5_cusum_order3_real_producer`, freeze `e69a0224`, qualification `4a1b20a8`) is byte-identical and pinned
  file by file in the R2 protocol.
- No real CUSUM cell is evaluated, no `R'''` of any `(D,m)` is computed, and no probe or authorization exists.
- Results are in `RESULT.md`, written after the freeze commit.

## 0. Identity

`origin/p5y-postk1-frontier` moved during R1/R2 work: `323e2b8f`, `879792d0`, `aca34248`, `e7a9fbb0` and
`84aaa6a5`. All are additive, in namespaces R2 does not read (GammaTilde audit/point certificate, P5X L5 review). R2
is based on `84aaa6a5`.

## 1. R2-A: the R05 test-power repair

R05 makes the `r = 0` residual subtract the candidate `S_0'''` instead of the closed form. That silently drops the
charge `C‖Ŝ_0''' − S_0'''‖`, and in R1 no fixture isolated that edge.

**Fixture T25** (`code/r05_fixture.py`):
- Geometry is predeclared and differs from the post-R1 diagnostic: `controlled_K3`, `e0 = 13/40`, `ρ = 1/80`,
  offset `1/500`.
- The `S_0'''` candidate is offset, and `G_0` is re-solved **exactly** from the offset candidate. The only path to the
  true `G_0` error is the closed-form source term.

**Frozen invariants** (`r05_invariants`), plus R05 detected in QM:

| Case | unmutated | R05 mutant |
|---|---|---|
| fixture | 0 violations | > 0 violations |
| `ABL_ZERO_OFFSET` (offset 0) | 0 | 0 |
| `ABL_RESOLVE_CLOSED` (`G_0` from the closed form) | 0 | 0 |

The two ablations are the fixture's own mutation tests. They show that detection is caused by the isolated edge and
nothing else. All 21 R1 mutations are retained in their R1 trial order, with T25 appended last, so R1 detections
cannot change.

## 2. R2-B: cell-0 conditioning autopsy (committed magnitudes only)

`code/cell0_forecast.py` recomputes the R1 scalar midpoint cascade from the committed, hash-bound Aux5 cell-0 record.
The residuals are `objects[*].delta_mid`; the norms come from the geometry-only `sharp_norms.table`. It **reproduces
the committed `eps_mid` of F:0, D:0 and H:0 exactly** (also for cell 309).

Exact budget, `r = 0`:

| level | value | dominant term | share |
|---|---:|---|---:|
| `ε_F = C(δ_F + ε_Sclosed0)` | 4.55·10⁻³ | `C·δ_F`, δ_F = 3.69·10⁻⁶ | 100 % |
| `ε_D = C(δ_D + k₁ε_F + …)` | 4.57 | `C·k₁·ε_F` | 97.9 % |
| `ε_H = C(δ_H + k₂ε_F + 2k₁ε_D + …)` | 9.00·10³ | `C·2k₁·ε_D` | 99.94 % |
| `ε_G ≥ C(… + 3k₁ε_H + …)` | ≥ 2.66·10⁷ | `C·3k₁·ε_H` | 99.94 % |

Here `C = 1232.8`, `k₁ = 0.798`, `k₂ = 0.968`, `k₃ = 1.510`. Closed-form source allowances are ≤ 10⁻⁵⁰. The error
bounds dwarf the certified candidates: `sup|D̂| = 21.7` and `sup|Ĥ| = 33.4` against `ε_H,mid = 9001`.

| candidate cause | verdict |
|---|---|
| resolvent conditioning | **primary**: the global bound `C` is applied at every derivative level, giving `ε_G ≈ C⁴·6k₁³·δ_F` (2.6·10⁷) |
| dependency inflation | **primary, same mechanism**: each level consumes the previous level's worst-case error through `C·k_i` |
| norm overestimation | secondary: the certified `C_upper = 1233` is 2.6× the operator estimate 466 at `e = 0` (section 3); `k_i` are drift-aware and tight |
| base Layer-2 solve | not the source: `δ_F`, `δ_D`, `δ_H` ≈ 4·10⁻⁶–10⁻⁴ |
| midpoint curvature certification | not the source: `ε_H` is 99.94 % propagated `ε_D` |
| global / reachable-state norm | contributes through its parity blindness: the sup norm over all functions forgets that odd levels never see the slow mode |
| Bernstein range | not the source (it bounds δ, which is small) |
| algebraic formulation | the **scalar** cascade is the formulation defect: it merges the even and odd subspaces the operator keeps apart at `e = 0` |

```text
PRIMARY_R1_WIDTH_SOURCE = resolvent conditioning compounded by dependency inflation: the parity-blind global resolvent
                          norm C (certified 1233, operator ~466) applied at all four derivative levels (C^4 · 6k1^3 ·
                          delta_F with delta_F = 3.7e-6); the base residuals, Bernstein ranges and sources are not the source
```

## 3. Structural audit at e = 0

**σ.** Let `σ(p, m) = (m, p)`. It maps the reachable set to itself (the branches `p + m ≶ 1` and the tail union are
symmetric), fixes `x0 = (0,0)`, and is an isometry of the sup norm. `P_e = (I+σ)/2` and `P_o = (I−σ)/2` have norm ≤ 1.

1. **Step map.** `q(σx, z) = σ q(x, −z)`: both sides are `(max(0, m + z − k), max(0, p − z − k))`, and the window
   `[m − c, c − p]` maps to itself under `z → −z`.
2. **Operator parity.** `K_i(0)` has weight `φ⁽ⁱ⁾(z) = (−1)^i He_i(z) φ(z)`, of parity `(−1)^i` in z. Substituting
   `z → −z` gives `σ K_i(0) = (−1)^i K_i(0) σ`.
   - `J_i(0) = Kz_i + i K_(i−1)` has weight parity `(−1)^(i+1)`, so `σ J_i(0) = (−1)^(i+1) J_i(0) σ`.
   - Away from 0 the symmetry breaks by `‖K_i(e) − K_i(0)‖ ≤ |e|·k_(i+1)`.
   - **Checked on the real Arb kernels** (QG4, synthetic polynomials).
3. **Object parities at e = 0.**
   - `S_0 = φ(c − p + e) − φ(m − c + e)` is odd; `h_1 = 1 − K1` is even.
   - `h_j` is even; `S_r = J h_r` is odd. So `F_r` is odd, `F_r'` even, `F_r''` odd, `F_r'''` even. `W_(r,j) = K^j S_r`
     is odd, `W'''` even.
   - Odd functions vanish at the fixed point `x0`, so `R(0) = R''(0) = 0` there. This matches R odd (P5-T3), and the
     next exact zero is `R''''(0) = 0`.
4. **Slow mode.** `K_0` is a positive operator, so its Perron eigenfunction is positive; `σ` commutes with `K_0`, so it
   is σ-even. Non-certified float estimate on the frozen collocation grid, K₀ only
   (`evidence/e0_operator_estimate/E0_OPERATOR_ESTIMATE.json`):
   - Perron eigenvalue 0.99782, even;
   - next eigenvalues 0.714 (even) and 0.708 (odd);
   - `‖(I−K₀)⁻¹‖ ≈ 466`, `‖(I−K₀)⁻¹P_o‖ ≈ 4.68`, even after deflating the Perron mode ≈ 11.2;
   - commutation defect 2·10⁻¹⁵.
5. **What interval arithmetic loses.** The scalar bound `‖X̂ − X‖` cannot see that F and H are odd levels, where the
   resolvent acts with norm ~5, not ~1233. The odd→even coupling happens only through odd-order `K_i`.
6. **Smaller certified system for `R'''(0)`.** At `e = 0` the value is `P_e G(0)(x0)`. Its error chain is
   `even(G) ← C_e ← odd(H) ← C_o ← even(D) ← C_e ← odd(F) ← C_o`. The graded cascade at `η = 0` is exactly this
   reduced system; there are no leakage terms.

`E0_PARITY_REDUCTION = USED`.

## 4. Base-solve alternatives

| class | applicable | R2 decision |
|---|---|---|
| 1. generic scalar resolvent enclosure | yes | baseline (`graded_dag` with `parity=False` reproduces R1 exactly) |
| 2. e = 0 parity-reduced / graded solve | yes, exact structure | **selected**. It removes two of the four `C` factors with one new operator constant, is sound on the whole cell by a Neumann perturbation (`η·k₁·√(C_e C_o) ≈ 0.04` at cell 0), and never exceeds the scalar bound |
| 3. residual-corrected / iterative refinement | yes | rejected: it shrinks `δ` linearly but leaves `C⁴`. The manufactured comparison emulates it with 10× smaller candidate error (radius only /10) |
| 4. block solve on reachable-state structure | partially | σ is the reachable-state symmetry used in 2; the branch/tail blocks carry no invariance |
| 5. direct certified linear solve, not a global inverse | in finite dimensions only | the CUSUM operator is continuous-state; a certified finite solve needs a rigorous discretization defect, a larger unbuilt project |
| 6. preconditioned interval solve | same as 5 | same |
| 7. Krawczyk / interval Newton with a computed inverse | same as 5 | the strongest in principle (keeps the slow-mode cancellation) but requires 5; kept as the follow-up after 2 |
| 8. componentwise instead of global norms | yes | used in its two-component parity form; a Perron-deflated even component is the next lever (forecast in section 7) |

Methods are compared on manufactured σ-systems with **certified** `C_e0` and `C_o0` (part `method_comparison`). No
real `R'''` informed the choice.

## 5. The selected method: σ-graded propagation (`code/graded_dag.py`)

Every error bound becomes `(e, o, t)` with `e ≥ ‖P_e err‖`, `o ≥ ‖P_o err‖` and `t ≥ ‖err‖`, normalized by
`t ≤ e + o`, `e, o ≤ t`.

**Rules.** Each is an upper bound of a term of an exact identity:
- **Operators.** `‖P_x K_i(e) P_y‖ ≤ k_i` if `K_i(0)` maps parity y to x, else `≤ η·k_(i+1)`, using hull norms since
  the leakage integrates from 0. `J_i` is the same with parity `(−1)^(i+1)`.
- **Resolvent.** `A(e) = (I − K₀) − Δ`, with `‖P_xΔP_x‖ ≤ η²k₂/2` (because `K₁(0)` swaps parity) and
  `‖P_xΔP_y‖ ≤ η k₁`. If `M = diag(C_e0, C_o0)·[[η²k₂/2, ηk₁],[ηk₁, η²k₂/2]]` has certified `1 − M_xx > 0` and
  `det(I−M) > 0`, then the block-norm matrix of `A(e)⁻¹` is `≤ (I−M)⁻¹ diag(C_e0, C_o0)`, capped by `C`. Otherwise
  scalar `C` is used.
- **Whole-cell residuals.** `residual(e0) + ρ·env`. The envelope is graded: `∂_e res = −Σ c·K_(i+1)(e) X̂`, bounded
  with the graded operator rule on the candidates' graded suprema. For closed-form leaves, `sup‖X⁽ⁿ⁾‖` has the right
  parity `T_n` and the wrong parity `η T_(n+1)`.
- **Export.** The error at the σ-fixed `x0` equals its even part, so `rad = Σ|c|·e`.

**Inputs beyond R1.**
- **`C_o0`**: certified `‖(I−K₀)⁻¹‖` restricted to σ-odd functions, at `e = 0`. This is the **new operator
  certificate**, not built in R2; the registry is frozen empty.
- `C_e0 ≤ C_upper`, already certified.
- Hull norms: equal to the cell norms for cell 0.
- Graded residual ranges: built (`cusum_graded.graded_range`, checked on real kernels).

**Precision policy.** Unchanged: {128, 192, 256, 384, 512}, production 256, exports exact `mid ± rad`.

## 6. Real wiring: specified, not built

`cusum_graded.certify_real_cell_r2` gates authorization, then the operator certificate, then refuses
`GRADED_REAL_WIRING_NOT_BUILT`. Building it requires:
1. graded certification of every frozen DAG residual (h, S, F/D/H/G, W, orders 0–3) with `graded_range`;
2. graded envelopes from graded candidate suprema (Bernstein ranges of symmetrized candidates);
3. truncation allowances charged to both components;
4. the `k_5` norm (He₅ roots, tabulated) and `j_5` (He₆ roots: a deliberate table extension);
5. the certified `C_o0` operator certificate.

None of these computes an `R'''` value.

## 7. Point versus whole cell; K5-B

**K5-B consumes `L_1 ≤ inf_{C_1} R'''`.**
- A point certificate at 0 is not consumable as is.
- It becomes consumable without weakening K5-B, because `R'''` is even and `R''''(0) = 0`:
  `L_1 := lo(R'''(0)) − (x_1²/2)·M_5` with `M_5 ≥ sup_{[0,x_1]} |R⁽⁵⁾|`, where `x_1²/2 = 1.29·10⁻⁷`.
- The alternative is the whole-cell graded interval directly.

**Forecast** (committed magnitudes; `C_e0 = C_upper`; conservative scalar envelopes on both components):

| | R1 | R2, `C_o0` = float estimate 4.68 |
|---|---:|---:|
| midpoint `R'''(e0)` radius, m = 1 | 2.66·10⁷ | 3.45·10³ (×7.7·10³) |
| point `R'''(0)`, conservative proxy (residual(0) ≤ residual(e0) + e0·env) | — | 1.91·10⁵ |
| whole cell 0, m = 1 | 2.27·10⁹ | 2.80·10⁵ (×8.1·10³) |

Sweep:
- `C_o0` = 10 → mid 8.8·10³; 50 → 1.1·10⁵; 466 → 8.5·10⁶; `C_upper` → no gain.
- The G-residual assumption (×1, ×10, ×100) is not load-bearing.
- A sharper certified even bound (466) gives mid 449; a Perron-deflated even component (hypothetical) gives mid 0.26.

`POINT_R3_AT_ZERO_CERTIFICATION = POSSIBLE` in structure; not demonstrated on a real cell.
`WHOLE_CELL_FIRST_CELL_CERTIFICATION = NOT_DEMONSTRATED`: it is not structurally blocked (the graded Neumann
condition holds on cell 0), but the forecast radius remains large.

## 8. Freeze discipline

- The seed-disjoint DEV protocol (`make_protocol_r2.py --dev`) calibrated fixtures and mutation `required` flags.
- The frozen protocol, gates, feasibility criterion, registries and bound code are committed before any R2
  qualification part runs.
