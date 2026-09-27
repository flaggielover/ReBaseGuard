# REVIEW_GLOBAL_INTEGRITY_R1 — global integrity review of the K5 tail overnight campaign

GLOBAL_REVIEW: DEFECTS_FOUND

**Reviewer.** Independent, adversarial and read-only. I wrote none of the reviewed material. Date: 2026-09-28.

**Scope.**
* NS = `level4/closure_proofs/p5y_k5_tail_overnight_research`, branch `p5y-k5-tail-overnight-306-309`.
* Excluded: `streams/C_308/LR/cusum/` (C1b) and `streams/C_308/A0X/gen/` (C2b), which are reviewed separately.
* HEAD moved during the review: 028afad2 → 1ee93ac5 → 4d64e2b0 → 2b118e62 → **23475bee** (final).
  * The new commits added the C2b review, INCIDENT_03, C1b (out of scope) and C1B_* JSONs, and a registry/report edit.
  * I re-checked the in-scope deltas at 23475bee. File:line references are to 23475bee.

**Verdict basis.**
* **No new quantity for cells 305–309, and no evaluation at an in-band drift, was found.**
* The defects are:
  * negative controls of class (c)/(d) still counted as evidence in streams A, B and C1a and in the governance tools;
  * governance artifacts that are stale or overclaim;
  * registry and cross-route rows that contradict repaired stream documents;
  * two residual juxtapositions: a cross-cell (R2.4) residue of Theorem M review N3, and an incident-01 residue in
    the dependency graph;
  * an incomplete latent-proxy list in amendment 2.
* None of the defects changes a theorem.

## 0. Method, coverage and quarantine conduct

**Reading.** I read all in-scope governance code and documents myself:
* `code/ov_quarantine.py`, `code/ov_audit.py`, `validation/build_validation_index.py` and `graph/build_graph_json.py`;
* the registry, the cross-route comparison, the validation report, the README, the dependency graph (md + sources),
  the three incidents, `streams/E_assembly/*` (for the TPT r2 repair) and `streams/D_309/*` (for the D repair).

**Sub-reviewers.** I delegated three read-only sub-reviews under `SCR/review_global/SUBAGENT_RULES.md`: stream A, stream
B, and stream C excluding cusum/ and gen/.
* They ran scratch copies only, with `ov_quarantine.LEDGER` redirected and synthetic or declared drifts only.
* The harness refused their FINDINGS.md writes, so their reports came back as text. The stream B report is summarised
  in `SCR/review_global/B307/FINDINGS_from_subagent.md`.
* I spot-verified every finding of theirs that I use below. Each spot-check is marked "(verified)".

**My own runs.** All were stdlib, `python3 -B`, and wrote nothing in NS:
* `SCR/review_global/audit_copy/`: a copy of `ov_audit.py` and `ov_quarantine.py` with every output (OV_AUDIT, the
  scan and ledger control temp files) redirected to scratch;
* `rg_leakscan.py`: a broader JSON leak scan of all 48 in-scope committed JSON (key/value/string patterns, with a
  planted control, which fired);
* `rg_band_literals.py`: an AST scan of all in-scope committed `.py` for in-band numeric literals;
* `rg_index_leak.py`: the index leak scan re-run on the HEAD artifacts, plus 7 coverage probes;
* `scanprobe/`: 7 planted files through a copy of the static scanner, rooted in scratch;
* `tpt/rg_mutant_baseline.py`: the 12 committed V1 FSM configs at e0 = 1/8, logged to a scratch ledger;
* `pmprobe/`: a copy of `streams/C_308/pm_probe_synthetic.py`, synthetic at e = 1/8. It has no ledger call.

**What I did not do.**
* I did not compute or combine any tail-cell number, and did not evaluate anything at |e| ∈ [1.2, 2.6].
* I imported no historical module.
* I ran no git write, contacted no remote host, and ran no script in place that writes into NS.

