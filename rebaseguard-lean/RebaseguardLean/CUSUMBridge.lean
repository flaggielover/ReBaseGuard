import RebaseguardLean.Domination

/-!
# Gate 4.5-A + 4.5-B: the ACTUAL two-sided ReBaseGuard CUSUM detector

Gate 4 (`Domination.lean`) closed the analytic side of the Gate 3 domination
hypothesis, but its CUSUM section was **one-sided** (`cusumStat`, `cusumAlarm`)
and used a strict `> h` alarm.  The real ReBaseGuard detector is two-sided:

```
S₀⁺ = S₀⁻ = 0
Sₙ₊₁⁺ = max 0 (Sₙ⁺ + Xₙ - k)
Sₙ₊₁⁻ = max 0 (Sₙ⁻ - Xₙ - k)
alarm  ⟺  max (Sₙ⁺, Sₙ⁻) ≥ h            -- NOTE: `≥`, not `>`
```
with the frozen constants `k = 1/2`, `h = 5`.  This file rebuilds that detector
faithfully and connects it to the abstract geometric-tail machinery of Gate 4.

## Gate 4.5-A
* `cusumPair`, `cusumMax` — the two-sided recursion.
* `measurable_cusumPair`, `measurable_cusumMax` — measurability by induction.
* `cusumTau` — the alarm time, built with mathlib's `hittingAfter` on `Set.Ici h`
  (so the alarm semantics is literally `≥ h`).
* `isStoppingTime_cusumTau` — a genuine stopping time.
* `cusumTau_le_of_lt` — the real two-sided forcing bound.

## Gate 4.5-B
* `measure_noForcing_le_pow` — independence + a uniform failure bound gives a
  geometric tail (Route B3; no product space is constructed).
* `measure_le_forcingNat_le_pow` — the same tail for the forcing time.
* `measure_never_forced_eq_zero` — forcing happens a.s. when `q < 1`.
* `integrable_exp_forcingNat` — the exponential moment, via the already
  kernel-accepted `measure_eq_le_of_tail_le` / `integrable_exp_of_geometric_tail`.
* `ae_cusumTau_le_forcingNat_succ` — `τ ≤ N + 1` a.e., the semantic bridge.

## Explicitly NOT done here (Gate 4.5-C)
No identification of `Zτ`/`Tτ`, no stopped random walk, no exponential moment of
`Tτ`, no optional stopping, no Wald identities, and nothing about `Γ > 2`.

## Semantic note on `WithTop ℕ`
`cusumTau` is `WithTop ℕ`-valued and is **never** silently coerced to `ℕ`.
The `ℕ`-valued object used for the exponential moment is the *forcing time*
`forcingNat`, whose `sInf` junk value `0` on the never-forced event is harmless
because `measure_never_forced_eq_zero` shows that event is null.
-/

noncomputable section

open MeasureTheory ProbabilityTheory Filter
open scoped ENNReal

namespace RebaseguardLean

variable {Ω : Type*} [mΩ : MeasurableSpace Ω]

/-! ## Gate 4.5-A — the two-sided detector -/

/-- The two arms of the ReBaseGuard CUSUM, driven by the score process `X`:
`S₀ = (0,0)` and `Sₙ₊₁ = (max 0 (Sₙ⁺ + Xₙ - k), max 0 (Sₙ⁻ - Xₙ - k))`. -/
def cusumPair (k : ℝ) (X : ℕ → Ω → ℝ) : ℕ → Ω → ℝ × ℝ
  | 0 => fun _ => (0, 0)
  | n + 1 => fun ω =>
      (max 0 ((cusumPair k X n ω).1 + X n ω - k),
       max 0 ((cusumPair k X n ω).2 - X n ω - k))

omit mΩ in
@[simp] lemma cusumPair_zero (k : ℝ) (X : ℕ → Ω → ℝ) (ω : Ω) :
    cusumPair k X 0 ω = (0, 0) := rfl

