# ReBaseGuard Continuum Certificate Design

**Status:** Approved architecture, implementation pending  
**Model:** `k = 0.5`, `h = 5`, two-sided Gaussian CUSUM  
**Target:** certify `Gamma = E[Z_tau T_tau] > 2`

## 1. Integrity rule and success condition

The finite approximation is never proof evidence. It supplies candidate functions only. The proof is a continuum statement obtained from:

1. outward-rounded Arb enclosures of the residuals of the exact dynamic equations over every reachable state;
2. an independently proved, Arb-certified uniform block contraction for the exact killed kernel;
3. an explicit resolvent bound that propagates the continuum residuals into an enclosure of the exact solution; and
4. an independent replay auditor that rejects the certificate unless its recomputed lower endpoint satisfies `Gamma_L > 2`.

Ordinary IEEE arithmetic may construct candidates and diagnostics. It cannot contribute a proof-critical endpoint.

## 2. Exact state reduction

Write the live CUSUM state as `s = (p,m) = (S_t^+, S_t^-)` and the current cumulative sum as `x = T_t`. Let `N` be the remaining time to alarm, let `W = Z_{t+N}` be the terminal future increment, and let `Y = sum_{j=1}^N Z_{t+j}` be the future cumulative sum. Conditional on `s`, the future is independent of `x`, so

```text
E[Z_tau T_tau | S_t=s, T_t=x]
    = E_s[W(x+Y)]
    = a(s) x + b(s),
```

where

```text
a(s) = E_s[W],
b(s) = E_s[W Y].
```

Consequently the target is exactly

```text
Gamma = b(0,0).
```

This proves that the cumulative sum need not be discretized. Two CUSUM coordinates remain necessary because both alarm thresholds and the next reset pattern depend on `(p,m)`.

## 3. Reachable continuum state space

For a continuing transition driven by `z`,

```text
p' = max(0, p + z - k),
m' = max(0, m - z - k).
```

Starting at `(0,0)`, the reachable pre-alarm set is contained in the simplicial complex

```text
D = { (p,0): 0 <= p < h }
  union { (0,m): 0 <= m < h }
  union { (p,m): p>0, m>0, p+m < h-2k }.
```

Proof: the first step lies on an axis. An interior point can first be entered only from an axis. If it is entered from `(p,0)`, both new coordinates are positive and their sum is `p-2k < h-2k`; the argument from the other axis is symmetric. If an interior state continues to another interior state, the new sum is `p+m-2k`, so the bound is preserved strictly. If either coordinate resets, the result is on an axis. The certifier works on the closure of this set, so null-probability boundary cases are enclosed too.

No computation over the unreachable remainder of `[0,h)^2` enters the proof.

## 4. Exact dynamic equations

Let `phi` and `Phi` be the standard normal density and CDF. Define

```text
ell(s) = m - h - k,
u(s)   = h + k - p,
q(s,z) = (max(0,p+z-k), max(0,m-z-k)).
```

The process continues exactly when `ell(s) < z < u(s)`. Define

```text
(K f)(s)   = integral_[ell(s),u(s)] f(q(s,z)) phi(z) dz,
(K_z f)(s) = integral_[ell(s),u(s)] z f(q(s,z)) phi(z) dz.
```

The absorbing rewards are full-tail Gaussian moments:

```text
r_a(s) = integral_[u,infinity] z phi(z) dz
       + integral_[-infinity,ell] z phi(z) dz
       = phi(u) - phi(ell),

r_b(s) = integral_[u,infinity] z^2 phi(z) dz
       + integral_[-infinity,ell] z^2 phi(z) dz
       = u phi(u) + (1-Phi(u)) + Phi(ell) - ell phi(ell).
```

First-step conditioning gives the coupled Fredholm equations

```text
a = K a + r_a,
b = K b + K_z a + r_b.
```

All equations will be checked against a separate direct recursion implementation on test cases. The implementation must also verify the reflection identities before enabling symmetry reduction:

```text
a(p,m) = -a(m,p),
b(p,m) =  b(m,p).
```

