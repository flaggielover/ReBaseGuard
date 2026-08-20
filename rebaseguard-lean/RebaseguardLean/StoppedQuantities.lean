import RebaseguardLean.CUSUMBridge

/-!
# Gate 4.5-C1: the actual stopped quantities `Zτ`, `Tτ`, `τR`

Gate 3 (`IntegralBridge.lean`) treats `Zτ Tτ τ : Ω → ℝ` as arbitrary unrelated
functions.  This file removes that abstraction: all three are *constructed* from
the score process `X` and the genuine two-sided CUSUM alarm time
`cusumTau k h X` of Gate 4.5-A.

## The indexing convention (derived, not assumed)

`CUSUMBridge.cusumPair` is defined by `Sₙ₊₁ = f (Sₙ, Xₙ)`: the transition
`n → n+1` consumes `X n`.  Matching the frozen model
`S_t = max (0, S_{t-1} + Z_t - k)` at `t = n + 1` forces

  `Z_t = X_{t-1}`,  equivalently  `X n = Z_{n+1}`.

Hence, with the SAME index on the statistic and the alarm time,

* `cusumPair k X n` is the mathematical `S_n`;
* `cusumTau k h X` is the mathematical `τ`;
* `T_t = Σ_{s=1}^t Z_s = Σ_{j=0}^{t-1} X_j = ∑ j ∈ Finset.range t, X j`;
* `Z_τ = X_{τ-1}`.

**Warning.**  The pre-implementation sketch `T n = ∑ s ∈ Finset.Icc 1 n, X s` is
off by one under this convention and is deliberately *not* used.  The convention
is pinned down by `walk_succ`, `walk_eq_sum_innov` and `innov_succ` below.

## Handling of `⊤`

`stoppedValue u τ ω = u (τ ω).untopA ω`, and `WithTop.untopA` is by definition
`WithTop.untopD (Classical.arbitrary _)`.  So on `{τ = ⊤}` the stopped value is
an **unspecified** element — it is *not* provably `0`, and nothing here pretends
otherwise.  The fallback is confined to a null set by CUSUMBridge's
`ae_cusumTau_ne_top`; see `ae_exists_succ_cusumTau` and
`ae_cusumTauReal_eq_of_eq_coe` below.

## Scope
This is C1 only: construction + measurability + semantic identification.
No exponential moment for `Tτ` (that is C2), no optional stopping, no Wald
identities, no product space, and no instantiation of the Gate 3 identity.
-/

noncomputable section

open MeasureTheory ProbabilityTheory Filter
open scoped ENNReal

namespace RebaseguardLean

variable {Ω : Type*} [mΩ : MeasurableSpace Ω]

/-! ## C1-A — the innovation and cumulative-walk processes -/

/-- The mathematical innovation process `Z_t`.  Under the CUSUMBridge convention
`Z_t = X_{t-1}`, so `innov X (n+1) = X n`.  There is no zeroth innovation;
`innov X 0` is set to `0`, consistently with `T_0 = 0`. -/
def innov (X : ℕ → Ω → ℝ) : ℕ → Ω → ℝ
  | 0 => fun _ => 0
  | n + 1 => X n

omit mΩ in
@[simp] lemma innov_zero (X : ℕ → Ω → ℝ) : innov X 0 = fun _ => 0 := rfl

omit mΩ in
@[simp] lemma innov_succ (X : ℕ → Ω → ℝ) (n : ℕ) : innov X (n + 1) = X n := rfl

/-- The cumulative innovation process `T_t = Σ_{s=1}^t Z_s`.  Under the
CUSUMBridge convention this is `∑ j ∈ Finset.range t, X j`. -/
def walk (X : ℕ → Ω → ℝ) (n : ℕ) : Ω → ℝ := fun ω => ∑ j ∈ Finset.range n, X j ω

omit mΩ in
@[simp] lemma walk_zero (X : ℕ → Ω → ℝ) : walk X 0 = fun _ => 0 := by
  funext ω; simp [walk]

