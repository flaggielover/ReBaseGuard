# Owner decision package, revision r4 (Cell-308 Cloud route r1): one consolidated instrument, four statements in dependency order

**Status: FOR THE OWNER · NOTHING HERE IS EFFECTIVE UNTIL THE OWNER ISSUES IT, AND EACH STATEMENT ONLY AFTER ITS
PREREQUISITES ARE RECORDED.**

**Precedence.** This revision supersedes `OWNER_DECISION_PACKAGE_R3_20261016.md` (`ef356fdb…d5`). R3 and the OD-2
package are preserved unchanged.

It applies external B1 findings X1, X2 and X3 (`reviews/external/REVIEW_EXTERNAL_B1_CONFORMANCE.md`, `cf1a4b18…8e41`):
* R3's statement 1 item 3, which proposed that the owner adopt "no E1″ exposure arose from the disclosed searches", is
  **withdrawn**;
* the S12 Q8 steps become explicit owner records;
* the order follows `READINESS_MATRIX_R4_20261016.md`.

The owner's stated direction (2026-10-16) is "to continue on one compliant, owner-controlled host under the reviewed
safeguards". `DECIDED` is empty. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The recommended resolution (unchanged in substance from R3 §1)

The route proceeds on one owner-controlled, single-tenant Linux machine, only through the gates of matrix R4, with:
* S12's mitigations written, confirmed in text, adopted, and then evidenced operationally at their stages (matrix R4
  A19 and OPS-1…OPS-12);
* the external checks done outside the coordinator's reach;
* every decision taken before any new-host reading exists.

The rating floor is **not lower than HIGH** on accepted text (amendment erratum E2.3), whatever S12's standing.

If an S12 condition proves unmet and uncorrectable, the S12 advice applies: V-C, close the route with MB-S r1 left at
NOT_DERIVED. That is reported as a finding, and no run is launched.

## 2. Statement 1: may issue now (no prerequisite outstanding)

Items 1 and 2 implement S12 Q8's "adopt FR1's standing first". Item 6 replaces R3's withdrawn certification.

> **Owner statement 1 (Cell-308 Cloud route r1), [date].**
> 1. **FR1 standing (first).** I adopt reviewerFR1 as a coordinator-appointed advisory reviewer under my OD-2
>    instruction. Review sha256 `af150ef4493f2601a7a17ecbecebc02ae4f237e3f3fcfe5914d0e11af704b6df`. It is advice. It
>    satisfies no requirement for an independent or owner-launched reviewer.
> 2. **S12 appointment (Q8-1).** I adopt reviewerS12's appointment as advisory: brief
>    `ledger/briefs/S12_RISK_REVIEW_CLOUD_R1.txt`, sha256
>    `d46c19f7d82905d36f643ac7f003d7130835c4b9868c50ee9939467398a3710d`; agent or session id [as I record it; if I
>    know it only from the coordinator, I say so]. Review sha256
>    `9d549eb2ad8aa9f72f49712961610b6f12b813d33eaa587dfa4f259862b2b55c`. It is advice.
> 3. **FR2.** I adopt reviewerFR2 as a coordinator-appointed advisory reviewer. Review sha256
>    `1ad769bbd35c1d4f7fbf2a47ba0b7bd907169c962795939613ed03adc9868cac`. It is advice.
> 4. **S12 digest channel (Q8-2).** The S12 review's sha256 did not reach me directly from the reviewer's reply
>    channel; the reply passed through the coordinator's session. I record that condition as **UNVERIFIED**. Nothing in
>    this statement satisfies it.
> 5. **OD-2 sentence (Q8-3).** I confirm that my OD-2 instruction's sentence "Complete the fresh S12 review using an
>    eligible reviewer" covered the coordinator's S12 appointment and its commissioning.
> 6. **Search breach.** I record that reviewerS12 and reviewerFR2 ran recursive searches their briefs prohibited, which
>    scanned the bytes of excluded files. That breach is established. Whether any excluded content reached either
>    reviewer's context, and their resulting E1″ holder status, are **UNVERIFIED**, and I certify neither. Both reviews
>    are advice only, with reduced weight. Neither satisfies a requirement for an independent, owner-launched or
>    non-holder reviewer. Neither reviewer takes any later role on this route.
>    (`REVIEWER_SEARCH_ELIGIBILITY_DETERMINATION_R2_20261016.md` §6.)
> 7. **External appointments, as recorded in my own record.**
>    * B1, conformance check: appointed and launched by me; identity B1-External (Codex); brief sha256
>      `732922a543bda0e3be5fb304eaf8a5d751a5975a0fce1e152050473fa60d08e3`; Phase 1 recorded; report released with
>      sha256 `cf1a4b18a08132da09ad4bc717c92b6f1056a949199394d15778708192e48e41`. B1's independence from the
>      coordinating environment is not established by this record.
>    * B2, incident-review reading: [identity, brief sha256 `e7b9ca962aa6d2ff90e5b4980852352f3216c07d439bef9a0572e5c40d93c210`, date].
>    * B3, provenance trace and T6 finding, under brief r2 after B2's release: [identity, brief r2 sha256, date].
>
>    Each reports to me directly. I release each output, with its sha256, by pushing it to branch
>    `owner-review/cell308-<B1|B2|B3>` or by giving it to the coordinator side.

**External action, no change from R3:** launch B2, and B3 after B2's release, per handoff §2 and addendum A1. The
coordinator side cannot do this: an agent it launches is inside its environment.

## 3. Statement 1A: issue only after B1's correction confirmation and the B2 / B3 corrections are recorded

This statement holds the owner-reserved determinations of S12 Q8 (checklist rows Q8-6 to Q8-8). The coordinator side
gives the facts (checklist §3) and no recommendation.

