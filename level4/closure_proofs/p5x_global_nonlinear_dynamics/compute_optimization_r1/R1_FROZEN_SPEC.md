# P5X Compute Optimization R1 — frozen benchmark specification

Frozen **before** any optimized benchmark result and committed at Checkpoint C.
Nothing below may be chosen or changed after observing an R1 number.

R-A′ remains the reference implementation. Its `PASS` at half-width
`0.014176477298268092` is untouched, and the `0.2` threshold is unchanged.

---

## 1. The single change

Substitute a tighter rigorous upper bound for `C = ||(I - K_e)^{-1}||_inf`:

```text
R-A'  (baseline)  : block forcing,        C = 1239.2722762545090  on [0.24, 0.26]
R1    (optimized) : monotone minorant,    C = 220.70751870968231  at the cell's worst drift
```

Everything else — operator, reward, kernel, state space, stopping convention,
estimand, enclosure semantics, candidate degree, precision, Bernstein depth,
gate semantics — is byte-for-byte the R-A′ computation, reused **by import** of
`certified_method_repair_ra/ra_certifier.py`, which this campaign does not
modify. See `NEUTRALITY_AUDIT.md` and `PROOF.md`.

## 2. Exact formula for the bound

```text
aligned arm increment:  V ~ N(|e| - k, 1)          (minus arm for e >= 0)
one-sided chain:        S_t = max(0, S_{t-1} + V_t)
left-endpoint envelope: lower_t[i] <= H_t(x_i),  x_i = h i / cells
                        lower_t = r + P lower_{t-1},   lower_0 = 0
                        r(x)     = Phi( x - (k - |e|) - h )
                        P(x, 0)  = Phi( dx + (k - |e|) - x )
                        P(x, j)  = Phi( x_{j+1} + (k-|e|) - x ) - Phi( x_j + (k-|e|) - x )
bound:                  C_opt = min_{1 <= t <= n_max}  t / lower_t[0]
```

evaluated at `|e| = e_lo` of the cell, which `PROOF.md` `L-R1.4` proves is the
worst case for the whole cell.

## 3. Frozen implementation parameters

| parameter | value | provenance |
|---|---|---|
| minorant cells | `100` | the value certified at `e = 0` as `N-01` |
| minorant `n_max` | `250` | same |
| minorant precision | `192` bits | same |
| certifier precision | `256` bits | unchanged from R-A′ |
| Taylor order `N` | `120` | unchanged from R-A′ |
| candidate degree | `12`, quadrature `400`, `scale_bits = 50` | unchanged from R-A′ |
| Bernstein subdivision depth | `3` | unchanged from R-A′ |
| `e_0` denominator | `10^7`, exact rationals | unchanged from R-A′ |
| `a` | `2 phi(0) = 0.7978845608...` | unchanged |
| `b2` | `4 phi(1) = 0.9678828981...` | unchanged |
| `c2` | `1.13788 + b2 * e_hi` | unchanged |

## 4. Frozen derived quantities (computed before the benchmark, from §2–§3)

```text
C_opt   = 220.7075187096823143058125152854812294891688046029854141728   (t* = 52, H_52(0) >= 0.2356059290775706108)
h_max   = 1 / (4 a C_opt) = 0.0014196550084052...
n_sub   = 8            (smallest n >= (e_hi-e_lo)/(2 h_max) whose closure check passes)
h_sub   = 0.00125      (exact rational 10^5 / (8 * 10^7))
closure = C (2 a h_sub + b2 h_sub^2) = 0.440582  <=  1/2      VERIFIED
```

These are **inputs** derived by the frozen formula, not outcomes. They are fixed
here so that the benchmark has nothing left to choose.

## 5. Retry / refinement rule

A single bounded, deterministic ladder, frozen here: `n_sub` is the smallest
integer `n >= (e_hi - e_lo)/(2 h_max)` for which the closure condition
`C (2 a h + b2 h^2) <= 1/2` holds, searched over `n, n+1, n+2, n+3`. It resolved
at the first candidate, `n = 8`. **No other retry, refinement or escalation is
authorised.** Anything else is an abort.

## 6. Abort rule

