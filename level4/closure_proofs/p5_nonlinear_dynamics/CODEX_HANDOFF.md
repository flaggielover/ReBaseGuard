# P5 → Codex discovery handoff

> **Adjudicated:** this discovery handoff is superseded by
> `INDEPENDENT_ADJUDICATION.md`. The final scientific verdict is `PARTIAL`.
> T1, T7, and T11 survive; deterministic attraction/flip and T10 operational
> claims are narrowed there.

```text
SCIENTIFIC_VERDICT             = PARTIAL (see independent adjudication)
REPOSITORY_INTEGRATION_VERDICT = APPROVED_PARTIAL_CHECKPOINT
```

P5 is the discovery phase and does not adjudicate itself. Everything needed to
attack it is below.

## 1. Strongest claimed result

An exact algebraic identity — the **raw-mean representation** (T1) — that
removes the state variable from the frozen re-baselining recursion:

```
e_{j+1} = rho * Rbar_j + (1 - rho) * fresh_j ,
Rbar_j  = (1/w_j) sum_{r<w_j} raw_{tau_j - r} ,   w_j = min(m, tau_j),
```

and the two consequences that close open questions from P7 and P3:

* **T7** — for both frozen detectors, every `m >= 1` and **every `rho in [0,1]`
  including full reuse**: a unique invariant law, uniform geometric ergodicity,
  and finite moments of every order. This closes all five stationary-law gaps
  that P7 recorded as evidenced-but-unproved.
* **T9 + T10** — the P3 critical reuse fraction is a genuine supercritical flip
  bifurcation of the deterministic conditional-mean skeleton, **and** it is
  provably invisible to the stochastic chain, because a supercritical flip emits
  a zero-amplitude orbit against a strictly positive noise floor.

## 2. Exact theorem statements

All conventions are those audited in `DEFINITION_AUDIT.md`; `D in {CUSUM(k=1/2,
h=5), SR(A=520.886133602749)}`, `m >= 1`, `rho in [0,1]`, `Delta = 0`.

