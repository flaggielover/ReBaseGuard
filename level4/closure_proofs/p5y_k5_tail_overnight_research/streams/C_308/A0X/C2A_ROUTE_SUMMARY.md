# C2A_ROUTE_SUMMARY — cell 308 exclusion question (stream C2a, theory and protocol only)

**Work done tonight:** no computation at any drift, no code run, no ledger entries. There were 0 target evaluations
and 0 new quantities for cells 305-309. Everything below is a reading of committed files or a proof.

Details are in `EXCLUSION_308.md` (proposition, certificates, Theorem M, consistency, conclusion) and
`FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md` (DRAFT ONLY — NOT FROZEN — NOT AUTHORIZED FOR EXECUTION).

## 1. Exclusion-theorem status

| item | status |
|---|---|
| **X308** := `Lambda_308 >= A0*`, with Lambda_308 = sup over the cell of E_a[tau] and A0* = C5-T critical A0 at A1 = A2 = 0 (committed float 4.442851487961) | **UNDECIDED on certified evidence.** The certified bracket `3.512733596 <= Lambda_308 <= 5.218548599` strictly contains A0*. **Expected false** on the uncertified 2e6-path MC, 4.30910 +- 0.00102 at e_lo |
| quantifier | **sup**, not inf (Lemma SM(d) plus the uniform-in-e admissibility, F3). Proving X308 needs one drift. Refuting it is universal in e |
| classification | **BOUNDABLE now; REFUTABLE in principle** (by one certified computation at e_lo, given Theorem M); **not provable** by any family whose ceiling is committed, and expected not provable by any family; **not undecidable** |
| value of settling it | zero closure leverage either way. If X308 is true, the result is exclusion only. If it is false, the refutation yields an A0 < A0*, but closing still needs (A1, A2) reductions (C4 Condition 3). Under floor r2 a scalar-drift A0 is CLOSURE-ONLY |

## 2. Routes, states and gates

| route | state | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 | G10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **M** — Theorem M: E_a[tau](e) is even and nonincreasing in abs(e) (V-mask + Anderson 1955 / Prekopa) | **THEORY_ONLY** (proved; pending review) | pass (resolves the recorded open obligations D3-adjacent / P5 §3 / C4 caveat; holds at every drift) | pass on paper; needs G6 | pass (atom start only; symmetric unimodal i.i.d. innovations; either alarm convention; not sup_x, not taboo tau_a or D_e) | n/a (no code) | **not done** (theory-only by instruction) | **not done** | pass | pass, but it opens a cross-drift proxy channel (§c.9) | pass | pass (collapses the refutation to one drift; zeroes C7's S4 lever) |
| **X308-proof** — a certified lower bound above A0* (as registered, `ROUTE_AUDIT_R1.md:450-459`) | **BLOCKED** (any evaluation is in-band); sub-routes **C4-L and C4-R4 REFUTED** as proof routes, rigorously (maxima 3.512733596 and 1.051130 < A0*) | pass | pass | pass | n/a | n/a | n/a | pass | fails tonight (in-band) | possible | fail: exclusion only, zero leverage, and expected false |
| **X308-refute** — a certified upper bound at e_lo below A0* (supersolution W >= 1 + K_{e_lo} W, C2b generator) | **THEORY_ONLY** (DRAFT protocol; not FREEZE_READY) | partial (the result is an A0, i.e. a Gamma input) | pass (Lemma T induction + Theorem M; completeness shown) | pass | not done (C2b in progress) | not done | not done | pass (designed before any evaluation) | result-chasing risk MEDIUM (see draft §9); forbidden tonight | draft only; needs P1-P5 | low |

Governance: X308 true → **exclusion-only**. The refutation's U used as a supply → **CLOSURE-ONLY** under floor r2
(F16: "A scalar drift ... never qualifies"; F1′ two-implementation rule).

## 3. Negative and corrective results (preserved)

1. **Route L and R4 cannot prove X308.** This is rigorous and independent of the MC. Their committed maxima over the
   cell are below A0*.
2. **The E2/E2c (C7) committed family ceiling does not exclude it as a proof route.** The ceiling is 4.679910340 at
   e = 19839101/10000000 = e_hi(308), which is above A0*. Only the (uncertified) truth caps it.
3. **C7's lever S4 ("gap between sup over the cell and the value at e_lo") is identically zero** for every cell with
   e_lo >= 0, by Theorem M. There is no headroom there.
4. **Wording issue in ADJUDICATION_C8.md:382.** "R3 closes 307 and 308" under perfect information compares A0* with
   the certified *floor*. For 308 the claim is conditional on not-X308, which is uncertified. For 307 it is certified
   independently (`C4_TARGET_RECONSTRUCTION.md:75`).
5. **"No certified upper bound on Lambda_308 exists"** (`ROUTE_AUDIT_R1.md:281`) holds only as "none below the
   thresholds". The certified A0s 5.218548599 and 6.174137364 are certified upper bounds.
6. **Reading-level entailment.** C7's committed E_a[tau](19839101/10000000) >= 3.586306094 is also a valid lower bound
   on Lambda_308, because that drift is e_hi(308). This involves no arithmetic, bears on nothing, and is adopted by
   nobody.

## 4. Quarantine-risk observations

* **Theorem M transports one-sided bounds between drifts.**
  * An upper bound at any e' <= e_lo(308), or a lower bound at any e'' >= e_lo(308), bounds Lambda_308.
  * Combining it with in-band values is a forbidden target proxy. So is combining it with validation-drift values
    (e <= 1 or e >= 3).
  * Recommendation to the campaign lead: Lambda values at validation drifts must never be compared with any 305-309
    threshold. **No such transport or comparison was made.**
* **The float proposal at e_lo is itself a target estimate.** In any future protocol it must exist only after the
  marker (draft §4).
* **Nothing computed.** No computation at any drift, no Gamma, no margin, no critical value. The only numbers are
  quoted committed values and orderings between them.

## 5. Recommended next action for 308's exclusion question

1. **A fresh-context independent review of Theorem M.** It is cross-cutting: it gives the atom version of P5's open
   claim `sup_e E[tau|e] = E[tau|0]`, discharges C4's caveat, and turns any future Abar/A0 uniform-in-e certification
   into a one-drift problem, subject to a floor extension.
2. **Non-target validation of Theorem M by the validation stream.** Check the order at e in {0, 1/4, 1/2, 1, 3}. The
   planted negative control is a start (p0, 0), p0 > 0, where the order must fail near e = 0 (§c.8).
3. **DEFER settling X308.** Either outcome has zero closure leverage.
   * Do **not** spend compute on lower-bound routes at 308: they are expected to be false and are rigorously
     impossible for L and R4.
   * If the user later wants the question settled, use the draft protocol's Variant P in a separately authorized
     campaign. It is best folded into an A0/Abar-supply campaign whose floor-extension decision is frozen before any
     evaluation, so that the refuting U is not produced as a free-floating per-cell number (S1).
4. **Record the wording corrections** in §3 items 4-5 in any successor text that cites C8 R3 or ROUTE_AUDIT_R1's
   308 disposition.
