# Graph C — K1 inputs, residuals, order-3, sup-norm and cover of the K5 Γ at CUSUM m = 5, cells 306–309

Read-only reconstruction. Worktree `/Users/suzhe/ReBaseGuard-k5ov` at `6735d945` (tree clean). Paths are relative to
`level4/closure_proofs/` unless stated. **Quarantine kept:** nothing in the repository was executed. `python3 -c` was
used only to list JSON keys. **No Γ, margin, radius, magnitude, factor or other number for cells 305–309 was computed
here.** Every number below is quoted from a committed file, with file:line or a JSON path. Where I read something
rather than quote it, the text says "(reading)".

Notation: `a = x0 = (0,0)` is the atom and evaluation point. `R_e = (I − K_e)⁻¹`. `K_i = ∂_e^i K_e`. `ρ` is the cell
half-width. `e0` is the cell midpoint. `x_lo`/`x_hi` are the left and right cell endpoints.

**Short file names used below**, all under `level4/closure_proofs/`:

| short name | full path |
|---|---|
| `CHECKPOINT.md` (§1), `ERROR_ALGEBRA.md`, `geometry.py`, `build_spec.py`, `cells.json` | `p5y_k1_cover_ledger_successor/{CHECKPOINT.md, ERROR_ALGEBRA.md, code/geometry.py, code/build_spec.py, config/cells.json}` |
| `THEOREM_TC.md`, `tc_rule.py`, `tc_producer.py`, `TC_SUCCESSOR_SPEC.md` | `p5y_k5_lower_front_order3/{theorem/, code/, code/, ./}` |
| `THEOREM_TCT.md`, `tct_rule.py`, `tct_inputs.py`, `tct_adopted_inputs.py` | `p5y_k5_m5_tail_closure/{theorem/, code/}` |
| `MEASUREMENT_NOTE.md`, `TCT_INPUTS_30x.json`, `ADOPTED_TAIL_INPUTS.json` | `p5y_k5_m5_tail_closure/evidence/measurement_r1/` |
| `TAIL_FORECAST_R2.json`, `FORECAST_R2.md` | `p5y_k5_m5_tail_closure/evidence/forecast_r2/` |
| `TAIL_BLOCKER_MAP.json`, `TAIL_BLOCKER_AUDIT.md` | `p5y_k5_m5_tail_closure/phase_a/` |
| `EXECUTION_DECISION.md` | `p5y_k5_m5_tail_closure/phase_c/` |
| `THEOREM_AD.md`, `OPERATOR_AUDIT.md` | `p5y_k5_perron_deflated_resolvent/theorem/` |
| `IMPLEMENTATION_MAP.md` | `p5y_k1_cusum_kernel/` |
| `DESIGN.md` | `p5y_k5_cusum_order3_producer_design/` |
| `K5_GLOBAL_BRIDGE.md` | `p5y_k5_feasibility/` |
| `R_STAGE_DESIGN.md` | `p5y_k5_tail_c2_closure/phase_r/` |
| `OPEN_NOTES_DISPOSITION_C2.md` | `p5y_k5_tail_c2_closure/` |
| `C4_ADJUDICATION.md` | `p5y_k5_tail_c4_exhaustion/evidence/adjudication/` |
| `C4_TARGET_RECONSTRUCTION.md` | `p5y_k5_tail_c4_exhaustion/phase_1/` |
| `C5_ADJUDICATION.md` | `p5y_k5_tail_c5_exhaustion/evidence/adjudication/` |
| `C5_BLOCKER_DECOMPOSITION.md` | `p5y_k5_tail_c5_exhaustion/phase_1/` |
| `C6_ADJUDICATION.md` | `p5y_k5_tail_c6_evidence_recovery/evidence/adjudication/` |
| `ADJUDICATION_C8.md`, `ERRATUM_C8_GATE.md` | `p5y_k5_tail_c8_operator_feasibility/{review/, ./}` |
| `ROUTE_AUDIT_R1.md` | `p5y_k5_tail_route_audit/` |

In §4.1–§4.4, a bare `README.md` / `OPEN_NOTES_DISPOSITION_*.md` / `evidence/…` means that subsection's namespace.

---

## 1. The cover (`cells.json`)

### 1.1 Location and identity

- **File.** `p5y_k1_cover_ledger_successor/config/cells.json`.
  - It is one line (`wc -l` = 1), so every citation into it is `cells.json:1`.
  - sha256 `341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f`, the pin cited at
    `p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md:147` ("cells.json `341eb5e9`") and at
    `p5y_k5_m5_tail_closure/phase_a/TAIL_BLOCKER_AUDIT.md:3-4`.
- **Size.** 642 entries: CUSUM 326, SR 316.
  - Source: `p5y_k1_cover_ledger_successor/CHECKPOINT.md:118`, and `p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md:135`.
- **The `index` field is NOT unique across detectors. Filter on `detector == "CUSUM"` first** (`THEOREM_TCT.md:134-139`).
  - Example: CUSUM 305 is `e0 = 1.661402, ρ = 0.040521, C_upper = 7.732565`. SR 305 is `e0 = 3.965268, ρ = 0.103301,
    C_upper = 3.033162`.
  - Keying on `index` alone "gets a Γ wrong by ≈ 0.41" (`THEOREM_TCT.md:136-138`).
  - The same warning appears at `p5y_k5_m5_tail_closure/evidence/measurement_r1/MEASUREMENT_NOTE.md:45-46`.
  - The frozen loader filters by detector (`p5y_k5_m5_tail_closure/code/tct_inputs.py:69`).

### 1.2 Fields

Each entry has the keys `C_evaluation, C_upper, detector, e0, index, left, nominal_step_half_width, rho, right`.
These come from the key listing and match the emitter at `p5y_k1_cover_ledger_successor/code/geometry.py:27-31`.

**There are no `x_lo` / `x_hi` fields.**
- In theorem C5-T, `x_lo = e0 − ρ` (= `left`) and `x_hi = e0 + ρ` (= `right`) (`p5y_k5_tail_c5_exhaustion/evidence/adjudication/C5_ADJUDICATION.md:25-27`).
- C5's decomposition records `x_hi` as the `right` string, e.g. 309 `"x_hi": "2092283/1000000"`
  (`p5y_k5_tail_c5_exhaustion/evidence/phase1/C5_DECOMPOSITION.json:253`).
- In theorem K5-B, `x_k` is the right endpoint of cell `C_k = [x_{k−1}, x_k]` (`p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md:7`).
- Note that bridge `k = K1 index + 1`.

| field | meaning | source |
|---|---|---|
| `left`, `right` | exact affine `[p, s]` = `p + s·c_SR`. For every CUSUM cell `s = 0/1` | `geometry.py:18-20`; `code/build_spec.py:101` |
| `e0` | exact midpoint `(left+right)/2` | `geometry.py:28`; `build_spec.py:100` ("EXACT_MIDPOINT") |
| `rho` | `(right−left)/2` | `geometry.py:29`; `build_spec.py:100` |
| `C_upper` | `c_num/2^32`, a certified **upper bound on ‖(I−K_e)⁻¹‖ for every e in the cell**, computed at the left endpoint | `geometry.py:30`; `ERROR_ALGEBRA.md:13-14` |
| `C_evaluation` | the left endpoint at which C was evaluated | `geometry.py:30`; `build_spec.py:92` |
| `nominal_step_half_width` | `s = 1/(4·a_up·C_upper)`, "NOT the actual Taylor radius" | `geometry.py:31`; `build_spec.py:97` |

### 1.3 Construction rule

The cover is **not uniform**. It is an adaptive, result-independent, left-to-right walk.
The rule is `direct-left-minorant-integer-floor-v1` (`build_spec.py:90`; `CHECKPOINT.md:71-110`):

1. **Grid.** `Q = 10^7`. Start at `left = 0` (`CHECKPOINT.md:81`).
2. **Evaluate C at the exact left endpoint.** For CUSUM: `drift_monotone_resolvent(cells=100, n_max=250, bits=192)`
   (`build_spec.py:93-94`; `geometry.py:95-98`).
3. **Round and carry.** `C_new = ceil(upper(C)·2^32)/2^32`, then `C_use = min(C_new, C_previous)`.
   - This is justified by M2: "a previous left bound remains valid at later drift".
   - It forces the stored C to be non-increasing, and "is NOT an assumption about monotonicity of two-sided E[τ]"
     (`CHECKPOINT.md:86-90`; `build_spec.py:95`; `geometry.py:103-104`).
4. **Step.** `a_up = ceil(upper(2φ(0))·2^60)/2^60` and `s = 1/(4·a_up·C_use)`. The advance is
   `floor(2·s·Q) = floor(Q/(2·a_up·C_use))`. STOP if the advance is below 1 (`CHECKPOINT.md:91-94`; `build_spec.py:96-98`;
   `geometry.py:44, 107`).
5. **Set the endpoints.** `right = min(left + advance/Q, 11/2)`, `e0` is the midpoint, and `ρ ≤ s ≤ 1/(4·a·C)`
   (`CHECKPOINT.md:95-97`). The CUSUM domain is `[0, 11/2]` (`CHECKPOINT.md:75`; `build_spec.py:102`).
