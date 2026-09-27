# Independent review — K5 remaining-cells prospective route audit, revision r1
ROUTE_AUDIT_ACCEPTED

## Reviewer context

* Fresh context, read-only, adversarial. I had no part in C1–C12-R2, floor r2, r0, the r0 review or r1.
* Target: worktree `/Users/suzhe/ReBaseGuard-k5c11rd`, branch `p5y-k5-tail-c11rd-d1d2-extension`, HEAD `4a4b1392`.
  * `level4/closure_proofs/p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md` (commit 802be11e, 671 lines).
  * `.../protocol/PROPOSED_K5_PARTIAL_CLOSEOUT_DRAFT.md` (commit 4a4b1392, 183 lines).
  * History read: `ROUTE_AUDIT.md` (r0, d52cec02), `protocol/PROPOSED_RSO_PROTOCOL_DRAFT.md` (1667ea88, headers only),
    `review/ROUTE_AUDIT_REVIEW.md` (27e259f4, in full).
* I changed nothing in either repository. Commands used: `git rev-parse/log/show/status --porcelain --ignored/
  for-each-ref/reflog/cat-file -t/ls-files/grep/merge-base --is-ancestor/diff --stat`, `sed -n`, `grep`, `wc`, and the
  system `jq` on exactly two JSON files: the floor-r2 config (rule-text fields `rule`, `quantity_compared`,
  `fail_closed`, `scope`, `authority`, `adoption_vs_closure`; I did not print `I2_constant_sources_for_cell_306`,
  `known_historically` or `what_the_designer_had_seen`) and r5 (only `K5_COVERAGE_COMPLETE` and the open ranges).
* I ran no python at all, no repository module, no campaign code, producer, certifier, verifier, driver or leak
  scanner. I computed no Γ, margin, factor, bisection, knockout or Λ bound.
* I opened no C11R quarantine path, did not open any `POST_WRITE_LEAK_SCAN.json`, wrote no D1/D2 value, read no
  session transcript, did not read the previous reviewer's scratch directory, and made no network, AWS or Vultr
  contact.
* **Incidental exposure (disclosed).** Committed adjudication text shows historical 306–309 numbers. I read, and used
  in no computation: C2 adjudication :45–48 and :470–506; C3 adjudication :346–351; C4 adjudication :229–243,
  :286–291, :501–556; C5 adjudication :135–136; C8 README :52–54, C8 adjudication :382–385; C9 README :29–39;
  C2 `phase_r/R_STAGE_DESIGN.md` :20–92 (critical-ratio table); Campaign B README :20–38; C12-R2 adjudication
  :380–400, :494–505; `MEASUREMENT_NOTE.md` :1–45 (record/output hash prefixes and CPU seconds).
* **Arithmetic.** None. The only operations were orderings of numbers printed side by side in one committed table
  (e.g. R_STAGE_DESIGN §2), which the source itself draws.

## What I checked (files and lines)

* **Starting state.** HEAD 4a4b1392; tree clean including ignored files; `git diff --stat 27e259f4 HEAD` adds only
  the two r1 files (r0, its draft and the r0 review unedited). r5 blob at HEAD `f978eeb6b411…`; r5
  `K5_COVERAGE_COMPLETE=false`, m1/m2/m3 open `[]`, m5 and union open `[[306,309]]`. No `*COVERAGE_MAP_R6*` tracked.
  `refs/c12r2/cell306-target-consumed → dec92e09` (commit), `refs/c12r2/cell306-pending-result → 0ac46b3d` (blob).
  `b83cc6f5` blob, `def4e453` commit. `refs/heads/main c123b9bb`, `refs/remotes/origin/main 1cb45382`. No remote copy
  of the branch. All as r1 §0 states.
* **Floor r2.** `FLOOR_R2_SPECIFICATION.md` (all 261 lines) and the config fields above.
* **§R sources** (point 0) and **evidence-map claims** (point 1): C2 adjudication, OND C2, R_STAGE_DESIGN; C3
  adjudication; C4 adjudication; C5 adjudication; C6 adjudication and OND C6; C7 OND and README; C8 README, erratum,
  adjudication; C9 README, `C9_ALPHA_LEVER.json` :43, REVIEW_C9_STOP; C10 README; C11 README and adjudication header;
  C11R execution review :105–110; C11RD review verdict lines; C12-R2 adjudication; Campaign B README; C1 README;
  `THEOREM_TCT.md`; `MEASUREMENT_NOTE.md`; `K5_TARGET_AND_THIRD_ORDER.md` :91; readiness audit README :100–118;
  `K5_STATUS.md` :40–57; `p5y_k5b_independent_countersignature/README.md` :222–238.
* **Sweep.** Verdict-bearing tokens of every review, adjudication, erratum, stop and status file in
  `p5y_k5_tail_*` (except the audit itself), `p5y_k5_m5_tail_closure`, `p5y_k5_order3_readiness_audit`,
  `p5y_k5_remaining_cell_closure`; `git grep` for `K5_INCONCLUSIVE`, `SR K5`, `all_four_together`; `git log --all`
  since 09-19 for SR K5 / K1 status commits.

