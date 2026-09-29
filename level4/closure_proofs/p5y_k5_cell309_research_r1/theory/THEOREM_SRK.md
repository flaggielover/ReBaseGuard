# Theorem SRK — state-resolved order-0 channel for the theorem-TC / TC-T whole-cell enclosure

**Status.** Written 2026-09-29, before any implementation, any decoy run or any route comparison of this campaign.
It uses no value of R, of any derivative of R, or of any quantity of CUSUM m = 5 cells 305–309. It is target-free
mathematics.

**Disclosed motivation liability.** The idea was conceived after ledgered exposures:
* graph A §2, necessary reading;
* incident 309R1-01, the incident-01 radius shares;
* incident 309R1-02, an in-band informal estimate.

Its motivation-provenance risk is therefore **MEDIUM-HIGH** (see `ledger/INCIDENT_309R1_02_*`). Nothing below depends
on those exposures. Every parameter rule in §7 is fixed here, before any decoy result.

**Notation.** This follows theorem AD (`p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md`) and theorem TC
(`p5y_k5_lower_front_order3/theorem/THEOREM_TC.md`), with the TC-T supplies (`p5y_k5_m5_tail_closure/theorem/
THEOREM_TCT.md`: Lemma G, (P2′) Ĝ := 0, (P3′)).
* X is the reachable closure and B(X) the bounded Borel functions with the sup norm.
* a = (0,0) is the atom.
* K_e is the whole CUSUM kernel and R_e = (I − K_e)⁻¹.
* K_i(e) = ∂_e^i K_e.
* c = h + k (frozen: h = 5, k = 1/2).
* For x = (p, m) the survival window is z ∈ (m − c, c − p), and the kernel weight is φ(z + e).

## 1. State-resolved kernel norms

For x ∈ X, e ∈ ℝ and i ≥ 0 define

    k_i(x; e) := ∫_{m−c+e}^{c−p+e} |He_i(v)| φ(v) dv,        κ_i := E|He_i(Y)|,  Y ~ N(0,1).

For a drift set E define κ̄_i^E(x) := sup_{e ∈ E} k_i(x; e).

**Lemma SK (pointwise kernel bound).** For every f ∈ B(X), x ∈ X, e ∈ ℝ, i ≥ 0:

    |(K_i(e) f)(x)| ≤ k_i(x; e)·‖f‖ ≤ κ_i‖f‖,   and   k_i(x; e) ≤ κ̄_i^E(x) for e ∈ E.

*Proof.* (K_e f)(x) = ∫_{m−c}^{c−p} f(T(x,z)) φ(z+e) dz. This includes the atom sub-window, where T(x,z) = a. The
window and T are e-free (OPERATOR_AUDIT §1). Differentiation under the integral sign is justified by the dominated
convergence argument of Lemma K (theorem AD §1). It gives
(K_i(e) f)(x) = ∫ f(T(x,z)) φ^{(i)}(z+e) dz with φ^{(i)}(v) = (−1)^i He_i(v) φ(v). Then bound |f(T(x,z))| ≤ ‖f‖ and
substitute v = z + e. Finally k_i(x; e) ≤ ∫_ℝ |He_i|φ = κ_i. ∎

**Monotonicity (used by the implementation).** k_i(x; e) depends on (x, e) only through the window
[m − c + e, c − p + e], and it is nondecreasing under enlargement of the window. Hence, for a box
B = [p₀, p₁] × [m₀, m₁] and E = [e_lo, e_hi],

    sup_{x ∈ B ∩ X, e ∈ E} k_i(x; e) ≤ I_i([m₀ − c + e_lo, c − p₀ + e_hi]),   I_i(J) := ∫_J |He_i| φ.

## 2. Weighted resolvent bounds by supersolution

**Lemma SV.** Let E be a drift set and Ψ ∈ B(X) with Ψ ≥ 0. Assume:
* (W) there is W ∈ B(X) with W ≥ 0 and W ≥ 1 + K_e W on X for every e ∈ E;
* (V) there is V ∈ B(X) with V ≥ Ψ + K_e V on X for every e ∈ E.