6. **Tile.** Exact shared boundaries, no gaps or overlaps, no adaptive splitting (`CHECKPOINT.md:106-110`; `build_spec.py:104-105`).
7. **The rule is geometry only.** "The s rule is a geometry bound, NOT a proof that B_cover will pass" (`CHECKPOINT.md:128-132`).

Consequences:
- Since `ρ ∝ 1/C_upper`, the tail cells are wide. There `C_upper` is 5.8–7.7 against 1011–1177 on the lower front,
  and ρ is 0.041–0.054 against 2.7e-4 (`p5y_k5_m5_tail_closure/phase_a/TAIL_BLOCKER_AUDIT.md:40`; `MEASUREMENT_NOTE.md:62`).
- K5 uses CUSUM cells 0–309, the cells meeting `(0,2]`. Cell 309 contains `e = 2`
  (`p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md:89, 96-98`; `K5_GLOBAL_BRIDGE.md:7`).

### 1.4 Committed CUSUM entries 300–309, verbatim (`cells.json:1`)

The second component of every affine pair is `"0/1"` and is omitted below. `C_evaluation` equals `left` in every row.

| idx | left | right | e0 | rho | C_upper | nominal_step_half_width |
|---|---|---|---|---|---|---|
| 300 | 1293099/1000000 | 13499249/10000000 | 26430239/20000000 | 568259/20000000 | 47363438991/4294967296 | 1237940039285380274899124224/43569545510609779121072557737 |
| 301 | 13499249/10000000 | 3526537/2500000 | 27605397/20000000 | 606899/20000000 | 44347861689/4294967296 | 1237940039285380274899124224/40795521172444278319067251023 |
| 302 | 3526537/2500000 | 461209/312500 | 7216209/5000000 | 32627/1000000 | 41246054664/4294967296 | 154742504910672534362390528/4742771782676418170229960231 |
| 303 | 461209/312500 | 386461/250000 | 3777141/2500000 | 87469/2500000 | 38463190795/4294967296 | 1237940039285380274899124224/35382222607282795377087511565 |
| 304 | 386461/250000 | 16208813/10000000 | 31667253/20000000 | 750373/20000000 | 35868414006/4294967296 | 618970019642690137449562112/16497645966172007172219287421 |
| 305 | 16208813/10000000 | 680769/400000 | 16614019/10000000 | 202603/5000000 | 33211115065/4294967296 | 1237940039285380274899124224/30550847238047329668071637455 |
| 306 | 680769/400000 | 17885921/10000000 | 17452573/10000000 | 108337/2500000 | 31054358416/4294967296 | 77371252455336267181195264/1785428158212130492576414607 |
| 307 | 17885921/10000000 | 1882413/1000000 | 36710051/20000000 | 938209/20000000 | 28687329103/4294967296 | 1237940039285380274899124224/26389424365247289816594022121 |
| 308 | 1882413/1000000 | 19839101/10000000 | 38663231/20000000 | 1014971/20000000 | 26517718059/4294967296 | 1237940039285380274899124224/24393602922892945805875781613 |
| 309 | 19839101/10000000 | 2092283/1000000 | 40761931/20000000 | 1083729/20000000 | 24835280415/4294967296 | 1237940039285380274899124224/22845931447581574579947274905 |

**Committed decimal renderings for 306–309.**
- From the Campaign-B blocker map (`p5y_k5_m5_tail_closure/phase_a/TAIL_BLOCKER_MAP.json`, m = 5 rows):

  | cell | lines | e_lo | e0 | e_hi | ρ | C_upper |
  |---|---|---|---|---|---|---|
  | 306 | 1980-1994, 2086 | 1.7019225 | 1.7452573 | 1.7885921 | 0.0433348 | 7.230406258255243 |
  | 307 | 2276-2290, 2382 | 1.7885921 | 1.83550255 | 1.882413 | 0.04691045 | 6.6792892997618765 |
  | 308 | 2572-2586, 2678 | 1.882413 | 1.93316155 | 1.9839101 | 0.05074855 | 6.174137363908812 |
  | 309 | 2868-2882, 2974 | 1.9839101 | 2.03809655 | 2.092283 | 0.05418645 | 5.782414324348792 |

- The same `C_upper` values appear as the Lemma-G `A0` in `evidence/forecast_r2/TAIL_FORECAST_R2.json:39,46,53,60`.
- The measured records repeat e0/ρ/left/right exactly: `evidence/measurement_r1/TCT_INPUTS_30{6..9}.json:45,51,172,173`.
- The adopted extract repeats C_upper: `ADOPTED_TAIL_INPUTS.json:109,214,319,424`.

---

## 2. K1 record objects and theorem-TC / TC-T inputs

### 2.1 Where the objects come from

**Theorem TC** (`p5y_k5_lower_front_order3/theorem/THEOREM_TC.md`) is reused **verbatim** at the tail by theorem **TC-T**
(`p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md:3-7`). TC-T changes exactly three premise supplies:
- Lemma G, in place of registry-based A0/A1/A2;
- (P2′), which sets `Ĝ := 0`;
- (P3′), which takes σ3/σ4 from the Aux3 evidence.

Source: `THEOREM_TCT.md:11-15`.

**Where the numbers live.**
- The **sealed K1 records** are the Aux5 CUSUM composite closure, files `k4_records/aux5_CUSUM_{k}_256.json`
  (`p5y_k5_m5_tail_closure/code/tct_adopted_inputs.py:42-46`).
  - They are external, about 90 MB.
  - Only cell 309's copy is in git (`p5y_k5_tail_c6_evidence_recovery/README.md:52-54`).
- The committed **verbatim extract** is `evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json`.
  - Its manifest is `29ad1f9b…`, and each record is sha-checked against the export manifest (`tct_adopted_inputs.py:1-12, 44-46`).
- The committed **replay measurement** is `evidence/measurement_r1/TCT_INPUTS_30{5..9}.json` (`tct_inputs.py:85-109`).

**Standing admissibility caveat.**
- All four records (306–309) are provenance **P3**, with `admissible_for_NEW_scientific_reuse: false`.
- They stand only through `already_adopted_exception`.
- C6 Condition 10 therefore binds: "no P3 object may be adopted as new scientific evidence"
  (`p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md:164, 196-201`; `p5y_k5_tail_c6_evidence_recovery/OPEN_NOTES_DISPOSITION_C6.md:20`).

### 2.2 Object table

In the "kind" column:
- **Pointwise** means a value (or enclosure) at the atom `a`.
- **Norm-only** means a sup-norm over the state space X, or an operator norm, used as a multiplier.

