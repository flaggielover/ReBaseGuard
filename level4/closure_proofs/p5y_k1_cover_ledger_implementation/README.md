# P5Y K1 cover-ledger IMPLEMENTATION namespace

This namespace implements the immutable specification frozen in
[`../p5y_k1_cover_ledger_successor/`](../p5y_k1_cover_ledger_successor/).
It is an implementation and qualification effort. It is **not** production, it
is **not** a scientific result, and it does not change any historical verdict.

```text
PRODUCTION_ENABLED                = false
SCIENTIFIC_VERDICT_CHANGED        = NO
LEVEL4_GLOBAL_CLOSURE             = NO      (unchanged)
P5_ORIGINAL_VERDICT               = PARTIAL (unchanged)
P5X_FINAL_VERDICT                 = PARTIAL (unchanged)
HISTORICAL_K1_VERDICT             = K1_INCOMPLETE_BUDGET (unchanged)
FROZEN_SUCCESSOR                  = FROZEN_WITH_IMPLEMENTATION_DEPENDENCIES
                                    (untouched, byte-identical)
HARD_CPU_CAP                      = 1126 CPU-hours (never increased)
PRODUCTION_PRECISION              = 256 bits (never escalated)
```

## The four kinds of thing here, kept separate

| Directory | What it is | Result-bearing? |
|---|---|---|
| `../p5y_k1_cover_ledger_successor/` | the FROZEN specification | binding, immutable, never written by this namespace |
| `code/` | the implementation | executable, not evidence |
| `tests/` | focused correspondence tests | not a scientific qualification |
| `diagnostics/` | representative qualification evidence | **non-result-bearing**, stamped `result_bearing: false` |
| `benchmarks/` | cost and memory measurements | **non-result-bearing** |
| `manifests/` | work-universe and implementation manifests | identity only |

There is deliberately no `results/`, `certificates/` or `production_logs/`
directory, and a focused test asserts that none is created.

## What the implementation actually closes

| Frozen implementation dependency | Status |
|---|---|
| complete derivative dependency propagation `epsD = C(deltaD + k1 epsF + epsS')` | **implemented and tested** |
| certified whole-cell curvature `M_R2` | **implemented for CUSUM**; NOT_IMPLEMENTED for SR |
| exact all-m certified interval assembly, m in {1,2,3,5} | **implemented for CUSUM**; NOT_IMPLEMENTED for SR |
| the 17,978-obligation work universe, ordering, hashing, replay | **implemented and tested** |
| floor sharding and resume admission | **implemented and tested** |
| representative complete cover ledger | **computed for CUSUM** |
| 256 / 384 / 512-bit numerical diagnostic | **measured** |
| full cost and memory model under the 1126 CPU-h cap | **CUSUM measured, SR not measurable** |
| complete SR raw-variable DAG | **NOT_IMPLEMENTED** |
| two detector far-field certificates | **NOT_IMPLEMENTED** |

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for the evidence and
the governance verdict.

## How the whole-cell certificate is constructed

The frozen ERROR_ALGEBRA requires curvature bounds that hold **uniformly on the
whole cell**, not at sampled points. The obvious route -- substituting an Arb
ball for `e` into the frozen recentred-Hermite / Bernstein residual machinery --
is rigorous but numerically useless. Measured on the frozen cover:

| cell | rho | point residual at e0 | interval-e residual |
|---|---|---|---|
| CUSUM 0 | 2.54e-04 | 3.69e-06 | 1.46e+42 |
| CUSUM 325 | 9.62e-02 | 1.96e-05 | 2.29e+60 |

The frozen order-120 series is evaluated against z-powers up to `(11/2)^121`;
any interval width destroys the cancellation that makes the point residual
small. That construction cannot certify anything.

What is used instead is the mean-value extension that ERROR_ALGEBRA sections 1-3
explicitly authorise. Every candidate is a state-only polynomial that is
constant in `e` across the cell, so

```text
r(x;e) - r(x;e0) = int_{e0}^{e} d_s r(x;s) ds ,    |e - e0| <= rho
sup_{x, e in cell} |r(x;e)| <= sup_x |r(x;e0)| + rho * Env
```

where `Env` is a finite sum of (certified operator norm) x (certified candidate
sup norm). The operator norms are whole-line absolute Gaussian moments --
`k_0 <= 1`, `k_1 <= 2 phi(0)`, `k_2 <= 4 phi(1)`, `k_3 <= 2 phi(0) + 8 phi(sqrt 3)`,
each also capped by the Cauchy-Schwarz bound `sqrt(i!)`, with the z-weighted
operator handled through `|z| = |y - e|`. Nothing is sampled, nothing is a
finite difference, and `M_2 = 8 phi(1) - 2 phi(0)` independently reproduces the
`1.13788` constant already frozen in the raw-variable certifier.

This bounds the residual simultaneously at every `e` in the cell. It is a
whole-cell certificate.

## Running it

```bash
# focused tests (fast)
PYTHONDONTWRITEBYTECODE=1 level4/.venv/bin/python -m pytest \
    level4/closure_proofs/p5y_k1_cover_ledger_implementation/tests -q

# one representative cell (~20 CPU-minutes)
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 level4/.venv/bin/python \
    level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/qualify.py \
    --detector CUSUM --cell 221 --bits 256 --out /tmp/cell221.json

# self-audit
PYTHONDONTWRITEBYTECODE=1 level4/.venv/bin/python \
    level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/audit_impl.py
```

`scipy` is required only by the frozen non-rigorous candidate solver that
`ra_certifier` imports at module load. No certified path in this namespace uses
it: `cusum_layer1.dyadic_candidate` is a numpy-only reimplementation of the
frozen dyadic rounding, and a focused test asserts it is byte-identical to the
frozen one.

## What this namespace may not do

It may not write into the frozen successor namespace, relax any threshold,
budget, precision, cap or obligation, narrow the frozen scientific scope,
subdivide the frozen cells, run production, or declare production readiness.
Production readiness is reserved for a later independent adjudication.
