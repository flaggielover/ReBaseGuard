import RebaseguardLean.IntegralBridge

/-!
# Level-4 Priority 1: independent truncated-window derivative proof spine

The file formalizes the high-value algebra and consumes the existing generic
dominated stopped-integral bridge. It does not construct the frozen CUSUM
probability space or prove its concrete stopped exponential-moment bound.
-/

noncomputable section

open MeasureTheory Filter Set
open scoped Topology

namespace RebaseguardLean.Level4Priority1

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

def windowLength (m τ : ℕ) : ℕ := min m τ

def directTerm (m τ : ℕ) (S T : ℝ) : ℝ :=
  S / (windowLength m τ : ℝ) * T

def fixedTerm (m : ℕ) (S T : ℝ) : ℝ := S / (m : ℝ) * T

def shortCorrection (m τ : ℕ) (T : ℝ) : ℝ :=
  if τ < m then (1 / (τ : ℝ) - 1 / (m : ℝ)) * T ^ 2 else 0

theorem windowLength_eq_tau_of_short {m τ : ℕ} (h : τ < m) :
    windowLength m τ = τ := by
  exact Nat.min_eq_right (Nat.le_of_lt h)

theorem windowLength_eq_m_of_full {m τ : ℕ} (h : m ≤ τ) :
    windowLength m τ = m := by
  exact Nat.min_eq_left h

theorem directTerm_short {m τ : ℕ} {S T : ℝ}
    (hshort : τ < m) (hwhole : S = T) :
    directTerm m τ S T = T / (τ : ℝ) * T := by
  simp [directTerm, windowLength_eq_tau_of_short hshort, hwhole]

theorem directTerm_full {m τ : ℕ} {S T : ℝ} (hfull : m ≤ τ) :
    directTerm m τ S T = fixedTerm m S T := by
  simp [directTerm, fixedTerm, windowLength_eq_m_of_full hfull]

theorem direct_eq_fixed_add_short {m τ : ℕ} {S T : ℝ}
    (hwhole : τ < m → S = T) :
    directTerm m τ S T = fixedTerm m S T + shortCorrection m τ T := by
  by_cases hshort : τ < m
  · have hS : S = T := hwhole hshort
    simp [directTerm, fixedTerm, shortCorrection,
      windowLength_eq_tau_of_short hshort, hshort, hS]
    ring
  · have hfull : m ≤ τ := Nat.le_of_not_gt hshort
    simp [directTerm, fixedTerm, shortCorrection,
      windowLength_eq_m_of_full hfull, hshort]

theorem shortCorrection_nonneg {m τ : ℕ} {T : ℝ}
    (_hm : 0 < m) (hτ : 0 < τ) : 0 ≤ shortCorrection m τ T := by
  by_cases hshort : τ < m
  · have hτr : 0 < (τ : ℝ) := by exact_mod_cast hτ
    have hτm : (τ : ℝ) ≤ (m : ℝ) := by exact_mod_cast Nat.le_of_lt hshort
    have hinv : 1 / (m : ℝ) ≤ 1 / (τ : ℝ) :=
      one_div_le_one_div_of_le hτr hτm
    have hdiff : 0 ≤ 1 / (τ : ℝ) - 1 / (m : ℝ) := sub_nonneg.mpr hinv
    simp only [shortCorrection, hshort, ite_true]
    exact mul_nonneg hdiff (sq_nonneg T)
  · simp [shortCorrection, hshort]

theorem windowLength_one {τ : ℕ} (hτ : 0 < τ) : windowLength 1 τ = 1 := by
  exact Nat.min_eq_left hτ

theorem directTerm_one {τ : ℕ} {S T : ℝ} (hτ : 0 < τ) :
    directTerm 1 τ S T = S * T := by
  simp [directTerm, windowLength_one hτ]

theorem shortCorrection_one {τ : ℕ} {T : ℝ} (hτ : 0 < τ) :
    shortCorrection 1 τ T = 0 := by
  have hnot : ¬ τ < 1 := Nat.not_lt_of_ge hτ
  simp [shortCorrection, hnot]

