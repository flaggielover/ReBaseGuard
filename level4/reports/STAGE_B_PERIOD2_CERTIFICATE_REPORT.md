# ReBaseGuard Level 4 — Stage B

## Rigorous period-2 certificate for the frozen CUSUM at full reuse

**Decision: `STAGE-B-CLOSED-RIGOROUS-PERIOD2`**

> Stage A statuses are untouched. This report adds Stage B entries; it
> does not restate, revise or supersede any Stage A or Level 1–3 claim.

---

## 1. Theorem

> **Theorem.** For the frozen symmetric two-sided Gaussian CUSUM with
> `k = 1/2`, `h = 5`, reuse window `m = 1` and full reuse `rho = 1`, let
> `F_1(e) = e + E_e[z_tau]` be the deterministic conditional-mean map.
> Then, with
> 
> `I = [1.028724, 1.044724]`,
> 
> 1. `H(e) = F_1(e) + e` has **exactly one** zero `e*` in `I`;
> 2. `0 ∉ I`, so `e* ≠ 0`;
> 3. `{e*, −e*}` is a period-2 orbit of `F_1`;
> 4. its multiplier satisfies `lambda_2 = [F_1'(e*)]² ∈
>    [0.108148, 0.832532] ⊂ (−1, 1)`,
> 
> so the orbit is **locally attracting**.

Part 3 follows from parts 1–2 together with the *proved* odd symmetry
`F_1(−e) = −F_1(e)` (Lemma L3): `F_1(e*) = −e*` gives
`F_1(−e*) = e*`, hence `F_1(F_1(e*)) = e*`.

**What this theorem is not about.** `F_1` is the deterministic
conditional-mean skeleton. The actual reference recursion is
`E_{j+1} = F_1(E_j) + noise`. Nothing here concerns that stochastic
recursion, its invariant law, or bimodality.

---

## 2. Model correspondence

| Frozen Level 1–3 item | Stage B usage |
|---|---|
| `k = 1/2`, `h = 5` exact | `domain.assert_frozen_constants` is called by the driver and raises on any other pair |
| two-sided CUSUM, shared innovation `z_t` | `S±_t = max(0, S±_{t−1} ± z_t − k)` |
| inclusive `≥ h` alarm, tested post-update | continuation set is the OPEN interval `(−v, u)`, `u = h+k−p`, `v = h+k−m` |
| `tau` starts at `t = 1` | the first step can alarm; no dwell |
| terminal observation included | the reward is `z_tau`, the alarm-causing innovation |
| `m = 1` reuse block | `e_{j+1} = e + z_tau`, so `F_1(e) = e + E_e[z_tau]` |
| `rho = 1` | full reuse; no fresh term |
| sign convention | `z_t = X_t − R_j ~ N(−e, 1)` with `e = R_j − mu_j` |
| reachable live region | axes plus the open triangle `p+m < h−2k`, the frozen certificate's `reachable_domain` |

`tests/test_enclosure_soundness.py` checks the operator against the
Stage A conditional simulator and against the Claude Science Bellman
solver at four separate reference errors.

---

## 3. Operator formulation

```text
(T G)(s) = int_R psi(s,z) phi(z+e) dz
psi(s,z) = z              if z <= -v(s) or z >= u(s)   [alarm]
         = G(q(s,z))      otherwise                    [continue]
q(s,z)   = ((p+z-k)^+, (m-z-k)^+)
G = T G ,  equivalently  G = K_e G + r_e ,  F_1(e) = e + G(0,0)
(I - K_e) G' = (d_e K_e) G + d_e r_e
```

`T` is monotone in `G`. `G` is the unique bounded solution because
`I − K_e` is injective (Lemma L2).

### Why this encloses the true map and not a discretization

The obvious shortcut — take the Claude Science Bellman solver and
evaluate it in Arb — does **not** produce a rigorous result. That solver
is midpoint collocation: `grid.cell(p + z_c − k)` projects the continuum
destination onto a cell using the sub-interval midpoint. Interval
arithmetic on it would certify the discretization, not the map. It is
used here only to place grid cells (which cannot affect validity) and as
an independent consistency check.

