# P5X feasibility audit

```text
AUDIT_DATE   = 2026-09-02
AUDIT_HEAD   = eea2bfb43803e853a1bc84d10410fd9f3984d849 (main == origin/main)
PHASE        = mathematical feasibility only; no production campaign was run
VERDICT      = P5X_THEOREM_PATH_FOUND
```

Everything numerical in this document comes from
`feasibility/results/reduction_probe.json`, which is ordinary double-precision
arithmetic and is **not** evidence for any scientific claim. It is evidence
about *proof feasibility* only.

---

## 1. Repository forensics

| item | finding |
|---|---|
| worktree at entry | two untracked audit namespaces present: `p4_final_disposition_audit/`, `p5_final_disposition_audit/`; nothing else |
| `HEAD` | `eea2bfb` "P9R Checkpoint B" |
| commits touching `p5_nonlinear_dynamics/` | exactly one, `bb03c0e`; tree byte-identical at `HEAD` |
| authoritative P5 verdict | `p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md`: `FINAL_P5_VERDICT = PARTIAL`, `STRONGEST_SURVIVING_THEOREM = T7, WITH SCOPING CORRECTIONS` |
| authoritative disposition | `p5_final_disposition_audit/P5_FINAL_DISPOSITION_AUDIT.md`: `P5_PARTIAL_SHOULD_BE_FINAL`, `P5R_LAUNCHED = NO`, `NEW_SCIENCE_REQUIRED = YES for literal G3/G7/G9` |
| existing certified numerics | `closure/04_ARB_CERTIFICATE.md` (`Gamma_CUSUM in [3.9243482…, 27.8493821…]`), `closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md` (`Gamma_SR in [5.8003917…, 28.7812858…]`) — both at `e = 0`, `m = 1` |
| existing certified numerics for `m > 1` / SR-Gaussian | **none**: `m_gt_1_priority1/THEOREM.md` §5 and `m_rho_stability_priority3/EVIDENCE_BOUNDARY.md` state that the `m > 1` and SR-Gaussian `GammaTilde` values are Monte Carlo, with the Arb work covering finite-support witnesses only |
| Level 1–3 open register | `closure/02_THEOREM_MAP.md` §E: `O-06 Global nonlinear bifurcation theorem = NOT CLAIMED`; `O-02 Cov_0(Z_{tau-r}, T_tau) > 0 = OPEN` |
| Lean toolchain | `rebaseguard-lean/` on mathlib `v4.34.0-rc1`; P5's spine is `lean/NonlinearSkeletonP5.lean`, 12 declarations, sorry-free, abstract skeleton algebra only |

The two untracked audit namespaces predate this campaign, are outside the P5X
namespace and are **not** modified, committed or relied upon as git objects by
P5X. `FROZEN_GATES.md` gate `G11` records them explicitly rather than letting
them make a protected-tree conjunct silently false — the exact failure mode that
cost P5 its gate `G20`.

## 2. Exact reconstruction of the frozen dynamics

Sources: `p5_nonlinear_dynamics/DEFINITION_AUDIT.md`, `PROOF.md`,
`src/rebaseguard_p5/kernel.py`, `p7_statistical_consequences/src/rebaseguard_p7/detectors.py`,
`level4/src/rebaseguard_level4/frozen.py`.

**Objects, kept apart deliberately.**

