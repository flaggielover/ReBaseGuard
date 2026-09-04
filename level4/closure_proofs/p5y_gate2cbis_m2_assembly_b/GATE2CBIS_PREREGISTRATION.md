# P5Y GATE 2C-bis — PILOT-M2-ASSEMBLY-B preregistration

**NON-BINDING.** A repair-validation pilot for the Gate-2C implementation defect.
Not a new estimand, not a production cover, not a binding checkpoint. Frozen
before any result-bearing execution (T2).

```text
P5_ORIGINAL_VERDICT = PARTIAL   P5X_FINAL_VERDICT = PARTIAL
P5X_CAMPAIGN = ARCHIVALLY_COMPLETE
P5Y_GATE1_DECISION  = GATE1_PASS_ROUTE_B_SUPPORTED      (immutable)
P5Y_GATE2A_DECISION = SR_PRECISION_PASS_256             (immutable)
P5Y_GATE2B_DECISION = SR_COVER_PASS_MEASURED            (immutable)
P5Y_GATE2C_DECISION = M2_ASSEMBLY_INCOMPLETE_EXTERNAL   (immutable; NOT a PASS,
                      and the failed run is preserved, not deleted or hidden)
```

## 0. The single question

Re-run the exact Gate-2C scientific object under the corrected low-complexity
certified-function representation; measure the true `m>1` incremental cost ratio
and perform the frozen independent correspondence check.

## 1. The one allowed architectural change

```text
Every object passed to _kernel_polynomials must be a degree-12 exact-dyadic
certified candidate.        h_1 -> hhat_1 ,   d_e h_1 -> dhhat_1
```
Nothing else changes: same detector, same drift, same `m` set, same estimand,
same assembly, same resolvent, same precision, same correspondence design and
tolerance.

## 2. Compute cap and its derivation

```text
GATE2CBIS_CPU_CAP       = 1260 CPU-seconds = 0.35 CPU-hours   (hard)
GATE2CBIS_CPU_PREFERRED <= 720 CPU-seconds = 0.20 CPU-hours
```
Derived, not inherited: Gate-1 measured `30.85` CPU-s for exactly the `m=1`
certification call, so the two-repeat denominator alone costs `~62` CPU-s; the
repaired `m=2` path makes 9 kernel calls against `m=1`'s 3, so `~3x` per repeat,
`~190` CPU-s for two; plus candidate construction and a `~30` CPU-s Monte Carlo.
Expected total `~300` CPU-s, so `1260` leaves a `4x` margin. **Gate-2C's `720 s`
was a round number rather than a derived one — that was a preregistration error,
and this cap is derived from the known baseline.** This is a new pilot with a new
predeclared cap, not an extension of the old run. The external CPU watchdog is
kept and may not be relaxed after T2.

## 3. Frozen scientific object

```text
detector CUSUM (k=1/2, h=5), inclusive post-update test, Stage-D convention A
e = 1/4 exact rational      m in {1,2}      256 bits, Taylor order 120, degree 12
R_{CUSUM,1}(e) = F_0(x0)
R_{CUSUM,2}(e) = (1/2)[ F_0(x0) + F_1(x0) + S_0^raw(x0) ]
S_0^raw = phi(c-p+e) - phi(m-c+e)      h_1 = 1 - Phi(c-p+e) + Phi(m-c+e)
d_e h_1 = -S_0^raw                     S_1^raw = K_{z,e} h_1 + e K_e h_1
F_1 = (I - K_e)^{-1} S_1^raw
```
The estimand and the assembly are **unchanged from Gate-2C**; a pre-T2 test
asserts the assembly expression is byte-identical in form.

## 4. Frozen degree-12 candidate construction

Both `h_1` and `d_e h_1` are **separable**: each is a constant plus a function of
`p` alone plus a function of `m` alone. So four 1-D candidates suffice:

```text
A(p) = Phi(c-p+e)   B(m) = Phi(m-c+e)   P(p) = phi(c-p+e)   Q(m) = phi(m-c+e)
```
For each, on its interval `[0,5]`:

