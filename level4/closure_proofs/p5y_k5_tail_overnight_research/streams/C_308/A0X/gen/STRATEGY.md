# C2b STRATEGY — a cell-independent certification strategy for E_a[τ], τ_a and C_T

Stream C2b (campaign brief §17). Sections 0–7 were fixed before the validation runs; the only earlier executions
were two N=10, e=1 smoke tests, recorded as such in PROGRESS.md step 8. Code: `gen/c2b_*.py` (stdlib only).
Nothing here mentions, uses or is tuned to any cell.

## 0. Model (checked against the docstring of `c11_certifier.py`, lines 1-50)

State x = (p, m) on the reachable set R = {0 ≤ p, m ≤ 5, and p + m ≤ 4 or p = 0 or m = 0}; atom a = (0, 0).
Increment z with z + e ~ N(0, 1). Alarm-free window z ∈ [m − C, C − p], C = K + H = 11/2, K = 1/2, H = 5.
Next state (max(0, p + z − K), max(0, m − z − K)).

    (K_e w)(p, m) = ∫_{m−C}^{C−p} w(next(z)) φ(z + e) dz,     K_e = K̂_e + k_{a,e} ⊗ δ_a,

where K̂_e (taboo kernel) omits the atom window z ∈ [m − K, K − p] (non-empty iff p + m < 1).
The kernel implementation was cross-checked against C11's `kernel_apply` (independent code, exact rationals):
0/28 mismatches, enclosure widths < 1e-33 (`c2b_checks.c11_kernel_check`). A planted wrong reference value
K = 0.4 gives 28/28 mismatches.

## 1. What is certified (exact statements)

Supersolution lemma (standard; THEOREM_AD Lemma T and its whole-kernel form): if w: R → [0, ∞) and
w ≥ 1 + K_e w on R, then E_x[τ] ≤ w(x) for all x ∈ R. Proof: iterating gives w ≥ Σ_{j<n} K^j 1 + K^n w ≥ Σ_{j<n} K^j 1.

| output | statement proved | kernel |
|---|---|---|
| Ā(E) = w(a) | for every e ∈ E: w ≥ 1 + K_e w on R, hence Λ(e) = E_a[τ] ≤ Ā(E) | K_e (whole) |
| τ(E) = ŵ(a) | for every e ∈ E: ŵ ≥ 1 + K̂_e ŵ on R, hence (Ĝ_e 1)(a) ≤ τ(E) | K̂_e |
| C_T(E) = max ŵ | the same certificate, hence ‖Ĝ_e‖ = sup_x (Ĝ_e 1)(x) ≤ max_R ŵ | K̂_e |

E is either a single drift {e} (pointwise) or a block [e_lo, e_hi] whose width is a multiple of the mesh h
(block-uniform). w is the P1 interpolant of a nodal vector, so max_R ŵ is the maximum nodal value (exact).

## 2. Untrusted proposal (a)

Mesh h = 1/N. Nodes: (i, j) with i + j ≤ 4N, plus the axis nodes (i, 0) and (0, j) with 4N < i, j ≤ 5N.

The float proposal solves the *discrete* equations of the family itself. Write K_h = K_e ∘ I_h, where I_h is P1
interpolation on the anti-diagonal triangulation. Every next state lies on an axis or on the anti-diagonal s' = s − 1,
which is a grid line when s is a grid level. So K_h at a node is an exact finite sum of nodal values times Gaussian
segment weights (`c2b_float.FloatKernel.apply`).

The steps:
1. Solve the taboo pair t = 1 + K̂_h t and d = h_1 + K̂_h d by Jacobi iteration (tolerance 1e-13; convergence is recorded).
2. Apply the regenerative identities Λ_h = t(a)/d(a) and V_h = t + (1 − d)Λ_h. These are exact for the discrete chain.
   Check: max |V_h − 1 − K_h V_h| ≈ 5e-13.
3. For a block E, compute proposals at both ends and take g = the nodal maximum over {e_lo, e_hi}.
4. For the whole kernel, g comes from V_h. For the taboo kernel, g comes from t_h.

## 3. Declared family ladder (b)

