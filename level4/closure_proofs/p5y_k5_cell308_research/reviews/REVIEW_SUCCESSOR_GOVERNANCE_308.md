# Independent governance review: SUCCESSOR_GOVERNANCE_308.md (cell-308 successor determination)
GOVERNANCE_REJECTED

Reviewer: reviewGOV (fresh, independent; wrote none of the reviewed material, reviewed none of it before).
Date: 2026-09-30. Mode: read-only (no mb308 driver mode run, no ref change, no git write, GIT_OPTIONAL_LOCKS=0 in the
formal worktree, no computation on cells 305-309, no drift in [6/5, 13/5] or its mirror, nothing of cell 309
inspected beyond what the 308 texts say).

Reviewed object: research branch `p5y-k5-cell308-research`, file
`level4/closure_proofs/p5y_k5_cell308_research/governance/SUCCESSOR_GOVERNANCE_308.md` as of commit `e5871aa6`.

## Work log (incremental)

- Started; read the determination (131 lines).
- Confirmed the reviewed file is byte-unchanged from e5871aa6 in the working tree (no diff); the research branch has
  since gained bddd85f8 (Phase 3 route audit, 03:14 JST), which does not touch governance/.
- Read formal protocol r3 §1-§3, §7, §8, §10-§14 (formal worktree, read-only, GIT_OPTIONAL_LOCKS=0), the driver
  docstring and exit-code messages, the grant JSON (all fields), qualification-review G1-G5/E1-E8/N1-N8 (as carried
  verbatim in the grant), USER_RULING_C4.md, USER_AUTHORIZATION_R3.md, the charter README.
- Read the recovery assessment, addendum A1, erratum E1, REVIEW_EXECUTION_INTERRUPTION §4b, §8b, §9, C1-C6, N1-N9.
- Verified precedents in git: K4 bc4ba08e / K4R1 81f5195a..b5b4c917 / e88a2885 (= tag p5y-k4-successor-closed);
  306 C12-R2 276f4d41 -> 9c2cbf21 -> c5324a78 (adjudication text read at lines 380-400).
- Read INCIDENT_INDEPENDENCE_REVIEW_MB308 Q4 and C9, COORDINATOR_EXPOSURE_DISCLOSURE (E1-E3, E1'), ROUTE_REGISTRY r2
  (C11R-I2 / COR-T rows), REVIEW_R3_HOST_REPAIR F3, the formal postexec record and checks (21e99cf0).
- Verified read-only that the formal worktree is clean including ignored files, and that the driver's only temporary
  directories are the pre-marker probe and the seal (Stage 1 keeps its certificates in memory).
- Searched both namespaces for the two user texts cited in §2 rows 8-9: no record exists.
- Reviewer start ledger line appended 2026-09-29T18:20:21Z (class REVIEW, agent reviewGOV, counts 0).

---

## Verdict in one paragraph

**Rejected as submitted, on the record of governing texts; the classification itself is confirmed as the right
target.** Four binding texts that bear directly on "may cell 308 be evaluated a second time?" are omitted or half
quoted. Two further texts that are cited as governing ("user campaign brief", "user overnight program") exist nowhere
in the repository. None of these texts forbids a successor outright once read with its scope. But the user will rule
under S1 on the basis of this document, and a ruling taken on an incomplete list of the prohibitions it overrides
would be defective. A bounded repair is enough: an addendum that quotes and reconciles the omitted texts, verbatim
records of the two user texts, and the missing conditions below, followed by a delta review. The operative
conclusions stand after that repair: a successor is permitted only as a new campaign; preparation may proceed; and a
new explicit user ruling is required before any successor grant. Nothing in the determination changes a status,
authorises a target step, or touches cell 309.

## 1. Are the governing texts quoted accurately, and is anything binding omitted? FAIL

**Accurate (verified against the bytes).**
* Protocol r3 §8, the INDETERMINATE row: "(target consumed; no rerun)" (MB308_PROTOCOL.md l.147).
* Protocol §10 step 3: "**REJECTED ⇒ STOP** (no same-round repair; a successor campaign only)" (l.179).
* Qualification review E7: "Lost result information is never recomputed without a new independent governance
  process" (MB308_QUALIFICATION_REVIEW.md l.469; grant copy identical).
* The grant statement: "No re-run, no tuning and no successor selected from the result" (grant `grant_statement`).
* U6 (USER_RULING_C4.md, point 6), verbatim, with emphasis added. U7 and U8 are fair paraphrases.

**Mislabelled or imprecise (minor).**
* "driver docstring | … 'NEVER run execute again'". That phrase is the runtime message at `mb308_driver.py` l.796,
  which was never printed, because the driver never returned. The docstring itself says "6 CONSUMED_UNRECORDED (never
  rerun)" (l.36).
