# CUSUM signed certified order-3 producer: real implementation, soundness, autopsy

**Non-scientific.** This namespace builds and qualifies the producer. It evaluates no real CUSUM cell, computes no
`R'''` of any `(D,m)`, runs no K5 probe and authorizes nothing. Results are in `RESULT.md`, written after the
freeze commit.

## 0. Identity audit (Phase 0)

The base is `origin/p5y-postk1-frontier`. It was fetched at session start at `10769e07`. It then moved three times
during this work. Each delta was inspected and is additive in a namespace this producer does not read:

| Commit | Content | Effect here |
|---|---|---|
| `323e2b8f` | GammaTilde sign audit (reuse only) | none; its cell-0 `supF3` reading agrees with section 6 |
| `879792d0` | P5X L5 independent review, PASS_WITH_SCOPE_LIMITATION | PB2 note updated (see section 5) |
| `aca34248` | GammaTilde point-certificate protocol (orders 0–1 at `e = 0`, frozen, not run) | none |

Frozen inputs, verified byte-for-byte:

| Object | Identity |
|---|---|
| Order-3 design / freeze | `10911e51`; `DESIGN.md` sha256 `33ccb2b4a7ac3fd5…` |
| Reference kernel | `code/order3_algebra.py` sha256 `d09c343102fc12dc…`; `manufactured.py` `fd27fea88ee5c79b…` |
| Synthetic qualification | `1bf31bc8`; evidence sha256 `75e159237500433b…` |
| Theorem K5-B | `K5_GLOBAL_BRIDGE.md` sha256 `c1c62346dcd11b3a…` |
| K5-B countersignature | `d7d3c08b`; `COUNTERSIGNATURE.json` sha256 `c16a830528026c24…` |
| Premise-binding result | `10769e07`; `PREMISE_BINDING_RESULT.json` sha256 `c29b5da7e79556b2…`; `CUSUM_K5B_K1_PREMISE_BINDING = PASS_WITH_NOTES` |
| K1 export manifest / producer | `29ad1f9bb8630a5f…` / `3692d0feeaef7136…` |
| Frozen assembly table | `checkpoint.json` sha256 `1c2a6825f19e19de…` |

None of these files differ between `10911e51` and the frontier head. The only additions to the design namespace are
the `1bf31bc8` result files.

## 1. The real mathematics (Phase 1)

**Detector.** Two-sided Gaussian CUSUM with `k = 1/2`, `h = 5`, reset state and `c = h + k = 11/2`. The raw state
is `x = (p, m)` on the reachable part of `[0,5]²`. The kernel is
`K_e f(x) = ∫ f(q(x,z)) φ(z+e) dz` with `q = (max(0, p+z−k), max(0, m−z−k))`. Operator derivatives in `e` put the
Hermite weight `φ^(i)/φ = (−1)^i He_i` on the density. `J_e = K_(z,e) + e K_e` is the raw-variable source operator,
and `J_i = Kz_i + e K_i + i K_(i−1)` is its exact Leibniz expansion.

**Objects** (frozen recursions; the candidates are state-only degree-12 dyadic polynomials, constant in `e`):

```text
h_1 = 1 − K 1           h_j = K h_(j−1)            S_0 = φ(u+e) − φ(l+e)   (closed form)
S_r = J h_r (r ≥ 1)     (I − K) F_r = S_r          W_(r,0) = S_r,  W_(r,j) = K W_(r,j−1)
R_m = (1/m) Σ_(r<m) F_r[x0] + Σ_(1≤t<m) (1/t − 1/m) Σ_(r<t) W_(r,t−r−1)[x0]      x0 = (0,0)
```

**Derivative solves.** Differentiate `(I − K_e)F = S` with Leibniz:

```text
order 1   (I−K) F'   = K_1 F + S'                                   frozen (D_r)
order 2   (I−K) F''  = K_2 F + 2 K_1 F' + S''                       frozen (H_r)
order 3   (I−K) F''' = K_3 F + 3 K_2 F' + 3 K_1 F'' + S'''          NEW rung G_r
```

The sources continue in the same way (Aux3, adjudicated `AUXILIARY_DERIVATIVE_SOUND = YES`): `h_1''' = −S_0''`,
`h_j''' = Σ C(3,i) K_i h_(j−1)^(3−i)`, `S_0''' = −He_3(u+e)φ(u+e) + He_3(l+e)φ(l+e)`,
`S_r''' = Σ C(3,i) J_i h_r^(3−i)`, and `W''' = Σ C(3,i) K_i W_(j−1)^(3−i)`.

