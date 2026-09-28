# Stream E (ASSEMBLY): TPT-B on the frozen TC-T consumer path

**Scope.** This is research code. It ran only on synthetic decoys and on real non-tail inputs.
* No CUSUM m = 5 cell 305–309 was evaluated, reproduced or labelled, except as a refused label inside a guard control.
* No file named TCT_INPUTS_30*, C2_D5_FORECAST*, REGISTRY_C1*/C2*, ADOPTED_TAIL_INPUTS*, TAIL_FORECAST_R2*, or any
  RLR307 result/evidence file was opened.
* No drift in [6/5, 13/5] or its mirror was evaluated.
* New target evaluations: Γ306/307/308/309 = 0/0/0/0.
* Nothing was committed.

**Route status.** TPT-B on the TC-T path is **VALIDATED_SYNTHETIC**. On the TC path with the lower-front committed
constants it is **VALIDATED_NON_TARGET**, where it is degenerate (see E5).

**Tail application.** Any tail application inherits incident 01 (the TPT proxy exposure) and
`FREEZE_DESIGN_TPT_TAIL.md` §0: disclosure plus the user's floor/closure-only ruling. Nothing here authorizes it.

## E1. The frozen consumer path, from a TC-T input object and a supply to Γ

**Files and pins.**

| key | file | blob / sha256 |
|---|---|---|
| c2 | `p5y_k5_tail_c2_closure/code/c2_d5_forecast.py` | blob 18403dbe |
| tct | `p5y_k5_m5_tail_closure/code/tct_rule.py` | blob 98f6eee4 |
| tc | `p5y_k5_lower_front_order3/code/tc_rule.py` | sha 8d402d11, the pin in tct:36-37 |
| dc | `p5y_k5_perron_deflated_resolvent/code/deflated_consume.py` | blob a0a836fa |
| km | `p5y_k5_order3_readiness_audit/code/k5_minimality.py` | sha 3a54f0fb |

All paths are under `level4/closure_proofs/`. Line numbers refer to these blobs.

| quantity | where it is computed |
|---|---|
| supply S | c2:194-204. G = `tct.atom_constants_generic(C_upper, k1, k2)` (tct:65-76). C_upper comes from the K1 record (c2:173), k1, k2 from `meas.norms.k` (c2:195). C1/C2 = `dc.atom_constants_r2(Abar, tau, C_T, D_lo, D1, D2)` (dc:97-109), cross-checked against `c2._atom_independent` (c2:60-67, c2:201). S = `c2.combine` (c2:70-76), a componentwise min with provenance. |
| direct clause | `c2.direct(T, R, meas, aux, A, ad, cov, KM)` (c2:79-89), called at c2:205 with `ad = adopted.cells[k].m["5"]` and `cov = cover[k]`. |
| TC-T enclosure (lo, hi) | c2:80 calls `tct.tail_enclosure(R, meas, aux, A, 5, None)` (tct:180-209). |
| rho, k, j, sup_S0 | read from `meas` (tct:185-188). |
| σ3, σ4 | `tct.sigmas` (tct:127-138), which uses `h_towers` (tct:94-116: midpoint tower and cell tower with the ρ mean-value correction) and `sigma_source` (tct:119-124). |
| per-r tuple | `tct.tail_object` (tct:154-177), per r = 0..4. <br>• sF, sD, sH = `meas.r[r].sup` (tct:160). <br>• Ĝ := 0, so sG = \|Ĝ(a)\| = 0 (tct:161-162). <br>• f_G = `fG_zero_candidate` + eps_src[3] (tct:163, 172; tct:142-150), where `fG_zero_candidate` = k3 sF + 3k2 sD + 3k1 sH + σ3. <br>• f_F, f_D, f_H = δ + eps_src[0..2] (tct:169-171). <br>• Env4 = `R.env4(sF, sD, sH, 0, k, σ4, ρ)` (tct:173; tc:66-71). <br>• p = `R.taylor_bounds(fF, fD, fH, fG, Env4, ρ)` (tct:174; tc:74-80). <br>• rad = `R.radius(A, p)` (tct:175; tc:83-87). <br>• half = `R.object_half_width(ρ, \|Ĝ(a)\|, rad)` (tct:177; tc:90-91). <br>• Ĥ_r(a) = `meas.r[r].H_at_a` (tct:198). |
| W terms | `R.coefficients(5)` (tc:35-41): W rows (r, t−r−1) with weight 1/t − 1/5 on `meas.W2["r:j"]` (tct:203-208). F rows have weight 1/5 (tct:197-202). |
| obj[r] | returned by `tail_enclosure`. It holds f_G, env4, p, rad, half, \|Ĝ(a)\|, σ3, σ4. It does **not** hold f_F, f_D, f_H. |
| cross-check | c2:81 compares against the independent `tct.tail_enclosure_crosscheck` (tct:213-280) and raises SystemExit if they differ. |
| H_final and the K1 cap | c2:83 sets H := `ad.R2_interval` (the K1 cap), c2:84 sets M0 := `ad.M_R2`, and c2:85 takes (a, b) = H ∩ (lo, hi) = **H_final**. |
| M | c2:86: M = M0 if (a, b) is empty, else min(M0, max(\|a\|, \|b\|)). |
| geometry | c2:87: e0, ρ, x_hi = `KM.rat(cov[e0 \| rho \| right])`, where KM is the frozen loader's `rat` (km:43-45), bound at c2:162. |
| Γ | c2:88: Γ = (R.hi − e0·D.lo) + ρ·x_hi·M, i.e. **g_hi = R.hi − e0·D.lo**. |

