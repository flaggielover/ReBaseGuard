# SR full-cell prototype — result: FAIL on two numerical blockers

```text
FROZEN GATE     FAIL      failed: P3 (resolvent bound), P4 (half-width)
TRACTABILITY    ESTABLISHED   0.4470 ms/cell, 1.8 s for a full 64x64 sweep,
                              0 z-panels, 0 softplus approximations
SCIENCE         CORROBORATED  candidate-implied R_{SR,1}(0.25) = -1.590342
                              vs Monte Carlo -1.592117 +/- 0.001251  (1.42 s.e.)
CERTIFICATION   BLOCKED       no certified enclosure was produced
```

Anchor: Checkpoint I `3fe7e0a81bb8a46640469e1b1186998ee1363df4`.

---

## 1. What passed

| criterion | verdict | evidence |
|---|---|---|
| `P1` candidate solve | PASS | monomial basis `cond = 6.43e19`, Chebyshev basis `cond = 4.05e5`; both give `ghat(x_0) = -1.8403422` to 7 digits |
| `P2` residual evaluated | PASS | all `4096` cells, `delta = 6.178e10` |
| `P5` panel/softplus free | PASS | `z_panels = 0`, `softplus_approximations = 0` |
| `P6` correspondence | PASS (diagnostic) | see §4 |
| `P7` resources | PASS | solve `0.1 s`, residual sweep `1.8 s`, resolvent `61 s`, all far inside the `3600 s` budget |
| `P8` exact rational `e` | PASS | cell endpoints `24/100`, `26/100` exact |

**The panel-free architecture is fast.** A complete certified residual sweep over
the whole state square costs `1.8 s`. That is the tractability question R4/R6
set out to answer, and it is answered.

## 2. Blocker `B1` — `RESOLVENT_BOUND_NOT_OBTAINED` (`P3` FAIL)

The frozen value iteration never leaves `q = 1.0`, through all `4000` frozen
sweeps (`n = 1, 10, 100, 500, 1000, 2000, 4000` all exactly `1.0`).

**Cause, diagnosed not guessed.** Bounding `int v_n(q(x,z)) phi dz` by
`sum_s (max over image box) * mass_s` is an **adversarial** bound, not a
probabilistic one: `max` over the image box lets the state remain at the *safest*
reachable point at every step, so the iteration models an opponent who never
lets the walk drift to the boundary. Its per-sweep decay is therefore the
**one-step** boundary mass from the reset corner, `~4e-11`, instead of the true
`~1/130`. Reaching `q <= 1/2` would need `~1.7e10` sweeps.

Monte-Carlo scoping (diagnostic) puts the true constant at
`E_{x_0}[tau] = 129.6` at `e = 0.25` and `472.1` at `e = 0` — entirely
workable, which is what makes this a *method* failure rather than a
*feasibility* failure.

A secondary, independent defect in the same algorithm: the frozen mass bound
sums to `1.0079776 > 1` because each `z`-sub-interval is maximised over `e`
separately. Even a perfect box bound would then be pinned at `1`.

## 3. Blocker `B2` — `INTERVAL_DEPENDENCY` (`P4` FAIL)

| quantity | value |
|---|---|
| residual at **points** (41x41 grid, exact `e`) | `2.252942e-05` |
| residual over one `1/64` **cell** at the same location | `6.736713e+04` |
| **blowup factor** | **`2.990e9`** |
| max monomial coefficient of the candidate | `2.012e10` |

The candidate genuinely solves the equation — the point residual `2.25e-5`
matches the degree-16 `zeta`-approximation quality measured independently for
`rho_1` (`2.5e-5`), and the monomial and Chebyshev solves agree to 6 digits. The
failure is entirely in **evaluating that residual as a ball over a cell**: naive
interval arithmetic on a polynomial whose monomial coefficients are `~2e10` with
heavy cancellation.

This is the **same defect class** as the first certified CUSUM method
(`4.96e41` interval-dependency amplification), which `R-A'` Device 2 and R2's
Bernstein range bound solved for CUSUM. Neither transfers directly, because the
SR residual is not a polynomial — it is
`polynomial - sum_k G_k(zeta) I_k(l(zeta),u(zeta),e) - rho_1(zeta)`.

**A dead end that was ruled out.** I first suspected the `zeta`-polynomial space
itself, because a degree-16 `zeta`-polynomial approximates `y` only to `0.23`.
That is a red herring: `y = log(1+A*zeta)` is precisely the function `zeta`
un-does. The functions that actually appear are well behaved — `rho_1` is fitted
to relative `2.5e-5` at degree 16 with **maximum monomial coefficient `0.168`**.
The approximation space is not the problem.

## 4. Correspondence — `P6`, diagnostic only

`P5X-T1(b)` at `r = 0` gives `g_0(x_0) = E_e[Z_tau]`, so
`R_{SR,1}(e) = e + E[z_tau] = E[raw_tau]`, a directly simulable target.

| `e` | Monte Carlo (`n = 400000`) | candidate-implied |
|---|---|---|
| `0.24` | `-1.593369 +/- 0.001273` | — |
| `0.25` | `-1.592117 +/- 0.001251` | `-1.590342` |
| `0.26` | `-1.589105 +/- 0.001220` | — |

Deviation `1.42` standard errors — **consistent**. A Monte-Carlo estimate is not
rigorous and can only refute; it does not refute. For context, R2's *certified*
CUSUM enclosure on the same cell is `[-1.584952, -1.567644]`, so the two
detectors give closely comparable selection maps, as expected.

This corroborates that the whole `xi`-space pipeline — kernel, `rho_1`,
candidate solve, `G_k` assembly — is **correct**. What is blocked is
certification, not the science.

## 5. Why this stops here

Autonomous **STOP condition 8**: both blockers admit multiple scientifically
distinct repair paths and none was pre-frozen.

* `B1`: finer grid with the cell margin removed; a Lyapunov/geometric-drift
  bound; a one-sided chart reduction; a spectral bound on `K_e`.
* `B2`: a Bernstein range bound on the polynomial part (R2 precedent); a
  per-cell Taylor model / centred form (`R-A'` Device 2 precedent); lower degree
  traded against a larger point residual; a reformulated candidate basis.

Choosing among these is a scientific decision, and the campaign's governance
requires a pre-result anchor for whichever is chosen. No repair is improvised
here, and Phases 3-5 (second moments, `m > 1`, cost adjudication, production)
are **not** entered: they are all downstream of a certified SR enclosure that
does not yet exist.

## 6. One protocol under-specification, disclosed

`PROTOTYPE_PROTOCOL.md` §4 says "grid `64 x 64`" without naming the coordinate.
A uniform grid in `zeta` was used, `zeta` being the declared R4 production
variable in which the candidate is polynomial. A uniform grid in `y` would give
a different (and for this purpose worse) partition. Recorded rather than
silently chosen.
