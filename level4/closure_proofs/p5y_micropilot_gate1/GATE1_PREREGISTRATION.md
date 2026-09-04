# P5Y MICRO-PILOT GATE 1 — preregistration

**NON-BINDING.** This is a pre-campaign falsification gate. It is not a P5Y
binding checkpoint, not production, and creates no scientific evidence. It
tests three architecture hypotheses and nothing else.

Frozen before any result-bearing execution (T2). Nothing on this page may be
changed after T2. Historical P5 and P5X artifacts are read-only inputs.

```text
P5_ORIGINAL_VERDICT = PARTIAL
P5X_FINAL_VERDICT   = PARTIAL
P5X_CAMPAIGN        = ARCHIVALLY_COMPLETE
```

---

## 0. Scope and prohibitions

In scope: `M1` raw-variable CUSUM 2-cell test; `M2` SR degree/continuous-panel
test; `M3` SR xi-coordinate test (conditional, see §5); three predeclared
non-decisive optional checks (§6).

Out of scope and **not run**: any full cover, any `m > 1` certification, any
second-moment production, `s_min`/`M_2` production, the `H2`/`H3a` derivative
cover, any Lean, any Monte Carlo quantity on any decision path.

## 1. Compute cap

```text
GATE1_CPU_CAP        = 5.0 CPU-hours   (hard, no extension after results)
GATE1_CPU_PREFERRED  < 3.0 CPU-hours
```

If any pilot is projected to need materially more, it is recorded
`REQUIRES_LARGER_FUTURE_PILOT` and **not run**. No production run follows a
PASS.

## 2. M1 — PILOT-RAW-2CELL (CUSUM, m = 1)

### 2.1 Frozen algebra to verify before execution

```text
rho_{1,e} + e h_1            = phi(u+e) - phi(l+e)                      (I1)
F = K_e F + [phi(u+e) - phi(l+e)] ,  R_{D,1}(e) = F(x_0)   (no external +e)  (I2)
S_r^raw = K_{raw,e} h_r = S_r + e h_{r+1}                                (I3)
```

`u = c_D - x^+`, `l = x^- - c_D`, `c_D = 11/2`, `h_1 = 1 - Phi(u+e) + Phi(l+e)`.
Execution does not proceed unless `I1` and `I3` hold to `<= 1e-12` absolute over
the frozen verification set (9 drifts x 16 states, `tests/test_gate1.py`).

### 2.2 Frozen cells (exactly two; no third cell may be added)

| cell | interval | rationale |
|---|---|---|
| **A** near field | `e in [0.24, 0.26]`, `DEN = 10^7` | the binding cell of the historical stop-gate, R-A', R1 and R2 — unchanged |
| **B** far field | `e in [10.5441104, 12]`, `DEN = 10^7` | the historical final failing outer cell reported in the Gate-1 brief |

### 2.3 Frozen implementation discipline

Unchanged and imported verbatim from the historical P5X modules: the operator
`K_e` (`_kernel_polynomials`), the state square `[0,5]^2`, the reachable-set
cover, the resolvent minorant (`drift_monotone_resolvent`), the Bernstein range
bound (`max_abs_on_reachable_fast`), precision `256` bits, Taylor order
`N = 120`, candidate degree `12`, quadrature `400`, scale bits `50`, detector
semantics, stopping convention, the sub-cell ladder rule and `h = 1/(4 a C)`.

Changed, and only this: the **source/unknown representation** (`rho_1 -> rho_1^raw`,
`d_e rho_1 -> d_e rho_1^raw`, collocation reward vectors) and the **bootstrap
constant** `c_2`. No historical file is modified; the pilot lives in a new file.

```text
rho_1^raw   = phi(u+e) - phi(l+e)
d_e rho_1^raw = -(u+e) phi(u+e) + (l+e) phi(l+e)
c_1^raw <= 2 max_x |x phi(x)|      = 2 phi(1)  = 0.483941...
c_2^raw <= 2 max_x |(x^2-1) phi(x)| = 2 phi(0) = 0.797884...
        (critical points of (x^2-1)phi are x = 0, +/-sqrt 3; |f(0)| = phi(0) > 2 phi(sqrt3))
reward_allow^raw = 2 * eps_reward * (1 + 5/2)          (the phi-site part of the
        frozen R-A' allowance, with the e-dependent cdf part removed; strictly
        conservative for a two-phi-site reward)
```

Assembly per sub-cell, identical to `r1_stop_gate.py` **minus the `e_range` term**:

