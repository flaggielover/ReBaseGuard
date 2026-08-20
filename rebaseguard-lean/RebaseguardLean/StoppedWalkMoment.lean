import RebaseguardLean.StoppedQuantities

/-!
# Gate 4.5-C2: exponential moment of the stopped walk `Tτ`

Target: `∃ a > 0, Integrable (fun ω => exp (a * |walkAt X (cusumTau k h X) ω|)) μ`.

## Strategy (Route C2-B), and why it is not circular

All assumptions are on the **one-step** variables `X j` (an exponential moment) plus
the Gate 4.5-B forcing probability `q`.  Nothing assumes any moment of `Tτ` itself,
and `τ` is nowhere assumed independent of the walk: the decomposition over the events
`{τ = m}` is exactly what avoids that false step.

  `∫ e^{a|Tτ|} = Σ_m ∫_{τ=m} e^{a|T_m|}`
  `∫_{τ=m} e^{a|T_m|} ≤ (∫ e^{2a|T_m|})^{1/2} · μ{τ=m}^{1/2}`   (Cauchy–Schwarz)
  `∫ e^{2a|T_m|} ≤ M^m`,  `μ{τ=m} ≤ q^{m-1}`
  ⇒ geometric series, convergent iff `M * q < 1`.

C2.1/C2.2 supply the two ingredients; C2.3 (below) performs the assembly and
reaches the **actual stopped walk** `walkAt X (cusumTau k h X)`.
-/

noncomputable section

open MeasureTheory ProbabilityTheory Filter
open scoped ENNReal

namespace RebaseguardLean

variable {Ω : Type*} [mΩ : MeasurableSpace Ω]

/-! ## C2.1 — deterministic-time exponential moment of the partial sum

`∫⁻ exp (a |T_m|) ≤ ∏_{j < m} ∫⁻ exp (a |X_j|)`.  Only independence of the `X j`
and the triangle inequality are used; no property of `τ` appears. -/

/-- The one-step integrand `ω ↦ exp (a * |X j ω|)`, as an `ℝ≥0∞`-valued function. -/
def expAbsScore (a : ℝ) (X : ℕ → Ω → ℝ) (j : ℕ) (ω : Ω) : ℝ≥0∞ :=
  ENNReal.ofReal (Real.exp (a * |X j ω|))

lemma measurable_expAbs_map (a : ℝ) :
    Measurable (fun x : ℝ => ENNReal.ofReal (Real.exp (a * |x|))) :=
  ENNReal.measurable_ofReal.comp
    (Real.measurable_exp.comp (measurable_abs.const_mul a))

lemma measurable_expAbsScore (a : ℝ) (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) (j : ℕ) :
    Measurable (expAbsScore a X j) :=
  (measurable_expAbs_map a).comp (hX j)

/-- Independence is inherited by the one-step exponential integrands. -/
lemma iIndepFun_expAbsScore {μ : Measure Ω} (a : ℝ) (X : ℕ → Ω → ℝ)
    (hindep : iIndepFun X μ) (hX : ∀ n, Measurable (X n)) :
    iIndepFun (expAbsScore a X) μ :=
  hindep.comp (fun _ x => ENNReal.ofReal (Real.exp (a * |x|)))
    (fun _ => measurable_expAbs_map a)

