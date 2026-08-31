# Independent adjudication of Level-4 Priority 5

```text
FINAL_P5_VERDICT               = PARTIAL
SCIENTIFIC_CORE                = SURVIVES
STRONGEST_SURVIVING_THEOREM    = T7, WITH SCOPING CORRECTIONS
REPOSITORY_CHECKPOINT          = SCIENTIFICALLY LEGITIMATE
NOVELTY                        = NOVELTY-NOT-ADJUDICATED
```

## Decision

P5 is **PARTIAL**.  The exact raw-mean identity survives, and the T7 proof does
establish, for each frozen detector, each fixed `m >= 1`, and each fixed
`rho in [0,1]`, a two-step whole-space minorisation, a unique invariant law,
uniform geometric convergence in total variation, and invariant moments of
every positive order.  The selection-channel mechanism and the main empirical
nonlinear picture also survive.

`CLOSED` is unavailable for two independent reasons.  First, frozen closure
gate G20 is literally false in the adjudication worktree: the pre-existing root
`README.md` modification and the untracked P6 pre-design sit outside P5.  The
focused suite therefore gives `44 passed, 1 failed`, rather than the reported
`45 passed`.  The brief forbids weakening that gate or deleting those unrelated
files.  Second, G3, G7, and G9 use universal language (`sup_e`, `wherever`, and
`anywhere`) while their evidence is finite-grid Monte Carlo/interpolation; they
do not pass as literal universal criteria.

This is not `FAIL`: the frozen semantics, core identity, T7 theorem, local P3
correspondence, T11 identity, and the principal bounded nonlinear mechanism all
survive independent review.

## Repository state and protected material

The authoritative starting point was exactly
`3ae61138dc2353e86788d4c5e44ab3e3286e1a6f`.  At entry, `README.md` was modified
and P5 and P6 pre-design were untracked.  No tracked P1, P2, P3, P4, P7,
Stage A--F, or `level4/src` file differed from that commit.  The supplied
294-file before/after SHA-256 inventories match the live protected tree, and
the protected-tree focused test passes.  P6 pre-design was not modified.

## Strongest surviving theorem: T7

### Exact transition law

Fix detector `D`, `m >= 1`, `rho in [0,1]`, and entering error `x`.  On iid raw
draws `X_t ~ N(0,1)`, the detector observes `Z_t = X_t - x`.  Let `tau_x` be the
first inclusive alarm time from the reset detector state, let
`w_x = min(m,tau_x)`, and define

```text
U_x = (1/w_x) sum_{r=0}^{w_x-1} X_{tau_x-r}.
```

With independent `F ~ N(0,1/m)`, the kernel is

```text
P(x,A) = P{rho U_x + (1-rho)F in A}.
```

`tau_x` is a stopping time for the raw filtration because `x` is fixed within a
cycle and both detector recurrences and the inclusive crossing decision at time
`t` are measurable functions of `X_1,...,X_t`.  The random denominator is
exactly the number of included terminal observations.  At `rho=0`, the kernel
is the state-independent `N(0,1/m)` law.  At `rho=1`, it is the selected raw
terminal-window mean with no fresh component.

### Uniform stopping-time control

The CUSUM block argument is valid uniformly in `x`: according to the sign of
`x`, either ten consecutive `Z_t >= 1` or ten consecutive `Z_t <= -1` has
probability at least `Phi(-1)^10` and forces a crossing from every reachable
detector state.  The SR argument is also valid: its log statistics stay
nonnegative, and one observation with
`Z_t >= log(A)+1/2` or its negative counterpart forces an inclusive crossing
from every reachable state.  This yields a finite `sup_x E_x tau` for both
detectors.  The constants are independent of `x` and `m`, but extremely loose.

Large `|x|` creates no omitted corner case; it makes one alarm arm easier to
cross.  The proof does not assume compactness.

### Wald/Tonelli and moments

For integer `p >= 1`, convexity and nonnegativity give

```text
|U_x|^(2p) <= sum_{t=1}^{tau_x} |X_t|^(2p).
```

