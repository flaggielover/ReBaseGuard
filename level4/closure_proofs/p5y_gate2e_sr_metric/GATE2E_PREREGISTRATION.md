# P5Y GATE 2E — PILOT-SR-METRIC preregistration

**NON-BINDING.** An acceptance-metric validation pilot. It does **not** turn
Gate-2D into a PASS: `P5Y_GATE2D_DECISION = SR_REALCANDIDATE_FAIL_REPRESENTATION`
stands permanently and its artifacts are preserved.

```text
P5Y_GATE1_DECISION     = GATE1_PASS_ROUTE_B_SUPPORTED        (immutable)
P5Y_GATE2A_DECISION    = SR_PRECISION_PASS_256               (immutable)
P5Y_GATE2B_DECISION    = SR_COVER_PASS_MEASURED              (immutable)
P5Y_GATE2C_DECISION    = M2_ASSEMBLY_INCOMPLETE_EXTERNAL     (immutable)
P5Y_GATE2CBIS_DECISION = M2_ASSEMBLY_B_PASS                  (immutable)
P5Y_GATE2D_DECISION    = SR_REALCANDIDATE_FAIL_REPRESENTATION (immutable, FAIL forever)
```

## 0. The question

What error metric is actually required by the load-bearing P5 proposition, and
do the already-frozen genuine SR candidates satisfy that proposition-derived
metric?

## 1. ANTI-CIRCULARITY — the dependency order, declared and auditable

The threshold below is constructed **entirely from inputs that predate
Gate-2D**. In dependency order:

| step | quantity | source | predates Gate-2D? |
|---|---|---|---|
| 1 | the proposition `sup_e\|R_{D,m}(e)\| < 2` | `P5X-T4` / `H3b`, frozen Checkpoint A 2026-09-02 | **yes** |
| 2 | admissible numerical half-width `0.2` | P5X `STOP_GATE.md`: `FROZEN_THRESHOLD = 0.2 (Checkpoint A; not reinterpreted)` | **yes** |
| 3 | error-budget shape | R1's published error budget (`C·delta`, second-order Taylor, sub-cell range as the three comparable mechanisms) | **yes** |
| 4 | amplification `C_SR(1/4) = 187.7472` | Gate-2B | **yes** |
| 5 | panels per patch `n_z + 2 = 30` | Gate-1 / Gate-2B (`n_z = 28`) | **yes** |
| 6 | **only now** evaluate the frozen Gate-2D candidates | — | — |

**No Gate-2D output enters the threshold.** Gate-2D residuals are used only for
the falsifiable predictions in section 11, which is explicitly permitted.

## 2. Compute cap

```text
GATE2E_CPU_CAP = 540 CPU-seconds = 0.15 CPU-hours (hard)   preferred <= 360 s
```
External watchdog kept; no extension after T2.

## 3. The load-bearing proposition and the full dependency chain

The unresolved load-bearing requirement is `K1`:

```text
R_max(D,m) = sup_{e in R} | R_{D,m}(e) |  <  2          (P5X-T4 = H3b = gate G3)
```

For this SR pilot the candidate is `hhat_1^SR`, and `h_1` enters the proof of
`R_max` **only through `m >= 2`** (it is absent from the `m = 1` chain). The
exact chain, written out:

```text
(1) candidate error       ‖h_1 - hhat_1‖_inf  <=  eps_cand            [whole square]
(2) kernel propagation    |K_{raw,e}(h_1 - hhat_1)|  <=  E|raw| eps_cand
                                                     =  0.7978845608 eps_cand
(3) panel accumulation    the patch integral sums n_z + 2 = 30 panels, so a
                          per-panel absolute error w_panel contributes
                          <= 30 w_panel to the residual sup-norm delta
(4) resolvent             F_1 = (I - K_e)^{-1} S_1^raw , and
                          ‖(I-K_e)^{-1}‖_inf <= C_SR(e)   [UPPER bound, section 4]
                          so |F_1 - Fhat_1| <= C_SR(e) * delta
(5) assembly              R_2 = (1/2)[ F_0 + F_1 + S_0^raw ]  (Gate-2C-bis, exact)
                          so the contribution is (1/2) C_SR(e) delta
(6) compact cover         hull over e in [0, e_star_SR]      (Gate-2B, 322 sub-cells)
(7) far field             P5X-T3 closes |e| >= e_star_SR
=>  sup_e |R_{SR,2}(e)|  <=  R_max  <  2
```