omit mΩ in
/-- Pointwise: `exp (a |T_m|) ≤ ∏_{j<m} exp (a |X_j|)` for `a ≥ 0`. -/
lemma expAbs_walk_le_prod {a : ℝ} (ha : 0 ≤ a) (X : ℕ → Ω → ℝ) (m : ℕ) (ω : Ω) :
    ENNReal.ofReal (Real.exp (a * |walk X m ω|))
      ≤ ∏ j ∈ Finset.range m, expAbsScore a X j ω := by
  have htri : |walk X m ω| ≤ ∑ j ∈ Finset.range m, |X j ω| :=
    Finset.abs_sum_le_sum_abs _ _
  have hmul : a * |walk X m ω| ≤ ∑ j ∈ Finset.range m, a * |X j ω| := by
    rw [← Finset.mul_sum]
    exact mul_le_mul_of_nonneg_left htri ha
  have hexp : Real.exp (a * |walk X m ω|)
      ≤ ∏ j ∈ Finset.range m, Real.exp (a * |X j ω|) := by
    rw [← Real.exp_sum]
    exact Real.exp_le_exp.mpr hmul
  calc ENNReal.ofReal (Real.exp (a * |walk X m ω|))
      ≤ ENNReal.ofReal (∏ j ∈ Finset.range m, Real.exp (a * |X j ω|)) :=
        ENNReal.ofReal_le_ofReal hexp
    _ = ∏ j ∈ Finset.range m, expAbsScore a X j ω := by
        unfold expAbsScore
        exact ENNReal.ofReal_prod_of_nonneg fun j _ => (Real.exp_nonneg _)

/-- **Gate 4.5-C2.1.**  Deterministic-time exponential moment of the partial sum,
factorised over the independent increments. -/
theorem lintegral_expAbs_walk_le_prod {μ : Measure Ω} {a : ℝ} (ha : 0 ≤ a)
    (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ) (m : ℕ) :
    ∫⁻ ω, ENNReal.ofReal (Real.exp (a * |walk X m ω|)) ∂μ
      ≤ ∏ j ∈ Finset.range m, ∫⁻ ω, expAbsScore a X j ω ∂μ := by
  calc ∫⁻ ω, ENNReal.ofReal (Real.exp (a * |walk X m ω|)) ∂μ
      ≤ ∫⁻ ω, ∏ j ∈ Finset.range m, expAbsScore a X j ω ∂μ :=
        lintegral_mono fun ω => expAbs_walk_le_prod ha X m ω
    _ = ∏ j ∈ Finset.range m, ∫⁻ ω, expAbsScore a X j ω ∂μ :=
        lintegral_prod_eq_prod_lintegral_of_indepFun _ _
          (iIndepFun_expAbsScore a X hindep hX) (measurable_expAbsScore a X hX)

/-- With a uniform one-step bound `M`, the deterministic-time moment is `≤ M ^ m`. -/
theorem lintegral_expAbs_walk_le_pow {μ : Measure Ω} {a : ℝ} (ha : 0 ≤ a)
    (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {M : ℝ≥0∞} (hM : ∀ j, ∫⁻ ω, expAbsScore a X j ω ∂μ ≤ M) (m : ℕ) :
    ∫⁻ ω, ENNReal.ofReal (Real.exp (a * |walk X m ω|)) ∂μ ≤ M ^ m := by
  refine le_trans (lintegral_expAbs_walk_le_prod ha X hX hindep m) ?_
  calc ∏ j ∈ Finset.range m, ∫⁻ ω, expAbsScore a X j ω ∂μ
      ≤ ∏ _j ∈ Finset.range m, M := Finset.prod_le_prod' fun j _ => hM j
    _ = M ^ m := by simp

/-! ## C2.2 — pmf bound for the actual two-sided CUSUM alarm time

`μ {τ = m} ≤ q ^ (m - 1)`, obtained from the Gate 4.5-A forcing lemma and the
Gate 4.5-B geometric tail.  No independence between `τ` and the walk is used. -/

omit mΩ in
/-- Pathwise: if the alarm fires exactly at `m`, no score before index `m - 1`
can have exceeded `h + k`. -/
lemma cusumTau_eq_subset_noForcing (k h : ℝ) (X : ℕ → Ω → ℝ) (m : ℕ) :
    {ω | cusumTau k h X ω = (m : WithTop ℕ)} ⊆ noForcing (h + k) X (m - 1) := by
  intro ω hω
  rw [mem_noForcing_iff]
  intro j hj
  by_contra hc
  push_neg at hc
  have hle : cusumTau k h X ω ≤ ((j + 1 : ℕ) : WithTop ℕ) := cusumTau_le_of_lt k h X hc
  rw [(by exact hω : cusumTau k h X ω = (m : WithTop ℕ))] at hle
  have hnat : m ≤ j + 1 := by exact_mod_cast hle
  omega

/-- **Gate 4.5-C2.2.**  Geometric pmf bound for the actual alarm time. -/
theorem measure_cusumTau_eq_le_pow {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hindep : iIndepFun X μ) {q : ℝ≥0∞}
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ q) (m : ℕ) :
    μ {ω | cusumTau k h X ω = (m : WithTop ℕ)} ≤ q ^ (m - 1) :=
  le_trans (measure_mono (cusumTau_eq_subset_noForcing k h X m))
    (measure_noForcing_le_pow X hindep hq (m - 1))

