# Findings status register: FR1, S12, FR2 (Cell-308 Cloud route r1)

**Status: CURRENT STATE RECORD.** Every finding of the three OD-2 reviews, with five separate states. **A disposition
document alone does not close a finding.** A finding is closed only when every state it requires is reached.
`new_target_evaluations = 0` · `cell309_activity = none`.

| code | state | meaning | who reaches it |
|---|---|---|---|
| **PC** | proposed correction | a corrective text exists (file named) | coordinator |
| **VC** | verified conformance | an eligible reviewer, outside the coordinator's environment where required, confirmed the correction meets the finding | handoff B1 (or B2 / B3 where named) |
| **OD** | owner decision | the owner's record adopts the correction or decides the item | owner |
| **IT** | implemented and tested | the successor build implements it, with tests and an implementation review | implementer; implementation reviewer |
| **AX** | authorization to execute | a valid recorded grant for the step it governs | owner (OD-3, S1, grant) |

In the columns below:
* "req" means the state is required, "—" that it is not;
* the **current** state of every finding is **PC only**: no VC, OD, IT or AX has been reached for any finding.

File abbreviations:
* amdE1 / amdE2: amendment r5 errata;
* ldE1 / ldE2: L-DET packet errata;
* hpE1 / hpE2: H1–H8 plan errata;
* r3: attestation procedure r3;
* pkg / pkgE1: D-* package r2 and its erratum;
* mxR3: readiness matrix r3;
* det: search-eligibility determination;
* ncr: new-constant recommendations;
* od2v: OD-2 verbatim supplement.

## FR1 (`af150ef4…b6df`)

| id | PC in | VC | OD | IT | id | PC in | VC | OD | IT |
|---|---|---|---|---|---|---|---|---|---|
| G1 | amdE1.2, amdE2.2 | req | req | — | G20 | pkg, pkgE1 §2 | req | req | — |
| G2 | amdE1.6, amdE2.3 | req | req | — | G21 | ldE1 §1–§2, ldE2.1 | req | req | req |
| G3 | amdE1.1, amdE2.5 | req | req | — | G22 | ldE1 §2, ldE2.2 | req | req | req |
| G4 | amdE1.3, amdE2.7 | req | req | req | G23 | ldE1 §1 | req | req | req |
| G5 | amdE1.4, amdE2.7, hpE2 | req | req | req | G24 | ldE1 §4, ldE2.4 | req | req | req |
| G6 | ldE1 §4, amdE2.1 | req | req | req | G25 | mxR3 | req | — | — |
| G7 | pkg row 20, pkgE1 | req | req | req | G26 | r3 §2–§3 | req | req | req |
| G8 | amdE1.5 | req | req | req | G27 | r3 §2; S12 brief | req | req | — |
| G9 | r3 §1, amdE2.1 | req | req | req | G28 | amdE1.7, amdE2.7 | req | req | — |
| G10 | r3 §5 | req | req | req | G29 | ldE1 §5 | req | — | — |
| G11 | r3 §4, hpE2 | req | req | req | G30 | ldE1 §5 | req | — | — |
| G12 | od2v | req | req | — | G31 | ldE1 §2 | req | req | req |
| G13 | amdE1.8, mxR3 §1 | req | req | — | G32 | hpE1 §2 | req | — | — |
| G14 | pkg row 14 | req | req | — | G33 | mxR3 | req | — | — |
| G15 | pkg row 16 | req | req | req | G34 | FR1 disposition | req | — | — |
| G16 | pkg row 9 | req | req | req | G35 | amdE1.1 | req | req | — |
| G17 | pkg row 5 | req | req | req | G36 | pkgE1 §2 | req | req | — |
| G18 | pkg row 6 | req | req | req | G37 | pkg rows 2–3 | req | req | — |
| G19 | pkg row 8 | req | req | req | G38 | — (B2 records the quotations) | req (B2) | — | — |

## S12 (`9d549eb2…b55c`; rating HIGH, conditional)

| id | sev | PC in | VC | OD | IT |
|---|---|---|---|---|---|
| S1 | BLOCKING | amdE2.4 | req | req (MBS-6 (i) + finality) | — |
| S2 | BLOCKING | amdE2.5, pkgE1 row 17 | req | req (MBS-6/7/8 before OD-1) | — |
| S3 | MAJOR | hpE2; OD-1 recommendation §4 | req | req (OD-1 record content) | — |
| S4 | MAJOR | amdE2.6 | req | req | req |
| S5 | MAJOR | r3 §5; ncr N1 | req, plus B3 for N1 | req | req |
| S6 | MAJOR | amdE2.3 | req, plus B2 (N1–N4, T1–T6 verbatim) | req | — |
| S7 | MAJOR | pkgE1 §1–§2 | req | req | req |
| S8 | MAJOR | pkgE1 §3; ncr | **B3** (non-holder trace, T6 transfer) | req | — |
| S9 | MAJOR | od2v | req | req | — |
| S10 | MINOR | amdE2.3 | req | req | — |
| S11 | MINOR | amdE2.5; mxR3 | req | req | — |
| S12 | MINOR | amdE2.7; hpE2 | req | req | — |
| S13 | MINOR | amdE2.7; ncr N2 | req, plus B3 for N2 | req | req |
| S14 | MINOR | owner package R3 §4 (S1-brief requirements) | req | at S1 | — |
| S15 | MINOR | amdE2.3; owner package R3 | req | req | — |
| S16 | MINOR | amdE2.7 | req | req | — |
| S17 | NOTE | — (B2) | B2 | — | — |
| S18 | NOTE | amdE2.7 | req | req | — |
| S19 | NOTE | owner package R3 §4 | req | at S1 | — |

**S12's own condition:** its HIGH rating holds only if S1 and S2 are corrected **and** its §5 mitigations are adopted
before OD-3. That needs VC and OD for S1, S2 and every §5 item. Owner approval alone is not verification.

## FR2 (`1ad769bb…8cac`)

| id | PC in | VC | OD | IT | id | PC in | VC | OD | IT |
|---|---|---|---|---|---|---|---|---|---|
| K1 | amdE2.1 | req | req | — | K12 | pkgE1 §2, row 18 | req | req | — |
| K2 | r3 §3, §5 | req | req | req | K13 | pkgE1 row 20 | req | req | req |
| K3 | r3 §2 | req | req | — | K14 | ldE2.1–2.3 | req | req | req |
| K4 | r3 §4 | req | req | req | K15 | amdE2.7 | req | req (OD-3 record) | — |
| K5 | r3 §1 | req | req | req | K16 | od2v | req | req | — |
| K6 | r3 §5 | req | req | req | K17 | r3 §1.2 | req | req | req |
| K7 | amdE2.2 | req | req | — | K18 | r3 §2 | req | req | — |
| K8 | amdE2.1, ldE2.4 | req | req | req | K19 | r3 §4 | req | — | — |
| K9 | amdE2.3 | req | req | — | K20 | r3 §1.2–1.3 | req | — | — |
| K10 | r3 §6 | req | req | — | K21 | ldE2.5 | req | req | — |
| K11 | amdE2.7; hpE2 | req | req | — | K22 | hpE2 | req | — | — |

## Other open items (not findings)

| item | state |
|---|---|
| the S12 / FR2 search breach | det: PC; VC optional (B1); OD req |
| FR2 conditions 1–9 | PC for all; VC req (B1) |
| the final-artifact audit report | externally reported; bytes not received |
