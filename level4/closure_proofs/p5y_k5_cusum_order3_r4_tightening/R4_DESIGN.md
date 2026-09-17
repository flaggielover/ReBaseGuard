# R4 tightening successor: exact odd-block C_o0, local first-cell R⁽⁵⁾ majorant, B01 test power

**Non-scientific, additive.**
- R1 (`e69a0224` / `4a1b20a8`), R2 (`a1dcf1e8` / `327e0e13`) and R3 (`1089ea1e` / `57cbc249`) are byte-identical
  and pinned file by file. R4 imports them and never edits them.
- No real CUSUM cell is evaluated and no `R'''` or `R⁽⁵⁾` value of any `(D,m)` is computed.
- The real-cell authorization registry is frozen **empty**.
- Results are in `RESULT.md`, written after the freeze commit.

## A. B01 test-power gap

**Why B01 escaped in R3.** `B01_M5_USES_ODD_COMPONENT` sums the odd component of the order-5 tower instead of the even
one. At the σ-fixed `x0` only the even part survives. So the mutant's M5 is a *leakage-sized* number, and it is caught
only when that number drops below the exact `max|R⁽⁵⁾|`. The frozen R3 fixtures had majorants 13–600× the truth, and
leakage plus slack stayed above it.

**R4 family `tight_M5`** (`FR4_01`–`FR4_03`). These are new, independently parameterised σ-systems. They were not
calibrated on the R3 result, and their seeds are disjoint from R3's (checked in `tests/test_r4.py`).
- Parameters: conditioning `C_target` ∈ {3, 5, 8}, exact candidates (noise 0), very small `x₁` ∈ {1/4000, 1/3000, 1/2000}.
- Leakage is `O(x₁)`, while the correct local majorant stays within a small factor of the truth.

**Self-test** (part `b01`, gate G09). On every `tight_M5` fixture:
1. the correct method has 0 violations;
2. B01 is detected, and its violations are **only** of kind `M5` or `strategyB`, with **no** `tower`, `anchor` or
   `point` violation (the mutation touches only the final component selection);
3. two sham controls on the same line have 0 violations:
   - `v.t` (a sound superset);
   - `v.e + 0·v.o` (an arithmetic no-op);
4. the correct method and B01 give identical detection at 256 and 384 bits (not precision noise).

## B. Certified σ-odd resolvent bound C_o0

### B1. Architectures compared

Float diagnostics are in `code/operator_audit.py` (non-evidence, gate G05).

| architecture | load-bearing missing piece | decision |
|---|---|---|
| 1. direct odd-block linear solve | a sup-norm operator-to-matrix error bound for the continuous kernel | not certified alone; float value 4.596 is the reference |
| 2. interval inverse / verified matrix solve | same projection error (certifies the matrix, not the operator) | rejected as primary |
| 3. Krawczyk operator | same | rejected as primary |
| 4. interval Newton | same (the problem is linear) | rejected as primary |
| 5. preconditioned Neumann `‖I − A(I − K_o)‖ < 1` | continuous-operator defect; the float matrix defect 3.5e-15 is not load-bearing | rejected as primary |
| 6. Schur / parity block decomposition | none: σ is an exact permutation symmetry at e = 0 | **used**: exact odd block (B2) |
| 7. Perron-mode separation | Perron mode is even (eigenvalue 0.99782); irrelevant to the odd block | informs `C_e0` only |
| 8. spectral-gap bound | spectral radius 0.708 does not bound a non-normal sup-norm resolvent | rejected |
| 9. componentwise bound | none, once the odd kernel is positive | **used**: supersolution on `H` (B3) |

The R3 strong-Markov coupling bound (`C_o0 ≤ 20.4322`) remains valid. It serves as the independent upper reference in
the cross-check (X4).

### B2. Exact odd-block reduction (`code/odd_block_certificate.py`)

**Setting.** `σ(p,m) = (m,p)`, `H = {x ∈ R : p ≥ m}`, `d = p − m`,
`q(x,z) = ((p+z−½)⁺, (m−z−½)⁺)`, survival window `z ∈ [m−c, c−p]`, `c = 11/2`.

