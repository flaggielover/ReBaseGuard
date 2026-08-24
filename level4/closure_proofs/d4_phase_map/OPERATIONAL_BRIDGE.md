# D4 operational bridge

The operational overlay is a consequence check, not a boundary-discovery or
discontinuity test.

| m | rho | theorem class | lambda | cycle ARL | reference MSE | e ACF1 | direction ACF1 |
|---:|---:|---|---:|---:|---:|---:|---:|
| 20 | 0.20 | LOCALLY-STABLE | -0.6489 | 279.78 | 0.0393 | -0.240 | -0.295 |
| 20 | 0.40 | LOCALLY-UNSTABLE | -1.2977 | 261.76 | 0.0458 | -0.440 | -0.575 |
| 50 | 0.60 | LOCALLY-STABLE | -0.8139 | 323.71 | 0.0269 | -0.369 | -0.515 |
| 50 | 0.90 | LOCALLY-UNSTABLE | -1.2209 | 277.11 | 0.0545 | -0.405 | -0.604 |
| 100 | 1.00 | LOCALLY-STABLE | -0.7742 | 322.39 | 0.0494 | -0.300 | -0.457 |

Within the paired `m=20` and `m=50` cells, higher reuse changes all four
reported metrics: cycle ARL falls, reference MSE rises, and the two lag-one
dependence measures become more negative. Those cell contrasts are compatible
with stronger feedback, but the sparse pre-frozen overlay does not establish
an abrupt change at `rho_c`.

Historical Stage-D D2.5 remains exactly **MATHEMATICAL, NOT OPERATIONAL**.
Its `m`-direction experiment found smooth monotone behavior through the
historical crossing; this later rho-direction consequence check neither
rewrites nor rescues that negative result.