**Not runnable under the quarantine:**
* `c2.main` (c2:128-256). It loads `tail_forecast_r2.py`, which does `import tct_rule` by name (tail_forecast_r2:40-41),
  and it reads target inputs (c2:167).
* `tail_forecast_r2.adopted_state`. It gets R through `tct.load_frozen("tc_rule", pin)` (tail_forecast_r2:108) and KM
  through the adapter (tail_forecast_r2:118).
* The loader below loads the same pinned bytes directly instead.

**Public sub-functions callable without modification:**
* c2: `direct`, `combine`, `_atom_independent`.
* tct: `tail_enclosure`, `tail_object`, `sigmas`, `h_towers`, `sigma_source`, `fG_zero_candidate`,
  `atom_constants_generic`, `tail_enclosure_crosscheck`.
* tc: `coefficients`, `env4`, `taylor_bounds`, `radius`, `object_half_width`, `per_r`, `cell_enclosure`.
* dc: `atom_constants_r2`, `block_for`.
* km: `rat`.

**Extraction method.** `R` is a *parameter* of `direct` and `tail_enclosure`.
* `tptb_tail.CapturingR` is passed as `R`. It delegates every call to the frozen tc_rule function unchanged and
  records the arguments and results.
* The per-r tuple is read off the recorded frozen calls `taylor_bounds(fF, fD, fH, fG, Env4, ρ)` and
  `object_half_width(ρ, |Ĝ(a)|, rad)`. The rows come from `coefficients(5)`.
* This extraction is from the very call that produced Γ. No module global is patched and no file is modified.
* Consistency is checked against obj[r]: f_G, env4, rad, half and |Ĝ| must all agree. So is the call pattern: exactly 5
  calls to each of env4, taylor_bounds, radius and object_half_width, and 1 call to coefficients.

## E2. `tptb_tail.py`

`evaluate_bundle(bundle)` takes an in-memory input object. Its schema is in the module docstring:
* `meas` is the exact TCT_INPUTS schema of `tct_inputs.py`:85-109;
* `aux` is the K1 `auxiliary_evidence`;
* `adopted_m5` is `R_interval`, `D_interval`, `R2_interval` and `M_R2`;
* `cover` is the cover cell;
* `supply`, or `supply_sources` combined through the frozen `c2.combine`;
* `blocks` is optional;
* `committed` is optional.

`evaluate_bundle` reads no file. Refusals are returned as `STOP` records with a code.