| object | exact definition | defined at | what it bounds | gate | kind |
|---|---|---|---|---|---|
| `R_k` = `m.<m>.R_interval` | outward interval ∋ `R_m(e0)`: the all-m assembly at order 0, at the midpoint | `K5_GLOBAL_BRIDGE.md:9`; `p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md:136-137, 150` | the point value at `a`, at `e0` | sealed record. The extract is manifest-checked (`EXECUTION_DECISION.md:40`) | **pointwise** (e0, a) |
| `D_k` = `m.<m>.D_interval` | outward interval ∋ `R'_m(e0)` | `K5_GLOBAL_BRIDGE.md:9`; `ERROR_ALGEBRA.md:150` | `R'` at `e0` | as above | **pointwise** |
| `H_k` = `m.<m>.R2_interval` | `⊇ R''_m(C_k)`: whole-cell curvature enclosure, `= Σ_{r<m}(1/m)[Ĥ_r(a) ± eps_cell_refined(H:r)] + Σ c·W2` | `K5_GLOBAL_BRIDGE.md:10`; `ERROR_ALGEBRA.md:120-122`; `TAIL_BLOCKER_AUDIT.md:28-29`; rebuild at `code/tct_rule.py:295-307` | `R''_m(e)` at `a`, for every e in the cell | sealed record, plus the **derived identity gate** (below) | **pointwise at a, whole-cell in e** |
| `M_k` = `m.<m>.M_R2` | `mag(R2_interval) ≥ sup_cell |R''_m|` | `ERROR_ALGEBRA.md:97-99, 122` | whole-cell | sealed | pointwise-derived scalar |
| `F̂_r, D̂_r, Ĥ_r` | frozen K1 candidates for `F_r, F_r', F_r''` at e0. They are state-only, degree-12 exact-dyadic polynomials, constant in e | `THEOREM_TC.md:11-13`; `THEOREM_AD.md:97-99`; `p5y_k1_cusum_kernel/IMPLEMENTATION_MAP.md:32-33` | — | **never serialized anywhere** (0/326 records). They are exactly regenerable from committed code (`p5y_k5_tail_c6_evidence_recovery/README.md:41-50`) | functions |
| `δ_mid(F_r), δ_mid(dF_r), δ_mid(H_r)` → `r.<r>.delta_F/D/H` | certified midpoint residual bound: "reachable-set Bernstein range + frozen truncation allowances" of the candidate's residual equation at e0 | `THEOREM_TC.md:22-31`; `tct_inputs.py:98-100` | `‖(I−K)X̂ − … − Ŝ‖` at e0 | **262-field identity gate**: every object `delta_mid`, exact | **norm-only** |
| `ε_mid(src(r,k))` → `r.<r>.eps_src[0..3]` | midpoint source-node errors. `src(0,k) = Sclosed:k`, `src(r,k) = S:r:k`. k ≤ 2 come from the frozen midpoint DAG, k = 3 from Aux3 `midpoint_order3_eps` | `THEOREM_TC.md:30-32`; `tct_inputs.py:54-55, 101-102` | `‖Ŝ^(k) − S^(k)‖` at e0 | identity gate: `eps_mid` exact, Aux3 midpoint eps at 53-bit rendering (`p5y_k5_lower_front_order3/code/tc_producer.py:175-203`) | **norm-only** |
| `f_F, f_D, f_H` | `f_X = δ_mid(X) + ε_mid(src(r,k))` | `THEOREM_TC.md:25-27`; `tct_rule.py:169-171` | `‖φ(e0)‖, ‖φ'(e0)‖, ‖φ''(e0)‖` | derived from gated fields | **norm-only** |
| `s_F, s_D, s_H` → `r.<r>.sup.{F,D,H}` | `cert.sup[fam, r, 0]`: certified supremum of the candidate polynomial on X, i.e. `s_X ≥ ‖X̂‖` | `THEOREM_TC.md:42`; `tct_inputs.py:103` | `‖F̂‖, ‖D̂‖, ‖Ĥ‖` | **neither gate directly** (`MEASUREMENT_NOTE.md:37`). See the note below | **norm-only** |
| `k_i` → `norms.k[0..4]` | drift-aware `k_i ≥ sup_cell ‖K_i(e)‖`. Implementation: `A_i(W) = ∫_W |He_i(y)| φ(y) dy` on the shifted window `W = [left−11/2, right+11/2]` | `THEOREM_TC.md:18-20`; `p5y_k1_final_completion/code/sharp_norms.py:20-37` | operator norms | neither gate directly | **norm-only, cell-uniform** |
| `j_i` → `norms.j[0..4]` | `j_i ≥ sup_cell ‖J_i(e)‖`, where `J_e = K_{z,e} + e·K_e` has weight `y·φ(y)`. Implementation: `j_i = A_{i+1}(W)` | `ERROR_ALGEBRA.md:54-58`; `sharp_norms.py:29-36` | operator norms | neither | **norm-only** |
| `sup_S0[n]` | `sup_cell ‖S_0^(n)‖`, with `S_0 = φ(u+e) − φ(l+e)` and a drift-aware closed form | `p5y_k1_cusum_completion_successor/code/order2.py:111-124`; `tct_inputs.py:91-92` | source derivative sup | neither | **norm-only, cell-uniform** |
| `Ĥ_r(a)` → `r.<r>.H_at_a` | `cert.origin(("H", r, 0))`: the order-2 candidate evaluated at the atom. It is committed as a degenerate interval (lo = hi) | `tct_inputs.py:96, 104` | centre of the F_r'' enclosure | **derived identity gate** | **pointwise** |
| `W2[r:j]` | `assembly.enclose(origin(W,(r,j),2), cellwise W:r:j:2)`: whole-cell enclosure of `W_(r,j)''(e)(a)`, where `W_(r,j) = K_e^j S_r` | `tct_inputs.py:106-109`; `THEOREM_TC.md:63-65` | finite-power terms of `R''_m` | **derived identity gate** | **pointwise at a, whole-cell** |
| `eps_cell_refined[H:r]` | `refine2` whole-cell error of `H_r`. It is the `±` in `R2_interval` | `THEOREM_AD.md:104-110, 135`; `tct_adopted_inputs.py:10` | `‖H_r(e) − Ĥ_r‖` uniformly on the cell | sealed (extract) | **norm-only** (applied at a) |
| `eps_mid` / `eps_cell` (record nodes) | midpoint / whole-cell node error bounds of the frozen DAG | `THEOREM_AD.md:101-102, 121-122` | source/object errors | identity gate, exact equality (`tc_producer.py:175-180`) | norm-only |
| `c(m)` | frozen assembly coefficients: `F_r` gets `1/m` (r < m); `W_(r,t−r−1)` gets `1/t − 1/m` (1 ≤ t < m) | `p5y_k5_lower_front_order3/code/tc_rule.py:35-41`; `ERROR_ALGEBRA.md:134-148` | — | exact rationals | — |
| `C_upper` | see §1.2. Also Lemma G's `A0` | `THEOREM_TCT.md:22-28` | `‖(I−K_e)⁻¹‖` | frozen cover | **norm-only** |
| `A0, A1, A2` (Lemma G) | `A0 = C`, `A1 = k1·C²`, `A2 = k2·C² + 2·k1²·C³` | `THEOREM_TCT.md:22-33`; `tct_rule.py:65-76` | `|[∂^j R_e f](a)| ≤ A_j ‖f‖` | derived | multiplier: sup-norm in, pointwise out |
| Aux3 `candidate_suprema['S:r:3','Sclosed:0:3','h:j:3']` and `midpoint_eps[…]` | order-3 source and h-tower candidate suprema, and certified midpoint errors | `THEOREM_TCT.md:82-88` | `‖S_r'''(e0)‖`, `‖h_j'''(e0)‖` via `sup + eps` | identity gate (53-bit rendering, `tc_producer.py:181-203`) | **norm-only, midpoint** |

**The 262-field identity gate.**
- `tc_producer.identity_gate` (`p5y_k5_lower_front_order3/code/tc_producer.py:163-208`) compares the following against
  the sealed record, and refuses if fewer than 150 fields are compared (:204-206):
  - every `cert.residuals[*].delta_mid`;
  - every `record.eps_mid` and `record.eps_cell` node, by exact rational equality;
  - the Aux3 `midpoint_eps`, the Aux3 object `delta_mid` and the Aux3 `candidate_suprema`, at a 53-bit rendering,
    where the 256-bit value must be no larger.
- The tail cells record `fields_compared: 262, identical: true` (`TCT_INPUTS_30{6..9}.json:46-48`; `MEASUREMENT_NOTE.md:19-23`).

**The derived identity gate** (`tct_rule.derived_identity_gate`, `code/tct_rule.py:284-315`):
- It rebuilds `R2_interval` for every m from `H_at_a`, `W2` and the record's `eps_cell_refined`.
- The rebuild must be contained in the record interval, with a normalised endpoint gap ≤ 1e-6.
- Worst observed gap: 3.63·10⁻⁸ over 20 comparisons (`MEASUREMENT_NOTE.md:36`; `EXECUTION_DECISION.md:38`).

**Note on the order-0 suprema (trust surface).**
- The Aux5 serializer writes only order-3 `cert.sup` entries into `candidate_suprema`
  (`p5y_k1_cusum_aux5_successor/code/qualify5.py:157-161`: `if k[2] == aux_certifier.AUX_ORDER`, and `AUX_ORDER = 3`
  at `p5y_k1_cusum_aux3_successor/code/aux_certifier.py:73`).
- So `sup.{F,D,H}` at order 0 are **not** compared directly, as `MEASUREMENT_NOTE.md:37` states.
- The C6 adjudicator's phrase "which is where `cert.sup[fam, r, 0]` appears directly"
  (`p5y_k5_tail_c6_evidence_recovery/evidence/adjudication/C6_ADJUDICATION.md:379`) is therefore inaccurate as worded
  (reading).
- Its conclusion still holds, through a different path. `sup{F,D,H}` feed `order2._env2_H` / `_dres_H`, which feed
  `delta_cell`/`eps`, and those are compared exactly. **So any material tightening of the sup norms is refused by the
  gate** (`C6_ADJUDICATION.md:388-395`).

### 2.3 Theorem TC / TC-T objects built from the inputs

**Taylor candidate and residual.** `F̃(e) = F̂ + tD̂ + (t²/2)Ĥ + (t³/6)Ĝ` and `φ(e) = S(e) − (I − K_e)F̃(e)`
(`THEOREM_TC.md:14`).

**Midpoint premises (P2).** `‖φ^(j)(e0)‖ ≤ f_F, f_D, f_H, f_G` (`THEOREM_TC.md:22-36`).

**(P2′), the zero order-3 candidate.** `Ĝ := 0` gives
`φ'''(e0) = S'''(e0) + 3K₁Ĥ + 3K₂D̂ + K₃F̂` (`THEOREM_TCT.md:46-57`). Hence:
- `f_G = 3k₁·s_H + 3k₂·s_D + k₃·s_F + σ3`, and the implementation adds `eps_src[3]` on top
  (`THEOREM_TCT.md:53, 59-61`; `tct_rule.py:142-150, 172`);
- `s_G = 0` and `|Ĝ(a)| = 0` (`THEOREM_TCT.md:55-57`).

**(P3), the fourth-derivative envelope, at s_G = 0.**
`Env4 = σ4 + 6k₂·s_H + 4k₃(s_D + ρ·s_H) + k₄(s_F + ρ·s_D + ρ²·s_H/2)`
(`THEOREM_TCT.md:128`; general form at `THEOREM_TC.md:37-47`; code at `tc_rule.py:66-71`). Env4 is **norm-only and
whole-cell**.

