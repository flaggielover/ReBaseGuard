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
| independent review | `review/REVIEW_R1.md`, `review/REVIEW_R2.md` | r1 PASS_WITH_NOTES (43/6/3/4); r2 PASS_WITH_NOTES (60/5/2/4) — all four r1 FAILs REPAIRED, four prose FAILs raised and corrected |

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

## The two independent reviews and the repairs they forced

**Round 1** reproduced every published number from its own implementation and confirmed the stop decision, but raised
four FAILs, all repaired:

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

**Round 2** checked the repairs themselves. It wrote its own exact-rational implementation of theorem TC-T from the
theorem text *before* opening any namespace code, drove it from committed files alone, and reproduced **all 20
published exact-rational strings as exact `Fraction` equalities**, both atom-constant series, all five critical ratios
and the derived identity gate; 49 of 53 input perturbations move its output. It found **all four round-1 FAILs
REPAIRED** and the (P3′) r2 mathematics sound, and raised four further FAILs — every one of them prose, none moving a
headline number, a theorem step, the stop decision or cell 305's closure:

- **M1** — §4's radius decomposition was wrong in both directions: the order-3 residual term is the largest single
  term everywhere except r = 4 on cells 308–309, and the f_G share is 71.6–78.7 %, not "about two thirds". Replaced
  with the exact eight-term decomposition; the C1-before-C2 ordering now rests on §3, where it belongs.
- **M2** — the adopted registry's gain at e = 0 is 500.409 against 1232.836, i.e. **2.46×**, not 469.8 / 2.6×.
- **M3** — the pure-tower σ₄ at r = 4 is 345.10 at cell 309; 355 is cell 305's.
- **M4** — `THEOREM_TCT.md` §2 labelled the *closure* threshold (10.55–64.72) as the break-even between the two
  enclosures; the break-even is 44.6–53.5.

Its informational notes were acted on too: which half of (P3′) actually binds (M5), the `cells.json` index collision
across detectors that traps third-party reproducers (M6), the defensive-only order-4 clamp (M7), the single hinge the
T2 refutation turns on (M8), and re-*derivable* versus re-*runnable* (M9). Following M10, its review is committed on
its own, before this response to it.