**Git history.**
* I extracted `git log -p 8b9fc0bb..HEAD` for in-scope paths (JSON and ledger excluded). It has 485 removed lines.
* I grepped the removed lines for tail ids, %, × and "share".
* The retracted content is all accounted for by incidents 01/02, the C2a S8 withdrawals (0d32a2e8), the TPT r2 repair
  (2f0fb5e1) and the D repair (028afad2). No other retracted target number was found.

## 1. Negative-control audit

**Classes.**
* (a): through the code under test, planted invalid input, guaranteed to fire.
* (b): through the code, not guaranteed; fire rate given.
* (c): tautological or arithmetic.
* (d): tests only a comparison operator.

### 1.1 Controls of class (c)/(d) still counted as evidence

| # | file:line | control | class | counted as evidence at |
|---|---|---|---|---|
| C-1 | `code/ov_audit.py:94` | L3 "negative_control_detected" = `not ("README.md".startswith(NS_REL + "/"))` | (c): constant, never touches the `outside` filter (:91); not in the verdict (:107-112) | `ledger/OV_AUDIT.json` `L3_scope.negative_control_detected: true` |
| C-2 | `streams/A_306/common/cv_validate.py:196-202` | refutation list | items 1, 3 (c) (`L-1/100<L`, `1001/1000>U_d` for U_d ≤ 1); items 2, 4 (d) | in the verdict via `refute_ok` (:202); A_306_ROUTE_SUMMARY.md:29 "refutation pattern exact"; THEOREM_CV.md §7.4 (verified) |
| C-3 | `cv_validate.py:156,164` | "planted_D2_claim_0.9LB2_refuted" | (c): reduces to `lb2 > 0` (verified) | gates `pass` (:164, `>= 5`); "planted claim refuted 5/5" |
| C-4 | `streams/A_306/mechanism/mech_pflat.py:106-110` | planted p-flat value | (d): the plant never enters the detection loop | gates `verdict` (:110) |
| C-5 | `mech_study.py:335-345` | NC2 | (c): the margin is exactly −0.01 by linearity (sub-review A) | "4 negative controls": A_306_ROUTE_SUMMARY.md:30, PROGRESS.md:10, NONTARGET_VALIDATION_REPORT.md:37. Only NC3 is a genuine plant, and NC4 is not a control |
| C-6 | `a306_reproduce_A.py:141-145, 153-154` | planted A1; float mismatch | (d), (d) | the stream's A-reproduction record |
| C-7 | `streams/B_307/code/b307_run_fixtures.py:182,193` | "A0 := τ_a", tested as `tb["tau_a"] < P.Lam` | (d): guaranteed by Lemma SM(d), since D < 1 (verified) | B307_AUDIT_FIXTURES.json P2; HIGHER_ORDER_AUDIT_307.md:358; PROGRESS.md:15 |
| C-8 | `b307_scaling.py:39-40` | planted Λ^{1/2} rung | (c): the least-squares slope is linear, so the result is exactly +1/2 for any data (verified) | B307_SCALING.json; HIGHER_ORDER_AUDIT_307.md:381 |
| C-9 | `b307_cellpipe.py:173` | five-way split identity | (c): holds by construction | fixture records |
| C-10 | `streams/C_308/LR/lr_fsm.py:272-273` | `neg_t_flip` | (d): compares `U20−U01` with `!=` and never exercises `moment_totals` (verified). Sub-review C mutation: corrupting U01 broke identity 2 on 6/6 while this control still reported "detected" 6/6 | `identity_counts`; C1LR_ROUTE_SUMMARY.md:52; THEOREM_LR.md:398; LR/PROGRESS.md:50 |
| C-11 | `lr_fsm.py:1009` | `rebuilt_matches` | (c) | not cited (harmless) |
| C-12 | `streams/C_308/A0X/EXCLUSION_308.md` §c.8 | "analytic negative control (no computation)" | a derivation, not a test | should not be counted as a control. Review M ran the numerical control. |

**No control gates anything in streams A (except C-2/C-3/C-4), B or C1a.**
* No control is asserted, and no script exits non-zero.
* A failing control would show only in a JSON count.

### 1.2 Controls that are sound, class (a)/(b)

