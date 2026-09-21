# Independent fresh-context adjudication — P5Y / K5 Campaign C5

Adjudicator: fresh context, no prior involvement in this programme. Target: `/Users/suzhe/ReBaseGuard-k5c5`,
branch `p5y-k5-tail-c5`, HEAD `8b2be7ab`, namespace `level4/closure_proofs/p5y_k5_tail_c5_exhaustion`.

Read-only throughout. Nothing in the working tree was created, edited, committed or deleted; `git status` was clean
at the start and clean at the end. No remote host was contacted, no `rebaseguard-aws` / `rebaseguard-vultr` tool was
used, no Order3Certifier, R-stage or kernel certification was run. All scratch work is under the session scratchpad.
Every number below I either re-derived from an independent re-implementation or re-ran and compared byte for byte.

---

## 1. Is the C5 theorem/mechanism sound?

**Yes. Theorem C5-T is correct, and I checked every step rather than the statement.**

*The derivative identity.* `g(e) = R(e) − e R'(e)` gives `g'(e) = R'(e) − R'(e) − e R''(e) = −e R''(e)`. Correct.

*The rightward branch.* For `e ≥ e0`, `g(e) − g(e0) = −∫_{e0}^{e} t R''(t) dt`. Since `t > 0` on the cell,
`−t R''(t) ≤ t·(−R''(t))⁺`, and `R''(t) ≥ H_lo` gives `(−R''(t))⁺ ≤ (−H_lo)⁺`. The integrand being non-negative,
extending the upper limit to `e0+rho` only increases the integral. So the bound is
`(−H_lo)⁺ ∫_{e0}^{e0+rho} t dt`. Each of the three inequalities needs `t > 0`; the second and third would both fail
on a cell straddling the origin.

*The weights.* `∫_{e0}^{e0+rho} t dt = ((e0+rho)² − e0²)/2 = rho·(e0 + rho/2)`, and `x_hi = e0+rho` gives
`e0 + rho/2 = x_hi − rho/2`, so `w_R = rho(x_hi − rho/2)`. **Correct.**
`∫_{e0−rho}^{e0} t dt = (e0² − (e0−rho)²)/2 = rho·(e0 − rho/2)`, and `x_lo = e0−rho` gives `e0 − rho/2 = x_lo + rho/2`,
so `w_L = rho(x_lo + rho/2)`. **Correct.** I recomputed both from the primitive `(b²−a²)/2` in my own code and
asserted equality with `rho*(x_hi − rho/2)` and `rho*(x_lo + rho/2)` at all four cells: exact match in rationals.

*The leftward branch.* `g(e) − g(e0) = ∫_{e}^{e0} t R''(t) dt ≤ (H_hi)⁺ w_L`. Correct, same positivity requirement.

*`x_lo > 0` is required and is enforced.* It is required at three separate points above. It is enforced in
`c5_transport.weights`, which raises `TransportRefusal` when `x_lo <= 0`, and mutant M07 exercises it.

*No-regression.* `P ≤ M·max(w_R, w_L) = M·w_R = M·rho(x_hi − rho/2) < M·rho·x_hi` for `rho > 0`. Proved, and
additionally asserted at runtime in `penalty()` (fail-closed: it raises rather than recording a violation).

**One unstated scope hole, which is mine, not the campaign's.** The premise `x_lo > 0` fails at exactly one
committed K1 cell: cell 0 has `left = 0` and `e0 = rho = 0.00025415`, so `x_lo = 0` — for **both** detectors
(CUSUM and SR). C5-T therefore cannot be a blanket replacement of the K5-B direct clause; at cell 0 the module
refuses and the frozen clause must remain. Nothing in the gate, the forecast or `phase_6/C5_SELECTED_MECHANISM.md`
says so, and the permitted conclusion "adopted into the authoritative clause" is stated without that restriction.
Cell 0 is precisely the cell the one real order-3 probe closed, so this is not a hypothetical cell. Condition 3.

---

## 2. Is temporal integrity valid? Was the gate frozen before the forecast?

**Yes, and I verified it from the object store rather than from the commit messages.**

* `config/FEASIBILITY_GATES_C5.json` hashes to `d0deada65971c3658e7d3b39f8b2bbf5ea4849f25a1570d8f3d272a2f996aa58`
  in the working tree **and** as a blob at `d2426c03` — the gate has not moved since the freeze commit.
* `d2426c03` (2026-09-22 03:18:46 +0900) adds exactly one file, the gate, and nothing else.
* `git log --all --name-only -- '*C5_FORECAST.json'` returns one commit, HEAD `8b2be7ab` (04:27:46). I additionally
  walked every commit reachable from every ref with `git ls-tree -r` and no other tree contains
  `.../evidence/forecast/`. `git fsck --lost-found` surfaces one dangling commit, `1301f8bb`, which is an unrelated
  2026-09-01 P6 screening-array preservation commit, and no dangling tree containing a C5 forecast.
* The reflog shows a clean linear sequence `e12a09e8 → 27a12bef → d2426c03 → cd4a72d3 → 5fad47ad → e667cdc5 → 8b2be7ab`
  with no rewinds after the freeze.

The gate is frozen, it is prior to the forecast artifact and prior to the forecast producer (`cd4a72d3`), and no
pre-freeze forecast exists anywhere in the object store.

---

## 3. Is the gate genuinely prospective? Is the disclosure adequate and are the classes fitted?

**The gate is post-hoc in the strict sense, the disclosure is adequate, and the classes are not fitted.**

`c5_transport.py` — the theorem, with its final arithmetic — landed at `27a12bef`, **twenty seconds before** the
freeze commit. The pre-freeze ledger already records `max_gain: "1.211% to 1.295% of the penalty; closes nothing"`
and the full C5-T formula. So the gate was written by an author who knew the answer to six significant figures.