**Steps, in order:**
1. **Guards** (defence in depth only; see Open issues 2): `guard_cell` on the label, `meas.cell` and `cover.index`;
   `guard_drift` on the geometry and on every block.
2. **Input checks.** The label must be bound to `meas` and `cover`. m must be 5. The input must be free of order-3
   fields. The geometry must be consistent.
3. **(a) Reproduction.** The frozen `c2.direct` is called through the capturing proxy. The frozen crosscheck refusal
   maps to `FROZEN_PATH_REFUSED`.
4. **(b) Gates.** Any failure gives `REPRODUCTION_FAILED`.

   | gate | requirement |
   |---|---|
   | G-R3 | The extracted tuple equals `rederive_tuple`, an independent re-derivation of THEOREM_TCT (P2′)+(P3′) in own code (tptb_tail:134-179), exactly, coefficient by coefficient. It must also equal `committed.per_r` if that is given. |
   | G-R1 | The whole-cell enclosure rebuilt from the tuple at s = ρ equals the frozen (lo, hi), and equals `committed.H_exact`. |
   | G-R2 | Γ rebuilt as g_hi + ρ x_hi min(M_R2, mag(H_final)) equals the frozen Γ and M, and equals `committed`. |
   | G-R4 | `M_consumed == mag(H_final)`. The capped band is non-empty at s = 0 for the cell constants, and at the narrowest point of every block piece. |

5. **(c) TPT.** Uses `tpt.py` r2, loaded by path at sha256 05cebc9c:
   * the profile at ρ must equal the frozen (lo, hi);
   * `penalty_closed`, `penalty_c5t` and `penalty_frozen`;
   * g_hi + P_frozen must equal the frozen Γ.
6. **(d) TPT-B.**
   * `check_blocks` refuses anything but an exact tiling of [x_lo, x_hi], and any block constant above S componentwise.
   * Then `tpt.penalty_blocked` runs.
7. **Transport gates.** Any failure gives `TRANSPORT_CHECK_FAILED`.
   * **G-T1 / G-T2.** tpt's P must lie in [P_lo, P_hi + tol], where [P_lo, P_hi] is a certified bracket of the true
     sup from an **independent integrator**. That integrator evaluates the band pointwise in t, uses Boole's rule
     (exact for the degree-5 integrands), and brackets any cap crossing to 2⁻²⁵⁶. tol bounds tpt's 60-bit split
     over-estimate. `P ≥ P_hi` certifies soundness.
   * An optional interior grid scan checks the piece-end-maximum claim (quasi-convexity).
   * **G-D.** P_B ≤ P_TPT ≤ P_C5T ≤ P_frozen.
8. **G-CF.** Applies when the binding regime holds (H ⊆ R2, lower end binds, C_lo < 0). The dependency-graph closed
   form Γ(S) = g_hi + ρx_hi|C_lo| + ρx_hi(A0P̄2 + 2A1P̄1 + A2P̄0) must equal the frozen Γ exactly.

The frozen-path loader is `frozen_path_loader.py`.
* It executes 6 pinned files by path under `c308E_fp_*` names.
* It checks each file's sha256 and git blob before and after execution, and records every load.
* It installs the c308 import guard first.
* Its only importer is `tptb_tail.py`, whose entry point refuses quarantined labels and drifts first. It is never
  imported by code that handles a quarantined cell.

## E3. Decoy validation (`decoy_gen.py`, `validate_decoys.py` → `validation/DECOY_VALIDATION.json`)

**Decoy set.** 18 seeded TC-T-shaped decoys, labelled DECOY 9000+. Geometries are e0 ∈ {1/4, …, 11/10, 3, 7/2, 4}.
The set crosses 3 radius regimes × 2 realized centre signs × 3 cap modes, with 1–6 blocks. Half take their supply
through the frozen combine, and some place a block edge at e0.

**Regimes, as measured.** The Taylor-growth share of rad(ρ) was:

