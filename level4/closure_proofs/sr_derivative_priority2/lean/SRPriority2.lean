import RebaseguardLean.IntegralBridge

/-!
# Level-4 Priority 2: SR ordinary-window derivative proof spine

This file independently formalizes the finite SR reflection, truncated-window
algebra, and abstract dominated derivative consequence. Concrete Gaussian
tail, measurability, moment, and domination proofs remain human analytic.
-/

noncomputable section

open MeasureTheory Filter Set
open scoped Topology

namespace RebaseguardLean.SRPriority2

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

local instance (p : Prop) : Decidable p := Classical.propDecidable p

@[ext] structure SRState where
  plus : ℝ
  minus : ℝ
deriving DecidableEq

def reset : SRState := ⟨0, 0⟩
def reflectState (s : SRState) : SRState := ⟨s.minus, s.plus⟩

def srStep (s : SRState) (z : ℝ) : SRState :=
  ⟨(1 + s.plus) * Real.exp (z - 1 / 2),
   (1 + s.minus) * Real.exp (-z - 1 / 2)⟩

theorem srStep_reflection (s : SRState) (z : ℝ) :
    srStep (reflectState s) (-z) = reflectState (srStep s z) := by
  ext <;> simp [srStep, reflectState]

def alarmed (A : ℝ) (s : SRState) : Prop := A ≤ max s.plus s.minus

theorem alarmed_reflection (A : ℝ) (s : SRState) :
    alarmed A (reflectState s) ↔ alarmed A s := by
  simp [alarmed, reflectState, max_comm]

structure StoppedRecord where
  time : ℕ
  terminal : ℝ
  total : ℝ
  state : SRState
deriving DecidableEq

def reflectRecord (r : StoppedRecord) : StoppedRecord :=
  ⟨r.time, -r.terminal, -r.total, reflectState r.state⟩

def firstAlarmFrom (A : ℝ) (state : SRState) (total : ℝ) :
    List ℝ → Option StoppedRecord
  | [] => none
  | z :: tail =>
      let next := srStep state z
      let nextTotal := total + z
      if alarmed A next then some ⟨1, z, nextTotal, next⟩
      else
        match firstAlarmFrom A next nextTotal tail with
        | none => none
        | some record => some { record with time := record.time + 1 }

def firstAlarm (A : ℝ) (path : List ℝ) : Option StoppedRecord :=
  firstAlarmFrom A reset 0 path

theorem firstAlarmFrom_reflection (A : ℝ) (path : List ℝ)
    (state : SRState) (total : ℝ) :
    firstAlarmFrom A (reflectState state) (-total) (path.map fun z => -z) =
      (firstAlarmFrom A state total path).map reflectRecord := by
  induction path generalizing state total with
  | nil => simp [firstAlarmFrom]
  | cons z tail ih =>
      simp only [List.map_cons, firstAlarmFrom]
      rw [srStep_reflection]
      have htotal : -total + -z = -(total + z) := by ring
      rw [htotal]
      by_cases h : alarmed A (srStep state z)
      · have hr : alarmed A (reflectState (srStep state z)) :=
          (alarmed_reflection A (srStep state z)).2 h
        simp [h, hr, reflectRecord]
      · have hr : ¬ alarmed A (reflectState (srStep state z)) := by
          intro ha
          exact h ((alarmed_reflection A (srStep state z)).1 ha)
        simp only [h, hr, ↓reduceIte]
        rw [ih (srStep state z) (total + z)]
        cases hrec : firstAlarmFrom A (srStep state z) (total + z) tail with
        | none => simp [hrec]
        | some record => simp [hrec, reflectRecord]

theorem firstAlarm_reflection (A : ℝ) (path : List ℝ) :
    firstAlarm A (path.map fun z => -z) =
      (firstAlarm A path).map reflectRecord := by
  simpa [firstAlarm, reset, reflectState] using
    firstAlarmFrom_reflection A path reset 0

def windowLength (m τ : ℕ) : ℕ := min m τ
def directTerm (m τ : ℕ) (S T : ℝ) : ℝ := S / (windowLength m τ : ℝ) * T
def fixedTerm (m : ℕ) (S T : ℝ) : ℝ := S / (m : ℝ) * T
def shortCorrection (m τ : ℕ) (T : ℝ) : ℝ :=
  if τ < m then (1 / (τ : ℝ) - 1 / (m : ℝ)) * T ^ 2 else 0