---

## BLOCKERS

**None.** No finding below makes r1 unfit to hand to the user as the basis for authorizing the recommended action
(architecture D). Every factual defect I found either leaves every recommendation label unchanged or, once
corrected, strengthens D. The closeout draft has defects that must be repaired **before it is frozen** (N4). None
makes it unusable, and the draft itself requires its own freeze review before anything binds (draft :5–8).

---

## NOTES (non-blocking)

**N1. The D-over-C0a argument is right in outcome but oversold in three places.** Each must be corrected in the
handover to the user.
* **(a) Information gain is mislabelled.** §10 :610 lists D's "Information gain: everything known is recorded, and
  nothing is foreclosed". That is preservation, not gain: D produces **no** new information. The r0 review asked for
  C vs D "on information gain alone" (r0 review :443). §7 :538–545 concedes C0a "buys one narrow, conditional
  mathematical answer" and then decides "on the remaining criteria". The honest statement is: **on information gain
  alone C0a is ahead (narrowly); D is chosen on governance simplicity, temporal integrity and compute, and because
  C0a's information does not need K5 to stay open (§7 :541–542) and can follow D as research.** That argument is
  valid; the §10 bullet is not.
* **(b) D's governance cost is understated.** §7 :534 and §10 :614 say "one adjudication plus one review". The draft
  itself requires the frozen text to pass its own review (draft :8) and then two further reviews (draft §11
  :114–116, adjudication plus adjudication review). D is therefore a freeze plus three fresh-context reviews. That is
  comparable to C0a's near-term "a freeze plus ≥ 2 reviews now" (§7 :509). The margin on the deciding criterion
  (§7 :544 "Governance simplicity and defensibility decide") is smaller than stated. D still wins, because C0a has
  no K5 consequence without U1–U3 (§7 :501–502).
* **(c) The U3 "temporal-integrity liability" is overstated.** §7 :503–505 likens a future floor extension to C5's
  post-hoc gate and C8's rule 1. But C5's gate was written by an author who "knew the answer to six significant
  figures" (C5 adj :71–73). A floor extension frozen before any RSO/R-asm evaluation would know only C8's
  atom-constant factors, not the new quantity. Floor r2 itself was frozen with disclosed knowledge of the historical
  306 figures (spec §11 :256–261). And r2 **anticipates** exactly this step for 307–309: "Any future campaign concerning
  them needs its own instruction and … freezes any further replacement before recomputing" (spec :202–203; config
  `scope.cells_307_309`). U3 is the ordinary prospective path r2 prescribes. It is a governance step, not a
  temporal-integrity defect.

**N2. The §6 structural finding (:485–492) contains two inaccuracies.** Neither changes a label.
* **(a) "It also needs U1" is false for R-I2-alone.**
  * I2 is the C11R/C11RD exact-rational certifier. Its independent path excludes numpy and flint (spec §7 :151–153).
  * C11R executed on the local Mac: `REVIEW_C11R_EXECUTION.md` :105–110 records `cost_host` node
    `suzhedeMacBook.local`.
  * So R-I2-alone needs no provisioned certifying host. It needs no U3 either (it is r2-conformant), and its P3
    standing is "as R-α" (§6 :380).
  * Its REJECT still stands, on the other two limbs of §10's conjunction: result-chasing HIGH, and not
    evidence-supported ("no evidence S_I2 is tighter", §6 :378).
  * §10 :617–621 should say that R-I2-alone fails RC and evidence, not U1.
* **(b) The "LOW result-chasing" list is inconsistent with r1's own ratings.**
  * The list is "R4, RSO theory, R-asm theory, B1, X308".
  * But R-asm theory is rated LOW–MEDIUM (§6 :445; §9 :591). This is despite "same basis as RSO", and RSO theory is
    LOW (:433).
  * B1 is LOW–MEDIUM (§6 :414).
  * Either rate R-asm theory LOW, which is what the §R N10 disposition claims (:57, "rated like RSO's"), or drop it
    from the LOW list. As written, N10 is resolved in words but not in the ratings.

**N3. Omitted negative evidence on R4 (real order-3).** This changes a scientific-risk rating, not a
recommendation.
* **What r1 says.** §6 R4 (:382–393) rates scientific risk **MEDIUM**, citing only "Perfect order-3 closes all four
  (diagnostic)". §9 (:587) gives success uncertainty "medium". The committed evidence says the *realistic* reach is
  much narrower.
* **C2's own R-stage design, §2.**
  * Source: `p5y_k5_tail_c2_closure/phase_r/R_STAGE_DESIGN.md` :27–40, cited by r1 as E09 but not for this.
  * It models a real candidate on adopted Campaign-A evidence. That modelling is "precisely what invalidated Campaign
    B's route T2" (:29).
  * It publishes C2-supply critical ratios of 37.32 / 23.26 / 14.16 for cells 307 / 308 / 309, against an adopted
    s_G/s_H range of 34.79–80.50 (:36–38).
  * It says 307 is "the only still-open cell inside the adopted range" (:77), and inside it only marginally
    (:62–67).
