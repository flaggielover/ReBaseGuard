import RebaseguardLean.IntegralBridge

/-!
# Gate 4: discharging the Gate 3 domination hypothesis

Gate 3 (`hasDerivAt_integral_stoppedIntegrand_zero`) assumes an *integrable
dominating function* `g` with

  `∀ᵐ ω ∂μ, ∀ e ∈ Set.Icc (-δ) δ, ‖paramIntegrandDeriv Zτ Tτ τ e ω‖ ≤ g ω`.

This file discharges that hypothesis as far as it is mathematically justified,
in four separated sub-gates.

* **Gate 4A** (`abs_stoppedIntegrandDeriv_le`) — a purely deterministic
  real-number inequality: for `|e| ≤ δ`,
  `‖Z * (-(T + e*t)) * exp (-e*T - e²/2*t)‖ ≤ |Z| * (|T| + δ*|t|) * exp (δ*|T| + δ²/2*|t|)`.

* **Gate 4B** (`explicitDominatingFunction`, `hdom_explicitDominatingFunction`) —
  the explicit dominating function, and the fact that it satisfies Gate 3's
  `hdom` *unconditionally* (the bound is pointwise, not merely a.e.).
  Its a.e.-strong-measurability is derived, not assumed.

* **Gate 4C** (`integrable_explicitDominatingFunction_of_expMoment` and friends) —
  abstract sufficient conditions for the dominating function to be integrable,
  built from exponential moments by elementary domination (`x ≤ exp x`) and the
  elementary Cauchy–Schwarz/AM–GM bound `2xy ≤ x² + y²`.

* **Gate 4D** — the forcing-time bridge.  This part is deliberately split:
  - `integrable_exp_abs_of_le`, `integrable_exp_of_geometric_tail` are
    **abstract**: "if `τ ≤ N` and `N` has geometric tails then the required
    exponential moments hold".
  - `cusumStat`, `cusumAlarm`, `forcingTime`,
    `cusumAlarm_le_forcingTime_succ` are **genuinely CUSUM-specific**, but
    *pathwise/deterministic* only.

  **Remaining mathematical debt (NOT proved here).**  Nothing in this file shows
  that the `Zτ`, `Tτ`, `τ` appearing in the Gate 3 integral are the stopped
  likelihood objects of the ReBaseGuard CUSUM process: there is no filtration,
  no stopping-time measurability, and no proof that the ReBaseGuard forcing time
  actually has geometric tails under the ReBaseGuard noise model.  Those remain
  hypotheses of the final theorems below and are listed explicitly there.
-/

noncomputable section

open MeasureTheory Filter Set

namespace RebaseguardLean

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

/-! ## Gate 4A — deterministic pointwise domination

Plain real-number inequalities.  No measure theory, no `HasDerivAt`. -/

/-- `|T + e*t| ≤ |T| + δ*|t|` whenever `|e| ≤ δ`. -/
lemma abs_add_mul_le_of_abs_le {T t e δ : ℝ} (he : |e| ≤ δ) :
    |T + e * t| ≤ |T| + δ * |t| := by
  have h1 : |T + e * t| ≤ |T| + |e * t| := abs_add_le _ _
  have h2 : |e * t| = |e| * |t| := abs_mul e t
  have h3 : |e| * |t| ≤ δ * |t| := mul_le_mul_of_nonneg_right he (abs_nonneg t)
  linarith

/-- `e^2 ≤ δ^2` whenever `|e| ≤ δ` and `0 ≤ δ`. -/
lemma sq_le_sq_of_abs_le {e δ : ℝ} (hδ : 0 ≤ δ) (he : |e| ≤ δ) : e ^ 2 ≤ δ ^ 2 := by
  have hmul : |e| * |e| ≤ δ * δ := mul_le_mul he he (abs_nonneg e) hδ
  have habs : |e| ^ 2 = e ^ 2 := sq_abs e
  nlinarith [hmul, habs]

/-- The exponent of the stopped integrand is bounded, uniformly for `|e| ≤ δ`, by
`δ*|T| + δ²/2*|t|`. -/
lemma stoppedExponent_le_of_abs_le {T t e δ : ℝ} (hδ : 0 ≤ δ) (he : |e| ≤ δ) :
    -e * T - e ^ 2 / 2 * t ≤ δ * |T| + δ ^ 2 / 2 * |t| := by
  have hsq : e ^ 2 ≤ δ ^ 2 := sq_le_sq_of_abs_le hδ he
  have h1 : -e * T ≤ δ * |T| := by
    have ha : -(e * T) ≤ |e * T| := neg_le_abs _
    rw [abs_mul] at ha
    have hb : |e| * |T| ≤ δ * |T| := mul_le_mul_of_nonneg_right he (abs_nonneg T)
    linarith
  have h2 : -(e ^ 2 / 2 * t) ≤ δ ^ 2 / 2 * |t| := by
    have ha : -(e ^ 2 / 2 * t) ≤ |e ^ 2 / 2 * t| := neg_le_abs _
    rw [abs_mul, abs_of_nonneg (by positivity : (0:ℝ) ≤ e ^ 2 / 2)] at ha
    have hc : e ^ 2 / 2 * |t| ≤ δ ^ 2 / 2 * |t| :=
      mul_le_mul_of_nonneg_right (by linarith) (abs_nonneg t)
    linarith
  linarith

