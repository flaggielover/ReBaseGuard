# P8 priority dependency audit

Every premise P8 could rest on, its source priority, and the strength at which
P8 is permitted to use it. Written before implementation.

**Classification vocabulary** (as required by the campaign policy):

| class | meaning | P8 may … |
|---|---|---|
| `EXACT_THEOREM` | proved, unconditional within a stated frozen scope, or definitional-exact | use as a hypothesis of a P8 theorem |
| `CERTIFIED_NUMERICAL` | interval/Arb-certified number | use as a hypothesis, with the enclosure carried |
| `EMPIRICAL` | Monte Carlo estimate with stated uncertainty from a `CLOSED` priority | use as a *comparator* or a *reproduction target*; never as a theorem hypothesis |
| `CONDITIONAL` | theorem whose hypotheses are not verified for P8's cells | use only if P8 verifies or explicitly assumes the hypotheses, and says which |
| `PARTIAL_ONLY` | from `PARTIAL` P4/P5, or from `STAGE-D-PARTIAL` | use only inside the source's own stated scope, and never as a premise of a P8 claim that reaches outside it |
| `NOT_ALLOWED_AS_PREMISE` | explicitly excluded, rejected, or superseded | must not appear in any P8 derivation |

`CLOSED` at the anchor commit: P1, P2, P3, P6, P7. `PARTIAL`: P4, P5, Stage D.

---

## 1. Definitional / frozen-convention premises (Level 1–3, `CLOSED`)

| id | premise | source | class | P8 use |
|---|---|---|---|---|
| `C1` | two-sided CUSUM `S±_t = max(0, S±_{t-1} ± Z_t − k)`, `k = 1/2`, inclusive alarm tested **after** the update, plus-arm tie priority | Level 1–3 frozen model, imported read-only from `level4/src/rebaseguard_level4/frozen.py` | `EXACT_THEOREM` (definitional) | detector recurrence, unchanged |
| `C2` | symmetric two-chart SR log-domain recursion, both charts updated before an inclusive comparison, no head start | P2 `CLOSED`; restated as `p7/detectors.py::sr_update` | `EXACT_THEOREM` (definitional) | detector recurrence, unchanged |
| `C3` | `tau = inf{t >= 1 : alarm}`, no minimum dwell; `T_tau` includes the terminal increment | Stage D / P3 / P5 / P7 | `EXACT_THEOREM` (definitional) | stopping semantics, unchanged |
| `C4` | **convention A**: `w = min(m, tau)`, `zbar^A_m = (1/w) sum_{r<w} z_{tau-r}` | Stage D; `p5/LIMITATIONS.md` §1 makes it load-bearing | `EXACT_THEOREM` (definitional) | primary window convention |
| `C5` | convention B: fixed-`m` denominator on the same truncated window | `stage_d/src/stopped.py::gamma_m("B")` | `EXACT_THEOREM` (definitional) | declared **alternative** convention; reported beside A, never merged |
| `C6` | reference update `e_{j+1} = rho (e_j + zbar_m) + (1-rho) fresh`, `fresh` independent of the cycle with variance `1/m` | Stage D / P5 T1 / P6 / P7 | `EXACT_THEOREM` (definitional) | chain semantics, unchanged |
| `C7` | frozen Gaussian operating point `ARL_0 = 465.50394`; CUSUM `h = 5`, SR `A = 520.886133602749` | `stage_d/results/calibration_d1.json`, `d3_nongaussian.json` | `EXACT_THEOREM` (definitional constant) / the SR value is `PARTIAL_ONLY` as a *measurement* | used as the frozen ARL-match target for every P8 family |

`C5` note: `p5/LIMITATIONS.md` §1 states T1 and "essentially every P5 theorem"
**fail** under a fixed-`m` denominator. P8 therefore reports convention B as an
*empirical contrast only* and attaches **no** P5 theorem to it. This is the
`X4` exclusion respected, not violated: `X4` forbids *changing* convention A for
P5's claims; P8 measures B as a separate labelled object.

## 2. P1 / P2 / P3 (`CLOSED`)