**Statement (theorem TC §3, verbatim in TC-T §4).**
- The Taylor sums are
  - `p0 = f_F + ρ·f_D + ρ²·f_H/2 + ρ³·f_G/6 + ρ⁴·Env4/24`,
  - `p1 = f_D + ρ·f_H + ρ²·f_G/2 + ρ³·Env4/6`,
  - `p2 = f_H + ρ·f_G + ρ²·Env4/2`.
- The radius is `rad_r = A0·p2 + 2A1·p1 + A2·p0`. The half-width is `half_r = rad_r` (plus `ρ|Ĝ(a)|` in general).
- The enclosure is `𝓗_m = Σ_{r<m}(1/m)[Ĥ_r(a) ± half_r] + Σ c·𝒲`.

Sources: `THEOREM_TCT.md:122-128`; `THEOREM_TC.md:53-69`; `tc_rule.py:74-91`.

**Consumption.**
- `H_k ← H_k ∩ 𝓗_m`, refusing if the intersection is empty, then `M_k ← min(M_k, mag(H_k))`, then the frozen
  `k5b_literal` (`THEOREM_TCT.md:129-130`).
- rad_r is a bound on a **pointwise-at-a** quantity (`|F_r''(e)(a) − Ĥ(a) − tĜ(a)|`), but it is built **entirely from
  norm-only inputs**.
- The route audit confirms this: "`f_G` and `Env4` are norm-only" (`ROUTE_AUDIT_R1.md:53`).

### 2.4 Committed values, cells 306–309

**Cell geometry and gate status (`TCT_INPUTS_30x.json`).**

| cell | e0 (:45) | ρ (:172) | left (:51) | right (:173) | K1 record sha (:50) | identity gate (:46-48) |
|---|---|---|---|---|---|---|
| 306 | 17452573/10000000 | 108337/2500000 | 680769/400000 | 17885921/10000000 | 9c9da15b…6476bcd59 | 262, identical |
| 307 | 36710051/20000000 | 938209/20000000 | 17885921/10000000 | 1882413/1000000 | 28bacf0a…1f56d23d65 | 262, identical |
| 308 | 38663231/20000000 | 1014971/20000000 | 1882413/1000000 | 19839101/10000000 | e8d7a412…9e955f2e5be5 | 262, identical |
| 309 | 40761931/20000000 | 1083729/20000000 | 19839101/10000000 | 2092283/1000000 | 95be4c65…a8e65cdacc0 | 262, identical |

**Candidate suprema `sup.{F,D,H}` per r (exact dyadics).**

| cell | r=0 (F / D / H) | r=1 | r=2 | r=3 | r=4 |
|---|---|---|---|---|---|
| 306 (:85-88, 105-108, 125-128, 145-148, 165-168) | 584850524711873/562949953421312 / 333904106410379/562949953421312 / 94046924504519/140737488355328 | 136760282352047/281474976710656 / 371021494067257/562949953421312 / 1017289958882113/1125899906842624 | 20814507638927/70368744177664 / 138905871519717/281474976710656 / 1019876638881427/1125899906842624 | 183516980499725/562949953421312 / 477147502022725/1125899906842624 / 1365456479088297/1125899906842624 | 71140413678183/281474976710656 / 23213755888499/70368744177664 / 1330518509940993/1125899906842624 |
| 307 (:86-88, 106-108, 126-128, 146-148, 166-168) | 1130301013857279/1125899906842624 / 312915445790241/562949953421312 / 355835383360391/562949953421312 | 560315086341445/1125899906842624 / 348445187832115/562949953421312 / 969957781920865/1125899906842624 | 180392740593751/562949953421312 / 572200157276593/1125899906842624 / 1077948010841399/1125899906842624 | 357584761680621/1125899906842624 / 107049786047993/281474976710656 / 80042964424255/70368744177664 | 268037186902519/1125899906842624 / 198372067825145/562949953421312 / 1082058045916461/1125899906842624 |
| 308 (same lines) | 545641669254003/562949953421312 / 592731262194493/1125899906842624 / 678044877746173/1125899906842624 | 276670108769/549755813888 / 645319035171935/1125899906842624 / 457327896819743/562949953421312 | 197112879588599/562949953421312 / 293053841848831/562949953421312 / 1123088113719093/1125899906842624 | 85351297476481/281474976710656 / 12487669761857/35184372088832 / 1334920658029875/1125899906842624 | 241931218401553/1125899906842624 / 396118539786979/1125899906842624 / 824037110254013/1125899906842624 |
| 309 (same lines) | 262811212386249/281474976710656 / 279538517188549/562949953421312 / 322156630215901/562949953421312 | 142775916541399/281474976710656 / 314432571304371/562949953421312 / 846705967152719/1125899906842624 | 419404623807529/1125899906842624 / 144852859252253/281474976710656 / 1123742779019817/1125899906842624 | 41126509840067/140737488355328 / 171815482733065/562949953421312 / 5022025716321/4398046511104 | 103759700944097/562949953421312 / 374516259726439/1125899906842624 / 343238440191949/562949953421312 |

**Order-2 candidate at the atom, `H_at_a` = Ĥ_r(a).** Each is a degenerate interval with lo = hi.
Lines :73, :93, :113, :133, :153.

| cell | r=0 | r=1 | r=2 | r=3 | r=4 |
|---|---|---|---|---|---|
| 306 | −73311762632211/281474976710656 | −358101866426925/1125899906842624 | 27820783961487/1125899906842624 | −472440385108547/1125899906842624 | −873293093892781/1125899906842624 |
| 307 | −138673106864445/562949953421312 | −309333755061143/1125899906842624 | 75946876361079/1125899906842624 | −35865913658147/70368744177664 | −766458319867053/1125899906842624 |
| 308 | −259969291916153/1125899906842624 | −130194234157165/562949953421312 | 101041768463363/1125899906842624 | −672428098706267/1125899906842624 | −592505263191429/1125899906842624 |
| 309 | −15026343592353/70368744177664 | −212299423539773/1125899906842624 | 95255675670117/1125899906842624 | −371737705538193/562949953421312 | −45180454768097/140737488355328 |

**Norms and source suprema.**
- `norms.k[0..4]` and `norms.j[0..4]` are 256-bit rationals at `TCT_INPUTS_30x.json:53-68`.
  - As strings, `j[i] = k[i+1]` for i = 0..3. That is what `sharp_norms.py:36` predicts.
- `sup_S0[0..4]` is at `:175-181`.
- Committed decimal ranges over 305–309 (`MEASUREMENT_NOTE.md:60-61`):
  - k₀ 0.99978–0.99995, k₁ 0.79706–0.79767, k₂ 0.96498–0.96705, k₃ 1.50064–1.50699, k₄ 2.77345–2.79053;
  - sup_S0: 0.41719–0.44103, 0.28729–0.33123, 0.49327–0.54617, 0.69424–0.70015, 1.33595–1.35489.

**Residuals and source errors.**
- `r.<r>.delta_F/D/H` and `eps_src[0..3]` are long 256-bit rationals.
  - Cell 306: `TCT_INPUTS_306.json:76-83, 96-103, 116-123, 136-143, 156-163`.
  - Cells 307–309: same layout.
- Committed decimal `delta_mid` for 306 (sealed-record rows): `phase_a/TAIL_BLOCKER_MAP.json:2010-2084`.
  - Examples: F_0 3.5685834706989496e-05, H_0 0.0004470042417948758, dF_0 7.123732443929636e-05.
  - Range over the tail: δ_mid(F) ≈ 1e-7…4e-5, δ_mid(dF) ≈ 4e-7…1.5e-4, δ_mid(H) ≈ 5e-6…4e-4 (`TAIL_BLOCKER_AUDIT.md:41`).

**K1 record intervals (`ADOPTED_TAIL_INPUTS.json`).**

| cell | block | C_upper | m=5 D / M_R2 / R2 / R | eps_cell_refined H:0..4 | record_sha256 |
|---|---|---|---|---|---|
| 306 | 108-212 | 109 | 191-205 | 138-144 | 207 |
| 307 | 213-317 | 214 | 296-310 | 244-248 | 312 |
| 308 | 318-422 | 319 | 401-415 | 349-353 | 417 |
| 309 | 423-527 | 424 | 506-520 | 454-458 | 522 |

- Short verbatim example: 306 m=5 `M_R2 = 24441055674252543/4503599627370496` (:196) and `R2_interval.lo = −24441055674252543/4503599627370496` (:199).

Committed decimal renderings of the sealed m = 5 state (`phase_a/TAIL_BLOCKER_MAP.json`):

