# Stream A (cell 306) — route summary

**Scope:** the cell-306 I1/I2 disagreement, its mechanism, and a common-theorem route.
**Status:** RESEARCH ONLY.
* No new quantity was computed for CUSUM m = 5 cells 305–309.
* No operator quantity was evaluated at a drift in [6/5, 13/5] or its mirror.
* The one 306 read is a HISTORICAL_READ reproduction. It is sanctioned by the marker at
  `audit/a306_reproduce_A.py`:27, and the scan lists it as SANCTIONED with 0 findings.
* PREAMBLE S8 is respected:
  * committed 306 numbers appear only in §4.1 (history), with no route factor;
  * route rows and gates carry no tail number.

Deliverables:
* `CELL306_I1_I2_DISAGREEMENT_AUDIT.md` — deliverable 1.
* `mechanism/MECHANISM_STUDY.md` — deliverable 2.
* `common/THEOREM_CV.md` — deliverable 3.
* this file — deliverables 4 and 5.
* Validation JSON:
  * `validation/A306_HISTORICAL_A_REPRO.json`
  * `validation/A306_MECHANISM.json`
  * `validation/A306_PFLAT.json`
  * `validation/A306_CV_VALIDATION.json`

## 1. Route registry

| route | cells | prospective motivation | theory status | implementation status | non-target validation | governance status | blocker | next action |
|---|---|---|---|---|---|---|---|---|
| **R-CV** Theorem CV part 4–5: one certificate set, verified by two arithmetically independent verifiers, gives one common supply | any K1 cell or drift block with an atom split; **not 306** | F1′ pays for soundness redundancy with a *value* requirement (FLOOR_R2 :62-77). Separation keeps the redundancy and drops the value duplication. | proved (THEOREM_CV §2–3) | V_A (exact rationals + C7), V_B (decimal directed rounding), untrusted search, all stdlib | PASS: 6/6 valid accepted by both with identical values; 7/7 planted rejected by both | CLOSURE-ONLY under r2. It redefines F1′(a) and uses a cross-set minimum. It needs a user-decided floor extension frozen before any tail search. | governance (floor extension); value tightness is limited by box/panel discretisation | user decision on a floor-r3 limb; independent review of Lemma BP and of both verifiers |
| **R-SAND** Theorem CV parts 2–3: two-sided sandwich and refutation of STRONGER claims | any; generic soundness audit of supply constants | STRONGER cannot be tested today (C11RD adjudication review N2; FLOOR_R2 :126) | proved, including the divided-difference lower bounds for sup\|D′\| and sup\|D″\| | same code; sandwich assembly and refutation logic in `cv_validate.assemble` | PASS: truth inside all four certified intervals; refutation pattern exact; divided-difference bounds sound on 5 exact fixtures (planted claim refuted 5/5; vacuous at wide enclosures, as predicted) | as an **audit** it changes no supply, but at 306 it computes new operator quantities in the quarantined band → barred tonight; needs its own authorization | quarantine; tight two-sided D enclosures are needed for (2b) | propose as a governance-neutral soundness audit, to be authorized separately |
| **R-PDEP** p-dependent taboo families (motivated by Proposition PF) | prospective cells without an I2 certification; **306: INVALID_RESULT_CHASING** | Proposition PF: any p-flat taboo certificate has τ ≈ whole-kernel ARL, which is structural slack | Proposition PF proved; family effect measured (float) | float LP study only; no rigorous certifier for p-dependent weights beyond V_A/V_B's generic polynomial support | float study PASS (4 negative controls); PF prediction 18/18 | at 306 this is route 306-c ("repair I2 until Γ < 0"), classed RESULT_CHASING_RISK (ROUTE_AUDIT_R1 §5) | governance; S1 | none for 306; for other cells only inside an authorized campaign |
| **R-HARM** statement harmonisation of D_lo/D1/D2 premises | any | the conditional vs unconditional D_lo was the only statement difference | done analytically: unconditional D_lo (D_SUB) is value-neutral in principle; D1/D2 stay conditional on (C_T, τ) in both (Theorem 5) | D_SUB kind implemented in both verifiers | covered by the CV validation | neutral | G10 fails: cosmetic, no value effect | none (record only) |
| 306-c / 306-d / 306-g (ROUTE_AUDIT_R1 §5) | 306 | — | — | — | — | RESULT_CHASING_RISK / GOVERNANCE_BARRED | fixed fact "no new 306 supply" (ROUTE_AUDIT_R1.md:92) | REJECT (unchanged) |

