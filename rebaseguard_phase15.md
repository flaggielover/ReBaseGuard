# ReBaseGuard — Phase-1.5 Adversarial Re-examination

**Working posture: unchanged — skeptical, phenomenon-first, and now self-correcting.** This memo re-runs
the Phase-1 experiments with an instrumented simulator after a hostile review flagged that the Phase-1
headline ("stable contractive AR(1), $|a|<1$ everywhere, no rich dynamics — PIVOT/STOP") rested on a
*secant* slope measured over $\pm0.5$ rather than the *local* derivative at the fixed point. That single
measurement error inverted the qualitative conclusion. All numbers below are Monte Carlo estimates from
this session (Gaussian mean-shift, two-sided CUSUM, slack $k=0.5$, boundary $h=5$). Figure:
`rebaseguard_phase15.png`.

**Headline finding (established this session, Level B): the Phase-1 stability claim is FALSE. The reference
recursion $e_{j+1}=F(e_j)+\varepsilon_j$ has a *locally unstable* fixed point at $0$ ($|F'(0)|>1$ for small
reuse windows) with a *globally bounded* nonlinear map, so the invariant law is BIMODAL and the chain
executes a noisy period-2 orbit — not the contraction to $e^\*\approx0$ Phase-1 reported. This is directly
observable in three matched-sample-size signatures that Phase-1 either mismeasured or missed: (i) alarm
directions alternate at rate 0.94 vs the fresh coin-flip 0.50; (ii) the reference-error ACF is a
damped oscillation (-0.56, +0.57, -0.47 at lags 1–3) against fresh $\approx0$ at every lag; (iii) reuse
cuts the in-control run length to 48% of matched-window fresh — a real calibration distortion, not
estimator noise. The effect turns on continuously with reuse fraction (a clean bifurcation) and survives
non-Gaussian noise. Recommendation: CONDITIONAL GO / PIVOT — the object is a genuine nonlinear stochastic
recursion with a characterizable invariant law and a run-length consequence, which is more than the
"reducible AR(1)" Phase-1 concluded, but still sits inside the self-starting / adaptive control-chart
literature and requires a literature clearance before any novelty claim.**

---

## 0. What Phase-1 got wrong, precisely

Phase-1 estimated the coupling slope $a(m)$ as a **secant** of $F$ over $e\in[-0.5,+0.5]$ and read
$a(5)=$ -1.36, concluding $|a|<1$ and "contraction to a unique point mass at $e^\*\approx0$." Two errors:

1. **Wrong derivative.** The secant over $\pm0.5$ straddles the bend-back of a strongly nonlinear map and
   understates the *local* slope at $0$. Measured locally, $F'(0)=$ -4.51 ($m{=}5$), -2.98 ($m{=}10$),
   -0.71 ($m{=}50$) — $|F'(0)|>1$ at small $m$ (Fig. b). The fixed point is **repelling**, not attracting.
