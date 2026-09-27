# Independent review — K5 remaining-cells prospective route audit
ROUTE_AUDIT_REJECTED

## Reviewer context

* Fresh context, read-only, adversarial. I had no part in C1–C12-R2, floor r2 or the audit.
* Target: worktree `/Users/suzhe/ReBaseGuard-k5c11rd`, branch `p5y-k5-tail-c11rd-d1d2-extension`, HEAD `1667ea88`.
  * `ROUTE_AUDIT.md` (commit d52cec02, 679 lines).
  * `protocol/PROPOSED_RSO_PROTOCOL_DRAFT.md` (commit 1667ea88, 295 lines).
* I changed nothing in either repository. I used only `git log/show/show-ref/cat-file/grep/ls-files/rev-parse/merge-base`,
  `sed -n`, `grep`, `head`, `wc` and `git status --porcelain --ignored`. Once, I used the system `python3 -I -S -B`
  (not repository code) to list string fields of the floor-r2 governance JSON.
* I ran no campaign code, producer, certifier, verifier or driver. I computed no Γ, margin, factor, bisection,
  knockout or Λ bound.
* I opened no C11R quarantine path, wrote no D1/D2 value, read no session transcript and made no network, AWS or
  Vultr contact.
* **Disclosure of incidental exposure.** Some committed text shows historical 306–309 numbers. None was used in any
  computation, and each was already quoted in committed adjudications:
  * `MEASUREMENT_NOTE.md` (aggregate input ranges over 305–309, and replay CPU seconds);
  * C9 README :82–88 (the cell-307 reconstruction);
  * C2 adjudication :45–48;
  * C5 adjudication :133–137;
  * one grep line that showed a truncated `M_now` rational from `C9_PHASE1.json`.
* **Arithmetic.** The only arithmetic I did was rounding checks of the E10 values the audit quotes (for example,
  −0.171755… rounds to −0.1718).

## What I checked and how

* **Starting state (§0).**
  * `refs/c12r2/cell306-target-consumed` points to dec92e09, and `refs/c12r2/cell306-pending-result` points to 0ac46b3d.
  * The r5 blob at HEAD is `f978eeb6b41188eabaf3c6d590c9178d711f1ce6`.
  * No `*COVERAGE_MAP_R6*` is tracked.
  * `b83cc6f5` is a blob and `def4e453` is a commit.
  * The tree is clean, including ignored files.
  * All confirmed.
* **Spot-checks of cited file/line claims:** see point 1 (21 checks).
* **Motivation, chronology and floor texts:**
  * C4 adjudication §5–§8 and Conditions (`C4_ADJUDICATION.md` :190–305, :486–581);
  * C5 adjudication :39–42, :66–76, :133–137, :605–630, and OND C5 :40–60;
  * C6 README, OND C6 and adjudication :17–24, :50–66, :133–140, :166–232, :368–412;
  * C8 adjudication :160–185, :370–395, :462–500, and `ERRATUM_C8_GATE.md` :1–50;
  * C9 README :1–120;
  * C10 README :90–100;
  * floor r2 `FLOOR_R2_SPECIFICATION.md` (all 261 lines) and `config/K5_TAIL_ADOPTION_FLOOR_R2.json` (string fields);
  * `THEOREM_TCT.md` :1–60 and :100–167;
  * `measurement_r1/MEASUREMENT_NOTE.md` :1–67;
  * C2 `R_STAGE_DESIGN.md`;
  * C2 adjudication §K :494–515;
  * C12-R2 adjudication :355–400 and verdict lines of every C12-R2 review;
  * `p5y_k5_perron_deflated_resolvent/FEASIBILITY_REPORT.md` :13–36, for the definitions of Ĝ_e and D_e.
* **Omitted-evidence sweep.**
  * The verdict token of every review, adjudication, erratum and stop file in `p5y_k5_tail_*`,
    `p5y_k5_m5_tail_closure`, `p5y_k5_order3_readiness_audit` and `p5y_k5_remaining_cell_closure`.
  * A `git grep` for residual-specific, pointwise and non-norm language across all K5 namespaces.

