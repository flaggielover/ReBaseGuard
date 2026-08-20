# Gate 4.5-C3 Progress

## Chosen Gate 4 instantiation route
`Domination.hasDerivAt_integral_stoppedIntegrand_zero_of_separate_moments`
(split-moment form), NOT the joint-moment form.

The rates `p` (walk, from C2.4) and `q` (alarm time, from C3-A) are produced by
existence theorems and are therefore fixed and possibly tiny.  So the Gate 4
parameters are shrunk to fit them, not the other way round:

    t     = min 1 (min (p/8) (q/6)),  t > 0
    δ = c = t
    a     = 2t          →  δ + c = 2t ≤ a            ✓
    b     = 3t²/2       →  δ²/2 + cδ = 3t²/2 ≤ b     ✓
    4a    = 8t  ≤ p                                   ✓ (t ≤ p/8)
    4b    = 6t² ≤ 6t ≤ q                              ✓ (t ≤ 1, t ≤ q/6)

## Theorems proved (RebaseguardLean/ReBaseGuardIdentity.lean, 404 lines)

C3-A (alarm-time exponential moment)
  cusumTauReal_nonneg
  cusumTauReal_le_of_le
  integrable_exp_abs_cusumTauReal
  exists_pos_exp_mul_lt_one
  exists_pos_integrable_exp_abs_cusumTauReal_gaussian

C3-B (stopped score in L²)
  exists_sq_majorant_lt_one
  sq_le_const_mul_exp_abs
  lintegral_slice_expAbs_scoreAt_le
  lintegral_expAbs_scoreAt_ne_top
  integrable_exp_abs_scoreAt
  integrable_sq_scoreAt_of_exp
  integrable_sq_scoreAt_gaussian

Assembly
  rebaseguard_separate_moments
  hasDerivAt_integral_rebaseguard_gaussian
  hasDerivAt_rebaseguard_cusum      -- frozen k = 1/2, h = 5

## Exact assumptions remaining in the final theorem
  hX     : ∀ n, Measurable (X n)
  hindep : iIndepFun X μ
  hlaw   : ∀ j, μ.map (X j) = gaussianReal 0 1
No hM / hq / hcd / domination function / stopped-moment assumption remains.
IsProbabilityMeasure is derived (hindep.isProbabilityMeasure), not assumed.

## Checklist
[x] 1/8 Inspect Gate 4 final theorem interface
[x] 2/8 τR exponential moment
[x] 3/8 scoreAt L²
[x] 4/8 Assemble separate moments
[x] 5/8 Instantiate Gate 4 derivative theorem
[x] 6/8 Frozen k=1/2, h=5 final theorem
[x] 7/8 Regression + lake build   (all exit 0; build 8717 jobs)
[x] 8/8 Semantic/axiom audit      (only propext, Classical.choice, Quot.sound)

## Status: GATE 4.5-C3 = PASS (fully verified)
No frozen file modified (mtimes unchanged).
