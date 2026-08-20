import RebaseguardLean.SmallMoment
import RebaseguardLean.Domination

/-!
# Gate 4.5-C3: the ReBaseGuard differentiation identity, at the actual detector

This is the final assembly.  Gate 3 (`IntegralBridge.lean`) proved the
differentiation-under-the-integral identity for *abstract* `Zτ, Tτ, τ` under a
domination hypothesis; Gate 4 (`Domination.lean`) discharged that hypothesis
from moment data; Gates 4.5-A/B/C1/C2 built the *actual* two-sided CUSUM alarm
time, the actual stopped quantities, and the stopped-walk exponential moment.

What remained were exactly two gaps, closed here:

* **C3-A** — an exponential moment for the real-valued alarm time `τR`.
  Route: the frozen pathwise bridge `τ ≤ N + 1` (`ae_cusumTau_le_forcingNat_succ`)
  plus the frozen forcing-time moment `integrable_exp_forcingNat`.  No optional
  stopping, no new tail theory.

* **C3-B** — `L²` control of the stopped score `Zτ`.
  Route: the *same* Cauchy–Schwarz slice decomposition as C2.3, applied to
  `exp (a |Zτ|)`.  On `{τ = m+1}` the stopped score is `X m`, whose one-step
  exponential moment is a constant (it does **not** grow with `m`), so the only
  scalar condition is `d < 1` — strictly weaker than C2.3's `c * d < 1`.
  `L²` then follows from the elementary pointwise bound `x² ≤ (4/a²) e^{a|x|}`.

  The stopped score is **not** assumed to be `N(0,1)`, and `τ` is never assumed
  independent of anything.  The `{τ = m+1}` indicator is handled by
  Cauchy–Schwarz exactly as in C2.3.

The scalar bookkeeping that feeds Gate 4 is in `rebaseguard_gate4_rates`: the
rates `p` (walk) and `q` (alarm time) produced by C2.4 and C3-A are *fixed and
possibly tiny*, so the Gate 4 parameters `δ, c, a, b` are shrunk to fit them,
not the other way round.
-/

noncomputable section

open MeasureTheory ProbabilityTheory Filter
open scoped ENNReal

namespace RebaseguardLean

variable {Ω : Type*} [mΩ : MeasurableSpace Ω]

/-! ## C3-A — the exponential moment of the alarm time `τR` -/

omit mΩ in
/-- `τR` is a cast natural number, hence nonnegative everywhere (including on the
null set `{τ = ⊤}`, where its value is the unspecified `untopA` fallback). -/
lemma cusumTauReal_nonneg (k h : ℝ) (X : ℕ → Ω → ℝ) (ω : Ω) :
    0 ≤ cusumTauReal k h X ω :=
  Nat.cast_nonneg _

omit mΩ in
/-- A finite upper bound on the alarm time transfers to `τR`.  The hypothesis
forces `τ ω ≠ ⊤`, so no meaning is attached to the `untopA` fallback. -/
lemma cusumTauReal_le_of_le {k h : ℝ} {X : ℕ → Ω → ℝ} {ω : Ω} {m : ℕ}
    (hle : cusumTau k h X ω ≤ (m : WithTop ℕ)) :
    cusumTauReal k h X ω ≤ (m : ℝ) := by
  have hne : cusumTau k h X ω ≠ ⊤ := by
    intro htop
    rw [htop] at hle
    exact absurd hle (by simp)
  obtain ⟨n, hn⟩ := WithTop.ne_top_iff_exists.mp hne
  rw [cusumTauReal_of_eq_coe k h X hn.symm]
  have hnm : n ≤ m := by
    rw [← hn] at hle
    simpa using hle
  exact_mod_cast hnm

/-- **Gate 4.5-C3-A.**  The alarm time has a finite exponential moment at every
rate `b ≥ 0` compatible with the geometric forcing tail (`exp b * r < 1`).

