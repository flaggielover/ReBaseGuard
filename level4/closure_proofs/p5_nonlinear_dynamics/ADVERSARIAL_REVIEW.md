# P5 adversarial self-review

Every candidate conclusion was attacked before it was written down. Attacks
that **changed the campaign** are marked ★.

## A1 ★ — "The raw-mean identity is too good to be true; you re-derived the model"

*Attack.* A cancellation that removes the state variable from a recursion is
exactly what a subtly wrong re-derivation looks like.

*Test.* Do not trust the algebra. Re-implement the frozen chain with the buffer
holding `raw_t` instead of `z_t`, consume the RNG in the identical order, and
compare against `rebaseguard_p7.chain.simulate_chain` (itself bit-identical to
`level4/stage_d/src/chain.py`).

*Result.* 12/12 configurations: `tau` arrays **bit-identical**;
`max |e_start difference| = 8.9e-16`, i.e. a few ULP of the reordered
floating-point sum — the signature of an exact identity computed in a different
association order, not of a different model. A second test compares
`Rbar_w` against `e + zbar_m` path-by-path on the frozen `p7.cycles` object
(`< 1e-12`).

*Outcome.* Identity stands. **This attack changed the campaign**: it forced the
truncated-denominator test (`test_window_denominator_is_truncated`), which
established that the identity is specific to the frozen Stage-D convention A
and would fail for a fixed-`m` denominator — now stated as a remark in
`PROOF.md`.

## A2 — "Is the local slope really P3's, or did you fit a different object?"

*Test.* Estimate `R'(0)` from the map grid alone and compare with the CLOSED
P3 `boundary_table.json`, which is read and never recomputed.

*Result.* Agreement to `0.14%–1.6%` in all eight cells; the induced `rho_c`
differs by at most `0.0012`. The residual is one-signed (P5 always slightly
below P3), reproduced by an independent seed family, and is a finite-difference
bias from the concavity of `R`. Logged as A3.

## A3 — "The one-signed slope bias is a real disagreement with P3"

*Test.* Repeat under seed family `20261119`. If it were Monte Carlo the sign
would flip in roughly half the cells.

*Result.* It does not flip; deviations `0.0001–1.1%`, same sign in 8/8. So it
is a deterministic finite-difference bias of the estimator, not a
model disagreement: `R` bends towards the origin, so a fit over `|e| <= 0.01`
sits below the tangent. Nothing in T8–T11 uses the numerical value.
**Non-material, documented, unresolved at the 1% level.**

## A4 — "The bifurcation is an artifact of the interpolation"

*Test.* The T9 branch is derived from the algebra `s(e*) = 1/rho`. Independently,
`run_skeleton.py` iterates the measured PCHIP map from 84 initial conditions,
199 values of `rho`, 4000 transient steps, and classifies the period of the last
256 iterates with no algebraic input.

*Result.* Periods 1 and 2 only, in all eight cells; onset within one `0.005`
grid step of the frozen P3 `rho_c` in **all eight**; no period 4, no cascade,
no aperiodic orbit, no asymmetric 2-cycle. One cell (SR `m=2` at `1.01 x rho_c`)
failed the `1e-7` convergence tolerance with amplitude `0.017` — critical
slowing down at a flip bifurcation, checked by inspecting the orbit.

## A5 ★ — "The oddness residual is larger than your error bars"

*Attack.* T3 says `R(-e) = -R(e)` exactly. The measured residual exceeds the
95% batch interval in 3–7 of 34 pairs per cell, up to `1.9 x` the interval.

*Test.* (i) Absolute size: max residual `0.011` against `|R|` up to `1.59`
(`<0.7%`). (ii) Interval calibration: with 8 batches, a `z`-interval understates
a `t_7` interval by 21%; on the `t_7` scale the worst case is `1.6 x`. (iii)
Independent seed family: residuals of the same magnitude, uncorrelated sign
pattern.

*Result.* An estimator-variance calibration issue, not evidence against an
exactly proved symmetry. **This attack changed the campaign**: every *inferential*
use of `R` — the deterministic skeleton scan (`run_skeleton.py`) and the T11
prediction (`analyze_chain.py`) — now applies the exact symmetrisation
`R <- (R(e) - R(-e))/2`, so no conclusion can inherit an antisymmetry artifact.
The hypothesis audit and the figures deliberately keep the **unsymmetrised**
estimate, because their job is to display and falsify it.

