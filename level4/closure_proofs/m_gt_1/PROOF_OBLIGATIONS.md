# Proof obligations

| ID | Obligation | Status | Evidence |
|---|---|---|---|
| M1 | Stage-D definition correspondence | HUMAN-PROVED | `DEFINITION_AUDIT.md`; line-by-line code match |
| M2 | measurability of stopped functional | HUMAN-PROVED | `THEOREM.md`, Lemma 1 |
| M3 | integrability | HUMAN-PROVED | `THEOREM.md`, Lemma 2 and exponential-moment inputs |
| M4 | differentiation under stopping | HUMAN-PROVED | `THEOREM.md`, Lemma 4 |
| M5 | stopped Gaussian score representation | HUMAN-PROVED | `THEOREM.md`, Lemma 3 |
| M6 | exact treatment of `tau<m` | HUMAN-PROVED | `DEFINITION_AUDIT.md`, short-cycle identity |
| M7 | exact rho scaling | HUMAN-PROVED | `F_{rho,m}=rho F_{1,m}` from zero-mean fresh term |
| M8 | m=1 reduction | HUMAN-PROVED | `w=1`, `A_1=Z_tau`, `C_1=0` |
| M9 | lag decomposition | HUMAN-PROVED | `widetilde Gamma_m=m^-1 sum gamma_r+C_m` |
| M10 | final derivative identity | HUMAN-PROVED | `THEOREM.md`, Theorem T1/T2 |
| M11 | independent numerical correspondence | FAILED | primary derivative criterion passed; complete gate failed auxiliary map-distinction threshold |
| M12 | Lean proof spine and axiom audit | OPEN | not started because M11 stopped the campaign |
| M13 | interval/certificate implication if applicable | HUMAN-PROVED | no new numerical inequality claimed; certificate not applicable under frozen scope |

Only the statuses `OPEN`, `HUMAN-PROVED`, `NUMERICALLY-CHECKED`,
`LEAN-CHECKED`, `RIGOROUS-CERTIFIED`, and `FAILED` are used.