| id | premise | source | class | P8 use |
|---|---|---|---|---|
| `A1` | `F'_{rho,m}(0) = rho (1 - GammaTilde_m)`, `GammaTilde_m = E_0[A_m T_tau]`, frozen Gaussian CUSUM | P1 | `EXACT_THEOREM` | the Gaussian anchor of P8's generalised identity; P8's `f = gaussian` column must reduce to it |
| `A2` | same for frozen symmetric two-chart SR | P2 | `EXACT_THEOREM` | as `A1`, SR column |
| `A3` | `rho_c(D,m) = 1/|1 - GammaTilde|`; `rho < rho_c` locally attracting, `> rho_c` locally repelling; `rho_c <= 1 <=> GammaTilde >= 2` | P3 `THEOREM.md` §4–§5 | `EXACT_THEOREM` | applied verbatim to every P8 `(D, f, m)` cell **once** P8 supplies a valid `Gamma` for that cell (see `B1`) |
| `A4` | the P3 regime audit table (all seven `GammaTilde` regimes, absolute-value form) | P3 | `EXACT_THEOREM` | P8 classifies each cell by that table; no regime is assumed |
| `A5` | exact finite-support witnesses `GammaTilde = 15/2` (CUSUM-witness) and `4, 3, 8/3, 12/5` (SR-witness, `m = 1,2,3,5`) | P3, `EXACT_SYMBOLIC` | `EXACT_THEOREM` | used as an exact regression test of the **`rho_c` arithmetic** (`tests/test_metrics.py::test_p3_exact_witness_values_round_trip`). P8 does **not** re-implement the finite-support detectors, so these do not anchor the Monte Carlo estimator. That estimator is anchored instead by P8's own exact construction: a degenerate detector (`threshold = 0`) alarms at `tau = 1` on every path, so `Gamma_A(m) = E[eps psi(eps)] = 1` exactly for every family and every `m`, and `R_m = (1 - 1/m)` exactly. Both are asserted in `tests/test_metrics.py` |
| `A6` | P3's measured Gaussian `GammaTilde` and `rho_c` values | P3 `boundary_table.json`, self-labelled `EMPIRICAL_ONLY` | `EMPIRICAL` | **reproduction target** `RE1`; not a premise |

## 3. P4 (`PARTIAL`)

| id | premise | source | class | P8 use |
|---|---|---|---|---|
| `B1` | abstract stopped-score derivative theorem: under hypotheses 1–9, `d/de E_e[H_tau]|_0 = E_0[H_tau S_tau]`, `S_tau = sum_{t<=tau} f'/f (Z_t)` | `location_family/THEOREM.md` §1; `decision.json` records the human theorem as `PROVED UNDER EXPLICIT ANALYTIC HYPOTHESES` | `CONDITIONAL` **and** `PARTIAL_ONLY` | P8 may cite it only as a *conditional* result and must (i) verify hypotheses 1–3 for its own `H_tau = zbar^A_m` and (ii) state hypotheses 7–9 as assumptions per family. P8 never calls it closed |
| `B2` | `Gamma_f = E_0[Z_tau sum psi(Z_t)]`, `F'_rho(0) = rho(1 - Gamma_f)`, `m = 1` raw reuse | `location_family/PROTOCOL.md` §2 | `CONDITIONAL` / `PARTIAL_ONLY` | P8's `m = 1` column is exactly this estimand; used as **reproduction target** `RE2` |
| `B3` | P4's measured `Gamma_f` for `gaussian, t10, t5, t3, contam0.05, contam0.1` | `location_family/results/correspondence.csv` | `PARTIAL_ONLY` | reproduction target `RE2` only. P4's own numerical gate **FAILED** (t3 replication 4.605% > 3%), so these are not premises for anything |
| `B4` | the six family definitions (`draw`, `psi`, standardisation) | `location_family/src/.../route_a.py` | `EXACT_THEOREM` (definitional) | P8 re-implements them independently and cross-checks against `route_a.py` numerically and against `log_density` by finite differences |
| `B5` | "the result is not distribution-free, universal, detector-independent, or a class-wide instability certificate" | `location_family/FINAL_REPORT.md` §A | `EXACT_THEOREM` (negative scope statement) | binding on P8: P8 may not close this gap by assertion, only by measurement, and only cell by cell |
| `B6` | P4's Lean/Arb layer | `decision.json`: `authorized: false, status: NOT RUN` | `NOT_ALLOWED_AS_PREMISE` | P8 starts no formal layer |

