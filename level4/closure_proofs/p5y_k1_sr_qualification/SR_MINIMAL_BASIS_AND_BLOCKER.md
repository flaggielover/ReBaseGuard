# SR minimal certified basis, exact contract census, and the cost blocker

Continues `SR_CENSUS_AND_OPTIMIZATION.md`. The census was attacked as instructed,
ahead of backend speed. The result moves in the opposite direction to the one
hoped for, and it is reported as measured.

---

## 1. The 72-node figure was an UNDER-count, not an over-count

A DAG node is not a unit of work. The unit of work is a **contract**: one
application of one moment operator to one candidate. The SR operator identities

```text
    K'    = -(K_z + eK)                    moment shift 1
    K''   =  K_z2 + 2e K_z + (e^2-1) K     moment shift 2
    K_z'  = -(K_z2 + e K_z)
    K_z'' =  K_z3 + 2e K_z2 + (e^2-1)K_z   moment shift 3
```

mean that Leibniz, `(M f)^(k) = sum_i C(k,i) M^(i) f^(k-i)`, requires each chain
element at several shifts. Deriving the closure exactly:

```text
    distinct (candidate, moment-shift) contracts : 102
    distinct candidates operated on              :  46   <- the MINIMAL BASIS
    max moment shift required                    :   3
    contracts by shift : {0: 43, 1: 35, 2: 20, 3: 4}
```

**Minimal independent certified basis = 46 candidates; 102 contracts.**
The reductions that do apply are already counted: `S_0 = rho_1` is closed form
(3 nodes free), `W_(r,0) = S_r` aliases (4 families free), and every derivative
object is obtained by applying an already-needed operator to an already-needed
candidate rather than by a new solve. Even so the contract count is **102, not
72**, because 72 counted nodes and the cost is paid per (candidate, shift).

## 2. Measured cost with the minimal basis

```text
    102 contracts x 4.845 ms x 316 cells x 83,452 panels / 3600 = 3619 CPU-h
    best measured optimization (O4+O5, bit-exact)       1.198x
    O7 grouped multi-operator contract (bit-exact)      1.061x measured
                                                        (modelled 1.54x -- the
                                                        model over-estimated the
                                                        error-channel share)
    => optimized projection ~2900 CPU-h  against a residual allowance of 773.0
    => shortfall 3.75x
```

## 3. The governing blocker is not my measurement — it is internal to the
## frozen record

`p5y_k1_sr_backend_cost_audit/config/frozen_audit.json` is an adjudicated,
binding artifact (27/27 checks). It defines the SR feasibility ladder:

| tier | SR allowance | vs governing residual (773.0) |
|---|---|---|
| **HARD** | 1480.9 CPU-h | **1.92x over** |
| STRONG | 3087.9 CPU-h | 3.99x over |
| PROMISING | 6301.8 CPU-h | 8.15x over |

with `semantics.HARD = "projected full K1 <= 1848 CPU-h (historical cap)"`.

> The ladder was calibrated against `HARD_CPU_CAP_historical = 1848`.
> The governing cap is **1126**, and `cap_may_be_raised = False`.
>
> **Under the governing cap, no outcome of the project's own frozen feasibility
> ladder satisfies the budget — not even complete success at the HARD tier,
> which still exceeds the residual allowance by 1.92x.**

This is independent of my backend measurements. Achieving everything the frozen
audit itself calls success would still not fit.

## 4. Why this cannot be resolved from inside the campaign

Closing the gap requires one of:

1. **raising the cap** — explicitly forbidden (`cap_may_be_raised = False`, and
   the superseded 1848 must not be reused);
2. **reducing frozen scope** — 316 cells, m={1,2,3,5}, 3,994 live patches, the
   panel census and the 8,849 obligations are all frozen;
3. **a further ~3.75x rigor-preserving backend speedup** — four routes have now
   been implemented and measured (O4, O5, O6, O7). The only one large enough
   (O6, 3.60x) was rejected because it structurally inflates certified radii
   23.549x at every precision, which is the interval dependency problem, not
   rounding.

None is available without a governance decision that the repository does not
contain.

## 5. Status

```text
    SR_MINIMAL_BASIS      = 46 candidates / 102 contracts   (DERIVED)
    SR_COST_FEASIBILITY   = INFEASIBLE_UNDER_GOVERNING_CAP
    COST_CAP              = NOT_ESTABLISHED  (SR unmeasurable within budget)
    K1                    = CUSUM PASS_CANDIDATE + SR BLOCKED
    P5Y                   = NOT READY for independent final adjudication
```

Historical `P5 = PARTIAL` and `P5X = PARTIAL` are untouched, as is the CUSUM
result at `ea2ce6b`.

## 6. What would unblock it (for the authority, not for this campaign)

* an authorized cost-cap decision for the successor campaign, or
* an adjudicated re-scoping of the SR cover geometry (patch grid / panel census),
  which changes the frozen estimand's certification route, or
* a new backend campaign achieving >=3.75x while preserving certified radii —
  plausible in a compiled contraction kernel, but that is a new governed
  optimization campaign with its own adjudication, not a step inside this one.
