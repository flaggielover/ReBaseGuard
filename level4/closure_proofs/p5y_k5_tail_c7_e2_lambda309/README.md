# C7 — E2 analytic lower-bound strengthening for Λ_309

**Class: STRENGTHENED.** Guard **DENY**, `EXECUTION_AUTHORIZED` **false**, **0** new-real addresses,
**0** scientific kernel evaluations, **0** remote hosts contacted, **0** toolchain provisioned.
Arithmetic: python3 `fractions.Fraction` only, outward rounding on a `2^-320` grid.

## The result

Four certified lower bounds on `Λ_309 = E_a[τ]` (frozen CUSUM, m = 5, cell 309), separated by what
each one depends on:

| bound | value | vs C4 | margin over the C5-T critical A0 | depends on |
|---|---|---|---|---|
| L1 tier-1 | 3.461283497 | +4.9748 % | 5.9658 % | — |
| **L3 elementary** | **3.586306094** | **+8.7666 %** | **9.7933 %** | **— (PRIMARY)** |
| L3 registry | 3.597941639 | +9.1195 % | 10.1495 % | Arb/FLINT surface |
| L3 Lorden | 3.600337620 | +9.1921 % | 10.2229 % | Lorden (1970), cited |

C4 published a margin of **2.5827 %**, measured against its own frozen-clause critical A0
`3.2142360226778806`. C5-T's exact-weight transport then raised the critical A0 to `3.266415728`,
consuming 63 % of that margin and leaving C4's floor `3.297250282` clearing it by only **0.9440 %**.
A second successor move of C5-T's size would have extinguished the exclusion.

The PRIMARY bound clears the same critical A0 by **9.7933 %** — **10.37×** what was left of C4's
margin — and the **bound** does so without depending on the Arb/FLINT certification surface at all.

One thing that independence does *not* buy, and an earlier draft of this file overclaimed: the
**margin statement** is not surface-free. It is measured against `critical_A0_C5T`, itself an
operator-level quantity read from C5's forecast. If that surface were doubted entirely, the *bound*
would survive intact and the *comparison target* would be gone. What C7 establishes is that the
exclusion no longer depends on the Arb/FLINT surface for its **margin**, not that it could be stated
without that surface at all.

## What this is not

Cell 309 is **not closed**. The exclusion is a statement about the deterministic operator-level
route, not a closure. K5 remains **PARTIAL**, m = 5 open on [305, 309]. No other cell's status
changes. The guard stays DENY and the R-stage is not authorised.

## The mathematics

**Theorem C7-E2.** C4 proves `E_a[τ] ≥ H/E[V]` via a pathwise majorant and Wald, discarding the
overshoot `R = S_τ′ − H`. Wald is an identity, `E[τ′]E[V] = H + E[R]`, so recovering `E[R]` converts
directly into the bound:

    E_a[τ]  ≥  (H + E[R]) / E[V],    E[R] = ∫ ψ dμ,  μ a probability measure on [0, H],

with `ψ(u) = E[(V−u)⁺]/P(V>u)` the mean residual life of `V = (|z|−K)⁺`. Tier 1 bounds `E[R]` below by
`inf ψ`, using only two monotonicity facts, both proved on all of ℝ: the Gaussian mean residual life
`r(t) = φ(t)/Φ(−t) − t` is decreasing (log-concavity), and the reflected tail ratio
`f(s) = Φ(−(s+e))/Φ(−(s−e))` is decreasing, since `d/ds log f = h(s−e) − h(s+e) < 0`.

**Theorem C7-E2c (multi-tier).** Splitting `[0,H]` at a partition turns the problem into a small LP:
`ψ ≥ ψ_lo(u_j)` on each subinterval, and `μ((u_i,H]) ≤ p(u_i)·E[τ′] ≤ p(u_i)·U`. Because `ψ_lo` is
non-increasing the LP solves greedily in closed form, pushing mass rightward, and the weights
telescope to exactly 1. Refining the partition adds constraints and can only raise the bound.

**Lemma C7-U.** The multi-tier theorem needs `U ≥ E[τ′]`. Taking it from a certified admissible `A0`
would tie the answer to the very surface C7 exists to be independent of, and Lorden's inequality is an
external theorem C7 does not re-prove. So C7 proves its own: `R ≤ V_τ′ ≤ a + V_τ′1{V_τ′>a}`, the second
term factorises as `E[τ′]g(a)` because `{τ′ ≥ n} = {S_{n−1} ≤ H}` is independent of `V_n`, and Wald
closes the recursion. Step 0 certifies `E[τ′] < ∞` by explicit geometric domination — which tiers 2+
need in any case and which was previously implicit.

This lemma is why the PRIMARY bound has an empty dependency set.

## Two structural holes, found and closed before the final evaluation

**U had no provenance.** The bound is monotone decreasing in `U`, so understating `U` inflates it
unsoundly. `U = 0.1` — false by a factor of ~47 — returned `Λ_309 ≥ 4.175`: well-ordered,
LP-consistent, and still *below* the certified `A0`, so even the kill gate comparing a lower bound
against a certified upper bound did not fire. Same species as C5's negate-and-swap. `U` now arrives as
a certificate that is re-derived from its declared source; and because re-derivation cannot catch a
mutation of a derivation itself, an independent floor `E[τ′] ≥ H/E[V]` is enforced too. That floor
evaluates to 3.297250281519544 — exactly C4's published bound, reached by a different route.