These follow from mapping every future increment sequence `z_j` to `-z_j`, which swaps the arms, negates the terminal increment and future sum individually, and preserves their product.

## 5. Existence, uniqueness, and rigorous block contraction

`K` is a positive sub-Markov operator on bounded functions on the closure of `D`. A uniform contraction is certified analytically in blocks, without sampling states.

For any integer `n >= 1`, let `G_n = sum_{j=1}^n Z_j`. From the recursion,

```text
S_n^+ >= p + G_n - n k,
S_n^- >= m - G_n - n k.
```

Since `p,m >= 0`, either event

```text
G_n >= h + n k
```

or

```text
G_n <= -(h + n k)
```

forces absorption by time `n` from every state in `D`. Because `G_n ~ N(0,n)`, the two events are disjoint and have total probability

```text
q_n = 2 * (1 - Phi((h+n*k)/sqrt(n))) > 0.
```

Therefore, over the entire reachable continuum,

```text
K^n 1(s) = P_s(tau > n) <= 1-q_n = beta_n < 1,
||K^n||_infinity <= beta_n.
```

The certificate evaluates `q_n` and `beta_n` with Arb balls and proves the strict inequalities using ball endpoints. Candidate integers `n` may be explored in ordinary arithmetic, but the chosen value and its bound are independently replayed by the auditor.

Writing any exponent as `j n + r`, `0 <= r < n`, positivity and sub-Markovity give `||K^r|| <= 1`, hence

```text
sum_{t=0}^infinity ||K^t||
    <= sum_{j=0}^infinity sum_{r=0}^{n-1} beta_n^j
    = n/(1-beta_n)
    =: C_n.
```

Thus `I-K` is invertible on bounded functions, the two equations have unique bounded solutions, and

```text
||(I-K)^(-1)||_infinity <= C_n.
```

This also supplies finiteness without relying on an empirical ARL.

## 6. Candidate approximation

An ordinary deterministic solver constructs continuous piecewise-linear candidates `a_hat` and `b_hat` on a dyadic triangulation of the interior triangle plus compatible one-dimensional axis meshes. Shared nodal values enforce continuity. Candidate coefficients are serialized as exact dyadic rationals before certification.

The ordinary solver may use NumPy/SciPy and high-order quadrature. Its outputs are explicitly labelled `NON-RIGOROUS DIAGNOSTIC ONLY`.

## 7. Continuum residual certification

Define exact residuals

```text
rho_a = a_hat - K a_hat - r_a,
rho_b = b_hat - K b_hat - K_z a_hat - r_b.
```

The certifier proves, over every point of the continuum complex `D`,

```text
||rho_a||_infinity <= delta_a,
||rho_b||_infinity <= delta_b.
```

For each source simplex or axis segment, the `z` interval is subdivided at reset thresholds and candidate-mesh crossings. On each resulting piece:

1. the image of `q(s,z)` is enclosed with Arb;
2. every candidate simplex intersecting that image is enumerated conservatively;
3. the exact range of the piecewise-linear candidate is enclosed from its dyadic vertex data;
4. sign-aware interval products enclose `f(q(s,z)) phi(z)` or `z f(q(s,z)) phi(z)`; and
5. Gaussian mass and first-moment factors are evaluated using Arb `exp` and `erf` balls.

Ambiguous reset or mesh-crossing slivers are never discarded; they are enclosed and subdivided adaptively. Source and integration subdivisions continue until the global residual targets are proved or a configured resource ceiling causes a non-certified exit.

There is no Gaussian truncation error. Continuation is intrinsically restricted to `[ell,u]`, and absorbing infinite-tail moments use the exact formulas in Section 4.

## 8. Residual-to-solution enclosure

Let `e_a = a-a_hat` and `e_b = b-b_hat`. The exact and approximate equations imply

```text
(I-K)e_a = -rho_a,
(I-K)e_b = K_z e_a - rho_b.
```

Furthermore

```text
||K_z||_infinity
    <= integral_R |z| phi(z) dz
    = sqrt(2/pi)
    =: mu.
```