1. **Geometry.** For `x ∈ H`, `q(x,z) ∈ H` iff `z ≥ −d/2`. On the interior `q_p − q_m = d + 2z`; the axes and the origin
   atom behave the same way. Also `σq(x,z) = q(x, −d−z)` exactly, including the clipping, and `z ↦ −d−z` maps the
   window onto itself.
2. **Invariance and the projected equation.** `σ` commutes with `K_0`, so the odd subspace is invariant. For odd
   `u = (I−K_0)⁻¹f` and `x ∈ H`:
   `u(x) = f(x) + ∫_{z>−d/2} [φ(z) − φ(−d−z)] u(q(x,z)) dz =: f(x) + (K_o u)(x)`.
   - The reset atom and the diagonal contribute `u = 0` exactly.
   - At exactly `e = 0` there is no even leakage.
   - The load-bearing operator is `K_o` itself; the full operator is never bounded and then projected.
3. **Positivity.** For `z ≥ −d/2`, `|z| ≤ d + z`, so `φ(z) ≥ φ(−d−z)` and `K_o` is a positive operator. Moreover
   `K_o ≤ K̂` (R3), so `Σ_j K_o^j 1 ≤ E_x[τ ∧ T_0] < ∞` and `u = Σ_j K_o^j f`.
   - This series is the unique bounded odd solution: its odd extension solves the full equation, and at the diagonal
     both sides vanish.
4. **Norm.** For a positive operator, the sup-norm resolvent norm equals `sup_H Σ_j K_o^j 1`. If `w ≥ 0` and
   `w ≥ 1 + K_o w` on `H`, induction gives `Σ_{j<n} K_o^j 1 ≤ w`, so
   `‖(I−K_0)⁻¹ f‖ ≤ ‖f‖ sup_H w` for every odd `f` (since `|u(σx)| = |u(x)|`).
   - This is the sup norm on `R`, the norm of the graded proof (R3 A1).
   - The bound is exact in the limit: the minimal supersolution is the odd resolvent applied to 1.

### B3. Certification

**Polynomial form of `K_o w`** (frozen pieces: "up" = p-axis, "both" = interior, "down" = m-axis; `w_s = w∘σ`,
`mid = (m−p)/2`):
- `p+m ≥ 1`: `up(w)[m−½, c−p] + both(w)[mid, m−½] − both(w_s)[½−p, mid] − down(w_s)[m−c, ½−p]`
- `p+m ≤ 1`: `up(w)[½−p, c−p] − down(w_s)[m−c, m−½]`

**Certificate.**
- Margin: `L = w − 1 − (K_o w)_poly − 2·Z_RANGE·sup|w|·ε_z`, where the frozen φ-truncation allowance is charged for both
  halves.
- Bernstein coefficients on the `H`-part of the frozen reachable cover certify `min L > 0`, `min w ≥ 0` and
  `C = max w`. The cover is the triangle parameter `t ∈ [½, 1]` for `r ∈ [0,1]` and `[1,4]`, plus the p-axis tail
  `p ∈ [4,5]`.

**Proposal.** A float collocation of `(I − K_o)g = 1` on the frozen Chebyshev grid, symmetrised, then `w = αg + β`
rounded to an exact dyadic payload. No float is rounded into a bound.

| (α, β, depth) | certified margin ≥ | C_o0 ≤ | status |
|---|---:|---:|---|
| (1.02, 0, 2), (1.05, 0, 2), (1.1, 0, 2), (1.02, 0.1, 2) | < 0 | n/a | not certified (the kink of the symmetric proposal at the diagonal) |
| **(21/20, 1/2, 3)** | **0.0971** | **5.3601** | **frozen** |
| (1.05, 1.0, 3) | 0.1499 | 5.8601 | certified |
| (1.1, 1.5, 3) | 0.2505 | 6.5916 | certified |
| (1.02, 2.5, 3) | 0.2706 | 7.2213 | certified |

- **Scan disclosure.** Every attempt is listed. Any certified supersolution is a valid bound, so the scan selects a
  certificate, not a result.
- **Classes.** The acceptance classes (`config/FEASIBILITY_CRITERION_R4.json`) are the requested ones, unchanged.
- **Constant shift.** β > 0 adds margin exactly where the kernel mass vanishes (near the diagonal); the float
  cross-check located the β = 0 failure at `(p,m) ≈ (1.97, 1.68)`.

