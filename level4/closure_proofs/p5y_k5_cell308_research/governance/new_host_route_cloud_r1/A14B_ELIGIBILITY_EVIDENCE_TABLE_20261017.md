# A14b eligibility evidence table (Cell-308 Cloud route r1), 2026-10-17 — prepared for the owner

**Status: PREPARED EVIDENCE TABLE · AUTHOR-PREPARED · NO DETERMINATION · NOTHING DECIDED.** This file lists, for each
person or role whose eligibility A14b must weigh, the following:
* the accepted condition that applies;
* the evidence that already exists;
* the one remaining fact that is actually needed;
* who can decide it.

It does not decide anything.
* It invents no clearance standard, no person, no signature and no ruling.
* It makes no non-holder finding from the absence of a label, or from someone being newly appointed.
* `DECIDED` stays empty.

`new_target_evaluations = 0` · `cell309_activity = none`.

Sources:
* the ER-T6 report (`reviews/external/READING_EXTERNAL_ER_T6_ROLE_HOLDERS.md`, `e2bcb406…dcbc4`; receipt
  `OWNER_RELEASE_ER_T6_REPORT_20261017.md`);
* ER-T6 r2 §3 (`fac34cb9…f0a`);
* governance A1 S13 and erratum E1 D3 (accepted);
* `REVIEWER_SEARCH_ELIGIBILITY_DETERMINATION_R2_20261016.md` (`09e5af4b…78d4`);
* the briefs index;
* this session's own metadata.

No excluded record, other conversation or private transcript was read to write this table.

## 1. The accepted conditions, and what they do not say

