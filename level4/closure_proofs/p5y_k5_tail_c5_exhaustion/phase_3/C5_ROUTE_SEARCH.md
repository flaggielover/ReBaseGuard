# Phases 3–5 — the route search, and why thirteen of fourteen routes are dead

Producer: `code/c5_ledger.py`. Evidence: `evidence/ledger/C5_ROUTE_LEDGER.json`. Kill gates:
`evidence/phase2/C5_SENSITIVITY.json`.

## Kill kinds — the distinction that matters

| kind | meaning | is the route refuted? |
|---|---|---|
| **MATH** | oracle-perfect tightening of the route's target still does not close the cell | **yes** |
| **DATA** | the mathematics could deliver, but the inputs are not in the committed corpus | no — a live future route |
| **NEW_REAL** | would need a new scientific value at a previously unevaluated real address | no — forbidden here only |

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
| A5 | tighten `sigma3` | KILLED | **MATH** | already measurement-improved, and the oracle closes 307 only. |
| A6 | tighten `sigma4` | KILLED | **MATH** | oracle closes 307 only; the order-3 measurement already propagates into the order-4 tower (99.5 against a pure 128.5). |
| B1 | refine the cover, smaller `rho` | KILLED | NEW_REAL | **the largest lever found** — halving `rho` closes all three. A new K1 cell is a new real address. |
| B2 | split the clause over sub-intervals of the cell | KILLED | NEW_REAL | `R` and `D` are certified **at e0 only**; transporting them to a sub-midpoint costs exactly what the split saves. |
| **D1** | **exact-weight sign-aware transport (C5-T)** | **SELECTED** | — | the only zero-new-real route whose inputs are all already certified. |
| D2 | sign-awareness alone | KILLED | **MATH** | `max(\|H_lo\|,\|H_hi\|)` ≡ `max((H_hi)⁺,(−H_lo)⁺)` identically; sign-awareness pays only against *different directional weights*, which is D1. |
| D3 | second-order transport of `g` | KILLED | NEW_REAL | its remainder needs `R'''` — the very quantity the programme lacks. Circular. |
| D4 | exploit `R`/`D` correlation in `g_hi` | KILLED | DATA | the two are sealed, independently certified intervals; no joint information is committed. |
| E1 | tighten `A0` by operator certification | KILLED | DATA | needs python-flint, absent. A live future route for 307 and 308 — and **provably useless for 309**. |
| E2 | a sharper lower bound on `E_a[tau]` than C4's | KILLED | **MATH** | zero verdict value: 309 is already excluded, and 308 can never be excluded because the truth (4.311) is below the threshold (4.375229). |

## The honest shape of the result

Only **five** routes are refuted on mathematics. Four are blocked on a corpus this campaign does not hold, and
four on a compute boundary it must not cross. The single largest lever — cover refinement at cell 309 — is a
NEW_REAL route, and the second largest — operator certification of `A0` — is a DATA block that would close 307 and
come within 0.003 of closing 308.

That leaves exactly one route with all its inputs already certified, and it is a transport refinement worth
1.2–1.3 %.