| regime | Taylor-growth share of rad(ρ) |
|---|---|
| "taylor" (order-3/4 terms dominate) | ≥ 0.99998 |
| "midpoint" (midpoint term dominates) | ≤ 0.044 |
| "mixed" | 0.28–0.67 |

**Results.**

| check | result |
|---|---|
| status OK, all gates pass | 18/18. G-CF applied on 3/18; transport gates exact-equal on 11/18, the rest are cap-crossing brackets |
| dominance P_B ≤ P_TPT ≤ P_C5T ≤ P_frozen | 18/18 |
| V-S1: relaxed extremal witness of the block band | soundness certified (P_B ≥ P_hi) 18/18; attained within tol 18/18 (sharpness in the measurable class) |
| V-S2: C² test functions R'' = c + a u + b u², certified inside the block band ∩ cap, g(e0) = g_hi | certified sup g ≤ g_hi + P_B for 108/108. The best reaches 0.97 of P_B |
| V-C: θ-controls (1/2, 9/10, 99/100, 999/1000) | detected 18/18 each |
| V-C: `penalty_blocked` fed half the block constants | detected 18/18 |
| determinism | two processes give identical canonical exact output (sha256 0a000f31…) |

**Decoy-only ratios.**

| ratio | range |
|---|---|
| P_B / P_TPT | 0.813–1.0 |
| P_TPT / P_C5T | 0.781–1.0 |
| P_C5T / P_frozen | 0.94–0.998 |

These ratios are driven by arbitrary synthetic block ratios (u ∈ [1/4, 1]) and synthetic inputs. They are not an
estimator of any tail quantity and must never be set beside one (incident 01).

**Not testable on decoys.** Lemma TC-P pointwise soundness cannot be tested here, because decoys have no underlying
operator. It rests on the OV FSM validations (V1; TPT-B B1, 24/24).

## E4. Negative controls through `tptb_tail.evaluate_bundle` (`controls.py` → `validation/CONTROLS.json`)

**29/29 detected.** For each control:
* the valid base decoy returns OK;
* the plant returns STOP with the expected code;
* where stated, the named gates fail while the named others still pass.

| control | plant | caught by |
|---|---|---|
| G-R3 shape | Null-space plant of the s = ρ Taylor map: p0, p1, p2(ρ) are preserved, so rad(ρ) is too, but rad(s) is mis-shaped. Four variants: both directions × two regimes. | G-R1 and G-R2 **pass**; only G-R3 fails. Without G-R3 the independent P would move by ×1.00016 / ×0.99984 on the decoy. The unsound direction is the latter. |
| Env4 dropped | Env4 set to 0 | G-R1 and G-R3 |
| tiling | gap, overlap, short of x_hi, beyond x_hi | BLOCKS_REFUSED |
| block constants | a constant above S | BLOCKS_REFUSED |
| wrong m | label m = 3 | INPUT_REFUSED |
| wrong m | extraction weighted for m = 3 | G-R1 and G-R3 |
| M ≠ mag(H_final) | adopted M_R2 below mag, with the committed record kept consistent | G-R4 **only** |
| M ≠ mag(H_final) | extraction override | G-R4 only |
| empty intersection at s = 0 | K1 cap between lo(ρ) and lo(0) | G-R4 (N5) |
| sign flip of t | t → −t (both binding sides) | G-T1 |
| sign flip of t | t → e0 − s on the right | G-T1 |
| sign flip of t | t → e0 + s on the left | G-T1 |
| sign flip of t | mirrored block lookup | G-T2 |
| sign flip of t | mirrored geometry | tpt's x_lo > 0 refusal |
| frozen call chain | a proxy halving `radius` | the frozen crosscheck (FROZEN_PATH_REFUSED) |
| committed record | H, Γ or per-r mismatch | G-R1, G-R2, G-R3 respectively |
| supply | explicit supply ≠ frozen combine | INPUT_REFUSED |
| guards | quarantined label, adjacent label, geometry in the band | GUARD_REFUSED, before any evaluation |

## E5. Real non-tail evidence (`lower_front_tptb.py` → `validation/LOWER_FRONT_TPTB.json`)

