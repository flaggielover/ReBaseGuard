# DRAFT future P4X Checkpoint A — NOT ACTIVE, NOT FROZEN

```text
STATUS       = DRAFT
ACTIVE       = NO       (this document is NOT ACTIVE and binds nothing)
FROZEN       = NOTHING
CREATED      = NO CHECKPOINT
P4_ORIGINAL_VERDICT = PARTIAL   (immutable)
```

This drafts what a P4X Checkpoint A would commit to if the campaign were
opened.  Nothing here is frozen, no anchor commit exists, and no number in it
has been produced by a production run.  It supersedes the estimator and
arbitration parts of `../feasibility_and_scope_audit/DRAFT_SUCCESSOR_SCOPE.md`,
which were written before the R0 measurements existed.

## 1. Exact scientific question

> P4 proved, and independent adjudication accepted, that the closed Gaussian
> reuse-derivative mechanism generalizes to regular one-dimensional location
> families at both frozen detectors for every window `m >= 1`.  Its three failed
> gates were measurement and gate-specification objects, not theorem objects.
>
> **Does a correctly specified numerical correspondence, run at a precision the
> frozen 3 % criterion can actually demand, confirm that theorem across the same
> 96-cell design — and does an independent reimplementation agree with the
> closed Gaussian gains under a correctly specified two-sample statistic?**

P4X does not re-ask P4's theorem question, does not re-run P4's gates, does not
weaken them, and does not reinterpret any P4 negative result.

## 2. Inherited theorem

`G1a`, `G1b`, `G1'`, `G2`, `G3a` (narrowed) and `G4`, verbatim from
`../../p4_theory_generalization/THEOREM.md`, cited by git object
`eede90383da44c250871b1bb97d12045c897c8d9`.  Hypotheses `(A1)-(A7)` unchanged,
discharged for the two frozen detectors by `L1`-`L5` of `PROOF.md` §8.

**P4X proves no new theorem.**

## 3. Numerical correspondence scope

```text
layers    frozen (cusum@5, sr@520.886133602749) and reduced (cusum@2, sr@20)
families  THEOREM-SUPPORTED  gaussian, laplace, logistic, skewnormal4, t1p5, t3
          OUTSIDE-ASSUMPTIONS uniform, cauchy
windows   m in {1, 2, 3, 5}
cells     96 theorem-supported + 32 outside-assumption
routes    A (score), B (Richardson CRN central difference),
          Q (deterministic quadrature, memoryless detector),
          N (deterministic-stopping neutrality control)
```

Identical to P4's design, so the comparison means something.

## 4. Fixed estimator

```text
Route A   the frozen score estimator, unchanged
Route B   the frozen CRN central difference with per-block Richardson,
          h = 0.05 / 0.025, unchanged
variance reduction   NONE ADOPTED
```

All four R0 candidates were measured and rejected: reflection-antithetic
(exact, but a 300-1000x variance increase), the Corollary-G2 control variate
(exactly zero variance, no information), coarse `h` (inadmissibly biased for
`skewnormal4`; unresolved bias for `t1p5`), fine `h` (variance increase).
Evidence: `PILOT_REPORT.md` §6, `results/pilot.json`, `results/bias_checks.json`.

## 5. Fixed precision policy

Frozen from `PRECISION_POLICY.md`, whose full cost table is computable — and was
computed — with no production data.

```text
target relative SE per route  r* = 0.010823, forced by the frozen 0.03 criterion
                                   via 1.96 * sqrt(2) * r* = 0.03
sample-size rule   N = N_ref * (relSE_ref / r*)^(1/kappa)
                   kappa = 0.5 if alpha >= 2, else 1 - 1/alpha
minimum block size 250 000 paths where alpha < 2, else 20 000
measured alpha     t1p5 ~ 1.5 (both routes, all layers/detectors);
                   every other theorem-supported family >= 2.7
```

The frozen 3 % accuracy criterion and the frozen `|z| <= 4` consistency
criterion are **inherited unchanged**.  `r*` is derived from the 3 % criterion,
not a replacement for it.

## 6. Route-Q role

```text
ROUTE_Q_ADMISSIBLE_ROLE = C -- independent cross-check of the identity only
```

Route Q evaluates the memoryless detector, not the frozen CUSUM or SR, so it is
evidence about the identity and never about a frozen operating point.  It may
**not** arbitrate a frozen-cell disagreement and may **not** serve as a control
variate.  The arbitration clause proposed in the earlier draft successor scope
is withdrawn.

## 7. CUT-2 failure-mode semantics

Split by the failure mode the theorem actually proves.