What is done instead: the `z` axis is cut at breakpoints and each piece
is integrated against the Gaussian **in closed form**; the outer tails
are pure-alarm regions integrated to `±∞` analytically; a source cell is
a box, so `u`, `v` and every breakpoint are intervals; and a destination
resolves to a **superset** of cells over which min/max is taken. A coarse
cell therefore widens the bracket and can never invalidate it.

---

## 4. Error budget

| Source | Present? | Rigorous bound | Magnitude |
|---|---|---|---|
| interval rounding (Arb ball radii) | yes | outward-rounded to float at 96 bits; insensitivity verified over 64-256 bits | < 1e-9 on the reported endpoints |
| quadrature error | NO | not applicable | exactly 0 — every z-segment is integrated against the Gaussian in closed form (Phi and phi differences); the pipeline contains no quadrature rule |
| domain truncation | NO | not applicable | exactly 0 — the continuation set is contained in (-(h+k), h+k), so |z| > z_cut is pure-alarm and is integrated to +/- infinity analytically |
| state-space escape | checked | hard failure | build_transitions raises if any continuation segment leaves the live region, so Lemma L1 is verified on the actual grid rather than assumed |
| cell projection / interpolation | yes | carried by the monotone bracket: destinations resolve to a SUPERSET of cells and min/max is taken | the whole reported bracket width; max cell width 0.023029 on G |
| iterative solve error | NO | not applicable | exactly 0 — T is monotone, so every iterate is already a valid bracket and the iteration may stop anywhere |
| float rounding inside the iteration | yes | ROUNDING_SLACK = 1e-9 applied outward per iteration on both sides | one iteration sums <= 1e4 products of magnitude <= 1e2, so the accumulated error is below 1e4 * 2^-53 * 1e2 ~ 1e-10 |
| e-dependence between mesh points | yes | |G''| <= 153.7383 from the twice-differentiated operator equation with analytic operator norms; times half-spacing 0.000500 | 0.076869 added outward to H' and F_1' over I |
| a priori |G| and |G'| used for the warm start | yes | |G| <= 23.4313 by Wald; |G'| <= 381.47 by the resolvent bound | affects iteration count only; a warm start is a starting bracket, and the test suite checks it reproduces the cold-start answer |
| grid placement from a non-rigorous float profile | yes, but cannot affect validity | the monotone bracket is valid on ANY partition | changes width only; three different grid-placement rules are compared in the adversarial checks |

Three of these are **exactly zero** rather than merely small: quadrature,
domain truncation, and iterative solve error. That is a structural
property of the scheme, not a numerical accident.

---

## 5. Root certificate

Mesh: 25 thin reference errors from
`1.024724` to `1.048724`, spacing
`0.001000`. Every operator solve is at a **thin** `e`;
the `e`-dependence is carried analytically (§6).

