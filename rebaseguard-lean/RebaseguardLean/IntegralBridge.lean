import RebaseguardLean.StoppedLikelihood

/-!
# Gate 3: differentiation under the integral sign

This file bridges the Gate 2 *pointwise* derivative identity
(`stoppedIntegrand_hasDerivAt`) to a derivative identity for the
*integrated* likelihood, at the parameter value `e = 0`.

The mathematical target is

  d/de ∫ Zτ ω * exp (-e * Tτ ω - (e^2/2) * τ ω) dμ(ω) |_{e = 0}
    = - ∫ Zτ ω * Tτ ω dμ(ω).

The domination hypothesis is kept as an **explicit assumption**: an integrable
`g` bounding the pointwise derivative uniformly for `e` in a closed interval
`[-δ, δ]` around zero.  Discharging it for the CUSUM setting is Gate 4.
-/

noncomputable section

open MeasureTheory Filter Set
open scoped Topology

namespace RebaseguardLean

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

/-- The parameterized integrand `e ↦ ω ↦ Zτ ω * exp (-e * Tτ ω - (e^2/2) * τ ω)`,
expressed through the Gate 2 definition. -/
def paramIntegrand (Zτ Tτ τ : Ω → ℝ) (e : ℝ) (ω : Ω) : ℝ :=
  stoppedIntegrand (Zτ ω) (Tτ ω) (τ ω) e

/-- The pointwise (in `ω`) derivative of `paramIntegrand` with respect to `e`,
expressed through the Gate 2 definition. -/
def paramIntegrandDeriv (Zτ Tτ τ : Ω → ℝ) (e : ℝ) (ω : Ω) : ℝ :=
  stoppedIntegrandDeriv (Zτ ω) (Tτ ω) (τ ω) e


/-! ### Pointwise values at `e = 0` -/

omit [MeasurableSpace Ω] in
lemma paramIntegrand_zero (Zτ Tτ τ : Ω → ℝ) (ω : Ω) :
    paramIntegrand Zτ Tτ τ 0 ω = Zτ ω := by
  unfold paramIntegrand stoppedIntegrand
  norm_num

omit [MeasurableSpace Ω] in
lemma paramIntegrandDeriv_zero (Zτ Tτ τ : Ω → ℝ) (ω : Ω) :
    paramIntegrandDeriv Zτ Tτ τ 0 ω = -(Zτ ω * Tτ ω) := by
  unfold paramIntegrandDeriv stoppedIntegrandDeriv
  norm_num


/-! ### Measurability of the integrand and of its derivative -/

lemma aestronglyMeasurable_paramIntegrand
    {Zτ Tτ τ : Ω → ℝ}
    (hZ : AEStronglyMeasurable Zτ μ)
    (hT : AEStronglyMeasurable Tτ μ)
    (hτ : AEStronglyMeasurable τ μ)
    (e : ℝ) :
    AEStronglyMeasurable (paramIntegrand Zτ Tτ τ e) μ := by
  unfold paramIntegrand stoppedIntegrand
  exact hZ.mul (Real.continuous_exp.comp_aestronglyMeasurable
    ((hT.const_mul (-e)).sub (hτ.const_mul (e ^ 2 / 2))))

lemma aestronglyMeasurable_paramIntegrandDeriv
    {Zτ Tτ τ : Ω → ℝ}
    (hZ : AEStronglyMeasurable Zτ μ)
    (hT : AEStronglyMeasurable Tτ μ)
    (hτ : AEStronglyMeasurable τ μ)
    (e : ℝ) :
    AEStronglyMeasurable (paramIntegrandDeriv Zτ Tτ τ e) μ := by
  unfold paramIntegrandDeriv stoppedIntegrandDeriv
  exact (hZ.mul (hT.add (hτ.const_mul e)).neg).mul
    (Real.continuous_exp.comp_aestronglyMeasurable
      ((hT.const_mul (-e)).sub (hτ.const_mul (e ^ 2 / 2))))


/-! ### The Gate 3 bridge -/

/-- **Gate 3.**  Differentiation under the integral sign for the stopped
likelihood at `e = 0`.