| rung | family | parameters |
|---|---|---|
| F0 | affine in m, w = β − α·m (the C11/I2 family); comparator rung | (α, β); α on the grid k/256 |
| F1(N) | P1 on the uniform anti-diagonal triangulation, mesh h = 1/N | nodal values α·g + β |
| ladder | N ∈ (10, 20, 40, 80) | each refinement doubles N |

F1 covers quadratic, piecewise-linear-in-m and low-degree bivariate candidates only approximately, and they are not
separate rungs. The reason is that the P1 proposal (§2) solves the discrete equation of the family itself, so its
vertex residual is zero up to iteration tolerance. A fitted polynomial carries a fit residual that enters every
margin (|r| ≤ 2‖g − V‖). This design choice is what allows sub-percent tightness.

## 4. Scaling on a fine ladder (c)

w = α·g + β, with α ∈ {1 + k·2^-12 : k = 0, …, 4096} and β ≥ 0 a dyadic multiple of 2^-52.

1. For each α, compute the smallest β that satisfies all linearised vertex constraints (§5).
2. Choose α to minimise w(a) = α g(a) + β over the ladder. The objective is convex in α, so a ternary search on k is
   used. This selection runs in floats and is UNTRUSTED.
3. Certify the chosen w exactly. If the exact check fails, set k → k + 1 (at most 64 bumps, all recorded).

There is no coarse ladder and no "first rung" rule. The returned α is the ladder point that minimises the certified
value, to 2^-12. For F0, α is the slope on the grid k/256, β is the minimal intercept, and the objective is w(a) = β.

## 5. Exact certification (d)

### 5.1 Drift–position lemma (the block-uniformity device)

Substitute u = p' = p + z − K on the p-branch and v = m' = m − z − K on the m-branch. Then, with s = p + m,
y = p − K − e, η = s − y − 1 = m − K + e, s' = s − 1 and A = max(0, s'):

    T3 = ∫_A^H a(u) φ(u − y) du,          a(u) = w(u, 0)          (p' > 0, m' = 0)
    T2 = ∫_A^H b(v) φ(v − η) dv,          b(v) = w(0, v)          (p' = 0, m' > 0)
    T1 = ∫_0^{s'} c(u) φ(u − y) du,       c(u) = w(u, s' − u)     (both > 0; only when s > 1)
    T4 = w(a) [Φ(−y) − Φ(η)]                                       (atom window; only when s < 1; absent for K̂)

(K_e w)(p, m) = T1 + T2 + T3 + T4 =: Ψ_w(s, y). **The drift enters only through y.** Varying e over [e_lo, e_hi]
is therefore the same as varying y over an interval, and a block-uniform check is a pointwise check on a widened
y-range. Every Gaussian argument at a vertex of a lattice-aligned slab lies on one of two lattices,
t = K + e_lo + d·h (for u − y and −y) or t = K − e_lo + d·h (for v − η and −η).

### 5.2 Vertex values (exact)

At a node, each T-term is a sum over P1 segments of W_k·A(d) + W_{k+1}·B(d), where the segment weights
A(d) = N(t_{d+1} M0 − M1) and B(d) = N(M1 − t_d M0) have M0 = Φ(t_{d+1}) − Φ(t_d) and M1 = φ(t_d) − φ(t_{d+1}).
Φ and φ at lattice points are the C7 rigorous rational enclosures (`c7_gaussian`, 2^-320 outward rounding; the only
change is that √(2π) is computed once). They are stored as integer intervals at scale 2^-128, and the weights are
rounded outward (A, B ≥ 0). The nodal values are exact dyadics, so every vertex bound of K_e w is an exact integer:
there is no rounding inside the sums (`c2b_exact.kernel_nodes`). Upper bounds are used for positive W and lower
bounds for negative W. The atom weight is Φ(K + e − p) − 1 + Φ(K − e − m).

### 5.3 Interpolation error (exact bounds on second derivatives)

The cells are: lower triangles L(i,j) = {(i,j),(i+1,j),(i,j+1)}, upper triangles U(i,j) = {(i+1,j),(i,j+1),(i+1,j+1)},
and the axis segments beyond s = 4. Each cell lies in one s-strip [n h, (n+1)h], and Ψ_w is C² inside a strip.