| object | definition |
|---|---|
| observations | `raw_1, raw_2, … ~ iid N(0,1)`; law does **not** depend on `e` |
| innovation seen by the detector | `z_t = raw_t - e` , so `z ~ iid N(-e, 1)` |
| detector `D` | CUSUM: `S+ = max(0, S+ + z - k)`, `S- = max(0, S- - z - k)`, `k = 1/2`, alarm iff `max(S+,S-) >= h = 5`, inclusive, tested after the update, plus-arm priority on ties. SR: `y+ = logaddexp(0, y+ + z - 1/2)`, `y- = logaddexp(0, y- - z - 1/2)`, alarm iff `max(y+ + z - 1/2, y- - z - 1/2) >= log A`, `A = 520.886133602749` |
| stopping time | `tau = inf{t >= 1 : alarm after the update at t}`; no minimum dwell (convention A) |
| window | `w = min(m, tau)`, `m in {1,2,3,5}` |
| selected average | `Rbar = (1/w) sum_{r<w} raw_{tau-r}` (terminal alarm-causing observation included) |
| reference update | `e_{j+1} = rho (e_j + zbar_j) + (1-rho) fresh_j`, `fresh ~ N(0, 1/m)` independent |
| convention A | denominator `= w`, i.e. equals the number of summands; `P5-T1` fails without it |
| symmetry | `raw -> -raw` with `e -> -e` swaps the two arms and leaves `tau, w` invariant |

**Stochastic recursion** (`P5-T1`, exact): `e_{j+1} = rho Rbar_j + (1-rho) fresh_j`.
The entering error acts on the future **only** by selecting which observations
enter the terminal window; it never enters additively.

**Conditional mean map** (`P5-T2`, exact): `M_{D,m,rho}(e) = rho R_{D,m}(e)`,
`R_{D,m}(e) = E[Rbar | e]`; `V = rho^2 S(e) + (1-rho)^2/m`, `S = Var(Rbar | e)`.

**Deterministic skeleton**: `f_rho = rho R`. It is a one-parameter *scaling*
family of one fixed odd function.

**Local linearisation**: `R'(0) = 1 - GammaTilde_{D,m}`, so
`lambda(rho) = rho (1 - GammaTilde)` — the P3 multiplier.

**Stationary kernel**: `P(x, ·) = law of rho Rbar(x) + (1-rho) fresh`; `P5-T7`
gives a unique invariant `pi` with all moments, per fixed `(D, m, rho)`.

These four are **not** the same object and P5X never substitutes one for
another. In particular the skeleton is *not* an approximation of the chain: P5
measured a branch-to-noise ratio `<= 1.5` over the whole admissible `rho`
range, so the deterministic branch is buried inside the chain's own one-step
noise. Any theorem that routes the mechanism through the skeleton is therefore
a theorem about the skeleton, not about the chain. `FROZEN_THEOREM.md` keeps
that separation load-bearing.

## 3. What is already proved, and what the global gap actually is

| statement | status entering P5X |
|---|---|
| `P5-T1` raw-mean identity | EXACT (convention A) |
| `P5-T2/T3` factorisation and symmetry | EXACT |
| `P5-T4` `sup_e E[tau|e] <= C_D` | EXACT, constants `9.9e8` / `1.4e11` (vacuous as rates) |
| `P5-T5` `sup_e E[Rbar^{2p}|e] <= (2p-1)!! C_D` | EXACT, same vacuous constants |
| `P5-T7` unique invariant law, uniform ergodicity, all moments | EXACT per fixed `(D,m,rho)`; qualitative constants |
| `P5-T11` `ACF1 = rho(1 - Gamma_eff)` | EXACT given `pi` |
| `P5-T8/T9/T10` skeleton results | CONDITIONAL on `H1`–`H3b` |
| `H2`, `H3a`, `H3b` | **NOT ESTABLISHED**; measured on finite grids |
| attraction of the branch, exclusion of asymmetric cycles, flip classification | **NOT ESTABLISHED** (numerical evidence) |
| `Gamma_{CUSUM}`, `Gamma_{SR}` at `e = 0`, `m = 1` | CERTIFIED (wide: widths `23.9` and `23.0`) |
| `GammaTilde_m` for `m > 1`, and Gaussian SR for `m > 1` | Monte Carlo only |

