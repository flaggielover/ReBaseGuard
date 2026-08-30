# Concrete Gaussian SR assumption discharge

This table was pre-registered in `results/assumption_targets.json` before final
experiments. Numerical evidence discharges none of these rows.

| ID | Obligation | Status | Priority-2 discharge | Provenance |
|---|---|---|---|---|
| SR-A1 | Almost-sure finiteness and geometric tail | `PROVED` | `|Z|>=log(A)+1/2` forces a crossing from every live state; its probability is uniformly positive near zero, giving a geometric tail. | `PROOF.md` §1; authoritative recurrence audited from Stage D |
| SR-A2 | Stopped measurability | `PROVED` | Finite-prefix SR states and alarm events are Borel; stopped variables are countable pastings on `{tau=n}`. | `PROOF.md` §1 |
| SR-A3 | `A_m` integrability | `PROVED` | `|A_m|<=S_tau<=b_A(tau-1)+|Z_tau|`, controlled by a stopped exponential moment. | `PROOF.md` §2 |
| SR-A4 | `A_mT_tau` integrability | `PROVED` | `|A_mT_tau|<=S_tau^2`, and the stopped exponential moment supplies all polynomial moments. | `PROOF.md` §2 |
| SR-A5 | Required exponential stopped moments | `PROVED` | Independence at the final trial plus the geometric survival bound gives finite `E exp(a|Z_tau|+c tau)` for small `c`; the nonterminal forcing bound controls `S_tau`. | `PROOF.md` §2 |
| SR-A6 | Stopped likelihood identity | `PROVED` | Finite-prefix Gaussian density ratios are summed over `{tau=n}` to obtain `exp(-eT_tau-e^2tau/2)` on `F_tau`. | `PROOF.md` §3 |
| SR-A7 | Local derivative domination | `PROVED` | The derivative bound is absorbed by the stopped exponential-moment margin for sufficiently small `delta`. | `PROOF.md` §4 |
| SR-A8 | Reflection symmetry and centering | `PROVED` | Path negation exchanges charts, preserves the inclusive first alarm, and negates `A_m,T_tau`; `Q_0` is invariant. | `PROOF.md` §6; Lean finite-path reflection spine |

All eight concrete obligations are analytically discharged. Generic dominated
integration machinery is consumed by Lean, but no concrete row is labeled
`INHERITED_GENERIC` and no numerical estimate is used as a proof.
