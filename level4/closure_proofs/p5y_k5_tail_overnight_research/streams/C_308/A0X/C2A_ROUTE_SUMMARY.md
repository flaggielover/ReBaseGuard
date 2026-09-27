# C2A_ROUTE_SUMMARY — cell 308 exclusion question (stream C2a, theory and protocol only)

**Work done tonight:** no computation at any drift, no code run, no ledger entries. There were 0 target evaluations
and 0 new quantities for cells 305-309. Everything below is a reading of committed files or a proof.

Details are in `EXCLUSION_308.md` (proposition, certificates, Theorem M, consistency, conclusion) and
`FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md` (DRAFT ONLY — NOT FROZEN — NOT AUTHORIZED FOR EXECUTION).

**S8 correction notice (2026-09-28).** The first version of this summary, and of both files above, did two things
that S8 forbids:
* it combined Theorem M with committed tail-cell values (the MC at e_lo, and the C3/C4/C5-T critical A0) to estimate
  the outcome of X308 ("expected false", "refutable");
* it used committed 306-309 values as validation evidence for Theorem M.

It also stated a cell-308 floor entailed from C7's 309 number next to A0*. All of these are withdrawn and marked
"[S8-corrected]" in place (§6 below lists them). The statements that remain compare committed numbers only with
committed numbers, or are structural.

## 1. Exclusion-theorem status

| item | status |
|---|---|
| **X308** := `Lambda_308 >= A0*`. Lambda_308 = sup over the cell of E_a[tau]; A0* = C5-T critical A0 at A1 = A2 = 0 (committed float 4.442851487961) | **UNDECIDED on certified evidence.** The committed certified bracket `3.512733596 <= Lambda_308 <= 5.218548599` strictly contains the committed A0*. **The outcome is not estimated** (S8) |
| quantifier | **sup**, not inf (Lemma SM(d) plus the uniform-in-e admissibility, F3). Proving X308 needs one drift. Refuting it is universal in e |
| classification | **BOUNDABLE now; DECIDABLE in principle** by one certified computation, in either direction; that is a single drift, e_lo, if Theorem M is accepted. **Route L and R4 cannot prove it** (their committed values are below the committed A0*). No committed ceiling excludes E2/E2c, R1 or R5. **Not undecidable** |
| value of settling it | zero closure leverage either way. If X308 is true, the result is exclusion only. If it is false, the result is an A0 < A0*, but closing would still need (A1, A2) reductions (C4 Condition 3). Under floor r2 a scalar-drift A0 is CLOSURE-ONLY |

## 2. Routes, states and gates

**M — Theorem M: E_a[tau](e) is even and nonincreasing in abs(e)** (V-mask + Anderson 1955 / Prekopa).
**State: THEORY_ONLY** (proved; pending review).

| gate | result |
|---|---|
| G1 | pass: it resolves recorded open obligations (P5 LIMITATIONS §3, C4's caveat) and holds at every drift |
| G2 | pass on paper; needs G6 |
| G3 | pass: atom start only; symmetric unimodal i.i.d. innovations; either alarm convention; not sup_x; not taboo tau_a or D_e |
| G4 | n/a (no code) |
| G5 | **not done** (theory-only by instruction). No target-cell values are used as evidence (S8) |
| G6 | **not done** |
| G7 | pass |
| G8 | pass, but it opens a cross-drift proxy channel (§c.9) |
| G9 | pass |
| G10 | pass: it collapses the refutation to one drift and zeroes C7's S4 lever |

**X308-proof — a certified lower bound above A0*** (as registered, `ROUTE_AUDIT_R1.md:450-459`).
**State: BLOCKED**, because any evaluation is in-band. Sub-routes **C4-L and C4-R4 are REFUTED** as proof routes:
their committed values are below the committed A0*.

| gate | result |
|---|---|
| G1 | pass |
| G2 | pass |
| G3 | pass |
| G4 | n/a |
| G5 | n/a |
| G6 | n/a |
| G7 | pass |
| G8 | fails tonight (in-band) |
| G9 | possible |
| G10 | fail: exclusion only, zero leverage |

**X308-refute — a certified upper bound at e_lo below A0*** (supersolution W >= 1 + K_{e_lo} W, C2b generator).
**State: THEORY_ONLY** (DRAFT protocol; not FREEZE_READY).

| gate | result |
|---|---|
| G1 | partial: the result is an A0, i.e. a Gamma input |
| G2 | pass: Lemma T induction + Theorem M; completeness shown |
| G3 | pass |
| G4 | not done (C2b in progress) |
| G5 | not done |
| G6 | not done |
| G7 | pass: designed before any evaluation |
| G8 | result-chasing risk MEDIUM (draft §9); forbidden tonight |
| G9 | draft only; needs P1-P5 |
| G10 | low |

Governance:
* X308 true → **exclusion-only**.
* The refutation's U used as a supply → **CLOSURE-ONLY** under floor r2 (F16: "A scalar drift ... never qualifies";
  F1′ two-implementation rule).