---

## BLOCKERS

### B1 — The adoption criterion is not "floor r2 verbatim". Under r2 as written, RSO cannot adopt at all, and making it adopt is a floor change the audit says it does not make.

**What floor r2 fixes.** Its machine-readable rule, `K5_TAIL_ADOPTION_FLOOR_R2.json`, contains three relevant fields:
* `rule/chosen_supply_restriction`: the chosen supply "must be a SINGLE-IMPLEMENTATION supply: the componentwise
  minimum (C2's D4 rule) over registry-free Lemma G and Lemma Dv' r2 applied to constant sets produced by ONE
  operator-constant implementation". The spec restates this in §3, :57–60.
* `quantity_compared/adoption_quantity`: Γ(5, k; S) is the value "computed by the frozen consumer path that produced
  C2's committed Gamma_exact (… c2_d5_forecast.py blob 18403dbe …)". The spec restates this in §4, :87–88, with
  "every other input unchanged", including "the TC-T premises".
* `fail_closed/3`: "the chosen supply violates 'chosen_supply_restriction': the base clause and F2 are not satisfied".

**Why S_RSO falls outside it.** The draft's S_RSO (§5) replaces TC-T's order-0 term with
`min(RSO bound, A0·‖φ_H‖)`.
* That is a modification of the consumer (a "TC-T variant", draft §2).
* It is not an atom-constant supply built from Lemma G and Lemma Dv′ r2.
* So Γ(5, k; S_RSO) is not r2's adoption quantity, and S_RSO violates the chosen-supply restriction.
* Applied verbatim, r2 **fails closed** on every RSO cell. Every RSO outcome is at best scientific closure, with no
  adoption and no r6.

**Where the audit and draft say otherwise.**
* Draft §13: "floor r2, verbatim … no new limb and no changed threshold".
* Audit §10: "It does not presume any floor change".
* G-1 asks a review to confirm that multiplying a non-atom-constant term by 1.25 "is not a floor change". It cannot
  be one, since r2's F2 is defined over the atom constants of an r2 chosen supply.
* G-2 frames the clause as a free "conservative choice". It is not free: r2 binds the adoption quantity to C2's
  consumer path.

**What an adoption route actually requires.** A prospective replacement under C2 Condition 1, as r2 §9 :202–203
itself says. That is a floor change. It needs the user's instruction and must be labelled as one. It must not reach
the user as a "G-1 reading" inside a Stage-0 freeze, because the audit's own fixed facts forbid reinterpreting r2.

**Asymmetric treatment of R-α.**
* R-α is REJECTED partly because "Under r2 it can at best give SCIENTIFICALLY_CLOSED_NOT_ADOPTABLE" (§6).
* Yet R-α is an r2-conformant supply: a new I1 constant set through Lemma Dv′ r2.
* RSO, which r2 structurally cannot adopt, is recommended.

**Consequence.** The recommendation's value proposition and the Stage-1 classes `CLOSED_F2_PASS` and `CLOSED_F2_FAIL`
(draft §9) are misdescribed to the person who would authorize the freeze.

### B2 — The case for C over D rests on claims that are false or contradicted by the repository and by the audit itself.

The audit (§7) argues D's cost is "information, not integrity" on three grounds. None survives.

**(a) The exclusivity claim is false.** The audit says RSO is "the only named one that 'escapes the floor entirely',
i.e. that can reach 309's refutation scope and 308's order-0 problem".
* C4's phrase, at :555, is about the **E_a[τ] floor within the order-0 channel**. It is not about 309's refutation
  scope in general.
* C4 §6 shows that halving the candidate sup norms, or halving ρ, voids the 309 exclusion:
  * the table at :229–235;
  * items 2, 3 and 7 at :260–271;
  * Condition 1 at :522–524.
* C5 adjudication :607–609 says three non-R-stage oracles each close every remaining open cell.
* C8's adjudicator forced C8 to **withdraw exactly this kind of exclusivity claim**. `ERRATUM_C8_GATE.md` E3 (:39–44)
  records that six C5 source-supply levers void the 309 exclusion, the cheapest being `all_four_together` at 0.6076 %.
* The audit's own §4 "309 UNKNOWN" list names R4, R5, B1 and R-asm as routes outside the refutation scope.
* For 308, a tighter uniform A0 also addresses the order-0 problem:
  * C8 adjudication R3 row, :382: ceiling 4.442851 vs floor 3.512734;
  * C5 Condition 11(c), :619–620.

**(b) The "three adjudications" claim is overstated.** The audit says "three independent adjudications (C4, C5, C8)
named, before C12, as the next thing to cost".
* Only C4 ranks RSO first (:259, :554).
* C5's ordered successor list is E2, A1, E1, B1, and it says RSO "should be costed alongside (b)" (C5 adjudication
  :615–622; OND C5 :47–53).
