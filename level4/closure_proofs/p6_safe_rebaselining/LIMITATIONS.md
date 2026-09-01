# P6 limitations

Written to be read by someone trying to break the campaign. Ordered by how much
damage the limitation does if it turns out to matter.

---

## 1. Scope limitations that no P6 result escapes

| # | limitation | consequence |
|---|---|---|
| L1 | **Everything is inside the frozen Gaussian convention-A model.** `N(0,1)` innovations, two frozen detectors at one frozen ARL match, one reuse convention, a step-shaped fresh-sample cost | No P6 number is evidence about a real process. Non-Gaussian innovations, contamination, other detectors, other reuse conventions and other cost models are **P8** (`X5`), and the method has never been run outside this model |
| L2 | **P6 optimises within the re-baselining formulation; it cannot evaluate the formulation.** If reusing the terminal window at all is the wrong operational design, P6 will never say so | Registered as `N2` in the pre-design's failure register, with no detector |
| L3 | **No P6 cell recovers nominal in-control performance.** The best matched-cost policy measured here reaches roughly a third of the nominal `ARL_0 ~ 465`; P7's `S20` says no cell in its whole grid reached within a factor of 4 | "Safe" in P6 means *less damaged than the incumbent at the same cost*, never *safe* |
| L4 | **The `e_0 = 0` canonical regime is a convention, not a deployment.** The finite-reference regime `e_0 ~ N(0, 1/m_0)` is run as secondary evidence only | A deployment starts from a real Phase-I estimate, which is neither |
| L5 | **Operational implementability is asserted, not demonstrated.** Latency, auditability and operator trust are not modelled anywhere in ReBaseGuard | `N3` in the register, no detector |

## 2. Theory limitations

| # | limitation |
|---|---|
| T1 | **T6-B covers memoryless policies only.** SAW is memoryless, so the theorem applies to the proposed method — but `B10_capped`, any EWMA-carrying rule and the whole Family-E filter fall outside it. For those the campaign runs and reports in finite-horizon language, and the closed-loop stationarity question is **open** |
| T2 | **T6-B's constants are astronomically loose.** The minorisation constant contains `exp(-(1+M)^2 / (2 s_min^2))` with `M ~ 30` on the *measured* `sup_x E_x[tau]`, and vastly worse on the theorem's own `C_D`. It must never be compared with a measured mixing time. This is the same qualitative/quantitative gap P5's adjudication recorded for T7 |
| T3 | **T6-B does not bound sample paths.** An invariant law with unbounded support still has arbitrarily large excursions. The P5 adjudication explicitly rejects the "exact finite-`e` reset" reading, and P6 keeps `rho_max < 1` and a positive variance floor as guards for that reason |
| T4 | **T6-C is one-step, from a common entering law, on a latent-layer quantity.** It does not prove that the *stationary* second moment falls, and `S18`/`X6` forbid inferring any monitoring gain from it. Both are measured instead, and the measured stationary reduction is therefore an empirical result with no theorem behind it |
| T5 | **No enforceable tail bound exists at the scale that matters.** T6-D's Chebyshev route is exact and never binds (`Q*(V)/c^2 > 1` in every cell at `c_beta`); the sharp sub-Gaussian route for a stopping-time-selected mean (the pre-design's route 2) remains **open**; the implementable rule uses a Gaussian approximation whose error is measured, not bounded. So P6 has **no theorem-backed safety guarantee** (criterion `N2` of `METHOD_NOVELTY_SEPARATION.md` is **not** met) |
| T6 | **T6-B's proof is new and unadjudicated.** It reuses P5's Doeblin architecture; its new content is that the raw-mean identity makes the decision on the minorising event independent of the state. That step is the one to attack |

## 3. Method limitations

| # | limitation |
|---|---|
| M1 | **SAW's constants are a plug-in fitted under one policy law.** The calibration is a fixed point, but it is a *stochastic* fixed point: iterating changes the chain, so the map is only deterministic up to Monte Carlo noise. Convergence is judged on `(g0, g1, s0)` at tolerance `5e-3` with the drift to a large final pass reported; `s1` (the truncated-window variance) is estimated from a group holding between 0% and 5% of cycles and in three cells from under a hundred observations |
| M2 | **SAW is calibrated entirely at `Delta = 0`.** That is a strength against leakage and a weakness against misspecification: under a shift, `zbar` acquires a `-Delta` offset the calibration never saw. The out-of-control behaviour is measured at `Delta in {0.5, 1, 2}` and not derived |
| M3 | **The conditional-mean model is linear-through-origin in the readout.** Oddness forces the *shape*, not the linearity. A cubic term was tested and discarded on TUNE; nothing rules out a better functional form, and the residual `R^2 ~ 0.95` leaves 5% unexplained |
| M4 | **SAW does not use the increment/history channel** (`OBSERVABILITY_AUDIT.md` section 4), which the audit shows carries real information. That was a deliberate choice — it buys memorylessness and hence T6-B — but it means SAW is **not** the best implementable policy, only the best *memoryless* one the campaign built |
| M5 | **`m` and `k` are design constants, not adapted.** Adaptive `m_j` was tested only through baseline `B5`, which is weak. The `(m, k)` surface is swept, not optimised |
| M6 | **The information ladder's top rung is not the true ceiling.** `Z1` uses the *realised* `U_j^2`, which is one-step-clairvoyant for the SAW rule shape; it is not the optimal policy, and `Z6` (the fully clairvoyant oracle of the pre-design) was **not** run |