**Scope.** The lower front uses the TC path, not TC-T. The only committed per-block constants there are those of
registry r1 (`p5y_k5_perron_deflated_resolvent/evidence/registry_r1/REGISTRY.json`, rule r2).

**Finding.** Registry r1 has **exactly one block per cover cell, with edges equal to the cell edges**: 136/136 pairs
hit one block. So committed constants resolve nothing finer than a cell, and on real lower-front data **TPT-B ≡ TPT**.
A V3-style *gain* validation of TPT-B is therefore impossible there.

**What was run.** The code path was validated on the 136 pairs (CUSUM cells 11–44 × m ∈ {1, 2, 3, 5}):

| check | result |
|---|---|
| S from frozen `block_for` + `atom_constants_r2` equals the committed tc_audit A | 136/136 |
| frozen `tc_rule.cell_enclosure` and the profile rebuilt at ρ from the frozen `per_r` tuple equal the committed H_TC | 136/136 |
| M_consumed = mag(H_final) | 136/136 |
| P_frozen equals the consumed clause | 136/136 |
| G-T1 | 136/136 |
| committed-block TPT-B: tiling exact, G-T2, P_B == P_TPT exactly | 136/136 |
| 3-way split carrying the valid cell triple: G-T2, P_B == P_TPT exactly | 136/136 |
| G-D | 136/136 |

P_TPT/P_C5T lies in 0.9752–0.9926. That independently reproduces V3.

## Files (all under `NS/streams/ASSEMBLY/`)

* `frozen_path_loader.py` — the frozen-path loader
* `tptb_tail.py` — sha256 b373a8b4…
* `decoy_gen.py`
* `validate_decoys.py`
* `controls.py`
* `lower_front_tptb.py`
* `validation/DECOY_VALIDATION.json`
* `validation/CONTROLS.json`
* `validation/LOWER_FRONT_TPTB.json`
* this report

**Ledger.** 9 streamE lines: SYNTHETIC_VALIDATION, NONTARGET_REAL_VALIDATION and INFRASTRUCTURE, including one
retroactive line for the dev smoke runs. None carries a LEAK_FLAG.

## Open issues

1. **The real tail input path is not built, by design.** A formal campaign needs a loader for TCT_INPUTS, the adopted
   extract, K1 C_upper and the cover.
   * Its "committed per-r values" for G-R3 exist only as floats (`tail_forecast_r2` detail). So G-R3 there can be
     exact only against the independent re-derivation, and float-tolerant against the record.
2. **Guards are defence in depth.**
   * The enclosure is e0-free and P is affine in e0, so the barrier is that this code reads no input file.
   * A formal campaign must pin `frozen_path_loader.py`, `tptb_tail.py` and `tpt.py`, and regenerate E3/E4 at its
     freeze commit.
3. **The TPT-B tail premise is unsupplied.** It needs a certified sub-block registry for the target cell, with
   per-block triples min'ed with S.
   * Such a registry was not opened or examined here: REGISTRY_C2 is quarantined.
   * A formal design must fix, before any evaluation, how the per-block triple is formed (which supplies are min'ed
     per block) and its provenance.
   * The incident-01 liability applies.
4. **Precision and scan scope.**
   * tpt.py's 60-bit cap split can over-estimate P by at most `tol` (reported). With a 256-bit bracket, soundness was
     certified in every decoy.
   * The static scan was run on this directory only, without planted controls, to avoid temp writes: 6 py + 3 text
     files, 0 findings, 1 report-only literal marked. The coordinator should run the full
     `code/c308_quarantine.py --scan`.
5. **Exposure disclosure.** While documenting E1 I read `THEOREM_TCT.md` §5. It quotes committed cover geometry of
   the tail-adjacent cell. The OV `THEOREM_TPT.md` and `INCIDENT_01` quote committed tail radius shares, and graph §0
   states the qualitative binding-regime facts. None of these was reused, computed on or written anywhere, and the
   decoy regimes follow the brief's wording only.
