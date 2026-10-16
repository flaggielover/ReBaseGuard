# Readiness matrix and ordered dependency list, revision r4 — Cell-308 Cloud route r1 (the one current matrix)

**Status: CURRENT STATE RECORD · PROPOSED ORDER · NOTHING ACCEPTED OR DECIDED BY THIS FILE.** This revision answers
external B1 finding X3 (`reviews/external/REVIEW_EXTERNAL_B1_CONFORMANCE.md`, `cf1a4b18…8e41`, lines 160–172). It also
places the gates of X2 (S12 Q8), X4 (procedure r3 erratum E1) and X6 (L-DET erratum E3).

**Precedence.**
* R4 supersedes `READINESS_MATRIX_R3_20261016.md` (`61973f2c…81f5dd`) and `READINESS_MATRIX_R2_20261016.md`
  (`3c1345d8…f3648`) as the current matrix. Both are preserved unchanged.
* R2's own supersession of `FORMAL_ROUTE_READINESS_PACKET_20261016.md` §2 (one row), §3, §6 and §7 **continues**
  through R4.
* Unlike R3, R4 does **not** supersede R2 wholesale. §1.2 states, row by row, which R2 corrections survive and where R4
  carries each one. Where R4 and an earlier matrix differ, R4 governs. Where R4 is silent on a surviving R2 correction,
  that R2 correction stands.

`DECIDED` is empty. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. Baseline and source classes

### 1.1 Baseline (verified at the start of the B1 correction round, 2026-10-16)

* The integration branch `codex/cell308-claude-r5-integration` was at `b4d814da9e0f52c33c47c82819c6331998aa0790`.
  There were no newer commits.
* PR3 is draft, open and unmerged.
* PR2 head is `3b2442770ebc68b8c5672786c2213c9da18b5479`.
* The original base `claude/cell-308-github-state-skb1g0` is at `37c62102c0e2e22563760173fb04a1fcf66d5e2f`.
* No `owner-review/*` branch exists.
* The development source is `9db01504`, and native run 38848711278 is unchanged. Suites were not re-run: this round
  changes documents only.
* The final-artifact audit report (`da6adcbe…8174`) is **externally reported**, not received.
* The external B1 report is recorded verbatim (`cf1a4b18…8e41`) and released by the owner
  (`OWNER_RELEASE_B1_20261016.md`).
* A Claude session on the coordinator's account is **not** outside the coordinator's reach.

### 1.2 Source classes (carried from R2 §1; FR1 G13; FR2 condition 8)

**The R2 source-class correction survives and governs.** Brief R2 (`governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md`,
`cda3cf45…ad9c`) is a **reader-checked decision brief**. It is **not** ACCEPTED as a whole:
* its §9 start-gate rows describe the protocol draft (`216c465f`);
* its MBS-5(b) stays accepted through route E2;
* passages quoted as [ACCEPTED] stand only where an accepted text holds them (amendment erratum E1.8).

This replaces the readiness packet §2 row that classes brief R2 ACCEPTED (packet line 40). The packet is preserved
unchanged. Its other §2 classes stand.

### 1.3 Carry-forward of R2 and R3

