# 01 — The Authoritative Frozen Level 1–3 Model

**Status of this document.** This is the single authoritative statement of the
model that every Level 1–3 claim refers to. It was **verified against the
repository**, not copied from the closure brief. Every line below is traced to
a source location in the correspondence tables of §7.

---

## 1. Probability space and score distribution

Let `(Ω, F, P)` be a probability space carrying a sequence `Z₁, Z₂, Z₃, …` of
real random variables with

```text
Z_t  iid  ~  N(0, 1)          (standard normal: mean 0, variance 1)
```

**Independence.** The `Z_t` are mutually independent — *not* merely pairwise
independent. In Lean this is `iIndepFun X μ` (mathlib's mutual independence for
a family of random variables). Note that `iIndepFun X μ` already forces `μ` to
be a probability measure; the Lean development uses this rather than assuming
`IsProbabilityMeasure` separately (`SmallMoment.lean:135`,
`haveI := hindep.isProbabilityMeasure`).

**Marginal law.** Encoded as a pushforward identity, not as a moment
assumption: `μ.map (X j) = gaussianReal 0 1` for every `j`. Both the one-step
exponential moment and the forcing probability `q < 1` are *derived* from this,
never assumed.

There is **no** in-control/out-of-control drift parameter in the frozen Level
1–3 model: everything is stated under the null `e = 0`. (The parameter `e`
appears only as the differentiation variable of §5.)

## 2. Frozen detector constants

```text
k = 1/2 = 0.5        (CUSUM reference/slack value)
h = 5                (alarm threshold)
H = h + k = 11/2     (derived forcing level, used only in proofs)
m = 1                (full stopping-selected reuse; fixed for Level 1–3)
```

These are frozen. No Level 1–3 claim is made for any other `(k, h)`.

## 3. Two-sided CUSUM recurrence

```text
S₀⁺ = S₀⁻ = 0

S_t⁺ = max(0,  S_{t-1}⁺ + Z_t − k)          (positive arm)
S_t⁻ = max(0,  S_{t-1}⁻ − Z_t − k)          (negative arm)
```

Both arms are driven by the **same** innovation `Z_t`; the negative arm sees
`−Z_t`. The detector is genuinely two-sided — a single-arm reduction is *not*
what is modelled, and the Lean development carries both components as a pair
(`cusumPair : ℕ → Ω → ℝ × ℝ`).

The detector statistic is

```text
M_t = max(S_t⁺, S_t⁻).
```

## 4. Alarm time, stopped quantities, and the target

**Alarm condition is inclusive (`≥`, not `>`), tested after the update, and the
first admissible index is `t = 1`:**

```text
τ = inf { t ≥ 1 : max(S_t⁺, S_t⁻) ≥ h }.
```

The `≥ h` convention matters and is implemented as such everywhere:

* Lean uses `hittingAfter (cusumMax k X) (Set.Ici h) 1`, and `Set.Ici h = {x | h ≤ x}`.
* Python uses `if plus >= h: … if minus >= h: …` (`model.py:step`).
* The certificate's continuation interval `ℓ < z < u` is the *open* complement
  of the closed absorption set (§6).

**Cumulative innovation walk**, including the terminal increment:

```text
T_t = Σ_{s=1}^{t} Z_s ,        T_0 = 0.
```

**Stopped quantities:**

```text
Z_τ  = the innovation that triggered the alarm
T_τ  = Σ_{s=1}^{τ} Z_s        (includes Z_τ)
```

`T_τ` includes the same increment that fired the alarm. This was explicitly
checked as a failure mode ("terminal increment omitted from `T_τ`",
"terminal reward implemented as `Z_τ T_{τ-1}`") and found absent — see
`Mathematical_proof/ReBaseGuard_Step3_Proof_to_Code_Correspondence_Audit.md` §18.

**The Level 1–3 target functional:**

```text
Γ_CUSUM  =  E₀[ Z_τ · T_τ ]
```

with `E₀` the expectation under the null model of §1.

## 5. The analytic identity that Lean formalizes

For the same frozen detector,

```text
d/de  E[ Z_τ · exp( −e·T_τ − (e²/2)·τ ) ] |_{e=0}   =   − E[ Z_τ · T_τ ]
```

This is the differentiation-under-the-expectation step. It is the analytically
delicate ingredient behind the human identity `F₁'(0) = 1 − Γ`; it is **not**
itself a statement about the numerical value of `Γ`.

