# CUSUM signed certified order-3 producer: design (not built, not run, not authorized)

```text
K5_B_COUNTERSIGNATURE                  = PASS_WITH_SCOPE_LIMITATION   (d7d3c08b; separate Claude session, not human, not a different model family)
B3                                     = CLOSED                       (CLOSED_BY_SESSION_INDEPENDENT_COUNTERSIGNATURE)

ORDER3_PRODUCER_DESIGN                 = PASS
REFERENCE_KERNEL                       = PENDING_SYNTHETIC_QUALIFICATION
SYNTHETIC_QUALIFICATION                = NOT_YET_RUN (protocol frozen in this commit)

CERTIFIED_REAL_CUSUM_ORDER3_PRODUCER   = NOT_BUILT
REAL_INTERVAL_QUALIFICATION            = NOT_DONE
B1_NO_CERTIFIED_ORDER3_PRODUCER        = OPEN

SCIENTIFIC_K5_PROBES_AUTHORIZED        = NO
FULL_K5_PRODUCTION_AUTHORIZED          = NO
```

Scope: **CUSUM only.** SR has no K1 inputs (B2) and a measured fourth-order tower failure
(`AUX3_SR_FEASIBILITY_FAIL`). An SR producer is not designed here.

## 1. What K5-B needs, and what does not exist

Theorem K5-B consumes, per cell `C_k` and per `m`, a **signed** lower bound `L_k ≤ inf_{C_k} R'''_m`. The frozen
oracle's `Q2` also reads a signed upper bound `U` (the counterexample signal). The readiness audit (`e8680998` §5–6)
established the gaps:

| Needed | In the CUSUM Aux3–Aux5 records |
|---|---|
| Order-3 source candidates `h_j:3`, `S_r:3`, `W_(r,j):3` with midpoint residuals | **yes**, as `auxiliary_third_derivative_evidence_v1` |
| Signed values of anything at order 3 | **no**: every stored value is `mag_fraction`, an unsigned magnitude |
| The resolvent rung `F_r:3` (`r = 0..4`): candidate plus certified residual | **no** |
| Order-3 error propagation through the resolvent | **no** |
| All-m assembly at order 3 | **no** |
| A whole-cell order-3 bound (a fourth-order tower, or an order-3 cellwise cascade) | **no** (towers to order 4 exist only as norm-only majorants inside `aux_refine`) |
| Signed order 0–2 candidates to seed from | **no**: the sealed records hold residual bounds, not polynomials, so the base solve is redone |

## 2. Objects (continuing the frozen recursions one order)

In the raw variable, `(I − K_e) F_r = S_r` and `W_(r,j) = K_e W_(r,j−1)`. Candidates are state-only polynomials,
constant in `e`. Differentiating three times with the Leibniz rule:

```text
F_r'''    = (I − K)^−1 [ K_3 F_r + 3 K_2 F_r' + 3 K_1 F_r'' + S_r''' ]            the NEW rung F_r:3
W_(r,j)'''= Σ_(i=0..3) C(3,i) K_i W_(r,j−1)^(3−i)                                 exists (Aux3)
S_r''', h_j''', S_0''' (closed form)                                              exist (Aux3)
R_m'''(e) = Σ_(r<m) (1/m) F_r'''(e)[x0] + Σ_(1≤t<m) Σ_(r<t) (1/t − 1/m) W_(r,t−r−1)'''(e)[x0]
```

The assembly coefficients are the frozen `e`-independent table (`assembly.coefficients`). The frozen docstring states
they serve every derivative order ("the SAME exact positive rational coefficients serve k = 0, 1, 2"). Order 3 is
the same statement for the same reason: the coefficients are constant in `e`.

**Layer 1 (float, proposes).** Solve `(I − K) Ĝ_r = dddK F̂_r + 3 ddK D̂_r + 3 dK Ĥ_r + Ŝ_r:3` on the frozen
grid, using `aux_collocation.collocation_order3` for `dddK`. Round to a degree-12 dyadic candidate exactly as for
`H_r`. Nothing new about degree, quadrature, nodes or precision.

## 3. Certified rules (Layer 2 disposes)

Norm constants are the cell-uniform drift-aware table: `C ≥ sup ‖(I−K_e)^−1‖`, `k_i`, `j_i` for `i ≤ 4`. The
table exists to order 4 (`sharp_norms.table(orders=4)`), and `He_n` roots are tabulated to `n = 5`, so
`sup_cell |S_0^(n)|` is available for `n ≤ 4`. **No new constant is required.**

### 3.1 Midpoint (at `e0`)

`δ_G` is the certified Bernstein range of the residual `(I − K)Ĝ − K_3 F̂ − 3K_2 D̂ − 3K_1 Ĥ − Ŝ:3` at `e0`,
plus the frozen truncation allowances `Z_RANGE·sup·eps_zi(i)` for `i = 0..3`. It is the same `certify()` path as
`H_r`. Then