* §1: "The §10 steps 6–8 … are running separately." Only step 6 has been launched (brief 27; reviewEXEC ledger line
  230). No adjudication or adjudication-review brief exists.
* §1 and §4.5 say "the Force Quit of the hosting app". The accepted record says it was **the user's** Force Quit
  (A1 (a), postexec §2). That fact matters to the selection argument (§4 below) and should be stated.

**Omitted or half-quoted binding texts (the reason for FAIL).**
* **O1. E3, half quoted.**
  * §4.5 cites "E3 says host events never change outcomes". The full text of E3 (qualification review l.439-441,
    carried verbatim into the grant; r3 repair review E2; protocol §14) continues: "**There is no rerun and no
    reinterpretation on host grounds.**"
  * Protocol §14 pre-declared the exact case in point: a host event "can therefore only waste the evaluation, never
    produce a wrong verdict … there is no re-run and no re-interpretation on host grounds."
  * A successor motivated by a host-wasted evaluation is exactly what this sentence addresses. The determination
    relies on the first half of E3 and drops the second half.
* **O2. Mitigation 5 of the coordinator exposure disclosure, omitted.**
  * The text is `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md` §E3, "Mitigations, bound into the charter": "5. **at
    most one target evaluation, of one frozen route.**"
  * This is a research-campaign-level commitment, and the successor governance, the route audit (bddd85f8) and the
    architecture are all being produced inside this research campaign.
  * The incident-independence review's reasons for rating result-chasing MEDIUM–HIGH and **not HIGH** include "There
    is exactly one sealed evaluation" and "D10 forbids evaluating any other route on 308" (Q4).
  * Of all the texts, this one comes nearest to an outright bar on a second evaluation.
* **O3. Incident-review C9, omitted.** "one sealed execution, with **no retry** and no post-result tuning". It is
  carried verbatim into the grant (`incident_review/conditions_C1_C9_verbatim`).
* **O4. Protocol §14 pre-declared consequence and qualification-review G2, omitted.**
  * The text: "Freeze r3 is **never re-run**, and **no r4 with the same caps** is made, **without a new explicit
    user decision recorded before it**."
  * G2 applies it to any change after the qualification review: "no r4 with the same caps without a new recorded
    user decision (§14)".
  * The Phase 3 audit (bddd85f8, not reviewed here) has since selected MB-S: MB r1 science unchanged. A successor
    with unchanged science and unchanged caps is an "r4 with the same caps" in substance, whatever its namespace.
    Under this text, the user decision must be recorded **before the successor is made**, i.e. before its freeze,
    not only before its grant (see item 6).
* **O5. The recovery-chain condition C6, and postexec §4, half cited.**
  * The determination cites E7's "new independent governance process".
  * The accepted recovery chain binds more: "Lost information is recomputed only through a new independent
    governance process **and a new user decision**" (REVIEW_EXECUTION_INTERRUPTION C6; formal postexec record §4;
    recovery assessment answer D).
  * S1 satisfies this in substance. The text should still be cited, because it is the accepted chain's own
    statement of the successor path.

**Governing texts that are not on record (U1).**
* §2 row 8 quotes a "user campaign brief (2026-09-28)", and row 9 a "user overnight program (2026-09-30)".
* A search of the research namespace, the formal namespace and the research branch finds no record of either text,
  except in the determination itself.