Then for every e ∈ E, R_e exists, R_e ≥ 0, and R_eΨ ≤ V on X. In particular sup_{e∈E} (R_eΨ)(a) ≤ V(a).

*Proof.*
1. By (W) and the whole-kernel supersolution lemma (theorem AD §4, Lemma T with K in place of K̂): W ≥ 0 gives
   K_eW ≥ 0, hence W ≥ 1, so
   K_e W ≤ W − 1 ≤ θW with θ = 1 − 1/‖W‖ < 1. Positivity then gives ‖K_e^j‖ = ‖K_e^j 1‖ ≤ θ^j ‖W‖. So
   R_e = Σ_j K_e^j converges in operator norm and is positive.
2. Put g := V − K_e V. Then g ≥ Ψ by (V), and V = R_e g because V is bounded and I − K_e is invertible.
3. Hence V − R_eΨ = R_e(g − Ψ) ≥ 0. ∎

(V need not be checked for sign: V ≥ R_eΨ ≥ 0 follows.)

**Definition.** Γ̄_i^E := V_i(a) for a certified pair (W, V_i) with Ψ = κ̄_i^E. By Lemma SV,
Γ̄_i^E ≥ sup_{e ∈ E} (R_e κ̄_i^E)(a).

**Dominance of the channel constant.** For any valid order-0 constant A0 (A0 ≥ sup_{e∈E} E_a[τ], Lemma SM(d)):
(R_eΨ)(a) ≤ ‖Ψ‖·(R_e1)(a) ≤ A0‖Ψ‖. Equality in the first step holds iff Ψ = ‖Ψ‖ almost everywhere for the occupation
measure μ_{a,e}(·) = Σ_n P_a(X_n ∈ ·, n < τ) (the "refuted family" of constant weights, RSO). SRK is strictly better
exactly when the weight is non-constant on the occupation support.

## 3. Theorem SRK (order-0 channel of theorem TC with Ĝ := 0)

**Setting.**
* Theorem TC §1 with the TC-T premise supplies: fixed candidates F̂, D̂, Ĥ, and Ĝ := 0 (P2′).
* Certified sups s_F, s_D, s_H ≥ ‖F̂‖, ‖D̂‖, ‖Ĥ‖ on X.
* Midpoint bound f_H ≥ ‖φ''(e0)‖.
* σ3 ≥ ‖S_r'''(e0)‖ and σ4 ≥ sup_{e ∈ C} ‖S_r⁗(e)‖ ((P3′)), plus the implementation's redundant ε3 := eps_src[3] ≥ 0.
* Cell C = [e0 − ρ, e0 + ρ], and a valid supply (A0, A1, A2) for the cell (Lemma G, Lemma Dv′ r2, their componentwise
  minimum, or any other valid supply).
* A certified pair (W, V_i), i = 1, 2, 3, 4, on E = C, giving Γ̄_i := Γ̄_i^C.

Define the unchanged TC quantities:
* f_G := 3k₁s_H + 3k₂s_D + k₃s_F + σ3 + ε3;
* Env4 := σ4 + 6k₂s_H + 4k₃(s_D + ρs_H) + k₄(s_F + ρs_D + ρ²s_H/2) (frozen drift-aware norms k_i);
* p0, p1, p2 as in theorem TC §3.

Define the state-resolved coefficients:

    B3 := min( A0·f_G ,  A0·(σ3 + ε3) + 3s_H·Γ̄_1 + 3s_D·Γ̄_2 + s_F·Γ̄_3 )
    B4 := min( A0·Env4 , A0·σ4 + 6s_H·Γ̄_2 + 4(s_D + ρs_H)·Γ̄_3 + (s_F + ρs_D + ρ²s_H/2)·Γ̄_4 )

**Statement.** For every e ∈ C:

    |F_r''(e)(a) − Ĥ(a)|  ≤  rad_r^SRK := A0·f_H + ρ·B3 + (ρ²/2)·B4 + 2·A1·p1 + A2·p0
                          ≤  rad_r     =  A0·p2 + 2·A1·p1 + A2·p0.

Consequently the TC enclosure 𝓗_m, built exactly as in theorem TC §3 with rad_r replaced by rad_r^SRK and |Ĝ_r(a)| = 0,
contains R''_m(e) for every e ∈ C, and it is contained in the TC-T enclosure built from the same inputs.

**Proof.**
1. *Error identity.* From theorem TC §4 steps 1–2:
   E''(e)(a) = [R_eφ''(e)](a) + 2[∂R_e φ'(e)](a) + [∂²R_e φ(e)](a).
   Here E''(e) = F''(e) − Ĥ, because Ĝ = 0. The last two terms are bounded by 2A1‖φ'(e)‖ + A2‖φ(e)‖ ≤ 2A1p1 + A2p0,
   exactly as in theorem TC.
2. *Positivity.* By (W) on E = C, R_e ≥ 0 (Lemma SV). So |[R_e f](a)| ≤ (R_e|f|)(a) for every f.
3. *Pointwise Taylor.* e ↦ φ(e) is analytic into B(X) (TC §4 step 1), and point evaluation δ_x is a bounded linear
   functional. So e ↦ φ(e)(x) is C⁴ with derivatives φ^{(j)}(e)(x). With t = e − e0:

       |φ''(e)(x)| ≤ |φ''(e0)(x)| + |t|·|φ'''(e0)(x)| + (t²/2)·sup_{s∈C} |φ⁗(s)(x)|.