## A6 — "The 2-cycle is a burn-in / initialisation artifact of the chain"

*Test.* Three initial-condition groups (`e_0 = 0, +6, -6`) inside every one of
176 chain cells; 400-cycle burn-in; compare post-burn-in `RMS`, `ACF1`, `ARL`
across groups.

*Result.* Over 552 max-of-three-pairs `z` statistics (176 cells x
`RMS`/`ACF1`/`ARL`) the median is `1.11`, only `2` exceed `3`, and the maximum
is `3.88` — against a null distribution whose own median maximum is `3.53` and
95th percentile `4.17`. Fully consistent with noise. The stress test is stronger: from `e_0 = 10^6` the mean
`|e_1|` after **one** cycle is `0.83`. There is no burn-in to speak of — the
measured integrated autocorrelation time is at its floor (`<= 1` cycle).

## A7 — "The dispersion minimum at `rho ~ 0.2-0.3` is Monte Carlo noise"

*Test.* Replicate 95% intervals on `RMS` are `+/-0.003`–`0.004`; the minimum is
`0.098` below the value at `rho_c` (CUSUM `m=1`) — 25–30 standard errors — and
appears in **8/8** cells with the same qualitative shape, on both detectors, at
consistent locations (`0.16`–`0.30`). The in-control `ARL` is maximised at the
same `rho` in 7/8 cells and one adjacent grid point in the eighth.

*Result.* Robust. Reported as the campaign's main operational finding.

## A8 — "A larger simulation reverses the map"

*Test.* Full independent replication of the map experiment (seed family
`20261119` vs `20260501`), 392 paired grid cells.

*Result.* `mean z = +0.016`, `sd z = 1.044`, `max |z| = 3.12`; fractions
`|z|>2 = 5.6%`, `|z|>3 = 1.0%` against nominal `4.6%`/`0.27%` — a mild excess
consistent with the 8-batch `t` vs `z` calibration of A5. Derived quantities
(`e*(1)`, multiplier, `SNR`) agree to 3–4 decimals in all 8 cells.

## A9 ★ — "You are calling smooth stochastic broadening a bifurcation"

*Attack.* The most available false positive in P5. A supercritical flip and a
smoothly broadening unimodal law can look alike.

*Test.* Separate the two objects explicitly and never mix their tiers. (i) The
*deterministic skeleton* is a genuinely different object from the chain, and it
does bifurcate — proved (T9, conditional on measured (H1)–(H3)) and verified by
a from-scratch orbit scan (A4). (ii) The *chain* is tested for the signature
with a pre-registered per-replicate statistic:
`density(+e*) + density(-e*))/2 - density(0)`, negative = unimodal, positive =
mass on the orbit.

*Result.* Both are true, at different `rho`. `contrast < 0` (significantly) at
`rho = 0.3`; `contrast > 0` (significantly) at `rho = 0.8` and `1.0`. So the
chain's marginal law really does become bimodal — **but only at `rho` of order
`0.5–0.8`, i.e. `7x–12x rho_c`, and never near the bifurcation point**. That is
exactly what T10 predicts. **This attack changed the campaign**: the original
draft claimed the stationary law was unimodal at every `rho` (based on a
5110-point subsample); the dedicated 864000-sample-per-cell experiment
(`run_density.py`) overturned that, and the claim was corrected before
publication rather than defended.

## A10 — "Multimodality means multiple attractors / multiple invariant measures"

*Test.* T7 proves the invariant law is **unique** for every `(D, m, rho)` in the
frozen core. So any multimodality is structure inside one invariant law.
Metastability is tested separately by residence time: how many consecutive
cycles does the chain spend on one side?

*Result.* Mean residence is `1.08–1.46` cycles across every measured cell, and
*falls* as `rho` rises (`1.46` at `rho=0.3` to `1.08` at `rho=0.8`), with a
sign-alternation rate rising to `0.93`. The chain does not linger in a mode —
it flips almost every cycle. This is a *stochastic period-2 orbit*, the
opposite of metastability. Multiple attractors: **rejected**, by theorem and by
measurement.

## A11 — "The stationary-law theorems assume what they should prove"

*Test.* Audit the proof of T7 for circularity. Steps: (1) T4 bounds `E[tau|e]`
uniformly by an explicit block argument — no stationarity used; (2) T5 bounds
`E[Rbar^{2p}|e]` by Jensen + Wald — no stationarity used; (3) Chebyshev gives a
one-step return to a compact set — no stationarity used; (4) the `tau = 1`
event gives a minorisation on that set with an explicit `delta` — no
stationarity used; (5) Doeblin on `P^2` yields existence **and** uniqueness.
Moments of `pi` then come from `pi = pi P` and the *already proved* uniform
one-step bound.

