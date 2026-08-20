import RebaseguardLean.StoppedWalkMoment

/-!
# Gate 4.5-C2.4: the small-rate existence theorem

Gate 4.5-C2.3 proved the stopped-walk exponential moment *conditionally* on scalar
data `c, d` satisfying `c * d < 1`.  This file shows those conditions are actually
satisfiable for some `a > 0`, and hence proves the **existential** form.

## Why the crude bound does not work

With the frozen detector `k = 1/2`, `h = 5`, the forcing level is `H = 11/2` and
`q = P(Z ≤ 11/2)` is within `2·10⁻⁸` of `1`.  So `d ≥ √q` is within `10⁻⁸` of `1`,
and `c < 1/d` forces `M(2a) ≤ 1 + O(10⁻⁸)`.  The familiar bound
`E e^{t|Z|} ≤ E e^{tZ} + E e^{-tZ} = 2 e^{t²/2}` tends to **2**, not `1`, so it can
never satisfy `c * d < 1`.  It is true but useless here.

## What is used instead: convexity of `exp`

For `0 ≤ t ≤ ε`, with `θ = t/ε ∈ [0,1]` and `u = ε|z| ≥ 0`, convexity of `exp` gives
`e^{t|z|} = e^{θ·u + (1-θ)·0} ≤ θ e^u + (1-θ) ≤ 1 + (t/ε) e^{ε|z|}`.
Integrating against a probability measure yields
`M_j(t) ≤ 1 + (t/ε)·M_ε`, which tends to `1` as `t ↓ 0` **uniformly in `j`**,
from a single one-step hypothesis at radius `ε`.  No dominated convergence is needed
and the witness for `a` is explicit.
-/

noncomputable section

open MeasureTheory ProbabilityTheory Filter
open scoped ENNReal

namespace RebaseguardLean

variable {Ω : Type*} [mΩ : MeasurableSpace Ω]

/-! ## C2.4.1 — the one-step small-rate bound -/

/-- **Convexity bound.**  For `0 ≤ t ≤ ε`, `e^{t|z|} ≤ 1 + (t/ε)·e^{ε|z|}`. -/
lemma exp_abs_le_convex {ε t z : ℝ} (hε : 0 < ε) (ht0 : 0 ≤ t) (htε : t ≤ ε) :
    Real.exp (t * |z|) ≤ 1 + (t / ε) * Real.exp (ε * |z|) := by
  have hθ0 : 0 ≤ t / ε := div_nonneg ht0 hε.le
  have hθ1 : t / ε ≤ 1 := (div_le_one hε).mpr htε
  have hkey := convexOn_exp.2 (Set.mem_univ (ε * |z|)) (Set.mem_univ (0 : ℝ))
      hθ0 (by linarith : (0 : ℝ) ≤ 1 - t / ε) (by ring)
  simp only [smul_eq_mul, mul_zero, add_zero, Real.exp_zero, mul_one] at hkey
  have harg : t / ε * (ε * |z|) = t * |z| := by
    field_simp
  rw [harg] at hkey
  linarith

