# P6R2 pre-repair record

```text
STATUS AT WRITING = PRE-REPAIR.  No repaired derived artifact has been produced.
NATURE            = POST-ADJUDICATION deterministic/statistical repair over
                    FROZEN P6R raw evidence.  NOT preregistered before the
                    original P6R EVAL, and not presented as such.
SOURCE P6R HEAD   = 73ecad84620e71b68db60612a7001707a2cbd741  (independently reviewed)
CHECKPOINT A      = fcc1355715426531c431e9390c9f12d1bad9b97c
CHECKPOINT B      = 185bda0f63da57162309111b0ff02215f6e805d1
```

This record is committed **before** the repaired artifacts are generated. It is
not a preregistration of a scientific claim — the science is frozen and already
adjudicated — it is a statement of exactly which implementation defects are
being repaired, with what operations, and which tests must pass.

Why a post-adjudication repair is admissible here:

* no new EVAL data are generated;
* no baseline is reselected and no sample size is increased;
* no algorithm is retuned and no estimand is changed;
* the repair addresses **literal implementation and artifact defects** that an
  independent reviewer identified.

---

## 1. Frozen inputs

`precommit/frozen_inputs.json` records the SHA-256 and byte length of every
consumed file: **37 files** — the 13 P6R per-replicate `.npz` arrays, the 12
scalar JSONs, both analysis JSONs, both confirmation manifests, the precommit
anchor, the undefined-ratio enumeration, the four precommit artifacts, the
frozen protocol, the P6R confirmation report, and the frozen P6 calibration.

**The original P6 and P6R artifacts are byte-preserved and are not modified.**
P6R2 consumes them read-only and writes corrected derived artifacts into its own
namespace under new file names.

## 2. Intended repair operations

### R1 — literal F3 *(Gate 6A)*

The frozen declaration is `REPAIRED_PROTOCOL.md` section 6:

> **F3** — the `Delta`-scope family: **the primary metric** at
> `Delta in {0.5, 2}`; BH `q = 0.10`; sub-floor cells are **excluded** from the
> family and labelled.

with section 7 declaring, for `Delta = 2`, that "`Dtail(100)` is inferentially
unresolved unless the 200-event floor is met in both arms; **`Dq95` is the
declared fallback metric**".

The literal family is therefore built by this rule, per `Delta` cell:

```text
take the PRIMARY metric Dtail(100)
if BOTH arms clear the 200-event floor:  include Dtail(100); do NOT include Dq95
else:                                    exclude Dtail(100), labelled
                                         INSUFFICIENT_TAIL_EVENTS, and include
                                         the declared fallback Dq95 in its place
```

No metric other than `Dtail(100)` and its declared fallback may enter F3. The
repair regenerates F3 from the frozen arrays, lists every included and every
excluded test with the reason, and recomputes raw and BH-adjusted p-values.
**The repaired family may not be used to make SAW-M look better**; the
interpretation is reported unchanged or changed, whichever the numbers give.

### R2 — correct two-block BCa acceleration for `Rdelta` *(Gate 6B)*

`Rdelta` is a functional of **two independent empirical blocks**:

```text
block A : the delay run,        n_A replicates, arrays  a_num (method), b_num (control)
block B : the in-control run,   n_B replicates, arrays  a_den (method), b_den (control)

theta = ( mean(a_num) / mean(a_den) ) / ( mean(b_num) / mean(b_den) )
      = ( mean(a_num) * mean(b_den) ) / ( mean(a_den) * mean(b_num) )
```

The bootstrap estimand is **unchanged**. Only the acceleration is repaired, from
a one-block jackknife to the complete two-sample jackknife:

```text
for each i in block A:  theta_(A,i)  = theta with replicate i deleted from A, B intact
for each j in block B:  theta_(B,j)  = theta with replicate j deleted from B, A intact

U_(s,i) = (n_s - 1) * ( mean_i theta_(s,i) - theta_(s,i) )      (centred within block s)

accel = (1/6) * [ sum_s n_s^-3 sum_i U_(s,i)^3 ]
              / [ sum_s n_s^-2 sum_i U_(s,i)^2 ]^(3/2)
```

This is the standard multi-sample BCa acceleration and it **reduces exactly** to
the existing single-block formula when one block carries no influence — a
property asserted by test. Both leave-one-out families have closed forms, so the
cost is `O(n_A + n_B)`.

