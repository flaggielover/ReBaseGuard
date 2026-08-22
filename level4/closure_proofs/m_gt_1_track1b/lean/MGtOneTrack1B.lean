import RebaseguardLean.IntegralBridge

/-!
# Proof Track 1B: the stable `m > 1` algebraic proof spine

This file intentionally formalizes the random-window algebra and the
consequence of the existing dominated stopped-integral derivative interface.
It does not construct the full CUSUM probability space or discharge the
random-window measurability and domination hypotheses.
-/

noncomputable section

open MeasureTheory Filter Set
open scoped Topology

namespace RebaseguardLean.Track1B

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

/-- Realized Stage-D reuse-window length. -/
def windowLength (m τ : ℕ) : ℕ := min m τ

/-- Direct random-denominator gain integrand from a stopped suffix sum `S`. -/
def directTerm (m τ : ℕ) (S T : ℝ) : ℝ :=
  S / (windowLength m τ : ℝ) * T

/-- Fixed-`m` stopped-lag gain integrand. -/
def fixedTerm (m : ℕ) (S T : ℝ) : ℝ :=
  S / (m : ℝ) * T

/-- Exact short-cycle correction integrand. -/
def shortCorrection (m τ : ℕ) (T : ℝ) : ℝ :=
  if τ < m then (1 / (τ : ℝ) - 1 / (m : ℝ)) * T ^ 2 else 0

theorem windowLength_eq_tau_of_lt {m τ : ℕ} (h : τ < m) :
    windowLength m τ = τ := by
  exact Nat.min_eq_right (Nat.le_of_lt h)

theorem windowLength_eq_m_of_le {m τ : ℕ} (h : m ≤ τ) :
    windowLength m τ = m := by
  exact Nat.min_eq_left h

/-- On a short cycle the stopped suffix is the whole path, so `S = T`. -/
theorem directTerm_short {m τ : ℕ} {S T : ℝ}
    (hshort : τ < m) (hwhole : S = T) :
    directTerm m τ S T = T / (τ : ℝ) * T := by
  simp [directTerm, windowLength_eq_tau_of_lt hshort, hwhole]

/-- On a long cycle the random and fixed denominators coincide. -/
theorem directTerm_long {m τ : ℕ} {S T : ℝ} (hlong : m ≤ τ) :
    directTerm m τ S T = fixedTerm m S T := by
  simp [directTerm, fixedTerm, windowLength_eq_m_of_le hlong]

/-- Pointwise Stage-D decomposition, partitioning on `τ < m`. -/
theorem directTerm_eq_fixed_add_shortCorrection {m τ : ℕ} {S T : ℝ}
    (hwhole : τ < m → S = T) :
    directTerm m τ S T = fixedTerm m S T + shortCorrection m τ T := by
  by_cases hshort : τ < m
  · have hS : S = T := hwhole hshort
    simp [directTerm, fixedTerm, shortCorrection,
      windowLength_eq_tau_of_lt hshort, hshort, hS]
    ring
  · have hlong : m ≤ τ := Nat.le_of_not_gt hshort
    simp [directTerm, fixedTerm, shortCorrection,
      windowLength_eq_m_of_le hlong, hshort]

/-- The correction is nonnegative for positive `m` and positive stopping time. -/
theorem shortCorrection_nonneg {m τ : ℕ} {T : ℝ}
    (_hm : 0 < m) (hτ : 0 < τ) : 0 ≤ shortCorrection m τ T := by
  by_cases hshort : τ < m
  · have hτr : 0 < (τ : ℝ) := by exact_mod_cast hτ
    have hτm : (τ : ℝ) ≤ (m : ℝ) := by exact_mod_cast (Nat.le_of_lt hshort)
    have hinv : 1 / (m : ℝ) ≤ 1 / (τ : ℝ) :=
      one_div_le_one_div_of_le hτr hτm
    have hdiff : 0 ≤ 1 / (τ : ℝ) - 1 / (m : ℝ) := sub_nonneg.mpr hinv
    simp only [shortCorrection, hshort, ite_true]
    exact mul_nonneg hdiff (sq_nonneg T)
  · simp [shortCorrection, hshort]