Assumptions:
* `Zτ`, `Tτ`, `τ` are a.e.-strongly-measurable;
* `Zτ` is integrable (this is the value of the integrand at `e = 0`);
* `δ > 0` gives a neighborhood `[-δ, δ]` of `0`;
* `g` is integrable and dominates the pointwise `e`-derivative uniformly on
  `[-δ, δ]`, almost everywhere.

Conclusion: the parameterized integral is differentiable at `0` with derivative
`- ∫ Zτ ω * Tτ ω ∂μ`. -/
theorem hasDerivAt_integral_stoppedIntegrand_zero
    {Zτ Tτ τ : Ω → ℝ}
    (hZmeas : AEStronglyMeasurable Zτ μ)
    (hTmeas : AEStronglyMeasurable Tτ μ)
    (hτmeas : AEStronglyMeasurable τ μ)
    (hZint : Integrable Zτ μ)
    {δ : ℝ} (hδ : 0 < δ)
    {g : Ω → ℝ} (hgint : Integrable g μ)
    (hdom : ∀ᵐ ω ∂μ, ∀ e ∈ Set.Icc (-δ) δ,
      ‖paramIntegrandDeriv Zτ Tτ τ e ω‖ ≤ g ω) :
    HasDerivAt
      (fun e : ℝ => ∫ ω, Zτ ω * Real.exp (-e * Tτ ω - (e ^ 2 / 2) * τ ω) ∂μ)
      (- ∫ ω, Zτ ω * Tτ ω ∂μ)
      0 := by
  have hs : Set.Ioo (-δ) δ ∈ 𝓝 (0 : ℝ) := Ioo_mem_nhds (by linarith) hδ
  have hF_meas : ∀ᶠ x in 𝓝 (0 : ℝ),
      AEStronglyMeasurable (paramIntegrand Zτ Tτ τ x) μ :=
    Filter.Eventually.of_forall fun x =>
      aestronglyMeasurable_paramIntegrand hZmeas hTmeas hτmeas x
  have hF_int : Integrable (paramIntegrand Zτ Tτ τ 0) μ :=
    hZint.congr (Filter.Eventually.of_forall fun ω =>
      (paramIntegrand_zero Zτ Tτ τ ω).symm)
  have hF'_meas : AEStronglyMeasurable (paramIntegrandDeriv Zτ Tτ τ 0) μ :=
    aestronglyMeasurable_paramIntegrandDeriv hZmeas hTmeas hτmeas 0
  have h_bound : ∀ᵐ ω ∂μ, ∀ x ∈ Set.Ioo (-δ) δ,
      ‖paramIntegrandDeriv Zτ Tτ τ x ω‖ ≤ g ω := by
    filter_upwards [hdom] with ω hω x hx
    exact hω x (Set.Ioo_subset_Icc_self hx)
  have h_diff : ∀ᵐ ω ∂μ, ∀ x ∈ Set.Ioo (-δ) δ,
      HasDerivAt (fun e : ℝ => paramIntegrand Zτ Tτ τ e ω)
        (paramIntegrandDeriv Zτ Tτ τ x ω) x :=
    Filter.Eventually.of_forall fun ω x _ =>
      stoppedIntegrand_hasDerivAt (Zτ ω) (Tτ ω) (τ ω) x
  obtain ⟨-, key⟩ :=
    hasDerivAt_integral_of_dominated_loc_of_deriv_le
      (F := paramIntegrand Zτ Tτ τ) (bound := g)
      (F' := paramIntegrandDeriv Zτ Tτ τ)
      hs hF_meas hF_int hF'_meas h_bound hgint h_diff
  have hval : (∫ ω, paramIntegrandDeriv Zτ Tτ τ 0 ω ∂μ)
      = - ∫ ω, Zτ ω * Tτ ω ∂μ := by
    have hrw : (∫ ω, paramIntegrandDeriv Zτ Tτ τ 0 ω ∂μ)
        = ∫ ω, -(Zτ ω * Tτ ω) ∂μ := by
      simp only [paramIntegrandDeriv_zero]
    rw [hrw, integral_neg]
  rw [hval] at key
  exact key

end RebaseguardLean