That is disclosed, in full, in `prior_evidence_known_at_freeze`: the selected route, the four per-cell improvement
percentages, the four resulting `Gamma` values, the expected class `MARGINAL`, the expected exhaustion verdict, and
the expected effect on C4 (`+0.004661130 → +0.001708896`, 36.7% retained). The disclosure names what it does not
excuse and asks the reviewer to look for fitting explicitly. This is the right way to run a post-hoc freeze.

**Are the classes fitted? No, and I tested it rather than accepting the assurance.** The class boundary that matters
is the 20% material-tightening threshold. I confirmed `0.20` in `FEASIBILITY_GATES_C2.json` and `0.2` in
`FEASIBILITY_GATES_C3.json`, the latter with C3's own recorded justification for inheriting rather than choosing. The
observed gap falls are 14.088% / 4.591% / 3.186%. Because the class requires **every** still-open cell to clear the
threshold, cell 309's 3.186% binds: the verdict would remain `MARGINAL` for **any** threshold above 3.19%, i.e.
across a 6× range around the inherited value. A fitted threshold would have to be within a factor of 1.05 of a
boundary; this one is nowhere near. Not fitted.

**One real defect, correctly confined to the erratum.** E1 concedes that C2/C3 measure the gap of the uniform
**atom-constant** reduction factor while C5 measures the gap of the **M-reduction** factor, and that the gate's
`inherited_from` sentence implies more continuity than exists. I checked C2's gate directly: it defines
`gap(cell) := requirement(cell) − 1` on the atom-constant requirement, with baseline gaps 0.2621 / 0.6635 / 1.1016 —
so C5 changed **both** the metric and the baseline, not only the metric. E1's defence is that the two metrics agree
to within 0.3 percentage points and that the substituted one is slightly harsher, and both halves of that are
correct. The substitution is therefore undisclosed-at-freeze but not outcome-fitting. E3 (class `INVALID`
unreachable because every premise failure raises before any artifact is written) and E2 (a five-decimal rounded
baseline used as a denominator, relative error ~7·10⁻⁶) are correctly recorded and correctly not used to amend the
frozen gate.

---

## 4. Are all inputs certified and within domain?

**Yes for the four cells in the universe; see §1 for the cell-0 domain hole outside it.**

* `g_hi = R.hi − e0·D.lo` is formed in the forecast itself from the sealed adopted K1 record
  (`p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json`), certified at `e0`. The substitution
  `sup(−e0·R'(e0)) = −e0·D.lo` requires `e0 > 0`, which holds.
* `[H_lo, H_hi]` is the sealed `R2_interval` intersected with the frozen TC-T whole-cell enclosure and clamped to
  `±M_R2` — whole-cell, as the theorem requires. The forecast **re-derives** these signed endpoints
  (`checked_enclosure`) and refuses on disagreement with `signed_enclosure`; mutant M14 exercises exactly that.
* `e0`, `rho`, `x_lo`, `x_hi` come from the K1 cover ledger `cells.json`. I checked `e0 + rho == right` and
  `e0 − rho == left` exactly in rationals at all four cells, independently of the campaign's own cross-check.
* Domain: `x_lo > 0` holds at 306–309 (`left` = 1.6851 … 1.9839).
* `Gamma_frozen` reconstructed from these same inputs reproduces the frozen consumer's `d["Gamma"]` **exactly** at
  all four cells, and my independently computed `M = max(|H_lo|,|H_hi|)` equals `d["M"]` exactly. That is the
  strongest available evidence that the enclosure has been read with the right orientation.

---

## 5. Is the result reproducible?

**Yes, at two independent levels.**

*Re-run.* `python3 -B c5_forecast.py --out <scratch>` produces a file **byte-identical** to the committed
`evidence/forecast/C5_FORECAST.json`, sha256 `69cceb89…`, matching the HEAD commit message. `c5_analysis.py`,
`c5_ledger.py` and `c5_mutations.py` likewise reproduce their committed artifacts byte-identically.
`c5_b0_audit.py` reproduces identically except for two fields: `head` (`5fad47ad` committed vs `8b2be7ab` now) and
`uncommitted` (8 vs 0). All seventeen B0 checks still pass at HEAD, so the staleness is cosmetic — but the round-2
reviewer explicitly directed "re-run it at the final HEAD before adjudication" and that was not done. Minor, and
recorded as part of the pattern in ruling (d).

*Re-implementation.* I wrote my own clause from the integral primitive `(b²−a²)/2` — importing nothing from
`c5_transport` — and recomputed, per cell: the weights, `P`, `Gamma_C5T`, the frozen penalty, the improvement
percentage, `M_needed` under both clauses and the gap fall. Every value matches the committed artifact to all
printed digits. `Gamma_C5T = −0.039425934 / +0.022641576 / +0.090222449 / +0.148146343`; improvements
1.211422 / 1.246019 / 1.279003 / 1.294912 %; gap falls 14.088 / 4.591 / 3.186 %.

*Attainment, independently.* For each cell I evaluated the witness `g(e) = g_hi − H_lo(e²−e0²)/2` over a 2001-point
exact-rational grid of the closed cell: the supremum equals the C5-T bound **exactly**, attained at `e = x_hi`.

---

## 6. Which cells, if any, close?

**Cell 306 closes; it already closed at the baseline. No previously open cell closes. Newly closed: none.**

| cell | `Gamma` frozen | `Gamma` C5-T | closes | status |
|---|---|---|---|---|
| 306 | −0.036197780 | −0.039425934 | yes | closed before C5; blocked from adoption by the inherited floor |
| 307 | +0.026354631 | +0.022641576 | no | open |
| 308 | +0.094564145 | +0.090222449 | no | open |
| 309 | +0.153019689 | +0.148146343 | no | open |