/-- At `m = 1`, every positive stopping time realizes a one-point window. -/
theorem windowLength_one {τ : ℕ} (hτ : 0 < τ) : windowLength 1 τ = 1 := by
  exact Nat.min_eq_left hτ

theorem directTerm_one {τ : ℕ} {S T : ℝ} (hτ : 0 < τ) :
    directTerm 1 τ S T = S * T := by
  simp [directTerm, windowLength_one hτ]

theorem shortCorrection_one {τ : ℕ} {T : ℝ} (hτ : 0 < τ) :
    shortCorrection 1 τ T = 0 := by
  have hnot : ¬ τ < 1 := Nat.not_lt_of_ge hτ
  simp [shortCorrection, hnot]

/-- Expectation-level decomposition from the pointwise identity. -/
theorem integral_direct_eq_fixed_add_correction
    {m : ℕ} {τ : Ω → ℕ} {S T : Ω → ℝ}
    (hwhole : ∀ ω, τ ω < m → S ω = T ω)
    (hfixed : Integrable (fun ω => fixedTerm m (S ω) (T ω)) μ)
    (hcorr : Integrable (fun ω => shortCorrection m (τ ω) (T ω)) μ) :
    (∫ ω, directTerm m (τ ω) (S ω) (T ω) ∂μ) =
      (∫ ω, fixedTerm m (S ω) (T ω) ∂μ) +
      ∫ ω, shortCorrection m (τ ω) (T ω) ∂μ := by
  calc
    (∫ ω, directTerm m (τ ω) (S ω) (T ω) ∂μ) =
        ∫ ω, (fixedTerm m (S ω) (T ω) +
          shortCorrection m (τ ω) (T ω)) ∂μ := by
            apply integral_congr_ae
            exact Filter.Eventually.of_forall fun ω =>
              directTerm_eq_fixed_add_shortCorrection (hwhole ω)
    _ = (∫ ω, fixedTerm m (S ω) (T ω) ∂μ) +
        ∫ ω, shortCorrection m (τ ω) (T ω) ∂μ :=
          integral_add hfixed hcorr

/-- The frozen affine update gives exact rho scaling. -/
def reuseMap (ρ : ℝ) (base : ℝ → ℝ) : ℝ → ℝ := fun e => ρ * base e

theorem reuseMap_apply (ρ : ℝ) (base : ℝ → ℝ) (e : ℝ) :
    reuseMap ρ base e = ρ * base e := rfl

theorem reuseMap_zero (base : ℝ → ℝ) : reuseMap 0 base = fun _ => 0 := by
  funext e
  simp [reuseMap]

theorem reuseMap_one (base : ℝ → ℝ) : reuseMap 1 base = base := by
  funext e
  simp [reuseMap]

/-- Algebraic derivative consequence: identity derivative plus expectation derivative. -/
theorem rho_derivative_of_expectation_derivative
    {I : ℝ → ℝ} {Γ ρ : ℝ}
    (hI : HasDerivAt I (-Γ) 0) :
    HasDerivAt (fun e => ρ * (e + I e)) (ρ * (1 - Γ)) 0 := by
  have hsum : HasDerivAt (fun e => e + I e) (1 + -Γ) 0 :=
    (hasDerivAt_id (x := 0)).add hI
  simpa [sub_eq_add_neg] using hsum.const_mul ρ

/--
Machine-checked reuse of the existing stopped-integral differentiation bridge.

The hypotheses explicitly expose the analytic work: measurability,
integrability at zero, and a uniform integrable dominator for the derivative.
-/
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
      (ρ * (1 - ∫ ω, A ω * T ω ∂μ))
      0 := by
  have hI := hasDerivAt_integral_stoppedIntegrand_zero
    hAmeas hTmeas hτmeas hAint hδ hgint hdom
  exact rho_derivative_of_expectation_derivative hI

end RebaseguardLean.Track1B
