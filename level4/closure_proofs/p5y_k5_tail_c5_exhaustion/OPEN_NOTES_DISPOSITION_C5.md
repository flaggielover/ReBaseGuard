# Disposition of the C5 review and adjudication conditions

Pre-forecast review: `review/REVIEW_C5_PREFORECAST_R2.md` (NOT_READY) and `..._R3.md`
(`READY_TO_FORECAST_WITH_NOTES`), three rounds, two blocking failures, both repaired at source.
Adjudication: `evidence/adjudication/C5_ADJUDICATION.md` — **ACCEPTED_WITH_SCOPE_LIMITATION**, adopted set **[]**,
eleven conditions.

Every load-bearing figure in the adjudication was reproduced here before anything was acted on: the cell-0 domain
hole (exactly **2 of 642** cover cells, both with `left = 0`, both refused by `c5_transport`), the missing
round-3 review artifact, and the five fragility currencies.

## The two blocking review failures

| # | finding | disposition |
|---|---|---|
| R1-C | the ledger recorded A5 and A6 as `MATH` with `closure_possible: false` while its own kill gate **closes cell 307** | **Fixed at source.** Kill kinds cell-scoped (`MATH_PARTIAL` + `refuted_at_cells`); the producer refuses any `MATH` kill whose oracle closes a cell; refutation sets are **derived from the gate**, not compared against hand-written copies; headline corrected from five routes to **two**. Route **E2 re-opened** — v1 killed it as "zero verdict value" in the same commit in which C5-T consumed 63 % of that margin, and its 308 leg rested on uncertified Monte-Carlo. |
| R1-I / R2-I | the mutation suite never tested the **leftward** weight; then, after repair, **negate-and-swap** on `signed_enclosure` survived every check | **Fixed at source, twice, at the cause.** The leftward branch is now exercised on a manufactured cell the producer refuses unless it genuinely binds (M11–M13). The sign-bearing input is **re-derived** in the forecast (`checked_enclosure`) rather than trusted, and M14 exercises it; it understated the penalty by **2.6238 %**, more than double C5-T's whole gain. 14 mutants, 0 undetected. |

## The eleven adjudication conditions

