# P5X frozen scope

Frozen at Checkpoint A and hashed into `PROTOCOL_DIGEST.json`. Any production
result outside this scope is inadmissible; any narrowing must be reported as a
narrowing, not presented as the original plan.

## 1. Model

| item | frozen value |
|---|---|
| detectors | `CUSUM(k = 1/2, h = 5)` two-sided, inclusive post-update test, plus-arm priority on ties; `SR` symmetric two-chart, `A = 520.886133602749`, stored state `y = log(1+R)`, `y_0 = 0`, inclusive test on `max(y^+ + z - 1/2, y^- - z - 1/2)` |
| observations | `raw_t ~ iid N(0,1)`, `Delta = 0` (in-control only) |
| innovation | `z_t = raw_t - e` |
| stopping | `tau = inf{ t >= 1 : alarm after the update at t }`, no minimum dwell |
| window | `w = min(m, tau)`, denominator `w`, terminal alarm-causing observation included — **Stage-D convention A** |
| windows | `m in {1, 2, 3, 5}` |
| reuse | `e_{j+1} = rho(e_j + zbar_j) + (1-rho) fresh_j`, `fresh ~ N(0, 1/m)` independent |
| policy | constant `rho`, non-adaptive |

Nothing outside this list is in scope: not non-Gaussian innovations, not
contaminated data, not other detectors or thresholds, not other reuse
conventions, not `m > 5`, not out-of-control operation, not adaptive `rho`.
Those are P8/P8R territory and P5X imports no result from them.

## 2. `rho` scope

| statement | `rho` scope | reason |
|---|---|---|
| `P5X-T1`, `T2`, `T3` | independent of `rho` | they concern `R` and `S` only |
| `P5X-T4` (saturation) | independent of `rho` | same |
| `P5X-T5` (drift, trapping) | **all** `rho in [0,1]` | follows from `P5-T2` |
| `P5X-T6` (dispersion bounds) | **all** `rho in [0,1]` | follows from invariance + `P5-T2` |
| `P5X-T7` (map shape) | independent of `rho` | same |
| `P5X-T8` (skeleton dynamics) | `rho in [ (1+eta) rho_c , 1 ]`, `eta` reported | at `rho = rho_c` the 2-cycle multiplier is exactly `1`; hyperbolicity is uncertifiable there by any interval method |
| `P5X-T9` (synthesis) | `rho in (rho_c, 1]` | needs `|lambda| > 1` |

`eta` is **not** frozen to a number, because pre-committing a number would
either be arbitrary or invite tuning. What is frozen is the rule: the campaign
reports the smallest `eta` for which the certified cover closes, reports it
once, and does not re-run the cover after seeing the result to obtain a
prettier `eta`. Gate `G6` enforces that the reported `eta` comes from the first
completed cover.

## 3. `e` scope

`P5X-T4`, `T6`, `T7` are global in `e in R`. The certified cover is
`[0, e_far]` (with oddness `P5-T3` supplying `e < 0`), and `P5X-T3` closes
`[e_far, infinity)`. `e_far` is frozen at **`e_far = 12`** for both detectors,
chosen because the reproducible secondary lobe of `|R|` ends by `|e| ~ 8` in
both detectors and the far-field majorant is already `< 1e-4` at `|e| = 10`.
If a production run needs `e_far > 12`, that is a reported change of plan.

## 4. Cover granularity

Frozen as a *rule*, not a number, because the required granularity is a
property of the certificate that cannot be known before it runs:

* the cover of `[0, e_far]` must be finite, must be produced by an adaptive
  bisection that terminates on a certified criterion, and must be recorded in
  full in the result artifact;
* the certificate must state, for every cell, the enclosure and the criterion
  that accepted it;
* no cell may be accepted by sampling. Gate `G8` fails the campaign if any
  accepted cell's evidence is a point evaluation.

## 5. Evidence tiers admitted

| tier | admissible use in P5X |
|---|---|
| `EXACT_THEOREM` | premises, and the reduction `P5X-T1`–`T3` |
| `CERTIFIED_THEOREM` | `P5X-T4`, `T6`, `T7`, `T8` |
| `CONDITIONAL_THEOREM` | permitted only with the condition named in the statement |
| `NUMERICAL_EVIDENCE` | correspondence checks, non-vacuousness, finite-sample illustration — never a bound |
| imported P5/P3/P7 results | cited, never restated as P5X work |

## 6. Protected tree

Every tracked path outside
`level4/closure_proofs/p5x_global_nonlinear_dynamics/` is immutable for the
duration of the campaign, including all of `P1`–`P9`, `P8R`, `P9R`,
`p5_nonlinear_dynamics/`, `closure/`, `rebaseguard-proof/`, `rebaseguard-lean/`,
and the root `README.md`.

Two **untracked** namespaces exist at the anchor and are outside P5X:
`level4/closure_proofs/p4_final_disposition_audit/` and
`level4/closure_proofs/p5_final_disposition_audit/`. P5X neither commits,
modifies nor deletes them; gate `G11` records their presence and their content
hashes so that a "worktree scope" conjunct cannot be silently false — the exact
defect that failed P5's gate `G20`.
