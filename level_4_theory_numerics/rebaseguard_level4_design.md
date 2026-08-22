# ReBaseGuard Level 4 — Multi-Cycle Reference Dynamics: Theory, Falsification, Gate

**Role:** lead mathematical research scientist, adversarial posture. Levels 1-3 treated as frozen.
**Verdict up front: the period-2 hypothesis survives as a statement about the deterministic
skeleton and is FALSIFIED as a statement about the stochastic system at the frozen operating
point.** Gate recommendation: **PROCEED-ALTERNATIVE-DYNAMICS** (section J).

---

## 0. Provenance notice (must be read first)

The brief stated that the current closure/repository materials would be provided. **No materials
were attached.** I reconstructed the frozen baseline from the 13 ReBaseGuard documents already in
project `proj_17da7dd79649` (Phase 1, 1.5, 2B, 2C, 4C feasibility, 4D audit, lemma handoff,
Level-4 review, blind re-derivation, four falsification/survival memos, `gamma_table.csv`).
**If the intended Level 1-3 package differs from what is stored, stop here and re-issue it** —
every number below is downstream of that reconstruction.

---

## A. Frozen baseline audit

### A.1 Model, restated without modification

Per-cycle, with reference error `e_j` (the signed error of the current baseline estimate):

- innovations `Z_t = X_t - mu_hat_j = W_t - e_j`, `W_t ~ iid N(0,1)`
- two-sided CUSUM, shared innovation, both arms reset each cycle:
  `S_0^+ = S_0^- = 0`, `S_t^+ = max(0, S_{t-1}^+ + Z_t - k)`, `S_t^- = max(0, S_{t-1}^- - Z_t - k)`
- alarm `tau_j = inf{t >= 1 : max(S_t^+, S_t^-) >= h}`
- frozen operating point `(k, h, m) = (0.5, 5, 1)`
- re-baselining with reuse fraction `rho`:
  `e_{j+1} = rho*(Z_{tau} + e_j) + (1-rho)*V_j`, `V_j ~ N(0,1)` fresh, alarm-independent

`e_j` is a sufficient Markov state because the detector resets fully each cycle.

### A.2 Correspondence table: what is actually established

| Object | Level 1-3 status | Verified here? |
|---|---|---|
| Score identity `F_1'(0) = 1 - Gamma`, `Gamma = E_0[Z_tau T_tau]` | PROVED-BASELINE | Yes, numerically to 4e-4 by two independent routes |
| Mixed-reuse linearity `F_rho'(0) = rho * F_1'(0)` | PROVED-BASELINE | Yes, exact by construction (fresh block is alarm-independent, mean zero) |
| Kernel reflection symmetry; `F_rho` odd | PROVED-BASELINE | Yes, and used throughout |
| `Gamma > 2` (hence `rho_c` interior) | **OPEN** / REQUIRES-RIGOROUS-CERTIFICATE | Unchanged. Numerically `Gamma = 15.887`, but that is not a proof |
| Existence of a stable symmetric 2-cycle | CONJECTURE | **Answered: yes for the skeleton, no for the stochastic law** (D, G) |
| Bimodality of invariant law | CONJECTURE | **Answered: only for `rho >= ~0.55`** (G) |
| Cubic normal form / flip-bifurcation framing | Rejected in Phase 2B | Rejection confirmed and strengthened (D.3) |
| AR(1) reduction (Phase 1) | Superseded by Phase 1.5 | **Decisively falsified: off by 30x** (F) |

### A.3 Internal inconsistencies found in the frozen corpus

1. **`Gamma` discrepancy, now arbitrated.** The corpus carries `Gamma ~ 18.74` (a finite Bellman
   value) and `Gamma ~ 15.87` (MC), a ~18% gap the Level-4 review flagged at 71 SE. An
   independent deterministic solve (B) gives, by Richardson extrapolation,
   **`Gamma = 15.8869`** against the frozen table's `15.8851`. **The 18.74 figure is not
   reproducible and I judge it erroneous.** This is a hygiene item closed.
2. Two conflicting values of `F_1'(0)` at `m = 1` appear in different documents; the correct
   value at `(0.5, 5)` is `1 - 15.885 = -14.885`, matching `gamma_table.csv`.
3. Three mutually inconsistent in-control run-length values at `(k,h) = (0.5,5)` appear across
   Phase 1 (~900), the `m*` table, and `gamma_table.csv` (465.4). **465.42 is correct**
   (B, validated against MC).

