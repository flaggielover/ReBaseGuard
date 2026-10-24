# Receipt: A6c candidate 4, Phase-1 disclosure (Cell-308 Cloud route r1), 2026-10-23

**Status: RECEIPT OF OWNER-RELEASED EVIDENCE · ADMINISTRATIVE EFFECTS ONLY · NO DETERMINATION · NO PHASE 2.**
`new_target_evaluations = 0` · `cell309_activity = none`.

```text
A6C_CANDIDATE_4   PHASE_1_COMPLETE
                  ELIGIBILITY_PENDING
                  NO_PHASE_2_AUTHORIZATION
```

## 1. The record

| item | value |
|---|---|
| file | `reviews/external/A6C_EXTERNAL_CANDIDATE4_PHASE1_DISCLOSURE.md` |
| bytes / sha256 | 3,686 / `ad2adbc6984416c058c9a800a99b3f852ca16a4bb2451f6674a0dae32f1c81a3`. The owner-stated count and digest **MATCH** |
| blob | `aa5295c005e398002761cc5d846451c3710991f2` |
| owner release | branch `owner-review/cell308-A6c`, commit `b11f172eaf83ce129fbdad03ea5b79ffbce2c323`. Its only parent is `40328447edeee5c68d35fe8e914155f5548b446d`. It adds only this file |
| recording | `codex/cell308-claude-r5-integration` fast-forwarded to `b11f172e`. The file is byte-identical: not retyped. No force-push and no history rewrite |
| pre-read scan | confined scoped scan **before** display (scanner `e103c196`, configuration `ab0104c6`, `python3 -I -B`, counts only): 1 text file, **0 findings**, controls detected, PASS |
| brief | canonical `ledger/briefs/A6C_REDERIVATION_CLOUD_R1.txt` at `797248fcdc45038eb10254b223a3a40838174c63`, 17,499 bytes, `489dec78a91aa0945f866ad6bbb72590988bcee0872961e45f279f76bf472f0c` |

## 2. Appointment terms (owner-stated, 2026-10-23)

| term | as issued |
|---|---|
| 1. external-origin list (Part A) | **the proposed official documentation-site list** (brief lines 66–74) |
| 2. Part D / A16 | **out of scope** (NOT_IN_SCOPE). A16 has no A6c Part D result |
| 3. `mbs308_host.py` at `142d97a9` | **permitted only for a13 and a14** |
| 4. reuse | **no reuse** of the A6b candidate or of A6c candidates 1–3 |
| appointment date and exact text | not supplied to the recorder |

## 3. The disclosure, item by item (as disclosed; nothing upgraded)

| brief item | disclosed (line) | status |
|---|---|---|
| 1 identity | thread / conversation ID: **"UNVERIFIED; none was exposed in my execution context"** (5). Platform: "Codex desktop/API execution environment" (5). Account identity, and whether it matches any coordinator or recorder account: **UNVERIFIED** (5). Environment ID exposed: `ccarenv_b64_Y2NhcmVudl83NjQ3NGYxYTcwMTQ4MTkxODgwOWM1MzRlN2IxYjE3Yg` (5) | present |
| 2 context and history | appointment, platform metadata and the verified brief only; no compaction or summary exposed. Omitted history: **UNVERIFIED** (9) | present |
| 3 prior roles | only the A6c candidate 4 role is known. Any prior role: **UNVERIFIED** (13) | present |
| 4 excluded sources | no listing, search, read, hash or other process contact with the listed excluded sources in this session. Prior contact: **UNVERIFIED** (17) | present |
| 5 the coordinator and recorder | no known relationship or communication. Whether either can reach the candidate: **UNVERIFIED** (21) | present |
| 6 attachment | metadata showed no attached project, artifact, repository or terminal session. No checkout inspected and no repository path read. Hidden attachment: **UNVERIFIED**. "Isolation is not certified" (25) | present |
| 7 tools | `exec_command`, `apply_patch`, `download_file`, `view_image` available; only `exec_command` was used, in `/tmp`. App, thread, artifact, collaboration and MCP-resource tools were available but **not used**. No repository-worker or remote-worker tool was used (29) | present |
| brief verification | HTTP 200; 17,499 bytes; `489dec78…2f0c` (33–35): **MATCH** with the canonical values | — |
| fetches | none beyond the brief: no documentation, repository file, `mbs308_host.py`, Phase 2 input, Part D material or external source (36) | — |
| re-derivation | none (36) | — |
| commands and paths | commands listed (40–53); paths touched: `/tmp`, the scratch directory `/tmp/a6c-external-candidate4.7zPLLw` and two files in it. "No other local filesystem path was touched" (55–62) | — |

## 4. The recorder's administrative observations (facts only; no eligibility judgment)

* **O1. Environment.** The disclosed environment ID's payload decodes, as a string, to
  `ccarenv_76474f1a701481918809c534e7b1b17b`.
  * It is **not equal** to the coordinator's `env_01GTgmTdDaUY28GtoGZVi3QY`.
  * This says **nothing** about account or control identity, which stay UNVERIFIED.
* **O2. The decline list.** No category is disclosed as applicable. None is affirmatively excluded either: prior roles
  are UNVERIFIED (line 13). "Not candidates 1–3, and not the A6b candidate" rests on line 13's "only known role".
* **O3. Abbreviated commands.** Four commands are abbreviated (lines 46, 48, 49 and 51, shown as `printf ...`,
  `awk ...`, `wc -c ...` and `sha256sum ...`), so their full arguments are not disclosed. The paths list (lines 55–62) is complete as stated.
* **O4. Reach-capable tools.** Tools that could reach other conversations or resources (app, thread, collaboration,
  MCP-resource) were available, but are disclosed as unused.
* **O5. No contact.** No contact with `/workspace`, any repository path or any excluded source is disclosed.

## 5. State and non-effects

* **Eligibility is PENDING.** The Option A / Option B draft is filled from this record and is not issued.
* **Not done:**
  * no proceed instruction was sent;
  * the recorder fetched no Phase 2 input and performed no re-derivation;
  * nothing is adopted, and no statement is issued;
  * the register was not read.
* **Not added:** a matrix erratum and a ledger line. The owner asked for the disclosure and its receipt.
* **The recorder:** `claude_cloud_recorder_20261022` (`session_01EKeyysqJNJgvrdiLFAA43o`), as disclosed in
  `OWNER_STATEMENT_7_RECEIPT_20261022.md` §5. It is never the candidate.
