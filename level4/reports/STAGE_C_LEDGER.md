# ReBaseGuard Level 4 — Stage C Result Ledger

Statuses are defined in `level4/src/rebaseguard_level4/ledger.py`.
`NEW-NUMERICAL` and `CANDIDATE` entries are Monte Carlo findings and
are **not** proofs. `FROZEN-*` entries are Level 1–3 results quoted
here unchanged. `RIGOROUS-CERTIFIED` means the analytic lemmas are
proved and **every** approximation between the true mathematical
object and the computed one is explicitly bounded — not merely that
interval arithmetic was used somewhere.

| ID | Status | Statement | Evidence |
|---|---|---|---|
| `SC-F1` | **FROZEN-CERTIFIED** | Frozen Level 1-3, Stage A and Stage B are quoted unchanged; Stage C adds no claim about them and modifies no frozen artifact. | `closure/04_ARB_CERTIFICATE.md`<br>`level4/stage_b/certificate/period2_certificate.json` |
| `SC-F2` | **FROZEN-PROVED** | F'_rho(0) = rho(1-Gamma) and F_rho = rho F_1 are Level 2C results used here as given. | `rebaseguard_phase2c.md` |
| `SC-M1` | **METHOD-DEFINITION** | The ReBaseGuard policy is rho_safe(delta) = clip((1-delta)/(Gamma-1), 0, 1); at delta = 0.2, substituting the upper end of the frozen Gamma enclosure gives rho = 0.029796. | `level4/stage_c/src/policy.py`<br>`level4/stage_c/STAGE_C_PROTOCOL.md` |
| `SC-M2` | **RIGOROUS-CERTIFIED** | The CONSERVATIVE variant keeps \|F'_rho(0)\| <= 1-delta for every Gamma the frozen enclosure admits, because \|F'_rho(0)\| = rho(Gamma-1) increases in Gamma. | `level4/stage_c/tests/test_policy.py` |
| `SC-M3` | **NEW-NUMERICAL** | The POINT variant is heuristic: at the upper end of the frozen Gamma enclosure its reuse fraction would exceed the local stability boundary. It is reported only for contrast. | `level4/stage_c/results/adversarial.json` |
| `SC-N1` | **NEW-NUMERICAL** | Stationary reference MSE falls monotonically from 1.0003 at rho = 0 to a minimum of 0.7086, then rises to 1.8773 at full reuse. | `level4/stage_c/results/incontrol_main.json` |
| `SC-N2` | **NEW-NUMERICAL** | In-control cycle ARL is non-monotone in rho: 83.31 at rho = 0, peaking near rho = 0.25, falling to 50.02 at full reuse. | — |
| `SC-N3` | **NEW-NUMERICAL** | A(e) = E[tau \| e] is symmetric within Monte Carlo error and monotone decreasing in \|e\| across the whole tested grid; monotonicity was TESTED, not assumed. | `level4/stage_c/results/arl_curve.json` |
| `SC-NULL1` | **NEW-NUMERICAL** | Crossing the local stability boundary rho_c leaves NO visible signature in stationary reference MSE or in cycle ARL: both vary smoothly through rho_c with no kink or discontinuity. | — |
| `SC-NULL2` | **NEW-NUMERICAL** | The ReBaseGuard policy is NOT performance-optimal: a fixed rho = 0.3 attains reference MSE 0.7086 against 0.9437 for the policy. | — |
| `SC-NULL3` | **FAILED-TO-REPRODUCE** | Pre-specified criterion C6 FAILED at Delta=0.25, Delta=0.5: ReBaseGuard's raw detection delay exceeds full reuse's by more than the 25% threshold. The criterion was left unchanged and the Stage C decision reflects the failure. | `level4/stage_c/notes/CRITERION_C6_DIAGNOSIS.md`<br>`level4/stage_c/results/detection_main.json` |
| `SC-NULL4` | **NEW-NUMERICAL** | The C7 decomposition check initially failed (max \|z\| = 3.70) because the implementation omitted the bias_interp term the protocol had already specified. With the specified formula it gives 2.12; with a sharper Richardson bias estimate 3.34, and 2 of 23 points would exceed 3. | `level4/stage_c/notes/PROTOCOL_DEVIATIONS.md` |
| `SC-OPEN1` | **OPEN** | Nothing here concerns the invariant law of the noisy recursion. Empirical stationary shapes are numerical descriptions only; no bimodality, ergodicity or stochastic period-2 claim is made. | — |
| `SC-OPEN2` | **OPEN** | Pre-allocated thinning and sample splitting are not implemented: both would change the frozen re-baselining rule. | — |
| `SC-OPEN3` | **OPEN** | Only m = 1, k = 1/2, h = 5, Gaussian innovations, and shifts applied at a cycle boundary. Adaptive reuse is untouched. | — |

## Notes

- **`SC-M1`** — Defined before any Stage C evaluation and independent of every Stage B and Stage C outcome; enforced by a test that scans the module for outcome values and identifiers.
- **`SC-M2`** — Certified for LOCAL LINEAR stability of the DETERMINISTIC map only. It is not a statement about the noisy recursion.
- **`SC-NULL1`** — A null result, and an important one: the certified local boundary is not an observable transition in these endpoints. The nonlinearity of F_1 caps the instability well before it shows up in stationary summaries.
- **`SC-NULL2`** — Pre-registered in STAGE_C_PROTOCOL.md section 12 BEFORE the campaign, reported as a headline limitation. The policy buys a certified local-stability guarantee, not optimality.
- **`SC-NULL3`** — The criterion compares raw delays across policies whose in-control ARLs differ by 1.7x. Full reuse's delay-to-baseline ratio is ~1.0 at every shift, i.e. it alarms at essentially the same rate with or without a change -- the ABSENCE of sensitivity. On that baseline-free measure ReBaseGuard preserves sensitivity (0.93 -> 0.41) and is absolutely faster than full reuse at Delta = 1.5. The criterion was badly formulated; it was not rewritten.
- **`SC-NULL4`** — Recorded because this is the one correction that turned a failure into a pass. Raw agreement between the two ARL routes is better than 0.6% at every rho, the discrepancy's sign and grid-scaling are fully explained by log-linear interpolation of a convex function, and the C7 verdict does not change the Stage C decision because C6 already fails.
