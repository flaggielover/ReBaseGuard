# Readiness matrix and ordered dependency list, revision r2 — Cell-308 Cloud route r1 (the one current matrix)

**Status: CURRENT STATE RECORD · NOTHING ACCEPTED OR DECIDED BY THIS FILE.** This supersedes
`FORMAL_ROUTE_READINESS_PACKET_20261016.md` §3, §6 and §7 (preserved unchanged). It applies the corrections of formal
review FR1: F7, G3, G11, G25 and G33. `DECIDED` is empty. `new_target_evaluations = 0` · `cell309_activity = none`.

Status values:
* **MET** (with evidence);
* **UNMET** (evidence missing);
* **OPEN_DECISION** (a decision is missing);
* **BLOCKED** (waits on a named earlier row).

Authority: only the owner (**O**) brings a rule into force. Reviewers advise. **I** = implementation reviewer.

## 1. Baseline

| item | value |
|---|---|
| integration branch | `codex/cell308-claude-r5-integration`; PR3 draft, open, unmerged |
| readiness baseline | `29d79e70` (packet); OD-2 phase commits `de160b56`, `6b3aac20`, `e9c42a97`, `6d5f9a63`, `6df68a62`, `45a52623` and later |
| development source | `9db01504` (`lx_platform.py` `da32ce8c…6389`), unchanged |
| native run | 38848711278: 230 tests, 207/207 mutants, 208 suites, git 2.55.0 |
| final-artifact audit | artifact 12025299365, ZIP sha256 `49c5f5b4…86aa2` (GitHub digest). External audit report sha256 `da6adcbe…8174`: **externally reported**. The report was never supplied to this session, so its hash is not verified here and its content not inspected. Unchanged suites were not re-run |
| PR2 / original base | PR2 head `3b244277`; base branch `claude/cell-308-github-state-skb1g0` at `37c62102`, both unchanged |

## 2. Matrix

