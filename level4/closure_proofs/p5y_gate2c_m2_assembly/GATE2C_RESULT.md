# P5Y GATE 2C — PILOT-M2-ASSEMBLY result

```text
P5Y_GATE2C_DECISION = M2_ASSEMBLY_INCOMPLETE_EXTERNAL
STOP_FIRED          = YES  (S1: cumulative result-bearing CPU reached the cap)
CPU USED            = 723 CPU-seconds against a frozen 720 s (0.20 CPU-hour) cap
MEASUREMENT         = NOT COMPLETED.  No timing, no correspondence, no cost band.
BINDING = NO ; PRODUCTION RUN = NO ; CHECKPOINT = NO
```

The frozen cap was enforced mechanically by an external watchdog polling the
worker's CPU time every 5 s and killing it the first time CPU reached 720 s. It
fired at 723 s, mid-way through the `m = 2` certification. **No result file was
written and no cost ratio was measured.** The cap was not extended.

---

## 1. What was established (algebra, before any timing)

The exact raw-variable `m = 2` assembly, derived from `P5X-T1(c)` and checked
against the probabilistic decomposition:

```text
m = 1:  R_{CUSUM,1}(e) = F_0(x0)
m = 2:  R_{CUSUM,2}(e) = (1/2)[ F_0(x0) - S_0^raw(x0) + F_1(x0) ] + S_0^raw(x0)
                       = (1/2)[ F_0(x0) + F_1(x0) + S_0^raw(x0) ]

against  R_2 = E[raw_tau; tau=1] + (1/2)E[raw_tau; tau>=2] + (1/2)E[raw_{tau-1}; tau>=2]
with     S_0^raw(x0) = E[raw_1; tau=1],  F_0(x0) = E[raw_tau],
         F_1(x0)     = E[raw_{tau-1}; tau>=2]                        -- identical.
```

Structure of the increment, confirmed:

```text
S_0^raw = phi(u+e) - phi(l+e)              closed form, SHARED with m=1
h_1     = 1 - Phi(u+e) + Phi(l+e)          closed form, no solve
d_e h_1 = -S_0^raw                         exact identity
S_1^raw = K_{z,e} h_1 + e K_e h_1          kernel-derived source
F_1     = (I - K_e)^{-1} S_1^raw           ONE new resolvent solve
```

`m = 2` adds **one resolvent solve plus its `e`-derivative and no new solve
architecture**. `F_0` is reused by identity; no duplicate solve is created.
That part of Gate-1's MSHARE picture is intact.

## 2. What was NOT established

* the `m > 1` per-function cost ratio — **unmeasured**;
* correspondence of `R_{CUSUM,2}(1/4)` against the Monte Carlo — **never reached**;
* any updated P5Y CPU band — **the Gate-2B bands stand unchanged**.

## 3. Why the cap fired — diagnosed, with measured evidence

A 0.57 CPU-second static measurement of the polynomial representations:

| object fed to `_kernel_polynomials` | bidegree | terms |
|---|---|---|
| `F_0` candidate (what `m=1` uses) | **(12, 12)** | 169 |
| `h_1` (what this pilot's `m=2` used) | **(121, 121)** | 243 |
| `d_e h_1 = -S_0^raw` | (120, 120) | 241 |

The `m = 2` source chain applied `_kernel_polynomials` **six times** to these
degree-121 objects. That routine substitutes the argument, multiplies by the
degree-120 `phi` series and integrates symbolically in `z`, so a 10x higher
degree per variable inflates every intermediate `TriPoly` and roughly doubles
the `z`-degree.

```text
CAUSE CLASS = IMPLEMENTATION_DEFECT (in this pilot, not in the architecture)
```

`h_1` **is** closed form. Being closed form did not make its polynomial
representation small. This is the same lesson class as Gate-2A's
exponential-Gaussian identity needing 400+ bits: **mathematically exact is not
computationally cheap in the chosen representation** — twice now in this
campaign, and worth carrying forward as a standing rule.

## 4. Inferred lower bound — an inference, not a measurement

From the phase ordering (resolvent `~0.4 s`, then two `m=1` repeats at Gate-1's
measured `30.85` CPU-s each `~62 s`), at least `660` CPU-s were consumed by at
most two `m=2` repeats without completing:

```text
ratio_incremental  >=  ~10x     for the naive degree-121 implementation
```

This is inferred from ordering plus a prior measurement. **No timing was
recorded before the kill**, so it is not a measurement and must not be quoted as
one. It is nonetheless enough to say the naive implementation is far outside the
`STRONG`/`MODERATE` bands.

## 5. The repair — designed, deliberately NOT applied

Gate-1's MSHARE accounting already counts `h_j` and `S_j` as **certified
functions**, each with its own exact-dyadic candidate. This pilot departed from
that accounting by feeding the *exact* series into the kernel instead of a
candidate. The repair is therefore to return to the accounting the cost model
actually rests on:

> build a **degree-12 exact-dyadic candidate `hhat_1`** with its own certified
> residual, and apply the kernel to `hhat_1` — never to the exact degree-121
> series. Every kernel application in the `m=2` chain then acts on a degree-12
> object, exactly as `m=1` does.

It is **not applied here**: the frozen rules forbid adaptive repair after `T2`
and forbid extending the cap after results. A test asserts `m2_certifier.py`,
`m2_assembly.py` and the preregistration are byte-identical to their `T1`
hashes, so no post-`T2` mutation occurred.

**It is not claimed that the corrected ratio is acceptable.** That is exactly
what the successor gate must test, and it may still fail.

## 6. Consequences

`CHECKPOINT_READY = NO`. The first-moment production cost model retains an
unresolved input — the `m>1` per-function cost — and Gate-2B's conservative and
worst bands, which exist precisely to hedge it, cannot be narrowed. The
Gate-2B central estimate of `3,092` CPU-hours still assumes `ratio_per_unit = 1.0`,
and this gate did not test that assumption; it only showed that one particular
implementation of the `m=2` source violates it badly.

Nothing here touches `K2` `s_min`, `K3` `M_2`, `K4` `H2` or `K5` `H3a`, which
remain unresolved. P5, P5X, Gate-1, Gate-2A and Gate-2B are untouched.
