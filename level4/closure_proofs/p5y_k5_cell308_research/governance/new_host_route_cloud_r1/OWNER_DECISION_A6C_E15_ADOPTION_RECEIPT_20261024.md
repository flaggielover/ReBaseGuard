# Receipt: owner adoption of A6C-E15, sanitized input set S1, manifest R2 and the B2 classification rule (Cell-308 Cloud route r1), 2026-10-24

**Status: OWNER DECISION (recorded) · RECEIPT · ADMINISTRATIVE EFFECTS ONLY · NOTHING APPOINTED, FETCHED, SENT OR RUN.**
`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The record

| file (under `level4/closure_proofs/p5y_k5_cell308_research/`) | bytes | sha256 |
|---|---|---|
| `governance/new_host_route_cloud_r1/OWNER_DECISION_A6C_E15_ADOPTION_20261024.md` (decision record) | 6,671 | `f5603b6ad3e1373f45040e801901d8465ddf1574b1d33204a871eecd59af6167` |
| `governance/new_host_route_cloud_r1/READINESS_MATRIX_R4_ERRATUM_E16_20261024.md` (RM-E16) | 2,816 | `8c98f244baea6a2705d3544655e1ffa0fca277cf7e904a8a6d00b290799e3974` |
| `ledger/TARGET_INTEGRITY_LEDGER.jsonl` | one appended line, append-only | — |

* **Owner text.** §1 of the decision record reproduces the owner's decision exactly as issued in this recorder's
  session on 2026-10-24. The owner supplied no separate file, so no owner-stated digest of the text exists for
  comparison.
* **Reference state.** `codex/cell308-claude-r5-integration` at `a2aff3cbf92b6b5d53cadf16406d0df8ae993a22`, draft PR3.
  This commit is a fast-forward of it.

## 2. Owner-stated values checked against the repository (local git objects; nothing fetched)

| object | owner-stated | in the repository | result |
|---|---|---|---|
| manifest R2 at `0c6c0a30f321ecc3d9891acef9fb5d99e1e6ffef` | 20,981 bytes, `a12470137f0f34c0a687a07c2b8f5e45517acd29ffc377143c50ae2e6e3c07cf` | 20,981 bytes, `a1247013…07cf`, blob `1ab17821b855e8633fc25002bcb347fd1e562e9c` | **MATCH** |
| A6C-E15 at `a2aff3cbf92b6b5d53cadf16406d0df8ae993a22` | 4,855 bytes, `680b4d3e48328c1caa850e128899e99cd98d483e67d7c2cd4292eea9d6d8d701` | 4,855 bytes, `680b4d3e…d701`, blob `966652d6fa473f3d9835fe98ada5a0732f7b9656` | **MATCH** |
| both, at the reference head `a2aff3cb` | — | byte-identical | **MATCH** |
| S1 at `90d12cef` (entries 4, 6, 7), as manifest R2 binds them | — | 14,955 / `8c91a8f9…0390`; 46,480 / `691eff13…d8a6`; 20,593 / `979a3b97…c26e` | **MATCH** (manifest R2 byte-verified 40/40) |

## 3. Effects

* **In force:** A6C-E15, sanitized input set S1, manifest R2 and the B2 classification rule. Manifest R1 is no
  longer used for A6c.
* **Unchanged by the rule:** entry 15 line 57 and entry 8 line 1.
* **RM-E16** records the A6c row as BLOCKED on the owner's appointment of a new candidate.
* **Preserved unchanged:** the canonical brief, the original entries 1, 4, 6 and 7, the S1 files, manifest R1 and
  A6C-E14. All were checked unchanged at the reference head.
* **Recorder notes** (decision record §3; nothing decided):
  * N1: S1 redacts a superset of what the rule requires;
  * N2: entry 24 line 115 is the one kept line pairing "incident review" with an attribution verb;
  * N3: the rule lives in the decision record, not in the candidate-facing A6C-E15 text.

## 4. Not done

* No candidate is launched or appointed. No proceed instruction is sent.
* No B2 source and no Phase 2 input is fetched. No re-derivation is run.
* No statement is issued. Nothing is adopted beyond the decision. There is no T6 ruling.
* The register was not read. There is no host, grant, freeze or execution.

## 5. The recorder and the check

* **The recorder:** `claude_cloud_recorder_20261022` (`session_01EKeyysqJNJgvrdiLFAA43o`), with the limits and
  contacts disclosed in `OWNER_STATEMENT_7_RECEIPT_20261022.md` §5.
* **The check:** a scoped administrative check of this commit's staged blobs. The scanner (`e103c196`) and the
  configuration (`ab0104c6`) were loaded from an isolated copy. Only the ledger's added line is scanned (the deviation
  disclosed in `OWNER_STATEMENT_7_RECEIPT_20261022.md` §6). The result, as counts only, is in the commit message.