* C8's adjudicator lists RSO among four unevaluated items. It points out that `all_four_together` is the smallest
  published requirement (:174–181, :385, :390–392).
* The three are sequential and each cites C4. They are not independent.

**(c) "No host" is false.** The audit says RSO's "first stage needs no target, no host and no new real address".
* Stage 0 contains S4 and KG5: "an authorized certifying host exists with the pin, and 305 replay identity PASSES"
  (audit §8; draft §7 S4, §8 KG5, §17 "host build … needs the user's permission").
* §10 also places the host authorization in the **Stage-1** authorization ("That authorization includes an explicit
  host authorization").
* As recommended, Stage 0 therefore cannot pass KG5 without a host decision the recommendation defers. That is an
  internal contradiction in the one action the audit asks the user to authorize.

With (a)–(c) removed, and with B1 applied (no adoption path under r2), the §7 conclusion that "C with a D fallback
dominates D" is no longer supported by the argument given. It may still be defensible on information grounds, but
the audit has not made that case honestly.

### B3 — Omitted negative evidence on the data path of the recommended route. The applicability gate cannot detect it.

RSO Stage 1 consumes φ_H "as a function" from an identity-gated replay (draft §3; audit §6 RSO). The repository
records two facts the audit and draft do not carry.

**(a) Provenance.**
* All four open-tail K1 records are **P3 with `admissible_for_NEW_scientific_reuse: false`**. Their standing exists
  only through the `already_adopted_exception` (C6 adjudication §2, :168–185).
* C6 Condition 10 ("no P3 object may be adopted as new scientific evidence") is recorded as binding (OND C6 :22).
* C6-N4 records a standing provenance anomaly in the export manifest that carries all 326 record hashes (OND C6
  :37–39).
* RSO would derive a **new** scientific quantity from objects that are never serialized and are regenerated against
  those records.
* Whether the already-adopted exception covers that is an open governance question. E17 mentions "P3" but omits the
  admissibility flag, Condition 10 and C6-N4.

**(b) Trust surface.**
* The replay's identity gate compares 262 scalar fields, with candidate suprema compared only at 53 bits (C6
  adjudication (b), :375–390).
* `MEASUREMENT_NOTE.md` :37 states that `sup.{F,D,H}` are gated by "neither gate directly … the residual trust
  surface".
* A pointwise φ_H is exactly that ungated surface. The draft's "The replay must reproduce every committed scalar
  bit-identically" (§3) does not certify any function value.

**Why this matters for the gate.** S3 and KG4 check only "presence, hashes and call signatures" (draft §7). They
would pass while the load-bearing input is unadmitted and ungated. So the route's classification as
PROCEED_IF_GATE_PASSES rests on a gate that does not test the relevant risk.

---

## NOTES (non-blocking)

**N1. 306-f is mislabelled.**
* C2 §K (:501–506), the adjudication that set the floor, lists "a real order-3 candidate … under the R-stage's own
  separately frozen gate" as one of three discharge routes for 306.
* C8 adjudication Condition 6 (:482–483) required successors to carry it.
* The audit instead labels 306-f NO_SUPPORTED_ROUTE, and lists the order-3 R stage under 306 "NOT APPLICABLE". It
  relies only on E09 §3 and C4 §8.