* **Campaign B.** Its T2 (a real order-3 candidate at the tail) "closes 0/5 — INFEASIBLE" with Campaign A's
  order-3 scale (`p5y_k5_m5_tail_closure/README.md` :22–26). E07 records only "STOPPED".
* **Consequence.**
  * On committed evidence, R4's reach is plausibly 307 alone. Its scientific risk is HIGH for 307 and at least HIGH,
    arguably VERY_HIGH, for 308–309.
  * The label stays DEFER (guard DENY), and the correction strengthens D.
  * But the closeout's ranked research item "R4 after N1, N5 and N7" (draft :154; r1 §7 :526) must carry this
    evidence.

**N4. Closeout draft: repairs required before any freeze.** The draft is complete against every required heading
(point 10). It is not freezable verbatim.
1. **Allowed inputs are too narrow** (draft :46–48: "committed artifacts only: E01–E30 of the route audit r1").
   * A final adjudication that must confirm each disposition is "no stronger" than the evidence (:28–29) needs
     licence to read **any** committed artifact, subject to the §3 forbidden list.
   * Otherwise it cannot find what r1 omitted. Examples: the K5-B countersignature (item 4); C2 R_STAGE_DESIGN §2
     (N3); C8 Condition 6 (N6).
2. **P4 contradicts the rest of the draft.**
   * P4 (:82) requires "the value-free leak scan (the inherited D1/D2 hash sets)". That means executing a scanner.
   * But §3 (:52) forbids "any campaign code … execution", and §10 (:107) says "No code is involved".
   * The hash-set files and the scanner are not bound by path/blob. The candidates are C11RD's
     `…/POST_WRITE_LEAK_SCAN.json` family, which I did not open.
   * Bind them and carve out that one scanner, or replace P4 with a document-only rule: the closeout carries no
     D1/D2-derived number.
3. **Outcome vocabulary.**
   * E01's rule (`K5_TARGET_AND_THIRD_ORDER.md` :91) is K5-level: "unresolved cells ⇒ `K5_INCONCLUSIVE`". It is not
     a per-cell "outcome class".
   * The draft's :137 ("unresolved cells in the outcome class `K5_INCONCLUSIVE`") and the verdict tokens
     `K5_PARTIAL_CONFIRMED/REJECTED` (:114) reinterpret it.
   * State explicitly that the closeout confirms the CUSUM **status** PARTIAL.
   * State that it issues no K5-level terminal verdict, because SR K5 is NOT STARTED and K5 as specified covers SR
     cells 0–294 and CUSUM cells 0–309 (E01 :89).
   * Or, if a CUSUM-level `K5_INCONCLUSIVE` is intended, say so and name it.
4. **Missing consequences and restrictions.**
   * **P5Y consequence.** State the P5Y consequence of a *final* CUSUM PARTIAL: "P5Y final assembly waits on SR K1,
     SR K5 and CUSUM K5" (`K5_STATUS.md` :55–57). The user authorizing "final" should see it.
   * **Countersignature failure semantics.** Carry them: no failed recurrence, `K5_INCONCLUSIVE` or failed cell
     "(including cell 309 or the m = 5 tail) is evidence against H3a"
     (`p5y_k5b_independent_countersignature/README.md` :236–238). "PARTIAL is not unclosability" (:139) is necessary
     but not the whole restriction.
5. **The proposed 307 scope statement is false as worded.**
   * It reads: "No certified route evaluated" (:39).
   * In fact, certified supplies were evaluated at 307 and did not close it: C2 D4 (C2 adj :48, positive Γ) and C3
     D′ (C3 adj :349). r1's own dossier lists 307 FAILED items (:244–247).
   * Replace it with: "no route that closes 307 has been certified".
6. **The 308 scope statement carries only half of C4's binding wording.**
   * It has "operator-level route not excluded" (:40).
   * It omits C4 Condition 3's binding counterpart. That is: "nothing licenses 'cell 308 is closable'", with 18.2× on
     (A1, A2) at the MC Λ₃₀₈ (C4 adj :534–537).
   * It also omits the 2,000,000-path MC evidence (C4 adj :510–512). r1's dossier has both (:278–281); the proposed
     disposition does not.
7. **The ranked research items are incomplete and unranked by any stated basis** (draft :151–155; r1 §7 :523–527).
   * The list is RSO, R-asm, R4 and B1.
   * It omits three items:
     * R5, the sup-norm channel. C4 calls it "the dominant channel at cell 309" (C4 adj Condition 7(b), :556–557).
       C5 ranks it (b) (C5 adj :617–619).
     * R-E1g. C5 ranks it (c) (:618–619), and it was C8's selected route.
     * R-F1′, the only r2-conformant DEFER.
   * All of these appear in r1 §9 as DEFER or INSUFFICIENT_EVIDENCE.
   * Either list every DEFER/INSUFFICIENT_EVIDENCE row, or state the ranking rule. N3 applies to R4's entry.