**I additionally tested what C5 did not: whether C5-T unblocks cell 306's adoption.** The inherited K5 tail adoption
floor (set prospectively by the C2 adjudicator, inherited verbatim by C3) requires either a supply independent of the
Arb/FLINT `taboo_certify` surface, or `Gamma < 0` under a ×1.25 inflation of every atom constant. Under C5-T with all
three atom constants inflated by 1.25 — a real evaluation, the TC-T cross-check live — cell 306 gives
`Gamma_C5T = +0.018069433 > 0`. It still fails. (Cell 305, already adopted, survives at −0.043637040.) **C5-T
licenses no adoption anywhere.**

---

## 7. Which deterministic families, if any, are exhausted?

**Exactly one: the K5-B midpoint-to-cell transport family** — every bound on `max_{e ∈ cell} g(e)` derivable from
exactly (i) an upper bound `g_hi` on `g(e0)` and (ii) a whole-cell enclosure `H_lo ≤ R'' ≤ H_hi`, on a cell lying in
`e > 0`. Nothing else in C5 is exhausted, and nothing else is claimed to be.

---

## 8. What exact scope does each exhaustion result have?

The only exhaustion result must be stated as:

> Relative to the two certified inputs `g_hi` (the sealed adopted K1 record at the cell midpoint) and the sealed-∩-TC-T
> whole-cell enclosure `[H_lo, H_hi]` of `R''`, on CUSUM cells 306, 307, 308 and 309 at `m = 5`, each of which lies
> strictly in `e > 0`: no bound on `max_{e ∈ cell} g(e)` using only those two inputs is smaller than theorem C5-T's,
> because C5-T's bound is attained by an admissible member of the input set (`R'' ≡ H_lo` constant, `g(e0) = g_hi`).
> This exhausts the **transport**, not the cell. It says nothing about improving `g_hi`, nothing about improving the
> `R''` enclosure, and nothing about a transport consuming a third certified input. It is not deterministic
> exhaustion of cell 309, of the tail, or of K5, and it has no R-stage consequence.

Two scope limits the campaign's own three-item list omits and which a successor must carry:

* **The witness is an arbitrary absolutely-continuous function consistent with the two inputs, not a genuine
  resolvent-type `R`.** That is the correct notion for "derivable from exactly these two inputs" — a valid bound must
  hold for every consistent function — but the family's exhaustion is therefore over a *relaxation* of the true
  problem. A bound exploiting analytic structure of the real `R` is outside the family and is not excluded.
* **`x_lo > 0`.** The result does not apply at cell 0 of either detector.

---

## 9. What deterministic mechanisms remain unexcluded?

**Almost all of them.** From C5's own ledger, of fourteen routes only **two** are refuted on mathematics at every
still-open cell, and both of those carry **no kill gate** — they are unmachine-checkable arguments:

* **D2** (sign-awareness alone) — I proved the identity myself: for `H_lo ≤ H_hi`,
  `max(|H_lo|,|H_hi|) ≡ max((H_hi)⁺, (−H_lo)⁺)` in all three sign cases. Genuinely refuted.
* **A4** (reuse existing certified order-3 evidence) — the one real probe is at cell 0 with drift ≈ 0, the tail is at
  `e ∈ [1.70, 2.09]`, and no certified transport across that range exists. The argument is sound, but note that it is
  an *absence-of-a-transport* claim, i.e. structurally a DATA/corpus fact, not the "oracle closes no cell" fact that
  the ledger's own definition of `MATH` names. A4 is `MATH` by declaration, not by the ledger's definition.

Everything else is live: **A1, A3, D4, E1** (DATA — inputs exist but are in the external 90 MB K1 record store, or
need a toolchain absent on this host), **A2, B1, B2, D3** (NEW_REAL — permission, not mathematics), **E2** (re-opened
live), and **A5 / A6 at cell 307** (refuted only at 308 and 309). Beyond the ledger, everything that improves `g_hi`,
everything that improves the `R''` enclosure, and every transport using a third certified input (a midpoint or
sub-cell enclosure of `R''`, any bound on `R'''`, joint `R`/`D` information) remain entirely unexcluded.

---

## 10. Is broader deterministic exhaustion established?

**No — and C5's own kill gates refute the idea.** The oracle `rho` halved (route B1, cover refinement) closes **all
three** remaining cells (`−0.130448 / −0.086647 / −0.050020`). The oracle `sup F/D/H → 0` (route A1) closes all three
as well (`−0.103207 / −0.049231 / −0.000347`). `f_G → 0` (A2) closes all three. Each is blocked by a permission or a
corpus boundary, not by mathematics. A programme in which three separate non-R-stage oracles each close every open
cell is not deterministically exhausted by any reading.

---

## 11. Is the prerequisite for DESIGNING a future real R-stage satisfied?

**No. I decide this on the evidence and the answer is not close.**

The R-stage premise, as C4's gate frames it, is that all deterministic routes required by it are exhausted. C5
exhausts one transport family worth 1.2–1.3% of a single inequality, on a channel that carries none of the deficit.
C5's own Phase 1 decomposition puts ~82% of the radius sum in `A0` multiplying the order-3 surrogate (58.8–61.6%) and
the order-4 envelope (19.9–23.1%) — neither of which C5 touches, both of which are DATA- or NEW_REAL-blocked rather
than refuted. Two of the three cheapest levers (operator certification of `A0`; tightening the candidate sup norms)
are blocked only by a missing toolchain and an un-checked-in record store. The largest lever, cover refinement, is a
new **K1 cover cell** — a new real address, but emphatically *not* the R-stage.