> **Scope note, stated precisely.** The Lean chain proves exactly the displayed
> derivative identity. The step from that identity to `F₁'(0) = 1 − Γ`
> (which additionally needs `F(0) = 0` by reflection symmetry and the
> change-of-measure setup) is **PROVED by human mathematics only** — see
> `02_THEOREM_MAP.md`, claim `C-F1`.

## 6. Indexing convention (derived, not assumed)

The Lean recursion is written as `Sₙ₊₁ = f(Sₙ, Xₙ)`: the transition `n → n+1`
consumes `X n`. Matching the model recurrence `S_t = max(0, S_{t-1} + Z_t − k)`
at `t = n+1` **forces**

```text
Z_t = X_{t-1},     equivalently     X n = Z_{n+1}.
```

Consequences, all with the *same* index on both sides:

| Mathematics | Lean |
|---|---|
| `S_n` | `cusumPair k X n` |
| `τ` | `cusumTau k h X` |
| `T_t = Σ_{s=1}^t Z_s` | `walk X t = ∑ j ∈ Finset.range t, X j` |
| `Z_τ = X_{τ-1}` | `scoreAt X (cusumTau k h X)` |

This convention is pinned by the Lean lemmas `walk_succ`, `walk_succ_innov`,
`walk_eq_sum_innov` and `innov_succ` (`StoppedQuantities.lean`), and is
documented as *derived* in `rebaseguard-lean/C1_PROGRESS.md`. The alternative
sketch `T n = ∑ s ∈ Finset.Icc 1 n, X s` is off by one under this convention and
is deliberately **not** used — the source says so explicitly.

## 7. Discretization and truncation used by the certificate

The certificate is a **continuum** certificate: there is no state-space grid in
the proof path, and no Gaussian tail cutoff.

| Aspect | What is actually done | Source |
|---|---|---|
| State reduction | `E[Z_τT_τ \| S_t=(p,m), T_t=x] = a(p,m)·x + b(p,m)`; `Γ = b(0,0)` | `certificate.json: state_reduction`, `derivation.md` |
| Reachable domain | Axes `0≤p<h` or `0≤m<h`, plus the interior triangle `p>0, m>0, p+m<h−2k = 4` | `certificate.json: reachable_domain` |
| Continuation interval | `ℓ = m−h−k < z < u = h+k−p` (open); absorption is the closed complement | `derivation.md` |
| Candidate | Degree-12 tensor Chebyshev collocation, coefficients rounded to **exact dyadic rationals** with common denominator `2^50` | Proof Report §6 |
| Candidate's proof role | **None.** `"candidate_role": "exact dyadic candidate only; not proof evidence"` | `certificate.json` |
| Gaussian density | Degree-100 Maclaurin polynomial **plus a rigorous uniform Lagrange remainder** `ε_φ ≤ 3.75603444895965e-7` | `certificate.json: gaussian_handling` |
| Tail truncation | **None.** `"gaussian_tail_truncation": "none"`, `"tail_cutoff": null`; absorbing tails use exact full Gaussian moment formulas | `certificate.json` |
| Range bounding | Symbolic integration + tensor Bernstein convex-hull bounds over `p=r·t, m=r·(1−t)`, pieces `0≤r≤1`, `1≤r≤4`, axis tails `4≤r≤5`; `subdivision_depth = 0`, 4 Bernstein patches | `certificate.json: continuum_method` |
| Sampled grid | **Not used.** `"sampled_grid_used": false`; `"reachable_continuum_complete": true` | `certificate.json` |
| Contraction | Monotone one-sided minorant, `n = 250`, 100 cells, `q_safe = 19/100`, `β = 0.81`; left-endpoint step envelope is a continuum bound by pathwise-coupling monotonicity | `certificate.json: block_contraction` |
| Resolvent | `‖(I−K)^{-1}‖_∞ ≤ n/q_safe = 250/0.19 = 1315.789473684…` | `certificate.json` |
| Precision | 256 bits (residual); 192 bits (stored contraction artifact) | `certificate.json: interval_backend` |

Note that the *finite* 12-cell Bellman solve (`bellman_crosscheck.json`) **is**
discretized, but it is a cross-check outside the trusted computing base, not a
certificate.

---

## 8. Correspondence table — one model, five representations