* In this campaign a user decision is recorded verbatim before it is cited. Qualification-review N6 / N-b on the r3
  paraphrase led to `USER_AUTHORIZATION_R3.md` (`8d690a88`); the C4 ruling is in `USER_RULING_C4.md` (`0aeaec23`).
  Row 9 carries the whole "preparation now" branch of the classification, so it must be on record.

## 2. Is a successor after CONSUMED_UNRECORDED permitted, or does a text forbid it outright? PASS WITH NOTE

**No text forbids a second cell-308 evaluation outright, once each is read with its scope.**
* **Scoped to MB r1's own authorization:**
  * §8 "no rerun";
  * the grant's "No re-run";
  * E3's "no rerun … on host grounds" (O1);
  * C9's "no retry" (O3);
  * the driver's "never rerun".

  Each binds the consumed marker and grant `afa93072`, which stay consumed forever.
* **U6 is scoped** "under the frozen protocol", and its "from its result" is not triggered, because no result exists.
* **Two accepted texts name the path.** E7 and the recovery chain's C6 / postexec §4 both provide one for lost
  result information: "a new independent governance process and a new user decision". The permission is therefore
  positive, not merely the absence of a bar.
* **The 306 record supports the scope reading.** Its no-rerun rule reads "no re-evaluation … may follow **in this
  campaign**" (item 3).

**Note 2a. Mitigation 5 (O2) is the one text that reaches beyond MB r1.**
* It binds this research campaign: "at most one target evaluation, of one frozen route".
* It is a coordinator-declared mitigation, not a user ruling, so a user ruling can lift it for a successor. It must
  be lifted **expressly**, in the S1 ruling, with the incident review's reliance on it (Q4, "why not HIGH") in view.

**Note 2b. Asymmetry in §10.**
* §10 names "a successor campaign only" for a **pre-target** stop (step 3). For a post-target failure (step 6) it
  says only "no rerun".
* A reader could take that as a deliberate exclusion of post-target successors. E7 fills the gap, since it is
  specifically about post-marker lost information. The addendum should say so rather than rest on step 3.

**Conclusion.** A successor is permitted only as a new campaign and only through a user ruling that expressly
addresses:
* the second consumed evaluation of cell 308;
* mitigation 5;
* E3's "no rerun on host grounds". The successor proceeds on a new governance decision, not as a host-grounds
  rerun;
* §14 / G2's same-caps r4 clause.

## 3. Do the precedents apply as claimed? PASS WITH NOTE

**K4 → K4R1: the facts are verified.**

| item | commit | as claimed |
|---|---|---|
| historical K4 run, NOT_CLOSED (K4_INCONCLUSIVE_K1_RECORDS) | `bc4ba08e` | yes |
| K4R1 candidate | `81f5195a` | yes |
| qualification rejections r1–r4 | `ce144fd7`, `c5e677a3`, `49a48a50`, `0dc949b5` | yes |
| K4R1 freeze | `8928b8f1` | yes |
| one K4R1 execution | `b5b4c917` | yes |
| K4R1 closure | `e88a2885` = tag `p5y-k4-successor-closed`, which records HISTORICAL_K4_VERDICT = NOT_CLOSED (preserved) | yes |

**But K4R1 is an existence precedent, not a governance template.**
* It was designed **from the observed historical result**: `81f5195a` begins "Phase A residual table (exact, from
  the historical K4 report 83cabce2)".
* It was committed about 70 minutes after that result.
* Its namespace holds no user-ruling record.
* Under cell 308's rules (U6, quarantine, "independent prospective motivation") that design would be illicit.
* So the a-fortiori claim ("closer fit here than there") holds on one axis only: here no outcome was observed. It
  cannot be read as "K4R1's governance is sufficient here". The addendum should say this.

**Cell 306.**
* Verified facts: C12-R2 sealed `276f4d41` (TARGET_EVALUATED), CELL306_NOT_ADOPTED `9c2cbf21` (Γ(S_I2) > 0 recorded
  there), ADJUDICATION_ACCEPTED `c5324a78`.