**Stream A (sub-review A).**
* P1, P2, P5, P6 and P7 are (a) through the real box inequality in both verifiers (`cv_verify_a.py:162-170`,
  `cv_verify_b.py:216-251`).
* P3 is (a) on the claim line. P4 is a weak (a).
* V_B also rejected near-boundary plants (×0.999, ×0.9999, ×1.001).

**Stream B (sub-review B, fire rates).**
* (a): run_fixtures :88-99, :110-114, :134-139; lower-front 2⁻⁶⁰ plant (`b307_lower_front.py:158-165`).
* (b):

| control | fired |
|---|---|
| cellpipe sign flip | 328/640 |
| f_G := 0 | 146/320 |
| ADLR B3 := 0 | 247/320 (FX_B 7/80; oracle variant only) |
| Hermite sign | 112/120 |
| variance | 225/300 (the 75 n = 1 cases can never fire) |
| tower binomial | 6/54 |

**C1a.**
* `:269-270` sign flip through `moment_totals` is (a), 24/24.
* The checker plants (`:318-362`) are (a) through `check_quadratic_cert`, 24/24. However, dropping the A ≥ 0 conjunct
  is caught by no control (sub-review mutation 0/6).
* The block slack = 0 control is (b), 70/72; it was disclosed and replaced.
* `:1010-1012` is (a), 8/8.

**TPT r2** (E stream; the repair of review R1 B2/B3 is verified in §1.3).
* **P1 code-path plant** (`validate_tpt_r2.py:116-120`) and **TPT-B B4 plant** (`validate_tptb_synthetic.py:77-84`)
  are (a) through `tpt.rad_poly` / `tpt._lo_hi_with`.
  * Both are construction-guaranteed, because λ-scaling a homogeneous radius to max-dev/2 always fires.
  * They show that the comparison path is wired, not that it has power.
* **θ plants** (`:128-129`) are (b): 11/5/2 of 12 for θ = 1/2, 9/10, 99/100.
  * They are truth-relative. A detection implies that `certified_sup_g` would fail, since that function returns an
    upper bound ≥ the grid max.
* **Mutants** M2/M4/M5 are (b): 6/4/2 of 12.
  * They mutate a local replica (`mutant_penalty`, :87-104), not `tpt.py`.
  * My run shows the unmutated replica equals `tpt.evaluate(...)["P_tpt"]` exactly on all 12 fixtures, so the mutants
    are faithful on the uncapped path.

**Stream D after repair** (checked against `D309_*.json` at HEAD).
* Box-wise defect plants in `box_upper_tf` / `box_upper_composite` are (b).
* Premise-truth mutants (`d309_supnorm_fsm.py`: Env4 := 0 60/60, A0/2 60/60, A0 × 0.99 20/60) are (a)/(b).
* RSO: NC a1 44/48, a2 48/48, b 48/48, c 4/12, 12/12, 12/12, d 12/12.
* Cover transport/profile mutants are (b), and `rad_half` is honestly 0/140.
* The relabelled comparator/harness checks (`d309_sct.py`, `d309_supnorm_fsm.py:74-77`, `d309_cover.py:266-268`) are
  no longer counted as evidence.

**Governance.**
* `ov_audit.ledger_negative_control` (:70-78) is (a).
* `build_graph_json` planted cycle (:104) is (a).
* The `ov_quarantine.scan` control (:181-189) and the index leak-scan control (`build_validation_index.py:79,101`) are
  (a), but their plants have exactly the shapes the detectors implement. They cannot show coverage (§1.4).

### 1.3 Were prior review repairs made?

**TPT R1 → r2: repaired.**
* B2: the tautological B4 was withdrawn (`validate_tptb_synthetic.py:77-80` comment) and replaced by the code-path
  plant. V1's operator-only plant is marked WITHDRAWN inside `TPT_SYNTHETIC.json`.
* B3: V2 was executed with a certified truth cap (`validate_tpt_r2.py:133-149`).
* N5/N6/N7 refusals: `tpt.py:160, 215, 327`, tested by `test_tpt_guards.py` G6–G8.
* guard_drift in `_check`: `tpt.py:166`.
* The sha256 pin 05cebc9c equals the current `tpt.py`.
* THEOREM_TPT.md:8-13, §2b and §4 are consistent with the JSON.

