/-
  ENVIRONMENT PROOF / FALSIFICATION TEST
  Blocks A,B  must SUCCEED.   Blocks C,D,E  must FAIL (or expose sorryAx).
  A toolchain that "passes" everything is broken; this file proves it discriminates.
-/
import RebaseguardLean
open MeasureTheory ProbabilityTheory RebaseguardLean

-- ══ A. POSITIVE: the real theorem's axiom footprint ══════════════════════════
#print axioms RebaseguardLean.hasDerivAt_rebaseguard_cusum

-- ══ B. POSITIVE: restate the theorem verbatim and discharge it by the theorem ══
--    If this elaborates, the statement below IS the theorem (no paraphrase drift).
example {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hX : ∀ (n : ℕ), Measurable (X n))
    (hindep : iIndepFun X μ)
    (hlaw : ∀ (j : ℕ), μ.map (X j) = gaussianReal 0 1) :
    HasDerivAt
      (fun e => ∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω *
        Real.exp (-e * walkAt X (cusumTau (1 / 2) 5 X) ω
          - e ^ 2 / 2 * cusumTauReal (1 / 2) 5 X ω) ∂μ)
      (-∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω
            * walkAt X (cusumTau (1 / 2) 5 X) ω ∂μ) 0 :=
  hasDerivAt_rebaseguard_cusum X hX hindep hlaw

-- ══ C. NEGATIVE: the SIGN is load-bearing — identical to B but "+" not "−" ════
example {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hX : ∀ (n : ℕ), Measurable (X n))
    (hindep : iIndepFun X μ)
    (hlaw : ∀ (j : ℕ), μ.map (X j) = gaussianReal 0 1) :
    HasDerivAt
      (fun e => ∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω *
        Real.exp (-e * walkAt X (cusumTau (1 / 2) 5 X) ω
          - e ^ 2 / 2 * cusumTauReal (1 / 2) 5 X ω) ∂μ)
      (∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω
            * walkAt X (cusumTau (1 / 2) 5 X) ω ∂μ) 0 :=
  hasDerivAt_rebaseguard_cusum X hX hindep hlaw

-- ══ D. NEGATIVE: a `sorry` IS caught by the very audit used on the real chain ══
theorem envproof_via_sorry : ∀ n : ℕ, n = n := by sorry
#print axioms envproof_via_sorry

-- ══ E. NEGATIVE: the kernel rejects a false statement ═════════════════════════
theorem envproof_false : (1 : ℕ) = 2 := by rfl
