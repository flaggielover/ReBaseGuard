# Pre-registration — HISTORICAL_RECONSTRUCTION R1–R4 for CUSUM m = 5 cell 308 (Stream A)

Written **before any script was run** (2026-09-28, Stream A). Sanctioned location (`history/recon/`).
Class: HISTORICAL_RECONSTRUCTION. `LP/` = `level4/closure_proofs/`. Worktree `/Users/suzhe/ReBaseGuard-c308`,
branch `p5y-k5-cell308-research` @ `33185113`.

**Output rule.** For every item the output is: the committed value (with file:line), an equality boolean, and the
recomputed exact value. Nothing outside this list is computed. No supply, clause, drift point or evaluation point other
than those listed is used. A mismatch is reported as a discrepancy; inputs are never adjusted.

## Evaluation points (the complete list; every one is a committed supply or a committed statement's point)

| id | (A0, A1, A2) | committed where |
|---|---|---|
| P_SI1 | S_I1 = C2 D5 `A_exact` (exact strings) | `LP/p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json` cells["308"] (l.106–110) |
| P_MIX | C3 operator-mixed A = Lemma Dv′(r2) of the committed exact `operator_tuple` | `LP/p5y_k5_tail_c3_closure/evidence/forecast/C3_FORECAST.json` cells["308"] |
| P_KO | (A0_mixed, 0, 0) | C3 adjudication §K row 308; C4 `C4_THRESHOLDS.json` cells["308"] |
| P_ZERO | (0, 0, 0) | C4 `C4_THRESHOLDS.json` cells["308"].monotone.Gamma_at_A0_zero |
| P_CRIT | (A0*, 0, 0), A0* = exact root of A0 ↦ Γ(A0, 0, 0) | C3 adj. §K (4.3752); C4 `C4_TARGET_RECONSTRUCTION.md:76` (4.375228833136) and the bisection bracket in `C4_THRESHOLDS.json` |
| P_4311 | (4311/1000, A1_mixed/s*, A2_mixed/s*) | C4 adjudication §4 (l.186–188); `OPEN_NOTES_DISPOSITION_C4.md:52`; `C4_TARGET_RECONSTRUCTION.md:119–121` |
| P_4375 | (4375229/1000000, 0, 0) | `OPEN_NOTES_DISPOSITION_C4.md:52–53` ("Gamma = +0.000000008 at A0 = 4.375229 with A1 = A2 = 0") |

## Committed non-constant inputs (read only)

* `LP/p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_308.json` (meas).
* `LP/p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json` cells["308"]: `auxiliary_evidence`
  (aux) and `m["5"]` (R_interval, D_interval, R2_interval, M_R2).
* `LP/p5y_k1_cover_ledger_successor/config/cells.json`, the CUSUM entry with index 308 (e0, rho, right), filtered on
  `detector == "CUSUM"` first.

## Frozen functions used (imported by file path, not modified; imports have no side effects)

* `LP/p5y_k5_m5_tail_closure/code/tct_rule.py`: `tail_enclosure` (frozen-rule path), `tail_enclosure_crosscheck`
  (independent path), `load_frozen` (loads the sha-pinned `LP/p5y_k5_lower_front_order3/code/tc_rule.py`).
