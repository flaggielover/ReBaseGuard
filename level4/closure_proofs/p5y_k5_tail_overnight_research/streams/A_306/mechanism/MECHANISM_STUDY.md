# Stream A mechanism study — candidate-family slack at non-target drifts

**Label: FLOAT, NON-CERTIFIED, NON-TARGET.** Drifts e ∈ {1/2, 1, 3} only (each passes `ov_quarantine.guard_drift`;
none in [6/5, 13/5] or its mirror). No CUSUM m = 5 tail cell and no tail drift is evaluated. No number in this file
is combined with, or placed next to, any committed tail-cell number (PREAMBLE S8), and no number here is
interpolated towards any tail drift.

Producers:
* `mech_core.py`: kernel, Nyström truth, continuous kernel.
* `mech_lp.py`: LP solver.
* `mech_study.py`: study and tables.
* `mech_pflat.py`: Proposition PF check.

Outputs:
* `validation/A306_MECHANISM.json` and `MECHANISM_TABLES.md` (generated tables).
* `validation/A306_PFLAT.json`.

Ledger: two NONTARGET_DRIFT_VALIDATION lines.

## 1. Question and why the answer could have gone either way

Four of the six operator statements are identical between the implementations (EQUIVALENT). For them, a value gap
can only come from how close each certificate gets to the true operator constant, which is implementation slack.
For D_lo, I2's statement is stronger (no premises). A stronger statement could in principle force a weaker value,
which would be a proof-strength effect.

The study measures three things:
* how far the I2-type families (the linear p-flat supersolution w = A − B·m; the linear sub-solution u = α + β·m) sit
  from the truth;
* how that distance splits into **family**, **block-uniformity** and **box/panel** parts;
* whether richer families of the **same** statement remove it.

Each outcome was possible:
* the families could have been essentially tight (the committed errata E13 found the linear D_lo family nearly tight
  at one non-target block, `C11R_ERRATA.json`:25-30);
* richer families could have plateaued far from the truth;
* the Sherman–Morrison and side-of-truth controls could have failed.

## 2. Method (declared in `mech_study.py`'s docstring before any run)

* **Truth.**
  * Piecewise-linear Nyström discretisation of K_e on R. The node sets are the m-axis, the p-axis and the interior
    level lines p + m = k·h.
  * Every integration limit lands on a node, and each linear segment × φ is integrated in closed form. The only error
    is O(h²) interpolation.
  * Solved by BiCGSTAB with 4–12 iterations and residual below 1e-12.
  * Richardson extrapolation over N = 20, 40. The reported uncertainty is |N40 − N20|/3: at most 2.5e-3 absolute on
    E_a[τ] at e = 1/2, and at most 1.3e-4 elsewhere (`truth.richardson_uncertainty`).
  * Mass balance max|rowsum + h₁ − 1| ≤ 1.2e-16.
* **Family values.**
  * An LP on the same discretised operator (N = 10, constraints at every node, plus w ≥ 0 or u ≥ 0).
  * Supersolution families minimise w(a) (for Ā on K_e, and for τ on K̂_e) or sup w (for C_T). Sub-solution families
    maximise u(a) (for D_lo on K̂_e).
  * Because the discrete truth is the extremal (super/sub)solution, each family value is ≥ the truth (≤ for D) exactly
    within the model. The slack ratio is therefore internally consistent.
* **I2's selector emulation.**
  * A float re-implementation of `c11r_boxdata.box_upper_coeffs` / `box_lower_coeffs` at C11R's frozen configuration:
    depth 5 (363 boxes), 32 u-panels, b_max 4, β_max 1.
  * Blocks [e, e + w] with w ∈ {0, 1/32, 1/16, 1/8}.
  * Cross-checked against the **exact** `c11_certifier` box bound: e = 3, depth 3, 8 panels, 30 boxes, |diff| = 1.1e-16.
* **Families** (fixed before running):
  * L1 {1, m}: I2's family.
  * M2–M6: polynomials in m.
  * PM2–PM4: polynomials in (p, m).
  * HATm: piecewise-linear in m with knots at k/2.
  * HATpm: HATm(m) + HATp(p).

## 3. Results (numbers from `MECHANISM_TABLES.md`; all non-target)

**3.1 Truth.**

| e | E_a[τ] | τ_a = (Ĝ1)(a) | sup Ĝ1 | D |
|---|---|---|---|---|
| 1/2 | 37.996 | 8.869 | 17.126 | 0.2334 |
| 1 | 10.376 | 6.661 | 9.722 | 0.6420 |
| 3 | 2.5733 | 2.5577 | 2.5733 | 0.99396 |

* sup Ĝ1 is attained **on or near the p-axis far from the atom**: at (4, 0) for e = 1, (3.7, 0.3) for e = 1/2 and
  (3, 0) for e = 3 (N = 40 grid). From such states the atom cannot be re-entered in one step.
