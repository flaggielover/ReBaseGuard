# Authoritative-threshold Arb rigor-upgrade attempt

**Threshold label:** `A=520.886133602749`  
**Exact code-correspondence rational:**
`4581762885148045/8796093022208`  
**Precision:** 192 bits  
**python-flint:** 0.9.0  
**Decision:** `OPEN — NO RIGOROUS SR GAMMA INEQUALITY CERTIFIED`

## 1. What was recomputed

No historical numerical enclosure or candidate coefficient was transferred.
The producer recomputed:

- `log(A)` and `log(1+A)` from the exact runtime rational;
- the invariant live-state sum/product enclosure;
- the nonreset coordinate floor and minimum continuation width;
- the directly derived forcing threshold and its Gaussian probability;
- a new degree-16 spectral candidate at the authoritative threshold;
- exact dyadic coefficient serialization at scale `2^44`; and
- three representative outward-rounded interval residual cells.

The exact geometry includes:

| Quantity | Arb enclosure / value |
|---|---:|
| `log(A)` | 6.25553146432147319… |
| `log(1+A)` | 6.25744942922713562… |
| invariant sum cap | 6.71724248125009169… |
| nonreset coordinate floor | 0.000706007647120927… |
| minimum continuation width | 6.79382044739285470… |
| forcing bound `log(A)+1/2` | 6.75553146432147319… |
| one-step forcing probability | 1.42312618477e-11 |
| resulting crude one-step resolvent upper bound | 7.02678378557e10 |

All analytic geometry checks passed under outward rounding.

## 2. Fresh candidate

The newly solved midpoint-collocation candidate gave

```text
Gamma_candidate = 17.290838801294704
float validation residual_a = 5.23e-7
float validation residual_b = 8.08e-6
condition number = 1913.90.
```

After exact dyadic serialization, Arb evaluation of the candidate at reset was
`17.290838801294967…`.  This is an exact evaluation of the candidate, not an
enclosure of the true fixed point or of `Gamma_SR`.

## 3. Representative interval residuals

Raw positive-measure interval partitions were evaluated on three width-`1/32`
state cells with 256 innovation partitions:

| Cell | residual-`a` width upper | residual-`b` width upper |
|---|---:|---:|
| reset patch | 0.36373 | 2.91316 |
| plus-boundary patch | 0.31414 | 2.61089 |
| symmetry diagonal | 0.04549 | 0.54114 |

The widths reproduce the known dependency-loss obstruction: raw interval
boxes do not preserve the cancellation between the candidate and its Bellman
image.  These cells are rigorous local probes, but they do not enumerate or
cover the continuum reachable enclosure.

## 4. Why certification remains open

A successful certificate requires a Taylor/Bernstein residual architecture
that symbolically preserves cancellation, plus all of the following:

1. an exact-rational global patch cover of the reachable enclosure;
2. explicit inclusion of the isolated reset point;
3. certified global suprema `epsilon_a` and `epsilon_b` over every patch;
4. a certified resolvent bound suitable for error propagation;
5. complete propagation of both coupled residual errors to `b(0,0)`;
6. a final outward-rounded `Gamma_SR` interval with lower endpoint strictly
   above two; and
7. an independent full-certificate auditor that reconstructs the critical
   operator, cover, remainder, and propagation claims.

Items 1--7 were not completed.  The crude forcing resolvent is mathematically
valid but far too loose to turn the representative residual widths into a
useful global error budget.  Neither the high candidate midpoint nor the
Monte Carlo evidence can fill these gaps.

## 5. Independent audit

`certificate/audit_arb_attempt.py` does not import producer functions.  At 256
bits it reconstructs the invariant sum cap by the algebraically rearranged
formula

```text
exp(C) = e A (A+1) / (e A-(A+1)),
```

and verifies overlap with the producer enclosure.  It also reconstructs the
candidate digest, checks exact antisymmetry/symmetry of the dyadic coefficient
matrices, verifies the authoritative threshold ratio and hex value, and
requires every absent global-certificate field to remain false.  The audit
passed, but its target is the honesty and consistency of the OPEN attempt; it
is not a Gamma certificate audit.

## 6. Status boundary

The only allowed conclusion is:

```yaml
derivative theorem: CLOSED after final repository verification
Gamma_SR > 2: CONFIRMATORY NUMERICAL
rigorous SR local-instability certificate: OPEN
```

No SR instability statement is certified or rigorous in this track.  The
non-blocking OPEN result does not alter the meaning of
`SR-DERIVATIVE-CLOSED`.

