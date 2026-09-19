# Independent mathematical review r1 of theorem AD (fresh-context agent; reviewed commit b67cb900)

**Overall verdict: PASS_WITH_NOTES.** Nothing found that breaks Theorem AD or any bound it claims. Two MAJOR gaps mean it
should not be frozen yet, and no certified registry exists at b67cb900, so nothing has actually been certified.

**Scope.** The blobs committed at b67cb900 were reviewed. The working tree changed during the review
(`code/deflated_consume.py` uncommitted edits adding a freeze guard, a replay mode and a new `main`, same rule functions;
new untracked `xcheck_registry.py`, `gate_eval.py`, `qualify_successor.py`, the successor spec) — not reviewed.
`qualify_ad.py` was re-run: Q_PASS and MUTATION_PASS both true with 0 violations, output identical to the committed
`QUALIFICATION_AD_r1.json`.

## The 12 attack points

1. **Rank-one identity, Sherman–Morrison, D > 0: SOUND_WITH_NOTE.** T(x,z) = a exactly when z ∈ [m−k, k−p]; non-empty only
   when p+m ≤ 1 and inside the survival window; at p+m = 1 a single point; endpoints measure zero. The frozen low branch
   (`residual.py:144-173`) is valid only for p+m ≤ 1 and the "origin" piece is only the w(0,0) term over [β, α], so
   `taboo_certify.py:148-155` rightly removes it from the low branch only; the high branch and the axis tails have no atom.
   I−K = (I−K̂)(I−h⊗δ_a) is valid in any Banach space; δ_a bounded. D = ν(h₁) ≥ h₁(a) > 0 proved (THEOREM_AD:53-56).
   Note: B(X) should say bounded Borel functions.
2. **Complement invariance / hidden spectral projection: SOUND.** Purely algebraic; no projection, eigenpair or invariant
   subspace used.
3. **Nonnormality: SOUND.** Every constant comes from positivity plus a supersolution or a taboo-residual certificate; the
   projector and conditioning numbers of OPERATOR_AUDIT §5 are informational only.
4. **τ_a/D = E_a[τ], and Lemma Dv′: SOUND.** f = 1 in SM(c) gives E_a[τ]. The five quotient-rule terms each carry exactly
   one factor τ_a/D, bounded by Ā_eff = min(Ā, τ/D_lo); δ₁ ≥ |D′|/D, δ₂ ≥ |D″|/D. Code matches
   (`deflated_consume.py:91-103`); r2 ≤ r1 always.
5. **Eigenvalue simplicity: SOUND_WITH_NOTE.** λ_e never used; the renewal-root claims in OPERATOR_AUDIT §4 are correct;
   existence of λ_e not proved (admitted). Label those claims informational.
6. **Uniformity over blocks and cells: SOUND_WITH_NOTE.** The block argument (`taboo_certify.py:206-228`) is correct (affine
   part smallest at s = ±1; ‖w‖ ≤ Chebyshev ℓ¹ sum; w ≥ 0 checked). D_lo = D_mid − ρ·D1_cell with D1_cell the smaller of two
   valid bounds (`taboo_certify.py:331-337`). Straddling cells take the worst constants with a coverage check
   (`build_registry.py:96-100`). All 326 cells have left = e0−ρ, right = e0+ρ, no gaps; cells 0–148 lie inside [0, 0.1147].
7. **Derivative terms D′, D″: SOUND.** ∂R = RK′R, ∂²R = 2RK′RK′R + RK″R; at a these are (ν/D)′ and (ν/D)″, so A1, A2 are
   complete. ν(K′h) = −D′ − Dν(k_a′) checks out. d′, d″ satisfy the right taboo equations; h₁′ = −S₀, h₁″ = −S₀′.
8. **Source errors: SOUND.** `Sclosed:k` for r = 0 and `S:r:k` otherwise, exactly the frozen rule (`propagate.py:37-39`);
   the r = 0 reward allowance is charged once, in the Sclosed node (`s0_charge_audit`).
9. **Interval certification in `taboo_certify.py`: SOUND.** Doubling the truncation allowance is conservative; `hallow`
   copied from the frozen `h1_allow`; envelopes env0, env1, env2 correct (binomial weights, κ₃ included); `prop` correct;
   the Bernstein cover has the same four pieces as the frozen `fast_range`.
10. **Tightening corollary: SOUND_WITH_NOTE.** The proof holds (Arb contains the exact Minkowski sum; used radius ≥
    recorded ε; outward endpoints). It depends on how the records were actually produced, which is not the path THEOREM_AD
    cites: they come from Aux5 (`aux_propagate.py:241-313` → `reviewed.enclosures`, midpoint DAG for F and D, `refine2`
    for H). Half-width / needed radius = 1.0000000 at m = 1 on the committed records. The refusal guard is necessary only;
    soundness rests on reading the producer code.
11. **Consumption: SOUND.** Every input to `k5b_literal` is a valid enclosure, including intersections; K5-B is monotone
    (Γ uses R.hi, D.lo and M; μ/ℓ use H.lo; `k5b_check.py:155-193`); the T-EXT C2 step is identical to
    `text_consume.py:114-121`.
12. **Slot-1 reuse: SOUND_WITH_NOTE.** Slot-1 L1 only as cell 0's L (E6 `cells_for_m`) and inside the T-EXT
    re-derivation, exactly as the adopted T-EXT consumer; the operator certification reads no record.

## Findings by severity

- **BLOCKING:** none.
- **MAJOR M1.** The certifier is not qualified: `taboo_certify.py` produces every certified constant and `build_registry`
  binds them, but neither has a test, mutant or float cross-check; `qualify_ad.py` tests only the consumer rule, so the
  affine block argument, the ρ·env extension, D_lo = D_mid − ρD1, worst-block selection, origin removal, truncation
  allowances and `prop` are never exercised.
- **MAJOR M2.** `build_registry.verify` does not check REGISTRY.json itself: the fields the consumer reads are never compared
  with the artifacts or the worst-block rule; fix by re-running `assemble` in memory and comparing byte for byte.
- **MINOR.** Premise citations should name the Aux5 producer chain (e.g. the record's `whole_cell_refinement` audit gives
  ε_H = 18059 while `eps_cell_refined` = 16669 is the one used). Qualification padding: M07 is a refusal test and M16 a
  property count, not mutants; the Q2 "range" check cannot fail when "point" passes; Q5 `closed_class` tests the harness;
  `record_like` sets `Sclosed:k` = `S:0:k`, so a source-node swap is undetectable; no mutant for over-shrinking with the
  wrong recorded radius or picking the wrong block. False docstring claim (`deflated_consume.py:47-48`) that κ₁/κ₂ are
  re-proved in Arb (the bounds do hold: √(2/π) = 0.797884561 < 0.7978846, 4φ(1) = 0.967882898 < 0.9678830). B(X) Borel.
  The committed qualification is bound to consumer sha 697f997d; re-run against whatever is frozen.
