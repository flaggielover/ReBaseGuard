# Receipt: A6c preparation and E-5 bookkeeping (Cell-308 Cloud route r1), 2026-10-22

**Status: PREPARATION RECORD · ADMINISTRATIVE EFFECTS ONLY · NOTHING ISSUED, APPOINTED, SENT OR RUN.**
`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. What was prepared, at the owner's direction

| file (under `level4/closure_proofs/p5y_k5_cell308_research/`) | bytes | sha256 |
|---|---|---|
| `ledger/briefs/A6C_REDERIVATION_CLOUD_R1.txt` (the A6c brief) | 17,499 | `489dec78a91aa0945f866ad6bbb72590988bcee0872961e45f279f76bf472f0c` |
| `governance/new_host_route_cloud_r1/A6C_APPOINTMENT_HANDOFF_20261022.md` (Phase-1 disclosure requirements; appointment, determination and proceed templates) | 7,250 | `e06c327ff5b0db0d728a4de4a99df21b4f39b33639ca8790648bca830c2a5701` |
| `governance/new_host_route_cloud_r1/READINESS_MATRIX_R4_ERRATUM_E13_20261022.md` | 2,522 | `be98391986933125285eb6e073bcf64e61d06aaf7ac83a56f7a333ab0309975e` |
| `ledger/TARGET_INTEGRITY_LEDGER.jsonl` | one appended line, append-only | — |

## 2. Content, as required by the owner

* **The scope** is owner decision E-5 §3:
  * S1, the YC1 inventory;
  * S2, the D-* package and errata;
  * S3, the Cloud development and integration layer;
  * S4, the L-DET reference list, **only if A16 remains in scope** and the appointment fixes its allowlist;
  * S5–S11, as the recorder identified them.
* **The covered results:**
  * MISSING_PRIMARY_SOURCE: a6–a11, a13, a14, a16–a18, a21–a23;
  * FREE_CHOICE: a12, a20;
  * NOT_DETERMINABLE: a19;
  * the T2 omissions.
* **Stated in the brief and the handoff:**
  * A6b is **input only**;
  * **no affected output may be adopted before independent re-derivation or confirmation**;
  * re-derivation **cures no later-proven role or exposure violation**.

## 3. Checks

* **Allowlist bindings.** 40 entries, each verified against git for length and sha256 after the brief was generated.
  * Part 1: 39 files at `4f814796`.
  * Part 2: `p5y_k5_cell308_mbs_r1/code/mbs308_host.py` at `142d97a9`. This is the pushed MB-S candidate branch, not
    the excluded MB r1 namespace `p5y_k5_cell308_mb_r1/`.
* **Pre-binding scan.** All 40 inputs were scanned in confinement (scanner `e103c196`, configuration `ab0104c6`,
  `python3 -I -B`, counts only). Result: 35 text and 5 py files, **0 findings**, controls detected, PASS.
* **The commit's own staged blobs** are covered by the scoped check reported in the commit message. The ledger was
  checked as append-only, with only the added line scanned (the deviation disclosed in
  `OWNER_STATEMENT_7_RECEIPT_20261022.md` §6).

## 4. Where it sits

* This commit is on `claude/youthful-goodall-xld4n8`, as a fast-forward of the integration head `4f814796`.
* **The integration branch `codex/cell308-claude-r5-integration` is left at `4f814796`, as the owner directed.**
* Integrating this preparation is a later owner choice: a fast-forward of the integration branch to this commit.

## 5. Not done

* No statement 1, 1B or 1A is issued.
* No candidate is appointed or launched.
* No proceed instruction is sent.
* No trace or re-derivation is run.
* The register was not read.
* Nothing is adopted.
* There is no T6 ruling.
* There is no host, grant, freeze or execution.
* `ledger/briefs/BRIEF_INDEX.md` is **not** updated. The owner did not request it, and the index row stays pending.

## 6. The recorder

`claude_cloud_recorder_20261022` (`session_01EKeyysqJNJgvrdiLFAA43o`). Its limits and contacts are as disclosed in
`OWNER_STATEMENT_7_RECEIPT_20261022.md` §5. In addition, for the allowlist check it computed the sha256 and length of
`mbs308_host.py` at `142d97a9` without displaying its content.