| `e` | `H(e)` enclosure | sign | `H'(e)` enclosure | `F_1'(e)` enclosure |
|---|---|---|---|---|
| 1.024724 | [-0.030761, -0.007732] | **−** | [+1.4102, +1.8376] | [+0.4102, +0.8376] |
| 1.025724 | [-0.029160, -0.006140] | **−** | [+1.4101, +1.8369] | [+0.4101, +0.8369] |
| 1.026724 | [-0.027560, -0.004548] | **−** | [+1.4099, +1.8363] | [+0.4099, +0.8363] |
| 1.027724 | [-0.025961, -0.002957] | **−** | [+1.4098, +1.8356] | [+0.4098, +0.8356] |
| 1.028724 | [-0.024362, -0.001367] | **−** | [+1.4090, +1.8356] | [+0.4090, +0.8356] |
| 1.029724 | [-0.022763, +0.000224] | — | [+1.4089, +1.8349] | [+0.4089, +0.8349] |
| 1.030724 | [-0.021165, +0.001814] | — | [+1.4087, +1.8342] | [+0.4087, +0.8342] |
| 1.031724 | [-0.019567, +0.003403] | — | [+1.4086, +1.8336] | [+0.4086, +0.8336] |
| 1.032724 | [-0.017969, +0.004992] | — | [+1.4081, +1.8333] | [+0.4081, +0.8333] |
| 1.033724 | [-0.016372, +0.006581] | — | [+1.4079, +1.8326] | [+0.4079, +0.8326] |
| 1.034724 | [-0.014775, +0.008170] | — | [+1.4078, +1.8319] | [+0.4078, +0.8319] |
| 1.035724 | [-0.013179, +0.009758] | — | [+1.4076, +1.8313] | [+0.4076, +0.8313] |
| 1.036724 | [-0.011583, +0.011345] | — | [+1.4075, +1.8306] | [+0.4075, +0.8306] |
| 1.037724 | [-0.009987, +0.012933] | — | [+1.4070, +1.8303] | [+0.4070, +0.8303] |
| 1.038724 | [-0.008392, +0.014520] | — | [+1.4068, +1.8297] | [+0.4068, +0.8297] |
| 1.039724 | [-0.006797, +0.016106] | — | [+1.4067, +1.8290] | [+0.4067, +0.8290] |
| 1.040724 | [-0.005203, +0.017692] | — | [+1.4065, +1.8284] | [+0.4065, +0.8284] |
| 1.041724 | [-0.003609, +0.019278] | — | [+1.4062, +1.8278] | [+0.4062, +0.8278] |
| 1.042724 | [-0.002015, +0.020863] | — | [+1.4060, +1.8272] | [+0.4060, +0.8272] |
| 1.043724 | [-0.000422, +0.022448] | — | [+1.4059, +1.8265] | [+0.4059, +0.8265] |
| 1.044724 | [+0.001171, +0.024033] | **+** | [+1.4057, +1.8259] | [+0.4057, +0.8259] |
| 1.045724 | [+0.002763, +0.025617] | **+** | [+1.4056, +1.8252] | [+0.4056, +0.8252] |
| 1.046724 | [+0.004356, +0.027201] | **+** | [+1.4052, +1.8248] | [+0.4052, +0.8248] |
| 1.047724 | [+0.005947, +0.028785] | **+** | [+1.4050, +1.8241] | [+0.4050, +0.8241] |
| 1.048724 | [+0.007539, +0.030368] | **+** | [+1.4049, +1.8235] | [+0.4049, +0.8235] |

**Existence.** `H` is continuous (Lemma L4). The table certifies
`H < 0` at `e = 1.028724` and `H > 0` at
`e = 1.044724`, so the intermediate value theorem
gives a zero in between. Certified: **True**.

**Uniqueness.** `H'` is certified at every mesh point, and `|H''| = |G''|`
is bounded by `153.7383` (§6), so between mesh
points `H'` can fall by at most
`0.076869`. Hence
`H'(e) >= 1.328858 > 0` on all of `I`, so `H`
is strictly increasing there and the zero is unique. Certified: **True**.

**`0 ∉ I`.** `I = [1.028724, 1.044724]` lies strictly to the right of 0. Certified: **True**.

> Interval Newton and Krawczyk were both attempted first and are
> reported as failures in §9; the mesh route above is what survived.

---

## 6. Derivative certificate

`G'` is obtained from the **differentiated operator equation**, never
from a finite difference:

```text
(I - K_e) G' = (d_e K_e) G + d_e r_e
```

with the `G` bracket from §5 as data. `K_e` is positive, so the same
monotone iteration applies and every iterate is again a valid bracket.

* `||G||_inf <= 2.10273` (certified, over all cells)
* `||G'||_inf <= 2.48296` at the mesh points, and `<= 2.56007` over the whole interval
  (self-consistent bound, contraction factor 0.01482 < 1)
* `||G''||_inf <= 153.7383` from the twice-
  differentiated equation with the analytic operator norms
  `||d_e K|| <= 2 phi(0) = 0.797884561`,
  `||d_e^2 K|| <= 4 phi(1) = 0.967882898`,
  `||d_e^2 r|| <= 8 phi(1) - 2 phi(0) + |e| * 4 phi(1)`

