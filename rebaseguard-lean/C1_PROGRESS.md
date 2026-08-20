# Gate 4.5-C1 checkpoint

## Indexing convention (DERIVED from CUSUMBridge, not assumed)

CUSUMBridge defines `Sₙ₊₁ = f(Sₙ, Xₙ)`, i.e. the transition `n → n+1` consumes `X n`.
Matching the model `S_t = max(0, S_{t-1} + Z_t - k)` at `t = n+1` gives

    Z_t = X_{t-1}          (equivalently  X n = Z_{n+1})

Consequences:
* Lean `cusumPair k X n` = mathematical `S_n`   (SAME index)
* Lean `cusumTau k h X`  = mathematical `τ`     (SAME index)
* `T_t = Σ_{s=1}^t Z_s = Σ_{j=0}^{t-1} X_j = ∑ j ∈ Finset.range t, X j`
* `Z_τ = X_{τ-1}`

NOTE: the earlier audit sketch `∑ s ∈ Finset.Icc 1 n, X s` is OFF BY ONE and was NOT used.

## Definitions introduced (StoppedQuantities.lean)
* `innov X : ℕ → Ω → ℝ`   -- Z_t;  `innov X 0 = 0`, `innov X (n+1) = X n`
* `walk  X : ℕ → Ω → ℝ`   -- T_t;  `walk X n = ∑ j ∈ range n, X j`
* `scoreAt X τ = stoppedValue (innov X) τ`   -- Zτ
* `walkAt  X τ = stoppedValue (walk  X) τ`   -- Tτ
* `cusumTauReal k h X = fun ω => ((cusumTau k h X ω).untopA : ℝ)`  -- τR

## ⊤ handling
`stoppedValue u τ ω = u (τ ω).untopA ω` and
`untopA = untopD (Classical.arbitrary _)`, so at `⊤` the value is an
UNSPECIFIED element (NOT provably 0). Handled by:
* `one_le_cusumTau` : `1 ≤ τ` always
* `exists_succ_of_cusumTau_ne_top` : finite ⟹ `τ = ↑(m+1)`
* CUSUMBridge's `ae_cusumTau_ne_top` ⟹ fallback is null-set only.

## Proved theorem names (all kernel-accepted, direct compile exit 0)
* measurable_innov, measurable_walk
* walk_succ, walk_succ_innov, walk_eq_sum_innov   (convention checks)
* scoreAt_of_eq_coe, walkAt_of_eq_coe             (semantic identification)
* measurable_stoppedValue_nat                     (countable-partition route)
* measurable_cusumTau                             (WithTop-valued)
* measurable_scoreAt_cusumTau, measurable_walkAt_cusumTau, measurable_cusumTauReal
* one_le_cusumTau, exists_succ_of_cusumTau_ne_top, cusumTauReal_of_eq_coe
* ae_exists_succ_cusumTau, ae_stopped_quantities_eq
* aestronglyMeasurable_{scoreAt,walkAt}_cusumTau, aestronglyMeasurable_cusumTauReal

## Status: GATE 4.5-C1 = PASS
C1_EXIT=0 | GATE45AB=0 | GATE4=0 | GATE3=0 | GATE2=0 | BUILD_EXIT=0
bypass scan clean | axioms = [propext, Classical.choice, Quot.sound]
No frozen file modified. Registered in RebaseguardLean.lean.
next: Gate 4.5-C2 (stopped-walk exponential moment) — precondition now satisfied