* The correct label is GOVERNANCE_BARRED: guard DENY, N1/N5/N7 open, and the 306 rescue prohibition. The 306
  conclusion does not change.

**N2. The 308 FAILED entry misquotes C4's status.**
* The audit quotes C4 §8's "cannot be excluded by this route".
* C4's verdict (:510–512) says the correct status is "operator-level route not excluded", **not** "cannot be
  excluded". C4 Condition 2 (:527–533) forbids quoting the universal negative.
* X308's risk note omits C4's Monte-Carlo evidence (~65 SE, :508–510; Condition 3, :534–537) that no lower-bound
  route will exclude 308. On uncertified evidence, X308 is effectively dead, not merely HIGH risk.

**N3. Outcome classes.**
* 309's "NOT APPLICABLE: any uniform-eff tightening" is a proved impossibility within scope. That is FAILED under the
  audit's own legend (§2), and it duplicates the FAILED bullet.
* 307's "F1′ NOT APPLICABLE" is better stated as UNAVAILABLE/UNKNOWN (never attempted). r2 makes F1′ available to
  any cell with its own two-implementation evidence (:193).

**N4. Compute.**
* Replay cost is **measured** in committed evidence. `MEASUREMENT_NOTE.md` :17–29 gives 1350–1360 CPU-s per cell for
  306–309, and ≈ 1.87 CPU-h for the replay of 305–309.
* The audit (§6 RSO) and draft (§17) call it "unmeasured". That is not invented, but it omits a committed
  measurement.
* KG6 multiplies the **replay** cost only. It never measures the RSO evaluation itself, which is a new per-cell
  operator-level bound. The nearest committed prior is C9's 887 CPU-s for one cell-307 taboo certification
  (`C9_ALPHA_LEVER.json`:43).

**N5. Toolchain and host.**
* The draft's S4 pin is C9's `taboo_certify` pin.
* The replay chain ran in the "frozen Aux5 venv (python 3.12.3, numpy 2.5.2, scipy 1.18.1, python-flint 0.9.0)" on
  `rebaseguard-vultr-02` on 09-20 (`MEASUREMENT_NOTE.md` :3–4). The draft's pin omits scipy.
* C6 adjudication N9 (:135–138) says vultr-02 lacks numpy, scipy and flint (by `find_spec`). That unreconciled
  inconsistency bears directly on KG5, and the audit repeats "no certifying host in scope" without surfacing it.

**N6. Notation and target term are undefined for a freeze.**
* The draft's Ĝ is the taboo resolvent Ĝ_e (C4 :256; Perron `FEASIBILITY_REPORT.md` :13–16). The same protocol
  admits TC-T as an input, and TC-T uses Ĝ for the order-3 candidate of F, set to 0 in (P2′) (TC-T :14, :46).
* TC-T's order-0 contribution is `A0·p2` with `p2 = f_H + ρ f_G + ρ² Env4/2` (TC-T :125), not `A0·‖φ_H‖`. Its sup-norm
  parts (f_G, Env4) are norm-only bounds, not residual functions.
* C4 §6 (:222–247) indicates the sup-norm-driven channel dominates at 309.
* The draft must state which part of `p2` the majorant replaces, and must rename Ĝ.

**N7. "Inherits … all 32 pin classes" (draft §10).** C12-R2 had 32 pinned **inputs** (`C12R2_ADJUDICATION_REVIEW.md`
:110), not 32 pin classes. The phrase has no transferable meaning.

**N8. Host provisioning.** C6 Condition 7 and adjudication §8 item 2 (:292) require host provisioning to be a
separately governed prerequisite: the user's decision, "not a parenthesis inside a route entry". Stage 0 bundles it
(S4–S5, KG5–KG6). A theory-and-fixtures-only Stage 0a would be cleaner and would make the "no host" claim true.

**N9. 307's place in the recommendation.**
* C4 §8 (:288–290) says A0 is **not** 307's blocker; its blocker is (A1, A2).
* C4's RSO motivation is centred on the E_a[τ] floor, that is, on 309 and 308.
* RSO's application to 307 (first in the frozen order) is therefore not motivated by the repository. It is harmless,
  since every cell runs regardless, but the audit should say so.

