# Independent pre-freeze review r1 — theorem-TC successor (CUSUM K5 lower front)

Reviewer: fresh context, did not write the code. Worktree `p5y-k5-lower-front-order3` @ `945dbdb9`.

Reviewed state: this is the working tree, not the bare commit. `code/tc_qualify.py` already had an uncommitted
modification when the review started (file mtime 04:08, one minute after 945dbdb9; this reviewer did not make it). The
modification adds the S06 `extraction_code_path` checks and the S08(e) no-op positive path. The findings below refer to
that working-tree version, and the freeze commit must include it.

Read in full:
`TC_SUCCESSOR_SPEC.md`, `theorem/THEOREM_TC.md`, `phase_a/LOWER_FRONT_BLOCKER_AUDIT.md`, `phase_b/ROUTE_COMPARISON.md`,
`config/FEASIBILITY_GATES_A.json`, every file in `code/`, `evidence/dev/MANUFACTURED_DEV.json`,
`evidence/forecast_r1/ROUTE_FORECAST.json`. Frozen dependencies read where the premises live:
`cusum_order3.py`, `rung3_residual.py`, `aux_certifier.py`, `aux_propagate.py`, `propagate.py`, `assembly.py`,
`cusum_layer2.py` (all_residuals, certify, K/J, closed forms), `repair_layer2.py` (Repair1 header), `order2.py`,
`sharp_certifier.py`, `sharp_norms.py`, `intervals.py`, `qualify5.py` (run_cell, _aux_record),
`deflated_consume.py` (block_for, atom_constants_r2), `consumption_adapter.py` (read_records, cells_for_m),
`THEOREM_AD.md`.

What I ran locally (pure Python only; nothing remote, no CUSUM computation):
- `tc_rule.cell_enclosure` vs `tc_crosscheck.enclosure` on 300 random all-m records (random k, j, sup_S0, W, A), m = 1, 2, 3, 5:
  0 mismatches.
- `cells.json`: for cells 0–59 (so all addresses 11–44), left = e0 − ρ and right = e0 + ρ exactly, with zero radii.
- Adopted `DEFLATED_CONSUMPTION.json`: whole-cell H radius minus the mean AD H radius (the W and origin share) is
  4.7e-5 (m = 1), 4.0e-4 (m = 2), 1.9e-3 to 2.0e-3 (m = 5) at cells 11 and 44.
- The `tc_rule.py` sha256 (8d402d11…) equals `rule_sha256` in `MANUFACTURED_DEV.json`.

## Summary

The mathematics is sound. P1–P4 are supplied by the frozen objects the producer reads, and the rule and the
independent cross-check implement the theorem exactly. The 53-bit identity-gate rendering is correct and does not weaken
soundness. The two BLOCKING findings are both in the frozen consumption path. The spec's acceptance items 1–3 are not
checked by any code that will be frozen. The consumer does not bind what it consumes to the frozen protocol. After the
freeze only `evidence/tc_r1/` may change, so neither can be added later. Both are small, local fixes in
`tc_consume.py` (plus a qualification case).

## Checks 1–8