### B4. Independent cross-check (`code/odd_block_crosscheck.py`, gate G04)

- **X1/X2.** Gauss–Legendre quadrature of the **raw** kernel applied to the odd extension of `w`, with no split at
  `−d/2` assumed, at 2,127 `H` samples; the margin must be ≥ the certified margin − 1e-6.
- **X3.** The reflected kernel is nonnegative.
- **X4.** Float odd-block norm (4.596) ≤ C_o0(R4) ≤ C_o0(R3).

## C. R⁽⁵⁾ majorant

### C1. Routes audited

| route | finding |
|---|---|
| 1. parity-reduced order-5 recurrence | the R3 graded tower already is this; kept as the engine |
| 2. norm-only operator majorant | the tower; its slack came from the **anchors**, not the recurrence |
| 3. direct differentiated resolvent equation | identical to the tower edges `F⁽ⁿ⁾ = A⁻¹[Σ C(n,i) K_i F⁽ⁿ⁻ⁱ⁾ + S⁽ⁿ⁾]` |
| 4. componentwise derivative bounds | graded (e, o, t) components, kept |
| 5. cancellation at e = 0 | **used**: the wrong-parity component of every true object vanishes exactly at e = 0 |
| 6. even/odd derivative structure | **used**: the drift of the right-parity component is bounded by the next order's *leakage* component |
| 7. Hermite source bounds | R3 `sup|S_0⁽ⁿ⁾|`, n ≤ 6, kept |
| 8. j₅ / He₆ | R3 extension, kept |
| 9. local first-cell bounds | **used**: hull `{0} ∪ [0, x₁]` only; anchors from the point run at e = 0, no whole-cell run |
| 10. transport-specific bound | order-4 alternative `R'''(e) ≥ R'''(0) − x₁·sup|R''''|`: DEV budget 8.9e3 vs 6.1e2 via M5 at C_o0 = 6, rejected |

**DEV budget** (committed magnitudes only, no `R⁽⁵⁾` value). The R3 anchored M5 = 4.71e10 was dominated by the
Strategy-A **whole-cell** errors inside the anchors: the cell drift, 2.58e5 at the `R` level. Scalar candidate suprema
were also assigned to both parity components; for example `F'''` odd part 1.07e5 fed `C_e0·4k₁` into `F⁽⁴⁾` even.

### C2. Local exact-parity anchoring (`code/local_r5.py`)

For a true object `X` of order `n ≤ 3` with exact parity at `e = 0`, and `e ∈ [0, x₁]`:
- **(a) Wrong parity.** `‖P_w X⁽ⁿ⁾(e)‖ ≤ x₁ · sup‖P_w X⁽ⁿ⁺¹⁾‖`.
- **(b) Right parity.** `‖P_r X⁽ⁿ⁾(e)‖ ≤ ‖P_r cand‖ + ‖P_r(X⁽ⁿ⁾(0) − cand)‖ + x₁ · sup‖P_r X⁽ⁿ⁺¹⁾‖`, where the last
  term is the next order's leakage component.
- **(c) Total.** `‖X⁽ⁿ⁾(e)‖ ≤ (a) + (b)`.

**Iteration.**
- The sups are components of the current tower, and the point errors are the graded point-run errors at e = 0.
- A componentwise minimum of valid bounds is valid, so every iterate `anchors_k = min(anchors_{k−1}, local(tower_{k−1}))`
  gives a valid tower. The iteration count is frozen at 12.
- `M5 = Σ|c| sup‖P_e F⁽⁵⁾‖` keeps the R3 semantics.

**Strategy B then needs only the point run:** `L_B = lo(I_0) − (x₁²/2)·M5`.

### C3. Manufactured qualification and cross-check

- **Fixtures** (gate G08): 8 R4 fixtures, each checked against exact rational truth on 17 grid points, for every
  component of every tower node and every local anchor, plus the point interval, Strategy B and M5. The families are:
  - tight M5;
  - parity-pure CUSUM-like;
  - parity-leak;
  - slow even mode;
  - well-conditioned odd;
  - near-boundary.