* The identity τ_a = D·E_a[τ] (Lemma SM(d)) holds to ≤ 1e-12 in every solve.

**3.2 Family slack at a point drift** (value/truth; for D the value is ≤ 1, and 1 is exact):

| family | e = 1/2: Ā, τ, C_T, D | e = 1: Ā, τ, C_T, D | e = 3: Ā, τ, C_T, D |
|---|---|---|---|
| L1 (I2) | 17.6, 75.4, 39.0, 0.716 | 1.146, 1.786, 1.224, 0.550 | 1.164, 1.171, 1.164, 0.994 |
| M6 (p-flat, degree 6) | 1.002, 4.29, 2.22, 0.770 | 1.001, 1.560, 1.069, 0.949 | 1.002, 1.008, 1.002, 1.000 |
| HATm (p-flat) | 1.023, 4.38, 2.27, 0.796 | 1.006, 1.567, 1.074, 0.966 | 1.002, 1.008, 1.002, 1.000 |
| PM4 (p-dependent) | 1.032, 1.18, 1.17, 0.896 | 1.016, 1.069, 1.064, 0.966 | 1.008, 1.008, 1.008, 1.000 |
| HATpm (p-dependent) | 1.023, 1.10, 1.48, 0.796 | 1.006, 1.033, 1.072, 0.966 | 1.002, 1.002, 1.002, 1.000 |

Readings:
1. **Ā.** A flexible p-flat family (M6, HATm) is within 0.1–2.3 % of the truth. The linear family is not. It needs
   positive m-drift μ = e − K, and at e = 1/2, where μ = 0, it is off by a factor of ~17. Its slack at e = 1 and
   e = 3 is 15–16 %. This is family slack.
2. **τ and C_T.** Every p-flat family, whatever its degree, stays at τ/τ_a ≈ 1/D or above: M2–M6 and HATm give
   4.29–4.61 at e = 1/2 and 1.56–1.79 at e = 1; L1 is far worse at e = 1/2 (75.4). Proposition PF explains this
   exactly (§4). Families with p-dependence break the ceiling: PM3, PM4 and HATpm give τ/τ_a = 1.03–1.23; PM2 gives
   2.02 at e = 1/2. This is a family property, not a statement property: control NC1 returns the truth exactly
   when the truth is in the family.
3. **D_lo.**
   * The linear family reaches 55 % of D at e = 1, 72 % at e = 1/2 and 99.4 % at e = 3.
   * The best richer family reaches 90 % at e = 1/2 (PM4) and 97 % at e = 1 (PM4, HATm), and ≥ 99.9 % at e = 3.
   * They do not reach 100 % with low-degree polynomials at e ∈ {1/2, 1}. d has band structure (kinks at
     p + m ∈ {1, 2, 3, 4}), which a global polynomial cannot follow.
   * The full nodal family reproduces D exactly (NC1), so the remaining gap is expressiveness, not the unconditional
     statement.

**3.3 The linear family: pointwise → block → box/panel (D5/P32).**

| e | w | truth sup E_a[τ] | L1 pointwise A | L1 box A | truth inf D | L1 pointwise α | L1 box α |
|---|---|---|---|---|---|---|---|
| 1/2 | 0 … 1/8 | 37.986 | 62607 (b_max active) | 1.17e6–1.18e6 (b_max active) | 0.2335 | 0.167 | 0.000 |
| 1 | 0 | 10.376 | 11.893 | 366.0 (b_max active) | 0.6419 | 0.353 | 0.169 |
| 1 | 1/8 | 10.376 | 11.893 | 380.9 (b_max active) | 0.6419 | 0.353 | 0.153 |
| 3 | 0 | 2.5733 | 2.9945 | 3.2966 | 0.99396 | 0.988 | 0.855 |
| 3 | 1/8 | 2.5733 | 2.9945 | 3.2987 | 0.99396 | 0.988 | 0.748 |

(Pointwise values are on the Nyström grid N = 20 at three drift samples per block. The binding sample is the block's
left end, so the pointwise value does not change with w.)

* **The box/panel loss dominates when the m-drift is small against the box and panel widths.**
  * In the upper bound, the effective drift is the panel-sum of m′_lo minus the box's top m. It loses up to
    2·(box width) + (panel z-width) against the true drift μ = e − K.
  * At depth 5 and 32 panels that loss is at most 2·(5/32) + 11/32 ≈ 0.66 (arithmetic on the declared
    configuration; the panel z-width is at most 11/32). At e = 1 (μ = 1/2) it can exceed μ: the selector hits b_max and A
    inflates ~31× over the pointwise optimum.
  * At e = 3 (μ = 5/2) the loss is +10 %.
