# Disposition of formal route review FR1 (Cell-308 Cloud route r1) — bounded corrections

**Status: COORDINATOR DISPOSITION · PROPOSED · NOTHING ACCEPTED OR DECIDED.** This responds to
`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md` (sha256 `af150ef4493f2601a7a17ecbecebc02ae4f237e3f3fcfe5914d0e11af704b6df`),
recorded verbatim. FR1's verdicts:
* ROUTE_TEXTS ACCEPTED_WITH_CONDITIONS;
* LDET_SPEC ACCEPTED_WITH_CONDITIONS;
* ATTESTATION_PROCEDURE NOT_ACCEPTED.

FR1 raised 38 findings: 0 BLOCKING, 12 MAJOR, 16 MINOR, 10 NOTE. As FR1 states, its verdicts bring nothing into force.
This disposition does not restart the development-review cycle and is not review 72. Reviewed files are not edited;
every correction is a new file. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. Correction files

| file | corrects |
|---|---|
| `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5_ERRATUM_E1.md` | G1, G2, G3, G4, G5, G8, G13, G28, G35, G36 |
| `LDET_SPECIFICATION_PACKET_ERRATUM_E1_20261016.md` | the packet's three open questions; G4, G6, G21, G22, G23, G24, G29, G30, G31 |
| `HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R2_20261016.md` | G9, G10, G11, G26; F5 circularity |
| `CONSOLIDATED_DSTAR_PACKAGE_R2_20261016.md` | F2 (all 21 rows); G7, G14–G20, G36, G37 |
| `HOST_EVIDENCE_PLAN_H1_H8_ERRATUM_E1_20261016.md` | F3 criteria; G5, G11, G15, G28, G32 |
| `ledger/briefs/S12_RISK_REVIEW_CLOUD_R1.txt` (the commissioned S12 brief) | G2 (rating floor in Q1), G27 (s12:29 delegation option removed) |
| `READINESS_MATRIX_R2_20261016.md` (written after the S12 and FR2 results) | G25, G11, G33, F7 |

## 2. Finding by finding

