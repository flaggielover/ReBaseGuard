# Independent pre-forecast review — Campaign C3 (P5Y / K5 CUSUM m = 5 tail)

**VERDICT: READY_WITH_NOTES**

Target: worktree `/Users/suzhe/ReBaseGuard-k5c2`, branch `p5y-k5-tail-c3`, HEAD `94bc0ad3`, namespace
`level4/closure_proofs/p5y_k5_tail_c3_closure/`. Review date 2026-09-21. No C3 forecast exists, and this review did
not create one.

None of the eleven notes below is a precondition for computing the C3 forecast. Three of them (N1, N2, N4) are
corrections that the forecast's own narrative must carry so that a later adjudicator is not misled; the rest are
hardening recommendations. **C3 is cleared to proceed to its forecast.**

---

## Reviewer context — what I re-derived, and what I did not

I am an independent fresh-context reviewer. I wrote none of this work and had no prior knowledge of it. I read
`THEOREM_AD.md`, `deflated_consume.py`, `c2_d5_forecast.py`, the C1 and C2 registries, C2's frozen gate, C2's
adjudication and its open-notes disposition, and all eight C3 artifacts, and then re-derived the following myself
rather than accepting any of it:

**Re-derived independently (exact rational arithmetic, `fractions.Fraction`, `PYTHONINTMAXSTRDIGITS=0`):**

- **Both C3 evidence artifacts regenerate bit-identically** from their producers on this host.
  `c3_blocker.py` → sha256 `d69a4500cb97bd09f04806d33481bf44ac8b393c4cfc160b8b987d289784d432`, identical to the
  committed `evidence/phase_c1/C3_BLOCKER.json`. `c3_mutations.py` → sha256
  `76a8eb0f2d30c53f626774291ba572bec155dd47568490d11c2142e1ed3fe38e`, identical to the committed
  `evidence/preforecast/C3_MUTATIONS.json`.
- **The Lemma Dv′ premise set actually enforced** by `deflated_consume.atom_constants_r2`, read from source:
  `τ ≥ 1`, `C ≥ τ`, `D_lo > 0`, `Ā ≥ 1`, all six nonnegative `Fraction`s, and `r2 ≤ r1` componentwise, each raising
  `DeflationRefusal`. The gate's description of this is accurate.
- **Every atom-constant value the selector produces, recomputed through a second, independent implementation** of
  Lemma Dv′ (`c2_d5_forecast._atom_independent`, which shares no function with `deflated_consume`). It agrees
  exactly with `DC.atom_constants_r2` on the mixed tuple on all four cells.
- **The per-field provenance of the mixed tuple** on all four cells: `τ`←C1, `C_T`←C1, `D1`←C2, `D2`←C2,
  `D_lo`←C2, `Ā`←tie (see N5). Identical on 306, 307, 308 and 309.
- **Structural claim K(a)**, the dominance of the componentwise-best tuple: verified *strictly* on all three atom
  constants against all three of Lemma G, C1 and C2, on all four cells (12/12 comparisons, strict in `A0`, `A1`
  and `A2` each time).
- **Structural claim K(b)**, and a stronger variant the analysis does not state. The constant-level distributivity
  (`max_i min(a, b_i) = min(a, max_i b_i)`, dually for `D_lo`) is an identity on totally ordered sets and needs no
  data. I additionally tested the genuinely different construction the claim's wording could be read to cover —
  applying Lemma Dv′ *per sub-block* and taking `max_i A_j` afterwards, which by monotonicity is `≤ A_j(worst
  tuple)` and could in principle be strictly tighter. It is **exactly equal**, ratio `1.000000000000` on every
  `A_j` on every cell, for both the C2-alone and the mixed construction, because sub-row 0 is the worst sub-block
  in all five per-sub-block fields on all four cells. The "no gain" claim therefore holds in the stronger sense too.
- **Claim K(c)**, the two baseline columns, from the requirement figures: vs r5 **20.457947 / 7.922037 /
  5.688601 %**, vs C1 **57.274132 / 30.566862 / 23.032317 %** for 307 / 308 / 309. Both columns are arithmetically
  correct and the gate's rounded values match.
- **That the C2 block-level constants are the worst over their sub-rows**, exactly, as rationals, for `τ`, `C_T`,
  `D1`, `D2` (max) and `D_lo` (min), on all four cells — the property `whole_cell_ok` needs but does not itself
  check (N6). Also that the sub-rows tile `[e0−ρ, e0+ρ]` exactly with max width `≤ 1/100`, and that both registries'
  `e0`/`ρ` match the cover ledger `cells.json` exactly.
- **The r5 open set**, read from `K5_COVERAGE_MAP_R5.json` itself: `K5_COVERAGE_COMPLETE=false`, m=1/2/3 fully
  closed, m=5 open on exactly `{306, 307, 308, 309}`, `union_open_ranges [[306,309]]`, count 4.
- **All eight sha256 claims in `C3_B0_AUDIT.json`** — r4, r5, and C2's gate, qualification, authorization,
  execution, seal, consumption and adjudication — each resolved back to the file it names.
- **Gate immutability and branch additivity**, from git plumbing (read-only): the gate blob is `d231250e` at both
  `24c038ec` and `HEAD`, one commit has ever touched it, and `git diff ae4cbc2c HEAD` outside the C3 namespace is
  empty.
