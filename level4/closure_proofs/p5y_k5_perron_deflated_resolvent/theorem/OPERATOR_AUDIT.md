# First-principles audit of the frozen CUSUM operator K_e (campaign K5_PERRON_DEFLATION_FEASIBILITY)

Everything here is read off frozen code and frozen theorem texts. The float numbers at the end are operator-only,
NON-CERTIFIED design inputs. They are never evidence.

## 1. The operator actually used by the proof stack

| item | frozen value / definition | source |
|---|---|---|
| state space | reachable closure X = {(p, m) ∈ [0,5]²: p = 0 or m = 0 or p + m ≤ h − 2k = 4} | `rebaseguard_certify/geometry.py::in_reachable_closure`; Bernstein cover `reachable_pieces` (triangle r = p+m ∈ [0,1] ∪ [1,4], axis pieces p ∈ [4,5], m ∈ [4,5]) |
| function space | B(X), bounded Borel functions, sup norm on X | every C certificate: "sup norm of bounded functions on the reachable CUSUM state set" |
| parameters | h = 5, k = 1/2, c = h + k = 11/2 | `ra_certifier` constants, `cusum_raw.py` |
| kernel | (K_e f)(p, m) = ∫_{m−c}^{c−p} φ(z+e) f(T(p,m;z)) dz, T = (max(0, p+z−k), max(0, m−z−k)) | `cusum_raw.collocation`, `_kernel_polynomials(…, z_weight=0)` |
| e-dependence | only through the weight φ(z+e); the survival window and T are e-free | same |
| evaluation point | x0 = (0,0) (node (0,0)) | `cusum_raw.assemble` |
| dimension | infinite (continuous state with atoms on the axes and at (0,0)); the degree-12 tensor Chebyshev grid (169 nodes) is only a *proposal* device, never the certified operator | R2_DESIGN §4 item 5 |

Invariance: for x ∈ X and z in the survival window, T(x, z) ∈ X (if both coordinates stay positive then p' + m' = p + m − 1 ≤ 4;
otherwise the image is on an axis with the free coordinate < h). So K_e : B(X) → B(X).

## 2. Structure

- **Positivity.** K_e ≥ 0 (nonnegative weight).
- **Sub-Markov.** K_e 1 = 1 − h_1 with h_1(x) = 1 − Φ(u+e) + Φ(l+e) ∈ (0, 1) the one-step alarm probability.
- **Atom.** T(x, z) = a := (0,0) iff z ∈ [β, α] = [m − k, k − p] (nonempty iff p + m ≤ 1); [β, α] lies inside the survival
  window. Hence, exactly,

      K_e = K̂_e + k_{a,e} ⊗ δ_a,     k_{a,e}(x) = ∫_β^α φ(z+e) dz,   (K̂_e f)(x) = ∫_{window ∖ [β,α]} φ(z+e) f(T(x,z)) dz.

  K̂_e is the chain killed on alarm *or* on return to a. This is the frozen "origin piece" of the R3 C_o0 certificate
  (`resolvent_certificate.certify(kind="odd")` subtracts `_kernel_piece(w, "origin", β, α, …)`).
- **Mass balance.** k_a + h_1 + K̂_e 1 = 1.
- **σ-symmetry.** σ(p, m) = (m, p) fixes a; σ K_e σ = K_{−e}, σ K̂_e σ = K̂_{−e}, k_{a,−e} = k_{a,e} ∘ σ. At e = 0, K_0 and K̂_0
  commute with σ.
- **Irreducibility.** From every x ∈ X the chain reaches a before alarm with positive probability (drive both
  coordinates down with small increments), so the atom is accessible; aperiodicity: k_a(a) = P(|z+e| ≤ 1/2) > 0.

## 3. Relation to the resolvent used by the R derivatives

