# Receipt: owner decision A1, the corrective Phase 1 scope amendment for A6c candidate 5 (Cell-308 Cloud route r1), 2026-10-24

**Status: OWNER DECISION (recorded) · RECEIPT · ADMINISTRATIVE EFFECTS ONLY · NO DETERMINATION · NO PHASE 2.**
`new_target_evaluations = 0` · `cell309_activity = none`.

```text
A6C_CANDIDATE_5   PHASE_1_COMPLETE
                  ELIGIBILITY_PENDING
                  NO_PHASE_2_AUTHORIZATION
```

## 1. The record

| file (under `level4/closure_proofs/p5y_k5_cell308_research/`) | bytes | sha256 |
|---|---|---|
| `governance/new_host_route_cloud_r1/OWNER_DECISION_A6C_CANDIDATE5_PHASE1_SCOPE_A1_20261024.md` (decision record) | 5,503 | `fdc842a1a791162f7628d95a65adfe2c8774786c0ebd50c0ff0e04268015f169` |
| `governance/new_host_route_cloud_r1/READINESS_MATRIX_R4_ERRATUM_E15_20261024.md` (matrix erratum E15) | 2,201 | `dc6ef5b0b822f01efbb077b8b7a42f0634c973bacc8c053f9d8e0d138836995a` |
| `ledger/TARGET_INTEGRITY_LEDGER.jsonl` | one appended line, append-only | — |

* **Owner text.** §1 of the decision record reproduces the owner's decision exactly as issued in this recorder's
  session on 2026-10-24. The owner supplied no separate file, so no owner-stated digest of the text exists for
  comparison.
* **Reference state.** `codex/cell308-claude-r5-integration` at `643149afe0d6328bd1610ddb08183f072dd66db0`, draft PR3.
  This commit is a fast-forward of it.

**The records it applies to (unchanged):**

| file | bytes | sha256 |
|---|---|---|
| `reviews/external/A6C_EXTERNAL_CANDIDATE5_PHASE1_DISCLOSURE.md` (owner release `5d78af7e`) | 6,026 | `4b383452afc235d6fd0a2e10b88b01b4c3096ec428adaece0997560cc9ac2b2a` |
| `governance/new_host_route_cloud_r1/A6C_CANDIDATE5_PHASE1_RECEIPT_20261024.md` | 8,480 | `ce12742287760b99e27d058aeaf6dc4c5f0ad466cdc479c84229a51a647644ee` |
| `governance/new_host_route_cloud_r1/A6C_CANDIDATE5_PHASE1_SCOPE_DEVIATION_RECORD_20261024.md` | 4,105 | `e5f7f047f60aa25e377247ef328fe2e4e80b4d0a0bd7bd3a12925c564c09d39e` |

## 2. Effects

* **The Phase 1 scope is amended for candidate 5 only.** In addition to the brief, it permits fetching and reading E14
  (`cd2fb234`, 4,293 bytes, `13622974…39e`) and the pinned manifest (`be78ccd5`, 20,603 bytes, `45e2d97d…3999`).
  The conditions are in decision record §2 item 4.
* **Recorded as the owner directed:**
  * candidate 5 followed the owner-issued appointment;
  * the amendment is issued now, as a corrective owner record;
  * it does **not** cure any later-proven role, exposure, independence or control violation under E-5.
* **Candidate 5 returns to** `PHASE_1_COMPLETE · ELIGIBILITY_PENDING · NO_PHASE_2_AUTHORIZATION`.
* **The disclosed actions** are consistent with each condition, as disclosed (decision record §3).
  * Line 59's environment status and wait tools are noted for the owner's reading.
  * Observation O3 (redirects followed; no HTTP status recorded) stands.
* **Matrix erratum E15:** A6c is BLOCKED on the owner's individual determination for candidate 5.
* **Every UNVERIFIED finding** in the candidate 5 receipt stands.
* **For every other candidate,** brief line 16 is unchanged.

## 3. Not done

* No eligibility is issued. No proceed instruction is sent.
* The recorder fetched no Phase 2 input and performed no re-derivation.
* The canonical brief, E14, the manifest and the earlier candidate 5 records are unchanged.
* No statement is issued. Nothing is adopted. There is no T6 ruling.
* The register was not read. There is no host, grant, freeze or execution.

## 4. The recorder and the check

* **The recorder:** `claude_cloud_recorder_20261022` (`session_01EKeyysqJNJgvrdiLFAA43o`), with the limits and
  contacts disclosed in `OWNER_STATEMENT_7_RECEIPT_20261022.md` §5. It had no contact with candidate 5.
* **The check:** a scoped administrative check of this commit's staged blobs. The scanner (`e103c196`) and the
  configuration (`ab0104c6`) were loaded from an isolated copy. Only the ledger's added line is scanned (the deviation
  disclosed in `OWNER_STATEMENT_7_RECEIPT_20261022.md` §6). The result, as counts only, is in the commit message.
