# P5X R4 — the exact frozen SR model, restated before any transformation

Identical in content to `compute_optimization_r3_sr_symbolic/EXACT_SR_TARGET.md`;
restated here so that R4's algebra can be checked against it without following a
reference. **Nothing in R4 may alter anything on this page.**

| item | exact content |
|---|---|
| stored state | `y = (y^+, y^-)`, two-chart symmetric SR, no head start, `y_0 = (0,0)` |
| pre-update | `v^{+} = y^+ + z - 1/2`, `v^{-} = y^- - z - 1/2` |
| innovation | `z_t = raw_t - e`, `raw ~ iid N(0,1)`, so `z ~ N(-e, 1)` |
| recurrence | `y' = softplus(v) = log(1 + exp(v))` on each chart |
| alarm | `max(v^+, v^-) >= log A`, tested on the **pre-update** `v` |
| threshold | `A = 4581762885148045 / 8796093022208` exactly (`= 520.886133602749`) |
| corrected domain | `y in [0, log(1+A)]`, `log(1+A) = 6.25744942922713562368...` (erratum `D1`) |
| `c_SR` | `log A + 1/2 = 6.75553146432147319284...` |
| live region | `z in (l(y), u(y)) = (y^- - c_SR, c_SR - y^+)` |
| convention A | `w = min(m, tau)`, denominator `w`, terminal increment included |
| stopping | `tau = inf{t >= 1 : alarm after the update at t}`, inclusive, no dwell |
| `m` | `{1, 2, 3, 5}` |
| kernel / reward | `K_e`, `K_{z,e}`, `K_{z2,e}`, `rho_{1,e}`, `rho_{2,e}` of `P5X-T1` |
| first moment | `R_{SR,m}(e) = e + E_e[A_m]` via `g_r`, `h_j`, `S_j` |
| second moment | `E_e[Rbar^2]` via `G_{r,r'}`; `S_{SR,m} = E[Rbar^2] - R^2` |
| theorem interface | `R_max`, `s_min`, `M_2` into `P5X-T4/T6/T9` and Lean `X1`-`X6` |