8. **Say "current", not "final".** "final coverage map" (:27) and "final authoritative map" (:136) sit badly with the
   reopening rule (§16). Say "authoritative" or "current".
9. **SR K5 re-check across refs.** The SR K5 status is branch-local (`K5_STATUS.md` :52, 09-19). Later SR K1 work
   exists on other refs, for example da79fe1f (2026-09-26, "READY for independent adjudication; K1 not decided").
   * I found no ref stating any SR K5 progress, so "NOT STARTED" is still accurate.
   * But P1 and P3 should direct the adjudicator to check all refs, not HEAD only, and to record that the "needs SR K1
     records" rationale may be stale.

**N5. Clause mismatch in the r2-adoptability thresholds** (a fortiori, so conclusions hold).
* **r2's adoption quantity** is "C2's frozen consumer path … `c2_d5_forecast.py` blob 18403dbe … and the
  k5b_literal direct clause" (config `quantity_compared.adoption_quantity`). That is the frozen K5-B direct clause.
* **C8's factors are under the C5-T clause.** C8 uses them (1.096007× to close, 1.370009× to be adoptable, …)
  "under the authoritative C5-T clause" (C8 README :43–54).
* **Where r1 uses the wrong clause.** R-α's r2 column (§6 :343–344; §9 :583) compares the C9 projection against the
  C5-T figure, and the 306 dossier quotes "1.067071×" without a clause label (:223).
* **Which figures are r2-relevant.**
  * C8 Condition 6 (C8 adj :482–484) says the three published 306 margins and requirements belong to different
    clauses (1.1277 ↔ 1.108452, …, 1.171431 ↔ 1.067071).
  * C12-R2 adj :494–496 calls them unreconciled.
  * The r2-relevant 306 figure is C2's 1.1277 (C2 adj :476).
* **Why the conclusions survive.**
  * C5-T is the tighter transport, so every "not adoptable" statement holds a fortiori.
  * 306 is barred regardless.
  * But r1's "1.098807× vs 1.096007× is thin" (§6 :340) overstates R-α's closure prospects under r2's own
    quantity: the base clause there is not C5-T. Label the clause wherever a C8/C9 factor is compared to r2.

**N6. Other omitted or mis-stated evidence** (none changes a classification).
* **306-e (:319) says "C8 rule 1 still bars it (E1)".** But C8's erratum E1 says rule 1 "embeds a false premise". It
  recommends that "a successor gate should state rule 1 as … a cell passing the clause but failing the floor still
  needs information" (`ERRATUM_C8_GATE.md` :6–31). 306-e is barred by the fixed fact "no new 306 supply" alone, so
  drop the rule-1 clause.
* **The 309 R-asm lever is not current.** The 309 dossier (:298) and R-asm (:439–440) cite `all_four_together`
  0.6076 %. This is correctly labelled "vs C4's floor", but the exclusion now in force uses C7's floor. No committed
  figure gives R-asm's requirement against C7's floor. The sup-norm lever went from 2.056 % to 19.612136 % between the
  two floors (C8 adj :384). Say so explicitly, so that "voids the 309 exclusion" (:440) is not read in the present
  tense.
* **E21's status is thin.** E21 (C10) gives the status as "adjudicated". The verdict is ACCEPTED_WITH_CONDITIONS,
  "repairs recorded-but-absent, now landed" (ec969db1).
* **The "Condition 10 binds" wording (§4 :200) is stronger than Condition 10's text.** The text is "no P3 object may
  be adopted as new scientific evidence" (OND C6 :20). It is also stronger than r1's own U2/KG-U2 framing (a
  governance ruling is needed, :480–481, :568–569) and than §15's "inferred" (:668–670). Treat it uniformly as an open
  admissibility question needing a ruling (U2). That is what the r0 review found ("an open governance question",
  :153).
* **The K4 ref in §14 (:662–663) is stale.**
  * r1 says `p5y-k4r1-nearzero-successor 5d33363c`.
  * The ref moved to 93d82c87 at 20:45:07 (reflog), before r1 was committed at 20:47:39.
  * This is immaterial, since K4 is unrelated and untouched, but a "recorded" ref value should be correct.

**N7. The prescribed final sentence needs its reading stated** (see point 12).

---

## 0. Were r0-review B1–B3 and N1–N13 genuinely resolved?

**§R spot-checks, 16 sources verified at the cited lines:**