```text
ε_G,mid = C ( δ_G + k_3 ε_F,mid + 3 k_2 ε_D,mid + 3 k_1 ε_H,mid + ε_S3,mid )
```

*Proof.* Subtract the true equation from the candidate residual identity:
`(I−K)(Ĝ − G) = res + K_3(F̂−F) + 3K_2(D̂−D) + 3K_1(Ĥ−H) + (Ŝ:3 − S''')`. Take norms. For `r = 0` the source is
the closed form `Sclosed:3`. The midpoint `ε_F, ε_D, ε_H` are the frozen *midpoint* DAG values, and `ε_S3,mid` is
Aux3's `midpoint_order3_eps`.

**Signed midpoint enclosure**: `R_m'''(e0) ∈ Σ c·(Ĝ_r[x0] ± ε_G) + Σ c·(Ŵ:3[x0] ± ε_W3)`, in Arb, with outward
endpoints.

### 3.2 Whole cell: two valid bounds per object, combined by `min`

For every object `X` of order `n ≤ 3` (`F_r` and `W_(r,j)`):

```text
cascade  ε^c_n = C ( δ_n + ρ Env_n + Σ_(i≥1) C(n,i) k_i ε^x_(n−i) + ε_S,n + ρ T[S,n+1] )
         Env_n = k_1 ‖X̂_n‖ + Σ_(i≥1) C(n,i) k_(i+1) ‖X̂_(n−i)‖            (≥ sup_cell ‖∂_e residual‖)
Taylor   ε^t_n = ε_n,mid + ρ T[X, n+1]
         T[F,n] = C ( Σ_(i≥1) C(n,i) k_i T[F,n−i] + T[S,n] ),  n ≤ 4        (norm-only tower of the TRUE object)
cell     ε^x_n = min(ε^c_n, ε^t_n)
```

W uses the same shape with `Σ_(i=0..n)` and no factor `C`. *Proof of the cascade.* For `e` in the cell,
`(I−K_e)(X̂_n − X_n(e)) = res_n(e) + Σ C(n,i) K_i(e)(X̂ − X)_(n−i)(e) + (Ŝ_n − S_n(e))`. Then
`‖res_n(e)‖ ≤ δ_n + ρ sup‖res_n'‖`, and `res_n' = −K_1 X̂_n − Σ C(n,i) K_(i+1) X̂_(n−i)`, because the candidates are
constant in `e`. *Proof of Taylor.* `X̂_n − X_n(e) = (X̂_n − X_n(e0)) − ∫ X_(n+1)`. Both are upper bounds on the
same quantity, so their `min` is valid, and so is every cascade that consumes a `min`.

For orders `n ≤ 2` the producer may substitute the frozen, adjudicated refined whole-cell values (`refine2`, and
`aux_refine` for W) where they are smaller. They are valid bounds on the same quantities.

### 3.3 Export (signed)

```text
centre_m = Σ c·Ĝ / Ŵ:3 [x0]      rad_m = Σ |c| ε^x_3      L_m = lo(centre_m − rad_m)      U_m = hi(centre_m + rad_m)
```

This is one predeclared rule for every cell and every `m`. Nothing is chosen after results. Both components
`(ε^c_3, ε^t_3)` are recorded per object, so a reader can see which one bound.

Record, `rebaseguard.p5y.k5.order3-export.v1`, one per `(cell, m)`:
- `R3_mid_interval {lo, hi}`, `R3_cell_lower_L`, `R3_cell_upper_U`, `sign_determinate`, as exact dyadic rationals;
- per-object `ε_mid`, `ε^c`, `ε^t`, `δ`, towers;
- producer identity: manifest hash, commit, runtime contract, bound to the checkpoint.

These records are **separate from** the K1 records. K1 is not re-exported, re-sealed or modified.

## 4. Reference kernel and what it qualifies

`code/order3_algebra.py` implements §3.1–3.3 literally over `Fraction` with the sup norm. The operators, norms and
sources come from the caller. `code/manufactured.py` supplies analytic systems `K(e) = Σ A_p (e−c)^p` and
`S_r(e) = Σ s_rp (e−c)^p`. Their true `F_r^(n)(e)` and `W^(n)(e)` are exact, via truncated power series, and their
norm constants are rigorous, via the triangle inequality over monomials.

The frozen `config/QUALIFICATION_PROTOCOL.json` tests:

| id | Question |
|---|---|
| QN1 | Do the rules contain the exact truth (objects, assembly, export) at `e0` and on 17 exact grid points, on 15 trials? These are scalar and 3×3, random or controlled, with exact or noisy candidates. |
| QN2 | Is each rule load-bearing? Eight mutations must each be caught on a designated trial whose unmutated run is clean: order-3 Leibniz coefficients; drop `k_3 ε_F`; drop `3k_1 ε_H`; midpoint-as-cell; Taylor without tower; assembly without W; wrong coefficient; lower-bound sign. |
| QN3 | Exact arithmetic only (no float in the kernel or systems) |
| QN4 | Fence: stdlib imports only; no reference to cell tables, records, exports, the CUSUM kernel, backends, network or subprocess |
| QN5 | The reference coefficient rule equals the frozen `checkpoint.json` assembly table |
| QN6 | Byte-identical replay in a fresh process |

**What a QN PASS does *not* show.** It says nothing about:
- Arb outward rounding or Bernstein range soundness (both already adjudicated upstream);
- whether the CUSUM operators satisfy the norm assumptions;
- whether any real `L_k` is positive.

It qualifies the **error algebra** the producer must implement, and gives a reference implementation for
differential testing of the Arb code.

## 5. Ladder to a scientifically qualified producer

| Level | Content | Scientific? | Status |
|---|---|---|---|
| L0 | This design, the reference kernel, QN1–QN6 | no | this namespace |
| L1 | Arb `Order3Certifier` in a new successor namespace. It extends the Aux3 certifier by **explicit wiring** (no module assignment, per `no_monkeypatch.py`), adds `F_r:3`, and adds the midpoint and cell propagation of §3 | no | not started |
| L2 | Differential tests: run the L1 code on `manufactured.py` systems supplied as exact Arb balls, with operators given as matrices; require `L1 ⊇ reference` and soundness against exact truth, with the same mutation matrix | no | not started |
| L3 | Identity layer: producer manifest v4 via the `make_aux5.py` pattern; identity kind v4 with Aux3–Aux5 identities rejected; runtime contract v3 reused as-is; fail-closed controls | no | not started |
| L4 | Host determinism A/B on `rebaseguard-vultr-02` under the frozen runtime contract | **decision needed**, see §6 | not started |
| L5 | Scientific feasibility: the frozen oracle (CUSUM `{0,221,309}`) or a new predeclared successor oracle (the audit's suggestion is `{0,148,305}`) | **yes** | **not authorized** |

## 6. Governance constraints and open decisions

- **No mutation hooks in the producer.** `mutation=` exists only in the reference kernel. L1 code has no test-only
  branch on the certifying path.
- **L4 input choice is the owner's decision.**
  - Aux3–Aux5 qualified determinism on far-field cells 318/323. For an order-3 producer, running any frozen cell
    computes `R'''` of a real `(D,m)`: that is scientific output, even outside `(0,2]`.
  - The alternatives are (a) determinism on manufactured inputs only, which is weaker because it does not exercise
    the CUSUM kernel path; or (b) an explicit authorization naming the cells, with results sealed and not consumed
    by K5.
  - This design does not choose.
- **Oracle choice is the owner's decision.** The frozen oracle cannot be edited. Using `{0,148,305}` needs a new
  oracle, frozen before any order-3 value exists.
- **B3 is closed by `d7d3c08b` and independent of this work.** That countersignature does not qualify a producer,
  and this design does not strengthen the countersignature. Whether K5-B's premises bind to the K1 records is a
  separate question, handled by the premise-binding audit (`p5y_k5b_k1_premise_binding_audit/`).

## 7. Technical risk (stated before any result)

- **Cell 0 width.**
  - H3a near 0 needs `L_0 > 0`, i.e. a certified width below `6a3`.
  - The cascade at order 3 carries `3k_1 ε^x_H`, and the frozen whole-cell `R''` enclosure at CUSUM cell 0 is wide
    (`M_R2 ≈ 1.7·10⁴`, audit §9). The cascade route is therefore expected to be useless at cell 0.
  - The Taylor route carries `ρ·T[F,4]`. Aux3 measured the norm-only towers overstating true derivatives by
    500–53000× at cell 321.
  - Sign-determinacy at cell 0 is therefore a **real risk, not a formality**.
- **Mitigation that exists on paper (not implemented, and must be chosen before any probe).**
  - Second-order Taylor at order 3: `ε_mid + ρ‖X_4(e0)‖ + (ρ²/2) T[X,5]`. It needs:
    - a midpoint order-4 rung `F_r:4` with order-4 sources;
    - `k_5` and `j_5` (the norm table stops at order 4);
    - `He_6` roots for `sup|S_0^(5)|` (tabulated only to `n = 5`).
  - Each is a deliberate table extension, not a tuning knob.
- **Cost.** The audit's measured figure, 0.75–1.10 CPU-h per CUSUM cell, stands. Nothing here re-estimates it.
