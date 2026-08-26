# Terminal adversarial audit

First run: **29/32 FAIL**. Final run: **32/32 PASS**.

| ID | Attack | First | Final | Final evidence |
|---|---|---|---|---|
| A1 | historical Stage F remains PARTIAL | PASS | PASS | protected Stage F is LEVEL-4-PARTIAL |
| A2 | previous Final Global Re-audit remains PARTIAL | PASS | PASS | historical Final Global verdict is LEVEL-4-PARTIAL |
| A3 | L4R-06 historical C6 failure preserved | PASS | PASS | Stage C remains PARTIAL and C6 remains FAILED |
| A4 | L4R-06 later same-requirement mapping verified | PASS | PASS | L4R06-POLICY-CLOSED maps only to original L4R-06 |
| A5 | L4R-12 D2.5 negative result preserved | PASS | PASS | negative scientific result remains historical fact |
| A6 | L4R-12 semantics verified investigational | PASS | PASS | frozen semantics permit a sufficiently supported negative answer |
| A7 | no positive-transition rewriting | PASS | PASS | requirement PASS is separated from the negative scientific outcome |
| A8 | L4R-13 remains PARTIAL | PASS | PASS | L4R-13 is unchanged |
| A9 | L4R-13 confirmed nonmandatory | PASS | PASS | STRONG_EXTENSION is nonblocking under the original rule |
| A10 | SR Arb remains OPEN | PASS | PASS | optional Arb certificate remains explicit |
| A11 | no SR certificate inflation | PASS | PASS | Gamma_SR > 2 is numerical and not Arb-certified |
| A12 | novelty remains N2 | PASS | PASS | N2 partial-overlap/claims-narrowed finding retained |
| A13 | no absolute novelty wording | PASS | PASS | allowed claims contain no absolute novelty or priority assertion |
| A14 | V2 remains PARTIAL | PASS | PASS | V2 remains PARTIAL with 1/3 support |
| A15 | Stage E remains 0/3 | PASS | PASS | Stage E remains PARTIAL with 0/3 support |
| A16 | V3 closure preserved without universality claim | PASS | PASS | V3 satisfies its frozen 3-versus-2 scoped rule |
| A17 | no P2 universal-safety claim | PASS | PASS | P2 safety remains regime-dependent |
| A18 | D4 remains local/deterministic | PASS | PASS | D4 is not promoted to an operational theorem |
| A19 | D2.5 remains MATHEMATICAL, NOT OPERATIONAL | PASS | PASS | historical D2.5 label is exact |
| A20 | original 18-row count unchanged | PASS | PASS | canonical and authoritative sources both contain 18 rows |
| A21 | original 16 mandatory rows unchanged | PASS | PASS | exactly 16 authoritative rows are mandatory |
| A22 | no manually altered classifications | PASS | PASS | all classifications match the protected source |
| A23 | all status transitions have evidence paths | PASS | PASS | all eight Stage-F-to-current transitions have existing evidence |
| A24 | counts generated mechanically | PASS | PASS | counts={'PASS': 17, 'PARTIAL': 1, 'FAIL': 0, 'OPEN': 0} mandatory={'PASS': 16, 'PARTIAL': 0, 'FAIL': 0, 'OPEN': 0} |
| A25 | verdict generated mechanically | PASS | PASS | ledger candidate=LEVEL-4-CLOSED |
| A26 | synthetic mandatory PARTIAL forces global PARTIAL | PASS | PASS | counterfactual mandatory non-PASS cannot close |
| A27 | synthetic nonmandatory PARTIAL does not block closure | PASS | PASS | original rule quantifies over mandatory rows only |
| A28 | protected historical hashes unchanged | PASS | PASS | 17 trees and 18 files intact |
| A29 | generated artifacts byte-stable | FAIL | PASS | digest=1b4c6b096d1da0be5882bf283b79b2219ad1ee3dc2865c846fc98f6ae83c9b0b |
| A30 | reproducer offline | FAIL | PASS | terminal audit uses committed local evidence only |
| A31 | focused tests green | PASS | PASS | focused tests=36 returncode=0 |
| A32 | authoritative repository verifier green | FAIL | PASS | status=PASS checks=1229 |

Only missing engineering records failed initially; no scientific rule was weakened.