- **Two adversarial probes of my own**, outside the suite (N8, N9, and the cleared point in section D).

**Not checked.** The Arb/FLINT certification artifacts behind either registry — I did not re-run `taboo_certify`
or the ARL supersolution certifier, so the six operator constants are accepted as certified by their campaigns.
The adopted K1 record store is not present on this host; I used the committed `ADOPTED_TAIL_INPUTS.json` and
`TCT_INPUTS_*.json` extracts as C3 does. I did not re-verify theorem TC-T, K5-B, or the frozen K1 error algebra —
I checked only that C3 consumes them unchanged and adds nothing to them. I did not exercise the FLINT venv. I did
not contact AWS or any remote host, and ran nothing that touches `/root/work`.

---

## A. Is C3 genuinely pre-registered before forecast? — **PASS**

The gate is frozen and unmodified. `config/FEASIBILITY_GATES_C3.json` hashes to
`f0bd87ecaeea4485560969770c95c9d4ad20bceedf9ac7ca11fb6d8d5de53ac7`, exactly the `GATE_SHA` pinned in
`c3_selector.py:25`. Its git blob is `d231250e4e1f1f7954c16f7ee30961afeb1f77bf` both at `24c038ec` and at `HEAD`,
and `git log --all -- <gate>` returns exactly one commit. There is no second version and no amendment.

The ordering is right. `24c038ec` (B0 audit, blocker reconstruction, gate freeze) precedes `94bc0ad3` (mechanism
and adversarial suite) by four minutes; the gate is in the *earlier* commit, so the mechanism was implemented
against an already-frozen gate rather than the reverse.

No forecast artifact exists, predates the gate, or accompanies it. The namespace holds exactly eight files;
`git status --porcelain --ignored` over it is empty, so there is no untracked or ignored forecast either. There is
no `c3_forecast.py` anywhere in the repository — `c3_selector.py:13` names it as the future home of
classification, which is the correct separation: the selector computes and does not decide. The only repository
file matching `*C3*` outside this namespace is `rebaseguard-lean/C3_PROGRESS.md`, an unrelated Lean Gate-4.5
artifact.

One qualification, which belongs here and which the campaign states itself: pre-registration here is *procedural*,
not *epistemic*. The gate openly discloses the mixed-supply Γ for all four cells under
`prior_evidence_known_at_freeze`. C3 knew the numbers before freezing. That is unavoidable — they are computable
in three seconds from committed predecessor artifacts — and disclosing them is the correct handling. Whether the
disclosure functions as a laundering device is section F.

## B. Is the mixed-operator rule mathematically sound? — **PASS**

Yes. The claim checks out against `THEOREM_AD.md`, and there is **no hidden joint constraint** that componentwise
mixing can violate.

The decisive structural fact is in §8's registry-obligation table: each of the six constants is a bound on a
quantity of the **true operator family** `{K_e : e ∈ B}`, not on anything belonging to the source that certified it.

| constant | the quantity it bounds | source-dependent? |
|---|---|---|
| `τ` | `sup_B E_a[τ ∧ T_a]` (Lemma T) | no |
| `C_T` | `sup_B ‖Ĝ_e‖` (Lemma T) | no |
| `D_lo` | `inf_B D_e` (Lemma SM) | no |
| `D1` | `sup_B |D′|` (Lemma Dv) | no |
| `D2` | `sup_B |D″|` (Lemma Dv) | no |
| `Ā` | `sup_B E_a[τ]` (Lemma Dv′) | no |

Because all six are bounds on the *same six fixed quantities*, two valid certificates give two true inequalities
about one number: `τ_a ≤ τ_C1` and `τ_a ≤ τ_C2` give `τ_a ≤ min`, and `D_e ≥ D_lo,C1` and `D_e ≥ D_lo,C2` give
`D_e ≥ max`. That is intersection of bound sets on one domain. It is a conjunction of deterministic inequalities,
not an average, so no independence assumption arises and shared assumptions are harmless to *soundness* (the gate
is right to add that they are not harmless to *robustness*, which is what the adoption floor is for).

I checked the Lemma Dv′ proof line by line for any place a constant enters other than through its own inequality.
There is none. `|ν_e(f)| ≤ τ‖f‖` uses `τ` alone; `|∂ν_e(f)| = |δ_aĜK̂′Ĝf| ≤ τκ₁C‖f‖` uses `τ` once at the
leftmost `Ĝ` (through `δ_a`) and `C` once at the rightmost, each through its own bound; `|∂²ν_e(f)| ≤
τ(2κ₁²C² + κ₂C)‖f‖` likewise; the quotient rule uses `D ≥ D_lo`, `|D′| ≤ D1`, `|D″| ≤ D2` separately. `κ₁`, `κ₂`
are universal (Lemma K), not per-source. `Ā_eff = min(Ā, τ/D_lo)` is a minimum of two independently valid bounds
on `E_a[τ]` — `Ā` from the whole-kernel supersolution, `τ/D_lo` from Lemma SM(d) — so it is valid whichever is
smaller, and from whichever sources they came.

