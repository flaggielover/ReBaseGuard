# Cell 308 — pre-registered HISTORICAL_RECONSTRUCTION R1–R4 (Stream A, Task 2)

Sanctioned location (`history/recon/`). Class HISTORICAL_RECONSTRUCTION. Pre-registration:
`RECON_PREREGISTRATION.md` (written before any run). Script: `recon_308.py` (header lists the frozen modules it
imports and why). Exact output: `C3_KNOCKOUT_RECONSTRUCTION.json` (sha256 `b2a00ace06a2498e…`; every rational as a
string). Ledger: two HISTORICAL_RECONSTRUCTION lines (START / END, 2026-09-28T13:04:30Z), `new_target_evaluations: 0`.

**Result: 55 / 55 pre-registered comparisons equal. No discrepancy in any reproduction.** Every evaluation point
is a committed supply or the point of a committed statement (7 points; list in the pre-registration). Nothing
outside the pre-registered list was computed.

## Route and inputs

* **R1 route: route 1** — the frozen consumer functions on committed inputs: `tct_rule.tail_enclosure` (frozen-rule
  path, with the sha-pinned `tc_rule.py`), `tct_rule.tail_enclosure_crosscheck` (independent path, asserted equal
  inside `direct`), and `c2_d5_forecast.direct` (the frozen K5-B direct clause). No module's `main()` was run; no
  import has side effects. An independent re-implementation of the clause and the affine closed form (R4) were run
  alongside and agree exactly at every point.
* Frozen code identities (git blob, matching the pins of floor r2 `FLR:76` / the dependency graph §0):
  `c2_d5_forecast.py` 18403dbe, `deflated_consume.py` a0a836fa (sha256 ef5d0474…, the C2 `DC_SHA` pin),
  `tct_rule.py` 98f6eee4, `tc_rule.py` sha256 8d402d11… (the `tct_rule.FROZEN` pin).
* Committed inputs (sha256 prefix): `TCT_INPUTS_308.json` 386f4a7774d69b0c (= MEASUREMENT_NOTE.md:22 `386f4a77…`),
  `ADOPTED_TAIL_INPUTS.json` 485fb1254e459683 (= MEASUREMENT_NOTE `485fb125…`), `cells.json` (K1 cover ledger
  successor) 341eb5e95161bbdc, `C2_D5_FORECAST.json` 784f25eecd65bad3, `C3_FORECAST.json` ad36d408f62119ce,
  `C3_EXECUTION.json` 4ca9b7ca6cc5464a, `C4_THRESHOLDS.json` 224ad5f143c4d8c7.
* The C3 mixed atom constants are **not committed as exact rationals**; C3 committed the exact operator tuple
  (`C3_FORECAST.json` cells["308"].operator_tuple: Ā, τ, C_T, D_lo, D1, D2; provenance Ā/τ/C_T ← C1, D_lo/D1/D2 ← C2).
  A_mixed = Lemma Dv′ r2 of that tuple (`deflated_consume.atom_constants_r2`, cross-checked equal to C2's
  independent `_atom_independent`). Its A0 equals C4's committed exact `A0_certified` string, and its three floats
  equal C3's committed floats (R2.1).
* **C4's (A1, A2) — identified documentarily:** `c4_common.cell_supply` → `c3_selector.build` → the C3
  operator-mixed supply; C4's `A0_certified` is A0_mixed. So "the committed supply that C4 used" = C3 mixed
  (A1, A2) = (22.79374449569498, 230.3658154880664). No alternative supply was evaluated.
* A0 = 4.311 and A0 = 4.375229 were parsed from the committed text (`OPEN_NOTES_DISPOSITION_C4.md:52–53`) and used
  as exact decimals 4311/1000 and 4375229/1000000.

## R1 — C2 D5 Γ₃₀₈ under S_I1 (frozen direct clause)

| item | quantity | committed | source | equal | recomputed |
|---|---|---|---|---|---|
| R1.1 | TC-T enclosure [lo, hi] | exact strings | C2_D5_FORECAST.json cells[308].H_exact (l.113–117) | True | exact (JSON `points.P_SI1`) |
| R1.2 | M_after_exact | exact string | l.118 | True | exact (1509 chars) |
| R1.2b | magnitude float | 3.4524564789357517 | cells[308].magnitude | True | 3.4524564789357517 |
| R1.3 | Γ exact | exact string | l.112 | True | exact (1536 chars), identical |
| R1.3b | Γ float | 0.10270008356594545 | l.111 | True | 0.10270008356594545 |
| R1.4 | pass | False | cells[308].pass | True | False |

## R2 — the C3 adjudicator's §K knockout row (`C3_ADJUDICATION.md:350`, ref p5y-k5-tail-c3 @ 019ecce0)

