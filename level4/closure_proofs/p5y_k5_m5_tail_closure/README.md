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
| B1. replay measurement of the tail inputs | `code/tct_inputs.py`, `code/tct_adopted_inputs.py`, `evidence/measurement_r1/` | done, producer identity gate identical 5/5; ≈ 1.87 CPU-h of replay, 0 new-real |
| theorem | `theorem/THEOREM_TCT.md` | theorem TC with Lemma G atom constants, a zero order-3 candidate and adopted Aux3 order-3 evidence |
| C. route scoring and execution decision | `code/tail_forecast_r2.py`, `evidence/forecast_r2/`, `phase_c/EXECUTION_DECISION.md` | **STOPPED** before freeze by the frozen `stop_rule`: every route is MARGINAL or INFEASIBLE |
| open notes N1 / N3 / N5 | `CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md` | dispositions recorded; N1's obligation reassigned, N3 answered, N5 retired for this route |
| independent review | `review/REVIEW_R1.md` | r1 PASS_WITH_NOTES (43 PASS / 6 INFO / 3 NOT_CHECKABLE_LOCALLY / 4 FAIL); repairs applied, see below |

## The finding

Route T2 (theorem TC with a real order-3 candidate at the five tail cells) was selected as USEFUL on a forecast that
is arithmetically wrong. Recomputed at the frozen route comparison's **own** stated inputs, and scored with the frozen
K5-B on the full adopted state, T2 closes **3/5** under NOMINAL and **0/5** under CONSERVATIVE; with every candidate
supremum measured it closes **4/5** and **1/5**. USEFUL needs NOMINAL = 5/5 or CONSERVATIVE ≥ 3/5, so no reading
reaches it, and with the order-3 scale taken from Campaign A's own adopted records T2 closes **0/5** — INFEASIBLE. The
frozen `selection_rule` forbids executing below USEFUL and the frozen `stop_rule` requires stopping and writing a
costed continuation plan when every route is MARGINAL or INFEASIBLE. That is what was done: no freeze, no
authorization, no new real compute.

Two results stand:

- **cell 305 is closable with zero new real addresses.** Theorem TC-T with Ĝ := 0 gives a certified whole-cell
  enclosure of magnitude 4.257155 against the 4.8916 the frozen K5-B needs, so Γ(305) goes from +0.041841 to
  −0.043752 and the cell passes via the direct test, margin 1.149×. Cells 306–309 reach 0.94×, 0.76×, 0.61×, 0.50×.
- **the remaining blocker is quantified exactly.** With Ĝ := 0 the four open cells close once the atom constants fall
  by 1.091×, 1.502×, 2.206×, 3.294× on A0 alone (1.071×, 1.362×, 1.771×, 2.253× uniformly) — a reduction an
  operator-only registry extension to the tail can pursue with **no new real address**, expected to clear 306–307
  securely and 308–309 only if the taboo constants are also favourable.

K5 therefore stays **PARTIAL** with m = 5 open on [305, 309]; coverage map r4 (`a3bddd83…`) is untouched and no r5
exists. The continuation plan is `phase_c/EXECUTION_DECISION.md` §5.

## Review r1 and the repairs it forced

The independent reviewer reproduced every published number from its own implementation and confirmed the stop
decision, but raised four FAILs, all repaired before publication:

- **N1** — premise (P3′) applied an adopted *midpoint* bound inside the order-4 recursion, which theorem TC (P3)
  needs uniformly on the cell. Repaired with two towers and a mean-value correction; the magnitudes moved from
  4.2031/4.0906/3.9692/3.9232/3.8719 to 4.2572/4.1517/4.0401/4.0051/3.9643 and cell 305 still closes.
- **N4** — T2 was scored on the unrefined tower while TCT0 had the refined one; (P3′) is route-independent. Every
  route now uses one premise supply, which moved T2_AUDIT_MEAS from 3/5 to 4/5 NOMINAL. The class is unchanged.
- **N14** — three published measured ranges and one growth-rate comparison were wrong; corrected.
- **N15** — the "two independent rule paths" shared the (P3′) functions, so their agreement was silent on N1. The
  second path now shares no function with the first.

Notes N2 (self-contained evidence), N3 (CONSERVATIVE scaling), N6, N7, N9, N10, N11 and N13 (the honest expectation
for the continuation) were also addressed.
