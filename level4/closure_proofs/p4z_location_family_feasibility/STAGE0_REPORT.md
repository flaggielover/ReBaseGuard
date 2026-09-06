# P4Z Stage-0 — the frozen pilot, and its one real finding

```text
STAGE0_VERDICT = STAGE0_PASS
Stage-0 CPU    = 0.6541 h
K1 (analytic contract vs quadrature)  worst |error| 3.733e-12  tol 1e-07  fired = False
K2 (alarm bounds vs frozen detector)  102,887 residuals, 0 mismatches, fired = False
configurations killed by K3           8 of 24
configurations excluded by K4         0
residue-carrying configurations lost  0
```

Stage-0 ran the production driver, not a separate script, on all 24
configurations at 20 blocks per route, exactly as frozen in
`production/stage0_freeze.json` before execution.

## 1. The trusted computing base held

`K1` compares all four alarm-set integrals against adaptive quadrature for
every theorem-supported family, including `logistic` and `skewnormal4`, which
the feasibility phase never exercised end to end.  Worst absolute error
**3.733e-12** against a tolerance of `1e-07`.

`K2` compares the analytic alarm bounds against the frozen `Detector.step`
crossing flag, residual by residual, on both detectors: **102,887 residuals, 0
mismatches**.

Both reproduced bit-identically across a restart, which is the first
determinism evidence of the campaign.

## 2. K3 falsified the variance model — not the estimator

This is the finding.  `K3` compares each configuration's measured per-path
relative standard deviation against twice its regime envelope, where the
envelope came from the feasibility micro-pilot.  It fired on **8 of 24**
configurations.

| configuration | regime | model | K3 limit | measured | ratio | |
|---|---|---|---|---|---|---|
| `frozen/cusum@5/gaussian` | light | 1.110 | 2.220 | 1.811 | 1.63 | ok |
| `frozen/cusum@5/laplace` | light | 1.110 | 2.220 | 2.279 | 2.05 | **K3** |
| `frozen/cusum@5/logistic` | light | 1.110 | 2.220 | 1.877 | 1.69 | ok |
| `frozen/cusum@5/skewnormal4` | light | 1.110 | 2.220 | 13.747 | 12.39 | **K3** |
| `frozen/cusum@5/t1p5` * | heavy | 2.982 | 5.963 | 3.292 | 1.10 | ok |
| `frozen/cusum@5/t3` * | moderate | 2.298 | 4.596 | 2.326 | 1.01 | ok |
| `frozen/sr@520.886/gaussian` | light | 1.110 | 2.220 | 1.751 | 1.58 | ok |
| `frozen/sr@520.886/laplace` | light | 1.110 | 2.220 | 2.055 | 1.85 | ok |
| `frozen/sr@520.886/logistic` | light | 1.110 | 2.220 | 1.811 | 1.63 | ok |
| `frozen/sr@520.886/skewnormal4` | light | 1.110 | 2.220 | 8.395 | 7.56 | **K3** |
| `frozen/sr@520.886/t1p5` * | heavy | 2.982 | 5.963 | 3.404 | 1.14 | ok |
| `frozen/sr@520.886/t3` | moderate | 2.298 | 4.596 | 2.097 | 0.91 | ok |
| `reduced/cusum@2/gaussian` | light | 1.110 | 2.220 | 2.293 | 2.07 | **K3** |
| `reduced/cusum@2/laplace` | light | 1.110 | 2.220 | 2.009 | 1.81 | ok |
| `reduced/cusum@2/logistic` | light | 1.110 | 2.220 | 2.155 | 1.94 | ok |
| `reduced/cusum@2/skewnormal4` | light | 1.110 | 2.220 | 3.201 | 2.88 | **K3** |
| `reduced/cusum@2/t1p5` | heavy | 2.982 | 5.963 | 2.404 | 0.81 | ok |
| `reduced/cusum@2/t3` | moderate | 2.298 | 4.596 | 1.758 | 0.76 | ok |
| `reduced/sr@20/gaussian` | light | 1.110 | 2.220 | 2.580 | 2.32 | **K3** |
| `reduced/sr@20/laplace` | light | 1.110 | 2.220 | 2.199 | 1.98 | ok |
| `reduced/sr@20/logistic` | light | 1.110 | 2.220 | 2.419 | 2.18 | **K3** |
| `reduced/sr@20/skewnormal4` | light | 1.110 | 2.220 | 2.658 | 2.39 | **K3** |
| `reduced/sr@20/t1p5` * | heavy | 2.982 | 5.963 | 2.637 | 0.88 | ok |
| `reduced/sr@20/t3` | moderate | 2.298 | 4.596 | 1.982 | 0.86 | ok |

`*` marks a configuration carrying one of the 8 historically unadjudicated cells.

Read the ratio column.  The **heavy** envelope (0.81–1.14) and the **moderate**
envelope (0.76–1.01) predict their configurations well.  The **light** envelope
under-predicts every one of its configurations, by 1.58× to 2.32× for the
symmetric families, so anything at twice the envelope trips a limit set at
twice the envelope.

Two compounding causes, both of them mine:

* **The light envelope was measured on one cell**, `reduced/cusum@2/gaussian`,
  and applied to two layers and two detectors.  Longer-ARL operating points
  have a larger relative spread.
* **Its RB-MAP leg was measured on four batches.**  `MICROPILOT_REPORT.md` §3.7
  flagged that four block means give an unreliable standard error, and here it
  is again: the same cell now measures 2.293 against a model of 1.110, a
  factor of 2.07 on the very cell the model was built from.

That is the P4Y Pilot-4 mechanism — a scale estimated from too few blocks
under-reports — reappearing inside P4Z's own cost model rather than in the
historical estimator.  A kill gate exists precisely to catch this, and it did.

**`skewnormal4` is different and the ratio understates it (2.88–12.39).**  Its
score is unbounded (`score_bound=None` in the frozen `families.py`), so it sits
outside the bounded-score moment argument that gives RB-SCORE its scale; it is
also the only asymmetric family, for which the origin is not a fixed point.
The feasibility checkpoint named it as the least-exercised branch of the
contract, and it is the one family the redesign does not obviously suit.

## 3. What is not being done about it

The K3 limit is not raised.  The envelope is not re-fitted after seeing these
numbers.  The killed configurations are not re-run under a kinder model.  All
eight stay killed and their 32 cells are reported `INCONCLUSIVE`.

Re-tuning a variance model against the data that falsified it is exactly the
post-hoc adjustment the frozen governance exists to prevent, and the cost of
honouring that is 32 cells — none of which is part of the historically
unadjudicated residue, and all of which P4X already passed.

## 4. Why Stage-0 still passes

The frozen rule: `STAGE0_KILLED` on a K1/K2/K9 failure, `STAGE0_INCONCLUSIVE`
if a residue-carrying configuration is killed or excluded, `STAGE0_PASS`
otherwise.  All four residue-carrying configurations survived with margin —
`frozen/cusum@5/t1p5` 3.292 against 5.963, `frozen/cusum@5/t3` 2.326 against
4.596, `frozen/sr@520.886/t1p5` 3.404 against 5.963, `reduced/sr@20/t1p5` 2.637
against 5.963 — so the residue is fully in play and Stage-1 is authorised.