| # | condition | disposition |
|---|---|---|
| 1 | C4's cell-309 scope sentence is superseded and must be restated with the C5-T figures | **Binding; adopted verbatim.** The restatement is in `evidence/forecast/C5_FORECAST.json` under `c4_exclusion_fragility.C4_scope_sentence_must_be_restated`, and the final report uses it. C4's 2.583 % may not be quoted again without the 0.944 % beside it. |
| 2 | no successor may restate the exclusion without re-deriving the fragility or executing E2 | **Binding.** Already carried in the forecast's `binding_conditions_on_any_successor`. |
| 3 | C5-T is authoritative **only where `x_lo > 0`** | **Done in documents.** `phase_6/C5_SELECTED_MECHANISM.md` now records the exception. Verified independently: exactly **2 of 642** cells fail it — cell 0 of the CUSUM cover and cell 0 of the SR cover — and `c5_transport.weights` refuses both. Cell 0 is the cell the one real order-3 probe closed, so this is concrete. |
| 4 | narrow the independence claim | **Done in documents.** The mechanism and the improvement factor `(x_hi − rho/2)/x_hi` are surface-independent; every `Gamma_C5T`, `M_factor_needed` and the whole fragility block are **not** — they run at `A` drawn from `REGISTRY_C1`/`C2`, whose Arb certification has never been independently written (N9/N10, undischarged). |
| 5 | re-establish the monotonicity licence **structurally** under the new clause | **Binding on the successor, not retrofitted.** The adjudicator verified it numerically at cell 309 under C5-T and it holds; a numerical spot-check is not C4's Condition 4. Carried as **C5-N1**. |
| 6 | replace confession with a mechanical check; commit the round-3 report or withdraw the claim | **Done, both halves.** The round-3 report is committed (`..._R3.md`), the round-2 report retained beside it, and `ERRATUM_C5_GATE.md` **E8** records the failure in full. `code/c5_selfcheck.py` refuses on a live withdrawn string, on a forecast without a clearing review in the tree, and on a README advertising a path that does not exist. It failed on its first run, catching a stale README this very repair had introduced. B0 re-run at HEAD. |
| 7 | derive `headline_caveat`; distinguish D2's proved identity from A4's corpus argument | **Carried, not regenerated — see E9.** The edit was made and reverted so the adjudicated ledger bytes stand. The substance: of the two routes carrying the corrected headline, **D2 is a proved identity** (`max(\|H_lo\|,\|H_hi\|) ≡ max((H_hi)⁺,(−H_lo)⁺)` in all sign cases) and **A4 is an absence-of-a-certified-transport claim** — structurally a corpus fact, not the "oracle closes no cell" fact the ledger's own `MATH` definition names. The honest headline is **"one proved identity and one corpus argument"**. |
| 8 | carry the two missing exhaustion scope limits | **Carried, not regenerated — see E9.** (i) The attainment witness is an arbitrary absolutely-continuous function consistent with the two inputs, **not a genuine resolvent-type `R`**, so the family is exhausted over a **relaxation**; a bound exploiting the analytic structure of the real `R` is outside it and is not excluded. (ii) The result does not apply where `x_lo ≤ 0`. |
| 9 | r5 authoritative, no r6, K5 PARTIAL, the token never shortened | **Binding, already satisfied.** Adopted set empty, no r6 exists, m = 5 open set unchanged at {306, 307, 308, 309}. |
| 10 | the R-stage premise is not available; guard stays DENY; C2's "route to the R stage" sentence may not be quoted as licensing anything | **Binding.** C5 asserted no R-stage consequence at any point. The adjudicator's reasoning is recorded as **C5-N2**. |
| 11 | the next successor should cost E2, A1, E1, B1 in that order | **Recorded as C5-N3**, superseding C5's own ranking. |

## Notes carried to a successor

* **C5-N1.** The monotonicity licence under C5-T is verified numerically, not structurally. `Gamma_C5T` must be
  proved nondecreasing in `A0`, `A1`, `A2` for `P = max((−H_lo)⁺ w_R, (H_hi)⁺ w_L)`, and the machinery must
  **refuse**, not report, when it fails.
* **C5-N2.** Deterministic exhaustion is **not** established and is not close. Three separate non-R-stage oracles
  — cover refinement (B1), candidate sup-norm tightening (A1), a real order-3 surrogate (A2) — each close **all
  three** remaining open cells. Two of them are blocked by a missing toolchain and an un-checked-in record store,
  not by mathematics. C2's frozen-gate sentence that below-threshold progress means the programme "should route
  to the R stage rather than grind" **may not be quoted as licensing anything here**: C5 fell below that
  threshold while forbidden to touch the three channels carrying 82 % of the deficit. That is evidence about
  C5's permissions, not about the mathematics.
* **C5-N3.** Next deterministic successor, in the adjudicator's order: **(a) E2** — a sharper *certified* lower
  bound on `Lambda_309`, the only lever that restores the margin C5-T consumed and the only one that makes the
  cell-309 exclusion robust again; **(b) A1** — retrieve the K1 object candidate payloads from the external
  record store and tighten `sup{F, D, H}`, the dominant channel; **(c) E1** — operator certification of `A0` on a
  host with python-flint; **(d) B1** — cover refinement at 309, the largest lever, a governed new K1 address and
  **not** the R-stage. C4's Condition 7 route (a), a residual-specific non-norm-only order-0 bound, remains
  unquantified by anyone.
* **C5-N4.** The B0 audit cannot record the commit that contains it — a fixpoint, not a defect. It is re-run at
  each HEAD and its assertions were independently confirmed at the final HEAD by the adjudicator.