The one clause in the lemma that looks like a joint constraint is `C ≥ τ`, and it is worth being precise about it.
For a single Lemma T supersolution `w`, `τ_a ≤ w(a) ≤ sup_X w = C_T`, so `C ≥ τ` is automatic. For a mixed tuple it
is not: a loose `τ` from one source could exceed a tight `C` from another. But `C ≥ τ` is **not required for the
Dv′ bound to be valid** — the proof never uses it — and `atom_constants_r2` enforces it anyway, *raising* rather
than returning. So the check can only cause refusal; it can never admit an invalid tuple. The direction is safe.

Existence of `Ĝ_e` and the convergence of `Σ_j K̂_e^j` needs *some* valid supersolution on the drift set; both
sources supply one, so existence is established twice over and does not depend on which components are selected.

`c3_selector.build` enforces exactly this: the mixed tuple is passed to the pinned consumer, which raises on any
premise failure, and the cell then falls back (`premise_fallback`) to the best single source. I confirmed the
premises hold with room on the real mixed tuple on all four cells (`τ ≥ 1`, `C ≥ τ`, `D_lo > 0`, `Ā ≥ 1`), with no
fallback and no rejection.

## C. Is component compatibility justified? — **PASS. Component mixing is sound. The route is not dead.**

This is the question that could have stopped C3, so I will answer it directly and then say exactly where the risk
would have been.

**Yes — `τ` from one source may legitimately be combined with `D_lo` from another.** The coupling the question
worries about is real but lives entirely in the *derivation*, not in the *conclusion*, and mixing consumes only
conclusions.

Concretely: Lemma T derives both `C_T = sup_X w` and `τ = w(a)` from one supersolution `w`. §8 further records
that `D_lo`'s certificate is built from a candidate for `d = Ĝ h_1` "with tame error `τ·residual`, extended over B
by `|D′|`" — so a campaign's `D_lo` is computed using *its own* `τ` and `D1`. That is genuine derivational
coupling. It does not propagate, because what each campaign publishes is a completed certified inequality about an
operator-intrinsic quantity: C2's `D_lo ≤ inf_B D_e` was established using C2's (larger, hence more conservative)
`τ`, and remains true as a statement about `inf_B D_e` no matter what `τ` is used downstream. Substituting a
*smaller* valid `τ` elsewhere cannot retroactively weaken a bound that was certified with a larger one. Mixing
would only be unsound if some constant were defined *relative to its source* — e.g. "the value of `w` at `a`" as
opposed to "a bound on `E_a[τ ∧ T_a]`". §8's table shows none of the six is.

The place this actually bites in C3 is worth naming, because it is load-bearing. On all four cells the selector
produces `Ā_eff = τ/D_lo` rather than `Ā` (I checked: `Ā > τ/D_lo` on every cell, so the whole-kernel `Ā` channel
is inert). So `A0` is literally **`τ` from C1 divided by `D_lo` from C2** — the sharpest possible instance of
cross-source mixing, and it is the quantity the whole campaign rests on. It is sound: `τ_C1 ≥ τ_a(e)` for every
`e` in the cell, `D_lo,C2 ≤ D_e` for every `e` in the cell, therefore `τ_C1/D_lo,C2 ≥ τ_a(e)/D_e = E_a[τ]` at the
same `e`, uniformly. The step that makes this work is that **both bounds are uniform on the whole cell, so they
hold simultaneously at every `e`** — which is precisely why section D's whole-cell premise is not a formality.

Two further observations that strengthen the position rather than weaken it. First, the one genuinely coupled pair
in the lemma — `(τ, C_T)`, which share a supersolution — happens to be drawn from a **single source (C1) on all
four cells**, so even a reviewer who insisted on preserving Lemma T's internal pairing is satisfied on this data.
Second, `Ā` is a tie between C1 and C2 and is inert anyway, so the only cross-source pairings that do any work are
`(τ_C1, D_lo,C2)`, `(C_T,C1, D1_C2)` and `(C_T,C1, D2_C2)` — all pairings of constants from *different* lemmas
(T vs SM/Dv), which never shared a certificate object to begin with.

## D. Are whole-cell premises enforced? — **PASS_WITH_NOTES**

`whole_cell_ok` is correct for what it checks, and what it checks is the right thing. For C1 it requires the
block's `[e_lo, e_hi]` to equal `[e0 − ρ, e0 + ρ]` taken from the **cover ledger** `cells.json`, not from the
block's own self-reported geometry — the right source of truth. For C2 it sorts the sub-rows by `e_lo` and
requires `rows[0].e_lo == lo`, `rows[-1].e_hi == hi`, and `rows[i].e_hi == rows[i+1].e_lo` throughout. Given
sorted order those three conditions are equivalent to an exact tiling, so the check is sound. I verified all three
hold exactly, as rationals, on all four cells, and that both registries' `e0`/`ρ` match the ledger exactly.

I probed for a way to make the tiling check accept a cover with a gap. There is none, and the reason is
structural: an accepted chain `lo = a₀ → a₁ → … → aₙ = hi` in which each row is `[a_i, a_{i+1}]` **is** a genuine
tiling regardless of the order in which the rows were presented, so no alternative ordering can invent a cover
that does not exist — it can only fail to find one that does. I confirmed this concretely: a mutant deleting the
`sorted(...)` call is behaviourally identical on the real data and, on a world with shuffled sub-rows, *rejects*
C2 (pessimistic), never accepts a bad cover. The suite's omission of such a mutant is therefore consistent with
its declared scope ("planted where an error would produce an artificially optimistic result"), and I record this
as checked and cleared rather than as a gap.

