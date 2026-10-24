# Owner decision package, revision r3 (Cell-308 Cloud route r1): one resolution, three statements in dependency order

**Status: FOR THE OWNER · NOTHING HERE IS EFFECTIVE UNTIL THE OWNER ISSUES IT, AND EACH STATEMENT ONLY AFTER ITS
PREREQUISITES ARE RECORDED.** This supersedes `OWNER_DECISION_PACKAGE_OD2_20261016.md` (preserved). It applies the
sequencing correction of `READINESS_MATRIX_R3_20261016.md`: the provenance check and the T6 ruling come **before** the
D-* decisions.

The owner's stated direction (2026-10-16) is "to continue on one compliant, owner-controlled host under the reviewed
safeguards". The recommended resolution follows that direction. `DECIDED` is empty. `new_target_evaluations = 0` ·
`cell309_activity = none`.

Source bindings: every file named here is listed with its sha256 in `EXTERNAL_REVIEW_HANDOFF_20261016.md` §5, at the
pinned commit named there.

## 1. The recommended resolution

The route proceeds on one owner-controlled, single-tenant Linux machine. It proceeds only through the gates of matrix
R3, with:
* S12's mitigations adopted **and** independently verified;
* the external checks done outside the coordinator's reach;
* every decision taken before any new-host reading exists.

If B1 finds S1, S2 or any S12 §5 item unmet and uncorrectable, the S12 condition fails. The S12 advice then applies:
V-C, close the route with MB-S r1 left at NOT_DERIVED. That is reported as a finding; no run is launched.

## 2. Statement 1: issue now (no prerequisite outstanding)

> **Owner statement 1 (Cell-308 Cloud route r1), [date].**
> 1. I adopt reviewerFR1, reviewerS12 and reviewerFR2 as coordinator-appointed advisory reviewers under my OD-2
>    instruction. Their reviews (sha256 `af150ef4…b6df`, `9d549eb2…b55c`, `1ad769bb…8cac`) are advice. They do not
>    satisfy any requirement for an independent or owner-launched reviewer.
> 2. I confirm that my OD-2 instruction's sentence "Complete the fresh S12 review using an eligible reviewer" covered
>    the coordinator's S12 appointment and its commissioning.
> 3. I adopt `REVIEWER_SEARCH_ELIGIBILITY_DETERMINATION_20261016.md` §5:
>    * no E1″ exposure arose from the disclosed searches;
>    * the breach is recorded;
>    * reviewerS12 and reviewerFR2 take no later role on this route.
> 4. I appoint and launch, outside the coordinator's session and account, with the briefs of
>    `EXTERNAL_REVIEW_HANDOFF_20261016.md`:
>    * reviewer **B1**, conformance check: [name or account];
>    * reader **B2**, incident-review reading: [name or account];
>    * checker **B3**, non-holder provenance trace and T6 transfer finding: [name or account].
>
>    Each reports to me directly. I will release each output, with its sha256, by pushing it to branch
>    `owner-review/cell308-<B1|B2|B3>` or by giving it to the coordinator.

**Exact external action:** launch B1, B2 and B3 per handoff §2. The coordinator cannot do this: an agent it launches is
inside its environment.

## 3. Statement 2: issue only after B1, B2 and B3 are recorded and their bounded corrections re-verified

The text is ready. The recommended answers come from package r2 with erratum E1, the amendment errata and the
new-constant recommendations, each **subject to B3 and B1 not finding otherwise**.

> **Owner statement 2, [date]. Issued with no new-host reading in view.**
> 1. **T6 transfer:** [as B3 finds]. The coordinator gives no recommended answer here, because T6's text is in the
>    excluded incident review, which the coordinator does not read.
> 2. I adopt, as the proposal for acceptance (precedence E2 > E1 > original):
>    * amendment r5 with errata E1 and E2;
>    * the L-DET packet with errata E1 and E2;
>    * the H1–H8 plan with errata E1 and E2;
>    * attestation procedure r3;
>    * package r2 with erratum E1;
>    * readiness matrix R3.
>
>    The rating floor is **not lower than HIGH**.
> 3. I decide **MBS-6 (i)** with the finality rule of amendment erratum E2.4, **MBS-7 (i)** and **MBS-8 (ii)**.
> 4. I decide the 21 D-* items as package r2 rows 1–21 with erratum E1 rows 12, 17, 18 and 20, and H8 DMI required.
> 5. I expressly set aside ROUTE_PREPARATION line 19 for each of the 11 rules listed in package erratum E1 §2.
> 6. I fix **N1 = 24 hours** (response time) and **N2 = 21 days** (interpreter build to marker), as B3-checked. The
>    deadline is never extended, and any update inside the window stops the route on that platform.

## 4. Statement 3: issue only after statement 2

> **Owner statement 3, [date].**
> 1. Host-stage appointments, each outside the coordinator's reach, with briefs I write or approve:
>    * acceptance reviewers for P1 and P2: [names];
>    * anchor checker(s): [names];
>    * post-marker checker: [name].
> 2. **OD-1:** the official host is [machine identifier, provider or ownership record, architecture]. It meets M1–M8
>    of the plan (erratum E1 §1.1, as amended by E2) and the decided preferences. No MB r1 target-run observation
>    informed this choice. My E1″ status: [as recorded, by name only].
> 3. I give the coordinator read-only access to that machine for the Phase-1 inventory, by [for example a Remote
>    Control session I start on it].

**Recommended machine class** (OD-1 recommendation §3). These are preferences, not requirements, until statement 2
decides them:
* bare metal x86_64;
* ≥ 6 physical cores for the unit's cpuset (8 suggested);
* memory sufficient for the R-MEM / R-FREE floors (32 GiB suggested);
* local SSD;
* Ubuntu 24.04 LTS with systemd;
* readable DMI, thermal zones with trip points, and PSI.

The coordinator cannot know which owner-controlled machines exist. No access from this container does not mean none
exists.

## 5. Later artifact-specific rulings (not covered by any general instruction)

* **OD-3:** the L-DET authorization, on the OD-3 record (amendment erratum E2.7).
* **S1:** the successor ruling, and the execution grant.

Both must be personally issued for the exact artifacts when they exist. The owner's continuation instruction of
2026-10-16 authorizes proceeding once those grants are recorded. It does not replace them.

## 6. Requirements carried into the S1 brief (S12 Q6, S14, S17, S19)

Unchanged from the OD-2 package §3: the rating and its standing; the decisive argument lost; the count of consumptions;
not a rerun on host grounds; the finality rule verbatim; every host and L-DET attempt; the SUBST list and the line-19
set-asides; the new constants with their trace; the decider's E1″ status (names only); the reviewers' standing; the
trigger table (from B2); a MATCH is not risk-reducing for the value; no figure or runtime next to any cell-308 quantity.
