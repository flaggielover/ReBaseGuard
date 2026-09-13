# P5Y K2/K3 closure packet (additive)

| Record | Verdict |
|---|---|
| `K2_ADJUDICATION.md` | `K2_ANALYTIC_PROOF_VALID = YES`, `K2_CERTIFICATION_SEMANTICS_SATISFIED = YES`, `K2_FINAL = CLOSED` |
| `K3_ADJUDICATION.md` | `K3_BINDING_REQUIREMENT = FINITENESS_ONLY`, `K3_EXISTING_THEOREM_DISCHARGES_REQUIREMENT = YES`, `K3_FINAL = CLOSED` |

K2 gives s_min ≥ κ*_D / m², with κ*_CUSUM = 121/46875 and κ*_SR = 49/30000. These are exact rational constants, replayed by `code/verify_k2_constants.py` and checked by `tests/test_k2_constants.py`.

K3 is discharged by P5-T4/T5, which give M2 ≤ C_D with C_CUSUM ≤ 9.8959e8 and C_SR ≤ 1.4054e11. The threshold `M2 ≤ 100·s_min` is **not** adopted: no binding consumer needs tightness.

Nothing in this packet is result-bearing. It changes no frozen K1 threshold or universe and does not claim K1 or P5Y closure. Independence limits are disclosed in each adjudication. Both verdicts are recommended for countersignature.
