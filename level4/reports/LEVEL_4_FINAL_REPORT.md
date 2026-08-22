# ReBaseGuard — Level 4 Final Closure Report

## 1. Exact verdict

> **Level 1–3: `CLOSED`**
> **Level 4: `LEVEL-4-PARTIAL`**

ReBaseGuard fully closes its Level 1–3 core and establishes several
Level-4-caliber theoretical and numerical results, including a rigorous
deterministic period-2 certificate, but does not satisfy the project's
conservatively reconstructed full Level-4 closure requirements.

## 2. Mechanical decision path

Derived by `level4/stage_f/src/make_final_decision.py` from the requirements
table, not asserted:

1. The central Level-4 claim is **not** contradicted and protocol integrity is
   intact (4/4 protocol hashes, 3/3 pre-commitment hashes, 5/5 stage decisions
   unchanged) ⟹ **`LEVEL-4-FAILED` does not apply.**
2. **5 of 16** mandatory requirements are FAIL or OPEN ⟹ **`LEVEL-4-CLOSED`
   does not apply.**
3. `LEVEL-4-CLOSED-WITH-LIMITATIONS` may be used **only if the original
   architecture permits such closure**. Exhaustive search found **no
   pre-specified Level-4 closure criteria and no Level-4 status taxonomy**
   anywhere in the repository ⟹ **not available without inventing the
   requirement after seeing the outcome.**
4. ⟹ **`LEVEL-4-PARTIAL`**: 9 mandatory pass, 2 mandatory partial/negative,
   5 mandatory unmet.

## 3. Why CLOSED is not permitted

Three mandatory items are explicitly unmet and two more are open:

* **`m>1` derivative theorem — FAILED** (Stage D D2.3, 0/8 at the frozen
  primary step `h = 0.05`).
* **`m`–`rho` phase map (D4) — NOT RUN**; the frozen Stage D protocol gated it
  on D2 surviving, and D2 did not.
* **Semi-real external validation — FAILED against its own frozen rule**
  (Stage E, `0/3` tasks met H-E5, 2 required).
* **SR derivative theorem — OPEN**: established numerically, never proved.
* **Prior-art / novelty verification — OPEN**: the review artifact is not
  persisted in the repository.

## 4. Why FAILED is also not appropriate

`LEVEL-4-FAILED` is reserved for a contradicted central claim or lost protocol
integrity. Neither occurred:

* the Lean-checked identity elaborates with a clean axiom audit;
* the Arb certificate replays fully, byte-identical;
* the Stage B certificate reproduces with all four requirements `ok: true`;
* all frozen protocol and pre-commitment hashes match;
* every stage decision is unchanged;
* **zero** protocol deviations are recorded in any stage.

The failures are of *generalization and external validation*, not of the core.

## 5. Requirements reconstruction

Full derivation in `level4/stage_f/LEVEL4_REQUIREMENTS_RECONSTRUCTION.md`.

**No Level-4 closure specification exists.** The Level 1–3 closure report states:
*"Level 4 is not authorized by this document and has not been started"*, and
classifies Level-4 material as `OPEN` (L-09) / `NOT CLAIMED` (L-10). Level 4 was
defined incrementally, stage by stage.

`staged_task_ranking.csv` classifies four Stage-D items as **MANDATORY**. Whether
that means "binding Level-4 requirement" or "Stage-D execution priority" is
**AMBIGUOUS** — the file is titled "Stage D" and sits under a "TASK RANKING"
heading with cost/probability columns (suggesting priority), yet it says
MANDATORY and defines a class "STRETCH / LEVEL-4+" that presupposes a Level-4
boundary. Unresolvable without choosing the convenient reading, so the
**conservative interpretation applies**.

**The verdict does not depend on that choice.** Strict reading: 3 of 4 MANDATORY
Stage-D items FAIL/OPEN ⟹ not closed. Lenient reading: closure then rests on the
frozen per-stage rules — `STAGE-C-PARTIAL`, `STAGE-D-PARTIAL`, `STAGE-E-PARTIAL`
⟹ not closed. **Both readings agree.**