> **Owner statement 1A, [date].**
> 1. **Material change (Q8-6).** Having seen the changes listed in `S12_STANDING_CHECKLIST_Q8_20261016.md` §3, I
>    determine that they are [material / not material] to the S12 rating.
> 2. **Standing (Q8-8).** For the decisions in statements 2 and 3, I [do / do not] require a risk rating with
>    independent standing beyond the existing advice.
> 3. **External rating (Q8-7 / Q8-8).** If item 1 is "material" or item 2 is "do", I appoint and launch, outside the
>    coordinator's session and account, with brief `ledger/briefs/S12X_EXTERNAL_RISK_RATING_CLOUD_R1.txt`
>    (sha256 [as in handoff addendum A1]): [identity]. That rater is not reviewerS12, reviewerFR1 or reviewerFR2, nor
>    B1, B2 or B3, nor any coordinator session. It reports to me directly. Otherwise I record that the S12 rating
>    stays advice, and that no rating on this route has standing beyond advice.

## 4. Statement 2: issue only after A5, A6, A8, A9, A12 (and A13 if commissioned) are recorded

The text is as in R3 §3, with three changes:
* matrix R4 replaces R3;
* procedure r3 erratum E1 and L-DET erratum E3 are added;
* the reference addendum is adopted expressly.

> **Owner statement 2, [date]. Issued with no new-host reading in view.**
> 1. **T6 transfer:** [as B3 finds]. The coordinator side gives no recommended answer here: T6's text is in the
>    excluded incident review, which it does not read.
> 2. I adopt, as the proposal for acceptance (precedence: later errata over earlier, errata over originals):
>    * amendment r5 with errata E1 and E2;
>    * the L-DET packet with errata E1, E2 and E3;
>    * the H1–H8 plan with errata E1 and E2;
>    * attestation procedure r3 with erratum E1;
>    * package r2 with erratum E1;
>    * readiness matrix R4.
>
>    The rating floor is **not lower than HIGH**.
> 3. I adopt the L-DET reference addendum r1, with L-DET erratum E1 §5's notes, as the reference list: five records by
>    blob id and the function digests. Its standing rests on my adoption of FR1 (statement 1 item 1; L-DET erratum E2.5).
> 4. I decide **MBS-6 (i)** with the finality rule of amendment erratum E2.4, **MBS-7 (i)** and **MBS-8 (ii)**. Each is
>    recorded before OD-1, and states that no new-host runtime, inventory reading or Q12 result existed.
> 5. I decide the 21 D-* items as package r2 rows 1–21, with erratum E1 rows 12, 17, 18 and 20, and H8 DMI required.
> 6. I expressly set aside ROUTE_PREPARATION line 19 for each of the 11 rules listed in package erratum E1 §2.
> 7. I fix **N1 = 24 hours** (response time) and **N2 = 21 days** (interpreter build to marker), as B3-checked. The
>    deadline is never extended. Any update inside the window stops the route on that platform.

## 5. Statement 3: issue only after statement 2

> **Owner statement 3, [date].**
> 1. Host-stage **designations**, each outside the coordinator's reach, with briefs I write or approve:
>    * acceptance reviewers for P1 and P2: [names];
>    * anchor checker(s): [names];
>    * post-marker checker: [name].
>
>    Under procedure r3 erratum E1.2 these are designations, not appointment entries. Each appointment entry is made
>    when its review starts, on a specific attestation sha256.
> 2. **OD-1:** the official host is [machine identifier, provider or ownership record, architecture]. It meets M1–M8 of
>    the plan (erratum E1 §1.1, as amended by E2) and the decided preferences. No MB r1 target-run observation informed
>    this choice. My E1″ status: [as recorded, by name only]. Any property beyond those criteria: [written target-free
>    reason, to be checked by a non-holder].
> 3. I give the coordinator side read-only access to that machine for the Phase-1 inventory, by [for example a Remote
>    Control session I start on it].

**Recommended machine class** (OD-1 recommendation §3; preferences, not requirements, until statement 2 decides them):
* bare metal x86_64;
* ≥ 6 physical cores for the unit's cpuset (8 suggested);
* memory sufficient for the R-MEM / R-FREE floors (32 GiB suggested);
* local SSD;
* Ubuntu 24.04 LTS with systemd;
* readable DMI, thermal zones with trip points, and PSI.

## 6. Later artifact-specific rulings, and the S1 brief

**Rulings not covered by any general instruction** (matrix R4):
* **A2:** the owner countersigns route-audit addendum A2 after OD-1 and before the L-DET interpreter build (row B7).
* **OD-3:** the L-DET authorization, on the OD-3 record (row B13).
* **The pre-freeze decision under §14 / G2** (S16(c), row C4). It is separate from S1.
* **S1:** the successor ruling, and the execution grant (row C6).

Each must be personally issued for the exact artifact when it exists. The owner's continuation instruction of
2026-10-16 authorizes proceeding once those grants are recorded. It does not replace them.

**Requirements carried into the S1 brief** (S12 Q6, S14, S17, S19). R3 §6 is unchanged, plus:
* the rating and its standing, **including S12 Q8-2's UNVERIFIED status** and the owner's statement 1A
  determinations;
* the decisive argument lost;
* the count of consumptions;
* not a rerun on host grounds;
* the finality rule verbatim;
* every host and L-DET attempt;
* the SUBST list and the line-19 set-asides;
* the new constants with their trace;
* the decider's E1″ status (names only);
* the reviewers' standing: the search breach is established, holder status is UNVERIFIED, and B1's independence is
  not established;
* the trigger table (from B2);
* a MATCH is not risk-reducing for the value;
* no figure or runtime next to any cell-308 quantity.
