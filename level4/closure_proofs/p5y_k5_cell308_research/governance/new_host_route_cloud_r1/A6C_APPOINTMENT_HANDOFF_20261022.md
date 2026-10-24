# A6c appointment handoff: the independent re-derivation or confirmation (Cell-308 Cloud route r1), 2026-10-22

**Status: PREPARED · NOBODY APPOINTED OR COMMISSIONED · NO CANDIDATE CERTIFIED · NO PROCEED INSTRUCTION SENT.**
Prepared by `claude_cloud_recorder_20261022` at the owner's direction. `new_target_evaluations = 0` ·
`cell309_activity = none`.

## 1. Purpose and basis

| item | basis | status |
|---|---|---|
| purpose | independently re-derive or confirm the affected covered-function texts before any adoption | owner decision E-5 §2 items 3–4 (`OWNER_DECISION_E5_A14B_CONSEQUENCE_OPTION_A_20261022.md`) |
| scope | E-5 §3, S1–S11: the YC1 inventory; the D-* package and errata; the development/integration layer; S5–S11. **S4 (the L-DET reference list) only if A16 remains in scope** and the appointment fixes its allowlist | owner-decided (S1–S4); recorder-identified (S5–S11), amendable by the owner |
| A6b | the trace (`reviews/external/TRACE_EXTERNAL_A6B_POLICY_PROVENANCE.md`, `c91c7ff9…4b7`) is **input only** and adopted nothing (statement 7 item 5; E-5 §2 item 2) | — |
| adoption bar | **no affected output may be adopted before independent re-derivation or confirmation** (E-5 §2 item 3) | owner-decided |
| no cure | re-derivation does not cure any later-proven role or exposure violation (E-5 §2 item 6) | owner-decided |
| function | the task re-derives and confirms; it designs nothing that is adopted, and its alternatives are proposals. Its own appointment, exposure and independence requirements apply (statement 4 MA3) | — |

## 2. Candidate requirements (the owner applies them to a named candidate; nothing is certified in advance)

* **Launched by the owner** in a new conversation that the coordinator's or recorder's session tools cannot reach. A
  Claude session on the coordinator's account does not qualify (`DEPENDENCY_EVIDENCE_HANDOFF_ERRATUM_E1_20261017.md`
  lines 36–39). Neither does any subagent.
* **Not** any participant on the brief's decline list.
* **The A6b candidate** is declined unless the appointment expressly permits it.
* **An MA2-complete Phase-1 disclosure** (brief Phase 1, items 1–7), given before any fetch other than the brief
  (statement 4 lines 34–46).
* **Not exposed** to the register or to any observation record in order to qualify. **No ER-T6 rerun** (statement 4
  line 42).
* **Recommended launch conditions** (carried from statement 7 (b)–(f)):
  * no conversation-management, remote-worker or repository-worker tool;
  * no input from any other conversation;
  * no local filesystem access outside its scratch directory;
  * the proceed instruction sent by the owner directly.

## 3. The sequence (finite)

| step | who | output |
|---|---|---|
| 1 | owner: launch a candidate and issue the appointment (§5.1), citing the brief by commit and SHA256 | appointment |
| 2 | candidate: Phase 1 only | disclosure, to the owner |
| 3 | owner releases the disclosure; the recorder records it and proposes one A14b row under statement 4 | receipt; proposed row |
| 4 | owner: the individual eligibility determination (§5.2) | owner statement |
| 5 | owner: the proceed instruction (§5.3), sent directly | — |
| 6 | candidate: Phase 2 in the same conversation | `REDERIVATION_EXTERNAL_A6C.md` + SHA256, to the owner |
| 7 | owner releases it (for example on `owner-review/cell308-A6c`); the recorder records it verbatim and writes an acceptance receipt | receipt |
| 8 | owner: decides, item by item, what statement 2 may adopt on the A6c result | statement 2 (later) |

## 4. Bindings

