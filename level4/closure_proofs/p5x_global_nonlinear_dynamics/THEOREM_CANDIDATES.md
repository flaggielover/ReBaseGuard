# P5X theorem hierarchy — weakest to strongest

Each level is scored on three axes: **is it true?**, **is it provable here?**,
**does it carry the mechanism?** A level that is provable but carries no
mechanism is not worth a campaign; a level that carries the mechanism but is
not provable is not worth a promise.

Notation: `R = R_{D,m}`, `S = S_{D,m}`, `M_2 = sup_e E[Rbar^2 | e]`,
`R_max = sup_e |R|`, `s_min = inf_e S`, `E = 2`, `r_lin ~ 0.05` (P7's
grid-defined linearisation radius), `lambda(rho) = rho(1 - GammaTilde)`.

---

## LEVEL A — global boundedness / drift

**Statement.** There are `R* < infinity` and `eps > 0` with
`sign(e) (E[e_{j+1}|e] - e) <= -eps` for `|e| > R*`; equivalently the
conditional mean map has a compact forward-invariant interval.

**Status.** *Already true, already vacuous.* It follows from `P5-T5` with
`R* = rho sqrt(C_D) <= 3.1e4`. P5's `T12` correctly says a Foster–Lyapunov
programme is unnecessary here, because `P5-T1` gives a *state-independent*
one-step moment bound, which is strictly stronger in form than any outer-drift
inequality.

**P5X verdict.** `PROVABLE — BUT NOT NEW UNLESS THE CONSTANT IS`. P5X states it
only as a corollary of the certified `R_max`, and says plainly that the content
is the constant, not the inequality. Claiming Level A as a result would be
overclaiming.

## LEVEL B — global invariant law with quantitative control

**Statement.** With `pi` the invariant law of `P5-T7`,

```text
rho^2 s_min + (1-rho)^2/m  <=  E_pi[e^2]  <=  rho^2 M_2 + (1-rho)^2/m ,
```

with `s_min > 0` and `M_2 < infinity` certified; and consequently
`RMS_pi >= sqrt(rho^2 s_min + (1-rho)^2/m)`, a **lower** bound on stationary
dispersion.

**Why it is provable.** The middle identity
`E_pi[e^2] = rho^2 E_pi[R^2 + S] + (1-rho)^2/m` is exact (invariance plus
`P5-T2`); everything else is a certified scalar. The certified scalars come
from `P5X-T1`/`T2` plus the Arb layer.

**Why it carries mechanism.** The *lower* bound is the local-to-global bridge:
it forces the stationary law off the scale where `lambda(rho)` means anything.
With the probe's constants, `RMS_pi >= 0.69` at `rho = 1, m = 1` against
`r_lin ~ 0.05`. No hypothesis about branches, cycles or bifurcations is used.

**P5X verdict.** `TARGET — PRIMARY`. Closure probability `0.90`.

## LEVEL C — global sign / shape of the selection map

**Statement.** For each frozen `(D, m)`:
`R(e) < 0` for `e in (0, E]`; `s(e) = -R(e)/e` attains each level `>= 1`
exactly once on `(0, E]`; `sup_e |R| = R_max < E`; and `|R(e)| -> 0`
super-exponentially as `|e| -> infinity` with explicit constants.

**Why it is provable.** A finite certified cover of `[0, e_far]` in
interval-valued `e` (the targets are real-analytic in `e`), plus the exact
far-field lemma `P5X-T3` beyond `e_far`. The sign near `0` comes from a
certified `R' < 0` on `[0, e_0]` together with the *exact* `R(0) = 0` of
`P5-T3`, not from an enclosure of `R` itself (whose width cannot resolve the
sign as `R -> 0`).

**What it buys.** `H1`,`H2`,`H3a`,`H3b` become theorems in the frozen cells, so
P5's `T8`, `T9`, `T10` become unconditional — credited to P5, with P5X
supplying only the discharged hypotheses. P5's literal gate `G3` becomes true.

**Cost.** The `R'` system roughly doubles the certified work and is the reason
`H3a` is the expensive hypothesis.

