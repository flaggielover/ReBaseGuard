# Erratum to the frozen C8 decision gate (`config/DECISION_GATE_C8.json`, sha256 `55e74332…`)

The gate is **not amended**. It stays byte-identical and the producers still require its frozen sha.
These are corrections to statements the gate makes, raised by the independent adjudication.

## E1 — gate rule 1 embeds a false premise, and C8 followed the rule rather than overriding it

The gate's decision ordering says, verbatim:

> "1. If a cell is already passing under committed certified supplies, its blocker is ADOPTION, not
> information. Route = GOVERNANCE, and no new information may be requested for it."

**The premise is false.** Passing the clause does not imply adoption-blocked. C2's adjudication
(`C2_ADJUDICATION.md` §K) sets a **binding prospective adoption floor** — F1 supply independence
**or** F2 uniform-A margin ≥ 1.25 — and cell 306 passes the clause while failing **both** limbs. Its
blocker is therefore information after all, and rule 1 routes it to a governance step that cannot
discharge it.

**What C8 did.** Cell 306 needs only **1.067071×** and is the cheapest target in the tail. C8
nevertheless selects **cell 307 first**, because rule 1 as frozen forbids requesting information for
a passing cell, and a campaign does not get to override a frozen rule in its own favour — least of
all when the override happens to select the outcome the campaign prefers. C7's adjudication made
exactly that failure (KG8) a binding condition.

**Consequence.** `306-first` is available only if governance amends rule 1 and re-freezes the gate.
That is a decision for the programme, not for C8. Both figures are published so the choice can be
made on the numbers.

**A successor gate** should state rule 1 as: *a cell passing the clause AND satisfying the binding
adoption floor is governance-blocked; a cell passing the clause but failing the floor still needs
information.*

## E2 — `DATA_AND_TOOLCHAIN_BLOCKED` was not a permitted class

The gate enumerates the permitted classes and that compound is not among them. Route R5 is now
classed **`DATA_BLOCKED`**, with the toolchain obstruction named in the detail rather than fused
into a label the gate does not define.

## E3 — the exclusivity claim about route R4 is withdrawn

C8 stated that R4 was "the only route with leverage on cell 309". That is false against C8's own
sources. `C5_FORECAST.json` publishes **six** source-supply levers that void the cell-309 exclusion,
the cheapest being `all_four_together` at **0.6076 %** — cheaper than the sup-norm lever at 2.0562 %
that C8 did find. The claim is withdrawn in the live artifacts, not merely annotated.

## E4 — scaled sweeps are DIAGNOSTIC, not certified

C5 records `status: CERTIFIED for the clause values; DIAGNOSTIC for every scaled sweep`, because the
independent TC-T crosscheck is aligned to the frozen path whenever an ingredient is scaled. C8's own
sup-norm sweeps inherit that status and are now labelled `COUNTERFACTUAL_ONLY` and DIAGNOSTIC.