```text
S2  = 2 C (2 a G1 + b G0 + b h G1 + c_2^raw)
R  in  F_encl  +/- h * dF_encl  +/- (h^2/2) S2 ,   F_encl = Fhat(x_0) +/- C delta
```

### 2.4 Frozen acceptance thresholds

```text
A1  near-cell enclosure MUST overlap the historical R2 enclosure
        [-1.584973380499857, -1.5676443748392161]              (correctness anchor)
A2  far-cell raw half-width  <  1.0        (primary, frozen)
A3  far-cell raw half-width  <  0.75       (preferred, reported not decisive)
A4  near-cell raw half-width <= 0.05       (must stay inside the R1/R2 regime)
```

`PILOT-RAW-2CELL = FAIL` if: `I1`/`I3` are not exact; `A1` fails; `A2` fails;
the certifier raises or is unstable; or the representation changes the estimand.

## 3. M2 — PILOT-SR-DEGREE

### 3.1 Frozen configuration

The historical R3 binding case, unchanged and not substituted for an easier one:
detector SR, `m = 1`, `e = 1/4` exact, patch `(17, 11)` on `grid = 64`, candidate
bidegree `(16,16)`, precision `192` bits, corrected domain `b_SR = log(1+A)`,
`A = 4581762885148045 / 8796093022208`.

### 3.2 Frozen degree grid

```text
DEGREES = {8, 10, 12}          (degree 6 run only as a free baseline control)
```

No degree may be added, and none removed, after T2.

### 3.3 Frozen continuous panel rule (replaces the dyadic rounding)

From the certified step-size inequality `E_d = M_{d+1} H^{d+1} / (d+1)! <= 1e-9`,
with `M_{d+1}` the tight u-independent Bernstein bound on `|sp^{(d+1)}|`:

```text
H_max = ( 1e-9 * (d+1)! / M_{d+1} )^(1/(d+1))       exact-arithmetic root, outward rounded down
h_z   = H_max - patch_half                          (patch_half = b_SR/(2*grid))
n_z   = ceil( core_len / (2 h_z) )                  (minimal safe panel count)
```

Deterministic, closed form, no rounding to powers of two, no tuning. If
`h_z <= 0` the degree is `INFEASIBLE` and fails.

### 3.4 Frozen validity gates (must pass BEFORE the cost gate is even read)

```text
P1  softplus local remainder E_d      <= 1e-9
P2  composed+integrated relative half-width <= 1e-6
P3  max composed coefficient radius   <  1e-20   (no interval dependency)
T1  enclosure contains point evaluations at -H, -H/2, 0, H/2, H
T2  remainder monotone in H
T3  core/strip split exhaustive
T5  centred Gaussian moment decay |N_k| <= h^k N_0 * 2
T7  corrected b_SR = log(1+A) used, log A not used
```

A faster candidate that fails any of these is `FAIL`.

### 3.5 Frozen cost gate and tie-break

```text
P4  n_z * t_panel <= 0.3314531805 seconds       (the exact frozen R3 threshold)
timing repeats = 5 (frozen); report median and full spread; timing noise may
move projected cost, never a mathematical PASS.
TIE-BREAK: select the LOWEST degree that passes every gate in 3.4 and 3.5.
```

## 4. M3 — PILOT-SR-XI

### 4.1 Frozen execution condition

```text
M3 RUNS IF AND ONLY IF M2 = FAIL.
```

If `M2 = PASS`, `M3 = NOT_RUN` and the Gate-1 decision follows CASE A. This is
frozen here so that no post-result choice of SR back-end is possible, and
because building the xi back-end is a materially larger effort than the frozen
Gate-1 envelope (§1) permits when a qualifying back-end already exists.

Regardless of M2, the following **non-decisive analytic** part of M3 runs and is
reported: identity verification (§4.2) and the deterministic panel-count bound
(§4.3). It produces no PASS/FAIL.

### 4.2 Frozen transform and moment identities

```text
xi = exp(y) ,  xi' = 1 + xi * w ,  w = exp(z - 1/2) ,  alarm iff xi * w >= A
G_c(L,U) = int_L^U exp(c z) phi(z+e) dz = exp(c^2/2 - c e) [ Phi(U+e-c) - Phi(L+e-c) ]
```

Both verified against the frozen softplus recurrence and against R3's own
`centred_gaussian_moments` at `c = 0`, tolerance `1e-25` relative.

### 4.3 Frozen panel semantics and threshold