/-- **Gate 4A.**  The deterministic domination inequality for the Gate 2
pointwise derivative `stoppedIntegrandDeriv`. -/
lemma abs_stoppedIntegrandDeriv_le {Z T t e δ : ℝ} (hδ : 0 ≤ δ) (he : |e| ≤ δ) :
    ‖stoppedIntegrandDeriv Z T t e‖
      ≤ |Z| * (|T| + δ * |t|) * Real.exp (δ * |T| + δ ^ 2 / 2 * |t|) := by
  have hnorm : ‖stoppedIntegrandDeriv Z T t e‖
      = |Z| * |T + e * t| * Real.exp (-e * T - e ^ 2 / 2 * t) := by
    unfold stoppedIntegrandDeriv
    rw [Real.norm_eq_abs, abs_mul, abs_mul, abs_neg, Real.abs_exp]
  rw [hnorm]
  have hfac : |Z| * |T + e * t| ≤ |Z| * (|T| + δ * |t|) :=
    mul_le_mul_of_nonneg_left (abs_add_mul_le_of_abs_le he) (abs_nonneg Z)
  have hexp : Real.exp (-e * T - e ^ 2 / 2 * t) ≤ Real.exp (δ * |T| + δ ^ 2 / 2 * |t|) :=
    Real.exp_le_exp.mpr (stoppedExponent_le_of_abs_le hδ he)
  exact mul_le_mul hfac hexp (Real.exp_nonneg _)
    (mul_nonneg (abs_nonneg Z) (add_nonneg (abs_nonneg T) (mul_nonneg hδ (abs_nonneg t))))


/-! ## Gate 4B — the explicit dominating function, and Gate 3's `hdom` -/

/-- The explicit dominating function

  `g ω = |Zτ ω| * (|Tτ ω| + δ*|τ ω|) * exp (δ*|Tτ ω| + δ²/2*|τ ω|)`

for the parameter range `e ∈ [-δ, δ]`. -/
def explicitDominatingFunction (Zτ Tτ τ : Ω → ℝ) (δ : ℝ) (ω : Ω) : ℝ :=
  |Zτ ω| * (|Tτ ω| + δ * |τ ω|) * Real.exp (δ * |Tτ ω| + δ ^ 2 / 2 * |τ ω|)

omit [MeasurableSpace Ω] in
lemma explicitDominatingFunction_nonneg (Zτ Tτ τ : Ω → ℝ) {δ : ℝ} (hδ : 0 ≤ δ) (ω : Ω) :
    0 ≤ explicitDominatingFunction Zτ Tτ τ δ ω := by
  unfold explicitDominatingFunction
  exact mul_nonneg
    (mul_nonneg (abs_nonneg _) (add_nonneg (abs_nonneg _) (mul_nonneg hδ (abs_nonneg _))))
    (Real.exp_nonneg _)

omit [MeasurableSpace Ω] in
/-- **Gate 4B, pointwise form.**  The Gate 3 integrand derivative is dominated by
`explicitDominatingFunction` for every `ω` and every `e ∈ [-δ, δ]`. -/
lemma norm_paramIntegrandDeriv_le (Zτ Tτ τ : Ω → ℝ) {δ : ℝ} (hδ : 0 ≤ δ)
    {e : ℝ} (he : e ∈ Set.Icc (-δ) δ) (ω : Ω) :
    ‖paramIntegrandDeriv Zτ Tτ τ e ω‖ ≤ explicitDominatingFunction Zτ Tτ τ δ ω := by
  have habs : |e| ≤ δ := abs_le.mpr ⟨he.1, he.2⟩
  unfold paramIntegrandDeriv explicitDominatingFunction
  exact abs_stoppedIntegrandDeriv_le hδ habs

/-- **Gate 4B.**  Exactly the `hdom` hypothesis of Gate 3, with the dominating
function explicitly identified.  No integrability is needed for this: the bound
holds unconditionally. -/
theorem hdom_explicitDominatingFunction (Zτ Tτ τ : Ω → ℝ) {δ : ℝ} (hδ : 0 ≤ δ) :
    ∀ᵐ ω ∂μ, ∀ e ∈ Set.Icc (-δ) δ,
      ‖paramIntegrandDeriv Zτ Tτ τ e ω‖ ≤ explicitDominatingFunction Zτ Tτ τ δ ω :=
  Filter.Eventually.of_forall fun ω _ he => norm_paramIntegrandDeriv_le Zτ Tτ τ hδ he ω

/-! ### Measurability, derived rather than assumed -/