| id | statement | tier |
|---|---|---|
| **T1** | `e_{j+1} = rho Rbar_j + (1-rho) fresh_j`, `Rbar_j` = mean of the last `min(m,tau_j)` raw `N(0,1)` draws | EXACT |
| **T2** | `E[e_{j+1}|e] = rho R(e)`; `Var(e_{j+1}|e) = rho^2 S(e) + (1-rho)^2/m`; `R'(0) = 1 - GammaTilde` | EXACT |
| **T3** | `R(-e) = -R(e)`, `S(-e) = S(e)`, `A(-e) = A(e)` | EXACT |
| **T4** | `sup_e E[tau|e] <= 10/Phi(-1)^10 = 9.8959e8` (CUSUM); `<= 1/Phi(-(log A + 1/2)) = 1.4054e11` (SR) | EXACT |
| **T5** | `E[Rbar^{2p}|e] <= (2p-1)!! C_D` for all `e`, `p`; hence `sup_e E[e_{j+1}^2|e] <= rho^2 C_D + (1-rho)^2/m` | EXACT |
| **T6** | the kernel is Feller; indeed `e' -> e_{j+1}(e', omega)` is a.s. locally constant | EXACT |
| **T7** | `P^2(e,.) >= delta nu(.)` for all `e`; unique `pi`; `sup_e ||P^n(e,.)-pi||_TV <= 2(1-delta)^{floor(n/2)}`; `E_pi[e^{2p}] < infinity` for all `p`; `pi` symmetric so `E_pi[e]=0` | EXACT |
| **T8** | `0` is the unique fixed point of `f_rho = rho R` for every `rho > 0` | CONDITIONAL on (H1),(H2) |
| **T9** | symmetric 2-cycles are exactly `s(e*) = 1/rho`; none for `rho <= rho_c`, exactly one for `rho > rho_c`, `e*` increasing with `e*(rho_c+) = 0`; multiplier `rho^2 R'(e*)^2` | CONDITIONAL on (H1)–(H3) |
| **T10** | `SNR(rho) = e*(rho)/sqrt(V(e*)) -> 0` as `rho -> rho_c+` | CONDITIONAL on (H1)–(H3), `S` continuous at `0` |
| **T11** | `ACF1 = rho(1 - Gamma_eff)` exactly, with `Gamma_eff = 1 + E_pi[e^2 s(e)]/E_pi[e^2]` | EXACT (uses T7's `pi`) |
| **T12** | runaway, global destabilisation by local repulsion, Foster–Lyapunov necessity, an operational signature at `rho_c`, multiple attractors, pitchfork/saddle-node/transcritical, and a cascade to chaos on `[0,1]` are all rejected | REJECTED HYPOTHESES |

## 3. Assumptions

* **Exact (T1–T7, T11).** Only the frozen conventions: iid `N(0,1)` raw
  observations, `z_t = raw_t - e_j` with `e_j` constant over the cycle,
  `tau = inf{t>=1: alarm}` with an inclusive post-update test from a reset
  state, `w = min(m, tau)` with the **truncated denominator**, terminal
  increment included, `fresh ~ N(0,1/m)` independent, `rho in [0,1]`.
  T1 **fails** for a fixed-`m` denominator; this is asserted by a test.
* **Measured (H1)–(H3), used only by T8–T10.**
  `(H1)` `R` odd — this is T3, exact, and is re-tested numerically as a
  falsification check. `(H2)` `R(e) < 0` for `e > 0`. `(H3a)` `s = -R/e` is
  continuous and strictly decreasing on `(0, 2]` with `s(0+) = GammaTilde - 1`
  and `s(2) < 1`. `(H3b)` `sup_e |R(e)| < 2`, so `s(e) < 1` for `e > 2`.
  Audited in `results/hypothesis_audit.json`: (H2) and (H3b) hold in 8/8 cells;
  (H3a) has one nominal violation at `z = 0.2` in one cell.
  **`s` is not globally monotone** — a secondary lobe of `|R|` near `|e| ~ 5.5-7`
  makes `s` rise between `e = 4` and `5`. Irrelevant for `rho <= 1` (which only
  probes `s >= 1`), but (H3) must never be quoted globally.

## 4. Proof dependencies

```
T1  algebra only
T2  <- T1
T3  raw-sign reflection; frozen two-arm symmetry of both recurrences
T4  block argument: 10 steps with z>=1 force a CUSUM alarm from any state;
    1 step with z >= log A + 1/2 forces an SR alarm from any state
T5  <- T1, T4          Jensen (w>=1) + Wald for a stopped sum of iid raw^{2p}
T6  <- T4              a.s. strict crossings + continuity in e; raw is e-free
T7  <- T4, T5          Chebyshev return to [-R*,R*] with prob >= 1/2,
                       {tau=1} minorisation on that set (uniform in m),
                       two-step Doeblin on the whole line
T8  <- (H1),(H2)
T9  <- T8, (H1)-(H3)   plus IVT for existence, StrictAntiOn for uniqueness
T10 <- T9, S continuous at 0, rho_c < 1
T11 <- T7, T3          stationarity + symmetry
```

`P5` imports the P7 package **read-only** and reads P3's
`results/boundary_table.json` as data. It never re-derives `GammaTilde` or
`rho_c`.

## 5. Numerical evidence

| evidence | value |
|---|---|
| chain correspondence with frozen P7/Stage-D | `tau` bit-identical 12/12; `max abs e_start difference = 8.9e-16` |
| `R'(0)` vs P3 `1 - GammaTilde` | `0.14%`–`1.6%` in 8/8 cells; induced `rho_c` shift `<= 0.0012` |
| independent seed-family replication of the map | 392 paired cells, `mean z = +0.016`, `sd z = 1.044`, `max |z| = 3.12` |
| saturation | `sup|R| = 0.91–1.59` at `|e| = 0.2–0.3` |
| total forgetting | `|R| <= 0.0021 +/- 0.0008` and `S = 1.000` for `|e| >= 10`, every `m`, both detectors; `P(tau=1) = 1.000000` |
| runaway hunt | from `e_0 = 10^6`: mean `|e_1| = 0.83`; global max `|e|` over every stress trajectory after cycle 0 is `5.43` |
| skeleton scan (no algebra) | periods `{1,2}` only, 199 `rho` x 84 initial conditions x 8 cells; period-2 onset within `0.0055` of the frozen `rho_c` in all 8 |
| dispersion law | interior RMS minimum at `rho = 0.163–0.30` = `1.5x–4.5x rho_c`, 8/8; `25–30` s.e. deep |
| ARL co-optimum | same `rho` in 7/8 cells, adjacent grid point in the 8th |
| boundary probe | `rho_c` ranks 1st in **0 of 40** (det x window x metric) curvature tests; best rank 4/21 |
| initial-condition independence | 552 `z` statistics, median `1.11`, max `3.88` (null max: median `3.53`, 95th pct `4.17`) |
| mixing | `ACF1 < 0` for every `rho > 0`; IACT at its floor (`<= 1` cycle) |
| bimodality onset | `rho = 0.411–0.593` = `4.1x–9.8x rho_c` (per-replicate density contrast, 864000 samples/cell) |
| metastability | mean residence `1.08–1.46` cycles, *falling* in `rho`; alternation up to `0.93` |
| tails | excess kurtosis `-0.09` to `-1.02`, never positive: **not** heavy-tailed |
| T11 cross-campaign check | map-predicted vs chain-measured `ACF1` agree to `<= 0.0174` absolute (`<= 3.5%`) |
| `Gamma_eff` | `1.48–2.19` measured, against tangent `GammaTilde = 11.8–17.3` (P7 reported a 5x–25x overshoot) |
| Lean | 12 declarations, sorry-free, axioms `{propext, Classical.choice, Quot.sound}` |

## 6. Rejected hypotheses

1. Runaway / divergence at `rho > rho_c` — rejected by T5/T7 and by the stress test.
2. Local repulsion is globally destabilising — rejected; `M(e) -> 0`.
3. A Foster–Lyapunov outer-drift argument is *needed* — rejected as unnecessary:
   T1 gives a state-independent moment bound, strictly stronger.
4. An operational signature at `rho_c` — rejected (0/40) and explained (T10).
5. Multiple attractors / invariant measures — rejected by T7 uniqueness.
6. Metastable coexisting regimes — rejected by residence times.
7. Pitchfork / saddle-node / transcritical bifurcation — rejected by T8.
8. Period-doubling cascade or chaos on `rho in (0,1]` — rejected by the scan.
9. Asymmetric 2-cycles — none found anywhere.
10. Heavy-tailed stationary reference law — rejected (platykurtic).
11. **P5's own draft claim** that the stationary law is unimodal at every `rho`
    — rejected by P5's own dedicated experiment and corrected.

## 7. Stationary-law limitations

Existence, uniqueness, ergodicity, geometric TV convergence and all moments are
**proved** (T7), not evidenced. The *constants* are vacuous:
`C_CUSUM <= 9.8959e8` against a measured `465.2`, and `delta'` inherits it, so
the TV rate is qualitative only. Measured mixing (IACT `<= 1` cycle) is reported
separately and used in no proof. A realistic-constant version is available by
assuming the measured `sup_e A(e)`; P5 states that route and does **not** claim
it. Proving `sup_e E[tau|e] = E[tau|0]` would make it unconditional.

## 8. Nonlinear-map evidence and detector/window comparison

`R` is odd, peaks at `|R| = 0.91–1.59` near `|e| = 0.2–0.3`, has a reproducible
secondary lobe near `|e| ~ 5.5–7`, and is indistinguishable from `0` beyond
`|e| ~ 10`, where `S = 1.000` — the one-step reset.

* **Detector.** CUSUM and SR are the *same map* away from the origin:
  `e*(rho=1) = 1.0434` vs `1.0418`, `SNR` equal to 3 decimals at every `rho`,
  `sup|R|` within `1.4%`. Only the linearisation differs (SR's `GammaTilde` is
  ~9% larger, so `rho_c` ~9% smaller). This is the map-level explanation of P7's
  detector-independence.
* **Window.** `m` up: `|R'(0)|` `14.9 -> 9.1`, `sup|R|` `1.56 -> 0.91`,
  `S(0)` `4.04 -> 1.59`, `e*(1)` `1.043 -> 0.604`, `rho_c` `0.067 -> 0.108`,
  `SNR(1)` `1.42 -> 2.08`, stationary RMS at every `rho` down, ARL up, and the
  dispersion-optimal `rho*` down. Monotone and unambiguous over `m <= 5`.

## 9. Key figures

| figure | claim it supports |
|---|---|
| `p5_nonlinear_map.png` | saturation, total forgetting, the P3 tangent, `s` decreasing |
| `p5_bifurcation_and_dispersion.png` | the flip branch against the chain's spread; `SNR <= 2.1`; the U-shaped dispersion law with `rho_c` far to the left of the optimum |
| `p5_stationary_density.png` | invariant densities with replicate bands, orbit overlaid |
| `p5_bimodality_onset.png` | the density-contrast zero crossing at `4x–10x rho_c` |

`figures/figure_index.json` records the sources and the caveat that CUSUM `m=1`
is hidden beneath SR `m=1` in every panel.

## 10. Adversarial attacks already run

17, in `ADVERSARIAL_REVIEW.md`. Three changed the campaign:

* **A1** forced the truncated-denominator test, which established that T1 is
  specific to the frozen Stage-D convention A.
* **A5** forced exact symmetrisation of `R` in every *inferential* use (the
  skeleton scan and the T11 prediction), while deliberately leaving the
  hypothesis audit and the figures unsymmetrised.
* **A9** overturned P5's own draft claim of unimodality at every `rho`.

## 11. Explicit attack targets for Codex

1. **T7 Step 2.** The minorisation uses `{tau = 1, plus alarm, raw_1 in J}` with
   `J = (R*+c_D+0.1, R*+c_D+0.6)` and `c_CUSUM = h+k = 5.5`,
   `c_SR = log A + 1/2`. Check that `w = min(m,1) = 1` really makes `Rbar =
   raw_1` for **every** `m` (it does in the frozen code; a test asserts it), and
   that `x <= R*` really makes the alarm condition hold across all of `J`.
2. **T5's use of Wald.** `{tau >= t} in F_{t-1}` and `raw_t` independent of
   `F_{t-1}` — verify that the *detector* filtration is the raw filtration, i.e.
   that `e` is deterministic within a cycle so `z_t` is `F_t`-measurable.
3. **T6's local-constancy argument.** The random neighbourhood `eps(omega)`
   depends on `omega`; verify the dominated-convergence step is legitimate and
   that the single common probability space (raw law independent of `e`) is
   really available.
4. **T4's block bound for SR.** The claim is `y^+ >= 0` always and a single step
   with `z >= log A + 1/2` alarms from any state. Check against
   `p7/detectors.py::sr_update` (`log_r_plus = yp + z - 0.5`, inclusive `>=`).
5. **T9's flip classification.** Verify the four conditions of a supercritical
   flip are all checked and none assumed, and that the branch is the *complete*
   set of 2-cycles on the measured map (the scan found no asymmetric one; the
   algebra only characterises symmetric ones).
6. **The T11 residual.** Predicted vs measured `ACF1` differ by up to `16` chain
   standard errors while agreeing to `0.0174` absolute. Determine whether the
   PCHIP interpolation and the sub-sampled `pi` account for it, or whether
   something is wrong.
7. **The one-signed `R'(0)` bias** (`0.14%–1.6%` below P3, 8/8 cells, both seed
   families). P5 attributes it to finite-difference concavity. Verify.
8. **The oddness residual** (up to `1.6x` a `t_7` batch interval). P5 attributes
   it to 8-batch interval calibration. Verify, or find the asymmetry.
9. **The dispersion optimum.** The headline operational finding. Re-derive
   `argmin_rho RMS` independently and check the ARL co-optimum in 7/8 cells.
10. **The bimodality onset.** Re-run the density contrast with a different seed
    family and check the `4.1x–9.8x rho_c` onsets.
11. **(H2)/(H3).** Try to prove them, or find a counterexample. This is the one
    gap that would upgrade T8–T10 from conditional to exact.

## 12. Unresolved discrepancies

| item | size | P5's position |
|---|---|---|
| T11 map-vs-chain `ACF1` | `<= 0.0174` absolute, up to `16` chain s.e. | prediction's own error budget unquantified; the identity is proved |
| `R'(0)` vs P3 | `0.14%`–`1.6%`, one-signed, 8/8 | finite-difference bias; immaterial to every theorem |
| oddness residual | `<= 0.011` absolute, `<= 1.6x` `t_7` CI | interval calibration; T3 is exact |
| `s` monotonicity beyond `e = 2` | genuine, reproducible | outside the region any `rho <= 1` probes; handled by the `sup|R| < 2` bound |
| SR `m=3,5` branch at `rho_c` | root below the `0.005` grid | exact amplitude at `rho_c` is `0`; reported as unresolved, not absent |

## 13. Focused tests

45, all passing: `tests/test_correspondence.py` (frozen-semantics
correspondence, the truncated-denominator convention, the P3 boundary table
pinned by value), `tests/test_results.py` (every headline claim asserted against
a produced artifact), `tests/test_protected_tree.py` (294-file SHA-256 check and
a worktree-scope check).

```bash
/Users/suzhe/ReBaseGuard/level4/.venv/bin/python -m pytest \
  level4/closure_proofs/p5_nonlinear_dynamics/tests -q
```

## 14. Protected-tree status

```
294 files under m_gt_1_priority1, sr_derivative_priority2,
m_rho_stability_priority3, p4_theory_generalization,
p7_statistical_consequences, stage_d, level4/src
SHA-256 before == SHA-256 after   (results/protected_hashes_{before,after}.txt)
```

`git status --porcelain` shows exactly one untracked path:
`level4/closure_proofs/p5_nonlinear_dynamics/`. **No commit, no push.**

## 15. Exact files added

```
p5_nonlinear_dynamics/
  README.md  DEFINITION_AUDIT.md  THEOREM.md  PROOF.md  NONLINEAR_MAP.md
  STATIONARY_DYNAMICS.md  NUMERICAL_CORRESPONDENCE.md  ADVERSARIAL_REVIEW.md
  LIMITATIONS.md  P6_HANDOFF.md  CODEX_HANDOFF.md  CLOSURE_REPORT.md
  reproduce.sh  run_lean.py
  src/rebaseguard_p5/{__init__,kernel,chain}.py
  experiments/{run_nonlinear_map,run_map_tail,run_skeleton,run_chain,
               run_stress,run_density,analyze_map,analyze_chain,
               audit_hypotheses,make_onset,make_figures,make_provenance}.py
  tests/{test_correspondence,test_results,test_protected_tree}.py
  lean/{NonlinearSkeletonP5.lean, AxiomAudit.lean}
  results/*.json  results/_log_*.txt  results/chain_samples.npz
  results/protected_hashes_{before,after}.txt
  figures/*.png  figures/figure_index.json
```

Nothing outside this directory is created, modified or deleted.

## 16. Recommended independent replay

```bash
bash level4/closure_proofs/p5_nonlinear_dynamics/reproduce.sh
```

~55 min single-core. For an independent-seed adjudication, re-run the map and
the density experiments with a third seed family:

```bash
PY=level4/.venv/bin/python
C=level4/closure_proofs/p5_nonlinear_dynamics
$PY $C/experiments/run_nonlinear_map.py --seed-family 20270214 --tag 3 \
    --out nonlinear_map_codex.json
$PY $C/experiments/analyze_map.py nonlinear_map_codex.json map_analysis_codex.json
$PY $C/experiments/run_chain.py --seed-family 20270214 --tag 30 \
    --out chain_sweep_codex.json
$PY $C/experiments/run_density.py --seed-family 20270214 --tag 61 \
    --out density_codex.json
```

The gates below should hold on any seed family.

## 17. Exact closure gates

| gate | threshold | measured |
|---|---|---|
| G1 chain correspondence | `tau` identical; `max abs e_start diff < 1e-13` | identical; `8.9e-16` |
| G2 `R'(0)` vs frozen P3 | `< 2%` relative, 8/8 cells | `0.14%`–`1.6%` |
| G3 saturation | `sup_e |R| < 2` in 8/8 | `0.908`–`1.585` |
| G4 forgetting | `|R| < 0.01` for `|e| >= 10`, 8/8 | `<= 0.0021` |
| G5 skeleton periods | `subset of {1,2}` in 8/8 | holds |
| G6 period-2 onset vs `rho_c` | `<= 0.0075` (1.5 scan steps), 8/8 | `<= 0.0055` |
| G7 2-cycle attracting | multiplier `< 1` wherever it exists | `<= 0.98` |
| G8 SNR at the boundary | `< 0.15` at the first resolvable `rho` | `<= 0.117` |
| G9 SNR anywhere | `< 2.5` | `<= 2.14` |
| G10 no feature at `rho_c` | 0 metrics rank `rho_c` first | 0 of 40 |
| G11 dispersion optimum | interior, `rho* > 1.4 rho_c`, `RMS(rho*) < 0.75 RMS(1)`, 8/8 | `rho*/rho_c = 1.5–4.9`; ratio `0.532–0.614` |
| G12 initial-condition independence | max `z < 4` over 176 cells | `3.88` (null 95th pct `4.17`) |
| G13 no heavy tail | kurtosis `< 3.1` in all cells | `<= 3.012` |
| G14 T11 cross-check | `abs gap < 0.02` | `<= 0.0174` |
| G15 `Gamma_eff` vs tangent | `< 0.25 x GammaTilde` | `0.086x`–`0.184x` |
| G16 no runaway | `global max |e| <= max(|e_0|, 6)` in every stress cell | holds |
| G17 bimodality onset | `> 3x rho_c` in every measured cell | `4.1x–9.8x` |
| G18 no metastability | residence `< 1.6` cycles; alternation `> 0.8` for `rho >= 0.6` | `<= 1.46`; `>= 0.86` |
| G19 Lean | 12 declarations, sorry-free, axioms subset of the three standard ones | holds |
| G20 protected tree | 294 files byte-identical; worktree scope = P5 only | holds |

All 20 are asserted by the test suite.

## 18. Reason for CLOSED_CANDIDATE

P5 produces a genuine nonlinear mechanistic contribution: an exact identity that
explains the local-to-global transition, four exact theorems that close every
stationary-law gap P7 left open, a conditional theorem set that simultaneously
*establishes* the bifurcation P5 was expected to find and *proves it cannot be
observed*, an exact identification of P7's empirical effective gain, and a new
interior operating-point optimum. It disproves the expected
`rho_c -> period-2 -> operational failure` narrative and replaces it with a
defensible mechanism, which is exactly the outcome the closure standard permits.

It is CLOSED_CANDIDATE rather than CLOSED because (H2)/(H3) are measured rather
than proved, the theorem constants are vacuous as rates, and the discrepancies
in §12 are documented rather than resolved. Codex adjudicates.
