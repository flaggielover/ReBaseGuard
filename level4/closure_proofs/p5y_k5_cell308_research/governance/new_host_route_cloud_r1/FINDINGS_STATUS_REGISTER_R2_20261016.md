# Findings status register, revision r2: FR1, S12, FR2 and external B1 (Cell-308 Cloud route r1)

**Status: CURRENT STATE RECORD.** This revision answers external B1 finding X5 (`reviews/external/REVIEW_EXTERNAL_B1_CONFORMANCE.md`,
`cf1a4b18…8e41`, lines 186–194).

**Precedence.** It supersedes `FINDINGS_STATUS_REGISTER_20261016.md` (r1, `5aa3e0e1…b4b4`), which is preserved
unchanged. Where they differ, r2 governs.

**A disposition document alone closes nothing.** **No finding has reached VC, OD, IT or AX.** That denial carries over
from r1 unchanged. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. States

Each finding's **current state** is the highest state reached in this chain. A finding is closed only when every state
it requires is reached.

| code | state | meaning | who reaches it |
|---|---|---|---|
| **NC** | no corrective artifact yet | no text proposes a correction | — |
| **PP** | partial proposed coverage | a text proposes part of the required correction; the rest is named | coordinator side |
| **PC** | complete proposed correction | a text proposes the whole required correction (file named) | coordinator side |
| **VC** | verified textual conformance | an eligible reviewer, outside the coordinator's environment where required, confirmed the text meets the finding, **and the owner has accepted that reviewer's standing** | B1 (or B2 / B3 where named); standing by O |
| **OD** | owner decision | the owner's record adopts the correction or decides the item | owner |
| **IT** | implemented and tested | the successor build implements it, with tests and an implementation review | implementer; implementation reviewer |
| **AX** | execution authorization | a valid recorded grant for the step it governs | owner (OD-3, S1, grant) |

**Columns.**
* **cover**: the current state (NC, PP or PC; nothing higher is reached).
* **PC in**: the corrective texts, by the abbreviations in §5.
* **text check**: what a reviewer has reported on the written correction.
  * **B1 MET** or **B1 PARTLY**: B1's report.
  * **FR2 met**: FR2's advisory check of round 1.
  * **new**: corrected in this round. Not yet checked. Its state is PC, not VC.
  * **—**: not checked by anyone.
* **VC / OD / IT**: "req" means required. "—" means not required. "at S1" means required in the S1 brief or ruling.

**Why no VC is recorded yet.** B1's results are MET or PARTLY on written text, but the owner's release says B1's
independence is not established. VC is recorded for an item only when the owner accepts B1's standing for it (matrix
R4, rows A8 and A19). A correction written in this round is PC until B1's single confirmation **and** that acceptance.

## 2. FR1 (`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md`, `af150ef4…b6df`)

