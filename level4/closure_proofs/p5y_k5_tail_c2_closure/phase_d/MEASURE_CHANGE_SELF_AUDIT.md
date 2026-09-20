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

## Conclusion

The measure change is sound in principle, more generous in effect, and immaterial to C2's class and decision. A
successor gate should set the threshold per cell from the gap it starts with, rather than applying one number to
gaps that differ by a factor of four.
