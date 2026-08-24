# Adversarial audit

The first run is preserved byte-for-byte in `results/adversarial_first.json`:
**16/18 FAIL**. A4 was a checker self-match
and A17 preceded the final verification record. The final run is
**18/18 PASS**.

| ID | Check | First | Final | Final evidence |
|---|---|---|---|---|
| A1 | historical Stage-F artifacts unchanged | PASS | PASS | content hash matches frozen baseline |
| A2 | post-closure re-audit unchanged | PASS | PASS | content hash matches frozen baseline |
| A3 | D4 closure unchanged | PASS | PASS | protected D4 hash and scoped decision preserved |
| A4 | no new scientific simulation | FAIL | PASS | audit code contains no simulation/RNG campaign |
| A5 | no unsupported first | PASS | PASS | current safe outputs contain no priority use of first |
| A6 | no unsupported first-ever | PASS | PASS | current safe outputs contain no first-ever |
| A7 | no unsupported unprecedented | PASS | PASS | current safe outputs contain no unprecedented |
| A8 | no paper classified DIRECT from title alone | PASS | PASS | DIRECT count=0; every DIRECT would require text audit |
| A9 | inaccessible papers explicitly marked | PASS | PASS | explicitly marked=3 |
| A10 | threatening prior art preserved | PASS | PASS | nine HIGH-PARTIAL works including W08 are persisted and audited |
| A11 | search query provenance complete | PASS | PASS | 36 frozen queries completed in each of two indexes |
| A12 | snowball provenance complete | PASS | PASS | two backward/forward rounds persisted; stopping rule satisfied |
| A13 | C1-C11 matrix complete | PASS | PASS | 33 rows x 11 components |
| A14 | claim firewall generated from canonical JSON | PASS | PASS | generator-owned mirrors are byte-stable |
| A15 | decision mechanically derived | PASS | PASS | NV1-NV12 true => CLOSED; partial overlap => N2 |
| A16 | external-validation blocker untouched | PASS | PASS | Stage E hash preserved; blocker remains explicit |
| A17 | repository verifier green | FAIL | PASS | 983 distinct checks recorded PASS |
| A18 | clean-tree/hash integrity | PASS | PASS | unauthorized dirty paths=[]; all protected hashes=True |

No scientific or literature criterion was weakened between runs.