**Chain as implemented** (code in brackets):

1. Layer 1 proposes `G_r` from `(I−K)G = dddK F + 3 ddK D + 3 dK H + S3` on the frozen grid
   [`cusum_order3.Order3Certifier._candidates_rung3`].
2. The certified midpoint residual `δ_G` is the reachable-set Bernstein range of
   `G − K_0G − K_3F̂ − 3K_2D̂ − 3K_1Ĥ − Src3`, plus the frozen truncation allowances
   `Z·(s_G ε_z0 + s_F ε_z3 + 3 s_D ε_z2 + 3 s_H ε_z1)` (and `reward_allow[3]` for `r = 0`). The whole-cell residual is
   `δ_G + ρ(k_1 s_G + k_4 s_F + 3k_3 s_D + 3k_2 s_H)` [`rung3_residual.g_residual`].
   This is the frozen `H_r` pattern one order up.
3. The midpoint error is `ε_G = C(δ_G + k_3 ε_F + 3k_2 ε_D + 3k_1 ε_H + ε_Src3)`. Its inputs are the frozen
   midpoint DAG values and Aux3's `midpoint_order3_eps` [`rung3_engine`].
4. The whole-cell bound is `min(cascade, Taylor)` for the source chain `h:3`, `S:3`, `W:3` and for `F:3`
   (section 4) [`rung3_engine`].
5. The assembly is `centre ± Σ|c| ε` with the frozen table. `L` and `U` are exact dyadic rationals
   [`rung3_engine`].

**Cross-checks against the reference kernel.** Part QR requires the Arb engine to reproduce, on the frozen
reference kernel's own 15 QN1 trials, its `F:3` midpoint and cascade values and its `W:3` cascade and Taylor values
exactly, up to outward rounding (relative excess `≤ 2^−200`). It also requires the engine's `F:3` Taylor bound and
export interval to lie inside the reference's. The engine's bounds can only be tighter, through the admissible
candidate-sup tower of section 4. The mutation matrix (21 source mutations of the engine and residual) is part QM.

## 2. Aux3 failure autopsy (Phase 2)

The historical failure is `AUX3_SR_FEASIBILITY_FAIL` (`p5y_k1_sr_o9_aux3_successor`, SR cell 313).

| Question | Finding |
|---|---|
| Which order failed | The **whole-cell fourth-order remainder** `T[X,4]` (equivalently `M_R4`) that bounds the cell variation of the order-2 curvature enclosure. It was measured against the K1 cover budget 1/20. |
| Did signed third order fail? | **No.** Signed order 3 was never built: Phases 5–7 did not run, and the midpoint order-3 objects were used only as unsigned Taylor inputs. |
| Which recurrence amplified | 1. The pure norm tower gave `M_R4 ≈ 2·10³–4·10³`, 6.8–15.4× the budget. 2. The self-consistent Taylor tower's resolvent factor `q_N = C Σ_(i=1..N) C(N,i) k_i ρ^i / i!` had `C ≈ 2`, `ρ ≈ 0.157`, giving `q_4 = 0.709`, `q_5 = 0.936`, `q_6 = 1.185`. At `q_6` there is no bound. Even with ideal midpoints and exact norms, m = 2, 3, 5 stayed above the kill ratio 1.1. |
| Role of `C·ρ ≈ 0.31` | 1. The frozen cover step ties `ρ` to `C`: every CUSUM cell ≤ 324 has `C·ρ = 0.3133` exactly, as do SR cells 0, 1, 207 and 313. 2. `q_N` is a polynomial in `Cρ·k_i ρ^(i−1)`, so the same product recurs wherever `C` is large. |
| Interval dependency | 1. Norm-only towers multiply operator norms by suprema and never cancel: at CUSUM cell 321 the certified candidate sup is 500× smaller for `h'''` and 53 000× smaller for `S'''`. 2. Every whole-cell step pays `C` again. |
| Mathematical or implementation? | **Mathematical and architectural** (norm-based remainders against a fixed budget), not a code defect. It is not an infeasibility proof: the certified bounds were valid, only too wide for that budget. |
| Precision escalation | **Does not help.** The widths are rigorous analytic upper bounds; rounding is ~2^−250 of them. This producer confirms it: on every precision fixture the whole-cell width is precision-independent. |
| Rescaling / reformulation | 1. Helps only where it removes norm overestimation, e.g. replacing tower terms by certified candidate suprema plus certified errors (used in section 4). 2. Adding higher midpoint rungs raises `q_N`, so it does not help. 3. Rescaling `e` leaves `C·ρ` invariant. |

