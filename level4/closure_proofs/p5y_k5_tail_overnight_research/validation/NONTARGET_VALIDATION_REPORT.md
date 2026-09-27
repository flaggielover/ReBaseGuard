# Non-target validation report (brief §21)

**Machine-readable companion:** `NONTARGET_VALIDATION_INDEX.json`, produced by `build_validation_index.py` and
regenerated at the final HEAD. It lists every artifact's sha256, schema and summary fields, together with a **leak
scan** of each artifact's content.
* **What the scan detects:** CUSUM m = 5 cells 305–309 as values, keys, lists, text or `index` keys, and drifts
  inside [6/5, 13/5] under drift- or block-like keys, in lists or in "e = …" text.
* **Controls:** 11 planted control shapes, each of which must be flagged, plus a benign control that must not be.
* **Limit:** a JSON leak scan cannot see numbers that are not tied to such keys or texts.

**Validation classes used:**

| class | meaning |
|---|---|
| SYNTHETIC | exact finite-state drift families (`code/ov_fixtures.py`); every quantity is exact, so exact truth is available |
| NONTARGET_DRIFT | the real CUSUM kernel at the declared drifts only: e ∈ {0, 1/4, 1/2, 1, 3}, their mirrors, and small blocks near them |
| NONTARGET_REAL | committed real records of non-tail cells: the lower-front CUSUM cells 11–44, all m |
| HISTORICAL_READ | reproduction of committed historical values under their own supply. One sanctioned script: stream A's A-reproduction. |

**How the validation sets were selected.** Every set was declared before its run. The selection rules were:
* the synthetic seed ranges and configurations are fixed;
* the drifts are the declared list, and the tail band is refused by `guard_drift`;
* the real cells are all 34 lower-front cells, not a subset.

No case was chosen for its similarity to 306–309.

## Per route: correctness, bound validity, controls, reproducibility, cost