| # | gate | status | evidence | missing | authority |
|---|---|---|---|---|---|
| 1 | step 1: inventory of the official host | BLOCKED (row 10: OD-1) | session-host inventories r1–r3 are illustration only | an official host | O |
| 2 | session host classification | MET: HOST_UNSUITABLE | amendment r5 §2.1; review 59; OD-1 recommendation §2 (fails M1, M2, M3, M5, M8 on observed facts) | — | — |
| 3 | development implementation (DEV_ONLY) | MET as development | `9db01504`; run 38848711278; review 71 | not an implementation review | — |
| 4 | formal route / governance review | MET as advice: FR1 (ROUTE_TEXTS and LDET_SPEC ACCEPTED_WITH_CONDITIONS; ATTESTATION_PROCEDURE NOT_ACCEPTED); bounded check FR2: see §4 | `reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md`; FR1 disposition; FR2 | the owner's adoption of FR1 and FR2 and their appointments | O |
| 5 | 21 D-* decisions | OPEN_DECISION (all 21) | `CONSOLIDATED_DSTAR_PACKAGE_R2_20261016.md` (FR1 F2 per item) | owner decisions | O |
| 6 | A1 / A2 operational wrapper | BLOCKED (rows 5, 14) | requirements A1.1–A2.4 (`OPERATIONAL_WRAPPER_READER_PINPOINT_REQUIREMENTS_20261016.md`) | implementation and review | O design; I |
| 7 | A5 pin point | BLOCKED (row 14) | requirements P1–P4 | the successor build; D-PIN-POINT | O; I |
| 8 | journal reader (L′) | BLOCKED (rows 5, 14) | requirements J1–J6 | implementation, tests, independent review | I |
| 9 | fresh S12 rating | see §4 | `reviews/REVIEW_S12_RISK_CLOUD_R1.md` | the owner's adoption of the appointment | O |
| 10 | official host (OD-1) | OPEN_DECISION; **external blocker** | `OD1_HOST_RECOMMENDATION_20261016.md` (recommendation V-B); no machine reachable | an owner decision and a named machine | O |
| 11a | attestation acceptance part 1 (H1, H3, H6, H7, H8) | BLOCKED (rows 10, 21) | procedure r2 §4 | inventory, H3 actions, attestation, appointed reviewer | O; appointed reviewer |
| 11b | attestation acceptance part 2 (H2, H5) | BLOCKED (row 15) | procedure r2 §4 | the reviewed implementation | O; appointed reviewer |
| 12 | L-DET reference list | MET as review advice: FR1 re-derived it independently on a history-complete clone and it agrees with the addendum | FR1 F4; L-DET erratum E1 §5 | the owner's adoption | O |
| 13 | L-DET comparison rule | OPEN_DECISION | L-DET erratum E1 §1–§2 (resolves the three open questions) | FR2 check; the owner's adoption | O |
| 14 | step 3: campaign namespace and reviewed successor build | BLOCKED (rows 4, 5, 9, 10, 19) | — | — | O design approval |
| 15 | step 4: implementation and premeasurement review | BLOCKED (row 14) | — | — | I (fresh) |
| 16 | OD-3 (L-DET authorization) | BLOCKED (rows 4, 5, 9, 11a, 11b, 12, 13, 15, 19-MBS-7) | — | — | O |
| 17 | S14 | MET per the register (`a40211cc`, `9ad632c9`, `e451e634` are not objects of this repository; UNVERIFIED here, FR1 G33) | register | — | — |
| 18 | S16 (a)–(d) freeze gates | (a), (d) MET per the register; (b) UNMET; (c) OPEN_DECISION (owner §14 / G2) | register | — | O |
| 19 | MBS-6, MBS-7, MBS-8 | OPEN_DECISION (owner). **MBS-7 before OD-3** (FR1 G3) | register; brief R2 §4–§6 | owner decisions | O |
| 20 | D-HOST-LIFETIME mechanism (procedure r2) | OPEN_DECISION; see §4 for FR2's verdict on r2 | `HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R2_20261016.md` | the owner's adoption | O |
| 21 | external anchor record | BLOCKED (row 20) | procedure r2 §5 | the owner's record | O |
| 22 | steps 5–9 (designated series … grant, target) | BLOCKED; not authorized | ROUTE_PREPARATION | everything above, then S1 | O (S1) |

## 3. Ordered dependency list (corrected)

1. **OD-2.** Done: FR1, its disposition, S12 and FR2 (§4).
2. **The owner adopts or rejects** the reviews and their appointments, the corrected route texts (amendment r5 with
   erratum E1, L-DET packet with erratum E1, procedure r2, plan with erratum E1), and the D-* rulings. At the same time
   the owner expressly sets ROUTE_PREPARATION line 19 aside for each amended measurement rule.
3. **MBS-7** recorded (FR1 G3).
4. **OD-1**: the owner names one machine (recommended: V-B, OD-1 recommendation §3), or decides V-C. V-C ends here.
5. Phase-1 read-only inventory on that machine.
6. The owner's H3 actions, no later than the L-DET interpreter build (G5).
7. The attestation, then acceptance part 1 (row 11a), then the ledger line and the anchor.
8. Owner design approval, then the campaign namespace and the reviewed successor build (D-PIN-POINT, the journal
   reader, the A1 / A2 wrapper). After that, D-INTERPRETER's build on the host under the reviewed procedure.
9. The implementation and premeasurement review.
10. Acceptance part 2 (row 11b).
11. **OD-3**, then exactly one L-DET attempt at the named commit. A mismatch or an incomplete attempt stops the route on
    that platform.
12. Only after a match: MBS-6 and MBS-8, S16(c), the prospective designation policy, steps 5–9 with the official
    MBR1_REPRO at qualification, and S1. None of this is authorized now.

## 4. Review results of the OD-2 phase

[Completed after S12 and FR2: see the final section.]
