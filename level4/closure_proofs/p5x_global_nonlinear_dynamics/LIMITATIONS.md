# P5X limitations

Written at Checkpoint A, before any result, so it cannot be trimmed to fit one.

## 1. Scope

Frozen Gaussian core only, convention A only, `m in {1,2,3,5}`, constant `rho`,
in-control operation. Everything outside is out of scope and no P8/P8R result is
imported. See `FROZEN_SCOPE.md`.

## 2. What P5X will not have established even in the best case

* any statement about the invariant **density** `pi` — its shape, modes,
  bimodality or metastability. The certified route bounds moments, not
  densities;
* therefore no rigorous account of P5's measured bimodality onset;
* any causal claim that the flip bifurcation produces the observed dispersion.
  The evidence is against it and `FROZEN_GATES.md` `G12` forbids the language;
* any operational claim. P7's negative operational-boundary finding stands
  untouched;
* any improvement to P5's `T4`/`T7` constants, or to the existing `Gamma`
  enclosures;
* anything about adaptive or state-dependent reuse policies.

## 3. Structural risks, named in advance

| risk | consequence |
|---|---|
| achieved enclosure half-width exceeds the `0.409` margin to `2` in the worst cell | Level C fails; possibly Level B too if `M_2` is also loose |
| the resolvent bound degrades as `\|e\|` enters the secondary-lobe region | cover cost explodes; `e_far` may have to be reconsidered, which is a reported change of plan |
| the `m >= 2` pair recursion for second moments is heavier than budgeted | `P5X-T6` retreats to `m = 1` |
| `R'` system unaffordable | `H3a` stays conditional; `P5-T9`'s uniqueness stays conditional |
| `P5X-T8` uncertifiable except far from `rho_c` | reported `eta`; no effect on the verdict by design |
| Lean spine drifts from the human statements | gate `G7` correspondence check is the only defence; it is a mapping check, not a proof of faithfulness |

## 4. Provenance

P5X has a genuine pre-result git anchor (`TEMPORAL_ANCHOR.md`), unlike P5,
which entered git in a single commit. That fixes P5X's own provenance only; it
repairs nothing about the 2026-08-31 P5 record and is not offered as doing so.

## 5. Novelty

`NOVELTY_STATUS = NOT_ESTABLISHED`. No literature search has been performed for
the reduction `P5X-T1` or for the certified saturation statement. Stopped-process
Fredholm reductions and rigorous interval enclosures of CUSUM functionals are
established techniques; the claim here is a specific application, and whether it
is new is for an independent adjudicator with a literature mandate to decide.