Route states (PREAMBLE S5):
* R-CV: **VALIDATED_NON_TARGET** in general; **BLOCKED** for 306 (governance).
* R-SAND: **VALIDATED_NON_TARGET** in general; **BLOCKED** at 306 (quarantine and authorization).
* R-PDEP: **THEORY_ONLY**, with a float study only; **INVALID_RESULT_CHASING** if applied to 306.
* R-HARM: **REFUTED as a value lever** (cosmetic).

No route is FREEZE_READY.

## 2. Gate table (G1–G10)

| gate | R-CV | R-SAND | R-PDEP | R-HARM |
|---|---|---|---|---|
| G1 prospective motivation, independent of target sign | PASS (trust structure of F1′; no Γ used) | PASS (N2 untestability) | PASS for new cells; **FAIL at 306** (the fix would be aimed at the sealed gap) | PASS |
| G2 mathematical validity | PASS (proof §3; Lemma BP §4) | PASS (mean value theorem; comparison lemmas) | PASS (Proposition PF proof) | PASS |
| G3 scope and assumptions explicit | PASS (A1–A5) | PASS | PASS | PASS |
| G4 reproducible implementation | PASS (stdlib; certificates, runs and JSON committed in the stream directory) | PASS | PARTIAL (float LP only) | PASS (D_SUB) |
| G5 non-target validation | PASS (A306_CV_VALIDATION verdict PASS) | PASS | PASS (float, non-certified) | PASS |
| G6 independent check | PARTIAL: two arithmetically independent verifiers from one author; Lemma BP common-mode; no independent reviewer yet | PARTIAL (same) | FAIL (single implementation) | n/a |
| G7 temporal integrity | PASS (declarations in docstrings before runs; search trial at depth 4 disclosed) | PASS | PASS | PASS |
| G8 no target leakage | PASS (guard_drift on every entry point; 0 scan findings in A_306; ledger lines NONTARGET) | PASS | PASS | PASS |
| G9 could be frozen prospectively | YES for new cells, given a floor extension; **NO for 306** | YES as an audit, given authorization | YES for new cells | n/a |
| G10 real improvement, not cosmetic | PARTIAL: real for trust semantics (removes value-duplication and makes STRONGER refutable); no value improvement by itself | PASS (adds a refuting object that did not exist) | PASS generically (large non-target slack removed by p-dependence) | **FAIL** |

## 3. Governance honesty (deliverable 4)

**Relation to the accepted route audit.** ROUTE_AUDIT_R1 §5 (`p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md`:311-324)
classes three routes as follows:
* 306-c ("tighten or repair I2 until Γ(S_I2) < 0"): RESULT_CHASING_RISK;
* 306-d ("a third implementation paired with I1"): RESULT_CHASING_RISK and GOVERNANCE_BARRED;
* 306-g ("RSO or any new mechanism applied to 306"): GOVERNANCE_BARRED.

Every way of using this stream's results at 306 falls into one of those classes:
* **R-PDEP at 306 is 306-c.** Replacing I2's p-flat family by a p-dependent one "repairs I2". This audit's own Part C
  and Proposition PF identify where I2's slack lies, so a 306 application would be designed with knowledge of the
  sealed gap. That is the definition of the result-chasing risk (PREAMBLE S1).
* **R-CV at 306 is 306-d or 306-g.** New certificates on the 306 block, verified by V_A and V_B, are a new 306
  supply produced after I2 failed to certify. Pairing it with I1 is 306-d. Replacing both is 306-g.
* **R-SAND at 306 would be an audit, not a supply.** Certified lower bounds on sup|D″| over the 306 block, to test
  I2's D2, change no supply. But they compute new operator quantities at a quarantined drift (TARGET_QUARANTINE
  forbidden class 3; amendment 1), so they are barred tonight. Even as an audit, the outcome could be read as
  evidence for or against I2's supply. It therefore needs its own user authorization and a pre-declared,
  outcome-independent consequence rule.

**Is any 306 use possible without new governance? No.** The accepted route audit fixes "no new 306 supply"
(ROUTE_AUDIT_R1.md:92). Floor r2 forbids mixing and cross-set minima (FLOOR_R2_SPECIFICATION.md:57-60, 79-83). The
exactly-once marker `refs/c12r2/cell306-target-consumed` records that 306's F1′ target was consumed. **No legitimate
306 route exists under current governance.** 306 stays OPEN / NOT ADOPTED.