## 4. Amplification-bound direction audit (mandatory, section 9 of the brief)

`C_SR(e) = min_t t / H_t(0)` with `H_t` a **lower** Bellman envelope of the hit
probability. A lower bound on hitting gives an **upper** bound on
`sup_x E_{x,e}[tau] = ‖(I-K_e)^{-1}‖_inf`. Three checks are asserted
mechanically before T2:

```text
(a) TYPE  = UPPER bound on the resolvent operator norm
(b) C_SR(0) = 1205.9371 <= the certified 25000/19 = 1315.7895   (Gate-2B cross-check)
(c) C_SR(e) is decreasing in e (1205.94 -> 2.00), consistent with faster alarms
```
If any fails, the gate returns `SR_METRIC_FAIL_NO_JUSTIFIED_METRIC`.

## 5. Proposition slack and `w_target`

```text
slack_R  = 2                  the frozen boundary of P5X-T4; the only
                              theorem-backed constant available in the compact
                              region (the analytic route to |R| < 2 is proved
                              dead in FAILURE_ANALYSIS.md section 1, which is
                              exactly why a certificate is needed)
alpha    = 0.1                frozen at P5X Checkpoint A as the 0.2 half-width rule
w_target = alpha * slack_R = 0.2
```
Equivalently: the certificate succeeds for any achieved centre with
`|R_hat| <= 1.8`. **No measured or Monte-Carlo value of `|R|` is used anywhere
in this derivation**, in keeping with the campaign's own `G8` firewall and the
P4 lesson.

## 6. Frozen error-budget ledger

Allocation shape follows R1's published budget, in which `C·delta`, the
second-order Taylor term and the sub-cell range were the three comparable
mechanisms:

```text
B_cover      = 0.25 * w_target = 0.050    e-cell Taylor model  h|R'| + (h^2/2) S2
B_candidate  = 0.20 * w_target = 0.040    candidate / source approximation
B_kernel     = 0.20 * w_target = 0.040    softplus + panel truncation
B_other      = 0.20 * w_target = 0.040    assembly, derivative equation, hull
B_rounding   = 0.05 * w_target = 0.010    exact-dyadic rounding
B_interval   = 0.05 * w_target = 0.010    Arb working-precision radius
B_resolvent  = 0                          C is a MULTIPLICATIVE amplifier, not an
                                          additive term; recorded so it is not
                                          silently double-counted
sum = 0.19 <= w_target = 0.2 ;  0.01 (5%) held in RESERVE
```
**No component may borrow the reserve or another component's unused budget after
T2.** No redistribution rule is defined, so none exists.

The local gate measures the panel-level enclosure, which carries exactly four of
these mechanisms:

```text
LOCAL_GATE_BUDGET = B_candidate + B_kernel + B_interval + B_rounding = 0.100
```
`B_cover` and `B_other` are outside this pilot's measurement and are neither
consumed nor released by it.

## 7. The ABSOLUTE metric (primary)

Inverting the chain of section 3 at the frozen drift `e = 1/4`:

```text
w_panel_max = LOCAL_GATE_BUDGET / ( (1/2) * C_SR(1/4) * (n_z + 2) )
            = 0.100 / ( 0.5 * 187.7472 * 30 )
            = 3.5511e-05                                    [FROZEN]

delta_candidate_max = 2 * B_candidate / ( C_SR(1/4) * 0.7978845608 )
                    = 0.080 / 149.783
                    = 5.3411e-04                            [FROZEN]
```

```text
DELTA_ABS_PASS  iff  w_panel_total  <=  w_panel_max   AND   eps_cand <= delta_candidate_max
w_panel_total = rem_width + acc_radius + eps_cand * N_0
```
`w_panel_total` is an **absolute** quantity; nothing is divided by `|acc|`.
The Gate-2D relative `P2` is reported for every cell as a **diagnostic only**
and may not decide anything.

