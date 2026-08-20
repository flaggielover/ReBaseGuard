# Phase-4C Exact SR Operator and Reachable Geometry

This note re-derives the frozen symmetric SR continuum system independently of
the Phase-4B prose. It is a feasibility lemma set, not a certificate of
`Gamma_SR>2`.

## Exact transition and continuation interval

Let `Y^+=log(1+R^+)`, `Y^-=log(1+R^-)`, `delta=1`, and
`A=520.3125`. Since

```text
R'^+ = exp(Y^+ + z - 1/2),
R'^- = exp(Y^- - z - 1/2),
```

the stable transition is

```text
q_+(y,z) = log(1+exp(y_+ + z - 1/2)),
q_-(y,z) = log(1+exp(y_- - z - 1/2)).
```

The plus chart remains live iff `y_+ + z - 1/2 < log A`; the minus
chart remains live iff `y_- - z - 1/2 < log A`. Therefore continuation
is exactly

```text
ell(y) < z < u(y),
ell(y) = y_- - log(A) - 1/2,
u(y)   = log(A) - y_+ + 1/2.
```

The signs in the Phase-4B specification are correct.

## Affine reduction

For current stopped-sum state `x=T_t`, define

```text
H(y,x)=E[Z_tau T_tau | Y_t=y,T_t=x].
```

On continuation, an innovation `z` changes the sum to `x+z`; on alarm,
the terminal reward is `z(x+z)`. Thus an affine continuation
`H(y,x)=a(y)x+b(y)` gives

```text
(Kf)(y)   = integral_ell^u f(q(y,z)) phi(z) dz,
(K_z f)(y)= integral_ell^u z f(q(y,z)) phi(z) dz,

a = Ka + r_a,
b = Kb + K_z a + r_b,
```

where

```text
r_a = integral_alarm z phi(z) dz
    = phi(u)-phi(ell),

r_b = integral_alarm z^2 phi(z) dz
    = Phi(ell)-ell phi(ell)+Phi(-u)+u phi(u).
```

At reset, `y=(0,0)` and `x=0`, so `Gamma_SR=b(0,0)`.

## Rigorous compact reachable enclosure

The naive live square is `0<=Y^+,Y^-<L`, where `L=log(1+A)`. A
strictly smaller invariant enclosure follows from the exact identity

```text
R'^+ R'^- = exp(Y^+ + Y^- - 1),
```

which is independent of `z`. Let `C` solve

```text
exp(C)=(1+A)(1+exp(C-1)/A).
```

Equivalently,

```text
exp(C)=(1+A)/(1-(1+A)/(eA)).
```

If `Y^++Y^-<=C`, the successor product is at most `exp(C-1)`. For a
fixed product `p` and live `0<R^+,R^-<A`, the convex function
`R^+ + p/R^+` is maximized at an endpoint, giving

```text
(1+R'^+)(1+R'^-) <= (1+A)(1+p/A) <= exp(C).
```

Starting from reset and iterating this inequality proves the invariant. Arb
certifies

```text
C <= 6.7161439552,
exp(-1) <= R^+R^- <= 303.73145983,
Y^++Y^- <= 6.7161439552.
```

The full-square sum bound would be `2L=12.51269934`. The reachable enclosure
also implies each nonreset coordinate is at least
`log(1+exp(-1)/A)=0.0007067857`. The reset point is included separately.

The continuation width is

```text
u-ell=2log(A)+1-(Y^++Y^-),
```

so Arb proves `u-ell>=6.79271523` on the enclosure. Unreachable upper-right
states are the only source of the nearly closed continuation strips in the
naive square.

This enclosure is rigorous but not claimed to equal the exact reachable-set
closure.

## Dimension and symmetry

The state cannot be reduced to one scalar. After two continued observations,
the Jacobian determinant from `(z_1,z_2)` to `(Y_2^+,Y_2^-)` is

```text
sigma(t_2^+) sigma(t_2^-)
  [sigma(-z_1-1/2)-sigma(z_1-1/2)],
```

which Arb proves nonzero at `z_1=1,z_2=0`. Hence the reachable set has
two-dimensional interior.

Reflection sends `(y_+,y_-,z,x)` to `(y_-,y_+,-z,-x)`, swaps the
transition coordinates, and preserves the terminal product. Therefore

```text
a(y_+,y_-)=-a(y_-,y_+),
b(y_+,y_-)= b(y_-,y_+).
```

Computation may be restricted to one half-domain, with `a=0` on the diagonal.
The full-domain prototypes retain both halves so symmetry can serve as an
independent numerical check.

## Transition regularity

For `s(t)=log(1+exp(t))`,

```text
s'(t)=sigma(t) in (0,1),
s''(t)=sigma(t)(1-sigma(t)) <= 1/4.
```

Thus `q_+` is increasing in `y_+` and `z`, while `q_-` is increasing in
`y_-` and decreasing in `z`. Each target coordinate is globally 1-Lipschitz
in its source coordinate and in `z`, and globally convex in its affine
argument. On the reachable continuation set, Arb bounds the sigmoid slopes
between approximately `0.000707` and `0.998082`. These bounds explain the
normal linear refinement observed by the interval prototype.