**Stream D R1: repaired in the stream, not propagated.**
* Condition 1 (B1): code, JSON power and D_309_ROUTE_SUMMARY §7 agree.
* Conditions 2/3: D docs and summary rows are fixed.
* Condition 5: guard at `d309_hermite_tf.py:72`, `d309_hermite.py:258`.
* Condition 4 (DRP wording): fixed in COVER_REFINEMENT_309.md:10-11, :255, :262-263.
* Condition 4 also required the **registry / final report** to carry the corrected wording. The registry and the
  cross-route comparison do not → finding F9.

**Theorem M R1 → EXCLUSION_308: partial.**
* C1 is fixed at :126-129, with a residue in the b.3 table at :193 (unqualified "optimal e_lo").
* C2 is fixed at :307-311. The residues are conservative understatements: :212-213 "specific to the **atom start**",
  :315, C2A_ROUTE_SUMMARY.md:37 "atom start only".
* N3 is fixed only in the §b.1 table (:137) → finding F12.
* N4/N5 are done: INCIDENT_02, ledger line 155, amendment 2.
* N6: the FREEZE draft :43 is stale.

### 1.4 Coverage of the governance detectors (reviewer probes)

**Static scan** (`ov_quarantine.scan`, copy rooted in scratch).

| detected | not detected |
|---|---|
| int target literal, incl. `305 + 2` | in-band drift literal `F(7, 4)` |
| | `importlib.import_module("tail_forecast_" + "r2")` |
| | `subprocess.run([... "c12r2_cell306.py"])` |
| | string cell id `"308"` |
| | any line carrying `literal-ok` |

* A file that self-declares `historical-read` gets its target literals SANCTIONED.
* `LITERAL_OK` (:155) also suppresses TARGET_INPUT_PATH findings. So the read of the sealed
  `C12R2_CELL306_RESULT.json` at `a306_reproduce_A.py:53` is silently dropped. This contradicts `ov_quarantine.py:53-56`
  ("never silently dropped").
* The only SANCTIONED hit the audit lists is the docstring mention of REGISTRY_C2 (`a306_reproduce_A.py:8`). So
  A_306_ROUTE_SUMMARY.md:7-8 ("the scan lists it as SANCTIONED") misdescribes what the scan saw.
* My greps of in-scope code found no use of dynamic import, subprocess or in-band literals, except guard tests:
  * `ov_quarantine.py:212` self-test;
  * `test_tpt_guards.py:57`, a spoof profile refused by `guard_drift` in `tpt._check` before any computation.

**Index leak scan** (`build_validation_index.leak_scan`) missed all 7 probes:
* a cell list;
* a string cell label;
* a `block: [lo, hi]` pair;
* the keys `drift_lo`, `e_block`, `cell_id` and `index`.

## 2. Leakage audit

**(i) New quantities for 305–309 or in-band drifts: none found.**
* My JSON scan (48 files) found no in-band drift value and no target-cell datum outside config text and labels. The key
  hits were false positives (E_a/τ values and ratios whose key contains `e_`).
* The C2B blocks lie in [1/2, 11/10] ∪ [3, 31/10], with pointwise e ∈ {0, 1/4, 1/2, 1, 3}.
* The AST scan for in-band literals found only guard tests, planted scanner controls and non-drift constants (Hermite
  states, √2).
* The sub-reviews found no in-band evaluation in A, B or C1a. B's real cells are lower-front 11–44, with e in
  [0.0057, 0.0252].
* Committed ledger: 181 lines; `new_target_evaluations` 0; 3 LEAK_FLAG / 3 proxies (incidents 01–03).