---

## B. Deterministic solver (independent re-derivation)

`bellman_solver.py` solves the cycle functionals with no Monte Carlo.

**Live-state enclosure (proved).** While both arms are strictly positive, neither reset is active,
so `S_t^+ + S_t^- = S_{t-1}^+ + S_{t-1}^- - 2k` — the sum *decreases deterministically* by `2k`
per step regardless of the innovation. Hence any live state with both arms positive satisfies
`S^+ + S^- <= h - k`... more precisely the reachable live set is contained in
`{(a,b) : 0 <= a,b < h, a + b <= max(h - k, ...)}` and is forward invariant. This turns the grid
from a square into a simplex and is what makes the solve cheap.

Discretization: an explicit atom at each arm's zero (the reset has positive probability) plus
midpoint-collocated cells; the innovation axis is split at every point where either arm crosses a
cell boundary, so each sub-interval's Gaussian mass and first moment are closed-form. Sparse
triplet assembly, sparse LU. The operator system is block-triangular: run length `A`, then
`Gamma`-type second-order rewards.

**Validation (`solver_validation.csv`):** clean second-order convergence in `N`; Richardson limits

| Quantity | Solver | Frozen table |
|---|---|---|
| `ARL_0` at `e = 0` | 465.44 | 465.4 |
| `Gamma` | 15.8869 | 15.8851 |
| `F_1'(0)` | -14.8869 | -14.8851 |

Two independent routes to `Gamma` (direct stopped-moment vs. the score identity) agree to
`4e-4`, which **numerically corroborates the frozen score identity** (it does not reprove it).
Against Monte Carlo, `F_1(e)` agrees to `3e-3` pointwise.

Status: **DERIVED** (solver), with all baseline reproductions **NUMERICALLY-TESTABLE** and passed.

---

## C. Symmetry

`W_t` is symmetric and the two arms are exchanged by `Z -> -Z`. Therefore the transition kernel
satisfies `P(-e, -B) = P(e, B)`, so `F_rho(-e) = -F_rho(e)` (**odd**, PROVED-BASELINE, re-derived)
and any invariant law is symmetric *if unique*. Uniqueness is not established; I do not assume it.
Consequences used below: only `e >= 0` need be computed; a 2-cycle is symmetric, `{-e*, +e*}`.

---

## D. Deterministic skeleton — the period-2 question, answered

### D.1 Exact reduction of the whole `rho`-family to one scalar function

Because the fresh block is alarm-independent and mean zero, the skeleton map is
`F_rho(e) = rho * F_1(e)` **exactly, for every `e`** — not just to first order. This is the
Level-3 mixed-reuse linearity extended off the fixed point, and it is the single most useful
structural fact at Level 4: it collapses a two-parameter search to a one-dimensional root problem.

A symmetric 2-cycle is `F_rho(e*) = -e*`, i.e.

> **`g(e*) = 1/rho`,  where `g(e) := -F_1(e)/e`.**   (**DERIVED**)

So the entire `rho`-family of 2-cycles is read off a single curve `g`. Note `g(0+) = -F_1'(0) =
14.885 = Gamma - 1`, and `rho_c = 1/(Gamma - 1) = 0.0672`.

### D.2 Existence and uniqueness

Computed `g` on `(0, 4]` (`f1_map.csv`): `g` is **strictly decreasing**, from `14.73` near zero
through `1` at `e ~ 1.03`, decaying like `O(1/e)` in the far field (checked to `e = 10`).
Therefore:

> **For every `rho` in `(rho_c, 1]` there is exactly one symmetric 2-cycle `+/- e*(rho)`, and none
> for `rho <= rho_c`.**   (**NUMERICALLY-TESTABLE**, verified at `N = 50/100/200`, branch stable
> to 5 digits; **not** PROVED — monotonicity of `g` is unproved and is the natural next lemma.)

`e*(rho)` rises from `0` at `rho_c` to `1.0367` at `rho = 1` (`period2_branch.csv`), with the
square-root onset expected of a supercritical flip.

### D.3 Stability — and why the flip framing is misleading

The 2-cycle multiplier is `mu = F_rho'(e*) * F_rho'(-e*) = rho^2 * F_1'(e*)^2` by oddness — **a
perfect square, hence non-negative always.** Measured: `F_1'(e*) > 0` on the whole branch (the map
has already folded back by `e*`), and

