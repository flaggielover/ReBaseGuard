# Independent static review of the r1 executor (freeze 8ffcfaff, qualification 80a3ab2b): FAIL

The reviewer was a separate read-only agent session. It ran no computation on python-flint, the operator, K1 records
or hosts.

## Findings

| # | question | verdict | summary |
|---|---|---|---|
| 1 | Faithful R4 mathematics | PASS_WITH_NOTES | Point cell, residual set with Repair1, origin values, `eta_mid` = 0, `C_hull` = `C_upper` valid on [0, x1], h1 omission correct, anchor coverage, exact transport and precision all check out |
| 2 | Certified objects | PASS_WITH_NOTES | Exact strings, no floats. The certificate-chain check is presence-only, and the precision probe reads back the context it just set |
| 3 | Preregistration preserved | **FAIL** | Preregistered Q01–Q16 not implemented (notably Q08, Q10, Q09, Q04 final gate and SciPy guard, Q05/Q13). The consumer used its own QE set instead of `probe_rules.producer_qualification` / `science_usable` |
| 4 | Guard | PASS_WITH_NOTES | Guard first; production re-check; Tripwire only; the adapter passes no payload; the smoke leaks no information about R'''(0). QE05 would VOID every genuine real record |
| 5 | Separation | PASS | |
| 6 | Serialization | PASS_WITH_NOTES | Determinism shown on manufactured systems only |
| 7 | Cost | PASS_WITH_NOTES | 6172 ≤ 9000, and the committed-collocation term double-counts, so the estimate is conservative. Q08, Q10 and the tower are unmeasured but small |
| 8 | Trust model | PASS_WITH_NOTES | Honest, but the spec claimed a final gate and SciPy guard that the code did not implement |

**Other findings.**
- No mutation touched the production `_CusumStack` methods.
- An exception inside a fixture counts as a detection. That is acceptable, but DEV_CALIBRATION overstated the rule.

## Required repairs

1. Aux5 final gate and SciPy guard.
2. Preregistered Q gates inside the executor, recorded in the seal.
3. Consumer uses `probe_rules.producer_qualification` / `science_usable`; QE05 removed.
4. ARITHMETIC_STARTED event, in-process authorization and prelaunch check, VOID sealing, SIGXCPU handling.
5. Activation must not require a code change after the countersignature.
6. Mutations on the production-stack methods.

**Disposition.** Repaired in r2 (`EXECUTOR_SPEC_R2.md`).