| item | quantity | committed | source | equal | recomputed |
|---|---|---|---|---|---|
| R2.1a | `atom_constants_r2` == `_atom_independent` on the tuple | — | frozen functions | True | exact (JSON) |
| R2.1 | A_mixed floats A0 / A1 / A2 | 5.218548598870686 / 22.79374449569498 / 230.3658154880664 | C3_FORECAST.json cells[308].A | True ×3 | identical |
| R2.1-A0exact | A0_mixed exact | exact string (156 chars) | C4_THRESHOLDS.json cells[308].A0_certified (l.35) | True | identical |
| R2.1-A0-4dp | "A0 certified" | 5.2185 | C3_ADJUDICATION.md:350 | True | 5.2185 |
| R2.1-eff | A0_mixed = τ/D_lo < Ā ("5.2185 (= τ/D_lo)") | — | C3 adj. §K text | True | True |
| R2.2 | Γ(mixed) float | 0.09456414496566364 | C3_FORECAST.json | True | 0.09456414496566364 |
| R2.2b | Γ(mixed) float | 0.09456414496566364 | C3_EXECUTION.json per_cell[308] | True | 0.09456414496566364 |
| R2.2c | Γ(mixed), 6 dp | +0.094564 | C3_ADJUDICATION.md:350 | True | +0.094564 |
| R2.2d | magnitude(mixed) | 3.3716470503119877 | C3_FORECAST.json | True | 3.3716470503119877 |
| R2.2e | closes | False | C3_FORECAST.json | True | False |
| R2.3 | Γ(A0_mixed, 0, 0) float | 0.039567845828196446 | C4_THRESHOLDS.json l.37 | True | 0.039567845828196446 |
| R2.3b | Γ(A0_mixed, 0, 0), 6 dp | +0.039568 | C3_ADJUDICATION.md:350 | True | +0.039568 |
| R2.3c | closes at A1 = A2 = 0 | False | C4_THRESHOLDS.json | True | False |
| R2.4a | Γ(A0*, 0, 0) by the frozen consumer | 0 (definition) | — | True | exactly 0 |
| R2.4b | A0* ∈ [closes_below_exact, open_at_or_above_exact] | C4 bracket (width 3.1e-66) | C4_THRESHOLDS.json l.44, l.46 | True | A0* exact (850 chars) |
| R2.4c | A0* ≤ 4.375228833136 and `%.12f`(A0*) = it | 4.375228833136 | C4_THRESHOLDS.json l.47; C4_TARGET_RECONSTRUCTION.md:76 | True | 4.375228833136 (float 4.375228833135616) |
| R2.4d | A0*, 4 dp | 4.3752 | C3_ADJUDICATION.md:350 | True | 4.3752 |
| R2.4e | A0* in the C4 phase-1 table | 4.375228833136 | C4_TARGET_RECONSTRUCTION.md:76 | True | 4.375228833136 |
| R2.5a | A0_mixed / A0* (float equality and 12 s.d.) | 1.19274872192929 | C4_THRESHOLDS.json l.40 | True | 1.19274872192929 |
| R2.5b | 100·(1 − A0*/A0_mixed) (float equality and 12 s.d.) | 16.16004430652551 | C4_THRESHOLDS.json l.41 | True | 16.16004430652551 |
| R2.5c | C3 adj. "×1.1927 (16.2 %)" | ×1.1927 (16.2 %) | C3_ADJUDICATION.md:350 | True | ×1.1927 (16.2 %) |

**Regime at the root (pre-registered check).** At (A0*, 0, 0): the TC-T/K5-B intersection is non-empty, the TC-T
enclosure lies inside the R2 interval, the lower endpoint binds (lo ≥ R2.lo and |lo| ≥ |min(hi, R2.hi)|), lo < 0,
|lo| ≤ M_R2, and C_lo < 0 — all **true**. So A0* is the root of the affine map, and the number is reported
(it is not replaced by a regime failure).

## R3 — the C4 adjudicator's §4 statement (`C4_ADJUDICATION.md:186–188`; ref p5y-k5-tail-c4 @ e12a09e8)

s* := the uniform divisor of the C3-mixed (A1, A2) at which Γ(4.311, A1/s*, A2/s*) = 0, solved exactly on the
affine form: s* = ρ·x_hi·(2·A1·P̄1 + A2·P̄0) / −(G0 + ρ·x_hi·4.311·P̄2).

| item | quantity | committed | source | equal | recomputed |
|---|---|---|---|---|---|
| R3.1a | Γ(4.311, A1_mix/s*, A2_mix/s*) by the frozen consumer | 0 (definition) | — | True | exactly 0 |
| R3.1b | s*, 4 dp | 18.2496 | OPEN_NOTES_DISPOSITION_C4.md:52 | True | 18.2496 (float 18.24959815514518; exact in JSON) |
| R3.1c | s*, 1 dp | 18.2 | C4_ADJUDICATION.md:187 | True | 18.2 |
| R3.1d | s*, 4 dp | 18.2496 | C4_TARGET_RECONSTRUCTION.md:121 | True | 18.2496 |
| R3.2a | Γ(4.375229, 0, 0), 9 dp | +0.000000008 | OPEN_NOTES_DISPOSITION_C4.md:52–53 | True | +0.000000008 (float 7.829e-09) |
| R3.2b | "impossible at any (A1, A2)": Γ(4.375229, 0, 0) > 0, P̄1 ≥ 0, P̄0 ≥ 0, intersection non-empty | stated | C4_ADJUDICATION.md:187–188 | True | True |
| R3.2c | 4.375229 > A0* | — | consistency | True | True |