Take a cell T and an e-slab S. The map (p, m, e) ↦ (s, y) is affine, and w is affine on T. So on each simplex of
the P1 split of T × S, the function w − 1 − I(Ψ) is affine and attains its minimum at vertices. The second-order
Taylor identity then gives

    I Ψ(x) − Ψ(x) = ½ Σ_i λ_i (x_i − x)ᵀ D²Ψ(ξ_i) (x_i − x),
    Σ λ_i (s_i − s)² ≤ r_s²/4,   |Σ λ_i d_s d_y| ≤ r_s r_y/4,

using Popoviciu's variance bound. Hence

    |Ψ − IΨ| ≤ (r_s² |Ψ_ss| + 2 r_s r_y |Ψ_sy| + r_y² |Ψ_yy|)/8,   r_s = h,  r_y = (p-range) + (e-slab width).

**Certified condition (per cell and slab):** min over the vertices of T × S of [w − 1 − (K_e w)_upper] ≥ err(T, S).
Rational arithmetic is used throughout (`c2b_exact.certify`).

The second derivatives come from integration by parts against the P1 kinks. For P1 f on [α, β]:

    ∂²_y ∫_α^β f(u) φ(u−y) du = f(α)(α−y)φ(α−y) − f(β)(β−y)φ(β−y) + f'(α+)φ(α−y) − f'(β−)φ(β−y)
                                 + Σ_{nodes u_k ∈ (α,β)} Δf'_k φ(u_k − y).

