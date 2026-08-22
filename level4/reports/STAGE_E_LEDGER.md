# Stage E — claim ledger

Every Stage E statement with its evidence status. **Decision: `STAGE-E-PARTIAL`.**
Protocol `974487019f57c7c3…`, unchanged. Adversarial 14/14.

| # | Statement | Status | Evidence |
|---|---|---|---|
| E-01 | Stage E validates the operational mechanism, not the Gaussian theorem; `F'(0)=1-Gamma` and the Stage B certificate are **not** tested on external data | `METHOD-DEFINITION` | protocol §0 |
| E-02 | Three tasks, one frozen protocol, chronological splits, frozen models | `METHOD-DEFINITION` | `DATA_PROVENANCE.md` |
| E-03 | Elec2 `date` is non-monotone (5 backward jumps at day boundaries); file row order is authoritative | `REPRODUCED` | verified in loader + test; provenance table |
| E-04 | Residual streams are strongly autocorrelated (ACF(1) 0.718 / 0.832 / 0.792) and were **not** whitened | `NEW-NUMERICAL` | §2 diagnostics |
| E-05 | Task C's residual retains a weekly cycle (ACF(168) = 0.780) from a frozen, misspecified feature set | `NEW-NUMERICAL` | left visible by design |
| E-06 | Detector thresholds (15.2–36.7) far exceed the frozen `h = 5` because of serial dependence | `NEW-NUMERICAL` | per-task calibration |
| E-07 | All three calibrations hit the frozen ARL0 target within 5% on the calibration block only | `CONFIRMATORY-NUMERICAL` | A5; rel err +0.024 / −0.018 / +0.041 |
| E-08 | **Task A: full reuse causes greater reference-state distortion than fresh and than ReBaseGuard** | **`CONFIRMATORY-NUMERICAL`** | `P1−P2 = +0.0766 [+0.0369,+0.1135]`, `P1−P0 = +0.0883 [+0.0498,+0.1326]` |
| E-09 | Task A: full reuse shows **no** normalised-discrimination penalty; point estimate is the opposite sign | **`NEW-NUMERICAL` (directional contradiction)** | `R(P1)−R(P2) = −0.0141 [−0.2855,+0.2047]` |
| E-10 | Task A H-E2 (alert burden) | **`FAILED`** — statistical non-demonstration | order P1>P2>P0 as predicted; all CIs include 0 |
| E-11 | Task A H-E3 non-inferiority | **`FAILED`** at both margins | fails 3 of 5 conditions; all point excesses negative |
| E-12 | Task A H-E5 | **`FAILED`** | needs H-E1 ∧ (H-E2 ∨ H-E4) |
| E-13 | Task B is **LOW-POWER**: closure policies sit exactly at the floor of 5 effective blocks | `METHOD-DEFINITION` | 4,496 eval obs → 19–23 cycles |
| E-14 | Task B H-E1, H-E2, H-E4 | **`FAILED`** — all statistical non-demonstration, predicted direction | CIs include 0 |
| E-15 | Task B H-E3 non-inferiority at `eps = 0.10` | `CONFIRMATORY-NUMERICAL` | all 5 conditions pass |
| E-16 | Task B H-E3 at the secondary `eps = 0.05` | **`FAILED`** | STEP_0.5 upper95 excess +0.0577 |
| E-17 | Task B P3 E2 interval | **`UNRELIABLE`** (4 blocks) | excluded from all hypotheses |
| E-18 | Task C is **PARTIALLY USABLE AFTER FREEZE**: E1/E4 valid, E2/E3 below floor | `METHOD-DEFINITION` | 2–3 effective blocks vs floor 5 |
| E-19 | **Task C: full reuse has significantly worse normalised response than ReBaseGuard** | **`CONFIRMATORY-NUMERICAL`** | `R(P1)−R(P2) = +0.0470 [+0.0062,+0.1266]` |
| E-20 | Task C H-E3 at **both** margins | `CONFIRMATORY-NUMERICAL` | `R(P2)/R(P0)` ∈ [0.987, 1.008] |
| E-21 | Task C H-E1 and H-E2 | **`UNEVALUABLE`** | E2/E3 below the reliability floor |
| E-22 | Task C's large apparent E2/E3 effects (P1 0.4315 vs P0 0.2397; burden 1.97 vs 1.05) | **`UNRELIABLE — excluded`** | the gate was applied against the most favourable data in the stage |
| E-23 | Task C H-E5 | **`NOT MET`** | H-E1 unevaluable, so the conjunction cannot hold |
| E-24 | `0 / 3` tasks support H-E5; `2` required | `CONFIRMATORY-NUMERICAL` | frozen closure rule |
| E-25 | Closure was **mathematically unreachable** after Task B, and was stated so before Task C ran | `METHOD-DEFINITION` | decision trace |
| E-26 | E4 raw-delay ordering **reverses** across tasks (P1 fastest in A, slowest in B and C) | `NEW-NUMERICAL` | §4 item 3 |
| E-27 | H-E4's sign is stream-dependent (−0.0141 / +0.0528 / +0.0470) | `NEW-NUMERICAL` | §4 item 2 |
| E-28 | E1 denominator was length-biased; corrected at the pilot gate before any confirmatory outcome | `METHOD-DEFINITION` | C3; biased quantity retained for audit |
| E-29 | Calibration policy ambiguity resolved to fresh `rho = 0` | `METHOD-DEFINITION` | C1 |
| E-30 | Task A's confirmatory run is **not statistically independent of its pilot** (bit-identical) | `METHOD-DEFINITION` | replication rests on A6 |
| E-31 | P3 (EXPLORATORY) does not replicate across tasks and is excluded from all closure statements | `CANDIDATE` | best in A, worst at STEP 1.0 in B |
| E-32 | No sample-efficiency claim is possible | `METHOD-DEFINITION` | every policy consumes the fresh block every cycle; pinned by test |
| E-33 | E3 is an alert **burden**, not a false-alarm rate | `METHOD-DEFINITION` | natural streams contain real drift |
| E-34 | `eps = 0.10` is an independent Stage E margin, not a relaxation of Stage C.1's `0.05` | `METHOD-DEFINITION` | `0.05` reported unchanged as secondary |
| E-35 | Adversarial suite 14/14 | `CONFIRMATORY-NUMERICAL` | `adversarial.json` |
| E-36 | Protocol deviations: **none** | `METHOD-DEFINITION` | `PROTOCOL_DEVIATIONS.md` |
| E-37 | Stages A/B/C/C.1/D and Level 1–3 untouched | `METHOD-DEFINITION` | no file outside `stage_e/` modified |
| E-38 | Whether reference distortion implies a discrimination penalty | **`OPEN`** | A says no, C says yes |
| E-39 | Adequate E2/E3 power on short streams without violating dependence coverage | **`OPEN`** | design question |
| E-40 | Behaviour at intermediate reuse intensities between 0.0298 and 1 | **`OPEN`** | untested by design |

## Forbidden wordings (none appear affirmatively in Stage E artifacts)

production-proven · industry-proven · universally robust · distribution-free ·
detector-independent · optimal · real-world deployment validated · sample
savings · data efficiency · "false-alarm rate" for E3 · "external validation
succeeded" · full reuse universally degrades discrimination.
