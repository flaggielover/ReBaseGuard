import RebaseguardLean.IntegralBridge

/-!
# Proof Track 2: symmetric two-chart SR derivative spine

This file formalizes finite-path reflection and the conditional algebraic
consequence of the existing stopped-integral differentiation bridge.  It does
not construct the concrete infinite Gaussian SR process or discharge its
measurability, tail, integrability, and domination obligations.
-/

noncomputable section

open MeasureTheory Filter Set
open scoped Topology

namespace RebaseguardLean.SRDerivative

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

local instance (p : Prop) : Decidable p := Classical.propDecidable p

@[ext] structure SRState where
  plus : ℝ
  minus : ℝ
deriving DecidableEq

def reset : SRState := ⟨0, 0⟩

def reflectState (state : SRState) : SRState := ⟨state.minus, state.plus⟩

@[simp] theorem reflectState_involutive (state : SRState) :
    reflectState (reflectState state) = state := by
  cases state
  rfl

/-- Raw two-chart SR update for unit design shift. -/
def srStep (state : SRState) (z : ℝ) : SRState :=
  ⟨(1 + state.plus) * Real.exp (z - 1 / 2),
   (1 + state.minus) * Real.exp (-z - 1 / 2)⟩

theorem srStep_reflection (state : SRState) (z : ℝ) :
    srStep (reflectState state) (-z) = reflectState (srStep state z) := by
  ext <;> simp [srStep, reflectState]

/-- Inclusive post-update two-chart alarm predicate. -/
def alarmed (A : ℝ) (state : SRState) : Prop :=
  A ≤ max state.plus state.minus

theorem alarmed_iff_chart (A : ℝ) (state : SRState) :
    alarmed A state ↔ A ≤ state.plus ∨ A ≤ state.minus := by
  simp [alarmed]

theorem alarmed_reflection (A : ℝ) (state : SRState) :
    alarmed A (reflectState state) ↔ alarmed A state := by
  simp [alarmed, reflectState, max_comm]

theorem alarmed_at_inclusive_plus (A minus : ℝ) :
    alarmed A ⟨A, minus⟩ := by
  simp [alarmed]

theorem reset_reflection : reflectState reset = reset := rfl

structure StoppedRecord where
  time : ℕ
  terminal : ℝ
  total : ℝ
  state : SRState
deriving DecidableEq

def reflectRecord (record : StoppedRecord) : StoppedRecord :=
  ⟨record.time, -record.terminal, -record.total, reflectState record.state⟩

@[simp] theorem reflectRecord_involutive (record : StoppedRecord) :
    reflectRecord (reflectRecord record) = record := by
  cases record
  simp [reflectRecord]

/-- First inclusive alarm on a finite residual list, carrying a running sum. -/
def firstAlarmFrom (A : ℝ) (state : SRState) (total : ℝ) :
    List ℝ → Option StoppedRecord
  | [] => none
  | z :: tail =>
      let next := srStep state z
      let nextTotal := total + z
      if alarmed A next then
        some ⟨1, z, nextTotal, next⟩
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
      by_cases halarm : alarmed A (srStep state z)
      · have hreflect : alarmed A (reflectState (srStep state z)) :=
          (alarmed_reflection A (srStep state z)).2 halarm
        simp [halarm, hreflect, reflectRecord]
      · have hreflect : ¬ alarmed A (reflectState (srStep state z)) := by
          intro h
          exact halarm ((alarmed_reflection A (srStep state z)).1 h)
        simp only [halarm, hreflect, ↓reduceIte]
        rw [ih (srStep state z) (total + z)]
        cases hrec : firstAlarmFrom A (srStep state z) (total + z) tail with
        | none => simp [hrec]
        | some record => simp [hrec, reflectRecord]

theorem firstAlarm_reflection (A : ℝ) (path : List ℝ) :
    firstAlarm A (path.map fun z => -z) =
      (firstAlarm A path).map reflectRecord := by
  simpa [firstAlarm, reset_reflection] using
    firstAlarmFrom_reflection A path reset 0

theorem reflected_alarm_preserves_time (A : ℝ) (path : List ℝ)
    (record : StoppedRecord) (h : firstAlarm A path = some record) :
    (firstAlarm A (path.map fun z => -z)).map StoppedRecord.time =
      some record.time := by
  rw [firstAlarm_reflection, h]
  simp [reflectRecord]

theorem reflected_alarm_negates_terminal_and_total (A : ℝ) (path : List ℝ)
    (record : StoppedRecord) (h : firstAlarm A path = some record) :
    (firstAlarm A (path.map fun z => -z)).map
        (fun reflected => (reflected.terminal, reflected.total)) =
      some (-record.terminal, -record.total) := by
  rw [firstAlarm_reflection, h]
  simp [reflectRecord]

