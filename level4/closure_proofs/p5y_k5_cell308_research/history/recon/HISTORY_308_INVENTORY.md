# Cell 308 — inventory of every committed Γ-type evaluation and proxy exposure (Stream A, Task 1)

Sanctioned location (`history/`). Read-only inventory of committed files, 2026-09-28. Nothing here was computed,
except that rows marked **[R]** were independently reproduced by the pre-registered HISTORICAL_RECONSTRUCTION
(`C3_KNOCKOUT_RECONSTRUCTION.md`). `LP/` = `level4/closure_proofs/`. Γ = the frozen K5-B **direct** clause
Γ = hi(R − e0·D) + ρ·x_hi·M (with M from the TC-T/K5-B intersection, capped at M_R2) unless the row says C5-T.
Commit = the commit that added the file (`add`) and, where different, the last commit that touched it (`last`).
Status: COMPLETE (Stream A, 2026-09-28).

## 0. Method

1. `git for-each-ref refs/heads refs/remotes refs/tags` in `/Users/suzhe/ReBaseGuard-c308`: 130 refs (§1).
2. Every ref was tested with `git merge-base --is-ancestor <ref> HEAD`. All K5-tail refs (m5-tail-closure 76c37de1,
   operator-registry 5289b6ce, c2 ae4cbc2c, c3 019ecce0, c4 e12a09e8, c5 69bff424, c6 f494416f, c7 df4ec179,
   c8 63a3f825, c9 fd3cb2d4, c10 ec969db1, c11 440bcd91, c11r 7375b9cd, c11rd 8b9fc0bb, overnight 7f45e048,
   cell-307 b73b9449, and every K5 namespace they carry) are ancestors of the research branch; so the HEAD tree
   contains every committed K5-tail file except files later deleted.
3. Non-ancestor refs (p4*, p5x, K1/K2/K4 lines, codex/main, 6 tags): `git diff --name-only $(merge-base) <ref> --
   'level4/closure_proofs/p5y_k5_*'` is empty for all but `p5y-k5-order3-producer-design` (49e0c3d8), whose 10
   extra files are `p5y_k5_cusum_order3_producer_design/*` and `p5y_k5b_independent_review_packet/*` with **no**
   cell-308 token (`git grep`).
4. Deleted files: `git log --all --diff-filter=D` under the tail namespaces lists only C11R's `c11r_screen.py`,
   `C11R_SCREEN.json`, `C11R_N9_TABLE.json` (deleted at 9801276c; no 308 token at 9801276c^) and 12 overnight
   validation-drift files (deleted at 47933904; validation drifts, not 308).
5. Every text/JSON file of 27 K5 namespaces was scanned for a free-standing token `308` (not inside a longer
   number); every JSON file was walked for keys `"308"` / `cell == 308`. All commit messages (`git log --all`) were
   scanned for `308`.
6. The research branch moved during this work (b6ab352e → 5dd80cb9 → bfa9ad3c: this campaign's own Theorem-MB and
   assembly commits, after 33185113). They belong to this campaign and are not inventoried here.

## 1. Refs scanned

130 refs: 50 `refs/heads`, 38 `refs/remotes`, 42 `refs/tags` (counted when this file was written, with the
branch at 33185113; full list reproducible with the command in §0.1).
Tail-relevant tips: see §0.2. No `refs/c12r2/*`, `refs/c11rd/*` or `refs/p5y-k5-cell307-rlr-r1/*` object was read.

## 2. Inventory table

Kinds: **EVAL** = certified evaluation of the clause under a committed certified supply; **EVAL-C5T** = the same
under the C5-T clause; **RECON** = an independent re-derivation of a committed value; **INV** = inversion
(critical constant, requirement, factor, ceiling, margin); **PROXY** = diagnostic / oracle / what-if / sensitivity /
forecast with assumed (uncertified) inputs; **EXPOSURE** = a committed juxtaposition or incident touching 308.

### 2a. Before the tail campaigns (adopted K1 state, no atom-constant supply)

| # | campaign | commit | file:line | supply / clause | committed value (308) | kind |
|---|---|---|---|---|---|---|
| A1 | remaining-cell closure, phase a | d91bc7de | `LP/p5y_k5_remaining_cell_closure/phase_a/OPEN_CELL_AUDIT.md:94` | adopted K1 state, M = M_R2 (no TC-T) | Γ = +0.288 | EVAL (baseline) |
| A2 | Campaign B (m5-tail-closure) phase a | 7ee92476 | `LP/p5y_k5_m5_tail_closure/phase_a/TAIL_BLOCKER_AUDIT.md:17` | adopted state, direct clause | Γ = +0.288, M_R2 5.296, M needed 2.432, reduction 2.18× | EVAL + INV |

### 2b. Campaign B — theorem TC-T forecast r2 (ref p5y-k5-m5-tail-closure @ 76c37de1)

