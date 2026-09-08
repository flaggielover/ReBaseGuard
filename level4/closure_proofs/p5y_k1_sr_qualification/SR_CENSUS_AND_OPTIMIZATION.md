# SR executable census and backend optimization campaign

Resolves the 19-vs-72 ambiguity and reports three optimization routes attempted
against the residual budget. All timings measured on the campaign host with the
frozen runtime binding (flint 0.9.0, OpenBLAS 0.3.34.0.0, 256 bits, 1 thread).

---

## 1. The 19-vs-72 question is resolved: both numbers are real, and they are
## not the same quantity

* **19** = `functions_per_detector` in the frozen work model = the count of
  top-level OBJECT CLASSES (`h_1..h_4, S_0..S_4, F_0..F_4, dF_0..dF_4`).
* **72** = the count of DAG nodes requiring an independent certified enclosure,
  i.e. `{reward_chain, source_chain, finite_power, resolvent} x orders {0,1,2}`:
  12 h + 15 S + 30 W + 15 F/D/H.

The cost model is driven by the **contract** stage, which is paid once per
(cell, panel, certified function). That is the 72-count, not the 19-count. The
frozen work model is not wrong; it is counting object classes, and it was never
reconciled against the per-order candidate census that `cusum_layer2._candidates`
actually builds.

## 2. The frozen amortization is correct (a suspicion ruled out)

`bench.py` computes `amort = t_sh/(CELLS*NFUN) + t_drift/NFUN + t_warm` with
`only_panel=0`, so `opt_shared_build` is **per panel**, not per patch. Shared
work is therefore NOT multiplied by the cell count anywhere. An earlier reading
of a 42x discrepancy was an error of mine (patch-vs-panel), now retracted.

## 3. Measured three-stage cost structure (this host)

```text
    t_shared    158.192 ms / panel     (patch,panel)        paid ONCE
    t_drift       2.357 ms / panel     (patch,panel,e)      per cell
    t_contract    4.865 ms / panel     (patch,panel,e,func) per cell PER FUNCTION
```

`t_contract` is quoted for a DENSE candidate. The sparse unit candidate gives
1.763 ms; the real candidates are dense (`complexity_guard.nonzero_coefficients
= 289` of 289), so the dense figure governs.

```text
    stage 1 shared      3.667 CPU-h    (once, all cells, all functions)
    stage 2 drift      17.597 CPU-h    (x322 cells)
    stage 3 contract   36.05 CPU-h     PER FUNCTION
    residual SR allowance = 1126/1.15 - 206.086 = 773.0 CPU-h
```

**The campaign fits iff the effective census F satisfies F <= 20.9** at baseline
speed. The census is 72. **Required speedup: 3.45x.**

## 4. Optimization routes attempted

| route | what | speedup | rigor | verdict |
|---|---|---|---|---|
| **O4** | hoist the candidate-independent `Ra` gather out of `contract` | 1.134x | Taylor coefficients **bit-for-bit identical** | **ACCEPTED** |
| **O5** | vectorize the 289-iteration error channel as `exV·(\|C\|magW) + magV·(\|C\|exW)` | 1.198x cumulative | coefficients bit-identical; error channel conservative, ratio 1.000000000 | **ACCEPTED** |
| **O6** | refactor the triple sum into one product against a candidate-independent tensor `T[(i,j),(a,bq)] = sum_k R[i,a,k] Q[j,k,bq]` | **3.60x raw**, 2.44x amortized at F=72 | **inflates Taylor-coefficient radii 23.549x** | **REJECTED** |

### Why O6 is rejected, and why more precision cannot save it

The inflation is **23.549x at 256, 384, 512 and 768 bits alike** — it is not
rounding, it is structural interval dependency:

```text
    baseline :  (C . R) . Q   -> radius picks up | sum_i C[i,j] R[i,a,k] |
                                  the sum is INSIDE the magnitude: cancellation
    route O6 :  C . (R . Q)   -> radius picks up sum_i |C[i,j]| |R[i,a,k]|
                                  magnitudes taken FIRST: no cancellation
```

The baseline association is mathematically superior for enclosure width. O6
would loosen every certified Taylor coefficient by up to 23.5x, violating the
backend governance rule that an optimization may not loosen a bound. It is
rejected despite being the fastest route found.

## 5. Position after the optimization campaign

```text
    accepted speedup (O4+O5)          1.198x
    required speedup                  3.45x
    remaining gap                     2.88x
    projected K1 with O4+O5 at F=72   1.15 x (2189 + 206.1) = 2754 CPU-h = 245% of cap
```

## 6. Status

```text
    SR_EXECUTABLE_CENSUS = 72 functions/cell   (RESOLVED)
    SR_COST_FEASIBILITY  = NOT_ESTABLISHED     (gap 2.88x after documented attempts)
    COST_CAP             = NOT_ESTABLISHED
```

This is **not** a proof that no governed optimization can close the gap. Three
routes were tried; the fastest was rejected on rigor. Routes not yet attempted
include reducing the census itself (proving some of the 72 nodes do not need
independent panel-resolved enclosures), m-sharing across the four m values,
and a lower-level (non-Python) contraction. The gap is 2.88x, not orders of
magnitude, so the question remains open rather than settled.
