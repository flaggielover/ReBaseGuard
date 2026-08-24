# Failure diagnoses

## F1 — first checkpoint formatting gate

The first checkpoint attempt stopped before commit because `git diff --check`
found extra blank lines at EOF in newly created files. EOF formatting was
normalized mechanically and the protocol bundle was re-frozen as
`c688dca913c439318815fb89eafab35b860023ad2a1295f85bbcfeec64fa86f4`.
No confirmatory outcome existed, and no scientific choice changed.

## F2 — pre-outcome calibration power projection

The initial 30/20/50 projection counted detector run lengths but omitted the
20-observation fresh block that every policy consumes after an alarm. That made
the stated 40-block calibration projections impossible. Before any V3 policy
outcome, the split was corrected to 20/30/50 and Retail's cycle-bootstrap block
to two. The 50% evaluation share, datasets, hypotheses, margins, event count,
and all closure rules are unchanged. Corrected projections are 46 and 58
calibration blocks for MetroPT and Retail, respectively.

## F3 — execution checkpoint formatting gate

The first P0-gate checkpoint attempt stopped before commit because newly added
execution files had extra blank lines at EOF. Mechanical normalization changed
only bytes, so the execution-config hash was refreshed to
`633cf2fb90f50c47845351f428b324813f6d2e21b33c49ff1ba30b73b8b48d4c`.
The protocol hash stayed unchanged, and no confirmatory result existed.

## F4 — first historical summary adapter

After both confirmatory task analyses were persisted, the first canonical
summary build stopped because it read V2 decision fields at the summary root
rather than under V2's `decision` object. Only the historical adapter was
corrected. V3 outcome arrays, H3 calculations, task verdicts, and the scientific
campaign verdict were already persisted and did not change.

## F5 — first outcome test run was 48/50

Two historical-timing tests correctly passed before outcomes but incorrectly
required confirmatory files to remain absent from the current tree forever.
They now inspect the final protocol commit `e8376cb` and P0 gate commit
`07e2fb7`, where the files are absent. Only test assertions changed; the frozen
outcomes and `EXTERNAL-VALIDATION-V3-CLOSED` scientific verdict are unchanged.
