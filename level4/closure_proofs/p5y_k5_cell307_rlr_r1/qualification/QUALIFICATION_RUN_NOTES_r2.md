# Qualification run notes: r2, the official run at freeze r2 `cd5016f1`

* **How it ran.** One launch, under `caffeinate -i`: `python3.14 -I -S -B
  level4/closure_proofs/p5y_k5_cell307_rlr_r1/code/rlr307_qualify.py`, from the repository root, with HEAD at the
  freeze commit. The wall time was 4174.6 s.
* **Result.** `QUALIFICATION PASS: Q1..Q12 = P`, and `cases_missing_pass = []`.
* **Stdout.** `QUALIFY_STDOUT_r2.txt`. It holds:
  * the sandbox flow status lines, from a `git clone --shared` sandbox: stubs only, sandbox refs only;
  * the expected P11 worker-bootstrap traceback.
* **Predecessor.** The r1 run at freeze `5c6667fd` is preserved in `r1_failed/` (FAIL on Q12 from a verifier
  aggregation defect; see `r1_failed/FAILURE_RECORD.md`). This run's decoy Stage 1 equals r1's exactly (QC03_cross_run).
* **Ledger.** The ledger lines are in the report's `ledger_entries`. They are appended to the ledger after the seal.