Combining: `F_1'(I) ⊆ [0.328858, 0.912432]`.

---

## 7. Multiplier certificate

By the proved odd symmetry, `F_1'` is even, so the period-2 multiplier is

```text
lambda_2 = F_1'(e*) F_1'(-e*) = [F_1'(e*)]^2 .
```

From `F_1'(I) ⊆ [0.328858, 0.912432]`:

```text
lambda_2 in [0.108148, 0.832532]   ->   |lambda_2| <= 0.832532 < 1
```

Certified: **True**. By the standard
hyperbolic fixed-point theorem applied to `F_1 ∘ F_1` (Lemma L8), the
orbit `{e*, −e*}` is locally asymptotically stable.

> The multiplier is *not* read off a floating-point derivative at a point.
> It is the square of a certified interval covering `F_1'` on the whole
> interval that provably contains `e*`.

---

## 8. Independent checks

### Route B — the reflected run

Route B is not Route A with different constants. It certifies `G` at the
**reflected** reference error `−e*`, where the drift drives the *plus*
arm instead of the minus arm, exercising the mirror half of the state
space and a different part of the grid. Lemma L3 then requires
`G(−e) = −G(e)`, so the two certified brackets must intersect. A defect
that is not symmetric under the arm swap shows up here.

* **reflection_symmetry_route_B** — PASS
  * `route_A_G` = [-2.09659342, -2.05128065]
  * `route_B_minus_G_at_minus_e` = [-2.09659872, -2.05129157]
* **derivative_evenness_route_B** — PASS
  * `route_A_F1p` = [0.22021980, 1.07133610]
  * `route_B_F1p_at_minus_e` = [0.22017062, 1.07136341]
* **claude_science_bellman** — PASS
  * `certified_F1p` = [0.22021980, 1.07133610]
  * `science_F1p` = 0.59154571
  * `science_e_star` = 1.03672429
  * `science_multiplier` = 0.34992632
  * evidence class: NON-RIGOROUS (midpoint-collocation Bellman solver)
* **claude_science_G_at_e_star** — PASS
  * `certified_G` = [-2.09659342, -2.05128065]
  * `science_G` = -2.07344858
  * evidence class: NON-RIGOROUS
* **stage_a_monte_carlo** — PASS
  * `certified_F1p` = [0.22021980, 1.07133610]
  * Stage A Monte Carlo: `e* = 1.03695 ± 0.00037`, `F_1'(e*) = 0.5954`, `lambda_2 = 0.3545`
  * evidence class: NON-RIGOROUS (Monte Carlo)

### Consistency with prior non-rigorous work

These can contradict the certificate but cannot support it, and are
labelled accordingly:

| Source | Evidence class | `e*` | `F_1'(e*)` | `lambda_2` |
|---|---|---|---|---|
| Stage A Gate 4.2 (Monte Carlo) | NON-RIGOROUS | 1.03695 ± 0.00037 | 0.5954 | 0.3545 |
| Claude Science Bellman solver | NON-RIGOROUS (midpoint collocation) | 1.03672429 | 0.59154571 | 0.34992632 |
| **Stage B (this work)** | **RIGOROUS** | in [1.028724, 1.044724] | in [0.32886, 0.91243] | in [0.10815, 0.83253] |

The Claude Science branch refinement (`branch_refinement.csv`) gives
`e* = 1.03678236 (N=50)`, `1.03672429 (N=100)`, `1.03670979 (N=200)` —
all inside the certified interval.

---

## 9. Failure attempts

### Approaches that were tried and did not work

Recorded because a certificate is only as informative as the attempts it
survived.

1. **Wrapping the Claude Science Bellman solver in Arb.** Rejected on
   inspection, not experiment: the solver is midpoint collocation, so
   interval arithmetic on it certifies the discretization rather than the
   map. Using it would have been the single easiest way to produce a
   confident and wrong result.
