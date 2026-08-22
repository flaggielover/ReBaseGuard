# Stage D — failures, diagnosed and left visible

Every entry records a criterion that was **not met**. No criterion in this file
was rewritten, no tolerance was widened, and no failure was converted into a
pass. Where a failure has a diagnosis, the diagnosis is stated *and the failure
still stands*.

---

## F1 — D2.3 derivative correspondence: **FAILED** at the pre-specified step

**Criterion (frozen, `925adecf…`):** central finite difference of the actual
induced map at `rho = 1` agrees with `1 − Gamma_m` within 3 combined SE.

**Result:** `0 / 8` grid points agree at the pre-committed primary step
`h = 0.05`. Discrepancies run from `+0.798` (17.0 combined SE) at `m = 1` to
`+0.033` (7.3 SE) at `m = 100`. **D2.3 is recorded as FAILED.**

### Diagnosis: `O(h^2)` central-difference truncation, predicted in advance

`notes/D2_3_STEP_PRECOMMIT.md` (sha256 `7b7a54c6…`), written **before any
induced-map data existed**, recorded this exact failure mode:

> the map is steep at small `m` (`F'(0) ≈ −14.9` at `m = 1`), so the `O(h²)`
> truncation error of the central difference may exceed 3 combined SE even when
> the identity holds exactly. If the primary step fails while the step sequence
> shows the discrepancy shrinking as `h → 0` at the expected `O(h²)` rate, that
> is a finite-difference truncation artifact, not a refutation — and it will be
> reported as a D2.3 failure *with* that diagnosis attached.

The step sequence behaves as predicted. Observed convergence order
`p = log2(disc(h) / disc(h/2))`:

| m | disc(0.10) | disc(0.05) | disc(0.025) | p(.10/.05) | p(.05/.025) | Richardson disc | /SE |
|---|---|---|---|---|---|---|---|
| 1 | 2.9161 | 0.7981 | 0.1863 | 1.87 | 2.10 | −0.0176 | −0.16 |
| 2 | 2.4610 | 0.6935 | 0.1696 | 1.83 | 2.03 | −0.0050 | −0.05 |
| 5 | 1.9049 | 0.5349 | 0.1322 | 1.83 | 2.02 | −0.0021 | −0.03 |
| 10 | 1.2801 | 0.3637 | 0.0842 | 1.82 | 2.11 | −0.0089 | −0.20 |
| 20 | 0.6797 | 0.1911 | 0.0463 | 1.83 | 2.05 | −0.0020 | −0.08 |
| 50 | 0.2650 | 0.0735 | 0.0218 | 1.85 | 1.76 | +0.0045 | +0.32 |
| 75 | 0.1719 | 0.0448 | 0.0148 | 1.94 | 1.60 | +0.0048 | +0.40 |
| 100 | 0.1259 | 0.0332 | 0.0093 | 1.92 | 1.84 | +0.0013 | +0.12 |

Mean observed order **`p = 1.938`** against the exact central-difference value
`2`. The discrepancy is **positive at every `m` and every step**, i.e. one-signed
— a bias, not noise. Richardson extrapolation from `h = 0.025` and `h = 0.05`
agrees with `1 − Gamma_m` to within **0.40 SE at every `m`**, maximum
`|discrepancy| = 0.0176` at `m = 1`.

### What this does and does not license

* **D2.3 is FAILED.** It enters the decision rule as a failure. Under the frozen
  rule this removes `STAGE-D-CLOSED-GENERALIZED` and
  `STAGE-D-NONGAUSSIAN-PARTIAL` from reach, since both require D2 to pass.
* The evidence is **consistent with** `F'_{rho,m}(0) = rho(1 − Gamma_m)` holding
  and the estimator, not the identity, being at fault. It does **not** establish
  the identity: Richardson agreement is numerical extrapolation, which the
  protocol forbids treating as a rigorous asymptotic result.
* The Richardson values are a **truncation diagnostic**. They were declared as
  such before the run and are not substituted for the primary estimate.
* The honest one-line summary: *the pre-specified test failed; the failure is
  explained by a known property of the estimator rather than by the hypothesis,
  and the hypothesis remains unconfirmed at Stage D.*

### Why the step was not simply made smaller

Re-running at `h = 0.0125` and reporting *that* as the primary result would be
re-tuning an estimator after seeing a `Gamma` — explicitly forbidden by
`STAGE_D_PROTOCOL.md` §8. The primary step stays `h = 0.05` and the verdict
stays FAILED.

---

## F2 — Adversarial A11 (outcome-blind code guard): **FAILED on first run, then fixed**

**First run: FAIL.** The guard reported six hard-coded outcome values in
`src/adversarial_d.py`: `15.8544`, `17.3198`, `72.19`, `1.036719`, `1.4037`,
`465.5`.

**Diagnosis: the checker matched its own search list.** Every hit was in the
single line that *defined the values to search for*, and `adversarial_d.py` was
inside its own scan set. No scientific module contained any measured outcome.
The failure was a defect in the check, not in the code under test.

**Fix.** The literal list was removed. The guard now **derives** the outcome
values from the confirmatory results files at 4 and 6 significant figures, and
exempts itself from the scan — holding measured values is precisely a checker's
job. After the fix the guard scans a larger set of values than the original
hard-coded six, so it is **stricter**, not laxer, and it passes.

**Why this is not a tolerance being widened.** No threshold moved. The check's
question ("does any executable scientific module contain a measured outcome?")
is unchanged; only the mechanism for obtaining the list of outcomes changed,
from retyped literals to values read from the data. Both runs are recorded, and
the pre-fix artifact is what the first run produced.

**Status:** A11 FAILED as originally written; **PASSES** as corrected.
Final suite: **12/12**.

---

## F3 — D3 assumption A4 (square-integrability of the stopped score sum): **LOW-POWER CHECK**

`notes/D3_REGULARITY.md` A4 proposed comparing the normal SE against the
batch-mean SE per family, treating disagreement as a symptom of a failure of
square-integrability. Observed ratios (batch / normal):

| family | ratio |
|---|---|
| gaussian | 1.229 |
| t10 | 1.160 |
| t5 | 1.191 |
| t3 | 1.351 |
| contam0.05 | 0.618 |
| contam0.1 | 0.847 |

**This check has too little power to conclude anything.** At `N = 1,000,000`
with a batch of `250,000` there are only **4 batches**, so the batch-mean SE has
3 degrees of freedom and ratios anywhere in roughly `[0.5, 1.6]` are ordinary
sampling noise. The Gaussian control — where A4 certainly holds — shows 1.229,
comparable to `t3`'s 1.351.

**Recorded honestly:** A4 is **neither confirmed nor refuted** by this check.
It remains **UNPROVED**, as `D3_REGULARITY.md` labelled it before the run. The
check is reported rather than dropped, with its power limitation stated, and it
is not used to support any claim in either direction.
