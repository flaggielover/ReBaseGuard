# K5_PERRON_DEFLATION_FEASIBILITY — report

Start frontier `5a8c194d` (verified on GitHub). All work is additive in this namespace. No real scientific computation,
no new real campaign namespace, no authorization or countersignature, no new R''' or R⁽⁵⁾, no frozen or adopted
artifact modified, AWS PS1 not touched, main untouched.

## 1. What the "Perron mode" is, exactly

The CUSUM kernel K_e acts on bounded Borel functions on the reachable set X and has an **atom at the evaluation point**
a = x0 = (0,0): K_e = K̂_e + k_a ⊗ δ_a exactly (the frozen "origin" piece). The slow mode is the regeneration of the
chain at a. Sherman–Morrison gives the exact identity

    (I − K_e)⁻¹ = Ĝ_e + (Ĝ_e k_a) ⊗ δ_aĜ_e / D_e,     D_e = P_a(alarm before return to a) = (Ĝ_e h_1)(a) > 0,

with a **positive** complement Ĝ_e (the taboo resolvent) and an **e-independent** left functional δ_a. At the atom,
R_e f(a) = ν_e(f)/D_e, and the whole amplification is one scalar: E_a[τ] = E_a[τ ∧ T_a]/D_e ≈ 6.8 × 69 ≈ 465.
No eigenpair, spectral projection, gap or conditioning number is used. At e = 0, σ-parity switches the channel off on odd
sources (ν_0(odd) = 0), which is why slot-1 worked.

## 2. What deflation can and cannot do (theorem AD)

- **Cannot:** improve an order-0 point value from a residual norm. sup_{‖f‖≤1} |R f(a)| = E_a[τ] is attained (Lemma SM(d)).
  The only order-0 gain is the sharp E_a[τ] (certified ≈ 371–501) against the one-sided C_upper (514–1233).
- **Can:** remove the products of Perron amplifications in the frozen error DAG. The order-1 and order-2 cross terms C²k₁
  and 2C³k₁² + C²k₂ become one channel division times tame factors: A1 = Ā(κ₁C_T + |D'|/D), A2 = Ā(2κ₁²C_T² + κ₂C_T +
  2κ₁C_T|D'|/D + 2(D'/D)² + |D''|/D), with C_T = ‖Ĝ‖ ≈ 19. The moving projection is avoided: only the scalar D_e and the
  positive Ĝ_e move.

## 3. Certified operator registry r1 (operator only; `evidence/registry_r1/REGISTRY.json`, sha256 1b7f5da7…)

| quantity | certified range over the front cells 11–148 | float value | ratio |
|---|---|---|---|
| ‖Ĝ_e‖ (C_T), 12 e-blocks on [0, 0.12] | 19.07 – 19.40 | 15.8 – 16.1 | 1.21 |
| E_a[τ ∧ T_a] (τ) | 8.155 – 8.400 | 6.80 – 7.02 | 1.20 |
| E_a[τ] (Ā), per cell | 371.3 – 500.9 | 325 – 466 | 1.08 – 1.14 |
| D_e lower bound, per cell | 0.01228 – 0.01783 | 0.0146 – 0.0215 | 0.83 – 0.84 |
| \|D'\| bound, per cell | 0.045 – 0.215 | 0 – 0.13 | — |
| \|D''\| bound, per cell | 4.28 – 8.92 | 1.02 – 1.36 | 4.1 – 6.5 |

Improvement of the error-propagation constants over the generic K1 stack (C_upper): order 0 ×1.4–2.3, order 1 ×21–117,
order 2 ×280–4288. Complement constant against the generic resolvent: 1233/19.07 ≈ 65 at e = 0, 514/19.40 ≈ 26 at cell 148
(against the sharp ARL: ≈ 24 and ≈ 16).

Certifier checks (pre-freeze, `evidence/precheck_r1/`): X-A float dominance PASS; X-B independent Fraction recomputation
PASS (max deviation 8.8e-8); probe PASS (the correct certifier refuses a wide block, a point certificate would accept it);
falsification gate PASS (independent Gauss–Legendre quadrature on 1,495 states: true supersolution margins ≥ 0.068,
residual ratios ≤ 0.67; all four planted certifier bugs flagged).

## 4. Frozen feasibility gate (thresholds frozen at 3e71dd3a, before any certified computation)

Result **USEFUL**: for every front cell the certified A-constants are dominated by the forecast model at scale 1.6, so
(the consumer and the frozen K5-B being monotone) the certified consumption closes at least what the forecast at 1.6
closes. STRONG was declared unattainable by this route before the certified run (order-0 floor).

| m | open now | guaranteed open at most after the successor (forecast at s = 1.6) | expected (forecast at s ≈ 1.3) |
|---|---|---|---|
| 1 | 11–132 (122) | 11–44 (34) | 11–38 |
| 2 | 11–144 (134) | 11–52 (42) | 11–45 |
| 3 | 11–145 (135) | 11–52 (42) | 11–46 |
| 5 | 11–148, 305–309 | 11–54, 305–309 | 11–48, 305–309 |

The guaranteed column is exact arithmetic on published records with float constants (FORECAST, labelled), turned into a
lower bound for the certified consumption by the per-cell dominance of certified over forecast constants. The certified
consumption itself is the frozen successor's evaluation.

## 5. What remains open and why

- **Lower front (cells 11 to ≈ 38–54 per m).** The K1 midpoint residuals put the order-0 floor E_a[τ]·‖ρ_F‖ ≈ 1.7e-3
  (m = 1) to ≈ 4.5e-3 (m = 5) above |g| ≈ (R'''(0)/3)e³ there, and the whole-cell R'' radius (≈ 100–700 with delta_cell
  residuals) keeps H.lo < 0, so the K5-B chain cannot carry from T-EXT's cell 10. This needs order-3 information beyond
  e = 0. FORECAST: the channel alone makes |R⁽⁵⁾(0)| ≈ |R'(0)|·120·β², β = D''/(2D) ≈ 35, i.e. ≈ 2.2e6 (m = 1) … 1.35e6
  (m = 5); reaching the boundary cells needs M5 ≤ 2L0/x² ≈ 5.6e6 (m = 1, cell 44) … 2.2e6 (m = 5, cell 54). An atom-deflated
  order-3 tower within ≈ 1.6–2.5× of the channel scale would therefore close the lower front with zero new values. T-EXT's
  graded tower is 50–100× above it at x1. Unforecast whether a certified tower can be that sharp.
- **m = 5 tail 305–309.** Unchanged (outside the deflation domain; curvature slack; `tail_design/` stands).

## 6. Status of the successor (see §7 of the final report for the execution state)

`K5_PERRON_DEFLATED_SUCCESSOR_SPEC.md`: deterministic, additive, zero new real addresses; the consumer refuses before the
freeze, requires a committed QUALIFIED qualification for its protocol, writes a ledger, and replays the adopted T-EXT C2
consumption byte-identically with an empty registry (checked). Independent review: r1 PASS_WITH_NOTES, r2 PASS_WITH_NOTES
(not ready: certifier falsification, dependency pins), both addressed.
