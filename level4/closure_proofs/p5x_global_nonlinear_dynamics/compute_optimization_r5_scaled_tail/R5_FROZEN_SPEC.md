# P5X R5 — FROZEN specification

**Frozen at Checkpoint G, before the scaled kernel is implemented or run.**
No criterion, threshold, formula, regime rule or class below may be edited after
a result exists. Bug fixes are permitted in code only.

---

## 1. Frozen configuration — deliberately the R4 `P3` case, not an easier one

```text
bits              = 192              (same as R4 P3)
candidate_degree  = 16               (n; same as R4 P3)
patch             = (17, 11)         (same frozen state patch)
state             = patch centre, point state   (same as R4 P3)
e                 = 1/4              exact rational
k range           = -16 .. +16       all 2n+1 values
probe candidate   = c_ij = 1/(1+i+2j)   (same as R4 section 4, extended to n=16)
A                 = 4581762885148045 / 8796093022208    exact
```

This is exactly the configuration that produced R4's `2.1356e17`. The
representative-patch runtime `Q7` is measured on the **ball** patch `(17,11)`,
matching R4's `t_patch = 0.399 ms`.

## 2. Frozen formulas and regime rule

```text
E(x) = k x - (x+e)^2/2
T(x) = exp(E(x)) * erfcx(|x+e-k| / sqrt(2))

selector (k exact integer; l,u balls):
    if  (u+e-k).upper() <= 0 :  B ->  I_k = [T(u) - T(l)] / 2
    elif (l+e-k).lower() >= 0 :  C ->  I_k = [T(l) - T(u)] / 2
    else                      :  D ->  I_k = exp(k^2/2-ke) * [Phi(b) - Phi(a)]
                                      Phi(b) = 1 - erfc(b/sqrt2)/2   (b >= 0 branch)
                                      Phi(a) = erfc(-a/sqrt2)/2      (a <= 0 branch)

erfcx branch:
    t <= 2 :  exp(t^2) * erfc(t)
    t >  2 :  hypgeom_u(1/2, 1/2, t^2) / sqrt(pi)
```

## 3. Frozen amplification metric

Identical in definition to R4 `P3`, so the comparison is honest:

```text
amplification = rad( sum_k G_k I_k ) * 2^bits
```

evaluated at the §1 configuration (point state, n = 16, e = 1/4, 192 bits).

```text
R4 reference value  = 2.1356e17
R4 frozen threshold = 1e12          NOT weakened
```

## 4. Frozen gate `Q1`-`Q10` (conjunctive; all must pass)

```text
Q1  exact algebraic correspondence.
    For EVERY k in -16..16, the R5 scaled interval must OVERLAP the R4 direct
    interval.  Both are rigorous Arb enclosures of the same exact I_k, so two
    correct evaluators MUST overlap; failure to overlap is a genuine defect.
    This is a rigorous-vs-rigorous test.

Q2  rigorous Arb containment.
    The R5 summed interval must OVERLAP the R4 summed interval (rigorous vs
    rigorous), AND the R5 interval must be a SUBSET of the R4 interval, since
    R5 is the refinement of the same enclosure.

Q3  amplification <= 1e12   (the unweakened R4 threshold)

Q4  huge_tiny_intermediate = NO.
    No product is constructed in which one factor has |log10| > 20 and the
    other has |log10| < -20.  Instrumented by counter, not by inspection.

Q5  z_panels = 0                    (instrumented)

Q6  softplus_approximations = 0     (instrumented)

Q7  runtime <= 2.0 ms per representative ball patch

Q8  no empirical monotonicity

Q9  e remains an exact rational (ball radius exactly 0) through the symbolic layer

Q10 the R4 xi/zeta recurrence is unchanged: xi_kernel.py's recurrence, live
    limits and G_k assembly are imported and reused, not reimplemented.

GATE = PASS iff Q1 and Q2 and ... and Q10.
```

## 5. Correspondence criterion replacing D11 — directionality fixed

