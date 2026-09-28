# Cell 308: committed history (HISTORY SECTION — sanctioned location for committed tail figures)

**Rules for this file.**
* Every row is a reading of a committed file, quoted with its source. Nothing here was computed by this campaign,
  except the rows explicitly marked HISTORICAL_RECONSTRUCTION, which reproduce committed values exactly.
* **No route factor, gain ratio, tightness figure or validation-drift value of any new route may ever be written in
  this file** (incident-01 class; quarantine T2). Conversely, the figures below may not be copied into any file outside
  `history/` or `ledger/` (the text co-location scan in `code/c308_quarantine.py` enforces this).
* `LP/` = `level4/closure_proofs/`.

## H0. Object

| id | fact | source |
|---|---|---|
| H0.1 | CUSUM m = 5 cell 308, cover interval [1882413/1000000, 19839101/10000000] (shares its right endpoint with cell 309) | `LP/cells.json` (CUSUM entries); `LP/p5y_k5_tail_overnight_research/streams/C_308/A0X/EXCLUSION_308.md` F5 |
| H0.2 | r5 per-cell verdict: 308 OPEN; m = 5 open set [306, 309]; r5 sha256 e2197051…, git blob f978eeb6… on b73b9449, 7f45e048 and 8b9fc0bb | `LP/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json` (verified 2026-09-28 by this campaign) |
| H0.3 | No r6 on any ref (all refs/heads, refs/remotes, refs/tags scanned for coverage-map r6 paths) | verified 2026-09-28 by this campaign |

## H1. Committed Γ308 values and supplies

| id | fact | source |
|---|---|---|
| H1.1 | C2 D5 forecast, supply S_I1 (provenance C2 for A0, A1, A2), frozen direct clause: Γ = 0.10270008356594545, pass = false; A0 = 5.332021179343055, A1 = 23.91517098849144, A2 = 246.74977924152824; M_after = 3.4524564789357517; required uniform atom-constant reduction 1.5002877825423833 | `LP/p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json` cells["308"] |
| H1.2 | Operator-mixed supply (not admissible under floor r2): Γ = +0.094564; A0 certified 5.2185 (= τ/D_lo); whole-kernel Ā 7.2179. **Correction (stream A D5):** this supply and its Γ₃₀₈ first appear in C2 (`12585997`, `C2_CRITICAL_RATIOS.json`), before C3 adopted it | `LP/p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md` §K (on ref p5y-k5-tail-c3 @ 019ecce0); `history/recon/HISTORY_308_INVENTORY.md` |
| H1.3 | **C3 knockout** (C3 adjudicator, "computed from committed rationals with no scientific address evaluated"): Γ at A1 = A2 = 0 is **+0.039568** (still open); critical A0 at A1 = A2 = 0 is **4.3752**; A0 reduction needed ×1.1927 (16.2 %). "Closure is infeasible by any improvement of A1 and A2 whatsoever." | same, §K table and text |
| H1.4 | C4: frozen-clause critical A0 at 308 = 4.375228833136 | `LP/p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md:76` (ref p5y-k5-tail-c4 @ e12a09e8) |
| H1.5 | C4 adjudicator §4 (**note, stream A D2:** the adjudicator's own MC is 4.30910; 4.311 is the pre-result reviewer's 4.31108 rounded): "at A0 = 4.311 (the Monte-Carlo value of Λ₃₀₈), closing cell 308 still requires an 18.2× reduction of (A1, A2); at A0 = 4.375229 it is impossible at any (A1, A2)." Reproduced as 18.2496× in the C4 open-notes disposition | `C4_ADJUDICATION.md` ~l.186; `OPEN_NOTES_DISPOSITION_C4.md:52` |
| H1.6 | C8 phase 4 (C5-T clause, mixed supply): A0 ceiling at A1 = A2 = 0 = 4.442851487961334; A_now = (5.218548598870686, 22.79374449569498, 230.3658154880664); required A0 factor 1.5955443343999633; M_used 3.3716470503119877; A1 ceiling at perfect A0 17.632791191529485 | `LP/p5y_k5_tail_c8_operator_feasibility/evidence/phase9/C8_DECISION.json` phase4_inversion_C5T["308"] |
| H1.7 | C8 uniform-eff factors (C5-T clause): ×1.438423 to close, ×1.798029 to adopt | `LP/p5y_k5_tail_c8_operator_feasibility/README.md:54`; `review/ADJUDICATION_C8.md:84` |
| H1.8 | **(stream A D6)** Campaign B's T2_AUDIT_MEAS NOMINAL forecast committed a negative Γ₃₀₈ with `pass: true` on ASSUMED order-3 inputs: a proxy, not an evaluation | `history/recon/HISTORY_308_INVENTORY.md` |
| H1.9 | **(stream A R1–R4)** Pre-registered HISTORICAL_RECONSTRUCTION: H1.1, H1.3, H1.4 and H1.5 reproduced exactly (55/55 committed values) from committed inputs through the frozen consumer and an independent re-implementation; Γ is affine in (A0, A1, A2) at all 7 committed points with the binding-regime facts holding | `history/recon/C3_KNOCKOUT_RECONSTRUCTION.md`, `.json`; `history/recon/recon_308.py` |