omit mΩ in
/-- The defining recurrence `T_{n+1} = T_n + X_n`. -/
lemma walk_succ (X : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) :
    walk X (n + 1) ω = walk X n ω + X n ω := by
  simp [walk, Finset.sum_range_succ]

omit mΩ in
/-- **Convention check.**  The recurrence in innovation form: `T_{n+1} = T_n + Z_{n+1}`. -/
lemma walk_succ_innov (X : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) :
    walk X (n + 1) ω = walk X n ω + innov X (n + 1) ω :=
  walk_succ X n ω

omit mΩ in
/-- **Convention check.**  `T_n = Z_1 + Z_2 + … + Z_n`, written with `s` ranging
over `Finset.range n` via `s ↦ s + 1`. -/
lemma walk_eq_sum_innov (X : ℕ → Ω → ℝ) (n : ℕ) (ω : Ω) :
    walk X n ω = ∑ s ∈ Finset.range n, innov X (s + 1) ω :=
  Finset.sum_congr rfl fun s _ => rfl

theorem measurable_innov (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) (n : ℕ) :
    Measurable (innov X n) := by
  cases n with
  | zero => exact measurable_const
  | succ m => exact hX m

theorem measurable_walk (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) (n : ℕ) :
    Measurable (walk X n) :=
  Finset.measurable_sum _ fun j _ => hX j

/-! ## C1-B — the stopped score and the stopped walk -/

/-- `Zτ`: the innovation at the alarm time, `Z_τ`. -/
def scoreAt (X : ℕ → Ω → ℝ) (τ : Ω → WithTop ℕ) : Ω → ℝ := stoppedValue (innov X) τ

/-- `Tτ`: the cumulative innovation through the alarm time, `T_τ`. -/
def walkAt (X : ℕ → Ω → ℝ) (τ : Ω → WithTop ℕ) : Ω → ℝ := stoppedValue (walk X) τ

omit mΩ in
lemma scoreAt_apply (X : ℕ → Ω → ℝ) (τ : Ω → WithTop ℕ) (ω : Ω) :
    scoreAt X τ ω = innov X (τ ω).untopA ω := rfl

omit mΩ in
lemma walkAt_apply (X : ℕ → Ω → ℝ) (τ : Ω → WithTop ℕ) (ω : Ω) :
    walkAt X τ ω = walk X (τ ω).untopA ω := rfl

omit mΩ in
/-- **Semantic identification of `Zτ`.**  If the alarm fires at index `m + 1`,
the stopped score is `X m`, i.e. the mathematical `Z_{m+1}`. -/
lemma scoreAt_of_eq_coe (X : ℕ → Ω → ℝ) {τ : Ω → WithTop ℕ} {ω : Ω} {m : ℕ}
    (hτ : τ ω = ((m + 1 : ℕ) : WithTop ℕ)) :
    scoreAt X τ ω = X m ω := by
  rw [scoreAt_apply, hτ]
  rfl

omit mΩ in
/-- **Semantic identification of `Tτ`.**  If the alarm fires at index `m`, the
stopped walk is `X 0 + … + X (m-1)`, i.e. the mathematical `T_m`. -/
lemma walkAt_of_eq_coe (X : ℕ → Ω → ℝ) {τ : Ω → WithTop ℕ} {ω : Ω} {m : ℕ}
    (hτ : τ ω = (m : WithTop ℕ)) :
    walkAt X τ ω = ∑ j ∈ Finset.range m, X j ω := by
  rw [walkAt_apply, hτ]
  rfl

/-! ## C1-C — measurability of stopped values

The route is the minimal one identified by the feasibility audit: `ℕ` is
countable, `{ω | τ ω = n}` is measurable because `τ` is a stopping time, and the
stopped value is measurable on the resulting countable partition.  No
progressive-measurability infrastructure is used. -/

