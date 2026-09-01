# P6 dependency ledger

**Status: MANDATORY PREREQUISITE.** No P6 design document, method, theorem
target or experiment may cite a scientific fact that is not classified here.

This ledger exists because P6 is the first *prescriptive* campaign in
ReBaseGuard. A diagnostic campaign that leans on a shaky premise produces a
wrong description; a prescriptive campaign that leans on a shaky premise
produces a wrong recommendation that someone may deploy. The bar is therefore
higher, and the mechanism for keeping it high is this table.

## 0. Classification scheme

| tier | meaning | may P6 use it as a premise? |
|---|---|---|
| `AUTHORITATIVE_CLOSED` | established by a campaign whose `SCIENTIFIC_VERDICT = CLOSED` and independently adjudicated | **yes**, unconditionally |
| `AUTHORITATIVE_PARTIAL` | from a campaign at `PARTIAL`; the specific claim survived adjudication but the campaign did not close | **yes, with the narrowing recorded inline**; never as the sole support for a headline |
| `PROVISIONAL_P5` | from `p5_nonlinear_dynamics`, `CLOSED_CANDIDATE / PENDING_CODEX` | **no** — may be used only inside a branch of `P5_ADJUDICATION_CONTINGENCIES.md`, never in a P6 statement that must survive all branches |
| `EMPIRICAL_HINT` | a measured regularity, from any campaign, that motivates a design but supports no guarantee | **no** — motivation and grid-selection only |
| `DESIGN_HYPOTHESIS` | invented by P6; not established anywhere | **no** — must be tested by P6 itself |
| `NOT_ALLOWED_AS_PREMISE` | refuted, out of scope, or a known trap | **never** |

Two orthogonal annotations are carried alongside the tier:

* **rank** — the P3/P7 evidence hierarchy (`1 EXACT_SYMBOLIC` … `5 EMPIRICAL_ONLY`,
  `6 INCONCLUSIVE`). A fact can be `AUTHORITATIVE_CLOSED` and still rank 5: the
  campaign closed, but the number is a Monte Carlo estimate.
* **P6 exposure** — what breaks in P6 if the fact turns out to be wrong.

---

## 1. Frozen model semantics (P1–P3, Stage D)

These are definitions, not findings. They are the ground on which everything
else stands, and P6 may not alter any of them.

| # | fact | source | tier | rank | P6 exposure |
|---|---|---|---|---|---|
| D1 | Cycle semantics: detector reset to `plus=minus=0` at each cycle start, no head start, no minimum dwell | `stage_d/src/chain.py`, `p7/.../chain.py` | `AUTHORITATIVE_CLOSED` | 1 | total — P6 must not change detector semantics |
| D2 | `z_t = raw_t - e_j` with `e_j` held constant over cycle `j`; `raw_t ~ N(0,1)` iid and independent of `e_j` | same | `AUTHORITATIVE_CLOSED` | 1 | total |
| D3 | `tau_j = inf{t >= 1 : alarm after the update at step t}`, two-sided, inclusive post-update test, no truncation | same | `AUTHORITATIVE_CLOSED` | 1 | total |
| D4 | Terminal increment included in the reuse window | same | `AUTHORITATIVE_CLOSED` | 1 | total |
| D5 | **Convention A**: `w_j = min(m, tau_j)`, denominator the *truncated* length `w_j` | same | `AUTHORITATIVE_CLOSED` | 1 | total; see `X4` |
| D6 | `e_{j+1} = rho (e_j + zbar_j) + (1-rho) fresh_j`, `fresh_j ~ N(0,1/m)` drawn after the alarm, independent of the cycle | same | `AUTHORITATIVE_CLOSED` | 1 | total; P6 generalises `rho -> rho_j`, `m -> m_j` **only in this line** |
| D7 | Frozen detectors: CUSUM `k=1/2, h=5`; SR two-chart log-domain, `A = 520.886133602749`; ARL-matched at `A(0) ~ 465` | `frozen.py`, `stage_d/src/stopped.py` | `AUTHORITATIVE_CLOSED` | 1 | total |
| D8 | Sign convention: a process shift `+Delta` enters as `e <- e - Delta`; shift and reference error share a coordinate | `p5/DEFINITION_AUDIT.md` §2.3 | `AUTHORITATIVE_CLOSED` | 1 | high — the blind-spot geometry of §4 depends on it |
| D9 | `(e_j)` is a time-homogeneous Markov chain on `R` under a **fixed** `(rho, m)` | `p5/DEFINITION_AUDIT.md` §2.10 | `AUTHORITATIVE_CLOSED` | 1 | **P6 breaks time-homogeneity by design** — see `H7` |

