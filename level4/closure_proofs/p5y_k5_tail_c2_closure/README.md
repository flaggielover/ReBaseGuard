# K5 Campaign C2 — two-stage tail closure (CUSUM m = 5, cells 305–309)

Additive namespace. Start: `p5y-postk1-frontier` at `5289b6ce`. Nothing outside this namespace is modified; AWS
SR/PS1 untouched; `main` untouched.

C2 is the successor to two complete negative/partial feasibility campaigns, and it does not reopen either:

- **Campaign B** (`p5y_k5_m5_tail_closure`) stopped before freeze; route T2 invalidated; cell 305 soundly closed
  under repaired TC-T arithmetic and **not adopted**.
- **Campaign C1** (`p5y_k5_tail_operator_registry`) stopped before freeze at MARGINAL; the tail operator registry
  certified 5/5 but atom deflation bought only 1.10–1.13× on A0 and made A2 **worse** by 1.25–1.36×; cells 305 and
  306 closed and **not adopted**.

C2 runs two stages, and the second is reachable only through its own separately frozen sub-gate:

| stage | what it does | new real addresses |
|---|---|---|
| **D** — deterministic | finer taboo partition, per-sub-block denominator certification, and a *pre-registered* componentwise minimum over every valid certified supply | 0 |
| **R** — real order-3 | the minimum address set the D-stage residual analysis supports, only if D leaves cells open and the residual is order-3-attributable | forecast-gated, capped |

## The governance lesson C2 encodes

Each predecessor lost its campaign to a gate defect, and C2's gate is written against both:

- Campaign C1 measured progress as a fraction of the raw residual requirement. C2 measures it as a fraction of the
  **gap above 1**, because a cell closes when its requirement reaches 1 — that is the scale-correct quantity, and
  C1's 10 % threshold is deliberately **not** inherited.
- Campaign C1 declined the componentwise minimum of two valid certified supplies because its gate specified one
  supply. C2 **pre-registers the minimum**, which is the legitimate way to obtain it.
- Both campaigns computed a sound closure of cell 305 and adopted nothing, because each gate demanded more than one
  cell. C2's `D_PARTIAL` rule states in advance that a non-empty closed subset is **always** adopted when the
  adjudication chain completes: an adopted cell is permanent progress that costs no new real compute.

| phase | where | state |
|---|---|---|
| B0. read-only verification | `code/c2_b0_verify.py`, `evidence/phase_b0/` | 7/7 PASS |
| gate (frozen **before** any forecast) | `config/FEASIBILITY_GATES_C2.json` | frozen at this commit |
| D1–D5 | `phase_d/` | — |
| R-stage design | `phase_r/` | — |

K5 remains **PARTIAL** (m = 5 open on 305–309); coverage map r4 (`a3bddd83…`) is authoritative and no r5 exists.