**(ii) Juxtapositions (S8, amendment 2 R2.1) other than incidents 01/02/03:**
* F12: EXCLUSION_308.md:418 and C2A_ROUTE_SUMMARY.md:88-89.
* F13: the dependency graph, including a same-row case at `graph/K5_TAIL_DEPENDENCY_GRAPH.md:89`.
* Minor layout cases:
  * `streams/B_307/B_307_ROUTE_SUMMARY.md`: the 307 share in its history subsection (:56-61) is on the same page as
    the R1 monomial statement (:25), a generic gain (:78-79) and lower-front factors (:41, :46);
  * `HIGHER_ORDER_AUDIT_307.md:56-60`: a new qualitative 307 claim, partly false as worded;
  * `CELL306_I1_I2_DISAGREEMENT_AUDIT.md` D.2: a 306 ratio quoted outside the history section;
  * `IDEA_LR_SCORE_CONSTANTS.md`: LR factors (:15-16) with the "307 blocker is (A1, A2)" note (:61).

**(iii) Cross-cell re-attribution (R2.4):**
* F12 (endpoint relabelling of a 309-drift quantity as "at e_hi(308)", including A0X/PROGRESS.md:17).
* The D2 row (EXCLUSION_308.md:370) prints the incident-02 value beside the note on its withdrawn "entailed 308 floor"
  label. F5 (:30) states the shared endpoint, which keeps the withdrawn inference one step away. It is not a new
  re-attribution.

## 3. Claims vs code (sampled)

**Hold.**
* TPT rows (registry :16-17; report :28-29) match `TPT_R2_VALIDATION.json` / `TPTB_SYNTHETIC.json`.
* The D report row as edited in 23475bee matches `D309_*.json`.
* The Hermite 1200/1200 check: `H1_ok` 1200.
* The C1LR headline counts (sub-review C regenerated all three JSONs, identical apart from timing).
* The C2b report counts.

**Outrun the evidence.**
* Registry :45-46 and cross-route :40, :81 (F9).
* Registry :26 "corrections applied" and :27 "discloses incident 02" (F10).
* Registry :53-54 and report :36-37, stream A (F11):
  * "6/6 valid accepted": the TABOO_* weights are byte-identical to ARL_* (verified), so there are 4 distinct
    certificates, and the taboo atom-skip branch is never exercised;
  * `D_SUPER`'s claimed value exceeds 1 (verified), so the D sandwich's upper side is trivial;
  * "certified bracketing … validated" rests on the (c)/(d) controls C-2/C-3.
* Registry :35, B summary :46, REAL_ORDER3_THEORY :403 "5–9×": the JSON gives 4.42–9.35×, against a pure-tower σ3
  baseline that favours R1. B summary G5 = P for R3 has no test.
* REAL_ORDER3_THEORY.md:315 "ADLR always looser" is contradicted by its own table.
* Cross-route :42 "ADLR vs TC-T incomparable" rests on fixture medians only.
* Cross-route :48 "Dv′ essentially exact" holds for E1d′ only.
* Report :41-48 "Every repaired control now plants invalidity through the code under test" and :34 "planted errors
  caught" (stream B) are false while C-2…C-10 stand.
* Report :3-6 says the leak scan flags "any" target cell or in-band drift (§1.4).
* Report :17 "every set was declared before its run" is verified for B by file times only; B's PROGRESS timestamps
  are not clock times.
* **Cross-route :32 and :77.** The strict "<" between C5-T and the frozen clause is not proved; TPT-D gives ≤. The
  notation of :77 is also the reverse of :83.

## 4. Governance (at 23475bee)

| check | result |
|---|---|
| files changed outside NS since 8b9fc0bb | **0** (`git diff --name-only 8b9fc0bb HEAD`; also 0 in the working tree; no untracked file outside NS) |
| r5 | `K5_COVERAGE_MAP_R5.json` blob `f978eeb6…` at HEAD and in the worktree: **unchanged** |
| r6 | no `COVERAGE_MAP_R6` path on any ref |
| exactly-once refs | `refs/c12r2/cell306-target-consumed` dec92e09, `refs/c12r2/cell306-pending-result` 0ac46b3d, `refs/c11rd/r1-execution-consumed` 4b716d43: **unchanged** |
| historical imports | ignored `__pycache__` outside NS exists only for the allowed pure libraries (c7_gaussian, c11_certifier, c11_common) |
| `ov_audit` (redirected copy) | verdict **FAIL**, by design: L1 counts 3 LEAK_FLAG / 3 proxies (incidents 01–03). Scan PASS (56 files, 1 sanctioned file), outside [], r5 true, r6 [], refs ok |