## 2. Local theory (P1–P3)

| # | fact | source | tier | rank | P6 exposure |
|---|---|---|---|---|---|
| L1 | Local derivative identity `F'_{rho,m}(0) = rho (1 - GammaTilde_{D,m})` | P1/P2 closed | `AUTHORITATIVE_CLOSED` | 1 (identity) | low — P6 uses it only as a landmark |
| L2 | `GammaTilde_{D,m} = E_0[A_m T_tau]` under convention A | P2 closed | `AUTHORITATIVE_CLOSED` | 1 | low |
| L3 | **Definition** `rho_c(D,m) := 1/|1 - GammaTilde_{D,m}|` | P3 closed | `AUTHORITATIVE_CLOSED` | 1 | low |
| L4 | **Numerical values** `rho_c in [0.061, 0.109]`, `GammaTilde in [11.8, 17.3]` over `D x m in {1,2,3,5}` | `m_rho_stability_priority3/results/boundary_table.json` | `AUTHORITATIVE_CLOSED` | **5** (`EMPIRICAL_ONLY` in P3's own hierarchy) | low — landmark only; P6 must never make a threshold out of it |
| L5 | Below `rho_c` the origin is locally attracting for the linearised map; above it, locally repelling | P3 closed | `AUTHORITATIVE_CLOSED` | 1 (given L4) | low — a *local linear* classification only |

> **L4/L5 carry a standing warning.** They are true and they are useless as a
> safety rule. See `X1`.

## 3. P4 — general location family

| # | fact | source | tier | rank | P6 exposure |
|---|---|---|---|---|---|
| G1 | The derivative theorem generalises beyond Gaussian to a general location family, **with G3's unproved `iff` wording narrowed in adjudication** | `p4_theory_generalization` (`PARTIAL`) | `AUTHORITATIVE_PARTIAL` | 3–4 | **none** — P6 is confined to the frozen Gaussian core |
| G2 | Three preregistered P4 gates remain failed (`t1p5` accuracy, one `skewnormal4` SR cell, Gaussian-consistency statistic mis-specified) | `p4/CLOSURE_REPORT.md` §1 | `AUTHORITATIVE_PARTIAL` | — | none |
| G3 | Cauchy cells recorded `COUNTEREXAMPLE-NOT-DEMONSTRATED` (`E|A_1| = infinity`) | `p4/CLOSURE_REPORT.md` §1.3 | `AUTHORITATIVE_PARTIAL` | — | none |
| G4 | **P4 novelty is not adjudicated** | `p4/NOVELTY_AUDIT.md` | `NOT_ALLOWED_AS_PREMISE` (for any novelty claim) | — | see `NOVELTY_AUDIT_PLAN.md` |

> P6 takes **nothing** from P4. Recorded here so that a future reviewer can see
> the omission was deliberate, not an oversight. Any P6 extension outside the
> Gaussian core is P8 territory and inherits P4's `PARTIAL` status.

## 4. P7 — statistical consequences (CLOSED)

| # | fact | source | tier | rank | P6 exposure |
|---|---|---|---|---|---|
| S1 | **THEOREM P7-A (exact).** Conditionally on `e_j`, the cycle is a fresh cycle at innovation mean `-e_j`. Hence `ARL_0 = E_pi[A(e)]` and `E[delay | Delta] = E_pi[A(e - Delta)]` for **any** entering-error law | `p7/THEORY_BRIDGE.md` §P7-A | `AUTHORITATIVE_CLOSED` | **1** (structural; exact, unmeasured) | **critical** — P6's whole objective apparatus rests on S1 |
| S2 | The response function `A(e)`: `A(0)=465`, `A(0.1)=348`, `A(0.2)=191`, `A(0.5)=38`; even, non-increasing in `|e|` on the measured range | `p7/results/response_curves.json` | `AUTHORITATIVE_CLOSED` | 5 | high — sets the *scale* of every safety target |
| S3 | Reuse-attributable in-control ARL loss `-39.5%` to `-50.6%` at `rho=1` vs the same-`m` fresh control, `PRACTICALLY_MATERIAL` in all 8 families | `p7/results/consequences.json` | `AUTHORITATIVE_CLOSED` | 5 | high — the headline P6 must beat |
| S4 | Absolute ARL loss vs nominal `A(0)~465`: `-83%` to `-90%` at `rho=1`; `-65%` to `-83%` even at `rho=0` | same | `AUTHORITATIVE_CLOSED` | 5 | high — **fresh-only is not safe either**; this is what makes P6 non-trivial |
| S5 | Mean detection delay at `Delta=1` rises `10.4 -> 52.8..66.1` (`+360%` to `+540%`) | same | `AUTHORITATIVE_CLOSED` | 5 | high |
| S6 | Discrimination ratio `R_Delta = E[tau_Delta]/E[tau_0]` rises `0.022 -> 1.06` at `m=1, rho=1`: the shifted cycle becomes **longer** than the in-control cycle | same | `AUTHORITATIVE_CLOSED` | 5 | high |
| S7 | `FAP(100)` rises `~0.19 -> 0.82..0.90` | same | `AUTHORITATIVE_CLOSED` | 5 | medium |
| S8 | **Finite-cycle collapse**: the cycle immediately after the first re-baselining has mean length `5.6..9.4` under full reuse, against `463..474` for cycle 1 — a `98%` collapse | same | `AUTHORITATIVE_CLOSED` | 5 | **critical** — forces recursive, multi-cycle evaluation (`EVALUATION_PROTOCOL.md` §5) |
| S9 | **The failure mode is a right tail.** CUSUM `m=1, rho=1, Delta=1`: mean `52.6`, **median `7`** (below the nominal `10.35`), `q95 = 275`, `P(delay>100) = 11.4%` | `p7/results/delay_validation.json` | `AUTHORITATIVE_CLOSED` | 5 | **critical** — forces a tail objective (`SAFETY_OBJECTIVES.md` §3) |
| S10 | Blind-spot mechanism: roughly one cycle in nine enters with `e` near the post-change mean and is effectively blind; `P(|e - Delta| < 0.2)` tabulated per cell | `p7/STATISTICAL_CONSEQUENCES.md` §4 | `AUTHORITATIVE_CLOSED` | 5 | **critical** — the mechanism Family B targets |
| S11 | **Boundary verdict `LOCAL-MATHEMATICAL, NOT OPERATIONAL`**: `rho_c` ranks first in at most 3 of 8 families over five pre-specified metrics, against a pre-committed threshold of 4 | `p7/results/boundary_verdict.json` | `AUTHORITATIVE_CLOSED` | 5 (pre-committed test) | **critical, negative** — see `X1` |
| S12 | In-control ARL is **maximised at `rho ~ 0.14..0.25`**, i.e. `1.25x..4.1x rho_c`, `+7.2%..+14.8%` over `rho=0`, at `z >= 13.5` in all 8 families — labelled **EXPLORATORY, not a recommendation** by P7 | `p7/results/adversarial.json` | `EMPIRICAL_HINT` | 5 | medium — motivates the interior-region hypothesis, supports nothing |
| S13 | Detector-agnosticism: every P7 consequence agrees between CUSUM and SR to within a few percent | `p7/STATISTICAL_CONSEQUENCES.md` §6 | `AUTHORITATIVE_CLOSED` | 5 | medium — justifies the two-detector reproduction gate, not a transfer guarantee |
| S14 | Reuse-attributable ARL loss **grows** with `m` (`-40%` at `m=1` to `-51%` at `m=5`); absolute damage is **worst** at small `m`; `m=1` is unusable under any `rho` | same §5 | `AUTHORITATIVE_CLOSED` | 5 | high — the two facts point opposite ways; `m` control must resolve them |
| S15 | `rho >= 0.5` is where collapse starts: ARL roughly halves between `rho=0.25` and `rho=1`, reference MSE roughly triples | same §6 | `AUTHORITATIVE_CLOSED` | 5 | medium |
| S16 | **PROPOSITION P7-B** `ACF1 = rho(1 - Gamma_eff)` — exact **conditionally on** a stationary law with finite fourth moment | `p7/THEORY_BRIDGE.md` §P7-B | `AUTHORITATIVE_CLOSED` **as a conditional**; its hypothesis is `PROVISIONAL_P5` (see `P1` below) | 4 | low — diagnostic only |
| S17 | **CONDITIONAL P7-C / P7-D** (mass escape; ARL-deficit plug-in) — conditional on the same stationary hypotheses plus an empirically checked sign condition | same | `AUTHORITATIVE_CLOSED` as conditionals | 4 | low |
| S18 | **Candidate P7-E rejected**: the derivative of `E[e_1]` does not determine the derivative of `E[M(e_1)]` while `e_1` remains random. No first-order monitoring-functional transfer theorem exists | `p7/THEORY_BRIDGE.md`; `p7/EVIDENCE_BOUNDARY.md` | `NOT_ALLOWED_AS_PREMISE` | — | **high** — forbids the most tempting P6 shortcut; see `X6` |
| S19 | **Stationary-law gaps left open by P7**: existence, uniqueness, second moment, fourth moment, geometric convergence — all *evidenced, not proved* at P7 | `p7/EVIDENCE_BOUNDARY.md` | open gap | — | **critical** — P5 claims to close all five; until adjudication P6 must be writable without them |
| S20 | No cell in P7's whole measured grid reaches within a factor of 4 of the nominal `ARL_0` | `p7/P6_HANDOFF.md` §6 | `AUTHORITATIVE_CLOSED` | 5 | high — P6 cannot promise recovery of nominal performance |
| S21 | P7 hands over **no** algorithm, correction term or bias adjustment, and claims **no** safe `rho` | `p7/P6_HANDOFF.md` §7 | `AUTHORITATIVE_CLOSED` (a scope statement) | — | — |

## 5. P5 — provisional, PENDING_CODEX

**Every row in this section is `PROVISIONAL_P5` and may not appear in a P6
statement that must survive all three adjudication branches.** The `if rejected`
column is what `P5_ADJUDICATION_CONTINGENCIES.md` acts on.

| # | claim | P5 tier | risk | if rejected / narrowed |
|---|---|---|---|---|
| P1 | **T7** — unique invariant `pi`, uniform ergodicity, finite moments of every order, for every `(D, m, rho in [0,1])` incl. `rho = 1` | EXACT | **low-medium**; the two-step Doeblin construction is the named attack target #1 | all stationary-law objectives lose their well-posedness guarantee; P6 falls back to finite-horizon empirical risk (Branch C) |
| P2 | **T1** — raw-mean identity `e_{j+1} = rho Rbar_j + (1-rho) fresh_j`, `Rbar_j` = mean of at most `m` iid `N(0,1)` draws | EXACT | **lowest**; pure algebra, reproduced bit-numerically (`max abs diff 8.9e-16`, `tau` identical 12/12) | Family F and theory targets T6-A/T6-D collapse; the observability design of §7 survives (it never uses `Rbar`) |
| P3 | **T2** — `E[e_{j+1}|e] = rho R(e)`; `Var(e_{j+1}|e) = rho^2 S(e) + (1-rho)^2/m` | EXACT (given T1) | lowest | as `P2` |
| P4 | **T5** — state-independent one-step moment bound `sup_e E[e_{j+1}^2|e] <= rho^2 C_D + (1-rho)^2/m` | EXACT | low; but the constants `C_CUSUM <= 9.9e8`, `C_SR <= 1.4e11` are **vacuous as rates** against a measured `sup_e A(e) ~ 465` | theory target T6-B loses its cheapest route |
| P5 | **T9/T10** — `rho_c` is a genuine supercritical flip bifurcation of the skeleton, and provably invisible against the `O(1)` noise floor (`SNR -> 0`) | CONDITIONAL on measured (H1)–(H3) | medium; (H2)/(H3) are measured on a finite grid, `s` is **not** globally monotone | P6 is unaffected — it never uses the bifurcation. Only the *explanation* of `S11` weakens; `S11` itself is P7's and stands |
| P6 | **T11** — `ACF1 = rho(1 - Gamma_eff)` with `Gamma_eff = 1 + E_pi[e^2 s(e)]/E_pi[e^2]` | EXACT (uses T7) | medium; the predicted-vs-measured residual is `<= 0.0174` absolute but up to `16` chain s.e. (P5 §12, unresolved) | diagnostic only; nothing in P6 depends on it |
| P7 | **Interior dispersion optimum**: stationary reference RMS minimised at `rho* = 0.16..0.30 = 1.5x..4.9x rho_c`, `25..30` s.e. deep, 8/8 cells; `RMS(rho*)/RMS(1) = 0.53..0.61` | NUMERICAL EVIDENCE | medium | **the headline provisional fact.** Its *existence* motivates P6's interior hypothesis; its *values* are never design constants |
| P8 | **RMS/ARL co-optimality**: `argmin_rho RMS` and `argmax_rho ARL_0` coincide in 7/8 cells, adjacent grid point in the 8th; P5 explicitly asks P6 to re-verify | NUMERICAL EVIDENCE | medium-high (a 7/8 coincidence on a coarse grid) | if it fails, RMS ceases to be a legitimate surrogate for ARL and P6 must optimise ARL directly |
| P9 | **`m` monotonicity**: increasing `m` lowers `sup|R|`, lowers `S(0)` (`4.04 -> 1.59`), lowers stationary RMS at every `rho`, raises ARL, raises `rho_c`, lowers `rho*`; measured only for `m <= 5`, no saturation | NUMERICAL EVIDENCE | medium | `m` remains a control variable; only the *direction* prior is lost. Note this points **against** `S14`'s reuse-attributable trend — see `X8` |
| P10 | **One-step forgetting**: from `e_0 = 10^6`, mean `|e_1| = 0.83`; `|R| <= 0.0021` and `S = 1.000` for `|e| >= 10`; global max `|e|` over every stress trajectory after cycle 0 is `5.43` | EXACT (T1/T5) + NUMERICAL | low | P6 loses its licence to omit anti-windup / reset / divergence guards and must add them defensively |
| P11 | **`S(e)` varies ~8x** over `e in [0,4]` (`4.04` at `0`, `0.48` near `e=0.5`) — the structure a state-dependent controller would exploit | NUMERICAL EVIDENCE | medium | Family A/E lose their stated motivation but not their testability |
| P12 | **Deterministic flip / exact 2-cycle branch** `s(e*) = 1/rho`, `e*(1) = 0.60..1.04` | CONDITIONAL | medium | **no P6 design rule may be derived from the bifurcation structure** in any branch — see Branch B |
| P13 | Stationary reference law is **platykurtic** (excess kurtosis `-0.01` to `-1.02`, never positive); **bimodal** above `rho = 0.41..0.59`; P5 *rejected its own* draft unimodality claim | NUMERICAL EVIDENCE | low-medium | affects tail-metric calibration only |
| P14 | Detector-agnosticism of the *map*: `e*(rho=1)` `1.0434` (CUSUM) vs `1.0418` (SR); only the linearisation at `0` differs (~9%) | NUMERICAL EVIDENCE | low | reinforced by `S13`, which is closed |
| P15 | T1 **fails** under a fixed-`m` denominator on a truncated window; every P5 theorem is specific to convention A | EXACT (asserted by test) | lowest | — (this is a *limitation*, and a warning: see `X4`) |

## 6. Empirical hints (motivation only, from closed sources)

| # | hint | source | use |
|---|---|---|---|
| E1 | The tolerable reference RMS implied by `A`'s steepness is of order `0.05`, i.e. `E_pi[e^2] <~ 0.0025`; **every** configuration P7 measured is `30x` to `400x` above that | `p7/P6_HANDOFF.md` §1 | sets the *aspiration*, and warns that P6 will not reach it. Success must be defined relatively, not against this |
| E2 | The ARL-vs-`rho` curve is non-monotone with an interior maximum (`S12`) | P7 (EXPLORATORY) | grid design: never use a `rho` grid that omits `[0.1, 0.35]` |
| E3 | Reference MSE roughly triples between `rho = 0.25` and `rho = 1` | P7 §6 | grid design |
| E4 | Chains mix within ~3 cycles empirically; P7 burn-in is 12 cycles | `p7/STATISTICAL_CONSEQUENCES.md` §5 | burn-in choice; **not** a mixing guarantee |

## 7. P6's own design hypotheses (nothing supports these yet)

| # | hypothesis | where tested |
|---|---|---|
| H1 | `zbar_j` (observable) is a usable proxy for `-e_j` (latent), with bias `R(e)` and conditional variance `S(e)` | `OBSERVABILITY_AUDIT.md` §3; Family A/E |
| H2 | `tau_j` (observable) is a usable proxy for `|e_j|`, because `A` is steeply decreasing in `|e|` (`S2`) | `OBSERVABILITY_AUDIT.md` §3; Family B/E |
| H3 | A filtered statistic over several cycles beats a single-cycle proxy, because the single-cycle proxy has `O(1)` noise against an `O(1)` signal | `P6_METHOD_CANDIDATES.md` Family E |
| H4 | Decoupling the fresh-baseline size `k_j` from the reuse window `m_j` is a legitimate and useful extra control | `P6_METHOD_CANDIDATES.md` Family C; `X4` |
| H5 | Fresh samples have an operational cost (`k_j` observations of post-alarm downtime, incurred only when `rho_j < 1`) that P5/P7 never modelled | `SAFETY_OBJECTIVES.md` §5 |
| H6 | State-dependent reuse beats the best fixed `rho` at equal sample cost | the whole campaign |
| H7 | A state-dependent policy makes `(e_j)` a **non-time-homogeneous, policy-dependent** chain, so `D9`, `P1` and every stationary-law statement need restating before use | `P6_THEORY_TARGETS.md` §T6-B |
| H8 | Since `Delta` is unknown at decision time, the blind-spot risk `S10` has **no** direct implementable proxy; reference-tail mass is the honest surrogate | `OBSERVABILITY_AUDIT.md` §5 |

## 8. Explicitly forbidden premises

| # | forbidden | why | authority |
|---|---|---|---|
| X1 | `rho < rho_c` (or `rho/rho_c`) as a safety rule, a controller or a success criterion | pre-committed test returned `LOCAL-MATHEMATICAL, NOT OPERATIONAL`; and the measured ARL optimum sits `1.25x..4.1x` **above** `rho_c`, inside the locally repelling region | `S11`, `S12`; reinforced by `P5` |
| X2 | "Stay below the bifurcation" / "suppress the period-2 orbit" as an objective | the orbit is not the harm; even on P5's own provisional numbers the optimum lies `2x..5x` above the bifurcation, i.e. **on** the bifurcated branch | `P7`, `P12` |
| X3 | Any assumption of a heavy-tailed stationary reference law | measured platykurtic at every `rho` | `P13` |
| X4 | Any change to convention A — fixed-`m` denominator, untruncated window, excluded terminal increment | breaks `D5`, and voids T1 and with it every P5 theorem | `D5`, `P15` |
| X5 | Non-Gaussian innovations, contamination, other detectors, other reuse conventions | that is **P8** | `p7/EVIDENCE_BOUNDARY.md`, `p5/LIMITATIONS.md` §1 |
| X6 | Any first-order/linear-response transfer from `d E[e_1]` to `d E[M(e_1)]` | candidate P7-E was **rejected in independent adjudication** | `S18` |
| X7 | "Larger `m` is universally better" | `P9` (provisional, `m<=5`) points one way; `S14` (closed) says reuse-attributable ARL loss *grows* with `m` | `X8` below |
| X8 | Treating `S14` and `P9` as consistent without stating the resolution | they are measured against **different controls**: `S14` is vs the same-`m` fresh baseline (a ratio), `P9` is in absolute RMS/ARL. A P6 document that quotes one without the other is misleading | `S14`, `P9` |
| X9 | Any P5 numeric (`rho* = 0.20`, `Gamma_eff = 1.48..2.19`, `e*(1) = 1.04`, the bimodality onset) as a design constant, tuning default or gate threshold | `CLOSED_CANDIDATE`, and grid-resolution limited | all of §5 |
| X10 | Novelty of any kind | not adjudicated anywhere in ReBaseGuard, and P4's own novelty audit is open | `G4`, `NOVELTY_AUDIT_PLAN.md` |
| X11 | Latent `e_j` inside any policy claimed to be implementable | it is not observable; using it silently is the single most likely way P6 produces a false result | `OBSERVABILITY_AUDIT.md`, `FAILURE_MODE_REGISTER.md` F1 |
| X12 | "Fresh-only is the safe fallback" | fresh-only already loses `65%..83%` of the nominal ARL (`S4`), and `m=1` is unusable at any `rho` (`S14`) | `S4`, `S14` |

## 9. Ledger invariants

1. Every quantitative claim in every other P6 pre-design document cites a row id
   from this ledger (`S9`, `P7`, `E1`, …) or is marked `DESIGN_HYPOTHESIS`.
2. No document may promote a row's tier. Promotion happens **only** by editing
   this file, and only in response to an adjudication verdict.
3. `PROVISIONAL_P5` rows are inert until Codex reports. On that day,
   `P5_ADJUDICATION_CONTINGENCIES.md` §5 is executed and §5 of this ledger is
   rewritten with the surviving tiers before any P6 experiment runs.