| id | cover | PC in | text check | VC | OD | IT |
|---|---|---|---|---|---|---|
| G1 | PC | amdE1.2, amdE2.2; mxR4 B7 (A2 gate, new) | FR2 met; B1 MET (K7, cond. 9); A2 gate new | req | req | — |
| G2 | PC | amdE1.6, amdE2.3; S12 brief | B1 MET (cond. 6; S12 item 6) | req | req | — |
| G3 | PC | amdE1.1, amdE2.5 | FR2 met; B1 MET (S12 item 2) | req | req | — |
| G4 | PC | amdE1.3, amdE2.7 | FR2 met; B1 MET (K15) | req | req | req |
| G5 | PC | amdE1.4, amdE2.7, hpE2 | FR2 met; B1 MET (K11) | req | req | req |
| G6 | PC | ldE1 §4, ldE2.4, amdE2.1 | B1 MET (cond. 1) | req | req | req |
| G7 | PC | pkg row 20, pkgE1 row 20 | FR2 met; B1 MET (K13) | req | req | req |
| G8 | PC | amdE1.5 | FR2 met. The re-read bound ≤ 3 goes to B3 | req, plus B3 | req | req |
| G9 | PC | r3 §1, amdE2.1, r3E1.1 (new) | B1 MET (cond. 5); r3E1 new | req | req | req |
| G10 | PC | r3 §5 | FR2 met; B1 MET (cond. 5) | req | req | req |
| G11 | PC | r3 §4, hpE2, r3E1.3 (new) | B1 PARTLY (cond. 4) → corrected (new) | req | req | req |
| G12 | PC | od2v | B1 MET (cond. 7, text); owner confirmation outstanding (Q8-3) | req | req | — |
| G13 | PC | amdE1.8; **mxR4 §1.2** (new; restored from mxR2 §1) | B1 X3 → corrected (new) | req | req | — |
| G14 | PC | pkg row 14 | FR2 met | req | req | — |
| G15 | PC | pkg row 16 | FR2 met | req | req | req |
| G16 | PC | pkg row 9 | FR2 met | req | req | req |
| G17 | PC | pkg row 5 | FR2 met | req | req | req |
| G18 | PC | pkg row 6 | FR2 met | req | req | req |
| G19 | PC | pkg row 8 | FR2 met | req | req | req |
| G20 | PC | pkg §2, pkgE1 §2 | B1 MET (S12 item 7) | req | req | — |
| G21 | PC | ldE1 §1–§2, ldE2.1 | FR2 met | req | req | req |
| G22 | PC | ldE1 §2, ldE2.2, **ldE3** (new; replaces E2.2) | B1 PARTLY (X6) → corrected (new) | req | req | req |
| G23 | PC | ldE1 §1 (structural floor) | FR2 met | req | req | req |
| G24 | PC | ldE1 §4, ldE2.4 | B1 MET (cond. 1) | req | req | req |
| G25 | PC | **mxR4** (new; supersedes mxR3) | B1 PARTLY (X3) → corrected (new) | req | — | — |
| G26 | PC | r3 §2–§3, r3E1.1 (new) | B1 MET (cond. 3) | req | req | req |
| G27 | PC | r3 §2; S12 brief; r3E1.2 (designations are not appointments) | B1 MET (cond. 6). The owner's naming is outstanding | req | req | — |
| G28 | PC | amdE1.7, amdE2.7 | B1 MET (S12 item 13) | req | req | — |
| G29 | PC | ldE1 §5 | — | req | req (A16) | — |
| G30 | PC | ldE1 §5 | — | req | req (A16) | — |
| G31 | PC | ldE1 §2 | FR2 met | req | req | req |
| G32 | PC | hpE1 §2 | — | req | — | — |
| G33 | PC | **mxR4 row C2** (new; S14 labelled UNVERIFIED, with a named evidence step) | — | req | — | — |
| G34 | PC | FR1 disposition | — | req | — | — |
| G35 | PC | amdE1.1 | FR2 met | req | req | — |
| G36 | PC | pkgE1 §2 (the set-aside list) | B1 MET (S12 item 7) | req | req (A17) | — |
| G37 | PC | pkg rows 2–3 | FR2 met | req | req | — |
| G38 | **NC** | — (B2 records the quotations) | — | req (B2) | — | — |

## 3. S12 (`reviews/REVIEW_S12_RISK_CLOUD_R1.md`, `9d549eb2…b55c`; rating HIGH, conditional)