4. *Order-3 piece.* By (P2′),
   φ'''(e0) = S'''(e0) + 3K₁(e0)Ĥ + 3K₂(e0)D̂ + K₃(e0)F̂.
   Lemma SK gives |φ'''(e0)(x)| ≤ Ψ3(x) := σ3 + ε3 + 3s_H κ̄_1(x) + 3s_D κ̄_2(x) + s_F κ̄_3(x). Also
   |φ'''(e0)(x)| ≤ ‖φ'''(e0)‖ ≤ f_G.
5. *Order-4 piece.* φ⁗(s) = S⁗(s) + 6K₂(s)Ĥ + 4K₃(s)(D̂ + tĤ) + K₄(s)(F̂ + tD̂ + t²Ĥ/2). This is TC (P3) with Ĝ = 0,
   where the K₁ term vanishes. With |t| ≤ ρ and Lemma SK:
   sup_s|φ⁗(s)(x)| ≤ Ψ4(x) := σ4 + 6s_H κ̄_2(x) + 4(s_D + ρs_H) κ̄_3(x) + (s_F + ρs_D + ρ²s_H/2) κ̄_4(x).
   It is also ≤ Env4 (TC (P3)).
6. *Apply R_e.* Use positivity and linearity of R_e, split into the three pieces of step 3, and bound each piece's
   image at a by the smaller of two valid bounds:
   * (R_e|φ''(e0)|)(a) ≤ f_H·(R_e1)(a) ≤ A0 f_H, because (R_e1)(a) = E_a[τ] ≤ A0 (Lemma SM(d));
   * (R_e|φ'''(e0)|)(a) ≤ min(A0 f_G, (σ3+ε3)A0 + 3s_HΓ̄_1 + 3s_DΓ̄_2 + s_FΓ̄_3) = B3;
   * (R_e sup_s|φ⁗(s)|)(a) ≤ min(A0 Env4, A0σ4 + 6s_HΓ̄_2 + 4(s_D+ρs_H)Γ̄_3 + (s_F+ρs_D+ρ²s_H/2)Γ̄_4) = B4.

   Hence |[R_eφ''(e)](a)| ≤ A0f_H + |t|B3 + (t²/2)B4 ≤ A0f_H + ρB3 + (ρ²/2)B4.
7. *Dominance.* B3 ≤ A0f_G and B4 ≤ A0Env4 give rad_r^SRK ≤ A0(f_H + ρf_G + ρ²Env4/2) + 2A1p1 + A2p0 = rad_r.
8. *Assembly.* The assembly and W terms follow theorem TC §4 step 4 verbatim. Radii are nonnegative and assembly
   coefficients are nonnegative, so the SRK enclosure is contained in the TC-T one. ∎

