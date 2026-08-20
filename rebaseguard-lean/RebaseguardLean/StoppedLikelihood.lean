import Mathlib

noncomputable section

def stoppedIntegrand
    (Z T τ : ℝ) (e : ℝ) : ℝ :=
  Z * Real.exp (-e * T - (e^2 / 2) * τ)

def stoppedIntegrandDeriv
    (Z T τ : ℝ) (e : ℝ) : ℝ :=
  Z * (-(T + e * τ)) *
    Real.exp (-e * T - (e^2 / 2) * τ)


/-
Derivative of the exponent `x ↦ -x * T - (x^2 / 2) * τ`,
assembled from the identity and power rules.
-/
lemma stoppedExponent_hasDerivAt
    (T τ e : ℝ) :
    HasDerivAt
      (fun x : ℝ => -x * T - (x^2 / 2) * τ)
      (-T - e * τ)
      e := by
  have hid : HasDerivAt (fun x : ℝ => -x * T) (-1 * T) e :=
    ((hasDerivAt_id' (x := e)).neg).mul_const T
  have hpow : HasDerivAt (fun x : ℝ => x ^ 2) ((2 : ℝ) * e ^ (2 - 1)) e :=
    hasDerivAt_pow 2 e
  have hsq : HasDerivAt (fun x : ℝ => x ^ 2 / 2 * τ)
      ((2 : ℝ) * e ^ (2 - 1) / 2 * τ) e :=
    (hpow.div_const 2).mul_const τ
  have hsub : HasDerivAt (fun x : ℝ => -x * T - x ^ 2 / 2 * τ)
      (-1 * T - (2 : ℝ) * e ^ (2 - 1) / 2 * τ) e :=
    hid.sub hsq
  have hval : -1 * T - (2 : ℝ) * e ^ (2 - 1) / 2 * τ = -T - e * τ := by
    norm_num
  rw [hval] at hsub
  exact hsub


/-
The pointwise derivative identity for `stoppedIntegrand`.
-/
lemma stoppedIntegrand_hasDerivAt
    (Z T τ e : ℝ) :
    HasDerivAt
      (fun x : ℝ => stoppedIntegrand Z T τ x)
      (stoppedIntegrandDeriv Z T τ e)
      e := by
  have hexp :
      HasDerivAt
        (fun x : ℝ => Real.exp (-x * T - (x^2 / 2) * τ))
        (Real.exp (-e * T - (e^2 / 2) * τ) * (-T - e * τ))
        e :=
    (stoppedExponent_hasDerivAt T τ e).exp
  have hmul :
      HasDerivAt
        (fun x : ℝ => Z * Real.exp (-x * T - (x^2 / 2) * τ))
        (Z * (Real.exp (-e * T - (e^2 / 2) * τ) * (-T - e * τ)))
        e :=
    hexp.const_mul Z
  have hval :
      Z * (Real.exp (-e * T - (e^2 / 2) * τ) * (-T - e * τ))
        = stoppedIntegrandDeriv Z T τ e := by
    unfold stoppedIntegrandDeriv
    ring
  rw [hval] at hmul
  exact hmul


/-
The corresponding `deriv` computation.
-/
lemma stoppedIntegrand_deriv
    (Z T τ e : ℝ) :
    deriv
        (fun x : ℝ => stoppedIntegrand Z T τ x)
        e
      =
    stoppedIntegrandDeriv Z T τ e :=
  (stoppedIntegrand_hasDerivAt Z T τ e).deriv