| Requirement | Class | Status |
|---|---|---|
| Level 1–3 closure foundation | mandatory | **PASS** |
| Multi-cycle oracle, reproducible | mandatory | **PASS** |
| Conditional map + derivative correspondence at `m=1` | mandatory | **PASS** |
| `Gamma_CUSUM > 2` rigorously | mandatory | **PASS** |
| Rigorous period-2, deterministic skeleton | mandatory | **PASS** |
| Stability-aware reuse policy + monitoring consequences | mandatory | **PARTIAL** |
| Confirmatory sensitivity of that policy | mandatory | **PASS** |
| SR Monte Carlo derivative | mandatory | **PASS** |
| **`m>1` derivative theorem** | mandatory | **FAIL** |
| **SR derivative theorem (proved)** | mandatory | **OPEN** |
| **`m`–`rho` phase map (D4)** | mandatory | **FAIL (not run)** |
| Operational consequence of the `Gamma_m` crossing | mandatory | **NEGATIVE** |
| Non-Gaussian robustness | strong extension | **PARTIAL** |
| General location-family theorem | stretch | **OPEN** |
| **Semi-real external validation** | mandatory | **FAIL** |
| **Prior-art / novelty verification** | mandatory | **OPEN** |
| Reproducibility of every stage | mandatory | **PASS** |
| Protocol integrity | mandatory | **PASS** |

## 6. Integrity audit

| Stage | Frozen protocol | Hash | Matches | Decision | Deviations | Reproducible |
|---|---|---|---|---|---|---|
| L1–3 | closure package | — | — | `CLOSED` | — | **yes** (ALL CHECKS PASSED) |
| A | Stage A brief | — | — | Gates 4.1/4.2 closed | none | yes |
| B | Stage B brief | — | — | `STAGE-B-CLOSED-RIGOROUS-PERIOD2` | none | yes |
| C | `STAGE_C_PROTOCOL.md` | `36bd6ba0…` | **yes** | `STAGE-C-PARTIAL` | none | yes |
| C.1 | `STAGE_C1_PROTOCOL.md` | `7b45c091…` | **yes** | `STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY` | none | yes |
| D | `STAGE_D_PROTOCOL.md` | `925adecf…` | **yes** | `STAGE-D-PARTIAL` | **none** | yes |
| E | `STAGE_E_PROTOCOL.md` | `974487…` | **yes** | `STAGE-E-PARTIAL` | **none** | yes |

Pre-commitments also verified: `D2_3_STEP_PRECOMMIT` `7b7a54c6…`, `D2_5_PRECOMMIT`
`fb6272ef…`, `D3_REGULARITY` `9eafbcd2…`.

**No historical scientific artifact was modified during Stage F** (check F3,
against a timestamp marker written at Stage F start).

## 7. Level 1–3 foundation

Command: `bash scripts/verify_level_1_3.sh --quick`
Outcome: **`RESULT: ALL CHECKS PASSED (0 skipped, explicitly allowed)`**

* Lean `leanprover/lean4:v4.34.0-rc1`; **axiom audit clean; final theorem
  elaborates** (`hasDerivAt_rebaseguard_cusum`).
* Arb certificate **full replay PASS**; regenerated audit report **byte-identical**
  to the stored one; `Gamma_lower = 3.92434820…`, margin above 2 `= 1.92434820…`.
* 90 regression tests pass.

## 8–13. Stage results

**Stage A** — Multi-Cycle Oracle and conditional-map estimator; Gates 4.1/4.2
closed; three-route derivative correspondence at `m=1`; 290 tests.

**Stage B** — `STAGE-B-CLOSED-RIGOROUS-PERIOD2`. For the **deterministic
conditional-mean skeleton** at `rho=1`, `m=1`: a unique nonzero root of
`H(e)=F₁(e)+e` in `[1.0287243, 1.0447243]`, zero excluded, `min H' = 1.32886`,
multiplier `lambda_2 ∈ [0.10815, 0.83253] ⊂ (−1,1)`.

**Stage C** — `STAGE-C-PARTIAL`. Policy well-defined and safe;
**criterion C6 failed and was left failed**; oracle `rho = 0.3` (MSE `0.70864`)
dominates the policy (`0.94369`) on in-control performance.

**Stage C.1** — `STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`. Preregistered and
hashed before data, new seeds: non-inferior to fresh at every tested shift
(`eps = 0.05`). **Does not make C6 pass** and makes no sample-efficiency claim.

