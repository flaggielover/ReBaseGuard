# Rigorous SR local-instability certificate

**Status:** `SR-GAMMA-CERTIFIED`

This document records the optional, post-Lean Arb rigor upgrade. It does not
rewrite the frozen historical `OPEN` reports or alter the closed SR derivative
theorem. The certificate applies to the exact runtime threshold rational

```text
A = 4581762885148045 / 8796093022208.
```

## Certified chain

At 192-bit Arb precision, the exact-dyadic degree-16 spectral candidate has the
global continuum residual bounds

```text
epsilon_a <= 4.5043909378315058215843298940788024066e-6
epsilon_b <= 4.0038134251523670398163874537129303724e-3.
```

Both bounds cover all 1,210 cells in the symmetry-reduced reachable live-state
superset. Each cell uses a Bernstein continuum bound and an exact adaptive
partition of the full state-dependent continuation interval. There is no
sampled-state inference, artificial Gaussian truncation, or omitted tail term.
The reset state is certified separately.

The previously certified 250-step monotone block argument supplies

```text
||(I-K)^-1||_inf <= 25000/19.
```

With `||K_z|| <= sqrt(2/pi)`, outward-rounded coupled propagation gives

```text
Gamma_SR in
[5.8003917995084423356616334171917868138,
 28.781285803081492059266061976370530081].
```

The lower endpoint exceeds 2 by
`3.8003917995084423356616334171917868138`, so the rigorous local-instability
inequality is certified.

## Certificate artifacts

- `results/sr_monotone_contraction.json`: monotone resolvent component;
- `results/sr_residual_global_a.json`: global `a` residual and exact cover;
- `results/sr_residual_global_b.json`: global `b` residual and coupled
  propagation;
- `certificate/audit_sr_resolvent.py`: independent resolvent auditor;
- `certificate/audit_global_residual_a.py`: independent global-`a` auditor;
- `certificate/audit_global_residual_b.py`: independent global-`b` and
  propagation auditor;
- `certificate/reproduce_closed_upgrade.sh`: byte-stable closed-chain
  reproducer.

The global-`a` run used 96,295 innovation intervals, between 62 and 94 per
patch, at maximum innovation depth 2. The global-`b` run used 50,947 intervals,
between 37 and 48 per patch, at maximum depth 1. The worst patches were
`p17_m11` for `a` and `p45_m04` for `b`.

Historical `OPEN` artifacts remain valid records of the earlier failed
architectures. They are not the authority for this later optional certificate.