| # | §R cite | result |
|---|---|---|
| 1 | floor-r2 config `rule.chosen_supply_restriction`, `quantity_compared.adoption_quantity` (blob 18403dbe; "every other input unchanged"), `quantity_compared.supplies.everything_else` (TC-T premises incl. zero order-3 candidate, σ3/σ4, cells.json), `fail_closed[3]` | ✓ verbatim |
| 2 | r2 spec §9 :202–203 (C2 Condition 1; freeze before recomputing) | ✓ |
| 3 | C4 adj §6 table :229–235 | ✓ |
| 4 | C4 adj Condition 1 :522–524 | ✓ |
| 5 | C5 adj Condition 10 :607–609 (three non-R-stage oracles) | ✓ |
| 6 | `ERRATUM_C8_GATE.md` E3 :39–44 (six levers; 0.6076 %) | ✓ |
| 7 | C4 :256–259 (ranks RSO first); C5 adj Condition 11 :615–622 (E2, A1, E1, B1; RSO "costed alongside (b)"); C8 adj :174–176, :385 | ✓ all |
| 8 | OND C6 :17 (Condition 7); C6 adj :292 (host provisioning "not a parenthesis") | ✓ |
| 9 | C6 adj §2 :168–185 (P3; `admissible_for_NEW_scientific_reuse: false`; `already_adopted_exception`) | ✓ |
| 10 | OND C6 row 10 (:20), C6-N4 (:37–39), C6-N5 (:40–41), C6-N1 (:28–29) | ✓ |
| 11 | `MEASUREMENT_NOTE.md` :33–37 ("neither gate directly"); :17–29 (1350.2–1359.6 CPU-s; ≈ 1.87 CPU-h); :3–4 (vultr-02, Aux5 venv, scipy 1.18.1) | ✓ |
| 12 | C2 adj §K :501–506 (three discharge routes) | ✓ |
| 13 | C4 adj :508–512 (verdict), :527–533 (Condition 2), :534–537 (Condition 3) | ✓ (verdict wording is at :510–512) |
| 14 | `THEOREM_TCT.md` :122–125 (`p2`, `rad_r`) and :14 (Ĝ = order-3 candidate of F) | ✓ |
| 15 | C4 §8 :288–290 (307: A0 not the blocker) | ✓ |
| 16 | C5 adj :39–42 (`x_lo > 0` fails at cell 0); `C11RD_R1_QUALIFICATION_REVIEW.md` line 2 `QUALIFICATION_REJECTED` (commit 89330534); OND C6 row 1 ("the INPUTS only. Never the gain.") | ✓ |

**Per finding:**

| r0 finding | resolved in r1? |
|---|---|
| B1 adoption | **Yes.** RSO, R-asm, R4, R5 and B1 are labelled closure-only (§6 :328–332, §9). Any adoption path is a user-instructed floor extension (U3, §6 :482–483; KG-U3 :573–574). R-α is held to the same standard (§6 :343–344). |
| B2 premises | **Yes.** The exclusivity (B2a), "three independent" (B2b) and "no host" (B2c) claims are withdrawn or corrected (§R :43–45; §9 :590 "ranked first by C4 only"). The C vs D re-argument is only partly on information gain alone (N1a). |
| B3 data path | **Yes.** P3 / Condition 10 / C6-N4 / C6-N5 are in E17 and §4 :196–201, and the trust surface is in E07a. KG-U2 and KG-T (:568–572) are the gates B3 asked for. The "binds" wording is overstated (N6). |
| N1 | Yes. 306-f is GOVERNANCE_BARRED (:320), and the order-3 NOT APPLICABLE entry is removed. |
| N2 | Yes (:278–284; X308 VERY_HIGH, REJECT). |
| N3 | Yes (309 FAILED within scope :300–302; 307/308/309 F1′ UNAVAILABLE). |
| N4 | Yes (E07a; §6 :400, :429). |
| N5 | Yes, as an unreconciled inconsistency (U1 :477–479). |
| N6 | Yes (§6 RSO :420–423; Ĝ_e). |
| N7 | Moot (the RSO draft is superseded). |
| N8 | Yes (C0a, §7). |
| N9 | Yes (:422). |
| N10 | **Partly.** The 0.6076 % figure is cited, but the ratings are not aligned (N2b). |
| N11 | Yes (E24, E17). |
| N12 | Yes (:425–426). |
| N13 | Yes. |

## 1. Completeness of the evidence map

**Further spot-checks** (beyond §R, all against HEAD; ✓ = text and numbers match):

