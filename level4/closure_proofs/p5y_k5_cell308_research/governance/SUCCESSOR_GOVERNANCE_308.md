# Cell 308: successor governance after MB308 r1 (coordinator determination; for independent review)

**Classification: SUCCESSOR_ALLOWED_WITH_CONDITIONS.**

Preparation of a new, prospective successor campaign is permitted now. **Any successor target authorization requires
a new, explicit user ruling (USER_RULING_REQUIRED at the grant step).** Nothing here authorizes a target evaluation,
a grant or a marker.

New cell-308 target evaluations since MB308 r1: **0**.

## 1. Starting state (accepted recovery chain)

* **MB308 r1** (formal branch `p5y-k5-cell308-mb-r1`, grant `afa93072`, postexec `21e99cf0`) consumed its one granted
  evaluation. Target evaluations: 1.
* **The run.** It was orphaned by the 23:29:00 JST Force Quit of the hosting app and ended at the latest by the forced
  power-button reset at 00:00:15 JST.
* **Nothing was persisted:** no durable result, no pending ref, no emergency file, no seal.
* **Frozen outcome** (protocol §8): **CELL308_EXECUTION_INDETERMINATE**, target consumed, no rerun.
* **Review status.** RECOVERY_ASSESSMENT_ACCEPTED (research `98118e22`). The §10 steps 6–8 (execution review,
  adjudication, adjudication review) are running separately and do not change the outcome.
* **Cell 308 is OPEN.** r5 is unchanged, there is no r6, K5 is PARTIAL and P5Y is unchanged.

## 2. Governing texts

