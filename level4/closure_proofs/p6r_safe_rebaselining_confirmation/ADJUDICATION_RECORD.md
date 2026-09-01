# Independent adjudication of P6 — record

```text
FINAL_P6_VERDICT = PARTIAL
T6-B              = EXACT_VALID
T6-C              = VALID_WITH_NARROWER_ASSUMPTIONS
SCIENTIFIC_CORE   = SURVIVES
CURRENT_CLOSURE   = REJECTED
```

This file is the P6R namespace's record of the independent Codex adjudication of
the original P6 campaign. **It is written to be read against, not edited.** No
statement in it is softened, and no later P6R result may be used to reword it.

**Provenance, stated plainly.** The verdict block above and the defect list
below are reproduced as they were relayed to this session in the P6R
instruction. The primary adjudication document itself was **not** supplied to
this session, so this record is a faithful transcription of what was relayed and
not a copy of the source artifact. An adjudicator holding the original should
check this file against it; any divergence is this file's error, not the
source's.

---

## 1. Standing of the original campaign

The original campaign at `level4/closure_proofs/p6_safe_rebaselining/` is now
**historical evidence**. It is preserved byte-for-byte. Nothing in P6R edits it,
and nothing in P6R may be arranged so as to make the original execution appear
retroactively compliant. Its own first-party classification was
`P6 = CLOSED_CANDIDATE`; the independent verdict is `PARTIAL` and its closure is
`REJECTED`.

## 2. The four blocking defects

| # | defect | what it invalidates | P6R repair |
|---|---|---|---|
| **B1** | **`B2*` violated frozen TUNE/EVAL selection.** The fixed-`rho` baseline was chosen as the grid member minimising the objective *on the EVAL table*, and re-chosen on REPLAY | the headline comparison itself: the bar was selected on the data it anchored | `select.py` rule **S1**: TUNE-only selection on a frozen `0.01`-spaced grid, written to a frozen artifact **before** any P6R EVAL run. A second control at the adjudication-identified `rho = 0.25` is carried as well, and the headline must survive against whichever control is less favourable |
| **B2** | **The preregistered statistical procedure was not executed.** The preregistration named 10,000-resample BCa with normal intervals beside it, ratios bootstrapped as ratios, and BH-FDR over a declared family; the campaign reported 4,000-resample percentile intervals | every reported interval and every verdict label | `stats_r.py` implements the named procedure exactly, and `tests/test_p6r_stats.py` asserts each element is *executed*, not merely available. **The original 4,000-resample artifacts are not replaced**; P6R writes new artifacts |
| **B3** | **`C1` temporal precommitment could not be independently established.** Nothing was committed, so the claim that the protocol predated the data rested on the campaign's own account | the pre-registration status of every gate | Checkpoint A: the precommit package is committed and pushed **before** any confirmation EVAL runs, and the commit SHA is the temporal anchor the original lacked |
| **B4** | **`G-E` contained an ordering defect.** The protocol required baseline `Coll` to be seen, the threshold written, and only then SAW's `Coll` computed; both were produced in one pass and inspected together | `G-E`'s pre-commitment status | P6R does not re-litigate `G-E`. `Coll` is a **reported diagnostic with no threshold** in the repaired protocol, declared as such in advance, and the original defect stands recorded |

## 3. Material non-blocking qualifications

Recorded in full, unsoftened. Each is binding on P6R's language.

| # | qualification | binding consequence for P6R |
|---|---|---|
| **Q1** | **T6-C holds under narrower assumptions than it was stated with.** The scalar Jensen formula is not claimed unchanged for adaptive `k` | `THEOREM_SCOPE.md` states T6-C for **fixed `k`** only. All headline SAW-M cells use fixed `k`, so T6-C is exact for the actual headline setting and **not** for the broader adaptive-`k` wording. No theorem for adaptive `k` is manufactured |
| **Q2** | **The cost language was not supported.** `C_fresh = k 1{rho<1}` is an *acquisition* count and was reported with claims it does not license | renamed **fresh-sample acquisition cost**; the only permitted primary claim is equality of newly acquired samples per update. "SAW reuses more", "SAW is cheaper", "SAW has lower effective fresh contribution cost" are **forbidden** unless the repaired baseline and the measured sensitivity actually support them in the cell being reported. Three accountings are reported: acquisition count, proportional contribution, quadratic/effective contribution |
| **Q3** | **Calibration was not uniformly sound.** Convergence, `s1` sample counts, floor activity and the status of the final large-pass refit were not reported per cell | `audit.py` reports all five per cell. **"All cells converged" is false and is not claimed**: 6 of 8 converged; `cusum_m2` and `sr_m3` did not. `s1` rests on 0-3653 observations depending on cell. The final refit was **not** followed by another fixed-point update. Primary-cell `s1` stability may **not** be used to excuse unstable secondary cells |
| **Q4** | **`Delta = 0.5` established no coherent aggregate adaptive advantage** | predeclared as a **limitation**, not as a result to optimise away. SAW-M is **not** altered to target `Delta = 0.5` |
| **Q5** | **`Delta = 2` tail claims are inferentially unresolved below the event floor** | `Dtail(100)` at `Delta = 2` is reportable only if the 200-event floor is met in **both** arms; `Dq95` is the declared fallback. The sample size may **not** be increased after inspecting the repaired EVAL result except through a separately preregistered power-extension campaign |
| **Q6** | **"Detector transfer" was the wrong description.** No no-recalibration transfer experiment was run | P6R says **separately calibrated replication across CUSUM and SR**, everywhere |
| **Q7** | **"Full initialization robustness" was the wrong description** | P6R says **post-burn-in robustness to alternative initialization**. Cycle-1 behaviour is reported separately as descriptive evidence |
| **Q8** | **The Jensen diagnostic was `sigma(V_hat)`-restricted.** Binning on the plug-in measures its calibration, not the achievable gap | the restricted diagnostic is retained and **explicitly labelled restricted**; a direct realized one-step risk comparison on `U^2` is added, with its formula precommitted in `onestep.py` before execution. The plug-in is **not** claimed to be the full oracle `F`-measurable optimizer |
| **Q9** | **Novelty was over-scoped** | `NOVELTY_SCOPE.md` uses the conservative independent wording verbatim: algorithmic **NOT ESTABLISHED**, theoretical **NOT ESTABLISHED**, formulation **PLAUSIBLE**, integration **PLAUSIBLE**. No upgrade without a genuinely stronger independent literature audit |

## 4. What survives

`SCIENTIFIC_CORE = SURVIVES`.

* **T6-B is `EXACT_VALID`.** The closed-loop invariant law, uniform geometric
  ergodicity and all positive invariant moments for a memoryless admissible
  policy with `rho_max < 1` stand as an exact theorem. P6R changes nothing in it
  except to state its policy-class scope more explicitly.
* **T6-C is `VALID_WITH_NARROWER_ASSUMPTIONS`.** For fixed `k` it is exact, and
  fixed `k` is the setting of every headline cell.
* **SAW-M itself is unchanged.** P6R imports the method, the chain and the
  frozen detector from the adjudicated `rebaseguard_p6c` package rather than
  re-implementing them, so the object under confirmation is the object that was
  adjudicated.

## 5. What P6R is not

* Not a reinterpretation of `PARTIAL` as `CLOSED`.
* Not an edit of the original campaign.
* Not an expansion of scope after seeing results.
* Not a novelty upgrade.
* Not the closure decision. The next independent reviewer owns that.