lemma aestronglyMeasurable_abs {f : Ω → ℝ} (hf : AEStronglyMeasurable f μ) :
    AEStronglyMeasurable (fun ω => |f ω|) μ :=
  continuous_abs.comp_aestronglyMeasurable hf

lemma aestronglyMeasurable_exp_abs {f : Ω → ℝ} (hf : AEStronglyMeasurable f μ) (a : ℝ) :
    AEStronglyMeasurable (fun ω => Real.exp (a * |f ω|)) μ :=
  Real.continuous_exp.comp_aestronglyMeasurable
    ((aestronglyMeasurable_abs hf).const_mul a)

lemma aestronglyMeasurable_exp_abs_add {Tτ τ : Ω → ℝ}
    (hT : AEStronglyMeasurable Tτ μ) (hτ : AEStronglyMeasurable τ μ) (a b : ℝ) :
    AEStronglyMeasurable (fun ω => Real.exp (a * |Tτ ω| + b * |τ ω|)) μ :=
  Real.continuous_exp.comp_aestronglyMeasurable
    (((aestronglyMeasurable_abs hT).const_mul a).add
      ((aestronglyMeasurable_abs hτ).const_mul b))

lemma aestronglyMeasurable_absZ_mul_exp {Zτ Tτ τ : Ω → ℝ}
    (hZ : AEStronglyMeasurable Zτ μ) (hT : AEStronglyMeasurable Tτ μ)
    (hτ : AEStronglyMeasurable τ μ) (a b : ℝ) :
    AEStronglyMeasurable (fun ω => |Zτ ω| * Real.exp (a * |Tτ ω| + b * |τ ω|)) μ :=
  (aestronglyMeasurable_abs hZ).mul (aestronglyMeasurable_exp_abs_add hT hτ a b)

lemma aestronglyMeasurable_explicitDominatingFunction {Zτ Tτ τ : Ω → ℝ}
    (hZ : AEStronglyMeasurable Zτ μ) (hT : AEStronglyMeasurable Tτ μ)
    (hτ : AEStronglyMeasurable τ μ) (δ : ℝ) :
    AEStronglyMeasurable (explicitDominatingFunction Zτ Tτ τ δ) μ := by
  unfold explicitDominatingFunction
  exact ((aestronglyMeasurable_abs hZ).mul
      ((aestronglyMeasurable_abs hT).add ((aestronglyMeasurable_abs hτ).const_mul δ))).mul
    (Real.continuous_exp.comp_aestronglyMeasurable
      (((aestronglyMeasurable_abs hT).const_mul δ).add
        ((aestronglyMeasurable_abs hτ).const_mul (δ ^ 2 / 2))))


/-! ## Gate 4C — exponential moments ⇒ the dominating function is integrable -/

/-- Elementary domination of a linear factor by an exponential: for every `c > 0`,

  `(T + δ*t) * exp (δ*T + δ²/2*t) ≤ c⁻¹ * exp ((δ+c)*T + (δ²/2 + c*δ)*t)`.

This is the scalar heart of Gate 4C; it uses only `x + 1 ≤ exp x`. -/
lemma linear_mul_exp_le_exp {T t δ c : ℝ} (hc : 0 < c) :
    (T + δ * t) * Real.exp (δ * T + δ ^ 2 / 2 * t)
      ≤ c⁻¹ * Real.exp ((δ + c) * T + (δ ^ 2 / 2 + c * δ) * t) := by
  have hu : c * T + c * δ * t ≤ Real.exp (c * T + c * δ * t) := by
    have h := Real.add_one_le_exp (c * T + c * δ * t)
    linarith
  have hcinv : (0:ℝ) < c⁻¹ := inv_pos.mpr hc
  have h2 := mul_le_mul_of_nonneg_left hu hcinv.le
  have h3 : c⁻¹ * (c * T + c * δ * t) = T + δ * t := by
    have hfac : c * T + c * δ * t = c * (T + δ * t) := by ring
    rw [hfac, ← mul_assoc, inv_mul_cancel₀ (ne_of_gt hc), one_mul]
  rw [h3] at h2
  calc (T + δ * t) * Real.exp (δ * T + δ ^ 2 / 2 * t)
      ≤ c⁻¹ * Real.exp (c * T + c * δ * t) * Real.exp (δ * T + δ ^ 2 / 2 * t) :=
        mul_le_mul_of_nonneg_right h2 (Real.exp_nonneg _)
    _ = c⁻¹ * Real.exp (c * T + c * δ * t + (δ * T + δ ^ 2 / 2 * t)) := by
        rw [mul_assoc, ← Real.exp_add]
    _ = c⁻¹ * Real.exp ((δ + c) * T + (δ ^ 2 / 2 + c * δ) * t) := by
        congr 2; ring