Why R3.2b proves the statement: every A_j enters only the half-widths half_r = A0·p2(r) + 2·A1·p1(r) + A2·p0(r)
with p_j(r) ≥ 0, so raising A1 or A2 widens [lo, hi]; a non-empty intersection stays non-empty and its magnitude
max(|a|, |b|) cannot fall; M = min(M_R2, ·) and Γ = g_hi + ρ·x_hi·M are then non-decreasing. Hence
Γ(4.375229, A1, A2) ≥ Γ(4.375229, 0, 0) > 0 for every A1, A2 ≥ 0.

## R4 — affine structure of Γ₃₀₈ under the frozen direct clause

Checked at every evaluation point (P_SI1, P_MIX, P_KO, P_ZERO, P_CRIT, P_4311, P_4375): the frozen-consumer Γ
equals **exactly**

    Γ(A0, A1, A2) = [R.hi − e0·D.lo] + ρ·x_hi·|C_lo| + ρ·x_hi·(A0·P̄2 + 2·A1·P̄1 + A2·P̄0)

(`K5_TAIL_DEPENDENCY_GRAPH.md:32`); lo = C_lo − Σ_r (1/5)·half_r and hi = C_hi + Σ_r (1/5)·half_r exactly; the
p_j(r) are identical at every point (independent of A); the independent path agrees exactly; and all six regime
facts hold at all seven points (R4.1/R4.2: 14 / 14 true). Γ(0, 0, 0) = −0.20528201397211823 equals C4's committed
`Gamma_at_A0_zero` (R4.3) and equals the intercept G0 exactly (R4.3b). P̄0, P̄1, P̄2 > 0 and ρ·x_hi > 0 (R4.4).

Coefficients for cell 308 (floats for reading; exact rationals in the JSON `coefficients_exact`). Here ρ is the cell
half-width and D.lo is the K5-B **D-interval** lower end (not the operator constant D_lo of Lemma Dv′).

| coefficient | float | exact size |
|---|---|---|
| ρ | 0.05074855 | 1014971/20000000 |
| x_hi | 1.9839101 | 19839101/10000000 |
| e0 | 1.93316155 | 38663231/20000000 |
| R.hi (m = 5) | −0.15550331135526302 | 157 chars |
| D.lo (m = 5) | 0.04624127760008984 | 156 chars |
| g_hi = R.hi − e0·D.lo | −0.24489517123463297 | 173 chars |
| ρ·x_hi | 0.100680560905355 | 30 chars |
| C_lo | −0.3934538793417449 | 36 chars (dyadic) |
| C_hi | 0.14388513336335515 | 34 chars |
| P̄0 | 0.00020875968377211568 | 849 chars |
| P̄1 | 0.0109274358945025 | 835 chars |
| P̄2 | 0.4660199414754093 | 821 chars |
| R2 interval | [−5.296076774839419, 5.0465080288610284] | 155 / 155 chars |
| M_R2 | 5.296076774839419 | 154 chars |
| G0 = g_hi + ρ·x_hi·\|C_lo\| | −0.20528201397211823 | 185 chars |
| A0* (critical, A1 = A2 = 0) | 4.375228833135616 | 850 chars |
| s* at A0 = 4.311 | 18.24959815514518 | 1543 chars |

Consistency with committed prose: g_hi = −0.244895 is committed at `C5_BLOCKER_DECOMPOSITION.md:31`;
`REVIEW_C8_PREPUBLICATION.md:175` writes −0.244895 + 0.0507486·1.9839101·5.296077 = +0.288317 (the saturation value).

**Scope of the affine form.** Along the segment A1 = A2 = 0, 0 ≤ A0 ≤ A0*, the regime holds throughout (it holds at
both ends, and each regime inequality is monotone in the enclosure width: lo decreases, |lo| − |hi| ≥ |C_lo| − C_hi > 0,
and |lo| ≤ |lo(A0*)| ≤ M_R2). Beyond the regime, M saturates at M_R2 and Γ at g_hi + ρ·x_hi·M_R2 (+0.2883168…,
committed as B2/B4/C4.4/C5.7 in the inventory).

## Discrepancies

None in R1–R4: every committed value reproduces exactly (exact-string equality where the commit is exact, float
equality where it is a float, digit equality where it is rounded prose). Related committed-record discrepancies found
while inventorying (not reproduction failures) are listed in `HISTORY_308_INVENTORY.md` §4 (D1–D8); the only one
touching these numbers is D1 (C5 adjudicator's "misses by 0.003" vs committed "closes").
