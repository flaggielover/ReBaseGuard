# P7 adversarial self-review

Every attack below was run, not merely considered. Machine-readable output:
`results/adversarial.json`, `results/sr_gain_check.json`,
`results/delay_validation.json`, `results/boundary_verdict.json`.

Three findings changed the campaign; they are listed first.

---

## Findings that changed the campaign

### F1. Seeds were not reproducible (fixed; all production data regenerated)

The first production pass derived seeds from `hash(detector_name) % 97`. Python
salts `hash` of a `str` per process, so **no result was reproducible across
runs** — confirmed by two identical invocations of the delay validation
returning `51.804` and `52.719`. Fixed with
`DETECTOR_CODE = {"cusum": 11, "sr": 13}`; every production artifact was
regenerated afterwards. `tests/test_reproducibility.py` now forbids `hash(` in
the campaign source and asserts a same-seed chain reproduces bit-identically.

### F2. The delay identity was biased by grid truncation (fixed)

`A(x)` was measured only to `|x| = 3`, and the interpolant held flat beyond.
For `m = 1, rho = 1` — where the next reference is essentially the
alarm-triggering observation — 7% of the delay integrand `A(e - Delta)` fell
outside, biasing the identity route upward by up to 5.6% (`z = -4.05` against
direct simulation). The grid was extended to `|x| = 12`; all eight validation
cells then agree (largest `|z| = 2.36`, largest relative gap 2.9%, over eight
tests). Had the identity still disagreed, `EXPERIMENT_DESIGN.md` §4 committed to
abandoning the identity route rather than patching it.

### F3. Reporting the mean delay alone would have misdescribed the failure mode

The mean detection delay rises 360%–540%, but the **median is at or below
nominal** (7 against 10.35 at CUSUM `m=1, rho=1, Delta=1`). The inflation is a
right tail: `q95 = 275`, `P(delay > 100) = 11.4%`. A uniform-slowdown reading
would have been wrong. The report now carries median, `q75`, `q95`,
`P(delay > 100)` and a blind-spot probability alongside every mean.

---

## Attacks that the conclusions survived

| # | attack | test | result |
|---|---|---|---|
| A1 | **ARL estimator bias / burn-in too short** | cycle-mean ARL over cycles 12–49 (reported) vs 30–49, all 104 cells | max shift **1.4%**; 0 cells above 2%. Burn-in adequate. |
| A2 | **heavy-tail instability of the ARL estimator** | normal-theory vs 10,000-resample replicate bootstrap interval width, all 104 cells | max width disagreement **2.9%**; 0 cells above 20%. The per-replicate mean over 38 cycles is well behaved even though the run length is not. |
| A3 | **right-censoring** | `max_steps` raises rather than truncates | asserted by `tests/test_semantics.py::test_no_censoring`; no run hit the cap |
| A4 | **seed dependence** | six cells re-run under an independent seed family (`20260901`) | max `|z| = 1.62`; every headline cell replicates |
| A5 | **CRN misuse** | CRN is used only within a response-curve grid point and in reusing one measured `pi` across shifts; it is **not** used across `rho`, because two chains at different `rho` decouple at the first alarm | stated in `EXPERIMENT_DESIGN.md` §5; no paired-difference claim is made across `rho` |
| A6 | **multiple comparisons** | three pre-committed confirmatory claims, fixed in `EXPERIMENT_DESIGN.md` §9 before the production analysis; everything else labelled exploratory | C1 and C3 hold with enormous margins; C2 is a negative result, so multiplicity could only weaken it, and it is not close (max 3 of 8 against a threshold of 4) |
| A7 | **effect size vs significance** | the three-way label `INCONCLUSIVE / STATISTICALLY_RESOLVED / PRACTICALLY_MATERIAL` was fixed in advance and is applied mechanically | e.g. `rho/rho_c = 0.25` at CUSUM `m=1` is `STATISTICALLY_RESOLVED` (+1.9%) but **not** material; only the large-`rho` cells reach `PRACTICALLY_MATERIAL` |
| A8 | **conditioning mismatch** | every chain starts at `e_0 = 0` exactly and no metric conditions on the alarm arm; two controls are reported and never merged | `DEFINITION_AUDIT.md` §3 |
| A9 | **inconsistent detector semantics** | the P7 CUSUM chain is **bit-identical** to `level4/stage_d/src/chain.py`, and the P7 cycle simulator's convention-A `Gamma_m` is bit-identical to `stopped.py`'s, for both detectors | `tests/test_correspondence.py` |
| A10 | **mismatch with the P3 `rho` definition** | `rho_c` is loaded from P3's `boundary_table.json` at run time, never transcribed; a test compares the loaded values against the file | `tests/test_correspondence.py::test_rho_c_is_read_from_the_closed_p3_artifact` |
| A11 | **transient mistaken for persistent** | the cycle-2 collapse (mean length 5.6–9.4) is explicitly a transient; the quasi-stationary claims use cycles 12–49 and are separately reported. Independent adjudication also rejected candidate P7-E, so no `lambda^j` propagation claim remains | both regimes are reported, neither is used as the other |
| A12 | **manufacturing a boundary effect** | the linear-response formula with its pole at `rho_c` was derived, stated, and **rejected on the evidence** (`THEORY_BRIDGE.md` §7): the measured reference MSE is smooth and non-monotone through `rho_c`, while empirical RMS / grid-defined `r_lin` is 8.2–18.9 at the exact boundary cells | the single most available route to a false positive was closed deliberately |
| A13 | **boundary verdict fragility** | the criterion needs 4 of 8 families; the observed maximum over five metrics is 3 | the verdict flips only if the threshold is lowered to 3, i.e. to "fewer than half" |
| A14 | **is the P7-D plug-in diagnostic vacuous or numerically violated?** | conditional P7-D evaluated on every admissible cell | not numerically violated; reaches 21.5% but is conservative by roughly an order of magnitude. It is not certified because assumptions and Monte Carlo inputs lack interval propagation |
| A15 | **P5 leakage** | `ACF1(e) < 0` in every cell and `|ACF1|` grows with `rho`, which is an alternation *statistic* | reported as a statistic and handed to P5; no period-2, attractor, basin or bifurcation claim is made anywhere |
| A16 | **P6 leakage** | the in-control ARL is maximised at `rho ~ 0.14 to 0.25` | labelled EXPLORATORY in `results/adversarial.json` and stated in `P6_HANDOFF.md` as a *negative* instruction (do not target `rho < rho_c`), never as a recommended operating point |

