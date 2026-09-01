# Level-4 Priority 8 — model-class robustness

**Authoritative status: `P8 = FAIL`** — independent adjudication finds 16 of 21
gates pass. The preregistered scientific gates `G4`, `G4-D`, `G4-F`, and `G7`
fail as the candidate reported. In addition, temporal-integrity gate `G14`
fails: the untracked campaign has no pre-result source/protocol digest, its E2
sample sizes contradict the executable results, and calibration refinement
reused an inspected verification address. The frozen verdict rule requires
`FAIL` when an integrity-spine gate fails. See
[`INDEPENDENT_ADJUDICATION.md`](INDEPENDENT_ADJUDICATION.md).

**In one paragraph.** The recursive re-baselining phenomenon **survives**
outside the frozen Gaussian model: `rho_c < 1` and full reuse is locally
repelling in all 40 eligible cells, and the reuse-attributable operational
damage is `-38%` to `-51%` in every innovation family. Its **magnitude does
not**: `rho_c` spans a factor of `2.54` at a matched `ARL_0`, and the
preregistered window-separability law is **rejected** across innovation families
(spread `22%`–`49%` against a `10%` margin), narrowed to a cross-detector
regularity that still misses its own `3%` sub-gate in one comparison of fifteen.
Three post-hoc explanations were frozen while seven cells did not yet exist and
**all three were rejected** by those cells. Along the way P8 shows that a
published factor-of-`3.35` gap between P4 and Stage-D D3 is **entirely
definitional**, and that a Gaussian-score analysis of this phenomenon overstates
the gain by up to `11.7x` under misspecification.

P8 is the *detector-family / distribution-family / drift-pattern robustness
matrix* handed over by P7 and by the P6 pre-design's `X5` exclusion. It asks one
question:

> Does the recursive re-baselining structure established for the two frozen
> Gaussian specialisations — the stopped-selection gain `Gamma`, the local
> stability boundary `rho_c` (P3), and the operational monitoring degradation
> (P7) — survive outside that specialisation?

The definition is traced to repository authority in
[`P8_DEFINITION_AUDIT.md`](P8_DEFINITION_AUDIT.md); nothing about the question
is invented here.

## Read in this order

| file | what it is |
|---|---|
| [`INDEPENDENT_ADJUDICATION.md`](INDEPENDENT_ADJUDICATION.md) | authoritative independent verdict, gate table, verification, and exact P9 boundary |
| [`P8_DEFINITION_AUDIT.md`](P8_DEFINITION_AUDIT.md) | where P8's question comes from; frozen vs historical vs optional vs unsupported |
| [`PRIORITY_DEPENDENCY_AUDIT.md`](PRIORITY_DEPENDENCY_AUDIT.md) | every premise, its source priority, and the strength P8 may use it at |
| [`THEORY.md`](THEORY.md) | `P8-L0`, `P8-T1`, `P8-L1`, `P8-T2`, and the empirical law `H1` |
| [`EXPERIMENT_PROTOCOL.md`](EXPERIMENT_PROTOCOL.md) | factors, sizes, estimands, statistics — frozen before production |
| [`CLOSURE_GATES.md`](CLOSURE_GATES.md) | the preregistered gates, verbatim |
| [`RESULTS.md`](RESULTS.md) | what was measured |
| [`ROBUSTNESS.md`](ROBUSTNESS.md) | detector / window / convention / drift / seed sensitivity |
| [`STATISTICAL_AUDIT.md`](STATISTICAL_AUDIT.md) | uncertainty, multiplicity, grid and moment caveats |
| [`ADVERSARIAL_REVIEW.md`](ADVERSARIAL_REVIEW.md) | the red-team pass and what it narrowed |
| [`NOVELTY_AUDIT.md`](NOVELTY_AUDIT.md) | prior-art audit and conservative labels |
| [`LIMITATIONS.md`](LIMITATIONS.md) | what P8 does not establish |
| [`CODEX_HANDOFF.md`](CODEX_HANDOFF.md) | what to attack, and how to replay it |

## Scope discipline

* P8 modifies **no** frozen artifact. `results/protected_tree_manifest_pre.json`
  records every protected tree at the anchor commit
  `ffe23a63181e2ff11380768d3c73980de80f94fb`; gate `G12` and
  `tests/test_protected_scope.py` re-check them.
* P8 does **not** reopen, repair or adjudicate P4 or P5. Where P8's measurements
  bear on a P4 artifact, they are reported as P8 observations and the P4
  artifact is left untouched.
* P8 evaluates **no policy**. P6's method, calibration and their limitations do
  not enter.
* P8 starts **no** formal layer. There is no Lean declaration and no Arb
  enclosure in this directory, and none is claimed.
* P8 owns exactly one new calibration — the non-Gaussian SR thresholds — which
  is declared in `P8_DEFINITION_AUDIT.md` §7 before any result existed and is
  labelled `NEW_P8_CALIBRATION` in every artifact.

## Layout

```text
src/rebaseguard_p8/
  families.py      the six frozen innovation families, independently written
  primitives.py    the addressable primitive field (P6R2b standard inherited)
  detectors.py     frozen CUSUM (imported) and frozen SR (restated)
  stopped.py       independent single cycles; every P8 estimand in one pass
  chain.py         the repeated-cycle chain, with step and ramp drift
  calibrate.py     ARL0 bisection (SR, non-Gaussian only)
  analysis.py      estimators, intervals, P7's boundary arithmetic
  config.py        grids, seed namespace, and every inherited constant by path
experiments/       one driver per experiment + derive_closure.py
results/           machine-readable artifacts (see CODEX_HANDOFF.md)
tests/             the focused P8 suite
```

P8 produces **no figures**. Every claim is a number in `results/*.json`,
rendered as markdown by `experiments/make_tables.py`; a plot would add nothing
that the tables do not already carry, and `results/result_tables.json` is the
single flattened artifact an independent replayer needs.

```text
```

## Reproducing

```bash
bash level4/closure_proofs/p8_model_class_robustness/reproduce.sh
```
