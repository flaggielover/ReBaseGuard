import RebaseguardLean.IntegralBridge

/-!
# Proof Track 3B: general location-family stopped-score spine

This file formalizes the reusable algebraic and conditional stopped-score
consequences.  It does not construct the concrete infinite t3 CUSUM process or
discharge its stopped change-of-measure, a.s.-finiteness, tail, measurability,
integrability, and domination obligations.
-/

noncomputable section

open MeasureTheory

namespace RebaseguardLean.LocationFamilyTrack3AB

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

/-- Conventional stopped location-score sum `sum psi(Z_t)`. -/
def conventionalScoreSum (ψ : ℝ → ℝ) (path : List ℝ) : ℝ :=
  (path.map ψ).sum

/-- Parameter-score sum for the convention `Z=epsilon-e`, hence `s=-psi`. -/
def parameterScoreSum (ψ : ℝ → ℝ) (path : List ℝ) : ℝ :=
  (path.map fun z => -ψ z).sum

theorem parameterScoreSum_eq_neg_conventional
    (ψ : ℝ → ℝ) (path : List ℝ) :
    parameterScoreSum ψ path = -conventionalScoreSum ψ path := by
  induction path with
  | nil => simp [parameterScoreSum, conventionalScoreSum]
  | cons z tail ih =>
      simp only [parameterScoreSum, conventionalScoreSum, List.map_cons,
        List.sum_cons]
      change -ψ z + (tail.map fun x => -ψ x).sum = -(ψ z + (tail.map ψ).sum)
      have htail : (tail.map fun x => -ψ x).sum = -(tail.map ψ).sum := by
        simpa [parameterScoreSum, conventionalScoreSum] using ih
      rw [htail]
      ring

/-- Pointwise raw-terminal stopped gain. -/
def stoppedGain (terminal scoreSum : Ω → ℝ) (ω : Ω) : ℝ :=
  terminal ω * scoreSum ω

/-- The theorem-relevant raw-reuse gain `Gamma_f`. -/
def gamma (terminal scoreSum : Ω → ℝ) (μ : Measure Ω) : ℝ :=
  ∫ ω, stoppedGain terminal scoreSum ω ∂μ

/--
Abstract stopped-score derivative bridge under explicit analytic hypotheses.

The final hypothesis is the stopped differentiation/change-of-measure result.
The measurability and integrability hypotheses make part of its analytic
boundary visible.  Concrete a.s. finiteness, likelihood domination, and the
derivation of `hbridge` remain outside this conditional Lean spine.
-/
theorem stoppedScore_derivative_bridge
    {terminal scoreSum : Ω → ℝ} {terminalMean : ℝ → ℝ}
    (_hterminal : AEStronglyMeasurable terminal μ)
    (_hscore : AEStronglyMeasurable scoreSum μ)
    (_hgain : Integrable (stoppedGain terminal scoreSum) μ)
    (hbridge : HasDerivAt terminalMean (-(gamma terminal scoreSum μ)) 0) :
    HasDerivAt terminalMean (-(gamma terminal scoreSum μ)) 0 := by
  exact hbridge

/-- Frozen affine matched-reuse mean map after integrating the fresh term. -/
def reuseMean (ρ : ℝ) (terminalMean : ℝ → ℝ) : ℝ → ℝ :=
  fun e => ρ * (e + terminalMean e)

theorem reuseMean_apply (ρ : ℝ) (terminalMean : ℝ → ℝ) (e : ℝ) :
    reuseMean ρ terminalMean e = ρ * (e + terminalMean e) := rfl

/-- Exact rho scaling of the local derivative. -/
theorem rho_scaling
    {terminalMean : ℝ → ℝ} {Γ ρ : ℝ}
    (hmean : HasDerivAt terminalMean (-Γ) 0) :
    HasDerivAt (reuseMean ρ terminalMean) (ρ * (1 - Γ)) 0 := by
  have hsum : HasDerivAt (fun e => e + terminalMean e) (1 + -Γ) 0 :=
    (hasDerivAt_id (x := 0)).add hmean
  change HasDerivAt (fun e => ρ * (e + terminalMean e)) (ρ * (1 - Γ)) 0
  simpa only [sub_eq_add_neg] using hsum.const_mul ρ

/-- Conditional general location-family derivative spine. -/
theorem locationFamily_derivative_spine
    {terminal scoreSum : Ω → ℝ} {terminalMean : ℝ → ℝ}
    (hterminal : AEStronglyMeasurable terminal μ)
    (hscore : AEStronglyMeasurable scoreSum μ)
    (hgain : Integrable (stoppedGain terminal scoreSum) μ)
    (hbridge : HasDerivAt terminalMean (-(gamma terminal scoreSum μ)) 0)
    (ρ : ℝ) :
    HasDerivAt (reuseMean ρ terminalMean)
      (ρ * (1 - gamma terminal scoreSum μ)) 0 := by
  have hmean := stoppedScore_derivative_bridge hterminal hscore hgain hbridge
  exact rho_scaling hmean

