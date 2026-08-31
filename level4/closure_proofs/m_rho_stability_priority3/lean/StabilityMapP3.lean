import MGtOneClosure
import SRPriority2

/-!
# Level-4 Priority 3: generic stability-map spine

Priority 3 is a synthesis layer.  It does not restate the Priority-1 or
Priority-2 derivative theorems; it *imports* their closed Lean spines and
formalizes only the generic map logic that turns the shared identity

`F'_{rho,m}(0) = rho * (1 - Gamma)`

into an attraction/repulsion/boundary classification with an explicit critical
reuse fraction, an admissible-domain intersection, and an interval-robustness
criterion.

Everything proved here is first order and local.  Nothing in this file asserts
global stability, nonlinear convergence, or uniqueness of a stationary law.
-/

noncomputable section

open MeasureTheory Set

namespace RebaseguardLean.Priority3Map

variable {ρ Γ Γlo Γhi : ℝ}

/-- The local multiplier supplied by both closed derivative theorems. -/
def multiplier (ρ Γ : ℝ) : ℝ := ρ * (1 - Γ)

/-- Distance of the gain from the neutral value one. -/
def gainDistance (Γ : ℝ) : ℝ := |1 - Γ|

def LocallyAttracting (ρ Γ : ℝ) : Prop := |multiplier ρ Γ| < 1
def LocallyRepelling (ρ Γ : ℝ) : Prop := 1 < |multiplier ρ Γ|
def FirstOrderBoundary (ρ Γ : ℝ) : Prop := |multiplier ρ Γ| = 1

/-- The Priority-3 predicates are definitionally the Priority-1 predicates. -/
theorem attracting_iff_priority1 :
    LocallyAttracting ρ Γ ↔ Level4Priority1.linearlyAttracting ρ Γ := Iff.rfl

theorem repelling_iff_priority1 :
    LocallyRepelling ρ Γ ↔ Level4Priority1.linearlyRepelling ρ Γ := Iff.rfl

/-- The Priority-3 predicates are definitionally the Priority-2 predicates. -/
theorem attracting_iff_priority2 :
    LocallyAttracting ρ Γ ↔ SRPriority2.linearlyAttracting ρ Γ := Iff.rfl

theorem repelling_iff_priority2 :
    LocallyRepelling ρ Γ ↔ SRPriority2.linearlyRepelling ρ Γ := Iff.rfl

theorem abs_multiplier (hρ : 0 ≤ ρ) :
    |multiplier ρ Γ| = ρ * gainDistance Γ := by
  rw [multiplier, gainDistance, abs_mul, abs_of_nonneg hρ]

/-- On the admissible domain the multiplier magnitude is strictly increasing in
the reuse fraction whenever the gain is not neutral. -/
theorem abs_multiplier_strictMonoOn (hΓ : Γ ≠ 1) :
    StrictMonoOn (fun r : ℝ => |multiplier r Γ|) (Ici 0) := by
  have hpos : 0 < gainDistance Γ := by
    have : (1 : ℝ) - Γ ≠ 0 := sub_ne_zero.mpr (Ne.symm hΓ)
    simpa [gainDistance] using abs_pos.mpr this
  intro a ha b hb hab
  simp only [abs_multiplier ha, abs_multiplier hb]
  exact mul_lt_mul_of_pos_right hab hpos

/-- Pure fresh estimation has multiplier zero and is therefore attracting.  This
is a consequence of the same criterion, not a separate convention. -/
theorem zero_attracting : LocallyAttracting 0 Γ := by
  simp [LocallyAttracting, multiplier]

/-- The critical reuse fraction in the regime the campaign actually measures. -/
def criticalRho (Γ : ℝ) : ℝ := 1 / (Γ - 1)

theorem criticalRho_pos (hΓ : 1 < Γ) : 0 < criticalRho Γ :=
  div_pos one_pos (sub_pos.mpr hΓ)

theorem gainDistance_of_one_lt (hΓ : 1 < Γ) : gainDistance Γ = Γ - 1 := by
  have : (1 : ℝ) - Γ ≤ 0 := by linarith
  rw [gainDistance, abs_of_nonpos this]; ring

/-- Exact boundary identity: at the critical reuse fraction the magnitude of the
multiplier is exactly one. -/
theorem boundary_at_criticalRho (hΓ : 1 < Γ) :
    FirstOrderBoundary (criticalRho Γ) Γ := by
  have hpos : 0 < Γ - 1 := sub_pos.mpr hΓ
  have hρ : 0 ≤ criticalRho Γ := le_of_lt (criticalRho_pos hΓ)
  rw [FirstOrderBoundary, abs_multiplier hρ, gainDistance_of_one_lt hΓ,
    criticalRho, one_div, inv_mul_cancel₀ (ne_of_gt hpos)]

/-- Attraction criterion in critical-reuse form. -/
theorem attracting_iff_lt_criticalRho (hρ : 0 ≤ ρ) (hΓ : 1 < Γ) :
    LocallyAttracting ρ Γ ↔ ρ < criticalRho Γ := by
  have hpos : 0 < Γ - 1 := sub_pos.mpr hΓ
  rw [LocallyAttracting, abs_multiplier hρ, gainDistance_of_one_lt hΓ,
    criticalRho]
  constructor
  · intro h; exact (lt_div_iff₀ hpos).mpr (by linarith)
  · intro h; have := (lt_div_iff₀ hpos).mp h; linarith