Everything is inherited: `τ ≤ N + 1` from Gate 4.5-B's pathwise bridge, the
moment of `N` from `integrable_exp_forcingNat`, and the comparison from Gate 4D's
`integrable_exp_abs_of_le`. -/
theorem integrable_exp_abs_cusumTauReal {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {r b : ℝ} (hr : 0 ≤ r) (hb : 0 ≤ b)
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ ENNReal.ofReal r)
    (hr1 : ENNReal.ofReal r < 1) (hbr : Real.exp b * r < 1) :
    Integrable (fun ω => Real.exp (b * |cusumTauReal k h X ω|)) μ := by
  have h0 : Integrable (fun ω => Real.exp (b * (forcingNat (h + k) X ω : ℝ))) μ :=
    integrable_exp_forcingNat X hX hindep hr hq hbr
  have hN : Integrable
      (fun ω => Real.exp (b * ((forcingNat (h + k) X ω + 1 : ℕ) : ℝ))) μ := by
    refine (h0.const_mul (Real.exp b)).congr ?_
    filter_upwards with ω
    push_cast
    rw [← Real.exp_add]
    congr 1
    ring
  refine integrable_exp_abs_of_le (aestronglyMeasurable_cusumTauReal k h X hX) hb
    (Filter.Eventually.of_forall (cusumTauReal_nonneg k h X)) ?_ hN
  filter_upwards [ae_cusumTau_le_forcingNat_succ k h X hindep hq hr1] with ω hω
  exact cusumTauReal_le_of_le hω

/-! ## Scalar helpers -/

/-- If `r < 1` then `exp b * r < 1` for some strictly positive `b`.  For `r > 0`
the explicit witness is `b = -(log r)/2`. -/
lemma exists_pos_exp_mul_lt_one {r : ℝ} (hr0 : 0 ≤ r) (hr1 : r < 1) :
    ∃ b : ℝ, 0 < b ∧ Real.exp b * r < 1 := by
  rcases hr0.lt_or_eq with hrpos | hrzero
  · refine ⟨-(Real.log r) / 2, ?_, ?_⟩
    · have hlog : Real.log r < 0 := Real.log_neg hrpos hr1
      linarith
    · have hlog : Real.log r < 0 := Real.log_neg hrpos hr1
      have hlt : Real.exp (-(Real.log r) / 2) < Real.exp (-(Real.log r)) :=
        Real.exp_lt_exp.mpr (by linarith)
      have hinv : Real.exp (-(Real.log r)) = r⁻¹ := by
        rw [Real.exp_neg, Real.exp_log hrpos]
      calc Real.exp (-(Real.log r) / 2) * r
          < Real.exp (-(Real.log r)) * r := by
            exact mul_lt_mul_of_pos_right hlt hrpos
        _ = 1 := by rw [hinv]; exact inv_mul_cancel₀ hrpos.ne'
  · exact ⟨1, one_pos, by rw [← hrzero]; simp⟩

/-- Any `q < 1` in `ℝ≥0∞` has a "square root majorant" `d < 1` with
`q ≤ d²`.  This is the scalar shape consumed by the C2.3-style slice bounds. -/
lemma exists_sq_majorant_lt_one {q : ℝ≥0∞} (hq1 : q < 1) :
    ∃ d : ℝ≥0∞, d < 1 ∧ d ^ (2 : ℕ) < 1 ∧ q ≤ d ^ (2 : ℕ) := by
  have hqtop : q ≠ ⊤ := hq1.ne_top
  set qr : ℝ := q.toReal with hqrdef
  have hqr0 : 0 ≤ qr := ENNReal.toReal_nonneg
  have hqr1 : qr < 1 := by
    have hlt := (ENNReal.toReal_lt_toReal hqtop ENNReal.one_ne_top).mpr hq1
    simpa using hlt
  set dr : ℝ := (1 + qr) / 2 with hdrdef
  have hdr0 : 0 < dr := by rw [hdrdef]; linarith
  have hdr1 : dr < 1 := by rw [hdrdef]; linarith
  refine ⟨ENNReal.ofReal dr, ENNReal.ofReal_lt_one.mpr hdr1, ?_, ?_⟩
  · rw [← ENNReal.ofReal_pow hdr0.le, ENNReal.ofReal_lt_one]
    nlinarith
  · rw [← ENNReal.ofReal_toReal hqtop, ← ENNReal.ofReal_pow hdr0.le]
    refine ENNReal.ofReal_le_ofReal ?_
    rw [hdrdef]
    nlinarith

