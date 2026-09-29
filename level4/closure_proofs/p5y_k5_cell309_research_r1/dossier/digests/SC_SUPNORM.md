# Digest: Theorem SC (composite-sup premise supply), code, and REVIEW_STREAM_D_R1

Firewalled digest. Sources (NS = `level4/closure_proofs/p5y_k5_tail_overnight_research/`):
`streams/D_309/SUPNORM_THEOREM.md`, `streams/D_309/code/{d309_core.py, d309_supnorm_fsm.py, d309_sct.py,
d309_hermite.py, d309_hermite_tf.py}`, `reviews/REVIEW_STREAM_D_R1.md`.
Redaction tokens: `[TAIL-NUMBER REDACTED]`, `[TAIL-COMPARISON REDACTED]`, `[LATENT-PROXY REDACTED]`.
All numbers kept are synthetic FSM, real-kernel test functions at the declared non-target drifts {0, 1/4, 1/2, 1, 3}
(no Λ / E_a[τ] / supersolution values appear), or generic.

---

## 0. Status (SUPNORM_THEOREM.md header), near-verbatim

Research theorem for the 2026-09-28 overnight campaign.
* General: every cell and every detector; not a 309 patch.
* **Never evaluated on CUSUM m = 5 cells 305–309, and on no drift in [1.2, 2.6].**
* Validation: synthetic finite-state (FSM) families with exact truth, and the real CUSUM kernel at the declared
  non-target drifts {0, 1/4, 1/2, 1, 3} only.
* Rule S8: no committed tail-cell share, factor or margin in the document.

Route state: theorem and certificate **VALIDATED_NON_TARGET**; real-cell use **BLOCKED** (candidate payloads never
serialized; U1/U2/U3 open).

## 1. Setting and notation (§1), verbatim-close

Setting (theorem TC §1, `p5y_k5_lower_front_order3/theorem/THEOREM_TC.md:9-14`): cell `C = [e0 − ρ, e0 + ρ]`; source
index r; true source `S = S_r(e)`, `F = F_r = R_e S`; fixed candidates `F̂, D̂, Ĥ, Ĝ ∈ B(X)`; `t = e − e0`,
`F̃ = F̂ + tD̂ + (t²/2)Ĥ + (t³/6)Ĝ`, `φ(e) = S(e) − (I − K_e)F̃(e)`.