| # | claim | where | result |
|---|---|---|---|
| 1 | E01 decision rule | `K5_TARGET_AND_THIRD_ORDER.md` :91 | ✓ |
| 2 | E03 `K5_INCONCLUSIVE` option | readiness README :111–112 | ✓ |
| 3 | E04 SR K5 NOT STARTED; P5Y waits on CUSUM K5 | `K5_STATUS.md` :52, :55 | ✓ |
| 4 | E08 2.252903 → 2.101597, 6.716 % | C1 README :29 | ✓ |
| 5 | E07 1.071×/1.362×/1.771×/2.253× | Campaign B README :37 | ✓ |
| 6 | E09 ≈0.44 / ≈1.3 CPU-h, caps 3/6, N1/N3/N5, "estimate … not a certificate" | R_STAGE_DESIGN :76, :81, :83, :87, :95–102 | ✓ |
| 7 | E11 Γ(306) −0.030469257709306738; Γ_deg +0.029163293; margin 1.1277; D′ −0.036198/1.1555 | C2 adj :47, :65, :476–478, :497–498 | ✓ |
| 8 | E14 knockouts +0.039568 / +0.092812; 5.2185 / 4.3752 | C3 adj :350–351 | ✓ |
| 9 | E15 "not a statement that cell 309 is unclosable" | C4 adj :503 | ✓ |
| 10 | E16 1.211–1.295 %, "closes nothing", post-hoc gate | C5 adj :69–75, :135–136 | ✓ |
| 11 | E18 3.586306094 / 9.7933 % | OND C7 :32–33; C7 README :15 | ✓ |
| 12 | E19 R3 ceilings/floors 6.262333/3.734070, 4.442851/3.512734, 3.266416/3.586306; R5 19.612136 % | C8 adj :382, :384 | ✓ |
| 13 | E19 per-cell factors 1.096007/1.370009, 1.438423/1.798029 | C8 README :53–54 | ✓ (clause: N5) |
| 14 | E20 α 1.098807–1.137406; ten sub-blocks at 6/5, margin ≈0.16; pin | C9 README :29–39, :63, :104 | ✓ |
| 15 | E20 887 CPU-s; "~31 CPU-minutes"; STOP_PREMATURE | `C9_ALPHA_LEVER.json` :43; REVIEW_C9_STOP :106, :357 | ✓ |
| 16 | E21 "next purchase … not an α" | C10 README :95 | ✓ |
| 17 | E22 EXECUTION_INVALID; "within 31%" | C11 README :3, :123 | ✓ |
| 18 | E25 F1′ availability; "does not revisit" | r2 spec :193, :224 | ✓ |
| 19 | E28 scope wording (non-certification, not disproof; base TRUE, F1′(d) FALSE, F2 FALSE) | C12-R2 adj :380–400 | ✓ |
| 20 | commit hashes and dates E01–E30 | `git log -1` on each | ✓ (E04's 5a8c194d is "coverage map r2", consistent) |

**Verdict:** transcription is accurate. The coverage gaps do not change any label:
* C2 R_STAGE_DESIGN §2 and Campaign B's T2 finding, against R4 (N3);
* the K5-B countersignature failure semantics (N4 item 4);
* C8 Condition 6's clause reconciliation (N5);
* C11R's execution host (N2a);
* C10's condition status (N6).

## 2. Omitted negative evidence

**Material to a rating, not to a label:**
* R4's modelled reach (R_STAGE_DESIGN §2 :27–40, :62–67, :77) and Campaign B T2 "0/5 — INFEASIBLE" (N3).

**Minor:**
* C8 Condition 6 / C12-R2 :494–496, the unreconciled clause-specific 306 margins (N5);
* the K5-B countersignature :236–238 (N4 item 4);
* C4 Condition 3's "nothing licenses 'cell 308 is closable'", which is absent from the draft's 308 disposition
  (N4 item 6);
* C8 erratum E1's successor-gate recommendation (N6).

**Correctly carried:**
* C1 MARGINAL;
* Campaign B STOPPED;
* C3 REJECTED;
* C4 scope and §6;
* C5's post-hoc gate and `x_lo`;
* C6 no host, "A1 harder", P3 / Condition 10 / N4 / N5;
* C8 E1 and E3;
* C9 blocked and STOP_PREMATURE;
* C11 EXECUTION_INVALID;
* C11R AGREEMENT_INSUFFICIENT;
* C11RD's first QUALIFICATION_REJECTED;
* C12 and C12-R1 rejections;
* the C12-R2 disagreement;
* r0's rejection.

**No omission I found would change a PROCEED / DEFER / REJECT / INSUFFICIENT_EVIDENCE label.** The one that
changes a rating (N3) moves R4 further from viability, which strengthens D.

## 3. FAILED vs UNKNOWN vs UNAVAILABLE vs NOT APPLICABLE

Correct per cell:
* **306.** FAILED: F1′(d), F2, D′, and the C12/C12-R1 process failures. UNKNOWN: single-implementation margin ≥ 1.25,
  I1/I2 attribution, real order-3. NOT APPLICABLE: Λ exclusion.
* **307.** FAILED: C1, Campaign B, C11. UNKNOWN: routes never attempted. UNAVAILABLE: F1′.
* **308.** UNKNOWN: status per C4's verdict wording. UNAVAILABLE: F1′.
* **309.** FAILED within scope: the uniform-A0 family, with scope stated. UNKNOWN: everything outside scope.
  UNAVAILABLE: F1′.

The C12-R2 result is correctly non-certification, not disproof (:210, :323–324).

The only class error is in the **draft**, not in r1's dossiers: "No certified route evaluated" for 307 (N4 item 5)
contradicts r1's own FAILED list.

## 4. Result chasing

* No route, parameter or threshold is selected from target-proximity numbers.
* "Closeness of +0.005159 to zero is not used" (§1 :93), and I found no use of it.
* R-α, R-I2-alone and Floor-307 are rejected for fitting known factors.

**Is the switch to D itself outcome-driven? No.**
* Between r0 and r1 no target information was generated: the diff adds only two documents, and §12 declares zero
  evaluations.
* The switch is driven by a governance fact surfaced by the r0 review. r2 binds the adoption quantity to C2's
  consumer path, so every low-RC route is closure-only.
* D produces no scientific result that could be chased, and it forecloses nothing (§16 reopening rule).

**One residual caution.** r1 declines the route the r0 review described as acceptable: C with an explicitly labelled,
pre-frozen floor extension (r0 review :433–435). It declines partly by overstating U3 as a temporal-integrity
liability (N1c). That is conservative, not chasing, but the handover should not present U3 as tainted.

## 5. Fixed 306 facts and prohibitions

**Respected:**
* The sealed values are quoted, never recomputed: −0.030469257709306738 and +0.005159101140006536.
* CELL306_NOT_ADOPTED stands, and 306-a…g are all REJECT.
* No new 306 supply, no r6, and r5 is unchanged (blob verified).
* The refs and forensic objects are retained.
* No D1/D2 value appears in any text I read.

**Floor r2.** r1 applies r2's `fail_closed[3]` and adoption quantity to 307–309 through the `standing_floor` clause.
r2 also says it "makes no statement about their closure or adoptability" (config `scope.cells_307_309`). r1's reading
is the conservative one and is not a reinterpretation. It should cite `standing_floor` explicitly as its basis
(E25 does, :172).

## 6. Are 307–309 routes prospective and correctly classified?

* **Prospective:** yes. Nothing is evaluated, and every route is a proposal with its prerequisites named.
* **The "r2 adoptability" column, checked against the config and the spec:**
  * **Closure-only is correct for RSO, R-asm, R4, R5 and B1.** Each changes something the adoption quantity fixes
    ("every other input unchanged … TC-T premises (zero order-3 candidate, sigma3/sigma4), cells.json"):
    * RSO: the consumer term;
    * R-asm: σ3/σ4/Env4/f_G;
    * R4: the zero order-3 candidate;
    * R5: the adopted K1 stack's sup inputs;
    * B1: cells.json and new K1.
  * **r2-conformant is correct for R-α, R-E1g, R-F1′ and R-I2-alone.** Each is a single-implementation constant set
    through Lemma Dv′ r2.
  * **X308 is exclusion-only:** correct.
  * **Caveat:** the thresholds used are C5-T-clause figures, not r2's clause (N5). The conclusions hold a fortiori.
* **The structural finding (:485–492):**
  * its substance holds;
  * "It also needs U1" is false for R-I2-alone (N2a);
  * the "LOW result-chasing" membership is inconsistent with r1's own ratings (N2b).
* **Scientific risk:** R4's MEDIUM is not supported by committed evidence (N3).
* **Labels:** none changes.

## 7. Independent motivation claims

* **Corrected:** "ranked first by C4 only" (§9 :590; §R B2b).
* **The dependence of C5 and C8 on C4** is acknowledged.
* **Ancestry:** C4's recommendation (e12a09e8) is an ancestor of the C12 freeze b9ffc87f (`merge-base --is-ancestor`).
* **RSO's reach** is narrowed to `A0·f_H` of `A0·p2` (:420–423), consistent with C4 §6 and TC-T :125.
* **RSO's 307 motivation** is withdrawn per C4 §8.
* No residual overstatement of motivation found.

## 8. Information boundary and corrected gates (§8)

**Sound.** The additions are what the r0 review asked for:
* KG-U1: host as a separate user decision;
* KG-U2: an admissibility ruling before any Stage-1 freeze;
* KG-T: a posteriori re-certification of pointwise quantities with outward arithmetic, because scalar identity does
  not certify function values;
* KG-U3: floor extension frozen and reviewed before Stage 1;
* cost that includes the new evaluation;
* KG2 as a soundness obligation.

"Calibration on any real cell" and "anything computed on replayed tail candidates beyond identity" are correctly
load-bearing.

**One tightening.** "cost of the replay" (:558) as safe preflight should read "the committed measurement (E07a) or
a 305-only replay". Replaying 306–309 regenerates tail candidates, which is adjacent to the load-bearing boundary. The
section is expressly not recommended now, so this does not bear on D.

## 9. Adoption-criterion handling

**Correct and honest in substance.**
* Every closure-only route is labelled as such.
* Adoption requires a user-instructed floor extension frozen before any recomputation (C2 Condition 1; r2 spec
  :202–203).
* R-α is judged by the same r2 standard and found closure-only in expectation.
* The closeout itself adopts nothing (draft §12).

**Two defects:**
* the clause mismatch in the thresholds (N5);
* the portrayal of U3 as a temporal-integrity liability, where r2 prescribes it as the ordinary path for 307–309
  (N1c).

## 10. Is the closeout draft freezable, complete and non-overreaching?

**Complete.** Every required heading is present:
* scope and cells (§1);
* question (§2);
* allowed and forbidden inputs (§3);
* implementations, constants and supply (§4);
* target (§5);
* safe preflight (§6);
* kill gates (§7);
* load-bearing boundary (§8);
* exactly-once (§9);
* qualification (§10);
* review (§11);
* adoption criterion (§12);
* stop conditions (§13);
* coverage consequence (§14);
* historical preservation (§17).

Publication (§15), reopening (§16) and compute (§18) are also present.

**No computation anywhere:** ✓.

**SR K5:** correctly out of scope and not decided (§1 :20–21). The re-check should span refs (N4 item 9).

**"PARTIAL is not unclosability":** present (:139). It is incomplete without the H3a non-refutation rule
(N4 item 4).

**Overreach:**
* "final" coverage map (N4 item 8);
* the per-cell use of `K5_INCONCLUSIVE` (N4 item 3);
* the false 307 statement (N4 item 5).

**Freezable after N4 items 1–9.** Items 1–3 are structural (inputs, P4/code contradiction, vocabulary). Items 4–9
are content.

## 11. Compute statements

**Honest:**
* D and the closeout: zero compute (§18);
* replay ≈1350 CPU-s per cell and ≈1.87 CPU-h, from committed measurement;
* C9's 887 CPU-s vs "~31 CPU-min", flagged as unresolved;
* R4's ≈0.44 / ≈1.3 CPU-h, labelled as a forecast;
* R-E1g "unknown";
* B1 "unmeasured".

**Unsourced but harmless:** X308 "minutes to hours".

No invented measurements, and no success percentages (§9 :596).

## 12. Is D over C/C0a justified on the stated criteria, and is the final sentence accurate?

**D over C0a: justified, but by a narrower argument than §7/§10 present.**
* **On information gain alone, C0a is ahead.** D adds no information (N1a).
* **On governance simplicity** the near-term costs are comparable: D is a freeze plus three reviews, C0a a freeze
  plus two or more (N1b).
* **What tips it to D:**
  * C0a has no K5 consequence without U1–U3 and a full chain.
  * C0a's lemma can be pursued as research after D without loss, since D forecloses nothing.
  * D has perfect temporal integrity, zero compute and a document-only chain.
* **Chance of CLOSED is not used.** The decision is not made on likelihood of CLOSED, and I found no likelihood
  estimate driving it.
* **A over D and B over D** are correctly dismissed: they inherit C's route problem, and B adds multiplicity.

**The final sentence.** "No scientifically justified prospective K5 campaign remains; await authorization for final
K5 PARTIAL adjudication and publication closeout."

* **Read literally, it is a mild overclaim.** r1 does not show that no *scientifically* justified campaign remains.
  It DEFERs six routes and lists one as INSUFFICIENT_EVIDENCE rather than rejecting them. It calls RSO and R-asm
  theory legitimate "research items" (§7 :523–527, §10 :623–624). R4 is preregistered, LOW result-chasing, and
  barred by guard DENY, not by science.
* **What r1 actually establishes** is narrower: **no prospective K5 campaign is justified on the instructed criteria
  under current governance.** No route for 307–309 is at once:
  * r2-adoptable;
  * low in result-chasing risk;
  * evidence-supported;
  * free of the user-level decisions U1–U3.
* **Of the two permitted sentences, it is the only one consistent with r1.** The other ("Await authorization to
  freeze the proposed prospective campaign.") would be false, because r1 proposes no campaign.
* **It is accurate only with that reading stated.** The handover should say so in the line immediately before it, for
  example: "'scientifically justified' here means justified on the instructed criteria under current governance;
  RSO/R-asm theory, R4 (after N1/N5/N7), R5 and B1 remain deferred research items, reopenable only under fresh
  authorization."

---

## What would change the verdict

**To ROUTE_AUDIT_REJECTED**, any one of:
* evidence that any number r1 quotes was computed rather than quoted, or that any 306–309 quantity was evaluated
  after c5324a78;
* a committed artifact showing a route for 307–309 that is simultaneously:
  * r2-adoptable under the frozen adoption quantity;
  * rated LOW result-chasing on a basis r1 applies elsewhere;
  * supported by committed evidence;
  * free of U1–U3.

  That would falsify the §10 conjunction on which D rests. R-I2-alone comes closest: it needs no U1 (N2a). It still
  fails on result chasing and evidence. If committed evidence showed S_I2 tighter than S_I1 at 307–309, that would
  change my assessment;
* the handover presenting the draft as freezable verbatim, or presenting D's information gain or governance cost as
  §10 states them (N1a, N1b);
* the handover ending with the D sentence without the qualification in point 12, if the user's instructions treat
  "scientifically justified" literally.

**Conditions of this acceptance.** Before the closeout is frozen:
* the N4 repairs are made;
* N2 and N3 are corrected in the closeout's recorded structural finding and research items.

Neither needs a re-audit, because both move nothing toward C.
