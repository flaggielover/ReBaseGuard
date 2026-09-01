# Method-novelty separation

A prescriptive campaign can be "new" in four different ways, and they are worth
very different amounts. Recording the distinction now prevents the common
failure of relabelling a lookup table as a method.

```text
NOVELTY = NOT_ADJUDICATED    (see NOVELTY_AUDIT_PLAN.md)
```

---

## 1. Four kinds of novelty

| kind | definition | how it is demonstrated | how it fails |
|---|---|---|---|
| **algorithmic** | a policy mechanism not previously used for this control problem | a precise statement of the mechanism plus a prior-art audit across all seven dimensions of `NOVELTY_AUDIT_PLAN.md` §2 | the mechanism is standard elsewhere and merely re-applied — usually L3, L9 or L13 |
| **theoretical** | a statement about the controlled system that was not previously available | a theorem with its hypotheses discharged, at a stated evidence rank | the "theorem" is an algebraic rearrangement of a known identity |
| **operational** | a demonstrated improvement on a metric that matters, under conditions someone could deploy | measured, uncertainty-aware, reproduced on both detectors and an independent seed family | the improvement is against a straw-man baseline (`B3`), or at unmatched cost |
| **integration** | connecting previously separate results into a usable whole | the connection is exhibited and shown to be non-obvious | the connection is a summary |

**Integration novelty is real but weak.** It is very likely what P6 will have at
minimum, and it should be claimed as exactly that: modest, and honest.

## 2. The bar for a P6 contribution

A P6 method should possess **at least one** of the following. Each is stated
with what would *count* and what would not.

| # | criterion | counts | does not count |
|---|---|---|---|
| N1 | **principled risk-control derivation** | the policy is derived from the frozen model's own conditional law (e.g. `P6_THEORY_TARGETS.md` §7's inverse-variance rule), and the derivation predicts behaviour that is then confirmed | a functional form chosen because it fit the screening data |
| N2 | **theorem-backed safety guarantee** | `T6-D`: an enforceable bound `P(|e_{j+1}| > c | Fcal_j) <= B` computable from observables | a bound so loose it is never binding at the `c ~ 0.16` scale that matters (`T6-D` route 1 is at real risk of this) |
| N3 | **new state-dependent reuse mechanism** | the increment-observability + stopping-time-likelihood filter of `OBSERVABILITY_AUDIT.md` §4, *if* the audit finds no prior art (queries 6/7/18) | thresholding a single observable — that is `B6`, a baseline |
| N4 | **new constrained optimisation formulation** | the delay-tail-constrained maximum-reuse problem with an explicit fresh-sample cost model (`OPTIMIZATION_FORMULATIONS.md` B + `H5`), if formulating it that way is genuinely absent from L2/L4/L9 | restating a known problem with different symbols |
| N5 | **new measurable proxy with demonstrated operational benefit** | the `-GammaTilde` high-gain sensor reading of `zbar` (`OBSERVABILITY_AUDIT.md` §3.1) *combined with* a measured improvement it causes | a proxy that correlates with the latent state but changes no decision |

## 3. What is explicitly **not** a contribution

* A **lookup table** from `(D, m)` to a recommended `rho`. Even a good one. It
  is a calibration, and it belongs in a table, presented as such.
* Reporting P5's `rho*` as a recommendation. Beyond being `PROVISIONAL_P5`
  (`X9`), it is P5's measurement, not P6's method.
* Beating `B3` (full reuse). `B3` is the known-worst case (`S3`, `S5`, `S8`);
  beating it is a *sanity check*, not a result. The bar is the matched-cost best
  fixed `rho` (`B2*`, estimated; `Z5`, the oracle version of the same bar).
* Renaming an EWMA. A fixed-`rho` reuse rule is already close to an EWMA on the
  reference; the relationship must be stated by P6 in §L3 of the audit, not
  discovered by a reviewer.
* An improvement on a surrogate with no measured monitoring effect (`F2`).

## 4. The honest floor

If the audit finds prior art for every mechanism and the frontier shows no
adaptive method beating the matched-cost fixed `rho`, P6's contribution is:

* a precise formulation of the safe re-baselining problem with an explicit cost
  model;
* an observability audit establishing what a deployable policy can and cannot
  see, including the two positive results (`-GammaTilde` sensor gain, increment
  observability) and the one negative one (`H8`: the blind spot has no
  implementable proxy);
* an oracle ceiling quantifying how much adaptive control could ever be worth;
* and a reproduced negative result.

That is a complete campaign and a defensible closure. Stating this in advance is
what stops the search for a positive result from becoming the objective.
