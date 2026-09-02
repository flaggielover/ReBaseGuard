# P5X — Global Nonlinear Dynamics Closure

**A successor research campaign, not a P5 repair.**

```text
CAMPAIGN            = P5X — Global Nonlinear Dynamics Closure
PHASE               = FEASIBILITY COMPLETE -> CHECKPOINT A (pre-result anchor)
P5_ORIGINAL_VERDICT = PARTIAL          (immutable, bb03c0e, never rewritten here)
P5X_FEASIBILITY     = P5X_THEOREM_PATH_FOUND
LEVEL4_GLOBAL_CLOSURE = NO             (no P5X result exists yet)
NOVELTY_STATUS      = NOT_ESTABLISHED
```

## Why this namespace exists

Original P5 (`../p5_nonlinear_dynamics/`) proved the exact identities `P5-T1`,
`P5-T2/T3`, the uniform stopping and moment bounds `P5-T4/T5`, the invariant-law
theorem `P5-T7` and the stationary ACF identity `P5-T11`. It did **not** prove
the global nonlinear statements its own skeleton results were conditioned on:
the hypotheses `H2` (`R < 0` on `e > 0`), `H3a` (secant monotonicity) and `H3b`
(`sup_e |R| < 2`). Its adjudicated gates `G3`, `G7` and `G9` fail literally for
exactly that reason, and the final-disposition audit
(`../p5_final_disposition_audit/`) ruled `P5_PARTIAL_SHOULD_BE_FINAL` and
recorded the missing work as **new science belonging to a new priority**.

P5X is that new priority. It does not re-ask P5's question, does not re-run
P5's gates, does not weaken them, and does not reinterpret any P5 negative
result. It asks a different question:

> Is there a rigorous **global** mechanism theorem for the frozen ReBaseGuard
> recursion connecting local repulsion at the origin to a bounded, genuinely
> nonlinear, high-dispersion stationary regime — without using finite-grid
> Monte Carlo as the theorem?

## Feasibility answer

`P5X_THEOREM_PATH_FOUND`. The decisive finding is a new exact reduction
(`P5X-T1`, `FROZEN_THEOREM.md` §2): for **every** window `m >= 1` and **every**
entering error `e`, the selection map `R_{D,m}(e)` and its second moment are
determined by *two-dimensional* Fredholm objects on the compact pre-alarm
detector-state square — the same objects the repository already certifies in
Arb for `Gamma` at `e = 0`, `m = 1`. There is no dimension blow-up in `m` and
none in `e`. A floating-point probe of the reduction
(`feasibility/`) reproduces P5's independently measured `R_{D,m}(e)` and
`S_{D,1}(e)` in both detectors, all four windows, across `|e| in [0.005, 12]`.

That converts P5's open hypotheses from *unproved global statements* into
*certifiable finite covers*, and it makes the honest mechanism theorem —
saturation and forgetting, not restoring drift — reachable.

## Document map

| file | content |
|---|---|
| `FEASIBILITY_AUDIT.md` | reconstruction of what P5/P3/P7/P9R prove, the exact global gap, the local-to-global analysis, and the twenty-point feasibility report |
| `THEOREM_CANDIDATES.md` | the Level A–E hierarchy, what is provable at each level, and the strongest realistic target |
| `FAILURE_ANALYSIS.md` | routes that are dead, and why; what P5X will **not** prove |
| `FROZEN_THEOREM.md` | the exact statements frozen before any production result |
| `FROZEN_SCOPE.md` | detector / window / `rho` / `e` scope, frozen |
| `PROOF_OBLIGATIONS.md` | lemma dependency graph and per-lemma discharge route |
| `CERTIFICATE_PLAN.md` | the Arb/interval design, the finite certified cover, budgets |
| `LEAN_PLAN.md` | what the Lean spine formalises, and what it deliberately does not |
| `EMPIRICAL_PLAN.md` | the support role of simulation, and its firewall |
| `FROZEN_GATES.md` | `G1`–`G13`, frozen before production |
| `LIMITATIONS.md` | scope boundaries and known risks |
| `TEMPORAL_ANCHOR.md` | the Checkpoint A anchor and what it does/does not contain |
| `CODEX_HANDOFF.md` | the production instruction set |
| `feasibility/` | the non-authoritative probe that produced the feasibility verdict |

## What this namespace must never do

* mutate `../p5_nonlinear_dynamics/` or any `P1`–`P9`, `P8R`, `P9R` namespace;
* restate `P5-T7` or any other P5 theorem as new work;
* relabel original P5 as `CLOSED`;
* promote a numerical enclosure to `EXACT_THEOREM`, or a Monte Carlo estimate
  to a certificate.