**P5X verdict.** `TARGET — SECONDARY`. Closure probability `0.75`.

## LEVEL D — flip / branch theorem for the deterministic skeleton

**Statement (scoped).** For `rho in [(1+eta) rho_c, 1]`: `f_rho = rho R` has the
unique fixed point `0`, exactly one symmetric 2-cycle `{+e*, -e*}`, that cycle
is hyperbolic and attracting, there is no asymmetric 2-cycle and no periodic
orbit of period `> 2` in the absorbing interval `[-rho R_max, rho R_max]`, and
every orbit from `R \ {0}` converges to it.

**Why it might be provable.** Given certified `R` and `R'` on a fine cover of a
compact absorbing interval, this is rigorous interval global dynamics of a
one-dimensional map — standard technology, run over a certified cover of `rho`.

**Why it is at risk.** (i) At `rho = rho_c` the multiplier is exactly `1`, so
hyperbolicity is uncertifiable in a neighbourhood; a supercritical
classification there needs a flip nondegeneracy coefficient, which for an odd
`R` is governed by `R'''(0)` and requires a third-derivative system. (ii)
Global convergence from *every* initial condition requires excluding all
higher-period orbits, i.e. a genuine cover of the square
`[-rho R_max, rho R_max]^2` for the second iterate. (iii) The secondary lobe of
`|R|` near `|e| ~ 5.5`–`7` means the map is not globally monotone, so no
one-line monotonicity argument is available.

**Honest caveat, load-bearing.** This is a theorem about the **skeleton**, not
about the chain. P5 measured a branch-to-noise ratio `<= 1.5` at every
admissible `rho` and `~0.01` at `rho_c`, so the deterministic 2-cycle is buried
in the chain's own one-step noise. Proving Level D does **not** prove that the
flip explains the stationary dispersion, and P5X must not let readers infer it.

**P5X verdict.** `TARGET — OPTIONAL, EXPLICITLY AT RISK`. Closure probability
`0.45`. Admissible outcome: proved only for a reported `eta`, or not proved.

## LEVEL E — full mechanism theorem

Two readings must be separated, because they have opposite feasibility.

**E-strong (rejected as a target).** "The flip bifurcation at `rho_c` causes the
bounded high-dispersion stationary regime." This is not provable and the
existing evidence is against it: the branch SNR never exceeds `1.5`, the
stationary dispersion has an interior *minimum* near `rho ~ 0.3` rather than
growing from `rho_c`, and the measured bimodality onset is `4.1x`–`9.8x rho_c`,
far from the boundary. P5X will not target E-strong and `FROZEN_GATES.md` `G12`
forbids language that implies it.

**E-honest (the target).** "For `rho > rho_c` the origin is locally repelling
for the conditional-mean map (P3), while the unique stationary law of `P5-T7`
has second moment bounded above and below by certified constants, with
`RMS_pi` more than an order of magnitude larger than the linearisation radius;
and the mechanism that bounds it is certified saturation of the stopped
selection map together with certified far-field forgetting, not a restoring
drift."

This is exactly Levels B + C plus the P3 import, assembled. It answers the
scientific question the brief poses — how local repulsion coexists with bounded
high-dispersion stationary behaviour — without asserting a bifurcation
mechanism the evidence does not support.

**P5X verdict.** `TARGET — FINAL SYNTHESIS (E-honest only)`. Closure
probability `0.70`.

---

## Summary

| level | provable here? | carries mechanism? | P5X role | probability |
|---|---|---|---|---|
| A | yes, trivially | no (constant is everything) | corollary only, not a claim | — |
| B | yes | **yes** | primary target | 0.90 |
| C | yes, at cost | yes (discharges `H2`/`H3a`/`H3b`) | secondary target | 0.75 |
| D | maybe, scoped | skeleton only | optional, at risk | 0.45 |
| E-strong | **no** | — | forbidden | — |
| E-honest | yes, given B+C | **yes** | final synthesis | 0.70 |

The strongest theorem P5X undertakes to try to prove is **E-honest**, resting on
B and C, with D reported as achieved-or-not without affecting the verdict.