**The global gap, stated exactly.** Everything P5 proved about boundedness is
*qualitative*: `P5-T5` gives a state-independent one-step second-moment bound
`sup_e E[e_{j+1}^2 | e] <= rho^2 C_D + (1-rho)^2/m` with `C_D >= 9.9e8`. That is
already stronger in form than any Foster–Lyapunov drift condition — P5 says so
in `T12` — but it is numerically empty: it bounds the stationary RMS by `3.1e4`
where the measured value is `1.37`. Symmetrically, every statement about the
*shape* of `R` (sign, monotonicity, saturation level, far-field decay) is
measured, not proved.

So the missing global mechanism is **not** "find a drift function". It is:

> obtain non-vacuous, rigorous, global control of the stopped-selection map
> `R_{D,m}` and its second moment `S_{D,m}` — sign, saturation level and
> far-field decay — and then read the mechanism off them.

## 4. Local-to-global: what P3 proves and what it does not

`lambda(rho) = rho (1 - GammaTilde_{D,m})` is a statement about the derivative
of the conditional-mean map at a single point. It establishes:

* `e = 0` is a fixed point of the conditional-mean map (by symmetry);
* for `rho > rho_c = 1/|1 - GammaTilde|` the linearisation at `0` is repelling.

It establishes **nothing** about: behaviour outside the linearisation radius
(P7's grid-defined `r_lin ~ 0.05`); boundedness; the existence, shape or
dispersion of the stationary law; any orbit of the skeleton away from `0`; or
any statement uniform in `e`. In particular "locally repelling" is compatible
with every one of: divergence, a bounded attractor, a 2-cycle, chaos, and a
featureless unimodal stationary law. P5 already excluded divergence (`T5`/`T7`)
and multiple invariant laws (`T7`), qualitatively.

**Additional ingredients genuinely required.** Only three, and they are all the
same object:

1. a rigorous non-vacuous bound `sup_e |R_{D,m}(e)| <= R_max < 2`;
2. a rigorous positive lower bound `inf_e S_{D,m}(e) >= s_min > 0`;
3. a rigorous upper bound `sup_e E[Rbar^2 | e] <= M_2 < infinity` with a
   realistic constant.

Given these, the whole chain closes by elementary algebra on `P5-T2` and
`P5-T7` (§7 below). Nothing else is needed for the mechanism.

**Techniques that genuinely fit the frozen kernel** (and, equally important,
those that do not):

| tool | fits? | why |
|---|---|---|
| second-kind Fredholm / Bellman state reduction on the pre-alarm detector state | **yes** | the state `(S+,S-)` is Markov on a compact square, the innovation is scalar, and the repository already certifies this architecture for `Gamma` |
| rigorous interval (Arb) enclosure on a finite cover | **yes** | all target quantities are analytic in the drift parameter `-e` |
| far-field first-step conditioning | **yes** | one innovation forces an alarm for `|e|` large; on `{tau = 1}`, `w = 1` for every `m`, so all windows collapse |
| Doeblin / minorisation / uniform ergodicity | **already used** by `P5-T7`; P5X must not restate it |
| Foster–Lyapunov drift, petite sets, contraction outside a compact set, Harris recurrence | **not needed** and would be weaker: `P5-T5` already gives a *state-independent* one-step moment bound. Naming them would be technique theatre |
| monotone drift / odd-even symmetry | partially: symmetry is `P5-T3` and is used; monotone drift is **false in the far field** — `\|R\|` has a reproducible secondary lobe near `\|e\| ~ 5.5` (CUSUM) and `~ 6.5–7` (SR) |
| random dynamical systems, stochastic bifurcation theory | **does not fit**: the branch amplitude is dominated by the one-step noise floor at every admissible `rho`, so no small-noise expansion is legitimate here |
| Cauchy–Schwarz through `P5-T5` | **dead**, see `FAILURE_ANALYSIS.md` §1 |

## 5. The reduction that makes the campaign feasible (new)

Stated exactly as `P5X-T1` in `FROZEN_THEOREM.md` §2. In outline: write
`x = (x+, x-)` for the pre-alarm detector state on the compact square
`E_D = [0, b_D)^2` (`b_CUSUM = h = 5`, `b_SR = log A`), `c_D = h + k = 11/2`
resp. `log A + 1/2` for the one-step alarm margin, and `(l(x), u(x)) =
(x- - c_D, c_D - x+)` for the continuation interval of the next innovation.
With `phi` the standard normal density and innovations `N(-e,1)`,

```text
(K_e f)(x)     = int_l^u f(q(x,z)) phi(z+e) dz
(K_{z,e} f)(x) = int_l^u z f(q(x,z)) phi(z+e) dz
rho_{1,e}(x)   = phi(u+e) - phi(l+e) - e (1 - Phi(u+e) + Phi(l+e))
h_1 = 1 - K_e 1 ,  h_j = K_e h_{j-1}          (h_j(x) = P_x(tau = j))
S_0 = rho_{1,e} ,  S_j = K_{z,e} h_j
g_r = (I - K_e)^{-1} S_r
```

then, at the reset state `x0 = (0,0)`, for every `m >= 1`,

```text
R_{D,m}(e) = e + (1/m) sum_{r<m} [ g_r(x0) - sum_{t=r+1}^{m-1} (K_e^{t-r-1} S_r')(x0) ]
                 + sum_{t=1}^{m-1} (1/t) sum_{i=1}^{t} (K_e^{i-1} S_{t-i})(x0)
```

with the short-`tau` corrections written out in `FROZEN_THEOREM.md`. The point
is structural, not cosmetic:

* the state space is **two-dimensional for every `m`** — the last `m-1`
  innovations never enter the state, because linearity moves them into
  `m - 1` extra *backward functions* `h_j` on the same square;
* `e` enters only through the Gaussian weight `phi(z + e)`, which is entire in
  `e`, so all targets are real-analytic in `e` and an interval-valued `e` is a
  legitimate input to the same machinery — no separate modulus of continuity is
  needed to go from grid points to a continuum;
* the operators `K_e`, `K_{z,e}` and the closed-form absorbing rewards are, at
  `e = 0`, literally the operators of the existing `Gamma` certificate
  (`closure/04_ARB_CERTIFICATE.md` §3), so the certified architecture —
  exact-dyadic Chebyshev candidate, degree-100 `phi` with Lagrange remainder,
  Bernstein continuum range bound on the reachable set, monotone Bellman
  resolvent bound, outward-rounded propagation — transfers with no new idea;
* `S_{D,m}` needs only second-moment rewards and `O(m^2)` further backward
  functions on the same square.

**Probe result.** `feasibility/run_probe.py` implements this in double
precision on a bilinear collocation grid and compares against P5's independent
Monte Carlo map, which was produced by a completely different method
(`4e5`–`3.2e6` simulated cycles per grid point, 8 batches, two seed families):

| check | result |
|---|---|
| cells compared | 2 detectors × 4 windows × 10 values of `e` in `[0.005, 5]` |
| worst standardised gap vs P5 Monte Carlo | `4.28` batch SE (at `e = 0.3`, CUSUM, `m = 1`), where the grid-refinement delta is itself `2.4e-3` |
| grid convergence `n = 61 -> 121` | `<= 2.4e-3` everywhere, `<= 3e-5` for `|e| >= 1.5` |
| `S_{D,1}(e)` vs P5 Monte Carlo | agrees to `<= 0.013` absolute across `e in {0, 0.1, 0.3, 0.5, 1, 2.2, 4}` |
| secondary lobe | reproduced at `\|R\| = 0.399` at `e = 5.5` (CUSUM) and `0.387` at `e = 7.0` (SR); P5 measured `0.399` and `0.388` |
| `sup \|R\|` on the scan | CUSUM `1.576` (`m=1`, `e = 0.25`); SR `1.591` (`m=1`, `e = 0.25`) |
| `inf S` on the scan (`m = 1`) | CUSUM `0.4796`, SR `0.4755`, both at `e = 0.5` |
| sign | `R < 0` at every scanned `e > 0`, all windows, both detectors |

The residual `4.28` SE is a *discretisation* discrepancy of the probe, not a
defect of the reduction: it shrinks under grid refinement in the same
direction. A certified implementation replaces the collocation error by an
outward-rounded enclosure, so this is exactly the error term the Arb layer
removes.

## 6. Global boundedness, attacked first (brief §5)

The brief asks for `sign(e) E[e_{j+1} - e_j | e_j = e] < -eps` outside a
compact set. Under `P5-T2` this is an identity, not a research question:

```text
sign(e) ( E[e_{j+1} | e] - e ) = sign(e) rho R(e) - |e| <= rho R_max - |e| ,
```

so the drift inequality holds with any `eps > 0` for `|e| > rho R_max + eps`,
**as soon as `R_max = sup_e |R|` is finite**. With P5's own constants it is
already true (`R_max <= sqrt(C_D) = 3.1e4`) and already useless. The entire
content of "global boundedness" is therefore the *value* of `R_max`, and a
quadratic Lyapunov statement is likewise an identity plus a constant:

```text
E[e_{j+1}^2 | e] = rho^2 E[Rbar^2 | e] + (1-rho)^2/m <= rho^2 M_2 + (1-rho)^2/m .
```

This is the honest reason a Foster–Lyapunov programme would be the wrong
campaign: there is nothing to construct, only something to *measure rigorously*.
P5X therefore attacks `R_max`, `M_2` and `s_min` directly and derives every
drift statement from them. `FAILURE_ANALYSIS.md` §2 records why the drift is
not "restoring" in the usual sense at all.

## 7. Using `P5-T7` without restating it (brief §6)

`P5-T7` is imported unchanged, per fixed `(D, m, rho)`, as: `pi` exists, is
unique, is symmetric, and has finite moments of every order. P5X adds nothing
to that list. What P5X adds is the *quantitative* layer `P5-T7` could not
supply, by combining invariance with the new certified constants:

```text
E_pi[e^2] = rho^2 E_pi[ R(e)^2 + S(e) ] + (1-rho)^2/m
```

(exact, from `P5-T2` and invariance), hence the two-sided bound

```text
rho^2 s_min + (1-rho)^2/m  <=  E_pi[e^2]  <=  rho^2 M_2 + (1-rho)^2/m .
```

With the probe's values (`s_min ~ 0.476`, `M_2 ~ 4.05`, `m = 1`, `rho = 1`)
this reads `0.476 <= E_pi[e^2] <= 4.05`, against P5's measured `1.880`. Both
ends are non-vacuous, the lower end is within a factor `4` and the upper end
within a factor `2.2`. Crucially the **lower** end is what carries the science:
`RMS_pi >= 0.69` against P7's linearisation radius `r_lin ~ 0.05`, i.e. the
stationary law provably lives more than an order of magnitude outside the
regime where `lambda(rho)` describes anything. That is the local-to-global
bridge, and it needs no hypothesis about the branch.

Uniqueness, geometric ergodicity and finite moments are `P5-T7` and are cited
as such. Quantitative concentration, stationary dispersion bounds and the
high-dispersion lower bound are new and belong to P5X.

## 8. `H2` / `H3a` / `H3b` reconstruction and classification (brief §8)

Exact original statements are `p5_nonlinear_dynamics/THEOREM.md` "Measured
hypotheses"; the audit table is `NONLINEAR_MAP.md` §4.

| id | exact claim | empirical evidence | necessary? | sufficient? | weakenable? | proof path | **classification** |
|---|---|---|---|---|---|---|---|
| `H1` | `R` continuous and odd | it is `P5-T3`, exact | — | — | — | already proved | `PROVABLE_CANDIDATE` (already a theorem; not P5X work) |
| `H2` | `R(e) < 0` for all `e > 0` | holds in 8/8 cells on the measured grid; probe: `R < 0` at every scanned `e in [0.05, 12]`, both detectors, all `m` | **not necessary globally**: `T8`/`T9` only ever use `e in (0, E]`, `E = 2`, because `sup|R| < E` kills `e > E` | sufficient for `T8` together with `H1` | yes — needed only on `(0, 2]` | certified enclosure of `R` on a finite cover of `[e_0, 2]` plus certified `R' < 0` on `[0, e_0]` (which gives `R < R(0) = 0`, and `R(0) = 0` is exact by `P5-T3`) | `PROVABLE_CANDIDATE` |
| `H3a` | `s(e) = -R(e)/e` continuous and strictly decreasing on `(0,2]`, `s(0+) = GammaTilde - 1`, `s(2) < 1` | holds in 8/8; one nominal violation at `z = 0.2` | needed for *uniqueness* of the symmetric 2-cycle, not for its existence | sufficient with `H1`,`H2`,`H3b` | yes — strict decrease can be replaced by "each level `1/rho >= 1` is attained exactly once", a weaker certifiable statement | certified enclosure of `R` **and** `R'` on a finite cover of `(0,2]`, then `s'(e) = (R(e) - e R'(e))/e^2 < 0` cellwise; near `0` use the `s(0+)` limit and a certified second-order remainder | `PROVABLE_CANDIDATE` (higher cost: needs the derivative system) |
| `H3b` | `sup_e \|R(e)\| < 2` | `1.563`–`0.908` measured; probe `1.576`/`1.591` at `e = 0.25` | **necessary** for every skeleton statement and for the trapping region | sufficient with `H1`,`H2`,`H3a` | the constant `2` may be replaced by any certified `E` with `s(E) < 1`; the *global* quantifier may not be dropped | certified enclosure on a finite cover of `[0, e_far]` plus the exact far-field lemma `P5X-T3` for `\|e\| >= e_far` | `PROVABLE_CANDIDATE` — this is gate `G3` |
| `H3` "globally" | — | **false**: `s` rises between `e = 4` and `e = 5` (secondary lobe) | — | — | — | — | `TOO_STRONG` (P5 already restricted it; P5X keeps the restriction) |

No hypothesis is classified `FALSE`, `EMPIRICAL_ONLY` or
`IRRELEVANT_TO_FINAL_CLOSURE`. `H2` and `H3a` are `CONDITIONAL_ONLY` today and
`PROVABLE_CANDIDATE` under the P5X plan; `H3b` is the load-bearing one.

## 9. Detector-specific vs general (brief §9)

The reduction `P5X-T1` is **detector-generic**: it uses only that the pre-alarm
state is Markov on a compact set, that the innovation is scalar, and that from
each state the alarm event is the complement of an interval. Both frozen
detectors satisfy this with the *same* `(l, u) = (x- - c_D, c_D - x+)` form.

The differences are confined to the certified layer:

| aspect | CUSUM | SR |
|---|---|---|
| state map `q(x,z)` | `max(0, ·)` — piecewise linear, two reset kinks | `logaddexp(0, ·)` — real-analytic, no kinks |
| consequence for certification | panels must be split at the kinks; the reachable set has singular mass on the axes | smoother integrand, but a larger square (`b = 6.2555` vs `5`) and a heavier tail regime |
| existing certified precedent | `closure/04_ARB_CERTIFICATE.md`, 4 Bernstein patches | `sr_derivative/certificate/GAMMA_CERTIFICATE.md`, 1210 cells, 96k innovation intervals |
| far-field lobe | `\|R\|` peaks at `0.399` near `e = 5.5` | `0.387` near `e = 7.0` |
| expected cost ratio | 1× | ~5–8× (measured on the existing `Gamma` certificates) |

So P5X targets **one common theorem with detector-specific certified
constants**, and explicitly permits the outcome "exact CUSUM constants, weaker
SR constants" (`FROZEN_GATES.md` `G5` admits per-detector verdicts). No
theorem is forced across the two detectors.

## 10. `rho` scope (brief §10)

The mechanism theorem (`P5X-T4`…`T6`, `T9`) holds for **every** `rho in [0,1]`
with no scoping, because it uses only `P5-T2`, `P5-T7` and the certified
constants — none of which depend on `rho`. That is a consequence of the
`rho`-factorisation and is not an achievement of P5X.

Only the skeleton dynamics theorem `P5X-T8` needs a scope, and it needs one for
a real mathematical reason: at `rho = rho_c` the 2-cycle multiplier is exactly
`1`, so no interval method can certify hyperbolicity in a neighbourhood of
`rho_c`. `FROZEN_SCOPE.md` freezes `rho in [(1 + eta) rho_c, 1]` with `eta`
fixed **before** production, and requires the campaign to report the smallest
`eta` it achieved rather than tuning `eta` to the result.

## 11. Formal proof strategy (brief §11)

Order is fixed: human theorem (`FROZEN_THEOREM.md`) → proof decomposition and
lemma graph (`PROOF_OBLIGATIONS.md`) → certified inequalities
(`CERTIFICATE_PLAN.md`) → Lean spine (`LEAN_PLAN.md`) → empirical support
(`EMPIRICAL_PLAN.md`). Lean formalises only the logical spine that consumes
certified scalars; it never touches the stochastic monitoring process. See
`LEAN_PLAN.md` §3 for the explicit non-goals.

## 12. Twenty-point feasibility report (brief §20)

1. **Authoritative P5 gap.** `P5 = PARTIAL`; gates `G3`, `G7`, `G9` fail as
   universal statements about the true stopped-selection map; `G4` is a short
   missing lemma; `G20` is procedural and already satisfied at a clean `HEAD`.
   The disposition audit rules this final and assigns the missing work to a new
   priority.
2. **Exact global-theory gap.** Non-vacuous, rigorous, global control of
   `R_{D,m}` and `S_{D,m}` — sign on `(0,2]`, saturation level `sup|R|`,
   positive floor `inf S`, finite ceiling `sup E[Rbar^2]`, far-field decay.
   Everything else follows algebraically.
3. **Strongest theorem candidate.** `P5X-T9`, the mechanism synthesis: for the
   frozen core, local repulsion at `0` for `rho > rho_c` coexists with a unique
   stationary law whose second moment is bounded **and bounded below** by
   certified constants, with `RMS_pi` more than an order of magnitude outside
   the linearisation radius; the boundedness mechanism is certified saturation
   and far-field forgetting of the stopped-selection map, not restoring drift.
4. **Local-to-global bridge.** `P5-T2` (`M = rho R`) plus a certified `R_max`
   turns the P3 multiplier into a statement about a *bounded* map; the
   certified `s_min` then forces the stationary law off the linearisation
   scale. Two certified scalars, no new probability.
5. **Lyapunov / drift feasibility.** Feasible but *trivial once the constants
   exist*, and not the interesting content — `P5-T5` already dominates any
   drift condition in form. P5X states the drift corollary and says so.
6. **Selection-map shape feasibility.** Feasible on a finite certified cover:
   `R` and `R'` are real-analytic in `e`, computable from 2-D Fredholm objects,
   and the far field is handled by an exact first-step lemma. Demonstrated in
   floating point across `|e| in [0.005, 12]` for both detectors and all four
   windows.
7. **`H2` status.** `PROVABLE_CANDIDATE`, needed only on `(0, 2]`.
8. **`H3` (`H3a`) status.** `PROVABLE_CANDIDATE` at higher cost (requires the
   derivative system); weakenable to a level-crossing-multiplicity statement.
   Globally: `TOO_STRONG`, and P5 already said so.
9. **`H3b` status.** `PROVABLE_CANDIDATE` and load-bearing; margin
   `2 - 1.591 = 0.409` at the worst cell, so the required enclosure half-width
   is `< 0.2`, against `~0.011` achieved by the existing `Gamma` `a`-equation
   propagation.
10. **CUSUM feasibility.** High. Existing certified precedent at `e = 0`,
    `m = 1`; the reduction adds `m` and `e` at no dimensional cost.
11. **SR feasibility.** Good but heavier: smoother integrand, larger square,
    ~5–8× the certified cost, and a wider existing enclosure. Permitted to end
    weaker than CUSUM.
12. **Required analytical lemmas.** `L1` reduction (`P5X-T1`); `L2` second-moment
    reduction; `L3` far-field forgetting with explicit constants; `L4` uniform
    resolvent bound `‖(I-K_e)^{-1}‖ <= sup_x E_x[tau]` and its monotone
    minorant in `|e|`; `L5` analyticity of the targets in `e`; `L6` stationary
    identity `E_pi[e^2] = rho^2 E_pi[R^2+S] + (1-rho)^2/m`; `L7`
    anti-concentration from a certified fourth moment. See `PROOF_OBLIGATIONS.md`.
13. **Required certified inequalities.** `sup_e |R_{D,m}| <= R_max < 2`;
    `R < 0` on a cover of `(0,2]` (via `R'` near `0`); `inf_e S_{D,m} >= s_min > 0`;
    `sup_e E[Rbar^2|e] <= M_2`; per-`e`-interval resolvent bounds; for the
    optional skeleton theorem, `R'` enclosures and a cover of `rho`.
14. **Lean formalisation plan.** Spine only: certified-scalars → drift →
    trapping region; certified `s_min`,`M_2` → two-sided stationary moment
    bound; certified `R_max` + `s_min` → dispersion exceeds a named radius;
    plus the level-crossing algebra for the optional skeleton statement. No
    measure-theoretic monitoring process. See `LEAN_PLAN.md`.
15. **Empirical support plan.** Correspondence only: independent Monte Carlo
    reproduction of `R`, `S`, and stationary `E_pi[e^2]`, checked to lie inside
    the certified intervals; non-vacuousness demonstration; finite-sample
    behaviour. Never a substitute for a bound. See `EMPIRICAL_PLAN.md`.
16. **Estimated computational burden.** Dominated by certified solves:
    `~120` `e`-intervals covering `[0, 12]` × 2 detectors × (`1` map + `4`
    backward functions + `1` second moment) ≈ `1.4e3` certified solves for the
    core, plus `~2e3` more if the derivative system and the `rho`-cover for the
    skeleton theorem are attempted. At the observed cost of the existing
    `Gamma` certificates this is `O(300–800)` CPU-hours, embarrassingly
    parallel over `e`-intervals.
17. **Estimated mathematical burden.** Core (`L1`–`L6`, `P5X-T1`…`T6`,`T9`):
    moderate — a few pages of standard stopped-process algebra, all of it
    checkable. Optional skeleton theorem (`P5X-T7`,`T8`): substantially harder —
    needs the derivative system, a flip nondegeneracy coefficient, and rigorous
    global interval dynamics with a `rho`-cover.
18. **Closure probability estimate.** Levels A/B (`P5X-T4`–`T6`): `0.90`.
    Level C (`P5X-T7`, i.e. `H2`/`H3a`/`H3b` as theorems): `0.75`.
    Level D (`P5X-T8`, skeleton global dynamics on a scoped `rho`): `0.45`.
    Mechanism closure as defined in `FROZEN_GATES.md` `G13`: `0.70`.
    Full literal replacement of P5's `G7`/`G9`: `0.35` — and P5X does not
    promise it.
19. **Feasibility verdict.** `P5X_THEOREM_PATH_FOUND`.
20. **Exact next action.** Commit and push this namespace as Checkpoint A
    (`TEMPORAL_ANCHOR.md`), then execute `CODEX_HANDOFF.md` §3 step 1: the
    human proof of `P5X-T1`, `P5X-T2` and `P5X-T3` with explicit constants,
    before any certified solve is written.
