# Lean correspondence and stop state

**Lean:** `NOT STARTED — FROZEN DECOMPOSITION GATE FAILED`  
**Axiom audit:** `NOT RUN`  
**New axioms introduced:** none

The protocol authorized Lean, but the campaign brief also required an
immediate stop if the decomposition correspondence failed. The pooled
independent-route `m=20` cell reached `3.130` SE, outside the frozen three-SE
bound. No `.lean` theorem, placeholder axiom, or partial elaboration was
created after that outcome.

| Target | Intended human statement | Track 1A status |
|---|---|---|
| L1 | `w=min m tau` | HUMAN-PROVED; LEAN NOT STARTED |
| L2 | partition `tau<m` / `m<=tau` | HUMAN-PROVED; LEAN NOT STARTED |
| L3 | short-cycle statistic equals `T_tau/tau` | HUMAN-PROVED; LEAN NOT STARTED |
| L4 | direct gain = fixed gain + correction | HUMAN-PROVED; LEAN NOT STARTED |
| L5 | correction nonnegative | HUMAN-PROVED; LEAN NOT STARTED |
| L6 | `m=1` reduction | HUMAN-PROVED; LEAN NOT STARTED |
| L7 | exact rho scaling | HUMAN-PROVED; LEAN NOT STARTED |
| L8 | derivative identity plus gain bound implies slope condition | HUMAN-PROVED algebra; LEAN NOT STARTED |

The existing generic analytic interface remains in
`rebaseguard-lean/RebaseguardLean/IntegralBridge.lean` and its stronger
Gaussian CUSUM specialization in `ReBaseGuardIdentity.lean`. Reusing it for
the random-window statistic would still require a truthful Lean representation
of `A_m^D` and explicit measurability/integrability hypotheses or their
discharge. Track 1A makes no claim that this instantiation has been checked.

There is consequently no theorem-specific axiom output to print. The absence
of a Track 1A axiom is not a substitute for a compiled proof.