It is **not sufficient on its own**, in one respect. The selector reads the *block-level* fields `b["τ"]`,
`b["C_T"]`, … , but `whole_cell_ok` validates the *sub-row* geometry. The bridge between them — that the
block-level constants are the worst over the sub-rows, and that `Ā` comes from a block-level ARL certificate
covering the whole cell — is an inherited property of the C2 registry that C3 nowhere re-checks (N6). I verified
it externally: `c2_refined_registry.py:160-166` constructs the block fields as `max` over sub-rows for the four
upper bounds and `min` for `D_lo`, with `Ā` taken from the whole-cell `arl` certificate; and I confirmed the
committed values satisfy this exactly on all four cells. So the premise is true — it is simply assumed rather than
enforced.

One conservatism worth recording: the C1 branch demands exact endpoint *equality*, so a block strictly **wider**
than the cell — a perfectly valid and more conservative certificate — is rejected. I confirmed this by widening
C1's `e_hi` by 1/1000 and watching all four cells reject C1. The direction is safe (it can only forfeit
tightening, never admit an invalid bound), but it is "equals", not "contains" (N9).

## E. Can the selector cherry-pick result-dependent components? — **PASS_WITH_NOTES**

No. `build()` is a pure function of `(cell, C1 block, C2 block, cover, meas)` and the two pinned theorem modules.
It computes no Γ, sees no Γ, and reaches no classification — Γ is computed downstream by `c2_d5_forecast.direct`,
after `A` is already fixed. There is no path by which a component could be chosen after a result exists.

Determinism is complete. All comparisons are exact `Fraction` comparisons with no tolerance and no float anywhere
on the selection path. Every `sorted` call carries an explicit total-order key. Dictionary iteration order is
insertion order and is fixed by construction: `sources = {"C1": …, "C2": …}`, `usable` preserves that order by
comprehension, and `supplies` is built `G`, then the usable sources in order, then `operator_mixed` last.

Tie handling is sound. `operator_best` breaks ties on `(value, name)`, so the lexicographically first source name
wins and is recorded in `operator_provenance`. Ties do occur on real data — `Ā` ties on all four cells (N5) — and
the recorded provenance is `C1` for all of them, deterministically. Since the tied values are equal the choice is
numerically immaterial; it matters only for the provenance record, which is what it is there for.

Two structural observations, neither a defect:

The ordering of `operator_best` (line 88) *before* the per-source premise check (lines 104-107) means a source
whose own constants violate a Dv′ premise still contributes components to the mixed tuple, while being excluded
from `supplies`. That looks alarming and is in fact correct: `C < τ` at the source level does **not** imply either
bound is invalid (a loose `τ` and a tight `C` can both be true), so excluding such a source's components would be
over-conservative, and the mixed tuple is guarded by the consumer regardless. The code's comment (lines 101-103)
gives the right reason for the ordering — it keeps the mixed-tuple guard observable. What is under-documented is
that `rejected_sources` now carries two dispositions with different consequences (N10).

The `frozen_gate()` / `GATE_SHA` pin is defined but **never called** on any existing code path (N3). Pre-forecast
this is not yet a defect — the consumer, `c3_forecast.py`, does not exist — but it is a carry-forward requirement.

## F. Is the gate prospective rather than outcome-fitted? — **PASS**

**Plainly: the disclosure is not a laundering device, and the gate is genuinely non-fitted.** I say this having
looked specifically for the opposite, and I would have said the opposite had I found it.

The gate is not epistemically blind and does not pretend to be. It publishes the mixed-supply Γ for all four cells,
publishes that 306's best uniform-A margin is 1.1555 against a floor of 1.25, and states in terms that "C3 expects
PARTIAL … and does not adjust it". Blindness was never available — every one of those numbers is three seconds of
arithmetic away from committed C2 artifacts, which is exactly what `c3_blocker.py` does. So the only question that
can be asked is the one the review asks: given that C3 knew, did it choose rules that fit what it knew?

It did not, and the reason is that on every consequential parameter **C3 had no degrees of freedom left to abuse**:

- **The adoption floor is not C3's.** It was set by the independent C2 adjudicator, in `C2_ADJUDICATION.md`
  (sha `f37dae47…`), before Campaign C3 existed. I read that adjudication. It does not merely predate C3 — it
  **anticipates this exact campaign and pre-rejects it by name**: "1.1555 — better, but still short of F2 — so I
  should be plain that a D′ campaign **alone will not discharge this floor for cell 306**." The adjudicator also
  defends the ×1.25 severity as C2's own invention, applied to all five cells and published against the campaign's
  interest before any adjudicator existed. C3 could not have weakened this floor without visibly overruling an
  independent adjudicator who had already ruled on precisely this case.
- **The 20 % material-tightening threshold is not C3's.** It is C2's frozen gate verbatim, including the
  gap-based (not ratio-based) measure, set there "with no forecast in hand" and explicitly *declining* to inherit
  C1's more flattering ratio threshold. C3 inherits the incumbent standard. Raising or lowering it for a successor
  that already knows its approximate prior would have been the suspicious move, and the gate says so.
