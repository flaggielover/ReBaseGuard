# Track-3 proof obligations

| ID | Obligation | Status | Evidence |
|---|---|---|---|
| D1 | frozen residual/code convention | PASS | `DEFINITION_AUDIT.md` |
| D2 | derive `f_e(z)=f(z+e)` and score sign | PASS | `s=f'/f=-psi` |
| D3 | event-sliced stopped likelihood identity | HUMAN-PROVED CONDITIONALLY | `THEOREM.md` hypotheses 1--9 |
| D4 | stopped differentiation | HUMAN-PROVED CONDITIONALLY | integrable difference-quotient/density-derivative dominator |
| D5 | actual raw-reuse specialization | PASS | `Gamma_f=E[Z_tau sum psi]` |
| D6 | Gaussian reduction | PASS | exact `psi(z)=z`, `S_tau=-T_tau` |
| D7 | rho scaling | PASS | exact affine expectation algebra |
| D8 | symmetry separated from derivative theorem | PASS | even density plus detector reflection only for oddness/fixed point |
| D9 | local-instability premises separated | PASS | `rho|1-Gamma_f|>1` |
| H1 | historical t3 ambiguity preserved | PASS | neither old estimand is raw-reuse gain; Stage D remains `AMBIGUOUS` |
| N1 | protocol and seeds frozen before outcomes | PASS | SHA-256 `52a27f…55f6` |
| N2 | source-level implementation separation | PASS | raw Route A versus signed-chart Route B |
| N3 | Gaussian numerical control | PASS | combined `|z|=0.928`, 0.442% |
| N4 | all-family primary correspondence | FAIL | t3 replication relative discrepancy 4.605% > 3% |
| N5 | ties and simultaneous crossings | PASS | zero for all regular cells |
| N6 | irregular-support negative control | PASS | uniform boundary-motion mismatch reproduced exactly |
| L1 | Lean authorization | FAIL / NOT AUTHORIZED | frozen numerical gate failed |
| L2 | Track-3 Lean spine | NOT RUN | no `lean/` directory |
| L3 | Track-3 axiom audit | NOT RUN | no formal declarations to audit |
| V1 | retained numerical audit | PASS | exact failed predicate independently reconstructed |
| V2 | historical integrity | PASS | 35 dependency hashes |
| V3 | authoritative repository verification | pending final clean replay | `reproduce.sh` |

The general human theorem is complete at its stated conditional level.  The
campaign closure is partial because N4 failed and therefore L1--L3 cannot
close.