1. **Theorem.** I checked the Leibniz forms of φ⁽ʲ⁾(e0) against the frozen residual code:
   - `cusum_layer2.all_residuals` F_r, dF_r, H_r are `(I−K)X̂ − Σ C(k,i)K_iX̂_{k−i} − Ŝ^(k)`.
   - `rung3_residual.g_residual` has `TERMS = (1,0,G),(3,1,H),(3,2,D),(1,3,F)`, so res_G = (I−K)Ĝ − 3K_1Ĥ − 3K_2D̂ − K_3F̂ − Ŝ'''.
   - All operators are at e0 (`self.b` built at `exact(e0)`), and truncation is covered by `eps_zi`.

   Signs and coefficients match THEOREM_TC P2. The source nodes are right. The residuals use the closed form `Sclosed`
   for r = 0 (propagate `_source_node`, `g_residual` line 45), and its error node `Sclosed:k` = reward_allow[k]
   (`aux_certifier.py:241` for k = 3). For r ≥ 1 they use `S:r:k`, whose midpoint node is δ_mid(S_r:k) + Σ C(k,i) j_i ε(h:r:k−i).

   The Taylor factorials and powers are right, and so is which terms carry t (p0 has ρ⁴/24, p1 ρ³/6, p2 ρ²/2). The
   φ⁗ formula is right: F̃⁗ = 0, and the i = 0 term vanishes.

   Env4 holds for every e in the cell:
   - k_i = min(∫_W |He_i|φ, …) with W = [left − 11/2, right + 11/2] (`sharp_norms.kernel_norm`), which is uniform on the cell.
   - j_i = ∫_W |He_{i+1}|φ is valid for J_i = ∂^i(K_z + eK). j_4 needs He_5 roots, and they are tabulated.
   - sup_S0[n] = `sup_source_derivative_on(n, left, right)` is uniform on the cell.
   - The candidate suprema are Chebyshev-coefficient sums from `_cand`, taken on the same payload as the power-basis polynomial.
   - σ4's r ≥ 1 tower is correct: h_1 = 1 − K_e1 ∈ [0,1], h_1' = −S_0 exactly (`_closed_forms`), and K_e is substochastic.

   E'' = Rφ'' + 2(∂R)φ' + (∂²R)φ with ∂R = RK'R and ∂²R = 2RK'RK'R + RK''R is correct. Lemma Dv/Dv' bound these
   functionals at a pointwise in e, for any argument, so applying them with f = φ⁽ʲ⁾(e) at each e is legitimate. The
   blocks come from `block_for(left, right)` and cover the whole cell.

2. **Regularity.** The z-window and the atom window are e-free, T(x,z) is e-free, and X is e-free. φ(·+e) is entire, so
   e ↦ K_e, K_z, J_e are analytic into B(X). S_0 is a closed form, and S_r = J_e K_e^{r−1} h_1. I found no hidden
   e-dependence. The resolvent exists on the whole cell (registry blocks cover [left, right]).
3. **Enclosure and assembly.**
   - The centre ± (ρ|Ĝ(a)| + rad) is right.
   - c(m) matches `assembly.coefficients` (checked by `frozen_table_ok`).
   - W2 is `assembly.enclose(origin(W,(r,j),2), cellwise W:r:j:2)`, which is exactly the adopted order-2 W enclosure
     (RefinedCellValues with AuxiliaryRefinement).
   - The arithmetic is exact rational, with outward inputs (mag / lower / upper of balls).
   - The intersection with the adopted H has a non-empty check (`tc_consume.py:153-155`).
4. **Consumer.**
   - The replay gate is strong: rows sha, pass ranges, and per-cell R, D, H, M and via for 0–159, per m.
   - Monotonicity is enforced (`tc_consume.py:162-163`).
   - Cell, geometry and K1-record binding are adequate against a stale cell or a wrong-m mapping (the record is
     m-free, and m enters only through the rule).
   - Protocol binding and the acceptance checks are missing. See B1 and B2.
5. **Producer.**
   - In mode real, `require_authorized` runs before any chain import or record read (`tc_producer.py:298-305`).
   - Replay proposes no G candidate (it uses Aux3Certifier, not Order3Certifier) and writes no scientific field. It does
     evaluate the order-3 right-hand-side terms K_3F̂ + 3K_2D̂ + 3K_1Ĥ + Ŝ''' in memory. See N6.
   - The identity gate is correctly implemented. See the 53-bit section and N3.
6. **Gates and temporal integrity.**
   - The gates were committed at e89b33f2 (02:48) before the forecast at 38c74494 (03:39).
   - Forecast inputs are honest: f_F, f_D, f_H are the adopted record values, and everything not yet measured is ×4 in
     CONSERVATIVE.
   - The one measurable quantity that was estimated is the W radius, 0.01. I verified the adopted value is ≈ 0.002 ≤ 0.01
     (N9).
   - The forecast centre equals the TC centre: symmetric AD shrink, and no T-EXT clip at 11–44.
   - No certified or real TC value exists in the tree. The dev replay only reproduced adopted quantities.
7. **Mutation coverage.**
   - All 14 mutants were detected in dev.
   - Every output-changing mutant of `tc_rule` I constructed is caught by S05 (cross-check equality on synthetic all-m
     records). Several are not caught by the truth-based S04. See N7.
   - The only survivors of S04 ∪ S05 are refusal-removal mutants (N7). They are harmless on producer-generated records.
