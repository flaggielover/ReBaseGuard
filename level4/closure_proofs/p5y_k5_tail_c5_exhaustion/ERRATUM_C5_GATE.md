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

## E6 — the sign-bearing input was defended only against a sign-blind check

Found by the round-2 pre-forecast review, repaired at source. `signed_enclosure` was the **one** input the
forecast took on trust from another module. Negate-and-swap — returning `(−H_hi, −H_lo)` — is well ordered, so the
inverted-interval guard never fires; it preserves `max(|H_lo|, |H_hi|)`, so the forecast's
`Gamma_frozen == d["Gamma"]` cross-check is blind to it; and part (1) of the mutation suite is self-consistent
with whatever enclosure it is handed. At cell 309 it understates the penalty by **2.6238 %** — more than double
C5-T's entire 1.295 % gain — and it survived every check in the campaign.

The shipped code was correct, so no number in the tree was ever wrong. What failed was the assurance claim. The
forecast now **re-derives** the signed endpoints from the sealed interval and the frozen consumer's own signed
output and refuses on disagreement (`checked_enclosure`), and mutant **M14** exercises exactly this. With that,
every input C5-T consumes is either computed in the forecast from a sealed artifact (`g_hi`) or cross-checked
against the frozen consumer (`e0`, `rho`, `M`, and now the signed endpoints).

## E7 — the ledger's guards were narrower than the ledger claimed

Also round 2. The first repair said the producer "refuses any `MATH` kill whose oracle closes a cell and
cross-checks each claimed refutation set against the gate". Neither held in general: the cross-check iterated a
hardcoded two-route allowlist, and the `MATH` guard compared two hand-written fields of the same dict, so it could
not detect a wrong `oracle_closes_at_cells`. The reviewer demonstrated both holes with fabricated routes the
producer accepted.

Now every route declares either a `kill_gate` naming a knob in the sensitivity evidence, or `argued_without_gate`;
the refutation sets are **derived from the gate** rather than compared against copies; a gate-free `MATH` kill must
carry an `argument` field or the producer refuses; and the artifact records `refuted_without_a_kill_gate` with a
`headline_caveat`, because the two routes carrying the corrected headline — A4 and D2 — are both gate-free
arguments rather than gate results.

Two consequential field fixes in the same pass. `C5_MUTATIONS.json` recorded `invisible_on_real_cells: false` on
M12 and M13, contradicting its own prose: the comparison used the manufactured cell's mutant Γ against the real
cells' Γ with the weights already restored, so it was true by construction. The honest value is **true** on both,
and it is now computed with the mutation live on the same cells. And route E1's withdrawn phrase "provably useless
for 309" survived in its primary `kill_reason` and in the phase-3 table row. It is now confined to
`withdrawn_phrase`, and E1's `refuted_at_cells` is emptied in favour of `refuted_at_cells_diagnostic_only`,
because that entry rests on C4's uncertified Monte-Carlo — the precise ground on which v1's E2 kill was condemned.

**This paragraph was itself wrong when first written, and that is the third time in this campaign line.** It
asserted the phrase was confined to `withdrawn_phrase` while the phase-3 table row still carried it verbatim; the
round-3 reviewer found it, exactly as C4's round found two "Fixed at source" claims that had landed in one file
and not the others. The repair is now verified in both places by the commit that carries this sentence. The
lesson C4 recorded and C5 failed to apply: **grep for the withdrawn string across the namespace before writing
that a withdrawal landed.**

## E8 — the forecast was committed against a clearance that was not in committed evidence

**This is the fourth instance in this campaign line of a repair or a state recorded as landed when it had not,
and the first at the governance layer.**

The commit that produced `evidence/forecast/C5_FORECAST.json` (`8b2be7ab`) asserts in its message:

> "pre-forecast review READY at round 3 … Three rounds of fresh-context review … the reviewer's terminating
> condition met … It re-ran its own attacks and none survived."

All of that is **true of what happened** — the round-3 reviewer did return `READY_TO_FORECAST_WITH_NOTES`, did
re-run its own attacks, and did record that none survived. But **the round-3 report was never committed.** The
file at `review/REVIEW_C5_PREFORECAST.md` at that commit was the **round-2** report, headed "ROUND 2", recording
two blocking FAILs and ending `HANDOVER: NOT_READY`. The frozen gate requires "0 blocking FAIL" before the
forecast is evaluated and says "file existence is not completion". So the forecast stands on a clearance that an
auditor reading the tree could not find, and on a commit message asserting one. Found by the independent
adjudicator, not by C5.

**Repair.** The round-3 report is now committed as `review/REVIEW_C5_PREFORECAST_R3.md` (the round-2 report is
retained alongside as `..._R2.md`, because a campaign that discards the report that failed it is hiding the
useful half). Both are in the tree; both handovers are machine-read by the self-check below.

**Why the previous three responses were inadequate.** Each of the first three instances was answered with a note
to the author — C4's Condition 2, then C5's E7 with its "grep before you claim" lesson. The lesson was written
into E7 and the pattern recurred **in the very commit that recorded it**. Notes to the author have a demonstrated
failure rate of 100 % in this line.

**The mechanical replacement (adjudicator condition 6).** `code/c5_selfcheck.py` refuses rather than reports:

1. every string in a machine-readable `withdrawn_strings` table must appear only inside a sentence that withdraws
   it, across every tracked `.md`, `.json` and `.py` in the namespace;
2. a forecast artifact may exist only if a reviewer artifact **in the tree** carries a clearing handover;
3. every path the README advertises must exist.

It is not decoration: on its first run it failed, catching a README that still advertised the pre-split review
filename — a staleness introduced minutes earlier, by this same repair.

## E9 — what was corrected after adjudication, and what was deliberately not

The adjudicator's eleven conditions bind **successor** campaigns. Two classes were nonetheless actionable now,
and they were treated differently on purpose:

* **Documents were corrected.** `phase_6/C5_SELECTED_MECHANISM.md` now records the `x_lo > 0` domain exception
  (condition 3 — verified independently: exactly **2 of the 642** committed cover cells fail it, cell 0 of the
  CUSUM cover and cell 0 of the SR cover, both with `left = 0`, and `c5_transport` refuses both) and the narrowed
  independence claim (condition 4 — the mechanism and the improvement factor are surface-independent; every
  `Gamma_C5T`, every `M_factor_needed` and the whole fragility block are not).
* **Adjudicated evidence was NOT regenerated.** Conditions 7 and 8 would have changed
  `evidence/ledger/C5_ROUTE_LEDGER.json` and `evidence/forecast/C5_FORECAST.json`, whose exact bytes the
  adjudicator verified (`C5_FORECAST.json` sha256 `69cceb89…`). Both edits were made, both were then **reverted**,
  and the artifacts are byte-identical to what was adjudicated. The substance is carried in
  `OPEN_NOTES_DISPOSITION_C5.md` instead. Regenerating an artifact after it has been adjudicated, to add caveats
  the adjudication itself supplies, would destroy the reproducibility of the thing adjudicated for no gain.