omit mΩ in
@[simp] lemma cusumPair_succ (k : ℝ) (X : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) :
    cusumPair k X (n + 1) ω =
      (max 0 ((cusumPair k X n ω).1 + X n ω - k),
       max 0 ((cusumPair k X n ω).2 - X n ω - k)) := rfl

/-- The detector statistic `max (S⁺, S⁻)`. -/
def cusumMax (k : ℝ) (X : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) : ℝ :=
  max (cusumPair k X n ω).1 (cusumPair k X n ω).2

omit mΩ in
lemma cusumPair_fst_nonneg (k : ℝ) (X : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) :
    0 ≤ (cusumPair k X n ω).1 := by
  cases n with
  | zero => exact le_refl 0
  | succ m => rw [cusumPair_succ]; exact le_max_left _ _

/-! ### A1 — measurability -/

theorem measurable_cusumPair (k : ℝ) (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) :
    ∀ n, Measurable (fun ω => (cusumPair k X n ω).1) ∧
         Measurable (fun ω => (cusumPair k X n ω).2) := by
  intro n
  induction n with
  | zero => exact ⟨measurable_const, measurable_const⟩
  | succ m ih =>
      refine ⟨?_, ?_⟩
      · show Measurable fun ω => max 0 ((cusumPair k X m ω).1 + X m ω - k)
        exact measurable_const.max ((ih.1.add (hX m)).sub measurable_const)
      · show Measurable fun ω => max 0 ((cusumPair k X m ω).2 - X m ω - k)
        exact measurable_const.max ((ih.2.sub (hX m)).sub measurable_const)

theorem measurable_cusumMax (k : ℝ) (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n))
    (n : ℕ) : Measurable (cusumMax k X n) :=
  (measurable_cusumPair k X hX n).1.max (measurable_cusumPair k X hX n).2