- **The one free choice C3 made, it made against itself.** Nothing compelled C3 to measure against r5 rather than
  C1. Choosing r5 converts its own headline result from **57.27 / 30.57 / 23.03 %** to **20.46 / 7.92 / 5.69 %** —
  a factor of roughly three — and, materially, moves 308 and 309 from comfortably above the 20 % threshold to
  clearly below it. C3 chose the baseline under which its own tightening fails the test on two of three cells.
  That is the signature of a gate written against its author's interest, not for it.
- **C3's PARTIAL branch is stricter than its predecessor's.** C2's gate, at `D_PARTIAL`, says "ADOPT THE CLOSED
  SUBSET ANYWAY" and argues for it at length. C3's PARTIAL says "propose NOTHING for adoption … Publish the
  negative result. A candidate closure that fails the floor is not adopted merely because it exists." C3 gave up
  an adoption its own predecessor's gate would have granted.

What C3 *did* author are the class definitions and their evaluation order. I checked these for fitting and found
none: the order `USEFUL → PARTIAL → MATERIAL_TIGHTENING_ONLY → MARGINAL → INVALID` is the natural severity
ordering, and `PARTIAL` and `MATERIAL_TIGHTENING_ONLY` are in any case mutually exclusive by their own definitions
(the latter requires no cell to have Γ < 0), so the ordering between them is inert and cannot have been chosen for
effect.

The honest summary is that the disclosure does not *make* the gate non-fitted — inheritance does. The disclosure
is what lets a reviewer check the inheritance. Both are present, and they hold.

## G. Are cell-306 adoption semantics prospective? — **PASS_WITH_NOTES**

Yes, and applying the floor to every cell identically with no carve-out is right. The floor is a general rule over
Γ and a fixed severity, not a per-cell threshold: F1 asks for closure under a supply that does not rest on the
Arb/FLINT `taboo_certify` surface, F2 asks for survival of a uniform ×1.25 degradation. Both limbs are stated
before any C3 number is consumed, and `applies_to_cell_306: "yes, identically to every other cell"`.

The substance is correct. Lemma G — the only registry-free supply available — leaves 306 open at Γ = +0.019115585,
so F1 fails; and 1.1554876238748288 < 1.25, so F2 fails. I reproduced both from `C3_BLOCKER.json`, which I
regenerated bit-identically. C3's own blocker analysis says all of this before the gate is frozen and declines to
weaken the floor, which is the correct handling.

A carve-out would have been the defect here, and there is none. More than that: the mixed supply is componentwise
**≤ Lemma G**, so it is strictly *more* dependent on the registry surface, and the blocker analysis says so —
mixing makes 306's independence position formally worse, not better. A campaign fitting a gate to its answer does
not volunteer that.