Summing T1…T4 and simplifying for s ≥ 1 (q = s-strip index − N), the value terms at u = s' cancel between T1 and
T3, and those at v = s' cancel between T1 and T2:

    Ψ_yy = −a(H)(H−y)φ(H−y) − b(H)(H−η)φ(H−η) − a'(H−)φ(H−y) − b'(H−)φ(H−η)
           + g_m[L(q,0)] φ(s'−y) + g_p[L(0,q)] φ(y)
           + Σ_{u_k∈(s',H)} Δa'_k φ(u_k−y) + Σ_{v_k∈(s',H)} Δb'_k φ(v_k−η) + Σ_{breaks β of c} Δc'_β φ(β−y)
    Ψ_s  = ∫_0^{s'} w_m(u, s'−u) φ(u−y) du − b(H)φ(H−η) + ∫_{s'}^H b'(v) φ(v−η) dv
    Ψ_sy = −g_m[L(q,0)] φ(s'−y) + Σ_{all breaks} Δg_m φ(β−y) + b(H)(H−η)φ(H−η) + b'(H−)φ(H−η)
           − Σ_{v_k∈(s',H)} Δb'_k φ(v_k−η)                       [g_m(0+) = b'(s'+) cancels exactly]
    Ψ_ss = g_m[L(q,0)] φ(s'−y) − Σ_{moving (horizontal) breaks} Δg_m φ(β−y) − b(H)(H−η)φ(H−η)
           − b'(H−)φ(H−η) + Σ_{v_k∈(s',H)} Δb'_k φ(v_k−η).

Here g_p and g_m are the P1 gradient components on a triangle. Along the line s' ∈ (q h, (q+1) h) the pieces are
L(0,q), U(0,q−1), L(1,q−1), …, L(q,0). The breaks are horizontal crossings (moving with s', inside [k h, (k+1) h])
and vertical crossings (fixed at u = (k+1) h).

For s < 1 the T4 terms cancel the value terms at 0:

    Ψ_yy = −a(H)(H−y)φ(H−y) − b(H)(H−η)φ(H−η) + a'(0+)φ(y) + b'(0+)φ(η) − a'(H−)φ(H−y) − b'(H−)φ(H−η)
           + Σ Δa'_k φ(u_k−y) + Σ Δb'_k φ(v_k−η)
    Ψ_sy, Ψ_ss: b(H)(H−η)φ(H−η) + b'(H−)φ(H−η) − b'(0+)φ(η) − Σ Δb'_k φ(v_k−η) (up to sign).

For the taboo kernel with s < 1 the cancellations are lost. The code adds |w(a)|·(|y|φ(y) + |η|φ(η)) to |Ψ_yy| and
|w(a)|·|η|φ(η) to |Ψ_ss| and |Ψ_sy|.

Every term is bounded by |coefficient| times a rigorous upper bound of φ or |t|φ over a lattice-aligned index range.
The bound is φ(0) if 0 is in the range and φ(1) if ±1 is in the range for |t|φ; otherwise it is the endpoint value.
Coefficients (slope jumps) are exact integers at scale 2^-Q·N, so the bounds are exact integers
(`c2b_exact.hessian_bounds`). Sanity checks with w ≡ const reproduce the window mass Φ(H − y) − Φ(η − H) and its
second derivatives.

**Claimed domain.** The bounds hold on the cell × slab, meaning (p, m) in the cell and e in the slab, which are the
ranges used for every φ-bound. They do not hold on the enclosing (s, y) rectangle, and the Taylor points ξ_i lie in
the cell, so the cell is all that is needed.

**Independent check.** Finite differences of an independent float point evaluator (`c2b_pointeval.psi`, which agrees
with brute-force z-quadrature to 5e-9) are compared with the bounds by `c2b_checks.hessian_fd_check_cell`, with
points drawn inside the cell (`c2b_fdcheck.py` → `results/fdcheck_r1.json`). The first version of this check drew
points from the rectangle and reported out-of-domain exceedances (PROGRESS step 17); it is superseded. The bounds
are sharp (FD/bound up to 0.99) and never exceeded in-domain. The planted control (bounds × 0.05) is always flagged.

### 5.4 What is and is not proved

Proved: the statements of §1 for the exact P1 function w with the certified nodal vector, **given** (i) the
correctness of the derivation in 5.3 (a mathematical claim, cross-checked by finite differences but not
machine-proved) and (ii) C7's Gaussian enclosures. Not proved: anything about the float truth. Nystrom values
are proposals only.

## 6. Stopping rule and complexity (e)

**Stopping rule (self-referential; it uses no truth and no target quantity).** Run the rungs N = 10, 20, 40, 80 in
order and stop at the first of these events:
1. The certified value improved by less than γ = 0.25% relative to the previous rung.
2. N = 80 has been reached.
3. The projected cost of the next rung exceeds the budget B = 1200 CPU-s per drift or per block. The projection is
   the measured cost of the current rung × 8, which is the O(N³) scaling.

The reported value is the smallest certified value over the rungs run. Every certified rung is valid, so taking
the minimum is sound. Record every rung, including failures.

**Complexity per drift, mesh N.**

| step | cost |
|---|---|
| Gaussian enclosures | O(N) c7 evaluations (≈ 20N at 5 ms each) |
| proposal | O(N³) per Jacobi sweep × n_it, with n_it ≈ log(1e-13)/log(1 − 1/C_T) (≈ 13 at e = 3, ≈ 130 at e = 1, ≈ 300 at e = 0) |
| vertex margins | O(N³) exact integer multiply-adds (the diagonal sums dominate) |
| Hessian bounds | O(N³) (the diagonal break sums) plus O(N²) suffix sums |
| selection | O(#constraints × log) floats |

A block of width W costs (J + 1) vertex evaluations and J Hessian slabs, where J = W·N.

**Accuracy model.** The certification overhead α − 1 (absolute vertex margin) must dominate err ≈ h²|Ψ''|/8, and
|Ψ''| scales with the size of w near the alarm boundaries. So the overhead is O(h²) at fixed drift and grows with
Λ(e). The Nystrom bias V_h(a) − Λ is also O(h²). The measured values are in C2B_ROUTE_SUMMARY.md.

## 7. Why it is cell-independent (f)

- **Inputs.** The strategy's only inputs are the model constants (K, H), a drift set E and the mesh ladder.
  It reads no registry, cover file, cell index, committed per-cell constant or target file.
- **Where the drift enters.** The drift enters only as the lattice offset K ± e_lo (§5.1). The same code with the
  same declared numerics (P = 128, Q = 40, α-ladder 2^-12, N-ladder, γ, B) certifies any E. The numerics were fixed
  before validation and are generic.
- **Quarantine guard.** Every entry point calls `ov_quarantine.guard_drift` on E. Validation used only
  E ⊂ {0, 1/4, 1/2, 1, 3} and blocks starting at 1/2, 1 and 3 of width ≤ 1/10, all outside [6/5, 13/5].
- **No retuning.** Nothing was selected or retuned after seeing any validation number. The only post-validation
  change allowed by this document is the bump counter in §4, which is part of the declared procedure.
- **What cell independence does not claim.** It does not say that the certified value at some other drift is
  small. It says that the procedure and its proof obligations do not depend on which drift set is given.
