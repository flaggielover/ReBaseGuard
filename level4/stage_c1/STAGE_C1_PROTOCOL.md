# ReBaseGuard Level 4 — Stage C.1 Protocol

## Confirmatory Sensitivity Evaluation

**This document is frozen before any confirmatory outcome is generated.** Its
SHA-256 is recorded in the Stage C.1 report and in
`results/protocol_hash.json`. Smoke sizing runs use a disjoint smoke-only seed
family and are explicitly permitted by §8 below; they may inform the replicate
count through the rule stated in §8 and nothing else.

---

## 1. Relation to Stage C — read this first

Stage C is **not** amended, corrected or relabelled by this document.

> **Stage C = `STAGE-C-PARTIAL`, because the preregistered criterion C6 failed.**
> That statement is historical and stands.

Stage C.1 is a **new experiment** asking a **better-defined question** with
**new seeds**. It cannot make C6 pass, and no wording in Stage C.1 may suggest
that it does.

### Chronology (mandatory, repeated in the report)

1. Stage C preregistered C6 as a **raw** cross-policy detection-delay criterion.
2. C6 **failed** at `Delta = 0.25` and `Delta = 0.5`.
3. C6 **remained failed**; the Stage C decision reflects it.
4. Post-hoc diagnosis (`CRITERION_C6_DIAGNOSIS.md`) showed the raw cross-policy
   comparison was confounded: the policies have very different in-control
   operating points (cycle ARL 85.2 vs 50.0, a factor of 1.7).
5. A baseline-normalised response metric was proposed in that diagnosis.
6. **Stage C.1 preregisters that metric here, before any new data.**
7. Stage C.1 uses entirely new seeds.
8. Stage C.1 reports its own decision, separately.

---

## 2. The confirmatory question

> Does the certificate-aware ReBaseGuard policy preserve a meaningful response
> to genuine distribution shifts **relative to its own in-control operating
> regime**, rather than obtaining stability by making alarms generally slower?

---

## 3. Policies (fixed; not re-optimised)

| Label | `rho` | Role |
|---|---|---|
| **fresh** | `0` | non-inferiority **reference** |
| **RBG** | `0.02979584394902044` | the Stage C certificate-aware policy, `delta = 0.2`, conservative `Gamma` upper endpoint |
| **full** | `1` | **diagnostic only**; never the non-inferiority reference |
| `0.25`, `0.30` | exploratory | performance context only; **must not affect the Stage C.1 decision** |

`rho_RBG` is taken verbatim from `level4/stage_c/src/policy.py`. It is **not**
re-derived, re-tuned or re-optimised, and no Stage C.1 outcome may reach it. A
test enforces this.

Note: Stage C evaluated the 6-dp rounded grid value `0.029796`. Stage C.1 uses
the **exact** policy value `0.02979584394902044`; the difference is `4e-9` in
`rho`, far below Monte Carlo resolution, and is recorded rather than hidden.

---

## 4. Primary metric — baseline-normalised detection response

```text
R_Delta(rho)  =  E[tau_Delta | rho]  /  E[tau_0 | rho]
```

* `R` near 1 — the shift produces little acceleration relative to that policy's
  own in-control alarm rate;
* smaller `R` — the shift accelerates detection strongly relative to baseline.

This separates *"long in-control run because the detector is stable"* from
*"long in-control run because the detector is blind"*.

**This is not a classical standardised ARL quantity** and is not claimed to be
one. It is a ratio of two expectations under the same policy, and its only
interpretation here is the relative one above.

**Estimator (fixed):** ratio of means, not mean of ratios.

```text
R_hat = mean_r(num_r) / mean_r(den_r)
```

where for replicate `r`, `num_r` is the mean stopping time over that replicate's
post-change cycles in the `Delta` arm, and `den_r` is the mean stopping time
over the identically-indexed cycles in the `Delta = 0` arm run with the **same
seed**. Uncertainty: nonparametric percentile bootstrap resampling **replicates**
(never cycles), recomputing the ratio on each resample.

---

## 5. Primary confirmatory hypothesis

**H-C1.** The certificate-aware ReBaseGuard policy is **non-inferior** to
fresh-only in baseline-normalised detection responsiveness.

```text
D_Delta = R_Delta(RBG) - R_Delta(fresh)
```

**Non-inferiority margin, fixed now: `epsilon = 0.05`** in normalised-response
units.

**Primary criterion:** for **every** preregistered `Delta`, the **upper 95%
confidence bound** of `D_Delta` is **strictly below `epsilon = 0.05`**.

* Shifts: `Delta ∈ {0.25, 0.5, 1.0, 1.5}` — all four, no subsetting.
* This is an intersection–union test: every shift must pass, so no multiplicity
  adjustment is applied or needed (the procedure is conservative by
  construction).
* `epsilon` will **not** be changed after seeing results.
* Point estimates and full intervals are reported for every `Delta` **whether or
  not the criterion passes**.

Because RBG and fresh share seeds, `D_Delta` is a **paired** contrast; the
bootstrap resamples replicate indices jointly across policies and arms.

---

## 6. Secondary criterion — absolute-delay guard

The primary metric is normalised and could in principle conceal absurd absolute
delays. So, descriptively, for each `Delta`:

