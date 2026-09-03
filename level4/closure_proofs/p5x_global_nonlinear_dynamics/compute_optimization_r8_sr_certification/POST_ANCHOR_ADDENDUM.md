# R8 — post-Checkpoint-J addendum: lemma `B1-L6` (drift coupling)

**Disclosed as added AFTER Checkpoint J** `55c5f1de9eb07a855948f92215b38a24b8321c5d`.
It changes no threshold, no criterion, no algorithm parameter and no scientific
object. It is a mathematical fact needed to obtain a `C_SR` valid on the whole
`e`-cell from the frozen algorithm's point outputs.

## Why it is needed

The frozen `B1` algorithm computes `C_SR` for a given `e`-cell by bounding each
`z`-sub-interval's Gaussian mass at its own worst `e*`. Run on the *point*
drifts it converges immediately (`e = 1/4` in `102` sweeps, `e = 0` in `753`).
Run on the **cell** `[24/100, 26/100]` it does **not** converge: `q` stays at
exactly `1.0` for all `4000` sweeps, because `sum_s max_e mass_s(e) > 1` when
each sub-interval is maximised at a different `e*`, so the survival bound can
never drop below `1`. This is the same failure mode as the Checkpoint-I
resolvent, now confined to the `e`-cell case.

## `B1-L6` — `E_y[tau^-]` is non-increasing in `e`

*Proof (pathwise coupling, not empirical monotonicity).* Fix a single sequence
of standard normals `raw_t`, and let `e_1 <= e_2` with `z_t(e) = raw_t - e`.
Write `y_t(e)` for the minus-chart state and `v_t(e) = y_{t-1}(e) - z_t(e) - 1/2`.

Base: `y_0(e_1) = y_0(e_2) = y`.
Step: assume `y_{t-1}(e_2) >= y_{t-1}(e_1)`. Then

```text
v_t(e_2) = y_{t-1}(e_2) - raw_t + e_2 - 1/2
        >= y_{t-1}(e_1) - raw_t + e_1 - 1/2 = v_t(e_1) ,
```

using the inductive hypothesis and `e_2 >= e_1`. Since `softplus` is increasing,
`y_t(e_2) = softplus(v_t(e_2)) >= softplus(v_t(e_1)) = y_t(e_1)`. ∎ (induction)

The alarm is `v_t >= log A`, so `v_t(e_2) >= v_t(e_1)` gives
`{tau^-(e_1) <= t} subset {tau^-(e_2) <= t}` for every `t`, hence
`tau^-(e_2) <= tau^-(e_1)` pathwise and `E_y[tau^-(e_2)] <= E_y[tau^-(e_1)]`
for every initial `y`. ∎

**Consequence.** `sup_{e in [e_lo, e_hi]} C_SR(e) = C_SR(e_lo)`, so the cell
bound is obtained from the frozen algorithm at the single point `e = e_lo`.

This is a coupling argument on a fixed innovation sequence — the same device as
`B1-L1` — and is therefore admissible under `B1-Q7` / `F6`, which forbid
*empirical* monotonicity (a monotonicity observed in output and assumed), not
proved monotonicity.

## What this does not do

It does not rescue the frozen cell-mass construction, which remains recorded as
non-convergent on an `e`-cell. It supplies a different, proved route to the same
scalar. The `B1` binding criteria `B1-Q3`/`Q4`/`Q5` are stated at the points
`e = 1/4` and `e = 0` and are unaffected.