```text
RIGOROUS  vs  RIGOROUS   (binding):
    R5 scaled interval   vs   R4 direct interval        -> Q1, Q2
    Both enclose the same exact I_k.  Overlap is required; containment
    R5 subset R4 is required at the summed level.

DIAGNOSTIC ONLY (never a containment obligation):
    composite Simpson quadrature, and the brute-force simulation of the frozen
    y-space recurrence.  Both are NON-RIGOROUS: their truncation error is not
    enclosed.  They are reported as agreement ratios and may not, on their own,
    fail or pass the gate.

Explicitly forbidden: widening the R5 interval so that it contains a
non-rigorous Simpson value.  That would manufacture a fake PASS and is the
inverse of the D11 error, not a fix for it.
```

## 6. Frozen success classes

```text
amplification:
    > 1e12         R5_P3_FAIL
    1e9  .. 1e12   R5_P3_PASS
    1e6  .. <1e9   R5_P3_STRONG_PASS
    < 1e6          R5_P3_BREAKTHROUGH

runtime per patch:
    <= 0.75 ms         EXCELLENT
    > 0.75 .. 2.0 ms   ACCEPTABLE
    > 2.0 ms           COST_FAIL

projected SR (formula 835*1210*t_patch*2*43/3600, unchanged from R4):
    > 100 CPU-h    R5_NOT_ENOUGH
    25 .. 100      R5_USEFUL
    10 .. 25       R5_STRONG
    <= 10          R5_BREAKTHROUGH

projected total (SR + 146 CUSUM):
    <= 500 CPU-h   PRODUCTION_COST_READY
    <= 250 CPU-h   STRONG_PRODUCTION_COST_READY
```

## 7. Frozen precision sweep

`192, 256, 320, 384, 512` bits. The candidate MUST be rebuilt at each precision
(R4's diagnostic was initially wrong because `rational(1,3)` built at 192 bits
carries a `2^-192` radius that dominates at higher precision). Record
amplification, interval width, runtime. A genuine repair must reduce the
amplification *metric itself*, not merely hide it under more bits.

## 8. Frozen self-test (must pass before the gate)

```text
S1  central regime (D) agrees with R4 direct
S2  deep negative tail (B) agrees with R4 direct
S3  deep positive tail (C) agrees with R4 direct
S4  near-equal tail difference behaves per the section 6 bounds
S5  both charts (plus and minus) exercised
S6  k positive, negative and zero
S7  boundary regime switching: k at and either side of ceil(u+e) and floor(l+e)
S8  R4 brute-force y-space reference (DIAGNOSTIC ONLY)
S9  high-precision quadrature (DIAGNOSTIC ONLY)
S10 alarm / live mass unchanged: live_limits identical to R4's
S11 erfcx branch agreement at t = 2 (the branch seam)
If any of S1-S7, S10, S11 fails: STOP.
```

## 9. Frozen retry ladder

**There is none.** If `Q3` still exceeds `1e12`, the result is `R5_P3_FAIL` and
is reported as such, with the residual classified as one of
`TAIL_DIFFERENCE_CANCELLATION`, `REGIME_SWITCH_DEFECT`,
`ARB_SPECIAL_FUNCTION_LIMITATION`, `INTERVAL_DEPENDENCY`, `FORMULA_DEFECT`,
`OTHER`. No post-result tuning.

## 10. Frozen prediction (recorded before implementation)

```text
Q1, Q2      PASS
Q3          amplification 1e0 .. 1e4   ->  R5_P3_BREAKTHROUGH
Q4          NO
Q5, Q6      0, 0
Q7          0.5 .. 1.5 ms   ->  ACCEPTABLE (hypgeom_u is dearer than erf)
Q8, Q9, Q10 PASS
gate        PASS
projected SR   12 .. 36 CPU-hours  ->  R5_STRONG or R5_USEFUL
full-cell prototype  authorized and expected to run
```

Basis: the `k = +-16` terms contribute `3.4e-41` of the `3.4022e-41` measured
radius, and the erfc branch improves their relative radius from `1.7e-32` to
`4.6e-56` — a factor `~3.7e23`. If nothing else degrades, `rad(sum)` should fall
to roughly `1e-57`, i.e. amplification of order `1`.

Named risks: (i) `hypgeom_u` may be markedly slower than `erf`, threatening
`Q7`; (ii) `hypgeom_u` near `z -> 0` may lose precision, mitigated by the
`t <= 2` branch; (iii) some *other* `k` may dominate the radius once `k = +-16`
is fixed, capping the gain well above the predicted amplification.