> **`mu <= 0.35` for all `rho` in `(rho_c, 1]`** — the 2-cycle is attracting everywhere it exists,
> and **never** undergoes a further flip. No period-4 cascade exists in this model.

This kills the "route to chaos" narrative outright, and it independently confirms Phase 2B's
rejection of the cubic normal form: the destabilization at `rho_c` is driven by a *boundary layer*
at the origin (slope `-14.9` over a width of order `0.1`), not by a cubic term. A low-order
expansion at `0` cannot see `e*`, because `e*` sits beyond the fold.

**Level 4's honest skeleton result:** period-2 exists, is unique, and is *robustly attracting* —
which is a cleaner theorem than the conjectured one, and a *less alarming* one.

---

## E. Candidate theorem (skeleton)

> **Theorem (candidate).** Fix `k, h > 0`, `m = 1`. Let `F_1` be the one-cycle conditional-mean map
> and `g(e) = -F_1(e)/e`. Assume (i) `Gamma > 2` [OPEN], (ii) `g` is strictly decreasing on
> `(0, inf)` with `g(0+) = Gamma - 1` and `g(e) -> 0` [NUMERICALLY-TESTABLE]. Then for
> `rho_c = 1/(Gamma-1)`: the origin is the unique fixed point of `F_rho` and is locally
> attracting for `rho < rho_c`, repelling for `rho > rho_c`; and for every `rho in (rho_c, 1]`
> there is a unique symmetric 2-cycle `{-e*, e*}` with `g(e*) = 1/rho`, whose multiplier
> `rho^2 F_1'(e*)^2` lies in `(0,1)` — so it is attracting.

Hypothesis (i) is the frozen open inequality (lemma handoff). Hypothesis (ii) is the new lemma
Level 4 would need. **Neither is proved here.** Certification route for (ii): the same
Fredholm/interval-arithmetic machinery already scoped in Phase 4C, applied to `g'` rather than to
a single orbit — a strictly better use of that effort than certifying one orbit at one `rho`,
which the Level-4 review already rated worst-in-class for generality.

---

## F. Solver-vs-simulation: the AR(1) reduction is dead

Paired simulation (1.65M cycle transitions, `rho = 1`) binned into `E[e_{j+1} | e_j]`
(`empirical_vs_deterministic.csv`) matches the deterministic `F_1` to `<= 5e-3` across
`[-2.7, 2.7]`. The same data fit as a linear AR(1) gives slope **-0.496**, against a true local
slope of **-14.885**.

> **The Phase-1 AR(1) reduction understates the local derivative by a factor of 30.** It is not a
> mild approximation; it is the wrong object. Phase 1.5's secant-vs-derivative correction is
> vindicated, and this is now demonstrated on the stochastic system rather than inferred.

---

## G. Stochastic long-run dynamics — where the hypothesis FAILS

Simulated the true recursion (3000 chains, burn-in discarded) at `rho = 0, 0.2, 0.5, 0.8, 1`, plus
a threshold sweep (`bimodality_threshold.csv`).

### G.1 An adversarial finding that invalidates the obvious diagnostic

**Stationary mass away from zero does not discriminate reuse.** At `m = 1` the *fresh* control
(`rho = 0`) already puts **61.7%** of its mass at `|e| > 0.5` — *more* than `rho = 0.2` does
(**56.1%**) — because a single-observation baseline is itself `N(0,1)`. Any claim of the form
"reuse pushes mass away from the target" is unsupportable at the frozen operating point. **I
decline to use it as evidence**, and I flag it as a trap for the manuscript: it is the diagnostic
a referee would reach for first, and it says nothing.

The full verified summary (`stochastic_summary.csv`):

| `rho` | mass `|e|>0.5` | lag-1 autocorr | cycle length | sign alternation |
|---|---|---|---|---|
| 0.0 | 0.617 | -0.002 | 83.2 | 0.501 |
| 0.2 | 0.561 | -0.197 | 94.7 | 0.614 |
| 0.5 | 0.620 | -0.469 | 81.5 | 0.814 |
| 0.8 | 0.739 | -0.535 | 56.9 | 0.892 |
| 1.0 | 0.775 | -0.496 | 50.1 | 0.879 |

