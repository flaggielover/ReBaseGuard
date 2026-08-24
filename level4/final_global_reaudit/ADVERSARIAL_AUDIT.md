# Final global re-audit adversarial audit

First run: **24/26 FAIL**. Final run: **26/26 PASS**.

| ID | Attack | First | Final | Final evidence |
|---|---|---|---|---|
| A1 | historical Stage-F cannot be rewritten to CLOSED | PASS | PASS | Stage F remains immutable LEVEL-4-PARTIAL |
| A2 | previous post-closure audit cannot be rewritten | PASS | PASS | previous re-audit remains immutable LEVEL-4-PARTIAL |
| A3 | Stage E zero-of-three cannot be erased | PASS | PASS | Stage E remains PARTIAL with H-E5 0/3 |
| A4 | V2 one-of-three cannot be erased | PASS | PASS | V2 remains PARTIAL with H2-4 1/3 |
| A5 | V3 cannot become universal external validation | PASS | PASS | publication-safe claim is explicitly scoped |
| A6 | P2 cannot become universally safe | PASS | PASS | P2 remains regime-dependent |
| A7 | SR numerical evidence cannot become rigorous certificate | PASS | PASS | Gamma_SR > 2 remains confirmatory numerical |
| A8 | SR Arb OPEN cannot be hidden | PASS | PASS | SR rigorous local-instability certificate remains visible and OPEN |
| A9 | D4 cannot become operational phase-transition proof | PASS | PASS | D4 is a deterministic local-stability map only |
| A10 | historical Track 3 failure cannot be erased | PASS | PASS | historical Track 3 remains PARTIAL with failed numerical gate |
| A11 | Track 1A failure cannot be erased | PASS | PASS | Track 1A remains failed |
| A12 | novelty verification cannot become absolute novelty | PASS | PASS | N2 partial-overlap/claims-narrowed position preserved |
| A13 | priority language cannot enter safe summaries | PASS | PASS | publication/resume summaries contain no priority language |
| A14 | original mandatory classification cannot change | PASS | PASS | all 18 classifications match the protected original |
| A15 | original requirement count cannot change | PASS | PASS | exactly 18 stable rows |
| A16 | acceptance thresholds and fallback rule cannot change | PASS | PASS | only PASS satisfies a mandatory row; CLOSED-WITH-LIMITATIONS unavailable |
| A17 | report counts cannot desynchronize from JSON | PASS | PASS | ledger is byte-derived from the canonical decision |
| A18 | changed rows cannot omit evidence paths | PASS | PASS | all three current transitions have complete existing evidence chains |
| A19 | later campaigns cannot close wrong requirements | PASS | PASS | six-campaign mapping exactly matches authorized targets |
| A20 | protected hashes cannot mutate | PASS | PASS | 23 trees and 23 files intact |
| A21 | final reproducer cannot depend on network access | PASS | PASS | audit reproducer uses committed local evidence only |
| A22 | generated audit artifacts must be byte-stable | FAIL | PASS | status=PASS byte_stable=True |
| A23 | audit cannot claim all open research questions solved | PASS | PASS | open SR Arb upgrade and remaining limitations are explicit |
| A24 | synthetic mandatory blocker cannot yield CLOSED | PASS | PASS | synthetic verdict=LEVEL-4-PARTIAL |
| A25 | full repository verification must pass | FAIL | PASS | status=PASS checks=1139 |
| A26 | focused final-audit tests must pass | PASS | PASS | focused tests=36/36 returncode=0 |

No scientific gate, classification, threshold, mapping, or historical status was weakened between runs.