theorem reflected_terminal_product (record : StoppedRecord) :
    (reflectRecord record).terminal * (reflectRecord record).total =
      record.terminal * record.total := by
  simp [reflectRecord]

/-- Frozen affine mean map after integrating out the mean-zero fresh term. -/
def reuseMean (ρ : ℝ) (terminalMean : ℝ → ℝ) : ℝ → ℝ :=
  fun e => ρ * (e + terminalMean e)

theorem reuseMean_apply (ρ : ℝ) (terminalMean : ℝ → ℝ) (e : ℝ) :
    reuseMean ρ terminalMean e = ρ * (e + terminalMean e) := rfl

theorem reuseMean_zero (terminalMean : ℝ → ℝ) :
    reuseMean 0 terminalMean = fun _ => 0 := by
  funext e
  simp [reuseMean]

theorem reuseMean_one (terminalMean : ℝ → ℝ) :
    reuseMean 1 terminalMean = fun e => e + terminalMean e := by
  funext e
  simp [reuseMean]

theorem reuseMean_odd {terminalMean : ℝ → ℝ}
    (hodd : Function.Odd terminalMean) (ρ : ℝ) :
    Function.Odd (reuseMean ρ terminalMean) := by
  intro e
  rw [reuseMean_apply, reuseMean_apply, hodd]
  ring

/-- Algebraic stopped-score consequence under an explicit expectation derivative. -/
theorem derivative_of_terminalMean
    {terminalMean : ℝ → ℝ} {Γ ρ : ℝ}
    (hmean : HasDerivAt terminalMean (-Γ) 0) :
    HasDerivAt (reuseMean ρ terminalMean) (ρ * (1 - Γ)) 0 := by
  have hsum : HasDerivAt (fun e => e + terminalMean e) (1 + -Γ) 0 :=
    (hasDerivAt_id (x := 0)).add hmean
  change HasDerivAt (fun e => ρ * (e + terminalMean e)) (ρ * (1 - Γ)) 0
  simpa only [sub_eq_add_neg] using hsum.const_mul ρ

/--
Conditional formal proof spine using the existing dominated stopped-integral
interface.  The hypotheses expose the concrete analytic boundary.
-/
theorem derivative_spine_of_dominated
    {Zτ Tτ τR : Ω → ℝ}
    (hZmeas : AEStronglyMeasurable Zτ μ)
    (hTmeas : AEStronglyMeasurable Tτ μ)
    (hτmeas : AEStronglyMeasurable τR μ)
    (hZint : Integrable Zτ μ)
    {δ : ℝ} (hδ : 0 < δ)
    {g : Ω → ℝ} (hgint : Integrable g μ)
    (hdom : ∀ᵐ ω ∂μ, ∀ e ∈ Set.Icc (-δ) δ,
      ‖paramIntegrandDeriv Zτ Tτ τR e ω‖ ≤ g ω)
    (ρ : ℝ) :
    HasDerivAt
      (reuseMean ρ (fun e : ℝ => ∫ ω, Zτ ω *
        Real.exp (-e * Tτ ω - (e ^ 2 / 2) * τR ω) ∂μ))
      (ρ * (1 - ∫ ω, Zτ ω * Tτ ω ∂μ))
      0 := by
  have hmean := hasDerivAt_integral_stoppedIntegrand_zero
    hZmeas hTmeas hτmeas hZint hδ hgint hdom
  exact derivative_of_terminalMean hmean

theorem gamma_gt_two_abs_derivative {Γ : ℝ} (hΓ : 2 < Γ) :
    1 < |1 - Γ| := by
  rw [abs_of_neg (by linarith : 1 - Γ < 0)]
  linarith

theorem gamma_gt_two_full_reuse_instability {Γ : ℝ} (hΓ : 2 < Γ) :
    1 < |(1 : ℝ) * (1 - Γ)| := by
  simpa using gamma_gt_two_abs_derivative hΓ

/-- Exact authoritative scientific decimal, represented as a rational real. -/
def authoritativeA : ℝ := 520886133602749 / 1000000000000

/-- Exact rational value of the active binary64 runtime threshold. -/
def runtimeA : ℝ := 4581762885148045 / 8796093022208

theorem authoritativeA_gt_one : 1 < authoritativeA := by
  norm_num [authoritativeA]

theorem runtimeA_gt_one : 1 < runtimeA := by
  norm_num [runtimeA]

theorem authoritativeA_ne_historical :
    authoritativeA ≠ (5203125 : ℝ) / 10000 := by
  norm_num [authoritativeA]

end RebaseguardLean.SRDerivative
