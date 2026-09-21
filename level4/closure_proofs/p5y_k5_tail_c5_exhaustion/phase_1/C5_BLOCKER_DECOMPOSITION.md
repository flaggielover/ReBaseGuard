# Phase 1 — where the closure deficit actually lives

Producer: `code/c5_analysis.py`. Evidence: `evidence/phase1/C5_DECOMPOSITION.json`. Every figure is a
deterministic re-evaluation of the frozen consumers on committed inputs: **CERTIFIED**, not diagnostic.

## 1. The clause, and what is improvable in it

    Gamma = g_hi + rho * x_hi * M,      g_hi = R.hi - e0 * D.lo,      closure iff Gamma < 0

`g(e) = R(e) - e R'(e)`, so `g'(e) = -e R''(e)`, and the clause transports the certified midpoint enclosure of `g`
to the cell edge using a whole-cell bound `M` on `|R''|`.

Three of the four ingredients are immovable for any deterministic successor:

| ingredient | source | improvable here? |
|---|---|---|
| `g_hi` | the sealed adopted K1 record (`R_interval`, `D_interval`, certified **at e0**) | no — sealed |
| `rho`, `x_hi` | the K1 cover ledger cell geometry | no — changing them is a new K1 cell |
| `M` | `min(M_R2, max abs of the TC-T whole-cell enclosure)` | **yes, this is the whole game** |
| the transport constant | the clause's own `rho * x_hi` | **yes — and this is what C5-T attacks** |

`M` is currently set by the TC-T enclosure, not by the sealed `M_R2`: at every open cell the TC-T bound (≈3.3) is
far tighter than the sealed interval (≈5.3), so the intersection is decided by TC-T.

## 2. What each open cell needs

| cell | `g_hi` | `M` used | `M` needed | factor needed | `Gamma` | radius sum `S` | `S` must fall by |
|---|---|---|---|---|---|---|---|
| 306 | −0.302674 | 3.438038 | 3.905056 | 0.880 | **−0.036198 closes** | 2.94 | — |
| 307 | −0.271639 | 3.374599 | 3.076148 | 1.097 | +0.026355 | 2.963991 | **10.07 %** |
| 308 | −0.244895 | 3.371647 | 2.432398 | 1.386 | +0.094564 | 2.978193 | **31.54 %** |
| 309 | −0.223326 | 3.319525 | 1.969828 | 1.685 | +0.153020 | 2.941558 | **45.88 %** |

`M = |centre| + S` where the centre comes from the `H_at_a` and `W2` enclosures and `S` is the radius sum. The
centre is small (≈0.38 at cell 309 against `S` ≈ 2.94), so **`S` is the target**.

## 3. The decomposition of `S` — the result that redirects the whole campaign

`S = (1/5) Σ_r rad_r` with `rad = A0·p2 + 2·A1·p1 + A2·p0` and
`p2 = f_H + rho·f_G + rho²·env4/2`.

| component | 307 | 308 | 309 |
|---|---|---|---|
| `A0 · p2` | 81.56 % | 81.66 % | 81.95 % |
| `2 A1 · p1` | 16.77 % | 16.73 % | 16.51 % |
| `A2 · p0` | 1.67 % | 1.61 % | 1.54 % |
| — of which `A0 · f_H` (the **measured** 2nd-order residual) | **0.11 %** | **0.10 %** | **0.09 %** |
| — of which `A0 · rho · f_G` (the **order-3 surrogate**) | **61.59 %** | **60.04 %** | **58.80 %** |
| — of which `A0 · rho² · env4/2` (the **order-4 envelope**) | 19.86 % | 21.52 % | 23.06 % |

**Roughly 82 % of the deficit is `A0` multiplying two quantities that are not measurements at all** — the zero-
candidate order-3 surrogate and the fourth-order envelope — while the residual that the K1 machinery actually
certifies contributes one part in a thousand. This is the quantitative form of the C4 adjudicator's finding that
the order-0 channel is not the dominant one, and it is sharper: the dominant channel is not `A0`'s *level* but
what `A0` is multiplied by.

`f_G = k₃·sup F + 3k₂·sup D + 3k₁·sup H + sigma3`, from the zero-candidate identity
`phi''' = S''' + 3K₁Ĥ + 3K₂D̂ + K₃F̂`. At `r ≥ 1`, `sigma3` is 42–48 % of it and the candidate sup norms are the
rest; `sigma3` is already measurement-improved (the frozen `sigma_source` takes the min of the pure tower and the
adopted measured `sup‖S_r'''‖`, which at r = 3, 4 is 5–20× below the tower).

## 4. Blocker classification

| cell | blocker | kind |
|---|---|---|
| 306 | none mathematically — it closes; adoption is blocked by the inherited C2 floor | **GOVERNANCE** |
| 307 | 10.07 % of `S`; reachable by `A0` alone at its floor, or by any of several surrogate routes | **CERTIFICATION** (the inputs exist; certifying them needs machinery absent here) |
| 308 | 31.54 % of `S`; the oracle-perfect atom-constant supply closes it by only 0.003 | **SCIENTIFIC + CERTIFICATION** |
| 309 | 45.88 % of `S`; the oracle-perfect atom-constant supply does **not** close it | **SCIENTIFIC** |

The last row restates C4's exclusion from the other side, and independently: at the diagnostic `Lambda_309`
with `A1 = A2 = 0`, `Gamma = +0.0468`, so the atom-constant direction is spent at 309 with about ten times the
margin C4's certificate could show.
