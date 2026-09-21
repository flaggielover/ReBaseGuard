# Independent fresh-context pre-forecast review — P5Y / K5 Campaign C5 — ROUND 3 (final)

Same fresh-context reviewer, third pass, at HEAD `e667cdc5` on `p5y-k5-tail-c5`. Read-only throughout: nothing in
the repository was created, edited or committed. No remote host contacted, no AWS/Vultr tool used, no
Order3Certifier / R-stage / kernel certification run. **`c5_forecast.py` was not executed** — including the new
`no_regression_sweep()` and `checked_enclosure()`, whose arithmetic I re-implemented independently in scratch.

**My round-2 terminating condition is met.** I could not get past `checked_enclosure`, all four of my ledger
attacks now refuse, the two wrong fields are corrected, and the twenty-row claim is now a real sweep whose every
row I reproduced. One stale markdown line remains, and the erratum claims it was fixed; that is a text repair, not
a forecast blocker, and I say why below rather than hiding behind the rule.

---

## 0. Invariants re-checked at the new HEAD

| invariant | status |
|---|---|
| `config/FEASIBILITY_GATES_C5.json` | **untouched** — sha still `d0deada6…`, `git diff` over `config/` empty across all three rounds |
| forecast artifact | **absent** — `find evidence -type f` returns exactly five pre-forecast artifacts; the empty scaffolding directories are gone |
| `c5_transport.py`, `c5_analysis.py` | **untouched this round** (`git diff --stat` empty), so round-1 items B, D, F, G, J stand unchanged |
| anything outside the C5 namespace | **nothing** since `e12a09e8` |
| `LOCAL_MAIN_REF` / `REMOTE_MAIN_REF` | `c123b9bb…` / `1cb45382…`, unchanged, still distinct, still never compared |

---

## 1. FAIL (b) — the sign-bearing input: **CLOSED**

### Every consumer is rewired; zero unchecked paths

Static audit of `c5_forecast.py`: `checked_enclosure` is called at lines 76 (`evaluate`), 159 (`c4_recheck`), 196
and 213 (`exclusion_fragility`). The **only** `signed_enclosure(` call in the file is line 51, inside
`checked_enclosure`'s own body. Unchecked call sites: **zero**.

### I attacked `checked_enclosure`. It holds

| attack on `signed_enclosure` | result |
|---|---|
| negate-and-swap `(−H_hi, −H_lo)` — **my M14** | **REFUSED** |
| `H_lo` shrunk by 1 part in 10⁹ | **REFUSED** |
| `H_hi` widened to `−H_lo` (magnitude-preserving, invisible to the `Γ_frozen` cross-check) | **REFUSED** |
| `empty` flag flipped to `True` | **REFUSED** |
| skip the `R2_interval` intersection | survived — **and this is not a weakness** |
| skip the `±M_R2` clamp | survived — **and this is not a weakness** |

The last two survive because on this data they are **correct**: the TC-T enclosure is strictly inside
`R2_interval` and `M_R2 == −R2_interval.lo` on **all twenty** (cell, m) rows — I verified both identities
independently — so each step is a no-op and returns the identical value to the honest function. The control row
confirms it: all three return exactly `(−3.3195244535, +3.1465429689, False)`.

The design is right in a way worth recording: `checked_enclosure` returns **`want`**, its own re-derivation, not
`got`. So even if the containment invariant ever failed, the forecast would consume the correct value and the
disagreement would surface as a refusal rather than as a silently wrong number.

The endpoints now trace to two independent derivations: `d["lo"]`/`d["hi"]` come from `T.tail_enclosure`, which
`FC.direct` already cross-checks against `tail_enclosure_crosscheck` (a path sharing no function), and
`max(|H_lo|,|H_hi|)` is cross-checked against `d["M"]`. **Every input C5-T consumes is now either computed in the
forecast from a sealed artifact (`g_hi`) or cross-checked against the frozen consumer (`e0`, `ρ`, `M`, and the
signed endpoints).** That is my terminating condition, and it is satisfied.