Abort, and record the benchmark as `FAIL`, if: the self-test of §9 fails; the
closure condition fails for all four ladder candidates; the sub-cells do not
tile `[0.24, 0.26]` exactly; a sub-cell's declared range is not contained in its
`e` ball; any Arb positivity, containment or mass-balance check raises; or the
monotone minorant's `C_opt` exceeds the block-forcing bound (which would mean
the "optimization" is not one). No parameter change, no partial substitution.

## 7. Benchmark cell — unchanged, and deliberately not made easier

```text
detector = CUSUM (k = 1/2, h = 5)
m        = 1
e-cell   = [0.24, 0.26]
```

The same cell as the failed first gate and as R-A′: it contains
`argmax_e |R_{CUSUM,1}|`, carries the tightest margin to `2`, sits in the
steepest part of the map, and has among the worst resolvents in the cover. It is
not moved, not narrowed and not widened.

## 8. Baseline

Taken from the authoritative stored artifact `results/ra_stop_gate.json`, not
re-run:

```text
wall 5173.3 s | CPU 22311.2 s = 6.20 CPU-hours | 5 workers
120 certified solves | 80 Bernstein bounds | 40 sub-cells | 0 refinements
half-width 0.014176477298268092
enclosure [-1.5902505376455707, -1.5618975830490345]
```

The optimized run uses the **same worker count (5)** so that CPU-seconds are
comparable without a parallelism confound.

## 9. Mandatory self-test, before the benchmark

| id | check |
|---|---|
| `T1` | the optimized path calls the *same* `ra_certifier.certify_at_exact_drift`; module identity asserted, and the certified `delta`, `ghat(x_0)` at a shared exact drift are bit-identical to a direct call |
| `T2` | `C_opt <= C_block` at the cell's worst drift (the optimization must be one) and at `e in {0, 1/2, 1, 2}` |
| `T3` | `C_opt(e = 0) <= 1315.79`, consistent with the independently certified `N-01` value `250/0.19` |
| `T4` | `C_opt` is not below a Monte-Carlo estimate of `E_{x_0}[tau]` at the cell drift — a validity spot-check that the bound is an upper bound, not proof |
| `T5` | interval containment: at a shared exact drift, the R1 value enclosure is contained in the R-A′ value enclosure (same centre, smaller radius) |
| `T6` | `e = 0` degenerate behaviour: the minorant with `|e| = 0` reproduces the `N-01` configuration (`k - |e| = k`) |
| `T7` | exact-rational drift handling: every `e_0` is an exact rational with denominator `10^7`, the sub-cells tile exactly, and each sub-cell range lies inside its ball |
| `T8` | `empirical_monotonicity_used` is `false` in every emitted artifact |

Any failure `->` STOP, do not run the benchmark.

## 10. Frozen acceptance thresholds

**Certification (all required):**
* the enclosure must be of the same target `R_{CUSUM,1}` on `[0.24, 0.26]`;
* achieved half-width `<= 0.2`;
* the R1 enclosure must **overlap** the authoritative R-A′ enclosure
  `[-1.5902505376455707, -1.5618975830490345]` (both are valid enclosures of the
  same number, so a disjoint result would falsify one of them).

**Speed** — `SPEEDUP = 6.20 / optimized_CPU_hours`, CPU-authoritative:

```text
SPEEDUP <  2.0            ->  NOT_WORTH_MIGRATING
2.0 <= SPEEDUP <  3.0     ->  BORDERLINE
3.0 <= SPEEDUP <  4.0     ->  WORTH_MIGRATING
SPEEDUP >= 4.0            ->  STRONG_PASS
```

These bands are not changed after the run.

## 11. Pre-registered prediction

Recorded before the benchmark so the outcome can falsify it:

```text
predicted half-width  = 0.00886      (band 0.006 - 0.014)
predicted CPU-hours   = 1.24
predicted SPEEDUP     = 5.0          (STRONG_PASS)
```

built from `n_sub = 8` and the R-A′-measured `delta ~ 1.03e-5`,
`delta' ~ 2.48e-5`, `sup|ghat'| ~ 3.24`, `d_e ghat(x_0) ~ -1.130`.

## 12. What this campaign will not do

It will not launch the full cover, will not shorten `[0, 12]`, will not touch
the R-A′ implementation or result, will not alter any P5X theorem statement, and
will not use the `0.2` threshold as anything but a fixed number.
