# P9R repair rationale — why each repair takes the shape it does

## 1. Why a new lineage rather than an edit

P9's defects are not typographical. Two of them (the temporal class and the
theorem-scope inflation) are properties of *how P9 was produced*, and editing
P9's files would destroy the evidence that produced the `PARTIAL` verdict. The
adjudication's own next action was "create a temporally anchored P9R repair".
So P9 is frozen and P9R is a new namespace with its own anchor.

`P9 = PARTIAL` remains the authoritative status of Priority 9 regardless of what
P9R is adjudicated to be. A `CLOSED` P9R would close the Priority-9 **repair**
lineage, exactly as `P8R = CLOSED` closed the Priority-8 repair lineage while
`P8 = FAIL` stayed.

## 2. Why the theorem is split rather than proved

The tempting move is to prove global monotonicity of `A` and keep `P9-T2` exact.
P9R declines, for two reasons.

*It is not available cleanly.* A proof would need a stochastic ordering showing
that a nonzero entering error can only accelerate a two-sided detector,
uniformly over the reset state, for both the CUSUM and the SR chart. Nothing in
P1-P8 supplies that. Producing it under closure pressure is precisely the
behaviour that produced the `PARTIAL` verdict.

*It is not necessary.* The strict-deficit argument needs only that `A` attains
its maximum at `0` almost everywhere (`ASM-DOM`), which is strictly weaker than
monotonicity. And the *strict* half needs nothing extra at all: `L3` (`A(0)>1`)
and `L4` (`A(e) -> 1`) already put `A` strictly below `A(0)` on a positive-measure
set. Isolating `ASM-DOM` therefore produces a **stronger** conditional theorem
than simply relabelling P9's proof, while making the gap smaller and easier for
a future campaign to attack.

## 3. Why the SR recurrence is rebuilt rather than patched

The adjudication's instruction was explicit: do not copy P9's implementation and
change a constant. Two independent reasons make that the right call.

A one-character fix would leave the *reason* for the defect in place — P9 stored
the alarm statistic in the slot that must hold the state. The repaired module
names the two quantities separately (`ell` = `log R`, the alarm statistic;
`y` = `log(1 + R)`, the stored state), so the confusion cannot recur silently.

And the defect must be *measured*, not just removed. `detectors.py` therefore
keeps the defective update as an explicitly named, never-scientifically-used
function, so `run_reproduction.py` can replay every SR cell both ways on
identical seeds and report the difference. Preserving the discrepancy is a
requirement, not a courtesy.

## 4. Why the ledger is rebuilt from source

P9's ledger validated at zero rank violations while carrying real inflation,
because the validator checked each claim's **self-assigned** class. A ledger that
grades its own homework cannot detect a promotion.

P9R's ledger is generated from `claims_source.py`, in which every row carries the
authoritative path *and the section* it was read from, and `build_ledger.py`
re-reads those paths (rule `V8`). The rules that matter are the ones that cannot
be satisfied by relabelling: an `EXACT_THEOREM` may take no `ASSUMPTION` edge
(`V2`), may take no conditional/empirical/certified `LOGICAL_PREMISE` (`V1`), and
may not contain monotonicity wording in its statement (`V11`).

## 5. Why P7-A had to be split into three nodes

P9's `P7-A` node asserted, in one `EXACT_THEOREM` row, both the exact
finite-cycle identity **and** that `A` is even and non-increasing in `|e|`. Every
downstream edge then inherited an exact-looking premise that was partly
unproved. Because downstream consumers need *only* the identity, the node is
split:

* `P7-A-ID` — the exact identity. This is what `P9R-T2a` consumes.
* `P7-A-MONO` — `NOT_ESTABLISHED`, quoting P7's own adjudication.
* `P7-A-OP` — `EMPIRICAL_ONLY`, the grid observation.

`P7-D0` is split the same way into `P7-D0-ID` (exact mixture identity) and
`P7-D0-DEF` (conditional reduction). This is what "a dependency graph must not
hide a premise inside a node" means operationally.

## 6. Why edge types are typed, and why the collapse is demonstrated

Typing is necessary: a Lean kernel check *about* a theorem is not a premise
*of* it, and a measurement consistent with a claim does not license it. But
typing is not sufficient — P9 had typed edges and still hid the premise. So
P9R adds `ASSUMPTION` as a first-class edge type, forbids `EXACT_THEOREM` from
carrying one, and runs the validator a second time on a **collapsed** copy of
the graph in which every edge is flattened to `LOGICAL_PREMISE`. The violation
count from that run is published: it is the concrete evidence that an untyped
representation of this project's evidence is unsound.

## 7. Why A5/A6 are regenerated rather than retired

Retiring them was permitted. Both were kept because both are load-bearing after
the narrowing, not merely for continuity:

* the response grid (A6) is the only quantitative evidence *for* `ASM-DOM`, and
  it is what makes `GLOBAL_MONOTONICITY = EMPIRICALLY_SUPPORTED` a defensible
  status rather than a guess. Its quadrature error, left unquantified by P9, is
  now a three-part budget whose truncation term is *rigorously* bounded by
  Lemma L2;
* the burn-in sensitivity (A5) is what allows P9R's reproduction to be
  **convention-matched** to P7's `burn_in = 12` instead of explaining a gap
  after the fact.

Both now have deterministic generators, seeds derived from a namespaced address,
full provenance records, and focused tests including a reduced deterministic
regeneration.

## 8. Why the operational claim is narrowed

"No conceivable `rho`-based operational boundary can ever exist" quantifies over
objects P9 never tested. The defensible statement is about the frozen models and
the frozen criterion: `rho < rho_c` does not *guarantee* nominal-ARL
preservation there. That is enough to retire `rho_c` as a safety rule, which is
the operational point, without asserting an impossibility.
