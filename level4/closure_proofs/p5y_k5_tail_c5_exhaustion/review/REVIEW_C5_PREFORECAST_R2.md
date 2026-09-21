# Independent fresh-context pre-forecast review — P5Y / K5 Campaign C5 — ROUND 2

Reviewer: same fresh-context reviewer, round 2, re-reviewing HEAD `5fad47ad` on `p5y-k5-tail-c5` after the repair
of the two blocking failures raised in round 1. Read-only throughout: nothing in the repository was created,
edited or committed; all scratch work is under the session scratch directory. No remote host contacted, no
AWS/Vultr tool used, no Order3Certifier / R-stage / kernel certification run. **`c5_forecast.py` was not
executed** — its arithmetic was re-implemented independently and checked value by value.

---

## 0. What the repair commit did and did not touch

| invariant | status |
|---|---|
| `config/FEASIBILITY_GATES_C5.json` | **untouched**, sha still `d0deada6…`, `git diff` over `config/` empty |
| forecast artifact | **absent** — `find evidence -type f` returns exactly the five pre-forecast artifacts |
| theorem arithmetic in `c5_transport.py` | **unchanged** — the only diff is the docstring "at least" → "at MOST" |
| `c5_analysis.py` (incl. `signed_enclosure`, the decomposition) | **unchanged**, so round 1's items B and F carry over |
| anything outside the C5 namespace | **nothing** — `git diff --name-only e12a09e8 5fad47ad` is entirely inside `p5y_k5_tail_c5_exhaustion` |
| `LOCAL_MAIN_REF` / `REMOTE_MAIN_REF` | `c123b9bb…` / `1cb45382…`, both unchanged, still distinct |

`evidence/` now contains five **empty** directories (`adjudication`, `forecast`, `freeze`, `phase3`,
`qualification`). Git does not track them, `git status` is clean, and no forecast output exists. Harmless
scaffolding; noted so no one mistakes the `forecast/` directory for a result.

---

## 1. (C) Route ledger — **repaired; PASS_WITH_NOTES**

### What is now right

A5 and A6 carry `kill_kind: MATH_PARTIAL`, `refuted_at_cells: [308, 309]`, `oracle_closes_at_cells: [307]`, and a
named `kill_kind_at_not_refuted_cells` (DATA for A5, NEW_REAL for A6). `closure_possible` is gone, replaced by
`closure_possible_at_cells`. `refuted_on_mathematics_at_every_still_open_cell` is now `['A4', 'D2']` and the
phase-3 headline reads "only **two** routes are refuted on mathematics at every still-open cell". That is the
correct count and it matches the kill gates, which I re-derived independently in round 1 (σ₃→0: 307 −0.049946
**closes**, 308 +0.007722, 309 +0.055204; σ₄→0: 307 −0.027574 **closes**, 308 +0.027307, 309 +0.072506).

**The ledger JSON reproduces byte-identically** from `c5_ledger.py` run against the committed sensitivity
evidence (`cmp` → identical). Good provenance; the JSON is not hand-edited.

### I attacked both guards. Both fire on the direct attacks

```
ATTACK 1  A5.refuted_at_cells := [307,308,309]   (a lie about its own gate)
  → route A5: claimed refuted_at_cells [307, 308, 309] / oracle_closes_at_cells [307] disagree with
    the kill gate 'sigma3 -> 0' (open [308, 309], closes [307])            REFUSED
ATTACK 2  A5.kill_kind := MATH  (keeping oracle_closes_at_cells=[307])
  → route A5: kill_kind MATH but the oracle closes [307]                   REFUSED
```

### But both guards are narrower than the campaign claims — **note, not blocking**

`cell_scoping_note` and phase-3 say the producer "refuses any `MATH` kill whose oracle closes a cell and
cross-checks each claimed refutation set against the gate". Neither is true in general:

* The gate cross-check (lines 187–196) iterates over a **hardcoded allowlist** `backing = {"A5", "A6"}`, not over
  `ROUTES`. Any route absent from that dict is never checked against any gate.