theorem integral_direct_eq_fixed_add_short
    {m : ℕ} {τ : Ω → ℕ} {S T : Ω → ℝ}
    (hwhole : ∀ ω, τ ω < m → S ω = T ω)
    (hfixed : Integrable (fun ω => fixedTerm m (S ω) (T ω)) μ)
    (hshort : Integrable (fun ω => shortCorrection m (τ ω) (T ω)) μ) :
    (∫ ω, directTerm m (τ ω) (S ω) (T ω) ∂μ) =
      (∫ ω, fixedTerm m (S ω) (T ω) ∂μ) +
      ∫ ω, shortCorrection m (τ ω) (T ω) ∂μ := by
  calc
    (∫ ω, directTerm m (τ ω) (S ω) (T ω) ∂μ) =
        ∫ ω, (fixedTerm m (S ω) (T ω) +
          shortCorrection m (τ ω) (T ω)) ∂μ := by
            apply integral_congr_ae
            exact Filter.Eventually.of_forall fun ω => direct_eq_fixed_add_short (hwhole ω)
    _ = (∫ ω, fixedTerm m (S ω) (T ω) ∂μ) +
        ∫ ω, shortCorrection m (τ ω) (T ω) ∂μ := integral_add hfixed hshort

theorem rho_derivative_of_expectation_derivative
    {I : ℝ → ℝ} {Γ ρ : ℝ} (hI : HasDerivAt I (-Γ) 0) :
    HasDerivAt (fun e => ρ * (e + I e)) (ρ * (1 - Γ)) 0 := by
  have hsum : HasDerivAt (fun e => e + I e) (1 + -Γ) 0 :=
    (hasDerivAt_id (x := 0)).add hI
  simpa [sub_eq_add_neg] using hsum.const_mul ρ

theorem derivative_spine_of_dominated
    {A T τR : Ω → ℝ}
    (hAmeas : AEStronglyMeasurable A μ)
    (hTmeas : AEStronglyMeasurable T μ)
    (hτmeas : AEStronglyMeasurable τR μ)
    (hAint : Integrable A μ)
    {δ : ℝ} (hδ : 0 < δ)
    {g : Ω → ℝ} (hgint : Integrable g μ)
    (hdom : ∀ᵐ ω ∂μ, ∀ e ∈ Set.Icc (-δ) δ,
      ‖paramIntegrandDeriv A T τR e ω‖ ≤ g ω)
    (ρ : ℝ) :
    HasDerivAt
      (fun e : ℝ => ρ * (e + ∫ ω, A ω *
        Real.exp (-e * T ω - (e ^ 2 / 2) * τR ω) ∂μ))
      (ρ * (1 - ∫ ω, A ω * T ω ∂μ)) 0 := by
  have hI := hasDerivAt_integral_stoppedIntegrand_zero
    hAmeas hTmeas hτmeas hAint hδ hgint hdom
  exact rho_derivative_of_expectation_derivative hI

def linearlyAttracting (ρ Γ : ℝ) : Prop := |ρ * (1 - Γ)| < 1

def linearlyRepelling (ρ Γ : ℝ) : Prop := 1 < |ρ * (1 - Γ)|

theorem attraction_from_derivative_bound {ρ Γ : ℝ}
    (h : |ρ * (1 - Γ)| < 1) : linearlyAttracting ρ Γ := h

theorem repulsion_from_derivative_bound {ρ Γ : ℝ}
    (h : 1 < |ρ * (1 - Γ)|) : linearlyRepelling ρ Γ := h

theorem multiplier_abs_of_nonneg_of_one_le
    {ρ Γ : ℝ} (hρ : 0 ≤ ρ) (hΓ : 1 ≤ Γ) :
    |ρ * (1 - Γ)| = ρ * (Γ - 1) := by
  rw [abs_mul, abs_of_nonneg hρ]
  have hnonpos : 1 - Γ ≤ 0 := sub_nonpos.mpr hΓ
  rw [abs_of_nonpos hnonpos]
  ring

end RebaseguardLean.Level4Priority1