/-- The `ℝ≥0∞` form of the convexity bound, integrated. -/
lemma lintegral_expAbsScore_le {μ : Measure Ω} [IsProbabilityMeasure μ]
    (X : ℕ → Ω → ℝ) {ε t : ℝ} (hε : 0 < ε) (ht0 : 0 ≤ t) (htε : t ≤ ε) (j : ℕ) :
    ∫⁻ ω, expAbsScore t X j ω ∂μ
      ≤ 1 + ENNReal.ofReal (t / ε) * ∫⁻ ω, expAbsScore ε X j ω ∂μ := by
  have hθ0 : 0 ≤ t / ε := div_nonneg ht0 hε.le
  have hpt : ∀ ω, expAbsScore t X j ω
      ≤ 1 + ENNReal.ofReal (t / ε) * expAbsScore ε X j ω := by
    intro ω
    unfold expAbsScore
    calc ENNReal.ofReal (Real.exp (t * |X j ω|))
        ≤ ENNReal.ofReal (1 + (t / ε) * Real.exp (ε * |X j ω|)) :=
          ENNReal.ofReal_le_ofReal (exp_abs_le_convex hε ht0 htε)
      _ = 1 + ENNReal.ofReal (t / ε) * ENNReal.ofReal (Real.exp (ε * |X j ω|)) := by
          rw [ENNReal.ofReal_add (by norm_num)
                (mul_nonneg hθ0 (Real.exp_nonneg _)),
              ENNReal.ofReal_mul hθ0, ENNReal.ofReal_one]
  calc ∫⁻ ω, expAbsScore t X j ω ∂μ
      ≤ ∫⁻ ω, (1 + ENNReal.ofReal (t / ε) * expAbsScore ε X j ω) ∂μ :=
        lintegral_mono hpt
    _ = (∫⁻ _ω, (1 : ℝ≥0∞) ∂μ)
          + ENNReal.ofReal (t / ε) * ∫⁻ ω, expAbsScore ε X j ω ∂μ := by
        rw [lintegral_add_left measurable_const,
            lintegral_const_mul' _ _ ENNReal.ofReal_ne_top]
    _ = 1 + ENNReal.ofReal (t / ε) * ∫⁻ ω, expAbsScore ε X j ω ∂μ := by simp

/-- **Gate 4.5-C2.4.1.**  From a single one-step exponential moment at radius `ε`,
the moment at rate `2a` can be pushed below `1 + η` for any `η > 0`, by choosing
`a > 0` small.  The bound is uniform in `j` and the witness is explicit. -/
theorem exists_rate_lintegral_le {μ : Measure Ω} [IsProbabilityMeasure μ]
    (X : ℕ → Ω → ℝ) {ε : ℝ} (hε : 0 < ε) {Mε : ℝ≥0∞} (hMtop : Mε ≠ ⊤)
    (hMε : ∀ j, ∫⁻ ω, expAbsScore ε X j ω ∂μ ≤ Mε)
    {η : ℝ} (hη : 0 < η) :
    ∃ a : ℝ, 0 < a ∧
      ∀ j, ∫⁻ ω, expAbsScore (2 * a) X j ω ∂μ ≤ 1 + ENNReal.ofReal η := by
  set m : ℝ := Mε.toReal with hmdef
  have hm0 : 0 ≤ m := ENNReal.toReal_nonneg
  have hmp : 0 < m + 1 := by linarith
  set t : ℝ := min ε (ε * η / (m + 1)) with htdef
  have ht0 : 0 < t := lt_min hε (by positivity)
  have htε : t ≤ ε := min_le_left _ _
  refine ⟨t / 2, by linarith, fun j => ?_⟩
  have h2a : 2 * (t / 2) = t := by ring
  rw [h2a]
  refine le_trans (lintegral_expAbsScore_le X hε ht0.le htε j) ?_
  have hstep : ENNReal.ofReal (t / ε) * ∫⁻ ω, expAbsScore ε X j ω ∂μ
      ≤ ENNReal.ofReal η := by
    have hMeq : Mε = ENNReal.ofReal m := (ENNReal.ofReal_toReal hMtop).symm
    have h1 : ENNReal.ofReal (t / ε) * ∫⁻ ω, expAbsScore ε X j ω ∂μ
        ≤ ENNReal.ofReal (t / ε) * ENNReal.ofReal m := by
      refine mul_le_mul' le_rfl ?_
      rw [← hMeq]
      exact hMε j
    refine le_trans h1 ?_
    rw [← ENNReal.ofReal_mul (div_nonneg ht0.le hε.le)]
    refine ENNReal.ofReal_le_ofReal ?_
    have htle : t ≤ ε * η / (m + 1) := min_le_right _ _
    have h2 : t * (m + 1) ≤ ε * η := by
      calc t * (m + 1) ≤ (ε * η / (m + 1)) * (m + 1) :=
            mul_le_mul_of_nonneg_right htle hmp.le
        _ = ε * η := by field_simp
    have hkey : t * m ≤ ε * η := by nlinarith [h2, hm0, ht0.le]
    rw [div_mul_eq_mul_div, div_le_iff₀ hε]
    nlinarith [hkey]
  calc (1 : ℝ≥0∞) + ENNReal.ofReal (t / ε) * ∫⁻ ω, expAbsScore ε X j ω ∂μ
      ≤ 1 + ENNReal.ofReal η := by gcongr

/-! ## C2.4.2 — the existential stopped-walk exponential moment

Explicit real witnesses.  With `qr = q.toReal ∈ [0,1)` put

* `dr = (1+qr)/2`   — then `qr ≤ dr²` because `(1-qr)² ≥ 0`, and `dr < 1`;
* `cr = (1+dr)/(2dr)` — then `cr > 1` and `cr·dr = (1+dr)/2 < 1`;
* `η  = cr² - 1 > 0`, fed to `exists_rate_lintegral_le` to obtain `a > 0`.

These are handed straight to the frozen Gate 4.5-C2.3 theorem. -/

theorem exists_pos_integrable_exp_abs_walkAt {μ : Measure Ω} (k h : ℝ)
    (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {ε : ℝ} (hε : 0 < ε) {Mε : ℝ≥0∞} (hMtop : Mε ≠ ⊤)
    (hMε : ∀ j, ∫⁻ ω, expAbsScore ε X j ω ∂μ ≤ Mε)
    {q : ℝ≥0∞} (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ q) (hq1 : q < 1) :
    ∃ a : ℝ, 0 < a ∧
      Integrable (fun ω => Real.exp (a * |walkAt X (cusumTau k h X) ω|)) μ := by
  haveI := hindep.isProbabilityMeasure
  have hqtop : q ≠ ⊤ := hq1.ne_top
  set qr : ℝ := q.toReal with hqrdef
  have hqr0 : 0 ≤ qr := ENNReal.toReal_nonneg
  have hqr1 : qr < 1 := by
    have hlt := (ENNReal.toReal_lt_toReal hqtop ENNReal.one_ne_top).mpr hq1
    simpa using hlt
  set dr : ℝ := (1 + qr) / 2 with hdrdef
  have hdr0 : 0 < dr := by rw [hdrdef]; linarith
  have hdr1 : dr < 1 := by rw [hdrdef]; linarith
  have hdrne : dr ≠ 0 := ne_of_gt hdr0
  set cr : ℝ := (1 + dr) / (2 * dr) with hcrdef
  have hcr1 : 1 < cr := by
    rw [hcrdef, one_lt_div (by linarith : (0:ℝ) < 2 * dr)]
    linarith
  have hcr0 : 0 < cr := by linarith
  have hcrd : cr * dr < 1 := by
    have hval : cr * dr = (1 + dr) / 2 := by
      rw [hcrdef]; field_simp
    rw [hval]; linarith
  set η : ℝ := cr ^ 2 - 1 with hηdef
  have hη0 : 0 < η := by rw [hηdef]; nlinarith
  obtain ⟨a, ha0, hbound⟩ := exists_rate_lintegral_le X hε hMtop hMε hη0
  refine ⟨a, ha0, ?_⟩
  have hc2 : (ENNReal.ofReal cr) ^ (2 : ℕ) = 1 + ENNReal.ofReal η := by
    rw [← ENNReal.ofReal_pow hcr0.le]
    have hsq : cr ^ 2 = 1 + η := by rw [hηdef]; ring
    rw [hsq, ENNReal.ofReal_add zero_le_one hη0.le, ENNReal.ofReal_one]
  refine integrable_exp_abs_walkAt_of_moment_tail k h X hX hindep ha0.le
      (c := ENNReal.ofReal cr) (d := ENNReal.ofReal dr)
      ENNReal.ofReal_ne_top ?_ ?_ ?_ ?_
  · intro j
    rw [hc2]
    exact hbound j
  · intro j
    refine le_trans (hq j) ?_
    rw [← ENNReal.ofReal_toReal hqtop, ← ENNReal.ofReal_pow hdr0.le]
    refine ENNReal.ofReal_le_ofReal ?_
    rw [hdrdef]
    nlinarith [hqr0, hqr1]
  · rw [← ENNReal.ofReal_pow hdr0.le, ENNReal.ofReal_lt_one]
    nlinarith [hdr0, hdr1]
  · rw [← ENNReal.ofReal_mul hcr0.le, ENNReal.ofReal_lt_one]
    exact hcrd

/-! ## C2.4.3 — the frozen ReBaseGuard Gaussian model

`X_j ~ N(0,1)` is encoded honestly as `μ.map (X j) = gaussianReal 0 1`; both the
one-step exponential moment and the forcing bound `q < 1` are *derived* from it,
not assumed. -/

/-- One-step exponential moment of the standard Gaussian law. -/
def gaussExpMoment (ε : ℝ) : ℝ≥0∞ :=
  ∫⁻ x, ENNReal.ofReal (Real.exp (ε * |x|)) ∂(gaussianReal 0 1)

lemma integrable_exp_mul_abs_gaussianReal (ε : ℝ) :
    Integrable (fun x : ℝ => Real.exp (ε * |x|)) (gaussianReal 0 1) :=
  integrable_exp_mul_abs (X := fun x : ℝ => x)
    (integrable_exp_mul_gaussianReal ε) (integrable_exp_mul_gaussianReal (-ε))

lemma gaussExpMoment_ne_top (ε : ℝ) : gaussExpMoment ε ≠ ⊤ := by
  have hfin := (integrable_exp_mul_abs_gaussianReal ε).hasFiniteIntegral
  rw [hasFiniteIntegral_iff_ofReal
    (Filter.Eventually.of_forall fun x => Real.exp_nonneg _)] at hfin
  exact hfin.ne

lemma lintegral_expAbsScore_eq_gaussExpMoment {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hlaw : ∀ j, μ.map (X j) = gaussianReal 0 1)
    (ε : ℝ) (j : ℕ) :
    ∫⁻ ω, expAbsScore ε X j ω ∂μ = gaussExpMoment ε := by
  unfold expAbsScore gaussExpMoment
  rw [← hlaw j]
  exact (lintegral_map (measurable_expAbs_map ε) (hX j)).symm

/-- The standard Gaussian charges every upper half-line: its density is positive
everywhere and `volume (Ioi H) = ∞`. -/
lemma gaussianReal_Ioi_pos (H : ℝ) : 0 < gaussianReal 0 1 (Set.Ioi H) := by
  rw [pos_iff_ne_zero]
  intro hzero
  rw [gaussianReal_of_var_ne_zero _ (by norm_num),
      withDensity_apply_eq_zero (measurable_gaussianPDF 0 1)] at hzero
  have hset : {x : ℝ | gaussianPDF 0 1 x ≠ 0} ∩ Set.Ioi H = Set.Ioi H :=
    Set.inter_eq_right.mpr fun x _ => (gaussianPDF_pos 0 (by norm_num) x).ne'
  rw [hset, Real.volume_Ioi] at hzero
  exact ENNReal.top_ne_zero hzero

/-- **Forcing bound, derived.**  `q = P(Z ≤ H) < 1` for standard Gaussian `Z`. -/
lemma gaussianReal_Iic_lt_one (H : ℝ) : gaussianReal 0 1 (Set.Iic H) < 1 := by
  have hcompl : (Set.Iic H)ᶜ = Set.Ioi H := by ext x; simp
  have hsum : gaussianReal 0 1 (Set.Iic H) + gaussianReal 0 1 (Set.Ioi H) = 1 := by
    rw [← hcompl, measure_add_measure_compl measurableSet_Iic, measure_univ]
  have hane : gaussianReal 0 1 (Set.Iic H) ≠ ⊤ := (measure_lt_top _ _).ne
  have hlt : gaussianReal 0 1 (Set.Iic H)
      < gaussianReal 0 1 (Set.Iic H) + gaussianReal 0 1 (Set.Ioi H) :=
    ENNReal.lt_add_right hane (gaussianReal_Ioi_pos H).ne'
  rwa [hsum] at hlt

lemma measure_le_eq_gaussianReal {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hlaw : ∀ j, μ.map (X j) = gaussianReal 0 1)
    (H : ℝ) (j : ℕ) :
    μ {ω | X j ω ≤ H} = gaussianReal 0 1 (Set.Iic H) := by
  rw [← hlaw j, Measure.map_apply (hX j) measurableSet_Iic]
  rfl

/-- **Gate 4.5-C2.4, Gaussian form.**  For independent standard-Gaussian scores,
the stopped walk at the actual two-sided CUSUM alarm has an exponential moment at
some strictly positive rate.  No `hM`/`hq`/`hcd` hypotheses remain. -/
theorem exists_pos_integrable_exp_abs_walkAt_gaussian {μ : Measure Ω}
    (k h : ℝ) (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n))
    (hindep : iIndepFun X μ) (hlaw : ∀ j, μ.map (X j) = gaussianReal 0 1) :
    ∃ a : ℝ, 0 < a ∧
      Integrable (fun ω => Real.exp (a * |walkAt X (cusumTau k h X) ω|)) μ := by
  refine exists_pos_integrable_exp_abs_walkAt k h X hX hindep (ε := 1) one_pos
    (Mε := gaussExpMoment 1) (gaussExpMoment_ne_top 1)
    (fun j => le_of_eq (lintegral_expAbsScore_eq_gaussExpMoment X hX hlaw 1 j))
    (q := gaussianReal 0 1 (Set.Iic (h + k)))
    (fun j => le_of_eq (measure_le_eq_gaussianReal X hX hlaw (h + k) j))
    (gaussianReal_Iic_lt_one (h + k))

/-- **Gate 4.5-C2.4, frozen ReBaseGuard detector** (`k = 1/2`, `h = 5`). -/
theorem exists_pos_integrable_exp_abs_walkAt_rebaseguard {μ : Measure Ω}
    (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n))
    (hindep : iIndepFun X μ) (hlaw : ∀ j, μ.map (X j) = gaussianReal 0 1) :
    ∃ a : ℝ, 0 < a ∧
      Integrable
        (fun ω => Real.exp (a * |walkAt X (cusumTau (1 / 2) 5 X) ω|)) μ :=
  exists_pos_integrable_exp_abs_walkAt_gaussian (1 / 2) 5 X hX hindep hlaw

end RebaseguardLean
