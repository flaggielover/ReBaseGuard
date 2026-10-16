# Erratum E1 to owner decision package R4 (Cell-308 Cloud route r1): statement 1B after B3's confirmation, and the T6 / N1 / N2 items

**Status: FOR THE OWNER · PREPARED · NOTHING EFFECTIVE UNTIL ISSUED, AND EACH ITEM ONLY AFTER ITS PREREQUISITES.** This
erratum amends `OWNER_DECISION_PACKAGE_R4_20261016.md` (`7eb9951b…faee`), which is preserved unchanged, as aligned by
matrix R4 erratum E1 §E1.2. Where they differ, this erratum governs.

Sources:
* external B3 (`16188ffd…e96a`);
* `T6_TRANSFER_DISPOSITION_20261016.md`;
* matrix R4 erratum E4.

`DECIDED` is empty. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The recommended resolution (direction unchanged)

The route continues on one owner-controlled host under the reviewed safeguards. It continues **without** any claim
that the historical T6 exception transfers.
* T6 and S13 apply as written.
* Role holders are checked against the register by a permitted reader.
* Any prospective safeguard is adopted as a **new** rule, with its own review, and placed at the stage that can produce
  its evidence.

If ER-T6 finds a holder in a route, implementation or caps role, those texts are not adopted until a non-holder
re-derives them. That is a new owner process, reported as a finding. It is never waived.

## 2. Statement 1B (new): the next determination. Issue after B3's single confirmation is released and recorded

> **Owner statement 1B (Cell-308 Cloud route r1), [date].**
> 1. **B3 standing.** I adopt B3-External's report (sha256
>    `16188ffd92313f661dbd5c33d72b831af11a41d0c5a93877736e8896d88ce96a`) and its confirmation (sha256 [as released])
>    as advice. Its eligibility is "no concrete disqualifier identified within available evidence". Full-register
>    non-holder status and platform isolation are UNVERIFIED, and I certify neither.
> 2. **No automatic historical transfer (decided now; needs no further evidence).** I do not carry forward the
>    historical T6 exception: one instance, conditional on M1–M8, with M6 denying precedent. No record on this route
>    may state that any of M1–M8 is satisfied by transfer.
> 3. **T6 and S13 unamended.** No E1″ holder may hold a successor route, implementation, caps or qualification role on
>    Cloud r1.
> 4. **ER-T6.** I appoint [name], who is permitted to read the E1″ register and holds no role on this route, to answer
>    `EVIDENCE_REQUEST_ER_T6_ROLE_HOLDER_CHECK_20261016.md` (sha256 [at the correction commit]), reporting to me only.
> 5. **Material change (S12 Q8-6).** The B3 corrections change provenance statements and add gates (B9-T, A14a, and
>    C1-M3 if adopted). I determine they are [material / not material] to the S12 rating. If "material", S12X runs
>    (statement 1A item 3).

**Why items 2 and 3 can be issued at this point.** They decide not to claim something, and they keep accepted text
unchanged. No evidence is needed for either, beyond B3's confirmation that the record describes the evidence gap
accurately.

## 3. Statement 2 item 1, replaced (issue only after ER-T6 is released and recorded)

> 1. **T6.** Items 2 and 3 of statement 1B stand. Role-holder status per ER-T6 (sha256 [as released]):
>    R1 [..] … R6 [..].
>    * A HOLDER result, or a CANNOT_TELL result, on R1–R3 means the affected texts are **not** adopted under item 2
>      below until a non-holder re-derives them.
>    * **[Only if I choose to rule prospectively]** I adopt the prospective safeguard package of §5 as **new** rules of
>      this route. This is not the historical exception.

## 4. Statement 2 item 7, replaced

> 7. I fix **N1 = 24 hours** and **N2 = 21 days**. These are discretionary recommendations, adopted with the choices
>    C1–C6 and D1–D4 of `NEW_CONSTANT_RECOMMENDATIONS_ERRATUM_E1_20261016.md` in view. Neither is evidence of response
>    capacity or of an update-free window. The 7-day deadline is never extended. Any update inside the window stops the
>    route on that platform, including an urgent fix. A pre-marker stop consumes no target, but it restores no L-DET
>    attempt and erases no host or attestation history.

The statement 2 adoption list also gains:
* the recommendations with erratum E1;
* package r2 with errata E1 and **E2**;
* the provenance record;
* matrix R4 with errata E1–**E4**.

## 5. The prospective safeguard package (draft; a new ruling, not the historical exception)

| id | safeguard | stage | evidence it produces |
|---|---|---|---|
| P1 | an M1-style trace of route-level rules, done (B3, with this round's corrections), **and** of code-level constants at the implementation review by a non-holder | A6 / A9c; B9-T | B3's report and confirmation; the B9-T trace |
| P3 | a non-holder confirms or replaces the memory-cap rule, headroom, exclusivity and allow-list from the official non-holder decoys, before the freeze | C1-M3, before C4 | the C1-M3 record |
| P4 / P5 | every new role appointment on this route (implementer, implementation reviewer, P1 / P2 reviewers, caps deriver, qualification reviewers, the S1 brief's author) is checked by a permitted register reader before the role starts, using ER-T6's form. A HOLDER result refuses the role | each appointment | one register line per appointment |
| P6 | the package licenses **no** holder role and creates no precedent | — | — |

Not covered by the package:
* **M2.** No analogue is proposed: no role on this route is defined to read MB r1 recovery records. If one ever is,
  that role needs its own ruling.
* **M7–M8.** Their definitions were not released, and this package does not claim to cover them. If the owner wants
  them, a new permitted reader (not the retired B2 reader) can extract their definitions only, under a request scoped
  like B2's supplement.

**Authority the package needs** before the owner adopts it:
1. A review of its text by an eligible reviewer outside the coordinator's environment. B3's correction confirmation
   does **not** cover it, because it is new content, not a correction.
2. The owner's statement 1A determination of whether it materially changes the S12 rating, with S12X if so.
3. The owner's adoption, in statement 2.

Until then, it is a draft. No gate depends on it, except C1-M3, which is CONDITIONAL.

## 6. Unchanged

Statements 1, 1A and 3, and R4 §6, stand as aligned by matrix R4 erratum E1 §E1.2.