```text
Q_Delta = E[tau_Delta | RBG] / E[tau_Delta | fresh]
```

**Guard: `Q_Delta <= 1.10`.**

This is **secondary and descriptive**. Its failure does not by itself overturn
the primary H-C1 verdict. But if absolute delay were catastrophically worse
despite normalised non-inferiority, Stage C.1 **must not** claim practical
success. Raw and normalised outcomes are reported side by side.

---

## 7. Full-reuse diagnostic

Full reuse is **not** the non-inferiority reference. It is used to test the
mechanism seen in Stage C: if `R_Delta(full) ≈ 1` across shifts, then full reuse
alarms nearly as fast with no change as with one. That must be described as

> **poor discrimination between in-control and shifted regimes**

and never as "high sensitivity". Short raw delay with a short in-control run
length is not good detection.

---

## 8. Design, seeds and sample size

**Seed namespace (mandatory, disjoint).** Every seed used anywhere in the
repository was audited: `{1234, 1729, 2024, 2026, 4242, 5150, 8080, 31337,
90210, 20260820, 20260821, 20260822}`. Stage C.1 uses

| Purpose | Master seed |
|---|---|
| smoke sizing (non-confirmatory) | `20260931` |
| **confirmatory** | `20260901` |
| adversarial independent rerun | `20260902` |

none of which appears above. A test draws from the Stage C seed and each Stage
C.1 seed and asserts the streams differ.

**Replicate structure.** Stage C's detection design gave one change event per
replicate, so a per-replicate ratio was impossible there. Stage C.1 therefore
uses many change events per replicate, via the **existing, unmodified**
simulator (`n_changes`):

```text
burn_in  in-control cycles
then K blocks, each: 1 detection cycle  +  (recovery + spacing) cycles
```

Per replicate, `num_r` / `den_r` average over that replicate's `K` detection
cycles in the `Delta` / `Delta = 0` arms.

**Sizing rule, fixed now and applied symmetrically.** From smoke-only seeds,
choose the smallest `(N replicates, K events)` on a prespecified ladder such
that the bootstrap standard error of `D_Delta` is `<= 0.010` (one fifth of
`epsilon`) at **every** `Delta`, subject to `N >= 100`. The same `(N, K)` is
then used for **every** policy and **every** shift. Replication is never
increased for cells that are close to passing.

**Statistical unit: the replicate.** Never the cycle. All intervals are 95%
percentile bootstrap over replicates. Policies and arms share seeds (CRN), so
all contrasts are paired and naive independent-cell standard errors are not used.

---

## 9. Shift protocol (unchanged from Stage C)

`Delta ∈ {0.25, 0.5, 1.0, 1.5}`, plus the `Delta = 0` arm as the denominator.

Frozen semantics preserved exactly: the detector (`k = 1/2`, `h = 5`, `m = 1`,
inclusive post-update alarm, shared innovation), the change-insertion convention
(a shift of `Delta` at a cycle boundary is exactly `e -> e - Delta`, because
`e = R - mu`), burn-in, monitoring initialisation, and the reference update rule.
**The simulator is not modified.** A test asserts it still reproduces the frozen
Stage A chain bit-for-bit at `Delta = 0`.

---

## 10. Sanity checks (before interpreting anything)

| ID | Check |
|---|---|
| A | fresh Stage C.1 results reproduce Stage C's fresh arm within independent Monte Carlo uncertainty |
| B | `rho_RBG` exactly matches the Stage C policy value |
| C | full reuse still shows degraded in-control behaviour |
| D | no policy-specific code path alters detector semantics |
| E | the `Delta = 0` arm returns the expected in-control behaviour |
| F | every ratio uses **that policy's own** in-control denominator |

---

## 11. Adversarial tests (all reported, pass or fail)

independent-seed rerun; CRN on/off; replicate count halved; burn-in variation;
ratio-estimator variant (ratio-of-means vs mean-of-ratios); raw-delay comparison
retained; baseline-normalised comparison retained; no outcome-dependent `rho`
selection; no access to Stage C outcomes from policy code; no shift cell dropped
after inspection.

---

## 12. Decision rule (fixed now)

Exactly one of:

* **`STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`** — H-C1 passes at *every*
  preregistered `Delta`; sanity checks A–F pass; no catastrophic absolute-delay
  problem; independent-seed and adversarial checks pass.
* **`STAGE-C1-MIXED`** — the normalised criterion passes only for a subset of
  shifts, or the absolute and normalised conclusions conflict materially, or
  sensitivity is clearly shift-dependent.
* **`STAGE-C1-FAILED`** — RBG is materially less responsive than fresh under the
  preregistered normalised criterion, or the experiment fails important
  reproducibility/adversarial checks.

No fourth status.

---

## 13. Prohibitions

* No sample-efficiency claim of any kind. Under the frozen convention every
  `rho < 1` policy still draws the fresh block each cycle, so there is nothing
  to claim. Stage C.1 concerns **sensitivity only**.
* No claim that C6 passed, was corrected, or was superseded.
* No claim that ReBaseGuard is universally better or optimal.
* No Stage C.1 Monte Carlo result may be labelled `RIGOROUS-CERTIFIED`; that
  status belongs to the Stage B deterministic theorem alone.
* `rho` is never selected using confirmatory outcomes.
* No shift is dropped after inspection.