*Result.* No step assumes a stationary law. T11 is the only statement that uses
`pi`, and it is stated as conditional on T7, which supplies it.

## A12 — "The theorem is vacuous because your constants are absurd"

*Test.* Honest accounting. `C_CUSUM <= 9.9e8` against a measured `465`;
`delta'` is astronomically small. The TV rate in T7(2) is therefore useless as a
quantitative statement.

*Result.* Accepted and stated. T7's *qualitative* content (existence,
uniqueness, ergodicity, all moments finite, no runaway) is what closes P7's
gaps, and it is not weakened by loose constants. Quantitative mixing is reported
separately as measurement (`IACT <= 1` cycle). `LIMITATIONS.md` §3 records the
sharpening route (import the measured `sup_e A(e)` as a hypothesis) and does not
claim it.

## A13 — "The T11 cross-check does not actually agree"

*Attack.* Predicted `ACF1` (from the map) vs measured `ACF1` (from the chain)
differ by up to `16 se`.

*Test.* Look at absolute size and at the error budget. Gaps: `0.0000–0.0174`,
median `0.0034`, on quantities of size `0.2–0.55`. The prediction uses a PCHIP
interpolant of a grid-measured `R` and a sub-sampled stationary sample, neither
of whose errors is in the quoted `se` (which is the chain's replicate `se`
alone).

*Result.* Agreement is `<= 0.018` absolute, `<= 3.5%` relative — strong support
for the identity, but **not** a `1-se` match, and it is reported that way.
Recorded as an unresolved discrepancy for Codex in `CODEX_HANDOFF.md`; the
identity T11 is *proved*, so the residual bounds the numerical machinery, not
the mathematics.

## A14 — "The boundary result is a grid artifact — you looked in the wrong place"

*Test.* A criterion different from P7's: at each `(det, m, metric)` compute the
second difference of the metric at the grid point nearest `rho_c`, in units of
its own standard error, and rank `|d2|` against every other interior grid point
of the same curve. If `rho_c` were special it would rank first.

*Result.* Rank 1 in **0 of 40** combinations; best rank 4 of 21. Five metrics
(`RMS`, `q95`, `P(|e|>2)`, `ACF1`, `ARL`), eight cells. The `rho` grid was
explicitly refined around `rho_c` (`0.5, 0.8, 1.0, 1.25, 1.5, 2 x rho_c`), so
the null result is not a resolution failure. Independently confirms P7 C2.

## A15 — "Did any frozen P1–P4/P7 semantics drift?"

*Test.* `tests/test_protected_tree.py` re-hashes all 294 files under the six
protected roots and compares with `results/protected_hashes_before.txt`; a
second test asserts the git worktree contains no modification outside the P5
directory. `tests/test_correspondence.py::test_p3_boundary_table_untouched`
pins the eight frozen `rho_c` values by value.

*Result.* No drift. P5 imports P7's package read-only and never writes to it.

## A16 — "Detector or window dependence is being hidden"

*Test.* Every experiment runs both detectors and all four windows; no result is
reported from a single cell.

*Result.* The nonlinear regime is **detector-independent** to Monte Carlo
precision (`e*(1)` agrees to `0.002`, `SNR` to 3 decimals), while the
*linearisation* differs by `~9%` (SR's `GammaTilde` is larger). Window `m`
changes everything monotonically and predictably. Both facts are reported, and
the detector-independence is what makes the P6 handoff detector-agnostic.

## A17 — "You forced classical bifurcation vocabulary"

*Test.* Before using "flip bifurcation", check the definition against an actual
object: a one-parameter family `f_rho` with a fixed point whose multiplier
crosses `-1`, a branch of period-2 orbits on exactly one side, emerging
continuously with zero amplitude, and no other bifurcating branch.

*Result.* All four conditions verified (T8 for uniqueness of the fixed point,
T9 for the branch, A4 for the absence of anything else). The words "pitchfork",
"saddle-node", "transcritical", "Hopf", "cascade", "chaos" and "multiple
attractors" are used **only in the negative** in this campaign, each backed by
T8, A4 or T7. The term "operational bifurcation" is explicitly **rejected**
(T10).