| id | accepted text | what it requires |
|---|---|---|
| **C1** | S13 (A1, accepted by erratum E1's DELTA_ACCEPTED), with D3 | No E1″ holder may take a successor **route, implementation or caps** role. reviewGOV and reviewADJ are holders |
| **C2** | S13, second bullet | The successor's route, implementation and caps agents **have not seen** the observations. "The builder … must **disclose** any prior reading" (instruction of 2026-09-29) |
| **C3** | S13 | No successor brief contains the observations, or points to REVIEW_EXECUTION_INTERRUPTION §4b |

**Missing authority.** The governing texts do not supply a criterion for any of the following. These are the
owner's to decide, and nothing below assumes an answer.

| id | question no accepted text answers |
|---|---|
| **MA1** | What counts as having "read" a location, for the register's conduct-defined classes (L92, L122)? In particular, does **a byte scan by a process**, with no content reaching the agent's context, count? (Search-eligibility r2 §2 keeps these two things apart) |
| **MA2** | What evidence is enough to treat a subject as **outside** those classes? The accepted mechanism is **self-disclosure** (C2). No text requires proof that no historical exposure occurred, and none is proposed here |
| **MA3** | Does C1's bar on route, implementation and caps roles extend to **reviewers**, and to whether their outputs may support adoption? ER-T6 r2 §5's "HOLDER ⇒ cannot support adoption" is author-proposed, not adopted |
| **MA4** | Does the owner accept the ER-T6 report as A14b evidence, given that its reader's independence (Q5) is UNVERIFIED and it ran in the coordinator's environment? |

**A required fact is not a demand for absolute proof.** The remaining facts below are bounded and can be answered:
* an identity: which participant a label names;
* a set-membership fact: whether a path a subject is recorded as touching is one of the register's L111–L116
  locations;
* a disclosure: the subject's own statement under C2.

## 2. The table: one row per subject

Abbreviations:
* *ER* = the ER-T6 report row; all are CANNOT_TELL.
* *brief excl.* = the subject's brief carried this route's exclusion instruction for the register, REVIEW_EXECUTION_INTERRUPTION and MB r1 target-run paths, and a disclosure instruction. The counts were taken by process from the coordinator's own briefs.

| row | subject | role on Cloud r1 | conditions | evidence already available | remaining fact actually needed | who decides |
|---|---|---|---|---|---|---|
| R1a | `claude_cloud_coordinator_20261014`, `session_01S66r3p84SFdY6Vc4RchSWr` (this coordinator) | route design; dev implementation; brief author | C1, C2, C3 | ER [U], [K]. The session was created **2026-10-14T18:46:28Z** (own session metadata), after the S13 instruction (2026-09-29) and the E1″ heading date (2026-09-30, per the reader at L79). Standing exclusions held in this context. **Self-disclosure (C2):** no known reading of the register, an REVIEW_EXECUTION_INTERRUPTION record, the incident review, `audit/*` or MB r1 target-run material. Limit: the earliest part of this session survives only in summaries, so completeness is **UNVERIFIED** | **Q1:** which session is the register's "the coordinator" (L3, "the main agent of this session"). Only the register's author or the owner knows this | owner (fact); owner (MA2) |
| R1b | other sessions under the same label | unknown | C1, C2 | ER [M]. None in permitted records | **Q1:** whether any exist, and their ids (the owner's own session list) | owner |
| R2 | `claude_cloud_worker_20261016_b1corr`, `session_01VGbYdSMrEaoYpdb386rCWk` | author of the B1 correction round | C1 if route-text authorship counts as a route role; C2 | ER [N], [K]. Ledger label and session id only | its **C2 disclosure**, which no permitted record holds; MA3 if its role is not a route role | owner |
| R3a | `codex_cell308_r5_integration_coordinator` | integration and implementation | C1, C2 | ER [U], [K]. Label only | **Q1:** the Codex thread behind it; whether it is the register's L3 "coordinator"; its C2 disclosure | owner |
| R3b | `fresh_codex_r5_sync_independent_code` | code review | C2; MA3 | ER [N], [K]. Label only | Q1 (thread); C2 disclosure | owner |
| R3c-1 | "coordinator recording independent code/evidence reviews" | unknown | C1, C2 | ER [U], [K], [M] | **Q1:** which participant this sublabel denotes, if any | owner |
| R3c-2 | "fresh independent evidence reviewer" | review | C2; MA3 | ER [N], [K], [M] | Q1, as for R3c-1 | owner |
| R4-59 | `reviewCLOUD_R1` (subagent of R1a) | dev and route review | C2; MA3 | ER [N], [K]. Brief excl. (brief 59). Its own report's self-statement exists but is **not re-examined** here | MA3. If the review role is barred: a bounded check of its recorded tool calls against L111–L116, by a party permitted to know those paths | owner (MA3); owner (who checks) |
| R4-60 | `reviewCLOUD_R1_DELTA` | as R4-59 | C2; MA3 | as R4-59 (brief 60) | as R4-59 | owner |
| R4-61 | `reviewCLOUD_R1_DELTA2` | as R4-59 | C2; MA3 | as R4-59 (brief 61) | as R4-59 | owner |
| R4-62 | `reviewCLOUD_R1_DELTA3` | as R4-59 | C2; MA3 | as R4-59 (brief 62) | as R4-59 | owner |
| R4-63 | `reviewCLOUD_R1_DELTA4` | as R4-59 | C2; MA3 | as R4-59 (brief 63) | as R4-59 | owner |
| R4-64 | `reviewREVIEW63_REPAIR` | as R4-59 | C2; MA3 | as R4-59 (brief 64) | as R4-59 | owner |
| R4-65 | `reviewREVIEW64_REPAIR` | as R4-59 | C2; MA3 | as R4-59 (brief 65) | as R4-59 | owner |
| R4-66 | `reviewREVIEW65_REPAIR` | as R4-59 | C2; MA3 | as R4-59 (brief 66) | as R4-59 | owner |
| R4-67 | `reviewREVIEW66_REPAIR` | as R4-59 | C2; MA3 | as R4-59 (brief 67) | as R4-59 | owner |
| R4-68 | `reviewREVIEW67_REPAIR` | as R4-59 | C2; MA3 | as R4-59 (brief 68) | as R4-59 | owner |
| R4-69 | `reviewREVIEW68_REPAIR` | as R4-59 | C2; MA3 | as R4-59 (brief 69) | as R4-59 | owner |
| R4-70 | `reviewREVIEW69_REPAIR` | as R4-59 | C2; MA3 | as R4-59 (brief 70) | as R4-59 | owner |
| R4-71 | `reviewREVIEW70_REPAIR` | as R4-59 | C2; MA3 | as R4-59 (brief 71) | as R4-59 | owner |
| R5a | `reviewerFR1` (subagent of R1a) | formal route review (OD-2) | C2; MA3 | ER [N], [K]. Brief excl. The coordinator's transcript audit found no excluded output in the forms it covered. This is **COORDINATOR-REPORTED** (search-eligibility r2 §4) | MA3 only. No byte-scan event is recorded for it | owner |
| R5b | `reviewerFR2` (subagent of R1a) | formal conditions check (OD-2) | C2; MA3; **MA1** | ER [N], [K]. **ESTABLISHED:** one recursive grep over all of NS. It byte-scanned the register, `audit/*`, REVIEW_EXECUTION_INTERRUPTION*, the incident review and `K5_AUDIT_EXCL_309.md` (search-eligibility r2 §3). It reports that nothing from them was printed. That report is not independently verified | **MA1**, the decisive fact here. Then whether any scanned path is among L111–L116. The reader says the register itself is not a listed location | owner |
| R5c | `reviewerS12` (subagent of R1a) | S12 risk rating | C2; MA3; **MA1** | ER [N], [A], [K]. **ESTABLISHED:** a recursive grep byte-scanned REVIEW_EXECUTION_INTERRUPTION* and the incident review. It reports nothing printed. Launched by the coordinator on 2026-10-16 (briefs index, row S12) | **MA1**; whether the scanned paths are among L111–L116; **Q1:** whether `reviewINC2` (L118, "the incident re-rating reviewer") is the same participant. The owner's records of the MBS-1 re-rating would show this | owner |
| R6a | `B1-External (Codex)` | external conformance check | C2; MA3 | ER [N], [K]. Owner-recorded identity. Isolation not certified | Q1 (thread id); its C2 disclosure (its report's own statement); MA3 | owner |
| R6b | `B3-External`, Codex thread `01a1449c-7b38-7273-a5b4-9364ee8a50a5` (owner-released) | external provenance check | C2; MA3 | ER [N], [K]. The thread id is not in the register. Its own reports state its exposure position (`16188ffd…e96a`, `6a721ada…253c`). Isolation not certified | MA3; the owner's acceptance of its self-statement under MA2 | owner |

## 3. Participants outside ER-T6's rows

| subject | evidence | remaining fact | who decides |
|---|---|---|---|
| **the owner** | Owner statement of 2026-10-17: never personally saw the observations. No accepted bar has been found (`OWNER_CLARIFICATION_AND_ER_T6_ROUTING_CORRECTION_20261017.md` §3) | none for the owner's role as decider. The owner holds no successor route, implementation or caps role | — |
| **ER-T6-Metadata-Reader** | report §1 and §7. It holds the register's names and locations and two event-time anchors. Retired from every role | none: it takes no role | — |
| **future appointees** (the A6b tracer, implementer, caps, qualification) | none yet. They have not been named | after MA1–MA2 are decided, a C2 disclosure from each appointee, and whatever the MA2 standard requires. A register lookup on a new name would return [K] CANNOT_TELL by construction, so **the MA2 standard, not another lookup, is what decides it** | owner |

## 4. What this table establishes

* **Q3 (register coverage):** supplied for all 24 rows by the ER-T6 report. Bounded; all CANNOT_TELL.
* **Q1 (identity):**
  * R1a: mapped to this session, but **not** mapped to the register's L3 "coordinator";
  * R2: mapped to a label and session id;
  * R6b: thread id supplied by the owner;
  * all other rows: open.
* **Q2 (source completeness):** UNKNOWN. Only snapshot `00d4df45` was read. The register digest is reported, not
  independently supplied.
* **Q4 (actual exposure):** UNVERIFIED for every row.
  * Two byte-scan events are ESTABLISHED (R5b, R5c), and their significance depends on MA1.
  * Self-disclosures exist where noted.
* **Q5 (independence):** UNVERIFIED. The reader shares the coordinator's environment.

**The single gating item is MA1–MA4, and they are the owner's.** Until the owner states a criterion, every row is
blocked on authority, not on fact-finding. The remaining facts per row are listed so that the criterion can be
applied once stated.

## 5. Proposed owner statement 4 (A14b criterion): a template, not issued

Every bracket is the owner's to fill. No option is pre-selected, and no factual commitment is made on the owner's
behalf.

> **Owner statement 4 (Cell-308 Cloud route r1, A14b criterion), [date].**
> 1. **ER-T6 evidence (MA4).** I [accept / do not accept] `READING_EXTERNAL_ER_T6_ROLE_HOLDERS.md`
>    (`e2bcb40660129665ed1ad5b45b80e578168ed5904c4e12a17d3ee2f2f68dcbc4`) as bounded register evidence for A14b. I do
>    not certify the reader's isolation.
> 2. **"Read" (MA1).** For the conduct-defined holder classes (register L92, L122), a subject has read a location if
>    [criterion]. A byte scan by a process, with no content reaching the subject's context, [does / does not / is
>    decided case by case as follows: …] count.
> 3. **Standard of evidence (MA2).** A subject is treated as outside those classes for a role when [standard].
>    No subject is required to prove the absence of all possible
>    historical exposure.
> 4. **Reviewers (MA3).** The S13 role bar [does / does not] extend to reviewers. A holder's review [may / may not]
>    support adoption [unless …].
> 5. **Identity facts I supply (Q1).** The register's L3 "coordinator" is [session or thread id / unknown]. R1b: [none
>    / ids]. R3a / R3b / R3c: [thread ids / unknown]. R6a: [thread id / unknown]. `reviewINC2` [is / is not / unknown]
>    `reviewerS12`.
> 6. **Effect.** This statement sets a criterion only. It determines no individual's eligibility, adopts nothing else,
>    and authorizes no execution.