I note that C2's frozen gate justified its 20% threshold with the sentence that below it "the deterministic direction
is exhausted and the programme should route to the R stage rather than grind". C5 falls far below it. **That
justification does not carry here**, and a successor must not quote it as though it did: it was written as a rationale
for a convergence-rate threshold, at a time when the route inventory had not been built. C5's own inventory now shows
that the reason C5 tightened by only 1.3% is not that the deterministic direction is spent, but that C5 was permitted
to touch only the one channel that was already nearly tight. Below-threshold progress by a campaign forbidden to use
the three levers that would close the cells is evidence about the permissions, not about the mathematics.

---

## 12. If not, what exact blocker remains?

Per cell, against the C5-T clause (the figures are `S`-relative and exact, not first-order, because `M = |C_lo| + S`
exactly on all four cells):

* **306** — no mathematical blocker; it closes. The blocker is **governance**: the inherited ×1.25 adoption floor,
  which it still fails under C5-T at `+0.018069` (my check, §6).
* **307** — needs `S` to fall by ~10.07% (slightly less under C5-T). **Reachable**: route E1 (operator certification
  of `A0`) closes it, route A1 closes it, `sigma3 → 0` and `sigma4 → 0` each close it. Blocker is toolchain/corpus.
* **308** — needs ~31.54%. The oracle-perfect atom-constant supply misses by 0.003. Reachable only by combined
  surrogate/envelope improvement, or cover refinement.
* **309** — needs ~45.88%. The atom-constant direction is **spent** (`A1 = A2 = 0` at the diagnostic `Lambda_309`
  still gives `Gamma = +0.0468`). The only oracles that close it are `rho` halved (a **new K1 cover cell** — a new
  real address, governed, and not the R-stage) and the unattainable `sup F/D/H → 0`, which closes it by 0.00035, i.e.
  is itself effectively spent. **The exact blocker at 309 is: no lever whose inputs are in the committed corpus
  reaches 45.88% of `S`, and the only lever that comfortably does is K1 cover refinement.**

---

## 13. Did C5 rely on the disputed single Arb/FLINT surface in a way that invalidates robustness?

**It relies on it, it does not disclose that it relies on it, and that does not invalidate robustness.**

`phase_6/C5_SELECTED_MECHANISM.md` item 4 asserts: "it consumes no registry constant, no candidate polynomial, no Arb
certificate and no atom constant. It is independent of every surface C2, C3 and C4 argued about." That is true of the
**theorem** and false of the **numbers**. `c5_common.committed_inputs` loads `REGISTRY_C1.json` and `REGISTRY_C2.json`,
`c3_selector.build` forms the atom tuple from them, and at cell 309 the authoritative evaluation runs at
`A = (4.867216, 19.747332, 187.971026)`. That tuple drives the TC-T enclosure, hence `H_lo`, hence `P`, hence every
`Gamma_C5T` in the forecast — and the entire `c4_exclusion_fragility` block, which is parameterised by `A0`. The
inherited adoption floor's clause F1 exists precisely because this supply "rests on the Arb/FLINT `taboo_certify`
surface". C5 nowhere names that dependence.

**Why it does not invalidate robustness.** C5 adds no new dependence and runs no Arb/FLINT operation (python-flint is
absent on the host; the gate forbids it). Its exposure is exactly C2's, C3's and C4's, no more. And the one quantity
C5 actually claims — the tightening — *is* surface-independent: when the negative end of the enclosure dominates, the
improvement factor collapses to `(x_hi − rho/2)/x_hi`, pure cell geometry. I verified this at cell 309:
`(2.092283 − 0.027093)/2.092283 = 0.9870509` → 1.294912%, exactly the reported figure. So the **1.2–1.3% gain is
robust to the disputed surface; the absolute `Gamma` values and the fragility percentages are not.** The independence
claim must be narrowed to the mechanism and to the improvement factor. Condition 4.

---

## 14. Is any claimed independence genuine?

Partly, and the distinctions matter.

* **Genuine.** The theorem's independence of candidate polynomials, Arb certificates and atom constants, *as a
  mechanism*. My own re-implementation's independence of `c5_transport`. The mutation suite's part-(1) brute-force
  integration, which really does share no code with the transport module.
* **Not genuine, as worded.** "Independent of every surface C2, C3 and C4 argued about" — see §13.
* **Partial.** Part (1) of the mutation suite integrates independently but is fed `H_lo`, `H_hi` by
  `signed_enclosure`, so it is self-consistent with whatever enclosure it is handed. The round-2 reviewer established
  exactly this, and the campaign now records it plainly. My own reproduction shares the same upstream — unavoidably,
  since the frozen TC-T consumer *is* the authority for the enclosure.
* **Reviewer independence — unevidenced at round 3.** See ruling (d).

---

## 15. Is any coverage-map update justified?

**No.** No previously open cell closes, no cell is adopted, and the gate's `r6_rule` is explicit that a tightened
bound, a superseded clause and a family exhaustion are each insufficient. **Coverage map r5 remains authoritative and
immutable. No r6 may be created on the strength of this adjudication.** The `m = 5` open set is unchanged at
{306, 307, 308, 309}. K5 remains **PARTIAL**.

---

# RULINGS

## (a) The C4 fragility finding

**Every figure verified independently. All five reproduce to all printed digits.**

I re-implemented the fragility computation — my own clause, my own bisections, calling nothing in
`exclusion_fragility` — and obtained:

| currency | frozen clause | under C5-T | committed | my value |
|---|---|---|---|---|
| `Gamma` at the C4 certified floor `B = 3.297250282` | +0.004661130 | **+0.001708896** | 36.66270509% retained | **36.66270509%** |
| critical `A0` (`A1 = A2 = 0`) | 3.214236023 → **2.582706%** slack | 3.266415728 → **0.943987%** slack | ✓ | **exact match** |
| further penalty cut that voids it | — | **0.7593915%** | ✓ | **0.7593915%** |
| the four source knobs together | — | **0.6076077%** | ✓ | **0.6076077%** |
| candidate sup norms `sup{F,D,H}` | **5.5356915%** | **2.0561597%** | ✓ | **exact match** |