Only this full stopped sum is handled by Wald/Tonelli.  The selected terminal
window is first bounded by the stopped sum; it is not incorrectly treated as
iid.  Because `{tau_x >= t}` is measurable at time `t-1` and `X_t` is
independent of that sigma-field,

```text
E_x sum_{t=1}^{tau_x} |X_t|^(2p)
  = E_x[tau_x] E|X_1|^(2p).
```

Tonelli handles the nonnegative series and the stopping bound supplies
integrability.  Thus the written even-integer moment bound is valid.  Bounds
for every real order `q>0` follow from any larger even integer moment by
Lyapunov's inequality.  The phrase “all moments” is therefore justified.

### Return, minorisation, and Doeblin

The uniform second-moment bound gives a bounded set `C=[-R*,R*]` with
`inf_x P(x,C) >= 1/2` by Markov's inequality.

On `C`, choose an interval `J` of raw observations above
`R* + c_D`, where `c_D` is the detector's one-step plus-alarm margin.  For all
`x in C` and `u in J`, `tau_x=1`, so `w_x=1` and `U_x=u`, for every `m`.

* At `rho=1`, the normal raw density restricted to `J` dominates a uniform law
  on `J`; no fresh noise is needed.
* At `0<rho<1`, the Gaussian fresh density has a positive lower bound on a
  compact output interval after integrating over `u in J`.
* At `rho=0`, the kernel is already independent of `x`.

The resulting minorising measure is real and common over `x in C`.  The proof
as written produces constants for each fixed `(D,m,rho)`; it does **not** prove
one useful positive constant uniform over all `m` and `rho` simultaneously.
That stronger uniformity is unnecessary for T7.

Combining return and minorisation gives

```text
P^2(x,A) >= epsilon nu(A)  for all x and measurable A.
```

The standard Doeblin/Dobrushin contraction theorem then supplies a unique
`P^2`-invariant probability and geometric total-variation convergence.  The
short argument that `pi P` is also `P^2`-invariant makes `pi` invariant for `P`
and establishes uniqueness for `P`.  This is the whole-space-small-set
criterion in Meyn and Tweedie, *Markov Chains and Stochastic Stability*, 2nd
edition, Theorem 16.0.2; here the claimed bound also follows directly from the
minorisation decomposition and contraction.

Invariant moments follow by integrating the already established uniform
one-step bounds against `pi`.  The Doeblin constants are qualitative and must
not be equated with the measured IACT.

### T7 adjudication

`T7 = EXACT THEOREM`, scoped per fixed `(D,m,rho)`.  It proves existence,
uniqueness, uniform geometric ergodicity, symmetry, and moments of every real
positive order for the frozen Gaussian convention-A chain.  It does not give a
practical mixing rate, transfer to state-dependent P6 policies, or prove that
sample paths are bounded; an invariant law with unbounded support still has
arbitrarily large excursions.  It does rule out convergence to infinity and
gives uniform-in-time tightness from every initial state.

## Raw-mean identity and selection channel

The algebra is exact:

```text
zbar = U_x - x,
rho(x+zbar) + (1-rho)F = rho U_x + (1-rho)F.
```

A fresh implementation in `experiments/independent_adjudication.py` compared
against the frozen P7 cycle implementation for both detectors,
`m in {1,2,3,5}`, `rho in {0,0.37,1}`, and positive and negative entering
errors.  Across 48 configurations, every `tau` matched exactly; the maximum
terminal-window and next-state gaps were both `6.66e-16`.

The empirical selection-channel picture is sound within the measured grid:
large local tangent gain near zero, bounded conditional raw-window means, and
near-immediate alarm/near-`N(0,1)` terminal raw observations for large `|x|`.
The discovery text's statement that the far-field law is *exactly* normal at a
finite `|x|` is false because Gaussian tails leave a nonzero chance of
`tau>1`; it is an excellent approximation in the reported simulation, and an
exact limiting statement as the one-step selection constraint becomes
negligible.