**Relevance to R'''.**
- **Soundness: not relevant.** This producer uses no self-consistent tower and no `q_N < 1` condition: every
  whole-cell bound is finite whenever the inputs are, and K5's test is a sign, not the 1/20 budget.
- **Tightness: relevant.** The same amplification class, `C` multiplied through lower-order errors, decides the sign
  test at CUSUM cell 0 (section 6). There the driver is `C ≈ 1233` acting on the frozen midpoint `ε_H`, not the
  fourth-order tower.

```text
AUX3_FAILURE_RELEVANCE_TO_R3 = MEDIUM
AUX3_FAILURE_ROOT_CAUSE      = norm-based whole-cell 4th-order remainder amplified by the resolvent
                               self-consistency q_N (C·ρ fixed at 0.3133 by the cover rule) against the 1/20 budget
```

## 3. Implementation (Phase 3)

The code is in a new namespace. No historical file is modified. The frozen chain is imported in place and wired
explicitly: no module attribute assignment, checked by Aux3's `no_monkeypatch` detector, which fires on its control.

| Module | Role | Runs in qualification |
|---|---|---|
| `rung3_engine.py` | Arb engine (section 4 rules, assembly, export, scientific serialization/hash) | yes, on manufactured inputs |
| `rung3_residual.py` | certified `G_r` residual; `TERMS` is the single Leibniz table | yes, manufactured and real Arb kernels on synthetic polynomials |
| `cusum_order3.py` | real front-end: `Order3Certifier(Aux3Certifier)`, `collect_inputs`, `cross_check_k1`, `certify_real_cell` | the governance gate only; the real science path is never entered |
| `k1_inputs.py` | fail-closed K1 record validation V01–V10 | yes, on committed record copies |
| `manufactured_chain.py`, `fixtures.py`, `soundness.py`, `independent_crosscheck.py`, `reference_differential.py`, `real_operator_integration.py`, `qualify_order3.py` | qualification | yes |

**Binding in the real export** (`certify_real_cell`; scientific payload separate from runtime metadata):
- detector `CUSUM(k=1/2, h=5)`, `D`, `m ∈ {1,2,3,5}`, cell id and exact `left/right/e0/rho/C_upper`;
- precision 256 and the coefficient table sha;
- source-definition hashes (design, K5-B theorem, countersignature, premise binding);
- K1 producer identity, K1 record sha256, K1 scientific hash and export manifest sha;
- the order-3 producer manifest sha (`config/ORDER3_PRODUCER_MANIFEST.json`) and the Aux5 runtime contract hash;
- the authorization entry and the K1 cross-check.

Output per `m`: `R3_interval.lo/hi/width`, signed `L` and `U`, midpoint interval, `sign_status`, certification
status, and per-component `eps_mid / cascade / taylor / kept`. Refusal happens on:
- a non-finite enclosure;
- a precision outside {128, 192, 256, 384, 512} (production is 256 only);
- a missing input or `C ≤ 0`;
- a manifest mismatch;
- the K1 validation failing, or the K1 cross-check being disjoint;
- a missing authorization.

**Exports are exact.** `arb.upper()` rounds at the ambient context precision. During development, exports taken
outside the certifying context were therefore silently rounded outward at 53 bits: sound, but it invalidated precision
measurement. Endpoints are now `mid ∓ rad` as exact dyadic rationals, independent of the ambient precision, and
the export radius is no longer passed through a 30-bit `mag`.

## 4. Whole-cell soundness (Phase 4)

Fix `e` in the closed cell, `|e − e0| ≤ ρ`. `ρ̄` is the certified upper endpoint of `ρ`; every rule is
nondecreasing in `ρ`, so using `ρ̄` is sound. All norms are the sup norm on the reachable state set, and all
constants are cell-uniform: `C ≥ sup‖(I−K_e)^−1‖`, `k_i ≥ sup‖K_i‖`, `j_i ≥ sup‖J_i‖` for `i ≤ 4`. These are the
frozen drift-aware tables, adjudicated SOUND.

**Lemma A (source chain, order 3).** For a candidate `X̂_3` constant in `e`, each of the following bounds
`‖X̂_3 − X_3(e)‖`:

- **Cascade.** Subtract the true order-3 recursion from the candidate residual identity at `e`:
  `X̂_3 − X_3(e) = res(e) + Σ_(i=0..3) C(3,i) K_i(e) (X̂ − X)_(3−i)(e)`, taking `J_i` for `S_r`. Here
  `‖res(e)‖ ≤ res(e0) + ρ̄ sup‖∂_e res‖ = delta_cell` (Aux3's certified envelope, a mean-value bound valid because
  only operators depend on `e`). The lower orders are bounded by the frozen whole-cell values (orders ≤ 2) and the
  already-bounded order 3 of the predecessor, following the strictly increasing dependency order
  `h_1 → … → h_4 → S → W`.
- **Taylor.** `X̂_3 − X_3(e) = (X̂_3 − X_3(e0)) − ∫_(e0)^e X_4`, so the bound is `ε_mid + ρ̄ T[X,4]`, where
  `T[X,4] ≥ sup_cell ‖X_4‖` is the frozen norm tower of the TRUE object (aux_refine, orders ≤ 4).
- `S_0`, `Sclosed`: `ε_mid + ρ̄ sup_cell|S_0^(4)|`, drift-aware with `He_5` roots (tabulated).

Both are upper bounds on the same quantity, so their `min` is one too.

**Lemma B (new rung).** Let `G = F'''`.

- **Midpoint.** `(I−K_(e0))(Ĝ − G(e0)) = res_G(e0) + K_3(F̂−F) + 3K_2(D̂−D) + 3K_1(Ĥ−H) + (Src3 − S''')` at `e0`,
  so `‖Ĝ − G(e0)‖ ≤ C(δ_G + k_3ε_F + 3k_2ε_D + 3k_1ε_H + ε_Src3) = ε_mid`.
- **Cascade.** The same identity at `e` gives
  `C(delta_cell_G + k_3 ε̄_F + 3k_2 ε̄_D + 3k_1 ε̄_H + ε̄_Src3)`, with the whole-cell errors from refine2 (adjudicated
  `REFINE2_SOUND`) and Lemma A.
- **Taylor.** `ε_mid + ρ̄ TF_4`, where `TF_4 ≥ sup_cell ‖F^(4)‖`. Differentiate the resolvent equation four times:
  `F^(4) = (I−K)^−1[Σ_(i=1..4) C(4,i) K_i F^(4−i) + S^(4)]`, so `TF_4 = C(Σ C(4,i) k_i TF_(4−i) + T[S,4])`. Here
  `TF_n` for `n ≤ 3` is any bound on `sup_cell ‖F^(n)‖`, and both the norm tower and
  `sup‖F̂_n‖ + (whole-cell error of F̂_n)` qualify. The engine takes their `min`, with the cascade value used for
  `n = 3`, so no quantity depends on itself.
- **Cell.** `min(cascade, Taylor)`.

**Lemma C (export).** `|X̂(x0) − X(e)(x0)| ≤ ‖X̂ − X(e)‖` because `x0 = (0,0)` is reachable. The coefficients are
exact, so `R'''_m(e) ∈ centre ± Σ|c| ε̄` for every `e` in the cell. `L` and `U` are exact endpoints of an outward
enclosure: `centre` is an Arb ball, and the radii are radius-zero upper bounds.

**Order-4 dependency, stated explicitly.**
- The whole-cell step uses sup bounds of TRUE fourth derivatives (`T[h,4]`, `T[S,4]`, `T[W,4]`, `TF_4`, `S_0^(4)`),
  and only as **norm-only majorants**. They are built from existing cell norms `k_1..k_4`, `j_0..j_4` and `He_5` roots.
- No order-4 candidate, residual or certified enclosure exists or is needed, and no new constant is introduced.
- The step is not the Aux3 self-consistent tower: there is no `q_N` and no fixed-point condition, so it cannot fail
  to exist. Its only risk is width.

## 5. K1 inputs (Phase 5)

`k1_inputs.validate` refuses unless V01–V10 hold:
- manifest and record bytes, the frozen `hash_v2` scientific hash, and producer identity;
- geometry equal to `cells.json` (`e0` = exact midpoint, `ρ` = exact half width);
- m blocks exactly {1,2,3,5}, with detector and cell repeated in every block;
- exact outward `R/D/R2` intervals with `mag = max|·|`, and `M_R2 = mag(R2_interval)`;
- status PASS, and **`target_gate` PASS with `strictly_inside_minus2_2` for every m on every consumed record**.

The composite closure does not enforce the target gate (PB6 note), so this producer does. Cell 309 (right endpoint
≥ 2) is flagged `endpoint_region`. Its target gate passes for m = 1, 2, 3, 5 on the committed copy.

The real front-end also requires the recomputed order 0–2 intervals to intersect the sealed record's; bit-equality is
recorded, not required. Both are enclosures of the same quantity, and the host runtime may differ from the sealed
checkpoint.

**PB2 note, carried forward.**
- At `10769e07`, P5X L5 was mathematically bound but not independently reviewed.
- It was reviewed afterwards at `879792d0`: PASS_WITH_SCOPE_LIMITATION (R only, qualitative, not independent by agent
  family), with `HIDDEN_C4_REQUIREMENT_IN_K5B = NO`.
- This producer neither relies on nor strengthens that review.

## 6. Cell-0 width forecast (from committed magnitudes; no R''' computed)

Every term of `ε_mid(G_r)` is nonnegative, so `ε_mid(G_r) ≥ C·3k_1·ε_H,mid(r)` and
`cascade ≥ C·3k_1·ε_H,cell(r)`. Hence `ε̄(G_r) = min(cascade, ε_mid + ρ̄TF_4) ≥ C·3k_1·ε_H,mid(r)`.

The values below use the committed, hash-bound Aux5 records. `k_1` is recovered exactly from their recorded
`ρ·C·2k_1`. The forecast assumes the recomputation reproduces the sealed midpoint values, as historical determinism
did.

| cell | r | C | k_1 | ε_H,mid | **C·3k_1·ε_H,mid** (radius lower bound) | C·3k_1·ε_H,cell |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 1232.8 | 0.7979 | 9.00·10³ | **2.66·10⁷** | 4.92·10⁷ |
| 0 | 1 | 1232.8 | 0.7979 | 2.46·10⁴ | **7.25·10⁷** | 1.34·10⁸ |
| 0 | 4 | 1232.8 | 0.7979 | 1.59·10⁴ | **4.68·10⁷** | 8.64·10⁷ |
| 309 | 0 | 5.78 | 0.7971 | 1.38·10⁻² | 0.19 | 21.3 |
| 309 | 4 | 5.78 | 0.7971 | 1.85·10⁻² | 0.26 | 108 |

**Consequence.**
- At CUSUM cell 0, `L_0 > 0` requires `R'''_1` on the cell to exceed ≈ 2.7·10⁷. For m = 2 it must exceed
  `½(2.66 + 7.25)·10⁷ ≈ 5·10⁷`.
- The committed refine2 majorant of `sup_cell ‖F_0'''‖` is itself 4.9·10⁷. The GammaTilde audit's `R'(0)` scale is
  O(10).
- The frozen feasibility oracle's `Q2` therefore very likely returns `L ≤ 0 → STOP` for the CUSUM route. That is a
  statement about this producer's certified radius, not about `R'''`.
- The binding term is the **frozen midpoint curvature error at `C ≈ 1233`**, inherited from K1's degree-12,
  `e0`-anchored base solve. It is not the order-4 tower.
- A repair must shrink `ε_H,mid` (and `ε_D`, `ε_F`) near `e = 0`, e.g. with a higher-accuracy base solve for the
  order-3 producer's own candidates or a point certificate at exact `e`. Precision will not do it.

## 7. Governance (Phases 9, 13)

**Real-cell qualification: NOT_AUTHORIZED.**
- No pre-result repository mechanism lets a real CUSUM cell qualify a producer while being excluded from K5
  evidence.
- The design's L4 choice is the owner's (DESIGN.md §6), and the frozen oracle requires probe cells to be fixed
  before any `R'''` value exists.
- `REAL_CELL_AUTHORIZATION_REGISTRY.json` is frozen EMPTY and pinned by sha256 in `cusum_order3.py`. Any entry
  changes the producer identity.

**Operator-level integration uses synthetic polynomials only.**
- Part QO runs `g_residual` on the real CUSUM Arb kernels, Pair branches, Bernstein range and truncation allowances,
  with synthetic degree-12 polynomials at synthetic drifts. It is compared pointwise on reachable states against
  independent float quadrature of the defining integrals.
- No collocation, candidate solve, DAG object or `R'''` is involved.

**No future probe packet.** It is not prepared, because the producer is not QUALIFIED (section 6 and `RESULT.md`).
