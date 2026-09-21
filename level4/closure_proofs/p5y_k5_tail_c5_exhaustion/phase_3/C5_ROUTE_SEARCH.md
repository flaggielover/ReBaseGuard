# Phases 3–5 — the route search, and why thirteen of fourteen routes are dead

Producer: `code/c5_ledger.py`. Evidence: `evidence/ledger/C5_ROUTE_LEDGER.json`. Kill gates:
`evidence/phase2/C5_SENSITIVITY.json`.

## Kill kinds — the distinction that matters

| kind | meaning | is the route refuted? |
|---|---|---|
| **MATH** | the oracle closes **no** still-open cell | **yes, outright** |
| **MATH_PARTIAL** | the oracle refutes the route at **some** still-open cells but not all | only at the named cells |
| **DATA** | the mathematics could deliver, but the inputs are not in the committed corpus | no — a live future route |
| **NEW_REAL** | would need a new scientific value at a previously unevaluated real address | no — forbidden here only |

**Kill kinds are cell-scoped, and this was got wrong first time.** v1 of the ledger recorded A5 and A6 as `MATH`
with `closure_possible: false` while its own kill gate showed both oracles **close cell 307**. The pre-forecast
review failed the phase on it. The producer now refuses any `MATH` kill whose oracle closes a cell, and
cross-checks each claimed refutation set against the gate it cites.

## The kill gates

Each row sets the named quantity to its oracle-perfect value and re-evaluates `Gamma` (DIAGNOSTIC: the
independent TC-T crosscheck cannot see a scaled ingredient, so it is aligned to the frozen path; the baseline and
`A1 = A2 = 0` rows scale nothing and run with the crosscheck live).

| oracle-perfect knock-out | 307 | 308 | 309 |
|---|---|---|---|
| baseline | +0.026355 | +0.094564 | +0.153020 |
| `f_G → 0` (perfect order-3 surrogate) | **closes** | **closes** | **closes** |
| `env4 → 0` | closes | +0.019908 | +0.064104 |
| `sigma3 → 0` | closes | +0.007722 | +0.055204 |
| `sigma4 → 0` | closes | +0.027307 | +0.072507 |
| `sigma3` and `sigma4 → 0` | closes | **closes** | **closes** |
| sup F/D/H halved | closes | +0.022667 | +0.076337 |
| sup F/D/H `→ 0` | closes | **closes** | **closes** (by 0.00035) |
| `A1 = A2 = 0` | closes | +0.039568 | +0.092812 |
| `rho` halved | **closes** | **closes** | **closes** |

## The ledger in one table

| id | route | status | kind | why |
|---|---|---|---|---|
| A1 | tighten the candidate sup norms `sup F/D/H` | KILLED | DATA | the K1 object candidates are **not in the repo** — `TCT_INPUTS_*.json` carries only their sup *values*; the payloads are in the external record store. The only committed Chebyshev payloads are the *operator* taboo/arl candidates, a different object. |
| A2 | a real order-3 candidate in place of the surrogate | KILLED | NEW_REAL | this is the R-stage. |
| A3 | exploit cancellation in the order-3 identity | KILLED | DATA | needs the candidates *and* kernel applications; python-flint is absent. |
| A4 | reuse existing certified order-3 evidence | KILLED | **MATH** | the one real probe is at cell 0, drift ≈ 0; the tail is at 1.70–2.09. No certified transport across that range exists. |
| A5 | tighten `sigma3` | KILLED | **MATH_PARTIAL** (refuted at 308, 309) | at 307 the oracle **closes**, so A5 is *not* refuted there; at 307 the binding reason is DATA — `sigma3` is already at the min of the pure tower and the adopted measurement, and no committed artifact offers a tighter one. |
| A6 | tighten `sigma4` | KILLED | **MATH_PARTIAL** (refuted at 308, 309) | at 307 the oracle **closes**, so not refuted there; at 307 the binding reason is NEW_REAL — it needs an order-4 measurement of the source. The order-3 measurement already propagates into the order-4 tower (99.5 against a pure 128.5). |
| B1 | refine the cover, smaller `rho` | KILLED | NEW_REAL | **the largest lever found** — halving `rho` closes all three. A new K1 cell is a new real address. |
| B2 | split the clause over sub-intervals of the cell | KILLED | NEW_REAL | `R` and `D` are certified **at e0 only**; transporting them to a sub-midpoint costs exactly what the split saves. |
| **D1** | **exact-weight sign-aware transport (C5-T)** | **SELECTED** | — | the only zero-new-real route whose inputs are all already certified. |
| D2 | sign-awareness alone | KILLED | **MATH** | `max(\|H_lo\|,\|H_hi\|)` ≡ `max((H_hi)⁺,(−H_lo)⁺)` identically; sign-awareness pays only against *different directional weights*, which is D1. |
| D3 | second-order transport of `g` | KILLED | NEW_REAL | its remainder needs `R'''` — the very quantity the programme lacks. Circular. |
| D4 | exploit `R`/`D` correlation in `g_hi` | KILLED | DATA | the two are sealed, independently certified intervals; no joint information is committed. |
| E1 | tighten `A0` by operator certification | KILLED | DATA | needs python-flint, absent. A live future route for 307 and 308 — and **provably useless for 309**. |
| **E2** | **a sharper CERTIFIED lower bound on `Lambda_309`** | **RE-OPENED, LIVE** | — | v1 killed this as "zero verdict value — a better floor only widens a margin that is already positive", **in the same commit in which C5-T consumed 63 % of that margin**. Doubly wrong: its cell-308 leg rested on C4's *uncertified* Monte-Carlo, which a MATH kill may not do, and its cell-309 leg is contradicted by C5's own result. Under C5-T the exclusion stands on **0.94 %** of critical-`A0` margin, and E2 is the only lever that restores it. C5 does not execute it — the gate is frozen on route D1 — and it is the **top** recommendation to the successor. |

## The honest shape of the result

Only **two** routes are refuted on mathematics at every still-open cell: A4 (existing order-3 evidence is at drift
≈ 0, the tail is at 1.70–2.09) and D2 (sign-awareness alone is identically zero). Two more are refuted only at
cells 308 and 309. Four are blocked on a corpus this campaign does not hold, four on a compute boundary it must
not cross, and one — E2 — is re-opened as live.

The single largest lever, cover refinement at cell 309, is NEW_REAL. The second, operator certification of `A0`,
is a DATA block that would close 307 and come within 0.003 of closing 308. The earlier claim that E1 is
"provably useless for 309" is **withdrawn**: it leaned on the C4 exclusion, which under C5-T retains only 0.94 %
of its critical-`A0` margin.

That leaves exactly one route with all its inputs already certified, and it is a transport refinement worth
1.2–1.3 %.