**N10. R-asm vs RSO result-chasing ratings are asymmetric.**
* R-asm's theory stage is as target-free as RSO's.
* The audit's R-asm entry omits the 0.6076 % `all_four_together` figure (C8 erratum E3). The C8 adjudicator called it
  the smallest published requirement.

**N11. Negative-evidence list omissions.**
* C11RD's first qualification was QUALIFICATION_REJECTED (`C11RD_R1_QUALIFICATION_REVIEW.md`).
* C6 Condition 1 says A1 must not be read as "replayable": "the INPUTS only. Never the gain." E17 quotes
  `REPLAYABLE_EXISTING_ADDRESS` without that qualification. It is harmless for RSO, which needs only inputs.

**N12. Stage-0 theorem premises.** If the RSO theorem needs cell-specific premises (compare C5-T's `x_lo > 0`, which
fails at cell 0; C5 adjudication :39–42), the draft must say that checking them on 307–309 uses geometry fields only,
or else moves to Stage 1.

**N13. Minor.**
* E15 cites :255–258. The text is at :256–259.
* E10 is marked "(explorer, not re-verified)". I verified its four values in `C2_ROBUSTNESS_AND_R_ATTRIBUTION.json`,
  so that caveat can be lifted for E10.
* KG2 is enforced by construction through the `min` in §5. It is a soundness obligation, not a kill gate.

---

## Evaluation of the 12 points

### 1. Completeness of the evidence map (21 spot-checks, all against HEAD)

| # | claim checked | where | result |
|---|---|---|---|
| 1 | E01 :91 `K5_INCONCLUSIVE` | | ✓ |
| 2 | E03 :112 | (text at :111–112) | ✓ |
| 3 | E11 :47: Γ(306) = −0.030469257709306738 | | ✓ |
| 4 | E11 :65: Γ_deg(306) = +0.029163293 | | ✓ |
| 5 | E11 :474–478: margin 1.1277; F2 +0.029163 | | ✓ |
| 6 | E11 :497: −0.036198 / 1.1555 | | ✓ |
| 7 | E14 :269, :283, :294–295 (7.56 %), :350 (+0.039568, 5.2185, 4.3752), :351 (+0.092812) | | ✓ |
| 8 | E15 §7.1 wording and :503 | | ✓ |
| 9 | E16 :41, :68–75 (post hoc, disclosed), :135–136 (1.211422–1.294912 %) | | ✓ |
| 10 | E19 factors 1.0670710354836621 / 1.0960072461461898 / 1.3700090576827373 / 1.4384228261705914 / 1.798028532713239 | `C8_ADOPTION.json` :28, :48, :47, :67, :66 | ✓ |
| 11 | E19 R3 floors/ceilings and R5 19.612136 % | C8 adjudication :382–384 | ✓ |
| 12 | E19 adjudication :168–171 | | ✓ |
| 13 | E20 α table 1.098807 / 1.137406 | C9 README :37–42 | ✓ |
| 14 | E20 887 CPU-s and "~31 CPU-minutes" | `C9_ALPHA_LEVER.json`:43; `REVIEW_C9_STOP.md`:106 | ✓ |
| 15 | E20 STOP_PREMATURE | `REVIEW_C9_STOP.md` :357 | ✓ |
| 16 | C10 "next purchase … not an α run" | C10 README :95 | ✓ |
| 17 | E22 "within 31%" | C11 README :123; EXECUTION_INVALID | ✓ |
| 18 | E18 3.586306094 / 9.7933 % | OND C7 :32–33 | ✓ |
| 19 | E07 1.071/1.362/1.771/2.253 and E08 2.252903 → 2.101597, 6.716 % | | ✓ |
| 20 | E09 ≈0.44 / ≈1.3 CPU-h, caps 3/6, "305 and 306 … need nothing", "estimate … not a certificate" | :76, :81, :83, :86–87, :99 | ✓ |
| 21 | floor r2 :224; E28 C12-R2 verdict lines, sealed value and F1′(a–c) hold / (d) fails | adjudication :362–368 | ✓ |

