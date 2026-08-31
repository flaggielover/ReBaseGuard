import StabilityMapP3

/-!
# Level-4 Priority 4: general location-family proof spine

Priority 4 generalises the closed Gaussian derivative mechanism.  Its Lean
layer does three things that the closed spines do not.

1. **It replaces the Gaussian likelihood by an abstract one.**  The Priority-1
   and Priority-2 bridges are stated for the concrete integrand
   `A ω * exp (-e * T ω - (e^2/2) * τ ω)`.  Here the family `L` is arbitrary,
   and the Gaussian one is recovered as an instance
   (`gaussianLikelihood_hasDerivAt`, `gaussian_reuse_derivative`).

2. **It weakens the differentiation hypothesis.**  The closed spines consume a
   dominated *pointwise derivative* on a whole neighbourhood, which the Laplace
   family does not satisfy.  This file uses the Lipschitz form
   (`hasDerivAt_integral_of_dominated_loc_of_lip`), which needs a derivative
   only at the base point.

3. **It separates what is generic from what is Gaussian.**  The random
   denominator decomposition is proved for an arbitrary score
   (`generalDirect_eq_fixed_add_short`); its *sign* is shown to be exactly the
   sign of `T * S`, positive for the Gaussian score and strictly negative on an
   explicit bounded-score witness.

Nothing here constructs a stochastic process, a stopping time, or a
location-family density.  The measure-theoretic and analytic obligations stay
visible as hypotheses, and `LEAN_CORRESPONDENCE.md` records the boundary.
-/

noncomputable section

open MeasureTheory Filter Set
open scoped Topology

namespace RebaseguardLean.Level4Priority4

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

/-! ## 1. The general stopped-likelihood derivative bridge -/

/-- **Priority-4 core bridge.**  For an abstract stopped likelihood family `L`
with `L 0 = 1` and derivative `-S` at zero, differentiation under the integral
gives the score identity `d/de E_e[A] = -E_0[A S]`.

