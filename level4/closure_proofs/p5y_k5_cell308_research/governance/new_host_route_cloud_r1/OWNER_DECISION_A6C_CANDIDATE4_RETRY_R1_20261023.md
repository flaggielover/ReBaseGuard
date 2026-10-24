# Owner decision R1: one corrected A6c Phase 2 retry by candidate 4 (Cell-308 Cloud route r1), 2026-10-23

**Status: OWNER DECISION (the owner's words recorded verbatim in §1) · RECORDED BY claude_cloud_recorder_20261022.**
§1 governs. §2 records what it applies to. `new_target_evaluations = 0` · `cell309_activity = none`.

```text
A6C_CANDIDATE_4   PHASE_2_ATTEMPT_1   STOPPED: candidate manually mistyped the Part 1 commit in its manifest
                  PHASE_2_RETRY       AUTHORIZED: exactly one (R1); NOT YET SENT; NOT STARTED
                  ON A SECOND STOP    candidate 4's role ends
```

## 1. The owner's decision (verbatim, as issued on 2026-10-23)

> I choose R1.
>
> Authorize exactly one corrected A6c Phase 2 retry by candidate 4. Record that the first attempt stopped because the candidate manually mistyped the Part 1 commit in its manifest. No result from attempt 1 may be reused.
>
> Keep the same scope and terms. The retry must use a new scratch directory and derive the complete manifest mechanically from the verified canonical brief. No commit ID, path, byte count, or digest may be typed manually.
>
> Expected derived values:
>
> Part 1 commit:
> 4f814796757bb1a14086b88d677adef94309d0f6
>
> Part 2 commit:
> 142d97a90a1c3fafff394044aa1448674f7a633c
>
> Entries: 40
>
> Expected manifest SHA-256:
> 45e2d97dbb07a24ef40d0a9027e2c67c08b6e44b36626742b46b9e68ec363999
>
> A second stop of any kind ends candidate 4's role. Do not issue a new candidate appointment.

## 2. What it applies to

| item | value |
|---|---|
| selected path | **R1**, as prepared after `A6C_CANDIDATE4_PHASE2_STOP_RECORD_20261023.md` (commit `ede29498`) |
| attempt 1 | stopped because the candidate **manually mistyped** the Part 1 commit (`…adef943e0d0f6` for `…adef94309d0f6`) in its manifest. **No result from attempt 1 may be reused** |
| canonical brief (unchanged) | `ledger/briefs/A6C_REDERIVATION_CLOUD_R1.txt` at `797248fcdc45038eb10254b223a3a40838174c63`, 17,499 bytes, `489dec78a91aa0945f866ad6bbb72590988bcee0872961e45f279f76bf472f0c` |
| scope and terms (unchanged) | Parts A–C; Part D / A16 out of scope; the proposed official documentation-site list; `mbs308_host.py` at `142d97a9` for a13/a14 only; every brief prohibition and stop condition |
| manifest method | derived mechanically from the verified brief. The reference script `a6c_derive_manifest.py` is 3,164 bytes, SHA-256 `78e672da064e21f14c427dc70438f2951c1c7c75fb3d7cba024f30b5e6f27572` (given verbatim in the retry instruction). No commit ID, path, byte count or digest is typed by hand |
| expected derived values | Part 1 `4f814796757bb1a14086b88d677adef94309d0f6`; Part 2 `142d97a90a1c3fafff394044aa1448674f7a633c`; 40 entries; manifest SHA-256 `45e2d97dbb07a24ef40d0a9027e2c67c08b6e44b36626742b46b9e68ec363999`. The recorder reproduced these locally from the canonical brief, parse-only with no network |
| a second stop | of any kind **ends candidate 4's role** |
| new appointment | **none** issued |

## 3. State and gaps

* **The retry instruction is not sent.** The owner sends it directly in candidate 4's conversation. Phase 2 retry has
  **not started**.
* **Not on the integration branch:** the owner's eligibility determination and the first proceed instruction for
  candidate 4, and candidate 4's attempt-1 stop report. The retry relies on that determination's conditions, which
  are therefore known to the recorder only as the owner reported them.
* **Nothing adopted.** No result exists. No statement other than this decision is issued.

**Not added:** a matrix erratum and a ledger line. The owner asked for the decision only.
