# Track 3A/3B proof obligations

## Human-proved analytic layer

The concrete infinite t3 CUSUM process remains justified at the human layer by
the historical Track-3 argument.  Its load-bearing obligations are:

1. the detector/stopping rule and terminal observation are fixed measurable
   functionals of the residual path while `e` changes only the path law;
2. the translated t3 family has positive density on common support and a
   differentiable finite-prefix likelihood;
3. the stopping time is almost surely finite;
4. stopped event slices are absolutely summable;
5. `Z_tau` and `Z_tau sum psi(Z_t)` are integrable; and
6. a stopped likelihood difference quotient admits an integrable dominator.

For unit-variance t3, `psi(z)=4z/(1+z^2)` is bounded.  A uniform one-step
forcing probability for the two-sided CUSUM yields a geometric stopping tail;
combined with the finite moments required of t3, this supplies the historical
human route to the stopped domination and integrability conditions.

## Lean-checked layer if authorized

Lean will formalize only the reusable conditional spine:

- an abstract stopped-score derivative bridge exposed as an explicit
  hypothesis;
- score-sign and stopped-sum algebra;
- exact rho scaling;
- reflection and oddness consequences under explicit assumptions;
- Gaussian score specialization;
- local-instability inequalities; and
- the distinction between raw terminal gain and terminal-score-only gain.

The Lean result must be described as a conditional formal proof spine over
explicit analytic hypotheses.  It is not an end-to-end formalization of the
concrete infinite t3 process unless all obligations above are actually
instantiated in Lean.

## Gate

Track-3B work is forbidden until the new decision says exactly:

```text
T3A-NUMERICAL-PASS
NUMERICAL GATE CLOSED — LEAN AUTHORIZED
```

No Arb work belongs to this campaign.
