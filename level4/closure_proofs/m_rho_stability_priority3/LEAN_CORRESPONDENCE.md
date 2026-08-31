# Priority-3 Lean correspondence

`lean/StabilityMapP3.lean` formalizes the generic stability-map logic and
nothing else. It is deliberately small: the campaign's numerical work is
mechanically checked by tests and by Arb, not by Lean, and the Lean file makes
no numerical claim.

## Declared reuse

Priority 3 is a synthesis layer, so its Lean file **imports** the two closed
spines rather than restating them:

```lean
import MGtOneClosure   -- Level-4 Priority 1
import SRPriority2     -- Level-4 Priority 2
```

`run_lean.py` compiles both dependencies from their own protected sources into
a temporary directory and then compiles the Priority-3 file against them. It
modifies neither. This is the opposite of the Priority-2 design, where
detector independence was the scientific point; here consuming the closed
theorems *is* the scientific point, and `manifest.json::lean` records that
choice and its rationale explicitly.

## Correspondence table

| prose statement | Lean declaration |
|---|---|
| `|lambda| = rho·d` for `rho >= 0` (Lemma 1) | `abs_multiplier` |
| `|lambda|` strictly increasing in `rho` (Lemma 2) | `abs_multiplier_strictMonoOn` |
| exact boundary at `rho_c` (Lemma 3) | `boundary_at_criticalRho` |
| attraction criterion (Theorem 4) | `attracting_iff_lt_criticalRho` |
| repulsion criterion (Theorem 4) | `repelling_iff_criticalRho_lt` |
| the three cases are exhaustive | `trichotomy` |
| `rho_c <= 1 <=> GammaTilde >= 2` (Theorem 5) | `criticalRho_le_one_iff` |
| gains in `[0,2]` attract on `[0,1)` (Theorem 6) | `attracting_of_gain_le_two` |
| neutral gain attracts everywhere, no `rho_c` | `attracting_of_gain_eq_one` |
| gains strictly in `(0,2)` attract at full reuse | `full_reuse_attracting_of_gain_between_zero_two` |
| gains `0` and `2` are boundaries at full reuse | `full_reuse_boundary_of_gain_eq_zero_or_two` |
| gain-interval envelope (Lemma 7) | `gainDistance_le_max` |
| interval robustness, attracting side (Theorem 8.1) | `attracting_of_interval` |
| interval robustness, repelling side (Theorem 8.2) | `repelling_of_interval` |
| Priority-3 predicates are the Priority-1 predicates | `attracting_iff_priority1`, `repelling_iff_priority1` |
| Priority-3 predicates are the Priority-2 predicates | `attracting_iff_priority2`, `repelling_iff_priority2` |
| CUSUM derivative plus classification | `cusum_attracting_of_lt_criticalRho` |
| SR derivative plus repelling classification | `sr_repelling_of_criticalRho_lt` |

The four `*_iff_priority*` lemmas are proved by `Iff.rfl`: the Priority-3
attraction and repulsion predicates are *definitionally* the ones already used
by the two closed campaigns, so the synthesis does not quietly introduce a
second, weaker notion of stability.

## Bridges

The two bridge theorems are the only detector-aware declarations. Each takes
the exact hypotheses of the corresponding closed dominated-derivative spine,
returns that spine's `HasDerivAt` conclusion with the derivative written as
`multiplier rho Gamma`, and pairs it with the generic classification at that
reuse fraction:

```text
cusum_attracting_of_lt_criticalRho :
  (measurability, integrability, domination) ->
  0 <= rho -> 1 < Gamma -> rho < criticalRho Gamma ->
  HasDerivAt F (multiplier rho Gamma) 0  ∧  LocallyAttracting rho Gamma
```

with `Gamma = ∫ A·T dμ`, and symmetrically for SR on the repelling side.

## Axiom audit

`lean/AxiomAudit.lean` prints axioms for fourteen declarations. All fourteen depend
on exactly `propext`, `Classical.choice`, `Quot.sound` — the standard Mathlib
set reported in the Priority-1 and Priority-2 closures. There is no `sorry`, no
`sorryAx`, and no project-specific scientific axiom. The raw output is stored
verbatim in `results/axiom_audit.txt`, and `run_lean.py` fails if the count,
the axiom set, or the source hash changes.

## What Lean does not do here

- It evaluates no `GammaTilde` value and certifies no Monte Carlo estimate.
- It does not re-prove the concrete Gaussian tail, moment or domination
  obligations; those remain human analytic obligations discharged in the
  Priority-1 and Priority-2 packages and are inherited, not re-derived.
- It proves nothing global or nonlinear. `LocallyAttracting` and
  `LocallyRepelling` are strictly conditions on the multiplier magnitude.