| # | commit | file:line | supply / clause | committed value (308, m = 5) | kind |
|---|---|---|---|---|---|
| B1 | ae153a69 / last 5ed8f059 | `LP/p5y_k5_m5_tail_closure/evidence/forecast_r2/TAIL_FORECAST_R2.json:4639` (CONSERVATIVE), `:5295` (NOMINAL) | **TCT0**: Lemma G (A0 = C_upper = 6.174137363908812, A1 = 30.393446012323317, A2 = 336.052306022857), Ĝ := 0, direct clause | Γ = +0.15834296474510035 (exact in `Gamma_exact`), pass false | EVAL (first certified TC-T evaluation) |
| B2 | ae153a69 | same file `:1005` / `:1663` | route T2_AUDIT, CONSERVATIVE / NOMINAL: **assumed** order-3 inputs (sG = 10, sH = 5, sD = 2, sF = 1, δG = 1/1000; ×4 conservative), Lemma G A | Γ = +0.2883168090540232 (saturated) / +0.005449764744236014 | PROXY (forecast) |
| B3 | ae153a69 | same file `:2325` / `:2984` | route T2_AUDIT_MEAS: same assumed order-3 inputs on measured suprema | Γ = +0.22353135655831818 / **−0.02864772215949453 (pass true, NOMINAL)** | PROXY (forecast) |
| B4 | ae153a69 | same file `:3644` / `:4298` | route T2_EVIDENCE | Γ = +0.2883168090540232 (both) | PROXY (forecast) |
| B5 | ae153a69 | same file `:71` | Lemma G, T2 | `critical_sup_G_over_sup_H_ratio` = 19.195056304643465 | INV |
| B6 | ae153a69 | `.../forecast_r2/ATOM_CONSTANT_REQUIREMENT.json:24` (also `TAIL_FORECAST_R2.json` `atom_constant_requirement`) | Lemma G, TCT0 | A0-only reduction 2.205574719994057; uniform 1.7713435857400779 | INV |
| B7 | ae153a69 / b920c757 | `LP/p5y_k5_m5_tail_closure/phase_c/EXECUTION_DECISION.md:112` | TCT0 | adopted M 5.2961, mag 4.005124, M needed 2.4324, Γ +0.288317 → +0.158343, margin 0.607× | EVAL (prose table of B1) |
| B8 | ae153a69 | same file `:171`, `:175–176` | Lemma G | A0-alone 2.206×; renewal heuristic "1.7× against 2.46×" | INV + PROXY (heuristic) |
| B9 | 46655b31 | `LP/p5y_k5_m5_tail_closure/review/REVIEW_R1.md:47`, `:137` | T2_AUDIT_MEAS r1 | "cell 308 misses by 0.004 out of 2.432" (r1 state; r2 then passes NOMINAL, B3) | RECON (of a PROXY) |
| B10 | — | `LP/p5y_k5_m5_tail_closure/review/REVIEW_R2.md:64` | all routes | "reproduced all 40 per-cell pass flags … and all 40 Γ floats with delta 0.0" | RECON |

### 2c. Campaign C1 — tail operator registry (ref p5y-k5-tail-operator-registry @ 5289b6ce)

| # | commit | file:line | supply / clause | committed value (308) | kind |
|---|---|---|---|---|---|
| C1.1 | 4ccee386 / last 5289b6ce | `LP/p5y_k5_tail_operator_registry/evidence/forecast_r1/C1_FORECAST.json:476` | **S_C1** = Lemma Dv′ from REGISTRY_C1 (A = 5.590460453801663, 31.631571724871883, 455.61048487373813), direct | Γ = +0.13619454282611712, M 3.7851369781202786, pass false | EVAL |
| C1.2 | 4ccee386 | same file `:818` | DEGRADED (S_C1 × 1.25) | Γ = +0.22156368202567597 | PROXY (degradation) |
| C1.3 | 4ccee386 | `.../forecast_r1/C1_DIAGNOSTIC_MIN.json:53` | componentwise min(G, C1) = (5.590460453801663, 30.393446012323317, 336.052306022857) | Γ = +0.13095734077307422, margin 0.6515725275493467 | EVAL (diagnostic combination) |
| C1.4 | 4ccee386 | `C1_FORECAST.json:146` (`material_improvement.per_cell_uniform_reduction_still_needed`) | S_C1 | 1.663450928753142 | INV |
| C1.5 | — | `LP/p5y_k5_tail_operator_registry/theorem/C1_OPERATOR_EXTENSION.md:36`, `:56`, `:72`; `phase_c/C1_EXECUTION_DECISION.md:37` | S_C1 | operator row (τ 4.633777, C_T 5.008961, Ā 7.217875, …); Γ +0.136195, 0.643× | EVAL (prose) |

### 2d. Campaign C2 (ref p5y-k5-tail-c2 @ ae4cbc2c)

