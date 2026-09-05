# CUSUM raw-variable kernel — implementation map

Reconstructed from the frozen artifacts, not from old code names.

## Raw vs old g-variable — the separation that matters

| | old g-variable | frozen raw-variable |
|---|---|---|
| unknown | `g = R − e` | `F = R` |
| reward | `rho_1 = phi_u − phi_l − e(1 − Phi_u + Phi_l)` | `rho_1^raw = phi_u − phi_l` |
| source | `ra_certifier.reward_rho1` | `raw_certifier.reward_rho1_raw` |
| certifier | `ra_certifier.certify_at_exact_drift` | `raw_certifier.certify_raw_at_exact_drift` |

`ra_certifier.certify_at_exact_drift` certifies a **different formulation** and
may be used only as a correspondence reference. It is never on the production
path; a test enforces this.

## Geometry (frozen)

`c = c_CUSUM = h + k = 11/2`, `u = c − x^+`, `l = x^- − c`, survival `l < z < u`,
update `T(x,z) = (max(0, x^+ + z − 1/2), max(0, x^- − z − 1/2))`, `z = raw − e`,
weight `phi(z+e)`.

## The DAG

| object | frozen equation | deps | representation | ledger | unit class |
|---|---|---|---|---|---|
| `h_1` | `1 − Phi(u+e) + Phi(l+e)` | — | closed form BiPoly | exact | `h` |
| `h_j`, j=2..4 | `K_e h_{j−1}` | `h_{j−1}` | deg-12 exact-dyadic Chebyshev + certified defect | `B_kernel` | `h` |
| `S_0` | `phi(u+e) − phi(l+e)` | — | closed form BiPoly | exact | `S` |
| `S_r`, r=1..4 | `K_{z,e} h_r + e K_e h_r` | `h_r` | deg-12 candidate + defect | `B_kernel` | `S` |
| `F_r`, r=0..4 | `(I − K_e)^{-1} S_r` | `S_r` | deg-12 candidate + equation defect | `B_candidate` | `F` |
| `dF_r`, r=0..4 | `dF = K dF + (d_e K) F + d_e S` | `F_r`, `S_r`, `h_r` | deg-12 candidate + defect | `B_candidate` | `dF` |

Exact identity used, not assumed: `d_e h_1 = −S_0^raw`.

`K_e` and `K_{z,e}` are supplied symbolically by
`rebaseguard_certify.residual._kernel_polynomials(cand, phi_coeffs, z_weight=0|1)`.
**Every argument to it is a degree-12 exact-dyadic candidate** — that is the
frozen Gate-2C lesson: feeding a high-degree exact series in its place is what
blew the Gate-2C cost budget.

## Assembly (frozen, from CHECKPOINT.md §3)

```
R_m = (1/m) sum_{r<m} F_r(x0) + sum_{t=1}^{m-1} (1/t − 1/m) sum_{r<t} (K_e^{t−r−1} S_r)(x0)
m=1: F_0
m=2: (F_0+F_1)/2 + S_0/2
m=3: (F_0+F_1+F_2)/3 + (2/3)S_0 + (1/6)(K S_0 + S_1)
m=5: (1/5)sum F_r + (4/5)S_0 + (3/10)(K S_0 + S_1) + (2/15)(K^2 S_0 + K S_1 + S_2)
     + (1/20)(K^3 S_0 + K^2 S_1 + K S_2 + S_3)
```
`R'_m` is the same combination of `dF_r` and `d_e`-differentiated finite terms.
Window convention: `w = min(m, tau)`, inclusive stopping, Stage-D convention A —
the random denominator is preserved; no Stage-A min-dwell semantics.
