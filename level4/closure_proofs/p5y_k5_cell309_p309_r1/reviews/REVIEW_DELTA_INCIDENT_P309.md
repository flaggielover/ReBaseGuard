# Incident-independence review of the rev. 2c delta (condition C2), P309 package 1, formal campaign p5y_k5_cell309_p309_r1
DELTA_INDEPENDENCE_ACCEPTED

**Standard.** The standard is **temporal and parametric independence only**, as in the original review.

**Conditions.** D1–D8 are in §7. D2, D4 and D5 must be met before the freeze.

**Reviewer.** I am the independent incident-independence reviewer, the author of
`reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md` (39ed662c) and `reviews/REVIEW_U2_CHECK_P309.md` (73200812). I did not
produce or coordinate the campaign.

**Brief.** `reviews/BRIEF_DELTA_INCIDENT_P309.md`, committed at 08acd6a2 and pushed before it was issued (C5 respected).

**Reviewed state.**
* HEAD was 3294e169 when I started. One commit landed during the review: 4f51a2df (03:43:18Z). It adds freeze
  tooling, a no-placeholder statement and **erratum E1-6**. I cover it in §2.
* The delta documents are `governance/P309_REV2C_AMENDMENTS.md` (A1–A19) and `fc2/FC2_SPEC_R2_ERRATUM_1.md`
  (E1-1..E1-6).
* The driver `code/p309_driver.py` is unchanged since 6522db10.

**Written.** 2026-09-30, 03:39–04:00Z.

---

## 0. Reads, runs and ledger