* The MATH guard (lines 198–200) compares `kill_kind` against `oracle_closes_at_cells` — **two hand-written
  fields of the same dict**. It cannot detect an `oracle_closes_at_cells` that is simply wrong, which is close to
  the v1 defect: v1 did not lie in a checkable field, it asserted a wrong kind beside a correct-but-unread gate.

I demonstrated both holes with fabricated routes:

```
ATTACK 3  new route F1: kill_kind=MATH, oracle_closes_at_cells=[] (by hand), no backing entry,
          real gate 'rho halved' closes 307, 308 AND 309
  → producer ACCEPTS. Emitted: refuted_on_mathematics_at_every_still_open_cell = ['A4','D2','F1']
ATTACK 4  new route F2: kill_kind=MATH_PARTIAL, refuted_at_cells=[307,308,309], no backing entry
  → producer ACCEPTS. Emitted: refuted_on_mathematics_only_at_some_cells = {...,'F2':[307,308,309]}
```

Note also that **A4 and D2 — the two routes that now carry the corrected headline — have no kill gate at all**;
their `oracle_closes_at_cells: []` is an unverified hand assertion and guard B reads that same assertion. I
independently proved D2's identity in round 1 and I find A4's drift-range argument sound, so neither claim is
false. But the headline "refuted on mathematics" currently comprises exactly two gate-free arguments, and the
artifact does not say so.

**Fix (not blocking):** make `kill_gate` a required per-route field naming a knob in the sensitivity evidence;
iterate over `ROUTES`, not `backing`; **derive** `refuted_at_cells` / `oracle_closes_at_cells` from the gate
rather than compare against hand-written copies; and require a route with no gate to declare
`kill_gate: null, argued_without_gate: true` and be counted separately in the headline.

### The E1 withdrawal did not land where it counts — **must fix before adjudication**