* The determination paraphrases the reason: "because re-running after an observed outcome would be result-chasing".
  The recorded basis is floor r2's frozen rule `disagreement.never`: "no re-evaluation, parameter change or supply
  change may follow in this campaign" (C12R2_ADOPTION_ADJUDICATION.md, l.389-390).
* The recorded basis should be cited. It is in the same spirit, and its "in this campaign" supports item 2.

**Cell 307.** Consistent with the charter: CLOSED_UNDER_RLR, closure-only, marker consumed, never re-run.

## 4. Prospective integrity, determinism, runtime-only observations: PASS WITH NOTE

**No target value was observed. Verified.**
* The postexec checks (`21e99cf0`):
  * no object strictly after the marker; the only window objects are the two pre-marker probes;
  * no pending ref, no emergency file, no guarded path.
* My read-only check: the formal worktree is clean including ignored files.
* The driver's only temporary directories are the pre-marker probe (l.295) and the seal (l.660).
* Stage 1 persists nothing to disk; the pinned certifiers' file-writing entry points are CLI functions that the
  driver does not call.
* The driver prints nothing before the seal.

**The determinism argument holds, conditionally, and is stronger than stated.**
* **The value is deterministic once the run completes.**
  * Verification budgets are operation counts (D14).
  * A cap hit or an exception outside a pinned certifier is an execution failure, never a dropped rung (D8, E5).
  * QC04 establishes determinism at non-target cells.
* **Timing affects only whether the run completes.** The per-job CPU caps and EVAL_CAP make INDETERMINATE vs
  sealed timing-dependent. A second run is therefore a second chance to **complete**, never a second draw of Γ.
* **The consequence.** With byte-identical science, the successor returns the Γ that MB r1 would have returned,
  whatever caused the interruption. Even a user Force Quit prompted by runtime could not bias a closure. The
  determination should state this; it is the decisive integrity argument for MB-S.
* **The argument holds only for byte-identical science** (condition GC-4). A refactored Stage-1 / supply / consumer
  path voids "bit for bit" unless equivalence is proven.

**The list of runtime-only observations (§4.3) is incomplete. Also held:**
* the OS thermal-pressure level 2 from 20:59:17 to the reboot;
* the powerlog per-coalition CPU, with its short load dips (not repeated here). These readings are **committed** in
  `reviews/REVIEW_EXECUTION_INTERRUPTION.md` §4b, and so are readable by any successor agent;
* the ReportMemoryException and the memory-pressure warning;
* the inference "mid-Stage-1 at 23:40:48 / most probably never finished Stage 1";
* the coordinator's 23:10 `ps` audit: worker ages and CPU times, which by pid succession also reveal how many jobs
  had completed.

**Holders:** the coordinator, reviewINT (three rounds) and, presumably, reviewEXEC.

**Why they are target-informative.** Under longest-first scheduling with one fresh worker per job, per-job durations
are latent proxies for rung outcomes.

**What S3 already does, and what is missing.**
* S3's exclusion ("no information from it enters any successor decision") is the right rule.
* Disclosure only in governance prose falls short of the E1′ precedent. See GC-6.

**The user Force Quit.** Its reason is not recorded. Under byte-identical science this is immaterial, by the argument
above. Under changed science it would matter, and S4's "changed" branch should say so.

## 5. Retry vs successor, and S1–S10: PASS WITH NOTE (conditions missing)

**The distinction in §4.4 is sound:**
* no outcome exists;
* the science is exact;
* any change needs a non-target motivation fixed in advance;
* the retry is disclosed.

**S1–S10 are necessary, and each is right as far as it goes.**
* **S3 and S6** match the recovery review's N8: detached launch, logs outside /private/tmp.
* **S7** keeps exactly-once per campaign.
* **S10** isolates cell 309.

