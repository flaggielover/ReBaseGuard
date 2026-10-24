# Readiness matrix and ordered dependency list, revision r2 — Cell-308 Cloud route r1 (the one current matrix)

**Status: CURRENT STATE RECORD · NOTHING ACCEPTED OR DECIDED BY THIS FILE.** This supersedes
`FORMAL_ROUTE_READINESS_PACKET_20261016.md` §2 (one row), §3, §6 and §7. The packet is preserved unchanged. Its draft
(commit `66fd25e9`, two sections pending) is completed here.

It applies:
* FR1 F7, G3, G11, G13, G25, G33;
* FR2 condition 8;
* S12 S2 and S11.

`DECIDED` is empty. `new_target_evaluations = 0` · `cell309_activity = none`.

Status values:
* **MET** (with evidence);
* **UNMET**;
* **OPEN_DECISION** (a decision is missing);
* **BLOCKED** (waits on a named row).

Only the owner (**O**) brings anything into force. Reviewers advise. **I** = implementation reviewer.

## 1. Baseline and source classes

| item | value |
|---|---|
| integration branch | `codex/cell308-claude-r5-integration`; PR3 draft, open, unmerged |
| baseline | readiness head `29d79e70`, verified at the start of the OD-2 phase; OD-2 phase commits from `de160b56` |
| development source | `9db01504` (`lx_platform.py` `da32ce8c…6389`), unchanged in this phase |
| native run | 38848711278: 230 tests, 207/207 mutants, 208 suites, git 2.55.0. Unchanged suites were not re-run |
| final-artifact audit | artifact 12025299365; ZIP sha256 `49c5f5b4f54383cd6b56a771ba862d4eb7c7d32e76411da4fcd0c95d1fa86aa2`; report sha256 `da6adcbe1bd27680e1528986e53a321db924667b760c278673ed3afad9278174`. **Externally reported.** The report was not supplied to this session, so its bytes are not verified and its content not inspected. This session did not download the artifact. Not every historical artifact was audited |
| PR2 / original base | `3b244277` / `claude/cell-308-github-state-skb1g0` at `37c62102`, unchanged |
| **source class correction (FR1 G13)** | brief R2 (`USER_DECISION_BRIEF_308_SUCCESSOR_R2.md`) is a **reader-checked decision brief**, not ACCEPTED as a whole. Its §9 start-gate rows describe the protocol draft (`216c465f`). Its MBS-5(b) stays accepted through route E2. This replaces packet §2's ACCEPTED classing of brief R2 |

## 2. Matrix