**Evaluating ψ at the wrong endpoint.** This inflated the bound by 0.96 % and *nothing* caught it:
weights still summed to 1, `ψ_lo` was still non-increasing, the result still sat below every certified
upper bound. Nothing was inconsistent; it was simply wrong — the C4 failure mode exactly. `ψ` is now
recomputed independently from its own definition and every `ψ_lo` the LP consumes is checked against
it. `psi_exact` is used **only** as a guard, never as the bound. An earlier draft justified that by
saying `ψ`'s monotonicity is "genuinely unclear". That was too weak, and both the pre-publication
review and an independent numerical check corrected it: **`ψ` is decreasing.** The exact criterion is
`ψ′(u) < 0 ⟺ ψ(u)·h(s) < 1`, which holds at all 65 knots with worst value 0.943443 at `u = H`; and
log-concavity of the folded-normal density proves it outright for `u ≥ arccosh(e)/e − K = 0.159112`,
i.e. on 96.8 % of the range, leaving exactly two of the 64 knots to the criterion.

It is still not used, for a quantified reason rather than an uncertain one: substituting `ψ_exact`
raises `E[R]` by 0.6978 % but only **+0.0562 %** on the reported bound, because `E[R]` is just 0.44
of the `H + E[R] = 5.44` being divided. See `evidence/psi_monotonicity/` and
`OPEN_NOTES_DISPOSITION_C7.md` → N1.

A third defect, the `k = 1` edge case, was surfaced by kill gate KG4 rather than by inspection.

**Two more, found by the fresh-context review, which returned NOT_READY.** The first repair above was
incomplete in a way the campaign did not see. The review obtained a dependency-free,
re-derivation-surviving, kill-gate-clean bound of **3.619819606** (+0.9345 % over PRIMARY) from
`U = 3.549353697` — **without mutating any code**, using only the public API — because Lemma C7-U's
own hypothesis `a > 0` was never enforced and `_resolve_U` re-derived `U` from the grid carried *in
the certificate under test* rather than the gate's frozen one. Provenance constrained `source`, the
field the mutants exercised, and never the field carrying the payload. Separately, nothing enforced
that the evaluation point `e` lies in the closed cell: `e = 1.90` gives 3.642963840, above PRIMARY,
firing nothing. Both are now enforced in code and regression-tested (M16, M17, M18), and both
falsified a claim the frozen gate made about itself — see `ERRATUM_C7_GATE.md` E1 and E2. Neither
affected the published numbers, which were always computed on the gate's own grid at `e = e_lo`.

## Exhaustion of the family

The E2 family's analytic ceiling is **4.679910340** — what it yields if `E[R]` were known exactly at
its largest provable value. That is **below** the certified `A0 = 4.867216117`, so no choice of
partition, split points or `U` can make this family reach the operator constant. It does not need to:
the exclusion test is against the critical `A0`, which it clears by 9.79 %. Remaining headroom inside
the family is ~30 %, obtainable only by sharpening `E[R]` toward its true value.

Going further needs what C7 cannot have: a bound on `E[τ] − E[τ′]` (the clipping majorant), or the
gap between `sup` over the cell and the value at `e_lo`. Both need operator information. Both point
the **favourable** way — `τ ≥ τ′` pathwise — so the true `Λ_309` can only exceed what C7 reports.

## Disclosure

The gate was frozen **after** exploratory evaluation and does not claim blindness. What makes that
sound is structural: every prospective choice — partition, `a`-grid, split points, the point `e`, the
choice of `U` — affects only the **tightness** of a bound, never its **validity**, and the verdict
rule contains **no tuned threshold**, only strict comparisons against C4's own published numbers.
`ROBUST_5`/`ROBUST_10` are descriptive bands, explicitly not verdict inputs.

## Layout

    config/FEASIBILITY_GATES_C7.json   frozen gate, sha256 9f7083b9…, KG1–KG9 (see erratum E8)
    code/c7_gaussian.py                rigorous rational Φ, φ, π, √ (imports `fractions` and nothing else)
    code/c7_theorem.py                 Theorems C7-E2, C7-E2c; Lemma C7-U; U provenance; ψ guard
    code/c7_common.py                  committed-fact readers, canonical JSON
    code/c7_b0_audit.py                17-check state audit (AST import walk, all modules)
    code/c7_ledger.py                  phases 1–2: slack ledger, required improvement
    code/c7_mutations.py               phase 7: 20 mutants, interface vs source
    code/c7_certificate.py             phases 9–11: evaluation, downstream, exhaustion
    code/c7_factcheck.py               phase 13: governance fact verification
    code/c7_primitives_test.py         known-value tests for G.Phi / G.phi
    code/c7_psi_monotonicity.py        the psi monotonicity analysis behind N1
    phase_3/C7_ROUTE_SEARCH.md         families A–I and why eight were stopped
    ERRATUM_C7_GATE.md                 E1–E9: corrections to the frozen gate's own statements
    OPEN_NOTES_DISPOSITION_C7.md       N1–N7
    review/REVIEW_C7_PREPUBLICATION.md the NOT_READY review, 17 findings
    review/ADJUDICATION_C7.md          ACCEPTED_WITH_CONDITIONS, 9 further defects