One fidelity gap. The gate says C3 "inherits it verbatim and does not restate, reinterpret or soften it," but the
gate's text is a **condensation**, not the adjudicator's words, and it drops one clause: the adjudicator's F1 is
"available for as long as **N9** … remains open, and lapses when N9 is closed." N9 is open (I confirmed in
`OPEN_NOTES_DISPOSITION_C2.md`: "A second, independently written certifier is the real answer, and C2 has not
built one"), so the condensed F1 and the adjudicator's F1 are operationally identical today and the floor C3 will
apply is the correct one. But "verbatim" is not accurate, and the dropped clause is the one that would make C3's
floor *weaker* than the adjudicator's if N9 ever closed (N2).

## H. Is the mutation suite adequate? — **PASS_WITH_NOTES**

Adequate, and better designed than most. The suite regenerates bit-identically, and the mutants are real: eight
source mutants applied by anchored textual substitution (anchor uniqueness checked, `applied: false` if not), five
data mutants that perturb the registries, plus a synthetic tie world.

**The "every mutant against every world" design is sound and does not mis-credit.** Each source mutant is compared
against `base_by_world[w]` — the *unmutated* selector's behaviour **in that same world** — so detection always
means "this mutant changed behaviour relative to correct behaviour under identical inputs". `caught_by` names the
specific world and the specific field and cell (`M11…:A@306`), and `worlds_that_exercised_it` is exactly the set
where behaviour differed. A mutant cannot be credited to a world that does not exercise it; the results bear this
out, e.g. M04 (premise check swallowed) is credited only to M11, and M06 (tiling gap accepted) only to M10 — the
worlds that actually make those guards fire. This design is the right answer to the standard failure mode where a
guard mutant is invisible on well-formed data and is scored as "equivalent" by default.

**The M08 equivalence proof is valid but narrower than it reads.** The mutant drops the source name from
`operator_best`'s upper-bound sort key. The argument — sources are inserted in lexicographic order and Python's
sort is stable, so a value-only key and a `(value, name)` key select the same element on a tie — is correct, and
the code does construct an all-equal probe and check both keys select `'C1'` rather than asserting it. But
`names = ["C1", "C2"]` is **hardcoded in the proof**, not read from the selector under test. I confirmed the
selector's literal is `{"C1": c1b, "C2": c2b}` so the premise is true today; the proof would nonetheless still
print "equivalent" if that literal were reordered (N7).

**Load-bearing mechanisms with no mutant.** Four, all checked by hand:

1. `combine_A`'s tie-break has no mutant and no equivalence proof, and — importantly — **M08's argument does not
   transfer to it**, because its `supplies` dict is inserted `G, C1, C2, operator_mixed`, which is *not*
   lexicographic order. I worked through it: on a tie the `A` values are by definition equal, so only the
   provenance label could differ and both variants remain deterministic. Inert, but unproved (N8).
2. `if not usable: raise SystemExit` is unreachable in every world, because no world breaks both sources (M09
   breaks C1; M10 and M13 break C2).
3. The per-source premise rejection (lines 104-107) has no source mutant, though world M11 does exercise the path.
4. The `frozen_gate()` pin has no mutant and no caller (N3).

**The headline count is wrong.** `applied: 13, detected: 13, undetected: [], pass: true`. M08 was **not**
detected — its own row correctly records `detected: false, equivalent: true` — and the summary's arithmetic
(`detected = applied − undetected`, with equivalents excluded from `undetected`) silently promotes it. The honest
statement is **12 killed, 1 proved equivalent, 0 unexplained** (N4).

One dead branch: the `M03_A_level_takes_max` equivalence block only executes if M03 was undetected, which it never
is; it is unreachable in practice.

## I. Is predecessor / C2 / r5 integrity preserved? — **PASS**

Fully. `git diff ae4cbc2c HEAD -- . ':(exclude)level4/closure_proofs/p5y_k5_tail_c3_closure'` is **empty** — C3's
two commits touch nothing outside their own namespace. Both commits are pure additions (746 and 646 insertions, 0
deletions, 0 modifications). The branch descends from C2's head `ae4cbc2c`, which I confirmed with
`git merge-base --is-ancestor`.

The predecessor artifacts hash to their recorded values: r5 `e2197051…`, r4 `a3bddd83…`, C2's adjudication
`f37dae47…`, gate `098dd7f5…`, qualification `336637a7…`, authorization `d0ebd06d…`, execution `3cd60254…`, seal
`abf463a8…`, consumption `4a89a719…`. `main` is `c123b9bb`, exactly as `C3_B0_AUDIT.json` records, and untouched.
The C3 namespace has no untracked or ignored files. C2 is read-only in fact, not merely by intention: the C3 code
opens its registries and modules for reading and writes nothing into it.

I confirmed for my own part that I modified no file other than this review.

## J. Is any new-real computation authorized or reachable? — **PASS_WITH_NOTES**

Guard `REAL_SCIENTIFIC_COMPUTE = DENY` is stated in both the gate and the B0 audit;
`new_real_scientific_addresses_authorized` is `0`. This is not only declared but structurally true:

- **No AWS, no network, no subprocess.** A grep of all three C3 modules for `boto`, `aws`, `ssh`, `urllib`,
  `requests`, `subprocess`, `socket`, `k4_records`, `record_store` and `/root/work` returns nothing. I contacted
  no remote host during this review.
- **No R-stage.** There is no R-stage code, design or sub-gate in the namespace.
- **No order-3 candidate.** `order3` is `None` on every path, and not by convention: `c2_d5_forecast.direct`
  hardcodes `T.tail_enclosure(R, meas, aux, A, 5, None)` and its crosscheck likewise, and `c3_blocker.py:101`
  passes `None` explicitly. There is no parameter through which a candidate of F could be introduced.
  `order3_real_cell_registry: FROZEN_EMPTY`.
- **No record store.** C3 reads only committed extracts (`ADOPTED_TAIL_INPUTS.json`, `TCT_INPUTS_*.json`) and
  committed registries. Both producers ran to completion on this laptop in 3.2 s and 0.9 s respectively, which is
  itself evidence that nothing expensive is reachable.
- The gate correctly refuses to assert deterministic exhaustion, and excludes the drift-aware per-cell norms
  (worth 0.02–0.2 %) on the ground that C3 has not independently verified premise (P1) — declining an unverified
  tightening that would have helped it.

The note here is N3: the gate's own `guard` clause is enforced by discipline and by the absence of any mechanism,
not by an executable check, and `frozen_gate()` — the one function that would bind execution to the frozen text —
is never called.

## K. The two structural claims, and the baseline figures — **PASS**

**(a) Componentwise-best dominance — verified, 12/12.** The monotonicity argument is correct by inspection of the
Dv′ formulas: `A0 = min(Ā, τ/D_lo)`, `A1 = Ā_eff(κ₁C + D1/D_lo)`, `A2 = Ā_eff(2κ₁²C² + κ₂C + 2κ₁C·δ₁ + 2δ₁² + δ₂)`
have non-negative coefficients throughout and `D_lo` only in denominators, so each `A_j` is non-decreasing in
`τ, C_T, D1, D2, Ā` and non-increasing in `D_lo`. The componentwise-best tuple therefore simultaneously minimises
all three. I verified the conclusion directly: mixed ≤ G, C1 and C2 on `A0`, `A1` and `A2`, on 306, 307, 308 and
309 — **strictly** in all twelve comparisons. The consequence the analysis draws is right: the A-level minimum
returns the mixed supply, so it is inert on this data; and pre-registering it anyway is the correct discipline,
since a rule known to be inert must not be *selected* after that is observed.

One wording point. §2's header calls both facts "derived rather than assumed", but `mixed ≤ G` cannot be derived
from monotonicity — Lemma G is a different lemma with different formulas — and is empirical. The body says so
correctly ("Verified on every open cell"), so the claim is not overstated where it matters, only in the header
(N11).

**(b) Per-sub-block mixing is identical, not tighter — verified, and in a stronger sense than claimed.** The
distributivity `max_i min(a, b_i) = min(a, max_i b_i)` holds on any totally ordered set because `min(a, ·)` is
monotone, and dually `min_i max(a, b_i) = max(a, min_i b_i)` for `D_lo`. So the fine construction yields the same
six constants, exactly as stated.

I also tested the construction the wording could be read to cover but the proof does not: applying Lemma Dv′ *per
sub-block* and composing `max_i A_j` afterwards. This is a genuinely different object — by monotonicity it is
`≤ A_j(worst tuple)` and could be strictly tighter when different sub-blocks are worst in different components —
and it is a valid uniform cell bound (each `e` lies in some sub-block). It is **exactly equal** here, ratio
`1.000000000000` on every `A_j` on every cell for both the C2-alone and the mixed construction, because sub-row 0
is the worst sub-block in all five per-sub-block fields on all four cells. So the gate's decision to *forbid*
sub-block mixing costs nothing, and the claim "there is no gain to be had there" survives the stronger reading.

**(c) The two baseline columns — verified exactly.** Against r5 (`min` over G, C1, C2, i.e. C2's frozen D4 rule):
**20.457947 / 7.922037 / 5.688601 %** for 307 / 308 / 309. Against C1: **57.274132 / 30.566862 / 23.032317 %**.
Both columns are arithmetically correct, they answer different questions, and the gate is right to measure against
r5 — that is the state C3 must improve on, and it is the choice that costs C3 its headline. The presentation is
handled well in `C3_BLOCKER_ANALYSIS.md` §4. It is handled less well in `C3_B0_AUDIT.json`, where the vs-C1 values
sit under a field named `gap_fall_vs_C2_baseline` (N1).

---

## Checklist

| # | question | verdict | notes |
|---|---|---|---|
| A | genuinely pre-registered before forecast | PASS | — |
| B | mixed-operator rule mathematically sound | PASS | — |
| C | component compatibility justified | PASS | — |
| D | whole-cell premises enforced | PASS_WITH_NOTES | N6, N9 |
| E | selector cannot cherry-pick; deterministic | PASS_WITH_NOTES | N3, N8, N10 |
| F | gate prospective, not outcome-fitted | PASS | — |
| G | cell-306 adoption semantics prospective | PASS_WITH_NOTES | N2 |
| H | mutation suite adequate | PASS_WITH_NOTES | N4, N5, N7, N8 |
| I | predecessor / C2 / r5 / main integrity | PASS | — |
| J | no new-real computation authorized or reachable | PASS_WITH_NOTES | N3 |
| K | blocker analysis structural claims and baselines | PASS | N11 |

---

## Notes

**N1 — `C3_B0_AUDIT.json` stores the vs-C1 improvement figures under a field named `gap_fall_vs_C2_baseline`.**
The values `0.5727 / 0.3057 / 0.2303` are falls against **C1**, not against C2 or r5. The name is defensible
(C2's gate's own `baseline` object holds the C1 requirements, so "the C2 baseline" is literally that object) and
`C3_BLOCKER_ANALYSIS.md` §4 corrects the confusion explicitly and at length — which is why this is a note and not
a FAIL. But the whole point of §4 is that stale baselines mislead, and this field is the one place the campaign
invites the misreading. **Required:** the forecast and every downstream summary must quote the r5 figures
(20.46 / 7.92 / 5.69 %) as C3's result and must not cite this field without naming C1 as its baseline.

**N2 — the gate's adoption floor is a condensation, not "verbatim", and drops one clause.** The C2 adjudicator's
F1 carries "This limb is available for as long as **N9** … remains open, and lapses when N9 is closed." The gate's
F1 omits it, while claiming C3 "inherits it verbatim and does not restate, reinterpret or soften it." N9 is open,
so the operative floor is identical today and nothing is currently softened. **Required:** the forecast must record
N9's open status as the precondition that makes the condensed F1 equivalent to the adjudicator's, and should drop
the word "verbatim" in favour of an accurate description.

**N3 — `frozen_gate()` and `GATE_SHA` are defined but never called.** No existing code path verifies that the gate
in the tree is the frozen one. Pre-forecast this is not a defect; at forecast time it is the single binding
between the executed mechanism and the pre-registered text. **Recommended:** `c3_forecast.py` must call
`frozen_gate()` before computing anything, and the qualifier should fail if it does not.

**N4 — the mutation summary counts a proved-equivalent mutant as detected.** `applied: 13, detected: 13,
undetected: []` promotes M08, whose own row honestly records `detected: false, equivalent: true`. **Required:**
report **12 killed, 1 proved equivalent, 0 unexplained**, not 13/13.

**N5 — the tie world's stated rationale is factually wrong.** `c3_mutations.py:155` says "Tie resolution is
unexercised on real data because the two registries agree on nothing." The registries agree **exactly on `Ā`, on
all four cells** — I confirmed the values are identical while the two ARL certificate artifacts have different
sha256, i.e. two independent runs of the same degree-12 `α = 5/4` procedure converging on the same rational. Tie
resolution *is* exercised on real data and resolves to C1 every time. Harmless (`Ā` is inert, since
`Ā_eff = τ/D_lo < Ā` on every cell, and the tied values are equal anyway), but the synthetic tie world's
justification should be restated correctly.

**N6 — `whole_cell_ok` validates sub-row geometry but not the block-level aggregation it actually consumes.** The
selector reads `b["τ"]`, `b["C_T"]`, … ; the check validates `b["sub_rows"]`. The bridge — block fields = worst
over sub-rows, `Ā` from a whole-cell ARL certificate — is inherited from `c2_refined_registry.py` and never
re-checked by C3. I verified it holds exactly on all four cells. **Recommended:** a six-line assertion in the
forecast (`max` over sub-rows for the four upper bounds, `min` for `D_lo`) would turn an inherited assumption into
an enforced premise, at no cost.

**N7 — M08's equivalence proof hardcodes its own premise.** It checks `names = ["C1", "C2"]` rather than reading
the selector's `sources` literal, so it would still certify equivalence if that literal were reordered. The
premise is true today (I checked `c3_selector.py:81`). **Recommended:** derive the source order from the module
under test.

**N8 — `combine_A`'s tie-break has no mutant and no equivalence proof, and M08's argument does not transfer.**
`supplies` is inserted `G, C1, C2, operator_mixed`, which is not lexicographic, so the stable-sort argument that
licenses M08 does not apply. I worked it through: on a tie the `A` values are equal by definition, so only the
provenance label could move and both variants stay deterministic — inert, but currently unproved.

**N9 — `whole_cell_ok`'s C1 branch requires "equals", not "contains".** A block strictly wider than the cell — a
valid, more conservative certificate — is rejected; I confirmed this by widening `e_hi` by 1/1000. The direction
is safe: it can forfeit tightening, never admit an invalid bound. Worth recording so a later campaign supplying
wider blocks is not surprised.

**N10 — `rejected_sources` conflates two dispositions with different consequences.** A whole-cell failure excludes
a source from `operator_best` *and* from `supplies`; a Dv′-premise failure excludes it from `supplies` only, and
its components still enter the mixed tuple. This is correct (a loose `τ` paired with a tight `C` violates `C ≥ τ`
without either bound being invalid, and the mixed tuple is guarded by the consumer), but the output field does not
distinguish the two, and a reader could conclude a "rejected" source contributed nothing. **Recommended:**
separate keys, or a disposition field.

**N11 — `C3_BLOCKER_ANALYSIS.md` §2's header says "derived rather than assumed" for both facts.** `mixed ≤ G` is
empirical, not derived — monotonicity covers only the Dv′-based supplies. The body states it correctly as
"Verified on every open cell", so only the header overstates.

---

## What I did not check

- **The Arb/FLINT certification artifacts behind either registry.** I did not re-run `taboo_certify`, the
  denominator certifier, or the ARL supersolution certifier, and I did not open the FLINT venv. The six operator
  constants of both C1 and C2 are accepted as certified by their campaigns. This is the residual trust surface
  that C2's N9 names and that C3's blocker analysis correctly identifies as cell 306's blocker; my review does not
  reduce it.
- **The adopted K1 record store** (`/root/work/.../k4_records`), which is not on this host. I used the committed
  `ADOPTED_TAIL_INPUTS.json` and `TCT_INPUTS_*.json` extracts, exactly as C3 does, and did not verify them against
  the records.
- **Theorem TC-T, theorem K5-B, `refine2`, `order2.py` and the frozen K1 error algebra.** I read Theorem AD closely
  because the mixed-operator question turns on it, and I read `atom_constants_r2` and `_atom_independent` in full.
  I checked only that C3 consumes the rest unchanged and adds nothing to them; I did not re-verify them.
- **The whole-kernel supersolution premise behind `Ā`.** It is inert on all four cells (`Ā_eff = τ/D_lo` every
  time), so I did not pursue it.
- **The drift-aware per-cell norms** the gate excludes under premise (P1). I did not assess whether (P1) holds;
  C3 does not rest on it and neither does this review.
- **Downstream governance.** Qualification, authorization, execution, seal, consumption and adjudication do not
  exist yet for C3 and are outside a pre-forecast review. N3 (gate pin) and N6 (aggregation assertion) are the two
  items I would expect a qualifier to pick up.
- **Anything on AWS.** Not contacted, by instruction and in fact.

---

## Verdict counts

Tallied mechanically from the checklist table above.

| outcome | count |
|---|---|
| PASS | 6 |
| PASS_WITH_NOTES | 5 |
| **FAIL** | **0** |
| total sections (A–K) | 11 |
| numbered notes | 11 |
| notes that block the forecast | 0 |
| notes requiring a correction in the forecast's narrative | 3 (N1, N2, N4) |

**VERDICT: READY_WITH_NOTES.** The mixed-operator rule is sound, component mixing across sources is legitimate,
the whole-cell premise is the right premise and is checked where it matters, the selector is deterministic and
cannot cherry-pick, the gate is genuinely non-fitted, and predecessor integrity is intact. C3 may compute its
forecast.