The first two rows are certified-grade: they scale no ingredient, so `knock` leaves the independent TC-T cross-check
**live** (I confirmed `knock({}) == FC.direct` exactly). Every `voiding_cut` row scales an ingredient and is therefore
DIAGNOSTIC, which C5 declares correctly in its `status` field. The claims in the adjudication instruction are all
three confirmed: a 0.759392% further penalty cut, a 0.6076% cut across the four source knobs, or a 2.0562%
tightening of the candidate sup norms would each void the exclusion outright.

**Is C5's handling correct and adequate?** Correct, and *nearly* adequate. C5 computes rather than quotes; it
discloses three figures tighter than the reviewer demanded; it labels the epistemic status of each row correctly; it
declines to absorb the finding and writes it into binding conditions; and it re-opens route E2 — the route its own v1
ledger had killed as having "zero verdict value" *in the same commit in which C5-T consumed 63% of that margin* —
while correctly refusing to execute E2 after freeze. That refusal is right: E2 is a new mechanism, the gate is frozen
on D1, and a margin-restoring mechanism designed after the margin was known to be needed would have the worst
possible provenance.

**One gap C5 did not close, and I closed it.** C4's exclusion is not a point claim at `A0 = B, A1 = A2 = 0`; it is a
universal claim over all `A0 ≥ B` and all `A1, A2 ≥ 0`, and it rests on a **monotonicity licence** (C4's own
Condition 4). C5 re-evaluates only the single point and infers survival. The licence must hold under the *new* clause,
and C5 never checks that it does. I checked: under C5-T at cell 309, `Gamma_C5T` is increasing in `A0` across
`B → 3B` (+0.001709 → +0.366408) and increasing in `A1` and `A2` from zero (`A1=1`: +0.004461; `A2=1`: +0.001736;
`(5,20)`: +0.016011; `(20,190)`: +0.061887). The licence survives. That is a numerical spot-check, not the structural
proof C4's Condition 4 demands, so it becomes Condition 5 below.

**Does C4's exclusion of cell 309 still stand, and on what scope sentence?**

**It stands — but not on C4's sentence, and C4's sentence must not be repeated.** C4's adjudicated verdict is scoped
verbatim to "the frozen measurement inputs and the frozen theorem TC-T / K5-B direct clause", and C5-T **replaces that
clause**. Adopting C5-T moves an adjudicated result outside the scope under which it was adjudicated, even though the
result survives. The honest restatement, which I hereby make binding, is:

> Against the frozen measurement inputs and the **C5-T exact-weight transport** of the K5-B direct clause, no
> atom-constant supply whose `A0` is a valid uniform order-0 bound on the closed cell can close CUSUM cell **309** at
> `m = 5`, for any `A1, A2 ≥ 0`. The margin is `Gamma = +0.001709` at the certified floor `B = 3.297250282`, i.e.
> **0.944% of critical `A0`**, not the 2.583% C4 published. A further 0.759% reduction of the transport penalty, a
> 0.608% reduction across the four source knobs, or a 2.056% tightening of the candidate sup norms would each void
> it. This removes one route from one cell. It is not a statement that cell 309 is unclosable, it is not exhaustion
> of the deterministic direction, and it has no R-stage consequence.

**And the direction of the effect must be stated plainly, because it is easy to get backwards.** C4's exclusion
*leans on the looseness of the transport*: a larger penalty makes `Gamma` larger, which makes "does not close" easier
to prove. So C5-T did not reveal that C4's margin was always 0.944% — it genuinely moved the goalposts, in the
direction that favours closure and disfavours exclusion. The real finding is therefore sharper and less comfortable
than C5 words it: **63% of C4's published exclusion margin was purchasable by a thirteen-line theorem with zero new
compute, and that margin is now thinner than several DATA-blocked routes could remove.** The exclusion is materially
more fragile than the programme believed, and that is true whether or not C5-T is adopted.

## (b) Is C5 worth adopting at all?

**Yes. Adopt C5-T as the authoritative transport, on the scope in Condition 3. I argue it rather than defer it.**

The case against is real and I take it seriously: C5-T closes nothing, buys 1.2–1.3%, forces the restatement of an
adjudicated verdict, cuts a predecessor's headline margin by 63%, and its own gate had to be frozen twenty seconds
after its numbers were known. On a pure cost-benefit reading of this campaign alone, it is a net negative.

But that reading is wrong, for three reasons.

**First, the fragility is a fact, not a consequence of adoption.** C5-T exists and is proved. Cell 309's exclusion
survives on 0.944% of critical `A0` *whether or not anyone adopts the clause* — declining to adopt would suppress
the disclosure, not the fact, and would leave 2.583% standing in the record as the margin of a published exclusion
when the true clause-relative figure available to any reader with a pencil is 0.944%. A programme that keeps a looser
inequality specifically because the looser one flatters a predecessor has stopped doing mathematics.

**Second, the gain is not where it looks.** 1.3% is trivial against gaps of 10%, 32% and 46%. But it is not trivial
against a 0.944% exclusion margin, and it will not be trivial against whatever the next campaign's margins are. The
programme's remaining path — as C5's own ledger makes clear — is the accumulation of several partial levers (A1, E1,
B1, E2), none of which closes 308 or 309 alone. A campaign line that will have to stack gains cannot afford to
compute every future "how much more do we need" figure against a bound it knows is not tight; every such figure would
be systematically overstated by ~1.3%, in the direction of making the remaining work look easier than it is.

**Third, the alternative is worse than it looks.** Keeping the frozen clause means every future campaign must
either re-derive C5-T privately to know the true margin, or work with a known-slack bound. Both are worse than one
restatement now. The restatement is cheap: it is three sentences and a table, and C5 has already written them.