## 8. Scale-aware fallback — declared, and NOT expected to be invoked

The fallback executes **only** if the section-4 direction audit fails or the
absolute chain cannot be formed. Its frozen form would be
`error_abs <= atol + rtol * scale` with `atol = B_candidate / (C_SR * 30 / 2)`,
`rtol = 1e-8`, `scale = |acc|`. The schematic `P2_rel <= 1e-8 * max(1,|acc|)`
suggested elsewhere is **rejected on dimensional grounds**: `P2` is
dimensionless while `|acc|` carries the units of the panel integral, so the
product mixes incommensurable quantities. A pre-T2 test asserts the fallback
cannot execute when the absolute route is valid.

## 9. Frozen objects, grid and guards

```text
objects   hhat_1^SR (primary, genuine), hhat_2^SR (non-separable probe,
          non-decisive), unit_candidate (control) -- all IDENTICAL to Gate-2D,
          rebuilt by importing Gate-2D's frozen module; coefficient identity asserted
patch     (17,11), grid 64, e = 1/4, degree 8, bidegree (16,16)
grid      {256, 384, 512} bits ; no adaptive point
guard     max bidegree <= 16, composed z-degree 128, score <= 100,000
P1        eps_P1 = 1e-3, n_z must remain 28   (Gate-2B: panel-count free)
```
`hhat_1` is **not refitted**. No object is re-tuned to improve the result.

## 10. Execution order — the Gate-2D defect, fixed

```text
1  metric derivation (frozen, above)
2  amplification direction audit          -> FAIL_NO_JUSTIFIED_METRIC on failure
3  candidate acceptance precondition      -> FAIL_CANDIDATE on failure
4  representation-complexity guard        -> FAIL_ARCHITECTURE on failure
5  ONLY THEN the precision grid
```
A pre-T2 test deliberately supplies an over-tight budget and asserts the
precision grid is **not entered** — the decisive fix for Gate-2D's defect.

## 11. Pre-registered falsifiable predictions (Gate-2D numbers permitted HERE only)

| quantity | prediction |
|---|---|
| `eps_cand` vs `delta_candidate_max` | `1.93e-07` vs `5.34e-04` -> PASS, `~2,770x` inside |
| `w_panel_total(hhat_1)` | `~3.0e-08` vs `3.55e-05` -> PASS, `~1,190x` inside |
| `w_panel_total(unit_candidate)` | `~5.7e-08` — the **same order** as `hhat_1`, though their relative `P2` differ by `4.7e7`x |
| `w_panel_total(hhat_2)` | `~6.3e-11` |
| safe precision | `256` |
| decision | `SR_METRIC_PASS_ABSOLUTE` |

If `hhat_1` and `unit_candidate` do **not** come out within an order of
magnitude of each other in absolute terms, the Gate-2D root-cause diagnosis is
wrong and that must be reported.

## 12. STOP rules

```text
S1 worker CPU reaches 540 s -> kill, no completed artifact, STOP_FIRED = YES
S2 direction audit fails                 -> FAIL_NO_JUSTIFIED_METRIC
S3 candidate exceeds its frozen budget   -> FAIL_CANDIDATE
S4 guard fails / propagation impossible  -> FAIL_ARCHITECTURE
S5 any path outside this namespace modified -> STOP the whole gate
S6 result-bearing semantic bug after T2  -> STOP; no adaptive repair
```
No post-T2 threshold, budget, object or architecture amendment.

## 13. Boundary

Even a perfect PASS does not establish `K2` `s_min`, `K3` `M_2`, `K4` `H2` or
`K5` `H3a`, and does not close P5.

## 14. Out of scope

Full SR cover, CUSUM production cover, second moments, `s_min`, `M_2`, `m = 3`
or `5`, `H2`/`H3a`, Lean, checkpoint creation, production campaign.

## 15. Repository safety

Branch `p5y-gate1-micropilots`, namespace
`level4/closure_proofs/p5y_gate2e_sr_metric/`. No merge to main, no push, no
binding checkpoint, no modification of P5, P5X or any prior gate.
