# SR prototype — repair-options audit

**This is an audit, not a repair.** Nothing here is implemented, and no path is
chosen. Each option is stated with the evidence that bears on it so the choice
can be made deliberately and given its own pre-result anchor, as governance
requires. Written because autonomous STOP condition 8 was reached: both
blockers admit multiple scientifically distinct paths and none was pre-frozen.

---

## Blocker `B2` — interval dependency in the certified residual

### Measured scaling — refinement alone is ruled out

| cells per side | cell residual at `zeta = (0.025, 0.025)` | ratio to previous |
|---|---|---|
| 64 | `6.736713e+04` | — |
| 128 | `1.889230e+03` | `35.66` |
| 256 | `3.018184e+02` | `6.26` |
| 512 | `8.746755e+01` | `3.45` |
| 1024 | `3.734004e+01` | `2.34` |
| 2048 | `1.740363e+01` | `2.15` |
| 4096 | `8.201415e+00` | `2.12` |

The ratio settles at `~2.12` per halving, i.e. the bound is **linear in the cell
width**, the signature of first-order interval dependency. Extrapolating from
`8.20` at `4096` cells per side to a usable `~1e-6` requires a further factor
`8.2e6`, i.e. `~3.4e10` cells per side, `~1.2e21` cells.

**Grid refinement alone is definitively ruled out.** Any viable repair must
change the *range-bounding method*, not the partition.

### Options

| # | path | precedent | expected gain | cost | main risk |
|---|---|---|---|---|---|
| `B2-a` | **Bernstein range bound on the polynomial part**, with the kernel part bounded separately | R2 `C2` / `_max_abs_on_reachable`, which gave a bit-identical bound at `12.04x` for CUSUM | Bernstein is exact at the vertices and converges quadratically under subdivision; should remove the first-order term entirely | one Bernstein conversion per cell, `O(n^2)` per cell at `n=16` | the residual is **not** a polynomial — `sum_k G_k(zeta) I_k(l(zeta),u(zeta),e)` is polynomial in `zeta` only through `G_k`; `I_k` depends on `zeta` through `l`, `u`. The split must be proved sound, and the `I_k` factor still needs its own range bound |
| `B2-b` | **per-cell Taylor model / centred form** in `zeta` | `R-A'` Device 2, which removed a `4.96e41` amplification for CUSUM | a first-order centred form makes the width `O(width^2)`; from the table that alone buys `~10^4` at `G=4096` | one derivative evaluation per cell | needs `d/dzeta` of the whole residual including `I_k`, i.e. `dI_k/dl`, `dI_k/du` — available in closed form (`phi` at the endpoints, by the same exponent identity R5 §8 used for the `k`-derivative) |
| `B2-c` | **lower candidate degree** | — | smaller monomial coefficients, hence less cancellation | free | the point residual grows: degree 8 gives `rho_1` only to `9.7e-4`, so `delta` cannot go below that. Probably incompatible with a `0.2` half-width once multiplied by `C ~ 500` |
| `B2-d` | **reformulated candidate basis** | — | unknown | unknown | the panel-free closed form of R4 §14 requires the *monomial* expansion in `zeta` to group by `k = i-j`; a Chebyshev candidate must be converted to monomials before the kernel, which reinstates the large coefficients. This path likely does not exist without changing the kernel algebra, which would reopen R4 |

**Assessment.** `B2-b` is the closest analogue of the repair that already worked
once in this campaign for exactly this defect class, and the derivative it needs
is available in closed form by machinery R5 already proved. `B2-a` is
complementary and could be combined. `B2-d` appears blocked by the R4 algebra
and would reopen a settled result.

## Blocker `B1` — no resolvent bound

### Why the frozen method cannot be rescued by parameters

The per-sweep excess of a `max`-over-box bound is `~|grad v| * (d + w)` where
`d = b_SR/G` is the cell width and `w = 2 c_SR/Z` the `z`-sub-interval width,
against a true per-sweep decay of `~v/E[tau]`. With `|grad v| ~ v/b_SR` this
needs

```text
(d + w) / b_SR  <<  1 / E[tau]      i.e.   d + w  <<  6.257 / 130  =  0.048 .
```

So `G >> 130` and `Z >> 280` — say `G = 512`, `Z = 2048`. That is not absurd,
but the current implementation materialises a `(G, G, Z)` tensor, which at those
sizes is `5.4e8` doubles ~ `4.3 GB` per array and several such arrays for the
sparse tables. It would need restructuring to stream over `z`.

Note this is an *estimate of what the frozen method would need*, not a claim
that it then works; the `max` is still adversarial and the estimate assumes the
excess is dominated by the box width.

### Options

| # | path | expected `C` | cost | main risk |
|---|---|---|---|---|
| `B1-a` | **finer grid, margin removed, streamed over `z`** | the true `sup_x E_x[tau]`, MC-scoped at `130` (`e=0.25`) to `472` (`e=0`) | `G=512`, `Z=2048`, `~200` sweeps; needs an out-of-core or streaming reduction | still adversarial; the estimate above may be optimistic, and a failed second attempt costs another anchor |
| `B1-b` | **Lyapunov / geometric drift**: find `W >= 1` and `lambda < 1` with `K_e W <= lambda W + b 1_S` | analytic, no grid | cheap once `W` is found | finding `W` is genuine mathematical work; the natural candidate `W = xi^theta` must be checked against `E[Lambda^theta]`, where `E[Lambda] = e^{-e}` on the plus chart and `e^{+e}` on the minus chart |
| `B1-c` | **one-sided chart reduction**: `E_x[tau] <= E_{x^-}[tau^-]` | a 1-D problem, so a fine grid is cheap | very cheap | gives a *larger* `C`; needs the one-sided value iteration to converge, which faces the same adversarial issue in 1-D but at a grid resolution that is affordable |
| `B1-d` | **spectral bound on `K_e`** via the panel-free kernel already built | `1/(1 - ||K_e^n||^{1/n})` | reuses R6 machinery | `||K_e^n||_inf = sup_x P_x(tau > n)` is the same object; no shortcut unless a weighted norm is used |

**Assessment.** `B1-c` combined with `B1-a` on the resulting 1-D problem is the
cheapest credible route and reuses the frozen construction at a resolution that
is affordable. `B1-b` is the most elegant and would give a clean analytic
constant, but is open-ended.

## What is already established and must not be re-derived

* The panel-free architecture is **fast**: `0.4470 ms` per cell, `1.8 s` for a
  full `64 x 64` certified residual sweep, `0` panels, `0` softplus.
* The R6 evaluator's conditioning is **closed**: amplification `1.0027e2`, flat
  across 192-512 bits.
* The `zeta`-polynomial approximation space is **adequate**: `rho_1` to relative
  `2.5e-5` at degree 16 with maximum monomial coefficient `0.168`.
* The pipeline is **scientifically correct**: candidate-implied
  `R_{SR,1}(0.25) = -1.590342` against Monte Carlo `-1.592117 +/- 0.001251`.
* `C_SR` is **small**: MC-scoped `129.6` at `e = 0.25`, `472.1` at `e = 0`.
* Grid refinement alone **cannot** fix `B2` (table above).