**Deviation.** The committed `ledger/OV_AUDIT.json` says **PASS** at head 9db36e13, with 9 ledger lines and 7 files
scanned. It is stale. A FAIL version at 62e9a74d sits uncommitted in the working tree (F2).

## 5. Findings

**F1 — MEDIUM — governance tool control (c).**
* `ov_audit.py:94`: the L3 control is a constant and is not in the verdict.
* L3 also diffs `BASE..HEAD` only (:89), so modified tracked files outside NS in the working tree would be missed. I
  checked manually and found none.
* **Action:** plant an outside path through the same filter, gate the verdict on it, and include `git diff BASE`
  (working tree).

**F2 — MEDIUM — stale governance artifact.**
* The committed `ledger/OV_AUDIT.json` reports PASS from 9db36e13. The current audit FAILs on the recorded incidents.
* **Action:**
  * regenerate and commit at the final HEAD;
  * record the incidents in the audit explicitly instead of letting a stale PASS stand;
  * never present PASS while LEAK_FLAG > 0.

**F3 — MEDIUM — scanner coverage and silent suppression** (§1.4).
* `ov_quarantine.py:155` lets `literal-ok` drop TARGET_INPUT_PATH, e.g. `a306_reproduce_A.py:53`.
* The scanner does not check drift literals, dynamic imports, subprocess or string cell ids.
* The marker is self-granting.
* A_306_ROUTE_SUMMARY.md:7-8 overstates what the scan saw.
* **Action:**
  * never suppress path findings;
  * add drift-literal, dynamic-import and subprocess checks;
  * list the sanctioned lines;
  * report scanner coverage with a multi-shape control.

**F4 — MEDIUM — stale validation index, narrow leak scan.**
* `NONTARGET_VALIDATION_INDEX.json` was last built at 980c5961:
  * its sha256 mismatches HEAD for C2B_VALIDATION.json and all six D309_*.json;
  * it indexed six C1B_* files while they were untracked, and two of those hashes no longer match;
  * five committed C1B_PW9/SUMMARY files are unindexed.
* Its leak scan misses 7/7 of my probe shapes. Report :3-6 overclaims.
* **Action:** broaden the scan, regenerate at the final HEAD, and restate the report sentence.

**F5 — MEDIUM — stream A (c)/(d) controls counted as evidence** (C-2 to C-6).
* Weak coverage:
  * the TABOO_* certificates duplicate ARL_*, and the taboo skip branch plus the C_T_lower rejection have no
    valid-or-planted case;
  * D_SUPER is vacuous;
  * PROGRESS:27-28 / THEOREM_CV §7.4 wrongly say the depth-5 re-run cured the vacuity.
* **Action:**
  * withdraw or relabel C-2 to C-6;
  * re-plant through `cv_verify_*` or the mechanism screen;
  * add taboo-specific valid and planted certificates;
  * correct the "4 controls", "5/5" and "refutation pattern exact" claims.

**F6 — MEDIUM — stream B (c)/(d) controls counted as evidence** (C-7 to C-9).
* B_307_ROUTE_SUMMARY.md:19 "every check has a negative control" is false. The RO3-E/RO3-F checks have none.
* `B307_LOWER_FRONT_ORDER3.json` predates the committed `b307_lib.py` / `b307_cellpipe.py` by 62 s (file mtimes), so
  its regeneration from committed code is unverified (S3).
* **Action:** relabel, add plants through the code, and regenerate the lower-front JSON.

**F7 — MEDIUM — C1a (d) control counted as evidence** (C-10). The A ≥ 0 conjunct of `check_quadratic_cert` has no
control; this matters before any freeze reuses the checker.
* **Action:**
  * replace `neg_t_flip` with a corruption inside `moment_totals`;
  * add an A < 0 plant;
  * correct THEOREM_LR:398, C1LR summary :52, PROGRESS :50 and report :30.