| artifact | path | bytes | sha256 |
|---|---|---|---|
| brief | `level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/A6C_REDERIVATION_CLOUD_R1.txt` | 17499 | `489dec78a91aa0945f866ad6bbb72590988bcee0872961e45f279f76bf472f0c` |
| allowlist part 1 | 39 files at `4f814796757bb1a14086b88d677adef94309d0f6`, listed in the brief | — | **all 39 verified** at binding |
| allowlist part 2 | `level4/closure_proofs/p5y_k5_cell308_mbs_r1/code/mbs308_host.py` at `142d97a90a1c3fafff394044aa1448674f7a633c` (pushed branch `p5y-k5-cell308-mbs-r1-candidate`; namespace `mbs_r1`, **not** the excluded MB r1 `mb_r1`) | 29728 | `6650ceebd7297dd4744c6121f9b41617aabbd50211a634df309c53b5945a2a8b` |
| pre-binding scan | the confined scoped scan (scanner `e103c196`, configuration `ab0104c6`) of all 40 files | — | 35 text and 5 py files; **0 findings**; controls detected; PASS |

The brief's own commit is the commit that adds this file. The owner cites that commit in the appointment.

## 5. Owner instrument templates (DRAFTS; [OWNER ACTION REQUIRED] to issue; nothing here is issued)

### 5.1 Appointment (step 1)

> **Owner appointment, A6c (Cell-308 Cloud route r1), [date].** I appoint [conversation or thread identifier,
> platform], launched by me, for **Phase 1 only** of brief A6c at commit [the commit adding this handoff] (sha256
> `489dec78a91aa0945f866ad6bbb72590988bcee0872961e45f279f76bf472f0c`, 17,499 bytes).
> * [OWNER DECISION REQUIRED] The external-origin list for Part A is [the brief's proposed list / amended list].
> * [OWNER DECISION REQUIRED] Part D (the L-DET reference list) is [NOT_IN_SCOPE / IN_SCOPE under this exact clone,
>   object and record allowlist: …].
> * [OWNER DECISION REQUIRED] The A6b candidate is [not permitted / permitted] in this role.
> * [OWNER DECISION REQUIRED] The part-2 file (`mbs308_host.py` at `142d97a9`) is [permitted / withheld]. If it is
>   withheld, a13 and a14 become NOT_DETERMINABLE.
>
> Report your Phase-1 disclosure to me only, then stop.

### 5.2 Individual eligibility determination (step 4)

> **Owner statement [n] (A6c candidate determination), [date].**
> 1. [OWNER DECISION REQUIRED] On the Phase-1 disclosure [sha256], I determine [identifier] eligible for the A6c
>    Phase 2 re-derivation only, as fixed by the brief at [commit] / `489dec78…2f0c`. I do not certify its E1″
>    status, isolation or unseen history. This confers no other role.
> 2. Standing rests on the disclosure, under statement 4 MA2, not on an ER-T6 result.
> 3. Conditions (a)–(f), as statement 7 (b)–(f), with the brief's allowlist and external-origin list.
> 4. Phase 2 starts only on my separate proceed instruction.
> 5. This statement adopts nothing. It decides no D-* item, and makes no T6, materiality, S12, host, freeze, grant or
>    execution decision.

### 5.3 Proceed instruction (step 5; the owner sends it directly)

> Owner instruction to [identifier], [UTC date and time]. I have issued owner statement [n]. **Proceed with PHASE 2**
> of brief A6c (`489dec78…2f0c`). Re-verify the brief first. Do Parts A–C, and Part D only if my appointment put it in
> scope. Observe every stop condition. Report `REDERIVATION_EXTERNAL_A6C.md` and its SHA256 to me only. Your role ends
> with the report.

## 6. Owner decisions this handoff leaves open

1. Who to launch, and the appointment (§5.1).
2. The external-origin list.
3. Whether Part D (A16) is in scope, and its allowlist.
4. The A6b candidate's permission.
5. The part-2 file's permission.
6. The individual determination (§5.2).
7. The proceed instruction (§5.3).
8. Whether to amend the recorder-identified scope S5–S11.