omit [MeasurableSpace Ω] in
/-- Pointwise: the dominating function is bounded by a constant multiple of an
exponential-moment integrand, provided `δ + c ≤ a` and `δ²/2 + c*δ ≤ b`. -/
lemma explicitDominatingFunction_le_expMoment (Zτ Tτ τ : Ω → ℝ) {δ c a b : ℝ}
    (hc : 0 < c) (ha : δ + c ≤ a) (hb : δ ^ 2 / 2 + c * δ ≤ b) (ω : Ω) :
    explicitDominatingFunction Zτ Tτ τ δ ω
      ≤ c⁻¹ * (|Zτ ω| * Real.exp (a * |Tτ ω| + b * |τ ω|)) := by
  have hkey := linear_mul_exp_le_exp (T := |Tτ ω|) (t := |τ ω|) (δ := δ) hc
  have hmono : Real.exp ((δ + c) * |Tτ ω| + (δ ^ 2 / 2 + c * δ) * |τ ω|)
      ≤ Real.exp (a * |Tτ ω| + b * |τ ω|) := by
    refine Real.exp_le_exp.mpr ?_
    have h1 : (δ + c) * |Tτ ω| ≤ a * |Tτ ω| := mul_le_mul_of_nonneg_right ha (abs_nonneg _)
    have h2 : (δ ^ 2 / 2 + c * δ) * |τ ω| ≤ b * |τ ω| :=
      mul_le_mul_of_nonneg_right hb (abs_nonneg _)
    linarith
  have hstep : (|Tτ ω| + δ * |τ ω|) * Real.exp (δ * |Tτ ω| + δ ^ 2 / 2 * |τ ω|)
      ≤ c⁻¹ * Real.exp (a * |Tτ ω| + b * |τ ω|) :=
    hkey.trans (mul_le_mul_of_nonneg_left hmono (inv_pos.mpr hc).le)
  unfold explicitDominatingFunction
  calc |Zτ ω| * (|Tτ ω| + δ * |τ ω|) * Real.exp (δ * |Tτ ω| + δ ^ 2 / 2 * |τ ω|)
      = |Zτ ω| * ((|Tτ ω| + δ * |τ ω|) * Real.exp (δ * |Tτ ω| + δ ^ 2 / 2 * |τ ω|)) := by
        ring
    _ ≤ |Zτ ω| * (c⁻¹ * Real.exp (a * |Tτ ω| + b * |τ ω|)) :=
        mul_le_mul_of_nonneg_left hstep (abs_nonneg _)
    _ = c⁻¹ * (|Zτ ω| * Real.exp (a * |Tτ ω| + b * |τ ω|)) := by ring

/-- **Gate 4C, main sufficient condition.**  A single joint exponential moment

  `Integrable (fun ω => |Zτ ω| * exp (a*|Tτ ω| + b*|τ ω|)) μ`

with `δ + c ≤ a`, `δ²/2 + c*δ ≤ b` for some `c > 0`, makes the explicit
dominating function integrable. -/
theorem integrable_explicitDominatingFunction_of_expMoment {Zτ Tτ τ : Ω → ℝ}
    (hZ : AEStronglyMeasurable Zτ μ) (hT : AEStronglyMeasurable Tτ μ)
    (hτ : AEStronglyMeasurable τ μ)
    {δ c a b : ℝ} (hδ : 0 ≤ δ) (hc : 0 < c)
    (ha : δ + c ≤ a) (hb : δ ^ 2 / 2 + c * δ ≤ b)
    (hmom : Integrable (fun ω => |Zτ ω| * Real.exp (a * |Tτ ω| + b * |τ ω|)) μ) :
    Integrable (explicitDominatingFunction Zτ Tτ τ δ) μ := by
  refine Integrable.mono' (hmom.const_mul c⁻¹)
    (aestronglyMeasurable_explicitDominatingFunction hZ hT hτ δ) ?_
  filter_upwards with ω
  rw [Real.norm_eq_abs, abs_of_nonneg (explicitDominatingFunction_nonneg Zτ Tτ τ hδ ω)]
  exact explicitDominatingFunction_le_expMoment Zτ Tτ τ hc ha hb ω

/-- The joint exponential moment already forces `Zτ` itself to be integrable
(when `0 ≤ a`, `0 ≤ b`), so Gate 3's `hZint` need not be assumed separately. -/
theorem integrable_of_expMoment {Zτ Tτ τ : Ω → ℝ}
    (hZ : AEStronglyMeasurable Zτ μ) {a b : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b)
    (hmom : Integrable (fun ω => |Zτ ω| * Real.exp (a * |Tτ ω| + b * |τ ω|)) μ) :
    Integrable Zτ μ := by
  refine Integrable.mono' hmom hZ ?_
  filter_upwards with ω
  rw [Real.norm_eq_abs]
  have h0 : (0:ℝ) ≤ a * |Tτ ω| + b * |τ ω| :=
    add_nonneg (mul_nonneg ha (abs_nonneg _)) (mul_nonneg hb (abs_nonneg _))
  exact le_mul_of_one_le_right (abs_nonneg _) (Real.one_le_exp h0)