**Scratch ledger:**
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/deltareview/DELTA_LEDGER.jsonl`.

**Reads.**
* **Committed FNS/RNS files, read with `git show HEAD:…`.** The working tree carries uncommitted edits by others; I
  did not rely on them.
* **Cell-307 file.** `rlr307_driver.py`, only through `code/code_skeleton.py` (masked), filtered to its job-order and
  cap lines.
* **Recovered briefs.** `governance/briefs_recovered/`: I checked all 25 sha256 values and read items 1–3 and the
  sandbox clause of item 23.

**Runs.** One reviewer scratch script, `spotcheck_masked_grep.py`, a static spot-check of the coordinator's masked
grep (§3). It prints only counts, and contexts with every surviving number re-masked. It is **declared here after it
ran**.

**Nothing else.**
* No kernel run and no evaluation.
* No git write.
* No file modified except this one.

---

## 1. Verdict in brief

* **Temporal.**
  * All nineteen amendments and the six errata postdate every recorded 305–309 exposure: the last coordinator
    exposure to a value was 309R1-02 (daa1bd64, 13:06:42Z on 09-29).
  * They postdate every exposure-ledger row since 39ed662c. None carries a value; see §3.
  * They precede any 309 Stage-1 quantity. None exists: 169 execution-ledger lines, 0 target evaluations, 0 proxies,
    no band drift, max |e| = 37/32.
* **Parametric.**
  * No Stage-1 scientific parameter changed: ladders, indices, numerics, hull rules, cover, the 48/12 CPU-h Stage-1a
    budget, the 21 600 s Stage-1b start threshold, failure mapping, fallback, outcome table, strictness. The freeze
    generator at 4f51a2df carries the rev. 2b values.
  * **One new numeric parameter** exists: the Stage-1b per-job CPU limit (A5). It was set with no Stage-1b cost
    evidence for 309 or for any decoy. No QC09 run exists at 4f51a2df.
* **Direction.** Four changes move the outcome toward closure or toward a conclusive result: A4, E1-1, A6 and A5
  (ambiguous). Each has a target-free basis:
  * **A4 and E1-1** repair defects that would have made SRK or RLR unusable in band. A4 came from my U2 check §9. E1-1
    came from comparing the two independent FC2 implementations.
  * **A6** implements R3 F2.2 ("stopping … not by an exception").
  * **A5** fills a gap left by rev. 2b.

  None is tuned to a target number. Their **stated directions and bounds are partly wrong** (A5, A6) and must be
  corrected and disclosed (D2, D3).
* **New findings outside the amendment list:**
  * The recovered reader-A brief shows that the 309-specific qualitative dominance was **solicited** (D3).
  * The FC2 rev-1 brief contained a quarantine-breaching instruction that was never executed (D4).
  * A10 and A19 extend the owner's scanner ruling (D5).

---

## 2. Task 1: each change

Legend: **R** rule, **P** parameter, **M** mechanism/binding, **Q** qualification-only. **Direction** means toward or
against closure (or neutral). **Basis** gives the source; every basis below is target-free.

| id | class | direction | source / basis | finding |
|---|---|---|---|---|
| A1 QC14 → QC14′ | Q | neutral (qualification is weaker: manufactured inputs) | the quarantine forbids any evaluation for 305–309, and C2's direct clause is tail-only, so no admissible real-data rehearsal cell exists | independent. The post-grant, pre-marker historical control (A12, strengthened) remains the real-data check |
| A2 FC2 spec rev. 2 | M | neutral (refusal-only before a grant) | owner rulings 2 | independent. TEST band = the declared h3 decoy hull, a synthetic geometry, disjoint from the real band |
| A3 QC08 h5 only | Q | neutral | consequence of A2 | independent |
| **A4** Stage-1b guard | M (restores the reviewed design) | **toward closure**: without it every in-band Stage-1b job raises (`c1b_certpw` `Ctx` calls `Q.guard_drift`), giving EXECUTION_INDETERMINATE with certainty | my U2 check §9 | **independent** (details below) |
| **A5** Stage-1b per-job limit = 21 600 s | **P (new)** | **efficacy-relevant, ambiguous**, not "none" | rev. 2b left it unstated | **independent**, but the stated rationale is false (details below) |
| **A6** no post-marker wall cap | R (implementation of rev. 2b §2.5) | **toward a conclusive outcome** (removes INDETERMINATE-by-slowness) | R3 F2.2, rev. 2b §2.5 | **independent**, but the stated CPU bound is wrong (details below) |
| A7 file locations | M | neutral | push procedure check 7 | independent |
| A8 check_grant allows ledger-only record commits | M | neutral | record-first push | independent. The pre-freeze review must confirm it cannot admit a commit that changes frozen files |
| A9 grant fields | M | neutral / stricter | owner rulings 2 | independent |
| **A10** pending-ref NAME; exactly-once sites | M | neutral | owner rulings 2 plus FC6 | independent, but it **extends an owner allowance** (D5) |
| A11 `direct` via shim | M | neutral. The `direct`-internal crosscheck is vacuous for SRK; the genuine TC-T crosscheck runs first (`evaluate_srk`) | U2 check U4(i) | independent |
| A12 two-part historical control | M | against closure / neutral (stricter) | protocol §4; F-U2-3 | independent |
| A13 K1 record binding via the adopted inputs | M | neutral | U2 check U6 | independent. Control part (a) requires per-supply and provenance equality with C2 |
| **A14** proposed execution host | P-adjacent | efficacy-relevant: with CPU budgets, which certificates exist depends on host speed (R3 F2.1) | owner decision on isolation | independent (details below) |
| A15 Stage-1b decoys 297, 316 | Q | neutral | declared prospectively; guard-checked at run time | independent (D6) |
| A16–A18 QC12 additions, QC-U2, QC16 | Q | neutral / stricter | U2 check; owner rulings 2 | independent |
| A19 scanner | M | neutral | owner rulings 2 | independent (D5) |
| **E1-1** strict descendant | M (fix) | **toward closure**: prevents silent REFUSE of every in-band certificate | comparison of the two independent implementations | **independent** (details below) |
| E1-2 / E1-3 / E1-4 | M | neutral / stricter | documented differences | independent |
| E1-5 harness `--out` | M | neutral | A8 | independent |
| E1-6 alternates sandboxes (4f51a2df) | M (qualification tooling) | neutral | the shallow repository exhausted the disk | independent. Isolation is by a separate git directory and refs, and the TestContext refusal still applies |

**Specific attention (brief task 3).**

**A6 (no post-marker wall-clock cap).**
* It implements a reviewed rule: rev. 2b §2.5 and R3 F2.2 require stopping "not by an exception". It is not a new
  choice.
* The driver clears every alarm before the marker (`p309_driver.py:1052-1053`). The pre-marker `PRE_CAP_S` alarm arms
  only in non-execute modes.
* **Error.** A6's bound "6 CPU-h for Stage 1b" is **wrong**.
  * `run_jobs` is a start threshold (`:590`), and running jobs continue to their per-job limit (`:608`).
  * With A5, Stage 1b can therefore reach **< 21 600 s + 4 × 21 600 s ≈ 30 CPU-h**, not 6.
* **Wall time is unbounded.** A non-CPU stall after the marker would never end. Killing the process then yields
  CONSUMED_UNRECORDED / lost information, and so EXECUTION_INDETERMINATE.
* That trade-off is an operational matter for the pre-freeze review and the owner, not an independence issue.

**A5 (the Stage-1b per-job limit).**
* **It is a new numeric parameter.** Its rationale, "a job can never exceed the total anyway", is false under the
  start-threshold semantics of `run_jobs`. It is also the most generous limit that does not exceed the threshold.
  Stage 1a's ratio of 12 to 48 would give 5 400 s.
* **Its direction is genuinely ambiguous.**
  * A larger limit lets the d = 8 rungs finish, which gives tighter A1 and A2.
  * Under the RLR307 degree-descending order (rev. 2b §3; `:749`; confirmed in the masked `rlr307_driver` skeleton),
    it can also consume the start threshold before the lower rungs of later blocks start. That makes
    CERTIFICATION_FAILED, and hence the S_I1 fallback, more likely.
* **No target information exists that could set it.** No Stage-1b computation has ever run at a band drift, and no
  QC09 decoy has run.
* The only cost reference in the record is the committed cost class of the 307 campaign's RLR run
  (`PHASE3_ROUTE_COMPARISON.md:46`). Rev. 2b's 21 600 s already rests on that "307 precedent", and it was accepted
  there.
* **Independent**, with text corrections (D2).

**A4 (the Stage-1b guard).**
* It restores what R2 (FC5), R3 and the owner (P0-1: in-band Stage 1 over Ew) all presupposed.
* The window is not widened. Each Stage-1b hull is the outward 2⁻²⁰ hull of a sub-block of C. Because every 2⁻¹⁰ grid
  point is a 2⁻²⁰ grid point, floor₂₀(lo) ≥ floor₁₀(x_lo) and ceil₂₀(hi) ≤ ceil₁₀(x_hi). So every hull lies inside Ew,
  and the admission conditions are those of Stage 1a.
* Before A4, **rev. 2b as reviewed would have ended in EXECUTION_INDETERMINATE with certainty**, and the out-of-band
  QC09 would not have shown it.

**A1 / A3.** Both are forced and independent. A1 removes a pre-grant real-data end-to-end test that could not be
performed legally. A12 compensates in part.

**A10 (the pending-ref NAME and the exactly-once sites).**
* It has no target content.
* The owner allowed the **production marker NAME** only, and stated that the allowance must not permit "creation of
  the marker ref".
* `config/SCANNER_ALLOWANCE_P309.json` adds the pending-ref NAME, and sanctions MARKER_MUTATION inside the two
  exactly-once sites. Those sites create the marker and the pending ref, post-grant only, with
  `_assert_execute_context` first.
* That is a necessary part of the reviewed exactly-once design (package §C). It is still **beyond the letter** of the
  owner's scanner ruling, and needs the owner's ratification (D5).

**A14 (the proposed execution host).**
* It is target-free: the host is proposed before any target information, and the owner decides in the grant.
* Host speed is efficacy-relevant whenever a budget binds. The host must therefore be fixed in the grant, with QC10
  re-run on it, and it must never be changed after the grant (D7).

**E1-1 (strict descendant).**
* The purpose of check 7 is to detect that recording has begun or that the target is consumed. Only a *proper*
  descendant of G (a result or seal commit) indicates that.
* A ref *at* G, such as the remote-tracking ref after the grant is pushed and fetched, does not.
* The strict reading keeps that purpose. Double execution stays excluded by the marker CAS and by check 7's
  namespace rule.
* Without E1-1 every in-band Stage-1a verdict would be REFUSE, and SRK would silently fall back. **Independent.**
* **Role separation is respected.** The change to the variant is requested of the verifier's author through a brief
  committed before issue (`reviews/BRIEF_FC2_VERIFIER_VARIANT_AUTHOR_FOLLOWUP_1.md`). At HEAD the committed variant
  does not yet implement it (D8).

---

## 3. Task 2: new exposures (ledgers from 39ed662c on)

* **`ledger/EXPOSURE_LEDGER.jsonl`, rows 2–22.** Every row is one of: a masked code skeleton; JSON key paths and
  types; a masked C6 grep; an AST-only scan; or a masked grep of the Stage-1b guard-call lines. Every row has
  `carried_309_numeric_values: false`.
* **`ledger/ZERO_TARGET_LEDGER.jsonl`, 169 lines:**
  * classes: SYNTHETIC 75, NONTARGET_DECOY 73, GOVERNANCE 21;
  * no cell touched, no band drift, and all counters 0;
  * decoy work: I1 on the decoy certificates; one development Stage-1a job on the h5 decoy sub-block, out of band;
  * dry admission only for real-band items, never evaluated.
* **Spot-checks.**
  * **Masked grep of C6** (`spotcheck_masked_grep.py`). Its mask covers decimals, fractions, exponents and numbers of
    three or more digits. It leaves only three 1–2-digit integers in the 28 lines it selects: a condition label, a
    duration in seconds, and an array index. None is followed by "%", and **none is of a 305–309 value class**.
  * **`code/code_skeleton.py`**, reviewed in my U2 check. The residual risk is LOW: non-numeric strings, small
    integers up to 24, and small-integer BinOps outside call arguments survive the mask.
* **Unledgered at the time.** The verifier author's rev-1 inspections were transcribed retrospectively (ZTL lines 7–8;
  FE-6). They were read-only, inspected guard sources and pattern constants, and carry no value class. This is the
  same class as E-17(a) (D3).
* **Conclusion.** No 305–309 value was seen by the coordinator, the FC2 authors or any tool, on the record.

---

## 4. Findings from the C5 / C6 answers

* **C6.** `governance/ERRATA_FORMAL_P309.md` FE-1..FE-7 answer C6(a)–(e) accurately. FE-1 now carries each rule
  choice's direction.
* **C5.** The 25 recovered briefs verify against their sha256 values, and the README states "content, not timing".
  C5 is satisfied as far as it can be.
* **What the recovered briefs show (new facts):**
  * **Reader A brief** (item 1, 12:59:21Z, before 309R1-01 and before THEOREM_SRK). Its section G explicitly asks
    which terms of the direct-clause closed form "have been identified (qualitatively) as dominant for 309 by committed
    records". Its example already states the C3 knockout.
    * So the 309-specific qualitative dominance that motivated SRK was **solicited**, not merely encountered as
      "programme-wide dominance knowledge".
    * This is consistent with a research campaign whose purpose was a 309 route. It does not change temporal or
      parametric independence, since no parameter is taken from it.
    * **My result-chasing rating for SRK stays MEDIUM-HIGH (upper end).** The solicitation must be disclosed by name
      (D3).
  * **Reader B and C briefs.** They are protective: the firewall, redaction of any "route gain × tail quantity"
    sentence, and exposure lists.
  * **FC2b rev-1 brief** (item 23, 01:49:53Z, issued while my first review was open). It instructed:
    * producing h = 3 certificates "at a test cell inside [3/2, 7/4]", which lies inside the geometry-blind inherited
      band;
    * sandbox admission tests with the **REAL** names and a sandbox marker, later forbidden by owner rulings 2.

    Per ZTL lines 7–8, FE-6 and FC2_SPEC_R2's preamble, nothing was run: the attempt was stopped by a permission
    denial, and the partial file was removed. It carries no information. It is **not recorded as an incident** (D4).

---

## 5. Task 4: liabilities

No delta item needs a new liability rating. Several need **disclosure** in `disclosed_liabilities` and in the
conditions carried into the grant (D3):
* the closure-relevant rev. 2c changes, each with its direction and basis:
  * A4: toward closure; restores executability;
  * E1-1: toward closure; prevents a silent SRK loss;
  * A6: toward a conclusive outcome; wall time unbounded;
  * A5: a new parameter, ambiguous direction, the maximal limit;
  * A14: host speed is efficacy-relevant;
* the solicited reader-A dominance request;
* the FC2 rev-1 instruction, never executed;
* the unledgered rev-1 inspections.

---

## 6. Result-chasing (delta)

* The **delta**'s own result-chasing component is LOW–MEDIUM.
  * Four changes favour closure or a conclusive outcome, all made by the exposed coordinator.
  * Three of them are repairs found by independent parties (A4, E1-1) or required by reviewed text (A6).
  * One (A5) is a gap-filling resource choice made without target or decoy cost evidence.
* **The route's overall rating is unchanged: MEDIUM-HIGH, upper end.**

---

## 7. Conditions

* **D1 (wording).** The rev. 2c delta is accepted on **temporal and parametric independence only**. C1–C8 continue.
* **D2 (A5 / A6 text; before the freeze).**
  * Correct A5's rationale. Classify A5 as a new parameter, **efficacy-relevant with an ambiguous direction**.
  * Correct A6's bound to "Stage 1b < 21 600 s + 4 × 21 600 s CPU" (or whatever follows from the frozen per-job
    limit).
  * Qualify "What is not changed": the 21 600 s is a start threshold, and the effective ceiling depends on the new
    per-job limit.
  * The owner or the pre-freeze review may instead set a smaller per-job limit, for example 5 400 s, the Stage-1a
    ratio. Any such change must be made **before any QC09 or other Stage-1b run** and reviewed as a delta.
  * QC11 must exercise the frozen Stage-1b limit and order.
* **D3 (disclosure).** Add the items of §5 to `disclosed_liabilities` and to the grant's
  `incident_review_conditions_verbatim` together with D1–D8.
* **D4 (incident record; before the freeze).** Record the FC2 rev-1 instruction as a formal incident (append-only),
  with liability NONE. Record it as:
  * an in-band synthetic test band, and the REAL names in a sandbox;
  * issued at 01:49:53Z;
  * never executed;
  * withdrawn by FC2_SPEC_R2 and owner rulings 2.
* **D5 (owner authority; before the freeze).** The owner must ratify the two scanner extensions: A10's pending-ref
  NAME, and A19's sanctioned marker-mutating exactly-once sites. Independent review can confirm that they are narrow,
  but it cannot supply the owner's authority. If the owner refuses, the design must change before the freeze.
* **D6 (A15).** The Stage-1b decoys (297, 316) stay as declared. A guard refusal or failure in QC09 is recorded as is;
  a substitute decoy needs a reviewed amendment.
* **D7 (A14).** The execution host is fixed in the grant, with QC10 re-run there, and is never changed after the grant.
* **D8 (pending implementation and later changes).**
  * The pre-freeze review must confirm that the verifier author's implementation of E1-1/E1-5 changes only those
    points. The uncommitted edits in the working tree are not reviewed here.
  * Any further rule, parameter or binding change after this review, including errata after E1-6, is a new delta for
    review under C2.

---

## 8. Reviewer disclosures

**Exposures:**
* the recovered reader-A brief, which contains an illustrative placeholder Γ number documented as made-up (not a cell
  value); I do not reproduce it;
* the class of a committed 307-campaign RLR cost (cited by line only);
* decoy and test-band drifts, and band literals;
* masked or re-masked outputs.

No 305–309 value was seen.

**Executions.** One static scratch spot-check (§0). No kernel run and no evaluation.

**Writes.** This file only. No git write.