### M14 is recorded accurately

`DETECTED_BY_GUARD`; `penalty_true` 0.371472388067586, `penalty_mutant` 0.3617256954265163,
`understatement_percent` **2.6238000331 %** — all three match my independent computation exactly. The `note`
correctly states it is caught *only* because the forecast re-derives, and that every other defence is sign-blind
by construction. 14 mutants, 0 undetected.

---

## 2. FAIL (a) — `invisible_on_real_cells`: **CLOSED**

Both M12 and M13 now record `true`, computed with the mutation live on the real cells on both sides. That matches
my round-2 honest recomputation exactly (mutated == unmutated on all four real cells), and the field no longer
contradicts its own `how` text.

---

## 3. (C) Ledger guards generalised: **CLOSED**

The producer now iterates `ROUTES`, requires either a `kill_gate` naming a knob in the sensitivity evidence or
`argued_without_gate`, and **derives** `refuted_at_cells` / `oracle_closes_at_cells` from the gate — a declared set
that disagrees is refused, an absent one is filled in, and the derived values are what get serialised, so no
hand-written copy can survive into the artifact. Six routes are gate-backed (A1, A2, A3, A5, A6, B1).

**The committed ledger JSON reproduces byte-identically** from the producer. All four of my attacks now refuse:

```
ATTACK 3a  MATH, no kill_gate, no argued_without_gate
  → route F1: no kill_gate and no argued_without_gate declaration                           REFUSED
ATTACK 3b  MATH, argued_without_gate=True, no `argument`
  → route F1: a gate-free MATH kill must carry an `argument` field                          REFUSED
ATTACK 4a  MATH_PARTIAL citing the real rho gate, refuted_at_cells fabricated as [307,308,309]
  → route F2: declared refuted_at_cells [307,308,309] disagrees with gate
    'rho halved (cover refinement)' (derived [])                                            REFUSED
ATTACK 4b  MATH citing the real rho gate (which closes all three)
  → route F3: kill_kind MATH but the oracle closes [307, 308, 309]                          REFUSED
```

Two residuals, neither a defect:

* A gate-free `MATH` kill with any prose `argument` is accepted. That is **correct by design** — D2's identity
  cannot be expressed as a knockout, and A4's is an absence-of-data argument — and the mitigation is disclosure,
  which is present and accurate: `refuted_without_a_kill_gate: ["A4","D2"]` plus a `headline_caveat` saying the
  corrected headline rests on two gate-free arguments. For the record, I checked both myself: **D2's identity I
  proved** by exhaustive case analysis, and A4's drift-range argument is sound. The `argument` fields now in the
  artifact state both correctly.
* A `MATH_PARTIAL` whose **derived** `refuted_at_cells` comes back empty is accepted and lands in
  `refuted_on_mathematics_only_at_some_cells` as `{"F5": []}` — a vacuous "refuted at no cells" entry.
  Unreachable in the present ledger (A5 and A6 both derive `[308, 309]`). One line: refuse it.

### E1 / E2 hygiene — landed in the JSON, **one markdown line missed**

In `C5_ROUTE_LEDGER.json`: E1's `kill_reason` is rewritten without the withdrawn phrase, `refuted_at_cells` is now
`[]` with `refuted_at_cells_diagnostic_only: [309]` and a `diagnostic_basis` field naming C4's uncertified
Monte-Carlo; E2 carries `withdrawn_kill_reason` with a "WITHDRAWN —" prefix. All correct.

**But `phase_3/C5_ROUTE_SEARCH.md` line 55 is unchanged and still reads:**

> `| E1 | tighten A0 by operator certification | KILLED | DATA | needs python-flint, absent. A live future route for 307 and 308 — and **provably useless for 309**. |`