| # | commit | file:line | supply / clause | committed value (308) | kind |
|---|---|---|---|---|---|
| C2.1 | e71378a0 / last 92c5d199 | `LP/p5y_k5_tail_c2_closure/evidence/phase_d1/C2_D1_BLOCKER.json:569` | S_C1, direct | Γ = +0.13619454282611712; M needed 2.432397764101128; requirement 1.663450928753142 | EVAL + INV |
| C2.2 | e71378a0 | same file `:598` (`order3_attribution`) | S_C1 with a perfect order-3 surrogate (f_G → 0) | Γ = −0.11866602542315288, closes | PROXY (oracle) |
| C2.3 | e71378a0 / 92c5d199 | same file (`sensitivity_10pct_improvement`, 9 leaves; C_T leaves corrected at 55c4cf00, `ERRATUM_C2.md:46`) | 10 % improvement of each of A0, A1, A2, A_all, τ, C_T, D_lo, D1, D2 | magnitudes 3.455–3.782 | PROXY (sensitivity sweep) |
| C2.4 | e71378a0 | `LP/p5y_k5_tail_c2_closure/phase_d/D1_BLOCKER_DIAGNOSIS.md:16` | S_C1 | per-cell radius-share decomposition (**not reproduced here**, H3 rule) | PROXY (decomposition) |
| C2.5 | e71378a0 | same file `:70`, `:76`, `:119` | S_C1 | C_T-sensitivity +1.1502 %; admissible C_T cut 7.490 %; perfect-order-3 mag 1.2538, Γ −0.118666 | PROXY |
| C2.6 | 5a94568a | `LP/p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json:111–112` | **S_I1** (= D4 componentwise min over {G, C1, C2}; provenance C2 on all three), direct | Γ = +0.10270008356594545 (exact l.112), M 3.4524564789357517, pass false **[R] R1** | EVAL |
| C2.7 | 5a94568a | same file (`required_uniform_atom_constant_reduction`) | S_I1 | 1.5002877825423833; gap fall 0.24593099374719365 | INV |
| C2.8 | 12585997 | `LP/p5y_k5_tail_c2_closure/evidence/phase_d5/C2_CRITICAL_RATIOS.json:55` (C1), `:127` (C2), `:199` (D4), `:271` (G), `:343` (min_G_C1), `:415` (operator_mixed; Γ at `:421`) | six supplies, direct | Γ = +0.13619454282611712 / +0.10270008356594545 / +0.10270008356594545 / +0.15834296474510035 / +0.13095734077307422 / **+0.09456414496566364**; requirements 1.663450928753142 / 1.5002877825423833 / 1.5002877825423833 / 1.7713435857396018 / 1.6379386982770991 / 1.4606547993946881 | EVAL + INV (first appearance of the operator-mixed supply, before C3) |
| C2.9 | 12585997 | same blocks | six supplies | `critical_sG_over_sH` 20.936 / 23.260 / 23.260 / 19.195 / 21.266 / 23.899; `Gamma_perfect_order3` −0.1187 / −0.1267 / −0.1267 / −0.1127 / −0.1200 / −0.1287 | INV + PROXY (oracle) |
| C2.10 | 5a94568a | `.../phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json:39–40` | S_I1; S_I1 × 1.25 | Γ +0.10270008356594545; Γ_degraded_125pct +0.17969560795046136; perfect-order-3 −0.12665519383926 | EVAL + PROXY |
| C2.11 | 12585997 / 2b045564 | `LP/p5y_k5_tail_c2_closure/phase_d/D_PRIME_OPPORTUNITY.md:40` | D′ = operator-mixed | requirement 1.46065480, gap fall 30.57 % | INV (forecast of C3) |
| C2.12 | 5a94568a / 8aee1fc5 | `LP/p5y_k5_tail_c2_closure/phase_r/R_STAGE_DESIGN.md:37` | G / C1 / C2 | critical s_G/s_H 19.19506 / 20.93621 / 23.26035 | INV |
| C2.13 | 5a94568a | `LP/p5y_k5_tail_c2_closure/phase_d/D_STAGE_DECISION.md:17`, `README.md:76`, `phase_d/MEASURE_CHANGE_SELF_AUDIT.md:17` | S_I1 | M 3.452456, M needed 2.432398, Γ +0.102700, 0.705×, 1.500288, gap fall 24.59 % | EVAL (prose) |
| C2.14 | e644bcb5 | `LP/p5y_k5_tail_c2_closure/evidence/execution/C2_EXECUTION.json:39`, `evidence/seal/C2_SEAL.json:63` | S_I1 (exactly-once execution and seal) | Γ = +0.10270008356594545, pass false | EVAL (sealed) |
| C2.15 | ae4cbc2c | `LP/p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md:49` | S_I1 | Γ +0.10270008356594545, mag 3.4524564789357517, 1.5002877825423833, gap fall 0.24593099374719365 | RECON |
| C2.16 | — | `LP/p5y_k5_tail_c2_closure/evidence/prefreeze/C2_MUTATIONS.json:37` | S_I1 (baseline of the mutation suite) | Γ exact (same value) | RECON |
| C2.17 | — | `review/REVIEW_C2_PREFREEZE.md:28`, `:119`, `:137`, `:292`; `_R2.md:149`, `:192`; `_R3.md:66`, `:217`; `_R4.md:131`; `_R5.md:74`; `_R7.md:85` | various | reviewers' reproductions (C1-measure fall 9.809 %, critical ratios, mixed requirement 1.46065480, C_T sensitivities, D_lo/τ table, Γ +0.102700) | RECON |

### 2e. Campaign C3 (ref p5y-k5-tail-c3 @ 019ecce0; REJECTED campaign)

