# Owner decision package after OD-2 (Cell-308 Cloud route r1) — one package, one recommended resolution

**Status: FOR THE OWNER · NOTHING HERE IS DECIDED UNTIL THE OWNER RECORDS IT.** The OD-2 phase's commissioned work is
complete. The next step is blocked by a host fact (no machine meeting M1–M8 is reachable) and by owner-reserved
decisions that must come before OD-1. This package lists every owner-reserved item in one place, each with the
recommended answer, so the owner can decide in one record. `DECIDED` is empty. `new_target_evaluations = 0` ·
`cell309_activity = none`.

## 1. The recommended resolution

**Adopt the corrected route as one package, decide the pre-OD-1 items below, then name one bare-metal Linux server
(V-B).**

**Evidence:**
* The session host fails M1, M2, M3, M5 and M8 on observed facts (OD-1 recommendation §2).
* No other machine is reachable from this session.
* FR1 and FR2 accept the route texts and the L-DET specification with conditions. Their conditions are addressed in
  text by two bounded disposition rounds (`FR1_DISPOSITION_20261016.md`, `S12_FR2_DISPOSITION_20261016.md`).
* S12 rates the route HIGH, conditional on its mitigations. Without them its rating is VERY-HIGH, and it then advises
  V-C.

**Exact authority required:** the owner's written decision record, outside this repository, mirrored by a committed
owner statement. No reviewer, coordinator or test can supply it. If the owner does not want the S12 conditions, the
recommendation is **V-C** (close the route; MB-S r1 stays NOT_DERIVED), per S12 Q7.

## 2. Decisions for one owner record (recommended answer in bold)

**A. Standing of the OD-2 reviews and texts**

| # | item | recommended |
|---|---|---|
| A1 | Adopt the appointments of reviewerFR1, reviewerS12 and reviewerFR2 (coordinator-appointed agents under OD-2), and their reviews as advice. Each is identified by its brief sha256, the session `session_01S66r3p84SFdY6Vc4RchSWr`, and the review sha256 in matrix R2 §4 | **adopt, as advice** |
| A2 | Confirm that OD-2's "Complete the fresh S12 review using an eligible reviewer" (full text in `USER_AUTHORIZATION_20261016_OD2_VERBATIM_SUPPLEMENT.md`) covered the coordinator's S12 appointment, including its commissioning before A1 | **confirm** |
| A3 | Adopt the corrected route texts as the proposal for acceptance. The precedence is erratum E2, then E1, then the original: <ul><li>amendment r5 with errata E1 and E2;</li><li>the L-DET packet with errata E1 and E2;</li><li>the plan with errata E1 and E2;</li><li>procedure r3;</li><li>package r2 with erratum E1.</li></ul> | **adopt for acceptance, subject to B1** |
| A4 | Rating floor: **not lower than HIGH**, resting on route A1 §1, route E2 and brief R2 lines 208–209. This supersedes owner brief r5's "unless reviewers and you decide otherwise" | **adopt** |