`git diff 5fad47ad e667cdc5 -- phase_3/` is empty; the file was not touched this round. And **ERRATUM E7 now
asserts the repair landed** — "it is now confined to `withdrawn_phrase`" — which is false of the phase-3 table.
That is the C4-Condition-2 pattern for the third time in this campaign: a repair recorded as complete that did not
land in committed evidence. Fix the table cell **and** the erratum sentence.

I am not blocking the forecast on it, and I want to be explicit about why rather than invoke a rule: it changes no
number, no producer and no gate; the claim is withdrawn twelve lines below it in the same file; and the
machine-readable artifact an adjudicator would parse is already clean. It must land before adjudication.

---

## 4. The twenty-row no-regression sweep: **executed, and I reproduced it**

I re-implemented `no_regression_sweep()`'s logic independently and ran all twenty rows. **Zero anomalies**, and
every premise it relies on holds:

* `M_R2 == max(|R2_lo|, |R2_hi|)` on **all 20** rows — so `Γ_frozen = g_hi + ρ·x_hi·M_R2` really is the frozen
  clause at that enclosure;
* `cov["right"] == e0 + ρ` exactly on all five cells, **including 305**, which no other C5 producer touches;
* `x_lo = e0 − ρ > 0` on all five, so C5-T's premise holds for every row and `TR.gamma` refuses none of them;
* `Γ_C5T ≤ Γ_frozen` on all 20, and no row closing under the frozen clause fails to close under C5-T.

Sample (m = 5): 305 +0.041841 → +0.037327; 306 +0.117964 → +0.112868; 307 +0.199484 → +0.193613;
308 +0.288317 → +0.281497; 309 +0.374145 → +0.366408.

Two notes on how it is reported:

* Those are **not** the authoritative Γ. The sweep deliberately uses the sealed `R2_interval` and `M_R2` so it is
  independent of the TC-T supply and works at m = 1, 2, 3 — the docstring says so — but the row keys are plain
  `Gamma_frozen` / `Gamma_C5T`, and at 309 m = 5 the sweep prints **+0.374145** where the authoritative Γ is
  **+0.153020**. Add a per-row or per-block marker: `"enclosure": "sealed R2_interval, NOT the authoritative
  TC-T-intersected M"`. Without it a reader could quote the wrong number.
* `violations` is effectively unreachable. Since `M_R2 == mag(R2_interval)` on every row, the `tighter` test is
  exactly the inequality `TR.penalty`'s tripwire already refuses on, so a genuine violation would **abort** the
  run rather than be counted. Fail-closed and therefore fine — but `violations: 0` reads stronger than it is, and
  the artifact should say that a violation is a refusal, not a count.

---

## 5. Recommendations taken — all three verified

* **E2 as a binding condition.** `binding_conditions_on_any_successor` states it, plus the C4 scope-sentence
  requirement and the family-exhaustion limit. This is the right shape: a ranking can be ignored, a condition
  inherits.
* **Fragility prose interpolated.** Fields 3 and 4 are now f-string-interpolated from the computed values, so the
  prose cannot drift. I re-verified every fragility number independently once more against round 2: Γ margin
  +0.004661130 → +0.001708896 (36.6627 % retained); critical `A0` 3.214236023 → 3.266415728 against
  `B` = 3.297250282, i.e. **2.5827 % → 0.9440 %** slack; further penalty cut **0.759392 %**; voiding cuts `f_G`
  1.3040 %, `env4` 3.3227 %, `σ₃` 3.2365 %, `σ₄` 3.6694 %, all four together **0.6076 %**, candidate sup norms
  **2.0562 %** under C5-T against **5.5357 %** under the frozen clause. All exact.
* **Phase-6 wording.** Now says the invariant is structural *and* executed, and names the producer. Correct.

`ERRATUM_C5_GATE.md` E6 and E7 are accurate and self-critical, with one exception: E7's claim about the phase-3
table row (§3 above).

---

## 6. Remaining notes, none blocking

