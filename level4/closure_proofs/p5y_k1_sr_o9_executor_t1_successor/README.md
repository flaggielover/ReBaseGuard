# P5Y K1 SR O9 executor — T1 successor: Layer-1 candidate construction

**STATUS: `T1_CANDIDATE_CONSTRUCTION_ONLY`.**

This namespace builds the frozen SR O9 minimal candidate basis for any frozen SR
cell. It certifies **nothing**:

* no patch or panel residual is certified (that is T2);
* no `B_cover` utilisation is computed or claimed;
* no top-level obligation is discharged, and no obligation status exists here;
* nothing here is production-ready, result-bearing or admissible as genuine evidence.

A candidate is a proposal. Only the certificate built on it later bounds the truth.

## What is built

The 46-member O9 minimal basis, derived from the frozen SR DAG and asserted equal to
the frozen O9 census (46 candidates / 102 contracts, moment shifts {0:43, 1:35, 2:20, 3:4}):

| class | nodes | method |
|---|---|---|
| EXACT | `const:1` | exact (the argument of `h_1^(k) = -K^(k) 1`) |
| CLOSED_FORM_INTERPOLANT | `h:1:k0..2`, `S:0:k0..2` | nodal closed form (SR_DERIVATION s1, s4) |
| FORWARD_OPERATOR | `h:2..4`, `S:1..2`, `W:(0,1),(0,2),(1,1)` at orders 0..2 | Leibniz chains with `K`, `K'`, `K''`, `K_z`, `K_z'`, `K_z''` |
| RESOLVENT_SOLVE | `F:r:k0` | `(I-K)F_r = S_r + e h_1` |
| DERIVATIVE_SOLVE | `F:r:k1` | `(I-K)D_r = K'F_r + S_r' + h_1 + e h_1'` |
| CURVATURE_SOLVE | `F:r:k2` | `(I-K)H_r = K''F_r + 2K'D_r + S_r'' + 2h_1' + e h_1''` |

`S_3`, `S_4` and the leaf `W` are nodal intermediates only: they are never kernel
arguments, so they are not basis candidates.

## Method (frozen, not re-derived)

Identical to the Task1R-adjudicated `task1_f0.build_candidate`: 17x17
Chebyshev-Lobatto collocation on `[0,b_SR]^2`, 220-point Gauss-Legendre Nystrom
quadrature, float linear solve, DCT, exact-dyadic rounding at `2^-50`. The moment
matrices `M_s` (`s = 0..3`) add the frozen `z^s` weights; `M_0` is byte-identical to
Task1R's `W`. One assembled `(I - M_0)` system per cell serves all 15 solves; every
solve factors afresh with `numpy.linalg.solve` (no LU reuse, no scipy).

**Float construction (non-authoritative):** Nystrom matrices, closed-form nodal
values, forward chains, solves, DCT. **Authoritative:** exact integer mantissas
(`coefficient = m * 2^-50`), exact affine cell geometry evaluated in Arb inside an
explicit 256-bit scope that re-verifies `ctx.prec`, candidate identities and hashes.

## Frozen-reference reproduction

* Bit-exact against the frozen `task1_f0.build_candidate` (run under the same runtime).
* Task1R's recorded 2026-09-04 construction diagnostics were produced on the
  pre-resize host; the frozen aux4 `blas_kernel_sensitivity.json` shows OpenBLAS kernel
  choice alone moves 62/240 dyadic candidates (including `F:0:0`), which is why the
  runtime contract `d49f0437...` is bound. Under that authorized contract (verified
  live) the T1 `F_0`, contracted over the 44 frozen contexts of the committed
  cap-authorized packet, reproduces the committed byte-exact scientific hash
  `c72f65b3...`; the dense control reproduces `c0fc8609...`.

## Cell 315

Its right endpoint is the exact splice `c_SR = log(A) + 1/2`, encoded affinely as
`[0, 1]`. Geometry is evaluated from the affine encoding at 256 bits; the defective
predecessor reading `F(pair[0])` (right = 0) is regression-tested and never used.
The frozen far-field treatment is untouched.

## Not changed

No degree, precision, patch, panel, threshold, obligation ID, predecessor file,
production launcher or lifecycle file was modified.
