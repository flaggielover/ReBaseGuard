# C7 Phase 3 — broad route search, families A–I

The question C7 was given is narrow: strengthen the certified lower bound on
`Λ_309 = E_a[τ]` using only committed evidence and deterministic analytic reasoning. Nine families
were considered before one was selected. A family is STOPPED the moment it requires a numerical
scientific oracle — the campaign's compute boundary forbids weakening that rule to rescue a route.

| family | idea | verdict |
|---|---|---|
| **A** | **overshoot correction to `H/E[V]`** | **SELECTED** |
| B | recover the clipping majorant, i.e. bound `E[τ] − E[τ′]` | STOP |
| C | replace the single-point evaluation by the true `sup` over the cell | STOP |
| D | moment / concentration bounds on `τ` | PURSUED, DOMINATED |
| E | solve the renewal equation for `E[τ′]` exactly | STOP |
| F | sharpen the pathwise majorant using the clipping frequency | STOP |
| G | optional stopping on the exponential (Wald) martingale | PURSUED, DOMINATED |
| H | Kac / atom-return formula | STOP |
| I | information-theoretic ARL lower bounds | STOP |

## A — overshoot correction (SELECTED)

C4 proves `E_a[τ] ≥ H/E[V]` by a pathwise majorant plus Wald, discarding the overshoot
`R = S_τ′ − H ≥ 0`. Since Wald gives `E[τ′]·E[V] = H + E[R]` exactly, every unit of certified `E[R]`
converts directly into the bound. `E[R]` is expressible through the mean residual life of the
increment law alone, which is a Gaussian computation C7 can do rigorously in exact rational
arithmetic. Nothing here touches the operator, the kernel, or any registry.

This is the only family that is simultaneously (i) inside the compute boundary, (ii) attacking a term
C4 provably discarded rather than one it bounded loosely, and (iii) independent of the disputed
Arb/FLINT surface.

## B, C, F, H — stopped on the compute boundary

All four require information C7 cannot obtain analytically:

- **B** needs the frequency with which the clipped CUSUM statistic is pinned at 0, which is a property
  of the recursion, not of the increment law.
- **C** needs `sup` over the closed cell, which is operator information.
- **F** needs the same clipping law as B.
- **H** needs the stationary distribution at the atom.

Each would need a kernel evaluation or new operator certification. Both are forbidden. Recorded as
STOPPED rather than attempted-and-failed: no work was done inside them beyond establishing the
dependency.

Note that **B and F point the favourable way.** `τ ≥ τ′` pathwise, so the discarded quantity is
non-negative and the true `Λ_309` can only exceed what C7 reports. C7's bound is not merely valid —
it is valid with a known-signed unexploited reserve.

## D — moment and concentration bounds (pursued, dominated)

A lower bound on `E[τ]` can be extracted from concentration of `S_n`: if `P(S_n > H)` is small for
`n ≤ n₀` then `E[τ] ≳ n₀`. With `E[V] = 1.5164` and `H = 5`, the walk crosses in about 3.3 steps on
average, so `n₀` is small and the Chernoff slack at such small `n` is large. Every variant tried gave
a bound below C4's existing floor, i.e. below 3.2973. Dominated by family A and dropped.

## G — exponential martingale (pursued, dominated)

`M_n = exp(θ S_n − n·κ(θ))` is a martingale for the cumulant generating function `κ`. Optional
stopping at `τ′` relates `E[e^{θ(H+R)}]` to `E[e^{τ′κ(θ)}]`. To turn this into a LOWER bound on
`E[τ′]` one needs an UPPER bound on the exponential moment of the overshoot, `E[e^{θR}]`. That is
strictly harder than the first-moment bound family A already supplies — the same mean-residual-life
machinery, but applied to a heavier functional, so every rounding loss is amplified. The route is
sound but yields less than A for more work. Dropped as dominated, not as impossible.

## E, I — stopped

**E** is the exact answer and is precisely what the programme cannot afford: solving the renewal
equation for `E[τ′]` is an integral-equation solve, i.e. a numerical scientific oracle.

**I** (Lorden-style information-theoretic ARL bounds) are asymptotic in the threshold and are
statements about the class of detectors at a given false-alarm rate. They do not produce a
finite-`H` certified lower bound for this fixed frozen model, and adapting them would require
assumptions C7 is not entitled to make.

## What the search actually settled

Family A was not selected because it looked promising; it was selected because it is the only family
that attacks a **provably discarded** term using **only the increment law**. Families B, C, F and H
all fail for the same reason — they need the operator — and that common cause is itself the finding:
inside C7's boundary, the increment law is the entire available surface, and the overshoot is the only
thing C4 left on the table that the increment law alone can recover.
