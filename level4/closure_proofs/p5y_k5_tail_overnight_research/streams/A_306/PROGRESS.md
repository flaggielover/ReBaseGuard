# Stream A (cell 306) — progress log

Binding: PREAMBLE Q1–Q8, S1–S8 (S8 received mid-task: no route/non-target factor next to committed tail numbers;
checked — nothing written before S8 combined them; all documents below keep committed history in separate sections).

| step | status | artefact |
|---|---|---|
| read preamble, quarantine, graph_B (b), key sources | DONE | — |
| historical A reproduction (HISTORICAL_READ) | DONE, PASS | audit/a306_reproduce_A.py -> validation/A306_HISTORICAL_A_REPRO.json |
| mechanism study (non-target, float) | DONE, PASS (R1: 3 class-(a) controls + 2 checks + exact cross-check; the earlier '4 NCs' was wrong) | mechanism/mech_*.py -> validation/A306_MECHANISM.json, mechanism/MECHANISM_TABLES.md |
| common-theorem route: theorem, verifiers, validation | DONE, PASS | common/ -> validation/A306_CV_VALIDATION.json |
| disagreement audit document | DONE | CELL306_I1_I2_DISAGREEMENT_AUDIT.md |
| route summary | DONE | A_306_ROUTE_SUMMARY.md |

## Notes as they arise
* Reproduction: Dv' r2 on each supply's own constants reproduces committed A exactly (C2 -> C2_D5 A_exact and C12-R2
  control; I2 -> C12-R2 target, using C11R's OUTWARD-ROUNDED C_T record). Branch labels: I1 (C1, C2) tau/D_lo; I2 Abar.
* Mechanism (non-target only): p-flat families (I2's w = A - B m is one) cannot separate tau from the whole-kernel
  value; linear family needs positive m-drift; D5/P32 box loss grows as the m-drift shrinks relative to box+panel width.
* Proposition PF (p-flat ceiling) proved and checked: every p-flat Khat-supersolution has tau = C_T >= L'(0), an
  m-arm ARL equal to E_a[tau] to 5-6 figures at e = 1, 3; 18/18 p-flat LP values respect it, p-dependent families
  break it (validation/A306_PFLAT.json). Explains review note N6 structurally.
* Audit Parts A, B written; mechanism/MECHANISM_STUDY.md written. Next: Part C/D, common route.
* (resumed after rate-limit stop) Theorem CV verifiers V_A (exact) and V_B (decimal) ran on 6 valid + 7 planted
  certificates at [3, 49/16]: all valid ACCEPTED by both with identical value strings, all planted REJECTED by both;
  sandwich contains float truth; synthetic divided-difference bounds sound (5 non-vacuous, 5 vacuous at delta=1e-3).
  validation/A306_CV_VALIDATION.json verdict PASS. A trial search at depth 4/16 panels gave a vacuous D_SUPER
  (f(a) > 1); the search was re-run at depth 5/32 (C11R's configuration) before any verification.
  CORRECTION (R1, review F5): the depth-5 re-run did NOT cure the vacuity; D_SUPER still has value > 1, so the D
  sandwich's upper side is the trivial D <= 1. The "5 refutations" count was class (c) and is withdrawn.
* Marker `# ov-quarantine: historical-read ...` added at a306_reproduce_A.py:27; static scan: 0 findings in A_306,
  file listed SANCTIONED (TARGET_INPUT_PATH). Script computes no Gamma, no mixed supply, no per-term decomposition.
  (Scan shows an unrelated finding in validation/build_validation_index.py -- not this stream's file; not touched.)
* Remaining: THEOREM_CV section 7, audit Parts C/D, A_306_ROUTE_SUMMARY.md.
* DONE. Disclosures: unlogged smoke tests (Nystrom timing at e = 1/2, 1, 3; LP timing at e = 1/2, 1; verifier smoke
  test at [3, 49/16]; the synthetic DD check) ran only at declared non-target drifts / synthetic fixtures before the
  logged runs; two early cv_search attempts crashed before producing any certificate (no ledger line); cv_search has
  two ledger lines (depth-4 trial, depth-5 run), both before any verifier ran.
* Final scan: 0 findings in streams/A_306; a306_reproduce_A.py SANCTIONED. Ledger: 8 A_306 lines, 0 target
  evaluations, no LEAK_FLAG.

## R1 repair (REVIEW_GLOBAL_INTEGRITY_R1: §1.1 C-2..C-6, F3, F5, F11, F18) -- done
* C-2 refutation list: withdrawn from the verdict (kept as a labelled illustration); its operational content is
  carried by class-(a) plants P1, P6, P7, P8 through both verifiers.
* C-3 "0.9 LB2 refuted": withdrawn; re-planted as an INVALID enclosure (d + 1/20 as a sub-solution) rejected by the
  exact check 10/10 (guaranteed), gating the DD part.
* C-4 PF plant: now run through the Khat screen (rejected at 3/3 drifts, margin -1/1000 as PF predicts), gating.
* C-5 NC2 shrink: replaced by NC2' localized planted defect (caught at its own node; twin passes); NC1/NC4
  relabelled CHECK1/CHECK4.
* C-6: two class-(d) controls in a306_reproduce_A.py withdrawn (a through-code plant would need a target
  perturbation); mixed-supply refusal kept.
* F5/F11 taboo coverage: new TABOO_SUPER_T (point {3}, Khat LP, weight distinct from ARL_SUPER) accepted by both;
  skip branch fires 2 panels in both and is load-bearing (same weight as ARL_SUPER rejected by both); lower drop
  fires 68 panels on TABOO_SUB; plants P8 (taboo value below certified lower side) and P9 (C_T_lower claim high)
  rejected by both. Khat sub-solution search reproduced ARL_SUB's weight byte-for-byte -> no distinct taboo lower
  certificate claimed (file deleted; SEARCH_LOG_T.json keeps the record).
* R-CV and R-SAND downgraded to IMPLEMENTED (qualification needed): 4 of 6 constants covered (no D1/D2 kind),
  D upper side vacuous, taboo lower branch not distinct.
* F18: guard_drift added to mech_study.box_upper_rows/box_lower_rows and cv_search.screen (guard verified to refuse
  an in-band call).
* F3: `literal-ok` removed from a306_reproduce_A.py (path line and CELL_KEY line); scan lists lines 1, 44, 53 as
  SANCTIONED; route summary's "0 findings" wording corrected.
* Amendment 2 R2.1: audit Part C made qualitative (it previously quoted non-target float ratios in a document that
  also quotes committed 306 numbers); latent-proxy notices added to MECHANISM_STUDY.md and THEOREM_CV.md section 7.
* Re-runs: a306_reproduce_A (PASS), mech_study (PASS; tables identical except control lines), mech_pflat (PASS),
  cv_search taboo, cv_validate A/B/assemble (PASS; pre-repair runs kept as runs/V_*_pre_R1.*).