| # | commit | file:line | supply / clause | committed value (308) | kind |
|---|---|---|---|---|---|
| C3.1 | 24c038ec | `LP/p5y_k5_tail_c3_closure/phase_c1/C3_BLOCKER_ANALYSIS.md:14`, `:74`; `evidence/phase_c1/C3_BLOCKER.json` | G / C1 / C2 / D4 / mixed | Γ +0.158342965 / +0.136194543 / +0.102700084 / +0.102700084 / +0.094564145; 1.500288 / 1.460655 (7.92 %) / 1.663451 (30.57 %) | EVAL + INV |
| C3.2 | — | `LP/p5y_k5_tail_c3_closure/evidence/phase_b0/C3_B0_AUDIT.json` (`prior_evidence_reproduced_from_committed_C2`) | G, C1, C2, mixed | Γ +0.15834296474510035, +0.13619454282611712, +0.10270008356594545, +0.09456414496566364 | RECON |
| C3.3 | d41604c2 | `LP/p5y_k5_tail_c3_closure/evidence/forecast/C3_FORECAST.json:97` (block) | **C3 operator-mixed** (operator tuple exact; A = 5.218548598870686, 22.79374449569498, 230.3658154880664) | Γ = +0.09456414496566364, magnitude 3.3716470503119877, requirement 1.4606547993946881, gap fall vs r5 0.07922036981652168, floor F1/F2 false **[R] R2.1–R2.2** | EVAL |
| C3.4 | e815a217 | `LP/p5y_k5_tail_c3_closure/evidence/execution/C3_EXECUTION.json:45` | mixed (exactly-once execution) | Γ = +0.09456414496566364 **[R]** | EVAL (sealed) |
| C3.5 | 019ecce0 | `LP/p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md:192` | mixed | +0.094564144965664, 1.460654799394688, 7.9220 % | RECON |
| C3.6 | 019ecce0 | same file `:350` (§K) | mixed; **knockout A1 = A2 = 0** | Γ mixed +0.094564; Γ(A1 = A2 = 0) +0.039568; A0 5.2185; critical A0 4.3752; ×1.1927 (16.2 %) **[R] R2** | EVAL + INV (knockout) |
| C3.7 | 019ecce0 | same file `:386–388` | — | "a certified lower bound on E_a[τ] at cells 308 and 309 exceeding 4.3752 and 3.2142 …" | INV (target statement) |
| C3.8 | — | `LP/p5y_k5_tail_c3_closure/OPEN_NOTES_DISPOSITION_C3.md:20–23` (C3-N4) | knockout | restates 4.3752 vs 5.2185 | RECON (prose) |

### 2f. Campaign C4 (ref p5y-k5-tail-c4 @ e12a09e8)

| # | commit | file:line | supply / clause | committed value (308) | kind |
|---|---|---|---|---|---|
| C4.1 | c9b06abf / last 5c69be5c | `LP/p5y_k5_tail_c4_exhaustion/evidence/phase0/C4_PHASE0_AUDIT.json` (`knockout.308`) | mixed; knockout | Γ mixed +0.09456414496566364; Γ(A1 = A2 = 0) +0.039567845828196446; A0 factor 1.19274872192929 | RECON |
| C4.2 | c9b06abf | `.../evidence/phase1/C4_THRESHOLDS.json:34–52` | mixed A0, A1 = A2 = 0 | Γ +0.039567845828196446 (l.37); bracket `closes_below_exact` / `open_at_or_above_exact` (l.44, 46), 220 steps; 4.375228833136 (l.47); factor 1.19274872192929 (l.40); 16.16004430652551 % (l.41); Γ(0,0,0) −0.20528201397211823 (l.51); 21-point A0 ladder | EVAL + INV **[R] R2.3–R2.5, R4.3** |
| C4.3 | c9b06abf | `LP/p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md:76` | same | 5.218548599 / +0.039567846 / 4.375228833136 / ×1.19275 (16.16 %) **[R] R2.4e** | EVAL + INV (prose) |
| C4.4 | 5c69be5c | `.../evidence/certificate/C4_CERTIFICATE.json:61–71` | A0 = certified floor 3.512733596022926, A1 = A2 = 0 | Γ_at_bound −0.04046754262884166; Γ_at_certified_A0 +0.039567845828196446; critical A0 4.375228833135616 (reported only); slack −19.713145757785686 %; ladder top (100000 × A0) Γ +0.2883168090540232 | EVAL (knockout at floor) + INV |
| C4.5 | c9b06abf | `.../evidence/phase3/C4_ROUTES.json` (`route_results.308`, `R4_detail.308`) | route L floor; route R4 floor 1.051130027512555 | Γ at bound −0.04046754262884166 / −0.15596388748690246 | EVAL (knockouts at floors) |
| C4.6 | c9b06abf | `C4_ROUTES.json` (`DIAGNOSTIC_true_E_a_tau_at_e0.308`); `phase_3/C4_CANDIDATE_ROUTES.md:81–92` | — | float diagnostics of E_a[τ] at the 308 midpoint 4.1743003050844845 / 4.17430081758821 | PROXY (diagnostic Λ) |
| C4.7 | c9b06abf | `.../evidence/phase3/C4_BOUND_PHASE3.json` | route L | certified lower bound 3.512733596022926 (at e_lo); at e0 3.4020702808704995 | EVAL (certified Λ floor) |
| C4.8 | — | `.../evidence/mutations/C4_MUTATIONS.json` (`cross_check.per_cell.308`) | route L | independent lower bound 3.5127332118947487 | RECON |
| C4.9 | 5c69be5c | `LP/p5y_k5_tail_c4_exhaustion/review/REVIEW_C4_PRERESULT.md:191`, `:455`, `:461` | — | uncertified MC E_a[τ](e_lo) 4.31108 ± 0.00102 | PROXY (MC) |
| C4.10 | e12a09e8 | `.../evidence/adjudication/C4_ADJUDICATION.md:80–82` | — | uncertified 2e6-path MC: 4.30910 ± 0.00102 (e_lo), 4.17398 ± 0.00097 (midpoint), 4.04731 ± 0.00092 (e_hi) | PROXY (MC) |
| C4.11 | e12a09e8 | same file `:186–188`, `:265`, `:534–537` | mixed (A1, A2) scaled uniformly; A0 = 4.311 | 18.2× reduction of (A1, A2); impossible at A0 = 4.375229 **[R] R3** | INV (knockout-type) |
| C4.12 | 5c69be5c / e12a09e8 | `LP/p5y_k5_tail_c4_exhaustion/OPEN_NOTES_DISPOSITION_C4.md:52–53`; `phase_1/C4_TARGET_RECONSTRUCTION.md:119–121` | same | 18.2496×; Γ = +0.000000008 at (4.375229, 0, 0) **[R] R3** | INV + EVAL (knockout) |

