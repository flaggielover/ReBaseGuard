# K4 independent review (P5Y, frozen checkpoint 95b1fd16 @ e5cc5a90)

**K4_ADJUDICATION = ACCEPTED**. The execution followed the frozen procedure, and the executor's result and classification are correct.
**K4_SCIENTIFIC_RESULT = NOT_CLOSED**. The frozen disposition is **K4_INCONCLUSIVE_K1_RECORDS**.
Machine-readable review: `K4_INDEPENDENT_REVIEW.json` (sha256 241953c0dafc02bb92c5320a9bbf2d1e277582b3565a114b47309a816e309dbb).

## Reproduced outcomes (exact rational)
| (D,m) | outcome | chain cells / up to | loose | counterexample |
|---|---|---|---|---|
| CUSUM m=1 | CELLWISE_ALL_CERTIFIED | 189 / 1747613/10000000 | – | – |
| CUSUM m=2 | CERTIFICATE_TOO_LOOSE | 0 | 0,1 | none |
| CUSUM m=3 | CERTIFICATE_TOO_LOOSE | 0 | 0,1,2 | none |
| CUSUM m=5 | CERTIFICATE_TOO_LOOSE | 0 | 0,1,2 | none |
| SR m=1 | CELLWISE_ALL_CERTIFIED | 198 / 2213511/10000000 | – | – |
| SR m=2 | CELLWISE_ALL_CERTIFIED | 191 / 2030461/10000000 | – | – |
| SR m=3 | CELLWISE_ALL_CERTIFIED | 187 / 386967/2000000 | – | – |
| SR m=5 | CELLWISE_ALL_CERTIFIED | 183 / 922449/5000000 | – | – |

No domain cell has R.lo > 0 for any (D,m).

## Checks
- **A. Checkpoint: PASS.** The checkpoint file, its HASH file and the 3 bound sources are byte-unchanged from e5cc5a90 to 5289b6ce (origin/p5y-postk1-frontier).
- **B. Temporal: PASS_WITH_NOTE.**
  - The decision procedure was predeclared at e47e8947 (06:11Z) and frozen at 06:53Z on 2026-09-13.
  - All CUSUM production came after the freeze.
  - 16 genuine SR T4 records were written at 06:26–06:29Z. These are cells 0,4,…,60, which are K4-domain cells. That is after the predeclaration but before the freeze, and the blinding disclosure does not mention them.
  - Nothing shows these records were observed. The amendments made at freeze do not change any outcome.
- **C. Provenance: PASS_WITH_NOTE.**
  - The Lane C re-run from a pristine 5289b6ce copy is byte-identical to the executor's output (82dae9dc).
  - My own copy of the CUSUM tree from vultr-02 verifies under pristine ce7fb933 `verify_closure.py --export-tree`: tree digest 7517199a, manifest 29ad1f9b.
  - The attestation equals the committed one (039e2e1c).
  - The producer-identity clause is satisfied: f9380847 declares identity 3692d0fe, and all 326 records carry it. The clause names the producer by role, not by hash.
- **D. Domain: PASS.** Both domains derived from the hash-bound tables match the records:
  - CUSUM: cells 0..309, last right 2092283/1000000.
  - SR: cells 0..294, last right 40372863/20000000.
  - Every record's e0 and rho equal its table cell exactly. m is always {1,2,3,5}, and detector identity is consistent.
- **E. Reproduction: PASS.** The frozen tool, run in GENUINE mode from a pristine archive, produced report sha 83cabce2, byte-identical to the executor's. The report contains no paths. The frozen tests pass locally (16/16).
- **F. Strict negativity: PASS.** An independent exact recomputation matches every per-cell classification and value.
- **G. Far field: PASS.** The obligation covers (0,2] only, and there is no gap on it. K4 asserts nothing for e>2; that range relies on the P5X-T7(1) licence and K1 sup|R|<2. Literal H2 on (2, ∞) is not covered by K4.
- **H. No relaxation: PASS.** There was one run with no refinement, retry or tolerance. The AppleDouble sidecar files were removed only from the executor's own staging copy, and that staged tree equals the original.
- **I. Disposition: PASS.** Some cells are CERTIFICATE_TOO_LOOSE and none is a counterexample, so the mapping gives K4_INCONCLUSIVE_K1_RECORDS.

## Residual blocker
**CERTIFICATE_TOO_LOOSE** for CUSUM m=2,3,5 at cells 0–2.
- The mean-value widening rho·M_R2 ≈ 7.5–7.9 exceeds |D.hi| (3.73 / 2.53 / 0.94), so the chain is empty.
- Cell 0 contains e=0, where R(0)=0, so it can only be certified through the chain.
- Any tightening would need a new predeclared successor.
