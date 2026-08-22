# Independent Stage-A / Stage-D replication report

**Numerical verdict:** `FAIL` under the complete frozen Track 1A gate  
**Stage-A / Stage-D distinction:** `PASS`  
**Independent decomposition gate:** `FAIL` at pooled `m=20`  
**Protocol:** `76a5d40b4165758afb72a12dd93f302dd03cbf7db78184ef248156962cc9a79f`

## 1. Design executed

The run used `m={1,2,5,10,20,50}`, two independent replications, one million
paths per Stage-A `m` cell, one million ordinary-stop paths per direct Stage-D
replication, and one million disjoint ordinary-stop paths per independent
reconstruction replication. The master seed family was `2026082211`. There
were no common random numbers between Stage A and Stage D or between the direct
and reconstruction routes.

Stage-A paths used the minimum-dwell stop `tau_m`; Stage-D paths used the
ordinary stop and denominator `min(m,tau)`.

## 2. Gain and derivative distinction

Values are inverse-variance pooled across the two frozen replications.
`Delta_Gamma=Gamma_D-Gamma_A`; the derivative difference is its negative.

| `m` | `Gamma_A ± SE` | `Gamma_D ± SE` | `Delta_Gamma ± SE` | 95% CI | standardized effect | `d_D-d_A` |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 15.87283 ± 0.02852 | 15.91283 ± 0.02857 | +0.03999 ± 0.04037 | [-0.03913, +0.11911] | +0.00099 | -0.03999 |
| 2 | 13.21935 ± 0.02365 | 13.28614 ± 0.02370 | +0.06678 ± 0.03348 | [+0.00115, +0.13241] | +0.00199 | -0.06678 |
| 5 | 10.15767 ± 0.01768 | 10.21176 ± 0.01770 | +0.05409 ± 0.02502 | [+0.00504, +0.10313] | +0.00216 | -0.05409 |
| 10 | 7.08479 ± 0.01166 | 7.10962 ± 0.01167 | +0.02482 ± 0.01650 | [-0.00751, +0.05715] | +0.00150 | -0.02482 |
| 20 | 4.20764 ± 0.00672 | 4.26631 ± 0.00668 | +0.05867 ± 0.00947 | [+0.04010, +0.07724] | +0.00619 | -0.05867 |
| 50 | 2.21270 ± 0.00337 | 2.36592 ± 0.00332 | +0.15321 ± 0.00473 | [+0.14394, +0.16248] | +0.03238 | -0.15321 |

Both independently seeded `m=20` and `m=50` gain differences were positive,
and their pooled 95% CIs exclude zero. This satisfies the preselected
distinction rule. Results at the other `m` values are reported rather than
turned into additional significance gates.

## 3. Short cycles and the two mechanisms

`Gamma_B` is the ordinary-stop fixed-denominator gain. The stopping component
is `Gamma_B-Gamma_A`; the denominator component is `C_m`.

| `m` | `P(tau<m)` | `Gamma_B` | stopping component | `C_m ± SE` |
|---:|---:|---:|---:|---:|
| 1 | 0 | 15.91283 | +0.04000 | 0 exactly |
| 2 | 0.0000005 | 13.28613 | +0.06678 | 0.00000759 ± 0.00000759 |
| 5 | 0.0006470 | 10.20925 | +0.05157 | 0.00251193 ± 0.00008189 |
| 10 | 0.0073225 | 7.08705 | +0.00226 | 0.02256694 ± 0.00024308 |
| 20 | 0.0276720 | 4.18873 | -0.01891 | 0.07757686 ± 0.00045932 |
| 50 | 0.0894750 | 2.16446 | -0.04825 | 0.20146107 ± 0.00073596 |

At `m=20` and `m=50`, the stopping-time contribution is negative, while the
larger positive short-cycle correction makes the total Stage-D-minus-Stage-A
gain positive. This explicitly separates the two mechanisms.

At `m=2`, one short cycle appeared in two million direct paths. One replicate
therefore had a zero sample SE for `C_2`, making the protocol's ordinary
inverse-variance pooling formula undefined. The reported value combines the
retained raw-moment equivalents across equal-size replications. This is a
reporting edge-case correction, not a changed estimand, new data, or verdict
rule.

## 4. Independent decomposition correspondence

The direct route estimates `Gamma_D`. The disjoint route estimates
`Gamma_B+C_m` while retaining within-path covariance. The discrepancy is
`Gamma_D,direct-(Gamma_B+C_m)_reconstruction`.

| `m` | direct `Gamma_D` | independent reconstruction | abs discrepancy | combined SE | abs z | relative discrepancy |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 15.91283 | 15.81745 | 0.09532 | 0.04037 | 2.361 | 0.5990% |
| 2 | 13.28614 | 13.20087 | 0.08528 | 0.03350 | 2.546 | 0.6419% |
| 5 | 10.21176 | 10.14653 | 0.06524 | 0.02503 | 2.606 | 0.6389% |
| 10 | 7.10962 | 7.06246 | 0.04714 | 0.01650 | 2.858 | 0.6631% |
| 20 | 4.26631 | 4.23676 | 0.02955 | 0.00944 | **3.130** | 0.6926% |
| 50 | 2.36592 | 2.35390 | 0.01202 | 0.00469 | 2.564 | 0.5080% |

The frozen pooled rule required every cell to be at most three SE. The `m=20`
cell failed by `0.130` SE. All 12 per-replication cells were below four SE; the
largest was `2.881` SE. The direct and reconstruction estimators reuse their
respective paths across `m`, so the same positive route-level fluctuation is
visible across the grid.

Separately, the pathwise identity

`A_m^D T_tau = B_m^D T_tau +
1{tau<m}(1/tau-1/m)T_tau^2`

held to machine roundoff on every generated path in both routes, and the
minimum correction was nonnegative. This supports the algebra but does not
override the pre-frozen independent-route criterion.

**Independent decomposition criterion: FAIL.** No pooling rule, sample size,
or threshold was changed after exposure.

## 5. `m=1` control

On a shared 20,000-path stream, `tau_1=tau`, both windows, both gain
integrands, and the zero correction agreed bit-for-bit. The separately seeded
Stage-A/Stage-D estimates differed by `0.991` combined SE. The pooled new
four-route gain was `15.89280 ± 0.02018`, agreeing with the prior independent
`15.88769 ± 0.02850` within `0.146` combined SE.

**`m=1` control: PASS.**

## 6. Rho scaling

The sample transformation `rho(1-Gamma)` was evaluated for
`rho={0,0.25,0.5,0.75,1}`. The maximum algebraic implementation error was
exactly zero.

**Rho scaling: PASS.**

## 7. Numerical conclusion

The actual Stage-A/Stage-D distinction replicated in the preselected cells and
the human decomposition held pathwise. Nevertheless, the complete frozen
Track 1A numerical gate is `FAIL` because the independent pooled `m=20`
decomposition comparison exceeded three SE. The campaign stopped before Lean.

