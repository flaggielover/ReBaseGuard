# C3 independent adjudication — P5Y / K5 CUSUM m = 5 tail, cells 306–309

**VERDICT: REJECTED — no cell is adopted. The adopted cell set is empty. The C3 packet itself is sound, fully
reproducible and correctly executed, and its sealed negative result stands as evidence for a successor; what is
rejected is adoption, which C3 itself did not propose and which I also decline. No coverage map r6 follows.**

Adjudicated at worktree `/Users/suzhe/ReBaseGuard-k5c2`, branch `p5y-k5-tail-c3`, HEAD `e815a217`, tree clean.
I wrote none of this work and I am not bound by the campaign's conclusions. I modified no file except this one and
ran no writing git command. AWS was not contacted. r4, r5, `main` and the C2 namespace are untouched.

## What REJECTED does and does not mean here

It means exactly one thing: **nothing from Campaign C3 enters the permanent record, and no r6 is generated.**

It is **not** an impeachment of the packet. I re-derived the whole of C3 independently and found no error of
arithmetic, of method, or of governance. C3's own decision rule for its `PARTIAL` class — "propose NOTHING for
adoption … publish the negative result" — is the correct call on this evidence, and I reached the same conclusion
by my own route before reading C3's reasoning for it. `C3_BLOCKER.json`, `C3_BLOCKER_ANALYSIS.md`,
`C3_FORECAST.json` and the seal remain valid, citable evidence. A successor should build on them, not repeat them.

I considered `NOT_READY` and rejected it: nothing about the packet needs to change. No repair could make C3 adopt
anything, because the obstacle is the science, not the paperwork. I considered a non-empty adopting verdict for
cell 306 and rejected it on the merits; see **H**.

---

## What I re-derived versus what I accepted

**Re-derived independently, from primary committed evidence, with my own code:**