- **Regression:** R3 FC1–FC5 rows.
- **Mutations** (gate G10): R3 B01–B06 verbatim, plus L01–L05 on `local_r5.py`.
- **Independent truth** (gate G11, `code/m5_crosscheck.py`):
  - the Cauchy integral of the model evaluated with python-flint `acb` / `acb_mat` solves at 256 bits;
  - a fresh re-typing of the model and coefficient table, with no Taylor recurrence;
  - an analyticity radius from a Neumann bound.

  Agreement with the exact derivatives, and `M5 ≥` the Cauchy max, are required.

## D. Forecast, sensitivity map, blocker (`code/forecast_r4.py`)

**Inputs.** Committed Aux5 cell-0 magnitudes (R3 input construction, unchanged), certified `C_o0` (R4) and `C_e0` (R3)
via `constants_r4.load_certificates()`, frozen and He₆ norms on `[0, x₁]`.

**Binding forecast** (G factor 1, m = 1). The point radius comes from assumption A1 (R3). The candidate suprema and
graded point errors of that point run anchor `local_r5`. The penalty is `(x₁²/2)·M5`.

**Classes.**
- Overall: the frozen R3 scale `S* = 33.4066`.
- C_o0 and transport: the requested engineering labels.

**Sensitivity grid.**
- Rows: `C_o0` ∈ {certified R4, 10, 6, 4.68 (non-certified)}, with the point radius and model M5 recomputed per row.
- Columns: `M5` ∈ {model, 1e10, 1e9, 1e8, 1e7}.
- Every cell except (certified R4, model) is marked hypothetical.

**Dominant blocker** (frozen). If total ≤ S*, NEITHER_INFRASTRUCTURE_READY. Otherwise:
- penalty ≥ 2 × point → R5_DOMINANT;
- point ≥ 2 × penalty → C_O0_DOMINANT;
- else BOTH_COMPARABLE.

**Governance disclosure.** The forecast code was run in DEV before the freeze, on the same committed magnitudes,
because it has no seed. The classes, `S*` and the labels were fixed before R4 (by R3 and the R4 request) and are not
changed.

## E. Qualification (`config/PRE_RESULT_GATES_R4.json`, `config/QUALIFICATION_PROTOCOL_R4.json`)

**Gates.** G01–G17 as frozen.
- R3 suites are re-executed unchanged with the frozen R3 protocol:
  - wiring 12/12, whose payload hash must equal the frozen R3 evidence;
  - certificate-verifier mutations 3/3;
  - He₆, parity and R2 soundness.
- R4 adds:
  - odd-certificate mutations O01–O04;
  - local mutations L01–L05;
  - the B01 self-test;
  - the cross-checks.

**Verdict, B1 and next step.** Mechanical from the frozen rules.

**DEV calibration.** Seed-disjoint (fixture seeds + 900000), used only to find defects before the freeze. It found two:
- `FR4_08_near_boundary` (`C_target` 50, `x₁` 1/10) violated the manufactured rig's own precondition
  `sup‖K‖ < 1` for both seed sets (1.003, 1.032). It was re-parameterised to `C_target` 20, `x₁` 1/20, which is still
  close to the resolvent boundary. The certificate and method were not changed.
- The fail-closed part crashed because a mutated `constants_r4` loaded from a temp directory could not resolve its
  repository path. The test mutant now pins the namespace path; production code is unchanged.

After the fixes, every DEV part passed: odd-certificate mutants 4/4, R3 certificate mutants 3/3, R3 wiring 12/12
(payload hash identical to the frozen R3 evidence), R⁽⁵⁾ + local mutants 11/11, B01 self-test, both cross-checks,
fail-closed 8/8, fences, regressions and forecast replay.

**Completion protocol.** The runner writes `RUN_STATE.json` (pid) first, then the result, then `RUN_COMPLETE.json`
(result sha256), or `RUN_FAILED.json` on an exception. The waiter reads these files and `/proc/<pid>/cmdline`, never
`pgrep -f` on its own command text.

## F. Real-cell policy

`REAL_CELL_QUALIFICATION = NOT_AUTHORIZED` throughout. If R4 reaches QUALIFIED_FOR_GOVERNED_REAL_CELL_QUALIFICATION,
a separate proposal is **prepared, not executed**. It leaves open, as an explicit decision for the governance owner,
whether the first real cell is:
- (A) pure qualification and permanently excluded from science; or
- (B) a preregistered scientific probe that simultaneously qualifies the producer.