## 4. P5 (`PARTIAL`)

Authoritative boundary: **T1–T5, T7, T11 may be used only within their stated
scope**, which `p5/LIMITATIONS.md` §1 fixes as *frozen Gaussian core, convention
A, `Delta = 0`, `rho in [0,1]`, `m in {1,2,3,5}`*.

| id | premise | class | P8 use |
|---|---|---|---|
| `D1` | T1 raw-mean identity `e_{j+1} = rho·Rbar_j + (1-rho)·fresh_j` | `PARTIAL_ONLY` (Gaussian scope) | P8 does **not** import it outside Gaussian. P8 states its own algebraic lemma `L0` (§ `THEORY.md`), which is a one-line change of variables valid for any iid innovation law, and records the Gaussian correspondence |
| `D2` | T2 `rho`-factorisation, T3 symmetry | `PARTIAL_ONLY` (Gaussian scope) | Gaussian column only; P8 re-derives symmetry per family from evenness of `f` (t and contaminated families are even; this is checked, not assumed) |
| `D3` | T4/T5 uniform `E[tau]` and moment bounds, T6 Feller, **T7 unique invariant law + uniform ergodicity + all moments finite** | `PARTIAL_ONLY` (Gaussian scope) | **not available for non-Gaussian cells.** Consequence: every non-Gaussian chain result in P8 is reported in **finite-horizon** language with an explicit burn-in, never as a stationary quantity |
| `D4` | T11 `ACF1 = rho(1 - Gamma_eff)` | `PARTIAL_ONLY` (needs T7's `pi`) | Gaussian only; not used for non-Gaussian cells |
| `D5` | T8–T10 (conditional on measured (H1)–(H3)) | `CONDITIONAL` / `PARTIAL_ONLY` | not used |
| `D6` | P5 numerics: `rho* = 0.20`, `Gamma_eff = 1.48..2.19`, `e*(1) = 1.04`, bimodality onset | `NOT_ALLOWED_AS_PREMISE` (`X9`) | not used, not quoted as a constant |
| `D7` | premise-label `P8` = RMS/ARL co-optimality | `NOT_ALLOWED_AS_PREMISE` for this priority | out of scope; see `P8_DEFINITION_AUDIT.md` §5 `U1` |

## 5. P6 (`CLOSED`, with its limitations intact)

| id | premise | class | P8 use |
|---|---|---|---|
| `E1` | **addressable primitive CRN standard**: every draw a pure function of `(namespace, cell, replicate, cycle, primitive_type, primitive_index)`; no live-set, execution-order, branch-count or policy component; block-materialised so overflow is not special | procedural standard, `EXACT` | **inherited verbatim** by P8's primitive field (`src/rebaseguard_p8/primitives.py`), extended from normals to a family-independent uniform channel pair |
| `E2` | `GATE_9 = PASS`, `CRN_PRIMITIVE_IDENTITY = PASS`, `LIVE_SET_DEPENDENCE = NO`, `EXECUTION_ORDER_DEPENDENCE = NO` | `EMPIRICAL` + procedural | P8 re-establishes the analogous property for its own field with its own test; it does not inherit the *result*, only the *standard* |
| `E3` | L3: no P6 cell recovers nominal in-control performance; the best matched-cost policy reaches ~1/3 of nominal `ARL_0` | `EMPIRICAL` (Gaussian) | comparator only |
| `E4` | SAW, its calibrated constants, `rho_max`, the `s1` truncated-window variance, the 6/8 calibration convergence | `NOT_ALLOWED_AS_PREMISE` | P8 evaluates **no policy**. P6's calibration limitations (2/8 nonconverged cells, sparse `s1`, unverified final fixed point) therefore do not propagate into P8 |
| `E5` | T6-B closed-loop stationarity for memoryless policies | `CONDITIONAL` / Gaussian | not used |

## 6. P7 (`CLOSED`)

| id | premise | class | P8 use |
|---|---|---|---|
| `G1` | **THEOREM P7-A**: full reset ⟹ conditional independence ⟹ `E[tau_j] = E[A(e_j)]`, `A(x) = E[tau | reset, z_t ~ N(-x,1)]`, `A` even | `EXACT_THEOREM` (frozen Gaussian) | P8 restates it as `P8-T2` for a general iid innovation law `f` — the proof uses only *reset* and *iid*, never Gaussianity — and marks the restatement as P8's own, with P7 credited for the Gaussian case |
| `G2` | P7-B conditional-exact stationary identity | `CONDITIONAL` | not used for non-Gaussian (no `pi`) |
| `G3` | P7's measured ARL/FAP/delay/MSE/ACF1 degradation across `104` Gaussian cells; `S20`: no cell within a factor of 4 of nominal | `EMPIRICAL` | comparator and reproduction target `RE4` |
| `G4` | adjudicated conclusion: `rho_c` is a **local mathematical boundary, not an operational safety boundary** under P7's frozen criterion | `EMPIRICAL` (adjudicated) | P8 tests whether this *transfers* across families and detectors; it is P8's `H3` |
| `G5` | `X6` / rejected candidate **P7-E**: the derivative of `E[e_1]` does **not** determine the derivative of `E[M(e_1)]` | `NOT_ALLOWED_AS_PREMISE` | binding: **P8 may never infer an operational consequence from `Gamma` or `rho_c`.** Every operational number in P8 is measured |
| `G6` | `ACF1(e) < 0` in every P7 cell, magnitude growing with `rho` | `EMPIRICAL` | comparator only |

## 7. Stage D (`STAGE-D-PARTIAL`)

| id | premise | class | P8 use |
|---|---|---|---|
| `S1` | family-specific **CUSUM** thresholds `h_f` calibrated to `ARL_0 = 465.50394`: `5.0, 5.234517732360302, 5.669498491821448, 6.337011391962933, 7.671712168173407, 9.381983052368211` | `PARTIAL_ONLY` | adopted as **frozen operating-point conventions** (the same way P4 adopted them: "copied exactly … never recalibrated"). P8 independently **re-measures the achieved `ARL_0`** at each and reports the residual |
| `S2` | Stage-D `Gamma_psi = E[(1/w) sum psi(z_{tau-i}) · sum psi(z_t)]` values | `NOT_ALLOWED_AS_PREMISE` **as a comparator for P8's estimand** | this is a **different estimand** (`psi` in *both* factors) and corresponds to a score-transformed reuse rule, not the frozen raw-mean update `C6`. P8 measures it separately, only to document the difference (`RE3`) |
| `S3` | D2.5: the `GammaTilde_m = 2` crossing along `m` at `rho = 1` is `MATHEMATICAL, NOT OPERATIONAL` | `EMPIRICAL` | consistent-with check |
| `S4` | Stage-D SR Gaussian threshold `A = 520.886133602749` | `PARTIAL_ONLY` measurement, used as a frozen constant | P8 re-measures its achieved `ARL_0` |

---

## 8. Premises P8 needs and **no** priority supplies

| id | gap | P8's response |
|---|---|---|
| `N1` | SR thresholds `A_f` for the five non-Gaussian families | P8 calibrates them itself. Declared in `P8_DEFINITION_AUDIT.md` §7 **before** any result; labelled `NEW_P8_CALIBRATION`; full bisection trace stored |
| `N2` | any stationarity/ergodicity theorem for a non-Gaussian reference chain | none exists. **All** non-Gaussian chain results are finite-horizon with a declared burn-in, and are never called stationary |
| `N3` | a generalisation of `A1`/`A2` to convention-A windows with `m > 1` under a general `f` | P4's `B1` is `m = 1` raw reuse. P8 proves its own `P8-T1` (an application of `B1` to `H_tau = zbar^A_m`, with hypotheses 1–3 verified and 7–9 assumed and stated) |
| `N4` | any theorem linking `Gamma` to an operational metric | forbidden by `G5`. P8 measures both and reports the relationship as `EMPIRICAL` only |
| `N5` | prior art adjudication | none exists anywhere in ReBaseGuard (`X10`). P8 runs its own audit and reports conservatively |