/-- Elementary: `x² ≤ (4/a²) · exp (a |x|)` for `a > 0`.  Proof: with
`y = a|x| ≥ 0`, `exp (y/2) ≥ y/2 + 1 ≥ y/2 ≥ 0`, so `exp y = exp (y/2)² ≥ y²/4`. -/
lemma sq_le_const_mul_exp_abs {a : ℝ} (ha : 0 < a) (x : ℝ) :
    x ^ 2 ≤ 4 / a ^ 2 * Real.exp (a * |x|) := by
  set y : ℝ := a * |x| with hy
  have hy0 : 0 ≤ y := mul_nonneg ha.le (abs_nonneg x)
  have h1 : y / 2 ≤ Real.exp (y / 2) := by
    have := Real.add_one_le_exp (y / 2)
    linarith
  have h2 : (y / 2) ^ 2 ≤ (Real.exp (y / 2)) ^ 2 := by
    have hnn : (0 : ℝ) ≤ y / 2 := by linarith
    nlinarith [Real.exp_pos (y / 2)]
  have h3 : (Real.exp (y / 2)) ^ 2 = Real.exp y := by
    rw [sq, ← Real.exp_add]
    congr 1
    ring
  rw [h3] at h2
  have h4 : y ^ 2 ≤ 4 * Real.exp y := by nlinarith
  have hyx : y ^ 2 = a ^ 2 * x ^ 2 := by rw [hy, mul_pow, sq_abs]
  rw [div_mul_eq_mul_div, le_div_iff₀ (by positivity : (0:ℝ) < a ^ 2)]
  nlinarith

/-! ## C3-B — the stopped score is in `L²`

### The slice bound

The structure is identical to C2.3's `lintegral_slice_expAbs_walkAt_le`, but the
one-step moment does **not** get raised to the power `m`: on `{τ = m+1}` the
stopped score is the single increment `X m`.  Hence the geometric majorant is
`∑ₘ A · d^(m-1)`, which converges as soon as `d < 1`. -/