/-! ### Building the joint exponential moment out of separate moments

Everything here is elementary: `2*x*y ≤ x² + y²`, i.e. Cauchy–Schwarz in its
pointwise AM–GM form, applied twice. -/

/-- Monotonicity of exponential moments in the exponent. -/
lemma integrable_exp_abs_mono {f : Ω → ℝ} (hf : AEStronglyMeasurable f μ) {p q : ℝ}
    (hpq : p ≤ q) (h : Integrable (fun ω => Real.exp (q * |f ω|)) μ) :
    Integrable (fun ω => Real.exp (p * |f ω|)) μ := by
  refine Integrable.mono' h (aestronglyMeasurable_exp_abs hf p) ?_
  filter_upwards with ω
  rw [Real.norm_eq_abs, Real.abs_exp]
  exact Real.exp_le_exp.mpr (mul_le_mul_of_nonneg_right hpq (abs_nonneg _))

/-- Separate exponential moments in `Tτ` and `τ` give a joint one. -/
theorem integrable_exp_abs_add_of_sq {Tτ τ : Ω → ℝ}
    (hT : AEStronglyMeasurable Tτ μ) (hτ : AEStronglyMeasurable τ μ) {a b : ℝ}
    (hTexp : Integrable (fun ω => Real.exp (2 * a * |Tτ ω|)) μ)
    (hτexp : Integrable (fun ω => Real.exp (2 * b * |τ ω|)) μ) :
    Integrable (fun ω => Real.exp (a * |Tτ ω| + b * |τ ω|)) μ := by
  refine Integrable.mono' ((hTexp.add hτexp).div_const 2)
    (aestronglyMeasurable_exp_abs_add hT hτ a b) ?_
  filter_upwards with ω
  simp only [Pi.add_apply]
  rw [Real.norm_eq_abs, Real.abs_exp, Real.exp_add]
  have h2 := two_mul_le_add_sq (Real.exp (a * |Tτ ω|)) (Real.exp (b * |τ ω|))
  have e1 : Real.exp (a * |Tτ ω|) ^ 2 = Real.exp (2 * a * |Tτ ω|) := by
    rw [sq, ← Real.exp_add]; congr 1; ring
  have e2 : Real.exp (b * |τ ω|) ^ 2 = Real.exp (2 * b * |τ ω|) := by
    rw [sq, ← Real.exp_add]; congr 1; ring
  rw [e1, e2] at h2
  linarith

/-- `Zτ ∈ L²` together with a square-integrable exponential factor gives the
joint moment of Gate 4C. -/
theorem integrable_absZ_mul_exp_of_sq {Zτ Tτ τ : Ω → ℝ}
    (hZ : AEStronglyMeasurable Zτ μ) (hT : AEStronglyMeasurable Tτ μ)
    (hτ : AEStronglyMeasurable τ μ) {a b : ℝ}
    (hZsq : Integrable (fun ω => Zτ ω ^ 2) μ)
    (hexp : Integrable (fun ω => Real.exp (2 * a * |Tτ ω| + 2 * b * |τ ω|)) μ) :
    Integrable (fun ω => |Zτ ω| * Real.exp (a * |Tτ ω| + b * |τ ω|)) μ := by
  refine Integrable.mono' ((hZsq.add hexp).div_const 2)
    (aestronglyMeasurable_absZ_mul_exp hZ hT hτ a b) ?_
  filter_upwards with ω
  have hnn : 0 ≤ |Zτ ω| * Real.exp (a * |Tτ ω| + b * |τ ω|) :=
    mul_nonneg (abs_nonneg _) (Real.exp_nonneg _)
  simp only [Pi.add_apply]
  rw [Real.norm_eq_abs, abs_of_nonneg hnn]
  have hE2 : Real.exp (a * |Tτ ω| + b * |τ ω|) ^ 2
      = Real.exp (2 * a * |Tτ ω| + 2 * b * |τ ω|) := by
    rw [sq, ← Real.exp_add]; congr 1; ring
  have h2 := two_mul_le_add_sq |Zτ ω| (Real.exp (a * |Tτ ω| + b * |τ ω|))
  rw [sq_abs, hE2] at h2
  linarith

