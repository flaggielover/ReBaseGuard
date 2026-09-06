# P4Z Mac runtime contract — human-readable summary

```text
P4Z_NUMERICAL_HOST  = LOCAL_MAC
AWS_CPU_USED_BY_P4Z = 0
campaign isolation  = MAC_ONLY
role                = RESULT_BEARING_HOST
runtime_hash        = fb9ec8f26ce46c4a7e566dc58683d2a3d3da866cae475aeca9ba35ff729f7410
```

The machine-readable contract is `production/mac_runtime_contract.json`.  It is
self-hashing: `runtime_hash` covers every field except itself, and the driver
rebuilds the contract at start-up and refuses to run on any drift.

## Host

| | |
|---|---|
| architecture | `arm64` |
| CPU | Apple A18 Pro |
| cores | 6 physical, 6 logical — **2 performance + 4 efficiency** |
| SMT | False |
| memory | 8 GiB |
| cache line | 128 bytes |
| OS | macOS 26.5.2 build 25F84 |
| kernel | `25.5.0` |

## Toolchain

| | |
|---|---|
| Python | 3.14.5 (v3.14.5:5607950ef23, May 10 2026 07:38:09) |
| compiler | Clang 21.0.0 (clang-2100.0.123.102) |
| numpy | 2.5.3 |
| scipy | 1.18.1 |
| pytest | 9.1.1 |
| BLAS / LAPACK | **accelerate** / accelerate, detected by system |
| numpy built by | clang 15.0.0 |

**The threading variable that actually binds on this host is
`VECLIB_MAXIMUM_THREADS`.**  numpy here is built against Apple
Accelerate, which does **not** honour `OMP_NUM_THREADS` or
`OPENBLAS_NUM_THREADS` — it threads through Grand Central Dispatch.  The
contract pins all of them anyway, so it stays correct if the wheel is ever
rebuilt against OpenBLAS or MKL, and the driver *measures* the CPU-to-wall
ratio rather than relying on the argument that the kernel makes no BLAS call.

## Pinned environment

Every result-bearing process must start with exactly:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONHASHSEED=0 LC_ALL=C
```

`runtime_contract.enforce_environment()` fails closed if any of these is
missing or different.  Floating point is IEEE-754 binary64, round to nearest;
no P4Z code changes the rounding mode, enables FTZ/DAZ, or uses fast-math.

## Worker and thread freeze

Frozen **before** Stage-0, and not revisitable after seeing any scientific
value.

| workers | CPU-s | CPU inflation | wall | speedup | parallel efficiency |
|---|---|---|---|---|---|
| 1 | 6.59 | ×1.00 | 7.10 s | 1.00 | 1.00 |
| 2 | 9.58 | ×1.45 | 6.15 s | 1.15 | 0.58 |
| 4 | 11.77 | ×1.78 | 4.06 s | 1.75 | 0.44 |

```text
FROZEN  workers = 1,  BLAS threads = 1
```

The measured single-worker CPU-to-wall ratio is
0.93, which is the empirical confirmation that the
estimator kernel is single threaded — it is element-wise numpy ufuncs and axis
reductions with no BLAS call on any path.

**Why one worker and not six.**  Total CPU-seconds *inflate* with worker count
on this chip, because extra work lands on efficiency cores that need far more
CPU-seconds for the same computation.  CPU-hours are the **capped** resource
(12.0 h), so parallelism here spends the budget
that gates the campaign in order to buy wall time.  At four workers the campaign
would burn ×1.78 the CPU for a
×1.75 wall gain.  One worker also makes every
block's CPU attributable to a single process, which is what the cost accounting
needs.

## What is bound into the scientific hash

The runtime hash above, the producer manifest over the exact path-based TCB,
the estimand contract, the frozen checkpoint, the campaign plan, the Stage-0
freeze, the seed schedule, the fixed 200-block
policy, the finite-difference convention [0.05, 0.025], and every threshold.
Hashing is exclusion based: a field nobody enumerated is hashed, not dropped,
and anything that cannot be canonicalised raises.
