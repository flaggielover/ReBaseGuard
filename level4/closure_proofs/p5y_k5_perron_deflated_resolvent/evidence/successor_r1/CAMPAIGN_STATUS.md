# K5_PERRON_DEFLATION_FEASIBILITY — campaign status (2026-09-19, after adjudication)

```text
START_FRONTIER                  = 5a8c194d
FREEZE_COMMIT                   = 730d6e83  (SUCCESSOR_PROTOCOL.json sha256 ef6c1d14…, 42 pins)
QUALIFICATION_COMMIT            = 1f5edae9  (S00-S12 QUALIFIED at the freeze commit; QUALIFICATION_RESULT sha256 90446aa6…)
SEAL_COMMIT                     = 2e9b1585  (two frozen evaluations byte-identical, S07 PASS; DEFLATED_CONSUMPTION sha256 5dcc9b7d…)
CERTIFIED_OPERATOR_REGISTRY     = evidence/registry_r1/REGISTRY.json sha256 1b7f5da7…  (operator only)
FEASIBILITY_GATE (frozen rule)  = USEFUL (certified constants dominated by the forecast model at scale 1.6 on every front cell)
INDEPENDENT_REVIEW              = r1 PASS_WITH_NOTES, r2 PASS_WITH_NOTES, r3 NOT_READY (B1), r4 READY_TO_FREEZE after one fix (applied)
ADJUDICATION                    = ADOPTED (adjudication_r1/: 17 PASS + 1 informational, 3 non-blocking notes; session-independent)
COVERAGE_MAP                    = r3, K5_COVERAGE_MAP_R3.json sha256 6d598dc5… (supersedes r2 ec5c3926 for the CUSUM K5 cover)
PERRON_DEFLATION_GATE           = FEASIBLE_READY_FOR_SUCCESSOR   (successor frozen, qualified, evaluated, sealed, adopted)
NEW_REAL_SCIENTIFIC_ADDRESSES   = 0 ; real-input guard DENY
K5_STATUS                       = PARTIAL (open cells remain: see below)
```

## Adopted result (sealed consumption, adjudicated)

| m | open before (map r2) | open now (map r3) | newly passing |
|---|---|---|---|
| 1 | 11–132 (122) | 11–35 (25) | 36–132 (97) |
| 2 | 11–144 (134) | 11–41 (31) | 42–144 (103) |
| 3 | 11–145 (135) | 11–42 (32) | 43–145 (103) |
| 5 | 11–148, 305–309 (143) | 11–44, 305–309 (39) | 45–148 (104) |

Union of open cells across m: 11–44 and 305–309 (39 cells). The pre-registered guarantee was at most 11–44/52/52/54 open;
the float forecast expected about 11–38/45/46/48. The sealed result is inside both.

## What remains open

- **Lower front, cells 11–35/41/42/44.** The order-0 floor E_a[τ]·‖ρ_F‖ is above |g| there. This needs order-3 information
  beyond e = 0, e.g. an atom-deflated order-3 tower (see `FEASIBILITY_REPORT.md` §5).
- **m = 5 tail, cells 305–309.** Outside the deflation domain; unchanged, and `tail_design/` still applies.

K5 cannot be reported as closed while either set is open.
