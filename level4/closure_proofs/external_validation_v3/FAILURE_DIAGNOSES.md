# Failure diagnoses

## F1 — first checkpoint formatting gate

The first checkpoint attempt stopped before commit because `git diff --check`
found extra blank lines at EOF in newly created files. EOF formatting was
normalized mechanically and the protocol bundle was re-frozen as
`c688dca913c439318815fb89eafab35b860023ad2a1295f85bbcfeec64fa86f4`.
No confirmatory outcome existed, and no scientific choice changed.
