# S12 standing checklist: every step of S12 Q8, as gates (Cell-308 Cloud route r1)

**Status: PROPOSED GATE RECORD · NOTHING DECIDED · STANDING AND MATERIALITY ARE OWNER-RESERVED.** This file answers
external B1 finding X2 (`reviews/external/REVIEW_EXTERNAL_B1_CONFORMANCE.md`, `cf1a4b18…8e41`, lines 148–158). It turns
S12 §5 item 14 ("The owner completes the steps of Q8") into separate gates, each with its own evidence, authority,
dependency and status. The matrix (`READINESS_MATRIX_R4_20261016.md`, rows A10–A13) and the owner package
(`OWNER_DECISION_PACKAGE_R4_20261016.md` §2–§3) cite these rows. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The requirement (S12 review, `reviews/REVIEW_S12_RISK_CLOUD_R1.md`, `9d549eb2…b55c`, lines 254–263, verbatim)

> **For full standing the owner would need to:**
> - record, in the owner's own record, adoption of this appointment, naming the brief's sha256 and the agent or session
>   id (the hap2:49–52 identity definition);
> - obtain this review's sha256 directly from the reviewer's reply channel and bind it there;
> - confirm or withdraw the quoted OD-2 sentence;
> - adopt FR1's standing first;
> - treat this rating as provisional until FR2 completes, and re-commission S12 if FR2 changes anything material.
>
> For weight beyond advice, the owner would also commission a second rating from a reviewer outside the coordinator's
> environment (a human, or an agent in a separate owner-started context).

## 2. Checklist

Status values: **OPEN** (an owner action is outstanding); **MET** (evidence named); **UNVERIFIED** (cannot be
established on the available evidence); **CONDITIONAL** (needed only if an owner determination says so); **BLOCKED**
(waits on a named row).

| id | step | evidence now | authority | depends on | status |
|---|---|---|---|---|---|
| Q8-1 | The owner's own record adopts reviewerS12's appointment, naming the brief sha256 (`ledger/briefs/S12_RISK_REVIEW_CLOUD_R1.txt`, `d46c19f7d82905d36f643ac7f003d7130835c4b9868c50ee9939467398a3710d`) and the agent or session id. The identity definition is procedure r2 lines 49–52, carried as procedure r3 §2 | None in the owner's record that the coordinator side can see. The agent id known to the coordinator is coordinator-supplied. If the owner's record can only repeat that id, it must say so | owner | Q8-4 (FR1 first) | **OPEN** |
| Q8-2 | The review's sha256 (`9d549eb2…b55c`) obtained **directly from the reviewer's reply channel** and bound there | The S12 reply was produced inside the coordinator's session (S12 lines 241–244). No owner-direct channel existed for it. A later copy, the coordinator's ledger line, or an owner acknowledgement does **not** retroactively establish that channel | — (historical fact) | — | **UNVERIFIED**, and not attainable for the existing review. It is recorded as unmet. It is never marked MET |
| Q8-3 | The owner confirms or withdraws the quoted OD-2 sentence ("Complete the fresh S12 review using an eligible reviewer") | The text is committed in `USER_AUTHORIZATION_20261016_OD2_VERBATIM_SUPPLEMENT.md` (`94a888814896e42e6ad96959285e1af09e8cda1397155c924df006992efbbd88`). Fidelity to the owner's original message is UNVERIFIED by any external reviewer (B1 line 100). The owner's confirmation is outstanding | owner | — | **OPEN** |
| Q8-4 | The owner adopts FR1's standing **first**: before Q8-1, and before any reliance on S12 | None recorded | owner | — | **OPEN** |
| Q8-5 | The rating is treated as provisional until FR2 completes | FR2 completed on 2026-10-16 (`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR2.md`, `1ad769bb…8cac`). The rating stays provisional until Q8-6 is recorded | — | — | **MET as to FR2's completion**; provisional status continues into Q8-6 |
| Q8-6 | **The owner's material-change determination.** Did FR2, and the corrections made after S12's pinned commit (§3), change anything material to the rating? | §3 lists the changes as facts. No determination recorded. The coordinator side makes no recommendation on materiality | owner (reserved) | the corrections are stable: B1's single correction confirmation recorded (matrix A8), and the B2 / B3 bounded corrections recorded and confirmed (matrix A9) | **BLOCKED**, then **OPEN** |
| Q8-7 | **Re-commissioning of S12** if Q8-6 finds a material change | Handoff prepared: brief `ledger/briefs/S12X_EXTERNAL_RISK_RATING_CLOUD_R1.txt` (prepared, not launched; addendum A1 to the external handoff). The reviewer is a new eligible reviewer. It is never reviewerS12, reviewerFR1 or reviewerFR2, nor B1, B2 or B3, nor this session or any coordinator | owner appoints and launches; the reviewer rates | Q8-6 = material | **CONDITIONAL** |
| Q8-8 | **A distinct eligible external second risk rating**, where the owner requires independent standing beyond the existing advice for any decision | The same prepared brief S12X serves. It is distinct from B1 (a conformance check of text), B2 (a reading) and B3 (a provenance trace). None of those is a risk rating, and none substitutes for one | owner determines whether it is required, and appoints and launches; the reviewer rates | the owner's determination, recorded with Q8-6 | **CONDITIONAL** |

**One external rating can serve Q8-7 and Q8-8 together**, if the owner records that it does. Under either row it must
be launched by the owner outside the coordinator's session and account, and report to the owner directly.

**Gate position.** Every row above is resolved before owner statement 2: done, recorded as UNVERIFIED, or determined
not required. If S12X is commissioned, its output is recorded and given one bounded correction round before statement
2. S12's own outer bound is OD-3 (S12 §3).

**Consequence while Q8-2 stays UNVERIFIED.** The existing S12 rating cannot reach the standing Q8 describes. It stays
**advice**, whatever Q8-1, Q8-3 and Q8-4 record. The rating floor of this route does not depend on S12's standing: it
rests on accepted text (amendment erratum E2.3).

## 3. Facts for Q8-6 (no recommendation)

S12 rated the texts at `6d5f9a63816ad9294afc85b17df0e49e0dec8bf3`. Since then:

| round | files | what changed |
|---|---|---|
| S12 / FR2 disposition (`8acec727`) | amendment erratum E2; procedure r3; package erratum E1; L-DET erratum E2; plan erratum E2; matrix R2; OD-1 recommendation; OD-2 verbatim supplement | S12's own S1–S18 corrections, and FR2's K1–K22 |
| continuation (`f814fe84`) | matrix R3; findings register; search determination r1; new-constant recommendations (N1 = 24 h, N2 = 21 days); owner package r3 | provenance check and T6 ruling moved before D-* adoption; two new owner numbers proposed |
| B1 correction round (this round) | search determination r2; this checklist; matrix R4; owner package R4; procedure r3 erratum E1; L-DET erratum E3; register R2 | B1 X1–X6 |

Whether any of this is material to the rating is the owner's determination alone.

## 4. Not done

* No external rater is appointed, contacted or launched. The coordinator side cannot do that: an agent it launches is
  inside its environment.
* No retired reviewer is reused.
* No determination of materiality or of standing is made or proposed.
