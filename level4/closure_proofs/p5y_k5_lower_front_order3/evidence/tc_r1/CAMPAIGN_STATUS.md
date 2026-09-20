# Campaign A (CUSUM K5 lower front) — status after adjudication

```text
START_FRONTIER          = 7cb01e38 (coverage map r3 adopted; open m1 11-35, m2 11-41, m3 11-42, m5 11-44 + 305-309)
GATES (frozen first)    = e89b33f2  config/FEASIBILITY_GATES_A.json
FREEZE                  = 3f540a33  config/TC_PROTOCOL.json sha256 10ff7e37…, 84 pins, 34 addresses (cells 11-44)
QUALIFICATION           = 2be00ddc  QUALIFIED at the freeze commit (S00-S09), result sha256 f95da15f…
AUTHORIZATION           = bb06260c  fresh-context review AUTHORIZED with conditions C1-C8
GUARD ALLOW / RUN HEAD  = 74d67ef4  (guard back to DENY at the seal)
SEAL                    = bc4235d0  TC_INDEX 51c5ca93…, 34 gated records, reproduction of cells 11 and 44 byte-identical,
                                    14.203 new-real CPU-hours
CONSUMPTION             = ad108619  TC_CONSUMPTION sha256 1fa8d8de… (two runs byte-identical), replay gate PASS,
                                    136 cross-check comparisons, no empty intersection
ADJUDICATION            = ADOPTED   (27 PASS, 7 INFO, 3 not checkable locally, 0 FAIL; the adjudicator reproduced
                                    theorem TC from its own implementation, 136/136 enclosures exact, and re-derived the
                                    K5-B pass sets and the whole 160-entry via map)
COVERAGE MAP            = r4, K5_COVERAGE_MAP_R4.json sha256 a3bddd83… (two generations byte-identical)
NEW REAL ADDRESSES      = 34 (CUSUM cells 11-44, midpoint, orders <= 3, r = 0..4); guard DENY again
K5_STATUS               = PARTIAL   (m = 5 tail 305-309 still open)
```

## Result

| m | open before (map r3) | open now (map r4) | newly passing |
|---|---|---|---|
| 1 | 11–35 (25) | — | 11–35 |
| 2 | 11–41 (31) | — | 11–41 |
| 3 | 11–42 (32) | — | 11–42 |
| 5 | 11–44, 305–309 (39) | 305–309 (5) | 11–44 |

The union of open CUSUM cells fell from 39 to 5. `K5_COVERAGE_COMPLETE = false`; K5 remains **PARTIAL** because the
m = 5 tail 305–309 is open. The tail is Campaign B (`../../p5y_k5_m5_tail_closure/`): audited, route T2 selected,
class USEFUL, ≈ 2.2 CPU-h of new real compute, execution NOT started.

## What the successor did

Theorem TC (`theorem/THEOREM_TC.md`): the whole-cell radius of the adopted K1 curvature enclosure is set by the
ρ-terms of e-constant candidates. Replacing the candidate by its Taylor polynomial in e (F̂ + tD̂ + t²Ĥ/2 + t³Ĝ/6, the
order-3 term being the only new object) and propagating the residual through the adopted atom-deflation constants
(theorem AD, registry r1) gives whole-cell enclosures of R''_m with half-widths 4.2–5.5 instead of 122–336. The certified
lower ends are positive on every lower-front cell (e.g. cell 11: +9.50 for m = 1, +3.99 for m = 5), so μ_k ≥ 0 and the
frozen K5-B chain carries from γ_10 < 0 across the whole front.

Procedural defect (disclosed, adjudicator note N7): the coverage map r4 and a stale in-progress copy of the
adjudication were committed at f2ac1eb3 before the adjudication was handed over. The final adjudicator re-verified the
published map as exactly what the verdict permits, and regeneration after the final verdict is byte-identical
(`adjudication_r1/SEQUENCING_DEFECT_NOTE.md`). Open obligations from the adjudication: N1/C7 cross-reference in the
order-3 namespace (that namespace is adopted and must not be edited here), N3 oracle coverage, N5 no identity gate on
the four new order-3 fields.

Disclosures: the frozen `Order3Certifier` was executed on real cells 11–44 under this protocol while the order-3
producer's own registry stays FROZEN EMPTY (SEAL C7); the consumption needed `PYTHONINTMAXSTRDIGITS=0` because CPython
3.12 refuses int→str beyond 4300 digits inside the adopted adapter (consumption_r1/CONSUMPTION_NOTE.md); the frozen prose
says cap 24 CPU-h while the binding protocol says 30 (SEAL note A; actual spend 14.203).
