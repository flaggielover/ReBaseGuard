# P5Y GATE 2F — PILOT-SR-METRIC-B result

```text
P5Y_GATE2F_DECISION = SR_METRIC_B_PASS_256
failure class = NONE ; STOP_FIRED = NO
CPU USED = 4.43 CPU-seconds against a frozen 180 s cap (2.5%)
BINDING = NO ; PRODUCTION RUN = NO ; CHECKPOINT = NO
Gate-2D and Gate-2E remain FAIL, permanently and unrewritten.
```

One semantic change — an asymmetric `P1` threshold pair — removes the knife edge
and the frozen genuine SR candidate passes at the lowest precision in the grid.

---

## 1. The one change, and what it did

```text
P1_RULE_TARGET     = (1 - 1e-3) * 1e-9 = 9.99e-10     solves for h_z  (headroom)
P1_CHECK_THRESHOLD = 1e-9                             tests E_d       (requirement)
E_d = 9.98999999999999261e-10        HEADROOM_REL = 1.000000e-03
guard MIN_HEADROOM_REL = 1e-6        -> 1000x above the guard
```
Gate-2E used the **same value** on both sides, so the check was decided by
rounding. `n_z = 28`, unchanged.

## 2. Negative control — the test that would have caught Gate-2E

```text
old symmetric (rule == check):  headroom = +3.21e-16   knife edge  -> P1 FAIL
new asymmetric:                 headroom = +1.00e-03   robust      -> P1 PASS
ratio 3.1e+12
```

**And the run produced its own independent confirmation.** The inherited
Gate-2E symmetric boolean now reads `True` on all three cells here, where in
Gate-2E it read `False` — flipped by a **one-ulp** difference in `h_z`. The same
check, the same mathematics, opposite verdicts. That boolean was never a real
gate; the headroom guard is, and it classifies the configuration as a knife edge
regardless of which side the rounding lands on.

## 3. Inheritance audit — PASS

Gate-2E's module is **imported and its attributes referenced directly**, so
equality is structural rather than transcribed, and every precision cell is
computed by calling Gate-2E's `run_cell` verbatim. All 19 constant checks pass,
including `run_cell_is_gate2e_function`.

| | Gate-2E | Gate-2F | |
|---|---|---|---|
| metric type / target | ABSOLUTE / `R_MAX_LT_2` | same object | ✓ |
| `slack_R` / `alpha` / `w_target` | `2.0 / 0.1 / 0.2` | same | ✓ |
| ledger + reserve | `.050/.040/.040/.040/.010/.010` + `.010` | same | ✓ |
| `w_panel_max` / `delta_candidate_max` | `3.550874e-05` / `5.340433e-04` | same | ✓ |
| `C_SR(1/4)` direction | `187.7472`, **UPPER** | re-audited, UPPER | ✓ |
| patch / grid / degree / bidegree / precisions | `(17,11)` / 64 / 8 / (16,16) / {256,384,512} | same | ✓ |
| **P1 thresholds** | one value used twice | **two distinct values** | ← the only change |

## 4. Objects — identical, not refitted

`eps_cand = 1.9301365637793417e-07` identical across Gate-2D, Gate-2E and
Gate-2F to the last digit. Precondition ratio `3.614e-04` — PASS, `2,767x`
inside `delta_candidate_max`. Representation guard PASS (bidegree 16, score
`37,281 / 100,000`).

## 5. Results — every object, every precision

| object @ bits | `w_panel` (abs) | budget | ratio | `P1` headroom | old `P2` (diag) | digits lost | CELL |
|---|---|---|---|---|---|---|---|
| `hhat_1` @256 | `2.9771e-08` | `3.5509e-05` | `8.38e-04` | `1.00e-03` | `3.5403e-02` | 30.54 | **PASS** |
| `hhat_1` @384 | `2.9771e-08` | | `8.38e-04` | `1.00e-03` | `3.5403e-02` | 30.54 | PASS |
| `hhat_1` @512 | `2.9771e-08` | | `8.38e-04` | `1.00e-03` | `3.5403e-02` | 31.34 | PASS |
| `hhat_2` probe @all | `6.2943e-11` | | `1.77e-06` | `1.00e-03` | `6.9643e-06` | 43.2–86.6 | PASS |
| `unit_candidate` @all | `5.7200e-08` | | `1.61e-03` | `1.00e-03` | `7.5325e-10` | 51.0–51.8 | PASS |

The old relative `P2` for `hhat_1` is `3.5e-02` — it would have failed the
obsolete instrument — while the proposition-derived absolute metric passes with
`1,193x` to spare. That contrast is the whole point of Gates 2D–2F.

Reproducibility (`hhat_1 @ 256`, computed twice): enclosure, absolute metric,
`E_d` and headroom all identical. PASS.

## 6. One recorded discrepancy — a single ulp, verdict-irrelevant

My own audit flagged `identical: false` when comparing the absolute metric with
Gate-2E's:

```text
hhat_1        2.9771109428542142e-08 (2E)  vs  2.9771109428542136e-08 (2F)
relative difference 2.22e-16  -- one ulp
```

**Cause:** `P1_RULE_TARGET` is evaluated at module scope, under whatever working
precision is current at import, whereas Gate-2E evaluated the same expression
inside `workprec(512)`. The resulting `h_z` differs in the last ulp of the
double and that propagates. **Fix for a successor:** compute the rule target
inside an explicit `workprec`.

This changes no verdict (`n_z = 28`, all ratios and headrooms unmoved to 15
digits) and it is not a semantic change to the geometry rule — both gates solve
`h_z` from `(1 - eps_P1) * 1e-9`. It is reported rather than smoothed over
because the preregistration claimed bit-identity, and bit-identity is not what
was achieved: **function-identity** was.

## 7. Cost model — unchanged

`256` was already the central band's assumption, so nothing moves:
`1,868 / 3,092 / 3,697 / 4,597` CPU-hours. A PASS does not lower costs.

## 8. Checkpoint readiness — YES, with the residual named

All eight frozen conditions hold: Gate-2F PASS; the absolute metric unchanged
and valid; `P1` headroom robust at `1000x` the guard; the genuine candidate
passing; safe precision resolved at `256`; representation guard PASS; prior
successful gates intact; and no remaining unmeasured load-bearing **first-moment
architecture or cost-model input** — the raw-variable reformulation, the SR
degree-8 backend, the safe precision, the cover geometry, the panel accounting,
the `m>1` cost ratio and the acceptance metric are now all measured.

```text
P5Y_FIRST_BINDING_CHECKPOINT_READY = YES     (ready to DESIGN, not to create)
```

**Named residual, stated plainly.** The certified-function candidates for the
resolvent solutions `F_r` have never been built — building one requires the
resolvent solve itself, which is production work. Their fit error will have to
sit inside the same `B_candidate = 0.040` that `h_1` uses `0.036%` of, and the
non-separable `hhat_2` probe passed at `1.77e-06` of budget, so the evidence
points the right way. But it is evidence, not measurement, and it belongs to the
first binding checkpoint's own first task rather than to another micro-pilot.

## 9. Boundary — no closure is claimed

`K2` `s_min`, `K3` `M_2`, `K4` `H2` and `K5` `H3a` remain unresolved. **P5
remains `PARTIAL`.** Readiness to design a checkpoint is not closure of anything
scientific.
