# K5 remaining-cell closure campaign (CUSUM): `K5_REMAINING_CELL_OVERNIGHT_CLOSURE`

This namespace is additive. It modifies no frozen or historical artifact: the slot-1 record, ledger, adjudication, E6,
K5-B, the K1 records, the R1–R5 artifacts and the CUSUM closure are all unchanged.

| phase | where | state |
|---|---|---|
| A. exact open-cell map | `phase_a/` (`OPEN_CELL_MAP.json`, `OPEN_CELL_AUDIT.md`, built by `code/open_cell_map.py`) | done |
| B. routes and strategy | `phase_b/STRATEGY.md`, `phase_b/FRONT_BLOCKER.md` | done |
| C. independent strategy review | `phase_c/STRATEGY_REVIEW.md`, `phase_c/REVIEW_DISPOSITION.md` | PASS_WITH_NOTES; every finding dispositioned before the freeze |
| D–G. T-EXT: deterministic wider-hull transport from the adopted slot-1 record | `transport_extension/` | QUALIFIED, sealed `cb97cabc…`, **ADOPTED** (37/37); K1 cells 1–10 now pass for every m |
| I. m = 5 tail design | `tail_design/` | DESIGN_ON_RECORD; execution packet deferred |
| K. status | `K5_STATUS.md`, `K5_COVERAGE_MAP.json` | K5 (CUSUM) PARTIAL; front blocked by the certification method |

Starting point: `p5y-postk1-frontier` at `84299314` (the adopted slot-1 probe `cf90f1ea…`, E6 consumption
`89017388…`).
