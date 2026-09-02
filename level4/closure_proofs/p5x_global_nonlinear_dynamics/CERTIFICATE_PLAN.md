# P5X certified-numerics plan

The design principle is inherited, not invented: reuse the architecture that
`closure/04_ARB_CERTIFICATE.md` and
`level4/closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md` already
established and that independent auditors already replayed. P5X changes the
*target functional* and adds an interval-valued drift parameter; it does not
change the method.

## 1. What is certified, and what is not

| certified | not certified |
|---|---|
| enclosures of `R_{D,m}`, `E[Rbar^2 | e]`, `S_{D,m}` (and optionally `R'`, `E[Rbar^4]`) over a finite cover that provably exhausts `e in [0, 12]` | anything at a single sampled `e` |
| the far-field majorant `B_D(e)` of `P5X-T3` | the invariant density `pi` |
| per-cell resolvent bounds | the existing `Gamma` enclosures (imported unchanged) |
| the derived scalars `R_max`, `s_min`, `M_2` | any Monte Carlo quantity |

## 2. Inherited machinery (used verbatim where possible)

1. **Exact rational model constants.** `k = 1/2`, `h = 5` as exact rationals;
   `A` as the exact runtime dyadic `4581762885148045 / 8796093022208` used by
   the SR certificate.
2. **Exact-dyadic candidate.** A tensor Chebyshev collocation solve produces a
   floating candidate for each backward function; coefficients are rounded to
   exact dyadic rationals. The floating solver then leaves the proof path
   entirely (`"candidate_role": "exact dyadic candidate only; not proof evidence"`).
3. **Certified residual.** The candidate is converted to power polynomials, the
   kernel is split at every reset regime (CUSUM: at `z = 1/2 - x^+` and
   `z = x^- - 1/2`; SR: no kinks, but the same panel discipline), `phi` is
   replaced by a truncated Maclaurin polynomial **with a rigorous uniform
   Lagrange remainder**, and each piece is integrated symbolically.
4. **Continuum range bound.** Tensor Bernstein conversion bounds the residual on
   the reachable-set patches — a continuum bound, never a sampled grid
   (`"sampled_grid_used": false`).
5. **Resolvent.** The monotone one-sided Bellman minorant plus pathwise-coupling
   monotonicity gives `‖(I-K_e)^{-1}‖_inf <= C(e)`, now as a function of the
   `e`-interval (obligation `L4`).
6. **Outward-rounded propagation.** Arb real balls at `>= 192` bits; every
   stored quantity serialised as `ball`, `lower_enclosure`, `upper_enclosure`;
   final inequalities evaluated on the conservative endpoint.

## 3. What is new

| new element | why it is needed | risk |
|---|---|---|
| interval-valued drift `e` inside the kernel weight `phi(z + e)` | turns a per-point enclosure into a continuum cover with no separate modulus of continuity (obligation `L5`) | inflates residuals; controlled by adaptive bisection in `e` |
| new absorbing rewards `rho_{1,e}`, `rho_{2,e}` in closed form | the target is a terminal-innovation moment, not `E[Z_tau T_tau]` | low: both are elementary Gaussian tail expressions |
| backward functions `h_j` and sources `S_j` for `m > 1` | replaces the `m-1` extra state dimensions | low: `m-1 <= 4` applications of an operator already certified |
| pair functions for `E[Rbar^2]`, `m >= 2` | second moments with window `m` | medium: `O(m^2) <= 25` further solves |
| a `rho`-cover for the skeleton theorem | `P5X-T8` | high; optional |

Note a structural simplification relative to the existing `Gamma` certificate:
`Gamma` required the **coupled** pair `a = Ka + r_a`, `b = Kb + K_z a + r_b`,
and its wide final interval came from propagating `delta_b + mu * E_a`. The
P5X targets are **single** second-kind equations `g = K g + source`, so the
propagated error is `C * delta` with one factor of `C`, not two. Against the
`e = 0` precedent (`delta_a <= 8.46e-6`, `C = 1315.79`, giving `E_a ~ 0.011`),
the required half-width for `P5X-T4` is `< 0.2`. That margin is the campaign's
central engineering bet, and step 3 of `PROOF_OBLIGATIONS.md` §4 tests it on a
single cell before any scaling.

## 4. The finite certified cover

* Domain `[0, 12]` per `(D, m)`; negative `e` by oddness (`P5-T3`, exact).
* Adaptive bisection in `e`: a cell is accepted when its enclosure satisfies the
  cell's acceptance criterion (for `C1`: half-width `<= w_target`; for the sign
  statements: the enclosure lies strictly on one side of `0`); otherwise it is
  bisected.
* Termination is certified: the accepted cells must tile `[0, 12]` exactly, with
  matching endpoints recorded, and the certificate must assert the tiling.
* A hard cell budget is fixed in advance; exceeding it is a **failure to
  certify**, reported as such, not a licence to widen `w_target`.
* `[12, infinity)` is closed by `P5X-T3` with a certified evaluation of
  `B_D(12)`.

## 5. Reproducibility

Every certificate artifact carries: target string (auditor-enforced, as in the
existing certificates), exact model rationals, precision, python-flint / FLINT
versions, the full accepted cover, per-cell enclosures and acceptance reasons,
resolvent bounds, and a payload digest. An independent auditor script must be
able to re-check every inequality from the stored artifact **without** re-running
the solver, mirroring `audit_global_residual_a.py` / `audit_sr_resolvent.py`.

## 6. Budget

| item | cells / solves | note |
|---|---|---|
| `C1` core map | ~120 `e`-cells × 2 detectors × 4 windows, sharing `h_j` | backward functions are shared across `m` within an `e`-cell |
| `C2` second moment | same cover, `m = 1` cheap, `m >= 2` `O(m^2)` | |
| `C5` resolvent | one per `e`-cell per detector | |
| `C3` derivative | ~60 `e`-cells on `[0,2]` × 8 cells | Level C only |
| `C4` skeleton | `rho`-cover × interval dynamics on `I_rho` | optional |
| total | `~1.4e3` core solves, `~3.5e3` with options | `O(300–800)` CPU-hours, embarrassingly parallel over `e`-cells |

## 7. Explicit prohibition

No floating-point grid, no Monte Carlo estimate and no interpolant (PCHIP or
otherwise) may appear inside any P5X proof path. They may appear only in
`feasibility/` and in the correspondence checks of `EMPIRICAL_PLAN.md`, both of
which are firewalled by gate `G8` and gate `G12`.