Panels arise ONLY at geometry breakpoints where `1 + xi * exp(z-1/2)` crosses a
frozen state-patch boundary. No error-driven adaptive subdivision, ever.

Because `y'_+` is increasing in `z` and `y'_-` decreasing, and both live in
`[0, b_SR]` partitioned into `grid` cells, the induced panel count is bounded
**deterministically and before any execution** by

```text
n_panels <= 2 (grid - 1) + 1 = 127     for grid = 64
```

The brief's default threshold is `100`. It is therefore replaced, **here and
before T2**, by

```text
M3_PANEL_THRESHOLD = 127
```

with the sole justification that `127` is the exact closed-form geometric bound
implied by matching R3's frozen `grid = 64` for comparability, is not a
measurement, and cannot be influenced by any result. The decisive M3 gate
remains the cost gate `total local-gate cost <= 0.3314531805 s`, unchanged.
This departure from `100` is disclosed rather than silently applied.

### 4.4 M3 pass condition (if it runs)

All of §3.4-equivalent mathematical gates; total local-gate cost no worse than
the historical R3 route on the same frozen patch; `n_panels <= 127`; no new
uncontrolled approximation; `erf`/`exp`/`log` Arb primitives suffice.

## 5. Decision logic (mechanical, no narrative override)

```text
M1 FAIL                          -> GATE1_FAIL_ROUTE_B_NOT_SUPPORTED
M1 PASS and M2 PASS              -> GATE1_PASS_ROUTE_B_SUPPORTED   (backend DEGREE_RETUNED)
M1 PASS and M2 FAIL and M3 PASS  -> GATE1_PASS_ROUTE_B_SUPPORTED   (backend XI_COORDINATE)
M1 PASS and M2 FAIL and M3 FAIL  -> GATE1_FAIL_ROUTE_B_NOT_SUPPORTED
```

## 6. Optional, predeclared, NON-DECISIVE checks

```text
PILOT-MSHARE      structural: assert the m=2 function set is a subset of the m=5
                  set derived from P5X-T1(c)/L2, and that the m=2 assembly cites
                  no m-specific solve. Deterministic set algebra, zero CPU.
PILOT-FARFIELD2   outward-rounded Arb evaluation of the proposed L3' majorant
                  B2_D(e) = 2[Phi(a)+|a|phi(a)] + Phi(a)/(1-Phi(a)), a = c_D-|e|,
                  at two frozen tail points per detector: e = 10 and e = 12.
PILOT-SMIN-ANALYTIC  scalar scoping check that the conditional-variance minorant
                  v_min = inf Var(raw | raw outside (L,U)) is strictly positive
                  over the frozen reachable threshold box. Explicitly a SCOPING
                  CHECK, not a certificate, and non-decisive.
```

None may consume budget needed by M1/M2/M3.

## 7. Measurement governance (P4 lesson)

No load-bearing Monte Carlo quantity is introduced anywhere in this gate. M1,
M2 and M3 are deterministic/certified architecture pilots. Timing repeat counts
are frozen in §3.5 before execution; variability is reported; timing noise may
affect projected cost only, never a mathematical PASS. No expected-precision
top-up scheme is permitted.

## 8. STOP rules

```text
S1  cumulative CPU reaches 5.0 CPU-hours              -> STOP, report INCOMPLETE
S2  a result-bearing semantic bug is found after T2   -> STOP that pilot; do not
    patch and continue unless the fix is provably reporting-only and cannot alter
    any result or selection
S3  I1 or I3 not exact                                -> STOP M1, FAIL
S4  any frozen mathematical gate fails for a degree   -> that degree FAILS; no
    grid expansion, no threshold relaxation
S5  the protected tree (P5, P5X, everything outside this namespace) is modified
    -> STOP the whole gate
```

## 9. Repository safety

Branch `p5y-gate1-micropilots`, namespace
`level4/closure_proofs/p5y_micropilot_gate1/`. No merge to main. No binding
checkpoint. No historical file modified. No push.

---

## 10. Pre-T2 amendment log

Amendments are permitted only before T2 and only when they cannot relax a
threshold or change a decision rule. Each is listed with its timestamp class.

**A-01 (pre-T2).** M1 additionally runs an unmodified **z-variable control arm**
on both frozen cells, using the historical R2 certifier
(`compute_optimization_r2/r2_certifier.py`) imported verbatim, so that the
far-field comparison in the brief's section 7 is a *measured* side-by-side rather
than a reconstruction. This adds a control, changes no threshold, no acceptance
rule and no decision logic, and cannot make M1 easier to pass.