| earlier element | in R4 |
|---|---|
| R2 §1 baseline rows | replaced by §1.1 (newer baseline); the native-run and audit facts are unchanged |
| R2 §1 **source-class correction** | **survives**: §1.2 |
| R2 row 1 (step 1 inventory) | row B4 |
| R2 rows 2, 3 (session host HOST_UNSUITABLE; DEV_ONLY development) | survive unchanged as facts: row A0 |
| R2 row 4 (formal review as advice) | row A1 |
| R2 row 5 (21 D-*, before the Phase-1 inventory) | row A17 (after B3 and the T6 ruling, per R3's correction) |
| R2 rows 6–8 (A1 / A2 wrapper, A5 pin point, journal reader) | row B8 (successor build items) |
| R2 row 9 (S12 rating as advice) | row A1, with standing in rows A10–A13 |
| R2 row 10 (OD-1) | row B2 |
| R2 rows 11a, 11b (P1, P2) | rows B6, B11, under procedure r3 with erratum E1 |
| **R2 row 12 (L-DET reference list; standing depends on FR1's adoption)** | **survives**: row A16 |
| R2 row 13 (L-DET comparison rule) | row A15 (adoption of the L-DET packet with errata E1–E3) |
| R2 rows 14, 15 (namespace and build; implementation review) | rows B8, B9 |
| R2 row 16 (OD-3) | row B13 |
| **R2 row 17 (S14)** | **survives**: row C2 |
| **R2 row 18 (S16 (a)–(d))** | **survives**: rows C3 and C4 (S16(c) is the distinct owner pre-freeze decision) |
| R2 row 19 (MBS-6/7/8 before OD-1) | row A18 |
| R2 row 20 (D-HOST-LIFETIME) | row A15 (procedure r3 with erratum E1, adopted) |
| R2 row 21 (external anchor record) | rows B6, B11 and each anchored step |
| R2 row 22 (steps 5–9) | rows C5–C7 |
| R2 row 23 (window bound, response time, OD-3 record) | rows A17 (numbers) and B13 (OD-3 record) |
| R2 rows 24, 25 (incident-review reader; non-holder trace and T6) | rows A5, A6, A14 |
| R2 §3 dependency list | replaced by §3, which keeps R3's correction (B3 and the T6 ruling before D-*) |
| R3 §2 rows 1–28 and §3 | replaced by §2 and §3. R3's sequencing correction survives in full. R3 row 13 is split (rows A19 and OPS-1…OPS-12) |

## 2. Gates

**Kinds:**
* **TEXT**: a written rule exists;
* **EXT**: an external review or reading;
* **OD**: an owner decision or record;
* **OPS**: operational evidence produced at that stage, and only then;
* **IT**: implemented and tested;
* **AX**: authorization to execute.

**States:**
* **PC**: a proposed correction exists;
* **VC**: verified textual conformance, by an eligible reviewer whose standing the owner accepts;
* **OD**, **IT**, **AX**: the event of that kind has happened;
* **MET**: evidence named;
* **BLOCKED**: waits on the named rows;
* **OPEN**: an owner action is outstanding now;
* **CONDITIONAL**: needed only if an owner determination says so;
* **UNVERIFIED**.

A PC is not a VC. A VC is not an OD. An OD is not IT. Only an AX authorizes execution.

### 2.1 Stage A: records, external checks, owner decisions (all before any reading of a named machine)

| # | gate | kind | state now | requires | evidence / file | authority |
|---|---|---|---|---|---|---|
| A0 | session host HOST_UNSUITABLE; development DEV_ONLY at `9db01504` | OPS | MET as facts | — | amendment r5 §2.1; review 59; run 38848711278; review 71 | — |
| A1 | OD-2 reviews FR1, S12 (HIGH, conditional), FR2 | EXT | MET as **advice** (standing: A10–A13) | — | reviews verbatim; two dispositions | — |
| A2 | search-breach determination r2 (no certification of absence) | TEXT | PC (this round) | — | `REVIEWER_SEARCH_ELIGIBILITY_DETERMINATION_R2_20261016.md` | O (statement 1, item 6) |
| A3 | **owner statement 1**: FR1 standing first; S12 / FR2 advisory adoption; OD-2 sentence confirmed; the breach recorded without certification; appointment records | OD | **OPEN** | — | owner package R4 §2 | O |
| A4 | B1: appointment, Phase 1, report released | EXT | MET as recorded: B1-External (Codex); report `cf1a4b18…8e41`. **Independence UNVERIFIED** (owner's release) | — | `reviews/external/REVIEW_EXTERNAL_B1_CONFORMANCE.md`; `OWNER_RELEASE_B1_20261016.md` | O |
| A5 | B2: incident-review reading (N1–N4, T1–T6, T6's M1–M6, Q4 premises; sanitised) | EXT | BLOCKED: owner launch and release. B2 may proceed independently on its unchanged brief (pin `f814fe84`) | — | brief B2 (`e7b9ca96…c210`) | B2 reader; O releases |
| A6 | B3: non-holder provenance trace of every new constant and rule (including L-DET E3 and procedure erratum E1) and the T6 transfer finding | EXT | BLOCKED | A5 released, with its digest verified | brief B3 r2 (handoff addendum A1) | B3 checker |
| A7 | bounded corrections of B1 X1–X6 | TEXT | PC (this round) | A4 | `B1_DISPOSITION_20261016.md` | coordinator side |
| A8 | B1's single correction confirmation | EXT (VC of text) | BLOCKED: the owner forwards the correction package | A7 | correction package (handoff addendum A1) | the same B1, through O |
| A9 | bounded corrections of B2 / B3 findings, each confirmed once by the same reviewer | TEXT, EXT | BLOCKED | A5, A6 | — | coordinator side; the same reviewer |
| A10 | S12 Q8 owner records: Q8-1 (S12 appointment with brief sha256 and agent / session id), Q8-3 (OD-2 sentence), Q8-4 (FR1 first) | OD | **OPEN** | — | `S12_STANDING_CHECKLIST_Q8_20261016.md` | O (statement 1) |
| A11 | Q8-2: S12 digest obtained directly from the reviewer's channel | OPS (historical) | **UNVERIFIED**: not attainable for the existing review; never marked MET | — | checklist Q8-2 | — |
| A12 | Q8-6: the owner's material-change determination; also whether independent standing beyond advice is required (Q8-8) | OD | BLOCKED | A8, A9 | checklist §3 (facts only) | O (statement 1A) |
| A13 | Q8-7 / Q8-8: re-commissioned or second external S12 rating (S12X), then its one bounded correction round | EXT | CONDITIONAL on A12 | A12 | brief S12X (handoff addendum A1) | O appoints and launches; external rater |
| A14 | **T6 transfer ruling** | OD | BLOCKED | A5, A6, A9 | — | O (statement 2) |
| A15 | **adoption of the corrected route texts**: amendment r5 + E1 + E2; L-DET packet + E1 + E2 + E3; plan + E1 + E2; procedure r3 + erratum E1; package r2 + E1; this matrix | OD | BLOCKED | A8, A9, A12, and A13 if commissioned | — | O (statement 2) |
| A16 | **adoption of the L-DET reference addendum r1 and its reference list** (five records by blob id; function digests), with L-DET E1 §5 notes and E2.5 standing | OD | BLOCKED | A3 (FR1 standing adopted), A15 | `PROPOSED_LDET_REFERENCE_ADDENDUM_R1_20261015.md`; ldE1 §5; ldE2.5 | O (statement 2) |
| A17 | **the 21 D-* decisions**, the line-19 set-asides, N1 and N2 | OD | BLOCKED | **A6, A14**, A15 | ncr; pkgE1 | O (statement 2) |
| A18 | MBS-6 (i) with the finality rule, MBS-7 (i), MBS-8 option: each recorded before OD-1, stating that no new-host runtime, inventory reading or Q12 result existed | OD | BLOCKED | A15 | amendment E2.4–E2.5 | O (statement 2) |
| A19 | **S12 conditions, text and adoption readiness only.** B1 confirms that the written controls for S1, S2 and §5 items 1–14 exist (VC of text), and the owner adopts them (OD). This row certifies **text and adoption only**. It certifies no host record, marker, preflight or later evidence: those are OPS-1…OPS-12 | EXT, OD | BLOCKED | A8, A10, A11 (recorded as UNVERIFIED in statement 1 item 4; it can never be met), A12, A13 if commissioned, A15, A17, A18 | register R2 | B1 (text); O |

### 2.2 Stage B: host stage up to the L-DET attempt

| # | gate | kind | state now | requires | evidence / file | authority |
|---|---|---|---|---|---|---|
| B1 | **owner statement 3**: designations of the P1 / P2 acceptance reviewers (not appointment entries, procedure erratum E1.2), the anchor checkers and the post-marker checker | OD | BLOCKED | A17, A19 | r3 §2, §5; r3 erratum E1 | O |
| B2 | **OD-1**: one machine named, with the plan-E2 record content | OD; OPS-1 | BLOCKED | A17, A18, A19 | OD-1 recommendation; plan E2 | O (statement 3); a non-holder checks any extra property |
| B3 | read-only access for the inventory | OD | BLOCKED | B2 | — | O |
| B4 | Phase-1 read-only inventory (a recorded host attempt; OPS-2) | OPS | BLOCKED | B3 | plan; `lx_inventory.py` | coordinator, on the access given |
| B5 | the owner's H3 actions | OD | BLOCKED | B4 | OD-1 recommendation §5 A4 | O |
| B6 | attestation; P1 appointment entry; P1 review; ledger line (`R`, `C`); anchor | OD, EXT | BLOCKED | B1, B5 | r3; r3 erratum E1.1–E1.2 | O; P1 reviewer |
| B7 | **route-audit addendum A2** (`registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A2.md`). It records the HOST row **CONDITIONAL on the named machine**. Until it exists, the HOST row reads **EXCLUDED** and no official step runs on the machine | TEXT, OD | BLOCKED | A8 (the fresh bounded check of corrected texts), A15, A17, B2 | amendment E1.2; amendment E2.2 | drafted after B2; countersigned in the owner's decision record |
| B8 | design approval; campaign namespace; reviewed successor build: A1 / A2 wrapper, journal reader, A5 pin point, per-part acceptance and rejection lines, `R` / `C` inputs, whole-history all-part veto reading ledger REJECTED and NOT_COMPLETED lines, schema without self-assertion, comparator per L-DET E1–E3 | IT | BLOCKED | A15, A17, B6 | requirements doc; r3 §7 as amended by r3 erratum E1.4 | O (design); implementer |
| B9 | implementation and premeasurement review (including E3's synthetic fixtures) | EXT | BLOCKED | B8 | — | fresh implementation reviewer |
| B10 | L-DET interpreter build: anchored, and the first official step. It starts the N2 window and the V-A runner check (OPS-5, OPS-6) | OPS | BLOCKED | B6, **B7**, B9; the procedure-E1.3 refusal does not hold | L-DET E1 §4; E2.3; r3 §5 | coordinator on the host, under the reviewed procedure |
| B11 | P2 appointment entry, P2 review, ledger line, anchor | OD, EXT | BLOCKED | B9, B10 | r3 §4; r3 erratum E1 | O; P2 reviewer |
| B12 | first S15 ref listing committed and anchored (package E1 row 20 (b′)) | OPS | BLOCKED | B10 | package E1 row 20 | O |
| B13 | OD-3 record (L-DET commit; the diff list; L-DET E3 bound by sha256; the comparator's per-record view declaration), then OD-3 | OD | BLOCKED | A16, B11, B12 | amendment E2.7; L-DET E3.1, E3.3 | O: an artifact-specific ruling |
| B14 | the one L-DET attempt. The exactness control is selected inside the attempt (E3) | AX | BLOCKED | B13 | — | AX by OD-3 |

### 2.3 Stage C: after an L-DET MATCH

| # | gate | kind | state now | requires | evidence / file | authority |
|---|---|---|---|---|---|---|
| C1 | official decoys; caps by the MBS-8 (ii) rule (EVAL_CAP ≤ 24 h, ncr §2) | AX, OPS | BLOCKED | B14 (MATCH) | — | AX per protocol |
| C2 | **S14**: MB r1 §10 steps 6–8 returned EXECUTION_ACCEPTED, the adjudication and ADJUDICATION_ACCEPTED | OPS | **UNVERIFIED here.** The register says met (`a40211cc`, `9ad632c9`, `e451e634`). Those ids are not objects of the clones available to the coordinator side. This round's clone is shallow, so their absence there is not evidence either way (FR1 G33) | — | `SUCCESSOR_CONDITIONS_REGISTER_308.md` S14; governance A1 S14 | the owner, or a reviewer, cites the repository or record that holds them, before C4 |
| C3 | **S16 (a), (b), (d)**: (a) the governance addendum accepted by a delta review; (b) route conditions RC1–RC6 met; (d) S14 holds | OPS | (a) met per the register (not re-verified here); (b) as facts at qualification; (d) = C2 | C2 | register S16; governance A1 S16 | per protocol |
| C4 | **owner pre-freeze decision, S16(c)**: a recorded user decision covering the freeze under §14 / G2. It is **distinct** from the S1 ruling and the execution grant (C6), and is recorded before any freeze | OD | BLOCKED; **OPEN USER DECISION** (register) | C1, C2, C3 (a) | governance A1 S16(c); register S16 | O |
| C5 | designation, freeze, qualification (MBR1_REPRO at the frozen commit; S16 (b) facts) | AX, OPS | BLOCKED | C4 | — | per protocol; fresh reviewers |
| C6 | S1 ruling and execution grant (S1 brief per owner package R4 §6) | OD, AX | BLOCKED | C5; A5 (the trigger table) | — | O: personally issued, artifact-specific |
| C7 | preflight, marker, formal execution, closeout | AX | BLOCKED | C6 | — | AX by the grant |

### 2.4 Operational checkpoints of S12's conditions (split out of R3 row 13)

Row A19 can certify only text and adoption. Each item below is evidence that exists only at its own stage. A pre-OD-1
row cannot certify it.

| # | S12 item | evidence, and when it can exist | stage row |
|---|---|---|---|
| OPS-1 | §5 item 3 (S3) | the OD-1 record: one machine and its architecture; criteria M1–M8 only; no MB r1 target-run observation informed it; the decider's E1″ status by name; a non-holder's check of any extra property | B2 |
| OPS-2 | §5 item 10 (S12) | every machine inventoried is recorded, and disclosed in every later brief | B4, and every later brief |
| OPS-3 | §5 item 2 (S2) | the MBS-6/7/8 records, with the "no runtime, no inventory reading, no Q12 result" statement, dated before OD-1 | A18 (dated record); checked again at B2 |
| OPS-4 | §5 item 9 (S11) | the D-* decision record, dated before the Phase-1 inventory | A17; checked at B4 |
| OPS-5 | §5 item 11 (S13) | the window bound, fixed before B4, and monitored from B10 to the marker | B10 → C7 |
| OPS-6 | §5 item 13 (S16) | a measured process list showing no V-A runner, from the L-DET build to the seal | B10 → C7 |
| OPS-7 | §5 item 7 (S7) | each SUBST statement with its measured cross-check, at each step it governs | B4 → C7 |
| OPS-8 | §5 item 4 (S4) | the marker's ref name and id recorded in the owner's record and mirrored in the ledger | C7 (marker) |
| OPS-9 | §5 item 4 (S4) | every later cell-308 preflight on any host asserts both markers | every later preflight |
| OPS-10 | §5 item 5 (S5) | the post-marker checker named and N1 fixed before B4; checks performed after the marker; a lapse is an INCIDENT firing T4 | B1, A17; exercised after C7's marker |
| OPS-11 | §5 items 1, 12 (S1, S18) | the finality rule verbatim in the accepted amendment, the MBS-6 record and the S1 ruling; E8 in every decision document | A15, A18, C6; every decision document |
| OPS-12 | §5 items 6, 8, 14 (S6, S8, S9) | B2's verbatim reading; B3's trace; the Q8 rows | A5, A6, A10–A13 |

## 3. Ordered dependency list

The order **B2 → B3 → bounded corrections → owner T6 ruling → D-* adoption → OD-1 → inventory** is preserved. B1's
correction confirmation and the S12 standing rows are placed inside it.

1. **Statement 1 (owner; may issue now):** rows A3 and A10.
2. **B1's single correction confirmation** (A8), through the owner. It runs in parallel with B2.
3. **B2** returns its sanitised reading. The owner releases it, and the coordinator side records it verbatim (A5).
4. **B3** (after B2) returns. It is recorded verbatim (A6).
5. **Bounded corrections** of B2 and B3 findings, each confirmed once (A9).
6. **Statement 1A (owner):** the material-change determination, and whether standing beyond advice is required (A12).
   If either needs it, S12X runs and is recorded (A13).
7. **Statement 2 (owner)**, with no new-host reading in view:
   * the **T6 ruling** (A14);
   * **adoption** of the corrected texts and the reference list (A15, A16);
   * the **D-* decisions**, set-asides, N1 and N2 (A17);
   * MBS-6/7/8 (A18).

   A19 closes at text and adoption level.
8. **Statement 3 (owner):** designations (B1), then **OD-1** (B2), then access (B3).
9. **Inventory** (B4), then rows B5–B14 in order. Route audit A2 (B7) exists before the interpreter build (B10).
10. Rows C1–C7 in order. C4 (the pre-freeze decision) and C6 (S1 and the grant) are separate owner rulings. OD-3 (B13)
    and C6 need artifact-specific rulings when their artifacts exist.

## 4. What the coordinator side can do while A3–A13 are pending

* Record the external outputs the owner releases, and make their bounded corrections.
* Nothing on the critical path beyond that. The successor build (B8) waits for the adopted design: writing it now would
  build an unadopted design, and would also invalidate the `9db01504` validation binding without an adopted reason.