2. **Interval Newton / Krawczyk with an interval-`e` operator.** Built,
   run, and it diverged: enclosing the segment masses over an `e`-interval
   loses the constraint that all segments share one `e`, and the measured
   total continuation mass reached **4.47 > 1**, making the upper operator
   expansive. The iteration ran to ±1e15.
3. **First-order Taylor-in-`e` masses.** Fixed the magnitude (measured
   total mass 1.0099 at `w = 0.012`) and the iteration converged, but
   the residual spurious mass `w * TV(phi)` is irreducible per segment.
   Measured `G` widths were 0.2268 at `w = 0.006` and 0.4375 at
   `w = 0.012`, against 0.0229 at `w = 0`. Propagating those through
   `||d_e K|| * resolvent` puts `H'(I)` astride 0 at every `w` that
   interval Newton could use, so the route was abandoned for the
   thin-`e` mesh, where total mass is 0.999996. (That last step is a
   projection from measured widths, not a completed Newton run.)
4. **A wrong analytic constant.** `∫|w||phi''(w)|dw` was initially coded
   as 1.1378772; the exact value is `8 phi(1) − 2 phi(0) = 1.1378812`.
   The error was in the **unsound** direction — too small a `|G''|` bound
   — and would have produced an invalid uniqueness/multiplier claim. It is
   now a closed form, checked against quadrature to 3e−11 and pinned by a
   test.
5. **A sup-norm taken at the mesh points only.** `||G||` and `||G'||`
   feed the `|G''|` bound, which has to hold for every `e` in `I`, not
   just at the 25 solved points. The first version used the mesh
   maximum directly. The correction is numerically tiny -- it moves the
   certificate below the sixth decimal -- but it was a real gap in the
   argument, and is now closed by inflating with
   `half_spacing * ||G'||` and re-solving the self-consistent bound. A
   test pins the inflation.

### Adversarial checks

| Check | Question | Result | Note |
|---|---|---|---|
| `precision` | does Arb working precision move the bracket? | PASS | max shift 3.55e-15 over 64..256 bits |
| `grid_refinement` | does the bracket shrink monotonically and keep containing the reference? | PASS | widths [0.11238, 0.05686, 0.02876], all contain reference: True |
| `z_cut` | does the tail cut point matter? (it must not: tails are exact) | PASS | max shift 0.00e+00 over z_cut 8..20 |
| `grid_placement` | does the (non-rigorous) grid-placement heuristic change validity? | PASS | all three grids contain the reference; widths [0.05686, 0.05366, 0.06227] |
| `profile_resolution` | does the float profile's resolution leak into the certificate? | PASS | all contain the reference; widths [0.0567, 0.05686, 0.05663] |
| `backend` | does the certified backend enclose the uncertified one? | PASS | Arb bracket contains the float bracket for both G and F1' |
| `deliberate_perturbation` | is a value deliberately pushed outside the bracket rejected? | PASS | a value 3 widths away is correctly outside the bracket |
| `mass_conservation` | is the upper operator sub-stochastic (necessary for contraction)? | PASS | max total continuation mass 0.99999596 |
| `killing_bound` | does the uniform resolvent bound dominate the true sup ARL? | PASS | bound 18.5782 > true sup ARL 9.7977 |

**9/9** adversarial checks passed.

---

## 10. Claim ledger

Stage A statuses are **not** modified. Stage B adds its own entries in
`level4/reports/STAGE_B_LEDGER.md`. The new status `RIGOROUS-CERTIFIED`
means: the analytic lemmas are proved, and every approximation between
the true mathematical object and the computed one is explicitly bounded.

| Upgraded | From (Stage A) | To (Stage B) |
|---|---|---|
| nonzero root of `H_1` at `rho = 1` | `CANDIDATE` (STRONG-CANDIDATE, Monte Carlo) | `RIGOROUS-CERTIFIED` |
| period-2 multiplier `|lambda_2| < 1` | `CANDIDATE` (Monte Carlo point estimate 0.3545) | `RIGOROUS-CERTIFIED` |
| odd symmetry of `F_1` | proved at Level 2 (human mathematics) | `RIGOROUS-CERTIFIED` (restated and used) |

