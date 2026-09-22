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

C4's floor was 3.297250282, clearing the C5-T critical A0 `3.266415728` by **0.9440 %**. The PRIMARY
bound clears it by **9.7933 %** — **10.37×** C4's margin — and does so **without depending on the
Arb/FLINT certification surface at all**.

That independence is the point. C4's exclusion of cell 309 tolerated a 0.94 % adverse move in the
critical A0, and a single successor — C5-T's exact-weight transport — had already consumed 63 % of
C4's original margin. A second move of that size would have extinguished the exclusion. It no longer
can, and that conclusion survives even if the operator certification surface is doubted entirely.

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
it. `psi_exact` is used **only** as a guard, never as the bound, because using it directly would
require `ψ` to be decreasing, which is *not* proved: the weights in its mixture shift toward the
larger term as `u` grows, so the monotonicity is genuinely unclear rather than merely unproved.

A third defect, the `k = 1` edge case, was surfaced by kill gate KG4 rather than by inspection.

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

    config/FEASIBILITY_GATES_C7.json   frozen gate, sha256 9f7083b9…, 9 kill gates
    code/c7_gaussian.py                rigorous rational Φ, φ, π, √ (imports `fractions` and nothing else)
    code/c7_theorem.py                 Theorems C7-E2, C7-E2c; Lemma C7-U; U provenance; ψ guard
    code/c7_common.py                  committed-fact readers, canonical JSON
    code/c7_b0_audit.py                16-check state audit (AST import walk)
    code/c7_ledger.py                  phases 1–2: slack ledger, required improvement
    code/c7_mutations.py               phase 7: 15 mutants, direction-organised
    code/c7_certificate.py             phases 9–11: evaluation, downstream, exhaustion
    phase_3/C7_ROUTE_SEARCH.md         families A–I and why eight were stopped