## P3 local correspondence

The exact identity `M_rho = rho R`, together with the closed P1/P2 derivative
result, gives `R'(0)=1-GammaTilde` under the same frozen conventions.  The
independent bandwidth audit reanalysed both seed families using symmetric
differences at `h=0.005,0.01,0.02,0.03,0.05`.  Bias grows smoothly with
bandwidth: at `h=0.05` the discrepancy is about 6--9%, while at `h=0.005` it is
0.1--3.2% and every cell is statistically compatible with P3.  Some smallest
bandwidth signs reverse across seed families.

```text
P3_SLOPE_CORRESPONDENCE = CONSISTENT_WITH_NUMERICAL_BIAS
```

The one-signed regression result came from finite-bandwidth curvature plus
Monte Carlo noise; there is no detector/window convention mismatch.

## Deterministic skeleton and period two

Oddness gives the exact algebraic equivalence for **symmetric** cycles:

```text
{e,-e} is a 2-cycle  <=>  s(e)=-R(e)/e = 1/rho.
```

Under the stated H2/H3 sign, continuity, one-crossing, and outer bound
assumptions, existence and uniqueness of a positive symmetric solution for
`rho>rho_c` and its amplitude tending to zero are valid conditional theorems.
These assumptions remain finite-grid empirical hypotheses.

The discovery proof does not establish a classical attracting supercritical
flip theorem.  It lacks a proved attraction inequality on the full branch and
does not verify the usual smooth nondegeneracy coefficient.  It also does not
exclude asymmetric 2-cycles.  The PCHIP orbit scan provides strong finite-grid
numerical evidence: onset within `0.0055` of `rho_c`, only periods 1 and 2 in
the scan, no asymmetric cycle found, and measured multiplier below one.  The
authoritative wording is therefore:

* local multiplier crossing at `rho_c`: exact, given differentiability and the
  closed derivative correspondence;
* continuous symmetric branch: conditional theorem on H2/H3;
* attracting supercritical flip, global uniqueness of all 2-cycles, and no
  later cascade: numerical evidence on the measured PCHIP map.

## T10 and operational interpretation

Conditional on the symmetric branch tending to zero and continuity of `S` at
zero, the one-step conditional variance has a strictly positive limit, so

```text
e*(rho) / sqrt(V_rho(e*(rho))) -> 0 as rho -> rho_c+.
```

This is a valid **conditional asymptotic theorem**.  It shows that this branch's
amplitude is locally small relative to one-step noise.  It does not imply that
“no statistic can show a feature” at `rho_c`; a vanishing amplitude alone does
not rule out changes in derivatives, rates, or other functionals of the
stochastic kernel.  T10 is consistent with and helps interpret P7's negative
operational-boundary result, but it does not cause or prove that result.

## T11 and the 0.0174 discrepancy

Stationarity, symmetry, and the finite second moment give

```text
Cov(e_j,e_{j+1})
  = E[e_j E(e_{j+1}|e_j)]
  = rho E[e R(e)]
  = -rho E[e^2 s(e)].
```

Dividing by `E[e^2]` proves

```text
ACF1 = rho(1-Gamma_eff),
Gamma_eff = 1 + E[e^2 s(e)]/E[e^2].
```

No separate innovation-orthogonality assumption is needed; the tower property
and the conditional mean already integrate out the fresh term.  T11 survives
as an exact theorem.

The independent long-chain replay targeted the worst discovery cell,
SR/`m=3`/`rho=0.8`, and recorded the realised terminal raw mean rather than
using a gridded conditional map.  Over 32 independent chains and 4,500
post-burn cycles each:

```text
measured ACF1                  = -0.54797 +/- 0.00186 (SE)
direct realised-Rbar identity = -0.54752 +/- 0.00179 (SE)
paired gap                    = -0.00045 +/- 0.00034 (SE)
discovery PCHIP prediction    = -0.53150
```