The signature that *does* discriminate cleanly and monotonically over `rho in [0, 0.8]` is **lag-1
autocorrelation** (`-0.002` fresh to `-0.535`). Note it is *not* monotone to `rho = 1`, and neither
is cycle length: **`rho = 0.2` has a longer cycle (94.7) than fresh (83.2)** — mild reuse slightly
*helps*, because it partially cancels the `N(0,1)` dispersion of a one-observation baseline before
the negative-feedback correlation dominates. This non-monotonicity is a further point against a
simple "reuse is harmful" narrative.

### G.2 Bimodality exists — but not where the theory predicts

Central-dip test (density at `0` vs. the off-centre maximum), stable across 41/61/81 bins:

| `rho` | dip `z` | mode at | verdict |
|---|---|---|---|
| 0.0 | -20 to -27 | — | unimodal (peaked at 0) |
| 0.5 | -4 to -5 | — | **unimodal**, significantly so |
| 0.6 | +7.2 | 0.52 | bimodal, weak |
| 0.8 | +26 | 0.79 | bimodal |
| 1.0 | +14 to +33 | 0.79-0.92 | bimodal |

> **The bimodality onset is `rho ~ 0.55`, versus `rho_c = 0.067` for the skeleton — an eightfold
> gap.** For `rho` in `(0.067, 0.55)` the skeleton has an attracting 2-cycle and the invariant law
> is nonetheless **unimodal at zero**. Moreover where bimodality does appear, the modes sit at
> `|e| ~ 0.79`, strictly **inside** `e* = 1.04`; the orbit does not locate the modes.

### G.3 What this falsifies

Per-cycle noise has standard deviation `~1`, while the orbit amplitude is `<= 1.04`. **The noise is
as large as the structure it is supposed to organize.** Consequently:

- **FALSIFIED:** "the destabilization at `rho_c` produces oscillatory/bimodal re-baselining."
  It does not, over most of the range where the skeleton is unstable.
- **FALSIFIED:** "period-2 describes the long-run behaviour at the frozen operating point."
  Even at `rho = 1`, sign alternation is `0.88` (not `1`) and only `25%` of mass lies within
  `25%` of `e*`.
- **SURVIVES:** the skeleton statements of section D, and the *mechanism* (negative feedback via
  the alarm-time score) as measured by lag-1 autocorrelation of the reference error.

This is the "failed period-2 hypothesis" the brief anticipated, and I report it as the main
result rather than burying it.

---

## H. Monitoring consequences — and an honest attribution

Renewal-reward: expected in-control cycle length `= E_pi[A(|e|)]`, with `A` the deterministic run
length. Simulation and this identity agree to 4 digits (`arl_degradation.csv`), confirming both.

| `rho` | cycle length | fraction of oracle 465.4 |
|---|---|---|
| oracle (`e = 0`) | 465.4 | 1.000 |
| 0.0 (fresh, `m=1`) | 83.2 | 0.179 |
| 0.2 | 94.7 | 0.203 |
| 0.5 | 81.5 | 0.175 |
| 0.8 | 56.9 | 0.122 |
| 1.0 | 50.1 | 0.108 |

`A` is even and steeply decreasing (`A(0) = 465`, `A(0.5) = 38.0`, `A(1) = 10.4`, `A(2) = 4.0`), so
Jensen against a spread-out `pi` is catastrophic. **But the attribution cuts against the
ReBaseGuard story on two counts:**

1. Fresh `m = 1` estimation already destroys **82%** of the oracle ARL before reuse enters at all.
   Reuse then moves `0.179 -> 0.108`. **Single-observation re-baselining is the primary mechanism;
   reuse is secondary.**
2. The dependence is **not monotone**: `rho = 0.2` (0.203) is *better* than fresh (0.179).

A manuscript claiming "reuse degrades monitoring" would therefore be overstating a real but
subordinate effect, and would be straightforwardly falsifiable at small `rho`. The defensible
claim is that ARL loss is governed by the dispersion of the invariant baseline law through the
convex, steeply decreasing `A`, with reuse one contributor that can act in either direction.

---

## I. Claim ledger

