# P4Z Phases 17–18 — independent correspondence, and what to certify

## 1. Phase 17 — the independent cross-check

Both official routes share one thing: the analytic triple `(f, F, Mlow)` and
the conditional-expectation construction.  A cross-check that shared it would
check nothing.  The diagnostic method is therefore chosen to share neither.

```text
METHOD    Route Q, the frozen deterministic quadrature already in
          p4_theory_generalization/numerics and src/.../quadrature.py
ROLE      INDEPENDENT_CROSS_CHECK_ONLY
STATUS    diagnostic.  It may not arbitrate a cell, may not rescue a gate,
          and may not serve as a control variate.
```

Route Q evaluates the memoryless detector `tau = inf{t : |Z_t| >= c}` at
`c = 2.0`, where `Gamma` is available in closed form.  It uses no Monte Carlo
at all — deterministic quadrature against an analytic identity — so its failure
mode (quadrature error, closed-form algebra) is disjoint from both official
routes' (Monte Carlo variance, finite-difference truncation).

P4X ran it at 24 rows with worst relative discrepancy `4.331e-09` against a
tolerance of `1e-6`, and recorded `arbitrated_any_cell = False`,
`rescued_any_gate = False`.  P4Z inherits that role verbatim, including the
constraint from P4's own `EVIDENCE_BOUNDARY.md` §3 that **nothing in Route Q is
evidence about `h = 5` or `A = 520.886133602749`**.

**What P4Z adds.**  Route Q is extended to the RB construction on the
memoryless detector only, where the survival interval is the fixed `(-c, c)`
and `h_n` is a constant.  There `Gamma` under RB has a closed form that can be
compared against the existing analytic value at the `1e-6` tolerance.  This
tests the RB algebra itself against a known answer, on a detector where the
answer is known — which is precisely the gap a shared-TCB cross-check would
leave.  It buys no evidence about a frozen operating point and is not permitted
to.

**Second diagnostic, zero compute.**  Corollary G2's exact constants
(`J0=1, J1=0, J2=1, J3=0` giving `Gamma = 1` for every family and every `m`)
are checked algebraically by `whole_line_integrals()` and its test.  Any sign,
normalisation or window error breaks it.  This is the campaign's cheapest and
strongest implementation control and it costs nothing.

## 2. Phase 18 — formal and certified connection

The question is what is *load bearing* and *not already covered*.  The answer
is narrow, and deliberately so.

### 2.1 Already covered — reuse, do not re-formalise

| object | existing artifact | P4Z action |
|---|---|---|
| differentiation under the stopped expectation (Level C spine) | `lean/GeneralLocationFamilyP4.lean`, `hasDerivAt_stoppedMean`, 19 declarations, axioms exactly `propext`, `Classical.choice`, `Quot.sound` | re-verify, add nothing |
| closed-form Laplace instance, moving-support counterexample, finite-support general-score witness | `certificates/certificate.json`, Arb at 160 bits, re-verified at 256 by P4X | re-verify, add nothing |
| the two integration-by-parts identities `E[psi]=0`, `E[eps psi]=1` | `THEOREM.md` §5(b), proved | reuse |

P4X's obligation C6 froze `NEW LEAN DECLARATIONS = NOT PERMITTED` and
`NEW ARB OBJECTS = NOT PERMITTED`.  That freeze applies to the *inherited*
artifacts and P4Z does not touch them.

### 2.2 The one thing worth certifying

The RB construction rests on exactly two new mathematical statements, and only
one of them is a candidate for formalisation:

**(i) The bounded-survival lemma.**  For the frozen CUSUM and SR, the set of
residuals that do not alarm is an interval `(L, U)` with `|L|, |U| <= c_D`,
`c_D = h+k` and `1/2 + log A` respectively.

This is a *finite, elementary, decidable* statement about two explicit
recursions with an inclusive boundary.  It is the smallest possible Lean target
that is genuinely load bearing: every moment claim in P4Z follows from it plus
discharge lemma L1, which is already proved.  It needs no measure theory, no
stopping-time machinery and no new axiom.

**Recommendation: formalise (i) in Lean, as a lemma about the two frozen
recursions, in a P4Z-local file that adds no declaration to the inherited P4
Lean namespace.**  Estimated size: two lemmas and a corollary.

**(ii) The RB identity itself**, `Gamma = sum_n E[1{tau>=n} h_n]`.

This is the tower property applied termwise to a sum that G1a already licenses.
Formalising it would require re-formalising the stopped-expectation apparatus
that Level C already carries, for a statement whose mathematical content is a
single application of a standard identity.  **Recommendation: do not
formalise.**  It is checked instead by the two zero-compute controls — the
Corollary-G2 algebraic identity and the Route-Q closed form — and by the
path-by-path equivalence test against the frozen `Detector.step`.

### 2.3 Arb

No new Arb object is warranted.  The gate is a frequentist two-route agreement,
not a deterministic enclosure, and `configs/estimand_contract.json` records
`deterministic_enclosure_required: false`.  Extending interval certification to
a frozen operating point would push past P4's own evidence boundary, which
states that every frozen CUSUM and SR gain in the line is a Monte Carlo
estimate.  P4Z does not move that boundary.

The one place interval arithmetic *would* pay is the outward rounding of the
Richardson truncation bound `T_B` (`CAMPAIGN_GOVERNANCE.md` §4).  That is a
scalar rounding operation, not an Arb object, and directed rounding in double
precision is sufficient.

### 2.4 Summary

```text
FORMALISE       the bounded-survival lemma, Lean, P4Z-local, ~3 declarations
DO NOT FORMALISE the RB identity (tower property; controlled instead)
NEW ARB OBJECTS none
RE-VERIFY       the inherited 19 Lean declarations and 3 Arb objects, unchanged
```