/-- Reflection of a finite residual path. -/
def reflectPath (path : List ℝ) : List ℝ :=
  path.map fun z => -z

@[simp] theorem reflectPath_involutive (path : List ℝ) :
    reflectPath (reflectPath path) = path := by
  simp [reflectPath, List.map_map]

/-- An odd location score makes its stopped finite-path sum odd. -/
theorem conventionalScoreSum_reflection
    {ψ : ℝ → ℝ} (hψ : Function.Odd ψ) (path : List ℝ) :
    conventionalScoreSum ψ (reflectPath path) =
      -conventionalScoreSum ψ path := by
  induction path with
  | nil => simp [conventionalScoreSum, reflectPath]
  | cons z tail ih =>
      simp only [conventionalScoreSum, reflectPath, List.map_cons, List.sum_cons]
      rw [hψ z]
      have htail : (List.map ψ (List.map (fun x => -x) tail)).sum =
          -(List.map ψ tail).sum := by
        simpa [conventionalScoreSum, reflectPath, List.map_map,
          Function.comp_def] using ih
      rw [htail]
      ring

/-- Reflection preserves the product of two odd stopped quantities. -/
theorem reflected_stopped_gain (terminal scoreSum : ℝ) :
    (-terminal) * (-scoreSum) = terminal * scoreSum := by
  ring

/-- Reflection-equivariant terminal means give an odd matched-reuse map. -/
theorem reuseMean_odd
    {terminalMean : ℝ → ℝ} (hodd : Function.Odd terminalMean) (ρ : ℝ) :
    Function.Odd (reuseMean ρ terminalMean) := by
  intro e
  simp only [reuseMean]
  rw [hodd]
  ring

/-- The conventional standard-Gaussian location score. -/
def gaussianScore (z : ℝ) : ℝ := z

theorem gaussian_score_specialization (z : ℝ) : gaussianScore z = z := rfl

theorem gaussian_score_sum_specialization (path : List ℝ) :
    conventionalScoreSum gaussianScore path = path.sum := by
  change (path.map fun z : ℝ => z).sum = path.sum
  simp

/-- The general gain becomes `Z_tau T_tau` for the Gaussian score. -/
theorem gaussian_gain_specialization (terminal total : ℝ) :
    terminal * gaussianScore total = terminal * total := by
  rfl

/-- General sign-reversing local-instability inequality for positive rho. -/
theorem gamma_threshold_derivative_lt_neg_one
    {Γ ρ : ℝ} (hρ : 0 < ρ) (hΓ : 1 + 1 / ρ < Γ) :
    ρ * (1 - Γ) < -1 := by
  have hρne : ρ ≠ 0 := ne_of_gt hρ
  have hmul : ρ * (1 + 1 / ρ) < ρ * Γ :=
    mul_lt_mul_of_pos_left hΓ hρ
  have hinv : ρ * (1 / ρ) = 1 := by
    field_simp
  rw [mul_add, mul_one, hinv] at hmul
  nlinarith

/-- Full-reuse specialization: `Gamma_f > 2` forces derivative below `-1`. -/
theorem gamma_gt_two_full_reuse_derivative_lt_neg_one
    {Γ : ℝ} (hΓ : 2 < Γ) :
    (1 : ℝ) * (1 - Γ) < -1 := by
  norm_num
  linarith

/-- Raw terminal-observation gain used by actual matched `m=1` reuse. -/
def rawTerminalGain (z stoppedScore : ℝ) : ℝ := z * stoppedScore

/-- Terminal-score-only gain used by the distinct historical Stage-D rule. -/
def terminalScoreGain (ψz stoppedScore : ℝ) : ℝ := ψz * stoppedScore

/-- Outside terminal equality, the two gains differ when the stopped sum is nonzero. -/
theorem raw_gain_ne_terminal_score_gain
    {z ψz stoppedScore : ℝ} (hz : z ≠ ψz) (hscore : stoppedScore ≠ 0) :
    rawTerminalGain z stoppedScore ≠ terminalScoreGain ψz stoppedScore := by
  intro heq
  apply hz
  apply mul_right_cancel₀ hscore
  exact heq

/-- Gaussian terminal-score equality collapses the historical distinction. -/
theorem gaussian_terminal_gain_eq_raw (z stoppedScore : ℝ) :
    terminalScoreGain (gaussianScore z) stoppedScore =
      rawTerminalGain z stoppedScore := by
  rfl

end RebaseguardLean.LocationFamilyTrack3AB