**Adopt, with the scope hole fixed** (cell 0 excepted; §1), **with the independence claim narrowed** (§13), and with
C4's scope sentence restated as above. The clause-level record improves; the cell-level record does not change at all.

## (c) The exhaustion claim

**The attainment argument is valid. The family is honestly drawn but drawn narrowly and late. The scope limits are
adequate but incomplete. It is meaningfully different from "our implementation cannot do better" — and also
meaningfully less than it sounds.**

*Valid.* The gate demands a constructive attainment argument and forbids "our implementation cannot do better". C5
supplies a witness: `R'' ≡ H_lo` constant with `g(e0) = g_hi`. That pair is admissible (a constant function lies
inside the certified enclosure; a quadratic `R` with any prescribed `R(e0)`, `R'(e0)` realises it and `g(e0) = g_hi`
is the certified upper end). With `R''` constant the transport integral is exact, so at `e = x_hi` the function value
equals the bound. I verified equality *exactly in rationals* at all four cells, and the supremum over a 2001-point
grid of the closed cell equals the bound with zero gap. Any valid bound from those two inputs must hold for this
function, so none can be smaller. That is a genuine minimax-optimality statement, not an implementation limit.

*Honestly drawn, but narrow and late.* The family is defined by the gate as "exactly two certified inputs", and the
gate was frozen after the route search had established that the two-input transport was the only admissible route
left. So the family was drawn around the single move C5 had available. That is not dishonest — the definition is
precise, mechanical, and the `does_not_cover` list is explicit and correct — but it means the exhaustion verdict
carries almost no programmatic weight: the family it exhausts contains exactly one interesting member and
contributes ~1.3% of the deficit.

*Scope limits incomplete.* The three recorded limits are correct. Two must be added: the witness is an arbitrary
absolutely-continuous function consistent with the two inputs and not a genuine `R`, so the result is an exhaustion
over a relaxation (a bound exploiting real analytic structure is outside the family); and `x_lo > 0` excludes cell 0.

*The honest one-line summary:* "the transport family is exhausted" means "we have written the exactly optimal
inequality for the two numbers we are allowed to use, and it is worth 1.3%". It should never be compressed further.

## (d) Three rounds of review

**The repairs went to the cause, not the symptom. The self-reporting is honest to an unusual degree. And the
pattern is *confessed*, not *addressed*, and it recurred a fourth time in the very commit that recorded the lesson.**

*The repairs are causal, and I re-ran the reviewer's attacks myself rather than trusting the claim.*

* **Ledger guards (E7).** The round-2 holes were a hardcoded `backing = {"A5","A6"}` allowlist and a guard comparing
  two hand-written fields of the same dict. The repair iterates all `ROUTES` and **derives** `refuted_at_cells` and
  `oracle_closes_at_cells` from the sensitivity gate. I attacked it: a route lying about `refuted_at_cells` against a
  real gate is **REFUSED** ("declared [307,308,309] disagrees with gate 'rho halved (cover refinement)' (derived
  [])"); a `MATH` kill on a gate that closes cells is **REFUSED**; a `kill_gate` naming a knob absent from the
  evidence is **REFUSED**; a gate-free `MATH` kill with no `argument` is **REFUSED**. That is a real class fix.
  *Residual, and it is the load-bearing one:* a gate-free `MATH` kill carrying **any** `argument` string is accepted
  (I fabricated route F1 and the producer accepted it, emitting `refuted_on_mathematics = ['A4','D2','F1']`). This is
  unavoidable — an argument cannot be machine-checked — and it is disclosed via `refuted_without_a_kill_gate` and
  `headline_caveat`. But it means the corrected headline "two routes refuted on mathematics" rests **entirely** on two
  unmachine-checkable arguments, one of which (A4) is structurally a corpus claim rather than a mathematical one.
  Separately, `headline_caveat` is a hardcoded string naming "A4 and D2"; I mutated A4 to DATA and the headline
  correctly became `['D2']` while the caveat still named both. Condition 7.
* **Sign-blindness (E6).** The diagnosis is exact and the fix is at the cause: `signed_enclosure` was the one input
  the forecast took on trust, negate-and-swap preserved `max(|H_lo|,|H_hi|)` and so was invisible to the
  `Gamma_frozen` cross-check, to part (1) and to the inverted-interval guard. `checked_enclosure` now re-derives the
  signed endpoints from the sealed interval and the frozen consumer's own signed output and refuses on disagreement;
  M14 exercises it and is recorded `DETECTED_BY_GUARD` with a 2.6238% understatement. Verified in the committed
  artifact.
* **`invisible_on_real_cells`.** M12 and M13 now record `true`, computed with the mutation live on the real cells,
  correcting the round-2 finding that the field was `false` by construction. Verified.
* **The withdrawn phrase.** I grepped the whole namespace for "provably useless": it survives only inside sentences
  that explicitly withdraw it (`phase_3` lines 55 and 67, the erratum, the review). E1's `refuted_at_cells` is now
  `refuted_at_cells_diagnostic_only`. The E7 repair landed.

*The self-reporting is honest.* E6 states plainly that the shipped code was always correct and that what failed was
the assurance claim. E7 states that its own previous paragraph was wrong. The erratum records five further defects in
the campaign's own frozen gate and refuses to amend it. The fragility block discloses figures tighter than the
reviewer demanded. The ledger re-opens a route whose kill would have protected the campaign's predecessor. I found
nothing in C5 that overstates a result in the campaign's favour, and I looked hard.

*But the pattern is not addressed.* E7 records the third occurrence and states the lesson — "grep for the withdrawn
string across the namespace before writing that a withdrawal landed" — as a *note to the author*. There is no
mechanical check. And in the same commit that records the lesson, **the pattern recurred a fourth time, at the
governance layer**:

> The HEAD commit message asserts "**pre-forecast review READY at round 3**" and "Three rounds of fresh-context
> review … the reviewer's terminating condition met … It re-ran its own attacks and none survived."
> **No round-3 review artifact exists in the tree.** `review/REVIEW_C5_PREFORECAST.md` is headed "ROUND 2", was last
> modified at `e667cdc5`, records two blocking FAILs, and ends `HANDOVER: NOT_READY`. `git log -- review/` confirms
> HEAD did not touch it. The gate requires "0 blocking FAIL required" before the forecast is evaluated, and states
> "file existence is not completion; no reviewer or adjudicator output may be consumed before its explicit handover".
> **The forecast was produced and committed against a clearance that is not in committed evidence.**

Two further, smaller instances in the same family: the B0 audit was not re-run at the final HEAD as the round-2
reviewer directed (it records `5fad47ad`, two commits stale), and `README.md` advertises
`evidence/adjudication/C5_ADJUDICATION.md`, which does not exist — the same hygiene defect C4's Condition 11 recorded
about C4's own README and told the line not to inherit.

*How much does the missing round-3 report cost?* Less than it might, because the committed round-2 report states an
explicit, pre-registered **terminating condition** ("re-derive the sign-bearing input, add M14, fix
`invisible_on_real_cells` … I will not ask for a fourth round on mutant-hunting grounds") plus three must-land items.
I verified all three must-land items and both terminating-condition items landed before the forecast artifact. So the
*judgement* is not missing; the *record* of it is. That is why this is a scope limitation and a binding condition
rather than a rejection — but it is the fourth consecutive instance, and confession has now demonstrably failed as a
control. Condition 6 replaces it with a mechanical one.

## (e) Does anything in C5 license adopting a cell, changing a coverage map, reporting K5 closed, or authorizing the R-stage?

**No, on all four, and I checked each independently rather than reading the gate back.**

* **Adopting a cell.** No previously open cell closes. The one cell that closes, 306, closed before C5 and **still
  fails** the inherited ×1.25 adoption floor under C5-T at `+0.018069433` — my own evaluation, cross-check live
  (§6). Nothing in C5 licenses an adoption.
* **Changing a coverage map.** The adopted set is empty, so by the gate's `r6_rule` and by C4's Condition 8, r5
  remains authoritative and immutable. No r6.
* **Reporting K5 closed.** The `m = 5` open set is unchanged at {306, 307, 308, 309}. K5 is **PARTIAL**. A family
  exhaustion may never be restated as exhaustion of a cell, of the tail, or of K5.
* **Authorizing the R-stage.** Three separate non-R-stage oracles (B1, A1, A2) each close every remaining open cell;
  the deterministic direction is manifestly not exhausted (§10, §11). The guard stays `REAL_SCIENTIFIC_COMPUTE =
  DENY` and `NEW_REAL_SCIENTIFIC_ADDRESSES = 0`. C5 evaluated zero new real scientific addresses, ran zero kernel
  evaluations and zero operator certifications, and contacted no compute host; the two read-only `git ls-remote`
  calls in the B0 audit are to the code host and are correctly declared.

---

# VERDICT

**ACCEPTED_WITH_SCOPE_LIMITATION**

Theorem C5-T is correct — I checked the proof line by line, re-derived the weights from the integral primitive, and
confirmed the bound is attained exactly. Every committed artifact reproduces byte-identically from its producer, and
every load-bearing number reproduces from an independent re-implementation that imports none of the campaign's
transport code. The gate was frozen before the forecast and is not fitted, its post-hoc status is fully disclosed,
five of its own defects are recorded in an erratum that correctly refuses to amend it, and the campaign's
self-reporting is honest to a degree I did not find a counterexample to. The C4 fragility disclosure is the most
valuable thing in the campaign and I verified all five of its currencies independently.

The scope limitation is fourfold: **(i)** C5-T's premise `x_lo > 0` fails at cell 0 of both detectors, so C5-T is not
a blanket replacement of the K5-B direct clause and the campaign nowhere says so; **(ii)** the claimed independence
from the Arb/FLINT `taboo_certify` surface is true of the mechanism and of the 1.2–1.3% improvement factor, and false
of every `Gamma` value and every fragility percentage reported; **(iii)** the exhaustion result is of a two-input
transport family over a relaxation of the true problem, is worth ~1.3% of the deficit, and must never be compressed;
**(iv)** the forecast was produced against a round-3 clearance that is asserted in the commit record and absent from
committed evidence — the fourth instance in this line of a repair or state reported as landed that had not.

I record plainly, as the instruction invites: C5's scientific contribution is small, and its principal effect is to
show that a predecessor's adjudicated exclusion is far more fragile than that predecessor published. I nonetheless
find it worth adopting, because the fragility is a fact that exists independently of adoption, and because the
alternative is to keep certifying against an inequality the programme now knows is not tight.

## ADOPTED CELL SET

[]

## CONDITIONS

These bind any successor campaign in this line. They are in addition to C4's eleven conditions and C3's and C2's,
none of which is discharged here.

1. **C4's cell-309 scope sentence is superseded and must be restated.** Wherever the exclusion is stated, it must
   read as the block quoted in ruling (a): against the frozen measurement inputs and the **C5-T** transport, with
   `Gamma = +0.001709` at `B = 3.297250282`, **0.944%** of critical `A0`, and the three voiding thresholds
   (0.759392% penalty, 0.6076% across the four source knobs, 2.0562% on the candidate sup norms). **C4's 2.583%
   figure may not be quoted again without the C5-T figure beside it.** C4's Condition 5 (the margin exists only by
   virtue of the sup-over-closed-cell quantifier and the left-endpoint evaluation) continues to apply and must be
   carried with it.

2. **No successor may restate the cell-309 exclusion without either (a) re-deriving the fragility figures under its
   own clause, or (b) executing route E2 and certifying a sharper lower bound on `Lambda_309`.** This is a condition,
   not a ranking, and it inherits. E2 is the top-ranked future route and remains unexecuted, correctly.