**Stage D** — `STAGE-D-PARTIAL`. D1.1/D1.2/D1.3 **PASS**
(`Gamma_SR = 17.3198 ± 0.0280`; excess `+1.4746 ± 0.0400`); D1.4 **CANDIDATE**;
D2.2 **PASS** (`m* ∈ [50,75]`); **D2.3 FAIL**; D2.5 **MATHEMATICAL, NOT
OPERATIONAL**; D3.2 6/6 frozen / 5/6 normalised with **`t3` AMBIGUOUS**;
**D4 NOT RUN**. Adversarial 12/12 after a diagnosed first-run A11 failure.

**Stage E** — `STAGE-E-PARTIAL`, **`0/3`** tasks met H-E5. Task A: H-E1
**SUPPORTED**, H-E4 **directional contradiction**. Task B: **LOW-POWER**, H-E3
supported at `eps=0.10`. Task C: **E2/E3 UNRELIABLE and excluded**, H-E4
**SUPPORTED** on usable endpoints. Adversarial 14/14.

## 14. Cross-stage synthesis

Full text in `level4/stage_f/SCIENTIFIC_SYNTHESIS.md`.

**CORE.** Alarm-conditioned reuse induces a cross-cycle reference-state feedback
mechanism; in the frozen Gaussian CUSUM setting that mechanism admits rigorous
local and nonlinear analysis, including a certified period-2 structure **of the
deterministic conditional-mean skeleton**.

**GENERALIZATION.** A structurally distinct Shiryaev–Roberts detector reproduces
the strong local stopped-selection feedback numerically at matched `ARL₀`, but
the broader `m`-dependent theorem and phase-map program did not close.

**EXTERNAL VALIDITY.** Semi-real streams behave heterogeneously: reference
distortion can occur without normalised discrimination degradation, and the
stochastic operational behaviour does not mirror the deterministic skeleton.

## 15. Deterministic vs stochastic — the governing distinction

Stage B certifies the **skeleton**. Three independent findings show the skeleton
does **not** govern the stochastic process:

1. 2026-08-21 design ledger, claim 12: "period-2 describes the stochastic long
   run" — **FALSIFIED** (alternation `0.88`, not `1`; 25% of mass near `e*`);
2. its gate recommendation was `PROCEED-ALTERNATIVE-DYNAMICS`, warning against
   "certifying a feature of a skeleton that does not govern the observable
   process";
3. Stage D D2.5, reached independently under a frozen protocol:
   **MATHEMATICAL, NOT OPERATIONAL** — 0/4 metrics peak at `m*`, 4/4 monotone,
   alternation persists above the crossing.

These do not contradict Stage B; Stage B completed items 8–9 of that same
ledger. The theorem is not weakened, and its interpretation is not strengthened.

## 16. Evidence hierarchy

| Level | Results |
|---|---|
| **PROVED / machine-checked** | the differentiation identity and its chain; score identity |
| **RIGOROUS NUMERICAL CERTIFICATE** | `Gamma_CUSUM ∈ [3.9243, 27.8494]`; Stage B period-2 root, uniqueness and multiplier |
| **CONFIRMATORY NUMERICAL** | `Gamma_SR`; SR excess; `m*` bracket; Wald identity; `Gamma_psi` 6/6; Stage C.1 non-inferiority; Stage E Task A H-E1, Task C H-E4 |
| **EXPLORATORY / CANDIDATE** | SR period-2 candidate; Stage E P3 |
| **DESCRIPTIVE** | `gamma_i` decay; naive `Gamma_T` diagnostic |
| **AMBIGUOUS** | `t3` estimand; MANDATORY-label provenance |
| **FAILED / FALSIFIED** | D2.3; Stage C C6; Stage E `0/3`; stochastic period-2; stationary-mass diagnostic; reuse as dominant ARL cause; Stage E Task A H-E4 |
| **UNEVALUABLE** | Stage E Task C H-E1/H-E2 |
| **OPEN** | invariant law; A1; general location-family theorem; SR certificate; detector generality; novelty |

## 17. Strongest defensible claims

1. For the frozen two-sided Gaussian CUSUM, the stopped-selection identity is
   **machine-checked in Lean** and `Gamma > 2` is **certified by outward-rounded
   interval arithmetic**, giving `F₁'(0) < −1` and an interior `rho_c`.
2. The deterministic conditional-mean skeleton at full reuse has a **certified
   period-2 orbit**: unique nonzero root in `[1.0287243, 1.0447243]`, locally
   attracting, multiplier in `[0.10815, 0.83253]`.
