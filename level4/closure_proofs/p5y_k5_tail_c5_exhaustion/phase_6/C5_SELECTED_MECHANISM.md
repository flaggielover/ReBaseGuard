# Phase 6 — the selected mechanism, and why this one

## Theorem C5-T (exact-weight, sign-aware transport)

Let a K1 cell be `[x_lo, x_hi] = [e0 − rho, e0 + rho]` with **`x_lo > 0`**. Let `g(e) = R(e) − e R'(e)`, so that
`g'(e) = −e R''(e)`. Suppose

* **(i)** `g(e0) ≤ g_hi` — certified at the midpoint, and
* **(ii)** `H_lo ≤ R''(e) ≤ H_hi` for every `e` in the cell — certified on the whole cell.

Then for every `e` in the cell

    g(e)  ≤  g_hi + P,     P := max( (−H_lo)⁺ · w_R ,  (H_hi)⁺ · w_L ),
    w_R := rho·(x_hi − rho/2),        w_L := rho·(x_lo + rho/2).

**Proof.** `g` is absolutely continuous with `g'(t) = −t R''(t)`. For `e ≥ e0`,

    g(e) − g(e0) = −∫_{e0}^{e} t R''(t) dt ≤ ∫_{e0}^{e} t (−R''(t))⁺ dt ≤ (−H_lo)⁺ ∫_{e0}^{e0+rho} t dt,

where `t > 0` on the cell — this is the only place `x_lo > 0` is used, and the module refuses a cell without it.
The integral is `((e0+rho)² − e0²)/2 = rho·(e0 + rho/2) = rho·(x_hi − rho/2) = w_R`. For `e ≤ e0`,

    g(e) − g(e0) = ∫_{e}^{e0} t R''(t) dt ≤ (H_hi)⁺ ∫_{e0−rho}^{e0} t dt = (H_hi)⁺ · rho·(e0 − rho/2),

and `e0 − rho/2 = x_lo + rho/2 = w_L`. Taking the larger gives `P`. ∎

**C5-T is never worse than the frozen clause.** With `M = max(|H_lo|, |H_hi|)`,
`P ≤ M·max(w_R, w_L) = M·w_R = M·rho·(x_hi − rho/2) < M·rho·x_hi`, the frozen penalty, because `rho > 0`. The
producer asserts `P ≤ frozen` at every evaluation and raises if it is ever violated.

**Where the two gains come from, separately.** The *exact-weight* gain is the factor `(x_hi − rho/2)/x_hi`: the
frozen clause bounds `|t|` by `x_hi` over the whole integration range, whereas `|t| ≤ x_hi` only at the right-hand
endpoint. The *sign-aware* gain is strict only when the **positive** end of the `R''` enclosure dominates in
magnitude, because `max(|H_lo|, |H_hi|) ≡ max((H_hi)⁺, (−H_lo)⁺)` identically — sign-awareness buys nothing on its
own and pays only against *different directional weights*. On all four K5 tail cells the negative end dominates
and the binding direction is rightward, so there the gain is the exact-weight factor alone.

## Why this route was selected

Against the frozen gate's criteria, in order:

1. **Soundness** — proved above and independently re-verified by direct exact-rational maximisation over the cell
   (`code/c5_mutations.py`, part 1), which also confirms the bound is *attained*.
2. **Does it affect the load-bearing blocker?** It attacks the transport constant, the only ingredient of
   `Gamma = g_hi + rho·x_hi·M` other than `M` that is not sealed record or cover geometry.
3. **Certified scope** — whole-cell, from two already-certified inputs.
4. **Independence** — it consumes no registry constant, no candidate polynomial, no Arb certificate and no atom
   constant. It is independent of every surface C2, C3 and C4 argued about.
5. **Closure or exhaustion value** — it closes nothing, and it carries a constructive exhaustion result.
6. **Robustness** — exact rationals throughout; no float reaches a load-bearing comparison.
7/8. **Complexity and runtime** — a dozen lines and milliseconds.

It was selected because it is **the only route in the ledger with every input already certified**. That is not a
recommendation of its power; routes B1 (cover refinement) and E1 (operator certification of `A0`) are far more
powerful and are blocked on permissions and on a missing toolchain, not on mathematics.

## What C5-T does not do

It does not close a cell, it does not improve `g_hi`, it does not improve the `R''` enclosure, and it does not
touch the order-3 surrogate or `rho`. It corrects one inequality, by 1.2–1.3 %.

## No-regression invariant

Across all five tail cells and all four `m` values — twenty rows — `Gamma_C5T ≤ Gamma_frozen` holds with **zero**
exceptions, and no row that closes under the frozen clause fails to close under C5-T. This is structural, not
fortunate: the producer refuses any evaluation in which `P` exceeds the frozen penalty.