## H2. Committed facts about Λ₃₀₈ = sup_cell E_a[τ]

| id | fact | source |
|---|---|---|
| H2.1 | Certified lower bound Λ₃₀₈ ≥ 3.512733596 (C4 route L, H/E[(\|z\| − K)⁺] at e_lo) | `LP/p5y_k5_tail_c4_exhaustion/phase_3/C4_CANDIDATE_ROUTES.md:52`; `C8_DECISION.json` Lambda_floor_on_A0 |
| H2.2 | Uncertified 2,000,000-path Monte-Carlo (C4 adjudicator): E_a[τ](1.8824130) = 4.30910 ± 0.00102; at the 308 midpoint 4.17398 ± 0.00097; at 1.9839101 4.04731 ± 0.00092 | `C4_ADJUDICATION.md:80-82` |
| H2.3 | Uncertified MC (C4 pre-result reviewer): 4.31108 ± 0.00102 | `LP/p5y_k5_tail_c4_exhaustion/review/REVIEW_C4_PRERESULT.md:191,455` |
| H2.4 | C4 float diagnostic of E_a[τ] at the 308 midpoint: 4.1743 (a candidate value, not a bound) | `C4_CANDIDATE_ROUTES.md:81-92` |
| H2.5 | No committed certified UPPER bound on Λ₃₀₈ below the committed supplies' A0 (C4-N2) | `OPEN_NOTES_DISPOSITION_C4.md:33-36` |

## H3. Structure of the radius at the tail

The committed per-cell decomposition of the TC-T radius sum (order-3 surrogate, order-4 envelope, midpoint
residual shares) is recorded in `LP/p5y_k5_tail_overnight_research/graph/HISTORICAL_DOMINANCE.md` and in the C5
adjudication. It is **not copied here**. Incident 01 arose from placing those shares next to a route factor; this
campaign does not reproduce them anywhere.

## H4. Incidents and exposures that touch cell 308 (all from the overnight campaign, 7f45e048)

| id | incident | bearing on 308 |
|---|---|---|
| H4.1 | Incident 01 (+ residue): committed tail radius shares (306–309) placed next to TPT-G's generic over-charge factors | TPT's (and any profile transport's) tail use carries a disclosed MEDIUM–HIGH result-chasing liability |
| H4.2 | Incident 02: stream C2a re-attributed a committed 309 floor to 308 | bears on the 308 EXCLUSION question only |
| H4.3 | Incident 03: the coordinator's C2b brief used a comparison scale derived from cell-308 figures | bears on the 308 exclusion question; C2b's certifier code is unaffected, but its use for 308 must disclose it |
| H4.3b | **(stream A D7)** `p5y_k5_tail_route_audit/ROUTE_AUDIT.md:315` placed C9's projected factor for a 307 route next to 308's C5-T closing factor — the incident-01 shape, committed before the overnight quarantine existed | `history/recon/HISTORY_308_INVENTORY.md` §4 |
| H4.4 | The cell-307 RLR campaign (b73b9449) evaluated nothing on 308 and inferred nothing about it | `LP/p5y_k5_cell307_rlr_r1/FINAL_REPORT.md` §Q |

## H5. Inventory of every historical evaluation touching Γ308

Complete inventory (about 90 classified rows over all 130 local refs): `history/recon/HISTORY_308_INVENTORY.md`.
Pruning theorems derived from committed values only: `history/recon/PRUNING_308.md` (P308-D direct clause, P308-T
C5-T clause). Committed-record discrepancies D1–D8 (none load-bearing) are listed in the inventory §4.
