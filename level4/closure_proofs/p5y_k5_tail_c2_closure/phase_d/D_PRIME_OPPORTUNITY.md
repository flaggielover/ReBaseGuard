# The deterministic step C2 did not pre-register, and why it must be tried before a real address is spent

**This is the finding that matters most for what happens after C2, and it is not C2's finding.** It was raised by
the independent pre-freeze review as its Note 11. C2 recomputed it from its own committed producer
(`code/c2_critical_ratio.py` → `evidence/phase_d5/C2_CRITICAL_RATIOS.json`), confirmed it exactly, and records it
here because the campaign's own R-stage argument is weaker than it looked before this number existed.

**Nothing in this document changes C2's class, C2's adopted subset, or any number C2 publishes.** C2 remains
`D_PARTIAL`, closing {305, 306}. The supply analysed here is deliberately **not** used in C2's result.

## 1. The step

Campaign C1 and Campaign C2 each certified the *same six operator quantities* over the *same five cells*:

    tau, C_T, D1, D2   -- upper bounds        D_lo -- a lower bound        Abar -- an upper bound

C1 certified them on one wide block per cell; C2 re-certified them on a partition into sub-blocks of width ≤ 1/100.
Both are valid uniformly on the whole cell — **checked, not assumed**: C1's block on each tail cell is exactly
[e₀ − ρ, e₀ + ρ], identical endpoint for endpoint to the frozen cover's own cell, on all five cells; and C2's
sub-blocks tile that same interval exactly (verified by the tiling invariant in `code/c2_mutations.py`, with three
mutants against it). If C1's block had been narrower than the cell, its constants would not have been whole-cell
bounds and the combination below would be unsound. It is not narrower. Therefore the **componentwise best of the two** — min on the five upper
bounds, max on D_lo — also holds uniformly on the whole cell, and satisfies all six Lemma Dv′ hypotheses
simultaneously. It is a sound supply. (The producer does not take this on faith: it feeds the mixed tuple through
`deflated_consume.atom_constants_r2`, which refuses unless τ ≥ 1, C ≥ τ, D_lo > 0 and Ā ≥ 1 all hold. It does not
refuse on any cell.)

This matters *because* of C2's τ regression. C2's refinement improved D_lo, D1 and D2 but made **τ and C_T 1.9–2.9 %
worse**, because the degree-20 candidate is anchored at its block's centre and the worst sub-block's centre sits
further left. So neither registry dominates the other field by field, and the best available deterministic supply is
in neither of them alone.

## 2. What it buys

Against the gate's own frozen C1 baseline, with the gate's own 20 % material-tightening threshold:

| cell | C2 requirement | C2 gap fall | **mixed-operator requirement** | **mixed-operator gap fall** | ≥ 20 % |
|---|---|---|---|---|---|
| 307 | 1.14076357 | 46.29 % | **1.11196624** | **57.27 %** | yes |
| 308 | 1.50028778 | 24.59 % | **1.46065480** | **30.57 %** | yes |
| 309 | 1.89901487 | 18.39 % — **misses** | **1.84787350** | **23.03 %** | **yes** |

Cell 309 is the single cell that cost C2 the `D_USEFUL` class, by 1.6 percentage points. Under the mixed operator
supply it clears the same frozen bar with 3 points to spare, and **all three still-open cells clear it** — which
under the frozen classes is `D_USEFUL`, not `D_PARTIAL`.

The critical order-3 ratios move the same way: 38.07 / 23.90 / 14.72 against C2's 37.32 / 23.26 / 14.16.

**This costs zero new CPU seconds and zero new real scientific addresses.** Every constant involved is already
certified, already committed and already reviewed, in two published namespaces.

## 3. Why C2 does not take it

Because the frozen gate does not permit it, and the gate is right.

The gate's D4 rule pre-registers the componentwise minimum over **A0/A1/A2 across whole supplies** — Lemma G,
Lemma Dv′ from C1, Lemma Dv′ from C2. It does not pre-register a minimum over the **six operator constants** before
Lemma Dv′ is applied. Those are different rules, and only the first one was frozen before any C2 number existed.

Adopting the second rule *now*, having seen that C2's τ regressed and that cell 309 landed at 18.39 %, is precisely
the post-hoc choice the gate exists to forbid. It would convert a missed threshold into a met one by changing the rule
after seeing the result. C2 does not do that, and a successor may not do it either — it must **freeze the rule
first**, as its own pre-registration, before recomputing anything.

## 4. What this does to C2's R-stage argument

The gate's reading of a sub-20 % result is that the deterministic direction is exhausted and the programme should
route to the R stage. **That reading is not established, and C2 should not have implied it was.**

The honest statement is narrower: **C2's pre-registration ran out, not the deterministic direction.** A successor
that pre-registers the operator-level combination reaches the gate's own bar on every open cell, using constants
that already exist, at no compute cost and with no new real address.

Spending the programme's first real order-3 tail address on the strength of "309 came in at 18.39 %" would be
spending it against a number that a cheaper, sound, pre-registerable deterministic step already beats. That is the
wrong order of operations, and the R-stage design now says so at its head.

## 5. What a successor must do, in order

1. **Freeze a D′ gate first**, pre-registering the operator-level combination rule (min on τ, C_T, D1, D2; max on
   D_lo; min on Ā) and its material-tightening test, before recomputing any magnitude.
2. Recompute the five cells under that rule. Expect 307/308/309 at roughly 57 / 31 / 23 % gap fall — but **expect
   is not a result**, and the frozen rule decides.
3. **Only if D′ still closes no further cell** does the R-stage eligibility argument in `phase_r/` become sound. Its
   attribution test, its minimal address set and its cost model are unaffected and remain usable as written.
4. N1, N3 and N5 remain open regardless; they gate the R stage independently of any of this.

Note that D′ is not predicted to *close* 307, 308 or 309 — the mixed supply still needs uniform reductions of
1.11×, 1.46× and 1.85×. It is predicted to clear the *material-tightening* bar. Whether a deterministic route can
close the remaining three cells at all is still answered by the D1 diagnosis: **no**, because A0 = τ/D_lo ≥ τ and
cell 309 would need τ ≤ 2.48 against a certified 4.42 that bounds a genuine hitting time. What D′ changes is the
*class*, the honesty of the exhaustion premise, and how much margin a real order-3 candidate would need — not the
verdict that the tail's remaining cells need order-3 information.