---

## 11. Remaining limitations

* The theorem is about the **deterministic** map `F_1`. It says nothing
  about the noisy recursion `E_{j+1} = F_1(E_j) + noise`, its invariant
  law, or bimodality. Those remain `OPEN`.
* Only `rho = 1` is certified. The `rho` branch and the approach to
  `rho_c` are untouched.
* Only `m = 1`, `k = 1/2`, `h = 5`, Gaussian innovations.
* Uniqueness is asserted **only inside `I`**. No global uniqueness of the
  period-2 orbit is asserted.
* `e*` is localized to an interval of width
  0.016000, which is far wider
  than the non-rigorous estimates. That is the honest cost of the
  piecewise-constant bracket; tightening it would need a Taylor-model or
  piecewise-polynomial representation.
* The certificate rests on python-flint / Arb being a correct
  implementation of ball arithmetic, and on the correctness of the code
  in `level4/stage_b/src`. It is not machine-checked in Lean.

---

## 12. Proposed extension (NOT executed)

The Stage B brief permits proposing a `rho < 1` extension once the
primary theorem is closed. It is proposed here and deliberately **not**
run: the requested deliverable was `rho = 1`, and a closed result is
worth more than a broader one that dilutes it.

**Why it is cheap.** Level 2C proves `F_rho = rho * F_1` exactly, so
`H_rho(e) = rho (e + G(e)) + e`. The certified `G` and `G'` enclosures
are `rho`-independent; only the mesh location changes. Each extra `rho`
costs one 25-point mesh (~36 min) around its own root.

| `rho` | Stage A / Science `e*` | Science multiplier | note |
|---|---|---|---|
| 0.5 | 0.648469 | 0.1414 | mesh over roughly [0.633, 0.665] |
| 0.25 | — | — | Science branch stops at 0.3; needs its own localization |
| 0.1 | 0.142298 | 0.1458 | close to `rho_c`; `H'` shrinks, so the mesh must be finer |

**Where it would get hard.** As `rho` falls toward
`rho_c = 1/|F_1'(0)| ~ 0.067`, the nonzero root merges into 0 and
`H_rho'` near the root tends to 0, so the uniqueness step (which needs
`min H' > |G''| * half_spacing`) degrades. Below some `rho` the present
piecewise-constant bracket will not close and a Taylor-model or
piecewise-polynomial representation would be needed. That boundary should
be found empirically rather than assumed.

```bash
# the command, once authorized
level4/.venv/bin/python level4/stage_b/src/run_stage_b.py \
    --backend arb --n-axis 400 --n-tri 60 \
    --center 0.648469 --radius 0.012 --spacing 0.001 --tag rho0p5
```

> The driver currently forms `H(e) = 2e + G(e)`, which is the `rho = 1`
> case. Extending it means using `H_rho(e) = rho(e + G(e)) + e`; that is a
> one-line change, but it is a change, so it is listed as work rather than
> as something already in place.

---

## 13. Decision

### `STAGE-B-CLOSED-RIGOROUS-PERIOD2`

| # | Requirement | Result |
|---|---|---|
| R1 | nonzero root existence rigorously certified (certified sign change + continuity, Lemma L4) | PASS |
| R2 | root uniqueness in the stated interval rigorously certified (H' > 0 on all of I) | PASS |
| R3 | the certified interval excludes 0 | PASS |
| R4 | multiplier abs(lambda_2) < 1 rigorously certified | PASS |
| R5 | every approximation between the true operator and the computed one is explicitly bounded | PASS |
| R6 | the certified backend is interval arithmetic, not floating point | PASS |

### Reproduction

```bash
bash level4/stage_b/reproduce.sh
```

| Field | Value |
|---|---|
| backend | python-flint/Arb at 96 bits |
| partition | 2631 cells, 4328840 segments |
| `n_axis` / `n_tri` | 400 / 60 |
| `z_cut` | 12.0 |
| mesh | 25 points, spacing 0.001000 |
| resolvent bound | 18.578214 |
| total runtime | 36.2 min |

