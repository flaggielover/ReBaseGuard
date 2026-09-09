# SR backend optimization successor — route O9, and the arithmetic floor

Predecessor `7389f57`. Target predeclared in `config/protocol.json`: **>= 3.75x**
additional effective speedup, subject to no loosening of any certified bound.

---

## 1. Profile of the accepted backend (dense candidate, this host)

`contract()` = 4.7931 ms. Decomposition:

| stage | ms | % | depends on |
|---|---|---|---|
| `Ct*Ra` matmuls | 1.6415 | **34.2%** | both |
| `flat*Qflat` matmuls | 1.2026 | **25.1%** | both |
| `flat` gather | 0.7441 | 15.5% | both |
| `Ra` gather | 0.7005 | 14.6% | panel only |
| error channel (289-loop) | 0.3721 | 7.8% | candidate + panel scalars |
| `C` build + transpose + abs | 0.1535 | 3.2% | candidate only |

**59.3% is FLINT matrix multiplication; 30.1% is Python gather/copy.**

This corrects an earlier working assumption that the error channel dominated. It
does not. That assumption came from a sparse-vs-dense timing difference which
actually reflects FLINT short-circuiting a near-zero `C` inside the matmuls.

## 2. Route O9 — batch the `a` axis, leave the `i`-sum untouched

The 12 separate `a`-iterations each perform a small `Ct*Ra` and a small
`flat*Qflat`. Batching them into one `Ct*Rbig` and one `SA*Qflat` leaves every
output entry as the *same* inner product `sum_i C[i,j] R[i*Dp+a,k]` in the same
order. The cancellation-critical `i`-sum is untouched — the exact opposite of
rejected route O6, which moved magnitudes outward.

```text
    Taylor coefficients bit-for-bit identical : True
    enclosures overlap                        : True
    max radius ratio O9 / baseline            : 1.000000     (O6 was 23.549)
    speedup                                   : 1.233x
```

**ACCEPTED** on rigor; insufficient on speed.

## 3. The arithmetic floor — the decisive measurement

Timing only the two FLINT matrix multiplications, with the **real** matrices —
i.e. the cost that remains if every line of Python were removed:

```text
    Ct*Rbig       1.6278 ms
    SA*Qflat      1.2118 ms
    FLOOR         2.8395 ms per contract     (22.9 ns per arb mul-add, 256 bits)

    accepted baseline                     4.8594 ms
    O9 (bit-exact)                        3.9425 ms   1.233x
    Python overhead remaining in O9       1.1030 ms   28.0%

    MAX speedup with a PERFECT zero-overhead compiled kernel :  1.711x
    REQUIRED                                                 :  3.75x
```

> A compiled C / Cython / Rust kernel cannot exceed **1.711x**, because 72% of
> O9 is already FLINT C-level arithmetic. Phase-3 interpreter removal is
> therefore **provably insufficient**, not merely unattempted.

## 4. Campaign cost at the floor

```text
    102 contracts x 2.8395 ms x 316 cells x 83,452 panels / 3600 = 2121.6 CPU-h
    residual SR allowance                                        =  773.0 CPU-h
    shortfall AT THE ARITHMETIC FLOOR                            =    2.74x
```

The operation count is fixed by frozen scope and frozen degrees
(`D=11, Z=20, cand_degree=16`, 256 bits, 3,994 patches, 83,452 panels, 316
cells, 102 contracts): **3.34e14 arb mul-adds**. Fitting 773 CPU-h would require
**8.3 ns** per 256-bit interval mul-add, against FLINT's measured **22.9 ns**.

## 5. Optimization classes — all six addressed

| class | route | result |
|---|---|---|
| interpreter removal / compiled kernel | arithmetic-floor measurement | **bounded at 1.711x — provably insufficient** |
| cancellation-preserving fused contraction | **O9** | 1.233x, bit-exact — ACCEPTED |
| candidate-independent intermediate reuse | O4, `Rbig` hoist | folded into O9 |
| multi-moment / multi-RHS reuse | O7 | 1.061x measured |
| allocation / copy elimination | — | bounded by the floor (28% of O9) |
| exact / dyadic representation | — | cannot reduce a frozen op count; precision may not be lowered |
| tensor reassociation (diagnostic only) | O6 | REJECTED, radii x23.549 |

## 6. Verdict

```text
    SR_BACKEND_OPTIMIZATION = EXHAUSTED_UNDER_FROZEN_SCOPE_AND_PRECISION
    shortfall at the implementation-independent floor = 2.74x
```

This is not "Python is slow". It is a measured lower bound on the arithmetic
itself. Closing a 2.74x gap at the floor would require reducing the frozen
operation count (frozen scope / degrees) or the frozen precision — both
prohibited — or beating FLINT's 256-bit ball arithmetic by >2.7x, which no
available implementation provides.