/-- Measurability of a stopped value, from measurability of the (`WithTop ℕ`-valued)
time and of each `u n`.  Proof by countable partition. -/
theorem measurable_stoppedValue_nat {u : ℕ → Ω → ℝ} (hu : ∀ n, Measurable (u n))
    {τ : Ω → WithTop ℕ} (hτ : Measurable τ) :
    Measurable (stoppedValue u τ) := by
  have hnat : Measurable (fun ω => (τ ω).untopA) := hτ.untopA
  intro t ht
  have hset : (stoppedValue u τ) ⁻¹' t
      = ⋃ n : ℕ, ({ω | (τ ω).untopA = n} ∩ (u n ⁻¹' t)) := by
    ext ω
    simp only [Set.mem_preimage, Set.mem_iUnion, Set.mem_inter_iff, Set.mem_setOf_eq]
    constructor
    · intro hω
      exact ⟨(τ ω).untopA, rfl, hω⟩
    · rintro ⟨n, rfl, hn⟩
      exact hn
  rw [hset]
  exact MeasurableSet.iUnion fun n =>
    (hnat (measurableSet_singleton n)).inter (hu n ht)

/-- The alarm time is measurable as a `WithTop ℕ`-valued map. -/
theorem measurable_cusumTau (k h : ℝ) (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) :
    Measurable (cusumTau k h X) := by
  have htop : MeasurableSet {ω | cusumTau k h X ω = ⊤} := by
    have hrw : {ω | cusumTau k h X ω = ⊤}
        = (⋃ n : ℕ, {ω | cusumTau k h X ω = (n : WithTop ℕ)})ᶜ := by
      ext ω
      simp only [Set.mem_compl_iff, Set.mem_iUnion, Set.mem_setOf_eq, not_exists]
      constructor
      · intro hω n hn
        rw [hω] at hn
        exact absurd hn (by simp)
      · intro hω
        by_contra hne
        obtain ⟨n, hn⟩ := WithTop.ne_top_iff_exists.mp hne
        exact hω n hn.symm
    rw [hrw]
    exact (MeasurableSet.iUnion fun n => measurableSet_cusumTau_eq k h X hX n).compl
  refine measurable_to_countable' fun y => ?_
  cases y with
  | top => exact htop
  | coe n => exact measurableSet_cusumTau_eq k h X hX n

/-- **Gate 4.5-C1.**  `Zτ` is measurable. -/
theorem measurable_scoreAt_cusumTau (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) :
    Measurable (scoreAt X (cusumTau k h X)) :=
  measurable_stoppedValue_nat (measurable_innov X hX) (measurable_cusumTau k h X hX)

/-- **Gate 4.5-C1.**  `Tτ` is measurable. -/
theorem measurable_walkAt_cusumTau (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) :
    Measurable (walkAt X (cusumTau k h X)) :=
  measurable_stoppedValue_nat (measurable_walk X hX) (measurable_cusumTau k h X hX)

/-! ## C1-D — the real-valued alarm time -/

/-- `τR`: the real-valued alarm time.  On `{τ = ⊤}` this is
`((Classical.arbitrary ℕ : ℕ) : ℝ)` — an unspecified constant, made harmless
almost everywhere by `ae_cusumTau_ne_top`. -/
def cusumTauReal (k h : ℝ) (X : ℕ → Ω → ℝ) : Ω → ℝ :=
  fun ω => ((cusumTau k h X ω).untopA : ℝ)

/-- **Gate 4.5-C1.**  `τR` is measurable. -/
theorem measurable_cusumTauReal (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hX : ∀ n, Measurable (X n)) :
    Measurable (cusumTauReal k h X) :=
  (measurable_from_top.comp (measurable_cusumTau k h X hX).untopA : _)

omit mΩ in
/-- The alarm index is always at least `1`, so a finite alarm is at some `m + 1`
and `Z_τ = X_{τ-1}` is well defined. -/
theorem one_le_cusumTau (k h : ℝ) (X : ℕ → Ω → ℝ) (ω : Ω) :
    ((1 : ℕ) : WithTop ℕ) ≤ cusumTau k h X ω :=
  le_hittingAfter ω

omit mΩ in
/-- A finite alarm time is a successor. -/
theorem exists_succ_of_cusumTau_ne_top (k h : ℝ) (X : ℕ → Ω → ℝ) {ω : Ω}
    (hne : cusumTau k h X ω ≠ ⊤) :
    ∃ m : ℕ, cusumTau k h X ω = ((m + 1 : ℕ) : WithTop ℕ) := by
  obtain ⟨n, hn⟩ := WithTop.ne_top_iff_exists.mp hne
  have h1 : ((1 : ℕ) : WithTop ℕ) ≤ cusumTau k h X ω := one_le_cusumTau k h X ω
  rw [← hn] at h1
  have hne0 : n ≠ 0 := by
    rintro rfl
    simp at h1
  obtain ⟨m, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hne0
  exact ⟨m, hn.symm⟩

omit mΩ in
/-- On a finite alarm, `τR` is the alarm index. -/
theorem cusumTauReal_of_eq_coe (k h : ℝ) (X : ℕ → Ω → ℝ) {ω : Ω} {m : ℕ}
    (hτ : cusumTau k h X ω = (m : WithTop ℕ)) :
    cusumTauReal k h X ω = (m : ℝ) := by
  unfold cusumTauReal
  rw [hτ]
  rfl

/-! ## C1-E — almost-sure semantic identification, and the Gate 3 package

Under the Gate 4.5-B hypotheses (independence and a uniform failure bound
`q < 1`) the alarm is a.s. finite, so the `⊤` fallback in every definition above
is confined to a null set. -/

/-- Almost surely the alarm fires at a genuine successor index, so a.e.
`Zτ = X_{τ-1}`, `Tτ = ∑_{j < τ} X_j` and `τR = τ`. -/
theorem ae_exists_succ_cusumTau {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hindep : iIndepFun X μ) {q : ℝ≥0∞}
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ q) (hq1 : q < 1) :
    ∀ᵐ ω ∂μ, ∃ m : ℕ, cusumTau k h X ω = ((m + 1 : ℕ) : WithTop ℕ) := by
  filter_upwards [ae_cusumTau_ne_top k h X hindep hq hq1] with ω hω
  exact exists_succ_of_cusumTau_ne_top k h X hω

/-- Almost surely, the three stopped quantities are simultaneously given by their
finite-index formulas. -/
theorem ae_stopped_quantities_eq {μ : Measure Ω} (k h : ℝ) (X : ℕ → Ω → ℝ)
    (hindep : iIndepFun X μ) {q : ℝ≥0∞}
    (hq : ∀ j, μ {ω | X j ω ≤ h + k} ≤ q) (hq1 : q < 1) :
    ∀ᵐ ω ∂μ, ∃ m : ℕ,
      scoreAt X (cusumTau k h X) ω = X m ω ∧
      walkAt X (cusumTau k h X) ω = ∑ j ∈ Finset.range (m + 1), X j ω ∧
      cusumTauReal k h X ω = ((m + 1 : ℕ) : ℝ) := by
  filter_upwards [ae_exists_succ_cusumTau k h X hindep hq hq1] with ω hω
  obtain ⟨m, hm⟩ := hω
  exact ⟨m, scoreAt_of_eq_coe X hm, walkAt_of_eq_coe X hm,
    cusumTauReal_of_eq_coe k h X hm⟩

/-! ### AEStronglyMeasurable forms, as consumed by Gate 3 / Gate 4 -/

theorem aestronglyMeasurable_scoreAt_cusumTau {μ : Measure Ω} (k h : ℝ)
    (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) :
    AEStronglyMeasurable (scoreAt X (cusumTau k h X)) μ :=
  (measurable_scoreAt_cusumTau k h X hX).aestronglyMeasurable

theorem aestronglyMeasurable_walkAt_cusumTau {μ : Measure Ω} (k h : ℝ)
    (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) :
    AEStronglyMeasurable (walkAt X (cusumTau k h X)) μ :=
  (measurable_walkAt_cusumTau k h X hX).aestronglyMeasurable

theorem aestronglyMeasurable_cusumTauReal {μ : Measure Ω} (k h : ℝ)
    (X : ℕ → Ω → ℝ) (hX : ∀ n, Measurable (X n)) :
    AEStronglyMeasurable (cusumTauReal k h X) μ :=
  (measurable_cusumTauReal k h X hX).aestronglyMeasurable

end RebaseguardLean
