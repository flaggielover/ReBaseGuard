# C2 disposition of the carried-forward notes (N1, N3, N5) and of the repaired (P3′) logic

Written before the C2 freeze. No predecessor namespace is edited.

## N1 / C7 — the order-3 producer's registry says no real CUSUM cell may be evaluated by it

**NOT LOAD-BEARING for C2 as executed. No bridge is issued, and the obligation is carried forward unchanged.**

C2 evaluates no order-3 quantity. Its own contribution is the refined operator registry, produced by the adopted
`taboo_certify`, which forms the kernel, its atom split, the one-step alarm probability and polynomial
supersolutions, and touches no source, no candidate of F/D/H/G, no K1 record and no value of R. The order-3 producer
namespace is never imported and its gated entry points are never reached. `NEW_REAL_ADDRESSES = 0`.

**N1 becomes load-bearing the moment the R stage runs, and C2's R-stage design says so explicitly** (`phase_r/`
§4). The bridge must be owned by the successor that evaluates the first real order-3 cell, must not edit the
historical registry, must state why that successor may use the qualified executor, and must bind executor identity,
protocol identity, runtime identity, the allowed address set, output schema, precision, resource cap, seal policy and
consumer — under independent review. C2 does not pre-empt any of that.

## N3 — the manufactured oracle covers r = 0 and m = 1

**Not widened by C2.** C2 alters no source-tower quantity, no W enclosure and no order-3 field; σ₃, σ₄, the h-tower,
`eps_src[*]`, `H_at_a` and `W2` are Campaign B's, byte-for-byte. C2 substitutes only A0, A1, A2.

C2 does add a second locally re-runnable adversarial suite (`code/c2_mutations.py`, **35 real mutants and 8 static
assertions** after the pre-freeze review, stdlib only) covering the source-node swap, the W endpoint swap, the order-3 field inserted at the wrong
location, the midpoint/whole-cell substitution and the omitted mean-value correction.

**Still open, and scoped to the R stage**: tail-geometry manufactured fixtures and exact independent cross-checks
for the source tower, the W assembly, the order-3 injection, whole-cell transport and consumer composition. C2 does
not need them because it proposes no candidate of F.

## N5 — the four new order-3 fields have no identity gate

**Remains retired for C2, by construction.** C2 inherits route TCT0 unchanged: Ĝ := 0, so `sup.G` and `abs_G_at_a`
are exactly zero, `delta_G` is a closed-form combination of identity-gated quantities, and `eps_src[3]` is the
adopted Aux3 value. The C2 consumer passes `order3 = None` on every call, and mutant `M09` confirms that inserting
an order-3 field at the wrong location is detected.

**For the R stage, N5 must be closed properly and "they can widen but not shift" is explicitly not enough**: the
four fields need bound and verified field names, semantic roles, source hashes, expected signs and ranges, the exact
insertion point, and mutation detection for each. C2's R-stage design lists this as a precondition, not an
afterthought.

## The repaired (P3′) logic

Preserved byte-for-byte and re-tested: σ₃ takes the midpoint tower (a (P2) premise at e₀), σ₄ takes the cell tower
with the mean-value correction (a (P3) premise, every e in the cell). Mutants `M01` and `M02` exercise exactly this
and are detected.

**C2's own new constants are whole-cell by construction and the refinement makes that tighter, not looser**: every
one of the six operator quantities is certified uniformly on a sub-block, and a cell takes the worst over a cover of
itself — an upper bound by maximum, a lower bound by minimum. Mutants `M11`–`M14` check that taking the best rather
than the worst sub-block, or swapping min for max on D_lo, is detected.

**That argument needs the cover to be a cover, and until the pre-freeze review nothing checked that it was.**
`M11`–`M14` perturb which sub-block row is *selected*; none of them perturbed the *geometry*. A partition with a
gap leaves part of the cell uncertified and the max/min composition is then not a whole-cell bound at all — a
direct soundness hole with no probe. The suite now verifies the tiling invariant (exact count `N_k = ceil(2ρ/(1/100))`,
row 0 starting at the cover's left edge, the last row ending at its right edge, contiguity, and every width
≤ 1/100) and carries three mutants against it: `M28` a gap, `M29` an overlap, `M30` an off-by-one short cover. All
three are detected, and the unmutated world is required to satisfy the invariant before any mutant runs.

## Notes opened by the C2 pre-freeze review

Full disposition in [`ERRATUM_C2.md`](ERRATUM_C2.md). Carried forward as open obligations on the successor:

- **N6 — the frozen gate's `why_gap_and_not_ratio` is directionally inverted.** Recorded in the erratum, **not**
  amended: a frozen pre-registration is not edited after a review, even to correct true errors in its prose. The
  clause that carries the argument is sound and nothing the gate decides changes. A successor gate must not copy
  the sentence.
- **N7 — the deterministic direction is not established as exhausted.** A sound operator-level combination C2 did
  not pre-register clears the gate's own 20 % bar on all three still-open cells at zero cost
  (`phase_d/D_PRIME_OPPORTUNITY.md`). **This blocks any R-stage authorization** and must be discharged by a
  successor D′ campaign, with its rule frozen first, before a real order-3 address is spent.
- **N8 — cell 306 has no margin floor that C2 can honestly set**, having already seen the margin. Referred to the
  adjudicator with C2's decision pre-committed in both directions (`phase_d/CELL_306_ADOPTION.md`).
- **N9 — the Arb/FLINT supersolutions remain the residual trust surface.** C2 has re-certified cell 306's eighteen
  artifacts, and re-run the whole-registry verification, on a host whose OS, architecture, Python and compiled
  Arb/FLINT build are recorded in the artifact — but this is still **one implementation**. A second, independently
  written certifier is the real answer and no campaign has built one.
- **N10 — the registry does not record the host that built it.** `REGISTRY_C2.json` carries no host, toolchain or
  precision field, and the worker's build log records only the registry summary, so the *build* host is reported by
  this campaign and recorded nowhere. Both verification artifacts record the host that *re-certified*, which is a
  different claim. The consequence is scoped in `phase_d/CELL_306_ADOPTION.md`: reproduction on a fully recorded
  host is what the evidence establishes, not reproduction across a recorded host *boundary*. Raised as note 4 by
  pre-freeze review r2, left undispositioned for five rounds, and failed by review r7. **A successor must have the
  registry builder record its own host, toolchain and precision into the registry at build time** — it is nearly
  free, and without it the "second host" half of the C1 reviewer's condition cannot be evidenced at all.
