# K5 Campaign B — the CUSUM m = 5 tail (K1 cells 305–309)

Additive namespace. Start: `p5y-postk1-frontier` at `3c1c6b9c`, after the theorem-TC lower-front successor
(m = 1, 2, 3 closed on 0–309; m = 5 open only on 305–309). Nothing outside this namespace is modified; AWS SR/PS1
untouched; `main` untouched. Guard **DENY** throughout — Campaign B computed **no new real scientific value** and
holds **no new real address**.

| phase | where | state |
|---|---|---|
| A. tail blocker audit | `phase_a/` | done: the blocker is the whole-cell curvature width; M must fall by 1.12× (305) … 2.67× (309) |
| gates (frozen before any forecast) | `config/FEASIBILITY_GATES_B.json` (`392101dd…`) | frozen, unmodified |
| B. route comparison | `phase_b/TAIL_ROUTE_COMPARISON.md` | selected T2, class USEFUL — **that class is refuted**, see below |
| B0. starting-state verification | `code/b0_state_verify.py`, `evidence/b0_r1/` | 8/8 gates PASS, incl. an independent byte-identical regeneration of coverage map r4 |
| B1. replay measurement of the tail inputs | `code/tct_inputs.py`, `evidence/measurement_r1/` | done, identity-gated 5/5; ≈ 1.87 CPU-h of replay, 0 new-real |
| theorem | `theorem/THEOREM_TCT.md` | theorem TC with Lemma G atom constants, a zero order-3 candidate and adopted Aux3 order-3 evidence |
| C. route scoring and execution decision | `code/tail_forecast_r2.py`, `evidence/forecast_r2/`, `phase_c/EXECUTION_DECISION.md` | **STOPPED** before freeze by the frozen `stop_rule`: every route is MARGINAL or INFEASIBLE |
| open notes N1 / N3 / N5 | `CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md` | dispositions recorded; N1's obligation reassigned, N3 answered, N5 retired for this route |
| independent review of the stop | `review/` | see `REVIEW_R1.md` |

## The finding

Route T2 (theorem TC with a real order-3 candidate at the five tail cells) was selected as USEFUL on a forecast that
is arithmetically wrong. Recomputed exactly at the frozen route comparison's **own** scenario inputs, and scored with
the frozen K5-B on the full adopted state, T2 closes **3/5** under NOMINAL and **1/5** under CONSERVATIVE — class
**MARGINAL**, not USEFUL. With the order-3 scale estimated from the campaign's own adopted Campaign-A records it closes
**0/5** — INFEASIBLE. The frozen `selection_rule` forbids executing below USEFUL, and the frozen `stop_rule` requires
stopping and writing a costed continuation plan when every route is MARGINAL or INFEASIBLE. That is what was done.

Two results stand:

- **cell 305 is closable with zero new real compute.** Theorem TC-T with Ĝ := 0 gives a fully certified whole-cell
  enclosure of magnitude 4.2031 against the 4.8916 the frozen K5-B needs, so Γ(305) goes from +0.041841 to
  −0.047477 and the cell passes via the direct test. Cells 306–309 reach 0.96×, 0.78×, 0.62×, 0.51× of what they need.
- **the remaining blocker is quantified exactly.** With Ĝ := 0 the four open cells close as soon as the atom constants
  fall uniformly by 1.053×, 1.335×, 1.731×, 2.195× — a reduction an operator-only certified registry extension to the
  tail (theorem AD Lemma Dv′, which bought 2.6× at e = 0) is expected to deliver with **no new real address at all**.

K5 therefore stays **PARTIAL** with m = 5 open on [305, 309]; coverage map r4 (`a3bddd83…`) is untouched and no r5
exists. The continuation plan is `phase_c/EXECUTION_DECISION.md` §5.