## 4. Which consumer term SRK replaces

Only the order-0 channel term A0·p2 inside rad_r = A0·p2 + 2A1·p1 + A2·p0. It is replaced by
A0·f_H + ρ·B3 + (ρ²/2)·B4.

Unchanged:
* A1·p1 and A2·p0;
* the centres Ĥ_r(a) and the W enclosures;
* the assembly and the intersection with R2_interval;
* M, g_hi, the direct clause Γ = g_hi + ρ·x_hi·M, and the supply S;
* all K1/TC-T inputs.

In the binding-regime closed form (graph A §0.2), SRK replaces A0·P̄2 by
(1/5)Σ_r [A0 f_H,r + ρB3,r + (ρ²/2)B4,r], and nothing else.

**Governance class.** SRK changes the enclosure theorem, a non-constant input computation, and adds operator
certificates that are not a Lemma G / Dv′ supply. Under floor r2 it is therefore **closure-only**.

## 5. Monotonicity, degenerate and equality cases

* **Monotone in every input.** rad_r^SRK is nondecreasing in s_F, s_D, s_H, σ3, σ4, ε3, f_H, A0 and Γ̄_i. So any
  valid, larger substitute keeps it valid, and any tighter certificate can only shrink it.
* **Never worse.** rad_r^SRK ≤ rad_r always (min construction). Equality holds iff both mins select their first
  argument.
* **Degenerate cases:**
  * **D1:** κ̄_i ≡ κ_i on the occupation support. At small |e| (long excursions through full windows) the gain tends
    to 1. SRK then reduces to TC-T.
  * **D2:** s_F = s_D = s_H = 0. B3 → A0(σ3+ε3) and B4 → A0σ4. There is no gain on the source parts; SRK-0 does not
    state-resolve sources (see §6).
  * **D3:** ρ = 0. SRK and TC-T coincide (midpoint only).
  * **D4:** an invalid certificate (V fails (V) anywhere). The theorem gives nothing; the implementation must refuse.
* **Boundary behaviour of the min.** When the two arguments of a min are equal the value is the same either way, so
  no tie rule is needed.

## 6. Extension SRK-1 (source resolution; stated, not required)

For r ≥ 1, S_r = J_e h_r with (J_e g)(x) = ∫_{window} (z+e)φ(z+e) g(T(x,z)) dz, so
∂_e^i[(z+e)φ(z+e)] = (−1)^i He_{i+1}(z+e)φ(z+e).