/-! ## C2.3 — assembly: from the slices to the actual stopped walk

### Scalar helpers -/

lemma ennreal_rpow_two_eq_pow (x : ℝ≥0∞) : x ^ (2 : ℝ) = x ^ (2 : ℕ) := by
  rw [← ENNReal.rpow_natCast x 2]
  norm_num

lemma ennreal_sq_rpow_half (x : ℝ≥0∞) : (x ^ (2 : ℕ)) ^ ((1 : ℝ) / 2) = x := by
  rw [← ENNReal.rpow_natCast x 2, ← ENNReal.rpow_mul]
  norm_num

omit mΩ in
lemma sq_ofReal_exp (y : ℝ) :
    (ENNReal.ofReal (Real.exp y)) ^ (2 : ℕ) = ENNReal.ofReal (Real.exp (2 * y)) := by
  rw [← ENNReal.ofReal_pow (Real.exp_nonneg y), pow_two, ← Real.exp_add]
  congr 2
  ring

/-- **Cauchy–Schwarz slice bound.**  If `∫⁻ f² ≤ A²` and `μ s ≤ B²` then
`∫⁻_s f ≤ A * B`.  This is where the `{τ = m}` indicator is handled *without*
any independence between `τ` and the walk. -/
lemma setLIntegral_le_of_sq_le {μ : Measure Ω} {s : Set Ω} (hs : MeasurableSet s)
    {f : Ω → ℝ≥0∞} (hf : AEMeasurable f μ) {A B : ℝ≥0∞}
    (hA : ∫⁻ ω, (f ω) ^ (2 : ℕ) ∂μ ≤ A ^ (2 : ℕ))
    (hB : μ s ≤ B ^ (2 : ℕ)) :
    ∫⁻ ω in s, f ω ∂μ ≤ A * B := by
  set ind : Ω → ℝ≥0∞ := s.indicator (fun _ => (1 : ℝ≥0∞)) with hind_def
  have hind_meas : AEMeasurable ind μ :=
    ((measurable_const : Measurable (fun _ : Ω => (1 : ℝ≥0∞))).indicator hs).aemeasurable
  have hprod : ∫⁻ ω in s, f ω ∂μ = ∫⁻ ω, (f * ind) ω ∂μ := by
    rw [← lintegral_indicator hs]
    congr 1
    funext ω
    by_cases hω : ω ∈ s <;> simp [hind_def, hω]
  rw [hprod]
  refine le_trans
    (ENNReal.lintegral_mul_le_Lp_mul_Lq μ Real.HolderConjugate.two_two hf hind_meas) ?_
  have h1 : (∫⁻ ω, (f ω) ^ (2 : ℝ) ∂μ) ^ ((1 : ℝ) / 2) ≤ A := by
    calc (∫⁻ ω, (f ω) ^ (2 : ℝ) ∂μ) ^ ((1 : ℝ) / 2)
        = (∫⁻ ω, (f ω) ^ (2 : ℕ) ∂μ) ^ ((1 : ℝ) / 2) := by
          simp_rw [ennreal_rpow_two_eq_pow]
      _ ≤ (A ^ (2 : ℕ)) ^ ((1 : ℝ) / 2) := ENNReal.rpow_le_rpow hA (by norm_num)
      _ = A := ennreal_sq_rpow_half A
  have hindsq : ∀ ω, (ind ω) ^ (2 : ℕ) = ind ω := by
    intro ω
    by_cases hω : ω ∈ s <;> simp [hind_def, hω]
  have h2 : (∫⁻ ω, (ind ω) ^ (2 : ℝ) ∂μ) ^ ((1 : ℝ) / 2) ≤ B := by
    calc (∫⁻ ω, (ind ω) ^ (2 : ℝ) ∂μ) ^ ((1 : ℝ) / 2)
        = (∫⁻ ω, ind ω ∂μ) ^ ((1 : ℝ) / 2) := by
          simp_rw [ennreal_rpow_two_eq_pow, hindsq]
      _ = (μ s) ^ ((1 : ℝ) / 2) := by
          rw [hind_def, lintegral_indicator hs]
          simp
      _ ≤ (B ^ (2 : ℕ)) ^ ((1 : ℝ) / 2) := ENNReal.rpow_le_rpow hB (by norm_num)
      _ = B := ennreal_sq_rpow_half B
  exact mul_le_mul' h1 h2

