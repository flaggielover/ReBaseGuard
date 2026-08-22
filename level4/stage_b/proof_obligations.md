# Stage B — proof obligations and their status

Every row is either discharged by ordinary mathematics (with the proof written
out in `theorem.md`) or by validated numerics (with the artifact named). No row
may be marked closed on the strength of a float computation.

## 1. Analytic obligations

| # | Obligation | Status | Where |
|---|---|---|---|
| A1 | exact mathematical definition of `F_1` and its correspondence to the frozen model | CLOSED | `theorem.md` §0; `tests/test_frozen_correspondence.py` |
| A2 | well-posedness: `tau < ∞` a.s., `E[tau] < ∞`, `z_tau ∈ L¹`, `G` bounded | CLOSED | `theorem.md` L0 + L2 |
| A3 | live-region enclosure and forward invariance | CLOSED | `theorem.md` L1 |
| A4 | uniform killing / resolvent bound `‖(I−K_e)^{−1}‖ ≤ n/q_n` | CLOSED | `theorem.md` L2; `src/killing.py` |
| A5 | odd symmetry `F_1(−e) = −F_1(e)` — **proved, not assumed** | CLOSED | `theorem.md` L3 |
| A6 | `C¹` dependence on `e`; `F_1'` even | CLOSED | `theorem.md` L4 |
| A7 | `G` is the unique bounded solution of `G = TG`; `T` monotone | CLOSED | `theorem.md` L5 |
| A8 | derivative equation `(I−K_e)G' = (∂_eK_e)G + ∂_e r_e` | CLOSED | `theorem.md` L6 |
| A9 | odd map + `F(e*) = −e*` ⟹ period-2 with multiplier `[F'(e*)]²` | CLOSED | `theorem.md` L7 |
| A10 | `|multiplier| < 1` ⟹ locally attracting 2-cycle | CLOSED | `theorem.md` L8 |

**A5 matters.** Had odd symmetry been only numerically observed, the multiplier
would have had to be certified as `F_1'(I)·F_1'(−I)` with two independent
enclosures. Because L3 is a proof, `[F_1'(I)]²` is legitimate. The two-variable
form is nonetheless computed as a cross-check (B8).

## 2. Computer-assisted obligations

| # | Obligation | Status | Artifact |
|---|---|---|---|
| C1 | rigorous enclosure of `G(e)` | see certificate | `certificate/root_certificate.json` |
| C2 | rigorous enclosure of `G'(e)` over an interval | see certificate | `certificate/root_certificate.json` |
| C3 | nonzero root: existence + uniqueness in `I`, `0 ∉ I` | see certificate | `certificate/root_certificate.json` |
| C4 | multiplier enclosure strictly inside `(−1,1)` | see certificate | `certificate/root_certificate.json` |

## 3. What must NOT be conflated

Stage B treats these as four different things and the report keeps them apart:

1. high-precision floating point — **not** rigorous;
2. Monte Carlo evidence (Stage A Gate 4.2) — **not** rigorous;
3. numerical convergence of the Claude Science Bellman solver under grid
   refinement — **not** rigorous, and in particular that solver is *midpoint
   collocation* (`grid.cell(p + z_c − k)` projects the continuum destination
   onto a cell using the sub-interval midpoint), so wrapping it in Arb would
   certify the discretization rather than the map;
4. a genuine enclosure of the true continuous-state operator — what Stage B
   builds.

The Claude Science solver is used here only (a) to place grid cells, which
cannot affect validity, and (b) as an independent consistency check.

## 4. Error budget — every approximation source

| Source | Present? | Rigorous bound |
|---|---|---|
| interval rounding | yes | Arb ball radii, outward-rounded to float by `arb_lower`/`arb_upper`; precision recorded in the certificate |
| quadrature error | **no** | each `z`-segment is integrated against the Gaussian in closed form (`Φ`, `φ` differences); no quadrature rule exists in the pipeline |
| domain truncation | **no** | continuation set ⊂ `(−(h+k), h+k)`; outer regions `|z| > z_cut` are pure-alarm and integrated to `±∞` analytically |
| interpolation / projection | yes | the cell partition. Handled by the *monotone bracket*: destinations resolve to a superset of cells and the min/max is taken, so a coarse cell widens the bracket and can never invalidate it |
| iterative solve error | **no** | by monotonicity of `T`, every iterate is already a valid bracket; the iteration may stop at any point |
| float rounding inside the iteration | yes | `ROUNDING_SLACK = 1e−9` applied outward on both sides each iteration; one iteration sums ≤ 10⁴ products of magnitude ≤ 10², so the accumulated error is below `10⁴ · 2^−53 · 10² ≈ 10^−10` |
| state-space escape | n/a | `build_transitions` raises if any continuation segment leaves the enclosed live region, so L1 is checked on the actual grid rather than assumed |
| grid placement from a float profile | yes, but harmless | the grid is chosen using a non-rigorous solve; this changes only the width of a valid bracket, never its validity. The profile and edges are persisted |

## 5. Deliberate scope limits

* only `rho = 1`;
* only `m = 1`, `k = 1/2`, `h = 5`, Gaussian innovations;
* the theorem concerns the **deterministic** map `F_1`, not the noisy
  recursion `E_{j+1} = F_1(E_j) + noise`;
* uniqueness is claimed **only inside the certified interval `I`**, not globally;
* nothing is claimed about the invariant law or bimodality.
