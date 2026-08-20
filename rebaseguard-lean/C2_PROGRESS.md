# Gate 4.5-C2 checkpoint

## Target
`∃ a > 0, Integrable (fun ω => exp (a * |walkAt X (cusumTau k h X) ω|)) μ`

## Chosen strategy: ROUTE C2-B (Hölder / Cauchy–Schwarz), all in ℝ≥0∞ (lintegral)

  ∫ e^{a|Tτ|} = Σ_m ∫_{τ=m} e^{a|T_m|}                (countable partition; {τ=⊤} is null)
  ∫_{τ=m} e^{a|T_m|} ≤ (∫ e^{2a|T_m|})^{1/2} · μ{τ=m}^{1/2}      (Cauchy–Schwarz, p=q=2)
  ∫ e^{2a|T_m|} ≤ M^m        where M bounds the ONE-STEP moment ∫ e^{2a|X_j|}
  μ{τ=m} ≤ q^{m-1}           from CUSUMBridge forcing + measure_noForcing_le_pow
  ⇒ Σ_m M^{m/2} q^{(m-1)/2} = M^{1/2} Σ_j (Mq)^{j/2}   converges iff  M*q < 1

Critical scalar condition: **M * q < 1**.

## Verified mathlib APIs (all confirmed present)
* `ProbabilityTheory.lintegral_prod_eq_prod_lintegral_of_indepFun` (no integrability side conditions)
* `ProbabilityTheory.iIndepFun.comp`
* `ENNReal.lintegral_mul_le_Lp_mul_Lq`
* `MeasureTheory.lintegral_iUnion`
* `ProbabilityTheory.integrable_exp_mul_abs` (two-sided → |·|)
ROUTE C2-D ruled out: mathlib has NO randomly-stopped-sum exponential-moment theorem.

## NON-CIRCULARITY (critical)
Assumptions are on the ONE-STEP variables `X j` only (`∫⁻ e^{2a|X j|} ≤ M`) plus the
Gate 4.5-B forcing bound `q`. Nothing assumes any moment of `Tτ`, and τ is never
assumed independent of the walk — the partition `{τ=m}` argument is what avoids that.

## Sub-gates
* C2.1 deterministic partial-sum bound  ∫⁻ e^{a|T_m|} ≤ ∏_{j<m} ∫⁻ e^{a|X_j|}
* C2.2 pmf bound  μ{τ = m} ≤ q^{m-1}
* C2.3 series bridge (Cauchy–Schwarz + geometric sum)   <-- main risk
* C2.4 ∃a>0 packaging; needs M(2a) → 1 as a→0 (dominated convergence)  <-- may be deferred

## PROVED (kernel-accepted, compiled first try, C2_EXIT=0)
File: RebaseguardLean/StoppedWalkMoment.lean (130 lines)
* `expAbsScore`, `measurable_expAbsScore`, `iIndepFun_expAbsScore`
* `expAbs_walk_le_prod`            -- pointwise e^{a|T_m|} ≤ ∏_{j<m} e^{a|X_j|}
* `lintegral_expAbs_walk_le_prod`  -- C2.1, factorised over independent increments
* `lintegral_expAbs_walk_le_pow`   -- C2.1 with uniform one-step bound M: ≤ M^m
* `cusumTau_eq_subset_noForcing`   -- pathwise {τ=m} ⊆ noForcing (h+k) X (m-1)
* `measure_cusumTau_eq_le_pow`     -- C2.2, μ{τ=m} ≤ q^(m-1)

## C2.3 COMPLETE (kernel-accepted)
Added to RebaseguardLean/StoppedWalkMoment.lean:
* `ennreal_rpow_two_eq_pow`, `ennreal_sq_rpow_half`, `sq_ofReal_exp`  (scalar helpers)
* `setLIntegral_le_of_sq_le`          -- Cauchy-Schwarz slice bound (Holder p=q=2)
* `lintegral_slice_expAbs_walkAt_le`  -- slice bound: <= c^m * d^(m-1)
* `lintegral_eq_tsum_slices`          -- partition; {tau = top} removed via ae_cusumTau_ne_top
* `tsum_geometric_majorant_ne_top`    -- sum finite iff c*d < 1
* `lintegral_expAbs_walkAt_ne_top`    -- ENNReal form
* `integrable_exp_abs_walkAt_of_moment_tail`  -- **C2.3 TARGET, reaches walkAt**

Scalar hypotheses use the square-rooted form: M = c^2, q = d^2, condition c*d < 1
(equivalently M*q < 1). This avoids all rpow algebra except one helper.

## STILL NOT DONE (later gates, deliberately out of scope)
C2.4 `∃ a > 0`: needs `M(2a) -> 1` as `a -> 0` (dominated convergence). NOT attempted.
Gaussian instantiation of the one-step moment. NOT attempted.

## Status: GATE 4.5-C2.3 = PASS (fully verified)
C23_EXIT=0 | C1=0 | GATE45AB=0 | GATE4=0 | GATE3=0 | GATE2=0 | BUILD_EXIT=0
bypass scan clean | axioms = [propext, Classical.choice, Quot.sound]
No frozen file modified. Resume point for C2.4: M(2a) -> 1 as a -> 0.