3. A **second, structurally distinct detector** reproduces the effect at matched
   `ARL₀`: `Gamma_SR = 17.3198 ± 0.0280`, excess `+1.4746 ± 0.0400`.
4. The stopped gain **decreases with window length** and crosses the `rho_c = 1`
   boundary within a tightly bracketed `m* ∈ [50, 75]`.
5. A **certificate-aware reuse policy** is non-inferior to fresh re-baselining in
   baseline-normalised sensitivity at every tested shift (Stage C.1).
6. **Numerical robustness across six ARL0-matched innovation families.**

## 18. Negative and falsified results

D2.3 **FAILED**; C6 **FAILED**; Stage E `0/3`; Stage E Task A H-E4 **directional
contradiction**; D2.5 **no operational transition**; three 2026-08-21 stochastic
claims **FALSIFIED**; naive `Gamma_T` **fails badly** off-Gaussian (`99.56` vs
`2.60`); D4 **NOT RUN**; Task C's largest apparent effects **excluded** by the
reliability gate.

**Why they matter.** Together they draw the boundary of the result: the rigorous
core is real and narrow; the mechanism does *not* automatically produce
operational consequences; and reference distortion does *not* imply degraded
discrimination.

## 19. Ambiguous / unevaluable

`t3` (frozen estimand PASS `2.5980` vs normalised FAIL `1.2990`); Stage E Task C
H-E1/H-E2 (below the reliability floor); the MANDATORY-label provenance.

## 20. Novelty position and provenance limitation

**Repository fact:** no standalone novelty review is persisted; `Touboul`,
`forgetting`, `post-selection` return **0 files**. The 2026-08-21 document
records that its literature reconnaissance **could not be run**.

**Project-history fact, supplied externally:** later adversarial literature
reviews were performed outside the repository, including a dedicated
adaptive/unknown-parameter SR novelty kill-search covering self-starting/adaptive
CUSUM, post-selection and optional-stopping inference, Touboul–Brette
integrate-and-fire adaptation maps, adaptive/variable-forgetting RLS,
multi-cyclic SR, SR-r / SRP, and non-Gaussian/robust sequential detection; they
reportedly found no direct overlap to the extent searched and classified the SR
direction `SR-NOVELTY-DEFENSIBLE`.

**Approved wording:**

> A later external prior-art search found no direct overlap to the extent
> searched, but the corresponding review artifact is not currently persisted in
> the repository and exhaustive novelty is not established.

This is a **documentation/provenance limitation, not a protocol violation**. The
words *novel*, *first*, *first-ever*, *unprecedented* are **forbidden**.

## 21. External-validity boundary

Semi-real, offline, three streams, one frozen protocol — **not** deployment.
Streams are strongly autocorrelated (ACF(1) `0.718 / 0.832 / 0.792`), one
heavy-tailed, one weekly-seasonal; calibrated thresholds `15.2–36.7` vs the
frozen `h = 5`. Behaviour is heterogeneous and the sign of the discrimination
effect is stream-dependent. **The pre-specified `≥2/3` criterion was not met.**

## 22. Reproducibility

**695 executable tests**, all passing:

| Suite | Tests |
|---|---|
| Level 1–3 | 90 |
| Stage A | 290 |
| Stage B | 46 |
| Stage C | 48 |
| Stage C.1 | 36 |
| Stage D | 72 |
| Stage E | 59 |
| Stage F | 54 |
| **TOTAL** | **695** |


`bash scripts/verify_level_1_3.sh` · `bash scripts/verify_level_4.sh` · plus
`reproduce.sh` in each of `stage_b/`, `stage_c/`, `stage_c1/`, `stage_d/`,
`stage_e/`, `stage_f/`. Every stage is seeded and hashed; Stage E fetches data by
checksum and redistributes nothing.

## 23. Open requirements preventing Level-4 closure

1. `m>1` derivative theorem (D2.3 FAILED);
2. `m`–`rho` phase map (D4 NOT RUN);
3. SR derivative theorem (numerical only, unproved);
4. Semi-real external validation against its own `≥2/3` rule (0/3);
5. Prior-art/novelty verification (artifact not persisted).

## 24. What a future legitimate Level-4 closure would require

Identified, **not undertaken**, and deliberately not named a stage:

1. **A pre-specified Level-4 closure criteria document with a frozen taxonomy**,
   written and hashed *before* further work. Its absence is the root cause of
   this audit's ambiguity.