/-- Repulsion criterion in critical-reuse form. -/
theorem repelling_iff_criticalRho_lt (hρ : 0 ≤ ρ) (hΓ : 1 < Γ) :
    LocallyRepelling ρ Γ ↔ criticalRho Γ < ρ := by
  have hpos : 0 < Γ - 1 := sub_pos.mpr hΓ
  rw [LocallyRepelling, abs_multiplier hρ, gainDistance_of_one_lt hΓ,
    criticalRho]
  constructor
  · intro h; exact (div_lt_iff₀ hpos).mpr (by linarith)
  · intro h; have := (div_lt_iff₀ hpos).mp h; linarith

/-- The three cases are exhaustive and mutually exclusive on the admissible
domain: linearization is silent exactly on the boundary. -/
theorem trichotomy (ρ Γ : ℝ) :
    LocallyAttracting ρ Γ ∨ FirstOrderBoundary ρ Γ ∨ LocallyRepelling ρ Γ := by
  rcases lt_trichotomy |multiplier ρ Γ| 1 with h | h | h
  · exact Or.inl h
  · exact Or.inr (Or.inl h)
  · exact Or.inr (Or.inr h)

/-- Admissible-domain intersection: the boundary is reachable with a reuse
fraction in `[0,1]` exactly when the gain is at least two. -/
theorem criticalRho_le_one_iff (hΓ : 1 < Γ) : criticalRho Γ ≤ 1 ↔ 2 ≤ Γ := by
  have hpos : 0 < Γ - 1 := sub_pos.mpr hΓ
  rw [criticalRho, div_le_one hpos]
  constructor <;> intro h <;> linarith

/-- If the gain lies in `[0,2]`, every reuse fraction strictly below full reuse
is locally attracting, so no boundary is accessible in the open domain. -/
theorem attracting_of_gain_le_two (h0 : 0 ≤ Γ) (h2 : Γ ≤ 2)
    (hρ : 0 ≤ ρ) (hlt : ρ < 1) : LocallyAttracting ρ Γ := by
  have hd : gainDistance Γ ≤ 1 := by
    rw [gainDistance, abs_le]; constructor <;> linarith
  rw [LocallyAttracting, abs_multiplier hρ]
  calc ρ * gainDistance Γ ≤ ρ * 1 := by
        exact mul_le_mul_of_nonneg_left hd hρ
    _ = ρ := mul_one ρ
    _ < 1 := hlt

/-- The neutral gain gives a multiplier that vanishes identically, so the whole
admissible domain is attracting and no critical reuse fraction exists. -/
theorem attracting_of_gain_eq_one (hΓ : Γ = 1) : LocallyAttracting ρ Γ := by
  simp [LocallyAttracting, multiplier, hΓ]

/-- Every gain strictly between zero and two remains attracting even at full
reuse.  The endpoints are excluded because they are first-order boundaries. -/
theorem full_reuse_attracting_of_gain_between_zero_two
    (h0 : 0 < Γ) (h2 : Γ < 2) : LocallyAttracting 1 Γ := by
  rw [LocallyAttracting, multiplier, one_mul, abs_lt]
  constructor <;> linarith

/-- At full reuse, gains zero and two are the two endpoint boundary cases. -/
theorem full_reuse_boundary_of_gain_eq_zero_or_two
    (hΓ : Γ = 0 ∨ Γ = 2) : FirstOrderBoundary 1 Γ := by
  rcases hΓ with rfl | rfl <;> norm_num [FirstOrderBoundary, multiplier]

theorem gainDistance_le_max (hlo : Γlo ≤ Γ) (hhi : Γ ≤ Γhi) :
    gainDistance Γ ≤ max (gainDistance Γlo) (gainDistance Γhi) := by
  simp only [gainDistance]
  have hl : |1 - Γlo| ≤ max |1 - Γlo| |1 - Γhi| := le_max_left _ _
  have hr : |1 - Γhi| ≤ max |1 - Γlo| |1 - Γhi| := le_max_right _ _
  have h3 : 1 - Γlo ≤ |1 - Γlo| := le_abs_self _
  have h4 : -(1 - Γhi) ≤ |1 - Γhi| := by
    rw [← abs_neg]; exact le_abs_self _
  rw [abs_le]
  exact ⟨by linarith, by linarith⟩

