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

---

# Second round — raised by the independent adjudication (`review/ADJUDICATION_C7.md`)

The adjudication returned **ACCEPTED_WITH_CONDITIONS**: 15 findings LANDED, 2 PARTIAL, 0 NOT_LANDED.
It also found nine defects that the pre-publication review had not. Four require errata.

## E6 — KG8 was narrowed in the campaign's own favour, without an erratum

This is the most serious governance defect in C7, and the campaign did not raise it. The frozen gate
says:

> `"KG8": "any mutant in the required-detection set survives -> REFUSE"`

`M01`–`M04` are in the required-detection set. The mutation artifact's own prose stated plainly that
they **survive and are not detected**. `MUTATION_CLASS` was nevertheless `"PASS"` with
`undetected: []`, because the four had been moved into a sibling list, and `c7_certificate.py`'s KG8
read exactly `MUTATION_CLASS == "PASS"`. **Under the frozen text, KG8 fires and `C7_CLASS` is
`REFUSED`.** The string `KG8` appeared in the gate and in the certificate module and nowhere else —
not in this erratum, not in the README, not in the disposition.

So the first round of repairs fixed the *reporting* of finding 4 while quietly leaving a frozen kill
gate narrowed from "survives" to "survives and alters a reported digit". In a campaign whose erratum
instrument exists precisely for that act, doing it silently is worse than the original defect.

**Why the narrowing is nonetheless the right reading — and it is still a narrowing.** `M01`–`M04` are
**source mutants**: they alter the production arithmetic itself. No program can refuse its own mutated
source, so KG8 applied to source mutants is **unsatisfiable in principle** — any campaign that
includes a source mutant at all would be refused by its literal text. The other fourteen are
**interface mutants**: inputs the public API accepts, which production code *can* refuse, and all
fourteen are detected.

**Correction.** The mutation artifact now partitions the required set into `interface_mutants` and
`source_mutants`, reports `interface_undetected` and `source_surviving` separately, carries the
frozen KG8 text alongside a `KG8_literal_status` field stating in terms that it is **NOT SATISFIED**,
and reports `MUTATION_CLASS = "PASS_WITH_SURVIVORS"` — a class that does not assert cleanliness.
`c7_certificate.py` enforces KG8 over interface mutants and states the narrowing at the call site.

**Materiality: nil for the number.** The four mutants move the bound by ~1e-94 relative. This is a
governance defect, not an arithmetic one. A successor gate should define its required-detection set
over interface mutants and require source mutants to be *enumerated with measured effect*, which is
the rule that was actually intended.

A smaller overstatement, also corrected: "does not alter any digit of the reported value" was
anchored on IEEE-double equality, while the certificate's authoritative field is an exact rational.
It is true of the float and false of the rational.

## E7 — `u0_ladder_for_tier2` is now inert

The gate freezes `u0_ladder_for_tier2` for `lambda_lower_tier2`, the single-split precursor of the
multi-tier theorem. That function had no caller, took a **bare** `U` with no certificate and no
`_resolve_U`, and never checked cell membership — so both repaired exploits remained reachable
through it: `lambda_lower_tier2(e = 1.90, U = 0.1)` returned **4.219038180** with no refusal. A dead
public entry point bypassing the guards E1 says are "now enforced in code" falsifies that sentence.

**Correction.** The function is removed. The gate's `u0_ladder_for_tier2` is consequently inert and
binds nothing. Tier 2 survives only as the `k = 2` case of the multi-tier theorem, which is guarded.

## E8 — kill gates were added that the frozen gate does not enumerate

The gate enumerates KG1–KG9. The certificate had also been enforcing KG8b, KG9b, KG10, KG10b and
KG11, none of them disclosed.

**KG10/KG10b** (the Gaussian primitives test, and that it ran against the committed
`c7_gaussian.py`) are conservative — they can only refuse, never admit — and are retained, now
declared here.

**KG11 is different in kind and is removed.** It made the verdict depend on
`criterion_holds_at_every_knot` in the ψ-monotonicity artifact — an analysis the theorem explicitly
**does not use**, since the bound consumes `ψ_lo` and never `ψ_exact`. A failure there could have
refused an otherwise valid campaign on the strength of an unused diagnostic. It is now reported as a
diagnostic under `psi_monotonicity_DIAGNOSTIC_NOT_A_GATE`.

## E9 — `K` and `H` are side-conditions, and E1's list did not name them

E1 corrected the gate's non-blindness claim and named the validity side-conditions for `e`, the
a-grid and `U`. It did not name `K` and `H`, and neither did the code: they were free parameters of
every entry point in `c7_theorem.py`. KG7 lived only in `c7_certificate.py`, where it tested that
module's own constants, and in the mutation suite's *mirror*. Driving the **real** entry point:

```
  K = 1/2, H = 11/2  ->  3.925355098     no refusal   (C4's documented threshold-confusion mode)
  K = 1/2, H = 6     ->  4.250984509     no refusal
  tier-1 at H = 11/2 ->  3.774230652 ;  at H = 6 -> 4.090097516     no refusal
```

Both inflated values exceed the published PRIMARY and sit below the certified `A0` and the family
ceiling, so **KG5 does not fire either**. At `+18.5 %` this is a larger inflation than either exploit
the pre-publication review found, reachable through the public API with no mutation — and it is
exactly the error KG7 exists to catch. That C4 documented this precise failure mode, and C7 inherited
the constant-equality check only into the certificate module, is the whole lesson.

**Correction.** `c7_theorem._require_frozen_model` enforces `K = 1/2` and `H = 5` at every entry
point — `lambda_lower`, `lambda_lower_tier_k` and `certified_U`. Regression-tested by M19 and M20,
which drive the **real** entry point rather than the mirror.

**No published number was affected**: C7's producers hardcode the frozen constants. As with E1 and
E2, the defect was in the mechanism.