* **The D_lo box loss.**
  * The lower bound drops every panel that meets the union of atom windows over the box. It also uses the
    intersection window and m′_lo.
  * At e = 3, α falls from 0.988 (pointwise) to 0.855 (box, w = 0) and to 0.748 at w = 1/8. That is block-uniformity
    loss on top of box loss.
  * At e = 1 the box α is about half the pointwise α.
* These are generic properties of the configuration and the family. They are reported at the declared drifts only
  and are not interpolated anywhere.

## 4. Proposition PF — the p-flat ceiling (`mech_pflat.py`)

**Proposition PF.**
* *Hypothesis.* Let w(p, m) = f(m) be p-flat, w ≥ 0 and w ≥ 1 + K̂_e w on R.
* *Construction.* Put p*(m) = max(0, 1 − m). The state (p*(m), m) ∈ R has an empty atom window, so K̂_e = K_e there.
  A p-flat function ignores p′, so f ≥ 1 + K′_e f on [0, 5], where
  (K′_e f)(m) = ∫_{m−C}^{C−p*(m)} f(max(0, m − z − K)) φ(z + e) dz.
* *Conclusion.* Lemma T's induction gives f ≥ L′_e := (I − K′_e)⁻¹1, hence **τ_F = C_T,F = f(0) ≥ L′_e(0)**.
* *Proof.* Every step is the pointwise inequality at (p*(m), m) plus positivity; see the docstring of `mech_pflat.py`.
  ∎

L′_e(0) is an ARL of the m-arm (killed at its own alarm and at the p-arm alarm from p* ≤ 1). It is therefore a
whole-kernel-type quantity: no p-flat family, of any degree, certifies τ or C_T below it.

**Check (could have failed).** On the LP's own discretised operator:

| e | L′(0) | E_a[τ] (same model) | τ_a | min τ over 6 p-flat families | min τ over 4 p-dependent families |
|---|---|---|---|---|---|
| 1/2 | 37.969 | 37.955 | 8.863 | 38.034 | 9.764 |
| 1 | 10.3756 | 10.3756 | 6.659 | 10.390 | 6.877 |
| 3 | 2.57339 | 2.57339 | 2.5579 | 2.5776 | 2.5621 |

* All 18 p-flat LP values are ≥ L′(0), with no violation. At least one p-dependent family goes below L′(0) at every
  drift.
* Negative control: a planted p-flat value 0.999·L′(0) is flagged.
* L′(0) agrees with E_a[τ] to 5–6 significant figures at e = 1 and e = 3, and is 0.04 % above it at e = 1/2.

**Consequence (generic, statement-level).**
* For any p-flat taboo certificate: τ_F ≳ E_a[τ] = τ_a/D_e. The τ/D_lo branch of Lemma Dv′ r2 is then
  ≥ E_a[τ]/D_lo, so eff always binds on Ā.
* τ contributes nothing to the supply, and C_T is inflated from sup Ĝ1 to ≈ E_a[τ].
* This is the structural content of review note N6. It is a property of the ansatz, i.e. implementation slack. A
  p-dependent family certifying the **same** statement removes it.

## 5. Negative controls and coverage

| control | what it plants | result |
|---|---|---|
| NC1 truth-in-family | the discrete truth as a family member (Ā, τ, D) | LP returns it to 1e-8; the family without it (L1) is strictly looser |
| NC2 shrink | 0.99 × truth as a supersolution | screen flags min margin −0.0100; truth + 1e-9 passes |
| NC3 wrong atom split | atom piece dropped from K as well | the Sherman–Morrison identity error jumps from 6e-13 to 3.7 |
| NC4 side of truth | — (all 120 family/objective/drift LP values checked) | 0 violations |
| box cross-check | float box bound vs exact `c11_certifier` | 1.1e-16 |
| PF prediction | 0.999·L′(0) planted | flagged; 0 violations over 18 p-flat values |

Coverage:
* 3 drifts × 4 widths for the linear/box study.
* 3 drifts × 10 families × 4 objectives LPs.
* Truth at N = 20 and N = 40, plus D′ and D″ by central differences (step 1/32, N = 40).
* Wall time 268 s.

## 6. What this does and does not show

* It shows, generically, that the I2-type families carry large, drift-dependent, avoidable slack of three kinds:
  * the ansatz: linear in m, and p-flat;
  * box/panel discretisation;
  * block uniformity.
* It also shows that richer families of the **same** statements remove most of it. Where they do not, the reason is
  the band structure, which the full nodal family resolves.
* It does **not** estimate the size of any of these effects at any tail drift, and must not be used to. By design no
  number here is carried to a tail cell (PREAMBLE S1, S8).
* All values are float and non-certified. The certified counterpart of the "sandwich" idea is in
  `common/THEOREM_CV.md`.