* `LP/p5y_k5_tail_c2_closure/code/c2_d5_forecast.py`: `direct` (the frozen K5-B direct clause as C2/C3/C4 ran it) and
  `_atom_independent` (C2's independent Lemma Dv′). Its `main()` is **not** run.
* `LP/p5y_k5_perron_deflated_resolvent/code/deflated_consume.py` (sha pinned `ef5d0474…`): `atom_constants_r2`
  (Lemma Dv′ r2). Its `main()` is **not** run.
* A shim `rat(p) = F(p) if str else F(p[0]) + F(p[1])`, copied verbatim from `tail_forecast_r2.rat` /
  `k5_minimality.rat`, is passed as the `KM`/`B` argument of `direct` (the frozen modules that carry it are not
  imported).
* An independent re-implementation of the direct clause (own code) is run alongside `direct`; both must agree.

## R1 — C2's committed Γ₃₀₈ under S_I1 (frozen direct clause)

| item | quantity recomputed | committed comparand |
|---|---|---|
| R1.1 | TC-T enclosure [lo, hi] at P_SI1 (frozen path; crosscheck path must agree) | `H_exact` (C2_D5_FORECAST.json l.113–117), exact equality |
| R1.2 | M at P_SI1 | `M_after_exact` (l.118), exact equality; `magnitude`/`M_after` floats |
| R1.3 | Γ at P_SI1 via frozen `direct` and via the independent re-implementation | `Gamma_exact` (l.112) exact equality; `Gamma` float (l.111) equality of `float()` |
| R1.4 | pass flag | `pass: false` |

Route: frozen consumer functions on committed inputs (route 1). Route 2 (committed intermediates only) is the
fallback if route 1 is impossible without side effects.

## R2 — the C3 adjudicator's knockout row for 308

| item | quantity recomputed | committed comparand |
|---|---|---|
| R2.1 | A_mixed = `atom_constants_r2(operator_tuple)`; must equal `_atom_independent(operator_tuple)` | C3_FORECAST cells["308"].A floats (equality of `float()`); `A0_certified` exact string in `LP/p5y_k5_tail_c4_exhaustion/evidence/phase1/C4_THRESHOLDS.json` cells["308"]; C3 adj. §K "A0 certified 5.2185" (4 dp) |
| R2.2 | Γ at P_MIX (frozen `direct` + independent) and magnitude | C3_FORECAST cells["308"].Gamma float and `magnitude` float; `C3_EXECUTION.json` per_cell Gamma; C3 adj. §K "+0.094564" (6 dp) |
| R2.3 | Γ at P_KO | C4_THRESHOLDS `Gamma_A1A2_zero_at_certified_A0` float; C3 adj. §K "+0.039568" (6 dp) |
| R2.4 | A0* exact rational = −(g_hi + ρ·x_hi·\|C_lo\|)/(ρ·x_hi·P̄2) (coefficients from R4); then Γ at P_CRIT via the frozen `direct` (must be exactly 0) and the regime facts at P_CRIT: intersection non-empty, lower endpoint binding (lo ≥ R2.lo, so a = lo), C_lo < 0, \|a\| ≥ \|b\|, \|a\| ≤ M_R2 | C4 bracket `closes_below_exact` ≤ A0* ≤ `open_at_or_above_exact` (containment boolean); C4 `outward_rounded_12dp` "4.375228833136" (A0* ≤ it and `f"{A0*:.12f}"` equality); C3 adj. "4.3752" (4 dp) |
| R2.5 | A0_mixed / A0* and 100·(1 − A0*/A0_mixed) | C3 adj. "×1.1927 (16.2 %)"; C4 `A0_reduction_factor_needed_from_certified` 1.19274872192929 and `A0_reduction_percent_needed` 16.16004430652551 (C4 used its bracket's lower end; compared to 12 significant digits and reported) |

## R3 — the C4 adjudicator's §4 statement

| item | quantity recomputed | committed comparand |
|---|---|---|
| R3.0 | Identification of the (A1, A2) C4 used — **documentary only** (C4 `code/c4_common.py` `cell_supply` → C3 selector `build` → C3 operator-mixed supply; C4's "A0 certified" = A0_mixed). No alternative supply is evaluated. | — |
| R3.1 | s* exact = ρ·x_hi·(2·A1_mixed·P̄1 + A2_mixed·P̄0) / −(g_hi + ρ·x_hi·\|C_lo\| + ρ·x_hi·(4311/1000)·P̄2); then Γ at P_4311 via frozen `direct` (must be exactly 0) and the regime facts there | "18.2496×" (4 dp, `OPEN_NOTES_DISPOSITION_C4.md:52`, `C4_TARGET_RECONSTRUCTION.md:121`); "18.2×" (1 dp, `C4_ADJUDICATION.md:187`) |
| R3.2 | Γ at P_4375 via frozen `direct`; regime facts there; P̄1 ≥ 0 and P̄0 ≥ 0 (so Γ(4.375229, A1, A2) ≥ Γ(4.375229, 0, 0) for all A1, A2 ≥ 0 by enclosure widening) | "+0.000000008" (9 dp, `OPEN_NOTES_DISPOSITION_C4.md:52–53`); "impossible at any (A1, A2)" (`C4_ADJUDICATION.md:187–188`) |

## R4 — affine structure for 308 under the frozen direct clause

Coefficients (exact, cell 308, written only into `history/recon/`): ρ, x_hi, e0, R.hi, D.lo,
g_hi := R.hi − e0·D.lo, C_lo and C_hi (the TC-T enclosure endpoints at A = 0, i.e. Σ_r (1/5)·H_at_a(r) plus the W
terms), P̄j := (1/5)·Σ_r p_j(r) for j = 0, 1, 2 (p from the frozen `tail_enclosure` object output; verified identical
at every evaluation point, i.e. independent of A), R2.lo, R2.hi, M_R2.

| item | check | committed comparand |
|---|---|---|
| R4.1 | at each of P_SI1, P_MIX, P_KO, P_ZERO, P_CRIT, P_4311, P_4375: frozen-consumer Γ == g_hi + ρ·x_hi·\|C_lo\| + ρ·x_hi·(A0·P̄2 + 2·A1·P̄1 + A2·P̄0) exactly | the formula of `LP/p5y_k5_tail_overnight_research/graph/K5_TAIL_DEPENDENCY_GRAPH.md` §0 (l.32) |
| R4.2 | regime facts at each point: intersection non-empty; [lo, hi] ⊆ R2_interval; lo ≥ R2.lo (lower endpoint of the intersection is lo); lo < 0; \|lo\| ≥ \|min(hi, R2.hi)\|; \|lo\| ≤ M_R2; C_lo < 0 | graph §0 "𝓗 ⊆ R2_interval; the lower endpoint binds; C_lo < 0" (l.25–28) |
| R4.3 | Γ at P_ZERO equals g_hi + ρ·x_hi·\|C_lo\| | C4_THRESHOLDS `monotone.Gamma_at_A0_zero` float |
| R4.4 | P̄0, P̄1, P̄2 > 0 and ρ·x_hi > 0 (Γ strictly increasing in each A_j on the regime) | — (structural) |

## Not computed (explicitly out of scope)

No uniform-reduction factor (C2 1.50029…, C3 1.46065…), no C5-T clause value, no C8 quantity, no Γ at any point
not listed above, no Γ for cells 305, 306, 307 or 309, no sensitivity or "what-if" evaluation, no registry read,
no RLR/TPT/Theorem-M quantity. The C5-T statements in `PRUNING_308.md` cite committed C8 values only.