| cell | M_R2 | R2_cell | g(e0) interval | ρ·x_hi·M_R2 | Γ (sealed, direct) | M needed | eps_cell_refined H:0..4 |
|---|---|---|---|---|---|---|---|
| 306 | 5.427004551140101 (:1983) | [−5.427004551140101, 4.994907120617597] | [−0.31064872814764055, −0.302674155894373] (:2002-2004) | 0.42063779338572466 (:2008) | +0.11796363749135165 (:1982) | 3.905055721051138 (:1984) | 1.7329698799731348, 3.365210205724418, 4.723632207264241, 6.892952794470229, 8.247927912648944 (:1996-2000) |
| 307 | 5.335183825031916 (:2279) | [−5.335183825031916, 4.9983563016494115] | [−0.27982185698825895, −0.2716387904948848] | 0.4711225589262594 (:2304) | +0.1994837684313746 (:2278) | 3.0761483479002325 (:2280) | 1.663066481291623, 3.3668792432490493, 4.600298970601028, 7.038195861199869, 7.954440572043019 (:2292-2296) |
| 308 | 5.296076774839419 (:2575) | [−5.296076774839419, 5.0465080288610284] | [−0.25292715305560626, −0.24489517123463297] | 0.5332119802886561 (:2600) | +0.2883168090540232 (:2574) | 2.432397764101128 (:2576) | 1.6038074621812768, 3.27953882423775, 4.787568130935219, 7.058504084318855, 7.783695178467173 (:2588-2592) |
| 309 | 5.269941292129297 (:2871) | [−5.269941292129297, 5.096959807552557] | [−0.2308374187469047, −0.22332604549393695] | 0.597471099721181 (:2896) | +0.374145054227244 (:2870) | 1.969827744481147 (:2872) | 1.5404061689770623, 3.199389617171967, 4.987929553811039, 6.924975777100094, 7.807170642435843 (:2884-2888) |

- R half-widths are 2–3e-4 and D half-widths 1.7–2.3e-3, so "the point enclosures are not the blocker" (`TAIL_BLOCKER_AUDIT.md:20-21`).
- A NON-CERTIFIED diagnostic puts the true R'' on the tail at −0.27 (305) … −0.09 (309). Certified M is therefore
  ≈ 20–55× the truth (`TAIL_BLOCKER_AUDIT.md:31-33`).

**Aux3 order-3 evidence for (P3′).**
- `ADOPTED_TAIL_INPUTS.json` candidate_suprema are at 306 :112-120, 307 :217-225, 308 :322-330, 309 :427-435.
  midpoint_eps are at :123-131, :228-236, :333-341, :438-446.
- Example (306): `S:1:3 = 346761737015811/140737488355328`, `S:4:3 = 3590706077558817/1125899906842624`,
  `h:4:3 = 3603911653200491/1125899906842624`, `Sclosed:0:3 = 6306391235615475/9007199254740992`.
- 309: `S:1:3 = 1710864258909607/562949953421312`, `S:3:3 = 534965384383071/140737488355328`,
  `h:3:3 = 985080425492483/281474976710656`.

**Lemma-G atom constants** (`TAIL_FORECAST_R2.json:38-64`):

| cell | A0 | A1 | A2 |
|---|---|---|---|
| 306 | 7.230406258255243 | 41.697052649841126 | 531.4670671630953 |
| 307 | 6.6792892997618765 | 35.57778229811774 | 422.1285970238484 |
| 308 | 6.174137363908812 | 30.393446012323317 | 336.052306022857 |
| 309 | 5.782414324348792 | 26.650741928068 | 277.9282709148853 |

Later campaigns replace these with registry supplies. C2 "substitutes only A0, A1, A2"
(`p5y_k5_tail_c2_closure/OPEN_NOTES_DISPOSITION_C2.md:22-23`).

**Committed σ3/f_G statements.**
- At 309 the pure tower gives σ3 = 5.9, 16.9, 36.5, 67.2 for r = 1…4, against adopted 3.04, 3.41, 3.81, 2.25 (`THEOREM_TCT.md:79-80`).
- (P3′) reduces σ3 to 0.69–3.81, and σ4 at r = 4 from 345.10 to 235 (`THEOREM_TCT.md:104-106`).
- f_G ≈ 4.9–8.9 with Ĝ := 0 (`THEOREM_TCT.md:64`).
- At r ≥ 1, σ3 is 42–48 % of f_G (`p5y_k5_tail_c5_exhaustion/phase_1/C5_BLOCKER_DECOMPOSITION.md:59-62`).

**Measured-range summary** (`MEASUREMENT_NOTE.md:50-62`):
- sup.F 0.1843–1.0789, sup.D 0.2981–0.6952, sup.H 0.5723–1.3345;
- `H_at_a` from −0.8171 to +0.0897 (4 of 25 are positive);
- sup.H/sup.D 1.113–4.464, sup.D/sup.F 0.532–1.805.

---

## 3. The order-3 part

### 3.1 The surrogate that TC-T actually uses

The zero-candidate order-3 residual (`resG` in C4/C8 language) is
`f_G = 3k₁·s_H + 3k₂·s_D + k₃·s_F + σ3 (+ eps_src[3])`.
- Theorem text: `THEOREM_TCT.md:53`. Code: `tct_rule.py:142-150, 172`.
- C4 calls it the "order-3 surrogate `resG = k₃·supF + 3k₂·supD + 3k₁·supH + σ₃`"
  (`p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md:238`).

**How it enters.**
- `f_G` enters `p2` as `ρ·f_G`, `p1` as `ρ²·f_G/2`, and `p0` as `ρ³·f_G/6`.
- `Env4` enters as `ρ²·Env4/2` in `p2` (`THEOREM_TCT.md:124-125`).
- **C5's decomposition** of the radius sum S (`C5_BLOCKER_DECOMPOSITION.md:41-51`), for 307/308/309 under the C2-era
  constants:

  | component | 307 | 308 | 309 |
  |---|---|---|---|
  | `A0·ρ·f_G` | 61.59 % | 60.04 % | 58.80 % |
  | `A0·ρ²·env4/2` | 19.86 % | 21.52 % | 23.06 % |
  | `A0·f_H` (the measured residual) | 0.11 % | 0.10 % | 0.09 % |

- Cell-309 values are at `C5_DECOMPOSITION.json:239-251`.

### 3.2 The (P3′) two towers

**Pure tower** (`THEOREM_TCT.md:76-78`; `tct_rule.py:80-91`):
- `‖h_1‖ ≤ 1` and `‖h_1^(n)‖ ≤ sup_S0[n−1]`, because `h_1' = −S_0` exactly;
- `‖h_j^(n)‖ ≤ Σ_i C(n,i)·k_i·‖h_{j−1}^(n−i)‖`;
- `σ_n(r) = Σ_i C(n,i)·j_i·‖h_r^(n−i)‖`.

**Two towers, r2 repair of review note N1** (`THEOREM_TCT.md:90-103`; `tct_rule.py:94-138`):
- **Midpoint tower**, used for σ3 only: `t_mid[j,3] = min(tower[j,3], adoptedh(j))`.
- **Cell tower**, used for σ4 only:
  - `t_cell[j,3] = min(tower[j,3], adoptedh(j) + ρ·tower[j,4])`;
  - `t_cell[j,4]` is re-derived by the Leibniz recursion.
- `adopted3(r) = cs['S:r:3'] + me['S:r:3']` bounds `‖S_r'''(e0)‖`, and `adoptedh(j) = cs['h:j:3'] + me['h:j:3']`
  (`THEOREM_TCT.md:87-88`).
- σ3 is a **midpoint (P2)** premise and σ4 a **whole-cell (P3)** premise. Substituting the midpoint value into the
  order-4 recursion was the unsound r1 defect (`THEOREM_TCT.md:90-95`).
- The live half is `S:r:3` for r = 1…4 and `h:j:3` for j = 2, 3, 4. `h:1:3` and the r = 0 refinement never bind
  (`THEOREM_TCT.md:114-117`).

### 3.3 What "real order-3 candidate Ĝ" and "real order-3 R" mean