Thus the `0.0174` discrepancy is a gridded-map/PCHIP plug-in error (including
the map estimator and interpolation), not chain autocorrelation, burn-in,
ratio bias large enough to matter, or a theory error.  G14 passes its literal
`<0.02` threshold, but that threshold concealed a statistically significant
plug-in discrepancy.

## Stationary law, dispersion, detectors, and windows

T7 makes the invariant law well posed.  Its shape remains numerical evidence.
The four measured density cells support a unimodal-to-bimodal contrast crossing
at roughly `4.1x--9.8x rho_c`.  This is neither a theorem nor an eight-cell
result.  Linear interpolation of a noisy density contrast does not provide a
confidence interval for onset.  Residence times `1.08--1.46` cycles reject
metastability in the tested cells and definition; bimodality does not imply
multiple invariant laws.

The interior RMS minimum is strong finite-grid evidence in all eight cells.
The measured ratios are `1.5x--4.9x rho_c` (not `1.5x--4.5x`; SR `m=1` is
`4.9x`).  The exact grid minimum is unique at the 95% pairwise-SE level in five
cells; CUSUM `m=3`, CUSUM `m=5`, and especially SR `m=5` have multiple
statistically near-optimal grid points.  ARL's optimum is at the same grid point
in seven cells and an adjacent point in SR `m=5`; this is descriptive
co-location, not a theorem or proof of a common continuous optimum.  The
curvature ranking at `rho_c` is a finite 40-test diagnostic and supports P7; it
does not prove the absence of every possible operational signature.

CUSUM and SR have closely matching measured nonlinear summaries after ARL
matching, but “the same map away from zero” is too strong.  The comparison is
finite-grid Monte Carlo evidence, with a systematic local linearisation
difference.  Increasing `m` improves the listed dispersion and ARL metrics over
`m in {1,2,3,5}` and common measured `rho` values; it is not a monotonic theorem,
does not cover `m>5`, and does not improve every conceivable metric (measured
SNR, for example, increases).

## Theory-status table

| statement | authoritative status |
|---|---|
| T1 raw identity | **EXACT THEOREM** |
| local derivative correspondence | **EXACT THEOREM**; numerical estimates **CONSISTENT_WITH_NUMERICAL_BIAS** |
| T7 invariant law / uniform ergodicity / all moments | **EXACT THEOREM**, per fixed `(D,m,rho)` |
| multiplier crosses `-1` at `rho_c` | **EXACT LOCAL STATEMENT** under the closed derivative convention |
| nonzero symmetric 2-cycle existence | **CONDITIONAL THEOREM** on H2/H3 |
| unique symmetric 2-cycle | **CONDITIONAL THEOREM** on one-crossing H3; uniqueness among all cycles unproved |
| attraction / supercritical flip classification | **NUMERICAL EVIDENCE** on the measured PCHIP map |
| T10 branch SNR tends to zero | **CONDITIONAL THEOREM**; universal operational-invisibility inference **REJECTED** |
| T11 ACF identity | **EXACT THEOREM** |
| bimodality onset | **NUMERICAL EVIDENCE**, four measured cells |
| dispersion/ARL optimum | **NUMERICAL EVIDENCE**, finite grid |
| monotonic improvement with `m` | **NUMERICAL EVIDENCE** for specified metrics and `m<=5` |

## Audit of the 17 prior attacks

