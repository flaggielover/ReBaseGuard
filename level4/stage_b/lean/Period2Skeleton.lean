/-
ReBaseGuard Level 4 — Stage B, optional Lean spine.

Scope, stated up front: this file formalises ONLY the elementary dynamical
skeleton that turns the Stage B numerical certificate into the statement
"locally attracting nonzero symmetric period-2 orbit".  It does NOT formalise
the Fredholm/Arb pipeline, and it is not part of the frozen Level 1-3 Lean
development (`rebaseguard-lean/`), which is untouched.

What is proved here:
  * an odd map with `F e = -e` has `F (F e) = e`  (a genuine 2-cycle when e ≠ 0);
  * the derivative of an odd differentiable map is even;
  * hence the 2-cycle multiplier is `(F' e)^2`;
  * `|multiplier| < 1` is exactly the hyperbolicity hypothesis for local
    attraction of the second iterate.

What is assumed (discharged by the validated numerics, not by Lean):
  * existence and uniqueness of the nonzero root in the certified interval;
  * the enclosure of `F'` on that interval.
-/

namespace ReBaseGuard.StageB

variable {F : ℝ → ℝ}

/-- Oddness, as used by Stage B Lemma L3. -/
def IsOdd (F : ℝ → ℝ) : Prop := ∀ x, F (-x) = -F x

/-- A point of the second iterate coming from an odd map and `F e = -e`. -/
theorem two_cycle_of_odd (hodd : IsOdd F) {e : ℝ} (hroot : F e = -e) :
    F (F e) = e := by
  rw [hroot, hodd e, hroot]
  ring

/-- The orbit really has period 2 (not 1) as soon as `e ≠ 0`. -/
theorem not_fixed_of_ne_zero {e : ℝ} (hne : e ≠ 0) (hroot : F e = -e) :
    F e ≠ e := by
  rw [hroot]
  intro h
  exact hne (by linarith [h])

/-- The derivative of an odd differentiable map is even. -/
theorem deriv_even_of_odd (hodd : IsOdd F) (hdiff : Differentiable ℝ F) :
    ∀ x, deriv F (-x) = deriv F x := by
  intro x
  have hfun : F ∘ (fun y => -y) = fun y => -F y := by
    funext y; simpa using hodd y
  have := congrArg (fun g => deriv g x) hfun
  simpa [deriv.comp, hdiff.differentiableAt, deriv_neg] using this

/-- The multiplier of the symmetric 2-cycle is the square of the slope.

This is the step that makes the *symmetric* route legitimate: without proved
oddness the multiplier would be `F' e * F' (-e)` with two independent factors,
each needing its own certified enclosure. -/
theorem multiplier_eq_sq (hodd : IsOdd F) (hdiff : Differentiable ℝ F)
    {e : ℝ} (hroot : F e = -e) :
    deriv F (F e) * deriv F e = (deriv F e) ^ 2 := by
  rw [hroot, deriv_even_of_odd hodd hdiff e]
  ring

/-- Hyperbolic attraction hypothesis for the second iterate, in the form the
Stage B certificate supplies it: a certified interval `[lo, hi]` containing
`F' e` with `hi^2 < 1` and `lo^2 < 1`. -/
theorem multiplier_lt_one_of_enclosure
    {lo hi d : ℝ} (hlo : lo ≤ d) (hhi : d ≤ hi)
    (h1 : -1 < lo) (h2 : hi < 1) : |d| < 1 := by
  rw [abs_lt]
  exact ⟨by linarith, by linarith⟩

/-- Packaged Stage B conclusion, with the numerical facts as hypotheses.

`certified_root` and `certified_slope` are exactly what
`level4/stage_b/certificate/period2_certificate.json` supplies. -/
theorem stage_b_period2
    (hodd : IsOdd F) (hdiff : Differentiable ℝ F)
    {e lo hi : ℝ}
    (hne : e ≠ 0)
    (certified_root : F e = -e)
    (certified_slope_lo : lo ≤ deriv F e)
    (certified_slope_hi : deriv F e ≤ hi)
    (hlo : -1 < lo) (hhi : hi < 1) :
    F (F e) = e ∧ F e ≠ e ∧ |deriv F (F e) * deriv F e| < 1 := by
  refine ⟨two_cycle_of_odd hodd certified_root,
          not_fixed_of_ne_zero hne certified_root, ?_⟩
  rw [multiplier_eq_sq hodd hdiff certified_root, sq_abs']
  have : |deriv F e| < 1 :=
    multiplier_lt_one_of_enclosure certified_slope_lo certified_slope_hi hlo hhi
  nlinarith [abs_nonneg (deriv F e)]

end ReBaseGuard.StageB
