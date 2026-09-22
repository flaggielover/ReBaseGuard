# Erratum to the frozen C7 gate (`config/FEASIBILITY_GATES_C7.json`, sha256 `9f7083b9…`)

The gate is **not amended**. It stays byte-identical, and kill gate `GATE` in
`code/c7_certificate.py` still requires its frozen sha. These are corrections to statements the gate
makes, recorded in the form this programme uses for a frozen artifact that turns out to be wrong.

All five were raised by the fresh-context pre-publication review
(`review/REVIEW_C7_PREPUBLICATION.md`), which returned **NOT_READY**.

## E1 — the non-blindness argument is false as stated (review finding 2, CRITICAL)

The gate says, at `disclosure_of_non_blindness.why_this_does_not_compromise_soundness[0]`:

> "Every prospective choice -- the partition, the a-grid, the u0 ladder, the point e, the choice of U
> -- affects only the TIGHTNESS of a bound, never its VALIDITY. … There is no setting of any of them
> that can make an invalid result appear valid."

**This is false for two of the five choices.**

- **the point `e`.** Validity requires `e` in the closed cell `[19839101/10000000, 2092283/1000000]`.
  Nothing enforced it. `e = 1.90` yields a tier-1 value of 3.642963840 — *larger than the published
  PRIMARY bound* — and fires no kill gate.
- **the a-grid.** See E2.

**Corrected statement.** The claim holds for the **partition** and the **`u0` ladder**: any
partition of `[0,H]` and any split point gives a valid bound, and refining only tightens. It does
**not** hold for the point `e`, the a-grid, or the choice of `U`, each of which carries a validity
side-condition — `e` in the closed cell, `a > 0`, and `U ≥ E[τ′]`. The correct general statement is
that the gate's choices divide into tightness-only knobs and knobs with side-conditions, and that
**the side-conditions must be enforced in code**, which they now are (`_require_in_cell`, the `a > 0`
refusal in `g_tail`, and `certified_U`'s floor).

The freeze-order disclosure itself stands. It was the sweeping "no setting of any of them" that was
wrong, and it was wrong in the campaign's own favour.

## E2 — the a-grid was frozen in prose and bound nothing (review finding 1, CRITICAL)

The gate freezes `a_grid_for_lemma_C7_U = "{j/4 : j = 8..24}"` as a **string**. No code compared a
presented grid against it: `_resolve_U` re-derived `U` from the grid carried *in the certificate under
test*. The provenance mechanism therefore constrained `source` — the field the mutants exercised —
and never the field carrying the payload.

Combined with an unenforced `a > 0` (Lemma C7-U's own hypothesis, without which the closed form is
not `E[V 1{V>a}]` at all), the review obtained a **dependency-set-EMPTY, re-derivation-surviving,
kill-gate-clean bound of 3.619819606** — `+0.9345 %` over the published PRIMARY — from
`U = 3.549353697`, a value C7's own arithmetic proves is not an upper bound on `E[τ′]`. No source
mutation was required; only the public API.

**Correction.** The frozen grid is now bound in code as `c7_theorem.GATE_A_GRID`, `_resolve_U`
re-derives from **it** and refuses any certificate presenting a different grid, and `g_tail` refuses
`a ≤ 0`. Regression-tested by mutants M16 and M17.

**The published numbers were never affected** — `c7_certificate.py` always passed the gate's grid.
The defect was in the mechanism and in the claims made for it.

## E3 — the gate never fixed the finiteness threshold `c` (review finding 3, MAJOR)

Lemma C7-U step 0 certifies `E[τ′] < ∞` by geometric domination at a threshold `c`. The gate fixes no
`c`, and `E_tau_prime_finite` **had no caller anywhere in the tree** while the docstring asserted the
finiteness "is certified, not assumed". Step 3 of the lemma divides by `E[V] − g(a)` after
substituting Wald, which is invalid if `E[R] = ∞`, so the PRIMARY bound's advertised *empty*
dependency set rested on a step proved in prose and executed nowhere.

**Correction.** `c = 1` is fixed here and bound in code as `c7_theorem.GATE_C_FINITENESS`.
`certified_U` now calls `E_tau_prime_finite`, refuses unless `P(V > c) > 0`, and carries the result
(`p_lower = 0.686022237`, 6 geometric stages, crude `E[τ′] ≤ 8.746072`) in every `U` certificate.

## E4 — Monte Carlo, which the gate forbids outright, was run (review finding 14, MAJOR)

The gate's `compute_boundary.forbidden` contains **"Monte Carlo of any kind"**, unconditionally and
with no "as evidence" qualifier.

**What happened.** The campaign commissioned an independent numerical cross-check, which wrote its
own simulator from scratch and ran ≥ 2,000,000-path Monte Carlo to estimate `E[τ′]` and `E[R]`. It
ran **out of tree**, in a scratch directory, in a separate process, using only the Python standard
library; it imported no campaign module and modified nothing in the repository.

**This breached the gate's prohibition in letter.** The campaign that froze a gate does not get to
reinterpret it afterwards, so this is recorded as a breach rather than argued away.

**What was and was not affected.** No C7 conclusion rests on it. The simulation is not a producer,
emits no committed artifact, and appears only in `OPEN_NOTES_DISPOSITION_C7.md` → N3 explicitly
labelled non-evidence. Its result (`E[τ′] ≈ 3.98842 ± 0.00050`) is *consistent with* the bracket C7's
own certified arithmetic independently gives, `E[τ′] ∈ [3.586306, 4.679910]`. The purpose of the
prohibition — keeping uncertified numerics out of the evidence chain — was not breached; its text
was.

**Correction.** The activity is now **declared** in the certificate under
`external_non_evidence_activity` rather than mentioned only in a note, so that the declaration and
the tree agree. A successor gate should say "no Monte Carlo **in the evidence chain**", which is the
rule that was actually intended, instead of a blanket prohibition that an external cross-check
violates by existing.

## E5 — `SCIENTIFIC_KERNEL_EVALUATIONS: 0` needs its scope stated

The counter is true on its own terms: C7 evaluated no scientific kernel, contacted no remote host,
provisioned no toolchain, and computed no new-real address. But read beside E4 a reader must
reconcile "0" with a simulator that was written and run.

**Correction.** The counters describe **the C7 evidence chain**: every committed producer and every
number any C7 conclusion rests on. Out-of-tree cross-checking activity is counted separately under
`external_non_evidence_activity`. Both are now reported.
