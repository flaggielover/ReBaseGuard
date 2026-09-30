# Independent check of the U2 corrected proposition (U2-CP), P309 package 1, formal campaign p5y_k5_cell309_p309_r1
U2_CP_ESTABLISHED

**Conditions U1–U6 (§8) are binding before the freeze relies on U2-CP.** If U4 cannot be met on the frozen drivers, the
outcome becomes U2_UNRESOLVED and the campaign STOPs before the freeze.

**Reviewer.** I am the independent incident-independence reviewer. I wrote `reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`
(sha256 f5ff1d68…, committed at 39ed662c; its line 3 and §8/C7 are preserved verbatim in U2-CP §1). I did not produce
or coordinate the campaign.

**Inputs checked.**
* Brief: `reviews/BRIEF_U2_CHECK_P309.md` (sha256 29bfa9bf…). It was committed at 46533afd and pushed before it was
  issued to me.
* Document under check: `governance/U2_CORRECTED_PROPOSITION.md` (blob 76c6b225, sha256 02a28685…).
* Evidence:
  * `code/u2_structure_check.py` (sha256 f4c1b0b5…) → `evidence/u2/U2_STRUCTURE_CHECK.json` (a4270542…);
  * `tests/test_u2_structure_controls.py` (cc8d0e21…) → `evidence/u2/U2_CONTROLS.json` (15133614…);
  * `code/code_skeleton.py`.
* Owner authority: `governance/OWNER_RULINGS_2_P309_VERBATIM.md`, "OWNER RULING — U2".

**Branch state.** HEAD was 7273b76e when I started and 78bd6a98 when I wrote this. The two intervening commits
(21819c0b, 78bd6a98) touch only the FC2 spec rev. 2, a brief and ledgers. The U2 document, checker, tests and evidence
are unchanged.

**Written.** 2026-09-30, 02:45–03:05Z.

---

## 0. Firewall conduct, executions and ledger