**Missing conditions** (GC-1 … GC-10 below):
* the order relative to MB r1's own §10 steps 6–8;
* the content of the S1 ruling;
* the definition of "unchanged";
* re-rating the result-chasing risk rather than carrying it "verbatim". Its "why not HIGH" premises are altered by a
  second evaluation;
* a formal exposure addendum;
* the successor preflight's handling of MB r1's consumed marker and of any late-found MB r1 evidence;
* resource containment, because the hang cause is unknown and memory-pressure events were logged during the run;
* host exclusivity, including the separate session's compute, arranged through the user without inspecting it;
* whether a successor INDETERMINATE is final.

## 6. Is the classification correct? Is preparation without a ruling legitimate, and a ruling before the grant? PASS WITH NOTE

**SUCCESSOR_ALLOWED_WITH_CONDITIONS, with S1 = USER_RULING_REQUIRED at the grant, is the correct class.**
* SUCCESSOR_NOT_CURRENTLY_ALLOWED is wrong: E7 and C6 provide the path, and no outcome exists.
* SUCCESSOR_ALLOWED without conditions is wrong: a second consumed evaluation needs the user (C6, O2, O4).
* SUCCESSOR_REQUIRES_USER_RULING would fit only if nothing could be prepared first. The user's own instruction,
  as reported, asks for preparation now.

**A ruling before any grant is required, and correctly placed.** C6: "and a new user decision". U6 authorised only
one evaluation "under the frozen protocol".

**Preparation without a ruling is legitimate up to, but not including, the successor freeze.**
* **Before the freeze:** target-free research, route audit, design, implementation, dev tests, crash-injection
  tests, and decoy runs outside the band under the research quarantine.
* **At the freeze:** O4 requires a user decision "recorded before it" for an r4 with the same caps. It applies in
  substance to MB-S if the caps are unchanged. If the caps are re-derived, the decision is still prudent, since the
  science is unchanged.
* **The user's overnight program may already be that decision**, if its words cover freezing and qualifying a
  successor. It must first be recorded verbatim (GC-2).
* **Otherwise**, the freeze waits for a user decision, and the class for anything past the design stage is in
  effect SUCCESSOR_REQUIRES_USER_RULING.

## 7. Does the determination change a status, authorise a target step, or touch cell 309? PASS

* §6 of the determination authorises no evaluation, grant or marker.
* It keeps every status: cell 308 OPEN, r5 unchanged, no r6, K5 PARTIAL, P5Y unchanged.
* Its ledger line (2026-09-29T18:09:45Z) records 0 / 0 / 0.
* S10 forbids any inspection of cell 309. The label "EXTERNALLY_IN_PROGRESS" is the coordinator's statement; by
  rule, I did not verify it.
* No cell-309 material was read for this review.

## 8. Anything else: NOTES

* **Preparation is running ahead of review.**
  * The Phase 3 route audit (bddd85f8, 18:13:54Z) and the Phase 4–8 architecture (ledger 18:19:40Z) were produced
    before this review returned.
  * The latter also created a successor worktree `/Users/suzhe/ReBaseGuard-c308mbs` on branch
    `p5y-k5-cell308-mbs-r1` from `21e99cf0`.
  * This is permitted as target-free preparation, but it is at risk. See GC-9.
* **Brief-index timestamps.**
  * Rows 24–29 of `ledger/briefs/BRIEF_INDEX.md` carry the calendar date 2026-09-30 with a "Z" time. The ledger puts
    these events on 2026-09-29 UTC; for example, this review's first line is 2026-09-29T18:20:21Z, against row 28's
    "2026-09-30 ~19:2xZ".
  * Rows 27–29 are also about an hour late. This is not load-bearing; it should be corrected as an erratum.
* **Pre-existing successor motivation.** The route registry r2 already recorded, before the MB r1 execution, that
  adding C11R-I2 is "a successor-campaign item" (not excluded by estimated effect). That is legitimate prior
  provenance, should a changed-science successor ever be considered.

## CONDITIONS

**Repair of this determination (before it may govern any successor freeze or be put to the user for S1).**