- the whole-cell validity of both certificate sources (cover endpoints, exact tiling, sub-block widths, and that
  C2's block-level constants really are the worst over its own sub-rows);
- the mixed operator tuple and its per-field provenance, from my own componentwise min/max;
- the Lemma Dv′ premises on the **mixed** tuple, checked directly rather than through the campaign's code;
- the atom constants A0, A1, A2 from a transcription of Lemma Dv′ made from `THEOREM_AD.md` §4 alone, then
  cross-checked against both the pinned `deflated_consume.atom_constants_r2` and C2's independent
  `_atom_independent` path — three routes, exact rational agreement;
- Γ, the closure verdicts, the required uniform reductions (my own bisection, 200 iterations, bracket 10⁻⁶ … 1),
  the gap falls against r5, and both adoption-floor components with the uniform-A margin (my own bisection,
  200 iterations, bracket 1 … 8), for all four cells;
- the measurement gating (`identity_gate.identical`, `order3_fields_present`) that C3's own forecast does **not**
  re-check;
- both registry hashes against C2's committed pins;
- the dominance and distributivity claims on which C3's "the envelope is exhausted at operator level" rests;
- the seal manifest (21 files, all hashes recomposed);
- new work C3 did not do: per-component knockouts, the critical A0 thresholds, and the A1/A2-only feasibility of
  each open cell (see **K**).

**Accepted without re-derivation** (predecessor-frozen and out of C3's scope): theorem TC-T and the frozen K5-B
closure rule; the K1 records, adopted tail inputs and drift-aware norms; the Arb/FLINT certification of the C1 and
C2 registry constants themselves; the validity of the cover ledger `cells.json`; the C2 adjudication as the
authoritative statement of the inherited floor.

---

## A. Temporal integrity — **PASS**

Verified from the object store, not from claims.

The gate blob `config/FEASIBILITY_GATES_C3.json` appears in exactly one commit in the whole repository history,
`24c038ec` (2026-09-21T23:06:07+09:00), `git log --follow` returns that single entry, and the blob at HEAD and at
`24c038ec` both hash to `f0bd87ecaeea4485560969770c95c9d4ad20bceedf9ac7ca11fb6d8d5de53ac7`. It was never amended.

`evidence/forecast/C3_FORECAST.json` first appears in `d41604c2` (23:44:03), 38 minutes later. I listed the full
namespace tree at `24c038ec`, `94bc0ad3` and `7ed23828`: no forecast artifact, under that or any other name, exists
in any tree before the freeze commit. The two files edited after the gate but before the forecast
(`C3_B0_AUDIT.json`, `c3_mutations.py`/`C3_MUTATIONS.json`, at `7ed23828`) are the pre-forecast review's note fixes
N1, N4 and N5; I read both diffs in full. N1 adds a correctly-labelled second baseline column and leaves every
number otherwise identical (one 15th-decimal-place difference in the vs-C1 figure for 307, from recomputation
rather than transcription); N4 splits a merged count; N5 corrects a docstring. None touches the gate, and none
moves a figure the gate depends on.

**But the honest reading of A is narrower than "the gate was frozen blind", and C3 says so itself.**
`C3_BLOCKER.json` — which contains Γ under the mixed supply for all four cells, to full precision — was committed
in the *same commit* as the gate. The C3 "forecast" is therefore a re-computation of numbers that already existed,
not a prediction. C3 discloses this in `prior_evidence_known_at_freeze` and the disclosed values match the blocker
file exactly. Temporal integrity in the strict sense (no rule written after seeing its own output) holds; temporal
integrity in the blinding sense was never available to C3, because C2 had already published these numbers. That
makes **B** the load-bearing question, not A.

## B. Gate pre-registration and non-fitting — **PASS, and the disclosure is the right practice**

The question is not whether C3 knew the answer — it did, completely, and says so — but whether any free parameter
of the gate was set to suit that answer. I checked every parameter that could have been:

| parameter | who set it | does it favour C3? |
|---|---|---|
| adoption floor (Γ<0 **and** (F1 or F2), ×1.25) | the independent C2 adjudicator, prospectively, before C3 existed | no — it is the one rule that stops 306 |
| material-tightening threshold 0.20 | C2's frozen gate | no — inherited unchanged |
| baseline (r5, not C1) | **C3's own free choice** | **no — it cuts C3's headline from 57/31/23 % to 20/8/6 % and pushes 308 and 309 below the threshold** |
| universe {306,307,308,309} | determined by r5's open set | no |
| class definitions and decision rules | C3-authored | no — `PARTIAL` proposes nothing, which is strictly stricter than C2's `D_PARTIAL`, under which a non-empty closed subset *is* adopted |

I verified the baseline numerically: the gate's `baseline.requirement` and `baseline.gap` reproduce C2's committed
`C2_D5_FORECAST.json` per-cell requirements to the last digit. They are not C3's numbers to choose.

The only free choice C3 made, it made against itself. The gate's `PARTIAL` branch is a pre-commitment to publish a
negative result. Its `adoption_floor.why_inherited_rather_than_invented` clause states in advance that C3 knew 306
would fail — and that is precisely why the floor was not C3's to write. **The gate is non-fitted.** Disclosure of
known priors in a pre-registration that cannot be blinded is the correct practice, not a confession; concealing
them would have been the defect.

One observation that reduces B's stakes further: the 20 % threshold is **inert on this data**. Class selection runs
USEFUL → PARTIAL → …, and 306 closing forces `PARTIAL` before the material-tightening test is ever consulted. So
307's 20.4579 % — which clears the bar by 0.46 percentage points and would fail a 21 % bar — changes nothing about
the class, the decision, or adoption. It is a reported finding, not a lever.

The **erratum** is correctly handled. The gate's condensation of the floor drops the adjudicator's clause that F1
is available only while N9 is open. I verified from `OPEN_NOTES_DISPOSITION_C2.md` that N9 and N10 are both still
open and that no second independently written certifier exists, so the dropped clause is inert. Refusing to amend a
frozen pre-registration and carrying the correction in an erratum is right.

## C. Mixed-selector soundness — **PASS. Componentwise mixing is valid. I found no hidden joint constraint.**

I read `THEOREM_AD.md` myself. §8 is decisive: each of the six constants is a bound on a quantity of the **true
operator family** on the block B, not a property of the certifier —

    Ā ≥ sup_B E_a[τ],  τ ≥ sup_B E_a[τ ∧ T_a],  C ≥ sup_B ‖Ĝ_e‖,
    D_lo ≤ inf_B D_e,  D1 ≥ sup_B |D′|,        D2 ≥ sup_B |D″|

— six independent scalar inequalities about six objectively defined numbers. Lemma Dv (§4) and Lemma Dv′ assume
exactly these inequalities and nothing about their provenance; each constant enters the proof only through its own
inequality, and κ₁, κ₂ are universal. Two valid certificates therefore give two true statements about the *same*
number, and taking the min (upper bounds) or max (lower bound) is the intersection of two valid bound sets, not an
average. No statistical independence is assumed or needed, and shared assumptions between C1 and C2 cannot corrupt
soundness — only robustness, which is what the floor is for. C3 states this correctly.

**Hidden joint constraints — the real question.** I found three candidates and checked each:

1. **τ and C are derivationally coupled.** Both come from a single supersolution w: τ = w(a), C = sup_X w, so
   τ ≤ C automatically *within one source*. Mixing τ from source 1 with C from source 2 could in principle break
   C ≥ τ. Lemma Dv does not need them to share a w, but it does need C ≥ τ, and `atom_constants` raises
   `DeflationRefusal` if that fails. I confirmed C ≥ τ holds on the mixed tuple for all four cells — and in fact the
   question never arises here, because **τ and C_T are both taken from C1 on every cell**, so the one genuinely
   coupled pair is never split. This is luck, not design, but the guard is real: adversarial world M11 forces the
   violation and kills mutant M04, which swallows the check.
2. **Ā_eff = min(Ā, τ/D_lo) mixes τ (C1) with D_lo (C2).** Valid: E_a[τ] = τ_a/D ≤ τ/D_lo whenever both source
   inequalities hold, which they do.
3. **δ₁ = D1/D_lo ≥ |D′|/D and δ₂ = D2/D_lo ≥ |D″|/D** each mix a numerator from one source with a denominator
   from the other. Valid for the same reason; both quantities are non-negative, so the 2δ₁² term in A2 is safe.

I verified all four Lemma Dv′ premises (τ ≥ 1, C ≥ τ, D_lo > 0, Ā ≥ 1) and the r2 ≤ r1 invariant on the mixed
tuple for every cell, independently, in exact rationals. All hold.

**Note (not a defect, but load-bearing):** the mixing is maximally active on this data — A0 = τ_C1 / D_lo,C2 on all
four cells. And Ā is entirely **inert**: Ā (7.9124 / 7.5556 / 7.2179 / 6.9010) exceeds τ/D_lo (6.0045 / 5.5980 /
5.2185 / 4.8672) on every cell, so `min` always takes τ/D_lo. Ā is also bit-identical between C1 and C2 on all four
cells, confirming erratum note N5.

## D. Certificate compatibility and whole-cell validity — **PASS, with one latent gap that does not bite**

Checked myself, in exact rationals, for every cell:

- **C1**: `e_lo`, `e_hi` equal e0 − ρ and e0 + ρ exactly. Whole-cell by construction.
- **C2**: 9 / 10 / 11 / 11 sub-rows; first `e_lo` = e0 − ρ, last `e_hi` = e0 + ρ, every interior boundary matches
  exactly (no gap, no overlap); maximum sub-row width 1/100 or narrower on every cell. **The cover is exact.**
- **C2 composition**: I recomputed the block-level constants as max over sub-rows for τ, C_T, D1, D2 and min for
  D_lo, and they equal the stored block values exactly on all four cells. C2 really is composed worst-over-cover,
  so its block constants are genuine whole-cell bounds.
- **Premises on the mixed tuple**: enforced, not assumed — the selector routes the mixed tuple through the pinned
  `atom_constants_r2`, which raises rather than returning constants for an inadmissible tuple, and falls back to the
  best single source if it does. I verified the premises hold directly.
- **Distributivity**: C3 claims per-sub-block mixing is *identical*, not tighter, because min distributes over max.
  I verified this numerically at the operator level (every field equal on every cell) and, going further than the
  proof covers, at the **A level**: worst-over-cover of per-sub-block A equals whole-cell mixed A at ratio exactly
  1.000000000000 for A0, A1 and A2 on all four cells. There is no gain hiding in the finer construction.

**Latent gap (C-1, see conditions).** `whole_cell_ok` validates C2's cover by its `sub_rows` only. C2's Ā does not
come from a sub-row — it comes from a separate per-cell `arl` sub-object with its own artifact hash — and the
selector performs no cover check on it. Today this is harmless twice over: the `arl` object is per-cell (so it is a
whole-cell certificate), and its value is bit-identical to C1's, so the tie resolves lexicographically to C1 and
C2's Ā is never selected. A future registry certifying Ā on a narrower or sub-blocked domain would slip through
unchecked. This must be closed before any successor mixes a differently-structured registry.

## E. Forecast and result reproducibility — **PASS. Exact, independently and byte-for-byte.**

Byte-identical regeneration of all three producers from the frozen tree:

| artifact | committed sha256 | my regeneration |
|---|---|---|
| `C3_FORECAST.json` | `ad36d408…` | `ad36d408…` identical |
| `C3_BLOCKER.json` | `d69a4500…` | `d69a4500…` identical |
| `C3_MUTATIONS.json` | `33d3b5e5…` | `33d3b5e5…` identical |

Re-running the campaign's own code proves determinism, not correctness, so I re-derived the science separately.
From my own selector, my own Lemma Dv′ transcription, and my own bisections:

| cell | Γ (mine = committed) | closes | requirement (mine) | requirement (committed) | gap fall vs r5 |
|---|---|---|---|---|---|
| 306 | −0.036197779964579 | **yes** | 1.0 | 1.0 | n/a (baseline gap 0) |
| 307 | +0.026354631323171 | no | 1.111966237137042 | 1.1119662371370425 | 20.4579 % |
| 308 | +0.094564144965664 | no | 1.460654799394688 | 1.4606547993946881 | 7.9220 % |
| 309 | +0.153019688894184 | no | 1.847873499844009 | 1.8478734998440092 | 5.6886 % |

Γ agreed **exactly** as rationals, not merely to floating point. Requirements agreed to 1 part in 10⁹ (my bisection
uses a different bracket and 4× the iterations, so residual disagreement is in the last digit and is bisection
granularity, not a discrepancy). Atom constants agreed exactly across three independent implementations. The
operator tuples and per-field provenance matched exactly. My run of every structural check produced **zero** false
flags across all four cells.

Floor components, re-derived: 306 Γ under Lemma G = +0.019115585047 (does not close); Γ at ×1.25 = +0.022002639886
(does not close); uniform-A margin = 1.1554876238748288 — identical to the committed value to all 16 digits.

**One methodological gap I closed myself.** C3's forecast reads the measurement files without re-running C2's
gating (`identity_gate.identical`, `order3_fields_present`, K1 record binding), and reads both registries without
pin checks. I checked all of it: both registry hashes match C2's committed pins exactly
(`87bb1cfa…` / `1b2b8349…`); `identity_gate.identical` is true and `order3_fields_present` is false on all four
measurement files. Nothing is wrong — but the forecast should have asserted it rather than inherited it.

## F. Mutation adequacy — **PASS on what it covers; two load-bearing mechanisms are unmutated**

Thirteen mutants, all applied. Twelve killed. One (M08, tie resolution) is not merely asserted equivalent but
**proved so in code**: sources are inserted lexicographically and Python's sort is stable, so dropping the name from
the sort key cannot change the selection on a tie, demonstrated by constructing an all-equal probe. That is the
right standard, and the N4 fix separating `killed` from `proved_equivalent` is the right reporting.

The mutants are real, not cosmetic. They are planted where an error produces an **artificially optimistic** result:
min/max inverted on upper and lower bounds, the A-level minimum flipped to a maximum, the premise check swallowed,
the whole-cell check disabled, a tiling gap accepted, cover endpoints unchecked.

The "evaluate each source mutant against every adversarial world" design is **sound and is the right answer to the
standard failure mode**, where a guard's mutant survives because no test ever makes the guard fire. It works here:
M04 (premise check swallowed) is invisible on real data and is killed only by world M11; M05 and M07 (whole-cell and
endpoint checks) are killed only by M13; M06 only by M10. Without the cross product these three guards would be
untested. Five data worlds plus a synthetic tie world is adequate coverage of the selector's refusal paths.

**Gap.** The suite mutates `c3_selector.py` and the input data. It does **not** mutate `c3_forecast.py::classify`
or the adoption-floor evaluation in `c3_forecast.main`. Those are the two most consequential pieces of code in the
campaign: `classify` decides USEFUL versus PARTIAL, and the floor decides adoptability. A mutant flipping
`meets_floor` to `f1 and f2`, or reordering the classification cascade, would have gone undetected by the suite.
This is a real hole in F. It does not change my verdict, because I evaluated both mechanisms independently myself
and reproduced them exactly — but a successor must not carry this design forward unchanged.

## G. Zero-new-real compliance — **PASS**

- `new_real_scientific_addresses_evaluated = 0`, `new_real_cpu_seconds = 0`, `new_real_scientific_addresses_authorized = 0`.
- Guard `REAL_SCIENTIFIC_COMPUTE = DENY` before, during and after; recorded in the gate, freeze record,
  authorization, execution, forecast, seal and consumption.
- **No R-stage.** `order3` is `None` on every path. I grepped the entire code tree: the only occurrences of
  "order3" are the string `None`, the *name* of the frozen predecessor namespace `p5y_k5_lower_front_order3` (a
  pinned read), and the blocker's read of the recorded `f_G` diagnostic. No candidate of F is constructed.
- **No AWS.** I grepped for `boto`, `requests`, `urllib`, `socket`, `ssh`, `aws`: no hits. `subprocess` appears only
  to invoke local `git` and local Python producers. The whole campaign ran in 4.9 seconds of wall clock, which is
  itself evidence that nothing expensive was evaluated.
- Predecessor integrity: `git diff ae4cbc2c HEAD` over the C2 namespace returns nothing. r4 hashes to
  `a3bddd83…` and r5 to `e2197051…`, both as recorded. No r6 exists anywhere in the tree. `main` is at
  `c123b9bb…`, unmoved.
- The qualification (19/19 PASS, nothing skipped, nothing failed) and the seal manifest verify: I recomputed all
  21 manifest hashes and found zero mismatches. The four namespace files outside the manifest are exactly the
  post-seal artifacts (the seal, the manifest, the consumption and its consumer), which is correct.
- Pre-freeze refusal exercised both ways (unbound protocol, tampered pin), both exit 1.

## H. Cell 306 — **is it adoptable? No. I verify both floor components and I agree it must not be adopted.**

**F1 fails.** Under Lemma G — the only supply available that touches no Arb/FLINT `taboo_certify` surface — I get
Γ(306) = **+0.019115585047**. It does not close. Verified by my own computation from `C_upper` and the frozen
drift-aware norms.

**F2 fails.** With every atom constant inflated by ×1.25 I get Γ(306) = **+0.022002639886**. It does not close. The
uniform-A margin is **1.1554876238748288** — the cell tolerates a 15.55 % uniform error in the atom constants before
reopening, against a floor that asks for 25 %. My bisection (bracket 1 … 8, 200 iterations) reproduced the campaign's
margin to all 16 significant digits.

**I do not set the floor aside. I would reach the same decision without it.** My reasons, in order of weight:

1. **C3's own step made 306 worse on the exact axis the floor measures.** I verified that the mixed supply dominates
   Lemma G componentwise on all three atom constants, on all four cells. Being componentwise tighter than the one
   registry-free supply means the mixed supply is *strictly more* dependent on the Arb surface than what it
   replaced. C3 improved Γ from −0.030469 to −0.036198 while making the closure's support narrower. That is a real
   reason to refuse, not a deference.
2. **The open risk is a correctness risk of unknown magnitude, and a margin cannot price it.** N9 records that the
   entire operator-registry surface is one implementation, never independently written; N10 records that its build
   host is recorded nowhere. Both are still open — I checked `OPEN_NOTES_DISPOSITION_C2.md` directly. A 15.5 %
   margin protects against a 15.5 % error. It does not protect against a logic error in the only implementation
   there is.
3. **The error asymmetry is severe and one-directional.** An adopted cell is permanent and leaves every future
   campaign's universe. A deferred cell is recomputed next cycle at zero compute cost with its registry intact.
   Cell 306 has been recomputed twice already at no scientific cost.
4. **Overturning a prospective standard in the first campaign it disfavours would destroy the standard.** The C2
   adjudicator set this floor before C3 existed, built it from severities C2 had itself published against its own
   interest, applied it identically to 305 (which passed both limbs) and 306 (which failed both), and predicted
   this campaign's result by name and to six decimals: "a D′ campaign alone will not discharge this floor for cell
   306 … Γ = −0.036198 with a uniform-A margin of 1.1555". C3 reproduced both figures exactly. A floor that is
   abandoned the moment it binds was never a floor.

The closure is *sound*. I reproduced its arithmetic exactly and I have no doubt about it. It is a sound closure
whose entire support is a single un-replicated certifier implementation, with 15.5 % of room, proposed for a
permanent and irreversible entry. **Do not adopt.**

**What would discharge it** — three routes, all still open, with a number attached to the second:

- a **second, independently written certifier** of the six operator constants for cell 306, closing N9 (after
  which F1 should be replaced by a cross-implementation-agreement limb, per the C2 adjudicator);
- **further deterministic tightening to a uniform-A margin ≥ 1.25**, which from 1.1555 requires a further
  **7.56 % uniform reduction** in the atom constants (scale ≤ 1.1555 / 1.25 = 0.92439). This is a small and
  concrete target — the closest any deterministic route has come — and unlike 308/309 it is *not* blocked at
  order 0: I computed that 306's critical A0 with A1 and A2 held at their certified values is 7.1501 against a
  certified 6.0045, so A0 carries 19 % of headroom at this cell;
- a **real order-3 candidate**, where the C2 adjudicator records Γ_perfect_order3(306) = −0.2175, under the
  R-stage's own separately frozen gate and only after N1, N5 and N7 are discharged.

## I. Cells 307, 308, 309 — **confirmed open under every available supply; the tightening verdicts are right**

**None closes, under any supply on the table.** I recomputed Γ for Lemma G, C1, C2, the r5 D4 minimum and the
operator-mixed supply on each cell; the mixed supply is componentwise best on all three atom constants on all four
cells (strictly better than each of G, C1 and C2), so the A-level minimum over {G, C1, C2, mixed} returns the mixed
supply and adds nothing — I verified this rather than taking it on trust. The best available Γ is +0.026355,
+0.094564 and +0.153020. Even the best supply still requires uniform atom-constant reductions of 1.111966, 1.460655
and 1.847873.

**Material tightening: 307 yes, 308 and 309 no — correct.** Measured against r5, the current authoritative state,
the gaps fall by 20.4579 %, 7.9220 % and 5.6886 %. I reproduced all three against the gate's frozen baseline, which
I separately confirmed equals C2's committed D5 requirements. Two caveats the record should carry:

- 307 clears the 20 % bar by **0.46 percentage points**. The bar is inherited and the arithmetic is right, but a
  verdict with that margin should not be leaned on. As noted in **B**, it has no effect on the class or on adoption.
- The widely-quoted 57 / 31 / 23 % are against **C1, two campaigns back**. Against r5 the same step buys
  20 / 8 / 6 %. C3 chose the r5 baseline against its own interest and said so plainly. That is the correct choice
  and the correct disclosure, and a successor must not quote the C1 column as current progress.

Since none of the three closes, the adoption floor is not reached for any of them, and none is adoptable on any
ground.

## J. The exact adoptable subset

Cell 306 closes but fails both limbs of the inherited floor (**H**). Cells 307, 308 and 309 do not close under any
available supply (**I**). No cell qualifies.

## ADOPTED CELL SET

    []

Empty. **No coverage map r6 is to be generated.** r4 (`a3bddd83…`) and r5 (`e2197051…`) remain authoritative and
immutable; the m = 5 open set stays {306, 307, 308, 309}.

## K. Deterministic exhaustion — **NOT established. C3 is right not to assert it. I sharpen why, and say exactly what would establish it.**

This is the question with real consequences, so I did work C3 did not do, and the answer changes shape per cell.

C3's blocker analysis argues from a **uniform** reduction factor (1.46 / 1.85) and concludes "operator-level
tightening cannot bridge a factor of 1.46–1.85." That argument is directionally right but rests on the wrong
feasible set: nothing requires a future certificate to improve all three atom constants by the same factor. A
non-uniform improvement is entirely admissible, so the uniform factor is a proxy, not a bound. I replaced it with
per-component knockouts, computed from committed rationals with no scientific address evaluated:

| cell | Γ, mixed | Γ at A1 = A2 = 0 | A0 certified | critical A0 (A1 = A2 = 0) | A0 reduction needed |
|---|---|---|---|---|---|
| 306 | −0.036198 | −0.079279 | 6.0045 | 8.5136 | none — already closes |
| 307 | +0.026355 | **−0.021906 → closes** | 5.5980 | 6.1725 | none — A0 is not the blocker |
| 308 | +0.094564 | **+0.039568 → still open** | 5.2185 | **4.3752** | **×1.1927 (16.2 %)** |
| 309 | +0.153020 | **+0.092812 → still open** | 4.8672 | **3.2142** | **×1.5143 (34.0 %)** |

**For 308 and 309 this is a genuine structural blocker, and a much sharper one than C3 stated.** Closure is
**infeasible by any improvement of A1 and A2 whatsoever** — driving both to zero still leaves Γ positive. Every
operator-level route to 308 or 309 must therefore push A0 below 4.3752 and 3.2142 respectively. And A0 is not an
arbitrary constant: A0 = Ā_eff = min(Ā, τ/D_lo) is an upper bound on E_a[τ], which Lemma SM(d) proves is **sharp** —
sup over ‖f‖ ≤ 1 of |[(I − K_e)⁻¹f](a)| equals τ_a/D exactly, attained at f = 1. The required reduction must come
entirely out of the slack between the certificate and the truth, and the truth is a hard floor no certificate can
go under.

**But that is not exhaustion, and I will not call it exhaustion.** Nothing in committed evidence gives a certified
**lower** bound on E_a[τ] at these cells. Without one, we cannot say that 4.3752 and 3.2142 are unreachable — only
that no one has reached them. The one hint available cuts against complacency in the other direction: Ā (7.2179 at
308) is 38 % looser than τ/D_lo (5.2185), so the whole-kernel supersolution is demonstrably *not* near-sharp at the
tail, and by implication we do not know how much slack sits in τ and D_lo either.

**For 307 the deterministic direction is plainly not exhausted.** A0 is not the constraint at all — its critical
value (6.1725) sits *above* the certified value (5.5980). 307 closes on a 1.112× uniform reduction, or on a 2.203×
reduction of A1 and A2 with A0 left exactly as certified. And C3 bought 20.46 % of 307's r5 gap by pure
recombination of existing certificates at zero new compute. A campaign that finds that much by rearrangement alone
has not demonstrated that the direction is spent.

**Consequence for the R-stage.** Deterministic exhaustion is the premise on which a real order-3 R-stage would
become justifiable. It is **not established for any of 307, 308 or 309**, so that premise is **not available** and
the R-stage is not yet justified on exhaustion grounds. C3's refusal to assert it — in the gate, the authorization,
the seal and the consumption — is correct and I uphold it.

**What would establish it, and it is cheap.** A certified lower bound on E_a[τ] at cells 308 and 309 exceeding
**4.3752** and **3.2142** respectively would prove that no operator-constant certificate can ever close those two
cells, converting "not achieved" into "cannot be done". That is a purely operator-level computation — a subsolution
or a direct ARL lower bound — with no scientific address, no order-3 candidate and no R-stage involved. I consider
it the single highest-value next step in this campaign line, worth more than another recombination pass, because it
is the only thing that can discharge the exhaustion premise for the tail. No such bound would be needed for 307,
where exhaustion is not in prospect.

**One prose defect to flag.** `C3_BLOCKER_ANALYSIS.md` §3 states flatly that "Operator-level tightening cannot
bridge a factor of 1.85." As written that is an assertion of exhaustion, it rests on the uniform-scaling proxy, and
it sits inside a sealed artifact. Every operative statement elsewhere in the packet correctly says exhaustion is
NOT established, so I treat this as a prose overstatement rather than a governance breach — but a successor must
not cite that sentence as establishing anything.

---

## Conditions

These attach to any successor campaign in this line. None of them is a defect requiring C3 to be reissued.

1. **No r6.** The adopted set is empty, so no coverage map is generated. r4 and r5 remain authoritative and
   immutable; the m = 5 open set is unchanged at {306, 307, 308, 309}.
2. **The K5 tail adoption floor stands, unchanged**, including the C2 adjudicator's N9-lapse condition on F1, which
   the C3 gate's condensation dropped and `ERRATUM_C3_GATE.md` restores. The **adjudication** is the source of
   truth for the floor, not the C3 gate.
3. **Do not read C3's F1 failure as evidence about cell 306's truth.** F1 is a supply-independence test. No
   registry-derived supply can ever pass it, by construction, and componentwise mixing moves a cell *away* from
   passing it. 306's F1 failure says the closure rests on one surface; it says nothing about whether the closure is
   correct, and I believe it is.
4. **Close gap C-1 before mixing a differently-structured registry.** `whole_cell_ok` does not check the domain of
   the certificate supplying Ā, which on C2 comes from a per-cell `arl` object outside the sub-row cover. Inert
   today only because that value is per-cell and bit-identical to C1's.
5. **Extend the adversarial suite to the classifier and the floor evaluator.** `classify` and the `meets_floor`
   computation are the two most consequential mechanisms in the campaign and are currently unmutated (**F**).
6. **A successor forecast must assert its own inputs**, not inherit C2's gating: pin both registry hashes and
   re-check `identity_gate.identical`, `order3_fields_present` and the K1 record binding at the point of use.
   All of these hold today — I checked — but the forecast does not say so.
7. **The concrete targets now on the record.** For adoption of 306: a further **7.56 %** uniform reduction in the
   atom constants (margin 1.1555 → 1.25), or a second independent certifier, or real order-3. For exhaustion of
   308 and 309: certified lower bounds E_a[τ] > **4.3752** and > **3.2142**. For 307: a **2.203×** reduction of A1
   and A2 with A0 unchanged, or **1.112×** uniform.
8. **Do not quote the vs-C1 tightening figures (57 / 31 / 23 %) as current progress.** Against r5 the step is
   20 / 8 / 6 %. C3 got this right; the risk is a successor reverting to the flattering column.

## What I did not check

- **The Arb/FLINT certification of the registry constants themselves.** I verified that both registries hash to
  C2's committed pins and that C2's block constants are correctly composed from its own sub-rows, but I did not
  re-run the supersolution certificates or inspect their Arb artifacts. N9 — that this is one implementation,
  never independently written — remains open and is the residual trust surface under everything above, including
  306's closure.
- **Theorem TC-T, the frozen K5-B closure rule, and `tc_rule`.** I called them from their pinned bytes and relied on
  `tail_enclosure_crosscheck` (an independent second path already built into `FC.direct`) rather than re-deriving
  the enclosure myself. They are predecessor-frozen and outside C3's scope.
- **The K1 records, the adopted tail inputs, the drift-aware norms and the cover ledger.** Taken as given from the
  adopted state. I checked the measurement files' own gating flags but did not re-derive the measurements.
- **The C2 campaign's internal correctness.** I read its adjudication, its D5 forecast, its registry and its open-
  notes disposition as evidence, and confirmed its namespace is unmodified, but C2 is immutable and I did not
  re-adjudicate it.
- **Whether a real order-3 candidate would close any of these cells.** Out of scope and forbidden: guard DENY, no
  address evaluated. The Γ_perfect_order3(306) = −0.2175 figure quoted in **H** is C2's, read and not verified.
- **Any host, toolchain or build-provenance claim.** N10 remains open: the registry records no build host, and
  nothing I can do from the object store changes that.
- **The pre-forecast review's own reasoning.** I read its verdict and its notes to confirm the notes were fixed at
  source, but I did my own analysis of sections A–K rather than auditing the reviewer.
