/-
Level-4 Priority-5 Lean spine: the deterministic skeleton algebra.

This file formalises exactly the *logical spine* of P5's local-vs-global
distinction, and nothing else.  It is deliberately abstract: it takes as input a
conditional-mean map written in the secant form that `DEFINITION_AUDIT.md` §5
and `THEOREM.md` T2 establish,

    M_rho(e) = rho * R(e),      R(e) = -(s e) * e,     s e > 0 for e /= 0,

and proves, with no numerics and no probability:

  * `fixedPoint_unique`     the origin is the ONLY fixed point for every rho > 0
                            (T8: no saddle-node / pitchfork / transcritical);
  * `twoCycle_iff`          symmetric 2-cycles are EXACTLY the solutions of
                            `rho * s e = 1` (T9);
  * `no_twoCycle_of_le_criticalRho`  none below the critical fraction;
  * `exists_twoCycle`       one above it, by the intermediate value theorem;
  * `twoCycle_unique_of_strictAntiOn`  exactly one, under strict monotonicity;
  * `abs_map_le` / `invariant_region` / `local_repulsion_with_global_bound`
                            a bounded map has a forward-invariant absorbing
                            region however large the multiplier at 0 is
                            (T12: local repulsion is not global instability);
  * `snr_le_of_small_amplitude`  an orbit whose amplitude is small against a
                            strictly positive noise floor has small
                            signal-to-noise ratio (T10).

The probabilistic theorems T1, T3-T7 and T11 are human-proved in `PROOF.md` and
are NOT formalised here; see `LIMITATIONS.md`.
-/
import Mathlib

namespace RebaseguardLean
namespace Priority5Skeleton

/-- A conditional-mean map in secant form: `R e = -(s e) * e` with `s` positive
away from the origin.  P5's measured maps satisfy this by (H1)+(H2). -/
structure SecantMap where
  s : ℝ → ℝ
  spos : ∀ ⦃e : ℝ⦄, e ≠ 0 → 0 < s e

namespace SecantMap

variable (M : SecantMap)

/-- The conditional-mean map `R`. -/
def R (e : ℝ) : ℝ := -(M.s e) * e

/-- The deterministic skeleton at reuse fraction `rho`. -/
def f (rho e : ℝ) : ℝ := rho * M.R e

@[simp] theorem R_zero : M.R 0 = 0 := by simp [R]

@[simp] theorem f_zero (rho : ℝ) : M.f rho 0 = 0 := by simp [f]