| Mathematical notation | Human derivation | Numerical implementation (Python/float) | Arb implementation (proof path) | Lean definition |
|---|---|---|---|---|
| `Z_t ~ iid N(0,1)` | `rebaseguard_lemma_handoff.md` §model; Proof Report §2 | `np.random.default_rng(seed).standard_normal` in `diagnostics.py` | `arb_backend.gaussian_phi/gaussian_cdf` (exact `φ`, `Φ` on balls) | `iIndepFun X μ` + `μ.map (X j) = gaussianReal 0 1` |
| `k = 1/2` | Proof Report §2 | `model.step(..., k=0.5)` | `certificate.json: model.k = 1/2` (exact rational) | literal `(1/2 : ℝ)` in `hasDerivAt_rebaseguard_cusum` |
| `h = 5` | Proof Report §2 | `model.step(..., h=5.0)` | `certificate.json: model.h = 5/1` (exact rational) | literal `(5 : ℝ)` in `hasDerivAt_rebaseguard_cusum` |
| `S_t⁺ = max(0, S⁺+Z−k)` | Proof Report §2 | `plus = max(0.0, state.plus + z - k)` | `q(s,z) = (max(0,p+z−k), …)` in `equations.py` | `(cusumPair k X (n+1) ω).1 = max 0 ((cusumPair k X n ω).1 + X n ω - k)` |
| `S_t⁻ = max(0, S⁻−Z−k)` | Proof Report §2 | `minus = max(0.0, state.minus - z - k)` | `q(s,z) = (…, max(0,m−z−k))` | `(cusumPair k X (n+1) ω).2 = max 0 ((cusumPair k X n ω).2 - X n ω - k)` |
| `max(S⁺,S⁻) ≥ h` | Proof Report §2 | `if plus >= h … if minus >= h` | continuation `ℓ < z < u`, open; absorption closed | `hittingAfter (cusumMax k X) (Set.Ici h) 1` |
| `τ = inf{t ≥ 1 : …}` | Proof Report §2 | `enumerate(innovations, start=1)` | first-step conditioning from the reset state | `cusumTau k h X`, with `one_le_cusumTau : 1 ≤ τ` |
| `T_t = Σ_{s≤t} Z_s` | Proof Report §2 | `t_sum = t_sum + z` before the alarm test | `x` in `H = a·x + b` | `walk X n = ∑ j ∈ Finset.range n, X j` |
| `Z_τ` | Proof Report §2 | `PathResult.z_tau` | `W` (terminal increment) | `scoreAt X (cusumTau k h X)` |
| `T_τ` | Proof Report §2 | `PathResult.t_sum` (post-update) | `x + Y` | `walkAt X (cusumTau k h X)` |
| `τ` as a real number | — | `PathResult.tau` | — | `cusumTauReal k h X` |
| `Γ = E[Z_τT_τ]` | Proof Report §2, §4 | `summary()["gamma"]` (MC estimate) | `b(0,0)`; `certificate.json: target_state` | `∫ ω, scoreAt … * walkAt … ∂μ` (appears as the derivative value) |
| `a = Ka + r_a`, `b = Kb + K_z a + r_b` | `derivation.md`; Step-2 audit §5 | — | `equations.py`, `residual.py` | **not formalized** — outside the Lean chain |
| `Γ > 2` | — | MC `≈ 15.9` (not proof) | `Gamma_lower = 3.9243482…` | **not formalized** — deliberately |
| `F₁'(0) = 1 − Γ` | Step-2 audit, canonical theorem | — | Proof Report §17 | **not formalized as such**; Lean proves the underlying derivative identity |

---

## 9. Model-consistency verdict

Every checked point agrees across the human derivation, the Python model, the
Arb certificate and the Lean formalization:

* two-sided recurrence with a shared innovation — **consistent**
* `k = 1/2`, `h = 5` as exact constants — **consistent** (exact rationals in Arb, literals in Lean)
* inclusive `≥ h` alarm, tested post-update — **consistent**
* `τ` starts at `t = 1` — **consistent**
* `T_τ` includes the terminal increment — **consistent**
* target is `E[Z_τ T_τ]`, not `E[Z_τ²]` and not `E[Z_τ T_{τ-1}]` — **consistent**

**No substantive model mismatch was found. Closure is not blocked at this phase.**

One *non-substantive* discrepancy is recorded rather than repaired:
`rebaseguard-proof/results/reproducibility.json` states `"tests": "26 passed"`,
whereas the current suite collects **90** tests (26 of which are the Level-4
`tests/phase4c` group, 20 the `tests/phase4b` group, 44 the core group). The
figure is a stale snapshot from before the Level-4 preparatory suites existed.
It has no bearing on the certificate and is left unedited so the historical
record stays intact; it is listed in `08_LIMITATIONS_AND_BOUNDARIES.md`.