* **GC-1. Addendum A1 to the determination.**
  * **Form.** The original stays byte-unchanged; A1 prevails where they differ.
  * **Quote verbatim, and reconcile, the omitted texts O1–O5:**
    * E3 in full, with protocol §14's "no re-run and no re-interpretation on host grounds";
    * mitigation 5 of the exposure disclosure §E3, with the incident review's Q4 reliance on "exactly one sealed
      evaluation";
    * incident-review C9;
    * the §14 pre-declared consequence and G2;
    * the recovery chain's C6 / postexec §4, "and a new user decision".
  * **Correct:**
    * the driver-quote attribution;
    * "steps 6–8 are running" (only step 6 is running);
    * "the user's Force Quit".
  * **Replace** the 306 paraphrase with floor r2's `disagreement.never` ("in this campaign").
  * **Qualify K4R1 as an existence precedent only.** Its successor was designed from the observed K4 residual
    table, and no user ruling is on record.
  * **State the §10 asymmetry**, and name E7 / C6, not step 3, as the operative path.
* **GC-2. Verbatim user records before citation.**
  * The 2026-09-28 campaign-brief sentence and the 2026-09-30 overnight program each go into `ledger/` word for word,
    with the time received, as `USER_AUTHORIZATION_R3.md` was.
  * Until they are recorded, §2 rows 8–9 are coordinator paraphrases and cannot carry "preparation now" past the
    design stage.
* **GC-3. The content of the S1 ruling.** The ruling must expressly:
  * authorise a second consumed evaluation of cell 308 (count 2);
  * lift mitigation 5 for the successor;
  * state that the successor is a new governance decision, not a rerun on host grounds (E3);
  * decide the §14 / G2 same-caps question;
  * re-affirm U1–U8;
  * say whether a successor INDETERMINATE is final for route MB.

  The brief put to the user must list O1–O5 verbatim.

**Conditions on the successor campaign (to be added to S1–S10).**

* **GC-4. "Unchanged science" means byte identity.**
  * The following must be sha256-identical to freeze r3 `c46434a3`:
    * the theory;
    * the pinned certifier bytes;
    * `mb308_stage1`, `mb308_supply`, `mb308_consumer`, `mb308_a0core`, `mb308_pinned`;
    * the guard's admitted-pair derivation, the cover geometry, D1–D14 and the criterion.
  * Anything else that changes must sit outside the evaluation path. Its qualification must include an
    exact-equality comparison of certified outputs, successor vs MB r1 frozen code, at the decoy cells (non-target
    only, timing fields stripped as in QC04).
  * Without this, the §4.4 determinism argument does not apply, and S4's "changed" branch governs.
* **GC-5. Re-rate the result-chasing risk; do not carry it verbatim.**
  * S5's "result-chasing MEDIUM–HIGH" becomes "not lower than MEDIUM–HIGH".
  * A fresh incident-independence reviewer re-rates it for the successor, because the Q4 premises (exactly one
    sealed evaluation; only R-MB on 308) are altered.
