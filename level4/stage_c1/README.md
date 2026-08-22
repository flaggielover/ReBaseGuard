# ReBaseGuard Level 4 — Stage C.1

**Confirmatory Sensitivity Evaluation.** A *separate* experiment, not a revision
of Stage C.

> **Stage C remains `STAGE-C-PARTIAL`, because its preregistered criterion C6
> failed.** Nothing here changes that. Stage C.1 asks a better-defined question
> with new seeds and reports its own decision.

| Entry point | Contents |
|---|---|
| [`STAGE_C1_PROTOCOL.md`](STAGE_C1_PROTOCOL.md) | frozen and hashed **before** any confirmatory outcome |
| [`../reports/STAGE_C1_CONFIRMATORY_REPORT.md`](../reports/STAGE_C1_CONFIRMATORY_REPORT.md) | the report and the decision |
| [`../reports/STAGE_C1_LEDGER.md`](../reports/STAGE_C1_LEDGER.md) | Stage C.1 ledger (Stage C untouched) |
| [`results/sizing_decision.json`](results/sizing_decision.json) | the sizing rule and what the smoke run showed |

```bash
bash level4/stage_c1/reproduce.sh
```

## What was tested

Stage C's C6 compared **raw** detection delays across policies whose in-control
run lengths differ by 1.7x. A detector that alarms constantly always posts short
"delays", change or no change, so that comparison could not answer the question
it was asked. Stage C.1 preregistered

```text
R_Delta(rho) = E[tau_Delta | rho] / E[tau_0 | rho]
D_Delta      = R_Delta(RBG) - R_Delta(fresh),   margin epsilon = 0.05
```

and tested non-inferiority of the certificate-aware policy to fresh-only at
`Delta in {0.25, 0.5, 1.0, 1.5}`.

## Integrity measures

* the protocol was **hashed before any confirmatory data existed**, and a test
  re-hashes it on every run;
* **new seed families** (`20260931` smoke, `20260901` confirmatory, `20260902`
  adversarial), none used by Stage A, B, C or the Claude Science work; tests
  assert the streams are uncorrelated with Stage C's;
* `rho` is **imported verbatim** from the Stage C policy module, which a test
  confirms contains no Stage C.1 identifier or outcome;
* the detection simulator is the Stage C one, **unmodified**; a test asserts it
  still reproduces the frozen Stage A chain bit-for-bit at `Delta = 0`;
* the sizing rule and ladder were recorded **before** the smoke run, and the
  chosen rung was applied identically to every policy and shift;
* a wording guard fails the build if the report ever claims C6 passed, claims
  superiority or optimality, or makes a sample-efficiency claim. The guard is
  insensitive to hyphenation and markdown emphasis, and has its own meta-tests
  proving it still fires on affirmative violations.

## What is not claimed

* not that C6 passed, was corrected, or was superseded;
* not superiority — `D` is indistinguishable from zero at the two smallest
  shifts, so **non-inferiority** is what was established;
* not optimality, and not universal improvement;
* **no sample-efficiency claim**: under the frozen convention every `rho < 1`
  policy still draws the fresh block each cycle;
* nothing certified — every Stage C.1 number is Monte Carlo.
