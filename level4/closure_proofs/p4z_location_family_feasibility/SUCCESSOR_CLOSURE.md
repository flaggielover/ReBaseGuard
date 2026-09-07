# P4Z successor closure

```text
P4Z_VERDICT = P4Z_NUMERICAL_PASS_AWAITING_FORMAL_OR_GOVERNANCE

P4_ORIGINAL_VERDICT = PARTIAL   (unchanged, untouched, not relabelled)
LEVEL4_GLOBAL_CLOSURE = NO
```

Historical P4 remains historical P4.  Nothing in the P4, P4X or P4Y namespaces
was modified, and no verdict of theirs was converted.  This is a **new**
successor artifact recording what a governed P4Z campaign, run entirely on the
local Mac, does and does not establish.

## 1. What was discharged

The historically unadjudicated residue is the **8 cells** that P4X's own
precision precondition could not decide — its obligation C2 / Checkpoint-A gate
`X6`, recorded `PRECONDITION_NOT_MET`.

```text
discharged PASS   8
FAIL              0
INCONCLUSIVE      0
```

| layer | detector | family | m | result | reasons |
|---|---|---|---|---|---|
| frozen | `cusum@5` | `t1p5` | 1 | **PASS** | — |
| frozen | `cusum@5` | `t1p5` | 2 | **PASS** | — |
| frozen | `cusum@5` | `t3` | 1 | **PASS** | — |
| frozen | `sr@520.886` | `t1p5` | 1 | **PASS** | — |
| frozen | `sr@520.886` | `t1p5` | 2 | **PASS** | — |
| frozen | `sr@520.886` | `t1p5` | 5 | **PASS** | — |
| reduced | `sr@20` | `t1p5` | 1 | **PASS** | — |
| reduced | `sr@20` | `t1p5` | 2 | **PASS** | — |

## 2. What was NOT re-adjudicated

The frozen scope is **96 cells** in 24 configurations.  Discharging the
8-cell residue is **not** a re-adjudication of all 96.

```text
PASS         44
FAIL         0
INCONCLUSIVE 52
```

Configurations killed by a prespecified kill gate: `{'frozen/cusum@5/laplace': 'K3 variance model exceeded', 'frozen/cusum@5/skewnormal4': 'K3 variance model exceeded', 'frozen/sr@520.886/skewnormal4': 'K3 variance model exceeded', 'reduced/cusum@2/gaussian': 'K3 variance model exceeded', 'reduced/cusum@2/skewnormal4': 'K3 variance model exceeded', 'reduced/sr@20/gaussian': 'K3 variance model exceeded', 'reduced/sr@20/logistic': 'K3 variance model exceeded', 'reduced/sr@20/skewnormal4': 'K3 variance model exceeded'}`
Configurations excluded on budget: `{}`

A cell reported `INCONCLUSIVE` is reported as `INCONCLUSIVE`.  It is never
counted as a pass and never dropped from the denominator.

## 3. Theorem scope

Inherited unchanged at tree `eede90383da44c250871b1bb97d12045c897c8d9`.

G1a: Gamma_{D,m,f} = E_0[A_m S_tau^psi], for a regular one-dimensional location family and a fixed residual-path stopping rule; the frozen two-sided CUSUM and two-chart SR only. Not distribution free, not detector universal, not global, not nonlinear, not valid for moving support or for an innovation law without a first moment.

## 4. Estimator

```text
PRIMARY    RB-SCORE   src/rebaseguard_p4z/rbscore.py
           sha256 981f4f09ed17c7afac59e81680128e882a9ee392e93254504d0227660351d975
COMPANION  RB-MAP     src/rebaseguard_p4z/rbmap.py
           sha256 8166946145d82d5049665d78a80ff43d705d4e40f6b0d326af9d8de1e1648ec3
CONTRACT   src/rebaseguard_p4z/analytic.py
           sha256 71e576e2ad218801dbee80ebfbf0108e10b0128549e6500404ac813ac1ffc111
```

## 5. Runtime

```text
host          LOCAL_MAC
AWS CPU used  0
runtime_hash  fb9ec8f26ce46c4a7e566dc58683d2a3d3da866cae475aeca9ba35ff729f7410
cpu           Apple A18 Pro
os            macOS 26.5.2 (25F84)
python        3.14.5   numpy 2.5.3   scipy 1.18.1
blas          accelerate
workers       1
```

## 6. Thresholds — none changed

```text
relative <= 0.03
|z|      <= 4.0
r*        = 0.010823063
any_threshold_changed_by_p4z = False
```

## 7. Cost

```text
CPU        2.3809 h
cap        12.0 h
COST_CAP   PASS
```

Includes every block produced, failed and inconclusive alike.

## 8. Provenance

```text
independent adjudication   ADJUDICATION_PASS  (44/44 checks)
replay                     24 blocks, hashes identical: True, field mismatches: False
```

## 9. Formal

```text
target       bounded-survival lemma only
declarations 12, errors 0, new axioms 0
axioms       ['propext', 'Classical.choice', 'Quot.sound']
```

## 10. What is awaiting

```text
formal      SATISFIED   -- bounded-survival lemma compiles, no sorry, no new axiom
governance  OUTSTANDING -- 52 of 96 frozen cells are INCONCLUSIVE
```

32 of those 52 were killed by `K3` because P4Z's own light-regime variance
envelope under-predicted them; 20 were refused by `K7` because the `h = 0.2`
rung of the frozen FD ladder is outside the `O(h^2)` asymptotic regime for
light-tailed families at the frozen thresholds.  Neither is evidence against
the estimator, and **every one of those 52 cells already PASSED in P4X**.

Re-certifying them requires a re-calibrated regime envelope and a ladder whose
coarsest rung is inside the asymptotic regime.  That is a **new frozen
campaign**, not an amendment of this one, and P4Z does not make it.

## 11. What this does not claim

* historical P4 was retroactively repaired
* P4 is CLOSED
* P5Y is CLOSED
* K1 is CLOSED
* Level-4 is CLOSED
* production readiness unrelated to this theorem
* all 96 frozen cells were re-adjudicated
