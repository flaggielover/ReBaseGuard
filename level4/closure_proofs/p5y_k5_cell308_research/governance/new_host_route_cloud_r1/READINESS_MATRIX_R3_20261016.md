# Readiness matrix and ordered dependency list, revision r3 — Cell-308 Cloud route r1 (the one current matrix)

**Status: CURRENT STATE RECORD · NOTHING ACCEPTED OR DECIDED BY THIS FILE.** This supersedes `READINESS_MATRIX_R2_20261016.md`
(`8acec727`), which is preserved unchanged.

R2 had a **sequencing error**. It placed the owner's D-* decisions (its §3 step 2) **before** the appointment of the
non-holder provenance checker (step 3). S12 §5 item 8 requires the non-holder trace of every new constant and rule, and
a ruling on T6's M1–M6 transfer, **before** the owner decides the D-* items. R3 corrects that and carries it through
every later gate. Finding-level states are in `FINDINGS_STATUS_REGISTER_20261016.md`. `DECIDED` is empty.
`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. Baseline (verified at the start of the continuation, 2026-10-16)

* The integration head on GitHub is `8acec727`; there are no newer commits on any related branch.
* PR3 is draft, open and unmerged.
* PR2 head is `3b244277`.
* Base `claude/cell-308-github-state-skb1g0` is at `37c62102`.
* The development source is `9db01504`, and native run 38848711278 is unchanged. Unchanged suites were not re-run.
* The final-artifact audit report (`da6adcbe…8174`; ZIP `49c5f5b4…86aa2`) is **externally reported**, not received.
* The repository is **public**, so external reviewers can read pinned commits without credentials.
* The coordinator's session can list and read other Claude sessions **on the same account**
  (`list_sessions` / `list_events`). A same-account session is therefore **not** outside the coordinator's reach.

## 2. Gates and their states

States are the five classes:
* **PC** proposed correction;
* **VC** verified conformance;
* **OD** owner decision;
* **IT** implemented and tested;
* **AX** authorization to execute.

Plus **BLOCKED** (waits on a named row) and **MET** (evidence named).

| # | gate | state now | requires (rows) | evidence / file | authority |
|---|---|---|---|---|---|
| 1 | OD-2 reviews FR1, S12, FR2 | MET as advice | — | reviews verbatim; two dispositions | — |
| 2 | search-breach eligibility determination | PC | — | `REVIEWER_SEARCH_ELIGIBILITY_DETERMINATION_20261016.md` | O (statement 1) |
| 3 | external handoffs B1, B2, B3 (briefs, allowlists, channels) | MET as prepared | — | `EXTERNAL_REVIEW_HANDOFF_20261016.md`; briefs B1–B3 | coordinator |
| 4 | appointment and launch of B1, B2, B3 outside the coordinator's reach | **BLOCKED: owner action** | 3 | — | O (statement 1) |
| 5 | B2: incident-review reading (N1–N4, T1–T6, T6's M1–M6, verbatim and sanitised) | BLOCKED | 4 | brief B2 | B2 reader; O releases |
| 6 | B3: non-holder provenance trace of every new constant and rule, plus the T6 transfer finding | BLOCKED | 4, **5** | brief B3; pkgE1 §3; ncr | B3 checker |
| 7 | B1: conformance of round-2 corrections (FR2 §7 conditions 1–9; S12 S1, S2 and §5 items 1–14; this matrix; the register) | BLOCKED | 4 | brief B1 | B1 reviewer |
| 8 | bounded corrections of B1 / B2 / B3 findings, re-verified by the same reviewer once | BLOCKED | 5, 6, 7 | — | coordinator; same reviewer |
| 9 | **T6 transfer ruling** | BLOCKED | 5, 6, 8 | — | O (statement 2) |
| 10 | **adoption of the corrected route texts** (amendment r5 + E1 + E2; L-DET + E1 + E2; plan + E1 + E2; procedure r3; package r2 + E1) | BLOCKED | 7, 8 | — | O (statement 2) |
| 11 | **the 21 D-* decisions**, the line-19 set-asides, and the two new numbers N1 and N2 | BLOCKED | **6, 9**, 10 | ncr; pkgE1 | O (statement 2) |
| 12 | MBS-6 (i) with finality, MBS-7 (i), MBS-8 (ii) | BLOCKED | 7, 8, 10 | amdE2.4–2.5 | O (statement 2) |
| 13 | S12 conditions verified (S1, S2, §5 items 1–14: VC and OD) | BLOCKED | 7, 10, 11, 12 | register | B1 (VC); O (OD) |
| 14 | owner appointments for the host stage: P1 / P2 acceptance reviewers, anchor checkers, post-marker checker | BLOCKED | 11 | r3 §2, §5 | O (statement 3) |
| 15 | OD-1: one owner-controlled machine named, with the plan-E2 record content; read-only access given | BLOCKED | 11, 12, 13 | OD-1 recommendation | O (statement 3) |
| 16 | Phase-1 read-only inventory (a recorded host attempt) | BLOCKED | 15 | plan; `lx_inventory.py` | coordinator, on the access given |
| 17 | the owner's H3 actions | BLOCKED | 16 | OD-1 recommendation §5 A4 | O |
| 18 | attestation, acceptance P1, ledger line, anchor | BLOCKED | 14, 17 | r3 | O; P1 reviewer |
| 19 | design approval; campaign namespace; reviewed successor build (A1 / A2 wrapper, journal reader, A5 pin point, schema without self-assertion, per-part acceptance, ledger veto, comparator per ldE1 / ldE2) | BLOCKED | 10, 11, 18 | requirements doc; r3 §7 item 4 | O (design); implementer |
| 20 | implementation and premeasurement review | BLOCKED | 19 | — | fresh implementation reviewer |
| 21 | L-DET interpreter build (anchored; starts the N2 window) | BLOCKED | 18, 20 | ldE1 §4; ldE2.3 | coordinator on the host, under the reviewed procedure |
| 22 | acceptance P2 (H2, H5) | BLOCKED | 20, 21 | r3 §4 | O; P2 reviewer |
| 23 | OD-3 record (L-DET commit and diff list) and OD-3 | BLOCKED | 21, 22 | amdE2.7 | O: an artifact-specific ruling |
| 24 | the one L-DET attempt | BLOCKED | 23 | — | AX by OD-3 |
| 25 | official decoys; caps by the MBS-8 (ii) rule (EVAL_CAP ≤ 24 h, ncr §2) | BLOCKED | 24 (MATCH) | — | AX per protocol |
| 26 | designation, freeze, qualification (MBR1_REPRO at the frozen commit) | BLOCKED | 25 | — | per protocol; fresh reviewers |
| 27 | S1 ruling and execution grant | BLOCKED | 26 | — | O: a personally issued, artifact-specific ruling |
| 28 | preflight, marker, formal execution, closeout | BLOCKED | 27 | — | AX by the grant |

## 3. Ordered dependency list (corrected)

1. **Statement 1 (owner, now):**
   * adopt the OD-2 reviews' standing and the search-breach determination;
   * appoint and launch B1, B2 and B3 outside the coordinator's reach (handoff §2).
2. **B2** returns its sanitised quotations. The owner releases them. The coordinator records them verbatim.
3. **B3** (after B2) and **B1** (in parallel) return. They are recorded verbatim.
4. Bounded corrections are made, each re-verified once by the same reviewer.
5. **Statement 2 (owner):** issued only after steps 2–4 are recorded, and with no new-host reading in view. It covers:
   * the T6 transfer ruling;
   * adoption of the corrected texts;
   * the 21 D-* decisions;
   * the line-19 set-asides;
   * N1 and N2;
   * MBS-6 (i) with finality, MBS-7 (i) and MBS-8 (ii).
6. **Statement 3 (owner):**
   * host-stage appointments;
   * OD-1, naming one machine with the plan-E2 record content;
   * read-only access to it for the coordinator, for example a Remote Control session the owner starts on that machine.
7. Then rows 16–28 in order. Rows 23 and 27 need separate, artifact-specific owner rulings when their artifacts exist.
   This continuation instruction does not stand in for either.

## 4. What the coordinator can do while rows 4–15 are pending

Nothing on the critical path. Every later row depends on an owner action, an external review, or a machine. The successor
implementation (row 19) waits for the adopted design. Writing it now would build an unadopted design, and it would
also invalidate the `9db01504` validation binding without an adopted reason.