| attack | adjudication |
|---|---|
| A1 raw identity | **independently confirmed** in 48 configurations |
| A2 P3 slope object | **independently confirmed** |
| A3 one-sided slope bias | **partially confirmed**; bandwidth bias is clear, “deterministic” was too certain |
| A4 interpolation artifact | **partially confirmed**; independent scan supports the branch but still scans an estimated PCHIP map |
| A5 oddness residual | **partially confirmed**; exact symmetry survives, while the interval-calibration explanation is plausible rather than proved |
| A6 initialisation artifact | **independently confirmed** for the measured chain cells |
| A7 dispersion minimum noise | **partially confirmed**; minimum is robust, exact location has near-ties in three cells |
| A8 seed replication | **independently confirmed** from artifacts and provenance |
| A9 unimodality draft | **independently confirmed as overturned**; bimodality evidence covers four cells |
| A10 multiple laws/metastability | **confirmed**: T7 gives one law; short residence rejects measured metastability |
| A11 circular T7 | **independently confirmed absent** |
| A12 vacuous constants | **independently confirmed**; qualitative theorem survives |
| A13 T11 discrepancy | **overturned as unresolved**; direct replay isolates the gridded-map/PCHIP plug-in |
| A14 boundary grid artifact | **partially confirmed**; 0/40 is a scoped finite-grid diagnostic |
| A15 protected semantics | protected hashes **confirmed**; worktree-scope subclaim **overturned** by README/P6 |
| A16 detector/window dependence | **partially confirmed**; finite-regime evidence was overgeneralised |
| A17 bifurcation vocabulary | **insufficient**; attraction/nondegeneracy/global-cycle claims were not proved |

New attacks added by this adjudication reject the inference from `SNR->0` to
featurelessness of every stochastic statistic, reject exact finite-`e` reset
normality, and reject universal controller/no-guard implications for P6.

## Literal closure-gate audit

Each criterion below is quoted from `CODEX_HANDOFF.md` section 17.

| gate and literal criterion | result | evidence and dependency |
|---|---|---|
| G1: “`tau` identical; `max abs e_start diff < 1e-13`” | **PASS** | supplied test plus fresh 48-configuration replay; no H2/H3 |
| G2: “`< 2%` relative, 8/8 cells” | **PASS** | discovery regression and both seed families; finite-bandwidth estimate |
| G3: “`sup_e |R| < 2` in 8/8” | **FAIL** | only a finite grid was measured; this is unproved H3b |
| G4: “`|R| < 0.01` for `|e| >= 10`, 8/8” | **FAIL** as universal; **PASS on measured tail grid** | finite-grid extrapolation and Monte Carlo |
| G5: “periods subset of `{1,2}` in 8/8” | **PASS for the specified scan** | 199-rho/84-start PCHIP scan; not a global theorem |
| G6: “onset vs `rho_c <= 0.0075`, 8/8” | **PASS** | finite scan and tolerance classification |
| G7: “multiplier `<1` wherever it exists” | **FAIL** | evaluated finite branch grid; global attraction is unproved |
| G8: “SNR `<0.15` at first resolvable `rho`” | **PASS** | finite grid; post-resolution metric |
| G9: “SNR anywhere `<2.5`” | **FAIL** as universal; **PASS on measured branch grid** | interpolation/finite-grid extrapolation |
| G10: “0 metrics rank `rho_c` first” | **PASS** | exactly 0/40 specified finite comparisons; post-hoc metric risk remains |
| G11: “interior, `rho*>1.4 rho_c`, `RMS(rho*)<0.75 RMS(1)`, 8/8” | **PASS** | finite grid; exact optimum location has near-ties |
| G12: “max `z<4` over 176 cells” | **PASS** | 3.88; replicate is the unit and null max calibration is supplied |
| G13: “kurtosis `<3.1` in all cells” | **PASS** | produced chain grid; not a tail theorem |
| G14: “T11 absolute gap `<0.02`” | **PASS** | 0.0174, though up to 16 chain SE; direct replay resolves plug-in error |
| G15: “`Gamma_eff <0.25 x GammaTilde`” | **PASS** | finite measured cells; ratio estimator/interpolation |
| G16: “global max `|e| <= max(|e0|,6)` in every stress cell” | **PASS** | specified finite stress experiment; T7 separately rules out divergence |
| G17: “bimodality onset `>3x rho_c` in every measured cell” | **PASS** | four measured cells, noisy crossing interpolation |
| G18: “residence `<1.6`; alternation `>0.8` for `rho>=0.6`” | **PASS** | finite density cells; supports rejection of metastability in that regime |
| G19: “12 declarations, sorry-free, axioms subset of three standard ones” | **PASS** | rebuilt during adjudication; 12 declarations, exact allowed axiom set |
| G20: “294 files byte-identical; worktree scope = P5 only” | **FAIL** | hashes pass; root README and P6 pre-design make the conjunctive criterion false |

