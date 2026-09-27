# Theorem SC — composite-sup premise supply for theorems TC / TC-T

**Status.** Research theorem written for the 2026-09-28 overnight campaign.
* It is general: it covers every cell and every detector, and is not a 309 patch.
* **Never evaluated on CUSUM m = 5 cells 305–309, and on no drift in [1.2, 2.6].**
* Validation is on synthetic finite-state (FSM) families, with exact truth, and on the real CUSUM kernel at the declared
  non-target drifts {0, 1/4, 1/2, 1, 3} only.
* Rule S8: this document contains no committed tail-cell share, factor or margin.

**Route state.**
* The theorem and the certificate are **VALIDATED_NON_TARGET**.
* Real-cell use is **BLOCKED**: candidate payloads were never serialized, and U1/U2/U3 below are open.

## 1. Setting and notation

Setting (theorem TC §1, `level4/closure_proofs/p5y_k5_lower_front_order3/theorem/THEOREM_TC.md:9-14`):
* cell `C = [e0 − ρ, e0 + ρ]`;
* source index r;
* true source `S = S_r(e)`, and `F = F_r = R_e S`;
* fixed candidates `F̂, D̂, Ĥ, Ĝ ∈ B(X)`;
* `t = e − e0`, `F̃ = F̂ + tD̂ + (t²/2)Ĥ + (t³/6)Ĝ`, and `φ(e) = S(e) − (I − K_e)F̃(e)`.

