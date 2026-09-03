# P4X production result

```text
CHECKPOINT              = P4X_CHECKPOINT_A (756bf68), ACTIVE and BINDING
P4_ORIGINAL_VERDICT     = PARTIAL   (immutable)
P4X_SUCCESSOR_VERDICT   = PARTIAL
P4_SCIENTIFIC_LINE      = PARTIALLY_REPAIRED_BY_SUCCESSOR
NOVELTY_STATUS          = NOT_ESTABLISHED
LEVEL4_GLOBAL_CLOSURE   = NO
```

## 1. Obligation ledger

| obligation | statement | status |
|---|---|---|
| `C1` | inherit the theorem unchanged | **PASS** |
| `C2` | attainable-precision numerical correspondence | **INCOMPLETE** |
| `C3` | Route Q as an independent cross-check only | **PASS** |
| `C4` | failure-mode evidence matched to the proved failure mode | **PASS** |
| `C5` | Gaussian consistency by a two-sample uncertainty statistic | **PASS** |
| `C6` | re-verify the inherited Lean and Arb artifacts | **PASS** |
| `C7` | protected-tree integrity | **PASS** |

## 2. Anchor reproduction (phase P0)

48 comparisons across 3 configurations, tolerance `1e-12`, **0 mismatches**.

Reproducing the frozen values bitwise validates, together: Route-A frozen score estimator; Route-B frozen CRN central difference; Richardson per-block combination at h = 0.05 / 0.025; Philox RNG addressing (seed, batch, step) with 2^64 stream stride; detector parameters k=1/2, h=5, A=520.886133602749; window semantics w = min(m, tau) with random denominator; inclusion of the alarm-causing increment; family parameterisation and per-family seed offset.

## 3. C2 correspondence

* cells: **88 / 96 PASS**
* failed: **0**
* precision-limited: **0**

Gate, unchanged from the frozen protocol: relative discrepancy `<= 0.03` **and** `|z| <= 4`.

No theorem-supported cell failed the frozen gate.

### Worst cells by relative discrepancy

| layer | detector | family | m | relative | \|z\| | Route-A relSE | Route-B relSE | result |
|---|---|---|---|---|---|---|---|---|
| frozen | sr@520.886 | t1p5 | 1 | 2.366% | 1.29 | 1.502% | 1.078% | PRECONDITION_NOT_MET |
| reduced | sr@20 | t1p5 | 1 | 2.098% | 1.14 | 0.748% | 1.721% | PRECONDITION_NOT_MET |
| frozen | sr@520.886 | t1p5 | 2 | 1.734% | 1.31 | 1.086% | 0.774% | PRECONDITION_NOT_MET |
| frozen | sr@520.886 | t1p5 | 5 | 1.680% | 1.40 | 1.108% | 0.460% | PRECONDITION_NOT_MET |
| frozen | sr@520.886 | t1p5 | 3 | 1.674% | 1.37 | 1.053% | 0.621% | PASS |
| reduced | sr@20 | t1p5 | 2 | 1.463% | 1.14 | 0.522% | 1.190% | PRECONDITION_NOT_MET |
| reduced | sr@20 | t1p5 | 3 | 1.207% | 1.19 | 0.420% | 0.934% | PASS |
| frozen | sr@520.886 | laplace | 1 | 1.030% | 2.25 | 0.287% | 0.361% | PASS |
| reduced | sr@20 | t1p5 | 5 | 0.986% | 1.27 | 0.321% | 0.717% | PASS |
| reduced | cusum@2 | t1p5 | 1 | 0.979% | 0.84 | 0.891% | 0.761% | PASS |
| frozen | sr@520.886 | laplace | 5 | 0.950% | 2.49 | 0.245% | 0.296% | PASS |
| frozen | sr@520.886 | laplace | 3 | 0.878% | 2.11 | 0.261% | 0.325% | PASS |

## 4. Two-stage precision acquisition

* already at `r*` after stage 1: **42** of 48 (configuration, route) pairs
* top-ups approved: **6**
* precision-limited: **0**

Trigger: *the route's own achieved relative standard error*.  It excludes discrepancy, discrepancy sign, whether the cell passes, whether the cell is close to passing, whether the campaign would close.

| configuration | route | stage-1 N | stage-1 relSE | target N | added N | reason |
|---|---|---|---|---|---|---|
| frozen/cusum@5/t1p5 | route_a | 44,500,000 | 1.372% | 93,464,696 | 48,964,696 | PRECISION_ONLY |
| frozen/cusum@5/t1p5 | route_b | 54,000,000 | 3.569% | 2,254,168,764 | 2,200,168,764 | PRECISION_ONLY |
| frozen/cusum@5/t3 | route_a | 3,200,000 | 1.220% | 4,065,855 | 865,855 | PRECISION_ONLY |
| frozen/sr@520.886/t1p5 | route_a | 14,750,000 | 1.249% | 23,063,753 | 8,313,753 | PRECISION_ONLY |
| reduced/cusum@2/t1p5 | route_b | 65,000,000 | 1.471% | 169,718,344 | 104,718,344 | PRECISION_ONLY |
| reduced/sr@20/t1p5 | route_b | 38,000,000 | 2.127% | 314,320,287 | 276,320,287 | PRECISION_ONLY |