`withdrawn_phrase` was added to E1, but the withdrawn sentence survives verbatim in **E1's `kill_reason`** — the
primary field — and in the **phase-3 table row for E1** (line 55: "a live future route for 307 and 308 — and
**provably useless for 309**"), twelve lines above the paragraph that withdraws it. A reader of the table, or a
parser reading `kill_reason`, still gets the withdrawn claim. This is exactly the failure pattern C4's binding
Condition 2 exists for ("two repairs the disposition records as complete did not land in committed evidence").

Two related problems in the same row:

* **E1 still asserts `refuted_at_cells: [309]`**, and its own `max_gain` says that rests on the **DIAGNOSTIC**
  Λ — C4's uncertified Monte-Carlo. That is the precise ground on which v1's E2 kill was condemned, now applied
  to E1 without comment. No guard checks `refuted_at_cells` on a non-MATH route. Drop it, or rename it
  `refuted_at_cells_diagnostic_only`.
* **E2 keeps its full retracted `kill_reason`** with `kill_kind: null` and `status: RE_OPENED_LIVE`. The adjacent
  `reopened_because` makes the situation clear to a human, but the retracted argument sits unmarked in the field
  a parser would read. Rename to `withdrawn_kill_reason`, or prefix "WITHDRAWN:".

### On E2's re-opening, and whether non-execution is a cop-out

**It is correct governance, not a cop-out, and I would reject execution if it were proposed.** The gate is frozen
on route D1; its `refusals` list forbids amending any class, threshold, criterion or permitted conclusion after
freeze; and E2 needs a *new certified lower bound on* Λ₃₀₉, which is a mechanism, not an evaluation. Adding it now
would be exactly the post-freeze scope creep the freeze discipline exists to prevent — and it would be a mechanism
whose result was known to be needed before it was designed, which is the worst possible provenance for a
margin-restoring result. `reopened_because` states the reason for re-opening in full and without self-protection,
including that v1 killed it in the same commit that consumed the margin. Ranking it first among future routes is
the right disposition.

One strengthening I do recommend: at present E2 is a *ranking*. Make it a **binding condition** in the forecast —
that no successor may restate the cell-309 exclusion without either re-deriving the fragility numbers under its
own clause or executing E2. A ranking can be ignored; a condition inherits.

---

## 2. (I) Mutation suite — **the round-1 hole is closed; a new one of the same species is open. FAIL**

### The leftward repair is correct and my exact mutant is now caught

The manufactured cell (`g_hi = −1/5, e0 = 2, ρ = 1/20, H_lo = −1/10, H_hi = 3`) genuinely binds leftward, and I
verified the arithmetic by hand rather than trusting the refusal: `w_R = 0.10125`, `w_L = 0.09875`, rightward term
`0.1 × 0.10125 = 0.010125`, leftward term `3 × 0.09875 = 0.29625` — leftward dominates by 29×. `Γ = −0.2 + 0.29625
= 0.09625`, and the brute-force maximum over the cell is exactly `0.09625`, attained at `e = e0 − ρ = 1.95`. The
`raise SystemExit` if the cell fails to bind leftward is the right guard and is load-bearing.

Re-running my round-1 attack against the repaired suite:

```
w_L := 0 on the manufactured leftward cell:
   binding=leftward  true=0.09625  brute-force=0.09625  mutant=-0.189875   CAUGHT=True
```

M13 (`w_L := ρ(x_lo − ρ/2)`) likewise: `0.08875 < 0.09625`, caught. Both now `DETECTED_BY_VERDICT`. The relabelling
of M02/M04 to `DETECTED_BY_ARGUMENT` and the admission of `PROVED_EQUIVALENT` to the docstring's outcome list are
both correct and honestly worded.

### FAIL (a) — `invisible_on_real_cells` is factually wrong in committed evidence

`C5_MUTATIONS.json` records `"invisible_on_real_cells": false` on **both** M12 and M13, in direct contradiction of
the same rows' own `how` text ("on the four real tail cells it is invisible, which is exactly why the manufactured
cell is required") and of the round-1 finding the repair was made to record.

The cause is a bug:

```python
caught_real = any(TR.gamma(v["g_hi"], v["Hlo"], v["Hhi"], v["e0"], v["rho"])["Gamma"] != mg
                  for v in st.values())
```

`mg` is the **manufactured** cell's mutant Γ (−0.189875), the comparison is against the four **real** cells' Γ,
and `TR.weights` has already been restored by the enclosing `finally` — so this compares unmutated real Γ values
to an unrelated synthetic number and is True by construction. Recomputed honestly (mutated vs unmutated on the
real cells, same mutation live):

```
mutated == unmutated on all four real cells: True   =>  true invisible_on_real_cells = True
                                                        the artifact records False
```

This field is the record of *why* the manufactured cell is necessary. As committed, it tells an adjudicator the
suite's real-cell coverage is better than it is. Fix: compare mutated against unmutated **on the real cells**.

### FAIL (b) — a new surviving unsound mutant, and it is structural

Following the coordinator's own pointer to `signed_enclosure` and the cross-check, I constructed:

> **M14 candidate — negate-and-swap:** `signed_enclosure` returns `(−H_hi, −H_lo)` instead of `(H_lo, H_hi)`.

Result on all four real tail cells:

| cell | `P` true | `P` mutant | unsound (smaller) | `M` unchanged | forecast cross-check passes | part (1) "sound" |
|---|---|---|---|---|---|---|
| 306 | 0.263248222 | 0.256791915 | yes | yes | **yes** | **yes** |
| 307 | 0.294280367 | 0.286854257 | yes | yes | **yes** | **yes** |
| 308 | 0.335117620 | 0.326434229 | yes | yes | **yes** | **yes** |
| 309 | 0.371472388 | 0.361725695 | yes | yes | **yes** | **yes** |

At cell 309 the forecast would report `Γ_C5T = +0.138400` instead of `+0.148146` — a **2.62 % understatement of
the penalty, more than double C5-T's entire 1.29 % claimed gain**, and it survives every check in the campaign.

Why each defence fails:

* **The forecast cross-check is sign-blind by construction.** It compares `Γ_frozen = g_hi + ρ·x_hi·M` against
  `d["Gamma"]`, and `M = max(|H_lo|, |H_hi|)` is invariant under negate-and-swap. Control: a magnitude-changing
  mutation (`H_lo × 0.9`) *is* caught, which confirms the cross-check works — just not on signs.
* **Part (1) is self-consistent with whatever enclosure it is handed.** `brute_max` is called with the same
  (mutated) `H_lo`, `H_hi`, so it validates C5-T against the mutated inputs, not against the true enclosure. A
  mutation *of* `signed_enclosure` is invisible to it by design.
* **M03 does not cover it.** M03 swaps the ends without negating, producing `H_lo > H_hi`, which the
  `inverted R'' enclosure` guard catches. Negate-and-swap yields a **well-ordered** interval, so the guard never
  fires. The suite tests the detectable sign mutation and misses the undetectable one.

The shipped code is **correct** — I verified `H_lo == d["lo"]` and `H_hi == d["hi"]` exactly on all four cells (the
`R2_interval` intersection and the `±M_R2` clamp are both no-ops, since `M_R2 == −R2_interval.lo` and the TC-T
enclosure is strictly inside `R2_interval`). So no number in the tree is wrong. What fails is the assurance
claim "13 mutants, 0 undetected" as evidence that the sign-bearing input is defended.

### The fix, and the terminating condition

The structural fault, stated once: **`signed_enclosure` is the only input the forecast takes on trust from another
module.** Everything else it already re-derives or cross-checks — `g_hi` is computed inline from the sealed record,
`e0` and `ρ` come from the cover and are validated by the cross-check's `x_hi = e0 + ρ` against `cov["right"]`, and
`M` is cross-checked against `d["M"]`. Close that one gap and the *class* closes, not just this instance:

1. In `evaluate()`, `c4_recheck()` and `exclusion_fragility()`, re-derive instead of trusting — assert
   `H_lo == max(F(ad5["R2_interval"]["lo"]), d["lo"])` and `H_hi == min(F(ad5["R2_interval"]["hi"]), d["hi"])`
   against the frozen consumer's own **signed** endpoints, and refuse on mismatch.
2. Add M14 = negate-and-swap `signed_enclosure`, which that assertion then catches.
3. Fix the `invisible_on_real_cells` computation.

**That is my terminating condition.** With the sign-bearing input re-derived rather than trusted, every quantity
C5-T consumes is either computed in the forecast from a sealed artifact or cross-checked against the frozen
consumer, and I will not ask for a fourth round on mutant-hunting grounds.

---

## 3. The fragility disclosure — **PASS, and it exceeds what I asked for**

`exclusion_fragility()` computes rather than quotes. I re-implemented its logic independently — same bisections,
same knobs, without calling it — and **every value reproduces exactly**:

| currency | frozen clause | under C5-T |
|---|---|---|
| margin in Γ at the C4 floor | +0.004661130 | **+0.001708896** (36.6627 % retained) |
| critical `A0` (A1 = A2 = 0) vs `B` = 3.297250282 | 3.214236023 → **2.5827 %** slack | 3.266415728 → **0.9440 %** slack |
| further penalty cut that voids the exclusion | — | **0.759392 %** |
| `f_G` cut that voids it (DIAGNOSTIC) | — | **1.3040 %** |
| `env4` cut | — | 3.3227 % |
| `σ₃` cut | — | 3.2365 % |
| `σ₄` cut | — | 3.6694 % |
| all four source knobs together | — | **0.6076 %** |
| candidate sup norms `sup{F,D,H}` | **5.5357 %** | **2.0562 %** (a 2.7× loss of buffer) |

The `f_G` (1.30 %) and all-four-together (0.61 %) figures are **tighter than anything I reported in round 1** — the
producer discloses more against itself than I demanded. The epistemic labelling is right: the critical-`A0`
bisections scale no ingredient, so `knock` leaves the independent TC-T crosscheck **live** and they are
certified-grade; every `voiding_cut` row scales an ingredient and is correctly declared DIAGNOSTIC in `status`.

`C4_scope_sentence_must_be_restated` states the point I raised, accurately and without hedging, and
`5_can_a_tighter_transport_void_it` gives the correct two-part answer (no within the transport family, by the
attainment argument; yes by an enclosure improvement, which is outside it).

Two small things: the prose in field 5 hardcodes "0.76 %" and "~2 %" as literals beside fields 3 and 4 that
compute them — interpolate, or the prose will drift from the numbers. And `exclusion_fragility` calls
`frozen_stack()` a third time in one run; deterministic and pinned, so correct, just wasteful.

---

## 4. Round-1 notes — all landed, verified

| round-1 note | status at `5fad47ad` |
|---|---|
| `B0_02_worktree_clean_at_audit` misleading name | renamed `B0_02_worktree_state_recorded`, with the reason in a comment ✔ |
| `B0_14` name overclaimed vs its body | renamed `B0_14_local_main_not_advanced` ✔ |
| docstring "sixteen checks" | "seventeen" ✔ |
| `M = |centre| + S` category error | corrected to `M = |C_lo| + S` **exactly**, with the binding-end reason and the consequence that the `S`-must-fall figures are exact, not first-order ✔ |
| `improvement_factor` "at least" | "at MOST", with the reason ✔ |
| `remote_hosts_contacted: 0` imprecise | replaced by an explicit statement naming the two read-only `git ls-remote` calls ✔ |
| dead `Hlo, Hhi` in `exhaustion_argument` | deleted ✔ |

`ERRATUM_C5_GATE.md` (E1–E5) is accurate. I checked its load-bearing table against my own computation: the
both-metrics figures (M-factor 14.088 / 4.591 / 3.186 % vs atom-constant 14.253 / 4.826 / 3.482 %) are **exactly**
mine, and its conclusions — threshold genuinely inherited, metric silently substituted, substitution slightly
harsher and therefore not outcome-fitting — are all correct. E2 (rounded baseline), E3 (INVALID unreachable) and
E4 (the gate should have required the C4 scope restatement) are correctly stated and correctly not used to amend
the frozen gate.

Two further notes:

* **`phase_6/C5_SELECTED_MECHANISM.md`** (new, not in the coordinator's summary) is a clean, correct restatement of
  the theorem; I re-checked every step against my round-1 derivation. But its closing claim — "across all five tail
  cells and all four `m` values — **twenty rows** — `Γ_C5T ≤ Γ_frozen` holds with **zero** exceptions" — asserts a
  sweep **no C5 producer performs**: `FC.direct` is hardwired to `m = 5` and only four cells are ever evaluated.
  The claim is *true by theorem* (`P ≤ frozen` is proved and enforced at runtime) and the same paragraph says so,
  but "holds with zero exceptions" reads as a verified sweep. State it as a corollary, or run it.
* **The B0 evidence is stale**: it records `head: cd4a72d3` and `uncommitted: 11`, i.e. it was re-run before the
  repair landed. I verified independently that the invariant it asserts still holds at `5fad47ad` — nothing outside
  the C5 namespace changed since `e12a09e8`, and both main refs are unchanged and still distinct. Re-run it at the
  final HEAD before adjudication.
* My round-1 report is committed at `review/REVIEW_C5_PREFORECAST.md` and will need replacing with this one.

---

## Summary

| item | round 1 | round 2 |
|---|---|---|
| A predecessor integrity / main refs | PASS_WITH_NOTES | **PASS** (both names fixed; refs verified unchanged and distinct) |
| B blocker decomposition | PASS | **PASS** (unchanged code; wording corrected) |
| C route-search completeness and kill honesty | **FAIL** | **PASS_WITH_NOTES** (cell scoping correct; guards narrower than claimed; E1 withdrawal incomplete) |
| D theorem C5-T | PASS_WITH_NOTES | **PASS** (docstring corrected; arithmetic unchanged) |
| E zero-new-real compliance | PASS_WITH_NOTES | **PASS** (`remote_hosts_contacted` now precise) |
| F whole-cell vs midpoint scopes | PASS | **PASS** |
| G dependency / independence | PASS | **PASS** |
| H gate prospective integrity | PASS_WITH_NOTES | **PASS** (gate untouched; erratum E1–E5 accurate) |
| I mutation adequacy | **FAIL** | **FAIL** (leftward hole closed; sign-direction hole open; one field factually wrong) |
| J exhaustion semantics | PASS | **PASS** |
| K scoping of impossibility claims | PASS_WITH_NOTES | **PASS_WITH_NOTES** (E1's withdrawn phrase still asserted in two places) |
| L main-ref distinction | PASS | **PASS** |
| the C4 cell-309 ruling | disclosure incomplete | **PASS** — all five currencies computed, reproduce exactly, and disclose more than I asked |

The repair is substantial and honest. Both round-1 findings are genuinely fixed, not papered over: my exact
`w_L := 0` mutant is caught, the ledger's cell scoping is correct and machine-checked, the guards fire on direct
attack, the ledger reproduces byte-identically from its producer, and the fragility block computes every number I
demanded plus three tighter ones I had not found. The gate is untouched, no forecast artifact exists, and the
theorem's arithmetic is unchanged and still correct.

**What still blocks, all inside the mutation phase, and all one-line fixes:**

1. `C5_MUTATIONS.json` records `invisible_on_real_cells: false` on M12 and M13, contradicting its own prose and
   the finding it was written to record. The comparison is against the manufactured cell's Γ with the weights
   already restored, so it is True by construction. The honest value is **True** on both.
2. A **new surviving unsound mutant**: negate-and-swap `signed_enclosure` → `(−H_hi, −H_lo)`. It preserves
   `max(|H_lo|, |H_hi|)`, so the forecast's `Γ_frozen == d["Gamma"]` cross-check passes; part (1) is
   self-consistent with the mutated enclosure; M03 misses it because the result is well-ordered. At cell 309 it
   understates the penalty by 2.62 % — twice C5-T's entire gain. The shipped code is correct, but the sign-bearing
   input is undefended, because it is validated only against a sign-blind quantity.
3. E1's withdrawn phrase "provably useless for 309" survives verbatim in its `kill_reason` and in the phase-3 table
   row, and E1 still asserts `refuted_at_cells: [309]` on a DIAGNOSTIC basis. (Must land before adjudication;
   would not on its own block the forecast.)

Fix 1 and 2 — assert `H_lo == max(R2lo, d["lo"])` and `H_hi == min(R2hi, d["hi"])` in the three consumers, add M14,
and correct the `invisible_on_real_cells` computation — and **every input C5-T consumes is then either computed in
the forecast from a sealed artifact or cross-checked against the frozen consumer.** That closes the class, and I
will not ask for a fourth round on mutant-hunting grounds.

Everything else is ready. On my independent recomputation the forecast will emit exactly:
`C5_PRIMARY_CLASS = MARGINAL`, `closed = [306]`, `newly_closed = []`, `still_open = [307, 308, 309]`,
`materially_tightened = {307: false, 308: false, 309: false}` (gap falls 14.088 % / 4.591 % / 3.186 % against the
inherited 20 % threshold), `Γ_C5T = −0.039425934 / +0.022641576 / +0.090222449 / +0.148146343`,
`exhaustion = EXHAUSTED`, `c4_still_excluded = {308: false, 309: true}`, no HARD_STOP, `adopted_cells = []`,
`coverage_map_revision = null`.

HANDOVER: NOT_READY