| route | cases | correctness / validity | negative controls (through the code path?) | reproducibility | runtime | artifact |
|---|---|---|---|---|---|---|
| TPT (r2) | 12 FSM fixtures; 136 lower-front (cell, m) pairs | Lemma TC-P: 0 pointwise violations. Transport certified sound 12/12. Cap path sound 12/12, with interior splits in 11/12 and 12/12. Independent TC re-derivation reproduces the committed H_TC exactly, 136/136. | **Yes:** code-path plant 12/12; transport plants θ = 1/2, 9/10, 99/100 detected 11, 5, 2; mutants M2, M4, M5 detected 6, 4, 2. The r1 controls were tautological and are withdrawn (review R1 B2). | all JSON pinned to `tpt.py` sha 05cebc9c | 5–120 s | TPT_SYNTHETIC, TPT_R2_VALIDATION, TPT_V3_LOWER_FRONT |
| TPT-B | 24 FSM | 0 violations; 24/24 sound; 24/24 dominated | **Yes:** code-path 24/24; θ controls detected 22, 10, 4 | pinned | 116 s | TPTB_SYNTHETIC |
| LR / RLR (theory, FSM) | 24 FSM seeds (Λ from 2.7 to 8.4); blocks [0, 1/4] | Identities exact. Ordering chain holds 24/24. RLR ≤ Dv′ on equal EXACT inputs 24/24 (with certified ρ only the min is guaranteed; REVIEW_RLR_R2). | **Repaired after global review F7:** the t-flip comparison control is withdrawn and replaced by corruptions inside `moment_totals` (24/24 + 5/5). An A < 0 plant is rejected 24/24, and a mutant checker without the A ≥ 0 test accepts it. The guaranteed-invalid block control is rejected 8/8. | exact | minutes | C1LR_* |
| RLR (real kernel) | e ∈ {0, 1/4, 1/2, 1, 3}; block [1/2, 17/32] | taboo and whole-kernel supersolutions; two-sided D-constants; quadratic certificates checked box by box; all certified; MC (non-certified) consistent | planted invalid certificates rejected. Control N1 was a design error: the "planted" function was a valid supersolution. It is preserved and replaced by guaranteed-invalid controls, which are detected. | exact | block about 246 s; point runs minutes | C1B_* |
| C2b strategy | 30 pointwise runs (5 drifts × N ∈ {10, 20, 40} × whole/taboo); 18 blocks | all certified. Every gap is < 1 % above the float truth at N = 40. The block floor is proved. | 0.97× and 0.999× candidates rejected; notches 10/10; wrong kernel 28/28; FD check of the Hessian bounds (after the domain fix) 0/7200 violations, ×0.05 control 20/20. The sign-flip is not detectable at the atom by symmetry (documented). | exact | 2–300 CPU-s per run | C2B_VALIDATION |
| Theorem M (review numerics) | declared drifts; 13,500 paths | V-mask identity; monotonicity and evenness hold at every resolved comparison | the non-atom start violates the property locally (as predicted); planted V-mask errors caught | MC seeds stated | — | THEOREM_M_REVIEW_NUMERICS |
| Stream B (307) | 64 fixture cells / 320 objects; 34 lower-front cells | all identities and bounds held at every grid point. The lower-front TC arithmetic reproduced 136/136 exactly (regenerated from committed code); a 2⁻⁶⁰ perturbation was detected. | **Repaired after global review F6:** three non-evidence controls relabelled; six class-(a) plants through the code, all firing. A controls register lists the class of every check. | — | — | B307_* |
| Stream D (309): SC, cover, RSO | FSM; Hermite closed form on the real kernel at declared drifts | SC and RSO enclosures 0 violations. Hermite closed form matches C11's kernel 1200/1200. | **Repaired after review D, B1:** arithmetic controls are withdrawn or relabelled. The code-path plants are box-wise soundness checks. The premise-level truth checks are load-bearing: they catch Env4 := 0 and a halved A0 60/60. The enclosure and transport checks are downgraded to weak necessary conditions. | regenerated | — | D309_* |
| Stream A (306): Theorem CV | block [3, 49/16] | two independent verifiers: 7 valid accepted with identical values (including a distinct taboo certificate with a load-bearing skip branch), 9 planted invalid rejected, plus 1 discrimination check. **State: IMPLEMENTED, qualification needed** (the D upper bound is vacuous; 4 of the 6 constants are covered). | **Repaired after global review F5:** the controls go through both verifiers and gate the verdict; the arithmetic controls are withdrawn | exact / directed decimal | — | A306_* |
| Stream A: mechanism | e ∈ {1/2, 1, 3} (float, labelled non-certified) | Proposition PF holds 18/18 | 3 class-(a) controls (p-flat plant through the screen, rejected 3/3; NC2′ node plant; NC3) plus 2 checks | — | — | A306_MECHANISM, A306_PFLAT |

## Weaknesses (stated, not hidden)

* **Tautological or non-guaranteed controls occurred in three streams**, each caught by review or by the authors:
  * TPT r1 (review R1 B2);
  * Stream D (review D B1);
  * C1a and C1b (authors: "slack = 0" and "w·(1 − 2⁻⁶)" were still valid certificates).

  Every repaired control now plants invalidity through the code under test.
  * The global controls-and-leakage review (`reviews/REVIEW_GLOBAL_INTEGRITY_R1.md`) returned **DEFECTS_FOUND**:
    residual class (c)/(d) controls in streams A, B and C1a and in the governance tools, among others.
  * All findings F1–F18 were repaired or recorded (see `ERRATA.md` and the incident residues). A second global review
    was **not** run.
* **No ground truth for the s-profile shape on real data.** On the lower front only s = ρ is anchored externally (TPT
  review N8).
* **The strongest routes' real-cell data paths cannot be validated tonight:**
  * the TC-T tail path's inputs exist only for the quarantined cells;
  * the SC and RSO payloads were never serialized.
* **Theorem M transfer (amendment 2).** Certified Λ bounds at the declared drifts logically bracket the band. They are
  **latent proxies**, and their values are not quoted in any cross-route or handover text.