### 2g. Campaign C5 (ref p5y-k5-tail-c5 @ 69bff424)

| # | commit | file:line | supply / clause | committed value (308) | kind |
|---|---|---|---|---|---|
| C5.1 | 27a12bef | `LP/p5y_k5_tail_c5_exhaustion/evidence/phase1/C5_DECOMPOSITION.json:129–131` | mixed; **C5-T** and frozen | Γ_C5T +0.09022244922018692; Γ_frozen +0.09456414496566364; M needed 2.432397764101128; factor 1.3861413211576237; radius sum S 2.9781931709702425 | EVAL-C5T + EVAL + INV |
| C5.2 | 27a12bef | `LP/p5y_k5_tail_c5_exhaustion/phase_1/C5_BLOCKER_DECOMPOSITION.md:31` | mixed | g_hi −0.244895; M 3.371647; M needed 2.432398; 1.386; Γ +0.094564; S 2.978193; 31.54 % | EVAL + INV (prose) |
| C5.3 | 27a12bef | `.../evidence/phase2/C5_SENSITIVITY.json:12–24` | A0 = C4 floor 3.512733596022926, A1 = A2 = 0 (CERTIFIED); A0 = 4.311, A1 = A2 = 0 (DIAGNOSTIC) | Γ −0.04046754262884166 (closes); **Γ −0.0030135621984619903 (closes)** | EVAL (knockout) + PROXY |
| C5.4 | 27a12bef | same file, `knockouts[0..11].cells.308` at `:72`, `:90`, `:108`, `:126`, `:144`, `:162`, `:180`, `:198`, `:216`, `:234`, `:252`, `:270` | mixed with 12 knobs (baseline; f_G→0; env4→0; both; σ3→0; σ4→0; both; sup F/D/H halved; →0; A1 = A2 = 0; ρ halved; all) | Γ +0.09456414496566364, −0.12867361039956238, +0.019907692150553564, −0.20333006321467245, +0.007722269290393314, +0.027306807435956794, −0.059535068239313524, +0.022666647477984164, −0.0492308500096953, +0.039567845828196446, −0.08664698724276013, −0.20488625316897732 | PROXY (oracle knockouts; two CERTIFIED rows) |
| C5.5 | — | `.../evidence/ledger/C5_ROUTE_LEDGER.json` (`kill_gate_backing`) | same knobs | same Γ values | PROXY |
| C5.6 | 8b2be7ab | `.../evidence/forecast/C5_FORECAST.json:117–118`, `:439–443` | mixed, C5-T | Γ_C5T +0.09022244922018692; M_needed_C5T 2.463911269745421; factor 1.3684125283701294; C4 test Γ at floor −0.04046754262884166 (frozen) / −0.04308217867804632 (C5-T) | EVAL-C5T + INV |
| C5.7 | 8b2be7ab | same file (`no_regression_sweep.rows[15]`) | adopted-state enclosure, m = 5 | Γ_frozen +0.2883168090540232, Γ_C5T +0.2814970104043067 | EVAL + EVAL-C5T (saturation) |
| C5.8 | — | `.../evidence/b0/C5_B0_AUDIT.json:38–39` | C4 reproduction | Γ at C4 floor −0.04046754262884166; knockout +0.039567845828196446 | RECON |
| C5.9 | 69bff424 | `.../evidence/adjudication/C5_ADJUDICATION.md:151`, `:254`, `:619` | mixed; oracles | +0.094564145 / +0.090222449; "needs ~31.54 %"; "oracle-perfect atom-constant supply misses by 0.003" (see §4 D1) | RECON + PROXY |
| C5.10 | — | `LP/p5y_k5_tail_c5_exhaustion/phase_3/C5_ROUTE_SEARCH.md:26–31`, `ERRATUM_C5_GATE.md:21`, `review/REVIEW_C5_PREFORECAST_R2.md:37`, `:178`; `_R3.md:144` | knockout table; gap falls 4.591 % / 4.826 % | as C5.4 | PROXY / RECON |