* **GC-6. A formal exposure addendum** to `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`, following the E1′ precedent.
  * **It names, never values:**
    * the MB r1 target-run runtime and host observations (item 4's full list);
    * where each is recorded: the session transcript, REVIEW_EXECUTION_INTERRUPTION §4b, the reviewEXEC files;
    * which agents hold them.
  * **Brief restrictions:**
    * no successor brief may contain them;
    * no successor brief may point to REVIEW_EXECUTION_INTERRUPTION §4b;
    * the successor's route, implementation and caps agents are agents that have not seen them.
  * **The caps decision** (keep MB r1's, or re-derive them from decoys) is justified in writing from decoy and
    qualification evidence alone.
* **GC-7. MB r1 closeout first.**
  * No successor freeze or grant before MB r1's §10 steps 6–8 have returned EXECUTION_ACCEPTED, the adjudication
    (§8 verbatim) and ADJUDICATION_ACCEPTED.
  * The successor cites them.
  * If any of them is REJECTED, this determination is re-reviewed before anything else proceeds.
* **GC-8. The successor preflight asserts MB r1's recorded state.**
  * The state asserted is the one in `21e99cf0`:
    * `refs/p5y-k5-cell308-mb-r1/target-consumed` → `afa93072` is the only ref under the prefix;
    * there is no pending ref, no emergency file and no `evidence/` path.
  * The successor refuses otherwise. Any later-found MB r1 evidence is a permanent STOP for the successor, pending
    its own governance.
  * The successor's "no prior evaluation" check treats exactly that one consumed MB r1 marker as a reviewed,
    named exception, never as a prefix wildcard.
* **GC-9. Freeze gating.** No successor freeze and no official qualification until:
  * this determination, as repaired, is accepted by a delta review;
  * the route selection is accepted;
  * GC-2 is satisfied, with a recorded user decision covering the freeze under §14 / G2.

  Preparation done before then (bddd85f8, the Phase 4–8 architecture, the `-c308mbs` worktree) is at risk and is
  re-checked against the accepted text.
* **GC-10. Reliability additions to S6** (all target-free, sized from decoys only):
  * **Resource containment.** The cause of the post-23:41 hang is unknown, and memory events were logged during the
    run. Measure peak RSS per job kind at the decoys, and set per-worker memory limits and host headroom, so that
    exhaustion becomes a recorded INDETERMINATE rather than a host hang.
  * **Host exclusivity during the run.** This covers any other session's heavy compute on the same host. It is
    arranged through the user, without inspecting that session.
  * **The E1 rule of MB r1**, restated for the successor: nothing else runs until the seal, and no in-run `ps`
    audit beyond what the frozen host contract records.

## NOTES

* **N1.** The classification, S1's placement at the grant, and S2, S3, S6, S7, S8 and S10 are sound and should be
  kept.
* **N2.** The decisive integrity argument for MB-S is determinism under byte-identical science (item 4). It makes
  the interruption's cause, including the user's Force Quit, immaterial to Γ. The addendum should lead with it.
* **N3.** Under GC-4, completion is timing-dependent but the value is not. Re-deriving caps from new decoy runtimes
  changes only the probability of completion, never Γ. That is why S3's decoy-only rule is sufficient for caps.
* **N4.** The brief-index timestamps (item 8) need an erratum.
* **N5.** Route registry r2 already names C11R-I2 as "a successor-campaign item" (pre-MB r1 provenance). This is
  relevant only if the science is ever changed.
* **N6.** Not independently re-verified here, and outside the scope of a governance review: the recovery facts
  themselves (accepted at `98118e22`), which I relied on as accepted. I did re-check the postexec checks' repository
  facts and the formal worktree's clean state.

## Verdict and reason

**GOVERNANCE_REJECTED, as submitted.**

**Confirmed:**
* The classification SUCCESSOR_ALLOWED_WITH_CONDITIONS, with a new explicit user ruling required before any successor
  grant.
* Preparation is legitimate up to the successor freeze.
* The prospective-integrity argument holds for byte-identical science.
* No status is changed, no target step authorised and cell 309 is not touched.

**Rejected for:**
* **Omissions.** The record of governing texts omits or half-quotes four binding texts that speak directly to a
  second evaluation (O1–O4) and half-cites a fifth (O5).
* **Unrecorded texts.** It cites two user texts that exist nowhere in the repository (U1), one of which carries the
  "preparation now" branch.
* **Missing conditions** (GC-4 … GC-10).

**The repair** is bounded: an addendum per GC-1, the records per GC-2, S1's content per GC-3, and GC-4 … GC-10
added to the conditions. A delta review follows. No change of classification is expected.

## Post-write checks

* Research scanner (`code/c308_quarantine.py --scan`, read-only) run after this file was written:
  * verdict PASS, 0 findings, over 365 text and 51 Python files;
  * both negative controls detected.
* This file contains no tail figure, no Γ value, and none of the MB r1 target run's per-interval runtime numbers.
* Line 2 is the only whole-line verdict token.
* Nothing was written outside this file, the research ledger (two REVIEW lines) and the scratchpad.