**What a prospective freeze would have to bind** (for any cell, and only after a user-decided floor extension. For
306 in particular, the user would also have to override ROUTE_AUDIT_R1 §1 and accept the disclosed result-chasing
exposure; this stream recommends against it.)
1. The floor-extension text:
   * a limb F1″ ("one certificate set accepted by two verifiers independent in the §6 sense; Γ < 0 on the supply
     built from it by Lemma Dv′ r2 ∪ Lemma G");
   * its relation to F1′ and F2;
   * the explicit permission (or not) of a componentwise minimum over doubly-accepted sets (Theorem CV (5)).
2. The verifiers:
   * code hashes of V_A, V_B and their libraries (C7 `c7_gaussian` sha);
   * arithmetic settings (2^-320; 90 decimal digits);
   * the Lemma BP specification text;
   * the cover and panel policy, fixed by a rule, never tuned per cell.
3. The certificate schema (`A306_CV_CERT/1`), and the rule that any verifier disagreement or rejection fails closed.
4. The **sandwich-consistency gate:**
   * every supply constant must lie on the correct side of the certified other side;
   * a violation is SCIENTIFIC_DISAGREEMENT (FLOOR_R2 §8), with no adoption.
5. The search:
   * either declared irrelevant (any certificate accepted by both verifiers counts, since search does not affect
     soundness);
   * or, to limit look-elsewhere, one frozen family ladder and a stopping rule, declared before any tail-drift
     evaluation.
6. The cell set: chosen by rule, never by closeness to closure.
7. Treatment of the historical I1/I2 constants (retained as-is, never mixed), and the consumer and its non-constant
   inputs unchanged (otherwise CLOSURE-ONLY under r2, PREAMBLE S6).
8. One sealed evaluation per cell, independent reviews, and an adjudication.
9. For 306 specifically: disclosure that the designer has seen the sealed disagreement, and this audit's mechanism
   findings.

## 4. Per-cell deliverable — cell 306

### 4.1 Current state (committed history; quotes only, no route factor attached)

* **OPEN / NOT ADOPTED.**
* Γ(5,306; S_I1) = −0.030469257709306738 (C2_D5_FORECAST.json:47).
* Γ(5,306; S_I2) = +0.005159101140006536, sealed once (C12R2_CELL306_RESULT.json:129).
* CELL306_NOT_ADOPTED because F1′(d) fails (C12R2_ADOPTION_ADJUDICATION.md:2-7); review ADJUDICATION_ACCEPTED
  (c5324a78).
* The route audit concludes NO_SUPPORTED_ROUTE (ROUTE_AUDIT_R1.md:322-324).

### 4.2 Disagreement decomposition (qualitative; `CELL306_I1_I2_DISAGREEMENT_AUDIT.md` Parts B and D)

* **Statements.** Five are EQUIVALENT. D_lo is PROOF_STRENGTH_DIFFERENCE in I2's favour, and value-neutral in
  principle.
* **Consumer and inputs.** EXACTLY_EQUIVALENT.
* **Supplies.** Each supply is effectively one constant set: C2 wins S_I1 and I2 wins S_I2 on every field. This is
  reproduced exactly (HISTORICAL_READ).
* **eff branch.** τ/D_lo in I1, Ā in I2 (SUPPLY_DIFFERENCE).
* **Cause of the branch difference.** I2's p-flat weight forces τ = Ā (Proposition PF), while I1's first-rung ARL
  candidate makes Ā loose.
* **Values.** IMPLEMENTATION_SLACK on both sides, of different kinds:
  * I1: α ladders, global-polynomial kinks, depth-0 residual ranges, ρ·env widening, sub-block decoupling;
  * I2: a linear p-flat family, a linear sub-solution, box/panel loss, whole-block uniformity, grid rounding.
* **Classification: IMPLEMENTATION_SLACK acting through a SUPPLY_DIFFERENCE**, not a proof-strength difference.
* **Unattributed.** Which constant drives the Γ sign stays UNKNOWN; attributing it is forbidden.

### 4.3 Summary fields

| field | value |
|---|---|
| strongest surviving route | Theorem CV (R-CV + R-SAND), as a prospective, implementation-independent trust structure for cells **other than 306**. For 306: none. |
| theorem / implementation | THEOREM_CV (proved). Proposition PF (proved). V_A, V_B, search and validation (stdlib). |
| validation | A306_CV_VALIDATION PASS; A306_MECHANISM PASS; A306_PFLAT PASS; A306_HISTORICAL_A_REPRO PASS. All non-target, except the sanctioned historical read. |
| defects flagged | none found. I2's D2 soundness is UNKNOWN: no refuting object exists at 306; R-SAND would supply one, but it is barred there tonight. |
| remaining blocker | governance: fixed fact "no new 306 supply"; consumed F1′ target; r2 forbids mixing and cross-set minima; S1 result-chasing exposure created by knowing the sealed gap and this audit |
| **FREEZE_READY** | **no** |