The K1 DAG (`IMPLEMENTATION_MAP.md`, `propagate.py`):

    F_r = (I − K_e)⁻¹ S_r,   D_r = (I − K_e)⁻¹ (K_e' F_r + S_r'),   H_r = (I − K_e)⁻¹ (K_e'' F_r + 2 K_e' D_r + S_r'')
    R_m = (1/m) Σ_{r<m} F_r(x0) + Σ_{t<m} (1/t − 1/m) Σ_{r<t} (K^{t−r−1} S_r)(x0)       (and the same for R', R'')

Every certified error in the stack is (I − K_e)⁻¹ applied to a residual, bounded by a scalar C ≥ ‖(I − K_e)⁻¹‖:
C_upper (one-sided block bound, 1233 at e = 0, 514–1233 on the front) in K1, C_e0 ≤ 469.77 in R3/R4. The frozen
DAG rules are

    eps(F) = C (λ_F + σ_0),   eps(D) = C (λ_D + k1 eps(F) + σ_1),   eps(H) = C (λ_H + k2 eps(F) + 2 k1 eps(D) + σ_2)

so the order-1 and order-2 errors carry C² and C³.

## 4. The slow mode, identified

For bounded positive operators on B(X), ‖(I − K)⁻¹‖ = ‖(I − K)⁻¹1‖ = sup_x E_x[τ] (the ARL). At e = 0 this is ≈ 465, the
two-sided ARL of the (h, k) = (5, 1/2) CUSUM. So the "Perron mode" is the quasi-stationary (regenerative) mode:

- By the rank-one atom split, for |z| > r(K̂_e): z − K_e = (z − K̂_e)(I − (z − K̂_e)⁻¹ k_a ⊗ δ_a), so z is in the spectrum iff
  Φ_e(z) := δ_a (z − K̂_e)⁻¹ k_a = Σ_{t≥1} z^{−t} f_t(e) = 1, with f_t = P_a(T_a = t < τ) ≥ 0 (renewal equation).
- Φ_e is strictly decreasing on (r(K̂_e), ∞) with Φ_e(1) = p_e = P_a(T_a < τ) < 1, so there is at most one real root
  λ_e ∈ (r(K̂_e), 1); f_1 > 0 (aperiodicity) makes |Φ_e(z)| < Φ_e(|z|) for non-real z, so λ_e is the unique spectral
  point of maximal modulus in |z| > r(K̂_e), and Φ_e'(λ_e) < 0 makes it a simple pole.
- Right eigenfunction r_e = (λ_e − K̂_e)⁻¹ k_a > 0, left functional ℓ_e = δ_a (λ_e − K̂_e)⁻¹ ≥ 0 (a positive measure).

| audit field | answer |
|---|---|
| (all rows of this table are INFORMATIONAL; nothing in theorem AD uses λ_e) | |
| PERRON_MODE_UNIQUE | YES in the region \|z\| > r(K̂_e) (renewal-equation root). Existence needs Φ_e(r(K̂_e)+) > 1; it is not needed by the deflation route, which never uses λ_e |
| PERRON_MODE_SIMPLE | YES (Φ_e' < 0 at the root) |
| PERRON_MODE_POSITIVE | YES (r_e > 0, ℓ_e ≥ 0) |
| LEFT_RIGHT_NORMALIZATION | ℓ_e(r_e) = −Φ_e'(λ_e)·… any positive normalization; the deflation route uses instead the e-independent functional δ_a and needs none |
| SPECTRAL_GAP_STRUCTURE | 1 − λ_e ≈ D_e / E_a[T_a ∧ τ-weighted return time] with D_e = 1 − p_e (mean-value theorem on Φ_e); subdominant spectrum lies in \|z\| ≤ max(r(K̂_e), \|λ₂\|) |

**Is the large constant really the Perron mode?** Yes, and exactly so: (I − K_e)⁻¹ = Ĝ_e + h_e ⊗ ν_e / D_e (theorem AD,
lemma 2), and at the atom the whole amplification is the scalar 1/D_e ≈ 69 multiplying ν_e(1) = E_a[τ ∧ T_a] ≈ 6.8:
ARL(a) = 6.8 × 69 ≈ 465. The rest of the operator (the taboo resolvent Ĝ_e) is positive with ‖Ĝ_e‖ = sup_x E_x[τ ∧ T_a] ≈ 16.
The large constant is therefore a regeneration count, not a pseudospectral effect.

**σ-parity at e = 0.** Ĝ_0 commutes with σ and a is σ-fixed, so ν_0(f) = (Ĝ_0 f)(a) = 0 for every σ-odd f: the Perron
(atom) channel is switched off exactly on odd sources. This is the mechanism behind C_o0 (R3: C_o0 ≤ sup E_x[τ ∧ T_a] ≤ 20.43)
and the reason slot-1 worked. For e ≠ 0 the channel carries ν_e(f) ≠ 0 generically.

## 5. Nonnormality / conditioning

| quantity | float (degree-12/20 grid, NON-CERTIFIED) | comment |
|---|---|---|
| spectral projector ‖P‖∞ = ‖r‖∞‖ℓ‖₁/ℓ(r) | 1.015 (e = 0) → 1.022 (e = 0.1135) | benign |
| eigenvector condition (2-norm) | 2.75 → 2.73 | benign |
| spectral-deflated ‖(I − K)⁻¹(I − P)‖∞ | 11.28 → 11.13 | the R-series float diagnostic |
| taboo ‖Ĝ‖ on reachable nodes | 15.77 → 16.09 (degree 20; 15.49 degree 12) | the atom-deflated complement |
| r(K̂) | 0.911 → 0.914 | r(K̂) ≤ 1 − 1/‖Ĝ‖ is certified by any supersolution |
| λ₂ of K | 0.714 → 0.737 | |
| D_e | 0.01460 → 0.02243 (e = 0 → 0.12) | 1/D ≈ 69 → 45 |
| Sherman–Morrison defect | 0 to machine precision | lemma 2 checked on the grid |

So the spectral projection is well-conditioned here, but that does not make it certifiable: the complement operator
(I − P)K(I − P) is not positive, so its norm cannot be certified by a supersolution, and certifying P needs an enclosed
eigenpair of an infinite-dimensional operator. The atom route has a *positive* complement (Ĝ), whose sup norm is
exactly ‖Ĝ1‖ and is certified by one polynomial supersolution with the frozen Pair kernel and Bernstein machinery. That
is decisive. The price is a slightly larger complement constant (≈ 16 against ≈ 11).

## 6. Dependence on e, m and detector

- e: only through φ(z+e); ‖∂_e^n K̂_e‖ ≤ E|He_n(Y)| (Y standard normal), uniformly in e. The atom functional δ_a is
  e-independent. Every constant in §5 varies by < 3 % (Ĝ, τ_a) or smoothly (D) across [0, 0.13].
- m: none. The operator, the atom and D_e are m-independent; m enters only through which F_r, W terms are assembled.
- detector: CUSUM only. SR has no K1 records (B2) and a different state space; nothing here transfers.