Verification required: agreement with a **brute-force** recomputation on a small
synthetic fixture, and a test showing the old one-block shortcut and the
corrected two-block calculation **differ** when the omitted block carries real
influence.

### R3 — first-class zero-denominator handling *(Gates 6C and 12)*

At the **source** of the analysis pipeline, not downstream. When the control
mean of a ratio is exactly zero the comparison is mathematically undefined and
the emitted record must be:

```json
{ "status": "UNDEFINED_ZERO_DENOMINATOR",
  "relative_effect": null, "bca_interval": null, "normal_interval": null,
  "p_value": null, "p_adjusted": null, "verdict": "NO_CLAIM" }
```

with **JSON `null`, never `NaN` or `Infinity`**, and strict standards-compliant
JSON output. Such a record may never enter a BH family and may never support a
claim. All **52 EVAL + 4 REPLAY** previously-mislabelled cases must appear as
first-class undefined results in the corrected artifacts, and a ledger must
enumerate them.

The old invalid P6R JSON **remains historical and unchanged**; P6R2 writes
corrected replacement derived artifacts.

### R4 — clean common-random-number calibration sensitivity *(Gate 9)*

**SAW-M is not recalibrated and no shipped constant changes.** Only the
confounded sensitivity artifact is replaced.

The defect is that the variants used different `policy_id` values and therefore
different RNG streams. The repair fixes the stochastic paths:

* the raw innovations of cycle `j` of replicate `r` are drawn from a generator
  seeded deterministically by `(cell, r, j)`, and the post-alarm fresh draw from
  a matching stream;
* **every variant sees the identical innovation sequence in every
  (replicate, cycle)**; the only thing that differs is the perturbed calibration
  constant, propagating through the chosen `rho`.

This is cycle-level common random numbers — the "per-(replicate, cycle)
substream" scheme the P6 statistical design named as the stronger coupling
option. It is a *diagnostic* driver, clearly labelled, used for no primary claim,
and it reuses the **frozen** detector step function.

Declared variants, all eight calibration cells: `s1 x 0.5`, `s1 x 2.0`,
`s1 := s0`, against the shipped baseline. Reported: mean `rho`, reference `Rms`,
`Arl0`, absolute and relative changes.

Carried forward unchanged and **not reinterpreted**: which cells use the `s1`
fallback; the number of `tau < m` events; the number of observations informing
`s1`; convergence status (**6/8 converged; `cusum_m2` and `sr_m3` did not**);
final-refit drift (**the final refit is not a verified fixed point**); floor
activity; `rho_max` activity.

The artifact is named so that it is unmistakably a corrected CRN / fixed-path
sensitivity analysis, and it **does not claim to prove calibration convergence**.

## 3. Tests that must pass

1. the exact F3 member set equals the frozen declaration;
2. no undeclared fallback metric enters F3 when the primary is eligible;
3. the two-block `Rdelta` jackknife matches brute force on a fixture;
4. the two-block and one-block accelerations differ when the omitted block has influence;
5. the two-block formula reduces to the one-block formula when it should;
6. a zero denominator yields `UNDEFINED_ZERO_DENOMINATOR`;
7. a zero denominator yields JSON `null`, never `inf`/`nan`;
8. corrected JSON parses under strict JSON (no `NaN`/`Infinity` tokens);
9. an undefined result never enters BH;
10. an undefined result's verdict is `NO_CLAIM`;
11. all 56 previously invalid ratios are repaired;
12. CRN sensitivity variants share identical random paths;
13. `policy_id` / RNG identity cannot confound the parameter sensitivity;
14. non-converged calibration cells remain reported as non-converged;
15. original P6 and P6R artifacts remain byte-unchanged;
16. protected Stage A-F / P1-P5 remain unchanged.

## 4. What is explicitly NOT touched

SAW-M; the calibration constants; the frozen TUNE-selected `rho` values; the S1
rule; the primary estimand; the closure thresholds; the twelve gates; T6-B;
T6-C; the novelty wording; historical P6; historical P6R; Stage A-F; P1-P5. No
TUNE selection, confirmation EVAL or REPLAY run is repeated, and no sample size
is increased. The nine passing gates are not reopened.