Arb certifies `mu`. With `C = C_n`,

```text
||e_a||_infinity <= C delta_a =: E_a,
||e_b||_infinity <= C (delta_b + mu E_a) =: E_b.
```

If Arb evaluation gives `b_hat(0,0) in B_0`, then the exact target is enclosed by

```text
Gamma in B_0 + [-E_b,E_b].
```

The proof passes only when the outward-rounded lower endpoint is strictly greater than `2`.

## 9. Independent Bellman fallback and cross-check

A separately implemented cellwise interval Bellman solver uses lower/upper range functions and interval transition/reward enclosures. It does not consume the residual candidate coefficients or residual-certifier output. It must maintain explicit probability-mass accounting and signed interval rewards.

Its purposes are:

1. a logically distinct cross-check against the residual enclosure;
2. a fallback certificate path if residual validation wraps too broadly; and
3. regression tests for kernel mass, refinement behavior, and symmetry.

If used as the final proof, it must independently enclose the continuum fixed point, not merely solve a finite transition matrix.

## 10. Diagnostics and tests

Before certification, a seeded vectorized simulation will reproduce the approximate target, ARL scale, arm symmetry, and `E[T_tau^2] approximately E[tau]`. At least two independent seeds and a separate ordinary dynamic-programming approximation provide non-proof cross-checks.

Automated tests cover:

- pathwise update and alarm-arm recording;
- reflection symmetry and zero-mean diagnostics;
- the affine state decomposition;
- reachable-domain invariance;
- analytic absorbing moments against ordinary quadrature;
- kernel mass balance;
- Arb interval containment and precision refinement;
- continuum residual coverage bookkeeping;
- the analytic block-contraction implication;
- residual error propagation;
- Bellman/residual cross-check agreement; and
- certificate tamper rejection.

## 11. Certificate and auditor

The JSON certificate stores at minimum:

- model parameters as exact rationals;
- Python, `python-flint`, FLINT, and Arb versions;
- Arb precision and rounding/ball semantics;
- reachable-domain definition and mesh hashes;
- exact dyadic candidate nodal data or a content-addressed companion artifact;
- the chosen block length `n`;
- Arb enclosures for `q_n`, `beta_n`, and `C_n`;
- all source/integration subdivisions needed to replay residual coverage;
- `delta_a`, `delta_b`, `mu`, `E_a`, and `E_b` as outward intervals;
- `b_hat(0,0)` and `[Gamma_L,Gamma_U]`;
- all mass-balance and coverage checks;
- proof status; and
- hashes of every proof-critical artifact.

The audit command reconstructs Arb values from exact stored inputs, replays domain coverage, block contraction, residual bounds, error propagation, hashes, and the final comparison. It exits nonzero for any missing coverage, inconsistent endpoint, hash mismatch, or `Gamma_L <= 2`.

## 12. Reproducibility and trusted computing base

The repository will pin the Python environment and record the resolved environment. The intended trusted computing base is:

1. CPython and its integer/rational serialization;
2. `python-flint` bindings;
3. FLINT/Arb ball arithmetic, including `exp`, square root, and `erf`;
4. the small certificate-auditor code path; and
5. the host's correct execution of the pinned binaries.

NumPy, SciPy, simulation code, and the ordinary candidate solver are explicitly outside the proof trusted base.

The primary interface is:

```text
make proof
python -m rebaseguard_certify.audit proofs/certificate.json
```

`make proof` and the auditor exit nonzero unless the audited continuum enclosure proves `Gamma_L > 2`.

## 13. Refinement and stopping rule

Start with a coarse diagnostic mesh. Refine source cells, integration intervals, candidate mesh, or Arb precision only in response to the largest certified residual contributors. Stop immediately after an independently audited enclosure has `Gamma_L > 2`. No effort is spent recovering unnecessary decimal digits.

If the residual route cannot close because of wrapping or resource limits, switch automatically to the independent interval Bellman fallback. If neither closes, report `CERTIFICATION CONDITIONAL` and identify the exact unresolved bound; never relabel numerical convergence as proof.
