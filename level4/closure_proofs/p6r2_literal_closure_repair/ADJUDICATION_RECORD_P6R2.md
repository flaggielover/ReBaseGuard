# Independent adjudication of P6R — record

```text
FINAL_P6_VERDICT        = PARTIAL

SCIENTIFIC_CORE         = SURVIVES
T6_B                    = EXACT_VALID
T6_C                    = VALID_WITH_NARROWER_ASSUMPTIONS
BASELINE_SELECTION      = VALID
STATISTICAL_ANALYSIS    = MATERIAL_DEFECT
TEMPORAL_PRECOMMIT      = VALID
POST_ANCHOR_CORRECTION  = DISCLOSED_NONBLOCKING_DEVIATION
CALIBRATION             = LIMITED
PRIMARY_EMPIRICAL_RESULT= CONFIRMED
REPLICATION             = CONFIRMED
NOVELTY_STATUS          = NOT_ESTABLISHED
PROTECTED_TREE          = PASS
```

| gate | verdict |
|---|---|
| G1 | PASS |
| G2 | PASS |
| G3 | PASS |
| G4 | PASS |
| G5 | PASS |
| **G6** | **PARTIAL** |
| G7 | PASS |
| G8 | PASS |
| **G9** | **PARTIAL** |
| G10 | PASS |
| G11 | PASS |
| **G12** | **PARTIAL** |

**Provenance.** The verdict block and the blocker list below are reproduced as
they were relayed to this session in the P6R2 instruction. The primary
adjudication document was **not** supplied, so this is a faithful transcription
of what was relayed, not a copy of the source. Any divergence is this file's
error, not the source's.

---

## The three remaining blockers, unsoftened

### GATE 6 — statistical analysis, three distinct faults

* **6A.** The **F3 family was not executed literally.** The implementation added
  an **undeclared extra `Dq95@Delta=0.5` test**. The declaration is "the primary
  metric at `Delta in {0.5, 2}`", with `Dq95` as the declared fallback used
  **only** when `Dtail(100)` is below the 200-event floor. Including both the
  primary and its fallback at `Delta = 0.5`, where the primary was eligible, is
  an undeclared test.
* **6B.** The **`Rdelta` BCa acceleration is incomplete for the two-block
  functional.** The bootstrap resampling across the independent delay and
  in-control blocks was conceptually correct, but the jackknife used for the
  acceleration deleted observations from **only the shorter block**. That is not
  the jackknife of the complete two-sample functional.
* **6C.** The **generic zero-denominator analysis produced invalid favourable
  verdicts.** Mathematically undefined ratios were labelled with finite effect
  verdicts.

### GATE 9 — calibration sensitivity confounded

The official `s1` sensitivity artifact is **confounded**: the variants used
different `policy_id` values and therefore **different RNG streams**, so the
measured movement mixes the parameter perturbation with Monte Carlo path
differences.

### GATE 12 — authoritative JSON contains invalid labels

The generated authoritative JSON contains **56 invalid favourable verdict
labels** for mathematically undefined zero-denominator comparisons
(52 EVAL + 4 REPLAY). A downstream enumeration artifact was added, but the
primary JSON itself was left false.

---

## What P6R2 is, and is not

**Is:** a post-adjudication **deterministic / statistical repair over frozen
P6R raw evidence**, confined to statistical post-processing, statistical result
artifacts, calibration-sensitivity methodology, tests, and reporting.

**Is not:** a new campaign, a new algorithm, a rerun of TUNE selection /
confirmation EVAL / REPLAY, a retune of SAW-M, a change to the primary estimand,
the closure thresholds, the twelve gates, T6-B, T6-C, or the novelty wording.

The nine passing gates are **not** reopened. `POST_ANCHOR_CORRECTION` remains a
`DISCLOSED_NONBLOCKING_DEVIATION` and is not re-litigated.
