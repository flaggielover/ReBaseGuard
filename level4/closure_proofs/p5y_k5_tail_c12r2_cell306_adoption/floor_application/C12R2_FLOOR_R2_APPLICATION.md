# C12-R2 — mechanical application of floor r2 to the sealed cell-306 evidence

Prepared for the independent adoption adjudicator. **It decides nothing and computes no Γ**: every value below is read from committed bytes, and the only arithmetic is the sign of an exact rational string.

All 21 provenance checks pass: **True** (HEAD `1173670f`).

| requirement | I1 | I2 | result | evidence |
|---|---|---|---|---|
| F1'(a) six constants certified on the whole block | certified (REGISTRY_C1/C2, C2 two-pass re-certification) | certified (C11R 4 targets CERTIFIED, C11RD runs CERTIFIED) | **PASS** | level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment/evidence/comparison/C11R_COMPARISON.json; level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/evidence/runs/C11RD_RUNS.json; floor r2 soundness_evidence |
| F1'(b) constant classes AGREES/STRONGER; statements EQUIVALENT/STRONGER; accepted comparisons | - | - | **PASS** | level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment/evidence/comparison/C11R_COMPARISON.json (7375b9cd COMPARISON_ACCEPTED); level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/evidence/comparison/C11RD_COMPARISON.json (90265349 COMPARISON_ACCEPTED); N9 7d67989d/fb237288 |
| F1'(c) soundness evidence per implementation | pinned | pinned | **PASS** | C12R2_FREEZE.json soundness_* pins, sha256 verified at HEAD |
| own-supply Gamma(5,306; S_I) < 0 | TRUE (sign -1) | FALSE (sign 1) | **I1 PASS, I2 FAIL** | level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json cells['306'].Gamma_exact = sealed control; level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/evidence/execution/C12R2_CELL306_RESULT.json target (blob 0ac46b3d) |
| F1' = (a) and (b) and (c) and (d: both own-supply Gamma < 0) | - | - | **FAIL** | floor r2 rule.limbs.F1_prime; disagreement.closure |
| F2 (uniform-A margin >= 1.25 on S_I1), historical, not re-run | - | - | **FAIL** | C2_ADJUDICATION.md section K; C10 Q2_phase11_cell306; floor r2 known_historically |
| base clause: Gamma(5,306; chosen supply S_I1) < 0 | TRUE | - | **PASS** | sealed control = C2 committed Gamma_exact |
| adoption criterion: base AND (F1' OR F2) | - | - | **NOT_MET** | floor r2 rule.base; gate G12; fail_closed |

- Γ(5,306; S_I1) = -0.030469257709306738 (sealed exact rational, sign -1); equals C2's committed record.
- Γ(5,306; S_I2) = 0.005159101140006536 (sealed exact rational, sign 1; sha256 of the exact string 8ef2815cd478b43b…); pass as sealed: False.
- The strict criterion Γ < 0 is applied with no tolerance, as the frozen rule states (`Gamma = 0 or an incomplete evaluation fails`).
- Mechanical outcome: base **True**, F1′ **False**, F2 **False** (historical), adoption criterion **NOT_MET**.
