# Frozen Phase-4B Detector Definition

This artifact fixes the exact detector used by every Phase-4B computation. It
is diagnostic only and does not alter the protected Level-3 CUSUM proof.

For residuals `Z_t=X_t-e`, with physical observations `X_t iid N(0,1)`, set
`delta=1` and initialize `R_0^+=R_0^-=0`. Update both charts from the same
observation:

```text
Lambda_t^+ = exp(Z_t-1/2),       Lambda_t^- = exp(-Z_t-1/2),
R_t^+ = (1+R_(t-1)^+) Lambda_t^+,
R_t^- = (1+R_(t-1)^-) Lambda_t^-.
```

With `A=520.3125`, selected by ARL-only calibration,

```text
tau_D = inf{t>=1 : max(R_t^+,R_t^-) >= A}.
```

The boundary is inclusive and checked after both updates. If both charts cross,
the larger post-update chart supplies the alarm direction; exact equality is a
recorded tie. The detector resets to `(0,0)` at every new cycle.

The numerical implementation stores `Y^+=log(1+R^+)` and
`Y^-=log(1+R^-)`. Its softplus recursion is algebraically identical to the raw
recursion. The scalar log implementation and a separately coded raw-state
replay are compared path by path in `pathwise_replay.json` and the Phase-4B
tests.

The reused `m=1` reference is the alarm-causing physical observation,
`e+Z_tau`. Mixed reuse is

```text
e_next = rho (e+Z_tau) + (1-rho) X_fresh,
X_fresh iid N(0,1), independent of the stopped path.
```

Neither `delta` nor `A` was selected using the stopped-score statistic.