Summary, counting the criteria literally: `15 PASS`, `5 FAIL`. G3, G4, G7,
G9, and G20 fail. G4 and G9 do pass on the produced finite grids, but their
universal wording does not. No gate was rewritten to manufacture closure.

## Statistical audit

Seed derivation is deterministic and hash-free.  The two map families are
independent.  Map uncertainty uses eight independent batches, although normal
intervals with only eight batches slightly understate uncertainty; the prior
review's `t_7` observation is correct.  Chain summaries use replicate chains as
the statistical unit, which is appropriate.  Burn-in and three starting groups
are adequate given the independently proved uniform ergodicity and the observed
mixing.

Weak points are the noisy ratio/interpolation calculations for T11, unquantified
PCHIP uncertainty, linear interpolation of density crossings without onset
intervals, multiple metric/grid comparisons, and finite-grid selection of
optima.  The reported chain SE cannot be used as the SE of a map-plug-in
prediction.  The direct T11 replay fixes the highest-impact instance.

## Verification

* Focused P5 suite: **44 passed, 1 failed**.  The sole failure is frozen G20's
  worktree-scope assertion, caused by the known root README and P6 pre-design.
* Independent replay: **PASS**, written to
  `results/independent_adjudication.json`.
* Lean rebuild: **PASS**, 12 declarations, sorry-free, only `propext`,
  `Classical.choice`, and `Quot.sound`.
* Repository-wide verification: **no P5 regression**. The full Level 1--3
  verification passed with zero skips, including Lean source elaboration, Arb
  replay, and 90 regressions. The Level-4 aggregate passed frozen Level 1--3
  (90), Stages A--F (290/46/48/36/72/59/54), post-closure (18), and D4 (18),
  then stopped at the known novelty protected-history manifest failure
  (`92 != 52`). A clean archive of authoritative HEAD fails the same node even
  earlier (`33 != 41`). Post-failure continuation passed external V3 (75),
  L4R-06 (28), and L4R-12 (26). External V2 (43/45), final global re-audit
  (33/36), and terminal closure (32/36) retain their historical
  protected-history/generated-byte failures; every exact failing group also
  fails in the clean baseline archive. See `results/repository_verification.json`.

## Exact P6 handoff

P6 **may** use as authoritative premises, only for the frozen constant-policy
Gaussian convention-A model:

1. T1's exact raw-mean transition law and T2's conditional mean/variance
   factorisation.
2. T3 symmetry.
3. T4/T5's state-independent stopping and moment bounds.
4. T7 existence, uniqueness, uniform ergodicity, symmetry, and all positive
   invariant moments for each fixed `(D,m,rho)`.
5. T11's exact stationary ACF identity.
6. The finite-grid `R`, `S`, dispersion, ARL, density, detector, and window
   results as **numerical prior information**, with their audited uncertainty
   and scope.
7. P7's already-authoritative rule that `rho<rho_c` is not an operational
   safety rule under its frozen criterion.

P6 **must not** use:

1. T7 for state-dependent/adaptive policies without a new proof.
2. H2/H3, global one-crossing, global 2-cycle uniqueness, attraction, or a
   supercritical flip classification as exact premises.
3. T10 as proof that no stochastic operational statistic can change at
   `rho_c`, or as a causal proof of P7.
4. `rho*=0.15--0.30`, `rho*/rho_c`, bimodality onset, `Gamma_eff`, or detector
   transfer as design constants or safety thresholds.
5. Exact RMS/ARL co-optimality or a universal theorem that larger `m` improves
   all metrics.
6. Exact one-cycle reset at finite `|e|`, guaranteed bounded sample paths, or
   the claim that divergence guards/reset logic can never be useful for a
   controller outside the frozen constant-policy model.
7. Any statement that P6's full campaign has started; only pre-design exists.