**Real Ĝ.** It is the frozen order-3 producer's degree-12 dyadic candidate `G_r` for `F_r'''` at `e0`. Its Layer-1 solve is
`(I − K)Ĝ_r = K₃F̂_r + 3K₂D̂_r + 3K₁Ĥ_r + Ŝ_r:3` (`p5y_k5_cusum_order3_producer_design/DESIGN.md:44, 54-56`).
- It carries its certified residual `δ_G`: the Bernstein range of `(I−K)Ĝ − K₃F̂ − 3K₂D̂ − 3K₁Ĥ − Ŝ:3` at e0 (`DESIGN.md:66-68`).
- There is **one real address per (cell, e0)**, with objects r = 0..4 (`THEOREM_TC.md:12-13`;
  `p5y_k5_lower_front_order3/TC_SUCCESSOR_SPEC.md:16-25`).
- In TC it contributes three quantities: `s_G = ‖Ĝ‖` (into Env4), `|Ĝ(a)|` (centre motion `ρ|Ĝ(a)|`), and
  `f_G = δ_G + eps_src[3]` (`tct_rule.py:165, 172`; `THEOREM_TC.md:67`).
- **Break-even** between a real Ĝ and Ĝ := 0: `s_G` below ≈ 44.6–53.5 × s_H per cell (`THEOREM_TCT.md:63-72`).
- **Adopted lower-front evidence** (Campaign A, cells 11–44) (`p5y_k5_m5_tail_closure/phase_c/EXECUTION_DECISION.md:53-55`):
  - `s_G/s_H` = 34.8–80.5;
  - `|Ĝ(a)|/s_G` = 0.680–0.681 over all 170 objects;
  - `δ_G` = 2.8e-3…7.9e-3.

**Real order-3 R.** It is a certified signed cell enclosure of `R'''_m`, built from:
- the new resolvent rung `F_r:3 = (I−K)⁻¹[K₃F_r + 3K₂F_r' + 3K₁F_r'' + S_r''']`;
- `W:3`, and the all-m assembly at order 3;
- a whole-cell remainder, exported as `L_m`/`U_m` (`DESIGN.md:43-48, 105-113`; `K5_TARGET_AND_THIRD_ORDER.md:85-99`).

It feeds K5-B's chain lower bound `L_k ≤ inf R'''` (`K5_GLOBAL_BRIDGE.md:11, 23-27`), not TC-T.

**The chain problem on the tail.** The readiness audit finds the m = 5 tail "a chain problem, not a local one". An order-3
bound on 305–309 alone buys nothing without an **unbroken** run from cell 0, or a tightened R'' enclosure
(`p5y_k5_order3_readiness_audit/README.md:79-81, 109-113`). `Z2` never fires, since no `R2_interval.lo > 0` (:106-108).

**What exists.**
- The Aux3/4/5 records carry order-3 **source** objects (`S_r:3`, `W:3`, `h_j:3`) as **unsigned magnitudes only**. They
  contain no `F_r:3` (`p5y_k5_order3_readiness_audit/README.md:126-130`; `DESIGN.md:28-36`).
- The real producer is qualified on synthetic systems only.
  - "No real CUSUM cell is evaluated" (`p5y_k5_cusum_order3_real_producer/README.md:3-4`).
  - The authorization registry is frozen **empty** (:15).
  - Qualification r1: QM mutation FAIL (20/21), QP STAGNATING (`p5y_k5_cusum_order3_real_producer/RESULT.md:31-37`).
- The one real order-3 probe is at cell 0, at drift ≈ 0. "No certified transport across that range exists" to the
  tail (`C5_ADJUDICATION.md:200-203`).

### 3.4 Critical ratio and E10 diagnostic (quoted)

**`TAIL_FORECAST_R2.critical_sup_G_over_sup_H_ratio`** (`p5y_k5_m5_tail_closure/evidence/forecast_r2/TAIL_FORECAST_R2.json:67-73`):
- 305 64.72474028085173, 306 47.986101203397524, 307 32.032829281673614, 308 19.195056304643465, 309 10.54598319680089.
- This is the largest `s_G/s_H` at which a real-Ĝ route still **closes**. It uses the Lemma-G constants and the model
  `|Ĝ(a)| = 0.681 s_G`, with δ_G the per-r adopted maximum (`THEOREM_TCT.md:66-69`; `FORECAST_R2.md:42-45`;
  `p5y_k5_tail_c2_closure/phase_r/R_STAGE_DESIGN.md:29-32`).
- The adopted lower-front ratio is 34.8–80.5, so 309 needs the tail ratio 3.3–7.6× smaller (`FORECAST_R2.md:44-45`).
- Per-r adopted `ag_max`/`dg_max`/`gh_max` are at `TAIL_FORECAST_R2.json:3-28`.

**Under later supplies** (`R_STAGE_DESIGN.md:34-38`; producer `p5y_k5_tail_c2_closure/code/c2_critical_ratio.py`):

| cell | Lemma G | C1 | C2 |
|---|---|---|---|
| 307 | 32.03283 | 34.55795 | 37.32219 |
| 308 | 19.19506 | 20.93621 | 23.26035 |
| 309 | 10.54598 | 12.18694 | 14.15799 |

- `min(G, C1)` at 307 = 34.82089 (`R_STAGE_DESIGN.md:62-66`).
- The tail's own `s_G/s_H` "has never been measured" (:69-70).

**E10**, the perfect-order-3 diagnostic (`p5y_k5_tail_c2_closure/evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json`,
C2 supply). "Perfect" means `sup_G = abs_G_at_a = delta_G = 0`, so f_G is reduced to `eps_src[3]`
(`c2_critical_ratio.py:189, 194`; `R_STAGE_DESIGN.md:23-24`).

| cell | Γ (lines) | mag | Γ_perfect_order3 | mag_perfect_order3 | critical_sG_over_sH |
|---|---|---|---|---|---|
| 306 | −0.030469257709306738 (:15) | 3.5119460127500672 | −0.21751603611711204 (:17) | 1.0986970521070953 | 54.8673607560044 |
| 307 | 0.033132953404317905 (:27) | 3.451359412896 | −0.17175591984010868 (:29) | 1.1311143264496613 | 37.32219327967945 |
| 308 | 0.10270008356594545 (:39) | 3.4524564789357517 | −0.12665519383926 (:41) | 1.1744072175613398 | 23.26034927841336 |
| 309 | 0.16224941061997425 (:51) | 3.400934402274074 | −0.08732986165115685 (:53) | 1.199542379772895 | 14.15799020701014 |

- `order3_would_close: true` for all four.
- The route audit classes E10 as "diagnostic (NE)" (`ROUTE_AUDIT_R1.md:157`).

### 3.5 Governance obligations on any real order-3 step (C2 notes)

- **N1.** The order-3 producer's registry forbids any real CUSUM cell. A successor-owned bridge must bind the executor,
  protocol, runtime, address set, schema, precision, cap, seal and consumer (`OPEN_NOTES_DISPOSITION_C2.md:5-18`).
- **N3.** The manufactured oracle covers only r = 0 and m = 1. The R stage needs tail-geometry fixtures and exact
  cross-checks for the source tower, the W assembly, the order-3 injection, whole-cell transport and consumer
  composition (:20-31).
- **N5.** The four order-3 fields (`sup.G`, `abs_G_at_a`, `delta_G`, `eps_src[3]`) have no identity gate. "They can
  widen but not shift" is not enough (:33-43).
- **N7.** The deterministic direction is not exhausted: a D′ step clears C2's 20 % bar at zero cost. This blocks any
  R-stage authorization (:72-75; `R_STAGE_DESIGN.md:8-18`).
- **R-stage design.** R-a is cell 307 only, 1 address, ≈ 0.44 CPU-h. R-b is 307–309, ≈ 1.3 CPU-h. An anchor at one cell
  transfers an *estimate*, not a certificate (`R_STAGE_DESIGN.md:76-88`).

---

## 4. Sup-norm and cover routes as previously analysed

### 4.1 C4 (`p5y_k5_tail_c4_exhaustion/`; verdict ACCEPTED_WITH_SCOPE_LIMITATION, excluded [309])

**§6 sensitivity** at cell 309 (single-knob, indicative) (`C4_ADJUDICATION.md:229-240`):

| probe | critical A0 |
|---|---|
| baseline | 3.214236 |
| residuals × 0.90 | 3.214686 |
| `sup_S0` × 0.5 | 3.367552 (voids the exclusion) |
| `sup{F,D,H}` × 0.5 | 4.160309 (voids it and becomes closable at the MC Λ) |
| ρ × 0.5 | 7.534321 |

"The dominant channels are the order-3 surrogate and the cell width" (:242-244).

**§7, the seven unexcluded mechanisms** (`C4_ADJUDICATION.md:254-269`):
1. residual-specific order-0 bounds `(Ĝ_e|φ_H|)(a)/D_e` in place of `A0‖φ_H‖`, which escapes the E_a[τ] floor;
2. tightening `sup{F,D,H}` and `sup_S0`, the dominant channel;
3. cover refinement (smaller ρ at 309);
4. TC-T assembly / K5-B clause (W2, the (P3) envelope, the σ₃/σ₄ towers);
5. for 308, a certified upper bound on Λ₃₀₈ below 4.375229 **plus** ≥ 18.2× on (A1, A2);
6. 306/307, untouched;
7. the order-3 R stage.

**Condition 7.** Cost (a) residual-specific order-0, (b) sup norms feeding `resG`, (c) cell width at 309, and
(d) 307's (A1, A2) (`C4_ADJUDICATION.md:554-559`).

**§8.** The R-stage premise is not available (:276-295).

### 4.2 C5 (`p5y_k5_tail_c5_exhaustion/`; ACCEPTED_WITH_SCOPE_LIMITATION, adopted [])

**Clause.** `Γ = g_hi + ρ·x_hi·M`. "Only M is improvable": `g_hi` is the sealed record and `ρ, x_hi` are the cover
(`README.md:30-35`; `phase_1/C5_BLOCKER_DECOMPOSITION.md:8-20`).
- M is set by TC-T (≈3.3), against the sealed ≈5.3 (:22-23).
- Theorem C5-T is an exact-weight transport:
  - `P = max((−H_lo)⁺·w_R, (H_hi)⁺·w_L)`, with `w_R = ρ(x_hi − ρ/2)` and `w_L = ρ(x_lo + ρ/2)`;
  - premise `x_lo > 0`, which fails at cell 0;
  - it gains 1.2–1.3 % (`C5_ADJUDICATION.md:13-44, 561-565, 573-577`).

**Condition 10: three non-R-stage oracles each close every open cell** (`C5_ADJUDICATION.md:606-613`; values at :215-219):

| oracle | Γ at 307 / 308 / 309 |
|---|---|
| ρ halved (cover refinement, route B1) | −0.130448 / −0.086647 / −0.050020 |
| `sup F/D/H → 0` (route A1) | −0.103207 / −0.049231 / −0.000347 |
| `f_G → 0` (a real order-3 surrogate, A2) | "closes all three" |

The first two are blocked "by a missing toolchain and an external record store, not by mathematics".

**The six source-supply levers** (percent cut that voids the 309 exclusion under C5-T;
`evidence/forecast/C5_FORECAST.json:24-32`, producer `code/c5_forecast.py:239-246`). All are DIAGNOSTIC (:40).

| lever | cut (%) |
|---|---|
| `f_G_order3_surrogate` | 1.3039933276160391 |
| `env4_order4_envelope` | 3.3226707586807693 |
| `sigma3` | 3.236522299841146 |
| `sigma4` | 3.6694468495892534 |
| `all_four_together` | 0.6076076662635768 |
| `candidate_sup_norms_supF_supD_supH` | 2.0561597034092847 (under the frozen clause: 5.535691483567017) |

- `ERRATUM_C8_GATE.md:39-44` counts these as the "six" levers.

**The 309 margin under C5-T** (`C5_FORECAST.json:10-23`; `C5_ADJUDICATION.md:321-327, 358-364`):
- Γ at the C4 floor B = 3.297250282 falls from +0.004661130 to **+0.001708896**.
- Critical A0 moves from 3.214236023 to 3.266415728, leaving 0.944 % slack.
- A further penalty cut of 0.7593915 % voids the exclusion.

**Condition 11 order.** E2 (sharper Λ₃₀₉), A1 (sup norms), E1 (operator A0), then B1 (cover refinement at 309:
"a governed new K1 address, not the R-stage"). C4 route (a) is to be costed alongside (b) (`C5_ADJUDICATION.md:615-622`).

### 4.3 C6 (`p5y_k5_tail_c6_evidence_recovery/`; ACCEPTED_WITH_SCOPE_LIMITATION, 14 conditions)

**Candidate payloads never serialized.**
- The K1 candidate **polynomials** were "never serialized — anywhere, ever": not in git, and 0 of the 326 sealed records.
- Their **suprema** are committed in `TCT_INPUTS_30{5..9}.json` (`README.md:41-50`).
- C5 Condition 11(b), "retrieve the payloads", is FALSIFIED (`OPEN_NOTES_DISPOSITION_C6.md:12`; `C6_ADJUDICATION.md:586-594`).

**The identity gate makes faithful replay give zero gain.**
- "A faithful replay returns the adopted `sup{F,D,H}` and delivers exactly zero of A1's gain, by construction."
- The mechanism is that sup norms propagate into `eps_mid`/`eps_cell`, which are compared exactly at 256 bits
  (`C6_ADJUDICATION.md:388-397`; `README.md:6-11`).
- **A1 is "harder than C5 believed"** (`OPEN_NOTES_DISPOSITION_C6.md:30-33`). It needs:
  - a certifying host (none is in scope, C6-N1 :28-29);
  - a producer protocol that permits a non-identical sup;
  - an unknown amount of slack in the certifier's sup routine, against the 2.0562 % requirement.

**A3** (a cancellation theorem for `φ''' = S''' + 3K1Ĥ + 3K2D̂ + K3F̂`):
- It is bounded above by the `f_G → 0` oracle, −0.173324 / −0.128674 / −0.089759 (DIAGNOSTIC, frozen clause)
  (`C6_ADJUDICATION.md:596-600`).

**Replay-surface caveat.** A pointwise φ_H is outside every committed gate (`ROUTE_AUDIT_R1.md:47`).

### 4.4 C7 (`p5y_k5_tail_c7_e2_lambda309/`; ACCEPTED_WITH_CONDITIONS)

**Method.** Exact rational arithmetic (`README.md:40-65`).
- C4's theorem L is `E_a[τ] ≥ H/E[V]` with `V = (|z|−K)⁺`.
- Wald's identity is exact: `E[τ′]E[V] = H + E[R]`, where R is the overshoot of the unclipped majorant walk and τ′ ≤ τ
  pathwise. Hence `E_a[τ] ≥ (H + E[R])/E[V]`.
- `E[R] = ∫ψ dμ`, where `ψ(u) = E[(V−u)⁺]/P(V>u)` is the mean residual life.
- Tier 1 bounds `E[R]` by `inf ψ`.
- The multi-tier LP (theorem C7-E2c) needs `U ≥ E[τ′]`, which Lemma C7-U supplies via geometric domination.
- The bound is evaluated at `e = e_lo`.

**Bounds** (`README.md:12-17`):
- L1 = 3.461283497;
- **L3 elementary = 3.586306094 (PRIMARY, dependency-free)**, which clears the C5-T critical A0 3.266416 by 9.7933 %;
- L3 registry = 3.597941639;
- L3 Lorden = 3.600337620.

**Family ceiling** 4.679910340, below the certified A0 4.867216117 (`README.md:109-113`).
- Going further needs a bound on `E[τ] − E[τ′]` or on the gap between the cell sup and `e_lo` (:115-117).
- Scope: 309 only. For 308 the current certified floor remains C4's 3.512733596 (§5).

---

## 5. Cell 308 specifically

### 5.1 What Λ is

**Definition.** `Λ_k := sup_{e ∈ cell k} E_a[τ](e)`: the expected alarm time (ARL) of the frozen two-sided CUSUM, started
at the atom `a = (0,0)`, under drift e (`p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md:12-16, 36`).
- `(I − K_e)⁻¹1(x) = E_x[τ]`, since `K_e` is positive and sub-Markov (`C4_ADJUDICATION.md:53`).

**The chain** (`C4_TARGET_RECONSTRUCTION.md:39-47`; `C4_ADJUDICATION.md:45-53`):

| item | value |
|---|---|
| state | reachable closure `X = {(p,m) ∈ [0,5]² : p = 0 or m = 0 or p + m ≤ H − 2K = 4}` |
| constants | H = 5, K = 1/2, C = H + K = 11/2 |
| innovation | `z ~ N(−e, 1)`: detector input `z = raw − e`, `raw ~ N(0,1)` |
| update | `s⁺ ← max(0, s⁺ + z − K)`, `s⁻ ← max(0, s⁻ − z − K)` |
| alarm | "iff the **unclipped** update exceeds H in either coordinate", i.e. `z > C − p` or `z < m − C`. "The threshold on the statistic is H = 5, not C = 11/2" |
| producer | pinned `cusum_layer1.py` sha `efcc0f36…` (:49-50) |
| atom split | `T(x,z) = a` iff `z ∈ [m − K, K − p]` (non-empty iff `p + m ≤ 1`) (`p5y_k5_perron_deflated_resolvent/theorem/OPERATOR_AUDIT.md:25-28`) |

### 5.2 How Λ relates to A0: the Lemma-SM admissibility floor

- **Lemma SM(d).** `sup_{‖f‖≤1} |[(I−K_e)⁻¹f](a)| = τ_a/D_e = E_a[τ]`, attained at `f = 1` (`THEOREM_AD.md:51, 56`).
- Hence a uniform order-0 atom constant is admissible **iff** `A0 ≥ Λ_k`. "No certificate can go under it"
  (`C4_TARGET_RECONSTRUCTION.md:8-18`).
- Lemma G's `A0 = C_upper ≥ sup_x E_x[τ] ≥ E_a[τ]`. Lemma Dv′ gives `A0 = min(Ā, τ/D_lo)` (:23-27).
- The floor constrains **only** norm-only order-0 bounds. "SM(d)'s sharpness is attained at f = 1 and says nothing
  whatever about a specific residual", hence the residual-specific escape (`C4_ADJUDICATION.md:205-209`).

### 5.3 Numbers for 308 (all quoted)

**Geometry.** Cell 308 is `e ∈ [1.882413, 1.983910]`. It shares its right endpoint with 309's left
(`C4_TARGET_RECONSTRUCTION.md:84-90`).

**Certified floor.** `Λ₃₀₈ ≥ 3.512733596`, from C4 route L `H/E[(|z|−K)⁺]` at `e_lo`. That is the optimal point for this
bound, which is monotone decreasing in e (`phase_3/C4_CANDIDATE_ROUTES.md:18, 30-38`; `C4_ADJUDICATION.md:81`).
- It is still "the current floor 3.512734" (`ROUTE_AUDIT_R1.md:270, 453`; `ADJUDICATION_C8.md:270, 382`).

**Monte-Carlo evidence** (the C4 adjudicator's own 2,000,000 paths; `C4_ADJUDICATION.md:9-11, 80-83, 175-181`):

| quantity | value |
|---|---|
| `E_a[τ](1.8824130)` | **4.30910 ± 0.00102** |
| 308 midpoint | 4.17398 ± 0.00097 |
| 309 `e_lo` | 4.04731 ± 0.00092 |

- The "~65 standard errors" gap is measured against the **frozen-clause** threshold 4.375229 (:176-177).
- Two committed float diagnostics give midpoint values 4.4445 (307) and 4.1743 (308), interpolating to ≈4.315 at
  `e = 1.882413` (`C4_TARGET_RECONSTRUCTION.md:107-111`).
- **Caveat (reading).** Identifying `Λ₃₀₈` with the value at `e_lo` assumes `E_a[τ]` is decreasing in e. No committed
  artifact certifies that (`C4_TARGET_RECONSTRUCTION.md:88-90`; `p5y_k5_tail_c7_e2_lambda309/README.md:115-117`). The certified floor is valid
  regardless.

**Thresholds.**

| threshold | value | source |
|---|---|---|
| frozen-clause critical A0 (A1 = A2 = 0) | 4.375228833136 | `C4_ADJUDICATION.md:105`; `C4_TARGET_RECONSTRUCTION.md:76` |
| C5-T ceiling | **4.442851487961** | `ADJUDICATION_C8.md:270` |
| certified operator-mixed A0 (C3) | 5.2185 | `C4_TARGET_RECONSTRUCTION.md:76` |
| Lemma G A0 | 6.174137363908812 | `TAIL_FORECAST_R2.json:53` |

**The exclusion proposition (X308).** "a certified floor above 4.442851, when the current floor is 3.512734 and the MC
truth is 4.311".
- It has zero closure leverage.
- Scientific risk is VERY_HIGH: "on uncertified MC at ~65 SE the target bound is false"
  (`ROUTE_AUDIT_R1.md:450-459`; `C4_ADJUDICATION.md:508-512`).
- C4 certifies **no upper bound** on Λ (C4-N2, `OPEN_NOTES_DISPOSITION_C4.md:33-36`).
- **The dichotomy.** A certified upper bound on Λ₃₀₈ below 4.375229 would itself be an admissible A0 that closes 308
  at A1 = A2 = 0. So "cannot be excluded" and "can be closed under the knockout" are exhaustive
  (`C4_TARGET_RECONSTRUCTION.md:113-115`).

**C3-N4.** The concrete next target is a certified lower bound on `E_a[τ]`, `> 4.3752` (308) and `> 3.2142` (309), against
certified A0 5.2185 / 4.8672. Setting A1 = A2 = 0 leaves Γ = +0.039568 (308) and +0.092812 (309)
(`p5y_k5_tail_c3_closure/OPEN_NOTES_DISPOSITION_C3.md:20-28`; table at `evidence/adjudication/C3_ADJUDICATION.md:346-359`).

**C4 Condition 2.** Erratum E4/E5.
- `C4_ROUTES.json`'s "the honest answer is that none can" and the `E[tau] < infinity (Lemma T)` citation must be
  recorded as errata.
- "No successor may quote either sentence as establishing anything" (`C4_ADJUDICATION.md:527-532`;
  `phase_3/C4_CANDIDATE_ROUTES.md:3-9`).

**C4 Condition 3.** Strike "one of them is progress".
- At `A0 = 4.311`, closing 308 still requires an **18.2× reduction of (A1, A2)**.
- At `A0 = 4.375229` it is impossible at any (A1, A2).
- C4-N3 is binding: nothing licenses "cell 308 is closable" (`C4_ADJUDICATION.md:534-537`; `C4_TARGET_RECONSTRUCTION.md:117-124`).
- These are frozen-clause figures.

**Other 308 status.**
- Under C5-T with perfect information (A0 → Λ, A1 = A2 = 0), R3 "closes 307 and 308" (`ADJUDICATION_C8.md:382`).
- It needs 1.438423× uniform eff to close, and 1.798029× to be adoptable (`ROUTE_AUDIT_R1.md:271`, COUNTERFACTUAL_ONLY).
- 308 needs S to fall 31.54 %. The oracle-perfect atom supply misses by 0.003 (`C5_BLOCKER_DECOMPOSITION.md:31, 70`;
  `C5_ADJUDICATION.md:254-255`).

---

## 6. What R(e) is

**Probabilistic definition** (`p5_nonlinear_dynamics/DEFINITION_AUDIT.md:24-56, 80-84, 104-108`):

| item | definition |
|---|---|
| cycle start | the detector is reset to `(0,0)` = the atom `a` |
| innovation | `z_t = raw_t − e` with `raw_t ~ N(0,1)` iid, where e is the reference error entering the cycle |
| stopping time | `τ` = first step whose post-update test alarms |
| window | `w = min(m, τ)` |
| terminal mean | `Rbar = (1/w)·Σ_{r<w} raw_{τ−r}` |
| response | `R_{D,m}(e) := E[Rbar | e_j = e]` |

- Also `E[e_{j+1}|e] = ρ_reuse·R(e)` (T2, `p5_nonlinear_dynamics/THEOREM.md:37-44`).
- **m is the reuse-window length** (the number of terminal raw observations averaged), with m ∈ {1,2,3,5}. It is **not a
  derivative order.** "Order 3" refers to `∂_e³`.

**Target H3a** (`p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md:19-22`): `s(e) := −R_{D,m}(e)/e` is continuous and
strictly decreasing on `(0,2]`, with `s(0+) = Γ̃ − 1 = 1/ρ_c` and `s(2) < 1`.
- R is odd and real-analytic, with `R'(0) = 1 − Γ̃` (:31-34).
- With `g(e) = R(e) − e·R'(e)`: `g' = −e·R''` and `s' = g/e²`, so H3a ⇔ `g < 0` on `(0,2]`
  (`K5_GLOBAL_BRIDGE.md:16`; `p5y_k5_order3_readiness_audit/README.md:45-46`).
- The K5-B direct clause is `Γ_k = hi(R_k − e0·D_k) + ρ_k·x_k·M_k` (`K5_GLOBAL_BRIDGE.md:27`).

**Operator form (CUSUM).**
- `(K_e f)(p,m) = ∫_{m−c}^{c−p} φ(z+e)·f(T(p,m;z)) dz` on `B(X)` with the sup norm, where
  `T = (max(0, p+z−k), max(0, m−z−k))` and `c = 11/2` (`OPERATOR_AUDIT.md:10-15`).
- `R_e = (I − K_e)⁻¹`, with `‖R_e‖ = sup_x E_x[τ]` (`OPERATOR_AUDIT.md:55`).

**Sources** (raw variable) (`p5y_k1_cusum_kernel/IMPLEMENTATION_MAP.md:28-33`; `ERROR_ALGEBRA.md:54-70`):

| object | definition |
|---|---|
| `h_1` | `1 − K_e 1`, the one-step alarm probability |
| `h_j` | `K_e h_{j−1} = P_x(τ = j)` |
| `S_0` | `φ(u+e) − φ(l+e)` |
| `S_r` | `J_e h_r = K_{z,e} h_r + e·K_e h_r` |
| `F_r` | `R_e S_r` |
| `W_(r,j)` | `K_e^j S_r` |

**Assembly** (`IMPLEMENTATION_MAP.md:46-51`; `ERROR_ALGEBRA.md:134-148`; `p5y_k5_cusum_order3_producer_design/DESIGN.md:47`):
- `R_m(e) = (1/m)·Σ_{r<m} F_r(e)(a) + Σ_{t=1}^{m−1} (1/t − 1/m)·Σ_{r<t} W_(r,t−r−1)(e)(a)`.
- For m = 5: `(1/5)·ΣF_r + (4/5)·S_0 + (3/10)(K S_0 + S_1) + (2/15)(K²S_0 + K S_1 + S_2) + (1/20)(K³S_0 + K²S_1 + K S_2 + S_3)`, all at a.
- The same coefficients serve every derivative order.

**Probabilistic meaning of the objects** (P5X-T1, `p5x_global_nonlinear_dynamics/FROZEN_THEOREM.md:72-98`):
- In the g-variable, `g_r(x0) = E_e[Z_{τ−r}; τ ≥ r+1]`.
- The raw-variable `F_r` is the same object with `raw = Z + e` (`IMPLEMENTATION_MAP.md:5-12, 31`).
- So (reading) `F_r(a) = E_e[raw_{τ−r}; τ ≥ r+1]`.
- The W terms restore the `τ < m` part with denominator `w = τ`.

**Order-0 amplification** at the atom (`THEOREM_AD.md:44-61`; `OPERATOR_AUDIT.md:74-77`):
- `[(I − K_e)⁻¹f](a) = ν_e(f)/D_e`, where `ν_e(f) = (Ĝ_e f)(a)`, `Ĝ_e = (I − K̂_e)⁻¹` is the taboo resolvent (killed on
  return to a), and `D_e = 1 − P_a(T_a < τ)`.
- Its sup over `‖f‖ ≤ 1` is `E_a[τ] = Λ`. That is the link to §5.
- The derivative identities are `∂R = R·K₁·R` and `∂²R = 2R·K₁·R·K₁·R + R·K₂·R` (`THEOREM_AD.md:65`; `THEOREM_TCT.md:30-33`).