The hypothesis `hlip` asks only that `e ↦ A ω * L e ω` be Lipschitz on a fixed
ball with an integrable constant.  It does **not** ask for differentiability
away from `0`, which is what makes the statement usable for a location family
whose log-density has a kink. -/
theorem hasDerivAt_stoppedMean
    {A S : Ω → ℝ} {L : ℝ → Ω → ℝ} {bound : Ω → ℝ} {δ : ℝ}
    (hδ : 0 < δ)
    (hmeas : ∀ᶠ e in 𝓝 (0 : ℝ),
      AEStronglyMeasurable (fun ω => A ω * L e ω) μ)
    (hbase : ∀ᵐ ω ∂μ, L 0 ω = 1)
    (hAint : Integrable A μ)
    (hASmeas : AEStronglyMeasurable (fun ω => A ω * S ω) μ)
    (hlip : ∀ᵐ ω ∂μ, LipschitzOnWith (Real.nnabs (bound ω))
      (fun e => A ω * L e ω) (Metric.ball (0 : ℝ) δ))
    (hbound : Integrable bound μ)
    (hderiv : ∀ᵐ ω ∂μ, HasDerivAt (fun e => L e ω) (-S ω) 0) :
    HasDerivAt (fun e : ℝ => ∫ ω, A ω * L e ω ∂μ)
      (-∫ ω, A ω * S ω ∂μ) 0 := by
  have hs : Metric.ball (0 : ℝ) δ ∈ 𝓝 (0 : ℝ) := Metric.ball_mem_nhds _ hδ
  have hF_int : Integrable (fun ω => A ω * L 0 ω) μ := by
    refine hAint.congr ?_
    filter_upwards [hbase] with ω hω
    simp [hω]
  have hF'_meas : AEStronglyMeasurable (fun ω => -(A ω * S ω)) μ := hASmeas.neg
  have h_diff : ∀ᵐ ω ∂μ,
      HasDerivAt (fun e => A ω * L e ω) (-(A ω * S ω)) 0 := by
    filter_upwards [hderiv] with ω hω
    have := hω.const_mul (A ω)
    simpa [mul_neg] using this
  obtain ⟨-, key⟩ :=
    hasDerivAt_integral_of_dominated_loc_of_lip (bound := bound)
      (F := fun e ω => A ω * L e ω) (F' := fun ω => -(A ω * S ω))
      hs hmeas hF_int hF'_meas hlip hbound h_diff
  rwa [integral_neg] at key

/-- The reuse map `F_{ρ,m}(e) = ρ (e + E_e[A])` for a general likelihood.  The
`ρ` scaling is exact algebra and is imported unchanged from the closed
Priority-1 spine. -/
theorem reuse_derivative
    {A S : Ω → ℝ} {L : ℝ → Ω → ℝ} {bound : Ω → ℝ} {δ : ℝ} (ρ : ℝ)
    (hδ : 0 < δ)
    (hmeas : ∀ᶠ e in 𝓝 (0 : ℝ),
      AEStronglyMeasurable (fun ω => A ω * L e ω) μ)
    (hbase : ∀ᵐ ω ∂μ, L 0 ω = 1)
    (hAint : Integrable A μ)
    (hASmeas : AEStronglyMeasurable (fun ω => A ω * S ω) μ)
    (hlip : ∀ᵐ ω ∂μ, LipschitzOnWith (Real.nnabs (bound ω))
      (fun e => A ω * L e ω) (Metric.ball (0 : ℝ) δ))
    (hbound : Integrable bound μ)
    (hderiv : ∀ᵐ ω ∂μ, HasDerivAt (fun e => L e ω) (-S ω) 0) :
    HasDerivAt (fun e : ℝ => ρ * (e + ∫ ω, A ω * L e ω ∂μ))
      (ρ * (1 - ∫ ω, A ω * S ω ∂μ)) 0 :=
  Level4Priority1.rho_derivative_of_expectation_derivative
    (hasDerivAt_stoppedMean hδ hmeas hbase hAint hASmeas hlip hbound hderiv)

/-! ## 2. The Gaussian family is one instance, not the statement -/

/-- The frozen Gaussian stopped likelihood, as it appears in the closed
Priority-1 and Priority-2 spines. -/
def gaussianLikelihood (T τR : Ω → ℝ) (e : ℝ) (ω : Ω) : ℝ :=
  Real.exp (-e * T ω - (e ^ 2 / 2) * τR ω)

omit [MeasurableSpace Ω] in
@[simp] theorem gaussianLikelihood_zero (T τR : Ω → ℝ) (ω : Ω) :
    gaussianLikelihood T τR 0 ω = 1 := by
  simp [gaussianLikelihood]

omit [MeasurableSpace Ω] in
/-- The Gaussian family satisfies the abstract hypothesis with score `T`. -/
theorem gaussianLikelihood_hasDerivAt (T τR : Ω → ℝ) (ω : Ω) :
    HasDerivAt (fun e : ℝ => gaussianLikelihood T τR e ω) (-T ω) 0 := by
  have hsub :=
    (((hasDerivAt_id (0 : ℝ)).neg).mul_const (T ω)).sub
      (((hasDerivAt_pow 2 (0 : ℝ)).div_const 2).mul_const (τR ω))
  have h := hsub.exp
  norm_num at h
  simpa [gaussianLikelihood] using h

/-- Specialising the general bridge to the Gaussian family reproduces exactly
the conclusion of the closed Priority-1 and Priority-2 derivative spines.  The
Gaussian case is therefore a corollary of the general one, not a parallel
result. -/
theorem gaussian_reuse_derivative
    {A T τR : Ω → ℝ} {bound : Ω → ℝ} {δ : ℝ} (ρ : ℝ)
    (hδ : 0 < δ)
    (hmeas : ∀ᶠ e in 𝓝 (0 : ℝ),
      AEStronglyMeasurable (fun ω => A ω * gaussianLikelihood T τR e ω) μ)
    (hAint : Integrable A μ)
    (hATmeas : AEStronglyMeasurable (fun ω => A ω * T ω) μ)
    (hlip : ∀ᵐ ω ∂μ, LipschitzOnWith (Real.nnabs (bound ω))
      (fun e => A ω * gaussianLikelihood T τR e ω) (Metric.ball (0 : ℝ) δ))
    (hbound : Integrable bound μ) :
    HasDerivAt
      (fun e : ℝ => ρ * (e + ∫ ω, A ω *
        Real.exp (-e * T ω - (e ^ 2 / 2) * τR ω) ∂μ))
      (ρ * (1 - ∫ ω, A ω * T ω ∂μ)) 0 :=
  reuse_derivative ρ hδ hmeas
    (Filter.Eventually.of_forall fun ω => gaussianLikelihood_zero T τR ω)
    hAint hATmeas hlip hbound
    (Filter.Eventually.of_forall fun ω => gaussianLikelihood_hasDerivAt T τR ω)

/-! ## 3. Random denominator: the identity is generic, the sign is Gaussian -/

/-- Window average against a general stopped score, with the random
denominator `min m τ`. -/
def generalDirect (m τ : ℕ) (num S : ℝ) : ℝ :=
  num / (Level4Priority1.windowLength m τ : ℝ) * S

/-- The same numerator over the fixed denominator `m`. -/
def generalFixed (m : ℕ) (num S : ℝ) : ℝ := num / (m : ℝ) * S

/-- The short-cycle correction for a general score.  For the Gaussian score
`S = T` this is Priority 1's `shortCorrection`. -/
def generalShortCorrection (m τ : ℕ) (T S : ℝ) : ℝ :=
  if τ < m then (1 / (τ : ℝ) - 1 / (m : ℝ)) * (T * S) else 0

/-- **The decomposition generalises verbatim.**  No property of the score is
used: only that on a short cycle the reuse window is the whole stopped path. -/
theorem generalDirect_eq_fixed_add_short {m τ : ℕ} {num T S : ℝ}
    (hwhole : τ < m → num = T) :
    generalDirect m τ num S = generalFixed m num S
      + generalShortCorrection m τ T S := by
  by_cases hshort : τ < m
  · have hnum : num = T := hwhole hshort
    simp [generalDirect, generalFixed, generalShortCorrection,
      Level4Priority1.windowLength_eq_tau_of_short hshort, hshort, hnum]
    ring
  · have hfull : m ≤ τ := Nat.le_of_not_gt hshort
    simp [generalDirect, generalFixed, generalShortCorrection,
      Level4Priority1.windowLength_eq_m_of_full hfull, hshort]

/-- For the Gaussian score the general correction is Priority 1's. -/
theorem generalShortCorrection_gaussian (m τ : ℕ) (T : ℝ) :
    generalShortCorrection m τ T T = Level4Priority1.shortCorrection m τ T := by
  by_cases hshort : τ < m <;>
    simp [generalShortCorrection, Level4Priority1.shortCorrection, hshort, sq]

/-- The correction is nonnegative exactly when `T * S` is.  The Gaussian score
makes `T * S = T^2`, which is why Priority 1 could prove nonnegativity
unconditionally. -/
theorem generalShortCorrection_nonneg {m τ : ℕ} {T S : ℝ}
    (hτ : 0 < τ) (hTS : 0 ≤ T * S) :
    0 ≤ generalShortCorrection m τ T S := by
  by_cases hshort : τ < m
  · have hτr : (0 : ℝ) < (τ : ℝ) := by exact_mod_cast hτ
    have hτm : (τ : ℝ) ≤ (m : ℝ) := by exact_mod_cast Nat.le_of_lt hshort
    have hdiff : 0 ≤ 1 / (τ : ℝ) - 1 / (m : ℝ) :=
      sub_nonneg.mpr (one_div_le_one_div_of_le hτr hτm)
    simpa [generalShortCorrection, hshort] using mul_nonneg hdiff hTS
  · simp [generalShortCorrection, hshort]

/-- **What does not generalise.**  With a score that is not proportional to the
identity the correction can be strictly negative on a short cycle, so the
truncated-window gain can be *smaller* than the fixed-denominator gain -- the
exact opposite of the Gaussian conclusion. -/
theorem generalShortCorrection_neg {m τ : ℕ} {T S : ℝ}
    (hshort : τ < m) (hτ : 0 < τ) (hTS : T * S < 0) :
    generalShortCorrection m τ T S < 0 := by
  have hτr : (0 : ℝ) < (τ : ℝ) := by exact_mod_cast hτ
  have hτm : (τ : ℝ) < (m : ℝ) := by exact_mod_cast hshort
  have hdiff : 0 < 1 / (τ : ℝ) - 1 / (m : ℝ) :=
    sub_pos.mpr (one_div_lt_one_div_of_lt hτr hτm)
  simpa [generalShortCorrection, hshort] using mul_neg_of_pos_of_neg hdiff hTS

/-- The bounded (Laplace-type) score, normalised to `b = 1`. -/
def signScore (z : ℝ) : ℝ := if 0 < z then 1 else if z < 0 then -1 else 0

/-- The witness residual prefix of `PROOF.md` Section 6. -/
def witnessPrefix : List ℝ := [5, -1, -1, -1]

theorem witnessPrefix_total : witnessPrefix.sum = 2 := by
  norm_num [witnessPrefix]

theorem witnessPrefix_score : (witnessPrefix.map signScore).sum = -2 := by
  norm_num [witnessPrefix, signScore]

/-- On that prefix the short-cycle correction is strictly negative, and equals
`-1/5` exactly.  The path has `τ = 4 < m = 5`. -/
theorem witness_shortCorrection :
    generalShortCorrection 5 4 witnessPrefix.sum
      (witnessPrefix.map signScore).sum = -(1 / 5) := by
  rw [witnessPrefix_total, witnessPrefix_score]
  norm_num [generalShortCorrection]

theorem witness_shortCorrection_neg :
    generalShortCorrection 5 4 witnessPrefix.sum
      (witnessPrefix.map signScore).sum < 0 := by
  rw [witness_shortCorrection]; norm_num

/-! ## 4. Neutrality of a non-selective stopping rule -/

/-- **Corollary G2, algebraic core.**  If the cross moments
`E[Z_s ψ(Z_t)]` are `1` on the diagonal and `0` off it -- which integration by
parts gives for *every* regular location family, with no variance appearing --
then the gain of a deterministic stopping rule is exactly one, for every window
length. -/
theorem neutral_gain_of_orthonormal_cross
    {n w : ℕ} (window : Finset ℕ) (hsub : window ⊆ Finset.range n)
    (hcard : window.card = w) (hw : 0 < w) :
    (1 / (w : ℝ)) * ∑ s ∈ window, ∑ t ∈ Finset.range n,
      (if s = t then (1 : ℝ) else 0) = 1 := by
  have hinner : ∀ s ∈ window,
      (∑ t ∈ Finset.range n, if s = t then (1 : ℝ) else 0) = 1 := by
    intro s hs
    rw [Finset.sum_ite_eq (Finset.range n) s (fun _ => (1 : ℝ))]
    simp [hsub hs]
  rw [Finset.sum_congr rfl hinner]
  have hwr : (w : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr hw.ne'
  simp [hcard, hwr]

/-- The multiplier of a non-selective rule is exactly zero, for every reuse
fraction. -/
theorem neutral_multiplier (ρ : ℝ) :
    Priority3Map.multiplier ρ 1 = 0 := by
  simp [Priority3Map.multiplier]

/-! ## 5. Symmetry gives the fixed point, and only the fixed point -/

/-- If a measure-preserving involution negates the reuse statistic, its mean is
zero and the origin is a fixed point of the reuse map.  This is the *only*
place symmetry is used; the derivative identity above never invokes it. -/
theorem integral_eq_zero_of_odd_under_involution
    {A : Ω → ℝ} (J : Ω ≃ᵐ Ω) (hJ : MeasurePreserving J μ μ)
    (hodd : ∀ ω, A (J ω) = -A ω) :
    ∫ ω, A ω ∂μ = 0 := by
  have h1 : ∫ ω, A (J ω) ∂μ = ∫ ω, A ω ∂μ :=
    hJ.integral_comp J.measurableEmbedding A
  have h2 : ∫ ω, A (J ω) ∂μ = -∫ ω, A ω ∂μ := by
    simp only [hodd]
    exact integral_neg A
  linarith [h1, h2]

/-- With a zero-mean reuse statistic the origin is a fixed point of the
conditional-mean reuse map. -/
theorem reuse_fixed_point_of_zero_mean
    {A : Ω → ℝ} {L : ℝ → Ω → ℝ} (ρ : ℝ)
    (hbase : ∀ᵐ ω ∂μ, L 0 ω = 1)
    (_hAint : Integrable A μ)
    (hzero : ∫ ω, A ω ∂μ = 0) :
    ρ * (0 + ∫ ω, A ω * L 0 ω ∂μ) = 0 := by
  have : ∫ ω, A ω * L 0 ω ∂μ = ∫ ω, A ω ∂μ := by
    refine integral_congr_ae ?_
    filter_upwards [hbase] with ω hω
    simp [hω]
  rw [this, hzero]; ring

/-! ## 6. Bridge into the closed Priority-3 classification -/

/-- The general gain feeds the closed stability map unchanged: below the
critical reuse fraction the general location-family multiplier is attracting.
Priority 3's classification is reused verbatim, which is what "no contradiction
with the closed core" means formally. -/
theorem general_attracting_of_lt_criticalRho
    {A S : Ω → ℝ} {L : ℝ → Ω → ℝ} {bound : Ω → ℝ} {δ ρ : ℝ}
    (hδ : 0 < δ)
    (hmeas : ∀ᶠ e in 𝓝 (0 : ℝ),
      AEStronglyMeasurable (fun ω => A ω * L e ω) μ)
    (hbase : ∀ᵐ ω ∂μ, L 0 ω = 1)
    (hAint : Integrable A μ)
    (hASmeas : AEStronglyMeasurable (fun ω => A ω * S ω) μ)
    (hlip : ∀ᵐ ω ∂μ, LipschitzOnWith (Real.nnabs (bound ω))
      (fun e => A ω * L e ω) (Metric.ball (0 : ℝ) δ))
    (hbound : Integrable bound μ)
    (hderiv : ∀ᵐ ω ∂μ, HasDerivAt (fun e => L e ω) (-S ω) 0)
    (hρ : 0 ≤ ρ) (hΓ : 1 < ∫ ω, A ω * S ω ∂μ)
    (hlt : ρ < Priority3Map.criticalRho (∫ ω, A ω * S ω ∂μ)) :
    HasDerivAt (fun e : ℝ => ρ * (e + ∫ ω, A ω * L e ω ∂μ))
        (Priority3Map.multiplier ρ (∫ ω, A ω * S ω ∂μ)) 0
      ∧ Priority3Map.LocallyAttracting ρ (∫ ω, A ω * S ω ∂μ) :=
  ⟨reuse_derivative ρ hδ hmeas hbase hAint hASmeas hlip hbound hderiv,
   (Priority3Map.attracting_iff_lt_criticalRho hρ hΓ).mpr hlt⟩

/-- The same bridge on the repelling side. -/
theorem general_repelling_of_criticalRho_lt
    {A S : Ω → ℝ} {L : ℝ → Ω → ℝ} {bound : Ω → ℝ} {δ ρ : ℝ}
    (hδ : 0 < δ)
    (hmeas : ∀ᶠ e in 𝓝 (0 : ℝ),
      AEStronglyMeasurable (fun ω => A ω * L e ω) μ)
    (hbase : ∀ᵐ ω ∂μ, L 0 ω = 1)
    (hAint : Integrable A μ)
    (hASmeas : AEStronglyMeasurable (fun ω => A ω * S ω) μ)
    (hlip : ∀ᵐ ω ∂μ, LipschitzOnWith (Real.nnabs (bound ω))
      (fun e => A ω * L e ω) (Metric.ball (0 : ℝ) δ))
    (hbound : Integrable bound μ)
    (hderiv : ∀ᵐ ω ∂μ, HasDerivAt (fun e => L e ω) (-S ω) 0)
    (hρ : 0 ≤ ρ) (hΓ : 1 < ∫ ω, A ω * S ω ∂μ)
    (hgt : Priority3Map.criticalRho (∫ ω, A ω * S ω ∂μ) < ρ) :
    HasDerivAt (fun e : ℝ => ρ * (e + ∫ ω, A ω * L e ω ∂μ))
        (Priority3Map.multiplier ρ (∫ ω, A ω * S ω ∂μ)) 0
      ∧ Priority3Map.LocallyRepelling ρ (∫ ω, A ω * S ω ∂μ) :=
  ⟨reuse_derivative ρ hδ hmeas hbase hAint hASmeas hlip hbound hderiv,
   (Priority3Map.repelling_iff_criticalRho_lt hρ hΓ).mpr hgt⟩

end RebaseguardLean.Level4Priority4
