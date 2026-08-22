# Stage F — integrity and freeze audit

Every value below was read from the repository during this audit, not copied
from a prior report.

## 1. Frozen protocol hashes

| Stage | Protocol | Expected | Verified |
|---|---|---|---|
| C | `level4/stage_c/STAGE_C_PROTOCOL.md` | `36bd6ba03a20b7f8…` | **MATCH** |
| C.1 | `level4/stage_c1/STAGE_C1_PROTOCOL.md` | `7b45c091229387e2…` | **MATCH** |
| D | `level4/stage_d/STAGE_D_PROTOCOL.md` | `925adecf08c72343…` | **MATCH** |
| E | `level4/stage_e/STAGE_E_PROTOCOL.md` | `974487019f57c7c3…` | **MATCH** |

## 2. Pre-commitment hashes

| Note | Expected | Verified |
|---|---|---|
| `D2_3_STEP_PRECOMMIT.md` | `7b7a54c64f4c8633…` | **MATCH** |
| `D2_5_PRECOMMIT.md` | `fb6272ef839d7f3b…` | **MATCH** |
| `D3_REGULARITY.md` | `9eafbcd25870a19e…` | **MATCH** |

These matter because each predicted its own stage's outcome: `D2_3_STEP_PRECOMMIT`
predicted the D2.3 failure mode, and `D3_REGULARITY` A5 predicted the `t3`
estimand disagreement — both before the data existed.

## 3. Stage decisions

| Stage | Decision | Verified |
|---|---|---|
| L1–3 | `CLOSED` | **MATCH** |
| B | `STAGE-B-CLOSED-RIGOROUS-PERIOD2` | **MATCH** |
| C | `STAGE-C-PARTIAL` | **MATCH** |
| C.1 | `STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY` | **MATCH** |
| D | `STAGE-D-PARTIAL` | **MATCH** |
| E | `STAGE-E-PARTIAL` | **MATCH** |

## 4. Protocol deviations

**Zero** deviations recorded in any stage. Stages C, D and E each carry a
`PROTOCOL_DEVIATIONS.md` recording clarifications and implementation
corrections, all made before the outcomes they could have influenced, and each
stating explicitly that no criterion, tolerance or decision rule was changed.

## 5. Historical artifacts untouched by Stage F

Verified by adversarial check **F3** against
`results/stage_f_start_marker.json`: no file under `level4/stage_a`,
`level4/src`, `level4/stage_b`, `level4/stage_c`, `level4/stage_c1`,
`level4/stage_d`, `level4/stage_e`, `closure/` or `rebaseguard-proof/` has a
modification time later than the marker.

## 6. Level 1–3 verification transcript

```
$ bash scripts/verify_level_1_3.sh --quick
[1/6] Lean environment      toolchain: leanprover/lean4:v4.34.0-rc1
      PASS  axiom audit clean; final theorem elaborates
            @hasDerivAt_rebaseguard_cusum
[5/6] Arb certificate full-replay audit
      PASS  certificate full replay: status PASS, Gamma_lower > 2,
            continuum residual replayed
            "Gamma_lower": "3.9243482005828971281857775466050952672958374023437500…"
            "Gamma_upper": "27.849382127546703280529527546605095267295837402343750…"
            regenerated audit_report.md is byte-identical to the stored one
[6/6] Numerical sanity checks
      PASS  regression suite: 90 passed
      PASS  certificate arithmetic and cross-check consistency
            margin above 2: 1.92434820058289712818577754660509526729583740234375
RESULT: ALL CHECKS PASSED (0 skipped, explicitly allowed)
```

## 7. Level 4 verification

```
$ bash scripts/verify_level_4.sh
… Stage B decision : STAGE-B-CLOSED-RIGOROUS-PERIOD2
   Stage C decision : STAGE-C-PARTIAL (failed: C6)
   Stage C.1        : STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY
   Stage D decision : STAGE-D-PARTIAL   (D2.3 FAIL; D2.5 MATHEMATICAL, NOT
                                         OPERATIONAL; D3.2-t3 AMBIGUOUS; D4 NOT RUN)
   Stage D adversarial: 12/12
   Stage E decision : STAGE-E-PARTIAL   (0 of 3 H-E5; closure unreachable)
   Stage E adversarial: 14/14
LEVEL 4 VERIFICATION OK
```

## 8. Stage F adversarial suite

**First run: 11 / 18** — preserved permanently at
`results/adversarial_f_FIRST_RUN.json`. All seven failures were the absence of
Stage F artifacts not yet written; the three integrity checks (F1, F2, F3) and
the test-accounting check (F13) passed on that first run. No criterion was
weakened between runs; the suite is byte-identical.

## 9. Classification of every discrepancy found

| Discrepancy | Classification |
|---|---|
| No pre-specified Level-4 closure taxonomy | **benign** — documented absence, drives the fallback taxonomy |
| `staged_task_ranking.csv` MANDATORY ambiguity | **benign** — resolved conservatively; verdict robust either way |
| Novelty review artifacts not persisted | **documentation / provenance gap**, not a protocol violation |
| 2026-08-21 gate recommended against the period-2 route | **benign** — a strategic recommendation not followed; no result is contradicted, and Stage B completed items 8–9 of that same ledger |

**No protocol integrity violation and no scientific artifact mutation was found.**