3. **C5-T is adopted as the authoritative transport ONLY where its premise holds.** It supersedes `rho·x_hi·M` on
   every K1 cell with `x_lo > 0`; at **cell 0 of both the CUSUM and SR covers**, where `left = 0`, the premise fails,
   `c5_transport` refuses, and the **frozen clause remains authoritative**. Any artifact that describes C5-T as "the
   authoritative K5-B direct clause" without this exception is wrong and must be corrected. A successor must state,
   once, whether any other committed cover contains a cell with `x_lo ≤ 0`.

4. **Narrow the independence claim.** `phase_6/C5_SELECTED_MECHANISM.md` item 4 must be corrected: the mechanism and
   the improvement factor `(x_hi − rho/2)/x_hi` are independent of the registry constants and the Arb/FLINT
   `taboo_certify` surface; every reported `Gamma_C5T`, every `M_factor_needed` and the whole
   `c4_exclusion_fragility` block are **not** — they are computed at `A` drawn from `REGISTRY_C1` / `REGISTRY_C2`,
   the supply whose Arb certification has never been independently written (N9/N10, undischarged).

5. **Re-establish the monotonicity licence under the new clause, structurally.** C4's exclusion is universal over
   `A0 ≥ B` and `A1, A2 ≥ 0` and depends on monotonicity of `Gamma` in all three constants; C5 re-evaluated only the
   single point `(B, 0, 0)`. I verified the licence numerically under C5-T at cell 309 and it holds, but a numerical
   spot-check is not C4's Condition 4. A successor that relies on the exclusion must prove it for
   `P = max((−H_lo)⁺ w_R, (H_hi)⁺ w_L)`, and the machinery must **refuse**, not merely report, when it fails.

6. **Replace confession with a mechanical check — the pattern has now failed four times.** Before any artifact in
   this line is committed, a producer or script must (a) grep the whole namespace for every string listed in a
   machine-readable `withdrawn_strings` field and refuse if one appears outside a sentence that withdraws it, and
   (b) refuse to write a forecast unless the `review/` directory at the current HEAD contains a reviewer artifact
   whose explicit handover is a clearance. **The missing round-3 review report must be committed, or the HEAD commit
   message's claim of a round-3 READY clearance must be withdrawn in `ERRATUM_C5_GATE.md` as E8.** Until one of those
   happens, no artifact in this line may cite C5 as having passed a cleared pre-forecast review. The B0 audit must be
   re-run at the final HEAD, and `README.md`'s advertisement of a non-existent adjudication artifact corrected — the
   same defect C4's Condition 11 told this line not to inherit.

7. **Fix the two residual ledger honesty gaps.** (a) `headline_caveat` is a hardcoded string naming "A4 and D2"; I
   demonstrated it goes stale when the route set changes. Derive it from `refuted_without_a_kill_gate`. (b) Record
   that of the two routes carrying the "refuted on mathematics at every still-open cell" headline, **D2** is a proved
   identity (I verified it: `max(|H_lo|,|H_hi|) ≡ max((H_hi)⁺,(−H_lo)⁺)` in all sign cases) while **A4** is an
   absence-of-a-certified-transport claim — structurally a corpus fact, not the "oracle closes no cell" fact that the
   ledger's own definition of `MATH` names. The headline should be "one proved identity and one corpus argument", not
   "two routes refuted on mathematics".

8. **Carry the two missing exhaustion scope limits.** The attainment witness is an arbitrary absolutely-continuous
   function consistent with the two certified inputs, not a genuine resolvent-type `R`, so the family exhaustion is
   over a relaxation and does not exclude a bound exploiting the analytic structure of the real `R`. And the result
   does not apply where `x_lo ≤ 0`.

9. **r5 remains authoritative and immutable. No r6.** The `m = 5` open set is unchanged at {306, 307, 308, 309}.
   K5 is **PARTIAL**. The token `DETERMINISTIC_TRANSPORT_FAMILY_EXHAUSTED` may appear only with its full scope
   sentence (§8), and may never be shortened to any form of "deterministic exhaustion".

10. **The R-stage premise is not available and the guard stays DENY.** `REAL_SCIENTIFIC_COMPUTE = DENY`,
    `NEW_REAL_SCIENTIFIC_ADDRESSES = 0`. Three non-R-stage oracles (cover refinement, candidate sup-norm tightening,
    a real order-3 surrogate) each close every remaining open cell; the first two are blocked by a missing toolchain
    and an external record store, not by mathematics. No launch, authorization packet or countersignature is
    licensed by anything in C5. **C2's frozen-gate sentence that below-20% progress means the programme "should
    route to the R stage rather than grind" may not be quoted as licensing anything**: C5 fell below that threshold
    while forbidden to touch the three channels that carry 82% of the deficit, which is evidence about C5's
    permissions and not about the mathematics.

11. **The next deterministic successor should cost these, in this order:** (a) **E2** — a sharper *certified* lower
    bound on `Lambda_309`, the only lever that restores the margin C5-T consumed, and the only one that makes the
    cell-309 exclusion robust again; (b) **A1** — retrieve the K1 object candidate payloads from the external record
    store and tighten `sup{F, D, H}`, which closes 307 and 308 and is the dominant channel at 309; (c) **E1** —
    operator certification of `A0` on a host that has python-flint, which closes 307 and comes within 0.003 of 308;
    (d) **B1** — cover refinement at 309, the largest lever found, which closes all three and is a governed new K1
    address, **not** the R-stage. C4's Condition 7 route (a) — a residual-specific, non-norm-only order-0 bound —
    remains unquantified by anyone and should be costed alongside (b).

HANDOVER: ADJUDICATION COMPLETE
