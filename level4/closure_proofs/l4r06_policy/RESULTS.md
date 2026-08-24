# L4R-06 numerical results

Scoped verdict: **L4R06-POLICY-CLOSED**

## Frozen hypotheses

- H6-1: **PASS**
- H6-2: **PASS**
- H6-3: **PASS**
- H6-4: **PASS**
- H6-5: **PASS**
- Absolute-delay safety: **PASS**

## Reference improvement family

| m | MSE(P1)-MSE(P3) | simultaneous lower 95% | status |
|---:|---:|---:|---|
| 1 | 0.976795 | 0.971083 | PASS |
| 20 | 0.072342 | 0.072100 | PASS |
| 70 | 0.006919 | 0.006875 | PASS |

## Operational false-alert family

| m | ARL0(P3)-ARL0(P1) | simultaneous lower 95% | status |
|---:|---:|---:|---|
| 1 | 36.634388 | 36.027223 | PASS |
| 20 | 120.873820 | 119.869938 | PASS |
| 70 | 29.470831 | 28.744044 | PASS |

## Detection families

All 16 normalized-response and 16 absolute-delay conditions are retained in `results/scientific_findings.json`.