8. **Pins.**
   - The repository modules that execute appear to be exactly those loaded by `_import_chain()`. The function-level
     imports on the executed path (order2, intervals, cusum_layer1) are already loaded.
   - Nothing at run time asserts this, and the runtime (host, venv, versions) is checked only at qualification. See N8.

## The 53-bit identity-gate rendering (specifically requested)

The reproduction is correct:
- `qualify5.run_cell` builds `record["auxiliary_evidence"] = _aux_record(...)` after the `with workprec(bits):` block
  (line 239), still inside `with guard:`.
- `mag_fraction(x) = x.abs_upper().upper().fmpq()`, and python-flint's `abs_upper` rounds at the context precision.
- So the sealed Aux3 fields are the 53-bit upward roundings of the same 256-bit balls. The gate recomputes exactly that
  (`tc_producer.py:179-185`).

It is not a soundness weakening, for three reasons:
1. Every value theorem TC consumes is the producer's own in-process 256-bit certified value, never the record value. The
   only Aux3 value used is ε(S:r:3 / Sclosed:3) at `tc_producer.py:213`. The theorem holds for whatever candidates are
   actually used, and the consumer only intersects two valid enclosures.
2. All K1 residual δ_mid values, every midpoint node and every whole-cell node are still compared exactly at 256 bits.
   Any change of an order 0–2 candidate (F̂, D̂, Ĥ, ĥ, Ŝ, Ŵ) is caught. Several eps_cell nodes are Aux3-refined, which
   also binds aux_mid at full precision wherever the Taylor branch is taken.
3. The residual provenance gap: an order-3 aux candidate that differs by less than 2⁻⁵³ relative in every rendered aux
   field would pass. That is the finest resolution the sealed record permits, and it cannot change a TC number.

The extra test `fine > recorded` is implied by `coarse == recorded` (abs_upper at 53 bits ≥ abs_upper at 256 bits), so it
is redundant but harmless. The protocol text still says "equals … exactly" (N3).

## Findings