```text
X7a  A3 / moving support -> the identity is FALSE, exact defect 2.
     Discharged by existing exact evidence: PROOF.md section 9 closed form,
     Route Q (score side exactly 0, exact slope -2.366025), and an exact
     rational Arb certificate.  Monte Carlo confirmation is corroborating,
     not load-bearing.

X7b  first moment / Cauchy -> NON-EXISTENCE of the estimand, E|A_1| = infinity.
     Discharged by PROOF.md section 10.  P4X asserts no empirical "failure
     signature" for this half, because a two-route discrepancy statistic
     cannot express non-existence.  An optional divergence diagnostic
     (truncated moment growing in K; standard error not shrinking at n^{-1/2})
     is priced at 0.008 CPU-hours and is explicitly NOT a gate.
```

## 8. Two-sample Gaussian consistency rule

```text
X11  |P4X - closed| / hypot(se_P4X, se_closed) <= 4
     on all eight Gaussian frozen cells, using the closed campaigns' own
     published gamma_tilde_se from the frozen Priority-3 stability map.

     The historical single-error statistic is REPORTED ALONGSIDE and gates
     nothing.  A failure of this test is evidence about Monte Carlo
     realizations and is never a licence to alter a frozen value.
```

This is a new preregistered object, not a repair of P4's gate.  P4's gate
remains failed and untouched.

## 9. CPU cap and stop rule

```text
P4X_PRODUCTION_CPU_CAP = 60 CPU-hours          (recommended, conservative)
PER_CONFIGURATION_ALLOWANCE = 40 CPU-hours

projected: median 1.13 h, conservative 2.91 h, worst case 36.81 h
           + outside-assumption cells, Route N, Route Q, Lean and Arb
             re-verification, estimated <= 4 h
           => worst realistic total ~ 41 h against a 60 h cap

STOP  a (configuration, route) whose projected worst-case cost exceeds the
      per-configuration allowance is declared PRECISION_LIMITED from projected
      cost alone, BEFORE its production estimate exists, and reported as a
      documented limitation.  Never declared after seeing a result.

HARD STOP  60 CPU-hours.  If the design cannot be completed inside it, the
      honest outcome is P4X = PARTIAL with the cost limitation recorded.
      The cap is NEVER raised after a result is seen.

PROHIBITED  any threshold change after a result is seen; any new theorem work;
      any new Lean declaration; any new certificate object; adoption of any
      variance-reduction method R0 rejected; use of Route Q as an arbiter.
```

## 10. Protected-tree rules

* `P4_ORIGINAL_VERDICT = PARTIAL` is immutable and restated in every document.
* `../../p4_theory_generalization/` is byte-frozen: its ten failed cells, its
  sixteen `COUNTEREXAMPLE-NOT-DEMONSTRATED` cells, its three failed gates and
  its `closure_decision.json` are never edited, regenerated or reinterpreted.
* No `P1`-`P9`, `P8R`, `P9R` or `P5X` namespace is modified.
* Every tracked path outside the P4X namespace is byte-identical to `HEAD`,
  recorded pre and post, with untracked namespaces enumerated by digest.
* P4X gates are **new preregistered objects**; P4X never describes itself as
  repairing, correcting or superseding a P4 gate.
* `P5_RESIDUAL_STATUS = DOCUMENTED_LIMITATION`, `LEVEL4_GLOBAL_CLOSURE = NO`
  and `NOVELTY_STATUS = NOT_ESTABLISHED` are restated; a P4X closure implies
  none of them changes.

## 11. Governance caveat — the destroyed historical P4 disposition audit

`level4/closure_proofs/p4_final_disposition_audit/` existed as an untracked
namespace at P5X Checkpoint A with content digest

```text
sha256  bda05c9c5ee5df2a7bfbe11ca1fb07432907378299fd36ea0b75cada68ffba34
```

and was destroyed by an external `git clean` alongside commit `31132e8`.  It
was never committed and is unrecoverable.

**Checkpoint A must record this loss explicitly and derive its own disposition
finding rather than claim to inherit one.**  The governance reading in force —
no retroactive repair of the historical priority, successor campaigns permitted
— is a structural inference from the surviving record (the parallel P5 ruling
quoted in P5X's feasibility audit; P5X opened and completed under it
unopposed; P5X's own disposition audit naming `P4X` explicitly; P4's own
closure report contemplating a follow-up campaign), **not** a quotation of the
P4 ruling.  If a copy hashing to `bda05c9c…` is recovered and forbids a
successor campaign, that ruling takes precedence and P4X must stop.
