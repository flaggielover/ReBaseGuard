# CUSUM K5 status after the remaining-cell campaign (2026-09-19)

```text
K5_STATUS (CUSUM)                 = PARTIAL
K5_COVERAGE_COMPLETE              = NO
K5_INDEPENDENT_ADJUDICATION       = NOT_RUN for K5 (no closure claim); T-EXT successor adjudicated: ADOPTED (37/37)
NEW_REAL_SCIENTIFIC_ADDRESSES     = 0
FRONT                             = BLOCKED_BY_CERTIFICATION_METHOD (Perron-mode amplification)
M5_TAIL                           = DESIGN_ON_RECORD (execution deferred; cannot change K5 alone)
NEXT_STEP                         = RESOLVE_K5_REMAINING_SCIENTIFIC_BLOCKER
```

## Open sets

| m | before (slot-1 + E6) | after T-EXT (adjudicated) | cells closed tonight |
|---|---|---|---:|
| 1 | 1–132 | 11–132 | 10 |
| 2 | 1–144 | 11–144 | 10 |
| 3 | 1–145 | 11–145 | 10 |
| 5 | 1–148, 305–309 | 11–148, 305–309 | 10 |

The machine-readable coverage map is `K5_COVERAGE_MAP.json`: cell → verdict → route → evidence → artifact sha256,
for every cell 0–309 and every m. Open cells carry their Phase A blocker class.

## Why the rest is open (one sentence each)

- **Graded zone, cells 11–40.** The only certified R''' information is the e = 0 point, and the certified M5 majorant
  of the 0-anchored tower explodes past cell 5 (2.8e10 at cell 10, 3.6e19 at cell 40). Anchors away from 0 would
  need a new executor mode, and the 0-anchored M4 makes their blocks far smaller than a cell.
- **Scalar zone, cells 41 up to 132 / 144 / 145 / 148.** The graded parity method does not exist there (the
  determinant is < 0). Every existing certified enclosure is set by the Perron-mode resolvent constant (C_upper
  514–1026), and the K1 point enclosure of g already contains 0 on 64–83 cells per m.
- **m = 5 tail, cells 305–309.** The failure is pure curvature slack. It is closable with about 11 new point
  evaluations and theorem K5-B-T (`tail_design/`), but that cannot change K5 while the front is blocked.

## What would unblock the front

A Perron-deflated certified resolvent (`phase_b/FRONT_BLOCKER.md` §4).
- A non-certified float diagnostic puts the deflated sup-norm at 11.1–11.3, flat across e ∈ [0, 0.1135], against
  325–466 for the full resolvent.
- That is about a 30–40× cut in the dominant constant, which is possibly sufficient once the Perron component is
  certified exactly.
- This is a research-grade successor with its own theorem, certificate and qualification. It is not an overnight run.

## P5Y consequence (nothing about P5Y changes tonight)

| obligation | state |
|---|---|
| CUSUM K1 | CLOSED (Aux5 composite closure, 326 cells, `ce7fb933`) |
| CUSUM K5 | **PARTIAL**: cells 0–10 and 133/145/146/149+ pass per m; front 11–K_m and the m = 5 tail open |
| SR/PS1 K1 (generation 2, AWS) | NOT CLOSED: independent long-running campaign on AWS; not inspected or touched tonight |
| SR K5 | NOT STARTED: needs SR K1 records, plus an SR order-3 producer (`AUX3_SR_FEASIBILITY_FAIL` on record) |
| K2 / K3 | CLOSED (`p5y_k2_k3_closure_packet`) |
| K4 | assembly checkpoint FROZEN; waits for complete K1 inputs (SR) |
| publication / assembly | P5Y final assembly waits on SR K1, SR K5 and CUSUM K5 |

`P5Y_STATUS = NOT_CLOSED`. It depends on the SR/PS1 campaign (K1, and then SR K5) and on resolving the CUSUM K5 front
blocker.

## Integrity

- Historical and frozen artifacts: none modified. `git diff 84299314..HEAD` touches only this namespace.
- AWS PS1: not touched.
- No real scientific run was launched, and no authorization or countersignature was created.