lemma lintegral_slice_expAbs_scoreAt_le {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {a : ℝ} {A d : ℝ≥0∞}
    (hM : ∀ j, ∫⁻ ω, expAbsScore (2 * a) X j ω ∂μ ≤ A ^ (2 : ℕ))
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ d ^ (2 : ℕ))
    (m : ℕ) :
    ∫⁻ ω in {ω | cusumTau k h X ω = (m : WithTop ℕ)},
        ENNReal.ofReal (Real.exp (a * |scoreAt X (cusumTau k h X) ω|)) ∂μ
      ≤ A * d ^ (m - 1) := by
  have hs : MeasurableSet {ω | cusumTau k h X ω = (m : WithTop ℕ)} :=
    measurableSet_cusumTau_eq k h X hX m
  match m with
  | 0 =>
      -- the alarm time is always `≥ 1`, so this slice is empty
      have hempty : {ω : Ω | cusumTau k h X ω = ((0 : ℕ) : WithTop ℕ)} = ∅ := by
        ext ω
        simp only [Set.mem_setOf_eq, Set.mem_empty_iff_false, iff_false]
        intro hc
        have h1 := one_le_cusumTau k h X ω
        rw [hc] at h1
        simp at h1
      rw [hempty, Measure.restrict_empty, lintegral_zero_measure]
      simp
  | n + 1 =>
      -- on the slice the stopped score is the single increment `X n`
      have hcongr : ∫⁻ ω in {ω | cusumTau k h X ω = ((n + 1 : ℕ) : WithTop ℕ)},
            ENNReal.ofReal (Real.exp (a * |scoreAt X (cusumTau k h X) ω|)) ∂μ
          = ∫⁻ ω in {ω | cusumTau k h X ω = ((n + 1 : ℕ) : WithTop ℕ)},
            ENNReal.ofReal (Real.exp (a * |X n ω|)) ∂μ := by
        refine lintegral_congr_ae ((ae_restrict_iff' hs).mpr
          (Filter.Eventually.of_forall ?_))
        intro ω hω
        show ENNReal.ofReal (Real.exp (a * |scoreAt X (cusumTau k h X) ω|))
            = ENNReal.ofReal (Real.exp (a * |X n ω|))
        rw [scoreAt_of_eq_coe X (by exact hω)]
      rw [hcongr]
      refine setLIntegral_le_of_sq_le hs ?_ ?_ ?_
      · exact ((ENNReal.measurable_ofReal.comp (Real.measurable_exp.comp
          ((hX n).abs.const_mul a)))).aemeasurable
      · calc ∫⁻ ω, (ENNReal.ofReal (Real.exp (a * |X n ω|))) ^ (2 : ℕ) ∂μ
            = ∫⁻ ω, expAbsScore (2 * a) X n ω ∂μ := by
              refine lintegral_congr fun ω => ?_
              rw [sq_ofReal_exp]
              unfold expAbsScore
              congr 2
              ring
          _ ≤ A ^ (2 : ℕ) := hM n
      · have hpow : (d ^ (2 : ℕ)) ^ (n + 1 - 1) = (d ^ (n + 1 - 1)) ^ (2 : ℕ) := by
          rw [← pow_mul, ← pow_mul, Nat.mul_comm]
        calc μ {ω | cusumTau k h X ω = ((n + 1 : ℕ) : WithTop ℕ)}
            ≤ (d ^ (2 : ℕ)) ^ (n + 1 - 1) :=
              measure_cusumTau_eq_le_pow k h X hindep hq (n + 1)
          _ = (d ^ (n + 1 - 1)) ^ (2 : ℕ) := hpow

/-- **Gate 4.5-C3-B (ℝ≥0∞ form).**  Finiteness of the stopped-score exponential
moment.  The only scalar condition is `d < 1`. -/
theorem lintegral_expAbs_scoreAt_ne_top {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {a : ℝ} {A d : ℝ≥0∞} (hA : A ≠ ⊤)
    (hM : ∀ j, ∫⁻ ω, expAbsScore (2 * a) X j ω ∂μ ≤ A ^ (2 : ℕ))
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ d ^ (2 : ℕ))
    (hd1 : d ^ (2 : ℕ) < 1) (hd : d < 1) :
    ∫⁻ ω, ENNReal.ofReal (Real.exp (a * |scoreAt X (cusumTau k h X) ω|)) ∂μ ≠ ⊤ := by
  rw [lintegral_eq_tsum_slices k h X hX hindep hq hd1]
  refine ne_top_of_le_ne_top ?_
    (ENNReal.tsum_le_tsum fun m =>
      lintegral_slice_expAbs_scoreAt_le k h X hX hindep hM hq m)
  rw [ENNReal.tsum_mul_left]
  refine ENNReal.mul_ne_top hA ?_
  have hgeo := tsum_geometric_majorant_ne_top (c := (1 : ℝ≥0∞)) (d := d)
    ENNReal.one_ne_top (by simpa using hd)
  simpa using hgeo

/-- The stopped-score exponential moment, in `Integrable` form. -/
theorem integrable_exp_abs_scoreAt {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {a : ℝ} {A d : ℝ≥0∞} (hA : A ≠ ⊤)
    (hM : ∀ j, ∫⁻ ω, expAbsScore (2 * a) X j ω ∂μ ≤ A ^ (2 : ℕ))
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ d ^ (2 : ℕ))
    (hd1 : d ^ (2 : ℕ) < 1) (hd : d < 1) :
    Integrable (fun ω => Real.exp (a * |scoreAt X (cusumTau k h X) ω|)) μ := by
  have hmeas : Measurable (fun ω => Real.exp (a * |scoreAt X (cusumTau k h X) ω|)) :=
    Real.measurable_exp.comp ((measurable_scoreAt_cusumTau k h X hX).abs.const_mul a)
  refine ⟨hmeas.aestronglyMeasurable, ?_⟩
  rw [hasFiniteIntegral_iff_ofReal
    (Filter.Eventually.of_forall fun ω => Real.exp_nonneg _)]
  exact lt_top_iff_ne_top.mpr
    (lintegral_expAbs_scoreAt_ne_top k h X hX hindep hA hM hq hd1 hd)

/-- `L²` control of the stopped score, from its exponential moment. -/
theorem integrable_sq_scoreAt_of_exp {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) {a : ℝ} (ha : 0 < a)
    (hexp : Integrable (fun ω => Real.exp (a * |scoreAt X (cusumTau k h X) ω|)) μ) :
    Integrable (fun ω => scoreAt X (cusumTau k h X) ω ^ 2) μ := by
  refine Integrable.mono' (hexp.const_mul (4 / a ^ 2))
    (((measurable_scoreAt_cusumTau k h X hX).pow_const 2).aestronglyMeasurable) ?_
  filter_upwards with ω
  rw [Real.norm_eq_abs, abs_of_nonneg (sq_nonneg _)]
  exact sq_le_const_mul_exp_abs ha _

/-! ## The frozen Gaussian model: both gaps closed -/

/-- **C3-B, Gaussian form.**  `Zτ ∈ L²` for independent standard-Gaussian scores.

Note what is *not* claimed: the stopped score `Zτ = X_{τ-1}` is not asserted to
be `N(0,1)`.  Only the one-step law is used, through the Cauchy–Schwarz slice
bound. -/
theorem integrable_sq_scoreAt_gaussian {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    (hlaw : ∀ j, μ.map (X j) = gaussianReal 0 1) :
    Integrable (fun ω => scoreAt X (cusumTau k h X) ω ^ 2) μ := by
  obtain ⟨d, hd, hd1, hqd⟩ :=
    exists_sq_majorant_lt_one (gaussianReal_Iic_lt_one (h + k))
  set A : ℝ≥0∞ := gaussExpMoment (2 * 1) + 1 with hAdef
  have hAtop : A ≠ ⊤ := by
    rw [hAdef]
    exact ENNReal.add_ne_top.mpr ⟨gaussExpMoment_ne_top _, ENNReal.one_ne_top⟩
  have hA1 : (1 : ℝ≥0∞) ≤ A := by rw [hAdef]; exact le_add_self
  have hAsq : gaussExpMoment (2 * 1) ≤ A ^ (2 : ℕ) := by
    have hself : gaussExpMoment (2 * 1) ≤ A := by rw [hAdef]; exact le_self_add
    have hmul : A * 1 ≤ A * A := mul_le_mul' le_rfl hA1
    rw [pow_two]
    calc gaussExpMoment (2 * 1) ≤ A := hself
      _ = A * 1 := (mul_one A).symm
      _ ≤ A * A := hmul
  refine integrable_sq_scoreAt_of_exp k h X hX one_pos ?_
  refine integrable_exp_abs_scoreAt k h X hX hindep hAtop ?_ ?_ hd1 hd
  · intro j
    rw [lintegral_expAbsScore_eq_gaussExpMoment X hX hlaw (2 * 1) j]
    exact hAsq
  · intro j
    rw [measure_le_eq_gaussianReal X hX hlaw (h + k) j]
    exact hqd

/-- **C3-A, Gaussian form.**  The alarm time has an exponential moment at some
strictly positive rate. -/
theorem exists_pos_integrable_exp_abs_cusumTauReal_gaussian {μ : Measure Ω}
    (k h : ℝ) (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n))
    (hindep : iIndepFun X μ) (hlaw : ∀ j, μ.map (X j) = gaussianReal 0 1) :
    ∃ b : ℝ, 0 < b ∧
      Integrable (fun ω => Real.exp (b * |cusumTauReal k h X ω|)) μ := by
  set Q : ℝ≥0∞ := gaussianReal 0 1 (Set.Iic (h + k)) with hQdef
  have hQ1 : Q < 1 := gaussianReal_Iic_lt_one (h + k)
  have hQtop : Q ≠ ⊤ := hQ1.ne_top
  set r : ℝ := Q.toReal with hrdef
  have hr0 : 0 ≤ r := ENNReal.toReal_nonneg
  have hrQ : ENNReal.ofReal r = Q := ENNReal.ofReal_toReal hQtop
  have hr1 : r < 1 := by
    have hlt := (ENNReal.toReal_lt_toReal hQtop ENNReal.one_ne_top).mpr hQ1
    simpa using hlt
  obtain ⟨b, hb0, hbr⟩ := exists_pos_exp_mul_lt_one hr0 hr1
  refine ⟨b, hb0, ?_⟩
  refine integrable_exp_abs_cusumTauReal k h X hX hindep hr0 hb0.le ?_ ?_ hbr
  · intro j
    rw [hrQ, measure_le_eq_gaussianReal X hX hlaw (h + k) j]
  · rw [hrQ]; exact hQ1

/-- **The three Gate 4 moment inputs, at the actual detector.**  No abstract
domination function, no assumed stopped moment: `p` and `q` are produced, not
assumed. -/
theorem rebaseguard_separate_moments {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    (hlaw : ∀ j, μ.map (X j) = gaussianReal 0 1) :
    ∃ p q : ℝ, 0 < p ∧ 0 < q ∧
      Integrable (fun ω => scoreAt X (cusumTau k h X) ω ^ 2) μ ∧
      Integrable (fun ω => Real.exp (p * |walkAt X (cusumTau k h X) ω|)) μ ∧
      Integrable (fun ω => Real.exp (q * |cusumTauReal k h X ω|)) μ := by
  obtain ⟨p, hp0, hpint⟩ :=
    exists_pos_integrable_exp_abs_walkAt_gaussian k h X hX hindep hlaw
  obtain ⟨q, hq0, hqint⟩ :=
    exists_pos_integrable_exp_abs_cusumTauReal_gaussian k h X hX hindep hlaw
  exact ⟨p, q, hp0, hq0, integrable_sq_scoreAt_gaussian k h X hX hindep hlaw,
    hpint, hqint⟩

/-! ## The final identity -/

/-- **Gate 4.5-C3, Gaussian form.**  Differentiation under the expectation at
`e = 0` for the **actual** two-sided CUSUM stopped likelihood ratio:

`d/de E[Zτ · exp(-e Tτ - (e²/2) τ)]|_{e=0} = -E[Zτ Tτ]`,

with `Zτ = scoreAt`, `Tτ = walkAt`, `τ = cusumTauReal` at the genuine alarm time
`cusumTau k h X`.

The rates `p, q` supplied by C2.4 and C3-A are fixed and possibly tiny, so the
Gate 4 parameters are shrunk to fit: `δ = c = t` with
`t = min 1 (min (p/8) (q/6))`, giving `a = 2t`, `b = 3t²/2`, `4a = 8t ≤ p` and
`4b = 6t² ≤ 6t ≤ q`. -/
theorem hasDerivAt_integral_rebaseguard_gaussian {μ : Measure Ω} (k h : ℝ)
    (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    (hlaw : ∀ j, μ.map (X j) = gaussianReal 0 1) :
    HasDerivAt
      (fun e : ℝ => ∫ ω, scoreAt X (cusumTau k h X) ω *
        Real.exp (-e * walkAt X (cusumTau k h X) ω
          - (e ^ 2 / 2) * cusumTauReal k h X ω) ∂μ)
      (- ∫ ω, scoreAt X (cusumTau k h X) ω * walkAt X (cusumTau k h X) ω ∂μ)
      0 := by
  obtain ⟨p, q, hp0, hq0, hZsq, hTexp, hτexp⟩ :=
    rebaseguard_separate_moments k h X hX hindep hlaw
  set t : ℝ := min 1 (min (p / 8) (q / 6)) with htdef
  have ht0 : 0 < t := by
    rw [htdef]
    exact lt_min one_pos (lt_min (by linarith) (by linarith))
  have ht1 : t ≤ 1 := by rw [htdef]; exact min_le_left _ _
  have htp : t ≤ p / 8 := le_trans (by rw [htdef]; exact min_le_right _ _) (min_le_left _ _)
  have htq : t ≤ q / 6 := le_trans (by rw [htdef]; exact min_le_right _ _) (min_le_right _ _)
  exact hasDerivAt_integral_stoppedIntegrand_zero_of_separate_moments
    (aestronglyMeasurable_scoreAt_cusumTau k h X hX)
    (aestronglyMeasurable_walkAt_cusumTau k h X hX)
    (aestronglyMeasurable_cusumTauReal k h X hX)
    (δ := t) (c := t) (a := 2 * t) (b := 3 * t ^ 2 / 2) (p := p) (q := q)
    ht0 ht0 (by linarith) (by nlinarith) (by linarith) (by nlinarith)
    hZsq hTexp hτexp

/-- **Gate 4.5-C3, frozen ReBaseGuard detector.**  The two-sided CUSUM with
`k = 1/2`, `h = 5`, alarm `max(S⁺,S⁻) ≥ 5`, driven by i.i.d. `N(0,1)` scores.

This is the end of the analytic chain: the assumptions are exactly the frozen
model (measurability, independence, standard-Gaussian marginals), and the
conclusion is exactly the ReBaseGuard differentiation identity. -/
theorem hasDerivAt_rebaseguard_cusum {μ : Measure Ω}
    (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    (hlaw : ∀ j, μ.map (X j) = gaussianReal 0 1) :
    HasDerivAt
      (fun e : ℝ => ∫ ω, scoreAt X (cusumTau (1 / 2) 5 X) ω *
        Real.exp (-e * walkAt X (cusumTau (1 / 2) 5 X) ω
          - (e ^ 2 / 2) * cusumTauReal (1 / 2) 5 X ω) ∂μ)
      (- ∫ ω, scoreAt X (cusumTau (1 / 2) 5 X) ω
            * walkAt X (cusumTau (1 / 2) 5 X) ω ∂μ)
      0 :=
  hasDerivAt_integral_rebaseguard_gaussian (1 / 2) 5 X hX hindep hlaw

end RebaseguardLean