Then |S_r'''(e0)(x)| ≤ Σ_{i≤3} C(3,i) j_i(x; e0) N_{r,3−i}, where:
* j_i(x; e) := ∫_{window+e} |He_{i+1}|φ;
* N_{r,n} ≥ ‖h_r^{(n)}(e0)‖ (frozen towers).

For r = 0, S_0 = φ(c−p+e) − φ(m−c+e) is explicit. Replacing σ3 (resp. σ4) in Ψ3 (resp. Ψ4) by the pointwise
min(σ3, source envelope(x)) is valid by the same proof. The implementation of SRK-1 is deferred; SRK-0 (§3) is the
object of this campaign.

**Deferral record (2026-09-29, engineering scope; independent of any target quantity).** SRK-1 needs four new
things:
* a He₅ weight (index 5) for σ4;
* a new closed-form weight for r = 0, namely |S₀^{(n)}(e₀)(x)| as a function of both window endpoints;
* pinned tower norms N_{r,n}, taken from the frozen `tct_rule.h_towers` (midpoint tower and cell tower);
* a verifier mode for each of the above.

Under ROUTE_SELECTION_RULE S, a component enters only when it is ready (C5). SRK-1 is therefore OUT of the first
freeze package. Omitting a min-composed component can never invalidate the route. Note the index identity
j_i(x; e) = k_{i+1}(x; e): the SRK-0 certificates Γ̄_1..Γ̄_4 already cover every σ3 weight of SRK-1.

## 7. Target-free parameter rules (fixed now, before any decoy result)

| parameter | rule |
|---|---|
| drift block | E = C, the cell itself. If a cover by sub-blocks is used: the fixed uniform split into N_E = 4 equal sub-blocks, Γ̄_i := max over sub-blocks (a max over a cover is valid) |
| weights | exactly κ̄_1..κ̄_4 over E. No other weight, no per-cell selection |
| box cover for the envelope and the check | the frozen C1b base cover with h = 1/4, adaptive halving up to 4 extra levels on failure |
| polynomial family | total-degree Chebyshev tensor basis (C1b declaration D3) on the ladder d ∈ {8, 10, 12}. Γ̄_i := min over the rungs that certify (a min of valid bounds is valid) |
| float proposal | collocation at the C1b sample set, RHS = float κ̄_i at the samples. Proposals are untrusted and every one is re-checked exactly |
| repair | additive: V' = V + λW with λ := max(0, −r_min) + μ·max(1, sup Ψ), where r_min is the certified lower bound of V − K_eV − Ψ over the cover and μ = 2⁻²⁰ (the margin that lets an independent verifier certify) |
| tolerance | none. Every inequality is exact rational or outward rigorous |
| failure | if no rung certifies for some i, Γ̄_i := +∞, so B3, B4 fall back to the TC-T terms. This is safe and never a retry with changed parameters |

## 8. Adversarial tests the implementation must pass (planned before implementation)

1. **Too-small weight (mutant).** Certify V against a shrunken window (e.g. κ̄_i computed on [m−c+e+1/4, c−p+e]).
   The independent verifier must reject it against the true κ̄_i.
2. **Taboo instead of whole kernel (mutant).** A V solving V ≥ Ψ + K̂_eV. The whole-kernel check must fail.
3. **Scaled-down V (mutant).** (1 − 2⁻⁸)·V must fail.
4. **Narrowed drift block (mutant).** A certificate valid at e_c only must fail on E.
5. **Dropped λ (mutant).** A repaired certificate with λ := 0 must fail when r_min < 0.
6. **Wrong Hermite index (mutant).** Use k_{i−1} for i must fail. This is a control that can fail; it is only
   meaningful where k_{i−1} < k_i pointwise, which is checked first.
7. **Monte Carlo consistency (positive control).** The empirical mean of Σ_{n<τ} κ̄_i(X_n) from the atom, at the
   decoy drift, must lie below V(a) up to a stated 5-σ allowance, and the float solve must lie below V(a).
8. **Constant-weight identity (degenerate control).** Ψ ≡ 1 must reproduce an Ā-type certificate: V(a) ≥ the float
   ARL and V(a) ≤ the independent Ā certificate at the same rung. This is a control that can fail.
9. **Dominance assembly test (two-sided).** rad_r^SRK recomputed independently from the same fields must equal the
   producer's value exactly. Planted assembly mutants must be caught: a dropped min, a wrong coefficient 3↔6, and ρ
   instead of ρ²/2.
10. **Determinism and serialization.** Two runs must be byte-identical. The certificate must round-trip through JSON
    with exact rationals. Malformed certificates (missing keys, a non-rational string, a negative λ, a mismatched
    block) must be refused.

Decoys:
* the real kernel at drifts outside [6/5, 13/5] and its mirror, restricted to e ≤ 1 so that decoys never bracket the
  band (QUARANTINE_AMENDMENT_2 R2.1 rationale);
* synthetic geometries (h, k) ≠ (5, 1/2) at any drift. These do not transfer to the target kernel.

## 9. Amendment A1 (2026-09-29, decoy-driven, target-free; before any real-geometry run)

The first synthetic-geometry profiling (h = 3, k = 1/2, E = [1/2, 1/2 + 1/32]) showed two things.
* A single e-independent V must absorb the genuine e-variation K₁(e)V·δe of the residual across the block.
* Splitting boxes on the *sign* of the residual never terminates for a float proposal whose residual is ≈ 0 ± ε.

Two changes follow. Neither concerns any quarantined cell or band drift, and neither changes any statement of §§1–3.

**Lemma SV′ (pointwise-in-e families).** Let W_e = W₀ + (e − e_c)W₁ and V_e = V₀ + (e − e_c)V₁, with bounded W_j, V_j.
Suppose that for every e ∈ E:
* W_e ≥ 0 and W_e ≥ 1 + K_eW_e on X;
* V_e ≥ Ψ + K_eV_e on X.

Then for every e ∈ E, (R_eΨ)(a) ≤ V_e(a). Hence sup_E (R_eΨ)(a) ≤ max(V_{e_lo}(a), V_{e_hi}(a)), since V_e(a) is
affine in e.

*Proof.* Apply Lemma SV at each fixed e with the pair (W_e, V_e). ∎

Implementation rules, replacing the corresponding rows of §7:

| parameter | amended rule |
|---|---|
| certificate family | e-affine: V_e = V₀ + (e − e_c)V₁ and W_e = W₀ + (e − e_c)W₁. The float proposals come from two collocation solves at e_lo and e_hi (P₀ = midpoint average, P₁ = difference quotient). The exact check runs over X × E with e as a Taylor-model variable |
| repairs | W: multiplicative, W' = (1+η)W_e with η = −r/(1+r), as in C1b. V: additive, V' = V_e + λW', with λ = max(0, −r_min) + μ·max(1, sup Ψ) and μ = 2⁻²⁰ (unchanged) |
| Γ̄_i | max over the two block endpoints of V'_e(a), exact |
| box refinement | C1b's tightness rule, not a sign rule. After a full pass, a box is halved (≤ 4 extra levels) iff its certified lower margin lies below m_c − (1/4)|m_c| − 2⁻⁴⁰, where m_c is the minimum over boxes of the centre margin |

Validity: e-affine families are a special case of Lemma SV′, and the refinement rule affects tightness only.

## 10. Amendment A2: taboo form SRK-T (target-free; a dominance-composition option)

**Lemma SV-T.** Let K̂_e be the taboo kernel: K_e with the atom sub-window removed (theorem AD Lemma K). Suppose that
for every e ∈ E:
* ŵ_e ≥ 0 and ŵ_e ≥ 1 + K̂_eŵ_e on X;
* v̂_e ≥ Ψ + K̂_e v̂_e on X.

Then for every e ∈ E, (Ĝ_eΨ)(a) ≤ v̂_e(a). If moreover D_e ≥ D_lo > 0 on E (a certified lower bound, e.g. the
committed D_lo of the chosen supply's registry), then Lemma SM(c) gives, for every f with |f| ≤ Ψ:

    |[R_e f](a)| = |ν_e(f)|/D_e ≤ (Ĝ_e|f|)(a)/D_e ≤ v̂_e(a)/D_lo.

*Proof.* Lemma SV applies verbatim with K̂_e in place of K_e (Lemma T of theorem AD supplies the Neumann series and
positivity of Ĝ_e). Then use Lemma SM(c). ∎

**Use.** Γ̂_i := max_{e∈{e_lo,e_hi}} v̂_{i,e}(a)/D_lo is an alternative valid value for Γ̄_i. The consumer may use
min(Γ̄_i, Γ̂_i), because both are valid. SRK-T is the analogue of the τ/D_lo branch of Ā_eff, while §2 is the analogue of
the Ā branch.

**Implementation.** `certify_W(..., whole=False)` and `certify_weight` inherit the flag. D_lo is not produced here:
in a formal campaign it would be the committed, pinned registry value of the chosen supply.

**SRK-1a (the cheapest increment; also deferred).** For r ≥ 1, the σ3 part alone needs only two things beyond SRK-0:
* the pinned midpoint tower norms N_{r,n};
* the existing Γ̄_1..Γ̄_4.

It reads

    B3 := min( A0 f_G ,  A0 ε3 + min( A0 σ3 , Σ_{i≤3} C(3,i) N_{r,3−i} Γ̄_{i+1} ) + 3 s_H Γ̄_1 + 3 s_D Γ̄_2 + s_F Γ̄_3 ).

It is valid by §6 and Lemma SV (a min of valid bounds on (R_e|S_r'''(e0)|)(a)). It is deferred only for the coupling
to the internals of `tct_rule.h_towers`, which the formal campaign would have to pin and qualify. It is a
target-free candidate for a later package.