1. evaluate at the `N+1 = 121` Chebyshev-Lobatto nodes using Arb (`gaussian_cdf`
   / the exact Gaussian density), giving interval enclosures;
2. form the degree-120 Chebyshev interpolation coefficients `a_0..a_120` by
   direct DCT-I summation in Arb;
3. **round `a_0..a_12` to exact dyadic multiples of `2^-50`** — this is the
   exact-dyadic candidate;
4. convert to the monomial basis by the Chebyshev recurrence and the affine map
   `t = (2x-5)/5`, in exact Arb arithmetic.

```text
hhat_1  = 1 - Ahat(p) + Bhat(m)        bidegree (12,12)
dhhat_1 = -( Phat(p) - Qhat(m) )       bidegree (12,12)
```

## 5. Frozen candidate certification residual (rigorous, three named terms)

```text
eps_f = sum_{k=13}^{120} |a_k|                    truncation of the interpolant
      + 2 (5/4)^{121} sup|f^{(121)}| / 121!       interpolation error of degree 120
      + 13 * 2^-50                                exact-dyadic rounding (|T_k| <= 1)
with sup|f^{(121)}| <= 0.4333 sqrt(121!)  (Cramer, the constant already used by
ra_certifier.taylor_remainder).   eps_h = eps_A + eps_B ,  eps_dh = eps_P + eps_Q
```

Propagation into the certificate, added as explicit allowances:

```text
| K_{raw,e}(h_1 - hhat_1) | <= eps_h * E|raw| = 0.79788 eps_h          -> delta
| d_e-source error | <= 2 eps_h + 0.79788 eps_dh                       -> delta'
contribution to the R_2 half-width  =  (1/2) * C * (those allowances)
```

**Frozen adequacy rule (`FAIL_REPRESENTATION` if violated):**

```text
candidate_residual_share = (candidate contribution to the R_2 half-width)
                           / (total R_2 half-width)          MUST BE <= 0.50
```
i.e. the candidate residual may not dominate the enclosure. **Degree 12 is
mandated and may not be raised after results.**

Pre-T0 design calibration, disclosed: a float Chebyshev computation gave
degree-12 tails of `8.9e-7` (`A`), `1.3e-6` (`B`), `2.5e-6` (`P`), `4.0e-6` (`Q`),
implying a contribution near `2e-4` against an expected total near `3e-3`, i.e. a
share near `0.06`. That is the *reason to expect* degree 12 to suffice; the
**decision rests on the rigorously measured residual**, not on this calibration.

## 6. Frozen representation-complexity guard (structural, pre-T2, not timing)

Every `_kernel_polynomials` argument is recorded. Hard failure if any exceeds
bidegree `(12,12)`.

```text
COMPLEXITY_SCORE = sum over kernel calls of
                   (deg_p + 1) * (deg_m + 1) * (z_degree_after + 1)
z_degree_after   = deg_p + deg_m + len(phi_coefficients) + z_weight
MAX_COMPLEXITY_SCORE = 400_000        (frozen)
```
Basis for the threshold: the Gate-1-validated `m=1` path makes 3 calls on
bidegree-`(12,12)` arguments, scoring `~74,000`; the repaired `m=2` path makes 9
such calls, scoring `~222,000`. `400,000` accommodates the repaired path with
`1.8x` headroom and rejects anything structurally larger. **If the score exceeds
the budget, T2 is not entered at all.**

The guard is also evaluated on the *Gate-2C defective* path (statically, from its
recorded bidegrees) purely to record whether it would have been caught.

## 7. Frozen sharing audit

```text
resolvent solves, m=1 : F_0, d_e F_0                    = 2
resolvent solves added by m=2 : F_1, d_e F_1            = 2
candidate/source objects added by m=2 (NOT resolvents)  : hhat_1, dhhat_1,
                                                          S_1^raw, d_e S_1^raw
shared resolvent fraction at m=2 = 2/4 = 0.50
```
Mechanically asserted: `F_0` and `d_e F_0` reused by identity; `hhat_1` is a
certified **source** object, not an independent resolvent; no duplicate `m=1`
solve is created.

## 8. Frozen timing protocol