/-- **Gate 4C, split form.**  `Zτ ∈ L²` plus *separate* exponential moments of
`Tτ` and of `τ` (at exponents at least `4a` and `4b`) give the joint moment. -/
theorem integrable_absZ_mul_exp_of_separate {Zτ Tτ τ : Ω → ℝ}
    (hZ : AEStronglyMeasurable Zτ μ) (hT : AEStronglyMeasurable Tτ μ)
    (hτ : AEStronglyMeasurable τ μ) {a b p q : ℝ}
    (hp : 4 * a ≤ p) (hq : 4 * b ≤ q)
    (hZsq : Integrable (fun ω => Zτ ω ^ 2) μ)
    (hTexp : Integrable (fun ω => Real.exp (p * |Tτ ω|)) μ)
    (hτexp : Integrable (fun ω => Real.exp (q * |τ ω|)) μ) :
    Integrable (fun ω => |Zτ ω| * Real.exp (a * |Tτ ω| + b * |τ ω|)) μ := by
  have hT4 : Integrable (fun ω => Real.exp (2 * (2 * a) * |Tτ ω|)) μ :=
    integrable_exp_abs_mono hT (by linarith) hTexp
  have hτ4 : Integrable (fun ω => Real.exp (2 * (2 * b) * |τ ω|)) μ :=
    integrable_exp_abs_mono hτ (by linarith) hτexp
  exact integrable_absZ_mul_exp_of_sq hZ hT hτ hZsq
    (integrable_exp_abs_add_of_sq hT hτ hT4 hτ4)


/-! ## Gate 4D — forcing time and geometric tails

### Part A: abstract results

These are genuine theorems about an *abstract* random time `ρ` dominated by an
abstract forcing time `N`.  They say nothing about CUSUM by themselves. -/

/-- If `0 ≤ ρ ≤ N` a.e. and `N` has the exponential moment at rate `b ≥ 0`,
then `ρ` has the exponential moment at rate `b`. -/
theorem integrable_exp_abs_of_le {ρ N : Ω → ℝ}
    (hρ : AEStronglyMeasurable ρ μ) {b : ℝ} (hb : 0 ≤ b)
    (hρ0 : ∀ᵐ ω ∂μ, 0 ≤ ρ ω) (hle : ∀ᵐ ω ∂μ, ρ ω ≤ N ω)
    (hN : Integrable (fun ω => Real.exp (b * N ω)) μ) :
    Integrable (fun ω => Real.exp (b * |ρ ω|)) μ := by
  refine Integrable.mono' hN (aestronglyMeasurable_exp_abs hρ b) ?_
  filter_upwards [hρ0, hle] with ω h0 h1
  rw [Real.norm_eq_abs, Real.abs_exp, abs_of_nonneg h0]
  exact Real.exp_le_exp.mpr (mul_le_mul_of_nonneg_left h1 hb)

/-- A geometric tail bound `μ {N ≥ n} ≤ C rⁿ` implies the pointwise bound
`μ {N = n} ≤ C rⁿ`. -/
lemma measure_eq_le_of_tail_le {N : Ω → ℕ} {C r : ℝ}
    (htail : ∀ n : ℕ, μ {ω | n ≤ N ω} ≤ ENNReal.ofReal (C * r ^ n)) (n : ℕ) :
    μ {ω | N ω = n} ≤ ENNReal.ofReal (C * r ^ n) :=
  le_trans (measure_mono fun _ hω => hω.ge) (htail n)