## 5. C5 Gaussian consistency

Statistic: `z_combined = |e1 - e2| / sqrt(SE1^2 + SE2^2)`, limit **4.0**, using both campaigns' published uncertainty.

| detector | m | closed | P4X | signed rel | `z_combined` | historical single-error | pass |
|---|---|---|---|---|---|---|---|
| cusum@5 | 1 | 15.916540 ± 0.059905 | 15.877342 ± 0.016821 | -0.246% | **0.630** | 2.33 | yes |
| cusum@5 | 2 | 13.264825 ± 0.050152 | 13.247492 ± 0.015087 | -0.131% | **0.331** | 1.15 | yes |
| cusum@5 | 3 | 11.957078 ± 0.043161 | 11.914735 ± 0.013733 | -0.354% | **0.935** | 3.08 | yes |
| cusum@5 | 5 | 10.226364 ± 0.035237 | 10.184212 ± 0.012062 | -0.412% | **1.132** | 3.49 | yes |
| sr@520.886 | 1 | 17.453571 ± 0.065881 | 17.258937 ± 0.020260 | -1.115% | **2.824** | 9.61 | yes |
| sr@520.886 | 2 | 14.500510 ± 0.056725 | 14.358610 ± 0.016104 | -0.979% | **2.406** | 8.81 | yes |
| sr@520.886 | 3 | 12.972655 ± 0.049011 | 12.831340 ± 0.013049 | -1.089% | **2.786** | 10.83 | yes |
| sr@520.886 | 5 | 11.048526 ± 0.041047 | 10.922955 ± 0.009725 | -1.137% | **2.977** | 12.91 | yes |

Worst `z_combined` = **2.977** against a limit of 4.0.  The historical single-error statistic reaches 12.91 and gates nothing.

## 6. C4 failure-mode evidence

**A3 half** — the identity is FALSE, exact defect 2.  Discharged by analytic closed form + Route Q + exact rational Arb.  16/16 uniform cells corroborate at `|z|` 468-714.  New compute: **NONE**.

**First-moment half** — NON-EXISTENCE of the estimand, E|A_1| = infinity.  Discharged by analytic (PROOF.md section 10).  No Monte Carlo disagreement signature is demanded, because a two-route discrepancy statistic cannot express non-existence; the measured `|z|` across the 16 Cauchy cells is 0.026-1.616.  New compute: **NONE**.

## 7. C3 Route-Q cross-check

Role: `INDEPENDENT_CROSS_CHECK_ONLY`.  24 rows, worst relative discrepancy `4.331e-09` against a tolerance of `1e-06`.  Cross-check: **CONSISTENT**.

Route Q arbitrated no cell (`False`) and rescued no gate (`False`).  Route Q evaluates the memoryless detector and is therefore evidence about the identity, never about a frozen operating point.  It entered no cell decision.

## 8. C6 Lean and Arb re-verification

* Lean: **19** declarations, axioms exactly `Classical.choice, Quot.sound, propext`, **0** new declarations
* Arb: objects `laplace_closed_form, uniform_counterexample, general_score_witness`, **0** new objects
  * at 160 bits: 19 checks, failed `[]`, pass `True`
  * at 256 bits: 19 checks, failed `[]`, pass `True`
* tools: {"lean": "Lean (version 4.33.1, arm64-apple-darwin24.6.0, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)", "lake": "Lake version 5.0.0-src+819816b (Lean version 4.33.1)", "python": "3.14.5", "python_flint": "0.9.0"}

## 9. Cost

```text
total CPU               24.7493 h   (cap 60.0)   PASS
total wall              8.3312 h
worst configuration     18.5994 h   (cap 40.0)   PASS
                        frozen/cusum@5/t1p5
```

The pre-registered high-risk configuration `frozen/sr@520.886/t1p5`: Checkpoint-A stage-1 projection 1.750 h, pre-run projection at the production block size 3.184 h, **actual 2.686 h**, against a checkpoint worst-case of 55.84 h and a 40.0 h cap.

## 10. Binding verdict

```text
P4X_SUCCESSOR_VERDICT   = PARTIAL
P4_ORIGINAL_VERDICT     = PARTIAL   (unchanged)
P4_SCIENTIFIC_LINE      = PARTIALLY_REPAIRED_BY_SUCCESSOR
load-bearing contradiction = False
integrity failure          = False
```

## 11. Integrity

Protected tree verified at three readings — pre-production, post-production and pre-verdict — over 33 tracked paths by git object: {'pre_production': 'PASS', 'post_production': 'PASS', 'pre_verdict': 'PASS'}.  `P4_ORIGINAL_MUTATED = NO`, `P5_P5X_MUTATED = NO`.