```text
CERTIFIED_REPEATS = 2 for m=1 and 2 for the m=2 increment    (frozen)
ASSEMBLY_REPEATS  = 5                                        (frozen)
candidate construction is timed separately and IS included in T_incr
```
Report median, min, max, relative spread. Timing affects the cost model only.

## 9. Frozen ratios, classes and which one enters the production model

```text
T_m1   = certified cost of (F_0, d_e F_0)
T_incr = certified cost of everything m=2 adds (candidates + sources + F_1, d_e F_1)
ratio_incremental = T_incr / T_m1          ratio_cold = (T_m1 + T_incr) / T_m1
ratio_source_only / ratio_resolvent_only reported where separable
units_added_by_m2 = 2      ratio_per_unit = ratio_incremental / 2

COST CLASS on ratio_incremental (this brief's frozen bands):
  STRONG <= 1.15 ; MODERATE <= 1.50 ; WEAK <= 2.00 ; HIGH > 2.00
```
**The P5Y production model uses `ratio_per_unit`,** because Gate-1's `24.5x`
already counts functions and the model's assumption is that each function-unit
costs one `m=1` unit. Both numbers are reported and the distinction is stated;
the cost *class* is taken from `ratio_incremental` exactly as this brief bands it.

## 10. Frozen independent correspondence — identical to Gate-2C

Direct Monte Carlo of the frozen detector recursion; touches no operator, no
candidate and no line of the assembly code.

```text
N_CYCLES = 1_000_000    SEED = 20260904    e = 1/4    m = 2
statistic Rbar = raw_tau if tau = 1 else (raw_tau + raw_{tau-1})/2
PASS iff (i) the certified R_2 enclosure intersects [mean - 4 SE, mean + 4 SE]
     AND (ii) |center - mean| <= max(4 SE, 5e-3)
```
Not weakened after T2.

## 11. Predeclared exact-candidate inclusion check (diagnostic only)

At the five fixed states `(p,m) in {(0,0), (5/4,5/4), (5/2,5/2), (15/4,15/4), (5,5)}`
compare the exact degree-121 `h_1` value against the `hhat_1 +/- eps_h` enclosure
and require inclusion. **The degree-121 object is used only here, never in the
kernel path** — a test asserts that.

## 12. STOP rules

```text
S1 worker CPU reaches 1260 s -> kill, write NO completed artifact, STOP_FIRED=YES
S2 any kernel argument exceeds bidegree (12,12)        -> FAIL_REPRESENTATION
S3 COMPLEXITY_SCORE > 400_000                          -> do not enter T2, FAIL_REPRESENTATION
S4 candidate_residual_share > 0.50                     -> FAIL_REPRESENTATION
S5 m=2 needs a different solve architecture            -> FAIL_REPRESENTATION
S6 correspondence fails the section 10 rule            -> FAIL_CORRESPONDENCE
S7 ratio_incremental > 2.0 with correspondence passing -> PASS_COST_HIGH
S8 any path outside this namespace modified            -> STOP the whole gate
S9 a result-bearing semantic bug found after T2 -> STOP; no adaptive repair
```
No degree change, no cap extension, no tolerance change after T2.

## 13. Checkpoint readiness

`YES` only if Gates 1/2A/2B intact, correspondence PASS, representation guard
PASS, `m`-sharing PASS, `ratio_incremental <= 2.0`, and the first-moment
production cost model has no remaining unmeasured load-bearing input. This means
**ready to DESIGN** a binding checkpoint, never that one exists.

**Scientific boundary:** even a full PASS does not close `K2` `s_min`, `K3` `M_2`,
`K4` `H2` or `K5` `H3a`.

## 14. Out of scope — not run

Second moments, `s_min`, `M_2`, SR production, all-`m` cover, `H2`/`H3a`, Lean,
binding Arb campaign, checkpoint creation.

## 15. Repository safety

Branch `p5y-gate1-micropilots`, namespace
`level4/closure_proofs/p5y_gate2cbis_m2_assembly_b/`. No merge to main, no push,
no binding checkpoint, no modification of P5, P5X or Gates 1/2A/2B/2C.
