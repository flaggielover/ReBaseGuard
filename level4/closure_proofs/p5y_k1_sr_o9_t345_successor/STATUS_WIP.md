# T3/T4/T5 successor — WORK IN PROGRESS (no status claimed yet)

Final over all 3,994 patches:
- **Cell 150:** T3 PASS, T4 all m PASS, T5 28/28 (provisional until the representative set completes).
- **Cells 0 and 250:** T3 PASS, T4 all m PASS.
- **Cell 275:** T3 PASS; T4 passes m = 1 and fails m = 2, 3, 5 (B_cover, curvature-driven).

Cells 313 and 315 are still running. On partial data they already show B_cover failures, which are final
because every certificate quantity is monotone in the per-patch sups.

The aggregator's provenance was fixed: it now hashes the records consumed for the cell, instead of the shared,
still-growing chunk files. The superseded replay is kept under `evidence/replay/superseded_whole_file_provenance/`.