**B. Reviews and appointments still needed** (reviewers outside the coordinator's environment; FR2 K3, S12 Q8)

| # | item | recommended |
|---|---|---|
| B1 | A bounded conformance check of round 2's corrections and procedure r3, against FR2 §7 conditions 1–9 and S12 §5 | **a human, or an agent the owner launches in a separate session, reporting to the owner** |
| B2 | An eligible reader of `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`. They record N1–N4 and T1–T6 verbatim, and whether T1 fires by construction (amd E2.3) | **appoint**: a non-holder permitted to read it |
| B3 | A non-holder check of the new-constant trace, and a ruling on whether T6's M1–M6 transfer (package E1 §3) | **appoint** |
| B4 | Host-attestation acceptance reviewer(s) for P1 and P2, and the anchor checkers (procedure r3 §2, §5), with their briefs written or approved by the owner | **appoint** after OD-1 |

**C. Decisions before OD-1** (S12 S2 / S11; no new-host reading in view)

| # | item | recommended |
|---|---|---|
| C1 | MBS-6 | **(i), with the finality rule** (amd E2.4): after this route's marker, any outcome ends route MB on 308 on every platform and host |
| C2 | MBS-7 | **(i), members unchanged** |
| C3 | MBS-8 | **(ii)**: caps re-derived by the accepted §3.2 rule from official decoy runtimes on the named host, with no further choice. The Q12 input is deleted |
| C4 | the 21 D-* items | **as package r2 with erratum E1**: rows 1–21 as recommended there; D-PAUSE bare metal with no fallback; H8 DMI required |
| C5 | set ROUTE_PREPARATION line 19 aside for each amended measurement rule (11 rules, package E1 §2) | **set aside, rule by rule, as listed** |
| C6 | the window bound: the maximum interval from the L-DET interpreter build to the marker | **owner number**. The coordinator does not propose one, because it would be an untraced constant |
| C7 | the H7 / anchor-check response time, and the post-marker anchor checker | **owner number and name** |
| C8 | the cross-host marker rule (amd E2.6), the host-attempt disclosure (amd E2.7), and E8 extended | **adopt** |

**D. OD-1 and after**

| # | item | recommended |
|---|---|---|
| D1 | OD-1 | **V-B**: one owner-controlled, single-tenant bare-metal x86_64 Linux server, ≥ 8 physical cores, ≥ 32 GiB, local SSD with ext4, Ubuntu 24.04 LTS with systemd, readable DMI, thermal zones with trips, PSI. The OD-1 record content is in plan E2 |
| D2 | the administrative actions A1–A8 of the OD-1 recommendation §5 | **owner performs them, in that order**. None is performed by this session |
| D3 | D-S15-NEWHOST: name the authoritative MB r1 ref store and commit its first ref listing before OD-3 | **owner** |
| D4 | OD-3, later, with the OD-3 record (the L-DET commit and diff list) | not now |

**E. Evidence the owner can supply at any time**

| # | item |
|---|---|
| E1 | the final-artifact audit report (sha256 `da6adcbe…8174`), so its bytes can be verified. Until then it stays "externally reported" |

## 3. Requirements carried into the S1 brief (S12 Q6, S14, S17, S19)

The S1 brief must state:
* the rating and its standing;
* that the decisive argument is lost (a second, different draw);
* the count of consumptions;
* why the route is not a rerun on host grounds;
* the finality rule, verbatim;
* every host attempt and every L-DET attempt;
* the SUBST list and the line-19 set-asides;
* the new constants with their trace;
* the decider's E1″ status (names only);
* the reviewers' standing;
* the trigger table, quoted by an eligible reader;
* that an L-DET MATCH is not risk-reducing for the value;
* no figure or runtime next to any cell-308 quantity.

## 4. What this session did not do

It made:
* no purchase;
* no provisioning;
* no install;
* no setting change;
* no update disabling;
* no reboot;
* no scientific evaluator, decoy, designated series, L-DET case, qualification, freeze, grant or production execution.

The coordinator read no excluded record and no Cell-309 content. **Two reviewers disclosed accidental contact:**
* **reviewerS12** ran one recursive grep for a literal sentence over `reviews/`, which scanned the bytes of the excluded
  interruption and incident reviews. There was no match and nothing was printed.
* **reviewerFR2** ran the same kind of grep over the whole research tree, which scanned the bytes of the excluded
  ledger disclosure, audit files and incident review, and of a governance file whose name contains "309". There was no
  match and nothing was printed.

Both disclosures are in the reviews, §2, and in the ledger. reviewerFR1's full clone fetched commit and tree objects of
every branch; it inspected none of the Cell-309 objects, and the clone was deleted. It did not use the quota-reset allowance. It did not
change the development source (`9db01504`) and did not re-run the unchanged suites.