The quoted numbers are accurate. The map's gaps are of **coverage**, not of transcription:
* C2 §K's order-3 route (N1);
* C6 Condition 10 and the admissibility flag (B3);
* C8 erratum E3 (B2a);
* `MEASUREMENT_NOTE` cost and host (N4, N5).

### 2. Omitted negative evidence

**Material:**
* C8 erratum E3, the withdrawn exclusivity claim, which the audit repeats (B2a).
* C6 Condition 10, the P3 admissibility flag and C6-N4 (B3a).
* The replay trust surface (B3b).
* C4 §6: the order-0 channel is not dominant at 309 (N6).
* C4's verdict wording on 308 and its Monte-Carlo evidence (N2).
* C2 §K's third discharge route for 306 (N1).

**Minor:** C11RD's first QUALIFICATION_REJECTED (N11).

**Correctly carried:** C1 MARGINAL, C3 REJECTED, C4 scope, C5 post-hoc gate, C6 "no host" and "A1 harder", C8
rule-1 erratum, C9 blocked, C11 EXECUTION_INVALID, C11R AGREEMENT_INSUFFICIENT, C12/C12-R1 rejections and the C12-R2
disagreement.

### 3. FAILED vs UNKNOWN vs NOT APPLICABLE

Mostly kept distinct and correct. The C12-R2 result is correctly described as non-certification, not disproof.

Errors:
* 306's order-3 entry is NOT APPLICABLE; per C2 §K it is applicable but barred (N1).
* 308's exclusion is under FAILED with the wording C4's verdict rejects (N2).
* 309's uniform-eff entry belongs in FAILED (N3).
* 307's F1′ entry should be UNKNOWN/UNAVAILABLE (N3).

None of these changes a recommendation.

### 4. Result chasing

* No recommended route or frozen parameter is chosen from target-proximity numbers.
* G-2 picks the conservative clause.
* The Stage-1 order is fixed, and every cell runs regardless.
* R-α, R-I2-alone and Floor-307 are correctly rejected for fitting known factors.
* The residual concern is the R-asm vs RSO asymmetry (N10). It is not a blocker.

### 5. Fixed 306 facts and prohibitions

**For 306: respected.**
* No recomputation.
* 306-a…g all REJECT.
* 306 is excluded from every RSO stage.
* No new 306 supply is sought.
* r5 and refs are untouched.
* No r6.

**For floor r2: not respected in substance.** The draft's adoption criterion for 307–309 relies on a reading of r2
(G-1, and S_RSO as a "chosen supply") that r2's text does not permit. It is presented as verbatim r2 (B1).

### 6. Are 307–309 routes genuinely prospective?

* **Stage 0: yes.** It is target-free as designed, but see B2c and B3 for its host and data gaps.
* **Stage 1: yes.** It has one sealed evaluation per cell, exactly once, with no adaptive selection.
* **Adoption: not prospective as written**, because the adoption rule it would need does not yet exist (B1).

### 7. Independent motivation of the recommended route

**The motivation exists and predates C12.** I verified each commit and checked ancestry with `merge-base
--is-ancestor` against C12's freeze b9ffc87f (2026-09-27):

| commit | date | location |
|---|---|---|
| e12a09e8 | 2026-09-22 02:34 | C4 :256–259, :554–556 |
| 69bff424 | 2026-09-22 04:58 | C5 adjudication :620–622; OND C5 :52 |
| 63a3f825 | 2026-09-22 20:58 | C8 adjudication :174–176, :385 |

**The audit overstates it** (B2b): only C4 ranks RSO first, and the three are not independent.

### 8. Kill gates, and SAFE PREFLIGHT vs LOAD-BEARING

**What is sound:**
* All gates precede any L-information.
* L1–L5 are well drawn.
* Forbidding real-cell calibration and real-cell rehearsal (L4, draft §11) is correct and stricter than C12-R2.

**The 305 replay-identity check is safe as specified.**
* 305 is adopted.
* Its scalars are already committed, and the same replay has been done before (`MEASUREMENT_NOTE` :17–23).
* The output is PASS/FAIL only.
* The candidates are deleted unread, and no RSO code touches them.