TC-T (`level4/closure_proofs/p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md:44-61`) takes `Ĝ := 0` and supplies the
order-3 midpoint premise by the **surrogate**

    f_G^sur := 3 k1 s_H + 3 k2 s_D + k3 s_F + σ3        (≥ ‖φ'''(e0)‖, TCT :53)

and the whole-cell order-4 premise by the (P3) envelope at `s_G = 0`:

    Env4 := σ4 + 6k2 s_H + 4k3 (s_D + ρ s_H) + k4 (s_F + ρ s_D + ρ² s_H/2)     (TCT :128)

Here `k_i ≥ sup_C ‖K_i(e)‖` and `s_X ≥ ‖X̂‖`. Both are the Leibniz triangle inequality plus submultiplicativity applied to

    φ'''(e0) = S'''(e0) + 3K1 Ĥ + 3K2 D̂ + K3 F̂                                     (Ĝ = 0; TCT :49)
    φ⁗(e)   = S⁗(e) + 6K2(e) Ĥ + 4K3(e)(D̂ + tĤ) + K4(e)(F̂ + tD̂ + t²Ĥ/2)            (Ĝ = 0; TC :43-44)

## 2. Statements

**Theorem SC-3 (composite order-3 premise).** Let `Ψ̂3 := 3K1(e0)Ĥ + 3K2(e0)D̂ + K3(e0)F̂`. Let `Ŝ3` be any fixed function
with `‖S'''(e0) − Ŝ3‖ ≤ ε3`. Two bounds are defined:

    (a)  f_G^SC  := B3 + σ3,    B3 ≥ sup_X |Ψ̂3|                   (candidate composite)
    (b)  f_G^SC' := B3' + ε3,   B3' ≥ sup_X |Ŝ3 + Ψ̂3|             (full composite)

Each is a valid TC (P2) order-3 premise: `‖φ'''(e0)‖ ≤ f_G^SC` and `‖φ'''(e0)‖ ≤ f_G^SC'`. So is
`min(f_G^sur, f_G^SC, f_G^SC')`.

**Theorem SC-4w (whole-cell composite order-4 envelope).** If `E4 ≥ sup_{e ∈ C} sup_X |φ⁗(e)|`, with `φ⁗` the function
displayed in §1, then E4 is a valid (P3) premise. So is `min(Env4, E4)`.

**Theorem SC-4m / TC⁺ (order-raised Taylor cell).** Suppose:
* `f4 ≥ ‖φ⁗(e0)‖` (a midpoint premise, which may be composite);
* `Env5 ≥ sup_C ‖φ⁽⁵⁾‖`.

For `s = |e − e0| = |t| ≤ ρ` define (repair r1, review N1)

    p2(s) = f_H + s f_G + s² f4/2 + s³ Env5/6
    p1(s) = f_D + s f_H + s² f_G/2 + s³ f4/6 + s⁴ Env5/24
    p0(s) = f_F + s f_D + s² f_H/2 + s³ f_G/6 + s⁴ f4/24 + s⁵ Env5/120

Then theorem TC §3 and Lemma TC-P (`streams/E_assembly/THEOREM_TPT.md` §2) hold with these `p_j(s)` in place of TC's.
With `Ĝ = 0`, the norm-only order-5 envelope is

    Env5 = σ5 + 10k3 s_H + 5k4 (s_D + ρ s_H) + k5 (s_F + ρ s_D + ρ² s_H/2)

because `F̃''' = F̃⁗ = F̃⁽⁵⁾ = 0`.

**Proofs.**
* **SC-3.** `φ'''(e0) = (S''' − Ŝ3) + (Ŝ3 + Ψ̂3)`, then the triangle inequality. For (a), use `S''' + Ψ̂3` with
  `‖S'''‖ ≤ σ3`.
* **SC-4w.** Immediate from the definition of (P3).
* **TC⁺.**
  1. Taylor's theorem in `B(X)` gives `‖φ⁗(u)‖ ≤ f4 + |u − e0|·Env5` on C.
  2. Integrate this in the remainders of `φ''`, `φ'` and `φ`, e.g.
     `‖φ''(t)‖ ≤ f_H + s f_G + ∫_0^s (s−v)(f4 + v Env5) dv`. That gives `p2`, `p1` and `p0`.
  3. Steps 2–3 of TC §4 are unchanged.
* The minimum of valid premises is valid. ∎

**Frozen assumptions.**
* (P1) of TC.
* The candidates are fixed before the certificate is computed, and the certificate never sees R.
* Sup norms are taken over the reachable closure X, exactly where TC's norms live.
* No assumption on the sign of any target quantity.

## 3. Relationship to the existing constants and sup norms

**Proposition SC-L (ladder).** For exact certificates (B3 equal to the true sup), write `‖·‖` for the sup over X:

    S0 := f_G^sur ≥ S1 := 3‖K1(e0)‖s_H + 3‖K2(e0)‖s_D + ‖K3(e0)‖s_F + σ3
       ≥ S2 := 3‖K1Ĥ‖ + 3‖K2D̂‖ + ‖K3F̂‖ + σ3
       ≥ S3 := ‖Ψ̂3‖ + σ3 = f_G^SC ≥ ‖φ'''(e0)‖.

The three steps remove, in order:
1. the cell-uniform operator norm, replaced by the midpoint norm;
2. submultiplicativity;
3. the cross-term triangle inequality.

`f_G^SC'` also removes the source/candidate triangle.

**Proposition SC-T (what the composite actually measures).** With `E_F = F̂ − F`, `E_D = D̂ − F'`, `E_H = Ĥ − F''` (all
at e0), differentiating `(I − K_e)F = S` three times gives the exact identity

    φ'''(e0) = (I − K)F'''(e0) + 3K1 E_H + 3K2 E_D + K3 E_F

so

    ‖φ'''(e0)‖ ≤ ‖(I − K)F_r'''(e0)‖ + 3k1‖E_H‖ + 3k2‖E_D‖ + k3‖E_F‖,

with `‖E_X‖` bounded by the frozen K1 rules `eps(F) = C f_F`, etc. (TCT :35-37).

Hence:
* The composite premise is the order-3 residual of the **true** third derivative, `‖(I − K)F'''‖`, up to
  candidate-error terms that vanish as the candidates improve.
* The surrogate S0 is the Leibniz triangle bound `Σ C(3,i) k_i ‖F^(3−i)‖ + σ3` of the same identity.
* The avoidable slack of the surrogate is therefore exactly the Leibniz gap `S0 − ‖(I − K)F'''‖`, minus the candidate
  errors. It is a property of F_r and K, not of any target sign.

**Validation of SC-T** (`code/d309_sct.py:36-49` → `validation/D309_SCT_FSM.json`, 48 source-cases):

| check | result |
|---|---|
| identity, exact | 48/48 |
| bound | 48/48 |
| comparator control (coefficient 3 → 2 on the K2 term; tests the identity comparator only, review B1) | differs 48/48 |
| `‖φ'''‖ / ‖(I−K)F'''‖` at pert 1e-6 | 1 ± 6·10⁻⁷ |
| `‖φ'''‖ / ‖(I−K)F'''‖` at pert 1e-2 | 0.995–1.008 |
| Leibniz gap `S0 / ‖(I−K)F'''‖` (synthetic) | 1.27–15.8 |

**Relation to the atom constants.** SC changes only (P2)/(P3) premises. The TC radius
`rad = A0 p2 + 2A1 p1 + A2 p0` is linear in the premises with nonnegative coefficients. So SC composes with **any**
A-supply (Lemma G, Lemma Dv′, RSO) and cannot be absorbed into one (`SCOPED_NEGATIVE_FAMILIES_309.md` §2).

**Relation to the sup norms `s_X`.**
* Under SC-3 the `s_X` leave `f_G` entirely.
* Under SC-4w they leave Env4 as well.
* Under TC⁺ they remain only in the order-5 envelope, which carries an extra factor of `s`.
* The **inputs** `s_X` are not changed, so every identity-gated K1 field is untouched. C6's "zero gain by construction"
  argument, which concerns tightening `s_X` (route A1), does not apply.
* Tightening `s_X` itself remains a separate lever. Its slack against a Bernstein certifier is unknown, and it is gated,
  per C6.

## 4. When SC is strictly stronger

**Proposition SC-S1 (the Gaussian-location kernel always leaves submultiplicativity slack).** Take the CUSUM kernel
`(K_i g)(x) = ∫_{m−C}^{C−p} g(n(x,z)) (−1)^i He_i(z+e) φ(z+e) dz`. Let `X̂` be continuous and nonzero on the compact
reachable set, and `i ≥ 1`. Then

    ‖K_i X̂‖ < k_i^true ‖X̂‖,   with   k_i^true = sup_x ∫_{win(x)} |He_i(z+e)| φ(z+e) dz.

The true operator norm is attained at the widest window, the atom, with `k_i^true = ∫_{e−C}^{e+C} |He_i| φ`.

*Proof.*
1. `x ↦ (K_iX̂)(x)` is continuous (the window endpoints and the integrand vary continuously), so its sup over the
   compact X is attained at some `x*`.
2. **If `win(x*)` is strictly inside the atom's window:** `|(K_iX̂)(x*)| ≤ ‖X̂‖ ∫_{win(x*)} |He_i| φ < k_i^true ‖X̂‖`,
   because `|He_i| φ > 0` a.e.
3. **Otherwise `x* = a`** (the only state with the widest window). There equality would need
   `X̂(n(a,z)) = ±‖X̂‖ sign He_i(z+e)` for a.e. z in the window. The window contains a sign change of `He_i`: every
   `He_i`, i ≥ 1, has a simple root in `[−1, 1]`, so a root lies in `(e − C, e + C)` whenever `|e| < C − 1`. This covers
   every order used here, i = 1..5 (repair r1, review N2). The left side is continuous in z, so equality is
   impossible. ∎

TC-T's `k_i` is a drift-aware upper bound, at least `k_i^true`. So on the Gaussian kernel with continuous candidates,
`S2 < S1 ≤ S0` always holds qualitatively.

**Scope of "strict" (repair r1, review N3).** SC-S1 is strictness of the **exact** sup. A certified `B3` carries
certificate overhead: the Taylor-form certificate is 1.19–1.44× a grid lower bound on the test functions of §7.
So strictness does **not** imply a certified gain. Whether a certified composite beats the surrogate for a given
candidate is an empirical property of that candidate and certificate configuration.

**Quantitative mechanism.** For i = 1, `∂_e φ(z+e) = ∂_z φ(z+e)`, and integration by parts gives

    (K1 g)(x) = [g(n(x,z)) φ(z+e)]_{m−C}^{C−p} − ∫_{win} ∂_z[g(n(x,z))] φ(z+e) dz,

that is, alarm-boundary density terms plus an average of a directional derivative of g (Stein's identity). The
submultiplicativity slack is therefore governed by the smoothness of the candidate on the unit Gaussian scale. i = 2, 3
work the same way, with one extra point term at each clipping kink.

**Proposition SC-S2 (cross-term cancellation).** `S3 < S2` iff, at every state where `|Ψ̂3|` attains its sup, the three
terms `3K1Ĥ`, `3K2D̂` and `K3F̂` do not all attain their own sups with a common sign.

**Where SC gives nothing: an adversarial FSM case.** On a general finite-state kernel, candidates equal to the sign
patterns of the maximizing rows of `K1`, `K2` and `K3` give `S3 = S1` exactly:
* in `validation/D309_SUPNORM_FSM.json` the adversarial seed 105 reaches `S3/S1 = 1.0`;
* the other adversarial seeds give 0.47–0.95.

Such candidates are discontinuous sign patterns. SC-S1 excludes them for continuous candidates on the Gaussian kernel,
but not on a general FSM kernel. The theorem's strictness is therefore **kernel- and candidate-dependent**, and SC is
stated with `min(·)` so it is never worse.

## 5. Computable certificate

**Lemma HC (Hermite closed form).** Let w be a bivariate polynomial. On each piece of the window
`[m − C, C − p]` between the clipping kinks `z = K − p` and `z = m − K`:
* `n(x, z)` is affine in z;
* so `w(n(x,z))·(−1)^i He_i(z+e)` is a polynomial in `u = z + e`.

Hence `(K_i w)(x)` is an exact finite combination of the Gaussian moments `M_j(A,B) = ∫_A^B u^j φ(u) du`, with

    M_0 = Φ(B) − Φ(A),   M_1 = φ(A) − φ(B),   M_j = (j−1)M_{j−2} + A^{j−1}φ(A) − B^{j−1}φ(B).

Implementation: `code/d309_hermite.py:119-142`, using the allowed pure library `c7_gaussian` for rigorous rational
`φ` and `Φ` (2⁻³²⁰ outward rounding).

**The certificate object** for the order-3 composite of Theorem SC-3 contains:
* the drift `e0`;
* the candidate payload hashes;
* a box cover of the reachable set X (the frozen box rule, as in `c11_certifier.cover`);
* the z-panel width;
* for every box, a rigorous enclosure of `{Σ_i c_i (K_i w_i)(x) : x ∈ box}`.

`B3` is the maximum over boxes of the enclosure magnitude. The per-box enclosure (`code/d309_hermite_tf.py:64-96`)
works panel by panel:
1. On each z-panel P, bound the image box of `n(x, z)` for `x ∈ box, z ∈ P`.
2. Bound each `w_i` on the image box by a **centred Taylor form**: exact bivariate shift to the box centre, then
   `a_00 ± Σ|a_ij| r_p^i r_m^j` (`:32-53`).
3. Bound the Hermite weight on P by a 1-D Taylor form (`:56-61`). When one function serves every order, the weights are
   summed first, so their cancellation is kept.
4. Multiply by the exact panel mass `Φ(z1+e) − Φ(z0+e)`.
5. For panels that lie inside the window for only some states of the box, take the hull with 0 (`:92-94`).

**Verification** is re-evaluation. The certificate is sound because each step is an interval enclosure of an exact
quantity. For the full composite `SC-3(b)`, the source candidate `Ŝ3` (the Aux3 `S:r:3` payload) is added as one more
term, and `ε3` is Aux3's committed midpoint eps.

**Whole-cell order 4 (SC-4w)** needs the same enclosure uniformly for `e ∈ C`. Interval drift enters only through
`φ(z+e)` and `He_i(z+e)`; I1/I2 already certify operator constants this way (`c11r_idrift`, read only). It is not
implemented here, because no non-target validation of interval drift was needed to establish the theorem.

## 6. Numerical stability

1. **Exactness.** Polynomial parts are exact rationals. The only transcendental inputs are `φ` and `Φ` at rational
   points, with proven remainder bounds. C11 erratum E5 (`c11_certifier.py:79-90`) warns that the series degrades for
   `|t| ≳ 20`. For any drift `|e| ≤ 2.6` the arguments satisfy `|u| ≤ e + C ≤ 8.1`, inside the safe range.
2. **Moment recursion.** The recursion multiplies interval widths by at most `max(|A|,|B|)^{j}` per order. For degree-12
   candidates plus i ≤ 4 (so j ≤ 16) and `|u| ≤ 8.1`, the width stays below `8.1^16·2^-320 < 10^-80`. Negligible.
3. **The dependency problem is the real risk, and it was measured.**
   * **Naive** monomial interval evaluation (`d309_hermite.py:245-279`), depth 4, panel 1/16:
     * sound in every case;
     * **vacuous** for the degree-9 test function `w_bump`: certified upper 12458 against a grid lower bound 1.06 at
       e = 1/4, and 22865 against 0.59 at e = 3.
     * The monomial expansion of `y(1 − (y/L)²)^4` about `m = 0` has large cancelling coefficients.
     * Source: `validation/D309_HERMITE_NONTARGET.json` H3.
   * **Centred Taylor forms** (`d309_hermite_tf.py`; `validation/D309_HERMITE_TF_NONTARGET.json`):

     | test function | depth | certified upper / grid lower |
     |---|---|---|
     | `w_bump` | 4 | 1.31–1.34 |
     | `w_bump` | 5 | 1.19–1.22 |
     | low-degree triple | 4 | 1.41–1.44 |

     The ratios converge as the boxes shrink.
   * **Consequence for real use.** Degree-12 dyadic candidates must use centred Taylor forms or Bernstein forms, never
     naive monomial evaluation. The depth and panel width must be fixed by a declared rule **before** any real
     evaluation. No real payload exists to calibrate on (§8), so such a rule could only be calibrated on synthetic
     functions of matching degree.
4. **Convergence order.**
   * Taylor-form overestimation is `O(r²)` in the box radius.
   * The window-membership hull is `O(panel + box width)`, and only on the two edge panels.
   * The panel-mass product loses the `z`–`n(x,z)` correlation, costing `O(panel width)`.

## 7. Validation (target-free; revised in repair r1 after `reviews/REVIEW_STREAM_D_R1.md`)

**FSM, exact truth** (`code/d309_supnorm_fsm.py` → `validation/D309_SUPNORM_FSM.json`).
* **Coverage:** 48 generic plus 12 adversarial source-cases; declared rule at `:42-55`.
* **Identities:** the two independent paths (Leibniz `d309_core.py:244-252`; polynomial `:254-270`) agree exactly for
  `φ^(j)(e0)`, `j = 0..5`, in 60/60 cases.
* **Ladder (truth-relative, can fail):** `TRUE ≤ S3 ≤ S2 ≤ S1 ≤ S0` and `TRUE ≤ S4` hold in 60/60 (`:80`). Strict
  submultiplicativity and strict cross-term cancellation hold in 48/48 generic cases.
* **Premise-level truth checks (load-bearing; `premise_truth`, `:119-153`).** Every premise of theorem TC is compared
  with the exact quantity it bounds:
  * `A0, A1, A2` vs the exact `max_e ‖R_e‖, ‖∂R_e‖, ‖∂²R_e‖` on a 9-point drift grid (`a_truth`, `:104-117`);
  * `f_F, f_D, f_H, f_G` vs `‖φ^(j)(e0)‖`;
  * `Env4` (or `f4`, `Env5`) vs a rigorous lower bound of the true whole-cell sup;
  * the Taylor profiles `p_j(s)` vs the exact `‖φ^(2−j)(t)‖` on 33 points.

  Genuine supplies: **0 violations over 300 supply checks** (5 supplies × 60 cases).
* **Mutation power.** Planted-INVALID supplies, fed through `premise_truth` and through `tc_rad_poly` +
  `enclosure_check` (`:229-252`):

  | mutant (on the SC4_E3 supply) | cases | premise check flags | enclosure check flags |
  |---|---|---|---|
  | `fG_zero` | 60 | 60/60 | 35/60 |
  | `Env4_zero` | 60 | 60/60 | 0/60 |
  | `fG_Env4_half_truth` | 60 | 60/60 | 1/60 |
  | `A0_half` | 60 | 60/60 | 1/60 |
  | `A0_x0.99` | 60 | 20/60 | 0/60 |
  | `Env4_midpoint_only` | 60 | 60/60 | 0/60 |
  | `Env4_x0.9` | 60 | 60/60 | 0/60 |
  | `fG_sigma3_dropped` | 24 | 24/24 | 14/24 |

* **The pointwise enclosure check is a weak necessary condition.** It reports 0 violations in 9900 point checks for the
  five genuine supplies (`:210-219`), but the fixtures are loose (worst genuine deviation/radius 0.538). By the
  mutation table it misses `Env4 := 0` and a halved `A0` almost always. **It is not cited as evidence of premise validity**; the premise-level checks are.
* **Comparator control (relabelled):** a hand-written wrong composite (coefficient 3 → 2 on `K2D̂`) differs from the
  polynomial path in 60/60 (`:74-77`). It tests the identity comparator only.
* **Withdrawn (review B1):** r0's "NC2" (radius := max deviation / 2), which was arithmetic.
* **Idealization (review N4).** `E3`, `Env5_comp` and `f4_comp` are sups of `phi_poly`, which contains the **exact**
  source `S(e)`. Their ratios and the SC3_E3 / SC4_E3 / SC4_TCplus radius ratios include a source cancellation that
  real SC-4w cannot certify, because it sees only σ4 or a source candidate. Validity is unaffected.
* **Synthetic ratios** (generic cases; a property of these fixtures, not a forecast):

  | quantity | range |
  |---|---|
  | `S3/S0` | 0.063–0.834 |
  | `S2/S1` | 0.261–0.883 |
  | `S1/S0` | 0.857–0.990 |
  | `E3/E0` (exact-source idealization) | 0.136–0.871 |
  | `rad(ρ)` SC3 / TCT_base (no source idealization) | 0.120–0.856 |
  | `rad(ρ)` SC4_E3 / TCT_base (idealized) | 0.080–0.799 |

**Real CUSUM kernel, non-target drifts {0, 1/4, 1/2, 1, 3}** (`code/d309_hermite.py` →
`validation/D309_HERMITE_NONTARGET.json`).
* **H1:** the Hermite closed form (`Ki_apply`, `:124-147`) agrees with the independent C11 kernel in
  1200/1200 cases. The comparison is direct for i = 0 and by central finite differences with
  rigorous truncation bounds for i = 1, 2, 3 (`fd_check`, `:189-215`). Maximum gap 5.8e-08.
  * The pass tolerance reaches about 10⁻³ for `w_bump` (review N6). The evidence is the observed gaps, not the pass
    count.
  * C11 shares the in-process memoised Gaussian primitives with the closed form (review N7). H1b closes that gap.
* **H1b (independent, repair r1).** A float Gauss–Legendre quadrature with `math.exp`, sharing no primitive with c7 or
  C11 (`Ki_quad_float`, `:353-380`), agrees in 1200/1200 cases, maximum gap
  1.7e-13.
* **Structural controls through the closed-form code path** (`Ki_apply(drop_sign / ignore_kinks)`):

  | control | comparator | flagged |
  |---|---|---|
  | Hermite sign dropped | FD comparator | 592/592 where applicable |
  | Hermite sign dropped | quadrature comparator | 592/592 |
  | clipping kinks ignored | FD comparator | 936/960 (non-constant w) |
  | clipping kinks ignored | quadrature comparator | 955/960 |

* **H2 (DIAGNOSTIC, grid, not certified):** the composite is 0.124–0.314 of the **ideal** surrogate (true operator norm via `op_norm_true`, `:218-248`; grid-lower `‖w‖`).
* **H3, naive certificate (`box_upper_composite`, `:251-298`).**
  * Soundness is now **per-box containment** (review N5, `containment`, `:307-331`): every exact point value at the
    box corners, edge midpoints and centre in the reachable set must lie in that box's enclosure.
  * Planted defects go **inside** the certificate code path.
  * The r0 "planted-too-small" control, which was arithmetic, is withdrawn.

  | drift | triple | points | genuine violations | drop_sign | collapse | shrink_half | drop_hull | upper/grid-lower |
  |---|---|---|---|---|---|---|---|---|
  | e = 1/4 | w_quad+w_lin+w_const | 749 | 0 | 38 | 513 | 0 | 1 | 1.53 |
  | e = 1/4 | w_bump+w_bump+w_bump | 749 | 0 | 0 | 749 | 0 | 0 | 1.178e+04 |
  | e = 3 | w_quad+w_lin+w_const | 749 | 0 | 45 | 265 | 0 | 3 | 4.024 |
  | e = 3 | w_bump+w_bump+w_bump | 749 | 0 | 0 | 749 | 0 | 0 | 3.879e+04 |

  The naive certificate is sound, but vacuous for the degree-9 triple (§6). There, every defect short of `collapse` stays
  contained in the vacuous enclosure, so those rows carry no detection power.
* **Taylor-form certificate (`box_upper_tf`, `d309_hermite_tf.py:69-107`)**, same containment test and planted defects
  inside `box_upper_tf` (`validation/D309_HERMITE_TF_NONTARGET.json`):

  | drift | triple | depth | points | genuine violations | zero_remainder | half_remainder | drop_sign | drop_hull | upper/grid-lower | upper/ideal surrogate |
  |---|---|---|---|---|---|---|---|---|---|---|
  | e = 1/4 | w_quad+w_lin+w_const | 4 | 749 | 0 | 516 | 0 | 95 | 2 | 1.413 | 0.184 |
  | e = 1/4 | w_bump+w_bump+w_bump | 4 | 749 | 0 | 749 | 219 | 578 | 0 | 1.340 | 0.418 |
  | e = 1/4 | w_bump+w_bump+w_bump | 5 | 3016 | 0 | 3016 | 69 | 2712 | 0 | 1.217 | 0.380 |
  | e = 3 | w_quad+w_lin+w_const | 4 | 749 | 0 | 362 | 0 | 379 | 65 | 1.443 | 0.189 |
  | e = 3 | w_bump+w_bump+w_bump | 4 | 749 | 0 | 699 | 237 | 542 | 0 | 1.314 | 0.238 |
  | e = 3 | w_bump+w_bump+w_bump | 5 | 3016 | 0 | 3016 | 513 | 2547 | 0 | 1.189 | 0.216 |

  Reading:
  * **Genuine certificates:** 0 containment violations everywhere.
  * **Detected defects:** zeroed remainders and a dropped Hermite sign are detected in every run.
  * **Coverage limit:** a halved remainder, or a dropped window hull, is detected only in some runs. The `O(panel)`
    decoupling overestimate hides small defects. This matches the independent review's own attack (§1.3 there).
  * **Consequence:** certificate soundness rests on the reading proof of §5, confirmed independently by the review,
    with these runs as a sanity layer.

These are declared test functions, **not** K1 candidates. They show that:
* the Stein-type slack exists on the real kernel **for exact sups**;
* the certificate is computable, stdlib-only.

They do **not** estimate the slack for any real candidate, nor a certified gain for one (N3).

## 8. Data requirement for real-cell use (checked, not assumed)

**The payloads do not exist anywhere.**
* The certificate needs the K1 candidate **payloads** `F̂_r, D̂_r, Ĥ_r`: degree-12 exact-dyadic, state-only
  polynomials.
* They were "never serialized — anywhere, ever": 0 of 326 sealed records
  (`level4/closure_proofs/p5y_k5_tail_c6_evidence_recovery/README.md:41-50`).

**Checked tonight: no non-target real cell has them either.**
* **Lower-front TC cell records** (`p5y_k5_lower_front_order3/evidence/tc_r1/cells/TC_CELL_11.json`): scalars only.
  The fields are `W2, binding, cell, e0, identity_gate, k1_record_sha256, left, mode, norms, r/*/{H_at_a, abs_G_at_a,
  delta_*, eps_src, sup}`.
* **Every other committed JSON** carrying a `payload`/`coeffs` key under `level4/`, which falls into one of:
  * operator taboo/ARL supersolution candidates (`registry_c1/`, `registry_c2/`, `registry_r1/`);
  * the Perron-deflated `PROBE.json` supersolutions;
  * synthetic order-3 qualification parts;
  * unrelated p8r/p9r results.
* So **there is no real-cell SC validation**; only the kernel-level machinery was validated on the real kernel.

**Regeneration and its obstacles.**
* **Host.** The payloads can be regenerated by a faithful replay of the frozen 13-module K1 chain (C6 README:41-50).
  That needs numpy and python-flint:
  * absent locally (checked: `find_spec` gives False for numpy, scipy, flint, mpmath, sympy, gmpy2);
  * absent on the permitted worker (C6-N1).
  * Host provisioning is a separately governed user decision (**U1**).
* **Admissibility of the new quantity.** The replay reproduces the identity-gated fields; SC changes none of them. SC is
  a **new** scientific quantity derived from P3 records, so C6 Condition 10 applies (**U2**).
* **Replay trust surface.** The payload bytes are not directly gated; they are tied to the record only through 262
  scalar fields (`MEASUREMENT_NOTE.md:33-37`, as quoted in `ROUTE_AUDIT_R1.md:47`). This is a disclosed residual risk.

## 9. Governance

* **Floor r2.** SC changes a non-constant input of the consumer (the TC-T premise supply), so it is **CLOSURE-ONLY**.
  Adoption needs a user-decided floor extension frozen before any evaluation (**U3**; `ROUTE_AUDIT_R1.md:477-487`).
* **Order-3 producer.** SC does not touch the order-3 producer or its guard: no real Ĝ is ever formed.

## 10. Kill gates

| gate | result |
|---|---|
| G1 prospective motivation | PASS. Structural: the Leibniz/submultiplicativity slack (SC-T, SC-S1). Independent of any target sign. |
| G2 validity | PASS. SC-3, SC-4w and TC⁺ are proved (§2); SC-T is an identity; SC-S1 is proved. |
| G3 scope | PASS. Premises and frozen assumptions in §2. The kernel dependence of strictness is stated (§4). |
| G4 reproducible | PASS. Stdlib-only scripts. The JSONs regenerate from `code/`. |
| G5 non-target validation | PASS on the premise-level truth checks (300 genuine supply checks, 0 violations, with mutation power reported) and on the real-kernel closed form (H1/H1b). The FSM enclosure check is a weak necessary condition and is not cited as evidence. |
| G6 independent check | PASS for the mathematics and the order-3 certificate. Evidence: the independent review R1 (re-derivation, its own quadrature, per-box attack), the H1b quadrature and the Leibniz/polynomial dual paths. |
| G7 temporal integrity | PASS. Designed and validated with 0 target evaluations. |
| G8 no leakage | PASS. The ledger holds only SYNTHETIC / NONTARGET_DRIFT entries; the scan finds 0 findings in D_309 files. |
| G9 prospective freeze | PASS for the theorem and certificate code. The certificate configuration (depth, panel, Taylor form) can be frozen by a declared rule. |
| G10 not cosmetic | PASS for **exact** sups: strict for continuous candidates on the Gaussian kernel (SC-S1); equality case exhibited on FSM. A **certified** gain is not guaranteed (certificate overhead; review N3). |

**Verdict: route NOT killed.** State **VALIDATED_NON_TARGET**. Real use is **BLOCKED** on payloads, U1, U2 and U3.
FREEZE_READY: **no**, because no real payload exists to evaluate a frozen stage on.