| id | sev | cover | PC in | text check | VC | OD | IT |
|---|---|---|---|---|---|---|---|
| S1 | BLOCKING | PC | amdE2.4 | B1 MET | req | req (MBS-6 (i) + finality; S1 ruling) | — |
| S2 | BLOCKING | PC | amdE2.5, pkgE1 row 17 | B1 MET | req | req (MBS-6/7/8 before OD-1) | — |
| S3 | MAJOR | PC | hpE2 (S3); OD-1 recommendation | B1 MET (item 3) | req | req (OD-1 record; mxR4 OPS-1) | — |
| S4 | MAJOR | PC | amdE2.6 | B1 MET (item 4) | req | req | req |
| S5 | MAJOR | PC | r3 §5; ncr N1 | B1 MET (item 5); N1 goes to B3 | req, plus B3 | req | req |
| S6 | MAJOR | **PP** | amdE2.3 (floor: PC). The verbatim N1–N4 / T1–T6 reading: **NC**, awaits B2 | B1 MET (item 6, floor) | req, plus B2 | req | — |
| S7 | MAJOR | PC | pkgE1 §1–§2 | B1 MET (item 7) | req | req | req |
| S8 | MAJOR | **PP** | pkgE1 §3, ncr (the requirement and its order: PC). The non-holder trace itself: **NC**, awaits B3 | B1 MET (item 8, requirement and order) | **B3** | req | — |
| S9 | MAJOR | PC | od2v; **Q8 checklist** (new) | B1 PARTLY (item 14) → corrected (new). Q8-2 is UNVERIFIED and is recorded as unmet | req | req | — |
| S10 | MINOR | PC | amdE2.3 | — | req | req | — |
| S11 | MINOR | PC | amdE2.5; mxR4 A17 | B1 MET (item 9) | req | req | — |
| S12 | MINOR | PC | amdE2.7; hpE2 | B1 MET (item 10) | req | req | — |
| S13 | MINOR | PC | amdE2.7; ncr N2 | B1 MET (item 11); N2 goes to B3 | req, plus B3 | req | req |
| S14 | MINOR | PC | **owner package R4 §6** (S1-brief requirements) | — | req | at S1 | — |
| S15 | MINOR | PC | amdE2.3; owner package R4 §1 (the floor stated) | — | req | req | — |
| S16 | MINOR | PC | amdE2.7 | B1 MET (item 13) | req | req | — |
| S17 | NOTE | **NC** | — (B2 lists T1–T6 verbatim) | — | B2 | — | — |
| S18 | NOTE | PC | amdE2.7 | B1 MET (item 12) | req | req | — |
| S19 | NOTE | PC | **owner package R4 §6** | — | req | at S1 | — |

**S12's own condition.** Its HIGH rating holds only if S1 and S2 are corrected **and** its §5 mitigations are adopted
before OD-3. That needs VC and OD for S1, S2 and every §5 item: matrix R4 row A19 for text and adoption, and
OPS-1…OPS-12 for operational evidence. Owner approval alone is not verification.

## 4. FR2 (`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR2.md`, `1ad769bb…8cac`)

| id | cover | PC in | text check | VC | OD | IT |
|---|---|---|---|---|---|---|
| K1 | PC | amdE2.1 | B1 MET (cond. 1) | req | req | — |
| K2 | PC | r3 §3, §5; r3E1.1–E1.2 (new) | B1 MET (cond. 2); recording of rejection new | req | req | req |
| K3 | PC | r3 §2 | B1 MET (cond. 3) | req | req | — |
| K4 | PC | r3 §4; r3E1.3 (new) | B1 PARTLY (cond. 4) → corrected (new) | req | req | req |
| K5 | PC | r3 §1.1–§1.2; r3E1.1 (new) | B1 MET (cond. 5) | req | req | req |
| K6 | PC | r3 §5 | B1 MET (cond. 5) | req | req | req |
| K7 | PC | amdE2.2; mxR4 B7 | B1 MET (cond. 9) | req | req | — |
| K8 | PC | amdE2.1, ldE2.4 | B1 MET (cond. 1, 9) | req | req | req |
| K9 | PC | amdE2.3 | B1 MET (cond. 9) | req | req | — |
| K10 | PC | r3 §6 | — | req | req | — |
| K11 | PC | amdE2.7; hpE2 | B1 MET (cond. 9) | req | req | — |
| K12 | PC | pkgE1 §2, row 18 | B1 MET (cond. 9) | req | req | — |
| K13 | PC | pkgE1 row 20 | B1 MET (cond. 9) | req | req | req |
| K14 | PC | ldE2.1–E2.3; **ldE3** (new) | B1 PARTLY (cond. 9; X6) → corrected (new) | req | req | req |
| K15 | PC | amdE2.7 | B1 MET (cond. 9) | req | req (OD-3 record) | — |
| K16 | PC | od2v | B1 MET (cond. 7, text) | req | req | — |
| K17 | PC | r3 §1.2; r3E1.4 (new) | B1 MET (cond. 5) | req | req | req |
| K18 | PC | r3 §2 | — | req | req | — |
| K19 | PC | r3 §4 | — | req | — | — |
| K20 | PC | r3 §1.2–§1.3 | — | req | — | — |
| K21 | PC | ldE2.5 | — | req | req | — |
| K22 | PC | hpE2 | — | req | — | — |