/-! ### The `{τ = m}` slice estimate -/

/-- **C2.3 slice bound.**  On the event `{τ = m}` the stopped walk *is* the
deterministic walk `T_m`, and Cauchy–Schwarz combines C2.1 with C2.2. -/
lemma lintegral_slice_expAbs_walkAt_le {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {a : ℝ} (ha : 0 ≤ a) {c d : ℝ≥0∞}
    (hM : ∀ j, ∫⁻ ω, expAbsScore (2 * a) X j ω ∂μ ≤ c ^ (2 : ℕ))
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ d ^ (2 : ℕ))
    (m : ℕ) :
    ∫⁻ ω in {ω | cusumTau k h X ω = (m : WithTop ℕ)},
        ENNReal.ofReal (Real.exp (a * |walkAt X (cusumTau k h X) ω| )) ∂μ
      ≤ c ^ m * d ^ (m - 1) := by
  have hs : MeasurableSet {ω | cusumTau k h X ω = (m : WithTop ℕ)} :=
    measurableSet_cusumTau_eq k h X hX m
  -- (1) on the slice the stopped walk is the deterministic walk
  have hcongr : ∫⁻ ω in {ω | cusumTau k h X ω = (m : WithTop ℕ)},
        ENNReal.ofReal (Real.exp (a * |walkAt X (cusumTau k h X) ω|)) ∂μ
      = ∫⁻ ω in {ω | cusumTau k h X ω = (m : WithTop ℕ)},
        ENNReal.ofReal (Real.exp (a * |walk X m ω|)) ∂μ := by
    refine lintegral_congr_ae ((ae_restrict_iff' hs).mpr (Filter.Eventually.of_forall ?_))
    intro ω hω
    show ENNReal.ofReal (Real.exp (a * |walkAt X (cusumTau k h X) ω|))
        = ENNReal.ofReal (Real.exp (a * |walk X m ω|))
    rw [walkAt_of_eq_coe X (by exact hω)]
    rfl
  rw [hcongr]
  -- (2) Cauchy-Schwarz
  refine setLIntegral_le_of_sq_le hs ?_ ?_ ?_
  · exact ((ENNReal.measurable_ofReal.comp (Real.measurable_exp.comp
      ((measurable_walk X hX m).abs.const_mul a)))).aemeasurable
  · -- square of the integrand is the 2a-integrand; apply C2.1
    have hsq : ∀ ω, (ENNReal.ofReal (Real.exp (a * |walk X m ω|))) ^ (2 : ℕ)
        = ENNReal.ofReal (Real.exp ((2 * a) * |walk X m ω|)) := by
      intro ω
      rw [sq_ofReal_exp]
      congr 2
      ring
    have hpow : (c ^ (2 : ℕ)) ^ m = (c ^ m) ^ (2 : ℕ) := by
      rw [← pow_mul, ← pow_mul, Nat.mul_comm]
    calc ∫⁻ ω, (ENNReal.ofReal (Real.exp (a * |walk X m ω|))) ^ (2 : ℕ) ∂μ
        = ∫⁻ ω, ENNReal.ofReal (Real.exp ((2 * a) * |walk X m ω|)) ∂μ := by
          simp_rw [hsq]
      _ ≤ (c ^ (2 : ℕ)) ^ m :=
          lintegral_expAbs_walk_le_pow (by linarith) X hX hindep hM m
      _ = (c ^ m) ^ (2 : ℕ) := hpow
  · have hpow : (d ^ (2 : ℕ)) ^ (m - 1) = (d ^ (m - 1)) ^ (2 : ℕ) := by
      rw [← pow_mul, ← pow_mul, Nat.mul_comm]
    calc μ {ω | cusumTau k h X ω = (m : WithTop ℕ)}
        ≤ (d ^ (2 : ℕ)) ^ (m - 1) := measure_cusumTau_eq_le_pow k h X hindep hq m
      _ = (d ^ (m - 1)) ^ (2 : ℕ) := hpow

/-! ### Partition over the alarm time

The `{τ = ⊤}` event is removed using CUSUMBridge's `ae_cusumTau_ne_top`; the
arbitrary `WithTop.untopA` fallback is therefore never given a meaningful value. -/

lemma lintegral_eq_tsum_slices {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {q : ℝ≥0∞} (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ q) (hq1 : q < 1)
    (f : Ω → ℝ≥0∞) :
    ∫⁻ ω, f ω ∂μ
      = ∑' m : ℕ, ∫⁻ ω in {ω | cusumTau k h X ω = (m : WithTop ℕ)}, f ω ∂μ := by
  have hmeas : ∀ m : ℕ, MeasurableSet {ω | cusumTau k h X ω = (m : WithTop ℕ)} :=
    fun m => measurableSet_cusumTau_eq k h X hX m
  have hdisj : Pairwise (Function.onFun Disjoint
      (fun m : ℕ => {ω | cusumTau k h X ω = (m : WithTop ℕ)})) := by
    intro m n hmn
    simp only [Function.onFun]
    rw [Set.disjoint_left]
    intro ω hm hn
    simp only [Set.mem_setOf_eq] at hm hn
    rw [hm] at hn
    exact hmn (by exact_mod_cast hn)
  have huniv : (Set.univ : Set Ω) =ᵐ[μ]
      ⋃ m : ℕ, {ω | cusumTau k h X ω = (m : WithTop ℕ)} := by
    rw [Filter.eventuallyEq_set]
    filter_upwards [ae_cusumTau_ne_top k h X hindep hq hq1] with ω hω
    simp only [Set.mem_univ, true_iff, Set.mem_iUnion, Set.mem_setOf_eq]
    obtain ⟨n, hn⟩ := WithTop.ne_top_iff_exists.mp hω
    exact ⟨n, hn.symm⟩
  calc ∫⁻ ω, f ω ∂μ
      = ∫⁻ ω in Set.univ, f ω ∂μ := by rw [Measure.restrict_univ]
    _ = ∫⁻ ω in ⋃ m : ℕ, {ω | cusumTau k h X ω = (m : WithTop ℕ)}, f ω ∂μ :=
        setLIntegral_congr huniv
    _ = ∑' m : ℕ, ∫⁻ ω in {ω | cusumTau k h X ω = (m : WithTop ℕ)}, f ω ∂μ :=
        lintegral_iUnion hmeas hdisj f

/-! ### The geometric majorant -/

/-- `∑ₘ cᵐ d^(m-1)` is finite exactly because `c * d < 1`: the `m = 0` term is `1`
and the `m = j+1` terms are `c * (c*d)^j`. -/
lemma tsum_geometric_majorant_ne_top {c d : ℝ≥0∞} (hc : c ≠ ⊤) (hcd : c * d < 1) :
    ∑' m : ℕ, c ^ m * d ^ (m - 1) ≠ ⊤ := by
  have hshift : ∀ j : ℕ, c ^ (j + 1) * d ^ ((j + 1) - 1) = c * (c * d) ^ j := by
    intro j
    rw [Nat.add_sub_cancel, pow_succ, mul_pow]
    ring
  rw [tsum_eq_zero_add' ENNReal.summable]
  simp only [hshift]
  rw [ENNReal.tsum_mul_left, ENNReal.tsum_geometric]
  have hne : (1 : ℝ≥0∞) - c * d ≠ 0 := (tsub_pos_of_lt hcd).ne'
  refine ENNReal.add_ne_top.mpr ⟨?_, ?_⟩
  · simp
  · exact ENNReal.mul_ne_top hc (ENNReal.inv_ne_top.mpr hne)

/-! ### C2.3 main results -/

/-- The stopped-walk exponential moment is finite (`ℝ≥0∞` form). -/
theorem lintegral_expAbs_walkAt_ne_top {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {a : ℝ} (ha : 0 ≤ a) {c d : ℝ≥0∞} (hc : c ≠ ⊤)
    (hM : ∀ j, ∫⁻ ω, expAbsScore (2 * a) X j ω ∂μ ≤ c ^ (2 : ℕ))
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ d ^ (2 : ℕ))
    (hd1 : d ^ (2 : ℕ) < 1) (hcd : c * d < 1) :
    ∫⁻ ω, ENNReal.ofReal (Real.exp (a * |walkAt X (cusumTau k h X) ω|)) ∂μ ≠ ⊤ := by
  rw [lintegral_eq_tsum_slices k h X hX hindep hq hd1]
  refine ne_top_of_le_ne_top (tsum_geometric_majorant_ne_top hc hcd) ?_
  exact ENNReal.tsum_le_tsum fun m =>
    lintegral_slice_expAbs_walkAt_le k h X hX hindep ha hM hq m

/-- **Gate 4.5-C2.3.**  The exponential moment of the **actual stopped walk**
`Tτ = walkAt X (cusumTau k h X)` at the actual two-sided ReBaseGuard CUSUM alarm
time, for a fixed `a`, under purely upstream hypotheses:

* `hX`, `hindep`  : the score family is measurable and independent;
* `hM`            : a **one-step** exponential moment bound at rate `2a`;
* `hq`            : the Gate 4.5-B uniform forcing bound;
* `hd1`, `hcd`    : the scalar convergence conditions (`hcd` is `c * d < 1`,
                    i.e. `√M · √q < 1`, equivalently `M * q < 1`).

No moment of `Tτ` is assumed, and `τ` is never assumed independent of the walk. -/
theorem integrable_exp_abs_walkAt_of_moment_tail {μ : Measure Ω} (k h : ℝ)
    (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {a : ℝ} (ha : 0 ≤ a) {c d : ℝ≥0∞} (hc : c ≠ ⊤)
    (hM : ∀ j, ∫⁻ ω, expAbsScore (2 * a) X j ω ∂μ ≤ c ^ (2 : ℕ))
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ d ^ (2 : ℕ))
    (hd1 : d ^ (2 : ℕ) < 1) (hcd : c * d < 1) :
    Integrable (fun ω => Real.exp (a * |walkAt X (cusumTau k h X) ω|)) μ := by
  have hmeas : Measurable (fun ω => Real.exp (a * |walkAt X (cusumTau k h X) ω|)) :=
    Real.measurable_exp.comp ((measurable_walkAt_cusumTau k h X hX).abs.const_mul a)
  refine ⟨hmeas.aestronglyMeasurable, ?_⟩
  rw [hasFiniteIntegral_iff_ofReal
    (Filter.Eventually.of_forall fun ω => Real.exp_nonneg _)]
  exact lt_top_iff_ne_top.mpr
    (lintegral_expAbs_walkAt_ne_top k h X hX hindep ha hc hM hq hd1 hcd)

end RebaseguardLean
