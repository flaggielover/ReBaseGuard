# P5X — CUSUM Global Production Cover: binding pre-result checkpoint

**Frozen before any production result exists.** This checkpoint does **not**
change P5X's final governance status, which remains `PARTIAL`.

```text
P5_ORIGINAL_VERDICT = PARTIAL          (immutable)
P5X_FINAL_VERDICT   = PARTIAL          (immutable; this run cannot produce CLOSED)
R8                  = FAIL             (immutable)
SR global G3        = OUT_OF_BUDGET    (frozen; no SR work in this task)
```

---

## 0. DISCLOSURE, BEFORE ANY COMPUTE — `m > 1` HAS NO CERTIFIER

The brief's premise is that "the CUSUM production cover is load-bearing,
affordable, and was never actually run". That is **only true for `m = 1`.**

`ra_certifier.py` states its own scope in its first line: *"R-A' certified
enclosure of `R_{CUSUM,m=1}(e)` over a cell."* A search of every `.py` file in
the P5X namespace finds the `m > 1` backward-function machinery (`h_j`, `S_j`)
**only** in `feasibility/fredholm_probe.py`, a Phase-1 feasibility probe — never
in a certifier. `P5X-T1(c)` describes the construction; it was never
implemented.

Therefore:

* `m = 1` can be run now with the validated R2/R-A' certifier;
* `m = 2, 3, 5` **cannot be run at all** without building new certifier code,
  which §3 forbids ("Do not invent a new CUSUM certifier");
* by §6, `G3 CUSUM` passes only if **all** `m in {1,2,3,5}` are
  `PROVED_ALL_CELLS`. Hence **`P5X_CUSUM_GLOBAL_G3` cannot exceed `INCOMPLETE`
  in this task**, whatever `m = 1` returns.

This run therefore produces the strongest affordable production evidence for the
`m = 1` subline. It is recorded as such and not as a CUSUM-global result.

## 1. Source and certifier version

```text
source commit          c6a82cc0a57d505a429ab2f8291f1a17c756fdbc
certifier              compute_optimization_r2/r2_certifier.py (R2, validated)
                       + certified_method_repair_ra/ra_certifier.py (R-A')
resolvent              compute_optimization_r1/drift_minorant.py
                       drift_monotone_resolvent  (drift-explicit monotone
                       Bellman minorant, one-sided k -> k - |e|)
range bound            compute_optimization_r2/fast_range.py (R2 C2)
precision              RA.BITS = 256; Taylor order N = 120; candidate degree 12
```

Unchanged: detector definition, convention A, `[0,12]`, the recurrence, the
candidate construction, `TAYLOR_N`, `DEGREE`, `QUADRATURE`, `SCALE_BITS`,
`DEPTH_LADDER`, `DEPTH_BUDGET`.

## 2. Scope

```text
detector   CUSUM (two-sided, k = 1/2, h = 5)
m          1                     (2,3,5 have no certifier -- see §0)
moment     FIRST only, with the derivative equation
e domain   [0, 12];  e < 0 by oddness P5-T3;  [12, inf) by P5X-T3
second moment                NOT RUN (explicitly excluded by §11)
```

## 3. Cover rule (deterministic, frozen)

`DEN = 10^7`, `a = 2 phi(0) = 2/sqrt(2 pi)`,
`b2 = 4 e^{-1/2}/sqrt(2 pi)`.

Walk `lo` from `0` to `12`. At each outer cell:

```text
C        = drift_monotone_resolvent(lo)      -- exact rational left endpoint;
                                                the minorant is monotone in the
                                                drift, so C(lo) bounds C on the cell
h_max    = 1/(4 a C)
hnum     = largest integer with hnum/DEN <= h_max AND
           C(2 a h + b2 h^2) <= 1/2  at h = hnum/DEN
n_sub    = 8   (matches the R2 benchmark)
span     = 2 * n_sub * hnum       -- so the cell tiles EXACTLY in rationals
cell     = [lo, lo + span/DEN], clipped at 12
```

Each sub-cell is certified at its exact rational centre. `c2 = 113788/100000 +
b2 * e_hi(cell)`, exactly as in the R2 benchmark with the cell's own upper
endpoint.

## 4. Per-sub-cell enclosure (verbatim from the R2 benchmark)

```text
G0     = sup_cheb_g  + C delta
G1     = sup_cheb_dg + C delta_d
S2     = 2 C (2 a G1 + b2 G0 + b2 h G1 + c2)
e_rng  = mid(e_lo,e_hi) +/- (e_hi-e_lo)/2
g_e    = ghat_origin  +/- C delta
dg_e   = dghat_origin +/- C delta_d
r_e    = e_rng + g_e + [+/- h] dg_e + [+/- h^2 S2/2]
R(cell) = union over sub-cells of r_e
```

## 5. Pass criterion — the theorem consumer, not `F3`

```text
For every accepted cell E:   ABS_MAX(E) = max(|lo|,|hi|)  <  2   STRICTLY
G3 margin = 2 - ABS_MAX(E)
```

`F3 = 0.2` is **not** applied: the F3 provenance audit established it as a
pre-result engineering stop-gate, not the theorem consumer. The achieved
half-width is **reported**, not gated. No safety margin is invented: the
inequality is used as written, with strictness required.

Per-`m` classification: `PROVED_ALL_CELLS` / `FAIL` / `INCOMPLETE`. No cell may
be inferred; every cell in the tiling must carry its own enclosure.

## 6. Far field

`[0,12]` is certified by the finite cover above. `[12, infinity)` is closed by
`P5X-T3` (exact), which gives a decreasing majorant with `|R_CUSUM(±10)| <=
3.2e-5`. `e < 0` by oddness `P5-T3`. The union must be recorded with no gaps:
consecutive cells share endpoints exactly in rational arithmetic.

## 7. Resource STOP rule

```text
projected m=1 first-moment cost   3.7 CPU-hours
   (361 sub-cells by trapezoid over the measured C(e), at the R2-measured
    0.010146 CPU-h per sub-cell)
HARD STOP if the running total exceeds 500 CPU-hours -- abort and report,
do not silently exceed.
```

Measured `C(e)`: `1232.84` at `e=0`, `567.16` at `0.1`, `207.75` at `0.25`,
`16.94` at `1`, `2.18` at `4`, `1.0000` at `>= 10`.

## 8. Pre-run correspondence (already performed)

`drift_monotone_resolvent(24,100)` reproduces
`C = 220.7075187096823143058125152854812294891688046029854141728 +/- 7.14e-5`,
matching the R1/R2 recorded `220.708`. The recorded R2 benchmark enclosure is
`[-1.584973380499857, -1.567644374839216]`, half-width `0.008664502830320444`,
`n_sub = 8`.

## 9. Failure handling

No post-result tuning. Any failing cell is classified `C-F1`..`C-F7` and
preserved. No threshold is weakened after a result.

## 10. Governance

A `PROVED_ALL_CELLS` outcome for `m=1` records
`P5X_CUSUM_M1_G3 = PROVED_ALL_CELLS` in the evidence ledger. It does **not**
change `P5X_FINAL_VERDICT = PARTIAL`, because SR global `G3` remains
out-of-budget, second moments are unrun, `m = 2,3,5` have no certifier, and
`G5`/`G7`/`G9`/`G13` remain open.