## 4. Statistical and procedural limitations

| # | limitation |
|---|---|
| S1 | **`B2*` and `Z5` are grid minima**, so their reported performance is optimistically biased on the family that selected them. They are re-selected and re-estimated on `REPLAY`, and the shift is reported — but the bias is not corrected analytically |
| S2 | **Pairing is seed alignment, not path coupling.** Two policies decouple as soon as they choose differently. The measured pair correlations are reported; sizing used the unpaired variance, as preregistered |
| S3 | **Multiplicity.** One primary objective at one primary cell, BH-FDR at `q = 0.10` within secondary metric families. The real protection is reproduction across both detectors, four `m`, and an independent seed family — not the alpha adjustment |
| S4 | **`G-E` carries a recorded ordering defect.** The protocol required baseline `Coll` to be seen, the threshold written, then SAW's `Coll` computed; the Stage-2 script computed both in one pass and both were inspected together. The *selection* of option E3 rests only on the baseline numbers, and E1/E2 are reported unedited beside it, but `G-E` does **not** have the pre-commitment status of `G-A`..`G-D`. See `results/gate_e.json` |
| S5 | **`G-D`'s count was restated.** D1's literal wording is ">= 6 of 8 families"; with `m = 1` excluded as the pre-design directs, only 6 remain and 6-of-6 would be option D2, which the pre-design rejects. `>= 5 of 6` was declared in advance in `CLOSURE_GATES.md`, and the deviation is recorded rather than made silently |
| S6 | **`G-C` option was changed from the pre-design's recommendation** (C-i) to C-iii plus a preregistered anti-degeneracy criterion `G-C'`. The reason follows from the approved cost model alone and from no result, and C-i's outcome is reported anyway — but it *is* a departure from a recommendation and an adjudicator should check the reasoning |
| S7 | **Screening ran on TUNE and dropped three baselines.** The drops and their numbers are recorded; but a policy dropped at screening scale might have survived at confirmation scale |
| S8 | **`Delta = 2` is under-powered for the tail metric.** The preregistered floor of 200 tail events per arm is met at `Delta = 0.5` and `Delta = 1` (6,278+ and 269-8,576 events) but not at `Delta = 2`, where most arms deliver 0-170. Those `Dtail(100)` values are labelled `INSUFFICIENT_TAIL_EVENTS` and the preregistered `Dq95` fallback is reported instead; the same applies to the two `m=5, k=20` frontier cells. Resolving `Delta = 2` at the tail would need roughly 10x the replicates, which was not budgeted |
| S9 | **R3 runs to 50-100 cycles.** Instabilities with a timescale beyond that are not detectable here (`N4` in the register, a known accepted gap) |

## 5. Novelty limitations

| # | limitation |
|---|---|
| V1 | **The rule's shape has close prior art** — adaptive-EWMA weight adaptation (Capizzi & Masarotto 2003), inverse-variance weighting (textbook), cautious parameter learning (Capizzi & Masarotto 2020). P6 claims **no algorithmic novelty** |
| V2 | **The novelty audit is a one-sitting web literature search**, not a systematic review, and several of the closest items were read from abstracts. Its negative findings are weak evidence of absence |
| V3 | **The novelty audit has not been independently adjudicated**, which `NOVELTY_AUDIT_PLAN.md` section 4 step 5 requires. Status stays `NOVELTY = PARTIAL / NOT_INDEPENDENTLY_ADJUDICATED` |

## 6. What P6 explicitly does not claim

* No claim that `rho < rho_c` is safe, or that `rho_c` means anything operational (`X1`).
* No claim that reducing `E[e^2]` improves any monitoring metric (`S18`, `X6`) — every monitoring number is measured.
* No claim of a safety *guarantee*: there is no binding tail bound (T5 above).
* No claim that SAW is optimal, or even the best implementable policy (M4).
* No claim of algorithmic novelty (V1).
* No claim about any process outside the frozen Gaussian convention-A model (L1).