### 2h. Campaigns C6, C8 (ref p5y-k5-tail-c6 @ f494416f; p5y-k5-tail-c8-operator-feasibility @ 63a3f825)

| # | commit | file:line | supply / clause | committed value (308) | kind |
|---|---|---|---|---|---|
| C6.1 | f494416f | `LP/p5y_k5_tail_c6_evidence_recovery/evidence/adjudication/C6_ADJUDICATION.md:293`, `:615`; `evidence/leverage/C6_CLASSIFICATION.json:58`, `:213`; `review/REVIEW_C6_FORENSIC.md:460–461` | diagnostic Λ with A1 = A2 = 0; sup F/D/H → 0 | "308 barely closes (−0.0030)"; −0.00301356; −0.049231 | RECON of C5 PROXY rows |
| C8.1 | d58176ae / last 63a3f825 | `LP/p5y_k5_tail_c8_operator_feasibility/evidence/phase4/C8_ROUTES.json:109` (`phase1_dag`) | mixed (C8's own chain) | Γ_now **+0.09456414496566366**; M 3.3716470503119877; M budget 2.432397764101128; Λ floor 3.512733596022926 | RECON (see §4 D3) |
| C8.2 | d58176ae | same file `:206` (`phase4_minimum_information_inversion`, frozen clause) | mixed | A0 ceiling at A1 = A2 = 0 **4.375228833135616**; A1 ceiling at A0 = floor 16.190846990321823; max admissible A0 (others fixed) 3.203078438436744; A0 factor 1.6292290991842175; uniform 1.460654799394688 | INV |
| C8.3 | d58176ae | same file `:260`, `:293` (R1, R2), `:331` (R3), `:366` (R4) | oracles | R1/R2 Γ unchanged +0.09456414496566366; R3 Γ(0,0,0) −0.20528201397211823, Γ(floor,0,0) −0.04046754262884166; R4 perfect order-3 −0.12867361039956238, critical s_G/s_H 23.899214127922175 | PROXY (oracles) + RECON |
| C8.4 | ad9e7745 / last 63a3f825 | `.../evidence/phase9/C8_DECISION.json:123–142` (`phase4_inversion_C5T["308"]`; section starts l.82) | mixed, **C5-T** | A0 ceiling at A1 = A2 = 0 **4.442851487961334**; A1 ceiling at perfect A0 17.632791191529485; max admissible A0 3.270701093262461; A0 factor 1.5955443343999633; M used 3.3716470503119877; M needed 2.463911269745421; M at perfect A0 2.5767032425169996; verdict FEASIBLE | INV (C5-T) |
| C8.5 | 4e3696c0 / 63a3f825 | `.../evidence/phase9/C8_ADOPTION.json:50`, `:127`, `:196` | mixed, C5-T; Lemma G | uniform eff to close 1.4384228261705914, to adopt 1.798028532713239; F1 Γ under Lemma G +0.15834296474510035; zero-leverage structural test | INV + RECON |
| C8.6 | 63a3f825 | `LP/p5y_k5_tail_c8_operator_feasibility/README.md:54`, `:92`; `review/ADJUDICATION_C8.md:84`, `:199`, `:270`, `:347`, `:369`, `:382`, `:446`; `review/HANDOVER_C8_REVIEW.md:17` | C5-T | ×1.438423 / ×1.798029; saturation +0.288316809054; ceiling 4.442851487961 vs floor 3.512733596; eff cut 30.479 % | RECON + INV |
| C8.7 | 4e3696c0 | `review/REVIEW_C8_PREPUBLICATION.md:168`, `:174–175`, `:242–248`, `:296–297`, `:442` | frozen and C5-T | saturation reproduced; "eff at the floor closes 308 under both clauses"; C4 critical 4.375228833135616 "bit-identical to C8's A0_ceiling_with_A1_A2_zero" (the phase-4 frozen-clause field, C8.2) | RECON + INV |
| C8.8 | 4e3696c0, d58176ae, ad9e7745 | commit messages | frozen / C5-T | saturation "+0.288316809 at 308" (4e3696c0); "A0 → floor AND A1 ≤ 17.632791 (1.2927x)" (ad9e7745); "A0 to its floor AND A1 … ≤ 16.190847 (1.4078x)" (d58176ae) | INV (commit text only) |

### 2i. Route audit, closeout freezes, overnight research, cell-307 RLR

| # | commit | file:line | content (308) | kind |
|---|---|---|---|---|
| RA.1 | d52cec02 | `LP/p5y_k5_tail_route_audit/ROUTE_AUDIT.md:129`, `:226–244`, `:315`, `:427`, `:589`, `:639` | restates C3 knockout; Λ between floor 3.512734 and certified A0; "for 308 the projected maximum of 1.137406× is below 1.438423×" (a 307-route projection written next to a 308 threshold); X308 DEFER; new Γ308 = 0 | RECON + EXPOSURE (l.315) |
| RA.2 | 802be11e | `LP/p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md:49`, `:161`, `:262`, `:592` | X308 "certified Λ₃₀₈ > 4.442851 … very high (MC says false)" → REJECT | RECON + PROXY (MC-based) |
| CO.1 | 08e9acd1, dfcd8f79, 9f702acb | `LP/p5y_k5_partial_closeout/protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL.md:243–260`, `:509`; `_r1/.../K5_PARTIAL_CLOSEOUT_PROTOCOL_R1.md:200–214`, `:376`; `_r2/.../K5_PARTIAL_CLOSEOUT_PROTOCOL_R2.md:222–228`, `:444` | quotes C4 Condition 3 (4.311; 18.2×; 4.375229); new Γ308 = 0 | RECON (quotation) |
| CO.2 | — | `review/CLOSEOUT_FREEZE_REVIEW.md:268–270`, `_R1.md:349–352`, `_R2.md:399–401` | verify C3 :350 and C4 :534–537 citations | RECON |
| OV.1 | 7e851139 / last ef6d8846 | `LP/p5y_k5_tail_overnight_research/streams/C_308/A0X/EXCLUSION_308.md:34–46` (F5–F17), `:60`, `:99`, `:137`, `:379–394`, `:444` | committed-fact table (MC, floors, 4.442851 C5-T ceiling, 4.375228833136); Theorem M; consistency table D1–D8 | RECON + EXPOSURE (incident 02, withdrawn) |
| OV.2 | 07ab6b94 / eb55bcab | `.../ledger/INCIDENT_02_C2A_CROSS_CELL_FLOOR.md:15–41`; ledger `ZERO_TARGET_LEDGER.jsonl:155`, `:193` | committed 309 floor re-attributed to 308's right endpoint and placed next to A0*; withdrawn (0d32a2e8), residue re-worded (ef6d8846) | EXPOSURE (PROXY_EXPOSURE, QUARANTINE_RULE_BREACH) |
| OV.3 | 4d64e2b0 | `.../ledger/INCIDENT_03_C2B_BRIEF_SCALE.md:7`, `:15`; ledger `:175` | coordinator's C2b brief used a comparison scale derived from committed 308 figures | EXPOSURE (qualitative) |
| OV.4 | 4403f86f (graph), later moves | ledger `:81`, `:192`; `graph/HISTORICAL_DOMINANCE.md` | incident 01: tail radius shares (incl. 308) co-located with TPT-G over-charge factors | EXPOSURE |
| OV.5 | 9e8ae240 → d3b60795 | `.../streams/C_308/LR/RLR_FREEZE_PROTOCOL_DRAFT.md:30–41` | RLR draft cell set {307, 308, 309} reduced to {307} using the committed C3 knockout (no evaluation) | none (scope decision) |
| OV.6 | — | `.../OVERNIGHT_FINAL_REPORT.md:7`, `:88–99`; `graph/K5_TAIL_DEPENDENCY_GRAPH.md:25–34` | "A1/A2-only route cannot close 308" (C3 knockout); binding-regime closed form (affine Γ) **[R] R4** | RECON (prose) |
| RL.1 | b73b9449 | `LP/p5y_k5_cell307_rlr_r1/FINAL_REPORT.md:13`, `:90`, `:187`, `:228`; `protocol/RLR307_PROTOCOL.md:29`; `audit/INCIDENT_AUDIT_RLR307.md:21–24`, `:77` | 308 untouched; driver refuses 308; guards refuse 308's cover interval; incidents 02/03 re-disclosed | none (0 evaluations) |
## 3. Campaigns checked with no cell-308 evaluation

| campaign | ref / commit | what the committed record shows for 308 |
|---|---|---|
| C7 (Λ₃₀₉, E2) | p5y-k5-tail-c7-e2 @ df4ec179 | no 308 token in any text/JSON file of `LP/p5y_k5_tail_c7_e2_lambda309/` (only `.py` constants). C7's family ceiling at 309's drift was later re-attributed to 308 by the overnight stream (incident 02, OV.2), not by C7 |
| C9 (cell 307, alpha lever) | fd3cb2d4 | `config/CHARTER_C9.json:10,13` "non_targets": 306, 308, 309; `README.md:97`, `STOP_RECORD_C9.md:40` "never evaluated" |
| C10 (governance) | ec969db1 | open-set bookkeeping only (`evidence/phase1/C10_ARCHAEOLOGY.json:165–171`; `review/ADJUDICATION_C10.md:147`, `:323`) |
| C11 (N9 certifier) | 440bcd91 | open-set bookkeeping only (`evidence/b0/C11_B0_N9.json:223–229`) |
| C11R | 7375b9cd | `adjudication/ADJUDICATION_C11R_N9.md:143` "cells 307, 308 and 309 (untouched: not executed, not compared)"; `config/N9R_GATE_C11R.json:174` lists "cell 308" as a refused string; deleted screen/table files carry no 308 token |
| C11RD | 8b9fc0bb | `review/C11RD_ADJUDICATION_REVIEW.md:219` "No changed path concerns 307, 308 or 309" |
| C12 / C12-R1 / C12-R2 (306 only) | on the c11rd lineage (C12-R2 qualification 107a8b36) | **confirmed: nothing computed on 308.** 308 appears only as a negative control that the driver refused: `C12_QUALIFICATION.json:93–100` "C12 REFUSED CELL_OUT_OF_SCOPE: 308"; `C12R1_QUALIFICATION.json:39–46` and `C12R2_QUALIFICATION.json:39–46` "REFUSED CELL_OUT_OF_SCOPE: 308"; status tables `C12_PROTOCOL.md:141`, `C12_CAMPAIGN_STATUS.md:40`, `C12R1_CAMPAIGN_STATUS.md:79` "OPEN (r5)" |
| floor r2 | a15d083b / 3fadb422 | no cell-308 content in `LP/p5y_k5_tail_floor_r2/` (the only `308` substring is inside a sha256, `config/K5_TAIL_ADOPTION_FLOOR_R2.json:111`) |
| closeout freezes (3, all REJECTED) | 08e9acd1, dfcd8f79, 9f702acb | quotation only (CO.1); each protocol records "new Γ evaluations, cell 308: 0" |
| overnight research | 7f45e048 | no Γ308 evaluation; exposures OV.2–OV.4; X308 exclusion stream is theory + draft protocol only |
| cell-307 RLR | b73b9449 | 0 evaluations on 308 (RL.1) |
| Perron deflation, lower-front TC, K5 feasibility | 7cb01e38, 3c1c6b9c, … | no cell-308 row with a Γ value (full-cover consumptions record pass ranges only) |

## 4. Discrepancies and notes

* **D1 (committed prose vs committed evidence, C5).** `C5_ADJUDICATION.md:254` says for 308 "The oracle-perfect
  atom-constant supply **misses** by 0.003" (and `:619` "comes within 0.003 of 308"). The committed C5 evidence at
  the same point (A0 = 4.311, A1 = A2 = 0) is Γ = −0.0030135621984619903, `closes: true`
  (`C5_SENSITIVITY.json:20–24`), and C6 restates it as "308 barely closes (−0.0030)" (`C6_ADJUDICATION.md:615`;
  `C6_CLASSIFICATION.json:213`; `REVIEW_C6_FORENSIC.md:461`). It is also what the reconstruction implies without a
  new evaluation: 4.311 < A0* (R2.4) and Γ(·, 0, 0) is strictly increasing, so Γ(4.311, 0, 0) < 0. The C5
  adjudicator's word "misses" has the wrong sign; the number is right. Not load-bearing (a DIAGNOSTIC point).
* **D2 (label, C4).** `C4_ADJUDICATION.md:186–187` calls 4.311 "the Monte-Carlo value of Λ₃₀₈"; the adjudicator's
  own MC (`:81`) is 4.30910 ± 0.00102. 4.311 is the pre-result reviewer's 4.31108 ± 0.00102
  (`REVIEW_C4_PRERESULT.md:191`) rounded. The 18.2496× factor is exact for A0 = 4.311 exactly (R3), not for either
  MC value.
* **D3 (float-level, C8 reconstruction path).** C8's own chain reports Γ_now = +0.09456414496566366
  (`C8_ROUTES.json` phase1_dag / R1 / R2; `C8_ADOPTION.json`), two ulp above the frozen-consumer value
  +0.09456414496566364 (C3_FORECAST, C3_EXECUTION, C8's own R4 row, and the exact reconstruction R2.2). C8's chain is
  not bit-identical to the frozen consumer. Non-load-bearing (it cross-checks M, not Γ, at 1e-12).
* **D4 (two A0 ceilings; not a discrepancy).** `REVIEW_C8_PREPUBLICATION.md:296–297` calls C4's critical A0
  4.375228833135616 "bit-identical to C8's A0_ceiling_with_A1_A2_zero for 308". That is the phase-4 **frozen-clause**
  field (`C8_ROUTES.json:207`), not the phase-9 **C5-T** field of the same name, 4.442851487961334
  (`C8_DECISION.json:124`). Any citation of "C8's A0 ceiling for 308" must name the clause.
* **D5 (operator-mixed supply predates C3).** The operator-mixed supply and its Γ308 = +0.09456414496566364 were
  first committed by C2 at 12585997 (`C2_CRITICAL_RATIOS.json:415–421`), before C3 (d41604c2) adopted it as its
  mechanism. HISTORY_308.md H1.2 attributes the value to C3 only.
* **D6 (Campaign B proxy that "passes").** Campaign B's T2_AUDIT_MEAS NOMINAL route committed Γ308 = −0.02864772215949453,
  `pass: true` (`TAIL_FORECAST_R2.json:2984`), on **assumed** order-3 inputs (sG = 10, …; `tail_forecast_r2.py:67–69`).
  It is a forecast, not an evaluation: the only committed negative Γ308 produced by a route *forecast* (the other
  negative values are oracle knock-outs, knockouts at floors, or diagnostics). It is not mentioned in HISTORY_308.md H1.
* **D7 (a 307-route factor next to a 308 threshold).** `ROUTE_AUDIT.md:315` "For 308 the projected maximum of
  1.137406× is below 1.438423×" places C9's projected 307 alpha-lever factor beside 308's C5-T close factor — the
  incident-01 shape (route factor × tail threshold), committed before the overnight quarantine existed. Not previously
  listed as an exposure in HISTORY_308.md H4.
* **D8 (saturation value only in a commit message).** As `ADJUDICATION_C8.md:208–209` noted, 308's saturation value
  +0.288316809 is carried by the C8 commit message 4e3696c0; in the tree it appears as Campaign B / C4 / C5 floats
  (B2, B4, C4.4, C5.7).
* **HISTORY_308.md H5** asked for this inventory; rows [R] are reproduced exactly (55/55 comparisons equal).
