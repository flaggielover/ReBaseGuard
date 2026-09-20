# Self-audit: does C2's change of residual measure flatter C2?

Written by the campaign against itself, before the pre-freeze review reported, because C2 changed the measure its
predecessor used and the honest test of such a change is whether it makes the campaign's own life easier.

## The change

Campaign C1 measured progress as a fraction of the **raw** required reduction factor, with a 10 % threshold. C2
measures it as a fraction of the **gap above 1** — the distance that must still be eliminated for a cell to close —
with a 20 % threshold, and says in its gate that C1's threshold is deliberately not inherited.

## The arithmetic, on C2's own numbers

| cell | C1 baseline requirement | C2 requirement | raw fall (C1's measure) | gap fall (C2's measure) | gap equivalent of C1's 10 % |
|---|---|---|---|---|---|
| 307 | 1.2620573 | 1.1407636 | 9.61 % — **fails** C1's 10 % | **46.29 %** — passes C2's 20 % | 48.16 % |
| 308 | 1.6634509 | 1.5002878 | 9.81 % — **fails** | **24.59 %** — passes | 25.07 % |
| 309 | 2.1015968 | 1.8990149 | 9.64 % — **fails** | 18.39 % — **fails** | 19.08 % |

**The gap measure is systematically more generous.** For any campaign,
`gap_fall = raw_fall × (1 + g₀)/g₀ > raw_fall`, so switching measures can only raise the reported figure. On these
numbers the effect is large: under C1's measure *none* of the three still-open cells would count as materially
tightened; under C2's, two of three do.

## Does it change anything that matters?

**No — the class is D_PARTIAL under either.** D_USEFUL requires that *every* still-open cell be materially
tightened. Under C1's measure that fails 0-of-3; under C2's it fails 2-of-3, because cell 309 misses either way
(9.64 % against 10 %, and 18.39 % against 20 %). The decision, the adopted subset and the R-stage routing are
identical under both measures.

## Is the change defensible anyway?

Two things are true at once and both belong in the record.

**The measure is right.** A cell closes when its requirement reaches 1, so the distance above 1 is exactly what
remains to be removed. A fraction of the raw factor is not scale-correct: it credits the same absolute progress
differently depending on how far the cell started from closing, and it systematically understates progress on a
nearly-closed cell. The last column shows the distortion — C1's uniform 10 % corresponds to 48 % of the gap at cell
307 and 19 % at cell 309, i.e. C1's measure demanded five times as much *real* progress at 307 as at 309 without
ever saying so.

**The threshold does not fully compensate, and the compensation is uneven.** Doubling 10 % to 20 % makes C2's test
slightly *stricter* than C1's at cell 309 (20 % vs an equivalent 19.08 %) and substantially *laxer* at cells 307 and
308 (20 % vs equivalents of 48.16 % and 25.07 %). C2 did not choose the threshold to achieve that profile — it was
frozen before any of these numbers existed, with the justification recorded in the gate — but the profile is what it
is, and a reader comparing C2's "materially tightened" flags against C1's would be misled without this table.

## What this audit left out, and the pre-freeze review supplied

This document was written before the review reported, and it audited **one** of the four things C2 changed. That
was incomplete in C2's own disfavour, which is the better direction to err, but incomplete is still incomplete. C2
changed four things at once, and two of them are strictly harder on C2:

| | C1's gate | C2's gate | direction for C2 |
|---|---|---|---|
| measure | fraction of raw requirement | fraction of the gap above 1 | **looser** where the gap < 1 |
| threshold | 10 % | 20 % | interacts with the row above |
| scope | the **worst** still-open cell, one test | **every** still-open cell must pass | **harder** |
| baseline | Campaign B (2.252903 at cell 309) | Campaign C1 (1.0 / 1.0 / 1.2621 / 1.6635 / 2.1016) | **harder** |

Apply **C1's gate verbatim** to C2's result and the arithmetic is: the worst still-open requirement is 1.8990149
against C1's frozen baseline 2.252903, a fall of **15.708 %**, comfortably past C1's 10 % bar; C2 closes 2 cells and
306 lies in C1's qualifying set {306, 307, 308, 309}. C2's class under C1's gate would therefore have been
**USEFUL**. Under its own gate it is **D_PARTIAL**. (C1's own fall on the same test was 6.716 %, which is why C1
was MARGINAL and stopped.)

So the complete answer to "does the measure change flatter C2?" has two halves that point opposite ways, and both
belong in the record:

- **On the measure alone — yes.** C2 reports the scale on which its numbers look 2.4× to 4.8× better, and that
  scale is what earns 307 and 308 their "materially tightened" verdicts. Under C1's measure none of the three
  would qualify.
- **On the gate as a whole — no, the opposite.** C2 wrote a gate that places it in a *lower* class than its
  predecessor's gate would have. Widening the scope from the single worst cell to every open cell, and moving the
  baseline forward from Campaign B to Campaign C1, cost more than the measure change gained.

What C2 should have done at publication, and did not, is state which way each of the four changes cuts, rather
than auditing the one change and leaving the other three unexamined. That omission is the substance of the review's
finding, and this section is the repair.

## Conclusion

The measure change is sound in principle, more generous in effect, offset by two changes that cut the other way,
and immaterial to C2's class and decision either way. A successor gate should set the threshold per cell from the
gap it starts with, rather than applying one number to gaps that differ by a factor of four — and should state, at
the moment of freezing, the direction of every change it makes to its predecessor's test.
