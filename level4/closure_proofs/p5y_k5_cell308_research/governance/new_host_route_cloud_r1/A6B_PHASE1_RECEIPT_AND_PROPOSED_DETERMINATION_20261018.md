# A6b candidate Phase 1: receipt, one proposed A14b row and one recommended owner determination (Cell-308 Cloud route r1), 2026-10-18

**Status: RECEIPT OF OWNER-RELEASED EVIDENCE · PROPOSED ROW (coordinator, under statement 5 §2 limits) · RECOMMENDED
STATEMENT NOT ISSUED.**
* This file is not the owner's individual determination.
* It does not authorize Phase 2.
* It adopts nothing.

`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The released bytes

| item | value |
|---|---|
| disclosure | `reviews/external/A6B_EXTERNAL_CANDIDATE_PHASE1_DISCLOSURE.md`: 7,642 bytes, sha256 `dbfe5d8f2a4ecac5fc3c05821426db528b48493131dc3c0e99d084f0ecc5aae8`, **MATCH**. One final LF. Byte-identical to the decoded payload (`cmp`). It was decoded as data only (standard-library base64 and gzip, `python3 -I`), in a fresh private scratch directory. Tail-figure count before reading: 0 |
| transmission | the owner's release message, committed unchanged as `OWNER_TRANSMISSION_A6B_PHASE1_20261018.txt`: 12,408 bytes, sha256 `003a75d874720757959abe1829ff95b66a034ffb24221e4a60e75e3148bd1d9f`. It contains the assistant-recorded receipt, a JSON object that parses validly. Tail-figure count: 0 |
| the receipt's standing | **ASSISTANT-RECORDED EVIDENCE**, made by the owner-assistance Codex conversation `01a13b76…`. It is not a candidate declaration, it is not an owner attestation of facts the owner cannot see, and it is not proof of independence |
| repository state at recording | head `9a811511d83c624dd54c80c26336b755577291a9` (no newer commits on the remote); PR3 draft, unmerged |

**Privacy note.** Disclosure line 61 gives the candidate's local working-directory path, which includes a local account
name. It is recorded verbatim as released. The coordinator does not alter external reports.

## 2. Evidence, kept in three classes

### 2a. Observed facts about creation and status (assistant-recorded receipt)

* **How it was created.** The owner instructed creation ("现在创建 A6b 候选会话", "now create the A6b candidate
  conversation"). The owner-assistance conversation `01a13b76…` then called `mcp__codex_app__create_thread`.
  * The target was a new **projectless** user-owned conversation, `cell308-a6b-phase1-20261018`, on host `local`.
  * `fork_thread` and collaboration subagents were **not** used.
* **The prompt.** The only prompt was the Phase 1 appointment: 5,217 bytes, sha256 `56f487ba…e7cb`.
  * No project id, repository attachment, inherited history, model override or Phase 2 instruction was supplied.
* **Status.** The thread is idle and the latest turn completed, with no error. Phase 1 is complete.
  `phase2_authorization_sent: false`.
* **The creator also inspected.** At the owner's request the creator inspected the candidate's single Phase 1 turn
  and its output. It sent no instruction or follow-up.

### 2b. The candidate's own finite disclosures

* **Identity.** `CODEX_THREAD_ID` = `01a14d7a-1ec2-7de3-ad42-5b24dedad813`, read from its own environment (line 18). It
  runs as an OpenAI Codex agent in the Codex desktop app, with a local macOS shell.
* **Brief.** It fetched the brief only, at `412214d8`, and verified its length and hash before reading (lines 9–14).
  * The first HTTPS attempt failed certificate validation and returned no content.
  * A second request with `curl` succeeded with verification on. No redirects were followed. No other repository URL
    was requested.
* **Context** (lines 24–26): platform instructions, tool and skill metadata, the appointment and this turn only. No
  earlier project conversation, and no compaction notice. Unseen history is **UNVERIFIED**.
* **Prior roles** (lines 30–32): none established. Earlier or externally mapped roles are **UNVERIFIED**.
* **Excluded sources** (lines 36–49): no known semantic reading of any excluded source and no known process contact
  with one.
  * The only contact disclosed: the names of excluded sources, labels and allowlist metadata, read from the
    appointment and the brief.
  * One local skill file was read.
  * The first command used a login shell.
  * Shell-startup and harness access are **UNVERIFIED**.
* **Tools advertised in its context** (lines 32 and 57): conversation-management tools, and "ReBaseGuard AWS/Vultr
  worker" tools. It reports that it did not use them.
* **Coordinator** (lines 53–57): it knows this session's identifier only from the appointment and brief, and has had
  no interaction with it. Reach and control are **UNVERIFIED**.
* **Checkout** (lines 61–63): a projectless working directory. Whether a checkout was attached or read is
  **UNVERIFIED**. It opened nothing.
* **Stop** (lines 67–69): no Phase 2 fetch, no trace and no messages.

### 2c. Facts that remain unresolved

* **Account, infrastructure and control:** the signed-in account, its relationship to other accounts, and the effect
  of harness and shell startup.
* **The creator's identity.** The creator `01a13b76…` disclosed prior Cell-308 integration and preparation work.
  Whether it is any historical R3 label is **UNRESOLVED** (statement 5 §1).
* **The creator's access.** The creator can create and inspect the candidate's conversation, so it has a working
  channel to it.
* **The candidate's own reach.** Its advertised tools could reach other conversations and project workers. They are
  unused, as far as it reports.

## 3. The requirements applied (statement 4 MA2 / MA3; statement 5 §6; statement 6 §8; A6b handoff §2)

| requirement | source | evidence | result |
|---|---|---|---|
| a genuinely new conversation launched at the owner's instruction, under a separate candidate appointment | statement 5 §6; statement 6 §8; handoff §2 | 2a: new projectless thread created at the owner's explicit instruction; the appointment's prompt only | **met on the evidence.** The owner instructed the launch and an owner-assistance tool executed it. This is disclosed, not concealed |
| outside **this coordinator's** reach; not a same-account Claude session; not a subagent | statement 5 §6; MA2 | It is a Codex desktop thread on a local macOS host (2b), and not a fork or collaboration subagent (2a). **Coordinator side:** this session has no tool that addresses Codex threads or the owner's local machine; its cross-session tools address Claude Code sessions only. Since the candidate was launched, it has made no attempt to reach it | **met, as far as the coordinator's own tool surface goes.** The wider boundary (account, indirect influence) is **UNVERIFIED** and is not certified. **Mitigation:** the Phase 2 materials are fixed by hash at `58769a0f`, so the coordinator cannot change what the candidate will read |
| not B1, B2, B3, the ER-T6 reader, a coordinator or worker session (R1a, R1b, R2, R3a–R3c), or the owner-assistance conversation | handoff §2; statement 5 §1, §6 | 2a: a new thread, created 2026-10-18 by a `create_thread` call, with a distinct identifier. 2b: no known prior role. **This rests on the creation-request fact, not on a date comparison** | **met on the evidence** |
| an MA2-complete Phase 1 disclosure, given before any fetch other than the brief | MA2; brief Phase 1 items 1–6 | 2b covers all six items. It identifies the participant, separates visible from unseen history, and states prior roles, contact, compaction and the scope of its statements. Verification happened before reading | **met** |
| not exposed in order to qualify; no ER-T6 rerun | statement 4 §3 | none was done | **met** |
| tracer is not an E1″ holder | author-prepared (B3 YC1, matrix E5 A6b); not an accepted text; adopted or not by the owner's appointment | no known exposure or contact, disclosed finitely. ER-T6 not repeated. A lookup would return [K] CANNOT_TELL by construction | **no contrary evidence; status UNVERIFIED.** Under MA2 the disclosure is the evidence, and absolute proof is not required |
| the function is not covered by S13 | MA3 | the trace designs, changes and selects nothing | its own appointment, exposure and independence requirements apply (rows above) |

**A limitation that is disclosed and does not block.** The creator and observer `01a13b76…` has prior project
involvement and an unresolved R3 mapping, and it holds a working channel to the candidate.
* **No issued requirement makes separation from that conversation a condition** of the tracer's eligibility. The
  issued conditions name only this coordinator, same-account Claude sessions, subagents, reused reviewers and the
  owner-assistance conversation itself as tracer.
* It is therefore **not** treated as a blocker.
* It is also **not** waived. It is recorded, and the recommended determination closes the channel for Phase 2 (§5
  item 3).
* Whether the owner wants separation from every unresolved author as an added condition is the owner's choice. This
  file does not invent that condition.

## 4. The proposed A14b row

| row | subject | function / intended use | proposed state | limits kept |
|---|---|---|---|---|
| A6b-C1 | **A6b External Candidate**, Codex thread `01a14d7a-1ec2-7de3-ad42-5b24dedad813` | the A6b policy-provenance trace (brief Phase 2), for the bounded scope only | **ESTABLISHED_ELIGIBLE (proposed)**, for that bounded trace | E1″ status UNVERIFIED. Account, infrastructure and control independence UNVERIFIED. Unseen history UNVERIFIED. The creator's channel is disclosed. **Not** a non-holder certificate. **Not** certified isolation. It confers no other role and no standing for any later use |

## 5. Recommended owner statement 7 (for approval as written; not issued)

> **Owner statement 7 (Cell-308 Cloud route r1, A6b candidate determination), [date].**
> 1. On its Phase 1 disclosure (`dbfe5d8f2a4ecac5fc3c05821426db528b48493131dc3c0e99d084f0ecc5aae8`) and the recorded
>    creation receipt, I determine that the Codex conversation `01a14d7a-1ec2-7de3-ad42-5b24dedad813` is
>    **ELIGIBLE for the A6b Phase 2 trace only**, as fixed by the brief at `412214d870f7ccc4d842c35b01bdc8b0ac5cd864`
>    (`aa0960778e2ec89e26e16a73dec022aaa8a183438b6bc434dcc284f82a974725`).
>    * I do not certify its E1″ status, its account or infrastructure isolation, or its unseen history.
>    * This determination confers no other role.
> 2. For this appointment I adopt the brief's requirement that the tracer not be a known E1″ holder. I accept the
>    candidate's disclosure as the evidence for it.
> 3. Phase 2 conditions, in addition to the brief:
>    * (a) The candidate fetches only the twelve allowlisted files at `58769a0f39014a43be984773de0f39f9fc8d469d`, and
>      checks each hash first.
>    * (b) It uses no conversation-management, remote-worker or repository-worker tool.
>    * (c) Apart from my verbatim instruction to proceed, no other conversation, including the one that created it,
>      sends it any message or material.
>    * (d) It reports only to me. Its role ends with the report.
> 4. I instruct this same candidate to proceed with Phase 2. [Issue this item only when sending the instruction to
>    the candidate.]
> 5. This statement adopts no traced policy item. It decides no D-* item, makes no T6, materiality or S12 ruling, and
>    authorizes no execution. The trace result goes to A15 / A17 as input only.
