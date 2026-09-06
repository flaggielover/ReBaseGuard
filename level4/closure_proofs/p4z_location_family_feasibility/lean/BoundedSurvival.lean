/-
P4Z -- the bounded-survival lemma for the two frozen ReBaseGuard detectors.

This is the ONLY new mathematics the P4Z estimator redesign rests on, and it is
deliberately the smallest load-bearing statement: every moment claim about the
Rao-Blackwellised estimators follows from it together with discharge lemma L1,
which the frozen P4 campaign already proved.

The claim, informally.  For the frozen two-sided CUSUM and the frozen two-chart
Shiryaev-Roberts recursion, the set of residuals that do NOT raise an alarm at a
step is an open interval `(L, U)` with `L < 0 < U`, and both endpoints are
bounded in absolute value by the detector's forcing increment `c_D`
(`h + k` for CUSUM, `1/2 + log A` for SR).  Hence every residual on a live path
is uniformly bounded, and the only unbounded coordinate of the reuse window
`A_m` is the single alarm-causing increment `Z_tau`.

Nothing here re-proves the P4 theorem.  Nothing here formalises the estimator.
-/
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

namespace P4Z

/-! ## 1. The frozen two-sided CUSUM

`S+_t = max 0 (S+_{t-1} + Z_t - k)`, `S-_t = max 0 (S-_{t-1} - Z_t - k)`,
alarm iff `max (S+, S-) >= h`, tested after the update, boundary inclusive. -/

/-- One frozen CUSUM up-chart update. -/
def cusumUp (k u z : ℝ) : ℝ := max 0 (u + z - k)

/-- One frozen CUSUM down-chart update. -/
def cusumDown (k d z : ℝ) : ℝ := max 0 (d - z - k)

/-- The up chart alarms exactly on a half line of residuals. -/
theorem cusum_up_alarm_iff {k h u : ℝ} (hh : 0 < h) (z : ℝ) :
    h ≤ cusumUp k u z ↔ h + k - u ≤ z := by
  unfold cusumUp
  rw [le_max_iff]
  constructor
  · rintro (H | H) <;> linarith
  · intro H; right; linarith

/-- The down chart alarms exactly on the opposite half line. -/
theorem cusum_down_alarm_iff {k h d : ℝ} (hh : 0 < h) (z : ℝ) :
    h ≤ cusumDown k d z ↔ z ≤ d - h - k := by
  unfold cusumDown
  rw [le_max_iff]
  constructor
  · rintro (H | H) <;> linarith
  · intro H; right; linarith

/-- **CUSUM alarm set.**  The detector alarms iff the residual leaves the open
interval `(d - h - k, h + k - u)`.  This is an exact reformulation of the frozen
recursion, not an approximation of it. -/
theorem cusum_alarm_iff {k h u d : ℝ} (hh : 0 < h) (z : ℝ) :
    (h ≤ cusumUp k u z ∨ h ≤ cusumDown k d z)
      ↔ (h + k - u ≤ z ∨ z ≤ d - h - k) := by
  rw [cusum_up_alarm_iff hh, cusum_down_alarm_iff hh]

/-- **CUSUM bounded survival.**  On a live state the survival interval straddles
the origin and both endpoints are bounded by the forcing increment `h + k`. -/
theorem cusum_survival_bounded {k h u d : ℝ}
    (_hk : 0 < k) (hu0 : 0 ≤ u) (hd0 : 0 ≤ d) (huh : u < h) (_hdh : d < h) :
    d - h - k < 0 ∧ 0 < h + k - u ∧
      |d - h - k| ≤ h + k ∧ |h + k - u| ≤ h + k := by
  have hh : 0 < h := lt_of_le_of_lt hu0 huh
  refine ⟨by linarith, by linarith, ?_, ?_⟩
  · rw [abs_of_nonpos (by linarith)]; linarith
  · rw [abs_of_nonneg (by linarith)]; linarith

/-- Every residual that does **not** alarm is bounded by the forcing increment. -/
theorem cusum_live_residual_bounded {k h u d z : ℝ}
    (_hk : 0 < k) (hu0 : 0 ≤ u) (hd0 : 0 ≤ d) (huh : u < h) (_hdh : d < h)
    (hsurv : ¬ (h ≤ cusumUp k u z ∨ h ≤ cusumDown k d z)) :
    |z| < h + k := by
  have hh : 0 < h := lt_of_le_of_lt hu0 huh
  rw [cusum_alarm_iff hh, not_or, not_le, not_le] at hsurv
  obtain ⟨hz₁, hz₂⟩ := hsurv
  rw [abs_lt]
  exact ⟨by linarith, by linarith⟩

/-! ## 2. The frozen two-chart Shiryaev-Roberts recursion

Carried in the log domain exactly as the frozen implementation carries it:
`u' = g u + z - 1/2` with `g u = log (1 + exp u)`, alarm iff `u' >= log A`.
Only two properties of `g` are used, so the alarm-set statement is proved for an
abstract chart transform and then instantiated. -/

/-- The log-domain SR chart transform, `logaddexp 0 u`. -/
noncomputable def srChart (u : ℝ) : ℝ := Real.log (1 + Real.exp u)

/-- **SR alarm set**, for an abstract chart transform.  `gu` and `gd` are the
transformed pre-step charts and `l = log A` is the log threshold. -/
theorem sr_alarm_iff (l gu gd z : ℝ) :
    (l ≤ gu + z - (1/2) ∨ l ≤ gd - z - (1/2))
      ↔ (l + (1/2) - gu ≤ z ∨ z ≤ -(l + (1/2) - gd)) := by
  constructor
  · rintro (H | H)
    · exact Or.inl (by linarith)
    · exact Or.inr (by linarith)
  · rintro (H | H)
    · exact Or.inl (by linarith)
    · exact Or.inr (by linarith)

