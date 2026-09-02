# P5X R3 — the exact frozen SR target

Reconstructed from the frozen sources before any architecture is proposed. **No
candidate method in R3 may alter anything on this page.**

Sources: `p7_statistical_consequences/src/rebaseguard_p7/detectors.py::sr_update`
(restated verbatim from Stage-D `_sr_update`), `p5x/FROZEN_THEOREM.md` §1–§2,
`p5x/PROOF.md` `L1`, `p5x/errata/D1_SR_DOMAIN_ERRATUM.md`.

---

## 1. Recurrence (frozen, byte-for-byte)

```python
def sr_update(yp, ym, z, log_thr):
    log_r_plus  = yp + z - 0.5
    log_r_minus = ym - z - 0.5
    return (np.logaddexp(0.0, log_r_plus), np.logaddexp(0.0, log_r_minus),
            log_r_plus >= log_thr, log_r_minus >= log_thr)
```

## 2. Objects

| item | exact content |
|---|---|
| threshold | `A = 520.886133602749`, exact runtime rational `4581762885148045 / 8796093022208` |
| stored state | `y = (y^+, y^-)`, symmetric two-chart, no head start, `y_0 = (0,0)` |
| **pre-update quantity** | `v^{+} = y^+ + z - 1/2`, `v^{-} = y^- - z - 1/2` |
| **softplus update** | `y' = softplus(v) = log(1 + exp(v))` |
| **alarm boundary** | alarm iff `max(v^+, v^-) >= log A` — tested on the **pre-update** `v`, not on the stored state |
| **corrected state domain** | `y in [0, log(1+A)]`, `log(1+A) = 6.25744942922713551796607132378`, per erratum `D1` (`b_SR = log A` is false) |
| alarm margin | `c_SR = log A + 1/2 = 6.75553146432147308692733728672` |
| continuation interval | `(l(y), u(y)) = (y^- - c_SR, c_SR - y^+)`; `u >= c_SR - log(1+A) = 0.49808203509433756896 > 0` |
| innovations | `z_t = raw_t - e`, `raw ~ iid N(0,1)`, so `z ~ N(-e, 1)` |
| stopping | `tau = inf{t >= 1 : alarm after the update at t}`, inclusive, no minimum dwell |
| window (convention A) | `w = min(m, tau)`, denominator `w`, terminal increment included |
| `m` | `{1, 2, 3, 5}` |

## 3. Operators (`P5X-T1`, detector-generic)

```text
(K_e f)(y)     = int_{l(y)}^{u(y)} f(q_SR(y,z)) phi(z + e) dz
(K_{z,e} f)(y) = int_{l(y)}^{u(y)} z f(q_SR(y,z)) phi(z + e) dz
(K_{z2,e} f)(y)= int_{l(y)}^{u(y)} z^2 f(q_SR(y,z)) phi(z + e) dz
q_SR(y, z)     = ( softplus(y^+ + z - 1/2) , softplus(y^- - z - 1/2) )
rho_{1,e}(y)   = phi(u+e) - phi(l+e) - e ( 1 - Phi(u+e) + Phi(l+e) )
rho_{2,e}(y)   = [ (u+e)phi(u+e) + 1 - Phi(u+e) ] - 2e phi(u+e) + e^2 (1 - Phi(u+e))
               + [ -(l+e)phi(l+e) + Phi(l+e) ] + 2e phi(l+e) + e^2 Phi(l+e)
h_1 = 1 - K_e 1 ,  h_j = K_e h_{j-1} ,  S_0 = rho_{1,e} ,  S_j = K_{z,e} h_j
g_r = (I - K_e)^{-1} S_r
```

## 4. Targets

```text
R_{SR,m}(e) = e + (1/m) sum_{r<m} [ g_r(y_0) - sum_{t=r+1}^{m-1} (K_e^{t-r-1} S_r)(y_0) ]
                + sum_{t=1}^{m-1} (1/t) sum_{i=1}^{t} (K_e^{i-1} S_{t-i})(y_0)

E_e[Rbar^2] : via P5X-T2 / PROOF.md L2, pair functions
              G_{r,r'} = (I-K_e)^{-1} K_{z,e} K_e^{r-r'-1} S_{r'}   (r > r')
              G_{r,r}  = (I-K_e)^{-1} [ delta_{r,0} rho_{2,e} + K_{z2,e} h_r ]
S_{SR,m}(e) = E_e[Rbar^2] - R_{SR,m}(e)^2
```

with `y_0 = (0,0)` the reset state.

## 5. Theorem consumer interface

Unchanged and untouched by R3: the certified scalars `R_max = sup_e |R|`,
`s_min = inf_e S`, `M_2 = sup_e E[Rbar^2]` feed `P5X-T4`, `P5X-T6`, `P5X-T9` and
the Lean spine `X1`–`X6`. **Every R3 construction lives strictly below this
interface**; nothing R3 does is visible to a theorem statement.

## 6. What R3 may and may not change

| may change | may **not** change |
|---|---|
| how the `z`-integral is enclosed | the integral itself |
| how `softplus` is bounded on a panel | the `softplus` update |
| the state-patch and panel geometry | the state domain `[0, log(1+A)]` |
| the polynomial basis of a candidate | the certified target `R_{SR,m}`, `S_{SR,m}` |
| the resolvent bound | the recurrence, alarm test, `tau`, convention A |
| — | the enclosure semantics (outward-rounded, continuum, no sampling) |
