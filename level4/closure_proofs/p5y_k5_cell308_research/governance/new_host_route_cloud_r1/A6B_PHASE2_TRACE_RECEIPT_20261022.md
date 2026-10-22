# Receipt: the A6b Phase 2 external policy-provenance trace (Cell-308 Cloud route r1), 2026-10-22

**Status: RECEIPT OF OWNER-RELEASED EVIDENCE · ADMINISTRATIVE ACCEPTANCE ONLY · NOTHING ADOPTED OR DECIDED.**

**Acceptance verdict: PASS WITH DISCLOSED CAVEAT** (owner-specified; see §4).
* It accepts the trace as a complete, bound and conforming deliverable under the brief and owner statement 7.
* It does **not** adopt any trace result. It decides no D-* item, makes no A14b consequence ruling for any other row,
  and makes no T6 ruling (A14). It issues no statement 2, and makes no materiality, S12, host, freeze, grant or
  execution decision.

`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The record

| item | value |
|---|---|
| file | `reviews/external/TRACE_EXTERNAL_A6B_POLICY_PROVENANCE.md` |
| bytes / sha256 | 23,691 / `c91c7ff9606ab36a1cba0c6452128a45a0530eb9b0545fd379937082057fa4b7`. The owner-stated count and digest **MATCH** |
| blob | `d4f48c0e01f94d3cfbeb383752aa9ac1b1e2c444` |
| owner release | branch `owner-review/cell308-A6b`, commit `ea26984f36686740ca115abb2b5d77d925f76aa3`. Its parent is `a82ac0fbec639430b489fb821bb812004b4d2d45`. It adds only this file |
| recording | `codex/cell308-claude-r5-integration` fast-forwarded to `ea26984f`. The file is byte-identical: not retyped and not reconstructed. No force-push and no history rewrite |
| author | A6b External Candidate, Codex conversation `01a14d7a-1ec2-7de3-ad42-5b24dedad813` (owner statement 7, row A6b-C1) |
| proceed instruction | sent by the owner directly in that conversation at **2026-10-22 15:19:25 UTC** (owner-reported; statement 7 condition (f)) |
| brief | `ledger/briefs/A6B_POLICY_PROVENANCE_TRACE_CLOUD_R1.txt` at `412214d8`, sha256 `aa096077…4725` |

## 2. The seven acceptance checks

| # | check | result | basis |
|---|---|---|---|
| 1 | 12/12 allowlisted file bindings | **PASS** | The manifest (trace lines 32–45) lists 12 files. Every path, byte count and sha256 equals the brief's allowlist (brief lines 39–50), in order. The brief's own binding (6,265 bytes, `aa096077…4725`) is stated at lines 25–28 |
| 2 | 17/17 T1 rows, exactly one result each | **PASS** | Rows a6–a14, a16, a20–a23, and a17–a19 for their untraced parts, in the brief's order (lines 53–69). Each row carries exactly one result from the brief's vocabulary. Tally: MISSING_PRIMARY_SOURCE 14; FREE_CHOICE 2 (a12, a20); NOT_DETERMINABLE 1 (a19); TRACED 0 |
| 3 | T2 list | **PASS** | §T2 (lines 71–115): requirements-document, development-source, ratification and route/governance omissions, each with a location |
| 4 | the Phase 1 disclosure | **PASS** | repeated at lines 9–21: identity, context and history, prior roles, excluded-source exposure and process contact, coordinator relationship, checkout or clone |
| 5 | accidental-contact disclosure | **PASS** | line 17: an unavailable `rg` command with no file content, and later grep limited to the verified scratch files. Line 21: one failed fetch-loop attempt before any download; Phase 2 used only its private scratch directory |
| 6 | non-effects statement | **PASS** | lines 7 and 137 |
| 7 | no quoted tail figure or MB r1 value | **PASS WITH CAVEAT** | the trace states it (line 5). See §4 |

**Further administrative consistency checks** (beyond the seven):
* **Citations.** All 74 `file:line` citations name allowlisted files. No cited line lies beyond the end of the cited
  file at `58769a0f`.
* **Statement 7 conditions.** The trace reports compliance with conditions (a)–(e) (lines 5, 17, 21, 30). These are
  the candidate's own statements and are not independently verified.

## 3. What the trace reports (recorded, not adopted)

* **T1.**
  * No NT/NV item is TRACED.
  * 14 are MISSING_PRIMARY_SOURCE. Their primary sources are outside the allowlist or unavailable (T3, lines
    117–131).
  * a12 (the test-seam list) and a20 (the subprocess timeouts) are FREE_CHOICE.
  * a19 (the exact `REQUIRED_MAPPED` / `PIN_KEYS` sets) is NOT_DETERMINABLE.
* **T2.** The trace lists concrete policy rules and subrules that the inventory does not list separately (lines
  75–115). This bears on the inventory's stated incompleteness (inventory lines 34–36) and on YC1.
* **Effect.** Per statement 7 item 5, the results go to A15 / A17 as **input only**.

## 4. The disclosed caveat

* The trace **states** that no target-run observation, tail figure or MB r1 value is quoted (line 5). It does **not**
  report having run a zero-hit scoped scan.
* **Recorder's supplementary check.** The trace bytes were scanned before they were displayed:
  * scanner `code/c308_quarantine.py`, blob `e103c196…`, sha256 `72d529cc…faa12`;
  * configuration blob `ab0104c6…`, sha256 `0dc2addc…9cbf5`;
  * both loaded from an isolated copy and run with `python3 -I -B` (3.13.16), counts only;
  * result: 1 text file, **0 findings**, 0 sanctioned, report-only 0/0, both negative controls detected, verdict PASS.

  This check supplements the trace and does not replace the author's own attestation. The caveat stands as the owner
  specified.
* The trace's own exposure, isolation and identity statements remain **UNVERIFIED** (trace lines 11–21; statement 7
  item 1).

## 5. The recorder, and its limits

* **The recorder.** Claude Code cloud session `session_01EKeyysqJNJgvrdiLFAA43o` (label
  `claude_cloud_recorder_20261022`). It is the same recorder as statement 7's receipt.
  * It is not the coordinator R1a.
  * It is on the same account, so it holds no covered or reviewer role.
* **Not done:**
  * A6b was not rerun.
  * The register was not read.
  * No allowlisted file was refetched for review purposes. Line counts at `58769a0f` were read only to check the
    citation ranges.
* **Contacts** are as disclosed in `OWNER_STATEMENT_7_RECEIPT_20261022.md` §5.

## 6. State after this record

See `READINESS_MATRIX_R4_ERRATUM_E12_20261022.md`. The A6b row is: Phase 2 complete; trace recorded; administrative
acceptance PASS WITH DISCLOSED CAVEAT. A15 / A17 receive the trace as input only. Every adoption, A14b-consequence,
T6, statement 1 / 1B / 1A and statement 2 decision remains the owner's and remains open.
