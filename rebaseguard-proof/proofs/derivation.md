# Exact Dynamic Equations for the ReBaseGuard Lemma

## Target and state reduction

For the two-sided CUSUM with `k=1/2` and `h=5`, let the current state be
`s=(p,m)=(S_t^+,S_t^-)` and let `x=T_t`. If `N` is the remaining time to
alarm, `W=Z_{t+N}`, and `Y=sum_{j=1}^N Z_{t+j}`, then the future depends on
the past only through `s`. Therefore

```text
E[Z_tau T_tau | s,x] = E_s[W(x+Y)] = a(s)x+b(s),
a(s)=E_s[W],  b(s)=E_s[WY].
```

In particular, `Gamma=E[Z_tau T_tau]=b(0,0)`. This is a direct certification
route; no sign is assumed for `E[Z_tau T_{tau-1}]`, and the invalid shortcut
from `E[Z_tau^2]>2` is not used.

## Reachable state space

A continuing update is

```text
p'=max(0,p+z-k),  m'=max(0,m-z-k).
```

Starting at the origin, the reachable pre-alarm states lie on either axis or
in the triangle `p>0,m>0,p+m<h-2k`. The first interior state must be entered
from an axis, where its coordinate sum is the previous active coordinate
minus `2k`, hence below `h-2k`. Every subsequent interior-to-interior update
reduces the sum by another `2k`. Resets return to an axis.

## Fredholm equations

Define

```text
ell=m-h-k,  u=h+k-p,
q(s,z)=(max(0,p+z-k),max(0,m-z-k)).
```

Continuation is exactly `ell<z<u`. With `phi,Phi` denoting the standard
normal density and CDF,

```text
(Kf)(s)   = integral_ell^u f(q(s,z)) phi(z) dz,
(K_zf)(s) = integral_ell^u z f(q(s,z)) phi(z) dz.
```

The absorbing rewards are the exact full-tail moments

```text
r_a=phi(u)-phi(ell),
r_b=u phi(u)+1-Phi(u)+Phi(ell)-ell phi(ell).
```

First-step conditioning gives

```text
a=Ka+r_a,
b=Kb+K_z a+r_b.
```

Reflection of every future increment swaps `(p,m)`, negates `W` and `Y`, and
preserves `WY`. Hence `a(p,m)=-a(m,p)` and `b(p,m)=b(m,p)`.

## Global block contraction and resolvent

Let `G_n=sum_{j=1}^n Z_j`. Pathwise,

```text
S_n^+ >= p+G_n-nk,  S_n^- >= m-G_n-nk.
```

Thus either `G_n>=h+nk` or `G_n<=-(h+nk)` forces absorption by time `n`
from every reachable state. Since `G_n~N(0,n)`,

```text
q_n=2(1-Phi((h+nk)/sqrt(n)))>0,
||K^n||_infinity <= beta_n:=1-q_n<1.
```

For `t=jn+r`, `0<=r<n`, sub-Markovity gives

```text
||(I-K)^(-1)||_infinity
 <= sum_{t>=0} ||K^t||_infinity
 <= n/(1-beta_n)=:C_n.
```

The certificate and auditor evaluate these quantities with Arb balls from
exact inputs; no sampled state grid enters this argument.

## Residual propagation

For continuum residual bounds

```text
||a_hat-Ka_hat-r_a|| <= delta_a,
||b_hat-Kb_hat-K_z a_hat-r_b|| <= delta_b,
```

and `mu=||K_z||<=E|Z|=sqrt(2/pi)`, the exact errors obey

```text
||a-a_hat|| <= C delta_a=:E_a,
||b-b_hat|| <= C(delta_b+mu E_a)=:E_b.
```

Therefore `Gamma` lies in the Arb enclosure of `b_hat(0,0)+[-E_b,E_b]`.
The proof succeeds only when an independent audit recomputes a lower endpoint
strictly greater than `2`.