/-- Interval robustness: when both endpoints of an enclosing gain interval are
attracting at the same reuse fraction, so is every gain inside it.  This is the
formal content of the campaign's rule that a classification may be reported as
robust only when the interval does not straddle unit magnitude. -/
theorem attracting_of_interval (hρ : 0 ≤ ρ)
    (hlo : Γlo ≤ Γ) (hhi : Γ ≤ Γhi)
    (hAlo : ρ * gainDistance Γlo < 1) (hAhi : ρ * gainDistance Γhi < 1) :
    LocallyAttracting ρ Γ := by
  rw [LocallyAttracting, abs_multiplier hρ]
  have hmax := gainDistance_le_max hlo hhi
  have : ρ * gainDistance Γ ≤ ρ * max (gainDistance Γlo) (gainDistance Γhi) :=
    mul_le_mul_of_nonneg_left hmax hρ
  rcases max_cases (gainDistance Γlo) (gainDistance Γhi) with ⟨h, _⟩ | ⟨h, _⟩ <;>
    rw [h] at this
  · exact lt_of_le_of_lt this hAlo
  · exact lt_of_le_of_lt this hAhi

/-- Interval robustness on the repelling side. -/
theorem repelling_of_interval (hρ : 0 ≤ ρ)
    (hlo : Γlo ≤ Γ) (_hhi : Γ ≤ Γhi) (hone : 1 ≤ Γlo)
    (hRlo : 1 < ρ * gainDistance Γlo) : LocallyRepelling ρ Γ := by
  have hΓ : 1 ≤ Γ := hone.trans hlo
  have hdlo : gainDistance Γlo = Γlo - 1 := by
    rw [gainDistance, abs_of_nonpos (by linarith)]; ring
  have hd : gainDistance Γ = Γ - 1 := by
    rw [gainDistance, abs_of_nonpos (by linarith)]; ring
  rw [LocallyRepelling, abs_multiplier hρ, hd]
  rw [hdlo] at hRlo
  have : ρ * (Γlo - 1) ≤ ρ * (Γ - 1) :=
    mul_le_mul_of_nonneg_left (by linarith) hρ
  linarith

/-! ## Bridges to the two closed derivative spines

These are the only places where Priority 3 touches detector-specific material.
Each bridge consumes a closed campaign's derivative theorem verbatim and adds
the generic classification proved above. -/

section Bridges

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

/-- Priority-1 CUSUM bridge: the closed dominated-derivative spine produces the
multiplier, and below the critical reuse fraction that multiplier is
attracting. -/
theorem cusum_attracting_of_lt_criticalRho
    {A T τR : Ω → ℝ}
    (hAmeas : AEStronglyMeasurable A μ) (hTmeas : AEStronglyMeasurable T μ)
    (hτmeas : AEStronglyMeasurable τR μ) (hAint : Integrable A μ)
    {δ : ℝ} (hδ : 0 < δ) {g : Ω → ℝ} (hgint : Integrable g μ)
    (hdom : ∀ᵐ ω ∂μ, ∀ e ∈ Set.Icc (-δ) δ,
      ‖paramIntegrandDeriv A T τR e ω‖ ≤ g ω)
    (hρ : 0 ≤ ρ) (hΓ : 1 < ∫ ω, A ω * T ω ∂μ)
    (hlt : ρ < criticalRho (∫ ω, A ω * T ω ∂μ)) :
    HasDerivAt
      (fun e : ℝ => ρ * (e + ∫ ω, A ω *
        Real.exp (-e * T ω - (e ^ 2 / 2) * τR ω) ∂μ))
      (multiplier ρ (∫ ω, A ω * T ω ∂μ)) 0
    ∧ LocallyAttracting ρ (∫ ω, A ω * T ω ∂μ) :=
  ⟨Level4Priority1.derivative_spine_of_dominated hAmeas hTmeas hτmeas hAint
      hδ hgint hdom ρ,
   (attracting_iff_lt_criticalRho hρ hΓ).mpr hlt⟩

/-- Priority-2 SR bridge, with the same generic classification. -/
theorem sr_repelling_of_criticalRho_lt
    {Awin T τR : Ω → ℝ}
    (hAmeas : AEStronglyMeasurable Awin μ) (hTmeas : AEStronglyMeasurable T μ)
    (hτmeas : AEStronglyMeasurable τR μ) (hAint : Integrable Awin μ)
    {δ : ℝ} (hδ : 0 < δ) {g : Ω → ℝ} (hgint : Integrable g μ)
    (hdom : ∀ᵐ ω ∂μ, ∀ e ∈ Set.Icc (-δ) δ,
      ‖paramIntegrandDeriv Awin T τR e ω‖ ≤ g ω)
    (hρ : 0 ≤ ρ) (hΓ : 1 < ∫ ω, Awin ω * T ω ∂μ)
    (hgt : criticalRho (∫ ω, Awin ω * T ω ∂μ) < ρ) :
    HasDerivAt
      (fun e : ℝ => ρ * (e + ∫ ω, Awin ω *
        Real.exp (-e * T ω - (e ^ 2 / 2) * τR ω) ∂μ))
      (multiplier ρ (∫ ω, Awin ω * T ω ∂μ)) 0
    ∧ LocallyRepelling ρ (∫ ω, Awin ω * T ω ∂μ) :=
  ⟨SRPriority2.derivative_spine_of_dominated hAmeas hTmeas hτmeas hAint
      hδ hgint hdom ρ,
   (repelling_iff_criticalRho_lt hρ hΓ).mpr hgt⟩

end Bridges

end RebaseguardLean.Priority3Map