| text | what it says |
|---|---|
| MB r1 protocol §8 | post-marker failure ⇒ INDETERMINATE, "target consumed; **no rerun**" |
| driver docstring | CONSUMED_UNRECORDED: "NEVER run execute again" (this campaign's driver and marker) |
| qualification review E7 | "Lost result information is never recomputed **without a new independent governance process**" |
| MB r1 protocol §10 step 3 | QUALIFICATION_REJECTED ⇒ STOP, "**a successor campaign only**" (successors are a recognised instrument) |
| grant `afa93072` | "No re-run, no tuning and **no successor selected from the result**" |
| user C4 ruling U6 (`0aeaec23`) | "exactly one authorized target evaluation **under the frozen protocol**, and no tuning or successor variant may be selected **from its result**" |
| user C4 ruling U7, U8 | qualification failure or review rejection still stops before the target; the ruling substitutes for no gate |
| user campaign brief (2026-09-28) | "If first route fails: no tuning against 308; successors need independent prospective motivation" |
| user overnight program (2026-09-30) | prepare a successor tonight; no target authorization, grant, marker or Γ(5,308) without a later explicit user authorization |

## 3. Precedents

* **K4 → K4R1: a successor after an executed, inconclusive run.**
  * The historical K4 run executed once (NOT_CLOSED, K4_INCONCLUSIVE_K1_RECORDS, `bc4ba08e`) and was preserved.
  * The K4R1 successor was governed separately: candidates r1–r5, four qualification rejections preserved, freeze
    `8928b8f1`, one execution `b5b4c917`.
  * It closed K4 under a fresh adjudication (`e88a2885`, CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN), and the historical
    verdict was kept.
  * So a separately governed successor after an execution that gave no usable result is accepted practice here.
* **Cell 306: no rerun after an observed result.** C12-R2 executed once and gave an observed positive Γ, then
  CELL306_NOT_ADOPTED. It was **not** re-run, because re-running after an observed outcome would be result-chasing.
* **Cell 307: one run.** CLOSED_UNDER_RLR, closure-only, never re-run.

## 4. The eight questions

1. **Is a successor permitted after CONSUMED_UNRECORDED?** Yes, as a *new* campaign, not under MB r1. MB r1's "no
   rerun" binds its own grant and marker, which stay consumed forever. E7 names the instrument for recomputing lost
   result information: "a new independent governance process". A successor campaign with its own charter, freeze,
   qualification, independent reviews and a new user ruling is that process.
2. **Does an existing precedent apply?** Yes, K4 → K4R1 (§3). It is a closer fit here than there: K4's historical run
   produced an inconclusive but observed outcome, whereas MB308 r1 produced no observed value at all.
3. **Does the absence of a durable target value preserve enough prospective integrity?** Yes.
   * No Γ(5,308), no bound, and no Stage-1 certificate value of the target run was ever written, printed or read.
     The driver prints nothing before the seal, and the process died before persistence.
   * The coordinator's knowledge of 308 is unchanged from E1/E1′ except for **runtime-only observations** of the
     target run: worker ages and CPU times at the 23:10 audit, and the reviewer's per-coalition powerlog CPU. These
     are latent runtime proxies with no value content, and they are disclosed here.
   * Condition S3 forbids using them for any successor design decision, including caps.
4. **What distinguishes a successor from an illicit retry?** An illicit retry re-runs **because of**, or **after
   seeing**, an outcome. That creates a selection effect (run until CLOSED), or it tunes toward the observed value.
   Here:
   * **No outcome exists.** Nobody knows what MB r1 would have returned, so no selection can condition on it.
   * **The science is exact and deterministic.** Re-evaluating the same Theorem MB r1 certificate with the same
     pinned inputs yields the value the lost run would have yielded, bit for bit (QC04 determinism). There is no
     stochastic "second draw".
   * **Any scientific change** from MB r1 must be motivated by non-target reasons fixed before any successor
     evaluation, and independently reviewed (the user's "independent prospective motivation"). No change may be
     tuned toward any threshold.
   * **The retry is disclosed.** The successor's adjudication records that cell 308 has been consumed twice (MB r1
     INDETERMINATE, and the successor).
5. **Does the 23:29 Force Quit matter to eligibility?** Not to eligibility: it carries no target information, and E3
   says host events never change outcomes. It matters to **design**. The successor must not depend on the hosting
   app's lifetime (Phase 5).
6. **Does the later hard reset matter?** The same as 5 for eligibility. It motivates the **durability** design
   (Phase 6): nothing of a completed result may live only in memory, and the recovery semantics per state must be
   frozen in advance.
7. **Do infrastructure changes make the successor genuinely prospective?** Prospectivity comes from the absence of any
   observed outcome and from freezing before evaluation, not from the infrastructure. The infrastructure changes are
   needed for **reliability** (so the one evaluation is not lost again). They must not change the science, the
   criterion or any threshold. Each change is target-free and independently reviewed.
8. **Is an explicit user ruling required before target authorization?** **Yes.**
   * The C4 ruling authorised exactly one evaluation under MB r1's frozen protocol (U6). It neither authorises nor
     forbids a successor.
   * A successor is a second consumed evaluation of cell 308, so the user must rule explicitly. The ruling should
     also re-affirm the C4 terms: closure-only; incidents 01–03 and the MEDIUM–HIGH result-chasing limitation
     preserved; closure is not adoption.
   * **USER_RULING_REQUIRED** at the successor's grant step. Preparation needs no ruling.

## 5. Conditions (S1–S10) binding any successor

* **S1. User ruling before any grant.** An explicit user ruling authorising a second cell-308 target evaluation, and
  re-affirming the C4 terms, is recorded verbatim before any successor grant. Until then: no grant, no marker, no Γ.
* **S2. New campaign namespace and branch.** MB r1 bytes, refs and records are never modified. The successor cites
  MB r1 as consumed, interrupted, INDETERMINATE and **not scientifically negative**.
* **S3. No dependence on the MB r1 target run.** No information from it enters any successor decision: none exists as
  a value, and the runtime observations of §4.3 are excluded. Caps and timing rules come from decoy runtimes only
  (incident review C7(b)).
* **S4. Science.**
  * **If unchanged** (Theorem MB r1, the same pinned inputs and criterion), the successor states the determinism
    argument of §4.4.
  * **If changed**, every change has a written non-target motivation fixed before any successor evaluation, is
    independently reviewed, and is never tuned toward a threshold. A route audit (Phase 3) decides.
* **S5. Liabilities carried forward verbatim.** Incidents 01–03, H4.3b, I-a…I-e with E1′, the F2/F3 exposures, the
  quarantine breach, single-implementation inputs, and result-chasing MEDIUM–HIGH. The C4 conditions U1–U8 are the
  minimum for any new ruling.
* **S6. Reliability.** The successor adds, prospectively and target-free:
  * a launcher that survives the hosting app's death and the launcher's parent's death;
  * crash-safe, atomic, durable persistence of the complete result before anything else can fail;
  * a frozen state machine with recovery semantics for every state;
  * crash-injection tests;
  * a host contract that keeps host health separate from scientific validity.
* **S7. Exactly-once, again.** The successor has its own single marker and grant. A failure after its marker gives
  its own frozen INDETERMINATE-class outcome. Any further successor needs a further governance process and user
  ruling.
* **S8. Independent reviews.** Fresh reviewers, preserved rejections and bounded deltas, for the governance (this
  document), the route selection, the implementation, the qualification, and later the execution and adjudication.
* **S9. Quarantine.** The research quarantine (drift band, T1–T4, scanner) applies. No new Γ308 before the grant. No
  target-valued proxy.
* **S10. Isolation from cell 309.** Cell 309 is EXTERNALLY_IN_PROGRESS in a separate session. No inspection for
  continuation, duplication, review, proxy, qualification, authorisation or evaluation of cell 309.

## 6. What this determination does not do

It authorises no target evaluation, grant or marker. It changes no status: cell 308 stays OPEN, r5 is unchanged,
there is no r6, and K5/P5Y are unchanged. It does not select the route; Phase 3 does, with its own review.