| id | severity | file:line | finding | required fix |
|---|---|---|---|---|
| B1 | BLOCKING | `TC_SUCCESSOR_SPEC.md:47-50`; `code/make_tc_protocol.py:113-117`; `code/tc_consume.py:85-175`; `code/tc_run.py:100-119` | **Pre-registered acceptance items 1–3 are not checked by any frozen code.** (3) "tc_rule and tc_crosscheck agree exactly on every cell and m": nothing in `tc_run`, `tc_consume` or the producer imports `tc_crosscheck` on real records. S05 checks only fixtures and synthetic records. (2) "the reproduction is byte-identical": `tc_run` still writes `TC_INDEX.json` when a reproduction differs (`reproduction: false`, exit 1), and `tc_consume` never reads `index["reproduction"]`. (1) "every address yields exactly one gated real record": `load_tc` consumes whatever cells the index lists and never checks that the set is the 34 addresses. After the freeze only `evidence/tc_r1/` may change, so these checks cannot be added later, and the acceptance decision would depend on unfrozen ad-hoc code. | In `tc_consume`, before any intersection: (a) refuse unless `set(index["cells"]) == set(protocol addresses)`; (b) refuse unless every `index["reproduction"]` value is `True` for exactly the pre-registered reproduction cells {11, 44}; (c) load `tc_crosscheck` from pinned bytes (pin from the protocol), and for every TC cell and m require `X.enclosure(rec, Ak, m) == R.cell_enclosure(rec, Ak, int(m))` exactly, refusing otherwise. Record (a)–(c) in the output. Add a qualification refusal case for each. |
| B2 | BLOCKING | `code/tc_consume.py:46, 67-74, 85-86, 178-185, 193`; `code/tc_qualify.py:180-189` | **The consumer is not bound to the frozen protocol.** The `tc_rule` pin is `None` in PINS and is filled from the CLI argument `--tc-rule-sha256`, so any `tc_rule.py` whose sha is passed is executed. The protocol's `pins` entry for `tc_rule.py` is never consulted. `--tc-index` and `--tc-dir` can be any path. The index's `protocol_sha256` is not compared with the protocol, and nothing checks that the index and cell files are the committed, sealed bytes. The record check (`tc_consume.py:139-144`) accepts any `mode == "real"` record with `identity_gate.identical`. It does not check `binding` (freeze_commit, head, authorization/guard sha), so a record from a different protocol or producer version (for example a pre-freeze or re-frozen producer) is consumed, and the output still reports "replay_gate PASS". This undermines the whole governed chain (protocol → producer → sealed index → consumption). | Make `tc_consume` take `--protocol-sha256`. Refuse unless (a) `sha(config/TC_PROTOCOL.json)` equals it; (b) the tc_rule and tc_crosscheck bytes equal `proto["pins"]`; (c) `index["protocol_sha256"]` equals it; (d) the index and every cell file are read from the committed `evidence/tc_r1/` (`git show HEAD:`) or equal those bytes; (e) every record's `binding` is non-null, with `freeze_commit` equal to the protocol's add-commit and `authorization_sha256` / `guard_sha256` equal to the committed files; (f) `rec["k1_record_sha256"] == proto["k1_record_sha256"][k]` (in addition to the adopted-manifest check). Add S08 refusal cases: wrong tc_rule sha, wrong index protocol sha, missing address, wrong K1 record sha, null binding. |
| N1 | NOTE (load-bearing for the authorization review) | `code/tc_producer.py:124-139, 252-253, 273`; `../p5y_k5_cusum_order3_real_producer/code/cusum_order3.py:3-7, 175-177` | The TC producer runs the order-3 candidate construction (`Order3Certifier._candidates_rung3`) and `g_residual` on 34 real cells directly, bypassing `certify_real_cell` and its pinned REAL_CELL_AUTHORIZATION_REGISTRY (which stays EMPTY). The TC records publish `G_at_a`, an uncertified real order-3 point value per (cell, r). This is a parallel authorization channel for real order-3 computation, with lighter governance than the slot-1 precedent (no launch notice or slot binding, no countersignature). The committed AUTHORIZATION/GUARD JSONs are checked only for `verdict`, `addresses` and `protocol_sha256`. | State explicitly in the spec and protocol that the TC protocol, not the order-3 registry, governs these 34 addresses, and that `certify_real_cell` and `rung3_engine.certify_order3` are not executed. The authorization review must accept this explicitly. In `require_authorized`, bind AUTHORIZATION to the QUALIFICATION_RESULT sha and to the review document, and enforce the commit order qualification < authorization < guard. |
| N2 | NOTE | `code/tc_producer.py:99-120` | In mode real the gate does not check (a) runtime equality (host, python, numpy, scipy, python-flint, venv), which only S02 checks at qualification; (b) `producer_manifest_problems()` of the order-3 producer (spec §4 says "must have no problem"); (c) that `--record-sha256` equals `proto["k1_record_sha256"][cell]` (tc_run supplies it, but a direct invocation need not). The identity gate and B2(f) make (c) fail closed. | Add (a)–(c) to `require_authorized`/`compute`. |
| N3 | NOTE | `code/make_tc_protocol.py:102-103`; `code/tc_producer.py:150-196` | The protocol text says the Aux3 midpoint eps and object delta_mid "equal the sealed K1 record exactly". The implementation compares them at the adopted 53-bit rendering (correct, see the section above). Other gaps: the W candidate suprema are skipped (`startswith("W:")`) although they could be parsed; objects' `delta_cell`/`envelope` and the candidate origins Ĥ_r(a), Ŵ(a) that TC actually consumes are not compared directly (only through the eps_cell nodes). | Freeze the exact rule in the protocol text ("Aux3 fields: equal at the adopted 53-bit rendering of qualify5._aux_record; all other fields: exact at 256 bits"). Optionally compare `R_interval` and `D_interval` per m exactly (this binds the F, D and W origins) and check that the TC centre lies in the record's `R2_interval`. |
| N4 | NOTE | `TC_SUCCESSOR_SPEC.md:54-56` vs `code/make_tc_protocol.py:118-119` | Budget inconsistency in the pre-registration: the spec says a 34 CPU-h protocol cap; the protocol generator hard-codes cap 20 and forecast 9.0. COST_NOTE.md is pending, and I treat the number itself as pending, not as a defect. | Take a single cap and forecast from COST_NOTE.md into both files before the freeze. |
| N5 | NOTE | `../p5y_k5_cusum_order3_real_producer/code/rung3_residual.py:47-48`; `../p5y_k1_cusum_aux3_successor/code/aux_certifier.py:241`; `code/tc_rule.py:104` | For r = 0, reward_allow[3] is counted twice: in δ_mid(G_0) (unrepaired pattern) and again in ε(Sclosed:3). Repair1 removed exactly this duplication for k ≤ 2. It is conservative and negligible (eps_r-sized), so soundness is not affected. | Document it in THEOREM_TC P2 as a deliberate conservative double count. No code change needed. |
| N6 | NOTE | `code/tc_producer.py:13-14, 275-280` | "Computes NO order-3 value of F" holds in the strict sense: no G candidate, no F''' value or enclosure. However, replay does evaluate K_3F̂ + 3K_2D̂ + 3K_1Ĥ + Ŝ''' (the order-3 equation's right-hand side) and its synthetic residual range in memory, and discards them. | Reword it as "proposes no order-3 candidate and records or reveals no order-3 quantity of F" so that the governance claim is precise. |
| N7 | NOTE | `code/tc_manufactured.py:155-203, 212, 240-281` | S04 is truth-based only for r = 0, m = 1, j = 0 and sup_S0[0..3] = 0, and SRC makes only the order-2 source term necessary. Not truth-tested: the r ≥ 1 σ4 J/h tower, the j_i and sup_S0[0..3] terms, the W assembly (m > 1), and the order-0, order-1 and new order-3 source terms. Concrete S04 escapes, all caught only by S05 cross-check equality: `fG = F(o["delta_G"])` (drops ε(S:r:3)); `range(1, n + 1)` in the h-tower (drops K_0h); `lo += c * w_hi; hi += c * w_lo`. Survivors of S04 ∪ S05: removing the refusals `h_lo > h_hi` / `w_lo > w_hi or c < 0` / `_nonneg` (harmless on producer output). | Add fixture families with J-structured r ≥ 1 sources (S_r = J_e K_e^{r−1}(1 − K_e1)) and truth W for m > 1, plus SRC fixtures for k = 0, 1, 3, and the corresponding mutants. Add a malformed-record refusal fixture. |
| N8 | NOTE | `code/make_tc_protocol.py:52-67`; `code/tc_producer.py:245-268` | The pins are collected from `sys.modules` after `_import_chain()` only, not after a full compute, and are never re-checked against what actually loads in the run. Shadowing by sys.path or cwd, or a lazily imported module, would go unnoticed (I found none on the executed path). Interpreter and binary packages are not pinned (runtime checked only at S02). | In `compute()`, after the computation, refuse unless the set of repository files in `sys.modules` equals `proto["loaded_repository_modules"]`. Re-check the runtime there as well (N2). |
| N9 | NOTE | `code/route_forecast.py:208-209, 234` | The forecast estimates the Σc·W'' radius as 0.01 (×4 CONSERVATIVE), although it is an adopted-record measured quantity (the gate rule says "as recorded"). I verified from the adopted consumption that the actual share is ≈ 2e-3 (m = 5) and ≤ 4e-4 (m ≤ 2), so the classification (STRONG) is unaffected. The real feasibility risk is the new sup‖Ĝ‖ (centre motion ρ·s_G and Env4). The CONSERVATIVE m = 5 margin at cell 11 is lo = 2.5 against a half-width of 6.4. | Informational. Record the measured W share in the forecast notes. |
| N10 | NOTE | `code/tc_run.py:37-46`; `code/tc_producer.py:99-120` | "Exactly once per address" is enforced only by `tc_run`. While GUARD is ALLOW, the producer accepts any number of direct real invocations for an address. Outputs are deterministic, so there is no selection freedom, but budget and governance rely on the ledger alone. | Optionally have the producer refuse if an output for the cell already exists in the run's evidence directory, or require a per-run nonce from the ledger. |
| N11 | NOTE | `phase_a/LOWER_FRONT_BLOCKER_AUDIT.md:57-60`; `README.md:10` | A non-certified float diagnostic of the true R'' size on the lower front was produced in the same commit as the frozen gates. The gates are generic (122/122, ×4), so I see no tuning, but the timing cannot be separated from the gate freeze. The README still says A2 is "in progress". | Informational. Update the README at the freeze. |

VERDICT = NOT_READY
