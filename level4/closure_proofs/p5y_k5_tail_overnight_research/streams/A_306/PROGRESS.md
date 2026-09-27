# Stream A (cell 306) — progress log

Binding: PREAMBLE Q1–Q8, S1–S8 (S8 received mid-task: no route/non-target factor next to committed tail numbers;
checked — nothing written before S8 combined them; all documents below keep committed history in separate sections).

| step | status | artefact |
|---|---|---|
| read preamble, quarantine, graph_B (b), key sources | DONE | — |
| historical A reproduction (HISTORICAL_READ) | DONE, PASS | audit/a306_reproduce_A.py -> validation/A306_HISTORICAL_A_REPRO.json |
| mechanism study (non-target, float) | DONE, PASS (4 NCs + exact cross-check) | mechanism/mech_*.py -> validation/A306_MECHANISM.json, mechanism/MECHANISM_TABLES.md |
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
  sandwich contains float truth; synthetic divided-difference bounds sound (5 refutations, 5 vacuous at delta=1e-3).
  validation/A306_CV_VALIDATION.json verdict PASS. A trial search at depth 4/16 panels gave a vacuous D_SUPER
  (f(a) > 1); re-run at depth 5/32 (C11R's configuration) before any verification.
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