---

## Open discrepancy handed to Codex, not resolved here

**The frozen Gaussian SR gain differs between campaigns by more than the stated
standard errors.** P7 re-measured `GammaTilde^SR` at P3's own sample size
(20 batches x 100,000 cycles) using an implementation that is bit-identical to
Stage D's:

| m | P7 (2x10^6 cycles) | P3 / P2 | Stage-D `d1_gamma` | z (P7 vs P3, combined SE) | implied `rho_c` shift |
|---|---|---|---|---|---|
| 1 | 17.2990 ± 0.0382 | 17.4536 ± 0.0659 | 17.3198 ± 0.0274 | −2.03 | +0.95% |
| 2 | 14.3752 ± 0.0309 | 14.5005 ± 0.0567 | — | −1.94 | +0.94% |
| 3 | 12.8481 ± 0.0284 | 12.9727 ± 0.0490 | — | −2.20 | +1.05% |
| 5 | 10.9423 ± 0.0229 | 11.0485 ± 0.0410 | — | −2.26 | +1.07% |

P7's CUSUM gains agree with P3's at every `m` (within 0.7 SE at `n = 4x10^5`).
Only SR is offset, by a consistent −0.9% to −1.1%, and P7's SR value agrees with
Stage-D's independent `d1_gamma` estimate (`z = -0.44` at `m = 1`). The SR
threshold is bit-identical to P2's (`0x1.04716cd36dd8dp+9`).

Caveats stated plainly: the four `m` values are **not** independent tests — they
come from the same paths — so this is one observation at roughly `2.1 sigma`,
corroborated by an independent agreement with Stage D. It is **not** enough to
call a closed campaign wrong.

P7 does not own these numbers, does not modify them, and its conclusions do not
depend on them: a 1% shift in `rho_c` cannot matter to a boundary that has no
observable signature. **Codex should adjudicate independently.**

---

## What would falsify P7

* A configuration in which the reference dispersion is small compared with
  `r_lin ~ 0.05`. Then the linear-response pole at `rho_c` would apply and the
  boundary could become observable. No such configuration exists in the frozen
  model at `m in {1,2,3,5}`, because the fresh term alone injects
  `Var >= (1-rho)^2/m`.
* Failure of existence, uniqueness, ergodicity, or finite fourth moment for a
  stationary law would void parts of P7-B/C/D. Finite sample fourth moments and
  burn-in agreement do not prove those properties.
* A failure of `THEOREM P7-A` — i.e. evidence that the entering reference error
  is not a sufficient statistic for the cycle. This is the load-bearing
  structural claim and the one an adjudicator should attack first. It is tested
  in eight cells against direct simulation and holds to 2.9%.