**No Stage-0 item is a disguised target proxy**, provided two conditions hold:
* the fixtures read no tail data;
* S3 stays code-and-schema-only.

**Defects:**
* KG5 requires a host that the recommendation assigns to Stage 1 (B2c).
* KG4 cannot detect the admissibility and trust-surface risk (B3).
* KG6 measures the wrong cost (N4).

### 9. Adoption criterion (G-1, G-2, G-3)

* **G-1.** Scaling the RSO term by 1.25 is dimensionally the same as degrading A0 in that term, so as a proposed
  **new** rule it is reasonable. But it cannot be "not a floor change": r2's F2 is defined over atom constants of an r2
  chosen supply, and S_RSO is not one (B1).
* **G-2.** Not a free choice. r2 fixes the adoption quantity to C2's consumer path, and RSO departs from that path
  anyway.
* **G-3.** Addresses operator-constant mixing only. It does not address that the RSO bound is a new certified
  object, outside r2's six-constant and N9 machinery.

**Verdict on point 9:** the criterion is prospective, but it is a floor change mislabelled as verbatim r2.

### 10. Is the draft freezable as a Stage-0 freeze?

**Not as written.**

Must close **before** a Stage-0 freeze:
* the B1 decision: RSO is declared closure-only under r2, **or** a prospective floor extension is explicitly
  proposed for user authorization;
* the B2c host placement;
* the B3 data-admissibility and trust-surface gate;
* the N6 definition of the replaced term and the Ĝ rename;
* the N5 pin, including scipy, and the host-record inconsistency;
* the N12 premise-check boundary.

Legitimately deferred to the Stage-1 freeze:
* grant and CAS mechanics;
* the concrete pin list (N7);
* the verifier sandboxes;
* the synthetic rehearsal cell;
* leak-scan sets;
* the per-cell wall cap;
* RSO-A/RSO-B independence details beyond the Stage-0 fixture agreement.

### 11. Compute estimates

* No invented measurements. "Unmeasured" labels are used consistently, and "No percentages" is honoured.
* But committed measurements were missed: replay ≈ 1350 CPU-s per cell, and C9's 887 CPU-s taboo run (N4).
* KG6's cap test omits the RSO evaluation's own cost.

### 12. Was D fairly considered, and is the preference over D justified on the stated criteria?

**D is described fairly** (§7 D; E01 :91; E03 :112).

**The preference over D is not justified as argued.** Two of its three premises are false and one is overstated
(B2). "Governance simplicity" is also understated for C: Stage 0 needs four reviews plus a host decision.

**The criteria it cites are the right ones, not chance of CLOSED.** Once B1 is admitted (no adoption under r2), the
residual case for C is information gain alone. The audit never states that case on its own terms.

---

## What would change the verdict

I would expect to return ROUTE_AUDIT_ACCEPTED if a revision does five things:

1. **Adoption (B1).** State plainly that S_RSO is not an r2 chosen supply, so RSO is closure-only under r2 as written.
   Offer any adoption path only as an explicitly labelled, prospective floor extension. That extension needs the
   user's instruction and must be frozen and reviewed before Stage 1. Apply the same adoptability standard to R-α.
2. **Premises (B2).** Delete or correct the three §7 premises. Then either:
   * restrict Stage 0 to theory plus fixtures, with no host, and treat host provisioning as a separate user decision
     (per C6 Condition 7); or
   * say explicitly that authorizing Stage 0 includes a host decision.
3. **Data path (B3).** Carry C6 Condition 10, the P3 admissibility flag, C6-N4 and the replay trust surface into the
   evidence map. Add an S3/KG4 item that decides admissibility and gating of pointwise replay data before Stage 1.
4. **Draft fixes.** Fix N6 and N5 in the draft.
5. **Comparison.** Re-argue C vs D on information gain alone.

The factual base (21/21 spot-checks), the 306 handling and the exactly-once design are sound. The defects are in the
adoption framing, the justification against stopping, and one gate.