TC-T (`THEOREM_TCT.md:44-61`) takes `Ĝ := 0` and supplies the order-3 midpoint premise by the **surrogate**

    f_G^sur := 3 k1 s_H + 3 k2 s_D + k3 s_F + σ3        (≥ ‖φ'''(e0)‖, TCT :53)

and the whole-cell order-4 premise by the (P3) envelope at `s_G = 0`:

    Env4 := σ4 + 6k2 s_H + 4k3 (s_D + ρ s_H) + k4 (s_F + ρ s_D + ρ² s_H/2)     (TCT :128)

Here `k_i ≥ sup_C ‖K_i(e)‖` and `s_X ≥ ‖X̂‖`. Both are Leibniz triangle inequality + submultiplicativity applied to

    φ'''(e0) = S'''(e0) + 3K1 Ĥ + 3K2 D̂ + K3 F̂                                     (Ĝ = 0; TCT :49)
    φ⁗(e)   = S⁗(e) + 6K2(e) Ĥ + 4K3(e)(D̂ + tĤ) + K4(e)(F̂ + tD̂ + t²Ĥ/2)            (Ĝ = 0; TC :43-44)

## 2. Statements (§2), verbatim-close

**Theorem SC-3 (composite order-3 premise).** Let `Ψ̂3 := 3K1(e0)Ĥ + 3K2(e0)D̂ + K3(e0)F̂`. Let `Ŝ3` be any fixed
function with `‖S'''(e0) − Ŝ3‖ ≤ ε3`. Two bounds:

    (a)  f_G^SC  := B3 + σ3,    B3 ≥ sup_X |Ψ̂3|                   (candidate composite)
    (b)  f_G^SC' := B3' + ε3,   B3' ≥ sup_X |Ŝ3 + Ψ̂3|             (full composite)

Each is a valid TC (P2) order-3 premise: `‖φ'''(e0)‖ ≤ f_G^SC` and `‖φ'''(e0)‖ ≤ f_G^SC'`. So is
`min(f_G^sur, f_G^SC, f_G^SC')`.

**Theorem SC-4w (whole-cell composite order-4 envelope).** If `E4 ≥ sup_{e ∈ C} sup_X |φ⁗(e)|` (φ⁗ as in §1), then E4
is a valid (P3) premise. So is `min(Env4, E4)`.

**Theorem SC-4m / TC⁺ (order-raised Taylor cell).** Suppose `f4 ≥ ‖φ⁗(e0)‖` (a midpoint premise, possibly composite)
and `Env5 ≥ sup_C ‖φ⁽⁵⁾‖`. For `s = |e − e0| = |t| ≤ ρ` (repair r1, review N1):

    p2(s) = f_H + s f_G + s² f4/2 + s³ Env5/6
    p1(s) = f_D + s f_H + s² f_G/2 + s³ f4/6 + s⁴ Env5/24
    p0(s) = f_F + s f_D + s² f_H/2 + s³ f_G/6 + s⁴ f4/24 + s⁵ Env5/120

Then theorem TC §3 and Lemma TC-P (THEOREM_TPT §2) hold with these `p_j(s)`. With `Ĝ = 0`, the norm-only order-5
envelope is

    Env5 = σ5 + 10k3 s_H + 5k4 (s_D + ρ s_H) + k5 (s_F + ρ s_D + ρ² s_H/2)

because `F̃''' = F̃⁗ = F̃⁽⁵⁾ = 0`.

**Proofs.**
* SC-3: `φ'''(e0) = (S''' − Ŝ3) + (Ŝ3 + Ψ̂3)`, triangle inequality. For (a), use `S''' + Ψ̂3` with `‖S'''‖ ≤ σ3`.
* SC-4w: immediate from the definition of (P3).
* TC⁺: (1) Taylor in `B(X)`: `‖φ⁗(u)‖ ≤ f4 + |u − e0|·Env5` on C. (2) integrate in the remainders of φ'', φ', φ,
  e.g. `‖φ''(t)‖ ≤ f_H + s f_G + ∫_0^s (s−v)(f4 + v Env5) dv`, giving p2, p1, p0. (3) TC §4 steps 2–3 unchanged.
* The minimum of valid premises is valid. ∎

**Frozen assumptions.** (P1) of TC; candidates fixed before the certificate is computed, certificate never sees R;
sup norms over the reachable closure X (where TC's norms live); no assumption on the sign of any target quantity.

## 3. Ladder, SC-T (§3)

**Proposition SC-L (ladder).** For exact certificates (B3 = true sup):

    S0 := f_G^sur ≥ S1 := 3‖K1(e0)‖s_H + 3‖K2(e0)‖s_D + ‖K3(e0)‖s_F + σ3
       ≥ S2 := 3‖K1Ĥ‖ + 3‖K2D̂‖ + ‖K3F̂‖ + σ3
       ≥ S3 := ‖Ψ̂3‖ + σ3 = f_G^SC ≥ ‖φ'''(e0)‖.

Steps remove (1) cell-uniform operator norm → midpoint norm; (2) submultiplicativity; (3) cross-term triangle.
`f_G^SC'` also removes the source/candidate triangle.

**Proposition SC-T.** With `E_F = F̂ − F`, `E_D = D̂ − F'`, `E_H = Ĥ − F''` (at e0), differentiating
`(I − K_e)F = S` three times gives the exact identity

    φ'''(e0) = (I − K)F'''(e0) + 3K1 E_H + 3K2 E_D + K3 E_F

so `‖φ'''(e0)‖ ≤ ‖(I − K)F_r'''(e0)‖ + 3k1‖E_H‖ + 3k2‖E_D‖ + k3‖E_F‖`, with `‖E_X‖` bounded by the frozen K1 rules
`eps(F) = C f_F`, etc. (TCT :35-37). Hence: the composite is the order-3 residual of the **true** third derivative,
up to candidate-error terms; the surrogate S0 is the Leibniz triangle bound `Σ C(3,i) k_i ‖F^(3−i)‖ + σ3` of the same
identity; the avoidable slack of the surrogate is the Leibniz gap `S0 − ‖(I − K)F'''‖` minus candidate errors — a
property of F_r and K, not of any target sign.

Validation of SC-T (`code/d309_sct.py` → `validation/D309_SCT_FSM.json`, 48 source-cases): identity exact 48/48;
bound 48/48; comparator control (coefficient 3 → 2 on the K2 term; tests the comparator only) differs 48/48;
‖φ'''‖/‖(I−K)F'''‖ at pert 1e-6 = 1 ± 6·10⁻⁷, at pert 1e-2 = 0.995–1.008; Leibniz gap S0/‖(I−K)F'''‖ (synthetic)
1.27–15.8.

**Relation to atom constants.** SC changes only (P2)/(P3) premises; the TC radius rad = A0 p2 + 2A1 p1 + A2 p0 is
linear in the premises with nonnegative coefficients, so SC composes with **any** A-supply (Lemma G, Lemma Dv′, RSO)
and cannot be absorbed into one.

**Relation to sup norms s_X.** Under SC-3 the s_X leave f_G entirely; under SC-4w they leave Env4 as well; under TC⁺
they remain only in the order-5 envelope (extra factor s). The inputs s_X are not changed, so every identity-gated K1
field is untouched; C6's "zero gain by construction" (tightening s_X, route A1) does not apply. Tightening s_X
remains a separate, gated lever.

## 4. When SC is strictly stronger (§4)

**Proposition SC-S1.** CUSUM kernel `(K_i g)(x) = ∫_{m−C}^{C−p} g(n(x,z)) (−1)^i He_i(z+e) φ(z+e) dz`. Let `X̂` be
continuous and nonzero on the compact reachable set, `i ≥ 1`. Then

    ‖K_i X̂‖ < k_i^true ‖X̂‖,   k_i^true = sup_x ∫_{win(x)} |He_i(z+e)| φ(z+e) dz,

attained at the widest window, the atom: `k_i^true = ∫_{e−C}^{e+C} |He_i| φ`.
*Proof.* (1) x ↦ (K_iX̂)(x) continuous, sup attained at x*. (2) If win(x*) strictly inside the atom's window, strict
inequality since |He_i|φ > 0 a.e. (3) Otherwise x* = a; equality would need X̂(n(a,z)) = ±‖X̂‖ sign He_i(z+e) a.e.;
every He_i, i ≥ 1, has a simple root in [−1, 1], so a root lies in (e − C, e + C) whenever |e| < C − 1 (covers
i = 1..5, repair r1 / review N2); continuity forbids equality. ∎
TC-T's k_i ≥ k_i^true, so on the Gaussian kernel with continuous candidates S2 < S1 ≤ S0 qualitatively.

**Scope of "strict" (repair r1, review N3).** Strictness of the **exact** sup only. Certified B3 carries overhead
(Taylor-form certificate 1.19–1.44× a grid lower bound on the §7 test functions). Strictness does **not** imply a
certified gain.

**Quantitative mechanism.** For i = 1, `∂_e φ(z+e) = ∂_z φ(z+e)`; integration by parts gives
`(K1 g)(x) = [g(n(x,z)) φ(z+e)]_{m−C}^{C−p} − ∫_{win} ∂_z[g(n(x,z))] φ(z+e) dz` (boundary density terms + average
of a directional derivative; Stein). Slack governed by candidate smoothness on the unit Gaussian scale; i = 2, 3
similar with one extra point term per clipping kink.

**Proposition SC-S2.** `S3 < S2` iff, at every state where |Ψ̂3| attains its sup, the three terms 3K1Ĥ, 3K2D̂, K3F̂ do
not all attain their own sups with a common sign.

**Adversarial FSM equality case.** Candidates = sign patterns of the maximising rows of K1, K2, K3 give S3 = S1
exactly (adversarial seed 105 reaches S3/S1 = 1.0; other adversarial seeds 0.47–0.95). Discontinuous; excluded by
SC-S1 on the Gaussian kernel but not on general FSM. Strictness is kernel- and candidate-dependent; SC stated with
min(·) so never worse.

## 5. Computable certificate (§5)

**Lemma HC (Hermite closed form).** For bivariate polynomial w, on each piece of the window `[m − C, C − p]` between
clipping kinks `z = K − p` and `z = m − K`, `n(x,z)` is affine in z, so `w(n(x,z))·(−1)^i He_i(z+e)` is a polynomial in
`u = z + e`. Hence `(K_i w)(x)` is an exact finite combination of Gaussian moments `M_j(A,B) = ∫_A^B u^j φ(u) du`:

    M_0 = Φ(B) − Φ(A),   M_1 = φ(A) − φ(B),   M_j = (j−1)M_{j−2} + A^{j−1}φ(A) − B^{j−1}φ(B).

Implementation `d309_hermite.py` (`moments`, `compose_piece`, `Ki_apply`), rigorous rational φ, Φ from the allowed
pure library `c7_gaussian` (2⁻³²⁰ outward rounding).

**Certificate object** (order-3 composite of SC-3): drift e0; candidate payload hashes; a box cover of X (frozen box
rule, as `c11_certifier.cover`); z-panel width; per box a rigorous enclosure of `{Σ_i c_i (K_i w_i)(x) : x ∈ box}`.
B3 = max over boxes of the enclosure magnitude. Per-box enclosure (`d309_hermite_tf.box_upper_tf`), panel by panel:
(1) image box of n(x,z) for x ∈ box, z ∈ P; (2) each w_i on the image box by a **centred Taylor form** (exact bivariate
shift to the box centre, then `a_00 ± Σ|a_ij| r_p^i r_m^j`); (3) Hermite weight on P by a 1-D Taylor form (weights
summed first when one function serves every order, keeping cancellation); (4) × exact panel mass `Φ(z1+e) − Φ(z0+e)`;
(5) panels inside the window for only some states of the box hulled with 0. Verification = re-evaluation; sound
because each step is an interval enclosure of an exact quantity. For SC-3(b), the Aux3 `S:r:3` payload is added as
one more term and ε3 = Aux3's committed midpoint eps.

**SC-4w** needs the same enclosure uniformly for e ∈ C (interval drift enters only through φ(z+e), He_i(z+e); I1/I2
certify operator constants this way, `c11r_idrift`, read only). **Not implemented.**

## 6. Numerical stability (§6)
1. Exact rationals except φ, Φ at rational points with proven remainders; C11 erratum E5 warns series degrade for
   |t| ≳ 20; for any |e| ≤ 2.6 the arguments satisfy |u| ≤ e + C ≤ 8.1 (safe).
2. Moment recursion multiplies widths by ≤ max(|A|,|B|)^j per order; for j ≤ 16, |u| ≤ 8.1: width < 10^-80.
3. Dependency problem measured: naive monomial interval evaluation (`box_upper_composite`), depth 4, panel 1/16 — sound
   but **vacuous** for degree-9 `w_bump` (certified upper 12458 vs grid lower 1.06 at e = 1/4; 22865 vs 0.59 at e = 3);
   centred Taylor forms: w_bump depth 4 1.31–1.34, depth 5 1.19–1.22, low-degree triple depth 4 1.41–1.44 (certified
   upper/grid lower), converging as boxes shrink. Consequence: degree-12 dyadic candidates must use centred Taylor or
   Bernstein forms; depth and panel fixed by a declared rule **before** any real evaluation, calibrated only on
   synthetic degree-matched functions.
4. Convergence: Taylor-form overestimation O(r²) in box radius; window-membership hull O(panel + box width) on the two
   edge panels only; panel-mass product loses z–n(x,z) correlation, O(panel width).

## 7. Validation (§7, repair r1)

**FSM exact truth** (`d309_supnorm_fsm.py` → `validation/D309_SUPNORM_FSM.json`): 48 generic + 12 adversarial
source-cases.
* Identities: Leibniz path (`TCFixture.phi_leibniz`) and polynomial path (`phi_poly`) agree exactly for φ^(j)(e0),
  j = 0..5, 60/60.
* Ladder `TRUE ≤ S3 ≤ S2 ≤ S1 ≤ S0` and `TRUE ≤ S4` hold 60/60; strict submultiplicativity and strict cross-term
  cancellation 48/48 generic.
* Premise-level truth checks (load-bearing; `premise_truth`): A0, A1, A2 vs exact max_e ‖R_e‖, ‖∂R_e‖, ‖∂²R_e‖ on a
  9-point drift grid (`a_truth`); f_F..f_G vs ‖φ^(j)(e0)‖; Env4 (or f4, Env5) vs a rigorous lower bound of the true
  whole-cell sup; p_j(s) vs exact ‖φ^(2−j)(t)‖ on 33 points. Genuine supplies: **0 violations over 300 supply checks**
  (5 supplies × 60).
* Mutation power (planted-INVALID supplies on SC4_E3; premise check / enclosure check): fG_zero 60/60 / 35/60;
  Env4_zero 60/60 / 0/60; fG_Env4_half_truth 60/60 / 1/60; A0_half 60/60 / 1/60; A0_x0.99 20/60 / 0/60;
  Env4_midpoint_only 60/60 / 0/60; Env4_x0.9 60/60 / 0/60; fG_sigma3_dropped (24 cases) 24/24 / 14/24.
* Pointwise enclosure check is a weak necessary condition (0 violations in 9900 point checks; fixtures loose, worst
  genuine dev/rad 0.538); **not cited as evidence**.
* Comparator control relabelled (tests identity comparator only); r0 NC2 withdrawn (arithmetic).
* Idealization (N4): E3, Env5_comp, f4_comp are sups of `phi_poly`, which contains the **exact** source S(e) —
  exact-source idealizations real SC-4w cannot certify.
* Synthetic ratios (generic; not a forecast): S3/S0 0.063–0.834; S2/S1 0.261–0.883; S1/S0 0.857–0.990; E3/E0
  (idealized) 0.136–0.871; rad(ρ) SC3/TCT_base 0.120–0.856; rad(ρ) SC4_E3/TCT_base (idealized) 0.080–0.799.

**Real CUSUM kernel, non-target drifts {0, 1/4, 1/2, 1, 3}** (`d309_hermite.py` →
`validation/D309_HERMITE_NONTARGET.json`):
* H1: closed form vs independent C11 kernel (`c11_certifier.kernel_apply`): 1200/1200 (i = 0 direct; i = 1, 2, 3 by
  central finite differences with rigorous truncation bounds `h²/6, h²/12, 0.2834 h²` × `(isqrt((i+2)!)+1)` ×
  crude sup |w|); max gap 5.8e-08. Tolerance reaches ≈ 10⁻³ for w_bump (N6); C11 shares memoised Gaussian primitives
  (N7).
* H1b (independent, r1): float Gauss–Legendre quadrature (24 nodes, unit sub-panels, math.exp; `Ki_quad_float`),
  1200/1200, max gap 1.7e-13.
* Structural controls through `Ki_apply(drop_sign / ignore_kinks)`: sign dropped flagged 592/592 (FD) and 592/592
  (quad) where applicable; kinks ignored flagged 936/960 (FD) and 955/960 (quad) for non-constant w.
* H2 (DIAGNOSTIC, grid, not certified): composite is 0.124–0.314 of the ideal surrogate (true operator norm via
  `op_norm_true`, grid-lower ‖w‖).
* H3 naive certificate (`box_upper_composite`): soundness = per-box containment (N5); planted defects inside:
  e = 1/4 low-degree triple: 749 points, 0 genuine, drop_sign 38, collapse 513, shrink_half 0, drop_hull 1, ratio
  1.53; e = 1/4 bump triple: 0 genuine, collapse 749, others 0, ratio 1.178e+04; e = 3 low-degree: 0 genuine,
  drop_sign 45, collapse 265, drop_hull 3, ratio 4.024; e = 3 bump: collapse 749, ratio 3.879e+04. Vacuous for the
  degree-9 triple (defects short of collapse hidden).
* Taylor-form certificate (`box_upper_tf`), `validation/D309_HERMITE_TF_NONTARGET.json`, containment test with
  defects zero_remainder / half_remainder / drop_sign / drop_hull:
  | drift | triple | depth | points | genuine | zero_rem | half_rem | drop_sign | drop_hull | upper/grid-lower | upper/ideal surrogate |
  |---|---|---|---|---|---|---|---|---|---|---|
  | 1/4 | quad+lin+const | 4 | 749 | 0 | 516 | 0 | 95 | 2 | 1.413 | 0.184 |
  | 1/4 | bump×3 | 4 | 749 | 0 | 749 | 219 | 578 | 0 | 1.340 | 0.418 |
  | 1/4 | bump×3 | 5 | 3016 | 0 | 3016 | 69 | 2712 | 0 | 1.217 | 0.380 |
  | 3 | quad+lin+const | 4 | 749 | 0 | 362 | 0 | 379 | 65 | 1.443 | 0.189 |
  | 3 | bump×3 | 4 | 749 | 0 | 699 | 237 | 542 | 0 | 1.314 | 0.238 |
  | 3 | bump×3 | 5 | 3016 | 0 | 3016 | 513 | 2547 | 0 | 1.189 | 0.216 |
  Genuine 0 violations everywhere; zeroed remainders and dropped sign detected every run; halved remainder / dropped
  hull only in some runs (O(panel) decoupling hides small defects). Soundness rests on the §5 reading proof.
* These are declared test functions, not K1 candidates: they show the Stein-type slack exists **for exact sups** and
  the certificate is computable stdlib-only; they do **not** estimate slack or certified gain for any real candidate.

## 8. Data requirement for real use (§8)

* Needs K1 candidate **payloads** `F̂_r, D̂_r, Ĥ_r` (degree-12 exact-dyadic state-only polynomials): "never serialized —
  anywhere, ever": 0 of 326 sealed records (`p5y_k5_tail_c6_evidence_recovery/README.md:41-50`).
* No non-target real cell has them: lower-front `TC_CELL_*.json` carry scalars only (fields `W2, binding, cell, e0,
  identity_gate, k1_record_sha256, left, mode, norms, r/*/{H_at_a, abs_G_at_a, delta_*, eps_src, sup}`); every other
  committed JSON with a `payload`/`coeffs` key under `level4/` is an operator taboo/ARL supersolution candidate
  (`registry_c1/`, `registry_c2/`, `registry_r1/`), Perron-deflated `PROBE.json` supersolutions, synthetic order-3
  qualification parts, or unrelated p8r/p9r results. So **no real-cell SC validation**; only the kernel machinery.
* Regeneration: faithful replay of the frozen 13-module K1 chain (C6 README:41-50) needs numpy and python-flint —
  absent locally (`find_spec` False for numpy, scipy, flint, mpmath, sympy, gmpy2) and on the permitted worker (C6-N1);
  host provisioning is a user decision (**U1**).
* Admissibility: SC is a **new** scientific quantity derived from P3 records → C6 Condition 10 (**U2**).
* Replay trust surface: payload bytes not directly gated; tied to the record only through 262 scalar fields
  (MEASUREMENT_NOTE.md:33-37 via ROUTE_AUDIT_R1.md:47) — disclosed residual risk.

## 9. Governance and kill gates (§9–§10)
* Floor r2: SC changes a non-constant consumer input (TC-T premise supply) → **CLOSURE-ONLY**; adoption needs a
  user-decided floor extension frozen before any evaluation (**U3**; ROUTE_AUDIT_R1.md:477-487).
* Order-3 producer untouched: no real Ĝ is ever formed.
* Gates: G1 PASS (structural Leibniz/submultiplicativity slack); G2 PASS; G3 PASS; G4 PASS (stdlib); G5 PASS on
  premise-level truth checks and H1/H1b (enclosure check not cited); G6 PASS for mathematics and order-3 certificate
  (review R1, H1b, dual paths); G7 PASS (0 target evaluations); G8 PASS; G9 PASS for theorem and certificate code
  (configuration freezable by declared rule); G10 PASS for **exact** sups, certified gain not guaranteed.
* **Verdict: NOT killed. VALIDATED_NON_TARGET. Real use BLOCKED on payloads, U1, U2, U3. FREEZE_READY: no.**

---

## 10. Code: functions, formulas, data needed

### `d309_core.py` (shared; target-free; `guard_drift` on every drift interval)
* Polynomials: `p_eval, p_deriv, p_add, p_scale, p_mul, p_taylor` (coefficients of c(x0 + t)); `_piece_bounds` and
  `sup_abs_on(c, lo, hi)` = RIGOROUS (upper, lower) of max|c| by recursive bisection with the exact Taylor remainder
  form |c(m)| + Σ_k |c^(k)(m)/k!| h^k; `min_on` rigorous lower bound of min c.
* Families: `make_family(n, seed, e_hi, deg=4, kill=1/5)` (ov_fixtures random sub-Markov family, kernel degree deg in
  e); `make_sources`; `k_cell(fam, i, lo, hi)` = k_i ≥ sup ‖K_i(e)‖ (max row sum of rigorous entry sups);
  `C_cell(fam, e0, ρ)` = Neumann ‖R_e‖ ≤ ‖R0‖/(1 − ‖R0‖d); `sigma_cell(sp, n, lo, hi)`.
* `TCFixture(fam, sp, e0, ρ, cand)` with candidates F, D, H (G default 0): `phi_leibniz(j)` =
  S^(j) − (I − K)F̃^(j) + Σ_{i≥1} C(j,i) K_i F̃^(j−i), j = 0..5; `phi_poly()` = independent exact polynomial in
  t = e − e0 of φ(e) = S(e) − (I − K_e)F̃(e); `phi_poly_deriv_at0(j)`; `phi_poly_deriv_sup(j)` rigorous whole-cell sup;
  `Fpp_at_atom(t)` exact F''(t)(a).
* `tc_profile_polys(f, variant)`: "TC": p2 = [H, G, Env4/2], p1 = [D, H, G/2, Env4/6], p0 = [F, D, H/2, G/6, Env4/24];
  "TCp" (TC⁺): p2 = [H, G, f4/2, Env5/6], p1 = [D, H, G/2, f4/6, Env5/24], p0 = [F, D, H/2, G/6, f4/24, Env5/120].
  `tc_rad_poly(A, f, variant)` = A0 p2 + 2A1 p1 + A2 p0.
* `lemma_g(k, C)` = (C, k1 C², k2 C² + 2 k1² C³). `perturbed(v, pert, rng)`.

### `d309_supnorm_fsm.py` (writes `validation/D309_SUPNORM_FSM.json`)
DECLARED_RULE (fixed before the first run): generic seeds 1..24, n = 4 + seed%4, kernel degree 4, kill 1/5,
e0 = 1/8, ρ = (1/64, 1/32, 1/16)[seed%3], pert = (1e-6, 1e-4, 1e-2)[(seed//3)%3], source degree (2, 5)[seed%2]
(degree 2 ⇒ σ3 = σ4 = 0), two sources per fixture, Ĝ := 0; adversarial seeds 101..106, n = 5, source degree 2,
candidates = sign patterns of maximising rows of K1(e0) (Ĥ), K2(e0) (D̂), K3(e0) (F̂); grid 33 points.
* `ladder`: S0 = 3k1 sH + 3k2 sD + k3 sF + σ3; S1 with exact midpoint op-norms ‖K_i(e0)‖; S2 = 3‖K1Ĥ‖ + 3‖K2D̂‖ +
  ‖K3F̂‖ + σ3; S3 = ‖3K1Ĥ + 3K2D̂ + K3F̂‖ + σ3; S4 = ‖Ŝ3 + comp‖ + ε3 (Ŝ3 = S''' + noise, ε3 = ‖noise‖); TRUE =
  ‖φ'''(e0)‖; comparator control (coefficient 2 on K2D̂).
* `env_levels`: E0 = σ4 + 6k2 sH + 4k3(sD + ρsH) + k4(sF + ρsD + ρ²sH/2); E3 = rigorous whole-cell sup of φ⁗ (composite,
  exact-source idealization); f4_sur = σ4(e0) + 6k2 sH + 4k3 sD + k4 sF; f4_comp = ‖φ⁗(e0)‖; Env5_norm = σ5 + 10k3 sH +
  5k4(sD + ρsH) + k5(sF + ρsD + ρ²sH/2); Env5_comp = whole-cell sup of φ⁽⁵⁾.
* `a_truth`: exact max over 9 drifts of ‖R‖, ‖RK1R‖, ‖2RK1RK1R + RK2R‖.
* `premise_truth`: returns violated premises (A's, f_*, Env4 or f4/Env5, profiles p_j(|t|) vs exact ‖φ^(2−j)(t)‖).
* `enclosure_check`: |F''(t)(a) − Ĥ(a)| ≤ rad(|t − e0|) on 33 points (weak).
* Supplies: TCT_base (G = S0, Env4 = E0), SC3 (G = min(S0, S3)), SC3_E3 (+ Env4 = min(E0, E3)), SC4_E3 (G = min(S0,
  S3, S4)), SC4_TCplus (TCp with f4 = min(f4_sur, f4_comp), Env5 = min(Env5_norm, Env5_comp)).
* Mutants on SC4_E3: fG_zero, Env4_zero, fG_Env4_half_truth, A0_half, A0_x0.99, Env4_midpoint_only, Env4_x0.9,
  fG_sigma3_dropped.
* Data needed: synthetic only (ov_fixtures).

### `d309_sct.py` (writes `validation/D309_SCT_FSM.json`)
Same generic seeds 1..24; for each source: E_F, E_D, E_H from exact F_derivs; IKF3 = (I − K)F'''; checks
φ'''(e0) == IKF3 + 3K1E_H + 3K2E_D + K3E_F exactly; bound ‖φ'''‖ ≤ ‖IKF3‖ + 3k1‖E_H‖ + 3k2‖E_D‖ + k3‖E_F‖;
comparator control (2 in place of 3 on the K2 term); ratios ‖φ'''‖/‖IKF3‖ and S0/‖IKF3‖ by pert. Synthetic only.

### `d309_hermite.py` (writes `validation/D309_HERMITE_NONTARGET.json`; drifts {0, 1/4, 1/2, 1, 3} only)
Frozen model re-derived: state (p, m), K = 1/2, C = H + K = 11/2, increment z with z + e ~ N(0,1), next state
(max(0, p + z − K), max(0, m − z − K)), alarm-free window z ∈ [m − C, C − p]; `(K_i w)(p, m) = ∫_{m−C}^{C−p}
w(n(x,z)) (−1)^i He_i(z+e) φ(z+e) dz`. HE = He_0..He_5.
* Imports allowed pure libraries `c7_gaussian` (rigorous φ, Φ, Iv) and `c11_certifier` (independent K_e, cover,
  poly_eval_iv); memoises φ/Φ/sqrt_two_pi in-process (value-identical, `_memo_selftest`).
* `moments(A, B, jmax)` (recursion above); `lin_pow`; `compose_piece` (w(p', m') as polynomial in z per piece);
  `Ki_apply(w, p, m, e, i, drop_sign, ignore_kinks)` (piecewise between window ends and kinks K − p, m − K; multiply by
  He_i(z+e) Taylor-shifted; re-express in u = z + e; sum coefficient × moment).
* `fd_check`: vs C11 finite differences (see H1). `op_norm_true(e, i)`: k_i(e) = ∫_{e−C}^{e+C} |He_i(u)| φ(u) du
  rigorously (split at roots; antiderivative of He_i φ is −He_{i−1} φ; ±√3 handled for i = 3).
* `box_upper_composite(triple, box, e, panel, defect)`: naive interval enclosure; defects drop_sign, collapse,
  shrink_half, drop_hull; `Q.guard_drift(e)` added (N8). `box_points`, `containment` (per-box point containment on
  `C11.cover(depth)`), `Ki_quad_float` (independent quadrature), `certified_sup`.
* DECLARED_RULE: 12 states, test polynomials w_const = 1, w_lin = p − 2m + 1, w_quad = p² + pm − m²/2 + 3, w_cub
  (seed 11), w_bump = y(1 − (y/(5/2))²)^4 with y = m − 5/2; H3 on triples 1 and 3 at e ∈ {1/4, 3}, depth 4, panels 1/16.
* Data needed: none from K1/cells; only the kernel model and the allowed pure libraries.

### `d309_hermite_tf.py` (writes `validation/D309_HERMITE_TF_NONTARGET.json`; drifts {1/4, 3})
`shift2` (exact bivariate shift to box centre), `tf_range2` (c0 ± rscale·Σ|a_ab| rp^a rm^b), `tf_range1` (1-D centred
Taylor form), `box_upper_tf(triple, box, e, panel, defect)` (defects zero_remainder, half_remainder, drop_sign,
drop_hull; `Q.guard_drift(e)` added per N8; combined Hermite weight when one function serves all orders). Triples
(w_quad, w_lin, w_const) depth 4 and (w_bump ×3) depths 4, 5; panel 1/16; containment test as in `d309_hermite`.

---

## 11. REVIEW_STREAM_D_R1 — ROUTE_REVIEW: ACCEPTED_WITH_CONDITIONS

Reviewer independent, fresh context, 2026-09-28. Scope: all D_309 documents, code, `validation/D309_*.json`. Quarantine:
only Stream-D functions and own stdlib scripts at declared drifts {0, 1/4, 1/2, 1, 3} and FSM fixtures; ledger
redirected; no Stream-D main() run; no 305–309 quantity; no band drift; no git write.

### §0 Verdict (near-verbatim)
* **Mathematics sound.** SC-3, SC-4w, TC⁺, SC-T, SC-S1, CR-1, leading-order `1 − 1/N^j`, RSO-0, RSO-PM, RSO-LR (order
  1), RSO-P re-derived; no validity-breaking error.
* **SC genuinely stronger than the surrogate, not a relabelling.** Needs candidate functions, not scalars; C5 route A3
  made precise, same DATA blocker.
* **Certificates sound** (naive and centred Taylor form) by reading; reviewer per-box attack 1280 exact point values,
  0 violations; Hermite closed form agrees with reviewer's own quadrature 2400/2400 (i = 0..5).
* **Evidence defects (B1–B3):** several "negative controls" arithmetic tautologies; B2 − TPT = 0 holds by construction;
  route B2's REFUTED label broader than CR-2 proves.
* Repairs are local (labels, controls, guards). Quarantine clean; governance labels correct; **no route is or could
  honestly be FREEZE_READY.**

### §1 Route SC findings
* SC-T identity, SC-3 (a)/(b), SC-4w: correct. TC⁺ remainder integrals recomputed: ∫_0^s (s−v)(f4+vE5)dv = f4 s²/2 +
  E5 s³/6; ∫(s−v)²/2(·) = f4 s³/6 + E5 s⁴/24; ∫(s−v)³/6(·) = f4 s⁴/24 + E5 s⁵/120; Env5 correct.
  **N1**: `s = |t − e0|` although t = e − e0 (should be |e − e0| or |t|).
* Not a relabelling: S3 needs candidate *functions*; C5 route A3 made precise (disclosed); novelty = rigour +
  certificate; DATA blocker unchanged.
* SC-S1 proof correct for continuous nonzero candidates. **N2**: root condition stated for i ≤ 3, but TC⁺/SC-4w use
  i = 4, 5 (every He_i, i ≥ 1, has a root in [−1, 1], so |e| < C − 1 suffices). **N3**: "strict" is for the exact sup;
  certified overhead (TF 1.19–1.44×) means no guaranteed certified gain; summary and commit 6d0f0615 wording must say so.
* **N4**: FSM SC-4w/TC⁺ ratios idealized (phi_poly contains exact S(e)); label them.
* §1.2 certificate soundness by reading: moment recursion correct; φ^(i) = (−1)^i He_i φ correct; image boxes correct;
  weight × image-range × panel mass valid (φ ≥ 0); partial-window hull valid; cover keeps a superset of the reachable
  set. No unsoundness found.
* §1.3 reviewer runs: `rev_quad.py` 2400/2400 agree, max abs diff 9.1·10⁻¹³; sign dropped detected 1185/1185; kinks
  removed 783/783. `rev_tf_attack.py` (cover(2)) TF 0/480, naive 0/480. `rev_tf_attack2.py` (depth 5, 800 points) TF
  0, naive 0; remainder zeroed 632/800; Hermite sign dropped 716/800; remainder halved 0/800; hull dropped 0/800.
  Point containment detects only gross defects; soundness rests on the reading proof.
* §1.4 test adequacy:
  * **B1 (tautological negative controls claimed as evidence).** `d309_hermite.py:350,357` (`planted = glo*99/100` …
    `not (planted >= glo)`), `d309_hermite_tf.py:130` — True for every glo > 0; SUPNORM ("planted-too-small detected
    6/6") and PROGRESS presented them as detections. Same pattern: SC-FSM NC2 (`rads = [max(devs)/2]`) and NC1 (hand-
    written alternative formula; tests the identity comparator only). **Repair:** relabel as harness/arithmetic
    checks; add controls feeding a planted-invalid object through the real path (planted-invalid premise supply
    through `tc_rad_poly` + `enclosure_check`; planted defect in `box_upper_tf` checked by containment).
  * **N5**: TF/H3 "soundness" = certified_upper ≥ 121-point grid max — necessary only; per-box containment is adequate.
  * **N6**: H1 tolerance up to 9.6·10⁻⁴ for w_bump vs values ≤ 0.48; observed gaps (≤ 5.8·10⁻⁸) carry the evidence.
  * **N7**: monkey-patched c7_gaussian shared with C11 in H1; `_memo_selftest` checks two arguments; reviewer quadrature
    closes the gap.
  * **N8**: `box_upper_tf` and `box_upper_composite` take a drift but did not call `Q.guard_drift`; add the guard.

### §2 Route CR and B2 (see also COVER digest)
* CR-1 re-derived: r0 = A0f_H+2A1f_D+A2f_F, r1 = A0f_G+2A1f_H+A2f_D, r2 = A0Env4/2+A1f_G+A2f_H/2, r3 = A1Env4/3+A2f_G/6,
  r4 = A2Env4/24; Γ_F − g_hi = ρ(e0+ρ)(|c_lo| + Σ r_jρ^j). Correct.
* "1 − 1/N^j": order-j slack of a TPT record over half-width h ≈ e_c r_{j−1} h^j / j; with h = ρ/N and e_J = e0 + O(ρ)
  the retained fraction is N^{−j}(1 + O(ρ/e0)); frozen-relative charges 1/N, 1/(2N²), 1/(3N³) follow. Correct as a
  leading-order statement with premises fixed; FSM shows the premise change matters (prediction error up to +37 %);
  the e_J/e0 factor must be shown.
* **N9**: CR-3 bookkeeping inconsistent (S_TPT contained w_g, yet CR-3 added [w_g(e0) − w_g(e_J)] separately).
* **N10**: CR-2 proof said "attained" — TPT-O is a supremum; conclusion survives.
* **B2 (blocker for route-B2 REFUTED label as worded).** "a record-free split can never gain anything" and B2
  **REFUTED** overreach: CR-2 covers only bounds built from the *fixed* triple (g_hi, L, U). A record-free split can
  still change the third input by re-certifying operator constants (k_i, A, Env4 k-terms) on shorter drift segments
  (s-dependent profile pointwise ≤ cell-uniform one; Lemma TC-P needs constants only on [e0, t]). That lever is not
  dominated by fixed-profile TPT and is neither NEW_REAL nor a new record. C5 killed B2 as NEW_REAL, not MATH
  (C5_ROUTE_SEARCH.md:50); upgrading to REFUTED on Stream D's own formalization is the S4 pattern. **Repair:** "B2 is
  REFUTED within the fixed-(g_hi, L, U) family"; record sub-segment constant re-certification as a separate,
  unevaluated lever.
* **B3 (validation by construction).** "B2 − TPT = 0 exactly in 30/30" is not evidence for CR-2: `d309_cover.py`
  implements B2 as the parent record's own TPT integrals over sub-lengths from the same e0, so the max equals parent TPT
  when integrands are nonnegative. Relabel as a transcription-consistency check; CR-2 rests on TPT-O.
* §2.2 policies: DRP-0 result-free provided ρ_k* = s_1/s_2 is computable from certified inputs; **N11**: s_1 includes a
  "centre error" that is not an input → use certified bound (W + r0 half-widths). DRP-1 **result-adaptive** (splits on
  Γ ≥ 0); rigour unaffected (every leaf certified) but under S1 a branch-and-bound toward Γ < 0 on a target cell is
  admissible only as a frozen, budget-capped, pre-authorized stage; **N12**: wording everywhere "DRP-0 result-free;
  DRP-1 outcome-adaptive, frozen-predicate". Cost bound records ≤ 2^{D+1} − 2 correct.
* §2.3 **N13**: `NC_half_transport` arithmetic; `NC_g_hi_planted` a harness check; flat profile the only code-path
  control (3/10). C2 soundness (clause ≥ grid max of exact g) is truth-relative — the real evidence. C5 "ρ halved"
  oracle diagnosis confirmed (`c5_common.py:85-86` scales `m2["rho"]` only).

### §3 Route RSO (see also RSO digest)
* RSO-0, RSO-PM (∂R = RK₁R, ∂²R = 2RK₁RK₁R + RK₂R; implementation uses entrywise cell-sup |K_i|, valid), RSO-LR
  (score identities; V = α + βμ² reduction re-derived; K^S = K₁, K^{S²} = K₂ + K), RSO-P: correct. Collapse statement
  correct. **N14**: "iff ψ non-constant on supp μ" misstated → "iff ψ ≠ ‖ψ‖ μ-a.e.". **N15**: Corollary RSO-G needs
  sup_{e∈C} μ_{a,e}(ψ). Original definition respected (S4).
* RSO tests: truth-relative checks that can fail (N0 ≥ max_e (R_e a)(a); N1/N2 ≥ PM and signed truths on 17-point
  grid; TC assembly vs exact F''(t)(a), worst dev/rad 0.98 for RSO-P-box1); certificates verified twice. **B1
  continued**: NC (a) (halves one entry of ψ, checks psi_bad ≥ a) and NC (c) (`not (lower*9/10 ≥ lower)`) arithmetic;
  NC (b) and NC (d) genuine.

### §4 Cross-cutting
* §4.1 reviewer `rev_fsm_power.py` (planted-invalid supplies through `tc_rad_poly` + `enclosure_check`): f_G := 0
  30/60; Env4 := 0 **0/60**; f_G := TRUE/2 & Env4 := sup/2 **1/60**; A0 halved **0/60**. **N16**: "0 violations in 9900
  point checks" and RSO "2376 checks" are weak evidence (fixtures loose, worst dev/rad ≤ 0.54); load-bearing SC
  evidence is the premise-level ladder / E3 ≥ true sup checks.
* §4.2 quarantine: static scan 0 findings on the 7 D_309 code files (planted control detected); 9 D_309 ledger entries,
  SYNTHETIC_VALIDATION / NONTARGET_DRIFT_VALIDATION, cells_touched = [], no LEAK_FLAG; drifts: FSM e ≤ 3/8 and CUSUM
  kernel at {0, 1/4, 1/2, 1, 3} ± 2·10⁻⁴; only allowed pure libraries imported. Temporal: mtimes precede runs;
  committed in 6d0f0615; `d309_rso.py` run 3× (**N17**: record re-run reasons). **S8**: committed tail numbers appear
  only in history sections (SCOPED §1, COVER §9); the reviewer grepped route sections for the committed values
  [TAIL-NUMBER REDACTED — list of fifteen committed tail values] and found none. **N18** (caution): RSO:25-27 pointed to
  the C5 per-cell A0·f_H share in the same document whose §6 reports RSO-C4 synthetic ratios; a reader can combine the
  two — drop the pointer or move it. Ranking in D_309 summary §3 structural; G1/G8 PASS.
* §4.3 governance: closure-only correct for every row (SC, RSO change TC-T premise supplies / a consumer term; CR changes
  records and geometry; none is a Lemma G / Dv′ r2 supply). Data-blocked correct (payloads 0/326; lower-front TC_CELL
  scalars only; U1 numpy/python-flint host; U2 C6 Condition 10); CR additionally NEW_REAL (guard DENY). FREEZE_READY no
  for every route: no payload, no declared calibration artefact for certificate configuration, SC-4w interval-drift
  enclosure not implemented, RSO-LR single-drift, every route needs U3.

### §5 Per-route gate review
| route | Stream D state | reviewer | gate changes |
|---|---|---|---|
| SC + certificate | VALIDATED_NON_TARGET; real use BLOCKED | agree, with B1/N3/N4/N8/N16 | G2 PASS; G5 PASS on premise-level checks + reviewer quadrature/containment; G6 PASS for math and order-3 certificate; G9 PASS for statements/formats only; G10 PASS for exact sups, certified gain unproven (N3) |
| CR (CR-1, CR-3, DRP-0/1) | VALIDATED_NON_TARGET (algebra); DRP-1 IMPLEMENTED; BLOCKED (NEW_REAL) | agree, with N9/N11/N12 | G2 PASS (leading-order, premises fixed); G7 PASS; "result-free" for DRP-0 only (after N11) |
| B2 | REFUTED (dominated by TPT) | REFUTED only within the fixed-(g_hi, L, U) family (B2); "0 in 30/30" by construction (B3) | G2 PASS for scoped statement via TPT-O |
| RSO-C4 | VALIDATED_NON_TARGET; narrow | agree | — |
| RSO-P / RSO-PM | VALIDATED_NON_TARGET; BLOCKED | agree, with N14/N15 and B1 (NC a) | G10 PASS iff ψ ≠ ‖ψ‖ μ-a.e. |
| RSO-LR order 1 | VALIDATED_NON_TARGET (single drift) | agree | G3: single drift; block-uniform version absent |
| RSO-LR order 2 | THEORY_ONLY | agree (sketch only) | — |
| any route | FREEZE_READY: no | agree | — |

### §6 Conditions for acceptance (verbatim-close; none changes a theorem)
1. **B1** — relabel every arithmetic/harness "negative control" (`d309_hermite.py:350,357`; `d309_hermite_tf.py:130`;
   `d309_supnorm_fsm.py:67-68, 104`; `d309_rso.py:201-204, 428`; `d309_cover.py:238-239`), correct the "detected n/n"
   claims (SUPNORM, RSO, PROGRESS), and add ≥ 1 code-path control per certificate claim (templates: reviewer's
   `rev_tf_attack2.py`, `rev_fsm_power.py`; report power).
2. **B2** — restate route B2 as "REFUTED within the fixed-(g_hi, L, U) family" (COVER, SCOPED, summary) and record
   sub-segment operator-constant re-certification as a separate, unevaluated, record-free lever; "attained" →
   "supremum" (N10).
3. **B3** — relabel "B2 − TPT = 0 exactly, 30/30" as a transcription-consistency check; CR-2's support is TPT-O.
4. Wording: SC gain "strict" only for exact sups (N3); DRP-1 outcome-adaptive, DRP-0 result-free only with certified
   s_1 (N11, N12); RSO "iff" (N14, N15). Commit subject of 6d0f0615 cannot be edited; registry/final report must carry
   corrected wording.
5. Add `Q.guard_drift` inside `box_upper_tf` and `box_upper_composite` (N8).
6. Label FSM SC-4w/TC⁺ ratios as exact-source idealizations (N4); state the enclosure check's measured power (N16).
Notes N1, N2, N5–N7, N9, N13, N17, N18 advisory.

### Disposition of the conditions (from D_309_ROUTE_SUMMARY §7 and PROGRESS repair r1)
* B1: arithmetic controls withdrawn and replaced by code-path controls with measured power (hermite H3: drop_sign 2/4
  runs, collapse 4/4, shrink_half 0/4, drop_hull 2/4, genuine 0/2996; hermite_tf: zero_remainder 6/6, half_remainder
  4/6, drop_sign 6/6, drop_hull 2/6, genuine 0/9028; SC NC1 relabelled comparator control (60/60); SC NC2 replaced by
  planted-invalid supplies (premise check Env4 := 0 60/60, A0 halved 60/60, A0 × 0.99 20/60; enclosure 0/60, 1/60,
  0/60); RSO and cover — see those digests). Documents corrected (SUPNORM §3, §7; RESIDUAL §6; COVER §8; PROGRESS).
* Test power: premise-level and profile-level truth checks added; enclosure/transport checks downgraded to weak
  necessary conditions.
* B2/B3: done (see COVER digest). N8: guards added in `box_upper_composite`, `box_upper_tf`, `abs_sup_matrix`,
  `check_cert_taylor`, `check_cert_grid`, `LRFamily.kernel`, `LRFamily.kernel_deriv`.
* Wording notes N1–N18 dispositioned (table in the summary digest). Commit subject of 6d0f0615 superseded by corrected
  wording. All six D309_*.json regenerated; states unchanged except B2 narrowed, B2c added THEORY_ONLY, G6 PASS for
  mathematics.
