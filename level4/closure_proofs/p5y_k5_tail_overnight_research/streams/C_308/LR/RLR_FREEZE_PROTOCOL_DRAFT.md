# RLR tail certification: prospective freeze protocol

**DRAFT ONLY. NOT FROZEN. NOT AUTHORIZED FOR EXECUTION.** No step of this document was executed in the overnight
campaign. It exists because the brief (§33 M) asks for an inactive protocol draft for any route that reaches
FREEZE_READY.

## 0. Status of the route this protocol would use

| item | value |
|---|---|
| route | regenerative likelihood-ratio atom constants, used through the combined supply **min(RLR, Dv′ r2, Lemma G)** for A1 and A2 |
| theory | `THEOREM_LR.md` (LR-1, LR-3, (i′) certificates, §6 block uniformity) |
| implementation | `cusum/c1b_*.py`, pinned hashes (`C1B_ROUTE_SUMMARY.md`, R2 revision) |
| reviews | REVIEW_RLR_R1 (incomplete, not a verdict); REVIEW_RLR_R2 ACCEPTED_WITH_CONDITIONS; REVIEW_RLR_R3_VERIFY CONFIRMED_WITH_NOTES (N3 and N5 fixed afterwards; see the campaign report) |
| governance | **CLOSURE-ONLY under floor r2.** RLR is neither a Lemma G nor a Lemma Dv′ r2 supply, and the combined supply mixes certifiers. |

## 1. Preconditions: user decisions, taken **before** any freeze commit

1. **U3.** Decide whether a closure under this supply could ever count for adoption.
   * If yes, a floor extension naming this supply must be frozen **before** the freeze of this protocol (C2
     Condition 1).
   * If no, the protocol runs as CLOSURE_ONLY. Its best outcome is `SCIENTIFICALLY_CLOSED_NOT_ADOPTED`, with no r6.
2. **Disclosure.** The authorizing user acknowledges the following before authorizing:
   * incidents 01–03 and their residues (`ledger/INCIDENT_0*.md`);
   * the committed per-cell factors (C3 knockout; C8 x-eff), which were known to everyone who designed this route.
     They were not used to design or tune RLR, but the choice of the A1/A2 channel was informed by committed C3/C4
     findings.
   * **Result-chasing risk: MEDIUM.**
3. **Cell set: {307} only, fixed in this draft (revision r1) and not to be changed after any result.**
   * **Why not 308 and 309 (committed scope, not a forecast).** This protocol changes only A1 and A2; A0 stays at C2's
     committed value. The committed C3 knockout (C3-N4; C4 §8; ROUTE_AUDIT_R1 §4) shows that at A1 = A2 = 0 with the
     certified A0:
     * cells 308 and 309 remain non-closing under the frozen consumer;
     * cell 307 closes.

     So an A1/A2-only supply **cannot** close 308 or 309 under this consumer, and evaluating them would consume their
     exactly-once target evaluations for no possible outcome. They need an A0-channel or other improvement (the C2b
     certifier, not yet freeze-ready; TPT, blocked by incident 01; SC or RSO, data-blocked) and a separate protocol.
   * 305 is OUT (adopted).
   * 306 is OUT (route audit 306-c/d/g).
   * **Revision note.** The r0 draft of this protocol (commit 9e8ae240) listed {307, 308, 309}. It was corrected before
     any freeze because of the scope fact above.

## 2. Stage 1: operator certification, exactly once

* **Blocks.** For each cell k, the pre-registered partition of its drift interval into N_k = ⌈2ρ_k / (1/100)⌉ equal
  sub-blocks. That is the C2 registry partition rule, adopted verbatim. No other partition is allowed.
* **Per block, with the pinned `c1b_*` code:**
  * the RLR certificates: taboo and whole-kernel supersolutions, two-sided D-constants, (i′) quadratic certificates;
  * the e-free block candidate family (D12);
  * the D13 coverage rule, which excludes only unreachable states (verified by R3).
* **Output per block:** the certified inputs and the combined A1, A2 = min(RLR, Dv′ r2, Lemma G), computed from the
  same certified inputs.
* **Cell constants.** Componentwise **max** over the cell's blocks, the standard worst-block composition.
* **A0.** Unchanged: C2's committed A0. This protocol changes only A1 and A2.
* **Stop rule.** If any block fails to certify, the cell's Stage-1 outcome is `CERTIFICATION_FAILED`. There is no
  retry with other parameters.

## 3. Stage 2: one sealed Γ evaluation per cell

* **Supply S_RLR(k):**
  * A0 = C2's committed A0;
  * A1 = min(C2's committed A1, the Stage-1 A1);
  * A2 = min(C2's committed A2, the Stage-1 A2).

  Each is a minimum of sound bounds. This is valid for **scientific** closure only, and is outside floor r2's
  single-implementation rule.
* **Consumer.** The frozen C2 consumer path, exactly as floor r2's adoption quantity describes it:
  * `c2_d5_forecast.py` 18403dbe;
  * `deflated_consume.py` a0a836fa;
  * `tct_rule.py` 98f6eee4;
  * the direct clause of `k5b_literal`;
  * `tail_forecast_r2.py`, pinned by hash.

  Only A is substituted. **Not TPT**: its tail use is blocked by incident 01.
* **Reproduction gate, before any target Γ.** The control evaluation with S_I1 must reproduce C2's committed
  `Gamma_exact` exactly for every cell in the set. Otherwise the outcome is `REPRODUCTION_FAILED` and no target value
  is produced.
* **Outcome per cell:**
  * `CLOSED_SCIENTIFIC_NOT_ADOPTED` if Γ < 0 under CLOSURE_ONLY;
  * `NOT_CLOSED` otherwise.

  Adoption is possible only under a pre-frozen floor extension.

## 4. Qualification (before any grant; decoys only)

* **Decoy blocks** at non-target drifts, run through the full Stage-1 pipeline.
* **Decoy TC-T inputs** in the committed schema, run through Stage 2. The reproduction gate must pass on the decoys
  and STOP on planted mismatches.
* **Negative controls, class (a):**
  * the C1b point and block plants: supersolution, interior-drift and discriminant-only;
  * the two-sided combined-supply test (R3 N5 fix).
* **C12-R1/R2 lessons, all binding:**
  * the sandbox is built at the freeze commit;
  * the verifier refuses at any later governance state;
  * every written path is a seal precondition (lexists / lstat, including ignored files);
  * writes use `O_CREAT|O_EXCL|O_NOFOLLOW`;
  * every post-marker failure is sealable;
  * the ledger line is written before execution.

## 5. Exactly-once mechanics

* Consumed ref: `refs/rlr-tail/cell307-target-consumed` → the grant commit.
* Pending-result ref and a sealed result JSON, committed alone.
* No re-run, no partial re-run, no change of partition, candidate family, arithmetic or cell set after the grant.

## 6. Cost (from C1b measurements at non-target drifts; to be re-measured on decoys at qualification)

* A block certification takes minutes of local CPU. The C1b block at width 1/32 took about 246 s.
* Cell 307 has 10 sub-blocks under the C2 partition rule.
* The whole of Stage 1 is of order 10 blocks, so on the order of an hour of CPU on this Mac.
* No host is needed (U1 not required).

## 7. What this protocol can and cannot establish

* **It can establish** scientific closure of a cell under a sound supply, or its absence.
* **It cannot adopt anything** under floor r2 as written. It cannot touch 305 or 306. It cannot create r6 without a
  pre-frozen floor extension and a separate adjudication.
