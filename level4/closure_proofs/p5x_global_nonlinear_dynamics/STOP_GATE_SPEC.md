# P5X single-cell stop-gate — specification, declared before the run

Checkpoint A fixed the stop-gate's **rule** (`CODEX_HANDOFF.md` §3 step 3,
`PROOF_OBLIGATIONS.md` §4 step 3):

> Build the certified enclosure `C1` for exactly one `e`-cell, one detector,
> `m = 1`. Publish the achieved half-width. If it exceeds `0.2`, **stop and
> re-plan**; do not scale.

It did **not** pin which detector, which `e`-cell, which precision or which
parameters. Those are chosen here, once, and recorded before the computation is
run, by rules stated in advance. Nothing below may be revised after seeing the
result.

## 1. Detector — CUSUM

Forced, not chosen: `DEFECT_REGISTER.md` `D1` bars any SR certified solve until
the SR state-square defect is adjudicated. CUSUM is unaffected by `D1` and is
also the detector with an existing certified precedent at `e = 0`.

## 2. Window — `m = 1`

Fixed by the frozen rule.

## 3. `e`-cell — `[0.24, 0.26]`

Selection rule, stated before running: **take the cell that binds
`P5X-T4`** — the cell containing the location of `sup_e |R_{CUSUM,1}|`, where the
margin to the `2` of `H3b` is smallest. The feasibility probe
(`feasibility/results/reduction_probe.json`, Checkpoint A) locates that maximum
at `e = 0.25` with `|R| ~ 1.576`.

This is deliberately the **least** favourable cell available:

* it carries the campaign's tightest theorem margin (`2 - 1.576 = 0.424`);
* it sits in the steepest part of the map (`R'(0) ~ -14.9`), where a low-degree
  polynomial candidate has the most work to do;
* its drift is small, so the alarm is nearly as slow as at `e = 0` and the
  resolvent constant is nearly worst-case. Larger `|e|` alarms faster and gives
  strictly better constants.

Cell half-width `0.01` in `e` contributes `0.01` of the `0.2` budget directly,
because `R(e) = e + g_0(x_0; e)` carries the cell's own `e`-range. A cover of
`[0, 12]` at this granularity is `600` cells, which is the order assumed in
`CERTIFICATE_PLAN.md` §6.

## 4. Numerical parameters — all inherited, none tuned

| parameter | value | provenance |
|---|---|---|
| interval backend | python-flint / FLINT-Arb, outward-rounded real balls | `closure/04_ARB_CERTIFICATE.md` §4 |
| working precision | `256` bits | existing residual certificate default |
| Chebyshev candidate degree | `12` | the degree of the certified `Gamma` run (`04_ARB_CERTIFICATE.md` §3.3) |
| candidate quadrature order | `400` | existing `construct_candidate_payloads` default |
| dyadic rounding | `scale_bits = 50` | same |
| `phi` Maclaurin order | `50` | existing `certify_continuum_residuals` default |
| Bernstein subdivision depth | `3` | same |
| reachable-set cover | `p = r t`, `m = r (1-t)`, `r in [0,1]`, `r in [1,4]`, axis tails `r in [4,5]` | `rebaseguard_certify.residual._max_abs_on_reachable`, reused unmodified |
| resolvent block length `n` | minimiser of `n / q_n` over `n in {1,…,60}` | declared here; `n` is an internal parameter of a valid bound, not a tolerance |

## 5. Method

1. **Candidate (not proof).** Solve `g = K_{e0} g + rho_{1,e0}` at the cell
   midpoint `e0 = 0.25` by tensor-Chebyshev collocation in double precision;
   round the Chebyshev coefficients to exact dyadic rationals. From this point
   the floating solver leaves the proof path.
2. **Certified residual.** With `e` carried as an Arb **ball covering the whole
   cell** `[0.24, 0.26]`, expand `phi(z + e)` as a truncated Maclaurin series in
   `z` with a rigorous uniform Lagrange remainder, substitute the exact dyadic
   candidate into `q(x,z)`, integrate in `z` symbolically over the three reset
   panels in both reachable regimes, and bound
   `res = ghat - K_e ghat - rho_{1,e}` on the **continuum** of the reachable set
   by tensor Bernstein conversion. No state is sampled.
3. **Resolvent.** Prove, from scratch and with the drift explicit, that from any
   live state `G_n >= h + nk` forces a plus-arm alarm within `n` steps and
   `G_n <= -(h+nk)` forces a minus-arm alarm, so
   `sup_x P_x(tau > n) <= 1 - q_n(e)` and
   `‖(I - K_e)^{-1}‖_inf <= n / q_n(e)`, with `q_n` evaluated on the `e`-ball.
   This needs no monotonicity in `e` and imports no constant, so
   `DEFECT_REGISTER.md` `D3` does not bite.
4. **Propagation.** `|g - ghat| <= ‖(I-K_e)^{-1}‖ · delta` in sup norm, hence
   `R_{CUSUM,1}(e) in [0.24, 0.26] + ghat(0,0) +/- C·delta` for every `e` in the
   cell, using `R(e) = e + g_0(x_0; e)` from `PROOF.md` `L1.7`.

`delta = (Bernstein continuum residual) + (11 sup|ghat| + 2 + 2 e_hi (c_D + e_hi)) * phi_error`,
the second term being the rigorous allowance for the `phi` truncation inside the
kernel (integration length `<= 11`) and inside the two `phi` and two `Phi` terms
of the reward.

## 6. The binding decision rule (frozen, not reinterpretable)

```text
achieved half-width <= 0.2   ->  STOP_GATE = PASS
achieved half-width >  0.2   ->  STOP_GATE = FAIL
```

The achieved half-width is the radius of the reported enclosure of
`R_{CUSUM,1}` over the whole cell, i.e.
`0.01 (the e-cell) + rad(ghat(0,0)) + C·delta`.
