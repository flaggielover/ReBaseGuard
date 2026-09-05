# P5Y K1 final-completion campaign

Successor to the independently validated Repair2. Everything previously
validated is **imported, never copied or edited**; this namespace adds one
scientific object (drift-aware certified operator norms), one analytic
certificate (far field), and honest measurement of what remains.

```text
PRODUCTION_ENABLED  = false            P5Y_PRODUCTION_ALLOWED = NO
HARD_CPU_CAP        = 1126 (unchanged) PRODUCTION_BITS = 256 (unchanged)
cover geometry, Taylor degree, budgets, thresholds, detector/m scope: unchanged
frozen successor / c0a1f40 / 4164121 / 7a7df9b: all byte-identical
```

## The one scientific change: drift-aware operator norms

The reviewed path bounds every kernel operator by a **whole-line** absolute
Gaussian moment, and the raw-kernel family additionally carries `e_max`
factors, so `j_i` grows linearly in the drift. At the far end of the CUSUM cover
that gave `j_0 = 11.8`, which dominated the order-2 envelopes.

Under the raw-variable formulation the state limits are `e`-free, so for
`x = (p,m)` in `[0,h]^2` the `z`-window is `[m-11/2, 11/2-p] ⊆ [-11/2, 11/2]`,
widest at `x = (0,0)`. Substituting `y = z+e`, **both** operator families have
Hermite weights and collapse to one quantity over `W = [left-11/2, right+11/2]`:

```text
||d_e^i K_e|| <= A_i(W)        ||J_i|| <= A_(i+1)(W)
A_n(W) = int_W |He_n(y)| phi(y) dy        (int He_n phi = -He_(n-1) phi)
```

evaluated in **closed form** by splitting `W` at the known roots of `He_n` —
never quadratured. Every entry is
`min(drift-aware, reviewed whole-line, Cauchy-Schwarz)`, so it can only tighten;
an audit asserts that across all 326 CUSUM cells, and the whole-line limits
reproduce the frozen named constants `1`, `2phi(0)`, `4phi(1)`,
`2phi(0)+8phi(sqrt3)` to 11 decimals.

ERROR_ALGEBRA section 2 calls the whole-line moments "admissible", not
mandatory. A sharper certified bound on the same operator relaxes nothing.

### Effect

At cell 325 the raw-kernel norms improve 13–29x:

```text
j_0  11.798 -> 0.406      j_1  10.777 -> 0.559
j_2  13.380 -> 0.777      j_3  21.963 -> 1.624
```

which flipped cell 325 from FAIL to PASS on all four m, and tightened every
other cell tested. No enclosure anywhere loosened.

## What is in here

| file | role |
|---|---|
| `code/sharp_norms.py` | the drift-aware certified norms |
| `code/sharp_certifier.py` | Repair1's certifier with `norms` swapped; nothing else |
| `code/final_qualify.py` | re-certification runner with full Repair2 provenance |
| `code/far_field.py` | the P5X-T3 far-field certificate, both detectors |
| `code/sr_status.py` | evidence-based assessment of the absent SR DAG |
| `code/sr_cost.py` | SR cost model anchored on measured primitives |
| `code/final_audit.py` | campaign self-audit and production gate |

`sharp_certifier` overrides exactly one attribute (`self.norms`). Everything
downstream — the residual envelopes, the propagation, the whole-cell
refinement, the Repair1 S0 accounting and the Repair2 provenance — reads
`norms["k"]` and `norms["j"]` and inherits the sharper bounds unchanged.

## Honest headlines

* **cell 325 = CERTIFIED_PASS** (worst utilization 22.7% of the .050 cap)
* a *different* high-radius cell, **320, still FAILS** m=2,3,5 — its
  `R2_interval` is near-symmetric about zero, so this is
  CERTIFICATE_TOO_LOOSE, not a counterexample
* far field **PASSES all m at P5X's frozen `e_far = 12`** but does **not** close
  m=3,5 at the frozen K1 splice `c_D`, leaving an uncovered interval
* **SR remains ABSENT** — 8,849 of 17,978 obligations undischarged
* **COST_CAP = NOT_ESTABLISHED**; production not authorized, not launched

See [STATUS.md](STATUS.md) for the full table and the exact blockers.
