# P5Y K1 SR O9 executor — T2 per-patch engine: NOT-CLOSING evidence

**STATUS: `T2_EXECUTOR_IMPLEMENTED_ENDPOINT_GATE_NOT_CLOSING`. This is NOT a CLOSED T2.**

* The generalized SR equation map is implemented (`config/EQUATION_MAP.json`: 45 residual
  nodes + 18 operator-image nodes); the 46-candidate / 102-contract universe is preserved
  exactly (contract set equals the frozen census).
* Authorized-runtime references pass: A4 (the generic engine in Task1R baseline mode is
  byte-identical to the frozen certifier), A5.3 (O9 mode equals the amendment certificate,
  exact gates pass), O9 packet references (C).
* One patch, full DAG executes (cell 150, patch (17,11): 63 nodes, 102 contracts, all
  bounds finite and nonnegative).
* **The frozen endpoint-sliver local gate `C * delta_end <= 1/250` systematically fails**
  across low/middle/high drift and interior/boundary/small-panel patches (table in
  `config/T2_NOT_CLOSING_RECORD.json`, raw run in `evidence/b_end_characterisation.txt`).
* T2 scientific closure is NOT achieved. No whole-cell `delta_cell`, refinement, `B_cover`
  or obligation closure is claimed. This namespace is immutable negative evidence.
