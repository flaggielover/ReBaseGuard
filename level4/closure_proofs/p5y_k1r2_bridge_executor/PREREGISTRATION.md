# Preregistration — P5Y-K1R2

Written, qualified, committed and frozen before any bridge computation. Not result-bearing.

## What K1R2 will do at production

1. **CUSUM bridge** — for cells 1000 and 1001 from the frozen bridge table, call the
   identical qualified kernel sequence on the bridge cell dict:
   `Aux3Certifier(cell, bits=256).prepare()` → `all_residuals()` → `aux_residuals()` →
   `aux_propagate.cell_obligations(whole_cell_refinement=refine2.refine,
   node_refinement_factory=AuxiliaryRefinement)` → `require_single_charge` →
   `tightening_report`. No kernel module is copied, patched or re-implemented.
2. **SR bridge** — for cells 2000–2005, run the qualified PS1 SR executor on AWS under the
   new bridge authorization and bridge owners map.
3. Seal each record independently; then compose with the inherited compact covers and the
   inherited P5X-T3 far field exactly as K1R's `DOMAIN_COVER.json` specifies.

## Gates

Every frozen K1R kill gate applies unchanged: `G_SCIENCE` (an enclosure reaching target 2
halts and is reported, never refined around), `G_COVERAGE`, `G_BUDGET` (depth 0 — a cell over
budget halts, it is never re-split), `G_GOVERNANCE`, `G_COST` (halt *before* 150 CPU-h),
`G_SCOPE`. K1R2 adds two: **bridge-only resolution** (a historical cell id is refused as new
work) and **kernel identity** (any drift in the 11 CUSUM modules or the 39 SR executor files
halts).

## What would make K1R2 halt rather than proceed

Any of the above; a C_upper recomputation that disagrees with the frozen witness; a bridge
width exceeding the frozen step rule; or a demand to change the inherited equations,
thresholds, precision, domains or m universe — that would be scientific redesign, not a
governance successor, and is out of scope by construction.

## What K1R2 does not do

It does not rerun B1, reopen the Aux5 admission, rewrite the K1R halt, touch a historical
producer identity, or decide K1. Closing B2 and B3 still needs independent adjudication.