theorem direct_eq_fixed_add_short {m τ : ℕ} {S T : ℝ}
    (hwhole : τ < m → S = T) :
    directTerm m τ S T = fixedTerm m S T + shortCorrection m τ T := by
  by_cases hshort : τ < m
  · have hS := hwhole hshort
    have hmin : windowLength m τ = τ := Nat.min_eq_right (Nat.le_of_lt hshort)
    simp [directTerm, fixedTerm, shortCorrection, hshort, hmin, hS]
    ring
  · have hfull : m ≤ τ := Nat.le_of_not_gt hshort
    have hmin : windowLength m τ = m := Nat.min_eq_left hfull
    simp [directTerm, fixedTerm, shortCorrection, hshort, hmin]

theorem shortCorrection_nonneg {m τ : ℕ} {T : ℝ}
    (_hm : 0 < m) (hτ : 0 < τ) : 0 ≤ shortCorrection m τ T := by
  by_cases hshort : τ < m
  · have hτr : 0 < (τ : ℝ) := by exact_mod_cast hτ
    have hτm : (τ : ℝ) ≤ (m : ℝ) := by exact_mod_cast Nat.le_of_lt hshort
    have hinv : 1 / (m : ℝ) ≤ 1 / (τ : ℝ) :=
      one_div_le_one_div_of_le hτr hτm
    simp only [shortCorrection, hshort, ite_true]
    exact mul_nonneg (sub_nonneg.mpr hinv) (sq_nonneg T)
  · simp [shortCorrection, hshort]

theorem integral_decomposition
    {m : ℕ} {τ : Ω → ℕ} {S T : Ω → ℝ}
    (hwhole : ∀ ω, τ ω < m → S ω = T ω)
    (hfixed : Integrable (fun ω => fixedTerm m (S ω) (T ω)) μ)
    (hshort : Integrable (fun ω => shortCorrection m (τ ω) (T ω)) μ) :
    (∫ ω, directTerm m (τ ω) (S ω) (T ω) ∂μ) =
      (∫ ω, fixedTerm m (S ω) (T ω) ∂μ) +
      ∫ ω, shortCorrection m (τ ω) (T ω) ∂μ := by
  calc
    _ = ∫ ω, (fixedTerm m (S ω) (T ω) +
        shortCorrection m (τ ω) (T ω)) ∂μ := by
          apply integral_congr_ae
          exact Filter.Eventually.of_forall fun ω =>
            direct_eq_fixed_add_short (hwhole ω)
    _ = _ := integral_add hfixed hshort

theorem m_one_reduction {τ : ℕ} {S T : ℝ} (hτ : 0 < τ) :
    directTerm 1 τ S T = S * T ∧ shortCorrection 1 τ T = 0 := by
  have hmin : windowLength 1 τ = 1 := Nat.min_eq_left hτ
  have hnshort : ¬ τ < 1 := Nat.not_lt_of_ge hτ
  constructor <;> simp [directTerm, shortCorrection, hmin, hnshort]

theorem derivative_spine_of_dominated
    {Awin T τR : Ω → ℝ}
    (hAmeas : AEStronglyMeasurable Awin μ)
    (hTmeas : AEStronglyMeasurable T μ)
    (hτmeas : AEStronglyMeasurable τR μ)
    (hAint : Integrable Awin μ)
    {δ : ℝ} (hδ : 0 < δ)
    {g : Ω → ℝ} (hgint : Integrable g μ)
    (hdom : ∀ᵐ ω ∂μ, ∀ e ∈ Set.Icc (-δ) δ,
      ‖paramIntegrandDeriv Awin T τR e ω‖ ≤ g ω)
    (ρ : ℝ) :
    HasDerivAt
      (fun e : ℝ => ρ * (e + ∫ ω, Awin ω *
        Real.exp (-e * T ω - (e ^ 2 / 2) * τR ω) ∂μ))
      (ρ * (1 - ∫ ω, Awin ω * T ω ∂μ)) 0 := by
  have hI := hasDerivAt_integral_stoppedIntegrand_zero
    hAmeas hTmeas hτmeas hAint hδ hgint hdom
  have hsum := (hasDerivAt_id (x := 0)).add hI
  simpa [sub_eq_add_neg] using hsum.const_mul ρ

def linearlyAttracting (ρ Γ : ℝ) : Prop := |ρ * (1 - Γ)| < 1
def linearlyRepelling (ρ Γ : ℝ) : Prop := 1 < |ρ * (1 - Γ)|

theorem attraction_criterion {ρ Γ : ℝ} (h : |ρ * (1 - Γ)| < 1) :
    linearlyAttracting ρ Γ := h

theorem repulsion_criterion {ρ Γ : ℝ} (h : 1 < |ρ * (1 - Γ)|) :
    linearlyRepelling ρ Γ := h

end RebaseguardLean.SRPriority2