| # | gate | status | evidence | missing | authority |
|---|---|---|---|---|---|
| 1 | step 1: inventory of the official host | BLOCKED (rows 10, 5, 19) | session-host inventories are illustration only | an official host, after the pre-OD-1 decisions | O |
| 2 | session host classification | MET: HOST_UNSUITABLE | amendment r5 §2.1; review 59; OD-1 recommendation §2 (fails M1, M2, M3, M5, M8 on observed facts) | — | — |
| 3 | development implementation (DEV_ONLY) | MET as development | `9db01504`; run 38848711278; review 71 | not an implementation review | — |
| 4 | formal route / governance review | MET as advice | FR1: ROUTE_TEXTS ACCEPTED_WITH_CONDITIONS, LDET_SPEC ACCEPTED_WITH_CONDITIONS, ATTESTATION_PROCEDURE NOT_ACCEPTED. FR2: FR1_CONDITIONS MET_WITH_EXCEPTIONS, procedure r2 ACCEPTED_WITH_CONDITIONS. Corrections in two dispositions | the owner's adoption; an owner-launched conformance check of round 2's corrections | O |
| 5 | 21 D-* decisions | OPEN_DECISION (all 21) | package r2 plus erratum E1 | owner decisions, **before the Phase-1 inventory** (S12 S11) | O |
| 6 | A1 / A2 operational wrapper | BLOCKED (rows 5, 14) | requirements A1.1–A2.4 | implementation and review | O design; I |
| 7 | A5 pin point | BLOCKED (row 14) | requirements P1–P4 | the successor build | O; I |
| 8 | journal reader (L′) | BLOCKED (rows 5, 14) | requirements J1–J6 | implementation, tests, independent review | I |
| 9 | fresh S12 rating | MET as advice: **HIGH, conditional** (VERY-HIGH without S1 / S2 and the §5 mitigations; Q7 prefers V-C) | `reviews/REVIEW_S12_RISK_CLOUD_R1.md` | the owner's adoption of the appointment and the rating | O |
| 10 | official host (OD-1) | OPEN_DECISION; **external blocker** | OD-1 recommendation: V-B with the S12 package; no machine reachable | the pre-OD-1 decisions; a named machine | O |
| 11a | attestation acceptance P1 (H1, H3, H4, H6, H7, H8) | BLOCKED (rows 10, 20) | procedure r3 §4 | inventory, H3 actions, attestation, an owner-appointed reviewer | O; appointed reviewer |
| 11b | attestation acceptance P2 (H2, H5) | BLOCKED (row 15) | procedure r3 §4 | the reviewed implementation | O; appointed reviewer |
| 12 | L-DET reference list | MET as advice (FR1 re-derivation; standing depends on the owner's adoption, L-DET E2.5) | FR1 F4 | the owner's adoption | O |
| 13 | L-DET comparison rule | OPEN_DECISION | L-DET errata E1, E2 | the owner's adoption | O |
| 14 | step 3: campaign namespace and reviewed successor build | BLOCKED (rows 4, 5, 9, 10, 19) | — | — | O design approval |
| 15 | step 4: implementation and premeasurement review | BLOCKED (row 14) | — | — | I (fresh) |
| 16 | OD-3 (L-DET authorization) | BLOCKED (rows 4, 5, 9, 11a, 11b, 12, 13, 15, 19, 23) | — | — | O |
| 17 | S14 | MET per the register (`a40211cc`, `9ad632c9`, `e451e634` are not objects of this repository; UNVERIFIED here) | register | — | — |
| 18 | S16 (a)–(d) | (a), (d) MET per the register; (b) UNMET; (c) OPEN_DECISION | register | — | O |
| 19 | MBS-6, MBS-7, MBS-8 | OPEN_DECISION. **Before OD-1** (S12 S2; FR1 G3) | register; brief R2 | owner decisions: recommended MBS-6 (i) with the finality rule (amd E2.4), MBS-7 (i), MBS-8 (ii) | O |
| 20 | D-HOST-LIFETIME mechanism | OPEN_DECISION | procedure r3 | an owner-launched conformance check of r3; the owner's adoption | O |
| 21 | external anchor record | BLOCKED (row 20) | procedure r3 §5 | the owner's record | O |
| 22 | steps 5–9 (designated series … grant) | BLOCKED; not authorized | ROUTE_PREPARATION | everything above, then S1 | O (S1) |
| 23 | pre-OD-3 owner numbers and records: window bound, response time, OD-3 record with the L-DET commit | OPEN_DECISION | amd E2.7; r3 §5 | owner numbers (before the inventory) and the OD-3 record | O |
| 24 | eligible reader of the incident review (N1–N4, T1–T6 verbatim) | UNMET | amd E2.3 | a reader permitted to open it | O appoints |
| 25 | non-holder check of the new-constant trace; T6 M1–M6 transfer ruling | UNMET | package E1 §3 | an owner-appointed non-holder | O |

## 3. Ordered dependency list

1. **OD-2.** Done in this session: FR1, its disposition, S12, FR2, and the second disposition.
2. **Owner adoption package** (`OWNER_DECISION_PACKAGE_OD2_20261016.md`). The owner adopts or rejects:
   * the reviews and their appointments;
   * the corrected route texts;
   * the finality rule.

   The owner also:
   * decides **MBS-6 (i), MBS-7 (i), MBS-8 (ii)** and **all 21 D-* items**;
   * sets ROUTE_PREPARATION line 19 aside per amended rule;
   * fixes the window-bound and response-time numbers.

   None of this is done with any new-host reading in view.
3. The owner-launched conformance check of the round-2 corrections and procedure r3. Owner appointments: the
   acceptance reviewer(s), the anchor checkers, the incident-review reader and the constant-trace checker.
4. **OD-1**: one named machine (V-B, OD-1 recommendation §3), with the OD-1 record content of plan E2. Or V-C, which
   ends the route.
5. Phase-1 read-only inventory, recorded as a host attempt.
6. The owner's H3 actions.
7. The attestation, then acceptance P1, then the ledger line and the anchor.
8. Owner design approval, the campaign namespace, the reviewed successor build, then the implementation and
   premeasurement review.
9. The L-DET interpreter build (anchored; the H1 / H3 / H8 window starts here).
10. Acceptance P2.
11. The OD-3 record (the L-DET commit and its diff list), then **OD-3**, then exactly one L-DET attempt. A mismatch or
    an incomplete attempt stops the route on that platform.
12. Only after a match: the caps by MBS-8 (ii)'s rule from official decoys, S16(c), the prospective designation policy,
    steps 5–9 with MBR1_REPRO at qualification, and S1, with the S1-brief requirements of S12 Q6. Not authorized now.

## 4. Review results of the OD-2 phase

| review | verdict | file (sha256) | disposition |
|---|---|---|---|
| FR1 formal route / governance | ROUTE_TEXTS ACCEPTED_WITH_CONDITIONS; LDET_SPEC ACCEPTED_WITH_CONDITIONS; ATTESTATION_PROCEDURE NOT_ACCEPTED; 0 BLOCKING · 12 MAJOR · 16 MINOR · 10 NOTE | `REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md` (`af150ef4…b6df`) | `FR1_DISPOSITION_20261016.md` |
| S12 risk | HIGH, conditional; 2 BLOCKING · 7 MAJOR · 7 MINOR · 3 NOTE | `REVIEW_S12_RISK_CLOUD_R1.md` (`9d549eb2…b55c`) | `S12_FR2_DISPOSITION_20261016.md` |
| FR2 bounded check | FR1_CONDITIONS MET_WITH_EXCEPTIONS; procedure r2 ACCEPTED_WITH_CONDITIONS; 0 BLOCKING · 4 MAJOR · 13 MINOR · 5 NOTE | `REVIEW_FORMAL_ROUTE_CLOUD_R1_FR2.md` (`1ad769bb…8cac`) | `S12_FR2_DISPOSITION_20261016.md` |

All three reviewers are fresh agents appointed by the coordinator under the owner's OD-2 instruction. They are not
human and not independent of the coordinator's environment. Their eligibility statements were committed before their
substantive phases. Their verdicts are advice.
