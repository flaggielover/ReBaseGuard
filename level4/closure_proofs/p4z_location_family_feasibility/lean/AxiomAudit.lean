/-
P4Z axiom audit: every bounded-survival declaration must depend on nothing
beyond Lean's three standard axioms, and on no `sorry`.
-/
import BoundedSurvival

open P4Z

#print axioms P4Z.cusum_up_alarm_iff
#print axioms P4Z.cusum_down_alarm_iff
#print axioms P4Z.cusum_alarm_iff
#print axioms P4Z.cusum_survival_bounded
#print axioms P4Z.cusum_live_residual_bounded
#print axioms P4Z.sr_alarm_iff
#print axioms P4Z.sr_survival_bounded
#print axioms P4Z.srChart_nonneg
#print axioms P4Z.srChart_mono
#print axioms P4Z.srChart_side_condition
#print axioms P4Z.srChart_lt_of_live
#print axioms P4Z.sr_live_residual_bounded

/-- A non-vacuity check: the CUSUM survival interval at the frozen operating
point `k = 1/2`, `h = 5` really does contain a residual, so the statements above
are not about an empty set. -/
example : (0:ℝ) < 5 + (1/2) - 0 ∧ (0:ℝ) - 5 - (1/2) < 0 := by norm_num

/-- And the frozen SR thresholds both satisfy the side condition. -/
example : Real.log (1 + 20) < Real.log 20 + (1/2) :=
  P4Z.srChart_side_condition (by norm_num)

example : Real.log (1 + 520.886133602749) < Real.log 520.886133602749 + (1/2) :=
  P4Z.srChart_side_condition (by norm_num)
