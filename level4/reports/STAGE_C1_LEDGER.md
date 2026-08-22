# ReBaseGuard Level 4 — Stage C.1 Result Ledger

Statuses are defined in `level4/src/rebaseguard_level4/ledger.py`.
`NEW-NUMERICAL` and `CANDIDATE` entries are Monte Carlo findings and
are **not** proofs. `FROZEN-*` entries are Level 1–3 results quoted
here unchanged. `RIGOROUS-CERTIFIED` means the analytic lemmas are
proved and **every** approximation between the true mathematical
object and the computed one is explicitly bounded — not merely that
interval arithmetic was used somewhere.

| ID | Status | Statement | Evidence |
|---|---|---|---|
| `C1-METHOD-DEFINITION` | **METHOD-DEFINITION** | Stage C.1 preregisters the baseline-normalised detection response R_Delta(rho) = E[tau_Delta\|rho]/E[tau_0\|rho], the paired contrast D_Delta = R_Delta(RBG) - R_Delta(fresh), the margin epsilon = 0.05, the shift set {0.25,0.5,1.0,1.5}, the ratio-of-means estimator and the decision rule, all frozen before any new outcome was generated. | `level4/stage_c1/STAGE_C1_PROTOCOL.md`<br>`level4/stage_c1/results/protocol_hash.json` |
| `C1-SEEDS` | **METHOD-DEFINITION** | Stage C.1 uses seed families 20260931 (smoke), 20260901 (confirmatory) and 20260902 (adversarial), none of which appears in Stage A, Stage B, Stage C or the Claude Science work. | `level4/stage_c1/tests/test_stage_c1.py` |
| `C1-CONFIRMATORY-NUMERICAL-HC1` | **CONFIRMATORY-NUMERICAL** | H-C1 (non-inferiority of ReBaseGuard to fresh-only in baseline-normalised response) holds at every preregistered shift: Delta=0.25: D=-0.00241, upper95=+0.01358; Delta=0.5: D=-0.00083, upper95=+0.01410; Delta=1: D=-0.01219, upper95=-0.00059; Delta=1.5: D=-0.01751, upper95=-0.00920; all upper bounds lie below epsilon = 0.05. | `level4/stage_c1/results/findings_confirmatory.json` |
| `C1-CONFIRMATORY-NUMERICAL-Q` | **CONFIRMATORY-NUMERICAL** | The secondary absolute-delay guard holds at every shift: Q_0.25=1.0147; Q_0.5=1.0163; Q_1=0.9977; Q_1.5=0.9705, all at or below 1.1. | — |
| `C1-CONFIRMATORY-NUMERICAL-FULLREUSE` | **CONFIRMATORY-NUMERICAL** | Full reuse shows poor discrimination between in-control and shifted regimes: Delta=0.25: R=1.0180; Delta=0.5: R=1.0437; Delta=1: R=1.0574; Delta=1.5: R=0.8781. R exceeds 1 at three of four shifts, i.e. a genuine shift makes it SLOWER to alarm than no shift. | — |
| `C1-STAGE-C-UNCHANGED` | **OPEN** | Stage C remains STAGE-C-PARTIAL because its preregistered criterion C6 failed. Stage C.1 is a separate experiment answering a better-defined question with new seeds; it does not alter C6. | `level4/reports/STAGE_C_METHOD_REPORT.md`<br>`level4/stage_c/notes/CRITERION_C6_DIAGNOSIS.md` |
| `C1-NULL-RAW` | **CONFIRMATORY-NUMERICAL** | The raw cross-policy delay comparison is retained and still shows ReBaseGuard slower than full reuse at small shifts, exactly as Stage C reported. Stage C.1 does not overturn that observation; it shows the observation does not mean what a raw reading suggests. | — |
| `C1-OPEN-SCOPE` | **OPEN** | Stage C.1 concerns SENSITIVITY ONLY, at m = 1, k = 1/2, h = 5, Gaussian innovations, shifts at a cycle boundary, and the single certificate-aware rho. No sample-efficiency claim is made or implied. | — |
| `C1-OPEN-EVIDENCE-CLASS` | **OPEN** | Every Stage C.1 number is Monte Carlo simulation and carries no evidence class stronger than CONFIRMATORY-NUMERICAL. | — |

## Notes

- **`C1-METHOD-DEFINITION`** — Protocol sha256 recorded before the confirmatory seeds were used; a test re-hashes the file and fails if it changed.
- **`C1-SEEDS`** — Tests assert the seeds are new and that the generated streams are uncorrelated with Stage C's.
- **`C1-CONFIRMATORY-NUMERICAL-FULLREUSE`** — Described as poor discrimination, never as high sensitivity. Short raw delay with a short in-control run length is not good detection.
- **`C1-STAGE-C-UNCHANGED`** — A test asserts the Stage C decision file still reads STAGE-C-PARTIAL with C6 failed, and that no Stage C.1 text claims C6 passed.
- **`C1-OPEN-EVIDENCE-CLASS`** — The only Level 4 claim with a stronger evidence class remains the Stage B deterministic result (RIGOROUS-CERTIFIED), which concerns the conditional-mean map F_1 and not the noisy recursion. No Stage C.1 entry may ever be labelled RIGOROUS-CERTIFIED.