## 3. Negative and corrective results (preserved)

1. **Route L and R4 cannot prove X308.** Their committed values over the cell are below the committed A0*. This is a
   committed-vs-committed comparison, independent of any MC.
2. **The E2/E2c (C7) committed family ceiling does not exclude it as a proof route.** The ceiling is 4.679910340 at
   e = 19839101/10000000 = e_hi(308), above the committed A0*.
3. **C7's lever S4 ("gap between sup over the cell and the value at e_lo") is identically zero** for every cell with
   e_lo >= 0, by Theorem M. This is structural: no number is attached.
4. **Wording issue in ADJUDICATION_C8.md:382.** "R3 closes 307 and 308" under perfect information compares A0* with
   the certified *floor*. For 308 the claim is conditional on not-X308, which is uncertified. For 307 it is certified
   independently (`C4_TARGET_RECONSTRUCTION.md:75`).
5. **"No certified upper bound on Lambda_308 exists"** (`ROUTE_AUDIT_R1.md:281`) holds only as "none below the
   thresholds". The certified A0s 5.218548599 and 6.174137364 are certified upper bounds.
6. **[S8-corrected]** The "reading-level entailment" of a cell-308 floor from C7's 309 number is **withdrawn**.

## 4. Quarantine-risk observations

* **Theorem M transports one-sided bounds between drifts.**
  * An upper bound at any e' <= e_lo(308), or a lower bound at any e'' >= e_lo(308), bounds Lambda_308.
  * Combining it with in-band values, with validation-drift values, or with committed tail-cell values is a
    forbidden target proxy (Q1/Q2, S8).
  * Recommendation to the campaign lead: Lambda values at validation drifts must never be compared with any 305-309
    number.
* **The first version of this stream did combine Theorem M with committed tail-cell values** (§6). That is now
  corrected. No transport to cell 308 from any computed value was ever made, because nothing was computed.
* **The float proposal at e_lo is itself a target estimate.** In any future protocol it must exist only after the
  marker (draft §4).

## 5. Recommended next action for 308's exclusion question

1. **A fresh-context independent review of Theorem M.** It is cross-cutting: it gives the atom version of P5's open
   claim `sup_e E[tau|e] = E[tau|0]`, discharges C4's caveat, and turns a future uniform-in-e Abar/A0 certification
   into a one-drift problem, subject to a floor extension.
2. **Non-target validation of Theorem M by the validation stream,** at e in {0, 1/4, 1/2, 1, 3} only. The planted
   negative control is a start (p0, 0), p0 > 0, where the order must fail near e = 0 (§c.8).
3. **DEFER settling X308,** because either outcome has zero closure leverage. The basis is leverage, not an expected
   outcome.
   * Do not spend compute on lower-bound routes at 308. Route L and R4 are rigorously incapable, and the others would
     need in-band evaluation.
   * If the user later wants the question settled, use the draft protocol's Variant P in a separately authorized
     campaign. It is best folded into an A0/Abar-supply campaign whose floor-extension decision is frozen before any
     evaluation.
4. **Record the wording corrections** of §3 items 4-5 in any successor text that cites C8 R3 or ROUTE_AUDIT_R1's 308
   disposition.

## 6. S8 corrections made (all preserved in place as "[S8-corrected]")

| file | location | what was removed |
|---|---|---|
| EXCLUSION_308.md | §a.2 | C5-T's consumed-margin share at 309, used in reasoning |
| EXCLUSION_308.md | §b.1 | Theorem M + MC + A0* → "no lower-bound route can prove X308" estimate; the entailed 308 floor next to A0* |
| EXCLUSION_308.md | §b.3 | the entailed floor |
| EXCLUSION_308.md | §c.10 | 306-309 MC / diagnostic ordering used as Theorem M evidence |
| EXCLUSION_308.md | §d | row D3 (same); the "entailed" label in D2; "MC supports C8's reading"; "MC puts Lambda_308 below A0*" |
| EXCLUSION_308.md | §e | "expected refutable / expected not provable"; the MC-based argument in item 2; C4 Condition 3's factor in item 5 |
| FREEZE_308_...DRAFT.md | §4 | the MC number inside the parameter prohibition |
| FREEZE_308_...DRAFT.md | §9 | the MC-via-Theorem-M location statement; committed A1/A2 values and C8's A1 reduction figure |
| C2A_ROUTE_SUMMARY.md | §1-§5 | "expected false", "refutable", "expected not provable"; the entailment item |