**FR2 §7 conditions 1–9** (B1 item 1):

| cond. | cover | text check |
|---|---|---|
| 1 | PC | B1 MET |
| 2 | PC | B1 MET (rejection recording made explicit: r3E1, new) |
| 3 | PC | B1 MET |
| 4 | PC | B1 PARTLY → r3E1.3 (new) |
| 5 | PC | B1 MET |
| 6 | PC | B1 MET |
| 7 | PC | B1 MET (text). The owner's confirmation is outstanding |
| 8 | PC | B1 PARTLY → mxR4 (new) |
| 9 | PC | B1 PARTLY (K14) → ldE3 (new) |

## 5. External B1 (`reviews/external/REVIEW_EXTERNAL_B1_CONFORMANCE.md`, `cf1a4b18…8e41`)

| id | sev | cover | PC in | text check | VC | OD | IT |
|---|---|---|---|---|---|---|---|
| X1 | MAJOR | PC | det R2; owner package R4 §2 item 6 | new | req (B1 confirmation) | req | — |
| X2 | MAJOR | PC | Q8 checklist; owner package R4 §2–§3; mxR4 A10–A13; brief S12X (prepared) | new | req (B1 confirmation) | req | — |
| X3 | MAJOR | PC | mxR4 | new | req (B1 confirmation) | req (A15) | — |
| X4 | MINOR | PC | r3E1 | new | req (B1 confirmation) | req (A15) | req |
| X5 | MINOR | PC | this register | new | req (B1 confirmation) | — | — |
| X6 | MINOR | PC | ldE3; brief B3 r2 | new | req (B1 confirmation) | req (A15) | req |

## 6. Other open items (not findings)

| item | state |
|---|---|
| the S12 / FR2 search breach | det R2: PC. Holder status UNVERIFIED (no certification). OD required (statement 1, item 6) |
| S12 standing (Q8) | checklist: Q8-1, Q8-3, Q8-4 OPEN; Q8-2 UNVERIFIED (unattainable); Q8-5 met as to FR2; Q8-6 BLOCKED; Q8-7, Q8-8 CONDITIONAL |
| S14 evidence | UNVERIFIED here (mxR4 C2) |
| S16(c), the owner's pre-freeze decision | OPEN USER DECISION (mxR4 C4) |
| the final-artifact audit report | externally reported; bytes not received |

## 7. Abbreviations

All files are in `governance/new_host_route_cloud_r1/` unless stated.
* **amdE1 / amdE2**: amendment r5 errata.
* **ldE1 / ldE2 / ldE3**: L-DET packet errata.
* **hpE1 / hpE2**: H1–H8 plan errata.
* **r3**: procedure r3. **r3E1**: its erratum E1.
* **pkg / pkgE1**: D-* package r2 and its erratum.
* **mxR4**: readiness matrix r4.
* **det R2**: search-eligibility determination r2.
* **ncr**: new-constant recommendations.
* **od2v**: OD-2 verbatim supplement.
* **Q8 checklist**: `S12_STANDING_CHECKLIST_Q8_20261016.md`.
* **owner package R4**: `OWNER_DECISION_PACKAGE_R4_20261016.md`.
* **brief S12X / brief B3 r2**: under `ledger/briefs/`, prepared in handoff addendum A1.

**Corrected references from r1:**
* G13 pointed to "mxR3 §1", which has no source-class row. Now **mxR4 §1.2**.
* G25 and G33 pointed to mxR3. Now **mxR4** and **mxR4 C2**.
* S14 and S19 pointed to "owner package R3 §4". The content was in R3 §6. Now **owner package R4 §6**.
* r1's "the current state of every finding is PC only" was inaccurate: G38 and S17 are **NC**, and S6 and S8 are
  **PP**. r1's "PC for all" FR2 conditions hid condition 8's incompleteness. Both universal claims are withdrawn.
