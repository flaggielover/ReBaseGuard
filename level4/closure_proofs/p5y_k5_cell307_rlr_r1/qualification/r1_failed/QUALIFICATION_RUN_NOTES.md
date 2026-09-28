# Qualification run notes (official run at the freeze commit 5c6667fd)

1. **First launch refused, fail-closed.**
   * `rlr307_qualify.py` refused at its preconditions: `no_review_grant_result = false`.
   * Cause: the empty, untracked directories `adjudication/`, `authorization/` and `qualification/`. They were created
     with `mkdir` when the namespace was set up (before any file existed), and `os.path.lexists(<NS>/adjudication)` is
     true for an empty directory.
   * No adjudication, grant or result existed; git tracks no empty directory.
   * The three empty untracked directories were removed (`find -type d -empty -delete`) and the verifier was
     relaunched. No tracked or frozen file changed, and HEAD stayed the freeze commit.
   * The refused attempt's complete output was a single line:
     `QUALIFY REFUSED: preconditions {... "no_review_grant_result": false ...}`.
2. **Second launch.** This is the official run whose report is `RLR307_QUALIFICATION.json`. It ran under
   `caffeinate -i`, as `python3.14 -I -S -B level4/closure_proofs/p5y_k5_cell307_rlr_r1/code/rlr307_qualify.py` from
   the repository root.
3. **Ledger.** The qualification commit may hold qualification files only. So the ledger lines of these runs are in
   the report's `ledger_entries`, and they will be appended to `ledger/ZERO_TARGET_LEDGER_307.jsonl` after the seal.
