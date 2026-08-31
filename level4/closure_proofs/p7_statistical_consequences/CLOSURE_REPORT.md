# P7 closure report

```text
SCIENTIFIC_VERDICT             = CLOSED
REPOSITORY_INTEGRATION_VERDICT = READY_FOR_COMMIT
REPOSITORY_VERIFICATION        = NO_P7_REGRESSION
```

Machine-readable: `results/closure_decision.json`, produced by
`derive_closure.py`, which checks every gate against a produced artifact.

---

## 1. The connection P7 establishes

P7 may close only if it establishes a defensible connection between the P1--P3
recursive re-baselining behaviour and at least one important
sequential-monitoring performance consequence. It establishes three, and
refutes a fourth that the local theory would have suggested.

**Established.**

* **In-control ARL.** Full reuse costs **39.5%–50.6%** of the in-control ARL
  against a fresh-reference control at the same window length,
  `PRACTICALLY_MATERIAL` in all 8 detector/window families, bootstrap intervals
  roughly ±1 percentage point. Against the calibrated nominal `A(0) ~ 465` the
  loss is 83%–90%.
* **Detection delay.** The mean delay for a unit shift rises from `10.4`
  (CUSUM) / `11.0` (SR) to `52.8–66.1` — **+360% to +540%** — and the
  discrimination ratio `R_Delta` rises from `0.022` to `1.06` at `m=1, rho=1`,
  i.e. the shifted cycle becomes *longer* than the in-control cycle.
* **False alarms.** `FAP(100)` rises to `0.82–0.90`; the cycle immediately
  following the first re-baselining has mean length `5.6–9.4` under full reuse,
  against `463–474` for the first cycle.

**Refuted.**

* The **P3 critical reuse fraction has no observable statistical signature**.
  The pre-committed criterion returns `LOCAL-MATHEMATICAL, NOT OPERATIONAL`
  (max 3 of 8 families against a threshold of 4, over five pre-specified
  metrics). This extends Stage-D D2.5's verdict from the `m` direction to the
  `rho` direction under the fixed grid criterion. Conditional P7-C supplies a
  compatible mass-escape interpretation, not a causal proof.

## 2. The closure standard, item by item

| # | requirement | status | where |
|---:|---|---|---|
| 1 | exact definition correspondence with P1--P3 | **met** — the P7 CUSUM chain is bit-identical to `stage_d/src/chain.py`, and convention-A `Gamma_m` is bit-identical to `stopped.py` for both detectors | `DEFINITION_AUDIT.md`, `tests/test_correspondence.py` |
| 2 | CUSUM and SR evidence | **met** — all 104 cells run on both ARL-matched detectors | `STATISTICAL_CONSEQUENCES.md` |
| 3 | attraction / near-boundary / repulsion comparisons | **met** — ladder at `0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2, 4 x rho_c` in every family | §2 |
| 4 | uncertainty-aware ARL evidence | **met** — replicate as the statistical unit, normal and bootstrap intervals for every cell, agreeing to within 2.9% of interval width | §2, `ADVERSARIAL_REVIEW.md` A2 |
| 5 | false-alarm and detection-delay evidence | **met** — both, plus the tail characterisation | §3, §4, §4b |
| 6 | finite-cycle evidence | **met** — cycles 1–50 from `e_0 = 0` in every cell | §5 |
| 7 | honest theory-to-consequence bridge, or a declared boundary | **met** — P7-A is exact for an actual entering-error law; P7-B is conditional-exact; P7-C/D are explicitly conditional/empirical; candidate P7-E and the linear-response pole are rejected | `THEORY_BRIDGE.md` |
| 8 | focused tests | **met** — 31 tests pass | `tests/` |
| 9 | adversarial self-review | **met** — 16 attacks run, 3 of which changed the campaign | `ADVERSARIAL_REVIEW.md` |
| 10 | explicit P5 / P6 / P8 scope boundaries | **met** | `EVIDENCE_BOUNDARY.md`, `P6_HANDOFF.md`, `THEORY_BRIDGE.md` §9 |
| 11 | no unsupported causal or novelty claim | **met** — the absolute re-baselining cost is explicitly attributed to matched information, not claimed as a P7 discovery; every rank-4/5 label is mechanical | `EVIDENCE_BOUNDARY.md` |

## 3. Confirmatory claims, as pre-committed

| claim | outcome |
|---|---|
| **C1** full reuse materially below the fresh control at every `(D,m)` | **confirmed**, 8/8 families `PRACTICALLY_MATERIAL` |
| **C2** no localised rate feature at `rho/rho_c = 1` | **confirmed** (negative result), max 3/8 against a threshold of 4; robust — the verdict flips only if the threshold is lowered below half |
| **C3** `ACF1 = rho(1 - Gamma_eff)` holds, and `Gamma_eff << GammaTilde` when dispersion exceeds `r_lin` | **confirmed** — max absolute gap over all 104 cells is **0.0071**, while the P3 multiplier overshoots the measured `ACF1` by 5x–25x |

## 4. Independent integration result

Independent adjudication passes 31 focused tests and reproduces the headline
ARL, FAP, cycle-2, and delay-tail results with seed family `20260917`. Repository
verification finds no P7 regression. A pre-existing/environment-dependent stale
protected-history manifest prevents a wholly green Level-4 wrapper; a detached
clean worktree at authoritative HEAD reproduces that failure without P7. The
frozen manifest was not modified. See `INDEPENDENT_ADJUDICATION.md` and
`results/repository_verification.json`.

The SR difference is resolved as non-material Monte Carlo variation using P4's
supplementary 1.6-million-path replay; P4 remains `PARTIAL` and is not a premise.

## 5. Honest limitations

* Conditional on the existence of a stationary law with finite fourth moment
  (evidenced by rapid mixing, not proved).
* No rank 1–3 evidence anywhere: no interval certification, no Lean spine.
* P7-D's plug-in deficit diagnostic is conservative by roughly an order of
  magnitude and is not certified; its hypotheses and inputs lack enclosure.
* The theory bridge does not deliver a sharp prediction of the deficit from
  `lambda`; the map from `lambda` to stationary dispersion runs through the
  saturation of `h_m` and has no closed form here.
* Frozen Gaussian CUSUM and SR only, `m in {1,2,3,5}`, `rho in [0,1]`.

## 6. Handoffs

* **P5** — `ACF1(e) < 0` in every cell, growing in magnitude with `rho` to
  about `-0.58`; the finite-cycle curves show a strong one-cycle overshoot and
  partial recovery. Recorded as an alternation statistic only. No period-2,
  attractor, basin, hysteresis or bifurcation claim is made.
* **P6** — `P6_HANDOFF.md`: control reference-state dispersion; do **not**
  target `rho < rho_c`; evaluate on a delay tail criterion, not the mean.
* **P8** — everything outside the two frozen Gaussian specialisations.