/-- **Gate 4D, abstract geometric-tail bridge.**  A `ℕ`-valued time whose
distribution has geometric tails `μ {N = n} ≤ C rⁿ` has a finite exponential
moment at every rate `b ≥ 0` with `exp b * r < 1`. -/
theorem integrable_exp_of_geometric_tail {N : Ω → ℕ} (hNmeas : Measurable N)
    {C r b : ℝ} (hC : 0 ≤ C) (hr : 0 ≤ r) (hbr : Real.exp b * r < 1)
    (hpmf : ∀ n : ℕ, μ {ω | N ω = n} ≤ ENNReal.ofReal (C * r ^ n)) :
    Integrable (fun ω => Real.exp (b * (N ω : ℝ))) μ := by
  have hcast : Measurable (fun ω => ((N ω : ℝ))) :=
    (measurable_of_countable (fun n : ℕ => (n : ℝ))).comp hNmeas
  have hmeas : Measurable (fun ω => Real.exp (b * (N ω : ℝ))) :=
    Real.measurable_exp.comp (hcast.const_mul b)
  refine ⟨hmeas.aestronglyMeasurable, ?_⟩
  rw [hasFiniteIntegral_iff_ofReal
    (Filter.Eventually.of_forall fun ω => Real.exp_nonneg (b * (N ω : ℝ)))]
  have hlint : ∫⁻ ω, ENNReal.ofReal (Real.exp (b * (N ω : ℝ))) ∂μ
      = ∑' n : ℕ, ENNReal.ofReal (Real.exp (b * (n : ℝ))) * μ {ω | N ω = n} := by
    calc ∫⁻ ω, ENNReal.ofReal (Real.exp (b * (N ω : ℝ))) ∂μ
        = ∫⁻ n : ℕ, ENNReal.ofReal (Real.exp (b * (n : ℝ))) ∂(Measure.map N μ) :=
          (lintegral_map (μ := μ)
            (f := fun n : ℕ => ENNReal.ofReal (Real.exp (b * (n : ℝ)))) (g := N)
            (measurable_of_countable _) hNmeas).symm
      _ = ∑' n : ℕ, ENNReal.ofReal (Real.exp (b * (n : ℝ))) * (Measure.map N μ) {n} :=
          lintegral_countable' _
      _ = ∑' n : ℕ, ENNReal.ofReal (Real.exp (b * (n : ℝ))) * μ {ω | N ω = n} := by
          refine tsum_congr fun n => ?_
          rw [Measure.map_apply hNmeas (measurableSet_singleton n)]
          rfl
  have hgeo : (0:ℝ) ≤ Real.exp b * r := mul_nonneg (Real.exp_nonneg b) hr
  have hbound : ∑' n : ℕ, ENNReal.ofReal (Real.exp (b * (n : ℝ))) * μ {ω | N ω = n}
      ≤ ∑' n : ℕ, ENNReal.ofReal (C * (Real.exp b * r) ^ n) := by
    refine ENNReal.tsum_le_tsum fun n => ?_
    have harith : Real.exp (b * (n : ℝ)) * (C * r ^ n) = C * (Real.exp b * r) ^ n := by
      rw [mul_comm b (n : ℝ), Real.exp_nat_mul, mul_pow]; ring
    calc ENNReal.ofReal (Real.exp (b * (n : ℝ))) * μ {ω | N ω = n}
        ≤ ENNReal.ofReal (Real.exp (b * (n : ℝ))) * ENNReal.ofReal (C * r ^ n) := by
          gcongr
          exact hpmf n
      _ = ENNReal.ofReal (Real.exp (b * (n : ℝ)) * (C * r ^ n)) :=
          (ENNReal.ofReal_mul (Real.exp_nonneg _)).symm
      _ = ENNReal.ofReal (C * (Real.exp b * r) ^ n) := by rw [harith]
  have hsummable : Summable (fun n : ℕ => C * (Real.exp b * r) ^ n) :=
    (summable_geometric_of_lt_one hgeo hbr).mul_left C
  have hfin : ∑' n : ℕ, ENNReal.ofReal (C * (Real.exp b * r) ^ n) < ⊤ := by
    rw [← ENNReal.ofReal_tsum_of_nonneg
      (fun n => mul_nonneg hC (pow_nonneg hgeo n)) hsummable]
    exact ENNReal.ofReal_lt_top
  rw [hlint]
  exact lt_of_le_of_lt hbound hfin

/-! ### Part B: the CUSUM construction — pathwise only

The definitions below are the *actual* CUSUM recursion and alarm time, and
`cusumAlarm_le_forcingTime_succ` is the *actual* forcing argument
(`H = h + k`, one score above `H` forces an alarm).  They are, however,
**purely deterministic statements about a single path** `z : ℕ → ℝ`.

They do **not** provide:
* measurability of `ω ↦ cusumAlarm k h (z ω)` as a stopping time,
* any tail bound on `forcingTime`, which would require the ReBaseGuard noise
  model (independence / Gaussian scores) and is *not* formalized here,
* any identification of the Gate 3 data `Zτ`, `Tτ`, `τ` with stopped CUSUM
  quantities.
-/

/-- The CUSUM statistic with reference value `k`, driven by the score sequence
`z`: `S₀ = 0`, `S_{n+1} = max 0 (Sₙ + zₙ - k)`. -/
def cusumStat (k : ℝ) (z : ℕ → ℝ) : ℕ → ℝ
  | 0 => 0
  | n + 1 => max 0 (cusumStat k z n + z n - k)

@[simp] lemma cusumStat_zero (k : ℝ) (z : ℕ → ℝ) : cusumStat k z 0 = 0 := rfl

@[simp] lemma cusumStat_succ (k : ℝ) (z : ℕ → ℝ) (n : ℕ) :
    cusumStat k z (n + 1) = max 0 (cusumStat k z n + z n - k) := rfl

lemma cusumStat_nonneg (k : ℝ) (z : ℕ → ℝ) (n : ℕ) : 0 ≤ cusumStat k z n := by
  cases n with
  | zero => exact le_refl 0
  | succ m => rw [cusumStat_succ]; exact le_max_left _ _

/-- The CUSUM alarm time: the first index at which the statistic exceeds `h`. -/
def cusumAlarm (k h : ℝ) (z : ℕ → ℝ) : ℕ := sInf {n | h < cusumStat k z n}

/-- The forcing time at level `H`: the first index whose score exceeds `H`. -/
def forcingTime (H : ℝ) (z : ℕ → ℝ) : ℕ := sInf {n | H < z n}

/-- **The CUSUM forcing step.**  A single score above `H = h + k` pushes the
CUSUM statistic above the alarm threshold `h` at the next index. -/
lemma lt_cusumStat_succ_of_lt (k h : ℝ) (z : ℕ → ℝ) {n : ℕ} (hz : h + k < z n) :
    h < cusumStat k z (n + 1) := by
  have h0 : 0 ≤ cusumStat k z n := cusumStat_nonneg k z n
  have hlt : h < cusumStat k z n + z n - k := by linarith
  rw [cusumStat_succ]
  exact lt_of_lt_of_le hlt (le_max_right _ _)

