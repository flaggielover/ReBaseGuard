# Evidence request ER-T6, revision r2: bounded register lookup (Cell-308 Cloud route r1) — prepared, not appointed

**Status: AUTHOR CORRECTION · PREPARED · NOT APPOINTED · NOT COMPLETED.** This revision replaces
`EVIDENCE_REQUEST_ER_T6_ROLE_HOLDER_CHECK_20261016.md` (`b03fc997…a5b`), which is preserved unchanged. It answers
external B3 confirmation finding **YC2 (BLOCKING)** (`reviews/external/CONFIRMATION_EXTERNAL_B3_CORRECTIONS.md`,
`6a721ada…253c`, lines 84–92), together with Y8.

**What this request does not do:**
* expand the coordinator side's access;
* appoint anyone;
* supply a source pin, an exhaustive identity map or any exposure proof;
* involve B3, the root Codex session, the coordinator side or the retired B2 reader as the reader.

`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. What r1 claimed, and is withdrawn

R1 §5 said "NOT_LISTED on all rows lets A15 and A17 proceed on this point". **That effect is withdrawn**, and so is
matrix R4 erratum E4's A15 condition, "no HOLDER, and no CANNOT_TELL, on R1–R3", **as a clearance**. A register lookup
establishes only its bounded result.

| establishes | does not establish |
|---|---|
| what the specified pinned register says about each specified identifier | actual non-holder eligibility |
| | the absence of restricted exposure |
| | that the register or the location list is complete |
| | that an identifier is correctly mapped to a real participant |
| | platform or control independence |

## 2. Five things kept separate (none implies another)

| # | question | who or what can answer it | status now |
|---|---|---|---|
| Q1 | **identity mapping**: which actual participants (sessions, agents, people) stand behind each identifier | permitted existing records only (the ledger and the briefs). The coordinator side does not read other sessions | partial (§3) |
| Q2 | **source completeness**: are the E1″ register and the MBS-1 location list complete for this purpose? | the owner, as the register's authority | **UNKNOWN** |
| Q3 | **register coverage**: what the pinned register says about each identifier | the ER-T6 reader (§4) | not done |
| Q4 | **actual restricted exposure** of each participant | not established by any register lookup. Needs its own evidence, under its own authority | **UNVERIFIED** |
| Q5 | **platform / control independence** | not established by any register lookup | **UNVERIFIED** |

## 3. Identifiers, expanded only from permitted existing records

The source is the ledger's agent labels and the briefs index (`ledger/TARGET_INTEGRITY_LEDGER.jsonl`;
`ledger/briefs/BRIEF_INDEX.md`). Every row is reported individually. Grouped results are not allowed.

| # | identifier | mapping status (Q1) |
|---|---|---|
| R1a | `claude_cloud_coordinator_20261014`, as session `session_01S66r3p84SFdY6Vc4RchSWr` | mapped (this session) |
| R1b | any **other** session that wrote under the label `claude_cloud_coordinator_20261014` | **CANNOT_TELL**: not determinable from permitted records |
| R2 | `claude_cloud_worker_20261016_b1corr`, session `session_01VGbYdSMrEaoYpdb386rCWk` | mapped (ledger `session` field) |
| R3a | `codex_cell308_r5_integration_coordinator` | label only; the session behind it is unknown |
| R3b | `fresh_codex_r5_sync_independent_code` | label only |
| R3c | "coordinator recording independent code/evidence reviews"; "fresh independent evidence reviewer" (two ledger agent labels) | **CANNOT_TELL**: no stable identifier |
| R4-59 … R4-71 | the development review agents, one row each: `reviewCLOUD_R1` (brief 59), `reviewCLOUD_R1_DELTA` (60), `_DELTA2` (61), `_DELTA3` (62), `_DELTA4` (63), `reviewREVIEW63_REPAIR` (64), `reviewREVIEW64_REPAIR` (65), `reviewREVIEW65_REPAIR` (66), `reviewREVIEW66_REPAIR` (67), `reviewREVIEW67_REPAIR` (68), `reviewREVIEW68_REPAIR` (69), `reviewREVIEW69_REPAIR` (70), `reviewREVIEW70_REPAIR` (71) | labels only (fresh subagents of R1a; no separate session ids) |
| R5a, R5b, R5c | `reviewerFR1`, `reviewerFR2`, `reviewerS12` | labels only (subagents of R1a) |
| R6a | `B1-External (Codex)` | owner-recorded identity; no session id in permitted records |
| R6b | `B3-External` | owner-recorded identity; no session id in permitted records |

**Not covered:** any participant who left no ledger label (for example a human who edited a file directly). That
coverage gap is **CANNOT_TELL** by construction.

## 4. Reader, sources and output

**Reader.** The reader must already be eligible to read the E1″ register under the governing rule. The prepared
requirement is: **the owner personally, or an existing listed holder whom the owner specifically authorizes**.
* A fresh reviewer is not exposed to the register in order to make them eligible; that would bootstrap eligibility.
* Not B3, not the root Codex session, not the coordinator side, not the retired B2 reader.

**Sources.** The E1″ register and the MBS-1 location list. These facts are missing, and the owner supplies them before
any reading:

| missing fact | why the coordinator side cannot supply it |
|---|---|
| the exact path of each source | the coordinator side does not list or read the excluded records |
| the commit pin of each source | as above |
| the raw-byte sha256 of each source | the coordinator side does not hash the excluded records |
| whether the MBS-1 location list is part of the register, or a separate record | as above |

No reading starts until these are fixed in the owner's appointment record.

**Output** (to the owner only): `READING_EXTERNAL_ER_T6_ROLE_HOLDERS.md`. One line per row of §3:

`<row>: HOLDER | NOT_LISTED | CANNOT_TELL — <register entry id or line number only>`

* A row the reader cannot match to a register entry with certainty is **CANNOT_TELL**. It is never NOT_LISTED by
  default.
* **No group results.**
* No observation, value, time or figure is quoted.

## 5. Effect (proposed; nothing decided)

* **HOLDER** on any row: T6's trigger is met for that role. Any text, review or decision that role produced cannot
  support adoption until the owner rules on the consequence, under its own authority. Re-deriving text does not
  retroactively undo a role / exposure combination (B3 confirmation line 72).
* **NOT_LISTED or CANNOT_TELL:** recorded as stated. **Neither clears A15 or A17.**
* **Adoption needs more than this lookup.** Whether adoption may proceed needs an owner eligibility determination with
  stated authority. It must weigh Q1–Q5 together, and it is **OPEN**. No decision rule equating absence from a list
  with no exposure exists in the accepted texts, and none is proposed here.
* **B3 (R6b):** the result is bounded register evidence about one identifier. It does not certify B3's full non-holder
  status or its isolation.
* **R4–R6 are separate from R1–R3.** Resolving R1–R3 does not verify the R4–R6 checks.