theorem stronglyMeasurable_cusumMax (k : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (n : ℕ) : StronglyMeasurable (cusumMax k X n) :=
  (measurable_cusumMax k X hX n).stronglyMeasurable

/-! ### A2 — filtration, adaptedness, stopping time -/

/-- The natural filtration of the detector statistic.  The audit established that
this suffices for Gate 4.5; the full innovation filtration is not built. -/
def cusumFiltration (k : ℝ) (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) :
    Filtration ℕ mΩ :=
  Filtration.natural (cusumMax k X) (stronglyMeasurable_cusumMax k X hX)

theorem adapted_cusumMax (k : ℝ) (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) :
    Adapted (cusumFiltration k X hX) (cusumMax k X) :=
  (Filtration.stronglyAdapted_natural (stronglyMeasurable_cusumMax k X hX)).adapted

/-- **The ReBaseGuard alarm time.**  `Set.Ici h = {x | h ≤ x}`, so this is exactly
`inf {n ≥ 1 : max (Sₙ⁺, Sₙ⁻) ≥ h}`.  It is `WithTop ℕ`-valued: `⊤` encodes
"never alarms", and is never silently coerced away. -/
def cusumTau (k h : ℝ) (X : ℕ → Ω → ℝ) : Ω → WithTop ℕ :=
  hittingAfter (cusumMax k X) (Set.Ici h) 1

/-- **Gate 4.5-A2.**  `cusumTau` is a genuine stopping time. -/
theorem isStoppingTime_cusumTau (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) :
    IsStoppingTime (cusumFiltration k X hX) (cusumTau k h X) :=
  (adapted_cusumMax k X hX).isStoppingTime_hittingAfter measurableSet_Ici

/-! ### A3 — event measurability -/

theorem measurableSet_cusumTau_eq (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (n : ℕ) :
    MeasurableSet {ω | cusumTau k h X ω = (n : WithTop ℕ)} :=
  (cusumFiltration k X hX).le n _
    ((isStoppingTime_cusumTau k h X hX).measurableSet_eq_of_countable n)

theorem measurableSet_cusumTau_le (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (n : ℕ) :
    MeasurableSet {ω | cusumTau k h X ω ≤ (n : WithTop ℕ)} :=
  (cusumFiltration k X hX).le n _
    ((isStoppingTime_cusumTau k h X hX).measurableSet_le n)

/-! ### A4 — the real two-sided forcing lemma -/

omit mΩ in
/-- One score above `h + k` drives the **positive** arm above `h`. -/
lemma lt_cusumPair_fst_succ (k h : ℝ) (X : ℕ → Ω → ℝ) {n : ℕ} {ω : Ω}
    (hz : h + k < X n ω) : h < (cusumPair k X (n + 1) ω).1 := by
  have h0 : 0 ≤ (cusumPair k X n ω).1 := cusumPair_fst_nonneg k X n ω
  have hlt : h < (cusumPair k X n ω).1 + X n ω - k := by linarith
  rw [cusumPair_succ]
  exact lt_of_lt_of_le hlt (le_max_right _ _)

omit mΩ in
/-- Hence the two-sided statistic `max (S⁺, S⁻)` is above `h`. -/
lemma lt_cusumMax_succ (k h : ℝ) (X : ℕ → Ω → ℝ) {n : ℕ} {ω : Ω}
    (hz : h + k < X n ω) : h < cusumMax k X (n + 1) ω :=
  lt_of_lt_of_le (lt_cusumPair_fst_succ k h X hz) (le_max_left _ _)

omit mΩ in
/-- **Gate 4.5-A4.**  The real pathwise forcing bound for the two-sided detector:
a single score above `H = h + k` forces an alarm by time `n + 1`.  The forcing
gives `> h`, which is more than enough for the `≥ h` alarm condition. -/
theorem cusumTau_le_of_lt (k h : ℝ) (X : ℕ → Ω → ℝ) {n : ℕ} {ω : Ω}
    (hz : h + k < X n ω) :
    cusumTau k h X ω ≤ ((n + 1 : ℕ) : WithTop ℕ) :=
  hittingAfter_le_of_mem (Nat.le_add_left 1 n)
    (Set.mem_Ici.mpr (lt_cusumMax_succ k h X hz).le)


/-! ## Gate 4.5-B — independence ⇒ geometric tail ⇒ exponential moment

Route B3: a reusable theorem under independence hypotheses.  No explicit
infinite product probability space is constructed. -/

/-- The event "no score exceeded `H` during the first `k` trials". -/
def noForcing (H : ℝ) (X : ℕ → Ω → ℝ) (k : ℕ) : Set Ω :=
  ⋂ j ∈ Finset.range k, {ω | X j ω ≤ H}

omit mΩ in
lemma mem_noForcing_iff (H : ℝ) (X : ℕ → Ω → ℝ) (k : ℕ) (ω : Ω) :
    ω ∈ noForcing H X k ↔ ∀ j < k, X j ω ≤ H := by
  constructor
  · intro hmem j hj
    exact Set.mem_iInter₂.mp hmem j (Finset.mem_range.mpr hj)
  · intro hall
    exact Set.mem_iInter₂.mpr fun j hj => hall j (Finset.mem_range.mp hj)

lemma measurableSet_noForcing (H : ℝ) (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n))
    (k : ℕ) : MeasurableSet (noForcing H X k) :=
  Finset.measurableSet_biInter _ fun j _ => measurableSet_le (hX j) measurable_const

/-! ### B1 — the geometric tail from independence -/

/-- **Gate 4.5-B1.**  If the scores are independent and each has failure
probability at most `q`, then failing `k` times in a row has probability at most
`q ^ k`.  The failure events are preimages of `Set.Iic H`, so no complement
manipulation of `iIndepSet` is needed. -/
theorem measure_noForcing_le_pow {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hindep : iIndepFun X μ) {H : ℝ} {q : ℝ≥0∞}
    (hq : ∀ j, μ {ω | X j ω ≤ H} ≤ q) (k : ℕ) :
    μ (noForcing H X k) ≤ q ^ k := by
  have hprod : μ (noForcing H X k) = ∏ j ∈ Finset.range k, μ {ω | X j ω ≤ H} :=
    hindep.meas_biInter fun i _ => ⟨Set.Iic H, measurableSet_Iic, rfl⟩
  rw [hprod]
  calc ∏ j ∈ Finset.range k, μ {ω | X j ω ≤ H}
      ≤ ∏ _j ∈ Finset.range k, q := Finset.prod_le_prod' fun j _ => hq j
    _ = q ^ k := by simp

/-! ### B2 — the forcing time and its tail

The forcing time reuses the Gate 4 pathwise definition `forcingTime`, so there
is only one notion of "first score above `H`" in the development. -/

/-- The forcing time as a random variable: `forcingNat H X ω = inf {n | H < Xₙ ω}`,
literally the Gate 4 `forcingTime` applied to the path `n ↦ Xₙ ω`. -/
def forcingNat (H : ℝ) (X : ℕ → Ω → ℝ) (ω : Ω) : ℕ :=
  forcingTime H (fun n => X n ω)

omit mΩ in
lemma forcingNat_le_of_lt (H : ℝ) (X : ℕ → Ω → ℝ) {n : ℕ} {ω : Ω}
    (hn : H < X n ω) : forcingNat H X ω ≤ n :=
  Nat.sInf_le hn

omit mΩ in
lemma lt_of_forcingNat (H : ℝ) (X : ℕ → Ω → ℝ) {ω : Ω}
    (hex : ∃ n, H < X n ω) : H < X (forcingNat H X ω) ω :=
  Nat.sInf_mem hex

omit mΩ in
lemma tail_subset_noForcing (H : ℝ) (X : ℕ → Ω → ℝ) (k : ℕ) :
    {ω | k ≤ forcingNat H X ω} ⊆ noForcing H X k := by
  intro ω hω
  rw [mem_noForcing_iff]
  intro j hj
  by_contra hc
  push_neg at hc
  have hle : forcingNat H X ω ≤ j := forcingNat_le_of_lt H X hc
  have hk : k ≤ forcingNat H X ω := hω
  omega

/-- **Gate 4.5-B2.**  The geometric tail of the forcing time. -/
theorem measure_le_forcingNat_le_pow {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hindep : iIndepFun X μ) {H : ℝ} {q : ℝ≥0∞}
    (hq : ∀ j, μ {ω | X j ω ≤ H} ≤ q) (k : ℕ) :
    μ {ω | k ≤ forcingNat H X ω} ≤ q ^ k :=
  le_trans (measure_mono (tail_subset_noForcing H X k))
    (measure_noForcing_le_pow X hindep hq k)

/-! ### B2' — forcing happens almost surely -/

omit mΩ in
lemma never_forced_subset_noForcing (H : ℝ) (X : ℕ → Ω → ℝ) (k : ℕ) :
    {ω | ∀ n, X n ω ≤ H} ⊆ noForcing H X k := by
  intro ω hω
  rw [mem_noForcing_iff]
  exact fun j _ => hω j

/-- **Gate 4.5-B2'.**  With a uniform failure bound `q < 1`, some score exceeds
`H` almost surely.  This is what makes the `sInf` junk value in `forcingNat`
harmless. -/
theorem measure_never_forced_eq_zero {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hindep : iIndepFun X μ) {H : ℝ} {q : ℝ≥0∞}
    (hq : ∀ j, μ {ω | X j ω ≤ H} ≤ q) (hq1 : q < 1) :
    μ {ω | ∀ n, X n ω ≤ H} = 0 := by
  have hle : ∀ k : ℕ, μ {ω | ∀ n, X n ω ≤ H} ≤ q ^ k := fun k =>
    le_trans (measure_mono (never_forced_subset_noForcing H X k))
      (measure_noForcing_le_pow X hindep hq k)
  have hlim : Tendsto (fun k : ℕ => q ^ k) atTop (nhds 0) :=
    ENNReal.tendsto_pow_atTop_nhds_zero_of_lt_one hq1
  have hzero : μ {ω | ∀ n, X n ω ≤ H} ≤ 0 := ge_of_tendsto hlim (Eventually.of_forall hle)
  exact le_antisymm hzero (by simp)

theorem ae_exists_forcing {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hindep : iIndepFun X μ) {H : ℝ} {q : ℝ≥0∞}
    (hq : ∀ j, μ {ω | X j ω ≤ H} ≤ q) (hq1 : q < 1) :
    ∀ᵐ ω ∂μ, ∃ n, H < X n ω := by
  have h0 := measure_never_forced_eq_zero X hindep hq hq1
  rw [ae_iff]
  refine measure_mono_null (fun ω hω => ?_) h0
  simp only [not_exists, not_lt] at hω
  exact hω

/-! ### B3 — measurability of the forcing time -/

omit mΩ in
lemma forcingNat_eq_iff (H : ℝ) (X : ℕ → Ω → ℝ) (ω : Ω) (m : ℕ) :
    forcingNat H X ω = m ↔
      ((H < X m ω ∧ ∀ j < m, X j ω ≤ H) ∨ (m = 0 ∧ ∀ n, X n ω ≤ H)) := by
  have hempty_of : (∀ n, X n ω ≤ H) → {n | H < X n ω} = ∅ := by
    intro hall
    ext n
    simp only [Set.mem_setOf_eq, Set.mem_empty_iff_false, iff_false, not_lt]
    exact hall n
  constructor
  · intro hm
    subst hm
    by_cases hne : ∃ n, H < X n ω
    · refine Or.inl ⟨lt_of_forcingNat H X hne, fun j hj => ?_⟩
      by_contra hc
      push_neg at hc
      exact absurd (forcingNat_le_of_lt H X hc) (not_le.mpr hj)
    · push_neg at hne
      refine Or.inr ⟨?_, hne⟩
      show sInf {n | H < X n ω} = 0
      rw [hempty_of hne]
      exact Nat.sInf_empty
  · rintro (⟨hm1, hm2⟩ | ⟨rfl, hall⟩)
    · refine le_antisymm (forcingNat_le_of_lt H X hm1) ?_
      by_contra hc
      push_neg at hc
      have hne : ∃ n, H < X n ω := ⟨m, hm1⟩
      exact absurd (hm2 _ hc) (not_le.mpr (lt_of_forcingNat H X hne))
    · show sInf {n | H < X n ω} = 0
      rw [hempty_of hall]
      exact Nat.sInf_empty

theorem measurable_forcingNat (H : ℝ) (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) :
    Measurable (forcingNat H X) := by
  have hall : MeasurableSet {ω | ∀ n, X n ω ≤ H} := by
    have hrw : {ω | ∀ n, X n ω ≤ H} = ⋂ n, {ω | X n ω ≤ H} := by
      ext ω
      simp only [Set.mem_iInter, Set.mem_setOf_eq]
    rw [hrw]
    exact MeasurableSet.iInter fun n => measurableSet_le (hX n) measurable_const
  refine measurable_to_countable' fun m => ?_
  have hbase : MeasurableSet ({ω | H < X m ω} ∩ noForcing H X m) :=
    (measurableSet_lt measurable_const (hX m)).inter (measurableSet_noForcing H X hX m)
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · have hset : forcingNat H X ⁻¹' {0}
        = ({ω | H < X 0 ω} ∩ noForcing H X 0) ∪ {ω | ∀ n, X n ω ≤ H} := by
      ext ω
      simp only [Set.mem_preimage, Set.mem_singleton_iff, Set.mem_union,
        Set.mem_inter_iff, Set.mem_setOf_eq]
      rw [forcingNat_eq_iff]
      constructor
      · rintro (⟨h1, h2⟩ | ⟨_, h3⟩)
        · exact Or.inl ⟨h1, (mem_noForcing_iff H X 0 ω).mpr h2⟩
        · exact Or.inr h3
      · rintro (⟨h1, h2⟩ | h3)
        · exact Or.inl ⟨h1, (mem_noForcing_iff H X 0 ω).mp h2⟩
        · exact Or.inr ⟨rfl, h3⟩
    rw [hset]
    exact hbase.union hall
  · have hset : forcingNat H X ⁻¹' {m} = {ω | H < X m ω} ∩ noForcing H X m := by
      ext ω
      simp only [Set.mem_preimage, Set.mem_singleton_iff, Set.mem_inter_iff,
        Set.mem_setOf_eq]
      rw [forcingNat_eq_iff]
      constructor
      · rintro (⟨h1, h2⟩ | ⟨h0, _⟩)
        · exact ⟨h1, (mem_noForcing_iff H X m ω).mpr h2⟩
        · omega
      · rintro ⟨h1, h2⟩
        exact Or.inl ⟨h1, (mem_noForcing_iff H X m ω).mp h2⟩
    rw [hset]
    exact hbase

/-! ### B3 — the exponential moment, via the Gate 4 machinery -/

/-- **Gate 4.5-B3.**  Independence plus a uniform failure bound `q = ofReal r`
gives a finite exponential moment for the forcing time, at every rate `b` with
`exp b * r < 1`.  This is exactly the hypothesis consumed by Gate 4's
`integrable_exp_abs_of_le`. -/
theorem integrable_exp_forcingNat {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) (hindep : iIndepFun X μ)
    {H r b : ℝ} (hr : 0 ≤ r)
    (hq : ∀ j, μ {ω | X j ω ≤ H} ≤ ENNReal.ofReal r)
    (hbr : Real.exp b * r < 1) :
    Integrable (fun ω => Real.exp (b * (forcingNat H X ω : ℝ))) μ := by
  have htail : ∀ n : ℕ, μ {ω | n ≤ forcingNat H X ω} ≤ ENNReal.ofReal (1 * r ^ n) := by
    intro n
    have h1 := measure_le_forcingNat_le_pow X hindep hq n
    have h2 : (ENNReal.ofReal r) ^ n = ENNReal.ofReal (1 * r ^ n) := by
      rw [one_mul, ← ENNReal.ofReal_pow hr]
    rw [← h2]
    exact h1
  exact integrable_exp_of_geometric_tail (measurable_forcingNat H X hX)
    zero_le_one hr hbr (fun n => measure_eq_le_of_tail_le htail n)

/-! ### The semantic bridge: the CUSUM alarm is dominated by the forcing time -/

omit mΩ in
/-- **Gate 4.5-B, pathwise bridge.**  `τ ≤ N + 1` for the real two-sided
detector, with `H = h + k`. -/
theorem cusumTau_le_forcingNat_succ (k h : ℝ) (X : ℕ → Ω → ℝ) {ω : Ω}
    (hex : ∃ n, h + k < X n ω) :
    cusumTau k h X ω ≤ ((forcingNat (h + k) X ω + 1 : ℕ) : WithTop ℕ) :=
  cusumTau_le_of_lt k h X (lt_of_forcingNat (h + k) X hex)

/-- **Gate 4.5-B, almost-sure bridge.**  Under independence and a uniform failure
bound `q < 1`, the real two-sided CUSUM alarm time is almost surely dominated by
`forcingNat + 1`, whose exponential moments are supplied by
`integrable_exp_forcingNat`. -/
theorem ae_cusumTau_le_forcingNat_succ {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hindep : iIndepFun X μ) {q : ℝ≥0∞}
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ q) (hq1 : q < 1) :
    ∀ᵐ ω ∂μ, cusumTau k h X ω ≤ ((forcingNat (h + k) X ω + 1 : ℕ) : WithTop ℕ) := by
  filter_upwards [ae_exists_forcing X hindep hq hq1] with ω hω
  exact cusumTau_le_forcingNat_succ k h X hω

/-- The alarm time is almost surely finite. -/
theorem ae_cusumTau_ne_top {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hindep : iIndepFun X μ) {q : ℝ≥0∞}
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ q) (hq1 : q < 1) :
    ∀ᵐ ω ∂μ, cusumTau k h X ω ≠ ⊤ := by
  filter_upwards [ae_cusumTau_le_forcingNat_succ k h X hindep hq hq1] with ω hω
  intro htop
  rw [htop] at hω
  exact absurd hω (by simp)

end RebaseguardLean