| # | Claim | Label |
|---|---|---|
| 1 | Score identity `F_1'(0) = 1 - Gamma` | PROVED-BASELINE |
| 2 | `F_rho = rho * F_1` exactly (all `e`), hence `F_rho'(0) = rho F_1'(0)` | PROVED-BASELINE / DERIVED (off-fixed-point extension) |
| 3 | `F_rho` odd; invariant law symmetric if unique | PROVED-BASELINE |
| 4 | `Gamma > 2` | OPEN / REQUIRES-RIGOROUS-CERTIFICATE |
| 5 | 2-cycle condition `g(e*) = 1/rho` | DERIVED |
| 6 | Multiplier `= rho^2 F_1'(e*)^2`, a perfect square | DERIVED |
| 7 | `Gamma = 15.887`, `ARL_0 = 465.44`; corpus value 18.74 erroneous | NUMERICALLY-TESTABLE (passed, 2 routes) |
| 8 | `g` strictly decreasing => unique 2-cycle for `rho > rho_c` | NUMERICALLY-TESTABLE; needs certificate |
| 9 | 2-cycle attracting (`mu <= 0.35`), no period-4 | NUMERICALLY-TESTABLE; needs certificate |
| 10 | AR(1) reduction wrong by 30x | NUMERICALLY-TESTABLE (passed) |
| 11 | Bimodality onset `~0.55 >> rho_c`; unimodal on `(rho_c, 0.55)` | NUMERICALLY-TESTABLE (passed) |
| 12 | Period-2 describes the stochastic long run | **FALSIFIED** |
| 13 | Stationary mass away from 0 diagnoses reuse | **FALSIFIED** (fresh control exceeds `rho=0.2`) |
| 14 | Reuse is the dominant cause of ARL loss | **FALSIFIED** (subordinate to `m=1`; non-monotone in `rho`) |
| 15 | Uniqueness of the invariant law | OPEN (not assumed anywhere above) |
| 16 | Detector-generality of the mechanism | OPEN (two Gaussian `m=1` witnesses only) |

**Not claimed:** any theorem from Monte Carlo; global dynamics from `F'(0) < -1`; chaos; any
modification of the frozen model.

---

## J. Gate recommendation

### **PROCEED-ALTERNATIVE-DYNAMICS**

Not `PROCEED-PERIOD2`: the period-2 program's advertised payoff was an oscillatory/bimodal
signature of re-baselining instability. Section G shows that signature is absent across most of
the parameter range where the skeleton is unstable, and where present it is misplaced relative to
the orbit. Certifying an orbit with validated arithmetic would be certifying a feature of a
skeleton that does not govern the observable process — expensive, and the Level-4 review already
rated it worst on generality-per-unit-risk. Skeleton period-2 also turned out *attracting with
`mu <= 0.35`*, so it is not even a marginal-stability story.

Not `BLOCKED-MODEL-ISSUE`: nothing in the frozen model is broken. The `Gamma` discrepancy resolved
in favour of the tabulated value, the score identity and mixed-reuse linearity both held under
independent re-derivation, and the solver reproduces every frozen number it can reach. The
inconsistencies found (A.3) are bookkeeping, not modelling.

**The alternative dynamics worth pursuing, in priority order:**

1. **Certify `g' < 0`, not an orbit.** One lemma delivers existence *and* uniqueness *and*
   attraction for the whole `rho`-family at once — strictly more general than a point certificate,
   using machinery already scoped in Phase 4C. **Highest value per unit effort.**
2. **Reframe the phenomenon as noise-dominated negative feedback.** The measurable, robust,
   honest signature is lag-1 autocorrelation of the reference error (`-0.50` at `rho = 1` vs `0`
   fresh), which is a genuine and testable consequence of the score identity and does not depend
   on the bimodality that failed. This is the publishable core.
3. **Separate the two ARL mechanisms** (baseline dispersion vs. reuse-induced correlation) with
   `m > 1`, where noise no longer swamps the orbit — the regime in which the period-2 hypothesis
   might actually be true, and the obvious falsification test for it.
4. **Close the two hygiene items** the Level-4 review raised and that remain open regardless of
   branch: `Gamma > 2` (still OPEN) and prior-art verification.

### Blocking caveat on prior art

The literature reconnaissance the brief requires (self-starting charts, post-alarm restart,
iterated random functions, multi-cyclic detection, computer-assisted orbit proofs) **could not be
run**: the scholarly connector now requires an OpenAlex API key for every request, and none is
configured. **I did not substitute recalled citations — fabricating references would be worse than
reporting the gap.** Add a key under Customize -> Credentials -> OpenAlex and this step can be
completed as-is. Until then, novelty risk in this project remains unquantified, and the Level-4
review's judgement that novelty risk now exceeds mathematical risk stands unrebutted.