lemma cusumAlarm_le_of_lt (k h : ℝ) (z : ℕ → ℝ) {n : ℕ} (hz : h + k < z n) :
    cusumAlarm k h z ≤ n + 1 :=
  Nat.sInf_le (lt_cusumStat_succ_of_lt k h z hz)

/-- **Gate 4D, CUSUM-specific pathwise bound.**  With `H = h + k`, the CUSUM
alarm time is at most one step past the forcing time.  This is the formal
content of "`Z_t > H` forces a threshold crossing, hence `τ ≤ N`". -/
theorem cusumAlarm_le_forcingTime_succ (k h : ℝ) (z : ℕ → ℝ)
    (hex : ∃ n, h + k < z n) :
    cusumAlarm k h z ≤ forcingTime (h + k) z + 1 :=
  cusumAlarm_le_of_lt k h z (Nat.sInf_mem hex)


/-! ## Final connection to Gate 3

The strongest theorem of this file.  Compared with Gate 3 it removes:
* the abstract dominating function `g` and its integrability,
* the `hdom` hypothesis entirely,
* the separate integrability hypothesis `Integrable Zτ μ`.

What remains exposed is exactly the mathematical debt: measurability of the
three stopped quantities, and one joint exponential moment. -/

/-- **Gate 4, final theorem (exponential-moment form).**  Differentiation under
the integral sign at `e = 0`, with the Gate 3 domination hypothesis discharged
from a single joint exponential moment. -/
theorem hasDerivAt_integral_stoppedIntegrand_zero_of_expMoment
    {Zτ Tτ τ : Ω → ℝ}
    (hZmeas : AEStronglyMeasurable Zτ μ)
    (hTmeas : AEStronglyMeasurable Tτ μ)
    (hτmeas : AEStronglyMeasurable τ μ)
    {δ c a b : ℝ} (hδ : 0 < δ) (hc : 0 < c)
    (ha : δ + c ≤ a) (hb : δ ^ 2 / 2 + c * δ ≤ b)
    (hmom : Integrable (fun ω => |Zτ ω| * Real.exp (a * |Tτ ω| + b * |τ ω|)) μ) :
    HasDerivAt
      (fun e : ℝ => ∫ ω, Zτ ω * Real.exp (-e * Tτ ω - (e ^ 2 / 2) * τ ω) ∂μ)
      (- ∫ ω, Zτ ω * Tτ ω ∂μ)
      0 := by
  have ha0 : 0 ≤ a := by linarith
  have hb0 : 0 ≤ b := by nlinarith
  exact hasDerivAt_integral_stoppedIntegrand_zero hZmeas hTmeas hτmeas
    (integrable_of_expMoment hZmeas ha0 hb0 hmom) hδ
    (integrable_explicitDominatingFunction_of_expMoment hZmeas hTmeas hτmeas
      hδ.le hc ha hb hmom)
    (hdom_explicitDominatingFunction Zτ Tτ τ hδ.le)

/-- **Gate 4, final theorem (split-moment form).**  Same conclusion from
`Zτ ∈ L²` and separate exponential moments of `Tτ` and of the stopping time
`τ`.  The exponential moment of `τ` is exactly what Gate 4D's abstract
forcing/geometric-tail results produce — see `integrable_exp_abs_of_le` and
`integrable_exp_of_geometric_tail`. -/
theorem hasDerivAt_integral_stoppedIntegrand_zero_of_separate_moments
    {Zτ Tτ τ : Ω → ℝ}
    (hZmeas : AEStronglyMeasurable Zτ μ)
    (hTmeas : AEStronglyMeasurable Tτ μ)
    (hτmeas : AEStronglyMeasurable τ μ)
    {δ c a b p q : ℝ} (hδ : 0 < δ) (hc : 0 < c)
    (ha : δ + c ≤ a) (hb : δ ^ 2 / 2 + c * δ ≤ b)
    (hp : 4 * a ≤ p) (hq : 4 * b ≤ q)
    (hZsq : Integrable (fun ω => Zτ ω ^ 2) μ)
    (hTexp : Integrable (fun ω => Real.exp (p * |Tτ ω|)) μ)
    (hτexp : Integrable (fun ω => Real.exp (q * |τ ω|)) μ) :
    HasDerivAt
      (fun e : ℝ => ∫ ω, Zτ ω * Real.exp (-e * Tτ ω - (e ^ 2 / 2) * τ ω) ∂μ)
      (- ∫ ω, Zτ ω * Tτ ω ∂μ)
      0 :=
  hasDerivAt_integral_stoppedIntegrand_zero_of_expMoment hZmeas hTmeas hτmeas hδ hc ha hb
    (integrable_absZ_mul_exp_of_separate hZmeas hTmeas hτmeas hp hq hZsq hTexp hτexp)

end RebaseguardLean