1. **Must land before adjudication** — phase-3 line 55, and the E7 sentence that claims it was fixed.
2. `no_regression_sweep` rows need an `enclosure` marker; `violations: 0` should say a violation is a refusal.
3. `MATH_PARTIAL` with an empty derived refutation set should be refused.
4. M14's `guard` field is **6 193 characters** of raw `Fraction(...)` repr, because the refusal message formats the
   endpoint tuples with `repr`. Truthful but it bloats the artifact; format them as decimals.
5. The B0 audit records `head: 5fad47ad`, `uncommitted: 8` — it cannot record the commit that contains it. I
   verified its assertions independently at `e667cdc5`: nothing outside the C5 namespace has changed since
   `e12a09e8`, and both main refs are unchanged and distinct. A fixpoint problem, not a defect; the adjudicator
   should re-run it.
6. `frozen_stack()` is now re-executed four times per forecast run (`evaluate`, `c4_recheck`,
   `exclusion_fragility`, `no_regression_sweep`). Deterministic and pinned, so correct; just wasteful.

---

## Summary

| item | R1 | R2 | R3 |
|---|---|---|---|
| A predecessor integrity / main refs | PASS_WITH_NOTES | PASS | **PASS** |
| B blocker decomposition | PASS | PASS | **PASS** |
| C route-search completeness and kill honesty | **FAIL** | PASS_WITH_NOTES | **PASS_WITH_NOTES** (one stale markdown line) |
| D theorem C5-T | PASS_WITH_NOTES | PASS | **PASS** |
| E zero-new-real compliance | PASS_WITH_NOTES | PASS | **PASS** |
| F whole-cell vs midpoint scopes | PASS | PASS | **PASS** |
| G dependency / independence | PASS | PASS | **PASS** |
| H gate prospective integrity | PASS_WITH_NOTES | PASS | **PASS** |
| I mutation adequacy | **FAIL** | **FAIL** | **PASS** |
| J exhaustion semantics | PASS | PASS | **PASS** |
| K scoping of impossibility claims | PASS_WITH_NOTES | PASS_WITH_NOTES | **PASS_WITH_NOTES** |
| L main-ref distinction | PASS | PASS | **PASS** |
| the C4 cell-309 ruling | incomplete | PASS | **PASS** |

Three rounds, and each repair went to the cause rather than the symptom: the leftward branch was not patched but
*exercised* on a manufactured cell that the producer refuses to accept unless it really binds; the ledger guards
were not extended but **inverted**, so the gate is the source of truth and hand-written sets are derived rather
than compared; and the sign-bearing input is not asserted but **re-derived**, with the function returning its own
derivation rather than the value it was handed. Twice the campaign found and disclosed more against itself than I
had asked for — the `f_G` 1.30 % and all-four-together 0.61 % voiding cuts, and the `headline_caveat` admitting
that its own corrected headline rests on two gate-free arguments.

**The theorem is correct, every number reproduces exactly, the gate was never touched, no forecast artifact
exists, and I found no surviving unsound mutant this round.** I said in round 2 that I would not ask for a fourth
round on mutant-hunting grounds, and I am not.

On my independent recomputation the forecast will emit exactly:
`C5_PRIMARY_CLASS = MARGINAL`, `closed = [306]`, `newly_closed = []`, `still_open = [307, 308, 309]`,
`materially_tightened = {307: false, 308: false, 309: false}` (gap falls **14.088 % / 4.591 % / 3.186 %** against
the inherited 20 % threshold), `Γ_C5T = −0.039425934 / +0.022641576 / +0.090222449 / +0.148146343`,
`exhaustion = EXHAUSTED`, `c4_still_excluded = {308: false, 309: true}` with `margin_retained_percent ≈ 36.6627`,
no `HARD_STOP`, `no_regression_sweep.violations = 0` over 20 rows, `adopted_cells = []`,
`coverage_map_revision = null`.

If the run produces anything other than that, stop and re-review rather than adjudicating.

HANDOVER: READY_TO_FORECAST_WITH_NOTES