| id | sev | disposition | where |
|---|---|---|---|
| G1 | MAJOR | accepted; HOST row CONDITIONAL with four sufficient conditions; the S4 instrument is route-audit addendum A2 after the owner's adoption | amd E1.2 |
| G2 | MAJOR | accepted; "not lower than HIGH" | amd E1.6; package row 1; S12 brief Q1 |
| G3 | MAJOR | accepted; members are [OPEN] MBS-7, recorded before OD-3 | amd E1.1; matrix R2 |
| G4 | MAJOR | accepted; L-DET is a pre-gate; MBR1_REPRO still runs and is not a repeat; L-DET bound to a named commit | amd E1.3; L-DET E1 §3 |
| G5 | MAJOR | accepted; window from the L-DET interpreter build; L-DET pins binding afterwards | amd E1.4; plan E1 §2 |
| G6 | MAJOR | accepted; L-PIN amended for a non-dpkg interpreter (provenance plus prefix manifest). The source-built recommendation is kept | L-DET E1 §4; package row 2 |
| G7 | MAJOR | accepted; the authoritative store is named by the owner, with an owner-supplied value-free ref listing and an exact assertion. Formal refs are never pushed | package row 20 |
| G8 | MAJOR | accepted; exited ⇒ refuse (as L-EXCL already reads); the re-read is a labelled new rule, max 3 | amd E1.5; package row 13 |
| G9 | MAJOR | accepted; C fixes the bytes, and HEAD's full history fixes the veto; C must be an ancestor of HEAD | procedure r2 §1 |
| G10 | MAJOR | accepted; an anchor check before each official step, recorded in the owner's record, fail-closed | procedure r2 §5 |
| G11 | MAJOR | accepted; split acceptance (part 1: H1/H3/H6/H7/H8; part 2: H2/H5 after the implementation review) | procedure r2 §4; plan E1 |
| G12 | MAJOR | **text part done; standing part owner-reserved.** The OD-2 text was committed at `de160b56`, before FR1's phase 2 began (FR1's eligibility was committed at `6b3aac20`, after it). FR1 could not see it because its pinned tree is `29d79e70`. That text says "Select fresh, eligible independent reviewers. Record their identities, assignments and exposure disclosures before substantive review begins", and its work list names FR1's scope. The owner's adoption of FR1's appointment and of this review is one item in the consolidated owner package | `USER_AUTHORIZATION_20261016_OD2.md`; owner package |
| G13 | MINOR | accepted; brief R2 §9 rows reclassed as the protocol draft as described in bR2 | amd E1.8 |
| G14 | MINOR | accepted | package row 14 |
| G15 | MINOR | accepted; physical cores in the unit cpuset | package row 16; plan E1 |
| G16 | MINOR | accepted; keyed on driver, EPP and `platform_profile` | package row 9 |
| G17 | MINOR | accepted; min of three; the claim is withdrawn | package row 5 |
| G18 | MINOR | accepted; defined for the root / no-limit case | package row 6 |
| G19 | MINOR | accepted; lowest trip of any type; a zone with no trip fails; hwmon recorded only | package row 8 |
| G20 | MINOR | accepted; SUBST label and one list | package §2 |
| G21 | MINOR | accepted; (a)∧(b) only; strict `fs` regex with gcd = 1; number tokens | L-DET E1 §1–§2 |
| G22 | MINOR | accepted; exactness control added | L-DET E1 §2 |
| G23 | MINOR | accepted, second option: a structural floor (> 0 per job and case), so no agent parses the records before OD-3 | L-DET E1 §1 |
| G24 | MINOR | accepted; libpython explicit; per-worker pin; post-job mapping check | L-DET E1 §4 |
| G25 | MINOR | accepted | matrix R2 |
| G26 | MINOR | accepted; the reviewer-reported digest goes to the owner; no self-asserted `reviewed` / `accepted`; agent identity defined | procedure r2 §2–§3 |
| G27 | MINOR | **partly accepted.** The host-attestation acceptance reviewer is appointed by the owner (procedure r2 §2). The s12:29 option of delegating to the formal (agent) reviewer is removed. For S12, the owner's OD-2 instruction itself says "Complete the fresh S12 review using an eligible reviewer" and delegates reviewer selection. The coordinator therefore appoints the S12 reviewer under that express instruction. The result is labelled as advice that needs the owner's adoption of the appointment, and that adoption is in the owner package. The stated limit (agents are not independent of the coordinator's environment or model family; not human) is repeated in the S12 brief | S12 brief; owner package |
| G28 | MINOR | accepted; no agent session on the host in the window | amd E1.7; plan E1 |
| G29 | NOTE | accepted | L-DET E1 §5 |
| G30 | NOTE | accepted | L-DET E1 §5 |
| G31 | NOTE | accepted; the comparator sets `sys.set_int_max_str_digits(0)` and records it | L-DET E1 §2 |
| G32 | NOTE | accepted; four restarts reconciled from boot ids | plan E1 §2 |
| G33 | NOTE | accepted; S14 reads "MET per register (ids not objects of this repository; UNVERIFIED here)" | matrix R2 |
| G34 | NOTE | accepted. The Codex integration supplement's HEAD-only veto (its line 17) is **superseded** by the development code's history-wide veto (`_historical_review_blobs`, reviews 64–71). Procedure r2 §1 states the rule. The supplement is preserved unchanged | this row |
| G35 | NOTE | accepted | amd E1.1 |
| G36 | NOTE | accepted; one list of the rules to set aside | package §2; owner package |
| G37 | NOTE | accepted | package rows 2, 3 |
| G38 | NOTE | recorded: the incident-review quotations are verified by the PR2 Codex amendment reviewer, not by FR1 | this row |

## 3. FR1's conditions (§7): status after this disposition

| # | condition | status |
|---|---|---|
| 1 | G12 | text committed (`de160b56`); the owner's adoption is **owner-reserved** |
| 2 | G1 | addressed in text |
| 3 | G2 | addressed in text |
| 4 | G3 | addressed in text; the MBS-7 decision is owner-reserved |
| 5 | G4 | addressed in text |
| 6 | G5 | addressed in text |
| 7 | G6 / G24 | addressed in text |
| 8 | G7 | addressed in text; the store and listing are owner facts |
| 9 | G8 | addressed in text |
| 10 | G21–G23 | addressed in text |
| 11 | G11 / G25 | addressed in text (procedure r2, plan E1, matrix R2) |
| 12 | G13–G20, G35, G37 | addressed in text |
| 13 | ATTESTATION_PROCEDURE | revision r2 written; **its fresh review is required** (FR2) |
| 14 | appointments (G27) | as the G27 row; the owner's adoption is owner-reserved |

FR1 required that conditions 1, 2, 3 and 12 be met before the S12 review is commissioned:
* 2, 3 and 12 are met in text;
* 1 is met as to the committed text. The owner's adoption is outstanding.

The coordinator commissions S12 now, because the owner's instruction orders it ("Complete the fresh S12 review using
an eligible reviewer"). The S12 result is recorded as advice that depends on that adoption.

**Fresh bounded check (FR2).** FR1 requires a fresh bounded re-check of the revised texts before OD-3 is put to the
owner, and a fresh review of procedure r2 before D-HOST-LIFETIME is put to the owner. Both are combined in one fresh
bounded review, FR2. FR2 checks only:
* conditions 2–13 against the correction files;
* the acceptability of procedure r2.

It is not a general review, and this is not a review cycle. FR2's findings get one bounded disposition, and anything
further goes to the owner package.
