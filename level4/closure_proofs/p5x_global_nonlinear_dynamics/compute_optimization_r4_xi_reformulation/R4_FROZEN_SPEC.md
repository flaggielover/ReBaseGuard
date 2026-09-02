# P5X R4 — FROZEN specification

**Frozen at Checkpoint F, before any gate is implemented or run.**
Nothing below may be edited after a result exists. Bug fixes are permitted only
in code, never in this file's criteria, thresholds, formulas or classes.

---

## 1. Frozen configuration

```text
bits              = 192            (same as R3)
candidate_degree  = 16             (n; same as R3)
patch             = (17, 11)       (same frozen state patch as R3)
e                 = 1/4            exact rational (same as R3)
production var    = zeta = (xi - 1)/A  on [0,1]
A                 = 4581762885148045 / 8796093022208     exact
c_SR              = log A + 1/2
```

Held identical to R3 **on purpose**: R4 must be measured against R3 with a single
variable changed — the elimination of the `z`-panel dimension.

## 2. Frozen cost formula (identical in shape to R3's, panel factor removed)

```text
SR_total_CPU_hours = 835 * 1210 * t_patch * 2 * 43 / 3600
```

`835` drift sub-cells, `1210` state patches, `2` charts, `43` certified functions
(`4m-2` first-moment plus `m(m+1)` second-moment, the corrected multiplier).
R3's formula was the same with `t_patch = n_z * t_panel = 128 * t_panel`.

## 3. Frozen gate criteria — `P1`-`P8`

```text
P1  xi/zeta recurrence exactness.
    1 + xi*e^{z-1/2}  and  exp(softplus(y+z-1/2))  must overlap as balls, with
    relative half-width <= 1e-40, at the frozen points
    (y,z) in {(0.7,1.3), (0,-5/2), (31/5,2/5)}.
    zeta' = (1/A+zeta)E must equal (xi'-1)/A likewise.

P2  closed-form kernel correctness.
    For the frozen probe candidate (§4) the closed form of §14 must CONTAIN a
    high-order quadrature reference, and its relative half-width must be
    <= 1e-12.

P3  conditioning at production degree.
    At n = 16 over the full domain, the dependency amplification
    (max output coefficient radius) / (2^-bits) must be <= 1e12.

P4  panel elimination, the decisive criterion.
    measured t_patch <= 0.3314531805 seconds
    (the identical per-patch budget R3 used; it is exactly the 8000-CPU-hour
    line under the §2 formula).

P5  structural zero-panel property.
    The implementation must perform 0 z-panel subdivisions and 0 softplus
    Taylor expansions on the certified path, asserted by instrumented counters,
    not by inspection.

P6  exact rational drift.
    e must remain an exact rational through the symbolic layer; no interval e
    may enter it.

P7  atom neutrality.
    zeta' > 0 strictly for every finite z, and the alarm predicate must agree
    with the frozen y-space predicate on both sides of the boundary.

P8  no empirical monotonicity is relied upon anywhere.

GATE = PASS  iff  P1 and P2 and P3 and P4 and P5 and P6 and P7 and P8.
```

Any single failure is a `FAIL`, reported as such. `P4` in particular will not be
re-budgeted after measurement.

## 4. Frozen probe candidate for `P2`

Bidegree `(3,3)`, coefficients frozen here:

```text
c[i][j] = 1/(1 + i + 2j)   for  0 <= i,j <= 3
```

Quadrature reference: composite Simpson in `z` on `(l,u)` with `40000`
subintervals at `256` bits.

## 5. Frozen classes

```text
speedup class, by projected SR CPU-hours from §2:
    <= 1000        R4_BREAKTHROUGH
    1000 - 3000    R4_STRONG
    3000 - 8000    R4_USEFUL
    8000 - 15000   R4_PARTIAL
    > 15000        R4_NOT_ENOUGH

campaign viability, projected SR + 146 CUSUM CPU-hours:
    <= 1000        STRONGLY_VIABLE
    1000 - 5000    VIABLE
    5000 - 12000   MARGINAL
    > 12000        MORE_OPT_REQUIRED

scientific class (asserted, and re-checked by the gate):
    CERTIFIED_COORDINATE_CHANGE + CERTIFIED_KERNEL_REFACTOR
    XI_SECOND_MOMENT_EXTENSION = DIRECT_WITH_SPECIAL_FUNCTIONS
```

## 6. Frozen prediction (recorded before running; R3's prediction missed 4 of 5)

```text
P1              : PASS, exact to working precision
P2              : PASS, relative half-width  1e-16 .. 1e-14
P3              : PASS with margin (the zeta rescaling was adopted for this)
t_patch         : 1.0 .. 4.0 ms
P4              : PASS by roughly two orders of magnitude
projected SR    : 25 .. 100 CPU-hours  ->  R4_BREAKTHROUGH
campaign total  : 170 .. 250 CPU-hours ->  STRONGLY_VIABLE
gate            : PASS
```

Chief risks to this prediction, named in advance: (i) `Phi`-difference
cancellation at large `|k|` could inflate `P2`/`P3` beyond the stated bands;
(ii) `e^{k^2/2}` reaches `~4e55` at `k = 16` and could dominate the ball radius;
(iii) `t_patch` could be worse than predicted if Arb's `erf` at 192 bits is
much slower than its elementary functions. If any of these bites, the gate
FAILs and R4 is reported as NO.
