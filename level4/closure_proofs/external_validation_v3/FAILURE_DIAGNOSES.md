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
