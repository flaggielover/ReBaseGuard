# A14b row dispositions, revision 1, under owner statement 4 (Cell-308 Cloud route r1), 2026-10-17

**Status: PROPOSED ROW FINDINGS (coordinator) · NOT OWNER DETERMINATIONS · NOTHING DECIDED.** This applies owner
statement 4 (`OWNER_STATEMENT_4_A14B_CRITERION_20261017.txt`, `e7571200…5457`) once. It uses only evidence that is
already permitted and released.

Every state below is a **proposal**. A proposed ESTABLISHED_ELIGIBLE is not an eligibility determination, and a
proposed ESTABLISHED_EXCLUDED is not a HOLDER finding. Every ER-T6 CANNOT_TELL stands.

Not read to write this file:
* any excluded record, or the raw register;
* any observation location, private transcript, other conversation or the retired reader's scratch.

`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. Coordinator (R1a) contact disclosure, made under MA1 and MA2

**Participant.** `session_01S66r3p84SFdY6Vc4RchSWr` (label `claude_cloud_coordinator_20261014`). Created
2026-10-14T18:46:28Z, in environment `env_01GTgmTdDaUY28GtoGZVi3QY`.

**Available context.** This turn and the one before it in full. Everything earlier is available only through
compaction summaries. **History before that is not available to me in detail.**

**Contact events I know of** (all from the turn of 2026-10-17 that ended in commit `b9860515`; outputs are as in my
context):

| # | command | what the process touched | what reached my context |
|---|---|---|---|
| C-1 | `git grep -l "CONFIRMATION_EXTERNAL_B3_CORRECTIONS" -- <NS> \| grep -v -E '<seven G file prefixes>'` | **A content scan of every tracked file under NS**, including `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`, `audit/*`, `reviews/REVIEW_EXECUTION_INTERRUPTION*` and `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`. The pattern is a literal file name, unrelated to any target | five permitted paths, the complete output. The filter could remove only G paths, so any excluded file containing the literal would have been printed. The one fact conveyed about the excluded files is that they **do not contain that literal**. This breached my own standing exclusion ("never grep"). It is a **contact event**. Under MA1 it is neither cleared nor treated as exposure |
| C-2 | `ls <NS>/ledger \| head -30` | the directory entries of `ledger/` | file **names**, including `COORDINATOR_EXPOSURE_DISCLOSURE.md` (a name already given in S13). This also breached my "never list" exclusion |
| C-3 | `ls <NS>/reviews \| head -50 \| grep -i index` | the directory entries of `reviews/` | nothing was printed |
| C-4 | `git ls-files \| grep -c READING_EXTERNAL_ER_T6` | index names | one count |
| — | the refused ledger cross-check (receipt `OWNER_RELEASE_ER_T6_REPORT_20261017.md` §3) | did not run | nothing |

**Timing.** Every authored route text that is currently under review predates C-1 and C-2. Those texts are the
amendment, the D-* package and its errata, the procedure and the policy inventory. **C-1 and C-2 therefore cannot
have influenced them.** They bear only on future covered work.

**Reading.** I know of no reading, by me, of the register, an REVIEW_EXECUTION_INTERRUPTION record, the incident
review, `audit/*`, or MB r1 postexec or target-run material. This is a scoped statement, not a historical audit, and
the compaction limit applies.

## 2. The row-disposition table

Notes on the columns:
* **"Function"** is the participant's actual function on this route, judged under MA3. A route, implementation or caps
  function is marked **covered**.
* **"Outside-reach"** marks any use that requires a reviewer outside the coordinator's reach. That requirement comes
  from the owner's continuation instruction and the A6b handoff. MA2 says a subagent of R1a, or a same-account Claude
  session, cannot meet it.

| row | subject | function / intended use | established evidence (source) | proposed state | exact missing fact | reserved owner decision |
|---|---|---|---|---|---|---|
| R1a | this coordinator | **covered**: route design (amendment, D-* package), dev implementation (`lx_platform.py`), brief author; also recording | §1; session created 2026-10-14, after the E1″ heading date (2026-09-30, reader L79); ER [U] [K] | **UNRESOLVED** (covered function) | (i) the L3 "coordinator" identity: **UNKNOWN**, and no known source can resolve it. Material, because R1a holds a covered function and carries the same role word. Partly bounded by the creation date; the dates of register L125–L127 and of erratum 2 are not known. (ii) Whether C-1's scanned files are among L111–L116 | statement 5 item 2 |
| R1b | other sessions under R1a's label | none known | ER [M]; owner: UNKNOWN | **UNRESOLVED** (identity) | none can be obtained from known sources | none (no role) |
| R2 | `claude_cloud_worker_20261016_b1corr`, `session_01VGbYdSMrEaoYpdb386rCWk` | **covered** in part: it changed route texts in the B1 correction round | B1 disposition §4 contact disclosure: a git checkout wrote all bytes to disk; `ls` of `reviews/` and `ledger/` filtered before display; nothing excluded opened, grepped, hashed or listed by name (ledger 555). Its earlier B1 phase-1 statement found **eligibility NOT ESTABLISHED, for reach and independence**, not exposure (`OWNER_RELEASE_B1_20261016.md` §3) | **UNRESOLVED** (covered function) | an MA2-complete disclosure. No committed record states its prior roles or history limits, and its phase-1 text is not in the repository | statement 5 item 3 |
| R3a | `codex_cell308_r5_integration_coordinator` | **covered**: integration of the combined dev layer | ledger 474, 478 (label only); owner: UNRESOLVED; supplemental Codex disclosure `01a13b76…` does not map it | **UNRESOLVED** (identity; covered function) | the participant behind the label, and whether it is the L3 "coordinator". UNKNOWN | statement 5 item 3 |
| R3b | `fresh_codex_r5_sync_independent_code` | integration code review (advisory) | ledger 475–477, 479 (label only) | **UNRESOLVED** (identity) | the participant behind the label, and a disclosure | none now: no qualified use is pending |
| R3c-1 | "coordinator recording independent code/evidence reviews" | recording | ledger 480 (label only) | **UNRESOLVED** (identity) | as R3b | none now |
| R3c-2 | "fresh independent evidence reviewer" | evidence review (advisory) | ledger 481 (label only) | **UNRESOLVED** (identity) | as R3b | none now |
| R4-59 | `reviewCLOUD_R1` | dev and route review (advisory; not covered) | report §1: full file list. Read **INCIDENT_INDEPENDENCE_REVIEW_MBS308 lines 94–240 and 270–300**, as permitted by its brief. Same VM and boot as the coordinator. "I hold no MB r1 target-run runtime observation". Subagent of R1a | outside-reach use: **ESTABLISHED_EXCLUDED** (independence). Advisory use: retained. Exposure: **UNRESOLVED** | whether the incident review bears restricted observations, or is an L111–L116 location. Not resolvable from permitted records | none now |
| R4-60 | `reviewCLOUD_R1_DELTA` | as R4-59 | report §1: incident review lines 114–135 and 163–170. **MB r1 qualification review lines 466–480, with an overshoot to note N1**: start load and thermal level "during the official run", which the reviewer reads as the qualification run (UNVERIFIED). Name-level `ls reviews/`. Subagent | outside-reach: **ESTABLISHED_EXCLUDED**. Exposure: **UNRESOLVED** | as R4-59, and whether N1 refers to the target run | none now |
| R4-61 | `reviewCLOUD_R1_DELTA2` | as R4-59 | report §1: incident review lines 112–118; name-level only otherwise. Subagent | outside-reach: **ESTABLISHED_EXCLUDED**. Exposure: **UNRESOLVED** | as R4-59 | none now |
| R4-62 | `reviewCLOUD_R1_DELTA3` | as R4-59 | report §1: incident review (part); name-level only otherwise. Subagent | as R4-61 | as R4-59 | none now |
| R4-63 | `reviewCLOUD_R1_DELTA4` | as R4-59 | report §1: incident review (part). Subagent | as R4-61 | as R4-59 | none now |
| R4-64 | `reviewREVIEW63_REPAIR` | as R4-59 | report §1: hashed five MB r1 **qualification** blobs in memory, never printed. **`cat-file -e` and `rev-parse` on postexec commit `21e99cf0`** (tree traversal only). Subagent | outside-reach: **ESTABLISHED_EXCLUDED**. Exposure: **UNRESOLVED** (process contact with a postexec commit's tree) | whether that traversal touched an observation-bearing object. Not resolvable from permitted records | none now |
| R4-65 | `reviewREVIEW64_REPAIR` | as R4-59 | report §1: name-level only; "no accidental contact". Subagent | outside-reach: **ESTABLISHED_EXCLUDED**. Exposure: no contact event disclosed | — | none now |
| R4-66 | `reviewREVIEW65_REPAIR` | as R4-59 | as R4-65 | as R4-65 | — | none now |
| R4-67 | `reviewREVIEW66_REPAIR` | as R4-59 | as R4-65 | as R4-65 | — | none now |
| R4-68 | `reviewREVIEW67_REPAIR` | as R4-59 | as R4-65 | as R4-65 | — | none now |
| R4-69 | `reviewREVIEW68_REPAIR` | as R4-59 | as R4-65 | as R4-65 | — | none now |
| R4-70 | `reviewREVIEW69_REPAIR` | as R4-59 | as R4-65 | as R4-65 | — | none now |
| R4-71 | `reviewREVIEW70_REPAIR` | as R4-59 | as R4-65 | as R4-65 | — | none now |
| R5a | `reviewerFR1` | formal route review (OD-2; advisory) | report §2: hashed the MB r1 r3 qualification blobs; printed **pre-grant** commit subjects naming qualification and freeze outcomes, including Q12 **decoy** cap figures; a blobless bare clone fetched every branch's commits and trees (Cell-309 objects possibly included, none inspected). **Ran inside the coordinator's session environment** (it saw the coordinator's task list). Subagent | outside-reach: **ESTABLISHED_EXCLUDED**. Exposure: no target-run contact disclosed; **UNRESOLVED** only to the extent pre-grant decoy figures matter to its function | — | none now |
| R5b | `reviewerFR2` | formal conditions check (OD-2; advisory) | search-eligibility r2 §3: **ESTABLISHED** recursive byte scan of the register, `audit/*`, REVIEW_EXECUTION_INTERRUPTION* and the incident review. It reports nothing printed. Subagent | outside-reach: **ESTABLISHED_EXCLUDED**. Exposure: **UNRESOLVED (restricted contact / potential exposure)**, per MA1 | none obtainable without excluded records or a transcript audit, neither of which is authorized | none now |
| R5c | `reviewerS12` | S12 risk rating (A1 GC-5 requires "a fresh incident-independence reviewer") | search-eligibility r2 §3: **ESTABLISHED** byte scan of REVIEW_EXECUTION_INTERRUPTION* and the incident review; name-level `ls ledger/`. Phase-1 statement: no prior reading, no earlier role. Subagent | as the A1 S12 re-rating: **UNRESOLVED**. The potential exposure is to the very incident records its independence concerns. Outside-reach: **ESTABLISHED_EXCLUDED** | reviewINC2 = reviewerS12: **UNKNOWN** | statement 5 item 4 |
| R6a | `B1-External (Codex)` | external conformance check (advisory; not covered) | report "Exposure and independence": no known earlier project role; 44 allowlisted files hash-verified; no restricted contact; reach of the coordinator **UNVERIFIED** | **UNRESOLVED** (identity) | its thread id: **UNKNOWN**. Material, because without it the "no earlier project role" statement cannot be checked against the R3 Codex labels | none now: B1's confirmation exists only as an excerpt |
| R6b | `B3-External`, Codex thread `01a1449c-7b38-7273-a5b4-9364ee8a50a5` | external provenance check (advisory; not covered) | report "Exposure and eligibility": no earlier role in MB r1, MB-S, Cloud drafts, reviews 59–71, FR1, FR2, S12, B1, B2 or coordination; 23 allowlisted files hash-verified; read B2's report only within its allowlist; it applies the holder bar to substantive descriptions and found none. Identity bound by the owner-released thread id. The coordinator's session tools reach Claude sessions, not Codex threads; isolation is **UNVERIFIED** | for its recorded advisory use (statement 1B item 1): **ESTABLISHED_ELIGIBLE** (proposed; exposure dimension). For any use requiring certified isolation: **UNRESOLVED** | none for the advisory use | statement 5 item 5 |

## 3. Participants outside the ER-T6 rows

| subject | function | evidence | proposed state |
|---|---|---|---|
| the owner | decider | owner statement of 2026-10-17; no accepted bar | not a role-holder; no disposition |
| ER-T6-Metadata-Reader | retired | report §1, §7 | no role; no disposition |
| owner-assistance Codex `01a13b76-54a9-7033-9d8a-e78fc2aa0fb5` | owner assistance | its attributed disclosure: prior Cell-308 integration and preparation work; not a fresh reviewer | for the **A6b tracer role**: **ESTABLISHED_EXCLUDED** (prior project involvement, self-disclosed). Its other functions: not assessed |
| A6b candidate | not yet named | none | no finding. Handoff prepared (`A6B_APPOINTMENT_HANDOFF_20261017.md`). Nothing certified in advance |

## 4. Gaps in requirements, identified rather than filled

* **G1 — the S12 re-rating requirement.** A1 S12 (GC-5) requires a fresh incident-independence re-rating before the
  successor freeze. reviewerS12's standing for that is UNRESOLVED (R5c).
  * The requirement is **not discarded**, and the HIGH rating is kept as an advisory floor.
  * A qualifying re-rating is a distinct check, needed before the freeze and not now.
  * Nothing is commissioned here.
* **G2 — the location membership of the incident review.** Several R4 rows turn on whether
  `INCIDENT_INDEPENDENCE_REVIEW_MBS308.md` bears observations. The facts are: it was permitted reading in the R4
  briefs; it is excluded for the coordinator; and the register's L111–L116 list is not known on the coordinator side.
  * Nothing permitted resolves this.
  * It matters only if an R4 review is later used for a purpose that needs exposure standing. None is pending.

## 5. Recommended owner statement 5 (for approval as written)

> **Owner statement 5 (Cell-308 Cloud route r1, A14b row determinations), [date].**
> 1. I determine the A14b rows as proposed in `A14B_ROW_DISPOSITIONS_R1_20261017.md` §2–§3. Every UNRESOLVED row stays
>    unresolved. No row is a HOLDER finding, and every ER-T6 CANNOT_TELL stands.
> 2. **R1a.** While unresolved, the coordinator does recording, documentary correction and handoff preparation.
>    * Every route text it authored stays a proposal, subject to its existing independent-review and adoption gates.
>    * It introduces no new policy number, threshold or rule without a provenance trace before the decision.
>    * It takes no official successor implementation, caps or qualification role.
> 3. **R2 and R3a.** Their covered-function outputs stay proposals, subject to the same gates. Neither takes a further
>    covered role while unresolved.
> 4. **S12 (R5c, G1).** reviewerS12's HIGH rating stays advisory. The A1 GC-5 re-rating requirement stays open, to be
>    met before any successor freeze by a reviewer whose standing I determine at that time.
> 5. **B3 (R6b).** B3's standing is established for the advisory use I adopted in statement 1B item 1. Its isolation
>    is not certified.
> 6. This statement adopts no policy and rules on no T6 question. It makes no materiality determination and
>    authorizes no execution.