/-- **T8.** For every `rho > 0` the origin is the unique fixed point.  There is
no non-zero equilibrium, hence no saddle-node, transcritical or pitchfork
bifurcation in `rho`. -/
theorem fixedPoint_unique {rho e : ℝ} (hrho : 0 < rho) (h : M.f rho e = e) :
    e = 0 := by
  by_contra hne
  have hs : 0 < M.s e := M.spos hne
  have hpos : 0 < 1 + rho * M.s e := by positivity
  have hmul : e * (1 + rho * M.s e) = 0 := by
    have h' : rho * (-(M.s e) * e) = e := h
    linear_combination -h'
  exact hne ((mul_eq_zero.mp hmul).resolve_right hpos.ne')

/-- **T9 (characterisation).**  `{e, -e}` with `e /= 0` is a symmetric 2-cycle of
the skeleton iff `rho * s e = 1`. -/
theorem twoCycle_iff {rho e : ℝ} (he : e ≠ 0) :
    M.f rho e = -e ↔ rho * M.s e = 1 := by
  constructor
  · intro h
    have h' : rho * (-(M.s e) * e) = -e := h
    have hmul : (rho * M.s e - 1) * e = 0 := by linear_combination -h'
    rcases mul_eq_zero.mp hmul with h3 | h3
    · linarith
    · exact absurd h3 he
  · intro h
    show rho * (-(M.s e) * e) = -e
    linear_combination (-e) * h

/-- **T9 (below the boundary).**  If `s` is bounded by `S0` away from the origin
and `rho * S0 <= 1`, the skeleton has no symmetric 2-cycle at all. -/
theorem no_twoCycle_of_le_criticalRho {rho S0 : ℝ}
    (hS : ∀ ⦃e : ℝ⦄, e ≠ 0 → M.s e < S0) (hrho : 0 < rho)
    (hle : rho * S0 ≤ 1) {e : ℝ} (he : e ≠ 0) : M.f rho e ≠ -e := by
  intro h
  have h1 : rho * M.s e = 1 := (M.twoCycle_iff he).mp h
  have h2 : rho * M.s e < rho * S0 := mul_lt_mul_of_pos_left (hS he) hrho
  linarith

/-- The critical reuse fraction of the abstract map: `rho_c = 1 / S0`. -/
noncomputable def criticalRho (S0 : ℝ) : ℝ := 1 / S0

theorem mul_criticalRho_le_one {S0 rho : ℝ} (hS0 : 0 < S0)
    (hle : rho ≤ criticalRho S0) (hrho : 0 ≤ rho) : rho * S0 ≤ 1 := by
  have hcancel : criticalRho S0 * S0 = 1 := by
    unfold criticalRho
    exact one_div_mul_cancel hS0.ne'
  nlinarith [mul_le_mul_of_nonneg_right hle hS0.le]

/-- **T9 (above the boundary, existence).**  If `s` is continuous on a bracket
`[a,b]` inside the positive axis and straddles the level `1/rho`, the skeleton
has a symmetric 2-cycle in that bracket. -/
theorem exists_twoCycle {rho a b : ℝ} (hab : a ≤ b) (ha : 0 < a)
    (hcont : ContinuousOn M.s (Set.Icc a b)) (hrho : 0 < rho)
    (hb : M.s b ≤ 1 / rho) (ha' : 1 / rho ≤ M.s a) :
    ∃ e ∈ Set.Icc a b, M.f rho e = -e := by
  have hmem : (1 / rho) ∈ Set.Icc (M.s b) (M.s a) := ⟨hb, ha'⟩
  obtain ⟨e, he, hse⟩ := intermediate_value_Icc' hab hcont hmem
  refine ⟨e, he, ?_⟩
  have hepos : 0 < e := lt_of_lt_of_le ha he.1
  refine (M.twoCycle_iff hepos.ne').mpr ?_
  rw [hse]
  field_simp

/-- **T9 (uniqueness).**  On any set where `s` is strictly decreasing there is at
most one symmetric 2-cycle. -/
theorem twoCycle_unique_of_strictAntiOn {rho : ℝ} {S : Set ℝ}
    (hanti : StrictAntiOn M.s S) {e₁ e₂ : ℝ} (h₁ : e₁ ∈ S) (h₂ : e₂ ∈ S)
    (hn₁ : e₁ ≠ 0) (hn₂ : e₂ ≠ 0)
    (hc₁ : M.f rho e₁ = -e₁) (hc₂ : M.f rho e₂ = -e₂) : e₁ = e₂ := by
  have k₁ : rho * M.s e₁ = 1 := (M.twoCycle_iff hn₁).mp hc₁
  have k₂ : rho * M.s e₂ = 1 := (M.twoCycle_iff hn₂).mp hc₂
  have hrho : rho ≠ 0 := by
    intro h; rw [h, zero_mul] at k₁; exact zero_ne_one k₁
  have : M.s e₁ = M.s e₂ := mul_left_cancel₀ hrho (k₁.trans k₂.symm)
  exact hanti.injOn h₁ h₂ this

/-- A bounded map stays bounded after damping by `rho in [0,1]`. -/
theorem abs_map_le {rho Rmax : ℝ} (h0 : 0 ≤ rho) (h1 : rho ≤ 1)
    (hb : ∀ x : ℝ, |M.R x| ≤ Rmax) (e : ℝ) : |M.f rho e| ≤ Rmax := by
  have hR : |M.R e| ≤ Rmax := hb e
  have hnn : 0 ≤ Rmax := le_trans (abs_nonneg _) hR
  calc |M.f rho e| = |rho| * |M.R e| := by rw [f, abs_mul]
    _ = rho * |M.R e| := by rw [abs_of_nonneg h0]
    _ ≤ 1 * Rmax := by
        apply mul_le_mul h1 hR (abs_nonneg _) zero_le_one
    _ = Rmax := one_mul _

/-- `[-Rmax, Rmax]` is absorbing in one step from ANY initial state, and hence
forward invariant.  This is the skeleton shadow of T5's state-independent
moment bound. -/
theorem invariant_region {rho Rmax : ℝ} (h0 : 0 ≤ rho) (h1 : rho ≤ 1)
    (hb : ∀ x : ℝ, |M.R x| ≤ Rmax) (e : ℝ) :
    M.f rho e ∈ Set.Icc (-Rmax) Rmax :=
  abs_le.mp (M.abs_map_le h0 h1 hb e)

/-- **T12.**  Local repulsion at the origin — a multiplier of arbitrarily large
modulus — is compatible with a one-step absorbing region.  Local instability
therefore does NOT imply global instability. -/
theorem local_repulsion_with_global_bound {rho Rmax lam : ℝ}
    (h0 : 0 ≤ rho) (h1 : rho ≤ 1) (hb : ∀ x : ℝ, |M.R x| ≤ Rmax)
    (hlam : 1 < |lam|) :
    1 < |lam| ∧ ∀ e : ℝ, M.f rho e ∈ Set.Icc (-Rmax) Rmax :=
  ⟨hlam, M.invariant_region h0 h1 hb⟩

end SecantMap

/-- **T10.**  An orbit of amplitude at most `eps * sqrt v0` measured against a
noise floor of variance at least `v0 > 0` has signal-to-noise ratio at most
`eps`.  As the bifurcating amplitude tends to `0` at fixed positive noise floor,
the signal-to-noise ratio tends to `0`: a supercritical flip bifurcation is
invisible at its own boundary. -/
theorem snr_le_of_small_amplitude {a v v₀ eps : ℝ} (hv₀ : 0 < v₀) (hv : v₀ ≤ v)
    (heps : 0 ≤ eps) (ha : |a| ≤ eps * Real.sqrt v₀) :
    |a| / Real.sqrt v ≤ eps := by
  have hs₀ : 0 < Real.sqrt v₀ := Real.sqrt_pos.mpr hv₀
  have hs : Real.sqrt v₀ ≤ Real.sqrt v := Real.sqrt_le_sqrt hv
  have hsv : 0 < Real.sqrt v := lt_of_lt_of_le hs₀ hs
  rw [div_le_iff₀ hsv]
  calc |a| ≤ eps * Real.sqrt v₀ := ha
    _ ≤ eps * Real.sqrt v := by exact mul_le_mul_of_nonneg_left hs heps

end Priority5Skeleton
end RebaseguardLean