2. **Confirming `F'_{rho,m}(0) = rho(1 − Gamma_m)` at `m > 1`** with an estimator
   not limited by `O(h²)` truncation — e.g. a score-based derivative estimator —
   pre-registered independently. D2.3 must stay failed as a historical record.
3. **Running D4** under a protocol whose gate does not depend on D2.3.
4. **Proving the SR derivative theorem**, or explicitly reclassifying it as
   numerical-only in a frozen requirements document.
5. **Discharging assumption A1** (differentiation under the expectation for
   non-Gaussian location families) — the binding obstacle to any general theorem.
6. **An external-validation design with adequate cycle counts** on short streams
   without violating the dependence-coverage rule; Stage E's `0/3` must stand.
7. **A persisted, reproducible prior-art audit** with search strategy, databases,
   dates and exclusions recorded in-repo.

## 25. Publication-safe abstract

> We study *stopping-selected recursive reference reuse*: when a sequential
> change detector's reference level is re-estimated from the very observations
> that triggered its alarm, the selection induced by stopping creates a
> cross-cycle feedback in the reference state. For a frozen two-sided Gaussian
> CUSUM (`k = 1/2`, `h = 5`), we machine-check the underlying
> differentiation-under-the-expectation identity in Lean 4 and certify
> `Gamma = E₀[Z_tau T_tau] ∈ [3.9243, 27.8494]` by outward-rounded interval
> arithmetic, yielding a local gain `F'(0) = 1 − Gamma < −1` and a strictly
> interior critical reuse fraction. For the deterministic conditional-mean
> skeleton at full reuse we certify a unique nonzero period-2 root in
> `[1.02872, 1.04472]` with multiplier in `[0.108, 0.833]`. An ARL₀-matched
> Shiryaev–Roberts chart reproduces the effect numerically
> (`Gamma_SR = 17.32 ± 0.03`), which is **two-detector replication and not
> detector independence**. Generalization is incomplete and we report it as
> such: a pre-specified test of the derivative identity for windows `m > 1`
> **failed** under its frozen finite-difference step, and the measured
> `Gamma_m = 2` crossing at `m* ∈ [50, 75]` has **no observable operational
> counterpart** — monitoring metrics vary smoothly through it and alarm
> alternation persists beyond it, so the boundary is mathematical rather than
> operational. Across six ARL₀-matched innovation families the score-based gain
> exceeds 2, which is numerical robustness and **not distribution-free** theory;
> one family is ambiguous between two estimands. On three semi-real streaming
> tasks with pre-specified failure criteria, results were heterogeneous and the
> `≥2/3` external-validation criterion was **not met**: aggressive reuse
> produced decisive reference distortion on one stream yet **no** normalised
> discrimination penalty there. The rigorous core is narrow and the
> generalization and external-validity claims remain partial.

## 26. Resume-safe wording

**One line.** Formalized and certified the core of a sequential-monitoring
stability result in Lean 4 and interval arithmetic, then stress-tested it across
a second detector, non-Gaussian noise and three semi-real streams under
pre-specified failure criteria, with 695 executable verification tests.

**Two bullets.**
* Machine-checked a differentiation-under-the-expectation identity in Lean 4 and
  certified the associated stopped-selection gain by outward-rounded interval
  arithmetic, establishing local instability and a certified period-2 orbit of
  the deterministic conditional-mean map.
* Designed and executed pre-registered, hash-frozen generalization and semi-real
  validation campaigns whose negative results — a failed derivative test at
  larger windows and an unmet external-validation criterion — were preserved
  rather than tuned away.

**Three technical bullets.**
* Proved (Lean 4/Mathlib) a differentiation-under-the-expectation identity for a
  stopped CUSUM functional and certified `Gamma ∈ [3.9243, 27.8494]` via
  outward-rounded Arb interval arithmetic, giving `F'(0) = 1 − Gamma < −1`.
* Certified a unique nonzero period-2 orbit of the deterministic conditional-mean
  map (root in `[1.02872, 1.04472]`, multiplier in `[0.108, 0.833]`), and
  replicated the mechanism on an ARL₀-matched Shiryaev–Roberts detector
  (`Gamma_SR = 17.32 ± 0.03`) — replication, not detector independence.
* Ran hash-frozen pre-registered protocols across non-Gaussian families and three
  semi-real streaming datasets with adversarial suites (12/12, 14/14, 18/18) and
  695 executable tests; reported the failed and ambiguous criteria as failures.