/-- **SR bounded survival**, for an abstract chart transform.  The two facts used
are `0 ≤ g` and `g < l + 1/2`; the second is what a live path supplies. -/
theorem sr_survival_bounded {l gu gd : ℝ}
    (hgu0 : 0 ≤ gu) (hgd0 : 0 ≤ gd)
    (hgu : gu < l + (1/2)) (hgd : gd < l + (1/2)) :
    -(l + (1/2) - gd) < 0 ∧ 0 < l + (1/2) - gu ∧
      |-(l + (1/2) - gd)| ≤ l + (1/2) ∧ |l + (1/2) - gu| ≤ l + (1/2) := by
  refine ⟨by linarith, by linarith, ?_, ?_⟩
  · rw [abs_of_nonpos (by linarith)]; linarith
  · rw [abs_of_nonneg (by linarith)]; linarith

/-- The chart transform is nonnegative: `log (1 + exp u) ≥ 0` for every `u`. -/
theorem srChart_nonneg (u : ℝ) : 0 ≤ srChart u := by
  unfold srChart
  have : (1 : ℝ) ≤ 1 + Real.exp u := by
    have := Real.exp_pos u; linarith
  exact Real.log_nonneg this

/-- The chart transform is monotone. -/
theorem srChart_mono {u v : ℝ} (h : u ≤ v) : srChart u ≤ srChart v := by
  unfold srChart
  have hu := Real.exp_pos u
  have hv := Real.exp_pos v
  exact Real.log_le_log (by linarith) (by
    have := Real.exp_le_exp.mpr h; linarith)

/-- The side condition `log (1 + A) < log A + 1/2`, which the chart bound needs,
holds for every threshold `A ≥ 2`.  Both frozen SR thresholds — `A = 20` for the
reduced layer and `A = 520.886133602749` for the frozen layer — satisfy it. -/
theorem srChart_side_condition {A : ℝ} (hA : 2 ≤ A) :
    Real.log (1 + A) < Real.log A + (1/2) := by
  have hA0 : (0 : ℝ) < A := by linarith
  have hstep : (1 + A) < A * Real.exp (1/2) := by
    have hexp : (3 : ℝ)/2 < Real.exp (1/2) := by
      have := Real.add_one_lt_exp (x := (1/2 : ℝ)) (by norm_num)
      linarith
    nlinarith
  have h1A : (0 : ℝ) < 1 + A := by linarith
  calc Real.log (1 + A)
      < Real.log (A * Real.exp (1/2)) := by
        exact Real.log_lt_log h1A hstep
    _ = Real.log A + (1/2) := by
        rw [Real.log_mul (ne_of_gt hA0) (ne_of_gt (Real.exp_pos _)), Real.log_exp]

/-- **SR chart bound on a live path.**  If the untransformed chart is below the
log threshold and the threshold is at least `2`, the transformed chart is below
`log A + 1/2`, which is exactly the hypothesis `sr_survival_bounded` needs. -/
theorem srChart_lt_of_live {A u : ℝ} (hA : 2 ≤ A) (hu : u < Real.log A) :
    srChart u < Real.log A + (1/2) := by
  have hA0 : (0 : ℝ) < A := by linarith
  have h1 : srChart u ≤ srChart (Real.log A) := srChart_mono (le_of_lt hu)
  have h2 : srChart (Real.log A) = Real.log (1 + A) := by
    unfold srChart; rw [Real.exp_log hA0]
  rw [h2] at h1
  exact lt_of_le_of_lt h1 (srChart_side_condition hA)

/-- Every residual that does **not** alarm the SR detector is bounded by the
forcing increment `1/2 + log A`. -/
theorem sr_live_residual_bounded {A u d z : ℝ} (hA : 2 ≤ A)
    (hu : u < Real.log A) (hd : d < Real.log A)
    (hsurv : ¬ (Real.log A ≤ srChart u + z - (1/2) ∨
                Real.log A ≤ srChart d - z - (1/2))) :
    |z| < Real.log A + (1/2) := by
  rw [sr_alarm_iff, not_or, not_le, not_le] at hsurv
  obtain ⟨hz₁, hz₂⟩ := hsurv
  have hgu : srChart u < Real.log A + (1/2) := srChart_lt_of_live hA hu
  have hgd : srChart d < Real.log A + (1/2) := srChart_lt_of_live hA hd
  have hgu0 : 0 ≤ srChart u := srChart_nonneg u
  have hgd0 : 0 ≤ srChart d := srChart_nonneg d
  rw [abs_lt]
  exact ⟨by linarith, by linarith⟩

/-! ## 3. What this buys

For both frozen detectors, the survival set is an interval straddling the origin
whose endpoints are bounded by the detector's own forcing increment `c_D` — the
same constant discharge lemma L1 already uses for the geometric stopping tail.
Consequently, on `{tau = n}` every residual `Z_1, ..., Z_{n-1}` satisfies
`|Z_t| < c_D`, so the only unbounded coordinate of the truncated reuse window is
the single alarm-causing increment `Z_tau`.  Integrating that one coordinate out
against the base law over the alarm set is what makes the P4Z estimators have
every moment finite, where the historical Route-A summand has an infinite second
moment for an innovation law with infinite variance. -/

end P4Z
