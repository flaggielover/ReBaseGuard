# Owner decision: adoption of A6c brief erratum E14 and the pinned Phase 2 manifest (Cell-308 Cloud route r1), 2026-10-24

**Status: OWNER DECISION (the owner's words recorded verbatim in §1) · RECORDED BY claude_cloud_recorder_20261022.**
§1 governs. §2 records what it applies to. `new_target_evaluations = 0` · `cell309_activity = none`.

```text
A6C_BRIEF_ERRATUM_E14   ADOPTED (in force from this decision)
A6C_PHASE2_MANIFEST_R1  PINNED by E14 and this decision
A6C                     BLOCKED: owner launch and appointment of a new candidate
```

## 1. The owner's decision (verbatim, as issued on 2026-10-24)

> I adopt proposed erratum E14 for A6c.
>
> Adopt E14 at:
>
> Commit:
> cd2fb2340b3a51f0b3e03c3a9e7dfc63279e5dd4
>
> Path:
> level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/A6C_REDERIVATION_CLOUD_R1_ERRATUM_E14.txt
>
> Bytes: 4293
> SHA-256:
> 13622974f3f9f961ec6f8a41a6d33ef1279c0156a21397bbcd479c55bd83a39e
>
> This adoption also pins the manifest:
>
> Commit:
> be78ccd5286ad0de4548e04361b3798d331f89bb
>
> Path:
> level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/A6C_PHASE2_MANIFEST_R1.json
>
> Bytes: 20603
> SHA-256:
> 45e2d97dbb07a24ef40d0a9027e2c67c08b6e44b36626742b46b9e68ec363999
>
> Record the owner decision and create the normal receipt, readiness-matrix bookkeeping, and append-only ledger line. Keep the canonical A6c brief unchanged.
>
> Do not launch a candidate, fetch Phase 2 inputs, or send a proceed instruction yet. Return the final commit, paths, byte counts, and SHA-256 values.

## 2. What it applies to

| item | value |
|---|---|
| erratum adopted | `ledger/briefs/A6C_REDERIVATION_CLOUD_R1_ERRATUM_E14.txt` at `cd2fb2340b3a51f0b3e03c3a9e7dfc63279e5dd4`, 4,293 bytes, `13622974f3f9f961ec6f8a41a6d33ef1279c0156a21397bbcd479c55bd83a39e`, blob `3b70734f687750f86345f5a48edc59d5a944b4c5` |
| manifest pinned | `ledger/briefs/A6C_PHASE2_MANIFEST_R1.json` at `be78ccd5286ad0de4548e04361b3798d331f89bb`, 20,603 bytes, `45e2d97dbb07a24ef40d0a9027e2c67c08b6e44b36626742b46b9e68ec363999`, blob `d9cd4690fda6f9e1e3fbb5c62c0602d0764af830` |
| canonical brief (unchanged) | `ledger/briefs/A6C_REDERIVATION_CLOUD_R1.txt` at `797248fcdc45038eb10254b223a3a40838174c63`, 17,499 bytes, `489dec78a91aa0945f866ad6bbb72590988bcee0872961e45f279f76bf472f0c` |
| E14's status line | E14 line 3 reads "PROPOSED. NOT IN FORCE until the owner adopts it by a recorded owner decision". **This decision is that record.** The file is not edited, so its pinned bytes and SHA-256 stay as adopted |
| effect | from this decision, the A6c brief is read **together with E14**. Where they differ, E14 governs (E14 line 10) |
| what E14 does | pins the manifest (E14.1); replaces the brief's REPOSITORY INPUTS procedure (lines 58–64) with fetch, verify and use-as-supplied, and no candidate reproduction of the manifest digest (E14.2); keeps the 40-file scope, Parts A–C, Part D / A16 NOT_IN_SCOPE, the documentation-site list, `mbs308_host.py` for a13/a14 only, every prohibition and E-5 (E14.2 item 5, E14.3); declines A6c candidates 1–4 and the A6b External Candidate (E14.4); adds output items (E14.5) and stop conditions (E14.6); sets aside R1's candidate-side derivation for future candidates (E14.7) |
| candidate 4 records | unchanged. Candidate 4's role stays ended (`A6C_CANDIDATE4_RETRY_STOP_AND_MANIFEST_AUDIT_20261024.md`) |

## 3. State

* **No candidate is launched or appointed.** No Phase 2 input is fetched. No proceed instruction is sent.
* **Nothing is adopted** from A6b or from any A6c attempt. No result exists.
* **A6c stays BLOCKED** on the owner's launch and appointment of a new, eligible candidate.
  * The appointment will need to bind E14 (`cd2fb234`, 4,293 bytes, `13622974…39e`) alongside the brief. The existing
    templates in `A6C_APPOINTMENT_HANDOFF_20261022.md` cite the brief only and predate E14.
  * How the appointment states this is the owner's decision. This record does not draft it.

**Added with this decision:** a receipt, readiness-matrix erratum E14 and one appended ledger line, at the owner's
direction.