2. **Wrong invariant law.** Because $F$ bends back sharply ($|F'|\ll1$ once $|e|\gtrsim0.4$), trajectories
   are pushed *away* from $0$ but *caught* before escaping — the hallmark of a bounded oscillator. The
   invariant density is **bimodal** (density at $0$ = 0.38, at the lobes $\approx$ 0.70; Fig. c), not
   a spike at $0$. Phase-1 reported only $\mathrm{sd}(e_j)$, which is blind to bimodality.

Phase-1's *non-pathology* falsifiers still hold and are not disputed: no bias accumulation, no divergence,
no persistent nonzero mean, no World-B hysteresis. The correction is narrow but qualitative — the chain is
**bounded and ergodic but oscillatory**, not **contractive** — and it changes the verdict because the
oscillation is a nonlinear period-2 orbit with an operating-characteristic cost, not a linear AR(1) nuisance.

---

## 1. The transition map and its instability (Fig. a, b)

**Established (Level B).** $F(e)=E[e_{j+1}\mid e_j=e]$ is odd, monotone through $0$ with slope $>1$ in
magnitude, then saturates: $|F'|$ exceeds $1$ *only* on a narrow interval around $0$ ($e\in[-0.2,+0.2]$ at
$m{=}5,10$) and falls to $\approx0.08$ by $|e|=3$. This is the canonical geometry of an unstable fixed
point inside a globally contracting map — a bounded oscillator. At $m{=}50$ the local slope is -0.71
($|F'(0)|<1$): the instability **switches off** as the reuse window grows and the excursion is diluted,
consistent with Phase-1's $m\to\infty$ argument but with the opposite sign of conclusion at small $m$.

*Mechanism.* A CUSUM alarm freezes a window whose mean carries the boundary excursion's sign. Reusing it
sets the next reference offset $e_{j+1}$ with sign *opposite* to the excursion that just fired — an
up-alarm leaves the reference too high, forcing the next alarm down. The gain of that sign-flip exceeds $1$
when the frozen window is small relative to the excursion length $O(h/k)$, i.e. exactly the small-$m$ regime.

---

## 2. Direct observables at matched sample size

All comparisons hold the reuse window $m$ fixed so that **fresh** (draw $m$ new post-alarm observations) is
an information-matched control; any naive-vs-fresh gap is a pure reuse effect, not a sample-size effect.

### 2.1 Run-length / calibration distortion (Fig. f) — Level B
| $m$ | fresh ARL / ARL$_{\rm oracle}$ | naive (reuse) | naive as % of fresh |
|---|---|---|---|
| 5  | —          | 0.17  | —      |
| 10 | 0.45  | 0.22 | 48% |
| 50 | 0.71  | 0.56 | 79% |

Reuse cuts the mean in-control run length to roughly half of matched-window fresh at $m{=}10$
(absolute ARL 101 vs 209; medians 33 vs 98). Because fresh at the same $m$
is the control, this is genuine in-control calibration loss — reuse **roughly doubles the endogenous
false-alarm rate** at matched nominal sample size. The gap narrows as $m$ grows (79% at $m{=}50$),
tracking the instability switch-off.

### 2.2 Alarm-direction alternation (Fig. e, g) — Level B
Fresh alarm signs are coin flips: $P(A_{j+1}=-A_j)=$ 0.50. Under reuse the sign stream alternates far
above chance: 0.92 ($m{=}5$), 0.94 ($m{=}10$), 0.80 ($m{=}50$). This is the period-2 orbit
made directly visible in the raw alarm stream — the single cleanest experimental signature, requiring no
density estimation.

### 2.3 Reference-error autocorrelation (Fig. d) — Level B
Multi-lag ACF of $e_j$ under naive reuse ($m{=}10$): -0.56, +0.57, -0.47 at lags 1, 2, 3 — a *damped
oscillation* (alternating sign, slow decay). Fresh is -0.00 at lag 1 and flat thereafter. Phase-1 saw
the lag-1 value and dismissed it as "AR(1)"; the alternating multi-lag envelope is the fingerprint of a
period-2 orbit, which a positive-marginal-variance AR(1) with $a<0$ reproduces only as pure geometric
decay — the *dynamical* content (an unstable fixed point) is what an AR(1) description discards.

---

## 3. Is it an artifact? Four kill-tests

### 3.1 Not a monitor-reset artifact (Fig. — reset sweep) — Level B
Carrying vs discarding CUSUM state across alarms does **not** create the alternation; it *weakens* it.
Full reset: alternation 0.94 (lag-1 ac -0.59). Retain 90% of CUSUM state: alternation drops to
0.69 (ac -0.09). The coupling lives in the **reference update**, not the detector reset — the
opposite of the Phase-1 hunch that a non-resetting Shiryaev–Roberts would couple *more* strongly.

### 3.2 A clean bifurcation in reuse fraction (Fig. e) — Level B
Sweeping the mix fraction $\rho$ (0 = fresh, 1 = full reuse), alarm-alternation rises continuously:
0.50 ($\rho{=}0$) → 0.72 → 0.90 → 0.96 → 0.94 ($\rho{=}1$). Fresh ($\rho{=}0$) is structureless;
the period-2 orbit switches on smoothly as reuse weight increases. The phenomenon is a controllable
function of one interpretable knob, not a fixed quirk of one policy.

### 3.3 Robust to noise model (Fig. g) — Level B
Alarm-alternation under naive $m{=}10$: Gaussian 0.94, Student-$t_3$ 0.90, skewed 0.91,
contaminated 0.77. It is not a Gaussian-symmetry artifact; heavy tails and asymmetry preserve it (the
contaminated case lowers it only because contamination shortens runs outright).

### 3.4 Unique invariant law and long-run stationarity (Fig. i) — Level B
From initial offsets $e_0\in\{-3,-1,0,+1,+3\}$ all trajectories converge to the same invariant law
($E|e_j|\to\approx0.47$ by cycle 20; max spread across $e_0$ = 0.0029). Over $J{=}1000$ cycles the late
blocks are stationary: $\mathrm{sd}(e_j)$ = 0.541 → 0.541, ARL = 100 → 101. So the chain is
Harris-ergodic with a *single* bounded invariant measure — Phase-1's "no divergence / no multiple
attractors" survives; only the *shape* of that measure (bimodal, not a point mass) is corrected.

---

## 4. The hidden state is the reference offset, not the run length (Fig. h)

**Established (Level B).** The next inter-alarm run length is essentially independent of the previous run
length (P(next short | prev short) = 0.24 vs | prev long = 0.25; marginal 0.25) but strongly
predicted by the previous reference offset (| prev $|e|>$med = 0.42 vs | prev $|e|<$med = 0.07). The
Markov driver is the scalar $e_j$, exactly as Phase-1 said — but because $e_j$ oscillates, the induced run
lengths **anti-cluster** (a short run follows a large $|e|$, which the orbit then flips), which *falsifies*
the brief's alarm-*clustering* hypothesis (measured clustering 0.40 < base 0.51) while confirming
the alternation that replaces it.

---

## 5. World B — no resonance (honest null) — Level B

A natural worry is that the null-world period-2 orbit *resonates* with a truly alternating drift and
inflates detection delay. It does not. Under alternating means (0, +2, 0, +2, …) the naive mean detection
delay is 102 vs fresh 208; the shorter naive delay is entirely explained by its doubled alarm rate
(Section 2.1), and the mean reference error stays at +0.000 ($\approx0$) with no amplification. The
phenomenon is a **stationary-null** effect; it neither helps nor harms drift tracking. Reporting this as a
null is deliberate — it removes the most attractive "application" and keeps the contribution honest.

---

## 6. Corrected candidate-mechanism table

| candidate (brief) | Phase-1 verdict | Phase-1.5 corrected verdict | level |
|---|---|---|---|
| bias accumulation $|E[e_j]|\uparrow$ | absent | **absent** (confirmed) | falsified |
| amplification $|a|>1$ | falsified (secant) | **PRESENT locally**: $|F'(0)|>1$ small $m$ | **B — overturned** |
| self-stabilization / contraction | present | **FALSE**: fixed point repelling | **overturned** |
| persistent offset $e^\*\neq0$ | absent | absent (mean 0) | falsified |
| multiple attractors | absent | absent — single invariant law | falsified |
| oscillation | present "= AR(1)" | **PRESENT — nonlinear period-2, not AR(1)** | **B — upgraded** |
| bimodal invariant law | not tested | **PRESENT** (density dips at 0) | **B — new** |
| run-length distortion at matched $m$ | not isolated | **PRESENT** — ARL halved | **B — new** |
| endogenous false-alarm inflation | "not observed" | **PRESENT** — $\approx2\times$ at matched $m$ | **B — overturned** |
| World-B overshoot / resonance | absent | absent (no resonance) | falsified |

---

## 7. Candidate mathematical object (corrected)

$e_{j+1}=F(e_j)+\varepsilon_j$ with $F$ odd, $|F'(0)|>1$, $|F'(e)|\to0$ as $|e|\to\infty$ — an **iterated
random function with a repelling fixed point inside a globally contracting envelope**. Such maps have a
unique bounded invariant law that is **bimodal / period-2-like** when the local instability is strong
enough, exactly the observed regime. The reduction Phase-1 offered (affine $|a|<1$ AR(1)) is the *wrong*
linearization: it is the secant, and it discards the instability that produces every observable in Section 2.

*What is provable now vs. what is not.* The existence of a unique bounded invariant law follows from
standard iterated-random-function theory (bounded Lipschitz-on-average map + additive noise). **UNPROVEN /
REQUIRES PROOF:** (i) a closed-form or tight bound for $F'(0)$ as a function of $(m,k,h)$ and the exact
$m^\*(k,h)$ at which $|F'(0)|$ crosses $1$ (the bifurcation boundary); (ii) that the invariant law is
genuinely bimodal (not merely heavy-shouldered) above that threshold; (iii) the induced endogenous
false-alarm rate as a function of the orbit amplitude. These are the theory deliverables a GO would owe.

---

## 8. Literature verification

**LITERATURE VERIFICATION REQUIRED (partial).** Three targeted searches this session (self-starting CUSUM
with estimated parameters; adaptive charts that update the reference after a signal; repeated / multi-cyclic
change detection with re-estimation) returned the *neighboring* facts but no direct hit:

- **Estimated-parameter run-length degradation** is well documented — using estimated rather than known
  in-control parameters substantially degrades and destabilizes conventional chart run-length performance.
  This is the closest prior art to Section 2.1, but it concerns estimation from an *unselected* Phase-I
  sample, not observations *selected by the stopping event* and *reused recursively across alarms*.
- **Self-starting / conditional-ARL work** shows a chart's realized in-control performance depends on the
  early reference readings (conditional vs unconditional ARL). This is adjacent to the $e_j$-as-hidden-state
  finding but again assumes a fixed (if random) reference, not a recursively re-selected one.
- **Multi-cyclic quickest detection** (Pollak–Tartakovsky style) repeats the *same* stopping rule over
  independent segments; there is no reference reuse and no cross-cycle coupling, so the period-2 orbit
  cannot arise there by construction.

I found **no** source describing a repelling reference fixed point or period-2 alarm-direction alternation
produced by stopping-selected recursive reuse. That absence across three searches is suggestive but not
exhaustive; a niche self-starting-chart or adaptive-windowing paper could contain it. **No citations are
asserted.** A proper clearance (systematic search + a control-charts specialist read) is a precondition for
any novelty claim.

---

## 9. GO / PIVOT / STOP — revised

Phase-1 recommended **PIVOT/STOP** on the ground that the recursion was a stable, reducible AR(1). That
ground is now shown to be a measurement error. The corrected evidence is:

- a **locally unstable fixed point** with a **bimodal invariant law** (nonlinear, not AR(1));
- a **clean bifurcation** in reuse fraction (one interpretable control knob);
- a **matched-sample-size run-length distortion** ($\approx2\times$ false-alarm inflation) — an operating
  cost, not just a nuisance variance;
- **robustness** to noise model and monitor-reset;
- an honest **null** in World B (no resonance), which bounds the claim rather than inflating it.

**CONDITIONAL GO / PIVOT.** The honest framing is not "rich chaotic dynamics" (the chain is a tame bounded
period-2 oscillator) but **"stopping-selected recursive reuse induces a characterizable bifurcation into a
bounded oscillatory reference orbit, with a quantifiable in-control false-alarm cost."** That is a real,
reproducible, Level-B phenomenon with a concrete theory program (Section 7) and a concrete practical
consequence (Section 2.1). It clears the bar for continued work **conditional on** two gates:

1. **Literature gate.** The Section 8 clearance must confirm the bifurcation / period-2 result is not
   already in the self-starting-chart or adaptive-windowing literature. If it is, STOP.
2. **Theory gate.** At least one of the Section 7 UNPROVEN items — most naturally the bifurcation boundary
   $m^\*(k,h)$ where $|F'(0)|=1$ — must be provable in closed form or tight bound. If the instability
   cannot be pinned analytically and only ever demonstrated by simulation, the contribution stays at the
   level of an empirical control-chart note (a modest PIVOT), not a theory result.

### Decision

**Reverse the Phase-1 STOP. Proceed (CONDITIONAL GO) to a Phase-2 targeting the bifurcation boundary
$m^\*(k,h)$ and the endogenous false-alarm rate of the orbit, gated on a literature clearance.** The
Phase-1 conclusion was driven by a single mismeasured slope; correcting it reveals a bounded nonlinear
instability that Phase-1's own falsifiers do not kill. The upside is bounded and the novelty is unverified,
so this is a conditional go, not an enthusiastic one.

---
*Monte Carlo estimates from this session (Gaussian mean-shift CUSUM, $k=0.5$, $h=5$). Established
simulation facts are labelled Level B; the invariant-law existence argument is standard theory; all
quantitative dynamical-threshold and bimodality claims that would need proof are marked UNPROVEN / REQUIRES
PROOF; the novelty gap is marked LITERATURE VERIFICATION REQUIRED (partial) with no citations asserted.
This memo corrects, and where noted overturns, the Phase-1 specification (`rebaseguard_phase1.md`).*
