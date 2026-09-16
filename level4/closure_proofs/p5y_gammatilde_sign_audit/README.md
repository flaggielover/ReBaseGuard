# P5Y — GammaTilde_m > 1 sign audit (CUSUM, m = 2, 3, 5), result r1

A **reuse and certification audit**. No scientific computation was run. Every number here is exact rational
arithmetic on fields of one committed, hash-bound certified record: the CUSUM Aux5 cell-0 record copy
(`p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json`, sha256 `4f8df44c…`). That hash
matches the composite export manifest, and the frozen `hash_v2` scientific hash recomputes. This namespace is
additive. It does not modify any P1/P5/K1/CUSUM evidence, and it does not close K5 or P5Y.

```bash
python3 -B code/verify_gammatilde_sign.py        # GAMMATILDE_SIGN_RESULT_VERIFIED <sha256>
python3 -B tests/test_gammatilde_sign.py         # ok
```

## Why

H3a writes `s(0+) = GammaTilde_m − 1 = 1/rho_c`, and P3-T1 defines `rho_c = 1/|1 − GammaTilde_m|`. The second
equality holds only when `GammaTilde_m > 1`. K5-B does not prove it. The premise-binding audit r1 found it
certified for m = 1 only.

## Definition (Phase 0)

- `GammaTilde_m = E_0[A_m T_tau]`, where `A_m = (1/w) Σ_{r<w} Z_{tau−r}` and `w = min(m, tau)`. The window
  includes the terminal alarm increment and keeps the random denominator (convention A).
- `T_tau = Σ_{t≤tau} Z_t` and `Z_t = X_t − R ~ N(−e, 1)`.
- The detector is the frozen two-sided Gaussian CUSUM: `k = 1/2`, inclusive threshold `h = 5`, reset state.
- The score is `dL_e/de|_0 = −T_tau`.
- P1-T1 (EXACT_THEOREM, independently reviewed) gives `F'_{rho,m}(0) = rho(1 − GammaTilde_m)`. With the K1
  raw-variable `R_m(e) = e + E_e[A_m]` at `rho = 1`, this is `R_m'(0) = 1 − GammaTilde_m`.
- The signs are consistent: `GammaTilde > 1 ⇔ R'(0) < 0 ⇔ s(0+) > 0`. **RPRIME_ZERO_IDENTITY = PASS.**

## Evidence (Phases 1–2)

| Source | Class | Settles m > 1? |
|---|---|---|
| CORE-C1 Arb: `GammaTilde_1 ∈ [3.9243482, 27.8493821]` | CERTIFIED_INTERVAL | no (m = 1 only) |
| P1-T1 identity; P1 T3/T4 decomposition with `Q_m ≥ 0` | EXACT_THEOREM | identity only, no value |
| P1-N1 estimates 13.265 / 11.957 / 10.226 | PREREGISTERED_ESTIMATE | no |
| P1 finite-support witness (`GammaTilde = 15/2`) | UNUSABLE for Gaussian | no |
| P3-N1 rho_c, d4 gamma grid, P8-S3 | EMPIRICAL_ESTIMATE | no |
| P5-MECH "GammaTilde ~ 9–17" | HEURISTIC | no |
| Cell-0 `D_interval` ± `e0·M_R2` (premise-binding r1) | CERTIFIED_DERIVED_BOUND | no (the intervals contain 0) |
| Cell-0 `supF3_final` and order-3 norm towers (this audit) | CERTIFIED_DERIVED_BOUND | **m = 2 only** |

Direct reuse finds nothing: no certified interval exists for `GammaTilde_m` with m > 1.

## Derivative-identity route (Phase 3): odd-C³ widening

Cell 0 is `[0, 2e0]`, with `e0 = 5083/20000000`. The first-order widening `e0·M_R2` (7.6–7.9) swallows the sign.
Oddness gives something tighter. R is odd (P5-T3), so `R''` is odd and `R''(0) = 0`. Then

```
R'(e0) − R'(0) = ∫_0^e0 (e0 − s) R'''(s) ds,      |·| ≤ (e0²/2) · M3(m)
M3(m) = (1/m) Σ_{r<m} supF3_r  +  Σ_t c_(m,t) Σ_r T_W[(r, t−r−1), 3]
```

The inputs come from the committed record:

- `supF3_r` is refine2's whole-cell majorant of `‖∂_e³ F_r‖` (REFINE2_SOUND = YES).
- `T_W[·, 3]` are aux_refine's norm towers (AUXILIARY_DERIVATIVE_SOUND = YES). Each is stored on the order-1
  node as `tower_next_order`. This storage is checked against refine2's independently recorded `sup|S_0'''|`.
- `c_(m,t) = 1/t − 1/m` are the ERROR_ALGEBRA §4 coefficients.

| m | D_interval(e0).hi | E = (e0²/2)·M3 | R'(0) upper | GammaTilde bound (outward decimals) | verdict |
|---|---:|---:|---:|---|---|
| 1 (control) | −10.3142 | 1.5954 | −8.7187 | [9.718727, 22.054855] ⊂ CORE-C1 | certified (already) |
| 2 | −3.7309 | 2.9647 | **−0.7663** | **[1.766264, 24.748817]**, margin 0.766264 | **CERTIFIED** |
| 3 | −2.5326 | 2.9177 | +0.3850 | [0.614984, 23.235820] | NOT_CERTIFIED (M3 is 1.15× too large) |
| 5 | −0.9404 | 2.8678 | +1.9275 | [−0.927465, 21.307502] | NOT_CERTIFIED (M3 is 3.05× too large) |

Other checks:

- Every interval contains the P1-N1 estimate. Nothing refutes the sign.
- `supF3` is dominated by the loop `3·C·k1·epsH_cell`, with `rho·C·2k1 ≈ 0.5`. It cannot be tightened with
  recorded fields alone.
- `R(e0)/e0` gives width ≈ 65, and whole-cell `epsD_cell` exceeds `|center|`. Neither helps.

## Analytic route (Phase 4): not proved

- Monotonicity in m is not proved; the decreasing P1-N1 values are empirical.
- The m = 1 result does not transfer. `E[B_m T_tau] = (1/m) Σ_{r<m} G_r` with
  `G_r = E_0[Z_{tau−r} T_tau; tau > r]`, and only `G_0` is certified.
- `tau − r` is not a stopping time, so Wald-type identities do not split `G_r`.
- `Q_m ≥ 0`, but it is tiny at h = 5.
- The survival event is not monotone, so FKG/association arguments fail.
- The m = 1 closure itself records that the cross term `E[Z_tau T_{tau−1}]` has no established sign.

## Minimal new evidence (Phase 5), not computed and not authorized

For m = 3 and m = 5:

- **Option A (preferred):** one certified point evaluation of `D_interval` at `e = 0` exactly. It uses the
  frozen K1 CUSUM kernel's midpoint objects only (orders 0–1, no whole-cell curvature). One run covers all m.
  It needs a new governed point-certificate protocol. Estimated cost: about 0.1–0.2 CPU-h on a single thread.
- **Option B:** one Aux5 cell `[0, 2e']` with `e' ≤ e0/4`, under a new checkpoint. Estimated cost: about
  0.6 CPU-h (cell 0 took 2055 CPU-s).
- **Forecast, not evidence:** carrying the e0 midpoint widths over to e = 0 would put `D(0).hi` near −2.5 for
  m = 3 and −1.0 for m = 5. The m = 5 margin would be thin.

## Governance (Phase 6)

- **The cell-0 record:**
  - It came from the K1 Aux5 campaign (2026-09-13 to 2026-09-16) under frozen checkpoint `f9380847`.
  - It was produced for K1, not for K5.
  - Its producer was adjudicated sound.
  - Its `supF3` and tower fields are SCIENTIFIC under `hash_v2`, and they carry weight elsewhere (they feed
    M_R2 and the K1 cover charge). This audit only reads them.
- **The R'''-based use is new.** It was not preregistered and is not independently countersigned, so this
  namespace is its additive certification wrapper.
- **The m = 2 bound inherits the P5X L5 (C³) note:** internal proof only, never independently reviewed.
  Independent countersignature is recommended before anything depends on it.
- **No estimate was promoted.**

## Verdicts

```
GAMMATILDE_GT_1_M2 = CERTIFIED   (CERTIFIED_DERIVED_BOUND, lower 1.766264, margin 0.766264)
GAMMATILDE_GT_1_M3 = NOT_CERTIFIED
GAMMATILDE_GT_1_M5 = NOT_CERTIFIED
ALL_CUSUM_M_GAMMATILDE_GT_1 = NOT_CERTIFIED
H3A_POSITIVE_BRANCH_PREMISE = OPEN
NEW_SCIENTIFIC_COMPUTE_REQUIRED = YES
SCIENTIFIC_COMPUTE_RUN = NO; CUSUM_CLOSURE_MODIFIED = NO; K1_MODIFIED = NO; AWS_PS1_TOUCHED = NO;
ORIGIN_MAIN_TOUCHED = NO; K5_DECLARED_CLOSED = NO; P5Y_DECLARED_CLOSED = NO
```

Machine result: `result_r1/GAMMATILDE_SIGN_RESULT.json`. Pinned sources at base `10769e07`: `config/SOURCES.json`.
