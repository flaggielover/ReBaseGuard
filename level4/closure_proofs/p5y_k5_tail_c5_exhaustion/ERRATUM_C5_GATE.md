# Erratum to the frozen C5 gate

`config/FEASIBILITY_GATES_C5.json` is frozen at commit `d2426c03`, sha256
`d0deada65971c3658e7d3b39f8b2bbf5ea4849f25a1570d8f3d272a2f996aa58`. It is **not amended**. Defects found after the
freeze are recorded here, as C2, C3 and C4 recorded theirs.

## E1 — the threshold is inherited, the metric is not, and the gate does not say so

`material_tightening_test` states `"inherited_from": "the C2 gate's 20% gap-fall threshold, carried unchanged
through C3"`, and the **threshold value** claim is true: the pre-forecast reviewer verified `0.20` in
`FEASIBILITY_GATES_C2.json` and `0.2` in `FEASIBILITY_GATES_C3.json`, the latter with C3's own justification
"inherited unchanged from C2's frozen gate rather than chosen for C3".

But **the metric changed and the gate is silent about it**. C2 and C3 measure the gap of the uniform
**atom-constant** reduction factor; C5 measures the gap of the **M-reduction** factor. Computed both ways under
C5-T:

| cell | C5's M-factor metric | C2/C3's atom-constant metric |
|---|---|---|
| 307 | 14.088 % | 14.253 % |
| 308 | 4.591 % | 4.826 % |
| 309 | 3.186 % | 3.482 % |

The two agree to within 0.3 percentage points, the class is **MARGINAL under either**, and the substituted metric
is very slightly **harsher** — so the substitution is not outcome-fitting. It is nonetheless undisclosed, and the
`inherited_from` sentence implies more continuity than exists. The correct statement is: **the threshold value is
inherited unchanged; the metric is the M-factor gap, not C2/C3's atom-constant gap.**

## E2 — the baseline in the gate is rounded, and the forecast divides by it

`baseline.M_reduction_factor_needed` stores five decimal places (e.g. `1.68519` against the exact
`1.6851851451…`), and `c5_forecast.py` uses those values as the denominator of `gap_fall_vs_baseline`. The
relative error is about 7·10⁻⁶, immaterial against a 20 % threshold and incapable of changing any class. A
successor gate should store exact rationals, or declare the rounding.

## E3 — class `INVALID` is unreachable

`classification.primary_order` lists `INVALID` first, but every premise failure raises `TransportRefusal` or
`SystemExit` and propagates out of `main()`, so **no artifact is written at all** and the class can never be
emitted. This is fail-closed, which is the right default — but the gate should have said that an INVALID outcome
is signalled by a refusal without an artifact, not by a class in the output.

## E4 — the gate did not require the C4 scope sentence to be restated

`permitted_conclusions.if_a_predecessor_result_is_affected` correctly required C5 to recompute a predecessor's
load-bearing test under the new clause and to HARD STOP if it no longer held. It did not anticipate the subtler
case that actually arose: the test still holds, but **C4's adjudicated verdict is scoped, verbatim, as holding
"against the frozen measurement inputs and the frozen theorem TC-T / K5-B direct clause", and C5-T replaces that
clause.** So adopting C5-T moves an adjudicated result outside the scope sentence under which it was adjudicated,
even though the result survives.

C5 handles this in `evidence/forecast/C5_FORECAST.json` under `c4_exclusion_fragility.
C4_scope_sentence_must_be_restated`, on the pre-forecast review's instruction. A successor gate should require it
directly.

## E5 — what the reviewer found in the ledger and the mutation suite, and what was done

Both were **blocking FAILs** at the first pre-forecast review, and both were repaired at source rather than by
erratum, because neither the ledger nor the mutation suite is frozen:

* **Route ledger.** v1 recorded routes A5 and A6 as `kill_kind: MATH` with `closure_possible: false`, when its own
  kill gate shows both oracles **close cell 307**. Kill kinds are now cell-scoped (`MATH_PARTIAL` with
  `refuted_at_cells`), the producer **refuses** any `MATH` kill whose oracle closes a cell and cross-checks each
  claimed refutation set against the gate, and the phase-3 headline "five routes refuted on mathematics" is
  corrected to **two** (A4 and D2). Route **E2 is re-opened as live**: v1 killed it as "zero verdict value — a
  better floor only widens a margin that is already positive", in the same commit in which C5-T consumed 63 % of
  that margin, and its cell-308 leg rested on C4's uncertified Monte-Carlo, which a MATH kill may not do.
* **Mutation suite.** "10 mutants, 0 undetected" did not cover the **leftward** weight `w_L`, and the reviewer
  exhibited `w_L := 0` — an unsound mutant surviving all ten mutants, the independent reproduction and the
  forecast cross-check, because the leftward branch binds on none of the four tail cells (ratios 0.85–0.92). The
  suite now manufactures a leftward-binding cell and runs three mutants on it (M11–M13), and it refuses if that
  manufactured cell does not in fact bind leftward.