**F8 — LOW — Q5/S3 in C.**
* `pm_probe_synthetic.py` has no import guard, no drift guard, no ledger call and no JSON output.
* The ratio ranges in `IDEA_LR_SCORE_CONSTANTS.md:15-16` were hand-copied and are inaccurate. My re-run gives PM/true
  A1 2.43–9.21 (stated "3–10×") and A2 7.33–23.6 (stated "10–20×").
* The same figure is repeated in the graph (:125).
* **Action:** add a guarded producer with JSON output and correct the ranges.

**F9 — MEDIUM — registry and cross-route contradict the repaired stream D.**
* Registry :45 "Result-free policies DRP-0/1 are ready" contradicts COVER_REFINEMENT_309.md:262-263.
* Registry :46 ("gains exactly 0 over TPT | FSM 30/30 | REFUTED as a lever beyond TPT") and cross-route :40 ("proved;
  validated 30/30") and :81 present:
  * the transcription identity as validation (review D B3);
  * the fixed-family refutation as unconditional, omitting B2c (review D B2).
* Review D condition 4 required this wording to be carried into the registry.
* **Action:** re-word them per D_309_ROUTE_SUMMARY.md rows B2/B2c and footnote 2.

**F10 — MEDIUM — Theorem M rows overclaim.**
* Registry :26 "corrections applied": the corrections are partial (§1.3).
* Registry :27 "discloses incident 02": false. `FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md` contains no incident
  disclosure (0 grep hits), although INCIDENT_02 and INCIDENT_03 require one.
* Stale status lines: EXCLUSION :3, :209, :349; C2A :31; FREEZE :43.
* **Action:** finish C1/C2/N3, add the incident 02+03 disclosure, and fix the status lines.

**F11 — MEDIUM — route states not fully justified** (§3).
* Stream A R-CV needs a qualification (taboo constants effectively unvalidated).
* R-SAND "validated" rests on (c)/(d) controls. Downgrade it to IMPLEMENTED or re-validate.
* B: "5–9×" → 4.42–9.35× with the baseline caveat; R3 G5 → "—".
* C1a:
  * C1LR_ROUTE_SUMMARY.md:40-41 and THEOREM_LR.md:3 claim VALIDATED_NON_TARGET with G6 unmet;
  * the real-kernel status now depends on C1b and REVIEW_RLR_R1, which are outside this review;
  * label it pending review.

**F12 — MEDIUM — leakage, R2.4 / N3 residue (an instance other than incidents 01/02/03).**
* **Where.** EXCLUSION_308.md:418 (§e item 2) and C2A_ROUTE_SUMMARY.md:88-89 (on which C2A :25 depends) re-label
  C7's committed E2 family ceiling as lying "at e_hi(308)" and compare it with 308's committed A0*. A0X/PROGRESS.md:17
  labels the ceiling's drift as 308's right endpoint.
* **Rules broken.** This is the endpoint-sharing attribution that amendment 2 R2.4 forbids. It is also the
  juxtaposition that review M N3 asked to remove, which was fixed only at :137.
* **Information content: nil for the sign of X308.** The ceiling is not a bound on Λ (review M §3.2; EXCLUSION D6).
  No number was computed. There is no ledger line.
* **Action:**
  * re-word all three as "no committed ceiling at e_lo(308) exists";
  * move the D2 row's withdrawn-label note to the incident file;
  * the coordinator decides whether a PROXY_EXPOSURE line is due.

**F13 — MEDIUM — leakage, incident-01 residue in the dependency graph (S8).**
* **The contradiction.** `graph/K5_TAIL_DEPENDENCY_GRAPH.md` §3 is headed "no tail weights, no route factors" (:102).
  Yet row :119 gives TPT-G's over-charge factor as an explicit formula in (x0, ρ), and row :125 gives the LR synthetic
  ratio.
* **The shares beside them.** The same document's node table quotes the committed tail shares of exactly those
  terms, with the route names in the adjacent column: N23 :81 and N24 :82 for the order-3 and order-4 Taylor terms,
  and N17 :75 for the A0 part, whose complement is the A1/A2 part.
* **Same-row case.** Row N31 (:89) puts the committed tail share of C5-T's gain beside "superseded in strength by TPT
  (TPT-D)". That row is a one-sided estimator of a new route's tail effect.
* **Why the retraction was incomplete.** Incident 01 retracted one sentence. Its scope check (INCIDENT_01 consequence
  5) missed these rows.
* **Severity.** Nothing was computed. TPT's tail use is already BLOCKED. For LR (closure-only, review running), the
  pairing is a latent proxy.
* **Action:**
  * move the "Dom" values into a separate history file with no route columns;
  * delete the TPT remark in N31;
  * keep §3 target-free;
  * the coordinator assesses whether the incident-01 ledger count should rise.

**F14 — MEDIUM — amendment 2 R2.3's latent-proxy list is incomplete.** These artifacts carry validation-drift Λ values
of the frozen CUSUM model (H = 5, K = 1/2, atom (0, 0)) and are not listed:
* `streams/A_306/common/certs/ARL_SUB.json`: a certified lower bound on E_a[τ] at e = 3, which by Theorem M T-LO is a
  certified lower bound throughout the band. This is review M N5's "lower bounds from 3". The same applies to
  TABOO_SUB (identical weights), `common/runs/V_A.json`, `V_B.json`, `validation/A306_CV_VALIDATION.json`, and the
  values quoted in THEOREM_CV.md §7.3.
* Float Λ at e ∈ {1/2, 1, 3}: `A306_MECHANISM.json`, `A306_PFLAT.json`, `mechanism/MECHANISM_STUDY.md` and
  `MECHANISM_TABLES.md`.

No juxtaposition with tail numbers was found. Stream A was committed after amendment 2 (980c5961 vs 07ab6b94).
* **Action:** a stricter-only amendment listing these files. Report them by content class only in handover text.

**F15 — LOW — ledger class.**
* `a306_reproduce_A.py` does Lemma Dv′ r2 arithmetic on each 306 supply's own constants. TARGET_QUARANTINE allowed[1]
  says to log that as HISTORICAL_DECOMPOSITION.
* It logs HISTORICAL_READ instead. That is the only class that `log_execution` (`ov_quarantine.py:123-126`) exempts
  from LEAK_FLAG, so the exemption is keyed on free text. The run's notes disclose this.
* The arithmetic stays within each supply (sub-review A), which is compliant with forbidden class 4.
* **Action:** reconcile the class vocabulary between the preamble and the config.

**F16 — LOW — timestamps.**
* `QUARANTINE_AMENDMENT_1.json` `written_utc` 18:40Z is later than its commit (17:52:48Z).
* `QUARANTINE_AMENDMENT_2.json` `written_utc` 2026-09-28T20:20Z is later than its commit (2026-09-27T20:13:39Z).
* B's PROGRESS.md times are not clock times.
* Temporal-integrity (G7) records must be commit-consistent. **Action:** errata notes; do not edit the frozen files.

**F17 — LOW — README layout** lists `streams/F_indep/` (empty and untracked) and `OVERNIGHT_FINAL_REPORT.md`. The
latter is absent at 23475bee; an untracked draft appeared as this review ended and was not reviewed.

**F18 — LOW — unguarded helpers** whose callers are guarded:
* `mech_study.box_upper_rows` / `box_lower_rows`, `cv_search.screen`;
* `lr_fsm.identity_checks`, `block_enclosures`, `build_block_cert`;
* the b307 Hermite helpers;
* `b307_lower_front.py:101`, which loads the whole cover (incl. 305–309) without `guard_path`, though only cells 11–44
  are used.

Defence in depth only.

## 6. Required before any route is called FREEZE_READY or the handover is written

1. F9, F10, F11 and F12: registry, cross-route and A0X wording.
2. F13 and F14: the graph and amendment-2 hygiene.
3. F1–F4: governance tools and artifacts regenerated at the final HEAD.
4. F5–F7: controls re-planted through the code, or their evidence claims withdrawn.

None of these requires a target evaluation.
