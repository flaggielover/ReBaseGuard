# P5Y GATE 2E — PILOT-SR-METRIC result

```text
P5Y_GATE2E_DECISION = SR_METRIC_FAIL_CANDIDATE   (mechanical; NOT reinterpreted)
P5Y_SR_METRIC_FAILURE_CLASS = IMPLEMENTATION_DEFECT
CPU USED = 4.46 CPU-seconds against a frozen 540 s cap (0.8%)
STOP_FIRED = NO ; BINDING = NO ; PRODUCTION RUN = NO ; CHECKPOINT = NO
Gate-2D remains SR_REALCANDIDATE_FAIL_REPRESENTATION, permanently.
```

**The metric question is answered, affirmatively. The gate still fails, and the
name understates the cause: the candidate passed its proposition-derived budget
by 1,193x, and what blocked the PASS is the `P1` floating-point knife edge —
its third recorded occurrence, and this time my own error.**

---

## 1. The proposition-derived metric (derived before any Gate-2D value was used)

```text
(1) ‖h_1 - hhat_1‖ <= eps_cand        (2) |K_raw(h_1-hhat_1)| <= 0.79788 eps_cand
(3) 30 panels per patch accumulate    (4) ‖(I-K)^-1‖ <= C_SR(e)   [UPPER, audited]
(5) R_2 = (1/2)[F_0 + F_1 + S_0^raw]  (6) hull over [0, e_star]   (7) P5X-T3 far field
=>  sup_e |R_{SR,2}(e)| <= R_max < 2
```

```text
slack_R  = 2                    the frozen P5X-T4 boundary
alpha    = 0.1                  P5X Checkpoint A's pre-result 0.2 half-width rule
w_target = 0.2
ledger   B_cover .050 | B_candidate .040 | B_kernel .040 | B_other .040
         B_rounding .010 | B_interval .010 | reserve .010 (non-redistributable)
         B_resolvent = 0  -- C is a MULTIPLICATIVE amplifier, recorded so it is
                            never double-counted as an additive term
LOCAL_GATE_BUDGET = B_candidate + B_kernel + B_interval + B_rounding = 0.100
w_panel_max         = 0.100 / (0.5 * 187.7472 * 30) = 3.5509e-05
delta_candidate_max = 2 * 0.040 / (187.7472 * 0.79788) = 5.3404e-04
```

Every input predates Gate-2D and is hashed into `GATE2E_SOURCE_MANIFEST.json`
at the T0/T1 commit. A pre-T2 test asserts no Gate-2D residual appears among the
frozen metric constants.

**Amplification direction audit — PASS.** `C_SR = min_t t/H_t(0)` with `H_t` a
*lower* Bellman envelope, so it is an **UPPER** bound on `‖(I-K_e)^{-1}‖`;
`C_SR(0) = 1205.94 <= 25000/19 = 1315.79` (certified), and `C_SR` is decreasing
in `e` (`1205.94 -> 2.00`). Correct object, correct direction.

**Scale-aware fallback: not invoked, and no code path for it exists.** The
suggested `P2_rel <= 1e-8 * max(1,|acc|)` is rejected on dimensional grounds —
`P2` is dimensionless while `|acc|` carries the panel integral's units.

## 2. Execution order — the Gate-2D defect is fixed

```text
direction_audit -> acceptance_precondition -> representation_guard -> precision_grid
```
recorded in `stages_run`, and a **decisive pre-T2 negative-control test** supplies
an impossible budget (`1e-30`) and asserts the grid is *not* entered. That test
passes.

## 3. Results under the new absolute metric — every object passes

| object @ bits | `w_panel` (abs) | budget | ratio | old `P2` (diagnostic) | ABS |
|---|---|---|---|---|---|
| `hhat_1` @256/384/512 | `2.9771e-08` | `3.5509e-05` | `8.38e-04` | `3.5403e-02` | **PASS** |
| `hhat_2` probe @all | `6.2943e-11` | `3.5509e-05` | `1.77e-06` | `6.9643e-06` | **PASS** |
| `unit_candidate` @all | `5.7200e-08` | `3.5509e-05` | `1.61e-03` | `7.5325e-10` | **PASS** |

Candidate acceptance precondition: `eps_cand = 1.9301e-07` against
`delta_candidate_max = 5.3404e-04` — **PASS, 2,767x inside**. Candidate identical
to Gate-2D's (`eps_cand` equal to the last digit); not refitted.

## 4. The Gate-2D root cause, confirmed quantitatively

```text
absolute:  w_panel(hhat_1) / w_panel(unit_candidate) = 0.52      -- within 2x
relative:  P2(hhat_1)      / P2(unit_candidate)      = 4.70e+07  -- 47 million x
```
The pre-registered prediction ("within an order of magnitude in absolute terms")
is **confirmed**. Gate-2D's diagnosis was right: the relative instrument, not the
architecture, separated these two objects.

## 5. Error-source decomposition — the certificate is approximation-limited

At `hhat_1 @ 256 bits`:

```text
candidate approximation   99.55 %
softplus/kernel truncation 0.45 %
Arb working precision      3.7e-46 %
```
Not precision-limited, not propagation-limited, not theorem-slack-limited. If a
future certificate needs a tighter local enclosure, the lever is the candidate
fit — degree or basis — and nothing else.

## 6. Why it still fails — the `P1` knife edge, third occurrence, my error

```text
E_d = 9.99000000000000376e-10   target (1 - 1e-3) * 1e-9 = 9.98999999999999962e-10
E_d / target - 1 = +4.44e-16
```
The continuous panel rule solves `E_d = (1 - eps_P1) * 1e-9` to **equality**, so
`h_z` is the float root and the acceptance test `E_d <= (1 - eps_P1) * 1e-9` is
decided in the 16th significant digit by rounding. Panel count is unaffected
(`n_z = 28`, unchanged); only the boolean flips.

Gate-2C recorded this defect and recommended "target `(1 - eps) * 1e-9`". **I
applied `eps` to both the rule and the check**, which reproduces equality and
reproduces the knife edge one notch lower. The fix is asymmetric and is now
precisely located:

> the **rule** targets `(1 - eps) * 1e-9`; the **check** tests against `1e-9`,
> so `eps` becomes genuine headroom rather than a shifted equality.

Not patched — no post-T2 amendment is permitted, and a test asserts the module
is byte-identical to its T1 hash.

## 7. Why the decision is not renamed

`SR_METRIC_FAIL_CANDIDATE` is defined as "the candidate exceeds its frozen
budget". It did not. But unlike Gate-2D — where a frozen rule explicitly mapped
the measured precondition to `FAIL_REPRESENTATION` and only the code failed to
implement it — **no frozen rule maps a `P1` knife edge to any other name**. The
decision vocabulary has no slot for it. Choosing a different name would be
inventing a rule after results rather than applying one, so the mechanical
decision stands and the true cause is recorded in `failure_class =
IMPLEMENTATION_DEFECT`.

## 8. Cost model — unchanged

Nothing here changes production cost. Carried forward from Gate-2C-bis:
`1,868 / 3,092 / 3,697 / 4,597` CPU-hours.

## 9. Boundary

`K2` `s_min`, `K3` `M_2`, `K4` `H2`, `K5` `H3a` remain unresolved; P5 is not
closed. `P5Y_FIRST_BINDING_CHECKPOINT_READY = NO`.