Scratch ledger (named as the brief requires):
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/u2check/U2CHECK_LEDGER.jsonl`.

**Reads.**
* **Consumer files** (`tct_rule.py`, `tc_rule.py`, `c2_d5_forecast.py`, `tail_forecast_r2.py`): read **only** through
  `python3 code/code_skeleton.py py …`.
* **Input files** (`TCT_INPUTS_309.json`, `ADOPTED_TAIL_INPUTS.json`): read **only** through
  `code_skeleton.py json` (key paths and types).
* **Cell-307 files** (`rlr307_stage1.py`, `rlr307_pinned.py`, `rlr307_independent.py`) and overnight `streams/C_308`
  files (`c1b_certpw.py`, `c1b_prov.py`): read **only** through `code_skeleton.py` or AST output.
* **C6 Condition 10:** read through a masked read. It was restricted to the lines containing "Condition 10" (±2) and
  the ranges the U2 document cites (173–180, 418–424, 664–668), plus the preceding condition (650–663). Every number
  with ≥ 2 digits, and every decimal, fraction, exponent and percentage, was masked before display.
* **Everything else read** was in FNS or RNS.

**Executions**, all static; nothing from an analysed file was imported or executed.
* `PYTHONDONTWRITEBYTECODE=1 python3 code/u2_structure_check.py`: exit 0, ok = true.
* `python3 tests/test_u2_structure_controls.py`: exit 0, 11/11 PASS.
* Both scripts rewrote `evidence/u2/*.json`. The reruns differed only in `utc` and `git_head` (4a50aa7b → 7273b76e).
  I restored **both files byte-identical** from copies taken before the runs (sha256 re-verified: a4270542…,
  15133614…).
* **Reviewer scratch scripts** (in the ledger directory):
  * `extra_scan.py`: the checker's own `_scan_module`, an AST scan, applied to four Stage-1 modules the checker does
    not scan;
  * `reviewer_controls.py`: the checker's S1–S4 functions run on planted temp copies of two research-namespace files;
  * `masked_grep.py`: the masked read above.

  These scratch runs are static analyses beyond the two sanctioned scripts. They are **declared here after they ran**.
  Declaring them in advance was not possible, because this file did not yet exist.
* **Ledger time correction.** The first nine ledger lines carry my estimated times. A later append-only line corrects
  them against the clock.

**Nothing else.**
* No git write.
* No file modified except this one. The two evidence files were restored.
* No kernel, no evaluation, no cell.
* The untracked `code/p309_guard.py` and the modified formal `ZERO_TARGET_LEDGER.jsonl` in the working tree are the
  coordinator's concurrent work, not mine.

---

## 1. Verdict in brief

* **U2-CP is established from committed evidence for every component that exists and is pinned**, and for the
  Stage-2 semantics the protocol fixes. Specifically:
  * the Stage-1a producer, gate and verifier;
  * the RLR307 Stage-1 code and its pinned C1B certifier set;
  * the SRK adapter and assembly;
  * the frozen TC-T and C2 clause.
* **The mechanical evidence is correct as far as it goes, but not complete.**
  * S1's identities are the right ones.
  * The checker has two blind spots. I **demonstrated** each with planted defects that pass S1–S4:
    * the binding of SRK's scalars to the input fields (`srk_adapter.fields_for_r`);
    * the B3/B4 selection step.
  * For the **pinned** bytes I closed both by direct reading, and the checker's pin check binds those bytes.
* **The document overstates two points; both need text fixes (U1).**
  * §4.3 says no recorded interval is re-derived. The frozen identity gate rebuilds one, for a pass/fail check only.
  * The heading of §4.4 ("forms no new function of adopted scalars") is literally false. The precise, true claim is
    "no new *form* of adopted scalars".
* **§5 has omissions but no mis-classified load-bearing quantity (U2).**
* **The load-bearing path "as frozen" includes drivers that are not yet written** (FC4 Stage 2, FC5 Stage 1b, the
  per-rung serializer, the FC2 guard and verifier variant).
  * The Stage-2 driver cannot call the frozen `direct` unchanged, because `direct` builds its own TC-T enclosure. It
    will therefore re-express the clause.
  * F-U2-1..3 do not cover this. U4 is the binding condition.
* **The Corollary T boundary** is now factually and mechanically separated for SRK, and it is anchored in committed
  governance text (§5 below). The remaining step is interpretive: that a consumer-level radius over adopted scalars
  is not a "new quantity derived from P3 tail records". The committed record grounds that step but does not state it
  in those words. The owner's ruling has taken that step on this premise.

---

## 2. Task 1: is the criterion Q1–Q5 (§3) faithful?

**Primary text, verified by masked read.** `C6_ADJUDICATION.md:666`: "**No P3 object may be adopted as new scientific
evidence.** All four recovered records are P3 with `admissible_for_NEW_scientific_reuse: false`."
* The continuation (:667–668) concerns *raising* those records. It sets preconditions (Aux5 schema semantics, closing
  the two links that fail by raw bytes). P309 raises nothing.
* The quotations at :175–178 (the tail inputs' standing "belongs to the predecessors' adoption of those bytes
  (ADOPTED_TAIL_INPUTS, TCT_INPUTS, C2–C5 consumption), not to C6") and :420–423 (the recovered bytes are "identical to
  what `ADOPTED_TAIL_INPUTS` names") are accurate.

**Faithful.** Q1–Q3 are exactly the committed examples:
* SC: a new statistic from payloads (`SC_SUPNORM.md:252`);
* RSO: regeneration (`RSO.md:229`);
* CR: new K1 records (`COVER.md:226`).

Q5 restates C6 Condition 10 with the standing that C6 itself assigns (:175–178). Q4 restates the committed reason
given for Corollary T (`PHASE1_RESULTS.md:169`: "tightens a recorded interval with a new quantity derived from the
record").

**Where the criterion is thin or needs saying:**
* **(a) Q1–Q5 is narrower than the literal definition.** The definition is "admissibility of **new** quantities derived
  from P3 tail records" (`READER_B_GOVERNANCE_REPORT.md:43`). Read literally, that could reach any new
  consumer-level value computed from record scalars. Q1–Q5 excludes this by construction.
  * The narrowing is supported by committed text: C6's standing clause includes "C2–C5 **consumption**". Every
    committed U2 example acts on the record itself.
  * It is **not stated** in the committed record in so many words. §3 should say that it is a reading.
* **(b) The only committed source for Q4's boundary is the research coordinator's own text.** That text is
  `PHASE1_RESULTS.md:169`, `ROUTE_MATRIX.md:69` and `ROUTE_SELECTION_RULE.md:29`, written on 09-29 at 13:49–13:52Z,
  before any decoy comparison, but by the party whose route benefits.
  * The document does not cite two committed governance anchors that do not depend on that authorship.
    `READER_B_GOVERNANCE_REPORT.md:25` (relaying ROUTE_AUDIT_R1:328–332): "a route that changes the consumer or other
    inputs is closure-only". `READER_B_GOVERNANCE_REPORT.md:140–145` (relaying C5_ADJUDICATION): "Scientific closure
    under a sharpened sound transport … is permitted, labelled closure-only".
  * Together these show that the programme governs **consumer changes** under U3 (closure-only; the owner set U3 =
    CLOSURE_ONLY) and **record-derived quantities** under U2. The two are orthogonal; RSO, for example, is both.
  * This is the strongest committed support for the boundary and should be added (U5(b)).
* **(c) Reliance on adopted standing should be declared prospectively.** C6's preceding condition (masked read, :663–665)
  requires the successor gate to be "frozen **before** the evidence phases it classifies", and says the
  `already_adopted_exception` "may be retained only if declared prospectively".
  * That condition is addressed to C6's successor gate, not to P309.
  * But U2-CP §4.2 rests on exactly that adopted standing. The freeze should therefore declare it prospectively
    (U5(a)), which §7 already intends by carrying U2-CP into the freeze.

**Nothing is missing that bears on P309.** No committed U2 example covers a quantity P309 forms.

---

## 3. Task 2: the inventory (§5) checked against the code

What I checked:
* the skeletons of `tct_rule` (tail_enclosure, tail_object, sigmas, fG_zero_candidate, atom_constants_generic,
  derived_identity_gate, tail_enclosure_crosscheck);
* `tc_rule` (env4, taylor_bounds, radius, object_half_width, coefficients);
* `c2_d5_forecast` (direct, combine, _atom_independent, load, main);
* `tail_forecast_r2` (adopted_state, pinned, module);
* the RLR307 skeletons;
* the raw `srk_adapter.py` and `srk_assemble.py`;
* the key structure of both input files.

**No load-bearing quantity is mis-classified.** Every load-bearing row is correct in source, role and entry point:
* the TCT scalars, and the order-3 bounds entering through `sigmas`;
* C_upper → Lemma G → `combine`;
* R2_interval, M_R2, R_interval.hi and D_interval.lo in `direct`;
* the cover geometry;
* the registries;
* Γ̄;
* the RLR supplies.

`direct` computes only the frozen clause: the intersection with R2_interval, M = min(M_R2, magnitude), and
Γ = R_interval.hi − e0·D_interval.lo + ρ·x_hi·M.

**Omissions and imprecisions** (U2):
1. **Present-only fields not listed:**
   * the TCT copy of `right`;
   * the per-cell duplicates in ADOPTED_TAIL_INPUTS: `C_upper`, `auxiliary_evidence`, `eps_cell_refined`, `e0`, `rho`,
     `record_sha256`, and the top-level `manifest_sha256`.

   The C2 path reads C_upper and the auxiliary evidence from the **K1 records** (`st['records'][k]`), not from
   ADOPTED_TAIL_INPUTS, which contributes only `cells.<k>.m.<m>`.
2. **candidate_suprema / midpoint_eps** feed σ4 as well as σ3, through the `h:j:3` entries and the cell tower in
   `sigmas`. The row says "→ σ3".
3. **"Loaded and hash-checked, never evaluated" is not exact.** `adopted_state` computes text objects at load
   (`TCm.text_objects`). These are present-only for 309 but are computed, not only loaded.
4. **Gate-only items not listed:**
   * the adapter's ρ-versus-cell-half-width refusal;
   * the adapter's `sup_G = abs_G_at_a = 0` refusal;
   * C2 `main`'s copy of C_upper into the measurement dict (`d['C_upper'] = …`). This is a subscript assignment, but a
     copy, not a derivation.
5. **Quantities that the C2 `main` pattern forms and that must be ABSENT from P309.** They should be listed as
   "absent — must not be computed", because the Stage-2 driver is modelled on that pattern:
   * `requirement` (the required uniform atom-constant reduction) and the gap / material-tightening classification;
   * the C2 feasibility gate's per-cell baseline gaps (`gate['baseline']['gap']`);
   * the `FC.compose` replay gate (the whole cover);
   * `tail_forecast_r2.critical_ratio` and `atom_constant_requirement`.

   These are target-equivalent diagnostics, and several fall in the quarantine's forbidden class (critical constants
   or ratios).
6. **§4.3 conflicts with §5's own row "eps_cell_refined, R2_interval (rebuilt containment) … gate-only".**
   `tct_rule.derived_identity_gate` **does rebuild** an R2 interval (H_at_a ± eps_cell_refined, plus W2) and compares
   it with the record's R2_interval: containment and a tolerance. So §4.3's "No record field or recorded interval … is
   recomputed … or re-derived" is false as written.
   * The rebuilt interval is gate-only (only `['pass']` is used), untightened and not adopted.
   * It is exactly C2's validation.
   * §4.3 must be restricted to the load-bearing path (U1).

---

## 4. Task 3: the mechanical evidence (§6)

**S1 (identities).** These are the right identities, and they are correct. I checked them against the raw
`srk_assemble.py:80, 84–85, 96` and against the masked `tct_rule.fG_zero_candidate` / `tail_object` and
`tc_rule.env4` / `taylor_bounds` / `radius`.
* new3[Γ̄_i := A0·k_i] = A0·(f_G of the zero candidate + ε3), and new4[Γ̄_i := A0·k_i] = A0·Env4 at s_G = 0. Since the
  SRK expressions contain no k symbol, the map Γ̄_i ↦ A0·k_i is injective on their monomials, so the identities
  **determine** new3 and new4 exactly.
* The Γ̄-coefficients equal the k-coefficients: 3s_H, 3s_D, s_F; 6s_H, 4s_D + 4ρs_H, s_F + ρs_D + ρ²s_H/2.
* The Γ̄-free parts A0(σ3 + ε3) and A0σ4 are the k-free parts of A0·f_G and A0·Env4.
* The p-terms and radius are identical to TC-T's.
* s_G = 0 on the path is enforced at runtime by the adapter's refusal (`srk_adapter.py:107-108`).
* **§4.4 is therefore true in this precise sense:** adopted scalars enter rad^SRK only through the frozen linear
  forms, which are the k_i-coefficients and k-free parts of f_G and Env4, together with the unchanged f_H, p1 and p0.
  Only the operator-side multipliers change (A0·k_i → Γ̄_i), under a min with the frozen value.
* **§4.4's heading is too strong.** rad^SRK *is* a new function of the adopted scalars together with Γ̄. It contains
  new products (s_H·Γ̄_1 and so on) and a min, which is piecewise. "No new form of adopted scalars" is true; "no new
  function" is not (U1).

**Could the checker pass on a formula that forms a new function of adopted scalars? Yes, outside the expressions S1
parses.** Reviewer controls (`reviewer_controls.py`, output `reviewer_controls.out`), each run through S1–S4:

| control | planted change | S1 | S3 | S4 | detected? |
|---|---|---|---|---|---|
| RV1 | `fields_for_r`: `sH` := sup_H + delta_H·sup_D | pass | pass | pass | **no** |
| RV2 | `fields_for_r`: `sigma3` := σ3·sup_F | pass | pass | pass | **no** |
| RV3 | `srk_coefficients`: B3 := new3 + s_H·s_D when SRK wins | pass | pass | pass | **no** |

The reasons:
* S1 treats `f["sH"]` as an opaque symbol and never checks where it comes from.
* S2 lists key names only.
* S1 substitutes B3 := A0·f_G and never parses the selection lines (`srk_assemble.py:86-87`).
* The runtime reproduction gate (`srk_adapter.py:103-114`) cannot catch RV1 or RV2 either. s_F, s_D, s_H, σ3, σ4 and
  ε3 do not enter rad_tct separately; they enter only through the frozen f_G and Env4.

In the full `main()` run, the **pins** check would fail on any such edit, because the analysed files must match their
rev. 2b sha256.

**The pinned bytes are correct by reading:**
* `fields_for_r` (`srk_adapter.py:30-36`) reads `sup.F/D/H` exactly as `tail_object` does;
* `sigma3` and `sigma4` come from the frozen object, which `tail_enclosure` fills with the same `sig[r]` values
  passed to `tail_object`;
* `eps3` = `eps_src[3]` (S1's statement-shape check confirms `fG = residual_G + F(meas_r['eps_src'][3])`);
* B3 = min(A0·f_G, new3) and B4 = min(A0·Env4, new4), with None → frozen and ties → frozen.

So U2-CP §4.4 holds for the pinned code. The *mechanical* claim covers only part of it (U3).

**S3 covers what it claims, but narrowly.**
* It scans the Stage-1a modules, `rlr307_{stage1, independent, pinned}` and the C1B_R2 `load_bearing` list.
* It does **not** scan `c1b_float` or `c1b_prov`, although `rlr307_pinned.LOAD_ORDER` loads both. It does not scan
  the guard modules `q309_guard` and `ov_quarantine` either.
* My AST scan of those four found:
  * no consumer imports;
  * `c1b_prov` reads only its own sources and the C1B pin file (skeleton);
  * the two guards name record files only in their deny lists, which is their refusal role.
* The pinned loader (`rlr307_pinned.load_certifier`, skeleton) execs exactly the six pinned C1B files and injects the
  guard.
* The RLR supply (`c1b_certpw.assemble`) uses only certified operator constants. Its κ1 and κ2 are analytic Gaussian
  constants (`c1b_gauss`; `rlr307_independent.kappa_check`).
* The RLR partition is a pure function of the cell interval.
* **U2-CP §4.1 is established.**
* S3 cannot see dynamically built paths or values the driver passes in (U4). `pins_match` omits the rlr307 and C1B
  files (`u2_structure_check.py:353`); they are pinned elsewhere (RLR307_FREEZE, C1B_R2_CODE_PINS) (U3).

**S4 covers what it claims.** `direct` reads the four fields by subscript and assigns none, and the adapter subscripts
no record field. But "no subscript assignment" does not by itself exclude a new derived value. My skeleton reading of
`direct` closes that gap for the frozen clause. S4 does not look at `main` or `derived_identity_gate` (see §3.4, §3.6).

**The planted controls are meaningful but aimed only at the parsed expressions.** C1–C8 are genuine single-defect
controls, and each targets exactly what its check parses. They show the checker can fail. They do not probe its blind
spots (RV1–RV3).

---

## 5. Task 4: the Corollary T boundary

**The facts are now established, mechanically where possible and otherwise by reading:**
* the SRK path reads no record-level field;
* the direct clause reads record fields only by subscript, in the frozen formula;
* adopted scalars enter rad^SRK only through TC-T's own forms;
* Stage 1 is operator-only.

So the S2 part of the line is no longer a matter of judgement. SRK changes a **consumer-level** radius. Corollary T, by
the committed description, re-derives a **recorded** interval.

**The classification is grounded but remains a reading.** The claim is that a consumer-level radius over adopted
scalars, with operator-only multipliers, is not a "new quantity derived from P3 tail records". Committed text grounds
it:
* C6:175–178: standing includes C2–C5 consumption;
* C6:666: the prohibition concerns P3 **objects**;
* READER_B:25 and :140–145: consumer changes are the closure-only (U3) axis, and closure under a sharpened sound
  transport is permitted as closure-only;
* PHASE1:169: Corollary T's U2 reason is the recorded interval.

The literal definition does not say this in so many words. That residual step is interpretive. The owner's ruling
("NOT_TRIGGERED only on the corrected/amended premise") has taken it on this premise, and it is not being
reinterpreted here. **My answer: established as far as committed evidence can establish a classification. The residual
judgement is the owner's and has been exercised.**

---

## 6. Task 5: are F-U2-1..3 sufficient? No.

* **F-U2-1** (pin the checker; QC re-runs it) is insufficient. The checker has the blind spots of §4. It also does not
  analyse any driver, although the drivers are part of the load-bearing path "as frozen".
* **F-U2-2** (cell 309 only) is too weak in form. The driver must not call `main`, `compose`, `requirement`, `classify`,
  `critical_ratio` or `atom_constant_requirement` **at all**, and must not read the C2 gate's baselines. `main`
  evaluates every tail cell.
* **F-U2-3** (the historical control as a hard pre-marker gate) is sound. But it certifies only the TC-T / S_I1 path
  and the input bytes. It says nothing about the SRK-specific reads (RV1/RV2) or the selection step (RV3).
* **Missing obligations.** The driver analysis (U4); the corrected text carried verbatim (U1, U5); the K1-record
  binding (U6).

---

## 7. Status of each U2-CP clause

| clause | status |
|---|---|
| 4.1 operator-only new evidence | **established** (S3 plus reviewer AST scan plus skeletons). The drivers are subject to U4 |
| 4.2 adopted standing, frozen roles | **established** for the pinned path. Needs a prospective declaration (U5a) and the record binding (U6) |
| 4.3 no record-level re-derivation | **established on the load-bearing path only**. The text overclaims (U1) |
| 4.4 new formula, no new form | **established by S1 plus reading**. The heading overclaims (U1). The checker needs completing (U3) |
| 4.5 supply is a min | **established** (`combine`; `rlr307_independent.consumed`; Lemma G via `atom_constants_generic`) |
| "same category as C2's TC-T" | grounded in committed text; interpretive residue adopted by the owner (§5) |

---

## 8. Conditions (binding before the freeze relies on U2-CP)

* **U1 (text, before U2-CP is carried verbatim into any freeze document or grant).**
  * **§4.3:** restrict it to the load-bearing path. State that the frozen `derived_identity_gate` rebuilds an R2
    interval for a pass/fail containment and tolerance check, exactly as C2 did. State that C2 `main` copies C_upper
    into the measurement dict. Neither is load-bearing, tightened or adopted.
  * **§4.4:** replace "forms no new function of adopted scalars" with "forms no new form of adopted scalars: they enter
    only through the k_i-coefficients and k-free parts of the frozen f_G and Env4 and through the unchanged f_H, p1,
    p0; only operator-side multipliers change, under a min with the frozen value".
  * **§3:** state that Q1–Q5 is a reading of the definition anchored in the committed examples and C6's standing
    clause.
* **U2 (inventory).** Complete §5 per §3 items 1–5 of this review, including the "absent — must not be computed" list,
  and carry it into the freeze.
* **U3 (checker completeness, pinned with it).**
  * (a) Bind each `fields_for_r` entry by AST to the corresponding `tct_rule.tail_object` / `tail_enclosure`
    expression.
  * (b) Verify that `srk_coefficients` selects exactly min(old, new), with old = A0·f_G / A0·Env4 and None → old.
  * (c) Extend S3 to the modules actually loaded (`c1b_float`, `c1b_prov`) and to the guard modules, with an explicit
    role whitelist. Extend `pins_match` to the rlr307 and C1B files against their own pin files.
  * (d) Add RV1–RV3 and controls for (b) and (c) to the planted-control suite.
* **U4 (drivers; the binding condition).** Before the freeze relies on U2-CP, the extended checker must pass on the
  **frozen** FC4 Stage-2 driver, the FC5 Stage-1b driver, the per-rung serializer and the FC2 guard / verifier
  variant. It must show:
  * (i) the clause evaluation is AST-equivalent to the frozen `direct` except that the enclosure is 𝓗_SRK, or `direct`
    is called unchanged through a documented injection whose crosscheck semantics are stated;
  * (ii) none of the forbidden calls or reads of §6 (F-U2-2) occurs;
  * (iii) no Stage-1 driver reads a record, measurement, adopted-input or registry file, or passes a record-derived
    value into a producer;
  * (iv) every record-field access is a subscript read in its frozen role.

  QC re-runs it. **If it cannot pass, U2 is UNRESOLVED and the campaign STOPs before the freeze.**
* **U5 (freeze declarations).** The freeze carries the corrected U2-CP verbatim, with:
  * (a) a **prospective** declaration that P3-provenance inputs are used solely under their existing adopted standing
    (C6:175–178; cf. C6's condition requiring an already-adopted exception to be declared prospectively);
  * (b) the governance anchors READER_B:25 and :140–145 (consumer changes are the U3 / closure-only axis; U3 =
    CLOSURE_ONLY is decided);
  * (c) the statement that the classification is a governance reading adopted by the owner's ruling, not a mechanical
    result;
  * (d) this review's NOT_TRIGGERED_WORDING_DISCREPANCY and U2_CP_ESTABLISHED lines.
* **U6 (record binding).** The open manifest item "K1 record manifest path/pin" must be closed so that the K1 records
  P309 loads are exactly those C2 consumed: bytes bound by the frozen loader's manifest hash, and the historical
  control reproducing C2's Γ_exact. No other P3 copy may enter, including C6's recovered files, even if byte-identical,
  under another path.

---

## 9. Out-of-scope observation (for FC2 / FC5, not U2)

**The FC2 specs do not cover the Stage-1b band guard.**
* Stage 1b's certifier calls the injected guard's `guard_drift`. The `Ctx` constructor and `run_point` in
  `c1b_certpw` (skeleton) call it, and `rlr307_pinned.load_certifier` injects the guard as `ov_quarantine`.
* The committed FC2 specs (`fc2/FC2_SPEC.md` §5; `fc2/FC2_SPEC_R2.md`) name only the Stage-1a producer guard
  (`srk_certify.Q`). A grep of rev. 2 finds no Stage-1b, c1b or ov_quarantine term.
* Unless the grant-scoped guard is also injected into Stage 1b, an in-band Stage 1b would raise. By protocol §3 that is
  EXECUTION_INDETERMINATE.
* This is an efficacy and safety item for FC2/FC5 and the qualification review. It is not a U2 finding.

---

## 10. Disclosures

**Exposures.** None to any 305–309 value.
* Consumer code was seen with all numbers masked.
* Input files were seen as key paths and types, with cell keys masked.
* The C6 text was seen with every number of two or more digits masked.
* Cell-307 and C_308-stream files were seen as skeletons or AST output. Module constants shown were masked, or were
  structural: key-name tuples, file hashes, HULL_BITS, the degree ladder.
* Nothing from THEOREM_TCT.md was read.

**Executions.** As in §0: static only, ledgered. The evidence files were restored byte-identical. No git write.

**Writes.** This file only.
